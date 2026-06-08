#!/usr/bin/env python3
"""Prepare a case-report PDF for extraction."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - fallback depends on local Poppler install.
    PdfReader = None


def normalize_case_id(value: str | None, pdf: Path) -> str:
    if value:
        return value
    stem = pdf.stem
    for part in stem.replace("-", "_").split("_"):
        if part.upper().startswith("CR") and part[2:].isdigit():
            return part.upper()
    return stem.split()[0].replace(" ", "_")


def render_pages(pdf: Path, pages_dir: Path, dpi: int) -> bool:
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        return False
    pages_dir.mkdir(parents=True, exist_ok=True)
    prefix = pages_dir / "page"
    cmd = [pdftoppm, "-r", str(dpi), "-png", str(pdf), str(prefix)]
    subprocess.run(cmd, check=True)
    for old in pages_dir.glob("page-*.png"):
        number = old.stem.split("-")[-1]
        new = pages_dir / f"page-{int(number):03d}.png"
        if old != new:
            old.rename(new)
    return True


def extract_with_pypdf(pdf: Path) -> list[dict]:
    if PdfReader is None:
        raise RuntimeError("pypdf is not available")
    reader = PdfReader(str(pdf))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        pages.append({"page": index, "text": page.extract_text() or ""})
    return pages


def poppler_page_count(pdf: Path) -> int:
    pdfinfo = shutil.which("pdfinfo")
    if not pdfinfo:
        raise RuntimeError("Neither pypdf nor pdfinfo is available")
    result = subprocess.run([pdfinfo, str(pdf)], check=True, text=True, capture_output=True)
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError("Could not determine PDF page count")


def extract_with_pdftotext(pdf: Path) -> list[dict]:
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        raise RuntimeError("Neither pypdf nor pdftotext is available")
    pages = []
    for index in range(1, poppler_page_count(pdf) + 1):
        result = subprocess.run(
            [pdftotext, "-layout", "-f", str(index), "-l", str(index), str(pdf), "-"],
            check=True,
            text=True,
            capture_output=True,
        )
        pages.append({"page": index, "text": result.stdout})
    return pages


def extract_pages(pdf: Path) -> list[dict]:
    if PdfReader is not None:
        return extract_with_pypdf(pdf)
    return extract_with_pdftotext(pdf)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--out", type=Path, required=True, help="Case output folder")
    parser.add_argument("--case-id", default=None)
    parser.add_argument("--render-pages", action="store_true")
    parser.add_argument("--dpi", type=int, default=180)
    args = parser.parse_args()

    pdf = args.pdf.expanduser().resolve()
    out = args.out.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    source_text = out / "source_text"
    source_text.mkdir(parents=True, exist_ok=True)

    case_id = normalize_case_id(args.case_id, pdf)
    pages = extract_pages(pdf)
    full_text_parts = []
    for item in pages:
        full_text_parts.append(f"\n\n--- Page {item['page']} ---\n{item['text']}")

    metadata = {
        "case_id": case_id,
        "source_pdf": str(pdf),
        "pages": len(pages),
        "rendered_pages": False,
    }

    (source_text / "pages.json").write_text(
        json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (source_text / "full_text.txt").write_text("".join(full_text_parts).strip(), encoding="utf-8")
    metadata["input_annotations"] = "ignored"
    metadata["annotation_extraction"] = "disabled"

    if args.render_pages:
        metadata["rendered_pages"] = render_pages(pdf, out / "pages", args.dpi)
        metadata["render_dpi"] = args.dpi

    (source_text / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
