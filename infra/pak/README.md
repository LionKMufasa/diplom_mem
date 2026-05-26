# VKR PAK InfluxDB and Grafana

This folder contains the optional live storage and dashboard layer for the VKR PAK.

Full runtime instructions are in `docs/vkr_practice/pak_runtime_runbook.md`.

The file pipeline remains the reproducible evidence layer:

1. collect final scene telemetry into `data/telemetry/vkr_raw/*.jsonl`;
2. run `scripts/data_pipeline/run_file_pipeline.py`, including the scikit-learn RUL neural network;
3. export validated telemetry, features, analytical RUL, neural-network RUL, and metrics into InfluxDB;
4. inspect the operator dashboard in Grafana.

## Start

```powershell
cd C:\Users\egork\Desktop\coppelia_dpilom\infra\pak
docker compose up -d
```

Services:

- InfluxDB: `http://localhost:8086`
- Grafana: `http://localhost:3000`
- Grafana login: `admin` / `admin`

Local InfluxDB settings:

- org: `vkr_org`
- bucket: `vkr_pak`
- token: `vkr-local-token-2026`

## Export Current Pipeline Outputs

Run from the project root after `run_file_pipeline.py`:

```powershell
python .\scripts\data_pipeline\export_to_influx.py
```

By default, export timestamps are aligned so the last telemetry sample is written near `now`.
This makes the whole finished simulation visible in Grafana immediately.

Use system `python` for these commands, because `scripts/data_pipeline/train_rul_mlp.py` depends on the installed `scikit-learn` package.

Dry-run without writing:

```powershell
python .\scripts\data_pipeline\export_to_influx.py --dry-run
```

One-command processing and export after a capture:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\data_pipeline\run_pipeline_and_export.ps1 -InputPath data\telemetry\vkr_raw\final_scene_full_01.jsonl -RunId final_scene_full_01
```

One-command demo run from the project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\pak\run_pak_demo.ps1 -RunId final_scene_demo_01
```

The exporter writes:

- `vkr_motor_telemetry`
- `vkr_cycle_state`
- `vkr_phase_features`
- `vkr_rul_estimates`
- `vkr_nn_rul_predictions`
- `vkr_rul_metrics`
- `vkr_nn_rul_metrics`

The latest verified `final_scene_full_02` export writes `33835` line-protocol rows.

## Optional Live Telemetry Stream

For Grafana updates during CoppeliaSim simulation, start the collector with live InfluxDB export:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\coppeliasim\python\run_final_scene_full_collection.ps1 -RunId final_scene_full_02 -Duration 1800 -InfluxLive
```

This writes raw motor telemetry and cycle state directly to InfluxDB while still saving JSONL.
After the simulation finishes, run the file pipeline and batch exporter to add features and HI/RUL.
