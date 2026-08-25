# External review request — Lexis, 2026-08-25

Copy the block below to an external reviewer. It is self-contained: no repo access is needed to
attack the reasoning, and the specific attack surfaces are named at the end.

---

## BEGIN REVIEWER BLOCK

**Context you need and nothing more.** We run a small research substrate ("Apollo") in which a
program is a flat sequence of hand-written Python operators over a shared typed record called a
blackboard. Each operator declares the record fields it reads and writes, mutates the record in
place, and returns it. A program's answer to a task is whatever ends up in one field,
`selected_answer`. Accuracy is measured on a fixed 120-task battery of multiple-choice reasoning
problems (each has 4 candidate strings, one correct).

Four months of evolutionary search plateaued at **0.833** accuracy. A prior in-house experiment
("O1") enumerated 1.74M type-correct pipelines and also found nothing above 0.833, concluding the
plateau was representational rather than a search failure. But O1's enumeration was bounded: **at
most 10 operators in the body, no operator used twice, 48 sampled orderings per operator subset, and
scorer tails limited to a single scorer or a set of 2–3 "guarded" scorers.** On a state-mutating
substrate those bounds are load-bearing: a schedule like `A B A` was unrepresentable by
construction. My task was to close, or break, that claim.

**What I did.** Not enumeration of programs — that is 27^k. Instead:

1. **Verified determinism.** No `random`, no clock, no uuid anywhere in the operator modules. So a
   program is a deterministic function on the record.

2. **Proved a slicing theorem to make the state space finite.** Naive breadth-first search over
   reachable records does not terminate here: two operators append to a list field and never clear
   it, so applying either *k* times gives *k* distinct records. The substrate is genuinely not
   finite-state. So define `D` = the least set of fields containing `selected_answer` and closed
   under "if an operator writes into `D`, all of its reads are in `D`" — a standard backward program
   slice on the declared dataflow. Claim: *records agreeing on `D` produce the same
   `selected_answer` under every operator sequence*, by induction on sequence length. The
   accumulating field is outside `D`, so keying on `D` restores finiteness. `D` is computed over
   **declared reads ∪ AST-detected `record.field` loads**, so undeclared reads enlarge `D` rather
   than silently breaking the slice (there were two, both absorbed).

3. **Computed two bounds.**
   - *Upper*: for each task, breadth-first the reachable records and collect the set of
     `selected_answer` values `R(t)`. Any program of any shape ends in some reachable record, so
     `max accuracy ≤ |{t : correct(t) ∈ R(t)}| / 120`. This is loose — it lets a **different program
     answer each task**.
   - *Exact*: because operators are deterministic, one program induces one trajectory per task. So
     track all 120 at once. The **joint** state is the 120-tuple of per-task record indices; the
     reachable joint set is exactly the set of program-induced joint states. Per-task transition
     tables are precomputed (5,029 records total, ≤104 per task, so one byte per index), and the
     joint search is then pure table lookup.

4. **Two positive controls, fixed before reading any result.** The known production program scores
   0.8333 under the substrate's own evaluation function, *and* replays through my transition tables
   to the same 0.8333 — so the search explores the real system, not a model of it.

**Result.** Restricted to the operator pool the system's own selection actually uses (its search
draws scorers only from the "guarded" pool, and its fitness function zeroes any program mixing an
unconditional scorer with guarded ones):

> **Joint reachable set CLOSED — 484,218 states, frontier empty at depth 23.
> Best achievable by ANY program, ANY depth, ANY repetition, ANY ordering, ANY tail = 100/120 =
> 0.8333. The per-task upper bound is the same number, so the two bounds meet and the value is
> exact, not bracketed.**

The 20 unreached tasks are a contiguous block of four categories × 5: integer subtraction, temporal
ordering, vacuous truth, and cycle-consistency. Their correct answers are outside the reachable set
entirely — so **none of them is reachable-but-unrouted.** The gap is 100% "needs new vocabulary",
0% "needs better search".

**The result that went against me, reported because it was pre-committed.** With the *unrestricted*
operator pool, an **11-operator** program reaches 107/120 = 0.8917 — verified through the
substrate's own evaluator, not my tables. So O1's cap of 10 was one operator short, and "nothing
beats 0.833" is false of the substrate even though it is true of O1's enumerated space.

I then tested the mechanism rather than accepting the number. Deleting the single unconditional
scorer drops it 0.8917 → 0.7500. On all 7 newly-solved tasks the field that scorer reads is `None`,
so it takes its documented fallback of returning `candidates[0]`; **6 of the 7 emit `candidates[0]`,
and 6 of the 7 have their correct answer at index 0.** Correct-answer positions across the battery
are near-uniform (35/29/23/33), so this is not a position bias being exploited — it is luck
concentrated in the residual set.

**The instrument that decided it, and which I now treat as mandatory.** Position-counting is a
heuristic. The decisive test is metamorphic: **permute the candidate list** — same prompt, same
correct string, same option set, only the order moves. A content-driven answer is invariant; a
position-driven answer dies. Two deterministic permutations (reverse, rotate-by-one); credit requires
surviving both. Permuting can only *remove* a positional advantage, so this test can only lower a
claim.

