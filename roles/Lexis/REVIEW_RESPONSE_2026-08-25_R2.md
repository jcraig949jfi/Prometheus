# Response to external review R2, 2026-08-25

**Seat:** Lexis · **Reviewer:** external, responding to `EXTERNAL_REVIEW_REQUEST_2026-08-25.md`

The review declined to certify claim 1 and gave a concrete counterexample. Four of its six
items were computable and I ran all four before writing this. **Two of my positions changed
on measurement, one of them against me.** Nothing below is adopted on argument alone.

New instruments: `instruments/congruence_audit.py`, `instruments/robust_ceiling.py`,
`instruments/bundle_test.py`. Raw rows in `notes/congruence_audit_result.json`,
`notes/robust_ceiling_result.json`, `notes/robust_ceiling_clean.json`,
`notes/bundle_test_result.json`.

---

## 1. The slicing theorem — objection ACCEPTED as stated, then discharged by measurement

**The reviewer is right that I had not proved what I needed.** I proved "reads are detected";
what the induction requires is that the projection is a **congruence**: for every operator,
records agreeing on `D` have poststates agreeing on `D`. The aliasing counterexample survives
perfect read detection, and the cleaner form is worse — two records with extensionally equal
`d` (`[]` and `[]`), one aliasing `scratch` to `d` and one not, agree on the projection and
diverge after `mutate_scratch`. Field-value equality does not capture alias topology. That is
a real gap in the argument I published and I am not going to argue it away.

**So I tested the property instead of assuming it**, at a bar deliberately stronger than the
reviewer's. Their condition is *no D-reachable mutable object reachable from outside D*. But
sharing **inside** `D` breaks the induction too: if `names` and `ordered` are the same list in
one record and equal-but-distinct lists in another, projections match and they diverge on the
next append. So the audit walks the full mutable object graph at **every reachable record of
every task** and tests three nested conditions:

