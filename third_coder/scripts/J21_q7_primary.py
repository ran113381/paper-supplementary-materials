"""J21_q7_primary.py -- replica + extension of third_coder_scripts/q7_construct_rescore.py.

WHAT   : Line-by-line replica of q7's definitions (scheme S/G positive classes, abstain rule,
         Hybrid rule, confusion matrix, Wilson CI, populations (a)(b)(c)(d), output format),
         extended with (i) a primary-gold run that DROPS the 7 unresolved (Coder-3 'U')
         paragraphs from every population, and (ii) a paragraph-level bootstrap 95% CI for F1.
WHY    : q7:37 asserts gold in {0,1} for all 600 rows, so it cannot score gold_primary
         (7 blanks) -> the "exclude unresolved" basis (protocol 7.3) cannot be computed with
         it (J20 q7_new_gold_primary.log: AssertionError). q7 also has no bootstrap.
         This script was written because of that; archived scripts are NOT modified/imported.
PROTOCOL: 7.3 (primary gold = Coder-3 binary label on non-concordant paragraphs, unresolved
         excluded), 8.2(i) (F1 bootstrap, 2000 resamples, seed archived by hash only),
         8.3 (Scheme G = Panel A primary, Scheme S = Panel B).

Positive controls (must all pass BEFORE the new basis is computed; any failure -> stop):
  C1: gold_binary column of the predictions file -> text identical to J20/q7_control.log
  C2: final_labels.csv gold_lean / gold_U0 / gold_U1 / gold_flip_lean (run with the q7
      --skip-control behaviour) -> text identical to J20/q7_new_gold_<col>.log
  (comparison after normalising CRLF->LF; raw CRLF presence is reported)

Bootstrap: numpy.random.default_rng(seed), seed = integer in sealed/seed_analysis.txt
  (file sha256 verified first). ONE generator, drawn in this fixed order:
    gold column  [gold_primary, gold_lean, gold_U0, gold_U1, gold_flip_lean]
      -> scheme [S, G]
        -> population [(a) all600, (b) hit300, (c) strict-covered, (d) non-hit300]
          -> method [Dictionary, StrictLLM, FinBERT, Hybrid]
  For each cell: idx = rng.integers(0, n, size=(2000, n)) over the n paragraphs of that
  population (after dropping gold-missing rows), resample with replacement, n unchanged;
  recompute F1 = 2TP/(2TP+FP+FN) of that method on the resample (abstention counted as
  not-detected, as in q7 report); F1 undefined iff TP+FP+FN==0 -> nan, counted in nan_draws
  and dropped (np.nanpercentile). CI = [2.5, 97.5] percentiles.
  NOTE: the point F1 printed in "F1=" uses q7's definition (nan if TP+FP==0 or TP+FN==0),
  whereas the bootstrap uses the protocol's (undefined only if TP+FP+FN==0); they differ
  only in degenerate cells (e.g. population (d)).
"""
import sys, math, hashlib, os
sys.stdout.reconfigure(encoding='utf-8', newline='\n')
import numpy as np
import pandas as pd

W = r"E:\論文投稿  送審\paper2\R3_work"
PRED = r"E:/paper2  daxiu/73ae4696cf54747044a03a936c4bb958_744934475e1139b8c27898b82ae5bbf0_8/paper2_github_replication/data/Table_3C_validation_predictions.csv"
PRED_SHA = 'dc3a67a6547336fd872f51f3ea6360e92e3a3c5785fe3093ed281ae9193f2b5c'
FINAL = os.path.join(W, 'J20_unblinding', 'final_labels.csv')
SEEDF = os.path.join(W, 'third_coder', 'sealed', 'seed_analysis.txt')
SEED_SHA = 'd802d334fa64c6fee7ef317d0b16bc42c8af758253b05d36a09eee8a6bff0c19'
B = 2000


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


# ---------- hash gates ----------
gates = [(PRED, PRED_SHA), (SEEDF, SEED_SHA)]
for p, h in gates:
    assert sha(p) == h, 'HASH MISMATCH ' + p
