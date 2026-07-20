"""
09_run_did_and_placebo.py
=========================
Run DID/event-study and placebo tests on focal-year panels derived from the
main and strict analysis samples.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = PROJECT_ROOT / "data" / "processed_data"
ARCHIVE_DIR = PROC_DIR / "archive_intermediate"
PREVIEW_DIR = ARCHIVE_DIR / "preview_figures"
DERIVED_DIR = ARCHIVE_DIR / "derived_results"
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
DERIVED_DIR.mkdir(parents=True, exist_ok=True)

MAIN_PACK = PROC_DIR / "08A_main_regression_package.xlsx"
STRICT_PACK = PROC_DIR / "08B_strict_regression_package.xlsx"
OUT = DERIVED_DIR / "12_causal_identification_results.xlsx"
EVENT_FIG = PREVIEW_DIR / "14_main_event_study.png"
PLACEBO_FIG = PREVIEW_DIR / "15_main_placebo_distribution.png"

N_PLACEBO = 500


FOCAL_CONTROLS = [
    "Focal_Size",
    "Focal_Lev",
    "Focal_Age",
    "Focal_CashFlow",
    "Focal_SoE",
    "Focal_HHI",
]


def prep(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    for col in work.columns:
        if str(work[col].dtype) in {"Int64", "Float64"}:
            work[col] = pd.to_numeric(work[col], errors="coerce")
        elif str(work[col].dtype) == "boolean":
            work[col] = work[col].astype(float)
    work["Year"] = pd.to_numeric(work["Year"], errors="coerce").astype(int)
    return work


def build_focal_year_panel(df: pd.DataFrame) -> pd.DataFrame:
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
    first_treat = agg.loc[agg["Focal_GenAI_Dummy"] == 1].groupby("Focal_ID")["Year"].min().rename("FirstTreatYear")
    agg = agg.merge(first_treat, on="Focal_ID", how="left")
    agg["EverTreated"] = agg["FirstTreatYear"].notna().astype(int)
    agg["LateTreated"] = agg["FirstTreatYear"].ge(2023).fillna(False).astype(int)
    agg["NeverTreated"] = agg["FirstTreatYear"].isna().astype(int)
    return agg


def fit_cluster(df: pd.DataFrame, formula: str, cluster_col: str):
    work = df.copy()
    model = smf.ols(formula=formula, data=work, missing="drop")
    used = model.data.row_labels
    groups = work.loc[used, cluster_col]
    return model.fit(cov_type="cluster", cov_kwds={"groups": groups})


def run_twfe_did(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sample = panel[(panel["LateTreated"] == 1) | (panel["NeverTreated"] == 1)].copy()
    sample["Post"] = (sample["Year"] >= 2023).astype(int)
    sample["TreatPost"] = sample["LateTreated"] * sample["Post"]
    formula = "Focal_ROA ~ TreatPost + " + " + ".join(FOCAL_CONTROLS + ["Partner_Size_mean", "Partner_Lev_mean", "Partner_ROA_mean", "C(Focal_ID)", "C(Year)"])
    res = fit_cluster(sample, formula, "Focal_ID")
    coef = pd.DataFrame(
        [{"term": term, "coef": coef, "std_err": res.bse.get(term), "t_value": res.tvalues.get(term), "p_value": res.pvalues.get(term)} for term, coef in res.params.items()]
    )
    meta = pd.DataFrame([["n_obs", int(res.nobs)], ["r_squared", float(res.rsquared)]], columns=["stat", "value"])
    return coef, meta


def run_event_study(panel: pd.DataFrame) -> pd.DataFrame:
    sample = panel[(panel["LateTreated"] == 1) | (panel["NeverTreated"] == 1)].copy()
    sample["event_time"] = sample["Year"] - sample["FirstTreatYear"]
    rels = [-4, -3, -2, 0, 1]
    term_map = {}
    for r in rels:
        name = f"evt_m{abs(r)}" if r < 0 else f"evt_p{r}"
        term_map[r] = name
        sample[name] = ((sample["LateTreated"] == 1) & (sample["event_time"] == r)).astype(int)
    formula = "Focal_ROA ~ " + " + ".join([term_map[r] for r in rels] + FOCAL_CONTROLS + ["Partner_Size_mean", "Partner_Lev_mean", "Partner_ROA_mean", "C(Focal_ID)", "C(Year)"])
    res = fit_cluster(sample, formula, "Focal_ID")
    rows = []
    for r in rels:
        term = term_map[r]
        rows.append({"event_time": r, "coef": res.params.get(term), "std_err": res.bse.get(term), "p_value": res.pvalues.get(term)})
    out = pd.DataFrame(rows)
    out["ci_low"] = out["coef"] - 1.96 * out["std_err"]
    out["ci_high"] = out["coef"] + 1.96 * out["std_err"]
    return out


def plot_event_study(df: pd.DataFrame) -> None:
    plt.figure(figsize=(7, 5))
    plt.plot(df["event_time"], df["coef"], marker="o", color="#203864", lw=2)
    plt.fill_between(df["event_time"], df["ci_low"], df["ci_high"], color="#9dc3e6", alpha=0.4)
    plt.axhline(0, color="gray", linestyle="--", lw=1)
    plt.axvline(-1, color="gray", linestyle=":", lw=1)
    plt.xlabel("Event Time")
    plt.ylabel("Effect on Focal ROA")
    plt.title("Figure 3. Event Study around GenAI Adoption")
    plt.tight_layout()
    plt.savefig(EVENT_FIG, dpi=300)
    plt.close()


def run_placebo(panel: pd.DataFrame, seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    sample = panel.copy()
    formula = "Focal_ROA ~ Focal_GenAI_Index + " + " + ".join(FOCAL_CONTROLS + ["Partner_Size_mean", "Partner_Lev_mean", "Partner_ROA_mean", "C(Focal_Industry)", "C(Year)"])
    actual = fit_cluster(sample, formula, "Focal_Industry")
    actual_coef = actual.params["Focal_GenAI_Index"]
    draws = []
    for i in range(N_PLACEBO):
        shuffled = sample.copy()
        shuffled["Focal_GenAI_Index"] = rng.permutation(shuffled["Focal_GenAI_Index"].values)
        res = fit_cluster(shuffled, formula, "Focal_Industry")
        draws.append({"draw": i + 1, "coef": res.params["Focal_GenAI_Index"]})
    placebo = pd.DataFrame(draws)
    summary = pd.DataFrame(
        [
            ["actual_coef", actual_coef],
            ["placebo_mean", placebo["coef"].mean()],
            ["placebo_sd", placebo["coef"].std()],
            ["empirical_p", (np.abs(placebo["coef"]) >= abs(actual_coef)).mean()],
        ],
        columns=["stat", "value"],
    )
    return placebo, summary


def plot_placebo(placebo: pd.DataFrame, actual_coef: float) -> None:
    plt.figure(figsize=(7, 5))
    plt.hist(placebo["coef"], bins=30, color="#b4c7e7", edgecolor="white")
    plt.axvline(actual_coef, color="#c00000", linestyle="--", lw=2)
    plt.xlabel("Placebo coefficient")
    plt.ylabel("Frequency")
    plt.title("Figure 4. Placebo Distribution of Randomized GenAI Coefficients")
    plt.tight_layout()
    plt.savefig(PLACEBO_FIG, dpi=300)
    plt.close()


def main() -> None:
    main_df = pd.read_excel(MAIN_PACK, sheet_name="main_winsorized", dtype={"Focal_ID": str, "Partner_ID": str})
    strict_df = pd.read_excel(STRICT_PACK, sheet_name="strict_winsorized", dtype={"Focal_ID": str, "Partner_ID": str})
    main_panel = build_focal_year_panel(main_df)
    strict_panel = build_focal_year_panel(strict_df)

    main_did, main_did_meta = run_twfe_did(main_panel)
    strict_did, strict_did_meta = run_twfe_did(strict_panel)

    main_event = run_event_study(main_panel)
    strict_event = run_event_study(strict_panel)
    plot_event_study(main_event)

    main_placebo, main_placebo_summary = run_placebo(main_panel)
    actual_coef = main_placebo_summary.loc[main_placebo_summary["stat"] == "actual_coef", "value"].iloc[0]
    plot_placebo(main_placebo, actual_coef)

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        main_did.to_excel(writer, sheet_name="main_twfe_did", index=False)
        main_did_meta.to_excel(writer, sheet_name="main_twfe_did_meta", index=False)
        strict_did.to_excel(writer, sheet_name="strict_twfe_did", index=False)
        strict_did_meta.to_excel(writer, sheet_name="strict_twfe_did_meta", index=False)
        main_event.to_excel(writer, sheet_name="main_event_study", index=False)
        strict_event.to_excel(writer, sheet_name="strict_event_study", index=False)
        main_placebo_summary.to_excel(writer, sheet_name="main_placebo_summary", index=False)
        main_placebo.to_excel(writer, sheet_name="main_placebo_draws", index=False)

    print("Ran DID/event-study and placebo tests")
    print(f"Output: {OUT}")
    print(f"Event-study figure: {EVENT_FIG}")
    print(f"Placebo figure: {PLACEBO_FIG}")


if __name__ == "__main__":
    main()
