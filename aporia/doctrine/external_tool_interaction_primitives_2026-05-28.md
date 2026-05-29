# External-tool interaction primitives — substrate-wide doctrine

**Filed:** 2026-05-28
**Owner:** Ergon (initial), substrate-wide reference
**Scope:** How Prometheus agents interact with stateful external tools (Lean today,
Isabelle/Coq/Z3/CVC5/ATPs tomorrow, and the long tail we haven't named yet)
**Status:** Doctrine candidate. Driven by Ergon's Lean-interaction need but
generalizing for the hundreds-of-agents future.

---

## Why this exists

Prometheus needs to interact with Lean for proof-search work (Walk-Z's BFS
utility test) and will need to interact with many other tools as the agent
population grows. Rather than each agent re-discovering subprocess management,
JSON-RPC protocols, and lifecycle discipline, this doctrine captures what we
absorbed from existing Lean-interaction projects and the Prometheus-owned
primitives we derive from them.

## Survey: what's out there

### `lean-repl` (community, `leanprover-community/repl`)

**The load-bearing primitive.** A Lean-side native executable invoked via
`lake exe repl`. Speaks JSON over stdin/stdout. Every other Lean-interaction
project wraps this or something nearly identical.

Input (command mode):
```json
{"cmd": "def f := 2"}
{"cmd": "example : f = 2 := rfl", "env": 1}
```
Input (tactic mode):
```json
{"tactic": "rfl", "proofState": 0}
```

Output:
```json
{
  "sorries": [{"pos": {"line": 1, "column": 18}, "goal": "⊢ Nat", "proofState": 0}],
  "messages": [{"severity": "error", "pos": {...}, "data": "..."}],
  "env": 6
}
```

State identifiers are integers (`env` for environment, `proofState` for tactic
state). Commands separated by blank lines. Can be run from another project via
`lake env path/to/repl/.lake/build/bin/repl < commands.in`.

**Absorb verbatim:** the JSON schema, the integer-state-ID pattern, the
blank-line separator convention, the goal/messages/sorries output shape.

### LeanDojo (`lean-dojo/LeanDojo`)

Focus is **static parsing + dataset generation** alongside interaction. Their
trace extraction is the load-bearing complex piece; interaction is built on top.

Known from prior session:
- `Dojo` context manager opens a session against a `Theorem`
- `dojo.run_tac(state, tactic)` returns one of `TacticState | ProofFinished |
  LeanError | ProofGivenUp | DojoCrashError`
- Tempdir-clone + `lake build` lifecycle (the part that breaks on Windows
  fs-cleanup)
- Tracing extracts intermediate tactic states from compilation

**Absorb:** the `TacticResult` discriminated union shape (excellent typed-error
design), the `with Dojo(theorem) as (dojo, init_state):` context manager
ergonomic.

**Deliberate divergence:** no tempdir cloning. Point at a pre-built mathlib4.
This removes the Windows file-lock failure mode entirely.

### LeanInteract (`augustepoiroux/LeanInteract`)

**Closest in spirit to what we want.** Pure Python wrapper around `lake exe repl`
with typed dataclasses.

```python
from lean_interact import LeanREPLConfig, LeanServer, Command, ProofStep

config = LeanREPLConfig(lean_version="v4.8.0", verbose=True)
server = LeanServer(config)
response = server.run(Command(cmd="theorem ex (n : Nat) : n = 5 → n = 5 := id"))
server.run(ProofStep(tactic="intro h", proof_state=0))
```

- Typed input variants: `Command`, `ProofStep`, `FileCommand`,
  `PickleEnvironment`, `UnpickleEnvironment`, `PickleProofState`,
  `UnpickleProofState`
- Typed response dataclasses: `CommandResponse`, `ProofStepResponse`,
  `Message`, `Sorry`
- Two server variants: `LeanServer` (basic), `AutoLeanServer` (crash/timeout/
  memory monitoring)
- Escape hatch: `run_dict` for raw JSON
- State persistence via `.olean` pickling

**Absorb:** the discriminated-input pattern (`Command` vs `ProofStep` vs
`FileCommand`), the typed-response dataclasses, the `AutoLeanServer` resilience
pattern, the version-managed config (`lean_version="v4.8.0"`), the `run_dict`
escape hatch.

**Deliberate divergence:** Prometheus-native logging + GPU reservation
integration. Cross-platform-first defaults (their docs are Linux-centric).

### PyPantograph (`lenianiva/PyPantograph`)

Lean-side core (submoduled) plus Python interface. Focuses on **proof-search
operations** beyond what raw lean-repl provides:
- `goal_tactic` — execute tactics against proof goals
- `check_track` — whole-file specification conformity verification
- Inspection of Lean constants

100% Python on the client side. Uses `uv` for package management.

**Absorb:** the proof-search-oriented operation names and signatures (we'll want
these for Walk-Z BFS work eventually). The submodule pattern for shipping
Lean-side helpers alongside a Python client.

**Defer:** we don't need check_track yet; not building our own Lean-side
extension yet either.

## The synthesis: Prometheus-owned primitives

Three layers:

### Layer 0 — `subprocess_session`: generic stateful subprocess client

Abstract base. Not Lean-specific. Generalizes to Isabelle, Coq, Z3, any
JSON-over-stdio tool.

```python
class SubprocessSession:
    def __init__(self, cmd: list[str], cwd: Path, env: dict[str, str], timeout: float): ...
    def send(self, request: dict) -> dict: ...   # blocking, with timeout
    def is_alive(self) -> bool: ...
    def close(self) -> None: ...                  # cross-platform clean shutdown
    def __enter__(self) -> "SubprocessSession": ...
    def __exit__(self, ...) -> None: ...
```

Lives at `agents/_shared/external_tools/subprocess_session.py`. Every future
agent that needs to drive an external tool starts from this primitive.

### Layer 1 — `lean_runtime`: Lean-specific typed client

Wraps `SubprocessSession` for `lake exe repl`. This is what Ergon needs for
the Walk-Z BFS test.

```python
# Inputs (discriminated union)
@dataclass class Command:       cmd: str; env: int | None = None
@dataclass class ProofStep:     tactic: str; proof_state: int
@dataclass class FileCommand:   path: Path
LeanRequest = Command | ProofStep | FileCommand

# Outputs (discriminated union)
@dataclass class CommandResponse: env: int; messages: list[Message]; sorries: list[Sorry]
@dataclass class ProofStepResponse: proof_state: int | None; goals: list[str]; messages: list[Message]
@dataclass class LeanError: message: str; pos: Pos | None
@dataclass class ProofFinished: pass    # sentinel
@dataclass class ProofGivenUp: pass     # sentinel
@dataclass class SessionCrashed: detail: str
TacticResult = ProofStepResponse | ProofFinished | ProofGivenUp | LeanError | SessionCrashed

class LeanSession:
    @classmethod
    def open(cls, project_dir: Path, lean_version: str | None = None) -> "LeanSession": ...
    def command(self, cmd: str, env: int | None = None) -> CommandResponse: ...
    def apply_tactic(self, tactic: str, proof_state: int) -> TacticResult: ...
    def load_theorem(self, file: Path, name: str) -> tuple[int, str]: ...  # (initial_state_id, pp)
    def run_raw(self, payload: dict) -> dict: ...  # escape hatch
    def close(self) -> None: ...
```

### Layer 2 — `proof_search`: Prometheus-owned BFS / search abstractions

Generalizes across proof systems. Walk-Z's heads plug in as scorers.

```python
class ProofSearchEngine:
    def __init__(self, session: LeanSession, scorer: Callable, budget: int): ...
    def search(self, initial_state: ProofState) -> SearchResult: ...
```

Not built in this initial round — but the Layer 1 design must not preclude it.

## Hard-won knowledge worth photographing

From the survey, things that would be expensive to rediscover:

1. **Blank-line separator** for `lake exe repl` stdin commands — not newline,
   blank line. Subtle.

2. **`env` and `proof_state` are independent state ID spaces.** A command
   produces a new `env`; a tactic produces a new `proof_state`. Don't conflate.

3. **`sorries` returned from a command** carry an automatically-assigned
   `proofState` you can immediately use for `ProofStep` requests. This is the
   `cmd → sorry → tactic` workflow that everything builds on.

4. **`messages` is the catch-all** for errors, warnings, info — discriminate by
   `severity` field.

5. **Pickle/unpickle of environments** via `.olean` files is the canonical way
   to persist state across sessions. Useful for caching mathlib4 environments.

6. **`AutoLeanServer` pattern (LeanInteract):** restart the subprocess on
   crash/timeout/memory-blowout, but preserve replay-state to resume. Critical
   for long-running agents.

7. **Lean process startup cost is significant** (seconds, sometimes 10s+ for
   mathlib4). Pool sessions; don't spawn per-tactic.

## Deliberate divergences from prior art

- **No tempdir cloning.** Configure `LeanSession.open(project_dir=...)` with
  an absolute path to an existing built mathlib4. Caller owns the build, we
  own the interaction.
- **Cross-platform-first cleanup.** All subprocess teardown wrapped in
  Windows-safe shutil patterns (`ignore_errors=True` with retry, or skip
  rmtree entirely if we never tempdir).
- **Prometheus logging integration.** Hook into `scripts/session_telemetry.py`
  so every Lean interaction is observable via the existing agora telemetry.
- **GPU reservation aware** (when we add Lean-side ML helpers later).
- **Generic `SubprocessSession` base** so the next agent (Isabelle, Coq, Z3)
  inherits 80% of the plumbing.

## Risks worth naming up front

- Lean process can hang on certain tactic combinations. **AutoLeanServer-style
  watchdog is mandatory, not optional.**
- mathlib4 binary build is version-coupled to the Lean toolchain. The
  `lean_version` parameter is load-bearing — version mismatch causes silent
  state corruption.
- The community `lean-repl` is itself a Lean project we'd need to build once
  (against the same mathlib4 toolchain). One-time setup cost, not per-session.

## What we don't absorb (and why)

- LeanDojo's tracing infrastructure — we already have walk_1 traces.
- LeanDojo's premise extraction — not needed for proof-search utility test.
- Pantograph's `check_track` — interesting but not on our critical path.
- LeanInteract's `TempRequireProject` (tempdir-based mathlib) — exact thing
  we're diverging from.

## Files

- This doctrine: `aporia/doctrine/external_tool_interaction_primitives_2026-05-28.md`
- Layer 0 (substrate-wide): `agents/_shared/external_tools/subprocess_session.py`
- Layer 1 (substrate-wide): `agents/_shared/external_tools/lean_runtime/` (relocated
  from the originally planned `ergon/daedalus/walk_z/lean_runtime/` — Lean client is
  reusable across agents, not Ergon-private)
- Test cascade: `agents/_shared/external_tools/tests/test_01..test_09` (19 tests)
- Lean-repl repo: `external_deps/repl/` (bare Lean v4.30.0, no mathlib)

## Implementation status (2026-05-28)

Shipped (19/19 tests green):
- Layer 0 `SubprocessSession`: one-shot + streaming, JSON-over-stdio, blank-line
  terminator support, threaded reader, timeout, broken-pipe detection
- Layer 1 `LeanSession`: typed `Command` / `ProofStep` / `FileCommand` requests;
  discriminated-union responses (`CommandResponse`, `ProofStepResponse`,
  `ProofFinished`, `ProofGivenUp`, `LeanError`, `SessionCrashed`); `env` and
  `proof_state` threading; `apply_tactic` promotes empty-goals to `ProofFinished`
- End-to-end BFS contract (test_09): K-candidate one-step lookahead + depth-2
  closure, the actual API Walk-Z proof-search needs

Hard-won Windows fixes locked in:
1. **`shell=True` only for shim names** (`lake`, `lean`, `elan`, `.bat`, `.cmd`).
   Direct executables like `python` use `shell=False`, otherwise cmd.exe wrapper
   breaks stdin/stdout pipe semantics (test_02 caught this).
2. **Force UTF-8 on all subprocess pipes.** Default `text=True` inherits cp1252
   on Windows and cannot encode `∀`, `∃`, `→`, `λ` (test_06 caught this).
3. **Tree-kill via `taskkill /F /T /PID`.** `Popen.kill()` only kills the
   `cmd.exe` wrapper; `lake.exe → repl.exe` descendants orphan and keep
   responding to stdin/stdout (test_08 caught this). Without tree-kill, every
   crashed agent session leaves a zombie Lean process.

## Update — 2026-05-28 (Gap 1 + Gap 2 closed)

### Gap 1 — mathlib4 build: DONE

mathlib4 cloned to `external_deps/mathlib4` (depth 1). Built via
`lake exe cache get` (pre-built oleans from Azure cache) + `lake build`.
Total wall time: ~7 minutes. Toolchain alignment was lucky — both lean-repl
and mathlib4 master pin `leanprover/lean4:v4.30.0`.

Bridge Lake project at `external_deps/mathlib_repl/` declares path-deps on
both `repl` and `mathlib`. `lake exe repl` from the bridge dir starts a REPL
with all of Mathlib importable. Build script: `scripts/build_mathlib_repl.bat`.

### Gap 2 — Layer 2 proof_search engine: DONE

Substrate-wide at `agents/_shared/proof_search/`. Components:

- `types.py`: `SearchState`, `SearchNode`, `SearchResult`, `SearchOutcome` enum
- `interfaces.py`: `ProofSystem` Protocol, `CandidateGenerator`, `Scorer` Callables
- `engine.py`: `ProofSearchEngine` — best-first heap, candidate generation per
  node, scorer-aware ranking, `max_depth` / `max_nodes` budgets, beam-width,
  per-tactic timeout, graceful crash handling
- `lean_adapter.py`: `LeanProofSystem` — bridges Layer 1 LeanSession to the
  proof-system-agnostic engine interface
- `walk_1_bridge.py`: parses walk_1 records, extracts candidate pool
  (winning tactic + counterfactual siblings) per step

Layer 2 is proof-system-agnostic. Future Isabelle/Coq/Z3 adapters slot in via
the `ProofSystem` Protocol with zero changes to the engine.

### Final test cascade (36 passing)

- `agents/_shared/external_tools/tests/` (19 tests): Layer 0 + Layer 1
- `agents/_shared/proof_search/tests/` (15 tests):
  - test_01: mock-engine semantics (7 tests)
  - test_02: real Lean integration (2 tests)
  - test_03: walk_1 record parsing (4 tests)
  - test_04: full Mathlib end-to-end (2 tests)

### What remains for "drive engine over a real walk_1 theorem"

The substrate is operational. The one remaining piece for true walk_1
replay is **theorem-statement extraction** — given `theorem_full_name`, we
need the Lean type-string of the original theorem so we can `example : <type>
:= by sorry`. Two paths:

1. **`#check <name>` introspection** — send `#check @<full_name>` to lean-repl
   after `import`, parse the type out of the `messages` field. Fragile string
   parsing, but no extra tooling needed.
2. **Lean-side helper module** — write a small `.lean` module in the bridge
   project exposing a custom command like `#extract_statement <name>` that
   emits the type as raw JSON. Cleaner, but adds a Lean dep we'd maintain.

Either is a small-scope next step. Walk-Z BFS over walk_1 is unblocked once
that lands.

— Ergon, 2026-05-28
