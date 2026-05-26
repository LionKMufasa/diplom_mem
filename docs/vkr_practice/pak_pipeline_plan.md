# VKR Practical PAK Pipeline Plan

Last updated: 2026-05-14

## Core Principle

The practical part must produce a working educational/research PAK prototype, not only materials for filling the RPZ.

The RPZ should then be filled with plausible and reproducible outputs from this working contour:

- screenshots;
- telemetry fragments;
- phase tables;
- plots;
- HI/RUL curves;
- model metrics;
- integration-test results.

Runtime runbook: [[docs/vkr_practice/pak_runtime_runbook]].

## Minimum Working PAK

The PAK is considered working when the following chain runs end to end:

`CoppeliaSim -> telemetry collection -> storage -> feature calculation -> HI/RUL -> operator display -> maintenance recommendation`

Required components:

1. Digital model:
   - `scenes/final_scena_diplom.ttt`;
   - `/base_respondable`;
   - `/conveyor_bottles`;
   - `/conveyor_pallet`;
   - `/packofbottle_respondable`;
   - `/Cartoon`;
   - `/Pallet_bottles`;
   - installed script `/base_respondable/palletizing_cycle_script`.

2. Palletizing cycle:
   - 4 cardboard sheets;
   - 12 water bundles;
   - loaded pallet outfeed;
   - cleanup of `cycle_*` objects;
   - phase state in `customData.palletizingCycle`.

3. Telemetry collector:
   - Python/ZMQ collector for `motor1..motor4`;
   - current final-scene collector: `scripts/coppeliasim/python/collect_final_scene_telemetry.py`;
   - fields: `time`, `run_id`, `scenario`, `cycle`, `phase`, `layer`, `item`, `axis`, `q`, `omega`, `accel`, `torque`, `carrying`;
   - raw CSV/JSONL output for reproducibility.

4. Storage layer:
   - file storage as the audit/reproducibility layer;
   - InfluxDB as the PAK time-series layer;
   - current exporter: `scripts/data_pipeline/export_to_influx.py`;
   - current stack: `infra/pak/docker-compose.yml`.

5. Analytics:
   - phase segmentation;
   - feature calculation;
   - degradation scenarios `S0...S3`;
   - `HI_i` calculation;
   - analytical `RUL` estimate;
   - neural-network `RUL` estimate through `sklearn.neural_network.MLPRegressor`;
   - RUL conversion from cycles to hours after the final scene cycle duration is measured;
   - `MAE`, `RMSE`, `R2` where applicable.

6. Operator display:
   - current CoppeliaSim `Motor dynamics monitor` for operational dynamics;
   - Grafana dashboard from `infra/pak/grafana/dashboards/vkr_pak_dashboard.json` for `phase`, `HI`, `RUL`, `risk`, `recommendation`.

## Execution Order

1. Stabilize scene and cycle:
   - tune cardboard pickup;
   - run the full cycle to `cycle_complete`;
   - save the canonical scene.

2. Implement reliable telemetry:
   - collect current scene telemetry with phase labels;
   - validate completeness and timing.

3. Restore/build PAK storage:
   - keep CSV/JSONL as required evidence;
   - connect to InfluxDB for the live PAK contour if possible.

4. Build the analytics layer:
   - generate features by phase and axis;
   - simulate or inject degradation levels;
   - calculate `HI` and `RUL`.

5. Build the display layer:
   - show dynamics, phase, `HI`, `RUL`, risk, and recommendation.

6. Run integration test:
   - prove that every stage of the chain produces a valid output.

7. Fill RPZ with factual outputs:
   - replace chapter 5-6 placeholders with selected plots/tables/screenshots;
   - move large raw tables, code listings, and extended plots to appendices.

## Current Implementation Status

- File-based pipeline is implemented and smoke-tested on legacy telemetry.
- Final-scene JSONL collector is implemented and imports successfully through system Python.
- First final-scene live capture was processed successfully:
  - raw file: `data/telemetry/vkr_raw/final_scene_live_01.jsonl`;
  - normalized rows: `5368`;
  - `K_data = 1.0`;
  - `K_phase = 1.0`;
  - feature rows: `36`;
  - phase count: `9`;
  - last captured simulation time: about `26.85 s`.
- Current state note: [[docs/vkr_practice/data_pipeline_state]].
- Current limitation: first live capture is partial and does not reach `cycle_complete`.
- InfluxDB/Grafana infrastructure and exporter are scaffolded under `infra/pak/`.
- Export dry-run generated `17020` InfluxDB line-protocol rows.
- Second capture `final_scene_full_01.jsonl` was processed and exported:
  - `K_data = 1.0`;
  - `K_phase = 1.0`;
  - feature rows: `52`;
  - InfluxDB export lines: `22452`.
- Export timestamps now use `--timestamp-mode align-end`, so finished simulations appear immediately in Grafana instead of partly in the future.
- Collector now supports optional `-InfluxLive` mode for live Grafana updates of raw motor telemetry and cycle state during simulation.
- Third capture `final_scene_full_02.jsonl` was processed and exported:
  - `K_data = 1.0`;
  - `K_phase = 1.0`;
  - feature rows: `40`;
  - batch export lines: `20987`;
  - final captured phase: `place`, layer 4, `water_bundle_1`;
  - `cycle_complete` still absent.
- Neural-network RUL layer is implemented with `scikit-learn MLPRegressor`:
  - script: `scripts/data_pipeline/train_rul_mlp.py`;
  - predictions: `data/results/vkr_nn_rul_predictions.csv`;
  - metrics: `data/results/vkr_nn_rul_metrics.csv`;
  - model: `data/results/vkr_nn_rul_model.json`;
  - average test `MAE = 2.5675`, `RMSE = 3.0033`, `R2 = 0.9662` on `final_scene_full_02`;
  - InfluxDB measurements: `vkr_nn_rul_predictions`, `vkr_rul_metrics`, `vkr_nn_rul_metrics`;
  - current full export after neural-network integration writes `33835` line-protocol rows.
- Grafana dashboard now includes raw torque, cycle phase, deterministic HI/RUL, neural-network RUL, neural-network error, and neural-network test metric panels.
- Next practical step: debug/stabilize the CoppeliaSim palletizing cycle at final-layer placement, then capture `cycle_complete`.

## Acceptance Criteria

The practical part is accepted when:

- `cycle_complete` is reached in the current scene;
- all expected cycle objects are created and then cleaned;
- telemetry contains mandatory fields and phase labels;
- `K_data >= 0.95`;
- `K_phase >= 0.95`;
- features are calculated for selected phases and axes;
- `HI` decreases with growing degradation;
- predicted `RUL` decreases with growing degradation;
- neural-network `RUL` is trained from the same feature table and exported with metrics;
- the operator display or generated dashboard shows current state and recommendation;
- RPZ figures/tables are generated from stored artifacts, not invented manually.

## RPZ Output Package

Final materials for RPZ chapters 5-6:

- scene screenshot with labels;
- full-cycle screenshot or sequence;
- `Motor dynamics monitor` screenshot;
- raw telemetry fragment;
- telemetry validation table;
- phase-feature table;
- degradation scenario table;
- torque/velocity/acceleration plots;
- `HI` plots for `S0...S3`;
- analytical actual/predicted RUL plot;
- neural-network actual/predicted RUL plot;
- analytical and neural-network metrics table;
- operator panel screenshot or dashboard mock from computed data;
- integration-test table;
- reliability/economic summary table.
