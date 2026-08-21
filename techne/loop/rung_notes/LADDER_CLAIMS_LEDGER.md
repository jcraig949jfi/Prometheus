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

- **v8 (cycle 011, current):** external round 4 adds coordinate 8, **epistemic-rule
  plasticity, constrained**: E_t -> E_{t+1} WITH retroactive revalidation and an
  evaluator-INDEPENDENT warrant. Executable: a corpus of 100 claims certified by a sampling
  evaluator contains an adversarial identity agreeing at every sampled point; after a
  warranted revision to symbolic normalization the plastic corpus retracts it AND its
  dependent (98 trusted), the fixed-evaluator corpus reports 100 forever, and a
  prospective-only revision leaves history contaminated until revalidation runs. The
  constitutional gate refuses the terminal cheat (revising failure to mean success).
  Also this cycle: R6 = provenance-sensitive diagnosis (non-unique proofs make
  rederive-and-diff SMEAR; and a corrupted derivation can have a legitimate endpoint, so the
  endpoint checker is not merely uninformative but wrong about the answer); and retraction
  proven necessary (add-only vocabularies poison a budgeted selector; guarding is not
  retraction; R_{t+1} SUBSET R_t must be possible).
  **PROMETHEUS CONNECTION:** coordinate 8 is the June-2026 formula-fossil finding in general
  form -- "2,351 promotions" were claims certified under a superseded gate that nothing
  revalidated. Retroactive revalidation is a missing organ we have already been bitten by,
  not a Band-G curiosity.

- **v9 (cycle 013, current):** round 5. (a) The cycle-012 doctrine was FALSIFIED and
  rewritten: identification is COMPETITOR-RELATIVE (finite observations never uniquely
  identify a mechanism; the universal danger is observational equivalence on the sampled
  support). Agreement-region unions are uncomputable, so batteries declare a threat model
  C<=k and conclude "not separated from C<=k". (b) R8 = CONSTRUCT a task-relevant
  representation-changing map (instance-derived partitions; precomputed views are R4).
  (c) Band-G machinery corrected: certification PROVENANCE (predicates invoked, not evidence
  consumed) + NEGATIVE dependencies (absence-of-record, invalidated by DB growth) +
  justification-vs-influence propagation + a thin immutable-observation constitution as the
  regress bottom.

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
(epistemic objective); proof-redundancy smearing + correct-endpoint/corrupt-middle (R6);
budget poisoning + guard-is-not-retraction (negative plasticity); adversarial-corpus
revalidation + unwarranted-revision refusal (epistemic-rule plasticity); instance-derived partition + catalogue-cannot-contain +
goal-incompatible quotients (R8); short-circuit predicate dirtying, DB-growth negative deps,
verify-without-upstream, un-fail-a-failure amendment refusal (Band G).

**Design finding (cycle 006, from the twins battery):** a bounded circuit's conservative
False on a forgotten fact IS a soundness violation on the twin pair — "conservative" and
"abstaining" are different behaviors, and batteries must offer an explicit abstention
channel once histories can exceed capacity, or they push honest circuits into lying.

## Cycle 016 — 8th instance, and the first one located INSIDE the canon

**Claim v10 (extension, not replacement of v9):** the competitor-relative law applies to
*kill tests specified by doctrine*, not only to circuits. Canon v2.0 §3 R9 names a circular-
lemma trap and specifies a kill test (proof-dependency-graph analysis) that cannot separate a
circular lemma from a load-bearing one — both are depended upon. Measured against Lean 4.30.0:
(lemma_true, goal_proved, load_bearing, accepted) = (True, True, True, True) for both.

**Kill-battery additions (executable):** deletion test + bounded-budget equivalence check +
flipped-equation evasion probe + over-strong-budget phantom-rejection probe (R9).

**Third sighting of the strength dial.** R3 (soundness, -coverage) lexicographic, R6
recall/phantom-rate, R9 catch-rate/phantom-rejection: in each case the battery has a tunable
whose two failure directions are a gaming surface and a false-kill rate. Recorded as a pattern,
not yet as a claim — a fourth sighting would justify promoting it.

## Cycle 017 — claim v11: instance-blind battery parameters (PROMOTED from pattern)

**Claim v11.** *A battery parameter that does not read the instance cannot separate instances
that differ.* Promoted on the fourth sighting, and stated as a specialisation of the
competitor-relative law: an instance-blind parameter makes the battery's observations
independent of the instance, so instances that differ are observationally equivalent to that
battery however sound each observation is.

