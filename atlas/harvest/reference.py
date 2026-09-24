"""Load atlas/registry.json into atlas.host and atlas.engine."""
from __future__ import annotations

from atlas import db

VERSION = "reference/2"


def run(args) -> dict:
    reg = db.registry()
    with db.harvest("reference", VERSION, source_ref="atlas/registry.json") as h:
        with h.conn.cursor() as cur:
            h.count("host", db.upsert(cur, "atlas.host", [
                {k: m.get(k) for k in ("host_id", "hostname", "lan_ip", "aliases", "roles", "evidence")}
                for m in reg["hosts"]], ["host_id"], h.id))
            h.count("engine", db.upsert(cur, "atlas.engine", [
                {k: e.get(k) for k in ("engine_id", "name", "kind", "code_paths", "owner_seats",
                                       "home_host", "status", "notes")}
                for e in reg["engines"]], ["engine_id"], h.id))
        return h.counts
