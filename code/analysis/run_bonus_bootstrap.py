import sys
sys.path.insert(0, r"C:\Users\asus\AppData\Local\Temp\claude\E--Supply---SHAP\ff49c3f8-4243-4540-abcd-8d73380c708c\scratchpad")
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import pyfixest as pf
from common import load_pack, CONTROLS
from battery_ext import extend_pack

pd.set_option("display.width", 200)

df_main = extend_pack(load_pack("main"))
controls_str = " + ".join(CONTROLS)

print("=" * 100)
print("BONUS: Year-dimension wild-cluster bootstrap (pyfixest), main sample")
print("vcov={'CRV1':'Year'}; wildboottest(reps=9999, cluster='Year', seed=42, bootstrap_type='11')")
print("=" * 100)
n_years = df_main["Year"].nunique()
print(f"Distinct Year values in main pack: {n_years} -> {sorted(df_main['Year'].unique())}")
print()

specs = {
    "2_PP_prose (Focal_GenAI_Index x PP_prose)": (
        f"Focal_ROA ~ Focal_GenAI_Index + PP_prose + Focal_GenAI_Index:PP_prose + {controls_str} | Focal_Industry + Year",
        "Focal_GenAI_Index:PP_prose",
    ),
    "3_PP_purchase (Focal_GenAI_Index x PP_purchase)": (
        f"Focal_ROA ~ Focal_GenAI_Index + PP_purchase + Focal_GenAI_Index:PP_purchase + {controls_str} | Focal_Industry + Year",
        "Focal_GenAI_Index:PP_purchase",
    ),
}

results = []
for label, (fml, param) in specs.items():
    print("-" * 100)
    print(label)
    print("formula:", fml)
    try:
        fit = pf.feols(fml, data=df_main, vcov={"CRV1": "Year"})
        n_eff = fit._N
        print(f"  pyfixest N used = {n_eff}  (raw pack N = {len(df_main)})")
        coef = fit.coef().loc[param]
        se = fit.se().loc[param]
        pval = fit.pvalue().loc[param]
        print(f"  CRV1(Year) asymptotic: coef={coef:.6f}  se={se:.6f}  p={pval:.6f}")

        res = fit.wildboottest(reps=9999, cluster="Year", param=param, seed=42, bootstrap_type="11")
        print(f"  wildboottest bootstrap_type=11 result:")
        print(res if not isinstance(res, pd.Series) else res.to_string())
        res_dict = dict(res) if hasattr(res, "keys") else {"raw_result": str(res)}
        results.append({
            "row": label, "param": param, "N": n_eff,
            "CRV1_Year_coef": float(coef), "CRV1_Year_se": float(se), "CRV1_Year_p": float(pval),
            **{f"wildboot_{k}": v for k, v in res_dict.items()},
            "status": "ok",
        })
    except Exception as e:
        print(f"  [TOOL FAILURE] {type(e).__name__}: {e}")
        results.append({"row": label, "param": param, "status": f"ERROR: {type(e).__name__}: {e}"})
    print()

pd.DataFrame(results).to_csv(
    r"C:\Users\asus\AppData\Local\Temp\claude\E--Supply---SHAP\ff49c3f8-4243-4540-abcd-8d73380c708c\scratchpad\out_bonus_bootstrap.csv",
    index=False)
print("DONE BONUS")
