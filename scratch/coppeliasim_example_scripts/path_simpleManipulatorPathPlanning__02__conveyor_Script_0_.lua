sim=require'sim'

function sysCall_init()
    self=sim.getObject('..')
    sensor=sim.getObject('../_sensor')
end

function sysCall_actuation()
    beltVelocity=0.08

    if sim.readProximitySensor(sensor)>0 then
        beltVelocity=0
    end
    
    sim.setBufferProperty(self, 'customData.__ctrl__', sim.packTable({vel=beltVelocity}))
end