"""SPIKE K5 -- supply vs mechanism (Block A discriminator).

Give the UNCHANGED donor (a17.donor: observe -> certified classes -> single-
hole LGG -> paired selection on validate cells) RICH, SOLVABLE supplies drawn
from the K2 pool (Q2-qualified, K1-admissible, solved by >= 1 arm in K2), and
compare DONOR_G1 with DONOR_P. Three supply regimes:

  GCD_RICH   observe 4 non-G1 gcd-stratum families, validate 3 other gcd ones
  NONG1_MIX  observe 4 non-G1 families (any stratum), validate 3 non-G1
  G1_PLUS    observe 2 G1-mechanism + 2 non-G1, validate 3 non-G1

6 independent family draws per regime x {G1, P}. Forensic labels
("K5-..."), never a campaign catalog. No tribunal/Q4 re-run: the question is
whether the MECHANISM derives and selects a NEW schema when the supply exists,
and whether inheriting G1 changes that.
"""
import json
import random
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ENG = Path(__file__).resolve().parents[3] / "engine"
sys.path.insert(0, str(ENG))
import os  # noqa: E402
os.environ["A17_FASTEVAL"] = "1"
import a17  # noqa: E402

HERE = Path(__file__).resolve().parent
LET = "abcdefghijklmnopqrstuvwxyz"


def fam_name(i):
    return "kf_%s%s%s" % (LET[i // 676 % 26], LET[i // 26 % 26], LET[i % 26])


def _donor(args):
    a17.worker_init()
    return a17.donor(args)


if __name__ == "__main__":
    rows = json.loads((HERE / "K2_ADMISSIBLE_SOLVABILITY.json").read_text())["rows"]
    pool = []
    for i, r in enumerate(rows):
        if r["Q2_size"] is None:
            continue
        if r["PRISTINE"]["solved"] + r["L1"]["solved"] == 0:
            continue
        pool.append(dict(r, name=fam_name(i)))
    ng = [r for r in pool if not r["g1_body"]]
    g1 = [r for r in pool if r["g1_body"]]
    gcd = [r for r in ng if r["op"] == "gcd"]
    print("pool", len(pool), "nonG1", len(ng), "G1", len(g1), "gcd", len(gcd),
          "nonG1 by op", Counter(r["op"] for r in ng))
    rng = random.Random("APHRODITE/FRONTIER/K5/v1")
    regimes = {}
    for k in range(6):
        if len(gcd) >= 7:
            s = rng.sample(gcd, 7)
            regimes["GCD_RICH_%d" % k] = (s[:4], s[4:])
        s = rng.sample(ng, 7)
        regimes["NONG1_MIX_%d" % k] = (s[:4], s[4:])
        a, b = rng.sample(g1, 2), rng.sample(ng, 5)
        regimes["G1_PLUS_%d" % k] = (a + b[:2], b[2:])
    jobs = []
    for key, (obs, val) in regimes.items():
        fams = ([dict(f, role="OBSERVE", qualified_dev_size=f["Q2_size"]) for f in obs]
                + [dict(f, role="VALIDATE", qualified_dev_size=f["Q2_size"]) for f in val])
        specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fams}
        for kind in ("G1", "P"):
            jobs.append(("K5-" + key, kind, 0, fams, specs))
    with ProcessPoolExecutor(8, initializer=a17.worker_init) as ex:
        res = list(ex.map(_donor, jobs, chunksize=1))
    summ = defaultdict(Counter)
    out = []
    for (cat, kind, _r, fams, _s), d in zip(jobs, res):
        reg = cat.split("-")[1].rsplit("_", 1)[0]
        t = d["trace"]
        row = {"regime": cat, "donor": kind, "classes": len(t["classes"]),
               "observed_families": sorted({o["family"] for o in t["observed"]}),
               "candidates": [(c["schema"], c["SEMANTICALLY_NEW"]) for c in t["candidate_schemas"]],
               "selected": t["selected"], "selected_schemas": t["selected_schemas"],
               "NEW": d["SELECTED_SEMANTICALLY_NEW"], "meta": d["meta_charges"],
               "table": {k: (round(v["mean_paired_saving"]), round(v["lower95_one_sided"]), v["eligible"])
                         for k, v in t["selection_table"].items()}}
        out.append(row)
        s = summ["%s/%s" % (reg, kind)]
        s["n"] += 1
        s["any_new_candidate"] += any(c[1] for c in row["candidates"])
        s["NEW_selected"] += row["NEW"]
        s["classes"] += row["classes"]
        print(cat, kind, "classes", row["classes"], "cands", row["candidates"][:6], "sel", row["selected"],
              row["selected_schemas"], "NEW", row["NEW"])
    (HERE / "K5_SUPPLY_VS_MECHANISM.json").write_text(json.dumps({"summary": {k: dict(v) for k, v in summ.items()},
                                                                  "rows": out}, indent=1))
    for k in sorted(summ):
        print(k, dict(summ[k]))
