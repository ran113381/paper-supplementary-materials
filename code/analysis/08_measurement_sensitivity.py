"""
JOB 1 -- Measurement-sensitivity panel re-estimation (paper2 IP&M revision, round 3)
Read-only w.r.t. manuscript/data. Writes only to this scratchpad folder.

Decision rule: exact-recipe-only, one run per target, no tuning toward any expectation.

STEP 0 -- how the ORIGINAL Focal_GenAI_Index is built (read from
<PROJECT_ROOT>\\code\\05_build_genai_measurement.py, not modified):
  - compute_genai_metrics(): clean_count = number of regex KEYWORD matches (longest-match,
    non-overlapping) found by scanning the FULL upper-cased MDA_Text for the ~103-term
    dictionary. This is a KEYWORD-FREQUENCY count over the whole document, NOT a passage count.
  - GenAI_Index = log1p(clean_count)   [see line: index = float(np.log1p(clean_count))]
  => CONFIRMED: the caveat in the task brief is correct. The original index is
     keyword-frequency-based (over full MD&A text), while
     full_sample_gpt55_claude_consensus_labels.csv is PASSAGE-level (1,256 discrete passages).
     These are NOT the same counting unit. To make any comparison honest, this script builds
     alternative indices on a PASSAGE-COUNT basis (count of passages per firm-year), and builds
     BOTH (i) an unfiltered "all-matched-passages" count (same unit, no consensus filter -- the
     like-for-like comparator) and (ii)/(iii) the two consensus-filtered subsets requested, on
     that SAME passage-count basis, so any difference in results between (i) and (ii)/(iii) is
     attributable to the FILTER, not to a change in counting unit. This is stated explicitly in
     the log below, per the task's instruction not to fake a frequency reweighting.

STEP 0b -- actual label schema in the consensus CSV (checked, NOT assumed):
  consensus_label observed values: substantive_adoption (483), unclear (372),
  generic_or_background (279), disagreement (122).  There is NO 'not_genai_related' value.
  Individual rater labels (gpt55_label / claude_label) only ever take
  {substantive_adoption, generic_or_background, unclear} -- because ALL 1,256 passages already
  passed the ORIGINAL dictionary keyword screen (they are, by the file's own name,
  "dictionary-matched passages"), so a "this passage has nothing to do with GenAI" option was
  never on the annotation menu. consensus_label='unclear' is assigned whenever EITHER rater said
  'unclear'; 'disagreement' is assigned when both gave a definite but DIFFERENT non-unclear label.
  'substantive_adoption'/'generic_or_background' consensus values are, by construction, cases
  where BOTH raters independently gave that exact same label (verified: agreement count on the
  diagonal of the gpt55 x claude crosstab exactly equals the count of each of those two
  consensus_label values).

  => Alternative (a) "strict-consensus index" = count of passages with
     consensus_label == 'substantive_adoption' (both raters agree substantive). Directly available.
  => Alternative (b) "GenAI-related index": the task's literal 'not_genai_related' class does not
     exist in this file (see above -- there is no such option because all passages are already
     dictionary hits). The strict-consensus GenAI-relatedness notion actually present in the data
     is consensus_label in {'substantive_adoption','generic_or_background'} -- i.e. both raters
     independently agree the passage is genuinely about GenAI, whether substantively or only in a
     generic/background capacity. 'unclear' and 'disagreement' rows (no consensus reached) are
     excluded from both (a) and (b), exactly as they would be excluded from a hypothetical
     not_genai_related bucket.

Merge rule: Firm_ID (int in the CSV) -> zero-padded 6-char string, joined to Focal_ID x Year in the
08A pack. Firm-years with NO rows in the consensus file get count=0 for all three alt indices
(confirmed: only 105 of 852 unique Focal_ID x Year combinations in the regression panel, covering
122 of 1017 dyad rows, have any consensus-file coverage at all -- this sparsity is inherent to the
annotation subsample and is reported, not concealed).

Partner index: NOT touched. Power_Pressure is left EXACTLY as computed by the canonical recipe
(clip(-Power_Diff,0) * clip(Partner_GenAI_Index_ORIGINAL - Focal_GenAI_Index_ORIGINAL, 0)) for ALL
specifications below, including the alternative-Focal-index H3 runs. Rationale (documented, not a
tuning choice): recomputing Power_Pressure by mixing an ORIGINAL Partner_GenAI_Index
(keyword-frequency basis) with an ALTERNATIVE Focal index (passage-count basis) would create a
"Partner ahead of Focal" gap measured in two incommensurable units glued together -- exactly the
kind of improvised reweighting the task brief says not to fake. Holding Power_Pressure fixed at its
established, already-published construction and swapping ONLY the "Focal_GenAI_Index" regressor
(as a main effect, and as the interacted variable in the H2/H3 interaction terms) is the
conservative, exact-recipe-preserving reading of "Partner index stays original."
"""
from __future__ import annotations
import os

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

