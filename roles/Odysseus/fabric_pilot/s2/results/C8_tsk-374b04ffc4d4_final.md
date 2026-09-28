I could not check claim C8 against the underlying data, because that data is not in this checkout. The claim repeats R-34's report accurately, but the report is where the claim comes from, not evidence that it is true.

- **Where the wording comes from:** The claim matches `roles/Artemis/selftest/runs/R-34/REPORT.md:73-75` and `:108-110`, and `roles/Artemis/selftest/ROUTING_DRAFT.tsv:35`. The report itself calls this "A candidate lead, not verified" (l.108).
- **The data is missing:** The report says the coding lives in `annot_A.json`, `annot_B.json`, `CODEBOOK.md`, `corpus_index.tsv`, `corpus/X01..X33.txt` and `analysis_out.txt` (l.18-34). None of these files exist anywhere in commit 59b94b4ed. `runs/R-34/` contains only `REPORT.md`.
- **Wording details:** "Under both annotators" is stated only for the improver × improvement-rate pairing. The improver × task-skill sentence has no such qualifier. The report also does not say which Archaeon SFE records or which Aphrodite records it means.
- **Not searched:** Bash was denied in this session, so I could not use `git log` or `git show` to look on other branches.
- **What would settle it:** R-34's `annot_A.json`, `annot_B.json` and `corpus_index.tsv`, probably on the Artemis host or branch that ran R-34. Failing that, a fresh blind re-coding of the named records using the codebook.

The verdict file is at `/home/jcraig/fabric-work/worker.ubu001/attempts/att-6ce37e31d724/out/verdict.json`.

VERDICT: CANNOT-VERIFY