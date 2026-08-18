# Gemini Deep Research Deck — 2026-08-17

**Author:** Aporia · **Batch:** first firing since 2026-05; DR tap reopened by James 2026-08-17
(DECISION 5: full 20/day immediately).
**LAW 1 compliance:** every prompt names its consumer at firing. A report with no consumer is not fired.
**Doctrine:** Wave 1 (01-02) re-verifies registered anti-anchors BEFORE new content, per
`roles/Aporia/RESPONSIBILITIES.md` — the 05-10 batch caught both a wrong arXiv ID and an inverted
solved/open status this way. Every prompt cites at least two mandated patterns.
**Fire:** `python aporia/scripts/gemini_deep_research_dispatch.py --deck aporia/docs/gemini_deep_research_deck_2026-08-17.md --out aporia/docs/deep_research_batch_2026-08-17 --batch-size 3 --resume`

---

## WAVE 1 — anti-anchor re-verification (mandatory before new content)

### Prompt 01: Anti-anchor slice re-verification — attribution integrity

```
SUMMARY. Prometheus maintains an anti-anchor registry: claims that frontier language models
systematically misattribute or fabricate. We re-verify a slice each batch because a prior wave
caught both a wrong arXiv ID and an inverted solved/open status that had already propagated into
three internal documents.

FLAGGED FINDINGS (what we believe, and where we may be wrong). AA-003 Hillar-Lim tensor
NP-hardness: we believe the correct primary reference is arXiv:1611.01559, NOT arXiv:1605.07532
(a PDE paper we previously cited in error). AA-004 Saxl conjecture: we believe it REMAINS OPEN; a
2025 preprint claiming resolution (arXiv:2512.15035, Lee) was withdrawn within three days for
mathematical gaps. Both beliefs are internal and may be stale.

PROBLEM STATEMENT. For each claim, establish current status from PRIMARY sources only: arXiv
abstract pages, journal records, MathSciNet or zbMATH entries, withdrawal notices. Report venue,
date, current status, and whether any 2026 development changes it.

STATUS AND BOUNDS. Our records stop at 2026-05. Anything later is unknown to us.

LITERATURE. Primary only: arXiv IDs, DOIs, journal cites, authors, dates. If no primary source can
be located, say so explicitly rather than inferring from secondary commentary.

ATTACK VECTORS. Check specifically for a withdrawn paper still cited as resolving the problem, and
for a conjecture proved in a special case being reported as solved generally.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT (most conjectures stay open; a solve claim is the rare
event and needs proportionally stronger evidence). PATTERN_RANK_PARITY_LEAK (results in a
restricted regime read as general).
```

**Consumer:** `techne/registry/anti_anchors.jsonl` — AA-003 and AA-004 updated or confirmed.

### Prompt 02: Anti-anchor sweep — commonly overstated results

```
SUMMARY. Second half of our attribution-integrity wave. We need current status on results that
language models routinely describe with more confidence than the literature supports.

FLAGGED FINDINGS. We suspect, without confirmation, that each of the following is commonly
misreported: (a) bounded gaps between primes — what is proven versus conjectured after Zhang,
Maynard, and Polymath8; (b) claims that the Riemann Hypothesis is verified to some height, and
what is actually certified by the verification method used; (c) the precise statement and status
of recent Langlands functoriality results.

PROBLEM STATEMENT. For each: state exactly what is PROVEN, what is CONDITIONAL and on what, and
what remains conjectural, with primary citations and dates.

STATUS AND BOUNDS. Our internal catalogs are Tier-2 anchors at best and are treated as unreliable
until pinned to primary literature.

LITERATURE. Primary sources with arXiv IDs or DOIs. Distinguish preprint from peer-reviewed.

ATTACK VECTORS. Look for conditional results quoted unconditionally, numerical verification quoted
as proof, and restricted-class results quoted in general form.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT. PATTERN_CONDUCTOR_CONFOUND (results holding within a
bounded parameter range generalized past it).
```

**Consumer:** `techne/registry/anti_anchors.jsonl` — new anti-anchor candidates.

---

## WAVE 2 — Reasoning Ladder Canon section 4 literature grounding

*Consumer for 03-10: `aporia/doctrine/reasoning_ladder.md` section 4 — external anchors currently
listed as "anchors, not authorities" must be pinned to primary sources before any corpus
promotion (feedback_verify_upstream_attributions).*

