# Data Folder

Only non-licensed, public-facing materials are included here. The folder holds
three layers:

## 1. `public/` and `restricted_placeholder/`

- `public/04_genai_dictionary.xlsx`: the public GenAI dictionary workbook.
- `restricted_placeholder/`: intentionally empty placeholder marking the
  licensed data layers that are NOT redistributed (see `DATA_AVAILABILITY.md`).

## 2. Table 3C SOTA-validation evidence package (folder root)

The files at this folder's root are the measurement-validation evidence behind
the manuscript's Table 3C (SOTA / hybrid validation of the dictionary-based
GenAI measure):

- gold standard: `genai_gold_standard_adjudication_workbook.xlsx` (600
  human double-coded, adjudicated passages), with sampling frame
  `mdna_passage_level_gold_standard_seed.csv/.xlsx` and
  `MDNA_passage_gold_standard_README.md`;
- frozen predictions and published outputs:
  `Table_3C_validation_predictions.csv`,
  `Table_3C_SOTA_validation_metrics.csv/.md/.xlsx`;
- full-sample LLM audit: `full_sample_segments_1256.csv`,
  `full_sample_gpt55_claude_consensus_labels.csv`,
  `full_sample_gpt55_claude_report.md`, and the raw label archives
  `claude_part_01..13.jsonl` (complete) and
  `genai_adoption_labels_part_01..08.jsonl` (GPT-5.5; parts 09-13 missing in
  this copy);
- early pilot validation: the `LLM_validation_*` files;
- package documentation and scripts: `DATA_DICTIONARY.md`,
  `METHODS_AND_REPRODUCTION_NOTES.md`, `SSCI_QC_REPORT.md`,
  `SSCI_REPRODUCTION_CHECKLIST.md`, `ssci_sota_package_overview.md`,
  `recompute_table3c_from_frozen_predictions.py`,
  `validate_ssci_sota_package.py`, `build_table3c_finbert_hybrid.py`;
- integrity: `MANIFEST.sha256` (SHA-256 manifest of the original evidence
  package; 20 file records still verify byte-identically).

These files were uploaded from a package whose internal layout had
subdirectories (`data/gold_standard/`, `evidence/llm_raw_returns/`, ...); this
repository stores them flat. The documentation files above therefore refer to
paths from the original layout — `MANIFEST.sha256` records the mapping.

## 3. Coverage and integrity documentation

See `README_label_archives.md` in this folder for: what each label-archive
series contains, part-by-part coverage, how every file's identity was verified
after the 2026-07-15 file-name repair, and the list of items lost in the
initial upload copy.
