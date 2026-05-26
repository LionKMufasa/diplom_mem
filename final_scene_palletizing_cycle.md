# final_scene_palletizing_cycle

Source file:

- Canonical: `C:\Users\egork\Desktop\coppelia_dpilom\scripts\coppeliasim\lua\final_scene_palletizing_cycle.lua`
- Legacy copy: `C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\final_scene_palletizing_cycle.lua`

Installed in scene:

- Canonical scene: `C:\Users\egork\Desktop\coppelia_dpilom\scenes\final_scena_diplom.ttt`
- Script object: `/base_respondable/palletizing_cycle_script`

Purpose:

- Runs the scripted palletizing cycle for the diploma scene.
- Creates working copies from scene templates:
  - `/Cartoon` -> cardboard sheet.
  - `/packofbottle_respondable` -> water bundle.
  - `/Pallet_bottles` -> pallet.
- Adds `simUI` motor graphs for `motor1..motor4`.

Important implementation details:

- Current default live motion strategy is uArm-style calibrated `sim.moveToConfig` pickup/place movement.
- Pose-based closed-chain `simIK` / `sim.moveToPose` code remains in the file as fallback and diagnostics, but the verified production cycle uses the calibrated config tables.
- Uses hidden IK helper dummies:
  - `cycleIkTip` under `/base_respondable/gripper_respondable`, zero local pose;
  - `cycleIkTarget` in world space as the moving pose target.
- Uses an attach dummy under the gripper to carry the object. The latest live cycle preserves payload orientation and applies only a small limited local-position correction to improve the visual grip.
- Writes phase state to `/base_respondable` custom data key `customData.palletizingCycle`.
- Writes `cycle` number into the same custom data table so repeated cycles can be separated in telemetry.
- Removes loaded pallet and placed objects after pallet outfeed.
- Temporary generated objects use `cycle_*` aliases.

Known tuning points:

- `poseApproachLift`
- `poseMaxVel`
- `poseMaxAccel`
- `poseMaxJerk`
- `gripContactClearance`
- `cardboardPickPose`
- `waterPickPose`

Install updated source into the open CoppeliaSim scene:

```powershell
python .\scripts\coppeliasim\python\install_palletizing_lua.py
```

Use `--save-scene` only after visual verification.

Current issue:

- 2026-05-14 source tuning pass reduced payload masses, disabled payload collisions for scripted placement, corrected cardboard/water placement orientation, changed water-bundle placement order to far-to-near along the pallet, and exposes `cycle_complete` before cleanup.
- 2026-05-14 second tuning pass after visual feedback:
  - `/Cartoon` is generated at its original scene pose instead of being moved to `cardboardPickPose`;
  - `/packofbottle_respondable` clones are generated at the original water template pose;
  - cardboard is placed at the same `x`/`y` center as `/Pallet_bottles`;
  - cardboard keeps the 90-degree yaw correction so its 1.4 m side aligns with the pallet length;
  - water bundles are rotated back to the original template orientation;
  - water bundles are placed in three rows across pallet width with offsets around `/Pallet_bottles`;
  - payloads are no longer moved to the gripper contact point before attachment.
- 2026-05-14 third/fourth tuning pass:
  - attempted `/base_respondable/motor4` parenting made pickup worse and was reverted;
  - `cycleAttachDummy` is parented to `/base_respondable/gripper_respondable`;
  - dummy local position/orientation under `gripper_respondable` is forced to zero on simulation start and before each attach;
  - release snap is limited by `releaseSnapTolerance = 0.12 m`;
  - if the carried object is farther from the target pose, the script skips teleporting it and logs that the place trajectory must be tuned.
- 2026-05-14 attempted manual trajectory table pass was rolled back at user request.
- 2026-05-14 pose-based IK/TCP pass:
  - added optional `simIK` loading and position-constrained `sim.moveToPose`;
  - added `cycleIkTip` under `gripper_respondable` and `cycleIkTarget` as hidden helper dummies;
  - added `pickAndPlaceByPose()`, which computes tool poses from the real pickup pose and final payload pose;
  - replaced cardboard and water calls in `runCycle()` with pose-based pickup/place movement;
  - `attachLoad()` now accepts a carry offset so the payload is held under the gripper rather than being carried with a large accidental offset;
  - smoke test through ZMQ compiled and reached first-layer cardboard and three water-bundle place phases.
