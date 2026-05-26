# VKR RPZ Final Insert/Delete Map

Last updated: 2026-05-22

Purpose: concrete map for replacing signed figure/table placeholders in the VKR explanatory note after the practical PAK work.

Execution status:

- 2026-05-22: executed for the working VKR DOCX. Remaining signed `ВСТАВКА` markers after cleanup: `0`.
- The final pass inserted more than the originally recommended `7-10` evidence items because the user asked to fill all remaining insertions and add concrete calculations. Manual Word page-count review is still needed to confirm the final main-text volume.
- Final formula sequence after removing repeated chapter 6 formulas: `(1)` ... `(114)`.

Working DOCX:

- `C:\Users\egork\Desktop\coppelia_dpilom\вкр\ВКР 2026 Миронов Егор Максимович.docx`

Current page budget:

- Word page count before inserting practical figures/tables: about `63`.
- Main RPZ target: about `70` pages excluding appendices.
- Therefore the main text should receive only high-value evidence: about `7-10` figures/tables. Secondary screenshots, repeated diagrams, large logs, code listings, and detailed CSV fragments should go to appendices.

## Main Practical Evidence Baseline

Use `long_live_01` as the current strongest processed evidence set unless the user decides to rerun and rename a final VKR run.

- raw file: `data\telemetry\vkr_raw\long_live_01.jsonl`;
- raw packets: `22174`;
- normalized rows: `88696`;
- valid rows: `88696`;
- `K_data = 1.000`;
- `K_phase = 1.000`;
- phase count: `14`;
- average sampling interval: `0.0929 s`;
- estimated sampling frequency: `10.77 Hz`;
- feature rows: `56`;
- degradation scenario rows: `17920`;
- RUL estimate rows: `17920`;
- neural-network prediction rows: `17920`;
- neural-network average test metrics: `MAE = 1.173`, `RMSE = 1.442`, `R2 = 0.994`.

Keep `nirs8_grafana_01` as a secondary dashboard/screenshot run if needed:

- raw packets: `2131`;
- normalized rows: `8524`;
- valid rows: `8524`;
- `K_data = 1.000`;
- `K_phase = 1.000`;
- feature rows: `52`;
- RUL estimate rows: `16640`;
- NN metrics: `MAE = 2.423`, `RMSE = 2.911`, `R2 = 0.977`;
- export lines: `44035`.

Do not use `final_scene_full_02` as the main final evidence because it did not reach `cycle_complete`; it may be mentioned only as a debugging/intermediate run.

## Figures To Insert

Core files already generated:

- `reports\figures\vkr_practice\torque_rms_by_axis.svg`
- `reports\figures\vkr_practice\hi_curves_motor1.svg`
- `reports\figures\vkr_practice\rul_actual_predicted_s3_motor1.svg`
- `reports\figures\vkr_practice\rul_nn_actual_predicted_s3_motor1.svg`
- `reports\figures\vkr_practice\pak_dashboard_summary.svg`

Screenshots still useful to capture manually:

- one CoppeliaSim screenshot of the final scene / completed palletizing cycle;
- one `Motor dynamics monitor` screenshot;
- one actual Grafana dashboard screenshot, if better than `pak_dashboard_summary.svg`.

## Delete Or Replace By Chapter

### Chapter 1

- Delete placeholder `1.8` about future `HI(t)` graph. Do not duplicate the practical HI graph in chapter 1; place the real HI plot in chapter 5 or 6.

### Chapter 2

Delete these placeholders because they duplicate later practical evidence or add low-value bulk:

- `2.3` IDEF0 model;
- `2.Б` feature-vector calculation;
- `2.В` telemetry-volume table;
- `2.4` sequence diagram;
- `2.Г` architecture-choice matrix;
- `2.5` technology-stack scheme;
- `2.6` RUL graph;
- `2.7` future Grafana mockup;
- `2.Д` availability calculation.

Keep/replace:

