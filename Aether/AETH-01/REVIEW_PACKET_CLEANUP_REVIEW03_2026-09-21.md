+======================================================================+
| AGE / AETH-01 -- REVIEW 03 CLEANUP REPAIR AND B3 HANDOFF               |
| Author: Augment Agent / Astra reviewer; Windows workstation + WSL    |
| Date: 2026-09-21                                                     |
| For: HITL operator and adversarial external reviewers                |
| Status: READY_FOR_ASTRA_CLOSURE_REVIEW                                |
| Admission hold: B3_OPERATIONAL_EVIDENCE_REQUIRED                      |
| Self-contained: no repository access needed to critique the claims  |
+======================================================================+

----- 0. Verdict and mandate -----

N1 and N2 are repaired under the declared bounded/trusted-storage contract.
The required counterexamples fail closed in offline tests. Recommend external
closure review, NOT unconditional acceptance or R1 admission. No provider calls,
paid instances, deployment, image build/push, GPU execution or physics changes.
Provider spend in this round: $0. B3 operational proof remains outstanding.

----- 1. Provenance and implementation -----

Repository: jcraig949jfi/Prometheus.
Branch: aether/base-role-adopt-2026-09-19.
Reviewed baseline: c6719c1beaad5d9c82f9bbe2eacd7b8417d2f07d.
Implementation: d5ffef03910f7ed2e18ae053e0823691b330dbb0.
Exactly 11 files: model amendment, three production modules, README, five test
modules and one reference oracle. The amendment was written before N1/N2 code;
it was committed WITH the tested implementation, not before measurement.
This packet is a separate follow-on commit. Earlier packets remain historical.

----- 2. Failure shapes -----

N1: after ACK plus two absence scans, a known pod could stop receiving GET.
LIST stayed empty while GET would return RUNNING at t=1800. A purported clean
3600-second window could therefore miss a directly observable contradiction.
N2: a valid old local report A could be combined with reaper evidence even
after newer authoritative durable controller state B contained live evidence.
Validating only the supplied report cannot discover an omitted newer report.

----- 3. N1: dual-endpoint falsification -----

Each qualifying round now requires complete LIST and GET of EVERY known reaper
ID, including confirmed IDs. LIST discovers unknown duplicates; GET challenges
known cleanup. RUNNING demotes confidence, resets coverage and retries DELETE
in the same round. Any exact-owned positive, even TERMINATED, resets coverage.
Transport/auth/schema failures invalidate the round. GET 404 is MISSING, not
an absence witness; only complete LIST contributes absence. Identity conflict
blocks deletion. Unrelated resources never become cleanup targets.

No qualifying sample is published until all required GETs finish. In-flight
checkpoints have reconciled=false without erasing healthy prior progress.
Legacy LIST-only states/reports are refused via LIST_AND_KNOWN_GET_V1; adding
that label manually is not migration. Obtain a fresh dual-endpoint horizon.

----- 4. N2: Option C, authoritative post-window local seal -----

The combiner requires the ORIGINAL authoritative run directory. Under the
same exclusive RunLock held throughout launch/recovery, it reloads plan/state,
requires DONE, verifies the local report's canonical state SHA-256 AND replayed
contents, evaluates the reaper evidence and atomically writes cleanup_seal.json.
The seal binds state, both reports and sealing UTC. It makes no provider calls.
Missing/offline source, stale A versus durable B, contention, unfinished state,
future report time, hash/content mismatch or failed seal persistence refuses.
Fresh B containing RUNNING yields unresolved, not confirmation.

The new combine CLI exposes this workflow. The pure shared-policy evaluator
cannot establish freshness and returns authoritative_local_state=false.
Later controller activity requires fresh aggregation; later evidence overlapping
the window requires a fresh horizon. A saved seal is point-in-time evidence,
NOT standing authorization. Hashes cannot authenticate a copied/rolled-back
directory. B3 must enforce one original directory and lock-obeying writers;
if that authoritative host is unavailable, operational aggregation must refuse.

----- 5. Independent oracle and claim ceiling -----

