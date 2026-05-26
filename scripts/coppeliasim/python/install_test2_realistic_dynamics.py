from __future__ import annotations

import json
import math
import time
from pathlib import Path

from remote_ik_demo import RemoteAPIClient, constants


MODEL_PATH = "/base_respondable"
SCRIPT_ALIAS = "realistic_dynamics_script"
SCRIPT_PATH = f"{MODEL_PATH}/{SCRIPT_ALIAS}"
OLD_SCRIPT_PATH = f"{MODEL_PATH}/torque_graph_script"
PICK_PLACE_SCRIPT_ALIAS = "pick_place_script"
PICK_PLACE_SCRIPT_PATH = f"{MODEL_PATH}/{PICK_PLACE_SCRIPT_ALIAS}"
PAYLOAD_ALIAS = "payload_box"
PAYLOAD_PATH = f"{MODEL_PATH}/{PAYLOAD_ALIAS}"
FALLBACK_PAYLOAD_PATH = "/Cuboid"

TARGET_ROBOT_MASS_KG = 1650.0
PAYLOAD_MASS_KG = 120.0
PAYLOAD_SIZE_M = [0.55, 0.40, 0.28]
PAYLOAD_OFFSET_M = [0.18, 0.0, 0.0]

AXIS16_STIFFNESS = 42000.0
AXIS16_DAMPING = 5500.0
AXIS16_FORCE_LIMIT = 18000.0
AXIS16_MAX_VEL = 0.35

DEFAULT_FORCE_CAPS = {
    "motor1": 15000.0,
    "motor2": 18000.0,
    "motor3": 18000.0,
    "motor4": 3000.0,
}

JOINT_DYNAMICS = {
    "motor1": {"max_vel": 1.2, "max_accel": 2.5, "max_jerk": 10.0},
    "motor2": {"max_vel": 1.0, "max_accel": 2.2, "max_jerk": 9.0},
    "motor3": {"max_vel": 1.0, "max_accel": 2.2, "max_jerk": 9.0},
    "motor4": {"max_vel": 2.0, "max_accel": 5.0, "max_jerk": 20.0},
    "axis16": {"max_vel": 0.35, "max_accel": 1.0, "max_jerk": 4.0},
}

OUTPUT_SCENE = Path(r"C:\Users\egork\Desktop\coppelia_dpilom\test2_realistic_dynamics.ttt")
REPORT_PATH = Path("test2_realistic_dynamics_report.json")


