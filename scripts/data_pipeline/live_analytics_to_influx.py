from __future__ import annotations

import argparse
import csv
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]

SCENARIOS = {
    "S0": 0.00,
    "S1": 0.08,
    "S2": 0.20,
    "S3": 0.35,
}

NUMERIC_FEATURE_FIELDS = (
    "sample_count",
    "duration",
    "torque_mean",
    "torque_max",
    "torque_std",
    "torque_rms",
    "omega_max",
    "accel_rms",
    "energy",
    "torque_slope",
)

NUMERIC_RUL_FIELDS = ("synthetic_cycle", "degradation_alpha", "HI", "RUL_actual", "RUL_pred")
NUMERIC_NN_RUL_FIELDS = ("synthetic_cycle", "degradation_alpha", "HI", "RUL_actual", "RUL_nn_pred", "abs_error")
NUMERIC_METRIC_FIELDS = ("count", "MAE", "RMSE", "R2")


def project_path(path: str | Path) -> Path:
    path = Path(path)
    if path.is_absolute():
        return path
    return ROOT / path


def to_float(value: object, default: float | None = None) -> float | None:
    if value is None:
        return default
    text = str(value).strip()
    if text == "":
        return default
    text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return default


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    return math.sqrt(sum((value - mu) ** 2 for value in values) / (len(values) - 1))


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values)) if values else 0.0


def escape_tag(value: object) -> str:
    text = str(value if value is not None else "")
    return text.replace("\\", "\\\\").replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")


def escape_measurement(value: str) -> str:
    return value.replace("\\", "\\\\").replace(" ", "\\ ").replace(",", "\\,")


def field_value(value: object) -> str | None:
    number = to_float(value)
    if number is not None:
        return f"{number:.12g}"
    if value is None or str(value).strip() == "":
        return None
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def line_protocol(measurement: str, tags: dict[str, object], fields: dict[str, object], timestamp_ms: int) -> str | None:
    clean_fields = {key: field_value(value) for key, value in fields.items()}
    clean_fields = {key: value for key, value in clean_fields.items() if value is not None}
    if not clean_fields:
        return None
    tag_text = ",".join(f"{escape_tag(key)}={escape_tag(value)}" for key, value in sorted(tags.items()) if str(value) != "")
    field_text = ",".join(f"{escape_tag(key)}={value}" for key, value in sorted(clean_fields.items()))
    head = escape_measurement(measurement)
    if tag_text:
        head = f"{head},{tag_text}"
    return f"{head} {field_text} {timestamp_ms}"


def write_influx_lines(args: argparse.Namespace, lines: list[str]) -> None:
    if not lines:
        return
    if args.dry_run:
        print(f"dry_run_lines={len(lines)}")
        for line in lines[: min(10, len(lines))]:
            print(line)
        return

    params = urllib.parse.urlencode({"org": args.influx_org, "bucket": args.influx_bucket, "precision": "ms"})
    url = f"{args.influx_url.rstrip('/')}/api/v2/write?{params}"
    headers = {
        "Authorization": f"Token {args.influx_token}",
        "Content-Type": "text/plain; charset=utf-8",
    }
    request = urllib.request.Request(url, data="\n".join(lines).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=args.influx_timeout) as response:
        if response.status >= 300:
            raise RuntimeError(f"InfluxDB returned HTTP {response.status}")


def health_index(alpha: float, fail_alpha: float) -> float:
    return max(0.0, min(1.0, 1.0 - alpha / fail_alpha))


def target_rul(alpha: float, cycle: int, cycles: int, fail_alpha: float) -> float:
    final_alpha = alpha / max(cycle / cycles, 1e-9)
    if final_alpha <= 1e-12:
        return float(cycles)
    return max(0.0, (fail_alpha - alpha) / final_alpha * cycles)


def deterministic_rul(actual: float, hi: float, cycle: int) -> float:
    oscillation = 0.04 * math.sin(cycle / 6.0)
    return max(0.0, actual * (0.96 + oscillation) + (1.0 - hi) * 2.0)


def risk_recommendation(hi: float, predicted: float, hi_crit: float) -> tuple[str, str]:
    if hi <= hi_crit or predicted < 10:
        return "high", "plan_maintenance"
    if hi < 0.55 or predicted < 25:
        return "warning", "increase_monitoring"
    return "normal", "continue_monitoring"


