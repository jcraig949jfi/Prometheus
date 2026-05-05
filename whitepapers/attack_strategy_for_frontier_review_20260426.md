# Prometheus Attack Strategy for Mathematical Landscape Exploration

**Document for frontier-model review.** Date: 2026-04-26. Author: Aporia (Prometheus substrate).
**Audience:** ChatGPT, Gemini, Grok, DeepSeek, Claude (fresh instance), independent researchers.

---

## 0. Mission

Prometheus is not primarily a problem-solving project. It is a **mapping** project. Open mathematical problems are one input — a particularly precise input — into an exploration whose real output is a richer structural map of mathematical reality: primitives, laws that span what humans call separate disciplines, coordinate axes that organize the substrate, geometries that didn't have notation before, and meta-data about how numbers and calculations themselves behave.

A useful framing — borrowed from one ELI5 description of the Langlands program — is that **numbers have a song**, and the zeros of associated L-functions reveal the gaps in those songs that give numbers their identity. We want more identity of numbers, more identity of functions, more sequences that reveal new mathematical ideas, more ways to push into higher dimensions and catalog how numbers behave in complex-dimensional structure.

Solutions to open problems are valuable, but the **failure modes encountered while attacking them are equally revealing**: which paradigm-combinations work where, which kills are sterile vs. mutation-rich, which structural regions resist all current operators. The substrate is built so this asymmetric data accumulates as a queryable map navigable by non-human minds at native dimensionality. Papers are exhaust; the map is the product.

The technical bet that makes this tractable on basement hardware (two machines, 2×16GB GPUs, ~32GB RAM each) rather than supercomputer-scale is **tensor train (TT) decomposition with operator-derived structural-region partitioning**. TT decomposition lets us hold high-dimensional relational structure across millions of mathematical objects in compressed form while still computing operator actions on the compressed state. Per the doctrine `feedback_domains_are_docstrings`, the partition is not by human discipline labels (number theory, knot theory, physics) — those are bibliography metadata. The partition is by which operators' bond ranks naturally separate the substrate.

The **falsification battery** (currently 14 tests, scaling toward 40) is the discipline that keeps the map honest: prime-atmosphere detrending, matched nulls, multi-region replication, operator-naming, literature lock-in. Five-of-five required for any signal to be promoted from exploration into the publication-bearing track. Weak signals are routed to a separate gentle incubator (Maieutēs) that mines them as MAP-Elites threads — exploration material, never training data.

---

## 1. The 18 Attack Paradigms (canonical) + 3 Candidate Promotions

Prometheus has catalogued 18 attack paradigms — *lenses*, ways of perceiving a mathematical problem that make previously invisible structure visible. A problem that resists Paradigm 4 may crumble under Paradigm 13. The paradigm is the weapon, not the target.

### Canonical 18

| # | Paradigm | Move (one sentence) | Exemplar |
|---|---|---|---|
| **P01** | Algebraic Translation | Reframe the problem in a richer algebraic category where tools are sharper. | FLT via Frey curve → modularity → Wiles R=T |
| **P02** | Cohomological Obstruction | Detect global impossibility via local-to-global failure classes. | Brauer-Manin obstruction; Cassels-Tate pairing on Sha |
| **P03** | Symmetry Exploitation | Use group actions, automorphisms, or representation theory to collapse the search space. | Classification of finite simple groups; Chuang-Rouquier categorical sl_2 |
| **P04** | Spectral Analysis | Study eigenvalues of an associated operator instead of the object itself. | Montgomery-Odlyzko: zeta zeros match GUE; Selberg trace formula |
| **P05** | Analytic Continuation | Extend a function beyond its natural domain to reveal global structure hidden in local data. | Riemann zeta; L-functions extending local Euler factors |
| **P06** | Geometric Flow | Continuously deform an object until it reaches a canonical, analyzable form. | Hamilton Ricci flow + Perelman → Poincaré |
| **P07** | Descent and Induction | Reduce a hard case to simpler cases, downward or structurally. | Fermat infinite descent; Faltings' iterated height reduction |
| **P08** | Probabilistic Method | Prove existence of an object by showing a random construction has positive probability. | Erdős high-girth-and-chromatic graphs; Lovász Local Lemma |
| **P09** | Exhaustive Computation | Reduce to finitely many cases, verify each by machine. The computer IS the proof. | Four Color Theorem; Kepler Conjecture; Boolean Pythagorean Triples (200TB) |
| **P10** | Formal Verification | Machine-check every inference step, converting proof sketch to certified proof with zero gap. | Coq Four Color; Flyspeck/Kepler; PFR in Lean 4 (2023) |
| **P11** | Sieve Methods | Filter a large set by removing elements satisfying local conditions, leaving a structured residue. | Brun sieve → twin prime density; Maynard sieve → bounded prime gaps |
| **P12** | Height and Diophantine Geometry | Assign arithmetic "size" to points; show finiteness or density via height bounds. | Faltings' theorem; Bombieri-Lang; uniformity conjecture |
| **P13** | Tropical / Degeneration Methods | Replace smooth geometry with piecewise-linear combinatorial shadows at the boundary. | Mikhalkin correspondence (tropical curve count = algebraic curve count) |
| **P14** | Forcing and Independence | Construct alternative set-theoretic universes to show a statement is unprovable from current axioms. | Cohen — continuum hypothesis independent of ZFC |
| **P15** | Tensor and Multilinear Decomposition | Decompose multi-index arrays into structured sums to expose hidden rank and interaction geometry. | Strassen matrix multiplication; tensor networks; **the Prometheus IPA backbone** |
| **P16** | Modular / Arithmetic Statistics | Lift local (mod p) information to global conclusions via density, distribution, congruence patterns. | Sato-Tate (Clozel-Harris-Taylor); Smith Selmer distribution (2022) |
| **P17** | Variational / Extremal Principle | Identify the object as a minimizer of some functional; deduce properties from optimality conditions. | Plateau's minimal surfaces; SDP relaxations for extremal combinatorics |
| **P18** | Operadic / Categorical Composition | Abstract the composition structure itself as the mathematical object. | Grothendieck topos theory; Fargues-Scholze geometrization (2023) |