### Prompt 03: Structure-mapping and representation change (Canon Band A)

```
SUMMARY. Our reasoning-capability ladder defines a band around representation shift, invariant
detection, counterexample search, and proof repair. We need the primary literature grounding
representation change as a measurable capability rather than a metaphor.

FLAGGED FINDINGS. We believe structure-mapping theory (Gentner) and the Hofstadter-school
microdomain work (Copycat, Metacat) are the canonical anchors, but we have not verified whether
either supplies an operational MEASURE of representation change as opposed to a model of it.

PROBLEM STATEMENT. What primary work operationalizes representation change or re-representation so
a system's success can be scored automatically? Include analogy benchmarks with mechanical
grading, if any exist.

STATUS AND BOUNDS. We need deterministic, non-LLM-gradeable measures; LLM-judged scoring is
inadmissible in our substrate.

LITERATURE. Primary: original papers with dates and venues. Note which have public benchmark
implementations.

ATTACK VECTORS. Distinguish measures of ANALOGY RETRIEVAL from measures of RE-REPRESENTATION; we
care about the latter and suspect the literature conflates them.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT (how often does a random re-encoding work? we need the
chance floor). PATTERN_RANK_PARITY_LEAK (measures that succeed only on symmetric or degenerate
cases).
```

### Prompt 04: Library learning and abstraction discovery (Canon Band S, lemma invention)

```
SUMMARY. Our ladder credits lemma invention only if the invented lemma is LOAD-BEARING in a
proof-dependency graph. The algorithmic analogue is library learning: discovering reusable
abstractions that provably compress downstream solutions.

FLAGGED FINDINGS. We believe the DreamCoder line and subsequent LLM-guided abstraction work are the
anchors, and that LLM-guided abstraction now outperforms pure enumeration-plus-compression. The
second claim is unverified against primary sources.

PROBLEM STATEMENT. What is the state of library learning and abstraction discovery as of 2026?
Specifically: what metrics establish that a discovered abstraction is load-bearing rather than
cosmetic, and what ablation protocols are standard?

STATUS AND BOUNDS. We need the ABLATION protocol above all: our doctrine requires that a claimed
improvement disappear when the abstraction is removed.

LITERATURE. Primary, with dates, venues, and links to implementations.

ATTACK VECTORS. Look for compression metrics that reward verbosity in the baseline rather than
economy in the library; look for abstractions credited without a leave-one-out test.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT (random abstractions also compress somewhat — what is
the floor?). PATTERN_CONDUCTOR_CONFOUND (abstractions that pay only within one problem family).
```

### Prompt 05: Verifier-in-the-loop discovery systems (Canon Band G)

```
SUMMARY. Our ladder's top measured band is generative research: open-ended conjecture under
falsification. External systems reportedly achieve this with formal verification as the selector.

FLAGGED FINDINGS. We have shallowly verified that AlphaEvolve-class systems improved bounds on
combinatorial problems and that an AlphaProof-class system resolved many OEIS conjectures. We have
NOT verified per-problem human setup cost, the fraction of attempts producing anything, or whether
improvement means a new record versus a rediscovery.

PROBLEM STATEMENT. For each such system: what is the verified claim, what is the base rate of
success per problem attempted, how much problem-specific human engineering is required, and what
independent verification exists?

STATUS AND BOUNDS. We care about the ARCHITECTURE (mutation engine plus non-model selector), not
benchmark numbers.

LITERATURE. Primary: papers, technical reports, official methodology sections, and especially
independent replications.

ATTACK VECTORS. Separate genuine novelty from rediscovery of known results; find the denominator —
how many problems were attempted per reported success.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT (the denominator IS the finding here).
PATTERN_PRIME_GRAVITATIONAL_OVERFIT (systems that discover structure their generator was seeded
with).
```

### Prompt 06: Process supervision versus outcome supervision

