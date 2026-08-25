# IQ-PORT-1 addendum — provenance by set membership, and a canary task that rewards being wrong

IQ-PORT-1 shipped **ADVANCE** at `28761a6f` with knockout, a mutation battery, state
injections and a footprint bound. It did **not** discharge requirement (4) as literally
stated: *show the winning pipelines and prove the op occurs in the newly successful ones —
set membership, not assertion.* Knockout is a statement about **one** pipeline. This closes
the gap. Same frozen evaluator hash, re-checked at run time.

Harness: `aporia/iq/run_provenance_audit.py`. Ledger: `aporia/iq/RESULT_PROVENANCE.json`.

---

## Scope, declared before the numbers

**464,652 pipelines**, enumerated exhaustively: all subsets of the 15 enumeration-reachable
transformers (the 13 live ones plus the two port ops) of size 1–6 = 9,948 subsets, each with
up to 8 valid orderings, each closed with all 36 O1 scorer tails; plus the ceiling body and
the ported body explicitly, which sit above the size cap. **Nothing sampled, no prefix taken.**
Not covered: subsets of size 7–15 other than the two named.

LOUD ACCOUNTING: 19,681 winners + 444,971 losers = 464,652 evaluated. **0 dropped.** The split
is asserted to partition in code. Exceptions inside `run_pipeline` count as *not solved*
rather than being discarded.

## HEADLINE — strict membership FAILS, and the failure is one degenerate task

    pipelines solving >=1 all_but_n task                     19,681
      WITH op_all_but_n:   943 solve 1  ·  14,807 solve all 5
      WITHOUT it:        3,931 solve 1  ·       0 solve 2, 3, 4 or 5

    max solved WITHOUT the port   1
    max solved WITH the port      5
    tasks ever solved without it  exactly one: index 33

Verdict: **PROVENANCE_CONFIRMED_MODULO_INCIDENTAL_HITS**, from a five-way branch table
asserted in code to partition every reachable reading. Strict membership at the ≥1 threshold
is **false** and is reported as false. The discriminating statistic — *does any non-port
pipeline reach the port's count?* — is **no, zero out of 464,652.**

Why the ≥1 threshold is the wrong line, stated as a model rather than an excuse: 4 candidates
per task, 5 tasks, so a uniformly guessing pipeline is Binomial(5, 0.25) with mean 1.25. One
incidental hit is the *expected* outcome. With 464,652 pipelines enumerated, per-pipeline tail
probabilities are uninformative — multiplicity swamps them. Which is why the audit reports the
**distribution**, not a p-value.

## The mechanism, identified by execution

The entire counterexample family is `parse_numbers → score_by_max_value` and its supersets.
Run over all five tasks it answers:

    idx 30  (T=15, N=1)   -> "1"    correct 14
    idx 31  (T=49, N=1)   -> "1"    correct 48
    idx 32  (T=5,  N=2)   -> "2"    correct 3
    idx 33  (T=10, N=5)   -> "5"    correct 5    HIT
    idx 34  (T=13, N=11)  -> "11"   correct 2

**It always returns N, the removed count.** It hits task 33 and only task 33 because that is
the one task where `T − N = N` — 10 − 5 = 5. The "alternate route" is a coincidence in the
task's parameters, not a route.

## The mutation battery had a hole, and this found it

IQ-PORT-1 preregistered four mutants (`T+N`, `T−N+1`, `N−T`, `T`) and P8 asserted **all**
mutants give ΔE exactly 0. All four do. But the mutant this diagnostic implies — *return N* —
was not among them. Executed now, together with a second wrong rule that lands on the same
degenerate task:

    M1_plus        dE +0.000000   0/5
    M2_off_by_one  dE +0.000000   0/5
    M3_swapped     dE +0.000000   0/5
    M4_identity    dE +0.000000   0/5
    M5_return_n    dE +0.008333   1/5      <- NOT in the preregistered battery
    M6_half_total  dE +0.008333   1/5      <- NOT in the preregistered battery
    TRUE PORT      dE +0.041667   5/5

**P8 as worded — "all mutants give ΔE 0" — is too strong for this canary and is corrected
here.** Two semantically wrong rules move ΔE by +0.0083 because one of the five tasks has
`T = 2N`. The defensible claim is the one the audit measures: **no semantically wrong rule
reaches the port's count, and the gap is 5/5 against 1/5.**

This is the self-identified weakness from the IQ-PORT-1 worklog — *"I chose which four
mutants to run; a mutant family I did not think of could pass where these fail"* — turning out
to be correct, and being closed by measurement one pass later rather than left standing.

## Consequence for TRANSFER-1, which is the next rung

The G-heldout generator must **exclude or explicitly stratify** parameter draws where
`T − N = N` (equivalently `T = 2N`), and more generally any draw where the target coincides
with an operand. One such task in five was enough to give two wrong rules a positive ΔE and to
break a strict provenance predicate. At generator scale this becomes a measurable contamination
rate rather than a single accident — which is exactly the kind of thing G-heldout exists to
control, and now has a concrete, pre-identified degeneracy to control *for*.

## What this does and does not change

- IQ-PORT-1's **ADVANCE stands**. ΔE_port = +0.0416667 = 5/120 is unchanged; nothing here
  touches the footprint, the knockout, the injections or the delegation probe.
- Requirement (4) is now **discharged**, with its result reported honestly as
  *confirmed modulo incidental hits* rather than as a clean pass.
- P8's wording is **corrected**, not quietly dropped.
- Novelty claim remains **ZERO**. Class `PORT_EXISTING_CAPABILITY`. Nothing here says anything
  about synthesis, discovery, abstraction learning or library growth — and the fact that this
  audit produced an interesting diagnostic is not an argument that the port is more
  scientifically interesting than its label allows. That would be the named bias.

## PIPELINE FROZEN

Per the ladder. Recorded in `RESULT_PROVENANCE.json → frozen_pipeline`:

    exhibited  parse_comparison · parse_which_extreme · parse_box_items ·
               parse_all_but_n · op_all_but_n · op_aggregate_quantities ·
               parse_rules · parse_ordinal · forward_chain ·
               parse_names_and_relations · relations_from_facts · op_build_ordering ·
               score_by_extreme_number__g · score_by_aggregate__g ·
               score_by_derivability__g · score_by_comparison__g · select_nth__g

    baseline pool   blackboard_evolve.REGISTRY — byte-frozen, never edited
    evaluator       10fa10db9989eb3a79c2039d18b748a83e93f751578ec6d0a0e12717eb0fa5ae
    harnesses       port_ops.py 6baff49dd03994be · run_iq_port_1.py 33ee51c8a590e8df ·
                    run_iq_null.py 152b714728858561 · run_provenance_audit.py (self)

**No further edits to the port, the harnesses or the pool without a new preregistration.**
IQ-NULL (already ADVANCE) and every downstream rung compare against exactly this configuration.
