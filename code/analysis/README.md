# Analysis Code: Estimation and Diagnostic Scripts

Date added: 2026-07-15

This folder contains the canonical estimation, panel-construction, and
diagnostic scripts behind the manuscript's regression results (baseline
H1-H3 grid, FY2025 panel extension, and the reviewer-response diagnostic
battery). They are provided for methodological transparency.

## Important: data these scripts read is NOT in this repository

Every script reads firm-level panels derived from licensed CSMAR and CNRDS
databases (see `DATA_AVAILABILITY.md` at the repository root). Those panels are
not redistributed here. All input/output paths are hard-coded absolute paths
from the authors' machine (e.g. `<PROJECT_ROOT>\data\processed_data\...`)
and **must be adjusted locally** by any user who holds licensed access to the
underlying data and has rebuilt the panels. The scripts are published exactly
as run (verified 2026-07-15); no path sanitization was applied so that the code
shown is byte-for-byte the code that produced the reported numbers.

## Software environment

- Python 3.10+ (scripts use modern type-hint syntax such as `int | None`)
- pandas, numpy, openpyxl (Excel panel I/O)
- statsmodels (OLS/WLS with cluster-robust covariance)
- scipy (t/normal reference distributions)
- pyfixest (only `run_bonus_bootstrap.py`: high-dimensional FE + wild-cluster bootstrap)

```powershell
python -m pip install pandas numpy openpyxl statsmodels scipy pyfixest
```

## Group 1 — FY2025 panel-extension pipeline (`01_...` to `06_...` with 2025 in the name)

These six scripts extend the published 2015-2024 dyadic panel by fiscal year
2025 using fresh CSMAR downloads, while reusing the original pipeline's
matching, variable-construction, and scoring functions via module import
(never reimplementing them), and end with an exact-reproduction gate.

| Script | What it does |
| --- | --- |
| `01_build_2025_dyad_pairs.py` | Builds FY2025 focal-partner supplier dyads from the fresh CSMAR top-five-supplier file with the original matching/normalization logic (imported from the frozen pipeline script); writes the 2025-only dyad rows and a full match log. |
| `02_build_2025_firm_year_panel.py` | Builds the FY2025 firm-year financial panel for all firms in the 2025 dyads with the original formulas/field codes; documents every field-code correspondence between old and fresh CSMAR files (SOE mapping, HHI granularity caveat, etc.). |
| `03_build_2025_variable_base.py` | Merges the 2025 panel onto the 2025 dyads and constructs derived variables via the original `construct_variable_base()` (module import); dyad durations inherit true historical inception years from the combined history. |
| `04_score_2025_genai.py` | Scores FY2025 GenAI disclosure intensity with the paper's own dictionary and longest-match counting (imported from the original measurement script); extracts MD&A text by column NAME (documented deviation: the fresh CSMAR file's column layout differs from the old one, so positional extraction would silently read the wrong column). |
| `05_concat_and_rebuild.py` | Concatenates the 2025 slice onto the untouched 2015-2024 slice and rebuilds main/strict winsorized regression packages. Winsorization bounds are FROZEN at their original 2015-2024 values so already-published rows cannot shift (deliberate, documented design decision in the file header). |
| `06_verify_2024_reproduction.py` | CRITICAL GATE: filters the extended packages back to Year<=2024 and re-runs the exact published Table-9 construction; requires coefficient-level reproduction to 4 decimals and the exact original sample sizes before the extension is accepted. |

## Group 2 — Baseline verification and reviewer-response diagnostics

Shared helpers:

| Script | What it does |
| --- | --- |
| `common.py` | Shared loader/spec helpers for the extended (2015-2025) packages: winsorized-sheet loading, construction of `Supplier_Dominance` / `Partner_Ahead` / `Power_Pressure`, industry+year-FE OLS with cluster-robust SEs, H1/H2/H3 term lists. Mirrors the construction verified in `06_verify_2024_reproduction.py`. |
| `battery_ext.py` | Extends `common.py` with alternative moderator constructs (binary partner-dominance, purchase-ratio and duration weightings, binary partner-ahead), NaN-safe construction, patsy term lookup, and a battery runner covering both samples x three cluster/subsample conditions. |

Runners (write CSV/JSON outputs plus readable logs):

| Script | What it does |
| --- | --- |
| `01_main_grid.py` | Full diagnostic grid on the published 2015-2024 packages: Cell A (published spec, firm-clustered SEs), Cell C (collapse to firm-year), Cell D (inverse-dyad-count WLS), Cells E-G (lagged GenAI and firm-FE variants), R1.2 descriptives, R1.5 mean-centering and lagged-R&D interactions, within-firm variation diagnostic, and MDE (minimum detectable effect) calculations. |
| `03_cellB_handroll_crosscheck.py` | Hand-rolled Cameron-Gelbach-Miller (2011) two-way (firm x year) cluster-robust variance as an independent cross-check of the two-way clustering result (V1 + V2 - V12 with PSD eigenvalue clipping). |
| `05_cellB_final.py` | Final Cell B two-way clustering run on both samples, reporting p-values under both the normal reference and the CGM-recommended conservative t(min(G)-1) reference. |
| `06_cellC_fix.py` | Corrected firm-year collapse (Cell C) using the industry value actually recorded within each firm-year group instead of the firm's all-time modal industry. |
| `run_full_battery.py` | R1.8 construct-validity battery: coverage audit by year, then an 8-row battery of alternative `Power_Pressure` operationalizations (code/prose/purchase/duration/binary variants, single components, full three-way joint-necessity specification) on both samples under three clustering/subsample conditions. |
| `run_decomposition.py` | Component-concentration decomposition: per-year non-missing/non-zero rates for `Partner_Ahead`, `Supplier_Dominance`, and binary partner dominance, plus pooled 2023-2025 concentration shares against the panel base rate. |
| `run_bonus_bootstrap.py` | Year-dimension inference stress test via pyfixest: CRV1(Year) asymptotic SEs plus wild-cluster bootstrap (9,999 reps, seed 42, WCR11) on the year dimension for the key interaction terms. |

