# Testing the BIND/EVAL MVP

Six layers, all runnable today except where flagged. Pick whichever
matches what you want to verify.

## Layer 1 — Pytest (the discipline contracts)

Two test modules, 27 tests, ≥2 in every math-tdd category. SQLite-only
(in-memory; no DB setup needed).

```bash
python -m pytest sigma_kernel/test_bind_eval.py prometheus_math/tests/test_sigma_env.py -q
```

Expected: `27 passed`. What this proves:

- `BIND` mints a binding-symbol; `EVAL` produces a fresh evaluation-
  symbol whose provenance includes the binding's callable_hash.
- Hash drift (someone edits the bound source after BIND) raises
  `EvalError` at the next EVAL — content addressing works.
- Capability tokens are linear: re-presenting a consumed cap to BIND
  raises `CapabilityError` whether or not the in-process flag was
  flipped (the `consumed=1` row in the DB enforces it across processes).
- Budget enforcement: a sleep payload exceeding `max_seconds` raises
  `BudgetExceeded`.
- Gym env: random-action agent runs to completion, gets non-degenerate
  reward, substrate grows by exactly 1 evaluation per `step()`.

## Layer 2 — Smoke demos (the eyeballable walkthroughs)

```bash
# Six-scenario kernel walkthrough.
python sigma_kernel/demo_bind_eval.py

# Random-agent over the Lehmer-Mahler RL env (default 30 steps).
python -m prometheus_math.demo_sigma_env --steps 25 --seed 7
```

Expected output for `demo_bind_eval.py`:

```
3. EVAL on Lehmer's polynomial (expect M ~ 1.17628)
   eval ref     = eval_bind_mahler_measure_2183b3cb@v1
   output       = 1.1762808182599187
   actual_cost  = {'elapsed_seconds': 0.000254, 'memory_mb': 0.0, 'oracle_calls': 0}

5. Hash drift: mutate binding's stored hash; EVAL must fail
   EvalError raised as expected: callable hash drift: stored=XXX live=55c4...

6. Budget enforcement: tight cost_model + slow callable
   BudgetExceeded raised as expected: max_seconds=0.05: actual=0.200
```

If `output` is not `1.1762808182599187`, the BIND/EVAL chain has a
correctness bug. If step 5 doesn't raise, content-addressing is broken.
If step 6 doesn't raise, budget enforcement is dead.

## Layer 3 — Performance benchmarks (the perf claims)

```bash
python sigma_kernel/bench_bind_eval.py
```

Sample output on the local dev machine:

```
[1] BIND overhead (n=200)
  bind p50:         0.270 ms
  bind p95:         0.322 ms
  claim <50ms:    PASS  (passes by ~185x)

[2] EVAL overhead per call (n=200)
  eval p50:         0.381 ms
  raw call p50:     0.043 ms
  overhead p50:     0.338 ms
  claim <50ms:    PASS  (passes by ~130x)

[3] Substrate growth (n=200 evals)
  rows-per-EVAL:       3.01
  claim <5/eval:       PASS

[4] Cost-model accuracy (5 bootstrapped ops)
  no overshoots:       PASS
```

What this proves vs the stoa proposal's falsification paths:

| Claim | Status |
|---|---|
| BIND adds < 50ms per call vs raw dispatch | PASS (~0.3ms overhead) |
| EVAL adds < 50ms per call vs raw callable | PASS (~0.3ms overhead) |
| Substrate growth < 5 rows per EVAL | PASS (3 rows: 1 symbol + 1 eval + 1 cap) |
| Cost-model accuracy within 2x | **CAVEAT** — declared models are 100-1000x too generous. Falsification path #2 in the stoa proposal calls this out; tightening is one-line per op in `arsenal_meta._bootstrap_registry`. No overshoots in this run, but a real RL agent that picks slow ops will hit `BudgetExceeded` only after the model is tightened. |

## Layer 4 — Live Postgres acceptance (gated on Mnemosyne)

