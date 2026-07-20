"""
v2025/03_build_2025_variable_base.py
======================================
Merge the FY2025 firm-year panel (v2025/02) onto the FY2025 dyad pairs
(v2025/01) and construct all derived financial/relationship variables using
the EXACT SAME formulas as
<PROJECT_ROOT>\\code\\06_restructure_reviewer_friendly_pipeline.py's
construct_variable_base() (reused directly via module import, not reimplemented).

Inception_Year / Dyad_Duration for 2025 dyads are computed against the FULL
combined history (old 2015-2024 pairs + new 2025 pairs), so continuing
relationships correctly inherit their true historical inception year rather
than being (incorrectly) treated as brand-new in 2025.

Focal_Growth / Partner_Growth need revenue at Year-1 (2024). Preferred source:
paper2's own already-processed 2015-2024 data (unchanged). Fallback (firms
absent from that history): a fresh 2024 revenue pull from the same FY2025
income-statement file (which also carries historical rows), using the
identical B001100000 field code.

Output: <PROJECT_ROOT>\\data\\processed_data\\v2025\\03_variable_base_2025.xlsx
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
NEW_RAW_ROOT = Path(r"E:\Supply - SHAP\data\raw_data\base1\downloads")
OUT_DIR = Path(os.environ.get("PAPER2_PROC_DIR", _REPO / "data")) / "v2025"

PAIRS_2025 = OUT_DIR / "01_dyad_pairs_2025_only.xlsx"
FIRM_PANEL_2025 = OUT_DIR / "02_firm_year_panel_2025.xlsx"
OUT_FILE = OUT_DIR / "03_variable_base_2025.xlsx"

INCOME_STMT_NEW = NEW_RAW_ROOT / r"利润表081207684(仅供vip使用)\FS_Comins.xlsx"
OLD_PAIRS_FILE = OLD_PROC_DIR / "01_supplier_dyad_pairs.xlsx"
OLD_VAR_BASE_FILE = OLD_PROC_DIR / "03_financial_variable_base.xlsx"

TARGET_YEAR = 2025


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, OLD_CODE_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_financial_merged_2025(pairs: pd.DataFrame, firm_panel: pd.DataFrame) -> pd.DataFrame:
    """Replicates 01_build_supplier_pairs_and_financial_panel.py's
    build_financial_merged() merge logic (Focal_/Partner_ prefix join)."""
    out = pairs.copy()
    out["_yr"] = out["Year"].astype("Int64")
    focal_fin = firm_panel.add_prefix("Focal_").rename(columns={"Focal_firm_code": "Focal_ID", "Focal_year": "_yr"})
    partner_fin = firm_panel.add_prefix("Partner_").rename(columns={"Partner_firm_code": "Partner_ID", "Partner_year": "_yr"})
    out = out.merge(focal_fin, on=["Focal_ID", "_yr"], how="left")
    out = out.merge(partner_fin, on=["Partner_ID", "_yr"], how="left")
    out = out.drop(columns=["_yr"], errors="ignore")
    return out


def recompute_inception_year(pairs_2025: pd.DataFrame) -> pd.DataFrame:
    """Compute Inception_Year / Dyad_Duration for 2025 dyads against the FULL
    combined history (old pairs + new 2025 pairs), matching the original
    groupby(["Focal_ID","Partner_ID"])["Year"].transform("min") logic exactly."""
    old_pairs = pd.read_excel(OLD_PAIRS_FILE, dtype={"Focal_ID": str, "Partner_ID": str})
    old_keys = old_pairs[["Focal_ID", "Partner_ID", "Year"]].copy()
    old_keys["Year"] = pd.to_numeric(old_keys["Year"], errors="coerce")

    new_keys = pairs_2025[["Focal_ID", "Partner_ID", "Year"]].copy()
    combined = pd.concat([old_keys, new_keys], ignore_index=True)
    inception = combined.groupby(["Focal_ID", "Partner_ID"])["Year"].transform("min")
    combined["Inception_Year"] = inception

    lookup = combined.drop_duplicates(subset=["Focal_ID", "Partner_ID", "Year"]).set_index(["Focal_ID", "Partner_ID", "Year"])["Inception_Year"]

    out = pairs_2025.copy()
    out["Inception_Year"] = out.apply(lambda r: lookup.get((r["Focal_ID"], r["Partner_ID"], r["Year"])), axis=1)
    out["Dyad_Duration"] = out["Year"] - out["Inception_Year"]
    n_continuing = (out["Inception_Year"] < TARGET_YEAR).sum()
    n_brand_new = (out["Inception_Year"] == TARGET_YEAR).sum()
    print(f"  2025 dyads that are continuations of pre-existing relationships: {n_continuing}")
    print(f"  2025 dyads that are brand-new relationships (Inception_Year==2025): {n_brand_new}")
    return out


def build_2024_revenue_lookup(strict, needed_codes: set[str]) -> pd.DataFrame:
    """Preferred: pull 2024 revenue from paper2's own already-processed history
    (unchanged). Fallback: fresh pull from the FY2025 income-statement file's
    historical 2024 rows (same B001100000 code) for firms absent from history."""
    hist = pd.read_excel(
        OLD_VAR_BASE_FILE, dtype={"Focal_ID": str, "Partner_ID": str},
        usecols=["Focal_ID", "Partner_ID", "Year", "Focal_Revenue", "Partner_Revenue"],
    )
    hist2024 = hist[pd.to_numeric(hist["Year"], errors="coerce") == 2024]
    focal_rev = hist2024[["Focal_ID", "Focal_Revenue"]].rename(columns={"Focal_ID": "firm_code", "Focal_Revenue": "Revenue_2024"})
    partner_rev = hist2024[["Partner_ID", "Partner_Revenue"]].rename(columns={"Partner_ID": "firm_code", "Partner_Revenue": "Revenue_2024"})
    combined = pd.concat([focal_rev, partner_rev], ignore_index=True).dropna()
    combined = combined.groupby("firm_code", as_index=False)["Revenue_2024"].first()

    covered = set(combined["firm_code"])
    missing = needed_codes - covered
    print(f"  Firms with 2024 revenue from existing history: {len(covered & needed_codes)}")
    print(f"  Firms needing fresh 2024 revenue pull (new entrants): {len(missing)}")

    if missing:
        needed_pairs_2024 = {(c, 2024) for c in missing}
        fresh = strict.stream_large_firm_year_table(
            INCOME_STMT_NEW, "Stkcd", "Accper", "Typrep", {"B001100000": "Revenue"}, needed_pairs_2024, yuan_cols={"Revenue"},
        )
        fresh = fresh.rename(columns={"firm_code": "firm_code", "Revenue": "Revenue_2024"})[["firm_code", "Revenue_2024"]]
        combined = pd.concat([combined, fresh], ignore_index=True).drop_duplicates("firm_code")

    return combined


def main() -> None:
    strict = load_module("strictmod_orig", "01_build_supplier_pairs_and_financial_panel.py")
    restruct = load_module("restructmod_orig", "06_restructure_reviewer_friendly_pipeline.py")

    pairs = pd.read_excel(PAIRS_2025, dtype={"Focal_ID": str, "Partner_ID": str})
    firm_panel = pd.read_excel(FIRM_PANEL_2025, dtype={"firm_code": str})

    print("Recomputing Inception_Year / Dyad_Duration against full combined history ...")
    pairs = recompute_inception_year(pairs)

    print("Merging FY2025 firm financials onto dyad pairs (Focal_/Partner_ prefix) ...")
    fin = build_financial_merged_2025(pairs, firm_panel)

    fin["Focal_StatDate"] = pd.Timestamp(year=TARGET_YEAR, month=12, day=31)
    fin["Partner_StatDate"] = pd.Timestamp(year=TARGET_YEAR, month=12, day=31)
    fin["Is_Listed"] = "Y"
    fin["Report_Type"] = 1
    fin["Focal_key"] = fin["Focal_ID"] + "_" + fin["Year"].astype(str)
    fin["Partner_key"] = fin["Partner_ID"] + "_" + fin["Year"].astype(str)

    print("Fetching Year-1 (2024) revenue for growth computation ...")
    needed_codes = set(pairs["Focal_ID"]) | set(pairs["Partner_ID"])
    rev_2024 = build_2024_revenue_lookup(strict, needed_codes)
    rev_lookup = rev_2024.set_index("firm_code")["Revenue_2024"]

    print("Constructing derived variables (Focal_Size, Focal_Lev, Focal_ROA, Power_Diff, etc.) ...")
    out = fin.copy()
    out["Year"] = pd.to_numeric(out["Year"], errors="coerce").astype("Int64")

    out["Focal_Size"] = np.log(pd.to_numeric(out["Focal_Asset"], errors="coerce").where(pd.to_numeric(out["Focal_Asset"], errors="coerce") > 0))
    out["Focal_Lev"] = restruct.safe_div(out["Focal_Liability"], out["Focal_Asset"])
    out["Focal_ROA"] = restruct.safe_div(out["Focal_NetProfit"], out["Focal_Asset"])
    out["Focal_Age"] = pd.to_numeric(out["Year"], errors="coerce") - restruct.est_year(out["Focal_EstabDate"])
    out["Focal_CashFlow"] = restruct.safe_div(out["Focal_NCF"], out["Focal_Asset"])
    out["Focal_RnD_Ratio"] = restruct.safe_div(out["Focal_RnD"], out["Focal_Revenue"])
    out["Focal_AdminExp_Ratio"] = restruct.safe_div(out["Focal_AdminExp"], out["Focal_Revenue"])

    out["Partner_Size"] = np.log(pd.to_numeric(out["Partner_Asset"], errors="coerce").where(pd.to_numeric(out["Partner_Asset"], errors="coerce") > 0))
    out["Partner_Lev"] = restruct.safe_div(out["Partner_Liability"], out["Partner_Asset"])
    out["Partner_ROA"] = restruct.safe_div(out["Partner_NetProfit"], out["Partner_Asset"])
    out["Partner_Age"] = pd.to_numeric(out["Year"], errors="coerce") - restruct.est_year(out["Partner_EstabDate"])
    out["Partner_CashFlow"] = restruct.safe_div(out["Partner_NCF"], out["Partner_Asset"])
    out["Partner_RnD_Ratio"] = restruct.safe_div(out["Partner_RnD"], out["Partner_Revenue"])
    out["Partner_AdminExp_Ratio"] = restruct.safe_div(out["Partner_AdminExp"], out["Partner_Revenue"])

    purchase_amt = pd.to_numeric(out["Purchase_Amount"], errors="coerce")
    out["Rela_Purchase_Ln"] = np.log(purchase_amt.where(purchase_amt > 0))
    out["Ln_Dyad_Duration"] = np.log(1 + pd.to_numeric(out["Dyad_Duration"], errors="coerce").where(pd.to_numeric(out["Dyad_Duration"], errors="coerce") >= 0))
    out["Power_Diff"] = out["Focal_Size"] - out["Partner_Size"]

    if all(c in out.columns for c in ["Focal_Latitude", "Focal_Longitude", "Partner_Latitude", "Partner_Longitude"]):
        out["Geo_Distance"] = restruct.haversine(out["Focal_Latitude"], out["Focal_Longitude"], out["Partner_Latitude"], out["Partner_Longitude"])
        out["Ln_Distance"] = np.log(1 + out["Geo_Distance"])
    else:
        out["Geo_Distance"] = np.nan
        out["Ln_Distance"] = np.nan

    # Growth formula: (Revenue_t - Revenue_{t-1}) / Revenue_{t-1}
    focal_rev_prev = out["Focal_ID"].map(rev_lookup)
    out["Focal_Growth"] = restruct.safe_div(out["Focal_Revenue"] - focal_rev_prev, focal_rev_prev)
    partner_rev_prev = out["Partner_ID"].map(rev_lookup)
    out["Partner_Growth"] = restruct.safe_div(out["Partner_Revenue"] - partner_rev_prev, partner_rev_prev)

    out.to_excel(OUT_FILE, index=False)
    print()
    print("=" * 60)
    print(f"2025 variable base written: {OUT_FILE}")
    print(f"Rows: {len(out)}  Cols: {out.shape[1]}")


if __name__ == "__main__":
    main()
