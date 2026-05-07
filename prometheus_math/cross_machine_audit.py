"""Cross-machine determinism audit harness for kill records.

Per inbox ticket T-2026-05-07-T013 (P1-high, Aporia 2026-05-07): James
operates two machines (M1 ``F:\\Prometheus``, M2 ``D:\\Prometheus``).
Cross-machine substrate-output divergence is a class of bug currently
undetectable. This module provides the **substrate-side** canonical-hash
computation; the cross-machine **orchestration** (running the audit on
M1 + M2, comparing reports, paging on divergence) is Charon's concern
(coordination ticket filed at ``aporia/meta/queue/charon_inbox.jsonl``
per acceptance #5).

The canonical hash is keyed by:

  * **The KillVector's content-addressed serialization** — component
    data, ``candidate_hash``, ``operator_class``, ``region_meta`` —
    but NOT ``timestamp`` (wall-clock; varies across runs by design).
    Components are sorted by ``falsifier_name`` before hashing so
    component order does not enter identity (per acceptance #3:
    permutation of independent fields is a no-op).

  * **The substrate version** — a static string for now; bumped when
    KillVector / KillComponent serialized shape changes. Two machines
    on different substrate versions MUST produce different hashes
    (per acceptance #4: hash unstable under semantic transformations).

  * **The transformation chain** — tuple of named operations applied
    upstream; empty for raw records. Two records that have been through
    different transformation pipelines MUST hash differently even if
    the resulting KillVector content is identical (otherwise we lose
    provenance in the cross-machine comparison).

NO contract change to KillVector / KillComponent / sigma_kernel — this
module is purely additive and operates on the existing public API
(``KillVector.to_dict()`` + Python ``hashlib``).

CLI
---
::

    python -m prometheus_math.cross_machine_audit \\
        --kill-store PATH [--substrate-version v2.3.0] [--out PATH]

Outputs:
  * Markdown report at ``--out`` (default
    ``prometheus_math/CROSS_MACHINE_AUDIT_RESULTS.md``).
  * Returns dict ``{candidate_hash -> canonical_hash}`` for
    programmatic use; the comparison logic
    (:func:`compare_against_remote_report`) takes a remote dict in the
    same shape.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from prometheus_math.kill_vector import KillVector


# ---------------------------------------------------------------------------
# Substrate version constant
# ---------------------------------------------------------------------------


SUBSTRATE_VERSION_FOR_AUDIT: str = "v2.3.0"
"""Substrate-shape version used as part of the canonical hash key.

Bump this string when KillVector / KillComponent serialized shape
changes (e.g. a new component field is added, a stability_pass schema
shifts). Two machines on different versions MUST produce different
hashes, by design — this is the cross-machine substrate-version-
divergence detector.

Per HARD-3 closed-loop discipline: deliberately a string constant in
this module rather than read from a settings file; the audit's
ground-truth shouldn't itself be configurable at audit time."""


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CanonicalHashInput:
    """One audit input: a kill record + the substrate version + the
    transformation chain that produced it.

    Two CanonicalHashInputs with identical fields produce the same
    canonical_hash. The transformation_chain field is stored as a tuple
    of strings so order is preserved (the chain is a sequence, not a
    set — applying ``[A, B]`` and ``[B, A]`` MUST hash differently)."""

    kill_record: KillVector
    substrate_version: str = SUBSTRATE_VERSION_FOR_AUDIT
    transformation_chain: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.kill_record, KillVector):
            raise TypeError(
                f"kill_record must be a KillVector; got "
                f"{type(self.kill_record).__name__}"
            )
        if not isinstance(self.substrate_version, str) or not self.substrate_version:
            raise ValueError(
                f"substrate_version must be a non-empty string; got "
                f"{self.substrate_version!r}"
            )
        if not isinstance(self.transformation_chain, tuple):
            raise TypeError(
                f"transformation_chain must be a tuple of strings; got "
                f"{type(self.transformation_chain).__name__}"
            )
        for op in self.transformation_chain:
            if not isinstance(op, str):
                raise TypeError(
                    f"transformation_chain entries must be strings; got "
                    f"{type(op).__name__}"
                )


