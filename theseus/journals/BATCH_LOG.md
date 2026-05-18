# Theseus Batch Log

Per-batch human-readable journal. Modeled on Techne's SUBSTRATE_FIRE_LOG
pattern: structured entries per batch with generator selection, yield
metrics, anomalies, and decisions for next batch.

Structured records mirror this in `batches.jsonl` (one JSON object per
batch).

---

## Initial state — 2026-05-18

- Engine bootstrapped with 5 active generators: A1, B5, C1, D1, E1
- 35 stubs registered (a2-a5, b1-b4, c2-c5, d2-d4, e2-e5, f1-f4,
  g1-g5, h1-h4, i1-i4, j1-j3)
- Bandit: epsilon-greedy (epsilon=0.2)
- Corpus dir: `theseus/corpus/<batch_id>.jsonl`
- Journal dir: `theseus/journals/` (this file + batches.jsonl)
- Consumer: Ergon Learner is currently paused; records accumulate
  until ingestion resumes

See CHARTER.md for design doctrine; inventory.md for the 40-type
catalog; ROADMAP.md for tier progression.

---

## Bootstrap smoke run — batch-20260518T111102Z-f693cf

First end-to-end execution. 30-second wall budget, all 5 active
generators in round-robin.

- Duration: 0.0083 h (~30 s)
- Requested: a1,b5,c1,d1,e1
- Active:    a1,b5,c1,d1,e1
- Records: 104,114 (kills=42,998, confirmations=60,341, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=25,835, throughput=350,966,037/h, info_density=0.528, diversity=0.814, yield_score=0.0043, kills=18,630, conf=7,205, errs=0
- **b5** — records=25,835, throughput=146,466,141/h, info_density=0.586, diversity=0.792, yield_score=0.0047, kills=3,694, conf=22,141, errs=0
- **c1** — records=25,835, throughput=313,151,515/h, info_density=0.528, diversity=0.808, yield_score=0.0043, kills=18,643, conf=7,192, errs=0
- **d1** — records=25,834, throughput=30,928,633/h, info_density=0.592, diversity=0.791, yield_score=0.0047, kills=2,031, conf=23,803, errs=0
- **e1** — records=775,    throughput=10,568,181/h, info_density=0.200, diversity=0.965, yield_score=0.0020, kills=0,      conf=0,      errs=0

### Observations

- Volume target met immediately. ~3.5M records/minute extrapolated; orders of magnitude above any reasonable consumption rate.
- B5 has high confirmation rate (operators ARE mostly preserving as expected). Will downweight when measuring info-density-net-of-confirmations.
- D1 has ~92% confirmation rate on kill-neighborhood predictions: kills DO cluster spatially in the integer-invariant metric. This is a positive substrate signal.
- A1 and C1 produce near-identical kill/confirmation profiles (~72% kills). C1 is essentially A1 with parent-driven seeding — expected by design.
- E1 mines 775 literature claims per 30 s from the existing `aporia/docs/deep_research_batch*` corpus. UNVERIFIED by design; downstream sigma routing will assign verdicts later.
- Zero errors across 104K emissions. Round-robin + retry-budget pattern stable.

### Bug caught at smoke

- C1 and D1 initially returned None on a single transient failure, which the daemon promoted to "exhausted" for the entire batch. Patched both generators with internal 30-call retry budgets matching A1's pattern. Re-ran clean.

### Decisions for next batch

- Add bandit-driven generator rotation: run with `--bandit` flag to let the epsilon-greedy selector pick the next active set based on yield_score.
- Start filling Family-E stubs (E2-E5) — literature mining has the highest diversity score per emission and is token-free.
- Consider de-duplication harness for A1/C1 overlap: they produce structurally similar records; cross-generator record_id collision rate is the metric to watch.

---
