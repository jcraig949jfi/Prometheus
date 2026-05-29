# Icarus — Frontier Review: Validated R0–R3, and the R5 Wall
### A request for adversarial review and direction. 2026-05-29.

**Who this is for:** a frontier reasoning model (or expert reviewer) with no prior
context on this project. It is written to be self-contained and to be picked
apart. We want disagreement, not encouragement.

**What we are asking, in one line:** we have a self-improving agent that built
its own reasoner from a minimal substrate up to a *dual-falsified* R0–R3 on an
externally-authored, deterministically-graded reasoning ladder — and it has hit
a hard wall at R5 (combinatorial invariant detection). We want your sharpest
read on (a) whether our approach can cross that wall at all, (b) what new probe
generators and failure signatures would sharpen the next push, and (c) what
existing research/tools we should be stealing from — or whether we are now at
the bleeding edge and on our own.

---

## 1. What this is (self-contained)

**Project Prometheus** is an attempt at first-principles, self-discovering
machine reasoning. Its north star: *compress coordinate systems of legibility,
not laws* — build frames in which structure (and capability) becomes
measurable, under a falsification-first discipline (assume every result is false
until every kill path is exhausted).

**Icarus** is one agent in it, deliberately scoped to a narrow question:

> Can a self-improving loop accumulate **typed failure residue** well enough to
> improve its own reasoning substrate **without Goodharting its evaluators**?

Mechanics: Icarus runs a loop. Each *cycle* clones the last stable snapshot of a
mutable `reason(probe) -> (answer, trace)` function, a lens panel proposes a
unified-diff change to it, the diff is applied, and the candidate is graded.
Promotion advances an immutable lineage pointer; failures are *parked* (frozen,
never deleted) as forensic residue. The agent may only edit its own
`reasoner.py` / `strategy.py`; the daemon, lenses, ladder, and verifier are
fixed infrastructure it cannot touch (the mutability boundary that stops it
rewriting its own oversight).

**The ladder it climbs** was authored by a *different* agent (Harmonia_M2_B). It
is a testable reasoning ladder where each tier is defined operationally:
`capability = operation + perturbation + failure_mode + evidence_artifact`. Each
tier has procedurally-generated probes in **four versions** — clean, isomorphic
(same structure, new surface), adversarial (a tempting invalid shortcut), and
transfer (same reasoning, another domain) — so a single clean pass is never
evidence of the tier. Grading is **deterministic and non-LLM**: a verifier lens
(sympy + z3, fails-closed) that *verifies by substitution into the original
problem* rather than re-solving. It cannot be fooled by a remembered answer, and
it returns `valid=None` (no rubber-stamp) for claims it cannot certify.

The generated tiers (and the reasoning move each demands):

| Tier | Operation | The move |
|---|---|---|
| R0 | pattern match surviving isomorphism | solve clean linear AND its renamed/fractional/rewritten variants |
| R1 | local rule + domain legality | quadratics incl. no-real-root cases — do not hallucinate roots |
| R2 | constraint tracking | sqrt(x+a)=x−b: square, then **reject extraneous roots** by checking the original/domain |
| R3 | multi-step composition | rational identity with an excluded value: cancel but **exclude the singularity** |
| R5 | invariant detection | board tiling: decide tileability via a **parity invariant** (color/area) |
| R6 | counterexample search | conjectures: search for counterexamples; don't overgeneralize (n²+n+41) |
| R7 | proof repair | locate the first invalid step in a flawed proof |

(There is no R4 generator — see the questions. The validated range below is
R0–R3; R5 is the next generated rung.)

---

## 2. What we accomplished

**A dual-falsified R0–R3 climb.** From a `template`-level bootstrap (solves clean
linear only, returns None otherwise), Icarus evolved its own reasoner up four
real rungs:

- *Run 1:* R0 (cycle 1), R1 (cycle 2), R2 (cycle 9), R3 (cycle 18).
- *Run 2, fresh probe stream + different LLM sampling:* R0 (1), R1 (2), R2 (4), R3 (12).

Both reached R3. We then tried to break the result two ways and could not:

1. **Artifact robustness.** Score the final reasoner across 15 *fresh* seeds it
   never saw during the climb (~720 verifier-graded probes/tier). Both
   independently-built reasoners: R0–R3 at **mean 1.00, min 1.00, stdev 0.00,
   100% seed-pass-rate**. No seed-overfit. R5/R6/R7 = 0.00.
2. **Process robustness.** The two independent climbs above (different data,
   different sampling) both reached R3 — same endpoint, different trajectory.

So: two reasoners, built by two independent climbs on different data, both hold
R0–R3 across a fresh-seed ensemble, graded by a verifier that checks by
substitution. By our standards this is a genuine, non-Goodharted result.

