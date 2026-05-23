"""Persistent cross-batch claim-shape signature index.

Per advisory board (Fire #50 critique, Claude + ChatGPT convergent):
each batch's CorpusWriter resets its _seen set, so the substrate's
in-batch dedup catches re-emissions WITHIN a batch but is blind to
cross-batch repetition. Penelope reports 90% downstream duplicates
because the substrate keeps re-emitting claim SHAPES (not just
record_ids — the record_id includes batch_id and other ephemerals).

PERFORMANCE NOTE (Fire #53 fix): per-record sqlite open/commit was
the daemon's bottleneck (~5-10ms per record dropped Fire #53 from
the expected 5M-records-in-90min to 18K-in-90min). Fixed by buffering
records in memory and flushing in a single transaction per batch.
The buffer carries at most one entry per (signature, ...) key since
within-batch repeats just bump an in-memory counter.

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


def _coarsen_relation(rel: str) -> str:
    """Bucket abs_diff_le_K to coarse classes so K=39 vs K=40 collapse.

    Per Fire #55 finding: c4 produced 2,211 "unique" shapes that were
    all abs_diff_le_K variants (K from 34-49+). Same RELATION at
    different precision thresholds is not substrate-novel; same shape.
    """
    if rel.startswith("abs_diff_le_"):
        try:
            k = int(rel.split("_")[-1])
        except ValueError:
            return rel
        if k <= 3:
            return "abs_diff_le_tight"
        if k <= 10:
            return "abs_diff_le_mid"
        return "abs_diff_le_wide"
    return rel


def compute_signature(record: TheseusRecord) -> str:
    """Derive the claim-shape signature from a record.

    Strips instance-specific info (which knot, which EC, which value)
    leaving the CLAIM TEMPLATE. Same shape across many records means
    the substrate has been testing the same hypothesis at scale.

    Fire #55 update: abs_diff_le_K relations are coarsened to 3 buckets
    (tight/mid/wide) — each K-value was previously a distinct shape,
    inflating c4/c1 "novelty" counts.
    """
    gid = record.generator_id
    kind = record.claim_kind
    vclass = _verdict_class(record.verdict)
    payload = record.claim_payload or {}

    # Family A (catalog cross-product), F (probabilistic): paired catalog+invariant
    if {"catalog_a", "invariant_a", "catalog_b", "invariant_b"}.issubset(payload):
        rel = _coarsen_relation(payload.get("relation", "?"))
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

    # Family D + H (triangulation, kill-neighborhood, self-play):
    # uses {knot_invariant, ec_invariant} directly (no catalog prefix).
    # Fire #56 fix per cross-batch novelty inflation diagnosis: these
    # were collapsing to fallback `{gid}:{kind}:{vclass}` signatures.
    if "knot_invariant" in payload and "ec_invariant" in payload:
        ki = payload.get("knot_invariant", "?")
        ei = payload.get("ec_invariant", "?")
        degree = payload.get("polynomial_degree")
        if degree is not None:
            return f"{gid}:tri:knot.{ki}|ec.{ei}:deg{degree}:{vclass}"
        return f"{gid}:tri:knot.{ki}|ec.{ei}:{vclass}"

    # h1 self-play: invariant_a/invariant_b without catalog prefix
    if "invariant_a" in payload and "invariant_b" in payload and "hunter_varied_side" in payload:
        ia = payload.get("invariant_a", "?")
        ib = payload.get("invariant_b", "?")
        side = payload.get("hunter_varied_side", "?")
        # Canonical order
        a, b = (ia, ib) if ia <= ib else (ib, ia)
        return f"{gid}:hunt:{a}|{b}:varied_{side}:{vclass}"

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
        # In-memory buffer per-batch. record() updates this dict;
        # flush() writes it to sqlite in a single transaction.
        # {signature: (generator_id, verdict_class, claim_kind, count, batch_id)}
        self._buffer: Dict[str, Tuple[str, str, str, int, str]] = {}
        # Per-gen breakdown of cross-batch-novel signatures, populated
        # by flush(). Cleared at the start of each flush.
        # Lets the daemon route novelty back into yield_score so the
        # bandit can prefer gens that contribute *new* shapes rather
        # than gens that contribute *many* records.
        self._last_flush_novel_by_gen: Dict[str, int] = {}

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def record(self, record: TheseusRecord) -> bool:
        """Buffer the record's signature in memory. Returns True iff
        this signature is first-seen WITHIN THIS BUFFER (call flush()
        to learn true cross-batch novelty).

        Hot-path optimization: O(1) dict update, no sqlite touch.
        Per-record cost is ~10us vs 5-10ms for the per-record sqlite
        path that bottlenecked Fire #53.
        """
        sig = compute_signature(record)
        if sig in self._buffer:
            gid, vc, ck, cnt, batch_id = self._buffer[sig]
            self._buffer[sig] = (gid, vc, ck, cnt + 1, record.batch_id)
            return False
        self._buffer[sig] = (
            record.generator_id,
            _verdict_class(record.verdict),
            record.claim_kind,
            1,
            record.batch_id,
        )
        return True  # first-in-buffer; cross-batch novelty learned at flush

    def flush(self) -> Tuple[int, int]:
        """Persist buffered signatures to sqlite in a single transaction.
        Returns (n_novel_cross_batch, n_signatures_flushed).

        Should be called once at batch end. Safe to call with empty
        buffer (no-op).
        """
        # Reset per-gen novelty breakdown for this flush. Even on
        # empty-buffer return, downstream callers see a fresh dict.
        self._last_flush_novel_by_gen = {}
        if not self._buffer:
            return (0, 0)
        now = datetime.now(timezone.utc).isoformat()
        n_novel = 0
        n_total = len(self._buffer)
        with self._conn() as c:
            for sig, (gid, vc, ck, cnt, batch_id) in self._buffer.items():
                cur = c.execute(
                    "SELECT seen_count FROM signatures WHERE signature = ?",
                    (sig,),
                )
                row = cur.fetchone()
                if row is None:
                    c.execute(
                        "INSERT INTO signatures (signature, generator_id, "
                        "verdict_class, claim_kind, first_seen_at, "
                        "last_seen_at, seen_count, first_batch_id, "
                        "last_batch_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (sig, gid, vc, ck, now, now, cnt, batch_id, batch_id),
                    )
                    n_novel += 1
                    self._last_flush_novel_by_gen[gid] = (
                        self._last_flush_novel_by_gen.get(gid, 0) + 1
                    )
                else:
                    c.execute(
                        "UPDATE signatures SET seen_count = seen_count + ?, "
                        "last_seen_at = ?, last_batch_id = ? "
                        "WHERE signature = ?",
                        (cnt, now, batch_id, sig),
                    )
        self._buffer.clear()
        return (n_novel, n_total)

    def last_flush_novel_by_gen(self) -> Dict[str, int]:
        """Return per-generator novel-signature count from the most-recent
        flush(). Empty dict if no flush has occurred or no novelty.
        Used by the daemon to feed novelty back into yield_score.
        """
        return dict(self._last_flush_novel_by_gen)

    def record_many(self, records: Iterator[TheseusRecord]) -> Tuple[int, int]:
        """Buffer-then-flush helper; returns (n_novel, n_total)."""
        n_first_in_buffer = 0
        n_total = 0
        for r in records:
            n_total += 1
            if self.record(r):
                n_first_in_buffer += 1
        novel_cross, _ = self.flush()
        return novel_cross, n_total

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

    def count_unique_signatures_for_roles(
        self,
        non_discovery_gids: set,
    ) -> int:
        """Count unique signatures EXCLUDING records from non-discovery
        roles (TAUTOLOGY_CONTROL, NULL_BASELINE, INFRA_DIAGNOSTIC).

        Per advisory board: substrate discovery novelty should not be
        inflated by tautology-control or null-baseline emissions even
        if they produce many shape variants.
        """
        with self._conn() as c:
            if not non_discovery_gids:
                cur = c.execute("SELECT COUNT(*) FROM signatures")
                return cur.fetchone()[0]
            placeholders = ",".join(["?"] * len(non_discovery_gids))
            cur = c.execute(
                f"SELECT COUNT(*) FROM signatures "
                f"WHERE generator_id NOT IN ({placeholders})",
                tuple(non_discovery_gids),
            )
            return cur.fetchone()[0]

    def saturation_score(
        self,
        generator_id: str,
        min_total_seen: int = 1000,
    ) -> Optional[float]:
        """Estimate generator's saturation: 1 - (n_unique / total_seen).
        Returns None if total_seen < min_total_seen (insufficient sample
        size for a reliable estimate). High = saturated.

        Fire #67 lesson: c5 had sat=9% from total_seen=22 (n=2 prior
        fires) — a statistical regression-to-mean artifact, not real
        exploration. Once c5 fired at scale (60K records), saturation
        immediately jumped to 100%.

        Default `min_total_seen=1000` prevents this. Callers can lower
        the threshold for diagnostic queries but the yield_score path
        uses the default — a gen needs to have actually run substantially
        before the bandit trusts the saturation estimate.
        """
        with self._conn() as c:
            cur = c.execute(
                "SELECT COUNT(*), SUM(seen_count) FROM signatures "
                "WHERE generator_id = ?",
                (generator_id,),
            )
            n_unique, total = cur.fetchone()
            if not total or total < min_total_seen:
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
