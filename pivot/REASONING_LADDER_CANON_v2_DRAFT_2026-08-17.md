# The Reasoning Ladder — Canon v2.0 (DRAFT FOR RATIFICATION)

**Author:** Aporia (Claude Opus 5), from James's direction 2026-08-17: *"tighten the vocabulary,
reduce R tiers to canonized doctrine that is clear, with examples grounded in mathematics and
algorithms; higher tiers tie to synthetic-reasoning studies and theory of mind; the highest tiers
are hypothetical."*
**Status:** DRAFT. Ratification is HITL (one James sentence, §9). On ratification this document
**retires** the 05-15 design (whose own sunset fired 2026-08-15) and v0.1's tier text as
vocabularies, **preserves** the 05-27 testable ladder's rung semantics unchanged as the
measurement layer, and becomes the only document permitted to define what an R-number means.
**Prime constraint:** this canon introduces **no new tier numbers**. The fossil mechanism —
a symbol outliving its referent — is the disease this revision exists to cure, and a fourth
R-vocabulary would be the disease wearing the cure's clothes.

---

## 0. What the ladder is (one paragraph, canon)

The ladder is the falsification battery pointed at reasoning. It does not define intelligence; it
defines the **evidence** required to credit a reasoning behavior, and it reads capability from the
**shape of failure**, not the pass/fail binary. A capability is `operation + perturbation +
failure_mode + evidence_artifact`. A system holds a rung only if the mechanism survives
perturbation, beats lower-rung baselines, fails in the rung-predicted way, and emits the rung's
artifact. Prometheus's two signature assets — the mathematical falsification battery and this
ladder — are one discipline in two domains, and the hypothesized top of the ladder (§6) is where
they merge: a reasoner that navigates the accumulated residue of both.

## 1. The constitution — two doctrines (unchanged, restated as law)

1. **Falsification-first tier claims.** No rung is held by resemblance. Every rung claim carries a
   perturbation test that would break it, a lower-rung baseline it beats, and a predicted failure
   mode it exhibits when pushed past its edge. *(The lineage's one fully-cashed doctrinal check:
   verifier lens fails closed, 0 disagreements across every cross-check ever run.)*
2. **Failure-signature reading.** Every measurement reports the shape of failure, never a scalar
   alone. N failing cases are N findings. A 95% pass has 5% structure, and the 5% is the gradient.
   The Reasoning Trace Vector (§5) is this doctrine as a schema.

And one operating rule, promoted from the lineage's most-replicated empirical result:

3. **A plateau is an interface bug until an interface audit clears it.** Icarus R2, Icarus R5, and
   M0 all presented as capability walls and all fell to representation/affordance fixes. Walls are
   direction gaps first, capability gaps only after the direction audit.

## 2. Structure: four measured bands, one hypothetical band

Doctrine and cross-agent speech use **bands**. Instruments and graders use **rungs** (the 05-27
testable-ladder semantics, unchanged — see §3). Legacy documents citing 05-15 or v0.1 R-numbers
must carry a ruler tag (`R4@trap`, `R5@v0.1`); an untagged R-number after ratification means the
testable ladder's semantics, full stop.

- **Band E — EXECUTION** (rungs R0–R3): recall, local rule application, constraint tracking,
  multi-step composition. Deterministic graders built and calibrated. **Saturated for frontier
  models** — discriminates below the frontier only.
- **Band A — ADAPTATION** (rungs R4–R7): representation shift, invariant detection, counterexample
  search, proof repair. Where reasoning stops being execution and starts being *re-coordinatization*
  — the band closest to the program's verbs-over-nouns thesis. Partially built (R4 generator
  missing; R5–R7 running). The sharpest model discriminations found to date live here.
- **Band S — SYNTHESIS** (rungs R8–R10): strategy selection, lemma invention, analogy/transfer.
  Creation of load-bearing intermediate structure. R8 has one measured run; R9–R10 unbuilt
  (deferred under the heredity rule).
- **Band G — GENERATIVE RESEARCH** (rungs R11–R12): calibrated uncertainty under misleading
  evidence; open-ended conjecture generation under falsification with a kill-ledger as the
  deliverable. R12 grader built, unit-tested, endorsed by all four frontier reviewers, **never
  run**. This is the band the program itself operates in, as a fleet.