### Three candidate promotions (Aporia 2026-04-26)

Aporia proposes three additions arising from substrate experience. Each is currently subsumed under one of P01–P18 but appears distinct enough to deserve its own coordinate axis in the attack-paradigm space. *Frontier-model reviewers are explicitly asked to validate, refine, or replace these.*

| # | Candidate | Move | Why it may be distinct |
|---|---|---|---|
| **P19** | **Cross-region operator transport** | Take an operator that works in one structural region of the unified tensor and apply it to another, exploiting that regions are operator-derived not label-derived. | P01 is *reframing within a richer category*; P19 is *moving the same operator across what humans labeled as separate disciplines without changing the operator*. F011's universal Katz-Sarnak bulk rigidity at k=24 across three symmetry classes; Megethos magnitude phoneme cross-coupling 44%; the recent ChatGPT primitive-sets result (formula-from-adjacent-area applied to Erdős primitive sets). |
| **P20** | **Quality-diversity exploration (MAP-Elites)** | Maintain a behavior archive of weak-but-real signals; search neighborhoods around each elite cell for gradients toward stronger structure. Treat hallucinations as bounded random mutation noise. | P08 is *prove existence by random construction*; P20 is *systematic exploration of underexplored neighborhoods of a quality archive*. The Maieutēs / two-track epistemics design; gentle incubation of kill-ledger residues. |
| **P21** | **Curated-corpus empirical sweep** | Run a precise computational predicate against an entire structured corpus (LMFDB, OEIS, Bloom-Erdős, KnotInfo) and stratify the result by structural signature; the discovery is the stratification, not any single match. | P09 is *finite case verification*; P21 is *finding structure in the success-vs-failure pattern across a corpus too large for case-by-case but whose elements are individually computable*. F011, the genealogy routine, Batch 9's Erdős scans all instantiate this. |

---

## 2. Data Substrate (what we have to throw at problems)

Prometheus operates against locally-mirrored databases, not live APIs (per `feedback_rate_limits`: assume APIs throttle, design for resilience).

