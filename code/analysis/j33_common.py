"""j33_common.py -- shared helpers for J33 runs (paper2 R3 pre-merge checks).
Purpose : load 08A main_winsorized (original) or the CNRDS-recomputed variants (B_truncation csv -> re-winsorize 1/99 as in run_B.py),
          build G / PP / GxPP / lagged R&D, fit OLS (industry + year FE, cluster-robust), year wild-cluster bootstrap (pyfixest, 9999, seed 42, type 11).
Inputs  : S\\data\\processed_data\\08A_main_regression_package.xlsx ; R3_work\\B_truncation\\main_raw_recomputed_variant{A,B}.csv
Outputs : none (library). Read-only on S, R, and all existing R3_work files.
Upstream: A_H3\\a_common.py, D_H2_T14\\common_d.py, B_truncation\\run_B.py (logic copied). Downstream: f1..f11, g2, g3 scripts.
"""
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
import statsmodels.formula.api as smf

W = r"E:\論文投稿  送審\paper2\R3_work"
OUT = os.path.join(W, "J33_runs")
S = r"E:\Supply_Chain_Project\data\processed_data"
PACK = S + r"\08A_main_regression_package.xlsx"
R = "E:/paper2  daxiu/73ae4696cf54747044a03a936c4bb958_744934475e1139b8c27898b82ae5bbf0_8/paper2_github_replication/"
CTRL = ['Focal_Size', 'Focal_Lev', 'Focal_Age', 'Focal_CashFlow', 'Focal_SoE', 'Focal_HHI', 'Partner_Size', 'Partner_Lev', 'Partner_ROA']
CS = " + ".join(CTRL)
FE = " | Focal_Industry + Year"

WINSOR_VARS = [
    "Focal_Size", "Focal_Lev", "Focal_ROA", "Focal_Age", "Focal_Growth", "Focal_CashFlow",
    "Focal_TobinQ", "Focal_RnD_Ratio", "Focal_AdminExp_Ratio",
    "Partner_Size", "Partner_Lev", "Partner_ROA", "Partner_Age", "Partner_Growth",
    "Partner_CashFlow", "Partner_TobinQ", "Partner_RnD_Ratio", "Partner_AdminExp_Ratio",
    "Rela_Purchase_Ln", "Ln_Distance", "Ln_Dyad_Duration", "Power_Diff",
    "Focal_GenAI_Index", "Focal_GenAI_Index_Overlap", "Partner_GenAI_Index", "Partner_GenAI_Index_Overlap",
]  # identical to run_B.py:29-36


class Tee:
    def __init__(self, path):
        self.f = open(path, "w", encoding="utf-8"); self.o = sys.stdout
    def write(self, s): self.f.write(s); self.o.write(s)
    def flush(self): self.f.flush(); self.o.flush()


def winsorize_series(s, lo=0.01, hi=0.99):
    s = pd.to_numeric(s, errors="coerce").astype(float); nm = s.dropna()
    return s if nm.empty else s.clip(lower=nm.quantile(lo), upper=nm.quantile(hi))


def winsorize_df(df):
    w = df.copy()
    for c in WINSOR_VARS:
        if c in w.columns: w[c] = winsorize_series(w[c])
    return w


def load_raw():
    return pd.read_excel(PACK, sheet_name="main_raw", dtype={"Focal_ID": str, "Partner_ID": str})


def load_orig():
    return pd.read_excel(PACK, sheet_name="main_winsorized", dtype={"Focal_ID": str, "Partner_ID": str})


def load_variant(v):
    """v in {'orig','A','B'}; returns the winsorized 1,017-row frame."""
    if v == "orig": return load_orig()
    raw = pd.read_csv(os.path.join(W, "B_truncation", f"main_raw_recomputed_variant{v}.csv"), dtype={"Focal_ID": str, "Partner_ID": str}, encoding="utf-8-sig")
    return winsorize_df(raw)


