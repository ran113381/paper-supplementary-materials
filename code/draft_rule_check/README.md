# Draft-rule check

These scripts check the earlier adjudication drafts of the gold standard. They are released
byte for byte as run, together with their logs.

| Script | Log | What it checks |
|---|---|---|
| `a9_gold_checks.py` | `J29_r5_a9_gold_checks.log` | Item [1]: a rule that labels a passage GenAI-related if and only if it contains one of five dictionary strings reproduces every binary draft on the 122 disagreements (log line 5: `five-term rule == draft on binary drafts: 121/121`), with discrimination controls (the dictionary-hit flag alone, and the rule without each string in turn). Further items: published final label against draft, coder diagnostics, concordant-subset metrics and bounds. |
| `a14_dr_kappa_boot.py` | `J29_r5_a14_dr_kappa_boot.log` | Review-sheet labels against the published final labels (12 passages whose label change in the review sheet was not transferred to the final labels), inter-coder kappa, and the 477-passage concordant subset. |
| `a17_collisions.py` | `J29_r5_a17_collisions.log` | Draft = 1 passages whose only matches are Latin strings embedded in longer words (substring collisions inside company or product names). |

## Inputs and the misnamed file in commit `e41356a`

All three scripts read the original May 2026 adjudication workbook from the repository history
with `git show e41356a:data/Table_3C_SOTA_validation_metrics.csv`. That blob is misnamed: despite
the `.csv` extension it is an Excel workbook (it begins with the ZIP signature `PK`), and the file
now at the same path is a different CSV file. The blob's SHA-256 is

`b0d365b8a19b9a3b8736e9640381f25cbabd536fe56c0c6ee9b865b8dc7c094f`,

the value recorded in `data/MANIFEST.sha256` for the gold-standard workbook. Commit `e41356a` is
part of the public history and is not rewritten. `a9_gold_checks.py` also reads the current
workbook `data/genai_gold_standard_adjudication_workbook.xlsx` and the frozen predictions
`data/Table_3C_validation_predictions.csv`.

## Running

The scripts are released as run, with the absolute path of the authors' local clone of this
repository in the variable `R` near the top of each script. To rerun, set `R` to the root of your
clone (the scripts call `git show`, so it must be a git clone that contains commit `e41356a`).

See `../../CORRECTION_NOTE.md` for the corrections that these checks support.
