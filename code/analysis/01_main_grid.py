"""
Diagnostic econometrics grid - Cells A, C, D, E, F, G + R1.2 + R1.5 + within-firm
variation + MDE.  Cell B (two-way clustering) is handled separately via the
statspai MCP tools.

All numbers are written to a JSON file for precise, non-transcribed reporting,
and also printed to stdout in readable form.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

PROC_DIR = Path(r"E:\Supply_Chain_Project\data\processed_data")
MAIN_PACK = PROC_DIR / "08A_main_regression_package.xlsx"
STRICT_PACK = PROC_DIR / "08B_strict_regression_package.xlsx"
SCRATCH = Path(r"C:\Users\asus\AppData\Local\Temp\claude\E--Supply---SHAP\ff49c3f8-4243-4540-abcd-8d73380c708c\scratchpad")

CONTROLS = ['Focal_Size', 'Focal_Lev', 'Focal_Age', 'Focal_CashFlow', 'Focal_SoE', 'Focal_HHI',
            'Partner_Size', 'Partner_Lev', 'Partner_ROA']

RESULTS: dict = {}


# --------------------------------------------------------------------------
# Loading / derived variables
# --------------------------------------------------------------------------
def load(path, sheet):
    df = pd.read_excel(path, sheet_name=sheet, dtype={"Focal_ID": str, "Partner_ID": str})
    df['Focal_Industry'] = df['Focal_Industry'].astype(str)
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df['Supplier_Dominance'] = (-pd.to_numeric(df['Power_Diff'], errors='coerce')).clip(lower=0)
    df['Partner_Ahead'] = (pd.to_numeric(df['Partner_GenAI_Index'], errors='coerce') - pd.to_numeric(df['Focal_GenAI_Index'], errors='coerce')).clip(lower=0)
    df['Power_Pressure'] = df['Supplier_Dominance'] * df['Partner_Ahead']
    return df


def add_firm_year_lag(df: pd.DataFrame, entity_col: str, value_col: str, out_col: str) -> pd.DataFrame:
    """Exactly mirrors regression_spec_utils._add_firm_year_lag."""
    lookup = (
        df[[entity_col, "Year", value_col]]
        .drop_duplicates(subset=[entity_col, "Year"])
        .sort_values([entity_col, "Year"])
    )
    lookup[out_col] = lookup.groupby(entity_col)[value_col].shift(1)
    return df.merge(lookup[[entity_col, "Year", out_col]], on=[entity_col, "Year"], how="left")


def stars(p):
    if pd.isna(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def term_result(fit, term):
    if term not in fit.params.index:
        return None
    return {
        "term": term,
        "coef": float(fit.params[term]),
        "se": float(fit.bse[term]),
        "p": float(fit.pvalues[term]),
        "stars": stars(fit.pvalues[term]),
    }


def run_ols(df, formula, cluster_col, weights_col=None, engine="ols"):
    """Fit OLS or WLS with cluster-robust SEs, matching the verified baseline pattern."""
    if weights_col is None:
        model = smf.ols(formula=formula, data=df, missing='drop')
    else:
        model = smf.wls(formula=formula, data=df, weights=df[weights_col].to_numpy(), missing='drop')
    idx = model.data.row_labels
    groups = df.loc[idx, cluster_col]
    fit = model.fit(cov_type='cluster', cov_kwds={'groups': groups})
    n_clusters = int(groups.nunique())
    return fit, idx, n_clusters


def fe_formula(rhs_terms, fe_terms=("Focal_Industry", "Year")):
    fe_rhs = [f"C({t})" for t in fe_terms]
    return "Focal_ROA ~ " + " + ".join(rhs_terms + fe_rhs)


print("Loading and constructing derived variables ...")
main_df = load(MAIN_PACK, "main_winsorized")
strict_df = load(STRICT_PACK, "strict_winsorized")

# lags needed for Cells E, F, G, and R1.5
for label, df in [("main", main_df), ("strict", strict_df)]:
    pass

main_df = add_firm_year_lag(main_df, "Focal_ID", "Focal_GenAI_Index", "L1_Focal_GenAI_Index")
strict_df = add_firm_year_lag(strict_df, "Focal_ID", "Focal_GenAI_Index", "L1_Focal_GenAI_Index")
main_df = add_firm_year_lag(main_df, "Focal_ID", "Focal_RnD_Ratio", "L1_Focal_RnD_Ratio")
strict_df = add_firm_year_lag(strict_df, "Focal_ID", "Focal_RnD_Ratio", "L1_Focal_RnD_Ratio")

# sanity check: is Focal_GenAI_Index / Focal_RnD_Ratio / Focal_Industry constant within Focal_ID-Year?
print("\n" + "=" * 100)
print("DATA-QUALITY SANITY CHECKS (within Focal_ID x Year, across dyad partner rows)")
print("=" * 100)
for label, df in [("main", main_df), ("strict", strict_df)]:
    g = df.groupby(["Focal_ID", "Year"])
    n_genai_bad = (g["Focal_GenAI_Index"].nunique(dropna=True) > 1).sum()
    n_rnd_bad = (g["Focal_RnD_Ratio"].nunique(dropna=True) > 1).sum()
    n_ind_bad = (g["Focal_Industry"].nunique(dropna=True) > 1).sum()
    n_groups = g.ngroups
    print(f"[{label}] firm-year groups={n_groups} | groups with >1 distinct Focal_GenAI_Index across partners: {n_genai_bad} "
          f"| >1 distinct Focal_RnD_Ratio: {n_rnd_bad} | >1 distinct Focal_Industry: {n_ind_bad}")
    # is Focal_Industry constant within Focal_ID across ALL years?
    n_ind_bad_id = (df.groupby("Focal_ID")["Focal_Industry"].nunique(dropna=True) > 1).sum()
    print(f"      Focal_ID with >1 distinct Focal_Industry across its whole history: {n_ind_bad_id}")

# --------------------------------------------------------------------------
# CELL A: published spec, cluster on Focal_ID
# --------------------------------------------------------------------------
print("\n" + "=" * 100)
print("CELL A: Published spec (C(Focal_Industry)+C(Year) FE), clustered on Focal_ID")
print("=" * 100)
RESULTS["cellA"] = {}
for label, df in [("main", main_df), ("strict", strict_df)]:
    RESULTS["cellA"][label] = {}
    specs = {
        "H1": ["Focal_GenAI_Index"] + CONTROLS,
        "H2": ["Focal_GenAI_Index"] + CONTROLS + ["Focal_RnD_Ratio", "Focal_GenAI_Index:Focal_RnD_Ratio"],
        "H3": ["Focal_GenAI_Index"] + CONTROLS + ["Power_Pressure", "Focal_GenAI_Index:Power_Pressure"],
    }
    for hname, rhs in specs.items():
        formula = fe_formula(rhs)
        fit, idx, n_clusters = run_ols(df, formula, cluster_col="Focal_ID")
        terms = [term_result(fit, "Focal_GenAI_Index")]
        if hname == "H2":
            terms.append(term_result(fit, "Focal_GenAI_Index:Focal_RnD_Ratio"))
        if hname == "H3":
            terms.append(term_result(fit, "Focal_GenAI_Index:Power_Pressure"))
        rec = {
            "terms": terms,
            "N": int(fit.nobs),
            "R2": float(fit.rsquared),
            "n_focal_id_clusters": n_clusters,
        }
        RESULTS["cellA"][label][hname] = rec
        tstr = " | ".join(f"{t['term']}={t['coef']:.4f}{t['stars']} se={t['se']:.4f} p={t['p']:.4g}" for t in terms)
        print(f"[{label}] {hname}: {tstr} | N={rec['N']} R2={rec['R2']:.4f} n_FocalID_clusters={n_clusters}")

# --------------------------------------------------------------------------
# CELL C: collapse to focal-firm-year (H1, H2 only)
# --------------------------------------------------------------------------
print("\n" + "=" * 100)
print("CELL C: Collapsed to (Focal_ID, Year) — H1 & H2 only")
print("=" * 100)
RESULTS["cellC"] = {}


def collapse(df):
    agg_cols = ["Focal_ROA", "Focal_GenAI_Index", "Focal_RnD_Ratio"] + CONTROLS
    grouped = df.groupby(["Focal_ID", "Year"], as_index=False)
    collapsed = grouped[agg_cols].mean()
    # attach Focal_Industry (assert invariant within Focal_ID, take first/mode defensively)
    industry_map = df.groupby("Focal_ID")["Focal_Industry"].agg(lambda s: s.mode().iat[0] if not s.mode().empty else s.iloc[0])
    collapsed["Focal_Industry"] = collapsed["Focal_ID"].map(industry_map)
    collapsed["Focal_GenAI_Index:Focal_RnD_Ratio"] = collapsed["Focal_GenAI_Index"] * collapsed["Focal_RnD_Ratio"]
    return collapsed


for label, df in [("main", main_df), ("strict", strict_df)]:
    collapsed = collapse(df)
    n_industry_clusters_collapsed = collapsed["Focal_Industry"].nunique()
    n_focalid_clusters_collapsed = collapsed["Focal_ID"].nunique()
    RESULTS["cellC"][label] = {
        "n_rows_collapsed": int(len(collapsed)),
        "n_industry_clusters_collapsed": int(n_industry_clusters_collapsed),
        "n_focalid_clusters_collapsed": int(n_focalid_clusters_collapsed),
    }
    print(f"[{label}] collapsed rows={len(collapsed)} (from {len(df)}); "
          f"industry clusters on collapsed={n_industry_clusters_collapsed}; focalID clusters on collapsed={n_focalid_clusters_collapsed}")

    specs = {
        "H1": ["Focal_GenAI_Index"] + CONTROLS,
        "H2": ["Focal_GenAI_Index"] + CONTROLS + ["Focal_RnD_Ratio", "Focal_GenAI_Index:Focal_RnD_Ratio"],
    }
    for hname, rhs in specs.items():
        formula = fe_formula(rhs)
        fit, idx, n_clusters = run_ols(collapsed, formula, cluster_col="Focal_Industry")
        terms = [term_result(fit, "Focal_GenAI_Index")]
        if hname == "H2":
            terms.append(term_result(fit, "Focal_GenAI_Index:Focal_RnD_Ratio"))
        rec = {"terms": terms, "N": int(fit.nobs), "R2": float(fit.rsquared), "n_industry_clusters": n_clusters}
        RESULTS["cellC"][label][hname] = rec
        tstr = " | ".join(f"{t['term']}={t['coef']:.4f}{t['stars']} se={t['se']:.4f} p={t['p']:.4g}" for t in terms)
        print(f"[{label}] {hname}: {tstr} | N={rec['N']} R2={rec['R2']:.4f} n_industry_clusters={n_clusters}")
print("[NOTE] H3 skipped for Cell C on both samples: Power_Pressure is dyad-specific (depends on which partner "
      "the focal firm is paired with), so it cannot be meaningfully averaged into a single focal-firm-year value "
      "without discarding the dyadic variation that defines the construct.")

# --------------------------------------------------------------------------
# CELL D: weighted by inverse dyad-count
# --------------------------------------------------------------------------
print("\n" + "=" * 100)
print("CELL D: WLS weighted by 1/dyad_count, industry+year FE, clustered Focal_Industry")
print("=" * 100)
RESULTS["cellD"] = {}
for label, df in [("main", main_df), ("strict", strict_df)]:
    df = df.copy()
    df["dyad_count"] = df.groupby(["Focal_ID", "Year"])["Focal_ID"].transform("size")
    df["inv_dyad_weight"] = 1.0 / df["dyad_count"]
    RESULTS["cellD"][label] = {
        "dyad_count_min": int(df["dyad_count"].min()),
        "dyad_count_median": float(df["dyad_count"].median()),
        "dyad_count_max": int(df["dyad_count"].max()),
    }

    specs = {
        "H1": ["Focal_GenAI_Index"] + CONTROLS,
        "H2": ["Focal_GenAI_Index"] + CONTROLS + ["Focal_RnD_Ratio", "Focal_GenAI_Index:Focal_RnD_Ratio"],
        "H3": ["Focal_GenAI_Index"] + CONTROLS + ["Power_Pressure", "Focal_GenAI_Index:Power_Pressure"],
    }
    for hname, rhs in specs.items():
        formula = fe_formula(rhs)
        # pre-filter explicitly so weights vector aligns 1:1 with rows entering WLS (avoid
        # any misalignment between formula-internal missing='drop' and an externally-passed
        # weights array)
        needed_cols = ["Focal_ROA", "Focal_Industry", "Year", "inv_dyad_weight"] + [
            c for c in rhs if ":" not in c
        ]
        sub = df.dropna(subset=needed_cols).copy()
        fit, idx, n_clusters = run_ols(sub, formula, cluster_col="Focal_Industry", weights_col="inv_dyad_weight")
        terms = [term_result(fit, "Focal_GenAI_Index")]
        if hname == "H2":
            terms.append(term_result(fit, "Focal_GenAI_Index:Focal_RnD_Ratio"))
        if hname == "H3":
            terms.append(term_result(fit, "Focal_GenAI_Index:Power_Pressure"))
        rec = {"terms": terms, "N": int(fit.nobs), "R2": float(fit.rsquared), "n_industry_clusters": n_clusters}
        RESULTS["cellD"][label][hname] = rec
        tstr = " | ".join(f"{t['term']}={t['coef']:.4f}{t['stars']} se={t['se']:.4f} p={t['p']:.4g}" for t in terms)
        print(f"[{label}] {hname}: {tstr} | N={rec['N']} R2={rec['R2']:.4f} n_industry_clusters={n_clusters}")
    print(f"[{label}] dyad_count: min={RESULTS['cellD'][label]['dyad_count_min']} "
          f"median={RESULTS['cellD'][label]['dyad_count_median']} max={RESULTS['cellD'][label]['dyad_count_max']}")

# --------------------------------------------------------------------------
# CELL E: industry+year FE, GenAI LAGGED (isolate timing effect)
# --------------------------------------------------------------------------
print("\n" + "=" * 100)
print("CELL E: C(Focal_Industry)+C(Year) FE, L1_Focal_GenAI_Index (lag only, FE unchanged), cluster Focal_Industry")
print("=" * 100)
RESULTS["cellE"] = {}
for label, df in [("main", main_df), ("strict", strict_df)]:
    rhs = ["L1_Focal_GenAI_Index"] + CONTROLS
    formula = fe_formula(rhs)
    fit, idx, n_clusters = run_ols(df, formula, cluster_col="Focal_Industry")
    term = term_result(fit, "L1_Focal_GenAI_Index")
    rec = {"term": term, "N": int(fit.nobs), "R2": float(fit.rsquared), "n_industry_clusters": n_clusters}
    RESULTS["cellE"][label] = rec
    print(f"[{label}] L1_Focal_GenAI_Index={term['coef']:.4f}{term['stars']} se={term['se']:.4f} p={term['p']:.4g} "
          f"| N={rec['N']} R2={rec['R2']:.4f} n_industry_clusters={n_clusters}")

# --------------------------------------------------------------------------
# CELL F: focal-firm FE, GenAI CONTEMPORANEOUS (isolate FE structure)
# --------------------------------------------------------------------------
print("\n" + "=" * 100)
print("CELL F: C(Focal_ID)+C(Year) FE, Focal_GenAI_Index contemporaneous, cluster Focal_ID")
print("=" * 100)
RESULTS["cellF"] = {}
for label, df in [("main", main_df), ("strict", strict_df)]:
    rhs = ["Focal_GenAI_Index"] + CONTROLS
    formula = fe_formula(rhs, fe_terms=("Focal_ID", "Year"))
    fit, idx, n_clusters = run_ols(df, formula, cluster_col="Focal_ID")
    term = term_result(fit, "Focal_GenAI_Index")
    rec = {"term": term, "N": int(fit.nobs), "R2": float(fit.rsquared), "n_focalid_clusters": n_clusters}
    RESULTS["cellF"][label] = rec
    print(f"[{label}] Focal_GenAI_Index={term['coef']:.4f}{term['stars']} se={term['se']:.4f} p={term['p']:.4g} "
          f"| N={rec['N']} R2={rec['R2']:.4f} n_focalid_clusters={n_clusters}")

# --------------------------------------------------------------------------
# CELL G: focal-firm FE + lagged (replicate historical result)
# --------------------------------------------------------------------------
print("\n" + "=" * 100)
print("CELL G: C(Focal_ID)+C(Year) FE, L1_Focal_GenAI_Index, cluster Focal_ID  [replicates 07_prepare_paper_regression_tables.py Baseline]")
print("=" * 100)
RESULTS["cellG"] = {}
for label, df in [("main", main_df), ("strict", strict_df)]:
    rhs = ["L1_Focal_GenAI_Index"] + CONTROLS
    formula = fe_formula(rhs, fe_terms=("Focal_ID", "Year"))
    fit, idx, n_clusters = run_ols(df, formula, cluster_col="Focal_ID")
    term = term_result(fit, "L1_Focal_GenAI_Index")
    rec = {"term": term, "N": int(fit.nobs), "R2": float(fit.rsquared), "n_focalid_clusters": n_clusters}
    RESULTS["cellG"][label] = rec
    print(f"[{label}] L1_Focal_GenAI_Index={term['coef']:.4f}{term['stars']} se={term['se']:.4f} p={term['p']:.4g} "
          f"| N={rec['N']} R2={rec['R2']:.4f} n_focalid_clusters={n_clusters}")

# --------------------------------------------------------------------------
# R1.2 descriptive statistics (main sample)
# --------------------------------------------------------------------------
print("\n" + "=" * 100)
print("R1.2 DESCRIPTIVE STATISTICS")
print("=" * 100)
RESULTS["R1_2"] = {}
for label, df in [("main", main_df), ("strict", strict_df)]:
    grp_sizes = df.groupby(["Focal_ID", "Year"]).size()
    rec = {
        "n_unique_focalid_year": int(len(grp_sizes)),
        "avg_dyad_rows_per_focalid_year": float(grp_sizes.mean()),
        "dyad_count_min": int(grp_sizes.min()),
        "dyad_count_median": float(grp_sizes.median()),
        "dyad_count_max": int(grp_sizes.max()),
        "total_rows": int(len(df)),
    }
    RESULTS["R1_2"][label] = rec
    print(f"[{label}] unique (Focal_ID,Year) combos={rec['n_unique_focalid_year']} | "
          f"avg dyad rows per firm-year={rec['avg_dyad_rows_per_focalid_year']:.3f} | "
          f"dyad-count distribution: min={rec['dyad_count_min']} median={rec['dyad_count_median']} max={rec['dyad_count_max']}")

# --------------------------------------------------------------------------
# R1.5 mean-centering + lagged R&D interaction
# --------------------------------------------------------------------------
print("\n" + "=" * 100)
print("R1.5 MEAN-CENTERING (H2) + LAGGED R&D INTERACTION")
print("=" * 100)
RESULTS["R1_5"] = {}
for label, df in [("main", main_df), ("strict", strict_df)]:
    df = df.copy()
    genai_mean = df["Focal_GenAI_Index"].mean()
    rnd_mean = df["Focal_RnD_Ratio"].mean()
    df["GenAI_c"] = df["Focal_GenAI_Index"] - genai_mean
    df["RnD_c"] = df["Focal_RnD_Ratio"] - rnd_mean
    df["GenAI_c_x_RnD_c"] = df["GenAI_c"] * df["RnD_c"]

    rhs = ["GenAI_c"] + CONTROLS + ["RnD_c", "GenAI_c_x_RnD_c"]
    formula = fe_formula(rhs)
    fit, idx, n_clusters = run_ols(df, formula, cluster_col="Focal_Industry")
    main_term = term_result(fit, "GenAI_c")
    inter_term = term_result(fit, "GenAI_c_x_RnD_c")
    rec_centered = {
        "main_term": main_term, "inter_term": inter_term,
        "N": int(fit.nobs), "R2": float(fit.rsquared), "n_industry_clusters": n_clusters,
        "genai_mean": float(genai_mean), "rnd_mean": float(rnd_mean),
    }
    print(f"[{label}] MEAN-CENTERED H2: GenAI_c={main_term['coef']:.4f}{main_term['stars']} se={main_term['se']:.4f} p={main_term['p']:.4g} | "
          f"inter={inter_term['coef']:.6f}{inter_term['stars']} se={inter_term['se']:.6f} p={inter_term['p']:.4g} "
          f"| N={rec_centered['N']} R2={rec_centered['R2']:.4f}")

    # lagged R&D interacted with contemporaneous GenAI
    df["GenAI_x_L1RnD"] = df["Focal_GenAI_Index"] * df["L1_Focal_RnD_Ratio"]
    rhs2 = ["Focal_GenAI_Index"] + CONTROLS + ["L1_Focal_RnD_Ratio", "GenAI_x_L1RnD"]
    formula2 = fe_formula(rhs2)
    fit2, idx2, n_clusters2 = run_ols(df, formula2, cluster_col="Focal_Industry")
    main_term2 = term_result(fit2, "Focal_GenAI_Index")
    inter_term2 = term_result(fit2, "GenAI_x_L1RnD")
    rec_lagged = {
        "main_term": main_term2, "inter_term": inter_term2,
        "N": int(fit2.nobs), "R2": float(fit2.rsquared), "n_industry_clusters": n_clusters2,
    }
    print(f"[{label}] LAGGED-R&D x CONTEMPORANEOUS GenAI: GenAI={main_term2['coef']:.4f}{main_term2['stars']} se={main_term2['se']:.4f} p={main_term2['p']:.4g} | "
          f"inter(GenAI x L1_RnD)={inter_term2['coef']:.4f}{inter_term2['stars']} se={inter_term2['se']:.4f} p={inter_term2['p']:.4g} "
          f"| N={rec_lagged['N']} R2={rec_lagged['R2']:.4f}")

    RESULTS["R1_5"][label] = {"centered": rec_centered, "lagged_rnd": rec_lagged}

# --------------------------------------------------------------------------
# Within-firm variation diagnostic (main sample; also computed for strict FYI)
# --------------------------------------------------------------------------
print("\n" + "=" * 100)
print("WITHIN-FIRM VARIATION DIAGNOSTIC")
print("=" * 100)
RESULTS["within_firm_variation"] = {}
for label, df in [("main", main_df), ("strict", strict_df)]:
    fy = df[["Focal_ID", "Year", "Focal_GenAI_Index"]].drop_duplicates(subset=["Focal_ID", "Year"])
    n_firms = fy["Focal_ID"].nunique()
    year_counts = fy.groupby("Focal_ID")["Year"].nunique()
    n_1year = int((year_counts == 1).sum())
    multi_year_ids = year_counts[year_counts >= 2].index
    nonzero_var_count = 0
    for fid in multi_year_ids:
        vals = fy.loc[fy["Focal_ID"] == fid, "Focal_GenAI_Index"]
        if vals.nunique(dropna=True) > 1:
            nonzero_var_count += 1
    pct_nonzero = 100.0 * nonzero_var_count / n_firms
    rec = {
        "n_firms": int(n_firms),
        "n_firms_1year": n_1year,
        "n_firms_multiyear": int(len(multi_year_ids)),
        "n_firms_nonzero_within_variance": int(nonzero_var_count),
        "pct_nonzero_within_variance": float(pct_nonzero),
    }
    RESULTS["within_firm_variation"][label] = rec
    print(f"[{label}] total unique Focal_ID={n_firms} | firms with only 1 year of data={n_1year} "
          f"({100*n_1year/n_firms:.1f}%) | firms with >=2 years={len(multi_year_ids)} | "
          f"of those, firms with nonzero within-firm GenAI variance={nonzero_var_count} "
          f"| share of ALL firms with usable within variation={pct_nonzero:.1f}%")

# --------------------------------------------------------------------------
# MDE for Cell F and Cell G
# --------------------------------------------------------------------------
print("\n" + "=" * 100)
print("MINIMUM DETECTABLE EFFECT (MDE = 2.8 x SE)")
print("=" * 100)
RESULTS["MDE"] = {}
PUBLISHED_H1 = {"main": 0.0146, "strict": 0.0123}
for label in ["main", "strict"]:
    se_f = RESULTS["cellF"][label]["term"]["se"]
    se_g = RESULTS["cellG"][label]["term"]["se"]
    mde_f = 2.8 * se_f
    mde_g = 2.8 * se_g
    bench = PUBLISHED_H1[label]
    rec = {
        "se_cellF": se_f, "mde_cellF": mde_f, "mde_cellF_lt_bench": mde_f < bench,
        "se_cellG": se_g, "mde_cellG": mde_g, "mde_cellG_lt_bench": mde_g < bench,
        "benchmark_published_H1": bench,
    }
    RESULTS["MDE"][label] = rec
    print(f"[{label}] Cell F: SE={se_f:.4f} -> MDE={mde_f:.4f} | published |H1|={bench} -> "
          f"{'MDE < published (null IS informative)' if mde_f < bench else 'MDE > published (null is UNINFORMATIVE)'}")
    print(f"[{label}] Cell G: SE={se_g:.4f} -> MDE={mde_g:.4f} | published |H1|={bench} -> "
          f"{'MDE < published (null IS informative)' if mde_g < bench else 'MDE > published (null is UNINFORMATIVE)'}")

# --------------------------------------------------------------------------
# dump
# --------------------------------------------------------------------------
with open(SCRATCH / "results_main_grid.json", "w") as f:
    json.dump(RESULTS, f, indent=2, default=str)

print("\n\nDONE. JSON dumped to results_main_grid.json")
