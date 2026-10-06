# Project Moonshot -- Requirements & Design (v0.3)

Seat: Themis (owner). Epic: EP-MOONSHOT. Supersedes v0.2 (in superseded/). Date: 2026-10-06.
Charter: roles/Themis/prompts/2026-10-05_charter/. Epic approval: roles/Themis/prompts/
2026-10-05_epic_approval_and_review/. Astra review + operator disposition (authority for v0.3):
roles/Themis/prompts/2026-10-06_astra_review/ and roles/Themis/design/
MOONSHOT_DESIGN_v0.2_ASTRA_REVIEW.md. Economics: versioned appendix beside this file. Running
synthesis: auto-memory project_moonshot_rso_lane.

Status: **REVISE BEFORE LAUNCHPAD; scientific status NOT_VERIFIED** (Astra). Keep the Epic, the
fixed-world CPU Launchpad and independent RSO authority. Do NOT freeze the scientific gates, and
do NOT run evolutionary science, until the contradictions below close and the native vertical
slice (S13) passes a fresh blinded qualification. The cluster/infrastructure experiments (M4)
and the contract closures start now.

> **Survival is the pressure. Sagacity is the measurement.**
> **Reachability is the prerequisite. The ruler is the adversary.**

**Amendment OP-LC1 (2026-10-06; roles/Themis/prompts/2026-10-06_op_lc1/).** Two contract changes to
R-EP/N1/N4, executable in moonshot/epoch/CONTRACT.md, which governs where this text differs: (1) the git
commit SHA is TRANSPORT identity; semantic identity is a transport-independent SHA-256 over canonical
epoch inputs/spec/runtime and canonical outputs, and git refs/commits only locate those bytes; (2) a
successful CAS is PUBLISHED, not "accepted" -- a push grants no scientific authority, validation/
acceptance is a separate state, DUPLICATE / DISAGREEMENT-QUARANTINE / AMBIGUOUS stay explicit,
contested chains fail closed, and a disagreement found after descendants exist taints that branch
until deterministic replay resolves it. Read "one accepted successor" below as "one PUBLISHED
successor". Lane C runs as campaign C-008.

## 0. What changed from v0.2 (Astra review F01-F10, all accepted)

Astra (Enceladus) reviewed v0.2 and returned ten findings (three BLOCKING, seven HIGH) plus
smaller corrections; the operator accepted all with rulings; Themis holds incorporation and
accepts all. The reviewed artifact is preserved beside this file. Changes:

- **F01 (BLOCKING) -> H1 narrowed (S2, S9).** The v0.2 claim "the RSO must reject
  internally-consistent fabrications" is REJECTED: a pre-registration fabrication whose evidence
  bytes equal an authentic run's is information-theoretically indistinguishable to that
  consumer. The correct behavior is to preserve an **EXECUTION_NOT_AUTHENTICATED** ceiling, not
  to "detect the lie." H1 gets an attack matrix (attack class -> accessible evidence -> expected
  typed decision -> claim ceiling). Testing that the RSO *knows what it does not know* is the
  adversarial Phase-3 test.
- **F02 (BLOCKING) -> R6 corrected.** Three distinct operations: channel-cut and
  information-destroying state resample (both causal interventions that SHOULD drop a genuine
  memory user) and a separate **information-preserving sham** that matches the procedure without
  removing the information (must NOT drop). Signal = drop under the destructive interventions AND
  no drop under the preserving sham. Intervention-validity failure is reported separately from
  absence of memory.
- **F03 (BLOCKING) -> explicit Moonshot->RSO claim map (R-CLAIMMAP, S9).** A deterministic
  integer organism is not a slice-001 case just because it uses integers; slice-001 is a finite
  reset-retention world, Moonshot is within-life delayed-cue survival with evolution and
  sampling. A versioned native-claim->predicate map is agreed with Palamedes before adapter work;
  a new native predicate/contract is a legitimate Phase-3 output; native physics is not distorted
  to fit W-S1.
- **F04 (HIGH) -> null information boundary + counterfactual schedule (R6, R-NULL).** The
  reactive-null family needs a policy class and information boundary (exact bound where
  tractable; best-found otherwise, labelled as such); environmental memory carriers
  (location, charge, pending actions, other organisms, world marks) are audited, not just a
  neural register. Paired interventions hold initial state + exogenous opportunities/randomness
  fixed, NOT factual actions/births/deaths; use event-keyed exogenous draws so a counterfactual
  death removes its downstream reproduction while exogenous arrivals stay matched.
