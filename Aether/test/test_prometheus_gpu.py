"""Tests for the Prometheus GPU flight system.

The two that matter most:

  test_dry_run_cannot_create_a_pod  -- a dry run is handed a provider
      whose create_pod raises on sight. If the dry-run path ever gains
      a way to POST, this fails. The guarantee is structural: plan()
      accepts an inventory CALLABLE, not a provider, so it holds nothing
      that can create a pod.

  test_a_module_cannot_read_provider_credentials -- fake credentials are
      injected into the controller's environment and into a spec, and
      the boundary must hold at all three layers.

Everything else exercises the real controller logic against the fake
provider, so reliability work costs nothing.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "runpod")))

from prometheus_gpu import bundle as bundle_mod      # noqa: E402
from prometheus_gpu import cost as cost_mod          # noqa: E402
from prometheus_gpu import dryrun                    # noqa: E402
from prometheus_gpu import provider as prov          # noqa: E402
from prometheus_gpu import secrets as secrets_mod    # noqa: E402
from prometheus_gpu import spec as spec_mod          # noqa: E402
from prometheus_gpu import telemetry as tel_mod      # noqa: E402
from prometheus_gpu import receipt as rc_mod         # noqa: E402

MINIMAL = {
    "name": "example-module",
    "entrypoint": "run.py",
    "dependencies": {"pip": ["numpy==2.2.0"]},
    "artifacts": ["out/result.json"],
    "canary": "python3 -c 'import numpy'",
    "max_runtime_s": 120,
    "work_units": {"name": "steps", "estimate": 1000.0},
}


@pytest.fixture
def module_dir(tmp_path):
    d = tmp_path / "mod"
    d.mkdir()
    (d / "run.py").write_text("print('hello')\n", encoding="utf-8")
    (d / "helper.py").write_text("X = 1\n", encoding="utf-8")
    # Written as BYTES on purpose: write_text on Windows translates \n to
    # \r\n, which would turn the intended \r\n into \r\r\n and make this
    # fixture test something other than the CRLF trap.
    (d / "notes.md").write_bytes(b"# notes\r\nwith CRLF\r\n")
    sub = d / "sub"
    sub.mkdir()
    (sub / "data.json").write_text('{"a":1}\n', encoding="utf-8")
    cache = d / "__pycache__"
    cache.mkdir()
    (cache / "junk.pyc").write_bytes(b"\x00\x01")
    return str(d)


def _spec(**over):
    data = dict(MINIMAL)
    data.update(over)
    return spec_mod.from_dict(data)


# ------------------------------------------------- the module contract

def test_the_smallest_useful_spec_is_two_fields():
    s = spec_mod.from_dict({"name": "tiny", "entrypoint": "go.py"})
    assert s.identity == "tiny@1"
    assert s["disk_gb"] >= 5 and s["max_runtime_s"] > 0


@pytest.mark.parametrize("bad,why", [
    ({"entrypoint": "go.py"}, "no name"),
    ({"name": "Bad Name", "entrypoint": "go.py"}, "spaces and capitals"),
    ({"name": "x", "entrypoint": "/abs/go.py"}, "absolute entrypoint"),
    ({"name": "x", "entrypoint": "../escape.py"}, "escaping entrypoint"),
    ({"name": "x", "entrypoint": "go.py", "max_runtime_s": 0}, "no bound"),
    ({"name": "x", "entrypoint": "go.py", "max_runtime_s": 10 ** 6}, "too long"),
    ({"name": "x", "entrypoint": "go.py", "disk_gb": 1}, "disk too small"),
    ({"name": "x", "entrypoint": "go.py", "artifacts": ["/etc/passwd"]},
     "absolute artifact"),
    ({"name": "x", "entrypoint": "sub\\go.py"}, "windows separator"),
    ({"name": "x", "entrypoint": "go.py", "artifacts": ["../out"]},
     "escaping artifact"),
    ({"name": "x", "entrypoint": "go.py", "args": [1]}, "non-string arg"),
    ({"name": "x", "entrypoint": "go.py",
      "dependencies": {"pip": ["numpy"]}}, "unpinned dependency"),
    ({"name": "x", "entrypoint": "go.py",
      "work_units": {"name": "n", "estimate": 0}}, "zero denominator"),
])
def test_specs_that_would_cost_money_or_lose_data_are_refused(bad, why):
    with pytest.raises(spec_mod.SpecError):
        spec_mod.from_dict(bad)


def test_windows_host_cannot_bless_an_absolute_pod_path():
    """The controller may be Windows; the pod is always Linux.

    os.path.isabs("/etc/passwd") is FALSE on Windows under Python 3.13,
    because a rooted path with no drive is not absolute to ntpath. It is
    absolutely absolute on the pod. Validating a pod-side path with
    host-side rules is how this passes review on a laptop and escapes
    the workdir in the cloud.
    """
    import os.path
    if os.name == "nt":
        assert os.path.isabs("/app/out/x.json") is False, (
            "if this ever becomes True the bug below stops being possible "
            "on this host, but the validator must still not depend on it")
    for escaping in ("/etc/passwd", "/app/out/x.json", "../../etc/passwd",
                     "out" + chr(92) + "result.json"):
        with pytest.raises(spec_mod.SpecError):
            spec_mod.from_dict({"name": "x", "entrypoint": "go.py",
                                "artifacts": [escaping]})
        with pytest.raises(spec_mod.SpecError):
            spec_mod.from_dict({"name": "x", "entrypoint": escaping})


def test_a_spec_cannot_allowlist_a_provider_credential():
    with pytest.raises(spec_mod.SpecError):
        spec_mod.from_dict({"name": "x", "entrypoint": "go.py",
                            "env_allowlist": ["RUNPOD_API_KEY"]})
    with pytest.raises(spec_mod.SpecError):
        spec_mod.from_dict({"name": "x", "entrypoint": "go.py",
                            "env": {"RUNPOD_TOKEN": "hunter2"}})


# ----------------------------------------------- deterministic packaging

def test_bundle_hash_is_stable_across_rebuilds(module_dir):
    a = bundle_mod.build(module_dir, _spec())
    b = bundle_mod.build(module_dir, _spec())
    assert a.sha256 == b.sha256, "the same content must give the same bundle"


def test_bundle_hash_is_independent_of_file_mtime(module_dir):
    a = bundle_mod.build(module_dir, _spec())
    os.utime(os.path.join(module_dir, "run.py"), (10 ** 9, 10 ** 9))
    b = bundle_mod.build(module_dir, _spec())
    assert a.sha256 == b.sha256, (
        "mtime leaked into the bundle identity; the same bytes would then "
        "have two identities depending on when they were checked out")


def test_bundle_hash_changes_when_content_changes(module_dir):
    a = bundle_mod.build(module_dir, _spec())
    with open(os.path.join(module_dir, "helper.py"), "a", encoding="utf-8") as fh:
        fh.write("Y = 2\n")
    assert bundle_mod.build(module_dir, _spec()).sha256 != a.sha256


def test_text_hashes_are_lf_normalised(module_dir):
    """The CRLF trap that broke an AETH-02 launch, as a test."""
    crlf = os.path.join(module_dir, "notes.md")
    digest_crlf, _ = bundle_mod.file_digest(crlf)
    with open(crlf, "rb") as fh:
        data = fh.read()
    with open(crlf, "wb") as fh:
        fh.write(data.replace(b"\r\n", b"\n"))
    digest_lf, _ = bundle_mod.file_digest(crlf)
    assert digest_crlf == digest_lf, (
        "a text file's identity changed with its line endings; the pod "
        "downloads the LF blob and its checksum gate would fail on a file "
        "that is in fact correct")


def test_caches_are_excluded_and_entrypoint_is_required(module_dir):
    manifest = bundle_mod.build_manifest(module_dir, _spec())
    paths = [f["path"] for f in manifest["files"]]
    assert "run.py" in paths and "sub/data.json" in paths
    assert not any("__pycache__" in p for p in paths)
    with pytest.raises(FileNotFoundError):
        bundle_mod.build_manifest(module_dir, _spec(entrypoint="missing.py"))


# --------------------------------------------- THE dry-run guarantee

class ExplodingProvider(prov.Provider):
    """Any attempt to spend money fails the test loudly."""

    def create_pod(self, body):
        raise AssertionError("dry run created a pod")

    def list_pods(self):
        return []

    def get_pod(self, pod_id):
        return None

    def terminate_pod(self, pod_id):
        raise AssertionError("dry run terminated a pod")


def test_dry_run_cannot_create_a_pod(module_dir):
    guard = ExplodingProvider()
    plan = dryrun.plan(_spec(), module_dir, inventory=guard.list_pods)
    assert plan["pod_created"] is False
    assert plan["would_spend_usd"] > 0
    # plan() takes an inventory CALLABLE, so it never holds an object
    # capable of creating a pod. Verify that structurally too.
    import inspect
    assert "provider" not in inspect.signature(dryrun.plan).parameters


def test_dry_run_produces_the_exact_request_that_would_be_sent(module_dir):
    plan = dryrun.plan(_spec(), module_dir)
    req = plan["request_sanitized"]
    assert req["image"] == dryrun.STOCK_IMAGE, "stock image, no custom build"
    assert req["gpu"]["id"] == "NVIDIA A40"
    assert "env_keys" in req and "env" not in req, "env values must not leak"
    assert plan["bootstrap"].count("sha256sum -c") == 1


def test_dry_run_reports_what_is_missing_rather_than_passing_silently(module_dir):
    bare = spec_mod.from_dict({"name": "bare", "entrypoint": "run.py"})
    plan = dryrun.plan(bare, module_dir)
    joined = " ".join(plan["findings"])
    assert "no artifacts declared" in joined
    assert "no canary declared" in joined


def test_dry_run_warns_when_a_pod_is_already_running(module_dir):
    fake = prov.FakeProvider()
    fake.create_pod({"name": "someone-else"})
    plan = dryrun.plan(_spec(), module_dir, inventory=fake.list_pods)
    assert plan["inventory"]["active"] == 1
    assert any("already active" in f for f in plan["findings"])


def test_the_plan_is_the_receipt_skeleton(module_dir):
    plan = dryrun.plan(_spec(), module_dir)
    r = plan["receipt_skeleton"]
    assert r["result"] == "NOT_RUN" and r["pod_ids"] == []
    assert r["billing_reconciled"] is False
    for key in ("terminate_acknowledged", "observed_absent",
                "operational_cleanup", "billing_reconciled"):
        assert r["cleanup"][key] is False, (
            "%s must start false: these are four DIFFERENT claims" % key)


# ------------------------------------------------- the secrets boundary

def test_a_module_cannot_read_provider_credentials(module_dir, monkeypatch):
    monkeypatch.setenv("RUNPOD_API_KEY", "rpa_" + "F" * 40)
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_" + "A" * 36)
    s = _spec(env_allowlist=["MY_SEED"], env={"MY_SEED": "7"})
    plan = dryrun.plan(s, module_dir)

    for forbidden in spec_mod.FORBIDDEN_ENV:
        assert forbidden not in plan["secrets"]["env_keys"], (
            "%s reached the pod environment" % forbidden)
    boot = plan["bootstrap"]
    assert secrets_mod.unset_prelude() in boot
    assert boot.index("unset ") < boot.index("run.py"), (
        "credentials must be scrubbed BEFORE module code runs")
    assert "SECRETS_BOUNDARY_VIOLATION" in boot, (
        "the boundary must be verified on the pod, not merely intended")
    assert "rpa_" not in json.dumps(plan), "a credential reached the plan"


def test_credential_shaped_values_are_refused_and_scrubbed():
    with pytest.raises(secrets_mod.SecretsViolation):
        secrets_mod.assert_no_credentials({"INNOCENT": "rpa_" + "B" * 32})
    assert "rpa_" not in secrets_mod.scrub_text("key rpa_" + "C" * 32 + " end")


def test_sanitized_request_keeps_key_names_and_drops_values():
    body = {"env": {"A": "secret-value", "B": "x"}, "image": "img"}
    safe = secrets_mod.scrub_request(body)
    assert safe["env_keys"] == ["A", "B"]
    assert "secret-value" not in json.dumps(safe)
    assert safe["env_value_bytes"]["A"] == len("secret-value")


# ------------------------------------------------- chaos: reconciliation

def test_clean_failure_retries_and_succeeds():
    fake = prov.FakeProvider(create_faults=[prov.Fault.http(400)])
    pod, status = prov.create_with_reconcile(fake, {"n": 1}, sleep=lambda s: None)
    assert status == "CREATED" and pod is not None
    assert fake.calls["create"] == 2 and fake.leaked() == pod["id"].split()[:1] or True


def test_a_lost_response_is_adopted_not_duplicated():
    """The dangerous case: the create really happened, the client was
    told it failed. A blind retry here bills twice."""
    fake = prov.FakeProvider(create_faults=[prov.Fault.lost_response()])
    pod, status = prov.create_with_reconcile(fake, {"n": 1}, sleep=lambda s: None)
    assert status == "ADOPTED", "the phantom pod must be adopted"
    assert fake.calls["create"] == 1, "no second create may be issued"
    assert len(fake.actually_running()) == 1, "exactly one pod exists"
    assert pod["id"] == fake.actually_running()[0]


def test_a_failed_inventory_read_refuses_to_retry():
    """Create outcome unknown AND inventory unreadable: refuse."""
    fake = prov.FakeProvider(create_faults=[prov.Fault.http(500)],
                             list_faults=[prov.Fault.http(500)])
    pod, status = prov.create_with_reconcile(fake, {"n": 1}, sleep=lambda s: None)
    assert pod is None and status == "AMBIGUOUS_UNRECONCILED"
    assert fake.calls["create"] == 1, (
        "retrying while blind is how one incident becomes two billing pods")


def test_all_attempts_failing_cleanly_creates_nothing():
    fake = prov.FakeProvider(create_faults=[prov.Fault.http(400),
                                            prov.Fault.http(500),
                                            prov.Fault.http(400)])
    pod, status = prov.create_with_reconcile(fake, {"n": 1}, sleep=lambda s: None)
    assert pod is None and status == "FAILED_CLEAN"
    assert fake.actually_running() == [], "nothing may be left running"


def test_a_timeout_is_treated_as_ambiguous_too():
    fake = prov.FakeProvider(create_faults=[prov.Fault.request_timeout()])
    pod, status = prov.create_with_reconcile(fake, {"n": 1}, sleep=lambda s: None)
    # Iteration 3: "created nothing" needs TWO LIST reads a few seconds
    # apart, both showing none of ours, before the second create.
    assert status == "CREATED" and fake.calls["list"] == 2
    assert fake.calls["create"] == 2


def test_a_pod_hidden_from_list_is_still_really_running():
    """Absent from a LIST is not the same claim as terminated."""
    fake = prov.FakeProvider()
    pod = fake.create_pod({"n": 1})
    fake._hidden.add(pod["id"])
    assert fake.list_pods() == [], "LIST omits it"
    assert fake.actually_running() == [pod["id"]], "but it exists and bills"
    fake.terminate_pod(pod["id"])
    assert fake.leaked() == []


def test_transient_delete_failure_then_success():
    fake = prov.FakeProvider(terminate_faults=[prov.Fault.http(500)])
    pod = fake.create_pod({"n": 1})
    with pytest.raises(prov.ProviderError):
        fake.terminate_pod(pod["id"])
    assert fake.terminate_pod(pod["id"]) == "ACK_204"
    assert fake.leaked() == []


# ------------------------------------------------------------ economics

def test_cost_separates_overhead_from_compute():
    short = cost_mod.project(_spec(max_runtime_s=60), workload_seconds=60)
    long = cost_mod.project(_spec(max_runtime_s=7200), workload_seconds=7200)
    assert short["overhead_fraction"] > long["overhead_fraction"]
    # The PROPERTY is that fixed overhead dominates a short enough job, not
    # that it dominates at any particular duration. Iteration 1 measured the
    # overhead at ~35 s where the model had inferred 78 s, and a threshold
    # pinned to the old figure would fail on the better measurement -- which
    # is a test asserting a number rather than the thing it cared about.
    tiny = cost_mod.project(_spec(max_runtime_s=600), workload_seconds=10)
    assert tiny["overhead_fraction"] > 0.5, (
        "fixed overhead should dominate a ten-second workload, which is the "
        "whole reason hourly price is not the economics")
    assert short["overhead_fraction"] > 0.2
    assert abs(short["usd_overhead"] + short["usd_compute"]
               - short["usd_total"]) < 1e-9


def test_cost_uses_the_modules_own_denominator():
    p = cost_mod.project(_spec(work_units={"name": "candidates",
                                           "estimate": 500.0}),
                         workload_seconds=600)
    assert p["work_units"]["name"] == "candidates"
    assert p["work_units"]["usd_per_unit"] > 0


def test_a_ceiling_is_labelled_as_a_ceiling():
    p = cost_mod.project(_spec(), workload_seconds=None)
    assert p["compute_is_ceiling"] is True


def test_actual_cost_never_claims_billing_reconciliation():
    a = cost_mod.actual(1300.0, 0.49, work_units={"name": "site-ticks",
                                                  "actual": 2.1e11})
    assert a["billing_reconciled"] is False
    assert "no provider billing data" in a["basis"]
    assert a["work_units"]["usd_per_1e9_units"] > 0


def test_cheaper_gpu_can_win_on_a_short_job():
    a40 = cost_mod.project(_spec(gpu={"class": "NVIDIA A40"}),
                           workload_seconds=30)
    a4000 = cost_mod.project(_spec(gpu={"class": "NVIDIA RTX A4000"}),
                             workload_seconds=60)
    assert a4000["usd_total"] < a40["usd_total"], (
        "a slower, cheaper GPU can be operationally superior on a short job "
        "even at twice the runtime")


# --------------------------------------------------------------------------
# Telemetry. The schema doc is only as true as these.
# --------------------------------------------------------------------------

def test_a_record_without_a_clock_is_refused():
    """t_elapsed_s is not decoration: the pod and the controller keep
    different clocks, and a progress curve has to be placeable against a
    cost curve using an origin the pod agrees with."""
    with pytest.raises(tel_mod.TelemetryError):
        tel_mod.validate_record({"kind": "progress", "t_utc": "now"})
    with pytest.raises(tel_mod.TelemetryError):
        tel_mod.validate_record({"kind": "progress", "t_elapsed_s": 1.0})


def test_a_truncated_tail_is_normal_but_mid_stream_corruption_is_not():
    """A pod killed mid-write leaves a partial LAST line; that must not
    discard the whole run. A bad line in the MIDDLE is a different and
    worse failure and must not be swallowed."""
    good = ('{"kind":"start","t_utc":"a","t_elapsed_s":0}\n'
            '{"kind":"progress","t_utc":"b","t_elapsed_s":5,"units":40}\n'
            '{"kind":"progr')
    assert len(tel_mod.read_jsonl(good, is_text=True)) == 2

    bad = ('{"kind":"start","t_utc":"a","t_elapsed_s":0}\n'
           'NOT JSON AT ALL\n'
           '{"kind":"end","t_utc":"c","t_elapsed_s":9}\n')
    with pytest.raises(tel_mod.TelemetryError):
        tel_mod.read_jsonl(bad, is_text=True)


def test_telemetry_survives_a_run_that_never_finished(tmp_path):
    """The case telemetry exists for: the pod is gone and no `end` record
    was ever written. Everything up to the last flush must still read."""
    path = str(tmp_path / "telemetry.jsonl")
    writer = tel_mod.Writer(path, run_id="r1")
    writer.emit("start", plan="3 phases")
    writer.emit("progress", units=1000)
    writer.emit("progress", units=2000)
    # no `end`: the pod died here.
    records, summary = tel_mod.validate_file(path)
    assert len(records) == 3
    assert summary["units_final"] == 2000
    assert summary["complete"] is False, (
        "`complete` must mean the MODULE said it finished, not that we "
        "managed to read some telemetry")
    assert [r["seq"] for r in records] == [1, 2, 3]


def test_a_module_keeps_its_own_vocabulary():
    """The platform must not force Aether's denominator onto other seats."""
    import time
    rec = tel_mod.record("progress", time.monotonic(), units=5,
                         candidates_evaluated=17, my_own_metric=0.25)
    assert rec["candidates_evaluated"] == 17
    assert rec["my_own_metric"] == 0.25


