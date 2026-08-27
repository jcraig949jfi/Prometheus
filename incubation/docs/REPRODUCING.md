# Reproducing the Incubation results

Environment: Python 3.11+ (stdlib only for all experiments; pytest for the test
suites). All experiments are single-threaded, deterministic, and seed-fixed: no
wall-clock dependence, no network, no environment variables. Wall times below are
from the recorded runs on Skullport (2026-08-26/27); they scale with CPU but the
numbers in the JSONs do not change.

Windows note: harness files are UTF-8; if editing with scripts, read/write with
explicit `encoding='utf-8'` (a cp1252 round-trip corrupted one file once during
development — repaired, but the failure mode is real).

## v1 — Executable Symbolic Learning

    cd incubation
    python -m pytest tests/ -q          # 20 tests, <1s

    # First Action censuses (each writes results/census_vN.json)
    python experiments/census_v0.py     # ~1s   REJECTS the v0 world design
    python experiments/census_v1.py     # ~8s   REJECTS v1 (acceptance floor)
    python experiments/census_v2.py     # ~5s   PASSES (the production design)

    # The preregistered experiment (5 seeds; ~9-10 min)
    python experiments/incubation_v1.py
    # -> results/incubation_v1.json  (prereg, aggregates, gates, kill conditions,
    #    A-G verdict, anti-cheat, 3,125 per-task rows)
    # -> ledger/entries/c0001.json, c0002.json

Note: census_v0/v1 were written against earlier world/primitive designs; they are
kept as the recorded rejections. Re-running them against the current
`primitives.py`/`worlds/` reproduces *a* rejection but not necessarily the
archived numbers (the archived JSONs are the record of what was rejected and why).
census_v2 and incubation_v1 reproduce exactly against the committed tree.

Expected headline numbers (results/incubation_v1.json):
gate_verdicts all true; ADMIT nodes ratio median 0.1689 CI [0.1643, 0.1705];
TRANSFER 0.1704; NEG_hostile 2.8531; guard OOS by seed [1.0, 0.9975, 1.0, 1.0,
1.0]; wC blind failure rate 0.3013 with 0 failures in wA/wB; verdict
"executable symbolic learning with revision".

## v2 — Operator Genesis

    cd incubation/v2
    python -m pytest tests/ -q          # 15 tests, <1s

    # First Action censuses (each writes results/census_meta_vN.json)
    python experiments/census_meta_v0.py   # ~140s REJECTS (budget leak; dC; dD)
    python experiments/census_meta_v1.py   # ~28s  REJECTS (dE halves too shallow)
    python experiments/census_meta_v2.py   # ~29s  PASSES (pre-first-run design)
    python experiments/census_meta_v3.py   # ~28s  REJECTS dD at 85/8
    python experiments/census_meta_v4.py   # ~28s  PASSES (production design, 85/24)

    # The preregistered experiment (5 seeds; ~7-8 min)
    python experiments/operator_genesis_v1.py
    # -> results/operator_genesis_v1.json (prereg, gates, verdict enum,
    #    anti-cheat, 1,640 rows)
    # -> ledger/o0001.json, o0002.json

Same caveat: census_meta_v0/v1 are archived rejections of earlier designs (their
scripts run against the current domains and will not reproduce the archived
numbers — census_meta_v3 for example now measures the 85/24 trap, not the 85/8 one
it rejected). census_meta_v4 and operator_genesis_v1 reproduce exactly.

Expected headline numbers (results/operator_genesis_v1.json):
gates all true; VERDICT "RECURSIVE_LEARNING_EFFECT"; admit ratio 0.0115; capture
1.0 every seed; dD blind harm 2.2559 with per-seed medians [33.16, 3.16, 1.39,
3.60, 2.16]; router AUDIT_T>0 in 5/5; e_naive 1200 candidates not-found in 5/5;
e_experienced candidate #2 in 5/5, program SEQ(o0001, o0001).

## Verifying integrity independently of the harnesses

- Enumeration pin: `python -c "import sys; sys.path.insert(0,'.');
  from dsl import enumerate_stage, enumeration_sha;
  print(enumeration_sha(enumerate_stage()))"` from incubation/v2 must print
  `c44f6a4f09094537` (the value inside the committed preregistration).
- Any solution word in any results row replays exactly: apply its pids to the
  task start through the domain and compare with the target (the harnesses already
  do this through fresh boundaries; the rows carry the words for v1).
- The observation-boundary claims are testable statically:
  `tests/test_incubation.py::test_static_import_boundary` (v1) and
  `tests/test_v2.py::test_learner_import_boundary` (v2).
