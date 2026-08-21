# Ladder Claims Ledger — the v1→v5 arc (living; updated per cycle)

Falsification-first bookkeeping for the loop's central theoretical object. Each version
states what killed its predecessor. Executable evidence lives in `techne/ladder_circuits/`.

- **v1 (cycle 001):** Band E rung = coarseness of the AST congruence the circuit's key
  respects. *Killed by R1:* answers vary within a template class — a congruence returns
  class-constant answers.
- **v2 (cycle 002):** rung = (congruence coarseness, witness arity, guard complexity); R1 is
  a guarded fibration. *Killed by external review (ChatGPT r1) + R2 build:* too expressive
  to break — unbounded witnesses make "witness-passing" describe everything; and what flows
  at R2 is an unbounded expression, not fixed-arity witnesses.
- **v3 (cycle 003):** rung = TYPE of carried state; R3 = R2 + blackboard. *Killed by the
  cycle-004 experiment (predicted by ChatGPT r1):* without a resource bound, a
  history-threading pipeline IS a blackboard — demonstrated by test (width-n ≡ store).
- **v4 (cycle 004):** rung profile = (equivalence class, witness structure, guard
  complexity, **state topology**), state topology = none → local params → sequential
  bounded → +iteration → persistent queryable, WITH resource bounds as part of every rung
  claim. *Survived R4 (cycle 005) with a sharpening:* at R4 the axis branches — selector
  (policy π(s,G,A)→a, the minimal ingredient per ChatGPT r2) vs branching+verification
  (stronger; needs a checker). *Survived the twins battery (cycle 006).*
- **v5 (cycle 006, current):** v4 + a fifth coordinate: **generative resources** — some
  operations must MINT a witness satisfying a global negative constraint (fresh binder
  names; and beyond binders: Skolem symbols, auxiliary variables, fresh lemma names).
  Guarding (checking freshness) and generating (producing it) are DIFFERENT powers,
  separated executably: the guard-only circuit detects capture and halts; only an allocator
  completes α-renaming; a bounded palette is adversarially exhaustible (the capacity
  phenomenon recurring one level up). Credit: ChatGPT r2 item C; build: fresh_generation.py.

- **v5 addendum (cycle 007, R5):** state topology gains PARALLEL composition — live
  co-resident branches, separated from run-twice-and-diff ONLY under single-pass input +
  metered memory (replay buffer = smuggled blackboard, the v3 kill recurring one rung up).
  Recurring law, third instance: every rung has a cheaper mechanism exact on a restricted
  battery slice (R0 retrieval/clean, R4 prior/stable-rates, R5 delta/additive) — batteries
  must be built to leave the slice.

**Standing kill-battery inventory (all executable):** isomorph/fresh-seed (R0); coefficient-
hull escape + symbolic-parameter probes (R1); trace re-execution, CAS-layer leakage,
path-separating twins [spec'd], step-count priors (R2); disequality separation, scale probe,
**indistinguishable-state twins + lexicographic (soundness, −coverage) contract** (R3);
base-rate inversion, **nonlocal-discriminator + depth-escape + rule-name randomization**
(R4); single-pass memory metering + mid-stream queries + **non-additive post-fork dynamics**
(R5); palette exhaustion (fresh-gen).

**Design finding (cycle 006, from the twins battery):** a bounded circuit's conservative
False on a forgotten fact IS a soundness violation on the twin pair — "conservative" and
"abstaining" are different behaviors, and batteries must offer an explicit abstention
channel once histories can exceed capacity, or they push honest circuits into lying.