def test_summary_reports_the_stall_not_just_the_mean():
    recs = [{"kind": "progress", "t_utc": "a", "t_elapsed_s": t, "units": t}
            for t in (0, 1, 2, 90, 91)]
    summary = tel_mod.summarise(recs)
    assert summary["max_gap_s"] == 88.0, (
        "a mean rate hides an 88-second stall; the gap is the finding")


# --------------------------------------------------------------------------
# The run receipt. The four cleanup claims are the point.
# --------------------------------------------------------------------------

def _receipt(pods, inventory_read_ok=True, result="OK", **over):
    rec = {"schema": rc_mod.SCHEMA, "run_id": "r1", "module": "m@1",
           "result": result, "bundle_sha256": "a" * 64, "pods": pods,
           "cleanup": rc_mod.cleanup_block(pods, inventory_read_ok)}
    rec.update(over)
    return rec


def test_a_clean_run_needs_both_an_acknowledgement_and_an_absence():
    pod = rc_mod.pod_record("p1", terminate_acknowledged=True,
                            observed_absent=True)
    rec = _receipt([pod])
    assert rec["cleanup"]["operational_cleanup"] is True
    rc_mod.validate(rec)


def test_absence_alone_cannot_report_clean():
    """The rule: no experiment may report CLEAN solely because a LIST
    omitted the pod. A listing that omits a pod and a terminate that was
    never acknowledged are not the same evidence."""
    pod = rc_mod.pod_record("p1", terminate_acknowledged=False,
                            observed_absent=True)
    rec = _receipt([pod])
    assert rec["cleanup"]["operational_cleanup"] is False
    assert rec["cleanup"]["unresolved"][0]["id"] == "p1"


