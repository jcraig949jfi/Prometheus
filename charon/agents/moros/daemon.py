"""Moros — cross-pollination automator (Charon child, MVP).

One tick = pick the next un-cross-pollinated load-bearing artifact,
dispatch to DeepSeek for adversarial critique, write a feedback artifact
+ meta-analysis stub. Multi-model cascade gated on budget greenlight.

See `charon/agents/moros/CHARTER.md` for the one-page brief.
"""
from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional

from charon.agents._base import CharonAgent
from harmonia.agents._base import REPO_ROOT


# Load-bearing-artifact pattern (relative to REPO_ROOT)
LOAD_BEARING_GLOBS = [
    ("pivot", "*.md"),
    ("harmonia/memory/architecture", "*.md"),
    ("aporia/doctrine", "*.md"),
    ("roles", "*/CHARTER.md"),
]

# Skip patterns — these are Moros's own outputs (recursive cross-pollination
# would be funny but counterproductive)
SKIP_FILENAME_PATTERNS = [
    re.compile(r"^feedback_.*\.md$"),
    re.compile(r"^meta_analysis_.*\.md$"),
]

# Skip dirs
SKIP_DIRS = {"feedback", "meta_analysis"}

MAX_ARTIFACT_BYTES = 30_000  # truncate huge docs to fit DeepSeek context
LOOKBACK_DAYS = 30


def _safe_slug(text: str, max_len: int = 50) -> str:
    s = re.sub(r"[^A-Za-z0-9_.-]", "_", text)
    return s[:max_len] or "noid"


CRITIQUE_SYSTEM = (
    "You are an independent adversarial reviewer of a research substrate. "
    "Read the artifact below and produce a structured critique. Focus on: "
    "(1) structural defects (load-bearing assumptions that aren't justified), "
    "(2) missing citations or hand-waved evidence, "
    "(3) alternative framings the author may have prematurely closed off, "
    "(4) terms or coordinates that are silently collapsed (HARD-5 violations), "
    "(5) overclaim risk (where the language outruns the evidence). "
    "Output 5-8 bullet points, each a concrete critique with a quote-or-paraphrase "
    "of the line the critique targets. Do NOT produce summary praise; this is "
    "an adversarial pass. If you find nothing to critique, say so explicitly "
    "with the specific reason why."
)


