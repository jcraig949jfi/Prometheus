# Icarus — Frontier Verdict Synthesis + Next Sprint
### 2026-05-29. Response to the frontier review of the R5-frontier packet.

This captures the frontier reviewer's verdict as navigable residue, records the
corrections we accept, and lays out the decision the verdict forces.

## The verdict, accepted

**R0–R3 is real enough to keep investing, but is NOT yet "synthetic reasoning"
in the strong sense.** The honest, narrowed claim:

> Icarus learned to stabilize **algebraic** symbolic-reasoning routines under
> deterministic held-out probes once failure signals became navigable.

The reviewer's strongest skeptical reading, which we accept: a major part of the
R0–R3 climb was **schema/affordance repair over a narrow symbolic API**, not
concept invention. R2 unblocked when we surfaced the probe schema + exception;
R3 unblocked when we stopped leaking a misleading ground_truth. Good
falsification hygiene — and also evidence the loop is *extremely sensitive to
which affordances are shown*. That is a real result (stabilizing algebraic
routines under a non-gameable held-out grader) but it is not evidence the loop
can discover a new representation class.

## The correction we most needed (a self-falsification)

We had been drifting toward "the substrate is the bottleneck" (the v3 thesis).
**The reviewer is right that we have not earned that claim.** Our only evidence
is `diff_apply_failed` at R5 — which proves **patch-generation brittleness under
too-large architectural jumps**, NOT "Python+sympy cannot express combinatorial
invariants." Reaching for a v3 typed-operator-graph now would be using
"representation change" as an **escape hatch before falsifying simpler
bottlenecks** (patch size, search locality, missing primitives, missing R4
bridge). We must run the discriminating experiment before any v3 commitment.

## The decisive experiment: the substrate/search matrix

A 2-axis grid that disambiguates mechanics vs search vs representation vs concept.

Rows (what the reasoner is given):
1. **No library** — current state.
2. **Seeded primitives** — `strategy.py` exposes combinatorial primitives
   (e.g. `color_counts`, `area`, `tile_delta_signature`) but does NOT wire them
   into `reason()`. The Generator must discover + compose them.
3. **Reference behind API** — `strategy.py` exposes the near-complete move; the
   Generator only has to call it.

Columns (the edit interface):
1. **Current unified diff.**
2. **Smaller staged diffs only.**
3. **Typed operator edit** (JSON plan compiled to Python).

Outcome reading:
- seeded primitives work, no-library doesn't → **search/locality** bottleneck.
- staged diffs work, single diff doesn't → **patch-size** bottleneck.
- typed edits work, diffs don't → **edit-interface/representation** bottleneck.
- only the hand-written reference passes → Generator lacks the **concept**.
- no hand-written reference passes → **verifier/spec bug**.

**The single most useful experiment** (reviewer's words): seed only three
primitives — coloring, count_by_color, tile_delta_signature — and see whether
Icarus composes them into the R5 trace across held-out boards. If yes, R5 is
search/library-locality. If no, there is a real concept-routing wall.

> TENSION TO RESOLVE WITH JAMES: seeding primitives is in direct tension with
> the standing directive "we still want to build our own reasoner from
> substrate." The seeded-primitive row is a *diagnostic* (does the concept
> exist in the Generator at all?), not the production path. We need James's
> call on whether to run the seeded diagnostic, and if R5 turns out to be
> search-bound, whether seeded primitives are an acceptable permanent affordance
> or must themselves be earned.

## The reviewer's next sprint (ordered)

1. **R4 strategy-selection probes** (deterministic strategy + evidence artifact).
   The R3->R5 cliff is partly self-inflicted: no R4 bridge from algebraic
   discipline to combinatorial routing. R4 = problems whose surface invites the
   wrong solver (algebraic-looking/invariant-solved; combinatorial-looking/
   algebraic-solved; two valid methods, require the cheaper; strategy-switch
   transfer). Grade with a tuple {answer, strategy_family, invariant, witness}.
2. **R5 difficulty gradient** (footholds, not a cliff): area parity -> color
   parity -> mod-k coloring -> weighted invariant -> monovariant -> conservation.
   All deterministically gradeable if the generator emits
   (answer, invariant_spec, computed_values, contradiction/witness).
3. **Trace-required grading** so boolean tileability can't be coin-flipped.
   Require the evidence artifact {answer, method, tile_invariant, counts,
   contradiction} and check it mechanically. Balance the dataset 50/50 with
   untileable causes split (area / color / boundary / nontrivial exact-cover),
   AND include adversarial cases where color balance holds but tiling still
   fails (punish "color-balance iff tileable").
4. **Diff failure taxonomy + Mechanic lens** — split `diff_apply_failed` into
   {stage, format_valid, applies_with_recount, files_touched, hunks, loc_+/-,
   max_hunk_span, ast_valid, imports_valid, tests_collected, exception_type}.
   Plus three probes: patch-minimization replay, intent extraction, oracle
   decomposition (empty typed functions to fill).
