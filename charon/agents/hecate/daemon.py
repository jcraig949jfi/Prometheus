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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator, Optional

from charon.agents._base import CharonAgent
from charon.agents._shared_queues import stygian_priority_queue
from harmonia.agents._base import REPO_ROOT


# Ledger sources. Hecate MERGES records from every source that exists
# (changed 2026-05-23 from "first existing" semantics to support
# Stygian's executor emissions landing in a separate file). Each entry
# can be a directory (walked for .jsonl[.gz]) or a single .jsonl file.
LEDGER_CANDIDATES: list[Path] = [
    REPO_ROOT / "theseus" / "corpus",  # Theseus's TheseusRecord emissions
    REPO_ROOT / "charon" / "agents" / "stygian" / "state" / "kill_ledger.jsonl",  # Stygian executor emissions
    REPO_ROOT / "charon" / "agents" / "pollux" / "state" / "kill_ledger.jsonl",   # Pollux scan emissions (v0.5)
    REPO_ROOT / "charon" / "agents" / "hephaestus" / "state" / "kill_ledger.jsonl",  # Hephaestus composed-claim emissions (v0.7)
]

# Sampling caps so a huge ledger doesn't blow MVP-tick budget.
# Raised 5000 → 50000 (Techne 2026-05-19) so multi-batch corpora are
# represented even when per-batch sizes are uneven. The instrument's
# sampling strategy is itself part of the analysis: alphabetical-then-
# fill iteration on multi-shard corpora produces sampling-window
# artifacts (see charon/agents/hecate/TECHNE_PROMPT_2026-05-19.md
# retraction note for the original incident).
MAX_RECORDS_PER_TICK = 50000
N_PERMUTATIONS = 200
MIN_CLUSTER_SIZE = 5
MI_DRIFT_THRESHOLD = 2.0
ALARM_CONSECUTIVE_THRESHOLD = 7

# Stygian-priority queue dedup window. Was hardcoded 24h, which on a
# 4-min rotation drains the queue after Stygian consumes the initial
# burst and blocks re-emission until next day even as the kill_ledger
# churns. Shortened to 4h (one cluster re-fires after the data shifts
# meaningfully but stale rows don't replicate).
STYGIAN_QUEUE_DEDUP_HOURS = 4


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


