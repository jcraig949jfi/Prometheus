# Cycle 004 — VERDICT: what is a measured circuit a property of?

**Date:** 2026-08-27. **Preregistration:** `CYCLE_004_PREREG_basis_audit.md`, written before any
cell was computed. **Fossil:** `ludus/fossils/FOSSIL_r0003_2026-08-27.json`, frozen before any repair.
**Data:** `ludus/atlas/cycle004_partner_matrix.json`, `cycle004_identified_design.json`.
**Model calls: zero. Every number is exact** — backward induction over complete state spaces, no
sampling, no estimation, no standard errors to quote because there is no noise to quote them against.

---

## VERDICT — `CONTEXTUAL_BASIS_REQUIRED`

Not primitive. Not partner-conditional. Not relational. **Contextual.**

```
EXACT variance share of E_ijk, identified design, 5 circuits x 5 partners x 16 worlds = 400 cells

  world                        0.3497     <- the largest single term
  circuit x world              0.1692
  partner                      0.1645
  partner x world              0.1026
  circuit                      0.0998
  circuit x partner x world    0.0834
  circuit x partner            0.0307     <- the SMALLEST term

  S_circuit = 0.2605      mean Kendall tau across partners = 0.9721
```

Preregistered rule: `S_circuit < 0.30` and `V_circuit×world > V_circuit×partner` →
**CONTEXTUAL_BASIS_REQUIRED**. Both conditions hold, and not marginally: 0.2605 against a 0.30
boundary, and a circuit×world term **5.5x** the circuit×partner term.

### The audit inverted its own premise

This cycle was called because a circuit's value changed with its **partner** — `r0003` reading
0.0000 beside one selector and 1.0000 beside another in the same world. That looked like the
phenomenon.

It is the smallest term in the decomposition.

The dramatic partner swing is real but **spatially concentrated**: it lives in one corner of world
space, `gate ∧ ¬decoy`. Add a decoy to the same gated world and the partner spread collapses from
1.0000 to 0.0396. So what presented as partner-dependence is world-dependence wearing a partner's
clothes — the world determines *whether* the partner matters. That is why the three-way term (0.0834)
is nearly three times the two-way circuit×partner term (0.0307).

**A circuit's measured value is primarily a property of the world it is measured in.** The world main
effect alone (0.3497) exceeds the circuit main effect (0.0998) by three and a half times. Most of the
variance in "how well does this circuit do" is simply "which world is this".

### What survives: rank, not magnitude

Kendall tau across partner pairs is **0.9721**. Circuit *ordering* is highly stable — if `r_a` beats
`r_b` beside one partner it almost always beats it beside another. What is unstable is *how much*.

That is a narrower object than the catalog assumed, and it is not nothing. A representation that
carries only ordering is weaker than one carrying effect sizes, and the ledger should say which it
has earned.

---

## The identifiability failure, and the intervention that fixed it

The first decomposition ran on the 16-world gate×decoy×arity×capacity factorial and the
identifiability override **fired**: `r0004` (never bank) and `r0007` (bank when P(death) ≥ ½) had
**identical signatures across all 400 cells**.

Diagnosis: `p_bust` was pinned at 0.25 in every one of the sixteen worlds, so `r0007`'s threshold
could never fire and it degenerated *into* `r0004`. Two genuinely distinct policies that the design
could not distinguish — non-identifiability caused by a hole in the design, not by the circuits.

Per the preregistration's census requirement, the question was then "what intervention would
maximally separate them". The answer was a FOUNDRY parameter, not a new game: **vary `p_bust`**.
Re-run over `p_bust ∈ {0.1, 0.25, 0.5, 0.7}`: **5/5 distinct signatures, identified = True.**

The verdict above is computed on that identified design only. The unidentified one is retained, not
discarded — a design that cannot separate two of its own circuits is a fact about the instrument.

## Construct validity: the verdict is not an artifact of the denominator

