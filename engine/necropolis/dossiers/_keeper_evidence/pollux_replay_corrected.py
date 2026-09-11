#!/usr/bin/env python3
"""
Corrected deterministic replay of the Pollux v0.5 -> v0.6 run (Rhadamanthus as Keeper, 2026-09-11).

Both prior replays (pollux_rescan.py Q4, k=0; cleric_census_fit.py S2, k=95) remove a settled pair
from the active rotation unconditionally. daemon.py _promote_settled_replace (lines 330-338) removes
it ONLY when CANDIDATE_POOL still has a replacement; on pool exhaustion it returns None and the
settled pair keeps rotating. This script replays with the daemon's semantics and a v0.5 prefix of k
ticks (plain round-robin over SEED_PAIRS, no settle), using today's per-pair verdicts, and reports
the k values whose census matches the second channel exactly (pollux_settling_query_result.json).
No LLM, no DB; deterministic. Usage: python pollux_replay_corrected.py [--out result.json]
"""
import json, os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 4))
spec = importlib.util.spec_from_file_location("pollux_daemon", os.path.join(REPO, "charon", "agents", "pollux", "daemon.py"))
d = importlib.util.module_from_spec(spec)
sys.path.insert(0, REPO)
spec.loader.exec_module(d)

TODAY = {  # verdict per pair, pollux_rescan_result.json Q2 (deterministic on rerun) == second channel
    "deg10_vs_deg12": "REJECTED", "deg14_vs_deg16": "PROMOTED", "salem_vs_pisot": "PROMOTED",
    "smyth_extremal_vs_rest": "REJECTED", "deg18_vs_deg20": "UNVERIFIED", "even_deg_vs_odd_deg": "UNVERIFIED",
    "small_deg_vs_large_deg": "PROMOTED", "narrow_band_1.10_1.20_vs_1.30_1.50": "REJECTED",
    "lehmer_witness_neighborhood": "UNVERIFIED"}
TOTAL = 286
CHANNEL = {"deg10_vs_deg12": 17, "deg14_vs_deg16": 17, "salem_vs_pisot": 17, "smyth_extremal_vs_rest": 16,
           "even_deg_vs_odd_deg": 56, "small_deg_vs_large_deg": 5, "narrow_band_1.10_1.20_vs_1.30_1.50": 53,
           "deg18_vs_deg20": 54, "lehmer_witness_neighborhood": 51}


def simulate(k, remove_on_exhaustion):
    seed = [p["name"] for p in d.SEED_PAIRS]
    pool = [p["name"] for p in d.CANDIDATE_POOL]
    thr = d.SETTLE_THRESHOLD
    counts = {n: 0 for n in seed + pool}
    rot = 0
    # v0.5 prefix: round-robin over seeds, no settle, no history
    for t in range(k):
        name = seed[rot % len(seed)]
        rot = (rot + 1) % len(seed)
        counts[name] += 1
    active = list(seed)
    history, cand, settled_order = {}, 0, []
    for t in range(k, TOTAL):
        if not active:
            break
        name = active[rot % len(active)]
        rot = (rot + 1) % max(1, len(active))
        counts[name] += 1
        v = TODAY[name]
        ph = history.get(name, []) + [v]
        ph = ph[-thr * 2:]
        history[name] = ph
        recent = ph[-thr:]
        if len(recent) >= thr and all(x == recent[0] for x in recent) and recent[0] in ("PROMOTED", "REJECTED"):
            settled_order.append((t + 1, name))
            if cand < len(pool):
                active = [a for a in active if a != name]
                active.append(pool[cand])
                cand += 1
            elif remove_on_exhaustion:
                active = [a for a in active if a != name]
            history[name] = []  # daemon keeps history but a settled pair never re-settles in practice; irrelevant to counts
    census = {"REJECTED": 0, "PROMOTED": 0, "UNVERIFIED": 0}
    for n, c in counts.items():
        census[TODAY[n]] += c
    return counts, census, settled_order


def main():
    out = {"script": "pollux_replay_corrected.py", "channel_per_pair": CHANNEL, "matches_daemon_semantics": [],
           "matches_unconditional_removal": []}
    for k in range(0, 200):
        for sem in (False, True):
            counts, census, so = simulate(k, sem)
            if counts == CHANNEL:
                (out["matches_unconditional_removal"] if sem else out["matches_daemon_semantics"]).append(
                    {"k_v05_ticks": k, "census": census, "settled": so})
    counts, census, so = simulate(48, False)
    out["k48_daemon_semantics"] = {"per_pair": counts, "census": census, "settled": so}
    print(json.dumps(out, indent=1))
    if "--out" in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index("--out") + 1], "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
