# AMA problem / evaluation generator

Milestone 1 of the sequence in `PREREG_A0.md`. Builds sealed evaluation sets:
statements, submitted reasoning, and oracle metadata, with the metadata never
reaching the player.

No epoch runner exists yet, and none should be built until the manual protocol
works.

## 1. The five sealed classes

Named explicitly rather than as "five oracle classes", because the epistemic
distinction is the point:

| class | truth known to generator | argument | correct disposition |
|---|---|---|---|
| `TRUE_VALID_ARGUMENT` | TRUE | VALID | `TRUE` |
| `FALSE_WITH_WITNESS` | FALSE | INVALID | `FALSE` |
| `TRUE_BUT_INVALID_ARGUMENT` | TRUE | INVALID (planted) | `TRUE_BUT_INVALID_ARGUMENT` |
| `FALSE_BUT_HARD_WITHIN_BUDGET` | FALSE | INCOMPLETE | `FALSE` |
| `UNRESOLVED_WITHIN_BUDGET` | TRUE or FALSE | INCOMPLETE | `UNRESOLVED` |

`UNRESOLVED_WITHIN_BUDGET` is operational, not Gödelian. The generator knows the
answer because it enumerates under a budget the player does not have: the player
gets `BUDGET_SEARCH_SIZE` (200,000), the generator runs to 3× that. Nothing
undecidable is imported into the alpha.

The truth status of `UNRESOLVED` items is balanced 50/50 by construction, and
the pilot fails the set if it skews. Without that, an agent that guessed the
majority truth value would score above chance on the one class specifically
built to measure calibration.

## 2. Two oracles, disjoint routes

The requirement that truth and argument-validity be independent channels is
enforced structurally, not by convention.

- **Truth oracle** — `templates.py`. Each template decides its proposition by
  direct native-Python enumeration over the stated domain. It never evaluates a
  derivation step and never imports `derivation.py`.
- **Argument oracle** — `derivation.py`. Runs a machine check per proof step over
  a small expression language. It never asks whether the conclusion is true.

The only shared component is `exprlang.py`, and it shares arithmetic evaluation
only — no decision logic of either kind. Where a template's closed form appears
both as a native callable and as an expression string, the duplication is
deliberate.

**Where the channels necessarily agree.** For a claim exhaustively checkable
over a small finite domain, two correct implementations of the same enumeration
will reach the same verdict. Independence here means independent
*implementation*, not guaranteed disagreement. The class where they genuinely
diverge is `TRUE_BUT_INVALID_ARGUMENT`, and `pilot.py` reports that divergence
count.

**The coupling detector.** `pilot.py` fails any set containing a FALSE claim
whose argument is fully VALID. That would mean the step checks are too coarse to
notice a falsehood being derived — a defect in `derivation.py`, not in the
players. It caught a real one during construction: iterated-map items were
marking a generalization `justified` while the sweep stopped short of the
witness, so a false claim passed every step.

## 3. Compositional construction of `TRUE_BUT_INVALID_ARGUMENT`

No bespoke hand-authored bad proofs. The route is:

1. build a mechanically certified true claim with a derivation whose every step
   passes its check;
2. apply one mutation operator to one step;
3. re-run the argument oracle and require the mutated step to be the **unique**
   invalid step;
4. reject and resample otherwise.

The conclusion stays true structurally: mutations edit `steps` only and never
touch the statement, so the truth oracle cannot notice a mutation happened.

Every mutation rewrites the step's prose alongside its check. A mutation visible
only in the check would be invisible to a player, who never sees the checks.

## 4. Mutation families and the holdout

Frozen in `MUTATION_SPLIT.json`.

**Play (M1–M8):** quantifier strengthening, illicit cancellation, invalid
converse, domain widening, non-equivalent algebraic rewrite, case-cover gap,
unjustified independence, off-by-one boundary.

**Holdout (M9–M12):** invalid transitivity across ranges, vacuous instantiation,
induction base omission, modulus confusion.

Holdout families must never appear in an item a player sees during play. They
are the pool from which defense promotion tests are drawn, which makes Purple's
promotion bar operational: a defense is promoted only when it catches an attack
from a **sealed pool frozen before the defense was written**, rather than
because Purple declares the new attack independent.

Template coverage per family is uneven and measured rather than assumed:

- M1, M3, M6 — all six templates
- M2, M4, M5, M7, M8, M9, M10, M12 — five templates
- M11 — three templates (needs a point-specific base case)
- t3 hosts only M1, M3, M6, M7, M8, M10, M12

**Known gap:** M9 and M11 cannot be planted in `t3_min_degree_connectivity`, so
the `new_mut_new_domain` transfer cell draws from M10 and M12 only. It is
narrower than the other two cells. Recorded in `PLAY_SCOPE.json`.

**t3 hosts no `FALSE_WITH_WITNESS` item.** Its only false instance (v = 6,
d = 2) has its first counterexample at enumeration index 5905, past the 5000
boundary of the easy band, so it is a `FALSE_BUT_HARD` item. The band decides
the class, not the template's intent. This surfaced as a generator failure —
every t3 `FALSE_WITH_WITNESS` attempt exhausted its retries — rather than as a
mislabelled item, which is the behaviour we want from a postcondition check.

**Known adjacency:** M4 (domain widening) and M9 (invalid transitivity) are
neighbouring mechanisms — both end with an assertion over a range wider than
what was established. A defense built for one may catch the other for reasons
that have nothing to do with abstraction. If M9 falls to an M4-derived defense,
read that as a family-boundary artifact before reading it as transfer.

## 5. Templates and domains

