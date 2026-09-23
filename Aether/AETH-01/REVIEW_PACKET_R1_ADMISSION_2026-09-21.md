+======================================================================+
| AGE -- AETH-01 / R1 ADMISSION REPAIR PACKET                          |
| Author: Claude (Sonnet 5), Anthropic; Windows workstation + WSL      |
| Date: 2026-09-21                                                     |
| For: operator and independent external reviewers                    |
| Target disposition requested: see section 16                         |
+======================================================================+

## 0. Scope discipline

This is a bounded engineering repair round responding to
`Aether/AETH-01/ASTRA_CLOSURE_REVIEW_02.md` (verdict `REPAIR_BEFORE_R1`).
It does NOT redesign Candidate 1's physics, does NOT launch RunPod, and
did NOT spend money. No authenticated RunPod call, image publication, or
provisioning occurred. Astra's review document was not modified.

## 1. Provenance

| Role | Commit / state |
|---|---|
| Base commit (resumed from) | `c36bfc2b17b10e03f1f2781e5bb55b9bb1f533cc` |
| Controlling review | `Aether/AETH-01/ASTRA_CLOSURE_REVIEW_02.md`, verdict `REPAIR_BEFORE_R1` |
| B1/B2/B4 repair | `d68f76c1e` |
| B3 independent reaper | `b52f467a8` |
| Integer domain + K1 + text corrections | `bc1b4f828` |
| Image/build identity prep | `79e28fa3b` |
| New HEAD | this packet's own commit, on top of `79e28fa3b` |