REALISTIC_SCRIPT = r"""
sim = require 'sim'

local modelPath = '/base_respondable'
local csvPath = 'C:/Users/egork/Desktop/coppelia_dpilom/test2_dynamics_monitor.csv'
local timeWindow = 20.0

local palette = {
    {230, 57, 70},
    {29, 53, 87},
    {69, 123, 157},
    {42, 157, 143},
    {233, 196, 106},
    {244, 162, 97},
    {131, 56, 236},
    {255, 0, 110},
}

local jointDefs = {
    {path = modelPath .. '/motor1', name = 'motor1', unitForce = 'N*m', kind = 'rev'},
    {path = modelPath .. '/motor2', name = 'motor2', unitForce = 'N*m', kind = 'rev'},
    {path = modelPath .. '/motor3', name = 'motor3', unitForce = 'N*m', kind = 'rev'},
    {path = modelPath .. '/axis16', name = 'axis16', unitForce = 'N', kind = 'lin'},
}

local function csvEscape(text)
    text = tostring(text)
    if string.find(text, '[,"]') then
        text = '"' .. string.gsub(text, '"', '""') .. '"'
    end
    return text
end

local function readJointForce(handle)
    local ok, value = pcall(sim.getJointForce, handle)
    if ok and value then return value end
    return 0.0
end

local function readJointVelocity(handle)
    local ok, value = pcall(sim.getObjectFloatParam, handle, sim.jointfloatparam_velocity)
    if ok and value then return value end
    return 0.0
end

local function toDisplay(kind, quantity, value)
    if quantity == 'force' then
        return value
    end
    if kind == 'lin' then
        return value
    end
    return math.deg(value)
end

local function destroyUi()
    if ui then
        pcall(simUI.destroy, ui)
        ui = nil
    end
end

local function createUi()
    local ok, module = pcall(require, 'simUI')
    if not ok then
        simUI = nil
        sim.addLog(sim.verbosity_warnings, 'Dynamics monitor: simUI plugin not available, CSV logging only.')
        return
    end
    simUI = module
    destroyUi()
    local xml = [[
        <ui title="Robot dynamics monitor" closeable="true" resizable="true" placement="relative" position="20,20" size="1020,880">
            <group layout="vbox" flat="true" margins="4,4,4,4" spacing="4">
                <plot id="1"/>
                <plot id="2"/>
                <plot id="3"/>
                <plot id="4"/>
            </group>
        </ui>
    ]]
    ui = simUI.create(xml)
    simUI.setPlotLabels(ui, 1, 'simulation time [s]', 'joint torque [N*m] / force [N]')
    simUI.setPlotLabels(ui, 2, 'simulation time [s]', 'joint position [deg] / axis16 [m]')
    simUI.setPlotLabels(ui, 3, 'simulation time [s]', 'joint velocity [deg/s] / axis16 [m/s]')
    simUI.setPlotLabels(ui, 4, 'simulation time [s]', 'joint acceleration [deg/s^2] / axis16 [m/s^2]')
    simUI.setLegendVisibility(ui, 1, true)
    simUI.setLegendVisibility(ui, 2, true)
    simUI.setLegendVisibility(ui, 3, true)
    simUI.setLegendVisibility(ui, 4, true)
    simUI.setPlotRanges(ui, 1, 0, timeWindow, -100, 100)
    simUI.setPlotRanges(ui, 2, 0, timeWindow, -100, 100)
    simUI.setPlotRanges(ui, 3, 0, timeWindow, -100, 100)
    simUI.setPlotRanges(ui, 4, 0, timeWindow, -100, 100)

    for i = 1, #jointDefs do
        local color = palette[((i - 1) % #palette) + 1]
        for plotId = 1, 4 do
            simUI.addCurve(
                ui,
                plotId,
                simUI.curve_type.time,
                jointDefs[i].name,
                color,
                simUI.curve_style.line,
                {}
            )
        end
    end
end

local function closeCsv()
    if csvFile then
        csvFile:flush()
        csvFile:close()
        csvFile = nil
    end
end

local function openCsv()
    closeCsv()
    local ok, file = pcall(io.open, csvPath, 'w')
    if not ok or not file then
        sim.addLog(sim.verbosity_warnings, 'Dynamics monitor: failed to open CSV ' .. csvPath)
        return
    end
    csvFile = file
    local header = {
        'time_s',
        'gripper_x_m', 'gripper_y_m', 'gripper_z_m',
        'payload_x_m', 'payload_y_m', 'payload_z_m',
    }
    for i = 1, #jointDefs do
        local def = jointDefs[i]
        local suffix = def.kind == 'lin' and 'm' or 'deg'
        header[#header + 1] = def.name .. '_force_' .. def.unitForce
        header[#header + 1] = def.name .. '_pos_' .. suffix
        header[#header + 1] = def.name .. '_vel_' .. suffix .. '_s'
        header[#header + 1] = def.name .. '_acc_' .. suffix .. '_s2'
    end
    for i = 1, #header do header[i] = csvEscape(header[i]) end
    csvFile:write(table.concat(header, ',') .. '\n')
    csvFile:flush()
    sim.addLog(sim.verbosity_scriptinfos, 'Dynamics monitor CSV: ' .. csvPath)
end

local function resetCurves()
    if not (simUI and ui) then return end
    for plotId = 1, 4 do
        for i = 1, #jointDefs do
            pcall(simUI.clearCurve, ui, plotId, jointDefs[i].name)
        end
        pcall(simUI.setPlotRanges, ui, plotId, 0, timeWindow, -100, 100)
        pcall(simUI.replot, ui, plotId)
    end
    lastRescaleTime = -1.0
end

local function clampTarget(def, value)
    local meta = limits[def.name]
    if not meta or meta.cyclic then return value end
    if value < meta.min then return meta.min end
    if value > meta.max then return meta.max end
    return value
end

local function readWorldPosition(handle)
    if not handle or handle == -1 then
        return {0.0, 0.0, 0.0}
    end
    local ok, pos = pcall(sim.getObjectPosition, handle, sim.handle_world)
    if ok and pos then return pos end
    return {0.0, 0.0, 0.0}
end

local function collectJoints()
    limits = {}
    jointsByName = {}
    for i = 1, #jointDefs do
        local def = jointDefs[i]
        local ok, handle = pcall(sim.getObject, def.path)
        if ok and handle ~= -1 then
            def.handle = handle
            jointsByName[def.name] = def
            local cyclic, interval = sim.getJointInterval(def.handle)
            limits[def.name] = {
                cyclic = cyclic,
                min = interval[1],
                max = interval[2],
            }
        else
            def.handle = -1
        end
    end
    gripper = sim.getObject(modelPath .. '/gripper_respondable')
    local ok, payloadHandle = pcall(sim.getObject, modelPath .. '/payload_box')
    if ok and payloadHandle ~= -1 then
        payload = payloadHandle
    else
        local ok2, payloadHandle2 = pcall(sim.getObject, '/Cuboid')
        payload = (ok2 and payloadHandle2) and payloadHandle2 or -1
    end
end

local function captureCenters()
    centers = {}
    for i = 1, #jointDefs do
        local def = jointDefs[i]
        if def.handle ~= -1 then
            centers[def.name] = sim.getJointPosition(def.handle)
        end
    end
end

local function buildMetrics(dt)
    local values = {}
    for i = 1, #jointDefs do
        local def = jointDefs[i]
        if def.handle ~= -1 then
            local pos = sim.getJointPosition(def.handle)
            local vel = readJointVelocity(def.handle)
            local acc = 0.0
            if prevVel[def.name] ~= nil and dt > 0.0 then
                acc = (vel - prevVel[def.name]) / dt
            end
            prevVel[def.name] = vel
            values[def.name] = {
                force = readJointForce(def.handle),
                pos = pos,
                vel = vel,
                acc = acc,
            }
        else
            values[def.name] = {force = 0.0, pos = 0.0, vel = 0.0, acc = 0.0}
        end
    end
    return values
end

local function writeCsvLine(t, metrics)
    if not csvFile then return end
    local g = readWorldPosition(gripper)
    local p = readWorldPosition(payload)
    local row = {
        string.format('%.6f', t),
        string.format('%.8g', g[1]), string.format('%.8g', g[2]), string.format('%.8g', g[3]),
        string.format('%.8g', p[1]), string.format('%.8g', p[2]), string.format('%.8g', p[3]),
    }
    for i = 1, #jointDefs do
        local def = jointDefs[i]
        local m = metrics[def.name]
        row[#row + 1] = string.format('%.8g', m.force)
        row[#row + 1] = string.format('%.8g', toDisplay(def.kind, 'pos', m.pos))
        row[#row + 1] = string.format('%.8g', toDisplay(def.kind, 'vel', m.vel))
        row[#row + 1] = string.format('%.8g', toDisplay(def.kind, 'acc', m.acc))
    end
    csvFile:write(table.concat(row, ',') .. '\n')
    csvFile:flush()
end

local function updateUi(t, metrics)
    if not (simUI and ui) then return end
    for i = 1, #jointDefs do
        local def = jointDefs[i]
        local m = metrics[def.name]
        simUI.addCurveTimePoints(ui, 1, def.name, {t}, {m.force})
        simUI.addCurveTimePoints(ui, 2, def.name, {t}, {toDisplay(def.kind, 'pos', m.pos)})
        simUI.addCurveTimePoints(ui, 3, def.name, {t}, {toDisplay(def.kind, 'vel', m.vel)})
        simUI.addCurveTimePoints(ui, 4, def.name, {t}, {toDisplay(def.kind, 'acc', m.acc)})
    end
    local xMin = math.max(0.0, t - timeWindow)
    local xMax = math.max(timeWindow, t + 0.05)
    for plotId = 1, 4 do
        pcall(simUI.setPlotXRange, ui, plotId, xMin, xMax)
        if t - lastRescaleTime > 0.5 then
            pcall(simUI.rescaleAxesAll, ui, plotId, true, true)
            pcall(simUI.replot, ui, plotId)
        end
    end
    if t - lastRescaleTime > 0.5 then
        lastRescaleTime = t
    end
end

function sysCall_init()
    prevVel = {}
    lastRescaleTime = -1.0
    collectJoints()
    createUi()
    sim.addLog(sim.verbosity_scriptinfos, 'Dynamics monitor ready.')
end

function sysCall_beforeSimulation()
    prevVel = {}
    createUi()
    captureCenters()
    resetCurves()
    openCsv()
    sim.addLog(sim.verbosity_scriptinfos, 'Dynamics monitor ready for pick and place cycle.')
end

function sysCall_sensing()
    if sim.getSimulationState() == sim.simulation_stopped then return end
    local dt = sim.getSimulationTimeStep()
    local t = sim.getSimulationTime()
    local metrics = buildMetrics(dt)
    writeCsvLine(t, metrics)
    updateUi(t, metrics)

    sim.setStringSignal(
        'robot_dynamics_monitor',
        string.format(
            't=%.3f,m1=%.3f,m2=%.3f,m3=%.3f,axis16=%.3f',
            t,
            metrics.motor1.force,
            metrics.motor2.force,
            metrics.motor3.force,
            metrics.axis16.force
        )
    )
end

function sysCall_afterSimulation()
    closeCsv()
end

function sysCall_cleanup()
    closeCsv()
    destroyUi()
end
"""


