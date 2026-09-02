"""Metabolize real SFE history into the PEW fossil record (charter s9/s10).

Every fossil row REFERENCES authoritative SFE identity (entry_hash /
content-hash artifact ids); nothing authoritative is copied or mutated.
SFE is opened READ-ONLY. Ingest is idempotent (ON CONFLICT DO NOTHING on
stable ids). Namespace 'prod' = real history.
"""
import json
import sqlite3
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew import db as ewdb  # noqa: E402

SFE = HERE.parent / "SerendipityFoundry" / "SerendipityFoundryEngine" / "var" / "engine.db"


def family_of(name, topo):
    if topo:
        return f"topo:{topo}"
    if not name:
        return "unnamed"
    return name.split("_")[0].split("-")[0][:24].lower()


def main():
    t0 = time.time()
    sfe = sqlite3.connect(f"file:{SFE}?mode=ro", uri=True)
    sfe.row_factory = sqlite3.Row
    conn = ewdb.connect()
    cur = conn.cursor()
    scur = sfe.cursor()

    n_worlds = n_edges = n_players = n_enc = 0

    # -------- worlds + fork lineage
    for w in scur.execute("SELECT * FROM worlds"):
        cur.execute("SELECT nextval('ew.canonical_revision_seq')")
        rev = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO ew.fossil_worlds(world_id, manifest_hash, parent_world, "
            "sfe_world_id, sfe_head_hash, family, namespace, revision) "
            "VALUES (%s,%s,%s,%s,%s,%s,'prod',%s) ON CONFLICT DO NOTHING",
            (w["world_id"], w["head_hash"], w["parent_world_id"], w["world_id"],
             w["head_hash"], family_of(w["name"], w["topology_group"]), rev))
        n_worlds += 1
        if w["parent_world_id"]:
            cur.execute("SELECT nextval('ew.canonical_revision_seq')")
            rev = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO ew.fossil_edges(edge_id, src_kind, src_id, dst_kind, "
                "dst_id, relation, sfe_entry_hash, namespace, revision) "
                "VALUES (%s,'world',%s,'world',%s,'FORK',%s,'prod',%s) "
                "ON CONFLICT DO NOTHING",
                (f"FE-fork-{w['world_id'][:20]}", w["parent_world_id"],
                 w["world_id"], w["head_hash"], rev))
            n_edges += 1

    # -------- players from candidate artifacts (content-hash identity)
    for a in scur.execute("SELECT * FROM artifacts WHERE kind='cand'"):
        meta = json.loads(a["meta"]) if a["meta"] else {}
        cur.execute("SELECT nextval('ew.canonical_revision_seq')")
        rev = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO ew.fossil_players(player_id, genome_hash, sfe_world_id, "
            "sfe_entry_hash, phenotype, namespace, revision) "
            "VALUES (%s,%s,%s,%s,%s,'prod',%s) ON CONFLICT DO NOTHING",
            (a["artifact_id"], a["blob_hash"], a["world_id"], a["artifact_id"],
             json.dumps({"score": meta.get("score"),
                         "info_kind": meta.get("info_kind"),
                         "candidate": meta.get("candidate")}), rev))
        n_players += 1

    # -------- encounters from ledger events (true entry hashes)
    for e in scur.execute(
            "SELECT world_id, event_id, event_type, entry_hash, payload, ts "
            "FROM events WHERE event_type IN "
            "('FAILURE_RECORDED','EXPERIMENT_COMMITTED')"):
        p = json.loads(e["payload"]) if e["payload"] else {}
        outcome = (p.get("failure_type") if e["event_type"] == "FAILURE_RECORDED"
                   else "committed")
        cur.execute("SELECT nextval('ew.canonical_revision_seq')")
        rev = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO ew.fossil_encounters(encounter_id, sfe_world_id, "
            "sfe_event_id, sfe_entry_hash, world_id, outcome, failure_class, "
            "occurred_ts, namespace, revision) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,to_timestamp(%s),'prod',%s) "
            "ON CONFLICT DO NOTHING",
            (f"ENC-{e['event_id']}", e["world_id"], e["event_id"],
             e["entry_hash"], e["world_id"], outcome,
             p.get("failure_type"), (e["ts"] or 0), rev))
        n_enc += 1

    conn.commit()
    dt = time.time() - t0
    total = n_worlds + n_edges + n_players + n_enc
    print(json.dumps({"worlds": n_worlds, "fork_edges": n_edges,
                      "players": n_players, "encounters": n_enc,
                      "seconds": round(dt, 1),
                      "rows_per_sec": round(total / dt, 1)}))
    sfe.close()
    conn.close()


if __name__ == "__main__":
    main()
