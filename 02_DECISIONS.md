# Decisions

Last updated: 2026-05-21

## Maintain Markdown External Memory

- Decision: use root Markdown files as durable external project memory for every substantial task in this folder.
- Reason: after context compaction or a new session, work must resume from stable facts rather than chat history.
- Required start sequence: read [[00_INDEX]] and [[01_CURRENT_STATE]].
- Required closeout: update [[01_CURRENT_STATE]], [[03_TASKS]], and when relevant [[02_DECISIONS]] plus `logs/YYYY-MM-DD.md`.

## Treat NIRS-8 as an Independent VKR Subtopic

- Decision: write NIRS-8 as a separate research report about the degradation model of mechanical robot units.
- Reason: the target deliverable is not a shortened full VKR, but a focused semester research work that can later feed VKR chapters.
- Scope emphasis: wear mechanisms, diagnostic features, mathematical degradation model, health index / limit-state criterion, and RUL-oriented conclusions.
- NIRS-7 should be used as broader context only where useful.

## Keep NIRS-8 Focused On Assignment Tasks, Not Economics

- Decision: remove the separate economic-calculation chapter from the NIRS-8 structure.
- Decision: required NIRS-8 contents order is title page, annotation, contents, introduction, chapters 1-6, conclusion, bibliography, appendix.
- Decision: chapters 1-6 must be `Предпроектное обследование`, `Концептуальное проектирование`, `Техническое задание`, `Техническое проектирование`, `Рабочее проектирование`, and `Апробация`.
- Decision: do not include a separate reliability/failure-probability chapter; cover validation through `6 Апробация`.
- Reason: the assignment sheet requires construction analysis, wear-mechanism study, degradation-model development, diagnostic-feature relation, and limit-state criterion; economics is outside this NIRS-8 task list.
- Practical rule: the report should target about 20 A4 sheets and every chapter should help close one or more assignment tasks.
- Formatting should follow applicable GOST requirements and the 7th-semester NIRS document.

## Move Project Out of CoppeliaSim Installation Folder

- Decision: canonical project root is `C:\Users\egork\Desktop\coppelia_dpilom`.
- Reason: `C:\Program Files\CoppeliaRobotics` is the CoppeliaSim installation folder and should not be used as the long-term ВКР workspace.
- Resulting structure separates scenes, scripts, data, models, docs, experiments, and Markdown memory.

## Use Current Scene, Not Older Test Scenes

- Decision: implement palletizing in `scenes\final_scena_diplom.ttt`.
- Reason: this is the currently running scene with the intended conveyors and objects.
- Avoid applying assumptions from `Diploma.ttt` or earlier `test2` variants unless explicitly revalidated.

## Use Existing Scene Objects as Templates

- Decision: generate cycle objects by cloning existing objects at their original scene positions.
- Mapping:
  - `/Cartoon` = cardboard sheet template.
  - `/packofbottle_respondable` = water bundle/bottle pack template.
  - `/Pallet_bottles` = loaded pallet template.
- Reason: user wants objects generated where they initially are, and previous confusion came from treating cardboard and bottle bundles interchangeably.

## Preserve Object Pose on Attach

- Decision: when gripping, create/use an attach dummy at the object pose and parent the object to that dummy while preserving world pose.
- Reason: avoids the visual error where the load jumps into the gripper from far away.
- Local references reviewed:
  - `staticPickWindow_child.lua`
  - `genericPartPalletizer_child.lua`
  - `pickAndPlaceSettings.lua`
  - `lua/actions/gripper-1.lua`

## Monitor Motors in CoppeliaSim UI

- Decision: graph `motor1..motor4` in a `simUI` window at simulation start.
- Metrics:
  - moment/torque
  - angle
  - velocity
  - acceleration
- Reason: these are the main user-facing motor telemetry requirements for the diploma scene.

## Keep Dynamics Later More Physical

- Decision: current cycle uses scripted pose/parenting for reliable visual/logical palletizing.
- Reason: full physical grasping and contact stability should be handled after the cycle geometry is reliable.

## Use VKR RPZ as Main Writing Artifact

- Decision: work directly in `ВКР\ВКР 2026 Миронов Егор Максимович.docx` for the VKR explanatory note.
- Reason: user explicitly chose this file as the main RPZ file.
- Related note: [[docs/vkr_rpz/working_state]].

## Build VKR Presentation After RPZ

- Decision: postpone `ВКР\Презентация ВКР 2026 Миронов Егор Максимович.pptx` until the RPZ content is stable.
- Reason: the defense deck should be based on the finalized RPZ story, figures, results, and conclusions.

## Use NIRS-7 as Baseline, Not as a Blind Copy

