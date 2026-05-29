# Tasks

Last updated: 2026-05-29

## Current Focus: VKR RPZ

- [in_progress] Fill VKR RPZ in `ВКР\ВКР 2026 Миронов Егор Максимович.docx`.
  - Current correction pass 2026-05-29:
    - [done] Saved external audit and user clarifications in [[docs/vkr_rpz/audit_findings_2026-05-29]], [[01_CURRENT_STATE]], [[02_DECISIONS]], and `logs/2026-05-29.md`.
    - [done] Corrected bibliography entries against local PDFs in `вкр\литература`, especially sources for Taşcı, Gharib, Liu and Kumar.
    - [done] Removed page numbers from in-text citations while keeping source markers.
    - [done] Restored/kept three-level contents structure in the DOCX by assigning heading levels `1-3`.
    - [done] Added synthetic-degradation limitation text without downgrading the whole work wording.
    - [done] Corrected practical-data evidence: inferred `12` cycles and `1121` phase segments, rebuilt `600` feature rows and `192000` RUL/NN rows.
    - [done] Reconciled model selection text around implemented `MLPRegressor`.
    - [done] Reran the file pipeline and regenerated practical figures/PNG copies.
    - [pending] Open the DOCX in Word, update fields/TOC, save a fresh PDF, and visually check page breaks/table layout.
  - Current correction list from `вкр\правки.pdf` 2026-05-29:
    - [done] Fixed title-page company quotes and extra period.
    - [done] Fixed abstract wording and reliability sentence.
    - [done] Resolved ГОСТ 34.602-2020 / 34.602-89 bibliography order and conclusion wording.
    - [done] Replaced `Глава 1...Глава 6` in table 14 with engineering deliverables.
    - [done] Fixed/explained chapter 6 frequency calculations (`2059.05 s` full run, `0.0929 s`, `10.77 Hz`) and `25 Hz` vs `10.77 Hz`.
    - [done] Fixed formula 48 so it renders as `1024²`, not `10242`.
    - [done] Moved the damage/RUL calculation from conclusion into chapter 6 and shortened conclusion.
    - [done] Added reliability and economic-assumption limitation paragraphs.
    - [done] Preserved empty Appendix A per user decision despite norm-control risk.
    - [done] Set all headings and table text runs to `Times New Roman`, `14 pt`.
    - [done] Removed page fragments from in-text citations.
    - [done] Reassigned all heading paragraphs to `Heading 3`, `14 pt`, bold to satisfy the latest norm-control warning about symbols over `18 pt`.
    - [done] Rebuilt upper headers to one empty paragraph in each section.
    - [done] Rebuilt footers to one centered page-number paragraph, with no page number on the title page.
    - [done] Removed old source 5 (`ГОСТ 34.602–89`), shifted in-text references down, and ensured the new source 5 has a citation.
    - [done] Renumbered main formula labels continuously to `(1)` ... `(113)` and updated the affected text/table formula references.
    - [done] Renumbered main-text table captions continuously to `Таблица 1` ... `Таблица 44` and fixed the affected table reference to `таблице 13`.
    - [done] Expanded subsection `3.6.1` with additional acceptance-test text to remove the small-fragment warning.
    - [done] Added an in-text citation for source `[35]`; current source references cover `1-44`.
    - [blocked] Visual render QA remains blocked because LibreOffice/`soffice` is not installed; automated Word COM update timed out.
  - Done: normalized heading structure and Word TOC.
  - Done: added `Перечень принятых сокращений`.
  - Done: inserted clean 32-entry bibliography.
  - Done: drafted expanded first version of `Введение`.
  - Done: drafted chapter 1 `Предпроектное обследование` as ready-to-insert Markdown text: [[docs/vkr_rpz/chapter1_predproject_draft]].
  - Done: inserted chapter 1 directly into the working DOCX and updated Word TOC.
  - Done: corrected RPZ target volume to 70 sheets/pages of main text with appendices outside the volume.
  - Done: switched the Word table of contents to two levels only (`Heading 1` and `Heading 2`).
  - Done: inserted chapter 2 `Концептуальное проектирование` directly into the working DOCX.
  - Done: compressed the already filled introduction and chapters 1-2 for the 70-page main-text limit.
  - Done: added more compact formulas, calculation dependencies, and future insertion markers.
  - Done: inserted chapter 3 `Техническое задание` directly in the DOCX, oriented to ГОСТ 34.602-2020 / ГОСТ 34.602-89.
  - Done: added ГОСТ 34.602-89 and selected PDF literature to bibliography.
  - Done: added literature-backed references into introduction and chapters 1-2.
  - Done: fixed citations to one-source-with-page format, added Russian literature, improved formula formatting, and restructured chapter 3 strictly by ГОСТ 34.602-89.
  - Done: rebuilt bibliography to 46 entries in the order: ГОСТы, Russian-language literature, other sources.
  - Done: inserted chapter 4 `Техническое проектирование` directly in the DOCX.
  - Done: removed source 6, the lecture course by Галахарь А.С., and renumbered old in-text citations.
  - Done: rebuilt bibliography to 45 entries in the order: ГОСТы, Russian-language literature, other sources.
  - Done: inserted chapter 5 `Рабочее проектирование` directly in the DOCX.
  - Done: inserted compact chapter 6 `Апробация и оценка эффективности системы` directly in the DOCX.
  - Done: summarized written RPZ and saved the practical execution plan in [[docs/vkr_rpz/current_written_summary_and_practice_plan]].
  - Done: converted display formulas in the VKR DOCX to real Word OMML equation objects; Word now reports `121` equations and no centered formula-like plain-text paragraphs remain.
  - Done: converted inline mathematical/designation indices in normal VKR text to real Word subscript formatting; code/object/event identifiers with underscores were intentionally left unchanged.
  - Done: set all Word equations to 14 pt and numbered all formula paragraphs at the right edge in round brackets `(1)` ... `(121)`.
  - Done: cleaned variable formatting in formula explanations and other body paragraphs, adding additional subscript formatting for compact variables such as `Nпал`, `Kз,i`, `D_raw`, `F_W`, and `HI_кр`.
  - Done: created concrete RPZ placeholder cleanup plan in [[docs/vkr_rpz/final_insert_delete_map]].
  - Done: generated DOCX-friendly PNG practical figures in `reports\figures\vkr_practice_png`.
  - Done: deleted/replaced the remaining signed placeholders using the final insert/delete map and practical artifacts.
  - Done: filled chapter 6 with final numerical results from `long_live_01`, including `22174` raw packets, `88696` normalized rows, `K_data = 1.000`, `K_phase = 1.000`, `600` feature rows, `192000` RUL/NN rows, and NN metrics `MAE = 1.441`, `RMSE = 2.144`, `R2 = 0.988`.
  - Done: added NIRS-based calculations: `63 kg` package mass, `187 s` cycle time, `231` packages/hour, `14.55 t/hour`, `58212 t/year`, load factor `0.35`.
  - Done: added a calculation-based economic scenario: annual effect `450000 rub/year`, payback `1.0` year.
  - Done: removed repeated RUL/metric formulas in chapter 6 and now refers to formulas `(88)`-`(93)` instead of restating them.
  - Done: reran formula numbering after removals; final sequence is `(1)` ... `(114)`.
  - Done: filled the final `Заключение`.
  - Structural check after final insertion pass: DOCX ZIP passed, remaining `ВСТАВКА` markers `0`, tables `48`, formula sequence continuous through `(114)`.
  - Done: reviewed the user's saved PDF `вкр\ВКР 2026 Миронов Егор Максимович.pdf`; see [[docs/vkr_rpz/pdf_review_2026-05-28]].
  - Done: applied PDF polish fixes directly to the working DOCX after the saved-PDF review.
  - Done: filled empty table captions, fixed stale formula references, renumbered duplicate figures, removed future-tense leftovers, fixed abstract page-count wording, and filled the empty appendix.
  - Done: replaced all `.ttt` scene mentions in the DOCX with the final scene name `vkr_scena.ttt` / `scenes/vkr_scena.ttt`.
  - Done: added `Приложение А` with four supporting tables: software modules, approbation artifacts, normalized telemetry example, and data-processing commands.
  - Structural check after PDF polish pass: DOCX ZIP passed, tables `52`, empty table captions `0`, figure captions `17`, duplicate figures `0`, stale tokens `0`, unexpected scene mentions `0`.
  - Done: expanded appendices to `Приложение А-Г`; see [[docs/vkr_rpz/appendices_2026-05-28]].
  - Done: added references to appendices in chapters `5.2`, `5.4`, `5.10`, `6.1`, `6.3`, `6.4`, and in the conclusion.
  - Done: rewrote the outdated chapter `5.4` collector paragraph to describe the implemented ZeroMQ Remote API JSONL collector.
  - Structural check after appendix expansion: DOCX ZIP passed, tables `60`, appendices `А-Г` present, appendix captions `А.1-А.3`, `Б.1-Б.3`, `В.1-В.3`, `Г.1-Г.3` present, stale old/future tokens `0`.
  - Done: shifted appendix letters after user correction: `Приложение А` is now empty, previous appendix content moved to `Б`, `В`, `Г`, `Д`, and code listings added in `Приложение Ж`.
  - Done: updated all main-text appendix references after the shift; no remaining content reference points to empty appendix `А`.
  - Done: added shortened code listings for telemetry extraction, file-pipeline orchestration, HI/RUL/risk calculation, and MLPRegressor training.
  - Structural check after appendix shift/code pass: DOCX ZIP passed, paragraphs `823`, tables `60`, appendices `А`, `Б`, `В`, `Г`, `Д`, `Ж` present, appendix caption/listing count `16`, stale appendix/scene/future tokens `0`.
  - Current step: open the DOCX in Word, update fields/TOC if needed, save a fresh PDF, and visually check page breaks/table layout.
  - See [[docs/vkr_rpz/working_state]].

