# Daedalus — Open Work

**Owner:** Daedalus (maintainer, Serendipity Foundry Engine)
**Last updated:** 2026-09-05, after Harmonia's independent qualification of session affinity v5 (ACCEPT ON ONE HOST)
**Pointer from:** `roles/Daedalus/RESPONSIBILITIES.md`

This is the standing list of what is NOT done. Items are closed by deleting
them and citing the commit in the sprint packet, never by marking them done
here and leaving them.

Status vocabulary is the same four states the closure pass established, because
collapsing any two of them is how "the fix is in" becomes a false statement:

    CODE_FIXED != SERVICE_DEPLOYED != LIVE_VERIFIED != QUALIFIED

---

## D0 — CLOSED 2026-09-04 19:45

### D0-1  Deploy the repaired engine to M2 — **DONE**
Deployed 19:45:35. PID 24324, `source_commit 0d3a52249` (contains `67c28acee`),
schema 4, 32 paths / 36 routes, correct M2 datastore and TLS identity. No race,
no second daemon, M1 and PEW untouched.
**Rollback point is now `var/engine.db.predeploy-20260904T194451.bak`** — the
earlier `pre-schema4-20260904T180254.bak` is SUPERSEDED and would discard
Harmonia's Round 1 work. The v3-cannot-open-v4 rule is unchanged and now live:
the database IS v4, so a code-only rollback leaves the service dead.

### D0-2  Pre-registered live bar — **DONE, one criterion corrected**
preflight exit 0; 119 tests; harness 12/12; isolation 7/7; live repair bar 8/8.
L-5 as I wrote it was mis-specified: four of six rows flipped, and the two that
did not are exercising the deliberate DEFAULT path (un-keyed creation; unattested
observation in a default world). Their opt-in counterparts are proven by live bar
H1/H2. The frozen probe was deliberately NOT edited — that would destroy
before/after comparability. Full reasoning: `sprint_20260904/M2_DEPLOYMENT_PACKET_2026-09-04.txt` §11.

### D0-3  M1 deployment decision — **STILL OPEN, NOT MINE**
M1 remains on `ce79401b` / schema 3, deliberately untouched. James's call.

---

## D1 — Engine work, justified but not urgent

### D1-1  Document the events() call-style asymmetry
The only residual defect from the REFUTED `I-EVENTS-SHAPE` finding. Raw HTTP
returns `{"events": [...]}`; `sfclient.events()` returns the unwrapped list.
Nothing tells a caller this. Belongs in `SerendipityFoundryClient/docs/API.md`
and the client guide. **Doc fix, not a code fix — do not "fix" the endpoint.**

### D1-2  Dry-run / preflight validation for frozen specs
Requested by Harmonia's freeze process. Blocked on **R-7** (her choice of shape).
My lean: (a) spec_hash prediction plus seed_root/enforcement TYPE validation —
cheap, purely functional, no shelf life. Not (b) full budget/window
admissibility, because that answer can go stale between preflight and execution
and **a stale PASS is worse than no PASS**.
Hard constraint: a dry run must append no event, debit no budget, mint no id,
and consume no idempotency key. A preflight that is itself a side effect leaves
the freeze dirtier than before it was checked.

### D1-3  Engine half of the measurement contract
`observations.content` is freeform and the SFE `measurements` table is empty, so
the engine cannot say WHAT was measured. This is the MEASUREMENT coordinate gap
and it is also Mnemosyne's standing ask (`roles/Daedalus/todo_20260902.md`,
`evidence_wiki/docs/PHENOTYPE_CONSUMER_REQUIREMENT.md`: 9 recoverable items;
only 2 of 6,006 candidate artifacts carry phenotype scores).
Blocked on **R-3** — which of the nine items are the ENGINE's versus the
experimenter's. Do not guess; guessing here produces a schema nobody consumes.

### D1-4  arena.run — bounded implementation
Engine-facing contract is CLOSED (closure packet §7). Five of six prerequisites
are met on the engine side. Blocked on **R-1** (fossil completeness) and **R-4**
(organism content id).
**Standing rule: the wrapper must make invalid states harder to express. It must
not automate the current 14-step hazard with the defects still underneath.**

---

## D2 — Deferred, with the trigger that revives each

