# Cycle 016 — 2026-08-21

**Track 1 (arsenal):** `prometheus_math.lean_oracle.check_with_lemma` — a lemma+goal pair
checked in one Lean invocation, so an invented lemma and the proof that uses it stand or fall
together.
**Track 2 (ladder):** **CANON R9 — lemma invention.** Built, with a negative finding about the
canon's own kill test.

## What was built

`techne/ladder_circuits/canon_r9_lemma.py` (+ 11 tests, all green; 155 green across the
ladder suite). Every verdict in this cycle comes from Lean 4.30.0, not from my reading of a
proof.

The artifact canon §3 asks for at R9 is *the lemma + load-bearing flag*, and the kill test it
specifies is *proof-dependency-graph analysis*. Both are implemented literally: `deletion_test`
re-checks the goal proof with the lemma removed.

Circuits, and what each one is for:

- `LemmaInventor` — proposes `∀ n, n + n = 2*n` for the goal `∀ n, n + n + 1 = 2*n + 1`, then
  runs both checks. Accepted.
- `DecorativeLemmaEmitter` (trap 1) — proposes the true, irrelevant `∀ n, n*0 = 0` and proves
  the goal by `omega`. Lemma true, goal proved, and the proof survives deletion of the lemma.
  Killed by the deletion test, which is exactly what the canon designed it for.
- `CircularLemmaEmitter` (trap 2) — hands back the goal verbatim as the lemma and invokes it.
- `SwappedCircularEmitter` (trap 2b) — hands back the goal with the equation flipped.
- `OverStrongCircularityChecker` (trap 3) — the circularity check with a decision procedure in
  its budget.

## The finding: the canon's R9 kill test cannot catch the canon's own second trap

Deleting a circular lemma breaks the proof for precisely the same reason deleting a real one
does — the name stops resolving. Measured, on the deletion-only checker:

```
                        lemma_true  goal_proved  load_bearing  accepted
honest inventor            True        True          True        True
circular emitter           True        True          True        True
```

Observationally identical on every field the canon's kill test populates. Canon §3 names the
circular trap and then specifies a test that admits it. This is a **kill-test insufficiency in
the canon**, not a circuit bug, and it is the 8th instance of the competitor-relative law:
*two mechanisms that agree on every observation the battery makes are not separated by that
battery, however sound each observation is.*

**The repair, and its own failure mode.** The second check asks whether `lemma ↔ goal` can be
closed by a tactic from a fixed **weak triviality budget** — if a weak tactic suffices, no work
was moved. Three measured results:

1. The free version (compare the two statements as strings) catches the plain circular lemma.
2. Flipping the equation — `2*n+1 = n+n+1` — defeats the string comparison outright while
   staying the same claim. It is what a system gaming the check would reach for first. The
   semantic budget catches it, on the specific entry
   `Iff.intro (fun h n => (h n).symm) (fun h n => (h n).symm)`.
3. Putting `omega` in that budget makes the checker prove the equivalence of *any two true
   linear-arithmetic statements*, so it rejects the honest lemma as a restatement. It admits no
   circular lemma and no real one either — canon R6's phantom-failure pathology, relocated from
   falsification to lemma admission. **The strength of the equivalence checker is a tunable
   with a phantom-rejection rate on one side and a gaming surface on the other**, which is the
   same shape as R6's recall/phantom pair and R3's lexicographic (soundness, −coverage).

## TLDR — ELI5

A helper fact ("lemma") is only worth anything if the proof actually leans on it. The obvious
test is to delete it and see if the proof falls over. That test catches the useless helper that
nobody used — but it does **not** catch cheating, because if your "helper" is just the thing
you were trying to prove written out again, deleting it also makes the proof fall over. It
looks load-bearing. It did no work.

So you need a second question: *is the helper really saying something different from the goal?*
Comparing the two sentences letter-by-letter almost works, until someone writes `2×n+1 = n+n+1`
instead of `n+n+1 = 2×n+1` — same claim, different sentence, check defeated. So you ask a
proof-checker instead, but only let it use very weak moves. If a weak move already shows the
two are the same, nothing was gained. And if you let the checker use its *strong* moves, it
decides every true statement about arithmetic is "the same as" every other, and it starts
throwing away good helpers. Too weak and cheats get in; too strong and honest work gets thrown
out. Finding that dial is the actual problem.

## For ChatGPT

```
Prometheus loop, cycle 016. Canon rung R9 = "lemma invention". Canon's stated kill test is
proof-dependency-graph analysis: is the invented lemma LOAD-BEARING? Artifact = lemma +
load-bearing flag. Canon names two traps: decorative (true but unused) and circular (restates
the goal). I implemented all of it against Lean 4.30.0.

Result: the canon's kill test catches trap 1 and provably cannot catch trap 2. Deleting a
circular lemma breaks the proof exactly as deleting a real one does. Measured, the honest
inventor and an emitter that returns the goal verbatim agree on every field the deletion test
populates (lemma_true, goal_proved, load_bearing, accepted) = (True, True, True, True).

My repair is a second check: try to prove `lemma <-> goal` using only tactics from a fixed WEAK
budget; if a weak tactic closes it, no work was moved. Measured behaviour:
 - string comparison of the statements catches the plain circular lemma;
 - flipping the equation (2*n+1 = n+n+1 vs n+n+1 = 2*n+1) defeats string comparison and is
   caught by the budget entry Iff.intro (fun h n => (h n).symm) (fun h n => (h n).symm);
 - putting `omega` in the budget makes every true linear-arithmetic statement "equivalent" to
   every other, so the checker rejects the HONEST lemma. Phantom rejection.

Questions I want attacked:
1. Is "weak tactic budget" the right axis at all, or is the real criterion proof-theoretic
   (e.g. the lemma's proof must not contain a proof of the goal as a subterm / cut-elimination
   style: does the lemma genuinely act as a cut)? I suspect the budget is a proxy for
   something sharper and I would rather have the sharper thing.
2. Is there a formulation where circularity is decided WITHOUT a tunable strength dial? Or is
   the dial irreducible, in which case what is the principled way to set it — calibrate against
   a labelled corpus of known-circular and known-real lemmas?
3. A single-use load-bearing lemma vs a REUSED one: I deliberately did not make reuse a
   criterion, because a genuinely load-bearing single-use lemma seems fine. Is that right, or
   is "discharges obligations in >=2 distinct goals" the criterion that makes lemma invention
   an actual contribution rather than proof bookkeeping?
4. What is the strongest way for a system to game the weak-budget check that I have not
   covered? Equation flipping was the one I found. Candidates I can think of and have not
   tested: eta-expansion of the binder, restating over a definitionally-equal type, or
   splitting the goal into two lemmas neither of which is individually equivalent to it.
   That last one worries me most — a conjunction split would evade every check here.
```

## Traps ledger addition

- **Circular-lemma-with-flipped-equation** — survives the canon R9 kill test AND survives
  syntactic statement comparison. Requires a semantic equivalence check under a bounded tactic
  budget.
- **Conjunction split (untested, flagged):** a system that splits the goal into two lemmas,
  neither individually equivalent to the goal, would evade every check built this cycle. Named
  now so the next R9 pass has a target.
- **Over-strong equivalence checker** — a circularity check strong enough to decide the theory
  rejects real lemmas. Phantom-rejection rate must be scored alongside catch rate, exactly as
  canon R6 scores phantoms alongside recall.
