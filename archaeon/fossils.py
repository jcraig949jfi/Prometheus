"""Deterministic reads of the fossil record.

Two sources, one normalized row type.

  SFE   ``var/engine.db``  (SQLite, schema 6) -- experiments JOIN observations.
        This is where the numeric observables actually live today: 3241 of
        3315 observations carry ``content.score`` and 3009 experiment specs
        carry a numeric ``spec.candidate`` coordinate.

  PEW   ``ew.fossil_*``    (PostgreSQL, prometheus_fire) -- the encounter /
        player / world fossils, plus ``fossil_worlds.family`` which is the
        only world-FAMILY key either substrate publishes.

Deliberate choices:

* **Structured queries, never textual summaries.** Nothing here reads prose.
* **Ordered by the ledger anchor, never by wall clock.** ``events.event_seq``
  is the authority (SFE_ARCHAEOLOGY_SCHEMA.md s1); ``ts`` is informational and
  ordering by it would silently reorder the corpus under clock skew.
* **Every row keeps its anchors.** A FossilRow can always name the SFE
  experiment, observation and (where present) ledger event it came from, so a
  proposal derived from it is traceable back to immutable evidence.
* **The window is recorded, not implied.** ``corpus_hash`` fingerprints the
  exact set of row ids read, so "re-run Archaeon on the same corpus" is a
  checkable statement rather than a hope.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from . import config as cfg

REPO_ROOT = Path(__file__).resolve().parent.parent
# The live ledger lives where the ENGINE runs, not where this reader's checkout
# is. An isolated worktree (operator directive 2026-09-06) has no var/engine.db,
# so ARCHAEON_SFE_DB names the file; the checkout-relative path is the fallback.
DEFAULT_SFE_DB = Path(os.environ.get(
    "ARCHAEON_SFE_DB",
    str(REPO_ROOT / "SerendipityFoundry" / "SerendipityFoundryEngine" / "var" / "engine.db")))


# --------------------------------------------------------------------------
# The normalized row
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class FossilRow:
    """One observation, projected through a CoordinateChart.

    ``coords`` are RAW parameter values. Normalization to [0, 1] happens in
    ``Corpus.normalized()`` and is recorded there, because a detector threshold
    expressed in normalized units is meaningless without the scaling that
    produced it.
    """
    row_id: str                       # stable within a corpus; provenance handle
    source: str                       # 'sfe' | 'pew'
    seq: int                          # ledger order (event_seq); the only order
    region: str                       # world
    family: Optional[str]             # world family
    player: Optional[str]             # player identity, or None if absent
    metric: float                     # the numeric observable
    coords: Dict[str, float] = field(default_factory=dict)
    anchors: Dict[str, Any] = field(default_factory=dict)

    def anchor_ref(self) -> Dict[str, Any]:
        """The provenance-safe reference written into a proposal."""
        return {"row_id": self.row_id, "source": self.source,
                "seq": self.seq, "region": self.region,
                "player": self.player, "anchors": dict(self.anchors)}


@dataclass
class Corpus:
    """The exact set of rows one Archaeon cycle read."""
    rows: List[FossilRow]
    chart: cfg.CoordinateChart
    source_ref: str                   # db path / dsn description
    window: Dict[str, Any]            # what the query asked for

    # ---- identity -------------------------------------------------------
    def corpus_hash(self) -> str:
        """sha256 over the ordered row ids AND their metric values.

        Ids alone would not notice a corrected metric; including the values
        makes the hash a statement about the DATA, not just the selection.
        """
        h = hashlib.sha256()
        for r in sorted(self.rows, key=lambda r: (r.seq, r.row_id)):
            h.update(r.row_id.encode("utf-8"))
            h.update(b"\x00")
            h.update(repr(round(r.metric, 12)).encode("utf-8"))
            h.update(b"\x00")
        return "corpus:" + h.hexdigest()[:24]

    def __len__(self) -> int:
        return len(self.rows)

    # ---- coordinate normalization ---------------------------------------
    def coord_scales(self) -> Dict[str, Dict[str, float]]:
        """min/max per coordinate axis over this corpus.

        Returned (not hidden) so the scaling that a normalized threshold was
        applied against is written into provenance.
        """
        scales: Dict[str, Dict[str, float]] = {}
        for axis in self.chart.coord_fields:
            vals = [r.coords[axis] for r in self.rows if axis in r.coords]
            if not vals:
                continue
            lo, hi = min(vals), max(vals)
            scales[axis] = {"min": lo, "max": hi, "span": (hi - lo)}
        return scales

    def normalized_coords(self, row: FossilRow,
                          scales: Optional[Dict[str, Dict[str, float]]] = None
                          ) -> Dict[str, float]:
        scales = scales if scales is not None else self.coord_scales()
        out: Dict[str, float] = {}
        for axis, s in scales.items():
            if axis not in row.coords:
                continue
            span = s["span"]
            # A degenerate axis (every row identical) normalizes to 0.0 rather
            # than dividing by zero. It carries no locality information, and
            # the eligibility census reports it as such.
            out[axis] = 0.0 if span <= 0 else (row.coords[axis] - s["min"]) / span
        return out


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _dig(obj: Any, dotted: str) -> Any:
    """Fetch a dotted path out of nested dicts. Missing -> None."""
    cur = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _num(v: Any) -> Optional[float]:
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return None


def _metric(content: Any, chart) -> Optional[float]:
    """The observable, from the chart's declared path or its declared
    alternates, in order. No searching: only paths the chart names."""
    for path in (chart.metric_field,) + tuple(
            getattr(chart, "metric_alt_fields", ()) or ()):
        v = _num(_dig({"content": content}, path))
        if v is not None:
            return v
    return None


def _loads(s: Any) -> Any:
    if isinstance(s, (dict, list)):
        return s
    if not isinstance(s, str):
        return None
    try:
        return json.loads(s)
    except Exception:
        return None


# --------------------------------------------------------------------------
# SFE reader
# --------------------------------------------------------------------------
def read_sfe(db_path: Optional[str] = None,
             chart: Optional[cfg.CoordinateChart] = None,
             lookback_rows: int = cfg.DEFAULT.lookback_rows) -> Corpus:
    """Read completed SFE experiments joined to their observations.

    Only OBSERVED experiments with a bound observation are fossils: an
    experiment with no observation has not happened yet, and including it would
    let an un-run experiment contribute to a detector.
    """
    chart = chart or cfg.CHARTS[cfg.DEFAULT_CHART]
    path = str(db_path or DEFAULT_SFE_DB)
    if not os.path.exists(path):
        return Corpus([], chart, path, {"error": "sfe db not found",
                                        "path": path})

    ten = cfg.DEFAULT.tenancy
    uri = "file:{}?mode=ro".format(path.replace("?", "%3f"))
    conn = sqlite3.connect(uri, uri=True, isolation_level=None)
    conn.row_factory = sqlite3.Row
    excluded_by_tenant: Dict[str, int] = {}
    try:
        # ONE transaction for every statement: SQLite WAL gives a consistent
        # view only within a transaction, and this file is being written by
        # three consumers. Several separate SELECTs would not be one
        # observation of one state (consumer contract s2, point 3).
        conn.execute("BEGIN")

        # Schema guard. The engine refuses to open a ledger newer than its
        # code; a raw reader has no such protection and would misread a v7
        # database as v6 (s2, point 4). Refuse, do not guess.
        have = conn.execute("SELECT value FROM meta WHERE key='schema_version'"
                            ).fetchone()
        have_v = int(have[0]) if have else None
        if have_v is None or have_v > ten.expected_schema_version:
            conn.execute("COMMIT")
            return Corpus([], chart, path, {
                "error": "sfe schema_version {} is newer than this reader "
                         "understands ({}); refusing to read rather than "
                         "misread a row shape".format(
                             have_v, ten.expected_schema_version),
                "schema_version": have_v})

        # Declared tenancy: client NAMES, resolved to ids inside the same
        # snapshot. Everything else is counted, never silently dropped.
        clients = conn.execute("SELECT client_id, name FROM clients").fetchall()
        admitted_ids = [c["client_id"] for c in clients
                        if c["name"] in ten.include_client_names]
        admitted_names = sorted({c["name"] for c in clients
                                 if c["name"] in ten.include_client_names})
        for row in conn.execute(
                "SELECT cl.name, count(*) AS n FROM observations o "
                "  JOIN worlds w ON w.world_id = o.world_id "
                "  JOIN clients cl ON cl.client_id = w.client_id "
                " WHERE o.evidence_class IN ({ev}) "
                " GROUP BY cl.name".format(
                    ev=",".join("?" * len(ten.evidence_classes))),
                list(ten.evidence_classes)):
            if row["name"] not in ten.include_client_names:
                excluded_by_tenant[row["name"]] = int(row["n"])

        # world family: SFE has no family column, so topology_group is the
        # nearest published grouping. NULL is honest and stays NULL.
        sql = """
            SELECT o.obs_id, o.exp_id, o.world_id, o.content, o.outcome,
                   o.evidence_class, o.work_id, o.created_seq AS obs_seq,
                   e.spec, e.spec_hash, e.committed_seq, e.state,
                   w.topology_group AS world_family, w.client_id
              FROM observations o
              JOIN experiments  e ON e.exp_id  = o.exp_id
              JOIN worlds       w ON w.world_id = o.world_id
             WHERE o.evidence_class IN ({ev})
               AND w.client_id IN ({cl})
             ORDER BY o.created_seq DESC
             LIMIT ?
        """.format(ev=",".join("?" * len(ten.evidence_classes)),
                   cl=",".join("?" * max(len(admitted_ids), 1)))
        params = (list(ten.evidence_classes)
                  + (admitted_ids or ["<no admitted client>"])
                  + [int(lookback_rows)])
        raw = conn.execute(sql, params).fetchall()
        conn.execute("COMMIT")
    finally:
        conn.close()

    rows: List[FossilRow] = []
    unattributed_multi_player = 0
    for r in raw:
        content = _loads(r["content"])
        spec = _loads(r["spec"])
        if not isinstance(content, dict):
            continue
        metric = _metric(content, chart)
        if metric is None:
            continue
        coords: Dict[str, float] = {}
        for axis in chart.coord_fields:
            v = _num(_dig({"spec": spec if isinstance(spec, dict) else {}}, axis))
            if v is not None:
                coords[axis] = v
        player = None
        if chart.player_field:
            pv = _dig({"spec": spec if isinstance(spec, dict) else {},
                       "content": content}, chart.player_field)
            if isinstance(pv, list):
                # Observation-level attribution from the sealed spec. Exactly
                # one declared player attributes the observation; several is
                # AMBIGUOUS and is left unattributed and counted, never
                # resolved by taking the first.
                if len(pv) == 1 and pv[0]:
                    player = str(pv[0])
                elif len(pv) > 1:
                    unattributed_multi_player += 1
            elif pv is not None:
                player = str(pv)
        rows.append(FossilRow(
            row_id=r["obs_id"],
            source="sfe",
            seq=int(r["obs_seq"]),
            region=r["world_id"],
            family=r["world_family"],
            player=player,
            metric=metric,
            coords=coords,
            anchors={"obs_id": r["obs_id"], "exp_id": r["exp_id"],
                     "work_id": r["work_id"], "world_id": r["world_id"],
                     "spec_hash": r["spec_hash"],
                     "committed_seq": r["committed_seq"],
                     "observation_created_seq": int(r["obs_seq"]),
                     "evidence_class": r["evidence_class"],
                     "outcome": r["outcome"]},
        ))

    rows.sort(key=lambda x: (x.seq, x.row_id))
    return Corpus(rows, chart, path,
                  {"lookback_rows": int(lookback_rows),
                   "order": "observations.created_seq DESC",
                   "join": "observations JOIN experiments JOIN worlds",
                   "returned": len(rows),
                   # The declared population, per the consumer contract.
                   "tenancy": {"admitted_client_names": admitted_names,
                               "admitted_client_ids": len(admitted_ids),
                               "excluded_attested_by_client_name":
                                   dict(sorted(excluded_by_tenant.items())),
                               "evidence_classes": list(ten.evidence_classes),
                               "schema_version": have_v,
                               "snapshot": "single transaction",
                               "basis": ("interim raw read with declared "
                                         "tenancy + evidence filter; a "
                                         "cross-tenant read grant is "
                                         "Daedalus's to build")},
                   "unattributed_multi_player_experiments":
                       unattributed_multi_player})


# --------------------------------------------------------------------------
# PEW reader
# --------------------------------------------------------------------------
def read_pew(chart: Optional[cfg.CoordinateChart] = None,
             lookback_rows: int = cfg.DEFAULT.lookback_rows,
             namespace: str = "prod",
             conn=None) -> Corpus:
    """Read PEW player fossils joined to their world family.

    ``namespace='prod'`` by default: the ``synthetic`` and ``test`` namespaces
    exist precisely so that fixtures cannot enter a production read.
    """
    chart = chart or cfg.CHARTS[cfg.PEW_PHENOTYPE_CHART.name]
    owns = conn is None
    if conn is None:
        try:
            from evidence_wiki.ew import db as ewdb  # type: ignore
            conn = ewdb.connect()
        except Exception as exc:                     # pragma: no cover
            return Corpus([], chart, "pew:unavailable",
                          {"error": "pew unreachable: {}".format(exc)})
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT p.player_id, p.genome_hash, p.sfe_world_id, p.sfe_entry_hash,
                   p.parent_player, p.phenotype, p.resources, p.revision,
                   w.family AS world_family, w.manifest_hash
              FROM ew.fossil_players p
              LEFT JOIN ew.fossil_worlds w ON w.sfe_world_id = p.sfe_world_id
             WHERE p.namespace = %s
             ORDER BY p.revision DESC
             LIMIT %s
            """, (namespace, int(lookback_rows)))
        raw = cur.fetchall()
        cols = [d[0] for d in cur.description]
    finally:
        if owns:
            try:
                conn.close()
            except Exception:
                pass

    rows: List[FossilRow] = []
    for rec in raw:
        r = dict(zip(cols, rec))
        pheno = r.get("phenotype") if isinstance(r.get("phenotype"), dict) else {}
        metric = _num(_dig({"phenotype": pheno}, chart.metric_field))
        if metric is None:
            continue
        region = r.get("sfe_world_id") or "<unbound>"
        rows.append(FossilRow(
            row_id=str(r["player_id"]),
            source="pew",
            # PEW revision is PEW's own write order, not producer order. It is
            # the only monotonic handle on a player fossil, and it is labelled
            # as such rather than passed off as an SFE event_seq.
            seq=int(r["revision"]),
            region=region,
            family=r.get("world_family"),
            player=str(r["player_id"]),
            metric=metric,
            coords={},
            anchors={"player_id": r["player_id"],
                     "genome_hash": r.get("genome_hash"),
                     "sfe_world_id": r.get("sfe_world_id"),
                     "sfe_entry_hash": r.get("sfe_entry_hash"),
                     "parent_player": r.get("parent_player"),
                     "pew_revision": int(r["revision"]),
                     "seq_kind": "pew.revision"},
        ))

    rows.sort(key=lambda x: (x.seq, x.row_id))
    return Corpus(rows, chart, "pew:ew.fossil_players",
                  {"namespace": namespace, "lookback_rows": int(lookback_rows),
                   "order": "fossil_players.revision DESC",
                   "returned": len(rows)})


