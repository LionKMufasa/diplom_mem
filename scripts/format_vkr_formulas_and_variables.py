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


def ensure_child(parent: etree._Element, tag: str, after: etree._Element | None = None) -> etree._Element:
    child = parent.find(f"./{tag}", NS)
    if child is not None:
        return child
    child = etree.Element(qn(*tag.split(":")))
    if after is not None and after.getparent() is parent:
        parent.insert(parent.index(after) + 1, child)
    else:
        parent.insert(0, child)
    return child


def get_or_create_ppr(paragraph: etree._Element) -> etree._Element:
    ppr = paragraph.find("./w:pPr", NS)
    if ppr is None:
        ppr = etree.Element(qn("w", "pPr"))
        paragraph.insert(0, ppr)
    return ppr


def set_paragraph_tabs(paragraph: etree._Element, center_pos: int, right_pos: int) -> None:
    ppr = get_or_create_ppr(paragraph)
    for tabs in ppr.findall("./w:tabs", NS):
        ppr.remove(tabs)
    tabs = etree.Element(qn("w", "tabs"))
    tab_center = etree.SubElement(tabs, qn("w", "tab"))
    tab_center.set(qn("w", "val"), "center")
    tab_center.set(qn("w", "pos"), str(center_pos))
    tab_right = etree.SubElement(tabs, qn("w", "tab"))
    tab_right.set(qn("w", "val"), "right")
    tab_right.set(qn("w", "pos"), str(right_pos))
    ppr.append(tabs)

    jc = ppr.find("./w:jc", NS)
    if jc is None:
        jc = etree.SubElement(ppr, qn("w", "jc"))
    jc.set(qn("w", "val"), "left")


def make_text_run(text: str = "", *, tab_before: bool = False, size_half_points: int = 28) -> etree._Element:
    run = etree.Element(qn("w", "r"))
    rpr = etree.SubElement(run, qn("w", "rPr"))
    fonts = etree.SubElement(rpr, qn("w", "rFonts"))
    fonts.set(qn("w", "ascii"), "Times New Roman")
    fonts.set(qn("w", "hAnsi"), "Times New Roman")
    fonts.set(qn("w", "cs"), "Times New Roman")
    size = etree.SubElement(rpr, qn("w", "sz"))
    size.set(qn("w", "val"), str(size_half_points))
    size_cs = etree.SubElement(rpr, qn("w", "szCs"))
    size_cs.set(qn("w", "val"), str(size_half_points))
    if tab_before:
        etree.SubElement(run, qn("w", "tab"))
    if text:
        t = etree.SubElement(run, qn("w", "t"))
        t.text = text
    return run


def set_math_run_font(math: etree._Element, size_half_points: int = 28) -> int:
    changed = 0
    for run in math.xpath(".//m:r", namespaces=NS):
        rpr = run.find("./w:rPr", NS)
        if rpr is None:
            rpr = etree.Element(qn("w", "rPr"))
            m_rpr = run.find("./m:rPr", NS)
            if m_rpr is not None:
                run.insert(run.index(m_rpr) + 1, rpr)
            else:
                run.insert(0, rpr)
        fonts = rpr.find("./w:rFonts", NS)
        if fonts is None:
            fonts = etree.SubElement(rpr, qn("w", "rFonts"))
        fonts.set(qn("w", "ascii"), "Cambria Math")
        fonts.set(qn("w", "hAnsi"), "Cambria Math")
        fonts.set(qn("w", "cs"), "Cambria Math")
        for tag in ("sz", "szCs"):
            node = rpr.find(f"./w:{tag}", NS)
            if node is None:
                node = etree.SubElement(rpr, qn("w", tag))
            node.set(qn("w", "val"), str(size_half_points))
        changed += 1
    return changed


def usable_width_twips(document: etree._Element) -> int:
    sect = document.find(".//w:sectPr", NS)
    if sect is None:
        return 9360
    pg_sz = sect.find("./w:pgSz", NS)
    pg_mar = sect.find("./w:pgMar", NS)
    if pg_sz is None or pg_mar is None:
        return 9360
    width = int(pg_sz.get(qn("w", "w"), "11910"))
    left = int(pg_mar.get(qn("w", "left"), "1134"))
    right = int(pg_mar.get(qn("w", "right"), "1134"))
    return width - left - right


