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

## Cycle 021 — R12 audited, and rungs are of two kinds (HITL #53 answered)

**Not a new claim; two resolutions and one confirmation.**

**Resolution 1: rungs come in two kinds.** R0-R10 are CAPABILITY-DEFINED — their aliasing
witnesses are breakable by a projection that reads more of the instance, and each rung's repair
was exactly that. R11 and R12 are IMPOSSIBILITY-DEFINED — the witness is unbreakable from inside
the situation, and the rung is the RESPONSE to it (calibration at R11; widen-the-universe at
R12). Canon v2.0 does not draw this distinction. Flagged to HITL, no amendment proposed under
vocabulary law 8.

**Resolution 2: canon R12's kill test IS an aliasing statement.** "A small closed universe"
formally reads "the projection is not sufficient for the target". Measured: `True`, `x <= 7` and
`s <= 14` all accept 64/64 on the 0..7 tuples universe and 256 / 128 / 120 of 256 on 0..15. The
canon wrote this in English in May; the instrument to state it formally arrived at cycle 018.

**Confirmation: claim v13 at its sharpest.** R12 generates its own candidate list, so best-of-N
is available to it. Mean score inflation over five seeds: +0.042 (N=2), +0.098 (4), +0.129 (8),
+0.173 (16), +0.188 (32), against honest means near 0.2. Nothing false in the emission; the
omission is the discarded attempts. **New limit found:** declaring N is insufficient, because a
generator can declare N=1 having run 32 times in a prior session. The pre-declared ledger must
span sessions, which makes the immutable-observation constitution a concrete engineering
requirement rather than a principle.

**Grader defect recorded against harmonia (not fixed by me):** conjecture-quality is
baseline-penalised, test-quality is not. A fixed probe chosen without reasoning averages 0.443
efficiency over five seeds and scores 1.000 on one. The undefended channel is where a gaming
system parks.

**Kill-battery additions (executable):** no-reasoning floor measurement per scoring channel;
closed-universe twin extension comparison; best-of-N inflation sweep.

---

# FIRST PASS COMPLETE — canon R0 through R12

Every rung has circuits, a kill test, traps and a green suite. Durable claims from the pass:
competitor-relative identification (v2), evaluator aliasing (v11-prime, with its factorization
precondition and its R11 counterexample), evidence typing with an external checker (v12), and
un-detectability of omission (v13).

**Standing caveat on the whole pass:** every battery in it is synthetic. This was instrument
CALIBRATION, not architectural validation. Second-pass priorities are in cycle_021.md.

## Cycle 022 — v11-prime NARROWED at R3, and the instrument found to be half-blind

**R3 claim, resolved.** The ledger carried "R3 capacity width" as an UNVERIFIED fourth instance
of aliasing since cycle 018. Verdict: **narrowed, not struck.**

- The cycle-006 twins DO alias the FIFO pipelines. Measured: identical bounded state, differing
  queried proposition, every width in the family wrong on one twin.
- They do NOT alias the LIFO pipelines. LIFO evicts the most recent arrival, so a fact declared
  first survives the flood; LIFO separates the twins perfectly.
- FIFO and LIFO views are INCOMPARABLE in both directions (verified twice: by
  `verify_factorization` and independently by partition refinement). No finest projection exists
  for the union short of the full history.

So incapacity holds **per observation class**, not for the family as stated. This is the
round-7 factorization precondition catching something in existing work rather than in a
constructed example, which is the first time that has happened.

## Cycle 022 — the aliasing instrument detects only ONE of two failure directions

**A projection can be wrong in two ways, with different logical force:**

- **Under-discrimination (merging):** `pi(x1) = pi(x2)`, `T(x1) != T(x2)`. An IMPOSSIBILITY —
  no member of the family is correct on both. This is what v11-prime is about and what
  `find_aliasing_witness` finds.
- **Over-discrimination (splitting):** `pi(x1) != pi(x2)`, `T(x1) = T(x2)`. **NOT** an
  impossibility — the family can be correct on both by treating them separately. The cost is
  that evidence does not transfer.

Found by sweeping R0, which reports NO aliasing witness (exact-AST keys never merge distinct
expressions) while being demonstrably defective in the other direction: `x + y` and `a + b`
share an answer and receive different keys. `find_splitting_witness` is the dual, and
`SplittingWitness.proves_impossibility` is a FIELD set to False, so the distinction survives
reporting — announcing a generalisation cost as an impossibility would be the v12 evidence-
typing error committed by the instrument itself.

**Consequence for the first pass, recorded rather than quietly fixed:** every "no aliasing
witness found" result from cycles 018-021 ran only half a sweep. None were reported as clean
bills of health, but none ran the dual either.

