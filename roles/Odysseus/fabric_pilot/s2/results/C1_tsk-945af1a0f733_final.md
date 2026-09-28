The three gaps the claim names are real, but the claim that they are "exactly" the whole gap, with everything else in Git, is contradicted by the source report itself. The claim comes from `roles/Artemis/selftest/runs/R-13/REPORT.md`; R-34 is an unrelated study of how to label experiments. Git commands were blocked in this session, so I checked the files on this commit only and could not read the seat branches.

**The three named gaps are real:**
- **BEE multi-day:** R-13 lists no committed outcome, only a prereg, code and pilots on a seat branch, with all outcomes on M2 (R-13:34, 59). `MULTIDAY_PREREG.md` and `md_analysis.py` are not on this commit. I could not open the seat branch itself.
- **Z80xAtlas `RUNS.jsonl`:** the file is excluded by `archaeon/z80atlas/.gitignore:2`. Only its sha256 is committed (`archaeon/z80atlas/postcampaign/AUDIT_RECEIPT_2026-09-23.json:12`).
- **BEE coupling denominators:** `results.jsonl` is not committed. The coupling report says so and records only its hash (`roles/Bellerophon/coupling_2026-09-24/COUPLING_CAMPAIGN_REPORT.md:164-165`). The per-run ledger, which holds only the positive runs, is on main, so the numerators can be rebuilt but the denominators cannot.

**"Exactly" and "all others in Git" are false:**
- **ENVGATE-02:** R-13's own limits section (R-13:174-177) says that for this row, as for the BEE numerators, whether the list of positive results is complete "still rests on host files". That fits the repository: `archaeon/envgate2/.gitignore:1` excludes `runs/`, so the block files are on M2 only (R-13:63).
- **Z80xAtlas:** besides `RUNS.jsonl`, a 14.1 GB tree is on M2 (R-13:61).
- **BEE coupling:** the p-value and P1-P6 also exist only as aggregates, not just the denominators (R-13:103).
- **Cosmos:** the real C3 headline is sealed and was not scored; a public gate result was substituted (R-13:44, 69).
- **Headline choice:** R-13 says the choice of headline number was its own, and a different pick for the deep-block row would rest on M2 (R-13:168-173).

The verdict file is at `/home/jcraig/fabric-work/worker.ubu001/attempts/att-c2fe72ce85c3/out/verdict.json`.

VERDICT: PARTIAL