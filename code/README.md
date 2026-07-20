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
  sample used in Tables 9-14, and the companion TWFE-DID in the same script runs
  on a further-restricted late-treated/never-treated subsample -- the three N's
  are different by design.

  The stored draws are released as `data/placebo_500_permutations_verified.json`;
  re-running this script with the same seed reproduces them elementwise. The
  licensed CSMAR/CNRDS-derived panels it reads are not redistributed (see
  DATA_AVAILABILITY.md).
