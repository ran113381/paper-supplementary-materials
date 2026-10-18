"""J3-D7 a14: read-only, stdout only.
 1. WB-May Disagreement_Review: cell types of adjudication_label/final_label; rows where DR label != AB final_label.
    Positive control: same comparison of AB.final_label with itself -> 0 differences; and DR vs AB adjudication_label.
 2. Cohen's kappa (three-class, binary excluding U) for coder1 vs coder2.
 3. 477 concordant subset: strict consensus with abstentions counted as non-detections; bootstrap 95% CI for F1 (2,000, seed 42).
"""
import subprocess, sys, io, math
sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, openpyxl
from sklearn.metrics import cohen_kappa_score
R = r"E:/paper2  daxiu/73ae4696cf54747044a03a936c4bb958_744934475e1139b8c27898b82ae5bbf0_8/paper2_github_replication"
b = subprocess.run(["git", "--no-optional-locks", "-C", R, "show", "e41356a:data/Table_3C_SOTA_validation_metrics.csv"], capture_output=True, check=True).stdout
wb = openpyxl.load_workbook(io.BytesIO(b), read_only=True, data_only=True)
def raw(name):
    rows = list(wb[name].iter_rows(values_only=True)); return rows[0], rows[1:]
print("=== RESULTS ===")
hdr, rows = raw("Disagreement_Review"); ia = hdr.index("adjudication_label"); ifl = hdr.index("final_label"); iid = hdr.index("sample_id")
ahdr, arows = raw("Annotation_Blind"); aid = ahdr.index("sample_id"); afl = ahdr.index("final_label"); aad = ahdr.index("adjudication_label")
abf = {r[aid]: str(r[afl]).split(".")[0] for r in arows}; aba = {r[aid]: str(r[aad]).split(".")[0] for r in arows}
types = {"adjudication_label": {}, "final_label": {}}
diff = []; diff_adj = []; ints = []
for r in rows:
    for col, i in (("adjudication_label", ia), ("final_label", ifl)):
        t = type(r[i]).__name__; types[col][t] = types[col].get(t, 0) + 1
        if isinstance(r[i], int): ints.append((r[iid], col, r[i]))
    if str(r[ifl]).split(".")[0] != abf[r[iid]]: diff.append((r[iid], str(r[ifl]), abf[r[iid]]))
    if str(r[ia]).split(".")[0] != aba[r[iid]]: diff_adj.append((r[iid], str(r[ia]), aba[r[iid]]))
print("[1] DR rows", len(rows), "| cell types", types)
print("    int-typed cells:", ints)
print("    DR.final_label != AB.final_label:", len(diff), diff)
print("    DR.adjudication_label != AB.adjudication_label:", len(diff_adj), diff_adj)
print("    positive control AB.final vs AB.final differences:", sum(1 for k in abf if abf[k] != abf[k]))
c1 = [str(r[ahdr.index("coder1_label")]).split(".")[0] for r in arows]; c2 = [str(r[ahdr.index("coder2_label")]).split(".")[0] for r in arows]
print(f"[2] kappa three-class={cohen_kappa_score(c1, c2):.4f}", end=" ")
bb = [(x, y) for x, y in zip(c1, c2) if x in "01" and y in "01" and x != "U" and y != "U"]
print(f"| binary (both non-U, n={len(bb)})={cohen_kappa_score([x for x,_ in bb],[y for _,y in bb]):.4f}")
pred = pd.read_csv(R + "/data/Table_3C_validation_predictions.csv", encoding="utf-8-sig").set_index("sample_id")
ab = pd.DataFrame({"sample_id": [r[aid] for r in arows], "c1": c1, "c2": c2}).set_index("sample_id").join(pred)
cc = ab[(ab.c1 == ab.c2) & ab.c1.isin(["0", "1"])].copy(); cc["y"] = cc.c1.astype(int)
y = cc["y"].values; pos = int(y.sum())
sc = cc["llm_consensus_pred"]; tp_full = int(((cc.y == 1) & (sc == 1)).sum())
print(f"[3] n={len(cc)} positives={pos} | strict consensus full-subset recall (abstention = non-detection) = {tp_full}/{pos} = {tp_full/pos:.4f}")
rng = np.random.default_rng(42)
def f1(yy, pp):
    tp = ((yy == 1) & (pp == 1)).sum(); fp = ((yy == 0) & (pp == 1)).sum(); fn = ((yy == 1) & (pp == 0)).sum()
    return 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else np.nan
for col in ("dictionary_pred", "finbert_pred", "hybrid_pred"):
    pp = cc[col].astype(int).values; bs = []
    for _ in range(2000):
        ix = rng.integers(0, len(y), len(y)); bs.append(f1(y[ix], pp[ix]))
    print(f"    F1 {col}: {f1(y, pp):.4f} bootstrap95 [{np.nanpercentile(bs, 2.5):.4f}, {np.nanpercentile(bs, 97.5):.4f}]")
cov = cc[sc.notna()]; yy = cov.y.values; pp = cov.llm_consensus_pred.astype(int).values; bs = []
for _ in range(2000):
    ix = rng.integers(0, len(yy), len(yy)); bs.append(f1(yy[ix], pp[ix]))
print(f"    F1 strict consensus (covered n={len(cov)}): {f1(yy, pp):.4f} bootstrap95 [{np.nanpercentile(bs, 2.5):.4f}, {np.nanpercentile(bs, 97.5):.4f}]")
print("=== END RESULTS ===")