| id | domain label | classes |
|---|---|---|
| `t1_integer_sum_identity` | integer_identities | TRUE_VALID, FALSE_WITNESS, TRUE_INVALID |
| `t2_modular_power_cycle` | modular_arithmetic | same |
| `t4_linear_recurrence` | recurrences | same |
| `t3_min_degree_connectivity` | finite_combinatorics | TRUE_VALID, TRUE_INVALID, FALSE_BUT_HARD |
| `t5_collatz_stopping_time` | elementary_number_theory | all five |
| `t6_shortcut_stopping_time` | recurrences | all five |

Every template ships an independent oracle that is not the claim's own verifier,
as `PREREG_A0.md` section 6 requires.

**The structural confound.** Only the two iterated-map templates can host
`UNRESOLVED_WITHIN_BUDGET`, and they carry most of `FALSE_BUT_HARD_WITHIN_BUDGET`
(t3 supplies the rest). The cause is real, because clean
elementary mathematics has short certificates and opacity is what makes a claim
genuinely unresolvable within budget. So template identity carries real
information about the sealed class.

This is measured, not waved away. `pilot.py` reports `I(template_id; class)` and
`I(domain_label; class)` in bits, **read against a 2000-draw label-shuffle null**
rather than against a bare threshold — mutual information on a sparse joint
histogram is biased upward, and at these sample sizes the bias is the dominant
term. The set fails only when the observed MI exceeds the null's 95th percentile
*and* exceeds 35% of class entropy.

On the 40-item pilot both sit at 0.506 bits of 2.322 (22%), against a null mean
of 0.274 and p95 of 0.431: real signal, under the ceiling. Three mitigations
keep it there — t5 and t6 also produce decoy items in the three easy classes, t6
carries the `recurrences` label that t4 also carries, and t3 hosts
`FALSE_BUT_HARD` so the opaque templates are not the sole source of a hard class.

**The gate has no power at n ≈ 10.** On the transfer sets the observed MI falls
inside the shuffle null (0.971 observed against p95 1.171 at n=10), so the honest
report is "indistinguishable from chance", not "clean". Those sets must be
enlarged before any confound claim about them means anything.

## 6. Transfer cells

`PLAY_SCOPE.json` declares the play scope before play, so the three cells are
defined by construction rather than after the fact.

- play templates: t1, t2, t4, t5
- reserved: t6 (new problem, domain already seen), t3 (new domain)

| cell | families | templates | tests |
|---|---|---|---|
| `same_mut_new_problem` | play | t6 | basic reuse |
| `new_mut_same_domain` | holdout | t1, t2, t4, t5 | abstraction |
| `new_mut_new_domain` | holdout | t3 | the interesting one |

## 7. Public / sealed separation

`public/<claim_id>.json` — statement, domain, quantifiers, hypotheses, and the
argument **as prose only**. `sealed/<claim_id>.json` — everything else.

Step checks are stripped from the public package. Shipping them would hand over
the planted defect's location, since running them prints it.

`pilot.py` scans every public package for sealed field names, mutation family
ids, machine checks, and witness values appearing verbatim.

## 8. Re-execution oracle

`oracle.py` rebuilds each proposition as a point predicate from the sealed
parameters, so the harness can adjudicate a submitted witness rather than trust
it. It checks two things separately:

1. is the point inside the quantified domain?
2. does the proposition actually fail there?

A witness failing (1) is not a counterexample regardless of (2) — the most
common bogus kill, and the basis of the invalid-falsifier rate.

## 9. Commands

```
python generate.py --set-name A0_EVAL --seed 20260825 --count 40 \
    --families play \
    --templates t1_integer_sum_identity,t2_modular_power_cycle,\
t4_linear_recurrence,t5_collatz_stopping_time

python generate.py --set-name XFER_NEW_MUT_NEW_DOMAIN --seed 990003 --count 9 \
    --transfer-cell new_mut_new_domain \
    --classes TRUE_VALID_ARGUMENT,FALSE_WITH_WITNESS,TRUE_BUT_INVALID_ARGUMENT

python pilot.py --set ../heldout/PILOT_A0
```

Determinism: the same (seed, set name, count, class mix, template pool, family
pool, budget, generator source) reproduces a set byte for byte. `pilot.py`
verifies this by regenerating into a temp directory and diffing.

## 10. What the pilot does not establish

It is an instrument calibration. It shows the machinery separates the five
classes on input built to be separable, that sealed data does not leak, and that
a fabricated kill is rejected. It says nothing about whether live agents produce
anything worth scoring, and it must not be reported as a result.

Open weaknesses, stated rather than buried:

- `UNRESOLVED_WITHIN_BUDGET` rests on "no short certificate known to the
  generator". An agent that finds one has not cheated — it has shown the budget
  model was too generous, and the pilot's separate reporting of TRUE-guesses and
  FALSE-guesses on this class is how that would surface.
- `FALSE_WITH_WITNESS` witnesses can land at n = 1, which is free to find. The
  band admits [1, 5000] and the pilot reports the observed range.
- 8 items per class gives 6 of 8 mutation families in the `TRUE_INVALID` cell.
  Even family coverage needs a larger set.
- The confound gate is underpowered below roughly n = 30. It reports this rather
  than passing quietly, but the transfer sets as generated (n = 9–12) cannot
  support a confound claim either way.
- t3 items cost 2–6 s each to build because every step check enumerates all
  32,768 labelled graphs on 6 vertices. A 9-item t3 set takes ~45 s. This is a
  throughput limit on `new_mut_new_domain`, not a correctness problem.