## Separate Track: NIRS 8th Semester

- [done] Confirmed this chat will handle NIRS-8 RPZ and the NIRS-8 presentation.
- [done] Created planning folders:
  - `docs/nirs8_rpz/`
  - `docs/presentations/`
- [done] Inspect the current NIRS-8 document structure.
  - Source: `ВКР\НИРС(8сем)\НИРС 2026 Миронов Егор Максимович.docx`
  - Result: document currently contains title page and assignment only; no substantive chapters yet.
- [done] Build the initial NIRS-8 report plan around the degradation-model subtopic.
  - Focus: construction analysis, degradation mechanisms, diagnostic features, mathematical model, health/limit-state criterion, and conclusions.
- [done] Correct NIRS-8 structure according to user requirements from 2026-05-21.
  - Removed separate economic calculations.
  - Removed separate reliability/failure-probability chapter.
  - Added required contents order with title page, annotation, contents, introduction, chapters 1-6, conclusion, bibliography, and appendix.
  - Set chapters 1-6 to `Предпроектное обследование`, `Концептуальное проектирование`, `Техническое задание`, `Техническое проектирование`, `Рабочее проектирование`, and `Апробация`.
  - Aligned subchapters with the four assignment-sheet tasks and 20-sheet target.
- [done] Find and download available literature for NIRS-8.
  - Downloaded new open PDFs into `вкр\литература\НИРС8`.
  - See [[docs/nirs8_rpz/nirs8_literature_selection]].
