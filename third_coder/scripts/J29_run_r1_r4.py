"""J29_run_r1_r4.py -- RUN R1-R4 (paper2 IP&M third revision), replica of J23_q7_primary.py definitions.

WHAT   : (0) replay J23_q7_primary.py end to end (same hash gates, controls C1/C2, primary basis,
             F1 bootstrap chain for all five gold columns) into a buffer and compare it byte for byte
             with J23_q7_primary.log -> positive control; any difference -> stop.
         (1) R1: 477 concordant passages (Coder 1 == Coder 2, both binary; computed from the gold workbook,
             must be exactly 477), Panel A (scheme G) and Panel B (scheme S), four methods, confusion cells,
             Wilson 95% CI for P and R, bootstrap 95% CI for F1 (2,000 resamples).
         (2) R2: strata random non-matched / near-miss non-matched (primary basis; unresolved dropped),
             cells + Wilson; recall and F1 undefined when there is no positive passage.
         (3) R3: two-sided Clopper-Pearson 95% CI for 0/150 (random non-matched), with positive controls
             on the CIs already in the manuscript (0/121, 4/123, 4/244).
         (4) R4: F1 bootstrap CI under the previous labels (gold_binary), all four populations, both schemes.
INPUT  : predictions csv, gold workbook, final_labels.csv, seed file (all hash-gated), J23 log.
OUTPUT : stdout only (pinned values between RESULTS markers). Panel A = scheme G, Panel B = scheme S.
BOOTSTRAP: numpy default_rng(seed in seed_analysis.txt), a FRESH generator for each of R1 and R4 (J23's chained
         generator never drew for gold_binary or the 477 subset); cell order scheme [S, G] -> population ->
         method, B = 2000, F1 = 2TP/(2TP+FP+FN), undefined iff TP+FP+FN == 0, percentile [2.5, 97.5].
"""
import sys, math, hashlib, os
sys.stdout.reconfigure(encoding='utf-8', newline='\n')
import numpy as np
import pandas as pd
import openpyxl
from scipy.stats import beta

W = r"E:\論文投稿  送審\paper2\R3_work"
RD = r"E:/paper2  daxiu/73ae4696cf54747044a03a936c4bb958_744934475e1139b8c27898b82ae5bbf0_8/paper2_github_replication/data/"
PRED = RD + "Table_3C_validation_predictions.csv"
PRED_SHA = 'dc3a67a6547336fd872f51f3ea6360e92e3a3c5785fe3093ed281ae9193f2b5c'
WBK = RD + "genai_gold_standard_adjudication_workbook.xlsx"
WBK_SHA = 'aa072750c0a1ae9ac68dece24f060ef2c8e1d1bfb7a153244f9d69791620b0a0'
FINAL = os.path.join(W, 'J23_unblinding', 'final_labels.csv')
SEEDF = os.path.join(W, 'third_coder', 'sealed', 'seed_analysis.txt')
SEED_SHA = 'd802d334fa64c6fee7ef317d0b16bc42c8af758253b05d36a09eee8a6bff0c19'
J23LOG = os.path.join(W, 'J23_unblinding', 'J23_q7_primary.log')
B = 2000
Z = 1.959963984540054


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


# ---------- hash gates ----------
for p, h in [(PRED, PRED_SHA), (SEEDF, SEED_SHA), (WBK, WBK_SHA)]:
    assert sha(p) == h, 'HASH MISMATCH ' + p
for p, h12 in [(FINAL, '4533fc1a863e'),
               (os.path.join(W, 'third_coder_scripts', 'q7_construct_rescore.py'), '901247c0d306'),
               (os.path.join(W, 'third_coder_scripts', 'analysis_third_coder.py'), '969fe48ed0b6'),
               (os.path.join(W, 'J23_unblinding', 'q7_control.log'), 'e6fa8d0f0f9a')]:
    assert sha(p)[:12] == h12, 'HASH MISMATCH ' + p
SEED = int(open(SEEDF, encoding='utf-8').read().strip())

D0 = pd.read_csv(PRED, encoding='utf-8-sig', dtype={'Firm_ID': str})
FL = pd.read_csv(FINAL, encoding='utf-8-sig')


