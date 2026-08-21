# signature_index Occupancy — TT-Rank Measurement (Walk-1 first light)

**Instrument:** `prometheus_math.tensor_train.tt_rank_null_test` (forged cycle 002, 11 tests).
**Data:** `theseus/orchestration/signature_index.sqlite`, all 3,311 signature classes.
**Tensor:** occupancy counts, generator_id (56) × claim_kind (33) × verdict_class (4).
**Discharges HITL #6** (own artifact, per my stand; fold into Walk-1 doc later if preferred).

## Result

- Observed TT ranks `[41, 4]` at cutoff 1e-6; total 45.
- Fiber-shuffle null (200 samples, seed 20260821): mean 52.51, sd 0.95.
- **Observed total is ~7.9 sd BELOW the null; percentile 0.000.**
- Robust across cutoffs: 1e-3 → obs 16 vs null 22.1 (pct 0.000); 1e-2 → obs 13 vs null 18.7
  (pct 0.000).

## Reading, with the skeptic's caveat up front

The occupancy tensor is far more compressible than its coupling-destroyed null at every
resolution tried: **the (generator, claim_kind, verdict) axes are genuinely coupled** in the
accumulated ledger. That is the qualitative claim this measurement supports, and nothing more.

**What it does NOT establish:** most of that coupling is probably the SUPPORT pattern —
generators only emit certain claim_kinds (structural zeros), which by itself couples the first
two axes. The interesting substrate question is whether the VERDICT MIX varies with
(generator, kind) beyond what support explains. That needs the sharper conditional test:
restrict to occupied (gen, kind) cells and null only the verdict axis. Queued as the natural
next measurement; NOT claimed here (`feedback_narrative_resistance`: simplest explanation
first — and the simplest explanation is support structure).

Second bond rank = 4 (full) at fine cutoff: the verdict axis is not compressible at 1e-6 —
no low-dimensional verdict factor at fine resolution; at coarser cutoffs it stays 4 while the
first cut collapses 41 → 12 → 9, i.e. the compressible structure lives in generator×kind.

*— Techne loop, cycle 003.*
