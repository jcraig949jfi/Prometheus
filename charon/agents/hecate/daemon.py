"""Hecate — continuous gradient archaeology over the kill ledger (Charon child, MVP).

One tick = scan Theseus's corpus (and fallback ledger locations) for
kill records, compute MI(kill_pattern, generator_id) with permutation-null
baseline, identify top kill-pattern clusters, emit
gradient_archaeology_run artifact.

See `charon/agents/hecate/CHARTER.md` for the one-page brief.
"""
from __future__ import annotations

import gzip
import json
import math
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Optional

from charon.agents._base import CharonAgent
from harmonia.agents._base import REPO_ROOT


# Ledger candidates in priority order. Hecate uses the first that exists
# and contains records with `kill_pattern`.
LEDGER_CANDIDATES: list[Path] = [
    REPO_ROOT / "theseus" / "corpus",  # Theseus's TheseusRecord emissions
]

# Sampling caps so a huge ledger doesn't blow MVP-tick budget.
MAX_RECORDS_PER_TICK = 5000
N_PERMUTATIONS = 200
MIN_CLUSTER_SIZE = 5
MI_DRIFT_THRESHOLD = 2.0
ALARM_CONSECUTIVE_THRESHOLD = 7


def _iter_jsonl_gz(path: Path) -> Iterator[dict]:
    try:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    except Exception:
        return


