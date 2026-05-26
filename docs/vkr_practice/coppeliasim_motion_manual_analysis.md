# CoppeliaSim Motion Manual And Example Analysis

Last updated: 2026-05-15

## Context

This note supports the current palletizing-scene blocker described in [[01_CURRENT_STATE]] and [[03_TASKS]]:

- the PAK data/ML/Influx/Grafana contour works;
- the remaining practical blocker is believable robot motion in `scenes/final_scena_diplom.ttt`;
- the imported robot is not a simple serial manipulator: it has parallel-link/dummy closure pairs `dummy1A/B` ... `dummy4A/B`;
- direct joint sweeps, widened joint limits, and direct application of sampled IK configs were tested and rejected because they can break dummy-loop closure.

Extracted local example scripts are stored in:

- `scratch/coppeliasim_example_scripts/`
- `scratch/coppeliasim_example_scripts/SUMMARY.md`

The examples were loaded through the CoppeliaSim ZMQ Remote API, then the working scratch scene was restored from `scratch/current_scene_before_simpleManipulatorPathPlanning_lookup.ttt` and the canonical Lua source was reinstalled without saving the `.ttt` scene.

## Manual Findings

Relevant local manual pages:

- `C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\manual\en\solvingIkAndFk.htm`
- `C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\manual\en\pathAndMotionPlanningModules.htm`
- `C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\manual\en\simIK.htm`
- `C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\manual\en\simOMPL.htm`

Important points:

- IK is expressed as groups and elements: an element is a base-tip-target chain with positional/orientation constraints.
- Several chains sharing joints should be solved in one IK group when their constraints are simultaneous.
- Overconstrained IK elements can produce strange behavior; damped least squares is recommended near singularities or when constraints are hard.
- `simIK.handleGroup(..., {syncWorlds=true})` synchronizes from the scene to the IK world, solves, then synchronizes back to the scene.
- `simIK.handleGroup(..., {debug=1|2, syncWorlds=true})` can visualize the IK group when elements were built with `simIK.addElementFromScene`.
- `simIK.findConfigs` is the standard way to find joint states for a target end-effector pose.
- `simIK.generatePath` is the standard way to generate a straight final IK approach/withdraw path.
- The path-planning manual recommends the pattern: goal pose -> `simIK.findConfigs` -> OMPL path -> short final IK approach.
- OMPL default validation is not enough for this robot: a custom `simOMPL.setStateValidationCallback` is needed if OMPL is used, because each candidate state must be rejected when dummy-loop closure error is too large.

## Example Findings

### `7-fkAndIkResolutionForParallelMechanisms.ttt`

Extracted script:

- `scratch/coppeliasim_example_scripts/kinematics_parallel_7__01__Script.lua`

Most relevant pattern:

- build one main IK group containing both the closure element and the useful target element;
- make the manually driven motor joint passive inside the IK world, so it behaves as a rigid known input during IK resolution;
- build a fallback IK group containing only the closure element;
- if the main group fails, handle the fallback group to preserve loop closure instead of letting the mechanism distort.

Implication for our robot:

- our current closed-chain group follows the "one simultaneous IK group" idea, but it does not yet have a fallback group that explicitly preserves closure when the tool target is unreachable;
- the current live loop calls `handleGroup(... allowError=true)`, so it can visually stop short while release correction moves the payload to the planned final pose;
- next code step should add an example-7-style fallback closure group and expose the failure state clearly.

### `8-computingJointAnglesForRandomPoses.ttt`

Extracted scripts:

- `scratch/coppeliasim_example_scripts/kinematics_random_8__01__IRB4600_Script.lua`
- `scratch/coppeliasim_example_scripts/kinematics_random_8__06__LBR4p_Script.lua`

Useful pattern:

- build an IK group from scene objects;
- set the target pose in the IK environment;
- call `simIK.findConfigs` with a validation callback and configuration metric;
- choose a configuration closest to the current one.

Implication for our robot:

- this is useful for an offline/diagnostic reachable-workspace map;
- it is not safe to directly apply returned configs unless the config is validated against actual dummy-loop errors in the scene.

### `10-visuallyDebuggingIkGroups.ttt`

Extracted script:

- `scratch/coppeliasim_example_scripts/kinematics_debug_10__01__IRB4600_Script.lua`

