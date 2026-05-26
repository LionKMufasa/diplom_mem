# VKR PAK Runtime Runbook

Last updated: 2026-05-22

## What The PAK Does

Target working contour:

```text
CoppeliaSim -> ZMQ telemetry collector -> JSONL audit log + InfluxDB -> features -> HI/RUL -> neural-network RUL -> Grafana alert/recommendation
```

The practical meaning is:

- CoppeliaSim is the digital twin and generates motor dynamics during palletizing;
- the collector reads motor positions, velocity, acceleration, torque, and cycle phase from `/base_respondable`;
- JSONL is kept as the reproducible experiment log;
- InfluxDB is the live/time-series storage for Grafana;
- the live analytics process builds rolling phase features and online degradation scenarios during simulation;
- the file pipeline rebuilds the same evidence layer after the run for reproducible reports;
- `sklearn.neural_network.MLPRegressor` learns to predict remaining useful life from features;
- Grafana shows motor state, phase, HI, RUL, neural-network error, and maintenance metrics.

## Real-Time Training vs Real-Time Prediction

For the VKR prototype, the technically sane architecture is not to retrain the neural network on every telemetry sample. The stable split is:

1. Real-time collection and display:
   - raw motor telemetry and cycle state are streamed to InfluxDB during simulation with `-InfluxLive`;
   - `live_analytics_to_influx.py` tails the JSONL file and streams rolling HI/RUL/neural-network predictions during simulation;
   - Grafana can show torque, phase, HI, RUL, neural-network RUL, live error, and periodically refreshed test MAE/R2 while CoppeliaSim is running.
2. Periodic learning / recalculation:
   - after a full cycle, or after a chosen experiment run, the pipeline rebuilds features, degradation scenarios, RUL labels, and retrains the neural network;
   - this produces updated predictions, metrics, and a saved model JSON.
3. Operational prediction:
   - the newest trained model is used to estimate RUL from the latest feature vector;
   - the result is converted to hours and compared with warning/maintenance thresholds.

This is easier to defend than “the network learns every 0.05 seconds”, because real predictive-maintenance systems normally separate fast inference from slower model updating.

## RUL In Hours

Current scripts estimate RUL in synthetic cycles. For the RPZ and dashboard this should be converted to hours after the scene reaches `cycle_complete` reliably:

```text
RUL_hours = RUL_cycles * T_cycle_seconds / 3600
```

Where `T_cycle_seconds` is measured from the final CoppeliaSim full-cycle run. After scene stabilization, use the captured simulation time from start to `cycle_complete` as the cycle duration.

Current maintenance decision logic in the neural-network stage:

- `high`: `HI <= 0.35` or predicted RUL below `10` cycles;
- `warning`: `HI < 0.55` or predicted RUL below `25` cycles;
- otherwise: `normal`.

After conversion to hours, the same thresholds can be presented as hour limits for planned ТО.

## One-Command Demo Run

From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\pak\run_pak_demo.ps1 -RunId final_scene_demo_01
```

What it does:

1. starts InfluxDB and Grafana with Docker Compose;
2. starts the CoppeliaSim telemetry collector;
3. starts live HI/RUL/neural-network analytics;
4. waits for simulation start;
5. writes live raw telemetry to InfluxDB and JSONL;
6. writes rolling HI/RUL/neural-network predictions and live metrics to InfluxDB;
7. after collection ends, runs the feature/RUL/neural-network pipeline;
8. exports final analytics and metrics to InfluxDB.

Manual action during the run:

1. open CoppeliaSim;
2. load `scenes/pred_final.ttt`;
3. keep simulation stopped;
4. start the PowerShell command above;
5. wait for “Waiting for CoppeliaSim simulation start”;
6. press Play in CoppeliaSim.

Open Grafana:

```text
http://localhost:3000
login: admin
password: admin
```

For long live monitoring with the infinite CoppeliaSim cycle, use continuous mode. In this mode the collector does not stop at the first `cycle_complete`; it runs until `-Duration` expires or until Ctrl+C:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\pak\run_pak_demo.ps1 -RunId final_scene_continuous_01 -Duration 21600 -Continuous
```

