from __future__ import annotations

import math
import random
import re
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer


BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]

GOLD_XLSX = BASE / "GenAI_gold_standard_adjudication_draft人工双核验.xlsx"
FULL_CONSENSUS_CSV = (
    BASE
    / "GPT_full_sample_scan"
    / "web_GPT55_Claude_full_sample_pack"
    / "04_merged_reports"
    / "full_sample_gpt55_claude_consensus_labels.csv"
)

OUT_DIR = BASE / "table3c_sota_validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_XLSX = OUT_DIR / "Table_3C_SOTA_validation_metrics.xlsx"
OUT_CSV = OUT_DIR / "Table_3C_SOTA_validation_metrics.csv"
OUT_MD = OUT_DIR / "Table_3C_SOTA_validation_metrics.md"
OUT_PRED = OUT_DIR / "Table_3C_validation_predictions.csv"

MODEL_NAME = "yiyanghkust/finbert-tone-chinese"
RANDOM_SEED = 20260510
MAX_LEN = 192
BATCH_SIZE = 8
EPOCHS = 2
LEARNING_RATE = 2e-5


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def normalize_code(value: object) -> str:
    text = str(value).strip()
    text = re.sub(r"\.0$", "", text)
    return text.zfill(6)


def normalize_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value)).strip()


def hit_to_full_segment_id(value: object) -> str:
    match = re.search(r"(\d+)$", str(value))
    if not match:
        return ""
    return f"P2FULL_{int(match.group(1)):04d}"


def binary_from_consensus(label: str) -> int:
    return 1 if label == "substantive_adoption" else 0


def binary_from_gold(label: object) -> int | None:
    text = str(label).strip()
    if text in {"1", "1.0"}:
        return 1
    if text in {"0", "0.0"}:
        return 0
    return None


def metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float | int]:
    tp = fp = tn = fn = 0
    for y, p in zip(y_true, y_pred):
        if y == 1 and p == 1:
            tp += 1
        elif y == 0 and p == 1:
            fp += 1
        elif y == 0 and p == 0:
            tn += 1
        elif y == 1 and p == 0:
            fn += 1
    n = tp + fp + tn + fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / n if n else 0.0
    return {
        "N_eval": n,
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
    }


class TextDataset(Dataset):
    def __init__(self, texts: list[str], labels: list[int], tokenizer):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        enc = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=MAX_LEN,
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long),
        }


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    annotation = pd.read_excel(GOLD_XLSX, sheet_name="Annotation_Blind", dtype={"firm_id": str})
    metadata = pd.read_excel(GOLD_XLSX, sheet_name="Sampling_Metadata")
    validation = annotation.merge(metadata, on="sample_id", how="left", validate="one_to_one")
    validation = validation.rename(
        columns={
            "firm_id": "Firm_ID",
            "year": "Year",
            "mdna_passage": "segment_text",
        }
    )
    full = pd.read_csv(FULL_CONSENSUS_CSV, dtype={"Firm_ID": str})

    for df in [validation, full]:
        df["firm_id_norm"] = df["Firm_ID"].map(normalize_code)
        df["year_norm"] = df["Year"].astype(int)
        df["text_norm"] = df["segment_text"].map(normalize_text)
        df["merge_key"] = df["firm_id_norm"] + "|" + df["year_norm"].astype(str) + "|" + df["text_norm"]

    validation["full_segment_id"] = np.where(
        validation["dictionary_hit"].eq(1),
        validation["original_passage_id"].map(hit_to_full_segment_id),
        "",
    )
    merged = validation.merge(
        full[
            [
                "segment_id",
                "gpt55_label",
                "claude_label",
                "consensus_label",
            ]
        ].rename(columns={"segment_id": "full_segment_id"}),
        on="full_segment_id",
        how="left",
        validate="many_to_one",
    )
    hit_missing = merged["dictionary_hit"].eq(1) & merged["consensus_label"].isna()
    if hit_missing.any():
        raise ValueError(f"Dictionary-hit gold rows not matched to full consensus: {int(hit_missing.sum())}")
    return merged, full


