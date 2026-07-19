# Reproduction Status

Date: `2026-07-17` (supersedes the 2026-07-15 and 2026-04-20 statements)

## Current Status

- public package type: manuscript-supporting archive with code and validation evidence
- frozen table layer: included — **synchronized 2026-07-17 to the revised
  manuscript's full set of 14 tables** (`output/tables/`, see
  `docs/EXHIBIT_MAP.md`)
- frozen figure layer: included — **all 14 figures as embedded in the revised
  manuscript** (`output/figures/manuscript_render/`), plus legacy exports and
  the SHAP swarm-plot archive
- public dictionary layer: included
- measurement-validation evidence layer (Table 3C gold standard, frozen
  predictions, LLM label archives, SHA-256 manifest): included, file names
  repaired 2026-07-15 (see `CHANGES_PROPOSED.md` and
  `data/README_label_archives.md`)
- false-positive-rate tables by keyword category × year: included
  (`data/Table_FP_rates_by_category_year.csv`, builder script
  `data/build_fp_rate_tables.py`, fully reproducible from package-internal data)
- estimation and diagnostic code (`code/analysis/`, incl. the verified FY2025
  clean-text script `07_fy2025_cleantext_extension.py`): included
- raw-data redistribution: not included (license-restricted)
- one-click raw-to-final rerun from this repository alone: not possible,
  because the licensed raw-data layer is excluded

## What Is Strongly Supported

- the final exhibit layer seen by manuscript readers
- the GenAI dictionary attachment material
- the authority manuscript's visible tables and figures
- the exact estimation specifications and diagnostic batteries
  (`code/analysis/`, with script-level documentation)
- exact reproduction of Table 3C from frozen row-level predictions
  (`data/Table_3C_validation_predictions.csv` plus the evidence-package
  scripts in `data/`), verified against the published metrics
- integrity of the validation evidence: 20 file records in
  `data/MANIFEST.sha256` still verify byte-identically

## What Still Requires Private Local Work

- raw-data reconstruction (requires licensed CSMAR / CNRDS access)
- firm-level processed-panel release decisions
- restoring evidence items lost in the initial upload copy (GPT-5.5 raw-return
  parts 09-13, the full-sample audit prompt file, four SVG figures, the
  manuscript snapshot; itemized in `data/README_label_archives.md`)
- end-to-end rerun validation on a licensed environment

## Recommended Citation Language

When describing this package, use wording such as:

`This GitHub package provides manuscript-supporting frozen exhibits, dictionary
materials, the estimation and diagnostic code, and the measurement-validation
evidence (gold standard, frozen predictions, and LLM label archives), but the
licensed raw-data layer is not publicly redistributed, so a full raw-to-final
rerun requires licensed CSMAR/CNRDS access.`

## 2026-07-19 follow-up round

- Four-channel mediation battery persisted (`code/analysis/10_channel_battery.py`):
  the response letter's R1.9 claim now has a runnable in-package source; the
  inventory-turnover row reproduces the manuscript Figure 11 numbers to the
  reported digits (self-check enforced in-script), and 0 of 4 channels meet the
  joint mediation criterion (a-path p<0.05 AND bootstrap CI excluding zero).
- Word-boundary-hardened dictionary variant persisted
  (`code/analysis/11_boundary_matched_index.py`): baseline recount matched the
  regression package on all 2,024 text-covered firm-year sides (0 mismatches)
  before the variant was computed. Reported in manuscript S4.4.
- Term-level FP table (`data/build_fp_rate_tables_by_term.py`) added; anchors
  cross-checked against the archived term audit (1,256 matched segments,
  154 pre-2022, 0 substantive pre-2022).
- `manuscript_render/figure_05/06/07/09.png` regenerated from re-verified fits
  (all Table 9 / lagged-H2 / event-study numbers asserted to 4dp before
  drawing); defects removed: stale "See Table 5" pointer (Fig 5), percentile
  annotations inconsistent with Table 7 (Fig 6), matplotlib debug residue and
  "X_max" tick (Fig 7), t=0-as-reference contradiction (Fig 9).
