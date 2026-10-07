"""B18 -- is the composition wall a property of FLAT programs? First world run of the Proteus GRAPH organism.

B03..B14': in the flat v0 VM, every reachable memory mechanism is a single module (one latch, one store, one guard,
one shift chain) and two genuinely stored values are unreachable under timing jitter (B08J L4 0/8). Proteus's graph
organism (proteus/graph, GRAPH_ORGANISM_V1.md: nodes + data/control edges, ROUTE and CALL/RETURN, no positional
jumps; "NO world has run it") changes ARCHITECTURE while keeping the world ABI. B18 runs it through the SAME
Evolution loop (archaeon.wse.evolve: tournament, elitism, CRN, E0) with graph-native pieces swapped in:
  player/meter   proteus.graph.handover.player_for / meter_for  (evaluator below: per-ask reward, v0-shaped dict)
  variation      proteus.graph.handover.descend_for            (graph_grammar.v1, 13 connectivity operators)
  gen 0          proteus.graph.generate.generate(DEFAULT_FOUNDRY_MANIFEST, seed per cell, n=N)
Worlds: the jittered ladder (B08J) rungs L1, L3, L2, L4 and L6 (W2_K2). Controls (graph witness organisms from
proteus/graph/witness.py) are scored on every rung first.

PREDICTION (before running): graph organisms reach L1/L3 (>= 2/4 each); L4 0/4 as in v0 (the wall is about
composition under selection, not about positional jumps). A graph L4 solve >= 1/4 would make the wall a
property of flat programs.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.graph import generate as G1
from proteus.graph import handover as H
from proteus.graph import witness as W

import archaeon.beta.b08_primitive_ladder as B
from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, REGIMES, TARGET
from archaeon.beta.b08j_jittered_ladder import jittered
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results"
SOLVED = 0.90
RUNGS = ("L1_one", "L3_last", "L2_first", "L4_order", "L6_w2k2")


def graph_evaluate(manifest, episodes, intervention=None, rng_seed=0, reward_mode="per_ask"):
    """Per-ask reward for a graph organism on WSE episodes; returns the keys Evolution reads (v0-shaped)."""
    player = H.player_for(manifest)
    meter = H.meter_for(manifest)
    correct = asks = ep_all = 0
    per_c, per_n = [], []
    for ei, ep in enumerate(episodes):
        st = player.fresh_state()
        rng = SplitMix64(seed_from("wse.vmrng", rng_seed, ei))
        epc = epa = 0
        for ti, words in enumerate(ep.ticks):
            outs, status = player.run_tick(st, [words], 1, rng, meter=meter)
            if ti in ep.expected:
                k = sum(1 for t in ep.expected if t < ti)
                while len(per_n) <= k:
                    per_n.append(0); per_c.append(0)
                per_n[k] += 1; asks += 1; epa += 1
                if outs[0] and outs[0][0] == ep.expected[ti]:
                    correct += 1; epc += 1; per_c[k] += 1
        if epa and epc == epa:
            ep_all += 1
    md = meter.as_dict(manifest)
    md.setdefault("persistent_state_words", 0)
    n = max(1, len(episodes))
    r = correct / max(1, asks)
    return {"reward": r if reward_mode != "episode" else ep_all / n, "reward_per_ask": r, "reward_episode": ep_all / n,
            "per_ask_reward": [round(c / max(1, k), 4) for c, k in zip(per_c, per_n)], "meter": md,
            "ops_per_episode": md["ops"] / n, "persist": "graph", "tick_budget": manifest.get("tick_budget", 0),
            "tape_words": manifest.get("state_words", 0), "n_regs": len(manifest["nodes"]), "code_writable": False,
            "statuses": {}, "yield_share": 0.0, "tape_occupancy_max": 0, "tape_writes_per_episode": 0,
            "intervention": None, "interventions_applied": 0, "asks": asks, "correct": correct}


def _shares_tolerant(scored):
    out = {}
    for _, org, _ in scored:
        k = org["manifest"].get("persist", "graph")
        out[k] = out.get(k, 0) + 1
    n = max(1, len(scored))
    return {k: round(v / n, 4) for k, v in out.items()}


def install():
    EV.evaluate = graph_evaluate
    EV._shares = _shares_tolerant
    B.eps_for = jittered


def wse_indexed_graph():
    """WSE-format positive control (one channel, ticks [kind, tag, value...]): state[tag] = value on PUT,
    out state[tag] on ASK. Built from proteus/graph/witness.py's keyed design, rewired for the WSE grammar."""
    from proteus.graph.affordances import KIND_OF as K
    from proteus.graph.vm import SCHEMA, canonicalize
    n = lambda kind, *p: {"kind": K[kind], "params": list(p), "persist": False}   # noqa: E731
    nodes = [n("CONST", 0), n("IN"), n("IN"), n("CONST", 1), n("EQ"), n("ROUTE"), n("IN"), n("ST"), n("HALT"),
             n("LD"), n("OUT"), n("HALT")]
    data = [[0, 1, 0], [0, 2, 0], [1, 4, 0], [3, 4, 1], [4, 5, 0], [0, 6, 0], [2, 7, 0], [6, 7, 1], [2, 9, 0],
            [9, 10, 0], [0, 10, 1]]
    control = [[0, 0, 1], [1, 0, 2], [2, 0, 3], [3, 0, 4], [4, 0, 5], [5, 0, 6], [5, 1, 9], [6, 0, 7], [7, 0, 8],
               [9, 0, 10], [10, 0, 11]]
    return canonicalize({"schema_version": SCHEMA, "nodes": nodes, "data_edges": data, "control_edges": control,
                         "entry": 0, "state_words": 1024, "tick_budget": 32, "out_cap": 1, "call_depth_max": 0,
                         "persist_state": True})