- **F05 (HIGH) -> reachability != power (R-RC, R10).** RC0/RC1/RC2 kept and valuable, but NOT
  sufficient for KILL. A scientific KILL needs the relevant reachability level AND a
  preregistered statistical rejection/equivalence rule over a frozen claim tuple. No finite null
  kills the unbounded existential H2; only a precise operational claim can be killed.
- **F06 (HIGH) -> H3 (S2).** HYB-vs-SYM advantage is a THIRD claim, distinct from H1 and H2, and
  a HYB win does not show the neural primitive carries the information (search-space geometry can
  change discovery rates). Add a post-search, cost-matched primitive-disable/substitution
  contrast against a strong symbolic-memory positive; keep it out of reproductive fitness.
- **F07 (HIGH) -> constitutional selection air-gap (R4).** Offline scoring is not by itself an
  air-gap (score-dependent promotion selects descendants by the metric). Rule: during one
  preregistered campaign, neither S-meter nor RSO outputs may alter reproductive ancestry,
  continuation budget, mutation policy, world parameters, or candidate allocation; the campaign
  runs to its preregistered stop independent of the ruler; afterward the ruler may report,
  select FROZEN organisms for confirmation, or motivate a NEW preregistered campaign. Test:
  permuting all S-meter scores during a campaign must not change reproductive ancestry.
- **F08 (HIGH) -> epoch commit semantics + bounded re-scoring (R-EP, N5).** Semantic epoch
  identity = input-checkpoint hash + epoch-spec hash + runtime version; one accepted successor
  via explicit compare-and-swap; duplicate equal attempts idempotent, disagreeing outputs
  quarantined, stale workers cannot advance the chain; retry costs charged. N5 bounded:
  re-scoring only within a declared versioned evidence schema; missing fields/arms =>
  NOT_EVALUABLE; a new counterfactual is a new charged run, not "re-scoring."
- **F09 (HIGH) -> wforge unpaid-write defect = STOP CONDITION for survival science (S8, S13).**
  Reproduced: an unaffordable action forced to abstain still queues writes (probe: charge 1,
  cost 3, charged 0, actions_used 0, register delta 251 vs a zero-action twin). Per Astra, Themis
  does NOT patch the dependency: Themis writes the red affordability regression and hands it to
  the substrate owner (Daedalus) to fix; this blocks survival-based search but NOT M4 or ruler
  development.
- **F10 (HIGH) -> fresh blinded qualification (R-QUAL).** Opaque IDs are necessary, not
  sufficient; repeatedly greening the same hidden controls overfits their generators. Separate
  public development fixtures from a freshly-generated qualification challenge issued AFTER
  scorer freeze, with exposure accounting; a revealed failed qualification stays in the record.
- **Typed outcome/execution vocabulary (S4a):** scientific outcomes stay PASS / KILL /
  UNDERPOWERED; execution/authority get separate typed states BLOCKED / INVALID / NOT_EVALUABLE /
  UNQUALIFIED, aligned to the RSO's three-field verdict (execution / authority / outcome). A
  runtime defect is INVALID/BLOCKED, not UNDERPOWERED; an unqualified predicate is UNQUALIFIED,
  not KILL; missing intervention data is NOT_EVALUABLE, not a negative.
- **Smaller corrections (review s2):** S-scale animal analogies are illustrative, not calibrated,
  and floor sagacity != world model / counterfactual reasoning / general intelligence; "LLMs
  cannot discover" and "built so it cannot fool its author" are downgraded from impossibility
  claims to a design preference + an adversarial-testing obligation; GPU scoped to later admitted
  acceleration with integer-equality semantics specified (accumulation order, overflow,
  saturation, rounding, activation); DB-free != available (git-remote-outage behavior stated; a
  completion push does not confer consumer/promotion authority; auto-join must not
  auto-authorize code); linear scaling is an M4 hypothesis, not a property.

## 1. Executive summary

Moonshot is prong 3 of the program: the hybrid neuro-symbolic engine, run as **an adversarial
external customer for Phase 3** and a **commodity-scale sagacity search**. It now carries THREE
independent claims (S2): H1 (can the RSO correctly *type* evidence and its epistemic limits?),
H2 (can survival-only evolution grow retained-information-dependent survival?), H3 (does the
integer neural primitive improve discovery under fair resource accounting, and is it causally
used?). Any can resolve while the others do not -- which is the point.

