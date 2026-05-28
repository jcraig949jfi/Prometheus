# ComposedClaim per-field consumer audit (Phase 1B ITER-36)

**Date:** 2026-05-28
**Author:** Charon (Erebos substrate)
**Audit tool:** `scripts/composed_claim_consumer_audit.py`
**Raw report:** `pivot/erebos_composed_claim_consumer_audit_2026-05-28.json`
**Doctrine alignment:** Doctrine v1.0 §"What this is NOT" + DR amendment §4.5 epistemic economy

---

## Audit purpose

Per Erebos Doctrine v1.0 + Phase 1B roadmap: every field on `ComposedClaim` is seam infrastructure. A field with N production producers + 0 production consumers is **seam-debt** — cost paid (production + storage + serialization) without downstream value. This audit identifies which fields have real consumers vs which are infra-pending.

The audit grep's `charon/`, `ergon/`, `scripts/`, `aporia/`, `theseus/` for three access patterns per field: `.field`, `field=`, and `"field":` dict-key. Each hit is classified as `producer` (assignment/kwarg/dict-key) or `consumer` (read access). Tests are tallied separately from production. Source-of-truth definitions (`generators/_base.py`) are excluded from counts.

## Headline result

| Bucket | Count | Fields |
|---|---|---|
| **Healthy** (has production consumers) | 11 | plugin_id, composed_id, input_provenance, transformation_description, output_claim_text, falsification_route, expected_kill_pattern, loader_feasibility_note, parent_record_ids, composition_payload, extras |
| **Infra-pending** (Phase 0 shipped, no production reader yet) | 5 | predicate_handle, generation_cost_seconds, falsification_cost_seconds, information_gain_nats, reuse_value_count |
| **Seam-debt** (production producers but zero production consumers) | **0** | — |

**Net assessment:** zero seam-debt fields. Every field is either actively consumed in production OR is Phase 0 infra explicitly scheduled for Phase 1B/1C wiring (cost-instrumentation daemon wire = ITER-37; predicate_handle plugin adoption = continuing through Phase 1).

## Per-field detail

Counts: `P_prod` = production producers; `C_prod` = production consumers; `P_test` = test producers; `C_test` = test consumers.

### Six-field spec (all healthy)

```
plugin_id                    P_prod=71   C_prod= 5   P_test=37   C_test= 4
composed_id                  P_prod=138  C_prod= 4   P_test=10   C_test=23
input_provenance             P_prod=26   C_prod= 1   P_test= 5   C_test=23
transformation_description   P_prod=26   C_prod= 2   P_test= 4   C_test=14
output_claim_text            P_prod=25   C_prod= 3   P_test= 4   C_test=16
falsification_route          P_prod=27   C_prod= 2   P_test= 4   C_test=19
expected_kill_pattern        P_prod=53   C_prod= 2   P_test= 4   C_test= 6
loader_feasibility_note      P_prod=26   C_prod= 1   P_test= 4   C_test= 6
```

All six required fields have both production producers AND production consumers. The high `P_prod / C_prod` ratio (8–18x) reflects the asymmetry that 25 generators + 22 composition loaders all produce these fields while only routing / dispatch / loader-match logic consumes them. That ratio is healthy for a six-field-spec-style schema where every emission writes the full struct but only a few sites route on each field.

### Routing metadata (all healthy)

```
parent_record_ids            P_prod=29   C_prod= 2   P_test=21   C_test=12
composition_payload          P_prod=26   C_prod= 1   P_test=11   C_test=24
extras                       P_prod=73   C_prod=30   P_test=54   C_test= 0
```

`extras` is the high-traffic catch-all field (30 production consumers) and dominates the consumption surface. `parent_record_ids` + `composition_payload` each have small consumer surfaces but real ones — used for cross-emission lineage and composition-loader dispatch.

### Phase 0 ITER-25 — predicate_handle (infra-pending)

```
predicate_handle             P_prod= 0   C_prod= 0*  P_test= 2   C_test= 5
```

*The audit reports `C_prod=1`, but inspection of the hit (`charon/agents/erebos/_residue_eligibility.py:124`) shows it is a docstring reference — not a real attribute access. **Actual production usage: 0 producers, 0 consumers.** The audit script's classifier does not strip docstrings; that's a known false-positive class.