- [done] Draft and insert full NIRS-8 RPZ content into the DOCX.
  - Inserted: title page, annotation, static contents, introduction, chapters 1-6, conclusion, bibliography, and appendix.
  - Included: chapter 3 technical assignment, degradation-model calculations, HI/RUL formulas, approbation, 6 tables, and signed placeholders for future figures/tables/screenshots.
  - User clarification on 2026-05-21: keep font size 14 and do not force the report to be exactly 20 pages.
- [done] Update the NIRS-8 `.docx` directly.
  - Working file: `вкр\НИРС(8сем)\НИРС 2026 Миронов Егор Максимович.docx`.
  - Backup before full fill: `вкр\НИРС(8сем)\НИРС 2026 Миронов Егор Максимович.backup_before_full_fill_20260521_195609.docx`.
  - Backup before style/volume changes: `вкр\НИРС(8сем)\НИРС 2026 Миронов Егор Максимович.backup_before_style_compact_20260521_200431.docx`.
  - Visual render QA is blocked by missing LibreOffice/`soffice`; structural DOCX checks passed.
- [done] Correct NIRS-8 chapter 3 and formatting after user review.
  - Chapter 3 now follows ГОСТ 34.602-89 sections.
  - Contents was refreshed as a clean static two-level list matching the current headings.
  - Main body text, list items, and table-cell paragraphs are justified.
  - Backup before this correction: `вкр\НИРС(8сем)\НИРС 2026 Миронов Егор Максимович.backup_before_gost_tz_20260521_204500.docx`.
