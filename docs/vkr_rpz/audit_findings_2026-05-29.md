# VKR RPZ Audit Findings 2026-05-29

## Context

- Working RPZ: `вкр\ВКР 2026 Миронов Егор Максимович.docx`.
- User asked to preserve the audit findings and then continue corrections.
- This note captures durable findings from the local audit and the external GPT-5.5 review.

## User Decisions After Audit

- Keep `vkr_scena.ttt` as the target final scene name in the RPZ; the scene will be finalized later.
- Correct the bibliography using the local `вкр\литература` folder, including Russian-language sources.
- In-text literature references should be without page numbers.
- Keep the contents/heading structure three-level.
- Keep Appendix A as currently planned.
- Do not broadly rephrase the work as a "software-simulation prototype"; only add a clarification that degradation is synthetic/model-based.
- Implement the remaining planned strengthening edits even if the RPZ volume increases.

## Confirmed Local Audit Findings

- Current PDF is about `95` pages; appendices start around page `86`.
- Current DOCX contains all bibliography references `1-45` in the text, but many in-text citations still include page numbers and should be simplified.
- The current DOCX uses `vkr_scena.ttt` in the text, but `scenes\vkr_scena.ttt` does not yet exist; this is accepted temporarily by the user.
- Current data issue:
  - `data\telemetry\vkr_validated\vkr_telemetry_validated.csv` has `88696` rows;
  - all rows currently have `cycle = 1`;
  - feature generation produces only `56` phase/axis rows;
  - phase durations become very large because equal phases across the long run are aggregated together.
- This data segmentation issue is the highest-priority technical correction before finalizing chapter 6 numbers.

## Bibliography Issues To Fix

- Source 15 in the current RPZ does not match the local PDF. It should describe:
  - Taşcı B., Omar A., Ayvaz S. Remaining useful lifetime prediction for predictive maintenance in manufacturing // Computers & Industrial Engineering. 2023. Vol. 184. Article 109566. DOI: 10.1016/j.cie.2023.109566.
- Source 17 in the current RPZ does not match the local PDF. It should describe:
  - Gharib H., Kovács G. A Review of Prognostic and Health Management (PHM) Methods and Limitations for Marine Diesel Engines: New Research Directions // Machines. 2023. Vol. 11. Article 695. DOI: 10.3390/machines11070695.
- Source 18 in the current RPZ does not match the local PDF. It should describe:
  - Liu Y., Wen J., Wang G. A comprehensive overview of remaining useful life prediction: From traditional literature review to scientometric analysis // Machine Learning with Applications. 2025. Vol. 21. Article 100704. DOI: 10.1016/j.mlwa.2025.100704.
- Source 19 in the current RPZ does not match the local PDF. It should describe:
  - Kumar S., Raj K.K., Cirrincione M., Cirrincione G., Franzitta V., Kumar R.R. A Comprehensive Review of Remaining Useful Life Estimation Approaches for Rotating Machinery // Energies. 2024. Vol. 17. Article 5538. DOI: 10.3390/en17225538.

## RPZ Strengthening Items

- Add an explicit limitation: degradation scenarios `S0-S3` are synthetic/model-based and validate the algorithmic contour, not industrial accuracy on real failure histories.
- Keep the current system wording, but avoid overstating industrial deployment.
- Align chapter 4/5/6 around the actual model used (`MLPRegressor`) or add an actual comparison table if Random Forest/XGBoost outputs are generated.
- Strengthen reliability/economics with a compact before/after availability and downtime comparison.
- Add or expand an FMEA-style table for critical robot-palletizer faults.
- Add a table of industrial/cell source assumptions if it does not overload the chapter.
- Add an InfluxDB/Grafana measurement schema table.
- Add a compact reproducibility/software-environment table.

## Formatting And Norm Control Items

- Keep three-level contents per latest user decision.
- Keep Appendix A per latest user decision.
- Remove page references from in-text citations.
- Clean obvious wording issues in the abstract/referral text:
  - "формируется в объеме основную часть" should become a normal sentence;
  - remove unnecessary comma in "Оценку надёжности, как технической системы";
  - normalize `motor1...motor4`, `S0...S3`, and scientific notation where feasible.

## Correction Status 2026-05-29

- Bibliography entries for Taşcı, Gharib, Liu and Kumar were corrected in the working DOCX.
- In-text citations were normalized to page-free markers.
- Three-level heading structure was restored in Word styles.
- Synthetic/model-based degradation limitation was added in chapter 6 and conclusion.
- Practical pipeline issue was corrected:
  - `long_live_01` now restores `12` cycles and `1121` phase segments;
  - feature rows increased from `56` to `600`;
  - degradation/RUL rows increased from `17920` to `192000`;
  - MLP train/test rows are now `153600` / `38400`;
  - current test metrics are `MAE = 1.441`, `RMSE = 2.144`, `R2 = 0.988`.
- Visual render remains blocked by missing LibreOffice/`soffice`; manual Word update and PDF export are still required.
