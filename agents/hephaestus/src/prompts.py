"""Prompt templates for Hephaestus code generation.

Supports multi-frame forge strategy:
  Frame A: Structural Parser (current default)
  Frame B: Constructive Computer (computation-first)
  Frame C: Dynamics Tracker (state evolution)
  Frame D: Judgment Calibrator (epistemic honesty)

Frame selection: weighted rotation per forge attempt.
"""

import logging
import random

log = logging.getLogger("hephaestus.prompts")

# Frame weights (Athena-recommended allocation)
FRAME_WEIGHTS = {"A": 10, "B": 35, "C": 30, "D": 25}
_frame_rng = random.Random(42)

CODE_GEN_PROMPT = """\
You are a computational engineer building reasoning tools.

A rigorous theoretical analysis has confirmed this as a high-value combination:
Concepts: {concept_1} x {concept_2} x {concept_3}

The analysis concluded:
{nous_response_text}

Ratings: Reasoning {r}/10, Metacognition {m}/10, Hypothesis Generation {h}/10
{coeus_section}
This combination has already passed theoretical review. Your job is implementation.

Implement this as a Python class with the following interface:

```python
class ReasoningTool:
    def __init__(self):
        # Initialize any state
        pass

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        \"\"\"
        Given a prompt and candidate answers, return a ranked list of dicts:
        [{{"candidate": str, "score": float, "reasoning": str}}, ...]
        Higher score = more likely correct.
        \"\"\"
        pass

    def confidence(self, prompt: str, answer: str) -> float:
        \"\"\"
        Given a prompt and a proposed answer, return confidence 0-1.
        0 = definitely wrong, 1 = definitely correct.
        \"\"\"
        pass
```

--- Quality Floor ---
A baseline tool using Normalized Compression Distance (zlib NCD) achieves
{ncd_accuracy}% accuracy and {ncd_calibration}% calibration. Your tool MUST beat these.

Key patterns that WORK (from our best tools at 55-94% accuracy):
- Structural parsing: extract negations, comparatives, conditionals from prompt
- Numeric evaluation: detect number comparisons, compute float("9.11") < float("9.9")
- Constructive computation: actually solve Bayesian posteriors, PEMDAS expressions, \
rate/work problems, modular arithmetic — CALCULATE answers, don't just pattern-match
- Constraint propagation: transitivity, modus tollens, subject-object roles
- NCD as tiebreaker only (not primary signal), max 15% of final score

Key patterns that DON'T work:
- Hash-to-vector similarity (measures string noise, not reasoning)
- Bag-of-words overlap (gameable by echoing prompt)
- Pure NCD (cannot distinguish short candidates like "Yes" vs "No")
- Returning high confidence on everything (overconfidence kills RLVF signal)

--- CRITICAL: Epistemic Honesty (Tier B Reasoning) ---
Your tool will be tested on TWO tiers:
  Tier A: Parsing traps (deterministic correct answer from structure)
  Tier B: Judgment traps (recognizing ambiguity, presupposition, insufficiency)

Tier B categories include: presupposition ("Have you stopped X?"), scope ambiguity \
("Every X did a Y" — same Y?), pronoun ambiguity ("John told Bill he was wrong" — \
who?), false dichotomy ("Either A or B" — other options exist), survivorship bias, \
sunk cost fallacy, regression to mean, validity vs truth, argument strength.

Your confidence() method MUST:
- Return < 0.3 when the prompt is ambiguous, contains a presupposition, or is unanswerable
- Return < 0.3 when no structural parser matches (honest uncertainty)
- NEVER return > 0.9 unless computation produced a definitive answer
- Base confidence on QUESTION PROPERTIES, not answer score

Implement a _meta_confidence() method that checks the PROMPT for:
1. Presupposition: "Have you stopped/quit X?", "Why did X fail/stop?"
2. Scope ambiguity: "Every X ... a Y" (same Y or different Y?)
3. Pronoun ambiguity: "X told Y he/she was..." + "who?" question
4. False dichotomy: "Either A or B" without exhaustive options
5. Subjectivity: "best/worst/favorite" without measurable criteria
6. Unanswerability: questions requiring information not in the prompt

confidence() should call _meta_confidence() and cap the return value.
A tool that says "I don't know" on ambiguous questions is MORE valuable \
than one that confidently picks an answer. Epistemic honesty matters \
more than raw accuracy for RLVF training signal.

Requirements:
- You MUST produce working code. Do not decline or return None.
- Even if the connection seems abstract, find a computational analogy and implement it.
- Imperfect implementations are acceptable — a rough approximation that captures the \
core mechanism is better than no implementation.
- Under 200 lines
- Only numpy and standard library (no torch, no sklearn, no external deps)
- Must be deterministic given the same inputs
- Include a brief docstring explaining the mechanism
- Use only ASCII characters in code and strings (no unicode symbols)
- Score decomposition: structural >= 50%, computation >= 20%, NCD <= 15%
"""

