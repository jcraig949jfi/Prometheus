The claim checks out against the ledger itself (`roles/Bellerophon/coupling_2026-09-24/COUPLING_ORIGIN_LEDGER.jsonl`), not just against the R-13 report.

- **47 ECHO K40 rows:** lines 20–66 are the `B-cop_ECHO_K40_*` rows, and each has a different run id. Lines 1–19 are E2 or ECHO K16 rows and lines 67–68 are CONST K40 rows, so none of those count.
- **Arm counts:** ON 29, OFF 6, YOKED 6, SHUFFLED 6. This matches R-13 REPORT.md:102.
- **13 rows with `self_copy` false:** the ledger has 21 lines with `"self_copy": false`. Eight are K16 rows (lines 6, 7, 9–14). The other 13 are ECHO K40 rows (lines 33, 34, 40, 42–48, 50, 55, 58). Lines 33–34 show that `self_copy` sits inside the `arch` object, and each line has exactly one `self_copy` key.
- **5 of the 6 YOKED rows:** lines 34, 42, 45, 47 and 48 are false. The sixth YOKED row, line 36 (run c009538), is true.

By arm, the 13 are 5 YOKED, 3 OFF, 3 SHUFFLED and 2 ON. I did not check the related statement at R-13 l.204 that 9 of these rows have no copy op, because it isn't part of this claim.

The verdict file is `out/verdict.json`.

VERDICT: CONFIRMED