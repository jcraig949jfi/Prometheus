"""Prompt templates for Hephaestus code generation."""

CODE_GEN_PROMPT = """\
You are a computational engineer building reasoning tools.

A theoretical analysis identified a promising combination:
Concepts: {concept_1} x {concept_2} x {concept_3}

The analysis said:
{nous_response_text}

Ratings: Reasoning {r}/10, Metacognition {m}/10, Hypothesis Generation {h}/10

Your task: implement this as a Python class with the following interface:

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

Requirements:
- Under 150 lines
- Only numpy and standard library (no torch, no sklearn, no external deps)
- Must be deterministic given the same inputs
- If the combination is genuinely unproductive for code, say so and return None
- Include a brief docstring explaining the mechanism
"""


def build_code_gen_prompt(concept_names: list[str], response_text: str,
                          ratings: dict) -> str:
    """Build the code generation prompt from Nous result fields."""
    return CODE_GEN_PROMPT.format(
        concept_1=concept_names[0],
        concept_2=concept_names[1],
        concept_3=concept_names[2],
        nous_response_text=response_text,
        r=ratings.get("reasoning", "?"),
        m=ratings.get("metacognition", "?"),
        h=ratings.get("hypothesis_generation", "?"),
    )
