"""C-018-T030 Part I: INSTRUMENT QUALIFICATION on planted fixtures and development native units (never confirmatory seeds).

    python -m rso.aether.qualify fixtures   -> qual/records/fix_*  (ancestry units: A B E G N + near-misses + teleport)
    python -m rso.aether.qualify content    -> qual/records/content_*.npz (Aether features; Cadmus's fixtures and seeds)
    python -m rso.aether.qualify graded [p ...] -> qual/records/graded_*.npz (graded-content relay, adapter.graded_unit)
    python -m rso.aether.qualify dev LAW k0 k1  -> qual/records/native_LAW_k (development seeds, adapter.DEV_K)
    python -m rso.aether.qualify verdict    -> qual/QUALIFICATION.json: evaluate.py over the stored records ONLY

The criteria (CRITERIA below) were committed with this file before any qualification record existed. Fixtures are hand-built:
they qualify the INSTRUMENT, not a discovery (SELECTION.md s4 (ii)).
"""
import glob
import json
import os
import sys
import time

import numpy as np

from rso.aether import adapter as A, evaluate as E
from rso.aether.demand import demand_gate as DG, fixtures as F

HERE = os.path.dirname(os.path.abspath(__file__))
REC = os.path.join(HERE, "qual", "records")
OUT = os.path.join(HERE, "qual", "QUALIFICATION.json")
FSEEDS = (0, 1, 2, 3)
Y0, X0 = A.FIX_ORIGIN
# name -> (fixture kind, B override, N override, law, expected ancestry class)
ANCESTRY_CASES = {
    "A": ("A", None, None, "V1", "CONFIRMED"),                     # content relay: ancestry + content
    "B": ("B", None, None, "V1", "CONFIRMED"),                     # wake chain: structure without content
    "E": ("E", None, None, "V1", "MULTI_SOURCE"),                  # pre-seeded: content without a pathway
    "G": ("G", None, None, "V1", "INSUFFICIENT"),                  # gapped relay: pathway destroyed
    "N": ("N", None, None, "V1", "MULTI_SOURCE"),                  # noise
    "A_wrongB": ("A", (Y0 - 2, X0), None, "V1", "NOT_INTERVENTIONAL"),  # near-miss: a claimed ancestor off the pathway
    "A_misN": ("A", None, (Y0, X0 + 1), "V1", "NONSPECIFIC"),      # near-miss: a claimed non-ancestor that IS upstream
    "A_vacN": ("A", None, (Y0 - 2, X0), "V1", "CONTROL_VACUOUS"),  # T020's non-ancestor site: never diverges, cannot fail
}
CONTENT_EXPECTED = {"A": "CONTENT_TRANSMITTED", "B": "CONTENT_ABSENT", "E": "CONTENT_TRANSMITTED",
                    "G": "CONTENT_TRANSMITTED", "N": "CONTENT_ABSENT"}       # demand PREREG; G read to its extent 3
EXTENT = {"A": 6, "B": 6, "E": 6, "G": 3, "N": 6}
GRADED_P = (0.0, 0.03, 0.06, 0.12, 0.25)
GSEEDS = tuple(range(20))                                           # v2: 20 seeds x 36 origins = 720 (v1: 4 x 12 = 48, failed)
CRITERIA = {
    "ancestry": "every ANCESTRY_CASES row classed as expected in 4/4 seeds",
    "locality": "light cone holds for A, B, G (4/4) and every dev native unit; TELEPORT violates it in 4/4",
    "content": "demand-gate verdict_content on stored features equals CONTENT_EXPECTED for A B E G N; |null excess| < 0.03 on A",
    "graded": "|excess(0)| < 0.03; excess(0.12) >= 0.05; excess(0.25) >= 0.15; |excess(p) - 7p/8| <= 0.03 at every p; "
              "excess non-decreasing in p within 0.01; |null excess(0.25)| < 0.03",
    "native_dev": "every dev native unit: no binding / tree_check problem, t0 identity 1",
}


def fixtures():
    os.makedirs(REC, exist_ok=True)
    for name, (kind, B, N, law, _) in list(ANCESTRY_CASES.items()) + [("TELEPORT", ("A", None, None, "TELEPORT", None))]:
        for s in FSEEDS:
            meta, arrays = A.fixture_unit(kind, s, B=B, N=N, law=law)
            A.save_unit(os.path.join(REC, "fix_%s_%d" % (name, s)), dict(meta, case=name), arrays)
        print("fixtures", name, file=sys.stderr, flush=True)


def content():
    os.makedirs(REC, exist_ok=True)
    for kind in F.KINDS:
        units = [F.decode_unit(kind, s) for s in FSEEDS]                  # Cadmus's decodability units (fixtures.py:141)
        np.savez_compressed(os.path.join(REC, "content_%s.npz" % kind), H=np.stack([u[2] for u in units]),
                            D=np.stack([u[3] for u in units]))
        print("content", kind, file=sys.stderr, flush=True)


def graded(ps=GRADED_P):
    os.makedirs(REC, exist_ok=True)
    for p in ps:
        us = [A.graded_unit(s, p) for s in GSEEDS]
        np.savez_compressed(os.path.join(REC, "graded_%03d.npz" % round(p * 100)), H=np.stack([u[1]["H"] for u in us]),
                            D=np.stack([u[1]["D"] for u in us]),
                            labels_sha256=np.array([u[0]["labels_sha256"] for u in us]))
        print("graded", p, file=sys.stderr, flush=True)