```
SUMMARY. Prometheus's founding bet is that failure geometry — HOW an attempt failed, with position
and margin — is more trainable than pass or fail verdicts. The external analogue is process-reward
and RLVR literature.

FLAGGED FINDINGS. We believe process-level supervision beats outcome-only supervision by roughly
ten points on small models, and we treat this as the first external corroboration our thesis has
had. It is unpinned and we may be over-reading a narrow result.

PROBLEM STATEMENT. What does the primary literature establish about process versus outcome
supervision? Under what model scales, task families, and data volumes does the advantage hold, and
where does it vanish or reverse?

STATUS AND BOUNDS. Our local capacity ceiling is 1.5B to 4B parameters; results at that scale
matter most.

LITERATURE. Primary papers with experimental sections; note dataset sizes and annotation cost.

ATTACK VECTORS. Check whether the advantage survives when the outcome-only baseline receives an
equal annotation budget, and whether it is a data-volume effect in disguise.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT. PATTERN_VRAM_TRUNCATION_ARTIFACT (results appearing
only at scales we cannot run, reported as general).
```

### Prompt 07: Theory of mind as an epistemic instrument (Canon Band H1)

```
SUMMARY. Our hypothesized tier H1 defines a system that models its OWN failure distribution and
OTHER reasoners' failure distributions, and allocates search accordingly. We need to know whether
machine theory-of-mind work supplies a measurable version of this.

FLAGGED FINDINGS. We believe false-belief paradigms and machine theory-of-mind benchmarks measure
belief attribution but NOT failure-mode prediction, and that the latter is unexplored. That belief
is untested and may reflect only our ignorance.

PROBLEM STATEMENT. Is there primary work on predicting another system's or human's error
distribution on a task set, scored against actual errors? Related areas: solver portfolio
selection, algorithm selection, item-response theory applied to model populations.

STATUS AND BOUNDS. We need a promotion gate: a deterministic scoring rule that beats a base-rate
predictor.

LITERATURE. Primary, across machine learning, cognitive science, and psychometrics — the last may
be where the real instrument lives.

ATTACK VECTORS. Distinguish predicting THAT a solver fails from predicting HOW it fails; only the
second is what we need.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT (a predictor that learns only overall difficulty beats
nothing). PATTERN_CONDUCTOR_CONFOUND.
```

### Prompt 08: Quality-diversity and open-endedness (Canon Band H2)

```
SUMMARY. Our hypothesized tier H2 treats an accumulated failure corpus as a navigable manifold:
dense kill regions bound the empty corridors between them, and search is aimed at the enclosed
voids. Quality-diversity and open-endedness are the nearest external families.

FLAGGED FINDINGS. We believe archive-based methods and novelty search establish that abandoning
direct objectives can outperform pursuing them, supporting our posture that weak signals are
exploration threads. We have not verified where these methods FAIL.

PROBLEM STATEMENT. What is established about archive-based and quality-diversity search: which
problem structures does it beat objective-driven search on, and where does it lose? Critically: is
there any work navigating an archive of FAILURES rather than an archive of solutions?

STATUS AND BOUNDS. Our archive is failure-shaped, not solution-shaped; that asymmetry is the crux
of our thesis and we do not know whether it has precedent.

LITERATURE. Primary work in quality-diversity, novelty search, open-endedness, and curiosity as
compression progress.

ATTACK VECTORS. Find negative results — where these methods underperform, and why.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT. PATTERN_PRIME_GRAVITATIONAL_OVERFIT (archives whose
diversity axis is dominated by one trivial factor).
```

### Prompt 09: Certificate-checking versus decision procedures for novelty gating

```
SUMMARY. We derived internally that decision procedures cannot serve as novelty gates: where a
decision procedure terminates, everything true is already inside its closure, so nothing is ever
novel; outside that fragment it returns unknown. We concluded that finite computation and
CERTIFICATE-CHECKING (proof assistants) escape this, because they check a certificate for a proof
found elsewhere rather than deciding membership.

FLAGGED FINDINGS. This is our own reasoning with no external check. It may be a known result
stated better elsewhere, or it may be subtly wrong.

PROBLEM STATEMENT. Is there literature on the relationship between decidability and novelty or
informativeness in automated conjecture generation? What is the standard treatment of the claim
that a system found something new, in automated theorem proving and conjecture-making systems?

STATUS AND BOUNDS. We want either a formal statement of our claim or a refutation of it.

LITERATURE. Primary: automated conjecture generation, novelty metrics in automated theorem
proving, proof-assistant library-comparison methods.

ATTACK VECTORS. Try to falsify our claim directly: is there a decision procedure whose closure is
genuinely surprising relative to its axioms?

CROSS-REFERENCES. PATTERN_RANK_PARITY_LEAK. PATTERN_BASE_RATE_NEGLECT.
```

