# Dims 2 / 3 / 10 Audit-Prep — Techne (2026-05-11)

**Audience:** Ergon (consumer of this audit-prep), Aporia (routing), James (final scope)
**Origin:** Ergon discussion `ergon/learner/v1_0_plans/substrate_quality_for_learner_discussion.md` §1; Techne reply 2026-05-11; precondition for the gating sub-pattern (pilot LoRA → measured deficiencies → targeted audit).
**Scope:** Doc-only. No contract changes. No compute. Maps the 3 deferred substrate-side dims (2 = counterfactual completeness, 3 = calibration-tier provenance, 10 = cross-fire replication-status tagging) to (a) what the substrate currently emits, (b) what minimum generator-side instrumentation would look like, (c) whether any contract change is implied.

The 5 easy-fix dims (1, 4, 6, 7, 9) shipped at the generator level on 2026-05-11 in `prometheus_math/substrate_generation/learner_enrichment.py` + `survivor_seed_pool.py`; the 1 in-flight dim (8 — near-miss density) is in P5 spec; this doc covers the remaining 3.

---

## Posture: read-the-pilot-evidence-first

**The HARD-2 anti-gravitational-well discipline applies here too.** It is tempting to design instrumentation for all three dims at full theoretical fidelity right now. The pilot LoRA evidence will tell us which of these dims actually limit learnability and which are only theoretically nice. Designing the cheap instrumentation now (so the audit can branch fast when evidence lands) is correct; building the full instrumentation now (before evidence) is over-engineering.

For each dim below: minimum-viable instrumentation, NOT exhaustive coverage. Per-dim subsection answers three questions:

1. **What does the substrate emit today?**
2. **What's the minimum generator-side instrumentation that would address this dim WITHOUT a contract change?**
3. **What contract change would be needed to address it more deeply, and what evidence would justify that change?**

---

## Dim 2 — Counterfactual completeness

**Ergon's framing:** "considered-but-not-chosen alternatives are not emitted." A learner training on substrate output sees only the path actually taken (CLAIM → FALSIFY → PROMOTE), not the considered-but-rejected branches (e.g., "tried method A, fell out at the F1 gate at margin 0.03; tried method B, failed irreducibility check at depth 4; chose method C"). The Learner sees outcomes, not search.

### What the substrate emits today

`DiscoveryRecord` (per `prometheus_math/discovery_pipeline.py`) carries:
- `candidate_hash`, `coeffs`, `mahler_measure`
- `terminal_state` (REJECTED / SURVIVED / PROMOTED / ERROR)
- `kill_pattern` — single string for the FIRST kill that fired
- `check_results` — dict keyed by check name (reciprocity / irreducibility / catalog_miss / F1 / F6 / F9 / F11) with per-check `(ok, rationale)` tuples
- `kill_vector` — KillVector v2 with N components, ONE per falsifier; each component carries `triggered: bool` + `margin: Optional[float]` + `metadata: dict`

So the substrate ALREADY emits per-falsifier outcomes. What's missing is the **search-tree dimension**: when a candidate has two plausible verification paths and we picked one, the substrate doesn't record the path-that-wasn't-taken.

**For most current substrate emissions, there is no search-tree branching.** The discovery pipeline is mostly linear: phase-0 band check → phase-1 mechanical kills → phase-2 F-gate battery → terminal. The "considered but not chosen" pattern shows up in genuinely agentic flows (CLAIM-then-multiple-FALSIFY chains), which substrate-tester saturation showed are mostly aspirational right now (the kernel supports it; generators don't yet route through it).

### Minimum-viable generator-side instrumentation

Add a `considered_alternatives: List[ConsideredAlternative]` field to the GENERATOR's enrichment record (NOT to the substrate's DiscoveryRecord — that would be a contract change). Each `ConsideredAlternative` carries:

