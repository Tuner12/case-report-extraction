---
name: case-report-extraction
description: Extract longitudinal medical case reports from uploaded PDF articles into a standard case folder. Use when Codex or Claude Code needs to process case report PDFs, NEJM Case Records, oncology case reports, clinicopathological cases, or existing CR*.xlsx examples into patient-record/recommendation stages with figures, tables, and workbook deliverables.
---

# Case Report Extraction

## Purpose

Build one complete folder per case report from a PDF. The folder must preserve the source article, extract the patient timeline into decision stages, attach relevant figures/tables, and emit a main workbook that downstream case-report tooling can consume.

Use the bundled scripts for mechanical work. Use clinical reasoning for the semantic split into patient records, questions, and recommendations.

When running scripts in Codex, use the workspace dependency Python returned by `load_workspace_dependencies` when available. System Python may miss `pypdf` or `openpyxl`; without `pypdf`, `prepare_pdf.py` can still extract text through Poppler but cannot export annotation metadata.

## Working Folder

Create a working folder named after the case id, for example `CR10/`. During extraction, this folder may contain both final deliverables and temporary audit material.

Final deliverables:

- `CR<ID>.xlsx`: main longitudinal workbook.
- `CR<ID>.pdf`: evidence-highlighted PDF generated from the uploaded article. Use source sentences to locate evidence, but highlight only the corresponding keywords or short phrases that support extracted `Record`, `Answer`, and final follow-up fields. Do not highlight whole paragraphs or deliver an unmarked raw source PDF as the final package PDF.
- `CR<ID>_figureN.png`: cropped or page-rendered figure assets.
- `CR<ID>_figureN.txt`: figure caption text when available.
- `CR<ID>_tableN.xlsx`: one workbook per extracted source table.

Working-only artifacts:

- `source_text/`: page text and metadata from `scripts/prepare_pdf.py`.
- `source_text/annotations.json`: PDF highlight/stamp metadata when annotations exist.
- `source_original.pdf`: optional verbatim copy of the uploaded PDF used as the base for evidence highlighting.
- `pages/`: rendered page PNGs when figure/table cropping needs visual inspection.
- `validation_report.json`: final structural checks from `scripts/validate_case_folder.py`.
- `source_alignment_report.json`: source-support audit when a source PDF is available.
- `evidence_highlight_report.json`: selected source sentences, keyword matches, and supporting PDF text blocks used to create the evidence-highlighted PDF.
- `figure_recrop_report.json`: template-match report from conservative figure recropping.

## Final Delivery Zip

The zip file shared with the user or committed as the final case package must contain only the case folder and final deliverables:

- `CR<ID>.xlsx`
- `CR<ID>.pdf` evidence-highlighted PDF
- `CR<ID>_figureN.png`
- `CR<ID>_figureN.txt`
- `CR<ID>_tableN.xlsx`

Do not include `source_original.pdf`, `pages/`, `source_text/`, `validation_report.json`, `source_alignment_report.json`, `evidence_highlight_report.json`, `figure_recrop_report.json`, or other extraction logs in the final delivery zip unless the user explicitly asks for an audit/debug bundle.

Read `references/schema.md` before extracting a new PDF or normalizing an existing case.

## Workflow

1. Create the case folder and keep the uploaded PDF as the source input. If a local working copy is needed, name it `source_original.pdf` so it does not become a final deliverable.
2. Run `scripts/prepare_pdf.py` on the PDF to create `source_text/pages.json`, `source_text/full_text.txt`, `source_text/annotations.json`, and optionally page images.
3. Read the article text and identify the true case narrative, excluding abstract, discussion-only literature review, references, funding, and unrelated author text.
4. Split the case into longitudinal clinical decision stages. Each stage should contain:
   - `Record N`: patient state and newly available data at that point.
   - `Question N`: the clinical decision question.
   - `Answer N`: the clinician action, recommendation, treatment, diagnostic test, or management decision that follows.
   - figure/table references in workbook rows 3 and 4.