# ---------- q7 / J23 replica (verbatim definitions) ----------
def wilson(k, n, z=Z):
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
    def __init__(self, d, gold):
        self.d = d.copy()
        self.d['gold'] = gold.values
        self.keep = self.d['gold'].notna()
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
        out.append("\n##### hit-layer crosstab: consensus_label x gold_binary (hit layer n=%d)" % int(d.dictionary_hit.eq(1).sum()))
        hl = d[d.dictionary_hit.eq(1)]
        out.append(pd.crosstab(hl['consensus_label'], hl['gold']).to_string())
        out.append("\n##### all-%d crosstab (NaN shown as non_hit)" % len(d))
        out.append(pd.crosstab(d['consensus_label'].fillna('non_hit'), d['gold']).to_string())


def replica_text(d, gold, with_control):
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
    raw = open(os.path.join(W, 'J23_unblinding', name), 'rb').read()
    return raw.decode('utf-8').replace('\r\n', '\n'), (b'\r\n' in raw)


def compare(mine, ref):
    a, b = mine.split('\n'), ref.split('\n')
    mism = sum(1 for i in range(max(len(a), len(b))) if (a[i] if i < len(a) else None) != (b[i] if i < len(b) else None))
    return max(len(a), len(b)), mism


def boot_f1(y, pp, rng):
    """verbatim J23 bootstrap cell -> (lo, hi, nan_draws)."""
    n = len(y)
    idx = rng.integers(0, n, size=(B, n))
    yb, pb = y[idx], pp[idx]
    tp = (yb * pb).sum(1); fp = pb.sum(1) - tp; fn = yb.sum(1) - tp
    den = 2*tp + fp + fn
    und = (tp + fp + fn) == 0
    f = np.where(und, np.nan, 2*tp / np.where(und, 1, den))
    nand = int(und.sum())
    if nand == B:
        return float('nan'), float('nan'), nand
    lo, hi = np.nanpercentile(f, [2.5, 97.5])
    return lo, hi, nand


# =====================================================================
# PART 0: replay J23 into a buffer (positive control)
# =====================================================================
cap = []
checks = []
ref, crlf1 = logtext('q7_control.log')
assert ref.splitlines()[1] == f"input={PRED}", 'q7_control input line differs'
assert int(D0['gold_binary'].sum()) == 216 and 'gold_pos=216' in ref
mine = replica_text(D0, D0['gold_binary'], True)
checks.append(('C1 gold_binary vs q7_control.log', *compare(mine, ref)))
M = D0.merge(FL, on='sample_id', how='left', validate='one_to_one')
assert len(M) == 600 and (M['sample_id'].values == D0['sample_id'].values).all()
crlf2 = {}
for col in ['gold_lean', 'gold_U0', 'gold_U1', 'gold_flip_lean']:
    ref, crlf2[col] = logtext(f'q7_new_{col}.log')
    mine = replica_text(D0, M[col], False)
    checks.append((f'C2 {col} vs q7_new_{col}.log', *compare(mine, ref)))
npass = sum(1 for c in checks if c[2] == 0); nfail = len(checks) - npass
cap.append('=== RESULTS ===')
cap.append(f"seed_file_sha256_ok=True seed={SEED} B={B}; pred_sha256_ok=True; final_labels sha12=4533fc1a863e ok")
for lab, n, mm in checks:
    cap.append(f"CHECK {lab}: lines={n} mismatching_lines={mm} -> {'PASS' if mm == 0 else 'FAIL'}")
cap.append(f"raw log CRLF present: q7_control={crlf1} " + ' '.join(f"{k}={v}" for k, v in crlf2.items()) + " (compared after CRLF->LF)")
cap.append(f"CONTROLS PASS={npass} FAIL={nfail}")
assert nfail == 0, 'C1/C2 failed'

drop_ids = M.loc[M['gold_primary'].isna(), 'sample_id'].tolist()
assert len(drop_ids) == 7 and M['gold_primary'].notna().sum() == 593
assert M['gold_primary'].dropna().isin([0, 1]).all()
Rp = Run(D0, M['gold_primary'])
out = [f"\n##### PRIMARY BASIS: gold_primary, unresolved (Coder-3 U) paragraphs dropped from every population",
       f"input={PRED}\nn={int(Rp.keep.sum())} (of {len(Rp.d)}) dropped={int((~Rp.keep).sum())} gold_pos={int(Rp.d.loc[Rp.keep,'gold'].sum())}",
       "dropped sample_id: " + ' '.join(drop_ids)]
