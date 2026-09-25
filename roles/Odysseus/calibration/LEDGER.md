# Odysseus calibration ledger

Currency: 2026-09-25. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently.

date | call made | what was true | corrected by | changed practice

2026-09-25 | Ran `git pull --ff-only` in the canonical checkout /home/jcraig/Prometheus before reading WORKING_CONTRACT.md, to "catch up" main | s1/s3 forbid pull there. It was NOT a no-op boot transient (HYPATIA-08 ruling): it MOVED the canonical checkout 815cdb32a -> 22bfbc966 (reflog HEAD@{2026-09-25 22:34:38 +0000}, fast-forward, tree clean before and after, no local commits lost). Reported as an incident with SHAs per s3. | self, on reading s3 the same pass; reported to the operator in chat | fetch + rev-parse + worktree add only; never pull; read the contract before any git write on a new host
2026-09-25 | Proposed "Athena" as the seat name after checking only roles/ and agents/ directory names | Athena is the retired ScienceAdvisor alias (M1 era) and still named in research docs; a content grep found it minutes later | self, before the operator answered; operator confirmed | check name candidates with `git grep` over content, not directory listings
