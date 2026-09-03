# -*- coding: utf-8 -*-
"""
Extended event-study horizons (round-2 revision, Reviewer 1 comment 1).

Reviewer 1 asked whether the negative association is genuinely confined to the
short run. The published Figure 9 stops at t = +1 because, on the 2015-2024
panel, the 2023/2024 first-disclosure cohorts are observed for at most one
post-disclosure year. Adding fiscal 2025 buys one more horizon.

Two specifications, both reusing the EXACT recipe of code/09_run_did_and_placebo.py
(focal firm-year panel collapsed from the dyadic sample; treated = first-disclosure
cohort; controls = never-disclosing firms; firm and year fixed effects; SEs
clustered by Focal_ID; reference period t = -1):

  A) PUBLISHED COHORT DEFINITION, extended window
     LateTreated = first disclosure in 2023 or later, window [-4 .. +2].
  B) WIDER COHORT VARIANT, longer window
     LateTreated = first disclosure in 2022 or later, window [-4 .. +3].
     Reported separately and explicitly labelled: it changes the cohort
     definition, so it is NOT a like-for-like extension of Figure 9.

The fiscal-2025 rows carry the Section 4.7 clean-text filter (drop Year == 2025
AND Focal_MDA_CharCount == 32767, the Excel cell cap that mechanically censors
the disclosure measure for the longest documents), applied on the dyadic sample
BEFORE the firm-year collapse, exactly as 07_fy2025_cleantext_extension.py does.

Per-horizon treated-firm counts are reported alongside every coefficient, because
the late horizons rest on very few firms and must not be over-read.

SELF-CHECK: running the published recipe on the ORIGINAL 2015-2024 package must
reproduce Figure 9's post-disclosure coefficients (t = 0: -0.0130, t = +1: -0.0204)
or the script aborts.

Requires the private regression packages (excluded from this public repo; see
DATA_AVAILABILITY.md):
    <private>/data/processed_data/08A_main_regression_package.xlsx          (main_winsorized)
    <private>/data/processed_data/v2025/08A_main_regression_package_2025.xlsx (main_winsorized)

Usage:  python 13_event_study_extended.py <08A_2015_2024.xlsx> <08A_2025.xlsx>
Output: ../../data/event_study_extended.json  (+ printed summary)
"""
from __future__ import annotations

import json
import os
import sys

import pandas as pd
import statsmodels.formula.api as smf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.normpath(os.path.join(HERE, "..", "..", "data", "event_study_extended.json"))

# identical to 09_run_did_and_placebo.py
FOCAL_CONTROLS = ["Focal_Size", "Focal_Lev", "Focal_Age", "Focal_CashFlow", "Focal_SoE", "Focal_HHI"]
PARTNER_MEANS = ["Partner_Size_mean", "Partner_Lev_mean", "Partner_ROA_mean"]
TRUNC_LEN = 32767


