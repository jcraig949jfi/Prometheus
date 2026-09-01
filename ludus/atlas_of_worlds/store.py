"""SQLite store for the Atlas of Game Worlds.

One row per world. List-valued fields are JSON text. Everything is idempotent on
`qid` (Wikidata) or `slug` (hand-seeded worlds), so a tick can be re-run safely
and the crawler can be killed at any point without corrupting state.
"""
from __future__ import annotations

import json
import pathlib
import re
import sqlite3
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
DB = HERE / "atlas.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS worlds (
  id                INTEGER PRIMARY KEY,
  slug              TEXT UNIQUE NOT NULL,
  name              TEXT NOT NULL,
  aliases           TEXT DEFAULT '[]',
  qid               TEXT UNIQUE,
  wp_title          TEXT,
  description       TEXT,

  -- temporal
  year_created      INTEGER,
  year_precision    TEXT,
  epoch             TEXT,

  -- cultural
  country           TEXT,
  region            TEXT,

  -- found layer (recorded, never trusted as structure)
  genres            TEXT DEFAULT '[]',
  instances         TEXT DEFAULT '[]',

  -- medium / audience
  media             TEXT DEFAULT '[]',
  min_age           INTEGER,
  age_band          TEXT,
  players_min       INTEGER,
  players_max       INTEGER,
  players_notation  TEXT,
  solitaire_capable INTEGER,
  team_play         INTEGER,

  -- difficulty / complexity
  rules_complexity  REAL,
  strategic_depth   REAL,
  state_space_log10 REAL,
  branching_factor  REAL,
  length_minutes    INTEGER,
  information_score REAL,

  -- chance
  luck_factor       REAL,
  randomness_sources TEXT DEFAULT '[]',

  -- information / interaction
  information       TEXT,
  interaction       TEXT,
  zero_sum          INTEGER,
  turn_structure    TEXT,

  -- declared structure (bench layer B)
  exogenous_process TEXT,
  loss_shape        TEXT,
  live_axes         TEXT DEFAULT '[]',
  horizon           TEXT,
  scoring_shape     TEXT,
  tractability      TEXT,

  -- strategy / algorithms
  strategies        TEXT DEFAULT '[]',
  algorithms        TEXT DEFAULT '[]',
  solved_status     TEXT,

  -- scoring for active selection
  novelty           REAL,
  complexity_score  REAL,

  -- bookkeeping
  catalog_state     TEXT DEFAULT 'CATALOGUED',
  method            TEXT DEFAULT 'heuristic',
  sources           TEXT DEFAULT '[]',
  wp_extract        TEXT,
  probe             TEXT,
  tick_added        INTEGER,
  first_seen        TEXT,
  last_updated      TEXT,
  -- When the full article was fetched. NULL means never attempted.
  -- This must be tracked explicitly rather than inferred from the length of
  -- wp_extract: many real articles are genuinely short (Towie is 401
  -- characters, Adji-boto 798), so a length test re-selects them on every tick
  -- forever, burning the enrichment budget while never-fetched worlds wait.
  enriched_ts       TEXT
);

CREATE INDEX IF NOT EXISTS ix_worlds_state  ON worlds(catalog_state);
CREATE INDEX IF NOT EXISTS ix_worlds_epoch  ON worlds(epoch);
CREATE INDEX IF NOT EXISTS ix_worlds_region ON worlds(region);
CREATE INDEX IF NOT EXISTS ix_worlds_nov    ON worlds(novelty);

-- lineage: variants, expansions, ancestors, regional cousins
CREATE TABLE IF NOT EXISTS relations (
  id   INTEGER PRIMARY KEY,
  src  TEXT NOT NULL,
  dst  TEXT NOT NULL,
  kind TEXT NOT NULL,          -- BASED_ON | VARIANT_OF | EXPANSION_OF | SUBCLASS_OF
                               -- | REGIONAL_COUSIN | INFLUENCED_BY | SAME_FAMILY
  note TEXT,
  UNIQUE(src, dst, kind)
);

-- the 'five fouls and you are benched' layer
CREATE TABLE IF NOT EXISTS conditions (
  id        INTEGER PRIMARY KEY,
  slug      TEXT NOT NULL,
  kind      TEXT NOT NULL,     -- taxonomy.CONDITION_KINDS
  trigger   TEXT NOT NULL,
  threshold TEXT,
  effect    TEXT,
  method    TEXT DEFAULT 'reviewed',
  UNIQUE(slug, kind, trigger)
);

