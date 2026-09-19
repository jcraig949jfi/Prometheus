"""Source adapter: Vivarium's research queue (schema viv on the M1 store).

Vivarium is an executor with its own identity: campaign = family_id
(rows without one go to 'unfamilied'), experiment = a queue row
(experiment_id UUID), attempt = viv.execution_attempt rows (parent_attempt_id
is a declared execution edge). replication_of is a declared scientific
edge. A family named like an Archaeon experiment (C4-REH-1) is linked to it
with EXECUTION_OF. Read-only; pointers to rows, not copies.
"""
from __future__ import annotations

import json
import re

from atlas import classify, db
from atlas.harvest import common as C
from atlas.harvest.pew import _read

VERSION = "vivarium/2"
PROG = "vivarium.queue"


def _host(worker):
    from atlas import classify as K
    m = re.match(r"^[\w.-]+@(m\d)$", worker or "")
    if m:
        return m.group(1).upper(), "worker_id {}".format(worker)
    h = K.host_from_tag(worker) if worker else None
    if h:
        return h, "worker_id tag {}".format(worker)
    h, basis = K.host_from_text(worker)
    return h, basis


def run(args) -> dict:
    b = C.Batch("vivarium", VERSION, "Vivarium")
    arch = dict(_read("SELECT native_id, experiment_key FROM atlas.experiment WHERE campaign_key LIKE 'archaeon.campaign/%'"))
    q = _read("""SELECT experiment_id::text, created_at, created_by, source_reason, spec_hash, status, started_at,
                        finished_at, sfe_experiment_id, pew_reference, left(result_summary::text, 1500), left(error::text, 1000),
                        family_id, arm_id, replication_of::text, cadence_lane
                 FROM viv.research_experiment_queue""")
    for (xid, created, by, reason, spec, status, st, fin, sfe_id, pew, summ, err, fam, arm, rep, lane) in q:
        fam_n = fam or "unfamilied"
        ck = C.campaign_key(PROG, fam_n)
        b.campaign(campaign_key=ck, program=PROG, native_id=fam_n, engine_id="vivarium", driver_seat="Vivarium",
                   title="Vivarium family {}".format(fam_n))
        ek = C.experiment_key(ck, xid)
        disp = status if not err else "{} ({})".format(status, "error")
        b.experiment(experiment_key=ek, campaign_key=ck, engine_id="vivarium", native_id=xid, kind="experiment",
                     title=C.trunc(arm or reason, 300), purpose=C.trunc(reason, 300), driver_seat=by or "Vivarium",
                     reported_disposition=disp, atlas_class=classify.status_class(
                         {"completed": "COMPLETE", "failed": "FAILED", "cancelled": "UNKNOWN", "queued": "QUEUED"}.get(status, status)),
                     atlas_class_confidence="LOW",
                     atlas_class_method="queue status only (completion, not a scientific disposition)",
                     validity_state="PARTIAL_EVIDENCE" if status == "failed" else "UNKNOWN",
                     config_digest=spec, result_summary=C.trunc(summ, 800),
                     extract={"sfe_experiment_id": sfe_id, "pew_reference": pew, "arm_id": arm, "cadence_lane": lane,
                              "created_at": str(created)})
        uri = "pg://prometheus_fire/viv.research_experiment_queue?experiment_id={}".format(xid)
        b.other_source(uri, "pg_rows", "PG:M1", host_id="M1", pg_ref="viv.research_experiment_queue", row_count=1,
                       record_key=xid, present=True)
        b.link(uri, "experiment", ek, "registry")
        if sfe_id:
            u2 = b.other_source("ledger://sfe/{}".format(sfe_id), "engine_ledger", "EXPECTED:M2", engine_ledger_id=sfe_id)
            b.link(u2, "experiment", ek, "engine_record")
        if err:
            b.fact("RAN", "failure_mode", "experiment", ek, "queue.error", err, uri, "error")
        if rep:
            b.edge(("experiment", ek), ("experiment", "?viv:" + rep), "REPLICATION_OF", "SCIENTIFIC",
                   reason="REPLICATION", basis="DECLARED", confidence="HIGH", uri=uri, locator="replication_of")
        if fam and fam in arch:
            b.edge(("campaign", ck), ("experiment", arch[fam]), "EXECUTION_OF", "EXECUTION", reason="UNKNOWN",
                   basis="INFERRED", confidence="MEDIUM",
                   detail="Vivarium family_id equals the Archaeon experiment id {}".format(fam), uri=uri)
    by_x = {k.rsplit(":", 1)[1]: k for k in b.t["experiment"]}
    for key in [k for k in b.edges if k[3].startswith("?viv:")]:
        e = b.edges.pop(key)
        e["dst_key"] = by_x.get(key[3][5:], C.experiment_key(C.campaign_key(PROG, "?"), key[3][5:]))
        b.edges[(key[0], key[1], key[2], e["dst_key"], key[4])] = e
    att = _read("""SELECT attempt_id::text, experiment_id::text, attempt_number, parent_attempt_id::text, design_digest,
                          bundle_hash, worker_id, opened_at, closed_at, terminal_state, receipt_digest, of_record
                   FROM viv.execution_attempt""")
    for aid, xid, n, parent, dd, bh, worker, op, cl, term, rd, rec in att:
        ek = by_x.get(xid)
        if not ek:
            continue
        ak = C.attempt_key(ek, aid)
        host, basis = _host(worker)
        b.attempt(attempt_key=ak, experiment_key=ek, native_id=aid, attempt_no=n, of_record=rec,
                  reported_status=term, validity_state=C.validity_from(term), started_at=op, finished_at=cl,
                  host_id=host, host_basis=basis, instance_tag=worker, operator_seat="Vivarium",
                  config_digest=dd, code_digest=bh, extract={"receipt_digest": rd})
        uri = "pg://prometheus_fire/viv.execution_attempt?attempt_id={}".format(aid)
        b.other_source(uri, "pg_rows", "PG:M1", host_id="M1", pg_ref="viv.execution_attempt", row_count=1,
                       record_key=aid, present=True)
        b.link(uri, "attempt", ak, "receipt")
        if parent:
            pk = next((k for k in b.t["attempt"] if k.endswith("#" + parent)), None)
            b.edge(("attempt", ak), ("attempt", pk or "?vivattempt:" + parent), "RERUN_OF", "EXECUTION",
                   reason="UNKNOWN", basis="DECLARED", confidence="HIGH", uri=uri, locator="parent_attempt_id")
    with db.harvest("vivarium", VERSION, source_ref="prometheus_fire.viv (read only)") as h:
        return b.flush(h)
