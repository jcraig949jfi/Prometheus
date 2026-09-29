# Research-ready Threads (delegation inventory)

Each file here is self-contained: a fresh researcher can work from git
alone. Shared ground rules for all Threads:
- Read first: ../C1B_REVIEW_AND_MECHANISMS.md, ../MEMORY_INTERVENTIONS.md,
  ../SPIKES_2026-09-27_LOG.md, and prometheus/ananke/lens.py.
- Never edit the frozen C1/C1b code paths (c1b.py, c1b_run.py, engine
  physics). Put new probes in lens.py or in roles/Ananke/research/spikes/.
  They act between ticks only. An engine change needs the golden check
  (prometheus/ananke/tests/golden_c1_controls.json) to stay bit-identical.
- Write predictions and decision rules into a PLAN file and COMMIT it
  before running. Keep every Attempt, including failures, in a LOG.
- Worlds: analysis namespaces 0x5E1-0x5EF belong to Ananke. Take a new one
  per Thread and name it in the PLAN. Use 64 worlds (32 mirror pairs),
  99% bootstrap over pairs (lens.ci).
- Compute: check the GPU is free (nvidia-smi) before any run over ~5 min.
  The CPU is fine for everything here. No cloud spend.
- Specimens: C1 rows roles/Ananke/pte/c1_rows/cells.jsonl.gz (load with
  c1b_run.load(cell_id)). M2 fresh champions are cached in
  ../spikes/out/champions_m2.json.

Threads: T-M2-2, T-M3-1, T-INS-1, T-TA-1, T-X-1, T-EXT-1 (one file each).
