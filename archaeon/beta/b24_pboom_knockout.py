"""B24 -- instrument the surviving P-boom elite before naming it: per-instruction knockout + input-dependence of actions.

P-boom_K_D_persist_s3 elite (32 instructions, persist all) beats constant (.09), blind (.07) and every echo twin (.13)
with .32 in a composed world (locality 12 nodes, lethal hazards, 3 resource types, objects, history, coupling, 4
output channels). Knockout: replace instruction i by NOP (0,0,0,0) one at a time; reward drop = elite - knocked.
Then: the action (first output channel used per tick) conditioned on the observed word, to see which input
distinctions the policy acts on.
"""
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

from archaeon.beta.b23b_composed_world_audit import RUNS, score
from archaeon.campaign6.segment import resolve_world

OUT = Path(__file__).resolve().parent / "results"
NAME = "P-boom_K_D_persist_s3"


def main():
    exp = [f / NAME for f in RUNS.iterdir() if (f / NAME).is_dir()][0]
    c = json.load(gzip.open(sorted(exp.glob("chunk_*.json.gz"))[-1]))
    world = resolve_world(c["spec"]["world"]); seed = c["spec"].get("provenance", {}).get("seed", 0) or 0
    er, m = max(((score(o["manifest"], world, seed), o["manifest"]) for o in c["out"]["checkpoint_out"]["population"]), key=lambda z: z[0])
    ko = []
    for i in range(len(m["genome"]) // 4):
        g = list(m["genome"]); g[4 * i:4 * i + 4] = [0, 0, 0, 0]
        ko.append({"i": i, "drop": round(er - score(dict(m, genome=g), world, seed), 4)})
    # action conditioned on observation
    p = Player(m); act = defaultdict(Counter)
    for ep in range(16):
        st = world.reset(seed, ep, None); vm = p.fresh_state(); rng = SplitMix64(seed_from("wse.vmrng", 7, ep))
        while not world.done(st):
            obs = world.observe(st)
            outs, _ = p.run_tick(vm, obs, world.K, rng)
            chans = tuple(i for i, o in enumerate(outs) if o)
            act[str(obs[0][:2])][chans] += 1
            world.act(st, outs)
    top_obs = sorted(act.items(), key=lambda kv: -sum(kv[1].values()))[:10]
    out = {"probe": "B24", "elite": round(er, 4), "knockout": ko,
           "load_bearing": [k for k in ko if k["drop"] >= .05],
           "action_by_obs_prefix": [{"obs": o, "actions": {str(k): v for k, v in cnt.most_common(4)}} for o, cnt in top_obs]}
    print(json.dumps({k: out[k] for k in ("elite", "load_bearing")}))
    for r in out["action_by_obs_prefix"]:
        print(r)
    (OUT / "B24_result.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
