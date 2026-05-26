sim=require'sim'
simIK=require'simIK'

function sysCall_init()
    local simBase=sim.getObject('..')
    local simTip=sim.getObject('../tip')
    local simTarget=sim.getObject('../target')
    
    ikEnv=simIK.createEnvironment()

    -- Main task:
    ikGroup=simIK.createGroup(ikEnv)
    simIK.setGroupCalculation(ikEnv,ikGroup,simIK.method_damped_least_squares,0.5,10)
    local ikElement=simIK.addElementFromScene(ikEnv,ikGroup,simBase,simTip,simTarget,simIK.constraint_x+simIK.constraint_y)

    -- Avoidance tasks:
    ikGroupAvoidance=simIK.createGroup(ikEnv)
    simIK.setGroupCalculation(ikEnv,ikGroupAvoidance,simIK.method_damped_least_squares,1,1)
    linksAndAvoidanceItems={}
    avoidanceItems={tips={},targets={},ikElements={},ikTips={}}
    for i=1,4,1 do
        local link=sim.getObject('../link',{index=i-1})
        local data={}
        local tip=sim.createDummy(0.05,{0,1,0,0,0,0,0,0,0,0,0,0})
        sim.setBoolProperty(tip, 'collidable', false)
        sim.setBoolProperty(tip, 'measurable', false)
        sim.setBoolProperty(tip, 'detectable', false)
        local target=sim.createDummy(0.05,{1,0,0,0,0,0,0,0,0,0,0,0})
        sim.setBoolProperty(target, 'collidable', false)
        sim.setBoolProperty(target, 'measurable', false)
        sim.setBoolProperty(target, 'detectable', false)
        data.tip=tip
        sim.setObjectParent(tip,link,true)
        data.target=target
        sim.setObjectParent(target,simBase,true)
        local ikEl,map=simIK.addElementFromScene(ikEnv,ikGroupAvoidance,simBase,tip,target,simIK.constraint_x+simIK.constraint_y)
        data.ikElement=ikEl
        data.ikTip=map[tip]
        simIK.setElementFlags(ikEnv,ikGroupAvoidance,ikEl,0)-- disable it
        sim.setIntProperty(tip, 'layer',0)
        sim.setIntProperty(target, 'layer',0)
        linksAndAvoidanceItems[link]=data
    end
    
    distThreshold=0.5
    obstacles=sim.createCollection(0)
    sim.addItemToCollection(obstacles,sim.handle_all,-1,0)
    sim.addItemToCollection(obstacles,sim.handle_tree,simBase,1)
    
    manipulatorLinks=sim.createCollection(0)
    sim.addItemToCollection(manipulatorLinks,sim.handle_tree,simBase,0)
    
    local color={1,0.5,0}
    distanceSegments=sim.addDrawingObject(sim.drawing_lines,2,0,-1,99,color)
    
    multipleAvoidanceTasks=true
end

function sysCall_actuation()
    simIK.handleGroup(ikEnv,ikGroupAvoidance,{syncWorlds=true})
    simIK.handleGroup(ikEnv,ikGroup,{syncWorlds=true})
end

function sysCall_sensing()
    sim.addDrawingObjectItem(distanceSegments,nil)
    
    if multipleAvoidanceTasks then
        for k,v in pairs(linksAndAvoidanceItems) do
            local res,d=sim.checkDistance(k,obstacles,distThreshold)
            if res>0 then
                sim.addDrawingObjectItem(distanceSegments,d)
                sim.setObjectPosition(v.tip,d)
                local p1=Vector3({d[1],d[2],d[3]})
                local p2=Vector3({d[4],d[5],d[6]})
                local vect=(p1-p2)
                local l=vect:norm()
                if l>0.001 then
                    sim.setObjectPosition(v.target,(p1+vect*(distThreshold-l)/l):data())
                    simIK.setElementFlags(ikEnv,ikGroupAvoidance,v.ikElement,1)-- enable it
                    sim.setIntProperty(v.tip, 'layer',2)
                    sim.setIntProperty(v.target, 'layer',2)
                end
            else
                simIK.setElementFlags(ikEnv,ikGroupAvoidance,v.ikElement,0)-- disable it
                sim.setIntProperty(v.tip, 'layer',0)
                sim.setIntProperty(v.target, 'layer',0)
            end
        end
    else
        for k,v in pairs(linksAndAvoidanceItems) do
            simIK.setElementFlags(ikEnv,ikGroupAvoidance,v.ikElement,0)-- enable it
            sim.setIntProperty(v.tip, 'layer',0)
            sim.setIntProperty(v.target, 'layer',0)
        end
        
        local res,d,objPairs=sim.checkDistance(manipulatorLinks,obstacles,distThreshold)
        if res>0 then
            local data=linksAndAvoidanceItems[objPairs[1]]
            sim.addDrawingObjectItem(distanceSegments,d)
            sim.setObjectPosition(data.tip,d)
            local p1=Vector3({d[1],d[2],d[3]})
            local p2=Vector3({d[4],d[5],d[6]})
            local v=(p1-p2)
            local l=v:norm()
            if l>0.001 then
                sim.setObjectPosition(data.target,(p1+v*(distThreshold-l)/l):data())
                simIK.setElementFlags(ikEnv,ikGroupAvoidance,data.ikElement,1)-- enable it
                sim.setIntProperty(data.tip, 'layer',2)
                sim.setIntProperty(data.target, 'layer',2)
            end
        end
    end
end

function sysCall_cleanup()
    -- Clean-up stuff:
    simIK.eraseEnvironment(ikEnv)
end


