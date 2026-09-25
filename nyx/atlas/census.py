"""PASS 1 census: one whole-system record per Techne fossil, from the tracked record.json ONLY.

Every field says where it came from. TECHNE_RECORD = copied from the record; NYX_DERIVED = a mechanical projection
of record fields that is named here (e.g. predecessors = lineage_relations with relation in a fixed set); UNKNOWN =
the record does not say. Nothing in this file is anatomy; the cut state of a fresh census record is NOT_CUT.
Re-running is idempotent for whole_system and never touches an existing file's organs / pressures / cut.

    python -m nyx.atlas.census            # write / refresh nyx/atlas/fossils/*.json
    python -m nyx.atlas.census sample 30  # a seeded stratified sample for Stage A (printed, and written to samples/)
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from nyx.atlas.schema import SCHEMA, ROOT

REPO = ROOT.parent.parent
SPECIMENS = REPO / "techne" / "fossils" / "specimens"
PRED = {"algorithm_from", "derived_from", "historical_version_of", "port_of", "reimplementation_of", "rewrote", "supersedes"}  # supersedes X => X is a predecessor (Techne 1bb9965b4, 2026-09-16)


def _v(value, basis="TECHNE_RECORD"):
    if value in (None, "", [], {}):
        return {"value": "UNKNOWN", "basis": "UNKNOWN"}
    return {"value": value, "basis": basis}


def _exec_model(rec: dict) -> dict:
    """A named, mechanical projection: Verilog -> synchronous hardware; everything else UNKNOWN unless the record
    says. Nyx refuses to guess execution models from package names."""
    langs = [str(x).lower() for x in rec.get("language", [])]
    if any("verilog" in l or "vhdl" in l for l in langs):
        return {"value": "SYNCHRONOUS_DIGITAL_LOGIC (derived from language=Verilog)", "basis": "NYX_DERIVED"}
    return {"value": "UNKNOWN", "basis": "UNKNOWN"}


def _rel_to(r: dict) -> str:
    """The lineage-relation target. Canonical key is "to". Between 2026-09-19 and 2026-09-25 the
    capsule generation wrote "target" (it reached 80 of 192 edges); Techne closed that drift on
    2026-09-25 (TECHNE-124, comms #575): every record migrated to "to", record.validate() refuses
    "target", and a source-grep test guards the writers. The fallback below is therefore no longer
    load-bearing (0 records carry "target" at the receipt) and is kept as defence in depth: a
    reader that tolerates both keys cannot be broken by the same drift twice. Any drift is reported
    to Techne, never normalised in the record."""
    v = r.get("to", r.get("target"))
    if v is None:
        raise KeyError(f"lineage relation has neither 'to' nor 'target': {r!r}")
    return v

def whole_system(rec: dict) -> dict:
    rels = rec.get("lineage_relations", []) or []
    hd = rec.get("historical_disposition") or {}
    cap = rec.get("human_capability_summary") or {}
    obs = rec.get("observability") or {}
    preds = [f"{r['relation']}: {_rel_to(r)}" for r in rels if r.get("relation") in PRED]
    # 2026-09-16 (later the same day): Techne replaced the undirected 'superseded' with superseded_by / supersedes and
    # migrated every edge (1bb9965b4). superseded_by X => X is a successor; supersedes X => X is a predecessor (PRED).
    succs = [f"{r['relation']}: {_rel_to(r)}" for r in rels if r.get("relation") == "superseded_by"]
    rivals = [f"{r['relation']}: {_rel_to(r)}" for r in rels if r.get("relation") == "shares_ancestor_with"]
    disp = hd.get("state") if hd else None
    if disp and disp != "UNKNOWN":
        disp_v = {"value": {"state": disp, "failure_reasons": hd.get("failure_reasons", []), "evidence": hd.get("evidence", [])}, "basis": "TECHNE_RECORD"}
    else:
        disp_v = {"value": "UNKNOWN", "basis": "UNKNOWN"}
    return {
        "FOSSIL_ID": _v(rec["specimen_id"]),
        "CANONICAL_NAME": _v(rec.get("canonical_name")),
        "VERSION": _v(rec.get("version")),
        "ERA": _v(rec.get("era")),
        "HUMAN_SYSTEM": _v({"domain": rec.get("domain"), "lineage": rec.get("lineage")}),
        "HUMAN_PROBLEM": _v(rec.get("known_human_problem_solved")),
        "OBSERVED_HUMAN_CAPABILITY": _v(cap),
        "DOCUMENTED_ENVIRONMENTAL_PRESSURE": _v({"pressure": rec.get("human_environmental_pressure"), "failure_condition": rec.get("human_failure_condition")}),
        "LANGUAGE": _v(rec.get("language")),
        "EXECUTION_MODEL": _exec_model(rec),
        "ANCESTRY": _v(rec.get("lineage")),
        "KNOWN_PREDECESSORS": _v(preds, "NYX_DERIVED") if preds else {"value": "UNKNOWN", "basis": "UNKNOWN"},
        "KNOWN_SUCCESSORS": _v(succs, "NYX_DERIVED") if succs else {"value": "UNKNOWN", "basis": "UNKNOWN"},
        "KNOWN_RIVALS": _v(rivals, "NYX_DERIVED") if rivals else {"value": "UNKNOWN", "basis": "UNKNOWN"},
        "KNOWN_HISTORICAL_DISPOSITION": disp_v,
        "SOURCE_STATUS": _v({"source_type": rec.get("source_type"), "recovered_status": rec.get("recovered_status"), "tree_sha256": (rec.get("hashes") or {}).get("tree_sha256")}),
        "RUN_STATUS": _v({"run": rec.get("run_classification"), "test": rec.get("test_classification"), "environment": rec.get("environment")}),
        "OBSERVABILITY": _v(obs),
        "ORACLE_STATUS": _v({"oracle_backed": obs.get("ORACLE_BACKED", "unknown"), "test_classification": rec.get("test_classification")}, "NYX_DERIVED"),
        "INTERVENTION_READINESS": _v({"intervention_ready": obs.get("INTERVENTION_READY", "unknown"), "patch_intervention": obs.get("PATCH_INTERVENTION", "unknown"), "runnable": rec.get("run_classification", "").startswith("RUNNABLE")}, "NYX_DERIVED"),
    }


def fresh(rec: dict) -> dict:
    return {"schema": SCHEMA, "fossil_id": rec["specimen_id"], "techne_record": f"techne/fossils/specimens/{rec['specimen_id']}/record.json",
            "whole_system": whole_system(rec),
            "cut": {"state": "NOT_CUT", "mode": None, "evidence": [], "inspected_files": [], "date": None, "note": "census only; no source opened"},
            "organs": [], "rejected_cuts": [], "pressures": [],
            "composition_edges": [],
            "ancestry_edges": [{"from": rec["specimen_id"], "relation": r["relation"], "to": _rel_to(r), "note": r.get("note", ""), "basis": "TECHNE_RECORD"} for r in rec.get("lineage_relations", []) or []],
            "residue": {"state": "NOT_CHECKED", "unexplained": []}}


def run() -> int:
    (ROOT / "fossils").mkdir(parents=True, exist_ok=True)
    n_new = n_upd = 0
    for rp in sorted(SPECIMENS.glob("*/record.json")):
        rec = json.loads(rp.read_text(encoding="utf-8"))
        out = ROOT / "fossils" / f"{rec['specimen_id']}.json"
        if out.exists():
            f = json.loads(out.read_text(encoding="utf-8"))
            f["whole_system"] = whole_system(rec)
            # ancestry edges from Techne are refreshed; Nyx-added edges (basis != TECHNE_RECORD) are kept
            f["ancestry_edges"] = [e for e in f.get("ancestry_edges", []) if e.get("basis") != "TECHNE_RECORD"] + fresh(rec)["ancestry_edges"]
            n_upd += 1
        else:
            f = fresh(rec); n_new += 1
        out.write_text(json.dumps(f, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"census: {n_new} new, {n_upd} refreshed, {len(list((ROOT / 'fossils').glob('*.json')))} total")
    return 0


# ---------------------------------------------------------------- stratified sample (Stage A order, not alphabetical)
def _strata(rec: dict) -> dict:
    era = str(rec.get("era", ""))
    yr = next((int(t[:4]) for t in era.replace("(", " ").replace("/", " ").split() if t[:4].isdigit()), None)
    decade = "UNKNOWN" if yr is None else ("pre1980" if yr < 1980 else "1980s" if yr < 1990 else "1990s" if yr < 2000 else "2000s" if yr < 2010 else "2010s+")
    lang = (rec.get("language") or ["UNKNOWN"])[0].split(" ")[0]
    dom = (rec.get("domain") or ["UNKNOWN"])[0]
    run = rec.get("run_classification", "UNKNOWN")
    disp = ((rec.get("historical_disposition") or {}).get("state") or "UNKNOWN")
    files = (rec.get("hashes") or {}).get("n_files") or 0
    size = "small" if files <= 30 else "medium" if files <= 300 else "large"
    tags = set(rec.get("acquisition_tags") or []) | set(rec.get("domain") or [])
    stoch = "stochastic" if tags & {"MCMC", "Monte-Carlo", "stochastic-local-search", "evolutionary-computation", "particle-filter", "fuzzing", "digital-evolution", "retry", "backoff"} else "deterministic_or_unknown"
    return {"decade": decade, "language": lang, "domain": dom, "run": run, "disposition": disp, "size": size, "stochastic": stoch}


def sample(n: int, seed: int = 20260913, pool: str = "all") -> list:
    """pool="all": every specimen (the 2026-09-13 n=30 draw). pool="not_cut" (2026-09-17, Stage A continuation, N1):
    only specimens whose atlas file is NOT_CUT, so the remaining population gets its own preregistered order instead of
    an alphabetical or convenience one; the universe changed since 09-13 (117 -> 121 records) so the original draw
    cannot simply be extended -- a new seed is used and written into the file name."""
    recs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(SPECIMENS.glob("*/record.json"))]
    if pool == "not_cut":
        def _state(sid):
            f = ROOT / "fossils" / f"{sid}.json"
            return json.loads(f.read_text(encoding="utf-8"))["cut"]["state"] if f.exists() else "NOT_CUT"
        recs = [r for r in recs if _state(r["specimen_id"]) == "NOT_CUT"]
    rows = [{"fossil_id": r["specimen_id"], **_strata(r)} for r in recs]
    rng = random.Random(seed)
    chosen, used = [], set()
    # round-robin over strata keys so no single axis dominates; losers/superseded and SOURCE_ONLY forced in
    keys = ["disposition", "decade", "domain", "language", "run", "size", "stochastic"]
    for key in keys:
        groups = defaultdict(list)
        for r in rows:
            groups[r[key]].append(r)
        for g, members in sorted(groups.items()):
            cands = [m for m in members if m["fossil_id"] not in used]
            if cands and len(chosen) < n:
                pick = rng.choice(cands); chosen.append({**pick, "stratum": f"{key}={g}"}); used.add(pick["fossil_id"])
    while len(chosen) < n:
        cands = [r for r in rows if r["fossil_id"] not in used]
        pick = rng.choice(cands); chosen.append({**pick, "stratum": "fill"}); used.add(pick["fossil_id"])
    (ROOT / "samples").mkdir(exist_ok=True)
    out = {"schema": SCHEMA + "/sample", "seed": seed, "n": n, "pool": pool, "universe": len(rows), "keys": keys, "rows": chosen[:n],
           "universe_strata": {k: dict(Counter(r[k] for r in rows)) for k in keys}}
    name = f"stageA_seed{seed}_n{n}.json" if pool == "all" else f"stageA_{pool}_seed{seed}_n{n}.json"
    (ROOT / "samples" / name).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    return chosen[:n]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sample":
        # python -m nyx.atlas.census sample <n> [<seed>] [all|not_cut]
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        seed = int(sys.argv[3]) if len(sys.argv) > 3 else 20260913
        pool = sys.argv[4] if len(sys.argv) > 4 else "all"
        for r in sample(n, seed, pool):
            print(f"{r['fossil_id']:40s} {r['stratum']:28s} {r['decade']:8s} {r['language']:10s} {r['run']:26s} {r['disposition']:10s} {r['size']:6s} {r['stochastic']}")
        sys.exit(0)
    sys.exit(run())
