from __future__ import annotations

import math
import time
from pathlib import Path

from remote_ik_demo import RemoteAPIClient, constants


MODEL_PATH = "/base_respondable"
TIP_PATH = f"{MODEL_PATH}/tip"
TARGET_PATH = f"{MODEL_PATH}/target"
SCRIPT_ALIAS = "IK_example7_parallel"
SCRIPT_PATH = f"{MODEL_PATH}/{SCRIPT_ALIAS}"

# The first dummy is the branch adjusted by its closure IK group.  The second
# dummy is on the branch treated as the already positioned reference.
LOOP_SPECS = [
    ("dummy1A", "dummy1B", 2.0, ("axis5", "axis8")),
    ("dummy2A", "dummy2B", 2.0, ("motor3", "axis6", "axis11")),
    ("dummy3A", "dummy3B", 2.0, ("axis9",)),
    ("dummy4B", "dummy4A", 2.0, ("axis4", "axis10", "axis12")),
]


CONTROL_SCRIPT = r"""
sim = require 'sim'
simIK = require 'simIK'

local modelPath = '/base_respondable'

local loopSpecs = {
LOOP_SPEC_ROWS
}

local targetActiveJoints = {
    motor1 = true,
    motor2 = true,
    axis7 = true,
    axis14 = true,
    axis15 = true,
}

local function basename(path)
    return path:match('[^/]+$')
end

local function getAlias(h)
    return basename(sim.getObjectAlias(h, 1))
end

local function setGroupRestoreFlags(group)
    local flags = simIK.getGroupFlags(ikEnv, group)
    flags = flags | simIK.group_restoreonbadlintol | simIK.group_restoreonbadangtol
    simIK.setGroupFlags(ikEnv, group, flags)
end

local function tuneTargetJoints(map)
    local joints = simIK.getGroupJoints(ikEnv, targetGroup)
    targetIkJoints = joints
    for i = 1, #joints do
        local ikJoint = joints[i]
        local simJoint = map[ikJoint]
        if simJoint then
            local alias = getAlias(simJoint)
            if targetActiveJoints[alias] then
                simIK.setJointMode(ikEnv, ikJoint, simIK.jointmode_ik)
                simIK.setJointWeight(ikEnv, ikJoint, 1.0)
                simIK.setJointMaxStepSize(ikEnv, ikJoint, math.rad(10.0))
            else
                simIK.setJointMode(ikEnv, ikJoint, simIK.jointmode_passive)
            end
        end
    end
end

local function tuneClosureJoints(group, map, active)
    local joints = simIK.getGroupJoints(ikEnv, group)
    for i = 1, #joints do
        local ikJoint = joints[i]
        local simJoint = map[ikJoint]
        if simJoint then
            local alias = getAlias(simJoint)
            local jointType = sim.getJointType(simJoint)
            if active[alias] and jointType ~= sim.joint_prismatic then
                simIK.setJointMode(ikEnv, ikJoint, simIK.jointmode_ik)
                simIK.setJointWeight(ikEnv, ikJoint, 1.0)
                simIK.setJointMaxStepSize(ikEnv, ikJoint, math.rad(10.0))
            else
                simIK.setJointMode(ikEnv, ikJoint, simIK.jointmode_passive)
            end
        end
    end
end

function sysCall_init()
    simBase = sim.getObject(modelPath)
    simTip = sim.getObject(modelPath .. '/tip')
    simTarget = sim.getObject(modelPath .. '/target')

    enabled = true
    handleWhenSimulationRunning = true
    handleWhenSimulationStopped = true

    ikEnv = simIK.createEnvironment()

    -- 1) Serial IK of the main robot branch: gripper tip follows target.
    targetGroup = simIK.createGroup(ikEnv)
    simIK.setGroupCalculation(ikEnv, targetGroup, simIK.method_damped_least_squares, 0.08, 100)
    targetElement, simToIkTargetMap, ikToSimTargetMap = simIK.addElementFromScene(
        ikEnv,
        targetGroup,
        simBase,
        simTip,
        simTarget,
        simIK.constraint_position
    )
    simIK.setElementWeights(ikEnv, targetGroup, targetElement, {1.0, 0.0})
    simIK.setElementPrecision(ikEnv, targetGroup, targetElement, {0.001, math.rad(1)})
    tuneTargetJoints(ikToSimTargetMap)

    -- 2) FK/IK closure of the auxiliary branches, as in example 7:
    -- dummy objects are only closure tips/targets in the IK environment.
    closureGroups = {}
    for i = 1, #loopSpecs do
        local closureGroup = simIK.createGroup(ikEnv)
        simIK.setGroupCalculation(ikEnv, closureGroup, simIK.method_damped_least_squares, 0.08, 80)
        local loopTip = sim.getObject(loopSpecs[i][1])
        local loopTarget = sim.getObject(loopSpecs[i][2])
        local loopElement
        loopElement, simToIkClosureMap, ikToSimClosureMap = simIK.addElementFromScene(
            ikEnv,
            closureGroup,
            simBase,
            loopTip,
            loopTarget,
            simIK.constraint_x + simIK.constraint_z
        )
        simIK.setElementWeights(ikEnv, closureGroup, loopElement, {loopSpecs[i][3], 0.0})
        simIK.setElementPrecision(ikEnv, closureGroup, loopElement, {0.001, math.rad(1)})
        tuneClosureJoints(closureGroup, ikToSimClosureMap, loopSpecs[i][4])
        closureGroups[#closureGroups + 1] = closureGroup
    end
end

function sysCall_actuation()
    if enabled and handleWhenSimulationRunning then handleIk() end
end

function sysCall_nonSimulation()
    if enabled and handleWhenSimulationStopped then handleIk() end
end

function sysCall_cleanup()
    if ikEnv then
        simIK.eraseEnvironment(ikEnv)
        ikEnv = nil
    end
end

function handleIk()
    local tr, tf, tp = simIK.handleGroup(ikEnv, targetGroup, {syncWorlds = true, allowError = true})
    local cr, cf, cp = simIK.result_success, 0, {0, 0}
    local maxClosurePrecision = 0
    for i = 1, #closureGroups do
        cr, cf, cp = simIK.handleGroup(ikEnv, closureGroups[i], {syncWorlds = true, allowError = true})
        if cp and cp[1] and cp[1] > maxClosurePrecision then
            maxClosurePrecision = cp[1]
        end
    end
    local targetPrecision = tp and tp[1] or -1
    sim.setStringSignal(
        'example7_parallel_ik_result',
        tostring(tr) .. ',' .. tostring(tf) .. ',' .. tostring(targetPrecision) .. ';' ..
        tostring(cr) .. ',' .. tostring(cf) .. ',' .. tostring(maxClosurePrecision)
    )
    return tr, tf, targetPrecision, cr, cf, maxClosurePrecision
end

function setEnabled(value)
    enabled = not not value
end

function getIkJoints()
    return targetIkJoints
end
"""