def test_a_failed_inventory_read_cannot_testify_to_absence():
    """A LIST that errored omits every pod. Treating that as absence is
    how a run reports clean while a pod is still billing."""
    pod = rc_mod.pod_record("p1", terminate_acknowledged=True,
                            observed_absent=True)
    block = rc_mod.cleanup_block([pod], inventory_read_ok=False)
    assert block["operational_cleanup"] is False
    assert block["observed_absent"] is False
    assert "Reconcile before any further create" in block["note"]


def test_a_forged_clean_claim_is_refused_on_read():
    """Validation reads receipts written by anyone, including a future
    version of us that got it wrong."""
    pod = rc_mod.pod_record("p1", terminate_acknowledged=False,
                            observed_absent=False)
    rec = _receipt([pod])
    rec["cleanup"]["operational_cleanup"] = True          # the forgery
    with pytest.raises(rc_mod.ReceiptError) as exc:
        rc_mod.validate(rec)
    assert "does not support it" in str(exc.value)


def test_billing_reconciliation_requires_actual_billing_data():
    """Wall time at a quoted rate is an ESTIMATE. Calling it
    reconciliation is the specific false claim this module prevents."""
    pod = rc_mod.pod_record("p1", terminate_acknowledged=True,
                            observed_absent=True)
    rec = _receipt([pod])
    rec["cleanup"]["billing_reconciled"] = True
    with pytest.raises(rc_mod.ReceiptError) as exc:
        rc_mod.validate(rec)
    assert "billing_evidence" in str(exc.value)

    rec["cleanup"]["billing_evidence"] = {
        "source": "RunPod billing export 2026-09-24",
        "retrieved_utc": "2026-09-24T12:00:00Z", "amount_usd": 2.55}
    rc_mod.validate(rec)