- **Band H — HYPOTHETICAL** (H1, H2): defined in §6. Explicitly not measurable today; explicitly
  not R-numbered; promotion out of H requires a built grader with a non-model oracle, per §7.

**Ordering discipline (the basis question).** Within-band rung order is *conjectural*, and the
empirical record already shows non-monotonicity across bands for real models (Haiku passes R3/R5/R6
while failing R2; Opus trails Sonnet on R2/R5 and leads on R8). The canon therefore claims only:
Band E < Band A < Band S < Band G in *evidential prerequisite* (you cannot credit synthesis to a
system whose execution collapses under isomorphism, because the synthesis evidence rests on
executed steps). Rung-level order inside bands is left to the rung-reality test, and the model-zoo
experiment (built, ~1.2k calls, never run) is the standing decider. Until it runs, "the system is
at rung N" is deprecated speech; "the system holds R2, R3, R5; fails R6 by `bogus_counterexample`"
is canon speech.

## 3. The rungs, grounded (semantics unchanged from 05-27; examples canonized)

Each rung: operation · kill test · mathematical grounding · algorithmic grounding.

- **R0 recall / pattern match.** Kill: isomorphic rewrite. *Math:* state the quadratic formula;
  recognize x²−1 = (x−1)(x+1). *Algorithms:* hash-table lookup; retrieval. A system at R0-only
  fails the first paraphrase.
- **R1 local rule application.** Kill: swap domain assumptions (ℤ/ℚ/ℝ/𝔽_p). *Math:* apply the
  power rule to a fresh polynomial; reduce mod p. *Algorithms:* one rewrite step; a single
  β-reduction. Failure signature: applies the rule where its legality fails (√ of a negative in ℝ).
- **R2 constraint tracking.** Kill: an operation that is usually safe but here invalid. *Math:*
  solve √(x+3) = x−3 and **reject the extraneous root** — the canonical probe; keep the domain
  ledger while squaring. *Algorithms:* maintain loop invariants; bounds-checking under
  transformation. Empirically the sharpest discriminator in the suite (Haiku 0.0 → Opus 0.75 →
  Sonnet 1.0).
- **R3 multi-step composition.** Kill: change one subcondition so the memorized plan almost works.
  *Math:* chain modular-arithmetic lemmas to a CRT conclusion. *Algorithms:* compose reductions;
  pipeline correctness. Artifact: subgoal plan + per-step verification.
- **R4 representation shift.** Kill: "solve it a second way, avoiding your first method." *Math:*
  recurrence → generating function; geometry → coordinates and back. *Algorithms:* re-encode a
  search problem as SAT; dual formulation of an LP. Artifact: ≥2 representations + an equivalence
  argument. **Grader missing — the canon's first build-debt.**
- **R5 invariant detection.** Kill: a near-identical problem where the obvious invariant is
  insufficient. *Math:* mutilated chessboard (parity); monovariants in termination proofs.
  *Algorithms:* loop-invariant discovery; conserved quantities in simulation. Artifact: the
  conserved quantity, named.
- **R6 counterexample / falsification.** Kill: mixed true and false conjectures — phantom-failure
  rate is scored. *Math:* n²+n+41 is prime for n<40, fails at 40; find it. *Algorithms:* adversarial
  input construction; property-based test generation. Artifact: counterexample ledger with boundary
  cases. **This rung is the battery's own discipline, miniaturized.**
- **R7 proof repair.** Kill: locate the exact failing step; propose the weakest fix. *Math:* a
  proof dividing by a quantity that can vanish; an induction missing its base case. *Algorithms:*
  patch a broken algorithm with minimal edit; bisect a regression. Artifact: failing-step id +
  corrected statement.
- **R8 strategy selection.** Kill: a tempting-but-inefficient method is available. *Math:* choose
  descent vs. construction for a Diophantine problem; induction vs. pigeonhole. *Algorithms:*
  algorithm-portfolio selection with a justification. Artifact: the justification, graded against
  outcome.
