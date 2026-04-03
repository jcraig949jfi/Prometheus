# Forge T2/T3 Architecture — v2 (Rebuild)

**Author:** Pipeline Orchestrator  
**Date:** 2026-04-02  
**Status:** AWAITING REVIEW — no implementation code until approved  

---

## 1. Failure Analysis of Previous Attempt

The previous T2/T3 forge failed because:

1. **Same session saw tests and wrote tools** — enabling answer-key construction
2. **Winning tools used 0% of their own primitive libraries** — primitives were decoration
3. **93% hand-coded regex/if-blocks** matching specific answer strings
4. **100% scores collapsed to 79-96% under seed variation** — overfitting to seed=42
5. **No diversity enforcement** — all tools shared the same fallback chain (monoculture)
6. **No pre-committed thresholds** — success criteria invented after results

This rebuild makes each failure mode structurally impossible through the Five Iron Laws.

---

## 2. External Libraries for Amino Acid Decomposition

### Selection Criteria
- Library must provide a reasoning capability that T1 primitives lack entirely
- Library must be decomposable into 5-20 line atomic functions
- Library must be established (>500 GitHub stars, active maintenance)
- Library must have a Python API with no GPU/ML dependencies

### Library 1: pgmpy (v1.0.0)
- **URL:** https://github.com/pgmpy/pgmpy
- **Purpose:** Probabilistic graphical models — Bayesian networks, d-separation, causal do-calculus
- **What T1 lacks:** T1 has `bayesian_update` (single-step) and `counterfactual_intervention` (simple additive). It cannot: compute conditional probabilities over networks, detect d-separation, identify confounders via back-door criterion, or detect Simpson's paradox. pgmpy provides all of these.
- **Target categories:** simpson_paradox, causal_counterfactual, causal_confounding_hard, conditional_probability_chain, meta_causal_reasoning
- **Estimated amino acids:** 8-12

### Library 2: PySAT (python-sat v1.9)
- **URL:** https://github.com/pysathq/pysat  
- **Purpose:** Industrial-strength SAT solving, MaxSAT, MUS (minimal unsatisfiable subset) extraction
- **What T1 lacks:** T1 has a brute-force SAT solver limited to ~20 variables. PySAT provides: efficient CDCL solvers (Glucose, MiniSat), MaxSAT for optimization under constraints, MUS extraction for identifying WHY a formula is unsatisfiable (critical for paradox detection and argument invalidity).
- **Target categories:** liar_detection, self_referential_paradox, argument_strength, hidden_constraint, adversarial_framing
- **Estimated amino acids:** 8-10

### Library 3: python-constraint (v2.5.0)
- **URL:** https://github.com/python-constraint/python-constraint
- **Purpose:** Constraint satisfaction with arc consistency, forward checking, and optimized backtracking
- **What T1 lacks:** T1 has a naive backtracking CSP solver. python-constraint provides: forward checking (prune domains early), optimized variable ordering, built-in constraint types (AllDifferent, ExactSum, etc.), and the ability to enumerate ALL solutions (needed for "is this problem uniquely solvable?" questions).
- **Target categories:** temporal_scheduling, cascading_inference, compositional_multi_step, hidden_constraint, insufficient_information_detection
- **Estimated amino acids:** 6-8

### Library 4: nashpy (v0.0.43)
- **URL:** https://github.com/drvinceknight/nashpy
- **Purpose:** 2-player game theory — Nash equilibrium computation via support enumeration, vertex enumeration, and Lemke-Howson
- **What T1 lacks:** T1 has no game-theoretic reasoning at all. T3's `game_tree_solve` does backward induction on explicit trees but cannot compute mixed-strategy Nash equilibria or handle simultaneous games. nashpy provides: Nash equilibrium computation, best-response analysis, dominance checking.
- **Target categories:** game_theory_sequential, mechanism_design_incentive, strategic_information_revelation, strategic_deception, tom_causal_deception
- **Estimated amino acids:** 6-8

**Total estimated amino acids: 28-38** from 4 external libraries.

---

## 3. Amino Acid Registry Design

