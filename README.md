# Case Report Extraction Skill

Codex skill for extracting longitudinal medical case reports from PDF articles into a standard case folder.

The skill is Excel-first: it creates a main `CR<ID>.xlsx` workbook, linked figure captions, extracted figure images, and optional source tables. Legacy JSON helper scripts are included only for conversion of old datasets.

## Install

Clone the repository and copy the skill folder into your Codex skills directory:

```bash
git clone https://github.com/Tuner12/case-report-extraction-skill.git
mkdir -p ~/.codex/skills
cp -R case-report-extraction-skill/case-report-extraction ~/.codex/skills/
```

Restart Codex or reload skills after installation.

## Use

Ask Codex to use the skill on a PDF:

```text
Use $case-report-extraction to extract this case report PDF into a complete case folder.
```

Expected outputs include:

- `CR<ID>.xlsx`: longitudinal case workbook
- `CR<ID>_figureN.png`: extracted figure image
- `CR<ID>_figureN.txt`: figure caption
- `CR<ID>_tableN.xlsx`: extracted source table, when the PDF contains tables
- `source_text/`: extracted PDF text and metadata
- `source_alignment_report.json`: heuristic source-support audit

## Contribute

Pull requests are welcome. Useful improvements include:

- better table extraction across journal layouts
- more robust figure cropping and panel handling
- additional validation checks for workbook quality
- examples from new case-report formats

Keep the `case-report-extraction/` folder installable as a Codex skill.
