"""Append-only JSONL persistence for the cartography campaign.

RESTARTABILITY IS THE REQUIREMENT. A crash at cycle 47 must not cost cycles 0-46. So every
store is an append-only JSONL file: a partially-written final line is detected and dropped on
read, and nothing is ever rewritten in place. There is no database to corrupt and no index to
fall out of sync.

DEDUPLICATION IS BY CONTENT KEY, NOT BY POSITION. Re-encountering a paper on a later cycle is
normal -- citation expansion revisits nodes constantly -- so `upsert` keys on the record's id
and keeps the LAST write, while the earlier write stays in the file as history. Reading gives
you current state; the file gives you how it got there.

WHY NOT sqlite: the campaign's most important artifacts are the pre-reveal freezes for the
historical backtest, and a plain text file whose hash can be published is a better freeze than
a binary a reader has to trust us about.
"""
from __future__ import annotations

import json
import pathlib
from typing import Any, Callable, Iterator, Optional

from .schema import digest, now_iso

CARTOGRAPHY_ROOT = pathlib.Path(__file__).resolve().parent
STORE_DIR = CARTOGRAPHY_ROOT / "store"
CYCLE_DIR = CARTOGRAPHY_ROOT / "cycles"

STORES = {
    "genomes": "genomes.jsonl",
    "claims": "claims.jsonl",
    "holes": "coverage_holes.jsonl",
    "confounds": "confounds.jsonl",
    "retrieval": "retrieval_log.jsonl",
    "experiments": "experiment_queue.jsonl",
    "taxonomy": "taxonomy_events.jsonl",
    "rejected": "rejected_sources.jsonl",
}

#: The id field for each store, used by upsert/current.
KEYS = {
    "genomes": "research_genome_id",
    "claims": "claim_id",
    "holes": "hole_id",
    "confounds": "confound_id",
    "retrieval": None,            # pure log; no identity, never deduplicated
    "experiments": "candidate_id",
    "taxonomy": None,             # pure log
    "rejected": None,             # pure log
}


def _path(store: str) -> pathlib.Path:
    if store not in STORES:
        raise KeyError("unknown store " + repr(store) + "; known: " + repr(sorted(STORES)))
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    return STORE_DIR / STORES[store]


def append(store: str, record: Any) -> str:
    """Append one record. Returns its content digest.

    Writes are flushed per line so a kill between cycles loses at most the line in flight,
    and a torn final line is dropped by `read`.
    """
    obj = record.as_dict() if hasattr(record, "as_dict") else dict(record)
    obj.setdefault("_written_at", now_iso())
    d = digest(obj)
    obj["_digest"] = d
    p = _path(store)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")
        fh.flush()
    return d


def append_many(store: str, records) -> int:
    n = 0
    for r in records:
        append(store, r)
        n += 1
    return n


def read(store: str) -> Iterator[dict]:
    """Yield every record ever written, in write order.

    A trailing partial line -- the signature of a crash mid-write -- is skipped rather than
    raising, because the campaign must survive its own interruption. Skipped lines are
    reported through `integrity`.
    """
    p = _path(store)
    if not p.exists():
        return
    with p.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def current(store: str) -> dict:
    """Current state: id -> last-written record. Logs (KEYS[store] is None) raise, because
    'current state' is not a meaningful question to ask of an append-only log."""
    key = KEYS[store]
    if key is None:
        raise ValueError("store " + repr(store) + " is a pure log; use read() or count()")
    out = {}
    for rec in read(store):
        rid = rec.get(key)
        if rid is not None:
            out[rid] = rec
    return out


def upsert(store: str, record: Any) -> str:
    """Append; the last write for an id wins on read. Earlier writes remain as history."""
    return append(store, record)


def count(store: str, predicate: Optional[Callable[[dict], bool]] = None) -> int:
    if predicate is None:
        key = KEYS[store]
        if key is None:
            return sum(1 for _ in read(store))
        return len(current(store))
    key = KEYS[store]
    src = read(store) if key is None else current(store).values()
    return sum(1 for r in src if predicate(r))


def has(store: str, record_id: str) -> bool:
    key = KEYS[store]
    if key is None:
        return False
    for rec in read(store):
        if rec.get(key) == record_id:
            return True
    return False


def known_source_ids() -> set:
    """Every source id already compiled to a genome or explicitly rejected.

    Used to keep citation expansion from re-fetching the same nodes forever. Rejections count:
    a source we looked at and declined is knowledge, and re-fetching it every cycle would be
    the crawler equivalent of a memory leak.
    """
    ids = set()
    for rec in read("genomes"):
        if rec.get("source_id"):
            ids.add(rec["source_id"])
    for rec in read("rejected"):
        if rec.get("source_id"):
            ids.add(rec["source_id"])
    return ids