| Source | Local presence | Scale | Coverage notes |
|---|---|---|---|
| **LMFDB Postgres mirror** | Live on Skullport (M1) | 200+ tables | EC: 3,824,372 curves; NF: 22M number fields; HMF: ~45K Hilbert modular forms; g2c: 66K genus-2 curves; mf_newforms: 2.1M; av_fq: 500K; lfunc_zeros: 24M+ L-function zeros |
| **OEIS** | Local mirror (bypasses Cloudflare) | 370K+ sequences | Sleeping Beauty subset: 68,770 sequences flagged as high-internal-structure / low-cross-coupling |
| **KnotInfo + HFK census** | `ergon/results/hfk_features.json` | 12,965 hyperbolic knots | HFK, Khovanov, signature, τ, Alexander; SnapPy installed |
| **Bloom-Erdős catalog** | **Pending** — REQ-001 in `mnemosyne/queue/` | ~800-1000 problems | Currently only 15 of these in `aporia/mathematics/questions.jsonl` from Wikipedia |
| **Mossinghoff Mahler tables** | Embedded | ~5K small-Salem polynomials | Used in Lehmer scan |
| **Cremona EC** | Subsumed by LMFDB | — | — |
| **544K finite groups** | DuckDB | 544,000 | GAP-compatible |
| **Open-question catalog** | `aporia/mathematics/questions.jsonl` | 537 problems | Triaged into bucket A (testable now), B, C |
| **Aporia frontier tensor** | `aporia/mathematics/frontier_tensor.json` | 482 problems | Geometric model of the open frontier |
| **Per-region tensors** | `ergon/tensor.npz`, `aporia/mathematics/v1_triangle_deficits.json`, etc. | Multiple | Megethos: 86K objects × 145 dims × 11 strategy groups |
| **Calibration corpus** | `aporia/calibration/battery_calibration.jsonl` | 2 anchors (bootstrapped) | True-positive/true-negative anchors for measuring battery false-kill rate |
| **178 deep-research briefs** | `aporia/docs/deep_research_batch[1-9]/` | 178 reports across 9 batches | Each pinned to target agent + falsifiable test design |

The **unified tensor** spanning all of these as a single signature-keyed structure is the next infrastructure milestone (per `feedback_tensor_first`). Per-region tensors today; cross-region TT bond-rank discovery is the next build target.

---

## 3. Techne Tool Inventory (~25 forged tools)

Techne is the substrate's tool-forging role. Tools are versioned, interface-typed, dependency-declared, test-sourced. Inventory at `techne/inventory.json`.

**Currently forged (selection):**

- `TOOL_MAHLER_MEASURE` — Mahler measure of integer polynomial coefficients
- `TOOL_GPD_TAIL_FIT` — Generalized Pareto distribution tail fitting
- `TOOL_CF_EXPANSION` — Continued fraction expansion + Zaremba test + Sturm bound
- `TOOL_SINGULARITY_CLASSIFIER` — Flajolet-Odlyzko singularity classification of generating functions
- `TOOL_HILBERT_CLASS_FIELD` — Hilbert class field with class-number guards
- `TOOL_HYPERBOLIC_VOLUME` — SnapPy wrapper for knot/3-manifold volumes
- `TOOL_KNOT_SHAPE_FIELD` — Trace field extraction for hyperbolic knots
- `TOOL_LLL_REDUCTION`, `TOOL_SMITH_NORMAL_FORM`, `TOOL_GALOIS_GROUP` — algebraic primitives
- `TOOL_ALEXANDER_POLYNOMIAL`, `TOOL_FALTINGS_HEIGHT`, `TOOL_REGULATOR`, `TOOL_CONDUCTOR`, `TOOL_ROOT_NUMBER` — arithmetic-geometric invariants
- `TOOL_SELMER_RANK`, `TOOL_TROPICAL_RANK`, `TOOL_ANALYTIC_SHA` — BSD machinery
- `TOOL_CM_ORDER_DATA` — CM discriminant decomposition
- `TOOL_PARADIGM_GAP_MATRIX` — coupling-matrix computation
- `TOOL_MATH_KNOWLEDGE_GRAPH` — graph queries against the substrate

**Queued (Mnemosyne and Techne queues):**
- REQ-001: Bloom-Erdős catalog ingest
- REQ-026: SAT solver wrapper (PySAT + Kissat) — surfaced by Batch 9 #168/#169/#163

