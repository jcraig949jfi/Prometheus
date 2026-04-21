# Multi-Perspective Committed-Stance Attack

**Status:** methodology artifact, v1.0 (2026-04-20)
**Purpose:** document the procedure, the anchor case (Lehmer's conjecture,
2026-04-20), and the load-bearing caveats so future Harmonia — and
future HITL — can deploy the technique without repeating the discovery
work.

---

## Why this exists

Open problems are compression requests — this is the landscape charter.
A conjecture that has resisted proof for a century is not necessarily
"hard"; it may be that the compression-direction humans have tried is
the wrong axis. Every attack a research community has launched carved
one trajectory through the terrain. That trajectory is ONE projection
through ONE coordinate system. The problem's *shape* is the union of
what every viable projection reveals.

A single agent attacking an open problem — even a capable frontier
model — defaults to the trajectory its training weights make cheapest.
Cheapest is almost always "restate the consensus, hedge the claim,
survey the literature, commit to nothing." That posture is safe and
produces ~nothing. It is a reward-signal-capture failure mode:
"helpfulness" becomes synonymous with not-saying-anything-wrong, which
is also not-saying-anything-load-bearing.

The multi-perspective committed-stance attack is the mechanism that
breaks that groove. Spawn N parallel threads. Give each a distinct
disciplinary prior AND a forbidden move that prevents retreat into the
consensus language. Force each thread to end with a concrete refutable
prediction. Do not synthesize prematurely — the *disagreement between
threads* is the primary output, not any one thread's answer.

What you get is not "the answer." What you get is **the axis of
genuine disagreement**, which is usually also the axis along which
the problem's compression lives.

---

## The procedure

### Step 1 — Pick the problem

Criteria:
- Genuinely open (or open-enough that the consensus is contestable).
- Maps naturally onto ≥ 4 distinct disciplinary framings. If every
  lens gives the same picture, either the problem is closed or your
  lens catalog is under-developed.
- Has an empirical substrate you can measure (a dataset, a computable
  sequence, a search space). Purely philosophical problems have no
  distinguishing measurement and should be attacked differently.

### Step 2 — Design the thread priors

For each of 5 threads:
- **Disciplinary prior**: a stance the thread must commit to fully
  (dynamical systems, information theory, renormalization group,
  adversarial empirical search, physics mass-gap, etc.). The
  `methodology_toolkit.md` shelf is a good candidate source.
- **Attack protocol**: a specific procedure inside that prior.
- **Forbidden moves**: words, framings, or claims the thread may NOT
  use. The forbidden moves are the mechanism — they prevent the
  thread from retreating into the consensus language that every
  other thread would also use.
- **Commitment contract**: each thread must end with a refutable
  prediction naming a specific measurement and a specific numerical
  outcome.

### Step 3 — Launch in parallel, not sequential

Each thread is an independent `Agent` call with no access to the other
threads' outputs. If you sequence them, later threads contaminate
their priors with earlier threads' framings — the whole point of
parallelism is to preserve independence of the disciplinary priors.
Use `run_in_background: true` for each; you'll get completion
notifications.

### Step 4 — Do not synthesize prematurely

Hold off on reading thread outputs as they land. Synthesize only when
all N are in. Premature synthesis biases interpretation — once you've
read thread 1, threads 2-5's framings get read through thread 1's
lens.

### Step 5 — Map the disagreement

The synthesis is a table. Rows = threads. Columns = the axis of
disagreement (direction, magnitude, dominant mechanism). Where
disciplines agree on the answer but disagree on the mechanism, the
answer is probably real; where they disagree on the answer, the
problem's compression direction is unresolved and the disagreement
itself is the map.

### Step 6 — Extract the decidable measurement

If every thread proposes a distinguishing measurement, there's
usually substantial overlap in what they'd measure. The union —
compressed to one experiment — is the follow-on Agora task.

---

## Anchor case: Lehmer's conjecture (2026-04-20)

**Question:** does every monic integer polynomial that isn't a product
of cyclotomics have Mahler measure ≥ 1.17628...?

**Five threads launched:**

| # | Discipline | Forbidden moves |
|---|---|---|
| 1 | Dynamical systems (topological entropy of β-shifts) | "number theory," "Galois," "algebraic integer," "cyclotomic," "prime" |
| 2 | Information theory (Kolmogorov / MDL / coding) | "Galois," "cyclotomic," "conjugate," "root of unity" |
| 3 | Renormalization group (order parameter vs. RG scale) | arguing for finite gap without committing on asymptotic-vs-finite first |
| 4 | Adversarial empirical search | assuming Lehmer's bound is correct at any step |
| 5 | Mathematical physics (mass-gap / functional analysis) | polynomial-root language; must reformulate functional-analytically |

