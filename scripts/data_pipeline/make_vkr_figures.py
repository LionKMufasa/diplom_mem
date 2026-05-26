from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from pipeline_common import project_path, read_csv, to_float, write_json


def points_to_svg(
    series: dict[str, list[tuple[float, float]]],
    *,
    title: str,
    x_label: str,
    y_label: str,
    output: Path,
) -> None:
    width = 900
    height = 520
    margin = 70
    plot_w = width - 2 * margin
    plot_h = height - 2 * margin
    all_x = [x for values in series.values() for x, _ in values]
    all_y = [y for values in series.values() for _, y in values]
    if not all_x or not all_y:
        return
    x_min, x_max = min(all_x), max(all_x)
    y_min, y_max = min(all_y), max(all_y)
    if x_min == x_max:
        x_max += 1
    if y_min == y_max:
        y_max += 1
    y_pad = (y_max - y_min) * 0.08
    y_min -= y_pad
    y_max += y_pad

    def sx(x: float) -> float:
        return margin + (x - x_min) / (x_max - x_min) * plot_w

    def sy(y: float) -> float:
        return margin + plot_h - (y - y_min) / (y_max - y_min) * plot_h

    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf"]
    lines = []
    legend = []
    for index, (name, values) in enumerate(sorted(series.items())):
        color = colors[index % len(colors)]
        path = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in sorted(values))
        lines.append(f'<polyline points="{path}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        legend_y = margin + 22 * index
        legend.append(f'<line x1="{width-230}" y1="{legend_y}" x2="{width-200}" y2="{legend_y}" stroke="{color}" stroke-width="3"/>')
        legend.append(f'<text x="{width-190}" y="{legend_y+5}" font-size="14" fill="#222">{escape(name)}</text>')

    grid = []
    for i in range(6):
        x = margin + i * plot_w / 5
        y = margin + i * plot_h / 5
        grid.append(f'<line x1="{x:.1f}" y1="{margin}" x2="{x:.1f}" y2="{margin+plot_h}" stroke="#e5e5e5"/>')
        grid.append(f'<line x1="{margin}" y1="{y:.1f}" x2="{margin+plot_w}" y2="{y:.1f}" stroke="#e5e5e5"/>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="white"/>
<text x="{width/2}" y="32" text-anchor="middle" font-size="22" font-family="Arial" font-weight="700">{escape(title)}</text>
{''.join(grid)}
<rect x="{margin}" y="{margin}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#222"/>
{''.join(lines)}
{''.join(legend)}
<text x="{width/2}" y="{height-20}" text-anchor="middle" font-size="15" font-family="Arial">{escape(x_label)}</text>
<text x="22" y="{height/2}" transform="rotate(-90 22,{height/2})" text-anchor="middle" font-size="15" font-family="Arial">{escape(y_label)}</text>
<text x="{margin}" y="{height-margin+24}" font-size="12" font-family="Arial">{x_min:.2f}</text>
<text x="{width-margin-42}" y="{height-margin+24}" font-size="12" font-family="Arial">{x_max:.2f}</text>
<text x="18" y="{margin+5}" font-size="12" font-family="Arial">{y_max:.2f}</text>
<text x="18" y="{height-margin}" font-size="12" font-family="Arial">{y_min:.2f}</text>
</svg>
'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")


def escape(text: object) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def make_figures(features_path: Path, estimates_path: Path, metrics_path: Path, output_dir: Path, nn_predictions_path: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    features = read_csv(features_path)
    estimates = read_csv(estimates_path)
    metrics = read_csv(metrics_path)

    torque_series: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for index, row in enumerate(features, start=1):
        torque_series[row.get("axis", "axis")].append((float(index), to_float(row.get("torque_rms"), 0.0) or 0.0))
    torque_file = output_dir / "torque_rms_by_axis.svg"
    points_to_svg(torque_series, title="Torque RMS by axis", x_label="Feature window", y_label="Torque RMS, N*m", output=torque_file)

    hi_series: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in estimates:
        if row.get("axis") != "motor1":
            continue
        name = row.get("scenario", "S")
        hi_series[name].append((to_float(row.get("synthetic_cycle"), 0.0) or 0.0, to_float(row.get("HI"), 0.0) or 0.0))
    hi_file = output_dir / "hi_curves_motor1.svg"
    points_to_svg(hi_series, title="Health Index scenarios, motor1", x_label="Synthetic cycle", y_label="HI", output=hi_file)

    rul_series: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in estimates:
        if row.get("scenario") != "S3" or row.get("axis") != "motor1":
            continue
        x = to_float(row.get("synthetic_cycle"), 0.0) or 0.0
        rul_series["actual"].append((x, to_float(row.get("RUL_actual"), 0.0) or 0.0))
        rul_series["predicted"].append((x, to_float(row.get("RUL_pred"), 0.0) or 0.0))
    rul_file = output_dir / "rul_actual_predicted_s3_motor1.svg"
    points_to_svg(rul_series, title="RUL actual vs predicted, S3 motor1", x_label="Synthetic cycle", y_label="RUL, cycles", output=rul_file)

    dashboard = output_dir / "pak_dashboard_summary.svg"
    write_dashboard_svg(metrics, dashboard)

    nn_file = output_dir / "rul_nn_actual_predicted_s3_motor1.svg"
    nn_figures = []
    if nn_predictions_path.exists():
        nn_predictions = read_csv(nn_predictions_path)
        nn_series: dict[str, list[tuple[float, float]]] = defaultdict(list)
        for row in nn_predictions:
            if row.get("scenario") != "S3" or row.get("axis") != "motor1" or row.get("split") != "test":
                continue
            x = to_float(row.get("synthetic_cycle"), 0.0) or 0.0
            nn_series["actual"].append((x, to_float(row.get("RUL_actual"), 0.0) or 0.0))
            nn_series["MLP predicted"].append((x, to_float(row.get("RUL_nn_pred"), 0.0) or 0.0))
        if nn_series:
            points_to_svg(nn_series, title="Neural network RUL prediction, S3 motor1", x_label="Synthetic cycle", y_label="RUL, cycles", output=nn_file)
            nn_figures.append(str(nn_file))

    summary = {
        "figures": [str(torque_file), str(hi_file), str(rul_file), str(dashboard), *nn_figures],
        "source_features": str(features_path),
        "source_estimates": str(estimates_path),
        "source_metrics": str(metrics_path),
        "source_nn_predictions": str(nn_predictions_path),
    }
    return summary


def write_dashboard_svg(metrics: list[dict[str, str]], output: Path) -> None:
    s3_motor1 = next((row for row in metrics if row.get("scenario") == "S3" and row.get("axis") == "motor1"), metrics[0] if metrics else {})
    mae = s3_motor1.get("MAE", "0")
    rmse = s3_motor1.get("RMSE", "0")
    r2 = s3_motor1.get("R2", "0")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="420" viewBox="0 0 900 420">
<rect width="900" height="420" fill="#f7f8fa"/>
<text x="40" y="52" font-size="28" font-family="Arial" font-weight="700" fill="#202124">PAK monitoring summary</text>
<text x="40" y="84" font-size="15" font-family="Arial" fill="#5f6368">Generated from VKR file pipeline artifacts</text>
<rect x="40" y="120" width="250" height="120" rx="8" fill="white" stroke="#d6d9de"/>
<text x="62" y="155" font-size="16" font-family="Arial" fill="#5f6368">Current phase</text>
<text x="62" y="205" font-size="30" font-family="Arial" font-weight="700" fill="#202124">legacy/data</text>
<rect x="325" y="120" width="250" height="120" rx="8" fill="white" stroke="#d6d9de"/>
<text x="347" y="155" font-size="16" font-family="Arial" fill="#5f6368">HI/RUL status</text>
<text x="347" y="205" font-size="30" font-family="Arial" font-weight="700" fill="#d18b00">warning</text>
<rect x="610" y="120" width="250" height="120" rx="8" fill="white" stroke="#d6d9de"/>
<text x="632" y="155" font-size="16" font-family="Arial" fill="#5f6368">Recommendation</text>
<text x="632" y="205" font-size="25" font-family="Arial" font-weight="700" fill="#202124">increase monitoring</text>
<rect x="40" y="275" width="820" height="90" rx="8" fill="white" stroke="#d6d9de"/>
<text x="62" y="315" font-size="18" font-family="Arial" fill="#202124">S3 motor1 metrics: MAE={escape(mae)}, RMSE={escape(rmse)}, R2={escape(r2)}</text>
<text x="62" y="345" font-size="15" font-family="Arial" fill="#5f6368">This panel is a static RPZ artifact; live Grafana/InfluxDB can use the same fields.</text>
</svg>
'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate SVG figures for VKR practical RPZ inserts.")
    parser.add_argument("--features", default="data/features/vkr_features.csv")
    parser.add_argument("--estimates", default="data/results/vkr_rul_estimates.csv")
    parser.add_argument("--metrics", default="data/results/vkr_rul_metrics.csv")
    parser.add_argument("--nn-predictions", default="data/results/vkr_nn_rul_predictions.csv")
    parser.add_argument("--output-dir", default="reports/figures/vkr_practice")
    parser.add_argument("--summary", default="data/results/figure_summary.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = make_figures(
        project_path(args.features),
        project_path(args.estimates),
        project_path(args.metrics),
        project_path(args.output_dir),
        project_path(args.nn_predictions),
    )
    write_json(args.summary, summary)
    print(f"figures={len(summary['figures'])} output_dir={project_path(args.output_dir)}")


if __name__ == "__main__":
    main()
