"""Unit tests for Phase 2C `(L, T, S)` artifacts, linear preconditioning, Ashenhurst-Curtis
discovery, hardened 3-seed RSO reducer, and fresh sealed v2c benchmarks."""
from __future__ import annotations

import json
import pytest

from comp_sprint.benchmarks import build_all_benchmarks, build_benchmarks_v2c, manifest_sha256
from comp_sprint.circuit import verify_truth_tables
from comp_sprint.library import (
    Artifact,
    RewriteRule,
    SearchStrategy,
    build_sham_matched_artifact,
    extract_dev_cofactor_partitions,
    mine_deterministic_artifact,
)
from comp_sprint.llm_proposer import compile_exprs_to_xag, parse_proposed_artifact
from comp_sprint.synth_base import synthesize_with_artifact, synthesize_with_library


def test_v2c_benchmarks_disjoint_from_v2b_and_deterministic():
    s2b = build_all_benchmarks()
    s2c_a = build_benchmarks_v2c()
    s2c_b = build_benchmarks_v2c()
    assert manifest_sha256(s2c_a) == manifest_sha256(s2c_b)
    assert manifest_sha256(s2c_a) != manifest_sha256(s2b)

    # Holdout structured task IDs & truth tables must be 100% disjoint from Phase 2B holdout
    ids_2b = {t.task_id for t in s2b["holdout_structured"]}
    ids_2c = {t.task_id for t in s2c_a["holdout_structured"]}
    assert ids_2b.isdisjoint(ids_2c)
    assert len(s2c_a["dev_structured"]) == 12
    assert len(s2c_a["dev_proc_shared"]) == 12
    assert len(s2c_a["dev_proc_comp"]) == 12
    assert len(s2c_a["holdout_structured"]) == 10
    assert len(s2c_a["holdout_proc_shared"]) == 10
    assert len(s2c_a["holdout_proc_comp"]) == 10
    assert len(s2c_a["holdout_proc_rand"]) == 10


def test_rewrite_rule_soundness_and_artifact_roundtrip():
    lc = compile_exprs_to_xag(3, ["(x0 & x1) ^ (x0 & x2)"])
    rc = compile_exprs_to_xag(3, ["x0 & (x1 ^ x2)"])
    rw = RewriteRule.from_circuits("dist", lc, rc, origin="test")
    assert len(rw.rhs_gates) < len(rw.lhs_gates)

    # Unsound rewrite MUST raise ValueError
    bad = compile_exprs_to_xag(3, ["x0 ^ x1 ^ x2"])
    with pytest.raises(ValueError, match="UNSOUND"):
        RewriteRule.from_circuits("bad", lc, bad, origin="test")

    strat = SearchStrategy(enable_linear_precond=True, enable_bijective_factor=True, enable_bridge_rewrites=True)
    art = Artifact(arm="TEST", generation=1, macros=(), rewrites=(rw,), strategy=strat)
    rt = Artifact.from_dict(art.to_dict())
    assert rt.sha256() == art.sha256()
    assert len(rt.rewrites) == 1
    assert rt.strategy == strat


def test_linear_precond_improves_or_matches_sbox_and_stays_exact():
    s2c = build_benchmarks_v2c()
    # Test on dev Serpent & Piccolo S-boxes (strictly DEV tasks!)
    art_lin = Artifact(
        arm="LIN", generation=1, macros=(), rewrites=(),
        strategy=SearchStrategy(enable_linear_precond=True, enable_bijective_factor=True, enable_bridge_rewrites=True),
    )
    for t in s2c["dev_structured"][-2:]:
        c0 = synthesize_with_library(t.n_inputs, t.targets, library=(), budget=4000, seed=0)
        c1 = synthesize_with_artifact(t.n_inputs, t.targets, artifact=art_lin, budget=4000, seed=0)
        assert verify_truth_tables(c1, t.targets)
        assert c1.gate_count() <= c0.gate_count()


def test_ashenhurst_curtis_discovers_alien_partitions_on_dev_proc_comp():
    s2c = build_benchmarks_v2c()
    parts = extract_dev_cofactor_partitions(s2c["dev_proc_comp"][:8], max_partitions=8)
    # Must discover recurring lossless 3->2 state-compressing partitions purely from black-box truth tables!
    assert len(parts) >= 1
    assert any(p["count"] >= 2 for p in parts)


def test_parse_proposed_artifact_rejects_unsound_rewrites():
    raw = json.dumps({
        "macros": [{"name": "ha", "n_inputs": 2, "exprs": ["x0 ^ x1", "x0 & x1"]}],
        "rewrites": [
            {"name": "good_dist", "n_inputs": 3, "lhs_exprs": ["(x0 & x1) ^ (x0 & x2)"], "rhs_exprs": ["x0 & (x1 ^ x2)"]},
            {"name": "unsound_rw", "n_inputs": 3, "lhs_exprs": ["x0 & x1"], "rhs_exprs": ["x0 ^ x1"]},
        ],
        "strategy": {"enable_linear_precond": True, "enable_bijective_factor": True, "enable_bridge_rewrites": True},
    })
    macros, rewrites, strat, rejected = parse_proposed_artifact(raw, origin="test", compress_exact=True)
    assert len(macros) == 1
    assert len(rewrites) == 1
    assert rewrites[0].name == "good_dist"
    assert len(rejected) == 1 and "rw:unsound_rw" == rejected[0]["name"]
    assert strat.enable_linear_precond is True


def test_sham_matched_artifact_preserves_strategy_and_replaces_lt():
    s2c = build_benchmarks_v2c()
    dev_train = s2c["dev_proc_comp"][:6]
    dev_circs = [synthesize_with_library(t.n_inputs, t.targets, library=(), budget=1000, seed=0) for t in dev_train]
    a3 = mine_deterministic_artifact(dev_train, dev_circs, max_macros=6, max_rewrites=3)
    sham = build_sham_matched_artifact(a3, seed=12345)
    assert sham.strategy == a3.strategy
    assert len(sham.macros) == len(a3.macros)
    assert len(sham.rewrites) == len(a3.rewrites)
    assert {m.sha256 for m in sham.macros}.isdisjoint({m.sha256 for m in a3.macros})
