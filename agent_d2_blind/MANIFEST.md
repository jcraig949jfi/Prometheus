# AGENT D-2 — BLIND HOMOICONIC EVOLUTION
## Design Manifest (independent construction)

Author: agent D-2. Date frozen: 2026-08-27.
Status of this document: **frozen before any census code was written.**
Nothing in this run was derived from, or checked against, any prior attempt at this
experiment. No prior artifact was read. Directory `agent_d2_blind/` was empty at t0.

---

## 0. Target

> Can accumulated executable experience create reusable transformations of executable
> structure, such that a machine-native system learns new ways of modifying its own
> computational machinery without being given a human-authored taxonomy of kinds of
> cognitive change?

This is run adversarially. The deliverable is the smallest environment in which this
can **fairly fail**, plus the causal gates that would distinguish failure from success.

## 1. Claim ladder (kept strictly separate)

- **P0** useful transformations of executable structure are *expressible* under the frozen physics.
- **P1** they are *discoverable* by some search under a metered budget.
- **P2** discovered transformations *persist* and *transfer* frozen to held-out tasks.
- **P3** a learned transformation can itself be the *input* to a later learned transformation.
- **P4** developmental history *changes what is practically reachable* in later acquisition,
  measured against the strongest history-free baseline at equal budget.

Reachability (grammar census) is evidence for **P0 only**. It is never evidence for P1-P4.

### Verdict hierarchy (exact gates frozen in PREREG-EVIDENCE.md before M1 is written)

```
SUBSTRATE_INVALID
SUBSTRATE_VALID_NO_LEARNING
ENDOGENOUS_TRANSFORM
TRANSFERABLE_ENDOGENOUS_TRANSFORM
TRANSFORM_OF_TRANSFORM
HISTORY_CONDITIONED_MUTATION_ADVANTAGE
RECURSIVE_MUTATION_EVOLUTION
NULL_BASELINE_PRESERVATION   (only from the noise world's confirmation protocol)
```

## 2. Experimental boundary (no elimination claim)

Humans (me) fix: values, primitive operations, sorts, evaluator, error semantics,
budgets, probe batteries, worlds, selectors, admission gates. This is unavoidable and
is **not** claimed to be eliminated.

The narrow question is whether, *given* fixed physics, humans must ALSO hand the learner
categories such as "change the algorithm", "change the representation", "change the
routing", "wrap the control flow", "append", "add memory" — or whether useful executable
self-transformation arises compositionally from the physics alone.

**No taxonomy API.** The learner receives no operator named or shaped as
MACRO/ALGORITHM/REPRESENTATION/MEMORY/ROUTING/CONTROL_WRAP/PRE_TRANSFORM/APPEND, and no
semantic equivalent (no operator whose argument slot *is* "the thing to wrap/append/route").
It receives only the sorts and primitives of the frozen language. If a human later
recognises a learned transform as "a wrap", that is retrospective commentary and is
recorded in a separate file from any machine state.

## 3. Physics: one language, two uses

Homoiconicity is obtained by refusing to have two languages.

**Values** Val ::= Sym(str) | List(tuple of Val). No integers, no floats.
Booleans exist as a *separate sort* at the expression level and are never Vals.

**A program is a Val.** An *artifact* (something that solves a task) and a *transform*
(something that edits an artifact) are terms of the same language, run by the same
evaluator E. Therefore:

```
E(artifact,  input_val)     -> Val          (object use)
E(transform, artifact_val)  -> Val          (meta use; validated back into a program)
E(transform2, transform1)   -> Val          (transform-of-transform: free, not bolted on)
```

There is no host-language code generation anywhere. Learned machinery lives entirely
inside the frozen substrate; the host only enumerates, evaluates, meters and records.

**Base grammar G1 (LISPY), sorts V (value) and B (bool):**

```
V ::= x | nil | (q S)
    | (head V) | (tail V) | (self V)
    | (cons V V)
    | (if B V V)
B ::= true | false | (atom V) | (null V) | (not B) | (eq V V)

S in SYMS = a b c d x nil true false q head tail self cons if atom null not eq   (18)
```

Semantics: x is the single input; (q S) is the symbol constant S; head/tail error on
non-lists and on the empty list; cons errors if its second argument is not a list; self
re-enters the *whole current program* on a new input (the only recursion, budget-bounded);
eq is structural equality.

Rationale for this shape:
- (q S) ranges over the language's own symbols, which is what makes construction of new
  programs possible at all. This is disclosed physics, not a mutation taxonomy: there is no
  primitive that takes a program and adds/wraps/dispatches; there is only cons.
- self is the *only* control primitive beyond if. Traversal, iteration, accumulation
  and dispatch must all be *built*, not selected from a menu.
- No append, no map, no subst, no at-path, no everywhere. Any such behaviour must
  be composed, and the census measures what that composition costs.

**Errors** are first-class and carry executable geometry only: kind (head-of-atom,
tail-of-atom, cons-onto-atom, budget, depth), node path, step index at failure, recursion
depth at failure. No semantic diagnostic labels are ever produced or stored.

**Budgets** are metered in evaluator steps, separately per phase (section 9).

## 4. Grammar family (independently plausible bases)

Per the adaptivity rule, three bases are built and run through the *same* frozen substrate
tests. None may be repaired after seeing its census. Rejected bases are preserved.

