"""Campaign evidence, projections, ingestion state and the producer-event
inbox (PEW point release 2026-09-17). Mounted by ew.service.

Read routes (bearer + agent identity, every read logged):
    GET /api/v1/campaign/observations   selectors: campaign_id, harness_id,
        attempt_id, kind, cell, world_id, arm, foundry_profile, stratum
        (json, jsonb containment on strata), generation_min/max; at least
        one selector; limit <= 2000
    GET /api/v1/campaign/summary?campaign_id=   counts by kind / harness /
        attempt / UNKNOWN identities -- a pure count, no interpretation
    GET /api/v1/projections                       the registry
    GET /api/v1/projections/{name}/{version}      definition + rows;
        selectors row_key_prefix, stratum (json containment on payload)
    GET /api/v1/ingestion/checkpoints, /ingestion/conflicts
    GET /api/v1/events   producer, stream, after_seq, kind, limit
    GET /api/v1/release  the restart receipt's machine-readable half

Write route (write scope), the receiving half of a producer outbox
(amendment 6D, order s14): POST /api/v1/events with one event or a list.
Per event the answer is one of
    accepted            new (producer, stream, seq), stored
    duplicate           same event_id or same (producer, stream, seq) with
                        the same payload digest: no-op
    checkpoint_mismatch same (producer, stream, seq), DIFFERENT digest:
                        refused, recorded in ingestion_conflicts, stored
                        row untouched
    rejected_malformed  missing/invalid fields: nothing stored
and `gap` (true when seq skipped ahead of the checkpoint; the gap is
recorded on the checkpoint, never healed). A producer never has to infer
PEW's state: the checkpoint is readable, and every answer is typed.
"""
from __future__ import annotations

import hashlib
import json
import time

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel

from . import db as ewdb


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), default=str)


class ProducerEventIn(BaseModel):
    model_config = {"extra": "forbid"}
    producer: str
    stream: str
    seq: int
    event_id: str
    kind: str
    payload: dict
    logical_time: int | None = None
    actor: str | None = None
    envelope: dict | None = None


