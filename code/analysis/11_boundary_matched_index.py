# -*- coding: utf-8 -*-
"""
Word-boundary-hardened dictionary variant (revision robustness; R1.3 follow-up).

Motivation: short Latin-script dictionary terms can fire inside longer ordinary
words (GAN in "Morgan", RAG in "Storage", CoT in "Scott", LLM in "Wellman",
MoE in the steel grade "42CrMoE"). The published index handles this risk through
validation arms (dual-LLM consensus indices, precision weighting, pre-2022
exclusion). This script adds the direct fix as a robustness variant: every
Latin-script term edge must not be adjacent to another ASCII letter/digit
([A-Z0-9] on uppercase-normalized text). Chinese-script term edges are
unaffected. Note the rule removes substring collisions, not homograph
collisions (e.g. the LoRa IoT standard vs. LoRA fine-tuning share the same
uppercase surface form); homographs remain covered by the consensus-filter arm.

Pipeline:
  1. Reproduce the baseline longest-match-first, non-overlapping counts from
     the raw MD&A text panel and ASSERT they equal the regression package's
     Focal/Partner_GenAI_Freq_Clean on every firm-year with text (abort else).
  2. Recount under the boundary rule; rebuild ln(1+count) indices for focal and
     partner sides; rebuild Partner lead and Power_Pressure from the hardened
     indices (Supplier dominance is size-based and unchanged).
  3. Re-estimate H1 / H2 (contemporaneous) / H3 on the baseline specification
     (controls + industry & year FE, industry-clustered SEs).
  4. Report how many pre-2022 firm-years with a nonzero count survive the
     boundary rule, and how many firms' first-disclosure year moves.

Requires private inputs (excluded from this public repo; see DATA_AVAILABILITY.md):
    raw MD&A text panel parquet  (columns: Firm_ID, Year, segment/text column)
    08A_main_regression_package.xlsx  (main_winsorized)

Usage:
  python 11_boundary_matched_index.py <raw_mda_panel.parquet> <08A_main_regression_package.xlsx>
Output:
  ../../data/Table_boundary_robustness.csv (+ printed summary)
"""
from __future__ import annotations

import os
import re
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CSV = os.path.normpath(os.path.join(HERE, "..", "..", "data", "Table_boundary_robustness.csv"))
DICT = os.path.normpath(os.path.join(HERE, "..", "..", "data", "public", "04_genai_dictionary.xlsx"))

CONTROLS = ["Focal_Size", "Focal_Lev", "Focal_Age", "Focal_CashFlow", "Focal_SoE", "Focal_HHI",
            "Partner_Size", "Partner_Lev", "Partner_ROA"]

ASCII_ALNUM = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")


def safe_print(s):
    try:
        print(s)
    except UnicodeEncodeError:
        print(str(s).encode("ascii", "replace").decode("ascii"))


def load_terms():
    dic = pd.read_excel(DICT)
    term_col = "term" if "term" in dic.columns else dic.columns[1]
    terms = sorted({str(t).upper() for t in dic[term_col].dropna()}, key=len, reverse=True)
    return terms


def build_patterns(terms, boundary: bool):
    parts = []
    for t in terms:
        esc = re.escape(t)
        if boundary:
            lb = r"(?<![A-Z0-9])" if t[0] in ASCII_ALNUM else ""
            rb = r"(?![A-Z0-9])" if t[-1] in ASCII_ALNUM else ""
            parts.append(f"{lb}{esc}{rb}")
        else:
            parts.append(esc)
    return re.compile("|".join(parts))


def count_hits(pattern, text):
    return len(pattern.findall(text))


def fit_fe(df, rhs, cluster_col="Focal_Industry"):
    formula = "Focal_ROA ~ " + " + ".join(rhs + ["C(Focal_Industry)", "C(Year)"])
    model = smf.ols(formula=formula, data=df, missing="drop")
    idx = model.data.row_labels
    used = df.loc[idx]
    return model.fit(cov_type="cluster", cov_kwds={"groups": used[cluster_col]})