- 2026-05-15 correction after user screenshot:
  - moved `cycleIkTip` from the gripper origin to a lower local TCP offset `tcpLocalOffset = {0, -0.105, 0}`;
  - changed tool-pose calculation to use world vertical `Z` height instead of payload local `Z`, so rotated water bundles do not shift the TCP sideways;
  - changed `attachLoad()` to preserve the payload world pose/orientation instead of forcing payload orientation to the gripper, fixing vertical cardboard pickup;
  - restored final release correction to always set the payload on the planned stack pose while logging large corrections;
  - reversed pallet outfeed direction from `Y - 1.25` to `Y + 1.25`;
  - added `poseReachTolerance` warnings when TCP cannot reach the requested pickup/place pose.
- 2026-05-15 correction after user pointed out the sweep was invalid:
  - the earlier stopped-scene direct joint sweep is not a valid reachability proof because it breaks the robot's dummy/parallel-link closure;
  - replaced simple `sim.moveToPose` movement with a custom closed-chain `simIK` group that includes `cycleIkTip`, `cycleIkTarget`, and loop closure constraints for `dummy1A/B` ... `dummy4A/B`;
  - `pickAndPlaceByPose()` now uses old `Above/Down` configs only as rough seeds, then lets closed-chain IK try to reach the real object pose;
  - direct `cfgTransfer` inside payload transfer was removed to avoid breaking the parallel linkage between pickup and place;
  - smoke test reached `grip_contact` for cardboard with dummy-loop errors essentially zero, but TCP still stayed short in `Y` (`cycleIkTip` about `[-1.681, 0.129, 0.205]` versus cardboard about `[-1.653, 0.845, 0.149]`). This means the next tuning step is not another raw joint sweep, but target/seed/geometry tuning under the closed-chain IK model.
- 2026-05-15 cardboard Y-stall follow-up:
  - added separate `cardboardGripPose` near the robot-facing edge of `/Cartoon`, while keeping the generated cardboard at the original template pose;
  - reduced per-target closed-chain IK timeout to `3.0 s` to avoid long visual stalls when IK sits in a local minimum;
  - tested and reverted a forward TCP offset because it moved the TCP in the wrong world direction in the cardboard pose;
  - tested and reverted scene-level `dummy_linktype_gcs_loop_closure` because it made the dummy-loop errors grow to meters; dummy link types were reset to `0`;
  - latest smoke test reached `grip_contact/lift_with_load` with loop errors near zero, but TCP still stayed short in `Y` (`cycleIkTip` about `Y=0.166`, cardboard about `Y=0.835`).
- 2026-05-15 `simpleManipulatorPathPlanning` inspection:
  - example pattern: use `simIK.findConfigs` to find a target joint configuration for a desired tip pose, then use `simOMPL` to plan/follow a path to that configuration;
  - this cannot be copied directly into the palletizing script because the diploma robot is an imported closed-chain mechanism with dummy loop constraints;
  - direct sampled-config application/manual joint sync was tested and disabled after it broke loop closure (`dummy3` reached about `0.77 m` error);
  - the safe source change retained from this pass is that exact down moves no longer force old `cfgCardboardDown`/`cfgPalletDown` seeds before pose IK;
  - latest stable smoke test reaches first-cardboard `grip_contact` with dummy-loop errors near zero, but the TCP is still visibly above/short of the cardboard surface.
- 2026-05-15 teleport/motion diagnosis:
  - the remaining object "teleports" are mostly deliberate `releaseLoad()` correction snaps to the planned final pose when the gripper has not reached the stack point;
  - temporary `motor2/motor3` limit expansion was tested and removed: it made low targets findable but caused invalid dummy-loop errors and worse live motion;
  - next real fix is geometry/workspace alignment or a planner that validates dummy-loop closure, not another raw angle-range tweak.
- 2026-05-15 release smoothing:
  - current pickup/place geometry was scanned with actual dummy-loop validation and found outside the valid closed-chain workspace for the main cardboard/water/pallet tool points;
  - added smooth release correction in `releaseLoad()` for large placement mismatches: the payload is detached to world and moved linearly to the planned stack pose instead of being instantly teleported;
  - smoke test reached first-cardboard `lift_after_place`; final cardboard pose was correct, but this is still a defensive visual correction because TCP does not physically reach the pallet point.
