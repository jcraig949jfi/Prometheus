"""Phase 2 A/C/D: exposure-normalised rates by topology, task and stage, with the allocation bias removed.

Unit: the RUN (one independent random initial population; distinct seed). Runs in one family share a factor vector,
so family-level clustering is reported beside every rate (n_families) and a family-bootstrap CI is given.
Lanes:
  FIXED   kind in {exploration} -- vectors chosen by the sparse pairwise sampler, not by promotion feedback
          (the early-stage matched 'control' partners are excluded: their vectors are chosen by a treatment)
  ALL     every non-positive-control run (allocation distorted by promotion; reported for contrast only)
Outcomes (computed from summary fields that do NOT depend on the discredited detectors):
  exact_solve     best_score_tail >= 0.999 (a sustained exact answer; comparable across ATOMIC/INCREMENTAL), non-NEUTRAL only
  hifi_repro      endogenous, replication_rate_tail >= 0.05 and mean_fidelity_tail >= 0.9 (the harness 'replication'
                  predicate -- NOT yet adjudicated as self-replication; see TRACED_*)
  spont           spontaneous_replication trigger, RANDOM init, no init_tapes (interventions excluded)
  extinct         summary.extinct
  persistent      endogenous & alive_fraction >= 0.3 & not extinct
Writes receipts/RATES.json."""
from __future__ import annotations

import collections
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import load as Ld  # noqa: E402

B = 400


def outcomes(r):
    s = r["summary"]; v = r["vec"]; endo = v["reproduction"] in Ld.ENDOGENOUS
    return {
        "exact_solve": None if v["scoring"] == "NEUTRAL" else (s.get("best_score_tail") or 0) >= 0.999,
        "hifi_repro": (s.get("replication_rate_tail") or 0) >= 0.05 and (s.get("mean_fidelity_tail") or 0) >= 0.9 if endo else None,
        "spont": bool(r["triggers"].get("spontaneous_replication")) if (endo and v["init"] == "RANDOM" and r["kind"] != "intervention") else None,
        "extinct": bool(s.get("extinct")),
        "persistent": (s.get("alive_fraction", 0) >= 0.3 and not s.get("extinct")) if endo else None,
    }


def rate_with_family_ci(rows, key, rng):
    xs = [(r["family"], o[key]) for r, o in rows if o[key] is not None]
    if not xs:
        return None
    by = collections.defaultdict(list)
    for f, x in xs:
        by[f].append(x)
    fams = list(by)
    k = sum(x for _, x in xs); n = len(xs)
    boots = []
    for _ in range(B):
        samp = [rng.choice(fams) for _ in fams]
        kk = sum(sum(by[f]) for f in samp); nn = sum(len(by[f]) for f in samp)
        boots.append(kk / nn if nn else 0)
    boots.sort()
    return {"k": k, "n": n, "n_families": len(fams), "rate": round(k / n, 4), "ci95_family_boot": [round(boots[int(0.025 * B)], 4), round(boots[int(0.975 * B)], 4)]}


def main() -> None:
    R = [r for r in Ld.runs() if r["kind"] != "positive_control"]
    rng = random.Random(20260923)
    O = [(r, outcomes(r)) for r in R]
    lanes = {"FIXED": [(r, o) for r, o in O if r["kind"] == "exploration"], "ALL": O}
    out = {"definition": __doc__, "lanes": {}}
    for lane, rows in lanes.items():
        L = {}
        for dim, keyf in (("topology", lambda r: Ld.topology(r["vec"])), ("task", lambda r: r["vec"]["task"]),
                          ("stage", lambda r: r["stage"]), ("reproduction", lambda r: r["vec"]["reproduction"]),
                          ("representation", lambda r: r["vec"]["representation"]), ("mutation", lambda r: r["vec"]["mutation"]),
                          ("mutation_rate", lambda r: r["vec"]["mutation_rate"]), ("init", lambda r: r["vec"]["init"]),
                          ("layout", lambda r: r["vec"]["layout"]), ("pressure", lambda r: r["vec"]["pressure"]),
                          ("scoring", lambda r: r["vec"]["scoring"]), ("world", lambda r: r["vec"]["world"])):
            g = collections.defaultdict(list)
            for r, o in rows:
                g[keyf(r)].append((r, o))
            L[dim] = {lvl: {"runs": len(rs), **{k: rate_with_family_ci(rs, k, rng) for k in ("exact_solve", "hifi_repro", "spont", "extinct", "persistent")}}
                      for lvl, rs in sorted(g.items())}
        out["lanes"][lane] = L
    # allocation distortion: share of runs per topology in FIXED vs ALL
    fx = collections.Counter(Ld.topology(r["vec"]) for r, _ in lanes["FIXED"]); al = collections.Counter(Ld.topology(r["vec"]) for r, _ in lanes["ALL"])
    out["allocation_share"] = {t: {"fixed": round(fx[t] / sum(fx.values()), 4), "all": round(al[t] / sum(al.values()), 4)} for t in sorted(al)}
    p = Ld.write("RATES.json", out)
    print(p)
    for dim in ("topology", "task", "reproduction", "representation", "stage"):
        print("==", dim, "(FIXED lane)")
        for lvl, d in out["lanes"]["FIXED"][dim].items():
            f = lambda k: ("%s/%s=%.3f[%.3f,%.3f]" % (d[k]["k"], d[k]["n"], d[k]["rate"], *d[k]["ci95_family_boot"])) if d[k] else "-"
            print("  %-28s runs=%-5d solve %s  hifi %s  spont %s  extinct %s" % (lvl, d["runs"], f("exact_solve"), f("hifi_repro"), f("spont"), f("extinct")))


if __name__ == "__main__":
    main()