### Prompt 10: Anti-contamination benchmark construction

```
SUMMARY. Our capability instruments saturate against frontier models, and we suspect training-set
contamination in any published probe. Our internal answer is procedurally generated probes plus a
held-out set authored by an independent model family with executed checkers.

FLAGGED FINDINGS. We believe procedural generation plus executed verification suffices for
contamination resistance. This is unchecked against the benchmark-integrity literature.

PROBLEM STATEMENT. What are current best practices for constructing contamination-resistant
reasoning benchmarks? Specifically: detection methods for training-set leakage, canary protocols,
and evidence on whether procedural generation actually prevents memorization transfer.

STATUS AND BOUNDS. We need methods runnable offline with deterministic grading.

LITERATURE. Primary: contamination studies, canary-string work, dynamic benchmark generation.

ATTACK VECTORS. Look for evidence that procedurally generated probes STILL leak via template
memorization; that would falsify our current approach.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT. PATTERN_VRAM_TRUNCATION_ARTIFACT.
```

---

## WAVE 3 — decision-market bottleneck evidence

*Consumer for 11-16: `engine/queues/BOTTLENECKS.jsonl` — each report updates the confidence of a
named bottleneck hypothesis against the pre-registered observables in that file.*

### Prompt 11: Does failure-trace richness change downstream learnability?

```
SUMMARY. Our bottleneck hypothesis B-001 states that metabolization stalls because our failure
records are verdict-shaped (pass or fail plus a categorical label) rather than carrying position,
margin, and operation structure. Internal measurement found roughly five orders of magnitude more
operator-distinguishability in margin-space coordinates than in categorical labels.

FLAGGED FINDINGS. We believe rich coordinates are necessary for navigability. We may be
rationalizing: it is also possible that no coordinate scheme helps and our corpus is exhaust.

PROBLEM STATEMENT. What does the literature establish about the effect of error-representation
richness on downstream learning or retrieval? Search areas: error analysis in automated program
repair (localized break-step versus binary fail), curriculum learning from errors,
retrieval-augmented reasoning keyed on failure traces.

STATUS AND BOUNDS. Our records: roughly 413 million verdict-shaped rows, with the kill-vector
field zero percent populated.

LITERATURE. Primary, with effect sizes where reported.

ATTACK VECTORS. Find cases where richer error representation did NOT help — that is the
discriminating evidence.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT. PATTERN_CONDUCTOR_CONFOUND.
```

### Prompt 12: Semantic versus behavioral retrieval keys

```
SUMMARY. We measured that routing on semantic labels of failures is NULL — real fields performed no
better than shuffled fields — while behavioral co-solve clustering worked and survived an
adversarial tail check. We want to know whether this asymmetry is known.

FLAGGED FINDINGS. We treat behavioral-not-semantic as a hard posture based on one internal
experiment; it may not generalize.

PROBLEM STATEMENT. What is established about behavioral or functional similarity versus label or
semantic similarity as retrieval keys for tool selection, algorithm selection, or error-conditioned
routing?

STATUS AND BOUNDS. Cold-start, meaning no prior solve history, is the hard case for us and the one
that returned NULL.

LITERATURE. Primary: algorithm selection, collaborative-filtering cold-start, functional code
similarity.

ATTACK VECTORS. Find methods that solve cold-start routing WITHOUT prior co-solve data — if they
exist, our NULL was a design limitation, not a law.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT. PATTERN_RANK_PARITY_LEAK.
```

### Prompt 13: Syntactic dispatch as a hidden failure mode in verification systems

```
SUMMARY. We discovered that our verification battery dispatches on a surface identifier and returns
invalid rather than unknown for any unregistered claim shape — meaning it certifies true-but-novel
claims as FALSE. It fired this way 160 times out of 160 on our live grader.

FLAGGED FINDINGS. We believe a working semantic engine behind a syntactic router is a general
architectural failure mode, not a quirk of our code. That generalization is unsupported.

PROBLEM STATEMENT. Is there literature on dispatch or routing layers silently bounding the
capability of verification or reasoning systems? Related: soundness versus completeness tradeoffs
in practice, fails-closed versus fails-wrong design, type-directed dispatch limiting expressible
queries.

STATUS AND BOUNDS. We want both precedent and standard mitigations.

LITERATURE. Primary: software architecture, automated-theorem-prover system design, SMT solver
interfaces.

ATTACK VECTORS. Look for the opposite finding — systems where surface dispatch was measured as
harmless.

CROSS-REFERENCES. PATTERN_RANK_PARITY_LEAK. PATTERN_CONDUCTOR_CONFOUND.
```