def _iter_jsonl(path: Path) -> Iterator[dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    except Exception:
        return


def _harvest_records(corpus_dir: Path, max_records: int) -> list[dict]:
    """Read jsonl[.gz] records from a directory. Returns first max_records."""
    out: list[dict] = []
    if not corpus_dir.exists():
        return out
    if corpus_dir.is_file():
        files = [corpus_dir]
    else:
        files = sorted(corpus_dir.glob("*.jsonl.gz")) + sorted(corpus_dir.glob("*.jsonl"))
    for p in files:
        if len(out) >= max_records:
            break
        iterator = _iter_jsonl_gz(p) if p.suffix == ".gz" else _iter_jsonl(p)
        for rec in iterator:
            if len(out) >= max_records:
                break
            out.append(rec)
    return out


def _entropy(counts: list[int]) -> float:
    total = sum(counts)
    if total <= 0:
        return 0.0
    h = 0.0
    for c in counts:
        if c <= 0:
            continue
        p = c / total
        h -= p * math.log2(p)
    return h


def _joint_entropy(pairs: list[tuple[str, str]]) -> float:
    c = Counter(pairs)
    return _entropy(list(c.values()))


def _mi(x_labels: list[str], y_labels: list[str]) -> float:
    """Mutual information in bits between two categorical sequences."""
    assert len(x_labels) == len(y_labels)
    if not x_labels:
        return 0.0
    cx = Counter(x_labels)
    cy = Counter(y_labels)
    pairs = list(zip(x_labels, y_labels))
    hx = _entropy(list(cx.values()))
    hy = _entropy(list(cy.values()))
    hxy = _joint_entropy(pairs)
    return max(0.0, hx + hy - hxy)


def _permutation_null(
    x_labels: list[str], y_labels: list[str], n_perms: int
) -> tuple[float, float]:
    """Return (null_mean, null_std) for MI under label-permutation."""
    if not x_labels:
        return 0.0, 0.0
    nulls: list[float] = []
    y_shuffled = list(y_labels)
    rng = random.Random(20260519)
    for _ in range(n_perms):
        rng.shuffle(y_shuffled)
        nulls.append(_mi(x_labels, y_shuffled))
    mu = sum(nulls) / len(nulls)
    var = sum((v - mu) ** 2 for v in nulls) / max(1, len(nulls) - 1)
    return mu, math.sqrt(var)


class HecateAgent(CharonAgent):
    """Continuous gradient archaeology over the kill ledger."""

    name = "Hecate"
    role = "continuous gradient archaeology over the kill ledger"

    # ---- backlog ----------------------------------------------------------

    def self_generate_backlog(self) -> list[dict]:
        """Hecate's backlog is the ledger itself — always one item per tick
        (re-run gradient archaeology on the latest ledger). Returns a
        single 'analyze' job pointing at the first available ledger."""
        for candidate in LEDGER_CANDIDATES:
            if candidate.exists():
                if candidate.is_dir():
                    # Check if it has any jsonl[.gz] files
                    has_data = any(candidate.glob("*.jsonl.gz")) or any(candidate.glob("*.jsonl"))
                    if has_data:
                        return [{"ledger": str(candidate), "kind": "directory"}]
                else:
                    return [{"ledger": str(candidate), "kind": "file"}]
        return []

    # ---- analysis ---------------------------------------------------------

    def _analyze(self, ledger_dir: Path) -> dict:
        records = _harvest_records(ledger_dir, MAX_RECORDS_PER_TICK)
        # Extract (kill_pattern, generator_id) pairs from records that have
        # both. Records without a kill_pattern (PROMOTED, UNVERIFIED) get
        # bucketed as "PROMOTED" / "UNVERIFIED" so the analysis still
        # captures the verdict-distribution context.
        x_labels: list[str] = []  # kill_pattern OR verdict-fallback
        y_labels: list[str] = []  # generator_id (operator-class proxy)
        verdict_counts: Counter = Counter()
        for rec in records:
            kp = rec.get("kill_pattern")
            gen = rec.get("generator_id") or rec.get("source") or "unknown"
            verdict = rec.get("verdict") or "UNKNOWN"
            verdict_counts[verdict] += 1
            if kp:
                x_labels.append(str(kp))
                y_labels.append(str(gen))
        n_with_kp = len(x_labels)
        mi_obs = _mi(x_labels, y_labels)
        mi_null_mean, mi_null_std = _permutation_null(x_labels, y_labels, N_PERMUTATIONS)
        if mi_null_std > 0:
            mi_z = (mi_obs - mi_null_mean) / mi_null_std
        else:
            mi_z = 0.0
        # Top kill_pattern clusters
        kp_counter = Counter(x_labels)
        top_patterns = kp_counter.most_common(15)
        clusters: list[dict] = []
        for kp, cnt in kp_counter.items():
            if cnt >= MIN_CLUSTER_SIZE:
                gens_for_kp = [y for x, y in zip(x_labels, y_labels) if x == kp]
                top_gen = Counter(gens_for_kp).most_common(3)
                clusters.append({
                    "kill_pattern": kp,
                    "size": cnt,
                    "top_generators": top_gen,
                })
        clusters.sort(key=lambda d: -d["size"])
        # Top generators
        gen_counter = Counter(y_labels)
        top_generators = gen_counter.most_common(10)
        return {
            "ledger_dir": str(ledger_dir),
            "total_records": len(records),
            "records_with_kill_pattern": n_with_kp,
            "verdict_distribution": dict(verdict_counts.most_common()),
            "n_unique_kill_patterns": len(kp_counter),
            "n_unique_generators": len(gen_counter),
            "top_kill_patterns": top_patterns,
            "top_generators": top_generators,
            "mi_observed": round(mi_obs, 4),
            "mi_null_mean": round(mi_null_mean, 4),
            "mi_null_std": round(mi_null_std, 4),
            "mi_z": round(mi_z, 3),
            "clusters_at_or_above_min_size": clusters[:10],
            "n_permutations": N_PERMUTATIONS,
        }

    # ---- artifact writers -------------------------------------------------

    def _emit_archaeology_run(self, analysis: dict, alarm: Optional[str]) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"gradient_archaeology_{utc}.md"
        lines: list[str] = []
        lines.append(f"# Hecate gradient archaeology — {utc}")
        lines.append("")
        lines.append(f"- emitted_at: {datetime.now(timezone.utc).isoformat()}")
        lines.append(f"- emitted_by: Hecate (charon/agents/hecate/daemon.py)")
        lines.append(f"- ledger_dir: `{analysis['ledger_dir']}`")
        lines.append(f"- total_records_scanned: {analysis['total_records']}")
        lines.append(f"- records_with_kill_pattern: {analysis['records_with_kill_pattern']}")
        lines.append(f"- n_unique_kill_patterns: {analysis['n_unique_kill_patterns']}")
        lines.append(f"- n_unique_generators (operator-class proxy): {analysis['n_unique_generators']}")
        lines.append("")
        lines.append("## MI(kill_pattern, generator_id)")
        lines.append("")
        lines.append(f"- mi_observed: **{analysis['mi_observed']} bits**")
        lines.append(f"- mi_null_mean: {analysis['mi_null_mean']} bits")
        lines.append(f"- mi_null_std: {analysis['mi_null_std']}")
        lines.append(f"- mi_z: **{analysis['mi_z']}**")
        lines.append(f"- n_permutations: {analysis['n_permutations']}")
        lines.append("")
        if alarm:
            lines.append("## SELF_AUDIT_ALARM")
            lines.append("")
            lines.append(alarm)
            lines.append("")
        lines.append("## Verdict distribution")
        lines.append("")
        for v, c in analysis["verdict_distribution"].items():
            lines.append(f"- {v}: {c}")
        lines.append("")
        lines.append("## Top kill patterns")
        lines.append("")
        for kp, cnt in analysis["top_kill_patterns"][:10]:
            lines.append(f"- `{kp}` — {cnt}")
        lines.append("")
        lines.append("## Top generators (operator-class proxy)")
        lines.append("")
        for gen, cnt in analysis["top_generators"]:
            lines.append(f"- `{gen}` — {cnt}")
        lines.append("")
        lines.append("## Kill-pattern clusters (≥ {} members)".format(MIN_CLUSTER_SIZE))
        lines.append("")
        if not analysis["clusters_at_or_above_min_size"]:
            lines.append("- (none — ledger too small or kill_pattern coverage too sparse this round)")
        else:
            for c in analysis["clusters_at_or_above_min_size"]:
                top_gens = ", ".join(f"{g}({n})" for g, n in c["top_generators"])
                lines.append(f"- `{c['kill_pattern']}` — size {c['size']}; top generators: {top_gens}")
        lines.append("")
        lines.append("## Interpretation hint")
        lines.append("")
        lines.append("MI(kill_pattern, generator_id) > 0 means kills are non-uniformly distributed across generators — different generators fail in characteristically different ways, and the kill geometry has structure. The README's headline number is 0.725 bits across 314K kills; this tick's number on Theseus's local corpus is a smaller sample and may differ. The mi_z score is the cleaner signal: |mi_z| > 2.0 says the observed MI is significantly above what label-shuffling would produce.")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by Hecate (charon/agents/hecate/daemon.py). MVP gradient archaeology — KillVector-embedding clustering (HDBSCAN) deferred to v0.2.*")
        return self.write_artifact(fname, "\n".join(lines))

    def _emit_ledger_absent(self) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"ledger_absent_{utc}.md"
        lines = [
            "# Hecate — kill ledger absent",
            "",
            f"- at: {datetime.now(timezone.utc).isoformat()}",
            "",
            "No kill-ledger candidate found this tick. Hecate searched (in priority order):",
            "",
        ]
        for c in LEDGER_CANDIDATES:
            lines.append(f"- `{c.relative_to(REPO_ROOT)}` (exists: {c.exists()})")
        lines.append("")
        lines.append("Required for execution: either Theseus's corpus to land kill_pattern-bearing records, or another ledger to be registered in `LEDGER_CANDIDATES` in this daemon. SELF_AUDIT_NULL emission is the correct behavior here — the alarm is that gradient archaeology cannot proceed.")
        lines.append("")
        return self.write_artifact(fname, "\n".join(lines))

    def _emit_self_audit_null(self, reason: str) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"self_audit_null_{utc}.md"
        return self.write_artifact(fname, f"# Hecate SELF_AUDIT_NULL\n\n- reason: {reason}\n- at: {datetime.now(timezone.utc).isoformat()}\n")

    # ---- alarm tracking --------------------------------------------------

    def _update_alarm_state(self, mi_z: float) -> Optional[str]:
        history = self.load_state("mi_z_history", []) or []
        history.append({
            "at": datetime.now(timezone.utc).isoformat(),
            "mi_z": mi_z,
        })
        history = history[-30:]
        self.save_state("mi_z_history", history)
        # Check for consecutive low-mi_z ticks
        recent = history[-ALARM_CONSECUTIVE_THRESHOLD:]
        if len(recent) >= ALARM_CONSECUTIVE_THRESHOLD and all(r["mi_z"] < MI_DRIFT_THRESHOLD for r in recent):
            return (
                f"mi_z < {MI_DRIFT_THRESHOLD} for {ALARM_CONSECUTIVE_THRESHOLD} consecutive ticks. "
                "Either kill geometry is decaying (signal weakening) or operator_class taxonomy is stale. "
                "Surface to Aporia/Techne for triage."
            )
        return None

    # ---- run_tick ---------------------------------------------------------

    def run_tick(self, dry_run: bool = False) -> dict:
        stats: dict[str, Any] = {
            "items_processed": 0,
            "artifacts_written": 0,
            "errors": 0,
            "backlog_remaining": 0,
            "ledger_found": None,
            "total_records": 0,
            "mi_observed": None,
            "mi_z": None,
            "alarm": False,
        }
        artifacts: list[str] = []

        backlog = self.self_generate_backlog()
        stats["backlog_remaining"] = max(0, len(backlog) - 1)

        if not backlog:
            try:
                if not dry_run:
                    out = self._emit_ledger_absent()
                    artifacts.append(str(out))
                    stats["artifacts_written"] += 1
                stats["items_processed"] += 1
            except Exception as e:
                self.log.exception(f"ledger-absent emit failed: {e}")
                stats["errors"] += 1
        else:
            item = backlog[0]
            ledger_dir = Path(item["ledger"])
            stats["ledger_found"] = str(ledger_dir.relative_to(REPO_ROOT))
            try:
                if dry_run:
                    stats["items_processed"] += 1
                else:
                    analysis = self._analyze(ledger_dir)
                    stats["total_records"] = analysis["total_records"]
                    stats["mi_observed"] = analysis["mi_observed"]
                    stats["mi_z"] = analysis["mi_z"]
                    alarm = self._update_alarm_state(analysis["mi_z"])
                    stats["alarm"] = bool(alarm)
                    out = self._emit_archaeology_run(analysis, alarm)
                    artifacts.append(str(out))
                    stats["items_processed"] += 1
                    stats["artifacts_written"] += 1
            except Exception as e:
                self.log.exception(f"gradient archaeology failed: {e}")
                stats["errors"] += 1

        summary = (
            f"ledger={stats['ledger_found']} "
            f"records={stats['total_records']} "
            f"mi={stats['mi_observed']} mi_z={stats['mi_z']} "
            f"alarm={stats['alarm']} "
            f"artifacts={stats['artifacts_written']} "
            f"errors={stats['errors']}"
        )
        self.log_work(
            "hecate_tick_complete",
            summary=summary,
            output_path=artifacts[0] if artifacts else None,
            success=stats["errors"] == 0,
        )
        return stats
