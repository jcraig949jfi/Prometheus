+==============================================================================+
| APHRODITE LOCAL ENGINE -- SLICE 2B                                           |
| Independent lineages, hostile tribunal, bounded structural search            |
|                                                                              |
| Author:  Aphrodite (RSI science seat), machine M4                            |
| Date:    2026-09-21                                                          |
| For:     HITL (James) + external reviewers (no repo access needed)           |
| Status:  DISCOVERY YIELD 0/16 -- reported as the result, not repaired        |
| Self-contained: every load-bearing number is inline.                         |
+==============================================================================+

------------------------------------------------------------------------------
0. HEADLINE
------------------------------------------------------------------------------

discovery_yield = 0/16 qualifying artifacts / independently launched lineages.

The slice did NOT meet the RULING 6 success criterion. It produced three
findings that are worth more than a pass would have been:

  F1  The hostile tribunal works, brutally. Every lineage's numtheory
      shortcut scored 0.00 on counterexamples and failed metamorphic checks.
  F2  STRUCTURAL THEATRE. Three lineages satisfied criterion C6 with helpers
      whose entire contribution is `h // h == 1` -- the v1 coprime shortcut
      with a decorative loop bolted on. My C6 detector is gameable and was
      gamed, first time out.
  F3  MY AMENDMENT-3 PREDICTION WAS WRONG, for a precise reason. I predicted
      a helper would make the true numtheory program reachable. It does not.

No engine change was made in response to any of this. RULING 7 holds:
Campaign 1 unrun, engine outside eligibility, no endpoint touched.

------------------------------------------------------------------------------
1. WHAT RAN
------------------------------------------------------------------------------

16 preregistered lineages L-001..L-016, each with independently derived
development and search entropy under the frozen rule:

    dev_entropy(lid, gen)  = sha256("APHRODITE/ENGINE/DEV/v1/"+lid+"/"+gen)
    search_entropy(lid)    = sha256("APHRODITE/ENGINE/SEARCH/v1/"+lid)
    tribunal_entropy(c, i) = sha256("APHRODITE/ENGINE/TRIBUNAL/v1/"+c+"/"+i)

The tribunal domain contains no lineage identifier. Enforced rather than
promised: Tribunal.after_freeze raises BoundaryViolation without a frozen
artifact and ValueError on any generation other than 8, no lineage object is
ever handed a tribunal, and the run script evolves and hashes all 16
artifacts in phase 1 before the first tribunal is constructed in phase 2.

Total run: 37.1 s for 16 lineages, 8 generations each.

RULING 2 quantities, reported together and never as a pass condition:
    independent launched lineages         16
    distinct extracted artifact hashes    14
    non-base artifacts                    16
Lineage independence is now real: v1's ten lineages produced ONE hash; these
sixteen produced fourteen.

------------------------------------------------------------------------------
2. THE TRIBUNAL WORKS (F1)
------------------------------------------------------------------------------

Per-class results, identical in shape across all 16 lineages:

    class      held-out   counterexample   metamorphic
    modexp       1.00          1.00            PASS
    numtheory    0.61          0.00            FAIL     (15 of 16)
    numtheory    0.00          0.00            FAIL     (L-014)

modexp: every lineage independently discovered `pow(nums[0], nums[1]) %
nums[2]`, the true program, which survives counterexamples (m=1, a divisible
by m, a == m, a > m) and both metamorphic relations (reduction
g(a,b,m) == g(a mod m, b, m); recurrence g(a,b,m) == g(a,b-1,m)*a mod m).
This is a genuine, falsification-surviving, endogenously discovered,
cleanly transplanted program composition.

numtheory: the coprime shortcut again, and the counterexample generator takes
it to EXACTLY 0.00 -- the non-coprime regions (shared prime factor, one
number dividing the other, equal numbers, common multiples) are precisely
where `a*b + 1` cannot be right. The metamorphic checks reject it with no
oracle at all, since it violates both symmetry-scaling relations.