SCRATCH = Path(str(os.environ.get("PAPER2_OUT_DIR", Path(__file__).resolve().parent / "_out")))
SCRATCH.mkdir(parents=True, exist_ok=True)
LOG_PATH = SCRATCH / "job1_measurement_sensitivity_log.txt"
RESULTS_PATH = SCRATCH / "job1_measurement_sensitivity_results.json"

MAIN_PACK = Path(r"<PROJECT_ROOT>\data\processed_data\08A_main_regression_package.xlsx")
CONSENSUS_CSV = Path(
    r"E:\paper2  daxiu\73ae4696cf54747044a03a936c4bb958_744934475e1139b8c27898b82ae5bbf0_8"
    r"\paper2_github_replication\data\full_sample_gpt55_claude_consensus_labels.csv"
)

CONTROLS = ["Focal_Size", "Focal_Lev", "Focal_Age", "Focal_CashFlow", "Focal_SoE", "Focal_HHI",
            "Partner_Size", "Partner_Lev", "Partner_ROA"]

LOG: list[str] = []
RESULTS: list[dict] = []


def log(msg: str = "") -> None:
    LOG.append(str(msg))
    print(str(msg)[:220])


def prep_pack(df: pd.DataFrame) -> pd.DataFrame:
    """Mirrors prep_pack() from the round-2 backtest / 13_prepare_publication_exhibits.py exactly."""
    df = df.copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Focal_Industry"] = df["Focal_Industry"].astype(str)
    df["Focal_ID"] = df["Focal_ID"].astype(str)
    df["Focal_SoE"] = pd.to_numeric(df["Focal_SoE"], errors="coerce")
    df["Supplier_Dominance"] = (-pd.to_numeric(df["Power_Diff"], errors="coerce")).clip(lower=0)
    df["Partner_Ahead"] = (
        pd.to_numeric(df["Partner_GenAI_Index"], errors="coerce") - pd.to_numeric(df["Focal_GenAI_Index"], errors="coerce")
    ).clip(lower=0)
    df["Power_Pressure"] = df["Supplier_Dominance"] * df["Partner_Ahead"]
    return df


def fit_model(df: pd.DataFrame, rhs_terms: list[str], cluster_col: str = "Focal_Industry"):
    formula = "Focal_ROA ~ " + " + ".join(rhs_terms + ["C(Focal_Industry)", "C(Year)"])
    model = smf.ols(formula=formula, data=df, missing="drop")
    idx = model.data.row_labels
    fit = model.fit(cov_type="cluster", cov_kwds={"groups": df.loc[idx, cluster_col]})
    return fit, df.loc[idx].copy()


def term_row(fit, term):
    return {
        "coef": float(fit.params[term]) if term in fit.params.index else None,
        "se": float(fit.bse[term]) if term in fit.params.index else None,
        "p": float(fit.pvalues[term]) if term in fit.params.index else None,
        "n": int(fit.nobs),
        "r2": float(fit.rsquared),
    }


