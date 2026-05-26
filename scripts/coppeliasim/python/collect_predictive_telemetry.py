from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CLIENT_SRC = ROOT / "programming" / "zmqRemoteApi" / "clients" / "python" / "src"
sys.path.insert(0, str(CLIENT_SRC))

from coppeliasim_zmqremoteapi_client import RemoteAPIClient


DEFAULT_OUTPUT = ROOT / "telemetry" / "irb140_predictive_telemetry.jsonl"
QUEUE_PROPERTY = "customData.predictiveTelemetry.queue"


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


def try_get_controller(sim) -> int | None:
    try:
        return sim.getObject("/cellController")
    except Exception:
        return None


def read_queue(sim, controller: int) -> list[dict[str, Any]]:
    packed = sim.getBufferProperty(controller, QUEUE_PROPERTY, {"noError": True})
    if not packed:
        return []
    unpacked = normalize_packed_value(sim.unpackTable(packed))
    if isinstance(unpacked, list):
        return [packet for packet in unpacked if isinstance(packet, dict)]
    if isinstance(unpacked, dict):
        return [unpacked]
    return []


def collect_packets(
    sim,
    *,
    duration_s: float | None,
    poll_interval_s: float,
    output_path: Path,
) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    start_time = time.time()
    last_seq = 0
    written = 0
    controller = None

    print(f"Writing telemetry to: {output_path}")

    with output_path.open("a", encoding="utf-8") as stream:
        while True:
            if duration_s is not None and time.time() - start_time >= duration_s:
                return written

            if controller is None:
                controller = try_get_controller(sim)
                if controller is None:
                    time.sleep(poll_interval_s)
                    continue

            try:
                packets = read_queue(sim, controller)
            except Exception:
                controller = None
                time.sleep(poll_interval_s)
                continue

            new_packets = 0
            for packet in packets:
                seq = int(packet.get("seq", 0))
                if seq <= last_seq:
                    continue
                stream.write(json.dumps(packet, ensure_ascii=False) + "\n")
                last_seq = seq
                written += 1
                new_packets += 1

            if new_packets:
                stream.flush()
                print(f"Saved {new_packets} packet(s), last seq={last_seq}")

            time.sleep(poll_interval_s)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect predictive telemetry from CoppeliaSim into JSONL.")
    parser.add_argument("--host", default="127.0.0.1", help="ZMQ remote API host.")
    parser.add_argument("--port", default=23000, type=int, help="ZMQ remote API port.")
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Optional collection duration in seconds. If omitted, runs until interrupted.",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=0.5,
        help="Polling interval in seconds.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output JSONL path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = RemoteAPIClient(args.host, args.port)
    sim = client.require("sim")
    written = collect_packets(
        sim,
        duration_s=args.duration,
        poll_interval_s=args.poll_interval,
        output_path=args.output,
    )
    print(f"Done. Packets written: {written}")


if __name__ == "__main__":
    main()
