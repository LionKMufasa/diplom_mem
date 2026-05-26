from __future__ import annotations

import argparse
import csv
import re
import shutil
import tempfile
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


def clean_paragraph_text(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS)).strip()


def paragraph_alignment(paragraph: etree._Element) -> str | None:
    node = paragraph.find("./w:pPr/w:jc", NS)
    if node is None:
        return None
    return node.get(qn("w", "val"))


def has_omml(paragraph: etree._Element) -> bool:
    return bool(paragraph.xpath(".//m:oMath|.//m:oMathPara", namespaces=NS))


def is_formula_candidate(text: str, paragraph: etree._Element) -> bool:
    if not text or paragraph_alignment(paragraph) != "center":
        return False
    if text.startswith("["):
        return False
    if re.search(r"https?://|\\|\.docx|\.csv|\.json|\.ttt|\.lua|\.py|\.ps1", text):
        return False
    if text.endswith("."):
        return False

    arrow = chr(0x2192)
    sigma = chr(0x03A3)
    sqrt = chr(0x221A)
    core_markers = {"=", "<", ">", chr(0x2264), chr(0x2265), sigma, sqrt, chr(0x00B7), arrow}

    if text.startswith("CoppeliaSim ") and ("->" in text or arrow in text):
        return False

    has_core_marker = any(marker in text for marker in core_markers) or "->" in text
    if not has_core_marker:
        return False

    if "=" in text:
        left = text.split("=", 1)[0].strip()
        if re.search(r"\s", left) and len(left) > 18 and sigma not in left and sqrt not in left:
            return False

    return True


def m_text(value: str) -> etree._Element:
    run = etree.Element(qn("m", "r"))
    text = etree.SubElement(run, qn("m", "t"))
    text.set(qn("xml", "space"), "preserve")
    text.text = value
    return run


def math_group(children: list[etree._Element]) -> etree._Element:
    group = etree.Element(qn("m", "e"))
    for child in children:
        group.append(child)
    return group


def simple_group(text: str) -> etree._Element:
    return math_group([m_text(text)])


def make_sub(base: etree._Element, sub: str) -> etree._Element:
    node = etree.Element(qn("m", "sSub"))
    node.append(math_group([base]))
    sub_node = etree.SubElement(node, qn("m", "sub"))
    sub_node.append(m_text(sub))
    return node


def make_sup(base: etree._Element, sup: str) -> etree._Element:
    node = etree.Element(qn("m", "sSup"))
    node.append(math_group([base]))
    sup_node = etree.SubElement(node, qn("m", "sup"))
    sup_node.append(m_text(sup))
    return node


def make_subsup(base: etree._Element, sub: str, sup: str) -> etree._Element:
    node = etree.Element(qn("m", "sSubSup"))
    node.append(math_group([base]))
    sub_node = etree.SubElement(node, qn("m", "sub"))
    sub_node.append(m_text(sub))
    sup_node = etree.SubElement(node, qn("m", "sup"))
    sup_node.append(m_text(sup))
    return node


def make_hat(children: list[etree._Element]) -> etree._Element:
    node = etree.Element(qn("m", "acc"))
    props = etree.SubElement(node, qn("m", "accPr"))
    char = etree.SubElement(props, qn("m", "chr"))
    char.set(qn("m", "val"), chr(0x0302))
    node.append(math_group(children))
    return node


def make_rad(children: list[etree._Element]) -> etree._Element:
    node = etree.Element(qn("m", "rad"))
    props = etree.SubElement(node, qn("m", "radPr"))
    hide = etree.SubElement(props, qn("m", "degHide"))
    hide.set(qn("m", "val"), "on")
    node.append(math_group(children))
    return node


def is_word_char(ch: str) -> bool:
    return ch.isalnum()