Rp.report('S', out, True); Rp.report('G', out, True)
Rp.tail(out)
cap.append('\n'.join(out))

rng = np.random.default_rng(SEED)
POPKEY = {'(a) all600 (abstain=0)': 'a_all600', '(b) hit-layer300 (abstain=0)': 'b_hit300',
          '(c) strict-covered': 'c_strict', '(d) non-hit-layer300 (abstain=0)': 'd_nonhit300'}
cap.append("\n##### F1 bootstrap (B=%d, paragraph resampling within population, seed=%d)" % (B, SEED))
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
                lo, hi, nand = boot_f1(y, pp, rng)
                cap.append(f"F1_boot {gcol} {scheme} {POPKEY[mk]} {name} F1={F:.4f} CI[{lo:.4f},{hi:.4f}] n={n} nan_draws={nand}")
cap.append('=== END RESULTS ===')
replay = '\n'.join(cap) + '\n'
refj = open(J23LOG, 'rb').read().decode('utf-8')
assert '\r' not in refj
nl, mm = compare(replay, refj)
assert mm == 0, f'J23 REPLAY MISMATCH lines={nl} mismatching={mm}'
replay_lines = replay.split('\n')

# =====================================================================
# data for the new parts
# =====================================================================
rows = list(openpyxl.load_workbook(WBK, read_only=True, data_only=True)['Annotation_Blind'].iter_rows(values_only=True))
hd = list(rows[0]); ix = {n: hd.index(n) for n in ('sample_id', 'coder1_label', 'coder2_label')}
def nl_(v): return '' if v is None else str(v).strip().upper()
lab12 = {r[ix['sample_id']]: (nl_(r[ix['coder1_label']]), nl_(r[ix['coder2_label']])) for r in rows[1:] if r[ix['sample_id']] is not None}
assert len(lab12) == 600
conc = {s for s, v in lab12.items() if v[0] == v[1] and v[0] in ('0', '1')}
assert len(conc) == 477, f'concordant count {len(conc)} != 477'
assert conc <= set(D0.sample_id)
M['conc'] = M.sample_id.isin(conc)
cc = M[M.conc]
assert (cc.gold_primary == cc.gold_binary).all(), 'gold_primary != gold_binary on concordant passages'
assert (cc.gold_binary.astype(str) == cc.sample_id.map(lambda s: lab12[s][0])).all(), 'gold_binary != Coder1 label on concordant'

def wl(k, n):
    lo, hi = wilson(k, n)
    return max(lo, 0.0), min(hi, 1.0)

def cell_line(tp, fp, tn, fn, boot=None):
    s = f"TP={tp} FP={fp} TN={tn} FN={fn} | "
    if tp+fp:
        l, h = wl(tp, tp+fp); s += f"P={tp/(tp+fp):.4f} (95% CI {l:.4f}-{h:.4f}) "
    else:
        s += "P=undefined (no predicted positives) "
    if tp+fn:
        l, h = wl(tp, tp+fn); s += f"R={tp/(tp+fn):.4f} (95% CI {l:.4f}-{h:.4f}) "
    else:
        s += "R=undefined (no positive passages) "
    if tp+fn == 0:
        s += "F1=undefined (no positive passages)"
    else:
        s += f"F1={2*tp/(2*tp+fp+fn):.4f}"
        if boot is not None:
            s += f" (95% CI {boot[0]:.4f}-{boot[1]:.4f}; nan_draws={boot[2]})"
    return s

PANEL = {'G': 'A', 'S': 'B'}
NAMES = ['Dictionary', 'StrictLLM', 'FinBERT', 'Hybrid']
RES = []   # lines for the RESULTS block

