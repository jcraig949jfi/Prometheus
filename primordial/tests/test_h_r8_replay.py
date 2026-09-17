"""H R8 replay: the independent C-R8-AP-01 evaluator agrees with C's reference on random genomes, catches planted
value/byte/duplicate defects, and the D-R8-1 re-derivation reaches INDETERMINATE on a failing binding control."""
import copy

import numpy as np

from primordial.cohorts.c import r8_ap01_pairwise_d1_corruption_graphblas as C
from primordial.lingua import signal as S
from primordial.score import replay_r8 as R


def test_r_stream_py_matches_signal():
    seeds = [0, 1, 127, 10_000_000, 10_000_255]
    assert np.array_equal(R.r_stream_py(seeds, 64), S.r_stream(np.array(seeds), 64))


def _c_rows(n_ctrl=32):
    hs = C.hists()
    rng = np.random.Generator(np.random.PCG64(5))
    G = np.concatenate([C.init(rng, n_ctrl - 1), C.planted()[:1]])
    held = C.ref_fit(G, hs["held_clean"]) / hs["held_clean"].sum()
    rows = [{"kind": "reference", "floor_held": C.floor_of(hs["held_clean"])}]
    for i, (f, s) in enumerate((f, s) for f in C.FAMILIES for s in range(8)):
        scr = C.scrambled_yield(G[i], C.HELD, False, [C.STREAM_TAG, f, s, C.ARM_INDEX["control"], 99])
        rows.append({"kind": "run", "arm": "control", "family": f, "run_seed": s, "top1_hex": G[i].tobytes().hex(),
                     "held_yield_top1": float(held[i]), "held_scrambled_top1": scr, "scramble_lowers": scr < held[i],
                     "recount_mismatched_top16": 0, "offers_mismatched": 0})
    return rows


def test_c_independent_evaluator_agrees_and_catches_plants():
    rows = _c_rows()
    rep = R.replay_c_ap01(rows)
    checks = [rep["floor_agrees"], rep["runs_replayed"] == 32, rep["value_mismatches"] == [],
              rep["balance"]["control"]["balanced_32_4_8"]]
    bad = copy.deepcopy(rows)
    bad[4]["held_yield_top1"] += 1 / 16384
    g = bytearray.fromhex(bad[9]["top1_hex"])
    g[100] ^= 1
    bad[9]["top1_hex"] = g.hex()
    bad.append(copy.deepcopy(bad[12]))
    rep2 = R.replay_c_ap01(bad)
    got = {(m["family"], m["run_seed"]) for m in rep2["value_mismatches"]}
    checks += [(bad[4]["family"], bad[4]["run_seed"]) in got, (bad[9]["family"], bad[9]["run_seed"]) in got,
               rep2["balance"]["control"]["duplicates"] == [(bad[12]["family"], bad[12]["run_seed"])],
               not rep2["balance"]["control"]["balanced_32_4_8"]]
    assert len(checks) == 8 and all(checks), checks


def test_d_rederivation_controls_and_decision():
    rows = []
    for fam, rk in R.D_CELLS:
        for w in R.D_WORLDS:
            for s in range(8):
                base = {"linear": 10.0, "tt_feat": 8.0 - 0.1 * (3 - rk), "tt_digits": 5.0}[fam]
                x = {"kind": "run", "family": fam, "rank": rk, "gen_seed": w, "run_seed": s,
                     "held64_per_seed": base + s * 0.01}
                if s == 0:
                    x.update(world_oracle_honest={"elites_failing": 0}, world_oracle_skip_lin={"elites_failing": 16},
                             brain_oracle_honest={"mismatched_rows": 0}, brain_oracle_cheat={"elites_mismatching": 16})
                rows.append(x)
    rep = R.replay_d_r8_1(rows)
    assert rep["decision_replay"] == "PARITY_HOLDS" and rep["i1_ok"] and rep["controls_ok"]
    weak = copy.deepcopy(rows)
    next(x for x in weak if x["family"] == "tt_feat" and x["rank"] == 1 and x["run_seed"] == 0)[
        "brain_oracle_cheat"] = {"elites_mismatching": 3}
    rep2 = R.replay_d_r8_1(weak)
    assert rep2["decision_replay"] == "INDETERMINATE" and rep2["failing_oracle_cells"]
    assert R.replay_d_r8_1(weak[:-1])["balance"]["complete_168"] is False


def test_signflip_mc_agrees_with_e_estimator_on_synthetic():
    from primordial.cohorts.e.transfer import signflip_p
    rng = np.random.default_rng(3)
    checks = []
    for shift in (0.0, 0.3, 0.6):
        d = rng.normal(shift, 1.0, 32)
        p, se = R.signflip_mc(d, draws=200_000)
        checks.append(abs(p - signflip_p(d)) < 5 * se + 1e-4)
    assert len(checks) == 3 and all(checks), checks


def test_e_h1_incomplete_is_indeterminate():
    rows = [{"condition": a, "status": "control", "run_id": f"{f}|{s}", "held_auc": 1.0}
            for f in R.FAMILIES for s in range(24, 31) for a in R.E_ARMS]
    rep = R.replay_e_h1(rows)
    assert rep["n_complete_runs"] == 28 and rep["outcome_replay"] == "INDETERMINATE"
