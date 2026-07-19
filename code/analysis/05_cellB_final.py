"""
Cell B FINAL: hand-rolled CGM two-way (Focal_ID x Year) cluster-robust variance,
main sample (required) + strict sample (optional, time allows).

Reports SE plus p-values under two conventions:
  (a) z/normal reference (matches this report's other cells' statsmodels default convention,
      which uses df_resid = N-K, indistinguishable from normal at this N)
  (b) CGM(2011)-recommended conservative t-reference with df = min(G_dim1, G_dim2) - 1,
      the standard practical guidance specifically for the two-way case with a thin dimension
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats as sstats

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


def cgm_twoway(df, formula, dim1="Focal_ID", dim2="Year"):
    model = smf.ols(formula=formula, data=df, missing='drop')
    base_fit = model.fit()
    idx = model.data.row_labels
    sub = df.loc[idx].copy()
    sub["_intersect"] = sub[dim1].astype(str) + "___" + sub[dim2].astype(str)

    fit1 = model.fit(cov_type='cluster', cov_kwds={'groups': sub[dim1], 'use_correction': True})
    fit2 = model.fit(cov_type='cluster', cov_kwds={'groups': sub[dim2], 'use_correction': True})
    fit12 = model.fit(cov_type='cluster', cov_kwds={'groups': sub["_intersect"], 'use_correction': True})

    V1, V2, V12 = fit1.cov_params(), fit2.cov_params(), fit12.cov_params()
    V_2way = V1 + V2 - V12

    vals, vecs = np.linalg.eigh(V_2way.values)
    psd_note = "PSD OK"
    if (vals < 0).any():
        vals_clipped = np.clip(vals, 0, None)
        V_2way = pd.DataFrame(vecs @ np.diag(vals_clipped) @ vecs.T, index=V_2way.index, columns=V_2way.columns)
        psd_note = "negative eigenvalues clipped to 0"

    se_series = pd.Series(np.sqrt(np.diag(V_2way)), index=V_2way.index)
    n1, n2, n12 = sub[dim1].nunique(), sub[dim2].nunique(), sub["_intersect"].nunique()
    dof_conservative = min(n1, n2) - 1
    dof_resid = int(base_fit.df_resid)

    out = {}
    for term in base_fit.params.index:
        coef = base_fit.params[term]
        se = se_series[term]
        t = coef / se
        p_conservative = 2 * (1 - sstats.t.cdf(abs(t), dof_conservative))
        p_normal = 2 * (1 - sstats.norm.cdf(abs(t)))
        out[term] = {
            "coef": float(coef), "se": float(se), "t": float(t),
            "p_conservative_df9": float(p_conservative),
            "p_normal_approx": float(p_normal),
        }
    meta = {"N": int(fit1.nobs), "n_dim1": n1, "n_dim2": n2, "n_intersect": n12,
            "dof_conservative": dof_conservative, "dof_resid": dof_resid, "psd_note": psd_note}
    return out, meta


RESULTS = {}
specs = {
    "H1": lambda: "Focal_ROA ~ Focal_GenAI_Index + " + " + ".join(CONTROLS) + " + C(Focal_Industry) + C(Year)",
    "H2": lambda: "Focal_ROA ~ Focal_GenAI_Index + " + " + ".join(CONTROLS) + " + Focal_RnD_Ratio + Focal_GenAI_Index:Focal_RnD_Ratio + C(Focal_Industry) + C(Year)",
    "H3": lambda: "Focal_ROA ~ Focal_GenAI_Index + " + " + ".join(CONTROLS) + " + Power_Pressure + Focal_GenAI_Index:Power_Pressure + C(Focal_Industry) + C(Year)",
}
term_of_interest = {"H1": ["Focal_GenAI_Index"],
                     "H2": ["Focal_GenAI_Index", "Focal_GenAI_Index:Focal_RnD_Ratio"],
                     "H3": ["Focal_GenAI_Index", "Focal_GenAI_Index:Power_Pressure"]}

for label, path, sheet in [("main", MAIN_PACK, "main_winsorized"), ("strict", STRICT_PACK, "strict_winsorized")]:
    df = load(path, sheet)
    RESULTS[label] = {}
    print("=" * 100)
    print(f"CELL B HAND-ROLLED CGM TWO-WAY (Focal_ID x Year) -- {label} sample")
    print("=" * 100)
    for hname, fbuilder in specs.items():
        formula = fbuilder()
        results, meta = cgm_twoway(df, formula)
        RESULTS[label][hname] = {"meta": meta, "terms": {t: results[t] for t in term_of_interest[hname]}}
        print(f"\n--- {hname} --- N={meta['N']} | Focal_ID clusters={meta['n_dim1']} Year clusters={meta['n_dim2']} "
              f"intersection groups={meta['n_intersect']} | conservative dof=min(G)-1={meta['dof_conservative']} | {meta['psd_note']}")
        for t in term_of_interest[hname]:
            r = results[t]
            print(f"  {t}: coef={r['coef']:.4f} se={r['se']:.4f} | "
                  f"p(normal approx)={r['p_normal_approx']:.4g}{stars(r['p_normal_approx'])} | "
                  f"p(conservative t, df={meta['dof_conservative']})={r['p_conservative_df9']:.4g}{stars(r['p_conservative_df9'])}")

with open(SCRATCH / "results_cellB.json", "w") as f:
    json.dump(RESULTS, f, indent=2, default=str)
print("\nDONE")
