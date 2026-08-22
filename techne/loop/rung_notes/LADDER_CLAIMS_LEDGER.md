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

## Cycle 029 — the structural-constancy probe, and a negative result worth having

**HITL #98 discharged: the standing rule is a tool.** Two tiers with different logical force,
plus an honest middle:

    VARIES                 a flipping input exhibited              proof it CAN fire
    PARAMETER_INDEPENDENT  body never loads its own args (AST)     proof it CANNOT
    UNSETTLED              reads them, nothing probed flipped it   honest

The static tier is conservative by construction — unreadable source, builtins and anything
unparseable all report "reads its parameters", so an unanalysable function is never CLAIMED
independent. `can_fire` is None for UNSETTLED: unknown, never silently safe.

**Sweep result, and the headline is NEGATIVE.** Twelve members across `discovery_pipeline`,
`lehmer_brute_force` and `canon_r6_falsification`: **F9 is the only structurally-constant member
found anywhere.** The substrate does not have a systemic dead-check problem. One instance,
already reported. The value of the result is that it came from a search rather than an
assumption.

**F11 refines cycle 028.** Hostile probe space: VARIES. Well-formed candidates: 0.000 bits. Both
true. Natural sampling measures REALIZED discrimination; mutation testing measures CAPABILITY.
**A constancy verdict must carry its input space.**

**The probe caught its own author.** The first sweep reported two `lehmer_brute_force` members
UNSETTLED. My probes were the wrong shape (full coefficients where length-8 half coefficients
were required), every call raised, and the probe — mapping all exceptions to one sentinel — saw
"one distinct value, no flip", which is indistinguishable from constancy. An instrument fault
dressed as a finding. Repaired with `n_evaluated` and an `INVALID_PROBE` status that precedes
every other verdict. **The finding I nearly published was entirely my own bug**, and the near-miss
is the argument for the repair.

**Known gap, declared up front.** Parameter-independence is SUFFICIENT for verdict-constancy, not
NECESSARY: a member can read its argument for a purpose that never reaches the verdict, as my own
EagerFalsifier and CredulousAsserter do. Those land in UNSETTLED correctly but unsatisfyingly.

**Reference-class problem, third arrival.** R11 (self-chosen reference class), battery strength
(F6: 0.908 narrow / 0.229 wide), and now constancy (F11: constant well-formed / varies hostile).
Each time the answer depends on a domain nobody declared, and each time the candidate fix is to
declare the input space as part of the specification. That is the pre-declared-ledger mechanism
in a third costume — flagged to HITL #104 as possibly one phenomenon rather than three.

**Kill-battery additions (executable):** parameter-independence AST scan; hostile-input mutation
search; INVALID_PROBE guard against an all-raising probe space; `ran/probed` denominators on
every verdict.

## Cycle 030 — claim v15: one core, two kinds of domain-relativity

**The reference-class problem arrived three independent times (R11's self-chosen class, battery
strength varying with candidate distribution, constancy varying with probe space). The question
was one phenomenon or three. The answer is neither.**

**Shared core (real).** Each is a property `Phi(O, D)` of an object AND a domain, stated as though
it were a property of the object alone, with the speaker choosing `D`. Same fix in all three:
make `D` part of the claim, refuse a claim without one.

**The split (measured), and it is claim v15.**

- **EXISTENTIAL claims are MONOTONE.** A witness stays a witness, so a positive existential holds
  on every superset of the domain it was found in. F11: UNSETTLED on well-formed input, VARIES
  once hostile input is added, VARIES on every superset. Only the NEGATIVE is domain-relative.
- **AGGREGATE claims are NON-MONOTONE in BOTH directions.** F6 over real candidates: 0.0000 bits
  on a subset excluding every firing case, **0.3651** after adding them (increase), **0.2285** on
  the full set (decrease). A superset value cannot be inferred in either direction, only
  re-measured.

> A witnessed existential may eventually be stated absolutely. An aggregate never may.

**Self-correction recorded.** My first pass exhibited only decreases, which would have left the
reading "monotone downward, therefore still well-behaved" open. The increase had to be
constructed deliberately. **To claim non-monotonicity, exhibit a move in both directions** — one
direction is consistent with a bound.

**Mechanism: `prometheus_math.relative_claim`.** Named, content-addressed domains; claims that
carry theirs. A claim without a domain is refused rather than defaulted (every one of the three
arrivals was an undeclared default read as universal); a positive existential without a witness is
refused (it cannot travel, so it is an aggregate in disguise); `entails_on` is true only for a
witnessed positive existential on a superset; aggregates never entail, not even on their own
domain.

