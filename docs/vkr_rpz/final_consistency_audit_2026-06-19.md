# Final VKR Consistency Audit - 2026-06-19

Working DOCX:

- `вкр\ВКР 2026 Миронов Егор Максимович.docx`

Generated audit artifact:

- `scratch\vkr_consistency_audit_20260619.json`

Structural checks:

- DOCX ZIP integrity passed.
- Main formulas are continuous: `(1)` ... `(86)`, no missing labels and no duplicate labels.
- Main table captions are continuous: `1` ... `44`, no gaps or duplicates.
- Main figure captions are continuous: `1` ... `19`, no gaps or duplicates.
- Appendix captions are continuous: `Таблица Б.1-Б.3`, `В.1-В.3`, `Г.1-Г.3`, `Д.1-Д.3`, `Листинг Ж.1-Ж.4`.
- Tables are normalized to `12 pt`; heading runs above `18 pt` were not detected.
- Broken Word reference text was not found.
- Old scene names `final_scena` and `pred_final` were not found; `vkr_scena.ttt` is present.

Numerical consistency:

- Local data and DOCX numbers agree for the main claims:
  - `22174` raw telemetry packets;
  - `88696` normalized rows;
  - `600` feature rows;
  - `192000` degradation/RUL rows and neural predictions;
  - train/test split `153600` / `38400`;
  - average test metrics `MAE = 1,441`, `RMSE = 2,144`, `R2 = 0,988`;
  - observation interval `2059,05 s`, average step `0,0929 s`, frequency `10,77 Hz`;
  - cycle duration about `187 s`, productivity `231` packages/h, `14,55` t/h, `58212` t/year;
  - economic effect `450000` rub.
- Old stale values were not found in the DOCX text/tables: `17920`, `14336`, `3584`, `1,173`, `1,442`, `0,994`, `23,6 / 472`, old `20 Hz`, `final_scena`, `pred_final`.

Open correction items:

1. Fix stale figure references:
   - text says telemetry graphs are on `рисунке 3`, but the actual caption is `Рисунок 5`;
   - text says IDEF0 decompositions are on `рисунках 5 и 6`, but the actual captions are `Рисунок 7` and `Рисунок 8`.
2. Fix appendix table `Г.2` old formula references:
   - `Формулы (80)-(84)`;
   - `Формулы (74)-(76)`;
   - `Формулы (85)-(87)`;
   - `Формула (106)`.
   Current formula numbering ends at `(86)`, so `(87)` and `(106)` are invalid.
3. Visually verify the metric formulas `(49)-(51)` in Word/PDF. XML contains accent objects for predicted `RUL`, but plain text extraction collapses actual `RUL_i` and predicted `hat(RUL_i)` into identical text.
4. Visually verify formula `(70)`. Text extraction shows `mini`, but XML confirms `min` has subscript `i`; this is likely only an extraction artifact.

Render status:

- `render_docx.py` in sandbox failed because it could not create/use the LibreOffice temporary profile.
- Escalated render failed because LibreOffice/`soffice` is not installed or not on PATH.
- Final visual QA still requires opening the DOCX/PDF in Microsoft Word and checking page breaks, captions, formulas, tables and appendix references.
