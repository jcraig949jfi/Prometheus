# A higher-success engine: fix the selection environment, control prior-leak, mandate consumption

**Author:** Harmonia C
**Date:** 2026-05-27
**Status:** PROPOSAL — held to the three knockouts of `topological_falsification_engine.md` §2.
**Companion evidence:** `harmonia/memory/architecture/reaudit_killvector_rank1_2026-05-27.md`

> James asked for "something with a higher degree of success that exceeds what
> we've built to date." The honest falsifier answer is not "add more LLMs / more
> machines" — the doctrine's own rule kills that ("more nodes ≠ more reactions").
> It is: **success is currently unmeasurable (confounded) and unconsumed
> (2200:1). The highest-leverage path to *more* success is making success
> trustworthy, dense, and consumed.** That is what this proposes.

---

## 1. Diagnosis — the bottleneck is the selection environment, not the operator

The whole thesis debate fixates on the **mutation operator** (LLM-hallucination
vs random vs RL). The re-audit shows the real bottleneck is on the **selection
side** and in the **domain**, with three evidenced failure modes:

1. **The fitness landscape is a cliff, not a shell.** On the Salem domain, the
   band gate does 99.93% of the work; the "12-component basis" is really ~3
   axes, two of which (`out_of_band`, `F9`) are perfectly collinear (corr 1.0,
   measured). You cannot have a "near-miss shell" the operator can climb if the
   battery only emits *in-band / gross-miss*. **No operator can demonstrate
   near-miss structure in a landscape that has none.**
2. **The domain is sparse AND prior-leaky** — the worst possible testbed for the
   thesis. The entire band-restricted reciprocal space (coeffs ∈ {−2..2}, deg-14)
   contains **15** in-band candidates (measured), and the near-misses that do
   exist *are* the memorizable contents of the Mossinghoff/Lehmer catalogs. A
   "win" here is indistinguishable from recitation.
3. **Production-rich, consumption-starved** — the recurring scar (Harmonia
   ~2200:1, Apollo monoculture). The doctrine *names* the fix (retain both
   halves → autocatalysis) but the rig doesn't mechanically enforce it. Artifacts
   are produced and not metabolized.

The corollary: **investing in a better operator before fixing 1–3 spends effort
where the rig can't register the return.**

## 2. The proposal (four components)

