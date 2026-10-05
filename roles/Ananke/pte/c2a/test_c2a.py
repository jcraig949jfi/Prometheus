"""PTE-C2A known-answer tests (CPU). Run: python -m pytest roles/Ananke/pte/c2a/test_c2a.py -q -p no:cacheprovider"""
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402
import pytest  # noqa: E402

import c2a_common as C  # noqa: E402
from prometheus.ananke import assays, envs, search  # noqa: E402


@pytest.fixture(scope="module")
def admit():
    import admit as A          # hides CUDA; CPU only
    return A


def _cell(admit, fam, i):
    c = admit.census.candidate(fam, i)
    return C.Physics.from_dict(c["physics"]).validate(), envs.EnvSpec(**c["env"])


def test_pairs_of_equals_env_score(admit):
    ph, env = _cell(admit, "FLIP", 0)
    seeds = assays.world_seeds(C.H_int(C.C2A_NS, 0x7E57, 1), 8)
    g = C.p_flip(ph)
    pt, ep = C.eval_programs(ph, env, seeds, [g], device="cpu")
    r = assays.evaluate(ph, g[None], env, seeds, device="cpu")
    assert np.allclose(C.pairs_of(pt[0], ep.scored), r.pair_acc()[0])


def test_attainability_golden_unreachable_not_admitted(admit):
    # RELAY candidate 0: joint ceiling .5 (no route within delta) -> P-CAPPED, never searched, never admitted
    r = admit.admit_one("RELAY", 0)
    assert r["ceiling"] <= 0.5 + 1e-9 and r["verdict"] in ("P-CAPPED", "OUT_OF_STRATUM")
    assert "plants" not in r


def test_attainability_golden_planted_positive_admitted(admit):
    # FLIP candidate 0: ceiling 1.0 and P-FLIP passes B on 128 fresh worlds; every in-scope adversary FALSE
    r = admit.admit_one("FLIP", 0)
    assert r["verdict"] == "ADMITTED" and r["plant_of_record"] == "P_FLIP"
    assert r["plants"]["P_FLIP"]["ruler"]["status"] == "TRUE"
    assert r["plants"]["P_FLIP"]["ablate"]["status"] != "TRUE"            # teacher_off must fail
    assert all(v["status"] == "FALSE" for k, v in r["adversaries"].items() if r["V_scope"][k])


def test_ruler_must_fail_null_and_latch(admit):
    ph, env = _cell(admit, "RELAY", 10)             # a >=2-hop RELAY cell
    seeds = C.admit_seeds("RELAY", 10)
    pt, ep = C.eval_programs(ph, env, seeds, [C.null(ph), C.onehop(ph)], device="cpu")
    for k in range(2):
        assert C.competence("RELAY-mh", pt[k], ep)["status"] == "FALSE"


def test_kseed_changes_exactly_k_fields():
    import run as R
    ph = C.Physics.from_dict(dict(C.Physics().to_dict(), prog_len=16, rules=1, state_dim=2)).validate()
    plant = C.PLANTS["FLIP"]["P_FLIP"](ph)          # canonical (inside the GA's support)
    for k in (1, 2, 4):
        g, edits = R.kseed_genome(plant, k, 12345, 0)
        assert int((g != plant).sum()) == k and len(edits) == k
        assert ((g[..., :4] >= 0) & (g[..., :4] <= 255)).all() and ((g[..., 4] >= -128) & (g[..., 4] <= 127)).all()
        g2, _ = R.kseed_genome(plant, k, 12345, 0)
        assert np.array_equal(g, g2)                  # deterministic per (cell, k, idx)


def test_canonical_plants_in_ga_support_and_equivalent_at_kp0(admit):
    """REPAIR R1 known answer: the raw P-FLIP carries imm 128 (outside the GA support); the canonical one does
    not, and at a cell without site mutation (FLIP-0000, mut_site 0) it behaves identically per trial."""
    ph, env = _cell(admit, "FLIP", 0)
    assert ph.mut_site == 0
    raw, can = C.p_flip(ph), C.PLANTS["FLIP"]["P_FLIP"](ph)
    assert (raw[..., 4] > 127).any() and not (can[..., 4] > 127).any()
    assert int((raw != can).any(-1).sum()) == 1
    seeds = C.admit_seeds("FLIP", 0)[:32]
    pt, _ = C.eval_programs(ph, env, seeds, [raw, can], device="cpu")
    assert np.array_equal(pt[0], pt[1])
    for fam in C.PLANTS:
        for nm, fn in C.PLANTS[fam].items():
            g = fn(ph)
            assert ((g[..., :4] >= 0) & (g[..., :4] <= 255)).all() and ((g[..., 4] >= -128) & (g[..., 4] <= 127)).all(), nm


def test_seeded_arm_shares_gen0_with_base():
    """CRN pairing: the seeded arm differs from BASE at gen 0 ONLY at index 0."""
    ph = C.Physics.from_dict(dict(C.Physics().to_dict(), prog_len=16, rules=1, state_dim=2)).validate()
    g1 = np.random.default_rng(99); g2 = np.random.default_rng(99)
    a = search.random_genomes(g1, 96, ph); b = search.random_genomes(g2, 96, ph)
    b[0] = C.p_flip(ph)
    assert np.array_equal(a[1:], b[1:]) and g1.random() == g2.random()


def test_namespaces_fresh():
    assert C.C2A_NS not in (0x7A1, 0xF1A, 0x4E1D, 0x57324144)
    assert C.search_seed(1, 0) != C.search_seed(1, 1) != C.search_seed(2, 0)
