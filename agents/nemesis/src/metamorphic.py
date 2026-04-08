"""Metamorphic relations for adversarial task generation.

Each MR is a formal specification of how inputs and outputs should co-vary.
MRs can be composed to produce tasks at any point in the (complexity, obfuscation) space.

This replaces ad-hoc mutation categories with a principled framework grounded
in the metamorphic testing literature.
"""

import random
import re
from dataclasses import dataclass, field
from typing import Callable

# Type alias for a transform function
# (prompt, candidates, correct, rng) -> (new_prompt, new_candidates, new_correct)
TransformFn = Callable[
    [str, list[str], str, random.Random],
    tuple[str, list[str], str] | None
]


@dataclass
class MetamorphicRelation:
    """A formal metamorphic relation."""
    name: str
    transform: TransformFn
    expected: str  # "same" | "flip" | "computed" (how correct answer changes)
    complexity_delta: int = 0
    obfuscation_delta: int = 0
    category: str = ""


# ---------------------------------------------------------------------------
# Transform implementations
# ---------------------------------------------------------------------------

def _comparison_flip(prompt: str, candidates: list[str], correct: str,
                     rng: random.Random) -> tuple[str, list[str], str] | None:
    """Swap the two values in a comparison question."""
    m = re.search(r"[Ii]s\s+([\d.]+)\s+(larger|greater|bigger|smaller|less)\s+than\s+([\d.]+)",
                  prompt)
    if not m:
        return None
    a, comp, b = m.group(1), m.group(2), m.group(3)
    new_prompt = prompt[:m.start()] + f"Is {b} {comp} than {a}" + prompt[m.end():]
    # Flipping values flips the answer
    new_correct = "No" if correct.lower().startswith("yes") else "Yes"
    return new_prompt, candidates, new_correct


def _verb_inversion(prompt: str, candidates: list[str], correct: str,
                    rng: random.Random) -> tuple[str, list[str], str] | None:
    """Replace 'larger' with 'smaller' etc."""
    swaps = {
        "larger": "smaller", "smaller": "larger",
        "greater": "less", "less": "greater",
        "taller": "shorter", "shorter": "taller",
        "heavier": "lighter", "lighter": "heavier",
        "bigger": "smaller",
    }
    new_prompt = prompt
    swapped = False
    for old, new in swaps.items():
        if old in prompt.lower():
            new_prompt = re.sub(old, new, prompt, flags=re.IGNORECASE)
            swapped = True
            break
    if not swapped:
        return None
    new_correct = "No" if correct.lower().startswith("yes") else "Yes"
    return new_prompt, candidates, new_correct


def _negation_inject(prompt: str, candidates: list[str], correct: str,
                     rng: random.Random) -> tuple[str, list[str], str] | None:
    """Add negation to change the expected answer."""
    if " not " in prompt.lower() or "n't " in prompt.lower():
        return None  # already negated, skip

    # Find the question or conclusion sentence — negate THERE, not in arbitrary premises
    # Look for question sentence first, then conclusion, then fall back to last sentence
    q_match = re.search(r"([^.!?\n]*\?)", prompt)
    concl_match = re.search(r"(Conclusion:[^\n.]*\.?)", prompt, re.IGNORECASE)
    target = q_match or concl_match
    if not target:
        # Fall back to last sentence
        sentences = re.split(r'(?<=[.!?])\s+', prompt)
        if not sentences:
            return None
        target_text = sentences[-1]
        target_start = prompt.rfind(target_text)
    else:
        target_text = target.group(1)
        target_start = target.start()

    # Add "not" before key verb WITHIN the target sentence
    for pattern, replacement in [
        (r"(\bis\b)", "is not"),
        (r"(\bare\b)", "are not"),
        (r"(\bcan\b)", "cannot"),
    ]:
        m = re.search(pattern, target_text)
        if m:
            abs_start = target_start + m.start()
            abs_end = target_start + m.end()
            new_prompt = prompt[:abs_start] + replacement + prompt[abs_end:]
            new_correct = "No" if correct.lower().startswith("yes") else "Yes"
            return new_prompt, candidates, new_correct
    return None


