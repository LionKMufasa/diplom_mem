original_scene=C:\Users\egork\Desktop\coppelia_dpilom\scratch\current_scene_before_simpleManipulatorPathPlanning_lookup.ttt
## kinematics_parallel_7
scene=C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\scenes\kinematics\simpleExamples\7-fkAndIkResolutionForParallelMechanisms.ttt
scripts=2
- /Script: 52 lines -> kinematics_parallel_7__01__Script.lua
  L2: simIK=require'simIK'
  L5: function sysCall_init()
  L21: ikEnv=simIK.createEnvironment()
  L23: -- Prepare the main ik group, using the convenience function 'simIK.addElementFromScene':
  L24: ikGroup=simIK.createGroup(ikEnv)
  L25: simIK.setGroupCalculation(ikEnv,ikGroup,simIK.method_damped_least_squares,0.1,100)
  L26: local ikElement=simIK.addElementFromScene(ikEnv,ikGroup,simBase,simClosureTip,simClosureTarget,simIK.constraint_x+simIK.constraint_y)
  L27: local ikElement,simToIkObjectMap=simIK.addElementFromScene(ikEnv,ikGroup,simBase,simTip,simTarget,simIK.constraint_x+simIK.constraint_y)
  L28: simIK.setJointMode(ikEnv,simToIkObjectMap[simMotorJoint],simIK.jointmode_passive) -- make sure that joint will act as 'rigid' during IK calculations
  L31: ikGroup_fallback=simIK.createGroup(ikEnv)
  L32: simIK.setGroupCalculation(ikEnv,ikGroup_fallback,simIK.method_damped_least_squares,0.1,100)
  L33: local ikElement,simToIkObjectMap=simIK.addElementFromScene(ikEnv,ikGroup_fallback,simBase,simClosureTip,simClosureTarget,simIK.constraint_x+simIK.constraint_y)
  L34: simIK.setJointMode(ikEnv,simToIkObjectMap[simMotorJoint],simIK.jointmode_passive) -- make sure that joint will act as 'rigid' during IK calculations
  L37: function sysCall_actuation()
  L38: -- Apply IK to the current scene, using the convenience function 'simIK.handleGroup':
  L39: if simIK.handleGroup(ikEnv,ikGroup,{syncWorlds=true})~=simIK.result_success then
  L40: simIK.handleGroup(ikEnv,ikGroup_fallback,{syncWorlds=true,allowError=true}) -- use the fall-back IK group if the main IK group failed
  L44: function sliderMoved(ui,id,value)
  L48: function sysCall_cleanup()
  L50: simIK.eraseEnvironment(ikEnv)
- /explanation/Script: 19 lines -> kinematics_parallel_7__02__explanation_Script.lua
  L3: function sysCall_init()
  L16: function sysCall_cleanup()
## kinematics_random_8
scene=C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\scenes\kinematics\simpleExamples\8-computingJointAnglesForRandomPoses.ttt
scripts=11
- /IRB4600/Script: 61 lines -> kinematics_random_8__01__IRB4600_Script.lua
  L2: simIK=require'simIK'
  L4: function sysCall_init()
  L16: ikEnv=simIK.createEnvironment()
  L18: -- Prepare the ik group, using the convenience function 'simIK.addElementFromScene':
  L19: ikGroup=simIK.createGroup(ikEnv)
  L20: local ikElement,simToIkObjectMapping=simIK.addElementFromScene(ikEnv,ikGroup,simBase,simTip,simTarget,simIK.constraint_pose)
  L21: simIK.setElementPrecision(ikEnv,ikGroup,ikElement,{0.00005,0.1*math.pi/180})
  L30: function validationCB(config,auxData)
  L31: sim.addLog(sim.verbosity_scriptinfos,"Hello from IRB4600 config validation callback")
  L32: -- Here you could check for collisions, and other test. If the configuration is valid, return true
  L36: function sysCall_actuation()
  L38: simIK.setObjectMatrix(ikEnv,ikTarget,sim.getObjectMatrix(dummyHandle,simBase),ikBase)
  L41: local configs = simIK.findConfigs(ikEnv, ikGroup, ikJointHandles, {cb = validationCB, auxData = simJointHandles, cMetric = {1.0, 1.0, 0.5, 0.25, 0.25, 0.1}})
  L59: function sysCall_cleanup()
  L60: simIK.eraseEnvironment(ikEnv)
