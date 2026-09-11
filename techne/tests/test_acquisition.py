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


_DESERIALIZERS = re.compile(
    r"\b(pickle\.loads?|cPickle|torch\.load|joblib\.load|dill\.loads?|marshal\.loads?"
    r"|yaml\.load\s*\()")


def test_engine_deserializes_no_upstream_object_graph():
    """'Never deserialize upstream pickles in the engine' -- enforced, not stated.

    The acquired DreamCoder copy ships a pickle (tests/resources/kellis_list_exp.pickle).
    A pickle is arbitrary code at load time, so the guard is that the engine contains no
    deserialization call at all and no reference to the tool cache. If the engine later
    gains a legitimate need for one, this test should fail and force the decision to be
    made deliberately rather than arrive as a diff nobody read.
    """
    engine = paths.REPO_ROOT / "SerendipityFoundry" / "SerendipityFoundryEngine"
    if not engine.exists():
        pytest.skip("SFE engine not present in this checkout")
    offenders, cache_refs = [], []
    for p in list((engine / "sfe").rglob("*.py")) + list(engine.glob("*.py")):
        text = p.read_text(encoding="utf-8", errors="replace")
        rel = str(p.relative_to(paths.REPO_ROOT)).replace("\\", "/")
        for m in _DESERIALIZERS.finditer(text):
            offenders.append(f"{rel}: {m.group(0)}")
        for needle in ("techne_tools", "TECHNE_TOOL_CACHE"):
            if needle in text:
                cache_refs.append(f"{rel}: {needle}")
    assert not offenders, (
        "the engine deserializes an object graph: " + "; ".join(offenders))
    assert not cache_refs, (
        "the engine reaches into the tool cache, which holds unvetted upstream bytes: "
        + "; ".join(cache_refs))


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


# ---------------------------------------------------------------- packet reconciliation
# The reconciler has never seen the operator's real files, so what is tested is the part that
# must hold whatever their schema is: the operator's pin wins on disagreement, a proposal above
# measured host capacity does NOT get adopted, and nothing is amended as a side effect.
def _synthetic_plan(agree_sha: str) -> dict:
    return {
        "_WARNING": "SYNTHETIC TEST FIXTURE, not the operator's packet",
        "tools": [
            {"name": "z3", "official_repository": "https://github.com/Z3Prover/z3",
             "observed_source_head": agree_sha},
            {"name": "pyribs", "official_repository": "https://github.com/icaros-usc/pyribs",
             "observed_source_head": "0" * 40},
            {"name": "egg", "official_repository": "https://github.com/egraphs-good/egg",
             "observed_source_head": "1" * 40},
        ],
        "resource_profiles": {
            "isolated_heavy_build": {"max_wall_seconds": 7200, "max_memory_gib": 4096,
                                     "max_cpu_cores": 9999},
        },
    }


def test_reconciler_agrees_disagrees_and_finds_both_one_sided_cases():
    from techne.scripts import reconcile_packet as R
    man = manifest_io.load()
    z3 = manifest_io.entry(man, "z3")["upstream_revision"]["commit"]
    out = R.reconcile_sources(_synthetic_plan(z3), man)
    by = {r["repository"]: r["verdict"] for r in out["rows"]}
    assert by["github.com/z3prover/z3"] == "AGREE"
    assert by["github.com/icaros-usc/pyribs"] == "DISAGREE_OPERATOR_PIN_WINS"
    assert by["github.com/egraphs-good/egg"] == "PRESENT_ONLY_IN_PACKET"
    assert by["github.com/ellisk42/ec"] == "PRESENT_ONLY_IN_MINE"
    assert out["n_agree"] == 1 and out["n_disagree"] == 1
    assert "HEURISTIC" in out["heuristic_warning"]


def test_reconciler_refuses_a_ceiling_above_measured_available_capacity():
    from techne.scripts import reconcile_packet as R
    rep = R.reconcile_budgets(_synthetic_plan("a" * 40))
    flags = rep["conflicts_with_measured_host"]
    dims = {f["dimension"] for f in flags}
    assert dims == {"memory", "cpu"}, f"expected both dimensions flagged, got {dims}"
    for f in flags:
        assert f["resolution"].startswith("MEASUREMENT STANDS")
    assert rep["host_measured"]["ram_available_bytes"]


