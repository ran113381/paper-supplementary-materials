from pathlib import Path
import os
import sys
sys.path.insert(0, str(os.environ.get("PAPER2_OUT_DIR", Path(__file__).resolve().parent / "_out")))
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from common import load_pack, CONTROLS
from battery_ext import extend_pack

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", None)

OUTDIR = str(os.environ.get("PAPER2_OUT_DIR", Path(__file__).resolve().parent / "_out"))

df_main = extend_pack(load_pack("main"))
df_strict = extend_pack(load_pack("strict"))


def decompose(df, sample_name):
    rows = []
    for yr, g in df.groupby("Year"):
        n_total = len(g)

        pa_nonmissing = g["Partner_Ahead"].notna().sum()
        pa_nonzero = (g["Partner_Ahead"] > 0).sum()

        sd_nonmissing = g["Supplier_Dominance"].notna().sum()
        sd_nonzero = (g["Supplier_Dominance"] > 0).sum()

        pdb_nonmissing = g["PartnerDominance_bin"].notna().sum()
        pdb_1 = (g["PartnerDominance_bin"] == 1).sum()

        rows.append({
            "sample": sample_name, "Year": int(yr), "N_total": n_total,
            "PartnerAhead_nonmissing": int(pa_nonmissing),
            "PartnerAhead_nonzero": int(pa_nonzero),
            "PartnerAhead_nonzero_pct_of_total": round(100 * pa_nonzero / n_total, 2),
            "PartnerAhead_nonzero_pct_of_nonmissing": round(100 * pa_nonzero / pa_nonmissing, 2) if pa_nonmissing else None,
            "SupplierDominance_nonmissing": int(sd_nonmissing),
            "SupplierDominance_nonzero": int(sd_nonzero),
            "SupplierDominance_nonzero_pct_of_total": round(100 * sd_nonzero / n_total, 2),
            "SupplierDominance_nonzero_pct_of_nonmissing": round(100 * sd_nonzero / sd_nonmissing, 2) if sd_nonmissing else None,
            "PartnerDominance_bin_eq1": int(pdb_1),
            "PartnerDominance_bin_eq1_pct_of_total": round(100 * pdb_1 / n_total, 2),
            "PartnerDominance_bin_eq1_pct_of_nonmissing": round(100 * pdb_1 / pdb_nonmissing, 2) if pdb_nonmissing else None,
        })
    return pd.DataFrame(rows).sort_values("Year")


decomp_main = decompose(df_main, "main")
decomp_strict = decompose(df_strict, "strict")

decomp_main.to_csv(f"{OUTDIR}/out_decomposition_main.csv", index=False)
decomp_strict.to_csv(f"{OUTDIR}/out_decomposition_strict.csv", index=False)

print("=== COMPONENT-CONCENTRATION DECOMPOSITION (main sample, as required) ===")
print(decomp_main.to_string(index=False))

print()
print("=== SAME DECOMPOSITION, STRICT SAMPLE (supplementary, not explicitly required but for completeness) ===")
print(decomp_strict.to_string(index=False))

# Concentration summary: what share of ALL nonzero Partner_Ahead obs (pooled across whole panel)
# falls in 2023-2025 vs what share of ALL nonzero Supplier_Dominance obs falls in 2023-2025.
print()
print("=== POOLED CONCENTRATION SUMMARY (main sample) ===")
total_pa_nonzero = (df_main["Partner_Ahead"] > 0).sum()
pa_nonzero_2023_2025 = (df_main["Partner_Ahead"] > 0) & (df_main["Year"] >= 2023)
print(f"Total nonzero Partner_Ahead obs (all years): {total_pa_nonzero}")
print(f"Nonzero Partner_Ahead obs in 2023-2025: {pa_nonzero_2023_2025.sum()}  "
      f"({100*pa_nonzero_2023_2025.sum()/total_pa_nonzero:.2f}% of all nonzero Partner_Ahead obs)")

total_sd_nonzero = (df_main["Supplier_Dominance"] > 0).sum()
sd_nonzero_2023_2025 = (df_main["Supplier_Dominance"] > 0) & (df_main["Year"] >= 2023)
print(f"Total nonzero Supplier_Dominance obs (all years): {total_sd_nonzero}")
print(f"Nonzero Supplier_Dominance obs in 2023-2025: {sd_nonzero_2023_2025.sum()}  "
      f"({100*sd_nonzero_2023_2025.sum()/total_sd_nonzero:.2f}% of all nonzero Supplier_Dominance obs)")

total_pdb1 = (df_main["PartnerDominance_bin"] == 1).sum()
pdb1_2023_2025 = (df_main["PartnerDominance_bin"] == 1) & (df_main["Year"] >= 2023)
print(f"Total PartnerDominance_bin==1 obs (all years): {total_pdb1}")
print(f"PartnerDominance_bin==1 obs in 2023-2025: {pdb1_2023_2025.sum()}  "
      f"({100*pdb1_2023_2025.sum()/total_pdb1:.2f}% of all PartnerDominance_bin==1 obs)")

# also same computed as share of TOTAL PANEL that falls 2023-2025, for reference (base rate)
total_n = len(df_main)
n_2023_2025 = (df_main["Year"] >= 2023).sum()
print(f"\nFor reference: {n_2023_2025}/{total_n} ({100*n_2023_2025/total_n:.2f}%) of ALL main-sample obs (regardless of component) fall in 2023-2025.")
print("DONE PART 3")
