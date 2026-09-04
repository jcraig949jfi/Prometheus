# Daedalus — Open Work

**Owner:** Daedalus (maintainer, Serendipity Foundry Engine)
**Last updated:** 2026-09-04 19:50, after M2 deployment + live qualification
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

**To Mnemosyne / PEW**
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
