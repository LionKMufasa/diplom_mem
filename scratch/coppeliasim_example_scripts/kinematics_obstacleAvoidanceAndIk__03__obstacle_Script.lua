sim=require'sim'

function sysCall_init()
    h=sim.getObject('..')
end

function sysCall_actuation()
    local t=sim.getSimulationTime()
    local p=sim.getObjectPosition(h)
    p[1]=math.sin(0.1*t)
    sim.setObjectPosition(h,p)
end

