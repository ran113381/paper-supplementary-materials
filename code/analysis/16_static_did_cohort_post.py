"""g2_static_did.py -- D16-2. Static TWFE DID (R code\09 run_twfe_did): original coding Post = Year>=2023 vs cohort-based recode (Post = Year >= own FirstTreatYear; 2024 cohort not coded as treated in 2023).
Self-check: original coding must reproduce the archived output of the same script (S\data\processed_data\archive_intermediate\derived_results\12_causal_identification_results.xlsx, sheets main_twfe_did / strict_twfe_did, TreatPost row; N in *_meta).
Inputs: S 08A main_winsorized, S 08B strict_winsorized; R code\09 functions exec'd verbatim. Outputs: g2_static_did.log, g2_static_did.csv. Read-only on S, R."""
import sys; sys.path.insert(0, r"E:\論文投稿  送審\paper2\R3_work\J33_runs")
from j33_common import *
sys.stdout = Tee(OUT + r"\g2_static_did.log")
src = open(R + "code/09_run_did_and_placebo.py", encoding="utf-8").read()
src = src.replace("PREVIEW_DIR.mkdir(parents=True, exist_ok=True)", "").replace("DERIVED_DIR.mkdir(parents=True, exist_ok=True)", "").replace('if __name__ == "__main__":\n    main()', "")
ns = {"__file__": R + "code/09_run_did_and_placebo.py", "__name__": "m09"}; exec(compile(src, "09", "exec"), ns)
dt = {"Focal_ID": str, "Partner_ID": str}
packs = {"main": pd.read_excel(PACK, sheet_name="main_winsorized", dtype=dt), "strict": pd.read_excel(S + r"\08B_strict_regression_package.xlsx", sheet_name="strict_winsorized", dtype=dt)}
arch = S + r"\archive_intermediate\derived_results\12_causal_identification_results.xlsx"
def did(panel, recode):
    smp = panel[(panel.LateTreated == 1) | (panel.NeverTreated == 1)].copy()
    smp["Post"] = (smp.Year >= smp.FirstTreatYear).astype(int) if recode else (smp.Year >= 2023).astype(int)
    smp["TreatPost"] = smp.LateTreated * smp.Post
    fm = "Focal_ROA ~ TreatPost + " + " + ".join(ns["FOCAL_CONTROLS"] + ["Partner_Size_mean", "Partner_Lev_mean", "Partner_ROA_mean", "C(Focal_ID)", "C(Year)"])
    r = ns["fit_cluster"](smp, fm, "Focal_ID")
    return smp, dict(coef=float(r.params["TreatPost"]), se=float(r.bse["TreatPost"]), p=float(r.pvalues["TreatPost"]), N=int(r.nobs))
rows = []; ok = True
for name, df in packs.items():
    panel = ns["build_focal_year_panel"](df)
    sm0, o = did(panel, False); sm1, n = did(panel, True)
    a = pd.read_excel(arch, sheet_name=f"{name}_twfe_did"); am = pd.read_excel(arch, sheet_name=f"{name}_twfe_did_meta")
    ar = a[a.term == "TreatPost"].iloc[0]; an = int(am[am.stat == "n_obs"].value.iloc[0])
    g = (abs(o["coef"] - ar.coef) < 1e-9 and abs(o["se"] - ar.std_err) < 1e-9 and o["N"] == an)
    ok &= g
    print(f"[{name}] archived: coef={ar.coef:.4f} se={ar.std_err:.4f} p={ar.p_value:.4f} N={an} | rerun original coding: coef={o['coef']:.4f} se={o['se']:.4f} p={o['p']:.4f} N={o['N']} | GATE {g}")
    c = sm0[sm0.LateTreated == 1]
    mis = int(((c.Year >= 2023) & (c.Year < c.FirstTreatYear)).sum())
    print(f"[{name}] sample N={len(sm0)}; late-treated firm-years={int(len(c))}; 2024-cohort firm-years in 2023 miscoded as Post by original rule: {mis}; treated cells original={int(sm0.TreatPost.sum())} recoded={int(sm1.TreatPost.sum())}")
    print(f"[{name}] recoded (cohort-based Post): coef={n['coef']:.4f} se={n['se']:.4f} p={n['p']:.4f} N={n['N']}")
    rows += [dict(sample=name, coding="original Post=Year>=2023", **o, treated_cells=int(sm0.TreatPost.sum()), miscoded=mis), dict(sample=name, coding="cohort-based Post=Year>=FirstTreatYear", **n, treated_cells=int(sm1.TreatPost.sum()), miscoded=0)]
pd.DataFrame(rows).to_csv(OUT + r"\g2_static_did.csv", index=False, encoding="utf-8-sig", float_format="%.6f")
print("=== RESULTS ===")
for r in rows: print(f"{r['sample']} | {r['coding']} | coef={r['coef']:.4f} se={r['se']:.4f} p={r['p']:.4f} N={r['N']} | treated cells={r['treated_cells']} miscoded 2024-cohort rows={r['miscoded']}")
print("GATE (original coding equals archived output, both samples):", ok)
print("=== END RESULTS ===")
assert ok