Useful pattern:

- call `simIK.handleGroup(ikEnv, ikGroup, {debug=1|2, syncWorlds=true})`;
- the explanation script states that the debug overlay shows IK objects and joint modes/colors.

Implication for our robot:

- add a temporary debug flag to visualize the real closed-chain IK group while moving toward cardboard and pallet poses;
- this should help catch whether a joint is accidentally treated as active/passive incorrectly.

### `ikPathGeneration.ttt`

Extracted script:

- `scratch/coppeliasim_example_scripts/kinematics_ikPathGeneration__01__UR10_Script.lua`

Useful pattern:

- create IK environment/group from base-tip-goal;
- get IK joint handles from `simToIkMap`;
- call `simIK.generatePath(..., pathPointCount)`;
- step through returned joint configurations.

Implication for our robot:

- `simIK.generatePath` is better than a local target-servo loop for final approach/withdraw, but only after the closed-chain group is built correctly and the path has validation for loop closure.

### `simpleManipulatorPathPlanning.ttt`

Extracted script:

- `scratch/coppeliasim_example_scripts/path_simpleManipulatorPathPlanning__01__UR5_Script.lua`

Useful pattern:

- `findConfigs(pose)` uses `simIK.findConfigs`;
- `selectOneValidConfig` checks collision and validates approach/withdraw paths through `simIK.generatePath`;
- `findPath(config)` uses `simOMPL.setStateSpaceForJoints`, `setCollisionPairs`, `setStartState`, `setGoalState`, `solve`, `simplifyPath`, `getPath`;
- `followPath(path)` converts the joint path into a time-parameterized trajectory with `sim.generateTimeOptimalTrajectory`.

Implication for our robot:

- this is the right high-level architecture for a serial manipulator;
- for the diploma robot it must be adapted, not copied directly;
- every sampled config/path waypoint must satisfy dummy-loop closure, otherwise the same `dummy3 ~= 0.77 m` failure can return.

### `stateValidationCallback-lua.ttt`

Extracted script:

- `scratch/coppeliasim_example_scripts/path_stateValidationCallback_lua__01__StartConfiguration_Script.lua`

Useful pattern:

- save the current OMPL state;
- write the candidate state;
- perform arbitrary checks;
- restore the saved state;
- return whether the candidate is valid.

Implication for our robot:

- if OMPL is added, its validation callback must save state, apply candidate state, measure `dummy1..dummy4` closure errors, optionally check collisions, restore state, and reject candidates above the closure threshold.

## Practical Conclusion

The manual/examples do not support "just use OMPL" for the current scene. The defendable route is:

1. Use example 7 as the primary reference for the imported parallel-link robot.
2. Add a fallback closure-only IK group before adding new planner complexity.
3. Add a temporary IK debug overlay from example 10.
4. Use example 8 / `simIK.findConfigs` only for validated reachability diagnostics.
5. Use `simIK.generatePath` for final approach/withdraw only after closure validation is in place.
6. Use OMPL only with a custom state-validation callback that rejects states with excessive dummy-loop error.

If the target pickup/place points remain outside the valid closed-chain workspace after that, no planner can physically solve the current geometry. Then the correct engineering fix is to move the cardboard/water/pallet pickup-placement geometry into a reachable workspace window, using the already found valid region around:

- pickup-like point: `[-1.30, -0.20, 0.55]`;
- low place-like point: `[-1.30, -0.60, 0.335]`.

## Recommended Next Step

Before touching pallet positions again, implement a small motion-diagnostic patch in `scripts/coppeliasim/lua/final_scene_palletizing_cycle.lua`:

- create `closedIkGroupFallback` with only `dummy1..dummy4` loop elements;
- when the main group fails or loop error grows, run the fallback group and log `target_unreachable` instead of silently relying on payload correction;
- add an optional `debugIkOverlay` flag that passes `debug=1|2` into `simIK.handleGroup`;
- keep canonical scene saving blocked until visual verification.

After that, run a short cardboard pickup/place smoke test and decide from evidence:

- if fallback keeps closure and target is still unreachable, shift the generated object/stack geometry into the valid closed-chain workspace;
- if fallback exposes a bad joint-mode/constraint setup, fix the IK group before changing geometry.
