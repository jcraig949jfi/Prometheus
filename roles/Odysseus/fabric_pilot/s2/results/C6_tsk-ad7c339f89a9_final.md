I found that both parts of claim C6 are true on origin/main (59b94b4ed, the same commit as HEAD).

- **Aphrodite A17 is on seat branches only:** Six commits add the A17 files (373d7ef28, 9adb83f6c, fb5628435, ac2a935db, 4f937e88f, 45a6bae22). One example is `4f937e88f:roles/Aphrodite/engine/A17_E1_RESULT_2026-09-26.json`. The key commits (9adb83f6c and 4f937e88f) are contained in exactly 4 remote branches: `origin/aphrodite/{a16-campaign-2026-09-26, arc3-2026-09-28, compounding-2026-09-27, frontier-2026-09-27}`. That matches `roles/Artemis/selftest/runs/R-13/REPORT.md:67`. No main ref contains these commits. A search of main for `roles/Aphrodite/**/*[aA]17*` finds nothing: `roles/Aphrodite/engine/` has `A16_*` files but no `A17_*`.
- **BEE multi-day is on one seat branch only:** The prereg (12ce26e23), the prep commit (45d7c0c0f) and the launch commit (ee7a7d954) exist only on `origin/bellerophon/multiday-campaign-2026-09-26`. There is no `roles/Bellerophon/multiday*` directory on main. The only related file on main is `roles/Bellerophon/coupling_2026-09-24/NEXT_MULTIDAY_CAMPAIGN.md`. Its own header (lines 1–5) calls it a design proposal, not frozen or launched, so it is not campaign evidence. The campaign's outcomes are not committed anywhere; R-13 grades them HOST-ONLY (R-13 lines 34 and 59).

My shell access was partly denied, so I used `git branch --contains` rather than ancestry checks. I also did not inspect the local `main` ref (22bfbc966), which differs from origin/main.

The verdict file is at `/home/jcraig/fabric-work/worker.ubu001/attempts/att-d73f6fada77f/out/verdict.json`.

VERDICT: CONFIRMED