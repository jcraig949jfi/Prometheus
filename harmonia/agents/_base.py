"""
HarmoniaAgent base class — shared scaffolding for the five children
(Phylax, Sophia, Iris, Argos, Telos).

Responsibilities of this base class:
- Heartbeat + log_work helpers (session_telemetry)
- DeepSeek + LLM cascade access (keys.py + apollo deepseek_client)
- Pythia DR enqueue convenience (agora_persist)
- Redis stream tail helpers (agora)
- Graceful degradation when Postgres / Redis / API keys absent

Subclasses must implement:
- run_tick(dry_run) -> dict     # one unit of work
- self_generate_backlog() -> list[dict]  # backlog source when nothing inbound

MVP scope: minimum lovable. Real work, real backlog generation,
no production-rigor on retry/quota/audit yet (those compound as the
swarm matures).
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_THIS_FILE = Path(__file__).resolve()
REPO_ROOT = _THIS_FILE.parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
HARMONIA_DIR = REPO_ROOT / "harmonia"
AGENTS_DIR = HARMONIA_DIR / "agents"

for p in (str(REPO_ROOT), str(SCRIPTS_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Env defaults so subprocesses inherit consistent Redis target
os.environ.setdefault("AGORA_REDIS_HOST", "192.168.1.176")
os.environ.setdefault("AGORA_REDIS_PORT", "6379")
os.environ.setdefault("AGORA_REDIS_PASSWORD", "prometheus")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# -- soft imports -----------------------------------------------------------

try:
    import agora_persist  # type: ignore
    HAS_PG = True
except Exception:
    agora_persist = None  # type: ignore
    HAS_PG = False

try:
    import session_telemetry  # type: ignore
    HAS_TELEMETRY = True
except Exception:
    session_telemetry = None  # type: ignore
    HAS_TELEMETRY = False

try:
    from keys import get_key  # type: ignore
    HAS_KEYS = True
except Exception:
    get_key = None  # type: ignore
    HAS_KEYS = False

try:
    import redis as _redis  # type: ignore
    HAS_REDIS = True
except Exception:
    _redis = None  # type: ignore
    HAS_REDIS = False


# -- DeepSeek client (lazy, shared) -----------------------------------------

_DEEPSEEK = None


def _deepseek_client():
    global _DEEPSEEK
    if _DEEPSEEK is not None:
        return _DEEPSEEK
    if not HAS_KEYS:
        return None
    try:
        from openai import OpenAI  # DeepSeek uses OpenAI-compatible API
        api_key = get_key("DEEPSEEK")
        _DEEPSEEK = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        return _DEEPSEEK
    except Exception:
        return None


# -- Redis client (lazy, shared) --------------------------------------------

_REDIS = None


def _redis_client():
    global _REDIS
    if _REDIS is not None:
        return _REDIS
    if not HAS_REDIS:
        return None
    try:
        _REDIS = _redis.Redis(
            host=os.environ.get("AGORA_REDIS_HOST", "192.168.1.176"),
            port=int(os.environ.get("AGORA_REDIS_PORT", 6379)),
            db=int(os.environ.get("AGORA_REDIS_DB", 0)),
            password=os.environ.get("AGORA_REDIS_PASSWORD", "prometheus"),
            decode_responses=True,
            socket_timeout=5,
        )
        _REDIS.ping()
        return _REDIS
    except Exception:
        _REDIS = None
        return None


# -- HarmoniaAgent ----------------------------------------------------------

class HarmoniaAgent(ABC):
    """Base class for the five Harmonia children.

    Each subclass overrides `name`, `role`, `run_tick`, and
    `self_generate_backlog`. Subclasses get heartbeat + log_work +
    DeepSeek / Pythia / Redis helpers for free.
    """

    name: str = "BaseHarmoniaAgent"
    role: str = "abstract harmonia agent (override)"
    machine: str = "M2"
    operator: str = "Harmonia"

    def __init__(self):
        self.log = logging.getLogger(self.name.lower())
        if not self.log.handlers:
            h = logging.StreamHandler(sys.stdout)
            h.setFormatter(logging.Formatter(
                f"%(asctime)s [{self.name.upper()}] %(message)s"
            ))
            self.log.addHandler(h)
            self.log.setLevel(logging.INFO)
        self.state_dir = AGENTS_DIR / self.name.lower() / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir = AGENTS_DIR / self.name.lower() / "artifacts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self._tick_started_at: Optional[datetime] = None
        self._cycle_id: Optional[str] = None

    # ---- abstract surface -------------------------------------------------

    @abstractmethod
    def run_tick(self, dry_run: bool = False) -> dict:
        """One unit of work.

        Returns a stats dict. The standard keys (none mandatory but
        useful for the rotation logger) are:
            {"items_processed": int, "backlog_remaining": int,
             "artifacts_written": int, "errors": int, "skipped": bool}
        """
        raise NotImplementedError

    @abstractmethod
    def self_generate_backlog(self) -> list[dict]:
        """Return zero or more new work items to enqueue.

        Called by run_tick when the inbound queue is empty. Each work
        item is an opaque dict the subclass understands. Subclasses
        decide their own backlog source — file-scan, combinatorial,
        DeepSeek-prompted, Pythia-DR-overflow, etc.
        """
        raise NotImplementedError

    # ---- heartbeat + log_work --------------------------------------------

    def heartbeat(self, status: dict, kind: str = "tool") -> None:
        """Update session_telemetry so Aletheia's dashboard sees us."""
        if not HAS_TELEMETRY:
            return
        try:
            session_telemetry.register_session(
                name=self.name,
                machine=self.machine,
                role=self.role,
                kind=kind,
                operator=self.operator,
                status_json=status,
            )
        except Exception as e:
            self.log.warning(f"heartbeat failed: {e}")

    def log_work(
        self,
        stage: str,
        summary: str,
        output_path: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
        cycle_id: Optional[str] = None,
        started_at: Optional[datetime] = None,
    ) -> None:
        if not HAS_TELEMETRY:
            return
        try:
            session_telemetry.log_work(
                stage=stage,
                agent=self.name,
                summary=summary[:1000],
                output_path=output_path,
                success=success,
                error=(error or "")[:500] if error else None,
                cycle_id=cycle_id or self._cycle_id,
                started_at=started_at or self._tick_started_at,
            )
        except Exception as e:
            self.log.warning(f"log_work failed: {e}")

    # ---- LLM helpers ------------------------------------------------------

    def deepseek_complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: str = "deepseek-chat",
        max_tokens: int = 600,
        temperature: float = 0.6,
    ) -> Optional[str]:
        """Synchronous DeepSeek chat completion. Returns None on any failure."""
        client = _deepseek_client()
        if client is None:
            return None
        try:
            msgs = []
            if system:
                msgs.append({"role": "system", "content": system})
            msgs.append({"role": "user", "content": prompt})
            resp = client.chat.completions.create(
                model=model, messages=msgs,
                max_tokens=max_tokens, temperature=temperature,
                timeout=120,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            self.log.warning(f"deepseek_complete failed: {e}")
            return None

    def pythia_enqueue_dr(
        self,
        title: str,
        prompt: str,
        priority: int = 5,
        tier: Optional[str] = "T5",
        tags: Optional[dict] = None,
    ) -> Optional[int]:
        """Enqueue a Gemini Deep Research request through Pythia's queue.

        Pythia (60s daemon) will dispatch within its 20/day budget and
        commit the report. Returns the row id or None.
        """
        if not HAS_PG:
            return None
        try:
            return agora_persist.enqueue_research(
                title=title,
                prompt_text=prompt,
                requested_by=self.name,
                priority=priority,
                tier=tier,
                tags=tags or {"source": f"harmonia_agent:{self.name.lower()}"},
            )
        except Exception as e:
            self.log.warning(f"pythia_enqueue_dr failed: {e}")
            return None

    # ---- Redis helpers ----------------------------------------------------

    def redis(self):
        return _redis_client()

    def tail_stream(self, stream_key: str, last_id: str = "$", count: int = 50) -> list[tuple]:
        """XREAD a Redis stream (one-shot, no blocking). Returns list of
        (message_id, fields) tuples in chronological order."""
        r = self.redis()
        if r is None:
            return []
        try:
            res = r.xrevrange(stream_key, count=count)
            return list(reversed(res))
        except Exception as e:
            self.log.warning(f"tail_stream({stream_key}) failed: {e}")
            return []

    # ---- state persistence -----------------------------------------------

    def load_state(self, key: str, default: Any = None) -> Any:
        path = self.state_dir / f"{key}.json"
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default

    def save_state(self, key: str, value: Any) -> None:
        path = self.state_dir / f"{key}.json"
        try:
            path.write_text(json.dumps(value, indent=2, default=str),
                            encoding="utf-8")
        except Exception as e:
            self.log.warning(f"save_state({key}) failed: {e}")

    def write_artifact(self, filename: str, content: str) -> Path:
        path = self.artifacts_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    # ---- tick wrapper -----------------------------------------------------

    def tick(self, dry_run: bool = False) -> dict:
        """Public entry-point — wraps run_tick with telemetry bookkeeping."""
        self._cycle_id = str(uuid.uuid4())
        self._tick_started_at = datetime.now(timezone.utc)
        t0 = time.time()
        try:
            stats = self.run_tick(dry_run=dry_run) or {}
        except Exception as e:
            self.log.exception(f"run_tick failed: {e}")
            stats = {"errors": 1, "exception": str(e)[:300]}
        elapsed = time.time() - t0
        stats["elapsed_sec"] = round(elapsed, 2)
        stats["tick_id"] = self._cycle_id
        # Heartbeat snapshot
        self.heartbeat({
            "last_tick_at": datetime.now(timezone.utc).isoformat(),
            "last_tick_stats": stats,
            "last_tick_dry_run": dry_run,
        })
        return stats


# -- convenience for the rotation orchestrator -----------------------------

def get_agent(name: str) -> HarmoniaAgent:
    """Import + instantiate one of the five children by lowercase name."""
    name = name.lower()
    if name == "phylax":
        from harmonia.agents.phylax.daemon import PhylaxAgent
        return PhylaxAgent()
    if name == "sophia":
        from harmonia.agents.sophia.daemon import SophiaAgent
        return SophiaAgent()
    if name == "iris":
        from harmonia.agents.iris.daemon import IrisAgent
        return IrisAgent()
    if name == "argos":
        from harmonia.agents.argos.daemon import ArgosAgent
        return ArgosAgent()
    if name == "telos":
        from harmonia.agents.telos.daemon import TelosAgent
        return TelosAgent()
    raise ValueError(f"unknown harmonia agent: {name}")
