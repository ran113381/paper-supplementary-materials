# Exhibit Map

Synchronized 2026-07-17 with the major-revision manuscript
("GenAI Disclosure and Short-Term Firm Performance in Buyer–Supplier Dyads:
Evidence from Text-Mined MD&A Signals") — 14 tables and 14 figures.
Every manuscript table is frozen to CSV under `output/tables/`; every
manuscript figure is frozen, exactly as embedded in the revised manuscript,
under `output/figures/manuscript_render/`.

## Tables (manuscript numbering after the 2026-07 revision)

| Manuscript exhibit | Included file |
| --- | --- |
| Table 1 Sample Construction Procedure | `output/tables/table_01_sample_construction_procedure.csv` |
| Table 2 Variable Definition and Calculation | `output/tables/table_02_variable_definition_and_calculation.csv` |
| Table 3 Classification of GenAI Dictionary Keywords | `output/tables/table_03_genai_dictionary_keyword_classification.csv` |
| Table 4 Full-Sample LLM-Assisted Semantic Audit | `output/tables/table_04_full_sample_llm_semantic_audit.csv` |
| Table 5 Human-Annotated Gold-Standard Validation | `output/tables/table_05_gold_standard_validation.csv` |
| Table 6 SOTA and Hybrid Benchmark Validation | `output/tables/table_06_sota_hybrid_benchmark.csv` |
| Table 7 Descriptive Statistics of Key Variables | `output/tables/table_07_descriptive_statistics.csv` |
| Table 8 The Correlation Matrix | `output/tables/table_08_correlation_matrix.csv` |
| Table 9 Baseline Regression Results | `output/tables/table_09_baseline_regression_results.csv` |
| Table 10 Summary of Robustness Tests (incl. the pre-2022 exclusion rows) | `output/tables/table_10_robustness_summary.csv` |
| Table 11 Robustness to Dyadic-Dependence Corrections | `output/tables/table_11_dyadic_dependence_corrections.csv` |
| Table 12 Candidate Operational Channel: Inventory Turnover | `output/tables/table_12_inventory_turnover_channel.csv` |
| Table 13 Extension of Baseline Estimates to Fiscal Year 2025 | `output/tables/table_13_fy2025_extension.csv` |
| Table 14 Heterogeneity Analysis | `output/tables/table_14_heterogeneity_analysis.csv` |
| Full bilingual dictionary (103 terms) | `output/tables/appendix_full_dictionary.csv` + `data/public/04_genai_dictionary.xlsx` |

## Figures (manuscript numbering after the 2026-07 revision)

Authoritative copies extracted from the revised manuscript itself:
`output/figures/manuscript_render/figure_01.png` … `figure_14.png`,
numbered exactly as in the manuscript:

| # | Manuscript exhibit |
| --- | --- |
| figure_01 | Time evolution of GenAI disclosure rates (2015–2024) |
| figure_02 | Theoretical Framework and Research Propositions |
| figure_03 | Full-Sample LLM-Assisted Semantic Audit |
| figure_04 | Dictionary Labels versus Strict LLM Consensus |
| figure_05 | ROA Distribution by GenAI Disclosure Status |
| figure_06 | R&D-Intensity Moderation Pattern |
| figure_07 | Power Pressure Moderation Pattern |
| figure_08 | Placebo Test: Random-Permutation Coefficients |
| figure_09 | Staggered DiD Event-Study Estimates |
| figure_10 | Covariate Balance before/after PSM |
| figure_11 | Candidate-Channel Path of Inventory Turnover |
| figure_12 | SHAP-based Feature Importance |
| figure_13 | SHAP Swarm Plot (GenAI adopter subsample) |
| figure_14 | Heterogeneity Forest Plot |

Legacy exports under `output/figures/figure_01_*.png` … `figure_09_*.png`
predate the revision renumbering and are retained for provenance only; the
`manuscript_render/` set above is authoritative.

## Code Assets (added 2026-07-15; FY2025 clean-text script added 2026-07-16)

They read licensed CSMAR/CNRDS-derived panels that are not included in this
repository (paths require local adjustment); see `code/analysis/README.md`.

| Asset | Role |
| --- | --- |
| `code/analysis/01_build_2025_dyad_pairs.py` | FY2025 supplier-dyad construction (original matching logic, fresh CSMAR files) |
| `code/analysis/02_build_2025_firm_year_panel.py` | FY2025 firm-year financial panel (original formulas/field codes) |
| `code/analysis/03_build_2025_variable_base.py` | FY2025 variable construction via the original `construct_variable_base()` |
| `code/analysis/04_score_2025_genai.py` | FY2025 GenAI disclosure scoring with the paper's own dictionary |
| `code/analysis/05_concat_and_rebuild.py` | 2015-2025 concatenation and winsorized regression packages (frozen bounds) |
| `code/analysis/06_verify_2024_reproduction.py` | Exact-reproduction gate against the published 2015-2024 results |
| `code/analysis/07_fy2025_cleantext_extension.py` | FY2025 clean-text filter + the four Table 13 estimates (verified end-to-end) |
| `code/analysis/common.py`, `battery_ext.py` | Shared loaders, construct definitions, FE/cluster estimation helpers |
| `code/analysis/01_main_grid.py` | Baseline diagnostic grid (clustering, collapsing, weighting, lags, firm FE, MDE) |
| `code/analysis/03_cellB_handroll_crosscheck.py`, `05_cellB_final.py` | Two-way (firm x year) cluster-robust variance, hand-rolled CGM cross-check and final run |
| `code/analysis/06_cellC_fix.py` | Corrected firm-year collapse specification |
| `code/analysis/run_full_battery.py` | Construct-validity battery for the Power_Pressure moderator (8 operationalizations) |
| `code/analysis/run_decomposition.py` | Component-concentration decomposition by year |
| `code/analysis/run_bonus_bootstrap.py` | Year-dimension wild-cluster bootstrap stress test (pyfixest) |
| `code/extract_docx_exhibits.py` | Packaging utility for frozen exhibits |
| `data/build_fp_rate_tables.py` | False-positive rates by keyword category × year (built from package-internal data) |
| `data/recompute_table3c_from_frozen_predictions.py` | Deterministic Table 3C recomputation from frozen row-level predictions |
| `data/validate_ssci_sota_package.py` | QC/validation script for the Table 3C evidence package (writes the QC report and SHA-256 manifest) |
| `data/build_table3c_finbert_hybrid.py` | Optional live FinBERT fine-tuning rerun (provenance only; requires torch/transformers) |
