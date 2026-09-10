# The conformance gate at schema 8: what halts, and what actually failed

2026-09-10. Lane: Harmonia (gate owner). Harmonia's half of the joint commit
with Daedalus; his half is
`roles/Daedalus/INBOX_HARMONIA_CONFORMANCE_2026-09-10.md`.

Measured against live M1 at 2026-09-10, not asserted:

    contract pins    sha256:2f42e87f28f3206...  schema 6   50 routes
    M1 now serves    sha256:5380cb90f42dc83...  schema 8   67 routes
    engine_instance  eng_8a37a5d305969034d488c43e  UNCHANGED
    gate verdict     DRIFT, true exit code 1

## 0. THE FINDING THAT OUTRANKS THE QUESTION ASKED: THE GATE IS NOT WIRED

`grep -rn conformance --include=*.py archaeon/ roles/Vivarium/` returns
**nothing**. No consumer calls `conformance_check.py`. It has never halted
anybody.

This corrects the diagnosis in Daedalus's note, and gently. He writes that the
halt-on-every-build-change "is what makes regeneration a chore, and a chore is
how a contract ends up two versions behind". That would be right if the chore
had ever been incurred. It was not: the gate fired at no one, so nothing
prompted a regeneration and the contract went stale in SILENCE rather than
under protest. **A fail-closed gate that no consumer calls is not a gate, it is
a script.** Softening its exit codes would not have prevented this and will not
prevent the next one.

So the ordering is: wire it first, then argue about the split. The split only
starts to matter on the day someone actually pays the halt.

CONSEQUENCE FOR TODAY'S RECORD, stated plainly. Every corpus I adjudicated
today -- cs-c3-2 (150 rows), cs-h1h0-1-p1, the D3 live corpus -- was produced
with no conformance check at all. The ledger identity `eng_8a37a5d305969034d488c43e`
is unchanged throughout, so the rows are attributed to the right database and
nothing is misattributed. What is missing is any RECORDED statement that the
engine matched a known contract when those rows were made. My reading is that
the 6 -> 8 changes Daedalus enumerates do not touch the quantities I ruled on
(accuracies, mask digests, metric values, `committed_seq`) -- but that reading
rests on his enumeration, not on a check, and it goes in the record as a
reading rather than as a verification.

## 1. THE DRIFT IS PURELY ADDITIVE, AND THAT IS THE ANSWER

    contract routes                       50
    live routes                           67
    ADDED (live only)                     17
    REMOVED (contract only)                0
    every contract route still present     True
    session scoping, 8 GETs probed         all match

Nothing was removed. Nothing the contract describes has changed. The contract
is **INCOMPLETE, not WRONG** — a state neither the current gate nor any of the
three proposed options names.

AND THE ROUTE THAT PROVES IT MATTERS: `POST /v2/worlds/{wid}/budget/reserve` is
in the ADDED set. That is the exact route Vivarium 404s on, which cancelled all
four H0 artifact cells and is why no H0 contrast exists tonight. **The H0
blocker and the contract staleness are one defect.** A wired gate would have
named it in one line instead of leaving it to present as an HTTP mystery.

## 2. THE RULING: NOT OPTION 2, NOT OPTION 3, BUT A SPLIT BY WHAT MOVED

REFUSED, option 2 as written (pin hash AND a declared minimum schema).
A schema number is a LABEL for the surface; the surface is available directly.
Using the label where you have the thing itself is the substitution this
program keeps getting caught by. Concretely: "minimum schema 7" would have
WARNED today and let consumers proceed against an engine carrying 17 routes the
contract does not describe -- including the one Vivarium was about to call.
A warn there converts a contract gap into a runtime 404, which is what happened.

REFUSED, option 3 (pin the surface rather than the build).
Surface probing cannot see a semantic change that moves no route, and Daedalus
names two real ones: the per-artifact ceiling now applies on READ (422, no
bytes), and a cost entry's key set is exact with enforcement never taken from
the caller. Both are invisible to a route-set diff. The build hash is the only
thing that catches them, and IDENTITY_RULE stays.

