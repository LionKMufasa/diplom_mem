from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]


TELEMETRY_FIELDS = [
    "time",
    "run_id",
    "scenario",
    "cycle",
    "segment",
    "phase",
    "layer",
    "item",
    "axis",
    "q",
    "omega",
    "accel",
    "torque",
    "carrying",
    "source_file",
]


FEATURE_FIELDS = [
    "run_id",
    "scenario",
    "cycle",
    "phase",
    "axis",
    "sample_count",
    "time_start",
    "time_end",
    "duration",
    "torque_mean",
    "torque_max",
    "torque_std",
    "torque_rms",
    "omega_max",
    "accel_rms",
    "energy",
    "torque_slope",
]


def project_path(path: str | Path) -> Path:
    path = Path(path)
    if path.is_absolute():
        return path
    return ROOT / path


def ensure_parent(path: str | Path) -> Path:
    path = project_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def read_csv(path: str | Path) -> list[dict[str, str]]:
    path = project_path(path)
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: str | Path, rows: Iterable[dict], fieldnames: list[str]) -> Path:
    path = ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_json(path: str | Path, payload: dict | list) -> Path:
    path = ensure_parent(path)
    with path.open("w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return path


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
    if not values:
        return 0.0
    return sum(values) / len(values)


def std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    return math.sqrt(sum((item - mu) ** 2 for item in values) / (len(values) - 1))


def rms(values: list[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(item * item for item in values) / len(values))


def rad(deg: float | None) -> float | None:
    if deg is None:
        return None
    return deg * math.pi / 180.0


def fmt(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ""
        return f"{value:.9g}"
    return str(value)

