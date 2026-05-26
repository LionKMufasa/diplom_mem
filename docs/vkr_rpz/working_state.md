# VKR RPZ Working State

Last updated: 2026-05-22

## Main File

- Working RPZ DOCX: `C:\Users\egork\Desktop\coppelia_dpilom\ВКР\ВКР 2026 Миронов Егор Максимович.docx`
- Backup before the first TOC/literature/introduction edit batch: `C:\Users\egork\Desktop\coppelia_dpilom\ВКР\ВКР 2026 Миронов Егор Максимович.backup_lit_toc_20260505_215140.docx`

## Source Materials

- Main baseline report: `ВКР\НИРС(7сем)\НИРС 2025 Миронов Егор Максимович.docx`
- NIRS-7 figures: `ВКР\НИРС(7сем)\Схемы и рисунки`
- Literature folder: `ВКР\литература`
- Literature working note: `ВКР\литература\Список литературы.docx`
- Deliverables map: [[docs/project_deliverables_plan]]

## Current Document State

- The RPZ has a real Word TOC field.
- Microsoft Word updated and saved the TOC successfully.
- TOC requirement corrected on 2026-05-06:
  - contents must be two-level only;
  - active TOC field is `TOC \o "1-2" \h \z \u`;
  - cached TOC contains `66` entries and no `toc 3` entries.
- RPZ volume requirement corrected on 2026-05-06:
  - target is 70 sheets/pages of main RPZ text;
  - appendices are outside this main-text volume.
- Planned section skeleton was converted from `List Paragraph` items to true Word headings:
  - `Heading 1 = 11`
  - `Heading 2 = 55`
  - TOC entries = `66`
- Added a clean `Список литературы` with 32 entries:
  - ГОСТ 27.002-2015, ГОСТ 27.003-2016, ГОСТ 27.301-95, ГОСТ 34.602-2020
  - ABB IRB 660 manual and datasheet
  - RUL/PHM sources
  - digital twin sources
  - CoppeliaSim / Remote API sources
  - scikit-learn / XGBoost sources
  - InfluxDB / Grafana sources
- Added `Перечень принятых сокращений`.
- Annotation now states that the RPZ is formed as 70 sheets of main A4 text, and that large schemes, listings, additional tables, graphs, and illustrations are moved to appendices and excluded from the main volume.
- Rewrote and expanded the first version of `Введение`:
  - актуальность;
  - проблема простоев и ограничения ППР;
  - объект и предмет;
  - роль ABB IRB 660-180/3.15;
  - обоснование цифровой модели / цифрового двойника;
  - обоснование RUL/PHM;
  - цель, задачи, методология, научная новизна и практическая значимость.
- New correction on 2026-05-06 before the next DOCX pass:
  - user estimates the current draft at about 59 pages already;
  - final main RPZ must fit 70 pages excluding appendices;
  - filled sections must be compressed before chapters 3-6 are written;
  - preferred style is less generic prose, more formulas, compact calculations, and future insertion markers for practical materials.
- Compression pass completed on 2026-05-06:
  - replaced `Введение`, chapter 1, and chapter 2 with compact versions;
  - compact sources: [[docs/vkr_rpz/introduction_compact]], [[docs/vkr_rpz/chapter1_predproject_compact]], [[docs/vkr_rpz/chapter2_conceptual_compact]];
  - script used: `scripts\compress_vkr_filled_sections.py`;
  - backup before compression: `ВКР\ВКР 2026 Миронов Егор Максимович.backup_before_compression_20260506_021552.docx`;
  - Microsoft Word updated the TOC and saved the document;
  - Word page count after compression: `29` pages total in the current draft.
- Chapter 3 pass completed on 2026-05-06:
  - filled `Техническое задание` directly in the working DOCX;
  - chapter 3 source: [[docs/vkr_rpz/chapter3_tz_draft]];
  - literature/citation map: [[docs/vkr_rpz/literature_citation_notes]];
  - script used: `scripts\insert_vkr_chapter3_and_references.py`;
  - backup before chapter 3 insertion: `ВКР\ВКР 2026 Миронов Егор Максимович.backup_before_chapter3_tz_20260506_024308.docx`;
  - chapter 3 is based on ГОСТ 34.602-2020 and ГОСТ 34.602-89 logic.