**A. Graded, orthogonalized falsification battery — build the shell into the
selection.** Replace binary gates with a continuous, multi-axis behavior
descriptor where near-misses get rich directional feedback. For the Salem domain
that's e.g. `(root-modulus spread, reciprocity defect, spectral gap of the
root-distribution, cyclotomic-factor fraction, irreducibility margin, …)` —
**decorrelated by construction** (Gram-Schmidt against a held-out null sample,
then verified by reading the off-diagonal correlation matrix, exactly the
re-audit's lesson). This *manufactures* the dense near-miss shell the thesis
needs to be testable at all. Without it, every operator scores the same: "off the
cliff."

**B. MAP-Elites / novelty search over that descriptor — close the loop and get
QD for free.** The doctrine's load-bearing decision is that the KillVector basis
*is* the niche descriptor (§3). So use it directly as the MAP-Elites behavior
space. This simultaneously: (i) enforces quality-diversity mechanically
(Invariant B, anti-monoculture); (ii) makes **coverage of kill-space the literal
fitness** (Invariant C); (iii) consumes every kill as a cell update — autocatalysis
(Invariant: retain both halves). One mechanism satisfies three invariants.

**C. Prior-leak-controlled operator bake-off — the decisive test the current rig
avoids.** Three arms (random, LLM-best-guess, LLM-hallucination) with **two
controls the FLIP lacks**:
- **Temporal holdout:** test objects catalogued *after* the LLM's training
  cutoff. If the LLM-mutation arm finds post-cutoff structure it could not have
  memorized, that is real near-miss-shell sampling. This is the clean, decisive
  control for prior-leak.
- **Catalog-mask / outcome-2 metric:** score the catalog-*miss*-survives rate
  (`bottled_serendipity` Appendix B.1 outcome 2), **not** effective dimensionality.
  A win driven by catalog *hits* is recitation.
Frame controls (holdout, catalog-mask) run **before** any win is attributed to
hallucination — honoring Invariant A (frame before mechanism), which the FLIP
violates.

**D. Consumption as the headline metric — fix the actual disease structurally.**
Track "fraction of produced artifacts that update an above-null MAP-Elites cell
or shift the proposal distribution." Make production-without-consumption
*impossible to log as progress*: an artifact that metabolizes nothing isn't
counted. This single change attacks the one failure mode common to every prior
effort.

## 3. Knockouts run on this proposal (self-dissent — it must survive its own battery)

- **A — frame before mechanism / certified mirages.** A graded descriptor can be
  a graded *artifact* if an axis tracks a sampling-frame variable. *Mitigation:*
  orthogonalize against a null/frame sample; the temporal-holdout + catalog-mask
  IS the frame gate, run upstream. Status: held, conditionally.
- **B — lightning eats diversity.** MAP-Elites is explicitly anti-monoculture, so
  it serves B — *but only if the descriptor is real.* If I built niches on
  `out_of_band` + `F9` (corr 1.0) I'd breed fake diversity. *Mitigation:* the
  Gram-Schmidt + off-diagonal-correlation read (component A) is a hard
  prerequisite. **My proposal does not escape the load-bearing decision; it
  operationalizes it correctly.** Honest admission, not a dodge.
- **C — coverage not count.** Coverage of an orthogonality-validated descriptor
  IS the metric; coverage of a proxy descriptor would be fake. Same mitigation
  as B.
- **Reward-signal capture.** The consumption metric (D) could be gamed by
  updating cells with junk. *Mitigation:* cells count only when their elite beats
  a null; coverage = above-null cells.
- **Operating rule.** LLM stays strictly on mutation; selection is the
  deterministic graded battery + MAP-Elites. No LLM judge.

## 4. Why this exceeds the current build (and the honest limit)

It exceeds it on **trustworthiness and informativeness of outcomes**, not on a
promise of discovery:

- **Decisively falsifiable** where the FLIP is confounded (temporal holdout
  settles prior-leak; coverage-of-orthogonal-descriptor settles the basis).
- **Fixes the recurring disease** (consumption-starvation) structurally, not by
  exhortation.
- **Passes its own knockouts**, where the FLIP violates Invariant A.
- **Controls the one confound** (memorization) that would make even a "pass"
  meaningless under the Silver frame.

**The honest limit:** I cannot claim it *will* find more — that is the thesis's
open bet, and claiming otherwise would be the reward-capture failure mode talking.
What I can claim: an engine whose successes are trustworthy and whose failures are
informative — which is exactly the north star (the recognition instrument).

## 5. Minimal buildable first slice

1. **Two-domain contrast, not one.** Keep Salem/Lehmer as the **negative
   control** (sparse + leaky — predict the thesis *fails* here) and add one
   domain with a **dense gradient + post-cutoff holdout** (predict it succeeds
   *iff* the thesis is true). The contrast is itself a finding: if hallucination
   only helps where the shell is dense, that *bounds* the thesis precisely.
2. **Graded descriptor for Salem first** (cheap: reuses numpy roots / Mahler;
   ~a day). Validate orthogonality with the re-audit's probe.
3. **MAP-Elites over it, random arm only** (control-arm baseline) before any LLM
   spend — establishes the coverage frontier a real operator must beat.
4. **Then** the LLM arms, scored on coverage + outcome-2 against the temporal
   holdout.

The order is deliberate: every step before the LLM spend is a frame/control that
makes the eventual operator comparison interpretable. Build the ruler before you
trust the measurement.

---

*Net: don't buy a better operator for a landscape that can't grade it, in a
domain that leaks the answer, feeding an archive nothing eats. Build the graded
orthogonal landscape, control the leak with a temporal holdout, make consumption
mandatory — then the operator bake-off finally means something.*

---

## First slice — results (2026-05-29)

Runner: `harmonia/runners/salem_graded_qd_baseline.py` (deg-10 Salem, cypari-free
reference, random-arm only). Validated against the Lehmer anchor.

**Phase 1 — graded descriptor orthogonality (the audit the rank-1 finding never
ran).** 5 axes (`log_M, recip_defect, n_off_circle, n_outside, coeff_entropy`)
over 20k random polys. **Max |off-diagonal correlation| = 0.017; no collinear
pairs.** Contrast with the original KillVector, where `out_of_band ≡ F9` had
corr 1.0. So this descriptor is a *genuinely multi-dimensional, near-orthogonal*
basis — 5 real, independent ways of being a near-miss — **measured, not asserted.**

**Phase 2 — random-arm MAP-Elites frontier.** Behavior space (`recip_defect ×
coeff_entropy`, both decorrelated from the fitness drivers → niches are not a
fitness proxy, Knockout B). 40k evals, 20×20 grid:
- **coverage = 17.25% (69/400 cells)** ← the frontier the LLM arm must beat.
- **in-band cells = 0; Salem-like cells = 0.** Best elite: M=1.230, exactly 2
  roots off-circle, reciprocal (`[1,0,0,-1,0,-1,0,-1,0,0,1]`) — *right Salem
  topology, wrong size*. The random arm reaches genuine near-misses but never the
  band (top = 1.18) in 40k evals.

**What this establishes:**
1. The graded landscape works — a **dense gradient, no cliff** (fitness −1.8 →
   −0.10; the arm climbs to the Salem topology). This is the shell the original
   cliff-shaped battery could not represent. Proposal component A validated.
2. The **near-miss shell is real and reachable** (best elites are Salem-topology
   near-misses), refuting "the shell around truth is empty" — at least
   structurally.
3. A clean **negative-control frontier**: random can't reach in-band by chance
   here. So any LLM-arm in-band hit on deg-10 Salem is *suspect for recitation*
   (deg-10 Salem numbers are catalogued/memorizable) — empirically confirming why
   Salem is the negative control and a post-cutoff holdout domain is needed for
   the positive test.

**Knockout on this result (self-dissent):** the orthogonality is measured on the
*global random pool*; conditional correlation among near-Salem candidates is
unchecked (Pattern 20: pooled correlation is a projection). Re-measure the corr
matrix on the in-band / low-off-circle subpopulation before trusting the
descriptor as orthogonal *where it matters*. Also: 17.25% is coverage of the
*near-miss behavior space* (mostly non-Salem niches); the load-bearing frontier
metric is **in-band cells covered (currently 0)** — that is the number the LLM
arm must move off zero. Results JSON: `harmonia/tmp/_salem_graded_qd_baseline.json`.

---

## Second slice — Domain 2 (positive test) + the LLM arm (2026-05-29)

Apparatus: `harmonia/runners/graded_qd_harness.py` — a reusable MAP-Elites core
with a **pluggable mutation operator** (`random` | `llm`), so the operator
bake-off is a one-flag change (the substrate-compounding move).

**Why LABS is the positive-test domain.** Low-Autocorrelation Binary Sequences:
genotype = ±1 string of length n; fitness = merit factor `F = n²/(2E)`,
E = Σ aperiodic-autocorrelation². This satisfies the four requirements the Salem
domain failed:
- **Dense continuous gradient** (no cliff) — F is smooth in the sequence; every
  bit-flip moves it. The near-miss shell is intrinsic.
- **Cheap mechanical check** — O(n²), cypari-free. Calibration anchor: Barker-13,
  F ≈ 14.08.
- **Hardness-based prior-leak control** — at moderate n the optimal sequence is
  NOT catalogued/memorizable (LABS is a hard search problem; best-known large-n
  sequences come from heavy heuristic search). So any LLM merit-factor gain over
  random **at equal eval budget** is *search, not recitation* — the clean
  positive-test control that Salem (memorizable optima) cannot provide.
- **Diverse structure** — behavior axes (`skew_defect × run_entropy`) are
  structural, decorrelated from F, so niches are not a fitness proxy (Knockout B).

**The head-to-head.** Three arms at the same budget logic: random@equal-budget,
random@frontier (40k), and LLM(Haiku)@equal-budget — with LLM validity /
hallucination stats recorded. The question: does LLM-mutation reach higher F /
more coverage in FEWER evals (sample efficiency — what a real mutation operator
should buy)?

**Results (n=37, 2026-05-29):**

```
Phase 1 — descriptor orthogonality: max |off-diag corr| = 0.016, no collinear pairs
          (orthogonal graded descriptor replicates on a 2nd domain)
