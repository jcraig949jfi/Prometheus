# Aphrodite bounded RSI news monitor (APHRODITE-12)

Currency: 2026-09-18. Owner and accountable seat: Aphrodite. Approved by
the operator 2026-09-18 (prompts/2026-09-18_charter/). Spec:
library/NEWS_MONITOR_SPEC.md. Registry row: roles/base-role/MONITORS.md
(AphroditeNewsWatch).

Purpose (operator): not a general AI-news feed; detect evidence capable of
changing Prometheus's experimental reasoning.

Limits, preserved exactly (monitor.py constants; tests/test_monitor.py):
weekly (Monday 03:00 local, scheduled task AphroditeNewsWatch on harry1);
inspect <= 8; admit <= 3; primary source required; dedupe against the
library; admit only if the item changes a named theory, open question,
experimental precedent, benchmark or active design; non-admitted
candidates expire after 30 days; after 4 consecutive empty runs pause and
report the pause once; resume only on explicit, committed clearance.

How a pass works: run_news_pass.py (from a pinned, detached worktree)
resets a service worktree to origin/main, builds a scratch directory with
a read-only library snapshot, runs one headless Claude pass there that may
only write pass_output.json, validates that output deterministically
(monitor.py), then writes NEWS.md admissions (tagged MONITOR-ADMITTED,
unreviewed until the seat annotates them), candidates.json (with expiry),
passes.jsonl (one record per pass) and state.json, commits those paths,
pushes, and verifies the ancestor. The model proposes; the validator and
the seat decide.

Files: PROMPT.md, monitor.py, run_news_pass.py, register_news_monitor.ps1,
state.json (circuit breaker), candidates.json, passes.jsonl, PARKED.md
(only when parked), tests/.

Freshness (base rule 7): state.json last_pass_at / last_success_at /
last_input_at; passes.jsonl. Productivity (rule 8): items admitted per
pass. Bound (rule 10): 4 consecutive empty passes -> park + one comms
message to Aphrodite. Evidence tier of admissions: LITERATURE (source
words), never this seat's own evidence.
