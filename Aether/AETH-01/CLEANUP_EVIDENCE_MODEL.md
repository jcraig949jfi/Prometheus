# AGE cleanup evidence policy v1 -- specified before implementation

Scope: the cleanup-only repair of c2b31062b. No physics, scientific freeze,
paid run, or operational deployment is authorized. Historical packets remain
unchanged. This policy separates three propositions, not three aliases:

1. KNOWN_OWNED_CLEANUP: sufficient current evidence for every known exact-owned ID.
2. RECONCILIATION_WINDOW: a completed healthy bounded observation horizon.
3. OPERATIONAL_CLEANUP: validated agreement of both evidence sources plus (1)+(2).

## Per-pod state machine

Ownership requires exact ID/name/image/run-environment binding. A similarly
named or partially matching pod is not owned, is not deleted and does not
demote this run. A different object returned at an already-owned ID remains
an ownership anomaly. All exact-owned duplicate IDs must be retained/cleaned;
multiple exact-owned IDs are a discovery, not a permanent bar to later cleanup.

Each positively owned ID has an append-only, secret-free event history with
sequence order and UTC observation timestamp. Events: DELETE_ATTEMPT,
DELETE_RESULT, OBSERVE (allowlisted provider status), ABSENT_SCAN (complete
inventory only), MISSING (ambiguous per-ID GET), UNKNOWN (failed GET).
An OBSERVE event records whether it contradicts earlier cleanup evidence.
No raw pod objects, environment, headers or exception strings are recorded.

Current facts are replay-derived: last visibility/status/time; current DELETE
acknowledgement; current positive termination; consecutive corroborating
absence scans; live contradiction; current confidence. Historical facts include
every DELETE attempt/result and every positive TERMINATED observation.

- TERMINATED: current positive termination and CONFIRMED known cleanup.
- Any other/unknown positively visible status, including PROVISIONING,
  STARTING, RUNNING, EXITED and ERROR: clear CURRENT termination/ACK/absence
  evidence; confidence UNRESOLVED; re-enable DELETE. Preserve all history.
- ACK_204: positive deletion acknowledgement in this visibility epoch, NOT
  termination by itself. Unknown/None return values are never coerced to ACK.
- A complete inventory scan not seeing an acknowledged ID adds one absence
  witness. Two such scans after ACK can confirm known cleanup. Per-ID 404 is
  not a witness. Reappearance resets this evidence, including the old ACK.
- Failed/partial inventory cannot add any absence witness. Positives from
  pages already received must still be retained and cleaned.

Historical evidence accumulates; current confidence rises AND falls. Consumers
must replay histories rather than trust cached confidence fields or status labels.

## Run-wide state and healthy observation policy

Retain manifest/run binding, creation/reconciliation obligation, all known IDs,
unresolved IDs, per-pod histories, discovery/interruption history and controller/
reaper states. A run with zero known IDs has vacuously clean KNOWN resources,
but still requires the entire window; it is never clean from emptiness alone.

A qualifying sample is a fully successful inventory scan with NO exact-owned
pod observed (even a visible TERMINATED record resets the empty-window policy).
It must occur at/after the manifest cutoff. Local controller evidence cannot
waive the independently observed horizon.

Window facts: process/session identity; start/latest qualifying observation;
UTC and monotonic timestamp of each qualifying complete empty scan; count;
covered duration; reset reason; whether failure or owned discovery interrupted
the window. Preserve reset/discovery events separately; never rewrite history.

Choose RESET, not gap subtraction: inventory/auth/schema/transport/pagination
failure, any exact-owned positive, or a gap over 60 seconds between samples
resets the qualifying window to zero. A new complete empty scan begins a new
window. Six samples are a minimum, never a substitute for duration.
Qualification requires at least the manifest horizon (normally 3600 seconds)
of both UTC span and monotonic span, with every adjacent sample <=60 seconds
apart and their UTC/monotonic elapsed deltas agreeing within 2 seconds.
Thus an hour of blindness followed by 50 seconds of empty scans covers only
50 seconds. Samples at 0 and 3600 alone are insufficient; intervening healthy
observations are required. An owned discovery at 3500 restarts the horizon.

## Restart, persistence, clocks

UTC timestamps are the local host's timezone-aware wall clock, not provider
timestamps. Monotonic time measures elapsed observation spacing within one
invocation. No distributed clock or cross-host elapsed inference is attempted.

Conservative restart rule: every new sweep invocation starts a NEW qualifying
window. Per-pod histories and interruption/discovery history persist; prior
window progress is archived as history but never credited after restart. This
explicitly excludes all downtime and avoids inventing healthy elapsed time
from two wall-clock readings on opposite sides of a restart. The deployed
worker must sustain one invocation for a full horizon; repeated short sweeps
cannot finish it. A restart is safe but may delay operational confirmation.

Backward/nonfinite/malformed/future persisted timestamps fail validation or
reset qualification. An in-process large forward wall jump relative to
monotonic time resets the window; a large jump in BOTH clocks violates the
60-second sample-gap bound. No clock reading alone advances covered duration.
Preserve evidence after each provider interaction/scan via atomic fsynced
snapshots; a write failure makes the report unusable for confirmation but must
not suppress best-effort deletion. Only one CLI sweep may write an evidence
file at a time (advisory lock). Old evidence versions are refused explicitly,
not silently promoted; no paid runs exist requiring in-place legacy migration.

