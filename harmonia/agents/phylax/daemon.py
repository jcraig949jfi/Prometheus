"""
Phylax — pre-promotion gate + retraction-adjacency sentinel.

Watches promotion-class events on the substrate, runs a Pattern-30
graded-severity sketch and a retraction-registry adjacency check, and
emits a verdict envelope (pass / flag / block) per claim. When inbound
is empty, rotates through already-promoted symbols re-auditing the
oldest — yesterday's pass might be today's flag because the discipline
standard moves.

Wire interface contract: see D:\\Prometheus\\harmonia\\agents\\_base.py.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from harmonia.agents._base import HarmoniaAgent, REPO_ROOT

HARMONIA_MEMORY = REPO_ROOT / "harmonia" / "memory"
SYMBOLS_DIR = HARMONIA_MEMORY / "symbols"
RETRACTION_REGISTRY = HARMONIA_MEMORY / "retraction_registry.md"
PATTERN_LIBRARY = HARMONIA_MEMORY / "pattern_library.md"
SYMBOLS_INDEX = SYMBOLS_DIR / "INDEX.md"
DR_REPORTS_ROOT = REPO_ROOT / "aporia" / "docs" / "deep_research_reports"

# Candidate sync streams in priority order (spec lists agora:sync; the
# repo's canonical helper writes agora:harmonia_sync, so we tail both).
SYNC_STREAMS = ("agora:sync", "agora:harmonia_sync")

PROMOTION_KEYWORDS = ("PROMOTE", "PROMOTION", "SHIP_COMPLETE", "PROMOTED")

ADJACENCY_THRESHOLD = 0.25

_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
_STOPWORDS = frozenset({
    "the", "and", "for", "with", "from", "this", "that", "was", "were",
    "but", "not", "any", "all", "are", "into", "via", "per", "see",
    "use", "used", "uses", "than", "then", "its", "their", "they",
    "your", "you", "have", "has", "had", "will", "would", "could",
    "should", "been", "being", "what", "which", "when", "where",
    "still", "more", "less", "much", "very", "also", "such", "some",
    "one", "two", "three", "four", "five", "level", "levels",
})


def _tokens(text: str) -> set[str]:
    return {
        t.lower() for t in _TOKEN_RE.findall(text or "")
        if t.lower() not in _STOPWORDS and len(t) >= 3
    }


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class PhylaxAgent(HarmoniaAgent):
    name = "Phylax"
    role = "pre-promotion gate + retraction-adjacency sentinel"
    machine = "M2"

    PATTERN30_LEVELS = (
        ("CLEAN", "Y and X mathematically independent; correlation test valid."),
        ("WEAK_ALGEBRAIC", "X appears in a term/factor with small coefficient or under a log-transform where other terms dominate; partial coupling."),
        ("SHARED_VARIABLE", "X appears directly as factor or term in Y's definition; correlation test no longer valid."),
        ("REARRANGEMENT", "Y is definitionally a rearrangement of X plus other known terms; correlation is restatement of identity."),
        ("IDENTITY", "Y = f(X) exactly (proved algebraic identity); identity verification only."),
    )

    # ---- inbound discovery ------------------------------------------------

    def _scan_sync_streams(self, count: int = 50) -> list[dict]:
        seen_ids = set(self.load_state("seen_promotion_ids", []))
        hits: list[dict] = []
        for stream_key in SYNC_STREAMS:
            for msg_id, fields in self.tail_stream(stream_key, count=count):
                if msg_id in seen_ids:
                    continue
                blob = " ".join(
                    f"{k}={v}" for k, v in (fields or {}).items() if v
                )
                upper = blob.upper()
                if any(k in upper for k in PROMOTION_KEYWORDS):
                    hits.append({
                        "source": stream_key,
                        "msg_id": msg_id,
                        "fields": dict(fields or {}),
                        "blob": blob,
                    })
        return hits

    def _scan_dr_reports(self, limit: int = 25) -> list[dict]:
        """Treat each new Pythia DR report as a candidate claim.

        Pythia DR reports are fresh primary-literature findings — exactly
        the surface where new claims adjacent to known retractions would
        surface. We hash-pin which reports we've audited so we only fire
        adjacency checks on genuinely-new ones.

        Returns list of pseudo-events with msg_id = the report file path
        (stable, deduplicated by `seen_promotion_ids` state).
        """
        if not DR_REPORTS_ROOT.exists():
            return []
        seen_ids = set(self.load_state("seen_promotion_ids", []) or [])
        out: list[dict] = []
        try:
            paths = sorted(
                DR_REPORTS_ROOT.rglob("*.md"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )[:limit * 2]  # over-fetch; many may be already-seen
        except Exception as e:
            self.log.warning(f"DR-report enumeration failed: {e}")
            return []
        for p in paths:
            msg_id = f"dr:{p.relative_to(REPO_ROOT).as_posix()}"
            if msg_id in seen_ids:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            # Use first ~1500 chars (title + summary + first content) as
            # the claim surface for adjacency checks. Full report text
            # would dominate token-overlap calculations.
            blob = text[:1500]
            out.append({
                "source": "dr_report",
                "msg_id": msg_id,
                "fields": {
                    "path": str(p),
                    "rel_path": p.relative_to(REPO_ROOT).as_posix(),
                },
                "blob": blob,
            })
            if len(out) >= limit:
                break
        return out

    def _scan_git_promotions(self, limit: int = 50) -> list[dict]:
        # Skip silently if git isn't on PATH (e.g., running under cmd.exe
        # rather than Git-Bash). Avoids one WinError 2 per tick.
        if shutil.which("git") is None:
            return []
        last_seen = self.load_state("last_seen_commit", None)
        cmd = [
            "git", "-C", str(REPO_ROOT), "log",
            f"-n{limit}", "--pretty=format:%H%x09%s",
            "--",
            "harmonia/memory/symbols/",
            "harmonia/memory/build_landscape_tensor.py",
        ]
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30, check=False,
            )
            if proc.returncode != 0:
                self.log.warning(f"git log failed: {proc.stderr[:200]}")
                return []
        except Exception as e:
            self.log.warning(f"git log invocation failed: {e}")
            return []
        commits: list[dict] = []
        for line in proc.stdout.splitlines():
            if "\t" not in line:
                continue
            sha, subject = line.split("\t", 1)
            if last_seen and sha == last_seen:
                break
            commits.append({
                "source": "git",
                "msg_id": sha,
                "fields": {"subject": subject},
                "blob": subject,
            })
        return commits

    # ---- the three per-claim checks --------------------------------------

    def _retraction_adjacency(self, claim_text: str) -> list[dict]:
        if not RETRACTION_REGISTRY.exists():
            return []
        try:
            raw = RETRACTION_REGISTRY.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            self.log.warning(f"retraction_registry read failed: {e}")
            return []
        claim_toks = _tokens(claim_text)
        hits: list[dict] = []
        # Split into entries; each entry starts with "### <date> — <title>".
        entries = re.split(r"^### ", raw, flags=re.MULTILINE)
        for entry in entries[1:]:
            head, _, body = entry.partition("\n")
            title = head.strip()
            was_match = re.search(r"\*\*Was:\*\*(.+?)(?:\n\n|\*\*Status:)", body, flags=re.DOTALL)
            mech_match = re.search(r"\*\*Mechanism:\*\*(.+?)(?:\n\n|\*\*What survives:)", body, flags=re.DOTALL)
            was_text = (was_match.group(1) if was_match else "").strip()
            mech_text = (mech_match.group(1) if mech_match else "").strip()
            entry_toks = _tokens(was_text + " " + mech_text + " " + title)
            score = _jaccard(claim_toks, entry_toks)
            if score >= ADJACENCY_THRESHOLD:
                hits.append({
                    "retraction_title": title,
                    "score": round(score, 3),
                    "was_excerpt": was_text[:240],
                    "mechanism_excerpt": mech_text[:240],
                    "anchor": str(RETRACTION_REGISTRY),
                })
        hits.sort(key=lambda d: d["score"], reverse=True)
        return hits

    def _pattern30_grade(self, claim_text: str) -> dict:
        level_brief = "\n".join(
            f"  {i}. {name} — {desc}" for i, (name, desc) in enumerate(self.PATTERN30_LEVELS)
        )
        prompt = (
            "You are Phylax, a pre-promotion gate. Grade the following claim "
            "for algebraic-identity coupling (Pattern 30, F043 anchor case). "
            "Levels 0..4:\n"
            f"{level_brief}\n\n"
            "Output strictly JSON: "
            '{"level": <0-4>, "name": "<LEVEL_NAME>", "reasoning": "<one-paragraph>"}\n\n'
            f"Claim:\n{claim_text[:2000]}\n"
        )
        raw = self.deepseek_complete(
            prompt,
            system="Respond ONLY with one JSON object, no prose, no fences.",
            max_tokens=400,
        )
        if not raw:
            return {
                "level": None,
                "name": "UNDETERMINED",
                "reasoning": "DeepSeek unavailable; human review required.",
            }
        try:
            cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
            parsed = json.loads(cleaned)
            level = int(parsed.get("level", -1))
            if 0 <= level <= 4:
                return {
                    "level": level,
                    "name": parsed.get("name") or self.PATTERN30_LEVELS[level][0],
                    "reasoning": (parsed.get("reasoning") or "")[:1200],
                }
        except Exception as e:
            self.log.warning(f"pattern30 parse failed: {e}")
        return {
            "level": None,
            "name": "UNDETERMINED",
            "reasoning": (raw or "")[:600],
        }

    def _verdict(self, adjacency_hits: list[dict], p30: dict) -> str:
        level = p30.get("level")
        if level is not None and level >= 2:
            return "block"
        top_adj = adjacency_hits[0]["score"] if adjacency_hits else 0.0
        if (level == 1) or top_adj >= 0.40:
            return "flag"
        if adjacency_hits:
            return "flag"
        return "pass"

    def _shadow_count(self, adjacency_hits: list[dict], p30: dict) -> int:
        count = len(adjacency_hits)
        if p30.get("level") not in (None, 0):
            count += 1
        return count

    # ---- Pythia DR enqueue (per Aporia doctrine 2026-05-19) ---------------

    def _build_dr_prompt(
        self,
        verdict: str,
        event: dict,
        adjacency_hits: list[dict],
        p30: dict,
    ) -> str:
        """Discipline-doctrine compliant DR prompt for promotion-adjacency verification.

        Compliance with the five requirements (Aporia doctrine §3):
          1. Names requester explicitly in prompt body
          2. Specifies substrate type (A = falsification data / anti-anchor)
          3. Sets verification criterion (arXiv ID + DOI + distinguish retracted form)
          4. Pre-declares landing path (retraction_registry.md OR anti_anchors.jsonl)
          5. Recency check enforced at the call site via dr_recent_topics state
        """
        claim_text = (event.get("blob") or "")[:600]
        top_hit = adjacency_hits[0] if adjacency_hits else {}
        retraction_title = top_hit.get("retraction_title", "—")
        jaccard = top_hit.get("score", 0.0)
        was = top_hit.get("was_excerpt", "")
        mech = top_hit.get("mechanism_excerpt", "")
        anchor = top_hit.get("anchor", "")
        today_iso = datetime.now(timezone.utc).date().isoformat()
        return (
            f"Requester: **Phylax** (Harmonia swarm, M2) — pre-promotion gate + "
            f"retraction-adjacency sentinel.\n"
            f"Substrate type: **A** (falsification data / anti-anchor verification).\n"
            f"Landing path: append findings to "
            f"`D:\\Prometheus\\harmonia\\memory\\retraction_registry.md` if the "
            f"prior retraction needs re-statement or update, OR file as anti-anchor "
            f"candidate at `D:\\Prometheus\\techne\\registry\\anti_anchors.jsonl` "
            f"if the literature has materially moved.\n\n"
            f"## Background\n"
            f"Phylax flagged a new candidate claim adjacent (Jaccard {jaccard:.2f}) "
            f"to a known retraction:\n"
            f"- Retracted entry: **{retraction_title}**\n"
            f"- Anchor: `{anchor}`\n"
            f"- Was: {was}\n"
            f"- Mechanism: {mech}\n\n"
            f"The candidate claim (excerpt):\n"
            f"```\n{claim_text}\n```\n\n"
            f"Phylax's Pattern-30 sketch graded this "
            f"**{p30.get('name','UNDETERMINED')}** "
            f"({p30.get('reasoning','no automated reasoning available')}).\n\n"
            f"## Question\n"
            f"Has the primary mathematical / scientific literature **since 2024-01** "
            f"(a) re-confirmed the prior retraction, (b) overturned the retraction "
            f"with a new proof / construction / counterexample, or (c) added a "
            f"new degree-of-freedom that changes the algebraic-coupling diagnosis?\n\n"
            f"## Verification criterion (doctrine §3.3)\n"
            f"For each cited result, provide: primary source (**arXiv ID + DOI** "
            f"when available), publication date, the specific claim or theorem "
            f"statement, and explicitly distinguish whether the new work "
            f"addresses the **exact retracted form** vs a **weaker / restated "
            f"form**. Reject sources older than 2024-01 unless they are the "
            f"primary source the retraction was originally based on (in which "
            f"case quote the relevant passage).\n\n"
            f"## Anti-recency-collision (doctrine §3.5)\n"
            f"Phylax has not enqueued a DR on retraction anchor `{anchor}` "
            f"in the last 7 days (tracked in `dr_recent_topics` state). If "
            f"Aporia's queue has covered this anchor recently, please reply "
            f"with `RECENT_COVERAGE — see DR <id>` as the first line so Phylax "
            f"can suppress future re-fires for this anchor.\n\n"
            f"Phylax artifact this came from: "
            f"`D:\\Prometheus\\harmonia\\agents\\phylax\\artifacts\\verdict_"
            f"{event.get('source','inbound')}_*` (timestamp around {today_iso})."
        )

    def _maybe_enqueue_dr(
        self,
        verdict: str,
        event: dict,
        adjacency_hits: list[dict],
        p30: dict,
        stats: dict,
        dry_run: bool,
    ) -> Optional[int]:
        """Cap-aware Pythia DR enqueue for flag/block verdicts. Returns row_id or None.

        Gate stack:
        - Only enqueue for verdict in ('flag','block') with non-empty adjacency
        - Daily cap (default 3/day, override via `dr_daily_cap.json` state file)
        - 7-day recency check on the retraction anchor (avoid re-firing)
        - dry_run short-circuits before any side effect
        """
        if dry_run:
            return None
        if verdict not in ("flag", "block"):
            return None
        if not adjacency_hits:
            return None

        dr_seeded = self.load_state("dr_seeded", default=[]) or []
        today = datetime.now(timezone.utc).date().isoformat()
        seeded_today = sum(
            1 for e in dr_seeded
            if str(e.get("ts", ""))[:10] == today
        )
        dr_cap = int(self.load_state("dr_daily_cap", default=3) or 3)
        dr_quota_remaining = max(0, dr_cap - seeded_today)
        stats["dr_seeded_today"] = seeded_today
        stats["dr_quota_remaining"] = dr_quota_remaining
        if dr_quota_remaining <= 0:
            return None

        dr_recent_topics = self.load_state("dr_recent_topics", default=[]) or []
        cutoff_iso = (
            datetime.now(timezone.utc) - timedelta(days=7)
        ).isoformat()
        dr_recent_topics = [
            t for t in dr_recent_topics
            if str(t.get("ts", "")) > cutoff_iso
        ]
        # Recency key is the retraction-title slug (entry-level granularity),
        # not the file path — otherwise the 7-day suppression would block all
        # retraction DRs after the first one.
        top_title = adjacency_hits[0].get("retraction_title", "")
        recency_key = re.sub(r"[^A-Za-z0-9]+", "_", top_title.lower()).strip("_")[:80]
        recent_keys = {t.get("recency_key", "") for t in dr_recent_topics}
        if not recency_key or recency_key in recent_keys:
            stats["dr_skipped_recent"] = stats.get("dr_skipped_recent", 0) + 1
            return None
        top_anchor = adjacency_hits[0].get("anchor", "")

        try:
            top_title = adjacency_hits[0].get(
                "retraction_title", "adjacent retraction"
            )
            title = f"Phylax verify: {top_title}"[:200]
            prompt = self._build_dr_prompt(
                verdict, event, adjacency_hits, p30
            )
            row_id = self.pythia_enqueue_dr(
                title=title,
                prompt=prompt,
                priority=4,
                tier="T4",
                tags={
                    "source": "harmonia_agent:phylax",
                    "substrate_type": "A",
                    "anchor": top_anchor,
                    "verdict": verdict,
                    "jaccard": round(adjacency_hits[0].get("score", 0.0), 3),
                },
            )
            if row_id is not None:
                now_iso = datetime.now(timezone.utc).isoformat()
                dr_seeded.append({
                    "anchor": top_anchor,
                    "queue_row_id": row_id,
                    "ts": now_iso,
                    "verdict": verdict,
                })
                self.save_state("dr_seeded", dr_seeded)
                dr_recent_topics.append({
                    "anchor": top_anchor,
                    "recency_key": recency_key,
                    "row_id": row_id,
                    "ts": now_iso,
                })
                self.save_state("dr_recent_topics", dr_recent_topics)
                stats["dr_seeded"] = stats.get("dr_seeded", 0) + 1
                stats["dr_quota_remaining"] = max(0, dr_quota_remaining - 1)
                stats["dr_last_row_id"] = row_id
                self.log.info(
                    f"DR enqueued anchor={top_anchor} verdict={verdict} "
                    f"row_id={row_id}"
                )
            return row_id
        except Exception as e:
            self.log.warning(f"pythia_enqueue_dr path failed: {e}")
            stats["errors"] += 1
            return None

    # ---- envelope writer --------------------------------------------------

    def _write_envelope(
        self,
        event: dict,
        claim_text: str,
        adjacency_hits: list[dict],
        p30: dict,
        kind: str,
    ) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        msg_id = str(event.get("msg_id", "unknown")).replace(":", "_").replace("/", "_")
        slug = re.sub(r"[^A-Za-z0-9_.-]", "_", msg_id)[:40] or "noid"
        fname = f"verdict_{kind}_{slug}_{utc}.md"
        verdict = self._verdict(adjacency_hits, p30)
        shadow = self._shadow_count(adjacency_hits, p30)
        lines: list[str] = []
        lines.append(f"# Phylax verdict — {verdict.upper()}")
        lines.append("")
        lines.append(f"- kind: {kind}")
        lines.append(f"- source: {event.get('source', 'n/a')}")
        lines.append(f"- msg_id: `{event.get('msg_id', 'n/a')}`")
        lines.append(f"- written_at: {datetime.now(timezone.utc).isoformat()}")
        lines.append(f"- shadow_count: {shadow}")
        lines.append("")
        lines.append("## Claim summary")
        lines.append("")
        lines.append("```")
        lines.append(claim_text[:1500])
        lines.append("```")
        lines.append("")
        lines.append("## Retraction-registry adjacency")
        lines.append("")
        if adjacency_hits:
            for h in adjacency_hits[:5]:
                lines.append(f"- **{h['retraction_title']}** (jaccard {h['score']:.3f})")
                lines.append(f"  - anchor: `{h['anchor']}`")
                if h.get("was_excerpt"):
                    lines.append(f"  - Was: {h['was_excerpt']}")
                if h.get("mechanism_excerpt"):
                    lines.append(f"  - Mechanism: {h['mechanism_excerpt']}")
        else:
            lines.append(f"- no adjacency above threshold {ADJACENCY_THRESHOLD}")
        lines.append("")
        lines.append("## Pattern-30 grade")
        lines.append("")
        lines.append(f"- level: {p30.get('level')}")
        lines.append(f"- name: {p30.get('name')}")
        lines.append(f"- reasoning: {p30.get('reasoning')}")
        lines.append("")
        lines.append("## Recommendation")
        lines.append("")
        rec_map = {
            "pass": "PASS — no adjacency above threshold, Pattern-30 level 0 (or undetermined with no other signal).",
            "flag": "FLAG WITH SHADOW COUNT — at least one signal warrants reviewer attention before promotion lands.",
            "block": "BLOCK WITH MECHANISM — Pattern-30 level >= 2 (definitional coupling); promotion should be halted and the claim restated as algebraic observation.",
        }
        lines.append(rec_map[verdict])
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by Phylax (D:\\Prometheus\\harmonia\\agents\\phylax\\daemon.py). MVP envelope; human review required on FLAG/BLOCK.*")
        return self.write_artifact(fname, "\n".join(lines))

    # ---- backlog ----------------------------------------------------------

    def _list_promoted_symbols(self) -> list[str]:
        if not SYMBOLS_DIR.exists():
            return []
        symbols: list[str] = []
        for p in sorted(SYMBOLS_DIR.glob("*.md")):
            stem = p.stem
            if stem in {"README", "INDEX", "OVERVIEW", "VERSIONING",
                       "CANDIDATES", "PROMOTION_WORKFLOW", "ANCHOR_PROGRESS_LEDGER"}:
                continue
            if stem.endswith("_DRAFT") or "DRAFT" in stem:
                continue
            symbols.append(stem)
        return symbols

    def self_generate_backlog(self) -> list[dict]:
        symbols = self._list_promoted_symbols()
        if not symbols:
            return []
        audited = self.load_state("symbol_last_audit", {}) or {}
        def _age(sym: str) -> str:
            return audited.get(sym, "0")
        symbols_sorted = sorted(symbols, key=_age)
        oldest = symbols_sorted[0]
        return [{
            "kind": "reaudit",
            "symbol": oldest,
            "path": str(SYMBOLS_DIR / f"{oldest}.md"),
        }]

    def _process_promotion_event(self, event: dict) -> Optional[Path]:
        claim_text = event.get("blob") or json.dumps(event.get("fields", {}))
        adjacency_hits = self._retraction_adjacency(claim_text)
        p30 = self._pattern30_grade(claim_text)
        return self._write_envelope(event, claim_text, adjacency_hits, p30, kind="inbound")

    def _process_reaudit_item(self, item: dict) -> Optional[Path]:
        path = Path(item["path"])
        symbol = item["symbol"]
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            self.log.warning(f"reaudit read failed for {path}: {e}")
            return None
        claim_text = text[:3000]
        adjacency_hits = self._retraction_adjacency(claim_text)
        p30 = self._pattern30_grade(claim_text)
        event = {
            "source": "reaudit",
            "msg_id": symbol,
            "fields": {"path": str(path)},
            "blob": text[:400],
        }
        out = self._write_envelope(event, claim_text, adjacency_hits, p30, kind="reaudit")
        verdict = self._verdict(adjacency_hits, p30)
        # The caller (run_tick reaudit branch) doesn't surface a stats dict
        # here; pass an ephemeral one. Real telemetry stays inside run_tick.
        ephemeral_stats: dict = {}
        self._maybe_enqueue_dr(
            verdict, event, adjacency_hits, p30, ephemeral_stats, dry_run=False
        )
        audited = self.load_state("symbol_last_audit", {}) or {}
        audited[symbol] = datetime.now(timezone.utc).isoformat()
        self.save_state("symbol_last_audit", audited)
        return out

    # ---- run_tick ---------------------------------------------------------

    def run_tick(self, dry_run: bool = False) -> dict:
        stats: dict[str, Any] = {
            "items_processed": 0,
            "artifacts_written": 0,
            "errors": 0,
            "backlog_remaining": 0,
            "verdicts": {"pass": 0, "flag": 0, "block": 0},
        }
        artifacts: list[str] = []

        # Inbound sources, in priority order. DR-report scan inserted as
        # the third tier so Phylax always has fresh primary-literature
        # claims to audit even when both the sync stream and recent git
        # log are quiet.
        events = self._scan_sync_streams()
        if not events:
            events = self._scan_git_promotions()
        if not events:
            events = self._scan_dr_reports()

        seen_ids = set(self.load_state("seen_promotion_ids", []) or [])
        new_seen: list[str] = []
        last_commit_to_save: Optional[str] = None

        for ev in events[:5]:
            try:
                if dry_run:
                    stats["items_processed"] += 1
                    new_seen.append(str(ev["msg_id"]))
                    continue
                claim_text = ev.get("blob") or ""
                adjacency_hits = self._retraction_adjacency(claim_text)
                p30 = self._pattern30_grade(claim_text)
                verdict = self._verdict(adjacency_hits, p30)
                out = self._write_envelope(ev, claim_text, adjacency_hits, p30, kind="inbound")
                stats["items_processed"] += 1
                stats["artifacts_written"] += 1
                stats["verdicts"][verdict] = stats["verdicts"].get(verdict, 0) + 1
                artifacts.append(str(out))
                new_seen.append(str(ev["msg_id"]))
                self._maybe_enqueue_dr(
                    verdict, ev, adjacency_hits, p30, stats, dry_run
                )
                if ev.get("source") == "git" and last_commit_to_save is None:
                    last_commit_to_save = str(ev["msg_id"])
            except Exception as e:
                self.log.exception(f"inbound event processing failed: {e}")
                stats["errors"] += 1

        if not dry_run and new_seen:
            merged_seen = list({*seen_ids, *new_seen})[-500:]
            self.save_state("seen_promotion_ids", merged_seen)
        if last_commit_to_save and not dry_run:
            self.save_state("last_seen_commit", last_commit_to_save)

        if not events:
            backlog = self.self_generate_backlog()
            stats["backlog_remaining"] = max(0, len(backlog) - 1)
            for item in backlog[:1]:
                try:
                    if dry_run:
                        stats["items_processed"] += 1
                        continue
                    out = self._process_reaudit_item(item)
                    if out is not None:
                        stats["items_processed"] += 1
                        stats["artifacts_written"] += 1
                        artifacts.append(str(out))
                except Exception as e:
                    self.log.exception(f"reaudit failed: {e}")
                    stats["errors"] += 1

        summary = (
            f"processed={stats['items_processed']} "
            f"artifacts={stats['artifacts_written']} "
            f"errors={stats['errors']} "
            f"verdicts={stats['verdicts']}"
        )
        try:
            started_dt = datetime.fromisoformat(self._tick_started_at) if isinstance(self._tick_started_at, str) else self._tick_started_at
        except Exception:
            started_dt = None
        self.log_work(
            "phylax_tick_complete",
            summary=summary,
            output_path=artifacts[0] if artifacts else None,
            success=stats["errors"] == 0,
            started_at=started_dt,
        )
        return stats
