# Case Report Extraction

Codex skill for extracting longitudinal medical case reports from PDF articles into a standard case folder.

The skill is Excel-first: it creates a main `CR<ID>.xlsx` workbook, linked figure captions, extracted figure images, and optional source tables. Legacy JSON helper scripts are included only for conversion of old datasets.

## Install

Clone the repository and copy the skill folder into your Codex skills directory:

```bash
git clone https://github.com/Tuner12/case-report-extraction.git
mkdir -p ~/.codex/skills
cp -R case-report-extraction/case-report-extraction ~/.codex/skills/
```

Restart Codex or reload skills after installation.

## Use

Ask Codex to use the skill on a PDF:

```text
Use $case-report-extraction to extract this case report PDF into a complete case folder.
```

Final delivery zips include:

- `CR<ID>.xlsx`: longitudinal case workbook
- source `.pdf`: original uploaded PDF, preserved verbatim
- `CR<ID>_figureN.png`: extracted figure image
- `CR<ID>_figureN.txt`: figure caption
- `CR<ID>_tableN.xlsx`: extracted source table, when the PDF contains tables

During extraction, the working folder may also contain `source_text/`, rendered `pages/`, `validation_report.json`, and `source_alignment_report.json`. These are audit/debug artifacts and should not be included in the user-facing final zip unless explicitly requested.

## Contribute

Pull requests are welcome. Useful improvements include:

- better table extraction across journal layouts
- more robust figure cropping and panel handling
- additional validation checks for workbook quality
- examples from new case-report formats

Keep the `case-report-extraction/` folder installable as a Codex skill.
