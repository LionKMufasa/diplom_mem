# Project Deliverables Plan

Last updated: 2026-05-26

## Source Materials

- Uploaded previous-semester materials are in `C:\Users\egork\Desktop\coppelia_dpilom\ВКР`.
- The main source document is `ВКР\НИРС(7сем)\НИРС 2025 Миронов Егор Максимович.docx`.
- The 7th-semester NIRS presentation is `ВКР\НИРС(7сем)\Презентация НИРС 2025 Миронов Егор Максимович.pptx`.
- The 8th-semester NIRS document is `ВКР\НИРС(8сем)\НИРС 2026 Миронов Егор Максимович.docx`.
- NIRS-8 topic: `Разработка и исследование модели деградации механических узлов промышленного робота для задач предиктивного обслуживания`.
- The VKR presentation `вкр\Презентация ВКР 2026 Миронов Егор Максимович.pptx` was built on 2026-05-26 as a 17-slide defense deck based on the NIRS-7 presentation and final VKR practical evidence.
- The VKR RPZ file `ВКР\ВКР 2026 Миронов Егор Максимович.docx` is currently a short title/service template, not a substantive draft.
- The scene file `ВКР\final_scena_diplom.ttt` matches `scenes\final_scena_diplom.ttt` by SHA256 hash.

## 7th-Semester NIRS Baseline

Topic:

- Development of a predictive maintenance system for units of an ABB IRB 660-180/3.15 palletizing robot on the bottled-water production/palletizing section of AO Zavod Sestritsa.

Core content already available:

- Problem relevance and transition from scheduled maintenance to condition-based / predictive maintenance.
- Object: ABB IRB 660-180/3.15 robot-palletizer.
- Process: bottled-water production line, with palletizing as the final and critical operation.
- Cargo/cycle assumptions: water bundle mass about 63 kg, cycle time about 3 min, average movement speed about 1.5 m/s.
- Functional decomposition of the line and IDEF0-style decomposition of the PdM system.
- PdM architecture: CoppeliaSim, Python, Remote API, MQTT, InfluxDB, Grafana, Docker/Docker Compose.
- Degradation/RUL concept: Health Index, degradation model for robot axes J1-J6, RUL as a regression task, XGBoost mentioned as a candidate model.
- Reliability chapter: Weibull-based estimate, robot treated as a sequential system of J1-J6, comparison without PdM and with PdM.
- Economic chapter: comparison of expected losses from downtime without PdM and with PdM; reserve robot considered qualitatively and rejected as the baseline solution.

## Target Deliverables

1. VKR practical part:
   - reliable CoppeliaSim palletizing cycle;
   - motor telemetry for motor1..motor4;
   - synthetic telemetry dataset;
   - degradation / health indicator / RUL experiment;
   - figures, tables, and conclusions for the VKR RPZ.

2. VKR RPZ:
   - full explanatory note based on the NIRS-7 foundation;
   - target volume: 70 sheets/pages of main RPZ text; appendices are outside this volume;
   - table of contents should be two-level (`Heading 1` and `Heading 2` only);
   - expanded practical implementation chapter;
   - stronger validation, results, and appendices;
   - final formatting according to VKR templates/examples.

3. VKR presentation:
   - defense deck based on the VKR RPZ;
   - clear story: problem, object, system architecture, simulation, telemetry/RUL, reliability/economics, results.

4. NIRS 8th semester RPZ:
   - separate report on a VKR subtopic, not a compressed copy of the full VKR;
   - focus: degradation model for mechanical robot units, wear mechanisms, diagnostic features, and limit-state criterion;
   - use NIRS-7 as the broader context only where needed.

5. NIRS 8th semester presentation:
   - shorter research-progress deck based on NIRS-8 RPZ.

## Recommended Chat Split

- Chat A: `Практика ВКР / CoppeliaSim / телеметрия`
  - Scope: scene, Lua/Python scripts, telemetry, experiments, screenshots, result figures.
  - Reads: `00_INDEX.md`, `01_CURRENT_STATE.md`, `03_TASKS.md`, `docs/project_deliverables_plan.md`.

- Chat B: `РПЗ ВКР`
  - Scope: full VKR explanatory note, structure, chapter text, citations, formatting.
  - Reads: `00_INDEX.md`, `docs/project_deliverables_plan.md`, `ВКР\НИРС(7сем)\НИРС 2025 Миронов Егор Максимович.docx`, templates/examples.

- Chat C: `НИРС 8 семестр / модель деградации`
  - Scope: NIRS-8 RPZ and NIRS-8 presentation on the VKR subtopic.
  - Focus: construction analysis, degradation mechanisms, mathematical degradation model, diagnostic features, limit-state criterion.
  - Reads: `00_INDEX.md`, `docs/project_deliverables_plan.md`, `ВКР\НИРС(8сем)\НИРС 2026 Миронов Егор Максимович.docx`, and NIRS-7 only as background.

- Chat D: `Презентации`
  - Optional separate chat if slides become heavy.
  - Scope: VKR presentation and NIRS-8 presentation visuals.
  - Reads: relevant RPZ draft plus old NIRS-7 presentation.

## Immediate Next Steps

1. Create direction-specific planning folders under `docs/`:
   - `docs/vkr_practice/`
   - `docs/vkr_rpz/`
   - `docs/nirs8_rpz/`
   - `docs/presentations/`
2. For VKR practice, finish the CoppeliaSim cycle and telemetry export first.
3. For VKR RPZ, build the chapter plan from NIRS-7 and expand it into a full VKR explanation of what happens, why, and how the system works.
4. For NIRS-8, work from the existing NIRS 2026 document/topic and write the degradation-model subtopic as an independent research report.
5. For presentations, postpone final slide design until the written structure and practical results are stable.
