sim = require 'sim'
local simIK = nil
pcall(function()
    simIK = require 'simIK'
end)

local modelPath = '/base_respondable'
local motorNames = {'motor1', 'motor2', 'motor3', 'motor4'}
local motionMotorNames = {'motor1', 'motor2', 'motor3'}

local maxVel = {1.85, 1.65, 1.65}
local maxAccel = {3.0, 2.6, 2.6}
local maxJerk = {11.0, 9.5, 9.5}
local poseMaxVel = {0.24, 0.24, 0.24, 0.8}
local poseMaxAccel = {0.45, 0.45, 0.45, 1.2}
local poseMaxJerk = {1.0, 1.0, 1.0, 2.4}

local motors = {}
local motionMotors = {}
local gripper = -1
local attachDummy = -1
local ikTip = -1
local ikTarget = -1
local closedIkEnv = nil
local closedIkGroup = nil
local closedIkGroupFallback = nil
local closedIkJoints = {}
local closedIkToSimMap = {}
local closedIkTarget = nil
local ikDebugSignal = 'palletizing_debug_ik'
local ikWarningSignal = 'palletizing_last_ik_warning'
local calibrationModeSignal = 'palletizing_calibration_mode'
local ui = nil
local simUI = nil

local templates = {}
local templateVisibility = {}
local templatePoses = {}
local generatedObjects = {}
local placedObjects = {}
local activeLoad = -1
local pallet = -1
local cycleIndex = 0
local graphState = {}
local lastGraphTime = 0.0
local graphPeriod = 0.04

local cardboardMass = 0.35
local waterBundleMass = 9.0
local palletMass = 18.0
local payloadRespondable = false
local gripContactClearance = 0.006
local poseApproachLift = 0.18
local tcpLocalOffset = {0.0, -0.105, 0.0}
local poseReachTolerance = 0.12
local maxLoopClosureError = 0.01
local poseStepDistance = 0.08
local closedIkTargetTimeout = 0.6
local goalConfigSearchTime = 0.75
local goalConfigSearchMaxDist = 3.0
local goalConfigJointStep = math.rad(5.0)
local cardboardGripEdgeInset = 0.08
local cardboardPlaceYaw = math.rad(-90)
local waterPlaceYaw = 0.0
local releaseSnapTolerance = 0.20
local releaseCorrectionSpeed = 0.65
local releaseCorrectionMinDuration = 0.18
local releaseCorrectionMaxDuration = 0.9
local allowLargeReleaseCorrection = false
local useUarmStyleConfigMotion = true
local usePlaceSeedConfigs = true
local infiniteCycleDefault = true
local infiniteCycleSignal = 'palletizing_infinite_cycle'
local palletStationZOverride = 0.134
local palletArrivalWait = 0.15
local gripSettleWait = 0.05
local releaseSettleWait = 0.05
local cycleCompleteHold = 0.6
local cycleRestartWait = 0.15
local outfeedDuration = 1.35
local outfeedVelocity = 0.28
local cardboardCarryLocalPosition = nil
local waterCarryLocalPosition = {0.06, 0.19, 0.0}

local palletStationPose
local palletExitPose
local cardboardPickPose
local cardboardGripPose
local waterPickPose
local stackCenter
local palletTopZ
local cardboardHeight
local waterBundleHeight
local waterBundleSize

local function rad(deg)
    return math.rad(deg)
end

local function copyPose(pose)
    local out = {}
    for i = 1, #pose do out[i] = pose[i] end
    return out
end

local function poseWithDz(pose, dz)
    local out = copyPose(pose)
    out[3] = out[3] + dz
    return out
end

local function carryOffsetForHeight(height)
    return {0.0, 0.0, -(height * 0.5 + gripContactClearance), 0.0, 0.0, 0.0, 1.0}
end

local function loadPoseToToolPose(loadPose, height)
    local out = copyPose(loadPose)
    out[3] = out[3] + height * 0.5 + gripContactClearance
    return out
end

local function quatMultiply(a, b)
    return {
        a[4] * b[1] + a[1] * b[4] + a[2] * b[3] - a[3] * b[2],
        a[4] * b[2] - a[1] * b[3] + a[2] * b[4] + a[3] * b[1],
        a[4] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[4],
        a[4] * b[4] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
    }
end

local function yawQuaternion(angle)
    return {0.0, 0.0, math.sin(angle * 0.5), math.cos(angle * 0.5)}
end

local function poseWithYawCorrection(pose, yaw)
    local out = copyPose(pose)
    if yaw and math.abs(yaw) > 1e-9 then
        local q = quatMultiply(yawQuaternion(yaw), {pose[4], pose[5], pose[6], pose[7]})
        out[4], out[5], out[6], out[7] = q[1], q[2], q[3], q[4]
    end
    return out
end

local function poseDistance(a, b)
    local dx = (a[1] or 0.0) - (b[1] or 0.0)
    local dy = (a[2] or 0.0) - (b[2] or 0.0)
    local dz = (a[3] or 0.0) - (b[3] or 0.0)
    return math.sqrt(dx * dx + dy * dy + dz * dz)
end

local cfgHome = {rad(0), rad(12), rad(-20)}
local cfgTransfer = {rad(0), rad(18), rad(-20)}
local cfgCardboardAbove = {rad(-90), rad(28), rad(0)}
local cfgCardboardDown = {rad(-90), rad(43), rad(40)}
local cfgBottleAbove = {rad(0), rad(12), rad(-20)}
local cfgBottleDown = {rad(0), rad(28), rad(60)}
local cfgPalletAbove = {rad(0), rad(50), rad(40)}
local cfgPalletDown = {rad(0), rad(60), rad(40)}
local cfgCardboardPlaceAbove = {
    {rad(0), rad(50), rad(40)},
    {rad(0), rad(40), rad(20)},
    {rad(0), rad(30), rad(0)},
    {rad(0), rad(20), rad(-10)},
}
local cfgCardboardPlaceDown = {
    {rad(0), rad(60), rad(40)},
    {rad(0), rad(45), rad(25)},
    {rad(0), rad(30), rad(10)},
    {rad(0), rad(20), rad(0)},
}
local cfgWaterPlaceAboveByLayer = {
    {
        {rad(0), rad(55), rad(20)},
        {rad(0), rad(50), rad(30)},
        {rad(0), rad(45), rad(40)},
    },
    {
        {rad(0), rad(45), rad(10)},
        {rad(0), rad(35), rad(15)},
        {rad(0), rad(30), rad(20)},
    },
    {
        {rad(0), rad(35), rad(-5)},
        {rad(0), rad(25), rad(0)},
        {rad(0), rad(20), rad(0)},
    },
    {
        {rad(0), rad(35), rad(-20)},
        {rad(0), rad(25), rad(-15)},
        {rad(0), rad(10), rad(-15)},
    },
}
local cfgWaterPlaceDownByLayer = {
    {
        {rad(0), rad(60), rad(20)},
        {rad(0), rad(55), rad(30)},
        {rad(0), rad(50), rad(40)},
    },
    {
        {rad(0), rad(50), rad(10)},
        {rad(0), rad(40), rad(20)},
        {rad(0), rad(35), rad(25)},
    },
    {
        {rad(0), rad(40), rad(0)},
        {rad(0), rad(30), rad(5)},
        {rad(0), rad(20), rad(10)},
    },
    {
        {rad(0), rad(35), rad(-15)},
        {rad(0), rad(25), rad(-10)},
        {rad(0), rad(10), rad(-10)},
    },
}

