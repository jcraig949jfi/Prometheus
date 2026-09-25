+======================================================================+
| AGE / AETH-01 -- CLEANUP EVIDENCE REPAIR AND OPERATIONAL HANDOFF       |
| Author: Augment Agent / Astra reviewer; Windows workstation + WSL    |
| Date: 2026-09-21                                                     |
| For: HITL operator and adversarial external reviewers                |
| Status: READY_FOR_ASTRA_CLOSURE_REVIEW                                |
| Admission hold: B3_OPERATIONAL_EVIDENCE_REQUIRED                      |
| Self-contained: no repository access needed to critique the claims  |
+======================================================================+

----- 0. Verdict and scope -----

The three reproduced cleanup-evidence defects are repaired and covered by
offline regression tests. This is engineering closure evidence, NOT R1
admission, operational deployment proof, a scientific freeze, or launch approval.
No authenticated RunPod call, paid instance, image build/publication, or live
scheduler deployment was performed. Provider spend in this repair round: $0.
Candidate-1 physics, scientific requirements and historical reviews are unchanged.

----- 1. Provenance: policy before implementation -----

Reviewed baseline: c2b31062b654a5ad7b3675ad426eb79d1b5ad23f.
Policy specification: 089d619e681a80161e912b0062fd4a332d2e1915.
Implementation/tests: e1d3d964103078275ede6500691d020107fff4b5.
Final combined-fault hardening: e801ec36d27427aedcd2292737a04570070702c4.
The policy was committed before implementation; this packet is a separate
follow-on commit. Implementation spans exactly eight cleanup, test and operator
documentation files; hardening touches two of those. No provider API or image
payload changed.

----- 2. Original failure shapes, not just verdicts -----

A: baseline reaper and label combiner reported operational cleanup at 20
seconds, although the manifest required a 3600-second reconciliation horizon.
B: TERMINATED followed by RUNNING stayed confirmed and attempted zero DELETEs.
C: after an hour of blindness, six empty scans spanning only 50 seconds
were accepted as satisfying a supposedly uninterrupted one-hour window.
These were reproduced offline before repair, not inferred from test counts.

The corrected endpoint is three separate propositions:
1. KNOWN_OWNED_CLEANUP: current evidence for every known exact-owned ID.
2. RECONCILIATION_WINDOW: full healthy independently observed empty horizon.
3. OPERATIONAL_CLEANUP: validated agreement of both sources plus 1 and 2.
An empty known set is vacuously clean for 1, never sufficient for 2 or 3.
The local controller still refuses local confirmation if it never found a pod.

----- 3. Per-pod repair -----

Shared stdlib policy retains append-only timestamped histories and replays
current facts. Positive TERMINATED is historical evidence, not irreversible
confidence. Any later non-TERMINATED visibility clears CURRENT termination,
DELETE acknowledgement and absence progress, demotes confidence and enables
DELETE again. Historical observations/results are retained. Unknown statuses
are treated conservatively; unknown DELETE returns never become ACK_204.

Known cleanup requires current positive TERMINATED, or current DELETE ACK_204
plus two complete absence scans. A per-ID 404 alone is not a witness. Partial
inventory contributes no absence but retains earlier exact-owned positives.
Every exact-owned duplicate is cleaned. Unrelated/partial matches do not
demote this run or become delete targets. An identity conflict at a known ID
blocks DELETE until fresh exact binding; the anomaly remains unresolved.

----- 4. Window, clocks and restarts -----

Choose RESET, not subtraction of guessed outage time. Full inventory failure,
any owned discovery (even TERMINATED), or sample gap >60 seconds resets the
window. Qualification requires >=6 samples AND >=3600 seconds, for the normal
manifest, of BOTH UTC and monotonic span. Adjacent gaps must be <=60 seconds;
adjacent UTC/monotonic elapsed deltas must agree within 2 seconds. Samples
must be at/after cutoff. An hour blind plus 50 observed seconds earns 50.

Each sweep invocation starts a new session and resets all window credit.
Pod histories and archived interruptions survive, but downtime earns nothing.
Repeated short cron jobs cannot finish this policy. At 10-second polling,
361 healthy scans in ONE invocation are needed in the ideal 3600-second case;
operational limits need headroom for resets and escalation on exhaustion.

Wall time is local UTC, not provider time. Monotonic time is per invocation;
no cross-host elapsed inference is attempted. Clock jumps reset progress;
future facts cannot establish operational confirmation and malformed histories
are refused. Atomic fsynced snapshots and a CLI single-writer lock preserve
facts across ordinary crashes. Journal or
runtime clock failure blocks success but does not gate best-effort deletion.
Missing timestamps are not invented. Such damaged evidence needs operator
remediation, not automatic confidence repair or hand-edited success labels.
Controller schema is now 3; reaper schema 2. Legacy schemas are refused.

