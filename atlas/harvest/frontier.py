"""Source adapter: Archaeon DEEP FRONTIER (archaeon/frontier/ on a git ref).

Identity: campaign = archaeon.frontier/deep-frontier. Idea = lineage
(LIN-*, last snapshot per id in the append-only LINEAGES.jsonl).
Experiment = transformation / spec id (B-scatter.T000, and derived
.d_seed/.d_horizon/... ids). Attempt = a RUN event (provenance.run_id).
Segment = a chunk. Run outputs live under archaeon/frontier/runs/ on the
executing host (git-ignored): pointers are recorded as EXPECTED:<host>,
never as absent.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict

from atlas import classify, db, gitsrc
from atlas.harvest import common as C

VERSION = "frontier/3"
PROGRAM = "archaeon.frontier"
CKEY = C.campaign_key(PROGRAM, "deep-frontier")
DIM_REASON = {"organism_profile": "ORGANISM_DEFORMATION", "organism": "ORGANISM_DEFORMATION",
              "world": "WORLD_DEFORMATION", "world_family": "WORLD_DEFORMATION", "pressure": "PRESSURE_DEFORMATION",
              "representation": "REPRESENTATION_CHANGE", "seed": "SEED_EXPANSION", "ruler": "RULER_REPAIR",
              "horizon": "PARAMETER_DEFORMATION", "view": "PARAMETER_DEFORMATION", "population": "PARAMETER_DEFORMATION"}
SUFFIX_REASON = {"d_seed": "SEED_EXPANSION", "d_horizon": "PARAMETER_DEFORMATION", "d_view": "PARAMETER_DEFORMATION",
                 "d_audit": "REPLICATION", "rerun": "REPLICATION", "d_unknown": "UNKNOWN"}
RUN_HOST = "M2"  # scheduler receipts are written on the executing host; see the basis text on each attempt


def ekey(tid: str) -> str:
    return C.experiment_key(CKEY, tid)


def run(args) -> dict:
    ref = args.ref
    sha = gitsrc.resolve(ref)
    files = gitsrc.ls_tree(ref, "archaeon/frontier")
    newest, oldest, touching = gitsrc.path_commits(ref, "archaeon/frontier")
    b = C.Batch("frontier", VERSION, "Archaeon")
    conn = db.connect()
    try:
        with conn.cursor() as cur:
            b.local_shas = C.local_commits(cur)
            cur.execute("SELECT native_id, experiment_key FROM atlas.experiment WHERE campaign_key LIKE 'archaeon.campaign/%'")
            camp_exp = dict(cur.fetchall())
    finally:
        conn.close()
    b.campaign(campaign_key=CKEY, program=PROGRAM, native_id="deep-frontier", engine_id="archaeon.frontier",
               driver_seat="Archaeon", title="DEEP FRONTIER (code-first scheduler)")
    blobs = {p: (s, z) for p, s, z in files}
    with gitsrc.CatFile() as cat:
        def src(path, obj=None, text=None, record=None, line=None):
            s, z = blobs[path]
            return b.git_source(ref, path, s, z, newest.get(path), oldest.get(path), obj=obj, text=text,
                                record_key=record, line=line)
        for path, (s, z) in blobs.items():
            name = path.rsplit("/", 1)[-1]
            if path.endswith(".py"):
                continue
            role = ("registry" if "/registry/" in path or "/queues/" in path else "digest" if "/digests/" in path
                    else "decision" if name == "DECISIONS.md" else "design" if name.endswith(".md") else "other")
            text = cat.text(s) if name.endswith(".jsonl") else None
            obj = cat.json(s) if name.endswith(".json") else None
            b.link(src(path, obj=obj, text=text), "campaign", CKEY, role)
        # ideas: lineages (last snapshot per id wins; earlier snapshots stay behind the pointer)
        lpath = "archaeon/frontier/registry/LINEAGES.jsonl"
        lineages, lline = {}, {}
        for i, row in enumerate(_jsonl(cat.text(blobs[lpath][0]) if lpath in blobs else ""), 1):
            lineages[row["lineage_id"]] = row
            lline[row["lineage_id"]] = i
        for lid, row in lineages.items():
            ikey = "{}/{}".format(PROGRAM, lid)
            oo = row.get("originating_observation") or {}
            b.idea(idea_key=ikey, native_id=lid, kind="lineage", engine_id="archaeon.frontier", campaign_key=CKEY,
                   title=C.trunc(row.get("title"), 500), question=C.trunc(oo.get("summary")),
                   reported_status=row.get("status"), origin_text=C.trunc(json.dumps(oo, sort_keys=True), 1500),
                   extract={"mode": row.get("mode"), "tags": row.get("tags"),
                            "representation_limits": row.get("representation_limits")})
            u = src(lpath, record=lid, line=(lline[lid], lline[lid]))
            b.link(u, "idea", ikey, "registry")
            for tok in re.findall(r"\bC\d-\d{2}\b", str(oo.get("source") or "")):
                if tok in camp_exp:
                    b.edge(("idea", ikey), ("experiment", camp_exp[tok]), "ORIGINATES_FROM", "SCIENTIFIC",
                           reason="CROSS_SUBSTRATE_TRANSPLANT" if "graph" in json.dumps(row) else "CONTINUATION",
                           basis="DECLARED", confidence="HIGH", detail=C.trunc(oo.get("summary"), 800), uri=u,
                           locator="originating_observation.source")
            for name, val in C.flatten({"representation_limits": row.get("representation_limits"),
                                        "failed_branches": row.get("failed_branches"),
                                        "controls": row.get("controls")}, depth=1):
                if val:
                    b.fact("OBSERVED", "representation_descriptor" if "representation" in name else "control",
                           "idea", ikey, name, val, u, name)
            if row.get("parent_lineage"):
                b.edge(("idea", ikey), ("idea", "{}/{}".format(PROGRAM, row["parent_lineage"])), "DESCENDANT_OF",
                       "SCIENTIFIC", reason="DECLARED_PARENT", basis="DECLARED", confidence="HIGH", uri=u)
            for t in row.get("transformations") or []:
                tid = t.get("id")
                if not tid:
                    continue
                k = b.experiment(experiment_key=ekey(tid), campaign_key=CKEY, engine_id="archaeon.frontier",
                                 native_id=tid, kind="transformation", title=C.trunc(t.get("note"), 500),
                                 question=C.trunc(t.get("note")), driver_seat="Archaeon",
                                 organism_family=t.get("to") if "organism_profile" in (t.get("dims") or []) else None,
                                 budget_summary="budget_evaluations={}".format(t.get("budget_evaluations")),
                                 reported_disposition=t.get("status"), atlas_class=classify.status_class(t.get("status")),
                                 atlas_class_confidence="LOW", atlas_class_method="status_class/1 on transformation status",
                                 extract={"dims": t.get("dims"), "from": t.get("from"), "to": t.get("to"),
                                          "pool": t.get("pool"), "trigger": t.get("trigger")})
                b.link(u, "experiment", k, "definition")
                b.edge(("experiment", k), ("idea", ikey), "TESTS", "SCIENTIFIC", basis="DECLARED", confidence="HIGH",
                       uri=u, locator="transformations[{}]".format(tid))
                for d in t.get("dims") or []:
                    b.fact("OBSERVED", "parameter", "experiment", k, "deformation.dim", d, u, tid)
                if t.get("from") or t.get("to"):
                    b.fact("OBSERVED", "organism_descriptor" if "organism_profile" in (t.get("dims") or []) else "parameter",
                           "experiment", k, "deformation.from_to", "{} -> {}".format(t.get("from"), t.get("to")), u, tid)
                    for tok in re.findall(r"\bC\d-\d{2}\b", str(oo.get("source") or "")):
                        if tok in camp_exp:
                            reason = next((DIM_REASON[d] for d in (t.get("dims") or []) if d in DIM_REASON), "UNKNOWN")
                            b.edge(("experiment", k), ("experiment", camp_exp[tok]), "DEFORMATION_OF", "SCIENTIFIC",
                                   reason=reason, basis="DECLARED", confidence="MEDIUM",
                                   detail="dims={} {} -> {}; {}".format(t.get("dims"), t.get("from"), t.get("to"),
                                                                        C.trunc(t.get("note"), 400)), uri=u)
                _derived_edge(b, tid, u)
        # events: runs, chunks, observations, interpretations, gates
        epath = "archaeon/frontier/registry/EVENTS.jsonl"
        freeze = defaultdict(int)
        for i, ev in enumerate(_jsonl(cat.text(blobs[epath][0]) if epath in blobs else ""), 1):
            kind, lid, p = ev.get("kind"), ev.get("lineage_id"), ev.get("payload") or {}
            ikey = "{}/{}".format(PROGRAM, lid)
            if kind == "FREEZE_REF":
                freeze[lid] += 1
                continue
            u = src(epath, record="{}:{}".format(kind, i), line=(i, i))
            if kind == "RUN":
                _run(b, ev, p, u, i)
            elif kind in ("OBSERVATION", "INTERPRETATION"):
                ref_t = (p.get("ref") or {}).get("transformation")
                stype, skey = ("experiment", ekey(ref_t)) if ref_t else ("idea", ikey)
                if kind == "OBSERVATION":
                    b.fact("OBSERVED", "measurement", stype, skey, "frontier.observation", p.get("text"), u,
                           str(i), stated_at=ev.get("at"))
                else:
                    b.conclusion(stype, skey, p.get("status"), p.get("text"), u, str(i), stated_at=ev.get("at"),
                                 status="UNRESOLVED" if str(p.get("status")).upper() == "PROVISIONAL" else "STANDING")
                    for tok in re.findall(r"Campaign (\d)", p.get("text") or ""):
                        b.edge(("idea", ikey), ("campaign", "archaeon.campaign/cmp" + tok), "EXPLAINS", "SCIENTIFIC",
                               basis="INFERRED", confidence="LOW",
                               detail="interpretation text names Campaign {}: {}".format(tok, C.trunc(p.get("text"), 300)),
                               uri=u)
            elif kind in ("FALSIFIER_FAILED", "BLOCKED_BY_SUPPRESSION", "GATED", "UNGATED", "CALIBRATION_EPOCH",
                          "BRANCH_POLICY_FIX", "RULER_AUTHORITY"):
                t = p.get("transformation")
                stype, skey = ("experiment", ekey(t)) if t else ("idea", ikey)
                fk = {"FALSIFIER_FAILED": "detector_firing", "BLOCKED_BY_SUPPRESSION": "campaign_decision",
                      "GATED": "campaign_decision", "UNGATED": "campaign_decision",
                      "CALIBRATION_EPOCH": "instrumentation_defect", "BRANCH_POLICY_FIX": "campaign_decision",
                      "RULER_AUTHORITY": "campaign_decision"}[kind]
                b.fact("CONCLUDED" if fk == "campaign_decision" else "OBSERVED", fk, stype, skey,
                       "frontier." + kind.lower(), p, u, str(i), stated_at=ev.get("at"))
            elif kind == "FRONTIER_EXTENDED":
                for tid in p.get("added") or []:
                    k = b.experiment(experiment_key=ekey(tid), campaign_key=CKEY, engine_id="archaeon.frontier",
                                     native_id=tid, kind="transformation", driver_seat="Archaeon",
                                     reported_disposition="PENDING", atlas_class="PLANNED", atlas_class_confidence="MEDIUM",
                                     atlas_class_method="FRONTIER_EXTENDED event")
                    b.link(u, "experiment", k, "registry")
                    _derived_edge(b, tid, u)
            elif kind == "DESIGNED":
                for tid in p.get("ids") or []:
                    k = b.experiment(experiment_key=ekey(tid), campaign_key=CKEY, engine_id="archaeon.frontier",
                                     native_id=tid, kind="transformation", driver_seat="Archaeon",
                                     title=C.trunc(p.get("note"), 300), reported_disposition="DESIGNED",
                                     atlas_class="PLANNED", atlas_class_confidence="MEDIUM",
                                     atlas_class_method="DESIGNED event")
                    b.link(u, "experiment", k, "design")
                    b.edge(("experiment", k), ("idea", ikey), "TESTS", "SCIENTIFIC", basis="DECLARED",
                           confidence="HIGH", uri=u)
        # provenance.parent_run names a run id; resolve it to the attempt that carries it (or keep it dangling)
        by_run = {a["native_id"]: k for k, a in b.t["attempt"].items() if a.get("experiment_key", "").startswith(CKEY)}
        for key in [k for k in b.edges if k[3].startswith("?run:")]:
            e = b.edges.pop(key)
            rid = key[3][5:]
            e["dst_key"] = by_run.get(rid, C.attempt_key(ekey("?"), rid))
            b.edges[(key[0], key[1], key[2], e["dst_key"], key[4])] = e
        for lid, n in freeze.items():
            b.fact("RAN", "telemetry_availability", "idea", "{}/{}".format(PROGRAM, lid), "frontier.freeze_refs", n,
                   src(epath), "kind=FREEZE_REF count", author="ATLAS_DERIVED")
        # queues: planned / claimed work
        for path in [p for p in blobs if "/queues/" in p and p.endswith(".jsonl")]:
            items = {}
            for row in _jsonl(cat.text(blobs[path][0])):
                if row.get("item_id"):
                    items[row["item_id"]] = row
            for qid, row in items.items():
                tid = row.get("transformation_id")
                if not tid:
                    continue
                k = b.experiment(experiment_key=ekey(tid), campaign_key=CKEY, engine_id="archaeon.frontier",
                                 native_id=tid, kind="transformation", driver_seat="Archaeon")
                u = src(path, record=qid)
                b.link(u, "experiment", k, "registry")
                b.fact("OBSERVED", "campaign_decision", "experiment", k, "queue." + row.get("pool", "?").lower(),
                       {x: row.get(x) for x in ("state", "lane", "priority", "budget_evaluations", "note")}, u, qid)
                _derived_edge(b, tid, u)
    # a spec id '<family>/<hash>' names FAMILY membership, not a parent experiment: keep the family on the
    # experiment and drop the edge unless the family is itself an indexed transformation
    for key in [k for k in b.edges if k[4] == "DESCENDANT_OF" and k[2] == "experiment" and k[3] not in b.t["experiment"]]:
        b.edges.pop(key)
        b.experiment(experiment_key=key[1], extract={"family_id": key[3].rsplit(":", 1)[-1]})
    with db.harvest("frontier", VERSION, source_ref=ref, source_sha=sha) as h:
        return b.flush(h)


def _derived_edge(b, tid: str, uri: str) -> None:
    """B-scatter.T000.d_seed -> B-scatter.T000 (a declared suffix; DF-012/013 naming)."""
    m = re.match(r"^(.*)\.(d_[a-z]+|rerun)$", tid)
    if m:
        b.edge(("experiment", ekey(tid)), ("experiment", ekey(m.group(1))),
               "REPLICATION_OF" if m.group(2) in ("d_audit", "rerun") else "DEFORMATION_OF",
               "SCIENTIFIC" if m.group(2) not in ("rerun",) else "EXECUTION",
               reason=SUFFIX_REASON.get(m.group(2), "UNKNOWN"), basis="INFERRED", confidence="HIGH",
               detail="derived id suffix .{} (frontier naming, DF-012/013)".format(m.group(2)), uri=uri)
    elif "/" in tid:
        base = tid.split("/", 1)[0]
        b.edge(("experiment", ekey(tid)), ("experiment", ekey(base)), "DESCENDANT_OF", "SCIENTIFIC",
               reason="PARAMETER_DEFORMATION", basis="INFERRED", confidence="MEDIUM",
               detail="spec id {} is a member of family {}".format(tid, base), uri=uri)


def _run(b, ev, p, u, line):
    """Two RUN shapes: the old loop's (chunks as dicts + provenance.run_id) and
    the scheduler's (chunks as digests + receipt path, no run id; the event
    time is the attempt identity)."""
    rr = p.get("run_ref") if isinstance(p.get("run_ref"), dict) else {}
    prov = rr.get("provenance") or {}
    chunks = rr.get("chunks") or []
    tid = p.get("transformation") or ev.get("transformation") or "?"
    rid = prov.get("run_id") or "at" + re.sub(r"[^0-9TZ]", "", ev.get("at") or str(line))
    k = b.experiment(experiment_key=ekey(tid), campaign_key=CKEY, engine_id="archaeon.frontier", native_id=tid,
                     kind="transformation", driver_seat="Archaeon")
    akey = C.attempt_key(k, rid)
    first = chunks[0] if chunks and isinstance(chunks[0], dict) else {}
    b.attempt(attempt_key=akey, experiment_key=k, native_id=rid, reported_status=p.get("status") or "RUN",
              started_at=None, finished_at=ev.get("at"), host_id=RUN_HOST,
              host_basis="INFERRED: DEEP FRONTIER scheduler runs on M2 (registry committed by Archaeon[m2-*]; runs/ absent on M1)",
              operator_seat="Archaeon", budget={"evaluations": p.get("evaluations")},
              config_digest=first.get("spec_hash"),
              extract={"lane": prov.get("lane"), "generator": prov.get("generator"),
                       "generator_version": prov.get("generator_version"), "params": prov.get("params"),
                       "seed": prov.get("seed"), "trigger": prov.get("trigger"), "receipt": rr.get("receipt")})
    b.link(u, "attempt", akey, "registry")
    b.experiment(experiment_key=k, seeds=[str(prov["seed"])] if prov.get("seed") is not None else [],
                 search_family=prov.get("generator"), reported_disposition=p.get("status"),
                 atlas_class="UNKNOWN", atlas_class_confidence="LOW",
                 atlas_class_method="RUN event carries no disposition")
    if rr.get("receipt"):
        path = "archaeon/frontier/" + rr["receipt"]
        ru = b.other_source("hostfile://{}/{}".format(RUN_HOST, path), "file", "EXPECTED:" + RUN_HOST,
                            host_id=RUN_HOST, path=path, present=None)
        b.link(ru, "attempt", akey, "receipt")
    for name, val in C.flatten({"lane": prov.get("lane"), "params": prov.get("params"), "seed": prov.get("seed"),
                                "generator": prov.get("generator")}, "provenance", depth=2):
        if val is not None:
            b.fact("RAN", "parameter", "attempt", akey, name, val, u, name)
    b.fact("RAN", "budget", "attempt", akey, "evaluations", p.get("evaluations"), u, "payload.evaluations")
    if prov.get("parent_run"):
        b.edge(("attempt", akey), ("attempt", "?run:" + str(prov["parent_run"])), "DESCENDANT_OF", "EXECUTION",
               reason="UNKNOWN", basis="DECLARED", confidence="HIGH", detail="provenance.parent_run", uri=u)
    for n, ch in enumerate(chunks):
        ch = ch if isinstance(ch, dict) else {"chunk": n, "out_digest": ch}
        nid = "chunk_{:03d}".format(int(ch.get("chunk", n)))
        sk = C.segment_key(akey, nid)
        b.segment(segment_key=sk, attempt_key=akey, native_id=nid, kind="chunk", ordinal=int(ch.get("chunk", n)),
                  host_id=RUN_HOST, evaluations=ch.get("evaluations"), digest=ch.get("out_digest"),
                  extract={x: ch.get(x) for x in ("g0", "g1", "anchors", "events", "freezes", "spec_hash") if x in ch})
        if ch.get("path"):
            cu = b.other_source("hostfile://{}/{}".format(RUN_HOST, ch["path"]), "file", "EXPECTED:" + RUN_HOST,
                                host_id=RUN_HOST, path=ch["path"],
                                file_sha256=(ch.get("out_digest") or "").replace("sha256:", "") or None, present=None)
            b.link(cu, "segment", sk, "rows")


def _jsonl(text):
    for line in (text or "").splitlines():
        line = line.strip()
        if line:
            try:
                v = json.loads(line)
                if isinstance(v, dict):
                    yield v
            except ValueError:
                pass
