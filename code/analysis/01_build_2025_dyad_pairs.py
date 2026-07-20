"""
v2025/01_build_2025_dyad_pairs.py
==================================
Build FY2025 focal-partner supplier dyad pairs from the fresh CSMAR download,
using the EXACT SAME matching logic as the original
<PROJECT_ROOT>\\code\\01_build_supplier_pairs_and_financial_panel.py
(classify_csmar_match / is_a_share / clean_code / normalize_name), just pointed
at the new FY2025 raw files.

This produces ONLY the new 2025 dyad-year rows (Year == 2025). The 2015-2024
rows are left completely untouched and are taken verbatim from the existing
<PROJECT_ROOT>\\data\\processed_data\\01_supplier_dyad_pairs.xlsx in a
later concatenation step (v2025/06_concat_and_rebuild.py).

Output: <PROJECT_ROOT>\\data\\processed_data\\v2025\\01_dyad_pairs_2025_only.xlsx
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

TOPFIVE_PURCHASE_2025 = NEW_RAW_ROOT / r"前五大供应商采购信息表090553750(仅供vip使用)\SC_TopFivePurchaseInfo.xlsx"
BASIC_INFO_NEW = NEW_RAW_ROOT / r"上市公司基本信息年度表074625739(仅供vip使用)\STK_LISTEDCOINFOANL.xlsx"
TRD_CO_NEW = NEW_RAW_ROOT / r"公司文件063640845(仅供vip使用)\TRD_Co.xlsx"

OUT_FILE = OUT_DIR / "01_dyad_pairs_2025_only.xlsx"
LOG_FILE = OUT_DIR / "01_dyad_pairs_2025_match_log.xlsx"

TARGET_YEAR = 2025


def load_strict_module():
    """Reuse the exact matching / normalization functions from the original
    frozen pipeline script, unmodified."""
    spec = importlib.util.spec_from_file_location(
        "strictmod_orig", OLD_CODE_DIR / "01_build_supplier_pairs_and_financial_panel.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_extended_name_map(strict) -> dict[str, set[str]]:
    """Extend the original name_map (built from the OLD Basic Information Table,
    ShortName + FullName) with names from the fresh TRD_Co.xlsx company file
    (Stknme + Conme), since the new STK_LISTEDCOINFOANL.xlsx basic-info download
    only has Symbol/ShortName/EndDate (no FullName) and would be a weaker map
    on its own. This only affects DISAMBIGUATION of multi-code BusinessSymbol
    strings; direct single-code matches do not use the name map at all."""
    name_map = strict.load_name_map()

    trd = pd.read_excel(
        TRD_CO_NEW, header=0, skiprows=[1, 2], usecols=["Stkcd", "Stknme", "Conme"], dtype={"Stkcd": str}
    )
    trd["Stkcd"] = trd["Stkcd"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(6)
    for _, row in trd.iterrows():
        code = row["Stkcd"]
        names = name_map.setdefault(code, set())
        for nm in [row["Stknme"], row["Conme"]]:
            n = strict.normalize_name(nm)
            if n:
                names.add(n)
    return name_map


def build_2025_pairs(strict) -> tuple[pd.DataFrame, pd.DataFrame]:
    name_map = build_extended_name_map(strict)

    csmar_raw = pd.read_excel(
        TOPFIVE_PURCHASE_2025,
        header=0,
        skiprows=[1, 2],
        dtype={"Symbol": str, "BusinessSymbol": str},
    )
    print(f"Raw rows in fresh SC_TopFivePurchaseInfo.xlsx: {len(csmar_raw):,}")

    csmar_raw["_year"] = pd.to_datetime(csmar_raw["EndDate"], errors="coerce").dt.year
    csmar_raw = csmar_raw[csmar_raw["_year"] == TARGET_YEAR].copy()
    print(f"Rows with EndDate year == {TARGET_YEAR}: {len(csmar_raw):,}")

    csmar_raw["IsListed"] = csmar_raw["IsListed"].astype(str).str.strip()
    csmar_listed = csmar_raw[csmar_raw["IsListed"].str.upper().isin(["Y", "YES", "是", "岆"])].copy()
    print(f"Rows with IsListed flag set (listed counterparty): {len(csmar_listed):,}")

    log_rows = []
    matched_rows = []
    row_id = 0
    direct_n = name_n = unresolved_n = 0

    for _, rec in csmar_listed.iterrows():
        row_id += 1
        focal_id = strict.clean_code(rec.get("Symbol"))
        year = TARGET_YEAR
        partner_id, match_method, confidence, unique_flag, exclusion_reason = strict.classify_csmar_match(
            rec.get("BusinessSymbol"),
            rec.get("InstitutionName"),
            name_map,
        )

        if exclusion_reason is None and not strict.is_a_share(focal_id):
            exclusion_reason = "invalid_focal_a_share_code"
            partner_id = np.nan

        if exclusion_reason is None:
            if match_method == "direct_code":
                direct_n += 1
            else:
                name_n += 1
        else:
            unresolved_n += 1

        log_rows.append(
            {
                "log_id": row_id,
                "source_db": "CSMAR_2025",
                "Focal_ID": focal_id,
                "Partner_name_raw": rec.get("InstitutionName"),
                "BusinessSymbol_raw": rec.get("BusinessSymbol"),
                "Partner_ID_standardized": partner_id if exclusion_reason is None else np.nan,
                "Year": year,
                "match_method": match_method,
                "match_confidence": confidence,
                "unique_match_flag": unique_flag,
                "exclusion_reason": exclusion_reason,
                "source_row_index": int(rec.name),
            }
        )

        if exclusion_reason is None:
            matched_rows.append(
                {
                    "log_id": row_id,
                    "source_db": "CSMAR_2025",
                    "Focal_ID": focal_id,
                    "Partner_ID": partner_id,
                    "Year": year,
                    "Partner": rec.get("InstitutionName"),
                    "Purchase_Amount": strict.to_number(rec.get("PurchaseAmount")) / 1_000_000,
                    "Rela_Purchase_Ratio": strict.to_number(rec.get("ProportionOfTotalValue")),
                    "Partner_Rank": strict.to_number(rec.get("Rank")),
                    "BusinessSymbol_raw": rec.get("BusinessSymbol"),
                    "_src_priority": 0,
                }
            )

    matched_df = pd.DataFrame(matched_rows)
    print(f"Direct-code matches: {direct_n:,}  Name-assisted matches: {name_n:,}  Unresolved/excluded: {unresolved_n:,}")
    print(f"Pre-dedup matched rows: {len(matched_df):,}")

    if matched_df.empty:
        logs = pd.DataFrame(log_rows)
        return matched_df, logs

    matched_df["_nonnull_score"] = matched_df[["Partner", "Purchase_Amount", "Rela_Purchase_Ratio", "Partner_Rank"]].notna().sum(axis=1)
    matched_df = matched_df.sort_values(
        ["Focal_ID", "Partner_ID", "Year", "_src_priority", "_nonnull_score"],
        ascending=[True, True, True, True, False],
    )
    final_pairs = matched_df.drop_duplicates(subset=["Focal_ID", "Partner_ID", "Year"], keep="first").copy()
    kept_log_ids = set(final_pairs["log_id"])

    logs = pd.DataFrame(log_rows)
    logs["entered_2025_sample"] = logs["log_id"].isin(kept_log_ids).astype(int)

    print(f"Final deduped 2025 dyad-year rows: {len(final_pairs):,}")
    print(f"Unique focal firms (2025): {final_pairs['Focal_ID'].nunique():,}")
    print(f"Unique partner firms (2025): {final_pairs['Partner_ID'].nunique():,}")

    final_pairs = final_pairs.drop(columns=["_src_priority", "_nonnull_score"])
    return final_pairs, logs


def main() -> None:
    strict = load_strict_module()
    pairs, logs = build_2025_pairs(strict)

    with pd.ExcelWriter(OUT_FILE, engine="openpyxl") as writer:
        pairs.to_excel(writer, sheet_name="pairs_2025", index=False)
    with pd.ExcelWriter(LOG_FILE, engine="openpyxl") as writer:
        logs.to_excel(writer, sheet_name="match_log_2025", index=False)

    print()
    print("=" * 60)
    print(f"2025 dyad pairs written: {OUT_FILE}")
    print(f"2025 match log written : {LOG_FILE}")


if __name__ == "__main__":
    main()
