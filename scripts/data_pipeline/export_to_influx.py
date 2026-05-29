from __future__ import annotations

import argparse
import csv
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from pipeline_common import project_path, to_float


NUMERIC_TELEMETRY_FIELDS = ("q", "omega", "accel", "torque")
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


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


def timestamp_base_ms(start_time: str | None) -> int:
    if not start_time:
        return int(time.time() * 1000)
    text = start_time.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def aligned_base_ms(rows: list[dict[str, str]]) -> int:
    max_time = 0.0
    for row in rows:
        value = to_float(row.get("time"))
        if value is not None and value > max_time:
            max_time = value
    return int(time.time() * 1000) - int(max_time * 1000)


def telemetry_lines(rows: list[dict[str, str]], base_ms: int) -> Iterable[str]:
    seen_state: set[tuple[str, str, str, str, str, str, str, str]] = set()
    phase_codes: dict[str, int] = {}
    for row in rows:
        time_s = to_float(row.get("time")) or 0.0
        timestamp_ms = base_ms + int(time_s * 1000)
        tags = {
            "run_id": row.get("run_id", ""),
            "scenario": row.get("scenario", ""),
            "phase": row.get("phase", ""),
            "segment": row.get("segment", ""),
            "axis": row.get("axis", ""),
            "layer": row.get("layer", ""),
            "item": row.get("item", ""),
            "source_file": row.get("source_file", ""),
        }
        fields = {field: row.get(field, "") for field in NUMERIC_TELEMETRY_FIELDS}
        fields["cycle"] = row.get("cycle", "")
        fields["carrying"] = row.get("carrying", "")
        line = line_protocol("vkr_motor_telemetry", tags, fields, timestamp_ms)
        if line:
            yield line

        state_key = (
            row.get("run_id", ""),
            row.get("scenario", ""),
            row.get("time", ""),
            row.get("phase", ""),
            row.get("layer", ""),
            row.get("item", ""),
            row.get("cycle", ""),
            row.get("segment", ""),
        )
        if state_key in seen_state:
            continue
        seen_state.add(state_key)
        phase = row.get("phase", "")
        if phase not in phase_codes:
            phase_codes[phase] = len(phase_codes) + 1
        state_tags = {
            "run_id": row.get("run_id", ""),
            "scenario": row.get("scenario", ""),
            "phase": phase,
            "segment": row.get("segment", ""),
            "layer": row.get("layer", ""),
            "item": row.get("item", ""),
        }
        state_fields = {
            "cycle": row.get("cycle", ""),
            "segment": row.get("segment", ""),
            "carrying": row.get("carrying", ""),
            "phase_code": phase_codes[phase],
        }
        state_line = line_protocol("vkr_cycle_state", state_tags, state_fields, timestamp_ms)
        if state_line:
            yield state_line


def feature_lines(rows: list[dict[str, str]], base_ms: int) -> Iterable[str]:
    for row in rows:
        time_s = to_float(row.get("time_end")) or to_float(row.get("time_start")) or 0.0
        timestamp_ms = base_ms + int(time_s * 1000)
        tags = {
            "run_id": row.get("run_id", ""),
            "scenario": row.get("scenario", ""),
            "cycle": row.get("cycle", ""),
            "phase": row.get("phase", ""),
            "axis": row.get("axis", ""),
        }
        fields = {field: row.get(field, "") for field in NUMERIC_FEATURE_FIELDS}
        line = line_protocol("vkr_phase_features", tags, fields, timestamp_ms)
        if line:
            yield line


def rul_lines(rows: list[dict[str, str]], base_ms: int) -> Iterable[str]:
    for row in rows:
        cycle = to_float(row.get("synthetic_cycle")) or 0.0
        timestamp_ms = base_ms + int(cycle * 1000)
        tags = {
            "run_id": row.get("run_id", ""),
            "scenario": row.get("scenario", ""),
            "phase": row.get("phase", ""),
            "axis": row.get("axis", ""),
            "risk": row.get("risk", ""),
            "recommendation": row.get("recommendation", ""),
        }
        fields = {field: row.get(field, "") for field in NUMERIC_RUL_FIELDS}
        line = line_protocol("vkr_rul_estimates", tags, fields, timestamp_ms)
        if line:
            yield line


def nn_rul_lines(rows: list[dict[str, str]], base_ms: int) -> Iterable[str]:
    for row in rows:
        cycle = to_float(row.get("synthetic_cycle")) or 0.0
        timestamp_ms = base_ms + int(cycle * 1000)
        tags = {
            "run_id": row.get("run_id", ""),
            "scenario": row.get("scenario", ""),
            "phase": row.get("phase", ""),
            "axis": row.get("axis", ""),
            "split": row.get("split", ""),
            "risk": row.get("risk", ""),
            "recommendation": row.get("recommendation", ""),
        }
        fields = {field: row.get(field, "") for field in NUMERIC_NN_RUL_FIELDS}
        line = line_protocol("vkr_nn_rul_predictions", tags, fields, timestamp_ms)
        if line:
            yield line


