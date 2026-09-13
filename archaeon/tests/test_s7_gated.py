"""S7: the gated candidate is EXACTLY G outside 5 <= N <= 18 and EXACTLY S6 A_v2w_0 inside; the gate sees only N;
permutation controls of the S5 defect class; no target/oracle in any signature."""
import inspect
import json
import random
from pathlib import Path

from archaeon.producer import fossil_inference as FI, s4_producers as P, s6_endgame as S6, s7_gated as G7

ROOT = Path(__file__).resolve().parents[2]


def _score(x, t):
    return sum(a == b for a, b in zip(x, t)) / len(t)


def _same(a, b):
    return a.probe == b.probe and a.tie_class == b.tie_class and a.objective_value == b.objective_value and a.ancestry.get("pool_size") == b.ancestry.get("pool_size")


def _states(L, n):
    """Evidence states from the S6 endgame universe files (real decision states G reached), spread over N."""
    rows = json.loads((ROOT / ("archaeon/docs/h0h5/S6_ENDGAME_UNIVERSE_L%d_2026-09-13.json" % L)).read_text(encoding="utf-8"))
    rnd = random.Random(7); rnd.shuffle(rows)
    return [[FI.Fossil(b, s) for b, s in r["fossils"]] for r in rows[:n]]


def test_signatures_carry_no_target_or_oracle():
    for fn in (G7.gate, G7.produce_gated_v2w):
        assert not any(k in ("target", "hidden_target", "t", "oracle", "target_index", "winner", "outcome") for k in inspect.signature(fn).parameters), fn
    assert (G7.GATE_LOW, G7.GATE_HIGH, G7.STATISTIC, G7.WINDOW) == (5, 18, "v2w", 0.0)


def test_outside_the_gate_the_candidate_is_G_exactly_and_inside_it_is_A_v2w_0_exactly():
    n_out = n_in = 0
    for L in (8, 9):
        for k, fs in enumerate(_states(L, 400)):
            si = {"lane": "t7", "L": L, "world": "w%d" % k, "arm": "G", "step": 1}
            c = G7.produce_gated_v2w(fs, si); N = FI.infer(fs).feasible_targets
            assert c.extra["gate"]["N"] == N and c.producer_id == "GATED_V2W"
            if 5 <= N <= 18:
                assert c.extra["gate"]["active"] and c.extra["gate"]["branch"] == "v2w" and _same(c, S6.produce_refined(fs, si, "v2w", 0.0)); n_in += 1
            else:
                assert not c.extra["gate"]["active"] and c.extra["gate"]["branch"] == "G" and _same(c, P.produce_G(fs, si)); n_out += 1
    assert n_out >= 100 and n_in >= 50


def test_the_seven_S6_canaries_root_decision_is_G():
    can = json.loads((ROOT / "archaeon/docs/h0h5/S7_CANARIES_FROM_S6_2026-09-13.json").read_text(encoding="utf-8"))
    assert len(can) == 7
    for L in (8, 9):
        worlds = {w["state_id"]: w for w in json.loads((ROOT / ("archaeon/docs/h0h5/S5_RESULTS_RUN2_L%d_SLIM_2026-09-13.json" % L)).read_text(encoding="utf-8"))["worlds"]}
        for c in can:
            if c["L"] != L:
                continue
            fs = [FI.Fossil(b, s) for b, s in worlds[c["root"]]["fossils"]]; si = {"lane": "s6", "L": L, "world": c["root"], "arm": "G", "step": 1}      # the S6 seeds verbatim: identical pools, so the S6 offending choice is reproduced and then suppressed
            g = P.produce_G(fs, si); x = G7.produce_gated_v2w(fs, si); v = S6.produce_refined(fs, si, "v2w", 0.0)
            assert x.extra["gate"]["N"] == 30 and not x.extra["gate"]["active"] and _same(x, g)
            assert v.probe != g.probe, "the S6 offending refinement is expected to differ from G at this root"   # it is exactly what the gate must suppress


def test_permutation_controls_fossil_order_cannot_change_the_decision():
    for L in (8, 9):
        for k, fs in enumerate(_states(L, 60)):
            si = {"lane": "t7", "L": L, "world": "p%d" % k, "arm": "G", "step": 3}
            ref = G7.produce_gated_v2w(fs, si)
            for perm in (fs[::-1], sorted(fs, key=lambda f: f.score), sorted(fs, key=lambda f: f.bits, reverse=True)):
                assert _same(G7.produce_gated_v2w(perm, si), ref) and G7.gate(perm)["N"] == ref.extra["gate"]["N"]


def test_gate_sees_only_the_count_and_provenance_carries_no_oracle_or_target():
    fs = _states(8, 5)[0]; si = {"lane": "t7", "L": 8, "world": "z", "arm": "G", "step": 1}
    c = G7.produce_gated_v2w(fs, si); s = repr(c.ancestry) + repr(c.extra)
    assert "oracle" not in s and "V_star" not in s and "Q_" not in s and c.extra["gate"]["gate_units"] > 0 and c.extra["gate"]["candidate_version"] == G7.CANDIDATE_VERSION
