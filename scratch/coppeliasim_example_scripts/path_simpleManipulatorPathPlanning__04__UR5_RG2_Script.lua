sim=require'sim'

function sysCall_init()
    modelBase=sim.getObject('..')
    motorHandle=sim.getObject('../openCloseJoint')
    centerJoint=sim.getObject('../centerJoint')
end

function sysCall_actuation()
    local activity=sim.getBufferProperty(modelBase, 'customData.activity', {noError = true})
    if activity then
        activity=sim.unpackTable(activity)
    else
        activity={velocity=0,force=0}
    end

    sim.setJointTargetForce(motorHandle,activity.force)
    sim.setJointTargetVelocity(motorHandle,activity.velocity)
end

function sysCall_joint(inData)
    if inData.handle==centerJoint then
        local error=(-sim.getJointPosition(motorHandle)/2)-inData.currentPos 
        local ctrl=error*20 
        local velocityToApply=ctrl 
        if (velocityToApply>inData.maxVel) then 
            velocityToApply=inData.maxVel 
        end 
        if (velocityToApply<-inData.maxVel) then 
            velocityToApply=-inData.maxVel 
        end 
        local forceOrTorqueToApply=inData.maxForce 
        local outData={vel=velocityToApply,force=forceOrTorqueToApply} 
        return outData 
    end
end 
