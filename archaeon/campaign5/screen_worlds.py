"""World screening for Campaign 5 (directive fact 6 / hard rule): every world used for an
improvement claim is checked for pre-solution BEFORE populations are frozen or a preregistration
is sealed. The rule is fixed here, in code, before any candidate is looked at:

    ELIGIBLE iff  best held-out over ALL 57 starting parents (48 held-out episodes, rng_seed 7)
                  is  < 0.70   (headroom to the 0.90 summit >= 0.20)
             and  >= 3/16      (the world is not dead: some parent clears the viability floor)

    python -m archaeon.campaign5.screen_worlds [--out archaeon/campaign5/WORLD_SCREEN_<date>.json]

Candidates are the campaign's own world knobs varied one or two at a time; nothing is tuned after
seeing a result: the whole candidate list is evaluated and the receipt lists every candidate with
its number, eligible or not.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from archaeon.wse.evolve import evaluate                                     # noqa: E402
from archaeon.wse.worlds import WorldSpec, episodes_for                      # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign5.c5base import C5, CAMPAIGN_SEED                      # noqa: E402

BEST_MAX = 0.70
FLOOR = 3 / 16
HELDOUT = 48

CANDIDATES = {
    # C4 worlds (expected pre-solved or shelf; included so the receipt shows the rule applied to them)
    "W0": WorldSpec("W0", value_bits=4),
    "W1_d4": WorldSpec("W1_d4", delay=4, value_bits=4),
    "W2_K2": WorldSpec("W2_K2", K=2, value_bits=4),
    "W2_K2d1": WorldSpec("W2_K2d1", K=2, delay=1, value_bits=4),
    # new: deeper delay, more streams, random interleave, noise, ask kinds, fanout, DAG
    "W1_d8": WorldSpec("W1_d8", delay=8, value_bits=4),
    "W1_d16": WorldSpec("W1_d16", delay=16, value_bits=4),
    "W2_K2d4": WorldSpec("W2_K2d4", K=2, delay=4, value_bits=4),
    "W3_K3": WorldSpec("W3_K3", K=3, value_bits=4),
    "W3_K3d1": WorldSpec("W3_K3d1", K=3, delay=1, value_bits=4),
    "W4_K4": WorldSpec("W4_K4", K=4, value_bits=4),
    "W2_K2_rand": WorldSpec("W2_K2_rand", K=2, interleave="random", value_bits=4),
    "W2_K2_D2": WorldSpec("W2_K2_D2", K=2, D=2, value_bits=4),
    "W1_D2": WorldSpec("W1_D2", D=2, value_bits=4),
    "W1_D4": WorldSpec("W1_D4", D=4, value_bits=4),
    "W1_noise": WorldSpec("W1_noise", noise_rate=0.25, value_bits=4),
    "W1_noise_d2": WorldSpec("W1_noise_d2", noise_rate=0.25, delay=2, value_bits=4),
    "W1_askx2": WorldSpec("W1_askx2", ask_kind="ASKX", fanout=2, value_bits=4),
    "W1_ask2": WorldSpec("W1_ask2", ask_kind="ASK2", value_bits=4),
    "W1_asko": WorldSpec("W1_asko", ask_kind="ASKO", value_bits=4),
    "W1_interleaved": WorldSpec("W1_interleaved", ask_timing="interleaved", value_bits=4),
    "W1_expensive2": WorldSpec("W1_expensive2", expensive=2, value_bits=4),
    "W1_perstream": WorldSpec("W1_perstream", K=2, op_mode="per_stream", value_bits=4),
    "W1_dag2": WorldSpec("W1_dag2", topology="dag", n_defs=2, value_bits=4),
    "W0_8b_d4": WorldSpec("W0_8b_d4", delay=4, value_bits=8),
    "W2_K2_8b": WorldSpec("W2_K2_8b", K=2, value_bits=8),
}


def screen(parents, names=None) -> dict:
    out = {"schema": "archaeon.c5.world_screen.v1", "rule": {"best_max": BEST_MAX, "floor": FLOOR, "heldout_episodes": HELDOUT, "rng_seed": 7, "campaign_seed": CAMPAIGN_SEED},
           "parents": len(parents), "screened_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "worlds": {}}
    for name, spec in CANDIDATES.items():
        if names and name not in names:
            continue
        try:
            eps = episodes_for(spec, CAMPAIGN_SEED, "heldout", 1, HELDOUT)
        except Exception as exc:                                       # noqa: BLE001
            out["worlds"][name] = {"knobs": spec.knobs(), "error": str(exc)[:200], "eligible": False}
            continue
        scores = []
        for p in parents:
            try:
                scores.append((evaluate(p["parent"], eps, rng_seed=7, reward_mode="per_ask")["reward_per_ask"], p["stratum"], p["organism_id"][:12]))
            except Exception as exc:                                   # noqa: BLE001
                scores.append((0.0, p["stratum"], "ERR:" + str(exc)[:40]))
        scores.sort(reverse=True)
        best = scores[0][0]
        by_stratum = {}
        for s, st, _ in scores:
            by_stratum[st] = max(by_stratum.get(st, 0.0), s)
        out["worlds"][name] = {"knobs": spec.knobs(), "best": round(best, 4), "best_parent": scores[0][2], "best_stratum": scores[0][1],
                               "best_by_stratum": {k: round(v, 4) for k, v in by_stratum.items()},
                               "n_parents_above_floor": sum(1 for s, _, _ in scores if s >= FLOOR),
                               "eligible": bool(FLOOR <= best < BEST_MAX), "headroom_to_summit": round(0.90 - best, 4)}
    out["eligible"] = sorted(n for n, w in out["worlds"].items() if w.get("eligible"))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--names", nargs="*", default=None)
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C5 world screen")
    parents = C1.parents_from_population()
    res = screen(parents, a.names)
    out = REPO / (a.out or ("archaeon/campaign5/WORLD_SCREEN_%s.json" % _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")))
    out.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    for n, w in sorted(res["worlds"].items(), key=lambda kv: kv[1].get("best", 9)):
        print("%-16s best %s  above_floor %s  %s  %s" % (n, w.get("best"), w.get("n_parents_above_floor"), "ELIGIBLE" if w.get("eligible") else "-", w.get("error", "")))
    print("eligible:", res["eligible"]); print("written:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
