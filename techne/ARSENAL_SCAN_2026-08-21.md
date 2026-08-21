# Arsenal Scan — 2026-08-21

**Techne, resuming the perpetual-arsenal mandate after the June pause.** Web sweep across
synthetic reasoning, mathematics libraries, and tensor software; findings ranked by leverage
against Prometheus's actual bottlenecks (metabolization probe, tensor-first, verification
depth) — not by novelty. Sources are release trackers and project pages, checked 2026-08-21;
verify versions at install time.

---

## 1. Findings, ranked by leverage

### A. FLINT 3 via `python-flint` — ball arithmetic lands in our lap  🔵→wrap now
FLINT 3 **absorbed Arb, Antic and Calcium**. `python-flint` is already in our Tier-2 READY
list, which means **certified-interval (ball) arithmetic is one wrap away** — no new install.
This is a direct hit on the substrate's epistemic ontology: `precision_dps` fields today
record *how much* precision was requested; Arb-style balls record *what the error actually
is*, certified. Every INCONCLUSIVE-at-resolution-boundary verdict
(`feedback_resolution_dependent_truth`) gets a sharper instrument.
**Action: wrap `prometheus_math.certified` — ball-arithmetic evaluation + a
`certify(fn, dps)` primitive the battery can call. Small, high-value, zero procurement.**

### B. PySR 2.0 (beta, Mar 2026) — a conjecture generator the battery can kill  🟠 install
Symbolic regression with a new **first-class mutation & plugin configuration** API. The fit
with Prometheus is structural, not cosmetic: PySR's mutation operators are configurable,
which means our **operator registry / kill-geometry can shape its search space** — and its
output (closed-form candidate laws over our stored invariant tables) is exactly the artifact
class the falsification battery exists to kill. This is a bulk ore generator in the
`feedback_forge_division` sense, and its candidates are *checkable*, which keeps it out of
AI-to-AI-inflation territory. Caveat: Julia backend — heavier install, needs its own env
check on M1.
**Action: install in a venv, smoke-test on a known law (BSD rank vs analytic data we hold),
then point it at one EC invariant table with the battery as judge.**

### C. Lean 4 + mathlib as a VERDICT LANE (not a prover-model play)  🟠 evaluate
The open-prover wave matured: Goedel-Prover-V2 (32B, ~88% miniF2F), Kimina-Prover-RL
(open training pipeline), DeepSeek-Prover-V2. **We should not run these models** — 32B+ is
far over the local 3–4B VRAM ceiling, and renting them re-enters frontier-dependence. The
arsenal move is smaller and better: install **Lean 4 + mathlib as a checking service**
(the `kimina-lean-server` / LeanDojo pattern) so that *machine-checkable claims become a
verdict class*. The metabolization prereg §2 excluded Lean-checkable claims for lack of a
Lean-side owner; this is that owner's toolchain, pre-built. mathlib is at ~232k theorems —
as a **premise/statement index** it is also a calibration-anchor corpus
(`feedback_calibration_anchors_in_depth`).
**Action: feasibility spike — Lean 4 + mathlib on M1, wrap `check_lean(stmt, proof)` as a
tool. Defer any prover-model integration.**

### D. Tensor stack for Priority-#1 — quimb / tntorch / TensorLy  🔵 partial
Nothing revolutionary shipped; the field consolidated. quimb (1.14.x) remains the best
general TN contractor; **tntorch** gives TT decomposition with autograd; TensorLy is the
stable generic fallback. The relevant consumer is the **signature_index proto-tensor**
(3,311 classes, measured 185K tokens): TT-rank over the signature-keyed occupancy tensor is
Walk-1/Walk-2 of the tensor charter (`feedback_tensor_tooling_charter`), and we already
carry `tt_splice` + the F011-corrected null discipline for it
(`feedback_null_must_perturb_the_statistics_axis`).
**Action: confirm quimb/tntorch import on M1; wrap `prometheus_math.tensor_train` with the
matched-GUE/col-perm null baked into the API so the wrong null is hard to reach.**

### E. Version upgrades, low urgency  🟢 note only
SageMath 10.8 (Dec 2025), PARI/GP 2.17.1, SymPy 1.14. Our cypari pins predate these;
upgrade opportunistically when a wrap needs a new function, not before
(`feedback_infrastructure`: don't over-harden).

## 2. What did NOT make the list, and why
- **Prover models as reasoners** (Goedel/Kimina/DeepSeek-Prover): over VRAM ceiling, and
  "rent a reasoner" inverts the owned-model doctrine (`feedback_frontier_models_window`).
- **Neurosymbolic frameworks** (Dolphin, LINC-style): framework-shaped, not tool-shaped;
  they want to own the loop we already own. Watch, don't adopt.
- **Another program reassessment using the new provers as reviewers**: explicitly out —
  gravity-amplifier (`feedback_llm_convergence_is_gravity_amplifier`).

## 3. Build order (the queue the loop pulls from)
1. `prometheus_math.certified` — FLINT/Arb ball arithmetic wrap (small, unblocks depth).
2. Tensor-train wrap with correct-null API over signature_index (tensor-first).
3. PySR spike: install → smoke on a known law → one real table with battery adjudication.
4. Lean 4 + mathlib feasibility spike → `check_lean` tool.
5. Opportunistic: upgrade pins as wraps demand.

Each item lands as: TDD (math-tdd skill) → tests green → inventory.json + TDD_LOG row →
commit + push → fire-log line. Standing Order #1 holds: wrap, don't rewrite.

*— Techne, 2026-08-21.*
