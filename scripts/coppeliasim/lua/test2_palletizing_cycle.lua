sim = require 'sim'

local modelPath = '/base_respondable'

local maxVel = {1.05, 0.85, 0.85}
local maxAccel = {2.2, 1.8, 1.8}
local maxJerk = {8.0, 7.0, 7.0}

local motors = {}
local gripper = -1
local attachDummy = -1
local attachedPayload = -1
local currentAttachOffset = 0.17
local generated = {}

local cycleStateTarget = -1

local pickStation = {0.58, -1.02, 0.0}
local pickStart = {1.02, -1.02, 0.0}
local palletStation = {0.55, 1.06, 0.0}
local palletEntry = {0.55, 1.55, 0.0}
local palletExit = {0.55, 1.55, 0.0}

local conveyorTopZ = 0.055
local palletSize = {0.78, 0.56, 0.080}
local cardboardSize = {0.66, 0.42, 0.015}
local waterBundleSize = {0.20, 0.34, 0.100}
local palletMass = 28.0
local cardboardMass = 1.2
local waterBundleMass = 63.0

local homeCfg = {0.0, math.rad(12), 0.0}
local transferCfg = {0.0, math.rad(22), 0.0}
local pickBaseDeg = 45.0
local placeBaseDeg = -45.0

local function startsWith(text, prefix)
    return string.sub(text, 1, string.len(prefix)) == prefix
end

local function setState(phase, layer, item)
    if cycleStateTarget == -1 then return end
    sim.setBufferProperty(
        cycleStateTarget,
        'customData.palletizingCycle',
        sim.packTable({
            phase = phase,
            layer = layer or 0,
            item = item or '',
            attached = attachedPayload ~= -1,
        })
    )
end

