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
