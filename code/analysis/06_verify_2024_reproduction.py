"""
v2025/06_verify_2024_reproduction.py
======================================
CRITICAL VERIFICATION GATE. Filters the new 08A/08B_..._2025.xlsx packages
down to Year<=2024 and re-runs the EXACT published-Table-9 construction from
13_prepare_publication_exhibits.py (prep_pack + fit_model, reused verbatim)
to confirm the reconstruction reproduces the original 2015-2024-only results
to 4 decimal places, including the exact 1,017 / 897 sample sizes.

If ANY number fails to match exactly, this script prints a detailed
diagnostic (row-count deltas, per-column value diffs against the original
08A/08B raw+winsorized sheets) instead of silently reporting success.
"""
from __future__ import annotations

import os
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[2]

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

OLD_PROC_DIR = Path(os.environ.get("PAPER2_PROC_DIR", _REPO / "data"))
OUT_DIR = Path(os.environ.get("PAPER2_PROC_DIR", _REPO / "data")) / "v2025"

NEW_MAIN_PACK = OUT_DIR / "08A_main_regression_package_2025.xlsx"
NEW_STRICT_PACK = OUT_DIR / "08B_strict_regression_package_2025.xlsx"
OLD_MAIN_PACK = OLD_PROC_DIR / "08A_main_regression_package.xlsx"
OLD_STRICT_PACK = OLD_PROC_DIR / "08B_strict_regression_package.xlsx"

BASE_CONTROLS = [
    "Focal_Size", "Focal_Lev", "Focal_Age", "Focal_CashFlow", "Focal_SoE", "Focal_HHI",
    "Partner_Size", "Partner_Lev", "Partner_ROA",
]

# Published Table 9 numbers (from the task brief, independently verified this
# session against the untouched original 08A/08B before any 2025 work began).
EXPECTED = {
    "main": {
        "H1": {"coef": -0.0146, "se": 0.0048, "n": 1017, "r2": 0.384},
        "H2_main": {"coef": -0.0021, "n": 1017, "r2": 0.425},
        "H2_int": {"coef": -0.0446, "se": 0.0197},
        "H3_main": {"coef": -0.0117, "n": 1007, "r2": 0.393},
        "H3_int": {"coef": -0.0088, "se": 0.0017},
    },
    "strict": {
        "H1": {"coef": -0.0123, "n": 897},
        "H2_int": {"coef": -0.0562, "n": 897},
        "H3_int": {"coef": -0.0087, "n": 895},
    },
}


