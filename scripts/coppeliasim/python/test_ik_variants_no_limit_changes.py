from __future__ import annotations

import json
import math
import time
from pathlib import Path

from remote_ik_demo import RemoteAPIClient, constants


SCENE = Path(r"C:\Users\egork\Desktop\coppelia_dpilom\test1.ttt")
MODEL = "/base_respondable"
TIP = f"{MODEL}/tip"
TARGET = f"{MODEL}/target"
ABS_TARGET = [1.71638, -0.97206, 1.1409]
REPORT = Path("ik_variant_report.json")


def wait_stopped(client: RemoteAPIClient, sim: dict[str, int]) -> None:
    for _ in range(120):
        if client.call("sim.getSimulationState") == sim["simulation_stopped"]:
            return
        client.call("sim.stopSimulation")
        time.sleep(0.05)
    raise RuntimeError("simulation did not stop")


def safe_get(client: RemoteAPIClient, path: str) -> int | None:
    try:
        return client.call("sim.getObject", [path])
    except Exception:
        return None


def distance(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def dget(mapping: dict, key: int):
    return mapping.get(key, mapping.get(str(key)))


def merge_maps(dst: dict, src: dict | None) -> None:
    if src:
        dst.update(src)


def alias(client: RemoteAPIClient, handle: int) -> str:
    return client.call("sim.getObjectAlias", [handle, 1])


def load_test_scene(client: RemoteAPIClient, sim: dict[str, int]) -> None:
    wait_stopped(client, sim)
    client.call("sim.loadScene", [str(SCENE)])
    # Remove only known scripts/proxy from previous experiments if the file happens to contain them.
    for path in (
        f"{MODEL}/script",
        f"{MODEL}/ik_proxy_target",
        f"{MODEL}/IK_example7_parallel",
        f"{MODEL}/IK_all_axes_no_dummy",
        f"{MODEL}/IK",
    ):
        h = safe_get(client, path)
        if h is not None:
            client.call("sim.removeObjects", [[h]])


def set_problem_target(client: RemoteAPIClient) -> None:
    target = client.call("sim.getObject", [TARGET])
    client.call("sim.setObjectPosition", [target, -1, ABS_TARGET])


def loop_pairs(sim_ik: dict[str, int], mode: str = "p3_position") -> list[tuple[str, str, int]]:
    xz = sim_ik["constraint_x"] + sim_ik["constraint_z"]
    xy = sim_ik["constraint_x"] + sim_ik["constraint_y"]
    pos = sim_ik["constraint_position"]
    p3 = {
        "p3_position": pos,
        "p3_xz": xz,
        "p3_xy": xy,
        "all_position": pos,
    }[mode]
    other = pos if mode == "all_position" else xz
    return [
        (f"{MODEL}/dummy1A", f"{MODEL}/dummy1B", other),
        (f"{MODEL}/dummy2A", f"{MODEL}/dummy2B", other),
        (f"{MODEL}/dummy3A", f"{MODEL}/dummy3B", p3),
        (f"{MODEL}/dummy4B", f"{MODEL}/dummy4A", other),
    ]


def measure(client: RemoteAPIClient) -> dict:
    tip = client.call("sim.getObject", [TIP])
    target = client.call("sim.getObject", [TARGET])
    tip_pos = client.call("sim.getObjectPosition", [tip, -1])
    target_pos = client.call("sim.getObjectPosition", [target, -1])
    loops: list[float] = []
    for i in range(1, 5):
        a = client.call("sim.getObject", [f"{MODEL}/dummy{i}A"])
        b = client.call("sim.getObject", [f"{MODEL}/dummy{i}B"])
        loops.append(
            distance(
                client.call("sim.getObjectPosition", [a, -1]),
                client.call("sim.getObjectPosition", [b, -1]),
            )
        )
    return {
        "tip_error_m": distance(tip_pos, target_pos),
        "loop_errors_m": loops,
        "max_loop_error_m": max(loops),
        "tip_pos": tip_pos,
        "target_pos": target_pos,
    }


def joint_snapshot(client: RemoteAPIClient, sim: dict[str, int]) -> list[dict]:
    root = client.call("sim.getObject", [MODEL])
    out = []
    for joint in client.call("sim.getObjectsInTree", [root, sim["sceneobject_joint"], 0]):
        cyclic, interval = client.call("sim.getJointInterval", [joint])
        out.append(
            {
                "alias": alias(client, joint),
                "type": client.call("sim.getJointType", [joint]),
                "cyclic": cyclic,
                "interval": interval,
                "position": client.call("sim.getJointPosition", [joint]),
            }
        )
    return out


def intervals_unchanged(before: list[dict], after: list[dict]) -> bool:
    by_name = {item["alias"]: item for item in before}
    for item in after:
        src = by_name.get(item["alias"])
        if src is None:
            return False
        if src["cyclic"] != item["cyclic"]:
            return False
        if any(abs(a - b) > 1e-12 for a, b in zip(src["interval"], item["interval"])):
            return False
    return True


class IkBuild:
    def __init__(self, env: int, groups: list[int], joints: list[int], ik_to_sim: dict):
        self.env = env
        self.groups = groups
        self.joints = joints
        self.ik_to_sim = ik_to_sim


def set_group_calc(client: RemoteAPIClient, sim_ik: dict[str, int], env: int, group: int) -> None:
    client.call(
        "simIK.setGroupCalculation",
        [env, group, sim_ik["method_damped_least_squares"], 0.08, 160],
    )


def add_target_element(
    client: RemoteAPIClient,
    sim_ik: dict[str, int],
    env: int,
    group: int,
    target_handle: int,
    ik_to_sim: dict,
    weight: float = 1.0,
) -> None:
    base = client.call("sim.getObject", [MODEL])
    tip = client.call("sim.getObject", [TIP])
    element, _sim_to_ik, local_ik_to_sim = client.call(
        "simIK.addElementFromScene",
        [env, group, base, tip, target_handle, sim_ik["constraint_position"]],
    )
    merge_maps(ik_to_sim, local_ik_to_sim)
    client.call("simIK.setElementWeights", [env, group, element, [weight, 0.0]])
    client.call("simIK.setElementPrecision", [env, group, element, [0.001, math.radians(1)]])


def add_loop_elements(
    client: RemoteAPIClient,
    sim_ik: dict[str, int],
    env: int,
    group: int,
    ik_to_sim: dict,
    pair_mode: str,
    weight: float = 1.0,
) -> None:
    base = client.call("sim.getObject", [MODEL])
    for a_path, b_path, constraint in loop_pairs(sim_ik, pair_mode):
        element, _sim_to_ik, local_ik_to_sim = client.call(
            "simIK.addElementFromScene",
            [
                env,
                group,
                base,
                client.call("sim.getObject", [a_path]),
                client.call("sim.getObject", [b_path]),
                constraint,
            ],
        )
        merge_maps(ik_to_sim, local_ik_to_sim)
        client.call("simIK.setElementWeights", [env, group, element, [weight, 0.0]])
        client.call("simIK.setElementPrecision", [env, group, element, [0.001, math.radians(1)]])


def configure_joints(
    client: RemoteAPIClient,
    sim: dict[str, int],
    sim_ik: dict[str, int],
    env: int,
    joints: list[int],
    ik_to_sim: dict,
    active: str,
) -> dict:
    active_aliases = []
    passive_aliases = []
    motor_names = {f"{MODEL}/motor1", f"{MODEL}/motor2", f"{MODEL}/motor3", f"{MODEL}/motor4"}
    for ik_joint in joints:
        sim_joint = dget(ik_to_sim, ik_joint)
        sim_alias = alias(client, sim_joint) if sim_joint is not None else f"ik:{ik_joint}"
        is_active = True
        if active == "axis16_passive" and sim_alias.endswith("/axis16"):
            is_active = False
        elif active == "motors_only" and sim_alias not in motor_names:
            is_active = False

        if is_active:
            client.call("simIK.setJointMode", [env, ik_joint, sim_ik["jointmode_ik"]])
            active_aliases.append(sim_alias)
        else:
            client.call("simIK.setJointMode", [env, ik_joint, sim_ik["jointmode_passive"]])
            passive_aliases.append(sim_alias)

        client.call("simIK.setJointWeight", [env, ik_joint, 1.0])
        if sim_joint is not None and client.call("sim.getJointType", [sim_joint]) == sim["joint_prismatic"]:
            client.call("simIK.setJointMaxStepSize", [env, ik_joint, 0.02])
        else:
            client.call("simIK.setJointMaxStepSize", [env, ik_joint, math.radians(8)])
    return {"active": active_aliases, "passive": passive_aliases}


def build_single_group(
    client: RemoteAPIClient,
    sim: dict[str, int],
    sim_ik: dict[str, int],
    pair_mode: str = "p3_position",
    active: str = "all",
    target_handle: int | None = None,
    target_weight: float = 1.0,
    loop_weight: float = 1.0,
) -> tuple[IkBuild, dict]:
    env = client.call("simIK.createEnvironment")
    group = client.call("simIK.createGroup", [env])
    set_group_calc(client, sim_ik, env, group)
    ik_to_sim: dict = {}
    add_target_element(
        client,
        sim_ik,
        env,
        group,
        target_handle if target_handle is not None else client.call("sim.getObject", [TARGET]),
        ik_to_sim,
        target_weight,
    )
    add_loop_elements(client, sim_ik, env, group, ik_to_sim, pair_mode, loop_weight)
    joints = client.call("simIK.getGroupJoints", [env, group])
    joint_info = configure_joints(client, sim, sim_ik, env, joints, ik_to_sim, active)
    return IkBuild(env, [group], joints, ik_to_sim), joint_info


def build_target_only_group(
    client: RemoteAPIClient,
    sim: dict[str, int],
    sim_ik: dict[str, int],
    active: str = "all",
) -> tuple[IkBuild, dict]:
    env = client.call("simIK.createEnvironment")
    group = client.call("simIK.createGroup", [env])
    set_group_calc(client, sim_ik, env, group)
    ik_to_sim: dict = {}
    add_target_element(client, sim_ik, env, group, client.call("sim.getObject", [TARGET]), ik_to_sim)
    joints = client.call("simIK.getGroupJoints", [env, group])
    joint_info = configure_joints(client, sim, sim_ik, env, joints, ik_to_sim, active)
    return IkBuild(env, [group], joints, ik_to_sim), joint_info


def build_priority_groups(
    client: RemoteAPIClient,
    sim: dict[str, int],
    sim_ik: dict[str, int],
    order: str,
    pair_mode: str = "p3_position",
    active: str = "all",
) -> tuple[IkBuild, dict]:
    env = client.call("simIK.createEnvironment")
    target_group = client.call("simIK.createGroup", [env])
    closure_group = client.call("simIK.createGroup", [env])
    set_group_calc(client, sim_ik, env, target_group)
    set_group_calc(client, sim_ik, env, closure_group)
    ik_to_sim: dict = {}
    add_target_element(client, sim_ik, env, target_group, client.call("sim.getObject", [TARGET]), ik_to_sim)
    add_loop_elements(client, sim_ik, env, closure_group, ik_to_sim, pair_mode)
    groups = [closure_group, target_group] if order == "closure_first" else [target_group, closure_group]
    joints = sorted(
        set(client.call("simIK.getGroupJoints", [env, target_group]))
        | set(client.call("simIK.getGroupJoints", [env, closure_group]))
    )
    joint_info = configure_joints(client, sim, sim_ik, env, joints, ik_to_sim, active)
    return IkBuild(env, groups, joints, ik_to_sim), joint_info


def cleanup_build(client: RemoteAPIClient, build: IkBuild | None) -> None:
    if build is not None:
        try:
            client.call("simIK.eraseEnvironment", [build.env])
        except Exception:
            pass


def run_local_variant(
    client: RemoteAPIClient,
    sim: dict[str, int],
    sim_ik: dict[str, int],
    *,
    name: str,
    pair_mode: str = "p3_position",
    active: str = "all",
    target_weight: float = 1.0,
    loop_weight: float = 1.0,
    steps: int = 320,
) -> dict:
    build = None
    try:
        set_problem_target(client)
        before = measure(client)
        build, joint_info = build_single_group(
            client,
            sim,
            sim_ik,
            pair_mode=pair_mode,
            active=active,
            target_weight=target_weight,
            loop_weight=loop_weight,
        )
        last = None
        for _ in range(steps):
            last = client.call(
                "simIK.handleGroup",
                [build.env, build.groups[0], {"syncWorlds": True, "allowError": True}],
            )
        after = measure(client)
        return {
            "name": name,
            "kind": "handleGroup",
            "pair_mode": pair_mode,
            "active_policy": active,
            "target_weight": target_weight,
            "loop_weight": loop_weight,
            "before": before,
            "after": after,
            "last_result": last,
            "joint_info": joint_info,
        }
    finally:
        cleanup_build(client, build)


def run_priority_variant(
    client: RemoteAPIClient,
    sim: dict[str, int],
    sim_ik: dict[str, int],
    *,
    name: str,
    order: str,
    pair_mode: str = "p3_position",
    steps: int = 320,
) -> dict:
    build = None
    try:
        set_problem_target(client)
        before = measure(client)
        build, joint_info = build_priority_groups(client, sim, sim_ik, order=order, pair_mode=pair_mode)
        last = None
        for _ in range(steps):
            last = client.call(
                "simIK.handleGroups",
                [build.env, build.groups, {"syncWorlds": True, "allowError": True}],
            )
        after = measure(client)
        return {
            "name": name,
            "kind": "handleGroups",
            "order": order,
            "pair_mode": pair_mode,
            "before": before,
            "after": after,
            "last_result": last,
            "joint_info": joint_info,
        }
    finally:
        cleanup_build(client, build)


def apply_config(client: RemoteAPIClient, build: IkBuild, config: list[float]) -> None:
    for ik_joint, value in zip(build.joints, config):
        client.call("simIK.setJointPosition", [build.env, ik_joint, value])
    client.call("simIK.syncToSim", [build.env, build.groups])


def run_find_configs_variant(
    client: RemoteAPIClient,
    sim: dict[str, int],
    sim_ik: dict[str, int],
    *,
    name: str,
    pair_mode: str = "p3_position",
    max_time: float = 3.0,
    max_dist: float = 4.0,
    refine_steps: int = 100,
) -> dict:
    build = None
    try:
        set_problem_target(client)
        before = measure(client)
        build, joint_info = build_single_group(client, sim, sim_ik, pair_mode=pair_mode)
        params = {
            "maxDist": max_dist,
            "maxTime": max_time,
            "pMetric": [1.0, 1.0, 1.0, 0.05],
            "cMetric": [1.0] * len(build.joints),
            "findMultiple": False,
        }
        configs = client.call("simIK.findConfigs", [build.env, build.groups[0], build.joints, params])
        found = len(configs) if isinstance(configs, list) else 0
        if found:
            apply_config(client, build, configs[0])
            for _ in range(refine_steps):
                client.call(
                    "simIK.handleGroup",
                    [build.env, build.groups[0], {"syncWorlds": True, "allowError": True}],
                )
        after = measure(client)
        return {
            "name": name,
            "kind": "findConfigs",
            "pair_mode": pair_mode,
            "found": found,
            "before": before,
            "after": after,
            "joint_info": joint_info,
        }
    finally:
        cleanup_build(client, build)


def run_target_seed_then_closure_variant(
    client: RemoteAPIClient,
    sim: dict[str, int],
    sim_ik: dict[str, int],
    *,
    name: str,
    pair_mode: str = "p3_position",
    max_time: float = 3.0,
    max_dist: float = 4.0,
    refine_steps: int = 220,
) -> dict:
    seed_build = None
    full_build = None
    try:
        set_problem_target(client)
        before = measure(client)
        seed_build, seed_joint_info = build_target_only_group(client, sim, sim_ik)
        seed_params = {
            "maxDist": max_dist,
            "maxTime": max_time,
            "pMetric": [1.0, 1.0, 1.0, 0.05],
            "cMetric": [1.0] * len(seed_build.joints),
            "findMultiple": False,
        }
        seed_configs = client.call(
            "simIK.findConfigs", [seed_build.env, seed_build.groups[0], seed_build.joints, seed_params]
        )
        seed_found = len(seed_configs) if isinstance(seed_configs, list) else 0
        if seed_found:
            apply_config(client, seed_build, seed_configs[0])

        cleanup_build(client, seed_build)
        seed_build = None

        full_build, full_joint_info = build_single_group(client, sim, sim_ik, pair_mode=pair_mode)
        last = None
        for _ in range(refine_steps):
            last = client.call(
                "simIK.handleGroup",
                [full_build.env, full_build.groups[0], {"syncWorlds": True, "allowError": True}],
            )
        after = measure(client)
        return {
            "name": name,
            "kind": "target_seed_then_full_closure",
            "pair_mode": pair_mode,
            "seed_found": seed_found,
            "before": before,
            "after": after,
            "last_result": last,
            "joint_info": {"seed": seed_joint_info, "full": full_joint_info},
        }
    finally:
        cleanup_build(client, seed_build)
        cleanup_build(client, full_build)


def run_proxy_rollback_variant(
    client: RemoteAPIClient,
    sim: dict[str, int],
    sim_ik: dict[str, int],
    *,
    name: str,
    pair_mode: str = "p3_position",
    steps: int = 600,
    max_target_step: float = 0.01,
    max_loop_error: float = 0.002,
) -> dict:
    build = None
    proxy = None
    try:
        set_problem_target(client)
        base = client.call("sim.getObject", [MODEL])
        tip = client.call("sim.getObject", [TIP])
        target = client.call("sim.getObject", [TARGET])
        proxy = client.call("sim.createDummy", [0.04])
        client.call("sim.setObjectAlias", [proxy, "ik_test_proxy_target"])
        client.call("sim.setObjectParent", [proxy, base, True])
        client.call("sim.setObjectMatrix", [proxy, -1, client.call("sim.getObjectMatrix", [tip, -1])])
        build, joint_info = build_single_group(client, sim, sim_ik, pair_mode=pair_mode, target_handle=proxy)
        sim_joints = []
        for ik_joint in build.joints:
            sj = dget(build.ik_to_sim, ik_joint)
            if sj is not None:
                sim_joints.append(sj)
        before = measure(client)
        accepted = 0
        rejected = 0
        last = None
        for _ in range(steps):
            prev_cfg = [client.call("sim.getJointPosition", [j]) for j in sim_joints]
            prev_proxy = client.call("sim.getObjectMatrix", [proxy, -1])
            p = client.call("sim.getObjectPosition", [proxy, -1])
            q = client.call("sim.getObjectPosition", [target, -1])
            delta = [q[i] - p[i] for i in range(3)]
            length = distance(p, q)
            if length > max_target_step:
                q = [p[i] + delta[i] / length * max_target_step for i in range(3)]
            client.call("sim.setObjectPosition", [proxy, -1, q])
            client.call("sim.setObjectOrientation", [proxy, -1, client.call("sim.getObjectOrientation", [target, -1])])
            last = client.call(
                "simIK.handleGroup",
                [build.env, build.groups[0], {"syncWorlds": True, "allowError": True}],
            )
            now = measure(client)
            if now["max_loop_error_m"] <= max_loop_error:
                accepted += 1
            else:
                rejected += 1
                for j, v in zip(sim_joints, prev_cfg):
                    client.call("sim.setJointPosition", [j, v])
                client.call("sim.setObjectMatrix", [proxy, -1, prev_proxy])
        after = measure(client)
        return {
            "name": name,
            "kind": "proxy_rollback",
            "pair_mode": pair_mode,
            "accepted": accepted,
            "rejected": rejected,
            "before": before,
            "after": after,
            "last_result": last,
            "joint_info": joint_info,
        }
    finally:
        cleanup_build(client, build)
        if proxy is not None:
            try:
                client.call("sim.removeObjects", [[proxy]])
            except Exception:
                pass


def main() -> None:
    client = RemoteAPIClient()
    client.socket.RCVTIMEO = 180000
    try:
        client.call("zmqRemoteApi.require", ["sim"])
        client.call("zmqRemoteApi.require", ["simIK"])
        sim = constants(client.call("zmqRemoteApi.info", ["sim"]))
        sim_ik = constants(client.call("zmqRemoteApi.info", ["simIK"]))

        variants = [
            ("local_all_axes_p3_position", lambda: run_local_variant(client, sim, sim_ik, name="local_all_axes_p3_position")),
            ("local_all_axes_p3_xz", lambda: run_local_variant(client, sim, sim_ik, name="local_all_axes_p3_xz", pair_mode="p3_xz")),
            ("local_all_axes_p3_xy", lambda: run_local_variant(client, sim, sim_ik, name="local_all_axes_p3_xy", pair_mode="p3_xy")),
            ("local_all_pairs_position", lambda: run_local_variant(client, sim, sim_ik, name="local_all_pairs_position", pair_mode="all_position")),
            ("local_axis16_passive", lambda: run_local_variant(client, sim, sim_ik, name="local_axis16_passive", active="axis16_passive")),
            ("local_motors_only", lambda: run_local_variant(client, sim, sim_ik, name="local_motors_only", active="motors_only")),
            ("priority_closure_first", lambda: run_priority_variant(client, sim, sim_ik, name="priority_closure_first", order="closure_first")),
            ("priority_target_first", lambda: run_priority_variant(client, sim, sim_ik, name="priority_target_first", order="target_first")),
            ("find_configs_all_axes", lambda: run_find_configs_variant(client, sim, sim_ik, name="find_configs_all_axes")),
            ("target_seed_then_closure", lambda: run_target_seed_then_closure_variant(client, sim, sim_ik, name="target_seed_then_closure")),
            ("proxy_rollback_guard", lambda: run_proxy_rollback_variant(client, sim, sim_ik, name="proxy_rollback_guard")),
        ]

        report = {
            "scene": str(SCENE),
            "target_world_m": ABS_TARGET,
            "note": "No sim.setJointInterval calls are made; scene is reloaded between variants.",
            "variants": [],
        }
        for name, runner in variants:
            load_test_scene(client, sim)
            before_intervals = joint_snapshot(client, sim)
            print(f"RUN {name}", flush=True)
            try:
                result = runner()
                result["ok_for_target"] = result["after"]["tip_error_m"] <= 0.01
                result["ok_for_loops"] = result["after"]["max_loop_error_m"] <= 0.002
                result["works"] = result["ok_for_target"] and result["ok_for_loops"]
                result["error"] = None
            except Exception as exc:
                result = {
                    "name": name,
                    "error": repr(exc),
                    "works": False,
                    "ok_for_target": False,
                    "ok_for_loops": False,
                }
            after_intervals = joint_snapshot(client, sim)
            result["joint_intervals_unchanged"] = intervals_unchanged(before_intervals, after_intervals)
            report["variants"].append(result)
            if result.get("after"):
                loops = result["after"]["loop_errors_m"]
                print(
                    "  tip={:.5f} max_loop={:.5f} loops=[{}] works={} intervals={}".format(
                        result["after"]["tip_error_m"],
                        result["after"]["max_loop_error_m"],
                        ", ".join(f"{v:.5f}" for v in loops),
                        result["works"],
                        result["joint_intervals_unchanged"],
                    ),
                    flush=True,
                )
            else:
                print(f"  ERROR {result['error']}", flush=True)

        load_test_scene(client, sim)
        REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"REPORT {REPORT.resolve()}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