Entry points: `Aether/runpod/aeth01_canary/README.md`,
`Aether/runpod/aeth01_canary/independent_reaper.py`'s module docstring.
**D/** = `Aether/AETH-01/`, **P/** = `Aether/runpod/aeth01_canary/`,
**T/** = `Aether/test/`.

## 2. Exact files changed

Modified: `P/age_controller.py`, `P/runpod_api.py`, `P/Dockerfile`,
`P/README.md`, `P/aeth01_cpu_oracle.py`, `T/reference/oracle_aeth01.py`,
`T/test_aeth01_age_controller.py`, `T/test_aeth01_runpod_api.py`,
`T/test_aeth01_kill_gates.py`, `T/test_aeth01_pod_service.py`,
`T/test_aeth01_deployment_package.py`, `D/PHYSICS_SPEC_DRAFT.md`,
`D/GPU_RUNPOD.md`, `D/ECONOMICS.md`, `D/HEREDITY_REQUIREMENTS.md`,
`D/KILL_GATES_01.md`.

New: `P/independent_reaper.py`, `P/image_manifest.py`,
`P/image_manifest.json`, `T/test_aeth01_independent_reaper.py`,
`D/REVIEW_PACKET_R1_ADMISSION_2026-09-21.md` (this file).

Not touched: `ASTRA_CLOSURE_REVIEW_02.md`, `ASTRA_REVIEW_01.md`, and every
other prior review/packet document (historical record, left as-is).

## 3. B1 repair -- termination evidence is never invented

**Defect (reviewed HEAD).** `runpod_api.terminate_pod()` collapsed DELETE's
real outcome into an undifferentiated `None`, and `age_controller._Lifecycle
.terminate()` swallowed the DELETE exception and then treated a bare GET-404
(`pod is None`) as proof of termination. An ambiguous 404 -- which the
official v2 `NotFoundError` documents as "not found OR not accessible to the
caller" -- was therefore sufficient, alone, to mark a pod `terminated_ids`
and let `finish_owned()` skip it forever.

**Repair.**
- `runpod_api.terminate_pod()` now returns `"ACK_204"` or `"NOT_FOUND_404"`
  explicitly (never a bare `None`); any other outcome raises `ProviderError`
  with `.status` (HTTP) or `None` (transport) preserved.
- Each owned pod now carries an explicit evidence record
  (`state["pod_evidence"][pod_id]`): `delete_attempted`, `delete_result`
  (`NONE`/`ACK_204`/`NOT_FOUND_404`/`HTTP_OTHER`/`TRANSPORT_UNKNOWN`),
  `last_visibility` (`UNKNOWN`/`NOT_VISIBLE`/`VISIBLE`), `last_status`,
  `positive_termination_observed`, `absence_confirmations`, and
  `cleanup_confidence` (`UNRESOLVED`/`CONFIRMED`).
- `cleanup_confidence` reaches `CONFIRMED` ONLY via (a) a positive
  `TERMINATED` observation on an owned GET, or (b) an acknowledged DELETE
  (`ACK_204`) corroborated by `POST_DELETE_ABSENCE_SCANS_REQUIRED=2`
  independent, fully-successful inventory reconciliation scans that do not
  observe the pod, with no intervening `VISIBLE` reappearance. A once-ACK'd
  DELETE followed only by ambiguous GET-404s, with no successful
  reconciliation scan ever run, stays `UNRESOLVED` forever locally --
  exactly the "loud, recoverable CLEANUP_UNRESOLVED" the review asked for.
- Reappearance always demotes: any later `VISIBLE` observation resets
  `absence_confirmations` to 0 and removes the pod from `terminated_ids`,
  re-enabling `finish_owned()` to retry it. `terminated_ids` can no longer
  become an irreversible graveyard from negative visibility alone.

**Falsifier regressions added** (`T/test_aeth01_age_controller.py`,
`T/test_aeth01_runpod_api.py`): DELETE transport failure then GET-404 then
later visibility return; DELETE non-ACK then GET-404 then later visibility
return; DELETE-ACK but still `RUNNING`; Pod `EXITED`; Pod positively
`TERMINATED`; recovery re-checking a previously-absent pod; persistent
per-ID GET failure that must not block LIST-based confirmation (route b);
DELETE `ACK_204`/`NOT_FOUND_404` never collapsed at the transport layer.
Executed falsifier: with the OLD collapsed-404 behavior removed, a
synthetic DELETE-fails-then-GET-404 sequence now yields
`LOCAL_CLEANUP_UNRESOLVED`, not a false `CONFIRMED` (verified by the
updated `test_delete_response_or_exited_status_alone_is_not_confirmation`
and the new `test_reaper_*`/`test_sweep_never_confirms_from_ambiguous_404_alone`
suites, controller and reaper sides respectively).

## 4. B2 repair -- ownership reconciliation is run-wide and unconditional

**Defect.** `adopt()` set `reconciliation_required=False` on any successful
create response, and `cleanup()` only called `reconcile()` when that flag
was true -- so a normal single-pod success path never listed inventory at
all (`T/test_aeth01_age_controller.py:346` in the reviewed HEAD explicitly
asserted `"LIST" not in events`).

**Repair.**
- `adopt()` no longer disarms reconciliation. `reconciliation_required`
  stays `true` in `state.json` for the whole run and is reported in
  `outcome()` as a durable, informational obligation -- never a "still need
  more scans this run" gate the controller can satisfy and forget.
- `cleanup()` now calls `finish_owned()` (delete already-known IDs, never
  delayed for inventory), then `reconcile()`, then `finish_owned()` again,
  unconditionally, every round (bounded by `CLEANUP_ROUNDS=3` /
  `CLEANUP_SECONDS=120`, unchanged).
- `owned_confirmed()` requires `bool(owned_ids)` to be true: a run that
  never positively owned anything (e.g. a lost create response) can NEVER
  be `LOCAL_CLEANUP_CONFIRMED` from empty scans alone, preserving the
  original code's conservative "no proof of absence from nothing found"
  invariant while still fixing the reconciliation-skip defect.
- `reconcile()`'s post-scan pass advances `absence_confirmations` only for
  owned pods that (a) were not observed in a scan that fully succeeded and
  (b) already have `delete_result == ACK_204`; a duplicate/ambiguous
  exact-owned pod sets `ownership_ambiguous`, which blocks `CONFIRMED`
  regardless of per-pod evidence.

**Falsifier regressions added:** successful-response duplicate (ambiguous
create with an exact-owned duplicate hidden across scans); duplicate
appearing only after a later scan; a formerly-believed-absent pod
reappearing; partial-page inventory failure preserving earlier positive
records; 100-duplicate bounded-time cleanup (`test_duplicate_inventory_
does_not_multiply_cleanup_time_without_bound`); unrelated same-name/
same-image/same-run-id-only partial matches never deleted
(`test_unrelated_pods_are_never_deleted`).

## 5. B3 -- independent cleanup-only reaper

New module `P/independent_reaper.py`, with no import dependency on
`age_controller.py` and no `create_pod` capability anywhere in its own code
path (`ReaperProvider` deliberately never exposes one --
`T/test_aeth01_independent_reaper.py::test_provider_has_no_create_capability`).

**Pre-create handoff.** `age_controller.create_plan()` now also writes
`reaper_manifest.json` (run id/name, immutable image, cutoff, reconciliation
horizon, budget context, creation-intent id) beside `plan.json`.
`independent_reaper.arm()` reads that manifest and produces
`reaper_ack.json`: `{armed, scheduler_id, cutoff_utc, acknowledged_at_utc,
manifest_sha256, manifest_hmac_sha256}`, HMAC-keyed with
`AGE_REAPER_SHARED_SECRET` (a third credential, distinct from the RunPod
API key and the artifact token, read only by `arm()` and by
`age_controller.run()`'s new `_require_reaper_armed()` gate).
`run()` now refuses to POST (`REAPER_NOT_ARMED`) unless that ack exists,
its manifest hash and cutoff match the exact plan, and its HMAC verifies --
stronger than an operator's Boolean attestation, because it is a file the
reaper process itself produced.

**Sweep.** `independent_reaper.sweep()` reimplements the same B1 evidence
bar independently (positive `TERMINATED` observation, or ACK'd DELETE plus
independent reconciliation absence), scans ALL inventory every invocation,
never retries CREATE (no such code path exists), revisits uncertain IDs,
and accumulates evidence across repeated invocations in a durable
`reaper_evidence.json`. "Confirmed, zero pods ever found" requires BOTH the
full announced `reconciliation_horizon_seconds` to have elapsed AND
`EMPTY_HORIZON_SCANS_REQUIRED=6` consecutive fully-successful empty scans
spanning it -- never a handful of scans in one process lifetime (the
review's explicit objection to "three potentially stale scans").

**Regressions (`T/test_aeth01_independent_reaper.py`, 20 tests):** ack/HMAC
round-trip and tamper rejection; confirmation via positive `TERMINATED`;
confirmation via ACK+reconciliation; never-confirms-from-ambiguous-404-alone;
a late-visible pod with NO returned create ID discovered and deleted purely
via inventory; reappearance resets absence and blocks confirmation;
unrelated pod never deleted; ambiguous duplicate owned pods never confirm
(both still deleted); partial pagination failure preserves positive
records and stays unresolved; the empty-inventory horizon gate; no secrets
or raw exception text in evidence; CLI `arm`+`sweep` round trip.

**Host-offline rehearsal (zero-dollar, required by review section 6):**
`test_host_offline_rehearsal_reaper_arms_and_later_deletes_without_
controller` runs `age_controller.create_plan()` to produce a real
plan/manifest, then NEVER calls `age.run()` at all (the controller host is
treated as dead from that point on); `independent_reaper.arm()` is called
using only the manifest file, its ack is verified independently by
`age_controller._require_reaper_armed()`, and `independent_reaper.sweep()`
(using only a fresh `Provider` double and the manifest -- no reference to
the controller's runtime/process/state) later discovers and deletes a
"late-visible" pod that was never given a create-response ID, reaching
`REAPER_CLEANUP_CONFIRMED`.

**Honest operational status.** This constitutes: reviewed reaper
code/configuration; a durable, HMAC-bound manifest/ack handoff the
controller enforces in code; and an offline rehearsal covering the
required fault scenarios (transient outage, 404/access loss, late
visibility, duplicate owned pods, pagination failure, stale manifest,
unrelated-pod protection, host-offline). It does **not** constitute a
truly independent, already-armed reaper running on separate physical/cloud
infrastructure with its own scheduler -- that cannot be established from
inside this coding session. See section 16's disposition.

## 6. B4 repair -- diagnostics preserve distinguishing evidence

**Defect.** Every non-`ControllerError` exception in `run()` collapsed to
`reason="CONTROLLER_FAILED"` with no further detail; HTTP 401, HTTP 422,
and a bare transport failure were indistinguishable, as were a stalled
service and a failed artifact proxy.

**Repair.** A new, closed, secret-safe diagnostic vocabulary
(`_DIAG_STAGES`: `AUTH_PREFLIGHT`/`CREATE`/`GET_STATUS`/`LIST_INVENTORY`/
`ARTIFACT_RESULT`/`ARTIFACT_RECEIPT`/`ARTIFACT_LOG`/`DELETE`/`RECONCILE`;
`_DIAG_OUTCOMES`: `SUCCESS`/`MISSING`/`ACK_204`/`NOT_FOUND_404`/
`HTTP_OTHER`/`TRANSPORT_UNKNOWN`/`SCHEMA_INVALID`/`POD_ERROR`/`POD_EXITED`)
is journaled to a bounded (`_DIAGNOSTICS_LIMIT=200`) `state["diagnostics"]`
list at every provider/artifact call site, recording only
`{stage, outcome, http_status, pod_status, elapsed_seconds, attempt}` --
never raw exception text, headers, provider bodies, or credentials.
`runpod_api.ProviderError` gained an optional `category="SCHEMA_INVALID"`
field so a malformed/unexpected provider response is coarsely distinguished
from a plain transport failure at the transport layer itself. The
top-level `reason` code remains a fixed, coarse string (unchanged
contract, still secret-safe); the diagnostics list is what preserves the
finer distinction the review asked for.

**Regressions:** `test_diagnostics_distinguish_auth_schema_and_transport_
create_failures` (401 vs 422 vs malformed-response vs transport, each
recorded with a distinct `outcome`/`http_status`); `test_diagnostics_never_
leak_secrets_or_raw_exception_text`; `test_diagnostics_are_bounded_and_
never_unbounded_growth`; `test_pod_error_and_exited_status_are_journaled_
distinctly`. An independent, bounded, documented operator/provider-log
diagnostic route beyond the artifact proxy remains open for the actual
supervised R1 (RunPod console/API log retrieval); this repair adds the
in-controller half of that requirement, not a new external log pipeline.

## 7. Integer-domain repair (section 6)

**Defect.** `Aeth01World.__init__` in both `P/aeth01_cpu_oracle.py` and
`T/reference/oracle_aeth01.py` checked numeric ranges (`0 <= value <= 255`,
etc.) without requiring an exact Python `int`, so `E=5, WRITE_COST=0.5`
was silently accepted (producing `E=4.5`), and fractional/NaN/infinite/
numpy-scalar/boolean values passed for seed, tick, the three uint8
parameters, the two 33-bit parameters, and every per-cell field.

**Repair.** A single `_require_int(name, value, low, high)` helper, added
at the byte-identical AST position in both files (verified by the existing
`test_cpu_all_executable_definitions_match_reference` parity test, which
still passes), rejects: any non-`int` (float, `str`, numpy scalar),
`bool` (explicitly, despite being an `int` subclass), and out-of-range
integers -- by raising, never truncating. Applied to `H`, `W`, `seed`,
`tick`, `write_cost`, `maintenance_cost`, `replenish_amount`,
`replenish_numer`, `mut_numer`, and every per-cell field (opcode/arg0/
arg1/payload/energy). `from_bytes()` is unaffected in its own right (it
already delegates to `__init__` for validation).

**Regressions:** existing `test_properties.py`/`test_mutants.py`/
`test_golden_vectors.py`/`test_differential_oracle.py` all still pass
unchanged (66/66); no physics changed. New negative cases were exercised
directly (fractional `write_cost`, `bool` for `H`, `float("nan")`/
`float("inf")` for `mut_numer`, numpy `int64`/`float64` scalars, an
out-of-range cell field) -- all now raise `ValueError` where they
previously would have been silently accepted or truncated.

## 8. Cheap scientific text corrections (section 7)

- **S03** (`D/PHYSICS_SPEC_DRAFT.md`): removed the claims that repeated
  fixed-donor overwrite can cumulatively random-walk a target through byte
  space, and that activation is a generic "approximately 1-in-8" event.
  Replaced with the donor-conditioned formula
  `(1-mu)*[p=1] + (mu/8)*[popcount(p XOR 1)=1]` (matching the review's
  independent derivation) and an explicit statement that a fixed donor can
  only ever place itself or one of its 8 Hamming-1 neighbors. K8 remains
  the real accessibility test; no test enforced the old phrasing
  (verified: no test in the suite matched the removed strings).
- **S05** (`D/GPU_RUNPOD.md`): the `DEAD_CERTIFIED` description no longer
  claims that zero `WRITE` cells plus zero rain alone certifies full-state
  absorption. It now states that precondition certifies only
  template/activity observables, and requires either
  `MAINTENANCE_COST=0` or that the maintenance tail has actually run to
  completion for a full-state certificate -- matching `HABITABILITY.md:52`
  (already correct) instead of contradicting it. New regression
  `test_s05_inert_world_still_decays_under_maintenance_before_floor`
  (`E=10, MAINTENANCE_COST=1`) demonstrates energy changes on the very
  next tick and only reaches a truly fixed state after
  `ceil(10/1)=10` ticks.
- **M03** (`D/ECONOMICS.md`, `D/HEREDITY_REQUIREMENTS.md`): removed the
  claims that energy must be acquired only by winning a transfer (direct
  rain refutes this), that a donor's donation can "drain" the recipient
  (every source debit is made before any target credit -- the recipient
  is only ever credited, never debited, by being a transfer's target),
  and that passive receipt (transfer-in edges, no structural-copy-out
  edges) alone establishes "parasitism." Replaced with neutral,
  measured-benefit/contribution and donor-reconfiguration language in
  both documents; the `HEREDITY_REQUIREMENTS.md` "Parasite" adversarial-case
  row is retitled and now requires the same behavior/outcome evidence as
  any other resource-mediated case, never edge-type presence alone. No
  test enforced the old phrasing.

## 9. K1 golden-vector repair (section 8)

`KILL_GATES_01.md`'s case 2 hand ledger assumed "P wins" (total 80), but
the executable seed=5 case actually selects Q (total 90); the prior test
derived its expected credit FROM the trace under test, so it passed either
way and never caught the mismatch. Independently computed (not derived
from the trace): `arbitration_priority(5, 0, target=(0,1), field=4,
source=(0,0)) = 7433961230129473403` for P versus
`arbitration_priority(5, 0, target=(0,1), field=4, source=(0,2)) =
13045711265774597214` for Q -- Q's priority is higher, so Q wins.
`KILL_GATES_01.md` and `test_k1_case2_two_competing_donors` are both
corrected to the Q-wins, total-90 outcome, with both priorities pinned as
explicit assertions and the winner/credit read from a `"proposal_won"`
trace event rather than assumed.

## 10. Test results

Windows (`python -B -m pytest Aether/test -q`), clean local basetemp,
bytecode/plugin-autoload disabled: **564 passed, 5 skipped, 92 subtests
passed, 438.16s, exit 0.** (Up from the review's reproduced baseline of
442/5/92 -- the increase is entirely new B1/B2/B3/B4/integer-domain/S05
regressions added this round: 4 in `runpod_api`, ~24 in
`age_controller` [including B3-arming and B4-diagnostics cases], 20 in
the new `independent_reaper` suite, 1 image-manifest case, and 1 S05
inert-fixture case.)

Ubuntu 24.04 WSL (`python3 -B Aether/test/test_aeth01_pod_service.py` and
`python3 -B Aether/test/test_aeth01_runpod_api.py`, direct unittest, no
pytest available in that environment): **27 tests / 36 tests, both `OK`**
(covers Linux process-group/special-file/service-wrapper behavior Windows
skips; the 36 includes 2 new B1/B4 transport regressions added this round
versus the review's prior baseline of 34).

**Known, pre-existing, environment-specific flakiness (not a logic
defect, not introduced by this round):** on this Windows workstation,
`atomic_write()`'s `os.replace()` can rarely fail transiently (observed
independently on the UNMODIFIED base commit via `git stash`, hitting
`test_duplicate_inventory_does_not_multiply_cleanup_time_without_bound`
2 of 3 times before any of this round's changes). This round's mandatory
reconciliation substantially increases total commit volume per test run,
which increases the statistical chance of hitting this same pre-existing
issue somewhere in a ~600-test run (observed roughly once per several full
runs, always a different test, always resolved by rerunning). A bounded
retry was added to `_replace_with_retry()` to reduce (not eliminate) this;
brittle exact-count assertions that depended on it were also loosened.
This is disclosed, not hidden, per the review's own "report skips
honestly" instruction; it does not affect any B1-B4 correctness finding.

Do not sum test counts across runs as independent trials (multiple runs
overlap the same suite).

## 11. Image/build/digest status

Docker CLI is present (`docker version` succeeds) but the daemon/engine is
NOT running in this environment (`docker info` fails to reach the
Windows/WSL engine pipe) -- **left explicitly unresolved**, per the
task's own instruction, rather than falsely claimed. No build, inspect,
push, or registry pull was attempted or is claimed.

Completed without a build: `P/Dockerfile` now pins `numpy==2.2.0` and
`cupy-cuda12x==13.3.0` (previously fully floating), explicitly flagged in
its own comment as a best-effort, NOT build-verified pin. `P/image_manifest.py`
(new) hashes every runtime-critical file this image ships or that the
controller's approval should bind to -- `aeth01_cpu_oracle.py`,
`aeth01_gpu_kernel.py`, `run_canary.py`, `pod_service.py`,
`receipt_schema.json`, `watchdog.sh`, `Dockerfile` -- wider than
`age_controller.SOURCES`'s 3-file hash set (which is deliberately narrow:
only what the controller can verify without importing scientific code).
The committed `image_manifest.json` records current worktree hashes;
`installed_dependencies` and `immutable_image_digest` are explicitly
`null` and must be filled in from a real `docker build --platform
linux/amd64` + `docker inspect` + `pip freeze` before this manifest is
treated as binding image identity evidence for R1.

## 12. Remaining unverified provider behavior

Unchanged from `ASTRA_CLOSURE_REVIEW_02.md` section 9: actual CuPy device
allocation/kernel execution, real RunPod create/list/delete responses
against the documented v2 shapes, proxy latency/availability, and real
account-scope/credential behavior are all still unverified by construction
(no paid call was made). This round only changes local code and offline
tests; it retires none of that uncertainty and does not claim to.

## 13. Exact R1 information goal (unchanged from the controlling review)

For one approved account/key, hardware allocation, immutable image, and
bounded attempt: whether the create/status path is usable; whether that
image starts; whether actual CuPy device allocation/operations work;
whether all 200 single-tick plus 20x5 trajectory comparisons match the
bundled CPU; whether run-bound artifacts are retrievable; and whether
cleanup produces the required provider AND independent-reaper evidence,
followed by charge reconciliation. This retires feasibility uncertainty
for that one instance only -- not general API reliability, all GPUs,
performance, scientific inference, or spontaneous origin.

## 14. Exact conditions still required before paid authorization

1. **B3 operational**: deploy `independent_reaper.py` on infrastructure
   genuinely independent of this controller host (separate machine/process/
   scheduler/power/network), `arm` it against the real plan's
   `reaper_manifest.json` before the real POST, and keep it running through
   the real cutoff and reconciliation horizon. This repair delivers the
   code and an offline rehearsal; it does not and cannot deliver that
   deployment from inside this session.
2. Operator-verified current RunPod account balance/credentials and a
   real, out-of-band-armed independent billing cutoff (attested value in
   the approval JSON must correspond to something that actually exists).
3. An operator decision on the image: either accept the unverified
   Dockerfile pin as sufficient given no build is possible here, or defer
   R1 until Docker (or an equivalent remote build) is available to
   actually build/inspect/push and complete `image_manifest.json`.
4. A separately documented, bounded, independent-of-the-artifact-proxy
   diagnostic capture route for the first supervised R1 (operator/provider
   log retrieval is acceptable per the review; this round adds the
   in-controller diagnostic journal but does not stand up an external log
   pipeline).
5. Fresh operator approval JSON bound to the current plan/reaper-manifest
   hashes (the schema gained `reaper_arming`-adjacent files; existing
   approval JSON from before this round is not compatible as-is because
   `reaper_manifest.json`/`reaper_ack.json` did not exist then).

No paid RunPod action was taken or is authorized by this document.

## 15. Commit discipline

Focused commits, in this order: (1) B1/B2 cleanup semantics + B4
diagnostics (`age_controller.py`, `runpod_api.py`, their tests -- these
landed together because the terminate/monitor/create call sites are the
same code the diagnostics journal instruments); (2) independent reaper
(`independent_reaper.py`, its tests, README); (3) integer validation +
cheap scientific text corrections + K1 golden vector; (4) image/build
identity preparation; (5) this admission packet. Pushed and verified
against remote HEAD after all five land.

## 16. Disposition

**`B3_OPERATIONAL_EVIDENCE_REQUIRED`.**

B1, B2, B4, and the integer-domain gap are repaired and tested (Windows +
WSL Linux, see section 10). B3's code, HMAC-bound pre-create handoff, and
offline host-offline rehearsal are complete and tested. What is NOT
established from inside this coding session is a genuinely independent,
already-armed reaper running on separate physical/cloud infrastructure
through a real cutoff -- exactly the operational fact the review's own
section 12 anticipates cannot be manufactured by code alone
("No credible independent reaper means the operational hold remains even
after all code repairs pass"). Per that section's own guidance: prefer
`B3_OPERATIONAL_EVIDENCE_REQUIRED` over `READY_FOR_R1_ADMISSION_REVIEW`
whenever B3 code exists but true independent deployment is not yet
armed/rehearsed on separate infrastructure. That is the case here.

+=============================== END ==================================+