- `2.А`: replace with a compact target/factual metrics table.
- `2.1`: optional; delete if the technical architecture scheme is inserted in chapter 4. If retained, use only one compact architecture scheme.
- `2.2`: optional; replace with a small normalized telemetry fragment if no telemetry sample is inserted in chapter 5.

### Chapter 3

Delete:

- `3.А` source-document table;
- `3.Б` future target calculation;
- `3.1` object contour figure if the scene screenshot is inserted in chapters 5-6;
- `3.2` dashboard mockup;
- `3.3` development-stage diagram;
- `3.4` environment-readiness screenshot;
- `3.Д` documentation-kit table.

Keep/replace:

- `3.Г`: replace with a compact acceptance-test protocol table using the implemented components.

### Chapter 4

Keep/replace:

- `4.1`: insert the final PAK technical architecture scheme.
- `4.2`: insert either a CoppeliaSim scene screenshot, or delete if the only scene screenshot is reserved for chapter 6.
- `4.3`: insert `hi_curves_motor1.svg` if it is not used in chapter 5.
- `4.В`: replace with an actual deterministic-vs-neural RUL model comparison table.

Delete:

- `4.А` telemetry-volume calculation table;
- `4.Б` feature-vector calculation placeholder;
- `4.4` HI/RUL graph if the RUL graph is inserted in chapter 6;
- `4.5` storage-screenshot placeholder;
- `4.6` dashboard mockup;
- `4.7` container-deployment scheme.

### Chapter 5

Keep/replace:

- file-composition placeholder: replace with a compact table of implemented scripts and outputs.
- CoppeliaSim scene screenshot: keep one screenshot if it is not used in chapter 6.
- degradation placeholder: insert `hi_curves_motor1.svg`.
- telemetry fragment: insert a small CSV/JSONL table from real telemetry.
- signal-graph placeholder: insert `torque_rms_by_axis.svg`.
- feature table: insert a small feature table by phase/axis.
- `Motor dynamics monitor`: insert one screenshot.
- interface placeholder: delete here if Grafana is inserted in chapter 6.
- integration-test placeholder: replace with an implementation status table.

Delete:

- cyclegram placeholder;
- separate `M_rms`/energy trend placeholder unless a new graph is generated;
- training-flow diagram;
- duplicate RUL graph if chapter 6 contains the final NN RUL graph;
- ER/storage scheme;
- duplicate CSV/export sample.

### Chapter 6

Keep/replace:

- actual runs table;
- completed-cycle screenshot if not used in chapter 5;
- RUL metrics table;
- final NN RUL graph `rul_nn_actual_predicted_s3_motor1.svg`;
- Grafana dashboard screenshot or `pak_dashboard_summary.svg`;
- factual indicators table: `K_data`, `K_phase`, `K_pred`, `T_update`;
- compact economic calculation table with explicit assumptions.

Delete:

- methodology scheme;
- duplicate motor-dynamics graph if inserted in chapter 5;
- duplicate `Motor dynamics monitor` screenshot if inserted in chapter 5;
- final comparison diagram; replace it with a compact text/table comparison if needed.

## Ready-To-Insert Tables

### Table: Target And Actual Quality Indicators

| Indicator | Target value | Actual value | Source |
| --- | ---: | ---: | --- |
| Valid telemetry ratio `K_data` | at least `0.95` | `1.000` | `long_live_01` validation |
| Phase-linking ratio `K_phase` | at least `0.95` | `1.000` | `long_live_01` validation |
| Sampling frequency | at least `10 Hz` | `10.77 Hz` | normalized telemetry |
| NN RUL MAE | no more than `3 cycles` | `1.173 cycles` | test split |
| NN RUL RMSE | no more than `4 cycles` | `1.442 cycles` | test split |
| NN RUL `R2` | at least `0.90` | `0.994` | test split |

### Table: Implemented Script Composition