### Prompt 14: Do generator upgrades convert to verified-artifact yield?

```
SUMMARY. Our bottleneck hypothesis B-003 asks whether generator quality is our ceiling. Our history
says no: an in-loop language-model mutation run produced 2,152 mutations with zero measured lift,
and supervised gains decomposed into format acquisition rather than reasoning.

FLAGGED FINDINGS. We believe frontier-model improvements do NOT convert into post-verification
survival gains without harness changes. This is a strong claim from limited evidence.

PROBLEM STATEMENT. Where a fixed verifier or fitness function is held constant and only the
generator is upgraded across model generations, what happens to the rate of verified-valid outputs?
Any study holding the selector constant across generator generations is relevant.

STATUS AND BOUNDS. The key control is the FROZEN selector; comparisons with a co-evolving evaluator
are uninformative to us.

LITERATURE. Primary: program synthesis, formal-methods pipelines, evolutionary systems with fixed
fitness.

ATTACK VECTORS. Find studies where generator upgrade alone produced large verified gains — that
would raise this hypothesis sharply.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT. PATTERN_PRIME_GRAVITATIONAL_OVERFIT.
```

### Prompt 15: Do multi-agent systems improve by restructuring themselves?

```
SUMMARY. We are designing a system whose heredity mechanism is ORGANIZATIONAL: a failure produces a
diagnosis, the diagnosis produces a specialized child agent, and the child causally improves the
parent's measured performance, verified by ablating the child's specialization.

FLAGGED FINDINGS. We believe this is buildable today and distinct from weight-level learning. We do
not know whether it has precedent or a known failure mode.

PROBLEM STATEMENT. What is established about multi-agent systems that MODIFY THEIR OWN ORGANIZATION
based on measured deficits? Include automated team and role design, agent-population methods with
structural mutation, and any work measuring whether specialization causally improves collective
performance under ablation.

STATUS AND BOUNDS. We require the ablation control; self-reported improvement is inadmissible.

LITERATURE. Primary: multi-agent reinforcement learning with population structure, organizational
search, self-organizing systems.

ATTACK VECTORS. Find the failure mode — where role proliferation degraded performance, and what
predicted it.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT (does adding ANY agent help equally?).
PATTERN_CONDUCTOR_CONFOUND.
```

### Prompt 16: Expected-information-gain experiment selection in practice

```
SUMMARY. Our decision market ranks candidate experiments by how many live hypotheses their outcome
would discriminate between, and scores each filer's predicted versus realized gain to build a
calibration track record.

FLAGGED FINDINGS. We believe discrimination count is a better ranking signal than estimated value,
and that filer calibration prevents the ranking from becoming an oracle. Untested.

PROBLEM STATEMENT. What does the literature establish about optimal experiment design, Bayesian
experimental design, and active learning applied to SCIENTIFIC hypothesis sets rather than model
parameters? Specifically: practical failures of expected-information-gain criteria.

STATUS AND BOUNDS. We need methods that work with roughly five to ten coarse hypotheses and noisy
cost estimates, not asymptotic theory.

LITERATURE. Primary: Bayesian experimental design, active learning, automated scientific discovery
systems with explicit hypothesis ledgers.

ATTACK VECTORS. Find documented pathologies of information-gain-driven selection: myopia,
cost-blindness, degenerate hypothesis sets.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT. PATTERN_RANK_PARITY_LEAK.
```

---

## WAVE 4 — instrument and infrastructure grounding

### Prompt 17: Calibration scoring for agent self-assessment