PICK_PLACE_SCRIPT = r"""
sim = require 'sim'

local modelPath = '/base_respondable'
local payloadPathCandidates = {'/Cuboid', modelPath .. '/payload_box'}

local maxVel = {1.2, 1.0, 1.0}
local maxAccel = {2.5, 2.2, 2.2}
local maxJerk = {10.0, 9.0, 9.0}

local function rad(v)
    return math.rad(v)
end

local function pose(a1, a2, a3)
    return {rad(a1), rad(a2), rad(a3)}
end

local function findPayload()
    for i = 1, #payloadPathCandidates do
        local ok, h = pcall(sim.getObject, payloadPathCandidates[i])
        if ok and h ~= -1 then
            return h
        end
    end
    return -1
end

local function restoreAttachDummy()
    sim.setLinkDummy(attachDummyA, -1)
    sim.setObjectParent(attachDummyA, gripper, true)
    local m = sim.getObjectMatrix(attachDummyB)
    sim.setObjectMatrix(attachDummyA, m)
end

local function attachPayload()
    if payload == -1 then
        return
    end
    attached = true
end

local function releasePayload()
    if payload ~= -1 then
        zeroPayloadDynamics()
    end
    restoreAttachDummy()
    attached = false
end

local function zeroPayloadDynamics()
    if payload == -1 then
        return
    end
    sim.resetDynamicObject(payload)
end

local function placePayloadAtPick()
    if payload == -1 then
        return
    end
    sim.setLinkDummy(attachDummyA, -1)
    sim.setObjectParent(attachDummyA, gripper, true)
    sim.setObjectParent(payload, -1, true)
    sim.setObjectPosition(payload, sim.handle_world, pickWorld)
    sim.setObjectOrientation(payload, sim.handle_world, {0, 0, 0})
    zeroPayloadDynamics()
    attached = false
end

local function moveToConfig(target, sync)
    local params = {
        joints = motors,
        targetPos = target,
        maxVel = maxVel,
        maxAccel = maxAccel,
        maxJerk = maxJerk,
        flags = sync and -1 or sim.ruckig_nosync,
    }
    sim.moveToConfig(params)
end

function sysCall_init()
    motors = {
        sim.getObject(modelPath .. '/motor1'),
        sim.getObject(modelPath .. '/motor2'),
        sim.getObject(modelPath .. '/motor3'),
    }
    gripper = sim.getObject(modelPath .. '/gripper_respondable')
    payload = findPayload()

    local okA, hA = pcall(sim.getObject, modelPath .. '/pickAttachDummyA')
    if okA and hA ~= -1 then
        attachDummyA = hA
    else
        attachDummyA = sim.createDummy(0.02)
        sim.setObjectAlias(attachDummyA, 'pickAttachDummyA')
        sim.setObjectParent(attachDummyA, gripper, true)
    end

    local okB, hB = pcall(sim.getObject, modelPath .. '/pickAttachDummyB')
    if okB and hB ~= -1 then
        attachDummyB = hB
    else
        attachDummyB = sim.createDummy(0.02)
        sim.setObjectAlias(attachDummyB, 'pickAttachDummyB')
        sim.setObjectParent(attachDummyB, gripper, true)
    end

    sim.setObjectInt32Param(attachDummyA, sim.objintparam_visibility_layer, 0)
    sim.setObjectInt32Param(attachDummyB, sim.objintparam_visibility_layer, 0)
    sim.setObjectPosition(attachDummyB, sim.handle_parent, {0.0, 0.0, -0.17})
    sim.setObjectOrientation(attachDummyB, sim.handle_parent, {0.0, 0.0, 0.0})

    restoreAttachDummy()

    home = pose(0, 12, 0)
    pickAbove = pose(0, 28, 0)
    pickDown = pose(0, 40, 0)
    placeAbove = pose(-22, 28, 0)
    placeDown = pose(-22, 40, 0)

    pickWorld = {0.995, 0.028, 0.05}
    placeWorld = {0.898, 0.529, 0.05}
end

function sysCall_thread()
    while true do
        payload = findPayload()
        if payload ~= -1 then
            placePayloadAtPick()
        end

        moveToConfig(home, true)
        moveToConfig(pickAbove, true)
        moveToConfig(pickDown, true)
        attachPayload()
        sim.wait(0.3)
        moveToConfig(pickAbove, true)
        moveToConfig(placeAbove, true)
        moveToConfig(placeDown, true)

        if payload ~= -1 then
            sim.setObjectParent(payload, -1, true)
            zeroPayloadDynamics()
        end
        releasePayload()
        sim.wait(0.3)

        moveToConfig(placeAbove, true)
        moveToConfig(home, true)
        sim.wait(0.6)
    end
end

function sysCall_actuation()
    if attached and payload ~= -1 then
        local m = sim.getObjectMatrix(attachDummyB)
        sim.setObjectMatrix(payload, sim.handle_world, m)
    end
end

function sysCall_cleanup()
    if attachDummyA and attachDummyB then
        restoreAttachDummy()
    end
end
"""


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
    for _ in range(200):
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