def prep(df):
    d = df.copy()
    d["Year"] = pd.to_numeric(d["Year"]); d["Focal_Industry"] = d["Focal_Industry"].astype(str)
    d["Focal_SoE"] = pd.to_numeric(d["Focal_SoE"], errors="coerce")
    lk = d[["Focal_ID", "Year", "Focal_RnD_Ratio"]].drop_duplicates(["Focal_ID", "Year"]).sort_values(["Focal_ID", "Year"])
    lk["L1_RnD"] = lk.groupby("Focal_ID")["Focal_RnD_Ratio"].shift(1); lk["prev_year"] = lk.groupby("Focal_ID")["Year"].shift(1)
    d = d.merge(lk[["Focal_ID", "Year", "L1_RnD", "prev_year"]], on=["Focal_ID", "Year"], how="left")
    d["gap_lag"] = d.Year - d.prev_year
    d["SD"] = (-pd.to_numeric(d.Power_Diff, errors="coerce")).clip(lower=0)
    d["PA"] = (pd.to_numeric(d.Partner_GenAI_Index, errors="coerce") - pd.to_numeric(d.Focal_GenAI_Index, errors="coerce")).clip(lower=0)
    d["PP"] = d.SD * d.PA
    d["G"] = pd.to_numeric(d.Focal_GenAI_Index, errors="coerce"); d["R"] = d.Focal_RnD_Ratio
    d["GxR"] = d.G * d.R; d["GxL"] = d.G * d.L1_RnD; d["GxPP"] = d.G * d.PP
    return d


def fit_sm(d, terms, cl="Focal_Industry"):
    f = "Focal_ROA ~ " + " + ".join(terms + CTRL + ["C(Focal_Industry)", "C(Year)"])
    m = smf.ols(f, data=d, missing="drop"); idx = m.data.row_labels
    r = m.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d.loc[idx, cl])[0]})
    return r, d.loc[idx]


def year_boot(d, terms, key, reps=9999, seed=42):
    import pyfixest as pf
    fm = "Focal_ROA ~ " + " + ".join(terms + CTRL) + FE
    fit = pf.feols(fm, data=d, vcov={"CRV1": "Year"})
    bt = fit.wildboottest(reps=reps, cluster="Year", param=key, seed=seed, bootstrap_type="11")
    return float(bt["Pr(>|t|)"]), int(fit._N)


def run_row(label, d, terms, key, boot=True):
    ri, u = fit_sm(d, terms, "Focal_Industry"); rf, _ = fit_sm(d, terms, "Focal_ID")
    pb, npf = year_boot(d, terms, key) if boot else (np.nan, 0)
    row = dict(model=label, term=key, N=int(ri.nobs), coef=float(ri.params[key]), se_ind=float(ri.bse[key]), p_ind=float(ri.pvalues[key]),
               se_focal=float(rf.bse[key]), p_focal=float(rf.pvalues[key]), p_yearboot=pb, k_of_1024=pb * 1024, N_pyfixest=npf)
    print(f"{label:44s} {key:5s} N={row['N']:4d} coef={row['coef']:.4f} se_ind={row['se_ind']:.4f} p_ind={row['p_ind']:.4f} | se_focal={row['se_focal']:.4f} p_focal={row['p_focal']:.4f} | p_yearBoot={pb:.4f} (k={pb*1024:.2f}/1024; N_pf={npf})")
    return row


def sha12(path):
    import hashlib
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:12]


def boot_suite(d, tag, with_formula_path=True):
    """H1 / H2 contemporaneous (full) / H2 lagged (585) / H2 strict t-1 (498) / H3 (budget-column path); H3 formula path optional."""
    rows = []
    com = d.dropna(subset=["L1_RnD"]).copy(); strict = com[com.gap_lag == 1].copy()
    rows.append(run_row(f"{tag} H1 G", d, ["G"], "G"))
    rows.append(run_row(f"{tag} H2 contemp GxR (full)", d, ["G", "R", "GxR"], "GxR"))
    rows.append(run_row(f"{tag} H2 lagged GxL (common)", com, ["G", "L1_RnD", "GxL"], "GxL"))
    rows.append(run_row(f"{tag} H2 lagged GxL (strict t-1)", strict, ["G", "L1_RnD", "GxL"], "GxL"))
    rows.append(run_row(f"{tag} H3 GxPP budget-column path", d, ["G", "PP", "GxPP"], "GxPP"))
    if with_formula_path:
        import pyfixest as pf
        fm = "Focal_ROA ~ G + PP + G:PP + " + CS + FE
        fit = pf.feols(fm, data=d, vcov={"CRV1": "Year"})
        key = [k for k in fit.coef().index if ":" in k][0]
        bt = fit.wildboottest(reps=9999, cluster="Year", param=key, seed=42, bootstrap_type="11")
        pb = float(bt["Pr(>|t|)"])
        print(f"{tag} H3 formula-interaction path (param {key}) coef={fit.coef()[key]:.4f} p_yearBoot={pb:.4f} (k={pb*1024:.2f}/1024; N_pf={int(fit._N)})")
        rows.append(dict(model=f"{tag} H3 GxPP formula-interaction path", term=key, N=int(fit._N), coef=float(fit.coef()[key]), p_yearboot=pb, k_of_1024=pb * 1024))
    return rows