- /joint[0]/Script: 15 lines -> kinematics_random_8__02__joint_0_Script.lua
  L3: function sysCall_init()
  L11: function sysCall_actuation()
- /joint[1]/Script: 15 lines -> kinematics_random_8__03__joint_1_Script.lua
  L3: function sysCall_init()
  L11: function sysCall_actuation()
- /joint[2]/Script: 15 lines -> kinematics_random_8__04__joint_2_Script.lua
  L3: function sysCall_init()
  L11: function sysCall_actuation()
- /joint[3]/Script: 14 lines -> kinematics_random_8__05__joint_3_Script.lua
  L3: function sysCall_init()
  L11: function sysCall_actuation()
- /LBR4p/Script: 61 lines -> kinematics_random_8__06__LBR4p_Script.lua
  L2: simIK=require'simIK'
  L4: function sysCall_init()
  L16: ikEnv=simIK.createEnvironment()
  L18: -- Prepare the ik group, using the convenience function 'simIK.addElementFromScene':
  L19: ikGroup=simIK.createGroup(ikEnv)
  L20: local ikElement,simToIkObjectMapping=simIK.addElementFromScene(ikEnv,ikGroup,simBase,simTip,simTarget,simIK.constraint_pose)
  L21: simIK.setElementPrecision(ikEnv,ikGroup,ikElement,{0.00005,0.1*math.pi/180})
  L30: function validationCB(config,auxData)
  L31: sim.addLog(sim.verbosity_scriptinfos,"Hello from LBR4p config validation callback")
  L32: -- Here you could check for collisions, and other test. If the configuration is valid, return true
  L36: function sysCall_actuation()
  L38: simIK.setObjectMatrix(ikEnv,ikTarget,sim.getObjectMatrix(dummyHandle,simBase),ikBase)
  L41: local configs = simIK.findConfigs(ikEnv, ikGroup, ikJointHandles, {cb = validationCB, auxData = simJointHandles, cMetric = {1.0, 1.0, 0.5, 0.5, 0.25, 0.25, 0.1}})
  L59: function sysCall_cleanup()
  L60: simIK.eraseEnvironment(ikEnv)
