"""
Iris auto-promotion pipeline (Phase 1 proof-of-concept).

Per spec section 5.3 of AUTOPROMOTION_TARGETS.md v0.2 (commit f9370eb5).

Source artifacts: Iris cluster dicts where the underlying fingerprint
has crossed the >=3-distinct-files threshold AND >=1 of the files is
NOT in the agent's internal corpus (cross-corpus signal).

Scoring (Tier 0 hard filters + Tier 1 transparent rank):

    # Tier 0 hard-filter gates:
    reject if phrase is mostly markdown boilerplate (>30% boilerplate chars)
    reject if fingerprint stem is in known_template_spans.json
    reject if slug is in dismissed_candidates.json
    reject if slug already present in symbols/INDEX.md

    # Tier 1 transparent score (capped entropy term per reviewer):
    entropy_score = clamp(1 / max(paraphrase_entropy, 0.05), 0.0, 3.0)
    score = (distinct_files_count - 2)
          * entropy_score
          * (1.0 if cross_corpus else 0.5)

    auto_promote if score >= 1.5 AND all Tier 0 gates pass

Target substrate slot: append a candidate entry to
    D:\\Prometheus\\harmonia\\memory\\symbols\\CANDIDATES.md
with auto-promotion provenance + "requires human review" tag.

Kill-path: append the slug stem to
    D:\\Prometheus\\harmonia\\agents\\iris\\state\\auto_promoted_candidates.json
which mirrors the existing dismissed_candidates.json shape; conductor
can revert by moving the slug between the two lists.

Taint scope: readable_by_agents=[iris]; downstream_slots=[CANDIDATES.md];
requires_taint_sweep_on_retract=False (CANDIDATES.md is not load-bearing).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from harmonia.agents._scorer import (
    HarmoniaScorer,
    append_yield_row,
    emit_event,
    EVENT_AUTOPROMOTE_PROPOSED,
    EVENT_AUTOPROMOTE_COMMITTED,
    EVENT_AUTOPROMOTE_ABORTED,
    EVENT_KILL_PATH_WRITTEN,
    EVENT_TAINT_SCOPE_WRITTEN,
)

REPO_ROOT = Path(r"D:\Prometheus")
IRIS_STATE_DIR = REPO_ROOT / "harmonia" / "agents" / "iris" / "state"
CANDIDATES_MD = REPO_ROOT / "harmonia" / "memory" / "symbols" / "CANDIDATES.md"
SYMBOLS_INDEX_MD = REPO_ROOT / "harmonia" / "memory" / "symbols" / "INDEX.md"
KNOWN_TEMPLATE_SPANS = IRIS_STATE_DIR / "known_template_spans.json"
DISMISSED_CANDIDATES = IRIS_STATE_DIR / "dismissed_candidates.json"
AUTO_PROMOTED = IRIS_STATE_DIR / "auto_promoted_candidates.json"

# Per spec section 5.3 Tier 0
BOILERPLATE_CHARS = set("#*|_`-=>~+/<>")
BOILERPLATE_RATIO_MAX = 0.30

# Per spec section 5.3 Tier 1
PROMOTE_THRESHOLD = 1.5
ENTROPY_FLOOR = 0.05
ENTROPY_SCORE_MAX = 3.0

# Cross-corpus heuristic: any file under one of these path stems counts
# as "internal Harmonia corpus". Anything else is external.
INTERNAL_PATH_STEMS = (
    str(REPO_ROOT / "harmonia" / "memory") + "\\",
    str(REPO_ROOT / "harmonia" / "docs") + "\\",
    str(REPO_ROOT / "roles" / "Harmonia") + "\\",
)


# ---------------------------------------------------------------------------
# Helpers (entropy + cross-corpus detection)
# ---------------------------------------------------------------------------

def _is_internal_file(file_path: str) -> bool:
    """True if the file is part of Harmonia's own writing surface."""
    norm = file_path.replace("/", "\\")
    return any(norm.startswith(stem) for stem in INTERNAL_PATH_STEMS)


