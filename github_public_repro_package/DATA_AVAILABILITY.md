# Data Availability

## Publicly Included Here

- `data/public/04_genai_dictionary.xlsx`
- frozen manuscript tables in `output/tables/`
- frozen manuscript figures in `output/figures/`
- public attachment files in `paper/attachments/`

## Not Publicly Included Here

The following materials are intentionally excluded from this GitHub package:

- licensed CSMAR raw tables
- licensed CNRDS raw tables
- full MD&A text archives
- firm-level processed panels
- firm-level regression workbooks
- internal manuscript candidates used during package reconstruction

## Why They Are Excluded

- database license restrictions
- manuscript-stage sensitivity
- redistribution risk for firm-level source extracts
- the current estimation chain still requires additional audit before public release

## Consequence

This public package supports the manuscript and its final exhibits, but it does not by itself enable a full raw-to-final rerun.

## If You Need a Fuller Reproduction Environment

You would need all of the following locally:

1. licensed access to the underlying CSMAR and CNRDS data
2. the private raw-data layer
3. the private processed firm-level workbooks
4. additional audit and cleanup of the legacy code chain before rerunning models