5. **Run the substrate/search matrix.**
6. **Promote strategy.py into a DreamCoder-style primitive library** with
   MDL/reuse pressure (primitives promoted when reuse compresses many solved
   probes).
7. **Add at least one non-LLM lens**: exact-cover solver, z3 relation checker,
   ILP invariant miner, or Lean-lite proof checker.
8. **Declare R5 success only if it transfers** to a non-board invariant family
   (Diophantine modular obstruction or graph parity). Otherwise it's a board-
   tiling trick, not invariant reasoning.

## Bridge generators (highest-leverage, reviewer-flagged)

"Algebraic shell, invariant core" probes connect the substrate Icarus already
has to the combinatorial reasoning R5 needs — and they're gradeable now:
- linear Diophantine solvability (gcd(a,b) | c)
- quadratic-residue impossibility (no square is 2 or 3 mod 4)
- coin problems with modular obstruction (6a+10b=17?)
- graph handshaking (odd degree sum impossible)
- permutation parity (sliding-puzzle reachability)

## Verifier-bottleneck boundary (accepted)

- R0–R6: deterministic custom graders (have).
- R7-lite: templated proof-step verifier (typed steps + injected first-bad-step
  from a catalog: divide-by-zero, square-without-domain, bad induction, missing
  base case, quantifier flip, cancellation-across-addition, ...).
- R7-hard / R8+: Lean/Coq/Isabelle or a proof DSL (LeanDojo for programmatic
  Lean + retrieval).
- R10–R12: no single verifier; proof obligations + falsification batteries +
  compression/MDL + human-audited novelty.

## Research map (steal these)

- **FunSearch** — closest precedent to our outer loop (LLM proposes code,
  deterministic evaluator scores, evolve). Lesson we're missing: **population
  ecology** — keep competing lineages, not one immutable chain. Add competing
  lineages for R5.
- **DreamCoder** — learned library growth via wake-sleep. `strategy.py` should
  become an MDL-compressed primitive library, not a stub. (Sprint #6.)
- **AlphaGeometry / AlphaProof** — neurosymbolic split: LLM proposes
  constructions/lemmas, symbolic engine decides survival. Our Generator +
  verifier-lens is a thin version; push proposals (invariant guesses, lemmas,
  representation shifts) to the LLM and survival to the symbolic side.
- **LeanDojo / ReProver** — for R7+ when proofs leave the templated regime;
  frame as "generate proof-state transitions with retrieval," not "LLM critiques
  proof text."
- **ILP (Popper/Metagol)** — non-LLM invariant miner: "find a predicate
  preserved by all legal moves and violated by the target." Directly an R5 lens.
- **ARC solver literature** — competing abstractions / transformation hypotheses.
- **Voyager** — skill-library accumulation (needs stronger anti-Goodhart guards
  in our setting).

## Bleeding-edge verdict (accepted framing)

The components are NOT novel (FunSearch = loop, DreamCoder = library,
AlphaGeometry = neurosymbolic, LeanDojo = formal proving). The **synthesis** may
be novel in packaging: externally-authored procedural capability ladder +
immutable lineage + typed failure residue + fixed mutability boundary +
climb-without-Goodharting framing. Describe it as:

> "An experimental integration of program-search, deterministic falsification,
> capability-ladder evaluation, and structured failure-memory for self-modifying
> reasoner code."

NOT "a new reasoning paradigm." The danger is overclaiming "synthetic reasoning"
before R5/R7/R8 demonstrate **representation transfer**.

## What this changes in our roadmap

- **De-prioritize** the v3 typed-representation rebuild (IC-1) until the
  substrate/search matrix falsifies the simpler bottlenecks. (Self-correction:
  we were about to over-invest in representation.)
- **Promote** to immediate: R4 generator, R5 gradient, trace-required grading,
  diff-failure taxonomy + Mechanic lens, the substrate/search matrix, bridge
  generators. (Most are cross-agent — they extend Harmonia B's ladder — so they
  are PROPOSALS pending James + Harmonia, except the Icarus-side matrix harness
  and the Mechanic lens which are ours.)
- **Add** population ecology (competing lineages) — a FunSearch lesson the
  immutable-single-lineage design currently lacks.

## Cross-agent vs Icarus-side split (for execution)

- **Icarus-side (ours to build now):** Mechanic lens + diff-failure taxonomy;
  the substrate/search matrix harness; competing-lineage support; the
  seeded-primitive diagnostic (pending the build-from-substrate tension call).
- **Cross-agent (propose to James / Harmonia_M2_B):** R4 generator, R5 gradient,
  trace-required grading, bridge generators, R7 procedural proof generation,
  ILP/exact-cover/Lean non-LLM lenses. These extend `harmonia/experiments/`.
