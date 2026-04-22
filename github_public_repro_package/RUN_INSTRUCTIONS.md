# Run Instructions

## Scope

This package supports two practical actions:

1. review the frozen manuscript exhibits already exported into `output/`
2. re-extract those frozen exhibits from the authority manuscript `.docx`

It does not currently rerun the statistical models from raw licensed data.

## Environment

Install the small dependency set:

```powershell
python -m pip install -r requirements.txt
```

## Review the Included Outputs

- tables: `output/tables/`
- figures: `output/figures/`
- exhibit mapping: `docs/EXHIBIT_MAP.md`

## Re-Extract Frozen Exhibits From the Authority Manuscript

If you have the authority manuscript `.docx`, run:

```powershell
python code/extract_docx_exhibits.py --docx "PATH_TO_MANUSCRIPT.docx"
```

Optional custom destinations:

```powershell
python code/extract_docx_exhibits.py --docx "PATH_TO_MANUSCRIPT.docx" --table-dir "output/tables" --figure-dir "output/figures"
```

## Important Boundary

The extraction script only exports embedded tables and figures from a manuscript file.

It does not estimate regressions, rebuild samples, or regenerate figures from raw data.
