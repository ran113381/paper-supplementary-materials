"""
Corrected Cell C: use the Focal_Industry value actually recorded within each
(Focal_ID, Year) group (already confirmed invariant at that level - 0 violations)
instead of the firm's all-time modal industry (which could be wrong for the ~15
firms whose recorded industry changes across years).
"""
from pathlib import Path
import json
import pandas as pd
import statsmodels.formula.api as smf

PROC_DIR = Path(r"E:\Supply_Chain_Project\data\processed_data")
MAIN_PACK = PROC_DIR / "08A_main_regression_package.xlsx"
STRICT_PACK = PROC_DIR / "08B_strict_regression_package.xlsx"
SCRATCH = Path(r"C:\Users\asus\AppData\Local\Temp\claude\E--Supply---SHAP\ff49c3f8-4243-4540-abcd-8d73380c708c\scratchpad")
CONTROLS = ['Focal_Size', 'Focal_Lev', 'Focal_Age', 'Focal_CashFlow', 'Focal_SoE', 'Focal_HHI',
            'Partner_Size', 'Partner_Lev', 'Partner_ROA']


def load(path, sheet):
    df = pd.read_excel(path, sheet_name=sheet, dtype={"Focal_ID": str, "Partner_ID": str})
    df['Focal_Industry'] = df['Focal_Industry'].astype(str)
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df['Supplier_Dominance'] = (-pd.to_numeric(df['Power_Diff'], errors='coerce')).clip(lower=0)
    df['Partner_Ahead'] = (pd.to_numeric(df['Partner_GenAI_Index'], errors='coerce') - pd.to_numeric(df['Focal_GenAI_Index'], errors='coerce')).clip(lower=0)
    df['Power_Pressure'] = df['Supplier_Dominance'] * df['Partner_Ahead']
    return df


def stars(p):
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""


def term_result(fit, term):
    return {"term": term, "coef": float(fit.params[term]), "se": float(fit.bse[term]),
            "p": float(fit.pvalues[term]), "stars": stars(fit.pvalues[term])}


def run_ols(df, formula, cluster_col):
    model = smf.ols(formula=formula, data=df, missing='drop')
    idx = model.data.row_labels
    groups = df.loc[idx, cluster_col]
    fit = model.fit(cov_type='cluster', cov_kwds={'groups': groups})
    return fit, int(groups.nunique())


def collapse_fixed(df):
    agg_dict = {c: 'mean' for c in ["Focal_ROA", "Focal_GenAI_Index", "Focal_RnD_Ratio"] + CONTROLS}
    agg_dict['Focal_Industry'] = 'first'  # already confirmed invariant within (Focal_ID, Year)
    collapsed = df.groupby(["Focal_ID", "Year"], as_index=False).agg(agg_dict)
    collapsed["Focal_GenAI_Index:Focal_RnD_Ratio"] = collapsed["Focal_GenAI_Index"] * collapsed["Focal_RnD_Ratio"]
    return collapsed


def fe_formula(rhs_terms):
    return "Focal_ROA ~ " + " + ".join(rhs_terms + ["C(Focal_Industry)", "C(Year)"])


RESULTS = {}
for label, path, sheet in [("main", MAIN_PACK, "main_winsorized"), ("strict", STRICT_PACK, "strict_winsorized")]:
    df = load(path, sheet)
    collapsed = collapse_fixed(df)
    n_ind = collapsed["Focal_Industry"].nunique()
    n_fid = collapsed["Focal_ID"].nunique()
    print(f"[{label}] collapsed rows={len(collapsed)} industry_clusters={n_ind} focalid_clusters={n_fid}")

    specs = {
        "H1": ["Focal_GenAI_Index"] + CONTROLS,
        "H2": ["Focal_GenAI_Index"] + CONTROLS + ["Focal_RnD_Ratio", "Focal_GenAI_Index:Focal_RnD_Ratio"],
    }
    RESULTS[label] = {"n_rows_collapsed": int(len(collapsed)), "n_industry_clusters_collapsed": int(n_ind), "n_focalid_clusters_collapsed": int(n_fid)}
    for hname, rhs in specs.items():
        formula = fe_formula(rhs)
        fit, n_clusters = run_ols(collapsed, formula, "Focal_Industry")
        terms = [term_result(fit, "Focal_GenAI_Index")]
        if hname == "H2":
            terms.append(term_result(fit, "Focal_GenAI_Index:Focal_RnD_Ratio"))
        rec = {"terms": terms, "N": int(fit.nobs), "R2": float(fit.rsquared), "n_industry_clusters": n_clusters}
        RESULTS[label][hname] = rec
        tstr = " | ".join(f"{t['term']}={t['coef']:.6f}{t['stars']} se={t['se']:.6f} p={t['p']:.4g}" for t in terms)
        print(f"[{label}] {hname}: {tstr} | N={rec['N']} R2={rec['R2']:.4f}")

with open(SCRATCH / "results_cellC_fixed.json", "w") as f:
    json.dump(RESULTS, f, indent=2, default=str)
print("DONE")
