"""C7b: transparent Callaway-Sant'Anna (2021) group-time ATT, repeated-cross-section / unbalanced-panel version.
Why own implementation: csdid 0.2.9 returned identical never-treated / not-yet-treated results, NaN cells and singular
matrices on this very thin unbalanced panel (see c7.log); this script is cross-checked to csdid on cells where csdid is finite.
Design: sample = 734 firm-years (late-treated cohorts 2023/2024 + never-treated), universal base period b = g-1.
ATT(g,t) = [Ybar(g,t)-Ybar(g,b)] - [Ybar(C,t)-Ybar(C,b)]   (unconditional DiD = CS-DR with no covariates)
 control C: 'never' -> G==0 ; 'notyet' -> G==0 or (G>max(t,b) and G!=g)
 'ra' variant: outcome-regression adjustment with Size, Lev, CashFlow fitted on controls in each period.
Aggregation: dynamic (event time e=t-g) and overall post-treatment ATT, weights = treated firm-year counts in cell.
Inference: firm-clustered bootstrap, 2000 draws, seed 42 (whole pipeline re-run per draw). Pre-trend Wald from bootstrap covariance.
"""
import numpy as np, pandas as pd, sys
from scipy import stats
R = r"E:/paper2  daxiu/73ae4696cf54747044a03a936c4bb958_744934475e1139b8c27898b82ae5bbf0_8/paper2_github_replication"
OUT = r"E:/論文投稿  送審/paper2/R3_work/E_valid_shap_es"
src = open(R + "/code/09_run_did_and_placebo.py", encoding="utf-8").read()
src = src.replace("PREVIEW_DIR.mkdir(parents=True, exist_ok=True)", "").replace("DERIVED_DIR.mkdir(parents=True, exist_ok=True)", "").replace('if __name__ == "__main__":\n    main()', "")
ns = {"__file__": R + "/code/09_run_did_and_placebo.py", "__name__": "m09"}; exec(compile(src, "09", "exec"), ns)
df = pd.read_excel(r"E:/Supply_Chain_Project/data/processed_data/08A_main_regression_package.xlsx", sheet_name="main_winsorized", dtype={"Focal_ID": str, "Partner_ID": str})
panel = ns["build_focal_year_panel"](df)
s = panel[(panel.LateTreated == 1) | (panel.NeverTreated == 1)].copy().reset_index(drop=True)
s["G"] = s.FirstTreatYear.fillna(0).astype(int)
cov = ["Focal_Size", "Focal_Lev", "Focal_CashFlow"]
assert len(s) == 734 and s.Focal_ID.nunique() == 348
firms = s.Focal_ID.values; ufirm = pd.unique(firms)
idx_by_firm = {f: np.where(firms == f)[0] for f in ufirm}
Y = s.Focal_ROA.values; T = s.Year.values; G = s.G.values; X = s[cov].values
GS = [2023, 2024]; YEARS = sorted(s.Year.unique())

def ols_pred(Xc, yc, Xp):
    A = np.column_stack([np.ones(len(Xc)), Xc]); b = np.linalg.lstsq(A, yc, rcond=None)[0]
    return np.column_stack([np.ones(len(Xp)), Xp]) @ b

def attgt(rows, ctrl, ra):
    y, t, g, x = Y[rows], T[rows], G[rows], X[rows]
    out = {}
    for gg in GS:
        b = gg - 1
        for tt in YEARS:
            if tt == b: continue
            m = max(tt, b)
            c_ok = (g == 0) if ctrl == "never" else ((g == 0) | ((g > m) & (g != gg)))
            tr_t = (g == gg) & (t == tt); tr_b = (g == gg) & (t == b)
            ct_t = c_ok & (t == tt); ct_b = c_ok & (t == b)
            if min(tr_t.sum(), tr_b.sum(), ct_t.sum(), ct_b.sum()) == 0:
                out[(gg, tt)] = (np.nan, 0); continue
            if not ra:
                att = (y[tr_t].mean() - y[tr_b].mean()) - (y[ct_t].mean() - y[ct_b].mean())
            else:
                rt = y[tr_t] - ols_pred(x[ct_t], y[ct_t], x[tr_t]); rb = y[tr_b] - ols_pred(x[ct_b], y[ct_b], x[tr_b])
                att = rt.mean() - rb.mean()
            out[(gg, tt)] = (att, int(tr_t.sum()))
    return out

def aggregate(out):
    cells = pd.DataFrame([(g, t, a, n) for (g, t), (a, n) in out.items()], columns=["g", "t", "att", "n"])
    cells["e"] = cells.t - cells.g
    ok = cells.dropna(subset=["att"])
    dyn = pd.Series({e: np.average(d.att, weights=d.n) for e, d in ok.groupby("e") if d.n.sum() > 0})
    post = ok[ok.e >= 0]
    overall = np.average(post.att, weights=post.n) if len(post) else np.nan
    return cells, dyn, overall