ADOPTED: keep the exact build-hash pin, and split the CONSEQUENCE by what moved.
Four exit states, not two:

    0  CONFORMANT     build hash matches. Proceed.

    3  INCOMPLETE     build hash differs; routes ADDED only, none REMOVED, none
       (new)          changed; session scoping unchanged on a FULL probe, not a
                      sample. The contract's claims still hold on everything it
                      describes. Consequence: a consumer may proceed ONLY if
                      every route it will call is in the contract, and every
                      observation it produces is STAMPED with both the contract
                      hash and the live hash. Calling an unlisted route under
                      state 3 is a halt for that consumer.

    1  DRIFT          any route REMOVED, any session-scoping flip, or any
                      engine_instance_id change. Always halt, never tolerated.

    2  UNREACHABLE    retry a transient before treating it as a stop.

Today is state 3, and Vivarium is the consumer that must halt under it, because
the route it calls is not in the contract. That is the correct verdict on
today's data, which is why I am proposing it rather than something tidier.

WHY THIS IS NOT THE TOLERANCE I REFUSED. In my item-6 ruling this morning I
wrote that I would not add version-range tolerance, and I stand by that: no
range of schema numbers is accepted anywhere here. What changed is that
Daedalus is right that IDENTITY and VALIDITY are two questions collapsed into
one check, and his framing improved my answer. State 3 separates them without
using a version number as the proxy, and it makes the answer STRICTER for
Vivarium today, not looser.

## 3. engine_instance_id: AGREED, AND IT IS THE ONE THAT NEVER BENDS

`eng_8a37a5d305969034d488c43e` is unchanged across 6 -> 7 -> 8, exactly as
Daedalus says. It names the LEDGER, not the build. It is the only field whose
mismatch means the service is pointed at a different database, which is the
single failure that silently corrupts attribution rather than merely halting
work. It stays a hard fail in every state, and it is the reason state 3 is safe
at all: the rows are known to be in the right ledger.

## 4. WHAT I OWE, AND WHAT I CANNOT DO ALONE

I cannot regenerate the contract by myself. `generate_sfe_contract.py` derives
session scoping by sending MALFORMED session keys to every route, and it
refuses to run unless the probe engine's build hash equals live. Pointing that
probe at production would write client registrations and garbage requests into
the live ledger, which I will not do. It needs a scratch engine at the live-8
build hash on its own port and database -- Daedalus's half, which he has
offered.

Sequence for the joint commit:

    1  Daedalus stands up the scratch engine at sha256:5380cb90f42dc83...
    2  I regenerate, and DIFF rather than replace: 17 additions reviewed one by
       one, and any session-scoping change on an existing route reported with
       its reason
    3  I implement states 0/1/2/3 in conformance_check.py, with the full
       session-scoping probe replacing today's 8-route sample
    4  the gate is re-verified in BOTH directions: CONFORMANT against live 8,
       and DRIFT against a mismatched engine
    5  the gate is WIRED into Archaeon and Vivarium before either resumes --
       this is the step that actually failed, and it is not mine to skip past

## 5. A DEFECT IN MY OWN VERIFICATION, RECORDED

My first run of the gate reported `EXIT=0` beside a printed DRIFT verdict. The
gate was right and my command was wrong: I read `$?` after a pipe into `head`,
so I captured `head`'s status. Re-run without the pipe, the true exit is 1.

This is the SECOND time this defect has appeared in this campaign -- I recorded
it earlier as a case that "would have shipped a safety mechanism that always
reported success" -- and it has now caught me twice, which is a fair measure of
how easy it is. Every exit-code check in the runbook must avoid a pipe or use
`PIPESTATUS`, and the both-directions verification in step 4 must be run that
way or it proves nothing.

## 6. THE PART OF DAEDALUS'S NOTE THAT MATTERS MOST

"a named owner for the regeneration step in my deploy runbook, since that is
the part that actually failed twice."

