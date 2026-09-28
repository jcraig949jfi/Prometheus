I checked the claim against commit 59b94b4ed, which is the same commit as origin/main. It holds: the Aphrodite A17 files and the BEE multi-day files are on seat branches only, not on main.

- **Aphrodite A17 is on seat branches.** The per-draw and per-replicate files exist in `roles/Aphrodite/engine/` on the branches, for example `A17_DRAWS_2026-09-26.json`, `A17_E1_RESULT_2026-09-26.json` (lists replicates 0–7), `A17_FOUNDRY_EVALS_2026-09-26.jsonl` and `A17_A_DONORS_2026-09-26.json`. The commit that adds the A17 campaign report (4f937e88f) is on exactly 4 branches: `origin/aphrodite/a16-campaign-2026-09-26`, `arc3-2026-09-28`, `compounding-2026-09-27` and `frontier-2026-09-27`. That matches the "4 seat branches" in R-13 (`roles/Artemis/selftest/runs/R-13/REPORT.md:67`).
- **Aphrodite A17 is not on main.** No `A17_*` files exist at 59b94b4ed. The two commits that add A17 files (4f937e88f and ac2a935db) are not part of main's history.
- **BEE multi-day is on one branch only.** The prereg, the code (`multiday_campaign.py`, `md_analysis.py`) and the pilot receipts come from commits 35de9b083 → 12ce26e23. The last of these is only on `origin/bellerophon/multiday-campaign-2026-09-26`. Nothing matching `roles/Bellerophon/multiday*` or `prometheus/z80atlas/*multiday*` exists on main.

One nuance: the BEE multi-day branch holds only the prereg, code and pilot receipts. No campaign outcomes are committed anywhere. R-13 says they are on M2 and grades the row HOST-ONLY (`REPORT.md:59`). The claim still holds as worded.

`verdict.json` is written to the output directory.

VERDICT: CONFIRMED