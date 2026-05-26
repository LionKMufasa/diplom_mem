sim=require'sim'

function initialize(maxVel,maxAccel,maxJerk,maxTorque)
    motorHandles={-1,-1,-1,-1}
    for i=1,4,1 do
        motorHandles[i]=sim.getObject('../motor'..i)
        sim.setJointTargetForce(motorHandles[i],maxTorque)
        local mvaj = sim.getFloatArrayProperty(motorHandles[i], 'maxVelAccelJerk')
        mvaj[1] = maxVel
        sim.setFloatArrayProperty(motorHandles[i], 'maxVelAccelJerk', mvaj)
    end
    auxMotor1=sim.getObject('../auxMotor1')
    auxMotor2=sim.getObject('../auxMotor2')

    maxVelVect={maxVel,maxVel,maxVel,maxVel}
    maxAccelVect={maxAccel,maxAccel,maxAccel,maxAccel}
    maxJerkVect={maxJerk,maxJerk,maxJerk,maxJerk}
end

function moveToPosition(newMotorPositions,synchronous,maxVel,maxAccel,maxJerk)
    local _maxVelVect={}
    local _maxAccelVect={}
    local _maxJerkVect={}
    if not maxVel then
        maxVel=maxVelVect[1]
    end
    if not maxAccel then
        maxAccel=maxAccelVect[1]
    end
    if not maxJerk then
        maxJerk=maxJerkVect[1]
    end
    for i=1,4,1 do
        _maxVelVect[i]=math.max(1*math.pi/180,math.min(maxVel,maxVelVect[i]))
        _maxAccelVect[i]=math.max(1*math.pi/180,math.min(maxAccel,maxAccelVect[i]))
        _maxJerkVect[i]=math.max(1*math.pi/180,math.min(maxJerk,maxJerkVect[i]))
    end
    local op=sim.ruckig_nosync
    if synchronous then
        op=-1
    end
    local params = {
        joints = motorHandles,
        targetPos = newMotorPositions,
        maxVel = _maxVelVect,
        maxAccel = _maxAccelVect,
        maxJerk = _maxJerkVect,
        flags = op,
    }
    sim.moveToConfig(params)
end

function enableSuctionCup(enable)
    if enable then
        sim.setStringProperty(gripperHandle, 'customData.activity', 'on')
    else
        sim.setStringProperty(gripperHandle, 'customData.activity','off')
    end
end

function sysCall_thread()
    modelBase=sim.getObject('..')
    gripperHandle=sim.getObject('../uarmVacuumGripper')
    pickupPart=sim.getObject('../pickupPart')
    sim.setObjectParent(pickupPart,-1,true)

    local maxVelocity=45*math.pi/180 -- rad/s
    local maxAcceleration=40*math.pi/180 -- rad/s^2
    local maxJerk=80*math.pi/180 -- rad/s^3
    local maxTorque=10 -- kg*m^2/s^2

    initialize(maxVelocity,maxAcceleration,maxJerk,maxTorque)

    while true do
        enableSuctionCup(false)
        -- Synchronous operation of the individual joints:
        moveToPosition({180*math.pi/180,59*math.pi/180,84*math.pi/180,180*math.pi/180},true)
        moveToPosition({180*math.pi/180,52.5*math.pi/180,84*math.pi/180,180*math.pi/180},true)
        enableSuctionCup(true)
        moveToPosition({180*math.pi/180,59*math.pi/180,84*math.pi/180,180*math.pi/180},true)
        moveToPosition({90*math.pi/180,104*math.pi/180,60*math.pi/180,90*math.pi/180},true)
        -- Asynchronous operation of the individual joints:
        moveToPosition({180*math.pi/180,59*math.pi/180,84*math.pi/180,180*math.pi/180},false)
        moveToPosition({180*math.pi/180,52.5*math.pi/180,84*math.pi/180,180*math.pi/180},true)
        enableSuctionCup(false)
        moveToPosition({180*math.pi/180,59*math.pi/180,84*math.pi/180,180*math.pi/180},true)
        moveToPosition({90*math.pi/180,104*math.pi/180,60*math.pi/180,90*math.pi/180},false)
    end
end

function sysCall_joint(inData)
    if inData.handle==auxMotor1 then
        local t2=-sim.getJointPosition(motorHandles[2])+104*math.pi/180
        local t3=sim.getJointPosition(motorHandles[3])-59.25*math.pi/180
        error=t3-t2-inData.pos
    end
    if inData.handle==auxMotor2 then
        local t3=sim.getJointPosition(motorHandles[3])-59.25*math.pi/180
        error=-t3-inData.pos
    end
    local ctrl=error*20
    
    local maxVelocity=ctrl
    if (maxVelocity>inData.maxVel) then
        maxVelocity=inData.maxVel
    end
    if (maxVelocity<-inData.maxVel) then
        maxVelocity=-inData.maxVel
    end
    local forceOrTorqueToApply=inData.maxForce

    local outData={}
    outData.vel=maxVelocity
    outData.force=forceOrTorqueToApply
    return outData
end