def _harvest_records(corpus_dir: Path, max_records: int) -> tuple[list[dict], dict]:
    """Read jsonl[.gz] records from a directory with stratified sampling.

    Sampling strategy (post-Techne-2026-05-19 retraction):
    - Files sorted by mtime descending — newest batches first.
    - Per-file cap = ceil(max_records / n_files) so every batch contributes.
    - Second pass after the per-file cap loop fills remaining budget from
      whichever files still had records to give (the chronologically newest
      get the second-pass headroom first).

    Alphabetical-then-fill iteration on multi-shard corpora produces
    sampling-window artifacts — the original Hecate v0.1 hit this and
    misreported a monoculture finding that was actually an artifact of
    reading only the chronologically-first 54MB batch. Stratifying
    avoids that.

    Returns (records, sampling_context). sampling_context names every
    file inspected, its per-file take, and the global cap, so the artifact
    consumer can audit the data selection separately from the analysis.
    """
    out: list[dict] = []
    sampling_context: dict = {
        "corpus_dir": str(corpus_dir),
        "max_records_budget": max_records,
        "files_seen": [],
        "files_n": 0,
        "per_file_cap": None,
        "exhausted_budget": False,
    }
    if not corpus_dir.exists():
        return out, sampling_context
    if corpus_dir.is_file():
        files = [corpus_dir]
    else:
        all_files = list(corpus_dir.glob("*.jsonl.gz")) + list(corpus_dir.glob("*.jsonl"))
        # mtime descending — newest first
        try:
            files = sorted(all_files, key=lambda p: p.stat().st_mtime, reverse=True)
        except Exception:
            files = sorted(all_files)
    n_files = max(1, len(files))
    # Ceil division so per_file_cap * n_files >= max_records and stratification
    # actually fills the budget when each file has enough records.
    per_file_cap = max(1, (max_records + n_files - 1) // n_files)
    sampling_context["files_n"] = n_files
    sampling_context["per_file_cap"] = per_file_cap

    per_file_taken: dict[str, int] = {}
    # Pass 1: per-file cap. Every file gets a fair share.
    for p in files:
        if len(out) >= max_records:
            break
        iterator = _iter_jsonl_gz(p) if p.suffix == ".gz" else _iter_jsonl(p)
        taken = 0
        for rec in iterator:
            if len(out) >= max_records:
                break
            if taken >= per_file_cap:
                break
            out.append(rec)
            taken += 1
        per_file_taken[str(p)] = taken

    # Pass 2: if budget not filled, top up from files that still have records
    # (those whose per-file cap was below their actual record count).
    if len(out) < max_records:
        for p in files:
            if len(out) >= max_records:
                break
            already = per_file_taken.get(str(p), 0)
            if already < per_file_cap:
                # File was exhausted before hitting the per-file cap — skip
                # (no more records to give).
                continue
            iterator = _iter_jsonl_gz(p) if p.suffix == ".gz" else _iter_jsonl(p)
            # Skip the records we already took.
            skip = already
            for rec in iterator:
                if skip > 0:
                    skip -= 1
                    continue
                if len(out) >= max_records:
                    break
                out.append(rec)
                per_file_taken[str(p)] = per_file_taken.get(str(p), 0) + 1

    sampling_context["exhausted_budget"] = len(out) >= max_records
    sampling_context["total_records_taken"] = len(out)
    sampling_context["files_seen"] = [
        {
            "file": str(p.name) if hasattr(p, "name") else str(p),
            "records_taken": per_file_taken.get(str(p), 0),
        }
        for p in files
    ]
    return out, sampling_context


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
        (re-run gradient archaeology). Returns a single 'analyze' job
        listing every existing source in LEDGER_CANDIDATES so _analyze
        can merge them."""
        sources: list[dict] = []
        for candidate in LEDGER_CANDIDATES:
            if not candidate.exists():
                continue
            if candidate.is_dir():
                has_data = any(candidate.glob("*.jsonl.gz")) or any(candidate.glob("*.jsonl"))
                if has_data:
                    sources.append({"ledger": str(candidate), "kind": "directory"})
            else:
                sources.append({"ledger": str(candidate), "kind": "file"})
        if not sources:
            return []
        return [{"sources": sources, "kind": "multi"}]

    # ---- analysis ---------------------------------------------------------

    def _analyze(self, sources: list[dict]) -> dict:
        """Merge records from every source listed; compute MI signal.

        Measurement-circularity fix (2026-05-23): in addition to raw MI,
        compute a *cross-generator* MI restricted to kill_patterns that
        appear under >=2 distinct generator_ids. If a kill_pattern is
        only ever emitted by one generator (e.g., Theseus's a1 generator
        always emits a1_* patterns by design), it contributes
        tautological MI signal -- the prefix encodes the generator.
        Cross-generator MI strips that bias and reports what's genuinely
        emergent across operator classes.
        """
        records: list[dict] = []
        merged_sampling: list[dict] = []
        # Distribute per-source budget evenly; each source gets MAX/n.
        n_sources = max(1, len(sources))
        per_source_budget = max(1, MAX_RECORDS_PER_TICK // n_sources)
        for src in sources:
            src_path = Path(src["ledger"])
            recs, sc = _harvest_records(src_path, per_source_budget)
            records.extend(recs)
            merged_sampling.append(sc)
        sampling_context = {
            "max_records_budget": MAX_RECORDS_PER_TICK,
            "n_sources": n_sources,
            "per_source_budget": per_source_budget,
            "per_source_context": merged_sampling,
            "total_records_taken": len(records),
        }

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

        # --- Cross-generator MI (measurement-circularity audit) ---
        # Patch 2026-05-25: strip known generator prefixes from each
        # kill_pattern before checking cross-generator membership. Every
        # current generator (Theseus a1/a2/h2/etc., Stygian stygian_,
        # Pollux pollux_) prefix-codes its emissions, so the v0.4 audit
        # found ZERO cross-generator overlap by construction even
        # though the underlying patterns clearly map to shared themes
        # (e.g., stygian_f3_effect_size_below_threshold and
        # pollux_no_correlation_observed both reflect "weak signal").
        # Canonicalize to the post-prefix tail and the audit becomes
        # meaningful.
        import re
        _GEN_PREFIX_RE = re.compile(
            r"^(stygian|pollux|nephele|moros|acheron|lethe|hecate|"
            r"a\d+|h\d+|c\d+|f\d+)_+"
        )
        def _canon_kp(kp: str) -> str:
            return _GEN_PREFIX_RE.sub("", kp)

        from collections import defaultdict
        canon_to_gens: dict[str, set] = defaultdict(set)
        for kp, gen in zip(x_labels, y_labels):
            canon_to_gens[_canon_kp(kp)].add(gen)
        crossgen_canon = {
            ck for ck, gens in canon_to_gens.items() if len(gens) >= 2
        }
        # Pair indices restricted to records whose canonical kp is
        # cross-generator
        cg_pairs = [
            (_canon_kp(kp), gen) for kp, gen in zip(x_labels, y_labels)
            if _canon_kp(kp) in crossgen_canon
        ]
        if cg_pairs:
            xcg, ycg = zip(*cg_pairs)
            xcg, ycg = list(xcg), list(ycg)
            mi_crossgen = _mi(xcg, ycg)
            mi_cg_null_mean, mi_cg_null_std = _permutation_null(
                xcg, ycg, N_PERMUTATIONS
            )
            mi_crossgen_z = (
                (mi_crossgen - mi_cg_null_mean) / mi_cg_null_std
                if mi_cg_null_std > 0 else 0.0
            )
        else:
            mi_crossgen = 0.0
            mi_crossgen_z = 0.0
        n_crossgen_kps = len(crossgen_canon)
        n_crossgen_records = len(cg_pairs)
        # For artifact transparency: which canonical patterns crossed?
        crossgen_kp_top = sorted(
            crossgen_canon, key=lambda c: -len([1 for x in xcg if x == c])
        )[:10] if cg_pairs else []
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
            "ledger_sources": [s["ledger"] for s in sources],
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
            "mi_crossgen": round(mi_crossgen, 4),
            "mi_crossgen_z": round(mi_crossgen_z, 3),
            "n_crossgen_kill_patterns": n_crossgen_kps,
            "n_crossgen_records": n_crossgen_records,
            "crossgen_canonical_kp_top": crossgen_kp_top,
            "clusters_at_or_above_min_size": clusters[:10],
            "n_permutations": N_PERMUTATIONS,
            "sampling_context": sampling_context,
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
        srcs = analysis.get("ledger_sources") or []
        lines.append(f"- ledger_sources ({len(srcs)}):")
        for s in srcs:
            lines.append(f"  - `{s}`")
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
        lines.append("## MI cross-generator (measurement-circularity audit)")
        lines.append("")
        lines.append(
            "Raw MI conflates two effects: (1) genuine emergent operator "
            "structure in the kill geometry, and (2) tautology -- each "
            "Theseus generator emits kill_patterns prefixed with its own "
            "id (`a1_*` from a1, `h2_*` from h2, ...) by design. The "
            "cross-generator MI below restricts to kill_patterns that "
            "appear under >=2 distinct generator_ids; anything below "
            "that threshold is single-generator noise and excluded."
        )
        lines.append("")
        lines.append(f"- mi_crossgen: **{analysis['mi_crossgen']} bits**")
        lines.append(f"- mi_crossgen_z: **{analysis['mi_crossgen_z']}**")
        lines.append(f"- n_crossgen_kill_patterns: {analysis['n_crossgen_kill_patterns']} (of {analysis['n_unique_kill_patterns']} total)")
        lines.append(f"- n_crossgen_records: {analysis['n_crossgen_records']} (of {analysis['records_with_kill_pattern']} total)")
        lines.append("")
        if analysis.get("crossgen_canonical_kp_top"):
            lines.append("### Top canonical (prefix-stripped) cross-generator patterns")
            lines.append("")
            for c in analysis["crossgen_canonical_kp_top"]:
                lines.append(f"- `{c}`")
            lines.append("")
        lines.append(
            "Cross-gen audit was updated 2026-05-25 to strip known "
            "generator prefixes (stygian_, pollux_, a1_, h2_, c1_, "
            "f3_, etc.) before checking >=2-generator membership. "
            "Without this, every generator's prefix-coded emissions "
            "looked single-generator by construction and crossgen MI "
            "was 0 by construction. The canonical form reveals genuine "
            "cross-generator structural themes."
        )
        lines.append("")
        if analysis['n_crossgen_kill_patterns'] == 0:
            lines.append(
                "**Note:** zero kill_patterns appear across >=2 generators "
                "this tick. The raw MI signal is therefore 100% generator-"
                "prefix tautology. Cross-generator emergence needs at "
                "least one second generator-class (e.g., Stygian's "
                "executor emissions) before this becomes a meaningful "
                "signal."
            )
            lines.append("")
        if alarm:
            lines.append("## SELF_AUDIT_ALARM")
            lines.append("")
            lines.append(alarm)
            lines.append("")
        # Sampling context — what data this analysis is over, separate from
        # the analysis itself. Lets a future reader audit data selection
        # independently from inference. Added 2026-05-19 after Hecate v0.1
        # misreported a monoculture artifact as a substrate finding because
        # the alphabetical-iteration sampler only ever read the chronologically
        # first 54MB batch.
        sc = analysis.get("sampling_context", {}) or {}
        lines.append("## Sampling context")
        lines.append("")
        lines.append(f"- max_records_budget: {sc.get('max_records_budget')}")
        lines.append(f"- files_n: {sc.get('files_n')}")
        lines.append(f"- per_file_cap: {sc.get('per_file_cap')}")
        lines.append(f"- exhausted_budget: {sc.get('exhausted_budget')}")
        lines.append(f"- total_records_taken: {sc.get('total_records_taken')}")
        lines.append("")
        lines.append("### Files seen (mtime descending)")
        lines.append("")
        for f in sc.get("files_seen", []):
            lines.append(f"- `{f['file']}` — {f['records_taken']} records")
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

    # ---- DR prompt builder (substrate A — retraction patterns) -----------

    def _build_dr_prompt(self, top_pattern: str, top_generator: str) -> str:
        """Retraction-pattern survey grounded in this tick's dominant
        kill_pattern + generator. Per doctrine §6 Hecate row."""
        return (
            f"Hecate (Charon swarm, continuous gradient archaeology over "
            f"the kill ledger) is mining retraction-pattern signal adjacent "
            f"to dominant kill_pattern `{top_pattern}` (top generator: "
            f"`{top_generator}`). Substrate type A (patterned cases that "
            f"feed gradient archaeology).\n\n"
            f"Survey 2024-2026 mathematical retractions / withdrawals / "
            f"errata adjacent to the technique class implied by "
            f"`{top_pattern}`. Group findings by failure mode:\n"
            f"- computation error (numerical, symbolic, or computer-algebra)\n"
            f"- gap in proof (lemma quietly assumed)\n"
            f"- prior art collision (the result was already known)\n"
            f"- hypothesis failure (the result is true but the proof's "
            f"hypotheses don't hold in the claimed generality)\n\n"
            f"For each retraction case: arXiv ID + DOI (REQUIRED), the "
            f"failure-mode classification, the kill_pattern signature "
            f"this case would have produced inside a v10-class battery, "
            f"and any signal that distinguishes this kind of failure from "
            f"the others (so we can refine the kill_pattern taxonomy).\n\n"
            f"Verification criterion: each retraction must cite both the "
            f"original arXiv preprint and the retraction notice / "
            f"superseding paper. Generic 'this paper has known issues' "
            f"is NOT substrate-grade.\n\n"
            f"Landing path: Hecate's gradient_archaeology artifact "
            f"(`charon/agents/hecate/artifacts/gradient_archaeology_*.md`) "
            f"— the retraction-pattern groupings refine the kill_pattern "
            f"taxonomy and feed primitive_proposal candidates."
        )

    def _emit_dr_intake(self, notification: dict) -> Optional[Path]:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        row_id = notification.get("row_id", "noid")
        fname = f"dr_intake_{row_id}_{utc}.md"
        lines = [
            f"# Hecate DR intake — row {row_id}",
            "",
            f"- received_at: {datetime.now(timezone.utc).isoformat()}",
            f"- substrate_type: A (retraction patterns)",
            f"- title: {notification.get('title', 'n/a')}",
            f"- report_url: {notification.get('report_github_url', 'n/a')}",
            f"- completed_at: {notification.get('completed_at', 'n/a')}",
            "",
            "## Summary (Pythia)",
            "",
            notification.get("summary", "_(no summary)_"),
            "",
            "## Downstream action",
            "",
            "Cross-reference each retraction case's kill_pattern signature "
            "against the current kill_ledger cluster geometry. Strong "
            "matches refine the kill_pattern taxonomy; novel patterns "
            "become primitive_proposal candidates filed against "
            "techne/registry/.",
            "",
        ]
        return self.write_artifact(fname, "\n".join(lines))

    # ---- stygian-priority queue feed -------------------------------------

    def _feed_stygian_priority(self, analysis: dict) -> int:
        """Walk this tick's clusters_at_or_above_min_size; enqueue any
        kill_pattern not seen in the last 24h as a Stygian attack target.

        Producer-side dedup keeps the queue tight: we don't want to flood
        Stygian with the same kill_pattern every 20-minute rotation when
        the cluster geometry hasn't actually changed.
        """
        clusters = analysis.get("clusters_at_or_above_min_size") or []
        if not clusters:
            return 0
        mi_z = float(analysis.get("mi_z") or 0.0)
        # Only emit when MI signal is meaningfully above null (don't feed
        # Stygian noise during decay states; alarm already fires if mi_z
        # drops, so this gating is the operational corollary).
        if mi_z < MI_DRIFT_THRESHOLD:
            return 0
        queue = stygian_priority_queue()
        cutoff = (
            datetime.now(timezone.utc) - timedelta(hours=STYGIAN_QUEUE_DEDUP_HOURS)
        ).isoformat()
        recent_kps = queue.recent_keys("kill_pattern", cutoff)
        n_emitted = 0
        for cluster in clusters:
            kp = cluster.get("kill_pattern")
            if not kp or kp in recent_kps:
                continue
            top_gens = cluster.get("top_generators") or []
            top_gen = top_gens[0][0] if top_gens else "unknown"
            queue.append({
                "source": "hecate",
                "kill_pattern": kp,
                "cluster_size": int(cluster.get("size") or 0),
                "top_generator": top_gen,
                "mi_z": round(mi_z, 3),
                "mi_observed": float(analysis.get("mi_observed") or 0.0),
                "hecate_ledger_dir": analysis.get("ledger_dir"),
            })
            n_emitted += 1
        if n_emitted:
            self.log.info(
                f"stygian-priority: enqueued {n_emitted} cluster(s) "
                f"(mi_z={mi_z:.2f}); recent_kps_skipped={len(recent_kps)}"
            )
        return n_emitted

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
            "dr_inbox_processed": 0,
            "dr_seeded": False,
        }
        artifacts: list[str] = []

        # ---- DR inbox processing ----
        if not dry_run:
            for note in self._process_dr_inbox():
                try:
                    out = self._emit_dr_intake(note)
                    if out is not None:
                        artifacts.append(str(out))
                        stats["artifacts_written"] += 1
                    self._mark_dr_processed(note)
                    stats["dr_inbox_processed"] += 1
                except Exception as e:
                    self.log.exception(f"dr_inbox processing failed: {e}")
                    stats["errors"] += 1

        backlog = self.self_generate_backlog()
        stats["backlog_remaining"] = max(0, len(backlog) - 1)
        analysis_cached: Optional[dict] = None

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
            sources = item.get("sources") or []
            stats["ledger_found"] = ",".join(
                str(Path(s["ledger"]).relative_to(REPO_ROOT)) for s in sources
            ) or "none"
            try:
                if dry_run:
                    stats["items_processed"] += 1
                else:
                    analysis = self._analyze(sources)
                    analysis_cached = analysis
                    stats["total_records"] = analysis["total_records"]
                    stats["mi_observed"] = analysis["mi_observed"]
                    stats["mi_z"] = analysis["mi_z"]
                    stats["mi_crossgen"] = analysis["mi_crossgen"]
                    stats["mi_crossgen_z"] = analysis["mi_crossgen_z"]
                    stats["n_crossgen_kps"] = analysis["n_crossgen_kill_patterns"]
                    alarm = self._update_alarm_state(analysis["mi_z"])
                    stats["alarm"] = bool(alarm)
                    out = self._emit_archaeology_run(analysis, alarm)
                    artifacts.append(str(out))
                    stats["items_processed"] += 1
                    stats["artifacts_written"] += 1
            except Exception as e:
                self.log.exception(f"gradient archaeology failed: {e}")
                stats["errors"] += 1

        # ---- Stygian-priority queue feed (closed-loop edge) -------------
        # Per Stand #1 (2026-05-21): when a kill_pattern cluster crosses the
        # MIN_CLUSTER_SIZE threshold with high mi_z, enqueue it as a
        # high-priority attack target for Stygian. Closed-loop: Hecate finds
        # the cluster, Stygian validates with the v10 battery, the kill row
        # grows the ledger, next Hecate analysis sees the refined geometry.
        if (not dry_run) and analysis_cached is not None:
            try:
                self._feed_stygian_priority(analysis_cached)
            except Exception as e:
                self.log.exception(f"stygian-priority queue feed failed: {e}")
                stats["errors"] += 1

        # ---- Pythia DR enqueue (retraction-pattern hunt grounded in this tick) ----
        if (not dry_run) and analysis_cached is not None:
            top_patterns = analysis_cached.get("top_kill_patterns") or []
            top_generators = analysis_cached.get("top_generators") or []
            if top_patterns and top_generators:
                top_pattern = top_patterns[0][0]
                top_generator = top_generators[0][0]
                dr_result = self._dr_enqueue_if_quota(
                    title=f"Hecate retraction-pattern survey: kill_pattern `{top_pattern}`",
                    prompt=self._build_dr_prompt(top_pattern, top_generator),
                    recent_coverage_keywords=["Hecate", top_pattern],
                    substrate_type="A",
                    tags={"top_kill_pattern": top_pattern, "top_generator": top_generator},
                )
                stats.update({
                    "dr_seeded": dr_result["dr_seeded"],
                    "dr_seeded_today": dr_result["dr_seeded_today"],
                    "dr_quota_remaining": dr_result["dr_quota_remaining"],
                    "dr_skipped_reason": dr_result["dr_skipped_reason"],
                    "dr_row_id": dr_result["dr_row_id"],
                    "dr_top_pattern": top_pattern,
                })

        if not dry_run:
            self._emit_dr_discipline_adoption(
                daily_cap=3,
                substrate_types=["A"],
                builder_ref="charon/agents/hecate/daemon.py:_build_dr_prompt",
            )

        summary = (
            f"ledger={stats['ledger_found']} "
            f"records={stats['total_records']} "
            f"mi={stats['mi_observed']} mi_z={stats['mi_z']} "
            f"alarm={stats['alarm']} "
            f"artifacts={stats['artifacts_written']} "
            f"errors={stats['errors']} "
            f"dr_seeded={stats.get('dr_seeded')} "
            f"dr_inbox={stats['dr_inbox_processed']}"
        )
        self.log_work(
            "hecate_tick_complete",
            summary=summary,
            output_path=artifacts[0] if artifacts else None,
            success=stats["errors"] == 0,
        )
        return stats
