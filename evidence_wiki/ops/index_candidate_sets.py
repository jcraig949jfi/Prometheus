"""Index a Vivarium candidate set into PEW as typed references.

Order: roles/Archaeon/prompts/2026-09-10_delegation/MNEMOSYNE_PROTEUS.md item 1.

REFERENCE-ONLY. Every reference is built from identifiers and digests the
ENGINE already supplied on the completed queue row. Nothing here reads, copies
or recomputes scientific bytes: if a digest is not present in the authoritative
record, the reference is reported UNRESOLVED rather than invented.

Four references per completed row, when their authoritative digest exists:

    EXPERIMENT   sfe_experiment_id      digest = queue.spec_hash
    OBSERVATION  obs_id                 digest = anchor.sfe_entry_hash of the
                                        OBSERVATION_RECORDED event (selector
                                        names the event, so the digest's
                                        meaning is unambiguous: it is the
                                        ledger entry's hash, not a hash of
                                        observation content PEW never saw)
    ENCOUNTER    pew encounter_id       digest = audit_envelope.envelope_hash
    RECEIPT      work result            digest = anchor.work_completed_event
                                                 .result_hash
    ARTIFACT     artifact_locators      only where present

Axis derivation, stated so it is auditable rather than assumed:

    software_stage       'alpha' when the row's declared authority says alpha,
                         else NULL. Never guessed from a passing run.
    connection_evidence  'runnable' -- these rows are typed end-to-end
                         executions with an engine observation and a resource
                         receipt. NEVER 'demonstrated-transfer': no controlled
                         held-out effect is claimed by indexing.
    scientific_outcome   'inconclusive' -- PEW is recording the ABSENCE of an
                         adjudicated outcome. Promotion belongs to Harmonia /
                         Archaeon; an index pass must not manufacture one.
    reproduction_state   'benchmark-attempted' for a completed executed row.

Usage (from evidence_wiki/):
    python ops/index_candidate_sets.py --candidate-set cs-c3-2 --namespace prod
    python ops/index_candidate_sets.py --candidate-set cs-h1h0-1-p1 --receipt <path>
"""
import argparse
import json
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew import db as ewdb
from ew import workspace                       # noqa: E402

SHA = "sha256:"


def rows_for(conn, cs):
    with ewdb.dict_cur(conn) as cur:
        cur.execute(
            "SELECT experiment_id, sfe_experiment_id, pew_reference, spec_hash, "
            "       status, family_id, arm_id, source_evidence, "
            "       artifact_locators, result_summary "
            "FROM viv.research_experiment_queue "
            "WHERE candidate_set_id=%s ORDER BY created_at", (cs,))
        return [dict(r) for r in cur.fetchall()]


def encounter_of(row):
    """PEW encounter id from the queue's pew_reference:
    pew:encounter/<encounter_id>:<exp_id>:<work_id>"""
    ref = row.get("pew_reference") or ""
    if not ref.startswith("pew:encounter/"):
        return None, None
    tail = ref[len("pew:encounter/"):]
    parts = tail.split(":")
    return parts[0], (":".join(parts[1:]) if len(parts) > 1 else None)