def metric_lines(rows: list[dict[str, str]], measurement: str, base_ms: int) -> Iterable[str]:
    for index, row in enumerate(rows):
        timestamp_ms = base_ms + index
        tags = {
            "split": row.get("split", ""),
            "scenario": row.get("scenario", ""),
            "axis": row.get("axis", ""),
        }
        fields = {field: row.get(field, "") for field in NUMERIC_METRIC_FIELDS}
        line = line_protocol(measurement, tags, fields, timestamp_ms)
        if line:
            yield line


def batched(items: Iterable[str], size: int) -> Iterable[list[str]]:
    batch: list[str] = []
    for item in items:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def write_batches(args: argparse.Namespace, lines: list[str]) -> None:
    if args.dry_run:
        print(f"dry_run_lines={len(lines)}")
        for line in lines[: min(5, len(lines))]:
            print(line)
        return

    params = urllib.parse.urlencode({"org": args.org, "bucket": args.bucket, "precision": "ms"})
    url = f"{args.url.rstrip('/')}/api/v2/write?{params}"
    headers = {
        "Authorization": f"Token {args.token}",
        "Content-Type": "text/plain; charset=utf-8",
    }
    written = 0
    for batch in batched(lines, args.batch_size):
        body = "\n".join(batch).encode("utf-8")
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=args.timeout) as response:
                if response.status >= 300:
                    raise RuntimeError(f"InfluxDB returned HTTP {response.status}")
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise SystemExit(f"InfluxDB write failed: HTTP {exc.code}: {details}") from exc
        except urllib.error.URLError as exc:
            raise SystemExit(f"InfluxDB is not reachable at {args.url}: {exc}") from exc
        written += len(batch)
    print(f"influx_lines_written={written}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export VKR PAK pipeline artifacts to InfluxDB 2.x line protocol.")
    parser.add_argument("--url", default="http://localhost:8086", help="InfluxDB base URL.")
    parser.add_argument("--org", default="vkr_org", help="InfluxDB organization.")
    parser.add_argument("--bucket", default="vkr_pak", help="InfluxDB bucket.")
    parser.add_argument("--token", default="vkr-local-token-2026", help="InfluxDB API token.")
    parser.add_argument("--validated", default="data/telemetry/vkr_validated/vkr_telemetry_validated.csv")
    parser.add_argument("--features", default="data/features/vkr_features.csv")
    parser.add_argument("--rul", default="data/results/vkr_rul_estimates.csv")
    parser.add_argument("--nn-rul", default="data/results/vkr_nn_rul_predictions.csv")
    parser.add_argument("--rul-metrics", default="data/results/vkr_rul_metrics.csv")
    parser.add_argument("--nn-rul-metrics", default="data/results/vkr_nn_rul_metrics.csv")
    parser.add_argument("--start-time", default=None, help="Base wall time for relative simulation timestamps, ISO format.")
    parser.add_argument(
        "--timestamp-mode",
        choices=["align-end", "start-now"],
        default="align-end",
        help="align-end maps the last telemetry sample to now; start-now maps simulation t=0 to now.",
    )
    parser.add_argument("--batch-size", type=int, default=5000)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--dry-run", action="store_true", help="Print generated line protocol without writing.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    lines: list[str] = []

    validated_path = project_path(args.validated)
    features_path = project_path(args.features)
    rul_path = project_path(args.rul)
    nn_rul_path = project_path(args.nn_rul)
    rul_metrics_path = project_path(args.rul_metrics)
    nn_rul_metrics_path = project_path(args.nn_rul_metrics)
    validated_rows = read_csv(validated_path) if validated_path.exists() else []
    features_rows = read_csv(features_path) if features_path.exists() else []
    rul_rows = read_csv(rul_path) if rul_path.exists() else []
    nn_rul_rows = read_csv(nn_rul_path) if nn_rul_path.exists() else []
    rul_metric_rows = read_csv(rul_metrics_path) if rul_metrics_path.exists() else []
    nn_rul_metric_rows = read_csv(nn_rul_metrics_path) if nn_rul_metrics_path.exists() else []

    if args.start_time:
        base_ms = timestamp_base_ms(args.start_time)
    elif args.timestamp_mode == "align-end":
        base_ms = aligned_base_ms(validated_rows)
    else:
        base_ms = timestamp_base_ms(None)

    lines.extend(telemetry_lines(validated_rows, base_ms))
    lines.extend(feature_lines(features_rows, base_ms))
    lines.extend(rul_lines(rul_rows, base_ms))
    lines.extend(nn_rul_lines(nn_rul_rows, base_ms))
    lines.extend(metric_lines(rul_metric_rows, "vkr_rul_metrics", base_ms))
    lines.extend(metric_lines(nn_rul_metric_rows, "vkr_nn_rul_metrics", base_ms))

    write_batches(args, lines)


if __name__ == "__main__":
    main()
