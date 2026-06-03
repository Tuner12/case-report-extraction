#!/usr/bin/env python3
"""Recrop existing figure images from rendered PDF pages with safer padding."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    import cv2
except Exception as exc:  # pragma: no cover - depends on local image stack.
    raise SystemExit("OpenCV (`cv2`) is required for template-based figure recropping") from exc

from PIL import Image


def figure_number(path: Path) -> int:
    match = re.search(r"_figure(\d+)\.", path.name, flags=re.IGNORECASE)
    return int(match.group(1)) if match else 0


def find_best_match(figure: Path, pages: list[Path], match_scale: float) -> dict | None:
    template0 = cv2.imread(str(figure), cv2.IMREAD_GRAYSCALE)
    if template0 is None:
        return None
    template_h, template_w = template0.shape[:2]
    scaled_w = max(16, int(template_w * match_scale))
    scaled_h = max(16, int(template_h * match_scale))
    template = cv2.resize(template0, (scaled_w, scaled_h), interpolation=cv2.INTER_AREA)

    best = None
    for page in pages:
        page0 = cv2.imread(str(page), cv2.IMREAD_GRAYSCALE)
        if page0 is None:
            continue
        page_h, page_w = page0.shape[:2]
        if template_h > page_h or template_w > page_w:
            continue
        page_scaled = cv2.resize(
            page0,
            (max(16, int(page_w * match_scale)), max(16, int(page_h * match_scale))),
            interpolation=cv2.INTER_AREA,
        )
        if template.shape[0] > page_scaled.shape[0] or template.shape[1] > page_scaled.shape[1]:
            continue
        result = cv2.matchTemplate(page_scaled, template, cv2.TM_CCOEFF_NORMED)
        _, score, _, loc = cv2.minMaxLoc(result)
        if best is None or score > best["score"]:
            x_scaled, y_scaled = loc
            best = {
                "score": float(score),
                "page": page,
                "x": int(round(x_scaled / match_scale)),
                "y": int(round(y_scaled / match_scale)),
                "width": template_w,
                "height": template_h,
            }
    return best


def expanded_box(match: dict, page_size: tuple[int, int], pads: dict[str, int]) -> tuple[int, int, int, int]:
    page_w, page_h = page_size
    x0 = max(0, match["x"] - pads["left"])
    y0 = max(0, match["y"] - pads["top"])
    x1 = min(page_w, match["x"] + match["width"] + pads["right"])
    y1 = min(page_h, match["y"] + match["height"] + pads["bottom"])
    return x0, y0, x1, y1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_folder", type=Path)
    parser.add_argument("--case-id", default=None)
    parser.add_argument("--pages-dir", type=Path, default=None)
    parser.add_argument("--match-scale", type=float, default=0.25)
    parser.add_argument("--min-score", type=float, default=0.82)
    parser.add_argument("--left-padding", type=int, default=40)
    parser.add_argument("--right-padding", type=int, default=24)
    parser.add_argument("--top-padding", type=int, default=18)
    parser.add_argument("--bottom-padding", type=int, default=18)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    folder = args.case_folder.expanduser().resolve()
    case_id = args.case_id or folder.name
    pages_dir = (args.pages_dir or folder / "pages").expanduser().resolve()
    pages = sorted(pages_dir.glob("page-*.png"))
    if not pages:
        raise SystemExit(f"No rendered page PNGs found in {pages_dir}")

    figures = sorted(folder.glob(f"{case_id}_figure*.png"), key=figure_number)
    pads = {
        "left": args.left_padding,
        "right": args.right_padding,
        "top": args.top_padding,
        "bottom": args.bottom_padding,
    }
    report = {
        "case_folder": str(folder),
        "pages_dir": str(pages_dir),
        "case_id": case_id,
        "padding": pads,
        "match_scale": args.match_scale,
        "min_score": args.min_score,
        "figures": [],
        "warnings": [],
    }

    for figure in figures:
        match = find_best_match(figure, pages, args.match_scale)
        item = {"figure": figure.name}
        if not match:
            item["status"] = "no_match"
            report["warnings"].append(f"No page match found for {figure.name}")
            report["figures"].append(item)
            continue
        item.update(
            {
                "status": "matched",
                "score": round(match["score"], 4),
                "page": match["page"].name,
                "original_box": [match["x"], match["y"], match["x"] + match["width"], match["y"] + match["height"]],
            }
        )
        if match["score"] < args.min_score:
            item["status"] = "low_score"
            report["warnings"].append(f"Low template match score for {figure.name}: {match['score']:.3f}")
            report["figures"].append(item)
            continue

        page_image = Image.open(match["page"]).convert("RGB")
        box = expanded_box(match, page_image.size, pads)
        item["expanded_box"] = list(box)
        item["old_size"] = list(Image.open(figure).size)
        item["new_size"] = [box[2] - box[0], box[3] - box[1]]
        if not args.dry_run:
            page_image.crop(box).save(figure)
        report["figures"].append(item)

    if args.report:
        out = args.report.expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["warnings"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
