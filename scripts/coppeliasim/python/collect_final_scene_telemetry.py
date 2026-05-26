from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "telemetry" / "vkr_raw"
MODEL_PATH = "/base_respondable"
STATE_PROPERTY = "customData.palletizingCycle"
MOTOR_NAMES = ("motor1", "motor2", "motor3", "motor4")


def add_remote_api_paths() -> None:
    candidates = [
        os.environ.get("COPPELIASIM_ZMQ_CLIENT_PATH"),
        r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\programming\zmqRemoteApi\clients\python\src",
        r"C:\Program Files\CoppeliaRobotics\CoppeliaSim\programming\zmqRemoteApi\clients\python\src",
        r"C:\Program Files (x86)\CoppeliaRobotics\CoppeliaSimEdu\programming\zmqRemoteApi\clients\python\src",
        "/Applications/CoppeliaSim.app/Contents/Resources/programming/zmqRemoteApi/clients/python/src",
        "/Applications/CoppeliaSimEdu.app/Contents/Resources/programming/zmqRemoteApi/clients/python/src",
    ]
    applications = Path("/Applications")
    if applications.exists():
        candidates.extend(
            str(path)
            for path in applications.glob("CoppeliaSim*.app/Contents/Resources/programming/zmqRemoteApi/clients/python/src")
        )
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists():
            sys.path.insert(0, str(path))


add_remote_api_paths()

try:
    from coppeliasim_zmqremoteapi_client import RemoteAPIClient
except ImportError as exc:
    raise SystemExit(
        "Cannot import coppeliasim_zmqremoteapi_client. "
        "Set COPPELIASIM_ZMQ_CLIENT_PATH to CoppeliaSim's "
        "programming\\zmqRemoteApi\\clients\\python\\src directory."
    ) from exc


def normalize_packed_value(value: Any) -> Any:
    if isinstance(value, list):
        return [normalize_packed_value(item) for item in value]
    if isinstance(value, dict):
        numeric_items: list[tuple[int, Any]] = []
        for key, item in value.items():
            if isinstance(key, int):
                numeric_items.append((key, item))
                continue
            if isinstance(key, str) and key.isdigit():
                numeric_items.append((int(key), item))
                continue
            return {str(k): normalize_packed_value(v) for k, v in value.items()}
        return [normalize_packed_value(item) for _, item in sorted(numeric_items)]
    return value


def try_unpack_cycle_state(sim: Any, model: int) -> dict[str, Any]:
    try:
        packed = sim.getBufferProperty(model, STATE_PROPERTY, {"noError": True})
    except Exception:
        return {}
    if not packed:
        return {}
    try:
        unpacked = normalize_packed_value(sim.unpackTable(packed))
    except Exception:
        return {}
    return unpacked if isinstance(unpacked, dict) else {}


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
        if math.isfinite(number):
            return number
    except (TypeError, ValueError):
        pass
    return default


def escape_tag(value: object) -> str:
    text = str(value if value is not None else "")
    return text.replace("\\", "\\\\").replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")


def escape_measurement(value: str) -> str:
    return value.replace("\\", "\\\\").replace(" ", "\\ ").replace(",", "\\,")


def field_value(value: object) -> str | None:
    if value is None or str(value).strip() == "":
        return None
    if isinstance(value, bool):
        return "1" if value else "0"
    try:
        number = float(value)
        if math.isfinite(number):
            return f"{number:.12g}"
    except (TypeError, ValueError):
        pass
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def line_protocol(measurement: str, tags: dict[str, object], fields: dict[str, object], timestamp_ms: int) -> str | None:
    clean_fields = {key: field_value(value) for key, value in fields.items()}
    clean_fields = {key: value for key, value in clean_fields.items() if value is not None}
    if not clean_fields:
        return None
    tag_text = ",".join(f"{escape_tag(key)}={escape_tag(value)}" for key, value in sorted(tags.items()) if str(value) != "")
    field_text = ",".join(f"{escape_tag(key)}={value}" for key, value in sorted(clean_fields.items()))
    head = escape_measurement(measurement)
    if tag_text:
        head = f"{head},{tag_text}"
    return f"{head} {field_text} {timestamp_ms}"


