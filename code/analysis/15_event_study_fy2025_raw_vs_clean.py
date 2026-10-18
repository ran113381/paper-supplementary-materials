r"""s8_event_raw.py -- S8: FY2025 event study, clean-exclusion vs raw (truncated rows kept), using R\code\13_event_study_extended.py functions unchanged.
Purpose : gate = clean A (cohort>=2023, window [-4..+2]) t=0/+1/+2 = -0.0122 / -0.0070 / +0.0112 (P0154); then raw version of A and variant B (cohort>=2022, window [-4..+3]) for both,
          with coefficient, SE, p, treated firm-years and firms per horizon.
Inputs  : S\data\processed_data\08A_main_regression_package.xlsx ; S\data\processed_data\v2025\08A_main_regression_package_2025.xlsx (main_winsorized)
Outputs : s8_event_raw.log
Upstream: R code\analysis\13_event_study_extended.py (imported). Downstream: J35_summary.md
"""
import sys, importlib.util, warnings; warnings.filterwarnings("ignore")
import pandas as pd
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
S = r"E:\Supply_Chain_Project\data\processed_data"
R = "E:/paper2  daxiu/73ae4696cf54747044a03a936c4bb958_744934475e1139b8c27898b82ae5bbf0_8/paper2_github_replication/"
spec = importlib.util.spec_from_file_location("es13", R + "code/analysis/13_event_study_extended.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
# self-check on the 2015-2024 package (Figure 9)
df24 = pd.read_excel(S + r"\08A_main_regression_package.xlsx", sheet_name="main_winsorized", dtype={"Focal_ID": str, "Partner_ID": str})
rows24, n24, f24 = m.run_event_study(m.build_focal_year_panel(df24, 2023), [-4, -3, -2, 0, 1])
g24 = {r["event_time"]: round(r["coef"], 4) for r in rows24}; print("Fig9 self-check:", g24); assert g24[0] == -0.0130 and g24[1] == -0.0204
df25 = m.prep(pd.read_excel(S + r"\v2025\08A_main_regression_package_2025.xlsx", sheet_name="main_winsorized", dtype={"Focal_ID": str, "Partner_ID": str}))
clean, n_trunc = m.clean_text_filter(df25); print(f"FY2025 pack rows={len(df25)}; truncated dropped in clean={n_trunc}; clean rows={len(clean)}")
out = {}
for sample, d in [("clean", clean), ("raw", df25)]:
    for lab, cohort, rels in [("A>=2023", 2023, [-4, -3, -2, 0, 1, 2]), ("B>=2022", 2022, [-4, -3, -2, 0, 1, 2, 3])]:
        rows, nobs, nf = m.run_event_study(m.build_focal_year_panel(d, cohort), rels)
        out[(sample, lab)] = (rows, nobs, nf)
        print(f"\n--- {sample} | {lab} | N={nobs} firm-years, {nf} focal firms ---")
        for r in rows: print(f"  t={r['event_time']:+d} coef {r['coef']:+.4f} se {r['std_err']:.4f} p={r['p_value']:.4f} (treated firm-years={r['n_firm_years']}, firms={r['n_firms']})")
gA = {r["event_time"]: round(r["coef"], 4) for r in out[("clean", "A>=2023")][0]}
assert (gA[0], gA[1], gA[2]) == (-0.0122, -0.0070, 0.0112), f"GATE FAIL {gA}"
print("\nGATE PASS clean A: t0/t1/t2 = -0.0122 / -0.0070 / +0.0112")
print("=== RESULTS ===")
print("GATE PASS: Fig9 -0.0130/-0.0204; clean A t0/t1/t2 = -0.0122/-0.0070/+0.0112")
print(f"truncated dropped in clean = {n_trunc}; rows raw {len(df25)} vs clean {len(clean)}")
for (sample, lab), (rows, nobs, nf) in out.items():
    print(f"[{sample} {lab}] N={nobs} firms={nf}")
    for r in rows:
        if r["event_time"] >= 0: print(f"   t={r['event_time']:+d} coef={r['coef']:+.4f} se={r['std_err']:.4f} p={r['p_value']:.4f} firm-years={r['n_firm_years']} firms={r['n_firms']}")
print("=== END RESULTS ===")
