"""Dynamic trap generation for the Hephaestus test harness.

Generates parameterized variants of reasoning traps to prevent evaluator
overfitting to the static battery. Each generator produces infinite variants
of a trap category with known correct answers.

Usage:
    from trap_generator import generate_trap_battery
    traps = generate_trap_battery(n_per_category=5, seed=42)
"""

import random
import re


def _numeric_comparison(rng: random.Random) -> dict:
    """Generate 'Is X larger than Y?' where decimal places are misleading."""
    # Generate numbers where more digits doesn't mean larger
    base = rng.randint(1, 99)
    # Make a number with more decimal digits but smaller value
    larger = base + rng.uniform(0.1, 5.0)
    smaller = base + rng.uniform(0.01, 0.099)
    larger = round(larger, rng.randint(1, 2))
    smaller = round(smaller, rng.randint(2, 4))

    if rng.random() < 0.5:
        # Ask "is smaller larger than larger?" -> No
        return {
            "prompt": f"Is {smaller} larger than {larger}?",
            "candidates": ["Yes", "No"],
            "correct": "No",
            "category": "numeric_comparison",
        }
    else:
        # Ask "is larger larger than smaller?" -> Yes
        return {
            "prompt": f"Is {larger} larger than {smaller}?",
            "candidates": ["Yes", "No"],
            "correct": "Yes",
            "category": "numeric_comparison",
        }


def _numeric_which_larger(rng: random.Random) -> dict:
    """Generate 'X is less than Y. Which is larger?' with stated premise."""
    a = round(rng.uniform(0.01, 99.99), rng.randint(1, 3))
    b = round(rng.uniform(0.01, 99.99), rng.randint(1, 3))
    while a == b:
        b = round(rng.uniform(0.01, 99.99), rng.randint(1, 3))

    lesser, greater = (a, b) if a < b else (b, a)
    return {
        "prompt": f"{lesser} is less than {greater}. Which number is larger?",
        "candidates": [str(lesser), str(greater), "They are equal", "Cannot be determined"],
        "correct": str(greater),
        "category": "numeric_stated_premise",
    }


def _transitivity_chain(rng: random.Random) -> dict:
    """Generate transitive ordering: A > B > C > ... Who is tallest/shortest?"""
    names = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Hank"]
    n = rng.randint(3, min(5, len(names)))
    selected = rng.sample(names, n)
    # selected[0] is tallest, selected[-1] is shortest
    premises = []
    for i in range(n - 1):
        premises.append(f"{selected[i]} is taller than {selected[i+1]}")
    # Shuffle premises to avoid giving away the order
    rng.shuffle(premises)
    prompt = ", and ".join(premises) + ". Who is tallest?"
    candidates = rng.sample(selected, min(4, n))
    if selected[0] not in candidates:
        candidates[0] = selected[0]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": selected[0],
        "category": "transitivity",
    }


def _modus_tollens(rng: random.Random) -> dict:
    """Generate 'If P then Q. Not Q. Is P true?'"""
    scenarios = [
        ("it is raining", "the ground is wet", "the ground is not wet"),
        ("the alarm sounds", "there is a fire", "there is no fire"),
        ("he studied", "he passed the exam", "he did not pass the exam"),
        ("she is a doctor", "she went to medical school", "she did not go to medical school"),
        ("the switch is on", "the light is on", "the light is not on"),
        ("it is winter", "it is cold outside", "it is not cold outside"),
        ("the door is locked", "you need a key", "you do not need a key"),
    ]
    p, q, not_q = rng.choice(scenarios)
    prompt = f"If {p}, then {q}. {not_q.capitalize()}. Is it the case that {p}?"
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No", "Maybe", "Not enough information"],
        "correct": "No",
        "category": "modus_tollens",
    }


def _quantifier_inversion(rng: random.Random) -> dict:
    """Generate 'All X are Y. Are all Y X?'"""
    pairs = [
        ("cats", "animals"),
        ("dogs", "mammals"),
        ("squares", "rectangles"),
        ("roses", "flowers"),
        ("apples", "fruits"),
        ("sparrows", "birds"),
        ("trucks", "vehicles"),
    ]
    x, y = rng.choice(pairs)
    return {
        "prompt": f"If all {x} are {y}, are all {y} {x}?",
        "candidates": ["Yes", "No"],
        "correct": "No",
        "category": "quantifier_inversion",
    }


