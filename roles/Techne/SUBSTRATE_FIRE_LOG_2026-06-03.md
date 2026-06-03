# Techne Substrate Fire Log — 2026-06-03

## Calibration v3 — independent-null falsification of the v2 corpus sweep

**Context on entry.** Theseus bandit loop paused at Fire #236 (92 consecutive
0-promoted). GPT-5 2026-05-30 review forced the calibration pivot: prove the
substrate recovers known structure at better-than-null rates before resuming.
F2 content-aware filter calibrated on synthetic controls (v0 Murasugi, v1
EC-torsion) and shipped observation-only (`theseus/scoring/content_aware_promote.py`).
v2 corpus sweep then reported ~18.5% group-level contrast on real data while
flagging (caveats #2/#3) that most was probably selection bias. **The v2 claim
had not yet been falsified.** Per calibration-discipline mandate, the
independent null runs before the claim escapes upward.

**Probe built.** `theseus/scripts/calibration_v3_nonmutated.py`. A record is
mutation-derived iff it carries a `parent_record_id`; excluding them isolates
independently-sampled records. Added an optional `generator_id` filter to
isolate a1 (pure uniform `rng.choice`). Smoke at 200K before the 30M full scan
(smoke-before-full-scale rule). Matched v2's exact sorted-file / oldest-N window
for comparability.

**Result (30M-record window).**
- v2 analyzed 1,068 groups (≥50 all-record). Only **96** have ≥50 independently-
  sampled records → ~91% of v2's group diversity is mutation-generated K-variants.
- v2's named strongest residual (`knot/trace_field_class abs_diff_le_0 ec/torsion`)
  is **100% mutation-derived** — collapses to 0 non-mutated records.
- All-gen non-mutated: 61/96 promote, contrast up to 0.27 — but `sub_hold` 22–40%
  vs `null` often 0.00%, mechanically impossible under uniform sampling. Signal
  comes from non-a1 selection/transform generators.
- **a1-only (uniform, the unbiased baseline): 0/96 promote, max contrast 0.023,
  `sub_hold ≈ null` everywhere.** a1 has 0 records with a parent.

**Verdict.** No cross-catalog knot×EC coupling under unbiased sampling. v2's
apparent corpus signal was selection bias in two layers (mutation inheritance +
non-a1 generator construction), both stripped by v3. F2's calibration is
genuine: recovers planted (v0/v1), reports ~zero on the honest real null. The
92-consecutive-0-promoted streak is **correct refusal to promote artifacts**,
not a bounded-menu wall in this region.

Full verdict: `pivot/calibration_v3_VERDICT_2026-06-03.md`.

**Owed next probe (filed, not yet run).** Per-generator `sub_hold` vs null on the
96 groups — name which non-a1, non-mutation generators inject the Layer-2 bias
(targeting vs raw-vs-transformed value mismatch, v2 caveat #2), and decide
whether their SHADOW verdicts belong in the content-aware corpus at all.

**Doctrine:** calibration-discipline (independent null before claim) ✓;
counter-baseline discriminator (a1 uniform null) ✓; permutation/independent-null
mandatory ✓; assume-wrong / kills-are-the-output ✓; HARD-5 no-bridge-story ✓.

---

## Calibration v3c — per-generator audit: the signal was a claim-shape category error

Ran the owed next probe. `calibration_v3c_generator_audit.py` computes per-
generator group-level contrast with a WITHIN-generator re-pairing null (each
generator's own counter-baseline). 30M window, non-mutated only.

**Result — bias injectors named:**
- g4 reflection-duality: 91/96 groups promote, mean contrast 0.619, max 1.000, n=2.89M
- g5 scale-invariance: 78/80, mean 0.639, max 1.000, n=21K
- a3 functional-identity: 34/96, mean 0.091, max 0.332, n=3.20M
- f4 / f2 / f3 / a1 (direct-relation): 0/96, mean contrast <= 0.009

**Mechanism (confirmed in code, `g4_reflection_duality.py:72-78`):** g4/g5/a3
emit payloads in the SAME (value_a, value_b, relation) shape as a1's direct
claims, but their SHADOW/REJECTED verdict answers a DIFFERENT predicate —
g4: "rel is sign-reflection-invariant"; g5: "rel is scale-invariant"; a3:
"rel(f(a), g(b)) holds on transformed values". F2's group key conflates them
with direct records, then scores all against the raw-value null. Reflection-
symmetry is common exactly where the raw relation is False on both sides ->
sub_hold~100%, null~0% -> contrast pins at 1.000. **Category error, not coupling.**

**Production fix shipped this change set.** `content_aware_promote.py` gains
`is_direct_relation_record()` + `META_RELATIONAL_GENERATORS = {g4,g5,a3}`.
`maybe_promote_by_f2` and `build_value_pools_from_records` now skip meta-
relational records, so the daemon's observation-mode F1-vs-F2 delta (doctrine
criterion #5) is honest. Resolution order is backwards-compatible: honor an
explicit `claim_payload.predicate_kind` if present, else fall back to
generator_id. 5 new guard tests; full suite 15/15 green.

**Forward path (filed):** generators stamp `predicate_kind` on emission
(g4/g5='invariance', a3='transformed', a1/f-family='direct') + a record_schema
field, so the filter never depends on a generator_id denylist.

Full verdict: `pivot/calibration_v3c_VERDICT_generator_category_error_2026-06-03.md`.