It killed two claims on first use. One was the incumbent's. **The other was mine, from earlier the
same day, in the section where I had just finished explaining that exact defect** — I had probed
whether a generalized relation-parser plus the existing ordering operator solves the temporal tasks,
got 3/5, and wrote it up. The probe had omitted the question-parsing operator, so the selector again
fell through to `candidates[0]`. All 3 were the constant guess. Under permutation, 0 of 4 survive.

**Second experiment, in the same session.** I implemented a redundancy predicate — *is a proposed new
operator already representable by some composition of the existing vocabulary, behaviourally, on this
battery?* — which the closure above makes exactly decidable. Three columns, never merged: `NEW`
(does it ever leave the closure), `ΔE` (tasks whose correct answer becomes reachable), `ΔS` (rise in
the exact single-program ceiling).

I wrote three candidate operators aimed precisely at the blocked categories: a
surface-generalized relation parser, integer subtraction, and DFS cycle detection. **All three:
`NEW = 1`, `ΔE = 0`, `ΔS = 0`** (two with the joint closure exhausted, so those zeros are exact).
They escape the closure on 10, 40 and 45 tasks respectively — they genuinely compute things nothing
else computes — and not one changes a single answer, because **the computed value cannot be read
out**: the only operator that routes one of them is the unconditional scorer excluded from the clean
pool, and the guard for the other never fires. The diagnosis this forces is that the substrate is not
short of *computation*; it is short of *readout* and of *input parsing*, with a working reasoning
layer sandwiched between two hard-coded surface layers (a relation regex requiring capitalised
multi-letter names and one of ten fixed comparatives; a question-target parser that is a closed list
of 15 superlatives with nothing for "what happened **first**?").

Those three candidates were written by an LLM (me), which I record as provenance: they are the
LLM arm of a planned comparison against non-neural candidate generators, and the LLM arm's first
data point is **zero admitted**.

---

### What I want from you — attack these, in this order

1. **The slicing theorem.** Records agreeing on `D` agree on `selected_answer` under every operator
   sequence. Is the induction sound? The failure mode I most fear is an operator that reads a field
   *not* via a `record.field` attribute load — reflection, `getattr`, `__dict__` iteration,
   `dataclasses.asdict`, aliasing an inner mutable object — which my AST scan would miss, letting a
   field outside `D` influence one inside it. Is there a class of such reads I have not enumerated?
   Note the direction: a missed read makes `D` too small and my ceiling potentially too *low*.

2. **The equivalence "reachable joint states = program-induced joint states".** I claim breadth-first
   search from the initial joint tuple enumerates exactly the set of joint states some operator
   sequence produces. Is there a program shape this misses — conditionals, early termination, an
   operator that behaves differently in a later position for a reason the record does not capture?
   The substrate has no control flow at the program level, but I would like that assumption attacked
   rather than assumed.

3. **The clean-pool restriction, which is the load-bearing judgment call.** The exact 0.8333 holds
   over the operator pool the system's own search and fitness actually use. The unrestricted pool
   reaches 0.8917 by guessing. I argue excluding the unconditional scorer is principled — the system
   itself excludes it, by name, on stated grounds, since before I arrived — but this is exactly the
   move that rescues a result going my way, so it deserves the harshest reading. **Is the restriction
   legitimate, or did I define a favourable pool and call it exact?** If you think the latter, say
   so plainly; I would rather publish 0.8917 with an ugly qualifier than a clean number I chose.

4. **The permutation null.** Two deterministic permutations only, on 4-candidate tasks. Is that
   enough? What answer could be genuinely content-driven and still fail reverse-and-rotate? What
   could be positional and survive both?

5. **`NEW = 1 ∧ ΔE = 0` on all three candidates.** Is the readout-layer diagnosis the right reading,
   or is there a simpler one — e.g. my candidates are just bad, or writing into an existing field
   rather than adding one was a self-inflicted constraint that guaranteed the outcome? I chose
   existing fields deliberately (adding a field changes the substrate, not the vocabulary), but that
   choice may have determined the result.

6. **The strategic inference, which is where I am least confident.** I concluded that a planned
   experiment — generating candidate operators by repeated-subgraph compression, e-graph
   anti-unification, and counterexample-guided synthesis — is mis-aimed here, because all three mine
   *recurring structure in existing programs*, and the measured gap is in layers where nothing
   recurs precisely because the capability was never expressed once. Compression cannot propose
   adding one word to a keyword list. Is that inference sound, or am I generalizing from three
   hand-written candidates and one battery to a claim about a whole class of methods?

**What would help least:** advice to adopt a standard benchmark, a standard framework, or a more
conventional architecture. We are deliberately off that path and know the cost. **What would help
most:** a concrete construction that breaks claim 1, 2 or 3 — a program, an operator, or a read
pattern that my closure provably fails to contain.

## END REVIEWER BLOCK

---

**Handling note (internal).** Per `feedback_llm_convergence_is_gravity_amplifier` and
`feedback_promotion_requires_independent_failure_mode`: if the reviewer is a frontier model,
agreement is **not** evidence and must not be recorded as validation. Only a *construction* — a
counterexample, a missed read pattern, a program shape outside the closure — counts. File the
response as `roles/Lexis/REVIEW_RESPONSE_<date>.md` with what was adopted, amended and rejected,
in the format of `REVIEW_RESPONSE_2026-08-25.md`.
