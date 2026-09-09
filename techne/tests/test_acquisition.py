"""Tests for techne.acquisition. Concrete risks only.

The design says: *"Test only concrete risks: hash/permission/serialization contracts ...
Broad test counts and mirrored implementation tests are not acceptance evidence."*

So these test the four things that would actually let a bad artifact through, plus the two
contracts a consumer reads:

  1. a lock line without a --hash is REFUSED, not silently written
  2. the manifest cannot carry an entry with no named consumer
  3. a budget with network FORBIDDEN refuses an acquisition step
  4. the declarative export is pure JSON with no pickle and no binary payload
  5. every receipt names its stage and the stages it does NOT establish
  6. the reproduction manifest's expected values were committed before the result existed

They do NOT re-implement PyPI's digests, re-derive wheel tag matching, or assert that
a passing check passed.
"""
from __future__ import annotations

import json
import pathlib
import re

import pytest

from techne.acquisition import budget, manifest_io, paths, pypi, receipt

ACQ = paths.ACQ_ROOT


# ---------------------------------------------------------------- 1. hash contract
def test_unhashed_resolution_entry_is_refused_in_the_lock(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "locks", lambda: tmp_path)
    resolved = [
        {"name": "good", "version": "1.0", "sha256": "a" * 64},
        {"name": "bad", "version": "2.0", "sha256": None},
    ]
    lock = pypi.write_lock("t", "envx", resolved)
    text = lock.read_text(encoding="utf-8")
    assert "good==1.0 \\" in text
    assert "--hash=sha256:" + "a" * 64 in text
    # the unhashed one must appear as a REFUSAL comment, never as an installable line
    assert "# UNHASHED, REFUSED: bad==2.0" in text
    assert not re.search(r"^bad==2\.0", text, re.M)


def test_every_committed_lock_line_carries_a_hash():
    locks = sorted(ACQ.glob("locks/*.lock.txt"))
    assert locks, "no locks committed"
    for lock in locks:
        lines = [ln.rstrip() for ln in lock.read_text(encoding="utf-8").splitlines()]
        reqs = [i for i, ln in enumerate(lines)
                if ln and not ln.startswith("#") and "==" in ln]
        assert reqs, f"{lock.name} pins nothing"
        for i in reqs:
            assert lines[i].endswith("\\"), f"{lock.name}:{i+1} has no continuation"
            assert lines[i + 1].strip().startswith("--hash=sha256:"), \
                f"{lock.name}:{i+2} is not a sha256 hash line"
            assert len(lines[i + 1].strip().split(":")[1]) == 64


# ---------------------------------------------------------------- 2. manifest contract
def test_manifest_validates_and_every_entry_names_a_consumer():
    man = manifest_io.load()
    for e in man["entries"]:
        assert e["named_consumer"], e["id"]
        assert e["first_useful_check"], e["id"]


def test_entry_without_a_named_consumer_is_rejected(tmp_path):
    bad = {"entries": [{"id": "x", "kind": "python_package", "first_role": "r",
                        "integration_path": "p", "first_useful_check": "c",
                        "official_source": "s"}]}
    p = tmp_path / "m.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="named_consumer"):
        manifest_io.load(p)


def test_entries_with_no_consumer_are_marked_not_attempted():
    man = manifest_io.load()
    poet = manifest_io.entry(man, "poet")
    assert poet["acquisition_status"] == "NOT_ATTEMPTED_NO_CONSUMER"


# ---------------------------------------------------------------- 3. network contract
def test_offline_profile_refuses_an_acquisition_step():
    prof = budget.get_profile("offline_check")
    with budget.Budget(profile=prof) as b:
        with pytest.raises(budget.NetworkForbidden):
            b.require_network()


def test_acquisition_profiles_allow_network_and_reproduction_profile_does_not():
    assert budget.get_profile("light_probe")["network"].startswith("ALLOWED")
    assert budget.get_profile("isolated_heavy_build")["network"].startswith("ALLOWED")
    assert budget.get_profile("stitch_core_reproduction")["network"].startswith("FORBIDDEN")


def test_download_ceiling_aborts_rather_than_warning():
    prof = dict(budget.get_profile("offline_check"))
    prof["max_download_bytes"] = 10
    with budget.Budget(profile=prof) as b:
        with pytest.raises(budget.BudgetExceeded) as exc:
            b.count_download(11)
    assert exc.value.dimension == "max_download_bytes"


