from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipeline_common import TELEMETRY_FIELDS, fmt, project_path, rad, read_csv, write_csv, write_json


def normalize_csv(
    input_path: Path,
    *,
    run_id: str,
    scenario: str,
    cycle: int,
    default_phase: str,
) -> list[dict[str, str]]:
    rows = read_csv(input_path)
    if not rows:
        return []

    source = input_path.name
    header = set(rows[0].keys())
    output: list[dict[str, str]] = []

    for raw in rows:
        time_s = raw.get("time") or raw.get("time_s") or raw.get("t")
        for axis_index in range(1, 5):
            axis = f"motor{axis_index}"
            torque = None
            q = None
            omega = None
            accel = None

            force_key = f"{axis}_force_N*m"
            torque_key = f"{axis}_N*m"
            if force_key in header:
                torque = raw.get(force_key)
                q = fmt(rad_value(raw.get(f"{axis}_pos_deg")))
                omega = fmt(rad_value(raw.get(f"{axis}_vel_deg_s")))
                accel = fmt(rad_value(raw.get(f"{axis}_acc_deg_s2")))
            elif torque_key in header:
                torque = raw.get(torque_key)
            else:
                continue

            if torque is None or str(torque).strip() == "":
                continue

            output.append(
                {
                    "time": fmt_num(time_s),
                    "run_id": run_id,
                    "scenario": scenario,
                    "cycle": str(cycle),
                    "phase": default_phase,
                    "layer": "",
                    "item": "",
                    "axis": axis,
                    "q": q or "",
                    "omega": omega or "",
                    "accel": accel or "",
                    "torque": fmt_num(torque),
                    "carrying": "0",
                    "source_file": source,
                }
            )
    return output


def normalize_jsonl(
    input_path: Path,
    *,
    run_id: str,
    scenario: str,
    default_phase: str,
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    with input_path.open("r", encoding="utf-8") as stream:
        for line in stream:
            line = line.strip()
            if not line:
                continue
            packet = json.loads(line)
            phase = str(packet.get("phase") or packet.get("cycle_phase") or default_phase)
            cycle = str(packet.get("cycle") or packet.get("cycle_id") or 1)
            layer = str(packet.get("layer") or "")
            item = str(packet.get("item") or "")
            carrying = str(int(bool(packet.get("carrying") or packet.get("load_attached") or False)))
            time_s = first_present(packet, "time", "time_s", "timestamp")
            axis_records = packet.get("axes") or packet.get("motors")
            if isinstance(axis_records, dict):
                iterator = axis_records.items()
            elif isinstance(axis_records, list):
                iterator = [(record.get("axis") or record.get("name"), record) for record in axis_records if isinstance(record, dict)]
            else:
                iterator = []
            for axis, record in iterator:
                if not axis or not isinstance(record, dict):
                    continue
                output.append(
                    {
                        "time": fmt_num(time_s),
                        "run_id": str(packet.get("run_id") or run_id),
                        "scenario": str(packet.get("scenario") or scenario),
                        "cycle": cycle,
                        "phase": phase,
                        "layer": layer,
                        "item": item,
                        "axis": str(axis),
                        "q": fmt_num(first_present(record, "q", "position")),
                        "omega": fmt_num(first_present(record, "omega", "velocity")),
                        "accel": fmt_num(first_present(record, "accel", "acceleration")),
                        "torque": fmt_num(first_present(record, "torque", "moment", "force")),
                        "carrying": carrying,
                        "source_file": input_path.name,
                    }
                )
    return output


def rad_value(value: object) -> float | None:
    try:
        return rad(float(str(value).replace(",", ".")))
    except (TypeError, ValueError):
        return None


def fmt_num(value: object) -> str:
    try:
        return fmt(float(str(value).replace(",", ".")))
    except (TypeError, ValueError):
        return ""


def first_present(mapping: dict, *keys: str) -> object:
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]
    return None


def normalize_inputs(args: argparse.Namespace) -> tuple[list[dict[str, str]], dict]:
    all_rows: list[dict[str, str]] = []
    sources = []
    for input_name in args.inputs:
        input_path = project_path(input_name)
        if input_path.suffix.lower() == ".jsonl":
            rows = normalize_jsonl(
                input_path,
                run_id=args.run_id,
                scenario=args.scenario,
                default_phase=args.default_phase,
            )
        else:
            rows = normalize_csv(
                input_path,
                run_id=args.run_id,
                scenario=args.scenario,
                cycle=args.cycle,
                default_phase=args.default_phase,
            )
        all_rows.extend(rows)
        sources.append({"path": str(input_path), "normalized_rows": len(rows)})

    metadata = {
        "run_id": args.run_id,
        "scenario": args.scenario,
        "default_phase": args.default_phase,
        "sources": sources,
        "rows": len(all_rows),
        "fields": TELEMETRY_FIELDS,
    }
    return all_rows, metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize telemetry CSV/JSONL files into the VKR PAK long schema.")
    parser.add_argument("--inputs", nargs="+", required=True, help="Input telemetry files.")
    parser.add_argument("--output", default="data/telemetry/vkr_normalized/vkr_telemetry_normalized.csv")
    parser.add_argument("--metadata", default="data/telemetry/vkr_normalized/vkr_telemetry_normalized.json")
    parser.add_argument("--run-id", default="legacy_test2")
    parser.add_argument("--scenario", default="S0")
    parser.add_argument("--cycle", type=int, default=1)
    parser.add_argument("--default-phase", default="legacy_unsegmented")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows, metadata = normalize_inputs(args)
    write_csv(args.output, rows, TELEMETRY_FIELDS)
    write_json(args.metadata, metadata)
    print(f"normalized_rows={len(rows)} output={project_path(args.output)}")


if __name__ == "__main__":
    main()
