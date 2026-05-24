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

# Multi-provider fan-out (CHARTER §6: 3-5 frontier model responses).
# N=3 trades coverage vs latency: at ~5s per cascade call, 3 calls in
# sequence stays within tick budget. Bump to 4-5 once Pythia-style
# parallel dispatch ships.
FANOUT_N_MODELS = 3

# Convergence threshold for PATTERN_* candidate emission. When N
# providers' critiques share >= this fraction of bullet-head tokens,
# emit a primitive_proposal candidate (the structural defect is
# convergent across models, not single-provider noise).
CONVERGENCE_PATTERN_THRESHOLD = 0.40


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
        """Legacy single-provider critique. Retained for any caller; the
        production path uses _critique_fanout below."""
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

    def _critique_fanout(self, artifact_path: Path) -> list[dict]:
        """Multi-provider cross-pollination. Fires up to FANOUT_N_MODELS
        cascade calls, each excluding previously-served providers, so
        successive responses come from distinct frontier models.

        Returns list of {provider, critique_text, ok} dicts in fire order.
        Empty list if the artifact read failed.
        """
        try:
            text = artifact_path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            self.log.warning(f"critique read failed {artifact_path}: {e}")
            return []
        truncated = text[:MAX_ARTIFACT_BYTES]
        truncation_note = ""
        if len(text) > MAX_ARTIFACT_BYTES:
            truncation_note = f"\n\n[truncated to first {MAX_ARTIFACT_BYTES} chars; original length {len(text)}]"
        prompt = (
            f"Artifact: `{artifact_path.relative_to(REPO_ROOT)}`\n\n"
            f"```\n{truncated}{truncation_note}\n```\n"
        )

        try:
            from llm_cascade import call_llm_with_provider  # type: ignore
        except Exception as e:
            self.log.warning(f"llm_cascade import failed in fanout: {e}")
            return []

        results: list[dict] = []
        excluded: list[str] = []
        for i in range(FANOUT_N_MODELS):
            critique, provider = call_llm_with_provider(
                prompt,
                system=CRITIQUE_SYSTEM,
                max_tokens=900,
                temperature=0.5,
                exclude_providers=excluded,
            )
            ok = bool(
                provider
                and critique
                and "(LLM cascade failed" not in critique
            )
            results.append({
                "provider": provider or f"<failed_call_{i}>",
                "critique": critique if ok else None,
                "ok": ok,
            })
            if provider:
                excluded.append(provider)
        return results

    @staticmethod
    def _extract_bullet_heads(critique: str) -> list[str]:
        """Pull the head clause from each bullet in a critique. Bullets
        recognized by leading -, *, or 1. style. Returns lowercased head
        clauses for naive overlap analysis."""
        if not critique:
            return []
        heads: list[str] = []
        for line in critique.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            # Match bullet markers
            m = re.match(r"^(?:[-*]|\d+[.)])\s+(.+)$", stripped)
            if not m:
                continue
            head = m.group(1)
            # Take the first ~12 words of the bullet (the head clause)
            words = head.split()[:12]
            heads.append(" ".join(words).lower())
        return heads

    @staticmethod
    def _tokens(text: str) -> set[str]:
        """Lowercase content tokens of length >=5 (filters stopwords without
        a list). Used for cross-critique overlap scoring."""
        return {
            t.strip(".,;:!?()[]{}'\"`")
            for t in text.lower().split()
            if len(t.strip(".,;:!?()[]{}'\"`")) >= 5
        }

    def _convergence_analysis(self, fanout_results: list[dict]) -> dict:
        """Compute pairwise Jaccard overlap on bullet-head token sets
        across the N critiques. Returns a structured summary suitable
        for the artifact + PATTERN_* threshold checking.
        """
        ok_results = [r for r in fanout_results if r.get("ok")]
        n_ok = len(ok_results)
        if n_ok < 2:
            return {
                "n_models_ok": n_ok,
                "pairwise_jaccards": [],
                "shared_tokens_3plus": [],
                "shared_tokens_2plus": [],
                "max_pairwise_jaccard": 0.0,
                "convergence_score": 0.0,
                "pattern_candidate": False,
            }
        # Per-model token sets (over bullet heads)
        per_model: list[set] = []
        for r in ok_results:
            heads = self._extract_bullet_heads(r["critique"])
            head_text = " ".join(heads)
            per_model.append(self._tokens(head_text))
        # Pairwise Jaccard
        pairs = []
        for i in range(n_ok):
            for j in range(i + 1, n_ok):
                a, b = per_model[i], per_model[j]
                if not (a or b):
                    j_score = 0.0
                else:
                    j_score = len(a & b) / max(1, len(a | b))
                pairs.append({
                    "i": i, "j": j,
                    "providers": [ok_results[i]["provider"], ok_results[j]["provider"]],
                    "jaccard": round(j_score, 3),
                })
        max_j = max((p["jaccard"] for p in pairs), default=0.0)
        # Tokens that appear in >=2 and >=3 critiques
        from collections import Counter
        token_appearances: Counter = Counter()
        for tokens in per_model:
            for t in tokens:
                token_appearances[t] += 1
        shared_2plus = sorted(
            [t for t, c in token_appearances.items() if c >= 2],
            key=lambda x: -token_appearances[x],
        )[:30]
        shared_3plus = sorted(
            [t for t, c in token_appearances.items() if c >= 3],
            key=lambda x: -token_appearances[x],
        )[:30]
        # Convergence score: fraction of total distinct tokens that
        # appear in >=2 critiques. Bounded [0, 1].
        total_distinct = len(token_appearances)
        convergence_score = (
            len(shared_2plus) / total_distinct if total_distinct else 0.0
        )
        pattern_candidate = (
            convergence_score >= CONVERGENCE_PATTERN_THRESHOLD and n_ok >= 3
        )
        return {
            "n_models_ok": n_ok,
            "pairwise_jaccards": pairs,
            "shared_tokens_3plus": shared_3plus,
            "shared_tokens_2plus": shared_2plus,
            "max_pairwise_jaccard": round(max_j, 3),
            "convergence_score": round(convergence_score, 3),
            "pattern_candidate": pattern_candidate,
        }

    # ---- artifact writers -------------------------------------------------

    def _write_feedback(
        self, item: dict, fanout: list[dict], convergence: dict
    ) -> Path:
        """Multi-provider feedback artifact. Per-provider critiques in
        separate sections; convergence summary at the bottom."""
        date_slug = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        artifact_slug = _safe_slug(Path(item["rel"]).stem)
        fname = f"feedback_{artifact_slug}_{date_slug}.md"
        out_path = REPO_ROOT / "pivot" / fname
        out_path.parent.mkdir(parents=True, exist_ok=True)
        ok_providers = [r["provider"] for r in fanout if r.get("ok")]
        lines: list[str] = []
        lines.append(f"# Cross-pollination feedback — `{item['rel']}`")
        lines.append("")
        lines.append(f"- generated_at: {datetime.now(timezone.utc).isoformat()}")
        lines.append(f"- generated_by: Moros (charon/agents/moros/daemon.py)")
        lines.append(f"- fanout_n_attempted: {len(fanout)}")
        lines.append(f"- fanout_n_ok: {len(ok_providers)}")
        lines.append(f"- providers_consulted: {ok_providers}")
        lines.append(f"- artifact_size_bytes: {Path(item['path']).stat().st_size}")
        lines.append("")
        for i, r in enumerate(fanout, 1):
            lines.append(f"## Critique {i} — {r['provider']}")
            lines.append("")
            if r.get("ok"):
                lines.append(r["critique"])
            else:
                lines.append(f"_(cascade call {i} failed; provider returned no usable text)_")
            lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(
            f"*v0.2 multi-provider cross-pollination per CHARTER §6. "
            f"Convergence analysis in companion meta_analysis_*.md.*"
        )
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return out_path

    def _write_meta_analysis(
        self, item: dict, feedback_path: Path, convergence: dict
    ) -> Path:
        """Real convergence triage now (not stub). Pairwise Jaccard,
        shared-token analysis, PATTERN_* candidate flag."""
        date_slug = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        artifact_slug = _safe_slug(Path(item["rel"]).stem)
        fname = f"meta_analysis_{artifact_slug}_{date_slug}.md"
        out_path = REPO_ROOT / "pivot" / fname
        out_path.parent.mkdir(parents=True, exist_ok=True)
        n_ok = convergence["n_models_ok"]
        lines: list[str] = []
        lines.append(f"# Cross-pollination meta-analysis — `{item['rel']}`")
        lines.append("")
        lines.append(f"- generated_at: {datetime.now(timezone.utc).isoformat()}")
        lines.append(f"- feedback_source: `{feedback_path.relative_to(REPO_ROOT)}`")
        lines.append(f"- n_models_ok: {n_ok}")
        lines.append(f"- convergence_score: **{convergence['convergence_score']}**  (PATTERN_* threshold: {CONVERGENCE_PATTERN_THRESHOLD})")
        lines.append(f"- max_pairwise_jaccard: {convergence['max_pairwise_jaccard']}")
        lines.append(f"- pattern_candidate_emitted: {convergence['pattern_candidate']}")
        lines.append("")
        lines.append("## Pairwise Jaccard (bullet-head token overlap)")
        lines.append("")
        if not convergence["pairwise_jaccards"]:
            lines.append("_(insufficient OK critiques for pairwise comparison)_")
        else:
            for p in convergence["pairwise_jaccards"]:
                providers = " ↔ ".join(p["providers"])
                lines.append(f"- {providers}: **{p['jaccard']}**")
        lines.append("")
        lines.append(f"## Shared tokens (≥3 critiques)")
        lines.append("")
        if convergence["shared_tokens_3plus"]:
            lines.append(", ".join(f"`{t}`" for t in convergence["shared_tokens_3plus"][:20]))
        else:
            lines.append("_(no tokens appear across ≥3 critiques)_")
        lines.append("")
        lines.append(f"## Shared tokens (≥2 critiques)")
        lines.append("")
        if convergence["shared_tokens_2plus"]:
            lines.append(", ".join(f"`{t}`" for t in convergence["shared_tokens_2plus"][:30]))
        else:
            lines.append("_(no tokens shared across ≥2 critiques)_")
        lines.append("")
        lines.append("## Triage interpretation")
        lines.append("")
        if convergence["pattern_candidate"]:
            lines.append(
                f"**PATTERN candidate fired** (convergence_score {convergence['convergence_score']} "
                f">= threshold {CONVERGENCE_PATTERN_THRESHOLD}, n_ok={n_ok} models). "
                f"See `pattern_candidate_*.md` companion artifact for the "
                f"structured proposal to file against `harmonia/memory/pattern_library.md`."
            )
        elif n_ok >= 2:
            lines.append(
                f"Sub-threshold convergence ({convergence['convergence_score']} < {CONVERGENCE_PATTERN_THRESHOLD}). "
                f"Critiques agree on some token-level features but not enough "
                f"to claim a structural defect generalizable across artifacts. "
                f"Record-only; no PATTERN_* candidate filed."
            )
        else:
            lines.append(
                f"Single-provider only (n_ok={n_ok}); convergence cannot be computed. "
                f"Cascade exhausted or rate-limited; review feedback artifact manually."
            )
        lines.append("")
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return out_path

    def _emit_pattern_candidate(
        self, item: dict, fanout: list[dict], convergence: dict
    ) -> Optional[Path]:
        """Emit a PATTERN_* candidate artifact when fanout convergence
        crosses the threshold. Structured for Phylax-class review +
        eventual landing in harmonia/memory/pattern_library.md."""
        try:
            utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            artifact_slug = _safe_slug(Path(item["rel"]).stem)
            fname = f"pattern_candidate_{artifact_slug}_{utc}.md"
            ok_providers = [r["provider"] for r in fanout if r.get("ok")]
            lines = [
                f"# PATTERN candidate — `{item['rel']}`",
                "",
                f"- emitted_at: {datetime.now(timezone.utc).isoformat()}",
                f"- emitted_by: Moros (charon/agents/moros/daemon.py)",
                f"- source_artifact: `{item['rel']}`",
                f"- convergence_score: {convergence['convergence_score']}",
                f"- max_pairwise_jaccard: {convergence['max_pairwise_jaccard']}",
                f"- n_models_ok: {convergence['n_models_ok']}",
                f"- providers: {ok_providers}",
                "",
                "## Convergent critique tokens (≥3 models)",
                "",
                ", ".join(f"`{t}`" for t in convergence["shared_tokens_3plus"][:30])
                or "_(none)_",
                "",
                "## Recommendation",
                "",
                "Surface to Phylax for adjudication. If the convergent "
                "critique tokens identify a structural failure mode "
                "(not just shared rhetoric), promote to "
                "`harmonia/memory/pattern_library.md` as a substrate-level "
                "PATTERN_* entry. If the tokens reflect surface-level "
                "vocabulary overlap (e.g., shared technical terminology "
                "from the artifact itself), reject as false-convergence.",
                "",
                "## Companion artifacts",
                "",
                f"- feedback: `pivot/feedback_{artifact_slug}_*.md`",
                f"- meta_analysis: `pivot/meta_analysis_{artifact_slug}_*.md`",
                "",
            ]
            return self.write_artifact(fname, "\n".join(lines))
        except Exception as e:
            self.log.warning(f"pattern_candidate emit failed: {e}")
            return None

    def _emit_self_audit_null(self, reason: str) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"self_audit_null_{utc}.md"
        return self.write_artifact(fname, f"# Moros SELF_AUDIT_NULL\n\n- reason: {reason}\n- at: {datetime.now(timezone.utc).isoformat()}\n")

    # ---- DR prompt builder (substrate A/B/C — cross-pollination) --------

    def _build_dr_prompt(self, artifact_rel: str) -> str:
        """Cross-pollination candidate hunt grounded in the artifact Moros
        is currently cross-pollinating. Per doctrine §6 Moros row."""
        return (
            f"Moros (Charon swarm, cross-pollination automator) is "
            f"adversarially cross-pollinating the load-bearing artifact "
            f"`{artifact_rel}`. Substrate type A/B/C (cross-fertilization).\n\n"
            f"Identify three to five 2025-2026 primary-literature results "
            f"from domains adjacent to the substantive content of the "
            f"artifact whose **technique** might transfer to extend, "
            f"refute, or sharpen the artifact's core claims. For each:\n"
            f"- the source-domain claim or technique (name + arXiv ID + DOI)\n"
            f"- a specific target-domain claim in the artifact this would "
            f"attack or extend (quote or paraphrase the line)\n"
            f"- the mechanical step needed to transfer (functor? base "
            f"change? coordinate translation? specialization?)\n"
            f"- a falsification or sharpening outcome that would be "
            f"observed if the transfer succeeds\n\n"
            f"Verification criterion: source-domain claim must cite "
            f"arXiv ID + DOI (post-2024). Target-domain claim must "
            f"quote a specific line from the artifact (not paraphrase). "
            f"Transfer mechanism must be concrete enough that a domain "
            f"expert could attempt the move in one paper-week.\n\n"
            f"Landing path: Moros feedback artifact "
            f"(`pivot/feedback_<artifact-slug>_<date>.md`); strongest "
            f"transfers become PATTERN_* candidates filed against the "
            f"substrate vocabulary."
        )

    def _emit_dr_intake(self, notification: dict) -> Optional[Path]:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        row_id = notification.get("row_id", "noid")
        fname = f"dr_intake_{row_id}_{utc}.md"
        lines = [
            f"# Moros DR intake — row {row_id}",
            "",
            f"- received_at: {datetime.now(timezone.utc).isoformat()}",
            f"- substrate_type: A/B/C (cross-pollination)",
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
            "Extract each transfer candidate into the cross-pollination "
            "feedback file for the corresponding artifact. PATTERN_* "
            "candidates promote to harmonia/memory/pattern_library.md "
            "via Phylax review.",
            "",
        ]
        return self.write_artifact(fname, "\n".join(lines))

    # ---- run_tick ---------------------------------------------------------

    def run_tick(self, dry_run: bool = False) -> dict:
        stats: dict[str, Any] = {
            "items_processed": 0,
            "artifacts_written": 0,
            "errors": 0,
            "backlog_remaining": 0,
            "artifact_targeted": None,
            "critique_obtained": False,
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
        chosen_artifact: Optional[dict] = backlog[0] if backlog else None

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
                    fanout = self._critique_fanout(Path(item["path"]))
                    n_ok = sum(1 for r in fanout if r.get("ok"))
                    stats["fanout_n_attempted"] = len(fanout)
                    stats["fanout_n_ok"] = n_ok
                    stats["fanout_providers"] = [
                        r["provider"] for r in fanout if r.get("ok")
                    ]
                    if n_ok == 0:
                        out = self._emit_self_audit_null(
                            f"cascade exhausted for {item['rel']} ({len(fanout)} attempts, 0 ok)"
                        )
                        artifacts.append(str(out))
                        stats["artifacts_written"] += 1
                        stats["items_processed"] += 1
                    else:
                        stats["critique_obtained"] = True
                        convergence = self._convergence_analysis(fanout)
                        stats["convergence_score"] = convergence["convergence_score"]
                        stats["pattern_candidate"] = convergence["pattern_candidate"]
                        stats["max_pairwise_jaccard"] = convergence["max_pairwise_jaccard"]
                        fb_path = self._write_feedback(item, fanout, convergence)
                        artifacts.append(str(fb_path))
                        meta_path = self._write_meta_analysis(item, fb_path, convergence)
                        artifacts.append(str(meta_path))
                        stats["items_processed"] += 1
                        stats["artifacts_written"] += 2
                        if convergence["pattern_candidate"]:
                            patt_path = self._emit_pattern_candidate(item, fanout, convergence)
                            if patt_path is not None:
                                artifacts.append(str(patt_path))
                                stats["artifacts_written"] += 1
                        # Mark processed
                        processed = self.load_state("processed_artifacts", {}) or {}
                        processed[item["rel"]] = {
                            "mtime": item["mtime"],
                            "processed_at": datetime.now(timezone.utc).isoformat(),
                            "feedback_path": str(fb_path.relative_to(REPO_ROOT)),
                            "meta_analysis_path": str(meta_path.relative_to(REPO_ROOT)),
                            "n_models_ok": n_ok,
                            "convergence_score": convergence["convergence_score"],
                        }
                        self.save_state("processed_artifacts", processed)
            except Exception as e:
                self.log.exception(f"cross-pollination failed for {item['rel']}: {e}")
                stats["errors"] += 1

        # ---- Pythia DR enqueue (cross-pollination grounded in this artifact) ----
        if (not dry_run) and chosen_artifact is not None:
            dr_result = self._dr_enqueue_if_quota(
                title=f"Moros cross-pollination: {chosen_artifact['rel']}",
                prompt=self._build_dr_prompt(chosen_artifact["rel"]),
                recent_coverage_keywords=["Moros", chosen_artifact["rel"]],
                substrate_type="A",
                tags={"artifact_path": chosen_artifact["rel"]},
            )
            stats.update({
                "dr_seeded": dr_result["dr_seeded"],
                "dr_seeded_today": dr_result["dr_seeded_today"],
                "dr_quota_remaining": dr_result["dr_quota_remaining"],
                "dr_skipped_reason": dr_result["dr_skipped_reason"],
                "dr_row_id": dr_result["dr_row_id"],
            })

        if not dry_run:
            self._emit_dr_discipline_adoption(
                daily_cap=3,
                substrate_types=["A", "B", "C"],
                builder_ref="charon/agents/moros/daemon.py:_build_dr_prompt",
            )

        summary = (
            f"artifact={stats['artifact_targeted']} "
            f"critique={stats['critique_obtained']} "
            f"artifacts={stats['artifacts_written']} "
            f"errors={stats['errors']} "
            f"dr_seeded={stats.get('dr_seeded')} "
            f"dr_inbox={stats['dr_inbox_processed']}"
        )
        self.log_work(
            "moros_tick_complete",
            summary=summary,
            output_path=artifacts[0] if artifacts else None,
            success=stats["errors"] == 0,
        )
        return stats