# ---------------- R1: 477 concordant ----------------
d477 = D0[D0.sample_id.isin(conc)].reset_index(drop=True)
gb = d477['gold_binary'].astype(float)
assert len(d477) == 477 and gb.isin([0, 1]).all()
R477 = Run(d477, gb)
rngR1 = np.random.default_rng(SEED)
R1D = {}
R2D = {}
RES.append(f"R1 concordant n={len(d477)} gold_pos={int(gb.sum())} hit={int(d477.dictionary_hit.sum())} nonhit={int((d477.dictionary_hit==0).sum())} strict_covered={int((~R477.abst).sum())}")
for scheme in ['S', 'G']:
    P = R477.scheme_pred(scheme)
    for mk in ['(a) all600 (abstain=0)', '(c) strict-covered']:
        m = (R477.masks[mk] & R477.keep).values
        pop = '477 full benchmark (abstain=0)' if mk.startswith('(a)') else '477 strict-covered'
        for name in NAMES:
            p = P[name]
            y = R477.y[m].astype(int).values
            pp = R477.pp(p, mk)[m].astype(int).values
            tp, fp, tn, fn = cm(pd.Series(y), pd.Series(pp))
            bt = boot_f1(y, pp, rngR1)
            R1D[(scheme, mk[:3], name)] = (tp, fp, tn, fn, bt)
            RES.append(f"R1 Panel {PANEL[scheme]} [{pop}, n={len(y)}] {name:10s} " + cell_line(tp, fp, tn, fn, bt) + f" cover={int(p[m].notna().sum())}/{len(y)}")

# ---------------- R2: strata (primary basis) ----------------
STR = [('matched (dictionary_hit_random)', 'dictionary_hit_random'),
       ('random non-matched', 'dictionary_non_hit_random'),
       ('near-miss non-matched', 'dictionary_non_hit_near_miss')]
for lab, grp in STR:
    ds = D0[D0.sample_group == grp].reset_index(drop=True)
    gp = M.set_index('sample_id').loc[ds.sample_id, 'gold_primary'].reset_index(drop=True)
    Rs = Run(ds, gp)
    keep = Rs.keep.values
    npos = int(gp.dropna().sum())
    RES.append(f"R2 stratum {lab}: n_total={len(ds)} n_resolved={int(keep.sum())} dropped_unresolved={int((~keep).sum())} positives={npos}")
    for scheme in ['S', 'G']:
        P = Rs.scheme_pred(scheme)
        for name in NAMES:
            pp = Rs.pp(P[name], '(a) all600 (abstain=0)')
            tp, fp, tn, fn = cm(Rs.y[keep].astype(int), pp[keep].astype(int))
            R2D[(grp, scheme, name)] = (tp, fp, tn, fn)
            RES.append(f"R2 Panel {PANEL[scheme]} [{lab}] {name:10s} " + cell_line(tp, fp, tn, fn) + f" cover={int(P[name][keep].notna().sum())}/{int(keep.sum())}")

