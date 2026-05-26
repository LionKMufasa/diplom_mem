from __future__ import annotations

import math
import time
from pathlib import Path

from remote_ik_demo import RemoteAPIClient, constants


MODEL_PATH = "/base_respondable"
TIP_PATH = f"{MODEL_PATH}/tip"
TARGET_PATH = f"{MODEL_PATH}/target"
GRIPPER_PATH = f"{MODEL_PATH}/gripper_respondable"
SCRIPT_ALIAS = "parallel_ik_example7"
SCRIPT_PATH = f"{MODEL_PATH}/{SCRIPT_ALIAS}"

# closureTip, closureTarget, positionWeight.  The closure tip is the branch
# that should be walked from base; the closure target is the matching dummy on
# the main low-arm branch.
LOOP_PAIRS = [
    ("dummy1A", "dummy1B", 3.0),
    ("dummy2A", "dummy2B", 3.0),
    ("dummy3A", "dummy3B", 2.0),
    ("dummy4B", "dummy4A", 2.0),
]

# ABB IRB 660 primary axes.  The rest of the imported revolute joints are
# passive parallelogram joints and get a symmetric -180..180 degree interval.
PRIMARY_REVOLUTE_LIMITS_DEG = {
    "motor1": (-180.0, 180.0),
    "motor2": (-42.0, 85.0),
    "axis7": (-20.0, 120.0),
    "axis15": (-300.0, 300.0),
    "motor4": (-300.0, 300.0),
}
DEFAULT_REVOLUTE_LIMITS_DEG = (-180.0, 180.0)


