# NIRS-8 Current DOCX State

Last updated: 2026-05-22

## File

- Current final DOCX: `C:\Users\egork\Desktop\coppelia_dpilom\вкр\НИРС(8сем)\НИРС 2026 Миронов Егор Максимович.docx`
- Latest checked file size after the 2026-05-22 citation pass: `1094979` bytes.
- Draft source mirror from the earlier generated fill pass: [[docs/nirs8_rpz/nirs8_full_draft_source]]
- Earlier build script: `scripts\build_nirs8_report.py`
- Latest citation helper script: `scripts\update_nirs8_citations.py`

## Current Structure

- The user has manually finished the NIRS-8 report and left one final DOCX in `вкр\НИРС(8сем)`.
- Visible structure:
  - title page;
  - annotation;
  - contents;
  - introduction;
  - `1. Предпроектное обследование`;
  - `2. Концептуальное проектирование`;
  - `3. Техническое задание`;
  - `4. Техническое проектирование`;
  - `5. Рабочее проектирование`;
  - `6. Апробация`;
  - conclusion;
  - bibliography;
  - appendix.
- Chapter 3 follows the GOST-style technical-assignment structure at NIRS scale.
- The report contains signed placeholders/captions for figures and screenshots that the user can replace manually.

## Citation Pass 2026-05-22

- The current bibliography contains `22` entries.
- Russian-language sources are present near the beginning of the bibliography: ГОСТ 20911-89, ГОСТ 27518-87, Sokolov/Ivanov, Tsarev, Vlasov et al., Kuzin, and Farukshin et al.
- In-text citations were strengthened using the bibliography order already present in the final DOCX.
- Citation format follows the user's requirement: each bracket contains one source number only, e.g. `[9]`; no grouped citations such as `[9, 18]`.
- The stale ABB citation `[5]` was corrected to `[13]` because source 5 is now ГОСТ 20911-89.
- Structural citation audit after save:
  - citation mentions: `56`;
  - citation numbers used: `[4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 18, 22]`;
  - invalid bracket markers: `0`;
  - citation numbers above bibliography length: `0`;
  - old wrong ABB `[5]` citation: `0`.
- Backup before the citation pass: `C:\Users\egork\Desktop\coppelia_dpilom\вкр\НИРС(8сем)\_backups\НИРС 2026 Миронов Егор Максимович.backup_before_citations_20260522_040135.docx`.

## Content Coverage

- Task 1: chapter 1 covers robot construction and degradation-prone units.
- Task 2: chapter 2 covers wear mechanisms and durability factors.
- Task 3: chapters 4-5 cover the mathematical damage-accumulation model and calculation algorithm.
- Task 4: chapters 4-6 cover diagnostic features, limit-state criterion, HI/RUL, and approbation.
- Chapter 5 includes demonstration calculations for load, damage accumulation, Health Index, and residual life.

## Placeholders To Replace Later

- `Рисунок 1` - CoppeliaSim/7th-semester NIRS robotized palletizing cell scheme.
- `Рисунок 2` - IDEF0/context or diagnostic-feature formation scheme.
- `Рисунок 3` - decomposition/functional scheme.
- `Рисунок 4` - RMS torque plot by axes.
- `Рисунок 5` - Health Index plot.
- `Рисунок 6` - actual/predicted RUL plot.
- `Рисунок 7` - Grafana/PAK screenshot.
- Appendix material: presentation and optional telemetry/feature tables if needed.

## QA Status

- Structural DOCX/citation checks passed with `python-docx`.
- Visual PNG render QA is still blocked:
  - sandboxed render failed due temp-folder permissions;
  - escalated render failed because LibreOffice/`soffice` is not installed.
- Next safe QA step is manual opening in Microsoft Word to check page breaks, figure placeholders, and bibliography numbering.
