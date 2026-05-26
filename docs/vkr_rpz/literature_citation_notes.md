# VKR Literature Citation Notes

Last updated: 2026-05-07

## Purpose

Working note for adding literature-backed references into `ВКР 2026 Миронов Егор Максимович.docx`.

## Current Citation Rule After 2026-05-06 Correction

- In-text numeric citations must point to one source only and include a page number: `[8, с. 100]`.
- Avoid grouped citation brackets in the main text, e.g. do not use `[7-12]`, `[4, 33]`, or `[1, 2]`.
- Current bibliography order in the working DOCX:
  1. ГОСТы: entries `1-5`;
  2. Russian-language literature: entries `6-11`;
  3. other sources: entries `12-45`.
- Source 6 from the previous pass, `Галахарь А.С. ... курс лекций`, was removed on 2026-05-07 at the user's request.
- Structural audit after chapter 5: `47` valid citation mentions before bibliography, `0` invalid citation-like brackets, maximum citation number `45`.
- Strict chapter 3 source: [[docs/vkr_rpz/chapter3_tz_gost_strict]].

## Russian-Language Literature Added

- `ВКР\литература\ГОСТ 34.602-89.pdf` - official ГОСТ 34.602-89 PDF downloaded from Wikimedia Commons.
- `ВКР\литература\Русская литература\03_Zadiran_Scherbakov_Sai_2023_RUL_malaya_vyborka.pdf` - RUL definition and data-driven / model-based methods, useful pages: `с. 100-101`.
- `ВКР\литература\Русская литература\06_Lavrischeva_Zelenov_Pakulin_2019_metody_ocenki_nadezhnosti.pdf` - reliability assessment, useful pages: `с. 95`, `с. 97`, `с. 99`.
- `ВКР\литература\Русская литература\08_Ravin_Hruckii_2018_engineering_methods_RUL_equipment.pdf` - engineering methods for RUL and time series, useful pages: `с. 33-35`.
- `ВКР\литература\Русская литература\09_Vlasov_Grigoryev_Krivoshein_2018_PdM_wireless_sensor_networks.pdf` - predictive maintenance definition and monitoring, useful pages: `с. 26-28`.
- `ВКР\литература\Русская литература\10_Qoibagarov_2025_PdM_ML.pdf` - ML-based predictive maintenance, useful pages: `с. 121-123`.
- `ВКР\литература\Русская литература\11_Starodubtseva_Gusev_2012_RUL_detali_mashin.pdf` - RUL for structures and machine parts, useful bibliography page range: `с. 355-360`.

## ГОСТ 34.602-89 / ГОСТ 34.602-2020

- Source PDF: `C:\Users\egork\Downloads\Лекция 5.2 - ТЗ по ГОСТ 34.602-89.pdf`.
- Key point: ГОСТ 34.602-89 defines the technical specification for automated systems as the main document that determines requirements and the order of system creation and acceptance.
- Key structure extracted from the PDF:
  - общие сведения;
  - назначение и цели создания системы;
  - характеристика объектов автоматизации;
  - требования к системе;
  - состав и содержание работ по созданию системы;
  - порядок контроля и приемки системы;
  - требования к подготовке объекта автоматизации к вводу системы;
  - требования к документированию;
  - источники разработки.
- Use in RPZ:
  - chapter 3 `Техническое задание`;
  - citations use one source per bracket, e.g. `[4, с. 1]` for ГОСТ 34.602-89 where page support is needed.

## Reliability Standards

- ГОСТ 27.002-2015: terms and definitions for reliability.
- ГОСТ 27.003-2016: composition and general rules for reliability requirements.
- ГОСТ 27.301-95: general provisions for reliability calculation.
- Use in RPZ:
  - definitions of technical state, reliability, failure, availability;
  - reliability requirements in chapter 3;
  - planned calculations in chapter 6.

## ABB Robot Sources

- ABB Product Manual IRB 660 and ABB IRB 660 datasheet support:
  - ABB IRB 660 is a palletizing robot;
  - IRB 660-180/3.15 and IRB 660-250/3.15 configurations;
  - reach/load basis for the selected robot.
- Use current citations `[12, с. ...]` for the ABB product manual and `[13, с. 1]` for the ABB datasheet after the source-6 removal.

## RUL / PHM Sources Already In Main Bibliography

- Kang et al. 2021, Taşcı et al. 2023, Baur et al. 2020, Gharib & Kovács 2023, Liu et al. 2025, Kumar et al. 2024.
- Key points:
  - RUL prediction is central to predictive maintenance;
  - PHM uses monitoring, diagnosis, prognosis, and maintenance decision support;
  - methods include model-based, data-driven, and hybrid approaches;
  - rotating machinery and machine-tool literature is relevant to robot drives, reducers, and bearings.
- Use individual current citations such as `[7, с. 100]`, `[7, с. 101]`, `[8, с. 34]`, `[9, с. 28]`, `[10, с. 121]`, and `[11, с. 355]`.

## Digital Twin Sources Already In Main Bibliography

- Kritzinger et al. 2018, Fuller et al. 2020, Sharma et al. 2022, Soori et al. 2023, Zhang et al. 2020.
- Key points:
  - digital twin / digital model concepts support virtual representation, simulation, data exchange, monitoring, and predictive maintenance;
  - manufacturing digital twins are commonly used for diagnosis, optimization, and decision support.
- Use individual current citations, e.g. `[20, с. 1016]` for Kritzinger et al. and `[41, с. 1]` for Xiao et al.

## New NIRS8 PDFs Added As Literature

- `[40]` Kumar, Khalid, Kim 2023: industrial robots include rotating machinery such as servo motors and gears; PHM of these components is important to reduce downtime.
- `[41]` Xiao et al. 2024: digital-twin-driven PHM for industrial assets supports reliability improvement and maintenance cost reduction.
- `[42]` Hu et al. 2019: RUL assessment of mechanical products includes physics-based and data-driven approaches; performance-variable observation is important when physical degradation is hard to observe directly.
- `[43]` Wang et al. 2021: bearing RUL estimation is critical for mechanical system reliability; health indicators and RUL estimation can be learned from degradation-related signal features.
- `[44]` Tanveer et al. 2026: real-time AI-driven PHM in robotics supports monitoring system health, detecting faults, and predicting failures before occurrence.
- `[45]` Wojtulewicz and Chaber 2025: industrial robot predictive maintenance can use process-data exchange, component consumption indicators, HMI visualization, MQTT, and IIoT interfaces.
