# PREREGISTRATION — Specimen 3: Q045 "unreachable class" through the closure gauntlet

**Filed:** 2026-09-01, before any run. **Author:** Hephaestus (conflicted: author of the gauntlet).
**Governing:** charter amendment Addendum 4 §7 (three conditions) and §10 (sequence). **Basis:**
A2-GENERIC-v1, hash `7f2ef69196e7f128`, frozen at commit `1f4c5ca72` *before* this document's author
read `aporia/lot/world3.py` or the Q045 probes. **Family (WALL_TAXONOMY_v1):** **F6 constructive
transformation** — targets are vector→vector functions, not verdicts.

## 0. What Q045 is, and why it is the right third specimen

Aporia's Q045 (`aporia/q100/dossiers/Q045_search_vs_representation.md`) built, in the TINYPROG world
(4-tuples over Z6; ten anonymous typed primitives p00–p09; programs are functions of one input;
behaviours are extensional signatures over a fixed 6-probe set), an exact **leave-one-out
certificate**: remove one primitive, and the behaviours reachable with the full inventory at
size ≤ 5 that the impoverished inventory cannot reach even at size ≤ 8 are a **certified
representation-failure class** — 93.4% of the class survives a 26× deeper search. Removing `p05`
(elementwise vector multiply) loses the largest class: 2,136 of 3,502 V-signatures (61.0%).

For the Forge this is the case the first two specimens lacked: **a wall where an operator is
missing by construction.** It is therefore simultaneously (a) a third family, and (b) a **positive
control** for whether the gauntlet can detect an OPERATOR gap at all — the concern of Addendum 4 Q4.
The same world supplies its own **negative control**: behaviours the impoverished inventory *does*
reach, which must classify SEARCH_ROUTING at margin A0.

## 1. Semantic state and target (extensional, from the existing probe — Addendum 4 §7(b))

- **Semantic state:** the input vector `x ∈ Z6^4`. No language, no parsing, no Apollo.
- **Target of a route:** a behaviour = the tuple of outputs on the world's own probe set
  `world3.probe_inputs()` (6 vectors, seed 20260827). Targets are *selected* from the world's
  closure certificate; they are *defined* by their outputs, never by a program the gauntlet is shown.
- **Verification domains (Addendum 4 Q5):** the target behaviour must be extended beyond the six
  probes to verify a witness. The extension uses the world's own certified minimal full-inventory
  program for that behaviour (`build_closure` gives it), evaluated on: **VERIFY_EXHAUSTIVE_SMALL** =
  all 1,296 vectors of Z6^4 minus the six probes; **VERIFY_STRUCTURAL_SHIFT** = 300 sampled vectors
  with entries drawn from **0..6** (one value outside the Z6 alphabet), evaluated under the world's
  own mod-6 arithmetic — inputs the world never generates, so any witness keyed to in-alphabet
  coincidences is exposed. (A true ring change to Z7 was considered and rejected for this run: the
  gauntlet evaluates all columns under one ring per call; changing the ring per column is a tooling
  change, and Addendum 4 §6 forbids more machinery before specimen 3.) A witness found on six probes
  that fails on 1,290 more is an alias; one that fails only under the shift is not robust.

## 2. Target selection rule (mechanical; fixed here)

Let `C_full` = p00..p09, `C_imp` = C_full \ {p05}. Compute with `world3.build_closure`:
`R_full5` (C_full, size ≤ 5), `R_imp5` (C_imp, size ≤ 5), `R_imp8` (C_imp, size ≤ 8, the dossier's
verification depth; if the 30M-candidate budget cannot complete on this machine in 10 minutes,
size ≤ 7 is used and stated).
- **LOST (case c) targets:** V-behaviours in `R_full5` with minimal full size ≤ 3, absent from
  `R_imp5` AND absent from the deeper `R_imp` closure. Take the first **20** in canonical order
  (minimal size, then signature). Size ≤ 3 so that the candidate-operator arm can reach them
  within the gauntlet's depth.
