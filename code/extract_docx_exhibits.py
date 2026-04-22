from __future__ import annotations

import argparse
import csv
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from docx.oxml.text.paragraph import CT_P
from docx.text.paragraph import Paragraph
from lxml import etree


TABLE_SPECS = [
    ("table_01_sample_construction_procedure.csv", "Table 1 Sample Construction Procedure"),
    ("table_02_variable_definition_and_calculation.csv", "Table 2 Variable Definition and Calculation"),
    ("table_03_genai_dictionary_keyword_classification.csv", "Table 3 Classification of GenAI Dictionary Keywords"),
    ("table_04_descriptive_statistics_of_key_variables.csv", "Table 4 Descriptive Statistics of Key Variables"),
    ("table_05_baseline_regression_results.csv", "Table 5 Baseline Regression Results"),
    ("table_06_summary_of_robustness_tests.csv", "Table 6 Summary of Robustness Tests"),
    ("table_07_candidate_channel_inventory_turnover.csv", "Table 7 Candidate Channel Test: Inventory Turnover"),
    ("table_08_heterogeneity_analysis.csv", "Table 8 Heterogeneity Analysis"),
    ("appendix_a2_correlation_matrix.csv", "Appendix A2 Correlation Matrix"),
    ("appendix_full_dictionary.csv", "Full Dictionary Appendix"),
]

FIGURE_SPECS = [
    ("figure_01_genai_adoption_rate", "Figure 1 Time evolution of GenAI adoption rate in Chinese listed companies (2015-2024)"),
    ("figure_02_theoretical_framework", "Figure 2 Theoretical Framework and Research Propositions"),
    ("figure_03_rd_moderation", "Figure 3 Moderating Effect of R&D Intensity on the Negative Performance Effect of GenAI"),
    ("figure_04_power_pressure_moderation", "Figure 4 Moderating Effect of AI-Induced Supply Chain Power Pressure"),
    ("figure_05_placebo_distribution", "Figure 5 Placebo Test: Distribution of Random-Permutation Coefficients"),
    ("figure_06_event_study", "Figure 6  Staggered DiD Event-Study Estimates"),
    ("figure_07_psm_balance", "Figure 7  Covariate Balance before and after Propensity Score Matching"),
    ("figure_08_inventory_turnover_path", "Figure 8 Candidate-Channel Path of Inventory Turnover"),
    ("figure_09_heterogeneity_forest_plot", "Figure 9 Heterogeneity Analysis: Forest Plot of Subsample Coefficients"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract frozen tables and figures from the authority manuscript docx.")
    parser.add_argument("--docx", required=True, help="Path to the authority manuscript .docx")
    parser.add_argument("--table-dir", default="output/tables", help="Directory for exported table CSV files")
    parser.add_argument("--figure-dir", default="output/figures", help="Directory for exported figure image files")
    return parser.parse_args()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)


def export_tables(doc: Document, out_dir: Path) -> None:
    if len(doc.tables) != len(TABLE_SPECS):
        raise RuntimeError(f"Expected {len(TABLE_SPECS)} tables, found {len(doc.tables)}")

    index_rows = [["file_name", "authority_label", "row_count", "column_count"]]
    for table, (filename, label) in zip(doc.tables, TABLE_SPECS):
        rows = []
        for row in table.rows:
            rows.append([cell.text.strip().replace("\n", " / ") for cell in row.cells])
        write_csv(out_dir / filename, rows)
        index_rows.append([filename, label, str(len(rows)), str(len(rows[0]))])

    write_csv(out_dir / "TABLE_INDEX.csv", index_rows)


def read_body_image_rel_ids(docx_path: Path) -> tuple[list[str], dict[str, str]]:
    ns = {
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    }
    rel_ns = {
        "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    }

    with ZipFile(docx_path) as zf:
        document_xml = etree.fromstring(zf.read("word/document.xml"))
        rels_xml = etree.fromstring(zf.read("word/_rels/document.xml.rels"))
        rel_ids = [
            blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
            for blip in document_xml.xpath(".//a:blip", namespaces=ns)
        ]
        rel_map = {
            rel.get("Id"): rel.get("Target")
            for rel in rels_xml.xpath(".//rel:Relationship", namespaces=rel_ns)
        }
    return rel_ids, rel_map


def figure_captions(doc: Document) -> list[str]:
    captions: list[str] = []
    for child in doc.element.body.iterchildren():
        if isinstance(child, CT_P):
            paragraph = Paragraph(child, doc)
            text = paragraph.text.strip()
            if text.startswith("Figure "):
                captions.append(text)
    return captions


def export_figures(doc: Document, docx_path: Path, out_dir: Path) -> None:
    captions = figure_captions(doc)
    expected_captions = [caption for _, caption in FIGURE_SPECS]
    if captions != expected_captions:
        raise RuntimeError("Figure caption order does not match the expected manuscript structure")

    rel_ids, rel_map = read_body_image_rel_ids(docx_path)
    if len(rel_ids) != len(FIGURE_SPECS):
        raise RuntimeError(f"Expected {len(FIGURE_SPECS)} embedded figures, found {len(rel_ids)}")

    index_rows = [["file_name", "authority_caption", "source_media_name"]]
    with ZipFile(docx_path) as zf:
        for rel_id, (stem, caption) in zip(rel_ids, FIGURE_SPECS):
            target = rel_map[rel_id]
            source_name = Path(target).name
            ext = Path(source_name).suffix.lower()
            out_name = f"{stem}{ext}"
            with zf.open(f"word/{target}") as src, (out_dir / out_name).open("wb") as dst:
                dst.write(src.read())
            index_rows.append([out_name, caption, source_name])

    write_csv(out_dir / "FIGURE_INDEX.csv", index_rows)


def main() -> None:
    args = parse_args()
    docx_path = Path(args.docx).expanduser().resolve()
    table_dir = Path(args.table_dir)
    figure_dir = Path(args.figure_dir)

    if not docx_path.exists():
        raise FileNotFoundError(f"Manuscript not found: {docx_path}")

    ensure_dir(table_dir)
    ensure_dir(figure_dir)

    doc = Document(str(docx_path))
    export_tables(doc, table_dir)
    export_figures(doc, docx_path, figure_dir)

    print(f"Exported tables to: {table_dir}")
    print(f"Exported figures to: {figure_dir}")


if __name__ == "__main__":
    main()