-- per-world deep artifacts: turn trace, state transition diagram, object model
CREATE TABLE IF NOT EXISTS artifacts (
  id   INTEGER PRIMARY KEY,
  slug TEXT NOT NULL,
  kind TEXT NOT NULL,          -- TURN_TRACE | CLOCK_TRACE | STATE_DIAGRAM
                               -- | OBJECT_MODEL | DOSSIER
  body TEXT NOT NULL,
  ts   TEXT,
  UNIQUE(slug, kind)
);

-- provenance for hand review. The method ladder (heuristic -> source ->
-- reviewed -> audited) was decorative until this existed: nothing could set
-- anything above 'heuristic'. Some cells are simply not recoverable from
-- source prose -- the word "simultaneous" appears nowhere in the Wikipedia
-- articles for 7 Wonders or Pandemic -- so a reviewed value is the only way
-- they can ever be filled correctly. Every one is attributed and dated.
CREATE TABLE IF NOT EXISTS reviews (
  id       INTEGER PRIMARY KEY,
  slug     TEXT NOT NULL,
  field    TEXT NOT NULL,
  old_value TEXT,
  value    TEXT NOT NULL,
  note     TEXT,
  reviewer TEXT,
  ts       TEXT
);
CREATE INDEX IF NOT EXISTS ix_reviews_slug ON reviews(slug);

CREATE TABLE IF NOT EXISTS ticks (
  n          INTEGER PRIMARY KEY,
  ts         TEXT,
  probes     TEXT,
  harvested  INTEGER,
  new_worlds INTEGER,
  classified INTEGER,
  deepened   INTEGER,
  note       TEXT
);

