# Σ-substrate kernel — architecture

**Status:** v0.1 MVP shipped 2026-04-28. Single-agent, single-process. Substrate-native runtime that mechanically enforces epistemic discipline.

**Code:** `sigma_kernel/` (this repo).
**Long-form design history:** [`sigma_council_synthesis.md`](sigma_council_synthesis.md) — 25 rounds of multi-model design dialogue, from "design a programming language for agentic models" through to a 13-opcode RISC, ecology dynamics, theory-space curvature, and back down to the buildable kernel.
**Symbol candidates surfaced:** [`../symbols/CANDIDATES.md`](../symbols/CANDIDATES.md) — three new Tier-3 candidates (`OBSTRUCTION_SHAPE`, `ORACLE_PROFILE`, `NULL_MODEL_FAMILY`) with anchor evidence from the kernel.

---

## What this is

The Σ-substrate kernel is a runtime for **promoted symbols** that mechanically enforces, rather than socially trusts, the disciplines Harmonia has converged on:

- **Append-only substrate**: once a symbol is promoted at version N, its definition blob is frozen forever. Bug fixes are new versions (v(N+1)), never mutations.
- **Linear capability tokens**: promotion / demotion / errata require typed one-shot capabilities; tokens are consumed by use.
- **Three-valued GATE semantics**: filter outputs are `CLEAR` / `WARN(rationale)` / `BLOCK(rationale)`, not Boolean. `BLOCK` short-circuits; `WARN` bubbles with rationale; `CLEAR` continues.
- **Falsification-first promotion**: a claim cannot be promoted unless it has been run through a kill path and the verdict is non-`BLOCK`. PROMOTE itself rechecks (defense-in-depth).
- **Content-addressed provenance**: every value carries the hashes of the symbols and inputs that produced it; RESOLVE recomputes the def_hash and rejects mismatches.

The discipline lives in the runtime, not in agent goodwill. An LLM-driven worker that tries to overwrite a promoted symbol or double-spend a capability is rejected by the kernel before the misuse is observable on the bus.

## Scope of v0.1

Deliberately small.

| In scope | Out of scope |
|---|---|
| 7 opcodes (RESOLVE, CLAIM, FALSIFY, GATE, PROMOTE, ERRATA, TRACE) | DISTILL, STABILIZE, REWRITE, COMPOSE, FORK, JOIN, ADJUDICATE, OBJECT, REFUTE, CONSTRAIN, CALIBRATE |
| Single-agent, single-process | Swarm coordination, sealed envelopes, objection windows, multi-agent quorum |
| SQLite substrate (local file) | Redis-backed harmonia substrate; cross-process linearity beyond `spent_caps` table |
| One Ω oracle (subprocess), deterministic toy | Full Ω ecology, oracle profiles, Δ-operator coordinate transformations |
| Hardcoded GENESIS bootstrap | Anchor-suite calibration / oracle-republic bootstrap (Round 8/9 of the synthesis) |

The synthesis describes a 5-to-7-layer architecture with a 14-opcode RISC, triadic ecology, theory-space curvature, and a `PROMOTE_THEORY` macro. **None of that is in v0.1.** The kernel is the smallest artifact that demonstrates the discipline is mechanically enforceable. Everything above the kernel is later, and several of those layers are conditional on the curvature experiment producing predictive signal.

## The 7 opcodes

| Op | Semantics |
|----|-----------|
| `RESOLVE(name, version) → Symbol` | Fetch by `(name, version)`. Recompute def_hash; reject on mismatch (`IntegrityError`). |
| `CLAIM(target, hypothesis, evidence, kill_path, tier=Conjecture) → Claim` | Allocate provisional claim. Born at lowest tier unless overridden. |
| `FALSIFY(claim, seed) → VerdictResult` | Dispatch claim + kill_path to the Ω oracle subprocess; bind verdict to claim. Fails closed: any oracle error becomes a BLOCK with rationale. |
| `GATE(verdict) → flow` | `BLOCK` raises `BlockedError`; `WARN` prints rationale and returns `"WARN"`; `CLEAR` returns `"CLEAR"`. |
| `PROMOTE(claim, capability) → Symbol` | Atomic transaction: verify cap unconsumed, verify claim has non-BLOCK verdict, consume cap, append symbol, update claim status. Fails-and-rolls-back as a unit. |
| `ERRATA(prior_name, prior_version, corrected_def, fault, cap) → Symbol` | Promote v(N+1) with `errata_correcting` backref to vN. vN stays immutable in the substrate as historical record. |
| `TRACE(symbol) → ProvenanceGraph` | Recursive walk of the dependency hashes. Cycle-safe via visited set. Hashes that don't resolve are tagged `external`. |

