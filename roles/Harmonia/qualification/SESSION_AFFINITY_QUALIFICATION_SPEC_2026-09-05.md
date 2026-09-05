# Cross-engine session-affinity qualification — PRE-REGISTRATION

**Seat:** Harmonia (M1)
**Frozen:** 2026-09-05, BEFORE the mechanism was deployed anywhere.
**Harness:** `roles/Harmonia/qualification/session_affinity_qualification.py`
**Charter:** `roles/Mnemosyne/prompts/CHARTER_SESSION_AFFINITY_PROVENANCE_2026-09-05.txt`
**Companion (Mnemosyne, PEW side):** `evidence_wiki/docs/EXECUTION_LINEAGE.md`

This document is the frozen bar. It is written before the engine change is
committed so that the verdict cannot be fitted to whatever the engine turns
out to do. If a gate below is later found to be mis-specified, the correction
is a new dated document citing this one — the frozen gate is never edited in
place, because that destroys before/after comparability.

## 0. What is being qualified, and what is NOT

QUALIFIED HERE: that a client which wanders between two live engines mid
experiment is *stopped*, *told which engine owns its session*, and *leaves no
evidence artifact that misrepresents where the work happened*.

NOT QUALIFIED HERE: that the mechanism is secure against an adversary who
holds a valid session key. Session keys are bearer material; anyone holding
one can act as that session by construction. This battery tests *misrouting*,
not *theft*.

NOT QUALIFIED HERE: fleet behaviour beyond two engines. Every gate is run on
an M1/M2 pair in both directions. A three-engine allocator is future work and
nothing here should be read as evidence about it.

## 1. Independence

The charter says to run the failure case rather than trust Daedalus's packet.
Accordingly:

- The harness does not import `sfe`. It speaks HTTP to two live engines.
- Expected wire behaviour is asserted from THIS document, not read out of the
  engine at run time.
- Every control is computed from a LIVE response. No control may be derived
  from a static expectation table and then reported as verification — that
  defect (NB-6) was found in the PEW battery's own S2 gate on 2026-09-04 and
  must not be reproduced here.
- Engine identity is read from the engine that ANSWERED, never from the URL
  that was dialled, never from a hostname map.

## 2. Three-valued gates

Every gate returns exactly one of:

    PASS            the preconditions held and the observed behaviour matched
    FAIL            the preconditions held and the behaviour did not match
    INDETERMINATE   a precondition did not hold; the gate could not fire

INDETERMINATE is never counted as a pass and never counted as a failure. A
gate whose precondition did not hold has measured nothing.

## 3. Eligibility, computed before the run

The harness prints an ELIGIBLE COUNT before executing any gate: how many of
the N gates below can fire against the two engines as they are right now.

The controlling precondition is engine schema version:

    schema >= 5 on BOTH engines   -> affinity gates are eligible
    schema  < 5 on EITHER engine  -> affinity eligible count is 0

With an eligible count of 0 the verdict is `NOT_RUN`. It is NOT `PASS` and it
is NOT `FAIL`. A battery that cannot fire has not tested anything, and reading
a clean exit as a clean result is how a preregistered gate becomes decorative.

## 4. Verdict rule (frozen)

    NOT_RUN                preflight aborted, or eligible count is 0
    NOT_QUALIFIED          one or more eligible gates FAILED
    QUALIFIED_WITH_GAPS    no FAIL, every eligible gate PASSED,
                           at least one gate INDETERMINATE
    QUALIFIED              no FAIL, no INDETERMINATE, all gates PASSED

`QUALIFIED_WITH_GAPS` must name every INDETERMINATE gate and its reason in the
report. A gap that is not named is a false clean result.

## 5. Preflight (P) — read-only, fail-fast, before any write

    P0  both engines answer /v2/version
    P1  both engines' schema_version, engine_source_hash, source_commit recorded
    P2  ELIGIBILITY: schema >= 5 on both
    P3  engine_instance_id read LIVE from each engine and the two DIFFER
    P4  each engine's live identity matches the operator's --expect-*-engine
        value, when one was supplied; INDETERMINATE when not supplied
    P5  harness provenance recorded: repo HEAD, tree dirtiness, sha256 of the
        harness file itself