def plan_refs(row, cs):
    """Return (list of ref payloads, list of unresolved reasons)."""
    rs = row.get("result_summary") or {}
    anchor = rs.get("anchor") or {}
    env = rs.get("audit_envelope") or {}
    eng = rs.get("engine") or {}
    wce = anchor.get("work_completed_event") or {}
    enc_id, run_id = encounter_of(row)
    obs_id = anchor.get("obs_id") or (anchor.get("binds") or {}).get("obs_id") \
        or rs.get("obs_id")
    world_id = (rs.get("pew") or {}).get("world_anchor", {}).get("body", {}) \
        .get("world_id") or anchor.get("world_id")
    authority = ((row.get("source_evidence") or {}).get("authority") or "").lower()
    status = row.get("status")
    # Axes by terminal state (--all-statuses, 2026-09-11). A failed row was
    # attempted and failed; a cancelled row was never run. Neither is
    # "runnable" evidence of connection: that word is reserved for a row
    # the engine observed to completion. Nothing here adjudicates outcome.
    axes = {
        "completed": ("runnable", "inconclusive", "benchmark-attempted"),
        "failed": ("conceptual", "not-run", "failed"),
        "cancelled": ("conceptual", "not-run", "blocked"),
    }.get(status, ("conceptual", "not-run", "blocked"))

    common = {
        "encounter_id": enc_id,
        "run_id": run_id,
        "sfe_world_id": world_id,
        "sfe_observation_id": obs_id,
        "sfe_event_seq": anchor.get("sfe_event_seq"),
        "sfe_entry_hash": anchor.get("sfe_entry_hash"),
        "sfe_engine_instance_id": eng.get("engine_instance_id"),
        "availability": "PRESENT",
        "candidate_set_id": cs,
        "producer_experiment_id": row.get("experiment_id"),
        "software_stage": "alpha" if "alpha" in authority else None,
        "connection_evidence": axes[0],
        "scientific_outcome": axes[1],
        "reproduction_state": axes[2],
        "namespace": "prod",
        "recorded_in_sfe": True,
        "terminal_state": row.get("status"),
        "producer": {"component": "vivarium.queue", "family_id": row.get("family_id"),
                     "arm_id": row.get("arm_id"),
                     "engine_source_commit": eng.get("source_commit"),
                     "engine_source_hash": eng.get("engine_source_hash")},
    }

    out, unresolved = [], []

    def add(kind, source_kind, source_id, digest, selector=None):
        if not source_id:
            unresolved.append(f"{kind}: no source id")
            return
        if not (isinstance(digest, str) and digest.startswith(SHA)
                and len(digest) == len(SHA) + 64):
            unresolved.append(f"{kind}: no authoritative digest "
                              f"(source {source_id})")
            return
        d = dict(common, ref_kind=kind, source_kind=source_kind,
                 source_id=source_id, content_digest=digest)
        if selector:
            d["selector"] = selector
        out.append(d)

    add("EXPERIMENT", "EXPERIMENT", row.get("sfe_experiment_id"),
        row.get("spec_hash"))
    add("OBSERVATION", "OBSERVATION", obs_id, anchor.get("sfe_entry_hash"),
        selector="event:OBSERVATION_RECORDED")
    add("ENCOUNTER", "ENCOUNTER", enc_id, env.get("envelope_hash"))
    add("RECEIPT", "EVENT", wce.get("event_id") or anchor.get("sfe_event_id"),
        wce.get("result_hash"), selector="work_completed_event.result_hash")

    locs = row.get("artifact_locators") or {}
    for name, loc in (locs.items() if isinstance(locs, dict) else []):
        if isinstance(name, str) and name.startswith(SHA) and isinstance(loc, dict)                 and "artifact_id" not in loc:
            # Phase-2 shape (cs-h1h0-1-p2b, 2026-09-11): the locator is KEYED
            # by the artifact's content address and carries source_world /
            # source_artifact. A content address is the engine's identity for
            # an artifact blob, so it is both source id and digest here.
            add("ARTIFACT", "ARTIFACT", name, name,
                selector=f"source_world:{loc.get('source_world')};"
                         f"source_artifact:{loc.get('source_artifact')}")
            continue
        dg = loc.get("digest") if isinstance(loc, dict) else None
        add("ARTIFACT", "ARTIFACT",
            (loc or {}).get("artifact_id") if isinstance(loc, dict) else str(loc),
            dg, selector=name)
    return out, unresolved


