from __future__ import annotations

import argparse
from collections import defaultdict

from pipeline_common import FEATURE_FIELDS, mean, project_path, read_csv, rms, std, to_float, write_csv, write_json


def build_features(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[tuple[str, str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (
            row.get("run_id", ""),
            row.get("scenario", ""),
            row.get("cycle", ""),
            row.get("phase", ""),
            row.get("axis", ""),
        )
        groups[key].append(row)

    features: list[dict[str, str]] = []
    for (run_id, scenario, cycle, phase, axis), group in sorted(groups.items()):
        points = []
        for row in group:
            time_value = to_float(row.get("time"))
            torque = to_float(row.get("torque"))
            if time_value is None or torque is None:
                continue
            points.append(
                {
                    "time": time_value,
                    "torque": torque,
                    "omega": to_float(row.get("omega"), 0.0) or 0.0,
                    "accel": to_float(row.get("accel"), 0.0) or 0.0,
                }
            )
        points.sort(key=lambda item: item["time"])
        if not points:
            continue
        times = [item["time"] for item in points]
        torques = [item["torque"] for item in points]
        omegas = [item["omega"] for item in points]
        accels = [item["accel"] for item in points]
        duration = max(times) - min(times)
        dt = duration / (len(points) - 1) if len(points) > 1 and duration > 0 else 0.0
        energy = sum(abs(item["torque"] * item["omega"]) * dt for item in points)
        torque_slope = (torques[-1] - torques[0]) / duration if duration > 0 else 0.0
        features.append(
            {
                "run_id": run_id,
                "scenario": scenario,
                "cycle": cycle,
                "phase": phase,
                "axis": axis,
                "sample_count": str(len(points)),
                "time_start": f"{min(times):.9g}",
                "time_end": f"{max(times):.9g}",
                "duration": f"{duration:.9g}",
                "torque_mean": f"{mean(torques):.9g}",
                "torque_max": f"{max(abs(value) for value in torques):.9g}",
                "torque_std": f"{std(torques):.9g}",
                "torque_rms": f"{rms(torques):.9g}",
                "omega_max": f"{max(abs(value) for value in omegas):.9g}",
                "accel_rms": f"{rms(accels):.9g}",
                "energy": f"{energy:.9g}",
                "torque_slope": f"{torque_slope:.9g}",
            }
        )
    return features


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build phase/axis features from validated telemetry.")
    parser.add_argument("--input", default="data/telemetry/vkr_validated/vkr_telemetry_validated.csv")
    parser.add_argument("--output", default="data/features/vkr_features.csv")
    parser.add_argument("--summary", default="data/results/feature_summary.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_csv(args.input)
    features = build_features(rows)
    write_csv(args.output, features, FEATURE_FIELDS)
    summary = {
        "input_rows": len(rows),
        "feature_rows": len(features),
        "cycle_count": len({row.get("cycle", "") for row in features if str(row.get("cycle", "")).strip()}),
        "segment_count": len({row.get("segment", "") for row in rows if str(row.get("segment", "")).strip()}),
        "axes": sorted({row["axis"] for row in features}),
        "phases": sorted({row["phase"] for row in features}),
        "output": str(project_path(args.output)),
    }
    write_json(args.summary, summary)
    print(f"feature_rows={len(features)} output={project_path(args.output)}")


if __name__ == "__main__":
    main()

