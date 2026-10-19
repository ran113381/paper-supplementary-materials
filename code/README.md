# Code Folder

This folder contains two layers:

- `extract_docx_exhibits.py`
  - a lightweight packaging helper that exports embedded tables and figures
    from a manuscript `.docx`; it is not part of the estimation chain.
- `analysis/`
  - the canonical estimation, panel-construction, and diagnostic scripts
    behind the manuscript's regression results (added 2026-07-15).
  - these scripts read licensed CSMAR/CNRDS-derived panels that are NOT
    included in this repository; paths must be adjusted locally.
  - see `analysis/README.md` for a script-by-script guide and the software
    environment.

## Added 2026-07-19

- `05_build_genai_measurement.py` -- the measurement build script, published
  exactly as run. It preserves, verbatim, the authors' original Excel-style
  substring-counting formula (`FORMULA_TEXT`) from which the 103-term lexicon
  originates, and builds `data/public/04_genai_dictionary.xlsx` plus the
  firm-year GenAI panel from the licensed raw text sources (CSMAR/CNRDS; not
  redistributed -- see DATA_AVAILABILITY.md). The frozen dictionary file in
  this package is byte-identical to the one this script produced for the
  original submission; no term was edited at any point afterwards.

## Added 2026-07-20

- `09_run_did_and_placebo.py` -- the identification script behind Section 4.3,
  published exactly as run. It produces both the event-study estimates plotted
  in Figure 9 and the 500-draw random-permutation placebo distribution plotted
  in Figure 8.

  The placebo test is estimated on the **focal firm-year panel** -- the 1,017
  dyad-year observations collapsed to 852 focal firm-year records -- with
  industry and year fixed effects, the focal-firm control vector alongside
  dyad-averaged partner controls, and standard errors clustered by the focal
  firm's industry. It permutes the continuous `Focal_GenAI_Index` (not a binary
  adopter flag), unstratified, 500 times under `seed=42`. The actual estimate is
  -0.012681 (SE 0.004816); exactly one of the 500 draws falls at or below it, so
  the empirical p-value is 0.002 one- and two-sided.

  Note that this 852-firm-year figure is NOT the 1,017 dyad-year estimation
  sample used in Tables 9-15, and the companion TWFE-DID in the same script runs
  on a further-restricted late-treated/never-treated subsample -- the three N's
  are different by design.

  The stored draws are released as `data/placebo_500_permutations_verified.json`;
  re-running this script with the same seed reproduces them elementwise. The
  licensed CSMAR/CNRDS-derived panels it reads are not redistributed (see
  DATA_AVAILABILITY.md).

## Added 2026-10-18

- `09_run_did_and_placebo.py` is kept unchanged as run. Its companion static
  TWFE-DID uses the earlier calendar definition `Post = (Year >= 2023)`, which
  codes the 2024 cohort as treated in 2023. The identification summary now uses a
  cohort-specific Post (`Post = 1` from each cohort's own first-disclosure year),
  estimated by `analysis/16_static_did_cohort_post.py`; that script executes the
  functions of `09_run_did_and_placebo.py` verbatim and reproduces the archived
  result of the old definition as a gate. Log and summary table:
  `output/logs/16_static_did_cohort_post.log` and `.csv`.
- `analysis/14_callaway_santanna.py`, `analysis/14b_csdid_crosscheck.py` and
  `analysis/15_event_study_fy2025_raw_vs_clean.py`: see `analysis/README.md`.
- `draft_rule_check/`: checks of the earlier adjudication drafts of the gold
  standard (see `draft_rule_check/README.md` and `../CORRECTION_NOTE.md`).

These scripts are released as run and still carry absolute local paths; the
environment variables below do not apply to them.

## Configuring data locations

The scripts previously carried absolute paths from the authors' machine. They
now read four environment variables and fall back to repo-relative defaults, so
the package runs unmodified after cloning:

| Variable | Meaning | Default |
|---|---|---|
| `PAPER2_PROC_DIR` | processed data packages (`08A_main_regression_package.xlsx` etc.) | `<repo>/data` |
| `PAPER2_RAW_DIR` | raw source data | `<repo>/data/raw` |
| `PAPER2_LEGACY_CODE` | the original numbered pipeline, where a script reuses one of its functions | `<repo>/code` |
| `PAPER2_OUT_DIR` | where analysis outputs are written | `<script dir>/_out` |

Set them only if your data lives elsewhere, e.g.

```bash
export PAPER2_PROC_DIR=/path/to/processed_data
python code/analysis/run_full_battery.py
```