```python
@dataclass(frozen=True)
class ConsideredAlternative:
    method_name: str           # e.g. "f6_high_precision_recheck"
    consideration_reason: str  # e.g. "f6 margin within retest threshold"
    chosen: bool               # always False — these are NOT-chosen
    fallout_check: str         # which check would have caught it
    fallout_rationale: str     # what verdict the alternative would have produced
```

The generator emits these from a SMALL hand-curated set of "fork points" in the discovery pipeline (places where the generator chose one path over another):

1. **Catalog routing fork.** When `catalog_miss` shows multiple catalog hits in different sources (e.g. Mossinghoff hits AND OEIS hits), the generator currently picks the most authoritative; emit the not-chosen catalog as an `Alternative`.
2. **Precision-tier fork.** When mpmath polyroots returns a marginal result (margin near threshold), the generator currently picks the marginal verdict; emit "would have been retried at higher dps" as an `Alternative`.
3. **F-gate ordering fork.** F1/F6/F9/F11 currently fire in a fixed order. If F1 kills, we don't run F6/F9/F11. The generator could OPTIONALLY emit the "would have been F6's verdict" — but this requires actually running F6 on the kill, which doubles compute cost. **Recommend: only emit on a configurable sample rate (e.g. 5% of kills), to keep compute cost bounded.**

Cost: ~50-100 lines on the generator side, no substrate contract change. The `ConsideredAlternative` lives in the LearnerRecord adapter (sister to `kill_signature` from Tier-1).

### Contract-change path (only if pilot evidence demands)

If the pilot LoRA finds Dim 2 load-bearing, the deeper fix is a **substrate-grade `AlternativeWitness` primitive** that carries the full path-not-taken with substrate-grade verifiability (re-runnable replay info, content-addressed hash). This is a Tier-B subtype-class addition; ~1 contract-change-window of work.

**Pilot evidence threshold:** if the LoRA shows it can't recover the *reason* for a given verdict (e.g. asked "why was this candidate rejected?", produces unrelated rationale), Dim 2 is load-bearing — ship the contract change. If the LoRA recovers reasons cleanly without considered-alternative context, Dim 2 is not load-bearing — leave the cheap generator-side enrichment in place.

---

## Dim 3 — Calibration-tier provenance

**Ergon's framing:** "currently Ergon post-hoc." When a kill record is emitted, the substrate doesn't tag whether the verifier's claim is `analytically_proven`, `numerically_certified`, `ml_predicted`, or `unverified`. Ergon has been deriving this post-hoc by inspecting the falsifier name; this is fragile and doesn't generalize as new falsifiers land.

### What the substrate emits today

`KillComponent` carries `precision_dps: Optional[int]` + `method: str` + `convergence_status: str` + (as of T029 mini-window 2026-05-10) `margin_high_precision: Optional[str]` + `margin_precision_dps: Optional[int]`.

`MethodSpec` carries `independence_class: IndependenceClass` (the 13-value enum — sympy_symbolic_factorization, mpmath_numerical_root_finding, lmfdb_catalog, etc.).

**The calibration tier is implicit in `independence_class` but not explicit.** A reader can map (e.g.) `sympy_symbolic_factorization → analytically_proven` and `lmfdb_catalog → numerically_certified` (most LMFDB tables), but the substrate doesn't ship the mapping. Ergon's post-hoc derivation IS this mapping, applied at training-corpus-build time.

The substrate's `triangulation_protocol.py` ALREADY HAS a 5-value `MethodClass` enum: PROOF_BEARING, NUMERICAL, CATALOG, ROBUSTNESS, EXPLORATORY. And it maps `IndependenceClass → MethodClass` via the `INDEPENDENCE_TO_METHOD_CLASS` dict (the one fire #65 surfaced as load-bearing). This is **already half of Dim 3**.

The other half is the analytically_proven vs ml_predicted vs numerically_certified distinction inside the CATALOG class. LMFDB GL(3) root numbers are CATALOG (per `lmfdb_catalog`) but ml_predicted (per AA-019); LMFDB elliptic curve ranks are CATALOG and analytically_proven. The substrate cannot distinguish these without finer-grained catalog metadata.

