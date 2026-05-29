from __future__ import annotations

import argparse
from collections import defaultdict

from pipeline_common import TELEMETRY_FIELDS, project_path, read_csv, to_float, write_csv, write_json


MANDATORY_FIELDS = ["time", "run_id", "scenario", "phase", "axis", "torque"]


def validate_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict]:
    valid_rows: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []
    axis_times: dict[tuple[str, str], list[float]] = defaultdict(list)

    for index, row in enumerate(rows, start=2):
        missing = [field for field in MANDATORY_FIELDS if not str(row.get(field, "")).strip()]
        time_value = to_float(row.get("time"))
        torque_value = to_float(row.get("torque"))
        if time_value is None:
            missing.append("time_numeric")
        if torque_value is None:
            missing.append("torque_numeric")
        if missing:
            errors.append({"line": str(index), "reason": ",".join(missing)})
            continue
        clean = dict(row)
        clean["time"] = f"{time_value:.9g}"
        clean["torque"] = f"{torque_value:.9g}"
        valid_rows.append(clean)
        axis_times[(clean.get("run_id", ""), clean.get("axis", ""))].append(time_value)

    dt_values: list[float] = []
    for times in axis_times.values():
        times.sort()
        dt_values.extend([b - a for a, b in zip(times, times[1:]) if b >= a])

    total = len(rows)
    phase_ok = sum(1 for row in rows if str(row.get("phase", "")).strip())
    data_ok = len(valid_rows)
    dt_avg = sum(dt_values) / len(dt_values) if dt_values else 0.0

    summary = {
        "total_rows": total,
        "valid_rows": data_ok,
        "invalid_rows": len(errors),
        "K_data": data_ok / total if total else 0.0,
        "K_phase": phase_ok / total if total else 0.0,
        "axis_count": len({row.get("axis", "") for row in valid_rows}),
        "run_count": len({row.get("run_id", "") for row in valid_rows}),
        "cycle_count": len({row.get("cycle", "") for row in valid_rows if str(row.get("cycle", "")).strip()}),
        "segment_count": len({row.get("segment", "") for row in valid_rows if str(row.get("segment", "")).strip()}),
        "phase_count": len({row.get("phase", "") for row in valid_rows}),
        "dt_avg_s": dt_avg,
        "sampling_hz": 1.0 / dt_avg if dt_avg > 0 else 0.0,
        "errors_sample": errors[:20],
    }
    return valid_rows, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate normalized telemetry and write a validated copy plus summary.")
    parser.add_argument("--input", default="data/telemetry/vkr_normalized/vkr_telemetry_normalized.csv")
    parser.add_argument("--output", default="data/telemetry/vkr_validated/vkr_telemetry_validated.csv")
    parser.add_argument("--summary", default="data/results/telemetry_validation_summary.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_csv(args.input)
    valid_rows, summary = validate_rows(rows)
    write_csv(args.output, valid_rows, TELEMETRY_FIELDS)
    write_json(args.summary, summary)
    print(f"valid_rows={len(valid_rows)} K_data={summary['K_data']:.3f} K_phase={summary['K_phase']:.3f}")
    print(f"summary={project_path(args.summary)}")


if __name__ == "__main__":
    main()