def _is_cross_corpus(cluster: dict) -> bool:
    """True iff the cluster spans both internal AND external files."""
    files = cluster.get("files") or {}
    if not files:
        return False
    has_internal = False
    has_external = False
    for f in files.keys():
        if _is_internal_file(f):
            has_internal = True
        else:
            has_external = True
        if has_internal and has_external:
            return True
    # If all files are external, still treat as cross-corpus (the most
    # informative case): the pattern recurs across heterogeneous external
    # sources. Internal-only is the LEAST informative.
    return has_external and not has_internal


def _paraphrase_entropy(cluster: dict) -> float:
    """Average pairwise Jaccard distance between example token sets.

    Low entropy (close to 0) = examples are near-identical wording -> high
        signal that the fingerprint is a real recurring pattern.
    High entropy (close to 1) = examples are wildly different texts that
        happen to share the same normalized fingerprint -> low signal,
        the fingerprint is too loose.
    """
    examples = cluster.get("examples") or []
    texts = [str(e.get("text", "")) for e in examples if e.get("text")]
    if len(texts) < 2:
        return 0.0
    token_sets: list[set] = []
    for t in texts:
        toks = set(re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", t.lower()))
        token_sets.append(toks)
    if all(not s for s in token_sets):
        return 0.0
    distances: list[float] = []
    for i in range(len(token_sets)):
        for j in range(i + 1, len(token_sets)):
            a, b = token_sets[i], token_sets[j]
            if not a and not b:
                continue
            jaccard_dist = 1.0 - (len(a & b) / max(1, len(a | b)))
            distances.append(jaccard_dist)
    if not distances:
        return 0.0
    return sum(distances) / len(distances)


def _boilerplate_ratio(fingerprint: str) -> float:
    """Fraction of fingerprint chars that are markdown boilerplate."""
    if not fingerprint:
        return 0.0
    n_boiler = sum(1 for c in fingerprint if c in BOILERPLATE_CHARS)
    return n_boiler / max(1, len(fingerprint))


def _longest_common_path_prefix(paths: list[str]) -> str:
    """Longest common path prefix shared by ALL given paths. Empty string
    if no common prefix beyond drive letter. Used by Tier 0 to detect
    'all examples under the same directory' template patterns."""
    if not paths:
        return ""
    norm = [p.replace("/", "\\") for p in paths]
    common_parts: list[str] = []
    split_parts = [p.split("\\") for p in norm]
    for i in range(min(len(p) for p in split_parts)):
        seg = split_parts[0][i]
        if all(p[i] == seg for p in split_parts):
            common_parts.append(seg)
        else:
            break
    return "\\".join(common_parts)


def _load_known_template_spans() -> list[str]:
    """Token patterns that, when present in a fingerprint, mark it as
    template-noise rather than real semantic structure."""
    if not KNOWN_TEMPLATE_SPANS.exists():
        return []
    try:
        return list(json.loads(KNOWN_TEMPLATE_SPANS.read_text(encoding="utf-8")))
    except Exception:
        return []


def _load_dismissed() -> set:
    if not DISMISSED_CANDIDATES.exists():
        return set()
    try:
        data = json.loads(DISMISSED_CANDIDATES.read_text(encoding="utf-8"))
        # dismissed list may be slug stems or full slugs with @vN
        return {str(s).upper().split("@")[0] for s in data}
    except Exception:
        return set()


def _load_auto_promoted() -> set:
    """Read auto_promoted_candidates.json -- slugs that have already been
    auto-promoted in a prior tick. Used for idempotency in Tier 0."""
    if not AUTO_PROMOTED.exists():
        return set()
    try:
        data = json.loads(AUTO_PROMOTED.read_text(encoding="utf-8"))
        return {str(s).upper().split("@")[0] for s in data}
    except Exception:
        return set()


def _load_existing_symbols() -> set:
    """Read symbols/INDEX.md for already-promoted symbol stems."""
    if not SYMBOLS_INDEX_MD.exists():
        return set()
    try:
        text = SYMBOLS_INDEX_MD.read_text(encoding="utf-8", errors="ignore")
        # Markdown table rows naming symbols, e.g. `| [NAME@v1](NAME.md) | ...`
        stems = set(re.findall(r"\[([A-Z][A-Z0-9_]+)@v\d", text))
        return stems
    except Exception:
        return set()


# ---------------------------------------------------------------------------
# IrisPipeline (Phase 1)
# ---------------------------------------------------------------------------

class Pipeline(HarmoniaScorer):
    """Iris auto-promotion pipeline. Subclasses HarmoniaScorer; the
    calibration watchdog (`scripts/harmonia_scorer_calibration.py`)
    discovers this class via the module path
    `harmonia.agents.iris._pipeline.Pipeline`.
    """

    name = "iris"
    promote_threshold = PROMOTE_THRESHOLD

    # ---- Tier 0 hard filters ---------------------------------------------

    def tier0_filter(self, candidate: dict) -> tuple[bool, Optional[str]]:
        fingerprint = candidate.get("fingerprint", "")
        slug = candidate.get("slug", "")
        files = candidate.get("files") or {}
        examples = candidate.get("examples") or []

        # Distinct-file threshold
        if len(files) < 3:
            return False, "distinct_files_below_3"

        # Known template spans (highest-priority hard filter)
        spans = _load_known_template_spans()
        fp_lower = fingerprint.lower()
        for span in spans:
            if span.lower() in fp_lower:
                return False, f"matches_known_template_span:{span[:40]}"

        # Same-kind heading dominance under common path stem -- the real
        # F043-class failure for Iris (e.g. DIRECTIONS_FUTURE_OPEN_PROBLEMS
        # repeating across 4 DR reports). If ALL examples are headings AND
        # the cluster's files share a common path prefix below the repo
        # root, it's almost certainly DR-report template noise.
        if examples and all(e.get("kind") == "heading" for e in examples):
            common = _longest_common_path_prefix(list(files.keys()))
            common_norm = (
                common.replace(str(REPO_ROOT), "").replace("/", "\\").strip("\\")
            )
            if common_norm and "\\" in common_norm:
                # at least 1 directory below repo root in common
                return False, f"all_headings_under_common_path:{common_norm[:60]}"

        # Fingerprint must have enough semantic tokens. Tokens >= 3 chars
        # after the slugify stopword strip. <= 2 of those means the
        # fingerprint is a generic section header.
        tokens = [t for t in fingerprint.split("_") if len(t) >= 3]
        if len(tokens) <= 2:
            return False, f"fingerprint_too_few_meaningful_tokens:{len(tokens)}"

        # Markdown boilerplate ratio computed on EXAMPLE TEXTS (the raw
        # phrases), not on the slugified fingerprint -- the slugifier
        # already strips structural chars, so fingerprint-level boilerplate
        # detection is a no-op in practice.
        combined_text = "".join(str(e.get("text", "")) for e in examples)
        if combined_text:
            ratio = sum(1 for c in combined_text if c in BOILERPLATE_CHARS) / len(combined_text)
            if ratio > BOILERPLATE_RATIO_MAX:
                return False, f"example_texts_boilerplate_ratio_{ratio:.2f}"

        # Already dismissed by conductor
        dismissed = _load_dismissed()
        slug_stem = slug.upper().split("@")[0]
        if slug_stem in dismissed:
            return False, f"slug_in_dismissed_list:{slug_stem[:40]}"

        # Already a promoted symbol
        existing = _load_existing_symbols()
        if slug_stem in existing:
            return False, f"slug_already_promoted_symbol:{slug_stem[:40]}"

        # Already auto-promoted (idempotency). The conductor can revert
        # an auto-promotion by moving the slug from auto_promoted_candidates
        # into dismissed_candidates (which the prior check catches).
        already_promoted = _load_auto_promoted()
        if slug_stem in already_promoted:
            return False, f"slug_already_auto_promoted:{slug_stem[:40]}"

        return True, None

    # ---- Tier 1 transparent score ----------------------------------------

    def tier1_score(self, candidate: dict) -> float:
        files = candidate.get("files") or {}
        n_files = len(files)
        # Per spec: (distinct_files_count - 2) -- baseline of 3 files gives 1
        files_factor = max(0, n_files - 2)

        entropy = _paraphrase_entropy(candidate)
        # entropy_score = 1 / max(entropy, 0.05), clamped to [0, 3]
        entropy_score = 1.0 / max(entropy, ENTROPY_FLOOR)
        entropy_score = max(0.0, min(ENTROPY_SCORE_MAX, entropy_score))

        cross = _is_cross_corpus(candidate)
        cross_factor = 1.0 if cross else 0.5

        score = files_factor * entropy_score * cross_factor
        return float(score)

    # ---- Tier 2 bandit arm key -------------------------------------------

    def arm_key(self, candidate: dict) -> str:
        """An arm is the slug stem (the canonical symbol-name prefix).
        Different fingerprints with the same slug stem fight over the
        same arm so the bandit learns 'this kind of slug pays off'."""
        slug = candidate.get("slug", "")
        return slug.upper().split("@")[0] or "unknown_arm"


# ---------------------------------------------------------------------------
# Auto-promotion hook — called from iris/daemon.py after artifact emission
# ---------------------------------------------------------------------------

def autopromote_clusters(
    clusters: dict,
    newly_crossed_fingerprints: list[str],
    tick_id: Optional[str] = None,
    dry_run: bool = False,
) -> list[dict]:
    """For each newly-crossed cluster, evaluate through the pipeline; for
    candidates that auto_promote=True, append an entry to CANDIDATES.md,
    write the kill-path artifact, and append a yield row.

    Returns the list of yield_ids written (empty if no promotions). The
    caller (iris daemon) can include this in its tick stats.
    """
    if not newly_crossed_fingerprints:
        return []

    if Pipeline().is_quiesced():
        # Calibration watchdog has paused this pipeline; do nothing.
        emit_event(
            EVENT_AUTOPROMOTE_ABORTED,
            {"reason": "scorer_quiesced",
             "n_candidates": len(newly_crossed_fingerprints)},
            agent="iris",
            tick_id=tick_id,
        )
        return []

    # Build candidate dicts from the cluster store
    candidates: list[dict] = []
    for fp in newly_crossed_fingerprints:
        cluster = clusters.get(fp)
        if not cluster:
            continue
        # Augment with distinct_files_count for convenience
        cand = dict(cluster)
        cand["distinct_files_count"] = len(cluster.get("files") or {})
        cand["cross_corpus"] = _is_cross_corpus(cluster)
        cand["paraphrase_entropy"] = _paraphrase_entropy(cluster)
        candidates.append(cand)

    pipeline = Pipeline()
    verdicts = pipeline.evaluate_batch(candidates, k=len(candidates), tick_id=tick_id)
    yield_ids: list[str] = []

    for v in verdicts:
        cand = v.candidate
        slug = cand.get("slug", "unknown")
        slug_stem = slug.upper().split("@")[0]
        fingerprint = cand.get("fingerprint", "")
        files = cand.get("files") or {}

        if dry_run:
            emit_event(
                EVENT_AUTOPROMOTE_PROPOSED,
                {"slug": slug, "score": v.tier1_score, "dry_run": True},
                agent="iris", tick_id=tick_id,
            )
            continue

        emit_event(
            EVENT_AUTOPROMOTE_PROPOSED,
            {"slug": slug, "score": v.tier1_score, "n_files": len(files)},
            agent="iris", tick_id=tick_id,
        )

        # 1. Append entry to CANDIDATES.md (atomic append)
        try:
            entry = _build_candidates_md_entry(cand, v.tier1_score, v.metadata)
            CANDIDATES_MD.parent.mkdir(parents=True, exist_ok=True)
            with open(CANDIDATES_MD, "a", encoding="utf-8") as f:
                f.write("\n\n---\n\n" + entry)
        except Exception as e:
            emit_event(
                EVENT_AUTOPROMOTE_ABORTED,
                {"slug": slug, "reason": f"CANDIDATES.md write failed: {e}"},
                agent="iris", tick_id=tick_id,
            )
            continue

        # 2. Write kill-path (append slug to auto_promoted_candidates.json)
        try:
            promoted = []
            if AUTO_PROMOTED.exists():
                try:
                    promoted = list(json.loads(AUTO_PROMOTED.read_text(encoding="utf-8")))
                except Exception:
                    promoted = []
            if slug_stem not in promoted:
                promoted.append(slug_stem)
            AUTO_PROMOTED.write_text(
                json.dumps(promoted, indent=2), encoding="utf-8",
            )
            emit_event(
                EVENT_KILL_PATH_WRITTEN,
                {"slug": slug, "kill_path": str(AUTO_PROMOTED)},
                agent="iris", tick_id=tick_id,
            )
        except Exception as e:
            emit_event(
                EVENT_AUTOPROMOTE_ABORTED,
                {"slug": slug, "reason": f"kill-path write failed: {e}"},
                agent="iris", tick_id=tick_id,
            )
            continue

        # 3. Construct taint scope (mandatory per spec section 6.4)
        taint_scope = {
            "readable_by_agents": ["iris"],
            "downstream_slots": [str(CANDIDATES_MD)],
            "used_for_training": False,
            "recency_keys_written": [f"symbol_candidate:{slug_stem}"],
            "requires_taint_sweep_on_retract": False,
            "cross_swarm_consumers": [],
        }
        emit_event(
            EVENT_TAINT_SCOPE_WRITTEN,
            {"slug": slug, "taint_scope": taint_scope},
            agent="iris", tick_id=tick_id,
        )

        # 4. Append yield row
        yid = append_yield_row(
            agent="iris",
            artifact_path=str(CANDIDATES_MD),
            action="auto_promoted_to_candidates_md",
            auto_promote_score=v.tier1_score,
            tier1_method="rule-based-v0.2",
            kill_path=str(AUTO_PROMOTED),
            taint_scope=taint_scope,
            doctrine_version=None,  # Iris does not depend on Aporia DR doctrine
            extra={
                "slug": slug,
                "fingerprint": fingerprint,
                "distinct_files_count": cand.get("distinct_files_count"),
                "cross_corpus": cand.get("cross_corpus"),
                "paraphrase_entropy": cand.get("paraphrase_entropy"),
                "bandit": v.metadata.get("bandit"),
            },
        )
        yield_ids.append(yid)
        emit_event(
            EVENT_AUTOPROMOTE_COMMITTED,
            {"slug": slug, "yield_id": yid, "score": v.tier1_score},
            agent="iris", tick_id=tick_id, yield_id=yid,
        )

    return yield_ids


def _build_candidates_md_entry(cand: dict, score: float, metadata: dict) -> str:
    """Markdown entry appended to CANDIDATES.md per spec section 5.3."""
    from datetime import datetime, timezone
    slug = cand.get("slug", "unknown")
    fp = cand.get("fingerprint", "")
    files = cand.get("files") or {}
    examples = cand.get("examples") or []
    n_files = len(files)
    entropy = cand.get("paraphrase_entropy", 0.0)
    cross = cand.get("cross_corpus", False)
    bandit_meta = (metadata or {}).get("bandit") or {}
    utc = datetime.now(timezone.utc).isoformat()

    lines: list[str] = []
    lines.append(f"## Auto-promoted candidate: `{slug.upper()}@v1`")
    lines.append("")
    lines.append(f"**Promoted by**: Iris auto-promotion pipeline (Phase 1) at {utc}")
    lines.append(f"**Status**: PROPOSED -- requires human review before promotion to symbol")
    lines.append(f"**Score**: {score:.2f} (rule-based-v0.2)")
    lines.append(f"**Distinct files**: {n_files}")
    lines.append(f"**Cross-corpus**: {cross}")
    lines.append(f"**Paraphrase entropy**: {entropy:.3f}")
    if bandit_meta:
        lines.append(
            f"**Bandit**: mode={bandit_meta.get('mode')} epsilon={bandit_meta.get('epsilon')} "
            f"arm_pull_count={bandit_meta.get('arm_pull_count')}"
        )
    lines.append("")
    lines.append("### Citations")
    lines.append("")
    for f, line_nums in list(files.items())[:8]:
        lines.append(f"- `{f}:{','.join(str(n) for n in line_nums[:5])}`")
    lines.append("")
    if examples:
        lines.append("### Sample snippets")
        lines.append("")
        for ex in examples[:4]:
            text = str(ex.get("text", ""))[:200]
            lines.append(f"- `{ex.get('file','?')}:{ex.get('line','?')}` (kind={ex.get('kind','?')}) -- {text}")
        lines.append("")
    lines.append("### How to reject (kill-path)")
    lines.append("")
    lines.append(
        f"Append the slug stem `{slug.upper().split('@')[0]}` to "
        f"`D:\\Prometheus\\harmonia\\agents\\iris\\state\\dismissed_candidates.json`. "
        f"Iris will skip future re-crossings of this fingerprint AND the "
        f"auto-promotion path will refuse to re-promote it."
    )
    lines.append("")
    return "\n".join(lines)
