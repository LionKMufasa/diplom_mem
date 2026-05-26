from __future__ import annotations

import argparse
import csv
import re
import shutil
import tempfile
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "xml": "http://www.w3.org/XML/1998/namespace",
}

for prefix, uri in NS.items():
    if prefix != "xml":
        etree.register_namespace(prefix, uri)


def qn(prefix: str, tag: str) -> str:
    return f"{{{NS[prefix]}}}{tag}"


TOKEN_RE = re.compile(
    r"(?<![\wА-Яа-яЁё])"
    r"(?P<base>[A-Za-zА-Яа-яЁёΔΣΩαβγδεθμσπω]+)"
    r"_"
    r"(?P<sub>\{[^}]+\}|[A-Za-zА-Яа-яЁё0-9]+(?:,[A-Za-zА-Яа-яЁё0-9]+)*)"
    r"(?![A-Za-zА-Яа-яЁё0-9_])"
)

KNOWN_MULTI_BASES = {"HI", "RUL", "RMS", "RMSE", "MAE"}
KNOWN_FIELD_BASES_WITH_INDEX = {"phase", "layer", "item", "event", "carrying"}
ALLOWED_SINGLE_BASES = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
ALLOWED_SINGLE_BASES.update("АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ")
ALLOWED_SINGLE_BASES.update("абвгдежзиклмнопрстуфхцчшщэюя")
ALLOWED_SINGLE_BASES.update("αβγδεθμσπωΔΣΩ")
SKIP_SUBSCRIPTS = {"hat"}


def is_inside_omml(element: etree._Element) -> bool:
    parent = element.getparent()
    while parent is not None:
        if parent.tag.startswith(f"{{{NS['m']}}}"):
            return True
        parent = parent.getparent()
    return False


def paragraph_style(element: etree._Element) -> str:
    parent = element
    while parent is not None and parent.tag != qn("w", "p"):
        parent = parent.getparent()
    if parent is None:
        return ""
    style = parent.find("./w:pPr/w:pStyle", NS)
    return style.get(qn("w", "val")) if style is not None else ""


def should_convert(base: str, subscript: str) -> bool:
    clean_sub = subscript.strip("{}")
    if clean_sub in SKIP_SUBSCRIPTS:
        return False
    if len(base) == 1 and base in ALLOWED_SINGLE_BASES:
        return True
    if base in KNOWN_MULTI_BASES:
        return True
    if base in KNOWN_FIELD_BASES_WITH_INDEX and len(clean_sub) == 1:
        return True
    return False


def split_indexed_text(text: str) -> list[tuple[str, bool]]:
    parts: list[tuple[str, bool]] = []
    position = 0
    for match in TOKEN_RE.finditer(text):
        base = match.group("base")
        subscript = match.group("sub")
        if not should_convert(base, subscript):
            continue

        if match.start() > position:
            parts.append((text[position : match.start()], False))
        parts.append((base, False))
        parts.append((subscript.strip("{}"), True))
        position = match.end()

    if position == 0:
        return [(text, False)]
    if position < len(text):
        parts.append((text[position:], False))
    return [(value, is_subscript) for value, is_subscript in parts if value]


def clone_rpr(run: etree._Element, subscript: bool) -> etree._Element | None:
    rpr = run.find("./w:rPr", NS)
    clone = deepcopy(rpr) if rpr is not None else etree.Element(qn("w", "rPr"))
    if subscript:
        for existing in clone.findall("./w:vertAlign", NS):
            clone.remove(existing)
        vert = etree.SubElement(clone, qn("w", "vertAlign"))
        vert.set(qn("w", "val"), "subscript")
    if len(clone) == 0 and not clone.attrib:
        return None
    return clone


def make_run(template: etree._Element, value: str, subscript: bool, carry_non_text: bool = False) -> etree._Element:
    new_run = etree.Element(qn("w", "r"))
    rpr = clone_rpr(template, subscript)
    if rpr is not None:
        new_run.append(rpr)
    if carry_non_text:
        for child in template:
            if child.tag not in {qn("w", "rPr"), qn("w", "t")}:
                new_run.append(deepcopy(child))
    text = etree.SubElement(new_run, qn("w", "t"))
    if value[:1].isspace() or value[-1:].isspace():
        text.set(qn("xml", "space"), "preserve")
    text.text = value
    return new_run


def run_is_simple_text(run: etree._Element) -> bool:
    allowed = {qn("w", "rPr"), qn("w", "t"), qn("w", "lastRenderedPageBreak")}
    return all(child.tag in allowed for child in run)


def convert_document(docx_path: Path, dry_run: bool) -> dict[str, object]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = docx_path.with_name(f"{docx_path.stem}.backup_before_inline_indices_{timestamp}{docx_path.suffix}")
    report_dir = Path.cwd() / "reports"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / f"vkr_inline_indices_{timestamp}.tsv"

    with ZipFile(docx_path, "r") as package:
        xml = package.read("word/document.xml")

    document = etree.fromstring(xml)
    rows: list[dict[str, str]] = []
    converted_tokens = 0
    converted_runs = 0

    for text_node in list(document.xpath("//w:t", namespaces=NS)):
        text = text_node.text or ""
        if "_" not in text:
            continue
        if is_inside_omml(text_node):
            continue
        style = paragraph_style(text_node)
        if style.lower().startswith("toc"):
            continue

        parts = split_indexed_text(text)
        if len(parts) == 1 and parts[0] == (text, False):
            continue

        sub_count = sum(1 for _, is_sub in parts if is_sub)
        run = text_node.getparent()
        if run is None or run.tag != qn("w", "r") or not run_is_simple_text(run):
            continue

        converted_tokens += sub_count
        converted_runs += 1
        rows.append(
            {
                "status": "dry_run" if dry_run else "converted",
                "style": style,
                "original": text,
                "converted_tokens": str(sub_count),
            }
        )

        if dry_run:
            continue

        parent = run.getparent()
        insert_at = parent.index(run)
        parent.remove(run)
        for offset, (value, is_subscript) in enumerate(parts):
            parent.insert(insert_at + offset, make_run(run, value, is_subscript, carry_non_text=(offset == 0)))

    with report_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["status", "style", "original", "converted_tokens"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    if not dry_run:
        shutil.copy2(docx_path, backup_path)
        new_xml = etree.tostring(document, xml_declaration=True, encoding="UTF-8", standalone=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx", dir=docx_path.parent) as tmp:
            tmp_path = Path(tmp.name)
        try:
            with ZipFile(docx_path, "r") as zin, ZipFile(tmp_path, "w", ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    data = new_xml if item.filename == "word/document.xml" else zin.read(item.filename)
                    zout.writestr(item, data)
            shutil.move(str(tmp_path), docx_path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    return {
        "docx": str(docx_path),
        "backup": "" if dry_run else str(backup_path),
        "report": str(report_path),
        "dry_run": dry_run,
        "converted_runs": converted_runs,
        "converted_tokens": converted_tokens,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = convert_document(args.docx.resolve(), args.dry_run)
    for key, value in result.items():
        print(f"{key}\t{value}")


if __name__ == "__main__":
    main()
