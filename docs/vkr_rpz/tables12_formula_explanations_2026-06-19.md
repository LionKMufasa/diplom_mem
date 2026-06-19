# Tables 12 Pt And Formula Explanations - 2026-06-19

Working DOCX:

- `вкр\ВКР 2026 Миронов Егор Максимович.docx`

Scripts used:

- `scripts\apply_vkr_tables12_formula_explanations_20260619.py`
- `scripts\fix_vkr_formula_explanation_placement_20260619.py`
- `scripts\fix_vkr_key_id_explanation_encoding_20260619.py`

Backups created:

- `вкр\ВКР 2026 Миронов Егор Максимович.backup_before_tables12_formula_explanations_20260619_024731.docx`
- `вкр\ВКР 2026 Миронов Егор Максимович.backup_before_formula_explanation_placement_20260619_024939.docx`
- `вкр\ВКР 2026 Миронов Егор Максимович.backup_before_key_id_encoding_fix_20260619_025140.docx`

## What Changed

- All table text runs were forced to `Times New Roman`, `12 pt`.
- Formula explanations were expanded or normalized across the document so variables are explained near their first relevant use.
- Added or improved explanations for grouped formulas covering:
  - phase/axis moments and energy;
  - reliability/availability and downtime-loss indicators;
  - Health Index, limit state, RUL, and maintenance recommendation;
  - observation records, normalization, feature vectors, slope and window features;
  - software-choice score, requirement inequalities, economic effect, and payback;
  - degradation scenario parameters and metric formulas;
  - InfluxDB key/value/time-series identifiers.
- Corrected a misplaced degradation explanation so the `alpha_i,kr` explanation follows the degradation formulas, not the sampling-frequency formula.
- Restored correct Russian text for the `key/value/id` explanations after a temporary encoding artifact was detected.

## Checks

- DOCX ZIP integrity: passed.
- Formula labels: `92`, continuous `(1)` ... `(92)`, no gaps, no duplicates.
- Tables: `64`.
- Table runs checked: `2030`; non-12-pt table runs: `0`.
- Broken Word reference text: not found.
- Triple-question-mark encoding artifacts: not found.
- Double formula-label artifacts: not found.
- Visual render QA remains blocked because LibreOffice/`soffice` is not available in the current environment.

## Manual Next Step

- Open the DOCX in Microsoft Word.
- Update fields/TOC if needed.
- Save a fresh PDF.
- Visually inspect wide tables and formula-explanation paragraphs after Word pagination.
