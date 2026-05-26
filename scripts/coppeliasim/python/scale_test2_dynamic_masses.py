from __future__ import annotations

import json
import time
from pathlib import Path

from remote_ik_demo import RemoteAPIClient, constants


MODEL_PATH = "/base_respondable"
TARGET_DYNAMIC_MASS_KG = 1650.0
OUTPUT_SCENE = Path(r"C:\Users\egork\Desktop\coppelia_dpilom\test2_torque_graphs_mass1650.ttt")
REPORT = Path("test2_mass_scaling_report.json")


def connect() -> tuple[RemoteAPIClient, int]:
    last_error = None
    for port in (23000, 23001, 23050, 23051):
        client = RemoteAPIClient(port=port)
        client.socket.RCVTIMEO = 5000
        try:
            client.call("zmqRemoteApi.require", ["sim"])
            client.socket.RCVTIMEO = 120000
            return client, port
        except Exception as exc:
            last_error = exc
            client.close()
    raise RuntimeError(f"Could not connect to CoppeliaSim ZMQ remote API: {last_error!r}")


def wait_stopped(client: RemoteAPIClient, sim: dict[str, int]) -> None:
    for _ in range(160):
        if client.call("sim.getSimulationState") == sim["simulation_stopped"]:
            return
        client.call("sim.stopSimulation")
        time.sleep(0.05)
    raise RuntimeError("Simulation did not stop")


def short(name: str) -> str:
    return name.rsplit("/", 1)[-1]


def main() -> None:
    client, port = connect()
    try:
        sim = constants(client.call("zmqRemoteApi.info", ["sim"]))
        wait_stopped(client, sim)

        root = client.call("sim.getObject", [MODEL_PATH])
        shapes = client.call("sim.getObjectsInTree", [root, sim["sceneobject_shape"], 0])

        candidates = []
        ignored = []
        for shape in shapes:
            alias = client.call("sim.getObjectAlias", [shape, 1])
            mass = float(client.call("sim.getShapeMass", [shape]))
            static = int(client.call("sim.getObjectInt32Param", [shape, sim["shapeintparam_static"]]))
            respondable = int(client.call("sim.getObjectInt32Param", [shape, sim["shapeintparam_respondable"]]))
            row = {
                "handle": shape,
                "alias": alias,
                "name": short(alias),
                "mass_before_kg": mass,
                "static": static,
                "respondable": respondable,
            }
            if static == 0 and respondable != 0 and mass > 0:
                candidates.append(row)
            else:
                ignored.append(row)

        before_total = sum(item["mass_before_kg"] for item in candidates)
        if before_total <= 0:
            raise RuntimeError("No dynamic respondable shapes with positive mass found")

        scale = TARGET_DYNAMIC_MASS_KG / before_total
        for item in candidates:
            shape = item["handle"]
            inertia, com = client.call("sim.getShapeInertia", [shape])
            new_inertia = [float(value) * scale for value in inertia]
            new_mass = item["mass_before_kg"] * scale
            client.call("sim.setShapeMass", [shape, new_mass])
            client.call("sim.setShapeInertia", [shape, new_inertia, com])
            item["mass_after_kg"] = new_mass

        after_total = 0.0
        for item in candidates:
            item["mass_after_verified_kg"] = float(client.call("sim.getShapeMass", [item["handle"]]))
            after_total += item["mass_after_verified_kg"]

        client.call("sim.saveScene", [str(OUTPUT_SCENE)])

        for item in candidates + ignored:
            item.pop("handle", None)

        report = {
            "connected_port": port,
            "model": MODEL_PATH,
            "target_dynamic_respondable_mass_kg": TARGET_DYNAMIC_MASS_KG,
            "dynamic_respondable_mass_before_kg": before_total,
            "dynamic_respondable_mass_after_kg": after_total,
            "uniform_mass_and_inertia_scale": scale,
            "scaled_shapes": candidates,
            "ignored_shapes": ignored,
            "scene_out": str(OUTPUT_SCENE),
        }
        REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        print(f"connected_port={port}")
        print(f"scaled_shape_count={len(candidates)}")
        print(f"before_dynamic_respondable_mass_kg={before_total:.6f}")
        print(f"scale={scale:.9f}")
        print(f"after_dynamic_respondable_mass_kg={after_total:.6f}")
        print(f"scene_out={OUTPUT_SCENE}")
        print(f"report={REPORT}")
        for item in sorted(candidates, key=lambda x: x["alias"]):
            print(f"{item['alias']}: {item['mass_before_kg']:.6f} -> {item['mass_after_verified_kg']:.6f} kg")
    finally:
        client.close()


if __name__ == "__main__":
    main()