- New correction request on 2026-05-06:
  - citations in the RPZ must refer to one source at a time and include page numbers;
  - add Russian-language literature, download source PDFs, and reorder bibliography as: ГОСТы first, Russian literature second, other sources third;
  - make formulas visually more readable;
  - rewrite chapter 3 strictly according to ГОСТ 34.602, including the required sections and updated contents/TOC.
- Correction pass completed on 2026-05-06:
  - strict chapter 3 source: [[docs/vkr_rpz/chapter3_tz_gost_strict]];
  - scripts used: `scripts\fix_vkr_citations_bibliography_formulas_tz.py` and `scripts\cleanup_vkr_citation_sentence_flow.py`;
  - backup before the correction: `ВКР\ВКР 2026 Миронов Егор Максимович.backup_before_gost_citation_formula_fix_20260506_033801.docx`;
  - chapter 3 now follows the ГОСТ 34.602-89 section order as Heading 2 items: общие сведения; назначение и цели; характеристика объекта; требования к системе; состав и содержание работ; порядок контроля и приемки; подготовка объекта к вводу; документирование; источники разработки; выводы;
  - bibliography rebuilt to 46 entries, ordered as ГОСТы first, Russian-language literature second, other sources third;
  - downloaded/copied Russian-language PDFs are in `ВКР\литература\Русская литература`; the official `ГОСТ 34.602-89.pdf` is in `ВКР\литература`;
  - in-text numeric citations before the bibliography now use one-source-with-page format only, e.g. `[8, с. 100]`;
  - Word TOC updated successfully through Microsoft Word; Word page count after the correction is `42`;
  - structural audit after the pass: paragraphs = `515`, tables = `17`, `Heading 1 = 11`, `Heading 2 = 57`, `Heading 3 = 40`, TOC entries = `68`, `toc 3` entries = `0`, bibliography entries = `46`, citations = `31`, invalid citations = `0`.

## Current Text Drafts

- Chapter 1 `Предпроектное обследование` drafted as ready-to-insert Markdown text: [[docs/vkr_rpz/chapter1_predproject_draft]].
- The draft includes:
  - sections 1.1-1.8 according to the RPZ skeleton;
  - suggested third-level subheadings;
  - 5 tables;
  - 12 placeholders for future figures, screenshots, telemetry graphs, and diagrams.
- The DOCX has now been edited directly: chapter 1 was inserted into `ВКР 2026 Миронов Егор Максимович.docx`.
- Backup before direct insertion: `ВКР\ВКР 2026 Миронов Егор Максимович.backup_before_chapter1_20260506_012229.docx`.
- Backup before 70-pages/two-level-TOC correction: `ВКР\ВКР 2026 Миронов Егор Максимович.backup_before_70pages_toc2_20260506_014025.docx`.
- After insertion and Word TOC update:
  - paragraphs = `438`;
  - tables = `8` total in document;
  - `Heading 1 = 11`;
  - `Heading 2 = 55`;
  - `Heading 3 = 21`;
  - TOC entries before two-level correction = `87`;
  - TOC entries after two-level correction = `66`;
  - chapter 1 placeholders = `12`.
- Chapter 2 `Концептуальное проектирование` was drafted in [[docs/vkr_rpz/chapter2_conceptual_draft]] and inserted into the working DOCX.
- Backup before chapter 2 insertion: `ВКР\ВКР 2026 Миронов Егор Максимович.backup_before_chapter2_20260506_015123.docx`.
- After chapter 2 insertion and Word TOC update:
  - paragraphs = `616`;
  - tables = `15` total in document;
  - `Heading 1 = 11`;
  - `Heading 2 = 55`;
  - `Heading 3 = 42`;
  - TOC entries = `66`;
  - `toc 3` entries = `0`;
  - total placeholders = `24`;
  - chapter 2 placeholders = `12`.
- After compression pass:
  - paragraphs = `396`;
  - document tables = `12`;
  - `Heading 1 = 11`;
  - `Heading 2 = 55`;
  - `Heading 3 = 28`;
  - TOC entries = `66`;
  - `toc 3` entries = `0`;
  - bracketed future inserts/placeholders = `26`;
  - short formula-like calculation lines = `32`.
- After chapter 3 insertion and literature pass:
  - paragraphs = `484`;
  - document tables = `18`;
  - `Heading 1 = 11`;
  - `Heading 2 = 55`;
  - `Heading 3 = 44`;
  - TOC entries = `66`;
  - `toc 3` entries = `0`;
  - bracketed future inserts/placeholders = `33`;
  - bibliography entries = `39`;
  - citation mentions = `32`;
  - Word page count = `41`.