def format_formula_paragraphs(document: etree._Element) -> dict[str, int]:
    width = usable_width_twips(document)
    center_pos = width // 2
    right_pos = width
    paragraphs = document.xpath("//w:p[.//m:oMath]", namespaces=NS)
    numbered = 0
    math_runs = 0

    for number, paragraph in enumerate(paragraphs, start=1):
        math = paragraph.find("./m:oMath", NS)
        if math is None:
            math_para = paragraph.find("./m:oMathPara", NS)
            if math_para is not None:
                math = math_para.find("./m:oMath", NS)
        if math is None:
            continue

        math = deepcopy(math)
        math_runs += set_math_run_font(math, 28)
        set_paragraph_tabs(paragraph, center_pos, right_pos)
        ppr = paragraph.find("./w:pPr", NS)

        for child in list(paragraph):
            if child is not ppr:
                paragraph.remove(child)

        paragraph.append(make_text_run(tab_before=True))
        paragraph.append(math)
        paragraph.append(make_text_run(f"({number})", tab_before=True))
        numbered += 1

    return {"formulas_numbered": numbered, "math_runs_sized": math_runs}


EXPLICIT_INDEX_RE = re.compile(
    r"(?<![\wА-Яа-яЁё])"
    r"(?P<base>[A-Za-zА-Яа-яЁёΔΣΩαβγδεθμσπω]+)"
    r"_"
    r"(?P<sub>\{[^}]+\}|[A-Za-zА-Яа-яЁё0-9]+(?:,[A-Za-zА-Яа-яЁё0-9]+)*)"
    r"(?![A-Za-zА-Яа-яЁё0-9_])"
)

NAMED_INDEX_PATTERNS: list[tuple[re.Pattern[str], str, str]] = []


def add_named_pattern(base: str, subs: list[str]) -> None:
    sub_pattern = "|".join(re.escape(s) for s in sorted(subs, key=len, reverse=True))
    pattern = re.compile(rf"(?<![\wА-Яа-яЁё])({re.escape(base)})({sub_pattern})(?![\wА-Яа-яЁё])")
    NAMED_INDEX_PATTERNS.append((pattern, base, ""))


add_named_pattern("D", ["clean", "raw", "lim"])
add_named_pattern("A", ["ТО", "то"])
add_named_pattern("C", ["экспл", "рем", "инф", "пр", "бр", "вн", "ТО", "то", "ч"])
add_named_pattern("E", ["год", "i"])
add_named_pattern("F", ["W"])
add_named_pattern("K", ["готовн", "пред", "дан", "фаз", "зм", "гр", "з,i"])
add_named_pattern("M", ["i,deg", "max", "доп", "ср", "rms", "i"])
add_named_pattern("N", ["своевр", "ожид", "пред", "общ", "корр", "тек", "лист", "созд", "пер", "кр,i", "пал", "кр", "пот", "уп", "сл", "ав", "зап", "p", "s"])
add_named_pattern("P", ["потерь", "пред", "отк", "доп", "пот", "i"])
add_named_pattern("Q", ["уп"])
add_named_pattern("RUL", ["N"])
add_named_pattern("T", ["работ", "прост", "набл", "смена", "пал", "обн", "пл", "рез", "см", "сек", "час", "ср"])
add_named_pattern("V", ["смена", "сут", "сек", "час"])
add_named_pattern("a", ["max", "i"])
add_named_pattern("c", ["k"])
add_named_pattern("f", ["кр,j", "s", "j"])
add_named_pattern("q", ["i"])
add_named_pattern("n", ["сл", "гр", "уп"])
add_named_pattern("r", ["j"])
add_named_pattern("s", ["k"])
add_named_pattern("t", ["кр,i", "пр", "k", "0"])
add_named_pattern("w", ["j"])
add_named_pattern("x", ["кр,j", "max", "min", "j"])
add_named_pattern("α", ["i,кр", "i"])
add_named_pattern("β", ["s"])
add_named_pattern("ε", ["i"])
add_named_pattern("σ", ["M", "x"])
add_named_pattern("ω", ["ср", "i"])
add_named_pattern("ΔC", ["пр"])
add_named_pattern("E", ["год"])
add_named_pattern("T", ["ок"])

