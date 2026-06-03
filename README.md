# Case Report Extraction

Codex and Claude Code skill for extracting longitudinal medical case reports from PDF articles into a standard case folder.

The skill is Excel-first: it creates a main `CR<ID>.xlsx` workbook, an evidence-highlighted `CR<ID>.pdf`, linked figure captions, extracted figure images, and optional source tables. Legacy JSON helper scripts are included only for conversion of old datasets.

Main workbooks use the CR10/example visual style: Calibri 16 pt, alternating blue/gray stage cells, yellow figure row, and green table row.

Evidence PDFs use sentence-guided keyword or short-phrase highlights instead of whole-paragraph highlights. Figure crops are recropped conservatively from rendered pages when needed so panel labels, axes, captions, and image edges are not cut off. The skill also includes figure and table audit scripts that flag suspicious crops, blank/over-tight images, empty tables, collapsed rows/columns, merged-cell issues, and non-Calibri table fonts before final packaging.

## Install For Codex

Clone the repository and copy the skill folder into your Codex skills directory:

```bash
git clone https://github.com/Tuner12/case-report-extraction.git
mkdir -p ~/.codex/skills
cp -R case-report-extraction/case-report-extraction ~/.codex/skills/
```

Restart Codex or reload skills after installation.

## Install For Claude Code

Claude Code skills can be installed as personal skills under `~/.claude/skills/` or as project skills under `.claude/skills/`. This repository includes a Claude Code adapter at `adapters/claude-code/skills/case-report-extraction`; it uses the same scripts and schema, with command examples written for `${CLAUDE_SKILL_DIR}`.

Personal install:

```bash
git clone https://github.com/Tuner12/case-report-extraction.git
mkdir -p ~/.claude/skills
cp -R case-report-extraction/adapters/claude-code/skills/case-report-extraction ~/.claude/skills/
```

Project install:

```bash
mkdir -p .claude/skills
cp -R /path/to/case-report-extraction/adapters/claude-code/skills/case-report-extraction .claude/skills/
```

In Claude Code, invoke the skill with:

```text
/case-report-extraction Extract this case report PDF into a complete case folder.
```

See Anthropic's Claude Code skills documentation: https://code.claude.com/docs/en/skills

The bundled scripts expect a Python environment with `openpyxl`, PyMuPDF, Pillow, OpenCV, and optionally `pypdf`:

```bash
python -m pip install openpyxl pymupdf pillow opencv-python pypdf
```

## Use

Ask Codex to use the skill on a PDF:

```text
Use $case-report-extraction to extract this case report PDF into a complete case folder.
```

Final delivery zips include:

- `CR<ID>.xlsx`: longitudinal case workbook
- `CR<ID>.pdf`: evidence-highlighted PDF generated from the uploaded source article
- `CR<ID>_figureN.png`: extracted figure image
- `CR<ID>_figureN.txt`: figure caption
- `CR<ID>_tableN.xlsx`: extracted source table, when the PDF contains tables

During extraction, the working folder may also contain `source_original.pdf`, `source_text/`, rendered `pages/`, `validation_report.json`, `source_alignment_report.json`, `evidence_highlight_report.json`, `figure_recrop_report.json`, `figure_asset_report.json`, `figure_contact_sheet.png`, `table_asset_report.json`, and `table_asset_preview.md`. These are audit/debug artifacts and should not be included in the user-facing final zip unless explicitly requested.

Useful audit commands:

```bash
python case-report-extraction/scripts/audit_figure_assets.py CR10 --report CR10/figure_asset_report.json --contact-sheet CR10/figure_contact_sheet.png
python case-report-extraction/scripts/audit_table_assets.py CR10 --report CR10/table_asset_report.json --preview CR10/table_asset_preview.md
```

## Contribute

Pull requests are welcome. Useful improvements include:

- better table extraction across journal layouts
- more robust figure cropping and panel handling
- additional validation checks for workbook quality
- examples from new case-report formats

Keep the `case-report-extraction/` folder installable as a Codex skill.