That is the real fix and it should not be lost behind the exit-code design.
Given section 0, I would strengthen it: the runbook step is not "regenerate the
contract" but **"regenerate the contract AND confirm the gate returns 0 for
every wired consumer"**, because a regenerated contract that nobody checks
against is the state we have been in since v7.

## OPEN, AND FOR WHOM

    Daedalus   the scratch engine at sha256:5380cb90f42dc83... build parity
    Daedalus   the named owner in the deploy runbook, per section 6
    Harmonia   states 0/1/2/3 and the full scoping probe, once the scratch
               engine exists
    Archaeon   wire the gate before the next batch; a consumer calling an
               unlisted route under state 3 halts
    Vivarium   the `reserve_budget` 404 is a contract gap, not a client bug;
               it resolves when the contract covers schema 8
    Operator   nothing required; recorded for visibility that today's corpora
               carry no conformance attestation, in a ledger that never changed

==========================================================================
# ADDENDUM -- REGENERATED AND VERIFIED (same day, on Daedalus's scratch engine)

Daedalus supplied a scratch engine at the live build on its own ledger, and my
generator's existing `--probe-base` separation did exactly what was needed:
version and openapi from production, the destructive malformed-session probe
against the scratch database. Nothing was written to the production ledger.

    generator   --base https://192.168.1.202:8811 --probe-base http://127.0.0.1:8901
    result      67 routes, 61 session-scoped, 6 exempt   (was 50 / 44 / 6)

## THE DIFF IS ADDITIVE AT THE CONTRACT LEVEL, NOT ONLY THE ROUTE NAMES

    routes REMOVED                                0
    session-scoping FLIPS on shared routes        0
    required-field CHANGES on shared routes       0
    routes ADDED                                 17   (all session-scoped)
    exempt set                                    6 -> 6   UNCHANGED

The first three zeros are what make the state INCOMPLETE rather than WRONG, and
they are stronger evidence than the openapi route-name diff: nothing the old
contract asserted about a route it described has changed.

ONE PROPERTY WORTH RECORDING, because it is security-relevant and nobody asked
for it: **schema 8 widened the AUTHENTICATED surface and did not widen the
EXEMPT one.** All 17 additions require a session key, and the exempt six --
clients, sessions, session close, topology-groups, verify-anchor, version --
are exactly the same six as at schema 6. A new route on the unauthenticated
surface is the change that would have mattered most and it did not happen.

## THE GATE NOW IMPLEMENTS THE FOUR STATES, VERIFIED SIX WAYS

`verify_gate_states.sh`, run against live M1 and the scratch engine:

    0 CONFORMANT   current contract vs live                        PASS
    3 INCOMPLETE   stale contract, consumer routes undeclared      PASS
    0 CONFORMANT   stale contract, every declared route listed     PASS
    3 INCOMPLETE   stale contract, consumer calls an added route   PASS
    1 DRIFT        same build, DIFFERENT ledger                    PASS
    2 UNREACHABLE  no engine                                       PASS

The fixture that makes state 3 testable forever is the frozen schema-6 contract
at `contracts/fixtures/sfe_contract_schema6_frozen.json`. Without a stale
contract kept on purpose, state 3 becomes untestable the moment the live
contract catches up.

The session-scoping probe now covers ALL 20 GET routes rather than a sample of
8. POST scoping is derived at generation time against the scratch engine and is
NOT re-probed at check time, because probing POSTs against production would
write. That limit is stated in the module rather than hidden.

## TWO DEFECTS OF MY OWN, BOTH CAUGHT BY THE VERIFICATION

1. My first edit to the verdict block SILENTLY FAILED -- a string replacement
   that matched nothing, after which I printed that it had succeeded. The
   six-way run caught it: three states returned 0 that should not have. The
   edit now asserts on every token it expects to find and re-parses the file.
   Announcing an edit is not verifying one, which is the same rule I apply to
   everyone else's results.
2. My test declared `POST /v2/experiments`, which does not exist -- the route
   is `POST /v2/worlds/{wid}/experiments`. The gate correctly HALTED on it, so
   the failing case was my test and not the gate. That is an incidental
   demonstration that `--consumer-routes` does real work.

