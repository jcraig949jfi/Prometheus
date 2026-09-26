"""Iteration 3: controlled failure injection against the fake provider.

Every failure the directive names is injected here, before any hardware,
and each test answers the same six questions from the receipt's own
`disposition` block (derived, never hand-written):

  1. what does the controller believe?   disposition.controller_believes
  2. what does the provider believe?     disposition.provider_believes
  3. what evidence is retained?        disposition.evidence_retained
  4. can the run resume?                 disposition.resumable / ledger
  5. can the resource be cleaned safely? disposition.cleanup_safe
  6. uncertainty or absence?             disposition.pod_state, artifact lists

`fake.leaked()` stays the ground truth: pods that REALLY exist whatever
the API said. A receipt that claims clean while `leaked()` is non-empty is
the defect this whole suite exists to prevent.
"""

import hashlib
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "runpod")))

from prometheus_gpu import launch                     # noqa: E402
from prometheus_gpu import provider as prov           # noqa: E402
from prometheus_gpu import receipt as rc              # noqa: E402
from prometheus_gpu import spec as spec_mod           # noqa: E402

SPEC = {
    "name": "chaos-test",
    "entrypoint": "run.py",
    "dependencies": {"pip": ["numpy==2.2.0"]},
    "gpu": {"class": "NVIDIA RTX A4000", "count": 1},
    "max_runtime_s": 3600,
    "artifacts": ["result.json"],
    "canary": "python3 -c 'import numpy'",
    "work_units": {"name": "steps", "estimate": 100},
    "telemetry": {"interval_s": 10},
}
TEL = launch.TELEMETRY_PATH
START = '{"kind":"start","t_utc":"a","t_elapsed_s":0,"seq":1}\n'
PROG = '{"kind":"progress","t_utc":"b","t_elapsed_s":30,"seq":2,"units":50}\n'
PROG2 = '{"kind":"progress","t_utc":"b","t_elapsed_s":60,"seq":3,"units":70}\n'
END = ('{"kind":"end","t_utc":"c","t_elapsed_s":90,"seq":4,"units":100,'
       '"status":"ok"}\n')
RESULT = b'{"answer": 42}'


class Clock(object):
    def __init__(self, start=1_000_000.0):
        self.t = float(start)

    def now(self):
        return self.t

    def sleep(self, seconds):
        self.t += float(seconds)


def frames(*texts):
    seq = list(texts)
    return lambda index: seq[min(index, len(seq) - 1)]


