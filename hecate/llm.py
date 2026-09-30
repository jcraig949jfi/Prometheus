"""Isolated model calls for Hecate's measurement instruments.

Uses the subscription `claude -p` (prometheus_llm's claude_cli route), but
strips the harness so the harness is not part of what is measured: an empty
working directory, no tools, no MCP servers, no settings sources (so no
CLAUDE.md, hooks or memory), no session persistence, dynamic system-prompt
sections excluded, and an explicit system prompt. The model id is pinned per
call and recorded with the prompt's sha256 and the raw output.

Nothing here retries on an unwelcome answer; a failed call is recorded as a
failure with its shape (return code, stderr head, elapsed).
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import time

FLAGS = ["--tools", "", "--strict-mcp-config", "--setting-sources", "",
         "--no-session-persistence", "--exclude-dynamic-system-prompt-sections"]


def sha256(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def call(prompt: str, model: str, system: str, timeout: int = 600) -> dict:
    t0 = time.time()
    rec = {"model": model, "system_sha256": sha256(system),
           "prompt_sha256": sha256(prompt), "flags": FLAGS}
    with tempfile.TemporaryDirectory(prefix="hecate_iso_") as cwd:
        cmd = ["claude", "-p", "--model", model, "--system-prompt", system] + FLAGS
        try:
            p = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                               encoding="utf-8", timeout=timeout, cwd=cwd)
            rec.update(rc=p.returncode, text=(p.stdout or "").strip(),
                       stderr_head=(p.stderr or "")[:500])
        except subprocess.TimeoutExpired:
            rec.update(rc=None, text="", stderr_head=f"timeout {timeout}s")
    rec["elapsed_s"] = round(time.time() - t0, 1)
    rec["ok"] = rec.get("rc") == 0 and bool(rec.get("text"))
    return rec


def extract_json(text: str):
    """First top-level JSON object or array in text, else None."""
    for open_c, close_c in (("{", "}"), ("[", "]")):
        start = text.find(open_c)
        while start != -1:
            depth, instr, esc = 0, False, False
            for i in range(start, len(text)):
                ch = text[i]
                if instr:
                    if esc:
                        esc = False
                    elif ch == "\\":
                        esc = True
                    elif ch == '"':
                        instr = False
                elif ch == '"':
                    instr = True
                elif ch == open_c:
                    depth += 1
                elif ch == close_c:
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[start:i + 1])
                        except json.JSONDecodeError:
                            break
            start = text.find(open_c, start + 1)
    return None
