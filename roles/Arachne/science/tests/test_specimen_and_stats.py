"""Controls for the specimen loader and the preregistered statistics.
- specimen: the manifest gate must refuse a tampered copy (cheat control on
  the freeze), the tick mapping must be monotone, and the fitness
  reconstruction must reproduce the swarm's logged parent_fitness
  (positive control, run on the real archive).
- branch_fitness: the sign statistic must read INDETERMINATE below the
  frozen eligibility, must see a planted effect (positive), and must not
  see one in symmetric data (negative).
- emergence: NMI/ARI on known partitions; a null must preserve degrees.
"""
from __future__ import annotations

import json
import random
import shutil
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
REPO = HERE.parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import specimen as SP                    # noqa: E402
import branch_fitness as BF              # noqa: E402
import emergence as EM                   # noqa: E402


@pytest.fixture(scope="module")
def S():
    return SP.Specimen()


def test_specimen_manifest_verifies_and_two_segments(S):
    assert len(S.hashes) == 6
    assert sum(e["segment"] == 1 for e in S.edges) == 1424
    assert sum(e["segment"] == 2 for e in S.edges) == 19785


def test_specimen_cheat_tampered_copy_is_refused(tmp_path, monkeypatch):
    dst = tmp_path / "run"
    shutil.copytree(SP.ARCHIVE, dst)
    p = dst / "population.json"
    p.write_text(p.read_text(encoding="utf-8").replace("\"tick\"", "\"tick_\"", 1), encoding="utf-8")
    monkeypatch.setattr(SP, "ARCHIVE", dst)
    with pytest.raises(RuntimeError, match="tampered"):
        SP.verify_manifest()


def test_tick_mapping_is_monotone_within_segment(S):
    for seg in (1, 2):
        es = sorted((e for e in S.edges if e["segment"] == seg), key=lambda e: e["order"])
        ticks = [e["tick"] for e in es]
        assert all(b >= a for a, b in zip(ticks, ticks[1:]))
        assert ticks[0] >= 1


def test_fitness_reconstruction_reproduces_logged_parent_fitness(S):
    v = S.validate_reconstruction()
    assert v["n"] == 82 and v["n_reconstructed"] == 82
    assert v["within_0.10"] == 82 and v["max_abs_err"] <= 0.10


def test_death_rows_edge_counts_reproduced_exactly(S):
    rows = [c for c in S.crawlers.values() if c.get("total_edges_logged") is not None]
    assert len(rows) == 124 and all(c["edges"] == c["total_edges_logged"] for c in rows)


# ---- branch-fitness statistic --------------------------------------------
def test_sign_stat_indeterminate_below_frozen_eligibility():
    st = BF.sign_stat([(1.0, 0.0)] * 19)
    assert st["status"] == "INDETERMINATE" and st["n_nontied"] == 19


def test_sign_stat_negative_symmetric_data_includes_half():
    rng = random.Random(0)
    pairs = [(rng.random(), rng.random()) for _ in range(200)]
    st = BF.sign_stat(pairs, tie=0.0)
    lo, hi = st["ci95"]
    assert lo < 0.5 < hi


def test_sign_stat_positive_planted_effect_excludes_half():
    rng = random.Random(1)
    pairs = [(rng.random() + 0.4, rng.random()) for _ in range(60)]
    st = BF.sign_stat(pairs, tie=0.0)
    assert st["ci95"][0] > 0.5 and BF.read_ladder(st) == "EXCLUDES_0.5_UP"


def test_sign_stat_cheat_all_ties_are_excluded_not_counted():
    st = BF.sign_stat([(0.5, 0.52)] * 30, tie=0.05)
    assert st["ties"] == 30 and st["n_nontied"] == 0 and st["status"] == "INDETERMINATE"


# ---- emergence instrument -------------------------------------------------
def test_nmi_ari_known_partitions():
    a = {i: i % 2 for i in range(100)}
    assert EM.nmi(a, a) == pytest.approx(1.0) and EM.ari(a, a) == pytest.approx(1.0)
    b = {i: (i // 50) for i in range(100)}
    assert abs(EM.nmi(a, b)) < 0.05 and abs(EM.ari(a, b)) < 0.05


def test_null_N1_preserves_degree_sequence_on_a_toy():
    import networkx as nx
    G = nx.Graph()
    edges = [("a:{}".format(i), "a:{}".format((i * 7 + 3) % 40)) for i in range(40)] + [("a:{}".format(i), "b:{}".format(i)) for i in range(20)]
    for u, v in edges:
        if u != v:
            G.add_edge(u, v, ops={"x"}, crawlers={"c"})
    H = EM.null_N1(G, 3)
    assert sorted(d for _, d in H.degree()) == sorted(d for _, d in G.degree())