| Component | File | Result |
| --- | --- | --- |
| Telemetry collector | `scripts\coppeliasim\python\collect_final_scene_telemetry.py` | JSONL telemetry from CoppeliaSim |
| Normalization | `scripts\data_pipeline\normalize_telemetry.py` | unified long CSV table |
| Validation | `scripts\data_pipeline\validate_telemetry.py` | `K_data`, `K_phase`, rejected rows |
| Feature generation | `scripts\data_pipeline\build_features.py` | phase/axis diagnostic features |
| Degradation scenarios | `scripts\data_pipeline\simulate_degradation.py` | scenarios `S0..S3` |
| RUL estimation | `scripts\data_pipeline\estimate_rul.py` | deterministic RUL estimates |
| Neural RUL model | `scripts\data_pipeline\train_rul_mlp.py` | predictions, metrics, saved model |
| Live analytics | `scripts\data_pipeline\live_analytics_to_influx.py` | rolling HI/RUL/NN points for Grafana |
| InfluxDB export | `scripts\data_pipeline\export_to_influx.py` | time-series measurements |
| Demo launcher | `scripts\pak\run_pak_demo.ps1` | one-command practical demo |

### Table: Actual Runs

| Run | Purpose | Raw packets | Valid rows | Phases | `cycle_complete` | Status |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `long_live_01` | main processed evidence | `22174` | `88696` | `14` | yes | use as main factual run |
| `nirs8_grafana_01` | Grafana/screenshot run | `2131` | `8524` | `13` | yes | use as secondary visual evidence |
| `final_scene_full_02` | debugging run | `1791` | `7164` | `10` | no | do not use as final proof |

### Table: RUL Model Comparison

| Model | MAE, cycles | RMSE, cycles | `R2` | Comment |
| --- | ---: | ---: | ---: | --- |
| Deterministic baseline | `6.335` | `7.883` | `0.807` | usable for preliminary estimate |
| Neural model `MLPRegressor` | `1.173` | `1.442` | `0.994` | selected as main prediction model |

### Table: NN RUL Metrics By Scenario

| Scenario | Degradation rate | MAE, cycles | RMSE, cycles | `R2` |
| --- | ---: | ---: | ---: | ---: |
| `S0` | `0.00` | `0.414` | `0.521` | `1.000` |
| `S1` | `0.08` | `2.409` | `2.922` | `0.983` |
| `S2` | `0.20` | `1.110` | `1.341` | `0.997` |
| `S3` | `0.35` | `0.759` | `0.985` | `0.998` |

### Table: Final Indicators

| Indicator | Meaning | Actual value |
| --- | --- | ---: |
| `K_data` | share of valid telemetry rows | `1.000` |
| `K_phase` | share of phase-linked telemetry rows | `1.000` |
| `K_pred` | prediction quality by test `R2` | `0.994` |
| `T_update` | live analytics update period | `5 s` |
| `f_s` | effective telemetry sampling frequency | `10.77 Hz` |

## Ready-To-Insert Figure Captions

- `Рисунок X - Техническая архитектура программно-аппаратного комплекса предиктивного обслуживания`.
- `Рисунок X - Цифровая модель роботизированной ячейки паллетизации в CoppeliaSim`.
- `Рисунок X - Среднеквадратический момент по контролируемым осям робота`.
- `Рисунок X - Изменение индекса технического состояния HI для сценариев деградации`.
- `Рисунок X - Сравнение фактического и прогнозного RUL для нейросетевой модели`.
- `Рисунок X - Сводная панель мониторинга ПАК предиктивного обслуживания`.
- `Рисунок X - Окно Motor dynamics monitor в CoppeliaSim`.

## Text Corrections

Replace future-tense wording in chapters 5-6:

- `будет реализовано` -> `реализовано`;
- `после получения экспериментальных данных` -> `по результатам контрольного прогона`;
- `макет панели` -> `панель мониторинга Grafana`;
- `будущий интерфейс` -> `реализованный интерфейс мониторинга`;
- `должен рассчитывать` -> `рассчитывает`;
- `будет использоваться` -> `используется`.

Avoid exposing `nirs8` in final VKR prose unless it is clearly named as a screenshot/control run. For the final version, prefer neutral wording: `контрольный прогон ПАК`, `файл телеметрии`, `экспериментальный прогон`.