### D2-1  Same-world concurrency qualification (Q-2) — DEFER
UNMEASURED and NOT ASSUMED SAFE. The code reads correct (claims run under
`BEGIN IMMEDIATE`, `UNIQUE(world_id, world_index)` backstop, server-issued
fencing `claim_id`) — **but that is a code reading, not a measurement, and I
decline to certify it as one.** Prefer campaigns designed not to need it.
*Revive:* a campaign that genuinely requires two workers in one world.

### D2-2  Duplicate work completion (Q-3) — before a parallel campaign
Complete the same `work_id` twice; complete with a stale `claim_id` after lease
expiry. Assert the second is REFUSED, not silently accepted.

### D2-3  N-isolated-world qualification (Q-1) — before a parallel campaign
N in {4, 16, 64}, one worker each. Success: zero errors, every world's ledger
verifies.

### D2-4  Restart durability under load (Q-4) — DEFER
Involves killing a live service under write load. Not to be run against an
engine holding anyone's campaign. Operator authorization required.

### D2-5  Throughput ceiling (Q-5) — DEFER
No number exists. Deliberate: the goal is trustworthy experimentation, not
maximum throughput. Measuring a ceiling we have no plan to approach buys
nothing.

### D2-6  Test-world GC / reaper — DEFER
M2 held 63 worlds at deploy time and the qualification run added more. Enumeration is now filterable, so cleanup candidates are identifiable
even though nothing reaps them. **Deleting worlds destroys ledgers** — that
waits for a stated retention policy, not a maintainer's judgement.
*Revive:* ~500 worlds, or disk pressure.

### D2-7  Universal constraint registry / predicate DSL — REJECTED for now
At seven constraints, a table of named tests IS the registry, and it executes on
every commit instead of drifting from the code it guards.
*Revive:* a constraint appears that a pytest cannot express.

---

## D3 — Blocked on other components (track, do not implement)