CREATE TABLE IF NOT EXISTS probe_state (
  probe     TEXT PRIMARY KEY,
  offset    INTEGER DEFAULT 0,
  exhausted INTEGER DEFAULT 0,
  runs      INTEGER DEFAULT 0,
  yielded   INTEGER DEFAULT 0,
  last_run  TEXT
);
"""

LIST_FIELDS = {
    "aliases", "genres", "instances", "media", "randomness_sources",
    "live_axes", "strategies", "algorithms", "sources",
}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "_", (name or "").lower()).strip("_")
    return s or "unnamed"


def connect(path=DB):
    con = sqlite3.connect(str(path), timeout=60)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.executescript(SCHEMA)
    _migrate(con)
    return con


def _migrate(con):
    """Add columns introduced after a database already existed.

    CREATE TABLE IF NOT EXISTS silently does nothing to an existing table, so
    new columns need an explicit ALTER. Idempotent: duplicate-column errors are
    the expected no-op.
    """
    have = {r[1] for r in con.execute("PRAGMA table_info(worlds)")}
    for col, decl in [("enriched_ts", "TEXT")]:
        if col not in have:
            con.execute("ALTER TABLE worlds ADD COLUMN %s %s" % (col, decl))
            # Backfill: anything past CATALOGUED has already had its article
            # fetched, so mark it done rather than re-fetching 200+ worlds.
            if col == "enriched_ts":
                con.execute(
                    "UPDATE worlds SET enriched_ts = COALESCE(last_updated, ?)"
                    " WHERE catalog_state IN ('SPECIFIED','DEEPENED',"
                    "                         'IMPLEMENTED','AUDITED')", (now(),))
            con.commit()


def _enc(rec):
    out = {}
    for k, v in rec.items():
        if k in LIST_FIELDS and not isinstance(v, str):
            out[k] = json.dumps(sorted(set(v or [])), ensure_ascii=False)
        elif isinstance(v, bool):
            out[k] = int(v)
        else:
            out[k] = v
    return out


def dec(row):
    d = dict(row)
    for k in LIST_FIELDS:
        if k in d and isinstance(d[k], str):
            try:
                d[k] = json.loads(d[k])
            except Exception:                                   # noqa: BLE001
                d[k] = []
    return d


def upsert_world(con, rec):
    """Insert or merge one world. Returns (slug, is_new).

    Merge policy: a non-null incoming value overwrites a null stored value.
    A stored value produced by a stronger method is never overwritten by a
    weaker one -- reviewed beats heuristic, always.
    """
    rec = dict(rec)
    rec.setdefault("slug", slugify(rec.get("name")))
    slug, qid = rec["slug"], rec.get("qid")

    cur = con.execute("SELECT * FROM worlds WHERE qid IS NOT NULL AND qid = ?", (qid,)) if qid else None
    row = cur.fetchone() if cur else None
    if row is None:
        row = con.execute("SELECT * FROM worlds WHERE slug = ?", (slug,)).fetchone()

    rec = _enc(rec)
    if row is None:
        # de-collide slugs
        if con.execute("SELECT 1 FROM worlds WHERE slug = ?", (slug,)).fetchone():
            slug = "%s_%s" % (slug, (qid or now())[-6:].lower())
            rec["slug"] = slug
        rec["first_seen"] = rec["last_updated"] = now()
        cols = ", ".join(rec)
        con.execute("INSERT INTO worlds (%s) VALUES (%s)"
                    % (cols, ", ".join("?" * len(rec))), list(rec.values()))
        return slug, True

    stored = dict(row)
    strength = {"heuristic": 0, "source": 1, "reviewed": 2, "audited": 3}
    incoming_m = strength.get(rec.get("method", "heuristic"), 0)
    stored_m = strength.get(stored.get("method") or "heuristic", 0)

    upd = {}
    for k, v in rec.items():
        if k in ("slug", "first_seen", "id"):
            continue
        if v in (None, "", "[]"):
            continue
        if stored.get(k) in (None, "", "[]"):
            upd[k] = v
        elif incoming_m >= stored_m:
            upd[k] = v
    if upd:
        upd["last_updated"] = now()
        con.execute("UPDATE worlds SET %s WHERE id = ?"
                    % ", ".join("%s = ?" % k for k in upd),
                    list(upd.values()) + [stored["id"]])
    return stored["slug"], False


def add_relation(con, src, dst, kind, note=None):
    con.execute("INSERT OR IGNORE INTO relations (src, dst, kind, note) VALUES (?,?,?,?)",
                (src, dst, kind, note))


def add_condition(con, slug, kind, trigger, threshold=None, effect=None, method="reviewed"):
    con.execute(
        "INSERT OR IGNORE INTO conditions (slug, kind, trigger, threshold, effect, method)"
        " VALUES (?,?,?,?,?,?)", (slug, kind, trigger, threshold, effect, method))


def put_artifact(con, slug, kind, body):
    con.execute(
        "INSERT INTO artifacts (slug, kind, body, ts) VALUES (?,?,?,?)"
        " ON CONFLICT(slug, kind) DO UPDATE SET body=excluded.body, ts=excluded.ts",
        (slug, kind, body, now()))


def probe_cursor(con, probe):
    row = con.execute("SELECT * FROM probe_state WHERE probe = ?", (probe,)).fetchone()
    if row is None:
        con.execute("INSERT INTO probe_state (probe) VALUES (?)", (probe,))
        return {"probe": probe, "offset": 0, "exhausted": 0, "runs": 0, "yielded": 0}
    return dict(row)


def probe_advance(con, probe, got, limit):
    con.execute(
        "UPDATE probe_state SET offset = offset + ?, runs = runs + 1,"
        " yielded = yielded + ?, exhausted = ?, last_run = ? WHERE probe = ?",
        (got, got, 1 if got < limit else 0, now(), probe))


def next_tick(con):
    r = con.execute("SELECT COALESCE(MAX(n), 0) + 1 AS n FROM ticks").fetchone()
    return r["n"]


def record_tick(con, n, probes, harvested, new_worlds, classified, deepened, note=""):
    con.execute(
        "INSERT OR REPLACE INTO ticks (n, ts, probes, harvested, new_worlds,"
        " classified, deepened, note) VALUES (?,?,?,?,?,?,?,?)",
        (n, now(), json.dumps(probes), harvested, new_worlds, classified, deepened, note))


def counts(con):
    q = lambda s, *a: con.execute(s, a).fetchone()[0]           # noqa: E731
    return {
        "worlds": q("SELECT COUNT(*) FROM worlds"),
        "relations": q("SELECT COUNT(*) FROM relations"),
        "conditions": q("SELECT COUNT(*) FROM conditions"),
        "artifacts": q("SELECT COUNT(*) FROM artifacts"),
        "ticks": q("SELECT COUNT(*) FROM ticks"),
        "deepened": q("SELECT COUNT(*) FROM worlds WHERE catalog_state = 'DEEPENED'"),
        "specified": q("SELECT COUNT(*) FROM worlds WHERE catalog_state = 'SPECIFIED'"),
    }


if __name__ == "__main__":
    con = connect()
    print("db:", DB)
    print(counts(con))
