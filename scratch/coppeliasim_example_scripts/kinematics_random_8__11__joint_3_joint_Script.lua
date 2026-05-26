sim=require'sim'

function sysCall_init()
        
    h=sim.getObject('..')
    amplitude=0.5
    speed=1
    
end

function sysCall_actuation()
    sim.setJointPosition(h,math.sin(sim.getSimulationTime()*speed)*amplitude)
end


