sim=require'sim'
simOMPL=require'simOMPL'

function stateValidation(state)
    -- Read the current state:
    local savedState=simOMPL.readState(omplTask)

    -- Apply the provided state:
    simOMPL.writeState(omplTask,state)

    -- Test the state. Allowed are states where the robot is at least
    -- 'minDistance' away from obstacles, and at most 'maxDistance':
    local res,d=sim.checkDistance(collisionPairs[1],collisionPairs[2],maxDistance)
    local pass= (res==1) and (d[7]>minDistance)

    -- Following to visualize distances of the states that are valid:
    if pass then
        sim.addDrawingObjectItem(cont,d)
    end

    -- Restore the current state:
    simOMPL.writeState(omplTask,savedState)

    -- Return whether the tested state is valid or not:
    return pass
end

function visualizePath(path)
    if not _lineContainer then
        _lineContainer=sim.addDrawingObject(sim.drawing_lines,3,0,-1,99999,{0.2,0.2,0.2})
    end
    sim.addDrawingObjectItem(_lineContainer,nil)
    for i=1,#path/3-1,1 do
        sim.addDrawingObjectItem(_lineContainer,{path[(i-1)*3+1],path[(i-1)*3+2],initPos[3],path[i*3+1],path[i*3+2],initPos[3]})
    end
end

function sysCall_thread()
    maxDistance=0.05 -- max allowed distance
    minDistance=0.01 -- min allowed distance
    cont=sim.addDrawingObject(sim.drawing_lines,2,0,-1,99999,{1,0,0})
    robotHandle=sim.getObject('..')
    targetHandle=sim.getObject('/GoalConfiguration')
    initPos=sim.getObjectPosition(robotHandle)
    initOrient=sim.getObjectOrientation(robotHandle)
    omplTask=simOMPL.createTask('omplTask')
    ss={simOMPL.createStateSpace('2d',simOMPL.StateSpaceType.pose2d,robotHandle,{-0.5,-0.5},{0.5,0.5},1)}
    simOMPL.setStateSpace(omplTask,ss)
    simOMPL.setAlgorithm(omplTask,simOMPL.Algorithm.RRTConnect)
    collisionPairs={sim.getObject('../start'),sim.handle_all}
    simOMPL.setStateValidationCallback(omplTask,'stateValidation')
    startpos=sim.getObjectPosition(robotHandle)
    startorient=sim.getObjectOrientation(robotHandle)
    startpose={startpos[1],startpos[2],startorient[3]}
    simOMPL.setStartState(omplTask,startpose)
    goalpos=sim.getObjectPosition(targetHandle)
    goalorient=sim.getObjectOrientation(targetHandle)
    goalpose={goalpos[1],goalpos[2],goalorient[3]}
    simOMPL.setGoalState(omplTask,goalpose)
    simOMPL.setup(omplTask)
    local lb=sim.setStepping(true)
    local r,path=simOMPL.compute(omplTask,8,-1,800)
    if r then
        visualizePath(path)
        
        local function cb(c1,c2)
            local d=sim.getConfigDistance(c1,c2,{1,1,0.001},{0,0,1})
            return d
        end
        
        local ls,l=sim.getPathLengths(path,3,cb)
        for i=0,1,0.0025 do
            local c=sim.getPathInterpolatedConfig(path,ls,i*l,{type='linear'},{0,0,1})
            simOMPL.writeState(omplTask,c)
            sim.step()
        end
    end
    sim.setStepping(lb)
end