@dataclass(frozen=True)
class HashComparisonResult:
    """Result of comparing one local hash against the remote report."""

    candidate_hash: str
    local_canonical_hash: str
    remote_canonical_hash: Optional[str]
    matches: bool
    diagnosis: str


@dataclass(frozen=True)
class CrossMachineAuditReport:
    """Aggregate result for a corpus of records audited against a
    remote-machine report."""

    n_records_local: int
    n_records_remote: int
    n_compared: int
    n_matching: int
    n_diverging: int
    n_only_local: int
    n_only_remote: int
    diverging: Tuple[HashComparisonResult, ...] = field(default_factory=tuple)
    only_local: Tuple[str, ...] = field(default_factory=tuple)
    only_remote: Tuple[str, ...] = field(default_factory=tuple)
    substrate_version: str = SUBSTRATE_VERSION_FOR_AUDIT


# ---------------------------------------------------------------------------
# Canonical hash
# ---------------------------------------------------------------------------


def _canonicalize_kill_record_for_audit(kv: KillVector) -> Dict[str, Any]:
    """Build the audit-grade canonical dict from a KillVector.

    Differences from KillVector.to_dict():
      * Drops ``timestamp`` (wall-clock; varies across runs by design).
      * Sorts ``components`` by ``falsifier_name`` so component order
        is not part of identity (per acceptance #3 — permutation of
        independent fields is a no-op).
      * Recursively sorts mapping keys at all depths (handled by
        ``json.dumps(..., sort_keys=True)`` at hash time).
    """
    raw = kv.to_dict()
    raw.pop("timestamp", None)
    components = raw.get("components") or []
    raw["components"] = sorted(
        components, key=lambda c: c.get("falsifier_name", "")
    )
    return raw


