sim=require'sim'

function sysCall_init()
        
    h=sim.auxiliaryConsoleOpen('Scene content explanation',100,2+4,{100,100},{800,300})
    local txt=[[This scene illustrates a very simple inverse kinematics example.
    
It contains two tasks: the first is responsible to keep the loop closed. The second is responsible to bring the green tip dummy onto its red target dummy.

The two tasks are handled via an IK group containing 2 IK elements. If computation fails, then we fall-back onto a single task of closing the loop.
    ]]
    sim.auxiliaryConsolePrint(h,txt)
    
end

function sysCall_cleanup()
    sim.auxiliaryConsoleClose(h)
end

