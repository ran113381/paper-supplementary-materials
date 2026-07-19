# Public Reproduction Package

## Manuscript

English title (major revision, 2026-07):

`GenAI Disclosure and Short-Term Firm Performance in Buyer–Supplier Dyads: Evidence from Text-Mined MD&A Signals`

(Original submission title, superseded: "Short-Term Performance Consequences
of Generative AI Adoption: Moderating Effects of R&D Intensity and
Supply-Chain Power Pressure" / 生成式人工智能采用的短期绩效后果：研发强度与供应链权力压力的调节作用.
The retitling reflects the revision's disclosure-based, association-level
framing; exhibit numbering follows the revised manuscript — see
`docs/EXHIBIT_MAP.md`, synchronized 2026-07-17 to 14 tables + 14 figures.)

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