for p, h12 in [(FINAL, '4533fc1a863e'),
               (os.path.join(W, 'third_coder_scripts', 'q7_construct_rescore.py'), '901247c0d306'),
               (os.path.join(W, 'third_coder_scripts', 'analysis_third_coder.py'), '969fe48ed0b6'),
               (os.path.join(W, 'J20_unblinding', 'q7_control.log'), 'e6fa8d0f0f9a')]:
    assert sha(p)[:12] == h12, 'HASH MISMATCH ' + p
SEED = int(open(SEEDF, encoding='utf-8').read().strip())

D0 = pd.read_csv(PRED, encoding='utf-8-sig', dtype={'Firm_ID': str})
FL = pd.read_csv(FINAL, encoding='utf-8-sig')


# ---------- q7 replica ----------
def wilson(k, n, z=1.959963984540054):
    if n == 0: return (float('nan'), float('nan'))
    p = k / n; den = 1 + z*z/n
    c = (p + z*z/(2*n)) / den
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return (c-h, c+h)


def cm(y, p):
    tp = int(((y==1)&(p==1)).sum()); fp = int(((y==0)&(p==1)).sum())
    tn = int(((y==0)&(p==0)).sum()); fn = int(((y==1)&(p==0)).sum())
    return tp, fp, tn, fn


def f1_q7(tp, fp, tn, fn):
    P = tp/(tp+fp) if tp+fp else float('nan'); R = tp/(tp+fn) if tp+fn else float('nan')
    return 2*P*R/(P+R) if (tp+fp and tp+fn and P+R>0) else float('nan')


def fmt(tp, fp, tn, fn, ncov, nsub):
    P = tp/(tp+fp) if tp+fp else float('nan'); R = tp/(tp+fn) if tp+fn else float('nan')
    F = 2*P*R/(P+R) if (tp+fp and tp+fn and P+R>0) else float('nan')
    pl = wilson(tp, tp+fp); rl = wilson(tp, tp+fn)
    return (f"TP={tp} FP={fp} TN={tn} FN={fn} | P={P:.4f} [{pl[0]:.4f},{pl[1]:.4f}] "
            f"R={R:.4f} [{rl[0]:.4f},{rl[1]:.4f}] F1={F:.4f} | cover={ncov}/{nsub}")