log("=" * 100)
log("JOB 1 -- MEASUREMENT-SENSITIVITY PANEL RE-ESTIMATION (round 3)")
log("Decision rule: exact-recipe-only, one run per target, no tuning.")
log("=" * 100)

# --- load canonical panel ---
main_raw = pd.read_excel(MAIN_PACK, sheet_name="main_winsorized", dtype={"Focal_ID": str, "Partner_ID": str})
main_df = prep_pack(main_raw)
log(f"08A main_winsorized rows: {len(main_df)}  Year range: {main_df['Year'].min()}-{main_df['Year'].max()}")

# --- load consensus labels, normalize Firm_ID ---
cons = pd.read_csv(CONSENSUS_CSV)
log(f"Consensus CSV rows: {len(cons)}  cols: {list(cons.columns)}")
cons["Firm_ID_norm"] = cons["Firm_ID"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip().str.zfill(6)
cons["Year"] = cons["Year"].astype(int)

label_counts = cons["consensus_label"].value_counts(dropna=False).to_dict()
log(f"consensus_label value counts (ACTUAL schema, checked not assumed): {label_counts}")
log("NOTE: no 'not_genai_related' value exists in this file -- all 1,256 passages already passed the "
    "ORIGINAL dictionary keyword screen, so annotators were never offered a not-GenAI-related option. "
    "See module docstring STEP 0b for the full reasoning behind the (a)/(b) operationalization below.")

# --- build the three passage-count firm-year indices ---
grp = cons.groupby(["Firm_ID_norm", "Year"])
n_all = grp.size().rename("n_all_matched")
n_strict = cons[cons["consensus_label"] == "substantive_adoption"].groupby(["Firm_ID_norm", "Year"]).size().rename("n_strict_substantive")
n_related = cons[cons["consensus_label"].isin(["substantive_adoption", "generic_or_background"])].groupby(["Firm_ID_norm", "Year"]).size().rename("n_genai_related")

fy_counts = pd.concat([n_all, n_strict, n_related], axis=1).fillna(0).reset_index()
log(f"Unique (Firm_ID_norm,Year) combinations with any consensus coverage: {len(fy_counts)}")

main_df = main_df.merge(
    fy_counts, left_on=["Focal_ID", "Year"], right_on=["Firm_ID_norm", "Year"], how="left"
)
for c in ["n_all_matched", "n_strict_substantive", "n_genai_related"]:
    main_df[c] = main_df[c].fillna(0.0)

n_covered_dyadrows = (main_df["n_all_matched"] > 0).sum()
n_covered_fy = fy_counts[["Firm_ID_norm", "Year"]].merge(
    main_df[["Focal_ID", "Year"]].drop_duplicates(), left_on=["Firm_ID_norm", "Year"], right_on=["Focal_ID", "Year"]
).shape[0]
log(f"Dyad rows (out of {len(main_df)}) whose FOCAL firm-year has >=1 consensus passage: {int(n_covered_dyadrows)}")
log(f"Unique Focal_ID x Year combos in the panel covered by the consensus file: {n_covered_fy} "
    f"(out of {main_df[['Focal_ID','Year']].drop_duplicates().shape[0]} unique Focal_ID x Year combos total)")
log("=> The alternative indices are ZERO for all uncovered firm-years, per task instruction "
    "('passages not in the consensus file mean zero hits that year'). This is a genuine sparsity "
    "limitation of the annotation subsample, not a bug; reported plainly.")

main_df["IDX_ALLMATCHED"] = np.log1p(main_df["n_all_matched"])
main_df["IDX_STRICT"] = np.log1p(main_df["n_strict_substantive"])
main_df["IDX_RELATED"] = np.log1p(main_df["n_genai_related"])

for c in ["IDX_ALLMATCHED", "IDX_STRICT", "IDX_RELATED"]:
    nz = int((main_df[c] > 0).sum())
    log(f"{c}: nonzero count={nz}/{len(main_df)}  mean={main_df[c].mean():.4f}  max={main_df[c].max():.4f}")

orig_nz = int((main_df["Focal_GenAI_Index"] > 0).sum())
log(f"For reference, ORIGINAL Focal_GenAI_Index (keyword-frequency, full MD&A, whole panel): "
    f"nonzero count={orig_nz}/{len(main_df)}  mean={main_df['Focal_GenAI_Index'].mean():.4f}")

# ===========================================================================
# Regressions: H1 (main effect), H2-contemporaneous (RnD interaction), H3 (Power_Pressure interaction)
# cluster Focal_Industry (canonical default), Power_Pressure held at its ORIGINAL construction throughout.
# ===========================================================================
INDEX_LABELS = {
    "ORIGINAL_Focal_GenAI_Index": "Focal_GenAI_Index",
    "IDX_ALLMATCHED_(comparator,_no_filter)": "IDX_ALLMATCHED",
    "IDX_STRICT_(a)_substantive_only": "IDX_STRICT",
    "IDX_RELATED_(b)_substantive_or_generic": "IDX_RELATED",
}

for label, col in INDEX_LABELS.items():
    log("\n" + "#" * 100)
    log(f"# INDEX: {label}  (column={col})")
    log("#" * 100)

    # H1
    try:
        rhs = [col] + CONTROLS
        fit, used = fit_model(main_df, rhs, cluster_col="Focal_Industry")
        r = term_row(fit, col)
        log(f"H1  [{col}]: coef={r['coef']:.6f} se={r['se']:.6f} p={r['p']:.4f} N={r['n']} R2={r['r2']:.4f}")
        RESULTS.append({"index": label, "column": col, "hypothesis": "H1_main_effect", "term": col, **r})
    except Exception as e:
        log(f"H1 [{col}] CRASHED: {e}")

    # H2 contemporaneous (Focal_RnD_Ratio interaction)
    try:
        rhs = [col] + CONTROLS + ["Focal_RnD_Ratio", f"{col}:Focal_RnD_Ratio"]
        term = f"{col}:Focal_RnD_Ratio"
        fit, used = fit_model(main_df, rhs, cluster_col="Focal_Industry")
        r = term_row(fit, term)
        log(f"H2c [{col}]: coef={r['coef']:.6f} se={r['se']:.6f} p={r['p']:.4f} N={r['n']} R2={r['r2']:.4f}")
        RESULTS.append({"index": label, "column": col, "hypothesis": "H2_contemporaneous_RnD", "term": term, **r})
    except Exception as e:
        log(f"H2c [{col}] CRASHED: {e}")

    # H3 (Power_Pressure interaction; Power_Pressure = ORIGINAL, unchanged)
    try:
        rhs = [col] + CONTROLS + ["Power_Pressure", f"{col}:Power_Pressure"]
        term = f"{col}:Power_Pressure"
        fit, used = fit_model(main_df, rhs, cluster_col="Focal_Industry")
        r = term_row(fit, term)
        log(f"H3  [{col}]: coef={r['coef']:.6f} se={r['se']:.6f} p={r['p']:.4f} N={r['n']} R2={r['r2']:.4f}")
        RESULTS.append({"index": label, "column": col, "hypothesis": "H3_PowerPressure", "term": term, **r})
    except Exception as e:
        log(f"H3 [{col}] CRASHED: {e}")

# ===========================================================================
log("\n" + "=" * 100)
log("SUMMARY TABLE (coef / se / p / N)")
log("=" * 100)
for r in RESULTS:
    coef = r.get("coef")
    se = r.get("se")
    p = r.get("p")
    n = r.get("n")
    log(f"{r['index']:42s} {r['hypothesis']:26s} coef={coef:+.5f} se={se:.5f} p={p:.4f} N={n}")

with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(RESULTS, f, indent=2, default=str)

print("DONE. Log ->", str(LOG_PATH))
print("Results JSON ->", str(RESULTS_PATH))
