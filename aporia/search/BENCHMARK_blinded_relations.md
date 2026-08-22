# BLINDED RELATION RECOVERY — benchmark specification

**Campaign X, pass 1 of 3** (instrument + preregistration). Aporia P108, 2026-08-22.
Builder: `build_blinded_benchmark.py`; growth matching: `growth_battery.py` (P21's calibrated
classifier, now imported rather than admired). **No retrieval has been run and no signature has
been designed.** That separation is the experiment.

## Why this exists

The loop has a competent adjudicator and an untested search policy. Before pointing anything at
the 68,770 unreferenced "Sleeping Beauty" sequences, we test whether behavioral signatures can
recover relationships that are **already known and deliberately hidden** from the retrieval
path. If concealed *known* structure cannot be rediscovered, there is no basis for believing
unknown structure will be.

## Preregistered design

**Operators (five, exact, machine-verifiable from terms alone):** first differences; partial
sums; binomial transform; Möbius transform; and shift as the deliberately-trivial control.

**Thresholds, fixed before the scan:** a pair counts only if the operator holds EXACTLY on
≥ 20 overlapping terms; 25 positives per operator; source pool restricted to sequences with
≥ 25 terms.

**Built:** 266,122 eligible sequences → 230,694 non-degenerate source pool → **125 positive
pairs (25 per operator)** and **124 matched negatives**. Split **75 development / 50 FROZEN**,
written to `benchmark_frozen_split.json` in this pass.

**Blinding:** the retrieval path may read `benchmark_terms.json` only — term vectors keyed by
opaque ids (`S000123`). A-numbers live in `NOT_FOR_RETRIEVAL_blindmap.json`. `names.gz` is
never opened by the builder, so titles and cross-references cannot leak.

**Matched negatives:** each positive's true target is paired with a decoy of the same growth
class (P21's battery), within one order of magnitude and 8 terms of length — so a retrieval win
cannot be explained by "the right answer was the only object of that size."

## BUILD-1 FAILED TOTALLY — and that is this pass's finding

The first build produced 125 positives of which **125 were the same source sequence mapping to
all-zero targets.** The tell was in the pair counts: 323 / 323 / 322 / 321 / 323 across five
structurally unrelated operators. Near-identical counts across unrelated operators is not a
result, it is a contamination signature — and the mechanism is that **a degenerate object
satisfies every operator simultaneously**, so it saturates every quota before any real
relationship is examined. The all-zeros sequence is a fixed point of differences, partial sums,
binomial transform, Möbius transform, and shift at once.

New class for the tier's catch ledger: **DEGENERACY-SATURATED-BENCHMARK**. It belongs to the
genericity/sampling family alongside P31's proportional-point sampler, but is nastier: the
degenerate cases are *correct* instances of the relation, so no per-pair verification catches
them. Only the cross-operator count pattern gives it away.

**Filters added and preregistered before the rebuild:** ≥ 8 distinct values in-window; not
eventually constant; the operator *image* must also be non-degenerate; ≤ 2 pairs per source and
per target per operator; source pool shuffled so dictionary order cannot dominate.

**Rebuild result:** zero all-zero targets, 112 distinct sources and 122 distinct targets across
125 positives, growth classes spread (POLY 24 / EXP 38 / ABSTAIN 63).

*Note on rebuilding a "frozen" split:* legitimate here precisely because no retrieval has run
and no signature exists — nothing could have been fitted to it. Rebuilding it after seeing
retrieval numbers would be misconduct; this file records the ordering so that distinction is
checkable.

## Preregistered pass-2 branches (retrieval will be judged against these only)

- **D1** — signature retrieval materially beats BOTH the raw-term baseline and the
  shuffled-signature baseline on FROZEN positives → the behavioral representation has
  demonstrated retrieval value.
- **D2** — raw terms do equally well → the signature adds nothing demonstrable.
- **D3** — development works, frozen fails → overfitting.
- **D4** — only shift/subsequence retrieves → the map detects superficial equivalence, not
  structural relation.
- **D5** — nothing retrieves → **KILL** the Sleeping Beauties search.

Metrics fixed now: top-1 recall, top-10 recall, mean reciprocal rank, per-operator recall, and
matched-negative false-retrieval rate. Baselines fixed now: raw-term nearest neighbour,
shuffled signature, and growth/magnitude-only signature.

## Campaign checkpoint

**Campaign X, pass 1 of 3 — checkpoint at pass 3.** No terminal state is due yet. Pass 2 runs
retrieval on development only; pass 3 touches the frozen split once and emits
ADVANCE / REDESIGN / PARK / KILL.

---

## CAMPAIGN X TERMINAL (pass 3, 2026-08-22): **REDESIGN**

Frozen split touched once, 50 positives. **D2 fired exactly** — operator-agnostic retrieval
4/50 top-10, raw-term baseline 4/50 top-10, and the signature worse on median rank (1,383 vs 598).
D5 (KILL) did **not** fire. The confound rule pre-committed in `RETRIEVAL_dev_2026-08-22.md` fired
**CONFOUNDED** at frozen L1 top-1 = 0.680, so no kill was permitted.

Full adjudication, the disclosed threshold weakness, and the L1 miss mechanism (8 of 16 misses are
a source-in-pool benchmark artifact, 8 of 50 are genuine collisions) are in
`CAMPAIGN_X_TERMINAL_2026-08-22.md`. The benchmark stands; the representation does not.
The operator-agnostic substrate claim is **untested, not refuted**.
