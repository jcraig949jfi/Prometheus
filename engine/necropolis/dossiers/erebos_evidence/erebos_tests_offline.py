"""erebos_tests_offline.py -- ONE question:

    Do the Erebos unit tests (25 generators, kill_tensor, motifs, routing,
    Sprint-1 A1-A10) and the Stygian composition-loader tests run and pass
    TODAY, offline, at the evidence baseline?

Runs pytest in a subprocess on three scopes and records pass/fail/error
counts and wall time per scope. Network is not disabled by policy here
(no such fixture exists in the tree); the test files were grepped for
requests/urllib/httpx/openai/anthropic/psycopg/redis/socket first (0 hits,
see result json field "network_lib_grep_hits").

Writes erebos_tests_offline_result.json next to this file. Pure ASCII.
Repo root is resolved from __file__ (no drive letters).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

SCOPES = {
    "erebos_tests": ["charon/agents/erebos/tests", "--ignore",
                     "charon/agents/erebos/tests/sprint1"],
    "erebos_sprint1_tests": ["charon/agents/erebos/tests/sprint1"],
    "stygian_composition_tests": sorted(
        str(p.relative_to(REPO)).replace("\\", "/") for p in
        (REPO / "charon/agents/stygian/tests").glob("test_composition_*.py")),
}
NET = re.compile(r"\b(requests|urllib|httpx|openai|anthropic|psycopg|redis|"
                 r"socket)\b")


def grep_net() -> dict:
    hits = {}
    roots = [REPO / "charon/agents/erebos", REPO / "charon/agents/stygian/tests",
             REPO / "charon/agents/stygian/loaders"]
    for r in roots:
        for f in r.rglob("*.py"):
            txt = f.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(txt.splitlines(), 1):
                if line.lstrip().startswith(("import", "from")) and NET.search(line):
                    hits[str(f.relative_to(REPO)).replace("\\", "/") + f":{i}"] = \
                        line.strip()[:120]
    return hits


def run_scope(name: str, args: list[str]) -> dict:
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
           "--no-header", "-rN"] + args
    t0 = time.time()
    try:
        cp = subprocess.run(cmd, cwd=str(REPO), capture_output=True,
                            text=True, timeout=900)
        rc, so, se = cp.returncode, cp.stdout, cp.stderr
    except subprocess.TimeoutExpired as e:
        rc, so, se = -1, (e.stdout or ""), "TIMEOUT 900s"
    if isinstance(so, bytes):
        so = so.decode("utf-8", "replace")
    tail = so.strip().splitlines()[-1] if so.strip() else ""
    counts = {k: int(v) for v, k in re.findall(
        r"(\d+) (passed|failed|error|errors|skipped|xfailed|xpassed|deselected)",
        tail)}
    return {"cmd": " ".join(cmd[2:]), "returncode": rc,
            "elapsed_s": round(time.time() - t0, 1), "summary_line": tail[:300],
            "counts": counts,
            "stderr_tail": se.strip().splitlines()[-3:] if se.strip() else [],
            "failed_tests": re.findall(r"^FAILED (\S+)", so, re.M)[:50],
            "error_tests": re.findall(r"^ERROR (\S+)", so, re.M)[:50]}


def main() -> int:
    out = {"question": __doc__.strip().splitlines()[0],
           "network_lib_grep_hits": grep_net(), "scopes": {}}
    for name, args in SCOPES.items():
        out["scopes"][name] = run_scope(name, args)
        print(name, out["scopes"][name]["summary_line"],
              out["scopes"][name]["elapsed_s"], "s")
    out["test_files_n"] = {
        "erebos_tests": len(list((REPO / "charon/agents/erebos/tests").glob("test_*.py"))),
        "erebos_sprint1_tests": len(list(
            (REPO / "charon/agents/erebos/tests/sprint1").glob("test_*.py"))),
        "stygian_composition_tests": len(SCOPES["stygian_composition_tests"]),
    }
    (HERE / "erebos_tests_offline_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="ascii")
    return 0


if __name__ == "__main__":
    sys.exit(main())