class MorosAgent(CharonAgent):
    """Cross-pollination automator. Picks one un-cross-pollinated
    load-bearing artifact per tick, dispatches to DeepSeek, writes
    feedback + meta-analysis artifacts."""

    name = "Moros"
    role = "cross-pollination automator (upstream of Phylax)"

    # ---- backlog ----------------------------------------------------------

    def _enumerate_candidates(self) -> list[Path]:
        cands: list[Path] = []
        for sub, pat in LOAD_BEARING_GLOBS:
            base = REPO_ROOT / sub
            if not base.exists():
                continue
            for p in base.rglob(pat):
                if any(rx.match(p.name) for rx in SKIP_FILENAME_PATTERNS):
                    continue
                if any(seg in SKIP_DIRS for seg in p.parts):
                    continue
                try:
                    if p.stat().st_size < 500:  # skip tiny stubs
                        continue
                except Exception:
                    continue
                cands.append(p)
        return cands

    def _has_feedback(self, artifact_path: Path) -> bool:
        """Check whether a feedback_<slug>_*.md exists under pivot/ for this artifact."""
        pivot_dir = REPO_ROOT / "pivot"
        if not pivot_dir.exists():
            return False
        slug = artifact_path.stem
        pattern = re.compile(rf"^feedback_.*{re.escape(slug)}.*\.md$", re.IGNORECASE)
        try:
            for p in pivot_dir.iterdir():
                if pattern.match(p.name):
                    return True
        except Exception:
            return False
        return False

    def self_generate_backlog(self) -> list[dict]:
        processed = self.load_state("processed_artifacts", {}) or {}
        cutoff = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
        items: list[dict] = []
        for p in self._enumerate_candidates():
            rel = str(p.relative_to(REPO_ROOT))
            try:
                stat = p.stat()
                mtime_dt = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            except Exception:
                continue
            # Backfill window: prefer recent artifacts but allow historical
            # backfill if not yet processed.
            already_done = rel in processed
            has_fb = self._has_feedback(p)
            if already_done and has_fb:
                continue
            # Prefer artifacts modified in the lookback window; backfill older
            # ones at lower priority (sort key handles this).
            recency_bucket = 0 if mtime_dt >= cutoff else 1
            items.append({
                "rel": rel,
                "path": str(p),
                "mtime": int(stat.st_mtime),
                "recency_bucket": recency_bucket,
                "has_feedback": has_fb,
            })
        # Recent first (bucket 0); within bucket, newest first.
        items.sort(key=lambda d: (d["recency_bucket"], -d["mtime"]))
        return items

    # ---- dispatch ---------------------------------------------------------

    def _critique(self, artifact_path: Path) -> Optional[str]:
        try:
            text = artifact_path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            self.log.warning(f"critique read failed {artifact_path}: {e}")
            return None
        truncated = text[:MAX_ARTIFACT_BYTES]
        truncation_note = ""
        if len(text) > MAX_ARTIFACT_BYTES:
            truncation_note = f"\n\n[truncated to first {MAX_ARTIFACT_BYTES} chars; original length {len(text)}]"
        prompt = (
            f"Artifact: `{artifact_path.relative_to(REPO_ROOT)}`\n\n"
            f"```\n{truncated}{truncation_note}\n```\n"
        )
        return self.deepseek_complete(
            prompt=prompt,
            system=CRITIQUE_SYSTEM,
            max_tokens=900,
            temperature=0.5,
        )

    # ---- artifact writers -------------------------------------------------

    def _write_feedback(self, item: dict, critique: str) -> Path:
        date_slug = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        artifact_slug = _safe_slug(Path(item["rel"]).stem)
        fname = f"feedback_{artifact_slug}_{date_slug}.md"
        # Write under pivot/ (mirroring the manual cross-pollination convention).
        out_path = REPO_ROOT / "pivot" / fname
        out_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []
        lines.append(f"# Cross-pollination feedback — `{item['rel']}`")
        lines.append("")
        lines.append(f"- generated_at: {datetime.now(timezone.utc).isoformat()}")
        lines.append(f"- generated_by: Moros (charon/agents/moros/daemon.py)")
        lines.append(f"- model: deepseek-chat")
        lines.append(f"- system_prompt: adversarial-review (5-8 bullet critique)")
        lines.append(f"- artifact_size_bytes: {Path(item['path']).stat().st_size}")
        lines.append("")
        lines.append("## Raw critique")
        lines.append("")
        lines.append(critique)
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*MVP cross-pollination: single-model (DeepSeek). Multi-model cascade (Claude + GPT + Gemini + DeepSeek) lands when budget is greenlit. See `roles/Charon/CHARTER.md` §6.*")
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return out_path

    def _write_meta_analysis(self, item: dict, feedback_path: Path) -> Path:
        date_slug = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        artifact_slug = _safe_slug(Path(item["rel"]).stem)
        fname = f"meta_analysis_{artifact_slug}_{date_slug}.md"
        out_path = REPO_ROOT / "pivot" / fname
        out_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []
        lines.append(f"# Cross-pollination meta-analysis — `{item['rel']}`")
        lines.append("")
        lines.append(f"- generated_at: {datetime.now(timezone.utc).isoformat()}")
        lines.append(f"- feedback_source: `{feedback_path.relative_to(REPO_ROOT)}`")
        lines.append(f"- models_consulted: [deepseek-chat]")
        lines.append(f"- convergence_n_models: 1 (MVP — multi-model cascade deferred to v0.2)")
        lines.append("")
        lines.append("## Triage")
        lines.append("")
        lines.append("MVP convergence triage cannot run on a single model (convergence requires N ≥ 2). This stub records the cross-pollination event; human or Phylax-class review categorizes the critique into:")
        lines.append("")
        lines.append("- **high-convergence (≥3 models)** — substrate-grade revisions, fold into artifact in-place")
        lines.append("- **medium-convergence (2 models)** — note for review")
        lines.append("- **singleton-signal** — record, don't act unilaterally")
        lines.append("")
        lines.append("## Next steps")
        lines.append("")
        lines.append("1. Read the feedback artifact at the link above.")
        lines.append("2. If a PATTERN_* candidate emerges (a structural failure mode generalizable across artifacts), file under `harmonia/memory/pattern_library.md` for Phylax.")
        lines.append("3. If the critique surfaces a HARD-5 violation, route to Acheron's collision-candidate adjudication.")
        lines.append("4. Once 2+ additional model responses are gathered (v0.2 multi-model cascade), re-run this meta-analysis with proper convergence triage.")
        lines.append("")
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return out_path

    def _emit_self_audit_null(self, reason: str) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"self_audit_null_{utc}.md"
        return self.write_artifact(fname, f"# Moros SELF_AUDIT_NULL\n\n- reason: {reason}\n- at: {datetime.now(timezone.utc).isoformat()}\n")

    # ---- run_tick ---------------------------------------------------------

    def run_tick(self, dry_run: bool = False) -> dict:
        stats: dict[str, Any] = {
            "items_processed": 0,
            "artifacts_written": 0,
            "errors": 0,
            "backlog_remaining": 0,
            "artifact_targeted": None,
            "critique_obtained": False,
        }
        artifacts: list[str] = []

        backlog = self.self_generate_backlog()
        stats["backlog_remaining"] = max(0, len(backlog) - 1)

        if not backlog:
            try:
                if not dry_run:
                    out = self._emit_self_audit_null("no un-cross-pollinated load-bearing artifacts found")
                    artifacts.append(str(out))
                    stats["artifacts_written"] += 1
                stats["items_processed"] += 1
            except Exception as e:
                self.log.exception(f"self_audit_null emit failed: {e}")
                stats["errors"] += 1
        else:
            item = backlog[0]
            stats["artifact_targeted"] = item["rel"]
            try:
                if dry_run:
                    stats["items_processed"] += 1
                else:
                    critique = self._critique(Path(item["path"]))
                    if not critique:
                        out = self._emit_self_audit_null(f"DeepSeek unavailable for {item['rel']}")
                        artifacts.append(str(out))
                        stats["artifacts_written"] += 1
                        stats["items_processed"] += 1
                    else:
                        stats["critique_obtained"] = True
                        fb_path = self._write_feedback(item, critique)
                        artifacts.append(str(fb_path))
                        meta_path = self._write_meta_analysis(item, fb_path)
                        artifacts.append(str(meta_path))
                        stats["items_processed"] += 1
                        stats["artifacts_written"] += 2
                        # Mark processed
                        processed = self.load_state("processed_artifacts", {}) or {}
                        processed[item["rel"]] = {
                            "mtime": item["mtime"],
                            "processed_at": datetime.now(timezone.utc).isoformat(),
                            "feedback_path": str(fb_path.relative_to(REPO_ROOT)),
                            "meta_analysis_path": str(meta_path.relative_to(REPO_ROOT)),
                        }
                        self.save_state("processed_artifacts", processed)
            except Exception as e:
                self.log.exception(f"cross-pollination failed for {item['rel']}: {e}")
                stats["errors"] += 1

        summary = (
            f"artifact={stats['artifact_targeted']} "
            f"critique={stats['critique_obtained']} "
            f"artifacts={stats['artifacts_written']} "
            f"errors={stats['errors']}"
        )
        self.log_work(
            "moros_tick_complete",
            summary=summary,
            output_path=artifacts[0] if artifacts else None,
            success=stats["errors"] == 0,
        )
        return stats