### Minimum-viable generator-side instrumentation

Two-step:

1. **Surface the existing `MethodClass` mapping at emit time.** The Tier-1 LearnerRecord adapter (shipped 2026-05-11) already has `verification_tier: str` populated from `CoordinateChart.canonicalization.decidability_status`. Add a parallel `method_class: str` field populated from `INDEPENDENCE_TO_METHOD_CLASS[component.method_spec.independence_class]`. ~10 lines on the adapter.

2. **Per-catalog trust-tier table.** A lookup table `prometheus_math/substrate_generation/catalog_trust_tiers.py` mapping `(catalog_source, anchor_type) → trust_tier`. Examples: `("lmfdb_catalog", "elliptic_curve_rank") → "analytically_proven"`; `("lmfdb_catalog", "gl3_root_number") → "ml_predicted"`. The Tier-1 adapter consults this table when emitting a record whose check_results include a catalog hit. ~50-100 lines (table + lookup function) plus per-anchor curation as new catalogs come online.

Cost: ~70-150 lines on the generator side. NO substrate contract change. The trust-tier table is the same shape as `survivor_seed_pool` — curated data, easy to extend, lives outside the kernel.

### Contract-change path (only if pilot evidence demands)

If the pilot LoRA shows it can't distinguish "this kill came from a proven theorem" from "this kill came from an ML-predicted catalog entry" (and that distinction matters for training quality), the deeper fix is a substrate-grade `TrustTier` field on `KillComponent`. Additive contract change, similar shape to T029 multi-precision sister fields. ~1 mini-window of work.

**Pilot evidence threshold:** if the LoRA produces overconfident outputs on murmuration-class predictions (treating ml_predicted catalog hits as certified ground truth), Dim 3 is load-bearing — ship the contract change. If the LoRA appropriately discounts catalog-derived claims, Dim 3 is addressed by the cheap generator-side mapping alone.

---

## Dim 10 — Cross-fire replication-status tagging

**Ergon's framing:** "substrate doesn't currently tag 'this kill was replicated by 3 independent methods.'" When triangulation fires (substrate v2.3 §6.4 P6 + 2026-05-08 contract-change window mini-fixes), the result is captured in `TriangulationResult` but generators don't currently route through that. So a Learner training on substrate output sees per-record kills but cannot tell which kills are corroborated by independent methods vs which are single-method calls.

### What the substrate emits today

`TriangulationProtocol.evaluate(paths)` (in `sigma_kernel/triangulation_protocol.py`) returns a `TriangulationResult` with:
- `verdict: TriangulationVerdict` (5 values: INCONCLUSIVE_WAITING, INCONCLUSIVE_INSUFFICIENT_INDEPENDENCE, UPGRADED_TO_LOCAL_LEMMA, CONTRADICTED, REJECTED)
- `paths_run: Tuple[TriangulationPath, ...]`
- `independence_classes_covered: frozenset[IndependenceClass]`
- `method_classes_covered: frozenset[MethodClass]`
- `summary: str`
- `upgrade_eligible: bool`