def dev(law, k0, k1):
    os.makedirs(REC, exist_ok=True)
    for k in range(k0, k1):
        assert k in A.DEV_K
        t = time.time()
        meta, arrays = A.native_unit(law, k)
        A.save_unit(os.path.join(REC, "native_%s_%d" % (law, k)), dict(meta, wall_s_note="see DEV_TIMING"), arrays)
        with open(os.path.join(REC, "DEV_TIMING.jsonl"), "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"law": law, "seed": k, "wall_s": round(time.time() - t, 1), "host": "harry1"}) + "\n")
        print("dev", law, k, round(time.time() - t, 1), file=sys.stderr, flush=True)


def _feats(path):
    with np.load(path) as z:
        return [(s, z["H"][i], z["D"][i]) for i, s in enumerate(range(z["H"].shape[0]))]


def verdict():
    out, ok = {"criteria": CRITERIA, "ancestry": {}, "locality": {}, "content": {}, "graded": {}, "native_dev": {}}, {}
    units = {}
    for p in sorted(glob.glob(os.path.join(REC, "*.json"))):
        meta, arrays = A.load_unit(p[:-5])
        units[os.path.basename(p)[:-5]] = (meta, arrays)
    for name, (_, _, _, _, want) in ANCESTRY_CASES.items():
        rows = [E.evaluate_unit(*units["fix_%s_%d" % (name, s)]) for s in FSEEDS]
        got = [r["cls"] for r in rows]
        out["ancestry"][name] = {"expected": want, "got": got, "removed_B": [r["removed_B"] for r in rows],
                                 "removed_N": [r["removed_N"] for r in rows], "problems": sum(len(r["problems"]) for r in rows)}
    ok["ancestry"] = all(v["got"] == [v["expected"]] * 4 and not v["problems"] for v in out["ancestry"].values())
    lc = {name: [E.light_cone(*units["fix_%s_%d" % (name, s)])[0] for s in FSEEDS] for name in ("A", "B", "G", "TELEPORT")}
    natives = {k: v for k, v in units.items() if k.startswith("native_")}
    lc["native_dev"] = [E.light_cone(*v)[0] for v in natives.values()]
    out["locality"] = lc
    ok["locality"] = all(all(lc[x]) for x in ("A", "B", "G", "native_dev")) and not any(lc["TELEPORT"]) and bool(lc["native_dev"])
    for kind in F.KINDS:
        feats = _feats(os.path.join(REC, "content_%s.npz" % kind))
        acc = E.decode(feats)
        st = {str(s): v for s, v in __import__("r1_reduce").stats(acc).items()}
        d = {"Dstat": {s: round(v["Dstat"], 4) for s, v in st.items()},
             "min_seed_acc_by_radius": [round(float(min(np.asarray(acc[s]).mean(axis=0)[r] for s in acc)), 3) for r in range(6)]}
        out["content"][kind] = {"verdict": DG.verdict_content(d, EXTENT[kind]), "expected": CONTENT_EXPECTED[kind],
                                "excess": round(E.excess_all(acc), 4), "acc_by_radius": d["min_seed_acc_by_radius"]}
        if kind == "A":
            out["content"]["A"]["null_excess"] = round(E.excess_all(E.decode(feats, null=True)), 4)
    ok["content"] = all(v["verdict"] == v["expected"] for v in out["content"].values()) and \
        abs(out["content"]["A"]["null_excess"]) < 0.03
    ex = {}
    for p in GRADED_P:
        feats = _feats(os.path.join(REC, "graded_%03d.npz" % round(p * 100)))
        ex[p] = E.excess_all(E.decode(feats))
        out["graded"][str(p)] = {"excess": round(ex[p], 4), "expected": round(7 * p / 8, 4),
                                 "per_seed_Dstat": [round(v["Dstat"], 4) for v in __import__("r1_reduce").stats(E.decode(feats)).values()]}
        if p == GRADED_P[-1]:
            out["graded"][str(p)]["null_excess"] = round(E.excess_all(E.decode(feats, null=True)), 4)
    ok["graded"] = (abs(ex[0.0]) < 0.03 and ex[0.12] >= 0.05 and ex[0.25] >= 0.15
                    and all(abs(ex[p] - 7 * p / 8) <= 0.03 for p in GRADED_P)
                    and all(ex[b] >= ex[a] - 0.01 for a, b in zip(GRADED_P, GRADED_P[1:]))
                    and abs(out["graded"][str(GRADED_P[-1])]["null_excess"]) < 0.03)
    for k, (meta, arrays) in sorted(natives.items()):
        out["native_dev"][k] = E.evaluate_unit(meta, arrays)
    ok["native_dev"] = bool(natives) and all(not r["problems"] and r["t0_sites"] == 1 for r in out["native_dev"].values())
    out["ok"] = ok
    out["qualified"] = all(ok.values())
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps(ok), "qualified", out["qualified"])
    return 0 if out["qualified"] else 1


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "fixtures":
        fixtures()
    elif c == "content":
        content()
    elif c == "graded":
        graded([float(x) for x in sys.argv[2:]] or GRADED_P)
    elif c == "dev":
        dev(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif c == "verdict":
        sys.exit(verdict())