**Constitution bearing, stated without inflation.** The declared-domain mechanism shares the SHAPE
the immutable-observation constitution needs but is not the same mechanism — the constitution
governs what the RECORD says, this governs what a CLAIM means. Four arguments for the
constitution, plus one adjacent requirement.

**Open (HITL #112):** is the split exhaustive? A UNIVERSAL claim is the obvious third — monotone
DOWNWARD, breakable by widening and never establishable by it — which would make the taxonomy
three-with-a-symmetry. Flagged rather than assumed.

**Kill-battery additions (executable):** undeclared-domain refusal; witnessless-existential
refusal; aggregate-entailment refusal; both-directions requirement for a non-monotonicity claim.

## Cycle 031 — claim v16: the kinds are a 2x2, derived

**HITL #112 asked whether cycle 030's two kinds were exhaustive and offered UNIVERSAL as the
third. Three was not exhaustive either.**

**Claim v16.** A domain-relative claim written as `Phi(O, D) = A({phi(O, x) : x in D})` inherits
its behaviour under domain extension entirely from `A`'s monotonicity under multiset extension.
"Monotone up?" and "monotone down?" are independent booleans, so there are exactly four kinds:

    up  down   kind          aggregations
    T   F      EXISTENTIAL   any / max / count / sum of non-negatives
    F   T      UNIVERSAL     all / min-as-a-requirement
    T   T      INVARIANT     an A that ignores the multiset
    F   F      AGGREGATE     mean / rate / entropy / variance — anything NORMALISED

Exhaustive by construction rather than by survey: no fifth kind without a third monotonicity
direction.

**The load-bearing measurement.** The same statistic changes kind depending only on whether it is
divided by |D|. F6's firings over a real nested chain: COUNT 0, 3, 3, 3 (monotone up,
EXISTENTIAL); RATE 0.0000, 0.1304, 0.0566, 0.0370 (up then down, AGGREGATE). Same predicate,
same data, same firings. **A claim's kind is a property of its aggregation operator, not of its
subject matter** — and "is this rate a fact about the object?" always answers no.

**The duality, tested on real substrate.** A holding UNIVERSAL travels downward to subsets; its
negation is an existential (a counterexample) and travels upward. Kronecker's M >= 1 holds across
81 real polynomials and travels down; canon R6's "every refutation carries a witness" fails for
EagerFalsifier, and the counterexample found on a 1-conjecture subset survives to the
6-conjecture superset. The module now refuses a failed universal without its counterexample,
symmetric to refusing a positive existential without its witness.

**INVARIANT closes the cycle-029 loop.** F9 is parameter-independent, therefore domain-independent,
therefore INVARIANT — "F9 cannot fire" is one of the very few claims in this loop that
legitimately needs no domain qualifier.

