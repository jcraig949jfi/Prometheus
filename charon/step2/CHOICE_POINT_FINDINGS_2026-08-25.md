# Choice-point census — c1 × equal_mod_2. Findings.

**Charon, M1, 2026-08-25.** Class I. Prompted by external review; run *before* the pre-registered
regret experiment, on the reviewer's ordering, which I accepted.

Rows: `charon/step2/choice_point_census_equal_mod_2.json`.
Instrument: `charon/step2/choice_point_census.py` (no new corpus scan — the completed action
`A⁺ = (side, replacement)` is recoverable from child rows, since `mutation_side == "a"` makes the
replacement the child's `object_a`).

---

## 1. The denominator collapses, as the reviewer predicted

```
rows (deduplicated by child x parent)          5,871,696
parents                                        3,060,875
  k_P = 1   (ONE completed intervention)       1,649,801   53.9%  <- no choice was ever posed
  k_P >= 2                                     1,411,074   46.1%
DECISION-BEARING parents (k_P>=2, outcomes differ)  724,723   23.7%
distinct replacement objects                       1,052
```

**53.9% of parents were never offered a choice at all** — one completed intervention, nothing to
choose between. That half of the population is trajectory data, not evidence about choosing among
alternatives. Only **23.7%** of parents are decision-bearing.

The action space is also far smaller than the framing implies: **1,052 distinct replacement
objects**, not an open-ended space of mathematical moves.

## 2. The recorded action is demonstrably insufficient — and this number is valid

```
(P,A) groups                                   3,993,727
(P,A) groups with >= 2 rows                    1,251,927
  of those, containing BOTH outcomes             482,576
  collision rate among REPEATED groups           38.55%
```

**Among (parent, side) groups where the same recorded decision was actually taken more than once,
38.55% produced both outcomes.** Identical recorded decisions, materially different results. That
establishes logging insufficiency directly: `mutation_side` does not specify the intervention.

**Correction to my own earlier figure.** I first reported the collision rate as 12.08%. That used
*all* `(P,A)` groups as the denominator, including 2.7M singleton groups which cannot exhibit
multiple outcomes by construction. **38.55% is the correct statistic**; 12.08% was diluted by cells
that were structurally incapable of showing the effect.

## 3. Whether the COMPLETED action suffices is UNMEASURABLE on this corpus

```
(P,A+) cells                                   5,871,696
(P,A+) cells with >= 2 rows                            0
(P,A+) repeat rate                                  0.000
```

**Every completed intervention in this population occurs exactly once. Zero repeats out of
5,871,696.** `(P,A+)_cells` equals `rows_deduplicated` exactly.

Consequences, and the first one is a kill on my own near-claim:

- **`H(Y | P, A⁺) = 0` is an artifact, not a finding.** A singleton cell has zero entropy
  mechanically. I was one step from reporting "the completed action fully determines the outcome",
  which would have been false profundity of exactly the kind this program has killed before. The
  degeneracy guard was added specifically to catch it, and it did.
- **`dH_repeats_only = 0.3939` is equally invalid** — it subtracts a mechanically-zero term. Both
  ΔH figures in the rows file are void. They are retained in the JSON with `DEGENERACY_WARNING`
  rather than deleted, so the artifact is auditable.
- **The reviewer's Q4 instrumentation test cannot be run on this corpus as designed.** It requires
  within-`(P,A⁺)` outcome variation; there are no observations of that quantity. Per the
  pre-registration, this is a **VACUOUS** reading, not a null.

What *can* be said: since `(P,A)` groups repeat but `(P,A⁺)` cells never do, every repeated
`(P,A)` group is a set of *distinct* replacement objects. So the 38.55% collision is fully
attributable to replacement choice. That is **consistent** with `A⁺` determining the outcome and
**equally consistent** with `A⁺` also being insufficient. **The corpus cannot distinguish these**,
and no amount of it will, because the experiment that would distinguish them was never run.

## 4. Irreducible regret lower bound — valid, and it does not depend on repeats

```
irreducible regret LB          0.072693
over parents with both sides live    932,852
```

Per parent: (best outcome among observed completed interventions) − (best outcome reachable by any
policy that can only choose the *side*). Arithmetic only, no model, no repeat requirement.

**7.27% of decision opportunities carry outcome improvement that is mathematically unreachable by
any policy restricted to the recorded action vocabulary.** That is decision information the logger
discarded, quantified without fitting anything.

---

## Ruling

- The **UNDER-SPECIFIED ACTION** reading pre-committed in amendment 1b is **confirmed** for the
  recorded action (38.55% collision among repeated groups; 0.0727 irreducible regret).
- The complementary question — is the *completed* action sufficient? — is **VACUOUS**: zero repeats.
- The navigation thesis's true population for c1 × equal_mod_2 is **724,723 decision-bearing
  parents**, not 7,062,044 rows and not 3,060,875 parents. Roughly a tenth of the framing.
- **Amending the corpus-wide claim accordingly:** "transition structure lives in 181,424,844 rows
  (32.3%)" must not be read as 181.4M decisions. If c1's ratio is anywhere near typical, the
  decision-bearing share of the transition corpus is on the order of a fifth to a quarter of
  parents — and that is before any leakage-distinctness requirement, which can only shrink it.

**The regret experiment remains built, pre-registered, and NOT run.** It is now known to be
measuring a population an order of magnitude smaller than its pre-registration assumed, on an
action vocabulary that provably under-specifies the intervention. Both facts belong beside its
result, whatever the result is.