class Run:
    """One evaluation context: d (600 rows, with 'gold' possibly NaN) + keep mask."""
    def __init__(self, d, gold, strict_n600=True):
        self.d = d.copy()
        self.d['gold'] = gold.values
        self.keep = self.d['gold'].notna()
        self.d = self.d  # gold kept as float; cast on use
        cl = self.d['consensus_label']
        self.cl = cl
        self.abst = cl.isna() | cl.eq('disagreement')
        self.masks = {'(a) all600 (abstain=0)': pd.Series(True, index=self.d.index),
                      '(b) hit-layer300 (abstain=0)': self.d['dictionary_hit'].eq(1),
                      '(c) strict-covered': ~self.abst,
                      '(d) non-hit-layer300 (abstain=0)': self.d['dictionary_hit'].eq(0)}
        self.y = self.d['gold']

    def scheme_pred(self, scheme):
        d, cl = self.d, self.cl
        pos = ['substantive_adoption'] + (['generic_or_background'] if scheme == 'G' else [])
        llm = pd.Series(np.where(cl.isin(pos), 1, 0), index=d.index).astype(float)
        llm[self.abst] = np.nan
        hyb = llm.copy()
        hyb[hyb.isna()] = d.loc[hyb.isna(), 'dictionary_pred']
        return {'Dictionary': d['dictionary_pred'].astype(float),
                'StrictLLM': llm,
                'FinBERT': d['finbert_pred'].astype(float),
                'Hybrid': hyb}

    def pp(self, p, mk):
        return p if mk.startswith('(c)') else p.fillna(0)

    def control(self, out):
        P = self.scheme_pred('S')
        exp = {('(a) all600 (abstain=0)', 'Dictionary'): (216,84,300,0),
               ('(c) strict-covered', 'StrictLLM'): (121,0,82,68),
               ('(a) all600 (abstain=0)', 'FinBERT'): (151,83,301,65),
               ('(a) all600 (abstain=0)', 'Hybrid'): (148,2,382,68)}
        ok = True
        for (mk, name), e in exp.items():
            m = self.masks[mk]; p = P[name]; pp = self.pp(p, mk)
            r = cm(self.y[m], pp[m])
            f = r == e; ok &= f
            out.append(f"CONTROL {name:11s} got={r} published={e} {'OK' if f else 'MISMATCH'}")
        ncov = int((~self.abst).sum()); out.append(f"CONTROL strict coverage n={ncov} (published 271) {'OK' if ncov==271 else 'MISMATCH'}")
        ok &= ncov == 271
        return ok

    def report(self, scheme, out, show_drop):
        P = self.scheme_pred(scheme)
        out.append(f"\n##### SCHEME {scheme} #####")
        for mk, m0 in self.masks.items():
            m = m0 & self.keep
            hdr = f"--- {mk}, n={int(m.sum())}"
            if show_drop:
                hdr += f" (dropped {int(m0.sum()) - int(m.sum())} of {int(m0.sum())} unresolved)"
            out.append(hdr)
            for name, p in P.items():
                pp = self.pp(p, mk)
                r = cm(self.y[m].astype(int), pp[m])
                ncov = int(p[m].notna().sum())
                out.append(f"  {name:11s} " + fmt(*r, ncov, int(m.sum())))

    def tail(self, out):
        k = self.keep
        d = self.d[k].copy(); d['gold'] = d['gold'].astype(int)
        full = bool(k.all())
        out.append("\n##### hit-layer crosstab: consensus_label x gold_binary (hit layer n=%d)" % int(d.dictionary_hit.eq(1).sum()))
        hl = d[d.dictionary_hit.eq(1)]
        out.append(pd.crosstab(hl['consensus_label'], hl['gold']).to_string())
        out.append("\n##### all-%d crosstab (NaN shown as non_hit)" % len(d))
        out.append(pd.crosstab(d['consensus_label'].fillna('non_hit'), d['gold']).to_string())


def replica_text(d, gold, with_control):
    """Exactly q7's stdout (minus nothing): used for C1/C2."""
    R = Run(d, gold)
    assert R.d['gold'].isin([0, 1]).all() and len(R.d) == 600, 'gold problem'
    R.d['gold'] = R.d['gold'].astype(int); R.y = R.d['gold']
    out = ['=== RESULTS ===', f"input={PRED}\nn={len(R.d)} gold_pos={int(R.d.gold.sum())}"]
    if with_control:
        ok = R.control(out)
        out.append('POSITIVE_CONTROL ' + ('PASS' if ok else 'FAIL'))
        assert ok
    R.report('S', out, False); R.report('G', out, False)
    R.tail(out)
    out.append('=== END RESULTS ===')
    return '\n'.join(out) + '\n'


def logtext(name):
    raw = open(os.path.join(W, 'J20_unblinding', name), 'rb').read()
    return raw.decode('utf-8').replace('\r\n', '\n'), (b'\r\n' in raw)


def compare(mine, ref):
    a, b = mine.split('\n'), ref.split('\n')
    mism = sum(1 for i in range(max(len(a), len(b))) if (a[i] if i < len(a) else None) != (b[i] if i < len(b) else None))
    return max(len(a), len(b)), mism


# ---------- positive controls ----------
checks = []   # (label, nlines, mismatches)
# C1 gold_binary column; confirm q7_control.log used this column (default --gold-col, input= line, gold_pos)
ref, crlf1 = logtext('q7_control.log')
assert ref.splitlines()[1] == f"input={PRED}", 'q7_control input line differs'
assert int(D0['gold_binary'].sum()) == 216 and 'gold_pos=216' in ref, 'gold_binary is not the control column'
mine = replica_text(D0, D0['gold_binary'], True)
checks.append(('C1 gold_binary vs q7_control.log', *compare(mine, ref)))
# C2
M = D0.merge(FL, on='sample_id', how='left', validate='one_to_one')
assert len(M) == 600 and (M['sample_id'].values == D0['sample_id'].values).all()
crlf2 = {}
for col in ['gold_lean', 'gold_U0', 'gold_U1', 'gold_flip_lean']:
    ref, crlf2[col] = logtext(f'q7_new_{col}.log')
    mine = replica_text(D0, M[col], False)
    checks.append((f'C2 {col} vs q7_new_{col}.log', *compare(mine, ref)))