- **CONTROL (case a) targets:** V-behaviours in `R_full5` with minimal size ≤ 3 that ARE in
  `R_imp5`. First **10** in canonical order, excluding the identity.

## 3. Arms (identical gauntlet; each target is its own single-route closure question)

| arm | operators | question |
|---|---|---|
| A0 | `C_imp` (9 primitives, typed V/S), terminal `X` | G(C) |
| A1 | same — TINYPROG has no route key; **A1 ≡ A0 here** and is reported as such | G(C∣R) with R = ∅ |
| A2 | A0 + **A2-GENERIC-v1** (S mapped to `int`; no generic op produces a V) | G(C∣R,A2) |
| B | generic small vector language: elementwise add/mul, increment, map-to-constant, rotate, reverse | the "any small program" control |
| **C** | A0 + the candidate operator `p05` (elementwise multiply) | does naming the missing operator close the wall at depth ≤ 4? |

Depth ≤ 4, budget 300,000 evaluations per arm per target. Membership as in `closure_test.py`:
*coerced* (equal on the six probes), *typed* (static type V), *verify_exhaustive*, *verify_shift*,
*mechanism-bearing* = typed ∧ exhaustive, *robust* = + shift. Equivalence classes ≤ 5 by tree shape.

## 4. Classification rule per target (fixed)

- **SEARCH_ROUTING** with margin A0/A1/A2_ONLY if that arm has a mechanism-bearing witness.
- **OPERATOR** if A0, A1, A2 have no witness (not even a coerced alias), B has a mechanism-bearing
  witness, **and C has a mechanism-bearing witness**.
- **INCONCLUSIVE** if C (the named operator) fails to reach the target at depth ≤ 4 — then the
  gauntlet's depth/budget, not the substrate, is the limit, and no class is assigned.
- **A2_LEAK** flag if A2 finds a witness that A0/A1 did not: the frozen basis supplied operator power.

## 5. Predictions (falsifiable, stated before running)

P1. ≥ 90% of LOST targets classify **OPERATOR** (A0/A1/A2 empty; B and C reach).
P2. 100% of CONTROL targets classify **SEARCH_ROUTING at margin A0**, robust.
P3. **A2_LEAK = 0** — the generic basis (booleans, order, counts, projections) cannot manufacture an
    elementwise vector product.
P4. Every C witness is robust under the ring shift (the operator, not a Z6 coincidence, closes it).
P5. Some LOST targets will have **coerced aliases** in A0 on the six probes that die on the
    1,290-point exhaustive check — this is the dossier's "label leaks" phenomenon seen from inside
    the gauntlet, and it is why verification columns exist.

## 6. Kill / abort conditions

- If P1 fails with A2 witnesses present (P3 fails): **the basis is too generous** — report, do not
  reclassify the earlier specimens until the basis is revised as a versioned intervention.
- If C reaches < 90% of LOST targets: the gauntlet cannot certify OPERATOR at this depth;
  result INCONCLUSIVE for those targets; no "OPERATOR" claim may be quoted.
- If P2 fails: the enumerator disagrees with the world's own closure — tooling defect; stop.
- If `R_imp8` cannot be built: state the depth actually used; contamination of the LOST label is
  then bounded only by the dossier's measured 6.6% at depth 8, not by this run.

## 7. What a result would mean

- P1–P4 hold: the funnel **can** detect an operator gap; the first two specimens' non-operator
  classifications are not an artefact of a funnel that only ever says "composition". The Forge's
  discriminator has a demonstrated positive case.
- P1 fails because A0/A1 reach LOST targets: Q045's own certificate is wrong or this enumerator
  is not equivalent to `build_closure` — tooling result, high priority.
- P1 fails because B does not reach: the target family exceeds "small generic program"; report.

## 8. Not decided by this experiment

Whether p05 is "the" missing operator in any sense beyond the world's construction; anything about
Apollo; anything about representation (arrow one), which this world does not have.

*Runner: `hephaestus/src/closure_q045.py`, committed unrun with this document. Result:
`hephaestus/closure_results/q045_lost_class.json`.*
