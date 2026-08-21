# Rung R3 — Constraint Maintenance · Circuit Study (Loop pass 1, cycle 004)

**Canon:** Band E. R3 = tracks multiple constraints; rejects inconsistent candidates.
**This cycle folded in the first external review** (ChatGPT via James, 2026-08-21) — it
reshaped the claim before the experiment ran, and the experiment then CONFIRMED the reshape.

## 1. The critique, adopted (with credit)

1. **v2/v3 were too expressive to break**: if a "witness" may be any AST, witness-passing
   describes everything. The ladder needs a RESOURCE RESTRICTION to stay discriminative.
2. **The true R2 breaker is unbounded iteration**, not expression growth: "apply until no
   match" over arbitrary n is not any fixed pipeline. Iteration is a new combinator.
3. **"R3 = R2 + blackboard" collapses** without a bound — threading full history IS a
   blackboard. Killable boundary: bounded local state vs persistent queryable facts.
4. e-graphs earn rent at late-R2 (noncanonical composition), not generic R2.
5. New trap: **endpoint shortcutting** — kill with path-separating twins + probes where the
   final answer matches but an intermediate must differ.

## 2. Claim v4 (adopting their state-topology coordinate)

Band E rung profile = (equivalence class, witness structure, guard complexity,
**state topology**), with state topology the load-bearing axis:

    none → local parameters → sequential bounded → (+iteration) → persistent queryable

R0 = none · R1 = local parameters · R2 = sequential bounded, fixed program · R2.5 = plus an
explicit iteration/fixpoint combinator · R3 = persistent, content-addressable store.

## 3. Executed evidence (all green: `test_r3_separation.py` 5 + `test_r2_pipeline.py` +3)

- **Separation (their minimal family, implemented):** declare x_1≠0…x_n≠0, noise, then
  adversarially query an evicted fact. For every n > width and both canonical eviction
  policies (FIFO/LIFO), the fixed-width pipeline fails where the constraint store succeeds;
  for n ≤ width they agree everywhere (Hypothesis-swept). Scale probe: n = 500, width 16,
  random early query — store True, pipeline False.
- **The v3 collapse, demonstrated:** a width-n pipeline is observationally identical to the
  store — without the bound there is nothing to kill. (So cycle-003's v3 as written was
  WRONG; recorded as such, not patched silently.)
- **Iteration ingredient:** succ-tower family — a fixed 3-step program dies at depth 5;
  `run_until_fixpoint` handles depth 60 with one rule; budget exhaustion fails loudly.

## 4. Trap ledger additions

- **Trap 11 — endpoint shortcutting** (theirs): path-separating twins; same start, same
  rules, different supplied paths must yield different outputs/intermediates. Strong form:
  final answers equal but an intermediate must differ — catches endpoint-invariant learners.
  (Complements trap 8, which assumes the checker can re-execute; twins work black-box.)
- **Trap 12 — hidden recursion in an "R1 rule"** (theirs, implicit): a rule whose apply()
  loops internally smuggles R2.5 into R1. Countermeasure: rules must be step-bounded;
  audit = call the rule on its own output and require progress or no-match, never a loop.

## 5. Next-pass questions

- The bounded circuit here is conservative (abstains when it forgot). An UNSOUND variant
  (guesses True) would pass more queries while being wrong — batteries must score soundness
  and completeness separately, or capacity pressure rewards liars.
- Their reply conceded binder rewriting is *probably* accommodation (environment witness +
  freshness guard) — untested. A capture-avoidance probe belongs with the R8 representation
  study later in this pass.

*— Techne loop, cycle 004.*
