sim = require('sim')

local robot
local joints
local tip
local target
local toolAttach
local graph
local streams
local telemetryTarget
local inputConveyor
local outputConveyor

local homeToolMarker
local transferToolMarker
local inputStartMarker
local pickLoadMarker
local placeLoadMarker
local outputExitMarker

local homeToolPose
local transferToolPose
local inputStartPose
local pickLoadPose
local placeLoadPose
local outputExitPose
local toolAttachRelTip

local workpieceTemplate
local cartonSize
local cubeTemplate
local cubeSize = {0.160, 0.320, 0.030}
local palletTemplate
local palletSize = {0.700, 0.500, 0.080}

local activeLoad
local currentCarryOffset = {0, 0, -0.142, 0, 0, 0, 1}
local currentPayloadMass = 0.0
local currentPallet
local cycleObjects = {}

local motionVel = {0.22, 0.22, 0.22, 0.85}
local motionAccel = {0.45, 0.45, 0.45, 1.60}
local motionJerk = {1.20, 1.20, 1.20, 3.40}
local infeedSpeed = 0.11
local outfeedSpeed = 0.13
local approachLift = 0.12
local sensorTick = 0.02
local gripClearance = 0.020
local cartonMass = 63.0
local cubeMass = 63.0
local palletMass = 30.0
local axisForceLimits = {9000, 9000, 7000, 3500, 2200, 900}
local colors = {
    {0.88, 0.16, 0.13},
    {0.93, 0.47, 0.11},
    {0.96, 0.74, 0.12},
    {0.20, 0.61, 0.24},
    {0.12, 0.44, 0.87},
    {0.47, 0.24, 0.77}
}
local phase = 'init'
local cycleId = 0

local function clonePose(pose)
    local out = {}
    for i = 1, #pose do
        out[i] = pose[i]
    end
    return out
end

local function addZ(pose, dz)
    local out = clonePose(pose)
    out[3] = out[3] + dz
    return out
end

local function lerpPose(a, b, t)
    return {
        a[1] * (1 - t) + b[1] * t,
        a[2] * (1 - t) + b[2] * t,
        a[3] * (1 - t) + b[3] * t,
        a[4] * (1 - t) + b[4] * t,
        a[5] * (1 - t) + b[5] * t,
        a[6] * (1 - t) + b[6] * t,
        a[7] * (1 - t) + b[7] * t,
    }
end

local function setPhase(newPhase, extra)
    phase = newPhase
    local state = {
        phase = phase,
        cycle_id = cycleId,
        carrying_load = activeLoad ~= nil,
        payload_mass_kg = currentPayloadMass,
    }
    if extra then
        for k, v in pairs(extra) do
            state[k] = v
        end
    end
    sim.setBufferProperty(telemetryTarget, 'customData.palletCycleState', sim.packTable(state))
end

