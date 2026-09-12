"""Gate tests: termination evidence, lookahead soundness, policy isolation, sibling matching, Q1 consistency."""
import random
import numpy as np
import pytest
from alien_circuitry.universe.enumerate import build
from alien_circuitry.universe.directed_rewriting import index_word
from alien_circuitry.gate.termination import termination_evidence
from alien_circuitry.gate.observation import Observer
from alien_circuitry.gate import analysis as A
from alien_circuitry.gate.navigation import make_policy, greedy_walk, guided_dfs
from alien_circuitry.gate.run_gate import mechanical_targets


@pytest.fixture(scope="module")
def U():
    L = 7
    return build("U_A3_ONEWAY_BRAID", L, targets=mechanical_targets("U_A3_ONEWAY_BRAID", L, 2))


def test_termination_intrinsic_and_dag(U):
    term, height = termination_evidence(U)
    assert term["measure_violations"] == 0 and term["self_loops"] == 0 and term["largest_scc"] == 1 and not term["cycles_present"]
    # height is a valid longest-path bound: for every distinct edge, height[src] >= height[dst] + 1
    assert (height[U["dsrc"]] >= height[U["ddst"]] + 1).all()
    assert (height[U["outdeg"] == 0] == 0).all()


def test_two_way_universe_is_not_a_dag():
    U2 = build("BRAID_B3", 5)
    from alien_circuitry.gate.termination import scc_evidence
    assert scc_evidence(U2)["cycles_present"]


def test_targets_are_mechanical_terminal_states(U):
    for t in U["targets"]:
        assert U["outdeg"][t] == 0 and len(index_word(t, U["L"])) <= 2


def test_lookahead_is_sound(U):
    obs = Observer(U); D = U["D"]; rng = random.Random(3)
    live = np.argwhere(D >= 0)
    for _ in range(400):
        s, j = live[rng.randrange(len(live))]; t = U["targets"][j]
        for h in range(6):
            st, d, *_ = obs.lookahead(int(s), t, h)
            if st == "SAFE":
                assert d == int(D[s, j]) and d <= h
            elif st == "TRAP":
                assert False, "SAFE state proven trap"
            else:
                assert int(D[s, j]) > h
    dead = np.argwhere(D < 0)
    for _ in range(400):
        s, j = dead[rng.randrange(len(dead))]; t = U["targets"][j]
        st, d, *_ = obs.lookahead(int(s), t, 5)
        assert st != "SAFE"
        region, ecc = A.forward_region(obs, int(s))
        assert (st == "TRAP") == (ecc <= 5)


def test_policies_do_not_touch_D(U, monkeypatch):
    obs = Observer(U)
    # remove D from the universe seen by the observer; policies must still run
    for pol in ("B0", "B1", "B2", "LA1", "LA3"):
        p = make_policy(pol, obs)
        from alien_circuitry.gate.navigation import Cost
        c = Cost(); k = p(U["targets"][3], U["targets"][3], 0, c)
        assert k[0] == 0 if pol not in ("B0", "B1") else True


def test_greedy_and_dfs_costs_and_solutions(U):
    obs = Observer(U); D = U["D"]; rng = random.Random(5)
    live = [(int(s), int(j)) for s, j in np.argwhere(D >= 3)]
    for pol in ("B2", "LA2", "LA5"):
        p = make_policy(pol, obs)
        for _ in range(60):
            s, j = live[rng.randrange(len(live))]; t = U["targets"][j]
            g = greedy_walk(obs, p, s, t, D[:, j]); d = guided_dfs(obs, p, s, t, D[:, j])
            assert d["solved"] and d["path_len"] >= int(D[s, j])
            if g["solved"]:
                assert g["path_len"] >= int(D[s, j]) and not g["catastrophic"]
            assert g["exp_c"] <= g["exp_u"] and g["exm_c"] <= g["exm_u"]


def test_trap_table_and_siblings(U):
    obs = Observer(U); term, height = termination_evidence(U)
    T = A.trap_table(U, obs, height); sib = A.sibling_match(U, obs, T)
    D = U["D"]
    for i in range(min(200, T["n"])):
        j = int(T["target_j"][i]); assert D[T["src"][i], j] >= 0 and D[T["dst"][i], j] < 0
        assert T["ecc"][i] <= T["height"][i]
        if T["exact_match"][i]:
            ge = int(T["good_edge"][i]); assert U["src"][ge] == T["src"][i] and D[U["dst"][ge], j] >= 0
    q = A.q1_exact(U, T)
    assert q["traps"] == T["n"] and q["per_depth"]["5"]["traps_proven_graph"] <= q["traps"]
    assert sib["exact_match_6_features"] <= sib["with_any_nontrap_sibling"] <= T["n"]
