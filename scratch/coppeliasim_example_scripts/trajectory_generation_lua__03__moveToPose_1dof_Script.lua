function sysCall_init()
    sim = require('sim')
    sim.setStepping(true)
    h = sim.getObject('..')
end

function sysCall_thread()
    local goalQ = sim.getObjectPose(h)
    goalQ[3] = goalQ[3] + 0.5
    goalQ[4] = -0.258251369
    goalQ[5] = -0.6419757009
    goalQ[6] = 0.5881109834
    goalQ[7] = 0.4186890125
    local params = {
        object = h,
        targetPose = goalQ,
        maxVel = {0.58},
        maxAccel = {0.024},
        maxJerk = {0.022},
        metric = {1, 1, 1, 1},
    }
    sim.moveToPose(params)
end