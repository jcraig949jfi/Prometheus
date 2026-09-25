+======================================================================+
| AGE / AETH-01 -- FINAL BOUNDED SOFTWARE FALSIFICATION, REVIEW 04      |
| Author: Augment Agent / Astra reviewer; Windows workstation + WSL    |
| Date: 2026-09-21; For: HITL and external reviewers                    |
| Verdict: BOUNDED_REPAIR_BEFORE_B3                                     |
| Self-contained result; repository needed only to rerun the appendix |
+======================================================================+

----- 0. Decision and exact scope -----

ONE executable blocker remains: C1, controller-known IDs omitted from the
reaper's probe set. A real production aggregation wrote an authoritative
OPERATIONAL_CLEANUP_CONFIRMED seal while an exact-owned, controller-known pod
would return RUNNING on GET. This is not a hypothetical or an absent billing
guarantee. AGE software may NOT yet proceed to B3 operational proof.
The N1 repair works for reaper-known IDs; N2's durable-local-state check held.
No architectural replacement is justified. Repair only the known-ID coverage
gap, with explicit authorization, then rerun its falsifier and affected tests.

Repository: jcraig949jfi/Prometheus.
Branch: aether/base-role-adopt-2026-09-19.
Exact reviewed HEAD: 694440ac5f0e89d4c9e30b816bc8d430eca8bc42.
Review-03 implementation: d5ffef03910f7ed2e18ae053e0823691b330dbb0.
Earlier baseline: c6719c1beaad5d9c82f9bbe2eacd7b8417d2f07d.
Reviewed the named Review-03 packet, CLEANUP_EVIDENCE_MODEL.md and only the
cleanup implementation, API adapter and relevant offline tests. No production
or test file changed. This review is the sole repository artifact. No RunPod,
deployment, image build, paid resource or scientific work. Provider spend: $0.
N2-F/section 3 arrived truncated; interpreted as unfinished-state refusal and
combined live-GET/newer-durable-local-state falsification, not a wider review.

----- 1. C1: exact initial state and executable event sequence -----

1. Existing offline controller fixture runs the real controller with injected
   transports. Original durable state is DONE and local report A confirms
   pod_1. It has an exact ID/name/image/run-environment binding and cleanup
   history. All local provider events precede cutoff. A's hash matches disk.
2. The independent reaper starts from its legitimate new_evidence_state:
   owned_ids=[], pod_evidence={}. Its pre-create manifest has run identity,
   not the controller's subsequently learned pod ID. No state is forged.
3. For the full cutoff..cutoff+3600 interval, LIST is complete but stale/empty.
   From relative t=1800 onward, GET pod_1 would return exact-owned RUNNING.
   The provider mock continues to offer this response through sealing.
4. Real sweep runs 61 rounds at 60s spacing. It makes 61 LIST calls, ZERO
   GET calls and ZERO DELETE calls, earning 3600s and REAPER_CLEANUP_CONFIRMED.
5. At t=3600, real combine_operational_cleanup(A, report, run_dir=ORIGINAL,
   now=clock.time()) acquires RunLock, validates current state and writes seal.
   Actual: OPERATIONAL_CLEANUP_CONFIRMED, authoritative_local_state=true,
   exit_code=0. The persisted cleanup_seal.json equals the returned result.
6. Direct GET pod_1 returns RUNNING with the exact original ownership binding.
   Expected safe result: refuse/unresolved until this already-known ID has
   participated in the independent cleanup and complete fresh GET horizon.

Counterfactual control: seed the SAME pod ID into the reaper's known set first.
The same stale LIST/live GET sequence then causes 61 GETs, 31 DELETE attempts
at t=1800..3600, zero clean coverage and OPERATIONAL_CLEANUP_UNRESOLVED.
This isolates the omitted known-ID handoff/coverage, not stale local hashing.
The independent oracle rejected the failing trace when supplied the COMPLETE
controller/reaper known-ID union. The real combiner nevertheless confirmed it.

----- 2. Cause, missed test and minimum repair -----

At reviewed HEAD, independent_reaper.py:269-284 initializes an empty known set;
its GET loop at 470 probes only state[owned_ids]. Controller-known IDs are not
inputs to sweep. cleanup_evidence.py:390-397 explicitly permits a locally
deleted pod to be absent from the reaper horizon. Lines 428-434 union IDs for
confidence but do NOT require dual-endpoint coverage of that union. The seal
in age_controller.py:1095-1128 binds this insufficient result to CURRENT state;
state freshness cannot substitute for independent GET coverage.

Existing tests miss C1 because reaper N1 tests seed IDs into the reaper before
measurement. test_aeth01_age_controller.py:1469-1497 deliberately constructs a
clean local pod plus reaper owned_ids=[] and expects operational confirmation.
Oracle comparison fixtures seed their two IDs into the reaper too; they do not
test controller-only known IDs against final authoritative aggregation.