FRAME_B_SUFFIX = """
--- FRAME B: CONSTRUCTIVE COMPUTATION ---
Your PRIMARY objective is to COMPUTE answers, not parse patterns.

For numeric questions: extract numbers as floats, perform arithmetic.
For probability questions: compute Bayesian posteriors, expected values.
For temporal questions: build timelines, compute durations, detect ordering.
For causal questions: trace causal chains, compute interventional effects.
For compositional questions: chain multiple reasoning steps sequentially.

Your tool MUST produce a score WITHOUT NCD. NCD may contribute as a secondary
signal, but the tool must function correctly if NCD is removed entirely.
Build real computation pathways — the tool should work on structure and math alone.
If you cannot compute the answer, return LOW confidence (< 0.3) rather than
falling back to string similarity.

Score decomposition: computation >= 40%, structural >= 30%, NCD as optional tiebreaker only.
The test will include: base rate neglect, expected value, temporal ordering,
rate problems, causal intervention, Simpson's paradox, age reasoning,
scheduling conflicts, and multi-step compositional chains.
"""

FRAME_C_SUFFIX = """
--- FRAME C: DYNAMICS TRACKER ---
Your PRIMARY objective is to track STATE EVOLUTION across reasoning steps.

Model the reasoning as a dynamical system. Each premise updates a state vector.
Track how the answer evolves as you process premises sequentially.
Use trajectory stability to judge confidence — stable answers under premise
reordering are more trustworthy than fragile ones.

Implement at least one of: reservoir dynamics, Lyapunov stability analysis,
Markov chain convergence, or recurrent state estimation (Kalman-style).
Score based on trajectory properties — convergence rate, basin stability,
divergence detection — not just static feature matching.

NCD must NOT be the primary scoring mechanism.
Score decomposition: dynamics/state >= 40%, structural >= 20%, NCD <= 15%.
The test will include: temporal sequence reconstruction, rate of change
detection, causal ordering, multi-step chains, and perturbation robustness.
"""

FRAME_D_SUFFIX = """
--- FRAME D: JUDGMENT CALIBRATOR ---
Your PRIMARY objective is EPISTEMIC HONESTY — knowing what you don't know.

Before scoring candidates, classify the QUESTION:
1. Is it ambiguous? (scope, pronoun, presupposition)
2. Is it unanswerable from the given information?
3. Does it contain a false dichotomy or loaded assumption?
4. Does it require information not present in the prompt?

If any of these fire, cap confidence at 0.25 regardless of answer quality.
Implement a _meta_confidence() method that evaluates the prompt itself.

You will be tested on: presupposition traps, scope ambiguity, false dichotomy,
survivorship bias, sunk cost fallacy, argument strength evaluation,
confidence calibration, intention vs outcome, and strategic deception.

CRITICAL CONSTRAINT: Tier B honesty must be above 0.95, BUT Tier A accuracy
must also exceed 30%. Honesty without competence is not the goal. A tool that
returns low confidence on everything is perfectly calibrated and completely
useless. You must STILL correctly answer parsing traps (numeric comparison,
transitivity, modus tollens, etc.) while being honest about ambiguous ones.

Score decomposition: judgment >= 40%, structural >= 30%, NCD <= 15%.
"""

COEUS_SECTION_TEMPLATE = """
--- Causal Intelligence (Coeus) ---
{enrichment_text}
---
"""

COEUS_FRAME_B_OVERRIDE = """
--- Causal Intelligence (Coeus) — COMPUTATION FRAME ---
{enrichment_text}

OVERRIDE: For this tool, prioritize COMPUTATIONAL implementation over structural
parsing. Implement actual mathematical operations: Bayesian posteriors, algebraic
solvers, temporal schedulers, causal graph traversal. If you cannot compute the
answer, return low confidence. The tool must produce a score WITHOUT NCD — NCD
may be a secondary tiebreaker only, and the tool must function if NCD is removed.
---
"""

