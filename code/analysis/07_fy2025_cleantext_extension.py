# -*- coding: utf-8 -*-
"""
FY2025 clean-text extension (manuscript §4.5, Table 12) — end-to-end, verified runnable.

Clean-text filter: drop rows with Year==2025 AND Focal_MDA_CharCount==32767 (the Excel
cell cap; 42 of the 143 fiscal-2025 main-sample rows hit it, mechanically censoring the
disclosure measure for the longest documents). All four §4.5 estimates use the identical
baseline specification: Focal_ROA ~ terms + controls + C(Focal_Industry) + C(Year),
SEs clustered by Focal_Industry. The predetermined-R&D lag is built on the FULL
2015–2025 panel BEFORE the clean-text filter (R&D is a financial variable, unaffected
by text truncation), mirroring 01_main_grid.py's order of operations.

Requires the private extended regression package (excluded from this public repo;
see DATA_AVAILABILITY.md):
    <private>/data/processed_data/v2025/08A_main_regression_package_2025.xlsx
        sheet: main_winsorized

Verified output (2026-07-16 backtest; = manuscript Table 12):
    H1  Focal_GenAI_Index                  -0.0094 (SE 0.0040, p=.019)  N=1,115
    H2  GenAI x R&D (contemporaneous)      -0.0510 (SE 0.0187, p=.006)  N=1,115
    H2  GenAI x lagged R&D (predetermined) -0.0945 (SE 0.0335, p=.005)  N=637
    H3  GenAI x Power_Pressure             -0.0057 (SE 0.0022, p=.009)  N=1,098

Usage:  python 07_fy2025_cleantext_extension.py <path-to-08A_main_regression_package_2025.xlsx>
"""
import sys
import pandas as pd
import statsmodels.formula.api as smf

CONTROLS = ["Focal_Size", "Focal_Lev", "Focal_Age", "Focal_CashFlow", "Focal_SoE",
            "Focal_HHI", "Partner_Size", "Partner_Lev", "Partner_ROA"]
TRUNC_LEN = 32767


def prep_pack(df):
    df = df.copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Focal_Industry"] = df["Focal_Industry"].astype(str)
    df["Focal_SoE"] = pd.to_numeric(df["Focal_SoE"], errors="coerce")
    df["Supplier_Dominance"] = (-pd.to_numeric(df["Power_Diff"], errors="coerce")).clip(lower=0)
    df["Partner_Ahead"] = (
        pd.to_numeric(df["Partner_GenAI_Index"], errors="coerce")
        - pd.to_numeric(df["Focal_GenAI_Index"], errors="coerce")
    ).clip(lower=0)
    df["Power_Pressure"] = df["Supplier_Dominance"] * df["Partner_Ahead"]
    return df


def fit_model(df, rhs_terms, cluster_col="Focal_Industry"):
    formula = "Focal_ROA ~ " + " + ".join(rhs_terms + ["C(Focal_Industry)", "C(Year)"])
    model = smf.ols(formula=formula, data=df, missing="drop")
    idx = model.data.row_labels
    return model.fit(cov_type="cluster", cov_kwds={"groups": df.loc[idx, cluster_col]})


def add_firm_year_lag(df, entity_col, value_col, out_col):
    lookup = (
        df[[entity_col, "Year", value_col]]
        .drop_duplicates(subset=[entity_col, "Year"])
        .sort_values([entity_col, "Year"])
    )
    lookup[out_col] = lookup.groupby(entity_col)[value_col].shift(1)
    return df.merge(lookup[[entity_col, "Year", out_col]], on=[entity_col, "Year"], how="left")


def show(label, fit, term):
    print(f"{label:42s} coef={fit.params[term]:+.4f}  se={fit.bse[term]:.4f}  "
          f"p={fit.pvalues[term]:.4f}  N={int(fit.nobs)}")


if __name__ == "__main__":
    pack = sys.argv[1]
    df = prep_pack(pd.read_excel(pack, sheet_name="main_winsorized",
                                 dtype={"Focal_ID": str, "Partner_ID": str}))
    focal_cc = pd.to_numeric(df["Focal_MDA_CharCount"], errors="coerce")
    trunc = (df["Year"] == 2025) & (focal_cc == TRUNC_LEN)
    print(f"fiscal-2025 rows: {int((df['Year'] == 2025).sum())}; truncated (dropped): {int(trunc.sum())}")

    clean = df.loc[~trunc].copy()

    show("H1", fit_model(clean, ["Focal_GenAI_Index"] + CONTROLS), "Focal_GenAI_Index")
    show("H2 contemporaneous",
         fit_model(clean, ["Focal_GenAI_Index", "Focal_RnD_Ratio",
                           "Focal_GenAI_Index:Focal_RnD_Ratio"] + CONTROLS),
         "Focal_GenAI_Index:Focal_RnD_Ratio")

    lagged = add_firm_year_lag(df, "Focal_ID", "Focal_RnD_Ratio", "L1_Focal_RnD_Ratio")
    lagged["GenAI_x_L1RnD"] = lagged["Focal_GenAI_Index"] * lagged["L1_Focal_RnD_Ratio"]
    show("H2 predetermined (lagged R&D)",
         fit_model(lagged.loc[~trunc], ["Focal_GenAI_Index", "L1_Focal_RnD_Ratio",
                                        "GenAI_x_L1RnD"] + CONTROLS),
         "GenAI_x_L1RnD")

    show("H3",
         fit_model(clean, ["Focal_GenAI_Index", "Power_Pressure",
                           "Focal_GenAI_Index:Power_Pressure"] + CONTROLS),
         "Focal_GenAI_Index:Power_Pressure")
