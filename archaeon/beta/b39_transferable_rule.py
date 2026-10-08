"""B39 -- what rule do the TRANSFERABLE (B35 echo-free world-distribution) foragers implement? (evaluation only)

On 5 echo-free unfiltered family worlds (B36's set) per elite: (1) sensed observation words (controls.audit_composed);
(2) the action taken per local-pool-presence pattern -- the invariant rule "harvest the non-empty pool by its position"
predicts HARVEST index == position of the (first) non-empty pool word, and MOVE when none is non-empty.
Readout per elite: share of ticks with exactly one non-empty pool word on which the harvest index equals that
position ("position-match"); share of all-empty ticks on which it moves.
"""
import json
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

from archaeon.beta.b32_world_distribution import family_world
from archaeon.beta.controls import audit_composed

OUT = Path(__file__).resolve().parent / "results"


def main():
    b36 = json.loads((OUT / "B36_result.json").read_text(encoding="utf-8"))
    free = [i for i, e in enumerate(b36["echo_lift"]) if e < .05][:5]
    worlds = [family_world(("unfiltered", i)) for i in free]
    rows = []
    for r in json.loads((OUT / "B32echofree_result.json").read_text(encoding="utf-8"))["rows"]:
        if "elite_manifest" not in r:
            continue
        m = r["elite_manifest"]; p = Player(m)
        sensed, match_n, match_ok, empty_n, empty_move = [], 0, 0, 0, 0
        for w, s in worlds:
            R = w.w.R
            a = audit_composed(m, w, s)
            sensed.append(sorted(i for i in a["sensed_words"] if i < R))
            for ep in range(8):
                st = w.reset(s, ep, None); vm = p.fresh_state(); rng = SplitMix64(seed_from("wse.vmrng", 7, ep))
                while not w.done(st):
                    obs = w.observe(st)[0]
                    outs, _ = p.run_tick(vm, [obs], w.K, rng)
                    nz = [i for i in range(R) if obs[i] > 0]
                    if len(nz) == 1 and outs and outs[0]:
                        match_n += 1; match_ok += (outs[0][0] % R) == nz[0]
                    if not nz:
                        empty_n += 1; empty_move += bool(len(outs) > 1 and outs[1])
                    w.act(st, outs)
        rows.append({"seed": r["seed"], "sensed_pool_words_per_world": sensed,
                     "position_match": round(match_ok / max(1, match_n), 3), "n_single_food_ticks": match_n,
                     "move_when_empty": round(empty_move / max(1, empty_n), 3)})
        print(json.dumps(rows[-1]), flush=True)
    (OUT / "B39_result.json").write_text(json.dumps({"probe": "B39", "worlds": free, "rows": rows}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