The world main effect being largest invites an obvious deflation — `E` is normalised by each world's
optimal EV, so "world" might just be encoding how much headroom the denominator leaves. The
preregistration named this and named its test. Recomputing under three denominators:

```
denominator                          S_circuit   cxp      cxw      world     class
optimal EV (original)                  0.2605   0.0307   0.1692   0.3497   CONTEXTUAL
best cheap policy                      0.2659   0.0341   0.1763   0.3173   CONTEXTUAL
range-normalised (floor..optimal)      0.2781   0.0319   0.1930   0.2713   CONTEXTUAL
```

Range-normalisation removes headroom differences and drops the world main effect from 0.3497 to
0.2713 — as it should — while circuit×world *rises* to 0.1930 and the class is unchanged in all
three. **`CIRCUIT_CONSTRUCT_INVALID` does not fire.**

## Prospective value is poor, and that is the practical finding

Leave-one-out, on the identified design:

```
leave-one-partner-out   mean |error| 0.3424    max 0.7415
leave-one-world-out     mean |error| 0.3353    max 0.7510
```

A circuit characterised on every partner but one predicts the held-out partner's cell with mean
absolute error **0.34 on a 0–1 scale**. Leave-one-world-out is no better. Whatever the rXXXX objects
are, **they do not currently predict their own behaviour somewhere they were not constructed** — which
is the only thing that would make them worth transferring.

## Where the preregistration was wrong

Null expectation #1 predicted `S_circuit ∈ [0.30, 0.70)` — partner-conditional. Observed **0.2605**,
outside the interval. The reasoning behind the expectation (one circuit swings on partner alone, but
three of four batch-1 worlds were pairing-invariant) was sound and still produced the wrong bracket,
because it never occurred to me to ask whether the partner swing was itself world-conditional.

Expectation #3 was right: the smallest FOUNDRY worlds did produce degenerate cells, and the
identifiability failure was of exactly that kind.

---

## Consequences, recorded rather than acted on hastily

1. **`r0003` is NOT renamed, NOT rescoped, NOT split.** The fossil's disposition stands: UNRESOLVED,
   because the protocol that produced the 0.0000 was invalid rather than negative. Its maturity state
   is `ABLATION_SUPPORTED`, **blocked at `PARTNER_ROBUST`** — it cannot be credited as cross-world
   while its magnitude is not yet a function of the world alone. It stays ugly.

2. **A flat circuit catalog is the wrong shape, but a hypergraph is not yet justified.** The evidence
   says the useful object is `r_i(W)` — a circuit *indexed by world properties* — not `r_ij`
   (pairs) and not a free-form hypergraph. `V_circuit×partner` at 0.0307 is too small to justify
   building a relational representation, and charter §13's warning applies precisely here:
   representation follows evidence. The minimal change the data actually demands is that every
   circuit claim carry the **world properties it is conditional on**.

3. **The next thing to build is the world-property vocabulary, not more circuits.** `w0001` (gating)
   was registered last cycle from one reversal; the decoy axis is a second candidate; `p_bust`
   turned out to be load-bearing for identifiability. If circuit value is mostly a function of world
   properties, then the properties are the objects that need a registry, ugly identifiers, and
   prospective predictions of their own.

4. **No twenty-second world.** Every question in this cycle was answered by FOUNDRY parameters. The
   admission ticket for a real world is unchanged and unfilled.

## Engineering failures, classified (they change which worlds are tractable)

| class | failure | consequence |
|---|---|---|
| instrument | measuring an axis against a single partner | a whole column of zeros that read as a kill |
| instrument | promotion guard was a string test | promoted `r0003` on its own first test case |
| representation | `p_bust` pinned across the factorial | two circuits unidentifiable |
| representation | redundant `drawn` counter in Coloretto | ~21x state blowup |
| representation | Lucky Numbers with-replacement "simplification" | *worse* than the problem it fixed |
| compute | recursion depth vs C stack | silent crash; `tail` reported exit 0 |
| compute | `lru_cache` on hot path | 4.1s → 20.1s regression |
| compute | `_one_draw_ev` recomputed per option | a run that looked slow was ~10^10 ops |
| scientific | none this cycle | the verdict is a real result, not a defect |