def remove_if_exists(client: RemoteAPIClient, path: str) -> None:
    handle = safe_get(client, path)
    if handle is None:
        return
    client.call("sim.removeObjects", [[handle]])


def short(alias: str) -> str:
    return alias.rsplit("/", 1)[-1]


def list_physical_robot_shapes(client: RemoteAPIClient, sim: dict[str, int], root: int) -> list[dict[str, object]]:
    shapes = client.call("sim.getObjectsInTree", [root, sim["sceneobject_shape"], 0])
    rows: list[dict[str, object]] = []
    for shape in shapes:
        alias = client.call("sim.getObjectAlias", [shape, 1])
        name = short(alias)
        if name.endswith("_visual") or name == PAYLOAD_ALIAS:
            continue
        mass = float(client.call("sim.getShapeMass", [shape]))
        inertia, com = client.call("sim.getShapeInertia", [shape])
        rows.append(
            {
                "handle": shape,
                "alias": alias,
                "name": name,
                "mass_before_kg": mass,
                "inertia_before": [float(v) for v in inertia],
                "com_matrix": com,
            }
        )
    return rows


def scale_robot_mass_distribution(
    client: RemoteAPIClient, sim: dict[str, int], root: int
) -> tuple[list[dict[str, object]], float, float]:
    rows = list_physical_robot_shapes(client, sim, root)
    before_total = sum(float(row["mass_before_kg"]) for row in rows)
    if before_total <= 0:
        raise RuntimeError("No physical robot shapes found for mass scaling")

    scale = TARGET_ROBOT_MASS_KG / before_total
    for row in rows:
        shape = int(row["handle"])
        new_mass = float(row["mass_before_kg"]) * scale
        new_inertia = [value * scale for value in row["inertia_before"]]
        client.call("sim.setShapeMass", [shape, new_mass])
        client.call("sim.setShapeInertia", [shape, new_inertia, row["com_matrix"]])
        row["mass_after_kg"] = float(client.call("sim.getShapeMass", [shape]))
        inertia_after, _ = client.call("sim.getShapeInertia", [shape])
        row["inertia_after"] = [float(v) for v in inertia_after]

    after_total = sum(float(row["mass_after_kg"]) for row in rows)
    return rows, before_total, after_total


