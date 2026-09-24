"""D2 (ANOM-1789415790381-0): why a fitness gate passes a wrong world that the trace hash catches.

Claim under test: a one-semantic cheat leaves fitness exactly invariant when the state it corrupts cannot
reach yield_reg. For skip_lin, the lin ops write only their dst registers and no other register reads a
dst, so yield_reg not in dsts -> yield trajectory, charge and fitness identical (theorem direction);
yield_reg in dsts -> fitness usually moves (empirical direction). Measured per world over gen_seed 1..40
on E4's genome distribution, seeds and fitness. Predicate on the bus ("D2-fitness-gate-blindness").

usage: python -m primordial.cohorts.d.d2_run [--quick]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from primordial.fabric.rows import RowWriter
from primordial.qd.e4_run import SEEDS, Spec, init_genomes
from primordial.soup.b1.common import hash_log
from primordial.soup.b1.np_world import NpEncounter

EXP = "D2-fitness-gate-blindness"
ROOT = pathlib.Path(__file__).resolve().parents[2]
CHEATS = ("skip_lin", "no_regime_flip", "stoch_swap", "fix_unaffordable")
N_GEN, N_HASH = 64, 8


def run(spec: Spec, G: np.ndarray, cheat: str):
    """Full-horizon batched episodes, every env recorded. -> world, E4 fitness [P]."""
    P, k = len(G), len(SEEDS)
    n = P * k
    w = NpEncounter(spec.mech, spec.wid, record=np.arange(n), cheat=cheat, with_obs=False)
    w.reset(np.tile(SEEDS, P))
    A = np.repeat(G, k, axis=0).astype(np.int32)
    for t in range(spec.T):
        w.step(A[:, t])
    fit = np.clip(w.charge, 0, None).sum(1).reshape(P, k).sum(1)
    return w, fit


def world_rows(gs: int) -> list[dict]:
    t0 = time.perf_counter()
    try:
        spec = Spec(gs)
    except Exception as e:                                    # infeasible world: kept as an aborted row
        return [{"status": "aborted", "kind": "world", "gen_seed": gs, "reason": repr(e)[:300]}]
    m = spec.mech
    rng = np.random.Generator(np.random.PCG64([7717, gs]))
    G = np.concatenate([np.zeros((1, spec.T, spec.S, spec.W), np.uint8), init_genomes(rng, spec, N_GEN)])
    dsts = sorted({int(op[0]) for op in m.lin_ops})
    y_dst = int(m.yield_reg) in dsts
    hon, f_hon = run(spec, G, "")
    hon2, f_hon2 = run(spec, G, "")
    base = {"gen_seed": gs, "world_id": spec.wid, "T": spec.T, "S": spec.S, "W": spec.W, "n_regs": int(m.n_regs),
            "lin_dsts": dsts, "yield_reg": int(m.yield_reg), "yield_in_dsts": y_dst,
            "regime_period": int(m.regime_period), "stoch_rate": int(m.stoch_rate), "genomes": len(G),
            "envs": len(G) * len(SEEDS)}
    rows = [{"status": "control", "kind": "honest_repeat", **base,
             "fitness_diff_genomes": int((f_hon != f_hon2).sum()),
             "reg_diff_envs": int((hon.log_regs != hon2.log_regs).any(axis=(0, 2)).sum())}]
    for cheat in CHEATS:
        w, f = run(spec, G, cheat)
        reg_env = (w.log_regs != hon.log_regs).any(axis=(0, 2))
        ch_env = (w.charge != hon.charge).any(1)
        inv_regs = [i for i in range(m.n_regs) if not (w.log_regs[:, :, i] != hon.log_regs[:, :, i]).any()]
        if cheat == "skip_lin":
            trig = np.zeros(len(ch_env), bool) if not y_dst else np.ones(len(ch_env), bool)
        elif cheat == "no_regime_flip":
            trig = np.full(len(ch_env), bool(m.regime_period) and y_dst)
        elif cheat == "stoch_swap":
            trig = hon.kicks > 0
        else:
            trig = hon.unpaid > 0
        hsample = np.nonzero(reg_env)[0][:N_HASH]
        hash_blind = sum(hash_log(w.log_regs[:, e], w.log_charge[:, e], w.log_alive[:, e], spec.T)
                         == hash_log(hon.log_regs[:, e], hon.log_charge[:, e], hon.log_alive[:, e], spec.T)
                         for e in hsample)
        rows.append({"status": "cheat", "kind": "cheat_world", "cheat": cheat, **base,
                     "fitness_gate_passes": bool((f == f_hon).all()),
                     "fitness_diff_genomes": int((f != f_hon).sum()),
                     "fitness_higher_genomes": int((f > f_hon).sum()),
                     "fitness_mean_delta": round(float((f - f_hon).mean()), 3),
                     "charge_diff_envs": int(ch_env.sum()), "reg_diff_envs": int(reg_env.sum()),
                     "invariant_regs": inv_regs,
                     "untriggered_envs": int((~trig).sum()),
                     "untriggered_but_charge_diff": int((~trig & ch_env).sum()),
                     "hash_sampled": int(len(hsample)), "hash_blind": int(hash_blind),
                     "wall_s": round(time.perf_counter() - t0, 2)})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args(argv)
    seeds = range(1, 4) if args.quick else range(1, 41)
    tag = EXP + ("-quick" if args.quick else "")
    t0 = time.perf_counter()
    rows = []
    with RowWriter(ROOT / "ledger" / "rows" / "D" / f"{tag}.jsonl", tag) as w:
        with ProcessPoolExecutor(max_workers=2) as ex:
            for rs in ex.map(world_rows, seeds):
                for r in rs:
                    if args.quick and r["status"] != "aborted":
                        r = dict(r, status="dev")
                    w.write(r)
                    rows.append(r)

        ok = [r for r in rows if r["kind"] == "cheat_world"]
        sk = {r["gen_seed"]: r for r in ok if r["cheat"] == "skip_lin"}
        agree = [(r["fitness_gate_passes"] == (not r["yield_in_dsts"])) for r in sk.values()]
        rng = np.random.default_rng(12345)
        passes = np.array([r["fitness_gate_passes"] for r in sk.values()])
        label = np.array([not r["yield_in_dsts"] for r in sk.values()])
        null = [int((passes == rng.permutation(label)).sum()) for _ in range(100)]
        inv_match = [set(r["invariant_regs"]) == set(range(r["n_regs"])) - set(r["lin_dsts"]) for r in sk.values()]
        e4 = {g: (not sk[g]["yield_in_dsts"]) for g in (1, 2, 3, 4, 5) if g in sk}
        checks = {
            "H1_skip_lin_gate_iff_yield_not_dst": all(agree),
            "H1_if_direction_theorem": all(r["fitness_gate_passes"] for r in sk.values() if not r["yield_in_dsts"]),
            "H2_e4_worlds_124_not_dst_35_dst": e4 == {1: True, 2: True, 3: False, 4: True, 5: False} if len(e4) == 5
            else None,
            "H3_w1_skip_lin_fitness_equal": sk[1]["fitness_diff_genomes"] == 0 if 1 in sk else None,
            "H4_invariant_regs_eq_non_dsts_ge38": sum(inv_match) >= 0.95 * len(inv_match),
            "H5_untriggered_envs_charge_equal": all(r["untriggered_but_charge_diff"] == 0 for r in ok),
            "C_honest_repeat_zero": all(r["fitness_diff_genomes"] == 0 and r["reg_diff_envs"] == 0
                                        for r in rows if r["kind"] == "honest_repeat"),
            "C_trace_hash_never_blind": all(r["hash_blind"] == 0 for r in ok),
            "C_label_shuffle_below_real_ge95": sum(x < sum(agree) for x in null) >= 95,
        }
        gate = {c: "%d/%d" % (sum(r["fitness_gate_passes"] for r in ok if r["cheat"] == c),
                              sum(1 for r in ok if r["cheat"] == c)) for c in CHEATS}
        summary = {"exp": tag, "checks": checks, "worlds": len(sk), "aborted": sum(r["status"] == "aborted" for r in rows),
                   "skip_lin_agreement": "%d/%d" % (sum(agree), len(agree)),
                   "label_shuffle_null_max": max(null) if null else None,
                   "invariant_regs_match": "%d/%d" % (sum(inv_match), len(inv_match)),
                   "fitness_gate_pass_worlds": gate,
                   "skip_lin_disagreements": [g for g, r in sk.items() if r["fitness_gate_passes"] == r["yield_in_dsts"]],
                   "wall_s": round(time.perf_counter() - t0, 1)}
        w.write({"status": "dev" if args.quick else "record", "kind": "summary", **summary})
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