Skipped silently if `~/.prometheus/db.toml` isn't configured or the
`sigma_proto` schema isn't provisioned.

```bash
# 1. Ask Mnemosyne to provision the proto schema:
psql -h <host> -U <admin> -d prometheus_fire \
     -v schema=sigma_proto \
     -f sigma_kernel/migrations/002_create_bind_eval_tables.sql

# 2. Then run:
python -m pytest sigma_kernel/test_bind_eval_postgres.py -v
```

Five tests cover:
- BIND/EVAL round-trip against live Postgres
- RESOLVE the freshly-written EVAL symbol via content hash
- Double-spend rejection (cross-process linearity check)
- Budget enforcement
- Substrate state observable via raw `SELECT COUNT(*) FROM
  sigma_proto.evaluations`

Each test cleans up its own rows (tagged with PID + timestamp). Re-runs
are idempotent; the schema is left in place for inspection.

## Layer 5 — Adversarial probes (hand-driven)

For when you want to poke the discipline directly. Run these in a
Python REPL after `from sigma_kernel.bind_eval import *` etc.

| Probe | Expected |
|---|---|
| BIND with `cap=None` | `CapabilityError("BIND requires a capability")` |
| BIND with `callable_ref="not.a.real.module:fn"` | `BindingError("cannot import module ...")` |
| BIND with `callable_ref="builtins:print"` (no source) | succeeds; callable_hash is `_sha256(repr(fn))` |
| EVAL with a cap that was already used in BIND | `CapabilityError("capability ... already spent")` |
| EVAL with `args=[None]` to a fn expecting an int | `Evaluation(success=False, error_repr="TypeError: ...")` (does NOT raise) |
| `UPDATE bindings SET callable_hash='X'*64`; EVAL again | `EvalError("callable hash drift: ...")` |
| BIND a fast op with `CostModel(max_seconds=0)` | next EVAL raises `BudgetExceeded` (any non-zero elapsed > 0) |
| Double-`commit()` after a BIND | no-op; idempotent |

Each of these is also encoded as a pytest case in `test_bind_eval.py`
under "Edge tests".

## Layer 6 — Learning-curve test (next milestone, not yet shipped)

The acceptance criterion from the pivot doc §4.4 — does a *learning*
agent beat random over the env? Not implemented in the MVP; the random
baseline is in place. To run it once shipped:

```bash
# Future:
python -m prometheus_math.demo_sigma_env_ppo --steps 50000 --seed 0
```

Should produce: a learning curve showing PPO mean-reward strictly above
random-action mean-reward by step ~10K. If it doesn't, the env's reward
signal is too noisy or too sparse and needs reshaping.

This is what would let Harmonia close the language-vs-runtime question
empirically (Test 5 in `2026-04-29-sigma-kernel-as-symbolic-language.md`).

## What each test layer is and isn't deciding

| Layer | Decides... | Doesn't decide... |
|---|---|---|
| 1 (pytest) | Discipline contracts hold | Whether the runtime is fast enough |
| 2 (demos) | End-to-end wiring works | Whether outputs are mathematically meaningful |
| 3 (bench) | Perf claims hold under load | Whether cost models are calibrated correctly |
| 4 (Postgres) | Live substrate path works | Whether multi-process linearity actually races correctly |
| 5 (adversarial) | Discipline rejects malformed inputs | Whether real attackers find paths we missed |
| 6 (learning) | The reward signal is learnable | Whether the agent discovers anything novel |

## Quickstart for a reviewer

```bash
# Two commands, ~15 seconds total. If either fails, the MVP isn't shippable.
python -m pytest sigma_kernel/test_bind_eval.py prometheus_math/tests/test_sigma_env.py -q
python sigma_kernel/bench_bind_eval.py
```

If both PASS, the MVP earns its claim that BIND/EVAL is the load-bearing
primitive for the next eight weeks of pivot work.