def resolve_or_create_payload(
    client: RemoteAPIClient, sim: dict[str, int], gripper: int
) -> dict[str, object]:
    payload = safe_get(client, FALLBACK_PAYLOAD_PATH)
    source = FALLBACK_PAYLOAD_PATH
    if payload is None:
        payload = safe_get(client, PAYLOAD_PATH)
        source = PAYLOAD_PATH
    if payload is None:
        payload = client.call("sim.createPureShape", [0, 0, PAYLOAD_SIZE_M, 0.001])
        client.call("sim.setObjectAlias", [payload, PAYLOAD_ALIAS])
        client.call("sim.setObjectParent", [payload, -1, True])
        client.call("sim.setObjectPosition", [payload, sim["handle_world"], [0.995, 0.028, PAYLOAD_SIZE_M[2] * 0.5]])
        client.call("sim.setObjectOrientation", [payload, sim["handle_world"], [0.0, 0.0, 0.0]])
        client.call("sim.setShapeColor", [payload, None, sim["colorcomponent_ambient_diffuse"], [0.93, 0.48, 0.20]])
        source = PAYLOAD_PATH

    client.call("sim.setObjectInt32Param", [payload, sim["shapeintparam_static"], 0])
    client.call("sim.setObjectInt32Param", [payload, sim["shapeintparam_respondable"], 1])
    client.call("sim.setObjectParent", [payload, -1, True])

    bbox = [
        float(client.call("sim.getObjectFloatParam", [payload, sim["objfloatparam_objbbox_min_x"]])),
        float(client.call("sim.getObjectFloatParam", [payload, sim["objfloatparam_objbbox_max_x"]])),
        float(client.call("sim.getObjectFloatParam", [payload, sim["objfloatparam_objbbox_min_y"]])),
        float(client.call("sim.getObjectFloatParam", [payload, sim["objfloatparam_objbbox_max_y"]])),
        float(client.call("sim.getObjectFloatParam", [payload, sim["objfloatparam_objbbox_min_z"]])),
        float(client.call("sim.getObjectFloatParam", [payload, sim["objfloatparam_objbbox_max_z"]])),
    ]
    size = [bbox[1] - bbox[0], bbox[3] - bbox[2], bbox[5] - bbox[4]]
    volume = max(size[0] * size[1] * size[2], 1e-6)
    density = PAYLOAD_MASS_KG / volume
    result = int(client.call("sim.computeMassAndInertia", [payload, density]))
    if result == 0:
        inertia, com = client.call("sim.getShapeInertia", [payload])
        sx, sy, sz = size
        ixx = PAYLOAD_MASS_KG * (sy * sy + sz * sz) / 12.0
        iyy = PAYLOAD_MASS_KG * (sx * sx + sz * sz) / 12.0
        izz = PAYLOAD_MASS_KG * (sx * sx + sy * sy) / 12.0
        client.call("sim.setShapeMass", [payload, PAYLOAD_MASS_KG])
        client.call("sim.setShapeInertia", [payload, [ixx, 0.0, 0.0, 0.0, iyy, 0.0, 0.0, 0.0, izz], com])
    mass = float(client.call("sim.getShapeMass", [payload]))
    inertia, _ = client.call("sim.getShapeInertia", [payload])
    return {
        "handle": payload,
        "source_path": source,
        "mass_kg": mass,
        "size_m": size,
        "density_kg_m3": density,
        "inertia": [float(v) for v in inertia],
        "used_compute_mass_and_inertia": bool(result),
    }


