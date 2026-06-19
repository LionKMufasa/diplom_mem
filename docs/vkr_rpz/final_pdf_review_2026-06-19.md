# Review Of Pred-Final VKR PDF - 2026-06-19

Reviewed PDF:

- `C:\Users\egork\Desktop\Итоговые_файлы_Миронов_2026-06-18_1644\01_Документы_для_сдачи\ВКР_нормоконтроль\Миронов Е.М. РК9-83Б - ВКР.pdf`

Generated analysis artifacts:

- `scratch/final_vkr_pdf_analysis_20260619/pdf_text.txt`
- `scratch/final_vkr_pdf_analysis_20260619/analysis.json`
- `scratch/final_vkr_pdf_analysis_20260619/quick_report.txt`

## Stable Findings

- PDF has 124 pages.
- Numeric main-text tables are continuous: `Таблица 1` ... `Таблица 44`, no gaps or duplicates detected in extracted text.
- Figures are continuous: `Рисунок 1` ... `Рисунок 19`, no gaps or duplicates detected.
- Sources `1` ... `44` all have in-text references.
- Old scene names such as `final_scena` / `pred_final` were not found; final scene name `vkr_scena.ttt` is preserved.
- No broken-reference text like `Ошибка! Источник ссылки не найден` was detected.

## Main Issue: Repeated Formulas

The user correctly noted that formulas are often repeated. The issue is mostly not numbering continuity, but repeated introduction of the same mathematical dependencies as if they were new formulas in later chapters.

Repeated formula bodies detected:

- `Kпред = Nсвоевр / Nпред`: formulas `(18)`, `(29)`, `(63)`, `(109)`.
- Observation vector `d_k = {t_k, c_k, s_k, i, q_i, omega_i, a_i, M_i, event_k}`: formulas `(19)`, `(30)`, `(43)`.
- Normalization `x_norm = (x - x_min)/(x_max - x_min)`: formulas `(20)`, `(84)`.
- Feature vector `F_W = {mean, max, std, rms, slope, E}`: formulas `(21)`, `(31)`.
- `slope(x) = [x(t0 + Delta t) - x(t0)] / Delta t`: formulas `(22)`, `(83)`.
- Update-period condition `Tобн <= Delta tдоп`: formulas `(24)`, `(36)`.
- Availability coefficient `Kготовн = Tработ/(Tработ + Tпрост)`: formulas `(26)`, `(27)`.
- Energy feature based on `|M_i(t_k) * omega_i(t_k)| * Delta t`: formulas `(32)`, `(52)`.
- RUL model `RUL_hat = g(F_W, HI, theta)`: formulas `(34)`, `(87)`.
- Maintenance decision rule `A_TO = 1 ...`: formulas `(94)`, `(106)`.
- MAE metric: formulas `(15)`, `(61)`.
- Weighted diagnostic/risk sum: formulas `(10)`, `(33)`.

Some apparent duplicate formula labels `(76)`, `(84)`, `(87)`, `(106)`, `(112)` in automated extraction are false positives from appendix/table text such as `Формулы (80)-(84)` or ordinary text references, not necessarily actual duplicate labels.

## Recommended Cleanup Strategy

- Keep base mathematical definitions once, preferably in chapter 2 or chapter 4 depending on meaning.
- In chapter 3 technical assignment, replace most repeated formula blocks with prose requirements and references to already introduced formulas.
- In chapter 5 implementation, do not repeat mathematical definitions; write that the implementation calculates features/normalization/RUL according to earlier formulas.
- In chapter 6, keep only numerical calculations and result formulas that are genuinely used for approbation; refer to earlier formula numbers for common metrics and rules.
- After deleting repeated formula paragraphs, renumber formulas and update all text references, appendix table references, and table/figure captions if Word fields shift.

## Other Structure Notes

- Current contents show `4.2. Создание цифровой модели РТК` and `5.2. Реализация цифровой модели в CoppeliaSim`. This is acceptable only if chapter 4 describes the design of the model and chapter 5 describes actual STEP -> SolidWorks -> URDF -> CoppeliaSim realization. To match the accepted plan better, rename `4.2` to a project/design wording such as `Проект цифровой модели РТК`.
- Main text reaches `Заключение` on page 98 and `Список использованных источников` on page 100; appendices start on page 105. If the department strictly expects about 70 pages of main text, volume should be checked manually against the latest requirement.
- The synthetic-degradation limitation is present, and this is good for defense risk.