- /explanation/Script: 15 lines -> kinematics_random_8__07__explanation_Script.lua
  L3: function sysCall_init()
  L6: local txt=[[This scene illustrates how to compute joint angles from random end-effector poses. Have a look at the attached scripts and the documentation for the API function simIK.findConfigs.
  L12: function sysCall_cleanup()
- /joint[0]/joint/Script: 14 lines -> kinematics_random_8__08__joint_0_joint_Script.lua
  L3: function sysCall_init()
  L11: function sysCall_actuation()
- /joint[1]/joint/Script: 14 lines -> kinematics_random_8__09__joint_1_joint_Script.lua
  L3: function sysCall_init()
  L11: function sysCall_actuation()
- /joint[2]/joint/Script: 14 lines -> kinematics_random_8__10__joint_2_joint_Script.lua
  L3: function sysCall_init()
  L11: function sysCall_actuation()
- /joint[3]/joint/Script: 15 lines -> kinematics_random_8__11__joint_3_joint_Script.lua
  L3: function sysCall_init()
  L11: function sysCall_actuation()
## kinematics_debug_10
scene=C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\scenes\kinematics\simpleExamples\10-visuallyDebuggingIkGroups.ttt
scripts=3
- /IRB4600/Script: 94 lines -> kinematics_debug_10__01__IRB4600_Script.lua
  L2: simIK=require'simIK'
  L4: function callback_ik(data)
  L6: simIK.handleGroup(ikEnv,ikGroup,{debug=1|2,syncWorlds=true})
  L20: sim.moveToConfig(params)
  L39: sim.moveToConfig(params)
  L42: function sysCall_thread()
  L48: ikEnv=simIK.createEnvironment()
  L50: -- Prepare an ik group, using the convenience function 'simIK.addElementFromScene':
  L52: ikGroup=simIK.createGroup(ikEnv)
  L53: simIK.addElementFromScene(ikEnv,ikGroup,simBase,simTip,simTarget,simIK.constraint_pose)
  L92: function sysCall_cleanup()
  L93: simIK.eraseEnvironment(ikEnv)
- /explanation/Script: 31 lines -> kinematics_debug_10__02__explanation_Script.lua
  L3: function sysCall_init()
  L8: It is enough to add the 'debug' option to simIK.handleGroup (or simIK.handleGroups), e.g. as in:
  L10: simIK.handleGroup(ikEnv,ikGroup,{debug=1|2,syncWorlds=true})
  L12: This however only works if IK elements were added with the simIK.addElementFromScene function. Otherwise, you may use simIK.createDebugOverlay and simIK.eraseDebugOverlay.
  L19: grey = joint in passive mode
  L28: function sysCall_cleanup()
- /IRB4600/IkTip/Script: 16 lines -> kinematics_debug_10__03__IRB4600_IkTip_Script.lua
  L3: function sysCall_init()
  L9: function sysCall_sensing()
## kinematics_ikPathGeneration
scene=C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\scenes\kinematics\ikPathGeneration.ttt
scripts=3
- /UR10/Script: 64 lines -> kinematics_ikPathGeneration__01__UR10_Script.lua
  L2: simIK=require'simIK'
  L4: function hopThroughConfigs(path,joints,reverse,dynModel)
  L29: function sysCall_thread()
  L42: -- Prepare an ik group, using the convenience function 'simIK.addElementFromScene':
  L43: local ikEnv=simIK.createEnvironment()
  L44: local ikGroup=simIK.createGroup(ikEnv)
  L45: local ikElement,simToIkMap=simIK.addElementFromScene(ikEnv,ikGroup,simBase,simTip,simGoal,simIK.constraint_pose)
  L55: local path=simIK.generatePath(ikEnv,ikGroup,ikJoints,ikTip,300)
  L57: simIK.eraseEnvironment(ikEnv)
- /explanation/Script: 16 lines -> kinematics_ikPathGeneration__02__explanation_Script.lua
  L3: function sysCall_init()
  L13: function sysCall_cleanup()
- /UR10/tip/Script: 16 lines -> kinematics_ikPathGeneration__03__UR10_tip_Script.lua
  L3: function sysCall_init()
  L9: function sysCall_sensing()
## kinematics_obstacleAvoidanceAndIk
scene=C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\scenes\kinematics\obstacleAvoidanceAndIk.ttt
scripts=3
- /Script: 120 lines -> kinematics_obstacleAvoidanceAndIk__01__Script.lua
  L2: simIK=require'simIK'
  L4: function sysCall_init()
  L9: ikEnv=simIK.createEnvironment()
  L12: ikGroup=simIK.createGroup(ikEnv)
  L13: simIK.setGroupCalculation(ikEnv,ikGroup,simIK.method_damped_least_squares,0.5,10)
  L14: local ikElement=simIK.addElementFromScene(ikEnv,ikGroup,simBase,simTip,simTarget,simIK.constraint_x+simIK.constraint_y)
  L17: ikGroupAvoidance=simIK.createGroup(ikEnv)
  L18: simIK.setGroupCalculation(ikEnv,ikGroupAvoidance,simIK.method_damped_least_squares,1,1)
  L36: local ikEl,map=simIK.addElementFromScene(ikEnv,ikGroupAvoidance,simBase,tip,target,simIK.constraint_x+simIK.constraint_y)
  L39: simIK.setElementFlags(ikEnv,ikGroupAvoidance,ikEl,0)-- disable it
  L59: function sysCall_actuation()
  L60: simIK.handleGroup(ikEnv,ikGroupAvoidance,{syncWorlds=true})
  L61: simIK.handleGroup(ikEnv,ikGroup,{syncWorlds=true})
  L64: function sysCall_sensing()
  L79: simIK.setElementFlags(ikEnv,ikGroupAvoidance,v.ikElement,1)-- enable it
  L84: simIK.setElementFlags(ikEnv,ikGroupAvoidance,v.ikElement,0)-- disable it
  L91: simIK.setElementFlags(ikEnv,ikGroupAvoidance,v.ikElement,0)-- enable it
  L107: simIK.setElementFlags(ikEnv,ikGroupAvoidance,data.ikElement,1)-- enable it
  L115: function sysCall_cleanup()
  L117: simIK.eraseEnvironment(ikEnv)
- /explanation/Script: 18 lines -> kinematics_obstacleAvoidanceAndIk__02__explanation_Script.lua
  L3: function sysCall_init()
  L15: function sysCall_cleanup()
- /obstacle/Script: 13 lines -> kinematics_obstacleAvoidanceAndIk__03__obstacle_Script.lua
  L3: function sysCall_init()
  L7: function sysCall_actuation()
## path_simpleManipulatorPathPlanning
scene=C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\scenes\pathPlanning\simpleManipulatorPathPlanning.ttt
scripts=4
- /UR5/Script: 361 lines -> path_simpleManipulatorPathPlanning__01__UR5_Script.lua
  L1: function setGripperData(open,velocity,force)
  L18: function moveToPose(pose)
  L26: sim.moveToPose(p)
  L29: function collides(configs)
  L30: -- checks if the configs are related to a collision with the environment or self-collision
  L35: local res = sim.checkCollision(params.robotCollection, sim.handle_all)
  L40: res = sim.checkCollision(params.robotCollection, params.robotCollection)
  L51: function selectOneValidConfig(configs, approachIkTr, withdrawIkTr)
  L52: local retVal, passiveVizShape
  L63: local ikEnv = simIK.createEnvironment()
  L64: local ikGroup = simIK.createGroup(ikEnv)
  L65: local ikEl, simToIk, ikToSim = simIK.addElementFromScene(ikEnv, ikGroup, params.robotBase, params.robotTip, params.robotTarget, simIK.constraint_pose)
  L70: local path = simIK.generatePath(ikEnv, ikGroup, ikJoints, simToIk[params.robotTip], 4)
  L71: simIK.eraseEnvironment(ikEnv)
  L81: local ikEnv = simIK.createEnvironment()
  L82: local ikGroup = simIK.createGroup(ikEnv)
  L83: local ikEl, simToIk, ikToSim = simIK.addElementFromScene(ikEnv, ikGroup, params.robotBase, params.robotTip, params.robotTarget, simIK.constraint_pose)
  L88: local path = simIK.generatePath(ikEnv, ikGroup, ikJoints, simToIk[params.robotTip], 4)
  L89: simIK.eraseEnvironment(ikEnv)
  L116: passiveVizShape = sim.groupShapes(list, true)
  L117: sim.setBoolProperty(passiveVizShape, 'respondable', false)
  L118: sim.setBoolProperty(passiveVizShape, 'dynamic', false)
  L119: sim.setBoolProperty(passiveVizShape, 'collidable', false)
  L120: sim.setBoolProperty(passiveVizShape, 'measurable', false)
  L121: sim.setBoolProperty(passiveVizShape, 'detectable', false)
  L122: sim.setColorProperty(sim.getIntArrayProperty(passiveVizShape, 'meshes')[1], 'color.diffuse', {1, 0, 0})
  L123: sim.setObjectAlias(passiveVizShape, 'passiveVisualizationShape')
  L129: return retVal, passiveVizShape
  L132: function setConfig(c)
  L138: function setTargetConfig(c)
  L144: function getConfig()
  L152: function findConfigs(pose)
  L153: local ikEnv = simIK.createEnvironment()
  L154: local ikGroup = simIK.createGroup(ikEnv)
  L155: local ikEl, simToIk, ikToSim = simIK.addElementFromScene(ikEnv, ikGroup, params.robotBase, params.robotTip, params.robotTarget, simIK.constraint_pose)
  L161: simIK.syncFromSim(ikEnv, {ikGroup}) -- make sure the arm is in the same configuration in the IK world!
  L168: local retVal = simIK.findConfigs(ikEnv, ikGroup, ikJoints, p)
  L169: simIK.eraseEnvironment(ikEnv)
  L173: function findPath(config)
  L174: local useForProjection = {}
  L176: useForProjection[i] = (i <= 3 and 1 or 0)
  L179: local task = simOMPL.createTask('task')
  L180: simOMPL.setAlgorithm(task, params.pathPlanningAlgo)
  L181: simOMPL.setStateSpaceForJoints(task, params.joints, useForProjection)
  L182: simOMPL.setCollisionPairs(task, {params.robotCollection, sim.handle_all, params.robotCollection, params.robotCollection})
  L183: simOMPL.setStartState(task, getConfig())
  L184: simOMPL.setGoalState(task, config)
  L185: -- simOMPL.addGoalState
  L186: simOMPL.setup(task)
  L188: if simOMPL.solve(task, params.pathPlanningMaxTime) and simOMPL.hasExactSolution(task) then
  L189: simOMPL.simplifyPath(task, params.pathPlanningMaxSimplificationTime)
  L190: retVal = simOMPL.getPath(task)
  L192: simOMPL.destroyTask(task)
  L197: function followPath(path)
  L205: pathPts, times, followPathScript = sim.generateTimeOptimalTrajectory(path, pl, minMaxVel, minMaxAccel, 1000, 'not-a-knot', 5, followPathScript)
  L219: function sysCall_thread()
  L221: simIK=require'simIK'
  L222: simOMPL=require'simOMPL'
  L241: params.pathPlanningAlgo = simOMPL.Algorithm.RRTstar
  L290: function pickPart(pickPose, approachIkTr, withdrawIkTr)
  L291: local configs = findConfigs(pickPose)
  L294: local pickConfig, passiveVizShape = selectOneValidConfig(configs, approachIkTr, withdrawIkTr) -- select the closest config to current config
  L295: sim.step() -- to make the passiveVizShape immediately visible
  L302: if passiveVizShape then
  L303: sim.removeObjects({passiveVizShape})
  L311: moveToPose(pose) -- move towards object to pick via IK
  L317: sim.setIntProperty(cube, 'collectionSelfCollisionIndicator', 10) -- so that the cube doesn't generate a robot-self collision between gripper parts and cube
  L321: moveToPose(pose) -- move back and lift object via IK
  L328: function dropPart(cube, dropPose, approachIkTr)
  L329: local configs = findConfigs(dropPose)
  L332: local dropConfig, passiveVizShape = selectOneValidConfig(configs, approachIkTr) -- select the closest config to current config
  L333: sim.step() -- to make the passiveVizShape immediately visible
  L340: if passiveVizShape then
  L341: sim.removeObjects({passiveVizShape})
  L349: moveToPose(pose) -- move towards drop location via IK
  L352: moveToPose(dropPose) -- move back up again via IK
- /conveyor/Script[0]: 16 lines -> path_simpleManipulatorPathPlanning__02__conveyor_Script_0_.lua
  L3: function sysCall_init()
  L8: function sysCall_actuation()
- /conveyor/Script[1]: 1 lines -> path_simpleManipulatorPathPlanning__03__conveyor_Script_1_.lua
- /UR5/RG2/Script: 36 lines -> path_simpleManipulatorPathPlanning__04__UR5_RG2_Script.lua
  L3: function sysCall_init()
  L9: function sysCall_actuation()
  L21: function sysCall_joint(inData)
## path_stateValidationCallback_lua
scene=C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\scenes\pathPlanning\stateValidationCallback-lua.ttt
scripts=2
- /StartConfiguration/Script: 79 lines -> path_stateValidationCallback_lua__01__StartConfiguration_Script.lua
  L2: simOMPL=require'simOMPL'
  L4: function stateValidation(state)
  L6: local savedState=simOMPL.readState(omplTask)
  L9: simOMPL.writeState(omplTask,state)
  L13: local res,d=sim.checkDistance(collisionPairs[1],collisionPairs[2],maxDistance)
  L22: simOMPL.writeState(omplTask,savedState)
  L28: function visualizePath(path)
  L38: function sysCall_thread()
  L46: omplTask=simOMPL.createTask('omplTask')
  L47: ss={simOMPL.createStateSpace('2d',simOMPL.StateSpaceType.pose2d,robotHandle,{-0.5,-0.5},{0.5,0.5},1)}
  L48: simOMPL.setStateSpace(omplTask,ss)
  L49: simOMPL.setAlgorithm(omplTask,simOMPL.Algorithm.RRTConnect)
  L50: collisionPairs={sim.getObject('../start'),sim.handle_all}
  L51: simOMPL.setStateValidationCallback(omplTask,'stateValidation')
  L55: simOMPL.setStartState(omplTask,startpose)
  L59: simOMPL.setGoalState(omplTask,goalpose)
  L60: simOMPL.setup(omplTask)
  L62: local r,path=simOMPL.compute(omplTask,8,-1,800)
  L66: local function cb(c1,c2)
  L74: simOMPL.writeState(omplTask,c)
- /explanation/Script: 17 lines -> path_stateValidationCallback_lua__02__explanation_Script.lua
  L3: function sysCall_init()
  L6: local txt=[[This scene illustrates how to use a state validation callback with OMPL.
  L14: function sysCall_cleanup()
## trajectory_generation_lua
scene=C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\scenes\trajectoryAndMotion\trajectoryGenerationExample-lua.ttt
scripts=3
- /moveToConfig/Script: 39 lines -> trajectory_generation_lua__01__moveToConfig_Script.lua
  L1: function sysCall_init()
  L6: function moveToConfig(handles, maxVel, maxAccel, maxJerk, targetConf)
  L14: sim.moveToConfig(params)
  L17: function sysCall_thread()
  L31: moveToConfig(jointHandles, maxVel, maxAccel, maxJerk, targetPos1)
  L34: moveToConfig(jointHandles, maxVel, maxAccel, maxJerk, targetPos2)
  L37: moveToConfig(jointHandles, maxVel, maxAccel, maxJerk, targetPos3)
- /moveToPose_4dof/Script: 22 lines -> trajectory_generation_lua__02__moveToPose_4dof_Script.lua
  L1: function sysCall_init()
  L7: function sysCall_thread()
  L21: sim.moveToPose(params)
- /moveToPose_1dof/Script: 23 lines -> trajectory_generation_lua__03__moveToPose_1dof_Script.lua
  L1: function sysCall_init()
  L7: function sysCall_thread()
  L22: sim.moveToPose(params)
restored_scene=C:\Users\egork\Desktop\coppelia_dpilom\scratch\current_scene_before_simpleManipulatorPathPlanning_lookup.ttt
reinstalled_lua=C:\Users\egork\Desktop\coppelia_dpilom\scripts\coppeliasim\lua\final_scene_palletizing_cycle.lua