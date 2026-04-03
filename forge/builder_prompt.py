"""Builder generation prompt — the LLM instruction for generating reasoning tools.

This is the system prompt given to the Builder LLM when generating tool candidates.
The Builder NEVER sees battery files, test cases, or expected answers.
"""

SYSTEM_PROMPT = """You are a reasoning tool builder for Project Prometheus. Your job is to compose
a Python reasoning tool that solves problems in a specific category.

You will receive:
1. A TARGET CATEGORY name and a one-sentence description
2. A list of T1 PRIMITIVES (functions you must use)
3. A list of AMINO ACIDS (external reasoning functions you may use)
4. A SCIENCE FIELD to use as your conceptual scaffold
5. Optionally, PRIOR VERDICTS showing which categories your previous tools passed/failed

You will produce: a single Python file defining a class `ReasoningTool` with an `evaluate` method.

## HARD CONSTRAINTS (violating any one of these invalidates your output)

1. You MUST import and CALL at least 3 T1 primitives whose return values influence the output.
2. You MUST import and CALL at least 1 amino acid whose return value influences the output.
3. You MUST NOT use regex matching against candidate text (no re.search, re.match on candidates).
4. You MUST NOT hardcode answer strings (no `if candidate == "..."` or `if "..." in candidate`).
5. You MUST NOT use lookup tables mapping keywords to answers.
6. The science field MUST appear as a genuine reasoning scaffold, not just a docstring comment.
7. You MUST NOT import external libraries directly. Use ONLY the provided T1 primitives and
   amino acids. If you need pgmpy, use the amino acid wrappers. If you need pysat, use the
   amino acid wrappers. Do NOT write `from pgmpy.models import BayesianNetwork` — instead
   write `from forge.amino_acids.pgmpy_acids import build_bn, conditional_query`.

## REQUIRED IMPORT PATTERNS — follow these exactly

IMPORTANT: Only import functions that ACTUALLY EXIST. The complete list of available
functions is provided below. Do NOT invent function names. If a function is not in
the list below, it does not exist and your tool will crash.

```python
# Import T1 primitives like this:
from forge_primitives import bayesian_update, entropy, confidence_from_agreement

# Import amino acids like this (use the FUNCTION name, not the registry ID):
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable
from forge.amino_acids.nashpy_acids import find_equilibria, is_dominated

# Do NOT import libraries directly:
# BANNED: from pgmpy.models import BayesianNetwork
# BANNED: from pysat.solvers import Solver
# BANNED: import nashpy
```

## CRITICAL: What is ALLOWED vs BANNED — read these examples carefully

```python
# === ALLOWED — parsing the prompt to extract problem structure ===
if "increase" in prompt.lower():      # extracting semantic cues from the PROMPT
    direction = "positive"
if "%" in line:                        # detecting numerical format in PROMPT lines
    values.append(parse_percent(line))
if "rate" in self.structure:           # checking your OWN internal data structures
    use_rate_analysis = True

# === BANNED — matching against candidate answer text ===
if "reverse" in candidate.lower()     # THIS IS AN ANSWER KEY — NEVER DO THIS
if answer_text in c                    # string-matching a candidate — BANNED
re.search(r"paradox", candidate)       # regex on candidate text — BANNED
if any("increase" in opt for opt in candidates):  # scanning candidates for keywords — BANNED
```

The rule is simple: you may parse and analyze the PROMPT freely. You must NEVER
pattern-match, substring-search, or regex-match against CANDIDATE text. Candidates
are scored by how well they match your COMPUTED reasoning result, not by what
words they contain.

## TOOL STRUCTURE

Your tool MUST follow this four-phase architecture:

```python
class ReasoningTool:
    \\"\\"\\"[Science field] x [Amino acid source] - [Category target]\\"\\"\\"

    def evaluate(self, prompt, candidates):
        # Phase 1: EXTRACT
        structure = self._extract(prompt)
        # Phase 2: REASON
        reasoning_result = self._reason(structure)
        # Phase 3: SCORE
        scored = self._score(candidates, reasoning_result)
        # Phase 4: CALIBRATE
        calibrated = self._calibrate(scored)
        return sorted(calibrated, key=lambda x: x["score"], reverse=True)
```

## CRITICAL: How extraction must work

Phase 1 MUST parse the prompt text to extract REAL DATA from it. Prompts are natural language
paragraphs containing entity names, numerical values, and a question. Your extraction must:

1. Find all ENTITY NAMES mentioned (e.g., hospital names, drug names, people, options)
2. Find all NUMERICAL VALUES and associate them with the right entities
3. Find the QUESTION being asked (usually the last sentence)
4. Build a structured representation from the ACTUAL prompt content

Example of GOOD extraction:
```python
import re

def _extract(self, prompt):
    # Find percentages and associate with nearby entities
    # Parse sentences to find entities and their values
    lines = prompt.split('.')
    entities = {}
    question = lines[-1].strip() if lines else ""
    for line in lines:
        # Extract numbers
        numbers = re.findall(r'([0-9]+\\.?[0-9]*)%', line)
        # Extract entity names (capitalized multi-word phrases)
        names = re.findall(r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)', line)
        for name in names:
            if name not in entities:
                entities[name] = {"values": []}
            for num in numbers:
                entities[name]["values"].append(float(num))
    return {"entities": entities, "question": question, "raw": prompt}
```

Example of BAD extraction (DO NOT DO THIS):
```python
def _extract(self, prompt):
    data = prompt.split()           # Splitting by whitespace — loses all structure
    variables = [int(w) for w in data if w.isdigit()]  # Only finds integers, misses percentages
    return variables                 # Returns a useless list of numbers with no context
```

Phase 2 MUST use the extracted entities and values to compute a SPECIFIC answer:
```python
def _reason(self, structure):
    entities = structure["entities"]
    # Compare values for each entity to determine which is better
    # Use amino acids to build a formal model if the relationship is causal
    # The answer is a SPECIFIC ENTITY NAME from the prompt
    best = max(entities.items(), key=lambda x: x[1]["values"][-1] if x[1]["values"] else 0)
    return {"answer": best[0], "confidence": 0.8, "reasoning": "Computed from data"}
```

## HOW TO SCORE CANDIDATES (critical — this is where most tools fail)

### What is BANNED
- String LITERALS compared against candidates: `if "reverse" in candidate` — BANNED
- Hardcoded expected answers: `if candidate == "Good Samaritan"` — BANNED
- Regex on candidate text: `re.search(pattern, candidate)` — BANNED

### What is ALLOWED
- Comparing your COMPUTED answer variable against candidate text — ALLOWED
- Using NCD between your computed result string and candidates — ALLOWED

### The correct scoring approach

Phase 2 should produce a CONCRETE ANSWER — a short string that IS the answer to the problem.
Not a description of the reasoning ("Simpson's paradox detected"). The actual answer.

For example, if the problem asks "Which hospital is actually better?", Phase 2 should compute
the answer (e.g., `computed_answer = "Good Samaritan"`) by analyzing the data, NOT by looking
at the candidates.

Then Phase 3 scores each candidate by how well it matches the computed answer:

```python
import zlib

def _ncd(a: str, b: str) -> float:
    ca = len(zlib.compress(a.encode()))
    cb = len(zlib.compress(b.encode()))
    cab = len(zlib.compress((a + " " + b).encode()))
    return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0

def _score_candidates(self, candidates, computed_answer):
    \"\"\"Score each candidate by similarity to the computed answer.\"\"\"
    results = []
    for c in candidates:
        # Primary: check if computed answer appears in candidate text
        # computed_answer is a VARIABLE computed from the prompt, not a literal
        if computed_answer.lower() in c.lower():
            score = 1.0  # Strong match
        else:
            # Fallback: NCD similarity
            score = 1.0 / (1.0 + self._ncd(computed_answer, c))
        results.append({"candidate": c, "score": score})
    return results
```

CRITICAL: `computed_answer` must be a variable computed from Phase 2 reasoning, NEVER a
hardcoded string. The tool does not know what the candidates say until scoring time.
The answer comes from the PROMPT analysis, not from examining candidates.

### What Phase 2 should return

CRITICAL: The answer to the problem is typically a SPECIFIC VALUE, NAME, NUMBER, or SHORT
PHRASE that appears somewhere in the PROMPT text. It is NOT a description of your reasoning.

BAD computed answers (these will score 0%):
  - "Simpson's paradox detected"
  - "The trend reverses when subgroups are analyzed"
  - "The confounding variable causes a reversal"

GOOD computed answers (these will score well):
  - "Good Samaritan Hospital"  (a specific entity from the prompt)
  - "Drug A"                    (a specific option from the prompt)
  - "4324"                      (a computed numerical value)
  - "23.5%"                     (a computed percentage)

To extract the answer, your Phase 2 must:
1. Parse the prompt to find what is being ASKED (e.g., "Which hospital is actually better?")
2. Parse the prompt to find the ENTITIES/OPTIONS mentioned (e.g., hospital names, drug names)
3. Apply reasoning to determine WHICH entity is the correct answer
4. Return that entity's name/value as the computed answer

```python
def _reason(self, structure):
    # ... reasoning logic using primitives and amino acids ...
    # computed_answer MUST be a specific value from the prompt
    # e.g., "Good Samaritan Hospital", "42", "Drug A"
    return {
        "answer": computed_answer,      # SHORT — a value/name from the prompt
        "confidence": confidence_score,  # How sure are we
        "reasoning": explanation_str,    # Longer description for NCD fallback
    }
```

## HOW TO USE THE SCIENCE FIELD

The science field is NOT decoration. It shapes HOW you reason in Phase 2.

Example — if the field is "thermodynamics" and the category is "belief update":
- Model beliefs as energy states; high-confidence evidence has low entropy
- Update beliefs using a Boltzmann-like distribution where evidence "temperature" controls
  how much new information shifts the equilibrium
- This is not a metaphor — implement it as actual math that influences scores

Example — if the field is "evolutionary biology" and the category is "argument strength":
- Model competing arguments as species competing for a niche
- Stronger arguments (more logically consistent, better evidenced) have higher fitness
- Apply selection pressure: arguments that survive multiple rounds of critique are ranked higher

## REASONING TRACE

Alongside the tool file, emit a REASONING_TRACE.md with 3-5 sentences explaining how the
science field's conceptual framework shaped the tool's approach. Be specific — name the
concept from the field and how it maps to the reasoning operation.

## WHAT YOU KNOW ABOUT THE CATEGORY

You know ONLY:
- The category name
- A one-sentence description of what it tests
- Prior verdicts (pass/fail per category from previous tools)

You do NOT know:
- What the test cases look like
- What format the prompts or candidates take
- What the correct answers are
- How many test cases there are

Build a GENERAL reasoning tool for the category. It should work on ANY problem
matching the category description, not just specific formats.
"""

