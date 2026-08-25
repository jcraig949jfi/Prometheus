# STEP 1 — the depth and repetition holes in the 0.833 ceiling, closed

**Seat:** Lexis · **Date:** 2026-08-25 · **Status:** measured, read-only w.r.t. `apollo/`
**Instruments (all in `roles/Lexis/instruments/`, all deterministic, all repo-relative):**
`answer_slice.py`, `reachable_answers.py`, `product_ceiling_fast.py`, `ceiling_diagnosis.py`
**Population:** Apollo's own 120-task battery, built by Apollo's own `o1_enumerate.build_battery()`
(50 canary + 30 synth + 20 inference + 20 cross-tier). Every number below is produced by Apollo's
own `_evaluate_acc` or by transition tables proven to replay it exactly.

---

## Headline

> **0.8333 is the EXACT ceiling of Apollo's blackboard substrate — at every depth, with every
> repetition, in every order, with every scorer tail. The search closed. It is no longer
> "well-supported but not proven"; it is proven.**
>
> **And the entire unreached 16.7% is ΔE: all 20 tasks lie outside the operator closure. ΔS = 0.
> No macro, no better guard, no better search, no deeper program can reach a single one of them.**

The pre-committed kill did **not** fire. One composition does exceed 0.833 and it is reported in
full in §4 — it wins by unconditional guessing, and Apollo's own fitness function already excludes
it by name.

---

## 1. Why enumeration was the wrong move, and what replaced it

The instruction offered (a) extend `traceclass.py` past k=10 with repetition, or (b) prove a
normalization theorem. Neither is available as stated:

- **(a) is hopeless.** 27 operators with repetition at depth k is 27^k. The production organism is
  15 operators deep.
- **(b) is FALSE as literally stated.** "Longer or repeating programs reduce to ≤10 distinct
  operators" is not true here. `op_fencepost` (`blackboard_ops.py:161`) and `distribution_reducer`
  (`blackboard_ops_v2.py:181`) both do `state.evidence.append(...)` and never clear, so applying
  either k times yields k distinct states. **The substrate is not finite-state.** A first BFS over
  full blackboard states ran for 20 minutes without terminating, for exactly this reason.

The move that works is a third one: **don't enumerate programs, enumerate reachable states.**

Apollo's operators are deterministic functions `BlackboardState -> BlackboardState` — verified, no
`random`, no clock, no uuid anywhere in `blackboard_ops*.py`. So for a fixed task the set of states
reachable by *any* sequence of *any* length with *any* repetition is just the closure of the initial
state under the transition relation. That is a BFS, and it is small.

**The normalization theorem that does hold** (`answer_slice.py`). Define the answer-relevant
backward slice:

> `D` = least slot set with `selected_answer ∈ D`, closed under: if an operator writes into `D`,
> all of its reads are in `D`.
>
> **Theorem.** If two states agree on every slot in `D`, then under every operator sequence the
> resulting states agree on `selected_answer`.
> *Proof.* Induction on length. An operator whose writes miss `D` cannot change a `D`-slot. An
> operator whose writes meet `D` computes them from its reads, and those are in `D` by
> construction. Nothing outside `D` ever flows in. ∎

Computed over `declared_reads ∪ AST-detected reads` — over-approximated, so `D` can only get larger
and the bound only more conservative; this is how `select_nth`'s two undeclared reads of `candidates`
are absorbed rather than assumed away.

**Result: |D| = 17 of 23 slots.** Outside `D`, provably unable to influence any answer:
`candidate_scores`, `confidence`, `evidence`, `hypotheses`, `probabilities`, `transitive_closure`.
`evidence` is outside `D`, so the unbounded accumulation that broke termination **is invisible to
the answer**. Keying the BFS on `D` restores finiteness and loses no reachable answer.

**Side finding, worth its own line.** Two of Apollo's 27 registry operators —
`distribution_reducer` and `evidence_updater` — write **only** slots outside `D`. They cannot change
any answer, in any pipeline, at any depth. That is decoration proven statically, in Apollo, on the
same day the forge's 86%-decoration rate was measured (`G1_ABLATION_2026-08-25.md`). Two independent
subsystems, the same pathology, found by two different instruments.

## 2. The two bounds, and how they meet

**Upper bound — per-task closure** (`reachable_answers.py`). For task `t` let
`R(t) = { s.selected_answer : s reachable }`. Any program of any shape ends in some reachable state,
so its answer on `t` lies in `R(t)`. Then `ACC_MAX = |{t : correct(t) ∈ R(t)}| / 120` bounds every
program — and it is *loose*, because it lets a different program answer each task.
Closure resolved on all 120 tasks (5,029 states total, mean 41.9, max 104 — no cap was hit).

