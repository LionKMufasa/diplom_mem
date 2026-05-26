sim=require'sim'

function sysCall_init()
    h=sim.getObject('..')
    dr=sim.addDrawingObject(sim.drawing_lines|sim.drawing_cyclic,2,0,-1,200,{1,0,1})
    pt=sim.getObjectPosition(h)
end

function sysCall_sensing()
    local l={pt[1],pt[2],pt[3]}
    pt=sim.getObjectPosition(h)
    l[4]=pt[1]
    l[5]=pt[2]
    l[6]=pt[3]
    sim.addDrawingObjectItem(dr,l)
end
