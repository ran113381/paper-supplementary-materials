"""J3-D7 a9: independent re-check (read-only, stdout only) of the facts the D7 answer relies on.
Inputs: WB-May (e41356a blob, original May workbook), current workbook, frozen predictions CSV.
 1. Five-term rule vs AI-assisted drafts on the 122 disagreements (+ discrimination controls).
 2. Published final_label vs draft.
 3. coder1/coder2 column diagnostics (types, notes, labels on non-matched passages, U by stratum).
 4. Concordant-binary subset metrics (Wilson 95% CI) for the four methods.
 5. Worst/best bounds over the non-concordant passages for the dictionary.
 6. One-sided 95% Clopper-Pearson upper bounds for 0/k.
"""
import subprocess, sys, io, re, collections, math
sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, openpyxl
from scipy.stats import beta, norm
R = r"E:/paper2  daxiu/73ae4696cf54747044a03a936c4bb958_744934475e1139b8c27898b82ae5bbf0_8/paper2_github_replication"
b = subprocess.run(["git", "--no-optional-locks", "-C", R, "show", "e41356a:data/Table_3C_SOTA_validation_metrics.csv"], capture_output=True, check=True).stdout
def sheet(src, name):
    wb = openpyxl.load_workbook(src, read_only=True, data_only=True)
    rows = list(wb[name].iter_rows(values_only=True))
    return pd.DataFrame(rows[1:], columns=rows[0])
ab_may = sheet(io.BytesIO(b), "Annotation_Blind")
ab_cur = sheet(R + "/data/genai_gold_standard_adjudication_workbook.xlsx", "Annotation_Blind")
pred = pd.read_csv(R + "/data/Table_3C_validation_predictions.csv", encoding="utf-8-sig")
print("=== RESULTS ===")
print("AB_may cols:", list(ab_may.columns))
norm_lab = lambda v: None if v is None or (isinstance(v, float) and math.isnan(v)) or str(v).strip() == "" else str(v).strip().split(".")[0]
for df in (ab_may, ab_cur):
    for c in ("coder1_label", "coder2_label", "adjudication_label", "final_label"):
        if c in df.columns:
            df[c + "_n"] = df[c].map(norm_lab)
m = ab_may.merge(pred[["sample_id", "sample_group", "dictionary_hit"]], on="sample_id", how="left", validate="1:1")
print("merge check: rows", len(m), "missing stratum", int(m["sample_group"].isna().sum()))
dis =m[m["coder1_label_n"] != m["coder2_label_n"]]
uu = m[(m["coder1_label_n"] == "U") & (m["coder2_label_n"] == "U")]
conc = m[(m["coder1_label_n"] == m["coder2_label_n"]) & m["coder1_label_n"].isin(["0", "1"])]
print(f"[counts] n={len(m)} disagreements={len(dis)} both-U={len(uu)} concordant-binary={len(conc)} agree-any={len(m)-len(dis)}")
TERMS = ["大模型", "大语言模型", "预训练模型", "LLM", "GPT"]
def rule(t, terms=TERMS):
    t = str(t); return "1" if any(x.lower() in t.lower() for x in terms) else "0"
txtcol = "mdna_passage"
d = dis.copy()
d["rule"] = d[txtcol].map(rule)
d["draft"] = d["adjudication_label_n"]
binary = d[d["draft"].isin(["0", "1"])]
print(f"[1] drafts: dist={d['draft'].value_counts().to_dict()} | five-term rule == draft on binary drafts: {(binary['rule']==binary['draft']).sum()}/{len(binary)}")
print("    non-binary drafts:", d.loc[~d['draft'].isin(['0','1']), ['sample_id','draft','rule']].values.tolist())
alt1 = (binary["dictionary_hit"].astype(str).str[0] == binary["draft"]).sum() if "dictionary_hit" in binary.columns else "n/a"
print(f"    control A: rule 'dictionary_hit==1' == draft: {alt1}/{len(binary)}")
for drop in TERMS:
    tt = [x for x in TERMS if x != drop]
    print(f"    control B: rule without '{drop}' == draft: {(binary[txtcol].map(lambda t: rule(t, tt))==binary['draft']).sum()}/{len(binary)}")
c1 = (binary["coder1_label_n"] == binary["draft"]).sum(); c2 = (binary["coder2_label_n"] == binary["draft"]).sum()
print(f"    control C: draft==coder1 {c1}/{len(binary)}, draft==coder2 {c2}/{len(binary)}")
cur = ab_cur.set_index("sample_id")
d["final_pub"] = d["sample_id"].map(cur["final_label_n"])
print(f"[2] published final_label == May draft on 122: {(d['final_pub']==d['draft']).sum()}/122; differing: {d.loc[d['final_pub']!=d['draft'], ['sample_id','draft','final_pub']].values.tolist()}")
pg = pred.set_index("sample_id")
print(f"    published final_label (workbook) == predictions gold_binary on 600: {(cur['final_label_n'].astype(str)==pg.reindex(cur.index)['gold_binary'].astype(str)).sum()}/600")
# 3. coder diagnostics
for c in ("coder1", "coder2"):
    raw = m[c + "_label"]
    types = collections.Counter(type(v).__name__ for v in raw)
    notes = m[c + "_notes"].map(lambda v: "" if v is None else str(v))
    print(f"[3] {c}: label cell types={dict(types)} | distinct notes={notes.nunique()} | top notes={notes.value_counts().head(2).to_dict()}")