def prep_pack(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Focal_Industry"] = df["Focal_Industry"].astype(str)
    df["Focal_SoE"] = pd.to_numeric(df["Focal_SoE"], errors="coerce")
    df["Supplier_Dominance"] = (-pd.to_numeric(df["Power_Diff"], errors="coerce")).clip(lower=0)
    df["Partner_Ahead"] = (
        pd.to_numeric(df["Partner_GenAI_Index"], errors="coerce") - pd.to_numeric(df["Focal_GenAI_Index"], errors="coerce")
    ).clip(lower=0)
    df["Power_Pressure"] = df["Supplier_Dominance"] * df["Partner_Ahead"]
    return df


def fit_model(df: pd.DataFrame, rhs_terms: list[str]):
    formula = "Focal_ROA ~ " + " + ".join(rhs_terms + ["C(Focal_Industry)", "C(Year)"])
    model = smf.ols(formula=formula, data=df, missing="drop")
    idx = model.data.row_labels
    fit = model.fit(cov_type="cluster", cov_kwds={"groups": df.loc[idx, "Focal_Industry"]})
    return fit, df.loc[idx].copy()


def run_and_compare(pack_path: Path, sheet_name: str, sample_key: str, label: str) -> list[dict]:
    print("=" * 70)
    print(f"{label}  (sheet={sheet_name}, filtered to Year<=2024)")
    print("=" * 70)
    raw = pd.read_excel(pack_path, sheet_name=sheet_name, dtype={"Focal_ID": str, "Partner_ID": str})
    raw["Year"] = pd.to_numeric(raw["Year"], errors="coerce")
    df = raw[raw["Year"] <= 2024].copy()
    print(f"Rows after Year<=2024 filter: {len(df):,}  (full sheet had {len(raw):,} rows)")

    df = prep_pack(df)
    results = []

    fit1, _ = fit_model(df, ["Focal_GenAI_Index"] + BASE_CONTROLS)
    exp1 = EXPECTED[sample_key]["H1"]
    results.append(check("H1 coef", fit1.params["Focal_GenAI_Index"], exp1["coef"]))
    if "se" in exp1:
        results.append(check("H1 se", fit1.bse["Focal_GenAI_Index"], exp1["se"]))
    results.append(check("H1 N", fit1.nobs, exp1["n"], is_count=True))
    if "r2" in exp1:
        results.append(check("H1 R2", fit1.rsquared, exp1["r2"], tol=5e-4))

    fit2, _ = fit_model(df, ["Focal_GenAI_Index"] + BASE_CONTROLS + ["Focal_RnD_Ratio", "Focal_GenAI_Index:Focal_RnD_Ratio"])
    if "H2_main" in EXPECTED[sample_key]:
        exp2m = EXPECTED[sample_key]["H2_main"]
        results.append(check("H2 main coef", fit2.params["Focal_GenAI_Index"], exp2m["coef"]))
        results.append(check("H2 N", fit2.nobs, exp2m["n"], is_count=True))
        if "r2" in exp2m:
            results.append(check("H2 R2", fit2.rsquared, exp2m["r2"], tol=5e-4))
    exp2i = EXPECTED[sample_key]["H2_int"]
    results.append(check("H2 interaction coef", fit2.params["Focal_GenAI_Index:Focal_RnD_Ratio"], exp2i["coef"]))
    if "se" in exp2i:
        results.append(check("H2 interaction se", fit2.bse["Focal_GenAI_Index:Focal_RnD_Ratio"], exp2i["se"]))
    if "n" in exp2i:
        results.append(check("H2 N (strict)", fit2.nobs, exp2i["n"], is_count=True))

    fit3, _ = fit_model(df, ["Focal_GenAI_Index"] + BASE_CONTROLS + ["Power_Pressure", "Focal_GenAI_Index:Power_Pressure"])
    if "H3_main" in EXPECTED[sample_key]:
        exp3m = EXPECTED[sample_key]["H3_main"]
        results.append(check("H3 main coef", fit3.params["Focal_GenAI_Index"], exp3m["coef"]))
        results.append(check("H3 N", fit3.nobs, exp3m["n"], is_count=True))
        if "r2" in exp3m:
            results.append(check("H3 R2", fit3.rsquared, exp3m["r2"], tol=5e-4))
    exp3i = EXPECTED[sample_key]["H3_int"]
    results.append(check("H3 interaction coef", fit3.params["Focal_GenAI_Index:Power_Pressure"], exp3i["coef"]))
    if "se" in exp3i:
        results.append(check("H3 interaction se", fit3.bse["Focal_GenAI_Index:Power_Pressure"], exp3i["se"]))
    if "n" in exp3i:
        results.append(check("H3 N (strict)", fit3.nobs, exp3i["n"], is_count=True))

    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        print(f"  [{status}] {r['label']}: got={r['got']}  expected={r['expected']}  diff={r['diff']:.6g}")

    return results


def check(label: str, got: float, expected: float, tol: float = 5e-5, is_count: bool = False) -> dict:
    got_f = float(got)
    diff = abs(got_f - expected)
    ok = (diff == 0) if is_count else (diff <= tol)
    return {"label": label, "got": got_f, "expected": expected, "diff": diff, "pass": ok}


def diagnose_divergence(pack_path: Path, sheet_raw: str, old_pack_path: Path, old_sheet_raw: str, sample_key: str) -> None:
    print()
    print(f"--- DIAGNOSTIC: comparing {sheet_raw} in new vs old {sample_key} pack (Year<=2024 subset) ---")
    new_raw = pd.read_excel(pack_path, sheet_name=sheet_raw, dtype={"Focal_ID": str, "Partner_ID": str})
    old_raw = pd.read_excel(old_pack_path, sheet_name=old_sheet_raw, dtype={"Focal_ID": str, "Partner_ID": str})
    new_raw["Year"] = pd.to_numeric(new_raw["Year"], errors="coerce")
    new_sub = new_raw[new_raw["Year"] <= 2024].copy()

    print(f"  old rows: {len(old_raw):,}  new(<=2024) rows: {len(new_sub):,}")

    old_keys = set(zip(old_raw["Focal_ID"], old_raw["Partner_ID"], old_raw["Year"].astype(int)))
    new_keys = set(zip(new_sub["Focal_ID"], new_sub["Partner_ID"], new_sub["Year"].astype(int)))
    only_old = old_keys - new_keys
    only_new = new_keys - old_keys
    print(f"  dyad-year keys only in OLD (missing from new): {len(only_old):,}")
    if only_old:
        print("    sample:", list(only_old)[:10])
    print(f"  dyad-year keys only in NEW (unexpected extra rows): {len(only_new):,}")
    if only_new:
        print("    sample:", list(only_new)[:10])

    common = old_keys & new_keys
    if common:
        old_idx = old_raw.set_index(["Focal_ID", "Partner_ID"])
        new_idx = new_sub.set_index(["Focal_ID", "Partner_ID"])
        numeric_cols = [c for c in old_raw.columns if c in new_sub.columns and pd.api.types.is_numeric_dtype(old_raw[c])]
        mismatch_counts = {}
        for col in numeric_cols:
            try:
                o = old_idx[col]
                n = new_idx[col]
                aligned = o.align(n, join="inner")
                diff = (aligned[0].astype(float) - aligned[1].astype(float)).abs()
                bad = int((diff > 1e-6).sum())
                if bad:
                    mismatch_counts[col] = bad
            except Exception:
                continue
        if mismatch_counts:
            print("  columns with value mismatches on common dyad-year keys:")
            for col, n in sorted(mismatch_counts.items(), key=lambda x: -x[1]):
                print(f"    {col}: {n} mismatched rows")
        else:
            print("  no value mismatches found on common dyad-year keys (row-set difference is the issue).")


def main() -> None:
    all_results = []
    all_results += run_and_compare(NEW_MAIN_PACK, "main_winsorized", "main", "MAIN SAMPLE")
    all_results += run_and_compare(NEW_STRICT_PACK, "strict_winsorized", "strict", "STRICT SAMPLE")

    n_fail = sum(1 for r in all_results if not r["pass"])
    print()
    print("=" * 70)
    if n_fail == 0:
        print(f"GATE CHECK: PASS -- all {len(all_results)} checks match the published Table 9 exactly.")
    else:
        print(f"GATE CHECK: FAIL -- {n_fail} of {len(all_results)} checks did not match. Running diagnostics ...")
        diagnose_divergence(NEW_MAIN_PACK, "main_raw", OLD_MAIN_PACK, "main_raw", "main")
        diagnose_divergence(NEW_STRICT_PACK, "strict_raw", OLD_STRICT_PACK, "strict_raw", "strict")
    print("=" * 70)


if __name__ == "__main__":
    main()