def _premise_shuffle(prompt: str, candidates: list[str], correct: str,
                     rng: random.Random) -> tuple[str, list[str], str] | None:
    """Shuffle the order of premises in a multi-premise prompt."""
    # Structured argument prompts: preserve header/conclusion, shuffle only premises
    premise_lines = re.findall(r"(Premise\s+\d+:\s*.+?)(?=\n|Premise\s+\d+:|Conclusion:|$)",
                               prompt, re.IGNORECASE)
    if len(premise_lines) >= 2:
        rng.shuffle(premise_lines)
        new_prompt = prompt
        # Replace original premises in order with shuffled ones
        originals = list(re.finditer(r"(Premise\s+\d+:\s*.+?)(?=\n|Premise\s+\d+:|Conclusion:|$)",
                                     prompt, re.IGNORECASE))
        for orig, shuffled in zip(reversed(originals), reversed(premise_lines)):
            new_prompt = new_prompt[:orig.start()] + shuffled + new_prompt[orig.end():]
        return new_prompt, candidates, correct

    # Fallback: split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', prompt)
    if len(sentences) < 2:
        parts = re.split(r',\s+and\s+|\s+and\s+|,\s+', prompt)
        if len(parts) < 2:
            return None
        sentences = parts

    # Separate the question (last part) from premises
    question = sentences[-1] if "?" in sentences[-1] else None
    premises = sentences[:-1] if question else sentences

    if len(premises) < 2:
        return None

    rng.shuffle(premises)
    if question:
        new_prompt = ". ".join(premises) + ". " + question
    else:
        new_prompt = ". ".join(premises)

    return new_prompt, candidates, correct  # answer unchanged


def _distractor_add(prompt: str, candidates: list[str], correct: str,
                    rng: random.Random) -> tuple[str, list[str], str] | None:
    """Add an irrelevant but plausible-sounding detail."""
    distractors = [
        "Note that this is a common type of problem.",
        "The temperature outside is 72 degrees.",
        "This question was asked by a professor of mathematics.",
        "Consider that there are many ways to approach this.",
        "Interestingly, most people get this wrong.",
        "The answer might surprise you.",
        "Think carefully before answering.",
        "This is often confused with a different problem.",
    ]
    distractor = rng.choice(distractors)
    # Insert before the question mark or at the end
    if "?" in prompt:
        q_idx = prompt.rindex("?")
        # Insert before the last sentence
        last_period = prompt.rfind(".", 0, q_idx)
        if last_period > 0:
            new_prompt = prompt[:last_period + 1] + " " + distractor + prompt[last_period + 1:]
        else:
            new_prompt = distractor + " " + prompt
    else:
        new_prompt = prompt + " " + distractor
    return new_prompt, candidates, correct


def _passive_voice(prompt: str, candidates: list[str], correct: str,
                   rng: random.Random) -> tuple[str, list[str], str] | None:
    """Convert active voice constructions to passive."""
    # "The dog chased the cat" -> "The cat was chased by the dog"
    m = re.search(r"[Tt]he\s+(\w+)\s+(chased|caught|followed|hit|bit|pushed|watched|spotted)\s+the\s+(\w+)",
                  prompt)
    if m:
        agent, verb, patient = m.group(1), m.group(2), m.group(3)
        passive = f"The {patient} was {verb} by the {agent}"
        new_prompt = prompt[:m.start()] + passive + prompt[m.end():]
        return new_prompt, candidates, correct
    return None