class JsonMlpRegressor:
    def __init__(self, payload: dict[str, Any]):
        metadata = payload.get("metadata") or {}
        self.fail_alpha = float(payload.get("fail_alpha") or 0.45)
        self.metadata = metadata
        self.numeric_features = list(metadata.get("numeric_features") or [])
        self.derived_features = list(metadata.get("derived_features") or [])
        self.phase_vocab = dict(metadata.get("phase_vocab") or {})
        self.axis_vocab = dict(metadata.get("axis_vocab") or {})
        self.scenario_vocab = dict(metadata.get("scenario_vocab") or {})
        self.x_mean = [float(value) for value in metadata.get("x_mean", [])]
        self.x_std = [float(value) or 1.0 for value in metadata.get("x_std", [])]
        self.coefs = payload.get("coefs") or []
        self.intercepts = payload.get("intercepts") or []
        if not self.coefs or not self.intercepts:
            raise ValueError("model JSON does not contain MLP weights")

    @classmethod
    def load(cls, path: Path) -> "JsonMlpRegressor | None":
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as stream:
            return cls(json.load(stream))

    def encode_one_hot(self, value: str, vocab: dict[str, int]) -> list[float]:
        vector = [0.0] * len(vocab)
        key = value if value in vocab else "unknown"
        if key in vocab:
            vector[vocab[key]] = 1.0
        return vector

    def vectorize(self, row: dict[str, object], cycles: int, fail_alpha: float) -> list[float]:
        numeric = [to_float(row.get(field), 0.0) or 0.0 for field in self.numeric_features]
        cycle = int(to_float(row.get("synthetic_cycle"), 1.0) or 1.0)
        alpha = to_float(row.get("degradation_alpha"), 0.0) or 0.0
        progress = max(cycle / cycles, 1e-9)
        degradation_rate = alpha / progress
        derived = [
            progress,
            degradation_rate,
            max(0.0, fail_alpha - alpha),
            health_index(alpha, fail_alpha),
            1.0 if degradation_rate <= 1e-12 else 0.0,
        ]
        x_raw = (
            numeric
            + derived
            + self.encode_one_hot(str(row.get("phase") or ""), self.phase_vocab)
            + self.encode_one_hot(str(row.get("axis") or ""), self.axis_vocab)
            + self.encode_one_hot(str(row.get("scenario") or ""), self.scenario_vocab)
        )
        return [
            (value - self.x_mean[index]) / self.x_std[index]
            for index, value in enumerate(x_raw)
            if index < len(self.x_mean) and index < len(self.x_std)
        ]

    def forward_layer(self, inputs: list[float], weights: list[list[float]], bias: list[float], *, activate: bool) -> list[float]:
        output_size = len(bias)
        outputs = []
        for out_index in range(output_size):
            value = bias[out_index]
            for in_index, input_value in enumerate(inputs):
                value += input_value * float(weights[in_index][out_index])
            outputs.append(math.tanh(value) if activate else value)
        return outputs

    def predict(self, row: dict[str, object], cycles: int, fail_alpha: float) -> float:
        values = self.vectorize(row, cycles, fail_alpha)
        for layer_index, weights in enumerate(self.coefs):
            bias = self.intercepts[layer_index]
            values = self.forward_layer(values, weights, bias, activate=layer_index < len(self.coefs) - 1)
        return max(0.0, math.expm1(values[0]))


