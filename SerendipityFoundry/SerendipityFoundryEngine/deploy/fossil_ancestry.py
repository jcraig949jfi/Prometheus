"""Selection ancestry: given a RETURNED fossil, mechanically identify the fossil
evidence and the selection decision responsible for proposing its ancestor
experiment. Read-only across three durable stores and git; every edge is a
durable identifier; no timestamps, no names, no fuzzy matching.

    python deploy/fossil_ancestry.py --encounter ENC-archaeon-4f6625f91b2e304b
    python deploy/fossil_ancestry.py --encounter ... --db <ledger> --json out.json

THE CHAIN, edge by edge, and the key that carries each one:

  returned fossil      ew.fossil_encounters[encounter_id]
     --run_id (exp:wrk), sfe_event_seq + sfe_entry_hash, sfe_world_id-->
  SFE                  experiments[exp_id]; observations[obs_id]; events[seq]
                       (entry_hash must EQUAL the fossil's copy; spec.pew.
                        encounter_id must EQUAL the fossil id)
     --producer.queue.experiment_id (UUID) on the fossil row-->
  Vivarium row         viv.research_experiment_queue[experiment_id]
                       (sfe_experiment_id must EQUAL exp_id; spec_hash must
                        EQUAL the SFE experiment's)
     --candidate_set_id, family_id, arm_id, request_key: on the row-->
  selection decision   the row's source_evidence: policy / mode, chosen_region
                       (an SFE world_id), preregistration path + commit,
                       the corpus table path (+ commit) it consulted
     --git blob at that commit; row where region == chosen_region-->
  source fossil        that table row's obs / exp / pew ids
     --ew.fossil_encounters[pew]; SFE observations[obs]-->
  source world/region  sfe_world_id == chosen_region, closing the loop, and
                       the preregistered rule re-applied to the committed table
                       must re-select the same region (argmax metric, tie ->
                       earliest created_ts).

VERDICTS
  ANCESTRY_COMPLETE  every edge resolved by a durable id and every equality
                     held; the source fossil ids are named
  ANCESTRY_UNIFORM   the decision record DECLARES it consumed no fossil
                     (a uniform-menu draw: corpus rows 0 and no chosen_region);
                     nothing is missing, there is no ancestor by design
  ANCESTRY_GAP       an edge could not be resolved or an equality failed; the
                     exact edge is named

Postgres credentials come from evidence_wiki/config.json (never printed).
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
DEFAULT_DB = r"D:\Prometheus-data\sfe\engine.db"


class Gap(Exception):
    def __init__(self, edge, detail):
        super().__init__("%s: %s" % (edge, detail))
        self.edge, self.detail = edge, detail


# -- stores -------------------------------------------------------------------
def pg():
    import psycopg2
    import psycopg2.extras
    cfg = json.load(open(os.path.join(_REPO, "evidence_wiki", "config.json"), encoding="utf-8"))
    host = os.environ.get("EW_DB_HOST", cfg["db_host"])
    conn = psycopg2.connect(host=host, dbname=cfg["db_name"], user=cfg["db_user"],
                            password=cfg["db_password"])
    conn.set_session(readonly=True, autocommit=True)
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def ro(db):
    c = sqlite3.connect("file:%s?mode=ro" % str(db).replace("\\", "/").replace("?", "%3f"), uri=True, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def git_show(commit, path):
    r = subprocess.run(["git", "-C", _REPO, "show", "%s:%s" % (commit, path.replace("\\", "/"))],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise Gap("decision->corpus_table", "git show %s:%s failed: %s" % (commit, path, r.stderr.strip()[:120]))
    return r.stdout


# -- the join -------------------------------------------------------------------
def trace(encounter_id, *, db=DEFAULT_DB, cur=None, git=git_show):
    cur = cur or pg()
    chain = {"schema": "fossil_ancestry.v1", "returned_fossil": encounter_id, "edges": []}

    def edge(name, **kv):
        chain["edges"].append(dict(edge=name, **kv))

    # 1. returned fossil (PEW)
    cur.execute("SELECT * FROM ew.fossil_encounters WHERE encounter_id=%s", (encounter_id,))
    f = cur.fetchone()
    if not f:
        raise Gap("returned_fossil", "no ew.fossil_encounters row for %s" % encounter_id)
    run_id = f.get("run_id") or ""
    if ":" not in run_id:
        raise Gap("fossil->sfe", "fossil carries no run_id (exp:wrk)")
    exp_id, work_id = run_id.split(":", 1)
    producer = f.get("producer") or {}
    if isinstance(producer, str):
        producer = json.loads(producer)
    qrow_id = (producer.get("queue") or {}).get("experiment_id")
    ru = f.get("resources_used") or {}
    if isinstance(ru, str):
        ru = json.loads(ru)
    obs_id = ru.get("obs_id")
    edge("returned_fossil", encounter_id=encounter_id, run_id=run_id, sfe_world_id=f.get("sfe_world_id"),
         sfe_event_seq=f.get("sfe_event_seq"), sfe_entry_hash=f.get("sfe_entry_hash"),
         queue_experiment_id=qrow_id, obs_id=obs_id)

    # 2. SFE
    c = ro(db)
    try:
        e = c.execute("SELECT exp_id, world_id, spec, spec_hash, work_id FROM experiments WHERE exp_id=?", (exp_id,)).fetchone()
        if not e:
            raise Gap("fossil->sfe", "no SFE experiment %s" % exp_id)
        spec = json.loads(e["spec"]) if e["spec"] else {}
        spec_enc = ((spec.get("pew") or {}).get("encounter_id"))
        if spec_enc != encounter_id:
            raise Gap("sfe->fossil", "SFE spec.pew.encounter_id=%r != %r" % (spec_enc, encounter_id))
        if e["world_id"] != f.get("sfe_world_id"):
            raise Gap("fossil->sfe", "world mismatch: fossil %s vs experiment %s" % (f.get("sfe_world_id"), e["world_id"]))
        if f.get("sfe_event_seq") is not None:
            ev = c.execute("SELECT entry_hash, event_type, world_id FROM events WHERE event_seq=?", (int(f["sfe_event_seq"]),)).fetchone()
            if not ev or ev["entry_hash"] != f.get("sfe_entry_hash"):
                raise Gap("fossil->sfe", "event seq %s entry_hash does not match the fossil's copy" % f.get("sfe_event_seq"))
        o = None
        if obs_id:
            o = c.execute("SELECT obs_id, exp_id, work_id, outcome, evidence_class FROM observations WHERE obs_id=?", (obs_id,)).fetchone()
            if not o or o["exp_id"] != exp_id:
                raise Gap("fossil->sfe", "observation %s missing or not on %s" % (obs_id, exp_id))
        edge("sfe", exp_id=exp_id, work_id=work_id, world_id=e["world_id"], spec_hash=e["spec_hash"],
             obs_id=obs_id, outcome=(o["outcome"] if o else None), evidence_class=(o["evidence_class"] if o else None),
             entry_hash_verified=f.get("sfe_event_seq") is not None)
        sfe_spec_hash = e["spec_hash"]
    finally:
        c.close()

    # 3. Vivarium row
    if not qrow_id:
        raise Gap("fossil->queue", "fossil producer block carries no queue experiment_id")
    cur.execute("SELECT experiment_id::text AS experiment_id, sfe_experiment_id, spec_hash, candidate_set_id, family_id, arm_id, "
                "request_key, source_reason, source_evidence, created_by FROM viv.research_experiment_queue WHERE experiment_id=%s::uuid", (qrow_id,))
    q = cur.fetchone()
    if not q:
        raise Gap("fossil->queue", "no viv.research_experiment_queue row %s" % qrow_id)
    if q["sfe_experiment_id"] != exp_id:
        raise Gap("queue->sfe", "queue.sfe_experiment_id=%r != %r" % (q["sfe_experiment_id"], exp_id))
    if q["spec_hash"] != sfe_spec_hash:
        raise Gap("queue->sfe", "queue.spec_hash != SFE experiment spec_hash")
    se = q["source_evidence"] or {}
    if isinstance(se, str):
        se = json.loads(se)
    edge("queue_row", experiment_id=q["experiment_id"], request_key=q["request_key"], candidate_set_id=q["candidate_set_id"],
         family_id=q["family_id"], arm_id=q["arm_id"], created_by=q["created_by"], source_reason=q["source_reason"],
         spec_hash_verified=True)

    # 4. selection decision
    corpus = se.get("corpus") or {}
    policy = se.get("policy") or {}
    policy_id = se.get("policy_version") or policy.get("name")
    chosen = se.get("chosen_region")
    decision = {"schema": se.get("schema"), "mode": se.get("mode"), "policy": policy_id,
                "selection_rule": se.get("selection_rule"), "corpus_hash": corpus.get("corpus_hash"),
                "corpus_rows": corpus.get("rows"), "chosen_region": chosen,
                "preregistration": se.get("preregistration"), "corpus_table": corpus.get("table"),
                "template_content_hash": policy.get("template_content_hash")}
    edge("selection_decision", **decision)
    if not chosen:
        if corpus.get("rows") == 0 or "uniform" in str(policy_id or ""):
            chain["verdict"] = "ANCESTRY_UNIFORM"
            chain["why"] = "the decision record declares no fossil input (policy %s, corpus rows %s); no ancestor by design" % (policy_id, corpus.get("rows"))
            return chain
        raise Gap("decision->source_region", "no chosen_region in source_evidence and the policy does not declare a uniform draw")

    # 5. committed corpus table -> the source fossil ids
    table = corpus.get("table")
    prereg = se.get("preregistration") or ""
    commit = None
    if "commit " in prereg:
        commit = prereg.split("commit ", 1)[1].strip(" )")
    if not table or not commit:
        raise Gap("decision->corpus_table", "source_evidence names no committed corpus table (table=%r, preregistration=%r)" % (table, prereg))
    rows = json.loads(git(commit, table))
    hit = [r for r in rows if r.get("region") == chosen]
    if len(hit) != 1:
        raise Gap("corpus_table->source_fossil", "%d rows for region %s in %s@%s" % (len(hit), chosen, table, commit))
    src = hit[0]
    # the preregistered rule, re-applied: highest metric, tie -> earliest created_ts
    best = sorted(rows, key=lambda r: (-float(r.get("metric", float("-inf"))), float(r.get("created_ts", float("inf")))))[0]
    if best.get("region") != chosen:
        raise Gap("rule->chosen_region", "re-applying the preregistered rule selects %s, not %s" % (best.get("region"), chosen))
    edge("source_fossil", region=chosen, obs_id=src.get("obs"), exp_id=src.get("exp"), pew=src.get("pew"),
         metric=src.get("metric"), table=table, commit=commit, rule_reproduced=True)

    # 6. the source fossil exists and sits in the chosen region
    cur.execute("SELECT encounter_id, sfe_world_id, run_id FROM ew.fossil_encounters WHERE encounter_id=%s", (src.get("pew"),))
    sf = cur.fetchone()
    if not sf:
        raise Gap("source_fossil->pew", "no ew.fossil_encounters row %s" % src.get("pew"))
    if sf["sfe_world_id"] != chosen:
        raise Gap("source_fossil->source_region", "source fossil world %s != chosen_region %s" % (sf["sfe_world_id"], chosen))
    c = ro(db)
    try:
        so = c.execute("SELECT obs_id, exp_id, world_id FROM observations WHERE obs_id=?", (src.get("obs"),)).fetchone()
        if not so or so["world_id"] != chosen or so["exp_id"] != src.get("exp"):
            raise Gap("source_fossil->sfe", "source observation %s missing or not (%s, %s)" % (src.get("obs"), chosen, src.get("exp")))
    finally:
        c.close()
    edge("source_region", world_id=chosen, source_run_id=sf["run_id"], source_pew=sf["encounter_id"])
    chain["verdict"] = "ANCESTRY_COMPLETE"
    chain["why"] = ("returned fossil %s <- SFE %s <- queue row %s <- decision %s over %s@%s <- source fossil %s (%s) in region %s"
                    % (encounter_id, exp_id, qrow_id, policy_id, table, commit[:9], src.get("pew"), src.get("obs"), chosen))
    return chain


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--encounter", required=True)
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)
    try:
        chain = trace(a.encounter, db=a.db)
    except Gap as g:
        chain = {"schema": "fossil_ancestry.v1", "returned_fossil": a.encounter,
                 "verdict": "ANCESTRY_GAP", "missing_edge": g.edge, "detail": g.detail}
    text = json.dumps(chain, indent=1, sort_keys=True, default=str)
    print(text)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    return 0 if chain["verdict"] != "ANCESTRY_GAP" else 1


if __name__ == "__main__":
    sys.exit(main())
