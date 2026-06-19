# Chapter 6 Formula Notation And Renumbering - 2026-06-19

## Scope

- Working DOCX: `вкр\ВКР 2026 Миронов Егор Максимович.docx`.
- User request: fix formulas and notation in chapter `6.2` and later, then verify/update formula numbering and in-text references.

## Applied Changes

- Rebuilt the formula blocks in chapter 6.2 and later as Word OMML equations, especially:
  - palletized object count formulas;
  - observation duration, average sampling step, and observed frequency;
  - data completeness and phase-label completeness coefficients;
  - downtime cost, annual effect, payback period;
  - final quality/risk summary score.
- Normalized explanatory notation in the same chapter range so mathematical variables use real Word subscripts instead of underscore-style notation where applicable.
- Renumbered formulas after the cleanup from the non-continuous set ending at `(92)` to a continuous sequence `(1)` ... `(86)`.
- Updated affected in-text formula references after the renumbering pass. Important chapter 6 references now point to:
  - RUL formulas `(69)`-`(70)`;
  - working regression formula `(14)`;
  - quality metrics `(49)`-`(51)`.

## Backups

- `вкр\ВКР 2026 Миронов Егор Максимович.backup_before_chapter6_formula_notation_20260619_044300.docx`
- `вкр\ВКР 2026 Миронов Егор Максимович.backup_before_formula_renumber_after_ch6_20260619_044639.docx`

## Scripts

- `scripts\fix_vkr_chapter6_formulas_notation_20260619.py`
- `scripts\renumber_vkr_formulas_after_chapter6_cleanup_20260619.py`

## Verification

- DOCX ZIP integrity passed: `zip_bad=None`.
- Formula count: `86`.
- Formula labels are continuous: `(1)` ... `(86)`.
- Missing formula labels: `0`.
- Duplicate formula labels: `0`.
- Detected formula-related text references all point to existing formula numbers.
- Broken Word reference text was not found.
- `???` encoding artifacts were not found.
- Render QA remains blocked in this environment:
  - sandbox render fails on temporary LibreOffice profile permissions;
  - escalated render fails because `soffice` / LibreOffice is unavailable.

## Next Manual Step

- Open the DOCX in Microsoft Word, update fields/TOC if needed, save a fresh PDF, and visually inspect chapter 6 formulas after Word layout pagination.
