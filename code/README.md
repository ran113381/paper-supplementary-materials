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
