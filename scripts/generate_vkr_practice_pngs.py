from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "reports" / "figures" / "vkr_practice_png"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def savefig(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()


def plot_torque() -> None:
    rows = read_rows(DATA / "features" / "vkr_features.csv")
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[row["axis"]].append(float(row["torque_rms"]))
    axes = sorted(grouped)
    values = [sum(grouped[a]) / len(grouped[a]) for a in axes]

    plt.figure(figsize=(7.2, 4.1))
    bars = plt.bar(axes, values, color=["#2f6f9f", "#3f9f8f", "#e0a33a", "#b85c45"])
    plt.title("Среднеквадратический момент по контролируемым осям")
    plt.ylabel("M_rms, Н·м")
    plt.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.1f}", ha="center", va="bottom", fontsize=9)
    savefig(OUT / "torque_rms_by_axis.png")


def plot_hi() -> None:
    rows = read_rows(DATA / "results" / "vkr_rul_estimates.csv")
    plt.figure(figsize=(7.2, 4.1))
    colors = {"S0": "#2f6f9f", "S1": "#3f9f8f", "S2": "#e0a33a", "S3": "#b85c45"}
    for scenario in ["S0", "S1", "S2", "S3"]:
        pts = [
            (int(r["synthetic_cycle"]), float(r["HI"]))
            for r in rows
            if r["axis"] == "motor1" and r["phase"] == "cycle_complete" and r["scenario"] == scenario
        ]
        pts = sorted(pts)
        if pts:
            x, y = zip(*pts)
            plt.plot(x, y, label=scenario, color=colors[scenario], linewidth=2)
    plt.axhline(0.35, color="#7c3f3f", linestyle="--", linewidth=1.2, label="HI_кр = 0,35")
    plt.title("Изменение HI для оси motor1")
    plt.xlabel("Номер синтетического цикла")
    plt.ylabel("HI")
    plt.ylim(0, 1.05)
    plt.grid(alpha=0.25)
    plt.legend(ncol=3, fontsize=9)
    savefig(OUT / "hi_curves_motor1.png")


def plot_nn_rul() -> None:
    rows = read_rows(DATA / "results" / "vkr_nn_rul_predictions.csv")
    pts = [
        (int(r["synthetic_cycle"]), float(r["RUL_actual"]), float(r["RUL_nn_pred"]))
        for r in rows
        if r["axis"] == "motor1" and r["phase"] == "cycle_complete" and r["scenario"] == "S3"
    ]
    pts = sorted(pts)
    x, actual, pred = zip(*pts)
    plt.figure(figsize=(7.2, 4.1))
    plt.plot(x, actual, label="Фактический RUL", color="#2f6f9f", linewidth=2.2)
    plt.plot(x, pred, label="Прогноз MLPRegressor", color="#b85c45", linewidth=2, linestyle="--")
    plt.title("Фактический и прогнозный RUL, сценарий S3, motor1")
    plt.xlabel("Номер синтетического цикла")
    plt.ylabel("RUL, циклы")
    plt.grid(alpha=0.25)
    plt.legend(fontsize=9)
    savefig(OUT / "rul_nn_actual_predicted_s3_motor1.png")


def plot_dashboard_summary() -> None:
    summary = {
        "K_data": "1,000",
        "K_phase": "1,000",
        "MAE": "1,173 цикла",
        "RMSE": "1,442 цикла",
        "R²": "0,994",
        "T_update": "5 с",
    }
    plt.figure(figsize=(7.2, 4.1))
    plt.axis("off")
    plt.text(0.5, 0.92, "Сводная панель результатов ПАК PdM", ha="center", va="center", fontsize=15, weight="bold")
    positions = [(0.25, 0.68), (0.5, 0.68), (0.75, 0.68), (0.25, 0.38), (0.5, 0.38), (0.75, 0.38)]
    colors = ["#d9edf7", "#d9edf7", "#e9f5e9", "#f7efd9", "#f7efd9", "#e9f5e9"]
    for (label, value), (x, y), color in zip(summary.items(), positions, colors):
        rect = plt.Rectangle((x - 0.14, y - 0.10), 0.28, 0.18, facecolor=color, edgecolor="#6d7a86", linewidth=1.0)
        plt.gca().add_patch(rect)
        plt.text(x, y + 0.035, label, ha="center", va="center", fontsize=11, weight="bold")
        plt.text(x, y - 0.035, value, ha="center", va="center", fontsize=11)
    plt.text(0.5, 0.12, "Данные контрольного прогона long_live_01 и тестовой выборки модели RUL", ha="center", fontsize=10)
    savefig(OUT / "pak_dashboard_summary.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plot_torque()
    plot_hi()
    plot_nn_rul()
    plot_dashboard_summary()
    print(f"generated={OUT}")


if __name__ == "__main__":
    main()