Note: the scratchpad-era scripts (`common.py`, `battery_ext.py`, `run_*.py`,
`01_main_grid.py`, `03/05/06_cell*.py`) contain `sys.path` and output-directory
constants pointing at the session workspace in which they were verified; adjust
those two constants along with the data paths when running locally.

## Relationship to the rest of the package

- `output/tables/` and `output/figures/` remain frozen exports from the
  authority manuscript (they were NOT regenerated by these scripts inside this
  repository).
- `data/` contains the Table 3C SOTA-validation evidence package (gold standard,
  frozen predictions, LLM label archives) — see `data/README_label_archives.md`.
  The three `.py` files inside `data/` belong to that evidence package and are
  documented there; they are separate from this folder.

## Added 2026-07-19 (revision follow-up round)

- `10_channel_battery.py` -- four-channel candidate-mechanism battery
  (inventory turnover, receivables turnover, administrative-expense ratio,
  operating cash flow) with the persisted bootstrap recipe (1,000 row-level
  resamples, seed 20260407). Self-check: the inventory row must reproduce the
  manuscript's Figure 11 mediation numbers exactly, or the script aborts.
  Usage: `python 10_channel_battery.py <path-to-08A_main_regression_package.xlsx>`
  Output: `data/Table_channel_battery.csv`. Verified result: 0 of 4 channels
  meet the joint mediation criterion.
- `11_boundary_matched_index.py` -- word-boundary-hardened dictionary variant
  (Latin-script term edges must not be adjacent to another ASCII letter/digit).
  Self-checks: baseline recount equals the package counts on all 2,024
  firm-year sides with text; the package index reproduces as
  ln(1+count) upper-winsorized at its within-sample 99th percentile.
  Usage: `python 11_boundary_matched_index.py <raw-mda-panel.parquet> <08A-package.xlsx>`
  Output: `data/Table_boundary_robustness.csv`. Verified result: pre-2022
  firm-years with any hit fall 96 -> 29; H1 -0.0184 (p=0.0003),
  H2 contemporaneous -0.0353 (p=0.019), H3 -0.0089 (p<0.001).

## Added 2026-07-24 (round-2 minor revision, Reviewer 1)

- `12_curvature_test.py` -- curvature-in-intensity test answering the request for
  a U-shaped specification. Adds a quadratic term in GenAI disclosure intensity
  to the Table 9 column (1) baseline and applies the Lind & Mehlum (2010) U-test
  conditions (significant quadratic term, opposite-signed and individually
  significant end-point slopes, interior turning point). Self-check: the linear
  baseline must reproduce the published Table 9 column (1) coefficient (-0.0146),
  R-squared (0.384) and N (1,017), or the script aborts.
  Usage: `python 12_curvature_test.py <08A.xlsx> [<08B.xlsx>]`
  Output: `data/curvature_test_results.json`. Verified result: the squared term
  is NOT significant in either sample (-0.0129, p = 0.28 main; -0.0087, p = 0.48
  strict) and the U-test conditions are not met, because the slope at the lower
  end of the intensity range is indistinguishable from zero. Scope note: this
  tests curvature in the DOSE of disclosure, not curvature in time.
- `13_event_study_extended.py` -- extends the event-study horizon with the
  fiscal-2025 data, reusing the exact recipe of `code/09_run_did_and_placebo.py`
  (focal firm-year collapse, first-disclosure cohorts vs never-disclosing
  controls, firm and year fixed effects, SEs clustered by Focal_ID, reference
  period t = -1) and applying the Section 4.7 clean-text filter before the
  collapse. Self-check: the published recipe must reproduce Figure 9's
  post-disclosure coefficients (t = 0: -0.0130, t = +1: -0.0204) or the script
  aborts. Usage:
  `python 13_event_study_extended.py <08A_2015_2024.xlsx> <08A_2025.xlsx>`
  Output: `data/event_study_extended.json`. Verified result: under the published
  cohort definition (>=2023) the coefficients are -0.0122 at t = 0 (61 treated
  firms), -0.0070 at t = +1 (15 firms) and +0.0112 at t = +2 (5 firms, p = 0.63);
  under a wider cohort variant (>=2022, NOT like-for-like with Figure 9) they are
  -0.0400 at t = +2 (11 firms) and -0.0308 at t = +3 (3 firms). No post-disclosure
  coefficient is statistically significant, and the sign beyond t = +1 depends on
  the cohort definition, so the later time profile is not identified.