# ---------------- R3: Clopper-Pearson ----------------
def cp(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else float(beta.ppf(alpha/2, k, n-k+1))
    hi = 1.0 if k == n else float(beta.ppf(1-alpha/2, k+1, n-k))
    return lo, hi
# positive controls: intervals already in the manuscript (3 decimals)
for k, n, exp in [(0, 121, ('0.000', '0.030')), (4, 123, ('0.009', '0.081')), (4, 244, ('0.004', '0.041'))]:
    lo, hi = cp(k, n)
    got = (f"{lo:.3f}", f"{hi:.3f}")
    assert got == exp, f'CP control failed {k}/{n}: {got} vs {exp}'
    RES.append(f"R3 control CP {k}/{n} = {lo:.4f}-{hi:.4f} (3dp {got[0]}-{got[1]}; manuscript {exp[0]}-{exp[1]}) OK")
rs = M[M.sample_group == 'dictionary_non_hit_random']
n_r = int(rs.gold_primary.notna().sum()); k_r = int(rs.gold_primary.dropna().sum())
assert (n_r, k_r) == (150, 0), f'random non-matched n,k = {n_r},{k_r}'
lo, hi = cp(k_r, n_r)
closed = 1 - 0.025 ** (1 / 150)
assert abs(hi - closed) < 1e-12
RES.append(f"R3 random non-matched {k_r}/{n_r} (gold_primary) two-sided Clopper-Pearson 95% CI = {lo:.4f}-{hi:.4f} (3dp {lo:.3f}-{hi:.3f}); closed form 1-0.025^(1/150)={closed:.6f}")

# ---------------- R4: previous labels, F1 bootstrap ----------------
Rb = Run(D0, D0['gold_binary'].astype(float))
rngR4 = np.random.default_rng(SEED)
EXPECT_S54 = {  # Table S5.4 'Previous labels (n = 600)' column, J28:270-277, P/R/F1 at 3 dp; plus covered note J28:280
    ('G', 'Dictionary'): ('0.720', '1.000', '0.837'), ('G', 'StrictLLM'): ('0.994', '0.833', '0.907'),
    ('G', 'FinBERT'): ('0.645', '0.699', '0.671'), ('G', 'Hybrid'): ('0.986', '0.958', '0.972'),
    ('S', 'StrictLLM'): ('1.000', '0.560', '0.718'), ('S', 'Hybrid'): ('0.987', '0.685', '0.809')}
R4 = {}
for scheme in ['S', 'G']:
    P = Rb.scheme_pred(scheme)
    for mk, m0 in Rb.masks.items():
        m = (m0 & Rb.keep).values
        for name in NAMES:
            y = Rb.y[m].astype(int).values
            pp = Rb.pp(P[name], mk)[m].astype(int).values
            tp, fp, tn, fn = cm(pd.Series(y), pd.Series(pp))
            bt = boot_f1(y, pp, rngR4)
            R4[(scheme, POPKEY[mk], name)] = (tp, fp, tn, fn, bt)
            RES.append(f"R4 previous labels Panel {PANEL[scheme]} {POPKEY[mk]} n={len(y)} {name:10s} " + cell_line(tp, fp, tn, fn, bt))
# note: the manuscript column order of the table was read from J28:270-277; the numbers below are compared at 3 dp
bad = 0
for (sc, nm), (p3, r3, f3) in EXPECT_S54.items():
    tp, fp, tn, fn, bt = R4[(sc, 'a_all600', nm)]
    got = (f"{tp/(tp+fp):.3f}", f"{tp/(tp+fn):.3f}", f"{2*tp/(2*tp+fp+fn):.3f}")
    ok = got == (p3, r3, f3)
    bad += (not ok)
    RES.append(f"R4 control vs manuscript previous-labels column Panel {PANEL[sc]} {nm}: got {got} manuscript {(p3, r3, f3)} {'OK' if ok else 'MISMATCH'}")
for sc, exp in [('G', ('0.994', '0.952', '0.973')), ('S', ('1.000', '0.640', '0.781'))]:
    tp, fp, tn, fn, bt = R4[(sc, 'c_strict', 'StrictLLM')]
    got = (f"{tp/(tp+fp):.3f}", f"{tp/(tp+fn):.3f}", f"{2*tp/(2*tp+fp+fn):.3f}")
    ok = got == exp
    bad += (not ok)
    RES.append(f"R4 control vs manuscript note (271 covered, strict consensus) Panel {PANEL[sc]}: got {got} manuscript {exp} {'OK' if ok else 'MISMATCH'}")


# ---------------- fill strings (3 dp, rounded from raw values) ----------------
def f3(x): return f"{x:.3f}"
def wci(k, n):
    l, h = wl(k, n); return f"{f3(l)}–{f3(h)}"
def prf(tp, fp, tn, fn, bt):
    return (f"P={f3(tp/(tp+fp))} (95% CI {wci(tp, tp+fp)}), R={f3(tp/(tp+fn))} (95% CI {wci(tp, tp+fn)}), "
            f"F1={f3(2*tp/(2*tp+fp+fn))} (95% CI {f3(bt[0])}–{f3(bt[1])})")
DN = {'Dictionary': 'Dictionary rules', 'StrictLLM': 'Strict consensus', 'FinBERT': 'FinBERT', 'Hybrid': 'Hybrid'}
cp_lo, cp_hi = cp(0, 150)
FILL = []
FILL.append(f"FILL F158 = two-sided Clopper–Pearson 95% CI for the proportion {f3(cp_lo)}–{f3(cp_hi)}")
f280 = []
for sc in ['G', 'S']:
    items = []
    for nm in (NAMES if sc == 'G' else ['StrictLLM', 'Hybrid']):
        tp, fp, tn, fn, bt = R4[(sc, 'a_all600', nm)]
        items.append(f"{DN[nm]} {f3(2*tp/(2*tp+fp+fn))} (95% CI {f3(bt[0])}–{f3(bt[1])})")
    f280.append(f"Panel {PANEL[sc]}: " + ', '.join(items))
cv = []
for sc in ['G', 'S']:
    tp, fp, tn, fn, bt = R4[(sc, 'c_strict', 'StrictLLM')]
    cv.append(f"{f3(2*tp/(2*tp+fp+fn))} (95% CI {f3(bt[0])}–{f3(bt[1])}) in Panel {PANEL[sc]}")
FILL.append("FILL F280 = (F1 bootstrap 95% CIs under the previous labels, full benchmark: " + '; '.join(f280) + "; strict consensus on the 271 covered passages: " + ' and '.join(cv) + ")")
rn = {k: v for k, v in R2D.items() if k[0] == 'dictionary_non_hit_random'}
nm_ = {k: v for k, v in R2D.items() if k[0] == 'dictionary_non_hit_near_miss'}
fb_r = R2D[('dictionary_non_hit_random', 'G', 'FinBERT')]; fb_n = R2D[('dictionary_non_hit_near_miss', 'G', 'FinBERT')]
assert R2D[('dictionary_non_hit_random', 'S', 'FinBERT')] == fb_r and R2D[('dictionary_non_hit_near_miss', 'S', 'FinBERT')] == fb_n
assert all(v[0] == 0 for v in R2D.values() if v[0] is not None) or True
others_r = [v for k, v in rn.items() if k[2] != 'FinBERT']; others_n = [v for k, v in nm_.items() if k[2] != 'FinBERT']
assert all(v[0] == 0 and v[1] == 0 and v[3] == 0 for v in others_r + others_n)
assert fb_r[0] == 0 and fb_n[0] == 0 and fb_r[3] == 0 and fb_n[3] == 0
t1 = (f"In the random non-matched stratum (150 passages, none GenAI-related) no method has a true positive; FinBERT has {fb_r[1]} false positives and the other methods none, "
      f"and recall and F1 are undefined (no positive passages); the two-sided Clopper–Pearson 95% CI for 0 of 150 is {f3(cp_lo)}–{f3(cp_hi)}. "
      f"In the near-miss non-matched stratum (143 resolved passages, none GenAI-related) no method has a true positive; FinBERT has {fb_n[1]} false positives (P=0.000, 95% CI {wci(0, fb_n[1])}) and the other methods none, "
      f"and recall and F1 are undefined (no positive passages). ")
dd = R1D[('G', '(a)', 'Dictionary')]
t2 = (f"On the 477 concordant passages (169 GenAI-related; full benchmark, abstentions counted as non-detections), the dictionary rules have {dd[0]} true positives, {dd[1]} false positives, {dd[2]} true negatives and {dd[3]} false negatives, and precision, recall and F1 are, "
      "in Panel A, " + '; '.join(f"{DN[nm]} " + prf(*R1D[('G', '(a)', nm)]) for nm in NAMES) + ". In Panel B, " + '; '.join(f"{DN[nm]} " + prf(*R1D[('S', '(a)', nm)]) for nm in NAMES) + ".")
FILL.append("FILL F295 = " + t1 + t2)
FILL.append("FILL F154 = The metrics on the 477 concordant passages and by stratum (matched, random non-matched, near-miss non-matched)")
FILL.append("FILL F330 = (the metrics on the 477 concordant passages are in the note to Table S5.5)")
RES.extend(FILL)

# =====================================================================
# output
# =====================================================================
print('=== RESULTS ===')
print(f"J23 REPLAY (positive control): regenerated J23_q7_primary output = {len(replay_lines)-1} lines, compared with J23_q7_primary.log: mismatching_lines={mm} -> {'PASS' if mm == 0 else 'FAIL'}")
print("J23 replay, pinned lines (regenerated text; Panel A = scheme G, Panel B = scheme S):")
for i, l in enumerate(replay_lines):
    if l.startswith('F1_boot gold_primary') and (' a_all600 ' in l or ' c_strict ' in l) and any(f' {n} ' in l for n in ('Dictionary', 'StrictLLM', 'Hybrid')):
        print('  ' + l)
cur = None
for i, l in enumerate(replay_lines):
    if l.startswith('##### SCHEME'):
        cur = l
    if cur and l.startswith('--- (a)'):
        print('  ' + cur.strip('# ') + ' | ' + l)
        for j in (1, 2, 4):
            print('    ' + replay_lines[i + j])
for r in RES:
    print(r)
print(f"R4 control mismatches={bad}")
print('=== END RESULTS ===')
assert bad == 0
