"""The frozen reasoner. RESTORED 2026-08-23 after the working-tree loss.

One model, one decoding config, one pinned serving provider, for every LLM arm.
The model is never fine-tuned and never carries a conversation across a round
boundary — a "fresh instance" is literally a new message list.
"""
from __future__ import annotations

import json
import re
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]


def _load_env() -> Dict[str, str]:
    env: Dict[str, str] = {}
    for rel in (".env", "agents/eos/.env"):
        p = ROOT / rel
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


@dataclass
class ModelConfig:
    model: str = "meta-llama/llama-3.3-70b-instruct"
    provider: str = "deepinfra"          # pinned; no fallbacks
    temperature: float = 0.0
    top_p: float = 1.0
    max_tokens: int = 900
    seed: int = 12345
    endpoint: str = "https://openrouter.ai/api/v1/chat/completions"
    key_env: str = "OPENROUTER_API_KEY"
    timeout: int = 180
    retries: int = 3


@dataclass
class Usage:
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0.0
    errors: int = 0

    def as_dict(self) -> Dict:
        return dict(self.__dict__)


class FrozenModel:
    """Stateless caller. Every `call` is an independent conversation."""

    def __init__(self, cfg: Optional[ModelConfig] = None,
                 transcript_path: Optional[Path] = None):
        self.cfg = cfg or ModelConfig()
        self.key = _load_env().get(self.cfg.key_env)
        if not self.key:
            raise RuntimeError(f"{self.cfg.key_env} not found")
        self.usage = Usage()
        self.transcript_path = transcript_path
        self.served_by: Optional[str] = None
        self.served_model: Optional[str] = None

    def call(self, system: str, user: str, tag: str = "") -> str:
        body = {
            "model": self.cfg.model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "temperature": self.cfg.temperature,
            "top_p": self.cfg.top_p,
            "max_tokens": self.cfg.max_tokens,
            "seed": self.cfg.seed,
        }
        if "openrouter" in self.cfg.endpoint:
            # pin the serving provider: "frozen" means one model on one server
            body["provider"] = {"order": [self.cfg.provider],
                                "allow_fallbacks": False}
        data = json.dumps(body).encode()
        last = ""
        for attempt in range(self.cfg.retries):
            req = urllib.request.Request(
                self.cfg.endpoint, data=data,
                headers={"Authorization": f"Bearer {self.key}",
                         "Content-Type": "application/json",
                         "User-Agent": "python-urllib/3.12"})
            try:
                with urllib.request.urlopen(req, timeout=self.cfg.timeout) as r:
                    resp = json.load(r)
                text = resp["choices"][0]["message"]["content"] or ""
                u = resp.get("usage") or {}
                self.usage.calls += 1
                self.usage.prompt_tokens += int(u.get("prompt_tokens", 0))
                self.usage.completion_tokens += int(u.get("completion_tokens", 0))
                self.usage.cost += float(u.get("cost", 0.0))
                self.served_by = resp.get("provider")
                self.served_model = resp.get("model")
                self._log(tag, system, user, text, u)
                return text
            except Exception as exc:                     # noqa: BLE001
                last = f"{type(exc).__name__}: {exc}"
                time.sleep(min(60, 5 * (attempt + 1) ** 2))
        self.usage.errors += 1
        self._log(tag, system, user, f"<<ERROR {last}>>", {})
        return ""

    def _log(self, tag, system, user, out, usage) -> None:
        if self.transcript_path is None:
            return
        # iteration 9 lesson: emission runs logged COUNTS but not claim CONTENT,
        # and only the raw transcript made the relevance analysis possible.
        # Always persist the full exchange.
        with self.transcript_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"tag": tag, "system": system, "user": user,
                                 "output": out, "usage": usage}) + "\n")


class ScriptedModel:
    """Offline stand-in for the test suite. No network."""

    def __init__(self, replies: List[str]):
        self.replies = list(replies)
        self.usage = Usage()
        self.cfg = ModelConfig(model="scripted", provider="none")
        self.served_by = self.served_model = "scripted"
        self.seen: List[Tuple[str, str]] = []

    def call(self, system: str, user: str, tag: str = "") -> str:
        self.seen.append((system, user))
        self.usage.calls += 1
        return self.replies.pop(0) if self.replies else "{}"


# --------------------------------------------------------------------------
#  Tolerant JSON extraction — a malformed reply is a wasted turn, not a crash
# --------------------------------------------------------------------------

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def extract_json(text: str) -> Optional[dict]:
    if not text:
        return None
    for cand in _candidates(text):
        try:
            obj = json.loads(cand)
        except Exception:                                # noqa: BLE001
            continue
        if isinstance(obj, dict):
            return obj
        if isinstance(obj, list):
            return {"_list": obj}
    return None


def _candidates(text: str):
    for m in _FENCE.finditer(text):
        yield m.group(1).strip()
    depth, start = 0, None
    for i, ch in enumerate(text):
        if ch in "{[":
            if depth == 0:
                start = i
            depth += 1
        elif ch in "}]":
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    yield text[start:i + 1]
    yield text.strip()
