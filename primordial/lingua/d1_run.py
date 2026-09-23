"""D1 record run: learner grid, bits-vs-yield front, scramble probe, Lua channel audit, bench.

usage: PM_LANE=D python -m primordial.lingua.d1_run [--quick]
Rows -> primordial/ledger/rows/D/<exp>.jsonl; elites + summary -> PM_D_HOT (never F:).
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import redis

from primordial.lingua import signal as S
from primordial.lingua.channel import URL, LuaChannel

EXP = "D1-metered-channel"
ROOT = pathlib.Path(__file__).resolve().parents[1]
HOT = pathlib.Path(os.environ.get("PM_D_HOT", "C:/Users/jcrai/lab/pm-data/D"))
ALPHAS, BETAS, DELTA = (0.0, 0.1, 0.3, 0.6, 1.5), (0.0, 0.01), 1.0
AUDIT = {"alpha_int": 2, "y_int": 3, "start": 8}
T = 64
PROBE_SEEDS = 10_000_000 + np.arange(512)     # held out from the learner pool (seeds < 65536)
AUDIT_SEEDS = 20_000_000 + np.arange(256)

_POOL = None


def _pool():
    global _POOL
    if _POOL is None:
        _POOL = S.r_stream(np.arange(1 << 16), T).astype(np.uint8)
    return _POOL


def cell(args):
    alpha, beta, run_seed, gens = args
    t0 = time.perf_counter()
    # the search seed depends on run_seed only, never on the cell
    k, enc, dec = S.learn(alpha, beta, DELTA, seed=1000 * run_seed + 17, pool=_pool(), gens=gens)
    return {"alpha": alpha, "beta": beta, "run_seed": run_seed, "gens": gens,
            "wall_s": round(time.perf_counter() - t0, 2), "k": k, "enc": enc.tolist(), "dec": dec.tolist()}


def describe(k, enc, dec, alpha, beta, rng, leak=False) -> dict:
    enc, dec = np.asarray(enc), np.asarray(dec)
    c, y, bits, ent = S.evaluate(np.array([k]), enc[None], dec[None], np.arange(256), alpha, beta, DELTA)
    m_opt, c_opt = S.analytic_optimum(alpha, beta, DELTA)
    probe = S.scramble_probe(k, enc, dec, PROBE_SEEDS, T, rng, leak=leak)
    d = {"k": int(k), "entries": int(ent[0]), "bits_per_tick": float(bits[0]), "yield": float(y[0]),
         "cost": float(c[0]), "opt_m": m_opt, "opt_cost": c_opt, "cost_gap": float(c[0]) - c_opt,
         "mi_bucket": S.mi_bucket(enc), "mi_low": S.mi_low(enc), "probe": probe}
    if leak:   # the leaker's yield is what the probe measured in the world, not its code's
        d["yield"], d["cost"] = probe["y"], alpha * d["bits_per_tick"] + beta * d["entries"] + DELTA * (1 - probe["y"])
    return d


def audit(r, label, k, enc, dec, leak=False) -> list[dict]:
    n, a, y, s0 = len(AUDIT_SEEDS), AUDIT["alpha_int"], AUDIT["y_int"], AUDIT["start"]
    ref_ch = S.NpChannel(n, a, s0)
    ref = S.run_world(k, enc, dec, AUDIT_SEEDS, T, ref_ch, y, leak)
    rows = []
    for cheat in ("", "free_unaffordable", "undercharge"):
        ch = LuaChannel(r, f"d1:{label}:{cheat or 'honest'}", n, a, s0, cheat)
        got = S.run_world(k, enc, dec, AUDIT_SEEDS, T, ch, y, leak)
        ch.cleanup()
        exercised = {"": 0, "free_unaffordable": ref_ch.unaffordable,
                     "undercharge": ref_ch.delivered_sends}[cheat]
        mism = sum(p != q for p, q in zip(ref["hashes"], got["hashes"]))
        viol = S.conservation_violations(got, s0, a, y)
        rows.append({"kind": "audit", "genome": label, "cheat": cheat or "honest", "n_envs": n, "ticks": T,
                     "hash_mismatch": int(mism), "conservation_violations": viol,
                     "ref_conservation_violations": S.conservation_violations(ref, s0, a, y),
                     "exercised_sends": int(exercised), "detected": bool(mism or viol)})
    return rows


def host_cpu():
    try:
        import psutil
        return psutil.cpu_percent(interval=0.5)
    except Exception:
        return None


def bench(r) -> list[dict]:
    out = []
    for n in (1, 64, 1024, 4096):
        rng = np.random.default_rng(n)
        bits, syms, cred = rng.integers(0, 4, (T, n)), rng.integers(0, 8, (T, n)), rng.integers(0, 3, (T, n))
        for form in ("numpy", "lua"):
            ch = S.NpChannel(n, 2, 1000) if form == "numpy" else LuaChannel(r, f"d1:bench:{n}", n, 2, 1000)
            cpu = host_cpu()
            t0 = time.perf_counter()
            for t in range(T):
                ch.tick(t, bits[t], syms[t], cred[t])
            dt = time.perf_counter() - t0
            if form == "lua":
                ch.cleanup()
            out.append({"kind": "bench", "form": form, "n_envs": n, "ticks": T, "ticks_per_s": T / dt,
                        "msgs_per_s": T * n / dt, "host_cpu_pct_before": cpu})
    return out


def front(points: list[dict]) -> list[dict]:
    def dom(q, p):
        return (q["bits_per_tick"] <= p["bits_per_tick"] and q["yield"] >= p["yield"]
                and (q["bits_per_tick"] < p["bits_per_tick"] or q["yield"] > p["yield"]))
    return [p for p in points if not any(dom(q, p) for q in points)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--gens", type=int, default=2000)
    args = ap.parse_args(argv)
    gens, seeds = (200, (0,)) if args.quick else (args.gens, (0, 1, 2))
    tag = EXP + ("-quick" if args.quick else "")
    HOT.mkdir(parents=True, exist_ok=True)
    r = redis.Redis.from_url(URL)
    t_start = time.perf_counter()

    jobs = [(a, b, s, gens) for s in seeds for a in ALPHAS for b in BETAS]
    with ProcessPoolExecutor(max_workers=3) as ex:
        elites = list(ex.map(cell, jobs))
    (HOT / f"{tag}.elites.json").write_text(json.dumps(elites), encoding="utf-8")

    rng = np.random.default_rng(99)
    rows = []
    for e in elites:
        rows.append({"kind": "elite", "alpha": e["alpha"], "beta": e["beta"], "run_seed": e["run_seed"],
                     "gens": e["gens"], "wall_s": e["wall_s"],
                     **describe(e["k"], e["enc"], e["dec"], e["alpha"], e["beta"], rng)})
    for m in range(1, 9):
        rows.append({"kind": "hand_code", "m": m, **describe(*S.hand_code(m), 0.0, 0.0, rng)})
    leak = {"kind": "leak_cheat", **describe(*S.hand_code(1), 0.0, 0.0, rng, leak=True)}
    rows.append(leak)

    for e in elites:
        if e["run_seed"] == 0:
            rows += audit(r, f"a{e['alpha']}-b{e['beta']}", e["k"], e["enc"], e["dec"])
    for m in (8, 4, 2, 1):
        rows += audit(r, f"hand{m}", *S.hand_code(m))
    rows += audit(r, "leak", *S.hand_code(1), leak=True)
    rows += bench(r)

    el = [x for x in rows if x["kind"] == "elite"]
    honest_pts = [x for x in rows if x["kind"] in ("elite", "hand_code") and not x["probe"]["flagged_leak"]]
    all_pts = honest_pts + [leak]
    fr = front(honest_pts)
    fr_unfiltered = front(all_pts)
    au = [x for x in rows if x["kind"] == "audit"]
    honest_au = [x for x in au if x["cheat"] == "honest"]
    cheat_au = [x for x in au if x["cheat"] != "honest"]
    elig = [x for x in rows if x["kind"] in ("elite", "hand_code") and x["probe"]["eligible"]]

    y0 = [x["yield"] for x in el if x["alpha"] == 0.0]
    y15 = [x["yield"] for x in el if x["alpha"] == 1.5]
    checks = {
        "P1_mi_bucket_alpha0_beta0": all(x["mi_bucket"] >= 2.5 for x in el if x["alpha"] == 0 and x["beta"] == 0),
        "P2a_k_le_3_alpha_pos": all(x["k"] <= 3 for x in el if x["alpha"] > 0),
        "P2b_mi_low_le_0.1_beta_pos": all(x["mi_low"] <= 0.1 for x in el if x["beta"] > 0),
        "P3_silence_at_alpha1.5": all(abs(x["yield"] - S.CHANCE) <= 0.02 and x["bits_per_tick"] == 0
                                      for x in el if x["alpha"] == 1.5),
        "P3_alpha0_vs_alpha1.5_differ": bool(min(y0) - max(y15) > 0.5),
        "P4_honest_norm_drop_ge_0.4": all(x["probe"]["norm_drop"] >= 0.4 for x in elig),
        "P4_leak_flagged": leak["probe"]["flagged_leak"],
        "P4_leak_would_dominate_unfiltered_front": any(p["kind"] == "leak_cheat" for p in fr_unfiltered),
        "P5_honest_lua_eq_numpy": all(x["hash_mismatch"] == 0 and x["conservation_violations"] == 0
                                      and x["ref_conservation_violations"] == 0 for x in honest_au),
        "P5_cheats_detected_when_exercised": all(x["detected"] for x in cheat_au if x["exercised_sends"] > 0),
        "P6_cost_gap_le_0.02": all(x["cost_gap"] <= 0.02 for x in el),
    }
    summary = {
        "exp": tag, "checks": checks,
        "cheat_audits_exercised": sum(1 for x in cheat_au if x["exercised_sends"] > 0),
        "cheat_audits_detected": sum(1 for x in cheat_au if x["exercised_sends"] > 0 and x["detected"]),
        "cheat_false_alarm_unexercised": sum(1 for x in cheat_au if x["exercised_sends"] == 0 and x["detected"]),
        "front": [{k: p.get(k) for k in ("kind", "alpha", "beta", "run_seed", "m", "k", "bits_per_tick", "yield")}
                  for p in fr],
        "max_cost_gap": max(x["cost_gap"] for x in el),
        "min_honest_norm_drop": min(x["probe"]["norm_drop"] for x in elig),
        "leak_norm_drop": leak["probe"]["norm_drop"],
        "wall_s": round(time.perf_counter() - t_start, 1),
    }
    rows_path = ROOT / "ledger" / "rows" / "D" / f"{tag}.jsonl"
    rows_path.parent.mkdir(parents=True, exist_ok=True)
    with open(rows_path, "w", encoding="utf-8", newline="\n") as fh:
        for x in rows:
            fh.write(json.dumps(x, sort_keys=True) + "\n")
        fh.write(json.dumps({"kind": "summary", **summary}, sort_keys=True) + "\n")
    (HOT / f"{tag}.summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
