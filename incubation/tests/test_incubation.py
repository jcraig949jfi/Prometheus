"""Tests for the incubation substrate. Fast, deterministic, no network.

The observation-boundary test is the load-bearing one: solver/concepts modules must not
import world/diagnostics code or reference the planted composition.
"""
from __future__ import annotations

import ast
import os
import random
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from primitives import PRIM_IDS, make_inv_prims, make_prims, selfcheck   # noqa: E402
from worlds import M_WORD, make_worlds                                   # noqa: E402
import diagnostics as dx                                                 # noqa: E402
from solver import Action, Boundary, iddfs, bfs                          # noqa: E402
from concepts import Concept, Guard, mine, learn_guard                   # noqa: E402
from ledger.ledger import append_event, new_entry, set_status            # noqa: E402


# ── primitives ──────────────────────────────────────────────────────────────────────

def test_primitive_inverses_all_world_instantiations():
    assert selfcheck(6, 997) and selfcheck(7, 673) and selfcheck(8, 809)


def test_primitives_typed_and_total():
    prims = make_prims(5, 11)
    rng = random.Random(0)
    for _ in range(50):
        s = tuple(rng.randrange(11) for _ in range(5))
        for f in prims:
            t = f(s)
            assert isinstance(t, tuple) and len(t) == 5
            assert all(0 <= v < 11 for v in t)


def test_every_primitive_has_live_consumer():
    """Each primitive appears in generated witnesses (no dead primitives)."""
    w = make_worlds()["wA"]
    rng = random.Random(3)
    used = set()
    for _ in range(12):
        _, omni = w.gen_task(rng, embed_m=True)
        used |= set(omni["witness"])
    assert used == {0, 1, 2, 3}


# ── worlds & family filters ─────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def worlds():
    return make_worlds()


def test_solver_visible_schema(worlds):
    rng = random.Random(1)
    for w in worlds.values():
        task, omni = w.gen_task(rng, embed_m=True)
        assert set(task) == {"start", "target"}
        assert "witness" not in task and "wid" not in task


def test_embed_family_filter_forces_m(worlds):
    w = worlds["wA"]
    rng = random.Random(2)
    task, omni = w.gen_task(rng, embed_m=True)
    L = dx.min_dist(w, omni["s"], omni["t"])
    assert L == len(omni["witness"])
    sols = dx.solutions_at(w, omni["s"], omni["t"], L)
    assert sols and all(dx.contains_word(x, M_WORD) for x in sols)


def test_null_family_filter_excludes_m(worlds):
    w = worlds["wA"]
    rng = random.Random(2)
    task, omni = w.gen_task(rng, embed_m=False)
    L = dx.min_dist(w, omni["s"], omni["t"])
    sols = dx.solutions_at(w, omni["s"], omni["t"], L)
    assert sols and not any(dx.contains_word(x, M_WORD) for x in sols)


def test_wc_constraint_fails_moves_into_band(worlds):
    wc = worlds["wC"]
    s = (5, wc.trap_lo, 0, 0, 0, 0, 0, 0)          # slot1 at the boundary: valid
    assert wc.valid(s)
    bad = (5, wc.trap_lo - 1) + (0,) * 6
    assert not wc.valid(bad)


def test_surface_codecs_roundtrip(worlds):
    wb = worlds["wB"]
    rng = random.Random(4)
    s = wb._rand_state(rng)
    assert wb.decode(wb.encode(s)) == s
    assert isinstance(wb.encode(s), str)


# ── boundary ────────────────────────────────────────────────────────────────────────

def test_boundary_opacity_and_counting(worlds):
    w = worlds["wA"]
    rng = random.Random(5)
    task, omni = w.gen_task(rng, embed_m=True)
    b = Boundary(w, task)
    assert not any(type(v).__name__ == "World" for v in vars(b).values())
    s = b.start
    n0 = b.execs
    t = b.apply("r00", s)
    assert b.execs == n0 + 1 and t is not None
    end, fail = b.run_word([PRIM_IDS[i] for i in omni["witness"]], b.start)
    assert fail is None and b.is_goal(end)