def read(chart_name: str = cfg.DEFAULT_CHART, **kw) -> Corpus:
    """Read the corpus for a named chart."""
    chart = cfg.CHARTS[chart_name]
    if chart.source == "sfe":
        return read_sfe(chart=chart, **kw)
    if chart.source == "pew":
        return read_pew(chart=chart, **kw)
    if chart.source == "sfe_proteus":
        return read_sfe_proteus(chart=chart, **kw)
    raise ValueError("unknown chart source: {}".format(chart.source))


def corpus_from_rows(rows: Sequence[FossilRow],
                     chart: Optional[cfg.CoordinateChart] = None,
                     source_ref: str = "synthetic") -> Corpus:
    """Build a Corpus from rows in memory. Used by the calibration harness."""
    chart = chart or cfg.CHARTS[cfg.DEFAULT_CHART]
    ordered = sorted(rows, key=lambda x: (x.seq, x.row_id))
    return Corpus(list(ordered), chart, source_ref,
                  {"synthetic": True, "returned": len(ordered)})


# --------------------------------------------------------------------------
# SFE + Proteus reader: player identity via the artifact join
# --------------------------------------------------------------------------
def read_sfe_proteus(db_path: Optional[str] = None,
                     chart: Optional[cfg.CoordinateChart] = None,
                     lookback_rows: int = cfg.DEFAULT.lookback_rows) -> Corpus:
    """Read SFE fossils with PROTEUS player identity attached.

    The join, and why it is legitimate rather than a convention:

        artifacts.kind = 'proteus_player_manifest'
        artifacts.blob_hash == Proteus organism_id

    Proteus posts the canonical manifest serialization and SFE content-
    addresses the BYTES, so the equality holds by construction. One assertion
    proves the specimen crossed unaltered (HARMONIA_HANDOFF.md s10).

    A world holding exactly one such artifact names the player that ran there.
    A world holding SEVERAL is ambiguous under this chart -- Archaeon cannot
    tell which player produced which observation from the artifact table alone
    -- so those worlds are EXCLUDED and counted, rather than being resolved by
    a guess. The exclusion count is reported in the corpus window, because a
    silently dropped world is a silently biased corpus.

    Coordinates come from the Proteus registry's resource envelope, not from
    the SFE spec.
    """
    from . import proteus_link as px

    chart = chart or cfg.PROTEUS_PLAYER_CHART
    path = str(db_path or DEFAULT_SFE_DB)
    if not os.path.exists(path):
        return Corpus([], chart, path, {"error": "sfe db not found",
                                        "path": path})
    try:
        known = px.entries_by_id()
    except px.ProteusUnavailable as exc:
        return Corpus([], chart, path,
                      {"error": "proteus registry unavailable: {}".format(exc)})

    uri = "file:{}?mode=ro".format(path.replace("?", "%3f"))
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        # world -> the proteus players whose manifests entered it
        world_players: Dict[str, set] = {}
        for r in conn.execute(
                "SELECT world_id, blob_hash FROM artifacts WHERE kind = ?",
                (px.PROTEUS_ARTIFACT_KIND,)):
            oid = str(r["blob_hash"]).split("sha256:")[-1]
            world_players.setdefault(r["world_id"], set()).add(oid)

        unique = {w: next(iter(p)) for w, p in world_players.items()
                  if len(p) == 1}
        ambiguous = sorted(w for w, p in world_players.items() if len(p) > 1)

        if not unique:
            return Corpus([], chart, path, {
                "join": "artifacts.kind=proteus_player_manifest -> blob_hash=organism_id",
                "worlds_with_proteus_artifact": len(world_players),
                "worlds_with_unique_player": 0,
                "worlds_ambiguous_excluded": len(ambiguous),
                "reason": ("no SFE world carries exactly one proteus player "
                           "manifest, so no player-bound fossil can be formed"),
                "returned": 0})

        marks = ",".join("?" for _ in unique)
        sql = """
            SELECT o.obs_id, o.exp_id, o.world_id, o.content, o.outcome,
                   o.evidence_class, o.work_id, o.created_seq AS obs_seq,
                   e.spec, e.spec_hash, e.committed_seq,
                   w.topology_group AS world_family
              FROM observations o
              JOIN experiments  e ON e.exp_id  = o.exp_id
              JOIN worlds       w ON w.world_id = o.world_id
             WHERE o.world_id IN ({})
             ORDER BY o.created_seq DESC
             LIMIT ?
        """.format(marks)
        raw = conn.execute(sql, list(unique) + [int(lookback_rows)]).fetchall()
    finally:
        conn.close()

    rows: List[FossilRow] = []
    unregistered = set()
    for r in raw:
        content = _loads(r["content"])
        if not isinstance(content, dict):
            continue
        metric = _num(_dig({"content": content}, chart.metric_field))
        if metric is None:
            continue
        oid = unique[r["world_id"]]
        if oid not in known:
            unregistered.add(oid)
        coords = {k: v for k, v in px.envelope_coords(oid).items()
                  if k in chart.coord_fields}
        rows.append(FossilRow(
            row_id=r["obs_id"], source="sfe_proteus", seq=int(r["obs_seq"]),
            region=r["world_id"], family=r["world_family"], player=oid,
            metric=metric, coords=coords,
            anchors={"obs_id": r["obs_id"], "exp_id": r["exp_id"],
                     "work_id": r["work_id"], "world_id": r["world_id"],
                     "spec_hash": r["spec_hash"],
                     "committed_seq": r["committed_seq"],
                     "observation_created_seq": int(r["obs_seq"]),
                     "evidence_class": r["evidence_class"],
                     "outcome": r["outcome"],
                     "proteus_organism_id": oid,
                     "proteus_generation": known.get(oid, {}).get("generation"),
                     "player_binding": ("artifacts.blob_hash == organism_id "
                                        "(kind=proteus_player_manifest)")},
        ))

    rows.sort(key=lambda x: (x.seq, x.row_id))
    return Corpus(rows, chart, path, {
        "join": "artifacts.kind=proteus_player_manifest -> blob_hash=organism_id",
        "worlds_with_proteus_artifact": len(world_players),
        "worlds_with_unique_player": len(unique),
        "worlds_ambiguous_excluded": len(ambiguous),
        "ambiguous_worlds": ambiguous[:20],
        "distinct_players": len({r.player for r in rows}),
        "unregistered_players": sorted(unregistered)[:10],
        "lookback_rows": int(lookback_rows),
        "order": "observations.created_seq DESC",
        "returned": len(rows)})