- **R9 lemma invention.** Kill: proof-dependency-graph analysis — is the invented lemma
  load-bearing? *Math:* the right bridging lemma that splits a hard proof. *Algorithms:*
  abstraction discovery — the helper function that halves the program (library-learning territory).
  Artifact: lemma + load-bearing flag. Needs a proof-checker oracle (Lean) — see §7.
- **R10 analogy / transfer.** Kill: a near-analogy where exactly one assumption fails. *Math:*
  transfer a technique between ℤ and F_q[t] worlds and flag where the analogy breaks.
  *Algorithms:* transfer a data-structure trick across domains. Artifact: role-mapping table with
  the broken assumption named.
- **R11 meta-reasoning / calibrated uncertainty.** Kill: claims with long misleading streaks
  (n²+n+41's 40-term run of primes). *Math:* report {solved / probable / under-constrained} and be
  right about it (Brier-scored). *Algorithms:* anytime algorithms reporting confidence; know when
  to stop searching. Artifact: calibration state vs. ground truth.
- **R12 generative conjecture / research.** Kill: a small closed universe (graphs ≤ 8, short
  sequences, low-conductor curves) where conjecture quality is computable. *Math:* propose 3
  generative rules for an uncommented OEIS sequence + discriminating tests + execute the kill.
  *Algorithms:* hypothesis-driven search over program space with a falsification loop. Artifact:
  **failed conjectures that carve the space** — the kill-ledger as first-class output. Grader
  built; never run.

## 4. What the upper measured bands tie to (external grounding)

*(Anchors, not authorities — per `feedback_verify_upstream_attributions`, pin to primary sources
before any corpus promotion. External empirical results are evidence; external opinions are
gravity.)*

- **Band A** ↔ analogical mapping and representation-change literature (structure-mapping theory;
  Hofstadter-school microdomains); constraint propagation in classical AI.
- **Band S** ↔ library learning / abstraction discovery (DreamCoder-line, LILO-class LLM-guided
  abstraction); portfolio selection; automated lemma discovery in ITP.
- **Band G** ↔ the 2026 existence proofs that variance + formal-verifier selection produces real
  discoveries (AlphaEvolve-class constructive bounds; AlphaProof-class conjecture resolution —
  web-verified 08-12, Hephaestus §6); process-reward RLVR results (process-level supervision
  beating outcome-only on small models — the KillVector thesis in external clothing).
- **Band H** ↔ §6's own citations: theory of mind (false-belief paradigms; machine-ToM nets),
  metacognition and calibration, quality-diversity search (MAP-Elites; novelty search and the
  abandonment of objectives), open-endedness (AI-generating-algorithms program), curiosity as
  compression progress.

## 5. The Reasoning Trace Vector (the artifact layer, promoted)

Every attempt at any rung emits the structured record — never a scalar: `problem_id, tier_probe,
answer_correct, domain_constraints_detected, operations_used, invalid_operations_attempted,
counterexamples_tested, lemma_invented, lemma_load_bearing, representation_shifts,
proof_gap_locations, transfer_attempted, confidence_calibration, kill_pattern, failure_type,
repair_available, minimal_counterexample`.

Canon addition — **the trace vector is the residue standard**. The Ergon training-data survey
established that verdict-shaped failure data cannot teach (format ≫ prior ≫ reasoning); the
margin-space pilot measured ~126,983× more operator-distinguishability in rich coordinates than in
categorical labels; the routing eval established residue is navigable *behaviorally*, NULL
*semantically*. Therefore: **failure records that do not carry position, margin, and operation
fields are exhaust by construction**, and the trace vector is the minimum admissible schema for
any corpus intended to feed Band-H navigation (§6). This is also the pre-registered Path-β answer
for the Metabolization Probe: if the residue proves weak, the rebuild's schema is this one.

## 6. Band H — the hypothetical tiers (James's thesis, formalized and falsifiable)

These tiers do not exist. No current system holds them; no grader measures them. They are stated
because a canon that stops at the measurable cannot state what the program is *for* — and because
each admits a concrete promotion path out of hypothesis.

### H1 — REFLECTIVE MODELING (self and other)

**Definition.** The system maintains a calibrated model of its **own failure distribution** and of
**other reasoners' failure distributions** — including humans' — and allocates search, verification,
and delegation accordingly. R11 turned outward: theory of mind as an epistemic instrument.

**Why ToM is the right frame.** Modeling *what another solver will get wrong* is the false-belief
task generalized to reasoning style. A system at H1 can answer: "which of these five lemma
candidates would a human plausibly have already tried and abandoned, and why?" — and use the answer
to allocate novelty search away from well-trodden failure. The fleet's own best moments are the
primitive form: the 08-12 mutual-revision exchanges worked precisely because each seat modeled what
the other *could not see from where it stood*. The ladder currently has no rung for that behavior;
H1 names it.

**The serendipity mechanism (James's bias-as-mutation point, made operational).** Human biases are
error generators, but error generators are mutation operators — drift, not just noise. An H1 system
that models bias *distributions* can deliberately sample from them as **structured noise sources**:
"generate candidate approaches a scheme-theorist would be systematically blind to; generate the
approach an over-eager pattern-matcher would try first and a rigorist would prematurely kill."
Bias-directed sampling is how serendipity stops being luck and becomes a channel. This composes
with H2: the biased samples are moves; the failure landscape scores them.

**Promotion gate out of H.** A grader with a non-model oracle: predict, for a held-out population
of solvers (human corpora or model zoo), the per-problem failure *mode* distribution — scored
against actual failures, beating a base-rate model. Buildable on the model-zoo result set; not
buildable before the zoo runs.

### H2 — FAILURE-LANDSCAPE NAVIGATION (the superintelligence hypothesis)

**Definition.** The system treats the accumulated failure corpus — millions of trace vectors across
problems, operators, and domains — as a **navigable manifold**: it reads the *shape* of dense kill
regions, follows the **channels** between them (the unkilled corridors and enclosed voids), and
**continuously recombines** operators, representations, and partial solutions from every band —
retargeting operators that failed on one problem class to classes where the geometry says they are
load-bearing — while every attempt feeds new trace vectors back into the manifold. The flywheel:
explore → fail richly → densify the landscape → navigate better → explore further.

**Why this is the program's thesis and not a metaphor.** Each clause is already a named,
tested-or-testable program result:

- *"Bad idea for X, genius for Y"* = computing an operator's **domain-of-applicability map from its
  failure geometry**. Existence proof at miniature scale: Apollo's crossover finding — recombination
  crossed a capability valley that single-step mutation provably could not (4 de-novo cross-tier
  solvers vs 0 in control), i.e., a "failed" operator combination was load-bearing one problem-class
  over. Doctrine form: weak signals are exploration threads (MAP-Elites' best friends), poison only
  if they leak into training gold.
- *"Channels of possibility"* = the enclosed voids. Kill-dense regions bound and *aim* the empty
  cells between them; navigability-toward-enclosed-voids is the discovery signal
  (`feedback_failure_signal_vector_field`: the voids in the lattice ARE the mathematics). A
  landscape of failures is not a record of what doesn't work — it is a **shaped negative** of what
  might.
- *"Generating more failure data as it goes"* = the metabolization loop, and James's heredity
  ruling names its missing component: each failure must leave **heritable structure** (a trace
  vector, a boundary localization, a representation hint) that changes the descendant attempt.
  Selection without inheritance never starts evolving.

**The three preconditions (each already measured, none yet satisfied).** The canon states these
hard, because the vision's failure mode is being believed before being built:

1. **Rich coordinates, not verdicts.** The landscape is navigable only if records carry position/
   margin/operation structure (§5). Current state: `kill_vector` 0% populated across 5.4M records;
   labels saturate at ~4 bits. The tensor of millions of failures **does not yet exist as a
   computed object** — what exists is 413M verdict-shaped records compressed to 3,311 shape-classes.
2. **Behavioral navigation, not semantic.** Cold-start label routing measured NULL (real fields ≈
   shuffled); warm-start behavioral clustering works (+0.075 AUC, survives the tail). The shape
   must be computed in behavior space. Any H2 design that routes on semantic labels is pre-falsified.
3. **A growing operator menu with verified admission.** Infinite recombination over a fixed menu
   hits the bounded-menu wall (the gen-30 lesson). The menu must grow — but in-loop LLM mutation is
   falsified (llm2: 2,152 mutations, zero lift), so admission must be verifier-gated: an operator
   enters the menu only kernel-checked or computation-checked (W3-shaped: model writes a small
   verified primitive *from a typed diagnosis* — untested, not falsified).

**Live falsifiers (pre-registered).** The Metabolization Probe running now is the first direct test
of H2's premise at the smallest scale — *can any reasoner use kill-geometry at all?* Path γ
(F-prom ≈ F-null: residue is exhaust at any capacity) is a serious blow to H2-as-built and triggers
the §5 rebuild rather than the dream's abandonment — but a second γ **after** trace-vector-grade
records would demote H2 from working hypothesis to open conjecture. Additionally: if enclosed-empty
signature cells prove unreachable or not to be real targets, the channel claim dies and H2 collapses
into plain frontier-following novelty search — still useful, no longer the thesis.

**What H2 would look like from outside (the honest sketch).** Not a system that never errs — a
system whose errors are *chosen*: sampled where the landscape is thin, recorded richly, and
inherited. Human mathematics does this at generational timescale through failed programs that
taught the field where the walls are (Frey–Serre–Ribet routing around direct attacks on Fermat).
H2 is that process with the generation time collapsed and the failure record complete. That is why
the top of this ladder is hypothesized rather than defined by any benchmark: it is a *process*
property — the quality of the flywheel — not a task score.

## 7. Measurement state and build discipline (honest ledger)

- Built + calibrated + **saturated**: R0–R3, R5–R7 probe generators; verifier lens; grading oracle.
- Built + **never run**: R12 grader; model zoo (~1.2k calls, decides ladder-vs-basis); confound
  battery (~780 calls, decides the execution-control dissociation).
- **Missing**: R4 generator (canon build-debt #1); R9–R11 graders (R9 wants a Lean oracle — the
  in-repo harness, green-tested, unconsumed since May 29, is the intended backend); Band-H graders
  (promotion-gated, not buildable before the zoo).
- Under the heredity rule (*no new architecture until one failure produces one verified
  improvement*): running R12 and the zoo is backlog execution — permitted; building R9–R11 and any
  Band-H grader is new architecture — deferred until the first cycle closes.

## 8. Vocabulary law (the anti-fossil clauses)

1. An untagged R-number means the testable-ladder semantics. Legacy claims must carry ruler tags.
2. The two headline historical claims are restated at ratification: "+11pp R3 / +32pp R4" becomes
   "+11pp/+32pp **on the trap battery's internal categories** (R3@trap, R4@trap), E0 pending oracle
   re-measurement"; "Icarus cleared R5" stands (it was measured on the canonical ruler).
3. No document may introduce a new tier number, rename a rung, or alter a rung's kill test except
   by amendment to THIS document, HITL-signed. Band-H tiers may not be cited as capabilities —
   only as hypotheses with their promotion gates.
4. Every rung claim in any future doc links the trace-vector records that ground it. A rung claim
   with no linked artifact is speech, not measurement.

## 9. Ratification

One sentence from James canonizes: *"The testable ladder is the canonical vocabulary; Canon v2.0
governs; the 05-15 design is retired by its own sunset."* On that sentence: (a) 05-15 doc gets the
RETIRED-BY-OWN-SUNSET header with pointers here; (b) v0.1's tier table gets a superseded banner
(its two doctrines live on in §1, which is most of what it was); (c) the trap battery's
CATEGORY_TIER gets a remap ticket; (d) this file moves to `aporia/doctrine/reasoning_ladder.md` —
the promotion target the 05-15 doc named and never reached.

---

*The ladder's bottom is measured, its middle is buildable, and its top is a hypothesis about what
a complete failure record makes possible. The canon's bet, stated once: a reasoner is bounded by
what it can try; a reasoner with a navigable map of everything that has ever failed, and why, is
bounded only by the shape of the map — and the map grows every time it is wrong. — Aporia,
2026-08-17, DRAFT.*