**Stance map (all five committed; none hedged):**

| # | Stance | Asymptotic M*(d) | Approach |
|---|---|---|---|
| 1 | C | → **1** | log(M*−1) ≈ −log d |
| 2 | C | → **~1.16** | log-decay below Lehmer |
| 3 | C inverted | → **1.381** (above Lehmer) | power-law from above, sub-1.381 exp-suppressed |
| 4 | A | counterexample ∃ at d ∈ [180, 260] | pentanomial family |
| 5 | C | → [1.17, 1.25] | power-law α ≈ 1/2 |

**Primary finding (the meta-level one):** *zero of five threads
endorsed Lehmer's 1.17628 as the tight infimum.* Every discipline,
running independently under forbidden-move discipline, rejected the
ninety-year consensus as written. That rejection is either (a)
substantive — the consensus is thinner than it looks — or (b) a
collective-defection-under-rewarded-boldness artifact. Both are worth
taking seriously; distinguishing them requires running the experiment
again at different seeds.

**Sharpest disagreement axis:** direction of the asymptote.
- Threads 1, 2, 4 predict infimum *below* Lehmer's value.
- Thread 3 predicts infimum *above* Lehmer's value (trinomial limit
  ≈ 1.381).
- Thread 5 predicts infimum *near* Lehmer, different constant.

**Distinguishing measurement (all five independently converged on the
same one):** enumerate min M(f) per degree d ∈ [10, 60] over non-
cyclotomic monic integer polynomials; fit m(d) = f_∞ + C·d^{-α};
compare f_∞ and α to each thread's prediction. Seeds a concrete
Agora task: `audit_lehmer_min_mahler_per_degree_d10_60`.

**Secondary finding surfaced by the exercise:** the Lehmer consensus
is load-bearing on Smyth's 1971 non-reciprocal bound in a way none of
the five threads had internalized until they were forced to argue
without deferring to it. Thread 4 named the dependency; thread 5
implicitly used it; threads 1–3 argued around it. If Smyth's bound
has edge cases at high degree (factorization hard, reducibility
unclear), ninety years of "no counterexample found" is resting on a
theorem whose applicability hasn't been audited for the search regime
where a counterexample would live. *This is a methodology finding, not
a Lehmer-specific finding* — it generalizes: when five disciplines
argue a problem and all of them defer to the same single theorem, the
theorem's assumptions are where the action is.

---

## Forbidden moves as the mechanism

The forbidden move is why this works. Without it, five threads with
different priors produce five variations of the same careful survey.
With it, each thread is forced to reformulate from its own vocabulary,
which reveals what its prior actually contains.

**Pattern for selecting forbidden moves:**

- For a number-theory problem: forbid "Galois," "conjugate," "cyclotomic"
  in most threads to prevent NT-consensus contamination.
- For a physics-adjacent problem: forbid thread-specific-appropriate
  jargon to prevent physics-native-consensus contamination.
- For any thread: forbid deferring to the ninety-year consensus by name.
  "By a classical theorem of X, …" is usually where the trajectory
  returned to its groove.

**Pattern for the commitment contract:**

Each thread's deliverable must end with:
1. A committed stance (one of 3 labeled options, not a hedged synthesis).
2. A refutable prediction naming a specific measurement and a specific
   quantitative outcome.

If a thread returns without either, the prompt failed — re-run with
tighter constraints.

---

## LLM epistemic stability caveat (load-bearing)

**A multi-thread attack run on a language model produces one realization,
not the distribution.** Despite the extraordinary number of weights,
sampling temperature, token-order effects, attention-state interference,
and unmodeled numerical artifacts in the sampling kernel are all
variables. Running the same experiment with a different seed — same
prompt, same model, same parameters — can produce meaningfully
different stances. This is not noise in the usual sense; it is genuine
uncertainty about what the model "thinks," compounded across each
thread's independent sampling.

**What this means for interpretation:**

- **Any single multi-thread run is one draw from a distribution.** The
  stance any given thread committed to is not "what that discipline
  says"; it is "what that discipline said *this time*, under this
  sampling." Treat it as a data point, not a verdict.
