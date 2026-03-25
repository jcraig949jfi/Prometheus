"""Prompt templates for Hephaestus code generation."""

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

Key patterns that WORK (from our best tools at 53-60% accuracy):
- Structural parsing: extract negations, comparatives, conditionals from prompt
- Numeric evaluation: detect number comparisons, compute float("9.11") < float("9.9")
- Constraint propagation: transitivity, modus tollens, subject-object roles
- NCD as tiebreaker only (not primary signal)

Key patterns that DON'T work:
- Hash-to-vector similarity (measures string noise, not reasoning)
- Bag-of-words overlap (gameable by echoing prompt)
- Pure NCD (cannot distinguish short candidates like "Yes" vs "No")

Requirements:
- You MUST produce working code. Do not decline or return None.
- Even if the connection seems abstract, find a computational analogy and implement it.
- Imperfect implementations are acceptable — a rough approximation that captures the \
core mechanism is better than no implementation.
- Under 150 lines
- Only numpy and standard library (no torch, no sklearn, no external deps)
- Must be deterministic given the same inputs
- Include a brief docstring explaining the mechanism
- Use only ASCII characters in code and strings (no unicode symbols)
"""

COEUS_SECTION_TEMPLATE = """
--- Causal Intelligence (Coeus) ---
{enrichment_text}
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
        except Exception:
            _ncd_baseline_cache = (40, 40)  # conservative fallback
    return _ncd_baseline_cache


def build_code_gen_prompt(concept_names: list[str], response_text: str,
                          ratings: dict, enrichment: dict | None = None) -> str:
    """Build the code generation prompt from Nous result fields.

    Args:
        concept_names: list of 3 concept names
        response_text: Nous response text
        ratings: Nous ratings dict
        enrichment: optional Coeus enrichment dict (with 'enrichment_text' key)
    """
    coeus_section = ""
    if enrichment and enrichment.get("enrichment_text"):
        coeus_section = COEUS_SECTION_TEMPLATE.format(
            enrichment_text=enrichment["enrichment_text"],
        )

    ncd_acc, ncd_cal = _get_ncd_baseline_scores()

    return CODE_GEN_PROMPT.format(
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