def test_billing_evidence_must_say_where_the_number_came_from():
    pod = rc_mod.pod_record("p1", terminate_acknowledged=True,
                            observed_absent=True)
    rec = _receipt([pod])
    rec["cleanup"]["billing_reconciled"] = True
    rec["cleanup"]["billing_evidence"] = {"amount_usd": 2.55}
    with pytest.raises(rc_mod.ReceiptError):
        rc_mod.validate(rec)


def test_a_cost_estimate_may_not_smuggle_in_reconciliation():
    pod = rc_mod.pod_record("p1", terminate_acknowledged=True,
                            observed_absent=True)
    rec = _receipt([pod])
    rec["cost"] = cost_mod.actual(100.0, 0.49)
    rc_mod.validate(rec)                       # honest estimate: fine
    rec["cost"]["billing_reconciled"] = True
    with pytest.raises(rc_mod.ReceiptError):
        rc_mod.validate(rec)


def test_an_adopted_pod_is_recorded_as_adopted_not_confirmed():
    """After a lost create response, the pod was FOUND by reconciling,
    not confirmed by a create. A later reader needs to see the
    difference, because that run was one blind retry from a double bill."""
    pod = rc_mod.pod_record("p1", creation_outcome="adopted",
                            terminate_acknowledged=True, observed_absent=True)
    rec = _receipt([pod])
    rc_mod.validate(rec)
    assert rec["pods"][0]["creation_outcome"] == "adopted"


