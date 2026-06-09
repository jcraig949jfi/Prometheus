# Proposal E — Closing the h2 Opaque-Kill Black Hole

**Author:** Harmonia_M2_B (cross-domain cartographer / falsification engine)
**Date:** 2026-06-09
**Status:** Proposal for review (null-hypothesis articulation, not validation)
**Thread:** E of {A, B, D, E, F}
**Primary paths affected:** `D:\Prometheus\theseus\generators\h2_triangulation_protocol.py` (refactor already landed — see §2), `D:\Prometheus\theseus\corpus\` (historical ledger to backfill)
**Primary path to create:** `D:\Prometheus\harmonia\experiments\h2_backfill_and_validate.py`

---

## §0 — Doctrinal posture for any reviewer (read first)

Not seeking validation. LLMs as null-hypothesis articulators, never value evaluators. Frontier convergence is a warning signal (`feedback_llm_convergence_is_gravity_amplifier`). No papers, no SOTA, no publication framing. Answer §5 adversarially.

---

## §1 — Prometheus background (for a cold reader)

Prometheus mines **gradients of failure** for signal. Its kill-ledger — the record of every hypothesis the substrate rejected — is training material for a downstream Learner, *but only to the extent each kill says WHERE in claim-space the failure points* (`feedback_failure_signature_doctrine`: "Every pass/fail summary destroys the gradient; report failure *shapes*, not verdict-lines"). A kill that says only "rejected" with no witness is information-destroying: it confirms a failure happened but emits no direction.

**Harmonia** is the falsification organ and the keeper of this discipline. The motivating finding (`kill_topography_findings_2026-05-29` Finding 3):

> "**h2 emits 43.68% of all kills (87K records), and ALL of them have the same kill_pattern: `h2_method_triangulated_reject`.** Zero internal differentiation. … This is the largest information-loss hole in the substrate. Until h2 breaks its kill into subclasses, 44% of the corpus's kill volume is opaque to the Learner."

The report's recommendation #2: refactor h2 to emit named-witness kill patterns; "this single change converts 44% of kill volume from opaque to named" — higher Learner yield than building any new generator (recommendation #3: *stop adding gens* until this and the a3 void-mining are done).

---

## §2 — Existing project / code this proposal affects (and what's already done)

**Falsification-first finding (verified by reading source 2026-06-09):** the h2 *code* refactor **has already landed.** In `theseus/generators/h2_triangulation_protocol.py`, the REJECTED branch (lines ~219–248) no longer emits the flat pattern. It now emits:

```
h2_triangulated_{agreement_class}_{ki}_{ei}_methods_{method_tag}_rejected
```

where `agreement_class ∈ {unanimous, majority}`, `(ki, ei)` is the witness invariant pair, and `method_tag` encodes *which* of the three method variants (linear-small / quadratic-mid / cubic-large) voted reject. The in-code comment names the exact problem this proposal would otherwise re-propose: *"Previous flat `h2_method_triangulated_reject` was opaque (44% of corpus volume → 1 pattern)."* **The naive version of this proposal is already obsolete.** What remains is the part the code change did *not* do — and a Harmonia-specific check the code change did not think to make.

So the real, open work has three parts:

1. **Production emission is unverified.** The code emits structured patterns; whether the *running daemon* (`theseus/daemon.py`) is producing them in the live corpus — and at what fraction — is unconfirmed. The refactor may be shipped-but-not-deployed, or deployed-but-rarely-hit.
2. **The 87K historical kills are still opaque.** They predate the refactor and carry the flat `h2_method_triangulated_reject`. They are 44% of the corpus and the Learner still can't read them. They must be **re-classified** — and whether that's possible depends on whether their stored `claim_payload`/`step_trace` retained the per-method verdicts and `(ki, ei)` witnesses needed to re-derive the structured pattern *without re-running* (re-running is impossible: the INCONCLUSIVE parents may no longer exist).
3. **The new subclasses might be a new costume.** This is the Harmonia contribution. A refactor that replaces *one* opaque pattern with a *thousand* sub-patterns that are themselves dominated by a single value (e.g., 90% are `..._methods_linear_quadratic_cubic_rejected`, i.e. "all three methods rejected") has **not** added directional information — it has re-painted the black hole. **The structured patterns must be shown to beat their own baseline** (this is Proposal A's `baseline_costume` primitive; E is one of its first customers).

---

## §3 — The proposal

`harmonia/experiments/h2_backfill_and_validate.py`, three stages mirroring §2:

### 3.1 Verify production emission
Scan the live corpus for h2 records by emission date; report the fraction carrying the new structured pattern vs the legacy flat one, and the *distribution* of structured patterns. Confirms the refactor is deployed and firing, and surfaces the deployment cutover date (the boundary between backfillable-by-rerun and backfill-by-rederive).

### 3.2 Backfill the historical 87K
For each legacy `h2_method_triangulated_reject` row, attempt to **re-derive** the structured pattern from its retained `claim_payload` (which, per the current schema, carries `method_verdicts`, `knot_invariant`, `ec_invariant`, `method_counts`). If those fields survive in the historical rows → backfill is a pure local rewrite, no re-computation. If they do **not** → document the exact information that was destroyed at emission time (a substrate lesson: the schema must retain re-derivation inputs), and bound how much of the 87K is recoverable vs permanently opaque.

### 3.3 Validate the subclasses carry signal (the Harmonia gate)
Run `baseline_costume.costume_check` (Proposal A) on the post-backfill h2 patterns:
- **Concentration check:** is the structured-pattern distribution still dominated by one value (the "all-methods-reject" pattern)? Report the Gini/top-1 share. If top-1 share ≈ the old 100%, the refactor was cosmetic.
- **Directional-information check:** do the subclasses *predict* anything the flat pattern didn't — e.g., does `method_tag = cubic_only_rejected` ("almost linearizable") identify a sub-population of parents with systematically different downstream behavior than `all_methods_rejected`? If the subclasses don't separate any downstream variable, they are names without referents.

Emission: a verdict doc — `production_emission_rate`, `backfill_recoverable_fraction`, `subclass_concentration`, `subclasses_carry_signal: bool` — and, if §3.3 fails, a **demotion**: the refactor is reverted-in-spirit (the new patterns are flagged as not-yet-informative) rather than celebrated.

---

## §4 — Falsification / win condition (stated so it can fail)

- **If** §3.3 shows the structured patterns are still single-value-dominated → the refactor swapped one black hole for one slightly-larger black hole; "44% converted from opaque to named" is **false**, and the kill-topography recommendation over-promised. Harmonia's job here is to catch *exactly* this and not let "we refactored h2" be logged as a win.
- **If** the historical rows lack the re-derivation fields → 44% of the corpus is **permanently** opaque to the Learner, and the only lesson is forward-looking (schema discipline). That is a smaller win than the report implied, honestly stated.
- **If** production emission rate is near zero (refactor shipped but daemon path rarely hits the REJECTED branch) → the corpus is not actually accumulating structured h2 kills and the whole concern is moot until the daemon is exercised.
- **Win:** production emission confirmed firing, ≥X% of historical rows backfilled, AND the subclasses demonstrably separate ≥1 downstream variable (the methods-disagreement split predicts parent behavior). Only then is the black hole genuinely closed.

---

## §5 — Questions for the review board (null-hypothesis articulation)

1. **What is the right test that a kill-pattern subclass "carries directional information"?** §3.3 proposes "subclasses separate a downstream variable." But which variable, and separated how — is mutual information between subclass and downstream-promotion the right metric, or does that smuggle in a circularity (the subclass was *defined* by the same method-verdicts that drive promotion)? Name a non-circular separability test.
2. **The method-disagreement split** (`cubic_only_rejected` = "almost linearizable" vs `all_methods_rejected` = "structurally noise") is *my* interpretation of what the `method_tag` means. Is that interpretation sound, or is the linear/quadratic/cubic vote spread dominated by sample-size/degree artifacts (more parameters → higher R² mechanically) rather than anything about the parent's structure? How would I tell?
3. **Is backfill even worth it?** 87K rows is 44% of *volume* but the kill-topography report's own Finding 1 says 99% of kill volume is catalog-uniform low-information. If h2's kills are mostly low-information regardless of how finely we name them, backfilling 87K opaque rows into 87K finely-named-but-still-low-information rows is motion without progress. What's the test that the *content* (not just the label) of h2's kills has any directional signal worth recovering?
4. **Schema-retention lesson generalizes:** if h2's historical rows turn out to have destroyed their re-derivation inputs, which *other* generators are emitting kills that can't be re-classified later? Is the right move a cross-generator schema audit (every kill must retain enough to re-derive its own pattern) rather than a one-off h2 backfill?
5. **Cheapest discriminator:** what single query against the existing corpus would tell me — before I build the backfill — whether h2's structured patterns are single-value-dominated (cosmetic) or genuinely spread (worth the effort)?
