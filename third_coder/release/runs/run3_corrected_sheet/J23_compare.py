import os, hashlib, glob
W = r"E:\論文投稿  送審\paper2\R3_work"
A = os.path.join(W, 'J20_unblinding'); B = os.path.join(W, 'J23_unblinding')
S = os.path.join(W, 'J21_primary')
pairs = [(os.path.join(A, f), os.path.join(B, f), f) for f in
  ['stage1.log','stage2.log','final_labels.csv','stage2_calibration_disagreements.csv','stage2_e1_labeled_1.csv','stage2_e1_labeled_U.csv','stage2_nonconcordant_labels.csv','stage2_e1_summary.json','q7_control.log','q7_new_gold_primary.log','q7_new_gold_lean.log','q7_new_gold_U0.log','q7_new_gold_U1.log','q7_new_gold_flip_lean.log','qualification_record.json','qualification_record_hash_log.txt']]
pairs.append((os.path.join(S,'J21_q7_primary.log'), os.path.join(B,'J23_q7_primary.log'), 'J23_q7_primary.log vs J21_q7_primary.log'))
for a, b, n in pairs:
    x = open(a,'rb').read(); y = open(b,'rb').read()
    if x == y: print(f"SAME  {n}  sha12={hashlib.sha256(y).hexdigest()[:12]}"); continue
    print(f"DIFF  {n}  J20/ref sha12={hashlib.sha256(x).hexdigest()[:12]} J23 sha12={hashlib.sha256(y).hexdigest()[:12]}")
    xl = x.decode('utf-8').split('\n'); yl = y.decode('utf-8').split('\n')
    for i in range(max(len(xl),len(yl))):
        l1 = xl[i] if i < len(xl) else None; l2 = yl[i] if i < len(yl) else None
        if l1 != l2: print(f"   line {i+1}:\n     ref: {l1!r}\n     J23: {l2!r}")
