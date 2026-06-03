#!/usr/bin/env python3
"""Create a clean user-facing zip from a case-report working folder."""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path


WORKING_ONLY_NAMES = {
    "pages",
    "source_text",
    "validation_report.json",
    "source_alignment_report.json",
}


def is_table_workbook(path: Path) -> bool:
    return re.search(r"_table\d+\.xlsx$", path.name, flags=re.IGNORECASE) is not None


def is_deliverable(path: Path, case_id: str) -> bool:
    if path.name in WORKING_ONLY_NAMES:
        return False
    if path.is_dir():
        return False
    suffix = path.suffix.lower()
    name = path.name
    if suffix == ".pdf":
        return True
    if suffix == ".xlsx":
        return name == f"{case_id}.xlsx" or is_table_workbook(path)
    if re.fullmatch(rf"{re.escape(case_id)}_figure\d+\.(png|jpg|jpeg|txt)", name, flags=re.IGNORECASE):
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_folder", type=Path)
    parser.add_argument("--out", type=Path, help="Output zip path. Defaults to <case_folder>.zip")
    args = parser.parse_args()

    folder = args.case_folder.expanduser().resolve()
    if not folder.exists() or not folder.is_dir():
        raise SystemExit(f"Case folder does not exist or is not a directory: {folder}")
    case_id = folder.name
    out = (args.out or folder.with_suffix(".zip")).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    deliverables = [p for p in sorted(folder.iterdir()) if is_deliverable(p, case_id)]
    if not any(p.name == f"{case_id}.xlsx" for p in deliverables):
        raise SystemExit(f"Missing main workbook: {case_id}.xlsx")
    if not any(p.suffix.lower() == ".pdf" for p in deliverables):
        raise SystemExit("Missing source PDF")

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{case_id}/", "")
        for path in deliverables:
            zf.write(path, f"{case_id}/{path.name}")

    print(out)


if __name__ == "__main__":
    main()
