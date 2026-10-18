# Release hashes

## Returned coding sheets

The four coding sheets below are released as copies in which only file metadata were cleared
to protect privacy: the document properties `creator` and `lastModifiedBy` were emptied, the
custom-properties part (office-suite build identifiers) was removed and, in the two author-entered
copies, an absolute local folder path stored in `xl/workbook.xml` was removed. No cell was changed:
every cell of every sheet was compared between each original and its released copy, and all are
identical. Because the metadata changed, the released files have new SHA-256 values; both are listed.

The original SHA-256 values are the receipt hashes. They were computed from the files as received
(for the two author-entered copies, as saved), and they are the values cited in the departure record
(`../DEPARTURE_RECORD.md`, departures (b) and (c)). No separate contemporaneous receipt log is
released; the file times and the times at which the first and the corrected sheet were hashed are
those stated in the departure record. All times are in a single local time zone.

| Role | Released file | File time | Hashed | Original SHA-256 (receipt hash) | Released copy SHA-256 |
|---|---|---|---|---|---|
| first returned sheet | `sheets/coder3_first_returned_sheet.xlsx` | 22:46:49 (first day) | 10:04 (next morning, before any row was read) | `3d0aff4b1e55ee4eedc4a3f41ef52ece0e16e98e9aace52938377c9819306169` | `b463a515ec5f5ad3253fd793b66cf08129228d3e88063739b08c3ebb5b1a723d` |
| author-entered copy 1 | `sheets/author_entered_copy_1.xlsx` | 10:32:46 | not returned by the third coder; saved by the author | `4a624ddfb65f9c9916e0fe0e8637f439fdf3e5b2526bb46c6346c90ae020824f` | `92c8521a7dd1b2e0f9e5f1a56cc4d9999fba8a88b5b37f7cde2962ae0a50d71c` |
| author-entered copy 2 | `sheets/author_entered_copy_2.xlsx` | 10:39:56 | not returned by the third coder; saved by the author | `e2602bd7d0f7737082c06c3fb1282eeddf43227153290aab7d2f8048ef9560bb` | `857897e9eb3171cf3395fa67d39d19a38dfce13f2cbdcb36ec5977cedc9898a4` |
| corrected sheet (used for the reported results) | `sheets/coder3_corrected_sheet.xlsx` | 11:45:16 | 11:47:10 (before any row was read) | `bfd18c9233c520098197f359fd194ea4a909e06bd3199d9669c672e6a8e4189f` | `6a4f9862b6219a01db40009b3338797f3e4c2b613bd794b2792700a5f65a4a41` |

The first returned sheet and the corrected sheet were returned by the third coder; the two
author-entered copies were made by the administrator (one of the authors) and were not returned by
the third coder (departure (c)). `sheets/sheet_comparison.txt` lists every cell in which the four
sheets differ. The signed declaration is not released; its SHA-256 is recorded in the protocol
(`../protocol_third_coder_v2.7.md`, Sections 9.1 and 11.3). No separate completion confirmation
accompanied the returned sheets (departure (a)).

## Other released files

