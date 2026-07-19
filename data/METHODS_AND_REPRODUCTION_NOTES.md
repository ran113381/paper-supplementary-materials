# Methods and Reproduction Notes

## Scope

This package reproduces the SOTA / hybrid benchmark reported as Table 3C. The benchmark evaluates passage-level semantic relevance for a disclosure-based GenAI proxy.

The package does not claim to measure latent firm capability, internal deployment depth, or model-output quality. It validates whether MD&A passages flagged or classified by each method correspond to GenAI-related disclosure content.

## Gold Standard

The benchmark is locked to 600 human double-coded and adjudicated MD&A passages:

- 216 GenAI-related passages.
- 384 non-GenAI passages.
- No unclear / `U` rows are included in the metric denominator.

## Methods

### Dictionary Rule

The dictionary rule predicts positive when a passage contains a GenAI dictionary hit. It is evaluated on all 600 gold-standard passages.

### GPT-5.5 / Claude Strict Consensus

GPT-5.5 and Claude independently labeled the dictionary-hit passage universe. The strict-consensus row evaluates only rows where the two models provide a covered consensus prediction. Abstentions include non-hit rows and disagreement / uncovered rows.

### FinBERT Fine-Tuned on Strict Consensus

The FinBERT row uses frozen predictions generated from a fine-tuned `yiyanghkust/finbert-tone-chinese` backbone. The exact reproduction package uses the frozen row-level predictions so that reviewers can reproduce Table 3C without internet access or model downloads.

### Hybrid Consensus with Dictionary Fallback

The hybrid rule uses strict LLM consensus when available and falls back to the dictionary rule for non-hit, missing, or disagreement rows.

## Why Frozen Predictions Are the SSCI-Locked Path

The manuscript table must be exactly reproducible by reviewers. Live neural-model retraining can vary by hardware, library versions, model-cache state, and random-number handling. Therefore:

- The deterministic reproduction path recomputes metrics from frozen row-level predictions.
- The optional live FinBERT script is preserved for provenance, not required for exact table reproduction.
- `MANIFEST.sha256` records file hashes for auditability.

