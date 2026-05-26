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
        maxVel={0.58, 0.58, 0.58, 0.58}, -- vx,vy,vz in m/s, Vtheta is rad/s
        maxAccel = {0.024, 0.024, 0.024, 0.024}, -- ax,ay,az in m/s^2, Atheta is rad/s^2
        maxJerk = {0.022, 0.022, 0.022, 0.022}, 
    }
    sim.moveToPose(params)
end