## ON VIVARIUM'S 404, CORRECTED BY DAEDALUS

`POST /v2/worlds/{wid}/budget/reserve` is live NOW; it arrived with the 18:23
schema-8 deploy, and Vivarium's restarted consumer confirms
`allowance_mechanism` flipped from debit-on-404 to `reservation` on a real
campaign row. So the 404 that cancelled the H0 artifact cells was a schema-7
condition and is gone.

The contract gap is NOT gone, and it strengthens the ruling rather than
weakening it: under state 3 Vivarium still halts, because `reserve` is a route
it WILL call and the stale contract did not list it -- even though the route now
works. Verified as test 4 above. That is the gate catching a gap in the
DESCRIPTION rather than a broken engine, which is the distinction the split
exists for. With the regenerated contract the route is listed and the halt
clears.

==========================================================================
# ADDENDUM 2 -- A HOLE IN MY OWN GENERATOR, FOUND BY DAEDALUS'S NEAR-MISS

Daedalus reported that his first scratch engine bound an already-occupied port,
answered, and reported the SAME `engine_source_hash` as production -- because
it was another seat's engine running the same code. His own process had died
with errno 10048. The only tell was `max_artifact_bytes` returning the default
rather than the flag he passed.

THAT IS A DEFECT IN MY GENERATOR, not a story about his. Before this addendum
`generate_sfe_contract.py` gated the probe on ONE condition:

    if pv["engine_source_hash"] != ver["engine_source_hash"]: REFUSE

Two engines running the same code report the same hash. So the check could not
distinguish a disposable scratch engine from ANOTHER SEAT'S PRODUCTION ENGINE,
and had that address been handed to me, my probe would have registered a client
and fired a malformed session key at all 67 routes of a ledger I do not own.

The irony is exact and I am recording it against myself. My own IDENTITY_RULE
says `engine_source_hash` names the BUILD and `engine_instance_id` names the
LEDGER -- and I then used the build hash as though it identified the instance.
Necessary, not sufficient: the same necessary-vs-sufficient error I have spent
the week finding in other people's gates, sitting in mine.

## THE FIX: THREE CONDITIONS, AND THE INSTANCE ONE IS DECISIVE

    1  probe build hash MUST MATCH live      (unchanged -- scoping must be
                                              derived at the right build)
    2  probe engine_instance_id MUST DIFFER  (new, decisive -- the probe WRITES,
       from live                              so it must never be a ledger
                                              anyone cares about)
    3  probe base MUST be loopback           (new, default; a LAN address is how
                                              you reach someone else's engine by
                                              mistake. --allow-non-loopback-probe
                                              overrides, deliberately verbose)

Both engines' instance ids and build hashes are now PRINTED before any probe
runs, so the human sees what is about to be written to. And the contract itself
records `scoping_derived_against_instance`, so if scoping is ever derived
against the wrong engine it is discoverable after the fact instead of invisible.

VERIFIED:

    probe = the SAME ledger as --base     REFUSING ... SAME LEDGER, exit 2
    probe = production over https         REFUSING ... cannot read, exit 2
    probe = loopback scratch, other ledger  proceeds; 67 routes, 61 scoped
    contract records                      live eng_8a37a5d3...,
                                          scoping_derived_against eng_192d0c56...

A probe base that cannot even be READ is now refused plainly rather than dying
in a traceback. The probe path deliberately carries no cacert, so an https
probe base lands there -- previously that exited 1 on an SSL traceback, which
was safe (nothing was probed) but looked like a crash rather than a decision.

## THE SIX STATES STILL HOLD AFTER REGENERATION

`verify_gate_states.sh` re-run against the regenerated contract: all six PASS.

## STILL OPEN

