# Proposed Changes (2026-07-15) — NOT YET COMMITTED

**Nothing in this change set has been committed or pushed.** All changes exist
only in the local working tree. The author must review, then commit and push
manually (or explicitly authorize it). `git status` will show every change.

## Why

The initial upload's `data/` folder had file NAMES and file CONTENTS shuffled
against each other: files carried other files' names and extensions (e.g. a
`.docx`-named file containing JSONL labels, a `.csv`-named file containing an
xlsx workbook, internal working filenames leaking revision-workflow language).
The manuscript is under review at IP&M and Reviewer 1 criticized
reproducibility transparency, so the package was repaired locally.

## How each file's true identity was established

1. **Cryptographic recovery.** The file uploaded as
   `GenAI_gold_standard_adjudication_draft人工双核验.xlsx` is actually
   `MANIFEST.sha256` — the SHA-256 manifest of the original evidence package,
   listing every original file's hash and path. Every current file was hashed
   and matched against it: 20 manifest path records matched byte-identically
   and were restored to their original basenames.
2. **Content forensics** for files whose bytes were re-serialized (hash not in
   the manifest): each LLM label part-file was attributed by exact comparison
   against the per-model columns of the 1,256-row consensus file (every Claude
   part agrees 100% with `claude_label` on its segment range; every GPT-5.5
   part agrees 100% with `gpt55_label`; cross-model agreement is only 34-94%,
   so attribution is unambiguous). Documentation and script files were
   identified from their headings and code contents.

File contents were never edited — renames only, verified byte-identical by
SHA-256 before/after each rename pass. Two documentation files (`data/README.md`
and the root docs listed below) were edited as documentation, not evidence.

## Complete rename table (old name at git HEAD -> new name), all inside `data/`

### Group A — restored by exact SHA-256 match against `MANIFEST.sha256`

| Old name (HEAD) | New name | Original path per manifest |
| --- | --- | --- |
| `GenAI_gold_standard_adjudication_draft人工双核验.xlsx` | `MANIFEST.sha256` | (the manifest itself) |
| `Table_3C_SOTA_validation_metrics.csv` | `genai_gold_standard_adjudication_workbook.xlsx` | `data/gold_standard/GenAI_gold_standard_adjudication_draft人工双核验.xlsx` (English name adopted) |
| `Table_3C_SOTA_validation_metrics.xlsx` | `full_sample_gpt55_claude_consensus_labels.csv` | `data/llm_consensus_source/full_sample_gpt55_claude_consensus_labels.csv` |
| `DATA_DICTIONARY.md` | `full_sample_gpt55_claude_report.md` | `data/llm_consensus_source/full_sample_gpt55_claude_report.md` |
| `METHODS_AND_REPRODUCTION_NOTES.md` | `full_sample_segments_1256.csv` | `data/llm_consensus_source/full_sample_segments_1256.csv` |
| `LLM_validation_adjudicated_metrics_report.md` | `mdna_passage_level_gold_standard_seed.csv` | `data/sampling_frame/mdna_passage_level_gold_standard_seed.csv` |
| `LLM_validation_adjudication_returned.jsonl` | `mdna_passage_level_gold_standard_seed.xlsx` | `data/sampling_frame/mdna_passage_level_gold_standard_seed.xlsx` |
| `SSCI_REPRODUCTION_CHECKLIST.md` | `MDNA_passage_gold_standard_README.md` | `data/manual_gold_standard_evidence/MDNA_passage_gold_standard_README.md` |
| `LLM_validation_disagreements_for_adjudication.csv` | `Table_3C_validation_predictions.csv` | `data/table3c_frozen_predictions/Table_3C_validation_predictions.csv` |
| `LLM_validation_prompt.md` | `Table_3C_SOTA_validation_metrics.csv` | `data/table3c_published_outputs/Table_3C_SOTA_validation_metrics.csv` (same bytes as `outputs/recomputed/Table_3C_recomputed_metrics.csv`) |
| `LLM_validation_results_returned.jsonl` | `Table_3C_SOTA_validation_metrics.md` | `data/table3c_published_outputs/Table_3C_SOTA_validation_metrics.md` |
| `LLM_validation_sample.csv` | `Table_3C_SOTA_validation_metrics.xlsx` | `data/table3c_published_outputs/Table_3C_SOTA_validation_metrics.xlsx` |
| `claude_part_04.jsonl` | `SSCI_QC_REPORT.md` | `docs/SSCI_QC_REPORT.md` |
| `claude_part_08.jsonl` | `LLM_validation_adjudicated_labels.csv` | `evidence/early_llm_validation/LLM_validation_adjudicated_labels.csv` |
| `claude_part_09.jsonl` | `LLM_validation_adjudicated_metrics_report.md` | `evidence/early_llm_validation/LLM_validation_adjudicated_metrics_report.md` |
| `claude_part_10.jsonl` | `LLM_validation_adjudication_returned.jsonl` | `evidence/early_llm_validation/LLM_validation_adjudication_returned.jsonl` |
| `claude_part_12.jsonl` | `LLM_validation_disagreements_for_adjudication.csv` | `evidence/early_llm_validation/LLM_validation_disagreements_for_adjudication.csv` |
| `claude_part_13.jsonl` | `LLM_validation_metrics_report.md` | `evidence/early_llm_validation/LLM_validation_metrics_report.md` |
| `genai_adoption_labels_part_02.jsonl` | `LLM_validation_results_returned.jsonl` | `evidence/early_llm_validation/LLM_validation_results_returned.jsonl` |
| `genai_adoption_labels_part_03.jsonl` | `LLM_validation_sample.csv` | `evidence/early_llm_validation/LLM_validation_sample.csv` |