def configure_axis16(client: RemoteAPIClient, sim: dict[str, int]) -> dict[str, float]:
    axis = client.call("sim.getObject", [f"{MODEL_PATH}/axis16"])
    current_pos = float(client.call("sim.getJointPosition", [axis]))
    client.call("sim.setObjectInt32Param", [axis, sim["jointintparam_motor_enabled"], 1])
    client.call("sim.setObjectInt32Param", [axis, sim["jointintparam_ctrl_enabled"], 1])
    client.call("sim.setObjectInt32Param", [axis, sim["jointintparam_dynctrlmode"], sim["jointdynctrl_spring"]])
    client.call("sim.setObjectFloatParam", [axis, sim["jointfloatparam_kc_k"], AXIS16_STIFFNESS])
    client.call("sim.setObjectFloatParam", [axis, sim["jointfloatparam_kc_c"], AXIS16_DAMPING])
    client.call("sim.setObjectFloatParam", [axis, sim["jointfloatparam_maxvel"], AXIS16_MAX_VEL])
    client.call("sim.setObjectFloatParam", [axis, sim["jointfloatparam_maxaccel"], JOINT_DYNAMICS["axis16"]["max_accel"]])
    client.call("sim.setObjectFloatParam", [axis, sim["jointfloatparam_maxjerk"], JOINT_DYNAMICS["axis16"]["max_jerk"]])
    client.call("sim.setJointTargetPosition", [axis, current_pos])
    client.call("sim.setJointTargetVelocity", [axis, 0.0])
    client.call("sim.setJointTargetForce", [axis, AXIS16_FORCE_LIMIT, True])
    return {
        "target_position_m": current_pos,
        "stiffness_n_m": AXIS16_STIFFNESS,
        "damping_ns_m": AXIS16_DAMPING,
        "force_limit_n": AXIS16_FORCE_LIMIT,
        "max_vel_m_s": AXIS16_MAX_VEL,
    }


