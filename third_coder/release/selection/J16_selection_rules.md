# J16 Selection Rules: Practice, Calibration, E1 and Coding-Sheet Construction

Executable specification for the selection script of the protocol `J16_third_coder_protocol_EN.md`. The runner implements it as written; no step below requires a judgment call. If any assertion fails, or any situation arises that this document does not cover, the script stops with a non-zero exit code, and the runner reports to the main session without patching around it.

This version supersedes `J15_selection_rules.md`. The practice-feedback script and its input file are withdrawn: the practice answer sheet `practice_answers.xlsx` takes the place of the input file, the script folder holds the two analysis scripts only, and B18, C13 and C15 are deleted (their numbers are not reused). All other step, assertion and control numbers are kept.

---

## 0. Handling

- This document contains the random seeds (Section 5). Before coding it is deposited **by SHA-256 only**, and it is released after coding (protocol 9.1, 9.3). It is never given to Coder 3.
- The script reads the seeds from seed files, not from this document, so that the scripts can be deposited in full before coding while the seeds are deposited by hash.
- Python: `D:\python.exe -I`. Libraries: `openpyxl`, `numpy`, standard library. No `try/except` that swallows an error.
- The script prints its pinned values between `=== RESULTS ===` and `=== END RESULTS ===` (Section 10).
- The script never prints passage text, and never prints the sample_id list of the non-concordant key or of the E1 key.

---

## 1. Input (read-only)

| Item | Value |
|---|---|
| Workbook | `E:\paper2  daxiu\73ae4696cf54747044a03a936c4bb958_744934475e1139b8c27898b82ae5bbf0_8\paper2_github_replication\data\genai_gold_standard_adjudication_workbook.xlsx` (two spaces after `paper2`) |
| Expected SHA-256 | `aa072750c0a1ae9ac68dece24f060ef2c8e1d1bfb7a153244f9d69791620b0a0` |
| Open mode | `openpyxl.load_workbook(path, read_only=True, data_only=True)`; the file is never opened for writing |
| Sheet `Annotation_Blind` | columns used: `sample_id`, `mdna_passage`, `coder1_label`, `coder2_label`, `coder1_confidence`, `coder2_confidence` |
| Sheet `Sampling_Metadata` | columns used: `sample_id`, `sample_group` |
| Sheet `Codebook` | rows 2 to 11, columns A and B (codebook export, step S7) |

Columns are located by header name. If a named header is missing, the script prints the sheet's header list and stops; it does not guess.

---

## 2. Outputs