An ordinary held-out sample would have scored this 0.61 and called it a
partial success. The hostile tribunal calls it what it is.

------------------------------------------------------------------------------
3. STRUCTURAL THEATRE (F2) -- A DEFECT IN MY OWN CRITERION
------------------------------------------------------------------------------

3 of 16 artifacts (L-004, L-005, L-008) passed C6. Here is L-004's:

    helper:  while y != 0 and steps < 64:  x, y = (x + y), (x // x)
    answer:  (h(nums[0], nums[1]) // h(nums[0], nums[1])) + (nums[0] * nums[1])

`x // x` is 1, so y never reaches 0 and the loop runs to its bound. Then
`h // h` is 1. The program is `a*b + 1`: the v1 coprime shortcut, with a
decorative loop attached, scoring the same 0.61.

My C6 detector asked "does a helper with bounded control flow exist, and does
the answer path call it?" Both true. Neither means the helper does anything.
This is the failure form the ruling named -- "artifacts changing extensively
while all causal improvement rides on one trivial constant" -- and the search
found it without being aimed at it, because a decorative helper is cheap and
the criterion could not tell the difference.

C6 must require the helper to be LOAD-BEARING: substituting a constant for
its value must change the answers. That is an ablation test, and it is not
implemented in this slice. The defect witness
(test_structural_detector_rejects_a_DECORATIVE_helper) is committed RED with
L-004's actual program in its docstring.

I am not claiming these three as structural discoveries. Under a load-bearing
criterion, the structural count for this slice is 0 of 16.

------------------------------------------------------------------------------
4. MY PREDICTION WAS WRONG (F3)
------------------------------------------------------------------------------

AMENDMENT 3 section 0 predicted: "a helper makes the true solution reachable
at depth 3, because add(h, fdiv(mul(n0,n1), h)) is op(terminal, op(depth2,
terminal))." That prediction is FALSE, and the reason is checkable.

The composition search builds each round as op(LEFT from the current
frontier, RIGHT from the whole pool). The frontier holds only the expressions
created in the previous round. So `add(h, X)` -- where h is a TERMINAL and X
is a depth-3 expression -- is never constructed: h is not in any frontier
after round 1, and X is created in the same round it would be needed. The
enumeration is asymmetric, and the true program sits in the gap.

Direct diagnostic, run with a deliberately generous budget: the structural
search on numtheory development instances spent 276,178 candidate charges in
0.9 s and returned NOTHING. The true program was not missed by luck or by
budget. It is outside the reachable set, exactly as it was in v1 -- the
helper changed nothing about that.

So the slice-2 story needs its third correction: `a*b + 1` is not merely a
shortcut preferred over the truth, nor merely the best thing in a depth-3
space. It is the best thing in a space that STILL does not contain the truth
after the grammar was extended.

------------------------------------------------------------------------------
5. WHY THE YIELD IS 0 -- PRECISE ATTRIBUTION
------------------------------------------------------------------------------

Criterion failures across the 16:
    C4 survives counterexamples      15 failures
    C5 two falsified classes         16 failures
    C6 structural                    13 failures (and the other 3 are theatre)
    C1 endogenous                     0 failures
    C2 membrane                       0 failures
    C3 improves on tribunal           0 failures

C5 is unreachable for a structural reason, not a stochastic one: only one of
the two headroom classes has a program inside the reachable search space, so
no lineage can improve two falsification-surviving classes no matter how the
entropy falls. The 0/16 is therefore NOT evidence that discovery is rare. It
is evidence that one of the two targets is unreachable and that my structural
criterion could be satisfied without structure.

AMENDMENT 3 section 6 predeclared a possible zero yield with a different
cause -- "nothing rewards structure over a lucky shortcut before the freeze".
That mechanism is also visible (selection ties at development 1.00 go to the
incumbent), but it is not the binding constraint. Reachability is.

------------------------------------------------------------------------------
6. WHAT THIS DOES AND DOES NOT ESTABLISH
------------------------------------------------------------------------------

ESTABLISHED:
  - lineage independence is now real and measured (16 launched, 14 distinct)
  - a hostile post-freeze tribunal with counterexample generators and
    oracle-free metamorphic checks discriminates a true program (modexp,
    1.00/1.00/PASS) from a plausible shortcut (numtheory, 0.61/0.00/FAIL)
  - endogenous discovery of a true, transferable program composition
    (modexp) replicated across all 16 independent lineages
  - a criterion I wrote was gamed by the system on its first exposure

NOT ESTABLISHED:
  - no structural algorithmic change (STRUCTURAL_ALGORITHMIC_CHANGE remains
    NOT YET EXPRESSIBLE; the three theatrical helpers do not change this)
  - RSI: NO
  - nothing about Campaign 1; engine remains outside eligibility

------------------------------------------------------------------------------
7. RECOMMENDATION (stopping here, per the ruling)
------------------------------------------------------------------------------

Three things need a ruling before any further engine work:

  R-A  C6 must become a LOAD-BEARING test (ablate the helper; the answers
       must change). This is a criterion repair, and I have not applied it.
  R-B  The enumeration asymmetry (left from frontier only) is why the true
       numtheory program is unreachable. Repairing it is a search-space
       change made AFTER seeing a failure, which is the shape of tuning
       against an outcome -- so it should be authorised explicitly, or
       explicitly refused, rather than slipped in as a bug fix.
  R-C  Whether numtheory should remain a headroom class at all, given that
       the reachable-set analysis says its true program is outside the
       grammar. Keeping it makes C5 permanently unreachable; removing it
       leaves ONE falsifiable class and violates R5 of the eligibility rule.

------------------------------------------------------------------------------
8. QUESTIONS FOR THE REVIEWER
------------------------------------------------------------------------------

Q1. A criterion I wrote was gamed immediately by a search with no model in
    it and no intent. What does that predict about criteria written for
    systems that DO optimise against their evaluators?
Q2. Is "the true program is outside the reachable set" a property of this
    toy, or the general condition of every evolutionary system we would call
    self-improving? If the latter, what does "capable of discovering X" even
    mean as a claim about a search space?
Q3. The tribunal took a 0.61 result to 0.00. How much of published RSI
    evidence would survive an equivalently hostile post-freeze evaluation,
    and is there any way to find out without rerunning it ourselves?
Q4. I predicted helpers would unlock the target and was wrong in a way I
    could have checked analytically BEFORE running 16 lineages. What process
    change would have caught it -- and is "check the reachable set before
    running the experiment" a general rule or hindsight?
Q5. Is a 0/16 yield with these attributions more informative than a 1/16
    pass would have been? If yes, should the slice be counted a success
    against RULING 6 -- or does that reasoning corrode the criterion?

------------------------------------------------------------------------------
9. ARTIFACTS
------------------------------------------------------------------------------

  branch aphrodite/engine-2026-09-21
  8ae1b6989  AMENDMENT 3 + slice-2B invariant tests, committed RED
  roles/Aphrodite/engine/AMENDMENT_3_2026-09-21.md
  roles/Aphrodite/engine/run_slice2b.py
  roles/Aphrodite/engine/SLICE2B_RESULTS_2026-09-21.json   (per-lineage rows)
  roles/Aphrodite/engine/tests/test_slice2b.py   (12 tests, 1 RED witness)
  roles/Aphrodite/engine/tests/test_improver.py  (1 RED witness)
  suite: 30 passed, 2 failed -- both failures are defect witnesses

+==============================================================================+
| END. "The engine is now measuring its own criteria rather than the           |
| phenomenon" is a first-class answer, as is "stop: a substrate whose target   |
| programs are outside its own grammar cannot inform the model case."          |
+==============================================================================+