The method is a funnel (generate wide on e-waste CPUs; sift with falsification; promote to GPU
then cloud only on earned, preregistered evidence) around four commitments: survival is the
only selection pressure (constitutionally air-gapped from the measurement, R4); sagacity is
scored offline; a null is a kill only once reachability AND a preregistered rejection rule are
met; and the ruler is attacked as an adversary, not trusted as a dashboard. Astra's review found
-- before any campaign -- an RSO epistemic boundary, a causal-inference error in the ruler, a
Phase-3 domain mismatch, a power/reachability conflation, a hidden third hypothesis, an
over-broad air-gap claim, a commit-semantics gap, a re-scoring overclaim, and a real
world-runtime bug. That is instrument-first working as intended.

## 2. The three hypotheses

**H1 -- Observatory.** Can Phase 3 correctly *type* an unfamiliar external producer's evidence
and its epistemic limits -- recognizing detectable violations and underpowered data, and
preserving an execution-authenticity ceiling where the evidence cannot distinguish an authentic
run from a consistent fabrication -- *without relaxing its ruler to flatter the producer*? H1 is
tested by a hostile integration with an expected-decision matrix:

| Attack class | Accessible evidence | Expected typed decision | Claim ceiling |
|---|---|---|---|
| Honest negative | complete | outcome=KILL (correct) | full |
| Underpowered | thin | outcome=UNDERPOWERED | reported as such |
| Post-anchor alteration | tamper-visible | execution=INVALID, refuse | none |
| Detectable contract violation | present | authority=UNQUALIFIED / refuse | none |
| Internally-consistent pre-reg fabrication | bytes = authentic | authority preserves EXECUTION_NOT_AUTHENTICATED ceiling | never "authenticated execution" |

Preserving that last ceiling is a PASS for H1, not a failure -- we are testing whether the RSO
knows what it cannot know. A stronger detection claim would require a distinct, qualified
instrument with a registered threat model and an independent execution check.

**H2 -- Evolution.** Can survival-only evolution in a fixed, then progressively richer,
deterministic world produce an organism whose survival depends on retained hidden information,
a dependence that survives the reactive-null family and the causal interventions (R6)? H2 is an
unbounded existential across worlds; only a precise operational instance is ever KILLable.

**H3 -- Fusion.** Does offering the integer neural primitive improve discovery under the
specified resource accounting (H3a: a named endpoint -- rate-at-fixed-budget or
time-to-first-qualified-crossing), AND is the primitive actually causally used (H3b: a
post-search, cost-matched primitive-disable/substitution contrast against a strong symbolic
positive)? H3a can PASS while H3b fails -- in which case we learned about search-space geometry,
not neural cognition.

Clean independence: H1 PASS with H2 KILL; H2 PASS with H3 KILL; H3a PASS with H3b fail. **None
rolls into a single Moonshot verdict.**

## 3. Premise

Evolution produced one cognitive architecture; the bet is it is one point in a space. Isolate
primitives, build worlds where sagacity is the only way to survive, and a different architecture
could crystallize. (Design preference, not an impossibility claim: LLMs are pulled toward the
human corpus, which is a reason to *grow* rather than *retrieve* -- and an obligation to test the
claim, not assert it. The premise is a restatement of the Avida/ALife + AI-GA program, S10, not
new.)

## 4. The spine; and 4a. the typed vocabulary

Spine: pressure = survival (R4); measurement = sagacity, offline (R5-R6); reachability =
prerequisite (R-RC); ruler = adversary (R11, H1). Floor only, because calibration needs known
positives and those exist only at the bottom.

**4a. Verdicts are typed on two axes** (aligned to the RSO's execution/authority/outcome
three-field verdict):
- **Scientific outcome:** PASS | KILL | UNDERPOWERED.
- **Execution/authority state:** BLOCKED (could not run / dependency unsafe) | INVALID (runtime
  or intervention-validity defect) | NOT_EVALUABLE (required evidence/arm absent) | UNQUALIFIED
  (no qualified predicate for this claim).
A result carries both. A wforge defect is INVALID/BLOCKED, never UNDERPOWERED; an unqualified
native predicate is UNQUALIFIED, never KILL; a scorer missing an intervention is NOT_EVALUABLE,
never a negative.

