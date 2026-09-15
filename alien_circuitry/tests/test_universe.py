"""Phase A/B instrument tests.  Run: python -m pytest alien_circuitry/tests -q"""
import itertools, random
import numpy as np
import pytest
from alien_circuitry.universe import directed_rewriting as dr
from alien_circuitry.universe.presentations import rules_for, exponent_vector
from alien_circuitry.universe.enumerate import build, graph_hash, UNREACH
from alien_circuitry.universe import metrics as M
from alien_circuitry.controls import construct as C


@pytest.fixture(scope="module")
def U6():
    return build("BRAID_B3", 6)


@pytest.fixture(scope="module")
def A6():
    return build("ABELIAN", 6)


def test_index_word_bijection():
    L = 4
    words = [""] + ["".join(p) for l in range(1, L + 1) for p in itertools.product(dr.ALPHABET, repeat=l)]
    idx = [dr.word_index(w, L) for w in words]
    assert idx == list(range(len(words)))
    assert all(dr.index_word(i, L) == w for i, w in zip(idx, words))


def test_vectorised_matches_scalar_semantics():
    for name in ("BRAID_B3", "ABELIAN"):
        L = 5; rules = rules_for(name); tr = dr.transitions(L, rules)
        got = set(zip(tr["src"].tolist(), tr["dst"].tolist(), tr["rule"].tolist(), tr["pos"].tolist()))
        exp = set()
        for i in range(tr["NS"]):
            w = dr.index_word(i, L)
            for rid, r in enumerate(rules):
                for p in range(len(w) - len(r.lhs) + 1):
                    w2 = dr.apply_rule_str(w, r, p, L)
                    if w2 is not None:
                        exp.add((i, dr.word_index(w2, L), rid, p))
        assert got == exp


def test_enumeration_deterministic(U6):
    h1 = graph_hash(U6); h2 = graph_hash(build("BRAID_B3", 6))
    assert h1 == h2


def test_length_never_increases_and_no_duplicate_distinct_edges(U6):
    LEN = U6["LEN"]
    assert (LEN[U6["dst"]] <= LEN[U6["src"]]).all()
    pairs = np.stack([U6["dsrc"], U6["ddst"]], axis=1)
    assert len(np.unique(pairs, axis=0)) == len(pairs)


def test_abelian_exponent_vector_invariant(A6):
    L = 6
    for s, d in zip(A6["dsrc"][:5000].tolist(), A6["ddst"][:5000].tolist()):
        assert exponent_vector(dr.index_word(s, L)) == exponent_vector(dr.index_word(d, L))


def test_D_matches_forward_bfs(U6):
    S = M.Searcher(U6); rng = random.Random(1)
    for _ in range(300):
        s = rng.randrange(U6["NS"]); j = rng.randrange(len(U6["targets"]))
        f = S.forward_bfs(s, U6["targets"][j])
        assert f["dist"] == int(U6["D"][s, j])


def test_bfs_bibfs_oracle_agree(U6, A6):
    for U in (U6, A6):
        b = M.baselines(U, per_stratum=150)
        assert b["distance_mismatches_bfs_bibfs_D_oracle"] == 0


def test_search_budget_accounting(U6):
    S = M.Searcher(U6); od = U6["outdeg"]
    fi, fx = U6["fwd"]
    s, t = U6["targets"][3], U6["targets"][0]
    # transitions examined by forward BFS == sum of out-degrees of expanded states (re-run with instrumentation)
    seen = {s}; dq = [s]; expanded = []; found = False
    while dq and not found:
        v = dq.pop(0); expanded.append(v)
        if v == t: found = True; break
        for u in fx[fi[v]:fi[v + 1]]:
            if int(u) not in seen: seen.add(int(u)); dq.append(int(u))
    f = S.forward_bfs(s, t)
    assert f["states_expanded"] == len(expanded)
    assert f["transitions_examined"] == int(sum(od[v] for v in expanded[:-1]))


def test_trap_definition(U6):
    tr = M.trap_analysis(U6)
    D = U6["D"]; L = 6
    for ex in tr["examples"]:
        s = dr.word_index(ex["state"], L); j = U6["targets"].index(dr.word_index(ex["target"], L))
        assert D[s, j] >= 0
        assert D[dr.word_index(ex["trap_successor"], L), j] == UNREACH
        assert D[dr.word_index(ex["ok_successor"], L), j] >= 0
        assert ex["trap_successor_outdeg"] > 0  # latent, not visible
    assert tr["totals"]["trap"] == tr["totals"]["visible_no_continuation"] + tr["totals"]["visible_length_bound"] + tr["totals"]["latent"]


def test_chart_accounting(U6):
    cd = M.chart_D(U6)
    assert cd["storage_dense"]["raw_bytes"] == U6["NS"] * len(U6["targets"]) * 2
    assert cd["storage_sparse_coo"]["raw_bytes"] == cd["live_entries"] * 6
    assert cd["storage_sparse_coo"]["lzma_bytes"] < cd["storage_sparse_coo"]["raw_bytes"]
    cm = M.chart_M(U6)
    assert cm["edge_target_entries"] == len(U6["src"]) * len(U6["targets"])
    assert cm["storage"]["edge_target_raw_bytes"] == 2 * cm["edge_target_entries"]
    assert cm["flag_counts"]["trap"] == M.trap_analysis(U6)["totals"]["trap"]


def test_masks_deterministic_and_disjoint(U6):
    m1 = M.mask_proposal(U6); m2 = M.mask_proposal(U6)
    assert m1 == m2
    live = int((U6["D"] >= 0).sum())
    assert sum(m1["state_target_entries"].values()) == live
    assert sum(v["live_entries"] for v in m1["state_rows"].values()) == live


def test_controls_behave(U6):
    # NC1-B: exact per-column marginals
    Dp = C.consequence_permutation(U6["D"], seed=1)
    for j in range(U6["D"].shape[1]):
        assert np.array_equal(np.sort(Dp[:, j]), np.sort(U6["D"][:, j]))
    assert not np.array_equal(Dp, U6["D"])
    # NC1-A: degrees preserved, no self loops, no multi-edges
    s2, d2, info = C.degree_preserving_shuffle(U6["dsrc"], U6["ddst"], seed=1, swaps_per_edge=2)
    n = U6["NS"]
    assert np.array_equal(np.bincount(s2, minlength=n), np.bincount(U6["dsrc"], minlength=n))
    assert np.array_equal(np.bincount(d2, minlength=n), np.bincount(U6["ddst"], minlength=n))
    assert (s2 != d2).all() and len(np.unique(np.stack([s2, d2], 1), axis=0)) == len(s2) and info["swaps_done"] > 0
    # PC3: naive flattening full rank, structured flattening rank 1
    pc = C.pc3_kronecker(5, seed=1)
    assert np.linalg.matrix_rank(pc["naive_flattening"]) == 25
    assert np.linalg.matrix_rank(pc["structured_flattening"]) == 1
    # PC2: clones add nominal edges but no distinct edges
    Uc = build("BRAID_B3", 5); Uk = build("BRAID_B3", 5, with_clones=True)
    assert np.array_equal(Uc["dsrc"], Uk["dsrc"]) and np.array_equal(Uc["ddst"], Uk["ddst"])
    assert len(Uk["src"]) > len(Uc["src"]) and np.array_equal(Uc["D"], Uk["D"])