**P3 is an abort, not a gate.** If the two URLs return the same
`engine_instance_id`, the run stops before a single write. Two engines sharing
one identity is either a split brain or a misconfigured target, and in both
cases writing into them contaminates the very evidence the battery exists to
produce. The precedent is NB-7, 2026-09-04: a battery pointed at the wrong
host correctly reported FAIL, did not fail fast, and wrote test rows into the
wrong machine anyway.

## 6. Sequence gates (S) — the charter's ten steps

Run twice: once with HOME=M1/FOREIGN=M2, once reversed. A gate must hold in
both directions; a gate that holds in one direction only is a FAIL, reported
with the direction that broke.

    S1  session created on HOME returns a session key, the engine instance id,
        and affinity_mode=STRICT
    S2  the key's own bytes claim HOME's engine instance id (parsed client-side
        without asking any engine — this is what lets a wrong engine answer
        from the key alone)
    S3  a real evidence-bearing event is produced on HOME: hypothesis ->
        committed experiment -> observation, with its ledger anchor captured
    S4  that anchor binds in PEW: verified true, with HOME's engine instance id
        and session id recorded as lineage
    S5  the SAME key and world id sent to FOREIGN is refused with the
        machine-readable code WRONG_SESSION
    S5b the refusal is NOT 404 and NOT 500: FOREIGN must distinguish "wrong
        machine" from "missing data" and from "something broke"
    S5c the refusal names both the claimed and the answering engine instance id
    S5d FOREIGN holds no trace of the rejected operation: the world id does not
        exist there, and FOREIGN's ledger head is unchanged across the attempt
    S6  PEW produces no misleading artifact for the rejected operation: either
        the write is refused, or it is recorded as a failure — never a fossil
        that verifies
    S7  the client returns to HOME and the next operation succeeds
    S8  every fossil for the experiment carries ONE engine instance id and ONE
        session id; the chain shows a single lineage
    S9  a genuine, cryptographically real anchor produced on FOREIGN cannot
        close the HOME chain

S9 is the one that matters most. S5 proves the engine says no. S9 proves that
saying no was not the only thing standing between us and a false closure.

## 7. Anchor-verification gates (V) — charter A–H

    VA  correct exp + obs + correct session/engine     -> verify TRUE
    VB  correct exp + obs, WRONG session (same engine) -> verify FALSE
    VC  correct exp + obs, session from OTHER engine   -> verify FALSE
    VD  correct session, WRONG exp                     -> verify FALSE
    VE  correct session, WRONG obs                     -> verify FALSE
    VF  random session fingerprint                     -> verify FALSE
    VG  replay of pre-session (LEGACY) evidence        -> explicitly handled;
                                                          never fabricated into
                                                          strict provenance
    VH  restore/migration continuity                   -> matches the policy
                                                          in EXECUTION_LINEAGE
                                                          section 6

Known blocker at freeze time, from EXECUTION_LINEAGE section 4: SFE does not
yet assert `binds_session`. VB and VC therefore have a documented
INDETERMINATE branch — `INDETERMINATE_BLOCKER_B1` — and the harness must take
it rather than passing them on `binds_engine_instance` alone. VB in particular
is a same-engine test: `binds_engine_instance` cannot discriminate it, so a VB
that reports PASS while B1 is open is the harness lying to itself.

VD and VE are the already-qualified C4b shape (a wrong-but-real anchor) and
are expected to hold on today's engine. They are included as the positive
control on the instrument: if VD/VE ever fail, the battery is broken, not the
engine.

## 8. Safety rails

- Nothing writes without `--go`. Default is PLAN: unauthenticated GETs only,
  print the ordered plan and the eligibility determination, exit `NOT_RUN`.
- No raw session key is ever logged, written to the ledger, or sent to PEW.
  Anything matching the session-key shape is replaced by its `sfp_` fingerprint
  before it can reach a file. PEW refuses such a value at the API anyway
  (422 `session_key_must_not_be_sent_to_pew`); the harness must not rely on
  that refusal as its only defence.
- All PEW writes carry `"namespace": "test"`.
- Preflight abort happens before the first write, not after.

## 9. Output

    <out>/affinity_qualification_results.json   gates, verdict, eligibility
    <out>/affinity_qualification_ledger.jsonl   every HTTP exchange, redacted

The verdict ships in the same commit as the ledger. A verdict without its rows
is an assertion.
