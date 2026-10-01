"""(7) Intervention provenance. Core only (no PTE import); git is used read-only and C1 rows are read as data."""
from __future__ import annotations

import gzip
import json
import pathlib
import subprocess

import pytest

from prometheus.explib.outcomes import FAIL, NOT_VERIFIED, PASS
from prometheus.explib.provenance import (Ledger, hook_digest, make_record, plan_precedes, seed_reuse, support_check,
                               verify_record)

from prometheus.explib.tests._paths import REPO  # noqa: E402
ROWS = REPO / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"


def factory(sub):
    return lambda w: ("swap", sub, w)


def flush(w):
    return w


def test_hook_digest_sees_code_and_captured_values():
    a, b, a2 = factory(0), factory(1), factory(0)
    assert hook_digest(a)["digest"] == hook_digest(a2)["digest"]
    assert hook_digest(a)["digest"] != hook_digest(b)["digest"]            # captured target differs
    assert hook_digest(flush)["digest"] != hook_digest(flush, {"tick": 5})["digest"]
    assert hook_digest(flush)["basis"] == "source"


def test_record_ids_ledger_tamper_and_duplicate(tmp_path):
    rec = make_record(experiment="T-X", arm="S", kind="intervention", seed_namespace=0x680, seeds=[1, 2, 3],
                      hook=flush, params={"tick": 5}, plan_path="p.md", plan_commit="017259a48", now="2026-10-01T00:00:00+00:00")
    v = verify_record(rec, stored_id=rec.record_id, hook=flush)
    by = {c["name"]: c["outcome"] for c in v["checks"]}
    assert by["R1_id"] == PASS and by["R2_hook_digest"] == PASS
    # MUST-FAIL: a different live hook (code changed after the record) is caught
    assert {c["name"]: c["outcome"] for c in verify_record(rec, hook=factory(0))["checks"]}["R2_hook_digest"] == FAIL
    L = Ledger(tmp_path / "ledger.jsonl")
    L.append(rec)
    with pytest.raises(ValueError):
        L.append(rec)                                                        # append-only
    assert L.verify().outcome == PASS
    txt = (tmp_path / "ledger.jsonl").read_text().replace('"arm":"S"', '"arm":"site_all"')
    (tmp_path / "ledger.jsonl").write_text(txt)
    assert L.verify().outcome == FAIL                                        # tamper detected


def test_seed_reuse_between_arms_declared_independent():
    mk = lambda arm, ns: make_record(experiment="T", arm=arm, kind="intervention", seed_namespace=ns, seeds=[ns],
                                     hook=flush, now="x")
    recs = [mk("normal", 0x600), mk("swap", 0x600), mk("replicate", 0x680)]
    assert seed_reuse(recs, [["normal", "replicate"]]).outcome == PASS
    bad = seed_reuse(recs, [["swap", "replicate", "normal"]])
    assert bad.outcome == FAIL and ("swap", "normal") in [tuple(sorted(c, reverse=True)) for c in bad.detail["clashes"]] \
        or bad.detail["clashes"]


@pytest.mark.skipif(not ROWS.exists(), reason="C1 rows not present")
def test_transfer_cell_is_not_a_search_null():
    """HISTORICAL (H-PLANT principal review, MULTIHOP QUALIFIED): fac4aaa23 (kind 'transfer': the RELAY d3
    champion re-evaluated at d5, no search ran) was read as 'C1 search failed multi-hop at d9cc'."""
    rows = {}
    with gzip.open(ROWS, "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["cell_id"].startswith("fac4aaa2") or (r["kind"] == "evolve" and len(rows) < 3):
                rows[r["cell_id"]] = {"cell_id": r["cell_id"], "kind": r["kind"]}
    cited = [v for k, v in rows.items() if k.startswith("fac4aaa2")]
    assert cited and cited[0]["kind"] == "transfer"
    c = support_check("search_null", cited)
    assert c.outcome == FAIL and c.detail["refused"][0]["kind"] == "transfer"
    evolve = [v for v in rows.values() if v["kind"] == "evolve"]
    assert support_check("search_null", evolve).outcome == PASS              # NEGATIVE control
    assert support_check("transfer_null", cited).outcome == PASS
    assert support_check("no_such_claim", cited).outcome == NOT_VERIFIED


def _git_ok():
    try:
        return subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True).returncode == 0
    except FileNotFoundError:
        return False


@pytest.mark.skipif(not _git_ok(), reason="git not available")
def test_plan_freeze_known_answers_REL4_pass_WO_fail():
    """HISTORICAL (BX-1 / Harmonia G1): REL4's plan (017259a48) predates W-W's results -> PASS; W-O's PLAN.md
    was first committed together with its REPORT (93e2e544b) -> FAIL. Read-only git."""
    ok = plan_precedes(str(REPO), "roles/Ananke/research/plans/T-SWAP-REL4_PLAN.md", ["roles/Ananke/research/workers/W-W/"])
    bad = plan_precedes(str(REPO), "roles/Ananke/research/workers/W-O/PLAN.md", ["roles/Ananke/research/workers/W-O/REPORT.md"])
    assert ok.outcome == PASS and ok.detail["plan_add"] == "017259a48"
    assert bad.outcome == FAIL and bad.detail["plan_add"] == bad.detail["result_add"] == "93e2e544b"
    rec = make_record(experiment="REL4", arm="all", kind="intervention", seed_namespace=1, seeds=[1], hook=flush,
                      plan_path="roles/Ananke/research/plans/T-SWAP-REL4_PLAN.md", plan_commit="017259a48", now="x")
    v = verify_record(rec, repo=str(REPO), result_pathspecs=["roles/Ananke/research/workers/W-W/"])
    by = {c["name"]: c["outcome"] for c in v["checks"]}
    assert by["R3_plan_precedes"] == PASS and by["R4_plan_commit_link"] == PASS


TARGET = 3


def reads_global(w):
    return w + TARGET


def test_hook_digest_includes_simple_globals():
    global TARGET
    d0 = hook_digest(reads_global)["digest"]
    TARGET = 4
    try:
        assert hook_digest(reads_global)["digest"] != d0
    finally:
        TARGET = 3
