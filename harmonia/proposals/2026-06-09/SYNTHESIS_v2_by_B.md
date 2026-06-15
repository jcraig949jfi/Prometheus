# Synthesis v2 — three lanes closed; coordinate-collapse confirmed (theorem-backed)

**Author:** Harmonia_M2_B (cartographer)  **Date:** 2026-06-10
**Supersedes:** `SYNTHESIS_interim_by_B.md` (which had D pending).
**Status:** all three proposal lanes returned decisive results. The finding is now
a **working theory** (up from surviving-candidate), bounded by two named caveats.

## The finding, now confirmed across five substrates

Apparent structure in the substrate collapses onto something already present — a
cheap baseline, an already-available coordinate, or a saturated menu. Three proposal
lanes + two prior substrates, no shared scour/scoring code:

| Substrate | "Structure" | Collapses onto | Evidence | Tier |
|---|---|---|---|---|
| Erebos L2 | motif routing | per-plugin counter | parity proven (25 seeds) | confirmed |
| Theseus h2 | 87K kills, 44% of volume | the mechanism: ≤4 bits total | I(tag;Y\|pair)≈0; P(kill\|pair)∈[0.9988,1] | validated |
| Theseus a3 | 250 lattice voids | set-level marginal certificates | **product-measure theorem** + 3 independent reconstructions (panel C4: ~140k fuzz trials, 0 mismatches) + 250/250 content-verified certificates (verify v2) | validated |
| Apollo branch-c | evolved comps | fixed-menu zero-improvement tail | FP-003 fired 49/49, 429/480 | candidate (confound flagged) |
| Techne | search | bounded-menu wall | 90 zero-batches | prior |

D's result is the strongest form: a **theorem**, not a measurement. Under cross-product
(or independent) object pairing the joint of (inv_a, inv_b) is the product of marginals,
so every exact a3 void is *necessarily* a set-level fact about each catalog separately
(certified: SINGLETON_EQUAL / PARITY_CONSTANT / DIVIDES_GCD / INTERVAL_WIDTH). The 250
voids are 173 constant-side, 53 marginal-fact, 24 pigeonhole — **zero** cross-domain
identities, and any cross-domain reading is Pattern-30 by construction. The "richest
substrate-internal artifact" (kill-topography Finding 2) is trivial, provably.

## Two standing program recommendations are now refuted

- **Kill-topography rec #2** ("refactor h2 to recover 44% of kill volume"): the 44% is
  ≤4 bits of information total; no labeling recovers entropy the source never had. C's
  result. *44% of volume = ≈0% of information, now with better labels.*
- **Kill-topography rec #1** ("mine a3's lattice voids — candidate identities"): the
  voids are provably set-level marginal/selection facts (e.g. "catalog EC ranks ∈ {0,1,2}"),
  not identities. D's theorem.

Both were the program's two most-promising "discovery-facing" leads. Both are clean
kills. That is the failure landscape doing its job.

## The how-to the void converges on (north-star payoff)

The bottleneck is **coordinates**, not labels or search:
- Don't refine labels on a low-entropy kill stream (h2) — richer witness ≠ more signal
  when conditional information is zero.
- Don't trust structure that ties its baseline (Erebos) — gate via `costume_check`.
- Don't deepen a saturated menu (Apollo/Techne) — grow the menu / branch the lineage.
- Don't read cross-domain identity into product-measure voids (a3) — they are
  single-catalog facts; the discovery content, if any, is one catalog's marginal structure.

Unifying prescription: **generators need richer coordinate systems, not finer failure
labels or more search inside the current menu.** The Prometheus north star, reached from
the failure side.

## Corrections this round forced on MY proposals (falsifier falsified = system working)

D's theorem and sweep surfaced three errors in my own Proposals A/B. I accept them:

1. **Proposal B cell count was wrong:** I wrote "20,736 cells"; the lattice is
   6³·4² = **3456**. A factor-6 arithmetic error (propagated into the handoff + C/D
   prompts; D computed the correct 3456 and cross-checked the 144 op×rel projection at
   0/144 anomalies). Errata added to Proposal B.
2. **Proposal B's prescribed marginal-pairing null is DEGENERATE** for this claim shape:
   a product-measure statistic cannot be moved by re-pairing objects. D proved it and
   replaced it with set-level certificates + a pigeonhole/constant-side/laxity cascade.
   My prescription was wrong; D's is correct.
3. **Proposal A's v0 catalog can't express set-level baselines** (it counts labels; B
   needs set arithmetic). D injected B-specific baselines via `CATALOG[name]` and noted
   a `register()` hook would be cleaner. Accepted as Proposal A Sprint-1 follow-up.

4. **`costume_check` had a unique-key degeneracy** (D's 7-agent panel, 2026-06-10):
   on a unique-key claim, the generic `marginal_majority` is an identity label-copier
   and ties at 100% — certifying nothing. **Fixed 2026-06-15:** a degeneracy guard
   marks within-key aggregators `vacuous` on unique keys and returns
   `INCONCLUSIVE_DEGENERATE` for unique-key / imbalanced-default-comparator claims
   (regression test reproduces D's case; `baseline_costume.py` + parity suite green).
   The guard does NOT catch caller-side circular construction (a claim defined as its
   own marginal — Proposal E's Q4); that stays usage discipline.

D's real a3 gate used a custom comparator + set-level baselines (per the frozen
contract's `comparator` param). Per D's panel, the original 250/250 tie was
pre-ordained because `verify_certificate` v1 ignored its argument (repaired to
content-checking v2; still 250/250, now meaningfully). The honest a3 evidence is the
**theorem + 3 independent reconstructions + content-verified certificates** (table
above); the costume ladder (pigeonhole 9.6% < constant-absorber 78.8% < certificate
100%) is a **gradient**, not a gate verdict.

## Honest tier + remaining lenses (the bar is ensemble invariance)

**Working theory**, not durable. Open lenses:
- **Authorship-independence** (FP-001 review S1): code-independent is proven across the
  five substrates; author-independent is not — the same model wrote several pipelines, so
  "the substrate fools itself the same way" may be partly a shared-prior of the author.
  This is the single biggest threat to the invariance claim and cannot be closed at one author.
- **h2 law generality:** C's law is proven for h2; the cross-generator audit (≥3 generators,
  hunt a counterexample on a state-consuming generator like d1/kill-neighborhood) is owed.
- **Apollo FP-003 cause:** structural ceiling vs broken-gate/Goodhart not yet adjudicated
  (capacity confound flagged; promotion withheld).
- **Information ≠ utility:** all measure intrinsic information, not Learner loss.

## Lane close-out
- **E (registry):** thin atlas + live generative hunt; FP-003 → Apollo with confound
  discipline. FP-001 promotable to coordinate_invariant pending the Apollo 3rd-anchor +
  authorship-independence ruling.
- **C (h2):** Proposal E complete to validated terminal state; self-corrected past both my
  review points; `E_RESULTS_2026-06-10.md` tiers every claim. Cross-generator audit owed.
- **D (a3):** Proposal B complete to a theorem-backed kill; promoted `lattice_void_miner`
  (validator 14/14); corrected my proposal arithmetic and null methodology.

Net: the three-lane program did exactly what a falsification engine should — it killed the
program's two most-attractive leads with proofs, promoted three reusable primitives
(`baseline_costume`, `failure_primitives`, `lattice_void_miner`), and converged on a single
actionable prescription. Zero novel discoveries. The honest number is still zero — and the
instrument is sharper for it.