def allocate_cycle(start_hint=None):
    """Reserve a collision-proof cycle number (LIM-011 repair). See allocator.py."""
    from .allocator import allocate
    return allocate(start_hint)


def write_cycle(record: Any) -> pathlib.Path:
    """Persist one cycle fossil as its own file, in addition to the rolling log.

    Per-cycle files exist so a reader can diff two cycles without parsing the whole campaign,
    and so a corrupted rolling log cannot take the cycle history with it.
    """
    CYCLE_DIR.mkdir(parents=True, exist_ok=True)
    obj = record.as_dict() if hasattr(record, "as_dict") else dict(record)
    obj["_digest"] = digest(obj)
    p = CYCLE_DIR / ("cycle_{:03d}.json".format(int(obj["cycle"])))
    # Stamp the writer so a fork is visible in the record itself rather than being
    # reconstructed from a merge conflict afterwards (LIM-011).
    try:
        from .allocator import worker_id
        obj.setdefault("written_by", worker_id())
    except Exception:                                                 # noqa: BLE001
        pass
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return p


def read_cycles() -> list:
    if not CYCLE_DIR.exists():
        return []
    out = []
    for p in sorted(CYCLE_DIR.glob("cycle_*.json")):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return out


def integrity() -> dict:
    """Report torn lines per store. A non-zero count is not necessarily a problem -- it is the
    expected signature of a kill during a write -- but it must be visible rather than silently
    swallowed, because a reader comparing counts across reports deserves to know."""
    out = {}
    for name in STORES:
        p = _path(name)
        if not p.exists():
            out[name] = {"lines": 0, "parsed": 0, "torn": 0}
            continue
        lines = parsed = 0
        with p.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                lines += 1
                try:
                    json.loads(line)
                    parsed += 1
                except json.JSONDecodeError:
                    pass
        out[name] = {"lines": lines, "parsed": parsed, "torn": lines - parsed}
    return out


def summary() -> dict:
    """Counts used by the four-hour report. Cheap enough to call every cycle."""
    genomes = current("genomes")
    claims = current("claims")
    holes = current("holes")
    confounds = current("confounds")
    return {
        "genomes": len(genomes),
        "genomes_with_fulltext": sum(1 for g in genomes.values() if g.get("fulltext_available")),
        "genomes_open_access": sum(1 for g in genomes.values() if g.get("open_access")),
        "genomes_with_code": sum(1 for g in genomes.values() if g.get("code_edges")),
        "claims": len(claims),
        "claims_present": sum(1 for c in claims.values() if c.get("predicate") == "CLAIM_PRESENT"),
        "claims_supported": sum(1 for c in claims.values()
                                if c.get("predicate") == "CLAIM_SUPPORTED"),
        "mechanism_isolated": sum(1 for c in claims.values()
                                  if c.get("predicate") == "MECHANISM_ISOLATED"),
        "claims_confirmed": sum(1 for c in claims.values()
                                if c.get("adjudication") == "CONFIRMED"),
        "claims_proposed": sum(1 for c in claims.values()
                               if c.get("adjudication") == "PROPOSED"),
        # Per-predicate confirmation counts. These exist because the first Charon report
        # printed the ALL-predicates confirmed total (63) under a label reading "of which
        # CONFIRMED by P3", which read as 51% mechanism isolation on abstract-only evidence.
        # The true figure was 2 of 123 (1.6%). A cross-predicate total under a single-predicate
        # label is precisely the inflated number this campaign exists to avoid producing.
        "mechanism_isolated_confirmed": sum(
            1 for c in claims.values()
            if c.get("predicate") == "MECHANISM_ISOLATED" and c.get("adjudication") == "CONFIRMED"),
        "mechanism_isolated_refuted": sum(
            1 for c in claims.values()
            if c.get("predicate") == "MECHANISM_ISOLATED" and c.get("adjudication") == "REFUTED"),
        "holes_candidate": sum(1 for h in holes.values()
                               if h.get("status") == "COVERAGE_HOLE_CANDIDATE"),
        "holes_persistent": sum(1 for h in holes.values()
                                if h.get("status") == "PERSISTENT_COVERAGE_HOLE"),
        "holes_killed": sum(1 for h in holes.values()
                            if h.get("status", "").startswith("KILLED")),
        "confounds": len(confounds),
        "confounds_with_cost_migration": sum(1 for c in confounds.values()
                                             if c.get("cost_migration")),
        "retrieval_attempts": sum(1 for _ in read("retrieval")),
        "rejected_sources": sum(1 for _ in read("rejected")),
        "cycles_recorded": len(read_cycles()),
    }