def packet_to_influx_lines(packet: dict[str, Any], phase_codes: dict[str, int], timestamp_ms: int) -> list[str]:
    phase = str(packet.get("phase") or "unknown")
    if phase not in phase_codes:
        phase_codes[phase] = len(phase_codes) + 1

    lines: list[str] = []
    common_tags = {
        "run_id": packet.get("run_id", ""),
        "scenario": packet.get("scenario", ""),
        "phase": phase,
        "layer": packet.get("layer", ""),
        "item": packet.get("item", ""),
        "source_file": "live_zmq",
    }
    axes = packet.get("axes") or {}
    if isinstance(axes, dict):
        for axis, record in axes.items():
            if not isinstance(record, dict):
                continue
            tags = dict(common_tags)
            tags["axis"] = axis
            fields = {
                "q": record.get("q"),
                "omega": record.get("omega"),
                "accel": record.get("accel"),
                "torque": record.get("torque"),
                "cycle": packet.get("cycle"),
                "carrying": packet.get("carrying"),
            }
            line = line_protocol("vkr_motor_telemetry", tags, fields, timestamp_ms)
            if line:
                lines.append(line)

    state_tags = {
        "run_id": packet.get("run_id", ""),
        "scenario": packet.get("scenario", ""),
        "phase": phase,
        "layer": packet.get("layer", ""),
        "item": packet.get("item", ""),
    }
    state_fields = {
        "cycle": packet.get("cycle"),
        "carrying": packet.get("carrying"),
        "phase_code": phase_codes[phase],
    }
    state_line = line_protocol("vkr_cycle_state", state_tags, state_fields, timestamp_ms)
    if state_line:
        lines.append(state_line)
    return lines


def write_influx_lines(args: argparse.Namespace, lines: list[str]) -> None:
    if not lines:
        return
    params = urllib.parse.urlencode({"org": args.influx_org, "bucket": args.influx_bucket, "precision": "ms"})
    url = f"{args.influx_url.rstrip('/')}/api/v2/write?{params}"
    headers = {
        "Authorization": f"Token {args.influx_token}",
        "Content-Type": "text/plain; charset=utf-8",
    }
    request = urllib.request.Request(url, data="\n".join(lines).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=args.influx_timeout) as response:
        if response.status >= 300:
            raise RuntimeError(f"InfluxDB returned HTTP {response.status}")


def get_joint_velocity(sim: Any, joint: int, previous_q: float, dt: float) -> float:
    try:
        return safe_float(sim.getObjectFloatParam(joint, sim.jointfloatparam_velocity))
    except Exception:
        if dt <= 0.0:
            return 0.0
        try:
            return (safe_float(sim.getJointPosition(joint)) - previous_q) / dt
        except Exception:
            return 0.0


def get_joint_torque(sim: Any, joint: int) -> float:
    try:
        return safe_float(sim.getJointForce(joint))
    except Exception:
        return 0.0


def build_output_path(output: Path | None, run_id: str) -> Path:
    if output:
        return output if output.is_absolute() else PROJECT_ROOT / output
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return DEFAULT_OUTPUT_DIR / f"{run_id}_{stamp}.jsonl"


def connect(args: argparse.Namespace) -> tuple[Any, Any]:
    client = RemoteAPIClient(args.host, args.port)
    sim = client.require("sim")
    return client, sim


