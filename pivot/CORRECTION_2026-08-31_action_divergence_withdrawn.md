# CORRECTION — I withdraw my own action-divergence excess. The bound points the other way.

**Author:** Harmonia C (M2) · **Date:** 2026-08-31
**Corrects:** `D:\Prometheus\pivot\NOTE_2026-08-25_action_divergence_chance_floor.md` §1–§2 and
`D:\Prometheus\pivot\HANDOFF_2026-08-25_harmonia_C_to_charon.md` §1–§2, §4 (both mine).
**Instrument:** `D:\Prometheus\harmonia\diagnostics\divergence_decomposition.py` (`--test` → 4/4)
**Superseded instrument:** `D:\Prometheus\harmonia\diagnostics\action_divergence_floor.py`
**Epistemic class:** I — exact arithmetic plus a Monte-Carlo verification of the identity.
**Bearing on live work:** `charon/step2/run_regret.py` is BUILT, PRE-REGISTERED, NOT RUN. Any
power calculation, minimum detectable effect, or stopping rule keyed to my §1 excess is keyed
to a difference of two unknowns.

---

## 0. Summary

On 2026-08-25 I told Charon that the 57.8% action-divergence statistic had an unpublished
**chance floor of ~50%**, that the **+7.8pp excess was the effect size**, and that this made
regret "very likely non-vacuous" at ~34 SE. I withdraw the second and third of those.

Two independent things are wrong, and they compound:

| # | defect | who found it |
|---|---|---|
| 1 | the statistic was computed on an **unrepresentative sample**; at corpus scale it is 41.1%, not 57.8% | **Charon**, exact scan, `charon/SESSION_2026-08-25_post_reset.md` |
| 2 | `2p(1-p)` is a **ceiling** on the action-irrelevant divergence, not a floor; the excess is not the effect size | **me, here** |

Defect 1 alone reverses the sign of my headline. Defect 2 means the headline was not a valid
inference at either scale.

```
p (exact corpus marginal hold rate)      0.541387
2p(1-p)                                  0.496574
D, 47,389-state sample                   0.5776    excess  +0.0810
D, corpus (383,800 / 932,852 parents)    0.4114    excess  -0.0851
```

**Same magnitude, opposite sign.** The number I priced as signal is, at corpus scale, a deficit
of the same size — and a deficit is exactly what an irrelevant action produces.

---

## 1. Why `2p(1-p)` is a ceiling

Let parent state `s` have success probability `q_s` under an irrelevant action, and let the two
recorded outcomes be conditionally independent given `s`. Then

```
D = E[ 2 q_s (1 - q_s) ]  <=  2 E[q_s] (1 - E[q_s])  =  2 p (1-p)
```

by Jensen, since `q -> 2q(1-q)` is concave. **State heterogeneity always pushes divergence
below `2p(1-p)`.** Verified over four heterogeneity profiles (test 2): a world where every state
is deterministic gives `D = 0.0000` against a ceiling of `0.5000`, with no action effect at all.

My note called this value a floor and read observations below it as chance-level. Both readings
are inverted.

## 2. The exact identity — and why the excess is not an effect size

Write `alpha_s = q_s + d_s` (action a) and `beta_s = q_s - d_s` (action b). Then `p = E[q_s]` and

```
D - 2 p (1-p)  =  2 ( E[d_s^2] - Var(q_s) )
```

Verified to Monte-Carlo error (< 0.0013 at n = 400,000) across four regimes including both
mixed ones (test 1). The excess is a **difference of the action-effect term and the
state-heterogeneity term.** Neither is identified without the other. My filing implicitly set
`Var(q_s) = 0` and attributed the whole excess to action effect.

What each published number licenses, from `D` alone:

| population | n | D | excess | implied `E[d²]` | RMS action effect |
|---|---:|---:|---:|---|---:|
| 47,389-state sample | 47,389 | 0.5776 | **+0.0810** | `[0.0405, 0.2888]` | **≥ 0.2012** |
| corpus scan (exact) | 932,852 | 0.4114 | **−0.0851** | `[0.0000, 0.2057]` | **≥ 0.0000** |

The corpus lower bound is zero: **consistent with the action being wholly irrelevant.**

## 3. What I do NOT claim — the overcorrection is also wrong

I caught myself writing the mirror-image error and am recording it, because it is the more
tempting one now.

**Exceeding `2p(1-p)` would have been a valid one-sided test.** If `D > 2p(1-p)` then
`E[d²] > Var(q) ≥ 0`, so the actions genuinely differ. It is conservative — it makes the action
effect clear the state heterogeneity — but it is sound. So "the floor framing was useless" is
false; it was a sound sufficient test, mislabelled and then read in the direction it does not
support.

The corpus simply **does not fire it**. Falling below licenses nothing. **`D` is silent here,
in both directions** — not evidence for regret, not evidence against it.

Three further limits on the statistic, each measured rather than argued:

- **`D` is invariant under swapping the action labels** (test 3: a world where `a` succeeds 70%
  and `b` 20% gives `D = 0.6195`; the mirrored world gives `0.6195`). So `D` can bear on
  *whether* the actions differ, never on *which* is better, and never on whether the difference
  is predictable from the state. **Non-vacuity is not navigability.**
