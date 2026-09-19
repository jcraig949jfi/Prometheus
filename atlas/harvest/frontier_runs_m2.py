"""Source adapter (Atlas-M2, host M2): the DEEP FRONTIER receipt tree.

archaeon/frontier/runs/<family>/<spec dir>/RECEIPT.json (+ chunk_NNN.json.gz)
is git-ignored and exists only on the executing host. Atlas's frontier
harvester (git, M1) records every receipt a RUN event names as an
EXPECTED:M2 pointer on the attempt; this module, run on M2, looks at the
tree and enriches the SAME rows:

  - the receipt pointer becomes FS:M2, present=true, with size/mtime/sha
  - the attempt gains started_at / finished_at / config_digest / budget
    and RAN facts from the receipt (status, evaluations, integrity)
  - each chunk in the receipt is a segment on the SAME segment key Atlas
    uses (chunk_NNN); a chunk file beside the receipt is an FS:M2 pointer

IDENTITY RULE (the reason this module exists as its own file): an attempt
id in the index is the RUN event's time ("at20260919T020405Z"), which is
within a second of the receipt's finished_at but NOT equal to it (8 of 42
differ by one second on 2026-09-19). A receipt time is therefore never
minted into an attempt key. Identity comes ONLY from the pointer Atlas
already linked (receipt path -> attempt key). A receipt with no pointer
yet (the RUN event is not on the ref Atlas harvested, or the run is still
RUNNING) is linked to its EXPERIMENT -- the receipt's own declared
experiment_id, which is the native id Atlas keys experiments by -- and
carries a fact saying so. It never gets a guessed attempt.

Non-interference: os.stat, os.listdir, one json.load per RECEIPT.json
(3-4 KB), sha256 of files <= SMALL bytes. Chunk archives are never
decompressed. Nothing is opened for writing, locked or signalled.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re

from atlas import db
from atlas.harvest import common as C

VERSION = "frontier_runs_m2/1"
PROGRAM = "archaeon.frontier"
CKEY = C.campaign_key(PROGRAM, "deep-frontier")
REL = "archaeon/frontier/runs"          # the path prefix Atlas's pointers use
SMALL = 5_000_000
REGISTRY_MODE = "frontier_receipts"     # local_roots rows this module owns


def _iso(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat()


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ekey(tid: str) -> str:
    return C.experiment_key(CKEY, tid)


def _linked(cur) -> dict:
    """receipt path (as Atlas wrote it) -> attempt key, from the pointers already in the index."""
    cur.execute("""SELECT s.path, l.entity_key FROM atlas.source s JOIN atlas.source_link l USING (source_id)
                   WHERE s.uri LIKE %s AND l.entity_type = 'attempt' AND l.role = 'receipt'""",
                ("hostfile://%/" + REL + "/%/RECEIPT.json",))
    return dict(cur.fetchall())


def run(args) -> dict:
    host = db.this_host()
    roots = [r for r in db.registry().get("local_roots", [])
             if r.get("host") == host and r.get("mode") == REGISTRY_MODE]
    b = C.Batch("frontier_runs_m2", VERSION, "Archaeon")
    conn = db.connect()
    try:
        with conn.cursor() as cur:
            linked = _linked(cur)
    finally:
        conn.close()
    stats = {"receipts": 0, "matched": 0, "unmatched": 0, "chunks": 0, "roots_missing": 0}
    for r in roots:
        if not os.path.isdir(r["root"]):
            stats["roots_missing"] += 1
            continue
        collect(b, r["root"], host, linked, stats)
    with db.harvest("frontier_runs_m2", VERSION,
                    source_ref="{} receipts / {} matched / {} unmatched on {}".format(
                        stats["receipts"], stats["matched"], stats["unmatched"], host)) as h:
        counts = b.flush(h)
    counts.update({"receipts_" + k: v for k, v in stats.items()})
    return counts


def collect(b, root: str, host: str, linked: dict, stats: dict = None) -> None:
    """Pure over the tree: reads receipts under root, writes into the batch.
    linked maps Atlas's receipt path -> attempt key; nothing else names an attempt."""
    stats = stats if stats is not None else {"receipts": 0, "matched": 0, "unmatched": 0, "chunks": 0}
    for fam in sorted(os.listdir(root)):
        fdir = os.path.join(root, fam)
        if not os.path.isdir(fdir):
            continue
        for spec in sorted(os.listdir(fdir)):
            sdir = os.path.join(fdir, spec)
            rpath = os.path.join(sdir, "RECEIPT.json")
            if not os.path.isfile(rpath):
                continue
            try:
                with open(rpath, "r", encoding="utf-8") as f:
                    rec = json.load(f)
            except (OSError, ValueError) as e:
                u = _file_source(b, host, rpath, "{}/{}/{}/RECEIPT.json".format(REL, fam, spec))
                b.fact("RAN", "failure_mode", "campaign", CKEY, "receipt.unreadable", "{}: {}".format(rpath, e), u,
                       rpath, author="ATLAS_DERIVED")
                continue
            stats["receipts"] += 1
            rel = "{}/{}/{}/RECEIPT.json".format(REL, fam, spec)
            u = _file_source(b, host, rpath, rel)
            tid = rec.get("experiment_id")
            if not isinstance(tid, str) or not tid:
                b.fact("RAN", "failure_mode", "campaign", CKEY, "receipt.no_experiment_id", rel, u, rel,
                       author="ATLAS_DERIVED")
                continue
            xk = ekey(tid)
            akey = linked.get(rel)
            if akey:
                stats["matched"] += 1
                _attempt(b, akey, xk, rec, rel, u, host)
                _chunks(b, akey, rec, sdir, fam, spec, host, u, stats)
            else:
                stats["unmatched"] += 1
                # the experiment exists in Atlas's index under this native id; the attempt does not (yet)
                b.experiment(experiment_key=xk, campaign_key=CKEY, engine_id=PROGRAM, native_id=tid,
                             kind="transformation", driver_seat="Archaeon")
                b.link(u, "experiment", xk, "receipt_unmatched")
                b.fact("RAN", "telemetry_availability", "experiment", xk, "receipt.present_no_run_event",
                       {"path": rel, "status": rec.get("status"), "started_at": rec.get("started_at"),
                        "finished_at": rec.get("finished_at"), "evaluations": rec.get("evaluations")},
                       u, rel, author="ATLAS_DERIVED")