KNOWN_MULTI_BASES = {"HI", "RUL", "RMS", "RMSE", "MAE", "ΔC"}
KNOWN_FIELD_BASES_WITH_INDEX = {"phase", "layer", "item", "event", "carrying"}
SKIP_SUBSCRIPTS = {"hat", "id", "raw", "features", "health", "events", "start", "end", "level"}


def should_convert_explicit(base: str, subscript: str) -> bool:
    clean = subscript.strip("{}")
    if base == "D" and clean in {"raw", "clean", "lim"}:
        return True
    if clean in SKIP_SUBSCRIPTS:
        return False
    if len(base) == 1:
        return True
    if base in KNOWN_MULTI_BASES:
        return True
    if base in KNOWN_FIELD_BASES_WITH_INDEX and len(clean) == 1:
        return True
    return False


def find_variable_matches(text: str) -> list[tuple[int, int, str, str]]:
    matches: list[tuple[int, int, str, str]] = []
    for match in EXPLICIT_INDEX_RE.finditer(text):
        base = match.group("base")
        sub = match.group("sub").strip("{}")
        if should_convert_explicit(base, sub):
            matches.append((match.start(), match.end(), base, sub))

    for pattern, _base, _unused in NAMED_INDEX_PATTERNS:
        for match in pattern.finditer(text):
            matches.append((match.start(), match.end(), match.group(1), match.group(2)))

    matches.sort(key=lambda item: (item[0], -(item[1] - item[0])))
    accepted: list[tuple[int, int, str, str]] = []
    last_end = -1
    for item in matches:
        if item[0] >= last_end:
            accepted.append(item)
            last_end = item[1]
    return accepted


def split_variable_text(text: str) -> list[tuple[str, bool]]:
    text = text.replace("RUL^", "RUL̂")
    matches = find_variable_matches(text)
    if not matches:
        return [(text, False)]
    parts: list[tuple[str, bool]] = []
    position = 0
    for start, end, base, sub in matches:
        if start > position:
            parts.append((text[position:start].replace("->", "→"), False))
        parts.append((base, False))
        parts.append((sub, True))
        position = end
    if position < len(text):
        parts.append((text[position:].replace("->", "→"), False))
    return [(value, sub) for value, sub in parts if value]


def paragraph_is_complex(paragraph: etree._Element) -> bool:
    complex_tags = {
        qn("w", "fldChar"),
        qn("w", "instrText"),
        qn("w", "drawing"),
        qn("w", "pict"),
        qn("w", "object"),
        qn("m", "oMath"),
        qn("m", "oMathPara"),
    }
    return any(node.tag in complex_tags for node in paragraph.iter())


def paragraph_style(paragraph: etree._Element) -> str:
    style = paragraph.find("./w:pPr/w:pStyle", NS)
    return style.get(qn("w", "val")) if style is not None else ""


def paragraph_text(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))


def clone_rpr(template_run: etree._Element | None, subscript: bool) -> etree._Element | None:
    if template_run is not None:
        rpr = template_run.find("./w:rPr", NS)
        clone = deepcopy(rpr) if rpr is not None else etree.Element(qn("w", "rPr"))
    else:
        clone = etree.Element(qn("w", "rPr"))
    if subscript:
        for existing in clone.findall("./w:vertAlign", NS):
            clone.remove(existing)
        vert = etree.SubElement(clone, qn("w", "vertAlign"))
        vert.set(qn("w", "val"), "subscript")
    if len(clone) == 0 and not clone.attrib:
        return None
    return clone


