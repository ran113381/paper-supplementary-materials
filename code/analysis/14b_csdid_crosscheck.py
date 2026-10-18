"""C7: (1) gate: rerun R/code/09 event study (Figure 9) on the 08A panel; (2) Callaway-Sant'Anna (csdid) with
never-treated and not-yet-treated controls; group-time ATT, event-time aggregation, pre-trend Wald.
Input : S/data/processed_data/08A_main_regression_package.xlsx; R/code/09_run_did_and_placebo.py (exec'd without its mkdir side-effects)
Output: c7_*.csv, stdout RESULTS
"""
import re, sys, warnings, numpy as np, pandas as pd
from scipy import stats
warnings.filterwarnings("ignore")

R = r"E:/paper2  daxiu/73ae4696cf54747044a03a936c4bb958_744934475e1139b8c27898b82ae5bbf0_8/paper2_github_replication"
OUT = r"E:/論文投稿  送審/paper2/R3_work/E_valid_shap_es"
src = open(R + "/code/09_run_did_and_placebo.py", encoding="utf-8").read()
src = src.replace("PREVIEW_DIR.mkdir(parents=True, exist_ok=True)", "").replace("DERIVED_DIR.mkdir(parents=True, exist_ok=True)", "")
src = src.replace("if __name__ == \"__main__\":\n    main()", "")
ns = {"__file__": R + "/code/09_run_did_and_placebo.py", "__name__": "m09"}
exec(compile(src, "09", "exec"), ns)

df = pd.read_excel(r"E:/Supply_Chain_Project/data/processed_data/08A_main_regression_package.xlsx",
                   sheet_name="main_winsorized", dtype={"Focal_ID": str, "Partner_ID": str})
panel = ns["build_focal_year_panel"](df)
ev = ns["run_event_study"](panel)
print("=== RESULTS ===")
print("GATE Figure 9 rerun (R/code/09):")
print(ev.round(4).to_string(index=False))
c0 = ev.loc[ev.event_time == 0, "coef"].iloc[0]; c1 = ev.loc[ev.event_time == 1, "coef"].iloc[0]
samp = panel[(panel.LateTreated == 1) | (panel.NeverTreated == 1)]
print(f"sample N={len(samp)} firms={samp.Focal_ID.nunique()} (expect 734/348)")
gate = round(c0, 4) == -0.0130 and round(c1, 4) == -0.0204 and len(samp) == 734 and samp.Focal_ID.nunique() == 348
print("GATE_PASS", gate)
if not gate:
    print("=== END RESULTS ==="); sys.exit(0)

# ---- structure facts
ft = samp.drop_duplicates("Focal_ID")
print("cohort sizes (firms): ", ft.FirstTreatYear.value_counts(dropna=False).to_dict())
print("firm-years by Year x cohort:\n", pd.crosstab(samp.Year, samp.FirstTreatYear.fillna(0)).to_string())
print("firms excluded from event-study sample (first disclosure <=2022):", int(((panel.FirstTreatYear < 2023)).groupby(panel.Focal_ID).any().sum()))
cnt = samp.groupby("Focal_ID").Year.count()
print("years per firm in sample: mean=%.4f, min=%d, max=%d; balanced(10 yrs) firms=%d" % (cnt.mean(), cnt.min(), cnt.max(), (cnt == 10).sum()))
# relative periods outside window [-4..+1] folded into reference
lt = samp[samp.LateTreated == 1].copy(); lt["et"] = lt.Year - lt.FirstTreatYear
print("late-treated firm-years by event time:", lt.et.value_counts().sort_index().to_dict())
print("late-treated obs with et<-4 (not dummied -> absorbed into baseline with t=-1):", int((lt.et < -4).sum()))

# ---- Callaway-Sant'Anna
from csdid.att_gt import ATTgt
d = samp.copy().reset_index(drop=True)
d["idn"] = pd.factorize(d.Focal_ID)[0] + 1
d["g"] = d.FirstTreatYear.fillna(0).astype(int)
ctrl = ["Focal_Size", "Focal_Lev", "Focal_Age", "Focal_CashFlow", "Focal_SoE", "Focal_HHI",
        "Partner_Size_mean", "Partner_Lev_mean", "Partner_ROA_mean"]