Output directory: `E:\論文投稿  送審\paper2\R3_work\third_coder\` (two spaces after `論文投稿`). The script creates the directory and the sub-folders below and writes nothing anywhere else. If the directory already holds any output file, the script stops rather than overwrite it.

CSV files are written as UTF-8 with BOM (`utf-8-sig`). Worksheet names are ASCII.

### 2.1 `to_coder\` (given to Coder 3 after the Release)

| File | Sheet | Columns, in this order (exact) | Rows |
|---|---|---|---|
| `codebook_for_coder.xlsx` | `Codebook` | `item`, `text` | 11 (title row + CB01 to CB10) |
| `practice_sheet.xlsx` | `Practice` | `passage_id`, `passage_text`, `label`, `confidence`, `reason`, `lean` | 20 |
| `practice_answers.xlsx` | `Answers` | `passage_id`, `feedback_label`, `codebook_text` | 20 |
| `coding_sheet.xlsx` | `Coding` | `passage_id`, `passage_text`, `label`, `confidence`, `reason`, `lean` | 437 |

### 2.2 `sealed\` (never given to Coder 3; deposited by hash)

| File | Columns, in this order (exact) | Rows |
|---|---|---|
| `key_practice.csv` | `passage_id`, `sample_id`, `cell`, `reference_label`, `codebook_row`, `codebook_text` | 20 |
| `key_calibration.csv` | `passage_id`, `sample_id`, `cell`, `reference_label`, `nonhigh`, `e1_layer` | 100 |
| `key_nonconcordant.csv` | `passage_id`, `sample_id` | 123 |
| `key_e1.csv` | `passage_id`, `sample_id`, `stratum`, `reference_label` | 214 |
| `selection_register.csv` | `sample_id`, `role`, `cell`, `nonhigh`, `dup_ineligible`, `e1_layer` | 600 |

`role` takes exactly one of: `nonconcordant`, `calibration`, `practice`, `e1`, `unused`. `e1_layer` is `True` for every concordant passage in stratum `NM` or `RND` (Section 3), whatever its role.

### 2.3 `sealed\replacement\` (used only under protocol 10.5; deposited by hash)

| File | Columns | Rows |
|---|---|---|
| `coding_sheet_replacement.xlsx` (sheet `Coding`) | same six columns as `coding_sheet.xlsx` | 437 |
| `key_calibration_replacement.csv` | as `key_calibration.csv` | 100 |
| `key_nonconcordant_replacement.csv` | as `key_nonconcordant.csv` | 123 |
| `key_e1_replacement.csv` | as `key_e1.csv` | 214 |

A replacement coder receives the same `codebook_for_coder.xlsx`, `practice_sheet.xlsx` and `practice_answers.xlsx` as Coder 3, and `coding_sheet_replacement.xlsx` in place of `coding_sheet.xlsx`.

### 2.4 `manifest\`

| File | Content |
|---|---|
| `selection_manifest.json` | SHA-256 of the input workbook, of each seed file, of every output file, of `J16_selection_rules.md`, of the selection script itself, of the analysis script and of `q7_construct_rescore.py` (Section 2.6); canonical content hash of every xlsx (Section 7.4); per-cell counts of every set; E1 counts by stratum and role; shortfall lines; versions of Python, numpy and openpyxl; run start time |

### 2.5 Seed files (written by the runner by hand before the run, outside the script)

`sealed\seed_selection.txt`, `sealed\seed_replacement.txt` and `sealed\seed_analysis.txt`, each holding one integer and a trailing newline (values in Section 5). The script reads the first two and hashes all three; it stops if any is missing or does not parse as an integer. `seed_analysis.txt` is used only by the analysis script (protocol 6.5, 8.2).

### 2.6 Script folder (prepared before the run, outside the script)

`E:\論文投稿  送審\paper2\R3_work\third_coder_scripts\` (two spaces after `論文投稿`) holds, before the selection script is run, the two scripts that are deposited in full with it (protocol 9.1): `analysis_third_coder.py` (the analysis script, Section 11, step 4) and `q7_construct_rescore.py` (protocol 8.5(h)). The analysis script and `q7_construct_rescore.py` are therefore written before the coding sheet is generated, and their SHA-256 is recorded in the selection manifest (Section 2.4). The selection script reads these two files only to hash them; it never runs, imports or modifies them. If either is missing or empty, the script stops (A10).

---

## 3. Definitions

- **Label normalization:** `norm(v) = str(v).strip().upper()`. `coder2_label` is stored as an integer and `coder1_label` as a string; after normalization both take values in `{"0", "1", "U"}`. Any other value → stop.
- **Confidence normalization:** `str(v).strip()`. Allowed values: `High`, `Medium`, `Low`. Any other value → stop.
- **Concordant:** `norm(c1) == norm(c2)` and `norm(c1) in {"0", "1"}`. Reference label = `int(norm(c1))`.
- **Non-concordant:** every passage that is not concordant (this includes `U/U`).
- **Stratum** (from `Sampling_Metadata.sample_group`; any other value → stop):
  - `dictionary_hit_random` → `HIT`
  - `dictionary_non_hit_near_miss` → `NM`
  - `dictionary_non_hit_random` → `RND`
- **Cell** (concordant passages only): `HIT-1`, `HIT-0`, `NM-0`, `RND-0`. A concordant passage in `NM` or `RND` with reference label 1 has no cell → stop ("design assumption violated: concordant positive in non-matched stratum").
- **nonhigh:** `True` if `coder1_confidence != "High"` or `coder2_confidence != "High"`; otherwise `False` ("both-High").
- **dup_ineligible:** among concordant passages, group by exact passage text (byte-for-byte string equality). In every group of size ≥ 2, every passage except the one with the lowest `sample_id` (string order) is ineligible. A concordant passage whose text equals the text of any non-concordant passage is also ineligible. Ineligible passages can never be drawn for calibration or practice; their role is `unused`.
- **e1_layer:** concordant and stratum in {`NM`, `RND`} (equivalently, cell `NM-0` or `RND-0`).
- **Eligible pool of a cell:** concordant, in that cell, not `dup_ineligible`, not yet drawn in an earlier step.
- **nh_remaining** (used in step S2): the eligible pool of the cell with `nonhigh == True`, excluding S1 draws.

---

## 4. Pre-draw assertions (in this order)

- **A1** The workbook SHA-256 equals the expected value in Section 1.
- **A2** `Annotation_Blind` and `Sampling_Metadata` each have 600 data rows. Their `sample_id` columns are identical in content and order, unique, and every value matches `^GS_\d{4}$`.
- **A3** Number of concordant passages = 477; number of non-concordant passages = 123; total = 600.
- **A4** `GS_0438` is non-concordant, and both its normalized labels equal `"U"`.
- **A5** No concordant passage has stratum `NM` or `RND` with reference label 1 (see "Cell" in Section 3).
- **A6** In S1 and S2, every eligible pool is at least as large as the quota drawn from it (Section 6), checked immediately before each draw.
- **A7** Every passage text is a non-empty `str` of length ≤ 32,767, the Excel cell limit.
- **A8** The number of `e1_layer` passages = 244.
- **A9** No `e1_layer` passage is `dup_ineligible` (protocol 6.4: the E1 layer must be covered in full).
- **A10** The script folder (Section 2.6) exists and holds `analysis_third_coder.py` and `q7_construct_rescore.py`, each a non-empty file. This is checked before any output file is written.

Pre-check against the workbook (read-only pool arithmetic, no draw): A8 and A9 hold, and every S1 and S2 pool covers its quota, so no `SHORTFALL` line is expected. These are expectations, not substitutes for the assertions.

---

## 5. Seeds and random-number generation

| Seed file | Value | Used for |
|---|---|---|
| `seed_selection.txt` | `20261015` | steps S1, S2, S4 and S6, in that order, from a single generator |
| `seed_replacement.txt` | `20261016` | step S5 only, from a separate generator |
| `seed_analysis.txt` | `20261017` | the analysis script only (bootstrap resamples); not read by the selection script |

Generator: `rng = numpy.random.default_rng(seed)`. Each draw is made by this one function:

```
def draw(pool_ids, k, rng):
    pool = sorted(pool_ids)              # sample_id string order
    assert k <= len(pool)                # A6
    perm = rng.permutation(len(pool))    # called even when k == 0 or k == len(pool)
    return [pool[i] for i in perm[:k]]
