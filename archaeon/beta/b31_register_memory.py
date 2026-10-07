"""B31 -- WHAT do the content-sensing foragers remember? Per-register forgetting ablation (evaluation only).

For a content-sensing elite (B30: uses state), zero ONE register at every tick boundary (all other state kept) and
measure the reward drop; also zero the tape region beyond the genome each tick ("tape forgetting"). The registers
whose forgetting costs >= .05 hold the carried state. Then, for the most load-bearing register, the value it holds
at tick start is tabulated against the last action, to read what it encodes (e.g. a direction bit).
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b27_noclock_generality import load_world

OUT = Path(__file__).resolve().parent / "results"


def run(m, w, seed, forget=None, E=8, trace=None):
    p = Player(m); total = mx = 0.0
    glen = len(m["genome"])
    for ep in range(E):
        st = w.reset(seed, ep, None); vm = p.fresh_state(); rng = SplitMix64(seed_from("wse.vmrng", 7, ep))
        last = None
        while not w.done(st):
            p.begin_tick(vm)
            if forget == "tape":
                for i in range(glen, len(vm["tape"])):
                    vm["tape"][i] = 0
            elif forget is not None:
                vm["regs"][forget] = 0
            if trace is not None:
                trace.append((tuple(vm["regs"]), last))
            vm["ticks"] = max(vm["ticks"], 1)
            outs, _ = p.run_tick(vm, w.observe(st), w.K, rng)
            last = tuple((ch, o[0] % 4) for ch, o in enumerate(outs) if o)
            w.act(st, outs)
        total += max(0.0, st["reward"]); mx += st["max_reward"]
    return min(1.0, total / max(1e-9, mx))


def main():
    b25 = {r["seed"]: r for r in json.loads((OUT / "B25_result.json").read_text(encoding="utf-8"))["rows"] if r.get("arm") == "NOCLOCK"}
    b27 = {(r["world"], r["seed"]): r for r in json.loads((OUT / "B27_result.json").read_text(encoding="utf-8"))["rows"] if "elite_manifest" in r}
    targets = [("P-boom_K_D_persist_s3", b25[2504]), ("P-boom_K_D_persist_s3", b25[2506]), ("C6-unable.T3", b27[("C6-unable.T3", 2703)])]
    rows = []
    for wname, r in targets:
        w0, seed = load_world(wname); w = NoClock(w0); m = r["elite_manifest"]
        base = run(m, w, seed)
        drops = {"r%d" % k: round(base - run(m, w, seed, forget=k), 4) for k in range(m["n_regs"])}
        drops["tape"] = round(base - run(m, w, seed, forget="tape"), 4) if m["persist"] in ("tape", "all") else None
        key = [k for k, v in drops.items() if v is not None and v >= .05]
        enc = {}
        for k in key:
            if k.startswith("r"):
                tr = []; run(m, w, seed, trace=tr, E=8)
                idx = int(k[1:]); tab = defaultdict(Counter)
                for regs, last in tr:
                    tab[str(last)][regs[idx] if regs[idx] < 8 else ">=8"] += 1
                enc[k] = {a: dict(c.most_common(3)) for a, c in sorted(tab.items(), key=lambda kv: -sum(kv[1].values()))[:5]}
        rows.append({"world": wname, "seed": r["seed"], "persist": m["persist"], "n_regs": m["n_regs"], "elite": round(base, 4),
                     "drops": drops, "load_bearing_state": key, "encoding_by_last_action": enc})
        print(json.dumps({k: rows[-1][k] for k in ("world", "seed", "persist", "elite", "load_bearing_state")}), flush=True)
        for k, v in enc.items():
            print("  ", k, json.dumps(v))
    (OUT / "B31_result.json").write_text(json.dumps({"probe": "B31", "rows": rows}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
