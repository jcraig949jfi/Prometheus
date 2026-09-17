"""Build the B1 receipt from committed rows and file it on the bus.

usage: python -m primordial.soup.b1.receipt [--dry] --git <sha>
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "B"
FORMS = ("np", "nb", "lua1", "luak", "fk")
CLAIM = ("B1 crossover crucible: wforge Encounter semantics in numpy-batched, numba, Redis Lua "
         "(1 EVALSHA/tick and k ticks server-side) and FalkorDB Cypher; each form is the SAME world iff "
         "every sampled episode's sha256 trace hash equals wforge's (zero tolerance). Predicted: numba "
         "fastest at every n_envs; numpy passes wforge by ~16 envs; Lua/tick RTT-bound; Lua k-ticks beats "
         "numpy only for small n; FalkorDB slowest at all n. Cheat: skipping lin_ops must fail the oracle.")


def _jsonl(p):
    return [json.loads(x) for x in open(p, encoding="utf-8")] if p.exists() else []


def oracle_counts(name):
    rows = _jsonl(ROWS / f"B1-oracle-{name}.jsonl")
    return {"episodes": len(rows), "trace_eq": sum(r["trace_eq"] for r in rows)}


def build(git: str) -> tuple[dict, dict]:
    oracle = {f: oracle_counts(f) for f in FORMS}
    cheats = {f: oracle_counts(f"{f}-cheat_skip_lin") for f in FORMS}
    cheats = {f: c for f, c in cheats.items() if c["episodes"]}
    bench = _jsonl(ROWS / "B1-bench-v0.jsonl")
    prod = _jsonl(ROWS / "B1-producers-v0.jsonl")
    verified = [f for f in FORMS if oracle[f]["episodes"] and oracle[f]["trace_eq"] == oracle[f]["episodes"]]

    best = {}
    for r in bench:
        if r["form"] == "ref" or r["form"] in verified:
            k = (r["form"], r["world_seed"])
            if r["steps_per_s"] and r["steps_per_s"] > best.get(k, {}).get("steps_per_s", 0):
                best[k] = r
    surface = {}
    for r in bench:
        surface.setdefault(f"w{r['world_seed']}", {}).setdefault(r["form"], {})[str(r["n_envs"])] = \
            round(r["steps_per_s"])
    winners = {}
    for w, forms in surface.items():
        for n in sorted({int(n) for f in forms.values() for n in f}):
            cand = {f: v[str(n)] for f, v in forms.items() if str(n) in v}
            winners.setdefault(w, {})[str(n)] = max(cand, key=cand.get)
    top = max((r for r in bench if r["form"] in verified), key=lambda r: r["steps_per_s"])
    prod_ceiling = {}
    for r in prod:
        k = f"{r['form']}_n{r['n_envs']}"
        prod_ceiling.setdefault(k, {})[str(r["producers"])] = \
            (round(r["agg_steps_per_s"]) if r.get("status", "OK") == "OK" else f"FAIL({len(r['errors'])})")

    cheat_ok = all(c["trace_eq"] == 0 for c in cheats.values())
    all_pass = len(verified) == len(FORMS)
    rec = {
        "lane": "B", "exp_id": "B1-crossover-crucible", "claim": CLAIM,
        "status": "PASS" if (all_pass and cheat_ok) else "FAIL",
        "engineering": {
            "steps_per_s_best_verified": round(top["steps_per_s"]),
            "best_form": top["form"], "best_at_n_envs": top["n_envs"], "best_world": top["world_id"],
            "numba_threads": 3,
            "surface_steps_per_s": surface,
            "winner_by_n_envs": winners,
            "producers_agg_steps_per_s": prod_ceiling,
            "host_cpu_pct_range": [min(r["host_cpu_pct_before"] for r in bench),
                                   max(r["host_cpu_pct_before"] for r in bench)],
            "caveats": ["steps = sum of min(episode length, ticks run); np/lua/fk still pay for "
                        "absorbed envs, truncated runs (lua1, fk at large n) pay less of that",
                        "fk receives the stochastic-kick schedule as an exogenous per-tick parameter "
                        "(state-independent draws; client work is timed)",
                        "ref is the wforge Encounter, single thread, capped at 64 episodes",
                        "luak n=4096 P=16 FAILED: every worker raised TimeoutError reading from socket "
                        "(redis-py socket_timeout None; cause not established). The first attempt hung the "
                        "parent and was killed, producing no row; the rerun wrote the FAIL row",
                        "numba: 3 threads; the n=1 cells include prange dispatch overhead"],
        },
        "science": {
            "oracle_trace_eq": oracle,
            "semantic_findings": [
                "wforge stoch kick `regs[below(n)] = below(M)` evaluates RHS first: value drawn before index "
                "(all three first-draft forms had it backwards; oracle caught it)",
                "wforge charges 0 for an unaffordable action but still applies its writes (200/200 worlds; "
                "packet PACKET_wforge_unaffordable_action.md)",
                "FalkorDB evaluates a division inside a false CASE branch (Division by zero)",
            ],
            "forms_verified": verified,
            "hypothesis_scoring": {
                "numba_fastest_every_n": "CONFIRMED (every cell)",
                "numpy_passes_wforge_by_16": "WRONG by one octave: crossover between 16 and 64 in both worlds",
                "numpy_beats_lua1_all_n": "CONFIRMED",
                "lua1_rtt_bound_small_n": "PARTLY: ~1.4-1.7 ms per call at n=1, 4-5x the 0.33 ms PING RTT; "
                                          "script overhead dominates",
                "luak_beats_numpy_only_small_n": "CONFIRMED (n<=16)",
                "falkordb_slowest_all_n": "CONFIRMED (every cell; narrowest w0 n=4096, 40k vs lua1 43k)",
                "redis_server_ceiling": "aggregate ~190k steps/s across 1..16 producers; lua1 converges to it",
            },
        },
        "controls": {
            "cheat": "skip_lin (transition ops dropped) trace_eq: " + json.dumps(cheats),
            "positive": "probe_unaffordable control: affordable action moved AND paid 200/200",
        },
        "rows": "primordial/ledger/rows/B/B1-*.jsonl",
        "git": git,
    }
    board = {"steps_per_s_verified": top["steps_per_s"]}
    return rec, board


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    rec, board = build(a.git)
    print(json.dumps({k: v for k, v in rec.items() if k != "engineering"}, indent=1))
    print(json.dumps({k: rec["engineering"][k] for k in
                      ("steps_per_s_best_verified", "best_form", "best_at_n_envs", "winner_by_n_envs",
                       "producers_agg_steps_per_s")}, indent=1))
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec, board=board))


if __name__ == "__main__":
    main()
