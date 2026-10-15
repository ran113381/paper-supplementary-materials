# Protocol: Blind Third-Coder Re-adjudication of the MD&A Passage Gold Standard

- **Version:** 2.7 (supersedes version 2.6). Sections 1 to 10 and Annexes A and B keep the text of version 2.6, except that the fields in 9.1 are filled in and 9.1 refers to Section 11. Section 11 records the departures from version 2.6 that occurred on 2026-10-15, before the push.
- **Deposit:** GitHub Release [RELEASE URL] on commit [PUSH COMMIT SHA] of the study's existing public replication repository (Section 9.1). The deposit time is the server-side time of that push and Release. These two values cannot appear in the file they identify (Annex C).
- **Coder 3:** referred to in this protocol, in every deposited or released file and in the manuscript only as "Coder 3" (Section 2.5).
- **Administrator:** one of the authors, acting only in the role defined in Section 2.6.
- **Companion documents:** `J16_selection_rules.md` (selection rules; deposited by SHA-256 only until coding is complete, because it contains the random seeds); the selection script and the analysis scripts, deposited in full; the codebook file. The SHA-256 of each is recorded in the selection manifest deposited with the Release.

**Access rule.** Before and during coding, Coder 3 receives only Annex A (Instructions to the coder), Annex B (Declaration of independence), the codebook file, the practice sheet, the practice answer sheet and the coding sheet. Sections 1 to 10 describe the composition of the coding sheet, which Coder 3 must not know (Section 2.3). Coder 3 may read the full protocol only after the returned coding sheet has been hashed and the hash recorded (Section 9.2).

**Placeholders.** Square-bracketed fields are listed in Annex C. Every field except the push commit and the Release URL is filled in before the push.

---

## 1. Purpose and scope

1.1 **The gold standard.** The validation sample consists of 600 MD&A passages: 300 dictionary-matched passages drawn by simple random sampling from the 1,256 matched passages in the seed pool, 150 randomly drawn non-matched passages, and 150 purposively drawn near-miss non-matched passages. Two research assistants (Coder 1 and Coder 2) labeled every passage independently under the codebook reproduced in Section 4, without access to dictionary-hit status or sampling metadata.

1.2 **What this protocol covers.**
- (a) **Re-adjudication** of all 123 passages without a concordant binary label ("non-concordant passages"): the 122 passages on which the labels of Coder 1 and Coder 2 differ, and the one passage (GS_0438) that both marked U.
- (b) **Calibration:** 100 passages drawn from the 477 passages to which Coder 1 and Coder 2 gave the same binary label ("concordant passages"). They are used to qualify Coder 3 (Section 6.5).
- (c) **Practice:** 20 further concordant passages from the matched stratum, used for training only (Section 5).
- (d) **E1, the concordant non-matched layer:** Coder 3 also labels every concordant passage in the two non-matched strata (near-miss and random), 244 passages in all, every one of them labeled blind on the coding sheet (Section 6.3). E1 changes no final label (Section 7.5); it is reported separately (Section 8.2(ix)).

Passages under (a), (b) and (d) are interleaved on one coding sheet, so that Coder 3 cannot tell them apart.

1.3 **Rule applied.** The re-adjudication applies the codebook's own third-coder rule (row CB08, Section 4): "unresolved disagreements should be adjudicated by discussion or a third coder. The adjudicated value becomes final_label." The earlier resolution of the non-concordant passages, and every document produced for it, is set aside and plays no part in this procedure.

1.4 **What does not change.** No dictionary term, no sample membership, no label of a concordant passage and no model output is changed by this procedure.

1.5 **Content restriction.** This protocol states procedures only. It reports no agreement coefficient, validation metric or expected outcome of the existing annotation.

---

## 2. Coder eligibility and independence

2.1 **Number.** One coder, Coder 3.

2.2 **Eligibility.** All of the following must hold:
- (a) Coder 3 is not an author;
- (b) Coder 3 took no part in dictionary construction, sampling, the original coding, any earlier review or resolution of the labels, the LLM audit or any analysis of the study;
- (c) Coder 3 has not read the manuscript, the response letters, the replication repository or any file derived from the study's data, and undertakes not to consult any of them until the coding sheet has been returned;
- (d) Coder 3 reads Chinese MD&A text as a native reader and reads the English codebook fluently. The codebook is used in its English original and is not translated; a translation would be a deviation from this protocol;
- (e) Coder 3 confirms, before signing Annex B, that about 7 to 9 hours can be given to the coding sheet before the return deadline in Section 10.3.

2.3 **Information withheld from Coder 3.** Coder 3 is told only to label the passages according to the codebook. Coder 3 is not told the study's hypotheses, the dictionary terms, which passages, if any, were disputed or how many were disputed, how the coding sheet was composed or which passages belong to any subset of it, the labels, notes or confidence ratings of Coder 1 and Coder 2, any model output, or which outcome would favor any method.

2.4 **Prohibited aids.** Throughout training and coding, Coder 3 uses no generative-AI tool of any kind, no machine translation, no web search and no external resource other than the codebook file, the practice sheet, the practice answer sheet and the coding sheet. Coder 3 does not copy passage text into any website, application or file other than the sheet in which it was supplied. Coder 3 does not discuss any passage with anyone, except through the question channel in 2.6.

