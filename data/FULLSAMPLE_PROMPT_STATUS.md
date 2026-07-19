# Full-Sample LLM Audit Prompt — Provenance and Status

## What this note documents

The full-sample (1,256-passage) LLM audit used one shared instruction prompt, given
verbatim to both raters (GPT-5.5 and Claude Opus 4.7) through their consumer web
interfaces. This note records the archival status of that prompt text.

## Evidence that the prompt existed and was identical across raters

The package's original integrity manifest (`MANIFEST.sha256`, recovered forensically
from this repository and retained at `data/MANIFEST.sha256`) records the prompt file
under two paths with **byte-identical SHA-256 digests**:

```
c980b8250a8af1e956438ab4614ced7f696c453c6111ea0faa3c272d0277de28  evidence/prompts/PROMPT_复制给Claude.txt
c980b8250a8af1e956438ab4614ced7f696c453c6111ea0faa3c272d0277de28  evidence/prompts/PROMPT_复制给GPT55.txt
```

Identical hashes across the two rater-specific copies establish that both models
received the same instructions.

## Current status: text missing from this copy

The prompt *text* itself is not present in this copy of the archive. Two files
carrying the prompt filenames existed in an earlier state of this repository, but a
content audit determined they had been mislabeled during an earlier packaging step —
they actually contained Claude full-sample label parts 10–11, which are now correctly
stored as `claude_part_10.jsonl` / `claude_part_11.jsonl`. No file in this repository
matches the manifest digest `c980b825…`.

If the original prompt text is recovered from the authors' records, it should be
restored at `data/` and verified against the digest above.

## What IS available

- **Pilot-round prompt (140 passages), verbatim**: `data/LLM_validation_prompt.md`
  (three-class labeling instructions: substantive_adoption / generic_or_background /
  not_genai_related, with coding rules). The full-sample audit used the same
  three-class scheme; per-class definitions and decision rules are also documented in
  `data/LLM_validation_coding_rules.md`.
- **All full-sample outputs**: both raters' complete labels
  (`claude_part_01–13.jsonl`, `genai_adoption_labels_part_01–08.jsonl`) and the
  consensus file `full_sample_gpt55_claude_consensus_labels.csv` (1,256 rows, no
  blank label cells — independently verified).
- **Gold standard**: the 600-passage human-coded seed and adjudication workbook.

The audit's *results* are therefore fully reproducible and auditable from this
repository; only the instruction text of the full-sample round is pending recovery.
