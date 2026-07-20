"""
JOB 2 -- SHAP model 5-fold cross-validation R^2 (paper2 IP&M revision, round 3)
Read-only w.r.t. manuscript/data. Writes only to this scratchpad folder.

Decision rule: exact-recipe-only, one run per target, no tuning toward any expectation.

Recipe source (read, not modified):
  E:\\paper2  daxiu\\73ae4696cf54747044a03a936c4bb958_744934475e1139b8c27898b82ae5bbf0_8\\
  paper2_github_replication\\output\\shap_files\\gen_shap_ipm.py
  -> features = ['Focal_GenAI_Index','Focal_RnD_Ratio','Power_Pressure',
                 'Focal_Size','Focal_Lev','Focal_Age','Focal_CashFlow','Focal_SoE','Focal_HHI',
                 'Partner_Size','Partner_Lev','Partner_ROA']
  -> target = 'Focal_ROA'
  -> for c in features+[target]: clip to [q0.01, q0.99] (winsorize AGAIN on top of the already
     winsorized 08A pack -- this double-clip is the script's own literal behavior, reproduced exactly)
  -> sub = df[features+[target]].dropna(); X=sub[features].values; y=sub[target].values
  -> GradientBoostingRegressor(n_estimators=300, max_depth=4, learning_rate=0.05, random_state=42)

The original script loads a pre-built 'data_ready.pkl' that no longer exists next to it.
Per task instruction, the design matrix is rebuilt from the 08A pack instead:
  <PROJECT_ROOT>\\data\\processed_data\\08A_main_regression_package.xlsx  sheet main_winsorized
'Power_Pressure' is not a stored column in 08A -- it is constructed with the canonical formula
(same as prep_pack() in the round-2 backtest / 13_prepare_publication_exhibits.py):
  Power_Pressure = clip(-Power_Diff, 0) * clip(Partner_GenAI_Index - Focal_GenAI_Index, 0)
"""
from __future__ import annotations
import os

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import KFold, cross_val_score
from sklearn.metrics import r2_score

SCRATCH = Path(str(os.environ.get("PAPER2_OUT_DIR", Path(__file__).resolve().parent / "_out")))
SCRATCH.mkdir(parents=True, exist_ok=True)
LOG_PATH = SCRATCH / "job2_shap_cv_log.txt"
RESULTS_PATH = SCRATCH / "job2_shap_cv_results.json"

MAIN_PACK = Path(r"<PROJECT_ROOT>\data\processed_data\08A_main_regression_package.xlsx")

LOG: list[str] = []


def log(msg: str = "") -> None:
    LOG.append(str(msg))
    print(str(msg)[:220])


log("=" * 100)
log("JOB 2 -- SHAP MODEL 5-FOLD CROSS-VALIDATION R^2 (round 3)")
log("Decision rule: exact-recipe-only, one run per target, no tuning.")
log("=" * 100)

df = pd.read_excel(MAIN_PACK, sheet_name="main_winsorized", dtype={"Focal_ID": str, "Partner_ID": str})
log(f"Loaded 08A main_winsorized: shape={df.shape}")

# --- construct Power_Pressure exactly per canonical recipe ---
df["Power_Diff"] = pd.to_numeric(df["Power_Diff"], errors="coerce")
df["Focal_GenAI_Index"] = pd.to_numeric(df["Focal_GenAI_Index"], errors="coerce")
df["Partner_GenAI_Index"] = pd.to_numeric(df["Partner_GenAI_Index"], errors="coerce")
supplier_dominance = (-df["Power_Diff"]).clip(lower=0)
partner_ahead = (df["Partner_GenAI_Index"] - df["Focal_GenAI_Index"]).clip(lower=0)
df["Power_Pressure"] = supplier_dominance * partner_ahead
log("Constructed Power_Pressure = clip(-Power_Diff,0) * clip(Partner_GenAI_Index-Focal_GenAI_Index,0)")

features = [
    "Focal_GenAI_Index", "Focal_RnD_Ratio", "Power_Pressure",
    "Focal_Size", "Focal_Lev", "Focal_Age", "Focal_CashFlow",
    "Focal_SoE", "Focal_HHI",
    "Partner_Size", "Partner_Lev", "Partner_ROA",
]
target = "Focal_ROA"
log(f"features ({len(features)}): {features}")
log(f"target: {target}")

# null audit before clipping/dropna
for c in features + [target]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
    log(f"  null count [{c}] = {int(df[c].isna().sum())}")

# --- exact double-winsorization from gen_shap_ipm.py (clip at 1%/99% quantiles, computed on full df) ---
clip_bounds = {}
for c in features + [target]:
    q_low = df[c].quantile(0.01)
    q_hi = df[c].quantile(0.99)
    clip_bounds[c] = (float(q_low), float(q_hi))
    df[c] = df[c].clip(q_low, q_hi)
log(f"Applied 1%/99% clip per column (script's own re-winsorization step). Bounds: {clip_bounds}")

sub = df[features + [target]].dropna().copy()
X = sub[features].values
y = sub[target].values
log(f"Design matrix after dropna: N={len(sub)}  (task expectation: N~=1007, the H3 estimation sample)")

if len(sub) != 1007:
    log(f"NOTE: N={len(sub)} does not exactly equal the expected 1007 -- reported as-is, no row was dropped/added "
        f"to force a match.")
else:
    log("N MATCHES the expected H3 estimation sample of 1007 exactly.")

# --- fit the exact model spec, in-sample R^2 ---
model = GradientBoostingRegressor(n_estimators=300, max_depth=4, learning_rate=0.05, random_state=42)
model.fit(X, y)
insample_pred = model.predict(X)
insample_r2 = r2_score(y, insample_pred)
log(f"In-sample R^2 (fit on full N={len(y)}, predict same data): {insample_r2:.6f}  (task expectation: ~0.91)")

# --- 5-fold CV, shuffled, random_state=42 ---
cv_model = GradientBoostingRegressor(n_estimators=300, max_depth=4, learning_rate=0.05, random_state=42)
kf = KFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(cv_model, X, y, cv=kf, scoring="r2")
cv_mean = float(np.mean(cv_scores))
cv_sd = float(np.std(cv_scores, ddof=1))
log(f"5-fold CV R^2 scores per fold: {[round(float(s), 6) for s in cv_scores]}")
log(f"5-fold CV R^2: mean={cv_mean:.6f}  sd={cv_sd:.6f}  (ddof=1, sample sd across the 5 fold scores)")

results = {
    "n_features": len(features),
    "features": features,
    "target": target,
    "N": int(len(sub)),
    "N_expected": 1007,
    "clip_bounds": clip_bounds,
    "model_spec": {"n_estimators": 300, "max_depth": 4, "learning_rate": 0.05, "random_state": 42},
    "insample_r2": insample_r2,
    "cv_fold_scores": [float(s) for s in cv_scores],
    "cv_r2_mean": cv_mean,
    "cv_r2_sd": cv_sd,
    "kfold_spec": {"n_splits": 5, "shuffle": True, "random_state": 42},
}

with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("DONE.")
print(f"in-sample R2 = {insample_r2:.4f}")
print(f"5-fold CV R2 = {cv_mean:.4f} +/- {cv_sd:.4f}")
print(f"N = {len(sub)}")