The 91-line offline oracle imports only math.isfinite, not production policy.
Its 64 tests include 12 instrumented reaper comparisons across missing, live,
terminated, GET failure, conflict and LIST failure at t=1800/t=3600. Traces come
from fake endpoint outputs, not production window counters or policy samples.
Additional checks cover omitted probes/IDs, clocks, gaps, freshness, ordering,
later contradictions and stale report hashes against actual durable bytes.

This is a necessary-invariant oracle, not a complete independent implementation
of ownership, ACK replay, journal durability or billing. It needs the complete
known-ID union and an authoritative current-state hash supplied by its caller.
Two equally stale caller-supplied hashes cannot reveal unseen state B. Shared
production policy still carries common-mode risk. Neither oracle agreement nor
HMAC arming establishes deployment independence, provider truth or billing stop.

----- 6. Executed validation -----

Combined Windows suite: 653 passed, 2 skipped, 74 subtests passed; 86.27s; exit 0.
Included test_aeth01_{cleanup_evidence,age_controller,independent_reaper,
cleanup_oracle,runpod_api,deployment_package}.py under Aether/test/.
Invocation: python -B -m pytest [those six paths] -q -p no:cacheprovider.
The oracle's 64 passes are INCLUDED in 653, not additional passes.
Package rerun: 7 passed, 2 skipped; exit 0. Skips are Linux bash runtime cases.

Ubuntu 24.04 WSL stdlib smoke: 5 checks passed; exit 0. Synthetic healthy hour
with every known GET; live reappearance/deletion at t=1800; atomic reload;
controller-lock exclusion/release; independent-oracle acceptance/falsification.
Linux pytest is unavailable; this is not a full Linux-suite claim. No whole
physics-suite rerun is claimed for Review 03. git diff --check passed.
The required crash-before-final-GET, stale A/durable B, bidirectional lock
exclusion and failed seal-write regressions are included in the Windows suite.
A delegated final validation attempt returned no result; no independent review
verdict is inferred from it. Parent inspection and executed tests are the evidence.

----- 7. Timing and remaining B3 proof -----

Require >=6 samples, UTC AND monotonic span >=3600s, gaps <=60s and adjacent
clock-delta disagreement <=2s. Failure, owned visibility, excessive gaps and
clock discontinuity reset coverage. Restart preserves histories, not credit.
At 10s polling, 361 healthy rounds in ONE invocation are needed ideally.
Cutoff means forced-cleanup start/deadline, NOT billing cessation. Confirmation
is no earlier than cutoff plus the post-cleanup horizon, later after resets.
Charge-reconciliation completion is a separate provider/accounting event.

Next, only with separate authorization: independent host/scheduler deployment,
durable handoff, usable LIST/GET/DELETE credentials, sustained horizon, actual
controller-host-loss rehearsal, alerts and tested operator fallback. Preserve
the authoritative directory contract. Keep Linux/image/provider/cutoff gates
and run-specific paid approval explicit. No scientific qualification was reopened.
For any review-driven change, update regression tests and execute them again.

----- 8. Questions designed to resist agreement -----

Can a completed-looking checkpoint evade an unperformed known-ID GET?
Can trusted entry points publish newer local facts without changing durable state?
Is original-directory authority enforceable during real controller-host loss?
Is the oracle's necessary-only ceiling adequate before a bounded R1 canary?
Is this operational burden disproportionate enough to retire the approach?

----- 9. Artifacts and dissemination -----

Aether/AETH-01/CLEANUP_EVIDENCE_MODEL.md and this Review 03 packet.
Aether/runpod/aeth01_canary/: age_controller.py, independent_reaper.py,
cleanup_evidence.py, README.md.
Aether/test/: five changed test modules named in section 6, except runpod_api
which was tested unchanged; reference/cleanup_aeth01_oracle.py.
Evidence Wiki lookup/publication blocked by unavailable client dependency.
No Wiki submission or canonical acceptance is claimed. Packet publication is
separate from external approval. Recommendation remains closure review + B3 hold.

+=============================== END ==================================+
Retirement, redesign and "not worth continuing" remain first-class answers.