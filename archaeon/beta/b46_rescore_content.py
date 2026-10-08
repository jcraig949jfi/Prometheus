"""B46 -- re-score the content-sensing claims (B25/B26/B27) under the B45 standard (E=64 x 4 world seeds).

B26/B27 called an elite a CONTENT sensor when the blind twin dropped reward by >= .05 (E=8, one world seed). Re-score
elite vs blind twin vs best constant with E=64 episodes on 4 world seeds (the run's spec seed + 0..3).
"""
import json
from pathlib import Path

from archaeon.beta.b23b_composed_world_audit import CONSTS, constant_manifest
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b26_word_ablation import Ablate
from archaeon.beta.b27_noclock_generality import load_world
from archaeon.campaign6.worlds.runtime import evaluate_world

OUT = Path(__file__).resolve().parent / "results"


def sc(m, w, s0):
    return sum(evaluate_world(m, w, s0 + k, 64, rng_seed=7)["reward"] for k in range(4)) / 4


def main():
    items = []
    for r in json.loads((OUT / "B25_result.json").read_text(encoding="utf-8"))["rows"]:
        if r.get("arm") == "NOCLOCK" and "elite_manifest" in r:
            items.append(("P-boom_K_D_persist_s3", r["seed"], r["elite_manifest"]))
    for r in json.loads((OUT / "B27_result.json").read_text(encoding="utf-8"))["rows"]:
        if "elite_manifest" in r and r["world"] in ("B-scatter.T000.d_horizon", "C6-unable.T3"):
            items.append((r["world"], r["seed"], r["elite_manifest"]))
    rows = []
    cache = {}
    for wname, seed, m in items:
        if wname not in cache:
            w0, s0 = load_world(wname); w = NoClock(w0)
            cache[wname] = (w, s0, max(sc(constant_manifest(c, w.K), w, s0) for c in CONSTS))
        w, s0, const = cache[wname]
        el = sc(m, w, s0); bl = sc(m, Ablate(w, "all"), s0)
        rows.append({"world": wname, "seed": seed, "elite": round(el, 4), "blind": round(bl, 4), "constant": round(const, 4),
                     "content_sensing": el - bl >= .05, "beats_constant": el - const >= .05})
        print(json.dumps(rows[-1]), flush=True)
    (OUT / "B46_result.json").write_text(json.dumps({"probe": "B46", "rows": rows}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
