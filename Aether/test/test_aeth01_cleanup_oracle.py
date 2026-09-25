"""Offline Review 03 qualification; no credentials, sockets, or paid calls.

Run: python -m pytest Aether/test/test_aeth01_cleanup_oracle.py -q
The oracle imports no production code. Only comparison tests load the reaper;
their trace comes from fake endpoint returns, never cached policy windows.
"""

import ast
import builtins
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pytest

from reference import cleanup_aeth01_oracle as oracle


EPOCH = 1_800_000_000.0
IDS = ("one", "two")
FIXTURE_HASH = hashlib.sha256(b"synthetic local state; not an authoritative seal").hexdigest()


def sample(seconds, ids=IDS, **changes):
    row = {"utc": EPOCH + seconds, "mono": float(seconds), "list_complete": True,
           "list_owned_ids": [], "get_results": {pid: "MISSING" for pid in ids}}
    row.update(changes)
    return row


def healthy(start=0, end=3600, step=60, ids=IDS):
    return [sample(t, ids) for t in range(start, end + 1, step)]


def permits(trace, **changes):
    args = dict(known_ids=IDS, horizon=3600, cutoff=EPOCH, last_local_event=EPOCH - 1,
                supplied_state_hash=FIXTURE_HASH, current_state_hash=FIXTURE_HASH,
                now_utc=trace[-1]["utc"] if trace else EPOCH)
    args.update(changes)
    return oracle.permits_confirmation(trace, **args)


def test_oracle_is_small_and_imports_only_native_math_not_shared_policy():
    source = Path(oracle.__file__).read_text(encoding="utf-8")
    assert len(source.splitlines()) < 150
    tree = ast.parse(source)
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    assert len(imports) == 1
    node = imports[0]
    assert isinstance(node, ast.ImportFrom) and node.level == 0 and node.module == "math"
    assert [alias.name for alias in node.names] == ["isfinite"]
    forbidden = {"__import__", "eval", "exec", "compile", "open", "getattr", "globals", "locals"}
    assert not any(isinstance(node, ast.Name) and node.id in forbidden for node in ast.walk(tree))
    observed, real_import = [], builtins.__import__

    def only_math(name, globals=None, locals=None, fromlist=(), level=0):
        assert name == "math" and level == 0
        observed.append(name)
        return real_import(name, globals, locals, fromlist, level)

    namespace = {"__builtins__": dict(vars(builtins), __import__=only_math)}
    exec(compile(tree, str(oracle.__file__), "exec"), namespace)
    assert namespace["permits_confirmation"](
        healthy(), known_ids=IDS, horizon=3600, cutoff=EPOCH, last_local_event=None,
        supplied_state_hash=FIXTURE_HASH, current_state_hash=FIXTURE_HASH,
        now_utc=EPOCH + 3600)
    assert observed == ["math"]


@pytest.mark.parametrize("ids", [(), IDS])
def test_complete_hour_and_every_known_get_404_permit_but_do_not_prove_cleanup(ids):
    trace = healthy(ids=ids)
    before = deepcopy(trace)
    assert permits(trace, known_ids=ids)
    assert trace == before
    assert not permits(trace[:-1], known_ids=ids)
    # A 404 is only a MISSING response; absent/in-flight requests are different.
    if ids:
        trace[-1]["get_results"].pop(ids[-1])
        assert not permits(trace, known_ids=ids)


@pytest.mark.parametrize("at", [1800, 3600])
@pytest.mark.parametrize("result", ["RUNNING", "TERMINATED", "TRANSPORT_FAILED",
                                    "AUTH_FAILED", "SCHEMA_FAILED", "CONFLICT", None])