- After strict ГОСТ/citation/formula correction:
  - paragraphs = `515`;
  - document tables = `17`;
  - `Heading 1 = 11`;
  - `Heading 2 = 57`;
  - `Heading 3 = 40`;
  - TOC entries = `68`;
  - `toc 3` entries = `0`;
  - bibliography entries = `46`;
  - citation mentions = `31`;
  - invalid numeric citations before bibliography = `0`;
  - formula-like paragraphs audited = `38`, centered formula lines = `37`, with the one non-centered item being explanatory prose;
  - Word page count = `42`.
- Chapter 4 `Техническое проектирование` inserted on 2026-05-06:
  - source note: [[docs/vkr_rpz/chapter4_technical_design]];
  - script used: `scripts\insert_vkr_chapter4_technical_design.py`;
  - backup before insertion: `ВКР\ВКР 2026 Миронов Егор Максимович.backup_before_chapter4_technical_design_20260506_131516.docx`;
  - chapter 4 fills the existing Heading 2 structure: architecture, digital model, degradation modeling, telemetry collection, preprocessing, degradation model, RUL formalization, ML algorithm choice, storage, visualization, containerization, and conclusions;
  - Word page count after chapter 4 and TOC update: `51`;
  - structural audit after chapter 4: paragraphs = `640`, tables = `22`, `Heading 1 = 11`, `Heading 2 = 57`, `Heading 3 = 62`, TOC entries = `68`, `toc 3` entries = `0`, bibliography entries = `46`, citation mentions = `39`, invalid citations = `0`.
- Source 6 removal and chapter 5 pass completed on 2026-05-07:
  - removed `Галахарь А.С. Диагностика и надежность автоматизированных систем: курс лекций` from the bibliography;
  - shifted old in-text citation numbers greater than `6` down by one; old source 6 citation mentions found = `0`;
  - current bibliography entries = `45`;
  - chapter 5 source: [[docs/vkr_rpz/chapter5_working_design]];
  - scripts used: `scripts\insert_vkr_chapter5_remove_source6.py`, `scripts\reinsert_vkr_chapter5_only.py`;
  - backups before edits: `ВКР\ВКР 2026 Миронов Егор Максимович.backup_before_remove_source6_and_chapter5_20260507_165326.docx`, `ВКР\ВКР 2026 Миронов Егор Максимович.backup_before_reinsert_chapter5_heading_fix_20260507_171248.docx`;
  - chapter 5 fills 10 Heading 2 sections: назначение рабочего проектирования, CoppeliaSim model implementation, degradation mechanism, telemetry collection, preprocessing/features, RUL algorithm, database, operator UI, component integration, conclusions;
  - Word page count after updating fields and TOC = `62`;
  - structural audit after chapter 5: paragraphs = `731`, document tables = `32`, `Heading 1 = 11`, `Heading 2 = 57`, `Heading 3 = 62`, TOC entries = `68`, `toc 3` entries = `0`, bibliography entries = `45`, valid citation mentions = `47`, invalid citation-like brackets = `0`, maximum citation number = `45`.
- Chapter 6 `Апробация и оценка эффективности системы` inserted on 2026-05-07:
  - chapter 6 source: [[docs/vkr_rpz/chapter6_approbation_effectiveness]];
  - summary and practical plan note: [[docs/vkr_rpz/current_written_summary_and_practice_plan]];
  - script used: `scripts\insert_vkr_chapter6_approbation.py`;
  - backups before edits: `ВКР\ВКР 2026 Миронов Егор Максимович.backup_before_chapter6_approbation_20260507_222025.docx`, `ВКР\ВКР 2026 Миронов Егор Максимович.backup_before_chapter6_approbation_20260507_222324.docx`;
  - first chapter 6 insertion made the DOCX `72` pages, so the chapter was compacted to fit the saved 70-page target;
  - Word page count after compact chapter 6 and TOC update = `68`;
  - structural audit after compact chapter 6: paragraphs = `784`, document tables = `34`, `Heading 1 = 11`, `Heading 2 = 57`, `Heading 3 = 62`, TOC entries = `68`, `toc 3` entries = `0`, bibliography entries = `45`, valid citation mentions = `53`, invalid citation-like brackets = `0`, maximum citation number = `45`.