- [done] Strengthen literature references in the user's final NIRS-8 DOCX.
  - Edited the single final file in place: `вкр\НИРС(8сем)\НИРС 2026 Миронов Егор Максимович.docx`.
  - Used the current 22-entry bibliography order in the document, including the Russian-language sources already moved into the early bibliography positions.
  - Inserted references only as one-source markers such as `[9]`; no grouped markers like `[9, 18]`.
  - Fixed the stale ABB reference `[5]` to `[13]`.
  - Structural check after save: `56` citation mentions, no invalid bracket markers, no citation number above `22`.
  - Backup before edit: `вкр\НИРС(8сем)\_backups\НИРС 2026 Миронов Егор Максимович.backup_before_citations_20260522_040135.docx`.
- [pending] Review the filled NIRS-8 document manually in Word and replace signed placeholders with actual figures/tables/screenshots.
- [pending] Build the NIRS-8 presentation after the written structure is accepted.

## Active

- [done] Move project memory and working files into `C:\Users\egork\Desktop\coppelia_dpilom`.

- [in_progress] Build the working VKR PAK contour.
  - Required chain: `CoppeliaSim -> telemetry collection -> storage -> feature calculation -> HI/RUL -> operator display -> maintenance recommendation`.
  - Planning note: [[docs/vkr_practice/pak_pipeline_plan]].
  - Done: implemented and smoke-tested the file-based data pipeline on legacy CSV telemetry.
  - Done: implemented final-scene ZMQ JSONL collector `scripts\coppeliasim\python\collect_final_scene_telemetry.py`.
  - Done: captured and processed first partial final-scene live telemetry run `data\telemetry\vkr_raw\final_scene_live_01.jsonl`.
  - Done: fixed JSONL normalization so zero values are preserved; first live run now validates with `K_data = 1.0` and `K_phase = 1.0`.
  - Done: added full-cycle helper `scripts\coppeliasim\python\run_final_scene_full_collection.ps1`.
  - Done: added InfluxDB/Grafana scaffold under `infra\pak`.
  - Done: added `scripts\data_pipeline\export_to_influx.py`; dry-run generated `17020` line-protocol rows.
  - Done: processed `data\telemetry\vkr_raw\final_scene_full_01.jsonl`; result `K_data = 1.0`, `K_phase = 1.0`, feature rows `52`, export rows `22452`.
  - Done: fixed exporter timestamp alignment so Grafana shows completed run immediately.
  - Done: added `scripts\data_pipeline\run_pipeline_and_export.ps1`.
  - Done: added optional `-InfluxLive` mode for live Grafana telemetry during simulation.
  - Done: added online HI/RUL/neural-network inference in `scripts\data_pipeline\live_analytics_to_influx.py`.
  - Done: connected live analytics to `scripts\pak\run_pak_demo.ps1` and optional `-LiveAnalytics` mode in `scripts\coppeliasim\python\run_final_scene_full_collection.ps1`.
  - Done: updated Grafana dashboard so lower panels accept live analytics points and periodically refreshed MAE/R2.
  - Done: processed and exported `data\telemetry\vkr_raw\final_scene_full_02.jsonl`; result `K_data = 1.0`, `K_phase = 1.0`, feature rows `40`, export rows `20987`.
  - Done: added neural-network RUL layer with `scikit-learn MLPRegressor` in `scripts\data_pipeline\train_rul_mlp.py`.
  - Done: generated neural-network artifacts `data\results\vkr_nn_rul_predictions.csv`, `data\results\vkr_nn_rul_metrics.csv`, `data\results\vkr_nn_rul_model.json`.
  - Done: exported neural-network predictions to InfluxDB as `vkr_nn_rul_predictions`.
  - Done: exported analytical and neural-network metric tables to InfluxDB as `vkr_rul_metrics` and `vkr_nn_rul_metrics`.
  - Done: updated Grafana dashboard with neural-network RUL, error, MAE, and R2 panels.
  - Done: verified latest InfluxDB measurements include `vkr_cycle_state`, `vkr_motor_telemetry`, `vkr_phase_features`, `vkr_rul_estimates`, `vkr_nn_rul_predictions`, `vkr_rul_metrics`, and `vkr_nn_rul_metrics`.
  - Done: added runtime runbook [[docs/vkr_practice/pak_runtime_runbook]].
  - Done: added one-command demo helper `scripts\pak\run_pak_demo.ps1`.
  - Done: added Python dependency list `requirements-pak.txt` for running on another computer.
  - Latest full export rows after neural-network integration: `33835`.
  - Current neural-network test metrics on `final_scene_full_02`: `MAE = 2.5675`, `RMSE = 3.0033`, `R2 = 0.9662`.
  - Current architecture note: live collection/display and live RUL inference are real-time; neural-network retraining remains post-run/periodic; later RPZ text should present this as fast inference plus scheduled model update.
  - Current state: [[docs/vkr_practice/data_pipeline_state]].
  - Current next blocker: run a fresh full live demo on `scenes\pred_final.ttt` and capture Grafana screenshots with all panels populated.
  - Evidence for RPZ must come from saved telemetry, computed features, plots, screenshots, and integration tests.