**To Mnemosyne / PEW**  (R-SFE-1 and R-SFE-2 are CLOSED on my side, live on
M2 at `0fd24e0f3` -- the ball is in PEW's court)
- **R-M-1 (new)** consume the SFE audit envelope. `GET /v2/worlds/{wid}/
  experiments/{eid}/audit-envelope` returns the whole sealed record as one
  hash-sealed object the PRODUCER exports. Store it immutably (the packet
  surface looks right) and serve it to third parties, so an investigator never
  needs an SFE credential. That is the half of R2-1 I cannot do.
- **R-M-2 (new)** wire `POST /v2/audit/verify-anchor` into fossil validation so
  `sfe_anchor_verified` can stop being pinned false. Send `exp_id`/`obs_id`
  along with the pair -- WITHOUT them the call only proves EXISTENCE, and a
  wrong-but-real event passes, which is the exact D1 hazard. With them the
  engine checks BINDING and rejects it.
- **R-M-3 (new)** record `engine_instance_id` from the verify response, not
  just `engine_source_hash`. The build hash was byte-identical on M1 and M2;
  the instance id is what disambiguates which engine minted an anchor.

- **R-1** typed fossil fields (action, input, output_digest, full world_config,
  registry_id, producer/schema versions) — 9 of 16 identities MISSING or
  AMBIGUOUS. Blocks a *preserved* result, not a one-off run.
- **R-2** anchor validation beyond shape + existence. The engine now RETURNS the
  exact anchor (D-ANCHOR-1); PEW should require the anchoring event to be the
  run's `OBSERVATION_RECORDED`, not merely an event that exists.
- **R-3** which of the nine phenotype items are the engine's (see D1-3).

**To Proteus**
- **R-4** the authoritative organism content id and where it is minted. The
  engine now ENFORCES an assertion; it does not MINT one.
- **R-5** `registry_id` for the fossil's registry_identity field.

**To Harmonia / James**
- **R-6** contract decision on a typed `components` field. The engine cannot see
  inside `spec`, so nothing mechanically checks that a run labelled A+B was
  actually A and B. **This is the likeliest route by which the programme
  produces a wrong interaction claim.** ~100 LOC once decided. It changes the
  meaning of `spec`, so it is not mine to decide.
- **R-7** dry-run shape (see D1-2).

---

## D4 — Session affinity v5: open items after Harmonia's qualification

Her packet closed with ACCEPT ON ONE HOST and four defects found and fixed
inside the review cycle (D-2, D-3, D-4/D-5, D-6/D-7 in her numbering). What
follows is what she did NOT close. **Nothing here is being fixed now** — logged
at James's instruction while she pushes on science.

Her closing question was "is a one-host pass being read anywhere as a fleet
pass?" **Checked, 2026-09-05: no.** No live doc makes a fleet claim;
`integration/M1_TEST_SURFACE_FOR_HARMONIA.md` explicitly warns against that
reading, and both engine packets say CLOSURE MET ON M1 / FLEET NOT CLOSED. The
real exposure is not the repo, it is packet drift in conversation — which is
exactly how the build-identity defect got written down in the first place.

### D4-1  Cross-machine affinity is unqualified BY ANYONE — the headline gap
The feature exists to stop an experiment wandering between MACHINES. Every
result to date comes from two processes on one box, where the path is
loopback-routed and **bypasses the host firewall entirely**. L1 (off-host
reachability), L2 (trust-anchor validation by a foreign client) and L3
(cross-machine affinity) are untouched by both seats.
**Trigger:** M2 back up. **Blocked on:** M2 down; also still on schema 4 with
no affinity layer, so deploy `b35046a60` or later there FIRST.

### D4-2  Legacy drain is not moving; the cutover will be date-driven
106 LEGACY sessions, all still OPEN, unchanged all day. `close_session` now
exists and is verified, but **nothing auto-closes and nothing should**: closing
a session to move a metric is gaming it unless the session is genuinely
finished. On current behaviour the cutover is date-driven (2026-10-01), not
drain-driven. **Decide before then:** drain deliberately, move the date, or
accept a date-driven cutover and say so.

### D4-3  Work-route claim scoping is HALF addressed (was R-E)
Strict now requires a session key on the four `/v2/work` routes, but a claim is
still bound only by `worker_id` — not to the session's own worlds. The unbound
half is untested by anyone.

### D4-4  Ablation is expressible but NOT enforced
T6 measured it both ways: four arms fork from one checkpoint with the world held
fixed structurally, specs re-hash identically on replay — but a child declaring
intervention A whose executor applied nothing was accepted end to end.
`interventions` are recorded verbatim and never interpreted BY DESIGN, so the
engine cannot check a declaration against an execution.
**This is not an engine fix.** Both the declaration and the executed spec are
independently recoverable, so the disagreement is DETECTABLE by an auditor
though not PREVENTED. Closing it needs an executor attestation binding the
applied component to the work result. Belongs to whoever runs the ablation.

### D4-5  Untested, and honestly recorded as such
- **Restart durability under load** (T5): needs an operator restart, and the
  restart procedure is itself hazardous — a stop can orphan the process tree
  while the OLD build keeps serving. Has happened twice.
- **Terminal-state sweep** across all 33 session-scoped routes (T7).
- Clone hazard, key TTL/rotation, singleton guard: read and accepted, never
  independently tested.

### D4-6  Battery count discrepancy — 23 vs 24, uninvestigated
I report `sfe_battery.py` at 23/23; she measures 24/24 on the same live engine.
Neither of us chased it. Harmless today, but it means one of us has a wrong
expectation of a control instrument, and a control whose expected value is
disputed is a poor control. **Cheap to settle; do it before it is load-bearing.**

### D4-7  C3e is a behaviour change in ADVISORY mode, not just strict
A completion replayed with a DIFFERENT result now returns 409 where it returned
200. Any instrument written against the old behaviour — including her T2 —
needs its expectation updated. Flagged so a future run does not read the fix as
a regression.

---

## D5 — Harmonia's scientific boundary campaign (S1/S2): what is ENGINE work

Her packet found the pipeline manufacturing a false discovery on the real
record: **p=0.0357 between a player and itself**, and p=0.4991 on the same data
when counted at the world unit. Five ranked blockers, three with ZERO
detectability after the fact. Logged, not fixed.

**Most of her five blockers are NOT engine work, and saying so precisely
matters more than volunteering to build things.**

### D5-1  Pre-registration is already sealable — VERIFIED, no engine change
Her C-3/C-4/C-5 (declare unit of analysis, comparison family, effect floor
before the data is seen) do not need an engine feature. Measured on a scratch
instance of the qualified build:

    spec = {unit_of_analysis, n_per_arm, comparison_family_size,
            smallest_effect_worth_believing, arms}   -> committed
    spec recovered byte-identical .................... True
    spec_hash sealed in the ledger ................... yes
    recomputes locally to the same hash .............. True
    EXPERIMENT_COMMITTED carries spec_hash + prospective_rule
                                    + engine_source_hash

So the declaration is **tamper-evident and order-provable**, not merely
disciplined: `committed_seq` fixes it in ledger order exactly as the DFX-1
prospective window fixes a prediction. Her §9 says these three are
"unreconstructible after the fact" — correct, which is precisely why sealing
them at commit is the whole fix, and it is available today.

**Honest limit, same shape as ablation: the engine SEALS the declaration and
does NOT check that the analysis obeyed it.** Detectable by audit, not
prevented. An engine that adjudicated analyses would be computing outcomes,
which it deliberately does not do.

### D5-2  Blocker 3 (player identity is a name) — the mechanism already exists
A player placed into a world as an artifact is content-addressed: `blob_hash`
is `sha256(bytes)` and is **world-independent**. Two arms that are the same
policy under two names would carry an IDENTICAL `blob_hash` — mechanically
detectable, no engine change. The duplicate-under-a-new-name that produced
p=0.036 against itself is catchable by comparing the hash the engine already
returns. Her C-2 ("different requires the hashes to differ") is satisfiable
today for any player that is placed as an artifact.
**Worth telling her before SE-1**, since it converts blocker 3 from a build
into a habit.

### D5-3  Executor attestation (C-1) — engine half is optional, not required
The executor's config hash can travel in the work `result`, which the engine
already seals into `result_hash`. No engine change is needed to make it
tamper-evident. A first-class typed field would be nicer to query and would let
the engine refuse a completion that omits it — **that is the only genuinely
engine-side option in her packet**, and it is a design choice, not a defect.
Do not build it unasked; the client-side form is available now.

### D5-4  The one thing no engine rule can close
Her S2 case 6 — declared A, ran A plus an undeclared co-intervention C — leaves
a record BYTE-IDENTICAL to the honest run. Five of six dishonest executions are
detectable from fossils; this one is a missing MEASUREMENT, not a missing
check. The engine cannot know what it was never told, and no engine-side rule
closes it. Correctly classified in her packet; recorded here so nobody later
files it as an engine bug.

### D5-5  Not mine, tracked only
Unit-of-analysis enforcement in ANALYSIS, comparison-family correction, effect
floors, and player-class breadth (her directive item 12, unaddressed: only
stochastic scalar-emitting policies exercised, nothing stateful or learning).
These belong to whoever runs the campaign.

---

## D6 — "What else fails in the direction of looking good?" (Harmonia S3)

Her S3 closing question, answered by MEASUREMENT on a scratch instance of the
qualified build rather than by listing suspicions. Four engine signals that
return GREEN where a careful reader would reasonably take them to mean
something they do not mean. Logged, not fixed.

### D6-1  EVERY epistemic signal stays green on a contradicted execution
The sharpest one, and it extends her S2 case 6 from ablation to the whole
epistemic surface. Spec declared `arm-A`; the executor completed reporting
`actually_ran: arm-NOT-A`; the observation bound that work_id. Result:

    observations_engine_attested         1
    observations_prospectively_predicted  1
    claims_surviving                      1

ENGINE-ATTESTED means the engine ran and sealed the work. It does NOT mean the
executor did what the spec declared — the engine never reads the spec against
the result, by design. PROSPECTIVE means ORDERING ONLY: the prediction preceded
the commit. It is not evidence the predictor lacked foreknowledge; on a
deterministic substrate it cannot be.
**A reader who takes "engine-attested + prospective + surviving" as a quality
stamp is reading three ordering facts as a correctness claim.**

### D6-2  `ledger_integrity_ok: true` on deliberate garbage
A world containing only meaningless bytes reports integrity TRUE. It verifies
the HASH CHAIN, never the CONTENTS. "Integrity OK" is the phrase most likely to
be quoted as assurance in a packet, and it assures only that nothing was
tampered with after the fact.

### D6-3  A budget that is REPORTED, looks tracked, and caps nothing
Declared `limit 2, enforcement measured`; attempted 6; **accepted 6**;
`resources` reports `consumed: {experiments: 6}` and `exhausted: false`. The
presence of budget instrumentation in the output reads as control. `measured`
is the DEFAULT, so this is the path of least resistance.

### D6-4  Event count is NOT a count of distinct things — my hypothesis was wrong
I predicted idempotent reposts would return 200 while creating nothing, so a
loop counting successes would overcount. **Measured: the opposite shape.** 20
identical reposts produced 20 HTTP 200s AND 20 `ARTIFACT_CREATED` events, while
the knowledge frontier correctly reports **1** distinct artifact.

So the inflation is in the LEDGER, not the response: an analyst who counts
`ARTIFACT_CREATED` events as n gets 20x the distinct artifacts. This is
Harmonia's unit-of-analysis defect one layer down — event rows are not
independent units any more than observations within a world are. Her C-3
(declare the unit) covers it only if "event count" is explicitly excluded as a
unit.

### D6-5  Advisory enforcement is itself a looks-good failure
A campaign running with no session key sees 200s everywhere and looks entirely
healthy while the affinity protection silently does not apply. The mode is the
DEFAULT and the live engine runs it. Every unkeyed request is counted
(`SESSION_ABSENT_ALLOWED`) — so the evidence exists, but nothing surfaces it to
the experimenter.

**Common shape across all five:** the engine reports faithfully on what it
MEASURES, and every one of these is a reader inferring a property the engine
never claimed to measure. That is not fixable by adding checks; it is fixable
by naming, in the claim, which property each green signal actually establishes.
Which is Harmonia's INVARIANT III arriving from the engine side.

---

## D7 — Substrate candidates from Harmonia S1-S5 (RECORDED, NOT ACCEPTED)

Operator-proposed 2026-09-05, with a governing test I am adopting verbatim:

> **Can SFE know the fact deterministically? If yes, expose or enforce it. If
> knowing it requires statistical or scientific interpretation, leave it to
> Harmonia and give her the provenance.**

Nothing here is scheduled. Each candidate has been PUT THROUGH that test rather
than transcribed, because three of eight turn out to be already-done, cheaper
than proposed, or impossible as stated.

### ALREADY DONE — do not schedule
**P2 pre-registration manifest hashing.** Verified in D5-1: a manifest carried
in the experiment spec is sealed by `spec_hash` at commit, recovers
byte-identical, recomputes locally, and is fixed in ledger order by
`committed_seq`. "Changes create a new hash rather than silently mutating" is
already true: the spec is frozen at commit and a later commit is a new
experiment. Satisfied by existing machinery plus the habit of putting the
manifest in the spec.

### CHEAPER THAN PROPOSED — expose, do not build
**P0 experimental-unit provenance.** The engine ALREADY records what separates
an independent world from a continuation: `parent_world_id`, `fork_point`, the
originating `checkpoint_id`, `seed_root`, and root-vs-fork-child. Deterministic
and durable today. The gap is that nothing SURFACES it as an independence
signal, so an analyst must walk lineage to discover that seven replicates are
fork children of one parent. Reduces to a derived read, not new state.

### DETERMINISTIC — genuinely buildable
**P0 replay-strength declaration (L0-L4).** The engine holds full event
sequences and terminal outcomes, so it can MEASURE achieved replay level
between two executions of one spec: L0 (sequence identical) and L1 (terminal
outcome identical) are hash comparisons, not judgements. A claim can declare
its required level; the engine can report the level achieved. L2-L4
(distribution, ranking, phenotype) are statistical and stay with Harmonia.
Buildable for L0/L1 ONLY — say so rather than implying all five.

**P1 claim-to-configuration provenance / experiment family.** Checked whether
`lineage_edges` already covers it. It has free-text `src_kind`/`dst_kind`/
`relation`, `add_lineage_edge` accepts arbitrary kinds, and it carries a
`claimed` flag separating asserted from derived edges. **But it is
WORLD-SCOPED** — `world_id NOT NULL`, and the only query is
`GET /v2/worlds/{wid}/lineage`. A claim family spans MANY worlds (the sweep,
the replication, the moderator arms), so the existing DAG cannot express one.
Real new work, and the reason is now precise.

**P1 degenerate-replication warning — WITH A CORRECTION I would insist on.**
The proposal says warn when replicates collapse to sd about 0. Computing sd
requires knowing WHICH field of a freeform observation is the outcome, which is
scientific interpretation and belongs to Harmonia. IDENTITY is not: "these
seven nominal replicates carry byte-identical content_hash" is a hash
comparison the engine can make deterministically. **Signal on exact
duplication, never on variance.** That keeps the engine on the correct side of
its own boundary and still catches the S3 artifact, whose worlds 2-8 were
identical to six decimals rather than merely low-variance.

**P2 machine-readable warning surface.** The `failures` table plus
`FAILURE_RECORDED` already gives a typed, queryable attachment point with a
`failure_type` vocabulary. Mostly a vocabulary decision
(`NON_INDEPENDENT_UNITS`, `STATE_CONTINUITY`, `REPLAY_L1_ONLY`), not new
storage.

### BUILDABLE ONLY AS DECLARATION + ATTESTATION — with a stated blind spot
**P0 replicate/state isolation contract.** The operator is right that this is
the highest value, and equally right that SFE must not become the statistician.
The precise limit: **the engine never sees player state and can never know
whether a reset happened.** What it CAN do is deterministic:

    1. the experiment DECLARES state_scope / independence_required
    2. the executor ATTESTS an entry-state hash per world
    3. the engine CHECKS (2) against (1) and emits
       INDEPENDENCE_CONTRACT_VIOLATED on disagreement

Step 3 is a hash comparison. Steps 1 and 2 are declarations the engine cannot
validate — it is checking a claim against a claim, which is still worth far
more than nothing because BOTH become part of the sealed record.

**Harmonia's S3 Q4 blind spot must ship with it or the check will be trusted
too far: a CONVERGED leaker enters every world from the same fixed point, so
its entry-state hashes become indistinguishable from an honest reset.** Under a
declared reset discipline identical entry states are expected; under declared
carry-over they are a red flag. The same observation means opposite things
depending on a declaration only the experimenter can make. An engine reporting
"independence verified" there would manufacture exactly the looks-good failure
D6 catalogues.

**P1 fixed-vs-factor declaration.** Once declared in the manifest, checking
that a declared-FIXED value actually stayed constant across a family is
deterministic — but it needs the cross-world family link to have anything to
check across. Depends on the family work; not independently useful.

### NOT ENGINE WORK — recorded so nobody re-files it
Multiplicity correction, null calibration, stopping rules, effect estimators,
and deciding whether a moderator sweep was sufficient. The S1 p=0.0357 result
and the S5 winner-curse finding are scientific-instrumentation
responsibilities. The engine's job is to keep the twelve draws visible as
twelve related attempts — the family work above — not to judge them.

### THE DEPENDENCY THAT MATTERS
Four candidates (fixed-vs-factor, claim provenance, cross-family degeneracy,
and any "show me every experiment run while trying to make claim C survive"
query) reduce to ONE missing primitive: **a lineage edge that crosses world
boundaries.** If any of this is scheduled, build that first; the rest are reads
on top of it.

Not reopening the closed strict-session and completion-replay defects; per
D4-7 their regression tests are in the suite.

---

## D8 — R1-R10 and nine structural changes from Harmonia S1-S7 (NOTES ONLY)

Operator-relayed 2026-09-05 after her packet 6. **Ingested, not scheduled, not
implemented; the engine was not restarted.** Same boundary rule as D7, and the
operator's explicit list of things NOT to hard-code (power >= 0.8, shrinkage as
universal estimator, mandatory replication, C-7'/C-8' as eternal laws) is
adopted.

