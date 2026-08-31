# D-2 PHASE 1 VERDICT — `SUBSTRATE_INVALID`

Frozen documents: `MANIFEST.md` (design), `PREREG-CENSUS.md` (gates), committed at
`7e46665` **before** any census code was written.
Rows behind this verdict: `ledgers/census_*.json`, `ledgers/census_*_classes.jsonl`,
`ledgers/substrate_tests.json`, `ledgers/horizon_freeze_*.json`, `ledgers/phase1_summary.json`.

Per `PREREG-CENSUS.md` section 8: *"If no basis passes ST4, the verdict is
SUBSTRATE_INVALID and the run stops there."* No basis passed. **The run stops here.**
No grammar was repaired after its census. No world was built. No M0 or M1 was written.

---

## 1. What was measured

Four independently-plausible computational bases were censused against the same frozen
probe battery (24 artifacts, hash `a8951833623dc6d1`), the same 12/24 input batteries,
the same executable classifiers, and the same gates. The object language is G1 in all
four cases; only the transform basis varies.

```
basis    horizon  programs   live%    struct   nontrivial   CG-B   CG-C    CG-Cworst  CG-D
                              (>=1     classes  sem classes
                              valid
                              output)
G1  LISPY      6   904,880    4.61%      138        91      FAIL   .209    .582 *      .0 *
G2  PATHEDIT   6   185,640    0.16%      230       108      FAIL   .204    .787 FAIL   +1.0
G3  REWRITE    7   447,678   93.49%      273       270      FAIL   .178    .985 FAIL   -1.0 FAIL
G3B ONEPASS    7   447,678   93.51%      310       278      FAIL   .201    .978 FAIL   -1.0 FAIL
```
`*` = passes but is not robust; see section 3.

Horizons were frozen from program counts and evaluator timing alone, before any
classifier statistic existed (`ledgers/horizon_freeze_*.json`). G2's horizon is 6
because size 7 would have been 1,012,586 programs, 1.3% above the preregistered
1,000,000 cap; the rule was applied as written rather than adjusted.

## 2. Cause 1 — behavioural poverty of the enumerable region (CG-B, all four bases)

The gate required >= 500 behaviourally distinct transformations at the horizon. The
attainable maximum is the program count (185k–905k), so the gate was eligible to fire in
every case. Measured: **138, 230, 273, 310**. All four fail by a factor of 1.6x to 3.6x.
This is not a threshold call: three of four still fail at a threshold of 300, all four at 350.

Raw program count overstates richness by three to four orders of magnitude:

```
G1: 904,880 syntactic  ->  138 structural-behavioural  ->   91 non-trivial semantic
G3B: 447,678 syntactic ->  310 structural-behavioural  ->  278 non-trivial semantic
```

A diagnostic run confirms this is not an artefact of collapsing invalid outputs. When
non-programs are distinguished rather than collapsed, G1 has 3,194 structural classes —
but the number of **distinct valid artifacts ever produced**, across all 904,880
transforms applied to all 24 probes, is **154**. For G2 it is 361, G3 876, G3B 1,183.
The generically reachable artifact set is tiny.

**Mechanism.** The binding constraint is the validity filter: a structural edit of a typed
program is almost never a program. G1 produces a valid artifact from 4.6% of its
transforms, G2 from 0.16%. The two rewriting bases invert this — 93.5% "live" — but
almost entirely because a rule that matches nothing returns the term unchanged, so the
live mass collapses into the identity class.

## 3. Cause 2 — taxonomy-neutrality is not established (CG-C_worst, CG-D)

CG-C (legacy families <= 60% of non-trivial semantic classes) passes everywhere, with
shares of 0.18–0.21. **That pass is worthless on its own**, because the residual is
enormous and mostly uncharacterised: R2 (classes with no legacy label *and* no
substantive secondary audit) is 37% of G1's non-trivial classes, 58% of G2's, 81% of G3's
and 78% of G3B's. Section 9 of the brief anticipates exactly this, and the preregistered
CG-C_worst charges the unaudited residual against the hypothesis.

Under that charge: **G2, G3 and G3B fail outright** (0.787, 0.985, 0.978 against a 0.60
line). G1 "passes" at 0.582 — a margin of 0.018 — and that pass is not robust:

- it flips to FAIL at classifier consistency thresholds c = 0.7 and c = 0.8 (CG-H
  invariance fails for G1 and only for G1);
- it flips to FAIL at every gate threshold below 0.60 in the preregistered 0.40–0.80
  sensitivity sweep.

A gate passed by 0.018 that reverses under two independent perturbations is not evidence.
**No basis establishes taxonomy-neutrality.**

CG-D detects positive leakage in both rewriting bases: the median minimal size of a
legacy-labelled behaviour is **4** against **6** for non-legacy behaviour — recognisable
legacy families are strictly *cheaper* than the surrounding space, driven by RELABEL
(representation change), which costs a single 4-node rule. G1's CG-D margin is exactly
0.0 (5 vs 6 with a -1.0 allowance) and fails at an allowance of 0.5, so it is knife-edge
in the other direction. G2 is the only clean pass (+1.0).

## 4. Cause 3 — the useful region and the enumerable region are disjoint

ST3 built, by hand, the canonical transformation this experiment would have needed: lift a
seed core into a structural recursion,

```
M(core) = (if (null x) nil (cons core[x := (head x)] (self (tail x))))
```

