# Cycle 022 — 2026-08-21 — SECOND PASS opens: instrument sweep

**Track 1:** `prometheus_math.partition` — refinement and Meilă's variation of information,
motivated directly by what the sweep needed.
**Track 2:** uniform instrument sweep of the rungs built before the instruments existed.

272 green. **Note on process:** HITL #60 (second-pass ordering) has not been ruled on, so I
proceeded with the proposed order and am recording that I did. The sweep is capped at two
cycles; cycle 024 moves to composition or real substrate regardless of what remains.

## R3 — the outstanding ledger claim was TOO BROAD, and is narrowed rather than struck

Carried since cycle 018 as an unverified claim of aliasing. Resolved, and the resolution is a
defect.

The cycle-006 twins **do** alias the FIFO pipelines: the flood evicts `xq`, both histories leave
identical bounded state, the queried proposition differs, and every width in the family answers
the same thing for both — wrongly on one.

They **do not** alias the LIFO pipelines. LIFO evicts the most recent arrival, so a fact
declared *first* is exactly the one it keeps. `xq` survives the flood and the LIFO pipeline
separates the twins perfectly. The witness was FIFO-specific and the ledger claim was
unqualified.

**The repair is not a cleverer pair.** FIFO and LIFO views are **incomparable** — measured, in
both directions, by `verify_factorization` and independently by partition refinement — so no
finest projection exists for the union short of the full history. Incapacity must be proved per
observation class, which is exactly the precondition cycle 019 added after external review, now
found in the wild rather than in a constructed example. `twins_for_policy` builds the right pair
for each class; `xq` must arrive *last* to be the fact LIFO evicts.

The rung's actual separation survives the narrowing: the unbounded constraint store answers both
twins correctly under both policies' pairs.

## R0 — the sweep found a limit in the ALIASING INSTRUMENT itself

R0 reports **no aliasing witness**. Every rung swept so far has yielded one, so a clean report
was the surprising outcome — and it is not a clean bill of health. Exact-AST keys never merge
two distinct expressions, so under-discrimination is impossible by construction. R0's defect
runs the other way.

> **Aliasing detects merging. It is silent on splitting.**
>
> - *Under-discrimination:* `π(x₁) = π(x₂)`, `T(x₁) ≠ T(x₂)`. An **impossibility** — no member
>   of the family is correct on both.
> - *Over-discrimination:* `π(x₁) ≠ π(x₂)`, `T(x₁) = T(x₂)`. **Not** an impossibility. The
>   family can be correct on both by treating them separately; what it loses is transfer.

`x + y` and `a + b` share an answer and receive different exact-AST keys. `find_splitting_witness`
is the dual instrument, and `SplittingWitness` carries `proves_impossibility = False` **as a
field, not only in the prose** — because reporting a generalisation cost as if it were an
impossibility is precisely the evidence-typing error of claim v12, and I would rather the data
structure refuse it than trust myself to remember.

The dual witness dissolves under the repair the rung already had: the canonicalising circuit
transfers `x + y`'s answer to `a + b`, the exact circuit abstains.

**Second R0 finding, of the cycle-013 family.** `ast_key` **cannot see commutative reordering**:
`srepr(x + y) == srepr(y + x)`, because sympy normalises commutative arguments at construction.
So the circuit's advertised "identity congruence" is partly delivered by the CAS rather than by
the circuit, and it retrieves `y + x` from a store trained on `x + y` without having earned it.
Not fatal, but a claim about the circuit's discrimination should not rest on it.

## Track 1 — `prometheus_math.partition`

Every projection induces a partition (its fibres), and the sweep's questions are partition
questions: *does one view factor through another* is refinement; *how far apart are two views*
wants a metric. `refines`, `entropy`, `mutual_information`, `variation_of_information`.

Reference: M. Meilă, *"Comparing clusterings — an information based distance"*, J. Multivariate
Anal. 98 (2007), 873–895. VI is a true metric on the partition lattice, which matters here: a
non-metric similarity would let "these two evaluators see almost the same thing" fail to compose
across a chain. Authority tests include the refinement identity `VI(P, Q) = H(P) − H(Q)` when P
refines Q; property tests cover non-negativity, symmetry and the **triangle inequality**; edges
include the incomparable-partitions case that the R3 finding turns on. Composition tests chain
it against `aliasing.verify_factorization` and against R0's own key functions.

Writing that composition test is what surfaced the sympy-normalisation finding — the test
asserted the canonical partition was strictly coarser and it was not.

## Sweep status

Swept: R0, R3 (this cycle), plus R6, R9, R10, R11, R12 during the first pass.
**Remaining: R1, R2, R4, R5, R7, R8** — six rungs, one cycle left in the cap.

## TLDR — ELI5

Two jobs this cycle, and both turned up something.