def find_matching_parenthesis(text: str, open_index: int) -> int:
    depth = 0
    for index in range(open_index, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                return index
    return -1


def parse_braced_or_word(text: str, index: int) -> tuple[str, int]:
    if index >= len(text):
        return "", index
    if text[index] == "{":
        end = text.find("}", index + 1)
        if end != -1:
            return text[index + 1 : end], end + 1
    start = index
    while index < len(text):
        ch = text[index]
        if is_word_char(ch) or ch in {",", "-", "."}:
            index += 1
        else:
            break
    return text[start:index], index


def parse_token(text: str, index: int) -> tuple[etree._Element | None, int]:
    sigma = chr(0x03A3)
    sup_two = chr(0x00B2)
    combining_hat = chr(0x0302)

    if text[index] == sigma:
        base: etree._Element = m_text(sigma)
        index += 1
    else:
        start = index
        while index < len(text) and is_word_char(text[index]):
            index += 1
        if start == index:
            return None, index
        base_text = text[start:index]
        base = m_text(base_text)

    if index < len(text) and text[index] == combining_hat:
        base = make_hat([base])
        index += 1

    sub = None
    sup = None

    if index < len(text) and text[index] == "_":
        sub, index = parse_braced_or_word(text, index + 1)
    if index < len(text) and text[index] == "^":
        sup, index = parse_braced_or_word(text, index + 1)
    elif index < len(text) and text[index] == sup_two:
        sup = "2"
        index += 1

    if sub and sup:
        return make_subsup(base, sub, sup), index
    if sub:
        return make_sub(base, sub), index
    if sup:
        return make_sup(base, sup), index
    return base, index


def build_math_children(text: str) -> list[etree._Element]:
    children: list[etree._Element] = []
    index = 0
    arrow = chr(0x2192)
    sqrt = chr(0x221A)

    while index < len(text):
        if text.startswith("->", index):
            children.append(m_text(arrow))
            index += 2
            continue

        if text.startswith("sqrt(", index):
            close = find_matching_parenthesis(text, index + 4)
            if close != -1:
                inner = text[index + 5 : close]
                children.append(make_rad(build_math_children(inner)))
                index = close + 1
                continue

        if text[index] == sqrt and index + 1 < len(text) and text[index + 1] == "(":
            close = find_matching_parenthesis(text, index + 1)
            if close != -1:
                inner = text[index + 2 : close]
                children.append(make_rad(build_math_children(inner)))
                index = close + 1
                continue

        if is_word_char(text[index]) or text[index] == chr(0x03A3):
            token, next_index = parse_token(text, index)
            if token is not None and next_index > index:
                children.append(token)
                index = next_index
                continue

        children.append(m_text(text[index]))
        index += 1

    return children


def replace_with_omml(paragraph: etree._Element, formula_text: str) -> None:
    ppr = paragraph.find("./w:pPr", NS)
    for child in list(paragraph):
        if child is not ppr:
            paragraph.remove(child)

    math_para = etree.Element(qn("m", "oMathPara"))
    math_para_pr = etree.SubElement(math_para, qn("m", "oMathParaPr"))
    jc = etree.SubElement(math_para_pr, qn("m", "jc"))
    jc.set(qn("m", "val"), "centerGroup")

    omath = etree.SubElement(math_para, qn("m", "oMath"))
    for child in build_math_children(formula_text):
        omath.append(child)

    paragraph.append(math_para)


def convert_docx(docx_path: Path, dry_run: bool) -> dict[str, object]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = docx_path.with_name(f"{docx_path.stem}.backup_before_equation_conversion_{timestamp}{docx_path.suffix}")
    report_dir = Path.cwd() / "reports"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / f"vkr_equation_conversion_{timestamp}.tsv"

    with ZipFile(docx_path, "r") as package:
        xml = package.read("word/document.xml")

    document = etree.fromstring(xml)
    paragraphs = document.xpath("//w:p", namespaces=NS)
    report_rows: list[dict[str, str]] = []
    converted = 0
    skipped_existing = 0

    for number, paragraph in enumerate(paragraphs, start=1):
        text = clean_paragraph_text(paragraph)
        if not is_formula_candidate(text, paragraph):
            continue

        status = "dry_run" if dry_run else "converted"
        if has_omml(paragraph):
            status = "skipped_existing"
            skipped_existing += 1
        elif not dry_run:
            replace_with_omml(paragraph, text)
            converted += 1

        report_rows.append(
            {
                "paragraph_index": str(number),
                "status": status,
                "original": text,
            }
        )

    with report_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["paragraph_index", "status", "original"], delimiter="\t")
        writer.writeheader()
        writer.writerows(report_rows)

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
        "would_convert": len([row for row in report_rows if row["status"] == "dry_run"]),
        "converted": converted,
        "skipped_existing": skipped_existing,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = convert_docx(args.docx.resolve(), args.dry_run)
    for key, value in result.items():
        print(f"{key}\t{value}")


if __name__ == "__main__":
    main()