local function remember(handle)
    generated[#generated + 1] = handle
    return handle
end

local function removeIfExists(path)
    local ok, handle = pcall(sim.getObject, path)
    if ok and handle ~= -1 then
        sim.removeObjects({handle})
    end
end

local function cleanupGeneratedObjects()
    local objects = sim.getObjectsInTree(sim.handle_scene, sim.handle_all, 0)
    local toRemove = {}
    for i = 1, #objects do
        local alias = sim.getObjectAlias(objects[i], 1)
        if startsWith(alias, 'palletizing_') or
            startsWith(alias, 'cardboard_') or
            startsWith(alias, 'water_bundle_') or
            startsWith(alias, 'pallet_') then
            toRemove[#toRemove + 1] = objects[i]
        end
    end
    if #toRemove > 0 then
        sim.removeObjects(toRemove)
    end
    removeIfExists('/Cuboid')
end

local function setShapeStatic(handle, value)
    sim.setObjectInt32Param(handle, sim.shapeintparam_static, value and 1 or 0)
    sim.setObjectInt32Param(handle, sim.shapeintparam_respondable, 1)
    sim.resetDynamicObject(handle)
end

local function createBox(alias, size, mass, color, pose)
    local shape = sim.createPureShape(0, 16, size, mass)
    sim.setObjectAlias(shape, alias)
    sim.setObjectParent(shape, -1, true)
    sim.setShapeColor(shape, nil, sim.colorcomponent_ambient_diffuse, color)
    setShapeStatic(shape, true)
    if pose then
        sim.setObjectPosition(shape, sim.handle_world, {pose[1], pose[2], pose[3]})
        sim.setObjectOrientation(shape, sim.handle_world, {0, 0, 0})
    end
    return remember(shape)
end

local function createSceneFixtures()
    createBox(
        'palletizing_near_conveyor_visual',
        {0.95, 0.48, 0.050},
        0.001,
        {0.34, 0.36, 0.38},
        {(pickStation[1] + pickStart[1]) * 0.5, pickStation[2], conveyorTopZ * 0.5}
    )
    createBox(
        'palletizing_pallet_conveyor_visual',
        {0.95, 0.72, 0.050},
        0.001,
        {0.30, 0.32, 0.35},
        {palletStation[1], palletStation[2], conveyorTopZ * 0.5}
    )
end

local function rad(deg)
    return math.rad(deg)
end

local function motor2ForLoadCenter(centerZ, attachOffset)
    local desiredGripZ = centerZ + attachOffset
    local lowZ = 0.262
    local highZ = 0.875
    local t = (desiredGripZ - lowZ) / (highZ - lowZ)
    if t < 0 then t = 0 end
    if t > 1 then t = 1 end
    return rad(40.0 + (12.0 - 40.0) * t)
end

local function cfg(baseDeg, centerZ, attachOffset, above)
    local j2 = motor2ForLoadCenter(centerZ, attachOffset)
    if above then
        j2 = j2 - rad(10.0)
        if j2 < rad(10.0) then j2 = rad(10.0) end
    end
    return {rad(baseDeg), j2, 0.0}
end

local function moveToConfig(target, sync)
    sim.moveToConfig({
        joints = motors,
        targetPos = target,
        maxVel = maxVel,
        maxAccel = maxAccel,
        maxJerk = maxJerk,
        flags = sync and -1 or sim.ruckig_nosync,
    })
end

local function objectPose(x, y, z)
    return {x, y, z}
end

local function moveObjectLinear(handle, fromPose, toPose, duration)
    duration = duration or 1.0
    local elapsed = 0.0
    sim.setObjectPosition(handle, sim.handle_world, fromPose)
    while elapsed < duration and not sim.getSimulationStopping() do
        local dt = sim.getSimulationTimeStep()
        elapsed = math.min(duration, elapsed + dt)
        local t = elapsed / duration
        local p = {
            fromPose[1] * (1.0 - t) + toPose[1] * t,
            fromPose[2] * (1.0 - t) + toPose[2] * t,
            fromPose[3] * (1.0 - t) + toPose[3] * t,
        }
        sim.setObjectPosition(handle, sim.handle_world, p)
        sim.wait(dt)
    end
    sim.setObjectPosition(handle, sim.handle_world, toPose)
end

local function setAttachOffset(offset)
    currentAttachOffset = offset
    sim.setObjectPosition(attachDummy, sim.handle_parent, {0.0, 0.0, -currentAttachOffset})
    sim.setObjectOrientation(attachDummy, sim.handle_parent, {0.0, 0.0, 0.0})
end

local function attachObject(handle, attachOffset)
    setAttachOffset(attachOffset)
    attachedPayload = handle
    sim.setObjectParent(attachedPayload, -1, true)
    setShapeStatic(attachedPayload, true)
    sim.resetDynamicObject(attachedPayload)
end

local function releaseObject(handle, placePose)
    sim.setObjectParent(handle, -1, true)
    sim.setObjectPosition(handle, sim.handle_world, placePose)
    sim.setObjectOrientation(handle, sim.handle_world, {0.0, 0.0, 0.0})
    setShapeStatic(handle, true)
    sim.resetDynamicObject(handle)
    attachedPayload = -1
end

local function makeCardboard(index)
    local z = conveyorTopZ + cardboardSize[3] * 0.5
    return createBox(
        string.format('cardboard_%02d', index),
        cardboardSize,
        cardboardMass,
        {0.72, 0.55, 0.30},
        {pickStart[1], pickStart[2], z}
    ), z
end

local function makeWaterBundle(layer, index)
    local z = conveyorTopZ + waterBundleSize[3] * 0.5
    return createBox(
        string.format('water_bundle_%02d_%02d', layer, index),
        waterBundleSize,
        waterBundleMass,
        {0.12, 0.38, 0.95},
        {pickStart[1], pickStart[2], z}
    ), z
end

local function makePallet()
    local z = conveyorTopZ + palletSize[3] * 0.5
    return createBox(
        'pallet_01',
        palletSize,
        palletMass,
        {0.48, 0.30, 0.15},
        {palletEntry[1], palletEntry[2], z}
    ), z
end

local function pickAndPlace(handle, pickCenterZ, placePose, attachOffset, phaseItem, layer)
    local pickDown = cfg(pickBaseDeg, pickCenterZ, attachOffset, false)
    local pickAbove = cfg(pickBaseDeg, pickCenterZ, attachOffset, true)
    local placeDown = cfg(placeBaseDeg, placePose[3], attachOffset, false)
    local placeAbove = cfg(placeBaseDeg, placePose[3], attachOffset, true)

    setState('lift_before_pick', layer, phaseItem)
    moveToConfig(transferCfg, true)
    moveToConfig(pickAbove, true)
    setState('pick', layer, phaseItem)
    moveToConfig(pickDown, true)
    attachObject(handle, attachOffset)
    sim.wait(0.12)

    setState('move_loaded_to_pallet', layer, phaseItem)
    moveToConfig(pickAbove, true)
    moveToConfig(transferCfg, true)
    moveToConfig(placeAbove, true)
    setState('place', layer, phaseItem)
    moveToConfig(placeDown, true)
    releaseObject(handle, placePose)
    sim.wait(0.12)
    moveToConfig(placeAbove, true)
    moveToConfig(transferCfg, true)
end

local function feedToPick(handle, centerZ, itemName, layer)
    local fromPose = objectPose(pickStart[1], pickStart[2], centerZ)
    local toPose = objectPose(pickStation[1], pickStation[2], centerZ)
    setState('near_conveyor_infeed', layer, itemName)
    moveObjectLinear(handle, fromPose, toPose, 0.9)
end

local function runPalletizingCycle()
    local pallet, palletZ = makePallet()
    local palletStationPose = objectPose(palletStation[1], palletStation[2], palletZ)
    setState('pallet_infeed', 0, 'pallet')
    moveObjectLinear(pallet, objectPose(palletEntry[1], palletEntry[2], palletZ), palletStationPose, 1.2)

    moveToConfig(homeCfg, true)

    local palletTopZ = conveyorTopZ + palletSize[3]
    local layerPitch = cardboardSize[3] + waterBundleSize[3]
    local bundleOffsets = {-0.225, 0.0, 0.225}

    for layer = 1, 4 do
        local sheet, sheetPickZ = makeCardboard(layer)
        feedToPick(sheet, sheetPickZ, 'cardboard', layer)
        local sheetPlaceZ = palletTopZ + (layer - 1) * layerPitch + cardboardSize[3] * 0.5
        pickAndPlace(
            sheet,
            sheetPickZ,
            objectPose(palletStation[1], palletStation[2], sheetPlaceZ),
            cardboardSize[3] * 0.5 + 0.17,
            'cardboard',
            layer
        )

        for i = 1, 3 do
            local bundle, bundlePickZ = makeWaterBundle(layer, i)
            feedToPick(bundle, bundlePickZ, string.format('water_bundle_%d', i), layer)
            local bundlePlaceZ = palletTopZ + (layer - 1) * layerPitch + cardboardSize[3] + waterBundleSize[3] * 0.5
            pickAndPlace(
                bundle,
                bundlePickZ,
                objectPose(palletStation[1] + bundleOffsets[i], palletStation[2], bundlePlaceZ),
                waterBundleSize[3] * 0.5 + 0.17,
                string.format('water_bundle_%d', i),
                layer
            )
        end
    end

    setState('return_home', 4, '')
    moveToConfig(transferCfg, true)
    moveToConfig(homeCfg, true)
    setState('pallet_outfeed', 4, 'pallet')
    moveObjectLinear(pallet, palletStationPose, objectPose(palletExit[1], palletExit[2], palletZ), 1.2)
    setState('cycle_complete', 4, '4_cardboards_12_water_bundles')
end

function sysCall_init()
    cleanupGeneratedObjects()
    motors = {
        sim.getObject(modelPath .. '/motor1'),
        sim.getObject(modelPath .. '/motor2'),
        sim.getObject(modelPath .. '/motor3'),
    }
    gripper = sim.getObject(modelPath .. '/gripper_respondable')
    cycleStateTarget = sim.getObject(modelPath)

    local ok, dummy = pcall(sim.getObject, modelPath .. '/palletizingAttachDummy')
    if ok and dummy ~= -1 then
        attachDummy = dummy
    else
        attachDummy = sim.createDummy(0.02)
        sim.setObjectAlias(attachDummy, 'palletizingAttachDummy')
        sim.setObjectParent(attachDummy, gripper, true)
    end
    sim.setObjectInt32Param(attachDummy, sim.objintparam_visibility_layer, 0)
    setAttachOffset(currentAttachOffset)

    createSceneFixtures()
    setState('ready', 0, '')
end

function sysCall_thread()
    runPalletizingCycle()
    while not sim.getSimulationStopping() do
        sim.wait(0.1)
    end
end

function sysCall_actuation()
    if attachedPayload ~= -1 then
        local m = sim.getObjectMatrix(attachDummy, sim.handle_world)
        sim.setObjectMatrix(attachedPayload, sim.handle_world, m)
    end
end

function sysCall_cleanup()
    attachedPayload = -1
end
