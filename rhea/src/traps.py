"""
TINY_TRAPS battery for Rhea (the forge).

Simple single-step reasoning traps targeting the 0.2–0.7 baseline
accuracy zone for SmolLM2-135M. Each trap is a forced-choice prompt
with a known correct token and a known incorrect token, enabling
both survival-rate scoring and logit-lens ejection analysis.

Shared concept with Ignis (the microscope), but Rhea's traps are
calibrated for tiny models and designed for CMA-ES fitness evaluation.
"""

from dataclasses import dataclass


@dataclass
class Trap:
    name: str
    prompt: str
    target_token: str   # correct answer token
    anti_token: str     # expected wrong answer token
    category: str       # arithmetic, ordering, logic, negation, contradiction


# === TINY_TRAPS battery ===
# Calibrated for 135M baseline accuracy in [0.2, 0.7]

TINY_TRAPS = [
    # --- Arithmetic ---
    Trap(
        name="add_7_8",
        prompt="What is 7 + 8? Answer with just the number:",
        target_token="15",
        anti_token="16",
        category="arithmetic",
    ),
    Trap(
        name="sub_13_7",
        prompt="What is 13 - 7? Answer with just the number:",
        target_token="6",
        anti_token="7",
        category="arithmetic",
    ),
    Trap(
        name="mul_6_4",
        prompt="What is 6 × 4? Answer with just the number:",
        target_token="24",
        anti_token="28",
        category="arithmetic",
    ),
    Trap(
        name="add_9_6",
        prompt="What is 9 + 6? Answer with just the number:",
        target_token="15",
        anti_token="14",
        category="arithmetic",
    ),

    # --- Ordering ---
    Trap(
        name="decimal_05_050",
        prompt="Which is larger, 0.5 or 0.50? Answer Same or Different:",
        target_token="Same",
        anti_token="Different",
        category="ordering",
    ),
    Trap(
        name="fraction_half_third",
        prompt="Which is larger, 1/2 or 1/3? Answer:",
        target_token="1/2",
        anti_token="1/3",
        category="ordering",
    ),
    Trap(
        name="decimal_magnitude",
        prompt="Is 9.11 larger than 9.9? Answer Yes or No:",
        target_token="No",
        anti_token="Yes",
        category="ordering",
    ),

    # --- One-step logic ---
    Trap(
        name="syllogism_mortal",
        prompt="All men are mortal. Socrates is a man. Is Socrates mortal? Answer Yes or No:",
        target_token="Yes",
        anti_token="No",
        category="logic",
    ),
    Trap(
        name="equality_chain",
        prompt="If A = B and B = C, does A = C? Answer Yes or No:",
        target_token="Yes",
        anti_token="No",
        category="logic",
    ),
    Trap(
        name="contrapositive",
        prompt="If all dogs are animals, are all non-animals non-dogs? Answer Yes or No:",
        target_token="Yes",
        anti_token="No",
        category="logic",
    ),

    # --- Negation ---
    Trap(
        name="odd_even_7",
        prompt="Is 7 an even number? Answer Yes or No:",
        target_token="No",
        anti_token="Yes",
        category="negation",
    ),
    Trap(
        name="divisible_10_3",
        prompt="Is 10 divisible by 3? Answer Yes or No:",
        target_token="No",
        anti_token="Yes",
        category="negation",
    ),
    Trap(
        name="prime_check_7",
        prompt="Is 7 a prime number? Answer Yes or No:",
        target_token="Yes",
        anti_token="No",
        category="negation",
    ),

    # --- Contradiction detection ---
    Trap(
        name="false_arithmetic",
        prompt="Is the statement '2 + 2 = 5' true or false? Answer True or False:",
        target_token="False",
        anti_token="True",
        category="contradiction",
    ),
    Trap(
        name="triangle_sides",
        prompt="Can a triangle have 4 sides? Answer Yes or No:",
        target_token="No",
        anti_token="Yes",
        category="contradiction",
    ),
    Trap(
        name="water_boil",
        prompt="Does water boil at 50°C at sea level? Answer Yes or No:",
        target_token="No",
        anti_token="Yes",
        category="contradiction",
    ),
]


def get_traps_by_category(category: str) -> list[Trap]:
    return [t for t in TINY_TRAPS if t.category == category]


def get_all_categories() -> list[str]:
    return sorted(set(t.category for t in TINY_TRAPS))