- **A** cross-boundary sharing (the reviewer's literal shape)
- **B** any inter-field sharing
- **C** any sharing at all — the same mutable object at two distinct paths anywhere

Plus the hidden-state classes the review correctly said "no random / no clock / no uuid" does
not cover: `global`/`nonlocal`, module-level mutables, mutable default arguments, closure
cells, function attributes, and the escape hatches (`getattr`, `vars`, `__dict__`, `asdict`,
`astuple`, `attrgetter`, `deepcopy`, serialization, `eval`/`exec`), plus calls that pass the
**whole record** to a helper.

**Result over all 120 tasks:**

```
records inspected: 5,029+ across the full battery
A cross-boundary sharing (D <-> non-D)  : 0
B inter-field sharing                   : 0
C any sharing at all                    : 0
globals / nonlocals                     : 0
mutable default arguments               : 0
closure cells                           : 0
function attributes                     : 0
escape hatches                          : 0
whole-record-passed-to-helper           : 0
module-level mutables reachable by ops  : 0
```

The object graph rooted at the fields is a **forest** at every reachable record. The
counterexample is valid Python and **does not obtain in this operator set**. The theorem now
rests on a measured premise rather than an assumed one.

**A detector bug I found and am reporting rather than quietly fixing.** The first run FAILED
the hidden-state check on three module-level dicts. They are `OP_REGISTRY`,
`OP_REGISTRY_V2`, `OP_REGISTRY_R2` — name→operator lookup tables. My detector flagged "mutable
container at module scope" without asking whether any operator can reach it. Resolved
properly rather than dismissed: the identifiers appear in **no** operator source, and a deep
before/after snapshot (repr, container identity, and every element identity) across 1,350
state expansions shows them **byte-identical**. They are read-only constants. The check now
separates LIVE from INERT and confirms inertness dynamically. **The FAIL was about my
instrument, not the substrate** — but a detector that cannot tell those apart is not a
detector, and it would have been easy to wave off.

**What I still cannot claim.** This is a *measurement over the current 27 operators*, not a
theorem about the substrate. Any newly admitted operator must be re-audited; aliasing is one
`bb.scratch = bb.d` away. `congruence_audit.py` is therefore now a **precondition of the
closure result**, not an optional extra, and the ceiling is only valid for an operator set
that passes it.

## 2. The joint-state equivalence — objection ACCEPTED, and it was the same audit

The reviewer is right that this is near-tautological *given* `T_o : S → S`, and that every
attack is on that phrase. Their `global calls; calls += 1; if calls == 7:` example is exactly
the shape a precomputed transition table cannot represent. Two dynamic tests, both adopted
from the review:

- **History independence.** For sampled reachable records, apply every operator (a) directly
  and (b) after 40 unrelated operator applications on *other* records; require byte-identical
  projected output. **189 (record, operator) pairs, 0 mismatches.**
- **Cross-task contamination** — the review's most important catch, because my joint
  construction assumes 120 independent evaluations of the same function. Build each task's
  reachable answer set with the battery in original order and in **reversed** order.
  **0 of 120 tasks changed.**

I accept the remaining limit: this samples, it does not prove. Fresh-process comparison is not
implemented and is the obvious next hardening.

## 3. The clean-pool restriction — objection ACCEPTED, and the fix went AGAINST me

**I accept the narrowed noun without reservation.** The sentence *"the substrate's exact
ceiling is 0.8333"* is retracted. I disproved it myself and should have written it the way the
reviewer phrases it:

> **Under Apollo's pre-existing admissibility rules — the operator alphabet its search draws
> from and the scorer combinations its fitness admits — the exact ceiling is 100/120.**

All three of the reviewer's legitimacy conditions hold and are checkable: the restriction
predates this experiment (`_MUT_SCORER_POOL`, `routing_purity`), it is mechanically enforced
rather than interpretive, and 0.833 is the quantity O1 set out to characterize.

**But I took the better suggestion — make the restriction stop mattering — and it did not go
my way.** I implemented permutation-robust correctness (correct under **all 24** orderings) as
the objective and ran the per-task joint search over the **unrestricted** 27-operator pool.
Pre-committed before the run: `≤ 100/120` means the pool boundary stops mattering; `> 100/120`
means the restriction is load-bearing and the unrestricted number is the honest headline.

```
permutation-robust per-task upper bound, UNRESTRICTED pool = 101/120 = 0.8417
permutation-robust per-task upper bound, CLEAN pool        = 100/120 = 0.8333
```

**The reading fires against me. The restriction is load-bearing, by exactly one task.**

That task is #33, `all_but_n`: *"There were 10 items. 5 were removed. How many remain?"*,
correct answer `5`. And the mechanism is a coincidence I verified rather than assumed —
across the five `all_but_n` instances, it is the **only** one whose answer is also a number
stated in the prompt:

```
task 30  15 - 1  = 14   answer stated in prompt? No
task 31  49 - 1  = 48   No
task 32   5 - 2  = 3    No
task 33  10 - 5  = 5    YES
task 34  13 - 11 = 2    No
```

So a content-matching heuristic that emits a candidate equal to some parsed number is right on
exactly one instance and wrong on four. It is permutation-equivariant, so my own robustness
test admits it — **which is the reviewer's §4 point landing on my own instrument within an hour
of my adopting it.** Passing permutation is not evidence of reasoning.

**Net position.** The narrowed claim stands. The attempt to make the narrowing unnecessary
*failed* by one task, and that one task is won without the capability its category tests. I am
reporting the failed attempt rather than the convenient half.

## 4. The permutation null — objection ACCEPTED, all 24 adopted

The criticism is correct and the arithmetic is trivial: 4! = 24, three sampled points is not
invariance, and reverse+rotate generate `D_4` which is not `S_4`. **All 24 permutations are now
the standard for any claim**; reverse+rotate remain only as a cheap canary. Both new
instruments use the full orbit.

I also accept the two-sided correction on what the test means, and it is now written into the
instruments' docstrings:

> Failure demonstrates unacceptable order sensitivity. Survival demonstrates permutation
> equivariance, **not** semantic reasoning.

Task 33 above is the worked example of the second half, produced by my own pipeline.
I accept the list of legitimate reasons a semantic solver could fail permutation testing
(order-dependent tie-breaking, prefix-only processing, self-referential options like "both A
and C"); none applies to this battery, but "failed permutation ⇒ positional guess" is retired
as a general inference.

## 5. `NEW = 1 ∧ ΔE = 0` — objection ACCEPTED, and the proposed bundle test RAN

The reviewer refused to let "readout bottleneck" stand as interpretation, named the three
nested explanations (A dead computation / B incompatible representation / C missing routing),
and proposed the discriminating measurement. I built the readout primitive it implies — a
**guarded** scorer matching `max_value` against candidates **by content** — and ran all four
arms over the clean pool.

```
arm                        ΔE      ΔS   ΔROBUST   closure
C + compute               +0      +0        +0    exhausted
C + readout               +0      +0        +0    exhausted
C + compute + readout     +5      +5        +5    exhausted
```

This is the reviewer's "embarrassingly clean" shape, obtained. Every closure **exhausted**, so
the zeros and the +5 are exact rather than capped. The +5 is exactly the five `all_but_n`
tasks — including the four that require real arithmetic — and it survives **all 24
permutations**, so it is not the task-33 coincidence and not positional fallback.

**Explanation A is ruled out by construction:** a wrong value cannot be rescued by adding a
reader. The deficit was routing. *"Readout bottleneck"* is now a measurement.

**And this is the first ΔE > 0 in the G5 ledger — it is a PAIR, not a primitive.** That is the
sharpest thing to come out of this exchange, and it was the reviewer's idea:

> **On this substrate the unit of vocabulary growth is not a primitive. It is a
> compute/readout interface pair. Any generator that proposes one operator at a time scores
> exactly zero here regardless of how good the operator is.**

Which retroactively explains my three failed singletons without special pleading: they were
not bad, they were **half of something**.

I also accept that writing into existing fields was a self-imposed constraint. The reviewer is
right that a brand-new field guarantees ΔE = 0 for a lone operator, so it would have tested
"new computation plus deliberately no consumer." The pair test is the escape from that
critique and it is why the result means something.

## 6. The strategic inference — objection ACCEPTED; my claim was too broad

The reviewer is right that **CEGIS does not belong in the same bucket as repeated-subgraph
compression**, and I over-generalized from three hand-written candidates to a class of methods.
CEGIS searches a hypothesis class against counterexamples; it does not mine recurring
structure. Given raw question text, candidates, failing examples, and string/regex/token
predicates, `"before"` is squarely inside its reach even though no Apollo program ever
expressed it.

I adopt the support theorem in place of my claim:

> **Any proposal mechanism whose output semantics remain in the compositional closure of
> Apollo's existing observables cannot repair a deficit requiring a distinction absent from
> those observables.**

— with the premise **tested per generator** rather than assumed: repeated-subgraph compression
almost certainly satisfies it; plain e-graph extraction probably does; CEGIS does not unless
its synthesis grammar is deliberately crippled; anti-unification depends on its constructors.

The empirical version is better than my version and is now the planned test: find input pairs
requiring different behaviour that are **observationally indistinguishable under the generator's
feature vocabulary**. That converts "compression seems mis-aimed" into an impossibility result
about a specified interface. `all_but_n` supplies a ready-made instance — tasks 30 and 34 are
indistinguishable to any generator whose observables lack integer subtraction.

**Consequence for STEP 3's design:** it is not cancelled, it is re-specified. Symbolic
generators are back in scope with the premise tested per generator, and every arm must propose
**bundles**, not primitives, or the measured answer is zero for reasons that have nothing to do
with the generator.

---

## 7. Where I still push back — one item, and it is small

The reviewer's framing that the 0.8917 witness "already falsified" the unrestricted statement
is right, and I said so first. But I would resist collapsing the two results into "O1 was
wrong." O1's enumerated space genuinely contains nothing above 0.833; its error was a **bound
it declared** (`max_k = 10`, tail grammar), not a mis-measurement. And the object it was
characterizing — Apollo's search language — does cap at exactly 100/120. The accurate summary
is that O1 measured the right thing, declared its bounds honestly, and then wrote a headline
one noun wider than its bounds supported. That is a different failure from an incorrect result
and the distinction matters for how much of O1 survives.

## 8. Corrected headline, adopting the reviewer's structure

> O1's unrestricted claim was false, and the 0.8917 witness is ours. **Apollo's historically
> admissible program language nevertheless has an exact ceiling of 100/120, at every depth,
> with every repetition, in every order, with every tail** — joint closure exhausted at
> 484,218 states, on a projection now measured to be a congruence. The apparently superior
> unrestricted witness is permutation-fragile fallback behaviour; under all-24-permutation
> robustness the unrestricted pool buys exactly **one** task, and that task is the single
> `all_but_n` instance whose answer is a literal in its own prompt. The first primitive
> additions extend internal computation without extending attainable answers — and the
> paired-operator test shows why: **a compute primitive and a readout primitive are each worth
> zero and are jointly worth +5, exact and permutation-robust.** The unit of vocabulary growth
> on this substrate is the interface pair.

## 9. What this review changed, in one list

- Claim 1 was **unproven as argued**; now measured (congruence audit, 5 checks, all pass).
- `congruence_audit.py` is a **precondition** of the ceiling result, re-run per operator set.
- "The substrate's ceiling" **retracted**; replaced with the admissibility-rules noun.
- Permutation standard raised from **2 → all 24**.
- "Failed permutation ⇒ guessing" **retired**; "passed permutation ⇒ reasoning" was never
  claimed and is now explicitly denied in the instruments.
- Readout-bottleneck **upgraded from interpretation to measurement** via the bundle test.
- **First ΔE > 0 in the G5 ledger, and it is a pair.**
- Strategic claim about symbolic generators **narrowed**; CEGIS removed from the bucket;
  STEP 3 re-specified around bundles.
- One detector bug in my own audit found, reported, and fixed.
