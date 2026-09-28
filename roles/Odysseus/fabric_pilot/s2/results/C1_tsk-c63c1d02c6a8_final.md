The three gaps the claim names are real, but its "exactly these three, everything else is in Git" part is overstated, so the claim is only partly true. I wasn't allowed to run Bash or `git`, so I checked the main tree with Read, Glob and Grep and could not inspect the seat-branch contents myself.

The claim comes from `roles/Artemis/selftest/runs/R-13/REPORT.md`. R-34's report is about something unrelated (a lens-field study).

**What checks out:**
- **BEE multi-day:** there are no outcomes in Git. R-13 says the seat branch holds only the prereg, code and pilot receipts, and the outcomes are on M2 (R-13:34, R-13:59). There is no multiday directory on main. One wording problem: the claim puts the *outcomes* on the seat branch, but the branch holds no outcomes, and the campaign was still running when R-13 was written.
- **Z80xAtlas RUNS.jsonl:** it is not in Git. `archaeon/z80atlas/campaign/` holds only five top-level files, and the file appears only as a hash (`Z80ATLAS_POSTCAMPAIGN_ADJUDICATION_2026-09-23.md:12`).
- **BEE coupling denominators:** the per-arm totals (150), P1–P6 and the comp_final p-value exist only as aggregates. The report and `COUPLING_RESULTS.json` are committed, but the per-run `results.jsonl` is not in the tree; only its sha256 is (`COUPLING_CAMPAIGN_REPORT.md:165`).

**What doesn't hold:**
- **ENVGATE-02 (deep block):** R-13's own limits section (R-13:174-177) says the committed records list positives only. Whether any *other* establishment was positive rests on block files kept on M2, and `archaeon/envgate2/.gitignore:1` excludes `runs/`. So not every input to this headline is in Git.
- **Aether:** its 72 E-006 unit files are on M2 only. The headline was re-run from committed code and inputs, so it is still recomputable.
- **Aphrodite A17:** the inputs are in Git, but only on four unmerged seat branches, not on main.

The verdict file is `out/verdict.json`.

VERDICT: PARTIAL