def test_reconciler_does_not_amend_the_manifest_or_the_budgets():
    from techne.scripts import reconcile_packet as R
    before = [(ACQ / n).read_bytes() for n in ("MANIFEST.json", "BUDGET_PROFILES.json")]
    R.reconcile_sources(_synthetic_plan("b" * 40), manifest_io.load())
    R.reconcile_budgets(_synthetic_plan("b" * 40))
    after = [(ACQ / n).read_bytes() for n in ("MANIFEST.json", "BUDGET_PROFILES.json")]
    assert before == after, (
        "the reconciler must report, never amend; an amendment is its own commit with its own "
        "reasoning, and a tool that rewrites the manifest as a side effect destroys the "
        "deviation history it exists to preserve")


def test_unit_is_not_guessed_for_an_undeclared_memory_number():
    from techne.scripts import reconcile_packet as R
    # 4096 read as GiB exceeds any plausible host; read as bytes it does not. The reconciler
    # must name WHICH readings exceed rather than picking one.
    rep = R.reconcile_budgets(_synthetic_plan("c" * 40))
    mem = [f for f in rep["conflicts_with_measured_host"] if f["dimension"] == "memory"][0]
    assert "GiB" in mem["exceeds_available_under_readings"]
    assert "bytes" not in mem["exceeds_available_under_readings"]


# --------------------------------------------------------------------------
# TECHNE-14: the component-library export. Three concrete risks, no mirroring.
# --------------------------------------------------------------------------
def test_export_refuses_to_parse_an_expression_it_was_not_given_an_ast_for():
    """A stitch body that is not a whole solved program has no published AST.
    The exporter must REFUSE it, because the alternative is a second parser
    that agrees with Proteus's grammar until it does not."""
    from techne.scripts import export_component_library as X

    res = {"ok": True, "n_abstractions": 1, "original_cost": 9, "final_cost": 8,
           "names": ["fn_0"], "arities": [1], "uses": [2], "bodies": ["(xor x1 x2)"]}
    out = X._score(res, "SYNTHETIC", ["(not (xor x1 x2))"], by_sexpr={}, held_out=set(),
                   ar=_StubArchaeon(), pb=None, va=_StubViv())
    assert out["refused_components"], "a body with no published AST must be refused"
    assert not out["components"]
    assert "will not parse an expression itself" in out["refused_components"][0]["refused"]


def test_a_component_that_is_a_held_out_solution_marks_the_corpus_unexportable():
    """The leak that matters: a component which IS a held-out target's solution
    turns that target into a size-1 leaf, so the library measures the leak."""
    from techne.scripts import export_component_library as X

    body = "(or x2 x1)"
    res = {"ok": True, "n_abstractions": 1, "original_cost": 9, "final_cost": 8,
           "names": ["fn_0"], "arities": [0], "uses": [6], "bodies": [body]}
    by = {body: {"ast": ["or", ["input", 2], ["input", 1]], "tasks": ["tgt-10"], "phases": {2}}}
    out = X._score(res, "ALL", [body], by, held_out={body},
                   ar=_StubArchaeon(), pb=_StubProteus(), va=_StubViv())
    assert out["n_components_from_held_out_phase2"] == 1
    assert out["exportable_for_phase2_use"] is False
    assert "size-1 LEAF" in out["why_not_exportable"]


def test_the_exported_artifact_is_json_with_no_pickle():
    """Deliverable 5 of the acquisition brief, at the one place bytes actually
    leave this seat for a consumer."""
    from techne.scripts import export_component_library as X

    body = "(and x0 x2)"
    res = {"ok": True, "n_abstractions": 1, "original_cost": 9, "final_cost": 8,
           "names": ["fn_0"], "arities": [0], "uses": [2], "bodies": [body]}
    by = {body: {"ast": ["and", ["input", 0], ["input", 2]], "tasks": ["src-17"], "phases": {1}}}
    out = X._score(res, "P1", [body], by, held_out=set(),
                   ar=_StubArchaeon(), pb=_StubProteus(), va=_StubViv())
    raw = out["artifact"]["canonical_json"].encode("utf-8")
    assert out["no_pickle"]["codec"] == "canonical-json-v1"
    assert json.loads(raw)["interface_id"] == "boolean-components-v1"
    # pickle protocol 2+ opens with \x80; a JSON document never does.
    assert not raw.startswith(b"\x80")
    assert b"__reduce__" not in raw and b"cPickle" not in raw