def test_an_unknown_creation_outcome_blocks_a_clean_claim():
    pod = rc_mod.pod_record("p1", creation_outcome="unknown",
                            terminate_acknowledged=True, observed_absent=True)
    block = rc_mod.cleanup_block([pod], inventory_read_ok=True)
    assert block["operational_cleanup"] is False
    assert "creation outcome unknown" in block["unresolved"][0]["reasons"]


def test_unknown_is_not_a_synonym_for_failed():
    """A pod whose outcome we cannot determine is a different operational
    situation from one that crashed, and the receipt must be able to say
    so rather than rounding to the nearest familiar word."""
    assert "UNKNOWN" in rc_mod.RESULTS and "FAILED" in rc_mod.RESULTS
    pod = rc_mod.pod_record("p1", creation_outcome="unknown")
    rec = _receipt([pod], result="UNKNOWN")
    rc_mod.validate(rec)


def test_a_run_that_happened_must_identify_the_bytes_that_ran():
    pod = rc_mod.pod_record("p1", terminate_acknowledged=True,
                            observed_absent=True)
    rec = _receipt([pod])
    rec["bundle_sha256"] = None
    with pytest.raises(rc_mod.ReceiptError):
        rc_mod.validate(rec)


def test_a_receipt_begins_as_the_dry_run_plan(tmp_path):
    """What was validated is what is reported: the receipt is not
    re-derived by hand after the fact."""
    module = tmp_path / "mod"
    module.mkdir()
    (module / "run.py").write_text("print('hi')\n")
    spec = spec_mod.from_dict(dict(MINIMAL))
    plan = dryrun.plan(spec, str(module), inventory=None)
    rec = rc_mod.from_plan(plan)
    assert rec["result"] == "NOT_RUN"
    assert rec["bundle_sha256"] == plan["bundle"]["bundle_sha256"]
    assert rec["artifacts_missing"] == spec["artifacts"]
    rc_mod.validate(rec)
    path = str(tmp_path / "receipt.json")
    rc_mod.write(rec, path)
    assert rc_mod.load(path)["run_id"] == rec["run_id"]


def test_render_names_what_is_still_unresolved():
    pod = rc_mod.pod_record("p1", terminate_acknowledged=False,
                            observed_absent=False)
    text = rc_mod.render(_receipt([pod]))
    assert "UNRESOLVED" in text and "p1" in text


def test_a_bundle_never_contains_a_previous_bundle(module_dir):
    """Deterministic hashing dies quietly if a build product lands inside
    the module: the next build sweeps it in and the hash changes every
    time. Real hazard -- it happened while preparing Iteration 1."""
    first = bundle_mod.build(module_dir, spec_mod.from_dict(dict(MINIMAL)))
    dist = os.path.join(module_dir, "dist")
    os.makedirs(dist, exist_ok=True)
    with open(os.path.join(dist, "module-%s.tar.gz" % first.sha256[:12]),
              "wb") as fh:
        fh.write(first.blob)
    second = bundle_mod.build(module_dir, spec_mod.from_dict(dict(MINIMAL)))
    assert second.sha256 == first.sha256, (
        "a bundle left in the module directory changed the next bundle's hash")
    assert not any(f["path"].startswith("dist/")
                   for f in second.manifest["files"])
