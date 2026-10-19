# Public Reproduction Package

## Manuscript

English title (major revision, 2026-07):

`GenAI Disclosure and Short-Term Firm Performance in Buyer–Supplier Dyads: Evidence from Text-Mined MD&A Signals`

(Original submission title, superseded: "Short-Term Performance Consequences
of Generative AI Adoption: Moderating Effects of R&D Intensity and
Supply-Chain Power Pressure" / 生成式人工智能采用的短期绩效后果：研发强度与供应链权力压力的调节作用.
The retitling reflects the revision's disclosure-based, association-level
framing; exhibit numbering follows the revised manuscript — see
`docs/EXHIBIT_MAP.md`, synchronized 2026-10-19 to the third-round (R3) manuscript: 15 tables + 14 figures.)

## Package Type

This is a manuscript-supporting public package prepared for GitHub.

It is not a full raw-data redistribution archive: the licensed raw-data layer
is excluded, so it is not a one-click raw-to-final rerun package. It does,
however, include the estimation and diagnostic code and the measurement
validation evidence.

What this package does provide:

- frozen manuscript-facing tables exported to CSV
- frozen manuscript-facing figures exported to PNG
- the public GenAI dictionary workbook
- the dictionary attachment files used by the manuscript
- the estimation, panel-construction, and diagnostic scripts behind the
  regression results (`code/analysis/`)
- the Table 3C SOTA-validation evidence package: human-adjudicated gold
  standard, frozen row-level predictions, GPT-5.5 / Claude label archives,
  and a SHA-256 manifest (`data/`)
- documentation on data availability, package status, and output mapping
- a small utility script for extracting frozen tables and figures from the authority `.docx`

What this package does not provide:

- licensed CSMAR or CNRDS raw data
- full MD&A text archives
- firm-level processed workbooks with redistribution risk

Because the licensed inputs are excluded, the included estimation code cannot
be rerun from this repository alone; it documents the exact specifications and
diagnostics, and runs for users who hold their own licensed access after local
path adjustment.

## Repository Layout

- `code/`
  - `extract_docx_exhibits.py`: packaging utility for frozen exhibits
  - `analysis/`: estimation, FY2025 panel-extension, and diagnostic scripts
    (see `code/analysis/README.md`; licensed inputs not included)
  - `05_build_genai_measurement.py`: the measurement build script, as run
  - `09_run_did_and_placebo.py`: the event-study and 500-draw placebo
    permutation script behind Figures 8-9 (Section 4.3), as run
- `data/`
  - Table 3C SOTA-validation evidence: gold-standard workbook, sampling
    frame, frozen predictions, published Table 3C outputs, GPT-5.5 / Claude
    label archives, early pilot-validation evidence, evidence-package
    scripts, and `MANIFEST.sha256`
  - `README_label_archives.md`: series-by-series coverage, verification, and
    known-missing-items documentation
- `data/public/`
  - public, non-licensed supporting files (GenAI dictionary workbook)
- `data/restricted_placeholder/`
  - intentionally empty placeholder for non-public data layers
- `output/tables/`
  - frozen table exports from the authority manuscript
- `output/figures/`
  - frozen figure exports from the authority manuscript
- `paper/attachments/`
  - public manuscript-supporting attachment files
- `docs/`
  - package notes and exhibit map

Added 2026-10-18 (third-round revision):

- `CORRECTION_NOTE.md`: correction of the gold-standard adjudication record,
  including the withdrawn attribution column of the adjudication workbook
- `data/genai_gold_standard_adjudication_workbook_corrected.xlsx`: corrected copy
  of the adjudication workbook (the original is kept unchanged)
- `code/draft_rule_check/`: check scripts and logs for the earlier adjudication
  drafts
- `code/analysis/14_callaway_santanna.py`, `14b_csdid_crosscheck.py`,
  `15_event_study_fy2025_raw_vs_clean.py`, `16_static_did_cohort_post.py`
  (with `j33_common.py`): Callaway–Sant'Anna estimates, fiscal-2025 event study
  on raw and clean texts, and the static DiD with cohort-specific Post
- `output/logs/`: the logs of these scripts
- `third_coder/`: blind third-coder re-adjudication — deposited protocol,
  codebook, scripts and selection manifest; `release/` (keys, seeds, selection
  rules, labels, the returned sheets and run records, `HASHES.md`); the wrapper
  and second script with their logs (`scripts/`, `logs/`); and
  `DEPARTURE_RECORD.md`, the complete record of departures from the protocol

Note (2026-07-15): file names inside `data/` were repaired in this working
tree — the initial upload had names and contents shuffled across files. See
`CHANGES_PROPOSED.md` for the complete old-to-new mapping and
`data/README_label_archives.md` for how each file's identity was verified.

## Quick Start

1. Read `DATA_AVAILABILITY.md`.
2. Read `REPRO_STATUS.md`.
3. Use `docs/EXHIBIT_MAP.md` to connect manuscript exhibits to exported files.
4. If you already have the authority manuscript `.docx`, you may re-extract frozen exhibits with:

```powershell
python code/extract_docx_exhibits.py --docx "PATH_TO_MANUSCRIPT.docx"
```

## Interpretation Rule

The files in `output/` are frozen exports from the authority manuscript.

They are provided to support review, verification, and package transparency.

They should not be described as rerun-generated outputs from redistributed raw data.
