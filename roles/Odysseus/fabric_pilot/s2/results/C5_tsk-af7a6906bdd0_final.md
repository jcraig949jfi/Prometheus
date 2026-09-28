The claim holds: in Aphrodite's A17 report, "accepted" is the number of candidates admitted under a cap of 4 per group, not the number that qualified.

- **The cap is in the code.** `a17.py` sets `K = 4` (`373d7ef28:roles/Aphrodite/engine/a17.py:44`). Its docstring says "acceptance = first 4 qualifying draws per stratum" (lines 303–304). The loop only adds a candidate while fewer than K have been accepted (lines 319 and 337).
- **The report's figure is the capped count.** The per-stratum "accepted" value is the length of that capped list (line 354).
- **The data shows the difference.** For catalog B, `add` stratum, 5 of 22 evaluated draws qualify in `ac2a935db:.../A17_FOUNDRY_EVALS_2026-09-26.jsonl`. The report still prints `'add': '4/22'` (`4f937e88f:roles/Aphrodite/pivot/APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-26.md:18`).
- **Source.** The claim comes from `roles/Artemis/selftest/runs/R-13/REPORT.md:131-133` and `:205`.

One wording point: the code's per-candidate flag `ACCEPTED_CANDIDATE` (line 269) marks a draw that qualified, not one that was admitted. The claim is about the report's "accepted/evaluated" figure, so this doesn't change the verdict.

All the evidence is on Aphrodite's own branches, not on `main`; I read it with `git show`. I wasn't allowed to run Python, so I counted the 5 and the 22 with `grep`.

The verdict is in `out/verdict.json`.

VERDICT: CONFIRMED