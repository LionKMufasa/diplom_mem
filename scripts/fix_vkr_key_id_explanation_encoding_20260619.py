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


def main() -> None:
    docx = helper.find_docx()
    backup = docx.with_name(
        f"{docx.stem}.backup_before_key_id_encoding_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    )
    shutil.copy2(docx, backup)

    with ZipFile(docx, "r") as zin:
        parts = {name: zin.read(name) for name in zin.namelist()}

    root = etree.fromstring(parts["word/document.xml"])
    body = root.find(".//w:body", namespaces=helper.NS)
    if body is None:
        raise RuntimeError("Body not found")
    paras = body.xpath("./w:p", namespaces=helper.NS)
    formulas = helper.formula_by_old_label(paras)

    def next_nonempty_after(formula_label: int):
        target = formulas[formula_label]
        idx = paras.index(target)
        for j in range(idx + 1, min(idx + 6, len(paras))):
            if helper.para_text(paras[j]):
                return paras[j]
        raise RuntimeError(f"No paragraph after formula {formula_label}")

    helper.set_para_text(
        next_nonempty_after(73),
        "где key – набор тегов временного ряда; value – набор сохраняемых измеряемых и расчетных значений; robotid, axisid и cycleid – идентификаторы робота, оси и цикла; phase, layer и item – фаза, слой и переносимый объект.",
    )
    helper.set_para_text(
        next_nonempty_after(74),
        "где id_k – уникальный ключ записи; phase_k и t_k – фаза и временная метка k-й записи; функция hash(·) используется для формирования воспроизводимого идентификатора и защиты от неотличимых дублей.",
    )

    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone="yes"
    )
    tmp = docx.with_suffix(".tmp_key_id_encoding_fix.docx")
    with ZipFile(tmp, "w", ZIP_DEFLATED) as zout:
        for name, data in parts.items():
            zout.writestr(name, data)
    tmp.replace(docx)
    print(f"backup={backup}")


if __name__ == "__main__":
    main()