def test_stale_empty_list_cannot_hide_get_positive_or_failure(at, result):
    trace = healthy()
    trace[at // 60]["get_results"]["one"] = result
    assert not permits(trace)


def test_later_live_contradiction_revokes_early_termination_and_old_success():
    trace = healthy(end=3660)
    trace[0]["get_results"]["one"] = "TERMINATED"
    assert permits(trace)  # A fresh full hour starts at 60, not at termination.
    trace.append(sample(3720, get_results={"one": "RUNNING", "two": "MISSING"}))
    assert not permits(trace)
    trace.append(sample(3780, get_results={"one": "TERMINATED", "two": "MISSING"}))
    assert not permits(trace)  # A new TERMINATED cannot rescue an old horizon.


@pytest.mark.parametrize("complete,owned", [(False, []), (False, ["one"]), (True, ["one"])])
def test_list_failure_partial_page_or_owned_positive_never_contributes(complete, owned):
    trace = healthy()
    trace[30].update(list_complete=complete, list_owned_ids=owned)
    assert not permits(trace)
    trace.extend(healthy(start=3660, end=5460))
    assert permits(trace)  # Reset, not subtraction: 1860..5460 is a new hour.


def test_404_without_successful_list_never_covers_a_horizon():
    trace = healthy()
    for row in trace:
        row["list_complete"] = False
    assert not permits(trace)


def test_every_known_id_and_discovered_id_must_be_represented():
    trace = healthy()
    trace[30]["get_results"].pop("two")
    assert not permits(trace)
    assert not permits(healthy(ids=("one",)))  # Entirely omitted known ID.
    assert not permits(healthy(), known_ids=("one",))  # Hidden from supplied union.
    trace = healthy()
    trace[0]["list_owned_ids"] = ["unrepresented-duplicate"]
    assert not permits(trace)


@pytest.mark.parametrize("wall,mono", [(3600, 3600), (120, 60), (60, 120),
                                     (-60, 60), (60, -60), (63, 60)])
def test_gap_or_clock_jump_cannot_bridge_coverage(wall, mono):
    trace = healthy()
    for row in trace[30:]:
        row["utc"] += wall - 60
        row["mono"] += mono - 60
    assert not permits(trace)


def test_hour_blind_then_burst_and_scan_count_are_not_duration():
    assert not permits([sample(0)] + healthy(start=3600, end=3650, step=10))
    assert not permits(healthy(end=20, step=4))
    assert not permits(healthy(end=40, step=10), horizon=40)  # Only five samples.
    assert permits(healthy(end=50, step=10), horizon=50)


@pytest.mark.parametrize("short_clock", ["utc", "mono"])
def test_both_total_clock_spans_must_cover_horizon(short_clock):
    trace = healthy()
    for index, row in enumerate(trace):
        row[short_clock] -= index  # Adjacent deltas differ by only 1s.
    assert not permits(trace)  # 3600s in one clock, only 3540s in the other.
    assert permits(trace, horizon=3540)


def test_cutoff_is_inclusive_controller_ordering_strict_and_latest_fresh():
    trace = healthy()
    assert permits(trace, last_local_event=None)
    assert not permits(trace, cutoff=EPOCH + 1)
    assert not permits(trace, last_local_event=EPOCH)
    assert not permits(trace, last_local_event=EPOCH + 1800)
    assert permits(healthy(start=60, end=3660), last_local_event=EPOCH)
    assert permits(trace, now_utc=EPOCH + 3660)
    assert not permits(trace, now_utc=EPOCH + 3660.001)
    assert not permits(trace, now_utc=EPOCH + 3599)
    trace[10]["utc"] = EPOCH + 9999  # Future history cannot be hidden by later rows.
    assert not permits(trace)


@pytest.mark.parametrize("field", ["utc", "mono"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), None, True, "1800"])
def test_malformed_clocks_fail_closed(field, value):
    trace = healthy()
    trace[30][field] = value
    assert not permits(trace)


@pytest.mark.parametrize("changes", [{"horizon": 0}, {"horizon": True}, {"horizon": float("nan")},
                                    {"known_ids": ["one", "one"]}, {"last_local_event": "bad"},
                                    {"supplied_state_hash": ""}, {"current_state_hash": None}])