def make_variable_run(template_run: etree._Element | None, text: str, subscript: bool) -> etree._Element:
    run = etree.Element(qn("w", "r"))
    rpr = clone_rpr(template_run, subscript)
    if rpr is not None:
        run.append(rpr)
    t = etree.SubElement(run, qn("w", "t"))
    if text[:1].isspace() or text[-1:].isspace():
        t.set(qn("xml", "space"), "preserve")
    t.text = text
    return run


def format_variable_paragraphs(root: etree._Element) -> dict[str, int]:
    changed_paragraphs = 0
    subscript_runs = 0
    in_bibliography = False
    for paragraph in root.xpath("//w:p", namespaces=NS):
        style = paragraph_style(paragraph).lower()
        if style.startswith("toc"):
            continue
        if paragraph_is_complex(paragraph):
            continue
        text = paragraph_text(paragraph)
        if not text:
            continue
        stripped = text.strip()
        upper = stripped.upper()
        if "СПИСОК ЛИТЕРАТУР" in upper or "БИБЛИОГРАФИЧЕСК" in upper:
            in_bibliography = True
        if in_bibliography:
            continue
        if stripped.startswith("["):
            continue
        if "`" in text or "\\" in text or ".py" in text or ".ttt" in text or ".json" in text or ".csv" in text:
            continue

        parts = split_variable_text(text)
        if len(parts) == 1 and parts[0] == (text, False):
            continue

        first_run = paragraph.find("./w:r", NS)
        ppr = paragraph.find("./w:pPr", NS)
        for child in list(paragraph):
            if child is not ppr:
                paragraph.remove(child)
        for value, is_subscript in parts:
            paragraph.append(make_variable_run(first_run, value, is_subscript))
            if is_subscript:
                subscript_runs += 1
        changed_paragraphs += 1

    return {"variable_paragraphs_changed": changed_paragraphs, "variable_subscripts_added": subscript_runs}


def process_part(xml: bytes, *, formulas: bool) -> tuple[bytes, dict[str, int]]:
    root = etree.fromstring(xml)
    stats = {"formulas_numbered": 0, "math_runs_sized": 0, "variable_paragraphs_changed": 0, "variable_subscripts_added": 0}
    if formulas:
        stats.update(format_formula_paragraphs(root))
    stats.update(format_variable_paragraphs(root))
    new_xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    return new_xml, stats


def convert_docx(docx_path: Path, dry_run: bool) -> dict[str, object]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = docx_path.with_name(f"{docx_path.stem}.backup_before_formula_numbering_{timestamp}{docx_path.suffix}")
    report_dir = Path.cwd() / "reports"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / f"vkr_formula_numbering_variables_{timestamp}.tsv"

    parts_to_process = {
        "word/document.xml": True,
        "word/footnotes.xml": False,
        "word/endnotes.xml": False,
    }
    changed_parts: dict[str, bytes] = {}
    totals = {"formulas_numbered": 0, "math_runs_sized": 0, "variable_paragraphs_changed": 0, "variable_subscripts_added": 0}

    with ZipFile(docx_path, "r") as package:
        names = set(package.namelist())
        for part_name, handle_formulas in parts_to_process.items():
            if part_name not in names:
                continue
            new_xml, stats = process_part(package.read(part_name), formulas=handle_formulas)
            changed_parts[part_name] = new_xml
            for key, value in stats.items():
                totals[key] += value

    with report_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["metric", "value"])
        for key, value in totals.items():
            writer.writerow([key, value])

    if not dry_run:
        shutil.copy2(docx_path, backup_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx", dir=docx_path.parent) as tmp:
            tmp_path = Path(tmp.name)
        try:
            with ZipFile(docx_path, "r") as zin, ZipFile(tmp_path, "w", ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    data = changed_parts.get(item.filename)
                    if data is None:
                        data = zin.read(item.filename)
                    zout.writestr(item, data)
            shutil.move(str(tmp_path), docx_path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    result: dict[str, object] = {
        "docx": str(docx_path),
        "backup": "" if dry_run else str(backup_path),
        "report": str(report_path),
        "dry_run": dry_run,
    }
    result.update(totals)
    return result


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