def controls():
    install()
    orgs = {"wse_indexed_graph": wse_indexed_graph(), "witness_keyed": W.keyed_memory_manifest(), "witness_one_value": W.one_value_manifest(),
            "witness_echo": W.echo_manifest(), "witness_inert": W.inert_manifest()}
    return {k: {r: round(graph_evaluate(m, B.eps_for(r, "heldout", 7, 48), rng_seed=7)["reward"], 4) for r in RUNGS}
            for k, m in orgs.items()}


def cell(job):
    install()
    rung, seed, G_, N = job["rung"], job["seed"], job["G"], job["N"]
    t0 = time.time()
    pop = G1.generate(dict(G1.DEFAULT_FOUNDRY_MANIFEST, seed=seed, n=N))
    prov = {"fill": "proteus.graph.generate", "seed": seed, "n": N, "verified_common": True}
    ev = EV.Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=16, branch="b18", init_pop=pop,
                      gen0_provenance=prov, descend_fn=H.descend_for)
    ho = B.eps_for(rung, "heldout", seed, 48)
    solved, best = None, []
    for g in range(G_):
        row = ev.evaluate_generation(episodes=B.eps_for(rung, "train", g * 100003 + seed, 16), last=(g == G_ - 1))
        best.append(round(row["best_reward"], 4))
        if row["best_reward"] >= SOLVED and graph_evaluate(ev.scored[0][1]["manifest"], ho, rng_seed=7)["reward"] >= SOLVED:
            solved = g
            break
        if g < G_ - 1:
            ev.reproduce()
    elite = ev.scored[0][1]["manifest"]
    return {"rung": rung, "seed": seed, "N": N, "solved_gen": solved, "max_train": max(best),
            "final_heldout": round(graph_evaluate(elite, ho, rng_seed=7)["reward"], 4), "elite_nodes": len(elite["nodes"]),
            "elite_manifest": elite, "wall_s": round(time.time() - t0, 1)}


def main(argv):
    OUT.mkdir(exist_ok=True)
    G_ = int(argv[0]) if argv else 300
    workers = int(argv[1]) if len(argv) > 1 else 2
    seeds = int(argv[2]) if len(argv) > 2 else 4
    ctl = controls(); print("controls", json.dumps(ctl), flush=True)
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(cell, {"rung": r, "seed": 1801 + s, "G": G_, "N": 200}): (r, s) for s in range(seeds) for r in RUNGS}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                rr, s = futs[f]; r = {"rung": rr, "seed": 1801 + s, "solved_gen": None, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B18_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {r: sum(x["rung"] == r and x["solved_gen"] is not None for x in rows) for r in RUNGS}
    print(json.dumps(summ), flush=True)
    (OUT / "B18_result.json").write_text(json.dumps({"probe": "B18", "G": G_, "controls": ctl, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