Three items were checked against the engine before being written down, and two
land harder than the packet states.

### R8 — the defect has a CONCRETE INSTANCE ALREADY IN THE ENGINE
`ObservationCreate.replication: bool = False` (`sfe/api.py:119`). The engine
literally ships the boolean replication claim the packet calls actively
dangerous.

Important nuance before anyone "fixes" it: its real meaning is narrow and
correct — F3, "this is a SECOND observation bound to a prediction, a retest
that never re-adjudicates the original". It does **not** mean "independently
replicated". So the defect is not the mechanism, it is that **the field name
invites exactly the misreading the packet warns about**, and a typed
replication level would sit naturally beside it rather than replacing it.
Small, high value, and it must not silently change F3 semantics.

**Caution the packet's own principle implies: the replication taxonomy is still
moving.** S3 defined L0-L4 (sequence / terminal / distribution / ranking /
phenotype); packet 6 defines L1-L6 (resampling / world-distribution /
landscape / implementation / player-build / full independent). Those are not
the same axis. Encoding either as an enum now risks hard-coding a taxonomy that
changed once in two loops — the same failure the operator warns about for
C-7'/C-8'. **Record the level as a declared STRING plus the dimensions
reinstantiated/held constant; do not enum it yet.**

### SUCCESSFUL_NEGATIVE — confirmed NOT representable today
Outcome vocabulary is exactly `FALSIFIED | SURVIVED | INCONCLUSIVE`
(`runtime.py:1370`); hypothesis states are `FALSIFIED | SURVIVED`. "The effect
is bounded below a declared relevance floor" is a POSITIVE result, and today it
can only be recorded as SURVIVED (ambiguous with "the hypothesis stood") or
INCONCLUSIVE (which destroys exactly the information that makes it valuable).
**The operator is right that this is an epistemic state-machine gap, not
statistics.** The engine would not be judging whether an equivalence test is
valid — only storing a conclusion the experimenter reached, which it already
does for the other three outcomes.

