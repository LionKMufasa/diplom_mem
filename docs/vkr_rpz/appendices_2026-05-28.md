# VKR RPZ Appendices Added 2026-05-28

Working DOCX:

- `вкр\ВКР 2026 Миронов Егор Максимович.docx`

Backup before this pass:

- `вкр\ВКР 2026 Миронов Егор Максимович.backup_before_extra_appendices_20260528_015000.docx`

Added appendix structure:

- `Приложение А` - состав программной реализации ПАК предиктивного обслуживания.
  - `Таблица А.1` - программные модули;
  - `Таблица А.2` - конфигурационные файлы инфраструктуры;
  - `Таблица А.3` - контрольные артефакты апробации.
- `Приложение Б` - структура экспериментальных данных и расчетных файлов.
  - `Таблица Б.1` - исходный JSONL-пакет телеметрии;
  - `Таблица Б.2` - нормализованная строка телеметрии;
  - `Таблица Б.3` - сводка обработки `long_live_01`.
- `Приложение В` - фрагменты алгоритмов обработки и прогнозирования.
  - `Таблица В.1` - алгоритм конвейера обработки;
  - `Таблица В.2` - логика расчета HI/RUL;
  - `Таблица В.3` - параметры MLPRegressor.
- `Приложение Г` - материалы воспроизведения и контроля результатов.
  - `Таблица Г.1` - команды воспроизведения;
  - `Таблица Г.2` - контрольные результаты;
  - `Таблица Г.3` - файлы рисунков из основной части.

Main-text references added:

- Chapter `5.2` references appendix `А` for scene and implementation files.
- Chapter `5.4` references appendices `Б` and `Г` for JSONL/normalized data structure and reproduction commands.
- Chapter `5.10` references appendices `А-В` for modules, data structure and algorithms.
- Chapter `6.1` references appendices `Б` and `Г` for control files and reproduction order.
- Chapter `6.3` references appendix `Б` for `long_live_01` file structure.
- Chapter `6.4` references appendix `В` for HI/RUL implementation logic.
- Conclusion references appendices `А-Г` as reproducibility support.

Other correction in this pass:

- Rewrote the chapter `5.4` collector paragraph from future wording to factual wording: `collect_final_scene_telemetry.py` uses CoppeliaSim ZeroMQ Remote API, `customData.palletizingCycle`, axes `motor1...motor4`, and writes JSONL.

Structural audit after the pass:

- DOCX ZIP integrity passed.
- Paragraphs: `753`.
- Tables: `60`.
- Appendix headings present: `Приложение А`, `Приложение Б`, `Приложение В`, `Приложение Г`.
- Appendix table captions present: `А.1-А.3`, `Б.1-Б.3`, `В.1-В.3`, `Г.1-Г.3`.
- Stale tokens after pass: none for old scene names, future insert wording, or old telemetry queue wording.

Visual QA:

- Attempted `render_docx.py` into `render_vkr_appendices_check`.
- Render failed because LibreOffice/`soffice` is not installed.
- Manual Word/PDF visual review is still required for page breaks and table layout.

## Shifted Appendix Letters And Added Code 2026-05-28

User correction:

- `Приложение А` must remain empty.
- Existing appendices should be shifted by one letter.
- Add code listings.

Applied to working DOCX:

- `вкр\ВКР 2026 Миронов Егор Максимович.docx`

Backups before this correction:

- `вкр\ВКР 2026 Миронов Егор Максимович.backup_before_appendix_shift_code_20260528_125432.docx`
- `вкр\ВКР 2026 Миронов Егор Максимович.backup_before_appendix_shift_code_20260528_125537.docx`

Final appendix structure:

- `Приложение А` - empty reserved appendix page.
- `Приложение Б` - состав программной реализации ПАК.
  - `Таблица Б.1` - software modules;
  - `Таблица Б.2` - infrastructure configuration files;
  - `Таблица Б.3` - approbation artifacts.
- `Приложение В` - структура экспериментальных данных и расчетных файлов.
  - `Таблица В.1` - source JSONL telemetry packet;
  - `Таблица В.2` - normalized telemetry row;
  - `Таблица В.3` - `long_live_01` processing summary.
- `Приложение Г` - фрагменты алгоритмов обработки и прогнозирования.
  - `Таблица Г.1` - telemetry-processing pipeline algorithm;
  - `Таблица Г.2` - HI/RUL calculation logic;
  - `Таблица Г.3` - MLPRegressor parameters.
- `Приложение Д` - материалы воспроизведения и контроля результатов.
  - `Таблица Д.1` - reproduction commands;
  - `Таблица Д.2` - control reproduction results;
  - `Таблица Д.3` - figure files used in the main text.
- `Приложение Ж` - листинги ключевых программных фрагментов.
  - `Листинг Ж.1` - cycle state and motor telemetry extraction;
  - `Листинг Ж.2` - file-processing pipeline sequence;
  - `Листинг Ж.3` - HI/RUL/risk calculation fragment;
  - `Листинг Ж.4` - MLPRegressor training fragment.

Updated main-text references:

- Chapter `5.2` now references appendix `Б`.
- Chapter `5.4` now references appendices `В`, `Д`, and `Ж`.
- Chapter `5.10` now references appendices `Б-Г` and `Ж`.
- Chapter `6.1` now references appendices `В` and `Д`.
- Chapter `6.3` now references appendix `В`.
- Chapter `6.4` now references appendix `Г`.
- Conclusion now references appendices `Б-Ж`.

Structural audit after this correction:

- DOCX ZIP integrity passed.
- Paragraphs: `823`.
- Tables: `60`.
- Appendix headings present: `Приложение А`, `Приложение Б`, `Приложение В`, `Приложение Г`, `Приложение Д`, `Приложение Ж`.
- Caption/listing count in appendices: `16`.
- No stale references to `приложении А`, `приложения А-В`, `Таблица А.1`, old scene names, or future collector wording.

Visual QA:

- Attempted `render_docx.py` into `render_vkr_appendix_shift_code_check`.
- Render failed because LibreOffice/`soffice` is not installed.