## 5. Requirements (revised per F01-F10)

R1. Organism = deterministic program over a fixed palette (optionally an integer neural module,
    R7), hashable, replayable, intervenable. Phenotype state, inherited genome and search
    history are kept distinct (F04).
R2. World = pure deterministic function of (grammar, seed, mutation-history), reproducing to
    canonical semantic identity (N1).
R3. Worlds support partial observability and irreversible state; enrichable by a seeded mutation
    grammar (deferred to M5; Launchpad world is fixed, S6.1).
R4. **(Constitutional air-gap)** Selection acts on survival/reproduction only. During one
    preregistered campaign, neither the S-meter nor RSO outputs may alter reproductive ancestry,
    continuation budget, mutation policy, world parameters, or candidate allocation; the campaign
    runs to its preregistered stop independent of the ruler. Afterward the ruler may report,
    select FROZEN organisms for confirmatory assays, or motivate a NEW preregistered campaign.
    Promotion/continuation/allocation decisions are archived as part of ancestry. ACCEPTANCE:
    permuting all offline scores during a campaign does not change reproductive ancestry.
R-AD. Viability = reproductive continuation / lineage persistence under resource turnover, not
    merely remaining alive (anti-degeneracy).
R5. Sagacity scored by a separate offline consumer reading only emitted logs; never in the
    selection loop.
R6. **(Null family + three interventions)** The verdict combines (a) a preregistered
    REACTIVE-NULL FAMILY with a stated policy class and information boundary -- at minimum
    constant/reflex, an optimal observation-only policy (exact bound where tractable, else a
    labelled best-found baseline), and an evolved memory-disabled population at equal budget; and
    (b) THREE causal operations on a paired counterfactual that holds initial state + exogenous
    opportunities/randomness fixed (event-keyed draws; a counterfactual death removes its
    downstream reproduction while exogenous arrivals stay matched): **channel-cut** and
    **information-destroying state resample** (both MUST drop a genuine memory user) and an
    **information-preserving sham** (MUST NOT drop). Signal = above the whole null family AND a
    drop under both destructive interventions AND no drop under the preserving sham.
    Intervention-validity failure (e.g. an invalid state encoding that crashes a reflex) is
    reported separately from absence of memory. Margins for intact-vs-null, intact-vs-destructive
    and intact-vs-sham are frozen before challenge. Environmental memory carriers (location,
    charge, pending, other organisms, world marks, adapter caches, observation buffers) are
    audited, not only a neural register.
R7. Neural primitives MAY be included; integer/quantized, reproducing to the canonical semantic
    oracle (N1, with accumulation/overflow/saturation/rounding/activation semantics specified),
    evolved by seeded mutation (no backprop). Fusion = neural-as-primitive first; neural-as-
    mutator is auxiliary and outside selection authority.
R8. Every experiment preregistered (claim tuple, arms, gates, margins, null family, required RC
    level, statistical rejection/equivalence rule, kill criteria) with a manifest, before data.
R-RC. **(Reachability, necessary not sufficient)** A claim names the reachability level it needs:
    RC0 expressible (a planted organism exhibits it); RC1 locally traversable (fitness-improving
    intermediaries exist -- necessary, not proof of enough paths); RC2 search-reachable (a
    preregistered search crosses at an estimated rate from randomized starts, with stated
    uncertainty, bound to the claim tuple). A scientific KILL requires the relevant RC level AND
    a preregistered statistical rejection rule; RC alone never kills. Discovery sampling unit =
    independent search populations, not descendants/ticks/episodes of one run. Discovery,
    calibration and confirmation seeds are distinct.
R10. Outcomes typed (S4a); PASS / KILL / UNDERPOWERED are scientific; BLOCKED / INVALID /
    NOT_EVALUABLE / UNQUALIFIED are execution/authority. A finite null gives at most a scoped
    operational KILL, never a global H2 KILL.
R11. Ruler calibrated against disguised known controls under operational blindness; see R-QUAL
    for the independence requirement.
R-QUAL. **(Fresh blinded qualification)** Public development fixtures are separate from a
    qualification challenge generated by an independent generator/keeper AFTER the scorer is
    frozen; the consumer gets only the fields it needs to verify evidence, no label-bearing
    metadata; exposure (who has seen which controls, unavoidable code exposure) is recorded; a
    revealed failed qualification stays in the record; a revised scorer needs a fresh challenge.
    ACCEPTANCE: renaming/permuting opaque IDs and irrelevant metadata leaves verdicts unchanged;
    classification is demonstrated on unseen variants with the full confusion table and scope.
