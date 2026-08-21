# Techne Substrate Fire Log — 2026-08-21

## Session: suite verification after the numeric-redaction contract change + a flake filed

**Context.** Returning from the Mark-detour (propulsion workbench, separate repo on D:,
shipped through `99ac434` there). A stale background task from 08-18 was killed by the
harness; verified zero impact — its work had landed via the foreground path.

## 1. Assembler verified under the 2026-08-19 contract change (E3)

Ergon's numeric-redaction pass (`NUMERIC_REDACTION_PLACEHOLDER`, `leaks_numeric_answer`)
altered the redaction contract my assembler tests pin: the ANSWER-tag pass now consumes
"Final answer: True" as tag+token, and standalone small integers are redacted as a count
channel ("gcd is 1" loses its "1" — accepted over-stripping, shrink-only for D0/D1 Δ).
My tests were updated by that commit's author to match. Re-ran the full probe suite:
**152/152 green**, assembler and redaction tests included. The redactor/scorer parity
guard (`A._VERDICT_TOKEN is extract._VERDICT_TOKEN`) still holds — the drift-proofing
survived the contract change, which is what it was for.

## 2. Flake filed, not chased (cross-lane observation)

First full-suite run: 2 failures in `ergon/probe/tests/test_r3_controls.py`
(`test_wall_substrate_check_real_corpus`, `test_calibration_suite_is_green`).
Did NOT reproduce: 21/21 in isolation, 152/152 on full-suite re-run. Pattern is
order/state-dependence, not a code defect. That file is Harmonia B's R3-controls lane,
currently hot (TIER-A-EXIT-FAIL → cures in flight, `d5472165`). Filed here so the owner
has the pointer if it recurs during Tier-A exit; not mine to chase.

## 3. Where Techne resumes

Per James (this session): resume the perpetual-arsenal mandate — scan for new open-source
libraries (synthetic reasoning / mathematics / tensor software), build against
`prometheus_math`, and set up a multi-day scanning/building loop. Scan artifact:
`techne/ARSENAL_SCAN_2026-08-21.md` (this session). Roadmap remains
`techne/ARSENAL_ROADMAP.md`.

*— Techne, M1, 2026-08-21.*
