# Label Archives: Series, Coverage, and Integrity Notes

Date: 2026-07-15

This note documents the LLM label archives in `data/`, what each part-file series
contains, which parts exist, which are missing, and how the current file set was
verified. It should be read together with `MANIFEST.sha256` (the SHA-256 manifest
of the original evidence package) and `CHANGES_PROPOSED.md` at the repository root.

## Background: the July 2026 file-name repair

The `data/` folder in the initial GitHub upload had file NAMES and file CONTENTS
shuffled against each other (files carried extensions and names belonging to other
files). On 2026-07-15 every file was re-identified and renamed, using two methods:

1. **Cryptographic recovery.** `MANIFEST.sha256` (itself uploaded under a wrong
   name) records SHA-256 hashes and original paths for the intact evidence
   package. Every current file was hashed and matched against it; 20 manifest
   path records were recovered byte-identically and now sit at their original
   basenames. Anyone can re-verify: hash any of those files and look the digest
   up in `MANIFEST.sha256`.
2. **Content forensics** for files whose bytes were re-serialized (hash no longer
   in the manifest): label part-files were attributed to their model by exact
   comparison against the per-model label columns of the consensus file (see
   "Attribution verification" below); documentation and script files were
   identified by their headings and code contents.

No file contents were modified at any point — renames only, verified by SHA-256
before/after.

## Series 1: Full-sample audit, segments `P2FULL_0001`-`P2FULL_1256`

All 1,256 dictionary-hit MD&A passages were independently labeled by GPT-5.5 and
Claude (three-class scheme: `substantive_adoption` / `generic_or_background` /
`unclear`). Raw per-batch model returns were archived in ~100-segment chunks.

### Claude raw returns — COMPLETE (13/13 parts)

| File | Segments | Lines |
| --- | --- | --- |
| `claude_part_01.jsonl` | P2FULL_0001-0100 | 100 |
| `claude_part_02.jsonl` | P2FULL_0101-0200 | 100 |
| `claude_part_03.jsonl` | P2FULL_0201-0300 | 100 |
| `claude_part_04.jsonl` | P2FULL_0301-0400 | 100 |
| `claude_part_05.jsonl` | P2FULL_0401-0500 | 100 |
| `claude_part_06.jsonl` | P2FULL_0501-0600 | 100 |
| `claude_part_07.jsonl` | P2FULL_0601-0700 | 100 |
| `claude_part_08.jsonl` | P2FULL_0701-0800 | 100 |
| `claude_part_09.jsonl` | P2FULL_0801-0900 | 100 |
| `claude_part_10.jsonl` | P2FULL_0901-1000 | 100 |
| `claude_part_11.jsonl` | P2FULL_1001-1100 | 100 |
| `claude_part_12.jsonl` | P2FULL_1101-1200 | 100 |
| `claude_part_13.jsonl` | P2FULL_1201-1256 | 56 |

### GPT-5.5 raw returns — PARTIAL (8/13 parts)

| File | Segments | Lines |
| --- | --- | --- |
| `genai_adoption_labels_part_01.jsonl` | P2FULL_0001-0100 | 100 |
| `genai_adoption_labels_part_02.jsonl` | P2FULL_0101-0200 | 100 |
| `genai_adoption_labels_part_03.jsonl` | P2FULL_0201-0300 | 100 |
| `genai_adoption_labels_part_04.jsonl` | P2FULL_0301-0400 | 100 |
| `genai_adoption_labels_part_05.jsonl` | P2FULL_0401-0500 | 100 |
| `genai_adoption_labels_part_06.jsonl` | P2FULL_0501-0600 | 100 |
| `genai_adoption_labels_part_07.jsonl` | P2FULL_0601-0700 | 100 |
| `genai_adoption_labels_part_08.jsonl` | P2FULL_0701-0800 | 100 |
| parts 09-13 (P2FULL_0801-1256) | **missing in this copy** | — |

Note on an earlier gap report: before the file-name repair, a filename-based scan
suggested `claude_part_01/06/07` and `genai_adoption_labels_part_04` were the
missing parts. That was an artifact of the shuffled names. After content
recovery, the Claude series is complete and the true gap is the GPT-5.5 raw
returns for segments 0801-1256 (parts 09-13).

### Attribution verification

Each part-file was checked line-by-line against the per-model columns of
`full_sample_gpt55_claude_consensus_labels.csv`:

- every `claude_part_NN` file agrees 100% with the `claude_label` column on its
  segment range (and only 34-94% with `gpt55_label`);
- every `genai_adoption_labels_part_NN` file agrees 100% with the `gpt55_label`
  column on its segment range (and only 81-94% with `claude_label`).

This confirms both the model attribution and the segment coverage stated above.

### The consensus CSV is the complete merged record

`full_sample_gpt55_claude_consensus_labels.csv` — verified on 2026-07-15:

- **1,256 rows**, one per segment, `P2FULL_0001` through `P2FULL_1256`, no
  duplicates;
- `gpt55_label` and `claude_label` populated in **every** row (zero blanks),
  together with per-model confidence and rationale columns;
- `consensus_label` distribution: 483 `substantive_adoption`,
  279 `generic_or_background`, 372 `unclear`, 122 `disagreement`.