### NO_EFFECTIVE_INTERVENTION — cheapest item on the list, and I would rank it
### HIGHER than its position as structural change #7
Confirmed: interventions are recorded VERBATIM in `WORLD_FORKED`
(`runtime.py:2009`) and nothing else. There is no before/after, so a
perturbation that changed nothing is indistinguishable from one that worked.

Why it is the cheapest: **`before_hash == after_hash` is a hash comparison, not
a judgement.** It needs no statistical interpretation, no new taxonomy, and no
cross-world primitive. It is fully inside the deterministic boundary, and it
came from a real mistake Harmonia made and caught (a seed perturbation that
initially had no effective change). Warning-only, not fail-closed: a legitimate
no-op perturbation is conceivable and the engine should say so loudly rather
than refuse.

### requested / executed / analysis config hashes — the engine already has 1 of 3
`spec_hash` at commit IS the requested-config hash, sealed and order-proved
(D5-1). So the structural change reduces to: obtain `executed_config_hash` by
executor attestation, obtain `analysis_config_hash` by analyst declaration, and
**compare three hashes** — which is deterministic. The operator's worked example
(requested noise 0, executor used 0.02, analyst assumed 0) is caught by
comparison alone, with the engine understanding nothing about noise.

### transport_domain vs tested_variation — deterministic set comparison
"Does the asserted claim domain exceed the experimentally tested domain?" is a
containment check over declared values. The engine asserts nothing about
transport; it compares two declarations. Correctly inside the boundary.