5. Extract figures and tables that are useful for the case state. Use original captions. Figure crops must be conservative: include complete left/right/top/bottom edges, panel labels, axes/scale bars, visible figure labels, and caption text when the example package style includes captions. Do not make tight crops; use `scripts/recrop_figures_with_padding.py` or manual recropping from rendered pages if any edge is close to being cut off.
6. Write `CR<ID>.xlsx` directly in the standard workbook format. Do not create JSON unless the user explicitly asks for it or an old JSON file must be normalized.
7. Apply the canonical workbook style with `scripts/style_case_workbook.py` so the workbook matches the CR10/example package style.
8. Run `scripts/audit_source_alignment.py` against the workbook and source text. Treat failures as a hard stop: records or answers may be from another case, over-paraphrased, or invented.
9. Run `scripts/highlight_evidence_pdf.py` to create `CR<ID>.pdf` from the source PDF and workbook evidence. It should use sentence-level evidence selection but keyword/short-phrase highlight annotations, not paragraph-wide highlights. Inspect `evidence_highlight_report.json` and the rendered PDF if matches are weak or visually too broad.
10. Run `scripts/validate_case_folder.py` and fix missing links, empty stages, missing highlights, or schema mistakes.
11. Package a clean delivery zip with `scripts/package_case_folder.py`. The working folder may keep the original source copy, `pages/`, `source_text/`, and reports for review, but the delivery zip must exclude them.

If the PDF contains annotations or highlights, inspect `source_text/annotations.json` and rendered pages. Use highlights as extraction cues only; do not assume color meanings across PDFs and do not let annotations override source text.

## Stage-Splitting Rules

Use a new stage when the article reveals information that would change a clinician's next decision:

- first presentation and initial empiric therapy;
- persistence/progression after initial therapy;
- pathology, biopsy, molecular testing, staging imaging, or lab results;
- treatment selection, surgery, systemic therapy, radiation, adverse effects, relapse, or surveillance;
- final follow-up or anatomical diagnosis.

Do not split merely because a paragraph changes topic. Merge adjacent sentences when they represent one clinical state before the next management decision.

For NEJM-style Case Records, treat `Presentation of Case`, diagnostic testing, `Discussion of Management`, pathology, treatment course, and final follow-up as source sections, but still output a patient-centered longitudinal sequence.

For short case-report articles, use fewer stages when appropriate. If the article contains only presentation, diagnostic workup, referral/treatment, and outcome, do not fabricate extra stages.

## Workbook Format

The main workbook uses one sheet and a wide layout:

- Row 1: headers.
- Row 2: case values.
- Row 3: figure references, with `figures` in column A.
- Row 4: table references, with `tables` in column A.

Use these headers for the standard format:

`CRID`, then repeating `Record N`, `Question N`, `Answer N`, followed by `Final follow up` or `Final output` when needed.

Workbook style must match the CR10/example packages:

- Main workbook font: Calibri 16 pt, black text. Do not leave cells in the default Chinese fallback font such as Songti.
- Row 1: bold headers, no fill.
- Row 2: thin borders and wrapped text; stage triples alternate `#DEEBF7` blue and `#F2F2F2` light gray, starting with blue for Record/Question/Answer 1.
- Row 3: figures row, `#FFF2CC` fill.
- Row 4: tables row, `#E2F0D9` fill.
- Use `scripts/style_case_workbook.py CR<ID>/CR<ID>.xlsx` after writing the workbook.
- For extracted table workbooks, use explicit Calibri font and avoid colored header fills unless reproducing a source table requires them.

Compatibility notes:

- Existing examples may use `Anwser 4`; scripts accept it and can reproduce it.
- Ignore example JSON files unless the user explicitly asks to inspect or convert them.
- Human benchmark packages may use versioned workbook names such as `CR1_v1.0_GWan_Ruiz_NHao.xlsx`. Use these files as references when comparing or normalizing manual extractions, but final generated packages must still emit the main workbook as `CR<ID>.xlsx`.
- Older CR3-style files may use `Patient record N` and `Clinician recommendation N`; normalize these into the standard stage schema.
- If filenames and the workbook `CRID` disagree, treat `CRID` as authoritative and preserve existing resource filenames unless the user asks to rename.
- If source PDF content and workbook content disagree, treat the source PDF as authoritative. Existing example packages can contain cross-case contamination; repair the workbook instead of carrying the mismatch forward.

