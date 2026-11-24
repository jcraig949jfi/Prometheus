"""Tests for shared synthesizer, deterministic miner (A3), and SHAM-MATCHED (A5)."""
from comp_sprint.benchmarks import build_all_benchmarks
from comp_sprint.library import (
    Artifact,
    build_sham_matched_library,
    mine_deterministic_library,
)
from comp_sprint.meter import WorkMeter
from comp_sprint.synth_base import synthesize_with_library


def test_synth_and_deterministic_miner_and_sham_roundtrip():
    suites = build_all_benchmarks()
    dev = suites["dev_structured"][:4]
    meter = WorkMeter()

    dev_circs = [
        synthesize_with_library(t.n_inputs, t.targets, library=(), budget=1500, seed=0, meter=meter, phase="dev")
        for t in dev
    ]
    assert all(c.gate_count() > 0 for c in dev_circs)

    art = mine_deterministic_library(dev_circs, max_macros=6, generation=1)
    assert len(art.macros) > 0
    # Strict serialization + SHA + truth-table re-verification roundtrip
    reloaded = Artifact.from_dict(art.to_dict())
    assert reloaded.sha256() == art.sha256()

    sham = build_sham_matched_library(art, seed=12345)
    assert len(sham.macros) == len(art.macros)
    # Run synthesizer with mined library and sham library on a target -> both verify exact
    t0 = suites["holdout_structured"][0]
    c_lib = synthesize_with_library(t0.n_inputs, t0.targets, library=art.macros, budget=1500, seed=0)
    c_sham = synthesize_with_library(t0.n_inputs, t0.targets, library=sham.macros, budget=1500, seed=0)
    assert c_lib.truth_tables() == t0.targets
    assert c_sham.truth_tables() == t0.targets
