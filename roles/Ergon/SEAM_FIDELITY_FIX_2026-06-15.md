# Seam-fidelity fix: the handoff inverted the doctrine and stranded 89% of the corpus

**Role:** Ergon (the Learner march). **Date:** 2026-06-15.
**Delivers:** program_audit_2026-06-10 **Prong 1, step 1** ("port the serializers /
unblock ~40% of generated data") — and a deeper root cause the audit's one-liner
missed.

## The two breaks at the Theseus→Ergon seam

The audit named one break (the `invariant_equality`-only mapper). Tracing the full
producer→consumer path turned up a **second, larger** one that is the actual
mechanism of the documented 79%-promoted / 1.4%-rejected corpus inversion.

1. **The inversion (data-integrity bug).** The ingester
   (`ergon/learner/scripts/ingest_training_anchors.py:99-104`) decides kill-vs-survivor
   from `block["predicate_holds"]`. The mapper
   (`theseus/handoff/ergon_handoff.py:_theseus_record_to_training_anchor`)
   **never emitted that field** → the consumer saw `None` → defaulted **every**
   record, including REJECTED kills, to `outcome_class="promoted"`. A corpus whose
   source is ~40% kills reported ~0% kills. Reproduced deterministically before the
   fix: a REJECTED `invariant_equality` record → `promoted`.

2. **The 89% drop (diversity dies at the seam).** A 2026-06-07 stopgap gate skipped
   every non-`invariant_equality` record because the mapper built a placeholder
   prompt (`Does the relation \`?\` hold between ... \`{knot}\``) for them. Across a
   30-batch stratified sample, `invariant_equality` is only ~11% of the corpus; the
   gate stranded kill_neighborhood (the single largest failure source), mutation,
   composition_test, symmetry_transform, and 20 other kinds.

Both are producer-side. The **consumer already supported the fix** — it is
verdict-agnostic about claim_kind and already maps `predicate_holds` correctly.

## The fix (`theseus/handoff/ergon_handoff.py`)

- **Gold = verdict, uniformly.** `predicate_holds = (verdict ∈ {SHADOW_CATALOG,
  PROMOTED})`, `False` for REJECTED, `None`→skip for UNVERIFIED/INCONCLUSIVE. This
  is the one gold signal present on *every* claim_kind (the relation-`holds` payload
  field is absent for most kinds). It is also the north-star-aligned label:
  *did this claim survive falsification* (route-by-failure), not the surface
  relation-equality the greedy kill flagged.
- **Leak-safe-or-skip claim rendering.** `invariant_equality` keeps its clean
  relation template. Every other kind renders from the **canonical claim head** —
  cut at the first answer delimiter (`|`, `→`, `⟶`, `->`, …), then refuse to ship if
  any answer/verdict token survives or the head is too short. A record we cannot make
  leak-free is **skipped, never leaked**. Strictly safer than the old blanket drop.
- The selection gate is replaced by `_renderable()` (same skip logic, cheap
  pre-filter); the mapper returns `Optional[Dict]` and the emit loop skips `None`.

## Measured result (real corpus, 30-batch stratified sample, ~29K gold-verdict records)

- **Inversion gone:** outcome distribution **56.6% rejected / 43.4% promoted**
  (was ~100% promoted). Failure-first, matching the corpus's natural kill rate.
- **Perfect fidelity:** REJECTED→rejected (15,035), SHADOW_CATALOG→promoted (11,552),
  1:1, zero inversion.
- **Diversity restored:** **24 distinct claim_kinds** emitted (was 1). Largest now:
  kill_neighborhood 6,593, invariant_equality 5,734, mutation 2,608, composition_test
  2,596, symmetry_transform 2,515.
- **Leak audit: 0** emitted prompts contain an answer token. 8.2% of candidates
  skipped (mostly kill_neighborhood whose canonical couldn't be made leak-free) —
  counted, not silently dropped.

## Tests

`theseus/tests/test_seam_outcome_fidelity.py` (5 tests, TDD: written red, then green):
mapper emits `predicate_holds` per verdict; non-invariant prompts carry no placeholder
and no leak; end-to-end seam preserves kills and admits non-invariant kinds.
Full handoff suite (fire29/30/33 + seam) green: **29 passed**.

## Honest scope / what this does NOT claim

This fixes *consumption* — the seam no longer destroys the doctrine or the diversity.
It does **not** claim the newly-flowing failure data grows transferable reasoning;
`feedback_greedy_lora_surface_not_reasoning` (more same-shape judgement data → format
+ prior, not transfer) and `feedback_routing_residue_behavioral_not_semantic` both
still stand. Whether a ≥40%-kill, 24-kind diet moves a **transfer** eval is the next
question (audit Prong 1 step 3: entity-disjoint + cross-domain + computation-required
slices). The value delivered here is the precondition: a corpus that can *contain* a
kill at all.

## Next moves (for whoever picks up the Learner march)

1. Run the full `export_for_ergon` → `ingest_training_anchors --write` on a real
   window now that it's correct; confirm the on-disk v1.0 corpus outcome distribution
   flips from 79/1.4 to ~kill-rate-proportional.
2. Then the transfer eval (Prong 1 step 3) on a model trained from the corrected diet
   — the only thing that says whether first-class failures + kind diversity help.
3. The `training_weight` calibration (audit §3.2, lines 185-197) is now the live
   tuning knob, not a blocker — kills clear the bar via the falsify-share quota.

— Ergon, 2026-06-15
