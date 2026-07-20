"""
v2025/02_build_2025_firm_year_panel.py
=======================================
Build the FY2025 firm-year financial panel for every firm code appearing (as
Focal_ID or Partner_ID) in the v2025/01 dyad pairs, using the EXACT SAME
formulas/field codes as the original 01_build_supplier_pairs_and_financial_panel.py,
pointed at the fresh CSMAR downloads under E:\\Supply - SHAP\\data\\raw_data\\base1\\downloads.

Field-code verification performed this session (see chat for detail):
- Balance sheet FS_Combas.xlsx: A001000000/A002000000/A001111000/A001123000 present,
  identical CSMAR standard codes to the old Balance Sheet file.
- Income statement FS_Comins.xlsx: B001100000/B002000000/B001216000/B001210000 present,
  identical codes.
- Cash flow FS_Comscfd.xlsx (direct method): C001000000 (net operating cash flow) present,
  same bottom-line code regardless of direct/indirect presentation.
- SOE: OLD SOE.xlsx used a pre-binarized "PropertyRightsNature" field (confirmed via
  value_counts to be a clean {0,1,NaN} field, so the original .clip(0,1) was defensive
  only). NEW EN_EquityNatureAll.xlsx has no such binary field; instead it has
  EquityNatureID (1=SOE,2=private,3=foreign,4=other, per its official CSMAR description
  file, with some multi-category strings like "1,2" for jointly-controlled firms). We
  map SoE=1 iff "1" appears as a token in EquityNatureID, else 0 -- the natural binary
  analogue of the original definition.
- HHI: OLD ListInduHHIY.xlsx's "HHIMainSaleRevenue" field is matched by NEW
  INDFI_HHI.xlsx's HHI_A field (both = revenue-share HHI within an industry bucket,
  confirmed via the official CSMAR description file). GRANULARITY CAVEAT: the OLD
  table only ever had 1-character industry-letter rows (the join key
  06_restructure...py actually uses), which we could not distinguish as CSRC-2001 vs
  CSRC-2012 vs any other single scheme with certainty; the NEW table has ONLY 3-char
  ('A01'-style) codes under the "中国上市公司协会" (CALC) scheme, with NO letter-only
  rows at all. We approximate the letter-level HHI for 2025 by averaging HHI_A across
  all 3-char sub-industry codes sharing the same first letter (within EndDate =
  2025-12-31), and we join it against firms' Focal_Industry itself (also CALC/"D"
  scheme, truncated to 1 char) so that the firm-side and HHI-side letter buckets are at
  least INTERNALLY self-consistent for 2025, even though the specific letter used per
  industry may not always match the older scheme used historically (flagged explicitly
  in the final report; this is a control variable, not a focal hypothesis variable).
- GovAbility BDT_ManaGovAbil.xlsx: IndDirectorRatio present, identical field name/scale.
- TobinQ: FI_T10.xlsx has F100901A (Tobin's Q value A), identical code to the original
  TobinQ.xlsx source.
- Static, slow-moving firm attributes (Industry[D-scheme]/EstabDate/Longitude/Latitude):
  the fresh "basic info" download (STK_LISTEDCOINFOANL.xlsx) only has 3 columns
  (Symbol/ShortName/EndDate) and cannot supply these. PRIMARY strategy: carry forward
  the most recent non-missing value per firm code from paper2's own already-processed
  2015-2024 history (03_financial_variable_base.xlsx), since these attributes are
  essentially time-invariant. FALLBACK (for firms never seen 2015-2024): pull Industry
  from TRD_Co.xlsx's IndcdZX field (confirmed via its own description file to be the
  same "中国上市公司协会" scheme) and EstabDate from TRD_Co's Estbdt. No fallback
  source for Longitude/Latitude was found for brand-new firms; left NaN and flagged.
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
OUT_DIR.mkdir(parents=True, exist_ok=True)

PAIRS_2025 = OUT_DIR / "01_dyad_pairs_2025_only.xlsx"
OUT_FILE = OUT_DIR / "02_firm_year_panel_2025.xlsx"
FLAGS_FILE = OUT_DIR / "02_data_quality_flags.xlsx"

BALANCE_SHEET_NEW = NEW_RAW_ROOT / r"资产负债表070127671(仅供vip使用)\FS_Combas.xlsx"
INCOME_STMT_NEW = NEW_RAW_ROOT / r"利润表081207684(仅供vip使用)\FS_Comins.xlsx"
CASH_FLOW_NEW = NEW_RAW_ROOT / r"现金流量表(直接法)081152089(仅供vip使用)\FS_Comscfd.xlsx"
SOE_NEW = NEW_RAW_ROOT / r"中国上市公司股权性质文件081633975(仅供vip使用)\EN_EquityNatureAll.xlsx"
HHI_NEW = NEW_RAW_ROOT / r"赫芬达尔指数表081716866(仅供vip使用)\INDFI_HHI.xlsx"
GOV_NEW = NEW_RAW_ROOT / r"管理层治理能力083720106(仅供vip使用)\BDT_ManaGovAbil.xlsx"
TOBINQ_NEW = NEW_RAW_ROOT / r"相对价值指标193936103(仅供vip使用)\FI_T10.xlsx"
TRD_CO_NEW = NEW_RAW_ROOT / r"公司文件063640845(仅供vip使用)\TRD_Co.xlsx"

TARGET_YEAR = 2025


def load_strict_module():
    spec = importlib.util.spec_from_file_location(
        "strictmod_orig", OLD_CODE_DIR / "01_build_supplier_pairs_and_financial_panel.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def get_needed_pairs() -> set[tuple[str, int]]:
    pairs = pd.read_excel(PAIRS_2025, dtype={"Focal_ID": str, "Partner_ID": str})
    codes = pd.concat([pairs["Focal_ID"], pairs["Partner_ID"]]).dropna().unique()
    return {(c, TARGET_YEAR) for c in codes}


def build_soe_2025(strict, needed_pairs: set[tuple[str, int]]) -> pd.DataFrame:
    df = pd.read_excel(
        SOE_NEW, header=0, skiprows=[1, 2], usecols=["Symbol", "EndDate", "EquityNatureID"], dtype={"Symbol": str}
    )
    df["firm_code"] = df["Symbol"].apply(strict.clean_code)
    ym = df["EndDate"].apply(strict.year_month)
    df["year"] = [x[0] for x in ym]
    df["month"] = [x[1] for x in ym]
    df = df[df["month"] == 12].copy()
    df = df[df.apply(lambda r: (r["firm_code"], r["year"]) in needed_pairs, axis=1)].copy()

    def parse_soe(v) -> int:
        if pd.isna(v):
            return 0
        tokens = [t.strip() for t in str(v).split(",")]
        return 1 if "1" in tokens else 0

    df["SoE"] = df["EquityNatureID"].apply(parse_soe)
    out = df[["firm_code", "year", "SoE"]].drop_duplicates(["firm_code", "year"])
    print(f"  SOE 2025 matched firm-years: {len(out):,}")
    return out


def build_hhi_letter_table_2025() -> pd.DataFrame:
    """Approximate a letter-level (1-char industry bucket) HHI table for 2025 by
    averaging the fine-grained HHI_A (revenue-share HHI, CALC scheme) across all
    3-char sub-industry codes sharing the same first letter. See module docstring
    for the full caveat."""
    df = pd.read_excel(HHI_NEW, header=0, skiprows=[1, 2], usecols=["IndustryCode", "EndDate", "HHI_A"])
    dt = pd.to_datetime(df["EndDate"], errors="coerce")
    df = df[(dt.dt.year == TARGET_YEAR) & (dt.dt.month == 12)].copy()
    df["indcd"] = df["IndustryCode"].astype(str).str.strip().str.upper().str[:1]
    df["hhi"] = pd.to_numeric(df["HHI_A"], errors="coerce")
    out = df.groupby("indcd", as_index=False)["hhi"].mean()
    out["year"] = TARGET_YEAR
    print(f"  HHI 2025 letter-buckets built (approximated from {len(df):,} sub-industry rows): {len(out):,} letters")
    return out


def build_static_attrs_from_history() -> pd.DataFrame:
    """Carry forward Industry / EstabDate / Longitude / Latitude from paper2's own
    already-processed 2015-2024 history, taking the most recent non-missing value
    per firm code (these attributes are essentially time-invariant)."""
    hist = pd.read_excel(
        OLD_PROC_DIR / "03_financial_variable_base.xlsx",
        dtype={"Focal_ID": str, "Partner_ID": str},
        usecols=[
            "Focal_ID", "Partner_ID", "Year",
            "Focal_Industry", "Focal_EstabDate", "Focal_Longitude", "Focal_Latitude",
            "Partner_Industry", "Partner_EstabDate", "Partner_Longitude", "Partner_Latitude",
        ],
    )
    focal = hist[["Focal_ID", "Year", "Focal_Industry", "Focal_EstabDate", "Focal_Longitude", "Focal_Latitude"]].rename(
        columns={
            "Focal_ID": "firm_code", "Year": "year", "Focal_Industry": "Industry",
            "Focal_EstabDate": "EstabDate", "Focal_Longitude": "Longitude", "Focal_Latitude": "Latitude",
        }
    )
    partner = hist[["Partner_ID", "Year", "Partner_Industry", "Partner_EstabDate", "Partner_Longitude", "Partner_Latitude"]].rename(
        columns={
            "Partner_ID": "firm_code", "Year": "year", "Partner_Industry": "Industry",
            "Partner_EstabDate": "EstabDate", "Partner_Longitude": "Longitude", "Partner_Latitude": "Latitude",
        }
    )
    combined = pd.concat([focal, partner], ignore_index=True).dropna(subset=["firm_code"])
    combined = combined.sort_values(["firm_code", "year"])

    def last_nonnull(s: pd.Series):
        s2 = s.dropna()
        return s2.iloc[-1] if len(s2) else np.nan

    grouped = combined.groupby("firm_code").agg(
        Industry=("Industry", last_nonnull),
        EstabDate=("EstabDate", last_nonnull),
        Longitude=("Longitude", last_nonnull),
        Latitude=("Latitude", last_nonnull),
    ).reset_index()
    return grouped


def build_static_attrs_fallback_trd(strict, missing_codes: set[str]) -> pd.DataFrame:
    """Fallback for firm codes never seen in the 2015-2024 history (genuinely new
    2025 entrants): pull Industry (CALC/"D" scheme, IndcdZX) and EstabDate from the
    fresh TRD_Co.xlsx company file. No Longitude/Latitude fallback is available."""
    if not missing_codes:
        return pd.DataFrame(columns=["firm_code", "Industry", "EstabDate", "Longitude", "Latitude"])
    trd = pd.read_excel(
        TRD_CO_NEW, header=0, skiprows=[1, 2], usecols=["Stkcd", "IndcdZX", "Estbdt"], dtype={"Stkcd": str}
    )
    trd["firm_code"] = trd["Stkcd"].apply(strict.clean_code)
    trd = trd[trd["firm_code"].isin(missing_codes)].drop_duplicates("firm_code")
    trd = trd.rename(columns={"IndcdZX": "Industry", "Estbdt": "EstabDate"})
    trd["Longitude"] = np.nan
    trd["Latitude"] = np.nan
    return trd[["firm_code", "Industry", "EstabDate", "Longitude", "Latitude"]]


def build_firm_panel_2025(strict, needed_pairs: set[tuple[str, int]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    print("Streaming FY2025 balance sheet ...")
    bs = strict.stream_large_firm_year_table(
        BALANCE_SHEET_NEW, "Stkcd", "Accper", "Typrep",
        {"A001000000": "Asset", "A002000000": "Liability", "A001111000": "AR", "A001123000": "Inventory"},
        needed_pairs, yuan_cols={"Asset", "Liability", "AR", "Inventory"},
    )

    print("Streaming FY2025 income statement ...")
    is_df = strict.stream_large_firm_year_table(
        INCOME_STMT_NEW, "Stkcd", "Accper", "Typrep",
        {"B001100000": "Revenue", "B002000000": "NetProfit", "B001216000": "RnD", "B001210000": "AdminExp"},
        needed_pairs, yuan_cols={"Revenue", "NetProfit", "RnD", "AdminExp"},
    )

    print("Streaming FY2025 cash flow statement (direct method) ...")
    cf = strict.stream_large_firm_year_table(
        CASH_FLOW_NEW, "Stkcd", "Accper", "Typrep",
        {"C001000000": "NCF"},
        needed_pairs, yuan_cols={"NCF"},
    )

    print("Building FY2025 SOE flag ...")
    soe = build_soe_2025(strict, needed_pairs)

    print("Reading FY2025 TobinQ (FI_T10, quarterly source filtered to year-end) ...")
    tobinq = strict.read_small_firm_year_table(
        TOBINQ_NEW, "Stkcd", "Accper", {"F100901A": "TobinQ"}, needed_pairs,
    )

    print("Reading FY2025 governance ability (independent director ratio) ...")
    gov = strict.read_small_firm_year_table(
        GOV_NEW, "Symbol", "Enddate", {"IndDirectorRatio": "IndepDir"}, needed_pairs, pct_cols={"IndepDir"},
    )

    for col in ["RnD", "AdminExp"]:
        if col in is_df.columns:
            is_df[col] = is_df[col].fillna(0)

    tables = [bs, is_df, cf, soe, tobinq, gov]
    firm_panel = None
    for tbl in tables:
        if tbl.empty:
            continue
        firm_panel = tbl if firm_panel is None else firm_panel.merge(tbl, on=["firm_code", "year"], how="outer")

    for col in ["RnD", "AdminExp"]:
        if col in firm_panel.columns:
            firm_panel[col] = firm_panel[col].fillna(0)

    print("Attaching static attributes (Industry / EstabDate / Longitude / Latitude) ...")
    all_codes = {c for c, _ in needed_pairs}
    static_hist = build_static_attrs_from_history()
    static_hist = static_hist[static_hist["firm_code"].isin(all_codes)]

    covered_codes = set(static_hist.loc[static_hist["Industry"].notna(), "firm_code"])
    missing_codes = all_codes - covered_codes
    static_fallback = build_static_attrs_fallback_trd(strict, missing_codes)
    print(f"  Firms with static attrs from 2015-2024 history: {len(covered_codes):,}")
    print(f"  Firms needing TRD_Co fallback (brand-new to the panel): {len(missing_codes):,}")

    static_all = pd.concat([static_hist[static_hist["firm_code"].isin(covered_codes)], static_fallback], ignore_index=True)
    static_all = static_all.drop_duplicates("firm_code")

    firm_panel["firm_code"] = firm_panel["firm_code"].astype(str)
    firm_panel = firm_panel.merge(static_all, on="firm_code", how="left")

    print("Joining FY2025 HHI (letter-bucket approximation, see module docstring) ...")
    hhi_letters = build_hhi_letter_table_2025()
    firm_panel["indcd_hhi"] = firm_panel["Industry"].astype(str).str.strip().str.upper().str[:1]
    firm_panel = firm_panel.merge(
        hhi_letters.rename(columns={"indcd": "indcd_hhi"}), on=["indcd_hhi", "year"], how="left"
    )
    firm_panel = firm_panel.rename(columns={"hhi": "HHI"}).drop(columns=["indcd_hhi"], errors="ignore")

    # ---- Data quality flags ----
    flag_rows = []
    still_no_industry = firm_panel.loc[firm_panel["Industry"].isna(), "firm_code"].tolist()
    flag_rows.append({"flag": "firms_missing_Industry_2025", "count": len(still_no_industry), "detail": ", ".join(still_no_industry[:30])})
    still_no_geo = firm_panel.loc[firm_panel["Longitude"].isna(), "firm_code"].tolist()
    flag_rows.append({"flag": "firms_missing_Longitude_Latitude_2025", "count": len(still_no_geo), "detail": ", ".join(still_no_geo[:30])})
    still_no_hhi = firm_panel.loc[firm_panel["HHI"].isna(), "firm_code"].tolist()
    flag_rows.append({"flag": "firms_missing_HHI_2025", "count": len(still_no_hhi), "detail": ", ".join(still_no_hhi[:30])})
    still_no_tobinq = firm_panel.loc[firm_panel["TobinQ"].isna(), "firm_code"].tolist()
    flag_rows.append({"flag": "firms_missing_TobinQ_2025", "count": len(still_no_tobinq), "detail": ", ".join(still_no_tobinq[:30])})
    still_no_indepdir = firm_panel.loc[firm_panel["IndepDir"].isna(), "firm_code"].tolist()
    flag_rows.append({"flag": "firms_missing_IndepDir_2025", "count": len(still_no_indepdir), "detail": ", ".join(still_no_indepdir[:30])})
    still_no_asset = firm_panel.loc[firm_panel["Asset"].isna(), "firm_code"].tolist()
    flag_rows.append({"flag": "firms_missing_Asset_2025", "count": len(still_no_asset), "detail": ", ".join(still_no_asset[:30])})
    flags = pd.DataFrame(flag_rows)

    print(f"Firm panel shape (2025): {firm_panel.shape[0]:,} rows x {firm_panel.shape[1]} columns")
    return firm_panel, flags


def main() -> None:
    strict = load_strict_module()
    needed_pairs = get_needed_pairs()
    print(f"Needed 2025 (firm_code, year) pairs: {len(needed_pairs):,}")

    firm_panel, flags = build_firm_panel_2025(strict, needed_pairs)

    with pd.ExcelWriter(OUT_FILE, engine="openpyxl") as writer:
        firm_panel.to_excel(writer, sheet_name="firm_year_panel_2025", index=False)
    with pd.ExcelWriter(FLAGS_FILE, engine="openpyxl") as writer:
        flags.to_excel(writer, sheet_name="flags", index=False)

    print()
    print("=" * 60)
    print(f"2025 firm-year panel written: {OUT_FILE}")
    print(f"2025 data-quality flags      : {FLAGS_FILE}")
    print(flags.to_string(index=False))


if __name__ == "__main__":
    main()
