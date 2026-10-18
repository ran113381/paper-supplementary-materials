# Correction note (2026-10-18)

This note records corrections to the adjudication record of the 600-passage gold standard
and to statements made about it in earlier versions of this repository and in the response to
the first round of review.

## 1. Withdrawn attribution column

When the first-round revision was prepared, a column `author_confirmation` was added to sheet
`Disagreement_Review` of `data/genai_gold_standard_adjudication_workbook.xlsx` (122 rows). Its
text attributed the adjudication drafts to a named model and stated that the final labels had
been confirmed and approved by the authors. No contemporaneous record supports that attribution.
The column was withdrawn on 2026-10-18.

The adjudication workbook records the draft decisions only as "AI-assisted"; no contemporaneous
record names the tool, and none is supplied here.

## 2. Original workbook kept; corrected copy added

The original workbook is kept unchanged, byte for byte
(SHA-256 `aa072750c0a1ae9ac68dece24f060ef2c8e1d1bfb7a153244f9d69791620b0a0`), because this hash is
fixed in the deposited third-coder protocol (`third_coder/protocol_third_coder_v2.7.md`, Section 4.1)
and in `third_coder/selection_manifest.json`, and the deposited selection script checks it.

The corrected copy is `data/genai_gold_standard_adjudication_workbook_corrected.xlsx`
(SHA-256 `d9da03a4b63dc9865489ba48bcd995ab384e1def28006af6ec4ba780c26739dd`). It differs from the
original only as follows:

- each of the 122 cells of `Disagreement_Review!author_confirmation` (P2:P123) reads
  "withdrawn 2026-10-18 – see CORRECTION_NOTE.md";
- the document properties `creator` and `lastModifiedBy` are empty, and the custom-properties
  part (office-suite build identifiers) is removed.

Every other cell of every sheet is identical to the original; this was checked cell by cell.

## 3. Earlier statements withdrawn

In the previous version of the manuscript and in the response to the first round of review, it
was stated that the coders' disagreements had been resolved under a protocol described as fixed
in advance, from AI-assisted drafts that the authors had confirmed one by one, with a dated
author-confirmation column. These statements were not accurate and are withdrawn:

- the codebook's rule was resolution by discussion or by a third coder, and the drafts were not
  part of it;
- the previously published final labels coincide with the drafts for 121 of the 122
  disagreements;
- label changes entered for 12 passages in the workbook's review sheet were not transferred to
  the final labels;
- the author-confirmation column was added later.

The same statements in this repository are corrected in place:

- `data/README_label_archives.md`, section "Adjudication confirmation note (2026-07-15)": withdrawn;
- `data/README_label_archives.md`, the statements that no file contents were modified and that the
  workbook's bytes are unchanged and its hash still verifies: the workbook was modified when the
  column was added, and its current SHA-256 (`aa072750…`) is not the one recorded for it in
  `data/MANIFEST.sha256` (`b0d365b8…`);
- `REPRO_STATUS.md`, the statement that 20 file records in `data/MANIFEST.sha256` still verify.

## 4. The original May 2026 workbook

The workbook as it stood before the column was added is preserved byte for byte in commit
`e41356a` of this repository, under the path `data/Table_3C_SOTA_validation_metrics.csv`. Despite
the `.csv` extension, that file is an Excel workbook (it begins with the ZIP signature `PK`); the
file now at the same path is a different CSV file. Its SHA-256 is

`b0d365b8a19b9a3b8736e9640381f25cbabd536fe56c0c6ee9b865b8dc7c094f`,

which is the value recorded in `data/MANIFEST.sha256` for the gold-standard workbook. It can be
retrieved with

```
git show e41356a:data/Table_3C_SOTA_validation_metrics.csv > gold_standard_workbook_2026-05.xlsx
```

Commit `e41356a` is part of the public history and is not rewritten.

## 5. The drafts reproduce a five-string rule

Every binary draft is reproduced exactly by a rule that labels a passage GenAI-related if and
only if it contains one of five dictionary strings (121 of 121 binary drafts). The drafts
therefore carry no information from either evaluated LLM rater. The check script and its log are
in `code/draft_rule_check/` (see the README there).

## 6. Re-adjudication

The drafts, and the labels taken from them, have been set aside. All 123 passages without a
concordant binary label were re-adjudicated by a blind third coder under the protocol deposited
before coding (`third_coder/protocol_third_coder_v2.7.md`; GitHub Release
third-coder-protocol-v2.7, commit fd6616d). The released keys, seeds, selection rules, labels and
run records are in `third_coder/release/`; the departures from the protocol are recorded in
`third_coder/DEPARTURE_RECORD.md`. The earlier labels remain in the repository unchanged for
traceability.
