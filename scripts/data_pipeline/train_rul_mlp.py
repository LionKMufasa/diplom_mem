from __future__ import annotations

import argparse
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

try:
    from sklearn.neural_network import MLPRegressor
except ImportError as exc:
    raise SystemExit(
        "scikit-learn is required for train_rul_mlp.py. "
        "Run the pipeline with the system Python where scikit-learn is installed, "
        "or install scikit-learn into the current Python environment."
    ) from exc

from pipeline_common import project_path, read_csv, to_float, write_csv, write_json


NUMERIC_FEATURES = [
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
    "synthetic_cycle",
    "degradation_alpha",
]

DERIVED_FEATURES = [
    "degradation_progress",
    "degradation_rate",
    "remaining_alpha",
    "HI",
    "is_no_degradation",
]

PREDICTION_FIELDS = [
    "run_id",
    "scenario",
    "phase",
    "axis",
    "synthetic_cycle",
    "degradation_alpha",
    "HI",
    "RUL_actual",
    "RUL_nn_pred",
    "split",
    "abs_error",
    "risk",
    "recommendation",
]

METRIC_FIELDS = ["split", "scenario", "axis", "count", "MAE", "RMSE", "R2"]


def one_hot(values: list[str]) -> tuple[dict[str, int], np.ndarray]:
    vocab = {value: index for index, value in enumerate(sorted(set(values)))}
    matrix = np.zeros((len(values), len(vocab)), dtype=float)
    for row_index, value in enumerate(values):
        matrix[row_index, vocab[value]] = 1.0
    return vocab, matrix


def target_rul(alpha: float, cycle: int, cycles: int, fail_alpha: float) -> float:
    final_alpha = alpha / max(cycle / cycles, 1e-9)
    if final_alpha <= 1e-12:
        return float(cycles)
    return max(0.0, (fail_alpha - alpha) / final_alpha * cycles)


def health_index(alpha: float, fail_alpha: float) -> float:
    return max(0.0, min(1.0, 1.0 - alpha / fail_alpha))


def prepare_dataset(rows: list[dict[str, str]], cycles: int, fail_alpha: float) -> tuple[np.ndarray, np.ndarray, dict]:
    numeric = np.array(
        [[to_float(row.get(field), 0.0) or 0.0 for field in NUMERIC_FEATURES] for row in rows],
        dtype=float,
    )
    derived_values = []
    targets = []
    for row in rows:
        cycle = int(to_float(row.get("synthetic_cycle"), 1) or 1)
        alpha = to_float(row.get("degradation_alpha"), 0.0) or 0.0
        progress = max(cycle / cycles, 1e-9)
        degradation_rate = alpha / progress
        derived_values.append(
            [
                progress,
                degradation_rate,
                max(0.0, fail_alpha - alpha),
                health_index(alpha, fail_alpha),
                1.0 if degradation_rate <= 1e-12 else 0.0,
            ]
        )
        targets.append(target_rul(alpha, cycle, cycles, fail_alpha))

    derived = np.array(derived_values, dtype=float)
    phases = [row.get("phase", "") for row in rows]
    axes = [row.get("axis", "") for row in rows]
    scenarios = [row.get("scenario", "") for row in rows]
    phase_vocab, phase_matrix = one_hot(phases)
    axis_vocab, axis_matrix = one_hot(axes)
    scenario_vocab, scenario_matrix = one_hot(scenarios)

    x_raw = np.concatenate([numeric, derived, phase_matrix, axis_matrix, scenario_matrix], axis=1)
    x_mean = x_raw.mean(axis=0)
    x_std = x_raw.std(axis=0)
    x_std[x_std == 0.0] = 1.0
    x = (x_raw - x_mean) / x_std

    # The network learns log(1 + RUL) to keep long-resource scenarios numerically stable.
    y = np.log1p(np.array(targets, dtype=float))
    metadata = {
        "numeric_features": NUMERIC_FEATURES,
        "derived_features": DERIVED_FEATURES,
        "phase_vocab": phase_vocab,
        "axis_vocab": axis_vocab,
        "scenario_vocab": scenario_vocab,
        "x_mean": x_mean.tolist(),
        "x_std": x_std.tolist(),
        "input_size": int(x.shape[1]),
        "target": "log1p(RUL_actual)",
    }
    return x, y, metadata


