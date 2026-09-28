The numbers in C7 match what R-34's report says, but the claim's requirement that they be reproducible from committed coding files fails. At this commit (59b94b4ed), the report is the only R-34 file in the repository.

- **Numbers match the report:** `roles/Artemis/selftest/runs/R-34/REPORT.md:43-44, 54, 82, 88` gives recall 0.34 and 0.23, precision 0.84 and 0.56, and per-field kappa 0.73, 0.74 and 0.76. The recall and precision follow from the table counts: 21/62, 14/62, 21/25 and 14/25. This only shows the report is internally consistent. Without the underlying data I could not check it against anything independent.
- **Coding files are not committed:** the report names `annot_A.json`, `annot_B.json`, `CODEBOOK.md`, `analyze.py`, `corpus_index.tsv`, `corpus/X*.txt` and `analysis_out.txt` (lines 19, 24, 31, 34 and 116). Searching the run directory and the whole checkout found none of them; `REPORT.md` is the only file in the R-34 folder. So the kappa, recall and precision cannot be recomputed from Git.
- **Other branches not checked:** Bash and git were denied in this sandbox, so I couldn't run `git log --all` or `git show`. If the files are on another branch or only on the worker's machine, that would change the answer on reproducibility.

The verdict is in `out/verdict.json`.

VERDICT: PARTIAL