"""PTE-C2B known-answer tests (order s24, s26). CPU.
Run: python -m pytest roles/Ananke/pte/c2b/test_c2b.py -q -p no:cacheprovider"""
import dataclasses
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

import c2b_common as B  # noqa: E402
C = B.C
from prometheus.ananke import search  # noqa: E402
from prometheus.ananke.search import FINAL_NS, HELD_NS, TRAIN_NS  # noqa: E402

PH = C.Physics.from_dict(dict(C.Physics().to_dict(), prog_len=16, rules=1, state_dim=2, payload_width=1,
                              channels=1)).validate()
SP = search.SearchSpec(pop=96, M=8, gens=36)


def test_tagged_mutate_and_crossover_match_search_exactly():
    for seed in range(200):
        g1, g2 = np.random.default_rng(seed), np.random.default_rng(seed)
        a = search.random_genomes(g1, 2, PH); search.random_genomes(g2, 2, PH)
        x1 = search.crossover(g1, a[0], a[1]); y1 = search.mutate(g1, x1, SP)
        t = np.ones(a.shape[:3], bool); t[1] = False
        x2, tx = B.crossover_tagged(g2, a[0], a[1], t[0], t[1])
        y2, ty = B.mutate_tagged(g2, x2, tx, SP)
        assert np.array_equal(y1, y2) and g1.random() == g2.random()


def test_lineage_tags_semantics():
    sp = dataclasses.replace(SP, p_field=1.0, p_instr=0.0, p_swap=0.0)        # every field resampled
    g = np.random.default_rng(1)
    a = search.random_genomes(g, 1, PH)[0]
    c, t = B.mutate_tagged(g, a, np.ones(a.shape[:2], bool), sp)
    assert t.all() and not np.array_equal(c, a)                  # field edits keep descent
    sp2 = dataclasses.replace(SP, p_field=0.0, p_instr=1.0, p_swap=0.0)
    c, t = B.mutate_tagged(g, a, np.ones(a.shape[:2], bool), sp2)
    assert t.sum() == t.size - 1                                  # a fresh random line loses the tag
    b = search.random_genomes(g, 1, PH)[0]
    x, tx = B.crossover_tagged(g, a, b, np.ones(a.shape[:2], bool), np.zeros(b.shape[:2], bool))
    assert np.array_equal(np.all(x == a, -1) | ~tx, np.ones_like(tx)) and 0 < tx.mean() < 1


def test_attribution_distinguishes_descendant_from_background():
    assert B.attribute(True, 0.75, "BRK1") == "BROKEN_LINEAGE_RECOVERY"
    assert B.attribute(True, 0.5, "STEP") == "STEP_LINEAGE_SUCCESS"
    assert B.attribute(True, 0.4375, "BRK2") == "BACKGROUND_SUCCESS"
    assert B.attribute(True, 0.0, "STEP") == "BACKGROUND_SUCCESS"
    assert B.attribute(True, None, "B4X") == "BACKGROUND_SUCCESS"
    assert B.attribute(False, 1.0, "BRK1") is None


def test_broken_start_rejects_neutral_and_indeterminate_accepts_false():
    plant = C.PLANTS["FLIP"]["P_FLIP"](PH)
    seq = iter(["TRUE", "INDETERMINATE", "TRUE", "FALSE", "FALSE"])
    g, att = B.broken_start(PH, None, "FLIP", plant, 1, 777, 0, score=lambda x: next(seq))
    assert [a["status"] for a in att] == ["TRUE", "INDETERMINATE", "TRUE", "FALSE"]
    assert int((g != plant).sum()) == 1
    # exact regeneration of the accepted edit from (cell_key, k, idx, attempt)
    rng = np.random.default_rng(C.H_int(B.C2B_NS, B.BRK_EDIT_KEY, 777, 1, 0, 3))
    g2, e2 = B.k_edit(plant, 1, rng)
    assert np.array_equal(g, g2) and e2 == att[-1]["edits"]
    g3, att3 = B.broken_start(PH, None, "FLIP", plant, 2, 777, 0, score=lambda x: "TRUE")
    assert g3 is None and len(att3) == B.MAX_BRK_ATTEMPTS        # capped, reported as a failure


def test_k_edit_exactly_k_ga_native():
    plant = C.PLANTS["FLIP"]["P_FLIP"](PH)
    for k in (1, 2):
        for s in range(50):
            g, e = B.k_edit(plant, k, np.random.default_rng(s))
            assert int((g != plant).sum()) == k and len({(x[0], x[1], x[2]) for x in e}) == k
            assert ((g[..., :4] >= 0) & (g[..., :4] <= 255)).all() and ((g[..., 4] >= -128) & (g[..., 4] <= 127)).all()


def test_qualification_namespace_distinct():
    keys = {B.BROKEN_QUAL_KEY, B.STEP_QUAL_KEY, B.BRK_EDIT_KEY, B.FINAL_CKPT_KEY}
    assert len(keys) == 4 and B.C2B_NS != C.C2A_NS
    q = set(B.qual_seeds(12345)); s = C.search_seed(12345, 0)
    prod = set(C.assays.world_seeds(C.H_int(s, HELD_NS), 128)) | set(C.assays.world_seeds(C.H_int(s, FINAL_NS), 16))
    for gen in range(144):
        prod |= set(C.assays.world_seeds(C.H_int(s, TRAIN_NS, gen), 32))
    assert not (q & prod)


def test_evolve_c2b_matches_c2a_runner():
    """The lineage-tagged loop reproduces C2A's evolve_c2a population exactly (small spec, CPU)."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "c2a"))
    import run as R2A
    import run_c2b as R2B
    from prometheus.ananke import envs
    env = envs.EnvSpec(family="FLIP", d=1, delta=4, trials=8, block=4)
    sp = dataclasses.replace(SP, pop=12, gens=3, M=2, M_final=2, elite=2)
    plant = C.PLANTS["FLIP"]["P_FLIP"](PH)
    a = R2A.evolve_c2a(PH, env, 4242, sp, "cpu", init=plant, plant=plant)
    hs = C.assays.world_seeds(C.H_int(4242, HELD_NS), 8)
    b = R2B.evolve_c2b(PH, env, 4242, sp, "cpu", init=plant, ckpts=(sp.gens - 1,), held=hs, role="FLIP")
    assert np.array_equal(a["pop"], b["pop"])
    assert b["checkpoints"][sp.gens]["champ_index"] == a["champ_index"]