def train_finbert(train_df: pd.DataFrame, eval_texts: list[str]) -> list[int]:
    seed_everything(RANDOM_SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=2,
        ignore_mismatched_sizes=True,
    )

    for param in model.parameters():
        param.requires_grad = False
    for param in model.classifier.parameters():
        param.requires_grad = True
    for param in model.bert.encoder.layer[-1].parameters():
        param.requires_grad = True

    model.to(device)
    labels = train_df["pseudo_binary"].astype(int).tolist()
    texts = train_df["segment_text"].map(normalize_text).tolist()
    dataset = TextDataset(texts, labels, tokenizer)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    class_counts = np.bincount(labels, minlength=2)
    weights = len(labels) / np.maximum(class_counts, 1)
    weights = torch.tensor(weights / weights.mean(), dtype=torch.float32, device=device)
    loss_fn = torch.nn.CrossEntropyLoss(weight=weights)
    optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=LEARNING_RATE)

    model.train()
    for epoch in range(1, EPOCHS + 1):
        total_loss = 0.0
        for batch in loader:
            optimizer.zero_grad(set_to_none=True)
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            y = batch["labels"].to(device)
            logits = model(input_ids=input_ids, attention_mask=attention_mask).logits
            loss = loss_fn(logits, y)
            loss.backward()
            optimizer.step()
            total_loss += float(loss.detach().cpu())
        print(f"epoch={epoch} loss={total_loss / max(len(loader), 1):.4f}")

    model.eval()
    preds: list[int] = []
    with torch.no_grad():
        for start in range(0, len(eval_texts), BATCH_SIZE):
            batch_texts = eval_texts[start : start + BATCH_SIZE]
            enc = tokenizer(
                batch_texts,
                truncation=True,
                padding=True,
                max_length=MAX_LEN,
                return_tensors="pt",
            )
            enc = {k: v.to(device) for k, v in enc.items()}
            logits = model(**enc).logits
            preds.extend(torch.argmax(logits, dim=1).cpu().tolist())
    return preds


def add_method_metrics(rows: list[dict[str, object]], method: str, y_true, y_pred, n_total: int, note: str) -> None:
    m = metrics(list(y_true), list(y_pred))
    rows.append(
        {
            "Method": method,
            "N_total": n_total,
            "Coverage": m["N_eval"] / n_total if n_total else math.nan,
            "N_eval": m["N_eval"],
            "TP": m["TP"],
            "FP": m["FP"],
            "TN": m["TN"],
            "FN": m["FN"],
            "Accuracy": m["Accuracy"],
            "Precision": m["Precision"],
            "Recall": m["Recall"],
            "F1": m["F1"],
            "Note": note,
        }
    )