local curveColors = {
    {230, 57, 70},
    {29, 53, 87},
    {42, 157, 143},
    {244, 162, 97},
}

local function startsWith(text, prefix)
    return string.sub(text, 1, string.len(prefix)) == prefix
end

local function setCycleState(phase, layer, item)
    sim.setBufferProperty(
        sim.getObject(modelPath),
        'customData.palletizingCycle',
        sim.packTable({
            phase = phase,
            layer = layer or 0,
            item = item or '',
            cycle = cycleIndex,
            carrying = activeLoad ~= -1,
        })
    )
end

local function shouldRunInfiniteCycle()
    local ok, value = pcall(sim.getInt32Signal, infiniteCycleSignal)
    if ok and value ~= nil then
        return value >= 0
    end
    return infiniteCycleDefault
end

local function setConveyorVelocity(path, velocity)
    local ok, handle = pcall(sim.getObject, path)
    if ok and handle ~= -1 then
        sim.setBufferProperty(handle, 'customData.__ctrl__', sim.packTable({vel = velocity}))
    end
end

local function stopConveyors()
    setConveyorVelocity('/conveyor_bottles', 0.0)
    setConveyorVelocity('/conveyor_pallet', 0.0)
end

local function localSize(handle)
    local minX = sim.getObjectFloatParam(handle, sim.objfloatparam_objbbox_min_x)
    local maxX = sim.getObjectFloatParam(handle, sim.objfloatparam_objbbox_max_x)
    local minY = sim.getObjectFloatParam(handle, sim.objfloatparam_objbbox_min_y)
    local maxY = sim.getObjectFloatParam(handle, sim.objfloatparam_objbbox_max_y)
    local minZ = sim.getObjectFloatParam(handle, sim.objfloatparam_objbbox_min_z)
    local maxZ = sim.getObjectFloatParam(handle, sim.objfloatparam_objbbox_max_z)
    return {maxX - minX, maxY - minY, maxZ - minZ}
end

local function worldAabb(handle)
    local minX = sim.getObjectFloatParam(handle, sim.objfloatparam_objbbox_min_x)
    local maxX = sim.getObjectFloatParam(handle, sim.objfloatparam_objbbox_max_x)
    local minY = sim.getObjectFloatParam(handle, sim.objfloatparam_objbbox_min_y)
    local maxY = sim.getObjectFloatParam(handle, sim.objfloatparam_objbbox_max_y)
    local minZ = sim.getObjectFloatParam(handle, sim.objfloatparam_objbbox_min_z)
    local maxZ = sim.getObjectFloatParam(handle, sim.objfloatparam_objbbox_max_z)
    local m = sim.getObjectMatrix(handle, sim.handle_world)
    local outMin = {math.huge, math.huge, math.huge}
    local outMax = {-math.huge, -math.huge, -math.huge}
    for _, x in ipairs({minX, maxX}) do
        for _, y in ipairs({minY, maxY}) do
            for _, z in ipairs({minZ, maxZ}) do
                local p = {
                    m[1] * x + m[2] * y + m[3] * z + m[4],
                    m[5] * x + m[6] * y + m[7] * z + m[8],
                    m[9] * x + m[10] * y + m[11] * z + m[12],
                }
                for i = 1, 3 do
                    if p[i] < outMin[i] then outMin[i] = p[i] end
                    if p[i] > outMax[i] then outMax[i] = p[i] end
                end
            end
        end
    end
    return outMin, outMax, {outMax[1] - outMin[1], outMax[2] - outMin[2], outMax[3] - outMin[3]}
end

local function normalizedQuaternion(q)
    local len = math.sqrt(q[1] * q[1] + q[2] * q[2] + q[3] * q[3] + q[4] * q[4])
    if len < 1e-9 then
        return {0.0, 0.0, 0.0, 1.0}
    end
    return {q[1] / len, q[2] / len, q[3] / len, q[4] / len}
end

local function interpolatePose(fromPose, toPose, k)
    local pose = {
        fromPose[1] * (1.0 - k) + toPose[1] * k,
        fromPose[2] * (1.0 - k) + toPose[2] * k,
        fromPose[3] * (1.0 - k) + toPose[3] * k,
        0.0,
        0.0,
        0.0,
        1.0,
    }
    local qa = {fromPose[4], fromPose[5], fromPose[6], fromPose[7]}
    local qb = {toPose[4], toPose[5], toPose[6], toPose[7]}
    local dot = qa[1] * qb[1] + qa[2] * qb[2] + qa[3] * qb[3] + qa[4] * qb[4]
    if dot < 0.0 then
        qb = {-qb[1], -qb[2], -qb[3], -qb[4]}
    end
    local q = normalizedQuaternion({
        qa[1] * (1.0 - k) + qb[1] * k,
        qa[2] * (1.0 - k) + qb[2] * k,
        qa[3] * (1.0 - k) + qb[3] * k,
        qa[4] * (1.0 - k) + qb[4] * k,
    })
    pose[4], pose[5], pose[6], pose[7] = q[1], q[2], q[3], q[4]
    return pose
end