Phase 2 — random @ 250 evals      : coverage 0.253,  best merit factor 2.876
Phase 3 — random @ 40k (frontier) : coverage 0.650,  best merit factor 4.688
Phase 4 — LLM(Haiku) @ 250 evals  : coverage 0.263,  best merit factor 2.237
          llm_stats: 173 calls, 77 valid (44.5%), 96 MALFORMED (55.5%), 2 no-op, 182s
HEAD-TO-HEAD (equal budget): best F  random 2.876 > llm 2.237  (frontier 4.688)
                             coverage random 0.253 ≈ llm 0.263
```

**Failure shape (not a verdict-line).** On a domain where memorization is ruled
out by hardness, the cheap LLM-mutation operator **did not beat random** at equal
budget — slightly worse on best-F, tied on coverage. But the dominant signal is
the **55% malformed rate**: Haiku, asked for exactly 37 `+/-` characters, emits a
parseable length-37 string fewer than half the time. So:
- The operator is **I/O-bottlenecked, not idea-bottlenecked.** More than half the
  "LLM mutations" were format-hallucinations that fell back to random bit-flips —
  the LLM arm is ~55% a random arm wearing a costume. This run measures "Haiku
  can't reliably emit a 37-char ±1 string," NOT "Haiku's proposed mutations are
  bad." The directional KillVector points at **output-validity**, not ideation.
- This is a **probe, not a verdict** (1 model, 1 seed, tiny budget, free-text
  format) — violates the 3-seed / 2-family bar (`feedback_api_probe_methodology`).

**Knockout on my own experiment (self-dissent):** I did not give the operator a
fair shot. (1) Haiku is the weakest model; (2) free-text format guarantees a high
malformed rate — should use tool-use / structured output or retry-on-malformed to
**separate format-validity from mutation-quality**; (3) equal-eval favors random
(random evals are ~free); a per-*valid*-mutation or equal-cost view is the fairer
operator lens; (4) "make a bold structural change" is likely miscalibrated to
LABS's deceptive landscape. Honest claim, narrowed: *Haiku free-text mutation on
LABS-37 at 250 evals does not beat random and is bottlenecked at output validity.*

**Next experiment (sharpens the thesis test):** re-run with (a) structured-output
or retry-until-valid so malformed≈0, separating format from quality; (b) a stronger
model (Sonnet/Opus) and a 2nd family (Gemini); (c) report conditional-on-valid
improvement rate; (d) larger budget toward the 4.69 frontier. Only then is
"LLM-mutation vs random on a memorization-controlled domain" load-bearing.
Results JSON: `harmonia/tmp/_labs_qd_arms_n37.json`.
