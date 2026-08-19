"""Solver transport for the Metabolization Probe (prereg §1, R8, R8a, R9).

Raw HTTP against an OpenAI-compatible endpoint. Not a harness session, no tools, no retrieval —
R8 excludes tool-enabled agents as solvers, and this module is deliberately incapable of being
one.

Three settings are preregistered rather than chosen at call time:

  * TIMEOUT 180s + one retry. Measured, not guessed: across 450 soak calls and 354 diurnal
    calls the worst HEALTHY latency was 114.7s (p90 = 7 x p50). A 60s timeout would have
    discarded 1.11% of healthy responses and a 120s one 0.22% — and those discards are not
    random, they track longer packets, so they would land as ARM-CORRELATED MISSING DATA.
  * No sampling parameters. `temperature`/`top_p`/`top_k` are removed on current frontier
    models and 400; determinism comes from pinned config plus the determinism re-run.
  * Every result carries executor identity, host, model, and time (R9).
"""
from __future__ import annotations

import json
import os
import pathlib
import socket
import random
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

ROOT = pathlib.Path(__file__).resolve().parents[2]

NVIDIA_BASE = "https://integrate.api.nvidia.com/v1"
DEEPSEEK_BASE = "https://api.deepseek.com"

#: prereg §1 — verified live, per-model. Entries: (model_id, context, base_url, key_env).
#: HOST/FAMILY PINNING RULE: nvidia:deepseek-v4-flash and deepseek:deepseek-v4-flash are the
#: same FAMILY (never counted as two) on different HOSTS (never compared as the same solver —
#: hosted endpoints do not disclose serving config). A host change is a solver-set change
#: under C2 and re-runs the cold-band check.
#:
#: The deepseek: lane is PAID (James funded $10 on 2026-08-19 after the free lane's per-model
#: quota wall — 397x instant HTTP429 with the same model answering fine via its own vendor).
#: At V4-flash list prices the full decision run costs well under $1.
VERIFIED_SOLVERS = {
    "nvidia:nemotron-super-49b-v1.5": ("nvidia/llama-3.3-nemotron-super-49b-v1.5", 128_000, NVIDIA_BASE, "NVIDIA_API_KEY"),
    "nvidia:nemotron-super-49b-v1": ("nvidia/llama-3.3-nemotron-super-49b-v1", 128_000, NVIDIA_BASE, "NVIDIA_API_KEY"),
    "nvidia:deepseek-v4-flash": ("deepseek-ai/deepseek-v4-flash-0731", 1_000_000, NVIDIA_BASE, "NVIDIA_API_KEY"),
    "nvidia:gpt-oss-120b": ("openai/gpt-oss-120b", 128_000, NVIDIA_BASE, "NVIDIA_API_KEY"),
    "deepseek:deepseek-v4-flash": ("deepseek-chat", 1_000_000, DEEPSEEK_BASE, "DEEPSEEK_API_KEY"),
}

TIMEOUT_S = 180.0
RETRIES = 1

#: 429 gets its own retry policy with backoff. The free tier enforces ~40 RPM (measured
#: 2026-08-13: clean to 40, cliff at 60), and an unpaced thread pool blows straight through it.
RATE_LIMIT_RETRIES = 5
RATE_LIMIT_BACKOFF_S = 4.0

#: Raised 96 -> 512 on 2026-08-16 after the pre-pass caught the cap MEASURING ITSELF: at 96 the
#: leveling run showed cold F0 39%/25%/0%/0% across L0-L3 with parse-failure 43%/52%/100%/100%.
#: That was not task difficulty. DeepSeek reasons before answering, and 96 tokens cut it off
#: mid-Euclidean-algorithm, so no verdict token was ever emitted. At 512 the same item completes
#: in 192 tokens. This mattered beyond leveling: packets make responses longer, so a too-low cap
#: truncates MORE on residue-bearing arms than on F0 — arm-correlated missing data, the exact
#: artifact this probe is built to avoid. Truncation is now a logged per-arm diagnostic
#: (completion_tokens == max_tokens), reported beside parse-failure and timeout.
MAX_TOKENS = 512
EXECUTOR = "ergon"


def _load_env(p: pathlib.Path) -> dict:
    env = {}
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def api_key(key_env: str = "NVIDIA_API_KEY") -> str:
    for src in (os.environ, _load_env(ROOT / "agents" / "eos" / ".env"), _load_env(ROOT / ".env")):
        v = src.get(key_env)
        if v:
            return v
    raise RuntimeError(f"{key_env} not found (env, agents/eos/.env, .env)")


