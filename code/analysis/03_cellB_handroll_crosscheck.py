"""
Hand-rolled Cameron-Gelbach-Miller (2011) two-way cluster-robust variance,
as a cross-check against the statspai hdfe_ols multiway_cluster result.

V_2way = V_cluster(Focal_ID) + V_cluster(Year) - V_cluster(Focal_ID x Year)
"""
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

PROC_DIR = Path(r"E:\Supply_Chain_Project\data\processed_data")
MAIN_PACK = PROC_DIR / "08A_main_regression_package.xlsx"
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
    idx = model.data.row_labels
    sub = df.loc[idx].copy()
    sub["_intersect"] = sub[dim1].astype(str) + "___" + sub[dim2].astype(str)

    fit1 = model.fit(cov_type='cluster', cov_kwds={'groups': sub[dim1], 'use_correction': True})
    fit2 = model.fit(cov_type='cluster', cov_kwds={'groups': sub[dim2], 'use_correction': True})
    fit12 = model.fit(cov_type='cluster', cov_kwds={'groups': sub["_intersect"], 'use_correction': True})

    V1 = fit1.cov_params()
    V2 = fit2.cov_params()
    V12 = fit12.cov_params()
    V_2way = V1 + V2 - V12

    # PSD safety: eigen-clip negative eigenvalues (standard CGM practical fix)
    vals, vecs = np.linalg.eigh(V_2way.values)
    if (vals < 0).any():
        vals_clipped = np.clip(vals, 0, None)
        V_2way_psd = vecs @ np.diag(vals_clipped) @ vecs.T
        V_2way = pd.DataFrame(V_2way_psd, index=V_2way.index, columns=V_2way.columns)
        psd_note = "NEGATIVE EIGENVALUES CLIPPED"
    else:
        psd_note = "PSD OK (no clipping needed)"

    se = np.sqrt(np.diag(V_2way))
    se_series = pd.Series(se, index=V_2way.index)

    n_dim1 = sub[dim1].nunique()
    n_dim2 = sub[dim2].nunique()
    n_intersect = sub["_intersect"].nunique()

    from scipy import stats as sstats
    params = model.fit().params
    results = {}
    for term in params.index:
        t = params[term] / se_series[term]
        # conservative df = min(G) - 1 per CGM guidance
        dof = min(n_dim1, n_dim2) - 1
        p = 2 * (1 - sstats.t.cdf(abs(t), dof))
        results[term] = {"coef": params[term], "se": se_series[term], "t": t, "p": p}
    return results, {"n_dim1": n_dim1, "n_dim2": n_dim2, "n_intersect": n_intersect, "psd_note": psd_note, "N": int(fit1.nobs)}


main_df = load(MAIN_PACK, "main_winsorized")

print("=" * 100)
print("HAND-ROLLED CGM TWO-WAY CLUSTER CROSS-CHECK (main sample)")
print("=" * 100)

specs = {
    "H1": "Focal_ROA ~ Focal_GenAI_Index + " + " + ".join(CONTROLS) + " + C(Focal_Industry) + C(Year)",
    "H2": "Focal_ROA ~ Focal_GenAI_Index + " + " + ".join(CONTROLS) + " + Focal_RnD_Ratio + Focal_GenAI_Index:Focal_RnD_Ratio + C(Focal_Industry) + C(Year)",
    "H3": "Focal_ROA ~ Focal_GenAI_Index + " + " + ".join(CONTROLS) + " + Power_Pressure + Focal_GenAI_Index:Power_Pressure + C(Focal_Industry) + C(Year)",
}

for hname, formula in specs.items():
    results, meta = cgm_twoway(main_df, formula)
    print(f"\n--- {hname} --- N={meta['N']} clusters: Focal_ID={meta['n_dim1']} Year={meta['n_dim2']} intersection={meta['n_intersect']} | {meta['psd_note']}")
    focal_r = results["Focal_GenAI_Index"]
    print(f"  Focal_GenAI_Index: coef={focal_r['coef']:.4f} se={focal_r['se']:.4f} p(conservative dof)={focal_r['p']:.4g}{stars(focal_r['p'])}")
    if hname == "H2":
        r = results["Focal_GenAI_Index:Focal_RnD_Ratio"]
        print(f"  Interaction (GenAI x RnD): coef={r['coef']:.4f} se={r['se']:.4f} p={r['p']:.4g}{stars(r['p'])}")
    if hname == "H3":
        r = results["Focal_GenAI_Index:Power_Pressure"]
        print(f"  Interaction (GenAI x PowerPressure): coef={r['coef']:.6f} se={r['se']:.6f} p={r['p']:.4g}{stars(r['p'])}")

print("\nDONE")