def _paraphrase(prompt: str, candidates: list[str], correct: str,
                rng: random.Random) -> tuple[str, list[str], str] | None:
    """Rewrite the prompt preserving meaning but changing surface form."""
    replacements = [
        (r"[Ii]s\s+([\d.]+)\s+larger\s+than\s+([\d.]+)\s*\?",
         lambda m: f"Between {m.group(1)} and {m.group(2)}, which quantity is greater?"),
        (r"[Ii]s\s+([\d.]+)\s+larger\s+than\s+([\d.]+)\s*\?",
         lambda m: f"Compare {m.group(1)} and {m.group(2)}. Which has the higher value?"),
        (r"[Ww]ho\s+is\s+(?:the\s+)?tallest\s*\?",
         lambda _: "Which person has the greatest height?"),
        (r"[Ww]ho\s+was\s+being\s+chased\s*\?",
         lambda _: "Which one was the target of the pursuit?"),
        (r"[Hh]ow\s+many\s+(?:are\s+)?left\s*\?",
         lambda _: "What is the remaining count?"),
        (r"[Ww]hat\s+place\s+are\s+you\s+in\s*\?",
         lambda _: "What is your position in the race?"),
        (r"[Ii]s\s+it\s+raining\s*\?",
         lambda _: "Can we conclude that precipitation is occurring?"),
    ]
    for pattern, replacement_fn in rng.sample(replacements, len(replacements)):
        m = re.search(pattern, prompt)
        if m:
            new_prompt = prompt[:m.start()] + replacement_fn(m) + prompt[m.end():]
            return new_prompt, candidates, correct
    return None


def _chain_extend(prompt: str, candidates: list[str], correct: str,
                  rng: random.Random) -> tuple[str, list[str], str] | None:
    """Add elements to a transitivity chain."""
    # Find "A is taller than B" patterns
    comps = list(re.finditer(
        r"(\w+)\s+is\s+(?:taller|larger|greater|heavier|older)\s+than\s+(\w+)",
        prompt, re.IGNORECASE
    ))
    if not comps:
        return None

    # Find the end of the chain (the "smallest" entity)
    all_greater = set()
    all_lesser = set()
    for m in comps:
        all_greater.add(m.group(1))
        all_lesser.add(m.group(2))
    chain_end = all_lesser - all_greater
    if not chain_end:
        return None

    end_name = next(iter(chain_end))
    new_names = ["Zara", "Quinn", "Wren", "Kai", "Sage"]
    new_name = rng.choice(new_names)

    # Get the comparison word from the first match
    comp_word = re.search(r"is\s+(taller|larger|greater|heavier|older)", prompt, re.IGNORECASE)
    comp = comp_word.group(1) if comp_word else "taller"

    # Add new link at the end of the chain
    addition = f" {end_name} is {comp} than {new_name}."
    # Insert before the question
    q_idx = prompt.find("?")
    if q_idx > 0:
        last_period = prompt.rfind(".", 0, q_idx)
        if last_period > 0:
            new_prompt = prompt[:last_period + 1] + addition + prompt[last_period + 1:]
        else:
            new_prompt = prompt + addition
    else:
        new_prompt = prompt + addition

    # Correct answer should still be the same (we extended the bottom, not the top)
    return new_prompt, candidates, correct


def _conditional_weaken(prompt: str, candidates: list[str], correct: str,
                        rng: random.Random) -> tuple[str, list[str], str] | None:
    """Weaken a conditional: 'if P then Q' -> 'if P then Q might be true'."""
    # Match only the FIRST if-then in the prompt; require 'then' keyword to avoid
    # partial captures, and stop at sentence boundary (period, comma, newline).
    m = re.search(r"[Ii]f\s+(.+?),\s+then\s+([^.,\n]+)(?:\.|,|$)", prompt)
    if not m:
        return None
    ante, cons = m.group(1).strip(), m.group(2).strip()
    if len(cons.split()) < 2:
        return None  # consequent too short, would produce garbled output
    weakened = f"If {ante}, then {cons} might be true"
    new_prompt = prompt[:m.start()] + weakened + prompt[m.end():]
    # Weakened conditional makes modus tollens uncertain
    new_correct = "Not enough information"
    new_candidates = list(candidates)
    if new_correct not in new_candidates:
        new_candidates.append(new_correct)
    return new_prompt, new_candidates, new_correct


def _affirm_consequent(prompt: str, candidates: list[str], correct: str,
                       rng: random.Random) -> tuple[str, list[str], str] | None:
    """Tempt with affirming the consequent fallacy."""
    m = re.search(r"[Ii]f\s+(.+?),?\s+(?:then\s+)?(.+?)\.", prompt)
    if not m:
        return None
    ante, cons = m.group(1).strip(), m.group(2).strip()
    # "If P then Q. Q is true. Is P true?" -> No (affirming consequent)
    new_prompt = f"If {ante}, then {cons}. {cons.capitalize()}. Is it the case that {ante}?"
    new_candidates = ["Yes", "No", "Not enough information"]
    new_correct = "Not enough information"
    return new_prompt, new_candidates, new_correct


