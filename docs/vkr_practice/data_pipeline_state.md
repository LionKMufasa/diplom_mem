# VKR Data Pipeline State

Last updated: 2026-05-22

## Implemented File Pipeline

The file-based PAK data pipeline is implemented in:

- `scripts/coppeliasim/python/collect_final_scene_telemetry.py`
- `scripts/data_pipeline/pipeline_common.py`
- `scripts/data_pipeline/normalize_telemetry.py`
- `scripts/data_pipeline/validate_telemetry.py`
- `scripts/data_pipeline/build_features.py`
- `scripts/data_pipeline/simulate_degradation.py`
- `scripts/data_pipeline/estimate_rul.py`
- `scripts/data_pipeline/train_rul_mlp.py`
- `scripts/data_pipeline/live_analytics_to_influx.py`
- `scripts/data_pipeline/make_vkr_figures.py`
- `scripts/data_pipeline/run_file_pipeline.py`

Purpose:

- provide a reproducible evidence layer before final CoppeliaSim scene tuning;
- turn raw telemetry into validated records, features, degradation scenarios, HI/RUL estimates, metrics, and RPZ-ready figures;
- allow the same analytics layer to be reused later with final `final_scena_diplom.ttt` telemetry.

## Final Scene Live Collector

The final-scene collector has been added:

- script: `scripts/coppeliasim/python/collect_final_scene_telemetry.py`;
- connection: CoppeliaSim ZMQ Remote API, default `127.0.0.1:23000`;
- robot root: `/base_respondable`;
- motors: `/base_respondable/motor1` ... `/base_respondable/motor4`;
- cycle state: `/base_respondable` property `customData.palletizingCycle`;
- output format: JSONL packets with `time`, `run_id`, `scenario`, `cycle`, `phase`, `layer`, `item`, `carrying`, and `axes`.

Use system Python for live collection because it already has `zmq` available:

```powershell
python .\scripts\coppeliasim\python\collect_final_scene_telemetry.py --duration 180 --run-id final_scene_live_01 --output data\telemetry\vkr_raw\final_scene_live_01.jsonl
```

Then run the existing file pipeline on the captured JSONL. Use system `python`, because the neural-network stage depends on the installed `scikit-learn` package:

```powershell
python .\scripts\data_pipeline\run_file_pipeline.py --inputs data\telemetry\vkr_raw\final_scene_live_01.jsonl --run-id final_scene_live_01
```

For future full-cycle runs, use the helper script while CoppeliaSim is open and simulation is stopped:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\coppeliasim\python\run_final_scene_full_collection.ps1 -RunId final_scene_full_01 -Duration 1800
```

The collector now waits for simulation start and can stop automatically after `cycle_complete`.

## Neural Network RUL Layer

The neural-network RUL layer has been added after deterministic degradation scenario generation:

```text
vkr_degradation_features.csv -> train_rul_mlp.py -> vkr_nn_rul_predictions.csv / vkr_nn_rul_metrics.csv / vkr_nn_rul_model.json
```

Implementation:

- script: `scripts/data_pipeline/train_rul_mlp.py`;
- library: `scikit-learn`;
- model class: `sklearn.neural_network.MLPRegressor`;
- architecture: one hidden layer with `16` neurons;
- activation: `tanh`;
- solver: `adam`;
- default max iterations: `2000`;
- target: `log1p(RUL_actual)`;
- prediction is converted back through `expm1`.

Training data:

- source: `data/experiments/vkr_degradation_features.csv`;
- current run id: `final_scene_full_02`;
- rows: `12800`;
- train rows: `10240`;
- test rows: `2560`;
- split: deterministic grouped split by `scenario|phase|axis`.

Input features:

- phase/axis/scenario one-hot encoded categorical features;
- numeric diagnostic features: `sample_count`, `duration`, `torque_mean`, `torque_max`, `torque_std`, `torque_rms`, `omega_max`, `accel_rms`, `energy`, `torque_slope`, `synthetic_cycle`, `degradation_alpha`;
- derived features: `degradation_progress`, `degradation_rate`, `remaining_alpha`, `HI`, `is_no_degradation`.

Current scikit-learn training result on `final_scene_full_02`:

- prediction rows: `12800`;
- metric rows: `32`;
- average test `MAE`: `2.5675` cycles;
- average test `RMSE`: `3.0033` cycles;
- average test `R2`: `0.9662`;
- actual training iterations before convergence: `166`.

Artifacts:

- predictions: `data/results/vkr_nn_rul_predictions.csv`;
- metrics: `data/results/vkr_nn_rul_metrics.csv`;
- model JSON: `data/results/vkr_nn_rul_model.json`;
- summary: `data/results/nn_rul_summary.json`;
- RPZ figure: `reports/figures/vkr_practice/rul_nn_actual_predicted_s3_motor1.svg`.

Runtime note:

- `scikit-learn` is installed in system Python;
- bundled Python currently does not have `scikit-learn`;
- use `python scripts/data_pipeline/run_file_pipeline.py ...` or `scripts/data_pipeline/run_pipeline_and_export.ps1` for neural-network runs.

## InfluxDB and Grafana Layer

Initial InfluxDB/Grafana infrastructure has been added:

- stack folder: `infra/pak/`;
- docker compose: `infra/pak/docker-compose.yml`;
- Grafana datasource provisioning: `infra/pak/grafana/provisioning/datasources/influxdb.yml`;
- Grafana dashboard provisioning: `infra/pak/grafana/provisioning/dashboards/dashboards.yml`;
- dashboard JSON: `infra/pak/grafana/dashboards/vkr_pak_dashboard.json`;
- exporter: `scripts/data_pipeline/export_to_influx.py`.

Local service settings:

- InfluxDB URL: `http://localhost:8086`;
- Grafana URL: `http://localhost:3000`;
- Influx org: `vkr_org`;
- Influx bucket: `vkr_pak`;
- Influx token: `vkr-local-token-2026`;
- Grafana login: `admin` / `admin`.

