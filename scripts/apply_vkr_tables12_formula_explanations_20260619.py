from __future__ import annotations

import importlib.util
import shutil
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


HELPER_PATH = Path("scripts/apply_vkr_formula_logic_cleanup_20260619.py")
spec = importlib.util.spec_from_file_location("formula_helper", HELPER_PATH)
helper = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(helper)

W_NS = helper.W_NS
NS = helper.NS


def wtag(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def qn(name: str) -> str:
    return helper.qn(name)


def ensure_child(parent: etree._Element, tag: str) -> etree._Element:
    child = parent.find(tag)
    if child is None:
        child = etree.Element(tag)
        parent.insert(0, child)
    return child


def set_run_font_12(run: etree._Element) -> None:
    rpr = run.find(wtag("rPr"))
    if rpr is None:
        rpr = etree.Element(wtag("rPr"))
        run.insert(0, rpr)

    fonts = rpr.find(wtag("rFonts"))
    if fonts is None:
        fonts = etree.Element(wtag("rFonts"))
        rpr.insert(0, fonts)
    for attr in ("ascii", "hAnsi", "cs", "eastAsia"):
        fonts.set(qn(f"w:{attr}"), "Times New Roman")

    sz = rpr.find(wtag("sz"))
    if sz is None:
        sz = etree.SubElement(rpr, wtag("sz"))
    sz.set(qn("w:val"), "24")

    szcs = rpr.find(wtag("szCs"))
    if szcs is None:
        szcs = etree.SubElement(rpr, wtag("szCs"))
    szcs.set(qn("w:val"), "24")


def set_table_text_12(root: etree._Element) -> tuple[int, int]:
    table_count = 0
    run_count = 0
    for tbl in root.xpath(".//w:tbl", namespaces=NS):
        table_count += 1
        for run in tbl.xpath(".//w:r", namespaces=NS):
            run_count += 1
            set_run_font_12(run)
    return table_count, run_count


def paragraphs(root: etree._Element) -> list[etree._Element]:
    body = root.find(".//w:body", namespaces=NS)
    if body is None:
        raise RuntimeError("Document body not found")
    return body.xpath("./w:p", namespaces=NS)


def replace_contains(paras: list[etree._Element], needle: str, replacement: str) -> None:
    for p in paras:
        if needle in helper.para_text(p):
            helper.set_para_text(p, replacement)
            return
    raise RuntimeError(f"Paragraph not found: {needle}")


def formula_map(paras: list[etree._Element]) -> dict[int, etree._Element]:
    return helper.formula_by_old_label(paras)


def insert_after_formula(
    paras: list[etree._Element],
    formulas: dict[int, etree._Element],
    label: int,
    text: str,
) -> None:
    p = helper.make_plain_para(text, helper.nearest_body_template(paras, formulas[label]))
    helper.insert_after(formulas[label], p)


def main() -> None:
    docx = helper.find_docx()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = docx.with_name(
        f"{docx.stem}.backup_before_tables12_formula_explanations_{timestamp}.docx"
    )
    shutil.copy2(docx, backup)

    with ZipFile(docx, "r") as zin:
        parts = {name: zin.read(name) for name in zin.namelist()}

    root = etree.fromstring(parts["word/document.xml"])
    paras = paragraphs(root)
    formulas = formula_map(paras)

    table_count, table_runs = set_table_text_12(root)

    replacements = [
        (
            "где M – момент, ω – угловая скорость",
            "где F_i,s – вектор признаков i-го привода на фазе s; Mср, Mmax и σM – среднее, максимальное значение и среднеквадратичное отклонение момента; ωср – средняя угловая скорость; amax – максимальное ускорение; E_i,s – энергетический показатель нагрузки; Δt – шаг интегрирования.",
        ),
        (
            "где Pi – мгновенная механическая мощность привода",
            "где P_i(t) – мгновенная механическая мощность i-го привода; M_i(t) – момент; ω_i(t) – угловая скорость; Kз,i – коэффициент загрузки; Mmax,i – максимальный момент в рассматриваемом окне; Mдоп,i – допустимый момент; L_i – накопленный показатель нагружения; Δt – шаг дискретизации.",
        ),
        (
            "где HI = 1 соответствует исправному состоянию",
            "где HI(t) – индекс технического состояния; HI = 1 соответствует исправному состоянию, а HI -> 0 – приближению к предельному состоянию; f_j(t) – j-й нормированный диагностический признак; w_j – вес признака; p – число признаков.",
        ),
        (
            "где Nкр – прогнозируемый номер цикла достижения предельного состояния",
            "где HIкр – критическое значение индекса технического состояния; x_j(t) – j-й диагностический параметр; xкр,j – его допустимый порог; RUL_N – остаточный ресурс в циклах; Nкр – прогнозируемый номер цикла достижения предельного состояния; Nтек – текущий номер цикла.",
        ),
        (
            "где D – временные ряды телеметрии",
            "где D – временные ряды телеметрии; F – диагностические признаки; HI – показатель состояния; RUL – остаточный ресурс; AТО – рекомендация для ТОиР.",
        ),
        (
            "где F – признаковый вектор, θ – параметры модели.",
            "где F – признаковый вектор, сформированный по окну наблюдения или циклу; θ – параметры регрессионной модели; g(·) – функция, связывающая признаки с прогнозом остаточного ресурса.",
        ),
        (
            "где ck – номер цикла, sk – фаза паллетизации",
            "где d_k – k-я запись наблюдения; t_k – метка времени; c_k – номер цикла; s_k – фаза паллетизации; i – номер привода; q_i – угол; ω_i – угловая скорость; a_i – ускорение; M_i – момент; event_k – диагностическое или технологическое событие.",
        ),
        (
            "где x – исходное значение признака; xmin и xmax",
            "где x – исходное значение признака; x_min и x_max – минимальное и максимальное значения в контрольном диапазоне; F_W – вектор признаков окна W; mean, max, std и rms – среднее, максимум, стандартное отклонение и среднеквадратичное значение; E – энергетический признак; t0 и Δt – начало и длительность окна.",
        ),
        (
            "где rj – балл варианта по критерию",
            "где R – интегральная оценка архитектурного варианта; r_j – балл варианта по j-му критерию; w_j – вес критерия; m – число критериев сравнения.",
        ),
        (
            "где Tобн – период обновления диагностических данных",
            "где Tобн – период обновления диагностических данных; Δtдоп – допустимый период обновления; Pпотерь – доля потерянных измерений; Pдоп – допустимая доля потерь; Kготовн – коэффициент готовности; Tработ – время работоспособного состояния; Tпрост – время простоя.",
        ),
        (
            "где ΔCпр – расчетное снижение потерь от простоя",
            "где ΔCпр – расчетное снижение потерь от простоя; Cпр,до – потери от простоев до внедрения диагностического контура; Cпр,после – ожидаемые потери после внедрения.",
        ),
        (
            "где Nпот – число потерянных или некорректных записей",
            "где Pпотерь – доля потерянных или некорректных записей; Nпот – число потерянных или некорректных записей; Nобщ – общее число ожидаемых записей; Pдоп – допустимая доля потерь. Ограничение на период обновления диагностических данных применяется по формуле (21).",
        ),
        (
            "где nсл – число слоев, nуп – число упаковок в слое.",
            "где Nукл – число операций укладки в одном полном цикле; nсл – число слоев на паллете; nуп – число упаковок в слое. Разделительные листы учитываются как отдельные операции, поскольку они отличаются массой, геометрией и траекторией.",
        ),
        (
            "где N – номер цикла, Mi(t) – исходный момент",
            "где α_i(N) – коэффициент деградации i-го привода к циклу N; α_i,0 – начальное значение коэффициента; k_i – скорость роста деградации; M_i(t) – исходный момент; M_i,deg(t) – момент с учетом деградации; T_s – длительность фазы s; T_s,deg – длительность фазы с учетом деградации; β_s – коэффициент чувствительности фазы к деградации.",
        ),
        (
            "где n – число проверочных наблюдений",
            "где n – число проверочных наблюдений; RUL_i – фактическое значение остаточного ресурса; RUL̂_i – прогноз модели; mean(RUL) – среднее фактическое значение RUL в проверочной выборке. MAE показывает среднюю абсолютную ошибку, RMSE сильнее штрафует крупные ошибки, R² характеризует долю объясненной дисперсии.",
        ),
        (
            "где FW – вектор признаков окна; HI – индекс технического состояния",
            "где RUL_N(N) – остаточный ресурс в циклах при текущем номере цикла N; Nкр – первый цикл, на котором индекс HI_i достигает критического значения HIкр; F_W – вектор признаков окна; HI – индекс технического состояния; θ – параметры регрессионной модели; RUL – прогноз остаточного ресурса.",
        ),
        (
            "где Tпл – плановый горизонт обслуживания",
            "где AТО = 1 означает необходимость планирования технического обслуживания; Tпл – плановый горизонт обслуживания; Tрез – резерв времени на подготовку ремонта; HI_i – индекс состояния i-й оси; HIкр – критический порог. При выполнении условия интерфейс выделяет ось и фазу цикла, по которой сформирован риск.",
        ),
        (
            "где дополнительная единица соответствует рабочей копии паллеты.",
            "где Nпер – число переносимых объектов в одном цикле; Nсл – число слоев; Nуп,сл – число упаковок в слое; Nсозд – число создаваемых рабочих объектов с учетом паллеты. Дополнительная единица соответствует рабочей копии паллеты.",
        ),
        (
            "где Nкорр – число корректных записей телеметрии",
            "где Kдан – коэффициент полноты корректных данных; Kфаз – коэффициент полноты фазовой разметки; Nкорр – число корректных записей телеметрии; Nобщ – общее число записей; Nзап,phase – число записей с заполненной фазовой меткой. Своевременность предупреждений контролируется по формуле (15).",
        ),
        (
            "где Cпр – стоимость одного простоя",
            "где Cпр – стоимость одного простоя; tпр – длительность простоя; Cч – стоимость часа остановки; Cрем – стоимость аварийного ремонта; Cбр – потери от брака и логистического срыва; Eгод – годовой экономический эффект; Nав – число потенциально предотвращаемых аварийных событий в год; Pпред – доля предупрежденных событий; Cэкспл – годовые затраты на сопровождение; Tок – срок окупаемости; Cвн – затраты на внедрение.",
        ),
    ]

    for needle, replacement in replacements:
        replace_contains(paras, needle, replacement)

    # Additional explanations where the original text jumped straight to a new section/table.
    insert_after_formula(
        paras,
        formulas,
        26,
        "где Accept – бинарный результат приемки; K_i – результат i-й проверки, равный 1 при выполнении критерия и 0 при невыполнении; n – число приемочных критериев.",
    )
    insert_after_formula(
        paras,
        formulas,
        40,
        "где μ_x, σ_x, x_max и x_min – среднее значение, стандартное отклонение, максимум и минимум сигнала x в окне W; RMS_x – среднеквадратичное значение; slope_x – наклон тренда; E_x – энергетический признак; ε – малое число, исключающее деление на ноль при нормировании.",
    )
    insert_after_formula(
        paras,
        formulas,
        65,
        "где α_i,кр – критическое значение коэффициента деградации; HI_i(N) – расчетный индекс состояния i-го привода; min(1; ·) ограничивает вклад деградации единицей, чтобы HI оставался в диапазоне от 0 до 1.",
    )
    insert_after_formula(
        paras,
        formulas,
        69,
        "где W_N,s – окно наблюдения для цикла N и фазы s; cycle_k и phase_k – цикл и фаза k-й записи; M_rms – среднеквадратичный момент на окне; n – число отсчетов в окне.",
    )
    insert_after_formula(
        paras,
        formulas,
        74,
        "где key – набор тегов временного ряда; value – набор сохраняемых измеряемых и расчетных значений; robotid, axisid и cycleid – идентификаторы робота, оси и цикла; id_k – уникальный ключ записи для защиты от неотличимых дублей.",
    )
    insert_after_formula(
        paras,
        formulas,
        76,
        "где D_raw – исходная телеметрия; D_clean – очищенный и нормализованный набор данных; F_W – признаки окна; HI – индекс технического состояния; RUL – прогноз остаточного ресурса; AТО – рекомендация по обслуживанию.",
    )
    insert_after_formula(
        paras,
        formulas,
        78,
        "где Sготов – интегральная бинарная готовность контура; Iсцена, Iцикл, Iтелем, Iпризнаки, I_RUL, I_UI – признаки готовности сцены, цикла, телеметрии, признаков, RUL-модуля и интерфейса; Accept = 1 означает успешную интеграционную проверку.",
    )
    insert_after_formula(
        paras,
        formulas,
        81,
        "где Sапр – бинарная оценка успешности апробации; Iсц, Iц, Iтел, Iпр, I_RUL и I_UI – результаты проверок сцены, цикла, телеметрии, признаков, RUL-модуля и интерфейса.",
    )
    insert_after_formula(
        paras,
        formulas,
        86,
        "где Tнабл – длительность наблюдения; tmax и tmin – максимальная и минимальная временные метки; n – число исходных пакетов телеметрии; Δtср – средний шаг записи; fнабл – фактическая средняя частота внешнего сбора данных.",
    )

    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone="yes"
    )

    tmp = docx.with_suffix(".tmp_tables12_formula_explanations.docx")
    with ZipFile(tmp, "w", ZIP_DEFLATED) as zout:
        for name, data in parts.items():
            zout.writestr(name, data)
    tmp.replace(docx)

    report = Path("scratch") / "tables12_formula_explanations_20260619_report.txt"
    report.write_text(
        "\n".join(
            [
                f"DOCX: {docx}",
                f"Backup: {backup}",
                f"Tables formatted: {table_count}",
                f"Table runs formatted to 12 pt: {table_runs}",
                f"Formula explanation replacements: {len(replacements)}",
                "Additional explanation paragraphs inserted: 9",
            ]
        ),
        encoding="utf-8",
    )
    print(report)
    print(f"backup={backup}")
    print(f"tables={table_count} table_runs={table_runs}")


if __name__ == "__main__":
    main()