**Kill-battery additions (executable):** per-policy twin construction (`twins_for_policy`);
cross-policy incomparability check; splitting-witness search; CAS-delivered-congruence probe
(does the key see the transformation the claim is about, or does the CAS normalise it away?).

## Cycle 023 — the two sweep directions unified, and two self-corrections

**The unification.** With P = fibres of the projection and T = fibres of the truth:

    deficit = H(T | P)   ALIASING   -> an impossibility
    excess  = H(P | T)   SPLITTING  -> a cost, in bits
    VI(P,T) = deficit + excess,  zero iff the projection is sufficient AND necessary

`H(P|Q) = 0` exactly when Q refines P, so **deficit > 0 iff an aliasing witness exists** and
**excess > 0 iff a splitting witness exists**. Verified under Hypothesis (250 examples) and
independently against the witness search on real rung data. This answers the measurement
question cycle 022 left open: pair counts scale with the battery, bits do not.

**Self-correction 1 (cycle 020).** Empirical calibration is SUFFICIENT BUT EXCESSIVE, not
exactly sufficient. Deficit 0.000 — the counterexample to v11-prime stands — but excess 1.200
bits: honest, hedging, memorising and mimicking forecasters all score ECE 0.0000 on four
different records. The surplus is what predictive calibration needs.

**Self-correction 2 (cycle 022).** Splitting is not automatically a cost. R9's checker carries
0.689 excess bits separating decorative from circular lemmas; R10's carries 0.324 separating
(BROKEN, SURVIVES) from (PRESERVED, SURVIVES). Both are deliberate diagnostic detail. Excess
measures finer-than-the-truth-function-requires, so a coarse truth function inflates it. **An
excess figure is meaningless without stating the truth function's granularity.**

**Two patterns, both flagged rather than claimed.**
(a) Exact-syntax circuits (R0, R1) are never aliased and always excessive. No impossibility is
    available against a projection that never merges anything — so the aliasing instrument used
    alone would pronounce the two lowest rungs defect-free, and its scope may be narrower than
    claimed since cycle 018. Flagged to HITL #69.
(b) R12 in-universe is the ONLY exactly-sufficient projection in the ladder (VI = 0), and it is
    precisely the closed-universe situation canon warns against. A perfect sufficiency reading
    is a prompt, not a result.

**Sweep coverage (cap honoured, two cycles).** Swept: R0, R1, R3, R6, R9, R10, R11, R12.
**Unswept: R2, R4, R5, R7, R8** — a known gap, carried explicitly.

**Kill-battery additions (executable):** sufficiency measurement in bits
(`sweep.sufficiency`); deficit/excess vs witness-search agreement check; truth-function
granularity disclosure alongside any excess figure.

## Cycle 024 — composition: claim v14, and a third arrival at "contract, not metric"

**Claim v14 (composition).** *Along any pipeline, deficit is non-decreasing and excess is
non-increasing.* A pipeline induces a refinement chain (stage k+1 sees only stage k's output, so
its fibres are unions of stage k's), and the data-processing inequality (Cover & Thomas 2nd ed.,
Thm 2.8.1) does the rest. Consequences:

- A chain cannot repair an upstream loss. Composition only ever discards.
- The only question a composition poses is whether what it discarded was excess (free) or
  deficit (fatal).
- **Seam location is a measurement, not a hunt:** the first stage where deficit rises above zero
  is where the chain broke. Measured at 1.918 bits at `degree_only` in the locally-sound chain,
  whose every stage is sound for its own local target.

**And the instrument is aliased against its own traps.** Under the projection "the chain's
profile", the sound and shortcut chains are indistinguishable (byte-identical profiles) while
differing on whether the stages are used at all. Three detectors are required and none is
redundant:

    profile        catches  locally-sound-but-globally-lossy
    ablation       catches  shortcut (R9's deletion test, lifted to stages)
    intervention   catches  interface laundering

**Withdrawn detector, kept renamed.** `discards_nothing` (VI(P_k, P_{k-1}) = 0) was built as the
laundering signature and fires identically on the SOUND chain's `together`, which is injective on
the battery. **Injectivity and laundering are indistinguishable to any information measure.** Now
`is_injective_on`, with the failure in its docstring.

**THIRD ARRIVAL at "the measurement cannot see it; an external declaration must."**
1. Completeness — no function of a record detects what is absent (v13, cycle 021).
2. Reference-class choice — a forecaster picking its own class can pick a flattering one (R11).
3. Interface entitlement — laundering is a CONTRACT violation, not an information-flow property;
   the bits are present in both chains and only entitlement differs (this cycle).

Three independent arrivals is enough to treat as one phenomenon rather than three coincidences.
If it is one phenomenon it wants one mechanism, and the immutable-observation constitution is the
candidate. Flagged to HITL #73 as the fourth independent argument for that proposal.

**Kill-battery additions (executable):** refinement-chain check; per-stage information profile
with seam location; stage ablation preserving chain type; declared-output corruption
intervention.

## Cycle 025 — first real-substrate contact: claim v13 confirmed in production, v14 does not transfer

**Claim v13 CONFIRMED OUTSIDE THE LAB.** "No function of a record can detect what is absent from
it" was derived from a toy at cycle 021. At cycle 025 it appeared unprompted in live code:
`ergon/probe`'s `load_prepass` drops 100% of a 333-row campaign ledger (writer emits
`key: [rep, uid]`, loader filters on a top-level `rep`), and the pipeline reports the stratum
UNSUPPLIED rather than unreadable. Absence and unreadability are indistinguishable downstream,
and the system reports the benign one. This is the strongest evidence the claim has.