def _subject_object(rng: random.Random) -> dict:
    """Generate 'The X verbed the Y. Who was verbed?'"""
    agents = ["dog", "cat", "lion", "hawk", "wolf", "fox", "bear", "eagle"]
    patients = ["rabbit", "mouse", "deer", "fish", "squirrel", "duck", "frog", "snake"]
    verbs_past = ["chased", "caught", "followed", "watched", "cornered", "spotted"]
    verbs_passive = ["being chased", "being caught", "being followed",
                     "being watched", "being cornered", "being spotted"]

    agent = rng.choice(agents)
    patient = rng.choice(patients)
    i = rng.randint(0, len(verbs_past) - 1)
    verb = verbs_past[i]
    passive = verbs_passive[i]

    prompt = f"The {agent} {verb} the {patient}. Who was {passive}?"
    candidates = [f"The {agent}", f"The {patient}", "Both", "Neither"]
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": f"The {patient}",
        "category": "subject_object",
    }


def _all_but_n(rng: random.Random) -> dict:
    """Generate 'A farmer has N sheep. All but M die. How many left?'"""
    total = rng.randint(10, 100)
    remaining = rng.randint(2, total - 2)
    died = total - remaining
    wrong = died  # common mistake
    owners = ["farmer", "rancher", "shepherd", "gardener"]
    animals = ["sheep", "cows", "chickens", "goats", "horses"]
    owner = rng.choice(owners)
    animal = rng.choice(animals)
    return {
        "prompt": f"A {owner} has {total} {animal}. All but {remaining} die. How many are left?",
        "candidates": [str(wrong), str(remaining)],
        "correct": str(remaining),
        "category": "all_but_n",
    }


def _negation_scope(rng: random.Random) -> dict:
    """Generate 'Not the case that all X can Y. Can specific-X Y?'"""
    groups_abilities = [
        ("birds", "fly", "penguins"),
        ("fish", "live in freshwater", "clownfish"),
        ("mammals", "swim", "cats"),
        ("reptiles", "be venomous", "turtles"),
        ("insects", "fly", "ants"),
    ]
    group, ability, specific = rng.choice(groups_abilities)
    return {
        "prompt": (f"It is not the case that all {group} can {ability}. "
                   f"Can {specific} {ability}?"),
        "candidates": [
            f"Yes, all {group} can {ability}",
            f"No, some {group} cannot {ability}",
            "The question cannot be answered from the given information",
            f"Yes, {specific} are {group}",
        ],
        "correct": "The question cannot be answered from the given information",
        "category": "negation_scope",
    }


# Registry of generators
GENERATORS = [
    _numeric_comparison,
    _numeric_which_larger,
    _transitivity_chain,
    _modus_tollens,
    _quantifier_inversion,
    _subject_object,
    _all_but_n,
    _negation_scope,
]


def generate_trap_battery(n_per_category: int = 3, seed: int | None = None) -> list[dict]:
    """Generate a fresh trap battery with n_per_category traps per generator.

    Returns list of trap dicts compatible with test_harness.run_trap_battery().
    """
    rng = random.Random(seed)
    traps = []
    for gen_fn in GENERATORS:
        seen_prompts = set()
        for _ in range(n_per_category * 3):  # oversample to avoid duplicates
            if len([t for t in traps if t.get("category") == gen_fn.__name__.lstrip("_")]) >= n_per_category:
                break
            trap = gen_fn(rng)
            if trap["prompt"] not in seen_prompts:
                seen_prompts.add(trap["prompt"])
                traps.append(trap)
    return traps


if __name__ == "__main__":
    battery = generate_trap_battery(n_per_category=2, seed=42)
    for t in battery:
        print(f"[{t['category']:25s}] {t['prompt'][:70]}")
        print(f"  candidates={t['candidates']}")
        print(f"  correct={t['correct']}")
        print()
    print(f"Total: {len(battery)} traps")
