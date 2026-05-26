sim=require'sim'
simIK=require'simIK'
simUI=require'simUI'

function sysCall_init()
    -- Take a few handles from the scene:
    local simBase=sim.getObject('..')
    local simClosureTip=sim.getObject('../closureTip')
    local simClosureTarget=sim.getObject('../closureTarget')
    local simTip=sim.getObject('../tip')
    local simTarget=sim.getObject('../target')
    simMotorJoint=sim.getObject('../motor')
    
    -- Create a custom UI:
    ui=simUI.create([[<ui title="IK" closeable="false" placement="center">
        <label text="Motor angle" />
        <hslider id="1" on-change="sliderMoved" />
    </ui>]])
    simUI.setSliderValue(ui,1,100*sim.getJointPosition(simMotorJoint)/math.pi)

    ikEnv=simIK.createEnvironment()

    -- Prepare the main ik group, using the convenience function 'simIK.addElementFromScene':
    ikGroup=simIK.createGroup(ikEnv)
    simIK.setGroupCalculation(ikEnv,ikGroup,simIK.method_damped_least_squares,0.1,100)
    local ikElement=simIK.addElementFromScene(ikEnv,ikGroup,simBase,simClosureTip,simClosureTarget,simIK.constraint_x+simIK.constraint_y)
    local ikElement,simToIkObjectMap=simIK.addElementFromScene(ikEnv,ikGroup,simBase,simTip,simTarget,simIK.constraint_x+simIK.constraint_y)
    simIK.setJointMode(ikEnv,simToIkObjectMap[simMotorJoint],simIK.jointmode_passive) -- make sure that joint will act as 'rigid' during IK calculations

    -- Prepare the fall-back IK group, where we only care about loop closure:
    ikGroup_fallback=simIK.createGroup(ikEnv)
    simIK.setGroupCalculation(ikEnv,ikGroup_fallback,simIK.method_damped_least_squares,0.1,100)
    local ikElement,simToIkObjectMap=simIK.addElementFromScene(ikEnv,ikGroup_fallback,simBase,simClosureTip,simClosureTarget,simIK.constraint_x+simIK.constraint_y)
    simIK.setJointMode(ikEnv,simToIkObjectMap[simMotorJoint],simIK.jointmode_passive) -- make sure that joint will act as 'rigid' during IK calculations
end

function sysCall_actuation()
    -- Apply IK to the current scene, using the convenience function 'simIK.handleGroup':
    if simIK.handleGroup(ikEnv,ikGroup,{syncWorlds=true})~=simIK.result_success then
        simIK.handleGroup(ikEnv,ikGroup_fallback,{syncWorlds=true,allowError=true}) -- use the fall-back IK group if the main IK group failed
    end
end

function sliderMoved(ui,id,value)
    sim.setJointPosition(simMotorJoint,math.pi*value/100)
end

function sysCall_cleanup()
    -- Clean-up stuff:
    simIK.eraseEnvironment(ikEnv)
    simUI.destroy(ui)
end
