"""O1: scheduled-task launcher. schtasks is faked here; the live dummy self-test is
`python -m primordial.ops.schtask_launch selftest` (run with PM_LIVE_SCHTASKS=1 to include it)."""
from __future__ import annotations

import os
import subprocess
import sys

import pytest

from primordial.ops import schtask_launch as sl

XML = "<Task><Settings><Enabled>{}</Enabled></Settings></Task>"


class FakeSchtasks:
    def __init__(self, fail_run=False, disable_sticks=True):
        self.calls, self.enabled = [], {}
        self.fail_run, self.disable_sticks = fail_run, disable_sticks

    def __call__(self, args, timeout=60):
        self.calls.append(args)
        verb, task = args[1], (args[3] if len(args) > 3 else "")
        rc, out = 0, ""
        if verb == "/Create":
            self.enabled[task] = True
        elif verb == "/Run":
            rc = 1 if self.fail_run else 0
        elif verb == "/Change" and self.disable_sticks:
            self.enabled[task] = False
        elif verb == "/Query" and "/XML" in args:
            if task not in self.enabled:
                rc = 1
            else:
                out = XML.format("true" if self.enabled[task] else "false")
        elif verb == "/Query":
            out = "\n".join(f'"\\{t}","N/A","Ready"' for t in self.enabled)
        return subprocess.CompletedProcess(args, rc, out, "")


def verbs(fake):
    return [c[1] for c in fake.calls]


def test_launch_creates_runs_then_disables_and_verifies(tmp_path):
    fake = FakeSchtasks()
    assert sl.launch("PM_F_x", tmp_path / "x.cmd", run=fake, log=lambda m: None) == 0
    assert verbs(fake) == ["/Create", "/Run", "/Change", "/Query"]
    create = fake.calls[0]
    assert ["/SC", "ONCE"] == create[6:8] and "/IT" in create
    assert fake.calls[2][-1] == "/DISABLE"
    assert fake.enabled["PM_F_x"] is False
    assert sl.audit(run=fake) == []


def test_failed_run_still_disables(tmp_path):
    fake = FakeSchtasks(fail_run=True)
    assert sl.launch("PM_F_y", tmp_path / "y.cmd", run=fake, log=lambda m: None) == 1
    assert "/Change" in verbs(fake) and fake.enabled["PM_F_y"] is False


def test_disable_that_does_not_stick_is_an_error_and_audit_names_it(tmp_path):
    fake = FakeSchtasks(disable_sticks=False)
    msgs = []
    assert sl.launch("PM_F_z", tmp_path / "z.cmd", run=fake, log=msgs.append) == 5
    assert "DISABLE FAILED" in msgs[-1]
    assert sl.audit(run=fake) == ["PM_F_z"]


def test_task_name_prefix_is_required(tmp_path):
    with pytest.raises(ValueError):
        sl.launch("Nestor_F", tmp_path / "n.cmd", run=FakeSchtasks())


def test_cmd_file_is_crlf_ascii_with_paths_intact(tmp_path):
    p = sl.write_cmd(tmp_path / "PM_F.cmd", "F", r"F:\Prometheus-worktrees\nestor-bld-f", name="Nestor F r3",
                     prompt_dir="prompts_bld")
    raw = p.read_bytes()
    assert raw.startswith(b"@echo off\r\n") and raw.endswith(b"\r\n")
    text = raw.decode("ascii")
    assert r'"F:\Prometheus-worktrees\nestor-bld-f"' in text                  # no `\n` corruption
    assert "-BootPrompt -PromptDir prompts_bld" in text and "-NoExit" in text
    assert str(sl.LAUNCH_PS1) in text


def test_missing_task_reads_as_none():
    assert sl.task_enabled("PM_nope", run=FakeSchtasks()) is None


@pytest.mark.skipif(sys.platform != "win32" or os.environ.get("PM_LIVE_SCHTASKS") != "1",
                    reason="live scheduled-task self-test: set PM_LIVE_SCHTASKS=1")
def test_live_selftest():
    assert sl.selftest(log=lambda m: None) == 0


def test_dummy_exe_args_are_one_string(tmp_path):
    # live self-test 18:51: '/c','exit 5' under powershell -File bound as ONE literal -> cmd exited 1
    text = sl.write_cmd(tmp_path / "d.cmd", "F", tmp_path, exe="cmd.exe", exe_args=["/c", "exit 5"]).read_text()
    assert '-ExeArgs "/c exit 5"' in text and "'" not in text
