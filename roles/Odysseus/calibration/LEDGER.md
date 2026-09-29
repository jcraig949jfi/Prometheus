# Odysseus calibration ledger

Currency: 2026-09-25. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently.

date | call made | what was true | corrected by | changed practice

2026-09-25 | Ran `git pull --ff-only` in the canonical checkout /home/jcraig/Prometheus before reading WORKING_CONTRACT.md, to "catch up" main | s1/s3 forbid pull there. It was NOT a no-op boot transient (HYPATIA-08 ruling): it MOVED the canonical checkout 815cdb32a -> 22bfbc966 (reflog HEAD@{2026-09-25 22:34:38 +0000}, fast-forward, tree clean before and after, no local commits lost). Reported as an incident with SHAs per s3. | self, on reading s3 the same pass; reported to the operator in chat | fetch + rev-parse + worktree add only; never pull; read the contract before any git write on a new host
2026-09-25 | Proposed "Athena" as the seat name after checking only roles/ and agents/ directory names | Athena is the retired ScienceAdvisor alias (M1 era) and still named in research docs; a content grep found it minutes later | self, before the operator answered; operator confirmed | check name candidates with `git grep` over content, not directory listings
2026-09-26 | Wrote test_seek_costs asserting seek(41) from tick 39 replays forward from the cursor | With keyframe 40 one tick away, loading it (1 tick) is cheaper than the cursor (2 ticks); the implementation chose correctly and the test was wrong | self, first green run (70/71) | a cost-rule test now covers each branch separately (backward, forward-from-cursor, forward-via-keyframe) and the fix is named in the commit, not buried
2026-09-28 | Frontier pass 1 reported that Prometheus had not cited Cicala 2026 (2607.09211) or BFF 2026 (2607.01483) and framed it as a blind spot | Both were already in the repository: frontier_campaign_69 dossier 74 (09-07/11), Atlas ECOSYSTEMS.jsonl, the 09-19 Z80 directive ("a donor of machinery"), Nestor npe-p2 (09-27) | Artemis FR-010 (read 2026-09-28); confirmed by git grep | before any "the program has not X" claim, git grep origin/main (all refs) for the identifier; the R4 packet rule now applies to Odysseus's own reports