**Evidence, R10 (cycle 017).** `FeatureSensitiveTransfer(k)` reads only (source world, target
world). Swept k = 0..3 over the 14-entry battery: (catch, phantom) = (0.00, 0.00) at k=0 and
(1.00, 1.00) at every k >= 1. The honest circuit sits at (1.00, 0.00), which is attained at no
setting. Structural argument, not a numerical accident: the circuit is constant across
techniques on a given world pair, while ground truth varies within the pair (measured: both
True and False occur for Z -> F_5[t]).

**The four sightings.** R3 capacity width (defeated by a history longer than the width); R6
search horizon (defeated by a counterexample past the horizon, Euler at n=40); R9 tactic budget
(defeated by a theory the budget cannot see); R10 feature count (defeated by ground truth
varying within a world pair). In each case the two ends of the dial are a gaming surface and a
false-kill rate, and the correct behaviour is a FUNCTION of the instance rather than a value.

**Second R10 finding, recorded separately (not yet a claim).** The R10 artifact requires two
independent instruments: assumption tracing supplies the broken assumption's NAME, running the
conclusion supplies the VERDICT and witness. Neither substitutes for the other, and the proof
is an instance where an assumption fails harmlessly — `frobenius_additive` assumes char 5, that
assumption is false in F_3, and the conclusion holds there anyway (a^5 = a in F_3). Watch for
a second rung where the artifact requirement forces two instruments; that would be a claim.

**Kill-battery additions (executable):** parameter-shifted near-analogy (q=5 breaks, q=3
transfers), technique-name randomisation, harmless-assumption-failure probe, dial sweep with
the structural constancy check (R10).

## Cycle 018 — claim v11 REWRITTEN as evaluator aliasing (external review, round 6)

**v11 (cycle 017, superseded):** ~~a battery parameter that does not read the instance cannot
separate instances that differ.~~ Misnamed the phenomenon — it pointed at dials, and the R9
deletion-only checker has no parameter at all yet fails identically.

**v11' (current).** *Evaluator aliasing / observational non-identifiability.* Let an evaluator
family `E_theta` observe only a projection `pi(x)`. Then `pi(x1) = pi(x2)` implies
`E_theta(x1) = E_theta(x2)` for all theta; if `Y(x1) != Y(x2)`, no theta is correct on both.
This is an impossibility proof against the whole family rather than a statement about tuning,
and it is a specialisation of the competitor-relative law: the aliased pair is observationally
equivalent TO THAT EVALUATOR.

**Refinement required in practice:** where family members differ in how much they observe, `pi`
must be the FINEST projection any member can see; a witness under the finest kills every member,
each seeing a coarsening of it.

**Battery-design rule (executable, `techne/ladder_circuits/aliasing.py`):** find two probes in
the same equivalence class under everything the evaluator can see, with different correct
verdicts. `find_aliasing_witness` searches; `family_cannot_be_correct` is the theorem;
`verify_family_incapacity` is the measurement that must agree with it.

**Retrofits (all executed, all producing witnesses):** R6 search horizon; R9 deletion test;
R10 world features. **R3 capacity width is NOT retrofitted — listed as unverified, not counted.**

**Strongest witness to date (R10, cycle 018):** at fixed q = 7 the technique `x^2 - a
irreducible` flips verdict with `a` alone (3^2 = 2 mod 7). The projection is the ENTIRE
(source, target) world pair — complete world knowledge — and it still aliases.

**Second cycle-018 result, recorded separately.** The R10 artifact requirement was too weak: a
BREAKS claim was supported by any populated witness field, and `UnknownCollapser` filled it with
a restatement of the assumption violation, manufacturing a refutation of the twin-prime
conjecture. Repair built: `is_supported_strict` demands `conclusion_status == REFUTED` — a
witness must witness the CONCLUSION. Generalises the R6 witness requirement: it is not enough to
demand a witness, one must demand that it witnesses the claim being made.

## Cycle 019 — claim v12: evidence has a type, AND types need a checker

**v12.** *Every artifact must witness the proposition attached to its own verdict — and the
type must be checked by something outside the circuit, because a type the circuit declares is
a label.*

The first half is external review (round 7), correcting cycle 018's over-strong "a witness must
witness the conclusion". Assumption-side evidence is the correct artifact for an assumption
claim: in F_3, `3 * 1 = 0` certifies that the characteristic is not 5. It cannot certify that
the conclusion is false. So `(BROKEN, UNKNOWN)` is fully supported carrying assumption-channel
evidence alone, and `(BROKEN, REFUTED)` needs both channels.

