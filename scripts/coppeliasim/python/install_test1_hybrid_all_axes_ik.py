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
local maxTargetStep = 0.03
local maxLoopError = 0.002
local targetTolerance = 0.01
local globalSearchTime = 0.9
local globalSearchMaxDist = 6.0
local globalCooldown = 0.6
local globalSearchAttempts = 5
local localIterationsPerCall = 3
local globalRefineIterations = 35

local loopPairs = {
    {'/base_respondable/dummy1A', '/base_respondable/dummy1B', simIK.constraint_x + simIK.constraint_z},
    {'/base_respondable/dummy2A', '/base_respondable/dummy2B', simIK.constraint_x + simIK.constraint_z},
    {'/base_respondable/dummy3A', '/base_respondable/dummy3B', simIK.constraint_position},
    {'/base_respondable/dummy4B', '/base_respondable/dummy4A', simIK.constraint_x + simIK.constraint_z},
}

local function distance(a, b)
    local dx = a[1] - b[1]
    local dy = a[2] - b[2]
    local dz = a[3] - b[3]
    return math.sqrt(dx * dx + dy * dy + dz * dz)
end

local function getNow()
    local ok, t = pcall(sim.getSystemTime)
    if ok then return t end
    return 0
end

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
        if string.find(chain[i], text, 1, true) then return true end
    end
    return false
end