The exporter writes current file-pipeline outputs to InfluxDB as:

- `vkr_motor_telemetry`;
- `vkr_cycle_state`;
- `vkr_phase_features`;
- `vkr_rul_estimates`;
- `vkr_nn_rul_predictions`;
- `vkr_rul_metrics`;
- `vkr_nn_rul_metrics`.

Dry-run check on the first live run generated `17020` InfluxDB line-protocol rows.

After re-running the file pipeline on `final_scene_full_01.jsonl`, dry-run/export generated `22452` rows. The earlier unchanged `17020` count happened because the file pipeline outputs still pointed to the previous `final_scene_live_01.jsonl` artifacts.

After adding the scikit-learn neural-network stage and metrics export, the current `final_scene_full_02` artifact set generates `33835` line-protocol rows and writes successfully to InfluxDB.

Exporter timestamp behavior was corrected:

- old behavior: default export mapped simulation `t = 0` to current wall time, so later simulation points could appear in the near future in Grafana;
- new default behavior: `--timestamp-mode align-end`, so the last telemetry point is mapped to `now` and the whole run is visible immediately in Grafana.

One-command post-capture processing and export:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\data_pipeline\run_pipeline_and_export.ps1 -InputPath data\telemetry\vkr_raw\final_scene_full_01.jsonl -RunId final_scene_full_01
```

Current helper defaults point to `final_scene_full_02`, so this shorter command processes and exports the latest captured run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\data_pipeline\run_pipeline_and_export.ps1
```

Optional live Grafana mode:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\coppeliasim\python\run_final_scene_full_collection.ps1 -RunId final_scene_full_02 -Duration 1800 -InfluxLive
```

This mode writes `vkr_motor_telemetry` and `vkr_cycle_state` to InfluxDB during simulation while still saving JSONL. The file pipeline and batch exporter are still needed after the run for `vkr_phase_features` and `vkr_rul_estimates`.

## Live Analytics Layer

Online HI/RUL/NN analytics were added for the Grafana runtime contour:

- script: `scripts/data_pipeline/live_analytics_to_influx.py`;
- input: the collector JSONL file while it is still being written;
- output measurements:
  - `vkr_phase_features`;
  - `vkr_rul_estimates`;
  - `vkr_nn_rul_predictions`;
  - `vkr_nn_rul_metrics`;
- default rolling feature window: `12 s`;
- default analytics update period: `5 s`;
- default metric update period: `60 s`;
- live MAE/R2 require at least `5` accumulated live prediction points;
- live RUL prediction is softly limited to `8 * synthetic_cycles` to avoid out-of-range spikes from short rolling windows;
- neural-network model source: `data/results/vkr_nn_rul_model.json`.

The script computes live phase/axis features from the latest rolling window, applies the same deterministic degradation scenarios `S0..S3`, estimates HI/RUL, loads the saved scikit-learn MLP weights from JSON, and writes live neural-network RUL predictions to InfluxDB.

Live metric behavior:

- `Neural Network RUL Error` is filled from online prediction error against the simulated degradation target;
- live rolling MAE/R2 are still emitted for diagnostics, but the dashboard metric panels display `split = test` because R2 is statistically meaningful only on a validation/test sample;
- if `data/results/vkr_nn_rul_metrics.csv` exists, its latest test metrics are re-published periodically so screenshot panels stay populated.

Full live command through the collector helper:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\coppeliasim\python\run_final_scene_full_collection.ps1 -RunId final_scene_live_full_01 -Duration 1800 -InfluxLive -LiveAnalytics
```

