#!/usr/bin/env python3
"""Audit extracted figure images for common crop and asset-quality issues."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat


def figure_number(path: Path) -> int:
    match = re.search(r"_figure(\d+)\.", path.name, flags=re.IGNORECASE)
    return int(match.group(1)) if match else 0


def figure_paths(folder: Path, case_id: str) -> list[Path]:
    paths: list[Path] = []
    for ext in ("png", "jpg", "jpeg"):
        paths.extend(folder.glob(f"{case_id}_figure*.{ext}"))
    return sorted(paths, key=figure_number)


def as_rgb(image: Image.Image) -> Image.Image:
    if image.mode in {"RGBA", "LA"}:
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        return Image.alpha_composite(background, rgba).convert("RGB")
    return image.convert("RGB")


def nonwhite_fraction(gray: Image.Image, threshold: int) -> float:
    width, height = gray.size
    if width == 0 or height == 0:
        return 0.0
    histogram = gray.histogram()
    nonwhite = sum(histogram[:threshold])
    return nonwhite / float(width * height)


def edge_content(gray: Image.Image, margin: int, threshold: int) -> dict[str, float]:
    width, height = gray.size
    margin_x = min(max(1, margin), max(1, width // 2))
    margin_y = min(max(1, margin), max(1, height // 2))
    strips = {
        "left": gray.crop((0, 0, margin_x, height)),
        "right": gray.crop((width - margin_x, 0, width, height)),
        "top": gray.crop((0, 0, width, margin_y)),
        "bottom": gray.crop((0, height - margin_y, width, height)),
    }
    return {side: nonwhite_fraction(strip, threshold) for side, strip in strips.items()}


def audit_image(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    warnings: list[str] = []
    review_notes: list[str] = []
    try:
        with Image.open(path) as raw:
            image = as_rgb(raw)
            gray = ImageOps.grayscale(image)
    except Exception as exc:
        return {
            "figure": path.name,
            "status": "error",
            "warnings": [f"Cannot open image: {exc}"],
        }

    width, height = image.size
    stat = ImageStat.Stat(gray)
    gray_stddev = float(stat.stddev[0])
    content_fraction = nonwhite_fraction(gray, args.content_threshold)
    edges = edge_content(gray, args.edge_margin, args.content_threshold)
    touching_edges = [
        side
        for side, fraction in edges.items()
        if fraction >= args.edge_content_fraction
    ]

    if width < args.min_width or height < args.min_height:
        warnings.append(
            f"Small figure dimensions ({width}x{height}); verify the crop includes the full source figure"
        )
    if gray_stddev < args.blank_stddev or content_fraction < args.min_content_fraction:
        warnings.append(
            "Image appears blank or very low-content; verify the figure was captured from the source page"
        )
    if touching_edges:
        review_notes.append(
            "Content touches the crop edge on "
            + ", ".join(touching_edges)
            + "; inspect visually and recrop with wider page margins if labels, axes, or panels are clipped"
        )

    return {
        "figure": path.name,
        "status": "warning" if warnings else ("review" if review_notes else "ok"),
        "size": [width, height],
        "content_fraction": round(content_fraction, 4),
        "gray_stddev": round(gray_stddev, 3),
        "edge_margin_px": args.edge_margin,
        "edge_content_fraction": {side: round(value, 4) for side, value in edges.items()},
        "warnings": warnings,
        "review_notes": review_notes,
    }


def draw_contact_sheet(folder: Path, items: list[dict[str, Any]], out: Path) -> None:
    if not items:
        return
    cell_w = 360
    cell_h = 300
    thumb_w = 320
    thumb_h = 220
    cols = 2
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for index, item in enumerate(items):
        col = index % cols
        row = index // cols
        x0 = col * cell_w
        y0 = row * cell_h
        figure_path = folder / item["figure"]
        if item.get("warnings"):
            border_color = (180, 30, 30)
        elif item.get("review_notes"):
            border_color = (200, 135, 20)
        else:
            border_color = (40, 130, 65)
        draw.rectangle((x0 + 8, y0 + 8, x0 + cell_w - 8, y0 + cell_h - 8), outline=border_color, width=3)
        try:
            with Image.open(figure_path) as raw:
                thumb = as_rgb(raw)
                thumb.thumbnail((thumb_w, thumb_h))
                tx = x0 + 20 + (thumb_w - thumb.width) // 2
                ty = y0 + 38 + (thumb_h - thumb.height) // 2
                sheet.paste(thumb, (tx, ty))
        except Exception:
            pass
        label = f"{item['figure']}  {item.get('status', '')}"
        draw.text((x0 + 20, y0 + 16), label[:58], fill=(0, 0, 0), font=font)
        warnings = item.get("warnings") or []
        if warnings:
            draw.text((x0 + 20, y0 + 260), warnings[0][:72], fill=(150, 0, 0), font=font)
        elif item.get("review_notes"):
            draw.text((x0 + 20, y0 + 260), item["review_notes"][0][:72], fill=(145, 90, 0), font=font)
        else:
            draw.text((x0 + 20, y0 + 260), "No automated crop warnings", fill=(0, 100, 0), font=font)

    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_folder", type=Path)
    parser.add_argument("--case-id", default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--contact-sheet", type=Path, default=None)
    parser.add_argument("--edge-margin", type=int, default=12)
    parser.add_argument("--edge-content-fraction", type=float, default=0.04)
    parser.add_argument("--content-threshold", type=int, default=248)
    parser.add_argument("--min-content-fraction", type=float, default=0.003)
    parser.add_argument("--blank-stddev", type=float, default=3.0)
    parser.add_argument("--min-width", type=int, default=200)
    parser.add_argument("--min-height", type=int, default=140)
    parser.add_argument("--allow-warnings", action="store_true")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args()

    folder = args.case_folder.expanduser().resolve()
    case_id = args.case_id or folder.name
    figures = figure_paths(folder, case_id)
    report: dict[str, Any] = {
        "case_folder": str(folder),
        "case_id": case_id,
        "figures_found": len(figures),
        "settings": {
            "edge_margin": args.edge_margin,
            "edge_content_fraction": args.edge_content_fraction,
            "content_threshold": args.content_threshold,
            "min_content_fraction": args.min_content_fraction,
            "blank_stddev": args.blank_stddev,
            "min_width": args.min_width,
            "min_height": args.min_height,
        },
        "figures": [],
        "warnings": [],
        "review_notes": [],
    }

    for path in figures:
        item = audit_image(path, args)
        report["figures"].append(item)
        for warning in item.get("warnings", []):
            report["warnings"].append(f"{item['figure']}: {warning}")
        for note in item.get("review_notes", []):
            report["review_notes"].append(f"{item['figure']}: {note}")

    if args.contact_sheet:
        contact_sheet = args.contact_sheet.expanduser().resolve()
        draw_contact_sheet(folder, report["figures"], contact_sheet)
        report["contact_sheet"] = str(contact_sheet)

    if args.report:
        out = args.report.expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    failed = bool(report["warnings"]) or (args.fail_on_review and bool(report["review_notes"]))
    if failed and not args.allow_warnings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