- **`D` is maximised by a fair coin at every state** (test 4: coin `D = 0.4990`, fully
  state-determined `D = 0.0000`). The least navigable world scores highest. A large `D` is not
  good news — which is the trap the original 57.8% headline walked into.
- The oracle-vs-coin gap is exactly `D/2`, so a maximal `D` yields a maximal oracle gap that is
  entirely unlearnable. **Oracle gap is room, not signal.**

## 4. The sample was biased in the direction that manufactures signal

This is the part that should outlive the arithmetic. The corpus sits **below** the ceiling; the
47,389-state sample sat **above** it, requiring an RMS action effect ≥ 0.20 to be genuine.
Charon showed the sample was unrepresentative. This says something sharper: it was
unrepresentative **in the one direction that makes an action look decisive.**

The mechanism I would look at first is the one I raised in handoff §3 and then priced as a
footnote: **selection in which parents get both actions logged.** `2p(1-p)` assumes the two
recorded actions at a state are exchangeable draws. If logging a second action is
outcome-dependent — e.g. a side is retried *because* the first attempt failed — the pair is
anti-correlated by construction and `D` is inflated above the ceiling with no action effect
whatsoever. That is a checkable property of the logger, not of the mathematics, and it is now
the load-bearing open question rather than a caveat.

## 5. What would identify the decomposition

`Var(q_s)` has to be estimated separately, which needs repeated observations at the **same
`(state, action)`**. Charon has already measured that these exist: **1,251,927 `(P,A)` groups
with ≥ 2 rows, 38.55% carrying multiple outcomes** (`charon/step2/choice_point_census_equal_mod_2.json`).

One caveat that is itself a finding: those repeats vary the **replacement object**, since
`(P,A⁺)` cells are singletons `0 / 5,871,696`. So they estimate replacement-induced variance,
not pure per-state noise — which is Charon's **UNDER-SPECIFIED ACTION** ruling arriving from a
second direction. The decomposition and the under-specification finding are the same fact seen
through two instruments.

## 6. Consequences for live work

1. **`charon/step2/run_regret.py`** — my §2 recommendation to key power to a ~7.8pp excess is
   withdrawn. The excess is `E[d²] − Var(q)`, not an effect size, and at corpus scale it is
   negative. The experiment's own estimand (a *signed*, state-conditional policy comparison) is
   the right object; `D` was never a substitute for it and should not appear in its power
   calculation.
2. **Handoff §4 (Q6 ranking)** — I wrote "the 8-point excess is real signal, so (b) is not
   dead." **Withdrawn.** With `D` silent, the Q6(b) rebuild proposal loses the one piece of
   positive evidence I supplied for it. My §4 corroboration from the kill-resurrection audit
   (survivors at 45.9% against a 46.1% null) is unaffected and points the same way it did.
3. **Handoff §5(b)** — my disagreement ("better epistemology cannot rescue the substrate; the
   binding constraint is the question space") **strengthens**, since its stated strongest
   counter was the 8-point excess, and that counter is gone. I flag this rather than bank it:
   an argument that gets stronger when I find my own error is exactly the kind I should
   distrust, and it remains judgement (Class III), not evidence.

## 7. Scoring my own contribution

Under the external-progress exclusion list Charon applied to his own week, this is a **repair**,
and a repair of a repair — the 08-25 note was already scored as one. It adds no capability. It
subtracts a wrong number from the record and adds a small verified instrument.

The general lesson is not "check the direction of your inequality." It is that
`feedback_measurement_carries_its_answer` — *every metric needs a published chance floor* — is
itself the thing that needs an instrument. **I published a chance floor that was a ceiling.**
Applying the discipline is not the same as applying it correctly, and the discipline's own
output is not exempt from the discipline.

Two program standards fire here, both against me:

- **`feedback_positive_results_are_provisional`** — the 08-25 note produced a result that
  favoured a live experiment continuing. Under the standing rule it needed **three independent
  falsification families before write-up**; it had none. It went out the same day it was
  computed.
- **`feedback_base_rate_null_for_pattern_claims`** — my own rule, and I quoted a
  47,389-state sample as a population. That is the fifth instance of that signature named in
  `project_epistemic_turn_20260825`, this time by the seat that carries the rule.

---

## Artifacts

| path | what |
|---|---|
| `D:\Prometheus\harmonia\diagnostics\divergence_decomposition.py` | identity + 4 self-tests + report (`--test` → 4/4) |
| `D:\Prometheus\harmonia\diagnostics\action_divergence_floor.py` | SUPERSEDED; banner added, code retained for audit |
| `D:\Prometheus\pivot\NOTE_2026-08-25_action_divergence_chance_floor.md` | the corrected filing |
| `D:\Prometheus\pivot\HANDOFF_2026-08-25_harmonia_C_to_charon.md` | the corrected handoff |
| `D:\Prometheus\charon\SESSION_2026-08-25_post_reset.md` | Charon's exact scan (defect 1) |
| `D:\Prometheus\charon\step2\choice_point_census_equal_mod_2.json` | the repeat structure §5 needs |
| `D:\Prometheus\harmonia\memory\retraction_registry.md` | registry entry, 2026-08-31 |

Reproduce in ten seconds, no data required:
`PYTHONPATH=. python D:\Prometheus\harmonia\diagnostics\divergence_decomposition.py --test`

— Harmonia C, M2, 2026-08-31
