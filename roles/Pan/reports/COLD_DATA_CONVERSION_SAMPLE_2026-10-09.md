# What converting the cold April JSON Lines to Parquet would buy (measured sample)

Currency: 2026-10-09T13:10Z (commit 7c2d44c15; first written as 13:40Z by estimate, corrected from the commit receipt). Command: `python -m pan.coldsample FULL SAMPLED...`
(pan/coldsample.py), with `PAN_COLD_FORCE_STRING=1` for the lossless string form.
Sources were READ only; nothing was moved, deleted or rewritten. Sample Parquet
lives in <lake>/cold_sample/ (M2 NVMe) and can be deleted.

Context (reports/INVENTORY_2026-10-09.md): 278.7 GB untracked in the canonical
checkout on M2, 92 percent last modified April 2026; cartography/convergence/data
holds 128.8 GB in 134 files, and four files are 125.2 GB of it.

## Method

- One file converted IN FULL with an oracle (Parquet rows == non-empty source
  lines).
- The three largest files measured by 10 random-offset blocks of 16 MiB each
  (seed 20261009), trimmed to whole lines -- never the file's first lines.
- Two forms: TYPED (pyarrow infers one schema) and RECORD_STRING (one column of
  verbatim JSON text per line, zstd) -- the lossless form PAN-16 uses.

## Results

    file                         source     form            ratio   projected   per-block spread
    formula_triage.jsonl         0.36 GB    typed (FULL)    14.19   0.026 GB    oracle OK: 3,133,171 rows = lines; 2.0 s
    hmf_hecke_eigenvalues.jsonl  74.08 GB   record_string    4.01   18.49 GB    4.1 - 5.4  (typed impossible: mixed string/number list)
    formula_trees.jsonl          36.89 GB   typed            0.45   81.68 GB    -- typed Parquet is LARGER than the JSON
                                            record_string   15.54    2.37 GB    14.8 - 16.3
    openwebmath_formulas.jsonl   13.91 GB   typed           10.34    1.35 GB
                                            record_string    7.93    1.75 GB    7.7 - 8.4

Best form per family, the four files: 125.2 GB -> about 22.2 GB (about 5.6x).

## Readings

- The form must be chosen per family BY MEASUREMENT: inferred typed columns for
  deeply nested trees came out 2.2x LARGER than the text (formula_trees), while
  flat records shrink 10-14x typed.
- The lossless string form is never the worst choice here (4.0-15.5x) and keeps
  every byte of every record; typed form adds column pruning for flat families.
- Sample size: 10 x 16 MiB is 0.2-1.2 percent of each large file; the per-block
  spread is narrow (above), so the projections are stable to about +/-15 percent.

## What is NOT decided here (QUESTIONS.md Q-008)

Whether to convert, where the output lives (Q-003), and whether the April
sources are archived or removed are the operator's calls. No consumer has asked
for these families yet (base role 2a I: utilisation is not the objective).