local function checkLoopTopology()
    local messages = {}
    for i = 1, #loopPairs do
        local a = sim.getObject(loopPairs[i][1])
        local b = sim.getObject(loopPairs[i][2])
        messages[#messages + 1] =
            'dummy' .. tostring(i) .. ':' ..
            sim.getObjectAlias(sim.getObjectParent(a), 1) .. '<->' ..
            sim.getObjectAlias(sim.getObjectParent(b), 1)
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
    end
    sim.setStringSignal('all_axes_ik_topology', table.concat(messages, '; '))
    return d3Ok
end

local function removeExistingProxy()
    for _, name in ipairs({'/ik_proxy_target', '/ik_hybrid_proxy_target'}) do
        local ok, h = pcall(sim.getObject, modelPath .. name)
        if ok and h ~= -1 then sim.removeObjects({h}) end
    end
end

local function getSceneJointPositions()
    local cfg = {}
    for i = 1, #simJoints do
        cfg[i] = sim.getJointPosition(simJoints[i])
    end
    return cfg
end

local function setSceneJointPositions(cfg)
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
        errors[i] = distance(sim.getObjectPosition(a, -1), sim.getObjectPosition(b, -1))
        if errors[i] > maxError then maxError = errors[i] end
    end
    return errors, maxError
end

local function getTipTargetError()
    return distance(sim.getObjectPosition(simTip, -1), sim.getObjectPosition(simTarget, -1))
end

local function getProxyTargetDistance()
    return distance(sim.getObjectPosition(proxyTarget, -1), sim.getObjectPosition(simTarget, -1))
end

local function copyUserTargetToProxy()
    sim.setObjectMatrix(proxyTarget, -1, sim.getObjectMatrix(simTarget, -1))
end

local function moveProxyTowardUserTarget()
    local p = sim.getObjectPosition(proxyTarget, -1)
    local q = sim.getObjectPosition(simTarget, -1)
    local len = distance(p, q)
    if len > maxTargetStep then
        q = {
            p[1] + (q[1] - p[1]) / len * maxTargetStep,
            p[2] + (q[2] - p[2]) / len * maxTargetStep,
            p[3] + (q[3] - p[3]) / len * maxTargetStep,
        }
    end
    sim.setObjectPosition(proxyTarget, -1, q)
    sim.setObjectOrientation(proxyTarget, -1, sim.getObjectOrientation(simTarget, -1))
    return len
end

local function configureIkJoints()
    ikJoints = simIK.getGroupJoints(ikEnv, ikGroup)
    cMetric = {}
    for i = 1, #ikJoints do
        local ikJoint = ikJoints[i]
        local simJoint = ikToSimMap[ikJoint]
        simIK.setJointMode(ikEnv, ikJoint, simIK.jointmode_ik)
        simIK.setJointWeight(ikEnv, ikJoint, 1.0)
        cMetric[i] = 1.0
        if simJoint and sim.getJointType(simJoint) == sim.joint_prismatic then
            simIK.setJointMaxStepSize(ikEnv, ikJoint, 0.02)
        else
            simIK.setJointMaxStepSize(ikEnv, ikJoint, math.rad(8))
        end
    end
end

local function buildIk()
    ikEnv = simIK.createEnvironment()
    ikGroup = simIK.createGroup(ikEnv)
    simIK.setGroupCalculation(ikEnv, ikGroup, simIK.method_damped_least_squares, 0.08, 160)

    local element
    element, simToIkMap, ikToSimMap = simIK.addElementFromScene(
        ikEnv,
        ikGroup,
        simBase,
        simTip,
        proxyTarget,
        simIK.constraint_position
    )
    simIK.setElementWeights(ikEnv, ikGroup, element, {1.0, 0.0})
    simIK.setElementPrecision(ikEnv, ikGroup, element, {0.001, math.rad(1)})

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

    configureIkJoints()
end

local function applyIkConfig(cfg)
    for i = 1, #ikJoints do
        simIK.setJointPosition(ikEnv, ikJoints[i], cfg[i])
    end
    simIK.syncToSim(ikEnv, {ikGroup})
end

local function refineLocal(iterations)
    local result, flags, precision
    for i = 1, iterations do
        result, flags, precision = simIK.handleGroup(
            ikEnv,
            ikGroup,
            {syncWorlds = true, allowError = true}
        )
    end
    return result, flags, precision
end

local function publishStatus(mode, accepted, result, flags, precision, found)
    local loopErrors, maxMeasuredLoopError = getLoopErrors()
    local tipError = getTipTargetError()
    local proxyRemaining = getProxyTargetDistance()
    local linearPrecision = precision and precision[1] or -1
    local text =
        'mode=' .. tostring(mode) ..
        ',accepted=' .. tostring(accepted) ..
        ',result=' .. tostring(result) ..
        ',flags=' .. tostring(flags) ..
        ',precision=' .. tostring(linearPrecision) ..
        ',found=' .. tostring(found or 0) ..
        ',tipError=' .. tostring(tipError) ..
        ',proxyRemaining=' .. tostring(proxyRemaining) ..
        ',maxLoop=' .. tostring(maxMeasuredLoopError) ..
        ',loops=' .. tostring(loopErrors[1]) .. '/' .. tostring(loopErrors[2]) .. '/' ..
        tostring(loopErrors[3]) .. '/' .. tostring(loopErrors[4])
    sim.setStringSignal('all_axes_ik_result', text)
    return result, flags, linearPrecision, accepted, maxMeasuredLoopError, tipError, proxyRemaining
end

local function tryGlobalSearch(reason, searchTime, attempts)
    local previousCfg = getSceneJointPositions()
    local previousProxyMatrix = sim.getObjectMatrix(proxyTarget, -1)
    local totalFound = 0
    attempts = attempts or globalSearchAttempts

    for attempt = 1, attempts do
        setSceneJointPositions(previousCfg)
        sim.setObjectMatrix(proxyTarget, -1, previousProxyMatrix)
        copyUserTargetToProxy()
        simIK.syncFromSim(ikEnv, {ikGroup})

        local params = {
            maxDist = globalSearchMaxDist,
            maxTime = searchTime or globalSearchTime,
            pMetric = {1.0, 1.0, 1.0, 0.05},
            cMetric = cMetric,
            findMultiple = false,
        }
        local configs = simIK.findConfigs(ikEnv, ikGroup, ikJoints, params)
        local found = configs and #configs or 0
        totalFound = totalFound + found
        if found > 0 then
            applyIkConfig(configs[1])
            local result, flags, precision = refineLocal(globalRefineIterations)
            local _, maxMeasuredLoopError = getLoopErrors()
            local tipError = getTipTargetError()
            local accepted = maxMeasuredLoopError <= maxLoopError and tipError <= targetTolerance
            if accepted then
                lastAcceptedCfg = getSceneJointPositions()
                lastAcceptedProxyMatrix = sim.getObjectMatrix(proxyTarget, -1)
                lastGlobalTime = getNow()
                return publishStatus('global_' .. reason, true, result, flags, precision, totalFound)
            end
        end
    end

    setSceneJointPositions(previousCfg)
    sim.setObjectMatrix(proxyTarget, -1, previousProxyMatrix)
    simIK.syncFromSim(ikEnv, {ikGroup})
    lastGlobalTime = getNow()
    return publishStatus('global_failed_' .. reason, false, 0, 0, nil, totalFound)
end

function sysCall_init()
    enabled = true
    autoGlobalSearch = true
    handleWhenSimulationRunning = true
    handleWhenSimulationStopped = true
    lastGlobalTime = -1000

    simBase = sim.getObject(modelPath)
    simTip = sim.getObject(modelPath .. '/tip')
    simTarget = sim.getObject(modelPath .. '/target')
    simJoints = sim.getObjectsInTree(simBase, sim.sceneobject_joint, 0)

    removeExistingProxy()
    proxyTarget = sim.createDummy(0.04)
    sim.setObjectAlias(proxyTarget, 'ik_hybrid_proxy_target')
    sim.setObjectParent(proxyTarget, simBase, true)
    sim.setObjectMatrix(proxyTarget, -1, sim.getObjectMatrix(simTip, -1))
    sim.setObjectInt32Param(proxyTarget, sim.objintparam_visibility_layer, 0)

    topologyOk = checkLoopTopology()
    buildIk()
    lastAcceptedCfg = getSceneJointPositions()
    lastAcceptedProxyMatrix = sim.getObjectMatrix(proxyTarget, -1)
end

function sysCall_actuation()
    if enabled and handleWhenSimulationRunning then handleIk(false) end
end

function sysCall_nonSimulation()
    if enabled and handleWhenSimulationStopped then handleIk(false) end
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

function handleIk(forceGlobal)
    if not enabled then
        return publishStatus('disabled', false, 0, 0, nil, 0)
    end

    topologyOk = checkLoopTopology()
    if not topologyOk then
        return publishStatus('bad_topology', false, 0, 0, nil, 0)
    end

    if forceGlobal then
        return tryGlobalSearch('forced', globalSearchTime)
    end

    local previousCfg = getSceneJointPositions()
    local previousProxyMatrix = sim.getObjectMatrix(proxyTarget, -1)
    local remainingBefore = moveProxyTowardUserTarget()
    local result, flags, precision = refineLocal(localIterationsPerCall)
    local _, maxMeasuredLoopError = getLoopErrors()

    if maxMeasuredLoopError <= maxLoopError then
        lastAcceptedCfg = getSceneJointPositions()
        lastAcceptedProxyMatrix = sim.getObjectMatrix(proxyTarget, -1)
        return publishStatus('local', true, result, flags, precision, 0)
    end

    setSceneJointPositions(previousCfg)
    sim.setObjectMatrix(proxyTarget, -1, previousProxyMatrix)
    simIK.syncFromSim(ikEnv, {ikGroup})

    local now = getNow()
    if autoGlobalSearch and remainingBefore > maxTargetStep and (now - lastGlobalTime) >= globalCooldown then
        return tryGlobalSearch('auto', globalSearchTime, globalSearchAttempts)
    end

    return publishStatus('blocked', false, result, flags, precision, 0)
end

function seedGlobal()
    return tryGlobalSearch('manual', 1.2, 10)
end

function setEnabled(value)
    enabled = not not value
end

function getEnabled()
    return enabled
end

function setAutoGlobalSearch(value)
    autoGlobalSearch = not not value
end

function getIkJoints()
    return ikJoints
end
"""


def wait_stopped(client: RemoteAPIClient, sim: dict[str, int]) -> None:
    for _ in range(120):
        if client.call("sim.getSimulationState") == sim["simulation_stopped"]:
            return
        client.call("sim.stopSimulation")
        time.sleep(0.05)
    raise RuntimeError("Simulation did not stop")


def safe_get(client: RemoteAPIClient, path: str) -> int | None:
    try:
        return client.call("sim.getObject", [path])
    except Exception:
        return None


def remove_if_present(client: RemoteAPIClient, path: str) -> bool:
    handle = safe_get(client, path)
    if handle is None:
        return False
    client.call("sim.removeObjects", [[handle]])
    return True


def clear_scene_dummy_links(client: RemoteAPIClient, sim: dict[str, int]) -> list[str]:
    cleared = []
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


def joint_intervals(client: RemoteAPIClient, sim: dict[str, int], root: int) -> dict[str, tuple[bool, list[float]]]:
    out = {}
    for joint in client.call("sim.getObjectsInTree", [root, sim["sceneobject_joint"], 0]):
        name = client.call("sim.getObjectAlias", [joint, 1])
        cyclic, interval = client.call("sim.getJointInterval", [joint])
        out[name] = (cyclic, interval)
    return out


def intervals_equal(a: dict[str, tuple[bool, list[float]]], b: dict[str, tuple[bool, list[float]]]) -> bool:
    if set(a) != set(b):
        return False
    for key in a:
        if a[key][0] != b[key][0]:
            return False
        if any(abs(x - y) > 1e-12 for x, y in zip(a[key][1], b[key][1])):
            return False
    return True


def install_script(client: RemoteAPIClient, sim: dict[str, int], root: int) -> int:
    for path in (
        SCRIPT_PATH,
        f"{MODEL_PATH}/ik_proxy_target",
        f"{MODEL_PATH}/ik_hybrid_proxy_target",
        f"{MODEL_PATH}/IK_example7_parallel",
        f"{MODEL_PATH}/IK_all_axes_no_dummy",
        f"{MODEL_PATH}/IK",
    ):
        remove_if_present(client, path)
    script = client.call("sim.createScript", [sim["scripttype_customization"], IK_SCRIPT, 0, "lua"])
    client.call("sim.setObjectAlias", [script, SCRIPT_ALIAS])
    client.call("sim.setObjectParent", [script, root, True])
    client.call("sim.initScript", [script])
    return script


def main() -> None:
    client = RemoteAPIClient()
    client.socket.RCVTIMEO = 120000
    try:
        client.call("zmqRemoteApi.require", ["sim"])
        sim = constants(client.call("zmqRemoteApi.info", ["sim"]))
        wait_stopped(client, sim)

        client.call("sim.loadScene", [str(DEFAULT_SCENE)])
        root = safe_get(client, MODEL_PATH)
        if root is None:
            raise RuntimeError(f"Missing {MODEL_PATH} in {DEFAULT_SCENE}")
        if safe_get(client, TIP_PATH) is None or safe_get(client, TARGET_PATH) is None:
            raise RuntimeError("Missing tip/target dummies")

        before_intervals = joint_intervals(client, sim, root)
        cleared = clear_scene_dummy_links(client, sim)
        script = install_script(client, sim, root)
        after_intervals = joint_intervals(client, sim, root)
        unchanged = intervals_equal(before_intervals, after_intervals)

        client.call("sim.setObjectSel", [[client.call("sim.getObject", [TARGET_PATH])]])
        client.call("sim.announceSceneContentChange")
        client.call("sim.saveScene", [str(OUTPUT_SCENE)])

        print(f"scene_out={OUTPUT_SCENE}")
        print(f"script={SCRIPT_PATH} handle={script}")
        print("dummy_links_cleared=" + ", ".join(cleared))
        print(f"joint_intervals_unchanged={unchanged}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
