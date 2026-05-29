from __future__ import annotations

import sys
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "вкр" / "ВКР 2026 Миронов Егор Максимович.docx"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    doc = Document(DOCX)
    keywords = [
        "5.2.",
        "5.4.",
        "5.5.",
        "5.6.",
        "5.7.",
        "5.8.",
        "6.2.",
        "6.3.",
        "6.4.",
        "6.5.",
        "Приложение",
        "long_live_01",
        "vkr_scena.ttt",
        "run_file_pipeline.py",
        "collect_final_scene_telemetry.py",
        "Grafana",
    ]
    for i, paragraph in enumerate(doc.paragraphs):
        text = " ".join(paragraph.text.split())
        if any(key in text for key in keywords):
            print(f"{i}\t{paragraph.style.name}\t{text}")


if __name__ == "__main__":
    main()