def deterministic_split(rows: list[dict[str, str]], test_ratio: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    train_mask = np.ones(len(rows), dtype=bool)
    cycles_by_scenario: dict[str, set[int]] = defaultdict(set)
    for row in rows:
        cycle = int(to_float(row.get("synthetic_cycle"), 1) or 1)
        cycles_by_scenario[row.get("scenario", "")].add(cycle)

    test_cycles_by_scenario: dict[str, set[int]] = {}
    for scenario, cycle_values in cycles_by_scenario.items():
        shuffled = np.array(sorted(cycle_values))
        rng.shuffle(shuffled)
        test_count = max(1, int(round(len(shuffled) * test_ratio))) if len(shuffled) > 1 else 0
        test_cycles_by_scenario[scenario] = set(int(value) for value in shuffled[:test_count])

    for index, row in enumerate(rows):
        cycle = int(to_float(row.get("synthetic_cycle"), 1) or 1)
        if cycle in test_cycles_by_scenario.get(row.get("scenario", ""), set()):
            train_mask[index] = False
    return train_mask


def train_model(
    x: np.ndarray,
    y: np.ndarray,
    train_mask: np.ndarray,
    *,
    hidden_size: int,
    epochs: int,
    learning_rate: float,
    seed: int,
) -> MLPRegressor:
    model = MLPRegressor(
        hidden_layer_sizes=(hidden_size,),
        activation="tanh",
        solver="adam",
        learning_rate_init=learning_rate,
        max_iter=epochs,
        random_state=seed,
        early_stopping=False,
        n_iter_no_change=50,
        tol=1e-6,
    )
    model.fit(x[train_mask], y[train_mask])
    return model


def predict_rul(model: MLPRegressor, x: np.ndarray) -> np.ndarray:
    return np.maximum(0.0, np.expm1(model.predict(x)))


def regression_metrics(actual: list[float], predicted: list[float]) -> tuple[float, float, float]:
    if not actual:
        return 0.0, 0.0, 0.0
    errors = [a - p for a, p in zip(actual, predicted)]
    mae = sum(abs(error) for error in errors) / len(errors)
    rmse = math.sqrt(sum(error * error for error in errors) / len(errors))
    mean_actual = sum(actual) / len(actual)
    denom = sum((value - mean_actual) ** 2 for value in actual)
    r2 = 1.0 - sum(error * error for error in errors) / denom if denom else 1.0
    return mae, rmse, r2


def build_outputs(
    rows: list[dict[str, str]],
    predictions: np.ndarray,
    train_mask: np.ndarray,
    *,
    cycles: int,
    fail_alpha: float,
    hi_crit: float,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    prediction_rows: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        cycle = int(to_float(row.get("synthetic_cycle"), 1) or 1)
        alpha = to_float(row.get("degradation_alpha"), 0.0) or 0.0
        actual = target_rul(alpha, cycle, cycles, fail_alpha)
        hi = health_index(alpha, fail_alpha)
        pred = float(predictions[index])
        risk = "normal"
        recommendation = "continue_monitoring"
        if hi <= hi_crit or pred < 10:
            risk = "high"
            recommendation = "plan_maintenance"
        elif hi < 0.55 or pred < 25:
            risk = "warning"
            recommendation = "increase_monitoring"
        prediction_rows.append(
            {
                "run_id": row.get("run_id", ""),
                "scenario": row.get("scenario", ""),
                "phase": row.get("phase", ""),
                "axis": row.get("axis", ""),
                "synthetic_cycle": str(cycle),
                "degradation_alpha": f"{alpha:.9g}",
                "HI": f"{hi:.9g}",
                "RUL_actual": f"{actual:.9g}",
                "RUL_nn_pred": f"{pred:.9g}",
                "split": "train" if train_mask[index] else "test",
                "abs_error": f"{abs(actual - pred):.9g}",
                "risk": risk,
                "recommendation": recommendation,
            }
        )

    metric_rows: list[dict[str, str]] = []
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in prediction_rows:
        groups[(row["split"], row["scenario"], row["axis"])].append(row)
    for (split, scenario, axis), group in sorted(groups.items()):
        actual = [to_float(row["RUL_actual"], 0.0) or 0.0 for row in group]
        pred = [to_float(row["RUL_nn_pred"], 0.0) or 0.0 for row in group]
        mae, rmse, r2 = regression_metrics(actual, pred)
        metric_rows.append(
            {
                "split": split,
                "scenario": scenario,
                "axis": axis,
                "count": str(len(group)),
                "MAE": f"{mae:.9g}",
                "RMSE": f"{rmse:.9g}",
                "R2": f"{r2:.9g}",
            }
        )
    return prediction_rows, metric_rows


def save_model(path: Path, metadata: dict, model: MLPRegressor, args: argparse.Namespace) -> None:
    payload = {
        "model_type": "sklearn.neural_network.MLPRegressor",
        "task": "remaining_useful_life_prediction",
        "hidden_layer_sizes": list(model.hidden_layer_sizes),
        "activation": model.activation,
        "solver": model.solver,
        "max_iter": args.epochs,
        "learning_rate_init": args.learning_rate,
        "seed": args.seed,
        "fail_alpha": args.fail_alpha,
        "hi_crit": args.hi_crit,
        "metadata": metadata,
        "n_iter": int(model.n_iter_),
        "loss": float(model.loss_),
        "loss_curve": [float(value) for value in getattr(model, "loss_curve_", [])],
        "coefs": [coef.tolist() for coef in model.coefs_],
        "intercepts": [intercept.tolist() for intercept in model.intercepts_],
    }
    write_json(path, payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train an scikit-learn MLPRegressor for VKR RUL prediction.")
    parser.add_argument("--input", default="data/experiments/vkr_degradation_features.csv")
    parser.add_argument("--predictions", default="data/results/vkr_nn_rul_predictions.csv")
    parser.add_argument("--metrics", default="data/results/vkr_nn_rul_metrics.csv")
    parser.add_argument("--model", default="data/results/vkr_nn_rul_model.json")
    parser.add_argument("--summary", default="data/results/nn_rul_summary.json")
    parser.add_argument("--cycles", type=int, default=80)
    parser.add_argument("--fail-alpha", type=float, default=0.45)
    parser.add_argument("--hi-crit", type=float, default=0.35)
    parser.add_argument("--hidden-size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=2000)
    parser.add_argument("--learning-rate", type=float, default=0.02)
    parser.add_argument("--test-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_csv(args.input)
    x, y, metadata = prepare_dataset(rows, args.cycles, args.fail_alpha)
    train_mask = deterministic_split(rows, args.test_ratio, args.seed)
    model = train_model(
        x,
        y,
        train_mask,
        hidden_size=args.hidden_size,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        seed=args.seed,
    )
    predictions = predict_rul(model, x)
    prediction_rows, metric_rows = build_outputs(
        rows,
        predictions,
        train_mask,
        cycles=args.cycles,
        fail_alpha=args.fail_alpha,
        hi_crit=args.hi_crit,
    )

    write_csv(args.predictions, prediction_rows, PREDICTION_FIELDS)
    write_csv(args.metrics, metric_rows, METRIC_FIELDS)
    save_model(project_path(args.model), metadata, model, args)

    test_rows = [row for row in metric_rows if row["split"] == "test"]
    test_mae = sum(to_float(row["MAE"], 0.0) or 0.0 for row in test_rows) / len(test_rows) if test_rows else 0.0
    test_rmse = sum(to_float(row["RMSE"], 0.0) or 0.0 for row in test_rows) / len(test_rows) if test_rows else 0.0
    test_r2 = sum(to_float(row["R2"], 0.0) or 0.0 for row in test_rows) / len(test_rows) if test_rows else 0.0
    summary = {
        "status": "ok",
        "library": "scikit-learn",
        "model_type": "MLPRegressor",
        "training_rows": int(train_mask.sum()),
        "test_rows": int((~train_mask).sum()),
        "prediction_rows": len(prediction_rows),
        "metric_rows": len(metric_rows),
        "hidden_size": args.hidden_size,
        "epochs": args.epochs,
        "learning_rate": args.learning_rate,
        "n_iter": int(model.n_iter_),
        "loss": float(model.loss_),
        "test_MAE_avg": test_mae,
        "test_RMSE_avg": test_rmse,
        "test_R2_avg": test_r2,
        "predictions": str(project_path(args.predictions)),
        "metrics": str(project_path(args.metrics)),
        "model": str(project_path(args.model)),
    }
    write_json(args.summary, summary)
    print(
        "nn_prediction_rows="
        f"{len(prediction_rows)} test_MAE_avg={test_mae:.3f} "
        f"test_RMSE_avg={test_rmse:.3f} test_R2_avg={test_r2:.3f} "
        f"library=scikit-learn"
    )


if __name__ == "__main__":
    main()
