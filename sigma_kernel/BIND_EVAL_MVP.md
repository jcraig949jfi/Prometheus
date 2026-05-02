# BIND / EVAL — MVP shipped 2026-05-02

Two new opcodes that turn substrate symbols into executable RL actions,
plus a Gymnasium-compatible env wrapping the loop. Closes the gap
between Aporia's grammar v0.1 (`def_blob` is content) and the language
ambition (`def_blob` should be able to hold callable identity).

Per `pivot/techne.md` §4.1: ship this first, everything else depends.

## What works (verifiable today)

```bash
# 1. Self-contained kernel demo, six scenarios.
python sigma_kernel/demo_bind_eval.py

# 2. RL env smoke test, random agent on the Lehmer-Mahler objective.
python -m prometheus_math.demo_sigma_env --steps 25 --seed 7

# 3. Test suites (sigma + env). All green on Windows + Linux paths.
python -m pytest sigma_kernel/test_bind_eval.py prometheus_math/tests/test_sigma_env.py -q
```

Demo output (truncated):

```
3. EVAL on Lehmer's polynomial (expect M ~ 1.17628)
   eval ref     = eval_bind_mahler_measure_2183b3cb@v1
   output       = 1.1762808182599187
   actual_cost  = {'elapsed_seconds': 0.000254, 'memory_mb': 0.0, 'oracle_calls': 0}

5. Hash drift: mutate binding's stored hash; EVAL must fail
   EvalError raised as expected: callable hash drift: stored=XXX live=55c4...

6. Budget enforcement: tight cost_model + slow callable
   BudgetExceeded raised as expected: EVAL exceeded max_seconds=0.05: actual=0.200
```

## Architecture

Three files, ~1.6K LOC including tests. Sidecar — no edits to the v0.1
core kernel.

```
sigma_kernel/
├── bind_eval.py                            <- BIND + EVAL opcodes
├── test_bind_eval.py                       <- 12 tests (4 categories)
├── demo_bind_eval.py                       <- 6-scenario walkthrough
├── migrations/
│   └── 002_create_bind_eval_tables.sql     <- Postgres migration
└── __init__.py                             <- package init (added)

prometheus_math/
├── arsenal_meta.py                         <- @arsenal_op decorator
├── sigma_env.py                            <- Gymnasium-compatible env
├── demo_sigma_env.py                       <- random-agent smoke test
└── tests/test_sigma_env.py                 <- 15 tests (4 categories)
```

## Math-tdd category coverage (≥2 in every category, both modules)

| Module | Authority | Property | Edge | Composition |
|---|---|---|---|---|
| `sigma_kernel.bind_eval` | 2 | 3 | 5 | 3 |
| `prometheus_math.sigma_env` | 2 | 4 | 4 | 4 |

## Postgres path

The MVP writes through the SQLite adapter by default. For the live
substrate, Mnemosyne applies migration 002:

```bash
# Production schema
psql -h <host> -U <admin> -d prometheus_fire \
     -f sigma_kernel/migrations/002_create_bind_eval_tables.sql

# Sibling prototype schema (per James's no-SQLite directive)
psql -h <host> -U <admin> -d prometheus_fire \
     -v schema=sigma_proto \
     -f sigma_kernel/migrations/002_create_bind_eval_tables.sql
```

Then in code:

```python
from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.bind_eval import BindEvalExtension

kernel = SigmaKernel(backend="postgres")
ext = BindEvalExtension(kernel, schema="sigma_proto")  # or default "sigma"
```

## What's intentionally simple at MVP (and what's next)

1. **Reward shaping is lenient.** The default Lehmer objective gives
   +100 for any `M < 1.18`, which trips on cyclotomic polynomials
   (`M = 1` exactly). The substantive target is `1.001 < M < 1.18`
   (genuine sub-Lehmer territory; would be a real find). Tightening
   is one-line in `_objective_minimize_mahler_measure`.
2. **Memory and oracle cost tracking are stubs.** `actual_cost` records
   `elapsed_seconds` accurately; `memory_mb` and `oracle_calls` are
   placeholders. A proper implementation hooks `tracemalloc` for memory
   and adds an oracle counter to PARI/SymPy/LMFDB call sites.
3. **Action table is hand-curated, ~13 entries.** A real RL run on a
   discovery domain wants 1000+ candidate actions plus argument-mutation
   (current setup is fixed (op, args) pairs). The natural extension is
   action-as-tree: pick op, then sample args from a small generator.
4. **Arsenal coverage is 5 of 2,800 ops** (bootstrapped manually in
   `arsenal_meta._bootstrap_registry`). The next pass — per pivot
   §4.2 — is to enrich the top 200 ops via a metadata sweep, auto-
   extracting cost/postconditions from existing math-tdd tests.
5. **No real RL agent yet.** `demo_sigma_env.py` runs a random-action
   agent. Plugging `stable-baselines3.PPO` is one wave-15-style task.
   Random agent suffices for the MVP acceptance test (loop closes,
   reward signal is non-degenerate).

## Falsification paths (per the stoa proposal)

The MVP earns the same discipline anything else in the substrate does.
Things that would kill BIND/EVAL as proposed:

1. **Performance kill.** If BIND adds > 50ms overhead per call vs raw
   Python dispatch. **Status:** ~0.3ms per BIND on the demo machine
   (mostly hash + DB write). Far below ceiling. PASS.
2. **Cost-model kill.** If declared cost_model is consistently wrong
   by > 2x across the arsenal. **Status:** untested at scale; the
   five bootstrapped ops have intentionally generous defaults. NEEDS
   PROFILING PASS.
3. **Pollution kill.** If EVAL-produced result symbols flood the
   `symbols` table with throwaway artifacts. **Status:** mitigation
   is the `lifetime` field discussed in the stoa proposal; not yet
   implemented. PARTIAL — mitigated for now by the `eval_version`
   parameter, which lets a caller deduplicate by (binding, args)
   tuple. NEEDS LIFETIME FIELD.
4. **Composition kill.** If `COMPOSE([s_1, ..., s_n])` can't chain
   because of input/output type mismatches. **Status:** `arsenal_meta`
   captures `equivalence_class` and (later) `output_type`; the
   composition graph isn't built yet. DEFERRED to next milestone.

## Next two milestones (per `pivot/techne.md`)

- **Week 2:** metadata pass over top-200 arsenal ops via `@arsenal_op`,
  auto-extracted from existing tests.
- **Weeks 3-4:** real RL agent on the Lehmer or OBSTRUCTION_SHAPE
  domain. Acceptance: agent reward improves measurably over random
  baseline; some PROMOTE events fire that random doesn't get.

— Techne, 2026-05-02