def _numeric_distractor(prompt: str, candidates: list[str], correct: str,
                        rng: random.Random) -> tuple[str, list[str], str] | None:
    """Add a misleading numeric fact."""
    distractors = [
        "Note that {a} has more decimal places than {b}.",
        "The difference between them is {diff}.",
        "If you add them together you get {total}.",
        "The ratio of {a} to {b} is approximately {ratio}.",
    ]
    nums = re.findall(r"\b(\d+\.?\d*)\b", prompt)
    if len(nums) < 2:
        return None
    a, b = float(nums[0]), float(nums[1])
    template = rng.choice(distractors)
    distractor = template.format(
        a=nums[0], b=nums[1],
        diff=f"{abs(a-b):.4f}",
        total=f"{a+b:.2f}",
        ratio=f"{a/b:.3f}" if b != 0 else "undefined",
    )
    q_idx = prompt.find("?")
    if q_idx > 0:
        new_prompt = prompt[:q_idx] + " " + distractor + " " + prompt[q_idx:]
    else:
        new_prompt = prompt + " " + distractor
    return new_prompt, candidates, correct


def _scale_transform(prompt: str, candidates: list[str], correct: str,
                     rng: random.Random) -> tuple[str, list[str], str] | None:
    """Multiply all numbers by a constant. Ordering should be preserved."""
    # Exclude numbers that are labels (Premise 1, Step 2) or inside times (14:30)
    nums = [m for m in re.finditer(r"\b(\d+\.?\d*)\b", prompt)
            if not re.match(r"(?:Premise|Step|Task|Phase)\s+$", prompt[:m.start()], re.IGNORECASE)
            and not re.match(r":", prompt[m.end():m.end()+1])]
    if len(nums) < 2:
        return None
    scale = rng.choice([10, 100, 0.1, 0.01, 7, 13])
    new_prompt = prompt
    # Replace from right to left to preserve positions
    for m in reversed(nums):
        old_val = float(m.group(1))
        new_val = old_val * scale
        # Format to avoid floating point ugliness
        if new_val == int(new_val):
            new_str = str(int(new_val))
        else:
            new_str = f"{new_val:.4f}".rstrip("0").rstrip(".")
        new_prompt = new_prompt[:m.start()] + new_str + new_prompt[m.end():]

    # Update candidates if they contain numbers
    new_candidates = []
    for cand in candidates:
        cand_nums = list(re.finditer(r"\$?(\d+\.?\d*)", cand))
        new_cand = cand
        for cm in reversed(cand_nums):
            old_val = float(cm.group(1))
            new_val = old_val * scale
            prefix = "$" if cand[cm.start()] == "$" else ""
            if new_val == int(new_val):
                new_str = prefix + str(int(new_val))
            else:
                new_str = prefix + f"{new_val:.4f}".rstrip("0").rstrip(".")
            new_cand = new_cand[:cm.start()] + new_str + new_cand[cm.end():]
        new_candidates.append(new_cand)

    # Scale correct answer too
    new_correct = correct
    cand_nums = list(re.finditer(r"\$?(\d+\.?\d*)", correct))
    for cm in reversed(cand_nums):
        old_val = float(cm.group(1))
        new_val = old_val * scale
        prefix = "$" if correct[cm.start()] == "$" else ""
        if new_val == int(new_val):
            new_str = prefix + str(int(new_val))
        else:
            new_str = prefix + f"{new_val:.4f}".rstrip("0").rstrip(".")
        new_correct = new_correct[:cm.start()] + new_str + new_correct[cm.end():]

    return new_prompt, new_candidates, new_correct


# ---------------------------------------------------------------------------
# MR Registry
# ---------------------------------------------------------------------------

