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

NS = helper.NS


def main() -> None:
    docx = helper.find_docx()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = docx.with_name(
        f"{docx.stem}.backup_before_formula_explanation_placement_{timestamp}.docx"
    )
    shutil.copy2(docx, backup)

    with ZipFile(docx, "r") as zin:
        parts = {name: zin.read(name) for name in zin.namelist()}

    root = etree.fromstring(parts["word/document.xml"])
    body = root.find(".//w:body", namespaces=NS)
    if body is None:
        raise RuntimeError("Body not found")
    paras = body.xpath("./w:p", namespaces=NS)
    formulas = helper.formula_by_old_label(paras)

    # Replace the incomplete degradation explanation after formulas (61)-(63).
    helper.replace_text_if_contains(
        paras,
        "где Mi(t) – измеренный момент на оси",
        "где M_i(t) – измеренный момент на оси; M_i,deg(t) – момент после введения диагностического сценария; α_i(N) – коэффициент деградации i-й оси; α_i,0 – начальное значение коэффициента; k_i – скорость роста деградации; Nкр – цикл, соответствующий предельному состоянию; ε_i(t) – шум измерения; HI_i(N) – индекс технического состояния оси; α_i,кр – критическое значение коэффициента деградации.",
    )

    # Remove the misplaced alpha explanation after formula (65).
    for p in list(paras):
        if "где α_i,кр – критическое значение коэффициента деградации" in helper.para_text(p):
            p.getparent().remove(p)
            break

    # Add missing explanation for limit-state rule (64).
    helper.insert_after(
        formulas[64],
        helper.make_plain_para(
            "где D_lim – бинарный признак достижения предельного состояния; HI_i(N) – индекс состояния i-й оси; HIкр – критическое значение индекса; x_j(N) – j-й диагностический признак; xкр,j – допустимый порог этого признака.",
            helper.nearest_body_template(paras, formulas[64]),
        ),
    )

    # Add explanation for frequency, acceleration and telemetry record formulas.
    helper.insert_after(
        formulas[67],
        helper.make_plain_para(
            "где f_s – расчетная частота обновления графиков в CoppeliaSim; T_s – период обновления; a_i(k) – ускорение i-й оси на k-м отсчете; ω_i(k) и ω_i(k - 1) – соседние значения угловой скорости; t_k и t_{k-1} – соседние временные метки; d_k – запись телеметрии с номером цикла N, фазой, слоем, объектом, осью и признаком переноса груза carrying_k.",
            helper.nearest_body_template(paras, formulas[67]),
        ),
    )

    # Split key/value/id explanations around the database formulas.
    helper.insert_after(
        formulas[73],
        helper.make_plain_para(
            "где key – набор тегов временного ряда; value – набор сохраняемых измеряемых и расчетных значений; robotid, axisid и cycleid – идентификаторы робота, оси и цикла; phase, layer и item – фаза, слой и переносимый объект.",
            helper.nearest_body_template(paras, formulas[73]),
        ),
    )
    helper.replace_text_if_contains(
        body.xpath("./w:p", namespaces=NS),
        "где key – набор тегов временного ряда; value – набор сохраняемых измеряемых и расчетных значений; robotid, axisid и cycleid",
        "где id_k – уникальный ключ записи; phase_k и t_k – фаза и временная метка k-й записи; функция hash(·) используется для формирования воспроизводимого идентификатора и защиты от неотличимых дублей.",
    )

    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone="yes"
    )
    tmp = docx.with_suffix(".tmp_formula_explanation_placement.docx")
    with ZipFile(tmp, "w", ZIP_DEFLATED) as zout:
        for name, data in parts.items():
            zout.writestr(name, data)
    tmp.replace(docx)

    print(f"backup={backup}")


if __name__ == "__main__":
    main()
