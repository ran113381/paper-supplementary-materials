import sys
sys.path.insert(0, r"C:\Users\asus\AppData\Local\Temp\claude\E--Supply---SHAP\ff49c3f8-4243-4540-abcd-8d73380c708c\scratchpad")
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from common import load_pack, CONTROLS
from battery_ext import extend_pack, run_row_battery

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", None)

OUTDIR = r"C:\Users\asus\AppData\Local\Temp\claude\E--Supply---SHAP\ff49c3f8-4243-4540-abcd-8d73380c708c\scratchpad"

df_main = extend_pack(load_pack("main"))
df_strict = extend_pack(load_pack("strict"))

print("MAIN raw N =", len(df_main), " STRICT raw N =", len(df_strict))
print("MAIN Year range:", df_main["Year"].min(), "-", df_main["Year"].max())
print("STRICT Year range:", df_strict["Year"].min(), "-", df_strict["Year"].max())

# ============================================================
# PART 1: COVERAGE AUDIT
# ============================================================
def coverage_by_year(df, sample_name, cols):
    rows = []
    for yr, g in df.groupby("Year"):
        row = {"sample": sample_name, "Year": int(yr), "N_total": len(g)}
        for c in cols:
            n_miss = int(g[c].isna().sum())
            row[f"{c}__n_missing"] = n_miss
            row[f"{c}__pct_missing"] = round(100 * n_miss / len(g), 2)
            row[f"{c}__n_present"] = len(g) - n_miss
        rows.append(row)
    return pd.DataFrame(rows).sort_values("Year")

cov_cols = ["Rela_Purchase_Ratio", "Dyad_Duration", "Ln_Dyad_Duration"]
cov_main = coverage_by_year(df_main, "main", cov_cols)
cov_strict = coverage_by_year(df_strict, "strict", cov_cols)
cov_all = pd.concat([cov_main, cov_strict], ignore_index=True)
cov_all.to_csv(f"{OUTDIR}/out_coverage_audit.csv", index=False)
print("\n=== COVERAGE AUDIT (main) ===")
print(cov_main.to_string(index=False))
print("\n=== COVERAGE AUDIT (strict) ===")
print(cov_strict.to_string(index=False))

# supplementary: GenAI index missingness by year (feeds Partner_Ahead / all PP_* variants)
cov_genai_main = coverage_by_year(df_main, "main", ["Focal_GenAI_Index", "Partner_GenAI_Index", "Partner_Ahead", "Supplier_Dominance"])
cov_genai_strict = coverage_by_year(df_strict, "strict", ["Focal_GenAI_Index", "Partner_GenAI_Index", "Partner_Ahead", "Supplier_Dominance"])
cov_genai_main.to_csv(f"{OUTDIR}/out_coverage_genai_supplementary_main.csv", index=False)
cov_genai_strict.to_csv(f"{OUTDIR}/out_coverage_genai_supplementary_strict.csv", index=False)
print("\n=== SUPPLEMENTARY: GenAI-index / Partner_Ahead / Supplier_Dominance coverage by year (main) ===")
print(cov_genai_main.to_string(index=False))
print("\n=== SUPPLEMENTARY: GenAI-index / Partner_Ahead / Supplier_Dominance coverage by year (strict) ===")
print(cov_genai_strict.to_string(index=False))

# ============================================================
# PART 2: THE 8-ROW BATTERY
# ============================================================
all_results = []

def add(row_name, rhs_fn, targets_fn):
    res = run_row_battery(df_main, df_strict, row_name, rhs_fn, targets_fn)
    all_results.extend(res)
    print(f"  ... row {row_name} done ({len(res)} result rows)")

print("\n\n" + "=" * 100)
print("RUNNING 8-ROW BATTERY")
print("=" * 100)

add("1_PP_code",
    lambda: ["Focal_GenAI_Index", "PP_code", "Focal_GenAI_Index:PP_code"] + CONTROLS,
    lambda: [["Focal_GenAI_Index", "PP_code"]])

add("2_PP_prose",
    lambda: ["Focal_GenAI_Index", "PP_prose", "Focal_GenAI_Index:PP_prose"] + CONTROLS,
    lambda: [["Focal_GenAI_Index", "PP_prose"]])

add("3_PP_purchase",
    lambda: ["Focal_GenAI_Index", "PP_purchase", "Focal_GenAI_Index:PP_purchase"] + CONTROLS,
    lambda: [["Focal_GenAI_Index", "PP_purchase"]])

add("4_PP_duration",
    lambda: ["Focal_GenAI_Index", "PP_duration", "Focal_GenAI_Index:PP_duration"] + CONTROLS,
    lambda: [["Focal_GenAI_Index", "PP_duration"]])

add("5_PP_binahead",
    lambda: ["Focal_GenAI_Index", "PP_binahead", "Focal_GenAI_Index:PP_binahead"] + CONTROLS,
    lambda: [["Focal_GenAI_Index", "PP_binahead"]])

add("6_Ahead_only",
    lambda: ["Focal_GenAI_Index", "Partner_Ahead", "Focal_GenAI_Index:Partner_Ahead"] + CONTROLS,
    lambda: [["Focal_GenAI_Index", "Partner_Ahead"]])

add("7_Dominance_only",
    lambda: ["Focal_GenAI_Index", "Supplier_Dominance", "Focal_GenAI_Index:Supplier_Dominance"] + CONTROLS,
    lambda: [["Focal_GenAI_Index", "Supplier_Dominance"]])

add("8_Joint_necessity",
    lambda: ["Focal_GenAI_Index", "Supplier_Dominance", "Partner_Ahead",
             "Supplier_Dominance:Partner_Ahead",
             "Focal_GenAI_Index:Supplier_Dominance",
             "Focal_GenAI_Index:Partner_Ahead",
             "Focal_GenAI_Index:Supplier_Dominance:Partner_Ahead"] + CONTROLS,
    lambda: [["Focal_GenAI_Index", "Supplier_Dominance"],
             ["Focal_GenAI_Index", "Partner_Ahead"],
             ["Focal_GenAI_Index", "Supplier_Dominance", "Partner_Ahead"]])

battery_df = pd.DataFrame(all_results)
battery_df.to_csv(f"{OUTDIR}/out_battery_results.csv", index=False)
print("\nFull battery result count:", len(battery_df))
print(battery_df[["row", "sample", "condition", "term", "status", "coef", "se", "p", "N", "n_clusters"]].to_string(index=False))

flagged = battery_df[battery_df["status"] != "ok"]
print("\n=== FLAGGED ROWS (status != ok) ===")
if len(flagged) == 0:
    print("  none")
else:
    print(flagged.to_string(index=False))

warned = battery_df[battery_df["warnings"].astype(str).str.len() > 0]
print("\n=== ROWS WITH WARNINGS ===")
if len(warned) == 0:
    print("  none")
else:
    print(warned[["row", "sample", "condition", "term", "warnings"]].to_string(index=False))

print("\nDONE PART 2")