def test_invalid_inputs_fail_closed(changes):
    assert not permits(healthy(), **changes)


def test_empty_oversized_or_incomplete_trace_fails_closed():
    assert not permits([])
    assert not permits([sample(0)] * 10001)
    trace = healthy()
    del trace[30]["mono"]
    assert not permits(trace)
    trace = healthy()
    trace[-1]["list_complete"] = 1  # Truthiness is not successful completion.
    assert not permits(trace)


def write_durable_state(path, value):
    # The fixture's agreed hash convention is canonical JSON bytes on disk.
    with path.open("wb") as stream:
        stream.write(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())
        stream.flush()
        os.fsync(stream.fileno())


def disk_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_stale_report_hash_rejected_against_actual_current_durable_state(tmp_path):
    path = tmp_path / "state.json"
    write_durable_state(path, {"owned_ids": list(IDS), "revision": "A"})
    supplied_a = disk_hash(path)
    assert permits(healthy(), supplied_state_hash=supplied_a, current_state_hash=disk_hash(path))
    write_durable_state(path, {"owned_ids": list(IDS), "revision": "B", "status": "RUNNING"})
    assert not permits(healthy(), supplied_state_hash=supplied_a, current_state_hash=disk_hash(path))
    # Explicit authority ceiling: a pure checker cannot discover hidden B if
    # a caller lies about the current disk hash. This is NOT a valid seal.
    assert permits(healthy(), supplied_state_hash=supplied_a, current_state_hash=supplied_a)


class Clock:
    def __init__(self, utc=EPOCH):
        self.utc, self.mono = utc, 0.0

    def time(self):
        return self.utc

    def monotonic(self):
        return self.mono

    def sleep(self, seconds):
        self.utc += seconds
        self.mono += seconds


class TracedProvider:
    """Capture actual fixture endpoint outputs, including incomplete rounds."""

    def __init__(self, clock, manifest):
        self.clock, self.manifest = clock, manifest
        self.seed, self.scenario, self.at = True, "missing", 1800
        self.rows, self.deletes, self.deleted = [], [], set()
        self.pods = {pid: {"id": pid, "name": manifest["run_name"], "image": manifest["image"],
                           "env": {"AETH01_RUN_ID": manifest["run_id"]}, "status": "RUNNING"}
                     for pid in IDS}

    def visit_pods(self, visitor):
        row = dict(utc=self.clock.time(), mono=self.clock.monotonic(), list_complete=False,
                   list_owned_ids=[], get_results={})
        self.rows.append(row)
        if not self.seed and self.scenario == "list_failure" and self.clock.mono == self.at:
            raise TimeoutError("offline LIST failure")
        # After seeding, LIST stays stale/empty even if GET returns a live Pod.
        for pid in (IDS if self.seed else ()):
            if pid not in self.deleted:
                row["list_owned_ids"].append(pid)
                visitor(deepcopy(self.pods[pid]))
        row["list_complete"] = True

    def get_pod(self, pid):
        pod = deepcopy(self.pods[pid]) if self.seed and pid not in self.deleted else None
        anomaly = (not self.seed and pid == "one" and self.clock.mono >= self.at
                   and (self.scenario == "running" or self.clock.mono == self.at))
        if anomaly:
            if self.scenario == "get_failure":
                self.rows[-1]["get_results"][pid] = "TRANSPORT_FAILED"
                raise TimeoutError("offline GET failure")
            if self.scenario in {"running", "terminated", "conflict"}:
                pod = deepcopy(self.pods[pid])
                if self.scenario == "terminated":
                    pod["status"] = "TERMINATED"
                if self.scenario == "conflict":
                    pod["image"] = "different-image"
        if pod is None:
            result = "MISSING"  # Successful ambiguous GET 404, not an absence witness.
        elif (pod["id"] != pid or pod["name"] != self.manifest["run_name"]
              or pod["image"] != self.manifest["image"]
              or pod["env"].get("AETH01_RUN_ID") != self.manifest["run_id"]):
            result = "CONFLICT"
        else:
            result = pod["status"]
        self.rows[-1]["get_results"][pid] = result
        return pod

    def terminate_pod(self, pid):
        self.deletes.append((self.clock.mono, pid))
        self.deleted.add(pid)
        return "ACK_204"