### Structure
Each amino acid is stored in a flat Python registry file (`forge/amino_acids/registry.py`).
Each amino acid is a standalone function with a decorator providing metadata:

```python
@amino_acid(
    id="pgmpy_dsep_check",
    source="pgmpy",
    reasoning_type="causal",
    description="Check if two variables are d-separated given observed variables in a Bayesian network"
)
def dsep_check(edges: list[tuple[str,str]], var_a: str, var_b: str, observed: set[str]) -> bool:
    """Returns True if var_a and var_b are d-separated given observed set."""
    from pgmpy.models import DiscreteBayesianNetwork
    model = DiscreteBayesianNetwork(edges)
    return not model.is_dconnected(var_a, var_b, observed=observed)
```

### Amino Acid Metadata Schema
```python
{
    "id": str,              # Unique identifier: "{source}_{short_name}"
    "source": str,          # Library name: "pgmpy", "pysat", "python_constraint", "nashpy"
    "reasoning_type": str,  # One of: logical, probabilistic, causal, temporal,
                            #         constraint, game_theoretic, metacognitive
    "signature": str,       # Function signature as string
    "description": str,     # One-line description
    "lines": int,           # Line count (must be 5-20)
    "dependencies": list,   # Other amino acids this one calls (for call graph tracking)
}
```

### Size Distribution Target
- Minimum: 5 lines (e.g., `is_dominated_strategy` — one comparison loop)
- Maximum: 20 lines (e.g., `enumerate_all_solutions` — CSP enumeration with domain check)
- Median target: 10-12 lines
- Any function >20 lines must be decomposed further before registration

### Type Distribution Target (approximate)
| Reasoning Type | Count | Source Libraries |
|---------------|-------|-----------------|
| causal | 8-10 | pgmpy |
| logical | 6-8 | pysat |
| constraint | 6-8 | python-constraint |
| game_theoretic | 6-8 | nashpy |
| probabilistic | 4-6 | pgmpy |
| metacognitive | 2-4 | pysat (MUS), pgmpy (d-sep) |

### Planned Amino Acids (by library)