### R10 measurement-process provenance — the auditability half is deterministic
The engine cannot know a scorer's precision or noise model. It CAN record a
declared `measurement_process_hash` and then detect that **two runs with
different measurement regimes are being compared as identical conditions** —
again a hash comparison. This is the right split, and the 1.8%-noise
sign-reversal is the motivating evidence rather than a rule to encode.

### Still gated on the same missing primitive
R4 (comparison family), R7 (campaign manifest), the claim-family lineage, and
"best of twelve remains visible as one selection family" all still reduce to
**a lineage edge that crosses world boundaries** (D7). `lineage_edges` is
world-scoped. Nothing in packet 6 changes that; it adds more consumers of it.

### First-class claim record
Would subsume claim_family_id, transport_domain, replication level claimed vs
observed, measurement_process_hash, and the SUCCESSFUL_NEGATIVE state. Note it
is the LARGEST item here and depends on the cross-world primitive. Recorded as
one coherent design, not as nine separate fields to bolt on.

### NOT engine work, restated
Multiplicity correction, null calibration, stopping rules, estimators, power
thresholds, whether a sweep was sufficient, and whether an equivalence test is
valid. Per the operator: expose `relevance_floor`, `design_effect`,
`target_power`, `estimated_power`, `promotion_rule`, `estimator` as FIELDS;
enforce none of them.

