# Formula Explanation Subscripts - 2026-06-19

Working DOCX:

- `вкр\ВКР 2026 Миронов Егор Максимович.docx`

Script:

- `scripts\fix_vkr_formula_explanation_subscripts_20260619.py`

Backup:

- `вкр\ВКР 2026 Миронов Егор Максимович.backup_before_formula_explanation_subscripts_20260619_030407.docx`

## What Changed

- Converted mathematical variables in formula explanations from underscore notation to real Word subscript formatting.
- Scope was limited to explanatory paragraphs starting with `где ...`, so code listings, file names, CSV field names, scene paths and identifiers in tables were not mass-converted.
- Examples of affected notation:
  - `F_i,s`, `E_i,s`, `P_i(t)`, `M_i(t)`, `ω_i(t)`;
  - `d_k`, `t_k`, `q_i`, `event_k`;
  - `x_min`, `x_max`, `F_W`;
  - `α_i(N)`, `M_i,deg(t)`, `T_s,deg`;
  - `RUL_i`, `D_lim`, `HI_i(N)`, `W_N,s`;
  - `I_RUL`, `I_UI`.
- Also normalized compact formula-designation indices inside the same explanation paragraphs, such as `HIкр`, `Nкр`, `AТО`, `Kдан`, `Kфаз`, `Sапр`, and `Iсц`.

## Checks

- Changed explanatory paragraphs: `26`.
- Subscript conversions: `119`.
- Remaining mathematical underscore tokens in ordinary paragraphs: `0`.
- Remaining underscores in paragraphs starting with `где ...`: `0`.
- Real Word/XML subscript runs in explanation paragraphs: `159`.
- Formula labels remain continuous: `(1)` ... `(92)`, no gaps, no duplicates.
- Table text remains `12 pt`: table runs checked `1495`, non-12-pt table runs `0`.
- Broken Word reference text: not found.
- `???` encoding artifacts: not found.
- Visual render QA remains blocked:
  - sandbox render failed on temporary-profile permissions;
  - escalated render failed because LibreOffice/`soffice` is unavailable.

## Manual Next Step

- Open the DOCX in Word and visually check a few formula explanation paragraphs, especially the first one with `F_i,s`.
- Update fields/TOC and save a fresh PDF after visual inspection.
