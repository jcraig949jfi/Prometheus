"""IrisAgent — prose-to-symbol compressor for the Harmonia swarm.

Iris reads the Harmonia substrate (memory + docs + role journals),
detects prose patterns repeated in 3+ distinct files with paraphrastic
variation, and proposes that they earn versioned symbols. Proposals
land under `D:\\Prometheus\\harmonia\\agents\\iris\\artifacts\\`.
She never promotes. The conductor decides.

See `CHARTER.md` next to this file for the one-page brief.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from harmonia.agents._base import HarmoniaAgent

# -- corpus configuration ---------------------------------------------------

REPO_ROOT = Path(r"D:\Prometheus")

# Source directories. Iris scans .md files at depth-1 in each.
SOURCE_DIRS: list[Path] = [
    REPO_ROOT / "harmonia" / "memory",
    REPO_ROOT / "harmonia" / "docs",
    REPO_ROOT / "roles" / "Harmonia",
]

# Files whose name contains any of these substrings are excluded.
# (Belt and suspenders — we never want to even open key material.)
EXCLUDE_NAME_SUBSTR = ("secret", "Key", "credential", ".env")

# Scan window size per tick.
WINDOW_SIZE = 18

# Cluster promotion threshold (distinct files).
DISTINCT_FILE_THRESHOLD = 3

# Heading word-count window for action-heading extraction.
HEADING_MIN_WORDS = 3
HEADING_MAX_WORDS = 9

# Procedural paragraph character window.
PARA_MIN_CHARS = 50
PARA_MAX_CHARS = 200

# Stopwords removed from fingerprints so paraphrastic variants collapse.
_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "if", "then", "so", "of", "in",
    "on", "to", "for", "with", "by", "is", "are", "was", "were", "be",
    "been", "being", "we", "i", "you", "they", "it", "this", "that",
    "these", "those", "as", "at", "from", "into", "via", "per", "our",
    "my", "your", "their", "its", "do", "does", "did", "doing", "done",
    "have", "has", "had", "having", "will", "would", "should", "could",
    "may", "might", "can", "than", "which", "who", "whom", "whose",
    "what", "when", "where", "why", "how", "no", "not", "yes", "any",
    "all", "each", "every", "some", "such", "only", "just", "also",
})

# Verb-ish hints — a token starting with one of these (or containing
# the gerund -ing suffix) marks a heading as "action-like".
_VERB_HINTS = frozenset({
    "run", "running", "build", "building", "scan", "scanning", "shuffle",
    "shuffling", "audit", "auditing", "refresh", "refreshing", "promote",
    "promoting", "demote", "demoting", "compute", "computing", "validate",
    "validating", "check", "checking", "compress", "compressing",
    "calibrate", "calibrating", "replay", "replaying", "test", "testing",
    "kill", "killing", "extract", "extracting", "cluster", "clustering",
    "propose", "proposing", "write", "writing", "read", "reading",
    "merge", "merging", "review", "reviewing", "decompose", "fix",
    "fixing", "ship", "shipping", "log", "logging", "track", "tracking",
    "emit", "emitting", "fetch", "fetching", "load", "loading", "save",
    "saving", "verify", "verifying", "sweep", "sweeping", "sync",
    "syncing", "tag", "tagging", "snap", "snapping", "halt", "block",
    "blocking", "dispatch", "rotate", "rotating", "score", "scoring",
    "draft", "drafting", "spawn", "spawning", "open", "opening", "close",
    "closing",
})

# Procedural-paragraph cues — substring (case-insensitive) hints that
# the paragraph describes a procedure rather than free narration.
_PROCEDURE_CUES = (
    " we ", "we ", " when ", " each ", " every ", " before ", " after ",
    " step ", " then ", " run ", " by ", " because ", " emit ", " write ",
    " load ", " save ", " scan ", " skip ", " check ", " ensure ",
    " requires ", " threshold ", " call ", " produce ", " yields ",
)

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
_NONALNUM_RE = re.compile(r"[^a-z0-9_]+")


# -- helpers ----------------------------------------------------------------

def _safe_name(name: str) -> bool:
    """Return True iff a filename is safe to read (no credential hits)."""
    low = name.lower()
    for sub in EXCLUDE_NAME_SUBSTR:
        if sub.lower() in low:
            return False
    return True


def _enumerate_corpus() -> list[Path]:
    """Deterministic sorted list of absolute paths across SOURCE_DIRS."""
    out: list[Path] = []
    for d in SOURCE_DIRS:
        if not d.exists():
            continue
        try:
            # depth-1: glob (not rglob)
            for p in d.glob("*.md"):
                if p.is_file() and _safe_name(p.name):
                    out.append(p.resolve())
        except Exception:
            continue
    # sort by absolute path string for determinism
    out.sort(key=lambda p: str(p).lower())
    return out


def _fingerprint(text: str) -> str:
    """Normalized fingerprint: lowercase alnum tokens, drop stopwords,
    drop very short tokens, dedupe, sort, join."""
    tokens = [t.lower() for t in _TOKEN_RE.findall(text)]
    keep = sorted({
        t for t in tokens
        if len(t) >= 3 and t not in _STOPWORDS
    })
    return "_".join(keep)


def _looks_action(text: str) -> bool:
    """Heuristic: text contains at least one verb-hint token."""
    toks = {t.lower() for t in _TOKEN_RE.findall(text)}
    if toks & _VERB_HINTS:
        return True
    # gerund hint: any token ending in 'ing' length >= 5
    for t in toks:
        if len(t) >= 5 and t.endswith("ing"):
            return True
    return False


def _looks_procedural(text: str) -> bool:
    """Heuristic: paragraph contains a procedure cue substring."""
    low = " " + text.lower() + " "
    return any(cue in low for cue in _PROCEDURE_CUES)


def _slugify(fingerprint: str, max_tokens: int = 5) -> str:
    """Turn a fingerprint into UPPER_SNAKE@v1 with at most max_tokens parts."""
    parts = [p for p in fingerprint.split("_") if p][:max_tokens]
    if not parts:
        parts = ["unnamed"]
    base = "_".join(p.upper() for p in parts)
    # safety scrub
    base = _NONALNUM_RE.sub("", base.lower()).upper()
    if not base:
        base = "UNNAMED"
    return f"{base}@v1"


def _utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _extract_from_file(path: Path) -> list[dict]:
    """Return list of phrase records {kind, text, line, fingerprint}
    for one file. Empty list on any error."""
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    lines = raw.splitlines()
    records: list[dict] = []

    # Headings ---------------------------------------------------------
    for i, line in enumerate(lines, start=1):
        m = _HEADING_RE.match(line)
        if not m:
            continue
        htext = m.group(2).strip()
        # strip trailing markdown anchors / link refs
        htext = re.sub(r"\s*\{#[^}]+\}\s*$", "", htext).strip()
        words = htext.split()
        if not (HEADING_MIN_WORDS <= len(words) <= HEADING_MAX_WORDS):
            continue
        if not _looks_action(htext):
            continue
        fp = _fingerprint(htext)
        if not fp or fp.count("_") < HEADING_MIN_WORDS - 2:
            # need at least 2 fingerprint tokens to cluster meaningfully
            continue
        records.append({
            "kind": "heading",
            "text": htext,
            "line": i,
            "fingerprint": fp,
        })

    # Paragraphs -------------------------------------------------------
    # Split on blank lines; track starting line numbers.
    buf: list[str] = []
    buf_start: int = 0
    paragraphs: list[tuple[int, str]] = []
    for i, line in enumerate(lines, start=1):
        if line.strip() == "":
            if buf:
                paragraphs.append((buf_start, " ".join(buf).strip()))
                buf = []
            continue
        if not buf:
            buf_start = i
        # skip pure markdown chrome
        s = line.strip()
        if s.startswith("#") or s.startswith("```") or s.startswith("|"):
            # close current buffer
            if buf:
                paragraphs.append((buf_start, " ".join(buf).strip()))
                buf = []
            continue
        buf.append(s)
    if buf:
        paragraphs.append((buf_start, " ".join(buf).strip()))

    for start_line, ptext in paragraphs:
        n = len(ptext)
        if not (PARA_MIN_CHARS <= n <= PARA_MAX_CHARS):
            continue
        if not _looks_procedural(ptext):
            continue
        fp = _fingerprint(ptext)
        if not fp or fp.count("_") < 3:
            continue
        records.append({
            "kind": "paragraph",
            "text": ptext,
            "line": start_line,
            "fingerprint": fp,
        })

    return records


# -- the agent --------------------------------------------------------------

class IrisAgent(HarmoniaAgent):
    """Prose-to-symbol compressor.

    Rotating-window scan over the Harmonia substrate. Clusters phrases
    by normalized fingerprint. Emits a candidate-symbol artifact when a
    cluster crosses ≥3 distinct files. Never promotes — proposals only.
    """

    name = "Iris"
    role = "prose-to-symbol compressor (substrate self-densifier)"
    machine = "M2"

    # ---- backlog source --------------------------------------------------

    def self_generate_backlog(self) -> list[dict]:
        """The corpus IS the backlog. Return the next file window
        starting at `scan_cursor`. Never empty as long as any source
        files exist. Cursor wraps."""
        files = _enumerate_corpus()
        if not files:
            return []
        cursor = int(self.load_state("scan_cursor", 0) or 0) % len(files)
        window: list[dict] = []
        for k in range(WINDOW_SIZE):
            idx = (cursor + k) % len(files)
            window.append({
                "kind": "scan_file",
                "path": str(files[idx]),
                "corpus_index": idx,
            })
            # if window is larger than corpus, stop to avoid duplicates
            if k + 1 >= len(files):
                break
        return window

    # ---- one tick --------------------------------------------------------

    def run_tick(self, dry_run: bool = False) -> dict:
        stats: dict[str, Any] = {
            "files_scanned": 0,
            "new_clusters": 0,
            "total_clusters_tracked": 0,
            "artifacts_written": 0,
            "errors": 0,
            "dry_run": dry_run,
        }

        # 1. Build the corpus + pick the window.
        files = _enumerate_corpus()
        if not files:
            self.log.warning("no corpus files found; nothing to do")
            self.log_work("iris_tick_complete",
                          summary="empty corpus; no scan performed",
                          success=True)
            return stats

        cursor = int(self.load_state("scan_cursor", 0) or 0) % len(files)
        window_size = min(WINDOW_SIZE, len(files))
        window_indices = [(cursor + k) % len(files) for k in range(window_size)]
        window_files = [files[i] for i in window_indices]
        next_cursor = (cursor + window_size) % len(files)

        self.log.info(
            f"scan window: cursor={cursor} size={window_size} "
            f"corpus={len(files)} files"
        )

        # 2. Load persistent state.
        clusters: dict[str, dict] = self.load_state("clusters", {}) or {}
        crossed: list[str] = list(self.load_state("crossed_threshold", []) or [])
        dismissed: list[str] = list(self.load_state("dismissed_candidates", []) or [])
        crossed_set = set(crossed)
        dismissed_set = {d.upper() for d in dismissed}

        # 3. Scan + extract + merge into clusters.
        newly_crossed_this_tick: list[str] = []
        for fpath in window_files:
            try:
                records = _extract_from_file(fpath)
            except Exception as e:
                self.log.warning(f"extract failed for {fpath}: {e}")
                stats["errors"] += 1
                continue
            stats["files_scanned"] += 1
            file_key = str(fpath)
            for rec in records:
                fp = rec["fingerprint"]
                slot = clusters.setdefault(fp, {
                    "fingerprint": fp,
                    "files": {},        # abs_path -> [line numbers]
                    "examples": [],     # at most 6 sample snippets
                    "kinds": {},        # kind -> count
                    "first_seen": datetime.now(timezone.utc).isoformat(),
                    "slug": _slugify(fp),
                })
                fmap = slot["files"]
                lines_list = fmap.setdefault(file_key, [])
                if rec["line"] not in lines_list:
                    lines_list.append(rec["line"])
                slot["kinds"][rec["kind"]] = slot["kinds"].get(rec["kind"], 0) + 1
                # keep up to 6 distinct example snippets
                if len(slot["examples"]) < 6 and not any(
                    ex["file"] == file_key and ex["line"] == rec["line"]
                    for ex in slot["examples"]
                ):
                    slot["examples"].append({
                        "file": file_key,
                        "line": rec["line"],
                        "kind": rec["kind"],
                        "text": rec["text"][:240],
                    })
                # threshold check
                if (
                    fp not in crossed_set
                    and len(fmap) >= DISTINCT_FILE_THRESHOLD
                    and slot["slug"].split("@")[0] not in dismissed_set
                ):
                    crossed_set.add(fp)
                    newly_crossed_this_tick.append(fp)

        stats["new_clusters"] = len(newly_crossed_this_tick)
        stats["total_clusters_tracked"] = len(clusters)

        # 4. Emit artifacts for new crossings.
        first_new_fp: str | None = (
            newly_crossed_this_tick[0] if newly_crossed_this_tick else None
        )
        artifact_paths: list[str] = []
        if not dry_run:
            for fp in newly_crossed_this_tick:
                try:
                    art_path = self._write_candidate_artifact(
                        clusters[fp],
                        refine_with_deepseek=(fp == first_new_fp),
                    )
                    artifact_paths.append(str(art_path))
                    stats["artifacts_written"] += 1
                except Exception as e:
                    self.log.warning(f"artifact write failed for {fp}: {e}")
                    stats["errors"] += 1

        # 5. Zero new clusters → still emit an audit scan-tick artifact.
        if (
            not newly_crossed_this_tick
            and not dry_run
        ):
            try:
                art_path = self._write_scan_tick_artifact(
                    window_files, cursor, next_cursor, len(files), len(clusters)
                )
                artifact_paths.append(str(art_path))
                stats["artifacts_written"] += 1
            except Exception as e:
                self.log.warning(f"scan-tick artifact failed: {e}")
                stats["errors"] += 1

        # 6. Persist state (only on real tick).
        if not dry_run:
            self.save_state("scan_cursor", next_cursor)
            self.save_state("clusters", clusters)
            self.save_state("crossed_threshold", sorted(crossed_set))
            # dismissed_candidates is read-only from Iris's side; if it
            # didn't exist yet, seed it so the conductor can edit.
            if self.load_state("dismissed_candidates", None) is None:
                self.save_state("dismissed_candidates", [])

        # 7. Telemetry.
        summary = (
            f"scanned {stats['files_scanned']} files "
            f"(cursor {cursor}->{next_cursor}/{len(files)}); "
            f"clusters tracked={stats['total_clusters_tracked']}; "
            f"new_candidates={stats['new_clusters']}; "
            f"artifacts={stats['artifacts_written']}"
        )
        self.log.info(summary)
        self.log_work(
            "iris_tick_complete",
            summary=summary,
            output_path=artifact_paths[0] if artifact_paths else None,
            success=stats["errors"] == 0,
        )

        stats["scan_cursor_from"] = cursor
        stats["scan_cursor_to"] = next_cursor
        stats["corpus_size"] = len(files)
        return stats

    # ---- artifact writers ------------------------------------------------

    def _write_candidate_artifact(
        self,
        cluster: dict,
        refine_with_deepseek: bool = False,
    ) -> Path:
        slug = cluster["slug"]
        slug_for_filename = slug.replace("@", "_at_").lower()
        ts = _utc_iso()
        filename = f"candidate_{slug_for_filename}_{ts}.md"

        files_map: dict[str, list[int]] = cluster["files"]
        n_files = len(files_map)
        total_occurrences = sum(len(v) for v in files_map.values())
        examples = cluster.get("examples", [])

        # Build citation block. Absolute paths, drive letter present.
        citation_lines: list[str] = []
        for abs_path in sorted(files_map.keys()):
            for ln in sorted(files_map[abs_path]):
                citation_lines.append(f"- `{abs_path}:{ln}`")

        # Savings estimate.
        # Heuristic: each cold-start re-reads ~M lines of explanatory
        # prose per occurrence. Use 8 lines/occurrence as a conservative
        # default (a paragraph plus a heading + context).
        est_lines_per_occurrence = 8
        est_savings_lines = total_occurrences * est_lines_per_occurrence

        # Example snippets (de-duplicated by text).
        seen_texts: set[str] = set()
        example_block: list[str] = []
        for ex in examples:
            t = ex["text"].strip()
            if t in seen_texts:
                continue
            seen_texts.add(t)
            example_block.append(
                f"- `{ex['file']}:{ex['line']}` ({ex['kind']}) — {t}"
            )
            if len(example_block) >= 4:
                break

        one_liner = self._one_line_description(cluster, examples)

        spec_stub = (
            f"```\n"
            f"symbol: {slug}\n"
            f"status: PROPOSED (Iris candidate, not yet promoted)\n"
            f"fingerprint: {cluster['fingerprint']}\n"
            f"distinct_files_at_proposal: {n_files}\n"
            f"total_occurrences_at_proposal: {total_occurrences}\n"
            f"description: {one_liner}\n"
            f"spec:\n"
            f"  - <FILL: precise mechanism the prose describes>\n"
            f"  - <FILL: invariants / preconditions / postconditions>\n"
            f"  - <FILL: inputs / outputs in operational terms>\n"
            f"```\n"
        )

        body = (
            f"# Candidate symbol: `{slug}`\n\n"
            f"**Proposed by**: Iris (Harmonia child agent, M2)\n"
            f"**UTC**: {datetime.now(timezone.utc).isoformat()}\n"
            f"**Status**: PROPOSED — Iris does not promote. The conductor decides.\n\n"
            f"## One-line description\n\n"
            f"{one_liner}\n\n"
            f"## Why this crossed Iris's threshold\n\n"
            f"This phrase fingerprint appears in **{n_files} distinct files** "
            f"({total_occurrences} total occurrences) with paraphrastic "
            f"variation. Iris's threshold is "
            f">= {DISTINCT_FILE_THRESHOLD} distinct files. Per the restore "
            f"protocol, prose read identically by every Harmonia cold-start "
            f"is a symbol-promotion candidate.\n\n"
            f"## Citations (file:line, absolute paths)\n\n"
            + "\n".join(citation_lines) + "\n\n"
            f"## Sample snippets\n\n"
            + ("\n".join(example_block) if example_block else "- (none captured)") + "\n\n"
            f"## Sketch versioned-spec stub\n\n"
            f"{spec_stub}\n"
            f"## Savings estimate\n\n"
            f"Appears in {n_files} files; each cold-start re-reads roughly "
            f"{est_savings_lines} lines of equivalent prose "
            f"(~{est_lines_per_occurrence} lines per occurrence x "
            f"{total_occurrences} occurrences). Promoting to `{slug}` "
            f"replaces those re-reads with one symbol lookup under "
            f"`D:\\Prometheus\\harmonia\\memory\\symbols\\`.\n\n"
            f"## How to reject (false positive)\n\n"
            f"Append the slug stem `{slug.split('@')[0]}` to the JSON list "
            f"at `D:\\Prometheus\\harmonia\\agents\\iris\\state\\"
            f"dismissed_candidates.json`. Iris will skip future "
            f"crossings of this fingerprint.\n"
        )

        if refine_with_deepseek:
            refinement = self._deepseek_refinement(examples, slug)
            if refinement:
                body += "\n## DeepSeek refinement\n\n" + refinement.strip() + "\n"

        return self.write_artifact(filename, body)

    def _write_scan_tick_artifact(
        self,
        window_files: list[Path],
        cursor_from: int,
        cursor_to: int,
        corpus_size: int,
        clusters_tracked: int,
    ) -> Path:
        ts = _utc_iso()
        filename = f"scan_tick_{ts}.md"
        files_block = "\n".join(
            f"- `{str(p)}`" for p in window_files
        )
        body = (
            f"# Iris scan tick (zero new clusters)\n\n"
            f"**UTC**: {datetime.now(timezone.utc).isoformat()}\n"
            f"**Cursor**: {cursor_from} -> {cursor_to} of {corpus_size}\n"
            f"**Clusters currently tracked**: {clusters_tracked}\n\n"
            f"No phrase fingerprint crossed the "
            f">= {DISTINCT_FILE_THRESHOLD} distinct-files threshold this "
            f"tick. Cursor advanced.\n\n"
            f"## Files covered this tick\n\n"
            f"{files_block}\n"
        )
        return self.write_artifact(filename, body)

    # ---- helpers ---------------------------------------------------------

    def _one_line_description(
        self,
        cluster: dict,
        examples: Iterable[dict],
    ) -> str:
        """Pick the shortest non-trivial example as the one-liner."""
        best: str | None = None
        for ex in examples:
            t = ex["text"].strip()
            if 20 <= len(t) <= 160:
                if best is None or len(t) < len(best):
                    best = t
        if best:
            return best
        # fallback: humanize the fingerprint
        toks = cluster["fingerprint"].split("_")
        return " ".join(toks[:8]) or "(no description available)"

    def _deepseek_refinement(
        self,
        examples: list[dict],
        proposed_slug: str,
    ) -> str | None:
        """Optional single short DeepSeek call. Returns None silently
        on any failure (no key, no network, rate-limit, anything)."""
        if not examples:
            return None
        # Pick up to 3 distinct-file snippets.
        per_file: dict[str, dict] = {}
        for ex in examples:
            if ex["file"] not in per_file:
                per_file[ex["file"]] = ex
            if len(per_file) >= 3:
                break
        snips = list(per_file.values())
        if len(snips) < 3:
            return None
        snippet_block = "\n".join(
            f"[{i + 1}] from `{ex['file']}`: {ex['text']}"
            for i, ex in enumerate(snips)
        )
        prompt = (
            f"Here are 3 prose snippets from different files in a research "
            f"substrate. Do they all describe the same concept?\n\n"
            f"{snippet_block}\n\n"
            f"If YES: name it (UPPER_SNAKE) and write a <=50-word spec.\n"
            f"If NO: name the distinct concepts.\n"
            f"Iris's proposed slug: {proposed_slug}.\n"
            f"Keep your full response under 150 words."
        )
        try:
            return self.deepseek_complete(
                prompt,
                system=(
                    "You are a terse technical reviewer assisting a "
                    "prose-to-symbol compressor."
                ),
                max_tokens=400,
                temperature=0.3,
            )
        except Exception as e:
            self.log.warning(f"deepseek refinement failed: {e}")
            return None
