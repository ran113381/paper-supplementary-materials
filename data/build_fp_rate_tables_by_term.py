# -*- coding: utf-8 -*-
"""
Build the TERM-LEVEL false-positive table companion to
build_fp_rate_tables.py (which reports keyword category x year), entirely from
files inside this public package:

  inputs:  data/full_sample_segments_1256.csv                    (1,256 rows)
           data/full_sample_gpt55_claude_consensus_labels.csv    (consensus labels)
           data/public/04_genai_dictionary.xlsx                  (103 terms, 'group' col)
  outputs: data/Table_FP_rates_by_term.csv
           data/Table_FP_rates_by_term.md

Method: identical matcher to build_fp_rate_tables.py (uppercase normalization,
longest-match-first, non-overlapping); each matched segment is attributed to the
term(s) that actually fired inside it. Per term we report segment counts,
occurrence counts, the consensus-label composition (substantive / generic /
unclear-or-disagreement), the FP rate vs substantive among label-resolved
segments, and the share of that term's matched segments dated before 2022.

Self-checks (abort on failure):
  - total matched segments = 1,256
  - pre-2022 matched segments = 154 with zero substantive consensus
  - anchor terms reproduce the archived term audit
"""
from __future__ import annotations

import os
import re

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SEGMENTS = os.path.join(HERE, "full_sample_segments_1256.csv")
LABELS = os.path.join(HERE, "full_sample_gpt55_claude_consensus_labels.csv")
DICT = os.path.join(HERE, "public", "04_genai_dictionary.xlsx")
OUT_CSV = os.path.join(HERE, "Table_FP_rates_by_term.csv")
OUT_MD = os.path.join(HERE, "Table_FP_rates_by_term.md")

seg = pd.read_csv(SEGMENTS)
lab = pd.read_csv(LABELS)
dic = pd.read_excel(DICT)

term_col = "term" if "term" in dic.columns else dic.columns[1]
group_col = "group" if "group" in dic.columns else dic.columns[-1]
terms = dic[[term_col, group_col]].dropna().copy()
terms["upper"] = terms[term_col].astype(str).str.upper()
terms = terms.sort_values("upper", key=lambda s: s.str.len(), ascending=False)
pattern = re.compile("|".join(re.escape(t) for t in terms["upper"]))
group_of = dict(zip(terms["upper"], terms[group_col]))
display_of = dict(zip(terms["upper"], terms[term_col]))

if "segment_id" in lab.columns:
    lab_key = lab.set_index("segment_id")
else:
    lab_key = lab.copy()
    lab_key.index = seg["segment_id"].values

consensus_col = next(c for c in lab.columns if "consensus" in c.lower())

rows = []
n_matched_segments = 0
pre2022_ids = set()
pre2022_substantive = 0
per_term = {}

for _, r in seg.iterrows():
    text = str(r["segment_text"]).upper()
    hits = pattern.findall(text)
    # non-overlapping longest-match is what re.findall on a length-sorted
    # alternation delivers for these literal terms
    if not hits:
        continue
    n_matched_segments += 1
    year = int(r["Year"])
    sid = r["segment_id"]
    label = str(lab_key.loc[sid, consensus_col]) if sid in lab_key.index else "missing"
    if year < 2022:
        pre2022_ids.add(sid)
        if label == "substantive_adoption":
            pre2022_substantive += 1
    for t in set(hits):
        d = per_term.setdefault(t, {"segments": 0, "occurrences": 0, "substantive": 0,
                                    "generic": 0, "unresolved": 0, "pre2022_segments": 0})
        d["segments"] += 1
        d["occurrences"] += hits.count(t)
        if label == "substantive_adoption":
            d["substantive"] += 1
        elif label == "generic_or_background":
            d["generic"] += 1
        else:
            d["unresolved"] += 1
        if year < 2022:
            d["pre2022_segments"] += 1

assert n_matched_segments == 1256, f"matched segments {n_matched_segments} != 1256"
assert len(pre2022_ids) == 154, f"pre-2022 matched segments {len(pre2022_ids)} != 154"
assert pre2022_substantive == 0, f"pre-2022 substantive {pre2022_substantive} != 0"

out = []
for t, d in per_term.items():
    resolved = d["substantive"] + d["generic"]
    out.append({
        "term": display_of.get(t, t), "category": group_of.get(t, ""),
        "n_segments": d["segments"], "n_occurrences": d["occurrences"],
        "substantive_adoption": d["substantive"], "generic_or_background": d["generic"],
        "unclear_or_disagreement": d["unresolved"],
        "fp_rate_vs_substantive": (d["generic"] / resolved) if resolved else None,
        "pre2022_share_of_segments": d["pre2022_segments"] / d["segments"],
    })
df = pd.DataFrame(out).sort_values("n_segments", ascending=False)

anchors = {"大模型": 654, "GAN": 131, "AIGC": 91, "智能体": 74}
for term, want in anchors.items():
    got = int(df.loc[df["term"].astype(str).str.upper() == term.upper(), "n_segments"].iloc[0])
    assert got == want, f"anchor {term}: segments {got} != {want}"

df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("# Term-level false-positive table (dual-LLM consensus ground truth)\n\n")
    f.write(df.head(25).to_markdown(index=False))
    f.write("\n\n(full table in Table_FP_rates_by_term.csv)\n")

def safe_print(s):
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode("ascii", "replace").decode("ascii"))


safe_print(f"terms that fired: {len(df)}; matched segments: {n_matched_segments}; "
           f"pre-2022 segments: {len(pre2022_ids)} (substantive: {pre2022_substantive})")
safe_print("top-8 terms by matched segments:")
for _, r in df.head(8).iterrows():
    fp = f"{r['fp_rate_vs_substantive']:.3f}" if pd.notna(r["fp_rate_vs_substantive"]) else "  na "
    safe_print(f"  {str(r['term'])[:24]:24s} segs={int(r['n_segments']):4d} occ={int(r['n_occurrences']):4d} "
               f"fp_vs_sub={fp} pre2022_share={r['pre2022_share_of_segments']:.2f}")
safe_print(f"written: {OUT_CSV}")
