from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from pipeline_common import ROOT, project_path, write_json


def run_step(args: list[str]) -> None:
    command = [sys.executable, str(Path(__file__).resolve().parent / args[0]), *args[1:]]
    print("RUN", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the VKR file-based PAK data pipeline.")
    parser.add_argument(
        "--inputs",
        nargs="+",
        default=[
            "data/telemetry/test2_dynamics_monitor.csv",
            "data/telemetry/test2_joint_torques.csv",
        ],
    )
    parser.add_argument("--run-id", default="legacy_test2")
    parser.add_argument("--scenario", default="S0")
    parser.add_argument("--cycles", type=int, default=80)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_step(
        [
            "normalize_telemetry.py",
            "--inputs",
            *args.inputs,
            "--run-id",
            args.run_id,
            "--scenario",
            args.scenario,
        ]
    )
    run_step(["validate_telemetry.py"])
    run_step(["build_features.py"])
    run_step(["simulate_degradation.py", "--cycles", str(args.cycles)])
    run_step(["estimate_rul.py", "--cycles", str(args.cycles)])
    run_step(["train_rul_mlp.py", "--cycles", str(args.cycles)])
    run_step(["make_vkr_figures.py"])
    summary = {
        "status": "ok",
        "inputs": [str(project_path(item)) for item in args.inputs],
        "normalized": str(project_path("data/telemetry/vkr_normalized/vkr_telemetry_normalized.csv")),
        "validated": str(project_path("data/telemetry/vkr_validated/vkr_telemetry_validated.csv")),
        "features": str(project_path("data/features/vkr_features.csv")),
        "degradation_features": str(project_path("data/experiments/vkr_degradation_features.csv")),
        "rul_estimates": str(project_path("data/results/vkr_rul_estimates.csv")),
        "rul_metrics": str(project_path("data/results/vkr_rul_metrics.csv")),
        "nn_rul_predictions": str(project_path("data/results/vkr_nn_rul_predictions.csv")),
        "nn_rul_metrics": str(project_path("data/results/vkr_nn_rul_metrics.csv")),
        "nn_rul_model": str(project_path("data/results/vkr_nn_rul_model.json")),
        "figures": str(project_path("reports/figures/vkr_practice")),
    }
    write_json("data/results/file_pipeline_run_summary.json", summary)
    print("pipeline_status=ok")
    print(f"summary={project_path('data/results/file_pipeline_run_summary.json')}")


if __name__ == "__main__":
    main()
