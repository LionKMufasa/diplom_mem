# Formula Logic Cleanup - 2026-06-19

Working DOCX:

- `вкр\ВКР 2026 Миронов Егор Максимович.docx`

Backup before the final successful pass:

- `вкр\ВКР 2026 Миронов Егор Максимович.backup_before_formula_logic_cleanup_20260619_023004.docx`

Script:

- `scripts\apply_vkr_formula_logic_cleanup_20260619.py`

Report:

- `scratch\formula_logic_cleanup_20260619_report.txt`

## What Changed

- Repeated formula bodies were removed or replaced with references to the first authoritative definition.
- Formula count was reduced to `92`.
- Formula numbering is continuous: `(1)` ... `(92)`.
- No duplicate formula labels or missing formula numbers were detected after the pass.
- No repeated formula bodies were detected after normalization.
- Early MAE/RMSE formulas in chapter 2 were replaced with a prose reference to section `4.8.2`.
- Section `4.8.2` now contains the authoritative metric formulas:
  - MAE - formula `(49)`;
  - RMSE with square root - formula `(50)`;
  - `R²` - formula `(51)`.
- Chapter 3 no longer restates base definitions. It references:
  - observation vector - formula `(16)`;
  - feature vector - formula `(18)`;
  - HI - formula `(9)`;
  - RUL regression relation - formula `(14)`;
  - update-period requirement - formula `(21)`.
- Chapter 5 no longer repeats slope, normalization, generic RUL regression and metric formulas. It references the authoritative definitions instead.
- Chapter 6 no longer repeats the warning rule and timely-warning coefficient. It references:
  - warning rule - formula `(75)`;
  - timely-warning coefficient - formula `(15)`;
  - RUL target formulas - `(70)` and `(71)`;
  - metrics - `(49)` ... `(51)`.
- Added explanations of variables for:
  - `Kпред`;
  - normalization, feature vector and `slope`;
  - MAE/RMSE/R²;
  - `Pпотерь`;
  - `Kдан` and `Kфаз`;
  - `Qv`.

## Checks

- DOCX ZIP integrity: passed.
- Formula sequence: `1-92`, no gaps, no duplicates.
- Double-label artifacts like `(38)(27)`: not found.
- Repeated formula bodies: not found.
- In-text source references: `1-44`, no missing source numbers.
- Old scene names `final_scena` / `pred_final`: not found.
- Broken Word reference text: not found.
- Visual render QA was attempted:
  - sandbox render failed on temporary-profile permissions;
  - escalated render failed because `soffice` / LibreOffice is not available.

## Manual Next Step

- Open the DOCX in Microsoft Word.
- Update all fields/TOC if needed.
- Save a fresh PDF.
- Visually inspect formulas `(49)` ... `(51)`, `(70)` ... `(75)`, `(87)` ... `(92)` and the page breaks around chapters 4-6.
