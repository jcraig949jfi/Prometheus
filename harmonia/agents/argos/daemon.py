"""Argos — PROBLEM_LENS_CATALOG@v1 expander (Harmonia child).

Per-tick MVP behavior is documented in
`D:\\Prometheus\\harmonia\\agents\\argos\\CHARTER.md`. This file is the
source-of-truth implementation.

Hard contract (set by the rotation orchestrator at
`D:\\Prometheus\\scripts\\harmonia_loop.py`):
- Exports class `ArgosAgent(HarmoniaAgent)` with `name="Argos"`,
  `role` set, `machine="M2"`.
- Implements `run_tick(self, dry_run=False) -> dict`.
- Implements `self_generate_backlog(self) -> list[dict]`.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from harmonia.agents._base import HarmoniaAgent, REPO_ROOT


# -- paths (absolute, drive-lettered everywhere) ----------------------------

APORIA_DIR = REPO_ROOT / "aporia"
APORIA_QUEUE = APORIA_DIR / "docs" / "gemini_research_queue" / "queue.jsonl"

HARMONIA_MEMORY = REPO_ROOT / "harmonia" / "memory"
METHODOLOGY_TOOLKIT = HARMONIA_MEMORY / "methodology_toolkit.md"
METHODOLOGY_MPA = HARMONIA_MEMORY / "methodology_multi_perspective_attack.md"
AXIS_CLASS_TAGS = HARMONIA_MEMORY / "axis_class_tags.md"
CATALOGS_DIR = HARMONIA_MEMORY / "catalogs"


# -- regexes ----------------------------------------------------------------

# methodology_toolkit.md header lines look like:
#   ### 1. `KOLMOGOROV_HAT@v1` — fingerprint compressibility
_TOOLKIT_OP_RX = re.compile(
    r"^###\s+\d+\.\s+`?([A-Z][A-Z0-9_]*@v\d+)`?",
    re.MULTILINE,
)

# Fallback for headers with the operator name unquoted:
#   ### 1. KOLMOGOROV_HAT@v1 — …
_TOOLKIT_OP_RX_PLAIN = re.compile(
    r"^###\s+\d+\.\s+([A-Z][A-Z0-9_]*@v\d+)",
    re.MULTILINE,
)


# Five disciplinary stances from
# methodology_multi_perspective_attack.md — used for tier-2+ problems.
DISCIPLINARY_STANCES = [
    "dynamical_systems",
    "information_theory",
    "renormalization_group",
    "adversarial_empirical",
    "mathematical_physics",
]


# Cheap-first lens ordering for tier-1 problems (per spec step 4).
TIER1_LENS_ORDER = [
    "KOLMOGOROV_HAT@v1",
    "CRITICAL_EXPONENT@v1",
    "MDL_SCORER@v1",
]


# Verdict bonus (anti-reward-capture: map_of_disagreement > null > durable).
_VERDICT_BONUS = {
    "map_of_disagreement": 3,
    None: 1,
    "null": 1,
    "coordinate_invariant": 0,
    "durable": 0,
}


# -- utilities --------------------------------------------------------------

def _utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _slugify(text: str, maxlen: int = 60) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", text or "problem").strip("-").lower()
    return (s or "problem")[:maxlen]


def _safe_read_text(path: Path) -> Optional[str]:
    try:
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def _norm_tier(raw: Any) -> str:
    """Normalize 'T1' / 'tier_1' / 1 → '1' for heuristic gating."""
    if raw is None:
        return ""
    s = str(raw).strip().lower()
    m = re.search(r"\d+", s)
    return m.group(0) if m else s


# -- Argos -----------------------------------------------------------------

class ArgosAgent(HarmoniaAgent):
    """PROBLEM_LENS_CATALOG@v1 expander."""

    name = "Argos"
    role = "PROBLEM_LENS_CATALOG@v1 expander (lens-fingerprint accretion)"
    machine = "M2"

    # -- corpus + shelf parsing --------------------------------------------

    def _parse_problem_corpus(self) -> list[dict]:
        """Return list of {id, title, prompt, tier, source} dicts.

        Primary source: Aporia gemini_research_queue. Falls back to a
        depth<=3 markdown + questions.jsonl scan of D:\\Prometheus\\aporia\\
        plus anchor catalogs under harmonia/memory/catalogs.
        """
        problems: list[dict] = []
        seen_ids: set[str] = set()

        # (1) Primary: gemini research queue
        if APORIA_QUEUE.exists():
            try:
                for line in APORIA_QUEUE.read_text(
                    encoding="utf-8", errors="replace"
                ).splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    pid = str(obj.get("id") or obj.get("problem_id") or "").strip()
                    if not pid or pid in seen_ids:
                        continue
                    seen_ids.add(pid)
                    problems.append({
                        "id": pid,
                        "title": str(obj.get("title") or pid),
                        "prompt": str(obj.get("prompt") or obj.get("statement") or ""),
                        "tier": str(obj.get("tier") or obj.get("priority") or ""),
                        "source": "aporia_queue",
                    })
            except Exception as e:
                self.log.warning(f"queue.jsonl parse failed: {e}")

        # (2) Always include anchor catalogs as known problems so Argos
        # can re-expand them even when the queue is the primary source.
        if CATALOGS_DIR.exists():
            for cat in sorted(CATALOGS_DIR.glob("*.md")):
                if cat.name.lower() == "readme.md":
                    continue
                text = _safe_read_text(cat) or ""
                pid = cat.stem
                # try to lift problem_id from frontmatter
                m = re.search(r"^problem_id:\s*(\S+)", text, re.MULTILINE)
                if m:
                    pid = m.group(1).strip()
                if pid in seen_ids:
                    continue
                seen_ids.add(pid)
                title_m = re.search(
                    r"^catalog_name:\s*(.+)$", text, re.MULTILINE
                )
                title = title_m.group(1).strip() if title_m else pid
                problems.append({
                    "id": pid,
                    "title": title,
                    "prompt": "",
                    "tier": "",
                    "source": f"catalog:{cat.name}",
                })

        # (3) Fallback / supplement: per-domain questions.jsonl under aporia/
        # Only used if the queue was missing entirely (to avoid swamping
        # Argos with thousands of MATH-* questions when the queue is the
        # operator inbox).
        if not APORIA_QUEUE.exists() and APORIA_DIR.exists():
            for jl in APORIA_DIR.glob("*/questions.jsonl"):
                try:
                    for line in jl.read_text(
                        encoding="utf-8", errors="replace"
                    ).splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                        except Exception:
                            continue
                        pid = str(obj.get("id") or "").strip()
                        if not pid or pid in seen_ids:
                            continue
                        if str(obj.get("status", "")).lower() not in (
                            "", "open", "unresolved"
                        ):
                            continue
                        seen_ids.add(pid)
                        problems.append({
                            "id": pid,
                            "title": str(obj.get("title") or pid),
                            "prompt": str(obj.get("statement") or ""),
                            "tier": "",
                            "source": f"aporia:{jl.parent.name}/questions.jsonl",
                        })
                except Exception as e:
                    self.log.warning(f"{jl} parse failed: {e}")

        return problems

    def _parse_lens_shelf(self) -> list[str]:
        """Return ordered list of unique lens operator names."""
        shelf: list[str] = []
        seen: set[str] = set()

        text = _safe_read_text(METHODOLOGY_TOOLKIT)
        if text:
            for m in _TOOLKIT_OP_RX.finditer(text):
                name = m.group(1)
                if name not in seen:
                    seen.add(name)
                    shelf.append(name)
            # plain (no-backtick) fallback to catch anything missed
            for m in _TOOLKIT_OP_RX_PLAIN.finditer(text):
                name = m.group(1)
                if name not in seen:
                    seen.add(name)
                    shelf.append(name)

        # disciplinary stances (multi-perspective attack methodology)
        for stance in DISCIPLINARY_STANCES:
            tag = f"STANCE_{stance.upper()}@v1"
            if tag not in seen:
                seen.add(tag)
                shelf.append(tag)

        # additional lens names extracted from catalogs/*.md (if present)
        if CATALOGS_DIR.exists():
            cat_rx = re.compile(r"`([A-Z][A-Z0-9_]*@v\d+)`")
            for cat in sorted(CATALOGS_DIR.glob("*.md")):
                text = _safe_read_text(cat) or ""
                for m in cat_rx.finditer(text):
                    name = m.group(1)
                    if name not in seen:
                        seen.add(name)
                        shelf.append(name)

        return shelf

    def _toolkit_line_for(self, op_name: str, text: Optional[str]) -> int:
        """Return 1-indexed line number where the operator header appears."""
        if not text:
            return 0
        op_name_re = re.escape(op_name)
        rx = re.compile(
            rf"^###\s+\d+\.\s+`?{op_name_re}`?",
            re.MULTILINE,
        )
        m = rx.search(text)
        if not m:
            return 0
        return text.count("\n", 0, m.start()) + 1

    # -- scoring + selection -----------------------------------------------

    def _score_problem(
        self,
        problem: dict,
        history: dict,
        total_lenses: int,
    ) -> tuple[int, str]:
        pid = problem["id"]
        h = history.get(pid, {}) or {}
        applied = h.get("applied_lenses") or []
        last_verdict = h.get("last_verdict")
        bonus = _VERDICT_BONUS.get(last_verdict, _VERDICT_BONUS.get(None, 1))
        deficit = max(0, total_lenses - len(applied))
        return deficit + bonus, (last_verdict or "null")

    def _select_problem(
        self,
        problems: list[dict],
        history: dict,
        shelf_size: int,
    ) -> tuple[Optional[dict], Optional[str]]:
        """Return (chosen_problem, tiebreak_log) or (None, None)."""
        if not problems:
            return None, None

        ranked: list[tuple[int, str, dict]] = []
        for p in problems:
            score, verdict = self._score_problem(p, history, shelf_size)
            ranked.append((score, verdict, p))

        # Higher score wins. Tie -> by verdict precedence
        # (map_of_disagreement > null > coordinate_invariant > durable),
        # then alphabetic id for full determinism.
        verdict_rank = {
            "map_of_disagreement": 0,
            "null": 1,
            "coordinate_invariant": 2,
            "durable": 3,
        }

        def sort_key(item):
            score, verdict, p = item
            return (
                -score,
                verdict_rank.get(verdict, 4),
                str(p.get("id", "")),
            )

        ranked.sort(key=sort_key)
        top_score = ranked[0][0]
        ties = [r for r in ranked if r[0] == top_score]
        chosen = ties[0][2]

        tiebreak = None
        if len(ties) > 1:
            tiebreak = (
                f"score-tie@{top_score} across "
                f"{len(ties)} problems; chose '{chosen['id']}' "
                f"(verdict={ties[0][1]}); next was "
                f"'{ties[1][2]['id']}' (verdict={ties[1][1]})"
            )
            self.log.info(f"tiebreak: {tiebreak}")
        return chosen, tiebreak

    # -- lens-selection heuristic ------------------------------------------

    def _propose_next_lenses(
        self,
        problem: dict,
        shelf: list[str],
        applied: list[str],
        k: int = 3,
    ) -> list[str]:
        """Deterministic next-k lens selection per CHARTER step 4."""
        applied_set = set(applied or [])
        tier_digit = _norm_tier(problem.get("tier"))

        ordered_candidates: list[str] = []

        if tier_digit == "1":
            # Cheapest first
            for lens in TIER1_LENS_ORDER:
                if lens in shelf and lens not in applied_set:
                    ordered_candidates.append(lens)
            # then everything else (toolkit operators + stances + catalog ops)
            for lens in shelf:
                if lens in applied_set:
                    continue
                if lens in ordered_candidates:
                    continue
                ordered_candidates.append(lens)
        else:
            # Tier 2+ (or unknown tier): disciplinary stances first
            for stance in DISCIPLINARY_STANCES:
                tag = f"STANCE_{stance.upper()}@v1"
                if tag in shelf and tag not in applied_set:
                    ordered_candidates.append(tag)
            # then the cheap-first lenses
            for lens in TIER1_LENS_ORDER:
                if lens in shelf and lens not in applied_set:
                    if lens not in ordered_candidates:
                        ordered_candidates.append(lens)
            # then everything else
            for lens in shelf:
                if lens in applied_set:
                    continue
                if lens in ordered_candidates:
                    continue
                ordered_candidates.append(lens)

        return ordered_candidates[:k]

    # -- artifact rendering ------------------------------------------------

    def _render_catalog_draft(
        self,
        problem: dict,
        applied_with_verdict: list[tuple[str, str]],
        proposed: list[str],
        shelf_size: int,
        toolkit_text: Optional[str],
        tiebreak_log: Optional[str],
    ) -> str:
        ts = datetime.now(timezone.utc).isoformat()
        pid = problem["id"]
        title = problem.get("title") or pid
        tier = problem.get("tier") or "(unspecified)"
        source = problem.get("source") or "(unknown)"
        prompt = (problem.get("prompt") or "").strip()

        applied_block_lines = []
        if applied_with_verdict:
            for lens, verdict in applied_with_verdict:
                applied_block_lines.append(
                    f"- `{lens}` -> verdict: `{verdict}`"
                )
        else:
            applied_block_lines.append(
                "_(no lenses recorded as applied yet)_"
            )

        proposed_block_lines = []
        for lens in proposed:
            line_no = self._toolkit_line_for(lens, toolkit_text)
            if line_no:
                cite = (
                    f"`D:\\Prometheus\\harmonia\\memory\\"
                    f"methodology_toolkit.md:{line_no}`"
                )
            elif lens.startswith("STANCE_"):
                cite = (
                    "`D:\\Prometheus\\harmonia\\memory\\"
                    "methodology_multi_perspective_attack.md`"
                )
            else:
                cite = (
                    "`D:\\Prometheus\\harmonia\\memory\\catalogs\\` "
                    "(referenced indirectly)"
                )
            proposed_block_lines.append(
                f"### `{lens}`\n"
                f"- **Citation:** {cite}\n"
                f"- **Spec sketch:** apply `{lens}` to problem `{pid}` "
                f"under the PROBLEM_LENS_CATALOG@v1 schema. Record the "
                f"projected measurement and the predicted "
                f"`map_of_disagreement` vs `coordinate_invariant` vs "
                f"`durable` verdict. Promote into the canonical catalog "
                f"file only after a human/conductor review.\n"
            )

        # Multi-perspective-attack scaffold (stubs)
        mpa_rows = []
        for i, stance in enumerate(DISCIPLINARY_STANCES, start=1):
            mpa_rows.append(
                f"| {i} | {stance.replace('_', ' ')} "
                f"| _(forbidden moves: TBD — see "
                f"methodology_multi_perspective_attack.md)_ "
                f"| _(commitment contract: 1 refutable prediction, "
                f"specific measurement + numerical outcome)_ |"
            )

        # Pythia DR prompt sketch (also used as the actual DR seed body)
        dr_sketch = self._build_dr_prompt(problem, proposed)

        body = f"""# Lens-catalog draft — `{pid}`