The second half is this cycle, learned from two red tests. Implementing the typing as a check
over the verdict's own fields was defeated at once: `UnknownCollapser` relabels its
`conclusion_status` as REFUTED at the same moment it moves the witness across, and the typed
check reads the label. **Typing over self-declared fields is typing over the attacker's
testimony.** `audit_verdict` re-derives every asserted status from the world and is deliberately
not a method on `TransferVerdict` — a verdict must not be able to certify itself.

**Measured.** Collapser: `typed_ok = True`, `verified_ok = False`, note *"conclusion_status
claims REFUTED, world says UNKNOWN"*. Honest circuit: sound on all three batteries, so the audit
costs it nothing (not the R6 phantom pathology in disguise).

**Known limit, recorded rather than papered over.** The audit works by querying the world. In
the `(BROKEN, UNKNOWN)` state the world cannot be queried, so an UNKNOWN claim is checkable only
against an external immutable registry of what is known open. That is a second independent
argument for the immutable-observation constitution proposal.

**Prior failures now readable as type confusions:** the R6 unwitnessed falsity claim (verdict
asserted, no witness of any channel); the R9 circular lemma (dependency evidence offered for a
contribution claim); the R10 collapser (assumption evidence in the conclusion slot).

**Corrections to v11-prime, both mine.** (a) The finest-projection argument requires that every
member's view FACTOR THROUGH the projection; incomparable observation sets admit no common
projection short of the full input, and incapacity must then be argued per observation class
(`verify_factorization`). (b) A witness shows any evaluator factoring through pi is wrong on AT
LEAST ONE member of the pair, not on both.

**Kill-battery additions (executable):** external audit vs self-declared status; fiber search
for witness SYNTHESIS (`fiber_search`, seeded at a=3 over F_7 and landing on a=2 where
3^2 = 2 mod 7); factorization precondition check; padded-assumption-list detection.

## Cycle 020 — claim v13, and the first counterexample to v11-prime

**Claim v13.** *No function of a record can detect what is absent from it.* Completeness is
therefore not establishable by any audit of the evidence, however external — it requires an
independent, pre-declared ledger of what was supposed to be there.

**Evidence (R11 selective reporter).** Forecast honestly, then decline to report the claims you
got wrong. Measured on the R11 battery: Brier 0.125 -> 0.0375, skill 0.500 -> 0.844,
`verify_refutations` clean, nothing falsified. Every number computable from the published record
improves. Completeness falls to 10/12 and is visible ONLY against the declared claim list.

**Relation to v12.** v12 says evidence must be typed and checked from outside the circuit. v13
is an escalation: some properties are not functions of the evidence at all, so no external audit
of the evidence suffices. This is the third independent argument for the immutable-observation
constitution (after circular legitimisation, cycle 013, and the un-auditable UNKNOWN, cycle 019)
and the first that demands a specific MECHANISM — a pre-declared ledger — rather than a rule.

**Caveat recorded against my own trap:** the selective reporter's reliability degrades
(0.0 -> 0.0375) under this particular drop rule, because dropping only confident-and-wrong
claims leaves survivors systematically under-forecast. Not a defence; a balanced drop rule would
not pay it.

## Cycle 020 — v11-prime: first genuine COUNTEREXAMPLE, and the rule it exposes

Two forecasters with byte-identical records on the R11 battery (one replays the other) are
aliased under the projection "the record". With the target being EMPIRICAL calibration on that
record, **no aliasing witness can exist** — the target is a function of the projection.

The general rule is cleaner than v11-prime itself:

> **Aliasing is escaped exactly when the projection is SUFFICIENT FOR THE TARGET.**

Empirical calibration is the rare case where sufficiency holds by definition. Change the target
to calibration on the next battery and the witness reappears on the same pair (ECE 0.500 vs
0.250 on SHIFTED_BATTERY). So v11-prime stands for every target anyone actually wants, and the
counterexample sharpens rather than overturns it.

**Second cycle-020 result, recorded as a framing rather than a claim.** At R11 the aliasing
witness is unbreakable from inside the situation, and the rung is the RESPONSE to it, not a
repair of it. R6, R9 and R10 all treated their witnesses as defects to design away. This
suggests rungs of two kinds — capability-defined and impossibility-defined — which canon v2.0
does not distinguish. Flagged to HITL (#53), no amendment proposed.

**Kill-battery additions (executable):** hedging-ties-on-calibration probe; refutation-beyond-
budget check (kills a memoriser without needing fresh instances); selective-reporting
completeness audit against a declared ledger; fiber-synthesised misleading streak.
