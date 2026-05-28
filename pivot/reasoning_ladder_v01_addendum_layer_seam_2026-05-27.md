# Reasoning Ladder v0.1 — Addendum: Layer 1 / Seam / Layer 2 mapping

**Date:** 2026-05-27
**Status:** Addendum to `pivot/reasoning_ladder_v01_2026-05-24.md`. Does not modify the ladder's R/F/M/H axes; adds the per-layer interpretation that the Erebos doctrine (v1) requires.
**Reading order:** original ladder first, then this addendum, then `pivot/erebos_doctrine_v1_2026-05-27.md`.

---

## What this addendum does

The Reasoning Ladder v0.1 defines R (mechanism depth), F (failure-signature depth), M (representation mobility), H (epistemic humility) as co-equal axes for evaluating a reasoning system. The Erebos doctrine v1 introduces a TWO-LAYER architecture with a deliberately-architected SEAM between traditional per-emission falsification (Layer 1) and a non-traditional cross-emission accumulator (Layer 2).

This addendum maps the ladder axes onto the two-layer architecture so tier assignments stay coherent with the substrate's structure.

## The mapping

### R-axis (mechanism depth) → primarily Layer 1

The R-tier of a plugin describes WHAT KIND of reasoning operation it performs at the per-emission level. R3 (constraint maintenance), R5 (counterfactual control), R8 (representation shift) are all properties of the plugin's `generate()` method — they describe the cognitive move that produces a candidate claim.

R-tier is a Layer-1 attribute. A plugin can be "doing R8 representation shift" at the per-emission level regardless of whether Layer 2 (the accumulator) consumes its output usefully.

### F-axis (failure-signature reading) → primarily the SEAM and Layer 2

F is where the Erebos doctrine has the most leverage. The F-axis asks: how deeply does the system READ the gradient of its own failures?