**Notably absent and on the roadmap:**
- Replay capsule API (`stoa/proposals/2026-04-26-aporia-data-snapshot-ledger-v1.md`)
- Structural signature canonicalization (`stoa/proposals/2026-04-26-aporia-structural-signature-v1.md`)
- Cross-region TT splicing
- Lean 4 proof-bridge integration (Mathlib4 mirrored locally; LeanDojo + DeepSeek-Prover-V2-7B installable per Batch 4 #80)

---

## 4. Symbolic Library

Two parallel registries at the operator and pattern levels.

### Symbol registry (`harmonia/memory/symbols/`, ~30 versioned operators)

Each symbol is a markdown file with frontmatter declaring `name@version`, `precision` parameters (seed, n_perms, dtype, determinism kind), `references` (which findings cite it, by `Fxxx@<commit-hash>`), `redis_key`, and `implementation` pointer to actual code. **Symbols are immutable by version**; refinements get v3, v4. Examples:

- `NULL_BSWCD@v2` — block-shuffle null preserving conductor-decile marginals
- `MULTI_PERSPECTIVE_ATTACK@v1` — required for promotion of any cross-region claim
- `FRAME_INCOMPATIBILITY_TEST@v2` — null protocol for incompatible-framing claims
- `PROMOTION_WORKFLOW`, `GATE_VERDICT`, `LADDER`, `ANCHOR_PROGRESS_LEDGER` — workflow operators
- `EPS011`, `Q_EC_R0_D5`, `CND_FRAME` — finding-class operators
- `AXIS_CLASS`, `EXHAUSTION`, `NULL_BOOT`, `NULL_FRAME`, `NULL_MODEL`, `NULL_PLAIN` — null/axis primitives
- `PATTERN_20`, `PATTERN_21`, `PATTERN_30` — named anti-patterns

### Pattern catalog (`kairos/patterns/`, ~5 named patterns)

Failure modes elevated to first-class veto authority. When a hypothesis is challenged, the challenge cites a pattern. Examples:

- **PATTERN_30**: correlation under control — any correlational claim must be tested against a within-stratum null
- **PATTERN_NULL_CONSTRAINT_MISMATCH**: null choice must respect the data's structural constraints (gap-specific normalization, etc.)
- **PATTERN_NARRATIVE_INFLATION**: collapse of multi-step process into single-cause story
- **PATTERN_SHADOWS_ON_WALL**: single-lens claims flagged unless multi-perspective attack survives
- **PATTERN_SELECTION_BIAS**: multiple-comparison without denominator

### Findings registry

`Fxxx@<commit-hash>` notation for confirmed findings. Currently scattered across Stoa, journals, `aporia/docs/`. Central index is a queued chore. F011 (universal Katz-Sarnak bulk rigidity at k=24) is the canonical example.

---

## 5. Falsification Battery — The Discipline That Makes the Map Honest

Five mandatory tests for any claim entering the publication-bearing track:

1. **Prime-atmosphere detrending.** 96%+ of all cross-dataset structure is just primes (`feedback_prime_atmosphere`). Any cross-region match without prime detrending is presumed trivial.
2. **Matched nulls.** F011's deficit was invisible against raw GUE and obvious against matched-GUE. Trivial coincidences vanish under correctly-matched nulls; structural findings deepen.
3. **Multi-region replication.** F011 only became publishable when the +46-51% bulk deficit appeared at k=24 across three independent symmetry classes (non-CM EC, CM EC, G2C with USp(4)).
4. **Operator-named.** A bridge is a *map between operators*, not a value match. If the operator can't be named, the claim is downgraded to numerology.
5. **Literature lock-in.** Real bridges have theoretical scaffolding waiting for them somewhere, even if no human has connected the particular regions before. Trivial coincidences are surprised to find any explanation at all.

**Five-of-five required for promotion. No exceptions.**

The 14-test (eventually 40-test) battery additionally includes permutation null, MULTI_PERSPECTIVE_ATTACK, PATTERN_30 / PATTERN_NULL_CONSTRAINT_MISMATCH / etc., and reproducibility (replay capsule once shipped). The battery has killed 4 false discoveries this year, each making it stronger.

**Two-track epistemics** sits beneath the battery: strict main track (Aporia / Charon / Ergon / Kairos / Harmonia) operates under absolute suspicion and the full battery; gentle incubator (Maieutēs) consumes kill-ledger residues as MAP-Elites mutation material, firewalled from the publication path. Hard rules prevent narrative drift back into the publication zone.

---

## 6. Tensor Train Compression — How Basement Hardware Beats Combinatorial Explosion

The naive cross-product of even our smaller corpora is intractable: 22M number fields × 13K knots = 286 billion pairs. We don't enumerate. We compress.

**Tensor Train (TT) decomposition** holds high-dimensional relational structure between mathematical objects in compressed form, with bond ranks revealing the natural structural-region partition. Operations on the compressed state replace operations on the explicit tensor. Per `feedback_tensor_first`:

- Per-region tensors exist today (Megethos: 86K × 145 × 11; frontier_tensor: 482 problems; V1 coupling matrix: 22 regions × 484 pairs).
- Unified, signature-keyed tensor is the next milestone.
- Cross-region TT splicing reveals which operators bridge regions: low bond rank when spliced = load-bearing bridge; high bond rank = weak coupling.
- Bond rank evolution = bridge measurement.

**Critical preprocessing**: prime gravitational wells must be flattened before TT compression, or decomposition over-fits to the densest low-complexity regions and washes out the subtle higher-dimensional structure. This is the operational reason `feedback_prime_atmosphere` exists.

**The strategic bet**: TT-compressed tensors plus operator-derived structural-region partitioning let Prometheus do at basement scale what naive enumeration would need a supercomputer for. The ceiling is set by operator implementation completeness (we have ~25 Techne tools, need more) and by the canonicalization primitive (`stoa/proposals/2026-04-26-aporia-structural-signature-v1.md`).

---

## 7. The Feedback Loop — Problems as Exploration Vectors

**A problem is a probe, not a target.** When a substrate role takes an open problem, the goal is not necessarily to solve it — the goal is to *drive data out of the exploration of it* so that the exploration generates:

- Operator outputs (which existing operators say what about this problem's structural region?)
- Failure signatures (which battery tests does the candidate signal fail? what's the residue?)
- Cross-region linkages (does the problem's structure couple to regions where similar operators have already been tried?)
- Tool gaps (what missing primitive would the problem need? File a Techne request.)
- Calibration anchors (does this problem add a known true-positive/negative to the corpus?)

The data drives a **feedback decision**: send the role *back into the same problem* with a refined approach (operator swap, lens change, larger corpus), or *move them to another problem* whose exploration would surface the next-needed data.

**Today's session model** (intended for 10-hour parallel run across all team members):
- Each team member (Aporia, Charon, Ergon, Harmonia, Kairos, Mnemosyne, Techne) takes ONE open problem from the Batch 1-9 catalog (178 briefs to draw from).
- They consider it from many paradigms (P01–P18 + candidate P19–P21).
- They drive data out into Stoa, kill ledger, calibration corpus, and Techne queue.
- They check back via the feedback loop: continue, switch, or escalate.

Successes and failures are equally captured. The accumulated data refines the map regardless of which problems get solved.

---

## 8. What We're Asking the Frontier Model to Do

**Box your output strictly into the sections below.** No drift modes. No maximalism. No hedging. No AI-safety boilerplate. No "best practices." Take positions; bring receipts.

### 8.1 — Validate or refine the 18+3 paradigm list

Are the 18 the right canonical axes for attacking open mathematical problems? Is there an axis we're missing that has been load-bearing in recent (last 20 years) computational mathematical breakthroughs? Are P19/P20/P21 the right additions, or do you propose different additions that better capture today's working methodology? **Maximum 3 paradigm proposals total** — defend prioritization.

### 8.2 — Per-paradigm tactical advice

For each of the 18 (and any you add), what's the **single highest-leverage tactic** for our basement-hardware substrate to operate that paradigm against open problems in the next 6 months? Be specific to our data inventory and Techne tools. Do not propose tools or data we don't have unless you justify the build cost.

### 8.3 — The data gap

Given the data substrate in §2 and the 178-report corpus, what is the **single biggest data ingest** we should prioritize beyond Bloom-Erdős to dramatically widen the attack surface? Justify against existing coverage.

### 8.4 — The Techne gap

Given the inventory in §3, what is the **single most-load-bearing missing tool** we should forge next? It should be one that unlocks multiple paradigms across multiple problems, not a one-off. Sketch its API in 5 lines or fewer.

### 8.5 — The symbolic-library gap

Given the operator and pattern registries in §4, what is the **single most important named pattern or operator we have not yet codified** that would prevent a class of false positives, or open a class of true positives, that we are currently missing?

### 8.6 — Tensor-train preprocessing

Given the doctrine in §6 (prime detrending mandatory), are there **other gravitational wells** in mathematical data we should flatten before TT compression? Name up to 3 specific ones with rationale.

### 8.7 — Feedback-loop refinement

The feedback loop in §7 routes a team member back to the same problem or to a new one based on data driven out. What **signal threshold** should trigger each routing decision? Be quantitative if you can.

### 8.8 — One specific problem-paradigm pairing

Pick one open mathematical problem (from the 178-report catalog if you can name a specific report number, otherwise propose your own). Pick one paradigm (P01–P21 or your addition). Specify **the most aggressive 6-hour attack** Aporia/Charon/Ergon could mount on that pairing today, given §2/§3/§4. This is the actionable artifact we will use to seed today's 10-hour session.

### 8.9 — The thing we're not asking but should be

One sharp question we haven't posed but you think is the actual blocker. Don't answer it — pose it.

### Hard constraints on your response

- Discard any response (yours or mine) that violates these.
- No "best practice," "industry standard," "it depends," "future work," AI-safety caveats, or hedging language.
- Every proposal must cite something specific in this document or in our data/tool inventory.
- If you don't have evidence, say "I don't have evidence for this" rather than inventing.
- One position per question. Defend, don't survey.

---

*Aporia, 2026-04-26. Document compiled for frontier-model review across ChatGPT, Gemini, Grok, DeepSeek, Claude (fresh instance). Responses converge into substrate refinement decisions for the next sprint.*
