"""Acheron — HARD-5 coordinate-collision detector (Charon child, MVP).

One tick = walk a rotating slice of the prose substrate, find the next
un-scanned-since-last-modification file, scan for coordinate-dictionary
hits, emit collision_candidate when ≥2 distinct coordinates fire on the
same term within the file.

See `charon/agents/acheron/CHARTER.md` for the one-page brief.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from charon.agents._base import CharonAgent
from harmonia.agents._base import REPO_ROOT


# ---- coordinate dictionary v0 (inline seed) -------------------------------

# Each entry: term (the ambiguous keyword), coordinates (list of distinct
# meanings, each with a `name` and a `disambiguator` regex that, if matched
# near the term, indicates the prose is asserting THIS coordinate). When
# ≥2 distinct coordinates fire on the same term within the same file
# (or paragraph cluster), it's a HARD-5 violation candidate.
COORDINATE_DICTIONARY: list[dict] = [
    {
        "term": "rank",
        "coordinates": [
            {"name": "tensor_rank", "disambiguator": r"(?i)\b(tensor[- ]rank|rank\s+of\s+a\s+tensor)\b"},
            {"name": "border_rank", "disambiguator": r"(?i)\bborder[- ]rank\b"},
            {"name": "cactus_rank", "disambiguator": r"(?i)\bcactus[- ]rank\b"},
            {"name": "border_cactus_rank", "disambiguator": r"(?i)\bborder[- ]cactus[- ]rank\b"},
            {"name": "slice_rank", "disambiguator": r"(?i)\bslice[- ]rank\b"},
            {"name": "partition_rank", "disambiguator": r"(?i)\bpartition[- ]rank\b"},
            {"name": "analytic_rank", "disambiguator": r"(?i)\banalytic[- ]rank\b|\border\s+of\s+vanishing\b"},
            {"name": "geometric_rank", "disambiguator": r"(?i)\bgeometric[- ]rank\b|\bmordell[- ]weil[- ]rank\b"},
        ],
    },
    {
        "term": "lehmer",
        "coordinates": [
            {"name": "lehmer_tau", "disambiguator": r"(?i)lehmer.*tau|tau.*lehmer|ramanujan.*tau|\btau\s*\(\s*p\s*\)"},
            {"name": "lehmer_mahler", "disambiguator": r"(?i)lehmer.*mahler|mahler.*lehmer|1\.17[56]|mahler\s+measure"},
        ],
    },
    {
        "term": "schinzel",
        "coordinates": [
            {"name": "schinzel_zassenhaus", "disambiguator": r"(?i)schinzel[- ]zassenhaus|house|dimitrov"},
            {"name": "schinzel_general", "disambiguator": r"(?i)schinzel.*hypothes|schinzel.*sieve|polynomial.*prime"},
        ],
    },
    {
        "term": "catalan",
        "coordinates": [
            {"name": "catalan_mihailescu", "disambiguator": r"(?i)mihailescu|consecutive\s+powers|x\^p\s*-\s*y\^q\s*=\s*1"},
            {"name": "tijdeman_zagier", "disambiguator": r"(?i)tijdeman[- ]zagier|beal"},
            {"name": "pillai", "disambiguator": r"(?i)pillai|a\^x\s*-\s*b\^y"},
        ],
    },
    {
        "term": "sato-tate",
        "coordinates": [
            {"name": "sato_tate_elliptic", "disambiguator": r"(?i)sato[- ]tate.*(elliptic\s+curve|non[- ]CM\s+EC)|EC.*sato[- ]tate"},
            {"name": "sato_tate_symk", "disambiguator": r"(?i)sato[- ]tate.*sym(metric)?\s*power|sym\^[0-9k]|newton[- ]thorne"},
            {"name": "sato_tate_genus2", "disambiguator": r"(?i)sato[- ]tate.*genus[- ]?2|52\s+sato[- ]tate|fite|kedlaya"},
        ],
    },
    {
        "term": "goldbach",
        "coordinates": [
            {"name": "binary_goldbach", "disambiguator": r"(?i)binary\s+goldbach|every\s+even|even\s+integer.*two\s+primes"},
            {"name": "ternary_goldbach", "disambiguator": r"(?i)ternary\s+goldbach|odd\s+integer.*three\s+primes|helfgott"},
        ],
    },
    {
        "term": "twin prime",
        "coordinates": [
            {"name": "twin_primes_conjecture", "disambiguator": r"(?i)twin\s+prime.*conjecture|gap\s*=\s*2|p\s*,\s*p\s*\+\s*2"},
            {"name": "bounded_gaps", "disambiguator": r"(?i)bounded\s+gaps|zhang|maynard|polymath|H\s*<=\s*\d|H\s*≤\s*\d"},
            {"name": "hardy_littlewood_ktuples", "disambiguator": r"(?i)hardy[- ]littlewood.*k[- ]tuple"},
        ],
    },
    {
        "term": "mertens",
        "coordinates": [
            {"name": "mertens_conjecture", "disambiguator": r"(?i)mertens.*conjecture|\|M\(x\)\|\s*<\s*sqrt"},
            {"name": "mertens_function_bound", "disambiguator": r"(?i)mertens.*function|M\(x\)\s*=\s*O|riemann.*equivalent"},
        ],
    },
]

# Rotation scope (relative to REPO_ROOT)
SCAN_ROOTS = [
    "harmonia/memory",
    "roles",
    "aporia/docs",
    "pivot",
    "charon/agents",  # self-review
]

MAX_FILES_PER_TICK = 1
MAX_FILE_SIZE_BYTES = 256_000  # skip huge files (gz/json caches etc.)


def _safe_slug(text: str, max_len: int = 40) -> str:
    s = re.sub(r"[^A-Za-z0-9_.-]", "_", text)
    return s[:max_len] or "noid"


class AcheronAgent(CharonAgent):
    """HARD-5 coordinate-collision detector. Picks one file per tick from
    rotating scope, scans, emits collision_candidate or clean_scan."""

    name = "Acheron"
    role = "HARD-5 coordinate-collision detector (Iris-complement)"

    # ---- backlog ----------------------------------------------------------

    def _enumerate_candidate_files(self) -> list[Path]:
        files: list[Path] = []
        for root in SCAN_ROOTS:
            base = REPO_ROOT / root
            if not base.exists():
                continue
            for p in base.rglob("*.md"):
                try:
                    if p.stat().st_size > MAX_FILE_SIZE_BYTES:
                        continue
                except Exception:
                    continue
                # Skip our own artifacts
                if "/artifacts/" in p.as_posix() or "\\artifacts\\" in str(p):
                    continue
                files.append(p)
        return files

    def self_generate_backlog(self) -> list[dict]:
        scanned = self.load_state("scanned_files", {}) or {}
        files = self._enumerate_candidate_files()
        items: list[dict] = []
        for p in files:
            try:
                stat = p.stat()
                mtime = int(stat.st_mtime)
            except Exception:
                continue
            last = scanned.get(str(p), {})
            last_mtime = last.get("mtime", 0)
            if mtime <= last_mtime:
                continue  # unchanged since last scan
            items.append({
                "path": str(p),
                "mtime": mtime,
                "rel": str(p.relative_to(REPO_ROOT)),
            })
        # Oldest-changed first (re-scan things that changed but haven't been
        # re-audited yet).
        items.sort(key=lambda d: d["mtime"])
        return items

    # ---- scanner ----------------------------------------------------------

    def _scan_file(self, path: Path) -> dict:
        """Return {collisions: [{term, coordinates_fired, contexts}], scanned: bool}."""
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            self.log.warning(f"scan read failed {path}: {e}")
            return {"collisions": [], "scanned": False, "error": str(e)[:200]}

        collisions: list[dict] = []
        for entry in COORDINATE_DICTIONARY:
            term = entry["term"]
            # Quick check: does the term appear at all (case-insensitive)?
            if not re.search(re.escape(term), text, flags=re.IGNORECASE):
                continue
            # Which coordinates fire in this file's prose?
            fired: list[dict] = []
            for coord in entry["coordinates"]:
                m = re.search(coord["disambiguator"], text)
                if m:
                    # Capture context: ~120 chars around the match
                    start = max(0, m.start() - 60)
                    end = min(len(text), m.end() + 60)
                    fired.append({
                        "name": coord["name"],
                        "match_excerpt": text[start:end].replace("\n", " ").strip(),
                    })
            if len(fired) >= 2:
                collisions.append({
                    "term": term,
                    "coordinates_fired": [f["name"] for f in fired],
                    "contexts": fired,
                })
        return {"collisions": collisions, "scanned": True}

    # ---- artifact writers -------------------------------------------------

    def _emit_collision_candidate(self, item: dict, scan: dict) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        slug = _safe_slug(item["rel"].replace("/", "_").replace("\\", "_"))
        fname = f"collision_candidate_{slug}_{utc}.md"
        lines: list[str] = []
        lines.append(f"# Acheron HARD-5 collision candidate")
        lines.append("")
        lines.append(f"- file: `{item['rel']}`")
        lines.append(f"- emitted_at: {datetime.now(timezone.utc).isoformat()}")
        lines.append(f"- emitted_by: Acheron (charon/agents/acheron/daemon.py)")
        lines.append(f"- collisions_found: {len(scan['collisions'])}")
        lines.append("")
        for c in scan["collisions"]:
            lines.append(f"## Term: `{c['term']}`")
            lines.append("")
            lines.append(f"Distinct coordinates asserted in same file: {', '.join(c['coordinates_fired'])}")
            lines.append("")
            for ctx in c["contexts"]:
                lines.append(f"### {ctx['name']}")
                lines.append("")
                lines.append("```")
                lines.append(ctx["match_excerpt"])
                lines.append("```")
                lines.append("")
        lines.append("## Recommendation")
        lines.append("")
        lines.append("Surface to Iris for adjudication. Likely-true positives produce `catalog_edit` candidates pinning each coordinate to its distinct primitive in `aporia/doctrine/substrate_vocabulary/`. Likely-false positives feed Acheron's false-positive-rate self-tune.")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by Acheron (charon/agents/acheron/daemon.py). MVP candidate; multi-paragraph context isolation deferred to v0.2.*")
        return self.write_artifact(fname, "\n".join(lines))

    def _emit_clean_scan(self, item: dict) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        slug = _safe_slug(item["rel"].replace("/", "_").replace("\\", "_"))
        fname = f"clean_scan_{slug}_{utc}.md"
        lines = [
            "# Acheron clean scan",
            "",
            f"- file: `{item['rel']}`",
            f"- emitted_at: {datetime.now(timezone.utc).isoformat()}",
            "",
            "No HARD-5 coordinate-collision detected this round. Clean files are",
            "calibration evidence for the dictionary's specificity — if the daemon",
            "produces only clean scans across the corpus, the dictionary is missing",
            "terms or the disambiguator regexes are too strict.",
            "",
        ]
        return self.write_artifact(fname, "\n".join(lines))

    def _emit_self_audit_null(self, reason: str) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"self_audit_null_{utc}.md"
        return self.write_artifact(fname, f"# Acheron SELF_AUDIT_NULL\n\n- reason: {reason}\n- at: {datetime.now(timezone.utc).isoformat()}\n")

    # ---- run_tick ---------------------------------------------------------

    def run_tick(self, dry_run: bool = False) -> dict:
        stats: dict[str, Any] = {
            "items_processed": 0,
            "artifacts_written": 0,
            "errors": 0,
            "backlog_remaining": 0,
            "file_scanned": None,
            "collisions_found": 0,
        }
        artifacts: list[str] = []

        backlog = self.self_generate_backlog()
        stats["backlog_remaining"] = max(0, len(backlog) - MAX_FILES_PER_TICK)

        if not backlog:
            try:
                if not dry_run:
                    out = self._emit_self_audit_null("no unchanged-since-scan files in rotation scope")
                    artifacts.append(str(out))
                    stats["artifacts_written"] += 1
                stats["items_processed"] += 1
            except Exception as e:
                self.log.exception(f"self_audit_null emit failed: {e}")
                stats["errors"] += 1
        else:
            for item in backlog[:MAX_FILES_PER_TICK]:
                stats["file_scanned"] = item["rel"]
                try:
                    if dry_run:
                        stats["items_processed"] += 1
                        continue
                    scan = self._scan_file(Path(item["path"]))
                    if not scan.get("scanned"):
                        stats["errors"] += 1
                        continue
                    stats["collisions_found"] = len(scan["collisions"])
                    if scan["collisions"]:
                        out = self._emit_collision_candidate(item, scan)
                    else:
                        out = self._emit_clean_scan(item)
                    artifacts.append(str(out))
                    stats["items_processed"] += 1
                    stats["artifacts_written"] += 1
                    # Update scanned ledger
                    scanned = self.load_state("scanned_files", {}) or {}
                    scanned[item["path"]] = {
                        "mtime": item["mtime"],
                        "last_scanned": datetime.now(timezone.utc).isoformat(),
                        "collisions": len(scan["collisions"]),
                    }
                    self.save_state("scanned_files", scanned)
                except Exception as e:
                    self.log.exception(f"scan failed for {item['rel']}: {e}")
                    stats["errors"] += 1

        summary = (
            f"file={stats['file_scanned']} "
            f"collisions={stats['collisions_found']} "
            f"artifacts={stats['artifacts_written']} "
            f"errors={stats['errors']}"
        )
        self.log_work(
            "acheron_tick_complete",
            summary=summary,
            output_path=artifacts[0] if artifacts else None,
            success=stats["errors"] == 0,
        )
        return stats