- [in_progress] Tune cardboard pickup in `final_scena_diplom.ttt`.
  - Current measured bbox gap at `grip_contact`: about `0.079 m`.
  - Done in source: added gripper-contact snapping before attachment to reduce visible distance at pickup.
  - Done in source: lowered payload masses and disabled payload/template collisions to reduce unrealistic motor moments and object ejection.
  - Done in source: changed cardboard and water placement yaw by 90 degrees.
  - Done in source: changed water-bundle layout to far-to-near along the pallet instead of side-by-side overlap direction.
  - Done in source: moved `cycle_complete` before cleanup with a 2-second capture window.
  - Done in second source pass: removed pre-pick movement of `/Cartoon`; it now appears at the original `/Cartoon` pose.
  - Done in second source pass: water bundle clones use the original `/packofbottle_respondable` pose and no longer run through a conveyor move during generation.
  - Done in second source pass: cardboard placement center is aligned to `/Pallet_bottles` `x`/`y`.
  - Done in second source pass: water bundles use the original template orientation and are placed as three rows across pallet width.
  - Done in second source pass: disabled gripper-contact snapping before attachment to avoid visible pre-grasp object flight.
  - Done in third source pass: attempted `/base_respondable/motor4` parenting for attach dummy.
  - Done in fourth source pass: reverted attach dummy to `/base_respondable/gripper_respondable` with zero local pose because motor4 parenting made pickup worse.
  - Done in third source pass: release snap is limited to `0.12 m`; larger placement mismatch is logged instead of teleporting the object.
  - Rolled back: fifth source pass with first-pass manual trajectory tables `pickPlans` / `placePlans`.
  - Rolled back: AABB attach blocking at `0.10 m`.
  - Rolled back: manual calibration helper `scripts\coppeliasim\python\capture_robot_config.py`.
  - Done in current source pass: added pose-based gripper/TCP movement with `sim.moveToPose`.
  - Done in current source pass: added hidden helper dummies `cycleIkTip` under `gripper_respondable` and `cycleIkTarget` in world space.
  - Done in current source pass: replaced cardboard/water pickup-place calls with `pickAndPlaceByPose()`, which computes gripper target poses from actual object pickup/final poses and object heights.
  - Done in current source pass: changed payload attachment to use a top-center carry offset under the gripper.
  - Done in 2026-05-15 source pass: moved TCP to lower gripper contact offset, preserved payload world orientation on attach, restored final release correction to planned stack pose, reversed pallet outfeed direction, and added TCP reach-error warnings.
  - Done: installed `scripts\coppeliasim\lua\final_scene_palletizing_cycle.lua` into the currently open scene via `scripts\coppeliasim\python\install_palletizing_lua.py`.
  - Done: short ZMQ smoke test reached first-layer cardboard and three water-bundle placement phases with the pose-based script.
  - Superseded: earlier raw kinematic reachability check was invalid because it broke the robot dummy/parallel-link closure.
  - Done: added closed-chain `simIK` with `dummy1A/B` ... `dummy4A/B` loop constraints.
  - Done: removed direct `cfgTransfer` during payload transfer and use old `Above/Down` configs only as closed-chain IK seeds.
  - Done: valid closed-chain smoke test reached cardboard `grip_contact` with loop errors near zero, but TCP is still short in `Y` by about `0.7 m`.
  - Done: added `cardboardGripPose` near the robot-facing cardboard edge and reduced closed-chain IK timeout to avoid long visible stalls.
  - Reverted: forward TCP offset experiment because it moved the TCP in the wrong world direction.
  - Reverted: scene-level `dummy_linktype_gcs_loop_closure` because it made loop errors grow to meters; dummy link types were reset to `0`.
  - Done: inspected CoppeliaSim example `simpleManipulatorPathPlanning` and extracted the relevant strategy: `simIK.findConfigs` goal search plus `simOMPL` path planning before local approach.
  - Tested/disabled: direct goal-config application in the live palletizing script, because manual sync of sampled IK configurations broke the imported dummy-loop closure (`dummy3` error about `0.77 m`).
  - Done in source: exact `pick`/`place` down motions no longer jump through old `cfg*Down` seeds before pose IK; those seeds were pulling the robot away from the reached approach pose.
  - Tested/rejected: widening `motor2/motor3` limits. It made low cardboard target mathematically reachable, but broke dummy-loop closure and worsened live motion.
  - Done in source: `releaseLoad()` now smooths large final placement corrections instead of teleporting the payload instantly to the planned stack pose.
  - Done: closed-chain reachability scan showed the current cardboard pickup, water pickup, and pallet place points are outside the valid workspace; candidate valid points are around `[-1.30, -0.20, 0.55]` for pickup and `[-1.30, -0.60, 0.335]` for low placement.
  - Done: analyzed local CoppeliaSim manual/examples and saved [[docs/vkr_practice/coppeliasim_motion_manual_analysis]].
  - Done: extracted example scripts into `scratch\coppeliasim_example_scripts`; the most relevant official example is `7-fkAndIkResolutionForParallelMechanisms.ttt`.
  - Done: added an example-7-style closure-only fallback IK group and optional debug overlay signal `palletizing_debug_ik`.
  - Done: added `palletizing_last_ik_warning` signal with `target_unreachable` diagnostics.
  - Done: reduced `closedIkTargetTimeout` to `0.6 s` so the cycle quickly falls back when a low target is unreachable.
  - Done: after the user moved pallet/cardboard geometry closer, restored `/Pallet_bottles` height to about `Z=0.247` in the open scene for testing.
  - Done: after user correction, reverted test-only scene moves in the open scene; `/conveyor_bottles` and `/Pallet_bottles` are back at their intended coordinates.
  - Done: extracted and analyzed the in-scene uArm scripts:
    - `scratch\uarm_robot_script.lua`
    - `scratch\uarm_gripper_script.lua`
  - Finding: uArm does pick-and-place with two responsibilities: robot movement by calibrated `sim.moveToConfig` poses, and physical suction by a separate gripper script using a proximity sensor plus `sim.setLinkDummy`.
  - New next step: adapt the uArm gripper principle to `/base_respondable` instead of moving pallet/conveyor geometry: create or reuse a contact/suction point, require contact before attach, and detach by breaking the dummy link.
  - Done: added `useUarmStyleConfigMotion = true` and switched the default live cycle to calibrated `moveToConfig` pickup/place movement.
  - Done: added `palletizing_calibration_mode` signal for safe config calibration without running the cycle.
  - Done: calibrated cardboard placement configs by layer and water-bundle placement configs by layer/row.
  - Done: full uArm-style smoke test reached `cycle_complete` at about `256 s` simulation time with 4 cardboard sheets and 12 water bundles.
  - Done on 2026-05-16: changed cardboard release yaw to `-90 deg`, added soft limited attach-position correction, lowered generated `cycle_loaded_pallet` to `Z=0.134`, increased motion limits, added `cycle` telemetry field, and added default infinite cycle mode with `palletizing_infinite_cycle` override.
  - Done on 2026-05-16: full ZMQ verification reached `cycle_complete` at `185.5 s` simulation time with 4 cardboard sheets and 12 water bundles, no `cycle_aborted`, no final `palletizing_last_ik_warning`; the source was installed into the open scene but canonical `.ttt` has not been saved.
  - Done on 2026-05-16 final grip pass: water-bundle carry local position adjusted to `{0.06, 0.19, 0.0}` under the gripper, `releaseSnapTolerance` raised to `0.20 m`, and full ZMQ verification reached `cycle_complete` at `187.35 s` simulation time with no final warning.
  - Current stable smoke result: full 4-layer cycle completed near the 3-minute target, water-bundle visual carry offset is improved, and loaded pallet moved out; open-scene object layout was preserved and canonical `.ttt` has not been saved yet.
  - User visual note: water bundles still visually intersect the gripper, but this is accepted for now; keep the current stable cycle and move on unless the user explicitly reopens gripper tuning.
  - Done: user saved the stable scene as `scenes\pred_final.ttt`.
  - Done: fixed infinite-cycle runtime flag handling; old test value `palletizing_infinite_cycle = 0` was cleared from the open scene, and future single-cycle tests should use a negative signal value.
  - Done: user visually confirmed that the infinite cycle now works and a new pallet appears after outfeed.
  - Next step: save `scenes\pred_final.ttt` again with the fixed infinite-cycle script if not already saved after the fix.
  - Next step after saving: collect final telemetry from `scenes\pred_final.ttt` to `cycle_complete`, run the PAK pipeline, export to InfluxDB/Grafana, and prepare final evidence for RPZ chapters 5-6.
  - Next step after visual approval: run final telemetry capture to `cycle_complete`, process telemetry, and export to the PAK pipeline.
  - Next step: visually verify in CoppeliaSim that `dummy1..dummy4`/robot links do not diverge during IK movement.
  - Next step after visual verification: save `scenes\final_scena_diplom.ttt`.