dd = d.dropna(subset=["Focal_ROA"] + ctrl).copy()
print("CS sample after dropping NaN controls:", len(dd), "firms", dd.idn.nunique())

def run(label, cg, xf, data):
    np.random.seed(42)
    m = ATTgt(yname="Focal_ROA", tname="Year", idname="idn", gname="g", data=data, control_group=cg,
              xformla=xf, panel=True, allow_unbalanced_panel=True, clustervar="idn", biters=2000, cband=False)
    m.fit(est_method="dr", base_period="varying", bstrap=True)
    r = m.results
    gt = pd.DataFrame({"g": r["group"], "t": r["year"], "att": r["att"], "se": r["se"]})
    gt["p"] = 2 * (1 - stats.norm.cdf(np.abs(gt.att / gt.se)))
    # pre-trend Wald on pre ATT(g,t) (t<g)
    inf = m.MP["inffunc"]["inffunc"]; n = inf.shape[0]
    pre = (gt.t < gt.g).values & np.isfinite(gt.att.values)
    V = np.cov(inf[:, pre].T, ddof=1) / n if pre.sum() > 1 else None
    if V is not None:
        a = gt.att.values[pre]
        Vp = np.linalg.pinv(V, rcond=1e-8); W = float(a @ Vp @ a); k = int(np.linalg.matrix_rank(V, tol=1e-10)); wp = 1 - stats.chi2.cdf(W, k)
    else:
        W, k, wp = np.nan, 0, np.nan
    print(f"\n### {label} | control={cg} | covariates={'none' if xf is None else 'yes'} | N rows={len(data)} firms={data.idn.nunique()}")
    print(gt.round(4).to_string(index=False))
    print(f"pre-trend joint Wald (varying base, {int(pre.sum())} pre cells): W={W:.4f} df={k} p={wp:.4f}")
    res = {"label": label}
    for typ in ["simple", "dynamic", "group"]:
        try:
            a = m.aggte(typec=typ, bstrap=True, biters=2000, cband=False, clustervars="idn")
            e = a.atte
            if typ=="simple": print("  aggte keys:", list(e.keys()))
            if typ == "dynamic":
                dyn = pd.DataFrame({"e": e["egt"], "att": e["att_egt"], "se": np.ravel(e["se_egt"])})
                dyn["p"] = 2 * (1 - stats.norm.cdf(np.abs(dyn.att / dyn.se)))
                print("event-time aggregation (dynamic):"); print(dyn.round(4).to_string(index=False))
                dyn.to_csv(f"{OUT}/c7_cs_dynamic_{label}.csv", index=False, encoding="utf-8-sig")
                pe = dyn[dyn.e < 0]
                print(f"  (pre-period aggregate coefficients: {len(pe)}; post: {(dyn.e>=0).sum()})")
            elif typ == "simple":
                print(f"overall (simple) ATT = {e['overall_att']:.4f}, SE = {e['overall_se']:.4f}")
            else:
                print("group aggregation:", {int(k): (round(float(v), 4)) for k, v in zip(e["egt"], e["att_egt"])},
                      "overall(group)=%.4f se=%.4f" % (e["overall_att"], e["overall_se"]))
        except Exception as ex:
            print(f"aggte {typ} failed: {type(ex).__name__}: {ex}")
    gt.to_csv(f"{OUT}/c7_cs_gt_{label}.csv", index=False, encoding="utf-8-sig")

xf = "Focal_ROA ~ Focal_Size + Focal_Lev"
for lab, cg, f in [("never_nocov", "nevertreated", None), ("notyet_nocov", "notyettreated", None),
                   ("never_cov2", "nevertreated", xf), ("notyet_cov2", "notyettreated", xf)]:
    try:
        run(lab, cg, f, dd)
    except Exception as ex:
        print("### " + lab + " FAILED: " + type(ex).__name__ + ": " + str(ex))
print("=== END RESULTS ===")