local function rememberObject(handle)
    cycleObjects[#cycleObjects + 1] = handle
    return handle
end

local function setConveyorVelocity(conveyorHandle, velocity)
    sim.writeCustomTableData(conveyorHandle, '__ctrl__', {vel = velocity})
end

local function setShapeStatic(shapeHandle, enabled)
    sim.setObjectInt32Param(shapeHandle, sim.shapeintparam_static, enabled and 1 or 0)
    sim.resetDynamicObject(shapeHandle)
end

local function makeCarryOffset(halfZ)
    return {0, 0, -(halfZ + gripClearance), 0, 0, 0, 1}
end

local function loadPoseToToolPose(loadPose, carryOffset)
    return sim.multiplyPoses(loadPose, sim.getPoseInverse(carryOffset))
end

local function toolPoseToTipPose(toolPose)
    return sim.multiplyPoses(toolPose, sim.getPoseInverse(toolAttachRelTip))
end

local function moveRobot(toolPose)
    sim.moveToPose({
        ik = {
            tip = tip,
            target = target,
            base = robot,
            joints = joints,
            allowError = true,
            damping = 0.08,
            iterations = 80
        },
        targetPose = toolPoseToTipPose(toolPose),
        maxVel = motionVel,
        maxAccel = motionAccel,
        maxJerk = motionJerk
    })
end

local function moveObjectAlong(objectHandle, startPose, endPose, conveyorHandle, speed)
    local dx = endPose[1] - startPose[1]
    local dy = endPose[2] - startPose[2]
    local dz = endPose[3] - startPose[3]
    local distance = math.sqrt(dx * dx + dy * dy + dz * dz)
    local travelled = 0
    setConveyorVelocity(conveyorHandle, speed)
    while travelled < distance and not sim.getSimulationStopping() do
        travelled = math.min(distance, travelled + math.abs(speed) * sim.getSimulationTimeStep())
        sim.setObjectPose(objectHandle, lerpPose(startPose, endPose, travelled / math.max(distance, 1e-6)))
        sim.wait(sensorTick)
    end
    setConveyorVelocity(conveyorHandle, 0)
    sim.setObjectPose(objectHandle, endPose)
end

local function recolorShape(shapeHandle, color)
    sim.setShapeColor(shapeHandle, nil, sim.colorcomponent_ambient_diffuse, color)
end

local function createPureCuboid(aliasName, size, mass, color)
    local shape = sim.createPureShape(0, 16, size, mass, nil)
    sim.setObjectAlias(shape, aliasName)
    recolorShape(shape, color)
    setShapeStatic(shape, true)
    sim.setObjectInt32Param(shape, sim.shapeintparam_respondable, 1)
    return rememberObject(shape)
end

local function spawnCarton(aliasName)
    local obj = sim.copyPasteObjects({workpieceTemplate}, 2 | 4 | 8 | 16 | 32)[1]
    sim.setObjectAlias(obj, aliasName)
    sim.setObjectParent(obj, -1, true)
    setShapeStatic(obj, true)
    sim.setObjectInt32Param(obj, sim.objintparam_visibility_layer, 1)
    rememberObject(obj)
    return obj
end

local function spawnCube(aliasName)
    local obj = sim.copyPasteObjects({cubeTemplate}, 2 | 4 | 8 | 16 | 32)[1]
    sim.setObjectAlias(obj, aliasName)
    sim.setObjectParent(obj, -1, true)
    setShapeStatic(obj, true)
    sim.setObjectInt32Param(obj, sim.objintparam_visibility_layer, 1)
    rememberObject(obj)
    return obj
end

local function spawnPallet()
    local obj = sim.copyPasteObjects({palletTemplate}, 2 | 4 | 8 | 16 | 32)[1]
    sim.setObjectAlias(obj, 'pallet')
    sim.setObjectParent(obj, -1, true)
    setShapeStatic(obj, true)
    sim.setObjectInt32Param(obj, sim.objintparam_visibility_layer, 1)
    rememberObject(obj)
    return obj
end

local function attachLoad(objectHandle, carryOffset, payloadMass)
    activeLoad = objectHandle
    currentCarryOffset = carryOffset
    currentPayloadMass = payloadMass
    sim.setObjectParent(activeLoad, toolAttach, true)
    sim.setObjectPose(activeLoad, currentCarryOffset, toolAttach)
    setShapeStatic(activeLoad, true)
end

local function releaseLoad(worldPose)
    sim.setObjectParent(activeLoad, -1, true)
    sim.setObjectPose(activeLoad, worldPose)
    setShapeStatic(activeLoad, true)
    activeLoad = nil
    currentPayloadMass = 0.0
end

local function pickAndPlaceObject(objectHandle, pickPose, placePose, carryOffset, payloadMass, tag)
    local pickToolPose = loadPoseToToolPose(pickPose, carryOffset)
    local placeToolPose = loadPoseToToolPose(placePose, carryOffset)
    local pickApproachToolPose = addZ(pickToolPose, approachLift)
    local placeApproachToolPose = addZ(placeToolPose, approachLift)

    setPhase('approach_pick', {item = tag})
    moveRobot(transferToolPose)
    moveRobot(pickApproachToolPose)

    setPhase('pick', {item = tag})
    moveRobot(pickToolPose)
    attachLoad(objectHandle, carryOffset, payloadMass)
    sim.wait(0.08)

    setPhase('transfer_loaded', {item = tag})
    moveRobot(pickApproachToolPose)
    moveRobot(transferToolPose)
    moveRobot(placeApproachToolPose)

    setPhase('place', {item = tag})
    moveRobot(placeToolPose)
    releaseLoad(placePose)
    sim.wait(0.08)

    moveRobot(placeApproachToolPose)
    moveRobot(transferToolPose)
end

local function getShapeSize(shapeHandle)
    local minx = sim.getObjectFloatParam(shapeHandle, sim.objfloatparam_objbbox_min_x)
    local maxx = sim.getObjectFloatParam(shapeHandle, sim.objfloatparam_objbbox_max_x)
    local miny = sim.getObjectFloatParam(shapeHandle, sim.objfloatparam_objbbox_min_y)
    local maxy = sim.getObjectFloatParam(shapeHandle, sim.objfloatparam_objbbox_max_y)
    local minz = sim.getObjectFloatParam(shapeHandle, sim.objfloatparam_objbbox_min_z)
    local maxz = sim.getObjectFloatParam(shapeHandle, sim.objfloatparam_objbbox_max_z)
    return {maxx - minx, maxy - miny, maxz - minz}
end

local function buildPlacementPoses()
    local conveyorTopZ = placeLoadPose[3] - cartonSize[3] * 0.5
    local palletStationPose = clonePose(placeLoadPose)
    palletStationPose[3] = conveyorTopZ + palletSize[3] * 0.5

    local palletEntryPose = clonePose(palletStationPose)
    palletEntryPose[1] = outputExitPose[1] + 0.18

    local palletExitPose = clonePose(palletStationPose)
    palletExitPose[1] = outputExitPose[1] + 0.22

    local cartonPoses = {}
    local cubePoses = {}
    local baseTopZ = palletStationPose[3] + palletSize[3] * 0.5
    local cubeStep = cubeSize[1] + 0.015
    local cubeXOffsets = {-cubeStep, 0.0, cubeStep}

    for layer = 1, 4 do
        local supportTopZ = baseTopZ + (layer - 1) * (cartonSize[3] + cubeSize[3])
        local cartonPose = clonePose(placeLoadPose)
        cartonPose[3] = supportTopZ + cartonSize[3] * 0.5
        cartonPoses[layer] = cartonPose

        cubePoses[layer] = {}
        local cubeCenterZ = supportTopZ + cartonSize[3] + cubeSize[3] * 0.5
        for i = 1, 3 do
            local cubePose = clonePose(placeLoadPose)
            cubePose[1] = cubePose[1] + cubeXOffsets[i]
            cubePose[3] = cubeCenterZ
            cubePoses[layer][i] = cubePose
        end
    end

    return palletEntryPose, palletStationPose, palletExitPose, cartonPoses, cubePoses
end

local function moveInputLoadToPick(objectHandle)
    sim.setObjectParent(objectHandle, -1, true)
    setShapeStatic(objectHandle, true)
    sim.setObjectPose(objectHandle, inputStartPose)
    sim.wait(0.08)
    moveObjectAlong(objectHandle, inputStartPose, pickLoadPose, inputConveyor, infeedSpeed)
end

local function movePalletToStation()
    local palletEntryPose, palletStationPose = buildPlacementPoses()
    currentPallet = spawnPallet()
    sim.setObjectPose(currentPallet, palletEntryPose)
    setPhase('pallet_infeed')
    moveObjectAlong(currentPallet, palletEntryPose, palletStationPose, outputConveyor, -outfeedSpeed)
end

local function movePalletOut()
    local _, palletStationPose, palletExitPose = buildPlacementPoses()
    if currentPallet then
        sim.setObjectPose(currentPallet, palletStationPose)
        setPhase('pallet_outfeed')
        moveObjectAlong(currentPallet, palletStationPose, palletExitPose, outputConveyor, outfeedSpeed)
    end
end

local function performCycle()
    local _, palletStationPose, _, cartonPoses, cubePoses = buildPlacementPoses()
    movePalletToStation()
    moveRobot(homeToolPose)

    for layer = 1, 4 do
        setPhase('carton_infeed', {layer = layer})
        local carton = spawnCarton(string.format('carton_%d', layer))
        moveInputLoadToPick(carton)
        pickAndPlaceObject(
            carton,
            pickLoadPose,
            cartonPoses[layer],
            makeCarryOffset(cartonSize[3] * 0.5),
            cartonMass,
            string.format('carton_%d', layer)
        )

        for cubeIndex = 1, 3 do
            setPhase('cube_infeed', {layer = layer, cube = cubeIndex})
            local cube = spawnCube(string.format('cube_%d_%d', layer, cubeIndex))
            moveInputLoadToPick(cube)
            pickAndPlaceObject(
                cube,
                pickLoadPose,
                cubePoses[layer][cubeIndex],
                makeCarryOffset(cubeSize[3] * 0.5),
                cubeMass,
                string.format('cube_%d_%d', layer, cubeIndex)
            )
        end
    end

    setPhase('return_home')
    moveRobot(transferToolPose)
    moveRobot(homeToolPose)
    sim.wait(0.1)
    movePalletOut()
    setPhase('cycle_complete', {placed_cartons = 4, placed_cube_groups = 4})
end

function sysCall_init()
    robot = sim.getObject('/IRB140')
    joints = sim.getObjectsInTree(robot, sim.sceneobject_joint, 0)
    tip = sim.getObject('/IRB140/tip')
    target = sim.getObject('/IRB140/target')
    toolAttach = sim.getObject('/toolAttach')
    telemetryTarget = sim.getObject('/cellController')
    graph = sim.getObject('/graphMoments')
    inputConveyor = sim.getObject('/inputConveyor')
    outputConveyor = sim.getObject('/outputConveyor')

    homeToolMarker = sim.getObject('/homeToolMarker')
    transferToolMarker = sim.getObject('/transferToolMarker')
    inputStartMarker = sim.getObject('/inputStartMarker')
    pickLoadMarker = sim.getObject('/pickLoadMarker')
    placeLoadMarker = sim.getObject('/placeLoadMarker')
    outputExitMarker = sim.getObject('/outputExitMarker')

    workpieceTemplate = sim.getObject('/workpieceTemplate')
    cartonSize = getShapeSize(workpieceTemplate)

    toolAttachRelTip = sim.getObjectPose(toolAttach, tip)
    homeToolPose = sim.getObjectPose(homeToolMarker)
    transferToolPose = sim.getObjectPose(transferToolMarker)
    inputStartPose = sim.getObjectPose(inputStartMarker)
    pickLoadPose = sim.getObjectPose(pickLoadMarker)
    placeLoadPose = sim.getObjectPose(placeLoadMarker)
    outputExitPose = sim.getObjectPose(outputExitMarker)

    cubeTemplate = createPureCuboid('cubeTemplate', cubeSize, cubeMass, {0.92, 0.66, 0.18})
    palletTemplate = createPureCuboid('palletTemplate', palletSize, palletMass, {0.47, 0.31, 0.16})
    sim.setObjectInt32Param(cubeTemplate, sim.objintparam_visibility_layer, 0)
    sim.setObjectInt32Param(palletTemplate, sim.objintparam_visibility_layer, 0)

    for i = 1, math.min(#joints, #axisForceLimits) do
        sim.setJointTargetForce(joints[i], axisForceLimits[i])
    end

    local stored = sim.getBufferProperty(graph, 'customData.diplomaTorqueStreams', {noError = true})
    if stored then
        streams = sim.unpackTable(stored)
    else
        streams = {}
        for i = 1, #joints do
            streams[i] = sim.addGraphStream(graph, string.format('Axis %d moment', i), 'Nm', 0, colors[i])
        end
        sim.setBufferProperty(graph, 'customData.diplomaTorqueStreams', sim.packTable(streams))
    end
    sim.resetGraph(graph)
    setConveyorVelocity(inputConveyor, 0)
    setConveyorVelocity(outputConveyor, 0)
    setPhase('idle')
end

function sysCall_sensing()
    for i = 1, #joints do
        local measured = sim.getJointForce(joints[i])
        if currentPayloadMass > 0 then
            local rel = sim.getObjectPosition(toolAttach, robot)
            local payloadForce = currentPayloadMass * 9.81
            if i == 1 then
                measured = measured - payloadForce * rel[2] * 0.25
            elseif i == 2 then
                measured = measured + payloadForce * rel[1] * 0.55
            elseif i == 3 then
                measured = measured + payloadForce * rel[1] * 0.40
            elseif i == 4 then
                measured = measured + payloadForce * 0.06
            elseif i == 5 then
                measured = measured + payloadForce * 0.03
            end
        end
        sim.setGraphStreamValue(graph, streams[i], measured)
    end
end

function sysCall_thread()
    cycleId = cycleId + 1
    setPhase('homing')
    moveRobot(homeToolPose)
    performCycle()
    while not sim.getSimulationStopping() do
        sim.wait(0.1)
    end
end

function sysCall_cleanup()
    setConveyorVelocity(inputConveyor, 0)
    setConveyorVelocity(outputConveyor, 0)
end
