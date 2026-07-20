"""
v2025/04_score_2025_genai.py
==============================
Score FY2025 GenAI disclosure intensity using paper2's OWN dictionary and
scoring method, reused directly (via module import) from
<PROJECT_ROOT>\\code\\05_build_genai_measurement.py:
FORMULA_TEXT, extract_terms(), classify_term(), build_pattern(),
compute_genai_metrics() (longest-match, non-overlapping counting) -- NOT
reimplemented, and NOT reusing any other project's precomputed GenAI index.

Text source: only the 3rd MD&A batch file
(管理层信息披露情感分析085620263\\BDT_MDAEmotAnal.xlsx) actually contains
2025 rows (confirmed this session -- batches 1 and 2 cover 2013-2015 and
2016-2020 only; batch 3 covers 2021-2025). Filtered to Enddate month==12
(annual report MD&A only, matching the original's month==12 filter).

Column-layout deviation (deliberate, documented): the ORIGINAL
read_csmar_mda() in 05_build_genai_measurement.py extracts the text column by
POSITION (df.columns[:4]), because the old crmas_mda_ascii.xlsx source
happens to have the MD&A text as its 4th column. The FRESH
BDT_MDAEmotAnal.xlsx file has a DIFFERENT column layout (Symbol, ShortName,
Enddate, IndustryCode, IndustryName, IndustryCode1, IndustryName1,
ManaDiscAnal, ...) -- the text is its 8th column, not 4th. Blindly reusing
positional extraction would silently score the wrong column (IndustryCode
text) as "MD&A text". We therefore extract by COLUMN NAME
(Symbol/Enddate/ManaDiscAnal) for the fresh file instead -- this preserves
the ORIGINAL INTENT (correctly locate Symbol/Date/MD&A-text) rather than the
literal mechanism, which does not transfer across the two files' layouts.

Truncation caveat (explicit, not silently ignored): CSMAR's ManaDiscAnal
field is capped at Excel's single-cell limit of 32,767 characters. Any row
whose text length is exactly 32767 is flagged Focal/Partner_MDA_Truncated=1
in the output; GenAI counts for those rows are still computed (on the
truncated text) but should be read as a lower bound, not a complete count.
"""
from __future__ import annotations

import os
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[2]

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OLD_CODE_DIR = Path(os.environ.get("PAPER2_LEGACY_CODE", _REPO / "code"))
NEW_RAW_ROOT = Path(r"E:\Supply - SHAP\data\raw_data\base1\downloads")
OUT_DIR = Path(os.environ.get("PAPER2_PROC_DIR", _REPO / "data")) / "v2025"

PAIRS_2025 = OUT_DIR / "01_dyad_pairs_2025_only.xlsx"
MDA_2025_FILE = NEW_RAW_ROOT / r"管理层信息披露情感分析085620263\BDT_MDAEmotAnal.xlsx"

OUT_FILE = OUT_DIR / "04_genai_panel_2025.xlsx"
TRUNCATION_FLAG_FILE = OUT_DIR / "04_mda_truncation_flags_2025.xlsx"

TARGET_YEAR = 2025
TRUNCATION_LEN = 32767


