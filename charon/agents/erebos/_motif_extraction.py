"""Motif extraction — first Layer 2 primitive (Phase 1C ITER-40).

Per Erebos Doctrine v1.0 §"Layer 2 — cross-emission accumulator":
the kill_ledger as queryable failure geometry. ITER-40 ships the
first query — surfacing recurring patterns across emissions that
subsequent Layer 2 primitives (tensor v0, null-space, rank-
expansion, cross-domain transfer) build on.

## What a motif is

A motif is a recurring pattern across ledger rows. Four kinds:

1. **plugin_kp motif** — same (plugin_id, kill_pattern) pair recurs.
   Tells us which plugin-detector combinations are common.
   Baseline frequency map.

2. **plugin_domain_kp motif** — same (plugin_id, domain,
   kill_pattern) triple recurs. Stronger than plugin_kp: separates
   "G10 fires sharp_boundary_detected in Mahler" from "G10 fires
   sharp_boundary_detected in BSD." Maps directly onto the
   (plugin, domain, kp) coordinate that ITER-41's tensor will use
   as a cell key.

3. **kp_chain motif** — same (kp_prev, kp_next) pair appears across
   consecutive emissions on related inputs. Feeds the kp routing
   wire from ITER-38: which routing transitions are common, and
   which are unique?

4. **confusion motif** — same input_signature gets two or more
   distinct kill_patterns across different emissions. These are
   the inputs where the substrate's verdict is unstable — i.e.,
   eligible for revocation per ITER-39.

## What this primitive is NOT

- NOT a generator. Motifs are read-side aggregations; they do not
  produce new ComposedClaims.
- NOT a quality filter. A high-count plugin_kp motif may be a
  real failure-geometry feature OR a calibration artifact. Layer 2
  navigation decides which.
- NOT a tensor. The tensor (ITER-41) will use motifs as cell
  counts; ITER-40 just surfaces the cells.
- NOT a clustering algorithm. Two motifs that look similar are
  not merged; G22's clique loader handles that downstream.

## Storage-backend independence

The extractors take an `Iterable[dict]` of ledger rows. Each row
is expected to have at least `plugin_id` and `kill_pattern`; the
specific keys per extractor are documented per function. The
primitive never reads files directly — the daemon / a composition
loader hands it rows. This matches the LedgerContext pattern from
ITER-35.

## Reference patterns

G15 ledger MI (charon/agents/stygian/loaders/composition_g15_*.py)
- multi-ledger union read. G22 subgraph clique
(charon/agents/erebos/generators/g22_subgraph_clique.py) - greedy
co-occurrence detection. Both consulted for ledger-row shape but
neither produces motifs.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Optional


# Motif type sentinels — used as the .motif_type field on Motif.
MOTIF_PLUGIN_KP = "plugin_kp"
MOTIF_PLUGIN_DOMAIN_KP = "plugin_domain_kp"
MOTIF_KP_CHAIN = "kp_chain"
MOTIF_CONFUSION = "confusion"

ALL_MOTIF_TYPES = (
    MOTIF_PLUGIN_KP,
    MOTIF_PLUGIN_DOMAIN_KP,
    MOTIF_KP_CHAIN,
    MOTIF_CONFUSION,
)


@dataclass(frozen=True)
class Motif:
    """A recurring pattern in the kill_ledger.

    Attributes:
        motif_type: one of ALL_MOTIF_TYPES.
        key: the pattern values (e.g. ("g11_exception_miner",
            "catalog_flag_inconsistent") for plugin_kp). Tuple
            shape is per-motif-type and documented per extractor.
        count: how many ledger rows match this pattern.
        fraction: count / total_rows_scanned. Always in [0.0, 1.0].
        sample_row_ids: up to N sample row ids that contributed to
            this motif (N defaults to 5 in extractors). Tuple so
            Motif is hashable.
        sample_payload: optional per-motif metadata. For confusion
            motifs, the set of distinct kps observed. Frozen via
            JSON-able primitive types.
    """
    motif_type: str
    key: tuple
    count: int
    fraction: float
    sample_row_ids: tuple[str, ...]
    sample_payload: tuple = ()


@dataclass(frozen=True)
class MotifExtractionResult:
    """Output of one extractor call.

    motifs are sorted by count descending; ties broken by key
    lexicographically for stable output across runs.
    """
    motif_type: str
    n_rows_scanned: int
    motifs: tuple[Motif, ...]
    min_count_threshold: int
    notes: str = ""

    def top(self, k: int) -> tuple[Motif, ...]:
        """Convenience: return the top-k motifs."""
        return self.motifs[:k]

    def count_at_or_above(self, threshold: int) -> int:
        """Count of motifs with count >= threshold."""
        return sum(1 for m in self.motifs if m.count >= threshold)


# ---------------------------------------------------------------------
# Shared core
# ---------------------------------------------------------------------

def _row_id(row: dict) -> Optional[str]:
    """Return row's id under the conventional keys (row_id / id /
    composed_id). None if no id present."""
    return (
        row.get("row_id")
        or row.get("id")
        or row.get("composed_id")
    )


def _count_motifs(
    rows: list[dict],
    key_fn: Callable[[dict], Optional[tuple]],
    *,
    motif_type: str,
    min_count: int,
    sample_limit: int = 5,
    payload_fn: Optional[Callable[[list[dict]], tuple]] = None,
) -> MotifExtractionResult:
    """Generic motif counter.

    key_fn(row) returns the motif key tuple, or None to skip the row.
    Rows whose key_fn returns None are NOT counted in n_rows_scanned
    so the denominator is the well-formed row count, not the total
    ingest. payload_fn(matching_rows) optionally produces a per-motif
    metadata tuple.
    """
    by_key: defaultdict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        key = key_fn(row)
        if key is None:
            continue
        by_key[key].append(row)

    n_scanned = sum(len(v) for v in by_key.values())
    if n_scanned == 0:
        return MotifExtractionResult(
            motif_type=motif_type,
            n_rows_scanned=0,
            motifs=(),
            min_count_threshold=min_count,
            notes=f"no rows had a well-formed {motif_type} key",
        )

    motifs: list[Motif] = []
    for key, matching in by_key.items():
        count = len(matching)
        if count < min_count:
            continue
        sample_ids = tuple(
            rid for rid in (_row_id(r) for r in matching[:sample_limit])
            if rid is not None
        )
        payload = payload_fn(matching) if payload_fn is not None else ()
        motifs.append(Motif(
            motif_type=motif_type,
            key=key,
            count=count,
            fraction=count / n_scanned,
            sample_row_ids=sample_ids,
            sample_payload=payload,
        ))

    # Stable sort: count desc, then key asc
    motifs.sort(key=lambda m: (-m.count, m.key))

    return MotifExtractionResult(
        motif_type=motif_type,
        n_rows_scanned=n_scanned,
        motifs=tuple(motifs),
        min_count_threshold=min_count,
        notes=(
            f"{len(motifs)} motifs at count >= {min_count} over "
            f"{n_scanned} well-formed rows"
        ),
    )


# ---------------------------------------------------------------------
# Extractor 1: plugin_kp motifs
# ---------------------------------------------------------------------

def extract_plugin_kp_motifs(
    rows: Iterable[dict],
    *,
    min_count: int = 3,
    sample_limit: int = 5,
) -> MotifExtractionResult:
    """Co-occurring (plugin_id, kill_pattern) pairs across ledger rows.

    Key shape: (plugin_id: str, kill_pattern: str).

    PROMOTED rows (kill_pattern is None) use the sentinel "PROMOTED"
    so they're countable as a motif distinct from any specific kp.

    Rows missing plugin_id are skipped (well-formed denominator).
    """
    rows_list = list(rows)

    def key_fn(row: dict) -> Optional[tuple]:
        pid = row.get("plugin_id")
        if not pid:
            return None
        kp = row.get("kill_pattern") or "PROMOTED"
        return (pid, kp)

    return _count_motifs(
        rows_list,
        key_fn,
        motif_type=MOTIF_PLUGIN_KP,
        min_count=min_count,
        sample_limit=sample_limit,
    )


# ---------------------------------------------------------------------
# Extractor 2: plugin_domain_kp motifs (tensor-cell shape)
# ---------------------------------------------------------------------

def extract_plugin_domain_kp_motifs(
    rows: Iterable[dict],
    *,
    min_count: int = 2,
    sample_limit: int = 5,
    default_domain: str = "unspecified",
) -> MotifExtractionResult:
    """Co-occurring (plugin_id, domain, kill_pattern) triples.

    Key shape: (plugin_id: str, domain: str, kill_pattern: str).

    Tensor-cell-shaped output — directly usable as cell keys for
    the ITER-41 kill_tensor.

    Rows missing domain use `default_domain` so they're not dropped
    silently; tracks how many rows lacked an explicit domain.
    """
    rows_list = list(rows)

    def key_fn(row: dict) -> Optional[tuple]:
        pid = row.get("plugin_id")
        if not pid:
            return None
        domain = row.get("domain") or default_domain
        kp = row.get("kill_pattern") or "PROMOTED"
        return (pid, domain, kp)

    return _count_motifs(
        rows_list,
        key_fn,
        motif_type=MOTIF_PLUGIN_DOMAIN_KP,
        min_count=min_count,
        sample_limit=sample_limit,
    )


# ---------------------------------------------------------------------
# Extractor 3: kp_chain motifs (routing transitions)
# ---------------------------------------------------------------------

def extract_kp_chain_motifs(
    rows: Iterable[dict],
    *,
    min_count: int = 2,
    sample_limit: int = 5,
) -> MotifExtractionResult:
    """(kp_prev, kp_next) chains across consecutive ledger rows.

    Key shape: (kp_prev: str, kp_next: str).

    Rows are assumed to be in chronological order as passed in
    (the caller's responsibility — no internal sort). PROMOTED uses
    the "PROMOTED" sentinel as for plugin_kp.

    A row with no plugin_id breaks the chain (we don't pair across
    malformed rows).
    """
    rows_list = list(rows)

    # Build the pair sequence; key_fn pattern doesn't apply here
    # because pairs span two rows. Use a custom shape.
    by_key: defaultdict[tuple, list[dict]] = defaultdict(list)
    prev_kp: Optional[str] = None
    n_pairs_scanned = 0
    for row in rows_list:
        if not row.get("plugin_id"):
            prev_kp = None  # chain break
            continue
        kp_now = row.get("kill_pattern") or "PROMOTED"
        if prev_kp is not None:
            by_key[(prev_kp, kp_now)].append(row)
            n_pairs_scanned += 1
        prev_kp = kp_now

    if n_pairs_scanned == 0:
        return MotifExtractionResult(
            motif_type=MOTIF_KP_CHAIN,
            n_rows_scanned=0,
            motifs=(),
            min_count_threshold=min_count,
            notes=(
                "no consecutive well-formed row pairs available "
                "for kp_chain extraction"
            ),
        )

    motifs: list[Motif] = []
    for key, matching in by_key.items():
        count = len(matching)
        if count < min_count:
            continue
        sample_ids = tuple(
            rid for rid in (_row_id(r) for r in matching[:sample_limit])
            if rid is not None
        )
        motifs.append(Motif(
            motif_type=MOTIF_KP_CHAIN,
            key=key,
            count=count,
            fraction=count / n_pairs_scanned,
            sample_row_ids=sample_ids,
        ))

    motifs.sort(key=lambda m: (-m.count, m.key))

    return MotifExtractionResult(
        motif_type=MOTIF_KP_CHAIN,
        n_rows_scanned=n_pairs_scanned,
        motifs=tuple(motifs),
        min_count_threshold=min_count,
        notes=(
            f"{len(motifs)} chain motifs at count >= {min_count} over "
            f"{n_pairs_scanned} consecutive row pairs"
        ),
    )


# ---------------------------------------------------------------------
# Extractor 4: confusion motifs (same input, conflicting kps)
# ---------------------------------------------------------------------

def extract_confusion_motifs(
    rows: Iterable[dict],
    *,
    min_distinct_kps: int = 2,
    sample_limit: int = 5,
) -> MotifExtractionResult:
    """Input signatures that receive multiple distinct kill_patterns.

    Key shape: (input_signature: str,).

    A confusion motif fires when the same canonical input has
    been emitted against multiple times with two-or-more DIFFERENT
    kill_patterns. These are exactly the inputs where the
    eligibility gate's CRITERION_FALSIFIES_PRIOR would have fired
    (per ITER-35) and where ITER-39 revocations are warranted.

    `count` is the number of rows for the signature (NOT the number
    of distinct kps). `sample_payload` carries the set of distinct
    kps observed as a tuple of strings.

    Rows missing input_signature are skipped.
    """
    rows_list = list(rows)
    by_sig: defaultdict[str, list[dict]] = defaultdict(list)
    for row in rows_list:
        sig = row.get("input_signature")
        if not sig:
            continue
        by_sig[sig].append(row)

    n_scanned = sum(len(v) for v in by_sig.values())
    if n_scanned == 0:
        return MotifExtractionResult(
            motif_type=MOTIF_CONFUSION,
            n_rows_scanned=0,
            motifs=(),
            min_count_threshold=min_distinct_kps,
            notes="no rows had input_signature",
        )

    motifs: list[Motif] = []
    for sig, matching in by_sig.items():
        kps = {r.get("kill_pattern") or "PROMOTED" for r in matching}
        if len(kps) < min_distinct_kps:
            continue
        count = len(matching)
        sample_ids = tuple(
            rid for rid in (_row_id(r) for r in matching[:sample_limit])
            if rid is not None
        )
        # Sort kps for deterministic payload
        payload = tuple(sorted(kps))
        motifs.append(Motif(
            motif_type=MOTIF_CONFUSION,
            key=(sig,),
            count=count,
            fraction=count / n_scanned,
            sample_row_ids=sample_ids,
            sample_payload=payload,
        ))

    motifs.sort(key=lambda m: (-m.count, m.key))

    return MotifExtractionResult(
        motif_type=MOTIF_CONFUSION,
        n_rows_scanned=n_scanned,
        motifs=tuple(motifs),
        min_count_threshold=min_distinct_kps,
        notes=(
            f"{len(motifs)} confusion motifs with >= "
            f"{min_distinct_kps} distinct kps per signature, "
            f"over {n_scanned} signed rows"
        ),
    )


# ---------------------------------------------------------------------
# Convenience: run all four extractors at once
# ---------------------------------------------------------------------

def extract_all_motifs(
    rows: Iterable[dict],
    *,
    min_count: int = 2,
) -> dict[str, MotifExtractionResult]:
    """Run all four extractors with the same min_count threshold.

    Returns a dict keyed by motif_type. Convenient for one-shot
    Layer 2 audits; per-extractor knobs are not surfaced (use the
    individual extractors when you need them).
    """
    rows_list = list(rows)
    return {
        MOTIF_PLUGIN_KP: extract_plugin_kp_motifs(
            rows_list, min_count=min_count
        ),
        MOTIF_PLUGIN_DOMAIN_KP: extract_plugin_domain_kp_motifs(
            rows_list, min_count=min_count
        ),
        MOTIF_KP_CHAIN: extract_kp_chain_motifs(
            rows_list, min_count=min_count
        ),
        MOTIF_CONFUSION: extract_confusion_motifs(
            rows_list, min_distinct_kps=max(min_count, 2)
        ),
    }