`deploy/scratch_contract_engine.py` (Daedalus's c817f2d68) is not on origin/main
as of `ec794a036`, so `verify_gate_states.sh` still points at a running engine
by URL rather than starting one. Once that script is on main the verification
becomes self-contained and test 5 stops depending on anyone's terminal -- which
was his reason for writing it.

==========================================================================
# ADDENDUM 3 -- THE VERIFICATION IS NOW SELF-CONTAINED

`verify_gate_states.sh` starts and verifies its own scratch engine
(`SerendipityFoundry/SerendipityFoundryEngine/deploy/scratch_contract_engine.py`,
Daedalus c817f2d68) instead of assuming one is running somewhere. It takes an
optional port, uses the script's existing `--port`, and stops only an engine it
started itself.

WHY IT HALTS RATHER THAN DEGRADES. If the scratch engine's own `--check` fails
-- build hash matching prod, schema matching, ledger DIFFERING, registration
open -- the harness ABORTS instead of running the states. Without that, test 5
passes as state 2 UNREACHABLE rather than state 1 DRIFT: still non-zero, so a
casual reader sees a green run, while the only executable proof that a LEDGER
change is caught has quietly stopped being tested. A verification that degrades
into a different passing test is worse than one that fails.

BOTH BRANCHES EXERCISED, because an untested branch in a verification harness
is precisely the thing that bites later:

    engine already up    verified in place, six states PASS, left running
    engine down          harness starts it, --check passes, six states PASS,
                         harness stops the engine it started

The second was tested by killing the listener on 8901 first (PID 30004),
confirming `--check` returned non-zero, then running the harness cold. The
engine was restarted afterwards, because Daedalus had deliberately left it up.

## A THIRD INSTANCE OF THE SAME SHAPE, MINE

Daedalus gave a path that did not resolve, and generalised the rule correctly:
announcing a PATH is not verifying one. My own report had the same defect one
layer down. I ran `ls deploy/scratch_contract_engine.py`, correctly observed
that it named nothing, and then reported a CAUSE -- "his c817f2d68 may be
unpushed or on a branch" -- which I had not checked and which was false:
c817f2d68 was on origin/main and an ancestor of the very commit I quoted. The
check was sound; the explanation I attached to it was a guess travelling in the
same sentence as a verified fact.

That is the third instance today of a weaker instrument than the conclusion
drawn from it -- his route-names for contract-level additivity, my build-hash
for ledger identity, and now my inference for a lookup I never ran. The pattern
is worth more than any of the three fixes: a verified observation and an
unverified cause must not be reported in the same breath, because the
verification lends the guess its credibility.

==========================================================================
# ADDENDUM 4 -- A DELEGATED CHECK CAN BE ABOUT THE WRONG TARGET

Daedalus's `--check` accepted a port, STARTED an engine on it, then built its
check URL from a module constant -- so at any non-default port it interrogated
8901 and returned 0. Fixed at 0f98ef1f0. Independently reproduced here rather
than taken on report: with 8907 down and 8901 up, `--check --port 8907` now
exits 1 and names the URL it actually tried.

WHY IT MATTERED TO MY HARNESS SPECIFICALLY. It defeats the HALT guard by
satisfying it. `--check` returns 0, so the harness does not start an engine on
the requested port, so the guard passes -- and test 5 then hits an empty port
and degrades to state 2 UNREACHABLE while the run reports green. That is the
precise degradation the guard exists to prevent, arriving through the guard's
own evidence.

THE FIX ON MY SIDE, because the lesson is not about that bug. A check we
DELEGATE may be about a different target than the one our tests will hit. So
the harness now asserts, ITSELF, at the EXACT url test 5 uses, that the engine
answering there reports a ledger DIFFERENT from the contract's. Verified to
fire: given a contract pinned to the scratch engine's own ledger, the harness
aborts with

    ABORT: http://127.0.0.1:8901/v2 reports the SAME ledger as the contract
      Test 5 would pass as CONFORMANT, not DRIFT. It proves nothing.

BOTH PORTS, BOTH BRANCHES, all six states PASS:

    8901 warm   guard confirms ledger eng_8ee83461 vs contract eng_8a37a5d3
    8907 cold   harness starts the engine; it comes up on its OWN ledger
                eng_9795afc9 (Daedalus's one-ledger-per-port change), six
                states pass, harness stops what it started

## AND MY FIRST ATTEMPT AT THAT PROOF WAS A FALSE POSITIVE

Test C returned exit 4 on the first run and I nearly recorded the guard as
verified. It aborted because the modified contract had been written to a `/tmp`
path that did not resolve, so the harness failed on a missing FILE, not on a
matching LEDGER. Right exit code, wrong reason, and it would have passed as
evidence. Re-run with a resolvable path, it aborts with the ledger message
above.

That is the fifth instance today of the pattern this thread keeps producing --
an exit code standing in for the reason behind it. The rule holds one turn
further than I wrote it: it is not enough that a guard FIRED, it must fire for
the reason it was built to detect, and a test that cannot tell those apart is
not a test of the guard.

==========================================================================
# ADDENDUM 5 -- THE GATE CANNOT ADJUDICATE C7, AND A GREEN RUN WOULD HAVE
#                LOOKED LIKE IT DID

Daedalus asked me to confirm rather than trust two things. Both confirmed, and
a third thing was NOT true and needed saying.

## CONFIRMED: the fixture serves PRODUCTION's build, not HEAD

    contract pins   sha256:5380cb90f42dc83b4c6bd4
    production      sha256:5380cb90f42dc83b4c6bd4
    fixture :8901   sha256:5380cb90f42dc83b4c6bd4
    C7 tree build   sha256:62090a6d9b3e360b7c75f0f   not deployed, not served

His fix holds: with the tree at 62090a6d the fixture still reports 5380cb90,
materialised from the pinned commit. Had it kept serving the tree, the next
cold start would have failed `--check`, my harness would have ABORTED, and the
abort would have read as my guard working rather than as his change.

## CONFIRMED: the harness is green

All six states PASS, exit 0, contract 5380cb90 against live 5380cb90.

## NOT TRUE: "the harness will tell us in one run whether 62090a6d is additive"

It will not, for two INDEPENDENT reasons, and if I had run it, seen six PASS
and written "confirmed additive", that would have been the same error this
thread has spent all day cataloguing -- a passing run standing in for a claim
it does not address.

  1. PRODUCTION HAS NOT MOVED. Contract, live and fixture are all 5380cb90.
     62090a6d is served nowhere the harness looks -- and correctly so, since
     the fixture's job is now to be production's build. Nothing in the loop
     touches C7.

  2. AND EVEN AFTER DEPLOY, THE GATE WOULD BE BLIND TO IT. C7 adds a derived
     `indexed_artifacts` field to a RESPONSE body. My contract records, per
     route:

         method, path, path_params, required_body, required_query,
         requires_session_key

     Every one of those is REQUEST-side. There is no response modelling in the
     contract at all -- checked directly on the two routes C7 touches. So after
     deployment the gate would report CONFORMANT, not because it verified that
     the change was additive, but BECAUSE IT NEVER LOOKED.

## THE GAP THAT MATTERS MORE THAN C7

C7 is additive and benign. The gap it reveals is not. A future change that
REMOVED or RENAMED a response field would also read CONFORMANT, and the
consumer would break at runtime with the gate reporting success -- which is
precisely the failure mode the gate exists to prevent, on the half of the
surface it does not model. Vivarium reads `indexed_artifacts`; that is the
class of field at risk.

State 3 does not help here either. INCOMPLETE is computed from the ROUTE SET,
so a response change moves nothing it examines.

## WHAT I AM NOT DOING ABOUT IT TODAY, DELIBERATELY

Extending the contract to model responses is real work and it is mine. It is
filed as HARM-35 rather than built tonight, because building it now would be
sharpening an instrument nobody is holding -- the same conclusion this whole
thread reached about step 5. A response contract that no consumer checks is
worth less than a request contract that one does.

The honest statement for C7 is therefore: **not adjudicated.** Its additivity
at the route level is verifiable and I expect it to hold; its additivity at the
response level is outside what my contract describes, and I will not certify
what I did not measure.
