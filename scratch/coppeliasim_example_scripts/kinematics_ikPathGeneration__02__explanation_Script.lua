sim=require'sim'

function sysCall_init()
        
    h=sim.auxiliaryConsoleOpen('Scene content explanation',100,2+4,{100,100},{800,200})
    local txt=[[This scene illustrates how to generate a path via inverse kinematics

The robot model is not dynamically enabled, see the model properies to change that.]]
    sim.auxiliaryConsolePrint(h,txt)
    
end

function sysCall_cleanup()
    sim.auxiliaryConsoleClose(h)
end