def _file_source(b, host, path, rel, **extra):
    st = os.stat(path)
    p = path.replace("\\", "/")
    return b.other_source("hostfile://{}/{}".format(host, rel), "file", "FS:" + host, host_id=host, path=rel,
                          local_path=p, size_bytes=st.st_size, mtime=_iso(st.st_mtime),
                          file_sha256=_sha(path) if st.st_size <= SMALL else None, present=True, **extra)


def _attempt(b, akey, xk, rec, rel, u, host):
    budget = (rec.get("spec") or {}).get("budget") if isinstance(rec.get("spec"), dict) else None
    b.attempt(attempt_key=akey, experiment_key=xk, started_at=rec.get("started_at"), finished_at=rec.get("finished_at"),
              host_id=host, config_digest=(rec.get("spec") or {}).get("spec_digest") if isinstance(rec.get("spec"), dict) else None,
              budget={"receipt": budget} if budget else None,
              extract={"receipt_schema": rec.get("schema"), "receipt_status": rec.get("status"),
                       "receipt_evaluations": rec.get("evaluations"), "receipt_integrity": rec.get("integrity"),
                       "capabilities": rec.get("capabilities")})
    b.link(u, "attempt", akey, "receipt")
    b.fact("RAN", "telemetry_availability", "attempt", akey, "receipt.host", host, u, rel)
    for name, key in (("receipt.status", "status"), ("receipt.evaluations", "evaluations"),
                      ("receipt.started_at", "started_at"), ("receipt.finished_at", "finished_at")):
        if rec.get(key) is not None:
            b.fact("RAN", "parameter" if key == "status" else "budget" if key == "evaluations" else "parameter",
                   "attempt", akey, name, rec.get(key), u, key)
    if rec.get("integrity"):
        b.fact("RAN", "telemetry_availability", "attempt", akey, "receipt.integrity", rec.get("integrity"), u, "integrity")


def _chunks(b, akey, rec, sdir, fam, spec, host, u, stats):
    for n, ch in enumerate(rec.get("chunks") or []):
        if not isinstance(ch, dict):
            continue
        try:
            ordinal = int(ch.get("chunk", n))
        except (TypeError, ValueError):
            continue
        nid = "chunk_{:03d}".format(ordinal)
        sk = C.segment_key(akey, nid)
        b.segment(segment_key=sk, attempt_key=akey, native_id=nid, kind="chunk", ordinal=ordinal, host_id=host,
                  reported_status=ch.get("status"), evaluations=ch.get("evaluations"), digest=ch.get("out_digest"),
                  extract={x: ch.get(x) for x in ("g0", "g1", "anchors", "events", "freezes", "spec_hash",
                                                  "checkpoint_out", "wall_s") if x in ch})
        b.link(u, "segment", sk, "receipt")
        stats["chunks"] += 1
        for det, cnt in (ch.get("fired") or {}).items() if isinstance(ch.get("fired"), dict) else ():
            b.fact("OBSERVED", "detector_firing", "segment", sk, "receipt.fired." + str(det), cnt, u,
                   "chunks[{}].fired.{}".format(ordinal, det))
        for det, cnt in (ch.get("unable") or {}).items() if isinstance(ch.get("unable"), dict) else ():
            b.fact("OBSERVED", "detector_firing", "segment", sk, "receipt.unable." + str(det), cnt, u,
                   "chunks[{}].unable.{}".format(ordinal, det))
        cfile = os.path.join(sdir, nid + ".json.gz")
        if os.path.isfile(cfile):
            cu = _file_source(b, host, cfile, "{}/{}/{}/{}.json.gz".format(REL, fam, spec, nid))
            b.link(cu, "segment", sk, "rows")