# ---------------------------------------------------------------- 4. serialization contract
def test_declarative_export_is_pure_json_with_no_pickle():
    exports = sorted(ACQ.glob("exports/*.json"))
    assert exports, "no export committed"
    for p in exports:
        raw = p.read_bytes()
        # a pickle protocol-2+ stream starts \x80; any of these markers in an "export" means
        # an upstream object graph is crossing the boundary instead of declarative data
        assert b"\x80\x04" not in raw and b"\x80\x02" not in raw
        assert b"cpickle" not in raw.lower()
        assert b"__reduce__" not in raw
        doc = json.loads(raw.decode("utf-8"))
        assert doc["export_rule"].startswith("DECLARATIVE ONLY")
        for a in doc["abstractions"]:
            # the typed AST must be plain nested lists and strings, nothing else
            def plain(node):
                if isinstance(node, str):
                    return True
                return isinstance(node, list) and all(plain(c) for c in node)
            assert plain(a["body_ast"]), a["name"]


def test_export_does_not_claim_usefulness():
    for p in sorted(ACQ.glob("exports/*.json")):
        doc = json.loads(p.read_text(encoding="utf-8"))
        assert "NOT_QUALIFIED" in doc


# ---------------------------------------------------------------- 5. receipt contract
def test_receipt_stage_and_does_not_establish_are_disjoint_and_complete():
    rec = receipt.new("INSTALLATION", "x")
    assert rec["stage"] not in rec["does_not_establish"]
    assert set(rec["does_not_establish"]) | {rec["stage"]} == set(receipt.STAGES)


def test_every_committed_receipt_names_its_stage():
    recs = sorted(ACQ.glob("receipts/*.json"))
    assert recs, "no receipts committed"
    for p in recs:
        d = json.loads(p.read_text(encoding="utf-8"))
        assert d["stage"] in receipt.STAGES, p.name
        assert d["stage"] not in d["does_not_establish"], p.name
        assert "LOCAL_SCIENTIFIC_BENEFIT" in d["does_not_establish"], (
            f"{p.name} claims to establish local scientific benefit; nothing in this "
            f"package is entitled to")


def test_unknown_stage_is_rejected():
    with pytest.raises(ValueError):
        receipt.new("BENEFIT", "x")


# ---------------------------------------------------------------- 6. preregistration contract
def test_reproduction_manifest_declares_tolerances_and_provenance():
    man = json.loads((ACQ / "reproduction" / "stitch_nuts_bolts.manifest.json")
                     .read_text(encoding="utf-8"))
    assert man["status"] == "DECLARED_NOT_RUN", (
        "the committed manifest must stay in its pre-run state; the RESULT goes in a "
        "separate file so the expected values cannot have been edited to match")
    assert man["observed"] is None
    for m in man["metrics"]:
        assert "tolerated_deviation" in m and "tolerance_reason" in m
        assert m["expected_provenance"]


def test_second_hand_expected_values_are_labelled():
    man = json.loads((ACQ / "reproduction" / "stitch_nuts_bolts.manifest.json")
                     .read_text(encoding="utf-8"))
    design_only = [m for m in man["metrics"]
                   if m["expected_provenance"].startswith("S-DESIGN only")]
    assert design_only, "expected at least one metric whose only source is the design packet"
    for m in design_only:
        # the grade may carry a trailing explanation; the prefix is the machine-readable part
        assert str(m.get("verdict_grade", "")).startswith("SECOND_HAND_EXPECTED_VALUE")


def test_host_capacity_was_measured_before_budgets_were_set():
    host = json.loads((ACQ / "HOST_CAPACITY.json").read_text(encoding="utf-8"))
    prof = json.loads((ACQ / "BUDGET_PROFILES.json").read_text(encoding="utf-8"))
    avail = host["ram_bytes"]["available"]
    assert avail, "available RAM was not measured"
    # the point of the measurement: no ceiling may exceed what the host actually has free
    for name, p in prof["profiles"].items():
        assert p["max_rss_bytes"] <= avail, f"{name} ceiling exceeds measured available RAM"


def test_live_interpreter_versions_are_recorded_as_unqualified():
    host = json.loads((ACQ / "HOST_CAPACITY.json").read_text(encoding="utf-8"))
    for name, info in host["live_interpreter"]["named_packages"].items():
        assert info["qualified"] is False, (
            f"{name} in the live interpreter must never be marked qualified: pip retains no "
            f"digest for it, so there is no hash evidence for what is installed")