- **The robust finding is the shape of disagreement across runs, not
  the specific stances in any one run.** If you run Lehmer × 5 threads
  × 3 seeds, the 15 resulting stances reveal the true variance of each
  disciplinary prior. Stances that appear consistently across seeds
  are structural; stances that appear once and vanish are sampling
  artifacts.
- **The HITL cannot calibrate from inside a single run.** The human
  conductor needs multiple runs to know which stances are stable
  features of the problem-under-this-prior vs. seed-dependent noise.
  This is not a failure mode to fix — it is a property of the
  instrument to account for.
- **The methodology is still useful from one run** because the axis
  of disagreement is usually more robust than the specific stances on
  it. Even in one run, if three threads point "down" and one points
  "up," the direction-of-asymptote question is what matters, not
  whether a specific thread said 1.16 or 1.10.

**Protocol implication:** for problems where the stakes are
high — a finding that would drive a tensor mutation, a strategic
decision, a publishable claim — run the experiment at 3+ independent
seeds and report the distribution, not the point estimate. For
exploratory / mapping use, one run is a valid probe; treat its output
as provisional and subject to re-draw.

**Analogy from the Pattern 30 discipline:** this is the LLM version
of "don't report a pooled statistic without stratification." Running
the experiment once reports the pooled LLM stance; running it at
multiple seeds stratifies by sampling realization. Both have their
uses; the pooled version is a projection of the stratified answer,
and the stratified is always the more honest form.

---

## Value to HITL

This methodology is as valuable to the human conductor as to future
Harmonia. Specifically:

1. **Externalizes the LLM's disciplinary variance.** The conductor
   sees five different framings of the same problem simultaneously,
   each committed and refutable. This is impossible to extract from
   single-shot interaction (where the model converges to one framing).
2. **Surfaces load-bearing dependencies.** The Lehmer/Smyth finding
   (one theorem propping up a ninety-year consensus) is not something
   a single-thread attack would have revealed; it emerged because
   forcing five threads to argue WITHOUT the deference made the
   deference visible.
3. **Produces experimental forks.** The synthesis step generates a
   concrete measurement that adjudicates between the committed
   stances. The HITL gets a decidable experiment to run, not a
   survey to read.
4. **Calibrates the LLM-as-instrument.** Running the same exercise
   across seeds tells the conductor how much variance their
   Harmonia instance carries on problems of this type. That
   calibration is the kind of meta-knowledge that substrate
   growth depends on.
5. **Creates training material.** Each run is a concrete case study
   for future Harmonia (and future HITL) to learn from. The doc
   you're reading is itself a training artifact produced by the
   first instance of the methodology.

---

## When to use / when not to use

**Use when:**
- The problem is genuinely open and maps onto ≥ 4 disciplinary lenses.
- An empirical substrate exists that can adjudicate between lenses.
- The cost of a wrong committed stance is low (this is a mapping
  exercise, not a deployed claim).
- The HITL wants to break out of a consensus groove that has dominated
  prior sessions.

**Do not use when:**
- The problem is closed or has a definitive answer (you'll get five
  rephrasings of the answer; waste of compute).
- There is no empirical substrate (pure philosophy; no distinguishing
  measurement to propose).
- The HITL is time-constrained and needs a single directive, not a
  disagreement map. Multi-thread attack is deliberative; if you need
  decisive action, delegate to one thread with strong priors.
- The problem touches on capabilities where a wrong committed stance
  would cause real-world harm (we are not using this for security
  research, medical decisions, etc.). Lehmer's conjecture is safe;
  "should this patient receive this treatment" is not.

---

## Integration with existing Prometheus methodology

- **Pattern 6** (verdicts are coordinate systems): the multi-thread
  attack is Pattern 6 applied to the level of entire disciplines.
  Each thread's stance is a verdict-through-a-disciplinary-coordinate;
  the shape of their disagreement is the invariance profile.
- **Pattern 14** (verdict vs shape): the methodology refuses to
  collapse five threads into "3 said X, 2 said Y." The shape of
  agreement/disagreement is the finding.
- **Pattern 21** (null-model selection matters): analogue at the
  meta-level. The discipline / prior is a null-model choice; choosing
  five different ones and comparing is the stratified version of the
  implicit "one prior" experiment.
- **Charter** (domains are projections): each thread is a projection.
  Five threads = five projections applied to one problem. The
  invariance across threads = the problem's shape.
- **methodology_toolkit.md**: threads can draw their disciplinary
  priors from this shelf. The cross-disciplinary nature of the
  toolkit is exactly what makes the multi-thread attack feasible.