# --------------------------------------------------------------------------
# Region -> executable landscape parameters
# --------------------------------------------------------------------------
def region_params(world_id: str, db_path: Optional[str] = None
                  ) -> Optional[Dict[str, Any]]:
    """The parameters that would re-create a region's landscape.

    A region is a world. Its landscape is fixed by ``worlds.seed_root`` and,
    for evaluate_bitstring, by ``work.payload.length`` on its experiments (the
    hidden target is sha256("target:<seed_root>:<length>")). Both are read from
    the ledger, never guessed: a world whose experiments carry no length is
    reported as such and no region-directed draw can target it.

    Measured 2026-09-06: 146/146 attested worlds carry seed_root; 41 carry a
    recoverable length (the Vivarium-shaped ones).
    """
    path = str(db_path or DEFAULT_SFE_DB)
    if not os.path.exists(path):
        return None
    uri = "file:{}?mode=ro".format(path.replace("?", "%3f"))
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        w = conn.execute("SELECT seed_root FROM worlds WHERE world_id = ?",
                         (world_id,)).fetchone()
        if w is None or w["seed_root"] is None:
            return None
        lengths = set()
        for r in conn.execute("SELECT spec FROM experiments WHERE world_id = ?",
                              (world_id,)):
            sp = _loads(r["spec"])
            if not isinstance(sp, dict):
                continue
            L = _num(_dig({"work": sp.get("work") or {}}, "work.payload.length"))
            if L is not None:
                lengths.add(int(L))
    finally:
        conn.close()
    out: Dict[str, Any] = {"world_id": world_id, "seed_root": int(w["seed_root"])}
    if len(lengths) == 1:
        out["length"] = lengths.pop()
    elif len(lengths) > 1:
        # several lengths in one world means several landscapes; the region
        # is not a single landscape and a directed draw cannot name one
        out["length_ambiguous"] = sorted(lengths)
    return out