def mount(app, get_conn, identity, log_read):
    from . import SCHEMA_VERSION, ONTOLOGY_VERSION, FOSSIL_CONTRACT_VERSION
    from .campaign_ingest import READER_VERSION, CONTRACT_VERSION
    from .projections import BUILDER_VERSION

    def _rows(cur):
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    @app.get("/api/v1/campaign/observations")
    def campaign_observations(request: Request, campaign_id: str | None = None, harness_id: str | None = None,
                              attempt_id: str | None = None, kind: str | None = None, cell: str | None = None,
                              world_id: str | None = None, arm: str | None = None, foundry_profile: str | None = None,
                              stratum: str | None = None, generation_min: int | None = None,
                              generation_max: int | None = None, limit: int = 200, conn=Depends(get_conn)):
        t0 = time.time()
        ident = identity(request)
        where, args = [], []
        for col, val in (("campaign_id", campaign_id), ("harness_id", harness_id), ("attempt_id", attempt_id),
                         ("kind", kind), ("cell", cell), ("world_id", world_id), ("arm", arm),
                         ("foundry_profile", foundry_profile)):
            if val is not None:
                where.append(f"{col}=%s"); args.append(val)
        if stratum is not None:
            try:
                st = json.loads(stratum)
            except ValueError:
                raise HTTPException(422, "stratum_not_json")
            if not isinstance(st, dict) or not st:
                raise HTTPException(422, "stratum_must_be_nonempty_object")
            where.append("strata @> %s::jsonb"); args.append(json.dumps(st))
        if generation_min is not None:
            where.append("generation >= %s"); args.append(generation_min)
        if generation_max is not None:
            where.append("generation <= %s"); args.append(generation_max)
        if not where:
            raise HTTPException(400, "at_least_one_selector_required")
        with conn.cursor() as cur:
            cur.execute("SELECT observation_id, kind, campaign_id, harness_id, execution_id, design_id, design_kind, "
                        "attempt_id, attempt_number, resumed_from_attempt, step_id, foundry_profile, schedule_id, "
                        "rng_identity, world_id, engine_instance_id, engine_source_hash, arm, seed, generation, cell, "
                        "knobs_digest, regime, n_pop, g_budget, e_episodes, strata, best_train_max, heldout, "
                        "first_foothold_gen, first_solved_gen, first_shelf_gen, summit_candidate_gen, first_summit_gen, "
                        "stopped_on_solve, summit_censored, level_as_written, reached, source_cell, target_cell, "
                        "source_competence, direct_reuse_best, edge_kind, termination_reason, horizon, censored, "
                        "censoring_reason, measured, definition_version, producer_row_digest, origin_kind, "
                        "source_commit, source_path, source_line, source_blob_sha, reader_version, recorded_at, "
                        "ingested_at FROM ew.campaign_observations WHERE " + " AND ".join(where) +
                        " ORDER BY campaign_id, harness_id, attempt_id, kind, generation NULLS FIRST, observation_id "
                        "LIMIT %s", args + [min(max(limit, 1), 2000)])
            rows = _rows(cur)
        log_read(conn, "campaign.observations", ident,
                 {"campaign_id": campaign_id, "harness_id": harness_id, "attempt_id": attempt_id, "kind": kind,
                  "cell": cell, "stratum": stratum}, len(rows), t0)
        conn.commit()
        return {"n": len(rows), "observations": rows,
                "note": "level_as_written and disposition_candidate are the PRODUCER's labels at definition_version; "
                        "PEW derives nothing on this route (projections are under /api/v1/projections)"}

    @app.get("/api/v1/campaign/summary")
    def campaign_summary(request: Request, campaign_id: str, conn=Depends(get_conn)):
        t0 = time.time()
        ident = identity(request)
        with conn.cursor() as cur:
            cur.execute("SELECT kind, count(*) FROM ew.campaign_observations WHERE campaign_id=%s GROUP BY 1 ORDER BY 1", (campaign_id,))
            by_kind = dict(cur.fetchall())
            cur.execute("SELECT harness_id, count(DISTINCT attempt_id) FILTER (WHERE attempt_id IS NOT NULL AND attempt_id<>'UNKNOWN'), "
                        "count(*) FROM ew.campaign_observations WHERE campaign_id=%s GROUP BY 1 ORDER BY 1", (campaign_id,))
            harnesses = [{"harness_id": h, "attempts": a, "observations": n} for h, a, n in cur.fetchall()]
            unknown = {}
            for col in ("harness_id", "attempt_id", "design_id", "engine_instance_id", "foundry_profile", "world_id", "rng_identity"):
                cur.execute(f"SELECT count(*) FROM ew.campaign_observations WHERE campaign_id=%s AND {col}='UNKNOWN'", (campaign_id,))
                unknown[col] = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM ew.campaign_observations WHERE campaign_id=%s AND origin_kind='reconstructed'", (campaign_id,))
            reconstructed = cur.fetchone()[0]
            cur.execute("SELECT DISTINCT source_commit FROM ew.campaign_observations WHERE campaign_id=%s", (campaign_id,))
            commits = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT count(*) FROM ew.campaign_observations WHERE campaign_id=%s AND kind='reachability' AND summit_censored", (campaign_id,))
            censored = cur.fetchone()[0]
        out = {"campaign_id": campaign_id, "observations_by_kind": by_kind, "harnesses": harnesses,
               "unknown_identity_counts": unknown, "reconstructed_rows": reconstructed,
               "source_commits": commits, "reachability_rows_censored_before_summit": censored}
        log_read(conn, "campaign.summary", ident, {"campaign_id": campaign_id}, sum(by_kind.values()), t0)
        conn.commit()
        return out

    @app.get("/api/v1/projections")
    def projections_list(request: Request, conn=Depends(get_conn)):
        identity(request)
        with conn.cursor() as cur:
            cur.execute("SELECT projection_name, projection_version, definition, source_kinds, source_code_identity, "
                        "thresholds, owner_seat, builder_version, built_at, evidence_count, rebuild_digest, limitations, "
                        "status FROM ew.projections ORDER BY 1, 2")
            rows = _rows(cur)
        return {"n": len(rows), "projections": rows, "builder_version": BUILDER_VERSION}

    @app.get("/api/v1/projections/{name}/{version}")
    def projection_rows(name: str, version: str, request: Request, row_key_prefix: str | None = None,
                        stratum: str | None = None, limit: int = 500, conn=Depends(get_conn)):
        t0 = time.time()
        ident = identity(request)
        with conn.cursor() as cur:
            cur.execute("SELECT projection_name, projection_version, definition, source_kinds, source_code_identity, "
                        "thresholds, owner_seat, builder_version, built_at, evidence_count, rebuild_digest, limitations, "
                        "status FROM ew.projections WHERE projection_name=%s AND projection_version=%s", (name, version))
            reg = _rows(cur)
            if not reg:
                raise HTTPException(404, f"unknown projection {name}/{version}")
            where, args = ["projection_name=%s", "projection_version=%s"], [name, version]
            if row_key_prefix:
                where.append("row_key LIKE %s"); args.append(row_key_prefix + "%")
            if stratum is not None:
                try:
                    st = json.loads(stratum)
                except ValueError:
                    raise HTTPException(422, "stratum_not_json")
                where.append("payload @> %s::jsonb"); args.append(json.dumps(st))
            cur.execute("SELECT row_key, payload, evidence_ids, evidence_count, built_at FROM ew.projection_rows WHERE "
                        + " AND ".join(where) + " ORDER BY row_key LIMIT %s", args + [min(max(limit, 1), 5000)])
            rows = _rows(cur)
        log_read(conn, "projections.rows", ident, {"name": name, "version": version, "prefix": row_key_prefix,
                                                  "stratum": stratum}, len(rows), t0)
        conn.commit()
        return {"projection": reg[0], "n": len(rows), "rows": rows}

    @app.get("/api/v1/ingestion/checkpoints")
    def ingestion_checkpoints(request: Request, producer: str | None = None, conn=Depends(get_conn)):
        identity(request)
        with conn.cursor() as cur:
            if producer:
                cur.execute("SELECT * FROM ew.ingestion_checkpoints WHERE producer=%s ORDER BY stream", (producer,))
            else:
                cur.execute("SELECT * FROM ew.ingestion_checkpoints ORDER BY producer, stream")
            rows = _rows(cur)
        return {"n": len(rows), "checkpoints": rows}

    @app.get("/api/v1/ingestion/conflicts")
    def ingestion_conflicts(request: Request, producer: str | None = None, limit: int = 200, conn=Depends(get_conn)):
        identity(request)
        with conn.cursor() as cur:
            if producer:
                cur.execute("SELECT * FROM ew.ingestion_conflicts WHERE producer=%s ORDER BY conflict_id DESC LIMIT %s", (producer, limit))
            else:
                cur.execute("SELECT * FROM ew.ingestion_conflicts ORDER BY conflict_id DESC LIMIT %s", (limit,))
            rows = _rows(cur)
        return {"n": len(rows), "conflicts": rows}

    # ------------------------------------------------------------ events
    def _ingest_event(cur, ev: ProducerEventIn, ident):
        pd = "sha256:" + hashlib.sha256(canon(ev.payload).encode()).hexdigest()
        cur.execute("SELECT event_id, payload_digest, seq FROM ew.producer_events WHERE event_id=%s OR (producer=%s AND stream=%s AND seq=%s)",
                    (ev.event_id, ev.producer, ev.stream, ev.seq))
        existing = cur.fetchall()
        cur.execute("SELECT last_seq FROM ew.ingestion_checkpoints WHERE producer=%s AND stream=%s", (ev.producer, ev.stream))
        cp = cur.fetchone()
        last_seq = cp[0] if cp else None
        if existing:
            if any(e[1] == pd for e in existing):
                return {"event_id": ev.event_id, "status": "duplicate", "gap": False, "checkpoint_seq": last_seq}
            cur.execute("INSERT INTO ew.ingestion_conflicts(producer, stream, seq, stored_digest, offered_digest, "
                        "stored_observation_id, note) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (ev.producer, ev.stream, ev.seq, existing[0][1], pd, existing[0][0],
                         "same (producer, stream, seq) or event_id with a different payload digest; refused, stored row untouched"))
            return {"event_id": ev.event_id, "status": "checkpoint_mismatch", "gap": False, "checkpoint_seq": last_seq,
                    "stored_digest": existing[0][1], "offered_digest": pd}
        gap = last_seq is not None and ev.seq > last_seq + 1
        cur.execute("SELECT nextval('ew.canonical_revision_seq')")
        rev = cur.fetchone()[0]
        cur.execute("INSERT INTO ew.producer_events(event_id, producer, stream, seq, kind, logical_time, actor, payload, "
                    "payload_digest, envelope, machine, agent, revision) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (ev.event_id, ev.producer, ev.stream, ev.seq, ev.kind, ev.logical_time, ev.actor,
                     json.dumps(ev.payload, default=str), pd, json.dumps(ev.envelope, default=str) if ev.envelope is not None else None,
                     ident["machine"], ident["agent"], rev))
        gaps_add = json.dumps([{"from": last_seq + 1, "to": ev.seq - 1, "seen_at": time.strftime("%Y-%m-%dT%H:%M:%S")}]) if gap else "[]"
        new_last = ev.seq if (last_seq is None or ev.seq > last_seq) else last_seq
        cur.execute("INSERT INTO ew.ingestion_checkpoints(producer, stream, last_seq, last_event_id, last_digest, rows_seen, rows_new, gaps, updated_at) "
                    "VALUES (%s,%s,%s,%s,%s,1,1,%s::jsonb,now()) ON CONFLICT (producer, stream) DO UPDATE SET "
                    "last_seq=%s, last_event_id=CASE WHEN %s>=COALESCE(ew.ingestion_checkpoints.last_seq,-1) THEN EXCLUDED.last_event_id ELSE ew.ingestion_checkpoints.last_event_id END, "
                    "last_digest=EXCLUDED.last_digest, rows_seen=ew.ingestion_checkpoints.rows_seen+1, rows_new=ew.ingestion_checkpoints.rows_new+1, "
                    "gaps=ew.ingestion_checkpoints.gaps || %s::jsonb, updated_at=now()",
                    (ev.producer, ev.stream, ev.seq, ev.event_id, pd, gaps_add, new_last, ev.seq, gaps_add))
        cur.execute("INSERT INTO ew.write_log(endpoint, machine, agent, payload_sha256, accepted, result_object_id) "
                    "VALUES ('events', %s, %s, %s, true, %s)", (ident["machine"], ident["agent"], pd[7:], ev.event_id))
        return {"event_id": ev.event_id, "status": "accepted", "gap": gap, "checkpoint_seq": new_last,
                "late": bool(last_seq is not None and ev.seq < last_seq)}

    @app.post("/api/v1/events")
    def post_events(body: ProducerEventIn | list[ProducerEventIn], request: Request, conn=Depends(get_conn)):
        ident = identity(request, write=True)
        events = body if isinstance(body, list) else [body]
        results = []
        with conn.cursor() as cur:
            for ev in events:
                if not ev.event_id or not ev.kind or ev.seq < 0:
                    results.append({"event_id": ev.event_id, "status": "rejected_malformed", "gap": False})
                    continue
                results.append(_ingest_event(cur, ev, ident))
        conn.commit()
        return {"n": len(results), "results": results if isinstance(body, list) else results[0]}

    @app.get("/api/v1/events")
    def get_events(request: Request, producer: str, stream: str | None = None, after_seq: int = -1,
                   kind: str | None = None, limit: int = 500, conn=Depends(get_conn)):
        t0 = time.time()
        ident = identity(request)
        where, args = ["producer=%s", "seq>%s"], [producer, after_seq]
        if stream:
            where.append("stream=%s"); args.append(stream)
        if kind:
            where.append("kind=%s"); args.append(kind)
        with conn.cursor() as cur:
            cur.execute("SELECT event_id, producer, stream, seq, kind, logical_time, actor, payload, payload_digest, envelope, "
                        "received_at, machine, agent FROM ew.producer_events WHERE " + " AND ".join(where) +
                        " ORDER BY stream, seq LIMIT %s", args + [min(max(limit, 1), 5000)])
            rows = _rows(cur)
        log_read(conn, "events", ident, {"producer": producer, "stream": stream, "after_seq": after_seq, "kind": kind}, len(rows), t0)
        conn.commit()
        return {"n": len(rows), "events": rows, "next_after_seq": rows[-1]["seq"] if rows else None}

    @app.get("/api/v1/release")
    def release_identity(request: Request, conn=Depends(get_conn)):
        """The machine-readable half of a restart receipt (order s16)."""
        identity(request)
        with conn.cursor() as cur:
            cur.execute("SELECT migration_id, applied_at, backup_id FROM ew.schema_migrations ORDER BY 1")
            migs = [{"migration_id": m, "applied_at": str(a), "backup_id": b} for m, a, b in cur.fetchall()]
            cur.execute("SELECT max(version) FROM ew.ontology_versions")
            onto_registry = cur.fetchone()[0]
            cur.execute("SELECT projection_name, projection_version, rebuild_digest FROM ew.projections ORDER BY 1, 2")
            projs = cur.fetchall()
            cur.execute("SELECT system_identifier::text, current_database() FROM pg_control_system()")
            sysid, dbname = cur.fetchone()
        routes = sorted(f"{list(r.methods)[0] if r.methods else ''} {r.path}" for r in app.routes if hasattr(r, "path"))
        return {"schema_version_constant": SCHEMA_VERSION, "ontology_version_constant": ONTOLOGY_VERSION,
                "ontology_registry_version": onto_registry, "fossil_contract": FOSSIL_CONTRACT_VERSION,
                "migrations_applied": migs, "reader_version": READER_VERSION, "ingestion_contract": CONTRACT_VERSION,
                "projection_builder": BUILDER_VERSION,
                "projection_registry_digest": "sha256:" + hashlib.sha256(canon([list(p) for p in projs]).encode()).hexdigest(),
                "projections": [{"name": p[0], "version": p[1], "rebuild_digest": p[2]} for p in projs],
                "route_digest": "sha256:" + hashlib.sha256("\n".join(routes).encode()).hexdigest(),
                "routes": routes, "db_system_id": sysid, "db_name": dbname}
