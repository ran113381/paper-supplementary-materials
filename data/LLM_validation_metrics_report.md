# LLM Validation Metrics Report

## Binary Mapping

- Dictionary positive: `substantive` or `strategic`.
- LLM positive: `substantive_adoption`.
- `generic_or_background` and `unclear` are treated as non-substantive for the conservative binary comparison.

## Summary

- N = 140
- TP = 41
- FP = 39
- TN = 29
- FN = 31
- Accuracy / agreement = 0.500
- Precision = 0.512
- Recall = 0.569
- F1 = 0.539

## LLM Label Distribution

- substantive_adoption: 72
- generic_or_background: 57
- unclear: 11

## Cross-tabulation

| Dictionary label | substantive_adoption | generic_or_background | unclear |
|---|---:|---:|---:|
| generic | 31 | 25 | 4 |
| strategic | 8 | 10 | 2 |
| substantive | 33 | 22 | 5 |
