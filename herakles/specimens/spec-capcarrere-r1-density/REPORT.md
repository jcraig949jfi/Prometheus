# spec-capcarrere-r1-density: footnote [13] replicated, one ranking clause only under one IC variant

Herakles, 2026-09-11. Rows: `derived/footnote13_screen.json` (same commit).
Runner: `herakles/eca/tools/run_capcarrere_screen.py`. Protocol:
`PROTOCOL.md`, committed at bea2f1c99 BEFORE the runner existed. Built from
c8d576e41 in the herakles-comms-queue worktree, branch
herakles/comms-queue-2026-09-11. Runtime 68.6 s.

Configuration exactly as preregistered: N = 149, T = 75, 1000 ICs per
seed, all 256 rules under two IC variants at two seeds; seven named rules
at five seeds; ICs shared across rules within a seed (paired).

## Predictions, as the predicates returned them

    P1  HOLDS    rules 184 and 226 score 1.000 on every IC, both variants,
                 all seven seeds (4000 screen ICs + 10000 named ICs per
                 rule). The theorem replicates. The controls below were
                 therefore read.
    P2  HOLDS    rules 57/99 in the preregistered band [0.50, 0.70] under
                 BOTH variants:
                   bernoulli        57: 0.5634  99: 0.5614  (5-seed means)
                   uniform_density  57: 0.5802  99: 0.5800
                 Per-seed Wilson 95% half-widths are 0.031 (n = 1000).
                 Neither variant lands on the paper's rounded 0.60; the
                 uniform-density variant is nearer (2.6 SE of the 5-seed
                 mean below 0.60; bernoulli 3.7 SE below).
    P3  FAILS under uniform_density, HOLDS under bernoulli.
                 bernoulli: top six are 226, 184 (1.000), 57, 99 (0.55 to
                 0.58), then 228 and 224 at 0.502. No intruder, both seeds.
                 uniform_density: rules 168, 172, 224, 228 score 0.599 /
                 0.585 (two seeds), ABOVE 57 and 99 (0.553 / 0.579). Under
                 that variant the footnote's "followed by rules 57 and 99"
                 is not reproduced.
    P4  HOLDS    57 and 99 agree within 2 SE under both variants (diff
                 0.002 and 0.0002 against se_diff 0.0098).
    P5  INDETERMINATE by its own predicate: P2 held under both variants,
                 so the preregistered discriminator does not separate them.
                 SEE THE UNPLANNED FINDING BELOW; it is reported beside
                 P5, not substituted for it.
    P6  HOLDS    rule 184 under the fixed-point criterion: 0.000
                 (bernoulli) and 0.014 (uniform_density; the 14 are ICs
                 already uniform or one step from it). The criterion
                 mismatch the 2026-09-10 catalogue warned about is now a
                 measured number, not an assumption.

## Controls (base rule 3), measured

    POSITIVE   184, 226:           1.000 everywhere (P1).
    CHEAT      planted 11 / 00 / alternation at steps = 0: fires (1.000),
               and the wrong planted block is refused (test suite).
    NEGATIVE   rule 0:   0.5022 (bernoulli), 0.5152 (uniform_density)
               rule 255: 0.4978,             0.4848
               rule 204: 0.0000,             0.1508
               The analytic chance floor of 0.5 is confirmed: 88 of 256
               rules sit in (0.45, 0.55) under bernoulli. Rule 0 + rule
               255 sum to exactly 1000 correct on every seed (odd N).
    WRONG      rule 184 under uniform_at_T: 0.000 / 0.014 (P6).
    CRITERION

## The unplanned finding, and what it may and may not be called

The preregistered discriminator for the IC distribution (P2's band) did
not discriminate. A clause I preregistered for a different purpose (P3,
the ranking) did: the published ranking "184, 226, then 57 and 99
trailing markedly" reproduces under i.i.d. Bernoulli(0.5) ICs and NOT
under uniform-density ICs, where four other rules overtake 57 and 99.

This is a LEAD, not a fact, and it is weaker than a preregistered
discrimination would have been, because the clause was not chosen for
this job before the run. What it may be quoted as: "the only one of the
two IC variants built that reproduces every clause of footnote [13] is
i.i.d. Bernoulli(0.5)". What it may not be quoted as: "the authors used
i.i.d. Bernoulli(0.5)". A third distribution not built here could also
reproduce all clauses. U1 stays UNSPECIFIED in the physics sheet with
this lead recorded beside it.

A hypothesis for the four intruders, written AFTER the numbers and so
worth exactly that: under the uniform-density ensemble most ICs are far
from 0.5, and a rule that merely drives a sparse ring toward 00-blocks
and a dense ring toward 11-blocks scores well there; under Bernoulli(0.5)
almost every IC sits within 0.04 of 0.5 and the same rules collapse to
the floor (0.502). The test of that hypothesis is a density-stratified
score, which was not preregistered and was not run.

## Corrections to my own protocol (annotations, not rewrites)

PROTOCOL.md U1 variant B says "the EvCA-line convention, evca.make_ics".
That attribution is wrong: `evca.make_ics` with density=None draws each
cell i.i.d. Bernoulli(0.5), which is variant A, and the EvCA line's
PERFORMANCE figures are defined over that unbiased ensemble (its GA
TRAINING sets are uniform-density). The variant definitions themselves
are unchanged and were run as written; only the parenthetical was wrong.
Annotated in PROTOCOL.md.

## Status of backlog items after this run

    L-2   RECOVERED. Paper in hand (ORIGINAL_SPECIMEN), rule executable
          in eca_rule_eval_v1 the same day, footnote [13] reproduced on
          its two exact clauses (184/226 at 100%) and its band clause
          (57/99 near 60%), with the ranking clause reproduced under one
          IC variant. The rule is HAND-DESIGNED, and the paper's own
          evolved rules (Sipper's cellular programming, refs [6], [7])
          are NOT recovered here.
    C-1   The fifth criterion is declared with its convention, floor and
          comparability in herakles/CRITERIA.md (this commit).
    X-4   A second lineage exists in the historical arm as a REFERENCE
          organism (EPFL LSL 1996). A cross-lineage claim about EVOLVED
          organisms still needs an evolved second-lineage rule; this does
          not close X-4.

## What would falsify this

- Any IC on which rule 184 fails the block convention at T = ceil(N/2):
  it would contradict a published theorem, so first suspect the
  implementation (the periodic pairing in `adjacent_pairs`, the horizon).
- A third IC distribution that reproduces every clause of footnote [13]
  would demote the lead to "one of several".

## What should stop

Nothing in this specimen needs further compute. The next step is a
recovery, not a run: the evolved radius-1 rules of the same laboratory,
so the second lineage holds an EVOLVED organism.
