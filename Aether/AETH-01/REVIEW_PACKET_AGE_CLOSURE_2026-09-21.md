+======================================================================+
| AETHER AETH-01 / AGE: REPAIRED CONTRACT AND ZERO-DOLLAR CONTROLLER      |
| Author: Augment Agent / Astra reviewer; local Windows + Ubuntu WSL    |
| Date: 2026-09-21                                                     |
| For: HITL and independent external reviewers                          |
| Status: READY_FOR_ASTRA_CLOSURE_REVIEW                                 |
| Self-contained: no repository access needed to critique these claims |
+======================================================================+

----- 0. MANDATE AND VERDICT -----
Review baseline 507793b07c07aa7919f7983fcd041667f2da9aad, repair defects,
finish the local AGE-to-RunPod path, then perform one adversarial double-check.
No paid launch was authorized or performed. Recorded RunPod spend remains $0.
Target: READY_FOR_ASTRA_CLOSURE_REVIEW, not READY_TO_DEPLOY or a science PASS.
The $3 canary sub-cap is inside the $19.93 total policy cap. The latter is
operator-stated, not a live account balance or provider-enforced guarantee.

----- 1. WHAT WAS BUILT AND WHEN -----
Integration commit: 5683092b214bfa977e0e3d2a2104be8fd01f87a2 (33 files).
It contains the repaired Candidate-1 inference documents and fixtures, a
stdlib AGE plan/run/recover controller, structured RunPod v2 API client,
authenticated on-pod artifact service, corrected canary harness, package
guardrails and offline failure tests. Legacy launch/terminate scripts now
refuse with exit 1; there is no shell-launch fallback.
Changes and regression tests were developed together, tested in the worktree,
then committed. These are engineering regressions, NOT an independently
preregistered empirical campaign. No image was built or published.

----- 2. SCIENTIFIC CONTRACT AND CLAIM CEILING -----
The formal ladder is exactly five tiers:
1. STRUCTURAL_RESEMBLANCE
2. CAUSAL_VALUE_CONSTRUCTION
3. CONSTRUCTED_CAPACITY
4. RECURSIVE_CONSTRUCTION
5. HEREDITY_VARIATION
Mechanism qualifiers are separate from tiers. Both the inherited scaffold
and the attributable constructor set must remain visible in every report.
All current K3 fixtures are SEEDED_CONTROL, observed over four transitions.
They establish bounded discrimination cases, not spontaneous origin, general
heredity detection, recursive configuration construction or population results.

----- 3. SCIENTIFIC REPAIRS AND FALSIFIERS -----
Distributed fixture: A_opcode=(0,1) and A_arg0=(1,0) write distinct B=(1,1)
fields in the same tick on a 3x3 torus. C=(1,2), F=(2,1). Observed downstream
(C.payload,F.payload): both=(77,0), no opcode donor=(0,0), no routing
donor=(0,77), neither=(0,0). Credit belongs to {A_opcode,A_arg0}, not one A.
B's arg1=3, payload=77 and initial energy=10 are initialized scaffold;
donor configurations are also scaffold. Separate interventions perturb them.
Relay and activation labels now depend on winning writes, changed state and
behavior under content-only ablation, not hard-coded label inequality.
Controls actually perturb content, including an active cost/energy-matched
control outside the focal path. Matching is not universal environmental control.
A byte change from routing 1 to 5 still decodes EAST: byte causation alone
must not be promoted to behavior construction.
Recursive fixture: A activates B, B activates C, C writes D. Blocking B's
opcode-writing payload tests the second edge independently; intermediate
rescues expose the initialized machinery. Tier RECURSIVE_CONSTRUCTION must
carry RECURSIVE_ACTIVATION_OF_PRECONFIGURED_MACHINERY. Only opcodes were built.
Economics correction: isolated persistent template writer, no energy inflow,
outgoing energy transfer or replenishment. For w>0: N=0 if E<w; otherwise
N=1+floor((E-w)/(w+m)). E=23,w=3,m=2 gives FIVE pulses, not four, because
maintenance follows emission and floors at zero. For w=0 there is no
energy-limited exhaustion. Transfers or reconfiguration invalidate this formula.
Fixed-donor overwrite is donor-relative, not cumulative drift; this does not
prove independence of deterministic hash-keyed events across ticks.

----- 4. DEPLOYMENT DESIGN AS EXECUTED LOCALLY -----
plan is offline and reads no credentials. It binds a unique run ID, immutable
image digest, exact source hashes, hardware, quote, durations and result gate.
run requires a matching unexpired approval, explicit paid-execution flag and
operator attestation that an independent cutoff has already been armed.
No such cutoff was armed here. It is attested, not verified by this controller.
Maximum lifetime is 900s, compute timeout 600s, retrieval reserve 60s, cleanup
reserve 120s and boot/pull reserve at least 30s. Quoted lifetime cost must fit
half the canary budget; the cutoff must fit the full quoted budget window.
Ownership/create intent is journaled before exactly one POST. Lost responses
trigger paginated ownership reconciliation, never a blind POST retry. Recovery
is cleanup-only, allowed after approval expiry, and cannot upgrade science.
API v2 create expects 201; termination expects DELETE 204 then GET 404 or
owned TERMINATED. DELETE alone, EXITED or an unreachable service is not cleanup.
An independent artifact token protects the HTTPS port-8080 proxy. The API key
is not forwarded to the pod. Responses/artifacts are size-bounded, redirects
are refused, failures are sanitized and local deadlines are cooperative.
Final run-bound result.json, receipt.json and canary.log are collected before
normal deletion. Failures trigger best-effort salvage without blocking cleanup
indefinitely. The Linux service kills the compute process group on timeout,
then remains available for retrieval; the pod STILL BILLS until terminated.
GPU gate: actual CuPy, 200 single ticks + 20 trajectories x 5 intermediate
ticks = 300 matches, no mismatches, approved source hashes/run ID and final
finished result. NumPy PASS is smoke-only. Performance is not adjudicated.

