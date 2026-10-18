"""J3-D7 a17: read-only. Among the 122 disagreements in WB-May, find draft=1 passages whose ONLY five-term hits are
Latin 'LLM'/'GPT' embedded in a longer ASCII word (substring collisions), and print 40-char context + published final.
Positive control: count standalone (word-boundary) LLM/GPT hits among draft=1 passages (expected > 0)."""
import subprocess, sys, io, re
sys.stdout.reconfigure(encoding="utf-8")
import openpyxl, pandas as pd
R = r"E:/paper2  daxiu/73ae4696cf54747044a03a936c4bb958_744934475e1139b8c27898b82ae5bbf0_8/paper2_github_replication"
b = subprocess.run(["git", "--no-optional-locks", "-C", R, "show", "e41356a:data/Table_3C_SOTA_validation_metrics.csv"], capture_output=True, check=True).stdout
rows = list(openpyxl.load_workbook(io.BytesIO(b), read_only=True, data_only=True)["Annotation_Blind"].iter_rows(values_only=True))
ab = pd.DataFrame(rows[1:], columns=rows[0])
n = lambda v: str(v).split(".")[0]
ab["c1"], ab["c2"], ab["draft"], ab["fin"] = ab.coder1_label.map(n), ab.coder2_label.map(n), ab.adjudication_label.map(n), ab.final_label.map(n)
d = ab[ab.c1 != ab.c2]
print("=== RESULTS ===")
standalone = 0
for _, r in d[d.draft == "1"].iterrows():
    t = str(r.mdna_passage)
    cn = [w for w in ("大模型", "大语言模型", "预训练模型") if w in t]
    lat = [(m.group(0), t[max(0, m.start()-15): m.end()+15]) for m in re.finditer(r"[A-Za-z0-9]*(?i:llm|gpt)[A-Za-z0-9]*", t)]
    stand = [x for x, _ in lat if x.lower() in ("llm", "llms", "gpt") or re.fullmatch(r"(?i)(chat)?gpt[-0-9a-z.]*|llms?", x)]
    standalone += bool(stand)
    if not cn and lat and not stand:
        print(f"collision {r.sample_id} tokens={[x for x,_ in lat]} final={r.fin} ctx={lat[0][1]!r}")
print("positive control: draft=1 passages with a standalone LLM/GPT token:", standalone, "of", int((d.draft == '1').sum()))
print("=== END RESULTS ===")
