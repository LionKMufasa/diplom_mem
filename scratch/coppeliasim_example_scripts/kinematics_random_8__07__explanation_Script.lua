sim=require'sim'

function sysCall_init()
        
    h=sim.auxiliaryConsoleOpen('Scene content explanation',100,2+4,{100,100},{800,300})
    local txt=[[This scene illustrates how to compute joint angles from random end-effector poses. Have a look at the attached scripts and the documentation for the API function simIK.findConfigs.
    ]]
    sim.auxiliaryConsolePrint(h,txt)
    
end

function sysCall_cleanup()
    sim.auxiliaryConsoleClose(h)
end

