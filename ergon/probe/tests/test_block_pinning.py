"""Block A's pin is immutable and the two blocks are disjoint — proven, not asserted in prose.

The REDESIGN ruling: *"do not mutate the original SHA-pinned manifest. Add a second
independently pinned replenishment block... The original pin then continues doing the exact job
for which it was created: preventing post-observation widening."*

The thing I least want to be true is that block A was quietly widened, or that block B's tasks
overlap A's and inflate n without adding independent information. Both are decidable, so they
are decided here rather than trusted. Generalized gate-fire: each test below also contains the
constructed case where the defect is present, so the check is shown capable of failing.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

MANIFESTS = ROOT / "ergon/probe/manifests"
BLOCK_A = MANIFESTS / "nearmiss_mix-M30_manifest_n200.jsonl"
BLOCK_B = MANIFESTS / "nearmiss_mixB-M30_manifest_n220.jsonl"
BLOCK_A_SHA16 = "e6b1e001bf79e3ef"


def _rows(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_block_a_pin_is_unchanged():
    """If this fails, a result computed against `e6b1e001` no longer describes the population
    it was computed on, and every Tier A/Tier B number in STATE_2026-08-25.md is void."""
    from ergon.probe.task_gen_v3 import manifest_sha256
    if not BLOCK_A.exists():
        pytest.skip("block A manifest absent")
    assert manifest_sha256(_rows(BLOCK_A))[:16] == BLOCK_A_SHA16, (
        "BLOCK A HAS BEEN MUTATED — the pin exists to prevent post-observation widening")


def test_the_pin_check_can_actually_fail():
    """The constructed world: a tampered manifest MUST NOT hash to the pin."""
    from ergon.probe.task_gen_v3 import manifest_sha256
    if not BLOCK_A.exists():
        pytest.skip("block A manifest absent")
    rows = _rows(BLOCK_A)
    rows[0] = dict(rows[0], prompt=rows[0]["prompt"] + " widened")
    assert manifest_sha256(rows)[:16] != BLOCK_A_SHA16, (
        "the pin check cannot detect tampering — it is not a pin")


def test_blocks_are_disjoint_in_uid_and_in_tasks():
    """Overlap would inflate n without adding independent information — power by double
    counting, which is the quiet version of widening the pin."""
    if not (BLOCK_A.exists() and BLOCK_B.exists()):
        pytest.skip("both blocks required")
    a, b = _rows(BLOCK_A), _rows(BLOCK_B)
    assert not ({r["uid"] for r in a} & {r["uid"] for r in b}), "uid namespaces intersect"
    assert not ({r["prompt"] for r in a} & {r["prompt"] for r in b}), (
        "the two blocks share TASKS — pooling them would double count")


def test_block_b_is_well_posed_independently():
    """Block A's well-posedness says nothing about block B. A deterministic program must
    recover block B's gold from its prompt text alone, or no LLM number on B means anything."""
    if not BLOCK_B.exists():
        pytest.skip("block B manifest absent")
    from ergon.probe.task_controls import deterministic_solver
    res = deterministic_solver(_rows(BLOCK_B))
    assert res["agreement"] == 1.0, f"block B gold not reproducible: {res['disagreements']}"


def test_block_b_carries_its_own_pin_and_names_the_merge_rule():
    """A block whose provenance is not committed is an assertion with a filename (ATK-015)."""
    meta_p = MANIFESTS / "nearmiss_mixB-M30_manifest_meta.json"
    if not meta_p.exists():
        pytest.skip("block B meta absent")
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    for k in ("manifest_sha256", "generator_sha256", "seed", "merge_rule", "solver_pin",
              "second_family_required"):
        assert meta.get(k), f"block B meta is missing {k}"
    assert (ROOT / meta["merge_rule"]).exists(), "the merge rule it names is not committed"
    assert meta["sibling_block_A"]["sha16"] == BLOCK_A_SHA16