local function remember(handle)
    generatedObjects[#generatedObjects + 1] = handle
    return handle
end

local function removeOldGenerated()
    local objects = sim.getObjectsInTree(sim.handle_scene, sim.handle_all, 0)
    local toRemove = {}
    for i = 1, #objects do
        local alias = sim.getObjectAlias(objects[i], 1)
        if startsWith(alias, 'cycle_') then
            toRemove[#toRemove + 1] = objects[i]
        end
    end
    if #toRemove > 0 then
        sim.removeObjects(toRemove)
    end
end

local function shapeHandlesInTree(handle)
    local shapes = {}
    local seen = {}
    local objects = {handle}
    local okTree, tree = pcall(sim.getObjectsInTree, handle, sim.handle_all, 0)
    if okTree and tree then
        for i = 1, #tree do
            if tree[i] ~= handle then
                objects[#objects + 1] = tree[i]
            end
        end
    end
    for i = 1, #objects do
        local object = objects[i]
        if not seen[object] and sim.getObjectType(object) == sim.sceneobject_shape then
            seen[object] = true
            shapes[#shapes + 1] = object
        end
    end
    return shapes
end

local function setStaticRespondable(handle, isStatic)
    local shapes = shapeHandlesInTree(handle)
    for i = 1, #shapes do
        local object = shapes[i]
        pcall(sim.setObjectInt32Param, object, sim.shapeintparam_static, isStatic and 1 or 0)
        pcall(sim.setObjectInt32Param, object, sim.shapeintparam_respondable, payloadRespondable and 1 or 0)
        pcall(sim.resetDynamicObject, object)
    end
end

local function setMass(handle, mass)
    local shapes = shapeHandlesInTree(handle)
    if #shapes == 0 then return end
    local perShapeMass = mass / #shapes
    for i = 1, #shapes do
        pcall(sim.setShapeMass, shapes[i], perShapeMass)
    end
end

local function cloneTemplate(templateKey, alias, mass)
    local template = templates[templateKey]
    local object = sim.copyPasteObjects({template}, 2 | 4 | 8 | 16 | 32)[1]
    sim.setObjectAlias(object, alias)
    sim.setObjectParent(object, -1, true)
    sim.setObjectPose(object, templatePoses[templateKey], sim.handle_world)
    sim.setObjectInt32Param(object, sim.objintparam_visibility_layer, 1)
    setStaticRespondable(object, true)
    setMass(object, mass)
    return remember(object)
end

local function restoreTemplateVisibility()
    for key, handle in pairs(templates) do
        if templateVisibility[key] then
            sim.setObjectInt32Param(handle, sim.objintparam_visibility_layer, templateVisibility[key])
        end
    end
end

local function hideTemplates()
    for key, handle in pairs(templates) do
        templateVisibility[key] = sim.getObjectInt32Param(handle, sim.objintparam_visibility_layer)
        setStaticRespondable(handle, true)
        sim.setObjectInt32Param(handle, sim.objintparam_visibility_layer, 0)
    end
end

local function moveObjectLinear(handle, fromPose, toPose, duration, conveyorPath, conveyorVelocity)
    if conveyorPath then
        setConveyorVelocity(conveyorPath, conveyorVelocity or 0.12)
    end
    sim.setObjectPose(handle, fromPose, sim.handle_world)
    local t = 0.0
    while t < duration and not sim.getSimulationStopping() do
        local dt = sim.getSimulationTimeStep()
        t = math.min(duration, t + dt)
        local k = t / duration
        local pose = interpolatePose(fromPose, toPose, k)
        sim.setObjectPose(handle, pose, sim.handle_world)
        sim.wait(dt)
    end
    sim.setObjectPose(handle, toPose, sim.handle_world)
    if conveyorPath then
        setConveyorVelocity(conveyorPath, 0.0)
    end
end

local function alignAttachDummyToTool()
    sim.setObjectParent(attachDummy, gripper, true)
    sim.setObjectPose(attachDummy, sim.getObjectPose(gripper, sim.handle_world), sim.handle_world)
    sim.setObjectPosition(attachDummy, sim.handle_parent, {0.0, 0.0, 0.0})
    sim.setObjectOrientation(attachDummy, sim.handle_parent, {0.0, 0.0, 0.0})
end

local function moveObjectToGripContact(handle, duration)
    local objMin, objMax, objSize = worldAabb(handle)
    local gripMin, gripMax = worldAabb(gripper)
    local pose = sim.getObjectPose(handle, sim.handle_world)
    local gripPose = sim.getObjectPose(gripper, sim.handle_world)
    local target = copyPose(pose)
    target[1] = gripPose[1]
    target[2] = gripPose[2]
    target[3] = gripMin[3] - objSize[3] * 0.5 + gripContactClearance
    if target[3] < pose[3] - 0.15 then
        target[3] = pose[3]
    end
    if target[3] > gripMax[3] then
        target[3] = gripMax[3] - objSize[3] * 0.5
    end
    moveObjectLinear(handle, pose, target, duration or 0.12, nil, 0.0)
end

local function attachLoad(handle, carryLocalPosition)
    alignAttachDummyToTool()
    activeLoad = handle
    sim.setObjectParent(activeLoad, attachDummy, true)
    if carryLocalPosition then
        sim.setObjectPosition(activeLoad, attachDummy, carryLocalPosition)
    end
    setStaticRespondable(activeLoad, true)
    sim.resetDynamicObject(activeLoad)
end

local function releaseLoad(handle, worldPose)
    local carriedPose = sim.getObjectPose(handle, sim.handle_world)
    local snapDistance = poseDistance(carriedPose, worldPose)
    if snapDistance > releaseSnapTolerance and not allowLargeReleaseCorrection then
        local warning = string.format(
            'Palletizing cycle: release blocked; payload is %.3f m from the planned stack pose. Tune the robot/path/scene instead of correcting by teleport.',
            snapDistance
        )
        pcall(sim.setStringSignal, ikWarningSignal, warning)
        sim.addLog(sim.verbosity_warnings, warning)
        return false
    end
    sim.setObjectParent(handle, -1, true)
    setStaticRespondable(handle, true)
    if snapDistance > releaseSnapTolerance then
        sim.addLog(
            sim.verbosity_warnings,
            string.format(
                'Palletizing cycle: release correction is %.3f m. Smoothing payload correction to the planned stack pose.',
                snapDistance
            )
        )
    end
    if snapDistance > 0.02 then
        local duration = math.max(
            releaseCorrectionMinDuration,
            math.min(releaseCorrectionMaxDuration, snapDistance / releaseCorrectionSpeed)
        )
        moveObjectLinear(handle, carriedPose, worldPose, duration, nil, 0.0)
    else
        sim.setObjectPose(handle, worldPose, sim.handle_world)
    end
    sim.wait(0.03)
    if pallet ~= -1 then
        sim.setObjectParent(handle, pallet, true)
    else
        sim.setObjectParent(handle, -1, true)
    end
    placedObjects[#placedObjects + 1] = handle
    activeLoad = -1
    return true
end

local function objectExists(handle)
    if handle == -1 then return false end
    local ok = pcall(sim.getObjectAlias, handle, 1)
    return ok
end

local function basename(path)
    return string.match(path, '[^/]+$') or path
end

local function mergeMap(dst, src)
    if not src then return end
    for key, value in pairs(src) do
        dst[key] = value
    end
end

local function loopPairs()
    if not simIK then return {} end
    return {
        {modelPath .. '/dummy1A', modelPath .. '/dummy1B', simIK.constraint_x + simIK.constraint_z},
        {modelPath .. '/dummy2A', modelPath .. '/dummy2B', simIK.constraint_x + simIK.constraint_z},
        {modelPath .. '/dummy3A', modelPath .. '/dummy3B', simIK.constraint_position},
        {modelPath .. '/dummy4B', modelPath .. '/dummy4A', simIK.constraint_x + simIK.constraint_z},
    }
end

local function loopClosureError()
    local maxError = 0.0
    local pairs = loopPairs()
    for i = 1, #pairs do
        local a = sim.getObject(pairs[i][1])
        local b = sim.getObject(pairs[i][2])
        local error = poseDistance(
            sim.getObjectPosition(a, sim.handle_world),
            sim.getObjectPosition(b, sim.handle_world)
        )
        if error > maxError then
            maxError = error
        end
    end
    return maxError
end

local function configureSceneDummyLinks()
    local pairs = loopPairs()
    for i = 1, #pairs do
        local a = sim.getObject(pairs[i][1])
        local b = sim.getObject(pairs[i][2])
        pcall(sim.setObjectInt32Param, a, sim.dummyintparam_link_type, sim.dummy_linktype_gcs_loop_closure)
        pcall(sim.setObjectInt32Param, b, sim.dummyintparam_link_type, sim.dummy_linktype_gcs_loop_closure)
        pcall(sim.setLinkDummy, a, b)
    end
end

local function findOrCreateDummy(alias, size)
    local ok, handle = pcall(sim.getObject, modelPath .. '/' .. alias)
    if not ok or handle == -1 then
        ok, handle = pcall(sim.getObject, '/' .. alias)
    end
    if not ok or handle == -1 then
        handle = sim.createDummy(size)
        sim.setObjectAlias(handle, alias)
    end
    sim.setObjectInt32Param(handle, sim.objintparam_visibility_layer, 0)
    return handle
end

local function ensurePoseIkDummies()
    if not objectExists(ikTip) then
        ikTip = findOrCreateDummy('cycleIkTip', 0.018)
    end
    if not objectExists(ikTarget) then
        ikTarget = findOrCreateDummy('cycleIkTarget', 0.026)
    end

    sim.setObjectParent(ikTip, gripper, true)
    sim.setObjectPosition(ikTip, sim.handle_parent, tcpLocalOffset)
    sim.setObjectOrientation(ikTip, sim.handle_parent, {0.0, 0.0, 0.0})

    sim.setObjectParent(ikTarget, -1, true)
    sim.setObjectPose(ikTarget, sim.getObjectPose(gripper, sim.handle_world))
end

local function destroyClosedChainIk()
    if closedIkEnv then
        pcall(simIK.eraseEnvironment, closedIkEnv)
        closedIkEnv = nil
        closedIkGroup = nil
        closedIkGroupFallback = nil
        closedIkJoints = {}
        closedIkToSimMap = {}
        closedIkTarget = nil
    end
end

local function simJointForIkJoint(ikJoint)
    return closedIkToSimMap[ikJoint] or closedIkToSimMap[tostring(ikJoint)]
end

local function configureIkJointsForGroup(group, keepAsPrimary)
    local joints = simIK.getGroupJoints(closedIkEnv, group)
    if keepAsPrimary then
        closedIkJoints = joints
    end
    for i = 1, #joints do
        local ikJoint = joints[i]
        local simJoint = simJointForIkJoint(ikJoint)
        simIK.setJointMode(closedIkEnv, ikJoint, simIK.jointmode_ik)
        simIK.setJointWeight(closedIkEnv, ikJoint, 1.0)
        if simJoint and sim.getJointType(simJoint) == sim.joint_prismatic then
            simIK.setJointMaxStepSize(closedIkEnv, ikJoint, 0.02)
        else
            simIK.setJointMaxStepSize(closedIkEnv, ikJoint, math.rad(6.0))
        end
    end
end

local function configureClosedIkJoints()
    configureIkJointsForGroup(closedIkGroup, true)
    if closedIkGroupFallback then
        configureIkJointsForGroup(closedIkGroupFallback, false)
    end
end

local function setClosedIkGroupDefaults(group)
    simIK.setGroupCalculation(
        closedIkEnv,
        group,
        simIK.method_damped_least_squares,
        0.08,
        50
    )
    local flags = simIK.getGroupFlags(closedIkEnv, group)
    pcall(
        simIK.setGroupFlags,
        closedIkEnv,
        group,
        flags | simIK.group_restoreonbadlintol | simIK.group_restoreonbadangtol
    )
end

local function addLoopElementsToGroup(group)
    local pairs = loopPairs()
    for i = 1, #pairs do
        local loopElement
        local simToIkMap
        local localIkToSimMap
        loopElement, simToIkMap, localIkToSimMap = simIK.addElementFromScene(
            closedIkEnv,
            group,
            sim.getObject(modelPath),
            sim.getObject(pairs[i][1]),
            sim.getObject(pairs[i][2]),
            pairs[i][3]
        )
        mergeMap(closedIkToSimMap, localIkToSimMap)
        simIK.setElementWeights(closedIkEnv, group, loopElement, {1.0, 0.0})
        simIK.setElementPrecision(closedIkEnv, group, loopElement, {0.001, math.rad(1)})
    end
end

local function buildClosedChainIk()
    if not simIK then return false end
    destroyClosedChainIk()
    ensurePoseIkDummies()

    closedIkEnv = simIK.createEnvironment()
    closedIkGroup = simIK.createGroup(closedIkEnv)
    setClosedIkGroupDefaults(closedIkGroup)

    local element
    local simToIkMap
    local localIkToSimMap
    element, simToIkMap, localIkToSimMap = simIK.addElementFromScene(
        closedIkEnv,
        closedIkGroup,
        sim.getObject(modelPath),
        ikTip,
        ikTarget,
        simIK.constraint_position
    )
    mergeMap(closedIkToSimMap, localIkToSimMap)
    closedIkTarget = simToIkMap[ikTarget] or simToIkMap[tostring(ikTarget)]
    simIK.setElementWeights(closedIkEnv, closedIkGroup, element, {1.0, 0.0})
    simIK.setElementPrecision(closedIkEnv, closedIkGroup, element, {0.001, math.rad(1)})

    addLoopElementsToGroup(closedIkGroup)

    -- Official parallel-mechanism example 7 uses a fallback group that only
    -- preserves loop closure when the useful target cannot be reached.
    closedIkGroupFallback = simIK.createGroup(closedIkEnv)
    setClosedIkGroupDefaults(closedIkGroupFallback)
    addLoopElementsToGroup(closedIkGroupFallback)

    configureClosedIkJoints()
    return true
end

local function ensureClosedChainIk()
    if not simIK then return false end
    if not closedIkEnv then
        return buildClosedChainIk()
    end
    return true
end

local function setClosedIkTargetPose(pose)
    local ok = pcall(sim.setObjectPose, ikTarget, pose)
    if not ok then
        pcall(sim.setObjectPose, ikTarget, sim.handle_world, pose)
    end
    pcall(sim.setObjectPosition, ikTarget, sim.handle_world, {pose[1], pose[2], pose[3]})
    pcall(sim.setObjectQuaternion, ikTarget, sim.handle_world, {pose[4], pose[5], pose[6], pose[7]})
    if closedIkEnv and closedIkTarget then
        ok = pcall(simIK.setObjectPose, closedIkEnv, closedIkTarget, -1, pose)
        if not ok then
            pcall(simIK.setObjectPose, closedIkEnv, closedIkTarget, pose)
        end
    end
end

local function makeIkParams()
    local ikParams = {
        tip = ikTip,
        target = ikTarget,
        base = sim.getObject(modelPath),
        joints = motionMotors,
        allowError = true,
        damping = 0.08,
        iterations = 90,
    }
    if simIK and simIK.constraint_position then
        ikParams.constraints = simIK.constraint_position
    end
    return ikParams
end

local function stepPoseToward(currentPose, targetPose, maxStep)
    local dx = targetPose[1] - currentPose[1]
    local dy = targetPose[2] - currentPose[2]
    local dz = targetPose[3] - currentPose[3]
    local distanceToTarget = math.sqrt(dx * dx + dy * dy + dz * dz)
    local out = copyPose(targetPose)
    if distanceToTarget > maxStep then
        local scale = maxStep / distanceToTarget
        out[1] = currentPose[1] + dx * scale
        out[2] = currentPose[2] + dy * scale
        out[3] = currentPose[3] + dz * scale
    end
    return out, distanceToTarget
end

local syncClosedIkConfigToSim

local function closedIkGroupList()
    local groups = {}
    if closedIkGroup then groups[#groups + 1] = closedIkGroup end
    if closedIkGroupFallback then groups[#groups + 1] = closedIkGroupFallback end
    return groups
end

local function ikHandleOptions(allowError)
    local options = {syncWorlds = true, allowError = allowError}
    local ok, debugValue = pcall(sim.getInt32Signal, ikDebugSignal)
    if ok and debugValue and debugValue > 0 then
        options.debug = debugValue
    end
    return options
end

local function handleClosedIkFallback(iterations)
    if not closedIkGroupFallback then return nil, nil, nil end
    local result, flags, precision
    for i = 1, iterations do
        result, flags, precision = simIK.handleGroup(
            closedIkEnv,
            closedIkGroupFallback,
            ikHandleOptions(true)
        )
    end
    return result, flags, precision
end

local function handleClosedIk(iterations)
    local result, flags, precision
    local fallbackUsed = false
    for i = 1, iterations do
        result, flags, precision = simIK.handleGroup(
            closedIkEnv,
            closedIkGroup,
            ikHandleOptions(true)
        )
        if result ~= simIK.result_success or loopClosureError() > maxLoopClosureError then
            local fallbackResult, fallbackFlags, fallbackPrecision = handleClosedIkFallback(1)
            fallbackUsed = true
            if fallbackResult then
                result, flags, precision = fallbackResult, fallbackFlags, fallbackPrecision
            end
        end
    end
    return result, flags, precision, fallbackUsed
end

local function getClosedIkConfig()
    if not ensureClosedChainIk() then return {} end
    pcall(simIK.syncFromSim, closedIkEnv, closedIkGroupList())
    local config = {}
    for i = 1, #closedIkJoints do
        local ok, value = pcall(simIK.getJointPosition, closedIkEnv, closedIkJoints[i])
        config[i] = ok and value or 0.0
    end
    return config
end

local function setClosedIkConfig(config)
    for i = 1, math.min(#closedIkJoints, #config) do
        pcall(simIK.setJointPosition, closedIkEnv, closedIkJoints[i], config[i])
    end
end

function syncClosedIkConfigToSim()
    local ok = pcall(simIK.syncToSim, closedIkEnv, {closedIkGroup})
    if ok then return end
    for i = 1, #closedIkJoints do
        local simJoint = simJointForIkJoint(closedIkJoints[i])
        if simJoint then
            local posOk, value = pcall(simIK.getJointPosition, closedIkEnv, closedIkJoints[i])
            if posOk then
                pcall(sim.setJointPosition, simJoint, value)
            end
        end
    end
end

local function isMotionMotor(simJoint)
    for i = 1, #motionMotors do
        if motionMotors[i] == simJoint then return true end
    end
    return false
end

local function configDistanceScore(config, reference)
    local score = 0.0
    for i = 1, math.min(#config, #reference) do
        local simJoint = simJointForIkJoint(closedIkJoints[i])
        local weight = (simJoint and isMotionMotor(simJoint)) and 3.0 or 0.35
        local d = config[i] - reference[i]
        score = score + weight * d * d
    end
    return score
end

local function normalizeConfigList(configs)
    if type(configs) ~= 'table' or #configs == 0 then return {} end
    if type(configs[1]) == 'number' then
        return {configs}
    end
    return configs
end

local function selectNearestClosedIkConfig(configs)
    local current = getClosedIkConfig()
    local bestConfig = nil
    local bestScore = math.huge
    for i = 1, #configs do
        local candidate = configs[i]
        if type(candidate) == 'table' and #candidate == #closedIkJoints then
            local score = configDistanceScore(candidate, current)
            if score < bestScore then
                bestScore = score
                bestConfig = candidate
            end
        end
    end
    return bestConfig
end

local function findClosedChainGoalConfig(toolPose)
    if not ensureClosedChainIk() then return nil, 0 end
    setClosedIkTargetPose(toolPose)
    pcall(simIK.syncFromSim, closedIkEnv, closedIkGroupList())
    setClosedIkTargetPose(toolPose)

    local params = {
        maxDist = goalConfigSearchMaxDist,
        maxTime = goalConfigSearchTime,
        findMultiple = true,
        cMetric = {},
    }
    for i = 1, #closedIkJoints do
        local simJoint = simJointForIkJoint(closedIkJoints[i])
        params.cMetric[i] = (simJoint and isMotionMotor(simJoint)) and 2.0 or 0.35
    end

    local ok, configs = pcall(simIK.findConfigs, closedIkEnv, closedIkGroup, closedIkJoints, params)
    if not ok then
        sim.addLog(sim.verbosity_warnings, 'Palletizing cycle: simIK.findConfigs failed: ' .. tostring(configs))
        return nil, 0
    end

    configs = normalizeConfigList(configs)
    return selectNearestClosedIkConfig(configs), #configs
end

local function moveClosedChainNearConfig(config, phase, layer, item)
    if not config then return false end
    if phase then
        setCycleState(phase .. '_goal_config', layer, item)
    end

    local current = getClosedIkConfig()
    local maxDelta = 0.0
    for i = 1, math.min(#current, #config) do
        maxDelta = math.max(maxDelta, math.abs(config[i] - current[i]))
    end
    if maxDelta < 1e-5 then return true end

    local steps = math.ceil(maxDelta / goalConfigJointStep)
    steps = math.max(6, math.min(steps, 80))
    for step = 1, steps do
        if sim.getSimulationStopping() then return false end
        local alpha = step / steps
        local blended = {}
        for i = 1, #current do
            blended[i] = current[i] + (config[i] - current[i]) * alpha
        end
        setClosedIkConfig(blended)
        syncClosedIkConfigToSim()
        setClosedIkTargetPose(sim.getObjectPose(ikTip, sim.handle_world))
        pcall(simIK.syncFromSim, closedIkEnv, closedIkGroupList())
        setClosedIkTargetPose(sim.getObjectPose(ikTip, sim.handle_world))
        handleClosedIk(2)
        sim.wait(sim.getSimulationTimeStep())
    end
    return true
end

local function seedClosedChainForPose(toolPose, phase, layer, item)
    local config, count = findClosedChainGoalConfig(toolPose)
    if not config then
        sim.addLog(
            sim.verbosity_scriptinfos,
            string.format(
                'Palletizing cycle: no closed-chain goal config found for phase "%s"; continuing with local IK.',
                phase or 'unknown'
            )
        )
        return false
    end
    sim.addLog(
        sim.verbosity_scriptinfos,
        string.format(
            'Palletizing cycle: selected one of %d closed-chain goal configs for phase "%s".',
            count,
            phase or 'unknown'
        )
    )
    return moveClosedChainNearConfig(config, phase, layer, item)
end

local function moveToolToPoseClosedChain(toolPose, phase, layer, item)
    if not ensureClosedChainIk() then return nil end
    if phase then
        setCycleState(phase, layer, item)
    end

    -- Keep the simpleManipulatorPathPlanning-style goal-config search disabled
    -- in the live cycle for now: direct application of sampled configs can
    -- violate the imported robot's dummy-loop closure.
    -- seedClosedChainForPose(toolPose, phase, layer, item)
    pcall(simIK.syncFromSim, closedIkEnv, closedIkGroupList())
    setClosedIkTargetPose(sim.getObjectPose(ikTip, sim.handle_world))
    local elapsed = 0.0
    local timeout = closedIkTargetTimeout
    local result, flags, precision
    local fallbackUsed = false
    while not sim.getSimulationStopping() and elapsed < timeout do
        local currentTargetPose = sim.getObjectPose(ikTarget, sim.handle_world)
        local nextPose, remaining = stepPoseToward(currentTargetPose, toolPose, poseStepDistance)
        setClosedIkTargetPose(nextPose)
        pcall(simIK.syncFromSim, closedIkEnv, closedIkGroupList())
        setClosedIkTargetPose(nextPose)
        local usedFallback
        result, flags, precision, usedFallback = handleClosedIk(1)
        fallbackUsed = fallbackUsed or usedFallback

        local reachedPose = sim.getObjectPose(ikTip, sim.handle_world)
        local reachError = poseDistance(reachedPose, toolPose)
        local loopError = loopClosureError()
        if remaining <= poseStepDistance and reachError <= poseReachTolerance and loopError <= maxLoopClosureError then
            return true
        end

        local dt = sim.getSimulationTimeStep()
        elapsed = elapsed + dt
        sim.wait(dt)
    end

    local reachedPose = sim.getObjectPose(ikTip, sim.handle_world)
    local reachError = poseDistance(reachedPose, toolPose)
    local loopError = loopClosureError()
    local reached = reachError <= poseReachTolerance and loopError <= maxLoopClosureError
    if not reached then
        local fallbackResult = handleClosedIkFallback(4)
        fallbackUsed = fallbackUsed or (fallbackResult ~= nil)
        reachedPose = sim.getObjectPose(ikTip, sim.handle_world)
        reachError = poseDistance(reachedPose, toolPose)
        loopError = loopClosureError()
        reached = reachError <= poseReachTolerance and loopError <= maxLoopClosureError
        local warning = string.format(
            'Palletizing cycle: target_unreachable in phase "%s"; TCP error %.3f m, loop error %.3f m, fallback=%s.',
            phase or 'unknown',
            reachError,
            loopError,
            tostring(fallbackUsed)
        )
        pcall(sim.setStringSignal, ikWarningSignal, warning)
        sim.addLog(sim.verbosity_warnings, warning)
    end
    return reached
end

local function moveToolToPoseSimple(toolPose, phase, layer, item)
    ensurePoseIkDummies()
    if phase then
        setCycleState(phase, layer, item)
    end
    setClosedIkTargetPose(toolPose)
    local ikParams = makeIkParams()
    local motion = {
        ik = ikParams,
        targetPose = toolPose,
        maxVel = poseMaxVel,
        maxAccel = poseMaxAccel,
        maxJerk = poseMaxJerk,
    }
    local ok, err = pcall(sim.moveToPose, motion)
    if not ok and ikParams.constraints then
        ikParams.constraints = nil
        ok, err = pcall(sim.moveToPose, motion)
    end
    if not ok then
        sim.addLog(
            sim.verbosity_errors,
            string.format('Palletizing cycle: simple pose IK move failed in phase "%s": %s', phase or 'unknown', tostring(err))
        )
        return false
    end
    return true
end

local function moveToolToPose(toolPose, phase, layer, item)
    if simIK then
        local closedOk = moveToolToPoseClosedChain(toolPose, phase, layer, item)
        if closedOk ~= nil then
            return closedOk
        end
    end
    return moveToolToPoseSimple(toolPose, phase, layer, item)
end

local function moveToolToPoseBestEffort(toolPose, phase, layer, item)
    local ok = moveToolToPose(toolPose, phase, layer, item)
    if not ok then
        sim.addLog(
            sim.verbosity_scriptinfos,
            string.format(
                'Palletizing cycle: continuing after best-effort phase "%s"; strict checks remain enabled for pick/place/release.',
                phase or 'unknown'
            )
        )
    end
    return true
end

local function repairClosedChain()
    if not ensureClosedChainIk() then return end
    pcall(simIK.syncFromSim, closedIkEnv, closedIkGroupList())
    setClosedIkTargetPose(sim.getObjectPose(ikTip, sim.handle_world))
    handleClosedIk(12)
end

local function moveToConfig(config)
    sim.moveToConfig({
        joints = motionMotors,
        targetPos = config,
        maxVel = maxVel,
        maxAccel = maxAccel,
        maxJerk = maxJerk,
        flags = -1,
    })
    repairClosedChain()
end

local function pickAndPlace(handle, pickAbove, pickDown, placeAbove, placeDown, placePose, layer, item, carryLocalPosition)
    setCycleState('lift_before_pick', layer, item)
    moveToConfig(pickAbove)
    setCycleState('pick', layer, item)
    moveToConfig(pickDown)
    setCycleState('grip_contact', layer, item)
    sim.wait(gripSettleWait)
    attachLoad(handle, carryLocalPosition)
    sim.wait(gripSettleWait)
    setCycleState('lift_with_load', layer, item)
    moveToConfig(pickAbove)
    setCycleState('move_to_pallet', layer, item)
    moveToConfig(cfgTransfer)
    moveToConfig(placeAbove)
    setCycleState('place', layer, item)
    moveToConfig(placeDown)
    if not releaseLoad(handle, placePose) then
        return false
    end
    sim.wait(releaseSettleWait)
    moveToConfig(placeAbove)
    return true
end

local function pickAndPlaceByPose(
    handle,
    pickPose,
    placePose,
    height,
    layer,
    item,
    pickSeedConfig,
    pickDownSeedConfig,
    placeSeedConfig,
    placeDownSeedConfig
)
    local pickToolPose = loadPoseToToolPose(pickPose, height)
    local placeToolPose = loadPoseToToolPose(placePose, height)

    if pickSeedConfig then
        moveToConfig(pickSeedConfig)
    end
    if not moveToolToPoseBestEffort(poseWithDz(pickToolPose, poseApproachLift), 'lift_before_pick', layer, item) then
        return false
    end
    -- Keep the exact down motion pose-driven; the old down CFGs can pull the
    -- imported closed-chain robot away from the approach pose.
    if not moveToolToPose(pickToolPose, 'pick', layer, item) then
        return false
    end

    setCycleState('grip_contact', layer, item)
    sim.wait(gripSettleWait)
    attachLoad(handle, carryOffsetForHeight(height))
    sim.wait(gripSettleWait)

    if not moveToolToPoseBestEffort(poseWithDz(pickToolPose, poseApproachLift), 'lift_with_load', layer, item) then
        return false
    end

    local transferPose = copyPose(placeToolPose)
    transferPose[1] = (pickToolPose[1] + placeToolPose[1]) * 0.5
    transferPose[2] = (pickToolPose[2] + placeToolPose[2]) * 0.5
    transferPose[3] = math.max(pickToolPose[3], placeToolPose[3]) + poseApproachLift + 0.18
    if not moveToolToPoseBestEffort(transferPose, 'move_to_pallet', layer, item) then
        return false
    end

    if usePlaceSeedConfigs and placeSeedConfig then
        moveToConfig(placeSeedConfig)
    end
    if not moveToolToPoseBestEffort(poseWithDz(placeToolPose, poseApproachLift), 'approach_place', layer, item) then
        return false
    end
    if not moveToolToPose(placeToolPose, 'place', layer, item) then
        return false
    end

    if not releaseLoad(handle, placePose) then
        return false
    end
    sim.wait(releaseSettleWait)
    return moveToolToPoseBestEffort(poseWithDz(placeToolPose, poseApproachLift), 'lift_after_place', layer, item)
end

local function shiftedPose(pose, dx, dy, dz)
    local out = {}
    for i = 1, #pose do out[i] = pose[i] end
    out[1] = out[1] + (dx or 0.0)
    out[2] = out[2] + (dy or 0.0)
    out[3] = out[3] + (dz or 0.0)
    return out
end

local function prepareGeometry()
    local palletPose = templatePoses.pallet
    palletStationPose = {palletPose[1], palletPose[2], palletPose[3], palletPose[4], palletPose[5], palletPose[6], palletPose[7]}
    if palletStationZOverride then
        palletStationPose[3] = palletStationZOverride
    end
    palletExitPose = shiftedPose(palletStationPose, 0.0, 1.25, 0.0)

    local _, _, palletSize = worldAabb(templates.pallet)
    local cardboardMin, cardboardMax, cardboardSize = worldAabb(templates.cardboard)
    local _, _, packSize = worldAabb(templates.water)

    palletTopZ = palletStationPose[3] + palletSize[3] * 0.5
    cardboardHeight = cardboardSize[3]
    waterBundleHeight = packSize[3]
    waterBundleSize = packSize

    stackCenter = {
        palletStationPose[1],
        palletStationPose[2],
        palletTopZ,
    }

    cardboardPickPose = copyPose(templatePoses.cardboard)
    cardboardGripPose = copyPose(cardboardPickPose)
    -- The center of the cardboard is too deep for the current closed-chain seed.
    -- Aim at the near edge first; the object itself still spawns at the original pose.
    cardboardGripPose[2] = cardboardMin[2] + cardboardGripEdgeInset
    waterPickPose = {
        templatePoses.water[1],
        templatePoses.water[2],
        templatePoses.water[3],
        templatePoses.water[4],
        templatePoses.water[5],
        templatePoses.water[6],
        templatePoses.water[7],
    }
    local okConveyor, bottleConveyor = pcall(sim.getObject, '/conveyor_bottles')
    if okConveyor and bottleConveyor ~= -1 then
        local conveyorPose = sim.getObjectPose(bottleConveyor, sim.handle_world)
        -- Keep the template height/orientation, but center generated bottles on
        -- the bottle conveyor width. The user's scene can still choose the
        -- longitudinal pickup point by moving the template along Y.
        waterPickPose[1] = conveyorPose[1]
        if math.abs(waterPickPose[2] - conveyorPose[2]) > 1.0 then
            waterPickPose[2] = conveyorPose[2]
        end
    end
end

local function placePoseAt(x, y, z, templateKey, yawCorrection)
    local basePose = templatePoses[templateKey]
    local corrected = poseWithYawCorrection(basePose, yawCorrection or 0.0)
    return {x, y, z, corrected[4], corrected[5], corrected[6], corrected[7]}
end

local function runOneCycle()
    placedObjects = {}
    activeLoad = -1
    pallet = -1

    pallet = cloneTemplate('pallet', 'cycle_loaded_pallet', palletMass)
    sim.setObjectPose(pallet, palletStationPose, sim.handle_world)
    setCycleState('pallet_arrived', 0, 'pallet')
    sim.wait(palletArrivalWait)

    moveToConfig(cfgHome)

    local layerPitch = cardboardHeight + waterBundleHeight
    local bundlePitch = 0.28
    if waterBundleSize then
        bundlePitch = math.max(0.26, math.min(0.34, waterBundleSize[1] * 0.98))
    end
    local bundleFarToNearOffsets = {bundlePitch, 0.0, -bundlePitch}
    for layer = 1, 4 do
        local cardboard = cloneTemplate('cardboard', string.format('cycle_cardboard_%02d', layer), cardboardMass)
        setCycleState('cardboard_generated', layer, 'cardboard')
        sim.setObjectPose(cardboard, cardboardPickPose, sim.handle_world)

        local cardZ = palletTopZ + (layer - 1) * layerPitch + cardboardHeight * 0.5
        local cardPose = placePoseAt(stackCenter[1], stackCenter[2], cardZ, 'cardboard', cardboardPlaceYaw)
        local cardboardOk
        if useUarmStyleConfigMotion then
            cardboardOk = pickAndPlace(
                cardboard,
                cfgCardboardAbove,
                cfgCardboardDown,
                cfgCardboardPlaceAbove[layer],
                cfgCardboardPlaceDown[layer],
                cardPose,
                layer,
                'cardboard',
                cardboardCarryLocalPosition
            )
        else
            cardboardOk = pickAndPlaceByPose(
                cardboard,
                cardboardGripPose,
                cardPose,
                cardboardHeight,
                layer,
                'cardboard',
                cfgCardboardAbove,
                cfgCardboardDown,
                cfgPalletAbove,
                cfgPalletDown
            )
        end
        if not cardboardOk then
            setCycleState('cycle_aborted', layer, 'cardboard_pose_ik_failed')
            return false
        end

        for bundleIndex = 1, 3 do
            local bundle = cloneTemplate(
                'water',
                string.format('cycle_water_bundle_%02d_%02d', layer, bundleIndex),
                waterBundleMass
            )
            setCycleState('water_bundle_generated', layer, string.format('water_bundle_%d', bundleIndex))
            sim.setObjectPose(bundle, waterPickPose, sim.handle_world)

            local packZ = palletTopZ + (layer - 1) * layerPitch + cardboardHeight + waterBundleHeight * 0.5
            local packPose = placePoseAt(
                stackCenter[1] + bundleFarToNearOffsets[bundleIndex],
                stackCenter[2],
                packZ,
                'water',
                waterPlaceYaw
            )
            local bundleItem = string.format('water_bundle_%d', bundleIndex)
            local bundleOk
            if useUarmStyleConfigMotion then
                bundleOk = pickAndPlace(
                    bundle,
                    cfgBottleAbove,
                    cfgBottleDown,
                    cfgWaterPlaceAboveByLayer[layer][bundleIndex],
                    cfgWaterPlaceDownByLayer[layer][bundleIndex],
                    packPose,
                    layer,
                    bundleItem,
                    waterCarryLocalPosition
                )
            else
                bundleOk = pickAndPlaceByPose(
                    bundle,
                    waterPickPose,
                    packPose,
                    waterBundleHeight,
                    layer,
                    bundleItem,
                    cfgBottleAbove,
                    cfgBottleDown,
                    cfgPalletAbove,
                    cfgPalletDown
                )
            end
            if not bundleOk then
                setCycleState('cycle_aborted', layer, string.format('water_bundle_%d_pose_ik_failed', bundleIndex))
                return false
            end
        end

        setCycleState('return_home_between_layers', layer, '')
        moveToConfig(cfgHome)
    end

    setCycleState('return_home', 4, '')
    moveToConfig(cfgHome)

    setCycleState('pallet_outfeed', 4, 'loaded_pallet')
    moveObjectLinear(pallet, palletStationPose, palletExitPose, outfeedDuration, '/conveyor_pallet', outfeedVelocity)
    setCycleState('pallet_removed', 4, 'loaded_pallet')
    sim.wait(releaseSettleWait)
    setCycleState('cycle_complete', 4, '4_cardboards_12_water_bundles')
    sim.wait(cycleCompleteHold)

    local toRemove = {pallet}
    for i = 1, #placedObjects do
        toRemove[#toRemove + 1] = placedObjects[i]
    end
    pcall(sim.removeObjects, toRemove)
    pallet = -1
    activeLoad = -1
    placedObjects = {}
    return true
end

local function runCycle()
    local continueRunning = true
    while continueRunning and not sim.getSimulationStopping() do
        cycleIndex = cycleIndex + 1
        local ok = runOneCycle()
        if not ok then
            return
        end
        continueRunning = shouldRunInfiniteCycle()
        if continueRunning and not sim.getSimulationStopping() then
            sim.wait(cycleRestartWait)
        end
    end
end

local function createUi()
    local ok, module = pcall(require, 'simUI')
    if not ok then
        sim.addLog(sim.verbosity_warnings, 'Palletizing monitor: simUI is unavailable.')
        simUI = nil
        return
    end
    simUI = module
    if ui then
        pcall(simUI.destroy, ui)
        ui = nil
    end
    local xml = [[
        <ui title="Motor dynamics monitor" closeable="true" resizable="true" placement="relative" position="30,30" size="1050,860">
            <group layout="vbox" flat="true" margins="4,4,4,4" spacing="4">
                <plot id="1"/>
                <plot id="2"/>
                <plot id="3"/>
                <plot id="4"/>
            </group>
        </ui>
    ]]
    ui = simUI.create(xml)
    simUI.setPlotLabels(ui, 1, 'time [s]', 'moment [N*m]')
    simUI.setPlotLabels(ui, 2, 'time [s]', 'angle [deg]')
    simUI.setPlotLabels(ui, 3, 'time [s]', 'velocity [deg/s]')
    simUI.setPlotLabels(ui, 4, 'time [s]', 'acceleration [deg/s^2]')
    for plotId = 1, 4 do
        simUI.setLegendVisibility(ui, plotId, true)
    end
    for i = 1, #motorNames do
        for plotId = 1, 4 do
            simUI.addCurve(ui, plotId, simUI.curve_type.time, motorNames[i], curveColors[i], simUI.curve_style.line, {})
        end
    end
end

local function updateMotorGraphs()
    if not (simUI and ui) then return end
    local t = sim.getSimulationTime()
    if t - lastGraphTime < graphPeriod then return end
    local dt = math.max(t - lastGraphTime, sim.getSimulationTimeStep())
    lastGraphTime = t

    for i = 1, #motors do
        local pos = sim.getJointPosition(motors[i])
        local vel = 0.0
        local okVel, measuredVel = pcall(sim.getObjectFloatParam, motors[i], sim.jointfloatparam_velocity)
        if okVel and measuredVel then
            vel = measuredVel
        else
            vel = (pos - graphState[i].lastPos) / dt
        end
        local acc = (vel - graphState[i].lastVel) / dt
        graphState[i].lastPos = pos
        graphState[i].lastVel = vel

        local force = 0.0
        local okForce, measuredForce = pcall(sim.getJointForce, motors[i])
        if okForce and measuredForce then
            force = measuredForce
        end

        pcall(simUI.addCurveTimePoints, ui, 1, motorNames[i], {t}, {force})
        pcall(simUI.addCurveTimePoints, ui, 2, motorNames[i], {t}, {math.deg(pos)})
        pcall(simUI.addCurveTimePoints, ui, 3, motorNames[i], {t}, {math.deg(vel)})
        pcall(simUI.addCurveTimePoints, ui, 4, motorNames[i], {t}, {math.deg(acc)})
    end
    for plotId = 1, 4 do
        pcall(simUI.rescaleAxesAll, ui, plotId, true, true)
        pcall(simUI.replot, ui, plotId)
    end
end

function sysCall_init()
    removeOldGenerated()

    templates.water = sim.getObject('/packofbottle_respondable')
    templates.cardboard = sim.getObject('/Cartoon')
    templates.pallet = sim.getObject('/Pallet_bottles')

    templatePoses.water = sim.getObjectPose(templates.water, sim.handle_world)
    templatePoses.cardboard = sim.getObjectPose(templates.cardboard, sim.handle_world)
    templatePoses.pallet = sim.getObjectPose(templates.pallet, sim.handle_world)

    hideTemplates()
    prepareGeometry()

    gripper = sim.getObject(modelPath .. '/gripper_respondable')
    for i = 1, #motorNames do
        motors[i] = sim.getObject(modelPath .. '/' .. motorNames[i])
        graphState[i] = {lastPos = sim.getJointPosition(motors[i]), lastVel = 0.0}
    end
    for i = 1, #motionMotorNames do
        motionMotors[i] = sim.getObject(modelPath .. '/' .. motionMotorNames[i])
    end

    local ok, existingDummy = pcall(sim.getObject, modelPath .. '/cycleAttachDummy')
    if ok and existingDummy ~= -1 then
        attachDummy = existingDummy
    else
        attachDummy = sim.createDummy(0.02)
        sim.setObjectAlias(attachDummy, 'cycleAttachDummy')
    end
    sim.setObjectInt32Param(attachDummy, sim.objintparam_visibility_layer, 0)
    alignAttachDummyToTool()
    ensurePoseIkDummies()
    buildClosedChainIk()

    createUi()
    stopConveyors()
    setCycleState('ready', 0, '')
end

function sysCall_thread()
    local ok, calibrationMode = pcall(sim.getInt32Signal, calibrationModeSignal)
    if ok and calibrationMode and calibrationMode > 0 then
        setCycleState('calibration_idle', 0, '')
        while not sim.getSimulationStopping() do
            sim.wait(0.1)
        end
        return
    end
    runCycle()
    while not sim.getSimulationStopping() do
        sim.wait(0.1)
    end
end

function sysCall_sensing()
    updateMotorGraphs()
end

function sysCall_actuation()
end

function sysCall_cleanup()
    stopConveyors()
    restoreTemplateVisibility()
    destroyClosedChainIk()
    if simUI and ui then
        pcall(simUI.destroy, ui)
        ui = nil
    end
end