## Aggregation (fail closed)

Controller outcome and reaper report include the same exact manifest/digest,
run ID, owned IDs, per-pod histories and schema/policy version. The controller
also reports journal health and local cleanup. The reaper reports its full
window evidence, current interruption state and independent cleanup state.

The combiner recomputes manifest hashes, per-pod confidence from histories,
and window qualification from samples. Cached CONFIRMED strings are not proof.
It rejects absent/mismatched/malformed evidence and requires neither source
to report unresolved cleanup. Union all known IDs; do not lose IDs by trusting
only one source. A newer contradictory live fact blocks older confirmation.
The reaper window must postdate the controller's last provider evidence;
otherwise refresh observation instead of ordering incompatible snapshots.
At aggregation, require a recent latest sample (<=60s old, not future) so a
stale successful report is not silently reused. Local/refreshed evidence may
always force a new independent horizon; availability is subordinate to safety.

Output: KNOWN_OWNED_CLEANUP_CONFIRMED/UNRESOLVED;
RECONCILIATION_PENDING/COMPLETE; OPERATIONAL_CLEANUP_CONFIRMED/UNRESOLVED.
REAPER_CLEANUP_CONFIRMED is derived only when known cleanup AND the healthy
window qualify; a quickly deleted pod leaves reconciliation PENDING.

## Meaning and required falsifiers

Confirmation means cleanup according to this declared bounded reconciliation
policy. It does NOT prove the provider can never reveal a duplicate later,
nor that billing has stopped. Independent deployment, scheduler/credential
proof, operator fallback and charge reconciliation remain separate B3 work.

Tests must cover the 20s/3600s failure; TERMINATED->RUNNING; ACK->absent->
absent->RUNNING; TERMINATED->absent->RUNNING->TERMINATED; unrelated/partial
matches; hour-blind/50s burst; healthy 3600s sampling; t=1800 failure; t=3500
owned discovery; partial pages retaining positives; permission loss; restarts
after each evidence state; wall/monotonic jumps; forged/stale aggregate labels.

## Review 03 amendment -- dual endpoints and authoritative local seal

Specified against c6719c1be before the N1/N2 implementation. No physics,
deployment, image build or paid canary is authorized by this amendment.

N1: each qualifying sample requires complete LIST plus GET of EVERY known
reaper-owned ID, including currently confirmed IDs. LIST discovers unknown
duplicates; GET attempts to falsify cleanup of known IDs. An exact-owned
GET positive (even TERMINATED) interrupts the empty window. A live response
demotes current cleanup and re-enables DELETE in that round. Failed GET
(transport/auth/schema) makes the round non-qualifying. GET 404 is MISSING,
not an absence witness; only complete LIST adds absence evidence. A GET
identity conflict is an ownership anomaly, never a deletion authorization.
Do not publish a qualifying sample before ALL required GETs finish. Any
failure later in the round must invalidate it, including at persistence/crash
boundaries. The existing maximum-gap and restart rules remain in force.
Reaper reports/states require observation_policy=LIST_AND_KNOWN_GET_V1;
older LIST-only evidence is refused, never upgraded by adding a label.

N2 chooses Option C: post-window, point-in-time sealing under RunLock. The
operational combiner MUST receive the authoritative original run directory;
copied/offline directories are not authoritative. It acquires the same OS
lock held for the entire launch/recovery provider-interaction lifecycle,
loads the current durable plan/state, verifies the supplied local report's
canonical state SHA-256 and replay-derived contents, and evaluates the reaper
report while still locked. Local reports include their state hash and UTC
generation time. A later durable state B rejects report A even if A's own
histories and the reaper window look clean. Lock contention, missing source,
unfinished local state, hash/content mismatch or malformed evidence refuse.
Sealing itself performs NO provider calls. The returned seal binds state,
local report, reaper report and seal time; it is NOT a permanent certificate.
Any later controller activity requires a fresh locked aggregation; evidence
after window start forces a fresh horizon by the existing ordering rule.

The pure policy evaluator has no access to authoritative storage and cannot
establish report freshness. Its results are explicitly non-authoritative;
only the locked controller workflow supplies an authoritative local seal.
This is not a distributed authenticated store: B3 must preserve one original
run directory, restrict writers to lock-obeying controller entry points, and
invoke sealing there (or refuse while that authoritative host is unavailable).
Hashes detect mismatch, not malicious rollback/copying by a trusted operator.

Qualification adds an independent small test oracle, with no import of the
shared policy module, checking observed endpoint traces, healthy duration,
interruptions, all known IDs, later contradictions and controller ordering.
Required adversaries: empty LIST with known GET becoming RUNNING at t=1800;
GET TERMINATED/failure/404/conflict; current A then durable B plus stale A;
concurrent recovery/sealing. These are software tests, not B3 operational proof.

Operator timing: cutoff_utc means independent forced-cleanup start/deadline,
not billing cessation. Confirmation is no earlier than cutoff plus a full
post-cleanup reconciliation horizon; provider charge reconciliation is a
separate completion event. HMAC arming and shared-policy agreement retain
their previously declared provenance and common-mode limitations.