class RollingTelemetry:
    def __init__(self, window_seconds: float, min_samples: int) -> None:
        self.window_seconds = window_seconds
        self.min_samples = min_samples
        self.points: dict[str, deque[dict[str, float]]] = defaultdict(deque)
        self.last_packet: dict[str, Any] | None = None
        self.previous_phase = ""
        self.completed_cycles = 0

    def add_packet(self, packet: dict[str, Any]) -> None:
        time_s = to_float(packet.get("time"))
        if time_s is None:
            return
        phase = str(packet.get("phase") or "unknown")
        if phase == "cycle_complete" and self.previous_phase != "cycle_complete":
            self.completed_cycles += 1
        self.previous_phase = phase
        self.last_packet = packet

        axes = packet.get("axes") or {}
        if not isinstance(axes, dict):
            return
        for axis, record in axes.items():
            if not isinstance(record, dict):
                continue
            torque = to_float(record.get("torque"))
            if torque is None:
                continue
            queue = self.points[str(axis)]
            queue.append(
                {
                    "time": time_s,
                    "torque": torque,
                    "omega": to_float(record.get("omega"), 0.0) or 0.0,
                    "accel": to_float(record.get("accel"), 0.0) or 0.0,
                }
            )
            cutoff = time_s - self.window_seconds
            while queue and queue[0]["time"] < cutoff:
                queue.popleft()

    def synthetic_cycle(self, cycles: int) -> int:
        return max(1, min(cycles, self.completed_cycles + 1))

    def feature_rows(self, run_id: str, cycles: int) -> list[dict[str, object]]:
        if not self.last_packet:
            return []
        phase = str(self.last_packet.get("phase") or "unknown")
        synthetic_cycle = self.synthetic_cycle(cycles)
        rows: list[dict[str, object]] = []
        for axis, points_deque in sorted(self.points.items()):
            points = list(points_deque)
            if len(points) < self.min_samples:
                continue
            times = [item["time"] for item in points]
            torques = [item["torque"] for item in points]
            omegas = [item["omega"] for item in points]
            accels = [item["accel"] for item in points]
            duration = max(times) - min(times)
            dt = duration / (len(points) - 1) if len(points) > 1 and duration > 0 else 0.0
            energy = sum(abs(item["torque"] * item["omega"]) * dt for item in points)
            torque_slope = (torques[-1] - torques[0]) / duration if duration > 0 else 0.0
            rows.append(
                {
                    "run_id": run_id,
                    "scenario": "live",
                    "cycle": synthetic_cycle,
                    "phase": phase,
                    "axis": axis,
                    "sample_count": len(points),
                    "time_start": min(times),
                    "time_end": max(times),
                    "duration": duration,
                    "torque_mean": mean(torques),
                    "torque_max": max(abs(value) for value in torques),
                    "torque_std": std(torques),
                    "torque_rms": rms(torques),
                    "omega_max": max(abs(value) for value in omegas),
                    "accel_rms": rms(accels),
                    "energy": energy,
                    "torque_slope": torque_slope,
                }
            )
        return rows


def scaled_feature_row(base: dict[str, object], scenario: str, cycles: int) -> dict[str, object]:
    row = dict(base)
    cycle = int(to_float(base.get("cycle"), 1.0) or 1.0)
    final_alpha = SCENARIOS[scenario]
    alpha = final_alpha * cycle / cycles
    torque_multiplier = 1.0 + alpha
    energy_multiplier = 1.0 + 1.2 * alpha
    duration_multiplier = 1.0 + 0.25 * alpha
    row["scenario"] = scenario
    row["synthetic_cycle"] = cycle
    row["degradation_alpha"] = alpha
    for key in ("torque_mean", "torque_max", "torque_std", "torque_rms", "torque_slope"):
        row[key] = (to_float(row.get(key), 0.0) or 0.0) * torque_multiplier
    row["energy"] = (to_float(row.get("energy"), 0.0) or 0.0) * energy_multiplier
    row["duration"] = (to_float(row.get("duration"), 0.0) or 0.0) * duration_multiplier
    return row