def safe_get(client: RemoteAPIClient, path: str):
    try:
        return client.call("sim.getObject", [path])
    except Exception:
        return None


def wait_stopped(client: RemoteAPIClient, sim: dict[str, int]) -> None:
    for _ in range(100):
        if client.call("sim.getSimulationState") == sim["simulation_stopped"]:
            return
        client.call("sim.stopSimulation")
        time.sleep(0.1)
    raise RuntimeError("Simulation did not stop")


def distance(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def loop_pair_rows() -> str:
    rows = []
    for tip, target, weight, active in LOOP_SPECS:
        active_rows = ", ".join(f"{name} = true" for name in active)
        rows.append(
            f"    {{'{MODEL_PATH}/{tip}', '{MODEL_PATH}/{target}', {weight:.3f}, {{{active_rows}}}}},"
        )
    return "\n".join(rows)


def ensure_kinematic_modes(client: RemoteAPIClient, sim: dict[str, int], root: int) -> list[str]:
    changed: list[str] = []
    joints = client.call("sim.getObjectsInTree", [root, sim["sceneobject_joint"], 0])
    for joint in joints:
        alias = client.call("sim.getObjectAlias", [joint, 1])
        client.call("sim.setJointMode", [joint, sim["jointmode_kinematic"]])
        changed.append(alias)
    return changed


def clear_scene_dummy_links(client: RemoteAPIClient, sim: dict[str, int]) -> list[str]:
    cleared: list[str] = []
    for a_name, b_name, _, _ in LOOP_SPECS:
        for name in (a_name, b_name):
            h = safe_get(client, f"{MODEL_PATH}/{name}")
            if h is None:
                raise RuntimeError(f"Missing {MODEL_PATH}/{name}")
            try:
                client.call("sim.setLinkDummy", [h, -1])
            except Exception:
                pass
            client.call(
                "sim.setObjectInt32Param",
                [h, sim["dummyintparam_link_type"], sim["dummytype_default"]],
            )
            cleared.append(name)
    return cleared


def remove_existing_script(client: RemoteAPIClient, sim: dict[str, int]) -> None:
    script = safe_get(client, SCRIPT_PATH)
    if script is not None:
        client.call("sim.removeObjects", [[script]])


def attach_script(client: RemoteAPIClient, sim: dict[str, int], root: int) -> int:
    remove_existing_script(client, sim)
    text = CONTROL_SCRIPT.replace("LOOP_SPEC_ROWS", loop_pair_rows())
    script = client.call("sim.createScript", [sim["scripttype_customization"], text, 0, "lua"])
    client.call("sim.setObjectAlias", [script, SCRIPT_ALIAS])
    client.call("sim.setObjectParent", [script, root, True])
    client.call("sim.setObjectInt32Param", [script, sim["objintparam_visibility_layer"], 0])
    client.call("sim.initScript", [script])
    return script


def measure_errors(client: RemoteAPIClient) -> tuple[float, list[float]]:
    tip = client.call("sim.getObject", [TIP_PATH])
    target = client.call("sim.getObject", [TARGET_PATH])
    tip_error = distance(
        client.call("sim.getObjectPosition", [tip, -1]),
        client.call("sim.getObjectPosition", [target, -1]),
    )
    loop_errors: list[float] = []
    for i in range(1, 5):
        a = client.call("sim.getObject", [f"{MODEL_PATH}/dummy{i}A"])
        b = client.call("sim.getObject", [f"{MODEL_PATH}/dummy{i}B"])
        loop_errors.append(
            distance(
                client.call("sim.getObjectPosition", [a, -1]),
                client.call("sim.getObjectPosition", [b, -1]),
            )
        )
    return tip_error, loop_errors


def validate(client: RemoteAPIClient, script: int) -> tuple[tuple[float, list[float]], tuple[float, list[float]], str]:
    target = client.call("sim.getObject", [TARGET_PATH])
    original_matrix = client.call("sim.getObjectMatrix", [target, -1])
    original_position = client.call("sim.getObjectPosition", [target, -1])
    before = measure_errors(client)
    client.call(
        "sim.setObjectPosition",
        [target, -1, [original_position[0] - 0.01, original_position[1], original_position[2] + 0.01]],
    )
    last = ""
    for _ in range(40):
        try:
            last = str(client.call("sim.callScriptFunction", ["handleIk", script]))
        except Exception as exc:
            last = f"call failed: {exc}"
        time.sleep(0.02)
    after = measure_errors(client)
    client.call("sim.setObjectMatrix", [target, -1, original_matrix])
    for _ in range(20):
        try:
            client.call("sim.callScriptFunction", ["handleIk", script])
        except Exception:
            pass
        time.sleep(0.02)
    return before, after, last


def main() -> None:
    client = RemoteAPIClient()
    try:
        sim = constants(client.call("zmqRemoteApi.info", ["sim"]))
        wait_stopped(client, sim)
        scene = Path(client.call("sim.getStringParam", [sim["stringparam_scene_path_and_name"]]))
        root = safe_get(client, MODEL_PATH)
        if root is None:
            raise RuntimeError(f"Missing {MODEL_PATH}; open test1.ttt first")
        if safe_get(client, TIP_PATH) is None or safe_get(client, TARGET_PATH) is None:
            raise RuntimeError(f"Missing {TIP_PATH} or {TARGET_PATH}")

        kinematic_joints = ensure_kinematic_modes(client, sim, root)
        cleared_dummies = clear_scene_dummy_links(client, sim)
        script = attach_script(client, sim, root)
        before, after, result = validate(client, script)

        out_scene = scene.with_name(f"{scene.stem}_example7_layers.ttt")
        client.call("sim.setObjectSel", [[client.call("sim.getObject", [TARGET_PATH])]])
        client.call("sim.announceSceneContentChange")
        client.call("sim.saveScene", [str(out_scene)])

        print(f"scene_in={scene}")
        print(f"scene_out={out_scene}")
        print(f"script={SCRIPT_PATH} handle={script}")
        print("kinematic_joints=" + ", ".join(kinematic_joints))
        print("cleared_scene_dummy_links=" + ", ".join(cleared_dummies))
        print(f"validation_result={result}")
        print(f"before_tip_error_m={before[0]:.6f}")
        print("before_loop_errors_m=" + ", ".join(f"{e:.6f}" for e in before[1]))
        print(f"after_test_tip_error_m={after[0]:.6f}")
        print("after_test_loop_errors_m=" + ", ".join(f"{e:.6f}" for e in after[1]))
    finally:
        client.close()


if __name__ == "__main__":
    main()
