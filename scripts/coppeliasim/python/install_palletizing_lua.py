from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_LUA = PROJECT_ROOT / "scripts" / "coppeliasim" / "lua" / "final_scene_palletizing_cycle.lua"
MODEL_PATH = "/base_respondable"
SCRIPT_PATH = "/base_respondable/palletizing_cycle_script"


def add_remote_api_paths() -> None:
    candidates = [
        os.environ.get("COPPELIASIM_ZMQ_CLIENT_PATH"),
        r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\programming\zmqRemoteApi\clients\python\src",
        r"C:\Program Files\CoppeliaRobotics\CoppeliaSim\programming\zmqRemoteApi\clients\python\src",
        r"C:\Program Files (x86)\CoppeliaRobotics\CoppeliaSimEdu\programming\zmqRemoteApi\clients\python\src",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            sys.path.insert(0, candidate)
            return


add_remote_api_paths()

try:
    from coppeliasim_zmqremoteapi_client import RemoteAPIClient
except ImportError as exc:
    raise SystemExit(
        "Cannot import coppeliasim_zmqremoteapi_client. Set COPPELIASIM_ZMQ_CLIENT_PATH "
        "to CoppeliaSim's programming\\zmqRemoteApi\\clients\\python\\src directory."
    ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install the canonical palletizing Lua script into the open CoppeliaSim scene.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=23000)
    parser.add_argument("--lua", default=str(DEFAULT_LUA))
    parser.add_argument("--save-scene", action="store_true", help="Save the currently open scene after script update.")
    return parser.parse_args()


def candidate_script_handles(sim) -> list[tuple[str, int]]:
    candidates: list[tuple[str, int]] = []
    try:
        handle = sim.getObject(SCRIPT_PATH)
        candidates.append((SCRIPT_PATH, handle))
    except Exception:
        pass
    try:
        model = sim.getObject(MODEL_PATH)
        handle = sim.getScript(sim.scripttype_childscript, model)
        candidates.append((f"child script attached to {MODEL_PATH}", handle))
    except Exception:
        pass
    return candidates


def main() -> None:
    args = parse_args()
    lua_path = Path(args.lua)
    if not lua_path.is_absolute():
        lua_path = PROJECT_ROOT / lua_path
    source = lua_path.read_text(encoding="utf-8")

    client = RemoteAPIClient(args.host, args.port)
    sim = client.require("sim")

    errors: list[str] = []
    for label, script_handle in candidate_script_handles(sim):
        try:
            sim.setScriptText(script_handle, source)
            print(f"installed_script={label}")
            print(f"source={lua_path}")
            if args.save_scene:
                sim.saveScene()
                print("scene_saved=1")
            return
        except Exception as exc:
            errors.append(f"{label}: {exc}")

    details = "\n".join(errors) if errors else "No candidate script handles found."
    raise SystemExit(f"Could not install Lua script into CoppeliaSim.\n{details}")


if __name__ == "__main__":
    main()
