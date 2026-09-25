import json
import numpy as np
import pytest

from ensorain.wtp.genome import random_genome, mutate, recombine, ghash, canonical, SPECIAL
from ensorain.wtp.world import run_world, build_field
from ensorain.wtp.organism import make_memory, KINDS
from ensorain.wtp.registry import REG, registry_table
from ensorain.wtp.detect import flags, class_refs, population_refs


def _legal(seed0=0):
    rng = np.random.default_rng(seed0)
    for i in range(200):
        g = random_genome(rng)
        r = run_world(g, 7 + i)
        if r["status"] == "OK":
            return g, r
    raise AssertionError("no legal world in 200 draws")


def test_genome_serialisable_hashable_mutable():
    rng = np.random.default_rng(1)
    g = random_genome(rng)
    assert json.loads(canonical(g))["memory"] == g["memory"]
    h = ghash(g)
    assert h == ghash(json.loads(canonical(g)))
    m = mutate(g, rng)
    assert m["meta"]["parents"] == [h]
    assert ghash(recombine(g, m, rng)) is not None
    for t in SPECIAL:
        random_genome(rng, bias=t)


def test_replay_is_deterministic():
    g, r = _legal(2)
    r2 = run_world(g, 7 + 0) if False else None
    seed = None
    rng = np.random.default_rng(2)
    for i in range(200):
        gg = random_genome(rng)
        a = run_world(gg, 7 + i)
        if a["status"] == "OK":
            b = run_world(gg, 7 + i)
            assert all(a[k] == b[k] for k in ("init_digest", "event_digest", "final_digest"))
            return
    pytest.fail("no legal world")


def test_memory_budgets_are_strict():
    rng = np.random.default_rng(3)
    for kind in KINDS:
        for cap in (16, 64, 300):
            try:
                m = make_memory(kind, [4, 5, 6], cap, rng)
            except ValueError:
                continue
            if kind not in ("none", "marks"):
                assert m.n_floats() <= cap, (kind, cap, m.n_floats())


def test_shuffle_latents_preserves_histogram():
    g, _ = _legal(4)
    a = run_world(g, 11)
    b = run_world(g, 11, shuffle_latents=True)
    assert a["status"] == b["status"] == "OK"
    assert a["init_digest"] != b["init_digest"]


def test_illegal_worlds_die_cleanly():
    g = random_genome(np.random.default_rng(5))
    g["memory"]["substrate"], g["memory"]["cap"] = "lowrank", 2
    r = run_world(g, 1)
    assert r["status"] == "ILLEGAL"


def test_registry_has_metadata_and_families():
    t = registry_table()
    fams = {r["family"] for r in t}
    assert {"TENSOR", "TN", "LINALG", "SPECTRAL", "STOCH", "SPARSE", "ELEMENT", "MEMORY"} <= fams
    for r in t:
        if r["family"] != "MEMORY":
            assert "invertible" in r and "flops_8x8x8" in r


def test_detectors_run():
    rows = []
    rng = np.random.default_rng(6)
    for i in range(60):
        g = random_genome(rng)
        r = run_world(g, 100 + i)
        if r["status"] == "OK":
            rows.append(dict(r, genome=g))
    cref, pref = class_refs(rows), population_refs(rows)
    for r in rows:
        flags(r, cref, pref)
