# SSCI Reproducibility Package: Table 3C SOTA / Hybrid Validation

This package reproduces the later-added SOTA benchmark used for Table 3C. It is locked to the corrected 600-passage binary gold standard.

## Quick Reproduction

From this folder:

```bash
python code/recompute_table3c_from_frozen_predictions.py
python code/validate_ssci_sota_package.py
```

The first command recomputes Table 3C from frozen row-level predictions. The second command validates the package, compares recomputed metrics with the published metrics, and writes:

- `outputs/recomputed/Table_3C_recomputed_metrics.csv`
- `outputs/recomputed/Table_3C_recomputed_metrics.md`
- `docs/SSCI_QC_REPORT.md`
- `MANIFEST.sha256`

No pandas, torch, transformers, internet access, or model download is required for the locked reproduction path.

## What Is Reproduced

The package reproduces four Table 3C rows:

- Dictionary rule
- GPT-5.5 / Claude strict consensus
- FinBERT fine-tuned on strict consensus
- Hybrid consensus with dictionary fallback

The expected gold-standard lock is:

- Total validation passages: 600
- GenAI-related gold labels: 216
- Non-GenAI gold labels: 384
- Strict LLM-consensus covered rows: 271

## Package Structure

- `data/gold_standard/`: human double-coded and adjudicated gold-standard workbook.
- `data/sampling_frame/`: annotation seed / sampling frame used to construct the benchmark.
- `data/llm_consensus_source/`: full-sample GPT-5.5 / Claude consensus labels and source segment file.
- `data/table3c_frozen_predictions/`: row-level frozen predictions used for exact Table 3C reproduction.
- `data/table3c_published_outputs/`: published Table 3C outputs from the manuscript workflow.
- `evidence/prompts/`: prompts used for the GPT-5.5 and Claude semantic audit.
- `evidence/llm_raw_returns/`: raw GPT-5.5 and Claude JSONL returns.
- `evidence/early_llm_validation/`: first-stage LLM validation sample, coding rules, returned labels, disagreements, and adjudicated outputs.
- `figures_and_tables/figure_files/`: later-added SOTA / LLM figure files used in the manuscript workflow.
- `figures_and_tables/table_and_figure_packages/`: Chinese working packages that define the later-added SOTA / LLM tables and figures.
- `figures_and_tables/manuscript_snapshots/`: manuscript snapshot containing the later-added Table 3C material.
- `code/`: standard-library reproducibility and validation scripts.
- `code/optional_live_finbert_rerun/`: optional live rerun script for the FinBERT training path.
- `docs/`: data dictionary, method notes, and generated QC report.

## Manual Gold Standard and Added Figures

The human-standard materials are included in two places:

- `data/gold_standard/GenAI_gold_standard_adjudication_draft人工双核验.xlsx`
- `data/manual_gold_standard_evidence/MDNA_passage_gold_standard_README.md`

The later-added figure/table package is also included:

- Figure files: `figures_and_tables/figure_files/`
- Table/figure working notes: `figures_and_tables/table_and_figure_packages/`
- Table 3C row-level and metric outputs: `data/table3c_frozen_predictions/` and `data/table3c_published_outputs/`

## Optional Live FinBERT Rerun

The locked reproduction path uses frozen row-level predictions. A live FinBERT rerun is not required for SSCI table reproduction because it requires external dependencies and the Hugging Face model `yiyanghkust/finbert-tone-chinese`.

The optional script is included only for provenance:

```bash
python code/optional_live_finbert_rerun/build_table3c_finbert_hybrid.py
```

That route requires pandas, openpyxl, torch, transformers, and access to the model files. Use the frozen path above when reviewers need a deterministic, local, exact reproduction of the submitted Table 3C.