def ensure_motor_force_caps(client: RemoteAPIClient) -> dict[str, dict[str, float]]:
    report: dict[str, dict[str, float]] = {}
    for joint_name, fallback_force in DEFAULT_FORCE_CAPS.items():
        handle = safe_get(client, f"{MODEL_PATH}/{joint_name}")
        if handle is None:
            continue
        before = float(client.call("sim.getJointTargetForce", [handle]))
        if abs(before) < fallback_force:
            client.call("sim.setJointTargetForce", [handle, fallback_force, True])
            after = float(client.call("sim.getJointTargetForce", [handle]))
            changed = 1.0
        else:
            after = before
            changed = 0.0
        report[joint_name] = {
            "target_force_before": before,
            "target_force_after": after,
            "applied_fallback": changed,
        }
    return report


def configure_joint_dynamics(client: RemoteAPIClient, sim: dict[str, int]) -> dict[str, dict[str, float]]:
    report: dict[str, dict[str, float]] = {}
    for joint_name, cfg in JOINT_DYNAMICS.items():
        handle = safe_get(client, f"{MODEL_PATH}/{joint_name}")
        if handle is None:
            continue
        client.call("sim.setObjectFloatParam", [handle, sim["jointfloatparam_maxvel"], cfg["max_vel"]])
        client.call("sim.setObjectFloatParam", [handle, sim["jointfloatparam_maxaccel"], cfg["max_accel"]])
        client.call("sim.setObjectFloatParam", [handle, sim["jointfloatparam_maxjerk"], cfg["max_jerk"]])
        report[joint_name] = cfg
    return report


def attach_script(client: RemoteAPIClient, sim: dict[str, int], root: int) -> None:
    remove_if_exists(client, SCRIPT_PATH)
    remove_if_exists(client, OLD_SCRIPT_PATH)
    script = client.call("sim.createScript", [sim["scripttype_customization"], REALISTIC_SCRIPT, 0, "lua"])
    client.call("sim.setObjectAlias", [script, SCRIPT_ALIAS])
    client.call("sim.setObjectParent", [script, root, True])