- **Problem title:** {title}
- **Problem id:** `{pid}`
- **Tier:** `{tier}`
- **Source:** `{source}`
- **Drafted by:** Argos (Harmonia child, M2) at `{ts}`
- **Catalog symbol:** `PROBLEM_LENS_CATALOG@v1`
- **Total known shelf lenses (this tick):** {shelf_size}

## Problem statement (verbatim from source if available)

{prompt or "_(no statement captured in queue / catalog frontmatter)_"}

## Applied lenses (from state — `D:\\Prometheus\\harmonia\\agents\\argos\\state\\lens_history.json`)

{chr(10).join(applied_block_lines)}

## Proposed next lenses (this tick)

{chr(10).join(proposed_block_lines) if proposed_block_lines else "_(none — shelf exhausted for this problem)_"}

## Multi-perspective-attack scaffold (stub)

Reference: `D:\\Prometheus\\harmonia\\memory\\methodology_multi_perspective_attack.md`.

| # | Disciplinary stance | Forbidden-move constraints (stub) | Commitment contract (stub) |
|---|---|---|---|
{chr(10).join(mpa_rows)}

**Anti-reward-capture brake.** Each thread must end with one refutable
prediction naming a specific measurement and a specific quantitative
outcome. Threads that hedge are re-run with tighter forbidden-move
discipline.

