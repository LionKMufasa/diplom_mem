sim=require'sim'
simIK=require'simIK'

function callback_ik(data)
    sim.setJointPosition(data.auxData, data.pos[1])
    simIK.handleGroup(ikEnv,ikGroup,{debug=1|2,syncWorlds=true})
end

moveToJointPositions=function(newPos,velF)
    if not velF then velF=1 end
    local accel=40*math.pi/180
    local jerk=20*math.pi/180
    local params = {
        joints = jointHandles,
        targetPos = newPos,
        maxVel = {velF*175*math.pi/180,velF*175*math.pi/180,velF*175*math.pi/180,velF*250*math.pi/180,velF*250*math.pi/180,velF*360*math.pi/180},
        maxAccel = table.rep(accel, 6),
        maxJerk = table.rep(jerk, 6),
    }
    sim.moveToConfig(params)
end

moveToAuxJointPosition=function(newPos,velF)
    if not velF then velF=1 end
    local vel=40*math.pi/180
    local accel=10*math.pi/180
    local jerk=30*math.pi/180
    sim.setObjectPosition(simTarget,{0,0,0},simTip)
    sim.setObjectOrientation(simTarget,{0,0,0},simTip)
    local params = {
        pos = {sim.getJointPosition(auxJoint)},
        targetPos = {newPos},
        maxVel = {vel*velF},
        maxAccel = {accel},
        maxJerk = {jerk},
        callback = callback_ik,
        auxData = auxJoint
    }
    sim.moveToConfig(params)
end

function sysCall_thread()
    -- Initialization:
    simBase=sim.getObject('..')
    simTip=sim.getObject('../IkTip')
    simTarget=sim.getObject('../IkTarget')
    
    ikEnv=simIK.createEnvironment()
    
    -- Prepare an ik group, using the convenience function 'simIK.addElementFromScene':

    ikGroup=simIK.createGroup(ikEnv)
    simIK.addElementFromScene(ikEnv,ikGroup,simBase,simTip,simTarget,simIK.constraint_pose)

    jointHandles={}
    for i=1,6,1 do
        jointHandles[i]=sim.getObject('../joint',{index=i-1})
    end
    auxJoint=sim.getObject('../auxJoint')

    -- Main loop:
    while true do

        moveToJointPositions({90*math.pi/180,-30*math.pi/180,60*math.pi/180,0*math.pi/180,60*math.pi/180,0*math.pi/180})

        sim.setObjectPosition(auxJoint,{0,1.5,0},simBase)
        sim.setJointPosition(auxJoint,0)
        sim.setObjectParent(simTarget,auxJoint,true)
        moveToAuxJointPosition(360*math.pi/180)


        moveToJointPositions({0*math.pi/180,-30*math.pi/180,60*math.pi/180,0*math.pi/180,60*math.pi/180,0*math.pi/180})

        sim.setObjectPosition(auxJoint,{1.5,0,0},simBase)
        sim.setJointPosition(auxJoint,0)
        sim.setObjectParent(simTarget,auxJoint,true)
        moveToAuxJointPosition(360*math.pi/180)


        moveToJointPositions({-90*math.pi/180,-30*math.pi/180,60*math.pi/180,0*math.pi/180,60*math.pi/180,0*math.pi/180})

        sim.setObjectPosition(auxJoint,{0,-1.5,0},simBase)
        sim.setJointPosition(auxJoint,0)
        sim.setObjectParent(simTarget,auxJoint,true)
        moveToAuxJointPosition(360*math.pi/180)

        moveToJointPositions({0*math.pi/180,0*math.pi/180,0*math.pi/180,0*math.pi/180,0*math.pi/180,0*math.pi/180})

    end
end

function sysCall_cleanup()
    simIK.eraseEnvironment(ikEnv)
end
