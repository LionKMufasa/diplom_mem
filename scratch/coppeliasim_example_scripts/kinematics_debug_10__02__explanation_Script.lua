sim=require'sim'

function sysCall_init()
        
    h=sim.auxiliaryConsoleOpen('Scene content explanation',100,2+4,{100,100},{700,400})
    local txt=[[This scene illustrates how to visually debug an IK group.
    
It is enough to add the 'debug' option to simIK.handleGroup (or simIK.handleGroups), e.g. as in:

simIK.handleGroup(ikEnv,ikGroup,{debug=1|2,syncWorlds=true})

This however only works if IK elements were added with the simIK.addElementFromScene function. Otherwise, you may use simIK.createDebugOverlay and simIK.eraseDebugOverlay.

Visual overlays are color-coded:

green = tip dummy
red = target dummy
orange =  joint in IK mode
grey = joint in passive mode
blue = dependent joint
white = link
black = connection between objects
purple = base]]
    sim.auxiliaryConsolePrint(h,txt)
    
end

function sysCall_cleanup()
    sim.auxiliaryConsoleClose(h)
end

