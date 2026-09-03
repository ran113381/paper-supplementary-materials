# -*- coding: utf-8 -*-
"""
Curvature-in-intensity test (round-2 revision, Reviewer 1 comment 1).

The reviewer asked whether a U-shaped / non-monotonic pattern was tested. This
script adds a quadratic term in GenAI disclosure intensity to the Table 9
column (1) baseline and applies the Lind & Mehlum (2010) U-test logic:

    Focal_ROA ~ Focal_GenAI_Index + Focal_GenAI_Index^2 + CONTROLS
                + C(Focal_Industry) + C(Year),  SEs clustered by Focal_Industry

A U/inverted-U requires ALL of:
    (i)  a statistically significant quadratic coefficient,
    (ii) end-point slopes of opposite sign, BOTH individually significant,
    (iii) a turning point strictly inside the observed range of the regressor.

IMPORTANT SCOPE NOTE (carried into the manuscript): this tests curvature in the
DOSE (disclosure intensity), not in TIME. The reviewer's J-curve question is a
question about the time profile, which this design cannot answer because the
rebound horizon lies outside the sample window; see 13_event_study_extended.py
for what the time dimension can and cannot show.

SELF-CHECK: the linear baseline must reproduce the published Table 9 column (1)
coefficient (-0.0146) and R-squared (0.384) or the script aborts.

Requires the private regression packages (excluded from this public repo; see
DATA_AVAILABILITY.md):
    <private>/data/processed_data/08A_main_regression_package.xlsx  (main_winsorized)
    <private>/data/processed_data/08B_strict_regression_package.xlsx (strict_winsorized)  [optional]

Usage:  python 12_curvature_test.py <08A.xlsx> [<08B.xlsx>]
Output: ../../data/curvature_test_results.json  (+ printed summary)
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.normpath(os.path.join(HERE, "..", "..", "data", "curvature_test_results.json"))

CONTROLS = ["Focal_Size", "Focal_Lev", "Focal_Age", "Focal_CashFlow", "Focal_SoE",
            "Focal_HHI", "Partner_Size", "Partner_Lev", "Partner_ROA"]
FE = " + C(Focal_Industry) + C(Year)"


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
    used = df.loc[model.data.row_labels]
    return model.fit(cov_type="cluster", cov_kwds={"groups": used["Focal_Industry"]})


def run(df: pd.DataFrame, label: str) -> dict:
    need = ["Focal_ROA", "Focal_GenAI_Index", "Focal_Industry", "Year"] + CONTROLS
    work = df[need].dropna().copy()
    work["GenAI_sq"] = work["Focal_GenAI_Index"] ** 2
    ctrl = " + ".join(CONTROLS)

    base = fit_cluster("Focal_ROA ~ Focal_GenAI_Index + " + ctrl + FE, work)
    quad = fit_cluster("Focal_ROA ~ Focal_GenAI_Index + GenAI_sq + " + ctrl + FE, work)

    b1 = float(quad.params["Focal_GenAI_Index"])
    b2 = float(quad.params["GenAI_sq"])
    V = quad.cov_params()
    v11 = float(V.loc["Focal_GenAI_Index", "Focal_GenAI_Index"])
    v22 = float(V.loc["GenAI_sq", "GenAI_sq"])
    v12 = float(V.loc["Focal_GenAI_Index", "GenAI_sq"])

    g = work["Focal_GenAI_Index"]
    gmin, gmax = float(g.min()), float(g.max())

    def slope(x: float):
        s = b1 + 2 * b2 * x
        se = float(np.sqrt(v11 + 4 * x * x * v22 + 4 * x * v12))
        return s, se, (s / se if se > 0 else np.nan)

    s_lo, se_lo, t_lo = slope(gmin)
    s_hi, se_hi, t_hi = slope(gmax)
    turning = (-b1 / (2 * b2)) if b2 != 0 else float("nan")

    cond_quad_sig = bool(quad.pvalues["GenAI_sq"] < 0.05)
    cond_opposite = bool(np.sign(s_lo) != np.sign(s_hi))
    cond_both_sig = bool(abs(t_lo) > 1.96 and abs(t_hi) > 1.96)
    cond_interior = bool(gmin < turning < gmax)

    res = {
        "sample": label,
        "n": int(len(work)),
        "share_positive_disclosure": float((g > 0).mean()),
        "g_min": gmin, "g_p50": float(g.median()),
        "g_p95": float(g.quantile(0.95)), "g_max": gmax,
        "linear_baseline": {
            "coef": float(base.params["Focal_GenAI_Index"]),
            "se": float(base.bse["Focal_GenAI_Index"]),
            "p": float(base.pvalues["Focal_GenAI_Index"]),
            "r2": float(base.rsquared), "aic": float(base.aic),
        },
        "quadratic": {
            "b1_linear": b1, "b1_p": float(quad.pvalues["Focal_GenAI_Index"]),
            "b2_squared": b2, "b2_se": float(quad.bse["GenAI_sq"]),
            "b2_p": float(quad.pvalues["GenAI_sq"]),
            "r2": float(quad.rsquared), "aic": float(quad.aic),
        },
        "slope_at_min": {"slope": s_lo, "se": se_lo, "t": t_lo},
        "slope_at_max": {"slope": s_hi, "se": se_hi, "t": t_hi},
        "turning_point": turning,
        "u_test": {
            "quadratic_significant": cond_quad_sig,
            "endpoint_slopes_opposite_sign": cond_opposite,
            "both_endpoint_slopes_significant": cond_both_sig,
            "turning_point_interior": cond_interior,
            "u_shape_supported": bool(cond_quad_sig and cond_opposite and cond_both_sig and cond_interior),
        },
    }
    return res


def main() -> None:
    main_pack = sys.argv[1]
    df = prep(pd.read_excel(main_pack, sheet_name="main_winsorized",
                            dtype={"Focal_ID": str, "Partner_ID": str}))
    out = [run(df, "main")]

    # SELF-CHECK against the published Table 9 column (1)
    lin = out[0]["linear_baseline"]
    checks = [("coef", round(lin["coef"], 4), -0.0146), ("r2", round(lin["r2"], 3), 0.384),
              ("n", out[0]["n"], 1017)]
    bad = [(k, got, want) for k, got, want in checks if got != want]
    if bad:
        for k, got, want in bad:
            print(f"SELF-CHECK FAIL {k}: got {got} want {want}")
        raise SystemExit(1)
    print("SELF-CHECK PASS: linear baseline reproduces Table 9 column (1) "
          "(-0.0146, R2 0.384, N=1,017).")

    if len(sys.argv) > 2:
        sdf = prep(pd.read_excel(sys.argv[2], sheet_name="strict_winsorized",
                                 dtype={"Focal_ID": str, "Partner_ID": str}))
        out.append(run(sdf, "strict"))

    for r in out:
        q = r["quadratic"]
        print(f"\n[{r['sample']}] N={r['n']}  positive-disclosure share={r['share_positive_disclosure']:.1%}"
              f"  g range [{r['g_min']:.3f}, {r['g_max']:.3f}]")
        print(f"  linear    GenAI     = {r['linear_baseline']['coef']:+.5f} (p={r['linear_baseline']['p']:.4f})")
        print(f"  quadratic GenAI     = {q['b1_linear']:+.5f} (p={q['b1_p']:.4f})")
        print(f"  quadratic GenAI^2   = {q['b2_squared']:+.5f} (se {q['b2_se']:.5f}, p={q['b2_p']:.4f})")
        print(f"  slope at g_min      = {r['slope_at_min']['slope']:+.5f} (t={r['slope_at_min']['t']:.2f})")
        print(f"  slope at g_max      = {r['slope_at_max']['slope']:+.5f} (t={r['slope_at_max']['t']:.2f})")
        print(f"  turning point       = {r['turning_point']:.3f}")
        u = r["u_test"]
        print(f"  U-test -> quadratic sig: {u['quadratic_significant']}; opposite slopes: "
              f"{u['endpoint_slopes_opposite_sign']}; both sig: {u['both_endpoint_slopes_significant']}; "
              f"interior TP: {u['turning_point_interior']}")
        print(f"  U-SHAPE SUPPORTED: {u['u_shape_supported']}")

    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nwritten: {OUT_JSON}")


if __name__ == "__main__":
    main()