- Decision: reuse suitable text and figures from `ВКР\НИРС(7сем)` but expand and adapt them for full VKR scope.
- Reason: VKR target volume is 70 sheets/pages of main RPZ text; NIRS-7 is a useful foundation but needs stronger practical implementation, validation, reliability/economics, and formatting. Appendices are outside the main RPZ volume.

## Maintain Word-Compatible RPZ Structure

- Decision: use true Word heading styles and a Word TOC field for the RPZ, not manually typed contents.
- Reason: the document will be long, and automatic contents/cross-references are needed to avoid fragile manual numbering.

## Use Two-Level VKR RPZ Contents

- Decision: the VKR RPZ table of contents must include only `Heading 1` and `Heading 2`.
- Reason: user corrected the requirement on 2026-05-06.
- Implementation: TOC field changed from `TOC \o "1-3" \h \z \u` to `TOC \o "1-2" \h \z \u`; third-level headings can remain in the body but are not listed in the contents.

## Fill VKR RPZ DOCX Directly by Default

- Decision: for VKR RPZ work, fill `ВКР\ВКР 2026 Миронов Егор Максимович.docx` directly by default.
- Reason: user returned to the workflow where Codex edits the working DOCX itself.
- Note: ready-to-insert chat text can still be used for review-heavy fragments, but the default deliverable for RPZ filling is the updated DOCX.

## Keep Filled VKR RPZ Text Dense for the 70-Page Limit

- Decision: compress already filled RPZ sections when they become too verbose, while keeping technical formulas, calculation placeholders, tables, and future figure/graph insertion points.
- Reason: user clarified on 2026-05-06 that the draft is already about 59 pages, but the final RPZ main text must fit 70 pages excluding appendices.
- Practical rule: chapters 1-2 and the introduction should establish the engineering basis compactly; detailed screenshots, large diagrams, listings, raw telemetry tables, and extended graphs should be moved to appendices or left as future inserts.

## Write VKR Chapter 3 As A ГОСТ-Oriented Technical Specification

- Decision: chapter 3 `Техническое задание` follows the structure and logic of ГОСТ 34.602-2020 and ГОСТ 34.602-89 while preserving the user's two-level RPZ contents.
- Reason: user provided a lecture/PDF on `ТЗ по ГОСТ 34.602-89` and asked to orient chapter 3 to it.
- Practical rule: ГОСТ sections that do not have separate Heading 2 slots in the RPZ skeleton are integrated as Heading 3/body content: sources of development, preparation of the automation object, documentation requirements, and measurable acceptance criteria.
- Status: superseded by the stricter 2026-05-06 decision below; ГОСТ sections are now visible Heading 2 items in chapter 3.

## Use Strict ГОСТ 34.602-89 Sections For VKR Chapter 3

- Decision: after the 2026-05-06 correction, chapter 3 uses the ГОСТ 34.602-89 required section order as visible Heading 2 items in the two-level TOC.
- Reason: user explicitly requested the ТЗ to be strict according to ГОСТ, including sections and updated contents.
- Practical rule: chapter 3 now contains `Общие сведения`, `Назначение и цели создания системы`, `Характеристика объекта автоматизации`, `Требования к системе`, `Состав и содержание работ`, `Порядок контроля и приемки`, `Требования к подготовке объекта к вводу`, `Требования к документированию`, `Источники разработки`, and `Выводы по главе`.

## Use One-Source Page Citations In VKR RPZ

- Decision: numeric in-text citations in the RPZ should cite one source per bracket and include a page number, e.g. `[8, с. 100]`.
- Reason: user corrected the citation requirement on 2026-05-06.
- Practical rule: avoid grouped citations such as `[7-12]` or `[4, 33]` in the main text; if several sources are needed, use separate sentences or keep only the most relevant source.

## Order VKR Bibliography By Source Type

- Decision: the VKR bibliography order is ГОСТы first, Russian-language literature second, and other sources third.
- Reason: user requested this ordering before continuing the RPZ.
- Current state: the working DOCX bibliography has 45 entries after removing the lecture course source on 2026-05-07.

## Exclude Lecture Course Source From VKR Bibliography

- Decision: remove `Галахарь А.С. Диагностика и надежность автоматизированных систем: курс лекций` from the VKR bibliography and avoid using it for RPZ citations.
- Reason: user explicitly requested removing source 6.
- Implementation rule: after this removal, all bibliography numbers greater than 6 shifted down by one; current maximum bibliography/citation number is `45`.

## Tie VKR Technical Design To The Current CoppeliaSim Scene