CONTROL_SCRIPT = r"""
sim = require 'sim'
simIK = require 'simIK'

local modelPath = '/base_respondable'
local loopPairs = {
LOOP_PAIR_ROWS
}

local function basename(path)
    return path:match('[^/]+$')
end

local function tuneJoints(map)
    local joints = simIK.getGroupJoints(ikEnv, ikGroup)
    for i = 1, #joints do
        local ikJoint = joints[i]
        local simJoint = map[ikJoint]
        if simJoint then
            local alias = basename(sim.getObjectAlias(simJoint, 1))
            local jointType = sim.getJointType(simJoint)
            if jointType == sim.joint_prismatic then
                -- Imported prismatic helper joints should not stretch the
                -- parallelogram during this kinematic test.
                simIK.setJointMode(ikEnv, ikJoint, simIK.jointmode_passive)
            else
                local weight = 0.7
                if alias == 'motor1' or alias == 'motor2' or alias == 'axis7' or alias == 'axis15' or alias == 'motor4' then
                    weight = 1.2
                elseif alias == 'axis4' or alias == 'motor3' or alias == 'axis5' or alias == 'axis9' or alias == 'axis13' then
                    weight = 1.0
                end
                simIK.setJointWeight(ikEnv, ikJoint, weight)
                simIK.setJointMaxStepSize(ikEnv, ikJoint, math.rad(4.0))
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
    dampingFactor = 0.08
    maxIterations = 160
    method = simIK.method_damped_least_squares

    targetConstraint = simIK.constraint_position
    loopConstraint = simIK.constraint_position
    ikOptions = {
        syncWorlds = true,
        allowError = false,
    }

    ikEnv = simIK.createEnvironment()

    -- Same structure as the official FK/IK parallel-mechanism example:
    -- one group solves all loop-closure elements and the gripper target.
    ikGroup = simIK.createGroup(ikEnv)
    simIK.setGroupCalculation(ikEnv, ikGroup, method, dampingFactor, maxIterations)
    local flags = simIK.getGroupFlags(ikEnv, ikGroup)
    simIK.setGroupFlags(
        ikEnv,
        ikGroup,
        flags | simIK.group_avoidlimits | simIK.group_restoreonbadlintol | simIK.group_restoreonbadangtol
    )

    for i = 1, #loopPairs do
        local loopTip = sim.getObject(loopPairs[i][1])
        local loopTarget = sim.getObject(loopPairs[i][2])
        local loopElement
        loopElement, simToIkMap, ikToSimMap = simIK.addElementFromScene(
            ikEnv,
            ikGroup,
            simBase,
            loopTip,
            loopTarget,
            loopConstraint
        )
        simIK.setElementWeights(ikEnv, ikGroup, loopElement, {loopPairs[i][3], 0.0})
        simIK.setElementPrecision(ikEnv, ikGroup, loopElement, {0.0005, math.rad(1)})
    end

    ikElement, simToIkMap, ikToSimMap = simIK.addElementFromScene(
        ikEnv,
        ikGroup,
        simBase,
        simTip,
        simTarget,
        targetConstraint
    )
    simIK.setElementWeights(ikEnv, ikGroup, ikElement, {1.0, 0.0})
    simIK.setElementPrecision(ikEnv, ikGroup, ikElement, {0.001, math.rad(1)})
    tuneJoints(ikToSimMap)
    ikJoints = simIK.getGroupJoints(ikEnv, ikGroup)

    -- Fallback group: if the target position is unreachable, keep the
    -- parallelograms closed instead of letting the dummy pairs drift apart.
    ikGroup_fallback = simIK.createGroup(ikEnv)
    simIK.setGroupCalculation(ikEnv, ikGroup_fallback, method, dampingFactor, maxIterations)
    local fallbackFlags = simIK.getGroupFlags(ikEnv, ikGroup_fallback)
    simIK.setGroupFlags(
        ikEnv,
        ikGroup_fallback,
        fallbackFlags | simIK.group_restoreonbadlintol | simIK.group_restoreonbadangtol
    )
    for i = 1, #loopPairs do
        local loopTip = sim.getObject(loopPairs[i][1])
        local loopTarget = sim.getObject(loopPairs[i][2])
        local loopElement
        loopElement, simToIkMap, ikToSimMap = simIK.addElementFromScene(
            ikEnv,
            ikGroup_fallback,
            simBase,
            loopTip,
            loopTarget,
            loopConstraint
        )
        simIK.setElementWeights(ikEnv, ikGroup_fallback, loopElement, {loopPairs[i][3], 0.0})
        simIK.setElementPrecision(ikEnv, ikGroup_fallback, loopElement, {0.0005, math.rad(1)})
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
    local result, failureReason, precision = simIK.handleGroup(ikEnv, ikGroup, ikOptions)
    if result ~= simIK.result_success then
        simIK.handleGroup(ikEnv, ikGroup_fallback, {syncWorlds = true, allowError = false})
    end
    local posPrecision = precision and precision[1] or -1
    sim.setStringSignal(
        'parallel_ik_result',
        tostring(result) .. ',' .. tostring(failureReason) .. ',' .. tostring(posPrecision)
    )
    return result, failureReason, posPrecision
end

function getEnvironment()
    return ikEnv
end

function getGroup()
    return ikGroup
end

function getFallbackGroup()
    return ikGroup_fallback
end

function getElement()
    return ikElement
end

function getBase()
    return simBase
end

function getTip()
    return simTip
end

function getTarget()
    return simTarget
end

function getIkJoints()
    return ikJoints
end

function setEnabled(b)
    enabled = not not b
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


def set_revolute_interval_deg(client: RemoteAPIClient, joint: int, low: float, high: float) -> None:
    client.call("sim.setJointInterval", [joint, False, [math.radians(low), math.radians(high - low)]])


def configure_joints(client: RemoteAPIClient, sim: dict[str, int], root: int) -> list[str]:
    changed: list[str] = []
    joints = client.call("sim.getObjectsInTree", [root, sim["sceneobject_joint"], 0])
    for joint in joints:
        alias = client.call("sim.getObjectAlias", [joint, 1]).split("/")[-1]
        joint_type = client.call("sim.getJointType", [joint])
        client.call("sim.setJointMode", [joint, sim["jointmode_kinematic"]])
        if joint_type == sim["joint_revolute"]:
            low, high = PRIMARY_REVOLUTE_LIMITS_DEG.get(alias, DEFAULT_REVOLUTE_LIMITS_DEG)
            set_revolute_interval_deg(client, joint, low, high)
            changed.append(f"{alias}:{low:g}..{high:g}deg")
        elif joint_type == sim["joint_prismatic"]:
            changed.append(f"{alias}:prismatic-kept")
        else:
            changed.append(f"{alias}:type-{joint_type}")
    return changed


def ensure_tip_and_target(client: RemoteAPIClient, sim: dict[str, int], root: int) -> tuple[int, int]:
    tip = safe_get(client, TIP_PATH)
    gripper = safe_get(client, GRIPPER_PATH)
    if tip is None:
        if gripper is None:
            raise RuntimeError(f"Missing {TIP_PATH} and {GRIPPER_PATH}")
        tip = client.call("sim.createDummy", [0.035])
        client.call("sim.setObjectAlias", [tip, "tip"])
        client.call("sim.setObjectParent", [tip, gripper, True])
        client.call("sim.setObjectMatrix", [tip, gripper, client.call("sim.getObjectMatrix", [gripper, gripper])])

    target = safe_get(client, TARGET_PATH)
    if target is None:
        target = client.call("sim.createDummy", [0.07])
        client.call("sim.setObjectAlias", [target, "target"])
        client.call("sim.setObjectParent", [target, root, True])

    client.call("sim.setObjectMatrix", [target, -1, client.call("sim.getObjectMatrix", [tip, -1])])
    return tip, target


def configure_dummy_links(client: RemoteAPIClient, sim: dict[str, int]) -> list[str]:
    configured: list[str] = []
    for a_name, b_name, _ in LOOP_PAIRS:
        a = safe_get(client, f"{MODEL_PATH}/{a_name}")
        b = safe_get(client, f"{MODEL_PATH}/{b_name}")
        if a is None or b is None:
            raise RuntimeError(f"Missing dummy pair {a_name}/{b_name}")
        for h in (a, b):
            client.call(
                "sim.setObjectInt32Param",
                [h, sim["dummyintparam_link_type"], sim["dummy_linktype_gcs_loop_closure"]],
            )
        client.call("sim.setLinkDummy", [a, b])
        configured.append(f"{a_name}->{b_name}")
    return configured


def remove_existing_script(client: RemoteAPIClient, sim: dict[str, int]) -> bool:
    script = safe_get(client, SCRIPT_PATH)
    if script is None:
        return False
    client.call("sim.removeObjects", [[script]])
    return True


def loop_pair_rows() -> str:
    rows = []
    for tip, target, weight in LOOP_PAIRS:
        rows.append(f"    {{'{MODEL_PATH}/{tip}', '{MODEL_PATH}/{target}', {weight:.3f}}},")
    return "\n".join(rows)


def attach_script(client: RemoteAPIClient, sim: dict[str, int], root: int) -> int:
    remove_existing_script(client, sim)
    script_text = CONTROL_SCRIPT.replace("LOOP_PAIR_ROWS", loop_pair_rows())
    # The built-in IK Generator uses a customization script, not a simulation
    # script, so sysCall_nonSimulation is active while the scene is stopped.
    script = client.call("sim.createScript", [sim["scripttype_customization"], script_text, 0, "lua"])
    client.call("sim.setObjectAlias", [script, SCRIPT_ALIAS])
    client.call("sim.setObjectParent", [script, root, True])
    client.call("sim.initScript", [script])
    return script


def dist(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def measure_errors(client: RemoteAPIClient) -> tuple[float, list[float]]:
    tip = client.call("sim.getObject", [TIP_PATH])
    target = client.call("sim.getObject", [TARGET_PATH])
    tip_error = dist(
        client.call("sim.getObjectPosition", [tip, -1]),
        client.call("sim.getObjectPosition", [target, -1]),
    )
    loop_errors = []
    for i in range(1, 5):
        a = client.call("sim.getObject", [f"{MODEL_PATH}/dummy{i}A"])
        b = client.call("sim.getObject", [f"{MODEL_PATH}/dummy{i}B"])
        loop_errors.append(
            dist(
                client.call("sim.getObjectPosition", [a, -1]),
                client.call("sim.getObjectPosition", [b, -1]),
            )
        )
    return tip_error, loop_errors


def validate_motion(client: RemoteAPIClient, sim: dict[str, int], script: int) -> tuple[float, list[float], str]:
    target = client.call("sim.getObject", [TARGET_PATH])
    original_target_matrix = client.call("sim.getObjectMatrix", [target, -1])
    original_target_pos = client.call("sim.getObjectPosition", [target, -1])
    test_pos = [
        original_target_pos[0] - 0.005,
        original_target_pos[1],
        original_target_pos[2] + 0.005,
    ]
    client.call("sim.setObjectPosition", [target, -1, test_pos])
    last_result = ""
    time.sleep(0.2)
    for _ in range(40):
        try:
            ret = client.call("sim.callScriptFunction", ["handleIk", script])
            last_result = str(ret)
        except Exception as exc:
            last_result = f"callScriptFunction failed: {exc}"
        time.sleep(0.02)
    tip_error, loop_errors = measure_errors(client)
    client.call("sim.setObjectMatrix", [target, -1, original_target_matrix])
    for _ in range(10):
        try:
            client.call("sim.callScriptFunction", ["handleIk", script])
        except Exception:
            pass
        time.sleep(0.02)
    return tip_error, loop_errors, last_result


def main() -> None:
    client = RemoteAPIClient()
    try:
        sim = constants(client.call("zmqRemoteApi.info", ["sim"]))
        wait_stopped(client, sim)

        scene_path = Path(client.call("sim.getStringParam", [sim["stringparam_scene_path_and_name"]]))
        root = safe_get(client, MODEL_PATH)
        if root is None:
            raise RuntimeError(f"Missing {MODEL_PATH}; load the robot scene first")

        tip, target = ensure_tip_and_target(client, sim, root)
        changed_joints = configure_joints(client, sim, root)
        configured_pairs = configure_dummy_links(client, sim)
        script = attach_script(client, sim, root)
        client.call("sim.setObjectSel", [[target]])
        client.call("sim.announceSceneContentChange")

        suffix = "_example7_parallel_ik"
        out_stem = scene_path.stem if scene_path.stem.endswith(suffix) else f"{scene_path.stem}{suffix}"
        out_scene = scene_path.with_name(f"{out_stem}.ttt")
        client.call("sim.saveScene", [str(out_scene)])

        tip_error, loop_errors, result = validate_motion(client, sim, script)
        client.call("sim.setObjectSel", [[target]])
        client.call("sim.announceSceneContentChange")
        client.call("sim.saveScene", [str(out_scene)])

        print(f"scene_in={scene_path}")
        print(f"scene_out={out_scene}")
        print(f"script={SCRIPT_PATH} handle={script}")
        print(f"tip={tip} target={target}")
        print("dummy_pairs=" + ", ".join(configured_pairs))
        print("joints=" + ", ".join(changed_joints))
        print(f"validation_call={result}")
        print(f"validation_tip_error_m={tip_error:.6f}")
        print("validation_dummy_errors_m=" + ", ".join(f"{e:.6f}" for e in loop_errors))
    finally:
        client.close()


if __name__ == "__main__":
    main()
