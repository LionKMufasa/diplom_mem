# Summary Of Written VKR RPZ And Practical Plan

Last updated: 2026-05-07

## Written RPZ Summary

- `Введение`: explains актуальность predictive maintenance for a robotized palletizing cell, defines object, subject, goal, tasks, methods, novelty, and practical significance.
- Chapter 1 `Предпроектное обследование`: describes the production line, palletizing process, ABB IRB 660 role, failure/degradation mechanisms, maintenance strategies, and justification for PdM.
- Chapter 2 `Концептуальное проектирование`: defines system goals, functional structure, data flows, architecture alternatives, technology choices, and system requirements.
- Chapter 3 `Техническое задание`: follows ГОСТ 34.602-89 visible sections in the two-level TOC; specifies purpose, object characteristics, requirements, work composition, acceptance order, documentation, and source documents.
- Chapter 4 `Техническое проектирование`: ties the technical design to the current CoppeliaSim scene, robot object paths, telemetry path, degradation model, RUL formalization, storage, visualization, and deployment logic.
- Chapter 5 `Рабочее проектирование`: fixes implementation artifacts, scene objects, Lua cycle phases, masses, telemetry record structure, feature formulas, RUL algorithm, database measurements, operator UI, and integration checks.
- Chapter 6 `Апробация и оценка эффективности системы`: defines the testing methodology, experiment scenarios, preliminary telemetry checks, RUL metrics, monitoring analysis, reliability indicators, economic formulas, and comparison of maintenance variants. It intentionally leaves placeholders for final practical figures and numeric results.

## Practical Part Plan

1. Stabilize the current CoppeliaSim scene:
   - open `scenes/final_scena_diplom.ttt`;
   - verify `/base_respondable`, conveyors, templates, and `final_scene_palletizing_cycle.lua`;
   - tune the cardboard pickup gap, currently known from memory as about `0.079 m`.
2. Verify the full palletizing cycle:
   - run to `cycle_complete`;
   - confirm 4 cardboard sheets, 12 water bundles, loaded pallet outfeed, and cleanup of `cycle_*` objects.
3. Extend telemetry collection:
   - bind `customData.palletizingCycle` phases to file telemetry;
   - write CSV/JSONL with `time`, `cycle`, `phase`, `layer`, `item`, `axis`, `q`, `omega`, `accel`, `torque`, `carrying`.
4. Generate experiment scenarios:
   - `S0` normal, `S1` weak degradation, `S2` medium, `S3` strong;
   - use the chapter 5 degradation coefficient `alpha_i(N)`.
5. Build preprocessing and feature scripts:
   - segment by phase;
   - compute `mean`, `max`, `std`, `rms`, `energy`, `slope`, phase duration;
   - export feature tables.
6. Implement and check HI/RUL:
   - calculate `HI_i`;
   - create labels `RUL_N = N_cr - N`;
   - train or simulate baseline RUL model;
   - compute MAE, RMSE, R2.
7. Produce final materials for RPZ:
   - screenshots of scene and monitor window;
   - telemetry graphs;
   - degradation and HI curves;
   - RUL actual/predicted graph;
   - reliability and economic tables.
8. Return to RPZ:
   - replace all chapter 5-6 placeholders with actual figures/tables;
   - write `Заключение`;
   - visually inspect and update TOC/page count.
