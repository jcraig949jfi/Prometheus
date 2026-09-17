"""WSE (workspace ecology) -- worlds are well posed, controls behave, loop is deterministic."""
import json

import pytest

from proteus.foundry.prng import SplitMix64
from archaeon.wse import controls as C
from archaeon.wse import interventions as I
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import evaluate, run_cell
from archaeon.wse.worlds import (K_ASK, K_ASK2, K_ASKO, K_ASKX, K_DEF, K_PUT, K_SETOP, MASK32, WorldSpec,
                                 combine, episodes_for, erase_ceiling, make_episode)
from archaeon.wse.survey import CELLS, classify, run_controls


def _reference(ep):
    """An independent evaluator of the event grammar: a dict of stream states, nothing shared
    with worlds.py beyond the kind codes."""
    st, op, first, last, nodes = {}, {}, {}, {}, {}
    pending = []
    out = {}
    for ti, w in enumerate(ep.ticks):
        k = w[0]
        if k == K_SETOP:
            op[w[1]] = (w[2], w[3], w[4])
        elif k == K_PUT:
            v = sum(w[2:]) & MASK32
            t = w[1]
            a, b, c = op.get(t, (1, 1, 0))
            st[t] = v if t not in st else (a * st[t] + b * v + c) & MASK32
            first.setdefault(t, v); last[t] = v
            nodes[t] = v
        elif k == K_DEF:
            pending.append(w)
        elif k == K_ASK:
            # resolve pending defs (any order) then answer
            progress = True
            while pending and progress:
                progress = False
                for d in list(pending):
                    if d[5] in nodes and d[6] in nodes:
                        nodes[d[1]] = (d[2] * nodes[d[5]] + d[3] * nodes[d[6]] + d[4]) & MASK32
                        pending.remove(d); progress = True
            out[ti] = st[w[1]] if w[1] in st else nodes[w[1]]
        elif k == K_ASKX:
            t, y = w[1], w[2]
            a, b, c = op.get(t, (1, 1, 0))
            out[ti] = (a * st[t] + b * y + c) & MASK32
        elif k == K_ASK2:
            out[ti] = combine(w[3], st[w[1]], st[w[2]])
        elif k == K_ASKO:
            t = next(u for u in first if first[u] == w[1])
            out[ti] = last[t]
    return out


@pytest.mark.parametrize("spec", CELLS, ids=[c.name for c in CELLS])
def test_every_survey_cell_matches_an_independent_reference(spec):
    for i in range(20):
        ep = make_episode(spec, SplitMix64(1000 + i))
        assert _reference(ep) == ep.expected, spec.name
        assert ep.n_asks() >= 1
        assert 0 < ep.intervention_tick <= len(ep.ticks)
        assert all(0 <= x <= MASK32 for tk in ep.ticks for x in tk)


def test_identities_are_re_randomised_per_episode_and_families_do_not_overlap():
    spec = WorldSpec("W3_K4", K=4, ask_mode="one")
    a = episodes_for(spec, 7, "train", 0, 8)
    b = episodes_for(spec, 7, "heldout", 0, 8)
    tags_a = [tuple(e.meta["tags"]) for e in a]
    assert len(set(tags_a)) == 8
    assert not set(tags_a) & {tuple(e.meta["tags"]) for e in b}
    assert [e.ticks for e in episodes_for(spec, 7, "train", 0, 8)] == [e.ticks for e in a]     # replayable


def test_positive_controls_solve_and_nulls_do_not():
    for name in ("W0", "W1_d16", "W2_K8", "W3_K8"):
        spec = next(c for c in CELLS if c.name == name)
        eps = episodes_for(spec, 3, "controls", 0, 16)
        pos = C.POSITIVE[name.split("_")[0]]
        assert evaluate(pos, eps)["reward"] == 1.0, name
        for nm, m in C.NULLS.items():
            assert evaluate(m, eps)["reward"] < 0.05, (name, nm)