@pytest.fixture(scope="module")
def production_reaper():
    path = Path(__file__).resolve().parents[1] / "runpod" / "aeth01_canary" / "independent_reaper.py"
    spec = importlib.util.spec_from_file_location("_cleanup_oracle_reaper_comparison", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("at", [1800, 3600])
@pytest.mark.parametrize("scenario", ["missing", "running", "terminated", "get_failure",
                                     "conflict", "list_failure"])
def test_actual_reaper_confirmations_are_permitted_by_independent_endpoint_trace(
        production_reaper, tmp_path, scenario, at):
    reaper = production_reaper
    manifest = {"version": 1, "run_id": "oracle-fixture", "run_name": "aeth01-age-oracle-fixture",
                "image": "registry.example/aeth01@sha256:" + "a" * 64,
                "creation_intent_id": "oracle-fixture",
                "cutoff_utc": datetime.fromtimestamp(EPOCH, timezone.utc).isoformat(),
                "cutoff_reference": "offline independent oracle", "reconciliation_horizon_seconds": 3600,
                "hourly_rate_usd": 6, "canary_budget_usd": 3}
    digest = hashlib.sha256((json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()).hexdigest()
    clock = Clock(EPOCH - 30)
    provider = TracedProvider(clock, manifest)
    state = reaper.new_evidence_state(manifest, digest)
    state = reaper.sweep(manifest, digest, provider, state, rounds=3, poll_seconds=10,
                         sleep=clock.sleep, clock_time=clock.time, monotonic=clock.monotonic)
    assert provider.deleted == set(IDS)
    assert set(state["owned_ids"]) == set(IDS)
    assert state["known_owned_cleanup_status"] == "KNOWN_OWNED_CLEANUP_CONFIRMED"
    # A new invocation: no oracle credit or trace is carried over from seeding.
    clock.utc, clock.mono = EPOCH, 0.0
    provider.rows.clear()
    provider.deletes.clear()
    provider.seed, provider.scenario, provider.at = False, scenario, at
    path = tmp_path / "state.json"
    write_durable_state(path, {"owned_ids": list(IDS), "last_provider_utc": EPOCH - 60})
    supplied = disk_hash(path)
    confirmed_checkpoints = []

    def permitted():
        return permits(provider.rows, now_utc=clock.time(), last_local_event=EPOCH - 60,
                       supplied_state_hash=supplied, current_state_hash=disk_hash(path))

    def checkpoint(snapshot):
        # Inspect ONLY the claimed status. Never use window, samples, counters,
        # pod confidence or policy replay to build the oracle's observations.
        if snapshot["status"] == "REAPER_CLEANUP_CONFIRMED":
            # The reaper catches callback exceptions: assert outside it, and
            # freeze each oracle verdict before later endpoint calls arrive.
            confirmed_checkpoints.append((clock.mono, permitted()))

    report = reaper.sweep(manifest, digest, provider, state, rounds=61, poll_seconds=60,
                          sleep=clock.sleep, clock_time=clock.time, monotonic=clock.monotonic,
                          persist=checkpoint)
    assert all(allowed for _, allowed in confirmed_checkpoints), confirmed_checkpoints
    assert len(provider.rows) == 61
    assert all(set(row["get_results"]) == set(IDS) for row in provider.rows)
    assert all(not row["list_owned_ids"] for row in provider.rows)
    assert set(report["owned_ids"]) == set(IDS)
    assert (report["status"] == "REAPER_CLEANUP_CONFIRMED") == permitted() == (scenario == "missing")
    assert bool(confirmed_checkpoints) == (scenario == "missing")
    if scenario == "running":
        assert (at, "one") in provider.deletes