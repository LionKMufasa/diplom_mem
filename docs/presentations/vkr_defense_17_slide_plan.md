# VKR Defense Presentation Plan

Last updated: 2026-05-26

## Source Deck

- Main visual/content base: `вкр/НИРС(7сем)/Презентация НИРС 2025 Миронов Егор Максимович.pptx`.
- The deck has 15 slides and should be treated as the source style/material base.
- Alternate duplicate: `вкр/НИРС(7сем)/Схемы и рисунки/Prezentatsia_NIRS_2025_Mironov_Egor_Maximovich.pptx`, 13 slides.
- Current VKR PPTX file `вкр/Презентация ВКР 2026 Миронов Егор Максимович.pptx` is currently zero bytes and should not be used as an editing base.

## Target

- Defense deck for VKR.
- Preferred slide count: 17.
- Maximum allowed slide count if needed after final polish: 20.
- Working mode: inherit NIRS-7 visual grammar, but strengthen the deck with VKR practical evidence.

## 17-Slide Spine

1. Title: development of a predictive maintenance system for robot-palletizer units on a bottling line.
2. Relevance: downtime risk, limits of scheduled maintenance, need for condition-based control.
3. Goal and tasks: object, subject, goal, development and approbation tasks.
4. Production line: place of palletizing in the technological process.
5. Palletizing cell: conveyors, pallet, packages, cardboard layers, robot role.
6. Research object: ABB IRB 660-180/3.15 and loaded mechanical/drive units.
7. Maintenance strategy: transition from scheduled maintenance to PdM and RUL-based decision support.
8. Digital model in CoppeliaSim: scene objects, palletizing cycle, phases, collected motion/torque data.
9. Telemetry and features: raw data, validation, phase segmentation, RMS/energy/slope/duration features.
10. System architecture: CoppeliaSim, telemetry collector, preprocessing, degradation/RUL model, InfluxDB, Grafana.
11. RUL estimation algorithm: feature matrix, labels, model, MAE/RMSE/R2 metrics.
12. Degradation model: health indicator, damage accumulation, degradation scenarios S0-S3.
13. Practical results: final dataset quality and cycle coverage; key values `K_data = 1.000`, `K_phase = 1.000`.
14. Forecast quality: NN RUL result `MAE = 1.173`, `RMSE = 1.442`, `R2 = 0.994`.
15. Operator monitoring: Grafana dashboard / PAK summary and update time `T_update = 0.093 s`.
16. Economic effect and conclusions: `450000 rub/year`, payback about `1.0` year, final VKR results.
17. Closing slide.

## Recommended Reuse From NIRS-7

- Keep the title, relevance, goal/tasks, production line, palletizing cell, object, architecture, RUL, reliability/economics, conclusion, and final slide patterns.
- Replace old generic reliability/economics proof with final VKR numeric evidence.
- Add new practical proof slides for CoppeliaSim model, telemetry/features, degradation scenarios, RUL metrics, and Grafana/PAK.

## Ready Proof Assets

- `reports/figures/vkr_practice_png/torque_rms_by_axis.png`
- `reports/figures/vkr_practice_png/hi_curves_motor1.png`
- `reports/figures/vkr_practice_png/rul_nn_actual_predicted_s3_motor1.png`
- `reports/figures/vkr_practice_png/pak_dashboard_summary.png`