## Script Usage

Prepare PDF text and page renders:

```bash
python scripts/prepare_pdf.py input.pdf --out CR10 --case-id CR10 --render-pages
```

Style the workbook:

```bash
python scripts/style_case_workbook.py CR10/CR10.xlsx
python scripts/style_case_workbook.py CR10/CR10_table1.xlsx --kind table
```

Audit workbook against source PDF text:

```bash
python scripts/audit_source_alignment.py CR10/CR10.xlsx --source-text CR10/source_text/full_text.txt --write-report CR10/source_alignment_report.json
```

Create the evidence-highlighted PDF:

```bash
python scripts/highlight_evidence_pdf.py CR10/CR10.xlsx source_original.pdf --out CR10/CR10.pdf --report CR10/evidence_highlight_report.json
```

Recrop existing figure assets from rendered pages with safer margins:

```bash
python scripts/recrop_figures_with_padding.py CR10 --report CR10/figure_recrop_report.json
```

Validate the case folder:

```bash
python scripts/validate_case_folder.py CR10 --workbook CR10/CR10.xlsx
```

Package the final user-facing zip:

```bash
python scripts/package_case_folder.py CR10 --out CR10.zip
```

Legacy JSON helpers exist only for conversion work:

```bash
python scripts/case_json_to_workbook.py old_case.json --out CR10/CR10.xlsx
python scripts/workbook_to_case_json.py CR10/CR10.xlsx --out legacy_case.json
```

## Quality Bar

Before finalizing:

- Every non-final stage has a non-empty patient record and management answer.
- Questions are decision-oriented, not generic summaries.
- Records use article facts and preserve clinically important dates, measurements, diagnoses, drugs, procedures, mutations, response, toxicity, and outcomes.
- Figures/tables listed in the workbook exist in the case folder.
- Table workbooks contain source table values with headers.
- Figure captions are saved in `.txt` files when available.
- Source-alignment audit has no failed fields, or every warning is manually explained.
- `CR<ID>.pdf` is an evidence-highlighted PDF with keyword/short-phrase highlight annotations guided by source sentences supporting the extracted records, answers, and final follow-up. Whole-paragraph highlights are not acceptable.
- Figure PNGs include all source-image edges and labels. If a crop touches content at the left/right/top/bottom boundary, recrop with padding before final packaging.
- Final delivery zips contain only workbook, evidence-highlighted PDF, figure PNG/TXT files, and table workbooks. Keep the original source PDF, source text, rendered pages, and validation reports outside the delivery zip.
- The final report states any figure/table extraction limitations.

Do not invent facts, dates, staging, mutation status, treatment names, or outcomes. If the PDF omits timing, say that the exact date is not stated.

## CR5 Lesson

The CR5 PDF `Unusual Morphological Presentation of Cutaneous Malignant Melanoma` should be learned from the PDF and figure/table assets, not from accidental JSON files in the example package. For this PDF:

- use Figure 1 for the initial lesion morphology and Figure 2 for rapid nodular progression;
- consider Figure 3 as diagnostic pathology support when staging/diagnosis is discussed;
- do not add lab tables unless the PDF actually contains those laboratory values;
- keep the extraction short if the PDF only supports presentation, diagnostic workup, oncology referral/chemotherapy, and death during chemotherapy.

## CR1 Lesson

The CR1 NEJM Case Record `A 57-Year-Old Woman with Melanoma and Fever` is a benchmark for cases with repeated treatment interruption and multiple laboratory snapshots:

- keep the longitudinal split around adjuvant dabrafenib/trametinib initiation, repeated pyrexia episodes, emergency evaluation, hospital course, liver biopsy, final drug-induced liver injury diagnosis, and future melanoma management;
- preserve multiple laboratory tables as separate source table workbooks when they represent different clinical timepoints, for example baseline labs, emergency-department/severe fever workup, and later hospital-day labs;
- include Figure 1 for imaging studies and Figure 2 for liver-biopsy pathology when they support the workup and final diagnosis;
- if the manual reference workbook is versioned, normalize the final workbook filename to `CR1.xlsx` while preserving the manual file only as a benchmark input.