Minimum safety repair: final aggregation must refuse if the authoritative
local/reaper known-ID union was not covered by the qualifying reaper GET
horizon. Never waive this for locally confirmed IDs. Supply authenticated/
trusted, run-bound known IDs to the cleanup-only reaper before credit begins;
newly supplied IDs require cleanup and a fresh full horizon. At minimum reject
local IDs missing from the reaper report; do not relabel an old window as covered.
Retain identity-conflict guards and no-create capability. Add C1 end-to-end
regression and its seeded control, using the oracle's COMPLETE known-ID union.
No repair was made or authorized by this review.

----- 3. Requested N1 attacks -----

N1-A: reaper-known RUNNING at t=1800 demoted confidence, reset the window and
attempted DELETE in the same round. Final operational result unresolved.
N1-B: TERMINATED at t=1800 kept known cleanup confirmed but reset EMPTY coverage.
N1-C: actual API adapter under an offline opener: 401, 403, 429, 500, 503, timeout
and malformed 200 JSON all prevented operational confirmation. At t=3600, the
post-interruption window covered only 1740s. No failure became an empty sample.
404 caveat: the declared model/API treats completed GET 404 as MISSING, not a
failed probe. It CAN coexist with a qualifying complete-LIST sample. It added
ZERO absence witnesses: 63 witnesses were two seed LIST absences plus 61 LIST
absences. Existing failed-LIST/404 regression also passed. Thus the literal
request that no 404 participate in a healthy round differs from the declared
policy. This is explicit, not an accidental promotion or a separate blocker.
N1-D: changed identity blocked DELETE, retained ambiguity and zero coverage.
N1-E: three known IDs A/B/C; actual process death before GET C left the current
round unqualified. Disk had 60 samples, reconciled=false; restart earned zero.
N1-F: death after final GET or after observe_window but before checkpoint did
not invent sample 61. Restart discarded all prior window credit.
N1-G: LIST duplicate at t=1800 was retained/deleted and reset coverage. A continued
invocation could first confirm at t=5460, after the fresh 1860..5460 full horizon.
These bounded N1 checks passed; C1 remains the cross-source coverage failure.

----- 4. Requested N2 and combined attacks -----

N2-A: allowed recover() persisted B with exact-owned RUNNING during the window.
Supplying old A refused STALE_LOCAL_OUTCOME. Supplying current B was unresolved.
N2-B: copying old original storage before B DID allow the copy to confirm.
Nothing cryptographically authenticates the original directory. This exactly
matches the explicit trusted-storage boundary, not an additional blocker.
N2-C: recovery attempted from another process while sealing held RunLock was
refused. Reverse ordering, aggregation during recovery's lock, also refused.
N2-D: seal persistence faults at temp/fsync/rename/directory boundaries yielded no API
success. After-rename failures may leave a fully formed HISTORICAL seal file;
that fact does not make the failed call successful or create standing authority.
N2-E: after valid seal S, allowed recovery changed original durable state.
Old A was refused; supplying S as local report was also refused. Production
canary-module search found no reader treating cleanup_seal.json as a token.
N2-F: CREATE_INTENT and CLEANUP authoritative phases both refused.
Combined: actual reaper GET RUNNING at t=1800 plus allowed controller recovery B
kept the reaper unresolved; old A refused, current B unresolved. No stale-B
bypass was found. A current, truthful but temporally old local observation
DOES participate in C1; its missing independent probes are the blocker.

----- 5. Oracle, crashes, clocks and trust -----

Oracle AST and restricted-import execution both verified only math.isfinite;
no cleanup_evidence, age_controller or independent_reaper import. Nine direct
attacks rejected missing GET, live pod, failed probe, incomplete LIST, short
duration, excessive gap, stale state hash, late local event and omitted known
ID. Complete-union input also rejected C1. Constants 60s/2s/6 samples and elapsed
span rules intentionally share the specification with production: independent
code, NOT independent requirements. Omitted IDs hidden from both trace and
supplied known set remain undetectable; this necessary-only ceiling is explicit.

Twelve actual reaper child-process deaths (os._exit, no exception unwinding):
LIST-positive visitor checkpoint, LIST completion, GET positive before journal,
GET failure, durable DELETE attempt, ACK returned before journal, ACK journaled,
before GET C, final GET completed, scan mutated but uncommitted, scan committed,
and journaled identity conflict. Durable ownership/history survived; partial
rounds did not qualify; conflict did not authorize deletion. Only the fully
committed healthy final round had historical confirmation; all restarts reset.
This does not claim persistence of a network response before its first write.

Ubuntu 24.04 WSL: five actual seal-process deaths after state reload, temp write,
temp fsync, rename and directory fsync; four OSError injections at persistence
boundaries. No call returned success on interruption/failure; fresh restart
acquired the released lock and revalidated. Linux directory fsync was actually
executed. This is targeted crash testing, not power-loss filesystem proof.

Ten clock/freshness attacks: wall backward, wall+600s, wall+3600s, monotonic
backward, both+3600s, future local report, future local RUNNING state, malformed
timestamp, aggregation 61s after last sample, future persisted reaper report.
All reset/refused/unresolved; none manufactured a full horizon.

