sim=require'sim'

function sysCall_init()
        
    h=sim.auxiliaryConsoleOpen('Scene content explanation',100,2+4,{100,100},{800,300})
    local txt=[[This scene illustrates a very simple obstacle avoidance IK example.

When you run the simulation, the main IK group's task is to bring the end-effector (green sphere) onto the target position (red sphere). An auxiliary IK group's task is to move the manipulator away from obstacles. To that end, minimum distances between each manipulator's link and obstacles are constantly computed and serve as 'avoidance vectors'. Those and also the avoidance tip-target pairs are visualized for better understanding.

By setting 'multipleAvoidanceTasks' to false, a single avoidance task is used and things are simplified.]]
    sim.auxiliaryConsolePrint(h,txt)
    
end

function sysCall_cleanup()
    sim.auxiliaryConsoleClose(h)
end

