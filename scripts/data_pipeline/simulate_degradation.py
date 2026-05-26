from __future__ import annotations

import argparse

from pipeline_common import FEATURE_FIELDS, project_path, read_csv, to_float, write_csv, write_json


SCENARIOS = {
    "S0": 0.00,
    "S1": 0.08,
    "S2": 0.20,
    "S3": 0.35,
}

OUTPUT_FIELDS = FEATURE_FIELDS + ["synthetic_cycle", "degradation_alpha", "degradation_level"]


def scale(value: str, multiplier: float) -> str:
    return f"{(to_float(value, 0.0) or 0.0) * multiplier:.9g}"


def simulate(features: list[dict[str, str]], cycles: int) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for base in features:
        for scenario, final_alpha in SCENARIOS.items():
            for cycle_index in range(1, cycles + 1):
                progress = cycle_index / cycles
                alpha = final_alpha * progress
                torque_multiplier = 1.0 + alpha
                energy_multiplier = 1.0 + 1.2 * alpha
                duration_multiplier = 1.0 + 0.25 * alpha
                row = dict(base)
                row["scenario"] = scenario
                row["cycle"] = str(cycle_index)
                row["synthetic_cycle"] = str(cycle_index)
                row["degradation_alpha"] = f"{alpha:.9g}"
                row["degradation_level"] = scenario
                for key in ["torque_mean", "torque_max", "torque_std", "torque_rms", "torque_slope"]:
                    row[key] = scale(row.get(key, "0"), torque_multiplier)
                row["energy"] = scale(row.get("energy", "0"), energy_multiplier)
                row["duration"] = scale(row.get("duration", "0"), duration_multiplier)
                output.append(row)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create deterministic degradation scenarios from feature rows.")
    parser.add_argument("--input", default="data/features/vkr_features.csv")
    parser.add_argument("--output", default="data/experiments/vkr_degradation_features.csv")
    parser.add_argument("--summary", default="data/results/degradation_summary.json")
    parser.add_argument("--cycles", type=int, default=80)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    features = read_csv(args.input)
    rows = simulate(features, args.cycles)
    write_csv(args.output, rows, OUTPUT_FIELDS)
    summary = {
        "base_feature_rows": len(features),
        "scenario_rows": len(rows),
        "cycles_per_scenario": args.cycles,
        "scenarios": SCENARIOS,
        "output": str(project_path(args.output)),
    }
    write_json(args.summary, summary)
    print(f"scenario_rows={len(rows)} output={project_path(args.output)}")


if __name__ == "__main__":
    main()

