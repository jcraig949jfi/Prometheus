"""B36 -- repair of B35's echo readout: compare groups only on unfiltered worlds that are NOT echo-solvable.

B35's echo count (ECHO_EXPLAINS on unfiltered worlds 0-2) was 24/24 and 47/48 -- a property of those three worlds
(echo-solvable), not of the elites: instrument error (mine). Repair: classify each of the 40 unfiltered worlds by its
best echo twin's lift over constant; restrict the DIST vs SPECIFIC paired comparison to echo-FREE worlds (lift < .05),
for both the original B32/B32rep elites and the B35 echo-free elites.
"""
import json
from pathlib import Path

from archaeon.beta.b23b_composed_world_audit import CONSTS, constant_manifest, score
from archaeon.beta.b23c_attack_artifacts import echo_manifest
from archaeon.beta.b32_world_distribution import family_world, lift
from archaeon.beta.b34_unfiltered_decider import sign_test

OUT = Path(__file__).resolve().parent / "results"


def elites(files):
    out = []
    for f in files:
        out += [r["elite_manifest"] for r in json.loads((OUT / f).read_text(encoding="utf-8"))["rows"] if "elite_manifest" in r]
    return out


def main():
    worlds = [family_world(("unfiltered", i)) for i in range(40)]
    echo_lift = []
    for w, s in worlds:
        n = len(w.observe(w.reset(s, 0, None))[0]); base = max(score(constant_manifest(c, w.K), w, s) for c in CONSTS)
        echo_lift.append(max(score(echo_manifest(0, j, w.K), w, s) for j in range(min(8, n))) - base)
    free = [i for i, e in enumerate(echo_lift) if e < .05]
    b25 = {r["seed"]: r for r in json.loads((OUT / "B25_result.json").read_text(encoding="utf-8"))["rows"] if r.get("arm") == "NOCLOCK"}
    b27 = json.loads((OUT / "B27_result.json").read_text(encoding="utf-8"))["rows"]
    spec = [b25[s]["elite_manifest"] for s in (2504, 2505, 2506)] + [r["elite_manifest"] for r in b27 if r.get("content_sensing")]
    groups = {"B32_dist": elites(["B32_result.json", "B32rep_result.json"]), "B35_echofree": elites(["B32echofree_result.json"])}
    sl = {i: sum(lift(m, *worlds[i]) for m in spec) / len(spec) for i in free}
    summ = {"n_worlds": 40, "echo_solvable": 40 - len(free), "echo_free_worlds": len(free)}
    for g, ms in groups.items():
        dl = {i: sum(lift(m, *worlds[i]) for m in ms) / len(ms) for i in free}
        diffs = [dl[i] - sl[i] for i in free]
        pos, neg, p = sign_test(diffs)
        summ[g] = {"mean_lift_on_echo_free": round(sum(dl.values()) / len(free), 4), "paired_vs_specific": round(sum(diffs) / len(free), 4),
                   "sign": [pos, neg], "p": round(p, 6)}
    summ["specific_mean_lift_on_echo_free"] = round(sum(sl.values()) / len(free), 4)
    print(json.dumps(summ))
    (OUT / "B36_result.json").write_text(json.dumps({"probe": "B36", "summary": summ, "echo_lift": echo_lift}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