npass = sum(1 for c in checks if c[2] == 0); nfail = len(checks) - npass

print('=== RESULTS ===')
print(f"seed_file_sha256_ok=True seed={SEED} B={B}; pred_sha256_ok=True; final_labels sha12=4533fc1a863e ok")
for lab, n, mm in checks:
    print(f"CHECK {lab}: lines={n} mismatching_lines={mm} -> {'PASS' if mm == 0 else 'FAIL'}")
print(f"raw log CRLF present: q7_control={crlf1} " + ' '.join(f"{k}={v}" for k, v in crlf2.items()) + " (compared after CRLF->LF)")
print(f"CONTROLS PASS={npass} FAIL={nfail}")
if nfail:
    print('=== END RESULTS ===')
    sys.exit(1)

# ---------- primary basis ----------
drop_ids = M.loc[M['gold_primary'].isna(), 'sample_id'].tolist()
assert len(drop_ids) == 7 and M['gold_primary'].notna().sum() == 593
assert M['gold_primary'].dropna().isin([0, 1]).all()
Rp = Run(D0, M['gold_primary'])
out = [f"\n##### PRIMARY BASIS: gold_primary, unresolved (Coder-3 U) paragraphs dropped from every population",
       f"input={PRED}\nn={int(Rp.keep.sum())} (of {len(Rp.d)}) dropped={int((~Rp.keep).sum())} gold_pos={int(Rp.d.loc[Rp.keep,'gold'].sum())}",
       "dropped sample_id: " + ' '.join(drop_ids)]
Rp.report('S', out, True); Rp.report('G', out, True)
Rp.tail(out)
print('\n'.join(out))


# ---------- bootstrap ----------
rng = np.random.default_rng(SEED)
POPKEY = {'(a) all600 (abstain=0)': 'a_all600', '(b) hit-layer300 (abstain=0)': 'b_hit300',
          '(c) strict-covered': 'c_strict', '(d) non-hit-layer300 (abstain=0)': 'd_nonhit300'}
print("\n##### F1 bootstrap (B=%d, paragraph resampling within population, seed=%d)" % (B, SEED))
for gcol in ['gold_primary', 'gold_lean', 'gold_U0', 'gold_U1', 'gold_flip_lean']:
    R = Run(D0, M[gcol])
    for scheme in ['S', 'G']:
        P = R.scheme_pred(scheme)
        for mk, m0 in R.masks.items():
            m = (m0 & R.keep).values
            for name, p in P.items():
                y = R.y[m].astype(int).values
                pp = R.pp(p, mk)[m].astype(int).values
                n = len(y)
                tp0, fp0, tn0, fn0 = cm(pd.Series(y), pd.Series(pp))
                F = f1_q7(tp0, fp0, tn0, fn0)
                idx = rng.integers(0, n, size=(B, n))
                yb, pb = y[idx], pp[idx]
                tp = (yb * pb).sum(1); fp = pb.sum(1) - tp; fn = yb.sum(1) - tp
                den = 2*tp + fp + fn
                und = (tp + fp + fn) == 0
                f = np.where(und, np.nan, 2*tp / np.where(und, 1, den))
                nand = int(und.sum())
                if nand == B:
                    lo = hi = float('nan')
                else:
                    lo, hi = np.nanpercentile(f, [2.5, 97.5])
                print(f"F1_boot {gcol} {scheme} {POPKEY[mk]} {name} F1={F:.4f} CI[{lo:.4f},{hi:.4f}] n={n} nan_draws={nand}")
print('=== END RESULTS ===')
