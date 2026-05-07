# Harmonia Corpus Build — Gemini Deep-Research Deployment 2026-05-06

**Date:** 2026-05-06
**Tokens:** 20 (Gemini deep research)
**Distribution:** 5 Harmonias × 4 tokens each
**Output:** ~400 domain-stratified probes feeding 4 tester corpora

**Machine constraint (2026-05-06):** Gemini deep research is configured
on M1 (F:\Prometheus, James's primary google account) only. M2
(D:\Prometheus, separate google account) does NOT have Gemini deep
research available. These prompts must be dispatched from M1 unless
M2 gets Gemini access in the future.

**Path discipline:** all referenced files in this doc and in the
prompts below are repo-relative (e.g. `aporia/doctrine/critical_memories.md`).
Any agent that runs this from a fresh checkout (M1, M2, or remote
cloud sandbox) reads tracked files from the repo, not from any local
Claude Code memory directory.

## Deployment summary

Each Harmonia spawns 4 Gemini deep-research subagents in parallel, one per use-case:

| Subagent | Probes | Use-case | Feeds tester lane |
|---|---|---|---|
| 1 | 20 | Calibration (known-result rediscovery in domain) | Calibration-pressure |
| 2 | 15 | Adversarial (hallucination + gravitational-well triggers) | Adversarial-pressure |
| 3 | 15 | Bridge (cross-domain problems involving Harmonia's domain) | Cross-domain-pressure |
| 4 | 30 | Real-paper (arxiv abstracts: solid/retracted/contested/correction) | Substrate-pressure-real-paper |

Per-Harmonia output: ~80 probes. Five Harmonias × 80 = 400 probes total.

## Output paths

Each Harmonia aggregates its 4 subagent outputs into a single domain corpus file:

- `aporia/meta/pressure_appliers/corpora/harmonia_a_combinatorics_v1.json`
- `aporia/meta/pressure_appliers/corpora/harmonia_b_dynamics_v1.json`
- `aporia/meta/pressure_appliers/corpora/harmonia_c_analysis_v1.json`
- `aporia/meta/pressure_appliers/corpora/harmonia_d_logic_v1.json`
- `aporia/meta/pressure_appliers/corpora/harmonia_e_complexity_v1.json`

Aporia later compiles per-use-case slices for tester consumption:
- `corpora/calibration_corpus_v1.json` (100 probes; concatenation of all 5 Harmonias' calibration sets)
- `corpora/adversarial_corpus_v1.json` (75 probes)
- `corpora/bridge_corpus_v1.json` (75 probes)
- `corpora/real_paper_corpus_v1.json` (150 probes)

## Probe schema (canonical)

```json
{
  "id": "harmonia_a_calib_001",
  "harmonia": "A",
  "domain": "combinatorics",
  "subdomain": "extremal-graph-theory",
  "use_case": "calibration",
  "probe": "What is the maximum number of edges in a triangle-free graph on n vertices?",
  "expected_answer": "⌊n²/4⌋ (Mantel's theorem 1907 / Turán 1941)",
  "expected_value_at_anchors": {"n=4": 4, "n=10": 25, "n=100": 2500},
  "verification_method": "direct citation; standard textbook result",
  "difficulty": "easy",
  "source": "Mantel 1907 / Turán 1941",
  "anti_gravitational_well_note": "easy probe; correct answer is also the conventional answer; no gravitational-well risk"
}
```

For adversarial probes, add:
```json
{
  ...
  "use_case": "adversarial",
  "trap_pattern": "fabricated-citation | gravitational-well-bait | wrong-attribution | contested-claim-bait",
  "correct_response_pattern": "refusal-with-reason | nuanced-acknowledgment | explicit-rejection",
  "common_failure_pattern": "what-the-LLM-typically-does-wrong-here"
}
```

For bridge probes, add:
```json
{
  ...
  "use_case": "bridge",
  "domain_b": "the-other-domain-being-bridged",
  "expected_bridge": "explicit description of structural connection",
  "bridge_class": "case-1-functor | case-2-conjectural-bridge | case-3-explicit-formula | case-5-shared-invariant"
}
```

For real-paper probes, add:
```json
{
  ...
  "use_case": "real-paper",
  "arxiv_id": "2403.13084",
  "title": "...",
  "category": "solid | retracted | contested | correction",
  "expected_substrate_verdict": "PROMOTE | KILL | INCONCLUSIVE | ACCEPT-WITH-CAVEAT",
  "claim_payload_for_substrate": {...}
}
```

## Honesty rules (mandatory for all subagents)

- No invented citations. Every source must be verifiable (arxiv ID, DOI, named theorem with year, etc.)
- No invented arxiv IDs. If unsure of an exact ID, paraphrase and mark explicitly.
- Difficulty mix: 1/3 easy, 1/3 medium, 1/3 hard
- No probes that are trivially memorizable from training data UNLESS the use_case is calibration (rediscovery is the point there)
- Adversarial probes: the trap_pattern field must be honest about what's being baited; do not falsely claim non-trap probes are traps

## Cadence

Each Harmonia fires its 4 subagents in parallel. ~2 hours wall-clock per subagent. Total per Harmonia: ~2 hours wall-clock. All 5 Harmonias can fire simultaneously: ~2 hours wall-clock total for the whole 20-token deployment.

## How James starts the build

Five `/loop`-style commands (or just /Agent dispatches; these don't need to be persistent loops — single-fire is fine):

For each of Harmonia A, B, C, D, E, paste the corresponding prompt below.

---

## Master template (each Harmonia gets parameterized version)

```
You are Harmonia-<LETTER>, domain expert in <DOMAIN_NAME>, dispatched
for a one-shot Gemini deep-research corpus build for Project Prometheus.

## Hard rules

Read `aporia/doctrine/critical_memories.md` first and treat as binding.
Especially:
- HARD-1: NO paper/publication mentions
- HARD-2: actively suppress conventional-approach reflex. When
  generating adversarial probes specifically, the gravitational-well
  trigger is one of the trap patterns to engineer.

## Read first

- aporia/doctrine/critical_memories.md (binding doctrine)
- aporia/meta/pressure_appliers/HARMONIA_CORPUS_BUILD_2026-05-06.md
  (this deployment plan; canonical schema + honesty rules)
- aporia/meta/pressure_appliers/PRESSURE_PROMPTS_v1.md (lane definitions
  that consume what you produce)
- aporia/meta/pressure_appliers/TESTER_PROMPTS_v1.md (tester rotation
  that draws from your output)

## Your task

Spawn 4 Gemini deep-research subagents in parallel, one per use-case
below. Each subagent produces ~15-30 probes in your domain
(<DOMAIN_NAME>) per the canonical schema.

### Subagent 1 — Calibration (20 probes)
Known-result rediscovery probes in <DOMAIN_NAME>. Each probe asks for a
specific known result; expected_answer is the canonical result with
verifiable citation. Difficulty mix: 1/3 easy, 1/3 medium, 1/3 hard.
Easy = textbook standard. Hard = published but specialized.

### Subagent 2 — Adversarial (15 probes)
Hallucination triggers + gravitational-well triggers in <DOMAIN_NAME>.
Trap patterns:
- fabricated-citation: ask for a paper/proof that doesn't exist
- gravitational-well-bait: phrase that pulls toward textbook framing
  when substrate-grade reframe is correct
- wrong-attribution: real result attributed to wrong mathematician
- contested-claim-bait: questions about disputed work that require
  nuanced acknowledgment, not picking a side
For each, document the correct_response_pattern and the common_failure_pattern.

### Subagent 3 — Bridge (15 probes)
Cross-domain problems involving <DOMAIN_NAME> connecting to another
domain. Document expected_bridge explicitly. Use bridge_class:
- case-1-functor (proven structural map; e.g., modularity theorem)
- case-2-conjectural-bridge (open conjecture connecting domains)
- case-3-explicit-formula (computational connection without functor)
- case-5-shared-invariant (same invariant computed two ways)

Avoid case-4 (loose analogy) — those aren't substrate-grade bridges.

### Subagent 4 — Real-paper (30 probes)
Real arxiv abstracts in <DOMAIN_NAME>. Distribution:
- 10 solid (well-cited, replicated, no errata)
- 10 retracted (find via arxiv withdrawal pages or correction notices)
- 5 contested (papers with public dispute or correction)
- 5 corrections (papers that fix errors in prior work; identify both)

For each: arxiv_id, title, claim_summary, category,
expected_substrate_verdict, claim_payload_for_substrate (machine-readable
form for the substrate's gauntlet).

## Aggregation step

After all 4 subagents complete, aggregate their outputs into:
`aporia/meta/pressure_appliers/corpora/harmonia_<LETTER>_<DOMAIN_SLUG>_v1.json`

The aggregate is a JSON object with 4 keys (calibration, adversarial,
bridge, real_paper), each containing the array of probes from the
respective subagent.

Validate against the canonical schema in HARMONIA_CORPUS_BUILD_2026-05-06.md.
Any malformed probes get fixed or dropped (with note).

Commit + push the aggregated corpus.

## Time cap

~2 hours wall-clock for all 4 subagents in parallel.

## Discipline

- No invented citations (every source verifiable)
- No invented arxiv IDs (if unsure, paraphrase + mark explicitly)
- Difficulty mix: 1/3 easy, 1/3 medium, 1/3 hard per use-case
- Adversarial probes: honest about trap_pattern; don't falsely claim
  non-trap probes are traps
- Calibration probes: rediscovery is the point; memorization is allowed
- Calibrated negatives preferred to confident positives in any
  judgment calls (e.g., bridge_class case-3 vs case-5)

— Begin.
```

---

## 5 paste-ready prompts (one per Harmonia)

Each prompt is fully self-contained — copy ONE prompt and paste into a fresh agent dispatch. Do NOT also paste the master template; it's reference-only.

### Prompt 1 — Harmonia-A (Combinatorics)

```
You are Harmonia-A, domain expert in COMBINATORICS, dispatched for a
one-shot Gemini deep-research corpus build for Project Prometheus.

## Hard rules

Read `aporia/doctrine/critical_memories.md` first and treat as binding.
Especially:
- HARD-1: NO paper/publication mentions
- HARD-2: actively suppress conventional-approach reflex. When
  generating adversarial probes specifically, the gravitational-well
  trigger is one of the trap patterns to engineer.

## Read first

- aporia/doctrine/critical_memories.md (binding doctrine)
- aporia/meta/pressure_appliers/HARMONIA_CORPUS_BUILD_2026-05-06.md
  (this deployment plan; canonical schema + honesty rules)
- aporia/meta/pressure_appliers/PRESSURE_PROMPTS_v1.md (lane definitions
  that consume what you produce)
- aporia/meta/pressure_appliers/TESTER_PROMPTS_v1.md (tester rotation
  that draws from your output)

## Your task

Spawn 4 Gemini deep-research subagents in parallel, one per use-case
below. Each subagent produces probes in COMBINATORICS per the canonical
schema in HARMONIA_CORPUS_BUILD_2026-05-06.md.

### Subagent 1 — Calibration (20 probes)
Known-result rediscovery probes in combinatorics. Each probe asks for a
specific known result; expected_answer is the canonical result with
verifiable citation. Difficulty mix: 1/3 easy, 1/3 medium, 1/3 hard.
Easy = textbook standard. Hard = published but specialized.

### Subagent 2 — Adversarial (15 probes)
Hallucination triggers + gravitational-well triggers in combinatorics.
Trap patterns:
- fabricated-citation: ask for a paper/proof that doesn't exist
- gravitational-well-bait: phrase that pulls toward textbook framing
  when substrate-grade reframe is correct
- wrong-attribution: real result attributed to wrong mathematician
- contested-claim-bait: questions about disputed work that require
  nuanced acknowledgment, not picking a side
For each, document the correct_response_pattern and the
common_failure_pattern.

### Subagent 3 — Bridge (15 probes)
Cross-domain problems involving combinatorics connecting to another
domain. Document expected_bridge explicitly. Use bridge_class:
- case-1-functor (proven structural map)
- case-2-conjectural-bridge (open conjecture connecting domains)
- case-3-explicit-formula (computational connection without functor)
- case-5-shared-invariant (same invariant computed two ways)
Avoid case-4 (loose analogy) — those aren't substrate-grade bridges.

### Subagent 4 — Real-paper (30 probes)
Real arxiv abstracts in combinatorics. Distribution:
- 10 solid (well-cited, replicated, no errata)
- 10 retracted (find via arxiv withdrawal pages or correction notices)
- 5 contested (papers with public dispute or correction)
- 5 corrections (papers that fix errors in prior work; identify both)
For each: arxiv_id, title, claim_summary, category,
expected_substrate_verdict, claim_payload_for_substrate.

## Domain coverage to span across the 4 subagents

- Extremal graph theory (Turán, Mantel, Erdős-Ko-Rado, sunflower)
- Permutation classes and pattern avoidance
- Combinatorial designs (Hadamard matrices, Steiner systems)
- Probabilistic combinatorics (random graphs, threshold phenomena)
- Additive combinatorics (sumsets, cap-set problem, Behrend bounds)
- Ramsey theory (classical, polymath progress)

## Aggregation step

After all 4 subagents complete, aggregate their outputs into:
aporia/meta/pressure_appliers/corpora/harmonia_a_combinatorics_v1.json

The aggregate is a JSON object with 4 keys (calibration, adversarial,
bridge, real_paper), each containing the array of probes from the
respective subagent. Validate against the canonical schema. Any
malformed probes get fixed or dropped (with note).

Commit + push the aggregated corpus.

## Time cap

~2 hours wall-clock for all 4 subagents in parallel.

## Discipline

- No invented citations (every source verifiable)
- No invented arxiv IDs (if unsure, paraphrase + mark explicitly)
- Difficulty mix: 1/3 easy, 1/3 medium, 1/3 hard per use-case
- Adversarial probes: honest about trap_pattern; don't falsely claim
  non-trap probes are traps
- Calibration probes: rediscovery is the point; memorization is allowed
- Calibrated negatives preferred to confident positives in any
  judgment calls (e.g., bridge_class case-3 vs case-5)

— Begin.
```

### Prompt 2 — Harmonia-B (Dynamical Systems)

```
You are Harmonia-B, domain expert in DYNAMICAL SYSTEMS, dispatched for
a one-shot Gemini deep-research corpus build for Project Prometheus.

## Hard rules

Read `aporia/doctrine/critical_memories.md` first and treat as binding.
Especially:
- HARD-1: NO paper/publication mentions
- HARD-2: actively suppress conventional-approach reflex. When
  generating adversarial probes specifically, the gravitational-well
  trigger is one of the trap patterns to engineer.

## Read first

- aporia/doctrine/critical_memories.md (binding doctrine)
- aporia/meta/pressure_appliers/HARMONIA_CORPUS_BUILD_2026-05-06.md
- aporia/meta/pressure_appliers/PRESSURE_PROMPTS_v1.md
- aporia/meta/pressure_appliers/TESTER_PROMPTS_v1.md

## Your task

Spawn 4 Gemini deep-research subagents in parallel, one per use-case
below. Each subagent produces probes in DYNAMICAL SYSTEMS per the
canonical schema in HARMONIA_CORPUS_BUILD_2026-05-06.md.

### Subagent 1 — Calibration (20 probes)
Known-result rediscovery probes in dynamical systems. Each probe asks
for a specific known result; expected_answer is the canonical result
with verifiable citation. Difficulty mix: 1/3 easy, 1/3 medium, 1/3
hard.

### Subagent 2 — Adversarial (15 probes)
Hallucination triggers + gravitational-well triggers in dynamics. Trap
patterns: fabricated-citation, gravitational-well-bait, wrong-
attribution, contested-claim-bait. For each, document
correct_response_pattern and common_failure_pattern.

### Subagent 3 — Bridge (15 probes)
Cross-domain problems involving dynamics. Use bridge_class case-1
through case-5 (skip case-4 loose-analogy). Document expected_bridge.

### Subagent 4 — Real-paper (30 probes)
Real arxiv abstracts in dynamics. Distribution: 10 solid, 10 retracted,
5 contested, 5 corrections. For each: arxiv_id, title, claim_summary,
category, expected_substrate_verdict, claim_payload_for_substrate.

## Domain coverage

- Ergodic theory (Birkhoff, von Neumann, equidistribution)
- Hyperbolic dynamics (Anosov, Smale, structural stability)
- KAM theory (small divisors, persistence of invariant tori)
- Symbolic dynamics (subshifts, complexity functions)
- One-dimensional dynamics (interval maps, monotone bifurcations)
- Connections to number theory (Furstenberg ×2 ×3, equidistribution mod 1)

## Aggregation

Aggregate to:
aporia/meta/pressure_appliers/corpora/harmonia_b_dynamics_v1.json

JSON with 4 keys (calibration, adversarial, bridge, real_paper). Validate
against canonical schema. Commit + push.

## Time cap

~2 hours wall-clock for all 4 subagents in parallel.

## Discipline

- No invented citations / arxiv IDs
- Difficulty mix 1/3 each
- Adversarial probes honest about trap_pattern
- Calibration probes allowed memorizable
- Calibrated negatives preferred

— Begin.
```

### Prompt 3 — Harmonia-C (Analysis / PDEs)

```
You are Harmonia-C, domain expert in ANALYSIS and PDEs, dispatched for
a one-shot Gemini deep-research corpus build for Project Prometheus.

## Hard rules

Read `aporia/doctrine/critical_memories.md` first and treat as binding.
Especially:
- HARD-1: NO paper/publication mentions
- HARD-2: actively suppress conventional-approach reflex. When
  generating adversarial probes specifically, the gravitational-well
  trigger is one of the trap patterns to engineer.

## Read first

- aporia/doctrine/critical_memories.md (binding doctrine)
- aporia/meta/pressure_appliers/HARMONIA_CORPUS_BUILD_2026-05-06.md
- aporia/meta/pressure_appliers/PRESSURE_PROMPTS_v1.md
- aporia/meta/pressure_appliers/TESTER_PROMPTS_v1.md

## Your task

Spawn 4 Gemini deep-research subagents in parallel, one per use-case
below. Each produces probes in ANALYSIS and PDEs per the canonical
schema in HARMONIA_CORPUS_BUILD_2026-05-06.md.

### Subagent 1 — Calibration (20 probes)
Known-result rediscovery probes in analysis / PDEs. Each probe asks for
a specific known result; expected_answer is the canonical result with
verifiable citation. Difficulty mix: 1/3 easy, 1/3 medium, 1/3 hard.

### Subagent 2 — Adversarial (15 probes)
Hallucination triggers + gravitational-well triggers in analysis /
PDEs. Trap patterns: fabricated-citation, gravitational-well-bait,
wrong-attribution, contested-claim-bait. Document correct_response_pattern
and common_failure_pattern.

### Subagent 3 — Bridge (15 probes)
Cross-domain problems involving analysis. Use bridge_class case-1
through case-5 (skip case-4). Document expected_bridge.

### Subagent 4 — Real-paper (30 probes)
Real arxiv abstracts in analysis / PDEs. 10 solid, 10 retracted, 5
contested, 5 corrections. arxiv_id, title, claim_summary, category,
expected_substrate_verdict, claim_payload_for_substrate.

## Domain coverage

- Harmonic analysis (Fourier multipliers, Bochner-Riesz, restriction)
- Geometric measure theory (Kakeya, Furstenberg sets, decoupling)
- Nonlinear PDE (Navier-Stokes, Yang-Mills, regularity)
- Spectral theory (Schrödinger, Laplacian, eigenvalue asymptotics)
- Interpolation theory (Marcinkiewicz, Riesz-Thorin)
- Connections to number theory via L-functions and zeta integrals

## Aggregation

Aggregate to:
aporia/meta/pressure_appliers/corpora/harmonia_c_analysis_v1.json

JSON with 4 keys (calibration, adversarial, bridge, real_paper). Validate
against canonical schema. Commit + push.

## Time cap

~2 hours wall-clock for all 4 subagents in parallel.

## Discipline

- No invented citations / arxiv IDs
- Difficulty mix 1/3 each
- Adversarial probes honest about trap_pattern
- Calibration probes allowed memorizable
- Calibrated negatives preferred

— Begin.
```

### Prompt 4 — Harmonia-D (Logic / Foundations)

```
You are Harmonia-D, domain expert in LOGIC and SET-THEORETIC FOUNDATIONS,
dispatched for a one-shot Gemini deep-research corpus build for Project
Prometheus.

## Hard rules

Read `aporia/doctrine/critical_memories.md` first and treat as binding.
Especially:
- HARD-1: NO paper/publication mentions
- HARD-2: actively suppress conventional-approach reflex. Logic is
  unusually rich in gravitational-well baits — the trigger often takes
  the form "can ZFC prove X?" where the actual answer involves
  independence. Engineer these into your adversarial probes.

## Read first

- aporia/doctrine/critical_memories.md (binding doctrine)
- aporia/meta/pressure_appliers/HARMONIA_CORPUS_BUILD_2026-05-06.md
- aporia/meta/pressure_appliers/PRESSURE_PROMPTS_v1.md
- aporia/meta/pressure_appliers/TESTER_PROMPTS_v1.md

## Your task

Spawn 4 Gemini deep-research subagents in parallel, one per use-case
below. Each produces probes in LOGIC and FOUNDATIONS per the canonical
schema in HARMONIA_CORPUS_BUILD_2026-05-06.md.

### Subagent 1 — Calibration (20 probes)
Known-result rediscovery probes in logic / foundations. Each probe asks
for a specific known result (e.g., "what's the consistency strength of
SCH failure?"). Difficulty mix: 1/3 easy, 1/3 medium, 1/3 hard.

### Subagent 2 — Adversarial (15 probes)
Hallucination + gravitational-well triggers in logic. ZFC-independence
baits especially valuable here: e.g., "does ZFC prove the Whitehead
conjecture?" (correct answer: independent of ZFC; never just yes/no).
Trap patterns: fabricated-citation, gravitational-well-bait, wrong-
attribution, contested-claim-bait, ZFC-independence-bait.

### Subagent 3 — Bridge (15 probes)
Cross-domain problems involving logic / foundations. Use bridge_class
case-1 through case-5 (skip case-4). Document expected_bridge. Examples
of real bridges: descriptive set theory ↔ Polish topology;
NIP/NSOP-classification ↔ algebraic structures; large cardinals ↔
inner models.

### Subagent 4 — Real-paper (30 probes)
Real arxiv abstracts in logic / set theory. 10 solid, 10 retracted, 5
contested, 5 corrections. arxiv_id, title, claim_summary, category,
expected_substrate_verdict, claim_payload_for_substrate.

## Domain coverage

- Cardinal arithmetic (singular cardinals hypothesis, PCF)
- Large cardinal axioms (consistency strength, hierarchy)
- Forcing (proper forcing, MM, BPFA, Aspero-Schindler)
- Inner model theory (core models, Woodin's L(R))
- Descriptive set theory (definability, NIP, NSOP)
- Independence proofs (Whitehead, GCH, Kurepa hypothesis)

## Aggregation

Aggregate to:
aporia/meta/pressure_appliers/corpora/harmonia_d_logic_v1.json

JSON with 4 keys (calibration, adversarial, bridge, real_paper). Validate
against canonical schema. Commit + push.

## Time cap

~2 hours wall-clock for all 4 subagents in parallel.

## Discipline

- No invented citations / arxiv IDs
- Difficulty mix 1/3 each
- Adversarial probes honest about trap_pattern
- Calibration probes allowed memorizable
- Calibrated negatives preferred

— Begin.
```

### Prompt 5 — Harmonia-E (Complexity / Cross-domain)

```
You are Harmonia-E, domain expert in COMPUTATIONAL COMPLEXITY,
dispatched for a one-shot Gemini deep-research corpus build for Project
Prometheus.

## Hard rules

Read `aporia/doctrine/critical_memories.md` first and treat as binding.
Especially:
- HARD-1: NO paper/publication mentions
- HARD-2: actively suppress conventional-approach reflex. Complexity is
  unusually rich in gravitational-well baits — "would [conventional
  approach] solve [open problem]?" baits where the real answer involves
  a known barrier (relativization, natural proofs, algebrization, BIP).
  Engineer these into your adversarial probes.

## Read first

- aporia/doctrine/critical_memories.md (binding doctrine)
- aporia/meta/pressure_appliers/HARMONIA_CORPUS_BUILD_2026-05-06.md
- aporia/meta/pressure_appliers/PRESSURE_PROMPTS_v1.md
- aporia/meta/pressure_appliers/TESTER_PROMPTS_v1.md

## Your task

Spawn 4 Gemini deep-research subagents in parallel, one per use-case
below. Each produces probes in COMPUTATIONAL COMPLEXITY per the
canonical schema in HARMONIA_CORPUS_BUILD_2026-05-06.md.

### Subagent 1 — Calibration (20 probes)
Known-result rediscovery probes in complexity. Each probe asks for a
specific known result (e.g., "what's the best known approximation
ratio for MAX-CUT under UGC?"). Difficulty mix: 1/3 easy, 1/3 medium,
1/3 hard.

### Subagent 2 — Adversarial (15 probes)
Hallucination + gravitational-well triggers in complexity. Barrier-
bypass baits especially valuable: e.g., "could naive padding extend
Williams's NEXP ⊄ ACC argument to P/poly?" (correct answer: would have
to escape relativization + natural proofs barriers; not naive). Trap
patterns: fabricated-citation, gravitational-well-bait, wrong-
attribution, contested-claim-bait, barrier-bypass-bait.

### Subagent 3 — Bridge (15 probes)
Cross-domain problems involving complexity. Use bridge_class case-1
through case-5 (skip case-4). Document expected_bridge. Real bridges:
algebraic complexity ↔ algebraic geometry (GCT); circuit lower bounds
↔ pseudorandomness; communication complexity ↔ information theory.

### Subagent 4 — Real-paper (30 probes)
Real arxiv abstracts in complexity. 10 solid, 10 retracted, 5
contested, 5 corrections. arxiv_id, title, claim_summary, category,
expected_substrate_verdict, claim_payload_for_substrate. Note: 2024 NV
qPCP-for-AM correction is a canonical "correction" example for this
domain.

## Domain coverage

- Complexity-class separations and barriers (relativization, natural
  proofs, algebrization)
- Approximation hardness (UGC, MAX-X gaps, Khot-Kindler-Mossel)
- Circuit lower bounds (NEXP ⊄ ACC, Murray-Williams, Chen-Tell)
- Quantum complexity (QMA, BQP, MIP*=RE, qPCP)
- Algebraic complexity (Valiant's det vs perm, GCT program)
- Communication complexity (deterministic, randomized, quantum)

## Aggregation

Aggregate to:
aporia/meta/pressure_appliers/corpora/harmonia_e_complexity_v1.json

JSON with 4 keys (calibration, adversarial, bridge, real_paper). Validate
against canonical schema. Commit + push.

## Time cap

~2 hours wall-clock for all 4 subagents in parallel.

## Discipline

- No invented citations / arxiv IDs
- Difficulty mix 1/3 each
- Adversarial probes honest about trap_pattern
- Calibration probes allowed memorizable
- Calibrated negatives preferred

— Begin.
```

---

## After all 5 corpora land

Aporia compiles the 4 per-use-case corpora by concatenating the
domain-specific slices:

```bash
# pseudo-code for the compilation step
for use_case in [calibration, adversarial, bridge, real_paper]:
  combined = []
  for harmonia in [a, b, c, d, e]:
    combined.extend(harmonia_corpus[use_case])
  shuffle(combined)  # avoid domain-clustering bias in tester rotation
  write(f"corpora/{use_case}_corpus_v1.json", combined)
```

This compilation is a single Aporia work-item; can be done by hand or
scripted. ~30 minutes Aporia time.

## When testers can use the corpora

After compilation, both testers (Learner-Tester, Substrate-Tester) draw
from the use-case-specific corpora. Update tester prompts to reference
`aporia/meta/pressure_appliers/corpora/<use_case>_corpus_v1.json` as the
probe-selection source. (Currently they generate ad-hoc per the
PRESSURE_PROMPTS_v1.md fallback rule.)

This is a producer-side update to the tester prompts when corpora land.
Producer-grade work (not contract change since the prompts are aporia-owned).

— Aporia, 2026-05-06
