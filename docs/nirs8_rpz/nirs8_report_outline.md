# NIRS-8 Report Outline

Last updated: 2026-05-21

## Target

- Build a focused 20-sheet NIRS report on the degradation model of mechanical units of an industrial robot for predictive maintenance.
- Use NIRS-7 as background only where it supports the object, production context, or previously chosen PdM architecture.
- Main content order and chapter names must follow the user-provided NIRS-8 contents list.
- Formatting should follow applicable GOST requirements and the 7th-semester NIRS document style.
- The report must directly satisfy the four task items from the assignment sheet.
- Do not include a separate economic-calculation chapter.
- Use `5. Рабочее проектирование` and `6. Апробация`; do not include a separate reliability/failure-probability chapter.
- Literature selection: [[docs/nirs8_rpz/nirs8_literature_selection]]

## Required Contents Order

1. `Титульный лист`
2. `Аннотация`
3. `Содержание`
4. `Введение`
5. `1 Предпроектное обследование`
6. `2 Концептуальное проектирование`
7. `3 Техническое задание`
8. `4 Техническое проектирование`
9. `5 Рабочее проектирование`
10. `6 Апробация`
11. `Заключение`
12. `Список литературы`
13. `Приложение`

## Assignment Tasks To Cover

1. Analyze the construction of an industrial robot and identify units subject to degradation during operation.
2. Study wear mechanisms of drive units and factors affecting their durability.
3. Develop a mathematical degradation model describing damage accumulation over time.
4. Establish the relation between degradation parameters and diagnostic features, and define the limit-state criterion of a unit.

## Proposed NIRS-8 Structure

1. `Титульный лист`
   - Already exists in the current DOCX template.
   - Preserve template formatting and university/department fields.

2. `Аннотация` - about 0.5 sheet
   - Briefly state the topic, object, purpose, degradation-model focus, methods, and result.
   - Should mention industrial robot mechanical units, diagnostic features, Health Index / degradation model, limit-state criterion, and approbation.

3. `Содержание`
   - Use the document's heading structure; follow the style of the 7th-semester NIRS.

4. `Введение` - about 1.5 sheets
   - relevance of predictive maintenance and degradation modeling;
   - object, subject, goal, tasks;
   - methods and expected practical result.

5. `1 Предпроектное обследование` - about 2.5-3 sheets
   - `1.1 Общие сведения об объекте исследования`
   - `1.2 Робот-паллетизатор в составе производственного участка`
   - `1.3 Конструктивные узлы промышленного робота, подверженные деградации`
   - `1.4 Эксплуатационные факторы, влияющие на деградацию механических узлов`
   - `1.5 Выбор узлов для построения модели деградации`
   - `1.6 Выводы по предпроектному обследованию`
   - Covers assignment task 1.

6. `2 Концептуальное проектирование` - about 2.5-3 sheets
   - `2.1 Анализ механизмов деградации приводных узлов`
   - `2.2 Факторы, влияющие на долговечность редукторов, подшипников и сочленений`
   - `2.3 Место модели деградации в системе предиктивного обслуживания`
   - `2.4 Информационная схема формирования диагностических признаков`
   - `2.5 Концепция показателя состояния и предельного состояния узла`
   - `2.6 Выводы по концептуальному проектированию`
   - Covers assignment task 2 and prepares tasks 3-4.

7. `3 Техническое задание` - about 2 sheets
   - `3.1 Основание и назначение разработки`
   - `3.2 Требования к анализу деградирующих механических узлов`
   - `3.3 Требования к математической модели деградации`
   - `3.4 Требования к диагностическим признакам и исходным данным`
   - `3.5 Требования к критерию предельного состояния`
   - `3.6 Требования к апробации модели`
   - `3.7 Выводы по техническому заданию`
   - Explicitly restates and formalizes the four assignment tasks.

8. `4 Техническое проектирование` - about 4 sheets
   - `4.1 Выбор параметров наблюдения и диагностических признаков`
   - `4.2 Математическая модель накопления повреждений во времени`
   - `4.3 Учёт нагрузки и режима движения в скорости деградации`
   - `4.4 Формирование интегрального показателя состояния Health Index`
   - `4.5 Связь параметров деградации с диагностическими признаками`
   - `4.6 Критерий предельного состояния узла`
   - `4.7 Выводы по техническому проектированию`
   - Covers assignment tasks 3 and 4.

9. `5 Рабочее проектирование` - about 3 sheets
   - `5.1 Подготовка исходных данных для расчёта модели`
   - `5.2 Алгоритм расчёта диагностических признаков`
   - `5.3 Алгоритм расчёта показателя состояния и остаточного ресурса`
   - `5.4 Реализация сценария деградации узла`
   - `5.5 Подготовка результатов для анализа и визуализации`
   - `5.6 Выводы по рабочему проектированию`
   - Shows how the designed model is practically prepared for calculation/appraisal.

10. `6 Апробация` - about 2.5-3 sheets
   - `6.1 Цель и исходные условия апробации`
   - `6.2 Расчёт диагностических признаков и Health Index`
   - `6.3 Проверка критерия предельного состояния`
   - `6.4 Анализ изменения остаточного ресурса`
   - `6.5 Выводы по апробации`
   - Uses CoppeliaSim/telemetry/synthetic degradation scenario where appropriate, but stays within the NIRS-8 degradation-model scope.

11. `Заключение` - about 1 sheet
   - summarize analyzed degradation mechanisms;
   - summarize proposed model, diagnostic-feature connection, and limit-state criterion;
   - explicitly state that the four assignment tasks were completed.

12. `Список литературы` - about 1 sheet
   - use a compact subset of VKR/NIRS-7 bibliography relevant to robotics, reliability, degradation modeling, PdM, RUL, and digital twins.

13. `Приложение` if needed, outside or minimally inside the 20-sheet target depending on template rules
   - formulas, feature table, or extra plots.

## Recommended Page Budget

- Title page, annotation, contents, introduction, chapters, conclusion, bibliography, and appendices should together stay near the required 20-sheet NIRS volume unless the template/instructor treats service pages separately.
- Suggested content distribution:
  - `Аннотация`: 0.5 sheet.
  - `Содержание`: 0.5 sheet.
  - `Введение`: 1-1.5 sheets.
  - Chapter 1: 2-2.5 sheets.
  - Chapter 2: 2.5 sheets.
  - Chapter 3: 1.5-2 sheets.
  - Chapter 4: 4 sheets.
  - Chapter 5: 2.5 sheets.
  - Chapter 6: 2-2.5 sheets.
  - `Заключение`: 1 sheet.
  - `Список литературы`: about 1 sheet.

## Formatting Orientation

- Follow the 7th-semester NIRS document for report rhythm, heading hierarchy, title page style, assignment handling, and contents placement.
- Use GOST-style formal report language, numbered chapters/subchapters, figure/table captions, bibliography formatting, and consistent terminology.
- Do not add a separate economic chapter or a separate reliability-probability chapter.

## First Drafting Step

- Draft `Аннотация`, `Введение`, and chapter 1 first.
- Keep the text self-contained and aligned with the assignment sheet: each chapter should make it clear which assignment task it closes.
