# Icarus -- experimental self-improving reasoning-ladder climber

**Status:** Phase 0 scaffold (2026-05-25). Experimental, not foundational. Expect breakage.

## What this is

Icarus is an agent that runs continuously in a 5-step loop, attempting on every iteration to improve its own reasoner code to climb the Prometheus Reasoning Ladder (R0 → R12 per `D:\Prometheus\pivot\reasoning_ladder_v01_2026-05-24.md`).

Each cycle:
1. Clones the last STABLE cycle's frozen snapshot into `cycles/cycle_<N>/code/`.
2. Calls `improve.propose_diff()` to ask "what should I change to pass the next-tier falsification test?"
3. (Phase 1+) Ingests Pythia DR, OSS code, Hephaestus Forge primitives.
4. Runs TDD + adversarial probe battery.
5. (Phase 1+) Emits frontier-review request, scans inbox.
6. Freezes the cycle and decides: mark_stable (advance pointer) or park (forensic record).

**Failed cycles are NEVER deleted** -- they're the forensic record of every attempt.

## Architecture (3-backend Improve)

Per `D:\Prometheus\pivot\icarus_design_v02_2026-05-25.md`:

- **Backend 1 (primary):** Claude API (synchronous, in-cycle). Daily token cap default 200k.
- **Backend 2 (fallback):** Chimera mode -- asynchronous human-in-the-loop. Icarus writes an `improve_request_<N>.md` to `chimera_outbox/`; James routes it to Claude (Harmonia in a conversation); response goes to `chimera_inbox/`; next cycle ingests.
- **Backend 3 (menial):** Local Qwen2.5-Coder via Ollama (stubbed in Phase 0). Only for test stubs, docstrings, syntax checks.

## Co-evolving Falsifier sub-agent

Per spec v0.2 Shift 2. Runs AFTER TDD passes, BEFORE freeze. Uses a DIFFERENT model than Icarus's Improve() backend (Gemini when Icarus uses Claude; Claude when Icarus uses Chimera). Generates fresh-seed adversarial probes per cycle. Failures park the cycle.

## Wisdom module

Per spec v0.2 Shift 3. Post-hoc DAG-mined failure-pattern extractor. Every 25 cycles, scans parked cycles and produces `wisdom/wisdom.md` (anti-patterns, recurring diagnoses) that gets prepended to the next Improve() prompt.

## Phase 0 status

What's wired:
- 5-step loop daemon (`daemon.py`)
- Immutable-lineage mechanism (`lineage.py`)
- 3-backend Improve() function (`improve.py`)
- FROZEN R0-R12 ladder definitions (`ladder.py`)
- Falsifier sub-agent (`falsifier.py`)
- TDD runner (`tdd_runner.py`)
- Complexity tracker (`complexity.py`)
- Wisdom module (`wisdom.py`)
- 8-probe adversarial battery (`adversarial.py`)
- R0/R1 falsification tests (`cycles/cycle_000/code/tests/`)
- Bootstrap reasoner targeting R1 (`cycles/cycle_000/code/reasoner.py`)

What's stubbed for Phase 0:
- DR / OSS / Forge consumers (return empty)
- Falsifier probe execution (returns inconclusive)
- Adversarial probes (all return passed=True until reasoner exists)
- Qwen Ollama backend (returns stubbed no-op)

## How to run

```powershell
# Single cycle
python D:\Prometheus\agents\icarus\daemon.py --once

# Continuous loop (90s tick)
python D:\Prometheus\agents\icarus\daemon.py --loop --interval 90

# Status
python D:\Prometheus\agents\icarus\daemon.py --status

# Pause (write the file)
echo "" > D:\Prometheus\agents\icarus\state\pause.flag

# Resume
echo "" > D:\Prometheus\agents\icarus\state\resume.flag

# Hard kill
echo "" > D:\Prometheus\agents\icarus\state\kill.flag
```

## File layout

```
agents/icarus/
├── daemon.py                  # main loop entry-point
├── lineage.py                 # clone/freeze/revert utilities
├── improve.py                 # 3-backend Improve()
├── falsifier.py               # co-evolving Falsifier sub-agent
├── ladder.py                  # FROZEN tier definitions
├── adversarial.py             # 8-probe battery
├── tdd_runner.py              # pytest harness
├── complexity.py              # capability-per-LOC + branching factor
├── wisdom.py                  # DAG-mined post-hoc analyzer
├── cycles/
│   ├── cycle_000/            # bootstrap (tracked in git)
│   │   ├── code/             # MUTABLE -- this is what Icarus improves
│   │   │   ├── reasoner.py
│   │   │   ├── strategy.py
│   │   │   ├── tests/
│   │   │   │   ├── test_tier_R0_falsification.py
│   │   │   │   ├── test_tier_R1_falsification.py
│   │   │   │   ├── test_tier_R2_falsification.py
│   │   │   │   ├── generated/        # MUTABLE -- Icarus-written tests
│   │   │   │   └── frontier_supplied/  # MUTABLE -- James-routed frontier tests
│   │   ├── parent.json
│   │   ├── outcome.json
│   │   └── meta.json
│   └── cycle_<N>/            # auto-generated; gitignored after 000
├── state/                    # mostly gitignored runtime state
├── chimera_outbox/          # Icarus -> James
├── chimera_inbox/           # James -> Icarus
├── frontier_outbox/         # Icarus -> frontier-model curation by James
├── frontier_inbox/          # James -> Icarus (frontier responses)
└── wisdom/                   # auto-generated DAG-mined patterns
```

## Design history

- v0.1: `D:\Prometheus\pivot\icarus_design_v01_2026-05-25.md`
- v0.2: `D:\Prometheus\pivot\icarus_design_v02_2026-05-25.md` (post-review delta with Chimera architecture + Falsifier + Wisdom)
- Frontier review prompt: `D:\Prometheus\pivot\icarus_frontier_review_prompt_2026-05-25.md`