def manifest(**files):
    """What the pod's /_manifest would say about these files."""
    return json.dumps({"epoch": 0, "files": {
        name: {"bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest()}
        for name, blob in files.items()}})


def stages(*names, rc_value=None):
    lines = ['{"stage": "%s", "epoch": %d}' % (n, 100 + i)
             for i, n in enumerate(names)]
    if rc_value is not None:
        lines.append('{"stage": "module_rc", "epoch": %d}' % rc_value)
    return "\n".join(lines) + "\n"


@pytest.fixture
def module_dir(tmp_path):
    d = tmp_path / "mod"
    d.mkdir()
    (d / "run.py").write_text("print('hello')\n")
    return str(d)


def controller(fake, module_dir, clock=None, spec=None, budget_usd=5.0, **kw):
    clock = clock or Clock()
    ctl = launch.Controller(fake, spec_mod.from_dict(spec or dict(SPEC)),
                            module_dir, budget_usd=budget_usd, poll_s=30.0,
                            now=clock.now, sleep=clock.sleep, **kw)
    ctl.clock = clock
    return ctl


def served(tel=None, extra=None, with_manifest=True):
    out = {TEL: tel or frames(None, START, START + PROG,
                              START + PROG + END),
           "result.json": RESULT}
    if with_manifest:
        out[launch.MANIFEST_PATH] = manifest(**{"result.json": RESULT})
    out.update(extra or {})
    return out


def six(r):
    d = r["disposition"]
    for key in ("cause", "controller_believes", "provider_believes",
                "evidence_retained", "resumable", "cleanup_safe", "pod_state"):
        assert key in d, key
    return d


# ---------------------------------------------------------------- baseline

def test_a_clean_run_answers_all_six_questions(module_dir):
    fake = prov.FakeProvider(served=served())
    r = controller(fake, module_dir).run()
    d = six(r)
    assert r["result"] == "OK" and d["cause"] == "OK"
    assert d["provider_believes"] == {"list_contains_pod": False,
                                      "get_returns_pod": False,
                                      "terminate_response": "ACK_204",
                                      "reads": 1}
    assert d["evidence_retained"]["artifacts_verified"] == ["result.json"]
    assert d["cleanup_safe"] is True
    assert d["pod_state"].startswith("ABSENT")
    assert r["artifacts"][0]["integrity"] == "verified"
    assert fake.leaked() == []
    rc.validate(r)


def test_api_latency_and_controller_health_are_on_the_record(module_dir):
    fake = prov.FakeProvider(served=served())
    r = controller(fake, module_dir).run()
    assert r["api_latency"]["create_pod"]["calls"] == 1
    assert r["api_latency"]["fetch"]["calls"] >= 3
    assert r["controller_health"]["polls"] >= 1


# ------------------------------------------------------------ module side

def test_a_module_that_exits_nonzero_is_seen_without_waiting_for_a_cap(
        module_dir):
    """Crash with no `end` record: the stage file says the module exited,
    so the watch stops within a poll instead of at max_runtime_s."""
    fake = prov.FakeProvider(served=served(
        tel=frames(START, START + PROG),
        extra={launch.STAGES_PATH: frames(
            stages("boot", "module_start"),
            stages("boot", "module_start"),
            stages("boot", "module_start", "module_end", rc_value=3))}))
    ctl = controller(fake, module_dir)
    r = ctl.run()
    d = six(r)
    assert r["result"] == "FAILED"
    assert d["cause"] == "MODULE_EXITED_WITHOUT_END"
    assert ctl.module_rc == 3
    assert d["evidence_retained"]["telemetry_records"] == 2
    assert d["cleanup_safe"] is True and fake.leaked() == []
    assert r["cost"]["elapsed_s"] < 600, "stopped at the crash, not a cap"


def test_a_hung_module_is_stopped_on_unchanged_telemetry(module_dir):
    fake = prov.FakeProvider(served=served(tel=frames(START, START + PROG)))
    r = controller(fake, module_dir, telemetry_stall_s=300.0).run()
    d = six(r)
    assert r["result"] == "ABORTED" and d["cause"] == "TELEMETRY_STALLED"
    assert d["evidence_retained"]["telemetry_records"] == 2
    assert d["cleanup_safe"] is True and fake.leaked() == []
    assert r["cost"]["elapsed_s"] < 900


def test_a_telemetry_pause_shorter_than_the_stall_is_not_a_hang(module_dir):
    """The false-positive guard: 240 s of unchanged telemetry, then the
    module finishes. A 300 s stall threshold must let it finish."""
    unchanged = [START + PROG] * 9            # 9 polls x 30 s = 270 s
    fake = prov.FakeProvider(served=served(
        tel=frames(START, *(unchanged + [START + PROG + END]))))
    r = controller(fake, module_dir, telemetry_stall_s=300.0).run()
    assert r["result"] == "OK", r["disposition"]


def test_timeout_answers_the_six_questions(module_dir):
    spec = dict(SPEC, max_runtime_s=120)
    fake = prov.FakeProvider(served=served(
        tel=lambda i: START + PROG * (i + 1)))       # keeps changing
    r = controller(fake, module_dir, spec=spec).run()
    d = six(r)
    assert r["result"] == "TIMEOUT" and d["cause"] == "MAX_RUNTIME"
    assert d["cleanup_safe"] is True and fake.leaked() == []


# ------------------------------------------------------------ server side

def test_the_artifact_server_disappearing_is_unknown_not_failed(module_dir):
    """The whole server goes away -- every path -- while GET still returns
    the pod."""
    fake = prov.FakeProvider(served=served(tel=frames(START, START + PROG)))
    ctl = controller(fake, module_dir, unreachable_s=300.0)
    original = ctl.raw_provider.fetch
    seen = {"tel": 0}

    def fetch(pod_id, path, **k):
        if path == TEL:
            seen["tel"] += 1
        if seen["tel"] > 2:
            return None                      # server gone, every path
        return original(pod_id, path, **k)
    ctl.raw_provider.fetch = fetch
    r = ctl.run()
    d = six(r)
    assert r["result"] == "UNKNOWN"
    assert d["cause"] == "ARTIFACT_SERVER_UNREACHABLE"
    # What remains is what was read BEFORE the server went away.
    assert d["evidence_retained"]["telemetry_records"] == 2
    assert d["evidence_retained"]["artifacts_missing"] == ["result.json"]
    assert d["cleanup_safe"] is True and fake.leaked() == []


def test_a_pod_that_vanishes_mid_watch_is_named(module_dir):
    fake = prov.FakeProvider(served=served(tel=frames(START, START + PROG)))
    ctl = controller(fake, module_dir, unreachable_s=120.0,
                     telemetry_stall_s=10_000.0)
    original = ctl.raw_provider.fetch
    calls = {"n": 0}

    def fetch_then_vanish(pod_id, path, **k):
        calls["n"] += 1
        if calls["n"] == 12:
            fake.truth.pop(pod_id, None)     # the provider lost it
        return original(pod_id, path, **k)
    ctl.raw_provider.fetch = fetch_then_vanish
    r = ctl.run()
    d = six(r)
    assert r["result"] == "UNKNOWN" and d["cause"] == "POD_VANISHED"
    assert d["pod_state"].startswith("ABSENT")


def test_a_corrupted_artifact_is_filed_as_mismatch_never_as_the_artifact(
        module_dir):
    fake = prov.FakeProvider(served=served(extra={
        "result.json": b'{"answer": 41}'}))          # not what the pod holds
    ctl = controller(fake, module_dir)
    r = ctl.run()
    d = six(r)
    assert d["evidence_retained"]["artifacts_corrupt"] == ["result.json"]
    assert d["evidence_retained"]["artifacts_verified"] == []
    entry = r["artifacts"][0]
    assert entry["integrity"] == "mismatch" and entry["attempts"] == 3
    assert entry["expected"]["sha256"] == hashlib.sha256(RESULT).hexdigest()
    assert "result.json" not in ctl.artifact_blobs
    assert "result.json.mismatch" in ctl.artifact_blobs


def test_a_transiently_corrupted_artifact_is_refetched(module_dir):
    fake = prov.FakeProvider(served=served(extra={
        "result.json": frames(b'{"answer": 41}', RESULT)}))
    r = controller(fake, module_dir).run()
    entry = r["artifacts"][0]
    assert entry["integrity"] == "verified" and entry["attempts"] == 2


def test_a_partial_artifact_retrieval_is_detected_by_size(module_dir):
    fake = prov.FakeProvider(served=served(extra={
        "result.json": RESULT[:5]}))                 # always truncated
    r = controller(fake, module_dir).run()
    entry = r["artifacts"][0]
    assert entry["integrity"] == "mismatch"
    assert entry["bytes"] == 5 and entry["expected"]["bytes"] == len(RESULT)


def test_without_a_manifest_an_artifact_is_unverified_not_missing(module_dir):
    fake = prov.FakeProvider(served=served(with_manifest=False))
    r = controller(fake, module_dir).run()
    d = six(r)
    assert d["evidence_retained"]["artifacts_unverified"] == ["result.json"]
    assert d["evidence_retained"]["artifacts_missing"] == []
    assert r["artifact_integrity"]["manifest_available"] is False


# --------------------------------------------------- controller interruption

def crash_at(event, nth=1):
    seen = {"n": 0}

    def hook(name):
        if name == event:
            seen["n"] += 1
            if seen["n"] == nth:
                raise launch.SimulatedCrash(name)
    return hook


def test_a_killed_controller_leaves_the_pod_and_a_ledger_then_resumes(
        module_dir, tmp_path):
    ledger = str(tmp_path / "run.ledger.json")
    clock = Clock()
    tel = frames(None, START, START + PROG, START + PROG, START + PROG2,
                 START + PROG2 + END)
    fake = prov.FakeProvider(served=served(tel=tel))
    first = controller(fake, module_dir, clock=clock, ledger_path=ledger,
                       crash_hook=crash_at("watch", nth=2))
    with pytest.raises(launch.SimulatedCrash):
        first.run()
    # The kill skipped every `finally`: the pod is still billing and the
    # only remaining record of it is the ledger.
    assert len(fake.leaked()) == 1
    saved = launch.load_ledger(ledger)
    assert saved["pod_id"] == fake.leaked()[0]
    assert saved["pod_name"] == saved["run_id"]
    assert saved["artifact_token"]

    clock.sleep(600)                     # ten minutes with no controller
    second = controller(fake, module_dir, clock=clock, ledger_path=ledger)
    r = second.resume(launch.load_ledger(ledger))
    d = six(r)
    assert r["result"] == "OK"
    assert fake.calls["create"] == 1, "resume never creates"
    assert fake.leaked() == []
    assert r["resumed"]["controller_absent_s"] >= 600
    assert d["resumed"]["ledger_last_event"] == "watch"
    # The pod billed through the gap, so the cost starts at the ORIGINAL
    # create, not at the resume.
    assert r["cost"]["elapsed_s"] >= 600
    assert d["cleanup_safe"] is True


def test_a_kill_before_first_telemetry_resumes_through_the_ready_wait(
        module_dir, tmp_path):
    ledger = str(tmp_path / "l.json")
    clock = Clock()
    fake = prov.FakeProvider(served=served())
    with pytest.raises(launch.SimulatedCrash):
        controller(fake, module_dir, clock=clock, ledger_path=ledger,
                   crash_hook=crash_at("created")).run()
    assert len(fake.leaked()) == 1
    r = controller(fake, module_dir, clock=clock, ledger_path=ledger).resume(
        launch.load_ledger(ledger))
    assert r["result"] == "OK" and fake.leaked() == []


def test_a_kill_before_create_leaves_nothing_to_resume(module_dir, tmp_path):
    ledger = str(tmp_path / "l.json")
    fake = prov.FakeProvider(served=served())
    with pytest.raises(launch.SimulatedCrash):
        controller(fake, module_dir, ledger_path=ledger,
                   crash_hook=crash_at("planned")).run()
    assert fake.calls["create"] == 0 and fake.leaked() == []
    with pytest.raises(launch.LaunchRefused):
        controller(fake, module_dir).resume(launch.load_ledger(ledger))


def test_resume_leaves_alone_a_pod_that_is_no_longer_ours(module_dir, tmp_path):
    ledger = str(tmp_path / "l.json")
    fake = prov.FakeProvider(served=served())
    with pytest.raises(launch.SimulatedCrash):
        controller(fake, module_dir, ledger_path=ledger,
                   crash_hook=crash_at("created")).run()
    pod_id = fake.leaked()[0]
    fake.truth[pod_id]["name"] = "someone-else"     # the id now names another
    with pytest.raises(launch.LaunchRefused) as exc:
        controller(fake, module_dir).resume(launch.load_ledger(ledger))
    assert "not ours" in str(exc.value)
    assert fake.calls["terminate"] == 0, "never terminate what is not ours"


def test_resume_after_the_pod_is_already_gone(module_dir, tmp_path):
    ledger = str(tmp_path / "l.json")
    fake = prov.FakeProvider(served=served())
    with pytest.raises(launch.SimulatedCrash):
        controller(fake, module_dir, ledger_path=ledger,
                   crash_hook=crash_at("watch")).run()
    fake.truth.clear()                                # gone meanwhile
    r = controller(fake, module_dir).resume(launch.load_ledger(ledger))
    d = six(r)
    assert r["result"] == "UNKNOWN" and d["cause"] == "POD_GONE_BEFORE_RESUME"
    assert d["pod_state"].startswith("ABSENT")
    assert fake.calls["create"] == 1


# ----------------------------------------------------------- control plane

def test_a_lost_create_is_adopted_by_name_not_by_position(module_dir):
    fake = prov.FakeProvider(create_faults=[prov.Fault.lost_response()],
                             served=served())
    r = controller(fake, module_dir).run()
    assert r["pods"][0]["creation_outcome"] == "adopted"
    assert fake.calls["create"] == 1 and fake.leaked() == []


def test_an_ambiguous_status_less_create_is_reconciled(module_dir):
    fake = prov.FakeProvider(create_faults=[prov.Fault.ambiguous()],
                             served=served())
    r = controller(fake, module_dir).run()
    assert r["pods"][0]["creation_outcome"] == "adopted"
    assert fake.calls["create"] == 1 and fake.leaked() == []


def test_someone_elses_pod_is_never_adopted():
    """A pod of another name appears after our create fails. It is not
    ours, and adopting it would mean terminating it."""
    fake = prov.FakeProvider()
    other = fake.create_pod({"name": "another-seat-run"})
    fake._create_faults.append(prov.Fault.http(500))
    pod, status = prov.create_with_reconcile(
        fake, {"name": "our-run"}, attempts=1, sleep=lambda s: None)
    assert pod is None and status == "FAILED_CLEAN"
    assert other["id"] in fake.actually_running()


def test_unnamed_listings_make_ownership_undecidable():
    fake = prov.FakeProvider(create_faults=[prov.Fault.lost_response()],
                             unnamed=True)
    pod, status = prov.create_with_reconcile(
        fake, {"name": "our-run"}, attempts=3, sleep=lambda s: None)
    assert pod is None and status == "AMBIGUOUS_UNRECONCILED"
    assert fake.calls["create"] == 1, "no retry while ownership is unknown"


def test_a_lost_create_that_every_list_omits_is_the_named_residual_risk(
        module_dir):
    """The one case nothing here can close: the create succeeded, its
    response was lost, and every LIST omits the pod. Without the id there
    is nothing to GET. The receipt must say its absence claim rests on LIST
    reads alone -- it may not look like a confirmed non-event."""
    fake = prov.FakeProvider(
        create_faults=[prov.Fault.lost_response_hidden()], served=served())
    r = controller(fake, module_dir).run()
    assert r["result"] == "NOT_RUN"
    assert any("omitted from every LIST cannot be excluded" in n
               for n in r["notes"])
    assert len(fake.leaked()) == 1, "the fake confirms the residual is real"


def test_an_acknowledged_terminate_with_the_pod_still_there_is_not_clean(
        module_dir):
    """ACK, and the pod stays; LIST hides it. Iteration 2's teardown would
    have reported this clean: acknowledged and absent from the listing."""
    fake = prov.FakeProvider(served=served(),
                             terminate_faults=[prov.Fault.ack_but_keep()])
    ctl = controller(fake, module_dir)
    original = ctl.raw_provider.create_pod

    def create_then_hide(body):
        out = original(body)
        fake._hidden.add(out["id"])
        return out
    ctl.raw_provider.create_pod = create_then_hide
    r = ctl.run()
    d = six(r)
    assert fake.leaked(), "it really is still there"
    assert r["cleanup"]["operational_cleanup"] is False
    assert d["cleanup_safe"] is False
    assert d["pod_state"] == ("UNCERTAIN: LIST omits it but GET still "
                              "returns it")
    # No ledger was configured, so nothing on disk could resume it: the
    # receipt says so rather than implying a recovery path exists.
    assert d["resumable"] is False
    assert d["evidence_retained"]["ledger"] is False
    rc.validate(r)


def test_a_stale_listing_after_terminate_resolves_on_a_later_read(module_dir):
    fake = prov.FakeProvider(served=served(), stale_list_reads=2)
    r = controller(fake, module_dir).run()
    ev = r["pods"][0]["absence_evidence"]
    assert ev["reads"] == 3 and ev["list_omits"] and ev["get_absent"]
    assert r["cleanup"]["operational_cleanup"] is True


def test_a_persistent_list_get_disagreement_is_recorded_not_resolved(
        module_dir):
    fake = prov.FakeProvider(served=served(), stale_list_reads=10)
    r = controller(fake, module_dir).run()
    d = six(r)
    assert r["cleanup"]["operational_cleanup"] is False
    assert d["pod_state"] == "UNCERTAIN: GET says gone but LIST still shows it"
    assert d["provider_believes"]["list_contains_pod"] is True
    assert d["provider_believes"]["get_returns_pod"] is False


def test_a_transient_delete_failure_is_retried_and_clean(module_dir):
    fake = prov.FakeProvider(served=served(),
                             terminate_faults=[prov.Fault.http(502)])
    r = controller(fake, module_dir).run()
    assert six(r)["cleanup_safe"] is True and fake.leaked() == []


def test_an_unreadable_inventory_at_teardown_is_uncertainty(module_dir):
    fake = prov.FakeProvider(served=served(),
                             list_faults=[None] + [prov.Fault.http(503)] * 20)
    r = controller(fake, module_dir).run()
    d = six(r)
    assert r["cleanup"]["inventory_read_ok"] is False
    assert d["cleanup_safe"] is False
    assert d["pod_state"].startswith("UNCERTAIN")
    rc.validate(r)


def test_ambiguous_get_errors_during_the_watch_are_not_verdicts(module_dir):
    fake = prov.FakeProvider(served=served(),
                             get_faults=[prov.Fault.http(502)] * 3)
    r = controller(fake, module_dir, get_every_polls=1).run()
    assert r["result"] == "OK"


# ------------------------------------------------------------- the receipt

def test_a_not_run_receipt_lists_nothing_as_missing(module_dir):
    fake = prov.FakeProvider(create_faults=[prov.Fault.http(400)])
    r = controller(fake, module_dir).run()
    assert r["result"] == "NOT_RUN"
    assert r["artifacts_missing"] == []
    assert r["artifacts_expected"] == ["result.json"]


def test_a_receipt_may_not_claim_absence_its_evidence_contradicts():
    pod = rc.pod_record("p1", terminate_acknowledged=True,
                        observed_absent=True,
                        absence_evidence={"list_omits": True,
                                          "get_absent": False})
    rec = {"schema": rc.SCHEMA, "run_id": "x", "module": "m",
           "result": "OK", "bundle_sha256": "b", "pods": [pod],
           "cleanup": rc.cleanup_block([pod], True)}
    with pytest.raises(rc.ReceiptError):
        rc.validate(rec)


def test_iteration_two_estimates_are_the_regression_case():
    """L4 campaign: spec sheet $0.0259, scout-calibrated $0.0432, actual
    $0.0408. The spec sheet was ~37% LOW and the scout ~5.9% HIGH."""
    block = rc.estimates_block(0.0259, 0.0432, 0.0408)
    assert block["scout_error"] == pytest.approx(0.0588, abs=5e-4)
    assert block["spec_sheet_error"] == pytest.approx(-0.3652, abs=5e-4)
    assert abs(block["scout_error"]) < abs(block["spec_sheet_error"])


def test_the_watch_tightens_its_poll_near_the_expected_end(module_dir):
    waits = []
    clock = Clock()

    def sleep(s):
        waits.append(s)
        clock.sleep(s)
    tel = lambda i: START + PROG * (i + 1) if i < 40 else START + END  # noqa
    fake = prov.FakeProvider(served=served(tel=tel))
    ctl = launch.Controller(fake, spec_mod.from_dict(dict(SPEC)), module_dir,
                            budget_usd=5.0, poll_s=30.0, ready_poll_s=3.0,
                            now=clock.now, sleep=sleep,
                            expected_module_s=600.0)
    r = ctl.run()
    assert r["result"] == "OK"
    watch_waits = [w for w in waits if w in (30.0, launch.TIGHT_POLL_S)]
    assert 30.0 in watch_waits and launch.TIGHT_POLL_S in watch_waits
    first_tight = watch_waits.index(launch.TIGHT_POLL_S)
    assert all(w == launch.TIGHT_POLL_S for w in watch_waits[first_tight:])


# ----------------------------------------------- scout -> plan -> campaign

from prometheus_gpu import campaign as campaign_mod     # noqa: E402
from prometheus_gpu import fanout                       # noqa: E402


def _receipt(result="OK", cause="OK", gpu="NVIDIA RTX A4000", usd=0.04):
    return {"result": result, "gpu_used": gpu,
            "disposition": {"cause": cause},
            "cost": {"usd_estimated": usd}}


def _plan(decision="PROCEED"):
    return {"decision": decision,
            "preregistered_estimate": {"expected_usd": 0.0259},
            "calibrated_estimate": {"expected_usd": 0.0432}}


def test_the_chain_runs_scout_plan_campaign_and_scores_both_estimates():
    calls = []
    out = campaign_mod.run(
        fly_scout=lambda: calls.append("scout") or _receipt(gpu="NVIDIA L4"),
        calibrate=lambda s: calls.append("cal") or _plan(),
        fly_campaign=lambda p, g: calls.append(("camp", g)) or _receipt(
            usd=0.0408, gpu=g))
    assert calls == ["scout", "cal", ("camp", "NVIDIA L4")]
    assert out["campaign_result"] == "OK"
    assert out["estimates"]["scout_error"] == pytest.approx(0.0588, abs=5e-4)


def test_a_capacity_refusal_earns_one_unpinned_rescout():
    scouts = iter([_receipt(gpu="NVIDIA RTX A4000"), _receipt(gpu="NVIDIA L4")])
    camps = iter([_receipt("NOT_RUN", "NO_CAPACITY", usd=0.0),
                  _receipt(usd=0.0408, gpu="NVIDIA L4")])
    pinned = []
    out = campaign_mod.run(lambda: next(scouts), lambda s: _plan(),
                           lambda p, g: pinned.append(g) or next(camps))
    assert pinned == ["NVIDIA RTX A4000", "NVIDIA L4"]
    assert out["rescouts"] == 1 and out["campaign_result"] == "OK"


def test_the_chain_stops_honestly_when_capacity_never_returns():
    out = campaign_mod.run(
        lambda: _receipt(), lambda s: _plan(),
        lambda p, g: _receipt("NOT_RUN", "NO_CAPACITY", usd=0.0),
        max_rescouts=1)
    assert out["rescouts"] == 1
    assert "no capacity" in out["stopped_because"]


def test_only_a_confirmed_capacity_refusal_is_retried():
    """An ambiguous create must never become a second campaign."""
    camps = []
    out = campaign_mod.run(
        lambda: _receipt(), lambda s: _plan(),
        lambda p, g: camps.append(g) or _receipt("UNKNOWN",
                                                "CREATE_UNRESOLVED"))
    assert len(camps) == 1 and out["rescouts"] == 0


def test_a_refused_plan_or_a_failed_scout_flies_no_campaign():
    flown = []
    out = campaign_mod.run(lambda: _receipt(), lambda s: _plan("REFUSE"),
                           lambda p, g: flown.append(g))
    assert flown == [] and "REFUSED" in out["stopped_because"]
    out = campaign_mod.run(lambda: _receipt("FAILED", "NEVER_READY"),
                           lambda s: _plan(), lambda p, g: flown.append(g))
    assert flown == [] and "scout did not complete" in out["stopped_because"]


# --------------------------------------------------------------- fan-out

def _shard_served(ok=True):
    tel = frames(None, START, START + PROG,
                 START + PROG + (END if ok else
                                 END.replace('"ok"', '"failed"')))
    return served(tel=tel)


def _shards(module_dir, n=3):
    spec = spec_mod.from_dict(dict(SPEC))
    return [{"id": "s%d" % i, "spec": spec, "module_dir": module_dir,
             "budget_usd": 1.0} for i in range(n)]


def _clockless_kwargs():
    return {"poll_s": 30.0, "now": Clock().now, "sleep": lambda s: None}


def test_one_failed_shard_is_isolated_and_the_rest_complete(module_dir):
    fake = prov.FakeProvider(served_by_name={
        "camp-s0": _shard_served(), "camp-s1": _shard_served(ok=False),
        "camp-s2": _shard_served()})
    clock = Clock()
    out, results, _ = fanout.run(
        lambda: fake, _shards(module_dir), "camp",
        controller_kwargs={"poll_s": 30.0, "now": clock.now,
                           "sleep": clock.sleep}, concurrent=False)
    assert [s["result"] for s in out["shards"]] == ["OK", "FAILED", "OK"]
    assert out["result"] == "PARTIAL"
    assert out["operational_cleanup"] is True and fake.leaked() == []
    assert out["distinct_pods"] is True
    assert [s["run_id"] for s in out["shards"]] == ["camp-s0", "camp-s1",
                                                    "camp-s2"]
    assert fake.calls["create"] == 3


def test_shards_run_concurrently_and_all_clean_up(module_dir):
    fake = prov.FakeProvider(served_by_name={
        "cc-s%d" % i: _shard_served() for i in range(3)})
    out, _r, ctls = fanout.run(
        lambda: fake, _shards(module_dir), "cc",
        controller_kwargs={"poll_s": 0.01, "ready_poll_s": 0.01},
        concurrent=True)
    assert out["result"] == "OK" and fake.leaked() == []
    # Each shard saw its siblings and did not refuse on them.
    assert all(c.allowed_pod_names for c in ctls)


def test_a_foreign_pod_refuses_the_whole_campaign_before_any_create(
        module_dir):
    fake = prov.FakeProvider()
    fake.create_pod({"name": "another-seat"})
    with pytest.raises(fanout.CampaignRefused):
        fanout.run(lambda: fake, _shards(module_dir), "camp")
    assert fake.calls["create"] == 1, "only the foreign pod exists"


def test_fail_fast_stops_siblings_as_a_campaign_decision(module_dir):
    fake = prov.FakeProvider(served_by_name={
        "ff-s0": served(tel=frames(None, START, START + END.replace(
            '"ok"', '"failed"'))),
        "ff-s1": served(tel=lambda i: START + PROG * (i + 1))})
    clock = Clock()
    out, results, _ = fanout.run(
        lambda: fake, _shards(module_dir, 2), "ff", fail_fast=True,
        controller_kwargs={"poll_s": 30.0, "now": clock.now,
                           "sleep": clock.sleep}, concurrent=False)
    assert out["shards"][0]["result"] == "FAILED"
    assert out["shards"][1]["cause"] == "CAMPAIGN_FAIL_FAST"
    assert fake.leaked() == []


# ---------------------------------------- container restart (flight F2)

def _bootstrap():
    from prometheus_gpu import dryrun as dr
    spec = spec_mod.from_dict(dict(SPEC))
    meta = {"run_id": "r", "seat": "Aether", "workdir": "/app/module",
            "artifact_dir": "/app/out",
            "telemetry_path": "/app/out/telemetry.jsonl", "image": "img"}
    transport = {"fetch_cmd": "curl -o b.tar.gz http://x",
                 "local_name": "b.tar.gz", "bundle_sha256": "a" * 64}
    return dr.build_bootstrap(spec, meta, transport), spec


def test_a_restarted_container_serves_but_never_reruns_the_module():
    """RunPod restarts a container whose main process died, re-running the
    bootstrap on the same disk. The guard must come before `stage boot`,
    bring the server back, and exit without reaching the module."""
    boot, spec = _bootstrap()
    guard_at = boot.index("stage restart")
    assert guard_at < boot.index("stage boot")
    guard = boot[guard_at:boot.index("fi\n", guard_at)]
    assert "python3 -u /app/_serve.py &" in guard
    assert "exit 0" in guard
    assert spec["entrypoint"] not in guard, "the guard must not run the module"
    assert "pip install" not in guard


def test_a_container_restart_during_the_watch_is_its_own_disposition(
        module_dir):
    fake = prov.FakeProvider(served=served(
        tel=lambda i: START + PROG * (i + 1),
        extra={launch.STAGES_PATH: frames(
            stages("boot", "module_start"), stages("boot", "module_start"),
            stages("boot", "module_start", "restart"))}))
    r = controller(fake, module_dir).run()
    d = six(r)
    assert r["result"] == "UNKNOWN" and d["cause"] == "CONTAINER_RESTARTED"
    assert d["cleanup_safe"] is True and fake.leaked() == []


def test_the_soak_fault_kills_the_server_and_not_the_bootstrap_shell():
    import importlib.util
    path = os.path.join(os.path.dirname(__file__), "..", "runpod",
                        "examples", "soak", "run.py")
    spec = importlib.util.spec_from_file_location("soak_run", path)
    soak = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(soak)
    boot, _spec = _bootstrap()
    assert soak.is_server_argv([b"python3", b"-u", b"/app/_serve.py"])
    assert not soak.is_server_argv([b"/bin/bash", b"-c", boot.encode()])
    assert not soak.is_server_argv([b"python3", b"-u", b"/app/_sample.py"])


def test_a_pod_clock_that_answers_late_is_still_measured(module_dir):
    """F2: /_clock failed in the first seconds and was never asked again."""
    clock = Clock()
    late = lambda i: (None if i < 12                       # noqa: E731
                      else json.dumps({"epoch": clock.t + 1000.0}))
    tel = lambda i: START + PROG * (i + 1) if i < 12 else START + END  # noqa
    fake = prov.FakeProvider(served=served(tel=tel,
                                           extra={launch.CLOCK_PATH: late}))
    ctl = controller(fake, module_dir, clock=clock)
    r = ctl.run()
    assert r["result"] == "OK"
    assert r["clock_sync"]["start"] is not None
    assert r["clock_sync"]["start"]["offset_s"] == pytest.approx(1000.0, abs=1)
    assert ctl._clock_tries <= 6
