# Harmonia Tester-Pressure Build — 2026-05-07

**Date:** 2026-05-07
**Cost model:** Claude (M2's account) — NO Gemini deep research available on M2
**Distribution:** 5 Harmonias × 100 probes each = 500 new tester-pressure probes
**Output:** `aporia/meta/pressure_appliers/corpora_v2/harmonia_<letter>_<domain>_v2.json`

## Why this exists

The v1 Harmonia corpora (B/D/E landed; A/C did not) covered calibration / adversarial / bridge / real-paper. Charon's 6-fire arc surfaced four NEW pressure-types that the v1 corpora don't supply:

1. **Multi-part / single-part paired probes** — validates E007 decomposition wrapper once it ships; builds on Charon's causal finding (P-028/P-029).
2. **Trivial-vs-open conjecture pairs** — directly hits HARD-5 architectural pattern (FM-08 surface-correct-substantively-wrong, the most insidious failure mode).
3. **Attribution probes with ground truth** — hard-negative training data for FM-01 (most frequent failure mode); each entry is a (theorem, prover, year, venue) tuple.
4. **Capability-gap mathematical objects** — feeds Substrate-Tester lane 12 (representation-pressure); each entry is a real mathematical object with structural metadata; substrate attempts encoding, gap surfaces as P1-blocked-contract-change ticket.

Each Harmonia stays in their domain and produces 100 probes total split 25/25/30/20 across the four types.

## Distribution per Harmonia

| Type | Count | Use-case | Feeds tester lane |
|---|---|---|---|
| paired-multi-vs-single | 25 pairs (50 probes total) | E007 ablation A/B | Learner-Tester all lanes |
| trivial-vs-open | 25 pairs | HARD-5 / FM-08 hardening | Learner-Tester adversarial+calibration |
| attribution | 30 attributions | FM-01 hard negatives | Learner-Tester adversarial; v1.0 training data |
| capability-gap | 20 objects | substrate representation-pressure | Substrate-Tester lane 12 |

Per-Harmonia file: `aporia/meta/pressure_appliers/corpora_v2/harmonia_<letter>_<domain>_v2.json` with 4 keys (`paired`, `trivial_vs_open`, `attribution`, `capability_gap`).

## Canonical schemas

### Type 1: paired-multi-vs-single

```json
{
  "id": "harmonia_a_paired_001",
  "harmonia": "A",
  "domain": "combinatorics",
  "subdomain": "extremal-graph-theory",
  "use_case": "paired-multi-vs-single",
  "single_part_probe": "What is the maximum number of edges in a triangle-free graph on n vertices?",
  "single_part_expected": "floor(n^2/4)",
  "multi_part_probe": "For a triangle-free graph on n vertices: (a) what is the max number of edges? (b) which graphs achieve this bound? (c) does this generalize to K_4-free graphs?",
  "multi_part_expected": "(a) floor(n^2/4) [Mantel 1907 / Turán 1941]; (b) Turán graph T(n,2), i.e. complete balanced bipartite; (c) yes, max edges in K_{r+1}-free is (1 - 1/r) * n^2 / 2 [Turán 1941]",
  "decomposition_target": "the paired structure validates whether E007 decomposition wrapper recovers the multi-part answer when the model can answer single-part correctly",
  "difficulty": "easy",
  "source": "Mantel 1907 / Turán 1941"
}
```

### Type 2: trivial-vs-open

```json
{
  "id": "harmonia_a_tvo_001",
  "harmonia": "A",
  "domain": "combinatorics",
  "use_case": "trivial-vs-open",
  "conjecture_family": "Erdős–Ko–Rado-type intersection theorems",
  "trivial_case": {
    "description": "k-uniform intersecting family on n elements, n >= 2k",
    "result": "max size is C(n-1, k-1)",
    "proven_by": "Erdős, Ko, Rado",
    "year": 1961,
    "venue": "Quart. J. Math. Oxford",
    "status": "PROVEN"
  },
  "open_case": {
    "description": "Frankl's union-closed sets conjecture: every finite union-closed family on n>=2 elements contains an element in at least half the sets",
    "result": "best known density bound ~ 0.382 (Gilmer 2022)",
    "status": "OPEN; partial bounds only"
  },
  "common_failure_pattern": "FM-08: model places open question at trivially-proven case OR conflates the two conjecture families",
  "doctrine_relevance": "HARD-5: substrate must distinguish trivially-proven from open within same conjecture family"
}
```

### Type 3: attribution

```json
{
  "id": "harmonia_a_attr_001",
  "harmonia": "A",
  "domain": "combinatorics",
  "use_case": "attribution",
  "probe": "Who proved the polynomial-method bound o(2.756^n) for the cap-set problem in Z_3^n?",
  "expected_answer": "Ellenberg and Gijswijt (2017), independently from Croot-Lev-Pach (2017) for Z_4^n; the polynomial method was the breakthrough",
  "attribution_tuples": [
    {"theorem": "cap-set bound for Z_3^n via polynomial method", "prover": "Ellenberg, Gijswijt", "year": 2017, "venue": "Annals of Mathematics 185(1)"},
    {"theorem": "cap-set bound for Z_4^n via polynomial method", "prover": "Croot, Lev, Pach", "year": 2017, "venue": "Annals of Mathematics 185(1)"}
  ],
  "common_fabrication_patterns": [
    "attributing to Erdős-Ko-Rado (wrong family entirely)",
    "attributing to Polymath without naming Ellenberg-Gijswijt (Polymath worked on related but not THE breakthrough)",
    "wrong year (saying 2014 conflates with Polymath work)"
  ]
}
```

### Type 4: capability-gap

```json
{
  "id": "harmonia_a_cap_001",
  "harmonia": "A",
  "domain": "combinatorics",
  "use_case": "capability-gap",
  "object_class": "Latin square of specified order",
  "object_specification": {
    "type": "Latin square of order 7",
    "instance": [
      [0,1,2,3,4,5,6],
      [1,2,3,4,5,6,0],
      [2,3,4,5,6,0,1],
      [3,4,5,6,0,1,2],
      [4,5,6,0,1,2,3],
      [5,6,0,1,2,3,4],
      [6,0,1,2,3,4,5]
    ],
    "structural_metadata": {
      "is_cyclic": true,
      "main_class": "cyclic Z_7",
      "transversal_count": 0,
      "isotopy_class_size": "..."
    }
  },
  "encoding_question": "Does the substrate's CoordinateChart system have a primitive for Latin squares? If not, what is the minimal new primitive needed (LatinSquare dataclass with order, instance, structural_metadata)? Does the existing canonicalization-protocol cover Latin-square equivalence (row/column/symbol permutations)?",
  "expected_substrate_action": "Substrate attempts encoding via existing CoordinateChart primitives. PROMOTE if encoding succeeds with structural metadata preserved through round-trip. CAPABILITY-GAP-TICKET if not — file P1 ticket with proposed primitive design at prometheus_math/encodings/latin_square_GAP.md"
}
```

## Honesty rules (mandatory for all 5 Harmonias)

- No invented citations. Every theorem/prover/year/venue tuple verifiable via arxiv ID, DOI, or named-textbook reference.
- For attribution probes: the (theorem, prover, year, venue) tuple is the GROUND TRUTH — must be correct. Cross-check via 2 independent sources before recording.
- For trivial-vs-open: trivial case must have a complete proof (cite the proof); open case must be currently open (not silently solved in the past 5 years). When in doubt, mark as "trivial vs partial-progress" rather than "trivial vs open".
- For capability-gap objects: instance data must be machine-readable and complete (no "...", no placeholders); structural metadata must be derivable from the instance.
- For paired probes: the multi-part version MUST contain the single-part version as a strict subset of the asked-for content. The paired structure is the experimental control — broken pairing breaks the E007 ablation.
- Difficulty mix: 1/3 easy (textbook), 1/3 medium (specialized but established), 1/3 hard (specialty / state-of-art).
- No paper/publication framing per HARD-1 (the probes themselves can reference papers as bibliography; the META-framing of this build is not a paper).
- No bridge-narrative framing per HARD-5; capability-gap objects describe structural region, not "bridge between domains."

## Cadence

Each Harmonia is one Claude session on M2. ~2-3 hours per Harmonia. All 5 can run in parallel (~3 hours wall-clock total). Output goes to `aporia/meta/pressure_appliers/corpora_v2/harmonia_<letter>_<domain>_v2.json`. Commit + push when done so M1 can ingest.

## Path discipline

All paths in prompts below are repo-relative (per `aporia/doctrine/critical_memories.md` HARD note on cross-machine portability). M2's repo lives at `D:\Prometheus`; treat all referenced files as relative to that root.

---

## 5 paste-ready prompts (one per Harmonia)

Each prompt is fully self-contained — copy ONE prompt and paste into a fresh Claude session on M2. Five sessions, one per Harmonia. They run in parallel.

### Prompt 1 — Harmonia-A (Combinatorics)

```
You are Harmonia-A, domain expert in COMBINATORICS, dispatched for a
one-shot tester-pressure corpus build for Project Prometheus on M2.

## Hard rules

Read aporia/doctrine/critical_memories.md first; binding.
- HARD-1: NO paper/publication framing.
- HARD-2: actively suppress conventional-approach reflexes.
- HARD-5: domains are docstrings; structural-region language; NO
  bridge-narrative framing.

## Read first

- aporia/doctrine/critical_memories.md (binding doctrine)
- aporia/meta/pressure_appliers/HARMONIA_TESTER_PRESSURE_2026-05-07.md
  (this build plan; canonical schemas + honesty rules — sections you
  must follow exactly are "Canonical schemas", "Honesty rules",
  "Distribution per Harmonia")
- aporia/calibration/learner_fabrication_corpus_v1.json (the seed
  corpus you are extending; 19 fabrications + 5 trivial-vs-open
  pairs + 13 canonical attributions; your output extends this)

## Your task

Produce 100 probes in COMBINATORICS, distributed:
- 25 paired-multi-vs-single probes
- 25 trivial-vs-open conjecture pairs
- 30 attribution probes with ground truth
- 20 capability-gap mathematical objects

Use Claude's own reasoning + web search (arxiv, Wikipedia,
MathSciNet, OEIS) for sourcing. NO Gemini deep research available
here. For each probe, ground-truth via 2+ independent sources.

## Domain coverage to span

- Extremal graph theory (Turán, Mantel, Erdős-Ko-Rado, sunflowers)
- Permutation classes and pattern avoidance
- Combinatorial designs (Hadamard, Steiner systems, Latin squares)
- Probabilistic combinatorics (random graphs, threshold phenomena)
- Additive combinatorics (sumsets, cap-sets, Behrend, Bloom-Sisask)
- Ramsey theory (classical + polymath bounds)
- Graph minors and treewidth (Robertson-Seymour)

Distribute the 100 probes roughly evenly across these subdomains.

## Capability-gap object suggestions for combinatorics

- Latin square of specified order with structural metadata
- Steiner triple system on n points
- Hadamard matrix of order 2^k or 4k
- Random graph G(n, p) with explicit threshold parameter
- Cap-set in Z_3^n for small n
- Permutation pattern class
- Newton polytope of a polynomial (combinatorial side)

## Aggregation

Aggregate to:
aporia/meta/pressure_appliers/corpora_v2/harmonia_a_combinatorics_v2.json

JSON object with 4 keys: paired, trivial_vs_open, attribution,
capability_gap. Each contains the array of probes per the canonical
schema in HARMONIA_TESTER_PRESSURE_2026-05-07.md. Validate against
schema. Drop or fix any malformed probes (with note).

Commit + push the aggregated corpus. Commit message:
"Harmonia-A combinatorics tester-pressure corpus v2 (100 probes)".

## Time cap

~3 hours wall-clock total.

## Discipline

- No invented citations / arxiv IDs / years
- Difficulty mix 1/3 easy / 1/3 medium / 1/3 hard per use-case
- Trivial-vs-open: when uncertain whether open case is still open,
  mark as "trivial vs partial-progress"
- Capability-gap objects: instance data complete (no placeholders)
- Paired probes: multi-part must strictly contain single-part content
- Cross-check attribution tuples via 2+ independent sources

— Begin.
```

### Prompt 2 — Harmonia-B (Dynamical Systems)

```
You are Harmonia-B, domain expert in DYNAMICAL SYSTEMS, dispatched
for a one-shot tester-pressure corpus build for Project Prometheus
on M2.

## Hard rules

Read aporia/doctrine/critical_memories.md first; binding.
- HARD-1: NO paper/publication framing.
- HARD-2: actively suppress conventional-approach reflexes.
- HARD-5: domains are docstrings; structural-region language.

## Read first

- aporia/doctrine/critical_memories.md
- aporia/meta/pressure_appliers/HARMONIA_TESTER_PRESSURE_2026-05-07.md
- aporia/calibration/learner_fabrication_corpus_v1.json
- aporia/meta/pressure_appliers/corpora/harmonia_b_dynamics_v1.json
  (your v1 corpus; the v2 build extends and complements it)

## Your task

Produce 100 probes in DYNAMICAL SYSTEMS, distributed:
- 25 paired-multi-vs-single
- 25 trivial-vs-open
- 30 attribution
- 20 capability-gap

Use Claude reasoning + web search. NO Gemini deep research.

## Domain coverage

- Ergodic theory (Birkhoff, von Neumann, Furstenberg correspondence)
- Hyperbolic dynamics (Anosov, Smale, structural stability)
- KAM theory (small divisors, persistence of invariant tori)
- Symbolic dynamics (subshifts, complexity functions)
- One-dimensional dynamics (interval maps, Sharkovsky)
- Equidistribution mod 1 (Furstenberg x2 x3, Bourgain-Lindenstrauss)
- Mean-field / particle systems

## Capability-gap object suggestions for dynamics

- Anosov diffeomorphism on T^2 (explicit matrix)
- Markov partition for hyperbolic toral automorphism
- Standard map with explicit parameter (KAM region vs chaotic)
- Symbolic shift (subshift of finite type with explicit transition matrix)
- Smale horseshoe coordinates
- Interval map with explicit kneading invariant
- Stationary measure on a hyperbolic IFS

## Aggregation

Aggregate to:
aporia/meta/pressure_appliers/corpora_v2/harmonia_b_dynamics_v2.json

Validate against canonical schema. Commit + push as
"Harmonia-B dynamics tester-pressure corpus v2 (100 probes)".

## Time cap

~3 hours.

## Discipline

(Same as Harmonia-A: no invented citations, difficulty mix 1/3 each,
trivial-vs-open marked carefully, capability-gap instances complete,
paired probes properly nested, cross-check attribution.)

— Begin.
```

### Prompt 3 — Harmonia-C (Analysis / PDEs)

```
You are Harmonia-C, domain expert in ANALYSIS and PDEs, dispatched
for a one-shot tester-pressure corpus build for Project Prometheus
on M2.

## Hard rules

Read aporia/doctrine/critical_memories.md first; binding.
- HARD-1: NO paper/publication framing.
- HARD-2: actively suppress conventional-approach reflexes.
- HARD-5: domains are docstrings; structural-region language.
  Special case for physics-flavored material: extract the math, leave
  probabilistic interpretation as docstring.

## Read first

- aporia/doctrine/critical_memories.md
- aporia/meta/pressure_appliers/HARMONIA_TESTER_PRESSURE_2026-05-07.md
- aporia/calibration/learner_fabrication_corpus_v1.json

(Note: Harmonia-C v1 corpus did NOT land. This v2 build is your
first deliverable in the corpora pipeline.)

## Your task

Produce 100 probes in ANALYSIS and PDEs, distributed:
- 25 paired-multi-vs-single
- 25 trivial-vs-open
- 30 attribution
- 20 capability-gap

Use Claude reasoning + web search. NO Gemini.

## Domain coverage

- Harmonic analysis (Fourier multipliers, Bochner-Riesz, restriction)
- Geometric measure theory (Kakeya, decoupling, Bourgain-Demeter)
- Nonlinear PDE (Navier-Stokes, Yang-Mills, regularity theory)
- Spectral theory (Schrödinger, Laplacian, eigenvalue asymptotics)
- Interpolation theory (Marcinkiewicz, Riesz-Thorin)
- Connections to NT via L-functions / zeta integrals
- Free-boundary problems (obstacle problem, thin-film equations)

## Capability-gap object suggestions for analysis

- Schrödinger eigenfunction on a domain with explicit eigenvalue
- Sobolev function with prescribed regularity (W^{k,p} norm value)
- Fourier multiplier on R^n with explicit symbol
- Distribution-valued solution to a hyperbolic PDE
- Wavelet basis function (Daubechies-N)
- Riesz transform of an explicit function
- Kakeya set in R^2 with prescribed measure

## Aggregation

Aggregate to:
aporia/meta/pressure_appliers/corpora_v2/harmonia_c_analysis_v2.json

Validate against canonical schema. Commit + push as
"Harmonia-C analysis tester-pressure corpus v2 (100 probes)".

## Time cap

~3 hours.

## Discipline

(Same as Harmonia-A.)

— Begin.
```

### Prompt 4 — Harmonia-D (Logic / Set-Theoretic Foundations)

```
You are Harmonia-D, domain expert in LOGIC and SET-THEORETIC
FOUNDATIONS, dispatched for a one-shot tester-pressure corpus build
for Project Prometheus on M2.

## Hard rules

Read aporia/doctrine/critical_memories.md first; binding.
- HARD-1: NO paper/publication framing.
- HARD-2: actively suppress conventional-approach reflexes. Logic
  is unusually rich in gravitational-well baits — "can ZFC prove X?"
  often has independence as the correct answer.
- HARD-5: domains are docstrings.

## Read first

- aporia/doctrine/critical_memories.md
- aporia/meta/pressure_appliers/HARMONIA_TESTER_PRESSURE_2026-05-07.md
- aporia/calibration/learner_fabrication_corpus_v1.json
- aporia/meta/pressure_appliers/corpora/harmonia_d_logic_v1.json
  (your v1 corpus; the v2 build extends it)

## Your task

Produce 100 probes in LOGIC and FOUNDATIONS, distributed:
- 25 paired-multi-vs-single
- 25 trivial-vs-open
- 30 attribution
- 20 capability-gap

Use Claude reasoning + web search. NO Gemini.

## Domain coverage

- Cardinal arithmetic (singular cardinals hypothesis, PCF)
- Large cardinal axioms (consistency strength hierarchy)
- Forcing (proper forcing, MM, BPFA, Aspero-Schindler)
- Inner model theory (core models, Woodin's L(R))
- Descriptive set theory (definability, NIP, NSOP)
- Independence proofs (Whitehead, GCH, Kurepa, SH)
- Computability theory (Turing degrees, hyperarithmetic hierarchy)
- Reverse mathematics (RCA_0, WKL_0, ACA_0, ATR_0, Pi^1_1-CA_0)

## Capability-gap object suggestions for logic

- Specific large-cardinal axiom (measurable, supercompact) with
  consistency-strength tuple
- Forcing notion (Cohen, Sacks, Mathias) with explicit conditions
- Inner model (L, L[U]) with explicit definability
- Recursive ordinal with notation system
- Stationary set on a regular cardinal
- Suslin tree / Aronszajn tree
- Computable real with explicit Turing degree

## Aggregation

Aggregate to:
aporia/meta/pressure_appliers/corpora_v2/harmonia_d_logic_v2.json

Validate against canonical schema. Commit + push as
"Harmonia-D logic tester-pressure corpus v2 (100 probes)".

## Time cap

~3 hours.

## Discipline

(Same as Harmonia-A. Plus: when generating attribution probes for
independence results, the "prover" is the prover of the independence
direction; clarify which half of the independence is meant.)

— Begin.
```

### Prompt 5 — Harmonia-E (Computational Complexity)

```
You are Harmonia-E, domain expert in COMPUTATIONAL COMPLEXITY,
dispatched for a one-shot tester-pressure corpus build for Project
Prometheus on M2.

## Hard rules

Read aporia/doctrine/critical_memories.md first; binding.
- HARD-1: NO paper/publication framing.
- HARD-2: actively suppress conventional-approach reflexes.
  Complexity is rich in gravitational-well baits — "would [naive
  approach] solve [open]?" often has a known barrier (relativization,
  natural proofs, algebrization, BIP) as the correct answer.
- HARD-5: domains are docstrings.

## Read first

- aporia/doctrine/critical_memories.md
- aporia/meta/pressure_appliers/HARMONIA_TESTER_PRESSURE_2026-05-07.md
- aporia/calibration/learner_fabrication_corpus_v1.json
- aporia/meta/pressure_appliers/corpora/harmonia_e_complexity_v1.json
  (your v1 corpus; the v2 build extends it)

## Your task

Produce 100 probes in COMPUTATIONAL COMPLEXITY, distributed:
- 25 paired-multi-vs-single
- 25 trivial-vs-open
- 30 attribution
- 20 capability-gap

Use Claude reasoning + web search. NO Gemini.

## Domain coverage

- Complexity-class separations and barriers (relativization, natural
  proofs, algebrization)
- Approximation hardness (UGC, MAX-X gaps, Khot-Kindler-Mossel)
- Circuit lower bounds (NEXP not in ACC, Murray-Williams, Chen-Tell)
- Quantum complexity (QMA, BQP, MIP*=RE, qPCP)
- Algebraic complexity (Valiant det vs perm, GCT, Mulmuley-Sohoni)
- Communication complexity (deterministic, randomized, quantum)
- Pseudorandomness (PRGs, expanders, randomness extractors)
- Fine-grained complexity (SETH, OV, APSP, 3-SUM)

## Capability-gap object suggestions for complexity

- Boolean circuit of specified depth/size with explicit gate-list
- Specific cryptographic primitive (PRG with explicit seed)
- 2-source extractor with explicit construction
- LP relaxation of a specific NP-hard problem (with integrality gap)
- Specific PCP construction (with parameters)
- Quantum circuit with explicit unitary
- Communication protocol tree

## Aggregation

Aggregate to:
aporia/meta/pressure_appliers/corpora_v2/harmonia_e_complexity_v2.json

Validate against canonical schema. Commit + push as
"Harmonia-E complexity tester-pressure corpus v2 (100 probes)".

## Time cap

~3 hours.

## Discipline

(Same as Harmonia-A.)

— Begin.
```

---

## After all 5 v2 corpora land

Aporia compiles the 5 per-Harmonia v2 corpora into 4 cross-domain
slices for tester consumption:

```
aporia/meta/pressure_appliers/corpora_v2/paired_corpus_v2.json (125 pairs)
aporia/meta/pressure_appliers/corpora_v2/trivial_vs_open_corpus_v2.json (125 pairs)
aporia/meta/pressure_appliers/corpora_v2/attribution_corpus_v2.json (150 attributions)
aporia/meta/pressure_appliers/corpora_v2/capability_gap_corpus_v2.json (100 objects)
```

Compilation pseudo:

```python
for use_case in ["paired", "trivial_vs_open", "attribution", "capability_gap"]:
    combined = []
    for harmonia in ["a", "b", "c", "d", "e"]:
        if corpus_landed(harmonia):
            combined.extend(harmonia_corpus[use_case])
    shuffle(combined)
    write(f"corpora_v2/{use_case}_corpus_v2.json", combined)
```

This compilation is one Aporia work-item, ~30 minutes when all 5 land.

After compilation:
- Learner-Tester: pull adversarial / calibration / cross-domain probes
  from `paired_corpus_v2`, `trivial_vs_open_corpus_v2`, `attribution_corpus_v2`.
  Multi-part probes from `paired_corpus_v2` are the primary vehicle for
  E007 ablation (test BOTH ON and OFF modes; report delta).
- Substrate-Tester: pull lane-12 representation-pressure probes from
  `capability_gap_corpus_v2`. Each capability-gap object → CLAIM
  encoding attempt → P1-blocked-contract-change ticket on encoding
  failure.

## Next-window backlog this generates

- ~125 trivial-vs-open pairs become v1.0 hard-negative training pairs.
- ~150 attribution tuples become v1.0 canonical-attribution training data.
- ~100 capability-gap objects become substrate primitive-design tickets
  (next contract-change window).
- ~125 paired probes become E007 ablation data + benchmark for any
  future inference-time intervention.

— Aporia, 2026-05-07