def prep(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    for col in work.columns:
        if str(work[col].dtype) in {"Int64", "Float64"}:
            work[col] = pd.to_numeric(work[col], errors="coerce")
        elif str(work[col].dtype) == "boolean":
            work[col] = work[col].astype(float)
    work["Year"] = pd.to_numeric(work["Year"], errors="coerce").astype(int)
    return work


def clean_text_filter(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Section 4.7 filter: drop fiscal-2025 rows whose MD&A hit the Excel cell cap."""
    if "Focal_MDA_CharCount" not in df.columns:
        return df, 0
    cc = pd.to_numeric(df["Focal_MDA_CharCount"], errors="coerce")
    trunc = (df["Year"] == 2025) & (cc == TRUNC_LEN)
    return df.loc[~trunc].copy(), int(trunc.sum())


def build_focal_year_panel(df: pd.DataFrame, cohort_from: int) -> pd.DataFrame:
    """Identical collapse to 09_run_did_and_placebo.build_focal_year_panel,
    with the first-disclosure cohort threshold made explicit."""
    work = prep(df)
    agg = (
        work.groupby(["Focal_ID", "Year"], as_index=False)
        .agg(
            Focal_ROA=("Focal_ROA", "first"),
            Focal_GenAI_Index=("Focal_GenAI_Index", "first"),
            Focal_GenAI_Dummy=("Focal_GenAI_Dummy", "first"),
            Focal_Size=("Focal_Size", "first"),
            Focal_Lev=("Focal_Lev", "first"),
            Focal_Age=("Focal_Age", "first"),
            Focal_CashFlow=("Focal_CashFlow", "first"),
            Focal_SoE=("Focal_SoE", "first"),
            Focal_HHI=("Focal_HHI", "first"),
            Focal_Industry=("Focal_Industry", "first"),
            Partner_Size_mean=("Partner_Size", "mean"),
            Partner_Lev_mean=("Partner_Lev", "mean"),
            Partner_ROA_mean=("Partner_ROA", "mean"),
        )
        .copy()
    )
    first_treat = (agg.loc[agg["Focal_GenAI_Dummy"] == 1]
                   .groupby("Focal_ID")["Year"].min().rename("FirstTreatYear"))
    agg = agg.merge(first_treat, on="Focal_ID", how="left")
    agg["LateTreated"] = agg["FirstTreatYear"].ge(cohort_from).fillna(False).astype(int)
    agg["NeverTreated"] = agg["FirstTreatYear"].isna().astype(int)
    return agg


def run_event_study(panel: pd.DataFrame, rels: list[int]) -> list[dict]:
    sample = panel[(panel["LateTreated"] == 1) | (panel["NeverTreated"] == 1)].copy()
    sample["event_time"] = sample["Year"] - sample["FirstTreatYear"]
    term_map = {}
    for r in rels:
        name = f"evt_m{abs(r)}" if r < 0 else f"evt_p{r}"
        term_map[r] = name
        sample[name] = ((sample["LateTreated"] == 1) & (sample["event_time"] == r)).astype(int)
    formula = ("Focal_ROA ~ " + " + ".join([term_map[r] for r in rels] + FOCAL_CONTROLS
                                           + PARTNER_MEANS + ["C(Focal_ID)", "C(Year)"]))
    model = smf.ols(formula=formula, data=sample, missing="drop")
    used = model.data.row_labels
    res = model.fit(cov_type="cluster", cov_kwds={"groups": sample.loc[used, "Focal_ID"]})
    fitted = sample.loc[used]
    rows = []
    for r in rels:
        t = term_map[r]
        rows.append({
            "event_time": r,
            "coef": float(res.params.get(t)),
            "std_err": float(res.bse.get(t)),
            "p_value": float(res.pvalues.get(t)),
            "n_firm_years": int(fitted[t].sum()),
            "n_firms": int(fitted.loc[fitted[t] == 1, "Focal_ID"].nunique()),
        })
    return rows, int(res.nobs), int(fitted["Focal_ID"].nunique())


def show(label: str, rows: list[dict], nobs: int, nfirms: int) -> None:
    print(f"\n--- {label} | N={nobs} firm-years, {nfirms} focal firms, reference t=-1 ---")
    for r in rows:
        print(f"   t={r['event_time']:+d}  coef {r['coef']:+.5f}  se {r['std_err']:.5f}  "
              f"p={r['p_value']:.4f}   (treated firm-years={r['n_firm_years']}, firms={r['n_firms']})")


def main() -> None:
    pack_2024, pack_2025 = sys.argv[1], sys.argv[2]

    # ---- SELF-CHECK: reproduce published Figure 9 on the original package ----
    df24 = pd.read_excel(pack_2024, sheet_name="main_winsorized",
                         dtype={"Focal_ID": str, "Partner_ID": str})
    panel24 = build_focal_year_panel(df24, cohort_from=2023)
    pub_rows, pub_n, pub_f = run_event_study(panel24, [-4, -3, -2, 0, 1])
    got = {r["event_time"]: round(r["coef"], 4) for r in pub_rows}
    want = {0: -0.0130, 1: -0.0204}
    bad = [(k, got.get(k), v) for k, v in want.items() if got.get(k) != v]
    if bad:
        for k, g, v in bad:
            print(f"SELF-CHECK FAIL t={k}: got {g} want {v}")
        raise SystemExit(1)
    print("SELF-CHECK PASS: published recipe reproduces Figure 9 "
          "(t=0: -0.0130, t=+1: -0.0204).")
    show("PUBLISHED Figure 9 (2015-2024, cohorts >=2023, window [-4,+1])",
         pub_rows, pub_n, pub_f)

    # ---- extended horizons on the fiscal-2025 panel ----
    df25 = prep(pd.read_excel(pack_2025, sheet_name="main_winsorized",
                              dtype={"Focal_ID": str, "Partner_ID": str}))
    df25c, n_trunc = clean_text_filter(df25)
    print(f"\nfiscal-2025 clean-text filter: dropped {n_trunc} truncated dyad-year rows "
          f"({len(df25)} -> {len(df25c)})")

    panelA = build_focal_year_panel(df25c, cohort_from=2023)
    rowsA, nA, fA = run_event_study(panelA, [-4, -3, -2, 0, 1, 2])
    show("A) published cohort definition (>=2023), window [-4,+2], FY2025 added", rowsA, nA, fA)

    panelB = build_focal_year_panel(df25c, cohort_from=2022)
    rowsB, nB, fB = run_event_study(panelB, [-4, -3, -2, 0, 1, 2, 3])
    show("B) WIDER cohort variant (>=2022), window [-4,+3] -- NOT like-for-like with Figure 9",
         rowsB, nB, fB)

    out = {
        "published_figure9": {"rows": pub_rows, "n_obs": pub_n, "n_firms": pub_f,
                              "cohort_from": 2023, "source": "2015-2024 package"},
        "extended_A_cohort2023": {"rows": rowsA, "n_obs": nA, "n_firms": fA,
                                  "cohort_from": 2023, "source": "FY2025 package, clean-text filtered",
                                  "n_truncated_dropped": n_trunc},
        "variant_B_cohort2022": {"rows": rowsB, "n_obs": nB, "n_firms": fB,
                                 "cohort_from": 2022, "source": "FY2025 package, clean-text filtered",
                                 "note": "cohort definition differs from Figure 9; reported as a variant only"},
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nwritten: {OUT_JSON}")


if __name__ == "__main__":
    main()