- F0 (cannot detect failure): no Layer 2 at all. Failure evaporates.
- F1-F2 (detects contradiction): Layer 2 exists but is shallow — kill_pattern is named but not routable.
- F3 (local repair): Layer 2 routes within a single plugin's domain.
- F4 (global repair): Layer 2 routes across plugins via shared kill_pattern semantics.
- F5 (strategy repair): Layer 2 changes the routing policy itself based on kill-density.
- F6 (ontology repair): Layer 2 reshapes the failure topology (the predicate_handle's algebraic class changes).
- F7 (problem repair): Layer 2 reformulates the inquiry; eligibility gate retroactively revokes prior residue.
- F8 (epistemic repair): Layer 2 identifies why prior evidence was misleading (the G15 self-audit pattern at full depth).

**The F-axis IS Layer 2 made internal to the system.** The substrate's claim that "every reasoning act leaves navigable residue" is a claim that the F-axis can be raised by architecture, not just by training.

The seam is what makes F3 and above OPERATIONALLY available: without typed first-class artifacts crossing from Layer 1 to Layer 2, the system cannot perform local-or-better failure repair because the failure has been collapsed into a scalar.

### M-axis (representation mobility) → THE SEAM

The M-axis describes how freely the system moves between representations. The seam — what crosses from Layer 1 to Layer 2 as a `ComposedClaim` — IS where representation mobility lives.

- M0 (given representation only): no seam; Layer 1 outputs go directly into a scalar loss
- M1-M2 (translates / chooses): seam exists but carries only one fixed payload shape
- M3 (compares representations): seam carries multiple payload variants; substrate can A/B them
- M4 (moves between representations mid-solution): predicate_handle allows the substrate to switch between text, SMT formula, Lean term, SymPy expression mid-emission
- M5 (invents a representation specific to the problem): the seam itself evolves — new composition_payload fields are PROPOSED by the substrate, not authored by humans
- M6 (extracts reusable representation schema): Layer 2 identifies recurring payload patterns and promotes them to first-class schema elements

Erebos at v0.36 sits at M2-M3. The doctrine targets M4 (`predicate_handle` is the move). M5-M6 are aspirational and require Phase 1C tensor operations + motif extraction.

### H-axis (epistemic humility) → spans both layers

H is about knowing what the system knows / doesn't know. Both Layer 1 (per-emission self-assessment) and Layer 2 (cross-emission self-audit) contribute:

- Layer 1 H: a plugin's `applicable(state)` predicate decides whether the plugin has the inputs to fire (H2: detects missing information)
- Seam H: the eligibility gate decides whether a Layer-1 result is rich enough to promote to Layer 2 (H3: identifies the exact missing variable)
- Layer 2 H: the kill_ledger MI self-audit measures whether the substrate's own emissions are coupled in ways that suggest bookkeeping bias (H5: designs a test to resolve uncertainty; H6: updates after the test)

The G15 v1 → v2 self-audit chain (ITER-13 → ITER-14) operationalized Layer 2 H6: the substrate measured its own MI, identified it was inflated by bookkeeping, shipped a v2 with control-flow filter, and re-measured. That's H6 in code.

## Doctrine #1 falsification-first → Layer 1

The first doctrine of the Reasoning Ladder ("a system does not occupy a reasoning tier because its output resembles that tier; it occupies the tier only if the relevant mechanism survives perturbation, beats lower-tier baselines, and fails in the tier-predicted way") is fundamentally about Layer 1. It says: tier claims must be empirically falsifiable at the per-emission level via perturbation tests.

The Erebos doctrine inherits this directly. Layer 1 quality is load-bearing; Layer 1 evaluation is via per-emission falsification.

## Doctrine #2 failure-signature reading → Layer 2

The second doctrine ("reasoning capability is read from the gradient of failure, not the binary of success") is fundamentally about Layer 2. The kill_ledger IS the accumulated gradient of failure; the kill_pattern_registry IS the routing semantics on that gradient; the tensor operations (Phase 2 deliverable) ARE the analytical machinery for reading it.

The substrate's central architectural commitment is: **make Doctrine #2 mechanizable.** Failure-signature reading must be a system property, not a human-only interpretation. Layer 2's job is to take the typed artifacts that crossed the seam and make them analyzable / queryable / routable without human intervention.

## What changes for tier assignment

Old tier readings (pre-addendum) assigned a single R/F/M/H tuple per plugin. With the two-layer architecture, the tuple needs to be qualified by layer:

- **R-tier (Layer 1):** what the plugin does per-emission
- **F-tier (Layer 2):** what the substrate's routing layer can do with the plugin's emissions
- **M-tier (seam):** what shape of artifact the plugin contributes to the seam
- **H-tier (both):** what self-assessment the plugin has at Layer 1 + what self-audit the substrate has at Layer 2 over the plugin's emissions

A plugin can be **R8 / F3 / M2 / H2** at v0.26 (decent local mechanism, narrow routing, fixed payload, decent self-assessment) and **R8 / F5 / M4 / H4** post-Phase-1 (same Layer 1 mechanism, but the substrate now has richer routing, schema mobility, downstream self-audit). The R-tier doesn't change; the Layer-2-derived tiers do.

This is the right framing because it cleanly separates "is the plugin doing good Layer 1?" from "is the substrate doing good Layer 2 with the plugin's output?"

## Gravity-well counter-discipline for tier assignment

Per `pivot/erebos_doctrine_v1_2026-05-27.md` §"counter-discipline":

When applying the Reasoning Ladder to evaluate Erebos plugins, **do not interpret high R-tier as substrate value**. A plugin can be R8 (representation shift) and still be a Layer-1-only contribution — its emissions never get used by Layer 2, the substrate gains nothing cumulative. The substrate's value is at Layer 2; the R-tier is one input to the substrate's value but not the substrate's value itself.

Conversely: a plugin at R3 (constraint maintenance) whose emissions reliably contribute high-quality residue that Layer 2 routes on is producing substrate value. Don't demote it because R3 is "low."

The integration with the gravity-well counter-discipline: **never use R-tier alone as the substrate's score.** R-tier is a per-emission diagnostic. The substrate's score is at Layer 2 (failure-topology density, compounding, rank expansion).

---

## Summary table

| Axis | Layer | Question it answers | Erebos primitive that enables it |
|---|---|---|---|
| R | Layer 1 | What cognitive move does the plugin perform? | `generate()` method semantics |
| F | Layer 2 | How deeply can the substrate read failure signatures? | kill_pattern_registry + tensor ops |
| M | Seam | What shape of artifact crosses Layer 1 → Layer 2? | `predicate_handle`, SurvivalCurve, eligibility gate |
| H | Both | What does the system know about its own emissions? | `applicable()` (L1) + ledger MI self-audit (L2) |

**The architectural target:** raise the Layer-2 axes (F, parts of M, parts of H) via system architecture, not just via better Layer-1 training. This is the structural property that distinguishes Erebos from a system that does only Layer 1 well.
