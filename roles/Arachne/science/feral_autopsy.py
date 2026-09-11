"""Item 5: why did the feral organism die, and is its death evidence about
"the fewer rules the better"? Reads the frozen specimen; simulates only
the DEATH RULE under the mismatch mechanism the code contains (no crawl,
no landscape). Writes roles/Arachne/ledgers/feral_autopsy_2026-06-04.json.

The mechanism, from agents/arachne/crawler.py at 3b9d9ed15:
  - hop=True: ls_name = rng.choice(landscapes) EVERY step;
  - the frontier is ONE queue; seeds are added only when it is empty or
    every reseed_every steps, from the landscape chosen THAT step;
  - the popped node is expanded by the adapter chosen that step; every
    adapter returns [] for a node whose prefix is not its own;
  - a step with no persisted edge is a stall; 12 consecutive stalls kill.
So with L live landscapes and a frontier of one landscape, a step succeeds
with probability about 1/L regardless of any rule the organism carries.
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from specimen import Specimen, REPO  # noqa: E402


def p_death_by(T: int, p_success: float, stall: int = 12, n: int = 200000, seed: int = 0) -> float:
    """Monte Carlo: probability a run of >= `stall` consecutive failures occurs
    within T steps when each step succeeds independently with p_success."""
    rng = random.Random(seed)
    dead = 0
    for _ in range(n):
        run = 0
        for _t in range(T):
            if rng.random() < p_success:
                run = 0
            else:
                run += 1
                if run >= stall:
                    dead += 1
                    break
    return dead / n


def run() -> dict:
    S = Specimen()
    out = {"specimen_hashes": S.hashes, "organisms": []}
    for seg in (1, 2):
        c = S.crawlers[(seg, "feral-0-7")]
        es = [e for e in S.edges if e["segment"] == seg and e["crawler"] == "feral-0-7"]
        byt = defaultdict(Counter)
        for e in es:
            byt[e["tick"]][e["landscape"]] += 1
        f = S.fitness_series(seg, "feral-0-7")
        out["organisms"].append({
            "segment": seg, "id": "feral-0-7", "ruleset": {"max_neighbors": 12, "novelty_floor": 0.97, "hop": True, "frontier_mode": "random", "reseed_every": 40, "seed": 505},
            "born_tick": c["born_tick"], "death_tick": c["death_tick"], "death_reason": c["death_reason"],
            "censored_at": None if c["death_tick"] else c["end_tick"],
            "edges": c["edges"], "nodes_introduced": c["nodes_introduced"],
            "productive_ticks": {t: dict(v) for t, v in sorted(byt.items())},
            "landscapes_touched": dict(Counter(e["landscape"] for e in es)),
            "cross_landscape_edges": sum(1 for e in es if e["src"].split(":")[0] != e["dst"].split(":")[0]),
            "min_fitness": round(min(f.values()), 3) if f else None,
            "fitness_at_death_or_end": round(f[max(f)], 3) if f else None,
            "last_productive_tick": max(byt) if byt else None,
        })
    # the other hop=True organisms the mutation produced (replication of the mechanism)
    hops = []
    for k, c in S.crawlers.items():
        rs = c.get("child_ruleset")
        if rs and rs.get("hop"):
            hops.append({"segment": k[0], "id": k[1], "born_tick": c["born_tick"], "death_tick": c["death_tick"],
                         "death_reason": c["death_reason"], "lifetime": c["lifetime_ticks"], "edges": c["edges"],
                         "landscapes_touched": dict(Counter(e["landscape"] for e in S.edges if e["segment"] == k[0] and e["crawler"] == k[1]))})
    out["other_hop_true_organisms"] = hops
    # founders' fates in segment 2 for scale
    out["segment2_founders"] = [{"id": f, "death_tick": S.crawlers[(2, f)]["death_tick"], "edges": S.crawlers[(2, f)]["edges"], "lifetime": S.crawlers[(2, f)]["lifetime_ticks"]}
                                for f in ["mathlib-0-1", "lmfdb-0-2", "algolib-0-3", "oeis-0-4", "knots-0-5", "groups-0-6"]]
    # the death rule under the mismatch mechanism, no rules involved
    L = 6
    seg2 = out["organisms"][1]
    T = seg2["death_tick"]
    obs_rate = len(seg2["productive_ticks"]) / max(1, seg2["last_productive_tick"])
    out["mismatch_mechanism"] = {
        "live_landscapes": L,
        "p_success_if_frontier_single_landscape": round(1 / L, 4),
        "observed_productive_rate_before_last_success": round(obs_rate, 4),
        "P_death_within_{}_ticks_at_p_1_over_L".format(T): round(p_death_by(T, 1 / L), 4),
        "P_death_within_{}_ticks_at_observed_rate".format(T): round(p_death_by(T, obs_rate, seed=1), 4),
        "P_death_within_700_ticks_at_p_1_over_L": round(p_death_by(700, 1 / L, n=20000, seed=2), 4),
        "P_death_within_700_ticks_at_observed_rate": round(p_death_by(700, obs_rate, n=20000, seed=3), 4),
        "P_death_within_700_ticks_for_a_specialist_at_p_0.9": round(p_death_by(700, 0.9, n=20000, seed=4), 4),
        "revival_path": "none: the population floor iterates over self.landscapes; 'feral' is a ruleset, not a landscape, so a dead feral is never revived (swarm.py step_all); the two hop=True children came from mutate() flipping hop, not from any feral lineage",
        "cross_landscape_capability": "none: every adapter emits edges inside its own landscape; hop changes which adapter is asked, never the endpoints; a feral organism cannot weave a bridge, only the rosetta and operational weavers do",
    }
    return out


def main():
    out = run()
    path = REPO / "roles" / "Arachne" / "ledgers" / "feral_autopsy_2026-06-04.json"
    path.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("organisms", "other_hop_true_organisms", "mismatch_mechanism")}, indent=1)[:6000])
    print("->", path)


if __name__ == "__main__":
    main()