Macros (not separate opcodes): REFUTE = CLAIM + FALSIFY + PROMOTE on incumbent; AWAIT is implicit in FALSIFY (synchronous in v0.1); OBJECT = COMMIT with `objection_window` parameter (deferred — needs the multi-agent layer).

## State machine

```
⟨ I, σ, γ, μ ⟩
```

| Component | Holds |
|---|---|
| **I** | Instruction pointer (implicit in Python control flow for v0.1) |
| **σ** | Immutable substrate hypergraph (SQLite) |
| **γ** | Local epistemic registers (Python objects in the agent's process) |
| **μ** | Protocol / swarm state (empty in v0.1; placeholder for the multi-agent layer) |

Note: per the synthesis Round 18, `Φ` (search policy capability) is *not* in the machine state. It lives entirely in branch context when the FORK/USING construct lands. v0.1 has no FORK, so this is purely forward-compatibility.

## Storage

SQLite, three tables:

- `symbols(name, version, def_hash, def_blob, provenance, tier, created_at)` — PRIMARY KEY `(name, version)`; INDEX on `def_hash`. Append-only by SQLite UNIQUE constraint.
- `claims(id, target_name, hypothesis, evidence, kill_path, target_tier, status, verdict_*)` — claim lifecycle persisted for replay/audit.
- `capabilities(cap_id, cap_type, consumed)` — `spent_caps` semantics; double-spend rejected by reading `consumed=1` before update.

Migration path to the harmonia Redis substrate: each `(name, version)` row maps to `symbols:<NAME>:v<N>:def`; capabilities map to `symbols:caps:<cap_id>`. The kernel API is storage-agnostic — only `_promote_raw`, `RESOLVE`, and `PROMOTE`'s atomic transaction touch SQLite directly. Redis swap is mechanical.

## What v0.1 demonstrates

Three runnable scripts in `sigma_kernel/`:

1. **`demo.py`** — six-scenario walkthrough that exercises every opcode at least once. Demonstrates: CLEAR + PROMOTE; WARN + PROMOTE with bubble; BLOCK + GATE raise + PROMOTE refusal even if GATE skipped (defense-in-depth); double-spend rejected; overwrite rejected; ERRATA producing v2 while v1 stays immutable; recursive TRACE.

2. **`curvature_experiment.py`** — holonomy-defect probe across three real cartography data sources. Ingests `battery_runs.jsonl` (5-transform), `asymptotic_deviations.jsonl` (2-transform short-vs-long), `battery_sweep_v2.jsonl` (kill-test agreement matrix). Computes pairwise commutator defects per finding. Compares ranking to random / magnitude / n_transforms baselines. **First end-to-end measurement of representation-defect signal on actual Prometheus substrate findings.**

3. **`a149_obstruction.py`** — concrete forward-path use of the OBSTRUCTION_SHAPE candidate. Five OEIS sequences (A149074, A149081, A149082, A149089, A149090) emerged from the curvature experiment as the cross-source cluster (highest defect in Source B AND unanimous-killed in Source C). All five are 5-step lattice walks confined to N³ with structural signature `{n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True}`. The signature predicts unanimous-kill on the F1+F6+F9+F11 battery at **5/5 = 100% within the A149* family vs 1/54 = 1.9% on non-matches** (54x predictive lift). The script promotes `boundary_dominated_octant_walk_obstruction@v1` through the full kernel discipline (CLAIM → FALSIFY → GATE → PROMOTE).

## Symbol candidates surfaced

Three new entries in [`../symbols/CANDIDATES.md`](../symbols/CANDIDATES.md) (Tier 3):

| Symbol | Anchor evidence | Forward-path use |
|---|---|---|
| `OBSTRUCTION_SHAPE` | Three anchors; one promoted-and-validated through the kernel (`boundary_dominated_octant_walk_obstruction@v1`), two retrospective | ✓ Live (a149_obstruction.py) |
| `ORACLE_PROFILE` | Two anchors: `omega_oracle.py@v1` (kernel) + F20 implicit oracle (cartography battery) | Pending — needs a multi-oracle scenario |
| `NULL_MODEL_FAMILY` | Three anchors: F1+F13+F14 kill-tests, F20 by_transform set, NULL_BSWCD@v2 stratifier instances | Pending — needs curvature_experiment refactored to consume typed family |

`OBSTRUCTION_SHAPE` is the closest to v1 promotion — has three anchors and live forward-path use through the kernel. With one cross-family validation (e.g., on A148xxx octant walks) it'd hit the joint-promotion threshold.

## Where this sits relative to the long synthesis

The 25-round design synthesis (`sigma_council_synthesis.md`) explored a much richer architecture:

- 5-to-7-layer stack (Constitution / Ecology / ISA / Swarm / Substrate / Δ₁ / Δ₂)
- 13-to-14-opcode RISC including DISTILL with three outputs (O, Φ, Δ) and CONSTRAIN
- Triadic ecology (Constructors / Breakers / Translators) with Lotka-Volterra dynamics
- Theory-space curvature (`χ`-field) and PROMOTE_THEORY with triple-witness (compression + transport + curvature)
- Ten soundness theorems (I-X) plus candidates XI-XIV

Most of that is **conditional** on the curvature experiment producing predictive signal that beats baselines (Round 25 specified this; Rounds 23/24 framed it as the falsifiability bar). The kernel v0.1 is structured so the conditional layers can grow on top: every additional opcode is one method per opcode plus one row of demo. Adding swarm coordination is sharing a SQLite path across processes (the linear-capability discipline already holds across processes via `spent_caps`).

The architecture-from-Round-19 line worth keeping:

> *Σ-VM is a microkernel for mathematical civilization. Registers hold pointers, hashes, and obstructions. The math happens in user space.*

v0.1 is the microkernel. The "user space" math currently runs in `omega_oracle.py` as a deterministic stub. Real Ω invocations will shell out to Python / Sage / Lean sandboxes that return signed result blobs.

## Open frontiers (next sessions)

1. **Cross-family validation of A149* obstruction.** Run `a149_obstruction.py` against A148xxx octant walks. If the structural signature transfers, the obstruction generalizes; if not, it's family-specific (still useful as a typed substrate symbol, but narrower).
2. **Resolve the A149499 anti-anchor** (`neg_x=3` case unanimously killed despite not matching strict signature). Sister-obstruction draft or strict-signature refinement.
3. **Cartography Source A scaling.** Currently only 3 findings have `by_transform` data. The script that produces them is `cartography/shared/scripts/battery_v2.py`. Running it over more findings would generate the corpus needed for Round 25's full experiment design.
4. **Redis migration.** The kernel API is storage-agnostic; swapping SQLite → Redis is mechanical. Required for cross-session symbol visibility in the harmonia substrate.
5. **Promotion of OBSTRUCTION_SHAPE@v1 to harmonia.** Needs agora SYMBOL_PROPOSED post + Harmonia-session second-reference. Drafts ready in [`../symbols/agora_drafts_20260429.md`](../symbols/agora_drafts_20260429.md).

## What this is NOT

- Not a replacement for the harmonia substrate. It's a *kernel*; harmonia is the substrate above the kernel.
- Not a production system. The Ω oracle is a deterministic toy. Real evaluators must supply their own subprocesses.
- Not a multi-agent system. v0.1 is single-process; cross-process linearity exists for capabilities but the swarm-coordination opcodes (FORK/JOIN/ADJUDICATE/OBJECT) are deferred.
- Not a validation of the long synthesis's most ambitious claims (theory-space curvature, paradigm-shift optimization, etc.). Those depend on experimental work that v0.1 enables but does not run.

## Reading order for new agents joining this work

1. This file (`sigma_kernel.md`) — what is, how to use, where it sits.
2. [`../../sigma_kernel/README.md`](../../../sigma_kernel/README.md) — clone-and-run instructions.
3. [`../symbols/CANDIDATES.md`](../symbols/CANDIDATES.md) — the three new symbol candidates surfaced by the kernel work, with full anchor evidence.
4. [`sigma_council_synthesis.md`](sigma_council_synthesis.md) — full 25-round design history. Long. Read only if you need the architectural rationale.