METAMORPHIC_RELATIONS = [
    MetamorphicRelation("comparison_flip", _comparison_flip, "flip",
                        complexity_delta=0, obfuscation_delta=0,
                        category="comparison"),
    MetamorphicRelation("verb_inversion", _verb_inversion, "flip",
                        complexity_delta=0, obfuscation_delta=1,
                        category="comparison"),
    MetamorphicRelation("negation_inject", _negation_inject, "flip",
                        complexity_delta=1, obfuscation_delta=1,
                        category="negation"),
    MetamorphicRelation("premise_shuffle", _premise_shuffle, "same",
                        complexity_delta=0, obfuscation_delta=2,
                        category="structural"),
    MetamorphicRelation("distractor_add", _distractor_add, "same",
                        complexity_delta=0, obfuscation_delta=3,
                        category="structural"),
    MetamorphicRelation("passive_voice", _passive_voice, "same",
                        complexity_delta=0, obfuscation_delta=3,
                        category="semantic"),
    MetamorphicRelation("paraphrase", _paraphrase, "same",
                        complexity_delta=0, obfuscation_delta=5,
                        category="semantic"),
    MetamorphicRelation("chain_extend", _chain_extend, "same",
                        complexity_delta=2, obfuscation_delta=0,
                        category="complexity"),
    MetamorphicRelation("conditional_weaken", _conditional_weaken, "computed",
                        complexity_delta=2, obfuscation_delta=1,
                        category="logic"),
    MetamorphicRelation("affirm_consequent", _affirm_consequent, "computed",
                        complexity_delta=3, obfuscation_delta=1,
                        category="logic"),
    MetamorphicRelation("numeric_distractor", _numeric_distractor, "same",
                        complexity_delta=1, obfuscation_delta=4,
                        category="numeric"),
    MetamorphicRelation("scale_transform", _scale_transform, "same",
                        complexity_delta=0, obfuscation_delta=2,
                        category="numeric"),
]

MR_BY_NAME = {mr.name: mr for mr in METAMORPHIC_RELATIONS}


# ---------------------------------------------------------------------------
# MR Composition
# ---------------------------------------------------------------------------

def compose_mrs(seed_prompt: str, seed_candidates: list[str], seed_correct: str,
                mr_names: list[str], rng: random.Random,
                base_complexity: int = 1, base_obfuscation: int = 1
                ) -> tuple[str, list[str], str, int, int, list[str]] | None:
    """Apply a sequence of MRs to a seed task.

    Returns (prompt, candidates, correct, complexity, obfuscation, mr_chain) or None.
    """
    prompt = seed_prompt
    candidates = list(seed_candidates)
    correct = seed_correct
    complexity = base_complexity
    obfuscation = base_obfuscation
    chain = []

    for mr_name in mr_names:
        mr = MR_BY_NAME.get(mr_name)
        if mr is None:
            continue
        result = mr.transform(prompt, candidates, correct, rng)
        if result is None:
            continue  # MR doesn't apply, skip it
        prompt, candidates, correct = result
        complexity += mr.complexity_delta
        obfuscation += mr.obfuscation_delta
        chain.append(mr_name)

    if not chain:
        return None

    # Clamp to grid range
    complexity = max(1, min(10, complexity))
    obfuscation = max(1, min(10, obfuscation))

    return prompt, candidates, correct, complexity, obfuscation, chain


def random_mr_chain(rng: random.Random, max_length: int = 4) -> list[str]:
    """Generate a random MR composition chain."""
    length = rng.randint(1, max_length)
    return [rng.choice(METAMORPHIC_RELATIONS).name for _ in range(length)]


def targeted_mr_chain(target_complexity: int, target_obfuscation: int,
                      rng: random.Random, max_attempts: int = 20) -> list[str]:
    """Generate an MR chain targeting a specific grid cell."""
    best_chain = []
    best_dist = float("inf")

    for _ in range(max_attempts):
        chain = random_mr_chain(rng, max_length=5)
        # Estimate resulting position
        c, o = 1, 1
        for name in chain:
            mr = MR_BY_NAME.get(name)
            if mr:
                c += mr.complexity_delta
                o += mr.obfuscation_delta
        c = max(1, min(10, c))
        o = max(1, min(10, o))
        dist = abs(c - target_complexity) + abs(o - target_obfuscation)
        if dist < best_dist:
            best_dist = dist
            best_chain = chain
        if dist == 0:
            break

    return best_chain