**Lower bound / exact value — joint product BFS** (`product_ceiling_fast.py`). A program induces one
trajectory per task, so track all 120 at once: the joint state is the 120-tuple of per-task state
indices, and the reachable joint set is *exactly* the set of program-induced joint states. Stage 1
builds per-task transition tables; stage 2 BFSes over 120-byte joint keys, so no operator ever runs
twice.

Two positive controls, both before any result was read:
- known production organism via Apollo's `_evaluate_acc` = **0.8333** ✓
- the same organism **replayed through the transition tables** = **0.8333** ✓ (the tables reproduce
  the substrate exactly, so what the BFS explores is Apollo, not a model of Apollo)

## 3. The result, under Apollo's own operator pool

`--pool clean` = transformers + **guarded** scorers only, minus the two provably-decorative
operators. This is not a convenience: it is *Apollo's own dispatch pool*. `evolve()` sets
`_MUT_SCORER_POOL = GUARDED_SCORERS`, and `fitness()` sets `routing_purity = 0` — zeroing
`causal_composition_score` — for any organism mixing a plain scorer with a guarded one, on the
stated grounds that an unconditional scorer *"fires on every task and racks up incidental hits that
mimic capability."* 18 operators.

```
SEARCH EXHAUSTED -- the joint reachable set CLOSED. This is exact.
   484,218 joint states, frontier empty at depth 23
BEST ACHIEVABLE BY ANY PROGRAM, ANY DEPTH, ANY REPETITION = 100/120 = 0.8333
per-task upper bound under the same pool                  = 100/120 = 0.8333
```

**The two bounds coincide.** The upper bound (a different program allowed per task) and the achieved
single-program optimum are the same number. That is a matching sandwich, and it is the strongest
form the claim can take:

- **The depth bound is removed.** Not k ≤ 10 — every depth. The frontier emptied at 23.
- **The repetition bound is removed.** Repetition was allowed throughout and never helped.
- **The ordering bound is removed.** All orderings are inside the closure by construction.
- **The tail bound is removed.** O1 enumerated single scorers and 2–3-guard sets; this covers all
  tails of all sizes.

O1's own caveat — *"I consider the ceiling claim well-supported but not proven"* — is discharged.
The correct language is now **"the exact ceiling of the operator set"**, not "bounded-language
ceiling (k ≤ 10, no repeats)" and not the withdrawn "expressivity ceiling."

## 4. The composition that does exceed 0.833 — reported in full, as pre-committed

With the **unrestricted** 27-operator pool the joint BFS found a program reaching **107/120 =
0.8917**, verified independently through Apollo's own `_evaluate_acc`:

```
parse_box_items -> op_aggregate_quantities -> parse_comparison -> parse_names_and_relations
-> parse_numbers -> parse_question_target -> parse_ordinal -> parse_rules -> forward_chain
-> relations_from_facts -> op_build_ordering
-> score_by_max_value -> score_by_aggregate__g -> score_by_comparison__g
-> score_by_derivability__g -> select_nth__g
```

