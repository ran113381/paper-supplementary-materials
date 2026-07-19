# -*- coding: utf-8 -*-
"""
Build the false-positive-rate tables (by keyword category x year) promised in the
revision's response to R1.3, entirely from files inside this public package:

  inputs:  data/full_sample_gpt55_claude_consensus_labels.csv   (1,256 rows)
           data/public/04_genai_dictionary.xlsx                 (103 terms, 'group' col)
  outputs: data/Table_FP_rates_by_category_year.csv
           data/Table_FP_rates_by_category_year.md

Method: re-match each segment_text against the dictionary with the same
longest-match-first / uppercase-normalized convention used by the measurement
pipeline; a segment may hit terms from more than one category (counted in each).
"FP rate (vs substantive)" = share of matched segments whose dual-LLM consensus
is NOT substantive_adoption. "Strict non-GenAI rate" = share whose consensus is
not_genai_related. The pre-2022 headline reported to reviewers (154 matched
passages, zero substantive) is recomputed and printed as a self-check.

Run:  python data/build_fp_rate_tables.py   (pandas + openpyxl required)
"""
import pandas as pd
import re
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LABELS = os.path.join(HERE, "full_sample_gpt55_claude_consensus_labels.csv")
DICT = os.path.join(HERE, "public", "04_genai_dictionary.xlsx")
OUT_CSV = os.path.join(HERE, "Table_FP_rates_by_category_year.csv")
OUT_MD = os.path.join(HERE, "Table_FP_rates_by_category_year.md")

df = pd.read_csv(LABELS)
dic = pd.read_excel(DICT)

term_col = "term" if "term" in dic.columns else dic.columns[1]
group_col = "group" if "group" in dic.columns else dic.columns[-1]
terms = (
    dic[[term_col, group_col]]
    .dropna()
    .assign(term_upper=lambda d: d[term_col].astype(str).str.upper())
    .sort_values(key=lambda s: s.str.len() if s.name == "term_upper" else s,
                 by="term_upper", ascending=False)
)

def hit_groups(text):
    up = str(text).upper()
    groups = set()
    for t, g in zip(terms["term_upper"], terms[group_col]):
        if t and t in up:
            groups.add(g)
    return groups

df["hit_groups"] = df["segment_text"].map(hit_groups)

rows = []
for (year,), sub in df.groupby(["Year"]):
    all_groups = set().union(*sub["hit_groups"]) if len(sub) else set()
    for g in sorted(all_groups):
        m = sub[sub["hit_groups"].map(lambda s: g in s)]
        n = len(m)
        n_sub = (m["consensus_label"] == "substantive_adoption").sum()
        n_non = (m["consensus_label"] == "not_genai_related").sum()
        rows.append({
            "Year": year, "keyword_category": g, "matched_segments": n,
            "substantive_adoption": int(n_sub),
            "fp_rate_vs_substantive": round(1 - n_sub / n, 4) if n else None,
            "not_genai_related": int(n_non),
            "strict_non_genai_rate": round(n_non / n, 4) if n else None,
        })
tab = pd.DataFrame(rows).sort_values(["Year", "keyword_category"])
tab.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

pre2022 = df[df["Year"] < 2022]
pre_n = len(pre2022)
pre_sub = (pre2022["consensus_label"] == "substantive_adoption").sum()

with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("# False-Positive Rates by Keyword Category and Year\n\n")
    f.write("Recomputed from `full_sample_gpt55_claude_consensus_labels.csv` + the public "
            "dictionary; see `build_fp_rate_tables.py` for the method.\n\n")
    f.write(f"**Pre-2022 self-check**: {pre_n} dictionary-matched passages before 2022; "
            f"{pre_sub} labeled substantive_adoption by dual-LLM consensus "
            f"(reviewers were told 154 and zero).\n\n")
    f.write(tab.to_markdown(index=False))

print(f"pre-2022 matched: {pre_n}, substantive: {pre_sub}")
print(f"rows: {len(tab)} -> {OUT_CSV}")