The substrate primitive is fully shipped, hardened to mutation score 0.500+ (fire #55), and load-bearing for `ExclusionCertificate.strength = COMPLETE`. **Generators just don't route through it.**

This is the cleanest of the three deferred dims because the kernel infrastructure already exists. The gap is purely on the generator side: nobody calls `TriangulationProtocol.evaluate()` from within `DiscoveryPipeline.process_candidate()`.

### Minimum-viable generator-side instrumentation

Two patterns, both lightweight:

1. **Same-candidate triangulation.** When the generator computes Mahler measure via mpmath AND has a sympy-symbolic verifier available, run BOTH; assemble a `TriangulationPath` per method; pass to `TriangulationProtocol.evaluate()`; emit the resulting `TriangulationVerdict` as a field on the LearnerRecord. ~50 lines: build paths from existing check_results, call evaluate, attach verdict.

2. **Cross-candidate replication tagging.** When a kill_pattern recurs across N independent candidates (e.g. the same reducibility factor pattern across 50 unrelated polynomials), tag the LearnerRecord with `replication_count: int`. This is a generator-aggregation pass over a batch of records, not per-record instrumentation. ~30 lines + a small index data structure.

Cost: ~80 lines on the generator side. NO substrate contract change — `TriangulationProtocol` is already the right primitive; we just call it.

### Contract-change path (only if pilot evidence demands)

If the pilot LoRA shows it can't distinguish corroborated kills from single-method kills (and that distinction matters for training quality), no contract change is needed — instead, the right move is to MAKE THE GENERATOR CALL `TriangulationProtocol.evaluate()` more aggressively (sample more candidates through triangulation; raise the cost ceiling per-candidate). The fix is generator policy, not substrate primitive design.

**Pilot evidence threshold:** if the LoRA over-trusts single-method kills (treats one-method REJECTED as strongly as triangulated REJECTED), Dim 10 is load-bearing — ship the generator-side triangulation routing. The substrate primitive needs no further work.

---

## Summary mapping

The three deferred dims share a structural shape: **the substrate primitive (or its analog) already exists; generators are not routing through it.** No contract change is required for the minimum-viable instrumentation of any of the three.

The instrumentation cost is bounded:
- Dim 2: ~50-100 lines (ConsideredAlternative on LearnerRecord; sample-rate-bounded compute)
- Dim 3: ~70-150 lines (method_class on adapter + catalog_trust_tiers table)
- Dim 10: ~80 lines (call TriangulationProtocol.evaluate; cross-candidate replication tagging)

Total: ~200-330 lines of generator-side enrichment. All within file ownership of `prometheus_math/substrate_generation/`. No kernel changes. No new opcodes. HARD-2 anti-gravitational-well discipline preserved.

---

## What Aporia / Ergon should do with this audit-prep

**Aporia:** route this doc to Ergon's audit-response queue. The dims are mapped; the cost is bounded; the contract-change paths are explicit. Ergon's role: confirm the per-dim cheap-instrumentation design is what they need, and define which evidence-thresholds in the pilot LoRA would trigger upgrading any of the three to a contract-change ask.

**Ergon:** when the pilot LoRA evidence is in, this doc is the pre-decided menu. For each dim, the response is one of:
1. "Dim N looks fine in the LoRA results — keep the cheap instrumentation, don't escalate."
2. "Dim N shows up as load-bearing — ship the cheap instrumentation now (~X lines), measure again."
3. "Dim N still load-bearing after cheap instrumentation — ship the contract-change path described above."

The audit-prep doesn't pre-commit to which response; it pre-commits to the design space.

---

## Cross-references

- `ergon/learner/v1_0_plans/substrate_quality_for_learner_discussion.md` (Ergon's 10-dim discussion; this doc covers the 3 deferred substrate-side dims)
- `ergon/learner/v1_0_plans/pilot_lora_design_tier_1_corpus.md` (Ergon's pilot LoRA design; the gating sub-pattern this doc supports)
- `prometheus_math/substrate_generation/learner_enrichment.py` (Tier-1 generator-side enrichment for the 5 easy-fix dims, shipped 2026-05-11)
- `prometheus_math/substrate_generation/survivor_seed_pool.py` (Dim 7 implementation pattern; the trust-tier table for Dim 3 follows the same shape)
- `prometheus_math/discovery_pipeline.py` (current substrate emission point; what considered_alternatives would attach to)
- `prometheus_math/kill_vector.py` (KillComponent + 2026-05-10 multi-precision sister fields; trust-tier sister field would extend similarly if Dim 3 needs the contract change)
- `sigma_kernel/triangulation_protocol.py` (TriangulationProtocol — the substrate primitive Dim 10 instrumentation calls)
- `T-2026-05-10-ergon-to-techne-falsification-routing-substrate` (Ergon's coord ticket; this doc is one of the 4 audit responses)

— Techne, 2026-05-11
