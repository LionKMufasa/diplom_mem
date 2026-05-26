sim=require'sim'

function sysCall_init()
        
    h=sim.auxiliaryConsoleOpen('Scene content explanation',100,2+4,{100,100},{800,200})
    local txt=[[This scene illustrates how to use a state validation callback with OMPL.
    
The task is to bring the first 'L' onto the second 'L' while keeping a
distance of at least 10 mm, and at most 25 mm from the walls.]]
    sim.auxiliaryConsolePrint(h,txt)
    
end

function sysCall_cleanup()
    sim.auxiliaryConsoleClose(h)
end