**Declared soft spot (HITL #117).** The derivation assumes every domain-relative claim can be
written as an aggregation over INDEPENDENT per-element values. Irreducibly relational claims may
not fit that normal form, in which case the 2x2 classifies a subclass rather than everything.
Recorded as a limit on the exhaustiveness claim, not as a footnote.

**Kill-battery additions (executable):** `kind_from_monotonicity` (the 2x2 as code);
`probe_monotonicity` over a nested chain, refusing a non-increasing chain; count-versus-rate
comparison as the normalisation probe.

## Cycle 032 — round-8 fold-in: two published claims narrowed, one superseded

**Merge/split duality (cycle 022) — SCOPED.** It exhausts CLASSIFICATION ERROR against a fixed
target. It does NOT exhaust REPRESENTATION ADEQUACY: a projection can induce exactly the truth
partition (VI = 0) and have destroyed everything a later task needs. Measured on integers 2..41 —
the primality projection is perfect for "is it prime" and loses 1.9567 bits against "smallest
factor". Adequacy is quantified over FUTURE targets, a different quantifier.

**New measure alongside the old.** `H(P|T)` is distribution-dependent, so a shattered rare corner
looks cheap (0.3322 bits for a 10-of-100 cell, against 0.7851 for the same shattering in the
90-cell). `refinement_multiplicity` reports worst-case fragmentation. Under cycle 031's 2x2 they
are different KINDS — multiplicity is max-of-counts (EXISTENTIAL), excess bits are normalised
(AGGREGATE) — verified in both directions only after a first chain made both look monotone.

**Per-class incapacity (cycle 022) — SUPERSEDED.** With infinitely many incomparable observation
classes, enumeration cannot finish, and "we could not enumerate, therefore possibly sufficient" is
a fallacy. A parameterised adversary constructor kills the family with one schema. Run against R3:
24 parameters (widths 1-12 x both eviction policies), 24 witnesses, schema survived.
`proves_family_incapacity` is hardcoded False — the schema's correctness is a UNIVERSAL claim over
the parameter space, monotone downward, so sampling refutes and never establishes.

**Preprocessing credit (cycle 022) — WORSE THAN REPORTED.** R0's projection is
`srepr o sympy-normalisation`. Seven of eight source-level distinctions are erased before the
circuit runs: commutativity, associativity with constant folding, power collapsing, rational
normalisation, sqrt evaluation, cancellation. Only `x*(y+1)` vs `x*y+x` survives for the circuit
to distinguish. **Open and consequential: if the CAS delivers most low-rung invariance, R0 and R1
may be measuring sympy's normaliser rather than any reasoning.**

**Kill-battery additions (executable):** second-target within-class loss; worst-case refinement
multiplicity; uniform adversary schema check; CAS-delivered-invariance probe.

## Cycle 033 — claim v16 SURVIVES, over a wider normal form, with two preconditions

**The soft spot declared at cycle 031 (HITL #117) is resolved.** The 2x2 derivation assumed
aggregation over independent PER-ELEMENT values; irreducibly RELATIONAL claims — "the domain
contains two elements that disagree", exactly what `find_aliasing_witness` computes — did not
obviously fit.

**They fit. The repair is arity:**

    Phi(O, D) = A({ phi(O, t) : t in D^k })      for fixed k

Monotonicity survives untouched, since `D subset D'` implies `D^k subset D'^k`. Measured at k = 2
over a threshold-crossing chain: aliasing (exists over D^2) 0,1,1,1 EXISTENTIAL; consistency
(forall over D^2) 1,0,0,0 UNIVERSAL; min pairwise distance 10,5,1 UNIVERSAL.

**v16 therefore stands, over a wider normal form than it was stated for, and is now tested rather
than assumed.**

**Two preconditions, previously unstated:**

- **(P1)** `phi` must not read the domain, in particular not |D|. A predicate that does is
  normalised and lands in AGGREGATE — cycle 031's rate defect at arity 2. Measured: "at least
  half of D is even" reads 1,1,0,1.
- **(P2)** The value must be meaningfully ordered. `probe_monotonicity` classified an ARGMIN as
  UNIVERSAL purely on Python's lexicographic tuple ordering — meaningless and confidently
  delivered. It now refuses non-numeric values; booleanised, the same claim reads EXISTENTIAL.

**Methodological finding, three instances (HITL #129).** Every instrument built this month shipped
with the exact defect it was built to detect — the constancy probe read an all-raising space as
constancy (029), the convergence claim rested on an unfalsifiable chain (032), the monotonicity
classifier ordered unordered values (033). All three were found by ACCIDENT. Candidate discipline:
before trusting an instrument, construct the input on which it must report the answer you do not
want, and check that it does.

**Kill-battery additions (executable):** arity-2 relational classification over a
threshold-crossing chain; |D|-reading predicate probe; non-numeric value refusal; value-sequence
variation check before reading a classification.

## Cycle 034 — preprocessing attribution: R0's congruence is borrowed, R1/R2's is not

**HITL #124 asked whether the ladder's bottom rungs measure a normaliser rather than reasoning.
Answer: R0 does, R1 and R2 do not.**

**First, the question had to be corrected.** HITL #129's discipline was applied to the
raw-syntax control before using it, and the control failed 6 of 6: `ast.parse` merges
parentheses, whitespace, comments, numeric literal spelling, radix and string quoting.
**There is no raw — every keyer is a preprocessing map.** So "what fraction of the invariance is
the circuit's" is unanswerable as posed, and the correct output is an ATTRIBUTION ACROSS LAYERS.

**The ladder and the attribution** (15-pair battery):

    L0  source text    no normalisation — the only true floor
    L1  python-ast     lexical                       4 invariances
    L2  sympy-srepr    algebraic                     7 invariances
    L3  circuit key    variable renaming             3 invariances
                       nothing erases                1 (x*(y+1) vs x*y+x)

**Per rung:**

- **R0 contributes ZERO.** `ast_key` IS `sympy.srepr`; the projection is exactly L2. Trained on
  `x+y` it retrieves `y+x` and abstains on `a+b`. Canon R0 is exact recall that ABSTAINS on
  isomorphs; with sympy's key it retrieves algebraic isomorphs, so it sits slightly ABOVE its
  rung on borrowed strength.
- **R0's kill test still stands.** Renaming is the one isomorphism sympy does not collapse, and
  renaming is exactly what the fresh-seed test uses. The DOCSTRING is what is wrong — "identity
  congruence" should read "sympy normal form". Not edited, per the standing instruction.
- **R1 and R2 contribute genuinely.** `2*x+4` and `3*x+6` have different sympy keys and the same
  R1 answer; scaling a rational leaves its root fixed and sympy does not know that.

**A prediction of mine failed and is recorded:** I expected `x+y` vs `x+z` never to merge. They
merge at L3, correctly — they are alpha-equivalent, so a renaming quotient should identify them.

**Kill-battery additions (executable):** layered invariance attribution; control-normalisation
self-test applied before any comparison; per-rung "does this circuit add any congruence above the
CAS?" probe.

## Cycle 035 — claim v16 keeps its cells and loses its premise; stage taxonomy derived

**v16 REVISED.** The four monotonicity classes stand. **The aggregation normal form is dropped** —
the classification needs only the extension relation, `D subset D'`, and the two booleans
"can the value move up / down". Cycle 033's arity repair is superseded: it defended a premise the
result never required.

Demonstrated on the case that breaks every normal form — induced-subgraph connectivity has no
fixed-arity aggregation form and classifies cleanly: UP on chain (0,2)->(0,1,2), DOWN on
(0)->(0,1)->(0,1,2)->(0,1,2,4), therefore AGGREGATE.

**Precondition (P1) RETIRED.** "phi must not read |D|" is a syntactic proxy and is false in both
directions: `sum 1 / |D|` reads |D| and is INVARIANT; `|D| - count_P(D)` reads |D| and is
EXISTENTIAL. Replacement shape (not yet built): a restricted aggregation DSL with certified
monotonicity signatures propagated compositionally, reporting PROVED / COUNTEREXAMPLE / UNSETTLED
and never turning failure-to-prove into non-monotonicity.

## Cycle 035 — claim v17: stage type is (partition motion, content transformation)

**Four motions, not three:** `Q<P` COARSENING, `Q>P` REFINEMENT, `Q=P` PRESERVING, `Q||P`
INCOMPARABLE. The fourth is real on live data — R10's assumption_status and conclusion_status
partitions over the battery are [6,8] and [5,9] and neither refines the other.

**Two coordinates, not one label.** Identity, reorder, redact and hash all read PRESERVING;
partition theory cannot separate them, which is cycle 025's blind spot located rather than
rediscovered. Correction to cycle 026: pure reordering is bijective and PRESERVING; truncation
coarsens.

**THE DERIVATION.** A DETERMINISTIC stage that is a pure function of its predecessor's output can
only COARSEN or PRESERVE — instances agreeing on the predecessor agree here, so the new partition
is a union of old blocks. **Refinement and incomparability are impossible, not unlikely.** Hence a
stage measuring REFINEMENT has PROVED it read beyond its predecessor, which explains the cycle
024 / 027 split rather than recording it: the transform pipeline saw only the previous output,
the battery reads the original candidate at every check.

**Precondition found by pointing the discipline at the derivation:** determinism. An `f` returning
`random()` measures REFINEMENT and is not a counterexample — it is not a function of its input,
it reads the generator state, which is information beyond the predecessor.

**Kill-battery additions (executable):** four-way partition-motion classification; two-coordinate
stage descriptor; function-of-predecessor derivation check; determinism precondition probe.

## Cycle 036 — claim v18: no instrument is admissible until it kills a constructed anti-case

**The habit becomes a mechanism.** Four cycles running, an instrument shipped blind in the
direction it was pointed (029 constancy probe, 032 unfalsifiable chain, 033 unordered-value
classifier, 034 the "raw" control), three found by accident. `prometheus_math.instrument_contract`
requires four fixtures and refuses submission without them:

    POSITIVE     must trigger the claimed signal
    NEGATIVE     the answer-you-do-not-want case — must refuse, report zero, or flip class
    INVALID      out-of-domain — NEITHER class, only an error or explicit UNSETTLED
    SENSITIVITY  a pair differing ONLY in the measured property, with M(x) != M(x')

The sensitivity witness is the measurement analogue of an aliasing witness: without one the
instrument has never shown it responds to its advertised target rather than to something merely
correlated with it on the cases tried.

**All four historical failures map to a slot**, checked in the suite: 029 -> INVALID,
032 -> NEGATIVE (absent), 033 -> INVALID, 034 -> NEGATIVE.

**The contract's own anti-case passes.** An instrument memorising the four fixtures and blind
elsewhere certifies cleanly — demonstrated, not conceded. Necessary and NOT sufficient: canon R0's
lookup-table trap one level up. Defence: fixture FACTORIES plus `draws > 1`. A clean report on
frozen fixtures means only that those inputs were handled.

**Honest status: convention, not enforcement.** Nothing forces a new module to register. Real
enforcement is a CI gate over measurement modules (HITL #147).

## Cycle 036 — attribution doctrine (HITL #136 closed)

**BOUNDARY attribution** works where components have explicit interfaces: intervene at each
boundary, measure marginal contribution. **CAUSAL contribution** under entanglement is
counterfactual and often not uniquely defined — synergistic components each contribute 0 alone
and 1 together, with no canonical owner.

    Report DEPENDENCE, not ownership: "this invariance disappears when C is removed."
    Never "C contributed 37%" unless a convention (e.g. Shapley) is explicitly named as one.

**Doctrine, general across tokenisers, parsers, canonicalisers, embeddings and theorem
preprocessors:** *never credit downstream machinery for invariance already present at its input.*

## Cycle 036 — R0 reclassified (HITL #135 answered)

R0 is **vacuous as a reasoning circuit** — `Pi_R0 = Pi_sympy`, zero endogenous invariance, a memo
table over the substrate's canonical form. It is worth keeping as a **calibrated floor** under a
renamed capability, "retrieval under inherited canonicalization", with a two-column battery:
BORROWED invariance must survive, UNEARNED invariance must fail. Not edited; the change is
James's to make.

**Kill-battery additions (executable):** four-fixture instrument certification; fixture-factory
redraw against memorisation; retroactive mapping of historical instrument failures to contract
slots.

## Cycle 037 — the contract retrofitted: 12 instruments, 3 refusals, 2 real defects

**Claim v18 (no instrument admissible without a killed anti-case) applied to the whole arsenal.**
Twelve instruments, generative fixtures, `draws = 4`. Three refused on the first pass.

**Two were real defects in shipped, trusted code.** `find_aliasing_witness` and `fiber_search`
returned `None` both for "searched and found nothing" and for "there was nothing to search" —
no-signal conflated with out-of-domain. **Identical to the defect cycle 029 fixed in
`structural_constancy` and never propagated.** Both now raise `OutOfDomain`.

**One was a reach limit:** `structural_constancy` reads its target's source, so it degrades to
UNSETTLED wherever source is unavailable. Honest, and previously unstated.

## Cycle 037 — claim v19: sensitivity is testable only for SHARP targets

**Round 10's diffuse-target question, answered negatively and measured.** `brier_score` certified
SENSITIVITY on a pair that does not isolate its target: decomposed, the pair moves reliability
(0.0000 -> 0.0100) AND resolution (0.0000 -> 0.2500). Holding calibration alone is impossible for
an aggregate score, so the witness changes two things and the contract accepts it.

> A SENSITIVITY pass on a diffuse target means only "these inputs differ somehow", not "this
> instrument responds to its advertised target".

**Repair, already made in the literature:** decompose the diffuse target into components that
each admit an isolating pair, then certify the components. `murphy_reliability` holds resolution
fixed at 0.0000 while moving reliability 0.4225 -> 0.0000 — genuine isolation, which is what
Murphy's 1973 partition is FOR. **The decomposition is a PRECONDITION of certification, not an
optional refinement**, and this is now stated rather than silently assumed.

**Open (HITL #154):** dependence does not compose. If A depends on C and B depends on C, nothing
says what happens to A+B without C — the joint removal is a separate experiment and there are
2^k of them. Shapley composes and is a convention. No middle found.

**Kill-battery additions (executable):** twelve-instrument certification registry;
out-of-domain-versus-no-signal regression tests; isolating-pair check for a sensitivity witness.

## Cycle 038 — claim v20: author-written anti-cases are systematically too easy (n=1 of 9)

**Cycle 037's nine first-time passes had two readings — "the arsenal was sound" or "my anti-cases
were too easy" — and I could not separate them because I wrote both sides.**

**Method.** State an INVARIANT following from what the instrument ADVERTISES, then property-search
the input domain for a violation. Invariant from the claim, input from the domain, neither from
intuition about hard cases.

**Result: two violations, different in kind.**

1. **A real defect.** `refinement_multiplicity` returned 0 for a projection COARSER than the truth
   — outside its advertised range of >= 1, reading as "perfectly efficient" when the projection is
   losing information. My hand-written fixture only ever supplied REFINING projections. Now
   raises.
2. **My invariant, not the instrument.** `brier_score` "failed" on ([1e-09],[0]) because I
   compared a mean-of-squares against an unsquared tolerance. Units error in the invariant.

**Of two violations, one was the instrument and one was me.** After both repairs, 10/10 survive at
max_examples 300 — evidence, not proof, since a bounded search establishes nothing about inputs it
did not draw.

**The bug class is now at four instances** (structural_constancy 029, find_aliasing_witness 037,
fiber_search 037, refinement_multiplicity 038): a measure answering on input outside its own
domain. Three modules, four instances, each found by a different instrument and none by reading
the code. **Proposed defence stronger than a registry: a mandatory three-valued return type
(SIGNAL / NO-SIGNAL / OUT-OF-DOMAIN) making the conflation unrepresentable.**

**Residual hole, stated:** I still write the invariants. A mis-stated one fired loudly this time;
it could equally produce a false clean, and nothing catches that. Closing it needs a second author,
metamorphic relations from the type signature, or differential testing against an independent
implementation.

**Partial answer to the diffuse-target question:** a target defined as an OPTIMUM OVER A FAMILY has
no additive decomposition, so the contract's sensitivity slot is unenforceable there. Murphy works
because Brier is algebraically a sum of three terms; nothing guarantees that shape in general.

**Kill-battery additions (executable):** invariant-driven domain search; generator POSITIVE
control (a planted broken instrument it must find); raising-invariant-as-violation guard.

## Cycle 039 — claim v21: the answering-outside-your-domain class, at seven, now unrepresentable

**Predicted a fifth instance; found three.** The class stands at SEVEN across FOUR modules:
structural_constancy (029), find_aliasing_witness (037), fiber_search (037),
refinement_multiplicity (038), murphy.skill (039), verify_factorization (039),
uniform_adversary.schema_survived (039). Every one found by a different instrument; none by
reading the code.

**Two are notable beyond the count.** `murphy.skill` returned 0.0 on a degenerate battery AND ITS
OWN TEST ASSERTED THAT — the bug defended by its guard. `uniform_adversary.schema_survived`
reported a never-run schema as surviving, in the module whose docstring warns against exactly that
inference.

**The type (`prometheus_math.measurement`).** SIGNAL / NO_SIGNAL / OUT_OF_DOMAIN. Three
guarantees, each traced to a past bug: `.value` raises on OUT_OF_DOMAIN; `__bool__` raises always,
on every boolean route; OUT_OF_DOMAIN without a reason refuses construction. `value_or(default)`
keeps explicit opt-in available.

**Buys:** the conflation is INEXPRESSIBLE — the two meanings live in different constructors and
the third refuses to be read as a value.
**Does not buy:** correctness. A measure can still return SIGNAL where OUT_OF_DOMAIN was right.
`mistyped_domain_is_still_possible()` builds that measure and returns True — tested, not conceded.
The type converts a silent-by-default failure into one requiring an explicit wrong decision.

**Registry (HITL #151) superseded FOR THIS CLASS ONLY.** The type prevents where a registry would
only remind. But cycle 038's mis-stated invariant is not type-shaped, so the registry question
remains open in general.

**Scope, stated:** the seven sites refuse by raising, not by returning `Measurement`. `measured()`
adapts without breaking signatures; the migration has NOT been done.

**Kill-battery additions (executable):** every-boolean-route leak test for a result type;
mistyped-domain anti-case; the seven-site refusal tally as one executable test.

## Cycle 040 — claim v22: the class is a HABIT, measured. Ten of forty.

**Claim.** The answering-outside-your-domain class stands at TEN instances among FORTY
measure-like functions in my modules — **25%**. Measured, not estimated.

**How the denominator was got, since a curated one would be worthless.** MECHANICAL criterion:
a function is measure-like iff it takes at least one argument and reduces to a scalar verdict
(bool / int / float / str / Optional thereof). Applied uniformly across eleven modules; disagree
with it in one place rather than per function. Forty qualified. Each was called with a degenerate
argument and a minimal legitimate one, and classified by comparing the two answers.

    REFUSES        26
    DISTINGUISHES   2
    CONFLATES       6   -> 3 real instances, 3 artefacts of crude generic argument construction
    UNPROBED        6   -> reported, never dropped

**Instances 8, 9, 10.** `is_refinement_chain([]) -> True`; `chain_direction([]) -> DESTROYING`
(downstream of 8, **inherited the defect verbatim**); `find_splitting_witness -> None` on fewer
than two instances. All three now raise.

**The finding inside the finding.** Instance 10 is the DUAL of `find_aliasing_witness`, which
cycle 037 repaired — same conflation, one file away, left untouched by the very cycle that was
fixing it. The class does not just recur; it recurs across pairs I have already touched.

**Consequence — HITL #167 flipped.** Last cycle I called the `Measurement` migration optional
because the type existed. A 25% as-written rate says otherwise: offering a type is not using it.
The migration is now load-bearing rather than available.

**What the number does NOT say, stated so it cannot be quoted without it:**
- 26 REFUSES includes ten reactive repairs from cycles 029-040. As-stands != as-written.
- No external baseline exists. "Habit" presumes 25% is above some normal rate I have never
  measured on code I did not write. The defensible claim is "10/40 here, unknown elsewhere".
- Ten sites may be fewer than ten roots: instance 9 is a wrapper that copied instance 8. Counting
  per root rather than per site could move this back toward a tail.

**Method result worth more than the count: reading scored ZERO for TEN.** Every instance surfaced
from an instrument pointed at something else. Confounded, though — I never read with this bug as
the question.

**Kill-battery additions (executable):** enumerator self-test on three planted measures
(conflater / refuser / distinguisher) before trusting any count from it; UNPROBED-is-counted
assertion; the ten-of-forty tally as one test.

## Cycle 041 — claim v23: v22 NARROWED. Priced, re-counted, and the regime changed.

**v22 said "the class is a HABIT, 10/40, 25%". Three parts of that are now withdrawn or
narrowed, none of them by me.**

**1. "Habit" is withdrawn (round-11 review).** There is no external corpus of comparable
functions — scalar-reducing measures that conflate degenerate input with a legitimate verdict —
so there was no baseline for 25% to be high against. Standing claim:
**11/40 in this corpus; external prevalence unknown.** The class is a LOCALLY RECURRENT DEFECT
CLASS, not a statistical claim about authorship. The migration case never rested on the
comparison: it rests on local expected loss, and eleven observed escapes are enough.

**2. One rate becomes three numbers (round-11 review).**

    ROOTS               10      independent originating defects — propensity to CREATE
    EXPOSED SITES       11      interfaces contaminated — how much of the system lies
    PROPAGATION FACTOR  1.10    sites / roots

The factor is the informative one. Near 1 means repeated CREATION; a factor of five would have
meant two roots leaking through ten wrappers and a diagnosis of failure to CONTAIN across seams,
which needs a different fix. Only `chain_direction` is inherited. **The idiom clustering therefore
describes HOW the error is made and does not reduce HOW OFTEN — v22's "the recount relocates the
claim" overstated it.**

**3. "Reading scored zero for ten" is narrowed.** Measured: `P(found | INCIDENTAL reading) = 0/11`.
Never measured: `P(found | TARGETED review with the bug as the question)`. Only
"incidental review has shown no sensitivity" is supported. Lane A/B pre-registered.

**NEW — the migration is priced.** Converting `refinement_multiplicity` (96 of 108 production
refusals, so the slice was chosen by liveness rather than taste) cost **13 edits: 11 tests + 2
production call sites**, all made. Gradual migration is now a costed decision rather than a
preference.

**NEW — instance 11, predicted.** Idiom-presence flagged four unaudited functions; all four were
checked BY CALLING them; `verify_family_incapacity` answered `all_members_err=True` on an empty
family, inside the module arguing that absence of a counterexample proves nothing. One in four.

**NEW — a confound in the flattering direction, caught.** Migrating a measure changed its return
annotation and removed it from the audit's denominator. The rate would have improved because the
population shrank.

**REGIME CHANGE (round-11 review, accepted).** Cycles 037-041 fail the gate "each ~5 cycles must
find a real-substrate defect, improve a live experiment, or validate/falsify a capability on real
data". Everything found was in code written for the loop. Cycles 042-046: **~80% real-substrate /
20% instrument repair**, beginning with HITL #78 measured for blast radius rather than restated.

**Kill-battery additions (executable):** probe-off/probe-on control on identical scope before any
claim of non-invasiveness; planted-idiom anti-cases before trusting a classifier count;
as-written source pulled from before the repair commit when the question is about mistakes;
`provenance()` reporting roots/sites/propagation rather than a single rate.

## Cycle 042 — claim v24: HITL #78 has a ROOT CAUSE and a MEASURED blast radius on live data

**First claim in this ledger about the running system rather than about the loop's own code.**

**Root cause.** `load_prepass` filters `int(d.get("rep", -1)) != 1`; live rows carry
`key: [rep, uid]` and have no flat `rep`/`uid`. Default `-1` fails on all 962 rows. `best()` in
the same package reads `tuple(r["key"])` and is correct. **Two readers of one file, disagreeing
about its schema, for sixteen cycles.** Data intact: 625 rep-1 / 337 rep-2.

**Method.** Predictions PRE-REGISTERED and committed (`0fd3273b`) before measurement, with the
NULL outcome specified in advance and prior knowledge disclosed rather than pretended away.

    Y4 consumer reach    predicted >=1 of 6    measured 1 of 6 (campaign.py:312)
    Y1 selection volume  predicted 0 vs >0     measured 0 vs 1 per uid
    Y2 packet tokens     predicted delta > 0   measured 58 vs 678-2662, mean ~2,070 tokens/task
    Y3 tau coverage      predicted {} vs non   measured {} vs {'p1_prepass': 624}

All four held. Five of six call sites read a different ledger where the two loaders AGREE exactly
(200 = 200) — that is legitimate filtering, and checking it was what kept this from being an
escalation about a file nothing reads.

**The finding inside the finding.** The empty pool emits *"no residue exists at this distance for
this task"* and *"NOT-RUN-FOR-LACK-OF-RESIDUE"*. **The sparsity report — the component whose whole
purpose is honest accounting of what the substrate did not record — asserts a loader schema
mismatch as an absence of data.** The answering-outside-your-domain class at PIPELINE SCALE in
PRODUCTION. Cycles 029-041 found eleven instances in code written for the loop; this is the first
found outside it, and it is the strongest evidence to date that the class generalises beyond me.

**Live impact, caught pre-emptively.** `Arms.pool` feeds `F-prom-retrieved` and `F-null`. With
`pool=[]` the residue arm ships boilerplate saying there is no residue — a null contrast presented
as a treatment. The campaign is live but the append-only phase log shows only P1; P3 constructs
`Arms`. No results contaminated.

**Not acted on.** Ergon is not mine. Finding made actionable without a diff; mechanism pinned in
7 tests that should go RED when the seam is repaired.

**Corrections folded in (round 12):** `C_site=1 = 13 edits` is one observation, not a per-function
migration cost — better unit is edits per production call edge (13/2 = 6.5), and a distribution
needs 3-5 sites. Prevalence (11/40, dead code INCLUDED) and live exposure are two populations, not
a denominator choice.

**Kill-battery additions (executable):** resolve consumer paths before escalating a loader defect;
diff a total-drop loader against the other reader of the same file before suspecting the data;
"not retrieved" and "does not exist" must be different strings; prefer a present append-only
record over an inference from absent files.

## Cycle 042 — claim v24 CORRECTED, same cycle

**Y₄ was published as "1 of 6". It is 1 of 8.** A repo-wide scan found two consumers a
directory-scoped grep (`ergon techne engine`) had missed: `charon/probe/run_r7_d1d2_build2.py` and
`harmonia/probe/c_static_leakage_probe.py`. Choosing the search window chose the answer.

Direction of the pre-registered prediction (≥1) still holds; both missed consumers read a third
ledger, `probe_prepass.jsonl` — raw=252, shipped=126, drop 50%, flat `rep` fields, zero rows with
`key` — and are unaffected.

**The correction strengthens the claim rather than weakening it.** Three ledgers, one loader:

    probe_prepass.jsonl              flat rep          loads correctly (50% = rep-2 filter)
    nearmiss_mix-M30_prepass.jsonl   flat rep          loads correctly (50% = rep-2 filter)
    p1_prepass.jsonl                 key:[rep,uid]     100% DROP

Two of three producers emit the expected schema. **The campaign writer is the outlier, so the fix
belongs on the WRITER side**, aligning it with two already-correct producers. A two-file
measurement could not distinguish reader-wrong from writer-wrong; a three-file one can. The
published version named the seam but not which side of it to repair.

**Kill-battery addition (executable):** a loader-defect claim must enumerate consumers REPO-WIDE,
and must measure at least one UNAFFECTED producer of the same loader before naming which side of a
seam is wrong.
