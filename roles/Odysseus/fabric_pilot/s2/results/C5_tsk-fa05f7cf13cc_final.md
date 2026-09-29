The claim holds. In Aphrodite's A16/A17 campaign report, "accepted" counts the candidates admitted up to a cap of 4 per stratum, not every candidate that qualified.

- **Where the claim comes from:** `roles/Artemis/selftest/runs/R-13/REPORT.md:131-132` and `:205`. The "#889" in the task is Odysseus's comms number (`roles/Artemis/selftest/ROUTING.md:12`), not a line in an Artemis report.
- **The label:** the Aphrodite report prints "per stratum accepted/evaluated". For catalog B it gives add as `4/22` (`4f937e88f:roles/Aphrodite/pivot/APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-26.md:16,18`).
- **The cap is 4:** `a17.py:44` sets `K = 4`. The code stops admitting to a stratum once it holds K candidates (`a17.py:319` and `:337-338`). It reports `accepted` as the size of that capped list (`a17.py:354`). The code comment says "acceptance = first 4 qualifying draws per stratum" (`a17.py:301-302`). `a16.py` has the same logic.
- **The data matches:** in `ac2a935db:roles/Aphrodite/engine/A17_FOUNDRY_EVALS_2026-09-26.jsonl`, five catalog B add candidates qualify (ac, ai, ak, av, au). The foundry log shows B add holding at `4/22` once the cap is hit (`A17_FOUNDRY_2026-09-26.log:10-12`). Across both catalogs, 20 candidates qualify but only 19 are admitted; the extra one is that fifth B add candidate.

I wrote the verdict with per-part citations to `out/verdict.json`.

VERDICT: CONFIRMED