"""E3 s4: causal dependency test for any depth claim (coordinator side; after final evaluation).

For each QUALIFIED solution (default: ADMITTED R3/R4 families) whose program calls a promoted primitive e, re-run THAT
family's lifetime search (same arm world slot, seed, budget B, burst R, start pool) three times:
  REPLAY   the library and start pool exactly as recorded            (sanity: must reproduce the recorded hit charge)
  REMOVED  library minus e and every entry whose lineage contains e; base expressivity intact (the base grammar is
           untouched); archive starts are EXPANDED with the original library and re-refactored modulo the reduced one,
           so the archive keeps the genotype but loses the primitive
  SHAM     REMOVED + one sham entry with e's parameter types (Int-only shams; non-Int parameters are matched on arity
           and recorded), result type and body size, body uniform over the TFS-1 size class (keyed by e's id)
Each re-run stops at the first dev-consistent program, which is judged on test + tribunal (worlds.judge).
DEPENDENCY_SUPPORTED(e) iff REPLAY qualified AND REMOVED not qualified AND SHAM not qualified.
The claimed depth of the solution is the max depth of its SUPPORTED entries (0 if none).
"""
from typing import Dict, List, Optional

from tfs1 import core as C
from tfs1 import compress as CP
from tfs1.enum import Enumerator
from tfs1.library import Library, lambda_to_body, references_xs
from atlas import common as AK
from atlas.sample import sample_uniform

from . import final_eval as FE
from . import worlds as WD
from .organism import LifetimeSearch, keyed_rng


def reduced_library(lib: Library, e_id: str) -> Library:
    recs = [r for r in lib.records() if r["id"] != e_id and e_id not in r["lineage"]]
    return Library.from_json({"format": lib.to_json()["format"], "contract": C.CONTRACT, "entries": recs,
                              "closed_args": lib.closed_args})


def sham_library(red: Library, e, seed) -> Dict:
    k = len(e.params)
    ctx = {0: (), 1: ("x",), 2: ("a", "b")}[k]
    ret = e.ret if e.ret in (C.INT, C.BOOL) else C.INT
    n = e.expansion_size
    E0 = Enumerator(None)
    rng = keyed_rng(seed, "SHAM", e.id)
    lib = Library.from_json(red.to_json())
    for _ in range(1000):
        b = sample_uniform(E0, ret, ctx, n, rng)
        if b is None:
            n = max(2, n - 1)
            continue
        if references_xs(b) or (k and not C.refs_range(b, 0, k)):
            continue
        body = lambda_to_body(("lam", k, b))[0] if k else b
        try:
            s, st = lib.promote_body(body, [C.INT] * k, {"sham_for": e.id})
        except (ValueError, C.TypeErr):
            continue
        if st == "new":
            return {"library": lib, "sham_id": s.id, "sham_body": s.body,
                    "param_mismatch": any(p != C.INT for p in e.params) or ret != e.ret}
    return {"library": lib, "sham_id": None, "sham_body": None, "param_mismatch": None}


def rerun(rec: Dict, fam: Dict, lib: Optional[Library], starts: List[str], task: Dict) -> Dict:
    cfg = rec["config"]
    view = AK.LearnerView({"family_id": fam["slot"], "output_type": fam["T"], "dev": task["dev"]})
    E = Enumerator(lib if lib is not None and len(lib) else None)
    s = LifetimeSearch(view, E, rec["seed"], cfg["B"], cfg["R"], starts, cfg["k_partial"], cfg["max_fill"],
                       cfg["max_size"])
    s.run()
    out = {"hit": s.hit is not None, "hit_charge": s.hit["charge"] if s.hit else None,
           "program": s.hit["program"] if s.hit else None, "charges": s.charges}
    if s.hit:
        out["verdict"] = WD.judge(s.hit["program"], task, lib)
        out["qualified"] = out["verdict"]["qualified"]
    else:
        out["qualified"] = False
    return out


def dependency_tests(rec: Dict, final: Dict, root, world_id: str, rungs=("R3", "R4"),
                     admitted_only: bool = True) -> List[Dict]:
    ev = WD.Evaluator(root, world_id)
    byop = {f["opaque"]: f for f in rec["families"]}
    out = []
    for row in final["families"]:
        if not row.get("qualified") or row["rung"] not in rungs:
            continue
        if admitted_only and row["status"] != "ADMITTED":
            continue
        calls = row["ledger"]["library_calls"]
        if not calls:
            continue
        fam = byop[row["opaque"]]
        task = ev.task(fam["opaque"])
        task = dict(task, dev=[[list(i), o] for i, o in ev.task(fam["opaque"])["dev"]])
        lib = FE.library_of(rec, fam)
        generic = list(AK.STARTS[fam["T"]])
        starts = generic + fam["archive_starts"]
        replay = rerun(rec, fam, lib, starts, task)
        res = {"family_id": row["family_id"], "program": fam["program"], "recorded_hit_charge": fam["hit_charge"],
               "replay": replay, "replay_reproduces": replay["hit_charge"] == fam["hit_charge"], "entries": []}
        for e_id in calls:
            e = lib.entries[e_id]
            red = reduced_library(lib, e_id)
            st_red = generic + [C.to_str(CP.refactor(lib.expand(C.parse(s)), red)) for s in fam["archive_starts"]]
            removed = rerun(rec, fam, red, st_red, task)
            sh = sham_library(red, e, rec["seed"])
            st_sh = generic + [C.to_str(CP.refactor(lib.expand(C.parse(s)), sh["library"]))
                               for s in fam["archive_starts"]]
            sham = rerun(rec, fam, sh["library"], st_sh, task)
            res["entries"].append({"entry": e_id, "depth": e.depth, "body": e.body, "removed": removed,
                                   "sham": dict(sham, sham_id=sh["sham_id"], sham_body=sh["sham_body"],
                                                param_mismatch=sh["param_mismatch"]),
                                   "DEPENDENCY_SUPPORTED": bool(replay["qualified"] and not removed["qualified"]
                                                                and not sham["qualified"])})
        sup = [x["depth"] for x in res["entries"] if x["DEPENDENCY_SUPPORTED"]]
        res["supported_depth"] = max(sup) if sup else 0
        out.append(res)
    return out
