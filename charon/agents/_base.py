"""
CharonAgent base class — thin subclass over HarmoniaAgent that points
state + artifact dirs under `charon/agents/<name>/` and sets the
operator label to "Charon".

Everything else (heartbeat, deepseek_complete, pythia_enqueue_dr,
tail_stream, load_state / save_state, write_artifact, tick wrapper) is
inherited verbatim from `harmonia.agents._base.HarmoniaAgent`. The
shared scaffolding lives there; Charon does not duplicate it.

Subclasses override `name`, `role`, `run_tick(dry_run)`, and
`self_generate_backlog()`. See Harmonia's exemplars at
`harmonia/agents/{phylax,sophia,iris,argos,telos}/daemon.py` for the
contract.

Per `aporia/doctrine/dr_prompt_discipline.md` (2026-05-19): every
swarm member that enqueues Pythia DR should also process its own
`<state_dir>/dr_inbox/` — `_process_dr_inbox()` is the canonical
reader, identical across all five agents. Recent-coverage check
`_recent_dr_coverage()` queries `agora.research_queue` history.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from harmonia.agents._base import HarmoniaAgent, REPO_ROOT

CHARON_AGENTS_DIR = REPO_ROOT / "charon" / "agents"


class CharonAgent(HarmoniaAgent):
    """Charon-swarm base. Repoints state + artifact dirs to
    `charon/agents/<name>/{state,artifacts}/`.
    """

    operator: str = "Charon"
    machine: str = "M2"

    def __init__(self):
        super().__init__()
        self.state_dir = CHARON_AGENTS_DIR / self.name.lower() / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir = CHARON_AGENTS_DIR / self.name.lower() / "artifacts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.dr_inbox_dir = self.state_dir / "dr_inbox"
        self.dr_inbox_dir.mkdir(parents=True, exist_ok=True)
        self.dr_inbox_processed_dir = self.dr_inbox_dir / "processed"
        self.dr_inbox_processed_dir.mkdir(parents=True, exist_ok=True)

    # ---- DR inbox processing ---------------------------------------------

    def _process_dr_inbox(self) -> list[dict]:
        """Scan dr_inbox/ for unprocessed Pythia completion notifications.

        Returns the list of new notification dicts (parsed JSON). After
        the caller routes each finding to its downstream substrate target,
        it should call `_mark_dr_processed(row_id)` to move the file into
        dr_inbox/processed/.

        Per `aporia/doctrine/dr_prompt_discipline.md` §5, the inbox writer
        is `scripts/pythia_notify_requesters.py` on M1; this side is read-
        only. Files arrive as `<row_id>.json` with title, report_path,
        report_github_url, summary, completed_at fields.
        """
        notifications: list[dict] = []
        try:
            for p in sorted(self.dr_inbox_dir.glob("*.json")):
                # Skip the processed subdir
                if p.parent != self.dr_inbox_dir:
                    continue
                try:
                    payload = json.loads(p.read_text(encoding="utf-8"))
                    payload["_inbox_path"] = str(p)
                    notifications.append(payload)
                except Exception as e:
                    self.log.warning(f"dr_inbox parse failed {p.name}: {e}")
        except Exception as e:
            self.log.warning(f"dr_inbox scan failed: {e}")
        return notifications

    def _mark_dr_processed(self, notification: dict) -> Optional[Path]:
        """Move a processed inbox file to dr_inbox/processed/<row_id>.json."""
        src = notification.get("_inbox_path")
        if not src:
            return None
        src_path = Path(src)
        if not src_path.exists():
            return None
        dst = self.dr_inbox_processed_dir / src_path.name
        try:
            shutil.move(str(src_path), str(dst))
            return dst
        except Exception as e:
            self.log.warning(f"dr_inbox move failed {src_path.name}: {e}")
            return None

    # ---- recent-coverage check ------------------------------------------

    def _recent_dr_coverage(self, keywords: list[str], days: int = 7) -> bool:
        """Return True if any DR within the past `days` matches all keywords.

        Per doctrine §3: "If a topic was DR'd within the last 7 days, don't
        re-fire unless an anti-anchor flag specifically demands re-
        verification." Caller decides whether to skip.

        Two-phase check:
        1. Local `dr_seeded` state — every enqueue this agent has made
           lands here with timestamp + target_keywords. Catches pending /
           dispatched / in-progress rows that Postgres-completed-only
           queries miss. This is the dominant case during active ticks.
        2. Postgres `read_recent_completed_research` — catches completed
           rows whose state has been pruned locally OR which were
           enqueued by a different process / a different agent.

        Falls back to False (allow enqueue) on connectivity errors —
        better to burn a duplicate than block all enqueues.
        """
        if not keywords:
            return False
        needles = [k.lower() for k in keywords if k]
        if not needles:
            return False

        # Phase 1: local state (catches pending/in-flight)
        try:
            history = self.load_state("dr_seeded", default=[]) or []
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            for entry in history:
                try:
                    ts = datetime.fromisoformat(str(entry.get("ts", "")).replace("Z", "+00:00"))
                except Exception:
                    continue
                if ts < cutoff:
                    continue
                target_kw = entry.get("target_keywords") or []
                haystack = (" ".join(str(k) for k in target_kw)).lower()
                if all(n in haystack for n in needles):
                    return True
        except Exception as e:
            self.log.warning(f"recent_dr_coverage local-state check failed: {e}")

        # Phase 2: Postgres completed (catches cross-process / cross-agent)
        try:
            import agora_persist  # type: ignore
        except Exception:
            return False
        try:
            recent = agora_persist.read_recent_completed_research(
                hours=days * 24, limit=500
            )
        except Exception as e:
            self.log.warning(f"recent_dr_coverage query failed: {e}")
            return False
        for row in recent or []:
            haystack = " ".join(
                str(row.get(k, "")) for k in ("title", "prompt_text", "tags")
            ).lower()
            if all(n in haystack for n in needles):
                return True
        return False

    # ---- DR cap accounting ----------------------------------------------

    def _dr_quota_state(self) -> tuple[int, int, list[dict]]:
        """Return (seeded_today, dr_cap, dr_seeded_history).

        Inlined identically across the five Charon agents. Mirrors the
        Argos pattern from harmonia/agents/argos/daemon.py:698-705.
        """
        history: list = self.load_state("dr_seeded", default=[]) or []
        today = datetime.now(timezone.utc).date().isoformat()
        seeded_today = sum(
            1 for e in history if str(e.get("ts", ""))[:10] == today
        )
        dr_cap = int(self.load_state("dr_daily_cap", default=3) or 3)
        return seeded_today, dr_cap, history

    def _record_dr_seeded(
        self, history: list[dict], row_id: int, **extras
    ) -> None:
        history.append({
            "queue_row_id": row_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            **extras,
        })
        self.save_state("dr_seeded", history)

    def _dr_enqueue_if_quota(
        self,
        title: str,
        prompt: str,
        recent_coverage_keywords: list[str],
        substrate_type: str,
        tags: Optional[dict] = None,
        priority: int = 5,
        tier: str = "T5",
        recent_coverage_days: int = 7,
    ) -> dict:
        """Cap-aware Pythia enqueue with recent-coverage gating.

        Returns a dict suitable for merging into the per-tick stats:
            {dr_seeded: bool, dr_seeded_today: int, dr_quota_remaining: int,
             dr_skipped_reason: str | None, dr_row_id: int | None}

        Per-agent run_tick should call this once after the main work is
        done, passing a target-specific recent_coverage_keywords list so
        the doctrine §3 "avoid recent coverage" rule kicks in correctly.
        """
        result: dict = {
            "dr_seeded": False,
            "dr_seeded_today": 0,
            "dr_quota_remaining": 0,
            "dr_skipped_reason": None,
            "dr_row_id": None,
        }
        seeded_today, dr_cap, dr_history = self._dr_quota_state()
        result["dr_seeded_today"] = seeded_today
        result["dr_quota_remaining"] = max(0, dr_cap - seeded_today)
        if result["dr_quota_remaining"] <= 0:
            result["dr_skipped_reason"] = "daily_cap_reached"
            return result
        if self._recent_dr_coverage(recent_coverage_keywords, days=recent_coverage_days):
            result["dr_skipped_reason"] = "recent_coverage"
            return result
        merged_tags = {
            "source": f"charon_agent:{self.name.lower()}",
            "substrate_type": substrate_type,
        }
        if tags:
            merged_tags.update(tags)
        try:
            row_id = self.pythia_enqueue_dr(
                title=title[:200],
                prompt=prompt,
                priority=priority,
                tier=tier,
                tags=merged_tags,
            )
        except Exception as e:
            self.log.warning(f"pythia_enqueue_dr failed: {e}")
            result["dr_skipped_reason"] = f"enqueue_error: {e}"
            return result
        if row_id is None:
            result["dr_skipped_reason"] = "enqueue_returned_none"
            return result
        result["dr_seeded"] = True
        result["dr_row_id"] = row_id
        self._record_dr_seeded(
            dr_history,
            row_id,
            substrate_type=substrate_type,
            target_keywords=recent_coverage_keywords,
        )
        return result

    def _emit_dr_discipline_adoption(
        self, daily_cap: int, substrate_types: list[str], builder_ref: str
    ) -> None:
        """Idempotent: post the doctrine-§8 adoption signal exactly once."""
        if self.load_state("dr_discipline_adopted", default=False):
            return
        types_s = ", ".join(substrate_types) or "?"
        self.log_work(
            "dr_prompt_discipline_adopted",
            summary=(
                f"{self.name} wired to Pythia DR pipeline; "
                f"daily cap={daily_cap}; substrate type(s)={types_s}; "
                f"prompt builder at {builder_ref}"
            ),
            success=True,
        )
        self.save_state("dr_discipline_adopted", True)


def get_charon_agent(name: str) -> CharonAgent:
    """Import + instantiate one of the five children by lowercase name."""
    name = name.lower()
    if name == "stygian":
        from charon.agents.stygian.daemon import StygianAgent
        return StygianAgent()
    if name == "lethe":
        from charon.agents.lethe.daemon import LetheAgent
        return LetheAgent()
    if name == "acheron":
        from charon.agents.acheron.daemon import AcheronAgent
        return AcheronAgent()
    if name == "moros":
        from charon.agents.moros.daemon import MorosAgent
        return MorosAgent()
    if name == "hecate":
        from charon.agents.hecate.daemon import HecateAgent
        return HecateAgent()
    if name == "nephele":
        from charon.agents.nephele.daemon import NepheleAgent
        return NepheleAgent()
    if name == "pollux":
        from charon.agents.pollux.daemon import PolluxAgent
        return PolluxAgent()
    if name == "erebos":
        from charon.agents.erebos.daemon import ErebosAgent
        return ErebosAgent()
    raise ValueError(f"unknown charon agent: {name}")
