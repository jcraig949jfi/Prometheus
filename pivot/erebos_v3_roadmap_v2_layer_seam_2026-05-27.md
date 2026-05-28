# Erebos v3 Roadmap v2 — Layer 1 / Seam / Layer 2 re-stratification + Sprint-1 redesign

**Date:** 2026-05-27
**Status:** Supersedes the Phase 1 / Phase 2 / Phase 3+ sequencing in `pivot/erebos_v3_synthesis_2026-05-27.md` §9 and `pivot/erebos_v3_amendment_dr_synthesis_2026-05-27.md` §6. Same kill conditions (v3 §6); re-stratified work-queue.
**Reading order:** `pivot/erebos_doctrine_v1_2026-05-27.md` first, then this doc.

---

## Why a re-stratification

The Phase 1 work in the prior roadmaps was a flat list of 13 items. Doctrine v1 names a two-layer architecture connected by a seam. The work-queue cleaves cleanly along that architecture:

- **Phase 1A** — Layer 1 retrofits (apply DR-recommended traditional methods to existing loaders; sharpen the generators)
- **Phase 1B** — Seam construction (what crosses the boundary; the gate that decides eligibility)
- **Phase 1C** — Layer 2 primitives (the cross-emission accumulator's actual operations)
- **Phase 2** — Sprint-1 self-falsification (tests the SEAM, not Layer 1 or Layer 2 in isolation)
- **Phase 3+** — conditional on Sprint-1 pass

This isn't different work from the prior roadmap. It's the same work, sorted by which layer each item lives in. The sorting clarifies what's traditional-and-well-understood (1A) vs deliberately-novel (1C) vs the architectural commitment that bridges them (1B).

## Phase 1A — Layer 1 retrofits (traditional, well-understood, sharpens generators)

Each retrofit takes one existing plugin's composition loader and replaces its current statistical method with the DR-recommended upgrade. Per-emission falsification gets sharper; failure data gets less noisy; the seam carries higher-quality artifacts to Layer 2.

| ITER | Plugin | Layer 1 upgrade |
|---|---|---|
| 31 | G02 contrast | Westfall-Young max-T over single-shuffle permutation (DR batch 1) |
| 32 | G10 boundary | BOCPD (Bayesian Online Change-Point Detection) over max/mean smoothness ratio (DR batch 2) |
| 33 | G23 asymptotic | bootstrap CI on the multi-law fit (DR batch 4) |
| 34 | G11 family | Monte Carlo permutation G-test over Pearson chi² on sparse cells (DR batch 2) |

These are the four highest-traffic Layer-1 retrofits. Each upgrade is a known-good statistical method swap — low architectural risk, high data-quality lift. After Phase 1A, four of the substrate's most-fired plugins emit higher-quality artifacts at the seam.

**Important:** Phase 1A is NOT optional. Sharp generators are how Layer 2 gets clean signal. The doctrine doc explicitly endorses Layer 1 work: "Use the BEST traditional methods available."

## Phase 1B — Seam construction (the architectural commitment)

The seam is where Erebos differs from every other ML system. These primitives define what crosses from Layer 1 to Layer 2 and gate which failures are eligible to do so.

| ITER | Primitive | What it ships |
|---|---|---|
| 35 | `_residue_eligibility.py` | 4-criterion gate (changes routing distribution / localizes boundary / falsifies prior signature / adds tensor rank). Failures that meet none → exhaust log, not kill_ledger. |
| 36 | Per-field consumer audit | Every field on `ComposedClaim` must have a downstream consumer (plugin reads it, loader routes on it, test asserts on it). Fields without consumers stripped. Currently 5 of 8 v3 fields are pending consumers. |
| 37 | Daemon-wire: cost-instrumentation | `time.perf_counter()` wraps `plugin.generate()` and loader execution; `generation_cost_seconds` + `falsification_cost_seconds` populated per emission. Enables Sprint-1 value_per_tick baseline. |
| 38 | Daemon-wire: kill_pattern routing | The daemon's next-plugin selection consults `kill_pattern_registry.routing_action_for(kp)` when a loader emits a directional kill_pattern. Replaces static round-robin priority. |
| 39 | Residue revocation mechanism | When downstream evidence falsifies a prior kill_pattern's observable_signature, the prior record is marked superseded. The ledger maintains a revocation chain. |

After Phase 1B, the seam is operational. Every Layer-1 emission crosses through eligibility + cost-instrumentation; every Layer-2 routing decision consults the kill_pattern registry; the substrate can falsify its own prior emissions.

## Phase 1C — Layer 2 primitives (where Prometheus is alone in the wilderness)

These primitives make the cross-emission accumulator more than a write-only log. They are the tensor-algebra layer.

| ITER | Primitive | What it ships |
|---|---|---|
| 40 | Motif extraction | Cluster kill_ledger records into reusable motifs via embeddings on (composition_payload, kill_pattern, parent lineage). Motifs become the "unit of inheritance" (Reasoning-Ladder Q4). |
| 41 | Kill tensor v0 | Factorize accumulated emissions by (generator × domain × invariant × confusion_class). Tucker / CP decomposition. Identify low-rank kill modes. |
| 42 | Null-space detection | Identify regions of high search density and ZERO PROMOTED emissions — exploration-deficit regions. (Reasoning-Ladder Q19.) |
| 43 | Rank-expansion test | When a new plugin (or new variant) is registered, measure whether it adds rank to the kill tensor or merely adds duplicate rows. Plugins that fail this for 3 consecutive iterations are flagged for merge / retire (per v3 §4.2 degeneracy audit). |
| 44 | Cross-domain transfer primitive | Map residue from one domain (Mahler) to another (BSD MVP). Test whether Layer-2 routing learned in one domain transfers. |

Phase 1C is the most architecturally novel work. Each primitive is a Layer-2 operation that the conventional ML stack has no equivalent of.

## Phase 1 enablers (parallel to 1A/1B/1C)

| ITER | Enabler | Role |
|---|---|---|
| 35 (parallel) | BSD MVP loader | First non-Mahler composition loader. Required for Sprint-1 ablation A8 (cross-domain). Per v3 §4.6 priority-elevation. |
| 36 (parallel) | Earned-tier protocol | declared_tier / executed_tier / observed_tier / downstream_tier on every plugin. Routing uses observed_tier, not declared_tier. (v3 §4.3.) |

These can run in parallel with 1B because they don't share dependencies.

## Sprint-1 redesign (Phase 2, ITER-45 → ITER-54)

**The hypothesis Sprint-1 tests:** *Layer 2 adds measurable value on top of Layer 1.* A substrate running the same Layer-1 statistical tests but WITHOUT the Layer-2 accumulator (no kill_ledger query, no routing-via-residue, no parent_record_ids consumed) performs strictly worse than one WITH the accumulator, on metrics the accumulator was designed to optimize.

**Pre-committed kill rule:** if Sprint-1 fails ≥ 4 of the 10 experiments, the architecture is paused per v3 §6.

The 10 experiments (revised — dropped A10 frontier-LLM-comparison; added rank / motif / transfer / residue-revocation tests):

| # | Experiment | What it tests | Decision rule |
|---|---|---|---|
| A1 | MEMORY vs NO_MEMORY ablation | Layer 2 contributes vs no Layer 2 | yield drop > 30% in NO_MEMORY → Layer 2 is load-bearing |
| A2 | Per-record causal attribution | Which specific Layer-2 records drove which routing decisions | ≥ 50% of routing decisions trace to specific records → Layer 2 is queried, not just stored |
| A3 | Kill-pattern predictive power | Train on early ledger; predict late kill_patterns out-of-sample | held-out F1 > random baseline → Layer 2 encodes structure |
| A4 | Routing-via-residue lift | EIG of routing decisions when consulting kill_ledger vs round-robin | EIG ratio > 1.2 → routing residue is actionable |
| A5 | Redundancy reduction over iterations | Mean ticks-to-novel-emission as ledger grows | downward trend → memory reduces wasted exploration |
| A6 | Cross-generator transfer | Kill_patterns from G02 predict G17 outcomes | held-out predictive lift > 0 → kill semantics generalize |
| A7 | Stable low-rank tensor structure | Effective rank of kill tensor over time | rank stabilizes (not linear in N) → real geometry, not duplicates |
| A8 | Cross-domain residue transfer | Layer-2 residue from Mahler routes BSD MVP loader more efficiently than null residue | wall-clock to first PROMOTED in BSD: with-residue < without-residue → cross-domain transfer real |
| A9 | Residue revocation correctness | When downstream falsifies a prior kill_pattern, the revocation mechanism marks it superseded AND downstream routing changes | ≥ 80% of revocations propagate to subsequent routing → revocation is causally connected |
| A10 | Motif emergence vs random | Extracted motifs (Phase 1C ITER-40) match human-recognizable structural classes at rate > random clustering | motif-to-class purity > 0.4 → motifs are meaningful |

**Replaced from the v3 original Sprint-1:** A10 was previously "compare Erebos to one frontier LLM asked to propose hypotheses directly." This was a gravity-well experiment (asks "does Erebos beat an LLM at the LLM's game?"). The right comparator is "Erebos with Layer 2 vs Erebos without Layer 2" — same Layer 1, isolate the architectural claim. Frontier-LLM comparison would never be informative because the LLM's training-corpus density on conventional mathematics makes it a poor proxy for Prometheus's actual value claim.

## Phase 2 wrap (ITER-55) — kill condition decision

Pre-committed:
- ≥ 8 of 10 pass → architecture justified; proceed to Phase 3+
- ≤ 6 of 10 pass → architecture paused; reopen assumptions
- 7 of 10 → narrow review; identify which experiment failed and why; iterate that specific subsystem before continuing

## Phase 3+ — conditional

If Sprint-1 passes:
- Retrofit the remaining 10 active plugins to use the seam primitives (predicate_handle, SurvivalCurve, eligibility gate)
- Ship OEIS + NF MVP loaders for additional cross-domain triangulation
- Composition-payload schema mobility deeper than predicate_handle (M5 candidate work)
- Learner integration spec (now informed by Sprint-1's actual loss-function signal)
- ATP backend exploration (v3 §8 open question 4)

## Sequencing constraints

```
1A.31 G02 Westfall-Young  ──┐
1A.32 G10 BOCPD           ──┤    ┌── 1B.37 cost-instr ──┐
1A.33 G23 bootstrap CI    ──┤    │                       │
1A.34 G11 G-test          ──┤    │   1B.38 routing wire ──┤
                            │    │                       │
1B.35 _residue_eligibility ─┼────┤                       ├── Phase 2 Sprint-1 (A1-A10)
1B.36 per-field audit      ─┘    │   1B.39 revocation ──┤
                                  │                      │
                                  └── 1C.40 motifs ──────┤
1C.41 kill tensor v0  ────────────────────────────────────┤
1C.42 null-space      ────────────────────────────────────┤
1C.43 rank expansion  ────────────────────────────────────┤
1C.44 cross-domain    ────────────────────────────────────┤
                                                          │
Parallel enablers:                                        │
  - BSD MVP loader (ITER 35)  ────────────────────────────┤
  - Earned-tier protocol (ITER 36)  ──────────────────────┘
```

Phase 1A + 1B + 1C can largely run in parallel within each ITER block. Sequencing is dependency-driven, not artificially sequential.

## Estimated calendar

- Phase 1A (4 retrofits): ITER-31 → ITER-34, ~4 iterations
- Phase 1B (5 seam primitives + 2 enablers): ITER-35 → ITER-39, ~5 iterations
- Phase 1C (5 Layer-2 primitives): ITER-40 → ITER-44, ~5 iterations
- Phase 2 Sprint-1 (10 experiments): ITER-45 → ITER-54, ~10 iterations
- Phase 2 decision (ITER-55): 1 iteration

Total to Sprint-1 verdict: ~25 iterations from now (ITER-31 → ITER-55).

## What this roadmap explicitly preserves from v3

- v3 §6 kill conditions (5 pre-committed) — unchanged
- v3 §8 open questions (6 still open) — unchanged
- v3 §4.10 finding reclassification — preserved with the doctrinal correction that reclassification's wrong premise was the publication ladder, not the demotion itself
- Phase 0 primitives (9 shipped at ITER-21 → ITER-30) — all stand
- The 22 DR outputs — preserved for Phase 3+ plugin retrofits

## What this roadmap explicitly rejects from v3

- The Phase 1 / Phase 2 / Phase 3+ flat sequencing without layer-architecture breakdown
- Sprint-1 experiment A10 (frontier-LLM comparison) — gravity-well, replaced with motif-emergence test
- Implicit assumption that "more good statistics in Layer 1" is the only kind of improvement — corrected to: Layer 1 retrofits AND Layer 2 primitives are BOTH load-bearing, and the seam is where the architectural commitment lives.
