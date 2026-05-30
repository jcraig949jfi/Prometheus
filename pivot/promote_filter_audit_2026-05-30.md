# Promote-Filter Audit — 2026-05-30
**Scope:** map the complete pathway by which a TheseusRecord becomes a "promoted record" (i.e., is counted toward `lifetime_discoveries_emitted`). Determine whether the filter is injectable for calibration testing, and surface any structural properties that affect the calibration design.

## The complete promote-filter

The pathway is shockingly thin. Tracing from `theseus/daemon.py` line 421:

```
maybe_emit_discoveries(records)  # theseus/orchestration/telemetry.py:163
└─ for r in records:
   ├─ if r.generator_id in NON_DISCOVERY_GIDS: skip
   ├─ w = training_weight(r)            # theseus/scoring/training_weight.py:207
   └─ if w >= 0.6: promote (top-20 per batch)
```

That is the entirety of the filter. There is no secondary review, no payload-content inspection, no per-domain plausibility check, no rediscovery cross-validation, no cross-batch deduplication for "high-quality" status. **A record is "promoted" iff `training_weight(r) >= 0.6` and its generator role isn't excluded.**

## What `training_weight` actually inspects

`training_weight(r) = base × verdict_mult × triangulation_bonus`, clamped to `[0,1]`.

The inputs touched, exhaustively:
- `r.claim_payload.get("relation", "")` — the relation **STRING** (`equal`, `equal_mod_2`, `divides`, `abs_diff_le_K`).
- `r.claim_kind` — the kind **STRING** (`bridge_extension`, `ratio_invariance`, `kill_neighborhood`, etc.).
- `r.verdict` — verdict enum value.
- `r.kill_pattern` — a string, searched for substring tokens `{specific, violated, boundary, F1_triggered, F6_triggered, F9_triggered, F11_triggered}`.
- `r.step_trace` — presence/absence boolean.
- `r.generator_id` — role-table lookup.

The inputs **NEVER touched**:
- The actual invariant values (`value_a_raw`, `value_b_raw`, etc.).
- The catalog objects (knot label, EC label).
- Whether the claimed relation holds, partially holds, or never holds.
- The numerical / structural content of the claim_payload beyond the `relation` string.
- Whether the record's relation is mathematically true.

## Structural property the filter has by construction

**The promote-filter is metadata-shape-driven.** It evaluates the *shape* of a record (which relation string, which kind string, which verdict, was triangulation done, what tokens are in the kill_pattern). It does not evaluate the *content* of the record.

This is not a bug — it's how Fire #141 designed it deliberately, on the theory that the metadata shape is an adequate proxy for Learner-training value. But it has a load-bearing implication for the calibration test:

**The existing filter cannot, even in principle, distinguish a Murasugi-true claim from a shape-identical artifact claim.** Both would be evaluated as `base × verdict_mult × triangulation_bonus`; if the metadata matches, both promote or neither does.

## What does and doesn't promote — closed-form

Common combinations and their resulting weight (no triangulation unless noted):

```
relation       verdict       kind                 base          weight   promotes?
equal_mod_2    SHADOW        a1                   0.65×0.30      0.195    no
equal          SHADOW        a1                   0.025×1.00     0.025    no
divides        SHADOW        a1                   0.35×0.70      0.245    no
abs_diff_le_3  SHADOW        a1                   0.60×0.55      0.330    no
bridge_ext     SHADOW        h4 +triangulation   0.55×1.0×1.3   0.715    YES
ratio_inv      SHADOW        a4 +triangulation   0.40×1.0×1.3   0.520    no
bridge_ext     REJECTED kp=violated +triang.    0.55×1.0×1.3   0.715    YES
kill_neigh     REJECTED kp=violated +triang.    0.40×1.0×1.3   0.520    no
```

The actual gate to promotion is **(kind == bridge_extension) AND (triangulation present) AND verdict ∈ {SHADOW, REJECTED-with-violated-kp}** — or some smaller set of analogous-multipliers paths. The 2,351 lifetime promoted records are dominated by this slice of metadata-space.