- 2026-05-15 CoppeliaSim manual/example follow-up:
  - added an example-7-style closure-only fallback IK group `closedIkGroupFallback`;
  - added optional IK debug overlay support via integer signal `palletizing_debug_ik`;
  - added string signal `palletizing_last_ik_warning` and explicit `target_unreachable` warnings with TCP error, loop error, and fallback status;
  - reduced `closedIkTargetTimeout` to `0.6 s`, so unreachable poses fail over quickly and the scripted cycle can progress instead of spending several seconds per unreachable pose;
  - smoke test with the user's closer pallet layout and `/Pallet_bottles` height restored to about `Z=0.247` completed layer 1 (`cardboard + 3 water bundles`) and reached `return_home_between_layers`;
  - dummy-loop error stayed `0.000 m` in warnings, confirming the fallback protects the closed-chain mechanism, while TCP errors remain nonzero because several target poses are still outside the robot's true reachable workspace.
- 2026-05-15 uArm-style motion pass:
  - user requested movement like the in-scene `/uarm` example instead of moving pallet/conveyor geometry;
  - reverted test-only scene geometry moves and kept `/conveyor_bottles = [-0.45, -1.625, 0.45]`, `/Pallet_bottles = [0.6964, -1.5475, 0.247]`;
  - extracted uArm scripts to `scratch/uarm_robot_script.lua` and `scratch/uarm_gripper_script.lua`;
  - added `useUarmStyleConfigMotion = true`;
  - switched the default live cycle to calibrated `pickAndPlace()` with `moveToConfig`, like `/uarm/Script`;
  - added `palletizing_calibration_mode` signal for safe open-scene config calibration without running the cycle;
  - calibrated `cfgCardboardPlaceAbove/Down` per layer and `cfgWaterPlaceAboveByLayer` / `cfgWaterPlaceDownByLayer` per layer and row;
  - kept large release correction blocked (`allowLargeReleaseCorrection = false`) so wrong configs fail instead of hiding the problem;
  - full ZMQ smoke test reached `cycle_complete` at about `256 s` simulation time for 4 cardboard sheets and 12 water bundles;
  - final pallet outfeed moved the loaded pallet in `+Y`, so end-of-run printed placed objects near `Y=-0.2975` after outfeed, not at the station coordinate.
- 2026-05-16 uArm-style polishing pass:
  - increased config-motion limits to `maxVel = {1.85, 1.65, 1.65}`, `maxAccel = {3.0, 2.6, 2.6}`, `maxJerk = {11.0, 9.5, 9.5}`;
  - shortened grip/release waits and pallet outfeed timing;
  - changed cardboard placement yaw correction to `-90 deg` so the planned final quaternion is the close equivalent of the carried orientation and the cardboard should not visually spin by 180 degrees at release;
  - generated `cycle_loaded_pallet` is now moved to `palletStationZOverride = 0.134`, while the original hidden `/Pallet_bottles` template remains unchanged in the scene;
  - `attachLoad()` now accepts a local carry target and applies only a `0.06 m` limited correction toward it, preserving payload orientation;
  - added `cycleIndex` to `customData.palletizingCycle`;
  - added default infinite cycle mode, with runtime signal override `palletizing_infinite_cycle`;
  - full ZMQ verification reached `cycle_complete` at `185.5 s` simulation time, with no `cycle_aborted` and no final `palletizing_last_ik_warning`;
  - installed into the currently open `/base_respondable/palletizing_cycle_script`, but the canonical scene file is still not saved.
- 2026-05-16 final grip visual pass:
  - the user's remaining visual issue was the water bundle being carried too far to the side of the gripper;
  - measured earlier first-water local position relative to `/base_respondable/gripper_respondable` was about `{0.119, 0.212, 0.0}`;
  - exact centering `{0.0, 0.16, 0.0}` looked best locally but broke release on later layers;
  - final compromise is `waterCarryLocalPosition = {0.06, 0.19, 0.0}` and `releaseSnapTolerance = 0.20`;
  - cardboard carry correction is disabled because exact cardboard centering caused a `0.307 m` release mismatch on layer 1;
  - full ZMQ verification reached `cycle_complete` at `187.35 s` simulation time with no `cycle_aborted` and no final warning;
  - source was installed into the open scene; canonical `.ttt` still needs visual approval before saving.
- 2026-05-16 infinite-cycle fix:
  - the cycle did not repeat because a test run left `palletizing_infinite_cycle = 0` in the open scene;
  - `shouldRunInfiniteCycle()` now treats `nil`, `0`, and positive values as repeat enabled;
  - use a negative `palletizing_infinite_cycle` value only when a future test must stop after one pallet;
  - cleared the old signal in the open scene and installed the updated source.
- Latest source was installed into the open CoppeliaSim script `/base_respondable/palletizing_cycle_script` via `install_palletizing_lua.py`.
- Needs visual verification in CoppeliaSim before saving `scenes/final_scena_diplom.ttt`.