### If any of this is ever scheduled, the order is
1. NO_EFFECTIVE_INTERVENTION before/after hashes — deterministic, no
   dependencies, catches a real mistake already made.
2. Cross-world lineage edge — unblocks four other items.
3. executed_config_hash attestation (R2) — the largest provenance hole, and
   the one that makes R5/R9/R10 checkable rather than declarative.
4. Typed replication level as a STRING plus dimensions — after the taxonomy
   stops moving.
Everything else is a read or a field on top of those.

---

## D9 — Estimator identity, and which of D7/D8 is fitted to one toy

Harmonia's S8 amendments, 2026-09-05. Notes only; engine untouched.

### The three amendments, accepted
1. **`estimator` must be an immutable identity HASH**, same treatment as R3
   player identity. Her measurement: a trimmed mean standardised by a
   winsorised sd overstates a heavy-tailed effect **3x with no selection in
   play**. Estimator choice is a 3x error channel independent of everything
   else the engine records, so a free-text field is not enough.
2. **`analysis_config_hash` must include the estimator and its parameters.**
   Her twin of the operator's worked example is exact: requested Hedges,
   analysed with a trimmed mean — same class, same invisibility, 3x the error.
3. **Boundary rule gains a clause:** a scientific rule that has survived only
   one estimator and one outcome distribution is L1 evidence ABOUT THAT RULE
   and must not be encoded. Applies to C-8' too, which has survived exactly one
   organism.