The first was an old loose end: we'd claimed a memory-limited circuit *provably* can't tell two
situations apart. Half right. It can't — if it forgets the oldest thing first. If it forgets the
newest thing first, it can tell them apart easily. The two forgetting policies aren't better and
worse versions of each other; they're just different, and neither sees a subset of what the
other sees. So the proof has to be done separately for each, and the old claim was written as if
one proof covered both.

The second was worse and more useful. Our tool for finding blind spots only finds *one kind* of
blind spot — when a grader can't tell two different things apart. It's completely silent on the
opposite mistake: treating two things as different when they're the same. That second mistake
isn't fatal the way the first is — you can still get both right, you just have to learn each one
separately instead of learning once — but it's a real cost and we had no way to see it. Now we
do, and the new tool has a flag on it saying "this is not a proof", so nobody (me) reports it as
one later.

## For ChatGPT

```
Prometheus loop, cycle 022 — first cycle of the SECOND pass over canon R0-R12. The plan is to
sweep the rungs built before the instruments existed (R0-R5, R7-R8), capped at two cycles so it
cannot absorb the whole pass. 272 green.

1. R3 RESOLVED, AND THE OLD CLAIM WAS TOO BROAD. Our ledger carried "R3 capacity width" as an
unverified aliasing claim since cycle 018. Measured: the cycle-006 twins DO alias the FIFO
pipelines (flood evicts the queried fact, identical bounded state, every width wrong on one
twin) and do NOT alias the LIFO ones (LIFO evicts the most RECENT arrival, so a fact declared
first survives, and LIFO separates them perfectly). FIFO and LIFO views are INCOMPARABLE in
both directions — verified twice, by verify_factorization and independently by partition
refinement — so there is no finest projection for the union short of the full history, and
incapacity has to be proved per observation class. That is exactly the precondition you added
in round 7, now found in the wild rather than in a constructed example. Claim narrowed, not
struck; twins_for_policy builds the right pair per class.

2. SWEEPING R0 FOUND A LIMIT IN THE ALIASING INSTRUMENT. R0 reports NO aliasing witness, which
was the surprise — every rung swept so far yielded one. The reason: exact-AST keys never merge
two distinct expressions, so under-discrimination is impossible by construction. R0's defect is
the OTHER direction. Aliasing detects merging (pi equal, truth differs: an impossibility) and is
silent on splitting (pi differs, truth equal: NOT an impossibility — the family can be right on
both, it just cannot transfer evidence between them). Built find_splitting_witness as the dual,
with proves_impossibility=False as a FIELD rather than only in the docstring, because reporting
a generalisation cost as an impossibility is exactly the v12 evidence-typing error.

3. SECOND R0 FINDING, cycle-013 family: srepr(x+y) == srepr(y+x), because sympy normalises
commutative arguments at construction. So the exact-AST circuit's "identity congruence" is
partly delivered by the CAS, and it retrieves y+x from a store trained on x+y without earning
it. Found by writing a composition test that asserted the canonical partition was strictly
coarser — it was not.

Track 1: prometheus_math.partition — refinement plus Meila (2007) variation of information, a
metric on the partition lattice. Motivated by the sweep: every projection induces a partition
and the sweep's questions are partition questions.

What I want attacked:
1. Is the splitting/merging duality actually the right frame, or is there a third failure mode
   of a projection I am not seeing? My current claim is that a projection can only be wrong by
   merging what differs or splitting what agrees, and that these have different logical force
   (impossibility vs generalisation cost). That feels exhaustive, which by now makes me suspect
   it.
2. Over-discrimination has no impossibility attached, so it is not clear what the RIGHT
   measurement of it is. Pair count is arbitrary — it scales with the battery. Should it be
   the VI between the evaluator's partition and the truth partition, so "how much finer than
   necessary" is a number of bits? That is available now that partition.py exists, and it would
   make the two directions symmetric: aliasing gives an impossibility, splitting gives a bit
   count.
3. The R3 result says incapacity must be argued per observation class. That is fine with two
   policies. Is there a case where the number of observation classes is unbounded — in which
   case per-class proof is not a repair, it is an infinite regress, and the honest report is
   "no impossibility result is available for this family at all"?
```

## Traps ledger additions

- **Policy-specific witness reported as family-wide** — a witness constructed against one
  eviction/tie-breaking policy does not bind members using another when the views are
  incomparable. Defence: check factorization across the whole family, not within one policy.
- **CAS-delivered discrimination** — a key function whose congruence is partly the CAS's
  normalisation rather than the circuit's own. Defence: assert the key's behaviour on the
  specific transformation the claim is about (here, commutative reordering) rather than assuming
  srepr is syntactic.
- **Splitting reported as impossibility** — over-discrimination costs transfer, not correctness.
  Defence: `proves_impossibility` as a field on the witness type.
