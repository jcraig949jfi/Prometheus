"""E3 s3: autonomous final evaluation + cognitive ledger (coordinator side; runs AFTER the lifetime).

Every family the lifetime ended with a dev-consistent program is re-evaluated ALONE (no archive, no search; library
primitives allowed: they are the organism's own machinery; a library call is evaluated exactly as its expansion) on the
evaluator view: test + tribunal, value-or-FAIL (worlds.judge). The library used is the one the lifetime had when that
family was searched (record.library_snapshots[family.library_sha256]).

Endpoint per (world, arm, seed):
  R3R4_admitted_qualified  = # ADMITTED R3/R4 families with a qualified program            [primary]
  R2_admitted_qualified    = # ADMITTED R2 families with a qualified program
  total_qualified          = # families (any rung/status) with a qualified program
  plus per-rung counts and spurious_dev_consistent (dev-consistent but not qualified).

Cognitive ledger per solved family (sources of the computation; a family can carry several):
  ORGANISM        the lifetime search produced the program (always true for a hit; the mutation chain did the work)
  DEVELOPMENTAL   the program calls >= 1 promoted primitive
  SEARCH_INFRA    the hit's burst was restored from an ARCHIVE program (or the archive program itself was
                  dev-consistent: 'archive_delivered')
  CERTIFIER       used for the final verdict only; 0 consultations during the lifetime (by construction: the lifetime
                  has no evaluator access, tested by the access log)
  primary_source  = SEARCH_INFRA:archive_delivered > DEVELOPMENTAL+SEARCH_INFRA > DEVELOPMENTAL > SEARCH_INFRA >
                    ORGANISM (a summary label only)
"""
from collections import Counter
from typing import Dict, Optional

from tfs1 import core as C
from tfs1.library import Library

from . import worlds as WD


def library_of(rec: Dict, fam: Dict) -> Optional[Library]:
    sha = fam.get("library_sha256")
    if not sha:
        return None
    return Library.from_json(rec["library_snapshots"][sha])


def evaluate_lifetime(rec: Dict, root, world_id: str, evaluator_dir: Optional[str] = None) -> Dict:
    ev = WD.Evaluator(root, world_id, override_dir=evaluator_dir)
    rows = []
    cnt = Counter()
    for fam in rec["families"]:
        meta = ev.meta(fam["opaque"])
        row = {"opaque": fam["opaque"], "family_id": meta["family_id"], "rung": meta["rung"],
               "status": meta["status"], "class": meta.get("class"), "solved_in_lifetime": fam["solved"]}
        if fam["solved"]:
            lib = library_of(rec, fam)
            v = WD.judge(fam["program"], ev.task(fam["opaque"]), lib)
            row.update({"program": fam["program"], "qualified": v["qualified"], "test_ok": v["test_ok"],
                        "tribunal_ok": v["tribunal_ok"]})
            src = ["ORGANISM"]
            if fam.get("uses_library"):
                src.append("DEVELOPMENTAL")
            if fam.get("origin") == "archive":
                src.append("SEARCH_INFRA")
            delivered = fam.get("origin") == "archive" and fam["hit_charge"] is not None and \
                fam["hit_charge"] <= fam["n_starts"]
            if delivered:
                primary = "SEARCH_INFRA:archive_delivered"
            elif "DEVELOPMENTAL" in src and "SEARCH_INFRA" in src:
                primary = "DEVELOPMENTAL+SEARCH_INFRA"
            elif "DEVELOPMENTAL" in src:
                primary = "DEVELOPMENTAL"
            elif "SEARCH_INFRA" in src:
                primary = "SEARCH_INFRA"
            else:
                primary = "ORGANISM"
            row["ledger"] = {"sources": src, "primary_source": primary, "archive_delivered": delivered,
                             "certifier": "final verdict only; 0 lifetime consultations",
                             "library_calls": sorted(set(C.calls_in(C.parse(fam["program"]))))}
            if lib is not None:
                row["ledger"]["library_call_depths"] = {c: lib.entries[c].depth
                                                        for c in row["ledger"]["library_calls"]}
            if v["qualified"]:
                cnt["total_qualified"] += 1
                cnt["qualified_" + meta["rung"]] += 1
                cnt["primary_" + primary] += 1
                if meta["status"] == "ADMITTED":
                    cnt["R3R4_admitted_qualified" if meta["rung"] in ("R3", "R4") else
                        "%s_admitted_qualified" % meta["rung"]] += 1
            else:
                cnt["spurious_dev_consistent"] += 1
        rows.append(row)
    adm = Counter(m["rung"] for m in ev.id_map.values() if m["status"] == "ADMITTED")
    endpoint = {"R3R4_admitted_qualified": cnt.get("R3R4_admitted_qualified", 0),
                "R2_admitted_qualified": cnt.get("R2_admitted_qualified", 0),
                "total_qualified": cnt.get("total_qualified", 0),
                "admitted_R3R4": adm.get("R3", 0) + adm.get("R4", 0), "admitted_R2": adm.get("R2", 0),
                "families": len(rows), "solved_in_lifetime": sum(r["solved_in_lifetime"] for r in rows),
                "counts": dict(sorted(cnt.items()))}
    return {"world_id": world_id, "arm": rec["arm"], "seed": rec["seed"], "endpoint": endpoint, "families": rows,
            "decision_sha256": rec["decision_sha256"]}
