"""
Extension of common.py for the R1.8 construct-validity battery.
Reuses load_pack/fit_model/CONTROLS exactly as verified earlier this session;
adds the additional moderator constructs and battery-running helpers.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from common import load_pack, fit_model, CONTROLS  # noqa: F401


def extend_pack(df: pd.DataFrame) -> pd.DataFrame:
    """Add the additional moderator-construct columns needed for the battery.
    df must already have Supplier_Dominance / Partner_Ahead / Power_Pressure from prep_pack().
    """
    df = df.copy()

    power_diff = pd.to_numeric(df["Power_Diff"], errors="coerce")
    focal_genai = pd.to_numeric(df["Focal_GenAI_Index"], errors="coerce")
    partner_genai = pd.to_numeric(df["Partner_GenAI_Index"], errors="coerce")

    # --- NaN-safe binary constructs ---
    partner_dom_bin = pd.Series(np.nan, index=df.index, dtype=float)
    mask_pd = power_diff.notna()
    partner_dom_bin.loc[mask_pd] = (power_diff.loc[mask_pd] < 0).astype(float)
    df["PartnerDominance_bin"] = partner_dom_bin

    ahead_bin = pd.Series(np.nan, index=df.index, dtype=float)
    mask_genai = focal_genai.notna() & partner_genai.notna()
    ahead_bin.loc[mask_genai] = (partner_genai.loc[mask_genai] > focal_genai.loc[mask_genai]).astype(float)
    df["Partner_Ahead_bin"] = ahead_bin

    # sanity: continuous constructs already present via prep_pack (Supplier_Dominance, Partner_Ahead)
    assert "Supplier_Dominance" in df.columns and "Partner_Ahead" in df.columns

    df["Rela_Purchase_Ratio"] = pd.to_numeric(df["Rela_Purchase_Ratio"], errors="coerce")
    df["Ln_Dyad_Duration"] = pd.to_numeric(df["Ln_Dyad_Duration"], errors="coerce")

    # --- composite M columns for rows 1-5 (product constructs; NaN propagates automatically) ---
    df["PP_code"] = df["Supplier_Dominance"] * df["Partner_Ahead"]                       # row 1 (== Power_Pressure)
    df["PP_prose"] = df["PartnerDominance_bin"] * df["Partner_Ahead"]                    # row 2
    df["PP_purchase"] = df["Rela_Purchase_Ratio"] * df["Partner_Ahead"]                  # row 3
    df["PP_duration"] = df["Ln_Dyad_Duration"] * df["Partner_Ahead"]                     # row 4
    df["PP_binahead"] = df["Supplier_Dominance"] * df["Partner_Ahead_bin"]               # row 5

    # cross-check row1 M equals the pre-existing Power_Pressure column from common.py
    diff = (df["PP_code"] - df["Power_Pressure"]).abs()
    assert (diff.fillna(0) < 1e-9).all(), "PP_code does not match Power_Pressure from common.py"

    return df


def find_term(fit, components: list[str]) -> str | None:
    """Locate a patsy param label matching `components` regardless of factor order."""
    target = set(components)
    for lbl in fit.params.index:
        if set(lbl.split(":")) == target:
            return lbl
    return None


def extract_term(fit, components: list[str], n_clusters: int | None = None) -> dict:
    lbl = find_term(fit, components)
    if lbl is None:
        return {
            "term": ":".join(components),
            "status": "TERM_NOT_FOUND",
            "coef": None, "se": None, "p": None,
            "N": int(fit.nobs), "n_clusters": n_clusters,
        }
    return {
        "term": lbl,
        "status": "ok",
        "coef": float(fit.params[lbl]),
        "se": float(fit.bse[lbl]),
        "p": float(fit.pvalues[lbl]),
        "N": int(fit.nobs),
        "n_clusters": n_clusters,
    }


def safe_fit(df: pd.DataFrame, rhs_terms: list[str], cluster_var: str, extra_label: str = ""):
    """Wrap fit_model with error/warning capture. Returns (fit_or_None, used_df_or_None, diag dict)."""
    import warnings
    diag = {"warnings": [], "error": None}
    try:
        with warnings.catch_warnings(record=True) as wlist:
            warnings.simplefilter("always")
            fit, used = fit_model(df, rhs_terms, cluster_var=cluster_var)
        for w in wlist:
            diag["warnings"].append(f"{w.category.__name__}: {w.message}")
        # rank check: compare model rank to number of exog columns
        try:
            k = fit.model.exog.shape[1]
            rank = np.linalg.matrix_rank(fit.model.exog)
            if rank < k:
                diag["warnings"].append(f"RANK_DEFICIENT: exog has {k} cols but rank {rank}")
        except Exception as e:
            diag["warnings"].append(f"rank check failed: {e}")
        # NaN check on params/bse
        if fit.params.isna().any() or fit.bse.isna().any():
            diag["warnings"].append("NaN present in params or bse")
        n_clusters = used[cluster_var].nunique()
        return fit, used, n_clusters, diag
    except Exception as e:
        diag["error"] = f"{type(e).__name__}: {e}"
        return None, None, None, diag


def run_row_battery(df_main: pd.DataFrame, df_strict: pd.DataFrame, row_name: str,
                     rhs_terms_fn, target_terms_fn, exclude_years=(2024, 2025)):
    """
    rhs_terms_fn: () -> list[str] RHS terms (without FE, without cluster)
    target_terms_fn: () -> list[list[str]]  list of component-lists to extract (usually 1, but 3 for row8)
    Returns a list of result rows (dicts) covering both samples x 3 conditions x all target terms.
    """
    results = []
    samples = {"main": df_main, "strict": df_strict}
    conditions = [
        ("i_industry_full", "Focal_Industry", False),
        ("ii_id_full", "Focal_ID", False),
        ("iii_id_excl2024_2025", "Focal_ID", True),
    ]
    for sample_name, df in samples.items():
        for cond_name, cluster_var, excl in conditions:
            use_df = df[~df["Year"].isin(exclude_years)] if excl else df
            rhs_terms = rhs_terms_fn()
            fit, used, n_clusters, diag = safe_fit(use_df, rhs_terms, cluster_var)
            year_min = int(use_df["Year"].min())
            year_max = int(use_df["Year"].max())
            years_present = sorted(use_df["Year"].unique().tolist())
            if fit is None:
                for comp in target_terms_fn():
                    results.append({
                        "row": row_name, "sample": sample_name, "condition": cond_name,
                        "cluster_var": cluster_var, "term": ":".join(comp),
                        "status": "FIT_ERROR", "coef": None, "se": None, "p": None,
                        "N": None, "n_clusters": None,
                        "years_in_subsample": f"{year_min}-{year_max}",
                        "error": diag["error"], "warnings": "; ".join(diag["warnings"]),
                    })
                continue
            for comp in target_terms_fn():
                row = extract_term(fit, comp, n_clusters=n_clusters)
                results.append({
                    "row": row_name, "sample": sample_name, "condition": cond_name,
                    "cluster_var": cluster_var, "term": row["term"], "status": row["status"],
                    "coef": row["coef"], "se": row["se"], "p": row["p"],
                    "N": row["N"], "n_clusters": row["n_clusters"],
                    "years_in_subsample": f"{year_min}-{year_max}" if excl else f"{year_min}-{year_max}",
                    "error": diag["error"], "warnings": "; ".join(diag["warnings"]),
                })
    return results