two interacting structural edits (variable re-binding and control scaffolding) whose
decomposition would never have been given to a learner. It was verified executably on
three distinct cores — `M` really does map the core over a list.

**P0 is TRUE**: G1 and G3B both express it. But:

```
basis   substitution   scaffold   census horizon
G1          24            27            6
G3B          6            17            7
G2      inexpressible     17            6      (no conditional: a node cannot be
                                                 rewritten only when it is the variable)
G3           6            17            7      (diverges: every non-shrinking rule
                                                 fails to reach a fixpoint)
```

The witnesses sit 3x to 4x beyond the largest horizon that exhaustive enumeration can
reach under the compute cap. G1's space grows ~13x per size level, so size 27 is on the
order of 10^25 programs. The generically reachable region contains 91–278 distinct
behaviours; the useful region is unreachable from it by any history-free search.

This is what makes the intended experiment unfair rather than merely hard. A serious M0
would exhaust the entire generically reachable space, so any M1 advantage would consist
wholly of jumps *outside* the region the census can characterise — and the causal
comparison of section 21 would be comparing "covered everything cheap" against
"landed somewhere unverifiable".

## 5. Other substrate tests

- **ST2 determinism / totality**: PASS for all four bases. 4,000 sampled programs x 24
  probes each: zero escaped exceptions, zero non-deterministic results.
- **ST1 homoiconicity**: G2 **fails** — its constructor alphabet ranges only over the
  object language's symbols, so it cannot build its own syntax at all. G1, G3 and G3B
  pass, but with an important asymmetry that must not be glossed: G3/G3B can only rewrite
  the *symbol constants* inside another transform; their structural heads
  (`r1`, `rule`, `qp`, `L2`) are outside the constructor alphabet, so structural
  transform-of-transform is inexpressible there. **Only G1 is fully homoiconic**, because
  its `(q S)` alphabet contains its own primitive names by construction. P3 would have
  been available only on G1.
- **CG-F canonical order**: minimal-size statistics are identical across all 12 orderings
  (declaration, reverse, 10 seeded permutations) for every basis — the invariance check
  passes, so no implementation defect. Median Spearman rho between per-family min-rank
  vectors is 1.00 (G1, G2) and 0.976 (G3, G3B), above the 0.8 line, so rank claims would
  have been robust. No favourable ordering was engineered and frozen.
- **CG-G alias stability**: PASS for all four — growing the input battery from 12 to 24
  changed the semantic class count by 0.0%. Semantic equivalence is reported as
  probe-relative regardless; no claim of program equivalence is made anywhere.

## 6. The trade-off this run actually found

The four bases do not fail in the same way, and the pattern is the substantive result:

> **Behavioural richness at small program size and neutrality with respect to the human
> mutation taxonomy trade off against each other, and the mediator is the validity filter.**

A basis whose edits reliably produce valid programs is a basis whose primitives respect
the object language's syntax — and syntax-respecting edit primitives are precisely the
ones that look like the human taxonomy. G1, the most neutral basis (legacy share 0.21,
CG-D margin 0.0, the only fully homoiconic one), is also the poorest: 4.6% live, 154
reachable artifacts. G3B, the richest (93.5% live, 1,183 reachable artifacts, 310
behavioural classes), is the most leaky: legacy families two nodes cheaper than the rest
and 78% of its behaviour space uncharacterised.

This is a claim about these four bases at these horizons, not a theorem.

## 7. What is and is not established

**Established**
- P0, by executable witness: useful transformations of executable structure are
  expressible under two of the four bases, verified on three distinct seeds.
- The enumerable transformation space of all four bases is behaviourally tiny
  (138–310 distinct behaviours from 185k–905k programs).
- Both rewriting bases privilege a legacy family (RELABEL) by 2 grammar nodes.
- No basis establishes taxonomy-neutrality once the unaudited residual is charged
  adversarially.

**Not established — and no number in this run may be quoted toward any of it**
- P1 (discoverability), P2 (persistence/transfer), P3 (transform-of-transform),
  P4 (history-conditioned acquisition). No learner exists in this run.
- Any claim about what a history-conditioned search would do. M0 was never built, so the
  equal-opportunity static test, the anti-cheat battery, the world bypass census and the
  budget-accounting separation were **never run**. They are listed here as not-reached,
  not as passed.

**Forbidden conclusions** remain forbidden and none is claimed.

## 8. Stop

Per the stop rule, this generation ends here. Specifically I am **not** doing any of the
following, all of which would be assay-breeding a fifth grammar against a census that has
already been read:

- widening the alphabet so G2/G3 can construct their own syntax;
- relaxing the object language's validity condition to raise the live fraction;
- adding a `map`/`subst`/`at-path` primitive to G1 to pull the size-27 witness down into
  the enumerable region (that would *be* the human taxonomy, handed over as physics);
- raising the 1M horizon cap to buy CG-B a pass.

Each of those is a legitimate design for a *future independent experiment*, which must
freeze its own manifest and gates before it looks at anything. The lesson this generation
earned, stated for that successor and for no other use:

> The binding constraint is not whether a homoiconic substrate can express useful
> self-transformation — it can — but whether the *generically reachable* region of its
> transformation space is behaviourally rich enough for a history-free baseline to be
> given a fair fight. Measure the count of distinct reachable **artifacts**, not the
> count of programs, before designing any world.

A clean negative, preserved.
