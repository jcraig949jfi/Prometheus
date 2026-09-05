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