COEUS_FRAME_C_OVERRIDE = """
--- Causal Intelligence (Coeus) — DYNAMICS FRAME ---
{enrichment_text}

OVERRIDE: For this tool, model reasoning as STATE EVOLUTION. Implement trajectory
tracking: how does the scoring state change as you process each premise? Use
reservoir dynamics, recurrent state updates, or convergence detection. Score based
on trajectory stability, not static features.
---
"""

COEUS_FRAME_D_OVERRIDE = """
--- Causal Intelligence (Coeus) — JUDGMENT FRAME ---
{enrichment_text}

OVERRIDE: For this tool, prioritize EPISTEMIC HONESTY. Detect ambiguity,
presupposition, and unanswerable questions BEFORE scoring candidates. Return
low confidence (< 0.3) on genuinely uncertain questions. BUT: Tier A accuracy
must remain above 30%. Honesty without competence is useless — you must still
correctly answer clear parsing traps while being honest about ambiguous ones.
---
"""


# Cache NCD baseline scores (computed once)
_ncd_baseline_cache = None


def _get_ncd_baseline_scores() -> tuple[int, int]:
    """Get NCD baseline accuracy/calibration as percentages."""
    global _ncd_baseline_cache
    if _ncd_baseline_cache is None:
        try:
            from test_harness import run_ncd_baseline
            results = run_ncd_baseline()
            _ncd_baseline_cache = (
                int(results["accuracy"] * 100),
                int(results["calibration"] * 100),
            )
        except Exception as e:
            log.debug("NCD baseline computation failed, using fallback: %s", e)
            _ncd_baseline_cache = (40, 40)  # conservative fallback
    return _ncd_baseline_cache


def select_frame() -> str:
    """Select a frame using weighted rotation. Returns 'A', 'B', 'C', or 'D'."""
    frames = list(FRAME_WEIGHTS.keys())
    weights = list(FRAME_WEIGHTS.values())
    frame = _frame_rng.choices(frames, weights=weights, k=1)[0]
    return frame


def build_code_gen_prompt(concept_names: list[str], response_text: str,
                          ratings: dict, enrichment: dict | None = None,
                          frame: str | None = None) -> str:
    """Build the code generation prompt from Nous result fields.

    Args:
        concept_names: list of 3 concept names
        response_text: Nous response text
        ratings: Nous ratings dict
        enrichment: optional Coeus enrichment dict (with 'enrichment_text' key)
        frame: 'A', 'B', 'C', or 'D'. If None, auto-selects via weighted rotation.
    """
    if len(concept_names) < 3:
        return "ERROR: need 3 concepts"

    if frame is None:
        frame = select_frame()

    # Select Coeus enrichment template based on frame
    coeus_section = ""
    if enrichment and enrichment.get("enrichment_text"):
        if frame == "B":
            coeus_section = COEUS_FRAME_B_OVERRIDE.format(
                enrichment_text=enrichment["enrichment_text"])
        elif frame == "C":
            coeus_section = COEUS_FRAME_C_OVERRIDE.format(
                enrichment_text=enrichment["enrichment_text"])
        elif frame == "D":
            coeus_section = COEUS_FRAME_D_OVERRIDE.format(
                enrichment_text=enrichment["enrichment_text"])
        else:
            coeus_section = COEUS_SECTION_TEMPLATE.format(
                enrichment_text=enrichment["enrichment_text"])

    ncd_acc, ncd_cal = _get_ncd_baseline_scores()

    # Build base prompt
    prompt = CODE_GEN_PROMPT.format(
        concept_1=concept_names[0],
        concept_2=concept_names[1],
        concept_3=concept_names[2],
        nous_response_text=response_text,
        r=ratings.get("reasoning", "?"),
        m=ratings.get("metacognition", "?"),
        h=ratings.get("hypothesis_generation", "?"),
        coeus_section=coeus_section,
        ncd_accuracy=ncd_acc,
        ncd_calibration=ncd_cal,
    )

    # Append frame-specific suffix
    if frame == "B":
        prompt += FRAME_B_SUFFIX
    elif frame == "C":
        prompt += FRAME_C_SUFFIX
    elif frame == "D":
        prompt += FRAME_D_SUFFIX

    log.info("Frame: %s (%s)", frame,
             {"A": "Structural", "B": "Constructive", "C": "Dynamics", "D": "Judgment"}.get(frame, "?"))

    return prompt
