"""THESEUS-39 S4: are the essential rules of solvers copies of injected-genome rules?

A rule is COPIED iff (op, src, dst, p rounded to 9 places) equals a rule of some injected
genome (exact identity, not provenance: copied provenance strings name the SOURCE run's
collision ids, which may collide with the new run's ids).

  python -m theseus.synth.inject_attr --evaldir theseus/runs/<tag> --run <run> --inject <jsonl>
"""

import argparse
import json

from . import ko_prov as kp
from . import sel_eval as se


def key(r):
    return (r["op"], tuple(r.get("src", [])), r.get("dst"), tuple(round(float(x), 9) for x in r.get("p", [])))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--evaldir", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--inject", required=True)
    a = ap.parse_args(argv)
    inj = {key(r) for l in open(a.inject, encoding="utf-8") for r in json.loads(l)["genome"]["rules"]}
    g = dict(se.sample(a.run))
    KO = {json.loads(l)["id"]: json.loads(l)["v"] for l in open(f"{a.evaldir}/KO_{a.run}.jsonl", encoding="utf-8")}
    n_ess = copied = solvers_any_copied = solvers_all_copied = with_ess = 0
    copied_prov = {}
    for i, ko in KO.items():
        rules = g[i]["rules"]
        c = [key(rules[x]) in inj for x in ko["essential"]]
        n_ess += len(c)
        copied += sum(c)
        for x, cc in zip(ko["essential"], c):
            if cc:
                k = kp.prov_class(rules[x].get("prov"))
                copied_prov[k] = copied_prov.get(k, 0) + 1
        if c:
            with_ess += 1
            solvers_any_copied += any(c)
            solvers_all_copied += all(c)
    print(json.dumps({"run": a.run, "solvers": len(KO), "solvers_with_essential": with_ess,
                      "essential_rules": n_ess, "essential_copied_from_injected": copied,
                      "copied_by_provenance_class": copied_prov,
                      "solvers_any_essential_copied": solvers_any_copied,
                      "solvers_all_essential_copied": solvers_all_copied}))


if __name__ == "__main__":
    main()