**Claim v14 (composition profiles) DOES NOT TRANSFER to content pipelines.** Measured, and
recorded as a negative result rather than repaired:

- Every real record renders to a unique string and stays unique through render and redaction, so
  every stage partition is all-singletons and `deficit = H(T|P) = 0` by construction at every
  stage for every truth function.
- **Partition measures see INTER-record distinguishability; every stage in this pipeline is an
  INTRA-record content transform.** The axes are orthogonal.
- Demonstrated by ablating the stage under test: replacing redaction with the identity leaves
  every number the profile produces unchanged.

**Scope statement for v14, added:** the composition profile applies to chains whose stages SELECT
or REORDER (discovery pipeline, ranking stages), not to chains whose stages REWRITE. That
boundary was not visible from synthetic work, where the two coincided because the toy stages did
both at once.

**Cycle 022's R0 result, at production scale.** An injective projection can never be aliased, so
a clean reading from one is uninformative rather than good. I had that result four cycles earlier
and still expected the instrument to transfer.

**What the right instrument said.** Ergon's own `leaks_verdict` post-condition: 120/120 rendered
records leak, 0/120 after redaction. The firewall is sound on real data. A one-line predicate
beat the partition machinery, which is worth remembering the next time an instrument gets built
before a target is chosen.

**Kill-battery additions (executable):** non-empty-file zero-row parse check; instrument
self-ablation (disable the stage the instrument watches and confirm its numbers move).

## Cycle 026 — claim v14's scope statement VINDICATED on live data

Cycle 025 narrowed v14 (composition profiles) to chains whose stages SELECT or REORDER, after
the instruments proved blind to ergon/probe's render/redact content transforms. Cycle 026 tested
that narrowing on the selection stages of the same module, on the same day, with the same
instruments.

**Measured** — live campaign pool (369 records), 24 target tasks, 8,000-token ceiling:

    plain `_order` + tail truncation      deficit 4.5850 bits   1 distinct head / 24   cov 5/369
    `_order_per_task_stratified` (BC-2)   deficit 0.0000       24 distinct heads       cov 95/369
    H(task) = 4.5850 bits

Plain ordering's deficit **equals the task entropy exactly** — a packet identical for every task
has one fibre, so H(T|P) = H(T) identically, and the normalised deficit is 1.000. BC-2 takes it
to zero and multiplies pool coverage nineteen-fold.

This reproduces Charon's independently-measured constant-packet defect (~0.5% of a 4,581-record
pool, every task the same window) from a different direction and as a number rather than a
narrative.

**The scope split is now measured, not asserted:**

    SELECT / REORDER stages   partition measures work        (deficit 4.585 vs 0.000)
    REWRITE stages            partition measures are blind   (identical with the stage disabled)

**Consequence for the arsenal:** two families of pipeline stage, one family of instrument. The
correct instrument for a rewrite stage is the pipeline's own predicate re-run on the output —
not a partition measure, and probably not convertible into one, since it would require
partitioning a record's internal token space, which has no ground truth. Flagged to HITL #88
before investing in a second family.

**Limitation recorded:** BC-2 has two halves (source round-robin, timeline bucket interleave) and
the campaign pool is single-source, so only the second was exercised. The measurement is a lower
bound on BC-2's effect.

**Track 1 addition:** `normalized_deficit = H(T|P)/H(T)`, since bits are not comparable across
batteries with different target entropies. Raises on a constant target rather than returning 0 —
a battery with no target variation cannot test sufficiency, and reporting 0 would claim one it
never measured.

**Kill-battery additions (executable):** constant-packet detection via deficit-equals-target-
entropy; per-task head-variation count; pool-coverage ratio under repeated truncated draws.

## Cycle 027 — claim v14 NARROWED AGAIN: a third stage type, and this one inverts

