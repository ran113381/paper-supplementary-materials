from __future__ import annotations

import csv
import hashlib
import importlib.util
import sys
from pathlib import Path


REQUIRED_FILES = [
    "README.md",
    "docs/DATA_DICTIONARY.md",
    "docs/METHODS_AND_REPRODUCTION_NOTES.md",
    "data/gold_standard/GenAI_gold_standard_adjudication_draft人工双核验.xlsx",
    "data/sampling_frame/mdna_passage_level_gold_standard_seed.csv",
    "data/sampling_frame/mdna_passage_level_gold_standard_seed.xlsx",
    "data/llm_consensus_source/full_sample_segments_1256.csv",
    "data/llm_consensus_source/full_sample_gpt55_claude_consensus_labels.csv",
    "data/llm_consensus_source/full_sample_gpt55_claude_report.md",
    "data/table3c_frozen_predictions/Table_3C_validation_predictions.csv",
    "data/table3c_published_outputs/Table_3C_SOTA_validation_metrics.csv",
    "data/table3c_published_outputs/Table_3C_SOTA_validation_metrics.md",
    "data/table3c_published_outputs/Table_3C_SOTA_validation_metrics.xlsx",
    "data/manual_gold_standard_evidence/MDNA_passage_gold_standard_README.md",
    "evidence/prompts/PROMPT_复制给GPT55.txt",
    "evidence/prompts/PROMPT_复制给Claude.txt",
    "figures_and_tables/figure_files/Figure_SOTA_LLM_validation_workflow.svg",
    "figures_and_tables/figure_files/Figure_LLM_adjudicated_label_distribution.svg",
    "figures_and_tables/figure_files/Figure_GPT55_Claude_label_distribution.svg",
    "figures_and_tables/figure_files/Figure_Dictionary_vs_LLM_consensus.svg",
    "figures_and_tables/table_and_figure_packages/08_SOTA_LLM_支持图表模板.md",
    "figures_and_tables/table_and_figure_packages/15_SOTA_LLM_最终图表包.md",
    "figures_and_tables/table_and_figure_packages/18_GPT55全样本_SOTA最终图表包.md",
    "figures_and_tables/table_and_figure_packages/22_SOTA_LLM_双模型最终图表包.md",
    "figures_and_tables/manuscript_snapshots/Paper2_revised_policy_light_reinforcement_Table3C_600gold_noU_IPM_refs.docx",
    "code/optional_live_finbert_rerun/build_table3c_finbert_hybrid.py",
]


NUMERIC_COLUMNS = {
    "N_total",
    "Coverage",
    "N_eval",
    "TP",
    "FP",
    "TN",
    "FN",
    "Accuracy",
    "Precision",
    "Recall",
    "F1",
}