## Injectability

Yes. `training_weight(record: TheseusRecord) -> float` is a pure function on a TheseusRecord and importable as `from theseus.scoring.training_weight import training_weight`. The calibration script can:

1. Synthesize TheseusRecord instances with arbitrary claim_payload.
2. Compute `training_weight(r)` directly.
3. Apply the threshold and role check inline.

No daemon scaffolding needed. The promote-filter is callable from a 10-line wrapper.

## Implications for v0 calibration

The expected calibration outcome under the existing filter is forced by the audit:

- TRUE planted claims (Murasugi-form): if we emit them with `kind=bridge_extension` and `step_trace` populated, they **WILL** promote at high rate. But this is shape-driven, not content-driven.
- DECOY artifacts (parity tautologies, codomain-bounded): if we emit them with the same metadata shape, they **WILL ALSO** promote at the same rate.
- STRATIFIED-PERMUTATION: if we emit them with the same metadata shape, **WILL ALSO** promote at the same rate.

→ **The existing filter is expected to score outcome (E) "Pathological"** — promotes by shape regardless of content.

This isn't a calibration failure; it's a calibration **finding**. The calibration test, run against the existing filter, will demonstrate that the existing pipeline cannot be used as a discovery-detector — only as a metadata-shape classifier.

## Revised v0 design

The calibration script should run **TWO** filters and report both:

1. **Filter F1 — existing `training_weight`** (the audit subject). Expected to be shape-only.
2. **Filter F2 — a content-aware contender** that the calibration script DEFINES, which inspects the actual claim_payload values and checks the relation against the catalog. For Murasugi-form claims: check whether `3-genus ≥ ⌈|signature|/2⌉` is genuinely informative across the knot catalog (vs a "this happens to hold" coincidence).

The four-way matrix becomes an **eight-way matrix** (4 claim sources × 2 filters):

```
                   F1 existing    F2 content-aware
TRUE planted       expected high  expected high
DECOY              expected high  expected low
STRATIFIED-PERM    expected high  expected low
RANDOM-MARGINAL    expected high  expected low
```

If F2 produces the expected pattern, the calibration finding is:
**"The current filter is replaceable. A content-aware filter exists that distinguishes signal from artifact in this claim ecology."**

If F2 also produces shape-driven outcomes, the finding is:
**"The claim ecology itself encodes too little to support a content-aware filter under the current invariant menu — confirming the catalog-gravitational-well concern from GPT-5 Q4."**

Either way, this is signal.

## Refactoring required for v0

None for F1 — `training_weight` is already a pure callable.

For F2, the calibration script defines its own scorer. Likely needs:
- Catalog loaders (already importable from `theseus/generators/a1_catalog_cross_product.py`).
- A relation evaluator that checks whether a claim's relation holds with statistical significance vs catalog-marginal expectation. This is ~50 lines.

Total v0 calibration effort estimate revises **downward** from the 0.5–1.5 days I quoted earlier to **~1 day** for the Murasugi-relation slice, plus ~2 days for the remaining 4 relations.

## One additional audit observation

The promote-filter's `_verdict_multiplier` returns `0.6` for generic REJECTED records and `1.0` for REJECTED records whose `kill_pattern` contains the substring `"violated"`. After the h2 refactor, **all h2 kills now contain `"violated"` in their pattern** (e.g., `h2_triangulated_unanimous_three_genus_rank_methods_c_l_q_rejected` — no, that has `"rejected"` not `"violated"`).

Actually checking: post-refactor h2 patterns end in `_rejected`, not `_violated`. So they get the 0.6 generic multiplier, not the 1.0 specific one. This is a subtle interaction worth flagging: the h2 refactor may have inadvertently down-weighted h2 records in the promote-filter. Worth verifying empirically.

## Status

Audit complete. Filter is fully injectable. The calibration v0 design now has a clear two-filter structure. Ready to proceed to v0 build (option 2).
