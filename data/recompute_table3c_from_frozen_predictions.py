from __future__ import annotations

import argparse
import csv
from pathlib import Path


METHODS = [
    (
        "Dictionary rule",
        "dictionary_pred",
        False,
        "Positive if the passage is a dictionary hit.",
    ),
    (
        "GPT-5.5 / Claude strict consensus",
        "llm_consensus_pred",
        True,
        "Evaluated only where GPT-5.5 and Claude agree; non-hit and disagreement rows are abstentions.",
    ),
    (
        "FinBERT fine-tuned on strict consensus",
        "finbert_pred",
        False,
        "Backbone: yiyanghkust/finbert-tone-chinese; train rows exclude dictionary-hit gold passages.",
    ),
    (
        "Hybrid consensus with dictionary fallback",
        "hybrid_pred",
        False,
        "Uses strict LLM consensus on covered hit rows; falls back to dictionary rule for non-hit, missing, or disagreement rows.",
    ),
]


EXPECTED_COUNTS = {
    "Dictionary rule": {"N_eval": 600, "TP": 216, "FP": 84, "TN": 300, "FN": 0},
    "GPT-5.5 / Claude strict consensus": {"N_eval": 271, "TP": 121, "FP": 0, "TN": 82, "FN": 68},
    "FinBERT fine-tuned on strict consensus": {"N_eval": 600, "TP": 151, "FP": 83, "TN": 301, "FN": 65},
    "Hybrid consensus with dictionary fallback": {"N_eval": 600, "TP": 148, "FP": 2, "TN": 382, "FN": 68},
}


def parse_binary(value: object, *, allow_blank: bool = False) -> int | None:
    text = "" if value is None else str(value).strip()
    if allow_blank and text == "":
        return None
    if text in {"1", "1.0"}:
        return 1
    if text in {"0", "0.0"}:
        return 0
    raise ValueError(f"Expected binary value, got {value!r}")


def compute_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float | int]:
    tp = fp = tn = fn = 0
    for gold, pred in zip(y_true, y_pred):
        if gold == 1 and pred == 1:
            tp += 1
        elif gold == 0 and pred == 1:
            fp += 1
        elif gold == 0 and pred == 0:
            tn += 1
        elif gold == 1 and pred == 0:
            fn += 1
    n_eval = tp + fp + tn + fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / n_eval if n_eval else 0.0
    return {
        "N_eval": n_eval,
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
    }


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"No rows found in {path}")
    return rows


def validate_rows(rows: list[dict[str, str]]) -> dict[str, object]:
    sample_ids = [row["sample_id"] for row in rows]
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("sample_id is not unique in frozen predictions.")
    if len(rows) != 600:
        raise ValueError(f"Expected 600 validation rows, got {len(rows)}.")

    gold_values = [parse_binary(row["gold_binary"]) for row in rows]
    gold_ones = sum(1 for value in gold_values if value == 1)
    gold_zeros = sum(1 for value in gold_values if value == 0)
    if (gold_ones, gold_zeros) != (216, 384):
        raise ValueError(f"Expected gold counts 216/384, got {gold_ones}/{gold_zeros}.")

    final_labels = {str(row.get("final_label", "")).strip() for row in rows}
    if final_labels - {"0", "1", "0.0", "1.0"}:
        raise ValueError(f"Unexpected final_label values: {sorted(final_labels)}")

    llm_covered = sum(1 for row in rows if str(row.get("llm_consensus_pred", "")).strip())
    if llm_covered != 271:
        raise ValueError(f"Expected 271 strict-consensus covered rows, got {llm_covered}.")

    return {
        "rows": len(rows),
        "sample_id_unique": True,
        "gold_positive": gold_ones,
        "gold_negative": gold_zeros,
        "llm_consensus_covered": llm_covered,
    }


def build_metrics(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    n_total = len(rows)
    output_rows: list[dict[str, object]] = []
    for method, column, allow_abstain, note in METHODS:
        y_true: list[int] = []
        y_pred: list[int] = []
        for row in rows:
            pred = parse_binary(row[column], allow_blank=allow_abstain)
            if pred is None:
                continue
            y_true.append(parse_binary(row["gold_binary"]))
            y_pred.append(pred)
        metrics = compute_metrics(y_true, y_pred)
        expected = EXPECTED_COUNTS[method]
        mismatches = [
            key
            for key, expected_value in expected.items()
            if metrics[key] != expected_value
        ]
        if mismatches:
            detail = ", ".join(f"{key}: {metrics[key]} != {expected[key]}" for key in mismatches)
            raise ValueError(f"{method} does not match expected SSCI-locked counts: {detail}")
        output_rows.append(
            {
                "Method": method,
                "N_total": n_total,
                "Coverage": metrics["N_eval"] / n_total if n_total else 0.0,
                "N_eval": metrics["N_eval"],
                "TP": metrics["TP"],
                "FP": metrics["FP"],
                "TN": metrics["TN"],
                "FN": metrics["FN"],
                "Accuracy": metrics["Accuracy"],
                "Precision": metrics["Precision"],
                "Recall": metrics["Recall"],
                "F1": metrics["F1"],
                "Note": note,
            }
        )
    return output_rows


def write_metrics_csv(rows: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict[str, object]]) -> str:
    headers = list(rows[0].keys())
    widths = {header: len(header) for header in headers}
    rendered_rows: list[dict[str, str]] = []
    for row in rows:
        rendered: dict[str, str] = {}
        for header in headers:
            value = row[header]
            if isinstance(value, float):
                text = f"{value:.3f}"
            else:
                text = str(value)
            rendered[header] = text
            widths[header] = max(widths[header], len(text))
        rendered_rows.append(rendered)

    lines = []
    lines.append("| " + " | ".join(header.ljust(widths[header]) for header in headers) + " |")
    lines.append("| " + " | ".join("-" * widths[header] for header in headers) + " |")
    for row in rendered_rows:
        lines.append("| " + " | ".join(row[header].ljust(widths[header]) for header in headers) + " |")
    return "\n".join(lines)


def write_metrics_md(rows: list[dict[str, object]], qc: dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(
        [
            "# Recomputed Table 3C Metrics",
            "",
            "This file is generated from `data/table3c_frozen_predictions/Table_3C_validation_predictions.csv` using only Python standard-library code.",
            "",
            f"- Validation rows: {qc['rows']}",
            f"- Gold positives / negatives: {qc['gold_positive']} / {qc['gold_negative']}",
            f"- Strict LLM-consensus covered rows: {qc['llm_consensus_covered']}",
            "",
            markdown_table(rows),
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Recompute SSCI-locked Table 3C metrics from frozen predictions.")
    parser.add_argument(
        "--package-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the root of SSCI_repro_package_SOTA_20260514.",
    )
    args = parser.parse_args()

    root = args.package_root.resolve()
    input_csv = root / "data" / "table3c_frozen_predictions" / "Table_3C_validation_predictions.csv"
    out_csv = root / "outputs" / "recomputed" / "Table_3C_recomputed_metrics.csv"
    out_md = root / "outputs" / "recomputed" / "Table_3C_recomputed_metrics.md"

    rows = load_rows(input_csv)
    qc = validate_rows(rows)
    metrics_rows = build_metrics(rows)
    write_metrics_csv(metrics_rows, out_csv)
    write_metrics_md(metrics_rows, qc, out_md)

    print(f"PASS: recomputed Table 3C from {len(rows)} frozen prediction rows")
    print(f"WROTE: {out_csv}")
    print(f"WROTE: {out_md}")


if __name__ == "__main__":
    main()