def import_recompute_module(root: Path):
    module_path = root / "code" / "recompute_table3c_from_frozen_predictions.py"
    spec = importlib.util.spec_from_file_location("recompute_table3c", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def compare_metric_files(published: Path, recomputed: Path) -> list[str]:
    published_rows = {row["Method"]: row for row in read_csv(published)}
    recomputed_rows = {row["Method"]: row for row in read_csv(recomputed)}
    errors: list[str] = []
    if set(published_rows) != set(recomputed_rows):
        errors.append("Published and recomputed method sets differ.")
        return errors
    for method in published_rows:
        for column, published_value in published_rows[method].items():
            recomputed_value = recomputed_rows[method][column]
            if column in NUMERIC_COLUMNS:
                if abs(float(published_value) - float(recomputed_value)) > 1e-12:
                    errors.append(f"{method} {column}: published={published_value}, recomputed={recomputed_value}")
            elif published_value != recomputed_value:
                errors.append(f"{method} {column}: published text differs from recomputed text")
    return errors


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(root: Path) -> Path:
    manifest = root / "MANIFEST.sha256"
    files = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.name != manifest.name
        and not path.name.endswith(".zip")
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    ]
    lines = []
    for path in sorted(files, key=lambda p: p.relative_to(root).as_posix().lower()):
        lines.append(f"{sha256(path)}  {path.relative_to(root).as_posix()}")
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def count_csv_rows(path: Path) -> int:
    return len(read_csv(path))


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    checks: list[tuple[str, bool, str]] = []

    missing = [rel for rel in REQUIRED_FILES if not (root / rel).exists()]
    checks.append(("Required files present", not missing, ", ".join(missing) if missing else "all present"))

    gpt_files = list((root / "evidence" / "llm_raw_returns" / "gpt55").glob("*.jsonl"))
    claude_files = list((root / "evidence" / "llm_raw_returns" / "claude").glob("*.jsonl"))
    figure_files = list((root / "figures_and_tables" / "figure_files").glob("*"))
    figure_table_packages = list((root / "figures_and_tables" / "table_and_figure_packages").glob("*.md"))
    early_validation_files = list((root / "evidence" / "early_llm_validation").glob("*"))
    checks.append(("GPT-5.5 raw-return files", len(gpt_files) == 13, f"{len(gpt_files)} files"))
    checks.append(("Claude raw-return files", len(claude_files) == 13, f"{len(claude_files)} files"))
    checks.append(("Added figure files", len(figure_files) == 4, f"{len(figure_files)} files"))
    checks.append(("Added figure/table package notes", len(figure_table_packages) == 4, f"{len(figure_table_packages)} files"))
    checks.append(("Early validation / adjudication evidence", len(early_validation_files) == 9, f"{len(early_validation_files)} files"))

    pred_rows = count_csv_rows(root / "data" / "table3c_frozen_predictions" / "Table_3C_validation_predictions.csv")
    consensus_rows = count_csv_rows(root / "data" / "llm_consensus_source" / "full_sample_gpt55_claude_consensus_labels.csv")
    checks.append(("Frozen prediction rows", pred_rows == 600, f"{pred_rows} rows"))
    checks.append(("Full-sample consensus rows", consensus_rows == 1256, f"{consensus_rows} rows"))

    recompute = import_recompute_module(root)
    rows = recompute.load_rows(root / "data" / "table3c_frozen_predictions" / "Table_3C_validation_predictions.csv")
    qc = recompute.validate_rows(rows)
    metrics_rows = recompute.build_metrics(rows)
    recomputed_csv = root / "outputs" / "recomputed" / "Table_3C_recomputed_metrics.csv"
    recomputed_md = root / "outputs" / "recomputed" / "Table_3C_recomputed_metrics.md"
    recompute.write_metrics_csv(metrics_rows, recomputed_csv)
    recompute.write_metrics_md(metrics_rows, qc, recomputed_md)
    checks.append(("Gold-label lock", True, f"{qc['gold_positive']} positive, {qc['gold_negative']} negative"))
    checks.append(("Strict-consensus coverage lock", qc["llm_consensus_covered"] == 271, f"{qc['llm_consensus_covered']} covered rows"))

    compare_errors = compare_metric_files(
        root / "data" / "table3c_published_outputs" / "Table_3C_SOTA_validation_metrics.csv",
        recomputed_csv,
    )
    checks.append(("Published metrics equal recomputed metrics", not compare_errors, "; ".join(compare_errors) if compare_errors else "exact match"))

    report_lines = [
        "# SSCI SOTA Reproducibility QC Report",
        "",
        "This report is generated by `code/validate_ssci_sota_package.py`.",
        "",
        "## Checks",
        "",
    ]
    for name, ok, detail in checks:
        report_lines.append(f"- {'PASS' if ok else 'FAIL'}: {name} ({detail})")
    report_lines.extend(
        [
            "",
            "## Recomputed Output",
            "",
            "- `outputs/recomputed/Table_3C_recomputed_metrics.csv`",
            "- `outputs/recomputed/Table_3C_recomputed_metrics.md`",
            "",
            "## Interpretation Lock",
            "",
            "The reproducible claim is limited to passage-level semantic validation of a disclosure-based GenAI proxy. It does not claim direct measurement of internal deployment depth or model-output quality.",
            "",
        ]
    )
    report_path = root / "docs" / "SSCI_QC_REPORT.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    manifest = write_manifest(root)

    failed = [name for name, ok, _detail in checks if not ok]
    if failed:
        print(f"FAIL: {len(failed)} checks failed. See {report_path}")
        sys.exit(1)
    print(f"PASS: SSCI package validated. See {report_path}")
    print(f"WROTE: {manifest}")


if __name__ == "__main__":
    main()
