function sysCall_init()
    sim = require('sim')
    sim.setStepping(true)
end

function moveToConfig(handles, maxVel, maxAccel, maxJerk, targetConf)
    local params = {
        joints = handles,
        targetPos = targetConf,
        maxVel = maxVel,
        maxAccel = maxAccel,
        maxJerk = maxJerk,
    }
    sim.moveToConfig(params)
end

function sysCall_thread()
    local jointHandles = {}
    for i = 1, 7 do
        jointHandles[i] = sim.getObject('../joint', {index = i - 1})
    end

    local vel = 110  
    local accel = 40
    local jerk = 80
    local maxVel = {vel*math.pi/180,vel*math.pi/180,vel*math.pi/180,vel*math.pi/180,vel*math.pi/180,vel*math.pi/180,vel*math.pi/180}
    local maxAccel = {accel*math.pi/180,accel*math.pi/180,accel*math.pi/180,accel*math.pi/180,accel*math.pi/180,accel*math.pi/180,accel*math.pi/180}
    local maxJerk = {jerk*math.pi/180,jerk*math.pi/180,jerk*math.pi/180,jerk*math.pi/180,jerk*math.pi/180,jerk*math.pi/180,jerk*math.pi/180}

    local targetPos1 = {90*math.pi/180,90*math.pi/180,170*math.pi/180,-90*math.pi/180,90*math.pi/180,90*math.pi/180,0}
    moveToConfig(jointHandles, maxVel, maxAccel, maxJerk, targetPos1)
    
    local targetPos2 = {-90*math.pi/180,90*math.pi/180,180*math.pi/180,-90*math.pi/180,90*math.pi/180,90*math.pi/180,0}
    moveToConfig(jointHandles, maxVel, maxAccel, maxJerk, targetPos2)

    local targetPos3 = {0, 0, 0, 0, 0, 0, 0}
    moveToConfig(jointHandles, maxVel, maxAccel, maxJerk, targetPos3)

end