def load_genai_module():
    spec = importlib.util.spec_from_file_location("genaimod_orig", OLD_CODE_DIR / "05_build_genai_measurement.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_target_keys() -> set[tuple[str, int]]:
    pairs = pd.read_excel(PAIRS_2025, dtype={"Focal_ID": str, "Partner_ID": str})
    codes = pd.concat([pairs["Focal_ID"], pairs["Partner_ID"]]).dropna().unique()
    return {(c, TARGET_YEAR) for c in codes}


def read_mda_2025_by_name(genai_mod, target_keys: set[tuple[str, int]]) -> pd.DataFrame:
    """Column-NAME based extraction (deliberate deviation from the original's
    column-POSITION based read_csmar_mda -- see module docstring)."""
    print(f"Reading {MDA_2025_FILE} (batch 085620263, the only batch with 2025 rows) ...")
    df = pd.read_excel(
        MDA_2025_FILE, header=0, skiprows=[1, 2],
        usecols=["Symbol", "Enddate", "ManaDiscAnal"], dtype={"Symbol": str},
    )
    print(f"  raw rows read: {len(df):,}")
    df["Firm_ID"] = genai_mod.normalize_code(df["Symbol"])
    dt = pd.to_datetime(df["Enddate"], errors="coerce")
    df["Year"] = dt.dt.year.astype("Int64")
    df["Month"] = dt.dt.month.astype("Int64")
    df["MDA_Text"] = df["ManaDiscAnal"].fillna("").astype(str)

    out = df[(df["Month"] == 12) & (df["Year"] == TARGET_YEAR)][["Firm_ID", "Year", "MDA_Text"]]
    out = out.drop_duplicates(subset=["Firm_ID", "Year"])
    print(f"  rows with Year=={TARGET_YEAR} & Month==12: {len(out):,}")

    out["Text_Length"] = out["MDA_Text"].str.len()
    out["Is_Truncated"] = (out["Text_Length"] == TRUNCATION_LEN).astype(int)
    n_trunc = out["Is_Truncated"].sum()
    print(f"  rows hitting the {TRUNCATION_LEN}-char Excel cell cap (truncated): {n_trunc:,}")

    out = out[out.apply(lambda r: (r["Firm_ID"], int(r["Year"])) in target_keys, axis=1)].copy()
    print(f"  rows matching our needed 2025 firm-year pool: {len(out):,}")
    out["Text_Source"] = "CSMAR_MDA_2025_batch085620263"
    return out


def main() -> None:
    genai_mod = load_genai_module()
    target_keys = build_target_keys()
    print(f"Target 2025 (Firm_ID, Year) keys needed: {len(target_keys):,}")

    panel = read_mda_2025_by_name(genai_mod, target_keys)

    missing_text = target_keys - set(panel[["Firm_ID", "Year"]].itertuples(index=False, name=None))
    print(f"Firm-years in our 2025 dyad pool with NO MD&A text found: {len(missing_text):,}")
    if missing_text:
        print("  sample missing:", list(missing_text)[:15])

    print("Building dictionary and scoring GenAI intensity (exact reuse of 05's FORMULA_TEXT logic) ...")
    dict_df = genai_mod.dictionary_df()
    terms_upper = dict_df["term_upper"].tolist()
    pattern = genai_mod.build_pattern(terms_upper)

    metrics = [genai_mod.compute_genai_metrics(text, terms_upper, pattern) for text in panel["MDA_Text"].fillna("").astype(str)]
    panel["GenAI_Freq_Clean"] = [m[0] for m in metrics]
    panel["GenAI_Freq_Overlap"] = [m[1] for m in metrics]
    panel["GenAI_Breadth"] = [m[2] for m in metrics]
    panel["GenAI_Index"] = [m[3] for m in metrics]
    panel["GenAI_Index_Overlap"] = np.log1p(panel["GenAI_Freq_Overlap"])
    panel["GenAI_Dummy"] = (panel["GenAI_Freq_Clean"] > 0).astype(int)
    panel["MDA_CharCount"] = panel["MDA_Text"].astype(str).str.len()

    out_cols = [
        "Firm_ID", "Year", "Text_Source", "MDA_CharCount", "Is_Truncated",
        "GenAI_Freq_Clean", "GenAI_Freq_Overlap", "GenAI_Index", "GenAI_Index_Overlap",
        "GenAI_Dummy", "GenAI_Breadth",
    ]
    out = panel[out_cols].drop_duplicates(subset=["Firm_ID", "Year"])
    out.to_excel(OUT_FILE, index=False)

    trunc_detail = panel.loc[panel["Is_Truncated"] == 1, ["Firm_ID", "Year", "Text_Length", "GenAI_Freq_Clean"]]
    trunc_detail.to_excel(TRUNCATION_FLAG_FILE, index=False)

    print()
    print("=" * 60)
    print(f"2025 GenAI panel written        : {OUT_FILE}")
    print(f"2025 MDA truncation flags written: {TRUNCATION_FLAG_FILE}")
    print(f"Firm-years scored: {len(out):,}")
    print(f"Firm-years with GenAI_Dummy==1 (any GenAI mention): {int(out['GenAI_Dummy'].sum()):,}  ({out['GenAI_Dummy'].mean()*100:.1f}%)")
    print(f"Truncated text rows among scored firm-years: {int(out['Is_Truncated'].sum()):,}")


if __name__ == "__main__":
    main()
