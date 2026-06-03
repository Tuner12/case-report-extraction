# Case Report Extraction Schema

## Folder Contract

Each case folder represents one source article and one case id such as `CR3` or `CR10`.

Use the `CRID` field in the workbook as the authoritative case id. Some legacy examples have mismatched filename prefixes; preserve existing resource filenames during normalization unless the user asks to repair filenames.

Required for the final delivery package:

| File | Purpose |
| --- | --- |
| `CR<ID>.xlsx` | Main wide workbook with longitudinal stages |
| source `.pdf` | Original uploaded article, copied verbatim so embedded highlights/annotations are preserved |
| `CR<ID>_figureN.png` | Extracted figure image or carefully cropped page render |
| `CR<ID>_figureN.txt` | Caption for figure N |
| `CR<ID>_tableN.xlsx` | Extracted table workbook |

Working-only extraction artifacts:

| File/folder | Purpose |
| --- | --- |
| `source_text/pages.json` | Page-by-page text from the PDF |
| `source_text/full_text.txt` | Full extracted text |
| `pages/page-NNN.png` | Rendered pages for visual figure/table cropping |
| `source_text/annotations.json` | PDF annotation metadata from the source file |
| `validation_report.json` | Validator output |
| `source_alignment_report.json` | Heuristic source-support audit |

Keep working-only artifacts in the local working folder when useful, but exclude them from user-facing final zips. A final zip should mirror the example packages: workbook, original PDF, figure PNG/TXT assets, and table workbooks only. Do not include `pages/`, `source_text/`, validation reports, source-alignment reports, or logs unless the user explicitly asks for an audit/debug package.

If source text and stored extraction disagree, the source PDF wins. A file prefix match is not enough to prove that records, recommendations, figures, or tables belong to the same case.

## Workbook Contract

The main workbook uses a single sheet.

Row 1 example:

```text
CRID | Record 1 | Question 1 | Answer 1 | Record 2 | Question 2 | Answer 2 | ... | Final follow up
```

Row 2 contains the values.

Row 3 contains figure references:

```text
figures | CR5_figure1.png, CR5_figure2.png | ... 
```

Place each figure list in the `Record N` column of the consultation it supports.

Compatibility: human workbooks may write a figure reference as `CR6_figure1.png (CR6_figure1.txt)` to show the caption file alongside the image. Accept this format and validate both files when present.

Row 4 contains table references:

```text
tables | ... | CR5_table1.xlsx | ...
```

Place each table list in the `Record N` column of the consultation it supports.

Compatibility:

- Existing example workbooks include `Anwser 4`; accept it. The exporter reproduces this typo by default to match legacy files.
- Older CR3 workbooks use `Patient record N` / `Clinician recommendation N`; normalize each pair to a consultation with a default question such as `What is the clinician recommendation at this point?`.

## Extraction Heuristics

Use the source article's chronology. For each stage:

1. Add information that is available before the next decision.
2. Stop the record before the clinician action if the action belongs in `Answer1`.
3. If the article presents the action before the data because of narrative style, reorder into patient-centered chronology only when the source clearly supports it.
4. Preserve exact dates, relative times, drug doses, test names, lesion sizes, staging, mutations, adverse effects, response, and outcome.
5. Avoid literature review content unless it explains the clinician's decision in this patient.

## Figure and Table Handling

- Use source figure captions verbatim when possible, but do not quote large unrelated text.
- Use the figure/table only when it materially supports the patient record.
- For multi-panel figures, keep the source figure as one PNG unless the user asks for panels.
- For table extraction, create a separate `.xlsx` with a simple header row and source rows. Do not embed the table in the main workbook.
- Link the resource from the stage where it first becomes clinically relevant.
- Include diagnostic pathology figures when they support the diagnosis or staging.
- Do not import a table from an example folder unless the same table appears in the source PDF.

## Source Alignment

Run `scripts/audit_source_alignment.py` whenever a PDF source is available:

```bash
python scripts/audit_source_alignment.py CR5/CR5.xlsx --source-text CR5/source_text/full_text.txt --write-report CR5/source_alignment_report.json
```

The audit is heuristic. It is designed to catch obvious cross-case contamination or unsupported details, not to prove clinical correctness. Low coverage with zero phrase hits is a red flag that the workbook field may not come from the PDF.

For short case reports with heavy paraphrasing, manually inspect warnings. Keep the extraction only if the unsupported terms are explainable from the source article.

## Legacy JSON

Ignore JSON files in example folders unless the user explicitly asks for JSON conversion. The historical JSON schema used `ConsulationN` blocks, but new PDF extractions should not create JSON by default.
