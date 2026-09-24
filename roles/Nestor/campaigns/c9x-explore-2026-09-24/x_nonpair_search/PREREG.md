# X-NONPAIR-SEARCH -- EXPLORE lane (hypothesis-generating, not confirmation)

Experiment id `X-NONPAIR-SEARCH`, parent `S1A-REPLAY-FUNNEL`, mutation class **PHYSICS**
(single coordinate: when mutation happens). Written 2026-09-24, before any run.

**Why it exists.** S1-A found that in all 907 FREE-policy random-start runs no birth
ever happened, and this substrate mutates only at a birth. So those populations never
varied. `PAIR_EXECUTION`, the only physics that produced replicators, mutates every
paired organism every epoch. The 72-hour contrast between pair and non-pair physics is
therefore a contrast between a search and no search.

**Question.** When every living organism is mutated in place each epoch at its cell's
own mutation rate, do the four non-pair physics (ENDOGENOUS_COPY, ENDOGENOUS_PARTIAL,
CONSTRUCTIVE, OVERWRITE) produce births, faithful births and evidence-backed replication
that they do not produce otherwise?

**Design.**
- Cells: the first 12 tier-M cells per physics in `REPLAY_SELECTION.json` order (48
  cells). That selection was deterministic and stratified over self_location x
  copy_primitive.
- Two arms per cell on a shared fresh seed (9,700,000 + cell index, not a predecessor
  seed):
  - **CONTROL**: the Cycle-9 substrate unchanged;
  - **INPLACE**: before each epoch, every living organism's genome is replaced by
    `_mutate(genome)`, the world's own operator at the cell's rate.
- Tier M, full length. The substrate is the frozen Cycle-9 code imported read-only; the
  treatment is a subclass (`run_x.py`).

**Readouts, per run:**
- `births_endogenous` (any accepted birth);
- faithful births: `replication_events + births_similar_no_write` (fidelity >= 0.90);
- `replication_events` (fidelity >= 0.90 AND the parent placed >= half the bytes);
- `max_causal_replication_depth`.

**Classification rule, declared now:**
- **SIGNAL**: INPLACE shows evidence-backed replication in >= 3 cells where CONTROL shows
  none.
- **WEAK_SIGNAL**: no SIGNAL, but INPLACE has accepted births in >= 5 more cells than
  CONTROL, or any faithful birth where CONTROL has none.
- **CLEAN_NULL**: otherwise.

Any result is exploratory. A SIGNAL would earn a fresh frozen CONFIRM child, with new
cells and seeds and a matched in-place-mutation-without-births control. It is not a
claim.