def run(ctrl, ra, B=2000, seed=42):
    rows_all = np.arange(len(s))
    cells, dyn, ov = aggregate(attgt(rows_all, ctrl, ra))
    rng = np.random.default_rng(seed)
    bd, bo, bc = [], [], []
    for _ in range(B):
        pick = rng.choice(ufirm, len(ufirm), replace=True)
        rows = np.concatenate([idx_by_firm[f] for f in pick])
        c2, d2, o2 = aggregate(attgt(rows, ctrl, ra))
        bd.append(d2); bo.append(o2); bc.append(c2.set_index(["g", "t"]).att)
    bd = pd.DataFrame(bd); bc = pd.DataFrame(bc)
    se_d = bd.std(ddof=1); se_o = np.nanstd(bo, ddof=1); se_c = bc.std(ddof=1)
    return cells, dyn, ov, bd, se_d, se_o, se_c, np.array(bo), bc

def wald(dyn, bd, es):
    es = [e for e in es if e in dyn.index and e in bd.columns]
    sub = bd[es].dropna()
    V = np.cov(sub.values.T, ddof=1); a = dyn[es].values
    V = np.atleast_2d(V)
    W = float(a @ np.linalg.solve(V, a)); return es, W, len(es), 1 - stats.chi2.cdf(W, len(es)), len(sub)

print("=== RESULTS ===")
allres = {}
for ctrl in ["never", "notyet"]:
    for ra in [False, True]:
        lab = f"{ctrl}_{'ra' if ra else 'nocov'}"
        cells, dyn, ov, bd, se_d, se_o, se_c, bo, bc = run(ctrl, ra)
        allres[lab] = (cells, dyn, ov)
        cells["se"] = [se_c.get((g, t), np.nan) for g, t in zip(cells.g, cells.t)]
        cells["p"] = 2 * (1 - stats.norm.cdf(np.abs(cells.att / cells.se)))
        cells.to_csv(f"{OUT}/c7b_cs_gt_{lab}.csv", index=False, encoding="utf-8-sig")
        d = pd.DataFrame({"e": dyn.index, "att": dyn.values, "se": [se_d.get(e, np.nan) for e in dyn.index]})
        d["p"] = 2 * (1 - stats.norm.cdf(np.abs(d.att / d.se))); d["lo"] = d.att - 1.96 * d.se; d["hi"] = d.att + 1.96 * d.se
        d["n_treated_obs"] = [int(cells[(cells.e == e)].n.sum()) for e in d.e]
        d.to_csv(f"{OUT}/c7b_cs_dynamic_{lab}.csv", index=False, encoding="utf-8-sig")
        print(f"\n### CS [{lab}]  N={len(s)} firm-years, 348 firms, base g-1, firm-cluster bootstrap B=2000 seed 42")
        print("group-time ATT(g,t):"); print(cells[["g", "t", "att", "se", "p", "n"]].round(4).to_string(index=False))
        print("event-time aggregation:"); print(d.round(4).to_string(index=False))
        print(f"overall post-treatment ATT = {ov:.4f}  (bootstrap SE {se_o:.4f}; 95% pct CI [{np.nanpercentile(bo,2.5):.4f}, {np.nanpercentile(bo,97.5):.4f}])")
        for lbl, es in [("pre e=-4..-2 (Fig 9 pre window)", [-4, -3, -2]), ("pre e=-2 only", [-2]), ("pre e=-9..-2 all", list(range(-9, -1)))]:
            try:
                e_, W, k, p, nb = wald(dyn, bd, es)
                print(f"  pre-trend joint Wald [{lbl}]: cells used e={e_}, W={W:.4f}, df={k}, p={p:.4f} (bootstrap draws usable={nb})")
            except Exception as ex:
                print(f"  pre-trend Wald [{lbl}] failed: {type(ex).__name__}: {ex}")
        # post-treatment e=0,1 compare with TWFE
# cross-check vs csdid 0.2.9 finite post/pre cells (c7.log): csdid 'never' and 'notyet' outputs were identical
chk = {(2023, 2023): -0.0282, (2023, 2024): -0.0147, (2024, 2023): None, (2024, 2024): -0.0147}
print("CROSS-CHECK vs csdid 0.2.9 (c7.log; csdid output identical for both control groups):")
for lab in ["never_nocov", "notyet_nocov"]:
    c = allres[lab][0].set_index(["g", "t"]).att
    for k, v in chk.items():
        if v is None or k not in c.index: continue
        print(f"  [{lab}] ATT{k}: own={c[k]:.4f} csdid={v:.4f} diff={abs(c[k]-v):.5f}")
# CS-style 'simple' (group-size weights) and 'group' overall for comparison with manuscript's -0.0137 (SE 0.0081)
ng = {2023: 22, 2024: 25}
for lab in allres:
    cl = allres[lab][0]; po = cl[(cl.t >= cl.g)].dropna(subset=["att"])
    w = po.g.map(ng); simple = np.average(po.att, weights=w)
    gm = po.groupby("g").att.mean(); group = np.average(gm.values, weights=[ng[g] for g in gm.index])
    print(f"  [{lab}] simple(group-size weights)={simple:.4f}  group-aggregate={group:.4f}   (manuscript line 166 reports -0.0137, SE 0.0081)")
print("=== END RESULTS ===")