- Decision: chapter 4 technical design should reference the actual current scene objects and telemetry path instead of describing a generic robot cell.
- Reason: the RPZ must support the practical implementation and later defense presentation.
- Practical rule: use `final_scena_diplom.ttt`, `/base_respondable`, `motor1...motor4`, `/conveyor_bottles`, `/conveyor_pallet`, `/packofbottle_respondable`, `/Cartoon`, `/Pallet_bottles`, and the current Lua cycle phases as the design baseline.

## Build A Working PAK Before Final RPZ Figures

- Decision: the VKR practical part must produce a working educational/research PAK prototype, not only isolated graphs for the RPZ.
- Reason: the RPZ chapters 5-6 should document a functioning contour and use factual outputs from it.
- Required contour: `CoppeliaSim -> telemetry collection -> storage -> feature calculation -> HI/RUL -> operator display -> maintenance recommendation`.
- Practical rule: CSV/JSONL remains the reproducible evidence layer, while InfluxDB/Grafana can serve as the live PAK layer. RPZ figures and tables should be generated from stored artifacts, not invented manually.
- Planning note: [[docs/vkr_practice/pak_pipeline_plan]].

## Prefer Pose-Based Robot Motion Before Full CFG Calibration

- Decision: after rolling back the first manual `pickPlans` / `placePlans` table, try pose-based gripper/TCP movement with `sim.moveToPose` before calibrating every object position by hand.
- Reason: the user noted that full per-object CFG calibration would be too slow, and the practical scene should look like the robot reaches for payloads rather than following one identical trajectory.
- Practical rule: keep a small number of safe home/transfer configs, but compute pickup/place targets from scene object poses where possible. If CoppeliaSim IK makes closure dummies diverge or does not reach reliably, switch to a hybrid strategy with only a few calibrated fallback configs.

## Respect Parallel-Link Dummy Closure In Robot Motion

- Decision: do not use direct joint sweeps or simple `motor1..motor3` pose tests as reachability proof for the imported palletizing robot.
- Reason: the robot model uses dummy/parallel-link closure; direct joint setting can make `motor3` and helper links drift in an invalid configuration.
- Practical rule: future trajectory tuning must use closed-chain `simIK` loop elements for `dummy1A/B` ... `dummy4A/B`, or be visually verified in CoppeliaSim with those dummy links staying closed.

## Do Not Directly Copy OMPL Planning Into The Closed-Chain Robot

- Decision: use `simpleManipulatorPathPlanning` only as an architectural reference, not as a direct drop-in implementation for the current palletizing script.
- Reason: the example assumes a serial UR5-style manipulator; the diploma scene robot is an imported closed-chain mechanism where sampled joint configurations can violate dummy-loop closure.
- Practical rule: a future planning implementation must validate dummy-loop error along every candidate path, or project each waypoint back through the closed-chain `simIK` model before applying it to the scene. Until then, keep the live cycle on the stable closed-chain servo and/or adjust the pickup geometry into a reachable zone.

## Use The Parallel-Mechanism Example As The Motion Baseline

- Decision: for the current robot-motion blocker, use CoppeliaSim example `7-fkAndIkResolutionForParallelMechanisms.ttt` as the primary local reference before adding more OMPL logic.
- Reason: this is the official example closest to the imported robot's dummy/parallel-link closure problem.
- Practical rule: the next scene-script patch should add a closure-only fallback IK group and optional IK debug overlay. OMPL or `simIK.generatePath` should be added only after candidate states/path waypoints are validated against `dummy1..dummy4` closure error.
- Analysis note: [[docs/vkr_practice/coppeliasim_motion_manual_analysis]].

## Prefer Fast Closure-Preserving Failover For PAK Runs

- Decision: unreachable low pickup/place poses should fail over quickly while preserving dummy-loop closure, instead of spending several seconds trying to solve an impossible target.
- Reason: the practical VKR PAK needs full-cycle telemetry and `cycle_complete`; long unreachable IK attempts were slowing the cycle and previously contributed to incomplete captures.
- Practical rule: keep `closedIkGroupFallback`, `target_unreachable` diagnostics, and `closedIkTargetTimeout = 0.6 s` unless visual testing shows a better reachable geometry. Nonzero TCP errors are acceptable for the current scripted prototype only if loop error remains near zero and payload release correction places objects at planned coordinates.

## Use uArm-Style Calibrated Motion For The Palletizing Cycle