----- 5. Aggregation and final double-check -----

The combiner validates matching manifests/digests, unions known IDs, replays
both histories and recomputes window coverage. Neither side may be unresolved
or have unhealthy journaling. The window must strictly postdate the local
controller's latest provider event. Latest sample age must be <=60 seconds
at aggregation and never future. Labels alone cannot establish confirmation.

Final adversarial checks found and repaired additional edges: a recorded GET
failure could coexist with a stale successful window; malformed runtime UTC
could abort before DELETE; controller recovery lacked the reaper's known-ID
identity-conflict deletion guard. Tests now cover these, including failed
DELETE facts during claimed coverage and live reappearance with a bad clock.
A final combined-fault check additionally hardened the controller conflict
guard against failed history recording, including recovery from that snapshot.
Two delegated validation attempts returned no result; no independent verdict
is claimed from them. The parent agent executed the substantive double-check.

----- 6. Executed validation -----

Final policy/controller/reaper: 510 passed in 66.77 seconds; exit 0.
Seven conflict-specific cases also passed before that rerun; exit 0.
Full Windows Aether suite at e1d3d9641: 877 passed, 5 skipped, 92 subtests passed in
496.48 seconds; exit 0. Command: python -B -m pytest Aether/test -q
-p no:cacheprovider. Package-only rerun: 7 passed, 2 skipped; exit 0.
Five Windows suite skips are Linux-specific; they are not counted as passes.
The later two-file combined-fault hardening reran all 510 affected tests,
not the full unrelated physics suite. Linux reaper code was unchanged by it.

Ubuntu 24.04 WSL stdlib smoke: 5 checks passed; exit 0. Checked advisory lock
exclusion/release, 20-second rejection, fsynced reload after a blind hour,
full healthy-hour confirmation, and TERMINATED->RUNNING deletion/history.
WSL pytest import failed (not installed); no full Linux suite is claimed.
All provider behavior in this round was fake/injected, not authenticated.

Regression coverage includes A/B/C; ACK->absent->absent->RUNNING;
TERMINATED->absent->RUNNING->TERMINATED; failures at t=1800 and t=3600;
owned discovery at t=3500; partial pages; permission loss; durable restarts;
wall/monotonic jumps; malformed/future histories; stale/forged summary labels;
persistence failure with continued deletion; and unrelated identities.

----- 7. Claim ceiling -----

Confirmation means evidence satisfies a bounded sampled policy. It does NOT
prove continuous provider visibility between samples, indefinite absence of
late duplicates, actual billing cessation, or truthful provider inventory.
Structured validation detects inconsistent facts/labels, not a malicious
writer fabricating an entirely consistent history. Report transport/storage
trust and clock synchronization remain operational responsibilities. The
shared policy also means controller/reaper logic is not independent diversity.
Passing physics regressions is no new scientific result or GPU qualification.

----- 8. Next gates, in order -----

1. External closure review of the repaired evidence model and implementation.
2. Separately authorized B3 proof: independent host/scheduler, durable handoff,
   usable list/get/delete credentials, sustained horizon, controller-host-loss
   rehearsal, alerts and tested operator fallback. An HMAC arm file proves
   manifest binding, NOT scheduler health, host independence or billing stop.
3. Explicitly authorized image build/identity verification and Linux validation.
4. Only after operational gates and run-specific approval: one bounded paid
   canary, with termination observation AND provider charge reconciliation.
5. Keep scientific instrumentation/qualification separate; no campaign grant.

Recommendation: accept cleanup repair for closure review; retain the B3 hold.
Update regression tests and rerun them for any review-driven change before
attempting an operational rehearsal. Stop if the independent cutoff cannot
be demonstrated; a local cleanup success is not an acceptable substitute.

----- 9. Questions designed to resist agreement -----

Can a newer live/failure fact evade window invalidation or current confidence?
Can a crash boundary lose ownership, or a conflict still trigger wrong deletion?
Is the 60-second gap/3600-second horizon a defensible provider policy at all?
Does shared-policy coupling defeat the intended independent safety argument?
Is the operational burden disproportionate enough to retire this path?

----- 10. Artifacts and dissemination -----

Under Aether/AETH-01/: CLEANUP_EVIDENCE_MODEL.md and this packet.
Under Aether/runpod/aeth01_canary/: cleanup_evidence.py, age_controller.py,
independent_reaper.py, README.md.
Under Aether/test/: test_aeth01_cleanup_evidence.py,
test_aeth01_age_controller.py, test_aeth01_independent_reaper.py,
test_aeth01_deployment_package.py.
Historical reviews/packets remain unchanged; this packet qualifies their
cleanup claims. Evidence Wiki read/publication blocked: client dependency
requests is unavailable. No Wiki submission or canonical acceptance claimed.

+=============================== END ==================================+
Retirement, redesign and "not worth continuing" remain first-class answers.