### Group B — content-identified documents and scripts (re-saved copies; hash not in manifest)

| Old name (HEAD) | New name | Identified as |
| --- | --- | --- |
| `claude_part_02.jsonl` | `DATA_DICTIONARY.md` | evidence-package data dictionary (`docs/DATA_DICTIONARY.md`) |
| `claude_part_03.jsonl` | `METHODS_AND_REPRODUCTION_NOTES.md` | evidence-package methods notes (`docs/METHODS_AND_REPRODUCTION_NOTES.md`) |
| `claude_part_05.jsonl` | `SSCI_REPRODUCTION_CHECKLIST.md` | evidence-package checklist (`docs/SSCI_REPRODUCTION_CHECKLIST.md`) |
| `claude_part_11.jsonl` | `LLM_validation_coding_rules.md` | pilot-validation coding rules |
| `genai_adoption_labels_part_01.jsonl` | `LLM_validation_prompt.md` | pilot-validation prompt |
| `full_sample_gpt55_claude_consensus_labels.csv` | `ssci_sota_package_overview.md` | the original evidence package's root README |
| `full_sample_segments_1256.csv` | `recompute_table3c_from_frozen_predictions.py` | deterministic Table 3C recomputation script |
| `MDNA_passage_gold_standard_README.md` | `validate_ssci_sota_package.py` | evidence-package QC/validation script |
| `mdna_passage_level_gold_standard_seed.xlsx` | `build_table3c_finbert_hybrid.py` | optional live FinBERT rerun script |

### Group C — LLM label archives, attributed by 100% agreement with the consensus columns