**From pgmpy (8-12):**
1. `pgmpy_build_bn` — construct a BayesianNetwork from edges + CPDs
2. `pgmpy_dsep_check` — check d-separation between two variables
3. `pgmpy_find_dseparators` — find minimal d-separating set
4. `pgmpy_get_markov_blanket` — get Markov blanket of a variable
5. `pgmpy_conditional_query` — query P(X|evidence) via variable elimination
6. `pgmpy_do_calculus` — compute P(Y|do(X)) via adjustment
7. `pgmpy_get_adjustment_set` — find back-door adjustment set
8. `pgmpy_detect_confounders` — identify common causes of two variables
9. `pgmpy_compare_conditional_marginal` — compare P(Y|X) vs P(Y) (Simpson's detector)
10. `pgmpy_chain_probability` — compute chain rule P(A,B,C) = P(A)P(B|A)P(C|B)

**From PySAT (8-10):**
1. `pysat_encode_cnf` — convert list of clauses to CNF object
2. `pysat_solve` — solve SAT instance, return model or None
3. `pysat_is_satisfiable` — boolean satisfiability check
4. `pysat_extract_mus` — find minimal unsatisfiable subset (why it's impossible)
5. `pysat_enumerate_models` — enumerate all satisfying assignments (up to k)
6. `pysat_maxsat_solve` — find assignment maximizing satisfied soft clauses
7. `pysat_check_validity` — check if formula is a tautology (negate and check unsat)
8. `pysat_encode_exactly_k` — cardinality constraint: exactly k of n variables true
9. `pysat_detect_paradox` — check if adding each candidate as assumption creates unsat

**From python-constraint (6-8):**
1. `csp_define_problem` — create CSP with variables and domains
2. `csp_add_all_different` — add AllDifferent constraint
3. `csp_add_function_constraint` — add arbitrary function constraint
4. `csp_solve_first` — find first solution
5. `csp_solve_all` — find all solutions (for uniqueness checking)
6. `csp_count_solutions` — count solutions without enumerating
7. `csp_is_uniquely_solvable` — check if exactly one solution exists

**From nashpy (6-8):**
1. `nash_create_game` — create 2-player game from payoff matrices
2. `nash_find_equilibria` — compute Nash equilibria via support enumeration
3. `nash_is_dominated` — check if a strategy is strictly dominated
4. `nash_best_response` — compute best response to opponent's mixed strategy
5. `nash_find_dominant_strategy` — find strictly dominant strategy if one exists
6. `nash_compute_minimax` — compute minimax strategy for zero-sum game
7. `nash_expected_payoff` — compute expected payoff under mixed strategy profile

---

## 4. Builder/Tester Firewall

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      RUNNER                              │
│  (forge/runner.py — orchestrates, enforces all 5 Laws)   │
│                                                          │
│  ┌──────────────────┐    FIREWALL    ┌────────────────┐  │
│  │     BUILDER       │  ◄─────────►  │     TESTER      │  │
│  │                    │   verdict.json│                  │  │
│  │ • T1 primitives    │              │ • Battery files  │  │
│  │ • Amino acids      │   NEVER:     │ • Ablation logic │  │
│  │ • Category names   │   prompts    │ • Diversity calc │  │
│  │ • 1-line category  │   answers    │ • Seed rotation  │  │
│  │   descriptions     │   candidates │                  │  │
│  │ • Science fields   │   test cases │                  │  │
│  │ • Prior verdicts   │              │                  │  │
│  │   (pass/fail only) │              │                  │  │
│  └──────────────────┘              └────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### What the Builder receives (COMPLETE list)

1. **T1 primitives** — all 28 functions from `forge_primitives.py`
2. **T2 primitives** — all 9 functions from `forge_primitives_t2.py`
3. **T3 primitives** — all 7 functions from `forge_primitives_t3.py`
4. **Amino acid registry** — all ~30 amino acids with full source code and metadata
5. **Category names** — string names only (e.g., "simpson_paradox")
6. **Category descriptions** — ONE sentence each (e.g., "Tests whether the tool can detect when aggregated data reverses subgroup trends")
7. **A randomly selected science field** per generation attempt
8. **Prior verdicts** from the Tester (see below)

### What the Builder NEVER receives

- Battery test case prompts
- Expected answers / correct candidates
- Candidate answer lists
- Any information about HOW test cases are structured
- Any information about NCD-adversarial padding or defense mechanisms
- The Tester's scoring logic or battery generator source code

### Verdict format (Tester → Builder)

```json
{
    "tool_id": "t2_thermodynamics_x_pgmpy_dsep_003",
    "tier": 2,
    "overall_score": 0.583,
    "seed_scores": [0.583, 0.542, 0.625, 0.583, 0.583],
    "seed_stability": 0.083,
    "per_category": {
        "simpson_paradox": {"pass": true, "failure_type": null},
        "causal_counterfactual": {"pass": true, "failure_type": null},
        "liar_detection": {"pass": false, "failure_type": "wrong_answer"},
        "temporal_scheduling": {"pass": false, "failure_type": "no_answer"}
    },
    "ablation": {
        "bayesian_update": {"delta": -0.167, "load_bearing": true},
        "dsep_check": {"delta": -0.125, "load_bearing": true},
        "solve_sat": {"delta": -0.042, "load_bearing": false}
    },
    "diversity": {
        "max_overlap_with_existing": 0.35,
        "most_similar_tool": "t2_thermodynamics_x_pgmpy_dsep_001",
        "passes_diversity_check": true
    },
    "verdict": "PASS"
}
```

### Firewall enforcement

The Builder and Tester run as **separate Python scripts** invoked by the Runner:
- `forge/builder.py` — generates tool `.py` files into `forge/candidates/`
- `forge/tester.py` — reads from `forge/candidates/`, writes verdicts to `forge/verdicts/`
- Neither imports the other. They share no modules except the amino acid registry.
- The Runner (`forge/runner.py`) invokes them sequentially via `subprocess.run()`
- Battery files are in `forge/tester_quarantine/` — a directory the Builder script never reads

### Process isolation verification

The Runner will verify isolation by:
1. Checking that `builder.py` does not import or open any file in `tester_quarantine/`
2. Checking that `tester.py` does not write to `forge/candidates/` or modify tools
3. Logging all file I/O from both processes

---

## 5. Diversity Enforcement (Law 4)

### Call graph computation

Each tool's "call graph" is the set of (primitive_name, amino_acid_id) pairs that are called during execution. This is extracted by:

1. **Static analysis**: AST walk of the tool's source to find all `import` and function call references
2. **Dynamic verification**: Instrument primitives/amino acids with call counters, run against a neutral test prompt, record which were actually called

### Overlap metric

```
overlap(tool_A, tool_B) = |calls_A ∩ calls_B| / |calls_A ∪ calls_B|
```

A new tool is **rejected** if `overlap(new_tool, existing_tool) > 0.40` for ANY existing tool in the same tier.

### Diversity budget

To ensure the population explores broadly:
- Maximum 3 tools per science field per tier
- Maximum 5 tools sharing the same "anchor amino acid" (the amino acid with highest ablation delta)
- After 10 tools pass in a tier, new tools must use at least 1 amino acid not used by any existing passing tool

---

## 6. Null Baselines and Pre-Committed Thresholds (Laws 3 & 5)

### Null baselines (computed BEFORE any tool evaluation)

**Baseline 1: Random Primitive Concatenation**
- Take 3 random T1 primitives
- Mechanically compose: output of A → input of B → input of C
- Score = fraction of candidates correctly ranked #1
- Run 50 random compositions per battery
- Report: mean, median, max, std

**Baseline 2: Single Primitive Ceiling**
- Run each of the 28 T1 primitives as a standalone scorer
- Each primitive scores candidates by heuristic relevance to its domain
- Report: best single-primitive score per battery

**Baseline 3: NCD Baseline**
- Normalized Compression Distance between prompt and each candidate
- This is the existing fallback in all T1 tools
- Already measured: ~29% on T2, ~1% on T3, ~20% on T1

### Pre-committed thresholds

These numbers are LOCKED before any tool evaluation. Justification in comments.

```python
# forge/thresholds.py — FROZEN after commit, do not modify after first eval run

THRESHOLDS = {
    "t2": {
        # T2 must substantially beat NCD (29%) and random chance (25%).
        # "Substantially" = at least 20 percentage points above max(NCD, random).
        # 29% + 20% = 49%, round up to 50%.
        "pass_threshold": 0.50,

        # Seed stability: score must not drop more than 15pp across 5 seeds.
        # Rationale: if a tool drops 15pp when the seed changes, it's memorizing
        # template structure, not reasoning. 15pp allows for legitimate variance
        # in problem difficulty across seeds while catching overfitting.
        "max_seed_drop": 0.15,

        # Ablation: no single primitive may account for more than 60% of the
        # total ablation budget (sum of all deltas). Rationale: a pgmpy d-sep
        # check SHOULD be the heavy lifter in a Simpson's paradox tool — if
        # removing it drops 35pp, that's correct architecture, not composition
        # failure. But if one primitive accounts for 90% of all ablation delta,
        # the other primitives are decoration. 60% is the ceiling.
        "max_ablation_budget_share": 0.60,

        # Ablation: every called primitive must matter — removing it must change
        # output on at least 20% of test cases. Below this, it's decoration.
        "min_ablation_impact": 0.20,

        # When a tool FAILS ablation but PASSES the battery, and one amino acid
        # accounts for >60% of ablation budget, flag that amino acid as
        # "promising primitive" — high-value raw material for next generation.
        # The Builder receives this signal as an additional input.
        "capture_promising_primitives": True,
    },
    "t3": {
        # T3 battery has NCD-adversarial defense (NCD scores ~1%).
        # Random chance is ~25% (4 candidates). T3 tools must beat random
        # by at least 15pp = 40%.
        "pass_threshold": 0.40,

        # T3 problems are harder and more variable. Allow 18pp seed drop.
        "max_seed_drop": 0.18,

        # Same ablation rules as T2.
        "max_ablation_budget_share": 0.60,
        "min_ablation_impact": 0.20,
        "capture_promising_primitives": True,
    },
}
```

---

## 7. Tool Generation Architecture

### T2 Tool Structure

Every T2 tool is a Python class `ReasoningTool` with:
- `evaluate(prompt: str, candidates: list[str]) -> list[dict]`
- `confidence(prompt: str, answer: str) -> float`

Internal structure MUST follow this template:

```python
class ReasoningTool:
    """[Science field] × [Amino acid source] — [Category target]"""

    def evaluate(self, prompt, candidates):
        # Phase 1: Extract problem structure using T1 primitives
        # (e.g., parse implications, extract numbers, identify temporal relations)
        structure = self._extract(prompt)

        # Phase 2: Apply amino acid reasoning
        # (e.g., build Bayesian network, check d-separation, solve CSP)
        reasoning_result = self._reason(structure)

        # Phase 3: Score candidates using science-field conceptual framework
        # (e.g., conservation law check, feedback loop analysis)
        scores = self._score(candidates, reasoning_result)

        # Phase 4: Calibrate using T1 meta-primitives
        confidence = confidence_from_agreement(scores)

        return sorted(results, key=lambda x: x["score"], reverse=True)
```

### Composition requirements enforced at generation time

The Builder template MUST:
1. Import at least 3 T1 primitives by name
2. Import at least 1 amino acid by ID
3. Call each imported function in the execution path (verified by dynamic instrumentation)
4. NOT contain any regex pattern matching against candidate text
5. NOT contain any hardcoded answer strings
6. NOT contain `if candidate == "..."` or `if "..." in candidate` patterns

### Banned patterns (checked by AST analysis in the Runner)

```python
BANNED_PATTERNS = [
    r're\.search\(.+candidate',        # regex matching candidates
    r're\.match\(.+candidate',         # regex matching candidates
    r'candidate\s*==\s*["\']',         # hardcoded answer comparison
    r'["\'].+["\']\s+in\s+candidate',  # substring matching in candidates
    r'if\s+["\'].*["\']\s+in\s+',      # pattern matching against strings
]
```

### T3 Tool Additional Requirements

T3 tools must:
- Import at least 2 T2 primitives AND at least 2 T1 primitives
- Import at least 1 amino acid
- Use concepts from at least 2 different science fields (verified by metadata)
- The two science fields must come from different domains (e.g., physics + biology, not physics + chemistry)

### Science Field Enforcement: REASONING_TRACE.md

The Builder emits a `REASONING_TRACE.md` alongside each tool. This file contains 3-5 sentences
explaining how the science field's conceptual framework shaped the tool's approach. The Tester
does not see this trace. It is reviewed by the human operator during periodic review.

**FAIL examples** (empty handwaving):
- "We used thermodynamics principles to guide our approach"
- "This tool applies concepts from evolutionary biology"

**PASS examples** (specific structural connection):
- "The tool models belief update as a thermal relaxation process where high-confidence evidence has lower entropy and dominates the equilibrium state"
- "The tool treats competing hypotheses as species competing for a niche — the fittest (most consistent with constraints) survive selection pressure from each new piece of evidence"

This is a HITL check, not automated — it runs only on tools that pass all other checks.

### Promising Primitive Capture

When a tool FAILS the ablation check (one primitive accounts for >60% of ablation budget)
but PASSES the battery and seed stability checks, the architecture does NOT simply discard it.
Instead:
1. The dominant amino acid is flagged as a "promising primitive"
2. The Builder receives this signal: `{"promising_primitive": "pgmpy_dsep_check", "category": "simpson_paradox", "note": "High-value — compose with more support primitives"}`
3. The next generation of tools for that category is biased toward using the promising primitive with ADDITIONAL supporting primitives to bring the ablation budget share below 60%

This captures the signal that the primitive is genuinely powerful while enforcing that it must be properly composed.

### Battery Difficulty Safeguard

After the first generation of T2 tools completes evaluation:
1. If >80% of tools pass every category except one → that category's tests may be broken. Flag for human review.
2. If no tools pass any category → the battery may be too hard OR the category descriptions may be too vague. Flag for human review.
3. If all tools pass all categories → the battery is too easy. This should not happen given the thresholds, but flag it.

This check runs once after Phase 2, generation 1 only. It does NOT feed any test content back to the Builder.

---

## 8. Category Descriptions for the Builder

The Builder receives ONLY these descriptions. Nothing more.

### T2 Categories (12)
| Category | One-sentence description |
|----------|------------------------|
| simpson_paradox | Tests whether the tool can detect when aggregated data reverses subgroup trends |
| causal_counterfactual | Tests whether the tool can reason about what would have happened under different interventions |
| conjunction_fallacy | Tests whether the tool correctly judges that P(A∧B) ≤ P(A) |
| strategic_deception | Tests whether the tool can model an adversary who may lie or bluff |
| perspective_shift | Tests whether the tool can reason about what different agents know |
| temporal_scheduling | Tests whether the tool can resolve scheduling conflicts with temporal constraints |
| argument_strength | Tests whether the tool can evaluate logical validity of formal arguments |
| liar_detection | Tests whether the tool can resolve truth-teller/liar puzzles |
| compositional_multi_step | Tests whether the tool can chain multiple reasoning steps where each depends on the prior |
| rate_of_change | Tests whether the tool can compute quantities that change over time |
| causal_confounding_hard | Tests whether the tool can identify and adjust for confounding variables |
| temporal_complex | Tests whether the tool can handle timezone conversions and complex temporal arithmetic |

### T3 Categories (20)
| Category | One-sentence description |
|----------|------------------------|
| causal_temporal_fusion | Tests reasoning that requires both causal and temporal analysis simultaneously |
| tom_causal_deception | Tests modeling an agent's beliefs when they have been deliberately misled |
| probabilistic_logic_conflict | Tests reasoning under conditions where multiple valid frameworks give different answers |
| temporal_tom_scheduling | Tests scheduling when agents have incomplete or inconsistent information about constraints |
| meta_causal_reasoning | Tests reasoning about the soundness and limitations of causal arguments |
| recursive_belief | Tests modeling nested mental states across multiple agents |
| self_referential_paradox | Tests detecting and classifying statements whose truth value depends on their own content |
| recursive_computation | Tests iterative/recursive numerical computation to a fixed point |
| reasoning_about_reasoning | Tests identifying which reasoning strategy is appropriate for a problem |
| insufficient_information_detection | Tests recognizing when the correct response is that the problem cannot be fully solved |
| adversarial_framing | Tests maintaining accurate reasoning when surface presentation is misleading |
| hidden_constraint | Tests identifying information that is implied but not directly stated |
| cascading_inference | Tests multi-step deduction where each conclusion enables the next |
| conditional_probability_chain | Tests computing quantities through chains of dependent relationships |
| game_theory_sequential | Tests reasoning about optimal strategy in multi-step strategic interactions |
| mechanism_design_incentive | Tests reasoning about rule systems and the behaviors they encourage |
| strategic_information_revelation | Tests reasoning about the value of information in strategic contexts |
| structural_analogy | Tests recognizing when two different situations share the same underlying structure |
| abstraction_level_shift | Tests reasoning about the same situation at different levels of granularity |
| domain_transfer | Tests applying reasoning patterns across different subject areas |

---

## 9. Science Field Pool

50 fields for random selection during tool generation:

**Physics:** thermodynamics, statistical mechanics, quantum mechanics, fluid dynamics, optics, electromagnetism, relativity, acoustics
**Biology:** evolutionary biology, ecology, immunology, genetics, neuroscience, cell biology, epidemiology
**Mathematics:** topology, graph theory, number theory, combinatorics, measure theory, category theory, group theory, game theory
**Computer Science:** information theory, automata theory, complexity theory, distributed systems, error-correcting codes, cryptography
**Engineering:** control theory, signal processing, feedback systems, network engineering, reliability engineering
**Social Science:** behavioral economics, decision theory, social choice theory, mechanism design, auction theory
**Chemistry:** chemical kinetics, thermochemistry, equilibrium chemistry
**Earth Science:** climate modeling, seismology, hydrology

Each tool generation randomly selects 1 field (T2) or 2 fields from different domains (T3).

---

## 10. Execution Plan

### Phase 0: Setup (before any tool generation)
1. Install libraries: `pip install pgmpy python-sat python-constraint2 nashpy`
2. Decompose libraries into amino acids, build registry
3. Create directory structure: `forge/candidates/`, `forge/verdicts/`, `forge/tester_quarantine/`
4. Move battery files into quarantine
5. Write `thresholds.py` (FROZEN)

### Phase 1: Null Baselines
1. Run 50 random primitive compositions against T2 battery → record scores
2. Run each T1 primitive individually against T2 battery → record best
3. Run NCD baseline against T2 and T3 batteries → record scores
4. Repeat for T3 with T2 primitives as base
5. All scores recorded in `forge/null_baselines.json`

### Phase 2: T2 Generation
1. For each of 12 T2 categories:
   - Builder generates 20 candidate tools (random science field each)
   - Runner runs AST ban-pattern check, rejects violations
   - Runner runs diversity check against existing tools, rejects >40% overlap
   - Tester evaluates survivors across 5 seeds
   - Tester runs ablation on passing tools
   - Verdicts written to `forge/verdicts/`
   - Category-level pass/fail fed back to Builder for next generation
2. Target: at least 3 diverse passing tools per category

### Phase 3: T3 Generation
1. Same process but with T2 tools/primitives as additional building blocks
2. Each T3 tool must compose across 2 science fields
3. T3 targets the 20 hardest categories

### Phase 4: Reporting
1. Full results table: tool × category × seed
2. Ablation tables for all passing tools
3. Diversity matrix (pairwise overlap)
4. Comparison to null baselines
5. Gap analysis: which categories still have no passing tools

---

## 11. File Structure

```
forge/
├── ARCHITECTURE_T2_T3.md          ← this document
├── thresholds.py                   ← FROZEN pre-committed thresholds
├── amino_acids/
│   ├── registry.py                 ← amino acid registry with metadata
│   ├── pgmpy_acids.py              ← amino acids from pgmpy
│   ├── pysat_acids.py              ← amino acids from PySAT
│   ├── constraint_acids.py         ← amino acids from python-constraint
│   └── nashpy_acids.py             ← amino acids from nashpy
├── builder.py                      ← tool generator (NO battery access)
├── tester.py                       ← tool evaluator (NO tool modification)
├── runner.py                       ← orchestrator (enforces all 5 Laws)
├── candidates/                     ← generated tools (Builder writes, Tester reads)
├── verdicts/                       ← evaluation results (Tester writes, Builder reads)
├── tester_quarantine/              ← battery files (Tester ONLY)
│   ├── trap_generator_t2.py
│   └── trap_generator_t3.py
└── null_baselines.json             ← baseline scores (computed in Phase 1)
```

---

## 12. Open Questions for Review

1. **Library installation**: Should we install pgmpy, python-sat, python-constraint2, and nashpy now, or do you want to review the amino acid decomposition plan first?

2. **T2 primitive reuse**: The existing T2 primitives (deliberate, perspective_shift, etc.) are well-designed compositions of T1. Should we keep them as-is and treat them as "T2 base primitives," or should we rebuild them from amino acids too?

3. **Battery evolution**: The current T2/T3 batteries were designed by the same session that built the failed tools. Should we regenerate the batteries from scratch (new trap generators), or are the existing generators sound despite the tools being bad?

4. **Parallelism**: The spec says 20 candidates per category × 12 T2 categories = 240 tool generations. Should we parallelize the Builder, or run sequentially to keep context usage manageable?

5. **Science field as genuine scaffold**: The spec says the science field must be "demonstrably used." Should the Runner enforce this via AST analysis (check for science-field-specific function names), or is it sufficient that the Builder's prompt includes the field and the resulting code reflects it structurally?

---

**END OF ARCHITECTURE DOCUMENT**

**Status: AWAITING REVIEW. No implementation code will be written until this document is approved.**