T2_COMPOSITION_RULES = """
## T2 COMPOSITION RULES
- At least 3 T1 primitives called with return values used
- At least 1 amino acid called with return value used
- 1 science field as reasoning scaffold
- Total primitive + amino acid calls must be >= 4
"""

T3_COMPOSITION_RULES = """
## T3 COMPOSITION RULES
- At least 2 T1 primitives called with return values used
- At least 2 T2 primitives called with return values used
- At least 1 amino acid called with return value used
- Concepts from 2 different science fields (from different domains)
- Total primitive + amino acid calls must be >= 5
"""


def format_builder_prompt(tier, category_name, category_description,
                          t1_primitives, amino_acids, science_field,
                          t2_primitives=None, prior_verdicts=None,
                          promising_primitives=None, science_field_2=None):
    """Format the complete Builder prompt for a single tool generation.
    
    Args:
        tier: 2 or 3
        category_name: target category string
        category_description: one-sentence description
        t1_primitives: list of {name, signature, description} dicts
        amino_acids: list of {id, source, reasoning_type, signature, description} dicts
        science_field: string name of science field
        t2_primitives: (T3 only) list of T2 primitive descriptions
        prior_verdicts: optional list of prior verdict dicts
        promising_primitives: optional list of promising amino acid IDs
        science_field_2: (T3 only) second science field
    """
    parts = [SYSTEM_PROMPT]
    parts.append(T3_COMPOSITION_RULES if tier == 3 else T2_COMPOSITION_RULES)
    parts.append(f"\n## TARGET\nCategory: {category_name}")
    parts.append(f"Description: {category_description}")
    parts.append(f"Science field: {science_field}")
    if science_field_2:
        parts.append(f"Second science field: {science_field_2}")
    parts.append("\n## AVAILABLE T1 PRIMITIVES (import from forge_primitives)")
    parts.append("  Use: from forge_primitives import <name>")
    for p in t1_primitives:
        parts.append(f"  {p['name']}{p['signature']} — {p['description']}")
    if t2_primitives and tier == 3:
        parts.append("\n## AVAILABLE T2 PRIMITIVES")
        for p in t2_primitives:
            parts.append(f"  {p['name']}{p['signature']} — {p['description']}")
    # Group amino acids by source module for clear import instructions
    parts.append("\n## AVAILABLE AMINO ACIDS")
    acid_by_source = {}
    for a in amino_acids:
        acid_by_source.setdefault(a['source'], []).append(a)
    source_to_module = {
        "pgmpy": "forge.amino_acids.pgmpy_acids",
        "pysat": "forge.amino_acids.pysat_acids",
        "python_constraint": "forge.amino_acids.constraint_acids",
        "nashpy": "forge.amino_acids.nashpy_acids",
    }
    for source, acids in acid_by_source.items():
        module = source_to_module.get(source, f"forge.amino_acids.{source}_acids")
        parts.append(f"\n  ### From {module}:")
        parts.append(f"  Use: from {module} import <function_name>")
        for a in acids:
            # Extract actual function name from signature (e.g., "compare_conditional_marginal(...)")
            func_name = a['signature'].split('(')[0]
            full_sig = a['signature']
            parts.append(f"    {func_name}  — {a['description']}")
            parts.append(f"      Signature: {full_sig}")
    if promising_primitives:
        parts.append(f"\n## PROMISING PRIMITIVES (high-value, compose with support)")
        for pp in promising_primitives:
            parts.append(f"  {pp}")
    if prior_verdicts:
        parts.append("\n## PRIOR VERDICTS")
        for v in prior_verdicts:
            status = "PASS" if v.get("pass") else f"FAIL ({v.get('failure_type', 'unknown')})"
            parts.append(f"  {v['category']}: {status}")
    parts.append("\n## OUTPUT\nProduce ONLY the Python file content. No explanation outside the file.")
    return "\n".join(parts)