R12. Diversity/health judged by mechanism; dead-world and random-population controls first-class.
R13. Promotion to paid compute requires a passed local gate + the required RC level + the
    preregistered rejection rule.
R-CLAIMMAP. **(Native claim -> RSO)** Before adapter work, agree a versioned map with Palamedes:
    Moonshot proposition -> native state/boundary -> interventions -> trace fields -> existing or
    new predicate -> calibration -> verdict/authority. A W-S1 pass supports only the W-S1 claim;
    native survival/origin claims need native-world calibration or a new predicate/contract. Do
    not impose an artificial reset and call it native physics.
R-EP. **(Epoch commit semantics)** Durable unit = immutable checkpoint + epoch spec -> trace +
    next checkpoint. Semantic identity = input-checkpoint hash + epoch-spec hash + runtime
    version; execution-attempt IDs/costs are separate. Output blobs durable before a verified
    completion manifest (binding input/spec/trace/output) is atomically exposed; one accepted
    successor via explicit CAS; duplicate equal attempts idempotent; disagreeing outputs
    quarantined; stale workers cannot advance the accepted chain; retry costs charged even when
    discarded. An ordinary epoch retry must never masquerade as an RSO content-reset intervention.
R-RUNTIME. **(Substrate readiness gate)** Native checkpoint/restore, reproduction policy, assay
    interventions, sufficient logs (R9) and consumer admission need conformance evidence before
    survival science; naming reuse is not completion. F09 is an explicit STOP CONDITION.
R9. Every run emits a complete structured log sufficient to compute R6 from logs alone; a digest
    identifies data, it does not contain the trace.

N1. Determinism = canonical SEMANTIC identity + a reference oracle; CPU integer reproduces it
    directly; any accelerated path demonstrates oracle-equality before admission, per stack
    version; integer-equality semantics (accumulation order, overflow, saturation, rounding,
    activation) are specified; host/perf metadata in a separate receipt.
N2. A Launchpad epoch runs as a lightweight process (<~1 GB RAM).
N3. No SPOF on the wide critical path: the wide search runs with no live dependency on the
    shared DB. **DB-free is not the same as available:** state git-remote-outage behavior; a
    worker gains no consumer/promotion authority merely by pushing a completion ref; auto-join
    must not auto-authorize arbitrary code.
N4. Fault tolerance via R-EP: node death requeues an epoch from its input checkpoint, exactly one
    accepted successor, no duplicate reproductive/promotion effect.
N5. **(Bounded re-scoring)** Logs durable, scorer versioned; re-scoring is supported only within
    a declared versioned evidence schema. Missing fields/arms => NOT_EVALUABLE. New counterfactual
    execution is a new charged derived run with frozen inputs and fresh provenance.
N6. No paid compute without a passed local gate + required RC + rejection rule; cloud spend
    bounded by a hard guardrail + preregistered estimate; cap fixed at launch (economics appendix).
N7. A new node joins with only Python, git and a push credential -- and that push grants no
    scientific authority (N3).

## 6. Architecture

6.0 Shard epoch (R-EP): immutable checkpoint + epoch spec -> trace + next checkpoint, one
accepted successor via CAS. Both a bag-of-tasks unit and the carrier of a resident population.
6.1 Launchpad is a FIXED-world assay: SYM and HYB see one identical preregistered world
distribution; world mutation / islands / Red Queen are M5, after the assay.
6.2 Organisms over a fixed palette (optional integer neural primitive); selection never wired to
a mechanism (R4).
6.3 Offline S-meter reads epoch logs + the paired-intervention logs + the null family, emits an
RSO-shaped producer receipt with no authority over its verdict (R5-R6), versioned (N5).
6.4 Funnel: RC0/expressibility + substrate readiness (R-RUNTIME) -> blinded qualified ruler
(R-QUAL) -> CPU sieve -> GPU confirm (oracle-equality) -> cloud scout (only after RC2 + gate).

## 7. Scaling