def main() -> None:
    validation, full = load_frames()
    validation["gold_binary"] = validation["final_label"].map(binary_from_gold)
    validation["dictionary_pred"] = validation["dictionary_hit"].astype(int)

    validation["llm_consensus_pred"] = np.where(
        validation["consensus_label"].eq("substantive_adoption"),
        1,
        np.where(validation["consensus_label"].eq("disagreement") | validation["consensus_label"].isna(), np.nan, 0),
    )
    validation["hybrid_pred"] = np.where(
        validation["llm_consensus_pred"].notna(),
        validation["llm_consensus_pred"],
        validation["dictionary_pred"],
    ).astype(int)

    train = full.loc[
        full["consensus_label"].ne("disagreement")
        & ~full["merge_key"].isin(set(validation.loc[validation["dictionary_hit"].eq(1), "merge_key"]))
    ].copy()
    train["pseudo_binary"] = train["consensus_label"].map(binary_from_consensus)

    eval_frame = validation.loc[validation["gold_binary"].notna()].copy()
    eval_frame["gold_binary"] = eval_frame["gold_binary"].astype(int)
    print(f"training_rows={len(train)} gold_rows={len(validation)} eval_rows={len(eval_frame)}")
    print(train["pseudo_binary"].value_counts().to_string())

    validation["finbert_pred"] = train_finbert(train, validation["segment_text"].map(normalize_text).tolist())
    eval_frame = validation.loc[validation["gold_binary"].notna()].copy()
    eval_frame["gold_binary"] = eval_frame["gold_binary"].astype(int)

    rows: list[dict[str, object]] = []
    n_total = len(eval_frame)
    add_method_metrics(
        rows,
        "Dictionary rule",
        eval_frame["gold_binary"],
        eval_frame["dictionary_pred"],
        n_total,
        "Positive if the passage is a dictionary hit.",
    )
    covered = eval_frame["llm_consensus_pred"].notna()
    add_method_metrics(
        rows,
        "GPT-5.5 / Claude strict consensus",
        eval_frame.loc[covered, "gold_binary"],
        eval_frame.loc[covered, "llm_consensus_pred"].astype(int),
        n_total,
        "Evaluated only where GPT-5.5 and Claude agree; non-hit and disagreement rows are abstentions.",
    )
    add_method_metrics(
        rows,
        "FinBERT fine-tuned on strict consensus",
        eval_frame["gold_binary"],
        eval_frame["finbert_pred"],
        n_total,
        f"Backbone: {MODEL_NAME}; train rows exclude dictionary-hit gold passages.",
    )
    add_method_metrics(
        rows,
        "Hybrid consensus with dictionary fallback",
        eval_frame["gold_binary"],
        eval_frame["hybrid_pred"],
        n_total,
        "Uses strict LLM consensus on covered hit rows; falls back to dictionary rule for non-hit, missing, or disagreement rows.",
    )

    metrics_df = pd.DataFrame(rows)
    display_df = metrics_df.copy()
    for col in ["Coverage", "Accuracy", "Precision", "Recall", "F1"]:
        display_df[col] = display_df[col].map(lambda x: f"{x:.3f}")

    validation_out = validation[
        [
            "sample_id",
            "sample_group",
            "original_passage_id",
            "full_segment_id",
            "Firm_ID",
            "Year",
            "dictionary_hit",
            "original_dictionary_label",
            "matched_terms",
            "final_label",
            "consensus_label",
            "gold_binary",
            "dictionary_pred",
            "llm_consensus_pred",
            "finbert_pred",
            "hybrid_pred",
            "segment_text",
        ]
    ].copy()
    validation_out.to_csv(OUT_PRED, index=False, encoding="utf-8-sig")
    metrics_df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as writer:
        display_df.to_excel(writer, sheet_name="Table_3C", index=False)
        validation_out.to_excel(writer, sheet_name="validation_predictions", index=False)
        train[["segment_id", "Firm_ID", "Year", "dictionary_label", "consensus_label", "pseudo_binary", "segment_text"]].to_excel(
            writer,
            sheet_name="finbert_train_pseudo_labels",
            index=False,
        )

    md = [
        "# Table 3C. SOTA / Hybrid Validation on MD&A Passages\n\n",
        "Gold benchmark: 600 human double-coded MD&A passages from `GenAI_gold_standard_adjudication_draft人工双核验.xlsx`. ",
        "All 600 passages have adjudicated binary final labels and are included in metric denominators.\n\n",
        display_df.to_markdown(index=False),
        "\n\n",
        "Notes: FinBERT is fine-tuned on the full-sample strict GPT-5.5/Claude consensus labels after excluding the dictionary-hit gold passages. ",
        "The strict LLM consensus row reports coverage because non-hit gold passages were not part of the hit-only LLM audit, and GPT/Claude disagreement rows are treated as abstentions. ",
        "The hybrid row uses strict LLM consensus where available and the dictionary rule as fallback for non-hit, missing, or disagreement rows.\n",
    ]
    OUT_MD.write_text("".join(md), encoding="utf-8")

    print(display_df.to_string(index=False))
    print(f"wrote={OUT_XLSX}")
    print(f"wrote={OUT_CSV}")
    print(f"wrote={OUT_MD}")
    print(f"wrote={OUT_PRED}")


if __name__ == "__main__":
    main()