| Old name (HEAD) | New name | Content (segments) |
| --- | --- | --- |
| `genai_adoption_labels_part_05.jsonl` | `claude_part_01.jsonl` | Claude labels P2FULL_0001-0100 |
| `genai_adoption_labels_part_06.jsonl` | `claude_part_02.jsonl` | Claude labels P2FULL_0101-0200 |
| `genai_adoption_labels_part_07.jsonl` | `claude_part_03.jsonl` | Claude labels P2FULL_0201-0300 |
| `genai_adoption_labels_part_08.jsonl` | `claude_part_04.jsonl` | Claude labels P2FULL_0301-0400 |
| `genai_adoption_labels_part_09.jsonl` | `claude_part_05.jsonl` | Claude labels P2FULL_0401-0500 |
| `genai_adoption_labels_part_10.jsonl` | `claude_part_06.jsonl` | Claude labels P2FULL_0501-0600 |
| `genai_adoption_labels_part_11.jsonl` | `claude_part_07.jsonl` | Claude labels P2FULL_0601-0700 |
| `genai_adoption_labels_part_12.jsonl` | `claude_part_08.jsonl` | Claude labels P2FULL_0701-0800 |
| `genai_adoption_labels_part_13.jsonl` | `claude_part_09.jsonl` | Claude labels P2FULL_0801-0900 |
| `PROMPT_复制给Claude.txt` | `claude_part_10.jsonl` | Claude labels P2FULL_0901-1000 |
| `PROMPT_复制给GPT55.txt` | `claude_part_11.jsonl` | Claude labels P2FULL_1001-1100 |
| `Figure_Dictionary_vs_LLM_consensus.svg` | `claude_part_12.jsonl` | Claude labels P2FULL_1101-1200 |
| `Figure_GPT55_Claude_label_distribution.svg` | `claude_part_13.jsonl` | Claude labels P2FULL_1201-1256 |
| `Figure_SOTA_LLM_validation_workflow.svg` | `genai_adoption_labels_part_01.jsonl` | GPT-5.5 labels P2FULL_0001-0100 |
| `Paper2_revised_policy_light_reinforcement_Table3C_600gold_noU_IPM_refs.docx` | `genai_adoption_labels_part_02.jsonl` | GPT-5.5 labels P2FULL_0101-0200 |
| `08_SOTA_LLM_支持图表模板.md` | `genai_adoption_labels_part_03.jsonl` | GPT-5.5 labels P2FULL_0201-0300 |
| `15_SOTA_LLM_最终图表包.md` | `genai_adoption_labels_part_04.jsonl` | GPT-5.5 labels P2FULL_0301-0400 |
| `18_GPT55全样本_SOTA最终图表包.md` | `genai_adoption_labels_part_05.jsonl` | GPT-5.5 labels P2FULL_0401-0500 |
| `22_SOTA_LLM_双模型最终图表包.md` | `genai_adoption_labels_part_06.jsonl` | GPT-5.5 labels P2FULL_0501-0600 |
| `Table_3C_recomputed_metrics.csv` | `genai_adoption_labels_part_07.jsonl` | GPT-5.5 labels P2FULL_0601-0700 |
| `Table_3C_recomputed_metrics.md` | `genai_adoption_labels_part_08.jsonl` | GPT-5.5 labels P2FULL_0701-0800 |

Unchanged in `data/`: `README.md` (name kept, content refreshed — see below),
`public/04_genai_dictionary.xlsx`, `restricted_placeholder/README.md` (both
verified correct as-is).

Note: because many old names were reused by different files, several NEW names
coincide with OLD names of other files (e.g. `claude_part_02.jsonl` existed
before and exists now, with different, now-correct content). The mapping above
is exact; read it row by row.

### Deviations from the earlier cleanup plan

The earlier plan (based on preliminary content guesses) proposed names like
`llm_audit_prompt_claude.txt` and `llm_fullsample_results_check.md`. Deeper
verification found: (a) the two `PROMPT_复制给*.txt` files did NOT contain the
audit prompts — they contain Claude label parts 10-11; the actual full-sample
prompt file is missing from this copy (see below); (b) `MANIFEST.sha256`
provides the true original names, which were restored in preference to
invented neutral names.

## Known-missing items (documented, not fixable by renaming)

Per `MANIFEST.sha256`, the following original files have no surviving copy in
the repository (details in `data/README_label_archives.md`):

- GPT-5.5 raw-return parts 09-13 (segments P2FULL_0801-1256) — the labels
  themselves survive inside `full_sample_gpt55_claude_consensus_labels.csv`
  (verified: 1,256 rows, zero blank `gpt55_label`/`claude_label` cells);
- `PROMPT_复制给Claude.txt` / `PROMPT_复制给GPT55.txt` (the full-sample audit
  prompt; both were identical per the manifest);