Because the consensus CSV retains both models' labels for all 1,256 segments,
the missing GPT-5.5 raw-return parts 09-13 do **not** remove any label data used
by the paper; what is lost is only the standalone per-batch return files for
that range (a redundancy/audit-trail layer), not the labels themselves.

## Series 2: Early pilot validation, segments `P2VAL_001`-`P2VAL_140`

A 140-passage stratified pilot (60 substantive / 60 generic / 20 strategic by
the original dictionary labels) used to design the full-sample audit:

- `LLM_validation_sample.csv` — the 140-passage sample (labels blank, for coding);
- `LLM_validation_prompt.md` — the pilot prompt given to the labeling LLM;
- `LLM_validation_coding_rules.md` — three-class coding rules (Chinese);
- `LLM_validation_results_returned.jsonl` — first-round returns (140 lines);
- `LLM_validation_disagreements_for_adjudication.csv` — 70 first-round
  dictionary/LLM disagreements sent to the second model;
- `LLM_validation_adjudication_returned.jsonl` — second-model adjudication
  returns (70 lines);
- `LLM_validation_adjudicated_labels.csv` — final 140-row adjudicated labels;
- `LLM_validation_metrics_report.md` / `LLM_validation_adjudicated_metrics_report.md`
  — first-round and post-adjudication metric reports.

## Gold standard and Table 3C evidence (related files)

- `genai_gold_standard_adjudication_workbook.xlsx` — human double-coded and
  adjudicated gold-standard workbook (600 binary final labels: 216 GenAI-related,
  384 non-GenAI; sheets: Annotation_Blind, Sampling_Metadata, Codebook,
  Sampling_Log, Adjudication_Summary, Disagreement_Review). Original name in
  `MANIFEST.sha256`: `GenAI_gold_standard_adjudication_draft人工双核验.xlsx`
  (renamed to English; bytes unchanged — hash still verifies).
- `Table_3C_validation_predictions.csv` — 600 frozen row-level predictions used
  to reproduce Table 3C exactly.
- `Table_3C_SOTA_validation_metrics.csv` / `.md` / `.xlsx` — published Table 3C
  outputs. The CSV is byte-identical to the recomputed
  `outputs/recomputed/Table_3C_recomputed_metrics.csv` recorded in
  `MANIFEST.sha256` (same hash, two manifest entries), which cryptographically
  corroborates the QC report's "published metrics equal recomputed metrics"
  check.
- `mdna_passage_level_gold_standard_seed.csv` / `.xlsx` — 1,706-passage sampling
  frame (1,256 dictionary-hit + 450 non-hit) used to build the gold standard.
- `full_sample_segments_1256.csv` — the 1,256 dictionary-hit segments with text.
- `recompute_table3c_from_frozen_predictions.py`,
  `validate_ssci_sota_package.py`, `build_table3c_finbert_hybrid.py` — the
  original evidence-package scripts (deterministic Table 3C recomputation,
  package QC, and the optional live FinBERT rerun, respectively). They reference
  the original package's directory layout recorded in `MANIFEST.sha256`; this
  repository stores the same files flat under `data/`.

## Lost in this copy (per MANIFEST.sha256)

The following original items have no byte-identical counterpart on disk, and
their content could not be located in any current file:

- GPT-5.5 raw returns parts 09-13 (`genai_adoption_labels_part_09..13.jsonl`,
  segments P2FULL_0801-1256) — labels survive in the consensus CSV;
- `PROMPT_复制给Claude.txt` and `PROMPT_复制给GPT55.txt` — the full-sample audit
  prompt (the manifest shows both files had identical content; the surviving
  `LLM_validation_prompt.md` is the earlier pilot prompt, not this one);
- all four SVG figures (`Figure_SOTA_LLM_validation_workflow.svg`,
  `Figure_LLM_adjudicated_label_distribution.svg`,
  `Figure_GPT55_Claude_label_distribution.svg`,
  `Figure_Dictionary_vs_LLM_consensus.svg`);
- the four Chinese figure/table working-package notes
  (`08_SOTA_LLM_支持图表模板.md`, `15_SOTA_LLM_最终图表包.md`,
  `18_GPT55全样本_SOTA最终图表包.md`, `22_SOTA_LLM_双模型最终图表包.md`);
- the manuscript snapshot
  `Paper2_revised_policy_light_reinforcement_Table3C_600gold_noU_IPM_refs.docx`;
- `outputs/recomputed/Table_3C_recomputed_metrics.md` (the recomputed CSV
  survives — see above).

The original raw-return part files also do not hash-match the manifest because
the surviving copies were re-serialized (JSON key spacing/encoding differences);
their contents were recovered and re-verified against the consensus columns as
described above.

These items can be restored from the authors' local archive in a future commit;
none of them affects the numbers reported in the manuscript, whose reproduction
path runs through the frozen predictions and the consensus CSV, both of which
are present and hash-verified.


## Adjudication confirmation note (2026-07-15)

The 122 inter-coder disagreement rows in `genai_gold_standard_adjudication_workbook.xlsx` (sheet `Disagreement_Review`) were adjudicated via AI-assisted drafts (Claude Opus 4.7) and subsequently reviewed and confirmed by the authors. The original `review_status` values ("Draft adjudicated") are preserved unchanged for audit purposes; a dated `author_confirmation` column has been added recording the completed author review. This note documents the confirmation without altering the historical record.