WORKSPACE = workspace.assert_not_canonical("index a candidate set")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-set", required=True)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8377)
    ap.add_argument("--machine", default="M1")
    ap.add_argument("--agent", default="mnemosyne-indexer")
    ap.add_argument("--namespace", default="prod")
    ap.add_argument("--receipt", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--all-statuses", action="store_true",
                    help="index failed and cancelled rows too; a row without "
                         "engine digests reports every reference UNRESOLVED "
                         "rather than inventing one")
    a = ap.parse_args()

    cfg = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    tok = cfg["machine_tokens"].get(a.machine) or cfg["auth_token"]
    base = f"http://{a.host}:{a.port}/api/v1"
    hdr = {"Authorization": f"Bearer {tok}", "X-Prometheus-Machine": a.machine,
           "X-Prometheus-Agent": a.agent}

    conn = ewdb.connect()
    rows = rows_for(conn, a.candidate_set)
    conn.close()

    started = time.time()
    counts = {"rows_total": len(rows), "rows_completed": 0, "rows_skipped": 0,
              "rows_by_status": {}, "rows_indexed_non_completed": 0,
              "refs_inserted": 0, "refs_duplicate_identical": 0,
              "refs_conflict": 0, "refs_rejected": 0}
    by_kind, unresolved_rows, errors = {}, [], []

    for row in rows:
        st = row.get("status")
        counts["rows_by_status"][st] = counts["rows_by_status"].get(st, 0) + 1
        if st != "completed" and not a.all_statuses:
            counts["rows_skipped"] += 1
            continue
        if st == "completed":
            counts["rows_completed"] += 1
        else:
            counts["rows_indexed_non_completed"] += 1
        payloads, unresolved = plan_refs(row, a.candidate_set)
        if unresolved:
            unresolved_rows.append({"experiment_id": row["experiment_id"],
                                    "sfe_experiment_id": row.get("sfe_experiment_id"),
                                    "reasons": unresolved})
        for d in payloads:
            d["namespace"] = a.namespace
            if a.dry_run:
                by_kind[d["ref_kind"]] = by_kind.get(d["ref_kind"], 0) + 1
                continue
            r = requests.post(f"{base}/refs", headers=hdr, json=d, timeout=60)
            if r.status_code == 200:
                st = r.json().get("status")
                counts["refs_inserted" if st == "inserted"
                       else "refs_duplicate_identical"] += 1
                by_kind[d["ref_kind"]] = by_kind.get(d["ref_kind"], 0) + 1
            elif r.status_code == 409:
                counts["refs_conflict"] += 1
                errors.append({"experiment_id": row["experiment_id"],
                               "ref_kind": d["ref_kind"], "http": 409,
                               "detail": str(r.json().get("detail"))[:200]})
            else:
                counts["refs_rejected"] += 1
                errors.append({"experiment_id": row["experiment_id"],
                               "ref_kind": d["ref_kind"],
                               "http": r.status_code,
                               "detail": str(r.text)[:200]})

    receipt = {
        "candidate_set_id": a.candidate_set,
        "indexed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "namespace": a.namespace,
        "command": (f"python ops/index_candidate_sets.py --candidate-set "
                    f"{a.candidate_set} --namespace {a.namespace}"
                    + (" --all-statuses" if a.all_statuses else "")),
        "all_statuses": a.all_statuses,
        "workspace": {k: WORKSPACE[k] for k in ("base_sha", "branch",
                                                  "worktree_path", "dirty")},
        "counts": counts,
        "refs_by_kind": by_kind,
        "artifacts_present": by_kind.get("ARTIFACT", 0),
        "rows_with_unresolved_references": unresolved_rows,
        "n_rows_with_unresolved_references": len(unresolved_rows),
        "errors": errors,
        "axis_derivation": {
            "software_stage": "alpha when the row's declared authority says alpha, else null",
            "connection_evidence": "runnable (typed end-to-end execution with an engine observation and resource receipt); never demonstrated-transfer",
            "scientific_outcome": "inconclusive -- PEW records the ABSENCE of an adjudicated outcome and never adjudicates one",
            "reproduction_state": "benchmark-attempted for a completed executed row",
        },
        "reference_only": ("every digest is engine-supplied on the queue row; "
                           "no scientific bytes were read, copied or recomputed"),
        "seconds": round(time.time() - started, 1),
    }
    out = Path(a.receipt) if a.receipt else (
        HERE / "integration" / f"index_receipt_{a.candidate_set}.json")
    out.write_text(json.dumps(receipt, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in receipt.items()
                      if k != "rows_with_unresolved_references"}, indent=1))
    print(f"receipt: {out}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
