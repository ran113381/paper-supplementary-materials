"""Q7: re-score Table 6 methods under two positive-class constructions.

Purpose : Scheme S (current): LLM consensus positive = substantive_adoption only.
          Scheme G: positive = substantive_adoption OR generic_or_background.
          unclear -> 0, disagreement / non-hit (NaN) -> abstain, in both schemes
          (same as build_table3c_finbert_hybrid.py lines 264-273).
          Hybrid = LLM pred where not abstaining, else dictionary pred (lines 269-273).
          Dictionary and FinBERT predictions are taken as stored (FinBERT is NOT retrained,
          does not vary with scheme).
Input   : --pred CSV (Table_3C_validation_predictions.csv), --gold-col (default gold_binary);
          a re-adjudicated gold file with columns sample_id + gold column can be given via
          --gold-file / --gold-file-col to override gold labels.
Output  : stdout only (redirect to log). Positive control (scheme S vs published Table 6)
          must pass before scheme G is computed.
"""
import sys, argparse, math
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import pandas as pd

DEF = r"E:/paper2  daxiu/73ae4696cf54747044a03a936c4bb958_744934475e1139b8c27898b82ae5bbf0_8/paper2_github_replication/data/Table_3C_validation_predictions.csv"
ap = argparse.ArgumentParser()
ap.add_argument('--pred', default=DEF)
ap.add_argument('--gold-col', default='gold_binary')
ap.add_argument('--gold-file', default=None)
ap.add_argument('--gold-file-col', default='gold_binary')
ap.add_argument('--skip-control', action='store_true', help='skip the published-Table-6 control (only for a new gold standard)')
a = ap.parse_args()

d = pd.read_csv(a.pred, encoding='utf-8-sig', dtype={'Firm_ID': str})
if a.gold_file:
    g = pd.read_csv(a.gold_file, encoding='utf-8-sig')[['sample_id', a.gold_file_col]]
    d = d.merge(g, on='sample_id', how='left', validate='one_to_one')
    d['gold'] = d[a.gold_file_col]
else:
    d['gold'] = d[a.gold_col]
assert d['gold'].isin([0, 1]).all() and len(d) == 600, 'gold problem'
d['gold'] = d['gold'].astype(int)
cl = d['consensus_label']
abst = cl.isna() | cl.eq('disagreement')

def wilson(k, n, z=1.959963984540054):
    if n == 0: return (float('nan'), float('nan'))
    p = k / n; den = 1 + z*z/n
    c = (p + z*z/(2*n)) / den
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return (c-h, c+h)

def scheme_pred(scheme):
    pos = ['substantive_adoption'] + (['generic_or_background'] if scheme == 'G' else [])
    llm = pd.Series(np.where(cl.isin(pos), 1, 0), index=d.index).astype(float)
    llm[abst] = np.nan
    hyb = llm.copy()
    hyb[hyb.isna()] = d.loc[hyb.isna(), 'dictionary_pred']
    return {'Dictionary': d['dictionary_pred'].astype(float),
            'StrictLLM': llm,
            'FinBERT': d['finbert_pred'].astype(float),
            'Hybrid': hyb}

def cm(y, p):
    tp = int(((y==1)&(p==1)).sum()); fp = int(((y==0)&(p==1)).sum())
    tn = int(((y==0)&(p==0)).sum()); fn = int(((y==1)&(p==0)).sum())
    return tp, fp, tn, fn

def fmt(tp, fp, tn, fn, ncov, nsub):
    P = tp/(tp+fp) if tp+fp else float('nan'); R = tp/(tp+fn) if tp+fn else float('nan')
    F = 2*P*R/(P+R) if (tp+fp and tp+fn and P+R>0) else float('nan')
    pl = wilson(tp, tp+fp); rl = wilson(tp, tp+fn)
    return (f"TP={tp} FP={fp} TN={tn} FN={fn} | P={P:.4f} [{pl[0]:.4f},{pl[1]:.4f}] "
            f"R={R:.4f} [{rl[0]:.4f},{rl[1]:.4f}] F1={F:.4f} | cover={ncov}/{nsub}")

masks = {'(a) all600 (abstain=0)': pd.Series(True, index=d.index),
         '(b) hit-layer300 (abstain=0)': d['dictionary_hit'].eq(1),
         '(c) strict-covered': ~abst,
         '(d) non-hit-layer300 (abstain=0)': d['dictionary_hit'].eq(0)}

def report(scheme):
    P = scheme_pred(scheme)
    print(f"\n##### SCHEME {scheme} #####")
    out = {}
    for mk, m in masks.items():
        print(f"--- {mk}, n={int(m.sum())}")
        for name, p in P.items():
            pp = p.fillna(0)  # abstention counts as not detected
            if mk.startswith('(c)'):
                pp = p
            y = d['gold']
            r = cm(y[m], pp[m])
            ncov = int(p[m].notna().sum())
            out[(mk, name)] = r
            print(f"  {name:11s} " + fmt(*r, ncov, int(m.sum())))
    return out

def control():
    P = scheme_pred('S')
    exp = {('(a) all600 (abstain=0)', 'Dictionary'): (216,84,300,0),
           ('(c) strict-covered', 'StrictLLM'): (121,0,82,68),
           ('(a) all600 (abstain=0)', 'FinBERT'): (151,83,301,65),
           ('(a) all600 (abstain=0)', 'Hybrid'): (148,2,382,68)}
    ok = True
    for (mk, name), e in exp.items():
        m = masks[mk]; p = P[name]; pp = p if mk.startswith('(c)') else p.fillna(0)
        r = cm(d['gold'][m], pp[m])
        f = r == e; ok &= f
        print(f"CONTROL {name:11s} got={r} published={e} {'OK' if f else 'MISMATCH'}")
    ncov = int((~abst).sum()); print(f"CONTROL strict coverage n={ncov} (published 271) {'OK' if ncov==271 else 'MISMATCH'}")
    ok &= ncov == 271
    return ok

print('=== RESULTS ===')
print(f"input={a.pred}\nn={len(d)} gold_pos={int(d.gold.sum())}")
if not a.skip_control:
    ok = control()
    print('POSITIVE_CONTROL', 'PASS' if ok else 'FAIL')
    if not ok:
        print('=== END RESULTS ==='); sys.exit(1)
rs = report('S'); rg = report('G')

print("\n##### hit-layer crosstab: consensus_label x gold_binary (hit layer n=300)")
hl = d[d.dictionary_hit.eq(1)]
print(pd.crosstab(hl['consensus_label'], hl['gold']).to_string())
print("\n##### all-600 crosstab (NaN shown as non_hit)")
print(pd.crosstab(d['consensus_label'].fillna('non_hit'), d['gold']).to_string())
print('=== END RESULTS ===')
