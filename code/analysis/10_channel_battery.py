# -*- coding: utf-8 -*-
"""
Four-channel candidate-mechanism battery (revision response R1.9).

Channels (column names in the regression package; mapping follows the original
mechanism script's outcome_specs):
    inventory turnover      Focal_InvTurn
    receivables turnover    Focal_SalesVol_Rec
    administrative-expense  Focal_AdminExp_Ratio
    operating cash flow     Focal_CashFlow   (dropped from the control vector
                                              when it is itself the channel)

Recipe -- identical to the persisted inventory-turnover mediation recipe
(data/processed_data/archive_intermediate/derived_results/mediation_results.xlsx
metadata; reproduced in the manuscript's Figure 11):
    a-path:   Channel ~ Focal_GenAI_Index + CONTROLS + C(Focal_Industry) + C(Year)
    b/c'-path: Focal_ROA ~ Focal_GenAI_Index + Channel + CONTROLS + C(Focal_Industry) + C(Year)
    c-path:   Focal_ROA ~ Focal_GenAI_Index + CONTROLS + C(Focal_Industry) + C(Year)
    point-estimate SEs clustered by Focal_Industry;
    indirect effect a*b with a percentile 95% CI from 1,000 row-level bootstrap
    resamples (seed 20260407; unclustered OLS refit per draw, mirroring the
    persisted recipe exactly);
    each channel's three formulas are fit on ONE analytic sample (dropna once).

Joint mediation criterion (stated in the response letter): significant a-path
(p < 0.05) AND bootstrap CI for a*b excluding zero.

SELF-CHECK: the inventory-turnover row must reproduce the persisted mediation
numbers (a = -2.7338, b = 3.230e-05, c' = -0.0143, indirect = -8.83e-05,
CI = [-0.000456, 0.000282], Sobel Z = -0.803) or the script aborts.

Requires the private regression package (excluded from this public repo; see
DATA_AVAILABILITY.md):
    <private>/data/processed_data/08A_main_regression_package.xlsx  (main_winsorized)

Usage:  python 10_channel_battery.py <path-to-08A_main_regression_package.xlsx>
Output: ../../data/Table_channel_battery.csv (+ printed summary)
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CSV = os.path.normpath(os.path.join(HERE, "..", "..", "data", "Table_channel_battery.csv"))

CONTROLS = ["Focal_Size", "Focal_Lev", "Focal_Age", "Focal_CashFlow", "Focal_SoE", "Focal_HHI",
            "Partner_Size", "Partner_Lev", "Partner_ROA"]

CHANNELS = [
    ("inventory_turnover", "Focal_InvTurn"),
    ("receivables_turnover", "Focal_SalesVol_Rec"),
    ("admin_expense_ratio", "Focal_AdminExp_Ratio"),
    ("operating_cash_flow", "Focal_CashFlow"),
]

BOOT_REPS = 1000
BOOT_SEED = 20260407


def prep(df: pd.DataFrame) -> pd.DataFrame:
    w = df.copy()
    for c in w.columns:
        if str(w[c].dtype) in {"Int64", "Float64"}:
            w[c] = pd.to_numeric(w[c], errors="coerce")
        elif str(w[c].dtype) == "boolean":
            w[c] = w[c].astype(float)
    w["Year"] = pd.to_numeric(w["Year"], errors="coerce")
    w["Focal_Industry"] = w["Focal_Industry"].astype(str)
    w["Focal_SoE"] = pd.to_numeric(w["Focal_SoE"], errors="coerce")
    return w


def fit_cluster(formula: str, df: pd.DataFrame):
    model = smf.ols(formula=formula, data=df, missing="drop")
    idx = model.data.row_labels
    used = df.loc[idx]
    return model.fit(cov_type="cluster", cov_kwds={"groups": used["Focal_Industry"]})


def run_channel(df: pd.DataFrame, label: str, chan: str) -> dict:
    controls = [c for c in CONTROLS if c != chan]
    needed = ["Focal_ROA", chan, "Focal_GenAI_Index", "Focal_Industry", "Year"] + controls
    work = df[needed].dropna().copy()

    fe = " + C(Focal_Industry) + C(Year)"
    ctrl = " + ".join(controls)
    f_a = f"{chan} ~ Focal_GenAI_Index + {ctrl}{fe}"
    f_b = f"Focal_ROA ~ Focal_GenAI_Index + {chan} + {ctrl}{fe}"
    f_c = f"Focal_ROA ~ Focal_GenAI_Index + {ctrl}{fe}"

    ra = fit_cluster(f_a, work)
    rb = fit_cluster(f_b, work)
    rc = fit_cluster(f_c, work)

    a, a_se, a_p = ra.params["Focal_GenAI_Index"], ra.bse["Focal_GenAI_Index"], ra.pvalues["Focal_GenAI_Index"]
    b, b_se, b_p = rb.params[chan], rb.bse[chan], rb.pvalues[chan]
    cprime = rb.params["Focal_GenAI_Index"]
    ctotal = rc.params["Focal_GenAI_Index"]
    indirect = a * b
    sobel = indirect / np.sqrt(b * b * a_se * a_se + a * a * b_se * b_se)

    rng = np.random.default_rng(BOOT_SEED)
    n = len(work)
    draws = []
    for _ in range(BOOT_REPS):
        sample = work.iloc[rng.integers(0, n, n)]
        try:
            ba = smf.ols(f_a, data=sample).fit().params["Focal_GenAI_Index"]
            bb = smf.ols(f_b, data=sample).fit().params[chan]
            draws.append(ba * bb)
        except Exception:
            continue
    ci_low, ci_high = np.percentile(draws, [2.5, 97.5])

    return {
        "channel": label, "column": chan, "n": int(len(work)),
        "a": a, "a_se": a_se, "a_p": a_p,
        "b": b, "b_se": b_se, "b_p": b_p,
        "c_prime": cprime, "c_total": ctotal,
        "indirect": indirect, "sobel_z": sobel,
        "boot_ci_low": ci_low, "boot_ci_high": ci_high,
        "a_path_significant": bool(a_p < 0.05),
        "ci_excludes_zero": bool(ci_low > 0 or ci_high < 0),
        "joint_criterion_met": bool(a_p < 0.05 and (ci_low > 0 or ci_high < 0)),
    }


def main() -> None:
    pack = sys.argv[1]
    df = prep(pd.read_excel(pack, sheet_name="main_winsorized",
                            dtype={"Focal_ID": str, "Partner_ID": str}))
    print(f"pack rows: {len(df)}; bootstrap: {BOOT_REPS} row-level resamples, seed {BOOT_SEED}")

    rows = [run_channel(df, label, chan) for label, chan in CHANNELS]
    out = pd.DataFrame(rows)
    for _, r in out.iterrows():
        print(f"{r['channel']:22s} n={r['n']:4d}  a={r['a']:+.4f} (p={r['a_p']:.3f})  "
              f"b={r['b']:+.6f} (p={r['b_p']:.4f})  c'={r['c_prime']:+.4f}  "
              f"indirect={r['indirect']:+.6f}  CI=[{r['boot_ci_low']:+.6f}, {r['boot_ci_high']:+.6f}]  "
              f"joint={'MET' if r['joint_criterion_met'] else 'not met'}")

    inv = out.iloc[0]
    checks = [
        ("a", inv["a"], -2.7338, 5e-4), ("b", inv["b"], 3.230e-05, 5e-8),
        ("c_prime", inv["c_prime"], -0.0143, 5e-5), ("indirect", inv["indirect"], -8.83e-05, 5e-7),
        ("ci_low", inv["boot_ci_low"], -0.000456, 5e-6), ("ci_high", inv["boot_ci_high"], 0.000282, 5e-6),
        ("sobel", inv["sobel_z"], -0.803, 5e-4),
    ]
    bad = [(nm, got, want) for nm, got, want, tol in checks if abs(got - want) > tol]
    if bad:
        for nm, got, want in bad:
            print(f"SELF-CHECK FAIL {nm}: got {got} want {want}")
        raise SystemExit(1)
    print("SELF-CHECK PASS: inventory row reproduces the persisted mediation numbers.")

    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"written: {OUT_CSV}")
    n_met = int(out["joint_criterion_met"].sum())
    print(f"channels meeting the joint mediation criterion: {n_met} of {len(out)}")


if __name__ == "__main__":
    main()
