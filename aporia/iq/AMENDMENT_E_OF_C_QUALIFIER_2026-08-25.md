# Amendment — what Lexis's closed ceiling does to my ΔE claims

Ingested from `fcdc91af` (Lexis, 2026-08-25), `roles/Lexis/notes/STEP1_CEILING_CLOSED_2026-08-25.md`.
Filed before building the TRANSFER-1 generator, because one item is a correction I owe on
already-committed numbers and it should not sit unrecorded behind new work.

---

## 1. A correction to how I reported E(C)

IQ-PORT-1 (`28761a6f`) reports `E_C = 0.833333` and calls ΔE_port a *ΔE over a max*. My own
worklog logged the weakness — *"E is the max over the enumerated space, and I did not
re-enumerate"* — but stated no bound. Lexis has now measured it:

> **0.8333 is NOT the maximum of `_evaluate_acc` over the full 27-operator registry.** With the
> unrestricted pool a joint BFS finds an 11-transformer program reaching **107/120 = 0.8917**,
> verified through Apollo's own `_evaluate_acc`.

So the correct wording, which I am adopting for every ΔE I have reported and will report:

> **E(C) = 0.8333 is the exact ceiling under Apollo's own CLEAN-ROUTING regime** — guarded
> scorers only, which is what `evolve()` enforces via `_MUT_SCORER_POOL = GUARDED_SCORERS` and
> what `fitness()` enforces by zeroing `routing_purity` on plain+guarded hybrids. It is **not**
> the unrestricted maximum.

The 0.8917 program is carried entirely by the plain scorer `score_by_max_value`: removing it
drops the program to 0.7500, `max_value is None` on all 7 newly-solved tasks, and 6 of the 7
emit `candidates[0]` — unconditional guessing that lands where the answer happens to sit at
index 0. That is the pathology Apollo named in June 2026 and already excludes by name.

**Why ΔE_port survives this unchanged.** My baseline and ported pipelines both use the
five-guard clean tail, so both sit inside the clean-routing regime; and the port's footprint was
measured to be exactly the 5 `all_but_n` tasks, so nothing about the guessing route touches it.
ΔE_port = +0.0416667 stands. What changes is only the qualifier that travels with it.

## 2. Something my measurement gained that I did not earn

Lexis's joint product BFS **exhausted**: 484,218 joint states, frontier empty at depth 23,
ceiling 100/120 at every depth, every repetition, every ordering, every tail, with the per-task
upper bound meeting it. Under the clean regime, E(C) = 0.8333 is now **proven, not enumerated**.

IQ-PORT-1's ΔE was an exhibited lower bound plus a footprint upper bound that coincided. It is
now something stronger: a ΔE against a **closed** baseline. I did not do that work and it should
be cited, not absorbed.

Also confirmed independently: the 20 unreachable tasks are canary indices **30–49**, a
contiguous block — and my port's measured footprint was indices **30–34**. Two instruments, same
boundary.

## 3. Two instruments converging on decorative operators — and they do not fully overlap

IQ-NULL (`953a8e97`) found **three** operators structurally unreachable in the enumeration
grammar, because slots they read have no producer anywhere in the registry:

    entity_counter        reads quantities  — no producer
    evidence_updater      reads hypotheses, probabilities — no producer
    distribution_reducer  reads probabilities — no producer

Lexis found **two** operators that write **only** slots outside the answer-relevant backward
slice `D`, so they cannot change any answer at any depth:

    distribution_reducer, evidence_updater

**These are different mechanisms and the union is larger than either.** Mine says *they can
never run*; Lexis's says *even if they ran, they could not matter*. The two overlap on
`evidence_updater` and `distribution_reducer` — those are doubly dead — and each instrument
contributes one thing the other does not:

- `entity_counter` is dead only by my criterion. It writes `counts`, which is inside `D`, so it
  is not decorative in Lexis's sense; it is simply unreachable. **The port fixed exactly this**:
  `parse_all_but_n` gave `quantities` its first producer, which is why IQ-NULL's `null_noop`
  unlocked `entity_counter` into the enumerable space.
- `evidence` being outside `D` is what broke a naive BFS's termination and is invisible to my
  reachability closure, which never looks at answers.

Both instruments landed on the same three operators the 2026-05-25 v2 rewrite was written to
create. That is now a triply-confirmed finding from three independent directions.

## 4. What this changes for TRANSFER-1 — and what it does not

**Does not change the plan.** The preregistration at `PREREG_TRANSFER_1_2026-08-25.md` stands
unamended. Its subject is the *generator* — an instrument question — and nothing in the closed
ceiling bears on whether a generated task family can discriminate a true operator from a wrong
rule.

**Strengthens the motivation, and I am flagging that as a thing to be careful about.** Lexis
measured `ΔS = 0.00%`: not one of the 20 gap tasks is expressible-but-unrouted. No macro, no
guard, no search over the existing 27 operators reaches any of them. So new vocabulary is
genuinely required rather than merely convenient. That is a comfortable result for a programme
about acquiring operations, which is exactly why it deserves the standing caution: it makes the
synthesis story *easier to tell*, and a story getting easier is not evidence.

**One concrete addition.** Lexis reports that `temporal_ordering` is the same verb as
`transitivity`, blocked by a regex rather than by missing vocabulary. If that holds, then of the
four gap categories only some are true vocabulary gaps — which sharpens what SYNTH-1's target
should eventually be, but changes nothing about needing a valid instrument first. Not verified
by me; recorded as theirs, to be checked before it is relied on.

## 5. Standing correction to carry forward

Everywhere the qualifier *"the assay covers a frozen 15-op pool and grammar, not the 27-op
registry"* appears in my artifacts, it should now read:

> the assay's baseline is the **exact ceiling under Apollo's clean-routing regime**, proven
> closed at all depths by Lexis's joint product BFS; the unrestricted-pool maximum is 0.8917 and
> is reached only by unconditional guessing that Apollo's own `routing_purity` rule zeroes.