The distinction matters because each demands a different response, and because three of these
determined **which worlds could be measured at all** — an instrument failure that silently shrinks the
world set is a scientific failure wearing overalls.

---

## EXTERNAL VALIDATION on the four real worlds — and a defect in my own decision rule

The verdict above was computed on FOUNDRY, which is synthetic. Charter v1 §37 is explicit that a
synthetic pass is instrument calibration, not an architectural result. The four real worlds with both
axes live (Martian Dice, Can't Stop, Lucky Numbers, Coloretto) form their own complete 5x5x4 design,
100 exact cells:

```
                          REAL WORLDS      FOUNDRY (identified)
  circuit x world            0.4374              0.1692
  circuit                    0.2126              0.0998
  partner x world            0.1416              0.1026
  partner                    0.0990              0.1645
  world                      0.0696              0.3497
  circuit x partner x world  0.0277              0.0834
  circuit x partner          0.0122              0.0307

  S_circuit                  0.3082              0.2605
  Kendall tau                0.9225              0.9721
  identified                 True                True (after varying p_bust)
```

**The two designs agree on the substance and disagree on the label.**

Substance, agreed by both: `circuit x world` overwhelms `circuit x partner` — by **5.5x** in FOUNDRY
and by **36x** in the real worlds. In the real worlds `circuit x world` (0.4374) is the largest term
in the entire decomposition, larger than every main effect. Circuit rank remains stable across
partners in both (tau 0.92, 0.97).

Label, disagreed: real worlds give `S_circuit = 0.3082`, which clears my 0.30 boundary by **0.0082**
and therefore classifies as `PRIMITIVES_PARTNER_CONDITIONAL`.

**That label is substantively wrong, and the fault is in the rule I wrote.** My preregistered decision
tree tests `S_circuit` first and only asks "relational or contextual?" *inside* the `S_circuit < 0.30`
branch. So a design in which world-conditionality is 36x partner-conditionality gets called
*partner*-conditional purely because its marginal share landed a hundredth above a threshold. The
rule cannot express "partly marginal AND strongly world-conditional", which is exactly what the real
worlds show.

The preregistration said boundary cases are reported as such and not resolved in the direction that
flatters. So:

- **Reported outcome, by the letter of the rule:** FOUNDRY `CONTEXTUAL_BASIS_REQUIRED`, real worlds
  `PRIMITIVES_PARTNER_CONDITIONAL` at a margin of 0.0082.
- **Reported outcome, by the evidence:** both designs say the same thing — a circuit's value is
  conditional on the **world**, and barely on the partner. The headline verdict stands.
- **Defect recorded:** the decision rule needs a world-vs-partner comparison at *every* level of
  `S_circuit`, not only below 0.30. Fixing it now would be fitting the rule to the data, so the rule
  is left as written, the defect is logged, and the corrected form is registered for cycle 005
  *before* it is used.

This is the second preregistered instrument in two cycles to fail in the permissive direction — the
first being the promotion guard that was a string test. Both failures share a shape: **a criterion
written as a sequence of checks, where an early check short-circuits a later one that carried the
real content.**

### What this changes about the consequences

Nothing in the four consequences above is weakened, and one is strengthened. Consequence 2 said a
flat catalog is the wrong shape but a hypergraph is not justified, because `circuit x partner` is too
small. The real worlds put that term at **0.0122** — three times smaller than in FOUNDRY. The case
against a relational basis is stronger on real games than on the synthetic controls, and the case for
indexing circuits by **world properties** is correspondingly stronger.