v14 (cycle 024) asserted that along any pipeline deficit is non-decreasing and excess
non-increasing, by the data-processing inequality. Cycle 025 narrowed it to stages that SELECT or
REORDER after finding it blind to REWRITE stages. Cycle 027 finds a third category where it is
neither blind nor applicable but **inverted**.

**Measured** — discovery pipeline kill-path battery (F1/F6/F9/F11), 34 real reciprocal
polynomials with high-precision Mahler measures, Lehmer's among them:

    deficit  1.8295 -> 0.8698 -> 0.0000 -> 0.0000 -> 0.0000     H(terminal) = 1.8295 bits
    forward is_refinement_chain  = False
    reversed is_refinement_chain = True

A falsification battery ADDS a verdict bit per check and discards nothing, so the state refines
forward. Deficit DECREASES — what a working battery should do, and what v14 asserts cannot
happen. `is_refinement_chain` reports False on a healthy battery.

**v14, current statement.** The profile's monotonicity holds for DESTROYING chains only. Its
direction must be established before it is read, and `chain_direction` (DESTROYING /
ACCUMULATING / NEITHER) is the precondition.

**Stage-type taxonomy, all three measured on live code:**

    transform / rewrite    instruments BLIND      cycle 025, ergon render/redact
    select / reorder       instruments WORK       cycle 026, ergon _order vs BC-2
    filter / accumulate    instruments INVERTED   cycle 027, discovery battery

**Blind is safe; inverted is not.** An empty reading is obviously useless; a confident wrong one
is not. This is the first stage type where the instruments would have produced a false verdict
rather than no verdict.

**Second finding — R11 reappears inside a real falsification battery.** Per-check resolution:
F1 = 0.9597 bits, F6 = 0.9082, F9 = 0.0000, F11 = 0.0000. Two of four members never fire on the
candidates measured, and the terminal verdict is settled after F6. A member that never fires is
observationally identical to an absent member and both are perfectly "sound" — canon R11's
hedging forecaster, in production. Caveat recorded: 34 candidates in a narrow band is a small
sample, and a non-firing check may be guarding a rare failure mode.

**Kill-battery additions (executable):** chain-direction precondition check; per-member
resolution measurement for a battery (advertised size vs measured discriminating size).

## Cycle 028 — a structural zero is not a sampling zero

**Cycle 027 reported F9 and F11 at 0.0000 bits over 34 candidates with a sample-size caveat.
Cycle 028 removed the caveat and found the caveat was answering the wrong objection.**

Widened sample: n = 81 (vs 34), degrees 2-8, coefficients to ±5, 37 reciprocal and 44
NON-reciprocal, M spanning 1.0000-9.6071 rather than one narrow band. F9 and F11 stay at exactly
0.0000. But the source settles it harder, and the two zeros have DIFFERENT causes:

- **F9 is structurally constant.** `return True` with no computation on the input; True even for
  the empty list. No candidate set at any size can make it fire.
- **F11's cross-validation path is vacuous by a theorem.** M(p) = M(reverse(p)) for every
  polynomial, since reversal maps roots α -> 1/α and swaps the leading and trailing coefficient.
  Verified on 40 random non-reciprocal polynomials: zero disagreements. Its surviving branch
  tests the CALLER's reported M — real, but no property of a candidate can trigger it.

**Measured battery strength:** F1 0.9599 bits, F6 0.2285, F9 0.0000, F11 0.0000 — four advertised
members, two discriminating. Neither silent member is fraudulent (one record-keeper, one
bookkeeping assertion); the COUNT is what overstates. Anything that "survived the four-member
battery" survived a two-member test.

**Unexpected second result, and more troubling than the zeros.** F6 measured 0.9082 bits on the
narrow band and 0.2285 on the wide one. **A battery's strength is not a property of the battery;
it is a function of the candidate distribution.** Every "survived the battery" claim is
implicitly relative to the distribution it was tested on. This may be R11's reference-class
problem wearing new clothes.

**Proposed standing rule (HITL #98, awaiting ruling).** When a measurement reads zero, read the
source before collecting more data: a structural zero and a sampling zero are indistinguishable
by sampling and only one is fixable by it. Mechanical form: mutation-test the member's input
space and check whether ANY input flips it. This makes an existing memory
(`feedback_verify_signature_exists_before_controls`) executable rather than habitual.

**Track 1:** `prometheus_math.battery` — advertised vs discriminating size, refusing both to call
a silent member useless and to guess whether it CANNOT fire or merely HAS not.

**Kill-battery additions (executable):** structural-constancy probe (does any input flip this
member?); independence probe for a "cross-validation" path (can the second path DISAGREE on any
input?); battery strength reported with its candidate distribution.
