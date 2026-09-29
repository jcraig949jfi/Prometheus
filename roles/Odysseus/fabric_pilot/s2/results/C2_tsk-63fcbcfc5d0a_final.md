Some of the claim checks out against the repository, but two parts don't hold as stated, so the verdict is PARTIAL.

- **The 27,083 count: true.** It is in `archaeon/causal_lens/out_v02/B6_PROBE_r038751.json:6` and matches the pack at `roles/Odysseus/th006/pack/r038751.pack.json:116`.
- **The hash in the recipe and pack: true.** Both files record `cd9547c24811f52b...` (`r038751.recipe.json:9`, `r038751.pack.json:188` and `:195`). Earlier runs on ubu001 and M2 are recorded with the same hash (`ops/campaigns/C-001/E-001/TASKS.md:23` and `:52`).
- **R-13's own replay producing that hash: can't be checked.** R-13 kept its replay output in a scratch folder on ubu002 and never committed it. The only source for "equals the recipe" is R-13's report (`roles/Artemis/selftest/runs/R-13/REPORT.md:73`).
- **"An M2 attestation of it is on main": true only in a looser sense.** `roles/Odysseus/th006/attest/M2_r038751_2026-09-28.txt` is committed and says MATCH. But what M2 attested is the preserved log's content hash `95a12c29...` (8,118,119 bytes, 74,800 rows). It did not attest `cd9547c2` or the 27,083 count. The two connect only through the pack's chain of hashes. The pack's own attestation field still reads PENDING (`r038751.pack.json:152-156`).

I couldn't run git in this session, so I couldn't confirm that commit 59b94b4 is on main. I took that from the task setup and the git status snapshot.

`verdict.json` is written to the output directory.

VERDICT: PARTIAL