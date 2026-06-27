# Harmonia A — The Measurement Fleet

**Author:** Harmonia_M2_A · **Date:** 2026-06-27 · **Directive:** James — "do all of these."

**The repoint:** Harmonia A's scientist swarm (`harmonia/agents/`: argos / iris /
phylax / sophia / telos) is moved off *claim generation* — the vein that collapsed
Sophia 137→0 (consumer-drift monoculture) — onto **measurement**. Under the v3
reframing (Prometheus = TDD layer / progress meter), the whole program is bottlenecked
on a trustworthy, non-gameable "are we closer?" instrument, and Harmonia owns the only
one. The fleet's new job is to *be the instrument panel*, not to mine more laws. This
is the North Star (compress coordinate systems of legibility) applied to Harmonia
itself.

---

## Track 1 — Grading oracle  ✅ BUILT + CALIBRATED (2026-06-27)

`harmonia/services/grading_oracle.py` — wraps the testable ladder
(`reasoning_phase0`, procedural probes) + the independent verifier (`verifier_lens`,
z3/sympy, fails closed) into "grade any candidate reasoner → tier staircase + failure
shapes." **Non-gameable:** the candidate only supplies an answer; correctness is
decided server-side against ground truth and re-certified by the independent verifier
(157/157 agreement observed). The candidate cannot grade itself.

**Calibration (seed 20260527, all tiers):** a clean capability staircase —

| reasoner | overall | R0 | R1 | R2 | R3 | R6 |
|---|---|---|---|---|---|---|
| template | 8% | 25 | 0 | 0 | 0 | 42 |
| procedural | 34% | 100 | 100 | 2 | 0 | 72 |
| careful | 59% | 100 | 100 | 100 | 100 | 72 |
| falsifier | 62% | 100 | 100 | 100 | 100 | 100 |

Each stronger reasoner climbs in tier-predicted ways; procedural's R2 failure is
specifically `extraneous_root_not_rejected` (the kill shape says *what to fix*).
(R4 absent by design; R5/R7/R8 uncovered by the baselines — open slice.)

**How any agent uses it:**
```python
from harmonia.services.grading_oracle import grade_reasoner
report = grade_reasoner(my_reasoner)                       # callable, local
report = grade_reasoner("agents.hephaestus.src.engines:composed_reasoner")
# cross-machine:  serve() on the reasoner's host; request_grade(ref) from anywhere
```
**This directly powers the Hephaestus organism loop** (its STATUS.md priority #1):
grade the composed engine each cycle → the staircase is "are we there yet," the kill
shapes are "what next," both from a non-gameable oracle.

## Track 2a — Coverage diagnostic sweep  ⏳ IN PROGRESS
Generalize `hypothesis_class_coverage_audit.py` (EC → 25%, B2 ceiling) into a reusable
`harmonia/diagnostics/coverage_diagnostic.py` and run across instruments (a3/knot
miner, Apollo's 27 primitives, Icarus rungs) → typed **B1 (truly exhausted)** vs **B2
(ceiling, fixable by widening the named axis)** verdicts. Operationalizes the doctrine
"no terrain-exhaustion claim without a coverage measure." *(results → `harmonia/diagnostics/COVERAGE_SWEEP_RESULTS.md`)*

## Track 2b — M0, the keystone experiment  ⏳ IN PROGRESS
"Can the selector recognize novelty *outside* its calibration manifold?" Build the
three anti-calibration sets (A: unfamiliar surface form; B: adjacent under-represented
domains; C: synthetic externally-checkable truths) and run the type-II test. This is
*the* experiment that decides whether the 20-year discovery bet is alive or should
fall back to the audit-substrate framing. *(→ `harmonia/experiments/M0_RESULTS.md`)*

---

## Proposed swarm-slice assignment (operator may adjust)

| Agent | Measurement slice |
|---|---|
| **iris** (has a pipeline/daemon) | run the grading-oracle bus daemon (`serve()`); own the request/result protocol |
| **phylax** ("guardian") | verifier hardening + calibration anchors — keep the oracle's core non-gameable; extend `verify` dispatch to R5/R7/R8 kinds |
| **argos** ("all-seeing") | the coverage sweep (track 2a) — one instrument per pass, B1/B2 verdicts |
| **sophia** (died of claim-monoculture) | repurposed to M0 anti-calibration set construction (track 2b) — sourcing novel-shaped truths is the anti-monoculture niche |
| **telos** ("end/purpose") | the rollup — aggregate staircases + coverage + M0 into the standing "closer than yesterday?" trend (the progress-meter itself) |

The fleet's product is a **dashboard, not a claim pile**: for any candidate organism,
the oracle staircase (are we there yet), the coverage verdict (is a null result terrain
or instrument), and the M0 reading (can we even see novelty). That is the
instrument panel the TDD-layer reframing requires.

---

*Track 1 shipped + calibrated this session. 2a/2b in flight via parallel workers; this
doc updates with their verdicts. Harmonia A measures terrain; now it also measures
whether the program's would-be reasoners are getting closer. — 2026-06-27*