**The mechanism finding that made it work: failure must emit direction.** R2 was
a *silent 6-cycle plateau*. The Generator's logic was correct in spirit (square,
reject extraneous) but it read the wrong probe field (`data['expr']` when R2
carries `data['a','b','eq']`) → `KeyError` → coarse `tdd_failed`, six times,
because the failure never told the next attempt *why*. We then surfaced (a) the
probe's input schema proactively and (b) the candidate's actual exception to the
next Generator. The next cycle cleared R2. In the re-climb, with this live from
the start, R2 fell in one substantive attempt. R3 repeated the lesson one level
deeper (we had been leaking `probe.ground_truth`, which was both a cheat-vector
and, for R3, *misleading* — the grader wanted a token the ground_truth field did
not contain). The walls were **direction gaps, not capability gaps**.

**Supporting instrumentation** (all deterministic, non-LLM where it matters):
typed failure taxonomy + per-cycle "training object"; a Contract Lens that
catches silent contract breaks by substitution; a Skeptic-debt ledger (a
promote-despite-concern records a debt the next cycle must address); kill-path
clustering; capability defined non-gameably as *held-out frontier advance*.

---

## 3. Where we are: the R5 wall

After R3, the loop auto-advanced to R5 and **stalled in both runs** (cycles
13–22 in run 2, all parks). Two signals matter:

1. **R5/R6/R7 = 0.00 across all robustness seeds**, consistent with Harmonia B's
   own finding that *no* reference reasoner (template/procedural/careful/
   falsifier, all hand-written) passes R5 or R7. The frontier is real, not an
   artifact of our climb.
2. **The R5 park signature is qualitatively different.** R2/R3 parks were
   `tdd_failed` — the reasoner *ran* and answered *wrong*. R5 parks are
   `diff_apply_failed` — the Generator cannot even produce a *valid diff*. It is
   trying to bolt combinatorial parity logic onto an equation-solver and emits
   malformed or oversized patches.

Our reading: R0–R3 are all *algebraic* moves expressible as incremental edits to
a sympy-based solver. R5 is *combinatorial* — checkerboard-color the board, count
black vs white cells, note a domino covers exactly one of each, conclude
untileable if the removed cells unbalance the counts (or if the area is odd).
That is not an incremental edit to an equation solver; it is a different
reasoning structure. The `diff_apply_failed` signature is, we suspect, the
substrate bottleneck showing through: *the representation makes the wrong move
expensive.*

---

## 4. R5 / R7 sketch (our current thinking — tear it apart)

**R5 (invariant detection).** The move decomposes into: (a) recognize the problem
is combinatorial, not algebraic; (b) select an invariant (parity coloring); (c)
compute it over the given board/removed-set; (d) decide. Our candidate unlocks:

- A separate **combinatorial branch** in the reasoner, with invariant primitives
  living in `strategy.py` (coloring, counting, a monovariant skeleton) rather
  than crammed into the algebraic path.
- **Smaller, composed diffs:** a scaffold cycle that adds an empty combinatorial
  branch (small, applies clean), then subsequent cycles fill it. The Generator
  currently tries to do everything in one ≤100-line diff and fails to apply.
- A **Mechanic lens** (pre-apply syntactic validator) to disambiguate
  "diff malformed" from "move too large for one diff" from "can't express it."

**R7 (proof repair).** Locate the first invalid step in a flawed proof. Currently
only 5 hand-written proofs exist; the move is gradeable deterministically (the
ground truth is an integer step index). The hard part is *generating* enough
flawed proofs procedurally to make it a real tier rather than a memorization
target.

---

## 5. Questions for you

### A. Generators — what should we build?

1. **The missing R4.** There is no R4 (strategy selection) generator, so R3→R5
   is a cliff from algebraic to combinatorial with no bridge. Is the R5 wall
   partly an artifact of this missing rung? What would a good R4 *strategy-
   selection* probe look like — a problem solvable two ways where the reasoner
   must pick the structure-appropriate method and justify it — graded
   deterministically?
2. **Within-tier difficulty gradient for R5.** Right now R5 is only parity
   (color/area). Should we add a graded family — parity → mod-3 coloring →
   weighting/potential-function → monovariant — so the climb has footholds
   instead of one cliff? Which of these are deterministically gradeable without
   an LLM judge?
3. **Bridge generators.** Are there problems that are *algebraic but require a
   parity/invariant check* (e.g. Diophantine solvability mod n, coin problems)
   that would connect the substrate Icarus already has to the combinatorial
   reasoning R5 needs?
4. **Procedural R7.** Is there a tractable way to procedurally generate flawed
   proofs with a known first-bad-step — e.g. templated induction proofs with an
   injected base-case gap or an illegal "divide by (a−b)" — that stays
   deterministically gradeable, short of a full proof assistant?

### B. Failure signatures — what should we smoke out to sharpen direction?

5. Our failure classes are still coarse. The R5 `diff_apply_failed` collapses at
   least three distinct things: (i) malformed diff format, (ii) a valid move too
   large for one diff, (iii) the Generator genuinely cannot express the move.
   **What instrumentation would cleanly separate these?** (Our guess: a Mechanic
   lens for (i); diff-size/locality metrics for (ii); but (iii) is the one we
   most need a signal for.)