Work plane = workgraph git-CAS pull-queue (DB-free, fault-tolerant via R-EP), treated as an
EXPERIMENT (M4): instrument claim latency, push/ref contention, abandoned-epoch rate, ref growth,
useful-CPU/coordination-CPU ratio, with a preregistered reconsider-transport threshold; state
remote-outage behavior (N3). Promote/confirm = A2A over fabric (capability-routed, low volume).
Nervous system = pub/sub for liveness/auto-join/wakeups only. Hardware split by primitive cost at
epoch granularity; GPU epochs demonstrate oracle-equality first; GPU routing is scoped to later
admitted acceleration (Launchpad integer HYB is CPU-only). Linear scaling is an M4 hypothesis.
Two new builds: the ruler-calibration/qualification harness (R-QUAL) and node auto-join (N7, no
auto-authorization); plus the sharded claim namespace if the M4 threshold is hit.
Refused (determinism + cheap-headless + no-human-world-priors): real-time UDP/MMORPG servers and
graphics game engines.

## 8. Leverage from existing engines

Primary substrate = wforge + Proteus (deterministic floatless replay, world-mutation grammar,
partial-observability mutator; Proteus organism VM). **F09 stop condition:** wforge has a
reproduced unpaid-write defect; the substrate owner (Daedalus) repairs it against Themis's red
affordability regression before any survival search; naming reuse is not completion (R-RUNTIME).
BEE = later substrate-transplant test. Reused: SFE executor contract + ledger format; mhc
alpha-ledger; cartography falsification battery; harmonia nulls; apollo mutation; Aphrodite
dedup; rso/slice001 adapter; workgraph; Aether RunPod module.

## 9. Phase 3 overlap, the claim map, and hostile integration

The S-meter is RSO consumer machinery (producer has no authority over its verdict). **A native
Moonshot receipt does not acquire a slice-001 (W-S1) claim by renaming fields (F03):** before
adapter work, Themis and Palamedes agree the versioned claim map (R-CLAIMMAP); a new native
predicate/contract is a legitimate Phase-3 output, reached through the cell's versioned process;
Themis may propose but cannot silently relax the ruler. H1 hostile integration submits honest,
underpowered, tamper-visible, violation and consistent-fabrication producers and checks the RSO
types each per the S2 matrix, preserving the EXECUTION_NOT_AUTHENTICATED ceiling on the last.
Float/GPU is a later amendment, not the first integration gap.

## 10. Prior art

As v0.2 S10 (unchanged): Moonshot reuses OEE/QD/neuroevolution/ALife wholesale (POET/Enhanced
POET, PAIRED/UED, MCC, AI-GAs, Deep Neuroevolution/ES, Tierra/Avida, Hide-and-Seek, XLand as the
expensive opposite pole, World Models, empowerment/MODES, ELM/FunSearch, causal scrubbing/amnesic
probing). Candidate novelty is the narrow combination -- offline selection-air-gapped ablation
sagacity over deterministic replayable co-evolved worlds with selection-admitted integer neural
primitives on commodity hardware under preregistration + RC0/1/2 -- stated "to our knowledge not
previously combined," never "first." "Sagacity" positioned against empowerment/MODES/amnesic
probing, not asserted sui generis.

## 11. Boundaries and economics

As v0.2 (unchanged): local / on-prem GPU / RunPod / hyperscaler tiers; determinism makes spot
usable via R-EP replay; concrete pricing and scenarios in the versioned economics appendix, out
of the scientific contract.

## 12. Epic structure and the three parallel closure lanes

Threads (EP-MOONSHOT): M1 RSO hostile integration (H1) / M2 floor sagacity science (H2) / M3
reachability science (RC0-2 + rejection rule) / M4 commodity fabric; candidates M5 open-ended
ecology, M6 scale escalation. The operator's three parallel lanes, with the blocker typing Astra
and the operator drew (do not recreate gating bureaucracy):

- **Lane A -- contracts (Themis + Palamedes):** close F01-F08 and produce the v0.3 claim/authority
  map. F02/F03 are assay/admission blockers; F01 is an H1 claim-definition blocker (fixtures and
  machinery can proceed while its wording settles).
- **Lane B -- substrate (Daedalus + Themis's regression):** fix F09 (affordability regression +
  surrounding wforge tests). Blocks survival science only; not M4, not ruler development.
- **Lane C -- M4 cluster, starts now:** synthetic epochs across the Linux fleet -- duplicate
  execution, worker death, lease expiry, CAS collision, remote outage, idempotent replay,
  heterogeneous-host canonical traces. Needs no trustworthy evolutionary substrate.