| File | SHA-256 |
|---|---|
| `keys/key_calibration.csv` | `fc582c6817f30a06ca1dfe6c18e53607115bed4864f072b7c826df80ecb246cb` |
| `keys/key_e1.csv` | `6c4667892a79fb4ae06ad4b44dcb4ff5d6c246f468d6cf0ed46a65293f9884f0` |
| `keys/key_nonconcordant.csv` | `ea3fe59376bf9668faa1fff582d56b822fffb158e041db64f667e7973e47b001` |
| `keys/key_practice.csv` | `6178bbc105c402ca84df7e2be7baceccd5d0b0dfbfee0da58571cedab1c99252` |
| `keys/replacement/key_calibration_replacement.csv` | `b59fa7d120f679342dce929e8700e64152ae1ffaa1f31b05beb1652cdad86ace` |
| `keys/replacement/key_e1_replacement.csv` | `f1243d8fa18805d5cacebce4cec0aaf39c1d4b1cabd2b4b0d7481b7eecc83a3e` |
| `keys/replacement/key_nonconcordant_replacement.csv` | `3c06189f0d38d13d18b64c6ae329ee498cde1de38a3d7d93b4ecdbf166e89633` |
| `labels/final_labels.csv` | `4533fc1a863eb7bb208c027a99505d1f2c5b9b0ddeeb48f1013c6d4997042379` |
| `labels/stage2_calibration_disagreements.csv` | `30a70b21b3c2d5fa95aa8811f2abb889ce29a715e6b11b9540a0a225e6f92b58` |
| `labels/stage2_e1_labeled_1.csv` | `ce14a6e02447111ee61d4f0dd85211de2172e0b278ad8654d2d8d516aacf3dbd` |
| `labels/stage2_e1_labeled_U.csv` | `304e0776e639d21d9a29730b664f4c5de34635e6cba630c39e8a7ff78eb9b9eb` |
| `labels/stage2_e1_summary.json` | `fdcb44690da101ae1203309b959396cf964d6eed28a2df66b240c7cb4c4aa0d1` |
| `labels/stage2_nonconcordant_labels.csv` | `8e00fdf01fc1268822c483fb5b25782b606373acd3e1d1f7f623392241c5b363` |
| `runs/run1_first_returned_sheet/q7_control.log` | `e6fa8d0f0f9ab2764307adaf3062abf3239d206bf1fc385c329d39b85f41c437` |
| `runs/run1_first_returned_sheet/qualification_record.json` | `b22a4d32deddd738426d697f1377a81e188857ed6b09fc2bfe1c4f9f8ec6f0bc` |
| `runs/run1_first_returned_sheet/qualification_record_hash_log.txt` | `80890a095b02a6a99c7e36fcdee49ddbe7ba819b4ee14907b215083087045e22` |
| `runs/run1_first_returned_sheet/resubmit_diff.txt` | `2e895f49ddf933de907ebdf84c74f7c4fcb58e7b674cdc6047a202b178b9138e` |
| `runs/run1_first_returned_sheet/resubmit_diff_sheets.py` | `96a8668bd43a650fdae68a91f86e1cdba50d78019e81a3fb15cb375ff73291a9` |
| `runs/run1_first_returned_sheet/stage1.log` | `dc391da307b02ca74e30c902d4b40a93bc866475a56cd2c8a344e117b61d06bd` |
| `runs/run1_first_returned_sheet/stage2.log` | `d624320b602337f4bc85e1f36b24179e40b15598f0a7e56f52b009e383d8f4e5` |
| `runs/run2_author_entered_copy_2/final_labels.csv` | `4533fc1a863eb7bb208c027a99505d1f2c5b9b0ddeeb48f1013c6d4997042379` |
| `runs/run2_author_entered_copy_2/q7_control.log` | `e6fa8d0f0f9ab2764307adaf3062abf3239d206bf1fc385c329d39b85f41c437` |
| `runs/run2_author_entered_copy_2/q7_new_gold_U0.log` | `ec8106399e12297c61e7277b2e0244280e4c2cbf7a983b4c4b164ac85a5afa7f` |
| `runs/run2_author_entered_copy_2/q7_new_gold_U1.log` | `12ba95cd681a8ef241a2989205f9d0ea64044b403c5014ff3420fd22e5729f0c` |
| `runs/run2_author_entered_copy_2/q7_new_gold_flip_lean.log` | `8bbcc062fb26082f5d88ef6d0b6d4464dda6aabd4ff73280db051216a8df8300` |
| `runs/run2_author_entered_copy_2/q7_new_gold_lean.log` | `12ba95cd681a8ef241a2989205f9d0ea64044b403c5014ff3420fd22e5729f0c` |
| `runs/run2_author_entered_copy_2/q7_new_gold_primary.log` | `6db75e47cbd93f2e9ae859c1c5427009c19202c709ba8aee010546309156000f` |
| `runs/run2_author_entered_copy_2/qualification_record.json` | `b7186c5877caa2f8dc01ff89cd8f89740c2fb2235e966ca013b5aa766733a673` |
| `runs/run2_author_entered_copy_2/qualification_record_hash_log.txt` | `d2dc854949948d54716dc3721c21c1c9a550480b7651c9233c4681e180ad0056` |
| `runs/run2_author_entered_copy_2/stage1.log` | `a209e8be1e7826de72f8e699f7dff2f62df30b8f274ad055cbcbc8be122c5da9` |
| `runs/run2_author_entered_copy_2/stage2.log` | `c6a6d3defb7ce65089aa8834790a52366548f0202923a9f929570ab557b1c78e` |
| `runs/run2_author_entered_copy_2/stage2_calibration_disagreements.csv` | `30a70b21b3c2d5fa95aa8811f2abb889ce29a715e6b11b9540a0a225e6f92b58` |
| `runs/run2_author_entered_copy_2/stage2_e1_labeled_1.csv` | `ce14a6e02447111ee61d4f0dd85211de2172e0b278ad8654d2d8d516aacf3dbd` |
| `runs/run2_author_entered_copy_2/stage2_e1_labeled_U.csv` | `304e0776e639d21d9a29730b664f4c5de34635e6cba630c39e8a7ff78eb9b9eb` |
| `runs/run2_author_entered_copy_2/stage2_e1_summary.json` | `fdcb44690da101ae1203309b959396cf964d6eed28a2df66b240c7cb4c4aa0d1` |
| `runs/run2_author_entered_copy_2/stage2_nonconcordant_labels.csv` | `8e00fdf01fc1268822c483fb5b25782b606373acd3e1d1f7f623392241c5b363` |
| `runs/run3_corrected_sheet/J23_compare.log` | `73f9c34665e1b7801e7f17b63ae59dc1f04c65e3c82911e18b918f38eced16be` |
| `runs/run3_corrected_sheet/J23_compare.py` | `bd020ed593893ade328e9bc2815ae0708796ad997a3c2475502f522dc76c3dd2` |
| `runs/run3_corrected_sheet/q7_control.log` | `e6fa8d0f0f9ab2764307adaf3062abf3239d206bf1fc385c329d39b85f41c437` |
| `runs/run3_corrected_sheet/q7_new_gold_U0.log` | `ec8106399e12297c61e7277b2e0244280e4c2cbf7a983b4c4b164ac85a5afa7f` |
| `runs/run3_corrected_sheet/q7_new_gold_U1.log` | `12ba95cd681a8ef241a2989205f9d0ea64044b403c5014ff3420fd22e5729f0c` |
| `runs/run3_corrected_sheet/q7_new_gold_flip_lean.log` | `8bbcc062fb26082f5d88ef6d0b6d4464dda6aabd4ff73280db051216a8df8300` |
| `runs/run3_corrected_sheet/q7_new_gold_lean.log` | `12ba95cd681a8ef241a2989205f9d0ea64044b403c5014ff3420fd22e5729f0c` |
| `runs/run3_corrected_sheet/q7_new_gold_primary.log` | `6db75e47cbd93f2e9ae859c1c5427009c19202c709ba8aee010546309156000f` |
| `runs/run3_corrected_sheet/qualification_record.json` | `d9dd5acffe871e10c3fcfd14bc9bf54179aaeadcda80436ca6a138e30b498843` |
| `runs/run3_corrected_sheet/qualification_record_hash_log.txt` | `737d6b16671f41807499e1dd5d76d771ec987d1f7340f4a9fb37c173a3383992` |
| `runs/run3_corrected_sheet/stage1.log` | `c7c6a81009091324da4905d2c6a43c878902ab0c26c383ce24cf5567e4020d4d` |
| `runs/run3_corrected_sheet/stage2.log` | `23ec41ea2108ad4b91901f3a965d6d60a75fcb2213754849f9103f746f42e742` |
| `seeds/seed_analysis.txt` | `d802d334fa64c6fee7ef317d0b16bc42c8af758253b05d36a09eee8a6bff0c19` |
| `seeds/seed_replacement.txt` | `b337bc82cd4ef1da72c4e5202ae71fa14b71ef2546b5de651ca359cb960ba185` |
| `seeds/seed_selection.txt` | `14cd753a7745eb8e2c40f42a1d7d423c68d1a72f58faf3742eb070182c935ec0` |
| `selection/J16_selection_rules.md` | `e5aa06323db5e75f4be3520eeeb7c4c03a0e766ff97297b8af69f9cc627e36be` |
| `selection/selection_register.csv` | `7042561621bb03140e863ed0fdbedd56ff0526464c908b2c2108a07106db8c82` |
| `sheets/sheet_comparison.txt` | `8a8eafac3e600b04d9943f23f89e63ec85c61e3db36eaaa5acb11b416571129e` |
| `qa_log.md` | `2a57b98979fcf5b1adcbb0331b22816c827b9893bd27ec08e7156f2b8350f69d` |
