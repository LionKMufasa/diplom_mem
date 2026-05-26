from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path

from docx import Document

from compress_vkr_filled_sections import find_index, replace_section, set_update_fields_on_open
from fix_vkr_citations_bibliography_formulas_tz import improve_formulas


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: insert_vkr_chapter4_technical_design.py <docx> <chapter4.md>")

    docx_path = Path(sys.argv[1])
    chapter4_path = Path(sys.argv[2])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = docx_path.with_name(
        f"{docx_path.stem}.backup_before_chapter4_technical_design_{timestamp}{docx_path.suffix}"
    )
    shutil.copy2(docx_path, backup)

    doc = Document(str(docx_path))
    replace_section(doc, "Техническое проектирование", "Рабочее проектирование", chapter4_path, 1, True)
    doc.paragraphs[find_index(doc, "Техническое проектирование")].paragraph_format.page_break_before = True
    formula_changes = improve_formulas(doc)
    doc.save(str(docx_path))
    set_update_fields_on_open(docx_path)

    print(f"Inserted chapter 4 into {docx_path}")
    print(f"Backup: {backup}")
    print(f"Formula replacements/format pass: {formula_changes}")


if __name__ == "__main__":
    main()
