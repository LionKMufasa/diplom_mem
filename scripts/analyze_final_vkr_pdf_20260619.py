from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader


def norm_formula(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", "", text)
    text = text.replace("−", "-").replace("–", "-").replace("—", "-")
    text = re.sub(r"\(\d{1,3}\)$", "", text)
    return text


def extract_pdf(pdf_path: Path) -> tuple[list[str], str]:
    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return pages, "\n".join(pages)


def collect_captions(pages: list[str], kind: str) -> list[dict[str, object]]:
    if kind == "table":
        pat = re.compile(r"Таблица\s+([А-ЯA-Z]?\.?\d+)\s*[-–]\s*([^\n]{0,180})")
    else:
        pat = re.compile(r"Рисунок\s+([А-ЯA-Z]?\.?\d+)\s*[-–]\s*([^\n]{0,180})")
    out = []
    for page_no, text in enumerate(pages, start=1):
        for m in pat.finditer(text):
            out.append(
                {
                    "number": m.group(1),
                    "page": page_no,
                    "caption": (m.group(2) or "").strip(),
                    "snippet": text[m.start() : m.start() + 240].replace("\n", " "),
                }
            )
    return out


def collect_formula_labels(pages: list[str]) -> list[dict[str, object]]:
    formulas = []
    for page_no, text in enumerate(pages, start=1):
        lines = [line.strip() for line in text.splitlines()]
        for idx, line in enumerate(lines):
            if not line:
                continue
            label = None
            if re.fullmatch(r"\(\d{1,3}\)", line):
                label = int(line[1:-1])
                body_lines = []
                j = idx - 1
                while j >= 0 and len(body_lines) < 4:
                    prev = lines[j].strip()
                    if prev and not re.fullmatch(r"\d+", prev):
                        if not prev.lower().startswith(("где ", "таблица", "рисунок")):
                            body_lines.append(prev)
                    j -= 1
                body = " | ".join(reversed(body_lines))
            else:
                m = re.search(r"\((\d{1,3})\)\s*$", line)
                if m and len(line) < 220:
                    label = int(m.group(1))
                    body = line[: m.start()].strip()
            if label is None:
                continue
            formulas.append(
                {
                    "number": label,
                    "page": page_no,
                    "line": line,
                    "body": body,
                    "norm": norm_formula(body),
                    "context": "\n".join(lines[max(0, idx - 4) : min(len(lines), idx + 3)]),
                }
            )
    return formulas


def collect_heading_lines(pages: list[str]) -> list[dict[str, object]]:
    pat = re.compile(r"^(?:\d+\.|\d+\.\d+\.|\d+\.\d+\.\d+\.|Введение|Заключение|Список использованных источников|Приложение\s+[А-Я])")
    out = []
    for page_no, text in enumerate(pages, start=1):
        for line in text.splitlines():
            s = line.strip()
            if pat.match(s):
                out.append({"page": page_no, "line": s})
    return out


def collect_ref_numbers(full: str) -> dict[str, object]:
    src = sorted(set(map(int, re.findall(r"\[(\d{1,2})\]", full))))
    table_refs = sorted(set(map(int, re.findall(r"таблиц(?:е|у|ы)?\s+(\d+)", full, re.I))))
    fig_refs = sorted(set(map(int, re.findall(r"рисунк(?:е|а|у|ах)?\s+(\d+)", full, re.I))))
    formula_refs = []
    for m in re.finditer(r"формул(?:е|ам|ы|а)?\s+\((\d+)\)(?:-\((\d+)\))?", full, re.I):
        formula_refs.append((int(m.group(1)), int(m.group(2)) if m.group(2) else None, m.group(0)))
    return {
        "source_refs": src,
        "missing_sources_1_44": [n for n in range(1, 45) if n not in src],
        "table_refs": table_refs,
        "figure_refs": fig_refs,
        "formula_refs": formula_refs,
    }


def find_suspicious_text(full: str) -> dict[str, int]:
    pats = {
        "insert_placeholders": r"Место для вставки|будет встав|будущ",
        "reference_errors": r"Ошибка!\s*Источник|Error!\s*Reference",
        "synthetic_terms": r"синтетическ|модельн",
        "digital_twin_terms": r"цифровой двойник|цифрового двойника|цифровая модель",
        "old_scene_names": r"final_scena|pred_final",
    }
    return {key: len(re.findall(pat, full, re.I)) for key, pat in pats.items()}


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: analyze_final_vkr_pdf_20260619.py <pdf>")
    pdf_path = Path(sys.argv[1])
    pages, full = extract_pdf(pdf_path)
    out_dir = Path("scratch") / "final_vkr_pdf_analysis_20260619"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pdf_text.txt").write_text(full, encoding="utf-8")

    formulas = collect_formula_labels(pages)
    grouped_by_norm = collections.defaultdict(list)
    for f in formulas:
        if len(f["norm"]) >= 4:
            grouped_by_norm[f["norm"]].append(f)
    repeated_formula_bodies = {
        key: value
        for key, value in grouped_by_norm.items()
        if len({v["number"] for v in value}) > 1 and len(value) > 1
    }

    formula_nums = [int(f["number"]) for f in formulas]
    table_caps = collect_captions(pages, "table")
    figure_caps = collect_captions(pages, "figure")
    report = {
        "pdf": str(pdf_path),
        "pages": len(pages),
        "chars": len(full),
        "tables": table_caps,
        "figures": figure_caps,
        "formula_labels": formulas,
        "formula_summary": {
            "count": len(formula_nums),
            "min": min(formula_nums) if formula_nums else None,
            "max": max(formula_nums) if formula_nums else None,
            "missing": [n for n in range(1, max(formula_nums) + 1) if n not in set(formula_nums)] if formula_nums else [],
            "duplicates": sorted([n for n, c in collections.Counter(formula_nums).items() if c > 1]),
        },
        "repeated_formula_bodies": {
            key: [
                {
                    "number": v["number"],
                    "page": v["page"],
                    "body": v["body"],
                    "context": v["context"],
                }
                for v in value
            ]
            for key, value in repeated_formula_bodies.items()
        },
        "refs": collect_ref_numbers(full),
        "suspicious": find_suspicious_text(full),
        "headings": collect_heading_lines(pages),
    }
    (out_dir / "analysis.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    # Human-readable quick report.
    lines = []
    lines.append(f"PDF: {pdf_path}")
    lines.append(f"Pages: {report['pages']}; chars: {report['chars']}")
    lines.append(
        "Tables: "
        + f"{len(table_caps)} captions; first={table_caps[:3]}; last={table_caps[-3:]}"
    )
    lines.append(
        "Figures: "
        + f"{len(figure_caps)} captions; first={figure_caps[:3]}; last={figure_caps[-3:]}"
    )
    lines.append(f"Formula summary: {report['formula_summary']}")
    lines.append(f"Missing sources: {report['refs']['missing_sources_1_44']}")
    lines.append(f"Suspicious text counts: {report['suspicious']}")
    lines.append("Repeated formula bodies:")
    for key, items in sorted(repeated_formula_bodies.items(), key=lambda kv: (len(kv[1]), kv[1][0]["number"]), reverse=True)[:30]:
        nums = [(it["number"], it["page"]) for it in items]
        sample = items[0]["body"][:180]
        lines.append(f"- nums/pages={nums}; body={sample}")
    (out_dir / "quick_report.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"OUT_DIR={out_dir}")


if __name__ == "__main__":
    main()