Trusted: original unrolled-back local storage and lock-obeying writers, OS locks,
atomic filesystem semantics, reaper storage/report provenance, sampled provider
responses, and clocks within the declared model. Hashes cannot authenticate a
copied/rolled-back directory. NON_BLOCKING_RISK: common-mode policy assumptions,
historical-seal misuse by external consumers, correlated/accelerated faulty
clocks outside these assumptions. B3_EMPIRICAL_QUESTION: real endpoint lag,
permissions, scheduler/host independence, durable handoff and outage behavior.
C1 needs neither malicious storage nor both endpoints hiding a known resource:
the specific GET that would falsify cleanup is available but never called.

----- 6. Executed validation and publication -----

Unmodified focused suite: 646 passed, 74 subtests passed, 92.83s, exit 0. Command:
python -B -m pytest Aether/test/test_aeth01_cleanup_evidence.py
Aether/test/test_aeth01_age_controller.py Aether/test/test_aeth01_independent_reaper.py
Aether/test/test_aeth01_cleanup_oracle.py Aether/test/test_aeth01_runpod_api.py
-q -p no:cacheprovider (one command). Plus the separate adversarial matrices
above, including actual production sealing for C1; all harnesses exited 0 after
asserting expected outcomes. Child exits 77/78 were intentional crash/refusal
signals, not unexpected test failures. No full physics or Linux pytest claim.
Evidence Wiki client unavailable (ModuleNotFoundError); no publication claimed.
Delegated read-only reviewer returned no substantive findings; no independent
second-agent approval is claimed. This artifact records executed parent review.
Review commit is the commit containing this sole artifact, reported at handoff.
Proceed to B3 only after the concrete C1 repair is separately authorized and
validated. No general cleanup re-review or unrelated software work is requested.

+=========================== END OF VERDICT ===========================+
Retirement or "not worth continuing" remains an available human decision.

----- Appendix A. Executable minimal C1 reproduction -----

Run from the reviewed worktree root with its existing Python/pytest environment.
Concatenate the five Python excerpts in order and execute as ONE script with
python -B. Splitting is presentation only; indentation continues across blocks.
It uses existing offline fixtures, temporary directories and blocked sockets.
No real credentials, provider connection, production edit or test edit is needed.
The fixture's launch() is an injected simulation of the real controller API.
Assertions deliberately verify the BUG at reviewed HEAD, not desirable behavior.
Expected output: C1_REPRODUCED: authoritative confirmation; live known pod; 0 GETs.

<augment_code_snippet mode="EXCERPT">
````python
import importlib.util, socket, tempfile
from pathlib import Path
from unittest.mock import patch
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module); return module
t = load("r04_age", Path("Aether/test/test_aeth01_age_controller.py"))
````
</augment_code_snippet>

<augment_code_snippet mode="EXCERPT">
````python
u = load("r04_reaper", Path("Aether/test/test_aeth01_independent_reaper.py"))
a, r = t.age, u.reaper
def blocked(*args, **kwargs):
    raise AssertionError("network forbidden")
with tempfile.TemporaryDirectory() as tmp, patch.object(socket, "socket", blocked), patch.object(socket, "create_connection", blocked):
    rig = t.rig.__wrapped__(Path(tmp))
    local = t.launch(rig)
    manifest = local["manifest"]
````
</augment_code_snippet>

<augment_code_snippet mode="EXCERPT">
````python
    cutoff = r._timestamp(manifest["cutoff_utc"])
    clock = u.Clock(start=cutoff)
    provider = u.Provider()
    provider._owned_pod("pod_1", manifest["run_name"], manifest["run_id"])
    provider.list_hook = lambda p: []
    provider.get_hook = lambda p, pid: (
        dict(p.pods[pid], status="RUNNING") if clock.mono >= 1800 else None)
    digest = r._sha(r._encode(manifest))
````
</augment_code_snippet>

<augment_code_snippet mode="EXCERPT">
````python
    state = r.new_evidence_state(manifest, digest)
    report = r.sweep(manifest, digest, provider, state, rounds=61,
        poll_seconds=60, sleep=clock.sleep,
        clock_time=clock.time, monotonic=clock.monotonic)
    assert provider.calls == ["LIST"] * 61
    assert local["owned_ids"] == ["pod_1"] and report["owned_ids"] == []
    result = a.combine_operational_cleanup(
        local, report, run_dir=rig.directory, now=clock.time())
````
</augment_code_snippet>

<augment_code_snippet mode="EXCERPT">
````python
    assert result["operational_cleanup_status"] == "OPERATIONAL_CLEANUP_CONFIRMED"
    assert result["authoritative_local_state"] is True
    assert result["exit_code"] == 0
    assert t.read_json(rig.directory / "cleanup_seal.json") == result
    assert result["local_seal"]["state_sha256"] == a._sha(a._encode(t.read_json(rig.directory / "state.json")))
    live = provider.get_pod("pod_1")
    assert r._owned(live, manifest) and live["status"] == "RUNNING"
    print("C1_REPRODUCED: authoritative confirmation; live known pod; 0 GETs")
````
</augment_code_snippet>