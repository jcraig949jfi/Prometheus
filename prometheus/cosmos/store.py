"""The world graph and the law ledger (SQLite, append-mostly), plus a receipt chain.

Tables
  nodes(world_id, family, lineage, params, coords_v1, coords_v2, origin)
  edges(src, dst, kind, delta)       kind: DEFORMATION_OF | COORD_PRESERVING | CONTROL_OF |
                                           TRANSPLANT_OF | INTERVENTION
  runs(world_id, replicate, seed, episodes, obs_digest, verdict, margin, margin_se, purpose, code_sha)
  laws(law_id, version, parent, body, freeze_hash)         a law row is immutable once written
  law_events(law_id, status, note)                          lifecycle: PROPOSED ATTACKED REVISED
                                                            FROZEN HOLDOUT_TESTED INTERVENTION_TESTED
                                                            FAILED SURVIVED RETIRED
Nothing is ever deleted. A revised law is a new row with parent = predecessor.
Edge vocabulary matches atlas.edge (DEFORMATION_OF, TRANSPLANT_OF) so an Atlas harvest
adapter can map rows 1:1 later; Atlas is not required online.
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from prometheus.cosmos.hashing import ReceiptChain, canon, h

EDGE_KINDS = ("DEFORMATION_OF", "COORD_PRESERVING", "CONTROL_OF", "TRANSPLANT_OF", "INTERVENTION")
LAW_STATES = ("PROPOSED", "ATTACKED", "REVISED", "FROZEN", "HOLDOUT_TESTED", "INTERVENTION_TESTED",
              "FAILED", "SURVIVED", "RETIRED")

SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes(world_id TEXT PRIMARY KEY, family TEXT, lineage TEXT, params TEXT,
    coords_v1 TEXT, coords_v2 TEXT, origin TEXT, t REAL);
CREATE TABLE IF NOT EXISTS edges(src TEXT, dst TEXT, kind TEXT, delta TEXT, t REAL,
    PRIMARY KEY(src, dst, kind));
CREATE TABLE IF NOT EXISTS runs(world_id TEXT, replicate INTEGER, seed INTEGER, episodes INTEGER,
    obs_digest TEXT, verdict TEXT, margin REAL, margin_se REAL, purpose TEXT, code_sha TEXT, t REAL,
    PRIMARY KEY(world_id, replicate, episodes));
CREATE TABLE IF NOT EXISTS laws(law_id TEXT PRIMARY KEY, version INTEGER, parent TEXT, body TEXT,
    freeze_hash TEXT, t REAL);
CREATE TABLE IF NOT EXISTS law_events(law_id TEXT, status TEXT, note TEXT, t REAL);
"""


class Store:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.root / "cwe.sqlite"))
        self.db.executescript(SCHEMA)
        self.receipts = ReceiptChain(self.root / "receipts.jsonl")

    # ---- graph
    def add_node(self, world_id, family, lineage, params, coords_v1, coords_v2, origin) -> None:
        self.db.execute("INSERT OR IGNORE INTO nodes VALUES(?,?,?,?,?,?,?,?)",
                        (world_id, family, lineage, canon(params), canon(coords_v1), canon(coords_v2), origin, time.time()))

    def add_edge(self, src, dst, kind, delta) -> None:
        if kind not in EDGE_KINDS:
            raise ValueError(kind)
        if src == dst:
            raise ValueError("self-edge: a transformation must change the world")
        self.db.execute("INSERT OR IGNORE INTO edges VALUES(?,?,?,?,?)", (src, dst, kind, canon(delta), time.time()))

    def add_run(self, rec: Dict[str, Any], purpose: str, code_sha: str) -> None:
        self.db.execute("INSERT OR IGNORE INTO runs VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                        (rec["world_id"], rec["replicate"], rec["seed"], rec["episodes"], rec["obs_digest"],
                         rec["verdict"], rec["margin"], rec["margin_se"], purpose, code_sha, time.time()))

    def counts(self) -> Dict[str, int]:
        q = lambda s: self.db.execute(s).fetchone()[0]
        return {"nodes": q("SELECT COUNT(*) FROM nodes"), "edges": q("SELECT COUNT(*) FROM edges"),
                "runs": q("SELECT COUNT(*) FROM runs"), "families": q("SELECT COUNT(DISTINCT family) FROM nodes"),
                "laws": q("SELECT COUNT(*) FROM laws")}

    def edge_counts(self) -> Dict[str, int]:
        return dict(self.db.execute("SELECT kind, COUNT(*) FROM edges GROUP BY kind").fetchall())

    # ---- laws
    def propose_law(self, body: Dict[str, Any], parent: Optional[str] = None, note: str = "") -> str:
        version = 1
        if parent:
            version = self.db.execute("SELECT version FROM laws WHERE law_id=?", (parent,)).fetchone()[0] + 1
        law_id = h({"body": body, "parent": parent})[:20]
        self.db.execute("INSERT OR IGNORE INTO laws VALUES(?,?,?,?,?,?)",
                        (law_id, version, parent, canon(body), None, time.time()))
        self.event(law_id, "PROPOSED", note)
        if parent:
            self.event(parent, "REVISED", "superseded by %s" % law_id)
        return law_id

    def freeze_law(self, law_id: str) -> str:
        row = self.db.execute("SELECT body, parent, freeze_hash FROM laws WHERE law_id=?", (law_id,)).fetchone()
        if row[2]:
            return row[2]
        fh = h({"law_id": law_id, "body": json.loads(row[0]), "parent": row[1]})
        self.db.execute("UPDATE laws SET freeze_hash=? WHERE law_id=? AND freeze_hash IS NULL", (fh, law_id))
        self.event(law_id, "FROZEN", fh)
        self.receipts.append("law_frozen", {"law_id": law_id, "freeze_hash": fh})
        self.db.commit()
        return fh

    def event(self, law_id: str, status: str, note: str = "") -> None:
        if status not in LAW_STATES:
            raise ValueError(status)
        self.db.execute("INSERT INTO law_events VALUES(?,?,?,?)", (law_id, status, note, time.time()))

    def law(self, law_id: str) -> Dict[str, Any]:
        r = self.db.execute("SELECT law_id, version, parent, body, freeze_hash FROM laws WHERE law_id=?", (law_id,)).fetchone()
        ev = self.db.execute("SELECT status, note FROM law_events WHERE law_id=? ORDER BY t", (law_id,)).fetchall()
        return {"law_id": r[0], "version": r[1], "parent": r[2], "body": json.loads(r[3]), "freeze_hash": r[4],
                "events": [{"status": s, "note": n} for s, n in ev]}

    def laws(self) -> List[Dict[str, Any]]:
        return [self.law(r[0]) for r in self.db.execute("SELECT law_id FROM laws ORDER BY t").fetchall()]

    def commit(self) -> None:
        self.db.commit()
