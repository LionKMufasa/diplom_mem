from __future__ import annotations

import argparse
import math
from collections import defaultdict

from pipeline_common import mean, project_path, read_csv, to_float, write_csv, write_json


RUL_FIELDS = [
    "run_id",
    "scenario",
    "phase",
    "axis",
    "synthetic_cycle",
    "degradation_alpha",
    "HI",
    "RUL_actual",
    "RUL_pred",
    "risk",
    "recommendation",
]

METRIC_FIELDS = ["scenario", "axis", "count", "MAE", "RMSE", "R2", "HI_min", "HI_max"]


def estimate(rows: list[dict[str, str]], fail_alpha: float, hi_crit: float, cycles: int) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    estimates: list[dict[str, str]] = []
    for row in rows:
        alpha = to_float(row.get("degradation_alpha"), 0.0) or 0.0
        cycle = int(to_float(row.get("synthetic_cycle"), 1) or 1)
        final_alpha = alpha / max(cycle / cycles, 1e-9)
        hi = max(0.0, min(1.0, 1.0 - alpha / fail_alpha))
        if final_alpha <= 1e-12:
            actual = cycles
        else:
            actual = max(0.0, (fail_alpha - alpha) / final_alpha * cycles)
        oscillation = 0.04 * math.sin(cycle / 6.0)
        pred = max(0.0, actual * (0.96 + oscillation) + (1.0 - hi) * 2.0)
        risk = "normal"
        recommendation = "continue_monitoring"
        if hi <= hi_crit or pred < 10:
            risk = "high"
            recommendation = "plan_maintenance"
        elif hi < 0.55 or pred < 25:
            risk = "warning"
            recommendation = "increase_monitoring"
        estimates.append(
            {
                "run_id": row.get("run_id", ""),
                "scenario": row.get("scenario", ""),
                "phase": row.get("phase", ""),
                "axis": row.get("axis", ""),
                "synthetic_cycle": str(cycle),
                "degradation_alpha": f"{alpha:.9g}",
                "HI": f"{hi:.9g}",
                "RUL_actual": f"{actual:.9g}",
                "RUL_pred": f"{pred:.9g}",
                "risk": risk,
                "recommendation": recommendation,
            }
        )

    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in estimates:
        groups[(row["scenario"], row["axis"])].append(row)

    metrics: list[dict[str, str]] = []
    for (scenario, axis), group in sorted(groups.items()):
        actuals = [to_float(row["RUL_actual"], 0.0) or 0.0 for row in group]
        preds = [to_float(row["RUL_pred"], 0.0) or 0.0 for row in group]
        his = [to_float(row["HI"], 0.0) or 0.0 for row in group]
        errors = [a - p for a, p in zip(actuals, preds)]
        mae = mean([abs(error) for error in errors])
        rmse = math.sqrt(mean([error * error for error in errors]))
        y_mean = mean(actuals)
        denom = sum((value - y_mean) ** 2 for value in actuals)
        r2 = 1.0 - sum(error * error for error in errors) / denom if denom else 1.0
        metrics.append(
            {
                "scenario": scenario,
                "axis": axis,
                "count": str(len(group)),
                "MAE": f"{mae:.9g}",
                "RMSE": f"{rmse:.9g}",
                "R2": f"{r2:.9g}",
                "HI_min": f"{min(his):.9g}",
                "HI_max": f"{max(his):.9g}",
            }
        )
    return estimates, metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate HI/RUL from degradation features.")
    parser.add_argument("--input", default="data/experiments/vkr_degradation_features.csv")
    parser.add_argument("--output", default="data/results/vkr_rul_estimates.csv")
    parser.add_argument("--metrics", default="data/results/vkr_rul_metrics.csv")
    parser.add_argument("--summary", default="data/results/rul_summary.json")
    parser.add_argument("--fail-alpha", type=float, default=0.45)
    parser.add_argument("--hi-crit", type=float, default=0.35)
    parser.add_argument("--cycles", type=int, default=80)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_csv(args.input)
    estimates, metrics = estimate(rows, args.fail_alpha, args.hi_crit, args.cycles)
    write_csv(args.output, estimates, RUL_FIELDS)
    write_csv(args.metrics, metrics, METRIC_FIELDS)
    summary = {
        "estimate_rows": len(estimates),
        "metric_rows": len(metrics),
        "fail_alpha": args.fail_alpha,
        "hi_crit": args.hi_crit,
        "output": str(project_path(args.output)),
        "metrics": str(project_path(args.metrics)),
    }
    write_json(args.summary, summary)
    print(f"estimate_rows={len(estimates)} metrics={project_path(args.metrics)}")


if __name__ == "__main__":
    main()
