# CAMPAIGN X — TERMINAL: **REDESIGN**

**Pass 3 of 3.** The frozen split was touched once, on 50 positives, and the terminal state was
computed and written to `retrieval_frozen_results.json` **before** any mechanism diagnostic ran.
The signature was not redefined: `run_retrieval_frozen.py` *imports* `run_retrieval_dev.py` and
calls its `signature`, its pool construction, its normalisation constants and its `rank_of`, so
the representation and metric are byte-identical to pass 2 by construction rather than by
assertion.

## Frozen results — raw beside derived

Pool 20,358. 50 frozen positives. Chance top-10 = 0.00049.

    L0 exact ceiling      50/50                                    (circular — sanity only)
    L1 operator-aware     top-1 34/50 = 0.680   top-10 40/50 = 0.800   MRR 0.741  median 1
    L2 operator-agnostic  top-1  0/50 = 0.000   top-10  4/50 = 0.080   MRR 0.038  median 1,383
    baseline raw terms    top-1  0/50 = 0.000   top-10  4/50 = 0.080   MRR 0.025  median 598
    baseline shuffled     top-1  0/50           top-10  0/50           MRR 0.0003 median 9,734
    baseline growth/mag   top-1  0/50           top-10  0/50           MRR 0.008  median 777

Decomposed, with the trivial control separated as required:

    L2 shift (trivial control)   3/10 = 0.300   median rank 56
    L2 four real operators       1/40 = 0.025   median rank 1,927
      diff 1/10 · partsum 0/10 · binomial 0/10 · moebius 0/10

    L1 four real operators       top-1 33/40 = 0.825
    L1 shift control             top-1  1/10 = 0.100

Matched-negative false retrieval (head-to-head, immune to pool size):
signature **15/50 = 0.300**, raw terms **14/50 = 0.280**, chance 0.500.

## D1–D5, read first and unmodified

- **D1** signature beats both baselines — **NOT fired.** L2 top-10 0.080 equals raw terms 0.080.
- **D2** raw terms do equally well → the signature adds nothing demonstrable — **FIRED**, and
  exactly: 4/50 versus 4/50. On median rank the signature is *worse* (1,383 vs 598).
- **D3** development works, frozen fails → overfitting — **NOT fired**; its precondition
  (development L2 ≥ 0.30) was never met, because development did not work either.
- **D4** only shift retrieves — **not fired on the numeric cut, and that cut is disclosed below.**
- **D5** nothing retrieves → KILL — **NOT fired.** L2 0.080 is ~160× chance.

**Disclosed methodological weakness, stated because it cuts against me:** D1–D5 were preregistered
in *qualitative* language with no numeric thresholds. I supplied thresholds at adjudication time in
`run_retrieval_frozen.py`, which is thresholds-invented-at-read-time — the failure mode the doctrine
warns about. D2's firing is robust to it (4/50 vs 4/50 is exact equality; any threshold fires it).
**D4's non-firing is not robust**: shift retrieves at 12× the real-operator rate (3/10 vs 1/40),
which is D4's qualitative claim, and only my invented 0.50 cut suppressed it. The honest reading is
that D2 and D4 both point the same way, and neither points to KILL.

## The confound rule, applied after — branch **CONFOUNDED**

Pre-committed in `RETRIEVAL_dev_2026-08-22.md` before frozen was ever touched: frozen L1 top-1
≥ 0.95 makes the L2 read clean; ~0.75 makes it confounded.

**Frozen L1 top-1 = 0.680.** CONFOUNDED fires. It fires under the most favourable decomposition
too — real-operator L1 top-1 is 0.825, still far below 0.95 — so no reading of the split rescues
the instrument. The rule is honoured as written; rewriting it now, having seen the numbers, is
precisely the move it existed to prevent.

## Mechanism: the 16 L1 misses are two different failures, and only one is ours

Run after the verdict was on disk, and unable to change it. Of 16 frozen L1 misses:

    source outranked the true target   10/16    (shift 9, moebius 1)
    rank-1 WAS the source itself        7/16
    rank-1 was an unrelated distractor  8/16    <-- genuine representational collisions

So the aggregate collision rate of 0.32 is **two defects pooled, and they need opposite fixes**:

1. **Benchmark construction artifact (8 of 16).** The query's own source sequence is a member of
   the retrieval pool. For a near-identity operator like `shift`, the image resembles the source
   more than it resembles the target, so the source wins. This fully explains why L1 on the trivial
   control (1/10) is *worse* than on the real operators (33/40) — a result that is backwards under
   any resolution story and was the thread worth pulling.
2. **Genuine representational collision (8 of 50 = 0.16).** An unrelated distractor outranks a
   sequence the query is *exactly equal to* over ≥ 20 terms. This is a real resolution deficit.

## Terminal state and what it licenses

**REDESIGN** — the benchmark stands, the representation does not. Explicitly **not KILL**: the
preregistered kill branch D5 did not fire, and the instrument is confounded, so this campaign is
not entitled to conclude that behavioral signatures cannot recover hidden relations. It is entitled
to conclude, and does, that **this** 33-feature signature adds nothing over raw terms.

Deficits a successor campaign must fix, in priority order:

1. **Exclude the query's own source from the candidate pool** — a one-line fix that removes 8 of 16
   L1 misses and is a benchmark bug, not a finding.
2. **Resolution.** 33 z-scored features under Euclidean distance cannot separate 20,358 objects;
   16% of exactly-equal queries collide. Either a higher-dimensional signature or a learned metric,
   with L1 top-1 ≥ 0.95 as the *entry gate* — a representation that fails the necessary condition
   may not be tested on the sufficient one again.
3. **Only then** re-read L2. The operator-agnostic claim remains untested, not refuted.

**Not started this pass.** Campaign discipline caps live threads at 2 and a terminal state does not
license its own successor.

## Campaign X TERMINAL: REDESIGN
