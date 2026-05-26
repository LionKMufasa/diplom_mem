from __future__ import annotations

import time
from pathlib import Path

from remote_ik_demo import RemoteAPIClient, constants


MODEL_PATH = "/base_respondable"
SCRIPT_ALIAS = "torque_graph_script"
SCRIPT_PATH = f"{MODEL_PATH}/{SCRIPT_ALIAS}"
DEFAULT_SCENE = Path(r"C:\Users\egork\Desktop\coppelia_dpilom\test2.ttt")
OUTPUT_SCENE = Path(r"C:\Users\egork\Desktop\coppelia_dpilom\test2_torque_graphs.ttt")


TORQUE_MONITOR_SCRIPT = r"""
sim = require 'sim'

local modelPath = '/base_respondable'
local plotId = 1
local timeWindow = 20.0
local csvPath = 'C:/Users/egork/Desktop/coppelia_dpilom/test2_joint_torques.csv'
local recordAllJointsToCsv = true
local plotAllJointsIfNoMotors = true

local palette = {
    {230, 57, 70},
    {29, 53, 87},
    {69, 123, 157},
    {42, 157, 143},
    {233, 196, 106},
    {244, 162, 97},
    {131, 56, 236},
    {255, 0, 110},
    {58, 134, 255},
    {0, 158, 115},
    {213, 94, 0},
    {86, 180, 233},
    {204, 121, 167},
    {0, 114, 178},
    {240, 228, 66},
    {0, 0, 0},
}

local function shortName(alias)
    return string.gsub(alias, '^.*/', '')
end

local function csvEscape(text)
    text = tostring(text)
    if string.find(text, '[,"]') then
        text = '"' .. string.gsub(text, '"', '""') .. '"'
    end
    return text
end

local function isMotorName(name)
    local low = string.lower(name)
    return string.find(low, 'motor', 1, true) ~= nil
end

local function readForce(joint)
    local ok, value = pcall(sim.getJointForce, joint.handle)
    if ok and value then return value end
    return 0
end

local function findRoot()
    local candidates = {
        modelPath,
        '/base',
        '/IRB660',
        '/ABB_IRB_660',
        '/robot',
    }
    for i = 1, #candidates do
        local ok, handle = pcall(sim.getObject, candidates[i])
        if ok and handle ~= -1 then return handle end
    end
    return -1
end

local function collectJoints()
    allJoints = {}
    motorJoints = {}

    root = findRoot()
    local handles
    if root ~= -1 then
        handles = sim.getObjectsInTree(root, sim.sceneobject_joint, 0)
    else
        handles = sim.getObjects(sim.sceneobject_joint)
    end

    for i = 1, #handles do
        local h = handles[i]
        local jointType = sim.getJointType(h)
        if jointType == sim.joint_revolute or jointType == sim.joint_prismatic then
            local alias = sim.getObjectAlias(h, 1)
            local item = {
                handle = h,
                alias = alias,
                name = shortName(alias),
                type = jointType,
                unit = jointType == sim.joint_prismatic and 'N' or 'N*m',
            }
            allJoints[#allJoints + 1] = item
            if isMotorName(alias) then
                motorJoints[#motorJoints + 1] = item
            end
        end
    end

    table.sort(allJoints, function(a, b) return a.alias < b.alias end)
    table.sort(motorJoints, function(a, b) return a.alias < b.alias end)

    plotJoints = motorJoints
    if #plotJoints == 0 and plotAllJointsIfNoMotors then plotJoints = allJoints end
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
        sim.addLog(sim.verbosity_warnings, 'Torque monitor: simUI plugin is not available, CSV logging only.')
        simUI = nil
        return
    end
    simUI = module

    destroyUi()
    local xml = [[
        <ui title="Joint torque monitor" closeable="true" resizable="true" placement="relative" position="20,20" size="940,520">
            <plot id="1" />
        </ui>
    ]]
    ui = simUI.create(xml)
    simUI.setPlotLabels(ui, plotId, 'simulation time [s]', 'torque [N*m] / force [N]')
    simUI.setPlotRanges(ui, plotId, 0, timeWindow, -100, 100)
    simUI.setLegendVisibility(ui, plotId, true)

    for i = 1, #plotJoints do
        local color = palette[((i - 1) % #palette) + 1]
        simUI.addCurve(
            ui,
            plotId,
            simUI.curve_type.time,
            plotJoints[i].name,
            color,
            simUI.curve_style.line,
            {}
        )
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
    if ok and file then
        csvFile = file
        local header = {'time_s'}
        local source = recordAllJointsToCsv and allJoints or plotJoints
        for i = 1, #source do
            header[#header + 1] = source[i].name .. '_' .. source[i].unit
        end
        for i = 1, #header do header[i] = csvEscape(header[i]) end
        csvFile:write(table.concat(header, ',') .. '\n')
        csvFile:flush()
        sim.addLog(sim.verbosity_scriptinfos, 'Torque monitor CSV: ' .. csvPath)
    else
        sim.addLog(sim.verbosity_warnings, 'Torque monitor: could not open CSV file: ' .. csvPath)
    end
end

local function resetCurves()
    if simUI and ui then
        for i = 1, #plotJoints do
            pcall(simUI.clearCurve, ui, plotId, plotJoints[i].name)
        end
        pcall(simUI.setPlotRanges, ui, plotId, 0, timeWindow, -100, 100)
        pcall(simUI.replot, ui, plotId)
    end
end

local function writeCsvLine(t)
    if not csvFile then return end
    local source = recordAllJointsToCsv and allJoints or plotJoints
    local row = {string.format('%.6f', t)}
    for i = 1, #source do
        row[#row + 1] = string.format('%.8g', readForce(source[i]))
    end
    csvFile:write(table.concat(row, ',') .. '\n')
    csvFile:flush()
end

local function updateUi(t)
    if not (simUI and ui) then return end
    for i = 1, #plotJoints do
        local item = plotJoints[i]
        simUI.addCurveTimePoints(ui, plotId, item.name, {t}, {readForce(item)})
    end
    local xMin = math.max(0, t - timeWindow)
    local xMax = math.max(timeWindow, t + 0.05)
    pcall(simUI.setPlotXRange, ui, plotId, xMin, xMax)
    if t - lastRescaleTime > 0.5 then
        pcall(simUI.rescaleAxesAll, ui, plotId, true, true)
        pcall(simUI.replot, ui, plotId)
        lastRescaleTime = t
    end
end

local function sample()
    if #plotJoints == 0 then return end
    local t = sim.getSimulationTime()
    writeCsvLine(t)
    updateUi(t)

    local values = {}
    for i = 1, #plotJoints do
        values[#values + 1] = plotJoints[i].name .. '=' .. string.format('%.5g', readForce(plotJoints[i]))
    end
    sim.setStringSignal('joint_torque_monitor', 't=' .. string.format('%.3f', t) .. ',' .. table.concat(values, ','))
end

function sysCall_init()
    lastRescaleTime = -1
    collectJoints()
    createUi()
    if sim.getSimulationState() ~= sim.simulation_stopped then
        resetCurves()
        openCsv()
    end
    sim.addLog(
        sim.verbosity_scriptinfos,
        'Torque monitor ready: plotting ' .. tostring(#plotJoints) ..
        ' motor joint(s), CSV joint count ' .. tostring(#allJoints)
    )
end

function sysCall_beforeSimulation()
    resetCurves()
    openCsv()
    lastRescaleTime = -1
end

function sysCall_sensing()
    sample()
end

function sysCall_afterSimulation()
    closeCsv()
end

function sysCall_cleanup()
    closeCsv()
    destroyUi()
end

function getMonitoredJoints()
    local names = {}
    for i = 1, #plotJoints do names[#names + 1] = plotJoints[i].alias end
    return names
end

function getLastTorqueValues()
    local values = {}
    for i = 1, #plotJoints do
        values[plotJoints[i].name] = readForce(plotJoints[i])
    end
    return values
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


def install_script(client: RemoteAPIClient, sim: dict[str, int], root: int) -> int:
    remove_if_present(client, SCRIPT_PATH)
    script = client.call("sim.createScript", [sim["scripttype_customization"], TORQUE_MONITOR_SCRIPT, 0, "lua"])
    client.call("sim.setObjectAlias", [script, SCRIPT_ALIAS])
    client.call("sim.setObjectParent", [script, root, True])
    client.call("sim.initScript", [script])
    return script


def main() -> None:
    client = None
    last_error = None
    for port in (23000, 23001, 23050, 23051):
        probe = RemoteAPIClient(port=port)
        probe.socket.RCVTIMEO = 5000
        try:
            probe.call("zmqRemoteApi.require", ["sim"])
            client = probe
            print(f"connected_port={port}")
            break
        except Exception as exc:
            last_error = exc
            probe.close()
    if client is None:
        raise RuntimeError(f"Could not connect to CoppeliaSim ZMQ remote API: {last_error!r}")
    client.socket.RCVTIMEO = 120000
    try:
        sim = constants(client.call("zmqRemoteApi.info", ["sim"]))

        state = client.call("sim.getSimulationState")
        if state != sim["simulation_stopped"]:
            wait_stopped(client, sim)

        root = safe_get(client, MODEL_PATH)
        if root is None:
            client.call("sim.loadScene", [str(DEFAULT_SCENE)])
            root = safe_get(client, MODEL_PATH)
        if root is None:
            raise RuntimeError(f"Missing {MODEL_PATH}; open test2.ttt or adjust MODEL_PATH")

        script = install_script(client, sim, root)
        monitored = client.call("sim.callScriptFunction", ["getMonitoredJoints", script])
        client.call("sim.saveScene", [str(OUTPUT_SCENE)])

        print(f"scene_out={OUTPUT_SCENE}")
        print(f"script={SCRIPT_PATH} handle={script}")
        print("monitored_plot_joints=" + ", ".join(monitored))
        print(r"csv=C:\Users\egork\Desktop\coppelia_dpilom\test2_joint_torques.csv")
    finally:
        client.close()


if __name__ == "__main__":
    main()
