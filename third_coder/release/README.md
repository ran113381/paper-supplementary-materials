# Post-coding release (blind third-coder re-adjudication)

This folder holds the materials released after coding under Section 9.3 of the deposited protocol
(`../protocol_third_coder_v2.7.md`; GitHub Release third-coder-protocol-v2.7, commit fd6616d). The
SHA-256 of every key, seed and coding sheet was deposited before coding in
`../selection_manifest.json`; the released keys, seeds, selection rules and register are
byte-identical to the deposited hashes. `HASHES.md` lists the SHA-256 of every file here.

| Path | Content |
|---|---|
| `keys/` | Sealed keys for the calibration, E1, non-concordant and practice passages, and the replacement keys prepared under protocol Section 10.5 (not used). |
| `seeds/` | The selection, replacement and analysis seed files. |
| `selection/` | `J16_selection_rules.md` (the selection rules, deposited by hash only before coding because they contain the seeds) and `selection_register.csv`. |
| `labels/` | All of the third coder's labels, confidence ratings, reasons and leans, from the run on the corrected sheet: non-concordant passages, E1 passages (labeled 1 and labeled U), calibration disagreements, the final labels and the E1 summary. The calibration labels themselves are in the returned sheets. |
| `sheets/` | The four coding sheets, each marked by its role: `coder3_first_returned_sheet.xlsx` (first returned sheet, incomplete: four leans missing), `author_entered_copy_1.xlsx` and `author_entered_copy_2.xlsx` (copies into which the administrator, one of the authors, entered the missing leans; not returned by the third coder), and `coder3_corrected_sheet.xlsx` (the third coder's corrected sheet, used for the reported results). They are metadata-cleaned copies with every cell unchanged; `HASHES.md` gives the original and the released SHA-256 of each. `sheet_comparison.txt` lists every cell in which the four sheets differ. |
| `runs/run1_first_returned_sheet/` | The run on the first returned sheet: qualification record and its hash log, stage logs (the second stage stopped at the first unclear label without a lean), the model-comparison control log, and a comparison of the first sheet with author-entered copy 2 (`resubmit_diff.txt`, from `resubmit_diff_sheets.py`). |
| `runs/run2_author_entered_copy_2/` | The run on author-entered copy 2, kept as a process record: qualification record, stage logs, label outputs and model-comparison logs. |
| `runs/run3_corrected_sheet/` | The rerun on the corrected sheet, whose results are reported: qualification record, stage logs and model-comparison logs; `J23_compare.log` (from `J23_compare.py`) compares its outputs with those of run 2. The label outputs of this run are in `labels/`. |

The wrapper that computes the primary metrics and the F1 intervals, the second script for the
477 concordant passages, and their logs are in `../scripts/` and `../logs/`. The departures from
the protocol, with the time of each step and the file hashes, are recorded in
`../DEPARTURE_RECORD.md`.

The question-and-answer log is not yet in this folder. [QA-LOG: to be added]

The scripts and logs are released as run; they contain absolute paths of the authors' local
folders, which must be adjusted to rerun them.