- [pending] Verify full 4-layer palletizing cycle end-to-end.
  - Done in open-scene smoke test: reached `cycle_complete`.
  - Done in 2026-05-16 ZMQ check: reached `cycle_complete` at `185.5 s` simulation time after speed tuning.
  - Done in 2026-05-16 final grip check: reached `cycle_complete` at `187.35 s` simulation time after water-bundle carry offset tuning.
  - Done in open-scene smoke test: final pallet outfeed ran in `+Y`.
  - Confirm temporary `cycle_*` cleanup after stop.
  - Need final telemetry capture after visual approval to confirm data no longer ends at layer 4 / `water_bundle_1`.

- [pending] Confirm motor graphs remain usable after closing and restarting simulation.
  - UI should be recreated on every simulation start.

- [done] Build VKR defense presentation after RPZ content stabilizes.
  - User confirmed preferred target: `17` slides; maximum allowed if needed: `20` slides.
  - Source baseline: `вкр\НИРС(7сем)\Презентация НИРС 2025 Миронов Егор Максимович.pptx`.
  - Final file: `вкр\Презентация ВКР 2026 Миронов Егор Максимович.pptx`.
  - The previous VKR PPTX placeholder was `0` bytes and was replaced with the generated deck.
  - Added VKR-specific proof slides for CoppeliaSim model, telemetry/features, PAK architecture, degradation/HI, RUL forecast, approbation metrics, monitoring dashboard, and economic effect.
  - Verification: PPTX ZIP passed, slide count `17`, `artifact-tool` import reports `17` slides, preview PNGs rendered and key slides visually checked.
  - Done on 2026-05-29: applied final RPZ sync fixes from PDF review: removed `J1-J6`, updated `600`/`192000`, updated `MAE/RMSE/R2`, separated `0.093 s` telemetry step from `5 s` dashboard update, added model-scenario note, economic formula, and safer prototype conclusion.
  - Planning note: [[docs/presentations/vkr_defense_17_slide_plan]].
  - Next polish step: open the PPTX manually in PowerPoint and review exact typography, line breaks, title-page wording, and whether any dense slide should be split while staying within the `20` slide maximum.