**Dependency graph:**
```
  contracts (A) ───┐
  wforge repair(B) ─┼─→ native planted vertical slice (S13) ─→ fresh blinded qualification (R-QUAL)
  M4 cluster (C) ──┘                                        ─→ RC/science preregistration ─→ Launchpad evolution
```
M4 runs independently as far as synthetic epochs permit; scientific execution never depends on
distributed-system polish, and unqualified evidence never enters the science.

## 13. First build: the native planted vertical slice (NO evolution)

Before any evolutionary population: planted memory-user + planted reflex + information-preserving
sham + channel-cut + information-destroying resample -> native Moonshot evidence (fixed-world,
delayed-cue) -> independent RSO decision via the agreed claim map. Gates: R6 three-intervention
signal on the planted memory-user; the reflex and the preserving-sham-only cases do not register;
the dead-world control stays silent; the slice carries honest in-scope / out-of-scope / typed
receipts (S4a). Only after this passes a FRESH blinded qualification (R-QUAL) do RC work and the
Launchpad evolutionary population begin. The Launchpad H3a question (does the integer primitive
raise rate/time-to-crossing at matched budget) and H3b (is the primitive causally used) follow,
with the primitive-use contrast out of reproductive fitness (F06).

## 14. Why this is rigorous, not a toy

As v0.2 S14, with the F01/F05/F10 corrections: the author is held to green tests where
correctness is the goal (engine, calibration) and barred from greening the tests where honesty
is (science). The guards: preregistration (R8); an independent, offline, blinded, freshly-qualified
ruler (R5/R11/R-QUAL) attacked as an adversary (H1); the reactive-null family + three-operation
causal test (R6); reachability-AND-rejection-gated kills (R-RC/R10); canonical semantic
determinism (N1); mechanism over coverage (R12); anti-degeneracy (R-AD); the constitutional
air-gap (R4); typed outcomes (S4a). Stated as a design preference and a testing obligation, not
an impossibility guarantee: a sufficiently rigorous instrument is one that reports what it cannot
know (F01), not one that claims it cannot be fooled.

## 15. Ownership (unchanged)

Themis owns the Epic/integration/producer/experiments; the RSO cell (Palamedes) owns whether
evidence satisfies RSO contracts/predicates; Themis may propose amendments but cannot silently
relax the ruler; Daedalus owns the wforge repair (Themis supplies the regression). It is because
Themis cannot move the ruler that an H1 pass means something.

## 16. What is authorized now

Start Lane A (contracts/claim map), Lane B (hand Daedalus the F09 regression), and Lane C (M4
synthetic-epoch cluster experiments) immediately. Build the ruler-qualification harness and node
auto-join. Do NOT run evolutionary science; do NOT run the Launchpad population; no paid cloud.
The scout mechanism may be built but fires only after RC2 + the local gate + the rejection rule,
cap fixed at launch. Coordinate the claim map with Palamedes and the F09 repair with Daedalus
before building on their components.

## 17. Development methodology: test-driven, three layers

As v0.2 S18: (1) engine/code -- strict TDD, exact via determinism (incl. the R4 score-permutation
air-gap test, R-EP fault-injection/idempotence tests, N1 oracle-equality, the F09 red
affordability regression); (2) calibration -- the instrument MUST pass its blinded controls
(R-QUAL) before judging real data; (3) science -- preregistered, where PASS/KILL/UNDERPOWERED are
all valid and a KILL is never "fixed" to pass. "Write test, pass, move on" is literal at layers
1-2 and inverted at layer 3.

## 18. Risks

As v0.2 plus: F09 corrupting selection (STOP until repaired, R-RUNTIME); H1 over-claiming
detection of unobservable fabrications (guarded by the F01 ceiling); power/reachability
conflation (guarded by R-RC + the rejection rule); re-scoring overclaim (guarded by N5);
qualification overfitting (guarded by R-QUAL fresh challenges); epoch double-commit (guarded by
R-EP CAS). The Epic yields value even if H2 never passes: M1 (H1), M3 (reachability method) and
M4 (fabric) each stand alone.

---
*v0.3 design of record. Incorporates the Astra review (F01-F10) with operator dispositions.
Economics in the versioned appendix. Experiments gated per S16; Launchpad evolution not yet
authorized.*
