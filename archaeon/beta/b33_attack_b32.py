"""B33 -- attack the B32 positive (world-distribution foragers transfer to unseen worlds) before believing it.

B32: elites evolved on a fresh procedurally generated world every generation reach mean held-out lift .07-.13 with
blind collapse, on held-out worlds SELECTED to discriminate (hand generalist lift >= .05, P-boom elite <= .02).
Attacks (evaluation only):
  A1 UNFILTERED  40 fresh family worlds with NO selection: mean lift of each B32 elite vs the hand generalist vs the
                 P-boom-specific elite (is the advantage a selection artifact of the held-out filter?)
  A2 NAMED       the three named NOCLOCK worlds (P-boom, B-scatter, C6-unable): lift (do they also work there?)
  A3 CONTROLS    archaeon.beta.controls.audit_composed on 3 held-out worlds per elite (blind / echo / constant /
                 carries-state verdicts)
  A4 IDENTITY    are the elites the same program? (genome equality / executed-code listing of the best one)
PREDICTION (before running): A1 mean lift of B32 elites >= .03 and >= the P-boom elite's + .03; A2 positive on >= 2/3
named worlds for >= 2 elites; A3 verdicts INPUT_USING on every held-out world tested.
"""
import json
from pathlib import Path

from archaeon.beta.b25_noclock_world import load
from archaeon.beta.b27_noclock_generality import load_world
from archaeon.beta.b25_noclock_world import NoClock
from archaeon.beta.b29_leave_one_world_out import generalist
from archaeon.beta.b32_world_distribution import family_world, heldout_worlds, lift
from archaeon.beta.controls import audit_composed

OUT = Path(__file__).resolve().parent / "results"


def main():
    d = json.loads((OUT / "B32_result.json").read_text(encoding="utf-8"))
    elites = {"B32_%d" % r["seed"]: r["elite_manifest"] for r in d["rows"] if "elite_manifest" in r}
    b25 = {r["seed"]: r for r in json.loads((OUT / "B25_result.json").read_text(encoding="utf-8"))["rows"] if r.get("arm") == "NOCLOCK"}
    refs = {"hand_generalist": generalist(), "pboom_specific_2506": b25[2506]["elite_manifest"]}
    progs = {**elites, **refs}
    unf = [family_world(("unfiltered", i)) for i in range(40)]
    a1 = {k: round(sum(lift(m, w, s) for w, s in unf) / len(unf), 4) for k, m in progs.items()}
    print("A1 unfiltered mean lift", json.dumps(a1), flush=True)
    named = {"P-boom": "P-boom_K_D_persist_s3", "B-scatter": "B-scatter.T000.d_horizon", "C6-unable": "C6-unable.T3"}
    nw = {k: (NoClock(load_world(v)[0]), load_world(v)[1]) for k, v in named.items()}
    a2 = {k: {n: round(lift(m, w, s), 4) for n, (w, s) in nw.items()} for k, m in progs.items()}
    print("A2 named-world lift", json.dumps(a2), flush=True)
    ho = heldout_worlds()[:3]
    a3 = {k: [audit_composed(m, w, s)["verdicts"] for w, s in ho] for k, m in elites.items()}
    print("A3 verdicts", json.dumps(a3), flush=True)
    genomes = {k: tuple(m["genome"]) for k, m in elites.items()}
    a4 = {"distinct_genomes": len(set(genomes.values())), "n": len(genomes),
          "sizes": {k: len(g) // 4 for k, g in genomes.items()}}
    print("A4", json.dumps(a4), flush=True)
    (OUT / "B33_result.json").write_text(json.dumps({"probe": "B33", "A1_unfiltered": a1, "A2_named": a2, "A3_verdicts": a3,
                                                    "A4_identity": a4}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
