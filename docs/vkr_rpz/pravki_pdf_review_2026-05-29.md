# Pravki PDF Review 2026-05-29

## Source

- Reviewed file: `вкр\правки.pdf`.
- Related current export: `вкр\ВКР 2026 Миронов Егор Максимович.pdf`, 98 pages.
- The correction review says the work became stronger after the previous pass, but still has visible critical issues.

## Confirmed Must-Fix Items

- Title page still has bad nested English quotes and a final period in the organization name: `ООО “Компания “Здоровая жизнь””.`.
- Abstract still has the grammatically wrong phrase: `формируется в объеме основную часть, список литературы и приложения формата А4`.
- Abstract still has wording `Оценку надёжности, как технической системы...`; should be smoothed.
- Conclusion still says `ГОСТ 34.602–89`; should be `ГОСТ 34.602–2020` or `ГОСТ 34.602–2020 с учетом преемственности ГОСТ 34.602–89`.
- Bibliography order/reference conflict remains visually in the PDF: [4] is ГОСТ 34.602-89, [5] is ГОСТ 34.602-2020, while chapter 3 discusses ГОСТ 34.602-2020 with [4]. Best correction: swap bibliography entries 4 and 5 and keep [4] for the active ГОСТ.
- Table 14 still uses `Глава 1...Глава 6` as results; replace with engineering deliverables.
- Chapter 6 has an unresolved frequency contradiction: full run duration `2059.05 s`, but formulas use `Tнабл = 23.6 s`, `472` samples and `20 Hz`.
- Chapter 5 states `25 Hz`, while chapter 6 factual collector frequency is `10.77 Hz`; add a note that `25 Hz` is the internal Lua/UI update target and `10.77 Hz` is the external Python collector average.
- Formula 48 renders as `10242`; should be `1024²`.
- Conclusion contains a detailed degradation/RUL calculation with `5.23 x 10-6`, `D = 0.052`, `HI = 0.948`, `RUL ≈ 114700` that is not clearly shown earlier; move it to chapter 6 or remove it from conclusion.

## Important But Lower Priority

- Appendix A is visually almost empty (`Презентация, 17 слайдов`). This conflicts with the user’s latest decision to keep Appendix A reserved/empty; treat as a norm-control risk rather than automatic correction.
- Section 2.5.1 still mentions `scikit-learn и XGBoost`; better clarify that scikit-learn is used for MLPRegressor and XGBoost remains a reserve/comparison tool.
- Chapter 6 reliability should clarify that strict robot reliability cannot be calculated without real failure/repair statistics; current values mostly characterize diagnostic-contour operability.
- Economic assumption `3 events/year` should be explicitly called a calculation assumption requiring enterprise statistics.
- Table 21 mentions a confidence interval for RUL, but confidence intervals are not implemented; replace with `прогнозное значение RUL`.
- Section 4.11 may overstate containerization of collector/ml-service if only InfluxDB/Grafana are actually containerized; write it as project/future structure unless implemented.
- Figure 1 is visually low-quality; replacing/perrawing it would improve presentation.
- Figure 12 is crowded; improve caption or simplify if time permits.
- Clarify that `mпал = 12 kg` is the empty pallet mass.
- Clarify that `Nобъект = 16` counts transferred objects, while `Nсозд = 17` includes the pallet.

## Recommended Priority

1. Fix title page and abstract.
2. Fix ГОСТ 34.602 references and conclusion wording.
3. Fix table 14.
4. Fix frequency formulas/explanations and formula 48.
5. Remove or move the new conclusion-only RUL calculation.
6. Add reliability/economics limitation paragraphs.
7. Decide whether to keep Appendix A reserved or fill it with a slide list despite the previous decision.
