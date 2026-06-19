from __future__ import annotations

import re
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCX_DIR = PROJECT_ROOT / "вкр"
HELPER_PATH = PROJECT_ROOT / "scripts" / "apply_vkr_formula_logic_cleanup_20260619.py"

import importlib.util

spec = importlib.util.spec_from_file_location("formula_helper", HELPER_PATH)
helper = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(helper)


def find_working_docx() -> Path:
    candidates = [
        p
        for p in DOCX_DIR.glob("*.docx")
        if "2026" in p.name and "backup" not in p.name.lower() and not p.name.startswith("~$")
    ]
    if not candidates:
        raise FileNotFoundError("Working VKR DOCX was not found in the vkr folder")
    return candidates[0]


def should_update_formula_refs(text: str) -> bool:
    if not re.search(r"\(\d{1,3}\)", text):
        return False
    keywords = (
        "формул",
        "формуле",
        "формулы",
        "выражени",
        "зависимост",
        "рассчитывается",
        "метрик",
        "MAE",
        "RMSE",
        "R²",
        "RUL",
        "HI",
        "AТО",
        "Kдан",
        "Kфаз",
        "Kпред",
        "Qv",
        "Tобн",
    )
    return any(keyword in text for keyword in keywords)


def update_text_node_refs(text: str, mapping: dict[int, int]) -> str:
    def repl(match: re.Match[str]) -> str:
        old = int(match.group(1))
        return f"({mapping.get(old, old)})"

    return re.sub(r"\((\d{1,3})\)", repl, text)


def main() -> None:
    docx_path = find_working_docx()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = docx_path.with_name(f"{docx_path.stem}.backup_before_formula_renumber_after_ch6_{timestamp}.docx")
    shutil.copy2(docx_path, backup_path)

    with ZipFile(docx_path, "r") as zin:
        files = {name: zin.read(name) for name in zin.namelist()}

    root = etree.fromstring(files["word/document.xml"])
    paragraphs = root.xpath(".//w:body//w:p", namespaces=helper.NS)

    formula_paragraphs: list[etree._Element] = []
    old_labels: list[int] = []
    for paragraph in paragraphs:
        if helper.is_formula_paragraph(paragraph):
            label = helper.formula_label(paragraph)
            if label is not None:
                formula_paragraphs.append(paragraph)
                old_labels.append(label)

    old_to_new: dict[int, int] = {}
    for new_number, paragraph in enumerate(formula_paragraphs, start=1):
        old_number = helper.formula_label(paragraph)
        if old_number is None:
            continue
        old_to_new[old_number] = new_number
        helper.set_formula_label(paragraph, new_number)

    refs_changed = 0
    in_bibliography = False
    for paragraph in paragraphs:
        text = helper.para_text(paragraph)
        if text.startswith("Список использованных источников"):
            in_bibliography = True
        elif text.startswith("Приложение А"):
            in_bibliography = False

        if in_bibliography or helper.is_formula_paragraph(paragraph):
            continue
        if not should_update_formula_refs(text):
            continue

        for node in paragraph.xpath(".//w:t", namespaces=helper.NS):
            if not node.text:
                continue
            new_text = update_text_node_refs(node.text, old_to_new)
            if new_text != node.text:
                node.text = new_text
                refs_changed += 1

    helper.cleanup_double_formula_labels(root.xpath(".//w:body//w:p", namespaces=helper.NS))

    files["word/document.xml"] = etree.tostring(
        root,
        xml_declaration=True,
        encoding="UTF-8",
        standalone=True,
    )

    tmp_path = docx_path.with_suffix(".tmp_formula_renumber_after_ch6.docx")
    with ZipFile(tmp_path, "w", ZIP_DEFLATED) as zout:
        for name, data in files.items():
            zout.writestr(name, data)
    tmp_path.replace(docx_path)

    final_labels = list(range(1, len(formula_paragraphs) + 1))
    duplicates = sorted([n for n, c in Counter(final_labels).items() if c > 1])

    print(f"docx={docx_path}")
    print(f"backup={backup_path}")
    print(f"formula_count={len(formula_paragraphs)}")
    print(f"old_labels={old_labels}")
    print(f"old_to_new={old_to_new}")
    print(f"refs_changed={refs_changed}")
    print(f"duplicates={duplicates}")


if __name__ == "__main__":
    main()