## Done

- [done] Created external Markdown project memory structure.
- [done] Created dedicated project structure under `coppelia_dpilom`.
- [done] Installed palletizing script in `/base_respondable/palletizing_cycle_script`.
- [done] Added motor telemetry UI for `motor1..motor4`.
- [done] Corrected object roles:
  - cardboard from `/Cartoon`
  - water bundles from `/packofbottle_respondable`
  - pallet from `/Pallet_bottles`

## Next Best Step

### For VKR RPZ

1. Open `вкр\ВКР 2026 Миронов Егор Максимович.docx` in Word and visually check chapters 1-6, TOC, bibliography numbering, formulas, captions, figures, and page breaks.
2. Update Word fields/TOC manually because automated Word COM update hung in the current environment.
3. Re-run the ВКР checker after the 2026-05-28 correction pass:
   - listed small headings were removed from the heading structure;
   - requested missing source references `1`, `3`, `5`, `6`, `12`, `14-19`, `21-39`, `42-44` were added.
4. Check the final main-text page count against the `70` page target and move any oversized detailed material to appendices only if needed.

### For CoppeliaSim Practice

1. Launch/save the final CoppeliaSim scene as `scenes\vkr_scena.ttt` (the accepted working scene was previously `scenes\pred_final.ttt`).
2. Run `scripts\pak\run_pak_demo.ps1 -RunId <run_id>` while simulation is stopped, then press Play after the script says it is waiting for simulation start.
3. Open Grafana and verify that raw telemetry, HI/RUL, neural-network RUL, error, MAE, and R2 panels fill during the run.
4. After the run, keep the post-run pipeline/export output as the reproducible evidence layer.
5. Capture Grafana screenshots for NIRS-8/VKR practical sections.
6. Verify `K_data`, `K_phase`, MAE/RMSE/R2, and cycle duration for text/table insertion.
7. Diagnose the scene at `place`, layer 4, `water_bundle_1`.
8. Reopen/connect to running CoppeliaSim via ZMQ port `23000`.
9. Visually verify the new pose-based `sim.moveToPose` movement from [[final_scene_palletizing_cycle]].
10. Run a longer corrected-scene test/capture toward `cycle_complete` with the fallback IK script installed.
11. If visual behavior is acceptable, save the scene under the final name `scenes\vkr_scena.ttt`.
12. Run the full cycle to `cycle_complete`, capture corrected telemetry, re-run the file pipeline, export to InfluxDB/Grafana, and prepare final evidence for RPZ chapters 5-6.