@dataclass
class SolverResult:
    status: str            # ok | timeout | http_error | transport_error
    text: str = ""
    latency_s: float = 0.0
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    error_type: Optional[str] = None
    error: str = ""
    attempts: int = 1
    ts_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))
    host: str = field(default_factory=socket.gethostname)
    executor: str = EXECUTOR


def call(solver: str, prompt: str, *, timeout: float = TIMEOUT_S,
         max_tokens: int = MAX_TOKENS, retries: int = RETRIES) -> SolverResult:
    if solver not in VERIFIED_SOLVERS:
        raise ValueError(f"{solver!r} is not in the verified solver set {sorted(VERIFIED_SOLVERS)}")
    model_id, _ctx, base_url, key_env = VERIFIED_SOLVERS[solver]
    body = json.dumps({"model": model_id,
                       "messages": [{"role": "user", "content": prompt}],
                       "max_tokens": max_tokens}).encode()
    last = None
    rl_attempt = 0
    attempt = 0
    while attempt <= retries:
        attempt += 1
        req = urllib.request.Request(
            f"{base_url}/chat/completions", data=body,
            headers={"Authorization": f"Bearer {api_key(key_env)}",
                     "Content-Type": "application/json"})
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                j = json.loads(r.read().decode("utf-8", "replace"))
            u = j.get("usage") or {}
            txt = (((j.get("choices") or [{}])[0].get("message", {}) or {}).get("content") or "")
            return SolverResult(status="ok", text=txt, latency_s=round(time.monotonic() - t0, 2),
                                prompt_tokens=u.get("prompt_tokens"),
                                completion_tokens=u.get("completion_tokens"),
                                attempts=attempt)
        except Exception as e:  # noqa: BLE001 - transport classification is the point
            dt = round(time.monotonic() - t0, 2)
            et = type(e).__name__
            status = "transport_error"
            if isinstance(e, urllib.error.HTTPError):
                et, status = f"HTTP{e.code}", "http_error"
            elif isinstance(e, (socket.timeout, TimeoutError)) or isinstance(
                    getattr(e, "reason", None), socket.timeout):
                et, status = "TIMEOUT", "timeout"
            last = SolverResult(status=status, latency_s=dt, error_type=et,
                                error=str(e)[:200], attempts=attempt + 1)
            if et == "HTTP429" and rl_attempt < RATE_LIMIT_RETRIES:
                # Back off and do NOT consume a normal retry: a 429 is congestion, not a
                # failed call, and treating it as one is how a run silently loses rows.
                time.sleep(RATE_LIMIT_BACKOFF_S * (2 ** rl_attempt) * (0.5 + random.random()))
                rl_attempt += 1
                attempt -= 1
    return last  # type: ignore[return-value]


def context_window(solver: str) -> int:
    return VERIFIED_SOLVERS[solver][1]


def spend_usd(prompt_tokens: int, completion_tokens: int, solver: str) -> float:
    """List-price accounting for the paid deepseek lane (R11). V4-flash cache-miss rates."""
    if not solver.startswith("deepseek:"):
        return 0.0
    return prompt_tokens / 1e6 * 0.14 + completion_tokens / 1e6 * 0.28


def preflight(solver: str, *, ceiling_tokens: int = 8_000, small_trials: int = 2) -> dict:
    """R8a — MANDATORY before every run. Swap a failing solver BEFORE any arm, never mid-run.

    The catalog drifts (a model that preflighted clean has 410'd out of existence before) and
    the failure is deterministic per model, so it is screenable — which is the whole reason
    this is a gate rather than a hope.
    """
    probe = ("Claim: 391 and 253 are coprime (share no common factor greater than 1).\n"
             "Is this claim true? Answer True or False, then justify in one sentence.")
    filler = ("kill_signature: invariant_equality | margin: 0.0031 | falsifier: F17 | "
              "kill_pattern: asserted-equality-without-executing-computation\n")
    big = "Prior failure residue.\n\n" + filler * max(1, ceiling_tokens // 38) + "\n\n" + probe

    trials = [call(solver, probe) for _ in range(small_trials)] + [call(solver, big)]
    ok = all(t.status == "ok" for t in trials)
    return {
        "solver": solver,
        "model_id": VERIFIED_SOLVERS[solver][0],
        "host": VERIFIED_SOLVERS[solver][2],
        "passed": ok,
        "small_latency_s": [t.latency_s for t in trials[:small_trials]],
        "ceiling_latency_s": trials[-1].latency_s,
        "ceiling_prompt_tokens": trials[-1].prompt_tokens,
        "failures": [t.error_type for t in trials if t.status != "ok"],
        "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "host": socket.gethostname(),
        "executor": EXECUTOR,
    }