----- 5. FINAL ADVERSARIAL DOUBLE-CHECK -----
Found and repaired three preventable cleanup gaps, all previously returning
CLEANUP_UNRESOLVED rather than false PASS:
(a) Expired recovery used the expired work deadline to stop after its first
    failed DELETE. Emergency retries now use a separate scheduling window.
(b) Inventory before known-ID deletion could consume the remaining lifetime.
    Known owned IDs now receive cleanup before further inventory scans.
(c) A later inventory-page failure discarded earlier positive ownership.
    Validated ownership is journaled as records arrive; later page failure
    cannot erase that evidence. Partial inventory never confirms cleanup.
Regressions exercise transient retry after expiry, deadline-crossing inventory,
lost-create/page-two failure and 100 duplicate owned IDs with slow deletion.
Duplicate discovery retains every ID for recovery; time limits may still leave
IDs unresolved. Cleanup is up to three rounds in a 120s cooperative scheduling
window, not hard preemption: in-flight calls can overrun. Lifetime overrun fails
the controller verdict even if the eventual deletion succeeds.
The integrated pass also repaired CuPy-incompatible seterr use, the documented
v2 cost-field check, oracle-bundle drift, intermediate trajectory comparison,
receipt/run binding, monotonic response/inventory checks and API/artifact-token
isolation. Offline sockets are forbidden in controller lifecycle tests.

----- 6. MEASURED VALIDATION -----
Focused scientific/NumPy differential/documentation run: 135 passed, exit 0.
AETH-01-only run: 442 passed, 5 skipped, 85 deselected, 92 subtests, exit 0.
Full Windows suite: 527 passed, 5 skipped, 92 subtests in 788.23s, exit 0.
The five skips cover Linux bash stubs/wrapper, POSIX special files and real
process-group termination; all were exercised in the separate Linux checks.
Ubuntu-24.04 WSL: pod-service suite 27 passed; API suite 34 passed; exit 0 each.
Linux runtime checks: both disabled shell stubs exit 1, stderr only, as required.
bash -n on all four package scripts: exit 0. Changed Python syntax and Git
whitespace checks passed. Suites overlap; these counts are NOT additive trials.
Reproduce from repo root: python -m pytest Aether/test -q -rs.
Linux: python3 -B Aether/test/test_aeth01_pod_service.py and
python3 -B Aether/test/test_aeth01_runpod_api.py.

----- 7. UNVERIFIED BOUNDARIES AND PROCESS HOLES -----
No Docker daemon was available: no image build, registry publication or image
digest-to-source verification. No GPU hardware or authenticated provider call
was exercised. The v2 wire shapes are documentation-informed offline fixtures,
not empirical confirmation of provider/proxy behavior. CuPy mocks are not CUDA.
Independent cutoff enforcement, current all-in pricing, actual account balance
and real billing/termination remain unverified. Local timers cannot bound an
unresponsive OS/network/provider; process exit does not stop billing. This is
a one-canary controller, not an account-wide budget reservation or scheduler.
Run journals require a durable private local filesystem and must not be copied
or reused. Provider eventual consistency and host loss remain cleanup risks.
K4/K5 population/audit work and K7/K8 remain deferred. Differential equivalence
cannot prove the scientific adequacy of a shared specification or input corpus.
Evidence Wiki consultation/publication is blocked: its Python client cannot
import requests in this environment. No Wiki submission is claimed; this
committed packet is the source artifact for later source-bound registration.

----- 8. DECISION AND NEXT GATES -----
Recommend closure review of THIS repaired artifact; do not launch RunPod.
After reviewer acceptance: build/inspect the image in an approved Docker
environment, verify immutable digest/source correspondence, arm and check an
independent cutoff, reconcile pricing/balance and obtain a separate run-specific
approval. Then, and only then, consider the $3 correctness canary; independently
verify termination/charges and preserve failure evidence. Add regressions for
new reviewer findings and rerun them plus the full suite before any paid step.

----- 9. QUESTIONS DESIGNED TO RESIST AGREEMENT -----
Can a causal activation chain still masquerade as recursively built machinery?
Do controls distinguish mechanism from energy/routing opportunity sufficiently?
What crash or provider-consistency sequence leaves a billed pod undiscoverable?
Is an operator-attested cutoff operationally credible, or should launch remain
blocked until cutoff enforcement has independent evidence?
Would this canary retire a meaningful uncertainty, or merely certify shared bugs?

----- 10. ARTIFACTS AND PROVENANCE -----
Baseline: 507793b07c07aa7919f7983fcd041667f2da9aad.
Integration: 5683092b214bfa977e0e3d2a2104be8fd01f87a2.
This packet is committed separately after integration; it is not part of the
scientific/runtime payload or the immutable image hash manifest.
Science: Aether/AETH-01/{HEREDITY_REQUIREMENTS,KILL_GATES_01,ECONOMICS,
OBSERVATORY,AETH01_REPAIRED_FREEZE_CANDIDATE}.md.
Deployment: Aether/runpod/aeth01_canary/{age_controller,runpod_api,
pod_service,run_canary}.py; README.md; receipt_schema.json; Dockerfile.
Tests: Aether/test/test_aeth01_*.py; reference/scientific_aeth01.py.
Budget/operations: Aether/AETHER_RUNPOD.md. Unrelated pivot files were untouched.

+=============================== END ==================================+
Retirement, redesign and "not worth continuing" remain first-class answers.
The principal danger is mistaking causally activated inherited machinery for
machinery whose useful configuration the world actually constructed.