def collect(args: argparse.Namespace) -> int:
    _, sim = connect(args)
    model = sim.getObject(MODEL_PATH)
    motors = {name: sim.getObject(f"{MODEL_PATH}/{name}") for name in MOTOR_NAMES}
    output_path = build_output_path(args.output, args.run_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Connected to CoppeliaSim at {args.host}:{args.port}")
    if args.wait_for_simulation:
        wait_for_running_simulation(sim)

    last_time = safe_float(sim.getSimulationTime())
    previous = {
        name: {
            "q": safe_float(sim.getJointPosition(handle)),
            "omega": 0.0,
        }
        for name, handle in motors.items()
    }

    started_at = time.time()
    sequence = 0
    written = 0
    last_phase = ""
    last_print = 0.0
    stop_phase_seen_at: float | None = None
    phase_codes: dict[str, int] = {}
    influx_buffer: list[str] = []
    influx_live_active = bool(args.influx_live)

    print(f"Writing final-scene telemetry to: {output_path}")
    print("Telemetry collection is active. Press Ctrl+C to stop collection.")
    if influx_live_active:
        print(f"Live InfluxDB export enabled: {args.influx_url}, bucket={args.influx_bucket}")

    with output_path.open("a", encoding="utf-8") as stream:
        while True:
            wall_elapsed = time.time() - started_at
            if args.duration is not None and wall_elapsed >= args.duration:
                break

            sim_time = safe_float(sim.getSimulationTime())
            dt = max(sim_time - last_time, args.period, 1e-6)
            cycle_state = try_unpack_cycle_state(sim, model)
            phase = str(cycle_state.get("phase") or "unknown")
            layer = cycle_state.get("layer") or 0
            item = str(cycle_state.get("item") or "")
            carrying = bool(cycle_state.get("carrying") or False)

            axes: dict[str, dict[str, float]] = {}
            for name, handle in motors.items():
                q = safe_float(sim.getJointPosition(handle))
                omega = get_joint_velocity(sim, handle, previous[name]["q"], dt)
                accel = (omega - previous[name]["omega"]) / dt
                torque = get_joint_torque(sim, handle)
                axes[name] = {
                    "q": q,
                    "omega": omega,
                    "accel": accel,
                    "torque": torque,
                }
                previous[name]["q"] = q
                previous[name]["omega"] = omega

            sequence += 1
            packet = {
                "seq": sequence,
                "time": sim_time,
                "wall_time": datetime.now().isoformat(timespec="milliseconds"),
                "run_id": args.run_id,
                "scenario": args.scenario,
                "cycle": args.cycle,
                "phase": phase,
                "layer": layer,
                "item": item,
                "carrying": carrying,
                "axes": axes,
            }
            stream.write(json.dumps(packet, ensure_ascii=False) + "\n")
            written += 1
            last_time = sim_time

            if influx_live_active:
                influx_buffer.extend(packet_to_influx_lines(packet, phase_codes, int(time.time() * 1000)))
                if len(influx_buffer) >= args.influx_batch_size:
                    try:
                        write_influx_lines(args, influx_buffer)
                        influx_buffer.clear()
                    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as exc:
                        print(f"Live InfluxDB export disabled after write error: {exc}")
                        influx_live_active = False
                        influx_buffer.clear()

            now = time.time()
            if phase != last_phase or now - last_print >= args.print_interval:
                last_phase = phase
                last_print = now
                print(
                    f"seq={sequence} t={sim_time:.3f}s phase={phase} "
                    f"layer={layer} item={item} carrying={int(carrying)}"
                )
                stream.flush()

            if args.stop_on_phase and phase == args.stop_on_phase:
                if stop_phase_seen_at is None:
                    stop_phase_seen_at = time.time()
                    print(f"Stop phase '{args.stop_on_phase}' detected.")
                    stream.flush()
                elif time.time() - stop_phase_seen_at >= args.stop_delay:
                    break
            else:
                stop_phase_seen_at = None

            time.sleep(args.period)

    if influx_live_active and influx_buffer:
        try:
            write_influx_lines(args, influx_buffer)
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as exc:
            print(f"Final live InfluxDB flush failed: {exc}")

    print(f"Done. Packets written: {written}")
    return written


def wait_for_running_simulation(sim: Any) -> None:
    last_print = 0.0
    while True:
        try:
            state = sim.getSimulationState()
            if state != sim.simulation_stopped:
                print("Simulation is running. Starting telemetry collection.")
                return
        except Exception:
            pass
        now = time.time()
        if now - last_print >= 1.0:
            print("Waiting for CoppeliaSim simulation start. Press Play in CoppeliaSim.")
            last_print = now
        time.sleep(0.2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect final VKR scene telemetry through CoppeliaSim ZMQ Remote API.")
    parser.add_argument("--host", default="127.0.0.1", help="ZMQ Remote API host.")
    parser.add_argument("--port", default=23000, type=int, help="ZMQ Remote API port.")
    parser.add_argument("--duration", type=float, default=None, help="Optional collection duration in seconds.")
    parser.add_argument("--period", type=float, default=0.05, help="Polling period in seconds.")
    parser.add_argument("--print-interval", type=float, default=1.0, help="Console status interval in seconds.")
    parser.add_argument("--run-id", default="final_scene_live", help="Run identifier written into JSONL.")
    parser.add_argument("--scenario", default="S0", help="Scenario label written into JSONL.")
    parser.add_argument("--cycle", default=1, type=int, help="Cycle number written into JSONL.")
    parser.add_argument("--output", type=Path, default=None, help="Output JSONL path.")
    parser.add_argument(
        "--wait-for-simulation",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Wait until CoppeliaSim simulation is running before writing telemetry.",
    )
    parser.add_argument("--stop-on-phase", default="", help="Optional cycle phase that stops collection.")
    parser.add_argument("--stop-delay", type=float, default=1.0, help="Seconds to keep recording after stop phase appears.")
    parser.add_argument("--influx-live", action="store_true", help="Write live motor telemetry and cycle state to InfluxDB.")
    parser.add_argument("--influx-url", default="http://localhost:8086", help="InfluxDB base URL for live export.")
    parser.add_argument("--influx-org", default="vkr_org", help="InfluxDB organization for live export.")
    parser.add_argument("--influx-bucket", default="vkr_pak", help="InfluxDB bucket for live export.")
    parser.add_argument("--influx-token", default="vkr-local-token-2026", help="InfluxDB token for live export.")
    parser.add_argument("--influx-batch-size", type=int, default=250, help="Live InfluxDB write batch size in line-protocol rows.")
    parser.add_argument("--influx-timeout", type=float, default=5.0, help="InfluxDB write timeout in seconds.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collect(args)


if __name__ == "__main__":
    main()