- Bibliography additions in this pass:
  - ГОСТ 34.602-89 as entry `33`;
  - robot PHM / digital-twin PHM / RUL and IIoT predictive maintenance PDFs as entries `34-39`.

## 2026-05-22 Formula Conversion Pass

- User manually adjusted the VKR Word file before this pass.
- Edited working DOCX in place: `C:\Users\egork\Desktop\coppelia_dpilom\вкр\ВКР 2026 Миронов Егор Максимович.docx`.
- Converted centered display formula paragraphs from plain text into real Word OMML equation objects, so variables such as `N_пал`, `M_i`, `F_W`, `Σ_{j=1}^{n}` and `RUL̂_i` use equation formatting and indices instead of visible underscores.
- Script used: `scripts\convert_vkr_formulas_to_omml.py`.
- Backup before conversion: `C:\Users\egork\Desktop\coppelia_dpilom\вкр\ВКР 2026 Миронов Егор Максимович.backup_before_equation_conversion_20260522_062014.docx`.
- Report: `C:\Users\egork\Desktop\coppelia_dpilom\reports\vkr_equation_conversion_20260522_062014.tsv`.
- Result: `120` display formula lines converted; Word COM opened the DOCX successfully and counted `121` equation objects.
- Structural checks: ZIP integrity passed; remaining centered formula-like paragraphs in normal text = `0`.
- Word read-only repagination after the pass: `63` pages.
- Render QA remains blocked because LibreOffice/`soffice` is unavailable in the environment.
- Follow-up inline-index pass:
  - script used: `scripts\convert_vkr_inline_indices.py`;
  - backups before edits: `C:\Users\egork\Desktop\coppelia_dpilom\вкр\ВКР 2026 Миронов Егор Максимович.backup_before_inline_indices_20260522_063021.docx` and `C:\Users\egork\Desktop\coppelia_dpilom\вкр\ВКР 2026 Миронов Егор Максимович.backup_before_inline_indices_20260522_063119.docx`;
  - reports: `reports\vkr_inline_indices_20260522_063021.tsv` and `reports\vkr_inline_indices_20260522_063119.tsv`;
  - result: `22` normal-text subscript runs added for inline designations such as `M_i`, `a_i`, `d_k`, `M_rms`, `E_i`, `P_i`, `HI_i`, `phase_k`;
  - remaining underscore tokens are code/object/event identifiers and were intentionally left unchanged.
- Formula numbering and deeper variable cleanup pass:
  - script used: `scripts\format_vkr_formulas_and_variables.py`;
  - backup before edit: `C:\Users\egork\Desktop\coppelia_dpilom\вкр\ВКР 2026 Миронов Егор Максимович.backup_before_formula_numbering_20260522_064415.docx`;
  - report: `reports\vkr_formula_numbering_variables_20260522_064415.tsv`;
  - all `121` equations were converted to the final layout with center-tabbed equation content and right-tabbed formula numbers in round brackets `(1)` ... `(121)`;
  - all OMML math runs were set to 14 pt (`w:sz=28`);
  - `68` explanatory/body paragraphs were cleaned up with `167` additional text subscript runs for variables such as `Nпал`, `nсл`, `P_i`, `Kз,i`, `D_raw`, `F_W`, `T_пл`, `HI_кр`;
  - technical identifiers and paths such as `robot_raw`, `base_respondable`, `Pallet_bottles`, and file paths remain plain text with underscores intentionally;
  - verification: DOCX ZIP integrity passed, formulas numbered `121/121`, math runs without 14 pt `0`, Word opened read-only with `121` equations and `63` pages.

## 2026-05-22 Final Practical Insertions Pass

- User asked to fill all remaining VKR RPZ insertions directly in the working DOCX, write the conclusion, stop repeating formulas in chapter 6, and add final numerical calculations from practical data and NIRS 7/8.
- Edited working DOCX in place: `C:\Users\egork\Desktop\coppelia_dpilom\вкр\ВКР 2026 Миронов Егор Максимович.docx`.
- Scripts used:
  - `scripts\generate_vkr_practice_pngs.py`;
  - `scripts\fill_vkr_remaining_insertions.py`;
  - `scripts\fix_vkr_final_insertions_cleanup.py`;
  - `scripts\format_vkr_formulas_and_variables.py`.
