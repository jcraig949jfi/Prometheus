# sigma_kernel — Σ-substrate runtime MVP

A minimal substrate kernel that mechanically enforces epistemic discipline:
append-only storage, linear capability tokens, three-valued GATE semantics,
falsification-first promotion, content-addressed provenance.

**Architecture spec:** [`harmonia/memory/architecture/sigma_kernel.md`](../harmonia/memory/architecture/sigma_kernel.md)
**Design history:** [`harmonia/memory/architecture/sigma_council_synthesis.md`](../harmonia/memory/architecture/sigma_council_synthesis.md) (25 rounds)
**Candidate symbols:** [`harmonia/memory/symbols/CANDIDATES.md`](../harmonia/memory/symbols/CANDIDATES.md)

## Layout

```
sigma_kernel/
├── README.md               -- this file
├── sigma_kernel.py         -- 7-opcode kernel (RESOLVE, CLAIM, FALSIFY,
│                              GATE, PROMOTE, ERRATA, TRACE)
├── omega_oracle.py         -- subprocess Ω oracle stub (deterministic;
│                              parses 'mean OP value' hypotheses)
├── demo.py                 -- 6-scenario walkthrough of every opcode
├── curvature_experiment.py -- holonomy-defect probe across 3 cartography
│                              data sources
├── a149_obstruction.py     -- forward-path use of OBSTRUCTION_SHAPE
│                              candidate against the A149* OEIS cluster
└── *.db                    -- per-script SQLite state (gitignored)
```

Zero external dependencies. Standard library only (sqlite3, hashlib, json,
subprocess, dataclasses, enum). Python 3.10+.

## Quick start

```bash
cd sigma_kernel/
python demo.py                  # six-scenario discipline walkthrough
python curvature_experiment.py  # representation-defect signal on real data
python a149_obstruction.py      # promotes the first concrete OBSTRUCTION_SHAPE
```

Each script writes its own SQLite database (`demo_substrate.db`,
`curvature_experiment.db`, `a149_obstruction.db`) and resets it on each run
so output is deterministic.

## What each script demonstrates

### `demo.py` — discipline walkthrough (six scenarios)

Exercises every opcode at least once. Verifies that:

| Scenario | Discipline |
|---|---|
| 1 | CLEAR verdict → PROMOTE succeeds |
| 2 | WARN verdict → PROMOTE proceeds with warning bubbled |
| 3 | BLOCK verdict → GATE raises; PROMOTE refuses even if GATE skipped (defense-in-depth) |
| 4 | Double-spend → second PROMOTE with same cap rejected |
| 5 | Overwrite → both `bootstrap_symbol` and direct SQL INSERT rejected by storage |
| 6 | ERRATA → v2 supersedes v1 with backref; v1 stays immutable |

Plus a recursive TRACE walk of the first promoted symbol's provenance graph.

### `curvature_experiment.py` — three-source holonomy probe

Loads three cartography data sources, computes pairwise commutator defects
between coordinate transforms, ranks findings by curvature density, compares
against baselines.

| Source | File | Δ-shape |
|---|---|---|
| A | `cartography/.../battery_runs.jsonl` | 5-transform F20 (raw / log / rank / z-score / sqrt) |
| B | `cartography/.../asymptotic_deviations.jsonl` | 2-transform (short_rate vs long_rate) |
| C | `cartography/.../battery_sweep_v2.jsonl` | kill-test agreement matrix |

Cross-source signal worth flagging on each run: the top-curvature B
sequences are also the most-killed C sequences.

### `a149_obstruction.py` — first concrete OBSTRUCTION_SHAPE

Investigates the cluster surfaced by the curvature experiment: 5 OEIS
sequences (A149074, A149081, A149082, A149089, A149090) all 5-step lattice
walks confined to N³ with a specific structural signature.

Tests the hypothesis: does the structural signature
`{n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True}` predict unanimous-kill
on the F1+F6+F9+F11 battery better than the family base rate?

Result on the available A149* corpus: **5/5 = 100% match-group kill rate
vs 1/54 = 1.9% non-match-group rate** (54x predictive lift). The script
promotes `boundary_dominated_octant_walk_obstruction@v1` through the full
kernel discipline.

This is the first end-to-end forward-path use of the `OBSTRUCTION_SHAPE`
candidate symbol — see `harmonia/memory/symbols/CANDIDATES.md`.

## What's mechanically enforced

The kernel rejects, at the API boundary, every attempt to violate the
discipline:

- An LLM agent that writes `promote(claim, cap); promote(claim, cap)` — the
  second call raises `CapabilityError` because `spent_caps` table flags
  the cap as consumed (and the in-memory frozen-dataclass copy-on-consume
  prevents reuse within a process before that).
- An agent that tries `bootstrap_symbol("X", 1, ...)` over an existing
  symbol gets `ImmutabilityError` from the SQLite UNIQUE constraint.
- An agent that calls `PROMOTE` on a claim with a BLOCK verdict gets
  `FalsificationError` even if it skipped GATE — defense-in-depth.
- An agent that calls `RESOLVE("X", 1)` on a substrate row whose
  `def_blob`'s sha256 doesn't match the stored `def_hash` gets
  `IntegrityError` — content-address tampering detected.
- An Ω subprocess that crashes, times out, or returns malformed JSON
  produces a BLOCK verdict with the error rationale (fail-closed).

## What's NOT in v0.1 (deliberately)

See [`harmonia/memory/architecture/sigma_kernel.md`](../harmonia/memory/architecture/sigma_kernel.md)
for the full out-of-scope list and rationale. Highlights:

- DISTILL, REWRITE, COMPOSE, STABILIZE — deferred opcodes
- FORK, JOIN, ADJUDICATE, OBJECT — swarm coordination, deferred
- Δ-operators / Layer Δ — speculative; conditional on curvature experiment
- κ-field, χ-field, paradigm shifts, PROMOTE_THEORY — long-design speculative
- GENESIS / CALIBRATE — anchor-suite oracle bootstrap, deferred
- Datalog ALU — hardcoded queries instead, for v0.1
- Tensor-train compression, async dispatch — out
- Multi-agent coordination — out (kernel is single-process)

## Storage and migration path

v0.1 uses local SQLite. Schema is in `sigma_kernel.py:SCHEMA`. Each script
writes its own DB so demos don't collide.

Migration to the harmonia Redis substrate is mechanical: each
`(name, version)` row maps to `symbols:<NAME>:v<N>:def`; capabilities
map to `symbols:caps:<cap_id>`. Only `_promote_raw`, `RESOLVE`, and
`PROMOTE`'s atomic transaction touch SQLite directly.

## Provenance of this work

The kernel is the implementation arm of a 25-round multi-model design
exercise (see `harmonia/memory/architecture/sigma_council_synthesis.md`).
The design exploration produced an ambitious 5-7 layer architecture; this
MVP implements the load-bearing kernel core that survives independent of
whether the more speculative layers (theory-space curvature, paradigm-shift
optimization, etc.) earn empirical support.

## Forward path

1. Cross-family validation of A149* obstruction on A148xxx walks.
2. Resolve A149499 anti-anchor (sister obstruction or signature refinement).
3. Generate more `by_transform` data via `cartography/shared/scripts/battery_v2.py`
   to scale Source A in the curvature experiment.
4. Migrate to Redis storage backend for cross-session symbol visibility.
5. Promote OBSTRUCTION_SHAPE@v1 in the harmonia substrate (agora drafts
   ready in `harmonia/memory/symbols/agora_drafts_20260429.md`).