2.5 **Identity and relationship to the authors.** Coder 3 is a doctoral student in Global Business and a classmate of the first author. The manuscript states this relationship in the same words as this protocol and Annex B (item 4). Coder 3 is not an author and is not named in the manuscript or in any deposited or released file. Coder 3's name appears only on the privately kept signed declaration (Section 9.4).

2.6 **Administrator and questions.** The administrator (one of the authors) handles logistics only: sending materials, including the practice answer sheet (5.3), receiving the returned files and recording their hashes. Questions from Coder 3 are answered only by quoting the relevant codebook row verbatim, without paraphrase, example or comment on any passage. Every question and answer is logged with its date and time and released after coding (Section 9.3). From the signing of Annex B until the coding sheet is returned, no author, including the administrator, discusses the study, the manuscript or any passage with Coder 3 outside this channel.

2.7 **Declaration.** Coder 3 signs the declaration in Annex B before receiving the practice sheet and countersigns its completion clause when returning the coding sheet. The signed copy is kept privately; only its SHA-256 is recorded (Section 9.4).

---

## 3. Materials

3.1 **What Coder 3 receives.** Exactly six items: (i) the codebook file, a verbatim export of the Codebook sheet of the gold-standard workbook; (ii) the practice sheet (20 passages); (iii) the practice answer sheet `practice_answers.xlsx`, sent together with the other materials and opened only after the practice sheet is finished (5.3); (iv) the coding sheet (437 passages; Section 6.1); (v) Annex A; (vi) Annex B. The SHA-256 of items (i) to (iv) is recorded in the selection manifest deposited with the Release.

3.2 **Field whitelist (practice sheet and coding sheet).** Each sheet has exactly two data fields:
- `passage_id`: a new identifier assigned after random ordering and not derived from any existing identifier;
- `passage_text`: the passage text, copied character for character from the workbook.

and exactly four blank entry fields: `label`, `confidence`, `reason`, `lean` (Section 4.4). The file has no other column, worksheet, comment, hidden content or document property that refers to the study.

