"""
v2025/05_concat_and_rebuild.py
================================
Concatenate the FY2025 slice (built in v2025/01-04, using paper2's own
formulas/dictionaries pointed at fresh raw files) onto the UNCHANGED 2015-2024
slice (read verbatim from paper2's existing processed_data files), then
rebuild the main/strict sample filters, the turnover-ratio patch (matching
12_complete_missing_legacy_vars.py), and the winsorized regression packages --
following 06_restructure_reviewer_friendly_pipeline.py's exact rules, reused
via module import wherever possible.

WINSORIZATION DESIGN DECISION (read before touching this file)
----------------------------------------------------------------
The original pipeline winsorizes each WINSOR_VARS column at the 1%/99%
quantiles of ITS OWN sample (main or strict), computed at the time 08A/08B
were built from the (then complete) 2015-2024 data. If we recompute 1%/99%
quantiles on the POOLED 2015-2025 sample and clip everything to the new
bounds, the 2015-2024 rows' winsorized values could shift slightly (new 2025
extremes can move the quantile cutoffs), which would silently change
already-published numbers -- exactly what the brief prohibits.

Instead we FREEZE the winsorization bounds at their original 2015-2024 values
(recovered directly from the existing 08A/08B "_raw" sheets, which are the
authoritative pre-winsorization 2015-2024 values) and apply those SAME fixed
bounds via .clip() to the pooled 2015-2025 raw data. This has two properties:
1. For 2015-2024 rows: clipping raw values with the exact bounds that were
   originally derived FROM those same raw values reproduces the original
   winsorized values exactly (clip is pointwise; unaffected by later
   additions to the sample). This is what makes the Step-6 gate check pass.
2. For 2025 rows: new observations are clipped to the historically-observed
   1%/99% envelope, a standard and defensible approach for incrementally
   extending an already-published winsorized panel.
This is a deliberate, documented design choice -- not a bug. It is flagged
again in the final report.
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
OLD_PROC_DIR = Path(os.environ.get("PAPER2_PROC_DIR", _REPO / "data"))
OLD_RAW_DIR = Path(os.environ.get("PAPER2_RAW_DIR", _REPO / "data" / "raw"))
OUT_DIR = Path(os.environ.get("PAPER2_PROC_DIR", _REPO / "data")) / "v2025"

PAIRS_2025 = OUT_DIR / "01_dyad_pairs_2025_only.xlsx"
VAR_BASE_2025 = OUT_DIR / "03_variable_base_2025.xlsx"
GENAI_2025 = OUT_DIR / "04_genai_panel_2025.xlsx"

OUT_PAIRS = OUT_DIR / "01_supplier_dyad_pairs_2025.xlsx"
OUT_FIN = OUT_DIR / "02_bilateral_financial_panel_2025.xlsx"
OUT_VARBASE = OUT_DIR / "03_financial_variable_base_2025.xlsx"
OUT_GENAI_PANEL = OUT_DIR / "05_genai_firm_year_panel_2025.xlsx"
OUT_ANALYSIS_BASE = OUT_DIR / "06_analysis_base_panel_2025.xlsx"
OUT_MAIN = OUT_DIR / "07A_main_analysis_sample_2025.xlsx"
OUT_STRICT = OUT_DIR / "07B_strict_robustness_sample_2025.xlsx"
OUT_MAIN_PACK = OUT_DIR / "08A_main_regression_package_2025.xlsx"
OUT_STRICT_PACK = OUT_DIR / "08B_strict_regression_package_2025.xlsx"
OUT_ADDITION_SUMMARY = OUT_DIR / "09_fy2025_addition_summary.xlsx"

TARGET_YEAR = 2025
TRUNCATION_LEN = 32767


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, OLD_CODE_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def normalize_ids(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "Focal_ID" in out.columns:
        out["Focal_ID"] = out["Focal_ID"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip().str.zfill(6)
    if "Partner_ID" in out.columns:
        out["Partner_ID"] = out["Partner_ID"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip().str.zfill(6)
    if "Year" in out.columns:
        out["Year"] = pd.to_numeric(out["Year"], errors="coerce").astype("Int64")
    return out


# ---------------------------------------------------------------------------
# Step 1: concat 01 (dyad pairs)
# ---------------------------------------------------------------------------
def step1_concat_pairs() -> pd.DataFrame:
    print("[1/8] Concatenating 01_supplier_dyad_pairs (old 2015-2024, unchanged) + new 2025 pairs ...")
    old = pd.read_excel(OLD_PROC_DIR / "01_supplier_dyad_pairs.xlsx", dtype={"Focal_ID": str, "Partner_ID": str})
    new = pd.read_excel(PAIRS_2025, dtype={"Focal_ID": str, "Partner_ID": str})
    combined = pd.concat([old, new], ignore_index=True, sort=False)
    combined = normalize_ids(combined)
    combined.to_excel(OUT_PAIRS, index=False)
    print(f"  old rows: {len(old):,}  new 2025 rows: {len(new):,}  combined: {len(combined):,}")
    return combined


# ---------------------------------------------------------------------------
# Step 2/3: concat 02 (bilateral financial panel, pre-derived) and
# 03 (financial variable base, with derived vars) -- our v2025/03 output
# already carries the full derived-variable superset, so we reuse it for
# both, restricting column sets to match the corresponding old file's schema
# (pandas concat aligns by column NAME; any column present in one file but
# not the other is filled with NaN, which is safe and transparent).
# ---------------------------------------------------------------------------
def step2_3_concat_financials() -> tuple[pd.DataFrame, pd.DataFrame]:
    print("[2/8] Concatenating 02_bilateral_financial_panel + 03_financial_variable_base ...")
    old_02 = pd.read_excel(OLD_PROC_DIR / "02_bilateral_financial_panel.xlsx", dtype={"Focal_ID": str, "Partner_ID": str})
    old_03 = pd.read_excel(OLD_PROC_DIR / "03_financial_variable_base.xlsx", dtype={"Focal_ID": str, "Partner_ID": str})
    new_full = pd.read_excel(VAR_BASE_2025, dtype={"Focal_ID": str, "Partner_ID": str})

    new_02 = new_full[[c for c in old_02.columns if c in new_full.columns]].copy()
    combined_02 = pd.concat([old_02, new_02], ignore_index=True, sort=False)
    combined_02 = normalize_ids(combined_02)
    combined_02 = combined_02.drop_duplicates(subset=["Focal_ID", "Partner_ID", "Year"])
    combined_02.to_excel(OUT_FIN, index=False)

    new_03 = new_full[[c for c in old_03.columns if c in new_full.columns]].copy()
    combined_03 = pd.concat([old_03, new_03], ignore_index=True, sort=False)
    combined_03 = normalize_ids(combined_03)
    combined_03 = combined_03.drop_duplicates(subset=["Focal_ID", "Partner_ID", "Year"])
    combined_03.to_excel(OUT_VARBASE, index=False)

    print(f"  02: old {len(old_02):,} + new {len(new_02):,} -> combined {len(combined_02):,}")
    print(f"  03: old {len(old_03):,} + new {len(new_03):,} -> combined {len(combined_03):,}")
    return combined_02, combined_03


# ---------------------------------------------------------------------------
# Step 4: concat 05 (GenAI firm-year panel)
# ---------------------------------------------------------------------------
def step4_concat_genai_panel() -> pd.DataFrame:
    print("[4/8] Concatenating 05_genai_firm_year_panel (old) + new 2025 GenAI scores ...")
    old = pd.read_excel(OLD_PROC_DIR / "05_genai_firm_year_panel.xlsx", dtype={"Firm_ID": str})
    new = pd.read_excel(GENAI_2025, dtype={"Firm_ID": str})
    combined = pd.concat([old, new], ignore_index=True, sort=False)
    combined["Firm_ID"] = combined["Firm_ID"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip().str.zfill(6)
    combined["Year"] = pd.to_numeric(combined["Year"], errors="coerce").astype("Int64")
    # Populate Is_Truncated uniformly (old rows never had this flag computed; it
    # is fully derivable post-hoc from MDA_CharCount alone).
    combined["Is_Truncated"] = (pd.to_numeric(combined["MDA_CharCount"], errors="coerce") == TRUNCATION_LEN).astype(int)
    combined = combined.drop_duplicates(subset=["Firm_ID", "Year"])
    combined.to_excel(OUT_GENAI_PANEL, index=False)
    print(f"  old rows: {len(old):,}  new 2025 rows: {len(new):,}  combined: {len(combined):,}")
    print(f"  truncated-text rows in combined panel: {int(combined['Is_Truncated'].sum()):,}")
    return combined


# ---------------------------------------------------------------------------
# Step 5: rebuild 06 (analysis base panel = 03 + GenAI merge), exact reuse of
# 06's merge_genai()
# ---------------------------------------------------------------------------
def step5_rebuild_analysis_base(restruct_mod, combined_03: pd.DataFrame, combined_genai: pd.DataFrame) -> pd.DataFrame:
    print("[5/8] Rebuilding 06_analysis_base_panel (03 + GenAI merge, exact reuse of merge_genai()) ...")
    # merge_genai() merges the FULL renamed genai frame (not a column subset), so
    # our extra Is_Truncated column (not part of the original genai panel schema)
    # would otherwise leak through as a colliding Is_Truncated_x/_y pair on both
    # the focal and partner merges. Drop it here -- it already lives in the
    # standalone 05_genai_firm_year_panel_2025.xlsx / 04_mda_truncation_flags_2025.xlsx
    # audit files, so nothing is lost, and this keeps 06/07A/07B/08A/08B's column
    # schema an exact match to the originals.
    genai_for_merge = combined_genai.drop(columns=["Is_Truncated"], errors="ignore")
    analysis_base = restruct_mod.merge_genai(combined_03, genai_for_merge)
    analysis_base = restruct_mod.dedupe_dyad_year(analysis_base)
    analysis_base.to_excel(OUT_ANALYSIS_BASE, index=False)
    print(f"  combined analysis base rows: {len(analysis_base):,}")
    return analysis_base


# ---------------------------------------------------------------------------
# Step 6: rebuild 07A/07B main & strict samples (exact MAIN_REQUIRED /
# STRICT_FOCAL / STRICT_PARTNER masks from 06)
# ---------------------------------------------------------------------------
def step6_rebuild_main_strict(restruct_mod, analysis_base: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    print("[6/8] Rebuilding 07A (main) / 07B (strict) samples with the original required-field masks ...")
    main_df = analysis_base.loc[analysis_base[restruct_mod.MAIN_REQUIRED].notna().all(axis=1)].copy()
    strict_df = analysis_base.loc[
        analysis_base[restruct_mod.STRICT_FOCAL].notna().all(axis=1)
        & analysis_base[restruct_mod.STRICT_PARTNER].notna().all(axis=1)
    ].copy()
    main_df = restruct_mod.dedupe_dyad_year(main_df)
    strict_df = restruct_mod.dedupe_dyad_year(strict_df)

    n_main_2025 = (pd.to_numeric(main_df["Year"], errors="coerce") == TARGET_YEAR).sum()
    n_strict_2025 = (pd.to_numeric(strict_df["Year"], errors="coerce") == TARGET_YEAR).sum()
    print(f"  main sample: {len(main_df):,} rows total ({n_main_2025} are 2025)")
    print(f"  strict sample: {len(strict_df):,} rows total ({n_strict_2025} are 2025)")

    main_df.to_excel(OUT_MAIN, index=False)
    strict_df.to_excel(OUT_STRICT, index=False)
    return main_df, strict_df


# ---------------------------------------------------------------------------
# Step 7: turnover-ratio patch (12_complete_missing_legacy_vars.py's target
# variables) for the NEW 2025 rows only; 2015-2024 rows already carry these
# (12 has already been applied to the current on-disk 07A/07B/08A/08B).
# ---------------------------------------------------------------------------
def build_2025_turnover_vars(strict_mod, main_df: pd.DataFrame, strict_df: pd.DataFrame) -> pd.DataFrame:
    print("[7/8] Computing FY2025 turnover ratios (Focal/Partner_SalesVol_Rec, Focal/Partner_InvTurn) ...")
    needed_ids = pd.concat(
        [
            main_df.loc[main_df["Year"] == TARGET_YEAR, ["Focal_ID", "Partner_ID"]],
            strict_df.loc[strict_df["Year"] == TARGET_YEAR, ["Focal_ID", "Partner_ID"]],
        ]
    )
    firm_codes = set(needed_ids["Focal_ID"]) | set(needed_ids["Partner_ID"])
    needed_pairs_2025 = {(c, TARGET_YEAR) for c in firm_codes}
    needed_pairs_2024 = {(c, TARGET_YEAR - 1) for c in firm_codes}

    # NOTE: paper2's own OLD "Balance Sheet" raw file no longer exists on disk
    # (likely cleaned up after the original 2015-2024 pipeline finished running --
    # confirmed absent from <PROJECT_ROOT>\data\raw_data\ this session).
    # The fresh FY2025 balance sheet download (FS_Combas.xlsx) also carries full
    # historical rows back to 2013 (confirmed this session), so we pull BOTH the
    # 2025 and 2024 (lag input for the turnover average) AR/Inventory values from
    # it in a single pass -- same CSMAR field codes (A001111000/A001123000), just
    # read from the only copy of this table actually available on this machine.
    needed_pairs_both_years = needed_pairs_2025 | needed_pairs_2024
    bs_both = strict_mod.stream_large_firm_year_table(
        Path(r"E:\Supply - SHAP\data\raw_data\base1\downloads\资产负债表070127671(仅供vip使用)\FS_Combas.xlsx"),
        "Stkcd", "Accper", "Typrep", {"A001111000": "AR", "A001123000": "Inventory"},
        needed_pairs_both_years, yuan_cols={"AR", "Inventory"},
    )
    bs_2025 = bs_both[bs_both["year"] == TARGET_YEAR].copy()
    bs_2024 = bs_both[bs_both["year"] == TARGET_YEAR - 1].copy()

    bs_2025 = bs_2025.rename(columns={"AR": "AR_2025", "Inventory": "Inv_2025"}).drop(columns=["year"])
    bs_2024 = bs_2024.rename(columns={"AR": "AR_2024", "Inventory": "Inv_2024"}).drop(columns=["year"])
    turnover_base = bs_2025.merge(bs_2024, on="firm_code", how="left")
    turnover_base["AR_avg"] = np.where(
        turnover_base["AR_2024"].notna(), (turnover_base["AR_2025"] + turnover_base["AR_2024"]) / 2, turnover_base["AR_2025"]
    )
    turnover_base["Inv_avg"] = np.where(
        turnover_base["Inv_2024"].notna(), (turnover_base["Inv_2025"] + turnover_base["Inv_2024"]) / 2, turnover_base["Inv_2025"]
    )

    # Revenue for 2025 comes from the already-built analysis base (Focal_/Partner_Revenue).
    rev_lookup = pd.concat(
        [
            main_df.loc[main_df["Year"] == TARGET_YEAR, ["Focal_ID", "Focal_Revenue"]].rename(columns={"Focal_ID": "firm_code", "Focal_Revenue": "Revenue"}),
            main_df.loc[main_df["Year"] == TARGET_YEAR, ["Partner_ID", "Partner_Revenue"]].rename(columns={"Partner_ID": "firm_code", "Partner_Revenue": "Revenue"}),
        ]
    ).dropna().drop_duplicates("firm_code")

    turnover_base = turnover_base.merge(rev_lookup, on="firm_code", how="left")

    def safe_div(num, den):
        num = pd.to_numeric(num, errors="coerce")
        den = pd.to_numeric(den, errors="coerce")
        out = num / den
        out[(den <= 0) | den.isna()] = np.nan
        return out

    turnover_base["SalesVol_Rec"] = safe_div(turnover_base["Revenue"], turnover_base["AR_avg"])
    turnover_base["InvTurn"] = safe_div(turnover_base["Revenue"], turnover_base["Inv_avg"])
    print(f"  firm codes with 2025 turnover computed: {len(turnover_base):,}")
    return turnover_base[["firm_code", "SalesVol_Rec", "InvTurn"]]


def attach_turnover(df: pd.DataFrame, turnover: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    focal = turnover.rename(columns={"firm_code": "Focal_ID", "SalesVol_Rec": "Focal_SalesVol_Rec", "InvTurn": "Focal_InvTurn"})
    partner = turnover.rename(columns={"firm_code": "Partner_ID", "SalesVol_Rec": "Partner_SalesVol_Rec", "InvTurn": "Partner_InvTurn"})
    is_2025 = out["Year"] == TARGET_YEAR
    out_2025 = out.loc[is_2025].drop(columns=["Focal_SalesVol_Rec", "Focal_InvTurn", "Partner_SalesVol_Rec", "Partner_InvTurn"], errors="ignore")
    out_2025 = out_2025.merge(focal, on="Focal_ID", how="left").merge(partner, on="Partner_ID", how="left")
    out_not2025 = out.loc[~is_2025]
    result = pd.concat([out_not2025, out_2025], ignore_index=True, sort=False)
    return result


# ---------------------------------------------------------------------------
# Step 8: winsorized packages, with FROZEN 2015-2024 bounds (see module docstring)
# ---------------------------------------------------------------------------
WINSOR_VARS = [
    "Focal_Size", "Focal_Lev", "Focal_ROA", "Focal_Age", "Focal_Growth", "Focal_CashFlow",
    "Focal_TobinQ", "Focal_RnD_Ratio", "Focal_AdminExp_Ratio",
    "Partner_Size", "Partner_Lev", "Partner_ROA", "Partner_Age", "Partner_Growth",
    "Partner_CashFlow", "Partner_TobinQ", "Partner_RnD_Ratio", "Partner_AdminExp_Ratio",
    "Rela_Purchase_Ln", "Ln_Distance", "Ln_Dyad_Duration", "Power_Diff",
    "Focal_GenAI_Index", "Focal_GenAI_Index_Overlap", "Partner_GenAI_Index", "Partner_GenAI_Index_Overlap",
]
# Also winsorized by 12_complete_missing_legacy_vars.py's update_package():
WINSOR_VARS_EXTRA = ["Focal_SalesVol_Rec", "Focal_InvTurn", "Partner_SalesVol_Rec", "Partner_InvTurn"]


def get_frozen_bounds(old_pack_path: Path, raw_sheet: str) -> dict[str, tuple[float, float]]:
    old_raw = pd.read_excel(old_pack_path, sheet_name=raw_sheet)
    bounds = {}
    for col in WINSOR_VARS + WINSOR_VARS_EXTRA:
        if col not in old_raw.columns:
            continue
        s = pd.to_numeric(old_raw[col], errors="coerce").dropna()
        if s.empty:
            continue
        bounds[col] = (s.quantile(0.01), s.quantile(0.99))
    return bounds


def apply_frozen_winsor(raw: pd.DataFrame, bounds: dict[str, tuple[float, float]]) -> pd.DataFrame:
    wins = raw.copy()
    for col, (lo, hi) in bounds.items():
        if col in wins.columns:
            wins[col] = pd.to_numeric(wins[col], errors="coerce").astype(float).clip(lower=lo, upper=hi)
    return wins


def coverage(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for c in cols:
        rows.append({"variable": c, "non_missing": int(df[c].notna().sum()), "missing": int(df[c].isna().sum()), "missing_pct": round(df[c].isna().mean() * 100, 2)})
    return pd.DataFrame(rows)


def descriptives(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for c in cols:
        s = pd.to_numeric(df[c], errors="coerce")
        rows.append({"variable": c, "n": int(s.notna().sum()), "missing_pct": round(s.isna().mean() * 100, 2), "mean": s.mean(), "median": s.median(), "std": s.std(), "min": s.min(), "p25": s.quantile(0.25), "p75": s.quantile(0.75), "max": s.max()})
    return pd.DataFrame(rows)


def build_package(raw: pd.DataFrame, bounds: dict, sample_name: str, formulas: pd.DataFrame, winsor_rules: pd.DataFrame, out_path: Path) -> None:
    wins = apply_frozen_winsor(raw, bounds)
    key_vars = [
        "Focal_Size", "Focal_Lev", "Focal_ROA", "Focal_Age", "Focal_Growth", "Focal_CashFlow", "Focal_SoE", "Focal_HHI",
        "Partner_Size", "Partner_Lev", "Partner_ROA", "Rela_Purchase_Ln", "Ln_Dyad_Duration", "Power_Diff", "Geo_Distance", "Ln_Distance",
        "Focal_RnD_Ratio", "Partner_RnD_Ratio", "Focal_AdminExp_Ratio", "Partner_AdminExp_Ratio",
        "Focal_GenAI_Index", "Focal_GenAI_Index_Overlap", "Partner_GenAI_Index", "Partner_GenAI_Index_Overlap",
    ]
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        formulas.to_excel(writer, sheet_name="formulas", index=False)
        winsor_rules.to_excel(writer, sheet_name="winsor_rules", index=False)
        raw.to_excel(writer, sheet_name=f"{sample_name}_raw", index=False)
        wins.to_excel(writer, sheet_name=f"{sample_name}_winsorized", index=False)
        coverage(raw, key_vars).to_excel(writer, sheet_name=f"{sample_name}_coverage", index=False)
        descriptives(raw, key_vars).to_excel(writer, sheet_name=f"{sample_name}_descriptives", index=False)


def main() -> None:
    strict_mod = load_module("strictmod_orig", "01_build_supplier_pairs_and_financial_panel.py")
    restruct_mod = load_module("restructmod_orig", "06_restructure_reviewer_friendly_pipeline.py")

    step1_concat_pairs()
    combined_02, combined_03 = step2_3_concat_financials()
    combined_genai = step4_concat_genai_panel()
    analysis_base = step5_rebuild_analysis_base(restruct_mod, combined_03, combined_genai)
    main_df, strict_df = step6_rebuild_main_strict(restruct_mod, analysis_base)

    turnover_2025 = build_2025_turnover_vars(strict_mod, main_df, strict_df)
    main_df = attach_turnover(main_df, turnover_2025)
    strict_df = attach_turnover(strict_df, turnover_2025)
    main_df.to_excel(OUT_MAIN, index=False)
    strict_df.to_excel(OUT_STRICT, index=False)

    print("[8/8] Building 08A/08B winsorized regression packages (frozen 2015-2024 bounds) ...")
    old_main_pack = OLD_PROC_DIR / "08A_main_regression_package.xlsx"
    old_strict_pack = OLD_PROC_DIR / "08B_strict_regression_package.xlsx"
    formulas = pd.read_excel(old_main_pack, sheet_name="formulas")
    winsor_rules_main = pd.read_excel(old_main_pack, sheet_name="winsor_rules")
    winsor_rules_strict = pd.read_excel(old_strict_pack, sheet_name="winsor_rules")

    main_bounds = get_frozen_bounds(old_main_pack, "main_raw")
    strict_bounds = get_frozen_bounds(old_strict_pack, "strict_raw")

    build_package(main_df, main_bounds, "main", formulas, winsor_rules_main, OUT_MAIN_PACK)
    build_package(strict_df, strict_bounds, "strict", formulas, winsor_rules_strict, OUT_STRICT_PACK)

    print()
    print("=" * 70)
    print("v2025 pipeline outputs written:")
    for p in [OUT_PAIRS, OUT_FIN, OUT_VARBASE, OUT_GENAI_PANEL, OUT_ANALYSIS_BASE, OUT_MAIN, OUT_STRICT, OUT_MAIN_PACK, OUT_STRICT_PACK]:
        print(" ", p)


if __name__ == "__main__":
    main()