def test_cheat_battery_sees_each_mechanism_and_ceiling_bounds_the_drop():
    ctl = run_controls(5, N=20, E=12, cells=[c for c in CELLS if c.name in ("W1_d4", "W2_K4")])
    assert ctl["verdict"] == "PASS", ctl["failures"]
    regs = ctl["cheat"]["POS_REGS_on_W1_d4"]
    table = ctl["cheat"]["POS_TABLE_on_W2_K4"]
    assert regs["drop"]["ERASE_REGS"] == 1.0 and regs["drop"]["ERASE_TAPE"] == 0.0
    assert table["drop"]["ERASE_REGS"] == 0.0
    assert table["drop"]["ERASE_TAPE"] <= table["erase_ceiling"] + 1e-9
    assert table["drop"]["SCRAMBLE_LOC"] >= 0.8 * table["erase_ceiling"]


def test_interventions_change_only_what_they_name():
    from proteus.foundry.vm import Player
    p = Player(C.POS_TABLE)
    st = p.fresh_state()
    glen = p.genome_len
    for i in range(glen, glen + 10):
        st["tape"][i] = i
    st["regs"][0] = 5
    rng = SplitMix64(1)
    s2 = {"tape": list(st["tape"]), "regs": list(st["regs"]), "ip": 8, "ticks": 3}
    I.apply("ERASE_REGS", p, s2, rng)
    assert s2["regs"] == [0] * len(st["regs"]) and s2["tape"] == st["tape"]
    s3 = {"tape": list(st["tape"]), "regs": list(st["regs"]), "ip": 8, "ticks": 3}
    I.apply("SCRAMBLE_LOC", p, s3, rng)
    assert sorted(s3["tape"][glen:]) == sorted(st["tape"][glen:]) and s3["tape"][:glen] == st["tape"][:glen]
    s4 = {"tape": list(st["tape"]), "regs": list(st["regs"]), "ip": 8, "ticks": 3}
    I.apply("RESET_IP", p, s4, rng)
    assert s4["ip"] == 0 and s4["tape"] == st["tape"]


def test_run_cell_is_deterministic_and_records_lineage():
    spec = WorldSpec("W1_d1", delay=1)
    a = run_cell(spec, REGIMES["E1"], 11, 1, N=12, G_=4, E=4)
    b = run_cell(spec, REGIMES["E1"], 11, 1, N=12, G_=4, E=4)
    assert a["elite"]["organism_id"] == b["elite"]["organism_id"]
    assert json.dumps(a["trace"], sort_keys=True) == json.dumps(b["trace"], sort_keys=True)
    assert len(a["trace"]) == 4
    c = run_cell(spec, REGIMES["E1"], 11, 2, N=12, G_=4, E=4)
    assert c["trace"] != a["trace"]                    # the seed is load-bearing
    if a["elite"]["generation"] > 0:
        assert a["ancestry"] and a["ancestry"][0]["organism_id"] == a["elite"]["organism_id"]


def test_classifier_uses_the_preregistered_predicates():
    spec = WorldSpec("W1_d4", delay=4)
    base = {"reward_heldout": 0.9, "reward_heldout_K2x": 0.85, "persist": "regs", "fanout_curve": None,
            "intervention_drop": {n: 0.0 for n in I.NAMES}}
    base["intervention_drop"]["ERASE_REGS"] = 0.9; base["intervention_drop"]["ERASE_ALL"] = 0.9
    assert classify(spec, base, 0.0)["class"] == "TRIVIAL_RECURRENCE"
    assert classify(spec, dict(base, reward_heldout=0.05), 0.0)["class"] == "NO_ADAPTATION"
    t = dict(base, persist="tape"); t["intervention_drop"] = dict(base["intervention_drop"], ERASE_REGS=0.0, ERASE_TAPE=0.9, SCRAMBLE_LOC=0.0)
    assert classify(spec, t, 0.0)["class"] == "STRUCTURED"
    t["intervention_drop"]["SCRAMBLE_LOC"] = 0.9; t["reward_heldout_K2x"] = 0.5
    assert classify(spec, t, 0.0)["class"] == "SPECIALIZED_MEMORY"


def test_erase_ceiling_is_one_when_the_only_asked_stream_is_complete():
    spec = WorldSpec("W3_K4", K=4, ask_mode="one")
    assert erase_ceiling(episodes_for(spec, 1, "x", 0, 10)) == 1.0
