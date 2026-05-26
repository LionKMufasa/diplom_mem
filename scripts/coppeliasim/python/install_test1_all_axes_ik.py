from __future__ import annotations

import math
import time
from pathlib import Path

from remote_ik_demo import RemoteAPIClient, constants


MODEL_PATH = "/base_respondable"
TIP_PATH = f"{MODEL_PATH}/tip"
TARGET_PATH = f"{MODEL_PATH}/target"
SCRIPT_ALIAS = "script"
SCRIPT_PATH = f"{MODEL_PATH}/{SCRIPT_ALIAS}"
DEFAULT_SCENE = Path(r"C:\Users\egork\Desktop\coppelia_dpilom\test1.ttt")
OUTPUT_SCENE = Path(r"C:\Users\egork\Desktop\coppelia_dpilom\test1_all_axes_ik.ttt")


IK_SCRIPT = r"""
sim = require 'sim'
simIK = require 'simIK'

local modelPath = '/base_respondable'
local maxTargetStep = 0.01
local maxLoopError = 0.002
local loopPairs = {
    {'/base_respondable/dummy1A', '/base_respondable/dummy1B', simIK.constraint_x + simIK.constraint_z},
    {'/base_respondable/dummy2A', '/base_respondable/dummy2B', simIK.constraint_x + simIK.constraint_z},
    {'/base_respondable/dummy3A', '/base_respondable/dummy3B', simIK.constraint_position},
    {'/base_respondable/dummy4B', '/base_respondable/dummy4A', simIK.constraint_x + simIK.constraint_z},
}

local function ancestorChain(handle)
    local chain = {}
    local current = handle
    while current ~= -1 do
        chain[#chain + 1] = sim.getObjectAlias(current, 1)
        current = sim.getObjectParent(current)
    end
    return chain
end

local function chainContains(chain, text)
    for i = 1, #chain do
        if string.find(chain[i], text, 1, true) then
            return true
        end
    end
    return false
end

local function checkLoopTopology()
    local messages = {}
    for i = 1, #loopPairs do
        local a = sim.getObject(loopPairs[i][1])
        local b = sim.getObject(loopPairs[i][2])
        local pa = sim.getObjectParent(a)
        local pb = sim.getObjectParent(b)
        messages[#messages + 1] =
            'dummy' .. tostring(i) .. ':' ..
            sim.getObjectAlias(pa, 1) .. '<->' .. sim.getObjectAlias(pb, 1)
    end

    local d3a = sim.getObject('/base_respondable/dummy3A')
    local d3b = sim.getObject('/base_respondable/dummy3B')
    local aChain = ancestorChain(d3a)
    local bChain = ancestorChain(d3b)
    local aLow = chainContains(aChain, 'low_arm')
    local bLow = chainContains(bChain, 'low_arm')
    local aHelp = chainContains(aChain, 'help')
    local bHelp = chainContains(bChain, 'help')
    local d3Ok = (aLow and bHelp) or (bLow and aHelp)
    if not d3Ok then
        messages[#messages + 1] = 'WARNING: dummy3 must connect low_arm branch with help branch'
        sim.addLog(
            sim.verbosity_warnings,
            'IK topology warning: dummy3 must connect low_arm branch with help branch. Current: ' ..
            table.concat(messages, '; ')
        )
    end
    sim.setStringSignal('all_axes_ik_topology', table.concat(messages, '; '))
    return d3Ok
end

local function removeExistingProxy()
    local ok, h = pcall(sim.getObject, modelPath .. '/ik_proxy_target')
    if ok and h ~= -1 then
        sim.removeObjects({h})
    end
end

local function moveProxyTowardUserTarget()
    local p = sim.getObjectPosition(proxyTarget, -1)
    local q = sim.getObjectPosition(simTarget, -1)
    local dx = {q[1] - p[1], q[2] - p[2], q[3] - p[3]}
    local length = math.sqrt(dx[1] * dx[1] + dx[2] * dx[2] + dx[3] * dx[3])
    if length > maxTargetStep then
        q = {
            p[1] + dx[1] / length * maxTargetStep,
            p[2] + dx[2] / length * maxTargetStep,
            p[3] + dx[3] / length * maxTargetStep,
        }
    end
    sim.setObjectPosition(proxyTarget, -1, q)
    sim.setObjectOrientation(proxyTarget, -1, sim.getObjectOrientation(simTarget, -1))
    return length
end

local function getJointPositions()
    local cfg = {}
    for i = 1, #simJoints do
        cfg[i] = sim.getJointPosition(simJoints[i])
    end
    return cfg
end

local function setJointPositions(cfg)
    for i = 1, #simJoints do
        sim.setJointPosition(simJoints[i], cfg[i])
    end
end

local function getLoopErrors()
    local errors = {}
    local maxError = 0
    for i = 1, #loopPairs do
        local a = sim.getObject(loopPairs[i][1])
        local b = sim.getObject(loopPairs[i][2])
        local pa = sim.getObjectPosition(a, -1)
        local pb = sim.getObjectPosition(b, -1)
        local dx = pa[1] - pb[1]
        local dy = pa[2] - pb[2]
        local dz = pa[3] - pb[3]
        errors[i] = math.sqrt(dx * dx + dy * dy + dz * dz)
        if errors[i] > maxError then
            maxError = errors[i]
        end
    end
    return errors, maxError
end

function sysCall_init()
    enabled = true
    handleWhenSimulationRunning = true
    handleWhenSimulationStopped = true
    topologyOk = checkLoopTopology()

    simBase = sim.getObject(modelPath)
    simTip = sim.getObject(modelPath .. '/tip')
    simTarget = sim.getObject(modelPath .. '/target')
    simJoints = sim.getObjectsInTree(simBase, sim.sceneobject_joint, 0)

    removeExistingProxy()
    proxyTarget = sim.createDummy(0.04)
    sim.setObjectAlias(proxyTarget, 'ik_proxy_target')
    sim.setObjectParent(proxyTarget, simBase, true)
    sim.setObjectMatrix(proxyTarget, -1, sim.getObjectMatrix(simTip, -1))
    sim.setObjectInt32Param(proxyTarget, sim.objintparam_visibility_layer, 0)

    ikEnv = simIK.createEnvironment()
    ikGroup = simIK.createGroup(ikEnv)
    simIK.setGroupCalculation(ikEnv, ikGroup, simIK.method_damped_least_squares, 0.08, 160)

    -- Main task: gripper target.
    local ikElement
    ikElement, simToIkMap, ikToSimMap = simIK.addElementFromScene(
        ikEnv,
        ikGroup,
        simBase,
        simTip,
        proxyTarget,
        simIK.constraint_position
    )
    simIK.setElementWeights(ikEnv, ikGroup, ikElement, {1.0, 0.0})
    simIK.setElementPrecision(ikEnv, ikGroup, ikElement, {0.001, math.rad(1)})

    -- Parallelogram closures. The scene dummy links stay disabled; dummies are
    -- used only as geometric closure points inside simIK, like example 7.
    for i = 1, #loopPairs do
        local loopElement
        loopElement, simToIkMap, ikToSimMap = simIK.addElementFromScene(
            ikEnv,
            ikGroup,
            simBase,
            sim.getObject(loopPairs[i][1]),
            sim.getObject(loopPairs[i][2]),
            loopPairs[i][3]
        )
        simIK.setElementWeights(ikEnv, ikGroup, loopElement, {1.0, 0.0})
        simIK.setElementPrecision(ikEnv, ikGroup, loopElement, {0.001, math.rad(1)})
    end

    ikJoints = simIK.getGroupJoints(ikEnv, ikGroup)
    for i = 1, #ikJoints do
        local ikJoint = ikJoints[i]
        local simJoint = ikToSimMap[ikJoint]
        simIK.setJointMode(ikEnv, ikJoint, simIK.jointmode_ik)
        simIK.setJointWeight(ikEnv, ikJoint, 1.0)
        if simJoint and sim.getJointType(simJoint) == sim.joint_prismatic then
            simIK.setJointMaxStepSize(ikEnv, ikJoint, 0.02)
        else
            simIK.setJointMaxStepSize(ikEnv, ikJoint, math.rad(8))
        end
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
    if proxyTarget then
        pcall(sim.removeObjects, {proxyTarget})
        proxyTarget = nil
    end
end

function handleIk()
    topologyOk = checkLoopTopology()
    local previousCfg = getJointPositions()
    local previousProxyMatrix = sim.getObjectMatrix(proxyTarget, -1)
    local remainingDistance = moveProxyTowardUserTarget()

    local result, flags, precision = simIK.handleGroup(
        ikEnv,
        ikGroup,
        {syncWorlds = true, allowError = true}
    )

    local loopErrors, maxMeasuredLoopError = getLoopErrors()
    local accepted = topologyOk and maxMeasuredLoopError <= maxLoopError
    if not accepted then
        setJointPositions(previousCfg)
        sim.setObjectMatrix(proxyTarget, -1, previousProxyMatrix)
        loopErrors, maxMeasuredLoopError = getLoopErrors()
    end

    local linearPrecision = precision and precision[1] or -1
    sim.setStringSignal(
        'all_axes_ik_result',
        tostring(result) .. ',' .. tostring(flags) .. ',' .. tostring(linearPrecision) ..
        ',topologyOk=' .. tostring(topologyOk) ..
        ',accepted=' .. tostring(accepted) ..
        ',remaining=' .. tostring(remainingDistance) ..
        ',loops=' .. tostring(loopErrors[1]) .. '/' .. tostring(loopErrors[2]) .. '/' ..
        tostring(loopErrors[3]) .. '/' .. tostring(loopErrors[4])
    )
    return result, flags, linearPrecision, accepted, maxMeasuredLoopError, remainingDistance
end

function setEnabled(value)
    enabled = not not value
end

function getEnabled()
    return enabled
end

function getIkJoints()
    return ikJoints
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


def ensure_kinematic_scene(client: RemoteAPIClient, sim: dict[str, int], root: int) -> tuple[list[str], list[str]]:
    joints_changed: list[str] = []
    for joint in client.call("sim.getObjectsInTree", [root, sim["sceneobject_joint"], 0]):
        client.call("sim.setJointMode", [joint, sim["jointmode_kinematic"]])
        joints_changed.append(client.call("sim.getObjectAlias", [joint, 1]))

    shapes_changed: list[str] = []
    for shape in client.call("sim.getObjectsInTree", [root, sim["sceneobject_shape"], 0]):
        client.call("sim.setObjectInt32Param", [shape, sim["shapeintparam_static"], 1])
        if "shapeintparam_respondable" in sim:
            client.call("sim.setObjectInt32Param", [shape, sim["shapeintparam_respondable"], 0])
        shapes_changed.append(client.call("sim.getObjectAlias", [shape, 1]))
    return joints_changed, shapes_changed


def clear_scene_dummy_links(client: RemoteAPIClient, sim: dict[str, int]) -> list[str]:
    cleared: list[str] = []
    for i in range(1, 5):
        for suffix in ("A", "B"):
            dummy = client.call("sim.getObject", [f"{MODEL_PATH}/dummy{i}{suffix}"])
            try:
                client.call("sim.setLinkDummy", [dummy, -1])
            except Exception:
                pass
            client.call(
                "sim.setObjectInt32Param",
                [dummy, sim["dummyintparam_link_type"], sim["dummytype_default"]],
            )
            cleared.append(f"dummy{i}{suffix}")
    return cleared


def ancestry(client: RemoteAPIClient, handle: int) -> list[str]:
    chain: list[str] = []
    current = handle
    while current != -1:
        chain.append(client.call("sim.getObjectAlias", [current, 1]))
        current = client.call("sim.getObjectParent", [current])
    return chain


def check_dummy3_topology(client: RemoteAPIClient) -> tuple[bool, str]:
    d3a = client.call("sim.getObject", [f"{MODEL_PATH}/dummy3A"])
    d3b = client.call("sim.getObject", [f"{MODEL_PATH}/dummy3B"])
    a_chain = ancestry(client, d3a)
    b_chain = ancestry(client, d3b)
    a_low = any("low_arm" in item for item in a_chain)
    b_low = any("low_arm" in item for item in b_chain)
    a_help = any("help" in item for item in a_chain)
    b_help = any("help" in item for item in b_chain)
    ok = (a_low and b_help) or (b_low and a_help)
    message = f"dummy3A ancestry={a_chain}; dummy3B ancestry={b_chain}"
    return ok, message


def remove_script_if_present(client: RemoteAPIClient, path: str) -> bool:
    script = safe_get(client, path)
    if script is None:
        return False
    client.call("sim.removeObjects", [[script]])
    return True


def install_script(client: RemoteAPIClient, sim: dict[str, int], root: int) -> int:
    for path in (
        SCRIPT_PATH,
        f"{MODEL_PATH}/ik_proxy_target",
        f"{MODEL_PATH}/IK_example7_parallel",
        f"{MODEL_PATH}/IK_all_axes_no_dummy",
        f"{MODEL_PATH}/IK",
    ):
        remove_script_if_present(client, path)
    script = client.call("sim.createScript", [sim["scripttype_customization"], IK_SCRIPT, 0, "lua"])
    client.call("sim.setObjectAlias", [script, SCRIPT_ALIAS])
    client.call("sim.setObjectParent", [script, root, True])
    if "objintparam_visibility_layer" in sim:
        client.call("sim.setObjectInt32Param", [script, sim["objintparam_visibility_layer"], 1])
    client.call("sim.initScript", [script])
    return script


def measure_errors(client: RemoteAPIClient) -> tuple[float, list[float]]:
    tip = client.call("sim.getObject", [TIP_PATH])
    target = client.call("sim.getObject", [TARGET_PATH])
    tip_error = distance(
        client.call("sim.getObjectPosition", [tip, -1]),
        client.call("sim.getObjectPosition", [target, -1]),
    )
    loops: list[float] = []
    for i in range(1, 5):
        a = client.call("sim.getObject", [f"{MODEL_PATH}/dummy{i}A"])
        b = client.call("sim.getObject", [f"{MODEL_PATH}/dummy{i}B"])
        loops.append(
            distance(
                client.call("sim.getObjectPosition", [a, -1]),
                client.call("sim.getObjectPosition", [b, -1]),
            )
        )
    return tip_error, loops


def validate(client: RemoteAPIClient, script: int) -> tuple[tuple[float, list[float]], tuple[float, list[float]], str]:
    target = client.call("sim.getObject", [TARGET_PATH])
    original = client.call("sim.getObjectMatrix", [target, -1])
    pos = client.call("sim.getObjectPosition", [target, -1])
    before = measure_errors(client)
    client.call("sim.setObjectPosition", [target, -1, [pos[0] - 0.01, pos[1], pos[2] + 0.01]])
    result = ""
    for _ in range(80):
        result = str(client.call("sim.callScriptFunction", ["handleIk", script]))
        time.sleep(0.01)
    after = measure_errors(client)
    client.call("sim.setObjectMatrix", [target, -1, original])
    for _ in range(40):
        client.call("sim.callScriptFunction", ["handleIk", script])
        time.sleep(0.01)
    return before, after, result


def main() -> None:
    client = RemoteAPIClient()
    try:
        sim = constants(client.call("zmqRemoteApi.info", ["sim"]))
        wait_stopped(client, sim)

        root = safe_get(client, MODEL_PATH)
        if root is None:
            client.call("sim.loadScene", [str(DEFAULT_SCENE)])
            root = safe_get(client, MODEL_PATH)
        if root is None:
            raise RuntimeError(f"Missing {MODEL_PATH}; open test1 first")
        if safe_get(client, TIP_PATH) is None or safe_get(client, TARGET_PATH) is None:
            raise RuntimeError("Missing tip/target dummies")

        joints, shapes = ensure_kinematic_scene(client, sim, root)
        dummies = clear_scene_dummy_links(client, sim)
        dummy3_ok, dummy3_message = check_dummy3_topology(client)
        script = install_script(client, sim, root)
        before, after, validation = validate(client, script)

        client.call("sim.setObjectSel", [[client.call("sim.getObject", [TARGET_PATH])]])
        client.call("sim.announceSceneContentChange")
        client.call("sim.saveScene", [str(OUTPUT_SCENE)])

        print(f"scene_out={OUTPUT_SCENE}")
        print(f"script={SCRIPT_PATH} handle={script}")
        print(f"joints_kinematic={len(joints)}")
        print(f"shapes_static={len(shapes)}")
        print("dummy_links_cleared=" + ", ".join(dummies))
        print(f"dummy3_topology_ok={dummy3_ok}")
        print(dummy3_message)
        print(f"validation_result={validation}")
        print(f"before_tip_error_m={before[0]:.6f}")
        print("before_loop_errors_m=" + ", ".join(f"{e:.6f}" for e in before[1]))
        print(f"after_test_tip_error_m={after[0]:.6f}")
        print("after_test_loop_errors_m=" + ", ".join(f"{e:.6f}" for e in after[1]))
    finally:
        client.close()


if __name__ == "__main__":
    main()
