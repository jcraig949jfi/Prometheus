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

- **v6 (cycle 008, current):** two amendments from external round 3, both executed.
  (a) **R5 DEMOTED unless relational**: independent counterfactual evaluation decomposes
  into branch-generation + R4 + comparison. R5 stands only as coupled execution (the pair
  IS the state; run-twice cannot even execute) or relational invariants R(s0_k,s1_k)
  maintained through the run — the transient-violation probe kills endpoint comparison.
  State is a RELATION over executions: the genuinely new object. Cycle-007's single-pass
  result survives as a resource theorem, not a rung definition.
  (b) **Sixth coordinate: OPERATOR PLASTICITY** — fixed rules → parameterized compositions
  → cached macros → induced operators → revisable abstractions. Coordinates 1-5 describe a
  fixed transition algebra; Bands S/G require R_t → R_{t+1} (the machine modifies the
  language of its later reasoning). Fake-synthesis kill executed: trace cache dies on
  held-out substitutions; the induced operator survives; the vocabulary measurably grows.
  Convergence note: this is our gen-30-wall / menu-growth doctrine arriving independently —
  treated as a warning to test (hence the kill), not as confirmation. Generative-resources
  battery extended beyond binders: existential elimination with reuse/palette/aux_1
  pathologies all caught; SkolemID shows freshness = inexhaustible namespace, not RNG.

- **v7 (cycle 009, current):** external round 3 (restated) adds a SEVENTH coordinate —
  **epistemic objective**. Coordinates 1-6 assume the objective is SUPPLIED. Band G asks
  "what should I try to learn next?", and two actions with identical immediate progress can
  differ enormously in expected uncertainty reduction ΔU(a|H). Executable: identical unit-cost
  experiment pool, only the objective differs — info-greedy is optimal on EVERY instance
  (ceil log2|H|); myopic progress-greedy is O(|H|) in expectation with worst case |H|-1.
  Their two-ceiling prediction recorded: operator plasticity is the Band-S ceiling; epistemic
  objective the Band-G one, and the latter is the more dangerous for research behaviour
  ("I have many operations but don't know which unknown is worth attacking").
  **Methodological finding from building it:** the separation is in EXPECTATION — the myopic
  arm sometimes WINS per instance (truth=0 resolves in one step). A battery sampling one
  instance per system can certify the wrong selector. Fourth instance of the cheaper-mechanism
  law, and the first where the cheaper mechanism can beat the better one on a single draw.
  Also this cycle: R5's guarded product state (their exact toy — chasing behaviour no snapshot
  reproduces), symbolic held-out abstraction (novel SYMBOL, not novel integer), and
  revisability/negative plasticity (add-only system's degradation measured, not asserted).

- **v7 addendum (cycle 010, third relay of round 3):** most content was already built; the
  residue sharpened three things. (a) **Legality-gated pairs**: the relation gates
  ADMISSIBILITY, not just values — one world perturbed and the joint transition becomes
  illegal, the pair STUCK. Strictly stronger than a value-changing guard: "run twice and
  diff" cannot even be posed, since there is no second run, only a blocked joint execution.
  (b) **Capacity theorem as a property**: for ANY finite palette a Γ exhausting it exists
  (Hypothesis-swept over arbitrary palettes); unbounded namespaces unaffected.
  (c) **Cross-realization transfer** — the macro-cache killer symbolic held-out cannot do:
  same higher-level operator, DIFFERENT internal primitives (ints → mod-7 → polynomials).
  A cache carries the realization and is silently wrong in the new domain; a schema carries
  the operator and instantiates. Schema ORDER matters (double∘succ ≠ succ∘double), so
  "knows these primitives are useful" is not enough.

**Standing kill-battery inventory (all executable):** isomorph/fresh-seed (R0); coefficient-
hull escape + symbolic-parameter probes (R1); trace re-execution, CAS-layer leakage,
path-separating twins [spec'd], step-count priors (R2); disequality separation, scale probe,
**indistinguishable-state twins + lexicographic (soundness, −coverage) contract** (R3);
base-rate inversion, **nonlocal-discriminator + depth-escape + rule-name randomization**
(R4); single-pass memory metering + mid-stream queries + **non-additive post-fork dynamics**
(R5); coupled-dynamics inexecutability + transient-violation relational probes (R5-rel);
palette exhaustion, existential-elimination distinctness pressure, deterministic-freshness
(fresh-gen/Skolem); held-out-substitution fake-synthesis kill + corrupted-trace audit
(operator plasticity); expectation-over-space experiment metering + worst-case cost
(epistemic objective).

**Design finding (cycle 006, from the twins battery):** a bounded circuit's conservative
False on a forgotten fact IS a soundness violation on the twin pair — "conservative" and
"abstaining" are different behaviors, and batteries must offer an explicit abstention
channel once histories can exceed capacity, or they push honest circuits into lying.