def canonical_hash(inp: CanonicalHashInput) -> str:
    """Compute the canonical SHA256 hash for an audit input.

    The hash is a deterministic function of:
      * the audit-canonicalized KillVector dict (timestamp dropped,
        components sorted by name)
      * the substrate version string
      * the transformation chain tuple

    Two machines running identical substrate code on identical kill
    records MUST produce identical hashes. Divergence is the substrate
    finding the audit is designed to surface.
    """
    payload = {
        "kill_record_canonical": _canonicalize_kill_record_for_audit(inp.kill_record),
        "substrate_version": inp.substrate_version,
        "transformation_chain": list(inp.transformation_chain),
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def canonical_hash_corpus(
    inputs: Sequence[CanonicalHashInput],
) -> Dict[str, str]:
    """Compute canonical hashes for a corpus of records, keyed by each
    record's ``candidate_hash`` field. Used to produce the local report
    that gets compared against the remote machine's report.
    """
    out: Dict[str, str] = {}
    for inp in inputs:
        out[inp.kill_record.candidate_hash] = canonical_hash(inp)
    return out


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------


def compare_against_remote_report(
    local_inputs: Sequence[CanonicalHashInput],
    remote_report: Dict[str, str],
) -> CrossMachineAuditReport:
    """Compare a local audit corpus against a remote-machine report.

    The remote report is a dict {candidate_hash -> canonical_hash} as
    produced by :func:`canonical_hash_corpus` running on the second
    machine. The comparison reports:

      * **n_matching** — same candidate_hash produces same canonical_hash
        on both machines (the green-light case)
      * **n_diverging** — same candidate_hash produces DIFFERENT
        canonical_hashes (substrate-level cross-machine bug; this is
        what the audit is designed to surface)
      * **n_only_local** / **n_only_remote** — record present on one
        machine but not the other (orchestration concern, not a
        substrate bug; reported for Charon's coordination view)
    """
    local_hashes = canonical_hash_corpus(local_inputs)
    local_keys = set(local_hashes)
    remote_keys = set(remote_report)
    common = local_keys & remote_keys
    diverging: List[HashComparisonResult] = []
    n_matching = 0
    for cand_hash in sorted(common):
        local_h = local_hashes[cand_hash]
        remote_h = remote_report[cand_hash]
        if local_h == remote_h:
            n_matching += 1
        else:
            diverging.append(
                HashComparisonResult(
                    candidate_hash=cand_hash,
                    local_canonical_hash=local_h,
                    remote_canonical_hash=remote_h,
                    matches=False,
                    diagnosis=(
                        "canonical hashes diverge — substrate-level "
                        "cross-machine bug. Investigate substrate version "
                        "drift, dict-ordering, or non-deterministic "
                        "computation in the kill-record producer."
                    ),
                )
            )
    only_local = tuple(sorted(local_keys - remote_keys))
    only_remote = tuple(sorted(remote_keys - local_keys))
    return CrossMachineAuditReport(
        n_records_local=len(local_keys),
        n_records_remote=len(remote_keys),
        n_compared=len(common),
        n_matching=n_matching,
        n_diverging=len(diverging),
        n_only_local=len(only_local),
        n_only_remote=len(only_remote),
        diverging=tuple(diverging),
        only_local=only_local,
        only_remote=only_remote,
    )


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def render_audit_report(report: CrossMachineAuditReport) -> str:
    """Render a CrossMachineAuditReport as a markdown string."""
    lines: List[str] = []
    lines.append("# Cross-Machine Determinism Audit")
    lines.append("")
    lines.append(
        f"_Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}_"
    )
    lines.append(
        f"_Per inbox ticket T-2026-05-07-T013 "
        f"(prometheus_math/cross_machine_audit.py)_"
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Substrate version (audit):** `{report.substrate_version}`")
    lines.append(f"- **Records on local machine:** {report.n_records_local}")
    lines.append(f"- **Records on remote machine:** {report.n_records_remote}")
    lines.append(f"- **Records compared (intersection):** {report.n_compared}")
    lines.append(f"- **Matching:** {report.n_matching}")
    lines.append(f"- **Diverging:** {report.n_diverging}")
    lines.append(f"- **Only on local:** {report.n_only_local}")
    lines.append(f"- **Only on remote:** {report.n_only_remote}")
    lines.append("")
    if report.n_diverging > 0:
        lines.append("## Substrate finding: divergent records")
        lines.append("")
        lines.append(
            f"**{report.n_diverging} record(s) produce different canonical "
            "hashes on the two machines.** This is a substrate-level bug — "
            "investigate substrate version drift, dict-ordering "
            "non-determinism, or non-deterministic computation in the "
            "kill-record producer."
        )
        lines.append("")
        lines.append("| candidate_hash | local hash | remote hash |")
        lines.append("|---|---|---|")
        for d in report.diverging[:50]:
            lines.append(
                f"| `{d.candidate_hash[:16]}...` | "
                f"`{d.local_canonical_hash[:16]}...` | "
                f"`{d.remote_canonical_hash[:16] if d.remote_canonical_hash else ''}...` |"
            )
        if len(report.diverging) > 50:
            lines.append(f"_(showing first 50 of {len(report.diverging)} divergences)_")
        lines.append("")
    else:
        lines.append("## Result")
        lines.append("")
        if report.n_compared == 0:
            lines.append(
                "No records to compare (intersection of local + remote keys "
                "is empty). This is an orchestration gap, not a substrate "
                "bug — Charon coordination required."
            )
        else:
            lines.append(
                f"All {report.n_matching} compared records produce identical "
                "canonical hashes on both machines. **No substrate-level "
                "cross-machine divergence detected.**"
            )
        lines.append("")
    if report.n_only_local > 0 or report.n_only_remote > 0:
        lines.append("## Coverage gaps (orchestration concern)")
        lines.append("")
        lines.append(
            "Records present on one machine but absent on the other are "
            "not a substrate bug — they reflect missing replication or "
            "orchestration mismatch. Surface for Charon coordination."
        )
        lines.append("")
        if report.n_only_local > 0:
            lines.append(
                f"- **{report.n_only_local}** record(s) only on local"
                f" (sample: {', '.join(report.only_local[:5])})"
            )
        if report.n_only_remote > 0:
            lines.append(
                f"- **{report.n_only_remote}** record(s) only on remote"
                f" (sample: {', '.join(report.only_remote[:5])})"
            )
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


_DEFAULT_REPORT_PATH = (
    Path(__file__).resolve().parent / "CROSS_MACHINE_AUDIT_RESULTS.md"
)


def _load_kill_records_from_pilot_store(path: Path) -> List[KillVector]:
    """Load KillVectors from the kill_vector pilot store schema (mirrors
    the loader in prometheus_math.triangulation_independence_audit)."""
    with open(path, encoding="utf-8") as f:
        store = json.load(f)
    pilot = store.get("pilot") or {}
    episodes = pilot.get("episodes") or []
    out: List[KillVector] = []
    for ep in episodes:
        kv_raw = ep.get("kill_vector") if isinstance(ep, dict) else None
        if kv_raw is None:
            continue
        out.append(KillVector.from_dict(kv_raw))
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m prometheus_math.cross_machine_audit",
        description=(
            "Compute canonical-hash report for a kill-record corpus. "
            "Output format consumable by a sister-machine run for "
            "cross-machine comparison (T-2026-05-07-T013)."
        ),
    )
    parser.add_argument(
        "--kill-store",
        type=Path,
        required=False,
        default=(
            Path(__file__).resolve().parent / "_native_kill_vector_pilot.json"
        ),
        help="Path to kill-record store JSON (default: _native_kill_vector_pilot.json)",
    )
    parser.add_argument(
        "--substrate-version",
        type=str,
        default=SUBSTRATE_VERSION_FOR_AUDIT,
        help=f"Substrate version string (default: {SUBSTRATE_VERSION_FOR_AUDIT})",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=_DEFAULT_REPORT_PATH,
        help=f"Markdown report output path (default: {_DEFAULT_REPORT_PATH.name})",
    )
    parser.add_argument(
        "--remote-report",
        type=Path,
        default=None,
        help=(
            "Optional path to remote-machine canonical-hash JSON report "
            "(produced by running this CLI on the second machine and "
            "saving the resulting hash dict). When provided, runs the "
            "comparison and renders the divergence report; when omitted, "
            "writes the local hash report only."
        ),
    )
    parser.add_argument(
        "--local-hashes-out",
        type=Path,
        default=None,
        help=(
            "Optional path to write the local {candidate_hash -> "
            "canonical_hash} JSON report (for handoff to the second "
            "machine). When omitted, prints to stdout."
        ),
    )
    args = parser.parse_args(argv)

    print(f"[audit] loading {args.kill_store}", file=sys.stderr)
    vectors = _load_kill_records_from_pilot_store(args.kill_store)
    print(f"[audit] loaded {len(vectors)} kill vectors", file=sys.stderr)

    inputs = [
        CanonicalHashInput(
            kill_record=kv,
            substrate_version=args.substrate_version,
        )
        for kv in vectors
    ]

    if args.remote_report is None:
        local_hashes = canonical_hash_corpus(inputs)
        if args.local_hashes_out is not None:
            args.local_hashes_out.write_text(
                json.dumps(local_hashes, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            print(
                f"[audit] wrote {len(local_hashes)} local hashes to "
                f"{args.local_hashes_out}",
                file=sys.stderr,
            )
        else:
            print(json.dumps(local_hashes, indent=2, sort_keys=True))
        return 0

    print(f"[audit] loading remote report from {args.remote_report}", file=sys.stderr)
    with open(args.remote_report, encoding="utf-8") as f:
        remote_report = json.load(f)
    if not isinstance(remote_report, dict):
        raise ValueError(
            f"remote-report must be a JSON dict; got {type(remote_report).__name__}"
        )
    report = compare_against_remote_report(inputs, remote_report)
    md = render_audit_report(report)
    args.out.write_text(md, encoding="utf-8")
    print(
        f"[audit] compared={report.n_compared}, matching={report.n_matching}, "
        f"diverging={report.n_diverging}, only_local={report.n_only_local}, "
        f"only_remote={report.n_only_remote}",
        file=sys.stderr,
    )
    print(f"[audit] markdown report written: {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "SUBSTRATE_VERSION_FOR_AUDIT",
    "CanonicalHashInput",
    "HashComparisonResult",
    "CrossMachineAuditReport",
    "canonical_hash",
    "canonical_hash_corpus",
    "compare_against_remote_report",
    "render_audit_report",
    "main",
]
