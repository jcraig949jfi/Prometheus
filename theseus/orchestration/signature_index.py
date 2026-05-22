"""Persistent cross-batch claim-shape signature index.

Per advisory board (Fire #50 critique, Claude + ChatGPT convergent):
each batch's CorpusWriter resets its _seen set, so the substrate's
in-batch dedup catches re-emissions WITHIN a batch but is blind to
cross-batch repetition. Penelope reports 90% downstream duplicates
because the substrate keeps re-emitting claim SHAPES (not just
record_ids — the record_id includes batch_id and other ephemerals).

This module is the substrate's persistent memory: a sqlite index
keyed on `claim_shape_signature` per generator, tracking how many
times each shape has been emitted across all fires.

The "claim shape" is the abstract claim TEMPLATE — what relation,
what catalog × invariant pair, what verdict class — independent of
the specific instance (which knot, which EC). A1 emitting
`equal(knot.crossing_number, ec.rank)` over 1M random knot/EC pairs
produces 1 unique signature, not 1M.

Schema:
    CREATE TABLE signatures (
        signature       TEXT PRIMARY KEY,
        generator_id    TEXT NOT NULL,
        verdict_class   TEXT NOT NULL,
        claim_kind      TEXT NOT NULL,
        first_seen_at   TEXT NOT NULL,
        last_seen_at    TEXT NOT NULL,
        seen_count      INTEGER NOT NULL,
        first_batch_id  TEXT NOT NULL,
        last_batch_id   TEXT NOT NULL
    );

The signature is computed by `compute_signature(record)`, which has
per-gen-family logic to extract the claim-shape from the record's
claim_payload. New gen-families fall back to (generator_id, claim_kind).
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Tuple

from theseus.config import THESEUS_ROOT
from theseus.emit.record_schema import TheseusRecord, Verdict


SIGNATURE_INDEX_PATH = (
    THESEUS_ROOT / "orchestration" / "signature_index.sqlite"
)


def _verdict_class(verdict: str) -> str:
    """Collapse verdicts into terminal classes for signature purposes."""
    if verdict in (
        Verdict.PROMOTED.value,
        Verdict.SHADOW_CATALOG.value,
    ):
        return "CONFIRM"
    if verdict == Verdict.REJECTED.value:
        return "KILL"
    if verdict == Verdict.INCONCLUSIVE.value:
        return "INCONCLUSIVE"
    return "UNVERIFIED"


def compute_signature(record: TheseusRecord) -> str:
    """Derive the claim-shape signature from a record.

    Strips instance-specific info (which knot, which EC, which value)
    leaving the CLAIM TEMPLATE. Same shape across many records means
    the substrate has been testing the same hypothesis at scale.
    """
    gid = record.generator_id
    kind = record.claim_kind
    vclass = _verdict_class(record.verdict)
    payload = record.claim_payload or {}

    # Family A (catalog cross-product), F (probabilistic): paired catalog+invariant
    if {"catalog_a", "invariant_a", "catalog_b", "invariant_b"}.issubset(payload):
        rel = payload.get("relation", "?")
        cat_a = payload.get("catalog_a", "?")
        inv_a = payload.get("invariant_a", "?")
        cat_b = payload.get("catalog_b", "?")
        inv_b = payload.get("invariant_b", "?")
        # Canonical order
        a = f"{cat_a}.{inv_a}"
        b = f"{cat_b}.{inv_b}"
        if a > b:
            a, b = b, a
        return f"{gid}:{rel}:{a}|{b}:{vclass}"

    # Family B (operator-action), some C: (operator, invariant) or operator-only
    if "operator" in payload:
        op = payload.get("operator", "?")
        inv = payload.get("invariant") or payload.get("input_invariant")
        if inv:
            return f"{gid}:op_{op}:{inv}:{vclass}"
        return f"{gid}:op_{op}:{vclass}"

    # Family G1: galois twist (twist class + invariant)
    if "twist_class_j" in payload:
        inv = payload.get("invariant", "?")
        return f"{gid}:twist:{inv}:{vclass}"

    # Family G2: functional equation per conductor band
    if "conductor" in payload and gid == "g2":
        cond = payload.get("conductor", 0)
        # Bucket conductors by order of magnitude
        bucket = "0" if cond <= 0 else str(10 ** (len(str(int(cond))) - 1))
        return f"{gid}:fe:cond_bucket_{bucket}:{vclass}"

    # Family G3: Hasse bound (prime)
    if "prime" in payload and gid == "g3":
        # Bucket primes by order of magnitude for signature coarsening
        p = payload.get("prime", 0)
        bucket = "small" if p < 100 else ("mid" if p < 1000 else "large")
        return f"{gid}:hasse:p_{bucket}:{vclass}"

    # Family E (literature): per-source signature
    if kind == "literature_mined":
        src = payload.get("source_path") or payload.get("arxiv_id") or \
              payload.get("page_title") or payload.get("knowl_id") or "unknown"
        # Coarsen to source directory / arxiv category
        src_str = str(src).split("/")[0] if "/" in str(src) else str(src)[:32]
        return f"{gid}:lit:{src_str}:{vclass}"

    # Fallback
    return f"{gid}:{kind}:{vclass}"


class SignatureIndex:
    """Persistent sqlite-backed cross-batch claim-shape memory."""

    SCHEMA = """
        CREATE TABLE IF NOT EXISTS signatures (
            signature       TEXT PRIMARY KEY,
            generator_id    TEXT NOT NULL,
            verdict_class   TEXT NOT NULL,
            claim_kind      TEXT NOT NULL,
            first_seen_at   TEXT NOT NULL,
            last_seen_at    TEXT NOT NULL,
            seen_count      INTEGER NOT NULL,
            first_batch_id  TEXT NOT NULL,
            last_batch_id   TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_gen ON signatures(generator_id);
        CREATE INDEX IF NOT EXISTS idx_kind ON signatures(claim_kind);
        CREATE INDEX IF NOT EXISTS idx_last_seen ON signatures(last_seen_at);
    """

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path if path is not None else SIGNATURE_INDEX_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.executescript(self.SCHEMA)

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def record(self, record: TheseusRecord) -> bool:
        """Upsert a record's signature. Returns True iff this was a
        NOVEL signature (first time the substrate has seen this shape)."""
        sig = compute_signature(record)
        now = datetime.now(timezone.utc).isoformat()
        with self._conn() as c:
            cur = c.execute(
                "SELECT seen_count FROM signatures WHERE signature = ?",
                (sig,),
            )
            row = cur.fetchone()
            if row is None:
                c.execute(
                    "INSERT INTO signatures (signature, generator_id, "
                    "verdict_class, claim_kind, first_seen_at, last_seen_at, "
                    "seen_count, first_batch_id, last_batch_id) "
                    "VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)",
                    (
                        sig, record.generator_id, _verdict_class(record.verdict),
                        record.claim_kind, now, now,
                        record.batch_id, record.batch_id,
                    ),
                )
                return True
            else:
                c.execute(
                    "UPDATE signatures SET seen_count = seen_count + 1, "
                    "last_seen_at = ?, last_batch_id = ? "
                    "WHERE signature = ?",
                    (now, record.batch_id, sig),
                )
                return False

    def record_many(self, records: Iterator[TheseusRecord]) -> Tuple[int, int]:
        """Bulk insert; returns (n_novel, n_total)."""
        n_novel = 0
        n_total = 0
        for r in records:
            n_total += 1
            if self.record(r):
                n_novel += 1
        return n_novel, n_total

    def count_signatures(
        self,
        generator_id: Optional[str] = None,
    ) -> int:
        with self._conn() as c:
            if generator_id is None:
                cur = c.execute("SELECT COUNT(*) FROM signatures")
            else:
                cur = c.execute(
                    "SELECT COUNT(*) FROM signatures WHERE generator_id = ?",
                    (generator_id,),
                )
            return cur.fetchone()[0]

    def summary_by_gen(self) -> Dict[str, Dict[str, Any]]:
        """Return per-generator: n_unique_signatures + total_seen_count."""
        with self._conn() as c:
            cur = c.execute(
                "SELECT generator_id, COUNT(*), SUM(seen_count) "
                "FROM signatures GROUP BY generator_id"
            )
            return {
                gid: {"n_unique_signatures": n_unique, "total_seen": total}
                for gid, n_unique, total in cur.fetchall()
            }

    def saturation_score(self, generator_id: str) -> Optional[float]:
        """Estimate generator's saturation: 1 - (n_unique / total_seen).
        Returns None if total_seen=0. High = saturated."""
        with self._conn() as c:
            cur = c.execute(
                "SELECT COUNT(*), SUM(seen_count) FROM signatures "
                "WHERE generator_id = ?",
                (generator_id,),
            )
            n_unique, total = cur.fetchone()
            if not total or total == 0:
                return None
            return 1.0 - (n_unique / total)

    def top_signatures(
        self,
        n: int = 20,
        generator_id: Optional[str] = None,
    ) -> list:
        """Return top-N signatures by seen_count (most-repeated)."""
        with self._conn() as c:
            if generator_id is None:
                cur = c.execute(
                    "SELECT signature, generator_id, seen_count, claim_kind, verdict_class "
                    "FROM signatures ORDER BY seen_count DESC LIMIT ?",
                    (n,),
                )
            else:
                cur = c.execute(
                    "SELECT signature, generator_id, seen_count, claim_kind, verdict_class "
                    "FROM signatures WHERE generator_id = ? "
                    "ORDER BY seen_count DESC LIMIT ?",
                    (generator_id, n),
                )
            return [
                {
                    "signature": sig, "generator_id": gid,
                    "seen_count": sc, "claim_kind": ck,
                    "verdict_class": vc,
                }
                for sig, gid, sc, ck, vc in cur.fetchall()
            ]


# Module-level singleton — daemon imports and uses this directly
INSTANCE = SignatureIndex()
