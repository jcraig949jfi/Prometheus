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

    # ---- DR prompt builder (substrate A — coordinate collisions) ---------

    def _build_dr_prompt(self, term_focus: str) -> str:
        """Coordinate-collision candidate hunt, per doctrine §6 Acheron row.

        `term_focus` is a HARD-5-risk term Acheron's dictionary already
        watches — Pythia is asked to surface primary-literature cases
        where that same term names two non-isomorphic coordinate systems
        with conflicting reported invariants.
        """
        return (
            f"Acheron (Charon swarm, HARD-5 coordinate-collision detector) "
            f"is hunting primary-literature cases of coordinate collision "
            f"around the term `{term_focus}`. Substrate type A "
            f"(collision-as-falsification signal).\n\n"
            f"Identify three to five 2024-2026 primary-literature cases "
            f"where the term `{term_focus}` (or a near-paraphrase) is used "
            f"in two or more distinct, non-isomorphic coordinate systems "
            f"within the same paper, the same proof, or two adjacent "
            f"papers in the same citation neighborhood. For each:\n"
            f"- the two (or more) coordinate systems being conflated\n"
            f"- the arXiv ID + DOI of the paper(s)\n"
            f"- the specific invariant or quantity whose reported value "
            f"changes under the alternative coordinate (the falsification "
            f"signal)\n"
            f"- whether the collision has been flagged in any erratum, "
            f"comment paper, or correction\n\n"
            f"Verification criterion: every case must cite arXiv ID + DOI "
            f"and quote the line in which both coordinates appear. "
            f"Generic 'authors use X loosely' is NOT a substrate-grade "
            f"finding — the collision must be specific enough that the "
            f"reported invariant differs across the two coordinates.\n\n"
            f"Landing path: Acheron's collision_candidate intake "
            f"(`charon/agents/acheron/artifacts/collision_candidate_*.md`). "
            f"Strong candidates feed Iris's adjudication and may produce "
            f"catalog_edit candidates against "
            f"`aporia/doctrine/substrate_vocabulary/`."
        )

    def _emit_dr_intake(self, notification: dict) -> Optional[Path]:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        row_id = notification.get("row_id", "noid")
        fname = f"dr_intake_{row_id}_{utc}.md"
        lines = [
            f"# Acheron DR intake — row {row_id}",
            "",
            f"- received_at: {datetime.now(timezone.utc).isoformat()}",
            f"- substrate_type: A (coordinate collisions)",
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
            "Extract the cited collision cases. Each becomes a "
            "collision_candidate artifact with provenance pointing to the "
            "primary-source paper(s). Iris adjudicates whether the "
            "collision warrants a catalog_edit against the substrate "
            "vocabulary.",
            "",
        ]
        return self.write_artifact(fname, "\n".join(lines))

    def _pick_dr_term_focus(self) -> Optional[str]:
        """Rotate through the coordinate_dictionary terms, picking the
        least-recently-DR'd one. Returns None if all 8 terms have been
        fired within the recent-coverage window.
        """
        last_dr = self.load_state("dr_term_last_fired", default={}) or {}
        candidates = [entry["term"] for entry in COORDINATE_DICTIONARY]
        ranked = sorted(candidates, key=lambda t: last_dr.get(t, "0000"))
        return ranked[0] if ranked else None

    # ---- run_tick ---------------------------------------------------------

    def run_tick(self, dry_run: bool = False) -> dict:
        stats: dict[str, Any] = {
            "items_processed": 0,
            "artifacts_written": 0,
            "errors": 0,
            "backlog_remaining": 0,
            "file_scanned": None,
            "collisions_found": 0,
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

        # ---- Pythia DR enqueue (rotate through coordinate_dictionary terms) ----
        if not dry_run:
            term_focus = self._pick_dr_term_focus()
            if term_focus:
                dr_result = self._dr_enqueue_if_quota(
                    title=f"Acheron coordinate-collision hunt: term `{term_focus}`",
                    prompt=self._build_dr_prompt(term_focus),
                    recent_coverage_keywords=["Acheron", term_focus],
                    substrate_type="A",
                    tags={"term_focus": term_focus},
                )
                stats.update({
                    "dr_seeded": dr_result["dr_seeded"],
                    "dr_seeded_today": dr_result["dr_seeded_today"],
                    "dr_quota_remaining": dr_result["dr_quota_remaining"],
                    "dr_skipped_reason": dr_result["dr_skipped_reason"],
                    "dr_row_id": dr_result["dr_row_id"],
                    "dr_term_focus": term_focus,
                })
                if dr_result["dr_seeded"]:
                    last_dr = self.load_state("dr_term_last_fired", default={}) or {}
                    last_dr[term_focus] = datetime.now(timezone.utc).isoformat()
                    self.save_state("dr_term_last_fired", last_dr)

            self._emit_dr_discipline_adoption(
                daily_cap=3,
                substrate_types=["A"],
                builder_ref="charon/agents/acheron/daemon.py:_build_dr_prompt",
            )

        summary = (
            f"file={stats['file_scanned']} "
            f"collisions={stats['collisions_found']} "
            f"artifacts={stats['artifacts_written']} "
            f"errors={stats['errors']} "
            f"dr_seeded={stats.get('dr_seeded')} "
            f"dr_inbox={stats['dr_inbox_processed']}"
        )
        self.log_work(
            "acheron_tick_complete",
            summary=summary,
            output_path=artifacts[0] if artifacts else None,
            success=stats["errors"] == 0,
        )
        return stats