## Tiebreak log

{tiebreak_log or "_(no tie — single highest-scoring problem)_"}

## Next step — Pythia DR prompt sketch (primary-literature lens fingerprint)

```
{dr_sketch}
```

This block is the body Argos would seed via
`pythia_enqueue_dr(...)` (one DR per tick max, gated by Pythia's 20/day
external budget).

---

_File generated by `D:\\Prometheus\\harmonia\\agents\\argos\\daemon.py`.
Argos proposes only — promotion into
`D:\\Prometheus\\harmonia\\memory\\catalogs\\{pid}.md` requires
human/conductor review._
"""
        return body

    def _build_dr_prompt(self, problem: dict, proposed: list[str]) -> str:
        pid = problem["id"]
        title = problem.get("title") or pid
        lens_lines = "\n".join(f"- `{lens}`" for lens in proposed) or "- _(none)_"
        return (
            f"Primary-literature lens fingerprint for open problem "
            f"`{pid}` ({title}).\n\n"
            f"For each of the following candidate lenses, identify the "
            f"two strongest primary-literature attempts (or "
            f"closest-analogue applications) and summarise (a) the "
            f"measurement projected, (b) the verdict reached, (c) the "
            f"axis of disagreement with other lenses applied to the "
            f"same problem.\n\n"
            f"Candidate lenses (Argos proposal, this tick):\n"
            f"{lens_lines}\n\n"
            f"Schema reference: "
            f"`D:\\Prometheus\\harmonia\\memory\\catalogs\\README.md`. "
            f"Multi-perspective methodology: "
            f"`D:\\Prometheus\\harmonia\\memory\\"
            f"methodology_multi_perspective_attack.md`."
        )

    # -- main per-tick entry point -----------------------------------------

    def run_tick(self, dry_run: bool = False) -> dict:
        stats: dict[str, Any] = {
            "problem_id_processed": None,
            "lenses_proposed": [],
            "dr_seeded": False,
            "artifacts_written": 0,
            "errors": 0,
            "backlog_remaining": 0,
            "skipped": False,
        }

        try:
            problems = self._parse_problem_corpus()
        except Exception as e:
            self.log.exception(f"corpus parse failed: {e}")
            stats["errors"] += 1
            problems = []

        try:
            shelf = self._parse_lens_shelf()
        except Exception as e:
            self.log.exception(f"shelf parse failed: {e}")
            stats["errors"] += 1
            shelf = []

        toolkit_text = _safe_read_text(METHODOLOGY_TOOLKIT)
        history: dict = self.load_state("lens_history", default={}) or {}

        if not problems:
            self.log.warning("no problems found in corpus — nothing to do")
            stats["skipped"] = True
            stats["note"] = "empty_corpus"
            self.log_work(
                "argos_tick_complete",
                summary="empty corpus; no lens-catalog draft produced",
                success=True,
            )
            return stats

        if not shelf:
            self.log.warning("lens shelf empty — nothing to propose")
            stats["skipped"] = True
            stats["note"] = "empty_shelf"
            self.log_work(
                "argos_tick_complete",
                summary="empty shelf; no lens-catalog draft produced",
                success=True,
            )
            return stats

        # Check backlog-exhaustion (every problem has every shelf lens
        # applied) -> trigger self-gen path
        backlog_remaining = 0
        for p in problems:
            applied = set(
                (history.get(p["id"]) or {}).get("applied_lenses") or []
            )
            unapplied = [s for s in shelf if s not in applied]
            if unapplied:
                backlog_remaining += 1
        stats["backlog_remaining"] = backlog_remaining

        if backlog_remaining == 0:
            self.log.info(
                "every problem has every shelf lens applied "
                "— firing self_generate_backlog"
            )
            try:
                backlog_items = self.self_generate_backlog()
            except Exception as e:
                self.log.exception(f"self_generate_backlog failed: {e}")
                stats["errors"] += 1
                backlog_items = []
            if backlog_items and not dry_run:
                seed_path = self._write_backlog_artifact(backlog_items)
                if seed_path:
                    stats["artifacts_written"] += 1
                    stats["backlog_artifact"] = str(seed_path)
            stats["note"] = "shelf_exhausted_self_gen"
            self.log_work(
                "argos_tick_complete",
                summary=f"shelf exhausted; emitted {len(backlog_items)} "
                        "self-gen seed proposals",
                success=True,
            )
            return stats

        chosen, tiebreak_log = self._select_problem(
            problems, history, len(shelf)
        )
        if chosen is None:
            stats["skipped"] = True
            stats["note"] = "no_problem_selected"
            self.log_work(
                "argos_tick_complete",
                summary="selector returned no problem",
                success=True,
            )
            return stats

        pid = chosen["id"]
        applied = list(
            (history.get(pid) or {}).get("applied_lenses") or []
        )
        last_verdict = (history.get(pid) or {}).get("last_verdict")
        proposed = self._propose_next_lenses(chosen, shelf, applied, k=3)

        # Pair each applied lens with its known verdict (one verdict per
        # problem in this MVP; we record it next to every lens for now).
        applied_with_verdict = [
            (lens, str(last_verdict) if last_verdict else "null")
            for lens in applied
        ]

        # Render + write catalog draft artifact
        artifact_body = self._render_catalog_draft(
            problem=chosen,
            applied_with_verdict=applied_with_verdict,
            proposed=proposed,
            shelf_size=len(shelf),
            toolkit_text=toolkit_text,
            tiebreak_log=tiebreak_log,
        )

        slug = _slugify(pid)
        ts = _utc_iso()
        artifact_name = f"lens_catalog_{slug}_{ts}.md"
        if not dry_run:
            try:
                artifact_path = self.write_artifact(
                    artifact_name, artifact_body
                )
                stats["artifacts_written"] += 1
                stats["artifact_path"] = str(artifact_path)
            except Exception as e:
                self.log.exception(f"write_artifact failed: {e}")
                stats["errors"] += 1
        else:
            # In dry-run we STILL write the artifact for inspectability
            # (the spec's smoke-test expects it under artifacts/), but
            # we tag the filename so it's distinguishable.
            try:
                artifact_path = self.write_artifact(
                    f"dryrun_{artifact_name}", artifact_body
                )
                stats["artifacts_written"] += 1
                stats["artifact_path"] = str(artifact_path)
            except Exception as e:
                self.log.exception(f"write_artifact (dry) failed: {e}")
                stats["errors"] += 1

        # Optional Pythia DR seed — gated by a self-imposed daily cap so
        # Argos doesn't saturate Pythia's 20-30/day budget. The cap is
        # advisory; raise via state file `dr_daily_cap.json` if intentional.
        dr_seeded_state: list = self.load_state("dr_seeded", default=[]) or []
        today = datetime.now(timezone.utc).date().isoformat()
        seeded_today = sum(
            1 for e in dr_seeded_state
            if str(e.get("ts", ""))[:10] == today
        )
        dr_cap = int(self.load_state("dr_daily_cap", default=3) or 3)
        dr_quota_remaining = max(0, dr_cap - seeded_today)
        stats["dr_seeded_today"] = seeded_today
        stats["dr_quota_remaining"] = dr_quota_remaining
        if (not dry_run) and proposed and dr_quota_remaining > 0:
            try:
                dr_title = f"Argos lens fingerprint: {chosen.get('title') or pid}"
                dr_prompt = self._build_dr_prompt(chosen, proposed)
                row_id = self.pythia_enqueue_dr(
                    title=dr_title[:200],
                    prompt=dr_prompt,
                    priority=5,
                    tier="T5",
                    tags={
                        "source": "harmonia_agent:argos",
                        "problem_id": pid,
                        "lenses": proposed,
                    },
                )
                if row_id is not None:
                    stats["dr_seeded"] = True
                    dr_seeded_state.append({
                        "problem_id": pid,
                        "queue_row_id": row_id,
                        "ts": datetime.now(timezone.utc).isoformat(),
                    })
                    self.save_state("dr_seeded", dr_seeded_state)
            except Exception as e:
                self.log.warning(f"pythia_enqueue_dr path failed: {e}")
                stats["errors"] += 1

        # Update lens_history (always — even in dry_run we want
        # progress; per spec step 7 "don't propose them again next
        # tick"). But to preserve smoke-test reproducibility we only
        # persist when not dry_run.
        if not dry_run:
            new_applied = list(applied)
            for lens in proposed:
                if lens not in new_applied:
                    new_applied.append(lens)
            history.setdefault(pid, {})
            history[pid]["applied_lenses"] = new_applied
            history[pid].setdefault("last_verdict", last_verdict)
            history[pid]["last_updated"] = datetime.now(
                timezone.utc
            ).isoformat()
            self.save_state("lens_history", history)

        stats["problem_id_processed"] = pid
        stats["lenses_proposed"] = proposed
        stats["items_processed"] = 1

        self.log_work(
            "argos_tick_complete",
            summary=(
                f"problem={pid} proposed={proposed} "
                f"dr_seeded={stats['dr_seeded']} "
                f"artifacts={stats['artifacts_written']}"
            ),
            output_path=stats.get("artifact_path"),
            success=stats["errors"] == 0,
        )
        return stats

    # -- backlog self-generation -------------------------------------------

    def self_generate_backlog(self) -> list[dict]:
        """Fires only when every known problem has every known lens
        applied. Uses DeepSeek to propose 5 fresh open problems from an
        undercovered subfield with primary-source pointers."""
        prompt = (
            "We have applied every lens in our methodology shelf to every "
            "open problem currently catalogued in the Prometheus project "
            "(see D:\\Prometheus\\harmonia\\memory\\catalogs\\ for the "
            "anchor catalogs Lehmer / Collatz / P vs NP and "
            "D:\\Prometheus\\aporia\\ for the queue). Propose FIVE new "
            "genuinely-open mathematical problems from a SUBFIELD WE ARE "
            "UNDER-COVERING (avoid: number theory, dynamical systems, "
            "computational complexity if they dominate the existing "
            "catalogs). For each, give: id (slug), title, one-sentence "
            "statement, the disciplinary frame, and ONE primary-source "
            "pointer (paper or canonical reference). Format as a "
            "markdown list. Be specific."
        )
        ds_out = self.deepseek_complete(
            prompt=prompt,
            system=(
                "You are Argos, the PROBLEM_LENS_CATALOG@v1 expander. "
                "Propose-only; never claim a problem is closed."
            ),
            max_tokens=900,
            temperature=0.4,
        )
        if not ds_out:
            return []
        return [{
            "kind": "pending_problem_seed_batch",
            "source": "deepseek",
            "body": ds_out,
            "ts": datetime.now(timezone.utc).isoformat(),
        }]

    def _write_backlog_artifact(
        self, backlog_items: list[dict]
    ) -> Optional[Path]:
        if not backlog_items:
            return None
        ts = _utc_iso()
        lines = [
            "# Pending problem seeds (Argos self-gen)",
            "",
            f"Generated at `{datetime.now(timezone.utc).isoformat()}` "
            "by `D:\\Prometheus\\harmonia\\agents\\argos\\daemon.py`.",
            "",
            "_Propose-only. The conductor / a human triages these into "
            "`D:\\Prometheus\\aporia\\docs\\gemini_research_queue\\queue.jsonl`._",
            "",
        ]
        for i, item in enumerate(backlog_items, start=1):
            lines.append(f"## Batch {i} — source: `{item.get('source')}`")
            lines.append("")
            lines.append(item.get("body", "_(empty)_"))
            lines.append("")
        try:
            return self.write_artifact(
                f"pending_problem_seeds_{ts}.md",
                "\n".join(lines),
            )
        except Exception as e:
            self.log.warning(f"backlog artifact write failed: {e}")
            return None
