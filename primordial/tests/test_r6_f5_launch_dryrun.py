"""F-R6-5 (gate item 20): every contract lane letter dry-launches rc 0 through launch_lane.ps1 -DryRun, which
parses, builds the launch line and exits without a log, env change or process (the D1 class: a letter
missing from ValidateSet broke a real launch). A letter outside LANES fails parameter validation."""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

import pytest

from primordial.core.contract import LANES

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "primordial" / "ops" / "launch_lane.ps1"

pytestmark = pytest.mark.skipif(shutil.which("powershell") is None, reason="powershell not available")


def dry(lane: str, logdir: pathlib.Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
                           "-Lane", lane, "-Worktree", str(ROOT), "-DryRun", "-LogDir", str(logdir), *extra],
                          capture_output=True, text=True, timeout=60)


def last_json(p: subprocess.CompletedProcess) -> dict:
    return json.loads([x for x in p.stdout.splitlines() if x.strip()][-1])


def test_every_lane_letter_dry_launches(tmp_path):
    logdir = tmp_path / "launcher"
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = dict(zip(LANES, ex.map(lambda L: dry(L, logdir), LANES)))
    for L, p in results.items():
        assert p.returncode == 0, (L, p.stdout, p.stderr)
        d = last_json(p)
        assert d["dry_run"] is True and d["lane"] == L and pathlib.Path(d["worktree"]) == ROOT
        assert "claude" in d["exe"].lower() and d["prompt_exists"] is None
    assert not logdir.exists()                                  # no log dir, no launch log


def test_unknown_letter_refused(tmp_path):
    p = dry("Z", tmp_path / "launcher")
    assert p.returncode != 0 and not (tmp_path / "launcher").exists()


def test_boot_prompt_reported(tmp_path):
    logdir = tmp_path / "launcher"
    ok = dry("F", logdir, "-BootPrompt", "-PromptDir", "prompts_bld_r6")
    assert ok.returncode == 0
    d = last_json(ok)
    assert d["prompt_exists"] is True and d["prompt_file"].endswith("F.md")
    assert "prompts_bld_r6/F.md" in d["args"]
    missing = dry("F", logdir, "-BootPrompt", "-PromptDir", "no_such_dir")
    assert missing.returncode == 0 and last_json(missing)["prompt_exists"] is False
    assert not logdir.exists()
