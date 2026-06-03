# Case-Specific Extraction Lessons

Use these lessons only when the source PDF, case id, or benchmark package resembles one of these known cases. They are not general schema requirements.

## CR5

The CR5 PDF `Unusual Morphological Presentation of Cutaneous Malignant Melanoma` should be learned from the PDF and figure/table assets, not from accidental JSON files in the example package.

- Use Figure 1 for the initial lesion morphology and Figure 2 for rapid nodular progression.
- Consider Figure 3 as diagnostic pathology support when staging or diagnosis is discussed.
- Do not add lab tables unless the PDF actually contains those laboratory values.
- Keep the extraction short if the PDF only supports presentation, diagnostic workup, oncology referral or chemotherapy, and death during chemotherapy.

## CR1

The CR1 NEJM Case Record `A 57-Year-Old Woman with Melanoma and Fever` is a benchmark for cases with repeated treatment interruption and multiple laboratory snapshots.

- Keep the longitudinal split around adjuvant dabrafenib/trametinib initiation, repeated pyrexia episodes, emergency evaluation, hospital course, liver biopsy, final drug-induced liver injury diagnosis, and future melanoma management.
- Do not merge the emergency-department workup, initial admission management, and later hospital-day diagnostic reasoning into one stage. A manual-like seven-stage split is:
  1. Initial scalp lesion, biopsy, wide excision, lymph-node dissection, stage IIIC melanoma, and BRAF V600E mutation.
  2. Oncology visit for dabrafenib/trametinib initiation, baseline laboratory table, and fever/nausea after the first dose.
  3. First treatment interruption/rechallenge followed by recurrent fever with normal liver, kidney, and blood-count testing.
  4. Second interruption/rechallenge followed by the third persistent fever episode, symptoms, exposure/social history, and referral to the emergency department; the answer should request physical examination, laboratory/microbiology testing, and imaging.
  5. Emergency-department vital signs, examination, laboratory abnormalities, negative respiratory viral testing, and ultrasound/CT findings; the answer should be fluids, broad-spectrum antibiotics, cultures, and admission.
  6. Hospital-day course, worsening liver tests, liver biopsy, pathology, and negative infectious studies; the answer should identify BRAF-MEK inhibitor-related drug-induced liver injury.
  7. Severe complicated pyrexia syndrome, future melanoma options, decision to avoid further targeted therapy, abdominal-pain endoscopy, and next treatment plan.
- Preserve multiple laboratory tables as separate source table workbooks when they represent different clinical timepoints, for example baseline labs, emergency-department/severe fever workup, and later hospital-day labs.
- Include Figure 1 for imaging studies and Figure 2 for liver-biopsy pathology when they support the workup and final diagnosis.
- If the manual reference workbook is versioned, normalize the final workbook filename to `CR1.xlsx` while preserving the manual file only as a benchmark input.

## CR6

The CR6 Cureus case `A Patient's Journey With Modern Melanoma Therapy` is a benchmark for short melanoma therapy timelines where diagnostic orders and results are easy to collapse.

- Split the initial mole presentation before biopsy from the biopsy-proven melanoma record. Stage 1 should ask for skin examination and punch biopsy; Stage 2 should contain the superficial spreading melanoma pathology and ask for wide excision plus sentinel lymph-node mapping/resection.
- Split final node-negative pathology from the prior surgical answer. The next decision is staging and whether adjuvant therapy is indicated; for the historical 2020 context, observation/no adjuvant systemic therapy is appropriate for stage IIB node-negative disease.
- Split locoregional relapse symptoms from relapse workup results. New right-groin masses/subcutaneous nodules should lead to lymph-node biopsy, PET staging, and BRAF testing; confirmed metastatic melanoma, BRAF V600E status, and PET findings belong in the following record before systemic therapy selection.
- Split immune-checkpoint toxicity from next-line targeted therapy. Toxicity after nivolumab/ipilimumab should lead to stopping immunotherapy and prednisone; after toxicity resolution and known BRAF mutation, dabrafenib plus trametinib becomes the next systemic therapy.
- Keep later dabrafenib/trametinib side effects, axillary granulomatous adenopathy, and durable remission as final follow-up unless the user wants a longer surveillance-stage extraction.