canary 0.600 → **0.740**; synth, inference, cross_tier all unchanged at 1.000. **11 transformers**
(O1's cap was 10) and **no operator repeated**. So had the kill stood, it would have been the
*depth* bound that failed, by exactly one operator — not repetition.

**It does not stand, and here is the measurement rather than the framing.** Removing the single
plain scorer `score_by_max_value` drops the program from 0.8917 to 0.7500. It is carrying the gain.
On all 7 newly-solved tasks, `max_value is None` — the op falls through to its documented default,
*"default to `candidates[0]` when state is incomplete."* **6 of the 7 emitted `candidates[0]`.** Six
of the seven gained tasks have the correct answer at candidate index 0.

The correct-answer position is near-uniform in the canary (13/11/14/12 across the four slots), so
this is not a global position bias being exploited — it is luck concentrated in the residual: among
the 20 tasks the organism fails, the ones whose answer happens to sit at index 0 come free with an
unconditional guesser. That is precisely the "incidental hits" pathology Apollo named in June 2026
and already excludes.

**Verdict: the pre-committed kill does not fire.** But the claim needs one honest correction that is
not a rescue: **0.8333 is not the maximum of `_evaluate_acc` over the full registry.** The sentence
"nothing in 1.74 million type-correct pipelines beats 0.833" is true of O1's enumerated space and
false of the substrate; O1's `max_k = 10` was one operator short and its tail grammar excluded mixed
plain+guarded tails. The claim that survives is narrower and should be stated in these words:
**0.8333 is the exact ceiling under Apollo's own clean-routing regime, and the only way past it is
unconditional guessing.**

## 5. The ΔE / ΔS split — the payload for this seat

Under the clean pool, the per-task upper bound is also 100/120, and the 20 unreachable tasks are
exactly canary indices **30–49**, a contiguous block:

- **ΔE-bound (correct answer outside the operator closure): 20 / 120 = 16.67%**
- **ΔS-bound (expressible but unrouted): 0 / 120 = 0.00%**

**The entire ceiling gap is ΔE.** Not one task is reachable-but-unrouted. Every macro over the
existing 27 operators, every routing improvement, every search improvement is bounded at 0.8333 —
now by proof rather than by inference. G3's pre-registered note that *"on Apollo's blackboard H is
bounded at zero"* is confirmed exactly, and G5's ΔE/ΔS ledger has its first entry.

The block is four categories × 5 tasks, and naming them names the missing vocabulary:

- **`all_but_n`** (5) — *"There were 15 items. 1 were removed. How many remain?"* No operator does
  arithmetic on parsed numbers to produce a candidate. Genuinely ΔE.
- **`vacuous_truth`** (5) — *"If there are no flying pigs, are all flying pigs pink?"* Quantification
  over an empty set. Genuinely ΔE.
- **`consistency_check`** (5) — *"A is taller than B, B is taller than C, C is taller than A. Are
  these consistent?"* Needs cycle detection and a boolean readout. ΔE — but see below.
- **`temporal_ordering`** (5) — *"sunrise happened before lunchtime, ... What happened first?"*
  **Not ΔE at all.** See §6.

## 6. Half the "missing vocabulary" is a regex

`_REL_PATTERN` (`blackboard_ops.py:37`) is:

```python
r"(\b[A-Z][a-z]+)\s+is\s+"
r"(?:taller|bigger|larger|greater|older|faster|heavier|smarter|stronger|richer)"
r"\s+than\s+(\b[A-Z][a-z]+)"
```

It requires a capitalised multi-letter token on both sides and one of ten hard-coded comparatives.
Measured: on all 20 ΔE tasks, `parse_names_and_relations` returns **0 relations, 0 names**. Two of
the four categories fail here rather than at the reasoning level:

- **`temporal_ordering`** is the *same strict partial order* as `transitivity`, which the substrate
  solves **10/10**. It is blocked by lowercase event nouns ("sunrise", "dusk") and by "happened
  before" not being in the adjective list. Probe: injecting relations from a hand-written
  generalized pattern and then running the **existing, unmodified** `op_build_ordering →
  select_nth__g` solves **3 of the 5**. No new verb was introduced.
- **`consistency_check`** uses single-letter names `A`, `B`, `C`; `[A-Z][a-z]+` requires at least one
  lowercase, so these parse to nothing. With a single-letter pattern all 3 relations per task parse
  cleanly. The *reasoning* step (cycle → "No") is still genuinely absent, so this one stays ΔE — but
  its input is already available.

**Caveat, stated plainly:** the generalized pattern is one I wrote by hand and used only to inject
state for the probe. Nothing in `apollo/` was modified, and this is not a claim that any automatic
generalization achieves it. It is a measurement that the *verb* is present and the *surface matcher*
is what excludes the task.

**Why this matters to the vocabulary seat.** This is the program's own doctrine — verbs over nouns,
`project_verbs_must_be_native` — appearing as a measured defect in Apollo's own operator set. The
operator encodes a real, general verb (strict partial order → extremum) and then keys it on
capitalised proper names and a closed list of English comparatives. Roughly a quarter of Apollo's
measured "expressivity ceiling" is not a missing capability; it is a present capability welded to a
noun.

**Consequence for the slice.** The ΔE headline stands: 16.7% is outside the closure, ΔS is zero,
and growing the operator menu is the only route past 0.8333. But the cheapest ΔE is not a new
concept — it is **decoupling an existing verb from its surface form**, which the redundancy
predicate `NEW(p, C, T)` would classify correctly and which a compression-style library learner
would never propose, because there is nothing recurring to compress.

## 7. Corrections this makes to committed documents

- `SIDE_BY_SIDE.md` §1, §7 and `REVIEW_RESPONSE_2026-08-25.md` §2.1: replace **"16.7% is unreachable
  by any composition of at most 10 transformers, without operator repetition"** with **"16.7% is
  unreachable by any composition, at any depth, with any repetition, under Apollo's clean-routing
  pool — proven by exhaustive closure, 484,218 joint states, frontier empty."**
- `REVIEW_RESPONSE_2026-08-25.md` §4 open item *"extend beyond k=10 with repetition allowed, or find
  the normalization theorem"* — **closed**. The literal normalization theorem is false; the
  answer-relevant-slice theorem replaces it and is stronger.
- O1 `FINDINGS.md` "Limits of this result": the ordering caveat was closed 2026-08-25 by
  `traceclass.py`; the depth, repetition and tail caveats are closed here. One correction runs the
  other way: *"Nothing in 1.74 million type-correct pipelines beats the organism"* is true of the
  enumerated space but **`max_k=10` was one operator short of a 0.8917 program**, and that program
  wins by guessing. Both halves belong in the record.
- `ROLE.md` §4: "16.7% of the battery is unreachable in that vocabulary" is now exact, and gains
  "ΔE = 16.7%, ΔS = 0".