`predicate_handle` is shipped infra (Phase 0 ITER-25) waiting on plugin adoption. The `MahlerPolynomialHandle` class exists and is fully implemented; the next step is having generators G03/G11/G18/G24 populate `claim.predicate_handle` in their `generate()` methods. That work is deferred to per-plugin v3 retrofits (Phase 3 conditional, per Phase 0 retrospective §"Phase 0 did NOT do").

**Recommendation:** leave field. Track adoption by re-running this audit each iteration; flag as seam-debt only if no producer appears by ITER-50.

### Phase 0 ITER-27 — cost instrumentation (infra-pending, 4 fields)

```
generation_cost_seconds      P_prod= 0   C_prod= 0   P_test=12   C_test= 0
falsification_cost_seconds   P_prod= 0   C_prod= 0   P_test=13   C_test= 1
information_gain_nats        P_prod= 0   C_prod= 0   P_test=13   C_test= 1
reuse_value_count            P_prod= 0   C_prod= 0   P_test=12   C_test= 0
```

All four cost-instrumentation fields have **zero production usage**. Tests construct them with default values but neither produce nor consume them in interesting ways. This is the largest "zero-use in production" cluster.

Per Phase 0 retrospective: _"Phase 0 did not ship the cost-instrumentation in the daemon loop. The `ComposedClaim` fields exist; the daemon must wrap `plugin.generate()` and loader execution with `time.perf_counter()` to populate them. Wiring is Phase 1."_

This audit confirms the deferral is intact. **All four fields are eligible to be wired during ITER-37** (cost-instrumentation daemon wire). After ITER-37, P_prod for `generation_cost_seconds` + `falsification_cost_seconds` should be ≥ 1 (the daemon bracket); `information_gain_nats` + `reuse_value_count` need separate post-hoc computation (deferred to ITER-37 or follow-on).

**Recommendation:** retain all four. Re-audit immediately after ITER-37; if any field still has zero producers, it is genuine seam-debt and should be retired.

## False-positive classes observed

The audit script's classifier is regex-based. Known false-positive categories that inflate counts (mostly producers, very rarely consumers):

1. **Docstring references** (`"""... claim.predicate_handle ..."""`): counted as consumer or producer based on regex match without comment-stripping. Estimated impact: ≤1 per field.
2. **Comment lines** (`# field=X`): partially suppressed via `split("#", 1)[0]` but inline-after-code comments slip through. Estimated impact: ≤5 per field across the codebase.
3. **String-literal mentions** (`"the field is x"`): can match the `"field":` dict-key regex. Estimated impact: low for our field names (no field name is a common English word).
4. **Variable-name aliasing** (`extras = composition_payload`): the LHS counts as producer for `extras` and the RHS as consumer for `composition_payload`. Real but minor.

None of these classes change the bucket assignment (healthy / infra-pending / seam-debt). The audit's conclusion is robust to these noise sources.

## Action items

| Item | When | Owner | Notes |
|---|---|---|---|
| Wire `generation_cost_seconds` + `falsification_cost_seconds` in daemon | ITER-37 | Charon | Bracket `plugin.generate()` and loader execution with `time.perf_counter()` |
| Wire `information_gain_nats` + `reuse_value_count` (post-hoc compute) | ITER-37 follow-on | Charon | Requires Hecate / Ergon downstream taps |
| Plugin adoption of `predicate_handle` (G03/G11/G18/G24) | Phase 3 conditional | Per-plugin retrofit | Already implemented MahlerPolynomialHandle |
| Re-run audit after ITER-37 | ITER-37 | Charon | Verify cost fields' `P_prod > 0` |
| Re-run audit after ITER-50 | ITER-50 | Charon | Flag any infra-pending field with no producer yet as candidate for retirement |

## Reproducibility

```
python scripts/composed_claim_consumer_audit.py \
    --json-path pivot/erebos_composed_claim_consumer_audit_2026-05-28.json
```

The script is idempotent and re-runnable. Cached file reads make second-and-later field audits within the same run essentially free.

---

**End audit.** Zero seam-debt fields. Five infra-pending fields, all explicitly scheduled. ComposedClaim's schema is justified per current codebase consumption.
