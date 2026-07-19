"""
05_build_genai_measurement.py
=============================
Build a reproducible GenAI dictionary and firm-year index from the official
firm-year text pool.

Design
------
- Primary text source: CSMAR annual MDA workbook.
- Supplement source: CNRDS annual-report text files (12-31 only) for firm-years
  missing from the primary source.
- Baseline GenAI measure: longest-match, non-overlapping count.
- Robustness GenAI measure: overlapping dictionary count, following the original
  Excel-style formula logic supplied by the user.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw_data"
PROC_DIR = PROJECT_ROOT / "data" / "processed_data"
MERGED_POOL_CANDIDATES = [
    PROC_DIR / "02_bilateral_financial_panel.xlsx",
    PROC_DIR / "02_financial_merged.xlsx",
]

DICT_OUT = PROC_DIR / "04_genai_dictionary.xlsx"
PANEL_OUT = PROC_DIR / "05_genai_firm_year_panel.xlsx"


FORMULA_TEXT = r'''=(LEN(E2)-LEN(SUBSTITUTE(E2,"生成式人工智能","")))/7+(LEN(E2)-LEN(SUBSTITUTE(E2,"生成式AI","")))/5+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"GENAI","")))/5+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"GENERATIVE AI","")))/13+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"AIGC","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"大语言模型","")))/5+(LEN(E2)-LEN(SUBSTITUTE(E2,"大模型","")))/3+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"LLM","")))/3+(LEN(E2)-LEN(SUBSTITUTE(E2,"人工智能基础模型","")))/8+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"FOUNDATION MODEL","")))/16+(LEN(E2)-LEN(SUBSTITUTE(E2,"预训练模型","")))/5+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"PRETRAINED MODEL","")))/16+(LEN(E2)-LEN(SUBSTITUTE(E2,"深度合成","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"提示词","")))/3+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"PROMPT","")))/6+(LEN(E2)-LEN(SUBSTITUTE(E2,"思维链","")))/3+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"COT","")))/3+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"RLHF","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"多模态生成","")))/5+(LEN(E2)-LEN(SUBSTITUTE(E2,"多模态大模型","")))/6+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"TRANSFORMER","")))/11+(LEN(E2)-LEN(SUBSTITUTE(E2,"生成对抗网络","")))/6+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"GAN","")))/3+(LEN(E2)-LEN(SUBSTITUTE(E2,"扩散模型","")))/4+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"DIFFUSION","")))/9+(LEN(E2)-LEN(SUBSTITUTE(E2,"变分自编码器","")))/6+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"VAE","")))/3+(LEN(E2)-LEN(SUBSTITUTE(E2,"自回归模型","")))/5+(LEN(E2)-LEN(SUBSTITUTE(E2,"智能体","")))/3+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"AI AGENT","")))/8+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"CHATGPT","")))/7+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"GPT","")))/3+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"OPENAI","")))/6+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"COPILOT","")))/7+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"CLAUDE","")))/6+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"ANTHROPIC","")))/9+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"GEMINI","")))/6+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"PALM","")))/4+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"LLAMA","")))/5+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"MISTRAL","")))/7+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"GROK","")))/4+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"HUGGING FACE","")))/12+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"SORA","")))/4+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"MIDJOURNEY","")))/10+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"STABLE DIFFUSION","")))/16+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"DALL-E","")))/6+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"RUNWAY","")))/6+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"PIKA","")))/4+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"DEEPSEEK","")))/8+(LEN(E2)-LEN(SUBSTITUTE(E2,"深度求索","")))/4+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"KIMI","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"月之暗面","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"文心一言","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"文心大模型","")))/5+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"ERNIE","")))/5+(LEN(E2)-LEN(SUBSTITUTE(E2,"通义千问","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"通义万相","")))/4+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"QWEN","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"混元大模型","")))/5+(LEN(E2)-LEN(SUBSTITUTE(E2,"腾讯混元","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"盘古大模型","")))/5+(LEN(E2)-LEN(SUBSTITUTE(E2,"华为盘古","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"星火大模型","")))/5+(LEN(E2)-LEN(SUBSTITUTE(E2,"讯飞星火","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"智谱清言","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"智谱AI","")))/4+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"CHATGLM","")))/7+(LEN(E2)-LEN(SUBSTITUTE(E2,"百川智能","")))/4+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"BAICHUAN","")))/8+(LEN(E2)-LEN(SUBSTITUTE(E2,"豆包","")))/2+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"DOUBAO","")))/6+(LEN(E2)-LEN(SUBSTITUTE(E2,"海螺","")))/2+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"MINIMAX","")))/7+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"ABAB大模型","")))/6+(LEN(E2)-LEN(SUBSTITUTE(E2,"幻方量化","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"零一万物","")))/4+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"YI大模型","")))/5+(LEN(E2)-LEN(SUBSTITUTE(E2,"阶跃星辰","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"面壁智能","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"天工大模型","")))/5+(LEN(E2)-LEN(SUBSTITUTE(E2,"商量大模型","")))/5+(LEN(E2)-LEN(SUBSTITUTE(E2,"日日新大模型","")))/6+(LEN(E2)-LEN(SUBSTITUTE(E2,"蓝心大模型","")))/5+(LEN(E2)-LEN(SUBSTITUTE(E2,"言犀大模型","")))/5+(LEN(E2)-LEN(SUBSTITUTE(E2,"可灵","")))/2+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"VIDU","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"生数大模型","")))/5+(LEN(E2)-LEN(SUBSTITUTE(E2,"火山引擎","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"火山方舟","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"千帆大模型","")))/5+(LEN(E2)-LEN(SUBSTITUTE(E2,"百炼大模型","")))/5+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"MODELARTS","")))/9+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"AMAZON BEDROCK","")))/14+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"VERTEX AI","")))/9+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"NVIDIA AI","")))/9+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"RAG","")))/3+(LEN(E2)-LEN(SUBSTITUTE(E2,"检索增强生成","")))/6+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"SFT","")))/3+(LEN(E2)-LEN(SUBSTITUTE(E2,"指令微调","")))/4+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"LORA","")))/4+(LEN(E2)-LEN(SUBSTITUTE(E2,"向量数据库","")))/5+(LEN(E2)-LEN(SUBSTITUTE(UPPER(E2),"MOE","")))/3+(LEN(E2)-LEN(SUBSTITUTE(E2,"混合专家模型","")))/6'''


def normalize_code(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
        .str.zfill(6)
    )


def extract_terms() -> list[str]:
    raw = re.findall(r'"([^"]*)"', FORMULA_TEXT)
    out = []
    for term in raw:
        if not term:
            continue
        if term not in out:
            out.append(term)
    return out


def classify_term(term: str) -> str:
    upper = term.upper()
    if upper in {"生成式人工智能", "生成式AI".upper(), "GENAI", "GENERATIVE AI", "AIGC"}:
        return "core_concept"
    if upper in {"大语言模型", "大模型", "LLM", "人工智能基础模型", "FOUNDATION MODEL", "预训练模型", "PRETRAINED MODEL", "深度合成", "提示词", "PROMPT", "思维链", "COT", "RLHF", "多模态生成", "多模态大模型", "TRANSFORMER", "生成对抗网络", "GAN", "扩散模型", "DIFFUSION", "变分自编码器", "VAE", "自回归模型", "智能体", "AI AGENT", "RAG", "检索增强生成", "SFT", "指令微调", "LORA", "向量数据库", "MOE", "混合专家模型"}:
        return "technology_term"
    if upper in {"MODELARTS", "AMAZON BEDROCK", "VERTEX AI", "NVIDIA AI", "火山引擎", "火山方舟", "千帆大模型", "百炼大模型"}:
        return "platform_infrastructure"
    return "product_or_vendor"


def dictionary_df() -> pd.DataFrame:
    terms = extract_terms()
    rows = []
    for i, term in enumerate(terms, start=1):
        rows.append(
            {
                "term_order": i,
                "term": term,
                "term_upper": term.upper(),
                "term_length": len(term),
                "group": classify_term(term),
            }
        )
    return pd.DataFrame(rows)


def merged_pool_file() -> Path:
    for path in MERGED_POOL_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("Cannot find a financial-panel source for the GenAI firm-year pool.")


def build_target_firm_year_pool() -> set[tuple[str, int]]:
    """Use the official merged bilateral table as the unique firm-year text pool."""
    merged = pd.read_excel(merged_pool_file(), dtype={"Focal_ID": str, "Partner_ID": str})
    merged["Year"] = pd.to_numeric(merged["Year"], errors="coerce").astype("Int64")
    focal = merged[["Focal_ID", "Year"]].rename(columns={"Focal_ID": "Firm_ID"})
    partner = merged[["Partner_ID", "Year"]].rename(columns={"Partner_ID": "Firm_ID"})
    pool = pd.concat([focal, partner], ignore_index=True).dropna().drop_duplicates()
    return set(pool.itertuples(index=False, name=None))


def read_csmar_mda(target_keys: set[tuple[str, int]]) -> pd.DataFrame:
    name = next(n for n in os.listdir(RAW_DIR) if "MDA" in n and n.endswith(".xlsx") and "crmas" in n)
    path = RAW_DIR / name
    df = pd.read_excel(path, header=0)
    code_col, _, date_col, text_col = df.columns[:4]
    df["Firm_ID"] = normalize_code(df[code_col])
    dt = pd.to_datetime(df[date_col], errors="coerce")
    df["Year"] = dt.dt.year.astype("Int64")
    df["Month"] = dt.dt.month.astype("Int64")
    df["MDA_Text"] = df[text_col].fillna("").astype(str)
    out = df[df["Month"] == 12][["Firm_ID", "Year", "MDA_Text"]].drop_duplicates(subset=["Firm_ID", "Year"])
    out = out[out.apply(lambda r: (r["Firm_ID"], int(r["Year"])) in target_keys, axis=1)].copy()
    out["Text_Source"] = "CSMAR_MDA"
    return out


def read_txt_with_fallback(path: Path) -> str:
    for enc in ["utf-8", "gb18030", "gbk"]:
        try:
            return path.read_text(encoding=enc, errors="ignore")
        except Exception:
            continue
    return path.read_text(errors="ignore")


def read_cnrds_mda_txt(existing_keys: set[tuple[str, int]], target_keys: set[tuple[str, int]]) -> pd.DataFrame:
    root = RAW_DIR / "cnrds_MDA"
    rows = []
    if not root.exists():
        return pd.DataFrame(columns=["Firm_ID", "Year", "MDA_Text", "Text_Source"])

    pattern = re.compile(r"^(\d{6})_(\d{4})-12-31\.txt$", re.IGNORECASE)
    for year_dir in sorted([p for p in root.iterdir() if p.is_dir() and p.name.isdigit()]):
        txt_dir = year_dir / "文本"
        if not txt_dir.exists():
            continue
        for txt_file in txt_dir.iterdir():
            m = pattern.match(txt_file.name)
            if not m:
                continue
            firm_id = m.group(1)
            year = int(m.group(2))
            key = (firm_id, year)
            if key not in target_keys:
                continue
            if key in existing_keys:
                continue
            text = read_txt_with_fallback(txt_file)
            rows.append({"Firm_ID": firm_id, "Year": year, "MDA_Text": text, "Text_Source": "CNRDS_MDA_TXT"})
    return pd.DataFrame(rows)


def build_pattern(terms_upper: list[str]) -> re.Pattern[str]:
    ordered = sorted(terms_upper, key=lambda x: (-len(x), x))
    escaped = [re.escape(x) for x in ordered]
    return re.compile("|".join(escaped))


def compute_genai_metrics(text: str, terms_upper: list[str], pattern: re.Pattern[str]) -> tuple[int, int, int, float]:
    upper_text = text.upper()
    clean_matches = [m.group(0) for m in pattern.finditer(upper_text)]
    overlap_count = sum(upper_text.count(term) for term in terms_upper)
    clean_count = len(clean_matches)
    breadth = len(set(clean_matches))
    index = float(np.log1p(clean_count))
    return clean_count, overlap_count, breadth, index


def build_genai_panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    dict_df = dictionary_df()
    dict_df.to_excel(DICT_OUT, index=False)

    target_keys = build_target_firm_year_pool()
    csmar = read_csmar_mda(target_keys)
    existing_keys = set(csmar[["Firm_ID", "Year"]].drop_duplicates().itertuples(index=False, name=None))
    cnrds = read_cnrds_mda_txt(existing_keys, target_keys)
    panel = pd.concat([csmar, cnrds], ignore_index=True)

    terms_upper = dict_df["term_upper"].tolist()
    pattern = build_pattern(terms_upper)

    metrics = [compute_genai_metrics(text, terms_upper, pattern) for text in panel["MDA_Text"].fillna("").astype(str)]
    panel["GenAI_Freq_Clean"] = [m[0] for m in metrics]
    panel["GenAI_Freq_Overlap"] = [m[1] for m in metrics]
    panel["GenAI_Breadth"] = [m[2] for m in metrics]
    panel["GenAI_Index"] = [m[3] for m in metrics]
    panel["GenAI_Index_Overlap"] = np.log1p(panel["GenAI_Freq_Overlap"])
    panel["GenAI_Dummy"] = (panel["GenAI_Freq_Clean"] > 0).astype(int)
    panel["MDA_CharCount"] = panel["MDA_Text"].astype(str).str.len()

    out_cols = [
        "Firm_ID",
        "Year",
        "Text_Source",
        "MDA_CharCount",
        "GenAI_Freq_Clean",
        "GenAI_Freq_Overlap",
        "GenAI_Index",
        "GenAI_Index_Overlap",
        "GenAI_Dummy",
        "GenAI_Breadth",
    ]
    out = panel[out_cols].drop_duplicates(subset=["Firm_ID", "Year"])
    out.to_excel(PANEL_OUT, index=False)
    return dict_df, out


def merge_into_sample(df: pd.DataFrame, genai: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "Year" in out.columns:
        out["Year"] = pd.to_numeric(out["Year"], errors="coerce").astype("Int64")
    if "Focal_ID" in out.columns:
        out["Focal_ID"] = normalize_code(out["Focal_ID"])
    if "Partner_ID" in out.columns:
        out["Partner_ID"] = normalize_code(out["Partner_ID"])

    # Remove old placeholder GenAI columns before merging the real panel.
    drop_cols = [
        c
        for c in out.columns
        if c.startswith("Focal_GenAI")
        or c.startswith("Partner_GenAI")
        or c.startswith("Focal_MDA_")
        or c.startswith("Partner_MDA_")
    ]
    out = out.drop(columns=drop_cols, errors="ignore")

    focal = genai.rename(
        columns={
            "Firm_ID": "Focal_ID",
            "Text_Source": "Focal_GenAI_Source",
            "MDA_CharCount": "Focal_MDA_CharCount",
            "GenAI_Freq_Clean": "Focal_GenAI_Freq_Clean",
            "GenAI_Freq_Overlap": "Focal_GenAI_Freq_Overlap",
            "GenAI_Index": "Focal_GenAI_Index",
            "GenAI_Index_Overlap": "Focal_GenAI_Index_Overlap",
            "GenAI_Dummy": "Focal_GenAI_Dummy",
            "GenAI_Breadth": "Focal_GenAI_Breadth",
        }
    )
    partner = genai.rename(
        columns={
            "Firm_ID": "Partner_ID",
            "Text_Source": "Partner_GenAI_Source",
            "MDA_CharCount": "Partner_MDA_CharCount",
            "GenAI_Freq_Clean": "Partner_GenAI_Freq_Clean",
            "GenAI_Freq_Overlap": "Partner_GenAI_Freq_Overlap",
            "GenAI_Index": "Partner_GenAI_Index",
            "GenAI_Index_Overlap": "Partner_GenAI_Index_Overlap",
            "GenAI_Dummy": "Partner_GenAI_Dummy",
            "GenAI_Breadth": "Partner_GenAI_Breadth",
        }
    )

    out = out.merge(
        focal[
            [
                "Focal_ID",
                "Year",
                "Focal_GenAI_Source",
                "Focal_MDA_CharCount",
                "Focal_GenAI_Freq_Clean",
                "Focal_GenAI_Freq_Overlap",
                "Focal_GenAI_Index",
                "Focal_GenAI_Index_Overlap",
                "Focal_GenAI_Dummy",
                "Focal_GenAI_Breadth",
            ]
        ],
        on=["Focal_ID", "Year"],
        how="left",
    )
    out = out.merge(
        partner[
            [
                "Partner_ID",
                "Year",
                "Partner_GenAI_Source",
                "Partner_MDA_CharCount",
                "Partner_GenAI_Freq_Clean",
                "Partner_GenAI_Freq_Overlap",
                "Partner_GenAI_Index",
                "Partner_GenAI_Index_Overlap",
                "Partner_GenAI_Dummy",
                "Partner_GenAI_Breadth",
            ]
        ],
        on=["Partner_ID", "Year"],
        how="left",
    )
    return out


def update_formulas(formulas: pd.DataFrame) -> pd.DataFrame:
    extra = pd.DataFrame(
        [
            ["Focal_GenAI_Index", "ln(1 + clean non-overlapping GenAI dictionary count in focal MDA)", "Baseline GenAI measure"],
            ["Focal_GenAI_Index_Overlap", "ln(1 + overlap GenAI dictionary count in focal MDA)", "Robustness measure following the original Excel-style counting logic"],
            ["Focal_GenAI_Dummy", "1 if clean GenAI count > 0", "Robustness measure"],
            ["Focal_GenAI_Breadth", "Number of distinct dictionary terms matched under longest-match counting", "Robustness measure"],
            ["Partner_GenAI_Index", "ln(1 + clean non-overlapping GenAI dictionary count in partner MDA)", "Baseline GenAI measure"],
            ["Partner_GenAI_Index_Overlap", "ln(1 + overlap GenAI dictionary count in partner MDA)", "Robustness measure following the original Excel-style counting logic"],
            ["Partner_GenAI_Dummy", "1 if clean GenAI count > 0", "Robustness measure"],
            ["Partner_GenAI_Breadth", "Number of distinct dictionary terms matched under longest-match counting", "Robustness measure"],
        ],
        columns=["variable", "formula", "note"],
    )
    keep = formulas[~formulas["variable"].isin(extra["variable"])].copy()
    return pd.concat([keep, extra], ignore_index=True)


def coverage(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for col in cols:
        rows.append(
            {
                "variable": col,
                "non_missing": int(df[col].notna().sum()) if col in df.columns else 0,
                "missing": int(df[col].isna().sum()) if col in df.columns else len(df),
                "missing_pct": round(df[col].isna().mean() * 100, 2) if col in df.columns else 100.0,
            }
        )
    return pd.DataFrame(rows)


def descriptives(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for col in cols:
        s = pd.to_numeric(df[col], errors="coerce")
        rows.append(
            {
                "variable": col,
                "n": int(s.notna().sum()),
                "missing_pct": round(s.isna().mean() * 100, 2),
                "mean": s.mean(),
                "median": s.median(),
                "std": s.std(),
                "min": s.min(),
                "p25": s.quantile(0.25),
                "p75": s.quantile(0.75),
                "max": s.max(),
            }
        )
    return pd.DataFrame(rows)


def update_package_workbook(genai: pd.DataFrame) -> None:
    xls = pd.ExcelFile(WORKBOOK)
    ordered = xls.sheet_names
    sheets = {sheet: pd.read_excel(WORKBOOK, sheet_name=sheet) for sheet in ordered}
    xls.close()

    for sheet in ["main_raw", "main_winsorized", "strict_raw", "strict_winsorized"]:
        if sheet in sheets:
            sheets[sheet] = merge_into_sample(sheets[sheet], genai)

    if "formulas" in sheets:
        sheets["formulas"] = update_formulas(sheets["formulas"])

    main_genai_cols = [
        "Focal_GenAI_Index",
        "Focal_GenAI_Index_Overlap",
        "Focal_GenAI_Dummy",
        "Focal_GenAI_Breadth",
        "Partner_GenAI_Index",
        "Partner_GenAI_Index_Overlap",
        "Partner_GenAI_Dummy",
        "Partner_GenAI_Breadth",
    ]
    if "main_coverage" in sheets:
        base_cov = sheets["main_coverage"]
        extra_cov = coverage(sheets["main_raw"], main_genai_cols)
        sheets["main_coverage"] = pd.concat([base_cov[~base_cov["variable"].isin(main_genai_cols)], extra_cov], ignore_index=True)
    if "strict_coverage" in sheets:
        base_cov = sheets["strict_coverage"]
        extra_cov = coverage(sheets["strict_raw"], main_genai_cols)
        sheets["strict_coverage"] = pd.concat([base_cov[~base_cov["variable"].isin(main_genai_cols)], extra_cov], ignore_index=True)
    if "main_descriptives" in sheets:
        base_desc = sheets["main_descriptives"]
        extra_desc = descriptives(sheets["main_raw"], [c for c in main_genai_cols if "Dummy" not in c])
        sheets["main_descriptives"] = pd.concat([base_desc[~base_desc["variable"].isin(extra_desc["variable"])], extra_desc], ignore_index=True)
    if "strict_descriptives" in sheets:
        base_desc = sheets["strict_descriptives"]
        extra_desc = descriptives(sheets["strict_raw"], [c for c in main_genai_cols if "Dummy" not in c])
        sheets["strict_descriptives"] = pd.concat([base_desc[~base_desc["variable"].isin(extra_desc["variable"])], extra_desc], ignore_index=True)

    with pd.ExcelWriter(WORKBOOK, engine="openpyxl") as writer:
        for sheet in ordered:
            sheets[sheet].to_excel(writer, sheet_name=sheet, index=False)


def main() -> None:
    _, genai = build_genai_panel()
    print("Built standalone GenAI dictionary and firm-year panel from the official financial-panel firm-year pool.")
    print(f"Dictionary : {DICT_OUT}")
    print(f"GenAI panel: {PANEL_OUT}")


if __name__ == "__main__":
    main()
