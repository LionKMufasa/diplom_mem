from __future__ import annotations

import copy
import re
import shutil
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": W_NS, "m": M_NS}


def wtag(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def mtag(name: str) -> str:
    return f"{{{M_NS}}}{name}"


def qn(prefix_name: str) -> str:
    prefix, name = prefix_name.split(":")
    uri = {"w": W_NS, "m": M_NS}[prefix]
    return f"{{{uri}}}{name}"


def find_docx() -> Path:
    candidates = [
        p
        for p in Path.cwd().rglob("*.docx")
        if "2026" in p.name and p.stat().st_size > 1_000_000
        and "backup" not in p.name.lower()
        and "НИРС" not in str(p)
    ]
    if not candidates:
        raise FileNotFoundError("VKR DOCX not found")
    return max(candidates, key=lambda p: p.stat().st_size)


def para_text(p: etree._Element) -> str:
    return "".join(p.xpath(".//w:t/text()|.//m:t/text()", namespaces=NS)).strip()


def has_math(p: etree._Element) -> bool:
    return bool(p.xpath(".//m:oMath|.//m:oMathPara", namespaces=NS))


def formula_label(p: etree._Element) -> int | None:
    for t in reversed(p.xpath(".//w:t|.//m:t", namespaces=NS)):
        value = t.text or ""
        m = re.fullmatch(r"\((\d{1,3})\)", value.strip())
        if m:
            return int(m.group(1))
    matches = re.findall(r"\((\d{1,3})\)", para_text(p))
    if matches:
        return int(matches[-1])
    return None


def set_formula_label(p: etree._Element, number: int) -> None:
    nodes = p.xpath(".//w:t|.//m:t", namespaces=NS)
    for t in reversed(nodes):
        value = t.text or ""
        if re.fullmatch(r"\(\d{1,3}\)", value.strip()):
            t.text = f"({number})"
            return
    old = formula_label(p)
    if old is not None:
        pattern = re.compile(rf"\({old}\)(?!.*\({old}\))")
        for t in reversed(nodes):
            if t.text and f"({old})" in t.text:
                t.text = pattern.sub(f"({number})", t.text)
                return
    # Fallback: append a label run if a malformed formula paragraph has no label.
    run = etree.SubElement(p, wtag("r"))
    text = etree.SubElement(run, wtag("t"))
    text.text = f"({number})"


def is_heading(p: etree._Element) -> bool:
    vals = p.xpath("./w:pPr/w:pStyle/@w:val", namespaces=NS)
    return bool(vals and "Heading" in vals[0])


def is_formula_paragraph(p: etree._Element) -> bool:
    text = para_text(p)
    if has_math(p):
        return formula_label(p) is not None
    if is_heading(p):
        return False
    nums = re.findall(r"\(\d{1,3}\)", text)
    if len(nums) != 1:
        return False
    if len(text) > 220:
        return False
    if re.match(
        r"^(Таблица|Рисунок|Приложение|Список|где|В данном|Для |По |При |Оператив|Расчетные|Формулы|Показатель|Прогноз|Регрессионная|Энергетическая|Нормирование|Наклон|Предупреждение|Коэффициент|Дополнительно)",
        text,
    ):
        return False
    return bool(re.search(r"[=≤≥Σ√→·{}]", text))


def make_run(text: str) -> etree._Element:
    r = etree.Element(wtag("r"))
    rpr = etree.SubElement(r, wtag("rPr"))
    fonts = etree.SubElement(rpr, wtag("rFonts"))
    for attr in ("ascii", "hAnsi", "cs"):
        fonts.set(qn(f"w:{attr}"), "Times New Roman")
    sz = etree.SubElement(rpr, wtag("sz"))
    sz.set(qn("w:val"), "28")
    szcs = etree.SubElement(rpr, wtag("szCs"))
    szcs.set(qn("w:val"), "28")
    t = etree.SubElement(r, wtag("t"))
    if text.startswith(" ") or text.endswith(" "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return r


def make_plain_para(text: str, template: etree._Element | None = None) -> etree._Element:
    p = etree.Element(wtag("p"))
    if template is not None:
        ppr = template.find(wtag("pPr"))
        if ppr is not None:
            p.append(copy.deepcopy(ppr))
    p.append(make_run(text))
    return p


def nearest_body_template(paras: list[etree._Element], target: etree._Element) -> etree._Element | None:
    try:
        idx = paras.index(target)
    except ValueError:
        return None
    for step in range(1, 20):
        for j in (idx - step, idx + step):
            if 0 <= j < len(paras):
                cand = paras[j]
                text = para_text(cand)
                if text and len(text) > 45 and not is_formula_paragraph(cand) and not is_heading(cand):
                    return cand
    return None


def replace_para(p: etree._Element, text: str, paras: list[etree._Element]) -> etree._Element:
    parent = p.getparent()
    new_p = make_plain_para(text, nearest_body_template(paras, p))
    parent.replace(p, new_p)
    return new_p


def set_para_text(p: etree._Element, text: str) -> None:
    ppr = p.find(wtag("pPr"))
    for child in list(p):
        if child is not ppr:
            p.remove(child)
    p.append(make_run(text))


def remove_para(p: etree._Element) -> None:
    parent = p.getparent()
    parent.remove(p)


def insert_after(ref: etree._Element, p: etree._Element) -> None:
    ref.addnext(p)


def formula_by_old_label(paras: list[etree._Element]) -> dict[int, etree._Element]:
    out: dict[int, etree._Element] = {}
    for p in paras:
        if is_formula_paragraph(p):
            label = formula_label(p)
            if label is not None:
                out[label] = p
    return out


def replace_text_if_contains(paras: list[etree._Element], needle: str, replacement: str) -> None:
    for p in paras:
        if needle in para_text(p):
            set_para_text(p, replacement)
            return
    raise RuntimeError(f"Paragraph not found: {needle}")


def update_formula_references(root: etree._Element, mapping: dict[int, int]) -> None:
    paras_all = root.xpath(".//w:body//w:p", namespaces=NS)
    in_bibliography = False
    for p in paras_all:
        text_all = para_text(p)
        if text_all.startswith("Список использованных источников"):
            in_bibliography = True
        if text_all.startswith("Приложение А"):
            in_bibliography = False
        if in_bibliography or is_formula_paragraph(p):
            continue
        if not re.search(r"формул|формуле|формулы|формула|выражени|зависимост|рассчитыва|метрик|MAE|RMSE|R²|RUL|HI|Kпред|Kдан|Kфаз|AТО|Qv|Tобн", text_all):
            continue

        for t in p.xpath(".//w:t", namespaces=NS):
            if not t.text:
                continue

            def repl(m: re.Match[str]) -> str:
                old = int(m.group(1))
                return f"({mapping.get(old, old)})"

            t.text = re.sub(r"\((\d{1,3})\)", repl, t.text)


def cleanup_double_formula_labels(paras: list[etree._Element]) -> None:
    """Remove stale split labels such as `(38)` in `...,(38)(27)`.

    Some Word equation labels are split across several text nodes. When a new
    label is appended, the old split label can remain visually before it. This
    cleanup keeps the final label and clears the stale nodes between the comma
    and the final label.
    """

    for p in paras:
        if not is_formula_paragraph(p):
            continue
        text = para_text(p)
        if not re.search(r"\(\d{1,3}\)\(\d{1,3}\)\s*$", text):
            continue
        nodes = p.xpath(".//w:t|.//m:t", namespaces=NS)
        label = formula_label(p)
        if label is None:
            continue
        final_idx = None
        for idx in range(len(nodes) - 1, -1, -1):
            if (nodes[idx].text or "").strip() == f"({label})":
                final_idx = idx
                break
        if final_idx is None:
            continue
        comma_idx = None
        for idx in range(final_idx - 1, -1, -1):
            if "," in (nodes[idx].text or ""):
                comma_idx = idx
                break
        if comma_idx is None:
            continue
        for node in nodes[comma_idx + 1 : final_idx]:
            node.text = ""


def main() -> None:
    docx = find_docx()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = docx.with_name(f"{docx.stem}.backup_before_formula_logic_cleanup_{timestamp}.docx")
    shutil.copy2(docx, backup)

    with ZipFile(docx, "r") as zin:
        parts = {name: zin.read(name) for name in zin.namelist()}

    root = etree.fromstring(parts["word/document.xml"])
    body = root.find(".//w:body", namespaces=NS)
    if body is None:
        raise RuntimeError("DOCX body not found")
    paras = body.xpath("./w:p", namespaces=NS)
    by_label = formula_by_old_label(paras)

    changes: list[str] = []

    # Move metric definitions to chapter 4: delete early chapter-2 formulas,
    # keep chapter-4 MAE/RMSE/R2 as the authoritative metric block.
    replace_para(
        by_label[15],
        "Для оценки качества прогноза далее используются MAE, RMSE и коэффициент детерминации R²; их расчетные выражения приведены в разделе 4.8.2.",
        paras,
    )
    remove_para(by_label[16])
    changes.append("Removed early MAE/RMSE formulas from chapter 2 and replaced them with a reference to section 4.8.2.")

    # Replace the incorrect chapter-4 RMSE formula with the correct sqrt version
    # cloned from the removed early RMSE formula, preserving equation formatting.
    rmse_clone = copy.deepcopy(by_label[16])
    set_formula_label(rmse_clone, 62)
    by_label[62].getparent().replace(by_label[62], rmse_clone)
    changes.append("Replaced chapter-4 RMSE formula with the square-root RMSE expression.")

    # Clone R2 formula from chapter 5 into chapter 4, after RMSE, then remove
    # the chapter-5 metric repetitions.
    r2_clone = copy.deepcopy(by_label[90])
    set_formula_label(r2_clone, 90)
    insert_after(rmse_clone, r2_clone)
    metric_expl = make_plain_para(
        "где n – число проверочных наблюдений; RULi – фактическое значение остаточного ресурса; RUL̂i – прогноз модели; mean(RUL) – среднее фактическое значение RUL в проверочной выборке.",
        nearest_body_template(paras, by_label[61]),
    )
    insert_after(r2_clone, metric_expl)
    changes.append("Moved R2 formula to section 4.8.2 and added metric-variable explanations.")

    # Chapter 2 explanations.
    insert_after(
        by_label[18],
        make_plain_para(
            "где Nсвоевр – число предупреждений, выданных раньше минимального времени подготовки ТО; Nпред – общее число сформированных предупреждений.",
            nearest_body_template(paras, by_label[18]),
        ),
    )
    insert_after(
        by_label[22],
        make_plain_para(
            "где x – исходное значение признака; xmin и xmax – минимальное и максимальное значения в контрольном диапазоне; W – окно наблюдения; E – энергетический признак; t0 и Δt – начало и длительность окна.",
            nearest_body_template(paras, by_label[22]),
        ),
    )
    changes.append("Added explanations for Kpred, normalization, feature vector and slope in chapter 2.")

    # Chapter 3: replace repeated formulas with references to earlier definitions.
    replace_para(
        by_label[27],
        "Коэффициент готовности для целей ТЗ принимается по формуле (26), а доля своевременных предупреждений – по формуле (18).",
        paras,
    )
    remove_para(by_label[29])
    replace_text_if_contains(
        body.xpath("./w:p", namespaces=NS),
        "где Kготовн – коэффициент готовности участка",
        "где ΔCпр – расчетное снижение потерь от простоя; Cпр,до – потери до внедрения диагностического контура; Cпр,после – ожидаемые потери после внедрения.",
    )
    replace_para(
        by_label[30],
        "Запись телеметрии должна соответствовать базовой структуре наблюдения, заданной формулой (19).",
        paras,
    )
    replace_text_if_contains(
        body.xpath("./w:p", namespaces=NS),
        "где tk – метка времени, ck – номер цикла",
        "В составе записи tk – метка времени, ck – номер цикла, sk – фаза операции, i – номер привода, qi – координата, ωi – скорость, ai – ускорение, Mi – момент, eventk – событие.",
    )
    replace_para(
        by_label[31],
        "Для каждого окна наблюдения W признаковый вектор формируется по составу, заданному формулой (21).",
        paras,
    )
    replace_para(
        by_label[32],
        "Энергетическая составляющая признакового описания должна рассчитываться по произведению момента и угловой скорости; базовый вид такой оценки приведен в формуле (5).",
        paras,
    )
    replace_para(
        by_label[33],
        "Показатель HI должен рассчитываться по нормированным диагностическим признакам и весам, как задано формулой (10).",
        paras,
    )
    replace_para(
        by_label[34],
        "Прогноз RUL задается регрессионной зависимостью, введенной в формуле (17), и уточняется в техническом проектировании для выбранного состава признаков.",
        paras,
    )
    replace_para(
        by_label[36],
        "где Nпот – число потерянных или некорректных записей; Nобщ – общее число ожидаемых записей; Pдоп – допустимая доля потерь. Ограничение на период обновления диагностических данных применяется по формуле (24).",
        paras,
    )
    changes.append("Reworked chapter 3 so the technical assignment references earlier formulas instead of restating them.")

    # Chapter 4 and 5 repeated definitions.
    replace_para(
        by_label[43],
        "Структура проектной записи телеметрии строится на основе базового вектора наблюдения, заданного формулой (19).",
        paras,
    )
    replace_para(
        by_label[63],
        "Дополнительно для оценки диагностической полезности используется доля своевременных предупреждений по формуле (18).",
        paras,
    )
    replace_para(
        by_label[82],
        "Энергетический признак окна используется в том же смысле, что и в формуле (52), то есть через произведение момента и угловой скорости на интервале наблюдения.",
        paras,
    )
    replace_para(
        by_label[83],
        "Наклон сигнала рассчитывается по ранее введенной формуле (22).",
        paras,
    )
    replace_para(
        by_label[84],
        "Нормирование признаков выполняется по формуле (48); при отсутствии нулевого диапазона она совпадает с базовой зависимостью (20).",
        paras,
    )
    replace_para(
        by_label[87],
        "Регрессионная модель использует зависимость RUL = g(FW, HI, θ), введенную в формуле (17).",
        paras,
    )
    replace_text_if_contains(
        body.xpath("./w:p", namespaces=NS),
        "где FW – вектор признаков окна; HI – индекс технического состояния; θ – параметры модели; RUL – прогноз остаточного ресурса.",
        "где FW – вектор признаков окна; HI – индекс технического состояния; θ – параметры регрессионной модели; RUL – прогноз остаточного ресурса.",
    )
    replace_para(
        by_label[88],
        "Качество прогноза в рабочей реализации оценивается по метрикам MAE, RMSE и R², заданным в разделе 4.8.2; в главе 6 по ним приводятся фактические численные результаты.",
        paras,
    )
    remove_para(by_label[89])
    remove_para(by_label[90])
    changes.append("Removed repeated implementation formulas for slope, normalization, generic RUL and metrics; added references to authoritative definitions.")

    # Chapter 6 repeated warning/reliability formulas and missing explanations.
    replace_para(
        by_label[106],
        "Предупреждение в панели мониторинга формируется по правилу (94).",
        paras,
    )
    replace_para(
        by_label[109],
        "где Nкорр – число корректных записей телеметрии; Nобщ – общее число записей; Nзап,phase – число записей с заполненной фазовой меткой. Своевременность предупреждений контролируется по формуле (18).",
        paras,
    )
    insert_after(
        by_label[113],
        make_plain_para(
            "где Qv – интегральная оценка варианта обслуживания; wj – вес j-го критерия; rv,j – нормированная оценка v-го варианта по j-му критерию; m – число критериев сравнения.",
            nearest_body_template(paras, by_label[113]),
        ),
    )
    changes.append("Replaced repeated chapter-6 warning/Kpred formulas with references and added explanations for reliability and comparison formulas.")

    # Refresh paragraph/formula list after structural edits.
    paras_after = body.xpath("./w:p", namespaces=NS)
    old_to_new: dict[int, int] = {}
    number = 1
    for p in paras_after:
        if is_formula_paragraph(p):
            old = formula_label(p)
            if old is None:
                continue
            old_to_new[old] = number
            set_formula_label(p, number)
            number += 1
    cleanup_double_formula_labels(paras_after)

    # First update generic formula references according to the old->new map.
    update_formula_references(root, old_to_new)

    # Then fix references whose target formula was deliberately removed.
    def n(old: int) -> int:
        if old not in old_to_new:
            raise RuntimeError(f"Formula {old} no longer has a mapping")
        return old_to_new[old]

    custom_replacements = [
        (
            "В данном подразделе повторно не приводятся формулы RUL и метрик качества",
            f"В данном подразделе повторно не приводятся формулы RUL и метрик качества: целевая переменная RUL рассчитывается по формулам ({n(85)})–({n(86)}), регрессионная зависимость используется по формуле ({n(17)}), а MAE, RMSE и R² – по формулам ({n(61)})–({n(90)}). Далее приводятся только численные результаты апробации. Логика программной реализации расчета HI/RUL кратко приведена в приложении Г.",
        ),
        (
            "Предупреждение в панели мониторинга формируется по правилу",
            f"Предупреждение в панели мониторинга формируется по правилу ({n(94)}).",
        ),
        (
            "Расчетные зависимости и критерии из формул",
            None,
        ),
    ]
    for needle, repl in custom_replacements:
        if repl is None:
            continue
        replace_text_if_contains(root.xpath(".//w:body//w:p", namespaces=NS), needle, repl)

    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone="yes"
    )

    tmp = docx.with_suffix(".tmp_formula_cleanup.docx")
    with ZipFile(tmp, "w", ZIP_DEFLATED) as zout:
        for name, data in parts.items():
            zout.writestr(name, data)
    tmp.replace(docx)

    report = {
        "docx": str(docx),
        "backup": str(backup),
        "formula_count": number - 1,
        "old_to_new": old_to_new,
        "changes": changes,
    }
    report_path = Path("scratch") / "formula_logic_cleanup_20260619_report.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        "\n".join(
            [
                f"DOCX: {report['docx']}",
                f"Backup: {report['backup']}",
                f"Formula count after cleanup: {report['formula_count']}",
                "Changes:",
                *[f"- {c}" for c in changes],
                "Old to new formula numbers:",
                *[f"{old}->{new}" for old, new in sorted(old_to_new.items())],
            ]
        ),
        encoding="utf-8",
    )
    print(report_path)
    print(f"backup={backup}")
    print(f"formulas={number - 1}")


if __name__ == "__main__":
    main()