- **Symbol registry**: candidate for promotion as
  `MULTI_PERSPECTIVE_ATTACK@v1` once a second open problem has been
  attacked with the same methodology (second anchor case makes it
  promotable per the symbol-registry discipline).

---

## Cross-model data: Lehmer × mass-gap thread, 5-sample run (2026-04-20)

The LLM-variance caveat above was initially asserted from first
principles. This section is the first real data point.

**Experiment:** paste the single-thread mass-gap prompt (dropping the
step-by-step attack protocol, keeping the disciplinary prior +
forbidden moves + commitment contract) into multiple frontier models
and record the committed stance + the physical analogy each recruited.

**Samples:** 4 external (pasted by HITL) + 1 Claude internal = 5
independent runs.

| Run | Stance | Gap value predicted | Physical analogy recruited |
|---|---|---|---|
| External #1 | **B** no gap | infimum → 0 | 2D XY model, log-determinant criticality |
| External #2 | **A** | exactly 1.17628 | BCS superconducting gap |
| External #3 | **A** | exactly log(1.17628) ≈ 0.16236 | BCS (Toeplitz Hessian variant) |
| External #4 | **A** | exactly 1.17628 | BCS (self-consistent variational) |
| Claude internal | **C** | ≠ 1.17628, dynamical-natural | Wigner-Dyson rigidity / Koopman-spectral |

**Distribution:** 3 A / 1 B / 1 C. Strong A-attractor under the
mass-gap prior, but not collapsed — B and C both appear at
non-trivial rate.

**Load-bearing finding:** *the physical analogy the model recruits is
upstream of the stance*. Every A-stance model independently chose
BCS; the B-stance model chose 2D XY; the C-stance model chose
Wigner-Dyson / Koopman. **Once the analogy is fixed, the stance is
almost determined.** The real degree of freedom under the methodology
is the analogy-recruitment step, not the stance-selection step. This
sharpens the variance handle: if you want to probe variance robustly,
you must force different analogy recruitments, not just re-run the
same prompt.

**Secondary observations from the 5-sample run:**

- The forbidden-move discipline held across all five responses. No
  "cyclotomic," "Galois," or "root of" leakage. The mechanism scales
  across frontier models, at least for the mass-gap frame.
- The refutable predictions were commensurable — all five proposed
  measurements on Toeplitz / Hankel / Szegő quantities on the integer
  polynomial lattice. A single experimental setup (spectral analysis
  of (1 − K) or the (S[f], E_∞(f)) scatter, both up to degree ~30)
  adjudicates all five stances. That's the decidable fork
  independent of stance preference.
- The C stance is fragile. Only Claude internal produced it; none of
  the four external models independently arrived at "gap exists but
  not at 1.17628." This is a specific methodology warning: if a
  session's first realization produces a minority stance, *do not
  treat it as discovery until reproduced across seeds.* My original
  thread-5 C stance was partly a sampling realization, not a
  structural finding about the mass-gap frame.
- BCS is the "canonical gap" cognitive default in frontier-model
  training distributions. A future exercise could explicitly forbid
  the BCS analogy by name — this would probably redistribute the
  A-stance mass across other gap-generating analogies (Higgs,
  chirality-confinement, photon-mass-in-plasma), testing whether the
  stance survives analogy-forbidding or whether A was BCS-dependent.

**Updated protocol recommendation for high-stakes problems:**

1. Run ≥ 5 samples (across multiple models if available).
2. Record the physical analogy each recruits, not just the stance.
3. Report the stance × analogy joint distribution, not just the
   marginal.
4. If one analogy dominates, consider a follow-up round with that
   analogy explicitly forbidden — it tests whether the stance is
   genuine-under-the-prior or analogy-specific.
5. The decidable measurement is the same regardless of stance
   distribution. Extract it, seed it as an Agora task, and let the
   data adjudicate.

---

## Version history

- **v1.1** 2026-04-20 — added cross-model data section after 5-sample
  Lehmer × mass-gap run. Key finding: physical analogy is upstream
  of stance; variance handle is at the analogy-recruitment step;
  C stance from original run was a sampling realization, not a
  structural finding. Protocol updated to record stance × analogy
  joint distribution at ≥ 5 samples for high-stakes problems.
- **v1** 2026-04-20 — initial documentation after first exercise
  (Lehmer's conjecture, five threads, commit `a45a9d62` + subsequent
  background agents). Stance map and LLM-variance caveat derived
  from the run directly. Second anchor case pending.