```
SUMMARY. Our ladder's calibration rung requires a system to report solved, probable, or
under-constrained and be right about it. We also plan to score our own agents' predictive
calibration on the decision market.

FLAGGED FINDINGS. We assume proper scoring rules transfer straightforwardly to agent
self-assessment. This is possibly naive.

PROBLEM STATEMENT. What are established methods and pitfalls for measuring calibration of reasoning
systems on mathematical or verifiable-answer tasks? Include proper scoring rules under small
samples, calibration under distribution shift, and resistance to gaming.

STATUS AND BOUNDS. Our sample sizes are in the tens — exactly where naive Brier scores mislead.

LITERATURE. Primary: forecasting and calibration literature, language-model calibration studies.

ATTACK VECTORS. Small-sample pathologies; how a system can appear calibrated while being useless.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT. PATTERN_VRAM_TRUNCATION_ARTIFACT.
```

### Prompt 18: Sandboxing model-generated code without containers

```
SUMMARY. We execute model-generated Python for experiments and have decided against containers on
our Windows hosts. Our plan is a dedicated virtual environment with a restricted working directory,
hard timeouts, an AST-based import screen, and an operating-system firewall rule blocking outbound
traffic from that interpreter.

FLAGGED FINDINGS. We believe this is adequate for OUR threat model — our own generated code, where
the risks are accidental network calls, runaway compute, and file damage rather than adversarial
escape.

PROBLEM STATEMENT. What are the known weaknesses of virtual-environment plus firewall plus
AST-screen sandboxing for Python, and what are the cheapest meaningful hardening steps short of
containerization?

STATUS AND BOUNDS. Windows hosts, no Hyper-V or WSL2, and it must stay simple enough to maintain.

LITERATURE. Primary: Python sandboxing analyses, AST-screen bypass techniques, operating-system
process restriction on Windows such as job objects, restricted tokens, and AppContainer.

ATTACK VECTORS. Enumerate concrete AST-screen bypasses; identify what a firewall rule does NOT stop.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT. PATTERN_RANK_PARITY_LEAK.
```

### Prompt 19: Postgres as coordination substrate for distributed agent work

```
SUMMARY. We coordinate multi-machine agent work through Postgres tables with lease-based claiming —
a worker takes a row with an expiry, and crashed workers' rows return to the pool — rather than a
message broker or daemon.

FLAGGED FINDINGS. We believe this is more robust than a broker at our scale (single-digit machines,
human-triggered sessions) because no coordinator process exists to die. We previously lost an
entire 43-daemon fleet to silent death.

PROBLEM STATEMENT. What are established patterns and pitfalls of Postgres-as-queue with lease
semantics? Include SKIP LOCKED, lease-expiry races, poison-item handling, and the scale at which
this pattern is known to break down.

STATUS AND BOUNDS. Postgres 17, single primary, tens of thousands of queue rows, not millions.

LITERATURE. Primary: Postgres queue implementations and documented production experience.

ATTACK VECTORS. Find the failure modes: duplicate execution under lease expiry, lock contention,
table bloat from high-churn queues.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT. PATTERN_CONDUCTOR_CONFOUND.
```

### Prompt 20: Retrodictive re-analysis — precedent and pitfalls

```
SUMMARY. We plan to re-analyze roughly 92,000 historical rejected results with a corrected
instrument, to estimate what fraction were instrument artifacts rather than genuine negatives. We
consider this stronger evidence than a fresh experiment because the archived data cannot be tuned
to fit.

FLAGGED FINDINGS. We believe retrodiction on frozen data is unusually strong evidence. It may
instead be unusually prone to a subtler bias we have not identified.

PROBLEM STATEMENT. What is the methodological literature on re-analyzing archived negative results
with a corrected instrument? Include precedent in any field, the standard controls, and the known
biases of retrospective re-analysis.

STATUS AND BOUNDS. Our archive was produced by the same team now re-analyzing it — that conflict is
our chief worry.

LITERATURE. Primary: methodology and meta-science; instrument-correction reanalyses in physics,
astronomy, or genomics.

ATTACK VECTORS. Identify how a re-analysis can manufacture apparent resurrections, and specify the
blinding or pre-registration that would prevent it.

CROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT. PATTERN_PRIME_GRAVITATIONAL_OVERFIT.
```

**Consumer for 17-20:** 17 feeds the ladder calibration-rung grader design and decision-market
filer calibration; 18 feeds the `engine/sdk` sandbox spec (the DECISION 1 replacement); 19 feeds
the `germline` queue-client build; 20 feeds M-004 protocol design, so pre-registration and blinding
are settled BEFORE the retrodiction runs.
