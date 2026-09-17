"""File the W2 receipt from committed rows. Run AFTER the rows are pushed (bus.receipt guards it).

usage: python -m primordial.nv.warp.receipt_w2 --git <sha on origin> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "W"
MAIN = ROWS / "W2-warp-numba-crossover.jsonl"
ORACLE = ["W1-warp-world-oracle-cpu", "W1-warp-world-oracle-cuda", "W1-warp-world-oracle-cuda-tick1"]
CHEAT = ["W1-warp-world-oracle-cpu-cheat_skip_lin", "W1-warp-world-oracle-cuda-cheat_skip_lin"]
CLAIM = ("W2 (predicate bus 1789426347225-0, posted before timing): lane B's open-loop world step as one Warp "
         "kernel, timed against soup/b1/nb_world.run_all (1 numba thread, W's budget) on B1 episodes, worlds 1-5 x "
         "n_envs 1..65536, compile excluded, median of 5 alternating reps, inside bus.gpu_lease. H1 warp_cuda beats "
         "numba at some n <= 4096 in >= 4/5 worlds. H2 warp_cpu wall within 2x of numba at n >= 1024 in >= 4/5 "
         "worlds. Gate per cell before a time counts: wforge trace-hash sample of the timed kernel, done_tick, "
         "charge + regs across forms. Exactness (W1): trace hash + final charge == wforge on 40 worlds x 12 envs, "
         "cpu and cuda; skip_lin must fail.")


def _jsonl(p):
    return [json.loads(x) for x in open(p, encoding="utf-8")] if p.exists() else []


def _oracle(name):
    rows = _jsonl(ROWS / f"{name}.jsonl")
    ok = sum(r["trace_eq"] and r["charge_eq"] and r["ticks_eq"] for r in rows)
    worlds_bad = len({r["world_seed"] for r in rows if not (r["trace_eq"] and r["charge_eq"] and r["ticks_eq"])})
    return ok, len(rows), worlds_bad


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    cells = [r for r in _jsonl(MAIN) if "gate_ok" in r]
    valid = [r for r in cells if r["speed_status"] == "VALID"]
    worlds = sorted({r["world_seed"] for r in cells})
    exact = {n: _oracle(n) for n in ORACLE}
    cheat = {n: _oracle(n) for n in CHEAT}
    exact_ok = all(ok == tot > 0 for ok, tot, _ in exact.values())
    cheat_ok = all(ok == 0 and tot > 0 and wb == 40 for ok, tot, wb in cheat.values())
    gate_ok = bool(cells) and all(r["gate_ok"] for r in cells)
    lease_ok = all(r["lease"] and r["lease_lost"] is False for r in cells)

    def world_h1(g):
        v = [r for r in valid if r["world_seed"] == g and r["n_envs"] <= 4096]
        if not v:
            return None                                   # no VALID cell: not eligible
        return any(r["median_s"]["warp_cuda"] < r["median_s"]["numba"] for r in v)

    def world_h2(g):
        v = [r for r in valid if r["world_seed"] == g and r["n_envs"] >= 1024]
        if not v:
            return None
        return all(r["median_s"]["warp_cpu"] <= 2 * r["median_s"]["numba"] for r in v)

    h1 = {g: world_h1(g) for g in worlds}
    h2 = {g: world_h2(g) for g in worlds}
    h1_pass = sum(bool(x) for x in h1.values()) >= 4
    h2_pass = sum(bool(x) for x in h2.values()) >= 4
    controls_ok = exact_ok and cheat_ok and gate_ok and lease_ok and len(cells) == 45
    status = "INDETERMINATE" if not controls_ok else ("PASS" if h1_pass and h2_pass else "FAIL")
    crossover = {}
    for g in worlds:
        v = sorted((r for r in valid if r["world_seed"] == g and r["median_s"]["warp_cuda"] < r["median_s"]["numba"]),
                   key=lambda r: r["n_envs"])
        crossover[f"w{g}"] = v[0]["n_envs"] if v else None
    per_cell = {f"w{r['world_seed']}_n{r['n_envs']}": {
        "Msteps_per_s": {k: round((r[f"{k}_slot_steps_per_s"] or 0) / 1e6, 2) for k in ("numba", "warp_cpu", "warp_cuda")},
        "h2d_ms": round((r["h2d_s"] or 0) * 1e3, 3), "speed_status": r["speed_status"]} for r in cells}
    rec = {
        "lane": "W", "exp_id": "W2-warp-numba-crossover", "claim": CLAIM, "status": status,
        "engineering": {
            "per_cell": per_cell,
            "first_n_cuda_beats_numba_valid": crossover,
            "peak_speedup_cuda_vs_numba_valid": round(max(r["speedup_cuda_vs_numba"] for r in valid), 1),
            "cpu_vs_numba_range_n_ge_1024_valid": [round(min(r["speedup_cpu_vs_numba"] for r in valid if r["n_envs"] >= 1024), 2),
                                                   round(max(r["speedup_cpu_vs_numba"] for r in valid if r["n_envs"] >= 1024), 2)],
            "cells_indeterminate": len(cells) - len(valid),
            "bounds": ("numba at 1 thread (B6 used 3); B1 random-action episodes die at ~20-27 ticks; H2D of the action "
                       "tensor is outside the timed wall (h2d_ms); cuda throughput falls 16384->65536 in w1/w4, unexplained"),
        },
        "science": {
            "hypothesis_scoring": {
                "h1_cuda_beats_numba_n_le_4096_ge_4_of_5": f"{'CONFIRMED' if h1_pass else 'WRONG'} {json.dumps(h1)}",
                "h2_cpu_within_2x_n_ge_1024_ge_4_of_5": f"{'CONFIRMED' if h2_pass else 'WRONG'} {json.dumps(h2)}",
            },
            "exactness_w1": json.dumps({n: f"{ok}/{tot}" for n, (ok, tot, _) in exact.items()}),
            "credit": "world semantics are lane B's B1 (nb_world.run_all, proved == wforge in B1); wforge is read-only",
        },
        "controls": {
            "cheat": "skip_lin Warp kernel vs wforge: " + json.dumps({n: f"{ok}/{tot} exact, {wb}/40 worlds failing"
                                                                    for n, (ok, tot, wb) in cheat.items()})
                     + "; crossover gate v1 (charge-only) passed skip_lin at w4 n=64, v2 (hash sample) catches it (test)",
            "gate": f"{sum(r['gate_ok'] for r in cells)}/{len(cells)} cells",
            "lease": f"held and not lost in {sum(bool(r['lease'] and r['lease_lost'] is False) for r in cells)}/{len(cells)} cells",
        },
        "rows": ("primordial/ledger/rows/W/W2-warp-numba-crossover.jsonl + "
                 + " + ".join(f"primordial/ledger/rows/W/{n}.jsonl" for n in ORACLE + CHEAT)),
        "git": a.git,
    }
    print(json.dumps({k: rec[k] for k in ("status", "science", "controls")}, indent=1))
    print(json.dumps({k: v for k, v in rec["engineering"].items() if k != "per_cell"}, indent=1))
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