def prediction_rows(
    feature_rows: list[dict[str, object]],
    *,
    model: JsonMlpRegressor | None,
    cycles: int,
    fail_alpha: float,
    hi_crit: float,
    max_rul: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    features: list[dict[str, object]] = []
    rul_rows: list[dict[str, object]] = []
    nn_rows: list[dict[str, object]] = []
    for base in feature_rows:
        for scenario in SCENARIOS:
            row = scaled_feature_row(base, scenario, cycles)
            cycle = int(to_float(row.get("synthetic_cycle"), 1.0) or 1.0)
            alpha = to_float(row.get("degradation_alpha"), 0.0) or 0.0
            hi = health_index(alpha, fail_alpha)
            actual = min(max_rul, target_rul(alpha, cycle, cycles, fail_alpha))
            pred = min(max_rul, deterministic_rul(actual, hi, cycle))
            nn_pred = min(max_rul, model.predict(row, cycles, fail_alpha) if model else pred)
            risk, recommendation = risk_recommendation(hi, nn_pred, hi_crit)
            row["HI"] = hi
            row["RUL_actual"] = actual
            row["RUL_pred"] = pred
            row["RUL_nn_pred"] = nn_pred
            row["abs_error"] = abs(actual - nn_pred)
            row["risk"] = risk
            row["recommendation"] = recommendation
            row["split"] = "live"
            features.append(row)
            rul_rows.append(row)
            nn_rows.append(row)
    return features, rul_rows, nn_rows


def feature_lines(rows: list[dict[str, object]], timestamp_ms: int) -> Iterable[str]:
    for row in rows:
        tags = {
            "run_id": row.get("run_id", ""),
            "scenario": row.get("scenario", ""),
            "cycle": row.get("cycle", ""),
            "phase": row.get("phase", ""),
            "axis": row.get("axis", ""),
            "source_file": "live_analytics",
        }
        fields = {field: row.get(field, "") for field in NUMERIC_FEATURE_FIELDS}
        line = line_protocol("vkr_phase_features", tags, fields, timestamp_ms)
        if line:
            yield line


def rul_lines(rows: list[dict[str, object]], timestamp_ms: int) -> Iterable[str]:
    for row in rows:
        tags = {
            "run_id": row.get("run_id", ""),
            "scenario": row.get("scenario", ""),
            "phase": row.get("phase", ""),
            "axis": row.get("axis", ""),
            "risk": row.get("risk", ""),
            "recommendation": row.get("recommendation", ""),
            "source_file": "live_analytics",
        }
        fields = {field: row.get(field, "") for field in NUMERIC_RUL_FIELDS}
        line = line_protocol("vkr_rul_estimates", tags, fields, timestamp_ms)
        if line:
            yield line


def nn_rul_lines(rows: list[dict[str, object]], timestamp_ms: int) -> Iterable[str]:
    for row in rows:
        tags = {
            "run_id": row.get("run_id", ""),
            "scenario": row.get("scenario", ""),
            "phase": row.get("phase", ""),
            "axis": row.get("axis", ""),
            "split": row.get("split", ""),
            "risk": row.get("risk", ""),
            "recommendation": row.get("recommendation", ""),
            "source_file": "live_analytics",
        }
        fields = {field: row.get(field, "") for field in NUMERIC_NN_RUL_FIELDS}
        line = line_protocol("vkr_nn_rul_predictions", tags, fields, timestamp_ms)
        if line:
            yield line


def metric_lines(rows: list[dict[str, object]], measurement: str, timestamp_ms: int) -> Iterable[str]:
    for index, row in enumerate(rows):
        tags = {
            "run_id": row.get("run_id", ""),
            "split": row.get("split", ""),
            "scenario": row.get("scenario", ""),
            "axis": row.get("axis", ""),
            "source_file": row.get("source_file", "live_analytics"),
        }
        fields = {field: row.get(field, "") for field in NUMERIC_METRIC_FIELDS}
        line = line_protocol(measurement, tags, fields, timestamp_ms + index)
        if line:
            yield line


class MetricAccumulator:
    def __init__(self, max_points: int, min_points: int) -> None:
        self.max_points = max_points
        self.min_points = min_points
        self.groups: dict[tuple[str, str], deque[tuple[float, float]]] = defaultdict(deque)

    def add_predictions(self, rows: list[dict[str, object]]) -> None:
        for row in rows:
            key = (str(row.get("scenario") or ""), str(row.get("axis") or ""))
            actual = to_float(row.get("RUL_actual"), 0.0) or 0.0
            predicted = to_float(row.get("RUL_nn_pred"), 0.0) or 0.0
            queue = self.groups[key]
            queue.append((actual, predicted))
            while len(queue) > self.max_points:
                queue.popleft()

    def rows(self, run_id: str) -> list[dict[str, object]]:
        output: list[dict[str, object]] = []
        for (scenario, axis), values_deque in sorted(self.groups.items()):
            values = list(values_deque)
            if len(values) < self.min_points:
                continue
            actuals = [item[0] for item in values]
            preds = [item[1] for item in values]
            errors = [actual - pred for actual, pred in values]
            mae = mean([abs(error) for error in errors])
            rmse = math.sqrt(mean([error * error for error in errors]))
            actual_mean = mean(actuals)
            denom = sum((value - actual_mean) ** 2 for value in actuals)
            r2 = 1.0 - sum(error * error for error in errors) / denom if denom else 1.0
            output.append(
                {
                    "run_id": run_id,
                    "split": "live",
                    "scenario": scenario,
                    "axis": axis,
                    "count": len(values),
                    "MAE": mae,
                    "RMSE": rmse,
                    "R2": r2,
                    "source_file": "live_analytics",
                }
            )
        return output


def read_metric_csv(path: Path, run_id: str) -> list[dict[str, object]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    output = []
    for row in rows:
        clean = dict(row)
        clean["run_id"] = run_id
        clean["source_file"] = path.name
        output.append(clean)
    return output


def read_new_packets(path: Path, position: int) -> tuple[int, list[dict[str, Any]]]:
    if not path.exists():
        return position, []
    packets = []
    with path.open("r", encoding="utf-8") as stream:
        stream.seek(position)
        for line in stream:
            if not line.endswith("\n"):
                break
            text = line.strip()
            if not text:
                continue
            try:
                packets.append(json.loads(text))
            except json.JSONDecodeError:
                continue
        position = stream.tell()
    return position, packets


def emit_live_snapshot(
    args: argparse.Namespace,
    telemetry: RollingTelemetry,
    model: JsonMlpRegressor | None,
    metrics: MetricAccumulator,
) -> int:
    base_rows = telemetry.feature_rows(args.run_id, args.synthetic_cycles)
    if not base_rows:
        return 0
    feature_rows_full, rul_rows_full, nn_rows_full = prediction_rows(
        base_rows,
        model=model,
        cycles=args.synthetic_cycles,
        fail_alpha=args.fail_alpha,
        hi_crit=args.hi_crit,
        max_rul=args.synthetic_cycles * args.max_rul_multiplier,
    )
    metrics.add_predictions(nn_rows_full)
    timestamp_ms = int(time.time() * 1000)
    lines = []
    lines.extend(feature_lines(feature_rows_full, timestamp_ms))
    lines.extend(rul_lines(rul_rows_full, timestamp_ms))
    lines.extend(nn_rul_lines(nn_rows_full, timestamp_ms))
    write_influx_lines(args, lines)
    return len(lines)


def emit_metrics(args: argparse.Namespace, metrics: MetricAccumulator) -> int:
    timestamp_ms = int(time.time() * 1000)
    rows = metrics.rows(args.run_id)
    rows.extend(read_metric_csv(project_path(args.metric_source), args.run_id))
    lines = list(metric_lines(rows, "vkr_nn_rul_metrics", timestamp_ms))
    write_influx_lines(args, lines)
    return len(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stream live VKR HI/RUL/NN analytics from collector JSONL to InfluxDB.")
    parser.add_argument("--input", required=True, help="Collector JSONL file to follow.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model", default="data/results/vkr_nn_rul_model.json")
    parser.add_argument("--metric-source", default="data/results/vkr_nn_rul_metrics.csv")
    parser.add_argument("--synthetic-cycles", type=int, default=80)
    parser.add_argument("--fail-alpha", type=float, default=0.45)
    parser.add_argument("--hi-crit", type=float, default=0.35)
    parser.add_argument("--window-seconds", type=float, default=12.0)
    parser.add_argument("--min-samples", type=int, default=8)
    parser.add_argument("--min-metric-points", type=int, default=5)
    parser.add_argument("--max-rul-multiplier", type=float, default=8.0)
    parser.add_argument("--period", type=float, default=5.0)
    parser.add_argument("--metric-period", type=float, default=60.0)
    parser.add_argument("--poll", type=float, default=0.5)
    parser.add_argument("--idle-timeout", type=float, default=0.0, help="Exit after this many seconds without new input; 0 means never.")
    parser.add_argument("--once", action="store_true", help="Process the current file once and exit.")
    parser.add_argument("--wait-for-input", action="store_true", help="Wait until the JSONL file appears and receives data.")
    parser.add_argument("--influx-url", default="http://localhost:8086")
    parser.add_argument("--influx-org", default="vkr_org")
    parser.add_argument("--influx-bucket", default="vkr_pak")
    parser.add_argument("--influx-token", default="vkr-local-token-2026")
    parser.add_argument("--influx-timeout", type=float, default=5.0)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = project_path(args.input)
    model = JsonMlpRegressor.load(project_path(args.model))
    telemetry = RollingTelemetry(args.window_seconds, args.min_samples)
    metrics = MetricAccumulator(max_points=500, min_points=args.min_metric_points)
    position = 0
    last_emit = 0.0
    last_metric_emit = 0.0
    last_input_at = time.time()

    print(f"Live analytics input: {input_path}")
    print(f"Live analytics run id: {args.run_id}")
    print(f"Live analytics model: {project_path(args.model) if model else 'not found; deterministic RUL fallback'}")

    while True:
        position, packets = read_new_packets(input_path, position)
        if packets:
            last_input_at = time.time()
            for packet in packets:
                telemetry.add_packet(packet)

        now = time.time()
        if telemetry.last_packet and (now - last_emit >= args.period or args.once):
            try:
                line_count = emit_live_snapshot(args, telemetry, model, metrics)
                if line_count:
                    print(f"live_analytics_lines={line_count}")
            except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as exc:
                print(f"Live analytics InfluxDB write failed: {exc}")
            last_emit = now

        if now - last_metric_emit >= args.metric_period or args.once:
            try:
                line_count = emit_metrics(args, metrics)
                if line_count:
                    print(f"live_metric_lines={line_count}")
            except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as exc:
                print(f"Live metric InfluxDB write failed: {exc}")
            last_metric_emit = now

        if args.once:
            break
        if not args.wait_for_input and not packets and not telemetry.last_packet:
            break
        if args.idle_timeout > 0 and now - last_input_at >= args.idle_timeout:
            print("Live analytics idle timeout reached.")
            break
        time.sleep(args.poll)


if __name__ == "__main__":
    main()