- all four `Figure_*.svg` files;
- the four Chinese figure/table working-package notes (`08_/15_/18_/22_...md`);
- the manuscript snapshot `.docx`;
- `outputs/recomputed/Table_3C_recomputed_metrics.md` (the recomputed CSV
  survives — it is byte-identical to the published CSV).

Restoring these from the authors' local archive is recommended before or after
the first cleanup commit.

## Added files

- `data/README_label_archives.md` — label-archive series, coverage,
  verification method, and missing-items list
- `code/analysis/README.md` — script-by-script guide, licensed-data caveat,
  software environment
- `code/analysis/` — 15 analysis scripts (copied from the authors' verified
  local versions; no data files copied):
  - FY2025 panel extension: `01_build_2025_dyad_pairs.py`,
    `02_build_2025_firm_year_panel.py`, `03_build_2025_variable_base.py`,
    `04_score_2025_genai.py`, `05_concat_and_rebuild.py`,
    `06_verify_2024_reproduction.py`
  - diagnostics: `common.py`, `battery_ext.py`, `01_main_grid.py`,
    `03_cellB_handroll_crosscheck.py`, `05_cellB_final.py`, `06_cellC_fix.py`,
    `run_full_battery.py`, `run_decomposition.py`, `run_bonus_bootstrap.py`
- `CHANGES_PROPOSED.md` — this file

## Edited documentation (in place)

- `README.md` — Package Type now states that estimation/diagnostic code and the
  validation-evidence layer ARE included (raw licensed data still excluded);
  Repository Layout updated for `code/analysis/` and the real `data/` contents;
  pointer to this change log added.
- `REPRO_STATUS.md` — status lines updated (code + validation evidence
  included; raw data still license-restricted; missing-items note); date bumped
  to 2026-07-15.
- `docs/EXHIBIT_MAP.md` — exhibit mappings untouched; appended a "Code Assets"
  section listing the new analysis scripts and the evidence-package scripts.
- `PACKAGE_MANIFEST.csv` — regenerated to cover the full current tree
  (113 entries; the old version listed 40 and omitted every `data/` evidence
  file and `output/shap_files/`).
- `code/README.md` — now describes both the packaging utility and `analysis/`.
- `data/README.md` — now describes the three layers actually in `data/`
  (public dictionary, restricted placeholder, Table 3C evidence package); the
  old text claimed the folder contained only `public/` and
  `restricted_placeholder/`.

Not edited (suggested follow-ups for the author):

- `DATA_AVAILABILITY.md` — still accurate on the license boundary, but its
  "estimation chain requires additional audit" wording predates the inclusion
  of `code/analysis/`.
- `RUN_INSTRUCTIONS.md` — still accurate (no raw-data rerun from this repo),
  but could mention `code/analysis/` for licensed users.
- `requirements.txt` — covers only the docx-extraction utility; the analysis
  environment is documented in `code/analysis/README.md` instead.

## Verification performed (all with `D:\python.exe`, scripts in session scratchpad)

- extension-vs-content audit over all 53 files in `data/` (recursive):
  0 mismatches after the repair;
- SHA-256 of every renamed file compared before/after each rename pass:
  all byte-identical;
- hash reconciliation against `MANIFEST.sha256`: 20 path records recovered;
- label-attribution test: every `claude_part_*` file 100% consistent with the
  consensus `claude_label` column; every `genai_adoption_labels_part_*` file
  100% consistent with `gpt55_label`;
- consensus CSV completeness: 1,256 unique rows (P2FULL_0001-1256), zero blank
  per-model label cells; consensus distribution 483 substantive / 279 generic /
  372 unclear / 122 disagreement;
- xlsx sheet inspection: gold workbook (Annotation_Blind, Codebook,
  Adjudication_Summary, ...), published metrics workbook (Table_3C,
  validation_predictions, finbert_train_pseudo_labels), sampling-frame seed
  (passages, summary, dictionary_terms) — all consistent with their restored
  identities.

## Git state

**No commit has been made. No push has been made. No remote interaction of any
kind.** Every change above is an uncommitted working-tree modification for the
author to review. To adopt: review the diff, then `git add -A && git commit`
and push manually.