**Engine-side note on (2) that raises its priority:** of the three config
hashes, `requested` already exists (`spec_hash`, sealed at commit) and
`executed` is obtainable by executor attestation — but **`analysis` has no home
in the engine at all.** An analysis is computed outside the substrate from
events and observations; the engine records nothing about it. So the third hash
is not the third of three equals — it is the only one with no representation
whatsoever, and the estimator that carries a 3x error lives inside it.

### WHY C-7 AND C-7' BOTH DIED THE SAME WAY
Both were stated as laws when they were conjunctions with an unstated term
doing the work. C-7' says power controls exaggeration; it silently required
"...given an unbiased estimator". **This is the same shape as my own coverage
test**, which scoped its probe with the predicate that created the gap it
missed, and as `engine_attested` reading as correctness when it establishes
ordering. In all three the claim carried a precondition that was invisible
precisely because nobody had varied it.

### SELF-CRITICISM: MY D7 CORRECTION IS FITTED TO HER ORGANISM
In D7 I insisted degenerate-replication should signal on **identical content
hashes, never on computed variance**, because identity is deterministic and
variance requires knowing which field is the outcome. I still hold the boundary
argument. **But the detector is fitted to her toy.**

Her S3 leaked learner CONVERGED, so worlds 2-8 were identical to six decimals
and a hash comparison catches it. **A leaking organism that does not converge
produces correlated-but-not-identical outcomes — invisible to hash identity,
visible only to variance or correlation, which is exactly what the engine must
not compute.** So my recommendation catches the observed case and not the
general one, and it was validated against a single organism in which
convergence made identity the right test.

Recorded rather than fixed: the honest response is not to reach for variance,
it is to state the detector's domain (converging state leakage only) and let
the general case remain Harmonia's.

### WHICH OF D7/D8 IS ORGANISM-INDEPENDENT
Her next move is a second organism to separate facts about experiments from
facts about this toy. The same question applies to the substrate backlog, and
the split is knowable now:

**Organism-INDEPENDENT (pure provenance; a second organism cannot refute
these):** requested/executed/analysis config-hash divergence; estimator
identity hash; player identity hash; `NO_EFFECTIVE_INTERVENTION`
(before == after); cross-world lineage edge; SUCCESSFUL_NEGATIVE as a state;
measurement-process hash. These are facts about records, not about dynamics.

**Organism-DEPENDENT (may be over-fitted, do not build first):**
degenerate-replication via hash identity (above); the L1-L6 replication
taxonomy, which Harmonia says she invented and has never seen give a wrong
answer; order-sensitivity checks, which presuppose stateful players;
independence-contract checking, whose blind spot is precisely a CONVERGED
leaker.

**Consequence for scheduling:** the D8 build order still holds, and it happens
to be organism-independent all the way down — no-effective-intervention hashes,
then the cross-world edge, then executed-config attestation. Nothing in D7/D8
gates a second organism, and **the substrate can run one today.**

---

## Standing discipline for whoever picks this up

- Run the standing battery in `RESPONSIBILITIES.md` after ANY engine change and
  before ANY onboarding.
- Attest the daemon before recording any result as evidence about new behaviour:
  `integration/sfe_preflight.py`. A green suite says nothing about a running
  process.
- Validate a gate in BOTH directions — it must fail on the known-bad target AND
  pass a positive control, or you have not shown it discriminates.
- A probe returning a status code is not measuring what you think unless you ran
  the same battery against a control, and checked that a success code
  corresponds to the effect actually occurring. Four of my own probe results
  were retracted for exactly this.
- Refuted findings are superseded, never deleted:
  `sprint_20260904/issue_disposition.json`, enforced by
  `sprint_20260904/validate_disposition.py`.
