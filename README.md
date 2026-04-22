# Public Reproduction Package

## Manuscript

Chinese title:

`生成式人工智能采用的短期绩效后果：研发强度与供应链权力压力的调节作用`

English title:

`Short-Term Performance Consequences of Generative AI Adoption: Moderating Effects of R&D Intensity and Supply-Chain Power Pressure`

## Package Type

This is a manuscript-supporting public package prepared for GitHub.

It is not a full raw-data redistribution archive and it is not yet a one-click raw-to-final rerun package.

What this package does provide:

- frozen manuscript-facing tables exported to CSV
- frozen manuscript-facing figures exported to PNG
- the public GenAI dictionary workbook
- the dictionary attachment files used by the manuscript
- documentation on data availability, package status, and output mapping
- a small utility script for extracting frozen tables and figures from the authority `.docx`

What this package does not provide:

- licensed CSMAR or CNRDS raw data
- full MD&A text archives
- firm-level processed workbooks with redistribution risk
- a validated end-to-end estimation pipeline

## Repository Layout

- `code/`
  - utility scripts only
- `data/public/`
  - public, non-licensed supporting files
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