class _StubArchaeon:
    """Only the envelope call is stubbed, and it is stubbed to the SHAPE the
    real library_object returns -- the real one is exercised by the run itself."""

    @staticmethod
    def library_object(components, *, provenance):
        obj = {"artifact_type": "component_library", "schema_version": "1",
               "interface_id": "boolean-components-v1", "components": [dict(c) for c in components]}
        raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return {"object": obj, "raw": raw, "provenance": provenance,
                "slot": {"digest": "sha256:stub", "expected_bytes": len(raw)}}


class _StubProteus:
    @staticmethod
    def truth_table(expr):
        return [0] * 8


class _StubViv:
    @staticmethod
    def _check_boolean_components_v1(obj, limits):
        return {"component_count": len(obj["components"])}


# --------------------------------------------------------------------------
# TECHNE-44: cancellation. Two concrete risks, both found by the probe.
# --------------------------------------------------------------------------
def test_a_resource_receipt_does_not_keep_changing_after_it_is_taken():
    """The defect the cancellation probe surfaced: resource_receipt() handed out
    a reference to the live kill list, so a receipt taken inside the context kept
    growing during teardown and every reading of it disagreed with the last."""
    prof = {"name": "t", "network": "FORBIDDEN", "max_wall_seconds": 60,
            "max_processes": 4, "max_download_bytes": 0}
    b = budget.Budget(profile=prof)
    taken = b.resource_receipt()["cancellation"]
    before = json.dumps(taken, sort_keys=True)
    b._kills.append({"pid": 1, "mechanism": "job_object"})
    b._job_failures.append({"pid": 1, "reason": "synthetic"})
    assert json.dumps(taken, sort_keys=True) == before, (
        "a receipt is a record of a moment; one that mutates afterwards cannot be "
        "compared against anything, including itself")


def test_cancelling_the_same_child_twice_does_not_invent_a_degraded_kill():
    """__exit__ sweeps kill_tree() over every child, so a process the caller
    already cancelled arrives a second time when it is dead and its job is gone.
    Recording that as 'nothing could be reaped' would manufacture a degraded
    cancellation out of ordinary teardown."""
    prof = {"name": "t", "network": "FORBIDDEN", "max_wall_seconds": 60,
            "max_processes": 4, "max_download_bytes": 0}
    b = budget.Budget(profile=prof)

    class _Dead:
        pid = 4242

        @staticmethod
        def poll():
            return 0

    p = _Dead()
    b._kill_one(p)
    b._kill_one(p)
    b._kill_one(p)
    assert len(b._kills) == 1, "one cancellation is one row, however many times it is swept"


# --------------------------------------------------------------------------
# D-23 (operator, 2026-09-11): the workspace invariant, on this seat's entry points.
# --------------------------------------------------------------------------
def test_the_canonical_checkout_is_detected_without_a_path_assumption():
    """Archaeon's test, and the reason it is theirs rather than mine: a
    path-based check would have to know a drive letter, which is the exact
    portability defect this seat exists to catch in other people's code."""
    from techne import workspace
    # The tests themselves run from a linked worktree, so this is the real answer
    # for the tree under test, not a stub.
    assert workspace.is_main_worktree() is False
    r = workspace.receipt()
    assert r["base_sha"] and len(r["base_sha"]) == 40
    assert r["branch"] and r["worktree_path"]
    assert r["tool_cache_versioned"] is False, (
        "base_sha pins this seat's CODE and not its installed tools; a receipt "
        "implying otherwise would claim a reproducibility this seat does not have")


def test_a_budgeted_step_refuses_to_run_from_the_canonical_checkout():
    """Rule 1 and rule d: the refusal is on the ENTRY POINT, and every check in
    this seat runs inside a Budget -- including ones not yet written."""
    from techne import workspace
    real = workspace.is_main_worktree
    workspace.is_main_worktree = lambda path=None: True
    try:
        with pytest.raises(workspace.CanonicalCheckoutRefused) as exc:
            with budget.Budget(profile={"name": "t", "network": "FORBIDDEN"}):
                pass
        assert "canonical checkout" in str(exc.value)
    finally:
        workspace.is_main_worktree = real


def test_every_receipt_carries_the_four_fields_d23_requires():
    from techne.acquisition import receipt as R
    ws = R.new("INSTALLATION", "probe")["workspace"]
    for field_name in ("base_sha", "branch", "worktree_path", "dirty"):
        assert field_name in ws, field_name