## Manual Run Commands

Start storage:

```powershell
cd C:\Users\egork\Desktop\coppelia_dpilom\infra\pak
docker compose up -d
```

Collect telemetry with live InfluxDB export:

```powershell
cd C:\Users\egork\Desktop\coppelia_dpilom
powershell -ExecutionPolicy Bypass -File .\scripts\coppeliasim\python\run_final_scene_full_collection.ps1 -RunId final_scene_full_03 -Duration 1800 -InfluxLive -LiveAnalytics
```

The helper stops on the short `cycle_complete` phase with `--stop-delay 0.2`. With `-LiveAnalytics`, the lower Grafana panels are filled during the run, not only after post-processing.

Continuous manual collection:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\coppeliasim\python\run_final_scene_full_collection.ps1 -RunId final_scene_continuous_01 -Duration 21600 -InfluxLive -LiveAnalytics -Continuous
```

Run analytics and export after collection:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\data_pipeline\run_pipeline_and_export.ps1 -InputPath data\telemetry\vkr_raw\final_scene_full_03.jsonl -RunId final_scene_full_03
```

## Running On Another Computer

Required software:

- Windows or macOS;
- PowerShell 7+ on macOS, command name `pwsh`;
- CoppeliaSim / CoppeliaSim Edu with ZMQ Remote API;
- Python 3 with `pip`;
- Docker Desktop;
- copied project folder `coppelia_dpilom`.

Install Python packages from the project root:

```powershell
python -m pip install -r requirements-pak.txt
```

On macOS, a virtual environment is recommended:

```bash
cd ~/coppelia_dpilom
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements-pak.txt
```

The collector searches common Windows and macOS CoppeliaSim locations automatically. If CoppeliaSim is not installed in a standard folder, set `COPPELIASIM_ZMQ_CLIENT_PATH` to the CoppeliaSim ZMQ client source directory.

Windows PowerShell example:

```powershell
$env:COPPELIASIM_ZMQ_CLIENT_PATH="C:\Path\To\CoppeliaSimEdu\programming\zmqRemoteApi\clients\python\src"
```

macOS shell example:

```bash
export COPPELIASIM_ZMQ_CLIENT_PATH="/Applications/CoppeliaSimEdu.app/Contents/Resources/programming/zmqRemoteApi/clients/python/src"
```

Then run on Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\pak\run_pak_demo.ps1 -RunId final_scene_demo_01
```

Or run on macOS from the project root:

```bash
pwsh -ExecutionPolicy Bypass -File ./scripts/pak/run_pak_demo.ps1 -RunId mac_scene_demo_01 -Python python3
```

Manual macOS sequence:

```bash
docker compose -f ./infra/pak/docker-compose.yml up -d
pwsh -ExecutionPolicy Bypass -File ./scripts/coppeliasim/python/run_final_scene_full_collection.ps1 -RunId mac_scene_live_01 -Duration 1800 -InfluxLive -LiveAnalytics -Python python3
pwsh -ExecutionPolicy Bypass -File ./scripts/data_pipeline/run_pipeline_and_export.ps1 -InputPath data/telemetry/vkr_raw/mac_scene_live_01.jsonl -RunId mac_scene_live_01 -Python python3
```

## Current Status

The data and neural-network pipeline runs on the pred-final scene. The NIRS-8 Grafana screenshot run `nirs8_grafana_01` reached `cycle_complete`, was processed, and exported to InfluxDB/Grafana.

Use the Grafana dashboard during the live run for screenshots that include raw telemetry, HI/RUL, neural-network RUL, live prediction error, and periodically refreshed MAE/R2. Use the post-run export as the reproducible final evidence layer.