- Decision: after inspecting the in-scene `/uarm` example, the diploma palletizing cycle now uses uArm-style calibrated `sim.moveToConfig` movement for pickup/place instead of the pose-IK path as the default live cycle.
- Reason: the user explicitly requested movement "like uArm"; the uArm example uses predefined joint configurations for motion and a separate gripper script for suction/contact.
- Practical rule: keep the intended `/conveyor_bottles` and `/Pallet_bottles` scene layout; do not move them as the fix. Calibrate per-layer/per-row place configurations and use `releaseSnapTolerance` as a guard against large hidden placement corrections.
- Current verified result: the open scene reached `cycle_complete` for 4 cardboard sheets and 12 water bundles with uArm-style configs; canonical `.ttt` still needs visual approval before saving.

## Fill NIRS-8 As A Complete Draft In The Working DOCX

- Decision: fill `вкр\НИРС(8сем)\НИРС 2026 Миронов Егор Максимович.docx` directly as a complete editable draft.
- Reason: user asked to fill the NIRS-8 report fully now, including calculations and the technical assignment, while leaving signed places for later inserts.
- Practical rule: keep Times New Roman 14, do not force the document to exactly 20 pages, and keep signed placeholders for figures, plots, screenshots, telemetry tables, and appendices.
- Structure rule: follow the user-specified order: title page, annotation, contents, introduction, chapters 1-6, conclusion, bibliography, appendix.
- Implementation note: the separate assignment sheet was removed from the visible report body, but its four tasks are covered inside the chapters and explicitly summarized through the content.

## Structure NIRS-8 Technical Assignment By GOST 34.602-89

- Decision: chapter 3 of NIRS-8 follows the section logic of ГОСТ 34.602-89.
- Reason: user explicitly requested the technical assignment to comply with the attached ГОСТ 34.602-89 PDF.
- Practical rule: adapt the ГОСТ structure to the NIRS scale: the “system” is the research degradation model and diagnostic-feature processing contour, not a full industrial automated system.
- Formatting rule: keep the NIRS report text in Times New Roman 14 and justify body paragraphs, list items, and table-cell paragraphs.
- Contents rule: because Word COM hangs while updating fields in the current environment, keep a clean static two-level contents list until manual Word review can add page numbers.

## Use Single-Source Citation Markers In NIRS-8

- Decision: NIRS-8 in-text references should use one source number per bracket, e.g. `[9]`.
- Reason: user clarified on 2026-05-22 that bracketed references should not contain grouped numbers.
- Practical rule: avoid grouped markers such as `[9, 18]` in NIRS-8. If more than one source is relevant, choose the most direct source for that sentence or use separate nearby sentences.
- Implementation note: after the 2026-05-22 citation pass, the current final NIRS-8 DOCX has `56` citation mentions and no invalid citation markers.

## Use Real Word Equations For VKR Display Formulas

- Decision: display formulas in the VKR RPZ should be stored as Word OMML equation objects, not as plain centered text with underscores.
- Reason: the user requested normal-looking formulas and proper indices instead of visible underscore notation.
- Practical rule: keep explanatory inline variables in prose as text unless they become a separate formula line; convert centered calculation/formula paragraphs to OMML and preserve a backup before each conversion pass.
- Implementation note: on 2026-05-22, `scripts\convert_vkr_formulas_to_omml.py` converted `120` display formula lines in the working VKR DOCX; Microsoft Word counted `121` equations after the pass.
- Follow-up decision: inline mathematical/designation indices in prose should use Word subscript formatting; code/object/event identifiers with underscores should remain unchanged.
- Implementation note: on 2026-05-22, `scripts\convert_vkr_inline_indices.py` added `22` normal-text subscript runs and intentionally left identifiers such as `base_respondable`, `cycle_complete`, and `robot_raw` as plain code-style names.
- Follow-up decision: VKR display formulas should be numbered sequentially at the right edge in round brackets and use 14 pt math formatting.
- Implementation note: on 2026-05-22, `scripts\format_vkr_formulas_and_variables.py` numbered `121` formulas as `(1)` ... `(121)`, set all OMML math runs to 14 pt, and added deeper subscript cleanup in explanatory paragraphs.

## Do Not Repeat Formula Blocks In VKR Chapter 6

- Decision: repeated RUL and metric formulas in the VKR approbation chapter should be removed; chapter 6 should refer to earlier numbered formulas instead.
- Reason: the user clarified that repeated formulas make the RPZ bulky and confusing. The approbation chapter should focus on final numerical results, calculations, tables and interpretation.
- Practical rule: when a calculation in chapter 6 reuses an earlier dependency, cite the existing formula number in prose, for example formulas `(88)`-`(90)` for RUL and `(91)`-`(93)` for MAE/RMSE/R2.
- Implementation note: after removing the repeated chapter 6 formula block and rerunning numbering on 2026-05-22, the VKR formula sequence is `(1)` ... `(114)`.
