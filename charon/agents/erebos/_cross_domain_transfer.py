"""Cross-domain transfer — fifth Layer 2 primitive (Phase 1C ITER-44).

Per Erebos Doctrine v1.0 §"Layer 2": the substrate's distinctive
contribution is failure metabolization across emissions.
Cross-domain transfer asks the substrate's first cross-domain
prediction question:

> "Given a (plugin, kp) pattern populated in domain A, is the
>  analogous (plugin, kp) populated in domain B?"

Three outcomes per (plugin, kp) pattern:

  1. CONFIRMED -- populated in both A and B. The transfer worked.
  2. MISSED    -- populated in A, NOT in B. Either we haven't
                  emitted the analog yet (go probe), or domain B
                  has a structurally different shape on this
                  pattern (the missing-cell IS the finding).
  3. NOVEL     -- populated in B but not A. Target has structure
                  source doesn't.

The transfer RATE between domain A and B is the fraction of
patterns populated in A that are also populated in B. Low rates
between sibling domains indicate structural divergence; high
rates indicate shared geometry.

Closes Phase 1C. Sets up Sprint-1's cross-domain ablation
experiments: if Layer 2 has navigable value, transfer predictions
on held-out (plugin, kp) cells should beat a Layer-1-only random
baseline.

## What this primitive is NOT

- NOT a generator. Read-side only.
- NOT a substitute for actually running the cross-domain
  composition loader. Transfer predictions are HYPOTHESES; the
  substrate's job is to falsify them with Layer 1 verdicts.
- NOT a similarity / embedding model. Pattern matching is exact
  (plugin, kp); semantic kp similarity (the kill_pattern
  registry's confusion_class) is a separate concern.

## Storage-backend independence

Takes a KillTensor (ITER-41). Inherits backend portability.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Optional

from charon.agents.erebos._kill_tensor import (
    AXIS_DOMAIN,
    AXIS_KP,
    AXIS_NAMES,
    AXIS_PLUGIN,
    KillTensor,
    N_AXES,
)


# Default transfer key: which axes define a "pattern" that should
# transfer across domains. Excludes DOMAIN (the scan axis) and
# INVARIANT (commonly bag-of-signatures; too granular to transfer
# directly at v0).
DEFAULT_TRANSFER_KEY_AXES = (AXIS_PLUGIN, AXIS_KP)


@dataclass(frozen=True)
class TransferReport:
    """Result of one transfer prediction between two domains.

    Attributes:
        source_domain: the from-domain.
        target_domain: the to-domain.
        key_axes: axes used to define a transferable pattern.
        confirmed: patterns populated in both source and target.
        missed: patterns populated in source only.
        novel: patterns populated in target only.
        n_source: count of source-populated patterns.
        n_target: count of target-populated patterns.
        transfer_rate: |confirmed| / n_source. None when n_source == 0.
        notes: human-readable summary.
    """
    source_domain: str
    target_domain: str
    key_axes: tuple[int, ...]
    confirmed: frozenset[tuple]
    missed: frozenset[tuple]
    novel: frozenset[tuple]
    n_source: int
    n_target: int
    transfer_rate: Optional[float]
    notes: str = ""

    def key_axis_names(self) -> tuple[str, ...]:
        return tuple(AXIS_NAMES[a] for a in self.key_axes)


@dataclass(frozen=True)
class TransferPairTable:
    """All-pairs transfer rate matrix."""
    domains: tuple[str, ...]
    rates: dict[tuple[str, str], Optional[float]]
    n_patterns: dict[str, int]
    notes: str = ""

    def rate(self, source: str, target: str) -> Optional[float]:
        return self.rates.get((source, target))


def _validate_key_axes(key_axes: tuple[int, ...]) -> tuple[int, ...]:
    if not key_axes:
        raise ValueError("key_axes must be non-empty")
    if any(a < 0 or a >= N_AXES for a in key_axes):
        raise ValueError(
            f"key_axes values must be in 0..{N_AXES - 1}; got {key_axes}"
        )
    if AXIS_DOMAIN in key_axes:
        raise ValueError(
            "key_axes must NOT include AXIS_DOMAIN (the scan axis)"
        )
    if len(set(key_axes)) != len(key_axes):
        raise ValueError(f"key_axes has duplicates: {key_axes}")
    return tuple(sorted(set(key_axes)))


def _patterns_in_domain(
    tensor: KillTensor,
    domain: str,
    key_axes: tuple[int, ...],
) -> set[tuple]:
    """Set of pattern keys (values along key_axes) populated in
    the given domain."""
    patterns: set[tuple] = set()
    for cell in tensor.cells:
        if cell[AXIS_DOMAIN] != domain:
            continue
        patterns.add(tuple(cell[a] for a in key_axes))
    return patterns


def predict_transfer(
    tensor: KillTensor,
    *,
    source_domain: str,
    target_domain: str,
    key_axes: tuple[int, ...] = DEFAULT_TRANSFER_KEY_AXES,
) -> TransferReport:
    """Compare source-domain patterns against target-domain patterns.

    Args:
        tensor: KillTensor with cells from both domains.
        source_domain: the from-domain.
        target_domain: the to-domain.
        key_axes: axes defining a transferable pattern. Default
            (PLUGIN, KP); caller can extend with INVARIANT for
            finer-grained transfer, or restrict to (PLUGIN,) for
            coarser.

    Returns:
        TransferReport with confirmed / missed / novel pattern sets
        and the aggregate transfer_rate.
    """
    if source_domain == target_domain:
        raise ValueError(
            "predict_transfer: source_domain and target_domain must "
            "differ"
        )
    key_axes = _validate_key_axes(key_axes)
    source_patterns = _patterns_in_domain(tensor, source_domain, key_axes)
    target_patterns = _patterns_in_domain(tensor, target_domain, key_axes)

    confirmed = source_patterns & target_patterns
    missed = source_patterns - target_patterns
    novel = target_patterns - source_patterns

    n_source = len(source_patterns)
    n_target = len(target_patterns)
    transfer_rate = (
        len(confirmed) / n_source if n_source > 0 else None
    )

    if n_source == 0 and n_target == 0:
        notes = (
            f"neither {source_domain!r} nor {target_domain!r} has "
            f"populated patterns; transfer undefined"
        )
    elif n_source == 0:
        notes = (
            f"source {source_domain!r} has no populated patterns; "
            f"transfer_rate undefined. Target {target_domain!r} has "
            f"{n_target} novel patterns."
        )
    elif n_target == 0:
        notes = (
            f"target {target_domain!r} has no populated patterns; "
            f"all {n_source} source patterns are missed."
        )
    else:
        notes = (
            f"{len(confirmed)}/{n_source} source patterns confirmed "
            f"in target (rate={transfer_rate:.4f}); "
            f"{len(missed)} missed; {len(novel)} novel-in-target"
        )

    return TransferReport(
        source_domain=source_domain,
        target_domain=target_domain,
        key_axes=key_axes,
        confirmed=frozenset(confirmed),
        missed=frozenset(missed),
        novel=frozenset(novel),
        n_source=n_source,
        n_target=n_target,
        transfer_rate=transfer_rate,
        notes=notes,
    )


def all_pairs_transfer(
    tensor: KillTensor,
    *,
    key_axes: tuple[int, ...] = DEFAULT_TRANSFER_KEY_AXES,
) -> TransferPairTable:
    """Compute transfer rates for every ordered (source, target)
    pair of distinct domains in the tensor.

    Returns a TransferPairTable. Diagonal entries (source == target)
    are excluded. The result is the substrate's first cross-domain
    map -- which domain pairs share geometry vs which diverge.
    """
    key_axes = _validate_key_axes(key_axes)
    domains = sorted(tensor.axis_values(AXIS_DOMAIN))
    if not domains:
        return TransferPairTable(
            domains=(),
            rates={},
            n_patterns={},
            notes="tensor has no domain values",
        )
    # Precompute patterns per domain (O(D x cells))
    patterns_by_domain: dict[str, set[tuple]] = {
        d: _patterns_in_domain(tensor, d, key_axes) for d in domains
    }
    rates: dict[tuple[str, str], Optional[float]] = {}
    for src in domains:
        for tgt in domains:
            if src == tgt:
                continue
            s_p = patterns_by_domain[src]
            t_p = patterns_by_domain[tgt]
            if not s_p:
                rates[(src, tgt)] = None
            else:
                rates[(src, tgt)] = len(s_p & t_p) / len(s_p)
    return TransferPairTable(
        domains=tuple(domains),
        rates=rates,
        n_patterns={d: len(patterns_by_domain[d]) for d in domains},
        notes=(
            f"all-pairs transfer over {len(domains)} domains; "
            f"key_axes = {tuple(AXIS_NAMES[a] for a in key_axes)}"
        ),
    )


def missed_patterns_priority(
    report: TransferReport,
    tensor: KillTensor,
) -> list[tuple[tuple, int]]:
    """Rank missed patterns by their source-domain prevalence.

    A missed pattern that occurs MANY times in the source domain
    is a higher-priority probe candidate than one that occurs once.
    Returns list of (pattern_key, source_count) tuples, sorted
    by source_count descending.
    """
    counts: defaultdict[tuple, int] = defaultdict(int)
    for cell, n in tensor.cells.items():
        if cell[AXIS_DOMAIN] != report.source_domain:
            continue
        pattern = tuple(cell[a] for a in report.key_axes)
        if pattern in report.missed:
            counts[pattern] += n
    return sorted(counts.items(), key=lambda kv: -kv[1])
