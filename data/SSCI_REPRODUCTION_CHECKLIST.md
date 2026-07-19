# SSCI Reproduction Checklist

- [ ] Run `python code/recompute_table3c_from_frozen_predictions.py`.
- [ ] Confirm `outputs/recomputed/Table_3C_recomputed_metrics.csv` is created.
- [ ] Run `python code/validate_ssci_sota_package.py`.
- [ ] Confirm every item in `docs/SSCI_QC_REPORT.md` is marked `PASS`.
- [ ] Confirm `MANIFEST.sha256` is present.
- [ ] Use the frozen prediction path for exact submitted-table reproduction.
- [ ] Treat the optional FinBERT live rerun as provenance-only unless model files and dependency versions are fixed.