grp = "sample_group"
nh = m[m["dictionary_hit"].astype(str).str[0] == "0"]
print(f"    non-matched passages n={len(nh)}: coder1 dist={nh['coder1_label_n'].value_counts().to_dict()} coder2 dist={nh['coder2_label_n'].value_counts().to_dict()}")
print(f"    coder2 'U' by stratum: {m.loc[m['coder2_label_n']=='U', grp].value_counts().to_dict()} | coder1 'U' by stratum: {m.loc[m['coder1_label_n']=='U', grp].value_counts().to_dict()}")
dn = dis[dis["dictionary_hit"].astype(str).str[0] == "0"]
print(f"    non-matched disagreements: {len(dn)}; coder pairs={collections.Counter(zip(dn['coder1_label_n'], dn['coder2_label_n']))}")
print(f"    concordant-binary by stratum: {conc[grp].value_counts().to_dict()}; non-concordant by stratum: {m.loc[~m.index.isin(conc.index), grp].value_counts().to_dict()}")
# 4. metrics on concordant subset
def wilson(k, n, z=1.959964):
    if n == 0: return (float('nan'), float('nan'))
    p = k / n; den = 1 + z*z/n; c = (p + z*z/(2*n)) / den; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return (c - h, c + h)
def metr(y, yhat, label):
    y = np.asarray(y, int); yhat = np.asarray(yhat, int)
    tp = int(((y==1)&(yhat==1)).sum()); fp = int(((y==0)&(yhat==1)).sum()); tn = int(((y==0)&(yhat==0)).sum()); fn = int(((y==1)&(yhat==0)).sum())
    P = tp/(tp+fp) if tp+fp else float('nan'); Rr = tp/(tp+fn) if tp+fn else float('nan'); F = 2*P*Rr/(P+Rr) if P+Rr else float('nan')
    pl, ph = wilson(tp, tp+fp); rl, rh = wilson(tp, tp+fn)
    print(f"    {label}: n={len(y)} TP/FP/TN/FN={tp}/{fp}/{tn}/{fn} P={P:.4f} [{pl:.4f},{ph:.4f}] R={Rr:.4f} [{rl:.4f},{rh:.4f}] F1={F:.4f}")
    return tp, fp, tn, fn
cc = conc.set_index("sample_id").join(pg[["dictionary_pred", "llm_consensus_pred", "finbert_pred", "hybrid_pred", "gold_binary"]])
cc["y"] = cc["coder1_label_n"].astype(int)
print("[4] concordant-binary subset (gold = shared coder label):")
metr(cc["y"], cc["dictionary_pred"], "Dictionary")
cov = cc[cc["llm_consensus_pred"].notna()]
metr(cov["y"], cov["llm_consensus_pred"].astype(int), "Strict consensus (covered only)")
print(f"      strict-consensus coverage on subset: {len(cov)}/{len(cc)} = {len(cov)/len(cc):.4f}")
metr(cc["y"], cc["finbert_pred"], "FinBERT")
metr(cc["y"], cc["hybrid_pred"], "Hybrid")
print("    positive control (published gold, all 600):")
metr(pred["gold_binary"], pred["dictionary_pred"], "Dictionary/published")
# 5. bounds over non-concordant passages (dictionary)
nc = m[~m.index.isin(conc.index)].set_index("sample_id").join(pg[["dictionary_pred"]])
base_tp = int(((cc.y==1)&(cc.dictionary_pred==1)).sum()); base_fp = int(((cc.y==0)&(cc.dictionary_pred==1)).sum()); base_fn = int(((cc.y==1)&(cc.dictionary_pred==0)).sum())
hit = int((nc.dictionary_pred==1).sum()); nonhit = int((nc.dictionary_pred==0).sum())
# worst: hits labelled 0 (FP), non-hits labelled 1 (FN); best: hits labelled 1 (TP), non-hits labelled 0 (TN)
wtp, wfp, wfn = base_tp, base_fp + hit, base_fn + nonhit
btp, bfp, bfn = base_tp + hit, base_fp, base_fn
f = lambda tp, fp, fn: (tp/(tp+fp), tp/(tp+fn), 2*tp/(2*tp+fp+fn))
print(f"[5] non-concordant n={len(nc)} (matched {hit}, non-matched {nonhit}); dictionary worst P/R/F1={tuple(round(x,4) for x in f(wtp,wfp,wfn))} best={tuple(round(x,4) for x in f(btp,bfp,bfn))}")
# 6. Clopper-Pearson one-sided 95% upper bound for 0/k
for k in (121, 150, 244, 300):
    print(f"[6] 0/{k}: one-sided 95% CP upper = {1-0.05**(1/k):.4f} (beta.ppf check {beta.ppf(0.95,1,k):.4f})")
print("=== END RESULTS ===")