The practice answer sheet has exactly three columns: `passage_id` (as on the practice sheet), `feedback_label` (the passage's concordant label) and `codebook_text` (the verbatim codebook row for that label). It has no other column, worksheet, comment, hidden content or document property that refers to the study.

3.3 **Fields that must not appear.** None of the following may appear in any material given to Coder 3, under any name:
- from the workbook's annotation table: `sample_id` (the GS identifier), `firm_id`, `year`, `coder1_label`, `coder1_confidence`, `coder1_notes`, `coder2_label`, `coder2_confidence`, `coder2_notes`, `adjudication_label`, `adjudication_notes`, `final_label`;
- from the sampling metadata: `sample_group` (stratum), `original_passage_id`, `dictionary_hit`, `matched_terms`, `text_source`, `original_dictionary_label`, `source_file`, `seed_file_sample_type`;
- from the disagreement review table: `review_status`, `author_confirmation`;
- from the published prediction file: `consensus_label`, `gold_binary`, `dictionary_pred`, `llm_consensus_pred`, `finbert_pred`, `hybrid_pred`;
- from the selection outputs: `role`, `cell`, `nonhigh`, `reference_label`, `e1_layer`. The one exception is the practice answer sheet, which carries, for each of the 20 practice passages, its concordant label (equal to `coder1_label`, `coder2_label` and `final_label` for that passage) in the field `feedback_label`, because that label is the answer against which Coder 3 checks the practice labels (5.3);
- any LLM, FinBERT or hybrid label, class, score or confidence; any stratum, group, subset, source, firm or year indicator; any earlier adjudication draft or rationale.

3.4 **Passage text.** The passage text carries no mark that flags dictionary terms. The few brackets or asterisks that occur in some passages come from tables or parentheses in the source documents; they are original text and are left unchanged.

3.5 **Enforcement.** The selection script checks the whitelists in 3.2 and the absence of every field in 3.3 on the files as written to disk, the practice answer sheet included. As a positive control, the same check must fail on the merged annotation-and-metadata table and on deliberately contaminated copies of the sheets and of the answer sheet (`J16_selection_rules.md`, Sections 8 and 9).

---

## 4. Codebook (verbatim) and the use of U

4.1 **Source.** Codebook sheet of `genai_gold_standard_adjudication_workbook.xlsx` (workbook SHA-256 aa072750c0a1ae9ac68dece24f060ef2c8e1d1bfb7a153244f9d69791620b0a0). The rows are reproduced below without change, including their original wording. Row identifiers CB01 to CB10 are added for reference only. The second cell of the title row holds a placeholder value that is not codebook text; it is omitted here and from the codebook file.

| Row | Item | Text |
|---|---|---|
| — | Gold-standard annotation codebook | — |
| CB01 | Purpose | Create a human-labeled gold standard for evaluating the dictionary-based GenAI disclosure measure and LLM baselines. |
| CB02 | Primary label values | Use 1, 0, or U only. |
| CB03 | 1 = GenAI-related disclosure | The passage clearly refers to enterprise-level generative AI, large models, AIGC, ChatGPT-like tools, content/code/image/text generation, intelligent Q&A/writing, model platforms/products, or business deployment/exploration of GenAI. |
| CB04 | 0 = Not GenAI-related disclosure | The passage refers only to ordinary digitalization, generic AI, automation, intelligent manufacturing, cloud computing, big data, IoT, robotics, strategic slogans, background noise, or an unrelated/false keyword match. |
| CB05 | U = Unclear | The passage is too vague to decide. Use U only when the text is genuinely ambiguous. |
| CB06 | Coder confidence values | High / Medium / Low. |
| CB07 | Blind coding rule | Coders should use Annotation_Blind only. Do not look at Sampling_Metadata before independent coding. |
| CB08 | Disagreement resolution | After coder1 and coder2 finish, unresolved disagreements should be adjudicated by discussion or a third coder. The adjudicated value becomes final_label. |
| CB09 | Metric calculation later | Dictionary precision, recall and F1 require the final_label merged with Sampling_Metadata. |
| CB10 | Important boundary | Label disclosure relevance, not true internal deployment scale. The passage can be coded 1 if it substantively discloses GenAI-related exploration, adoption, products, platforms, or applications. |

4.2 **Procedural reading of the codebook.** The following notes concern procedure only and add nothing to the label definitions:
- (a) CB07: for Coder 3, the coding sheet takes the place of Annotation_Blind. Sampling_Metadata is not supplied.
- (b) CB08 and CB09 describe how labels are used after coding. They do not bear on how any passage is labeled.
- (c) No example, gloss, decision tree or translation is given. Questions are handled under 2.6.

4.3 **Use of U.** U is permitted. Following CB05, it is used only when the text is genuinely ambiguous. Whenever Coder 3 enters U, Coder 3 must also (i) give a one-line reason quoting the phrase that makes the passage ambiguous and (ii) enter a binary lean, 1 or 0, stating which label Coder 3 would choose if forced. On calibration passages, the number of U labels determines which statistic qualifies Coder 3 and can by itself disqualify Coder 3 (Section 6.5). On all other passages there is no limit on U, but every U carries a reason and a lean.

4.4 **Entry rules.**
- `label`: 1, 0 or U (CB02).
- `confidence`: High, Medium or Low (CB06).
- `reason`: one line quoting the decisive phrase from the passage. Required for every 1 and every U; optional for 0.
- `lean`: 1 or 0. Required for every U; left blank otherwise.

---

## 5. Training

5.1 **Reading.** Coder 3 reads the codebook file in full before any practice passage.

5.2 **Practice passages.** Twenty concordant passages from the matched stratum that are not calibration passages: 8 with concordant label 1 and 12 with concordant label 0. They are drawn from passages that both Coder 1 and Coder 2 rated High confidence, so that the harder concordant passages remain available for calibration. Selection rules: `J16_selection_rules.md`, Section 6, step S2. No practice passage is taken from the near-miss or random non-matched strata, so that the whole E1 layer is labeled blind on the coding sheet (6.3). Practice passages do not appear on the coding sheet, so that no text appears twice in Coder 3's materials.

5.3 **Feedback.** Coder 3 labels the practice passages on the practice sheet, in Excel, in the order given. When the practice sheet is finished, Coder 3 opens the practice answer sheet `practice_answers.xlsx`, which is sent with the other materials and holds for each practice passage only `passage_id`, `feedback_label` (its concordant label) and `codebook_text` (the verbatim codebook row for that label: CB03 for 1, CB04 for 0). Coder 3 compares the practice labels with it alone. No other feedback, explanation or discussion is given. The practice sheet is not returned to the authors.

5.4 **Use of practice labels.** Practice labels are not returned to the authors and are not used for qualification or for any metric. Practice passages keep their concordant labels as final labels.

5.5 **Duration.** About 45 minutes, including reading the codebook.

---

## 6. Coding-sheet composition and qualification

6.1 **Composition.** The coding sheet holds 437 passages: the 123 non-concordant passages (1.2(a)), the 100 calibration passages (1.2(b)) and the 214 E1 passages that are not calibration passages (6.3). Rows are placed in random order and given new identifiers A001 to A437, so that Coder 3 cannot tell non-concordant, calibration and E1 passages apart. The seed is deposited by SHA-256 only. There is one coding sheet and one round of coding.

6.2 **Calibration sampling.** The 100 calibration passages are drawn without replacement from the 477 concordant passages, stratified by stratum and concordant label. Within each cell, passages that at least one of Coder 1 and Coder 2 rated Medium or Low confidence ("non-High") are over-sampled up to the target shown; the remainder of the cell quota is drawn from passages both rated High.

| Cell | Calibration quota | Non-High target within quota |
|---|---|---|
| Matched, concordant label 1 | 40 | 12 |
| Matched, concordant label 0 | 30 | 20 |
| Near-miss non-matched | 20 | 12 |
| Random non-matched | 10 | 6 |
| **Total** | **100** | **50** |

The matched-cell quotas keep reference positives and negatives close to balance, which limits prevalence effects on agreement statistics. The achieved share is reported (Section 8.2(vi)).

6.3 **E1 passages.** The E1 layer is every concordant passage in the near-miss and random non-matched strata: 244 passages. No E1 passage is drawn at random; the layer is taken in full, and all 244 passages are labeled blind on the coding sheet. None is a practice passage (5.2). The division of the layer on the coding sheet is fixed by the calibration draw:
- the 30 calibration passages in the two non-matched cells are on the coding sheet as calibration passages and serve both qualification (6.5) and E1 reporting (8.2(ix));
- the remaining 214 passages are on the coding sheet as E1 passages. They are never used for qualification.

E1 passages are interleaved at random with the other passages on the coding sheet (6.1). Their keys are opened only in Stage 2 (6.5).

6.4 **Exclusions and overlap.** Calibration, practice, E1 and non-concordant passages form pairwise disjoint sets on the coding sheet and the practice sheet. GS_0438 (marked U by Coder 1 and Coder 2) is a non-concordant passage and is never used for calibration, practice or E1. Where two concordant passages have identical text, only the one with the lower identifier is eligible for calibration or practice, so that no text appears twice in Coder 3's materials. Because the E1 layer must be covered in full, the selection script stops if any passage in the E1 layer is ineligible under this duplicate rule.

6.5 **Qualification by two-stage unmasking.**
- **Receipt.** On receipt, the returned coding sheet is hashed (SHA-256) and the hash is recorded with date and time before any row is read (Section 9.2).
- **Stage 1 (calibration rows only).** The pre-registered analysis script opens the calibration key and reads only the rows listed in it. Between Coder 3's labels and the reference (concordant) labels it computes: Krippendorff's α on the nominal scale with U treated as missing ("α, U missing"); Krippendorff's α with each U replaced by Coder 3's lean ("α, lean substituted"); Cohen's κ, U rows excluded; percent agreement with a Wilson 95% CI, U rows excluded; a percentile bootstrap 95% CI for each α (2,000 resamples of calibration passages; seed deposited by SHA-256 only); and the number of U labels among the 100 calibration passages.
- **Qualification statistic.** If the calibration passages carry fewer than 20 U labels, the qualification statistic is α, U missing. If they carry at least 20 and fewer than 40, it is α, lean substituted. Both α values, and the U rate, are reported in every case.
- **Threshold.** Coder 3 is qualified if the point estimate of the qualification statistic is at least 0.667 (Krippendorff, 2004) and the calibration passages carry fewer than 40 U labels. Coder 3 is not qualified if the qualification statistic is below 0.667, or if the calibration passages carry 40 or more U labels, whatever the value of α; CB05 restricts U to genuinely ambiguous text. There is a single threshold and no intermediate category.
- **Qualification record.** The script writes the qualification statistics and the outcome (qualified or not qualified) to a qualification record, which is hashed and logged before Stage 2.
- **Stage 2 (non-concordant and E1 rows).** The script opens the non-concordant key and the E1 key only if the qualification record exists and its logged hash matches. Stage 2 runs whatever the outcome, because the labels are reported in either case; the outcome decides only their role (Sections 7 and 10.4). The outcome is not revisited after Stage 2.
- **If qualified,** Coder 3's labels on the non-concordant passages form the primary benchmark (Section 7.2), and results on the 477 concordant passages are reported alongside them (Section 8.2(ii)).
- **If not qualified,** Section 10.4 applies.
- **Operating characteristics.** Any computation of the probability of qualification under hypothetical coder-accuracy scenarios is deposited with the Release and listed in the manifest. Such scenarios are not reproduced here because some are parameterized by agreement coefficients or validation metrics of the existing annotation (Section 1.5).

---

## 7. Final-label rules

7.1 **Concordant passages** (including practice, calibration and E1 passages): the final label is the concordant label. It does not change whatever Coder 3 enters.

7.2 **Non-concordant passages (123):** the final label is Coder 3's binary label (CB08: "The adjudicated value becomes final_label"). Where Coder 1 and Coder 2 gave opposite binary labels, this equals the three-coder majority. Where one of them entered U, Coder 3's label breaks the tie. For GS_0438, which both marked U, Coder 3's label decides.

7.3 **Coder 3 enters U on a non-concordant passage:** the passage is unresolved. It is excluded from the primary metrics, assigned Coder 3's lean in a sensitivity analysis, and assigned each label in turn when computing the bounds (Section 8.2(iv)).

7.4 **Calibration disagreements:** where Coder 3's label on a calibration passage differs from the concordant label, the concordant label stands (two original labels against one). Every such passage is listed, and a "flip variant" recomputing all metrics with these labels flipped is reported as one line in the supplement (Section 8.2(viii)).

7.5 **E1 disagreements:** where Coder 3 labels an E1-layer passage 1 or U, the concordant label 0 stands (two original labels against one). Such passages are counted and listed under Section 8.2(ix); they do not enter the primary metrics or any sensitivity analysis of them. The 30 E1-layer passages that are also calibration passages are in addition handled under 7.4: they are listed there and enter the flip variant.

7.6 **Not qualified, or labels set aside under Section 10:** no Coder 3 label enters the benchmark. The fallback benchmark (Section 10.7) applies.

---

## 8. Pre-registered analysis plan

8.1 **Positive controls.** Before any new label is read, the analysis script reproduces (i) the previously published validation counts and metrics under the previous labels and (ii) the corresponding values on the 477 concordant passages. The expected values are stored as assertions in the script and are not restated in this protocol. If any control fails, the script stops and the failure is reported before any further step.

8.2 **Outputs reported regardless of direction.**
- (i) The metrics of every method on the re-adjudicated labels: precision and recall with Wilson 95% CIs, and F1 with a bootstrap 95% CI (2,000 resamples; seed deposited by SHA-256 only).
- (ii) The same metrics on the 477 concordant passages.
- (iii) Results by stratum: matched, random non-matched, near-miss non-matched.
- (iv) Bounds over passages left unresolved by a Coder 3 U, assigning each such passage the label least favorable and most favorable to each metric.
- (v) Results under the previous labels (supplement).
- (vi) The qualification statistics (Section 6.5), including both α values and the U rate; the achieved share of reference positives in the calibration set; Coder 3's agreement with Coder 1 and with Coder 2 on the non-concordant passages; and the vote pattern (Coder 1 / Coder 2 / Coder 3) behind every final label that changes a dictionary error count relative to the concordant-subset baseline.
- (vii) For every non-matched passage whose final label is 1: its identifier, the decisive phrase and Coder 3's reason. Every new false negative of the dictionary is thus disclosed passage by passage.
- (viii) Calibration disagreements, listed passage by passage, with the flip variant as one line in the supplement (Section 7.4).
- (ix) **E1.** For all 244 E1-layer passages, every one of them labeled blind on the coding sheet (the 30 non-matched calibration passages and the 214 E1 passages), by stratum (near-miss, random) and in total: the number Coder 3 labeled 1, with a Clopper–Pearson 95% CI for the proportion; the number Coder 3 labeled U, with their leans; and, for each passage labeled 1, its identifier, the decisive phrase and Coder 3's reason. No E1-layer passage is a practice passage, so the report describes the layer as 244 passages labeled blind. Because the layer is a census, the counts describe these 244 passages without sampling error; the Clopper–Pearson interval is read as an interval for the underlying rate at which concordant 0 labels produced by the same coding process in the non-matched strata would be labeled 1 by Coder 3, not as uncertainty about the count in these 244 passages. These figures are reported separately from the primary metrics and are not combined with them. They are read as an empirical upper bound on the error of concordant labels in the non-matched strata, and they are reported whatever their value, including zero; the report does not state only that no final label changed.

8.3 **Evaluation populations.** Each method's metrics are reported for: all passages, excluding unresolved ones; the 477 concordant passages; the passages covered by strict LLM consensus; the full benchmark, with abstentions counted as non-detections; and each stratum. Coverage is reported separately.

8.4 **Stratification and weighting.**
- Precision is computed on the matched stratum, which is a simple random sample of the 1,256 dictionary-matched passages in the seed pool, and is reported as an estimate for those 1,256 passages.
- Recall is reported for the benchmark as a whole (8.3) and by stratum, with a Clopper–Pearson 95% CI for the random non-matched stratum. It is not weighted to the corpus: the near-miss stratum was drawn purposively and serves as a stress test of hard negatives, and no record of the number of non-matched passages in the corpus is available to the authors. Corpus-level recall is therefore not identified by this design, and no corpus-level recall is reported.

8.5 **Positive-class construct for model comparisons.** The following is fixed before coding begins and applies to every model comparison computed on the new final labels.
- (a) **Benchmark positive class.** A passage is positive if its final label is 1 under the codebook in Section 4 (CB03, read with CB10). The codebook given to Coder 3 is not altered.
- (b) **Two panels, both reported whatever the results.** Panel A (primary), positive class "GenAI-related": an LLM consensus label of `substantive_adoption` or `generic_or_background` counts as 1. Panel B (reported alongside), positive class "substantive adoption only": only `substantive_adoption` counts as 1. In both panels, `unclear` counts as 0; a `disagreement` label, and any passage without an LLM label (every non-matched passage), counts as an abstention. The hybrid rule uses the strict-consensus prediction where one exists and the dictionary prediction where strict consensus abstains; it is the existing hybrid rule, with only the positive set changed between panels. The dictionary and the fine-tuned classifier have the same predictions in both panels.
- (c) **Abstentions.** In full-benchmark metrics an abstention counts as a non-detection. Conditional metrics on the covered passages are reported alongside, with coverage stated separately.
- (d) **Evaluation populations.** The full benchmark (all passages with a resolved final label, abstentions counted as non-detections), the passages covered by strict consensus, and the matched stratum. The primary report gives the full benchmark and the covered passages.
- (e) **Intervals.** Precision and recall with Wilson 95% CIs; F1 as in 8.2(i).
- (f) **Existing outputs only.** LLM labels, dictionary predictions and fine-tuned classifier predictions are taken from the stored files and are not regenerated. The fine-tuned classifier is not retrained; its training target is the substantive-adoption class, so Panel B is its own construct and its Panel A figures are read as a cross-construct evaluation.
- (g) **Blinding.** Coder 3 has no access to consensus labels, dictionary-hit status or classifier predictions (Section 3.3).
- (h) **Script and order.** The comparison is computed by `q7_construct_rescore.py`, deposited in full before coding. The script is first run on the previous gold standard as a positive control: under Panel B it must reproduce the previously published model-comparison values, which are held as assertions in the script and are not restated here. Only after that control has passed is the script run on the new final labels through its `--gold-file` option. Both logs are released. If the control fails, the script stops and the failure is reported before any further step.
- (i) **Previous gold standard.** Both panels computed on the previous labels are reported in the supplement for traceability.
- (j) Under the fallback benchmark (Section 10.7), (a) to (i) apply unchanged to that benchmark.

8.6 **No result-driven changes.** The dictionary, the sample, the final-label rules and this analysis plan are not changed in response to the results. Any deviation is logged with its date and reason and reported in the manuscript.

---

## 9. Timestamping and archiving

9.1 **Before coding: push and Release.** The deposit is a single push to the study's existing public replication repository, confirmed by the authors, followed by a GitHub Release on the pushed commit. The server-side time of the push and of the Release is the timestamp. The commit is made under a neutral committer identity that names no person. The push contains:
- this protocol, with every Annex C field filled except the push commit and the Release URL;
- the codebook file;
- the selection script, the analysis script and `q7_construct_rescore.py`, in full;
- the selection manifest, which records the SHA-256 of `J16_selection_rules.md`, of the codebook file, of each script, of the practice sheet, the practice answer sheet, the coding sheet, the replacement coding sheet (Section 10.5) and every key file;
- the SHA-256 of each seed file: `seed_selection.txt` 14cd753a7745eb8e2c40f42a1d7d423c68d1a72f58faf3742eb070182c935ec0; `seed_replacement.txt` b337bc82cd4ef1da72c4e5202ae71fa14b71ef2546b5de651ca359cb960ba185; `seed_analysis.txt` d802d334fa64c6fee7ef317d0b16bc42c8af758253b05d36a09eee8a6bff0c19;
- the SHA-256 of the signed declaration (Section 9.4): 6176929e3f1a1307a85041889e61e575b23a42cd48ead01aaed2577247a9023b (the copy described in 11.3).

The order is fixed: Coder 3 signs Annex B; its hash is entered above; the push is made and the Release created; only then are the materials in 3.1(i) to (iv) sent, together and once. On 2026-10-15 this order was not followed; Section 11 records what was done instead. After the Release, the push commit and the Release URL are entered in the archived copy of this protocol and in the manuscript's supplement.

9.2 **During coding.** On receipt of the returned coding sheet, its SHA-256 is recorded with date and time before any row is read. The SHA-256 of the countersigned declaration is recorded on receipt in the same way. If a replacement coder is engaged (10.5), the replacement coder's signed declaration is hashed on receipt, and the hash is recorded in the same way and released (9.3); the replacement coder's countersigned declaration is handled likewise. The question-and-answer log (2.6) is kept continuously.

9.3 **After coding.** The following are released: the keys; the seeds; `J16_selection_rules.md`; all Coder 3 labels, confidence ratings, reasons and leans, including those on E1 passages; the question-and-answer log; the qualification record; any sheet set aside under Section 10.5 or 10.6, marked as such; the receipt hashes, including those of any replacement coder's signed and countersigned declarations. The previous labels and the earlier resolution record remain in the archive unchanged.

9.4 **Signed declaration.** Coder 3 signs a copy of the Annex B template that bears Coder 3's name. The signed copy, and the countersigned copy returned with the coding sheet, are kept privately by the authors and are neither deposited nor released. The signed copy may be shown to the handling editor in confidence on request; Coder 3 consents to this in Annex B, item 8. This protocol records only the SHA-256 of the signed copy (9.1); the SHA-256 of the countersigned copy is recorded on receipt (9.2) and released (9.3). A replacement coder's signed and countersigned copies are handled in the same way, except that the SHA-256 of the signed copy is recorded on receipt (9.2), because it cannot be entered before the push. No deposited or released file contains Coder 3's name or any personal detail beyond the relationship stated in 2.5.

---

## 10. Failure and timing contingencies

All times are Korea Standard Time (UTC+9).

10.1 **No coder.** A coder is confirmed when the coder meets Section 2, has signed Annex B, and the SHA-256 of the signed copy has been recorded. If no coder is confirmed by 2026-10-16, 18:00, this protocol is not activated and the fallback benchmark (10.7) applies; no new labels are collected.

10.2 **Planned timing.** Training takes about 45 minutes. Coding the 437 passages is expected to take about 7 to 9 hours; this estimate rests on an assumed reading speed that has not been measured. Stage 1 and Stage 2 run after the sheet is returned.

10.3 **Return deadline.** The coding sheet is due by 2026-10-19, 12:00. If no complete sheet has been returned by then, the fallback benchmark (10.7) applies. A returned sheet that lacks a label for any passage, or a lean for any U, is incomplete and is handled under 10.5. A missing `reason` does not make a sheet incomplete; it is recorded as missing and released with the other entries (9.3).

10.4 **Not qualified.** If Coder 3 is not qualified under Section 6.5 (qualification statistic below 0.667, or 40 or more U labels on the calibration passages), the fallback benchmark (10.7) applies. Coder 3's labels, the qualification statistics and the E1 counts are reported in the supplement.

10.5 **Withdrawal.** If Coder 3 withdraws, or returns an incomplete sheet, the sheet is hashed and archived but not unmasked: no key is opened against it, it enters no metric, and it is released after the procedure ends, marked as withdrawn. Before signing Annex B, a prospective replacement coder confirms that the coding sheet can be completed by the return deadline in 10.3. If a replacement coder is confirmed (10.1) before 2026-10-18, 12:00, the replacement codes from the start, on the replacement coding sheet: the same passages under a new random order and new identifiers, generated and hashed before the first push (`J16_selection_rules.md`, step S5), under this same protocol. The return deadline in 10.3 is unchanged. No coder continues another coder's sheet. If no replacement is confirmed by that time, or the replacement also withdraws, the fallback benchmark (10.7) applies. At most one replacement is made.

10.6 **Breach of the declaration.** If a breach of Annex B is found before unmasking, Coder 3's labels are void and are handled as in 10.5 (replacement or fallback). If a breach is found after unmasking, the manuscript discloses what the breach was, the 477 concordant passages become the primary benchmark, and Coder 3's labels are reported as a sensitivity analysis only. How the breach came to light (self-report, the administrator, or traces in the returned files) is recorded in the archive.

10.7 **Fallback benchmark.** The primary benchmark is the 477 concordant passages. The supplement reports, for all 600 passages, results under the previous labels, under the label variant recorded in the workbook's review sheet and under each of Coder 1's and Coder 2's labels, together with bounds over the 123 non-concordant passages. The model comparison follows Section 8.5. Wherever the fallback benchmark is used, the manuscript states that it excludes every passage on which Coder 1 and Coder 2 did not give the same binary label, including every non-matched passage that either of them did not label 0. Any Coder 3 labels collected are reported only as stated in 10.4 to 10.6.

10.8 **No further contingency.** There is no second round of coding, no retraining and no coder beyond the single replacement in 10.5.

---

## 11. Departures recorded before the push (2026-10-15)

All times are Korea Standard Time (UTC+9) on 2026-10-15. The administrator recorded the following departures from version 2.6 before the push. They are reported with this protocol and in the manuscript's supplement (8.6).

11.1 **Order of sending (2.7, 9.1).** The administrator sent Annex B in English (`B_declaration_to_sign.docx`, SHA-256 8982af27802fa71c2bb1f21593c920fc9b318043c874aa6cd1ca53a117ab1f2c) at 10:26 and, at 12:41, one archive holding the whole set of materials (SHA-256 3ce959c80c8142a667cbd234036fad8a3ab07429f48d506c5be654ce14f3676c; contents in 11.2). The materials in 3.1(i) to (iv) therefore reached Coder 3 before a signed copy of Annex B was returned (11.3) and before the push and Release, not after them. The coding sheet sent is byte-identical to the coding sheet recorded in the selection manifest, so the passages Coder 3 labels, and their order, are those fixed before any material was sent. The push and Release of this version are made before the coding sheet is returned, and the returned sheet is hashed on receipt (9.2).

11.2 **Materials sent (2.2(d), 3.1, 3.2, 4.2(c)).** The archive held seven files in place of the six items in 3.1:

| File | SHA-256 | Content |
|---|---|---|
| `0_说明.md` | 538956020421b64fe91033f50816422a0667c4a79a9d0e3451a9f4d2944490c7 | A note written for the administrator, listing the files and the intended sending order. It states that the coding sheet is identical to the English version and that the analysis script reads its column names. It contains nothing on the composition of the coding sheet, its strata, the calibration passages, any key or any threshold. |
| `1_独立性声明_签字用.docx` | e87b8610c263590f649ca861188504d998056a35e27a51724280a8aaede20135 | Chinese translation of Annex B. Not signed; Coder 3 signed the English Annex B (11.3). |
| `2_编码须知.docx` | a15044f07afd7bdc5fe6fbef1e70ff611df4ec1d31ca05777f20bd255bed9e52 | Chinese translation of Annex A. |
| `3_编码规则_中英对照.xlsx` | 425c073afc4afc76f5a84db29169f2ce287a7c77cc4b7c0f85c0d2df54bdf3e2 | The codebook file with a header row and an added column giving a Chinese translation of each row, with a note that the English original prevails. The English rows CB01 to CB10 are verbatim. |
| `4_练习表.xlsx` | 80844ea7d1a33f68056533b564d9cc8f8b5f971b3b99d9ed7eee8eb645c479e2 | The practice sheet with column headers in English and Chinese. Passage identifiers and texts are identical to those of the manifest practice sheet (20 of 20). |
| `5_练习答案_做完练习再打开.xlsx` | 4f804227b6b4ba641156eaa860d0393b35b47ee128ef0511ff801cbf7aa4f859 | The practice answer sheet with Chinese column names and each codebook row in Chinese translation and in the English original. Passage identifiers and feedback labels are identical to those of the manifest version (20 of 20). |
| `6_正式标注表.xlsx` | 8228c8a4f24a01df09ff88e0779a33bb9141205e2eec0b691444c601ca3dc1e1 | The coding sheet, byte-identical to the manifest version. |

The column headers of the practice sheet and the column names of the practice answer sheet therefore differ from those set in 3.2, and the practice answer sheet has four columns instead of three; neither sheet is returned to the authors or read by any script (5.3, 5.4). The Chinese translation of the codebook departs from 2.2(d) and 4.2(c). Its effect on Coder 3's labels cannot be separated from Coder 3's own judgement, and the manuscript reports it as a limitation.

11.3 **Declaration (2.7, 9.2, 9.4).** Coder 3 returned signed copies of the English Annex B at 15:20 and at 15:36 (SHA-256 4306c2f2af330c6c280e9288abdbd76c9c08df4825b98fce991b4d7e99c362f7 and 1f752697e6b2376104fcb71ac4256ddc8949068d6d0750da73b65b8171f4337d). In both copies the completion clause had also been signed, with the time of return entered as 12:00 PM and 10:00 AM on 2026-10-15 respectively, both earlier than 12:41, when the coding sheet was sent; neither copy therefore serves as the completion record in 9.2. Coder 3 then signed a new copy of the same Annex B, dated 15 October 2026, which the administrator received at 16:31. On this copy the completion clause was also filled in at signing, with the time entered as 16:20 PM on 2026-10-15, before coding was finished, so it does not serve as the completion record either. The SHA-256 entered in 9.1 is that of this copy. Completion is confirmed by Coder 3 when the coding sheet is returned, and that confirmation is hashed on receipt (9.2). The two earlier copies are kept privately with the re-signed copy (9.4).

11.4 **What is unchanged.** The selection rules, the selection script and its outputs, the keys, the seeds and the analysis scripts, which hold the qualification threshold, are those recorded in the selection manifest before any material was sent. Sections 8 and 10 are unchanged from version 2.6.

---

## Annex A. Instructions to the coder

*(This annex, Annex B, the codebook file, the practice sheet, the practice answer sheet and the coding sheet are the only materials given to the coder before the coding sheet is returned.)*

1. **Task.** You will label short passages from the Management Discussion and Analysis sections of Chinese listed firms' annual reports, using the attached codebook. There are two steps: a practice sheet of 20 passages, then a coding sheet of 437 passages.
2. **Codebook.** Read the codebook in full before you start. Apply it as written. Where the codebook mentions "Annotation_Blind", read this as the sheet you have been given; you will not receive any other sheet.
3. **For each passage, fill in:**
   - `label`: 1, 0 or U;
   - `confidence`: High, Medium or Low;
   - `reason`: one line quoting the phrase in the passage that decided your label (required for 1 and U; optional for 0);
   - `lean`: if you entered U, enter 1 or 0 for the label you would choose if you had to choose; otherwise leave blank.
4. **U.** Use U only when the text is genuinely ambiguous (codebook row U). Every U needs a reason and a lean.
5. **Practice.** Fill in the practice sheet in Excel, in the same way as the coding sheet. Only when you have finished it, open the answer sheet, which shows the reference label for each practice passage and the codebook row for that label. Compare your labels with it on your own. You do not return the practice sheet.
6. **Work alone and without aids.** Do not use any generative-AI tool, machine-translation tool, web search or other outside resource. Do not copy passage text into any website, application or file other than the sheet you were given. Do not discuss any passage with anyone. Do not discuss the study with any of its authors, including the administrator, except to send questions under item 7. Do not read any paper, letter, repository or data file connected with this study until you have returned the coding sheet.
7. **Questions.** Send questions to the administrator. Answers will consist only of quotations from the codebook. All questions and answers are recorded.
8. **Returning the sheet.** Before returning the sheet, check that every passage has a label and every U has a lean; a sheet in which a passage lacks a label, or a U lacks a lean, cannot be used. You may revise any label until you return the sheet. Once returned, it cannot be changed. The administrator records a fingerprint (hash) of the file on receipt.
9. **Time.** Allow about 45 minutes for the practice step and about 7 to 9 hours for the coding sheet. You may work in several sessions. The coding sheet is due by 2026-10-19, 12:00 Korea Standard Time.
10. **Declaration.** Sign Annex B before you receive the practice sheet, and sign its completion clause when you return the coding sheet.

---

## Annex B. Declaration of independence (template)

*Handling of the signed copy.* Coder 3 signs a copy of this template that bears Coder 3's name. The signed copy and the countersigned copy are kept privately by the authors and are neither deposited nor released; the signed copy may be shown to the handling editor in confidence on request (item 8). The protocol records only the SHA-256 of the signed copy (Section 9.1); the SHA-256 of the countersigned copy is recorded on receipt (Section 9.2). In the protocol and in every deposited or released file the signatory is referred to only as "Coder 3".

I, the undersigned, declare that:

1. I am not an author of the study for which I am labeling passages.
2. I have taken no part in building its dictionary, drawing its sample, its original coding, any earlier review or resolution of its labels, any audit of model labels, or any analysis of its data.
3. I have not read the manuscript, any response letter or the replication repository of the study, and I will not consult them, or any file derived from the study's data, until I have returned my coding sheet.
4. My relationship to the authors is: I am a doctoral student in Global Business and a classmate of the first author.
5. During training and coding I will not use any generative-AI tool, machine-translation tool, web search or other outside resource, apart from the codebook, the practice sheet, the practice answer sheet and the coding sheet, and I will not copy passage text into any website, application or file other than the sheet I was given.
6. I will not discuss the passages with anyone, I will not discuss the study with any of its authors until I have returned my coding sheet, and I will put any question to the administrator only.
7. I can give about 7 to 9 hours to the coding sheet and return it by the deadline stated in the instructions.
8. I consent to my signed declaration being shown to the handling editor of the journal in confidence on request.

Name (on the signed copy only): ____________________

Signature: ____________________ Date: ____________________

**Completion clause (signed on return of the coding sheet).** I confirm that I labeled every passage myself and complied with items 3, 5 and 6 throughout training and coding.

Signature: ____________________ Date and time of return: ____________________

---

## Annex C. Open items

Every item except the last is filled in before the push (Section 9.1). The last item cannot appear in the file it identifies; it is entered after the Release in the archived copy of this protocol and in the manuscript's supplement.

| Item | Location |
|---|---|
| SHA-256 of `seed_selection.txt`, `seed_replacement.txt` and `seed_analysis.txt` | 9.1 |
| SHA-256 of the signed declaration (the copy re-signed under 11.3) | 9.1; 11.3 |
| Date and time written on the re-signed declaration, and time of its receipt | 11.3 |
| Push commit SHA and Release URL | Header; 9.1 |

---

## References

Krippendorff, K. (2004). *Content analysis: An introduction to its methodology* (2nd ed.). Sage.