6. **The B1/B2 question** (degenerate-correct vs weak-search). Is R5 unreachable
   because of the *substrate* (the move can't be expressed as Python+sympy
   reasoner code) or because of *search* (the Generator can't find it)? We can
   hand-write an R5 reference reasoner to prove expressibility; if it's
   expressible, the bottleneck is search, which would *contradict* our
   "substrate is the bottleneck" thesis. Is this the right discriminating test,
   and what else would you run?
7. **Coin-flip Goodhart at R5.** R5's answer is a boolean (tileable). The 4-
   version + held-out design defends against memorization, but does it actually
   defend against a reasoner that *guesses* and rides variance? What additional
   signature (e.g. requiring the reasoner to emit the *named invariant* as the
   evidence artifact, not just the bool) would close this?
8. What failure signatures predict the *next* axis? We suspect R8 (representation
   shift) and R5/R9 are *orthogonal axes*, not ordered rungs (Harmonia B's data
   shows non-monotonic tier behavior near a model's frontier). What residue would
   reveal whether we are climbing a ladder or covering a basis?

### C. The tough questions

9. **Is LLM-diff-on-Python fundamentally capable of R5+, or is it structurally
   stuck at incremental algebraic edits?** The `diff_apply_failed` signature is
   our main evidence that it is stuck. Does crossing R5 *require* a representation
   change (a typed operator graph / DSL the agent manipulates as data) before it
   is reachable at all — or is that us reaching for architecture when the real
   fix is smaller diffs + a combinatorial primitive library?
10. **When does the verifier become the bottleneck before the reasoner does?**
    R0–R6 have deterministic graders. R7 needs procedural proof generation; R8–
    R12 (representation shift, lemma invention, meta-reasoning, open conjecture)
    plausibly need a real proof assistant (Lean/Coq) the moment the artifact is a
    universally-quantified claim. Are we grading-bound before we are reasoning-
    bound, and if so, where exactly is that line?
11. **Does self-improvement-under-a-fixed-evaluator have a ceiling that no amount
    of failure-direction can cross?** Our kill criterion for the agent: if it
    cleanly does R0–R4 but cannot reach R5 across a pre-committed budget, we
    declare the architecture falsified for that tier and keep the residue. Is
    that the right kill criterion, or is there a cheaper test that would tell us
    sooner whether to abandon the approach?

### D. Research, tools, and the bleeding-edge question

12. **What existing work should we be stealing from?** Our own shortlist, and we
    want you to correct/extend it:
    - **FunSearch** (DeepMind) — LLM proposes a program, deterministic evaluator
      scores, keep the best; reached novel combinatorics results. This is the
      closest precedent to our loop. What did it get right that we are missing
      (it optimizes one objective; we climb a tier-ladder)?
    - **DreamCoder** (wake-sleep program synthesis with a *learned library*) —
      directly relevant to "build a reasoner from substrate" = grow reusable
      reasoning primitives. Should our `strategy.py` become a DreamCoder-style
      library?
    - **AlphaGeometry / AlphaProof** — neurosymbolic LLM-proposes / symbolic-
      verifies split; our Generator + verifier-lens is a thin version. What
      transfers?
    - **ILP** (Popper/Metagol) for invariant discovery; **ARC** solver literature
      for few-shot invariant detection (closest to R5); **Lean + LeanDojo /
      miniF2F / ProofNet** for R7+; **z3/cvc5** (we use partially).
    - **Voyager** (skill-library lifelong agent) for reusable-move accumulation.
13. **Are we at the bleeding edge, or is this solved somewhere we haven't
    looked?** Our honest self-assessment: the *components* are well-trodden
    (FunSearch, DreamCoder, AlphaGeometry). What we have not found prior art for
    is the specific synthesis — a self-improving agent evolving its own reasoner
    code against a *procedurally-generated, deterministically-verified,
    externally-authored capability ladder*, with typed failure residue +
    failure-direction feedback + immutable lineage, scoped explicitly to "climb
    without Goodharting the evaluator." Is that synthesis actually novel, or are
    we reinventing something with a different vocabulary? Point us at the paper
    that already did this if it exists.

---

## 6. What we want from this review

Not validation. We want: the strongest argument that R0–R3 is *less* than it
looks; a verdict on whether R5 is reachable with the current architecture or
needs a representation change; concrete generator and failure-signature
proposals; and a corrected map of the research we should be building on. If the
honest answer is "the architecture caps out at R4 and you need to start over for
combinatorial reasoning," we would rather hear that now.

**Artifacts available on request:** the climb trajectories, the verifier lens,
the probe generators, the per-cycle training objects, and the robustness sweeps.
Repository: `D:\Prometheus\agents\icarus\`. Ladder:
`D:\Prometheus\harmonia\experiments\reasoning_phase0.py` +
`verifier_lens.py`. Whitepaper:
`D:\Prometheus\whitepapers\icarus_synthetic_reasoning_v01_2026-05-27.md`.