```

The calls are made exactly in the order of Section 6. Changing that order changes every downstream draw and counts as a deviation. Step S3 makes no random call.

---

## 6. Draw procedure

Targets (protocol 6.2 and 5.2):

| Cell | Calibration total | Non-High target | Practice (both-High) |
|---|---|---|---|
| HIT-1 | 40 | 12 | 8 |
| HIT-0 | 30 | 20 | 12 |
| NM-0 | 20 | 12 | 0 |
| RND-0 | 10 | 6 | 0 |
| Total | 100 | 50 | 20 |

**S1 Calibration.** For each cell in the order HIT-1, HIT-0, NM-0, RND-0:
1. `nh` = eligible pool with `nonhigh == True`; `hh` = eligible pool with `nonhigh == False`.
2. `k_nh = min(nonhigh_target, len(nh))`; `A = draw(nh, k_nh, rng)`.
3. `k_hh = calibration_total − k_nh`; `B = draw(hh, k_hh, rng)` (stop if `len(hh) < k_hh`).
4. If `k_nh < nonhigh_target`, append the line `SHORTFALL S1 <cell> nonhigh <k_nh>/<target>` to the manifest. This is logged, not a stop.
5. Mark `A ∪ B` as role `calibration`.

**S2 Practice.** Cells NM-0 and RND-0 have practice quota 0 and no draw is made for them (`draw` is not called for these cells), so that the whole E1 layer is labeled blind on the coding sheet (protocol 5.2, 6.3). For each cell in the order HIT-1, HIT-0:
1. `hh` = eligible both-High pool (excluding S1 draws).
2. If `len(hh) ≥ practice_quota`: `P = draw(hh, practice_quota, rng)`.
3. Otherwise: `P = draw(hh, len(hh), rng) + draw(nh_remaining, practice_quota − len(hh), rng)`, logging `SHORTFALL S2 <cell> bothhigh <len(hh)>/<quota>`. Stop if the non-High remainder is also too small.
4. Mark `P` as role `practice`.

**S3 E1 assembly (no random call).**
1. `e1_set` = every `e1_layer` passage whose role is not yet assigned (that is, neither `calibration` nor `practice`).
2. Assert `len(e1_set) == 214`, `len(e1_layer ∩ calibration) == 30` and `len(e1_layer ∩ practice) == 0`.
3. Mark `e1_set` as role `e1`.

**S4 Coding sheet.**
1. `rows = sorted(nonconcordant ∪ calibration ∪ e1_set)`, 437 sample_ids.
2. `perm = rng.permutation(437)`; `ordered = [rows[i] for i in perm]`.
3. `passage_id` of position `j` (0-based) = `"A" + f"{j+1:03d}"` (A001 to A437).

**S5 Replacement coding sheet** (sealed; protocol 10.5). `rng_r = default_rng(seed)` with the seed read from `seed_replacement.txt`; the same `rows` as S4; `perm = rng_r.permutation(437)`; IDs `"R" + f"{j+1:03d}"` (R001 to R437). The replacement keys map these IDs to the same sets as the S4 keys.

**S6 Practice sheet.** Using `rng` (continuing after S4): `rows = sorted(practice)`; `perm = rng.permutation(20)`; IDs `"T" + f"{j+1:02d}"` (T01 to T20). The same step writes `practice_answers.xlsx` (see Key contents); it makes no random call. The same practice sheet and answer sheet serve a replacement coder.

**S7 Codebook export.** `codebook_for_coder.xlsx`, sheet `Codebook`, columns `item`, `text`:
- row 1 = header (`item`, `text`);
- row 2 = (`Gold-standard annotation codebook`, empty). The second cell of the workbook's title row holds a placeholder value and is not copied (protocol 4.1);
- rows 3 to 12 = column A and column B of workbook rows 2 to 11, copied as strings without any change.

**Key contents.**
- `cell` = cell label from Section 3; `reference_label` = 0 or 1; `nonhigh` = `True`/`False`; `e1_layer` = `True`/`False`.
- `key_e1.stratum` = `NM` or `RND`; `key_e1.reference_label` = 0 for every row.
- `key_practice.codebook_row` = `CB03` if the reference label is 1, `CB04` if it is 0. `codebook_text` = the verbatim item and text of that row joined by `" | "`.
- `selection_register.cell` is empty for non-concordant passages.
- `practice_answers.xlsx` (sheet `Answers`): one row per practice passage, in practice-sheet order; `passage_id` as on the practice sheet (T01 to T20); `feedback_label` = the reference label (0 or 1); `codebook_text` = as in `key_practice.codebook_text`. The column is named `feedback_label`, not `reference_label`, because `reference` is a blocked header token under B5(b) and `reference_label` is listed in protocol 3.3.

---

## 7. Writing rules

7.1 **Sheets.** Write with `openpyxl.Workbook()`; rename the default sheet to the name in Section 2.1; create no other sheet. Entry columns (`label`, `confidence`, `reason`, `lean`) are left empty (`None`).

7.2 **Text cells.** Write `passage_text` as a string. If a text begins with `=`, set `cell.data_type = "s"` after assignment so that it is not stored as a formula. If openpyxl raises `IllegalCharacterError`, stop and report the `sample_id`; do not strip characters.

7.3 **Data validation** (coder convenience; not a field): `label` list `"1,0,U"`; `confidence` list `"High,Medium,Low"`; `lean` list `"1,0"`.

7.4 **Document properties.** Before saving, set `wb.properties.creator = "coordinator"`, set `lastModifiedBy`, `title`, `subject`, `keywords`, `description` and `category` to `None`, and set `created` and `modified` to `datetime(2026, 10, 15, 0, 0, 0)`. Because openpyxl may still stamp save-time metadata, xlsx bytes are not guaranteed to be identical across runs. Determinism (B12) is therefore checked on a **canonical content hash**: the SHA-256 of the UTF-8 text formed by joining, row by row, the cell values (`""` for `None`) with tab separators and newline row terminators. The deposited hashes are the byte hashes of the files actually sent.

---

## 8. Post-write assertions (run on files re-read from disk, not on in-memory objects)

- **B1** `coding_sheet.xlsx`: worksheet names == `["Coding"]`; 437 data rows; header == the six columns of Section 2.1, exactly and in order.
- **B2** `passage_id` values are unique, match `^A\d{3}$`, and run from A001 to A437.
- **B3** Through the key files, the set of sample_ids on the coding sheet == non-concordant (123) ∪ calibration (100) ∪ E1 (214). `key_calibration` has 100 rows, `key_nonconcordant` 123 and `key_e1` 214; their `passage_id` sets are pairwise disjoint and together equal the sheet's 437 IDs.
- **B4** For every row, `passage_text` equals the workbook `mdna_passage` of the mapped `sample_id`, character for character.
- **B5** Leak check `check_no_leak(sheet)`, which must pass:
  - (a) header set == whitelist `{passage_id, passage_text, label, confidence, reason, lean}` (exact equality; no extra and no missing column);
  - (b) no header contains, case-insensitively, any of: `hit`, `term`, `stratum`, `group`, `source`, `year`, `firm`, `model`, `llm`, `finbert`, `hybrid`, `pred`, `coder`, `draft`, `final`, `adjud`, `consensus`, `gold`, `dictionary`, `matched`, `sample`, `metadata`, `note`, `review`, `author`, `cell`, `nonhigh`, `reference`, `role`, `layer`, `subset`, `e1`;
  - (c) no cell anywhere matches `GS_\d{4}` or `P2_(NON)?HIT_\d+`;
  - (d) every entry-column cell is empty;
  - (e) no comments, no defined names, no hidden rows, columns or sheets;
  - (f) document properties: `creator == "coordinator"`, and `lastModifiedBy`, `title`, `subject`, `keywords`, `description` and `category` are empty.
- **B6** Same as B1 to B5 for `coding_sheet_replacement.xlsx`, with IDs `^R\d{3}$` running from R001 to R437 and the replacement keys. Its set of sample_ids equals that of `coding_sheet.xlsx`, and its sequence of sample_ids in sheet order differs from that of `coding_sheet.xlsx`.
- **B7** `practice_sheet.xlsx`: worksheet names == `["Practice"]`; 20 rows; IDs T01 to T20; leak check B5 passes; text identity as B4. Every practice passage has stratum `HIT`; per-cell counts are HIT-1 8 and HIT-0 12.
- **B8** The sets `nonconcordant`, `calibration`, `practice` and `e1` are pairwise disjoint; their sizes are 123, 100, 20 and 214; `GS_0438` is in `nonconcordant` only.
- **B9** Per-cell counts of `calibration` equal the cell totals in Section 6, and per-cell counts of `practice` equal the practice quotas. Non-High counts per cell equal the logged `k_nh` values.
- **B10** Every practice passage is both-High, unless an `S2` shortfall line is logged for its cell.
- **B11** No `dup_ineligible` passage is in any drawn set. The 437 passage texts on the coding sheet are pairwise distinct, the 20 practice texts are pairwise distinct, and no practice text occurs on the coding sheet.
- **B12** Determinism: the whole selection (S1 to S7) is run a second time in the same process from the same seed files. The canonical content hashes of all xlsx outputs and the byte hashes of all CSV outputs are identical to the first run.
- **B13** `codebook_for_coder.xlsx`: rows 3 to 12 equal workbook Codebook rows 2 to 11 (columns A and B) exactly; row 2 column A == `Gold-standard annotation codebook`; the document properties pass B5(f).
- **B14** Order is not the identity: the sequence of sample_ids in sheet order differs from `sorted(rows)` for the coding sheet, the replacement coding sheet and the practice sheet.
- **B15** `selection_register.csv` has 600 rows; the role counts are nonconcordant 123, calibration 100, practice 20, e1 214 and unused 143 (= 600 − 457); the count of `e1_layer == True` is 244.
- **B16** E1 coverage: the `e1_layer` passages (244) are exactly the union of `e1_layer ∩ calibration` (30) and `e1` (214); `e1_layer ∩ practice` is empty; `e1_layer ∩ calibration` equals the calibration passages in cells `NM-0` and `RND-0`; every `e1_layer` passage has reference label 0 and stratum `NM` or `RND`; no `e1_layer` passage has role `unused`, `nonconcordant` or `practice`.
- **B17** `practice_answers.xlsx` (re-read from disk): worksheet names == ["Answers"]; header == [`passage_id`, `feedback_label`, `codebook_text`], exactly and in order; 20 rows; its `passage_id` set equals the practice sheet's IDs T01 to T20; for every row, `feedback_label` equals the `reference_label` and `codebook_text` equals the `codebook_text` of the same `passage_id` in `key_practice.csv`; `check_no_leak_answers` passes, which applies B5(b) to every header, B5(c) to every cell, and B5(e) and B5(f) to the workbook.

---

## 9. Should-fail controls (each must raise; the script reports PASS only if it does)

| ID | Input | Check applied | Expected |
|---|---|---|---|
| C1 | In-memory table formed by joining `Annotation_Blind` and `Sampling_Metadata` on `sample_id` | `check_no_leak` | raises |
| C2 | Copy of the coding-sheet rows with an added column `dictionary_hit` | `check_no_leak` | raises |
| C3 | Copy of the coding-sheet rows with `passage_id` of row 1 replaced by its `sample_id` | `check_no_leak` | raises |
| C4 | Coding-sheet rows truncated to 436 | B1 row-count check | raises |
| C5 | `practice` set with one `calibration` sample_id added | B8 disjointness check | raises |
| C6 | Expected-hash string with its last character changed | A1 hash check | raises |
| C7 | Copy of the coding-sheet rows with the text of row 1 altered by one character | B4 text-identity check | raises |
| C8 | `e1` set with one passage removed | B16 coverage check | raises |
| C9 | Replacement-sheet sample_id sequence replaced by the coding-sheet sequence | B6 order check | raises |
| C10 | Copy of the coding-sheet rows with an added column `e1_layer` | `check_no_leak` | raises |
| C11 | Copy of the `practice_answers.xlsx` rows with column `feedback_label` renamed `reference_label` | `check_no_leak_answers` | raises |
| C12 | Copy of the `practice_answers.xlsx` rows with `passage_id` of row 1 replaced by its `sample_id` | `check_no_leak_answers` | raises |
| C14 | Copy of the script-folder file list with `analysis_third_coder.py` removed | A10 existence check | raises |

The controls run on in-memory copies and never modify an output file. If any control fails to raise, the script exits non-zero and writes no manifest.

---

## 10. RESULTS block (printed and also stored in the manifest)

```
=== RESULTS ===
workbook_sha256=<...>  seed_selection_sha256=<...>  seed_replacement_sha256=<...>  seed_analysis_sha256=<...>
nonconcordant=123 concordant=477 GS_0438=nonconcordant
calibration per cell: HIT-1 40 (nonhigh k) | HIT-0 30 (k) | NM-0 20 (k) | RND-0 10 (k)
practice per cell: HIT-1 8 | HIT-0 12 | NM-0 0 | RND-0 0
e1_layer=244 (NM <n>, RND <n>) = calibration 30 + e1 214 (practice 0)
coding sheet rows=437  replacement coding sheet rows=437  practice rows=20  answer sheet rows=20
role counts: nonconcordant 123 | calibration 100 | practice 20 | e1 214 | unused 143
SHORTFALL lines: <all, or "none">
dup_ineligible: <count> (in e1_layer: 0)
assertions A1-A10, B1-B17: <n> PASS / <n> FAIL
controls C1-C12, C14: <n> PASS / <n> FAIL
sha256 per output file: <file>=<hash> (one per line)
canonical content hash per xlsx: <file>=<hash>
python=<v> numpy=<v> openpyxl=<v>
=== END RESULTS ===
```

---

## 11. Hand-off after a clean run

1. The runner reports the RESULTS block to the main session and does not send anything to Coder 3.
2. Before coding, the deposit is made (protocol 9.1): a single push to the existing public replication repository under a neutral committer identity, confirmed by the authors, followed by a GitHub Release on the pushed commit. It contains the protocol; the scripts in full; the selection manifest, which records the SHA-256 of this document, of the three scripts (Section 2.4) and the byte SHA-256 of every file in `to_coder\`, `sealed\` and `sealed\replacement\`; the SHA-256 of each seed file; and the SHA-256 of the signed declaration.
3. Only after the Release exists does the administrator send `codebook_for_coder.xlsx`, `practice_sheet.xlsx` and `coding_sheet.xlsx` from `to_coder\`; `practice_answers.xlsx` is sent when Coder 3 reports that the practice sheet is finished (protocol 5.3). Annexes A and B of the protocol are sent earlier, for signing (protocol 9.1).
4. **Analysis script** (separate specification, protocol 6.5 and 8): Stage 1 opens only `key_calibration.csv` (or `key_calibration_replacement.csv` under protocol 10.5) and writes the qualification record; Stage 2 opens `key_nonconcordant.csv` and `key_e1.csv` (or their replacement versions) only if the qualification record exists and its logged hash matches. Bootstrap resamples use the seed in `seed_analysis.txt`. The model comparison is run by `q7_construct_rescore.py`: first the positive control on the previous gold standard, then the new final labels through `--gold-file` (protocol 8.5(h)).
