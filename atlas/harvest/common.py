"""Shared machinery for source adapters: a Batch that collects entities,
source pointers, facts, conclusions and edges in memory, then flushes them
in dependency order inside one harvest_run.

Identity rules (roles/Atlas/MODEL.md s3) are enforced here:
- entity keys are built only by the key helpers below, from native ids;
- a source's uri is its pointer identity (git:<path>[#record],
  file://<host>/<path>, pg://..., ledger://...);
- a fact's identity is (subject, kind, name, origin) hashed, so a re-harvest
  updates it in place and a recomb with a new variable adds rows.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from atlas import classify, db, gitsrc

REPO_NAME = "jcraig949jfi/Prometheus"
MAX_JSON = 2000          # facts keep small structured values inline; bigger ones stay behind the pointer
MAX_TEXT = 4000


def campaign_key(program: str, native: str) -> str:
    return "{}/{}".format(program, native)


def experiment_key(ckey: str, native: str) -> str:
    return "{}:{}".format(ckey, native)


def attempt_key(ekey: str, native: str) -> str:
    return "{}#{}".format(ekey, native)


def segment_key(akey: str, native: str) -> str:
    return "{}@{}".format(akey, native)


def h16(*parts: Any) -> str:
    return hashlib.sha256("\x1f".join(str(p) for p in parts).encode()).hexdigest()[:32]


def trunc(s: Optional[str], n: int = MAX_TEXT) -> Optional[str]:
    if s is None:
        return None
    s = str(s)
    return s if len(s) <= n else s[:n] + " [...truncated; see source]"


def flatten(obj: Any, prefix: str = "", depth: int = 3, limit: int = 120) -> List[Tuple[str, Any]]:
    """Leaves of a JSON document as (dotted path, value). Lists of scalars
    and small containers at max depth are kept whole."""
    out: List[Tuple[str, Any]] = []

    def walk(o, p, d):
        if len(out) >= limit:
            return
        if isinstance(o, dict) and d < depth and o:
            for k, v in o.items():
                walk(v, "{}.{}".format(p, k) if p else str(k), d + 1)
        else:
            out.append((p, o))
    walk(obj, prefix, 0)
    return out


def local_commits(cur) -> set:
    cur.execute("SELECT sha FROM atlas.git_commit WHERE seen_on_host IS NOT NULL")
    return {r[0] for r in cur.fetchall()}


class Batch:
    def __init__(self, harvester: str, version: str, author_default: str):
        self.method = "{}/{}".format(harvester, version) if "/" not in version else version
        self.author_default = author_default
        self.host = db.this_host()
        self.t: Dict[str, Dict[str, Dict[str, Any]]] = {k: {} for k in (
            "engine_instance", "campaign", "experiment", "attempt", "segment", "idea", "defect", "source")}
        self.links: List[Tuple[str, str, str, str]] = []
        self.facts: Dict[str, Dict[str, Any]] = {}
        self.fact_ev: List[Tuple[str, str, str]] = []
        self.concl: Dict[str, Dict[str, Any]] = {}
        self.edges: Dict[Tuple, Dict[str, Any]] = {}
        self.ecommits: set = set()
        self.local_shas: set = set()

    # entities --------------------------------------------------------------
    def put(self, table: str, key_col: str, row: Dict[str, Any]) -> str:
        k = row[key_col]
        cur = self.t[table].get(k)
        if cur is None:
            self.t[table][k] = dict(row)
        else:
            for c, v in row.items():
                if v is not None and v != [] and v != {}:
                    if isinstance(v, dict) and isinstance(cur.get(c), dict):
                        cur[c] = {**cur[c], **v}
                    elif isinstance(v, list) and isinstance(cur.get(c), list):
                        cur[c] = sorted(set(cur[c]) | set(v), key=str)
                    else:
                        cur[c] = v
        return k

    def campaign(self, **r) -> str:
        r.setdefault("seen_from_hosts", [self.host] if self.host else [])
        return self.put("campaign", "campaign_key", r)

    def experiment(self, **r) -> str:
        r.setdefault("seen_from_hosts", [self.host] if self.host else [])
        return self.put("experiment", "experiment_key", r)

    def attempt(self, **r) -> str:
        r.setdefault("seen_from_hosts", [self.host] if self.host else [])
        return self.put("attempt", "attempt_key", r)

    def segment(self, **r) -> str:
        return self.put("segment", "segment_key", r)

    def idea(self, **r) -> str:
        return self.put("idea", "idea_key", r)

    def defect(self, **r) -> str:
        return self.put("defect", "defect_key", r)

    def engine_instance(self, **r) -> str:
        r.setdefault("seen_from_hosts", [self.host] if self.host else [])
        return self.put("engine_instance", "engine_instance_key", r)

    # sources ---------------------------------------------------------------
    def git_source(self, ref: str, path: str, blob_sha: Optional[str], size: Optional[int],
                   newest: Optional[Tuple[str, str]] = None, oldest: Optional[Tuple[str, str]] = None,
                   obj: Any = None, text: Optional[str] = None, record_key: Optional[str] = None,
                   line: Optional[Tuple[int, int]] = None) -> str:
        uri = "git:{}".format(path) + ("#{}".format(record_key) if record_key else "")
        sha = newest[0] if newest else None
        vis = "GIT_LOCAL:{}".format(self.host) if sha and sha in self.local_shas else "GIT_REMOTE"
        keys, shp = db.shape(obj) if obj is not None else (None, None)
        rc = None
        if isinstance(obj, list):
            rc = len(obj)
        elif text is not None and path.endswith(".jsonl"):
            rc = sum(1 for x in text.splitlines() if x.strip())
        self.put("source", "uri", {
            "uri": uri, "kind": "git_blob", "repo": REPO_NAME, "ref": ref, "commit_sha": sha,
            "first_commit_sha": oldest[0] if oldest else None, "path": path, "blob_sha": blob_sha,
            "size_bytes": size, "mtime": newest[1] if newest else None, "record_key": record_key,
            "line_start": line[0] if line else None, "line_end": line[1] if line else None,
            "visibility": vis, "row_count": rc, "top_keys": keys, "shape_hash": shp, "present": True,
            "seen_from_hosts": [self.host] if self.host else []})
        return uri

    def other_source(self, uri: str, kind: str, visibility: str, **fields) -> str:
        row = {"uri": uri, "kind": kind, "visibility": visibility,
               "seen_from_hosts": [self.host] if self.host else []}
        row.update(fields)
        self.put("source", "uri", row)
        return uri

    def link(self, uri: str, etype: str, ekey: str, role: str) -> None:
        self.links.append((uri, etype, ekey, role))

    # facts / conclusions / edges -------------------------------------------
    def fact(self, layer: str, kind: str, stype: str, skey: str, name: str, value: Any,
             uri: Optional[str] = None, locator: str = "", author: Optional[str] = None,
             status: str = "REPORTED", unit: Optional[str] = None, band: Optional[Tuple[float, float]] = None,
             stated_at: Optional[str] = None) -> None:
        vt, vn = classify.scalar(value)
        vj = None
        if vt is None and value is not None:
            s = json.dumps(value, sort_keys=True, default=str)
            if len(s) <= MAX_JSON:
                vj = value
            else:
                vt = "<{} of {} items; see source>".format(type(value).__name__, len(value)) \
                    if hasattr(value, "__len__") else "<object; see source>"
        if value is None:
            status = "UNKNOWN" if status == "REPORTED" else status
        fk = h16(stype, skey, kind, name, uri or "", locator)
        self.facts[fk] = {"fact_key": fk, "layer": layer, "kind": kind, "subject_type": stype,
                          "subject_key": skey, "name": name[:300], "value_text": trunc(vt, MAX_TEXT),
                          "value_num": vn if vn is None or abs(vn) < 1e300 else None,
                          "value_json": vj, "band_low": band[0] if band else None,
                          "band_high": band[1] if band else None, "unit": unit, "status": status,
                          "author": author or self.author_default, "method": self.method,
                          "stated_at": stated_at}
        if uri:
            self.fact_ev.append((fk, uri, locator or ""))

    def conclusion(self, stype: str, skey: str, disposition: Optional[str], text: Optional[str],
                   uri: Optional[str], locator: str = "", author: Optional[str] = None,
                   stated_at: Optional[str] = None, status: str = "STANDING") -> None:
        if not disposition and not text:
            return
        ck = h16(stype, skey, author or self.author_default, uri or "", locator)
        self.concl[ck] = {"conclusion_key": ck, "subject_type": stype, "subject_key": skey,
                          "author": author or self.author_default, "disposition": trunc(disposition, 300),
                          "text_verbatim": trunc(text), "stated_at": stated_at, "status": status,
                          "_uri": uri, "locator": locator or None, "method": self.method}

    def edge(self, src: Tuple[str, str], dst: Tuple[str, str], relation: str, lineage_kind: str,
             reason: str = "UNKNOWN", basis: str = "DECLARED", confidence: str = "MEDIUM",
             detail: Optional[str] = None, uri: Optional[str] = None, locator: Optional[str] = None) -> None:
        if src == dst:
            return
        self.edges[(src[0], src[1], dst[0], dst[1], relation)] = {
            "src_type": src[0], "src_key": src[1], "dst_type": dst[0], "dst_key": dst[1],
            "relation": relation, "lineage_kind": lineage_kind, "reason": reason, "basis": basis,
            "confidence": confidence, "method": self.method, "detail": trunc(detail, 2000),
            "_uri": uri, "locator": locator}

    def commits(self, etype: str, ekey: str, shas: Iterable[str], basis: str = "PATH") -> None:
        for s in shas:
            self.ecommits.add((etype, ekey, s, basis))

    # flush -----------------------------------------------------------------
    def flush(self, h) -> Dict[str, int]:
        cur = h.conn.cursor()
        order = [("engine_instance", "engine_instance_key", ("host_id", "source_hash")),
                 ("campaign", "campaign_key", ()), ("experiment", "experiment_key", ("engine_id",)),
                 ("attempt", "attempt_key", ("host_id", "engine_instance_key", "commit_sha", "started_at")),
                 ("segment", "segment_key", ()), ("idea", "idea_key", ()), ("defect", "defect_key", ())]
        for table, key, watch in order:
            rows = list(self.t[table].values())
            if rows:
                _normalise_cols(rows)
                h.count(table, db.upsert(cur, "atlas." + table, rows, [key], h.id, watch=watch))
        srows = list(self.t["source"].values())
        if srows:
            _normalise_cols(srows)
            h.count("source", db.upsert(cur, "atlas.source", srows, ["uri"], h.id,
                                        replace=("top_keys", "shape_hash", "row_count", "blob_sha",
                                                 "commit_sha", "size_bytes", "mtime", "visibility")))
        needed = {u for u, *_ in self.links} | {u for _k, u, _l in self.fact_ev} | \
                 {c["_uri"] for c in self.concl.values() if c["_uri"]} | \
                 {e["_uri"] for e in self.edges.values() if e["_uri"]}
        sid = db.source_ids(cur, needed)
        lrows = [{"source_id": sid[u], "entity_type": t, "entity_key": k, "role": r}
                 for u, t, k, r in self.links if u in sid]
        h.count("source_link", db.upsert(cur, "atlas.source_link", lrows,
                                         ["source_id", "entity_type", "entity_key", "role"], h.id))
        fids = db.upsert(cur, "atlas.fact", list(self.facts.values()), ["fact_key"], h.id,
                         replace=("value_text", "value_num", "value_json", "status"), returning="fact_id") \
            if self.facts else {}
        h.count("fact", len(self.facts))
        ev = [{"fact_id": fids[k], "source_id": sid[u], "locator": loc}
              for k, u, loc in self.fact_ev if k in fids and u in sid]
        h.count("fact_evidence", db.upsert(cur, "atlas.fact_evidence", ev, ["fact_id", "source_id", "locator"], h.id))
        crows = []
        for c in self.concl.values():
            c = dict(c)
            c["source_id"] = sid.get(c.pop("_uri"))
            crows.append(c)
        h.count("conclusion", db.upsert(cur, "atlas.conclusion", crows, ["conclusion_key"], h.id,
                                        replace=("text_verbatim", "disposition")))
        erows = []
        for e in self.edges.values():
            e = dict(e)
            e["source_id"] = sid.get(e.pop("_uri"))
            erows.append(e)
        h.count("edge", db.upsert(cur, "atlas.edge", erows, ["src_type", "src_key", "dst_type", "dst_key", "relation"],
                                  h.id, replace=("reason", "basis", "confidence", "detail")))
        crow = [{"entity_type": a, "entity_key": b, "sha": c, "basis": d} for a, b, c, d in self.ecommits]
        h.count("entity_commit", db.upsert(cur, "atlas.entity_commit", crow,
                                           ["entity_type", "entity_key", "sha", "basis"], h.id))
        h.conn.commit()
        prune(cur, h)
        rollup(cur)
        h.conn.commit()
        return h.counts


PRUNABLE = ("atlas.edge", "atlas.fact", "atlas.conclusion", "atlas.source_link", "atlas.entity_commit")


def prune(cur, h) -> None:
    """RECOMB RULE: derived rows (edges, facts, conclusions, links) that this
    harvester wrote on THIS host in an earlier pass and did not re-emit now
    are removed -- an extractor fix must not leave its old mistakes standing.
    Entities (experiments, attempts, ideas, defects, sources) are never
    pruned: not seeing something again is not evidence it is gone. Rows last
    written by another host's instance are never touched."""
    cur.execute("SELECT harvester, host_id FROM atlas.harvest_run WHERE harvest_id = %s", (h.id,))
    harvester, host = cur.fetchone()
    for t in PRUNABLE:
        cur.execute("""DELETE FROM {t} x USING atlas.harvest_run r
                       WHERE x.last_harvest_id = r.harvest_id AND r.harvester = %s
                         AND r.host_id IS NOT DISTINCT FROM %s AND x.last_harvest_id <> %s""".format(t=t),
                    (harvester, host, h.id))
        if cur.rowcount:
            h.count("pruned_" + t.split(".")[1], cur.rowcount)


