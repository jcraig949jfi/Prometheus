"""B45 -- re-score B44 with adequate samples (instrument repair).

B44's held-out readout used E=8 episodes of ONE world seed, shared by every elite and control. Rule analysis then showed
the best elites LATCH the first hint, and hint accuracy is flat (~.54 at every tick, 400 episodes), so in expectation
latching the first hint scores the same as following each hint. The B44 "beats reactive" may be shared-sample luck.
Re-score: E=64 episodes on each of 4 world seeds (key 200-203); elites, REACTIVE, STICKY; persist=none for elites.
"""
import json
from pathlib import Path

from archaeon.beta.b43_evidence_world import REACTIVE, STICKY, evidence_world
from archaeon.campaign6.worlds.runtime import evaluate_world

OUT = Path(__file__).resolve().parent / "results"


def sc(m, seeds):
    vals = []
    for k in seeds:
        w, s = evidence_world(4, 0.6, key=k)
        vals.append(evaluate_world(m, w, s, 64, rng_seed=7)["reward"])
    return round(sum(vals) / len(vals), 4)


def main():
    seeds = [200, 201, 202, 203]
    rows = [r for r in json.loads((OUT / "B44_result.json").read_text(encoding="utf-8"))["rows"] if "elite_manifest" in r]
    out = {"REACTIVE": sc(REACTIVE, seeds), "STICKY": sc(STICKY, seeds)}
    for r in rows:
        m = r["elite_manifest"]
        out["B44_%d" % r["seed"]] = {"score": sc(m, seeds), "persist_none": sc(dict(m, persist="none"), seeds), "B44_E8": r["elite"]}
    print(json.dumps(out, indent=0))
    (OUT / "B45_result.json").write_text(json.dumps({"probe": "B45", "E": 64, "world_seeds": seeds, "scores": out}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
