"""RB-2 stage 1 -- census (forensic, not a disposition).

  A. Reproduce K1 (V0) EXACTLY: the parameterised row with V0's parameters on
     K1's own sample (K1's seed) must give K1's witness-level counts.
  B. Draw 1,500 per stratum from the forensic seed APHRODITE/COMPOUNDING/RB2/v1
     (paired H1 / widened inits) and evaluate every variant's structural
     preconditions (V0-V6), the T4 family profile (V7/V8), the task-grounded
     body class and K1's G1-body flag.
Writes RB2_CENSUS_ROWS.json (per-draw rows) for rb2_qualify.py.
"""
import json
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rb2_common as C   # noqa: E402

HERE = C.HERE


def _k1_job(args):
    op, p = args
    r = C.row(p, C.VARIANTS["V0"])
    r["g1_body"] = C.T3E.body_key(p[2]) in C.T3E.g1_mechanisms()
    return op, r


def _job(d):
    out = {"op": d["op"], "k": d["k"], "body": d["body"], "final": d["final"],
           "init_H1": d["init_H1"], "init_WIDE": d["init_WIDE"]}
    pH = ("fold", d["init_H1"], d["body"], d["final"])
    pW = ("fold", d["init_WIDE"], d["body"], d["final"])
    for v, prm in C.VARIANTS.items():
        r = C.row(pH if prm["inits"] == "H1" else pW, prm)
        out[v] = {k: r[k] for k in ("admissible", "struct_ok", "invariant", "nondegenerate",
                                    "stress_none", "prefix_violations", "wrap_probes")}
    out["profile_H1"] = C.T4.family_profile(pH)
    out["profile_WIDE"] = out["profile_H1"] if pW == pH else C.T4.family_profile(pW)
    out["body_class"] = C.body_class(d["body"])
    out["g1_body"] = C.T3E.body_key(d["body"]) in C.T3E.g1_mechanisms()
    return out


if __name__ == "__main__":
    t0 = time.time()
    import k1_supply_census as K1
    k1 = json.loads((C.SPIKES / "K1_SUPPLY_CENSUS.json").read_text())["witness_level"]
    with ProcessPoolExecutor(C.WORKERS, initializer=C.worker_init) as ex:
        krows = list(ex.map(_k1_job, K1.sample(), chunksize=25))
    rep = defaultdict(Counter)
    for op, r in krows:
        c = rep[op]
        c["n"] += 1
        for k in ("invariant", "struct_ok", "nondegenerate", "admissible", "g1_body"):
            c[k] += bool(r[k])
        c["stress_none_any"] += r["stress_none"] > 0
        c["admissible_and_g1"] += r["admissible"] and r["g1_body"]
        c["admissible_not_g1"] += r["admissible"] and not r["g1_body"]
    mism = {op: {k: [k1[op][k], rep[op][k]] for k in k1[op] if k1[op][k] != rep[op][k]} for op in k1}
    mism = {op: v for op, v in mism.items() if v}
    print("K1 reproduction:", "EXACT" if not mism else mism, "(%.0fs)" % (time.time() - t0), flush=True)
    draws = C.sample()
    with ProcessPoolExecutor(C.WORKERS, initializer=C.worker_init) as ex:
        rows = list(ex.map(_job, draws, chunksize=25))
    (HERE / "RB2_CENSUS_ROWS.json").write_text(json.dumps(
        {"seed_label": C.SEED_LABEL, "N_per_stratum": 1500,
         "k1_reproduction": {"exact": not mism, "mismatches": mism,
                             "reproduced": {op: dict(v) for op, v in rep.items()}},
         "rows": rows}, separators=(",", ":")))
    print("census rows:", len(rows), "(%.0fs)" % (time.time() - t0))
