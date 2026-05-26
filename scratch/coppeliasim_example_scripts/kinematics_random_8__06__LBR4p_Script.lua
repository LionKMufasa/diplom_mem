sim=require'sim'
simIK=require'simIK'

function sysCall_init()
    simJointHandles={}
    for i=1,7,1 do
        simJointHandles[i]=sim.getObject('../j',{index=i-1})
    end
    local simTip=sim.getObject('../tip')
    simBase=sim.getObject('..')
    local simTarget=sim.getObject('../target')
    targets={sim.getObject('../testTarget5'),sim.getObject('../testTarget6'),sim.getObject('../testTarget7'),sim.getObject('../testTarget8')}
    cnt1=0
    cnt2=0
    
    ikEnv=simIK.createEnvironment()
    
    -- Prepare the ik group, using the convenience function 'simIK.addElementFromScene':
    ikGroup=simIK.createGroup(ikEnv)
    local ikElement,simToIkObjectMapping=simIK.addElementFromScene(ikEnv,ikGroup,simBase,simTip,simTarget,simIK.constraint_pose)
    simIK.setElementPrecision(ikEnv,ikGroup,ikElement,{0.00005,0.1*math.pi/180})
    ikJointHandles={}
    for i=1,#simJointHandles,1 do
        ikJointHandles[i]=simToIkObjectMapping[simJointHandles[i]]
    end
    ikTarget=simToIkObjectMapping[simTarget]
    ikBase=simToIkObjectMapping[simBase]
end

function validationCB(config,auxData)
    sim.addLog(sim.verbosity_scriptinfos,"Hello from LBR4p config validation callback")
    -- Here you could check for collisions, and other test. If the configuration is valid, return true
    return true
end

function sysCall_actuation()
    local dummyHandle=targets[cnt1+1]
    simIK.setObjectMatrix(ikEnv,ikTarget,sim.getObjectMatrix(dummyHandle,simBase),ikBase)
    
    -- Search for a valid configuration:
    local configs = simIK.findConfigs(ikEnv, ikGroup, ikJointHandles, {cb = validationCB, auxData = simJointHandles, cMetric = {1.0, 1.0, 0.5, 0.5, 0.25, 0.25, 0.1}})
    if #configs > 0 then
        -- We pick the configuration closest to the current configuration
        for i = 1, #simJointHandles, 1 do
            sim.setJointPosition(simJointHandles[i], configs[1][i])
        end
    end
    
    cnt2=cnt2+1
    if cnt2>20 then
        cnt2=0
        cnt1=cnt1+1
        if cnt1>3 then
            cnt1=0
        end
    end
end

function sysCall_cleanup()
    simIK.eraseEnvironment(ikEnv)
end