def attach_pick_place_script(client: RemoteAPIClient, sim: dict[str, int], root: int) -> None:
    remove_if_exists(client, PICK_PLACE_SCRIPT_PATH)
    script = client.call("sim.createScript", [sim["scripttype_simulation"], PICK_PLACE_SCRIPT, 0, "lua"])
    client.call("sim.setObjectAlias", [script, PICK_PLACE_SCRIPT_ALIAS])
    client.call("sim.setObjectParent", [script, root, True])


def orient_robot_for_yz_motion(client: RemoteAPIClient, sim: dict[str, int], root: int) -> list[float]:
    current = client.call("sim.getObjectOrientation", [root, sim["handle_world"]])
    target = [0.0, 0.0, 0.0]
    client.call("sim.setObjectOrientation", [root, sim["handle_world"], target])
    return target


def main() -> None:
    client, port = connect()
    try:
        sim = constants(client.call("zmqRemoteApi.info", ["sim"]))
        wait_stopped(client, sim)

        root = client.call("sim.getObject", [MODEL_PATH])
        gripper = client.call("sim.getObject", [f"{MODEL_PATH}/gripper_respondable"])

        remove_if_exists(client, PAYLOAD_PATH)
        remove_if_exists(client, f"{MODEL_PATH}/Revolute_joint")
        scaled_rows, before_mass, after_mass = scale_robot_mass_distribution(client, sim, root)
        payload_info = resolve_or_create_payload(client, sim, gripper)
        axis16_info = configure_axis16(client, sim)
        motor_force_info = ensure_motor_force_caps(client)
        joint_dynamics = configure_joint_dynamics(client, sim)
        root_orientation = orient_robot_for_yz_motion(client, sim, root)
        attach_script(client, sim, root)
        attach_pick_place_script(client, sim, root)
        client.call("sim.resetDynamicObject", [root])
        client.call("sim.resetDynamicObject", [int(payload_info["handle"])])
        client.call("sim.saveScene", [str(OUTPUT_SCENE)])

        report = {
            "connected_port": port,
            "model_path": MODEL_PATH,
            "output_scene": str(OUTPUT_SCENE),
            "robot_mass_target_kg": TARGET_ROBOT_MASS_KG,
            "robot_mass_before_kg": before_mass,
            "robot_mass_after_kg": after_mass,
            "uniform_mass_and_inertia_scale": TARGET_ROBOT_MASS_KG / before_mass,
            "scaled_shapes": [
                {
                    "alias": row["alias"],
                    "mass_before_kg": row["mass_before_kg"],
                    "mass_after_kg": row["mass_after_kg"],
                    "ixx_before": row["inertia_before"][0],
                    "iyy_before": row["inertia_before"][4],
                    "izz_before": row["inertia_before"][8],
                    "ixx_after": row["inertia_after"][0],
                    "iyy_after": row["inertia_after"][4],
                    "izz_after": row["inertia_after"][8],
                }
                for row in scaled_rows
            ],
            "payload": payload_info,
            "axis16_compensation": axis16_info,
            "motor_force_caps": motor_force_info,
            "joint_dynamics": joint_dynamics,
            "root_orientation_world_rad": root_orientation,
            "abb_reference": {
                "product_page": "https://www.abb.com/global/en/areas/robotics/products/robots/articulated-robots/irb-660",
                "product_spec_pdf": "https://library.e.abb.com/public/0459fa7676cb44a18efaedd87e44d4d1/3HAC023932%20PS%20IRB%20660-en.pdf",
                "notes": [
                    "ABB lists IRB 660 payload variants up to 250 kg and reach up to 3.15 m.",
                    "ABB product specification lists robot weight 1750 kg; scene was normalized to 1650 kg as requested by the user.",
                ],
            },
        }
        REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        print(f"connected_port={port}")
        print(f"robot_mass_before_kg={before_mass:.6f}")
        print(f"robot_mass_after_kg={after_mass:.6f}")
        print(f"payload_mass_kg={payload_info['mass_kg']:.6f}")
        print(f"output_scene={OUTPUT_SCENE}")
        print(f"report={REPORT_PATH.resolve()}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