def main():
    raw_path, pack_path = sys.argv[1], sys.argv[2]
    terms = load_terms()
    pat_base = build_patterns(terms, boundary=False)
    pat_bnd = build_patterns(terms, boundary=True)

    raw = pd.read_parquet(raw_path)
    text_col = next(c for c in raw.columns if raw[c].dtype == object and
                    raw[c].astype(str).str.len().mean() > 200)
    raw["Firm_ID"] = raw["Firm_ID"].astype(str).str.zfill(6)
    raw["Year"] = pd.to_numeric(raw["Year"], errors="coerce").astype(int)
    safe_print(f"raw text panel: {len(raw)} firm-years, {raw['Year'].min()}-{raw['Year'].max()}, text col '{text_col}'")

    up = raw[text_col].astype(str).str.upper()
    raw["cnt_base"] = [count_hits(pat_base, t) for t in up]
    raw["cnt_bnd"] = [count_hits(pat_bnd, t) for t in up]
    counts = raw[["Firm_ID", "Year", "cnt_base", "cnt_bnd"]].drop_duplicates(["Firm_ID", "Year"])

    pack = pd.read_excel(pack_path, sheet_name="main_winsorized",
                         dtype={"Focal_ID": str, "Partner_ID": str})
    for c in pack.columns:
        if str(pack[c].dtype) in {"Int64", "Float64"}:
            pack[c] = pd.to_numeric(pack[c], errors="coerce")
    pack["Year"] = pd.to_numeric(pack["Year"], errors="coerce").astype(int)
    pack["Focal_Industry"] = pack["Focal_Industry"].astype(str)
    pack["Focal_ID"] = pack["Focal_ID"].astype(str).str.zfill(6)
    pack["Partner_ID"] = pack["Partner_ID"].astype(str).str.zfill(6)

    # ---- self-check 1: baseline recount == package Freq_Clean wherever text exists
    mism = 0
    checked = 0
    for side in ("Focal", "Partner"):
        m = pack.merge(counts, left_on=[f"{side}_ID", "Year"], right_on=["Firm_ID", "Year"], how="left")
        have = m["cnt_base"].notna() & m[f"{side}_GenAI_Freq_Clean"].notna()
        checked += int(have.sum())
        bad = m.loc[have & (m["cnt_base"] != m[f"{side}_GenAI_Freq_Clean"])]
        mism += len(bad)
        if len(bad):
            safe_print(f"  {side}: {len(bad)} mismatching firm-years, e.g.:")
            for _, r in bad.head(5).iterrows():
                safe_print(f"    {r[f'{side}_ID']} {r['Year']}: recount {r['cnt_base']} vs pack {r[f'{side}_GenAI_Freq_Clean']}")
    safe_print(f"self-check 1 (baseline recount vs package): {checked} firm-year sides checked, {mism} mismatches")
    if mism:
        raise SystemExit("ABORT: baseline matcher does not reproduce the package counts")

    # ---- self-check 2: package index is ln(1+count) upper-winsorized at its
    # own within-sample 99th percentile (the panel-build winsorization step)
    for side in ("Focal", "Partner"):
        raw_l = np.log1p(pack[f"{side}_GenAI_Freq_Clean"])
        q99 = raw_l.quantile(0.99)
        chk = pack[f"{side}_GenAI_Index"] - raw_l.clip(upper=q99)
        if chk.abs().max() > 1e-6:
            raise SystemExit(f"ABORT: {side} index is not clip(ln(1+Freq_Clean), q99)")
    safe_print("self-check 2 (index = ln(1+count) upper-winsorized at q99): PASS both sides")

    # ---- boundary indices (identical construction: log1p then within-sample q99 clip)
    for side in ("Focal", "Partner"):
        pack = pack.merge(counts.rename(columns={"Firm_ID": f"{side}_ID",
                                                 "cnt_base": f"{side}_cb", "cnt_bnd": f"{side}_cnt_bnd"}),
                          on=[f"{side}_ID", "Year"], how="left")
        fallback = pack[f"{side}_cnt_bnd"].isna()
        pack.loc[fallback, f"{side}_cnt_bnd"] = pack.loc[fallback, f"{side}_GenAI_Freq_Clean"]
        raw_l = np.log1p(pack[f"{side}_cnt_bnd"])
        pack[f"{side}_GenAI_Index_bnd"] = raw_l.clip(upper=raw_l.quantile(0.99))
        safe_print(f"  {side}: {int(fallback.sum())} rows without text fall back to package count")

    pack["Supplier_Dominance"] = (-pd.to_numeric(pack["Power_Diff"], errors="coerce")).clip(lower=0)
    pack["Partner_Ahead_bnd"] = (pack["Partner_GenAI_Index_bnd"] - pack["Focal_GenAI_Index_bnd"]).clip(lower=0)
    pack["Power_Pressure_bnd"] = pack["Supplier_Dominance"] * pack["Partner_Ahead_bnd"]
    pack["G_x_RnD_bnd"] = pack["Focal_GenAI_Index_bnd"] * pack["Focal_RnD_Ratio"]
    pack["G_x_PP_bnd"] = pack["Focal_GenAI_Index_bnd"] * pack["Power_Pressure_bnd"]

    changed = int((pack["Focal_cnt_bnd"] != pack["Focal_GenAI_Freq_Clean"]).sum())
    safe_print(f"focal dyad-rows whose count changes under the boundary rule: {changed}")

    # ---- pre-2022 collapse + first-disclosure shifts (on the text panel)
    pre = counts[counts["Year"] < 2022]
    safe_print(f"pre-2022 firm-years with nonzero count: baseline {int((pre['cnt_base'] > 0).sum())}, "
               f"boundary {int((pre['cnt_bnd'] > 0).sum())}")
    fd_base = counts[counts["cnt_base"] > 0].groupby("Firm_ID")["Year"].min()
    fd_bnd = counts[counts["cnt_bnd"] > 0].groupby("Firm_ID")["Year"].min()
    fd = pd.concat([fd_base.rename("base"), fd_bnd.rename("bnd")], axis=1)
    moved = int((fd["base"] != fd["bnd"]).sum() - fd["bnd"].isna().sum()) + int(fd["bnd"].isna().sum())
    later = int((fd["bnd"] > fd["base"]).sum())
    lost = int(fd["bnd"].isna().sum())
    safe_print(f"firms whose first-disclosure year changes: {moved} "
               f"(moves later: {later}; no disclosure left: {lost}; total disclosers baseline: {len(fd)})")

    # ---- re-estimation
    rows = []
    r1 = fit_fe(pack, ["Focal_GenAI_Index_bnd"] + CONTROLS)
    rows.append({"model": "H1 boundary-hardened", "term": "Focal_GenAI_Index_bnd",
                 "coef": r1.params["Focal_GenAI_Index_bnd"], "se": r1.bse["Focal_GenAI_Index_bnd"],
                 "p": r1.pvalues["Focal_GenAI_Index_bnd"], "n": int(r1.nobs)})
    r2 = fit_fe(pack, ["Focal_GenAI_Index_bnd", "Focal_RnD_Ratio", "G_x_RnD_bnd"] + CONTROLS)
    rows.append({"model": "H2 contemporaneous boundary-hardened", "term": "G_x_RnD_bnd",
                 "coef": r2.params["G_x_RnD_bnd"], "se": r2.bse["G_x_RnD_bnd"],
                 "p": r2.pvalues["G_x_RnD_bnd"], "n": int(r2.nobs)})
    r3 = fit_fe(pack, ["Focal_GenAI_Index_bnd", "Power_Pressure_bnd", "G_x_PP_bnd"] + CONTROLS)
    rows.append({"model": "H3 boundary-hardened", "term": "G_x_PP_bnd",
                 "coef": r3.params["G_x_PP_bnd"], "se": r3.bse["G_x_PP_bnd"],
                 "p": r3.pvalues["G_x_PP_bnd"], "n": int(r3.nobs)})
    out = pd.DataFrame(rows)
    for _, r in out.iterrows():
        safe_print(f"{r['model']:40s} b={r['coef']:+.4f} se={r['se']:.4f} p={r['p']:.4f} N={r['n']}")
    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    safe_print(f"written: {OUT_CSV}")


if __name__ == "__main__":
    main()
