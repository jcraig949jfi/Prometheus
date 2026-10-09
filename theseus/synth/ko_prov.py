"""Provenance of essential rules in task_comp knockouts (descriptive; 36/38/39 attribution).

  python -m theseus.synth.ko_prov --evaldir theseus/runs/<tag> --run <run tag>
"""

import argparse
import json
from collections import Counter

from . import sel_eval as se


def prov_class(p):
    p = str(p or "")
    if "law:" in p:
        return "law"
    if p.startswith("G0:"):
        return "G0"
    if "L:" in p:
        return "lens"
    if p.startswith("x:"):
        return "mutation_edit"  # rule inherited/substituted/mutated by a collision operator chain
    return p.split(":")[0] or "none"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--evaldir", required=True)
    ap.add_argument("--run", required=True)
    a = ap.parse_args(argv)
    g = dict(se.sample(a.run))
    KO = {json.loads(l)["id"]: json.loads(l)["v"] for l in open(f"{a.evaldir}/KO_{a.run}.jsonl", encoding="utf-8")}
    cls, ops, with_law = Counter(), Counter(), 0
    release = 0
    for i, ko in KO.items():
        rules = g[i]["rules"]
        cs = [prov_class(rules[x].get("prov")) for x in ko["essential"]]
        cls.update(cs)
        ops.update("+".join(sorted(ko["essential_ops"])) or "none" for _ in [0])
        with_law += "law" in cs
        release += sum(1 for x in ko["essential"] if "law:" in str(rules[x].get("prov")) and rules[x]["dst"] == 0)
    out = {"run": a.run, "solvers": len(KO), "essential_rule_provenance": dict(cls),
           "solvers_with_law_essential": with_law, "law_essential_rules_writing_ch0": release,
           "essential_op_sets": ops.most_common(8)}
    print(json.dumps(out))


if __name__ == "__main__":
    main()
