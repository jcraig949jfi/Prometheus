# THESEUS-31b AMENDMENT 1 -- checkpointing only (2026-10-08)

The first 31b run (2 workers, sharing 4 CPUs with the 30d scan) was killed at the 2-hour
background limit before writing anything (pool.map writes only at the end). No result of it
was produced or read. task_hard.py now appends Part 1 / Part 2 rows to PART1.jsonl /
PART2.jsonl as each genome completes and skips completed ids on restart. Genomes, seeds,
thresholds, arms, controls, decision rule and predictions are unchanged. The rerun uses all
4 workers and runs alone.
