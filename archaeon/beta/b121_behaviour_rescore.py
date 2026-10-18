"""B121 -- uniform BEHAVIOURAL re-score of every reward-semantics genome (exploratory, descriptive).

B119 showed the constant-twin type-info readout gives PLAIN false positives in family 2 (accidental reactions to a
non-zero type word). Behaviour (toxic share of harvests on the held-out set) separated the arms there. This re-scores
EVERY saved best genome of B118d/f/g (family 1, interleaved) and B119 (family 2) on toxic share, so both families are
compared on the same readout. 'avoids' = share < .25 (GEN3 ~.51, CHK3 0).
Exploratory: the threshold was chosen after B119's decode; the prereg use of this readout is B120 (secondary) and the
family-2 successor.
"""
import json
from pathlib import Path

from archaeon.beta.b118h_decode import trace
from archaeon.beta.b118d_seeded_forager import heldout as ho1
from archaeon.beta.b119_semantics_family2 import world_f2

R = Path(__file__).resolve().parent / "results"
SETS = [("f1", "B118d_seeded_forager"), ("f1", "B118f_type_rep"), ("f1", "B118g_type_rep_clean"), ("f2", "B119_semantics_family2")]


def main():
    hos = {"f1": ho1(), "f2": [world_f2(("b119ho", i), .5) for i in range(12)]}
    rows = []
    for fam, d in SETS:
        for f in sorted((R / d).glob("best_*.json")):
            arm, seed = f.stem.split("_")[1], int(f.stem.split("_")[2])
            t = trace(json.loads(f.read_text(encoding="utf-8")), hos[fam])
            r = {"family": fam, "set": d, "arm": arm, "seed": seed, "toxic_share": t["toxic_share"], "avoids": t["toxic_share"] < .25}
            rows.append(r); print(json.dumps(r), flush=True)
    summ = {}
    for fam in ("f1", "f2"):
        for arm in ("TOXIC", "PLAIN"):
            rs = [r for r in rows if r["family"] == fam and r["arm"] == arm]
            summ["%s_%s" % (fam, arm)] = {"n": len(rs), "avoid": sum(r["avoids"] for r in rs),
                                          "mean_share": round(sum(r["toxic_share"] for r in rs) / max(1, len(rs)), 3)}
    print(json.dumps(summ))
    (R / "B121_behaviour_rescore.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