The one-command demo `scripts/pak/run_pak_demo.ps1` now starts live analytics automatically unless `-NoLiveAnalytics` is passed.

For long live monitoring with the infinite scene cycle, pass `-Continuous`; then the helper does not stop on the first `cycle_complete` and runs until `-Duration` or Ctrl+C:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\pak\run_pak_demo.ps1 -RunId final_scene_continuous_01 -Duration 21600 -Continuous
```

Docker check:

- `docker --version` works;
- `docker compose version` works;
- `docker compose config` in `infra/pak` is valid.

## Current Test Run

Legacy smoke-test command:

```powershell
python .\scripts\data_pipeline\run_file_pipeline.py
```

Inputs:

- `data/telemetry/test2_dynamics_monitor.csv`
- `data/telemetry/test2_joint_torques.csv`

Outputs:

- `data/telemetry/vkr_normalized/vkr_telemetry_normalized.csv`
- `data/telemetry/vkr_validated/vkr_telemetry_validated.csv`
- `data/features/vkr_features.csv`
- `data/experiments/vkr_degradation_features.csv`
- `data/results/vkr_rul_estimates.csv`
- `data/results/vkr_rul_metrics.csv`
- `reports/figures/vkr_practice/torque_rms_by_axis.svg`
- `reports/figures/vkr_practice/hi_curves_motor1.svg`
- `reports/figures/vkr_practice/rul_actual_predicted_s3_motor1.svg`
- `reports/figures/vkr_practice/pak_dashboard_summary.svg`

Run summary:

- normalized rows: `2243`;
- valid rows: `2243`;
- invalid rows: `0`;
- `K_data = 1.0`;
- `K_phase = 1.0`;
- axes: `motor1..motor4`;
- base feature rows: `4`;
- degradation scenario rows: `1280`;
- RUL estimate rows: `1280`;
- RUL metric rows: `16`.

## First Final-Scene Live Run

Raw telemetry was captured from the running final scene:

- raw file: `data/telemetry/vkr_raw/final_scene_live_01.jsonl`;
- run id: `final_scene_live_01`;
- collector: `scripts/coppeliasim/python/collect_final_scene_telemetry.py`;
- wall duration: about `180 s`;
- last captured simulation time: about `26.85 s`;
- raw JSONL packets: `1342`;
- normalized long rows: `5368`.

The file pipeline was re-run on the captured JSONL:

```powershell
python .\scripts\data_pipeline\run_file_pipeline.py --inputs data\telemetry\vkr_raw\final_scene_live_01.jsonl --run-id final_scene_live_01
```

Results after fixing JSON normalization of zero values:

- total rows: `5368`;
- valid rows: `5368`;
- invalid rows: `0`;
- `K_data = 1.0`;
- `K_phase = 1.0`;
- phase count: `9`;
- axis count: `4`;
- average sampling interval: `0.0200 s`;
- estimated sampling rate: `49.94 Hz`;
- feature rows: `36`;
- degradation scenario rows: `11520`;
- RUL estimate rows: `11520`.

Captured phases:

- `move_to_pallet`: `5052` rows;
- `place`: `120` rows;
- `pick`: `48` rows;
- `lift_with_load`: `48` rows;
- `lift_before_pick`: `48` rows;
- `pallet_arrived`: `20` rows;
- `cardboard_generated`: `16` rows;
- `water_bundle_generated`: `8` rows;
- `grip_contact`: `8` rows.

Important note: this live run proves the data pipeline on final-scene telemetry, but it is still a partial cycle capture. It did not reach `cycle_complete`; a longer full-cycle capture is still required for final RPZ evidence.

## First Full-Scene Export Attempt

Second captured raw file:

- raw file: `data/telemetry/vkr_raw/final_scene_full_01.jsonl`;
- run id: `final_scene_full_01`;
- last captured simulation time: about `212.2 s`;
- normalized rows after pipeline run: `4608`;
- valid rows: `4608`;
- `K_data = 1.0`;
- `K_phase = 1.0`;
- phase count: `13`;
- feature rows: `52`;
- degradation scenario rows: `16640`;
- RUL estimate rows: `16640`;
- InfluxDB dry-run/export lines: `22452`.

Captured phases:

- `place`;
- `move_to_pallet`;
- `lift_with_load`;
- `pick`;
- `lift_before_pick`;
- `water_bundle_generated`;
- `cardboard_generated`;
- `grip_contact`;
- `unknown`;
- `return_home_between_layers`;
- `pallet_outfeed`;
- `pallet_arrived`;
- `return_home`.

Important limitation: `cycle_complete` was not present in `final_scene_full_01.jsonl`. The final part of the scene switched to `unknown`, which means the script state was no longer available to the collector or the simulation stopped/cleaned up before the final state was captured.

## Second Full-Scene Capture

Third captured raw file:

- raw file: `data/telemetry/vkr_raw/final_scene_full_02.jsonl`;
- run id: `final_scene_full_02`;
- last captured simulation time: about `181.35 s`;
- final captured phase: `place`;
- final captured layer/item: layer `4`, `water_bundle_1`;
- normalized rows after pipeline run: `7164`;
- valid rows: `7164`;
- `K_data = 1.0`;
- `K_phase = 1.0`;
- phase count: `10`;
- feature rows: `40`;
- degradation scenario rows: `12800`;
- RUL estimate rows: `12800`;
- batch export lines before neural-network predictions: `20987`;
- after adding scikit-learn neural-network predictions and metric measurements, dry-run/export lines: `33835`;
- latest neural-network average test metrics: `MAE = 2.5675`, `RMSE = 3.0033`, `R2 = 0.9662`.

Captured phases:

- `place`;
- `move_to_pallet`;
- `lift_with_load`;
- `pick`;
- `lift_before_pick`;
- `water_bundle_generated`;
- `cardboard_generated`;
- `grip_contact`;
- `return_home_between_layers`;
- `pallet_arrived`.

Important limitation: `cycle_complete` was not present in `final_scene_full_02.jsonl`. The collector ended while the scene was still in `place` for layer 4 / `water_bundle_1`, with repeated samples at the same simulation time. This suggests either manual stop/pause or a scene stall during final-layer placement.

InfluxDB verification after export showed `final_scene_full_02` data in:

- `vkr_cycle_state`;
- `vkr_motor_telemetry`;
- `vkr_phase_features`;
- `vkr_rul_estimates`;
- `vkr_nn_rul_predictions`;
- `vkr_rul_metrics`;
- `vkr_nn_rul_metrics`.

## Current Limitation

The legacy smoke test uses `test2` telemetry. The first live run proves that final-scene phase-linked telemetry can be captured and processed.

However, final VKR evidence still needs a longer run that reaches `cycle_complete` and includes all expected phases from `customData.palletizingCycle`, such as:

- `grip_contact`;
- `lift_with_load`;
- `move_to_pallet`;
- `place`;
- `return_home`;
- `cycle_complete`.

## NIRS-8 Grafana Screenshot Run

Raw telemetry was captured from the pred-final scene and then interrupted manually after more than one cycle because the helper's old `--stop-delay 2` was longer than the scene's `cycle_complete` hold time.

- raw file: `data/telemetry/vkr_raw/nirs8_grafana_01.jsonl`;
- run id: `nirs8_grafana_01`;
- raw packets: `2131`;
- normalized rows: `8524`;
- valid rows: `8524`;
- `K_data = 1.000`;
- `K_phase = 1.000`;
- feature rows: `52`;
- degradation scenario rows: `16640`;
- RUL estimate rows: `16640`;
- neural-network prediction rows: `16640`;
- neural-network average test metrics: `MAE = 2.423`, `RMSE = 2.911`, `R2 = 0.977`;
- InfluxDB export lines: `44035`.

The helper `scripts/coppeliasim/python/run_final_scene_full_collection.ps1` now uses `--stop-delay 0.2`, so future runs stop automatically when the short `cycle_complete` phase appears.

Dashboard cleanup for NIRS-8 screenshot:

- `Motor Torque` now groups by `axis`, so live and batch points are reduced to four motor curves instead of many phase/layer/item fragments.
- `Cycle Phase Code` panel was removed from the screenshot dashboard as nonessential; cycle phase remains stored in `vkr_cycle_state` for diagnostics and post-run checks.
- HI/RUL panels are filtered to `axis = motor1` and grouped by degradation `scenario`; they no longer wait only for `cycle_complete`, so live points are visible during the cycle.
- Neural-network RUL/error panels accept live points; MAE/R2 dashboard panels show periodically refreshed `split = test` quality metrics.

## Next Data Tasks

1. Launch CoppeliaSim with `scenes/final_scena_diplom.ttt`.
2. Diagnose why `final_scene_full_02` ended at `place`, layer 4, `water_bundle_1`.
3. Tune/fix the CoppeliaSim scene so the cycle continues through `return_home`, `pallet_outfeed`, and `cycle_complete`.
4. Run another final-scene telemetry capture until `cycle_complete`.
5. Re-run the file pipeline and export results into InfluxDB.
6. Verify the Grafana dashboard panels show torque, phase, HI, and RUL.
7. Verify `K_data >= 0.95` and `K_phase >= 0.95`.
8. Generate final RPZ figures from final run artifacts.
9. Keep current legacy outputs only as pipeline smoke-test artifacts, not final VKR evidence.