def test_static_import_boundary():
    for mod in ("solver/boundary.py", "solver/engine.py", "concepts/concept.py",
                "concepts/mine.py", "concepts/guard.py"):
        tree = ast.parse(open(os.path.join(ROOT, mod)).read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods = [n.name.split(".")[0] for n in node.names]
            elif isinstance(node, ast.ImportFrom):
                mods = [(node.module or "").split(".")[0]]
            else:
                if isinstance(node, ast.Name):
                    assert node.id != "M_WORD", f"{mod} references M_WORD"
                continue
            assert not set(mods) & {"worlds", "diagnostics"}, f"{mod} imports {mods}"


# ── engine ──────────────────────────────────────────────────────────────────────────

class TinyBoundary:
    """3 symbols, prims: a=+1 mod 5 on slot0, b=swap. Target crafted by hand."""

    def __init__(self, start, target, forbid=None):
        self.prim_ids = ("pa", "pb")
        self._start, self._target = start, target
        self._forbid = forbid or (lambda s: False)
        self.execs = 0

    @property
    def start(self):
        return self._start

    def is_goal(self, s):
        return s == self._target

    def apply(self, pid, s):
        self.execs += 1
        t = ((s[0] + 1) % 5, s[1]) if pid == "pa" else (s[1], s[0])
        return None if self._forbid(t) else t

    def read(self, s):
        return tuple(s)

    def run_word(self, word, s):
        for i, pid in enumerate(word):
            s = self.apply(pid, s)
            if s is None:
                return None, i
        return s, None


def _acts():
    return [Action("pa", ("pa",)), Action("pb", ("pb",))]


def test_iddfs_finds_minimal_and_counts():
    b = TinyBoundary((0, 0), (2, 0))
    res = iddfs(b, _acts(), dmax=6)
    assert res["solved"] and res["sol"] == ("pa", "pa") and res["found_at"] == 2
    assert res["execs"] == b.execs and res["nodes"] >= 2


def test_reified_vs_flat_accounting():
    b1 = TinyBoundary((0, 0), (3, 0))
    macro = Action("cX", ("pa", "pa", "pa"), reified=True)
    r1 = iddfs(b1, _acts() + [macro], dmax=6)
    b2 = TinyBoundary((0, 0), (3, 0))
    flat = Action("fX", ("pa", "pa", "pa"), reified=False)
    r2 = iddfs(b2, _acts() + [flat], dmax=6)
    assert r1["solved"] and r2["solved"]
    # reified finds it at composition depth 1; flat cannot beat primitive depth 3
    assert r1["found_at"] == 1 and r2["found_at"] == 3


def test_runtime_failure_recorded_not_fatal():
    b = TinyBoundary((0, 1), (2, 1), forbid=lambda s: s == (1, 0))
    res = iddfs(b, _acts(), dmax=8)
    # pb from (0,1) enters forbidden (1,0); pa-pa solves; failures must be recorded
    assert res["solved"]
    assert res["failures"]["pb"] > 0


def test_bfs_equivalent_solution_length():
    b1 = TinyBoundary((0, 1), (4, 1))
    b2 = TinyBoundary((0, 1), (4, 1))
    r_id = iddfs(b1, _acts(), dmax=8)
    r_bf = bfs(b2, _acts(), dmax=8)
    assert r_id["solved"] and r_bf["solved"]
    assert len(r_bf["sol"]) == r_bf["found_at"] == r_id["found_at"]


def test_guard_blocks_action_and_counts_probe_execs():
    b = TinyBoundary((0, 0), (3, 0))
    guard = Guard([((), 0, "<", 99)])          # always true -> macro always skipped
    macro = Action("cX", ("pa", "pa", "pa"), reified=True, guard=guard)
    res = iddfs(b, _acts() + [macro], dmax=6)
    assert res["solved"] and res["found_at"] == 3        # solved by primitives
    assert res["guard_skips"] > 0
    assert res["uses"].get("cX", 0) == 0


# ── mining ──────────────────────────────────────────────────────────────────────────

def test_miner_finds_planted_ngram():
    eps = []
    for k in range(8):
        b = TinyBoundary((k % 5, 1), (0, 0))     # target unused by fingerprint probes
        sol = ("pb",) + ("pa", "pb", "pa") + ("pb",) * (k % 2)
        eps.append((b, sol))
    cand, report = mine(eps, min_support_frac=0.5)
    assert cand is not None
    assert report["n_episodes"] == 8
    # the planted trigram must be among the top-scoring groups
    tops = [tuple(r["word"]) for r in report["top10"]]
    assert ("pa", "pb", "pa") in tops


def test_miner_deterministic():
    eps = [(TinyBoundary((1, 2), (0, 0)), ("pa", "pb", "pa", "pa"))] * 5
    c1, _ = mine(eps)
    c2, _ = mine(eps)
    assert c1 == c2


# ── guard learning ──────────────────────────────────────────────────────────────────

def test_learn_guard_exact_on_synthetic():
    # failure iff slot0 < 3 (entering swap puts slot0 into slot1 ... emulate simply)
    word = ("pb", "pa")
    ok = [(x, y) for x in range(3, 5) for y in range(5)]
    fail = [((x, y), 0) for x in range(3) for y in range(5)]

    def apply_fn(pid, s):
        if pid == "pb" and s[0] < 3:
            return None
        return ((s[0] + 1) % 5, s[1]) if pid == "pa" else (s[1], s[0])

    g, info = learn_guard(word, ok, fail, apply_fn, ("pa", "pb"))
    assert g is not None

    class Shim:
        def apply(self, pid, s):
            return apply_fn(pid, s)

        def read(self, s):
            return tuple(s)

    for s, _ in fail:
        assert g(Shim(), s) is True
    for s in ok:
        assert g(Shim(), s) is False


# ── ledger ──────────────────────────────────────────────────────────────────────────

def test_ledger_entry_schema_and_append_only():
    e = new_entry("c9999", {"word": ["r01"]}, ["r01"], {"phase": "test"})
    assert e["status"] == "candidate"
    n0 = len(e["events"])
    set_status(e, "admitted", "test")
    append_event(e, "note", detail="x")
    assert e["status"] == "admitted" and len(e["events"]) == n0 + 2
    with pytest.raises(AssertionError):
        set_status(e, "nonsense", "bad")


# ── concept identity hygiene ────────────────────────────────────────────────────────

def test_concept_serialization_clean():
    import json as _json
    c = Concept("c0001", ("r01", "r02", "r01"),
                Guard([((), 0, "<", 161)]))
    js = _json.dumps(c.to_json())
    for tok in ("wA", "wB", "wC", "embed", "hostile", "friendly", "witness"):
        assert tok not in js