- **G1 LISPY** — structural recursion over cons-cells (above).
- **G2 PATHEDIT** — a transform is a sequence of positional edits (at PATH OP) with
  OP in {put T, del, dup}, plus one positional-fixpoint form; no general recursion.
  Terms are still Vals, so it is homoiconic; its bias is positional rather than recursive.
- **G3 REWRITE** — a transform is an ordered list of (rule PATTERN TEMPLATE) with
  pattern variables, applied leftmost-outermost to a fixpoint under budget. Homoiconic;
  its bias is matching rather than traversal.

All three share Val, the probe batteries, the classifiers, the metering and the gates.

## 5. Substrate tests (frozen before the census executes)

- **ST1 Homoiconicity** — for each basis, apply(t2, t1) produces a Val that validates as a
  transform and runs; a two-level chain must execute (P3 is *possible* physically).
- **ST2 Determinism / totality-under-budget** — every program on every input either returns
  a Val or raises a typed error within the budget; repeated runs byte-identical.
- **ST3 Expressiveness floor** — for each candidate world, a hand-constructed witness
  transform exists in the basis. (Existence, not discoverability. P0 only.)
- **ST4 Non-privilege** — census gates of PREREG-CENSUS.md.
- **ST5 Alias stability** — semantic equivalence classes stable under probe-battery growth.
- **ST6 Residual characterisation** — the unclassified bucket must be characterised by
  executable secondary classifiers, not treated as "novelty".

## 6. Census plan (detail and thresholds in PREREG-CENSUS.md, frozen before execution)

Exact enumeration of the transform space to a preregistered horizon, then:
typed-valid outputs, structurally distinct transformations, semantically distinct
transformations under frozen probes, no-ops, destructive transforms, edit diversity,
minimal lengths per behaviour class, canonical ranks, and density of recognisable
human-legacy transformation families measured by **executable** classifiers.

Three diversity notions are reported separately and never conflated:
syntactic (program count) < structural-behavioural (distinct output terms on probes)
< semantic-behavioural (distinct extensional behaviour of those outputs).

Attacks run inside the census, not after it:
- **canonical order** — minimal size is ordering-invariant; *rank* is not. A preregistered
  battery of token orderings is run and rank-based statements are reported with their
  dispersion. No single favourable ordering is frozen.
- **classifier residual** — no gate may be passed by treating OTHER/MIXED as novelty.
- **semantic aliasing** — structural and extensional fingerprints are both computed;
  equivalence is reported as probe-relative, never as program equivalence.

## 7. History-free baselines (M0) — built and frozen BEFORE M1 exists

At minimum: canonical size-ordered enumeration; uniform sampling over typed-valid terms
at matched size; length-biased stochastic search; behaviourally-deduplicated enumeration.
M0 is not permitted to be stupid: the deduplicated variant is a genuinely strong generic
searcher, and a direct artifact search (skip transforms entirely) runs as a further control.

Equal opportunity is *static-tested*: M0 and M1 receive the same physics, language, worlds,
budgets, candidate accounting, verifier and gates. M1 additionally receives only
admissible developmental history. The observation interface handed to either arm is
enumerated in code and asserted field-by-field (allowlist, never denylist).

## 8. Worlds

Worlds are censused for bypasses *before* they are used for evidence, and killed on:
short trivial solution, single-family dominance, surface-metadata leakage, flat-feature
capture, a stronger generic algorithm making the phenomenon irrelevant, transfer overlap,
or budget-accounting artefacts. Rejected worlds are preserved.

Worlds are **not** built one-per-mutation-family. Each world requires interacting
structural edits whose decomposition is never told to the learner. One world contains
failures that no structural self-modification can causally repair; the correct outcome
there is NO TRANSFORM ADMITTED.

A transform is admissible only if it is a *function of the artifact*: it must convert
several distinct seeds into solvers of their own distinct tasks. This structurally
excludes constant transforms that merely emit one answer.

## 9. Metering

Separate counters: solving, candidate generation, transform execution, validation,
verification, confirmation, history processing, repertoire maintenance. Candidate-
independent work is hoisted out of candidate loops in both arms identically. Impossible
candidates short-circuit identically. Any arm's total is reported in absolute steps.

## 10. Anti-cheat battery

Static and dynamic tests against: world IDs, generator IDs, serialisation order, task
lengths, seed leakage, witness reuse, transfer overlap, oracle access, target leakage,
host introspection, filesystem access, human audit labels, cache contamination,
confirmation contamination, work outside the meter, success after budget exhaustion.

## 11. Generational rule (load-bearing)

Once PREREG-EVIDENCE.md is frozen, the evidence protocol is not rescued interactively.
A fatal methodological flaw discovered after evidence begins means: preserve the run, mark
its evidence invalid, state the defect, stop. No patching this generation into success.

## 12. Stop rule

Stop at the preregistered verdict. No scaling, no LLM, no open-ended evolution, no repair
of a failed evidence generation. A clean negative outranks a rescued positive.

## 13. Forbidden conclusions

No claim of AGI, consciousness, understanding, human-independent cognition, elimination of
human priors, or autonomous diagnosis. The strongest admissible statement is exactly:

> Under fixed computational physics and selection, accumulated executable history caused
> useful transformations of executable structure to emerge without selection from a
> predefined human taxonomy of mutation classes, and those learned transformations altered
> the future acquisition of additional transformations.

and it is only available if every gate below it fires.
