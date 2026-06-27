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

## Track 2a — Coverage diagnostic sweep  ✅ DONE (2026-06-27)
`harmonia/diagnostics/coverage_diagnostic.py` (reusable; EC regression reproduces).
Sweep verdicts — and the diagnostic **refuses to force a verdict** where in-class
recall < 1 (no overclaiming):

| instrument | coverage | verdict |
|---|---|---|
| EC void-miner | 12% | **B2_CEILING** — widen the *axis*, not the integer invariants |
| a3 cross-product | 0% | **B1_EXHAUSTED_BY_PROOF** — product-measure theorem; provably dead (the non-list-dependent anchor) |
| Apollo Frame-H | 50% | **MIXED/INCONCLUSIVE** — climb/wiring-limited, not class-limited |
| Icarus R0–R12 | 83% | **MIXED/INCONCLUSIVE** — limited by *climb* (R8–R12 unreached), not expressiveness |

**Partially falsifies the universal-ceiling hypothesis:** the EC ceiling is *not*
universal — three distinct stall mechanisms (narrow-class ceiling / dead-by-proof /
climb-search insufficiency). The one shared math-side widening lever: **admit
real-valued / tolerance relations** (opens EC's BSD/Szpiro axis AND Apollo's
optimization axis at once). `COVERAGE_SWEEP_RESULTS.md`.

## Track 2b — M0, the keystone  ✅ DONE (2026-06-27, re-executed + confirmed)
18 hand-curated TRUE claims (all independently oracle-confirmed true), run through the
real battery. Numbers (E3, reproduced by Harmonia A):

| Set | accept | reject | unknown |
|---|---|---|---|
| A (re-encodings of core facts) | 80% | 0% | 20% |
| B (adjacent domains — the real novelty arm) | **17%** | 0% | 83% |
| C (synthetic checkable) | 71% | 0% | 29% |
| overall (18) | 56% | **0%** | 44% |

**Can the selector see novelty? — Honest verdict: NO (Reading B / demoted).** Two
facts adjudicate it:
1. **0% reject — the battery never certifies a true claim FALSE.** It fails
   *closed/silent* (unknown), not *loud/wrong*. Strict type-II = 0/18. This is its
   trustworthy, defensible property and why the audit fallback (success-state A/C) is
   solid: it will not falsely kill a true discovery — it just can't recognize one yet.
2. **The packaged battery certifies ZERO genuinely-novel-shaped truths on its own.**
   The 4 real out-of-manifold accepts were all *hand-routed* to raw z3
   (`certify_universal`/`entails`), bypassing the `verify()` gate. On the true novelty
   arm (Set B) it is **17% — blind, not discerning.** The thesis's own self-flag — "a
   recognizer of things-that-look-like-existing-truths" — is **empirically confirmed.**

**The crucial nuance (and the way back to alive):** the blocker is
**representational/interface, not epistemic** (Lens 7). B4/B6 are z3-decidable *today*
and fail only because `certify_universal` is wired to one integer variable; A4 fails
only because the conjecture registry is keyed by a literal `cid` string, not meaning.
So discovery (B) is **gated on representational engineering** — widen the primitive
signature, add an identity kind, let `verify()` synthesize predicates — **not** more
crawlers/agents/terrain. Until then, the honest job is audit, and **B should stop being
advertised.** `M0_RESULTS.md`. *(Follow-up: the harness's mechanical 50%-knife-edge
verdict over-credits hand-routed-z3 accepts and mis-prints "Reading A"; phylax slice to
harden the verdict rule to packaged-battery-only reach.)*

---

## The integrated finding (all three tracks)

The grading oracle, the coverage sweep, and M0 converge on **one diagnosis**:
**Prometheus's stall is dominantly REPRESENTATIONAL / INTERFACE, not epistemic, not
terrain, not scale.** The same lever appears at every level —
- *Instrument level (2a):* EC's "0 novel" is a B2 ceiling → widen the relation class
  (real-valued/tolerance).
- *Candidate level (2a):* Apollo/Icarus are climb/wiring-limited, not class-limited.
- *Keystone discovery bet (2b):* the selector can't see novelty because novel shapes
  are *unrepresentable*, though the underlying z3 can often decide them.

**So the program's highest-leverage work is widening the representable-shape inventory**
(real-valued relations, identity kinds, multi-variable predicates, posable primitives,
meaning-keyed registries) — exactly Lens 7 ("suspect the interface before the
reasoning"). This is measurable progress the fleet can now track per cycle: each new
representable shape that lets the battery certify a previously-unknown Set-B truth is a
tick toward "the selector can see novelty," i.e. toward discovery (B) being alive again.

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
