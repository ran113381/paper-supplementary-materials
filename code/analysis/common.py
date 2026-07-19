"""
Shared helpers for the FY2025-extended-panel diagnostic battery.
Mirrors the EXACT construction used in E:\\Supply_Chain_Project\\code\\v2025\\06_verify_2024_reproduction.py
and the task brief's "Required construction" block.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

DATA_DIR = Path(r"E:\Supply_Chain_Project\data\processed_data\v2025")
MAIN_PACK = DATA_DIR / "08A_main_regression_package_2025.xlsx"
STRICT_PACK = DATA_DIR / "08B_strict_regression_package_2025.xlsx"

CONTROLS = [
    "Focal_Size", "Focal_Lev", "Focal_Age", "Focal_CashFlow", "Focal_SoE", "Focal_HHI",
    "Partner_Size", "Partner_Lev", "Partner_ROA",
]


def load_pack(sample: str = "main") -> pd.DataFrame:
    """sample in {'main','strict'}"""
    if sample == "main":
        raw = pd.read_excel(MAIN_PACK, sheet_name="main_winsorized", dtype={"Focal_ID": str, "Partner_ID": str})
    elif sample == "strict":
        raw = pd.read_excel(STRICT_PACK, sheet_name="strict_winsorized", dtype={"Focal_ID": str, "Partner_ID": str})
    else:
        raise ValueError(sample)
    return prep_pack(raw)


def prep_pack(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Focal_Industry"] = df["Focal_Industry"].astype(str)
    df["Focal_ID"] = df["Focal_ID"].astype(str)
    df["Focal_SoE"] = pd.to_numeric(df["Focal_SoE"], errors="coerce")
    df["Supplier_Dominance"] = (-pd.to_numeric(df["Power_Diff"], errors="coerce")).clip(lower=0)
    df["Partner_Ahead"] = (
        pd.to_numeric(df["Partner_GenAI_Index"], errors="coerce") - pd.to_numeric(df["Focal_GenAI_Index"], errors="coerce")
    ).clip(lower=0)
    df["Power_Pressure"] = df["Supplier_Dominance"] * df["Partner_Ahead"]
    return df


def fit_model(df: pd.DataFrame, rhs_terms: list[str], cluster_var: str = "Focal_Industry"):
    """statsmodels OLS with Industry+Year FE, cluster-robust SE on cluster_var."""
    formula = "Focal_ROA ~ " + " + ".join(rhs_terms + ["C(Focal_Industry)", "C(Year)"])
    model = smf.ols(formula=formula, data=df, missing="drop")
    idx = model.data.row_labels
    fit = model.fit(cov_type="cluster", cov_kwds={"groups": df.loc[idx, cluster_var]})
    return fit, df.loc[idx].copy()


def h1_terms():
    return ["Focal_GenAI_Index"] + CONTROLS


def h2_terms():
    return ["Focal_GenAI_Index"] + CONTROLS + ["Focal_RnD_Ratio", "Focal_GenAI_Index:Focal_RnD_Ratio"]


def h3_terms():
    return ["Focal_GenAI_Index"] + CONTROLS + ["Power_Pressure", "Focal_GenAI_Index:Power_Pressure"]


def stars(p: float) -> str:
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def fmt_coef(coef: float, se: float, p: float) -> str:
    return f"{coef:.4f}{stars(p)} (se={se:.4f}, p={p:.4f})"


def extract_row(fit, term: str) -> dict:
    return {
        "term": term,
        "coef": float(fit.params[term]),
        "se": float(fit.bse[term]),
        "p": float(fit.pvalues[term]),
        "n": int(fit.nobs),
        "r2": float(fit.rsquared),
    }


def print_row(label: str, r: dict) -> None:
    print(f"  {label:38s} coef={r['coef']:>10.4f}{stars(r['p']):<3s} se={r['se']:.4f}  p={r['p']:.4f}  N={r['n']}  R2={r['r2']:.4f}")