def _normalise_cols(rows: List[Dict[str, Any]]) -> None:
    """execute_values needs every row to carry the same columns."""
    cols = []
    for r in rows:
        for c in r:
            if c not in cols:
                cols.append(c)
    for r in rows:
        for c in cols:
            r.setdefault(c, None)
        for c in list(r):
            if r[c] is None and c in ("seen_from_hosts", "seeds", "hosts", "top_keys"):
                r[c] = [] if c != "top_keys" else None
            if r[c] is None and c in ("extract", "inferred", "budget", "os_env"):
                r[c] = {}
    order = cols
    for i, r in enumerate(rows):
        rows[i] = {c: r[c] for c in order}


def rollup(cur) -> None:
    """Derived tier-1 fields from tier-2 rows (ATLAS_DERIVED, recomputed every pass)."""
    cur.execute("""
      UPDATE atlas.experiment e SET
        n_attempts = s.n, hosts = s.hosts,
        first_seen_at = LEAST(e.first_seen_at, s.first_at),
        last_activity_at = GREATEST(e.last_activity_at, s.last_at)
      FROM (SELECT experiment_key, count(*) n,
                   ARRAY(SELECT DISTINCT x FROM unnest(array_agg(host_id)) x WHERE x IS NOT NULL ORDER BY 1) hosts,
                   min(started_at) first_at, max(COALESCE(finished_at, started_at)) last_at
            FROM atlas.attempt GROUP BY experiment_key) s
      WHERE s.experiment_key = e.experiment_key""")
    cur.execute("""
      UPDATE atlas.campaign c SET
        started_at = LEAST(c.started_at, s.first_at), ended_at = GREATEST(c.ended_at, s.last_at)
      FROM (SELECT campaign_key, min(first_seen_at) first_at, max(last_activity_at) last_at
            FROM atlas.experiment GROUP BY campaign_key) s
      WHERE s.campaign_key = c.campaign_key""")


VALIDITY_RULES = [
    (re.compile(r"INSTRUMENT_INVALID|INSTRUMENT_FAIL|RULER_INVALID|CONTROL_FAIL", re.I), "INSTRUMENT_FAILURE"),
    (re.compile(r"\bINVALID\b|\bVOID\b|UNUSABLE|BUG\b", re.I), "INVALID_ATTEMPT"),
    (re.compile(r"CRASH|TIMEOUT|PARTIAL|TRUNCAT|ABORT", re.I), "PARTIAL_EVIDENCE"),
]


def validity_from(*texts: Optional[str]) -> str:
    """Conservative: only words that name invalidity move the state off UNKNOWN."""
    for t in texts:
        if not t:
            continue
        for pat, state in VALIDITY_RULES:
            if pat.search(str(t)):
                return state
    return "UNKNOWN"