- Generated DOCX PNG figures in `reports\figures\vkr_practice_png`: torque RMS by axis, HI curves for motor1, NN RUL actual-vs-predicted for S3/motor1, and PAK dashboard summary.
- Backup before final insertion: `вкр\ВКР 2026 Миронов Егор Максимович.backup_before_final_insertions_20260522_113812.docx`.
- Backup before formula renumbering after insertion: `вкр\ВКР 2026 Миронов Егор Максимович.backup_before_formula_numbering_20260522_113841.docx`.
- Remaining `ВСТАВКА` markers after cleanup: `0`.
- Main inserted practical evidence:
  - final scene/object correspondence text and NIRS-7 robot-cell figure;
  - RUL training pipeline table;
  - storage/measurement table and CSV telemetry fragment;
  - integration-test, methodology and factual-run tables;
  - NIRS-based technological calculations: `63 kg`, `187 s`, `12` packages/cycle, `231` packages/hour, `14.55 t/hour`, `58212 t/year`, load factor `0.35`;
  - torque RMS plot, RUL actual-vs-predicted plot, HI curves and dashboard summary;
  - actual NN metrics from `long_live_01`: `MAE = 1.173`, `RMSE = 1.442`, `R2 = 0.994`;
  - reliability indicators: `K_data = 1.000`, `K_phase = 1.000`, `K_pred = 1.000`, `T_update = 0.093 s`;
  - economic scenario: `450000 rub/year`, payback `1.0` year;
  - maintenance-strategy comparison.
- Chapter 6 repeated RUL/metric formula block was removed; the text now refers back to formulas `(88)`-`(90)` and `(91)`-`(93)`.
- Final formula numbering after removal: `(1)` ... `(114)`.
- Filled `Заключение` with the final project summary, practical validation, NIRS-based calculations, economic estimate and future work.
- Structural verification:
  - DOCX ZIP integrity passed;
  - paragraphs = `693`;
  - tables = `48`;
  - formula sequence continuous through `(114)`;
  - image relationships = `15`.
- Render QA failed because LibreOffice/`soffice` is not installed.
- Automated Word COM attempts to update fields/get page count hung and were terminated. No Word lock file remained afterward. Manual Word field update, page-count check and visual review are still needed.

## Verification

- Structural checks completed:
  - no `[[TOC]]` or TOC placeholder remains;
  - Word field instruction contains `TOC \o "1-2" \h \z \u`;
  - `word/settings.xml` has `updateFields=true`.
- Visual DOCX-to-PNG render was not completed:
  - `soffice` and `pdftoppm` are unavailable;
  - Microsoft Word COM updated fields but hung during PDF export.
- Latest render attempt after compression:
  - first failed due temporary-folder permissions under sandbox;
  - after escalation, failed with `FileNotFoundError` for the LibreOffice/`soffice` executable;
  - temporary render folders were removed.
- Latest render attempt after strict chapter 3 correction:
  - `where soffice` found no installed LibreOffice executable;
  - `render_docx.py` first failed under sandbox due temp folder permissions, then failed outside sandbox with `FileNotFoundError` because LibreOffice/`soffice` is not installed;
  - no PNG visual QA was produced.
- Latest render attempt after chapter 4:
  - `where soffice` still found no installed LibreOffice executable;
  - `render_docx.py` failed outside sandbox with `FileNotFoundError`;
  - no PNG visual QA was produced.
- Latest render attempt after chapter 5:
  - first failed in sandbox due temporary-folder permissions;
  - after escalation, `render_docx.py` failed with `FileNotFoundError` because LibreOffice/`soffice` is not installed;
  - no PNG visual QA was produced.
- Latest render attempt after chapter 6:
  - first failed in sandbox due temporary-folder permissions;
  - after escalation, `render_docx.py` failed with `FileNotFoundError` because LibreOffice/`soffice` is not installed;
  - no PNG visual QA was produced.
- Next pass should include manual visual inspection in Word, especially front matter, TOC, page breaks, bibliography numbering, and heading spacing.

## Next Writing Steps

1. Visually inspect the current DOCX in Microsoft Word, especially chapters 5-6 tables/formulas, inserted figures, TOC, bibliography numbering, and page breaks.
2. Manually update Word fields/TOC and check the final main-text page count against the 70-page target.
3. If the main text is too long after field update, move the least important detailed tables/screenshots to appendices rather than cutting core calculations.

## Working Workflow

- Default for VKR RPZ work: edit `ВКР 2026 Миронов Егор Максимович.docx` directly.
- Ready-to-insert Russian text in chat is still acceptable when the user explicitly wants to review a fragment before insertion.
