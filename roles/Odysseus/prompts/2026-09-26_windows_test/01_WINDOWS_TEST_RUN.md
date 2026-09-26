# Windows test run of odysseus/tests (ODYSSEUS-01)

Blocker in one sentence: the brain substrate must work on Windows
(charter R2) and it has only been run on Linux (ubu001).

Procedure, in a worktree at or after the commit that contains odysseus/:

    python --version
    python -c "import platform; print(platform.platform())"
    python -m pytest -q odysseus/tests
    python -m odysseus.brain local --run %TEMP%\ody_win --neurons 2000 --shards 4 --ticks 100 --mode process
    python -m odysseus.brain verify --run %TEMP%\ody_win

If pytest is missing, `python -m pip install pytest` in your usual
environment (the substrate itself is stdlib-only). A Windows Firewall
prompt may appear for python binding UDP on 127.0.0.1; loopback needs
no inbound rule -- if one is needed, record that as a finding, do not
change firewall policy.

Artifact: roles/Odysseus/receipts/2026-09-26_windows_<HOST>.txt with the
five commands' outputs verbatim (pytest tail, verify JSON), the HEAD SHA
and your worktree path. Failures are the product: a failing test output
pasted whole is the most useful possible receipt.

Evidence Odysseus already has (Linux, ubu001, Python 3.14.4): 71 passed;
6-process 4000-neuron 200-tick run under 40% injected loss verifies and
matches the in-process reference on 200/200 ticks.
