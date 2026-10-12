# Falsifiability of claim-critical controls -- a qualification requirement (C-018-T012)

Directive 2026-10-12 s2B. Required from C-018 on.
- **Who:** every preregistration the Observatory freezes has a table answering the items below, one row per
  claim-critical control or baseline.
- **Where it is used:** the integrator checks the table, and the Q3 challenge set tests it.
- **Executable checks:** rso/qualify/falsifiable.py. Each one is tested on a miniature of the historical case it
  comes from (rso/qualify/tests/).

## Why this exists

Four campaigns produced controls that could not fail meaningfully, and each was found only by a challenge or by the
integrator.

| Campaign | Control | Why it could not fail | Check that catches it |
|---|---|---|---|
| C-013 D1 | analyze.py success count | It counted the runner's derived `discovery` field; tampered components did not change it | `trusts_derived` |
| C-016 Ensorain | K1, full vs the subject's own frozen arm | Perturbation noise beats a frozen arm that scores 0; the verdict depended on the innate value | `near_miss_rejected` (jitter) |
| C-017 Z80 | b1 / b2 must fail Q1 | Neither could output ENV, so they "failed" by construction | `cannot_emit`; audit `must_discriminate` |
| C-017 Z80 | Q2 origin | "Always INSERTED" passed for every possible outcome | `constant_passes` |
| C-017 Z80 | recipe lookup table | A table keyed on the registered arms is the ground-truth table | `reads_answer` (scrub the arm field) |

## The checklist: one row per claim-critical control

1. **Alternative.** Which simpler scientific explanation does this control stand for? Name it: copying, routing, a
   fixed prior, noise, recipe reading, initial geometry, and so on.
2. **Pass observation.** What would the control show if the alternative were true?
3. **Fail observation.** What would it show if the alternative were false?
4. **Impossible by construction?** Can the experimental construction ever produce both outcomes?
   - Run `cannot_emit` against the classes the control must discriminate.
   - Run `constant_passes` and `oracle_fails` against the pass rule.
   - A control that cannot produce a required classification does not discriminate that classification.
5. **Privileged access?** Does it read the answer: an arm name, a recipe table, a stored label, a derived field?
   - Run `reads_answer` with a scrub that removes only the answer-bearing fields.
   - Run `trusts_derived` with a tamper that makes the components contradict the derived field.
6. **Discriminates?** If it fails, does that separate the target mechanism from the alternative? A registered
   NEAR-MISS or COUNTERFEIT is required for every important inference:
   - a case that imitates the target;
   - its truth known by construction;
   - classed correctly by the instrument;
   - recorded with `near_miss_rejected`.
   An empty near-miss set is not a pass.

## How it enters qualification

- **Preregistration.** A preregistration without this table is incomplete, and the integrator does not freeze it.
- **The audit.** For every control, `audit(...)` must come out ok on development data before the freeze. A finding
  that cannot be repaired is written into the claim's scope, as the C-017 Q2 and Q4 narrowings were.
- **The challenge.** The Q3 challenge set must include at least one attack per row. Two attacks are standard: a
  constant detector, and a scrubbed or tampered input.
- **Scope of the checks.** They are necessary conditions, not sufficient ones. They catch a control that cannot
  fail; they do not prove that a control which can fail is the right control.
