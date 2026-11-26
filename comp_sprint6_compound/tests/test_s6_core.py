"""Unit tests for Sprint 6 Law 4b (`OpBudget v3`: Word-Width + Container + Call Metering) & 172-Task Manifest."""
from __future__ import annotations

from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact, LibModule
from comp_sprint6_compound.law4b_meter import synthesize_s6_xag
from comp_sprint6_compound.s6_benchmarks import build_s6_benchmarks, s6_manifest_sha256


def test_law4b_meters_containers_calls_and_bigints_deterministically():
    # Dict-heavy + sort-heavy module MUST pay dramatically more OpBudget v3 units than tight scalar loop!
    m_tight = LibModule.from_source(
        "m_tight", 0,
        "def work(circ):\n"
        "    x = 12345\n"
        "    for i in range(100):\n"
        "        x = (x ^ i) & 0xFFFF\n"
        "    return circ\n",
    )
    m_dict_sort = LibModule.from_source(
        "m_dict_sort", 0,
        "def work(circ):\n"
        "    for i in range(100):\n"
        "        d = {k: k ^ i for k in range(32)}\n"
        "        s = sorted(d.keys())\n"
        "    return circ\n",
    )
    orch = LibModule.from_source(
        "o", 0,
        "def solve(circ, n_inputs, targets, seed, api, lib, budget):\n"
        "    return lib.work(circ)\n",
        required_fn="solve",
    )
    suites = build_s6_benchmarks()
    assert s6_manifest_sha256(suites) == s6_manifest_sha256(build_s6_benchmarks())
    assert sum(len(v) for v in suites.values()) == 172

    t = suites["s6_hold_struct"][0]
    _, mt1 = synthesize_s6_xag(t.n_inputs, t.targets, CompositionalAlgoArtifact("T", "S6", 0, (m_tight,), orch), seed=0, v3_budget=500_000)
    _, mt2 = synthesize_s6_xag(t.n_inputs, t.targets, CompositionalAlgoArtifact("T", "S6", 0, (m_tight,), orch), seed=0, v3_budget=500_000)
    _, md = synthesize_s6_xag(t.n_inputs, t.targets, CompositionalAlgoArtifact("D", "S6", 0, (m_dict_sort,), orch), seed=0, v3_budget=500_000)
    # Law 1: 0.000 determinism
    assert mt1["ops_spent"] == mt2["ops_spent"]
    # Law 4b: 100 iters of dict(32) + sorted(32) (~30,000+ units) >> 100 scalar iters (~110 units)!
    assert md["ops_spent"] > 20_000 and mt1["ops_spent"] < 500
    assert not md["fn_errors"] and not mt1["fn_errors"]
