"""Tier 2 trap battery generator — targets categories where Tier 1 tools fail.

These traps require DEEPER reasoning than Tier 1: causal counterfactuals,
statistical paradoxes, multi-level theory of mind, temporal constraint
propagation, and compositional multi-step inference.

12 categories:
  0% on T1 (10): simpson_paradox, causal_counterfactual, conjunction_fallacy,
                  strategic_deception, perspective_shift, temporal_scheduling,
                  argument_strength, liar_detection, compositional_multi_step,
                  rate_of_change
  50% on T1 (2): causal_confounding_hard, temporal_complex

Usage:
    from trap_generator_t2 import generate_t2_battery, T2_CATEGORIES
    battery = generate_t2_battery(n_per_category=2, seed=42)
"""

import random

# ── Category registry ──────────────────────────────────────────────────────

T2_CATEGORIES = [
    "simpson_paradox",
    "causal_counterfactual",
    "conjunction_fallacy",
    "strategic_deception",
    "perspective_shift",
    "temporal_scheduling",
    "argument_strength",
    "liar_detection",
    "compositional_multi_step",
    "rate_of_change",
    "causal_confounding_hard",
    "temporal_complex",
]

# ── Shared pools ───────────────────────────────────────────────────────────

_NAMES = [
    "Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Hank",
    "Ivy", "Jack", "Karen", "Leo", "Mia", "Nate", "Olive", "Paul",
    "Quinn", "Rosa", "Sam", "Tara", "Uma", "Victor", "Wendy", "Xavier",
    "Yara", "Zane", "Amir", "Bianca", "Chen", "Diana", "Elias", "Fiona",
    "Gavin", "Holly", "Igor", "Jia", "Kenji", "Luna", "Marco", "Nina",
]

_HOSPITALS = ["City General", "St. Mary's", "Riverside", "Mercy", "Good Samaritan",
              "Kaiser", "Cedar-Sinai", "Johns Hopkins", "Mayo", "Cleveland Clinic"]

_TREATMENTS = ["Drug A", "Drug B", "Treatment X", "Treatment Y", "Protocol Alpha",
               "Protocol Beta", "Method 1", "Method 2", "Therapy A", "Therapy B"]

_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

_CITIES = ["New York", "London", "Tokyo", "Sydney", "Paris", "Dubai",
           "Los Angeles", "Chicago", "Berlin", "Moscow"]

# Timezone offsets from UTC for the cities above
_CITY_UTC = {
    "New York": -5, "London": 0, "Tokyo": 9, "Sydney": 11, "Paris": 1,
    "Dubai": 4, "Los Angeles": -8, "Chicago": -6, "Berlin": 1, "Moscow": 3,
}


def _pick(rng, pool, n=1, exclude=()):
    """Pick n unique items from pool, excluding some."""
    available = [x for x in pool if x not in exclude]
    return rng.sample(available, min(n, len(available)))


# ── 1. Simpson's Paradox ──────────────────────────────────────────────────

def generate_simpson_paradox(seed: int) -> list[dict]:
    rng = random.Random(seed)
    traps = []
    templates = [
        # (context_domain, group_label, subgroup1, subgroup2, metric)
        ("hospital", "survival rate", "mild cases", "severe cases", "better for"),
        ("school", "graduation rate", "STEM students", "humanities students", "higher for"),
        ("company", "promotion rate", "junior employees", "senior employees", "higher at"),
        ("treatment", "recovery rate", "young patients", "elderly patients", "more effective for"),
    ]
    for _ in range(max(4, len(templates))):
        ctx, metric, sg1, sg2, phrasing = rng.choice(templates)
        e1, e2 = _pick(rng, _HOSPITALS if ctx == "hospital" else _NAMES, 2)

        # Simpson's paradox: entity A has better aggregate but worse in each subgroup
        # Construct concrete numbers
        # Entity B is better in BOTH subgroups but worse overall (due to base rate)
        a_sg1_n, a_sg1_s = rng.randint(80, 95), 100  # A: high rate in sg1
        a_sg2_n, a_sg2_s = rng.randint(50, 65), 100  # A: moderate rate in sg2
        b_sg1_n, b_sg1_s = a_sg1_n + rng.randint(1, 4), 100  # B better in sg1
        b_sg2_n, b_sg2_s = a_sg2_n + rng.randint(1, 4), 100  # B better in sg2

        # But A handles mostly easy cases, B handles mostly hard cases
        a_sg1_total = rng.randint(800, 950)
        a_sg2_total = 1000 - a_sg1_total  # A mostly sees sg1
        b_sg1_total = rng.randint(50, 200)
        b_sg2_total = 1000 - b_sg1_total  # B mostly sees sg2

        prompt = (
            f"{e1} has an overall {metric} of "
            f"{round((a_sg1_n * a_sg1_total + a_sg2_n * a_sg2_total) / (100 * 1000) * 100, 1)}%, "
            f"while {e2} has an overall {metric} of "
            f"{round((b_sg1_n * b_sg1_total + b_sg2_n * b_sg2_total) / (100 * 1000) * 100, 1)}%. "
            f"However, for {sg1}, {e2} has {b_sg1_n}% vs {e1}'s {a_sg1_n}%. "
            f"For {sg2}, {e2} has {b_sg2_n}% vs {e1}'s {a_sg2_n}%. "
            f"Which is {phrasing} {sg2}?"
        )
        traps.append({
            "prompt": prompt,
            "candidates": [e1, e2, "Both are equal", "Cannot be determined"],
            "correct": e2,
            "category": "simpson_paradox",
        })
    return traps


# ── 2. Causal Counterfactual ──────────────────────────────────────────────

def generate_causal_counterfactual(seed: int) -> list[dict]:
    rng = random.Random(seed)
    traps = []

    scenarios = [
        {
            "chain": [("Rain", "Wet streets"), ("Wet streets", "Accidents")],
            "intervention": "it hadn't rained but someone spilled water on the street",
            "question": "would accidents still increase?",
            "answer": "Yes",
            "explanation": "Wet streets (the mediator) are still present via spilled water.",
        },
        {
            "chain": [("Fertilizer", "Plant growth"), ("Plant growth", "Fruit yield")],
            "intervention": "no fertilizer was used but the soil was naturally nutrient-rich",
            "question": "would fruit yield still increase?",
            "answer": "Yes",
            "explanation": "Plant growth still occurs via natural nutrients.",
        },
        {
            "chain": [("Alarm", "Waking up"), ("Waking up", "Arriving on time")],
            "intervention": "the alarm didn't ring and nothing else woke them",
            "question": "would they arrive on time?",
            "answer": "No",
            "explanation": "Without waking up, arrival on time is blocked.",
        },
        {
            "chain": [("Virus", "Fever"), ("Fever", "Dehydration")],
            "intervention": "the person didn't catch the virus but exercised intensely in heat",
            "question": "would dehydration still occur?",
            "answer": "Yes",
            "explanation": "Dehydration can be caused by intense exercise (alternative path).",
        },
        {
            "chain": [("Studying", "Good grades"), ("Good grades", "Scholarship")],
            "intervention": "the student didn't study but was awarded grades by administrative error",
            "question": "would they still get the scholarship?",
            "answer": "Yes",
            "explanation": "Good grades (the mediator) are present via admin error.",
        },
    ]

    for _ in range(max(4, len(scenarios))):
        s = rng.choice(scenarios)
        names = _pick(rng, _NAMES, 2)
        chain_desc = ". ".join(
            f"{a} causes {b.lower()}" for a, b in s["chain"]
        )
        prompt = (
            f"{chain_desc}. "
            f"If {s['intervention']}, {s['question']}"
        )
        traps.append({
            "prompt": prompt,
            "candidates": ["Yes", "No", "Cannot be determined", "Only partially"],
            "correct": s["answer"],
            "category": "causal_counterfactual",
        })
    return traps


# ── 3. Conjunction Fallacy ────────────────────────────────────────────────

def generate_conjunction_fallacy(seed: int) -> list[dict]:
    rng = random.Random(seed)
    traps = []

    profiles = [
        {
            "desc": "{name} is 31, single, outspoken, and very bright. "
                    "She majored in philosophy. As a student, she was deeply concerned "
                    "with issues of discrimination and social justice.",
            "general": "{name} is a bank teller",
            "conjunction": "{name} is a bank teller and is active in the feminist movement",
        },
        {
            "desc": "{name} is a 45-year-old man who loves chess and math puzzles. "
                    "He has no interest in sports or outdoor activities.",
            "general": "{name} is an accountant",
            "conjunction": "{name} is an accountant who plays chess competitively",
        },
        {
            "desc": "{name} is creative, artistic, and enjoys visiting museums. "
                    "She travels frequently and speaks three languages.",
            "general": "{name} works in marketing",
            "conjunction": "{name} works in marketing and paints watercolors on weekends",
        },
        {
            "desc": "{name} is meticulous, punctual, and keeps detailed records of everything. "
                    "He dislikes ambiguity and always follows rules.",
            "general": "{name} is a software engineer",
            "conjunction": "{name} is a software engineer and volunteers as a tax preparer",
        },
        {
            "desc": "{name} is enthusiastic about cooking, watches food shows daily, "
                    "and has a large collection of cookbooks from around the world.",
            "general": "{name} is a teacher",
            "conjunction": "{name} is a teacher who also runs a food blog",
        },
    ]

    for _ in range(max(4, len(profiles))):
        p = rng.choice(profiles)
        name = _pick(rng, _NAMES, 1)[0]
        desc = p["desc"].format(name=name)
        gen = p["general"].format(name=name)
        conj = p["conjunction"].format(name=name)

        # Randomize option ordering
        options = [gen, conj]
        if rng.random() < 0.5:
            options = list(reversed(options))

        prompt = (
            f"{desc} Which is more probable?\n"
            f"(A) {options[0]}\n"
            f"(B) {options[1]}"
        )
        # The general statement is always more (or equally) probable
        correct_label = "A" if options[0] == gen else "B"
        traps.append({
            "prompt": prompt,
            "candidates": ["A", "B", "Both equally probable", "Neither is probable"],
            "correct": correct_label,
            "category": "conjunction_fallacy",
        })
    return traps


# ── 4. Strategic Deception ────────────────────────────────────────────────

def generate_strategic_deception(seed: int) -> list[dict]:
    rng = random.Random(seed)
    traps = []

    directions = ["left", "right", "north", "south", "east", "west"]
    objects = ["treasure", "exit", "key", "safe room", "prize", "gold"]

    for _ in range(4):
        a, b, c = _pick(rng, _NAMES, 3)
        real_dir, fake_dir = _pick(rng, directions, 2)
        obj = rng.choice(objects)

        # Vary deception depth
        depth = rng.choice([1, 2, 3])

        if depth == 1:
            # A lies, B knows A always lies
            prompt = (
                f"{a} wants {b} to go {fake_dir}. {a} tells {b} 'The {obj} is to the {real_dir}.' "
                f"{b} knows that {a} always lies. Where does {b} go?"
            )
            # B inverts -> goes opposite of what A said
            # A said real_dir (lying to send B wrong way means A actually said real_dir
            # wanting B to go fake_dir... wait let me think clearly)
            # A wants B to go fake_dir. So A lies: says the opposite of fake_dir.
            # A tells B real_dir. B knows A lies, so B goes opposite of real_dir = fake_dir? No.
            # Let me re-read: "A wants B to go fake_dir. A tells B the obj is to the real_dir."
            # B knows A lies, so B goes opposite of real_dir.
            # The opposite of real_dir... we need to define opposites properly.
            # Simpler: use left/right explicitly.
            prompt = (
                f"{a} wants {b} to go left. {a} tells {b} 'The {obj} is on the right.' "
                f"{b} knows that {a} always lies. Where does {b} go?"
            )
            correct = "left"
            candidates = ["left", "right", f"{b} stays put", "Cannot determine"]
        elif depth == 2:
            # A lies, B knows A lies, A knows B knows A lies (double bluff)
            prompt = (
                f"{a} always lies. {b} knows {a} always lies. {a} also knows that {b} knows this. "
                f"The {obj} is actually on the left. "
                f"{a} wants {b} to go right (away from the {obj}). "
                f"Knowing {b} will invert, {a} says 'The {obj} is on the left.' "
                f"What does {b} conclude and where does {b} go?"
            )
            # B inverts "left" -> goes right. A's double bluff works.
            correct = "right"
            candidates = ["left", "right", f"{b} stays put", "Cannot determine"]
        else:
            # Triple: A knows B will double-invert
            prompt = (
                f"{a} always lies. {b} knows this. {a} knows {b} knows. "
                f"{b} also realizes {a} might double-bluff. "
                f"{a} says 'The {obj} is on the left.' "
                f"If {b} assumes {a} is using a simple lie (level 1 reasoning), where does {b} go? "
                f"Answer based on level 1 reasoning only."
            )
            correct = "right"
            candidates = ["left", "right", f"{b} stays put", "Cannot determine"]

        traps.append({
            "prompt": prompt,
            "candidates": candidates,
            "correct": correct,
            "category": "strategic_deception",
        })
    return traps


# ── 5. Perspective Shift ─────────────────────────────────────────────────

def generate_perspective_shift(seed: int) -> list[dict]:
    rng = random.Random(seed)
    traps = []

    containers = ["box", "drawer", "cabinet", "bag", "basket", "jar"]
    items = ["marble", "key", "coin", "ring", "letter", "toy"]

    for _ in range(4):
        a, b, c = _pick(rng, _NAMES, 3)
        item = rng.choice(items)
        c1, c2 = _pick(rng, containers, 2)

        # Classic Sally-Anne with a third observer twist
        prompt = (
            f"{a} puts a {item} in the {c1} and leaves the room. "
            f"While {a} is away, {b} moves the {item} from the {c1} to the {c2}. "
            f"{c} watched {b} move the {item} but doesn't know whether {a} saw this. "
            f"What does {c} think {a} believes about where the {item} is?"
        )
        # C knows A left before the move, so C thinks A still believes it's in c1
        correct = f"{a} believes it is in the {c1}"
        traps.append({
            "prompt": prompt,
            "candidates": [
                f"{a} believes it is in the {c1}",
                f"{a} believes it is in the {c2}",
                f"{a} has no belief about its location",
                "Cannot determine",
            ],
            "correct": correct,
            "category": "perspective_shift",
        })
    return traps


# ── 6. Temporal Scheduling ───────────────────────────────────────────────

def generate_temporal_scheduling(seed: int) -> list[dict]:
    rng = random.Random(seed)
    traps = []

    for _ in range(4):
        # Generate random task durations and dependencies
        n_tasks = rng.randint(3, 5)
        durations = [rng.randint(1, 8) for _ in range(n_tasks)]
        labels = [chr(65 + i) for i in range(n_tasks)]  # A, B, C, ...

        # Create some dependencies (DAG)
        deps = {}
        for i in range(n_tasks):
            deps[labels[i]] = []
        # Add 1-2 dependencies for tasks after the first
        for i in range(1, n_tasks):
            if rng.random() < 0.6:
                dep_idx = rng.randint(0, i - 1)
                deps[labels[i]].append(labels[dep_idx])

        # Compute critical path (earliest finish time)
        earliest_start = {}
        for i in range(n_tasks):
            lbl = labels[i]
            if not deps[lbl]:
                earliest_start[lbl] = 0
            else:
                earliest_start[lbl] = max(
                    earliest_start[d] + durations[labels.index(d)]
                    for d in deps[lbl]
                )
        min_time = max(earliest_start[lbl] + durations[i] for i, lbl in enumerate(labels))

        # Build description
        task_descs = []
        for i, lbl in enumerate(labels):
            dep_str = ""
            if deps[lbl]:
                dep_str = f" (requires {' and '.join(deps[lbl])} to finish first)"
            task_descs.append(f"Task {lbl} takes {durations[i]}h{dep_str}")
        desc = ". ".join(task_descs)
        prompt = (
            f"{desc}. Tasks without dependencies can run in parallel. "
            f"What is the minimum total time to complete all tasks?"
        )

        # Distractors: sum of all, max single, random wrong
        total_sum = sum(durations)
        candidates_set = {min_time, total_sum, max(durations)}
        while len(candidates_set) < 4:
            candidates_set.add(rng.randint(min_time - 2, total_sum + 2))
        candidates = sorted(candidates_set)

        traps.append({
            "prompt": prompt,
            "candidates": [f"{c}h" for c in candidates],
            "correct": f"{min_time}h",
            "category": "temporal_scheduling",
        })
    return traps


# ── 7. Argument Strength ─────────────────────────────────────────────────

def generate_argument_strength(seed: int) -> list[dict]:
    rng = random.Random(seed)
    traps = []

    fallacies = [
        {
            "name": "affirming the consequent",
            "premise1": "All {A} are {B}",
            "premise2": "{x} is a {B}",
            "conclusion": "Therefore {x} is a {A}",
            "valid": False,
        },
        {
            "name": "denying the antecedent",
            "premise1": "If it {A}, then {B}",
            "premise2": "It did not {A}",
            "conclusion": "Therefore it did not {B}",
            "valid": False,
        },
        {
            "name": "modus ponens",
            "premise1": "If {A}, then {B}",
            "premise2": "{A} is true",
            "conclusion": "Therefore {B}",
            "valid": True,
        },
        {
            "name": "modus tollens",
            "premise1": "If {A}, then {B}",
            "premise2": "{B} is false",
            "conclusion": "Therefore {A} is false",
            "valid": True,
        },
    ]

    fill_sets = [
        {"A": "dogs", "B": "mammals", "x": "Rex"},
        {"A": "cats", "B": "animals", "x": "Whiskers"},
        {"A": "roses", "B": "plants", "x": "the daisy"},
        {"A": "rains", "B": "the ground gets wet", "x": None},
        {"A": "the alarm sounds", "B": "people evacuate", "x": None},
        {"A": "you study", "B": "you pass the exam", "x": None},
    ]

    for _ in range(max(4, len(fallacies))):
        f = rng.choice(fallacies)
        fills = rng.choice(fill_sets)

        p1 = f["premise1"].format(**fills)
        p2 = f["premise2"].format(**fills)
        conc = f["conclusion"].format(**fills)

        prompt = (
            f"Evaluate this argument:\n"
            f"  Premise 1: {p1}.\n"
            f"  Premise 2: {p2}.\n"
            f"  Conclusion: {conc}.\n"
            f"Is this argument logically valid?"
        )
        correct = "Valid" if f["valid"] else "Invalid"
        traps.append({
            "prompt": prompt,
            "candidates": ["Valid", "Invalid", "Valid but unsound", "Cannot determine"],
            "correct": correct,
            "category": "argument_strength",
        })
    return traps


# ── 8. Liar Detection ────────────────────────────────────────────────────

def generate_liar_detection(seed: int) -> list[dict]:
    rng = random.Random(seed)
    traps = []

    # Pre-built liar puzzles with verified solutions
    puzzles = [
        {
            "prompt": (
                "Exactly one of these three statements is true:\n"
                "  (1) Statement 2 is true.\n"
                "  (2) Statement 3 is false.\n"
                "  (3) Statement 1 is true.\n"
                "Which statement is the true one?"
            ),
            # If (1) true -> (2) true -> contradiction (exactly one).
            # If (2) true -> (3) is false. (1) is false -> (2) is false -> contradiction.
            # If (3) true -> (1) is true -> contradiction.
            # Try: (2) true -> (3) false, (1) false -> (2) NOT true? contradiction.
            # Actually: (1) false means (2) is false. (2) false means (3) is true.
            # (3) true means (1) is true. But (1) is false. Contradiction.
            # So no consistent assignment with exactly one true.
            # Let me re-check with exactly one true:
            # Only (1) true: (2) true (from (1)) -> contradiction.
            # Only (2) true: (3) is false (from (2)). (1) is false -> (2) is false. Contradiction.
            # Only (3) true: (1) is true (from (3)). Contradiction.
            # None true: (1) F -> (2) F; (2) F -> (3) T. But (3) T contradicts "none true".
            # This is a paradox - no consistent solution.
            "correct": "No consistent solution exists",
            "candidates": ["Statement 1", "Statement 2", "Statement 3",
                           "No consistent solution exists"],
        },
        {
            "prompt": (
                "There are two people. {a} says 'We are both liars.' "
                "{b} says nothing. If truth-tellers always tell the truth and liars always lie, "
                "what is {a}?"
            ),
            # If A is truth-teller: "both liars" is true -> A is liar. Contradiction.
            # If A is liar: "both liars" is false -> at least one is truth-teller.
            # A is liar, so B must be truth-teller. Consistent.
            "correct": "{a} is a liar",
            "candidates": ["{a} is a truth-teller", "{a} is a liar",
                           "Cannot determine", "The scenario is paradoxical"],
        },
        {
            "prompt": (
                "{a} says 'I am a liar.' Is this statement possible under standard "
                "truth-teller/liar rules (truth-tellers always tell truth, liars always lie)?"
            ),
            # Truth-teller says "I'm a liar" -> false, contradiction.
            # Liar says "I'm a liar" -> "I'm a liar" is false -> "I'm a truth-teller" -> contradiction.
            "correct": "The statement is paradoxical",
            "candidates": ["{a} is a truth-teller", "{a} is a liar",
                           "The statement is paradoxical", "Cannot determine"],
        },
        {
            "prompt": (
                "On an island, knights always tell the truth and knaves always lie. "
                "{a} says: '{b} is a knave.' {b} says: 'We are not both knaves.' "
                "What are {a} and {b}?"
            ),
            # If A knight: B is knave (A tells truth). B is knave -> "not both knaves" is a lie
            # -> they ARE both knaves. But A is knight. Contradiction.
            # If A knave: B is NOT knave (A lies) -> B is knight.
            # B says "not both knaves" -> true (A knave, B knight). Consistent.
            "correct": "{a} is a knave and {b} is a knight",
            "candidates": [
                "Both are knights", "Both are knaves",
                "{a} is a knight and {b} is a knave",
                "{a} is a knave and {b} is a knight",
            ],
        },
        {
            "prompt": (
                "Knights always tell the truth, knaves always lie. "
                "{a} says: 'At least one of us is a knave.' "
                "What is {a}?"
            ),
            # If A is knight: statement true -> at least one is a knave.
            # A is knight, so "at least one" must refer to someone else, but there's only A.
            # Wait - "us" is ambiguous. Assume "us" = just A (alone).
            # If A knight: "at least one of us is knave" = true -> A is knave. Contradiction.
            # If A alone, this is paradoxical. But typically "us" implies a group.
            # Let me reframe with two people.
            "correct": "{a} is a knight",
            "candidates": ["{a} is a knight", "{a} is a knave",
                           "Cannot determine", "The scenario is paradoxical"],
            # Reframe: A and B exist. A says "at least one of us is a knave."
            # If A knight: true -> at least one knave -> B is knave. Consistent.
            # If A knave: lie -> nobody is knave -> A is not knave. Contradiction.
            # So A is knight. This works when there are 2 people.
            "prompt": (
                "Knights always tell the truth, knaves always lie. "
                "{a} and {b} are on the island. "
                "{a} says: 'At least one of us is a knave.' "
                "What is {a}?"
            ),
        },
    ]

    for _ in range(max(4, len(puzzles))):
        p = rng.choice(puzzles)
        a, b = _pick(rng, _NAMES, 2)
        prompt = p["prompt"].format(a=a, b=b)
        correct = p["correct"].format(a=a, b=b)
        candidates = [c.format(a=a, b=b) for c in p["candidates"]]
        traps.append({
            "prompt": prompt,
            "candidates": candidates,
            "correct": correct,
            "category": "liar_detection",
        })
    return traps


# ── 9. Compositional Multi-Step ──────────────────────────────────────────

def generate_compositional_multi_step(seed: int) -> list[dict]:
    rng = random.Random(seed)
    traps = []

    for _ in range(4):
        variant = rng.randint(0, 3)

        if variant == 0:
            # Day calculation with weekend postponement
            start_day_idx = rng.randint(0, 6)
            offset = rng.randint(2, 6)
            start_day = _DAYS[start_day_idx]
            target_idx = (start_day_idx + offset) % 7
            target_day = _DAYS[target_idx]
            # Weekend = Saturday(5) or Sunday(6)
            if target_idx in (5, 6):
                final_day = _DAYS[0]  # Postpone to Monday
                postponed = True
            else:
                final_day = target_day
                postponed = False

            prompt = (
                f"Today is {start_day}. A meeting is scheduled in {offset} days. "
                f"If the meeting falls on a weekend, it is postponed to Monday. "
                f"When is the meeting?"
            )
            candidates_set = {final_day}
            candidates_set.add(target_day)
            candidates_set.add(_DAYS[(start_day_idx + offset + 1) % 7])
            while len(candidates_set) < 4:
                candidates_set.add(rng.choice(_DAYS))
            candidates = sorted(candidates_set)

            traps.append({
                "prompt": prompt,
                "candidates": candidates,
                "correct": final_day,
                "category": "compositional_multi_step",
            })

        elif variant == 1:
            # Multi-step arithmetic with unit conversion
            km = rng.randint(10, 50)
            speed_kph = rng.randint(30, 80)
            fuel_per_100km = rng.randint(5, 12)
            fuel_cost = round(rng.uniform(1.0, 3.0), 2)

            time_h = round(km / speed_kph, 2)
            time_min = round(time_h * 60)
            fuel_used = round(km * fuel_per_100km / 100, 2)
            total_cost = round(fuel_used * fuel_cost, 2)

            prompt = (
                f"A car travels {km} km at {speed_kph} km/h. "
                f"It uses {fuel_per_100km} liters per 100 km. "
                f"Fuel costs ${fuel_cost}/liter. "
                f"How much does the fuel cost for this trip?"
            )
            candidates_set = {total_cost}
            candidates_set.add(round(km * fuel_cost, 2))  # Wrong: forget per-100
            candidates_set.add(round(fuel_per_100km * fuel_cost, 2))  # Wrong: just rate * cost
            while len(candidates_set) < 4:
                candidates_set.add(round(total_cost + rng.uniform(-2, 5), 2))
            candidates = sorted(candidates_set)

            traps.append({
                "prompt": prompt,
                "candidates": [f"${c}" for c in candidates],
                "correct": f"${total_cost}",
                "category": "compositional_multi_step",
            })

        elif variant == 2:
            # Chain of conditionals
            a, b, c = _pick(rng, _NAMES, 3)
            x = rng.randint(5, 20)
            y = rng.randint(2, 5)
            z = rng.randint(1, 3)

            result = (x + y) * z
            prompt = (
                f"{a} has {x} apples. {b} gives {a} {y} more apples. "
                f"Then {a} divides all apples equally into {z} bags, but then "
                f"realizes the bags are too small and puts everything into one bag. "
                f"How many apples are in the bag?"
            )
            traps.append({
                "prompt": prompt,
                "candidates": [
                    str(x + y),  # correct
                    str(result),  # distractor: multiplied
                    str(x),
                    str((x + y) // z),
                ],
                "correct": str(x + y),
                "category": "compositional_multi_step",
            })

        else:
            # Percentage chain
            base = rng.randint(100, 500)
            pct1 = rng.randint(10, 30)
            pct2 = rng.randint(10, 30)

            after_1 = base * (1 + pct1 / 100)
            after_2 = after_1 * (1 - pct2 / 100)
            final = round(after_2, 2)

            prompt = (
                f"A stock starts at ${base}. It rises {pct1}%, then drops {pct2}%. "
                f"What is the final price?"
            )
            naive = round(base * (1 + (pct1 - pct2) / 100), 2)
            candidates_set = {final, naive, float(base)}
            while len(candidates_set) < 4:
                candidates_set.add(round(final + rng.uniform(-20, 20), 2))
            candidates = sorted(candidates_set)

            traps.append({
                "prompt": prompt,
                "candidates": [f"${c}" for c in candidates],
                "correct": f"${final}",
                "category": "compositional_multi_step",
            })
    return traps


# ── 10. Rate of Change ───────────────────────────────────────────────────

def generate_rate_of_change(seed: int) -> list[dict]:
    rng = random.Random(seed)
    traps = []

    for _ in range(4):
        variant = rng.randint(0, 2)

        if variant == 0:
            # Tank fill/drain
            fill = rng.randint(3, 10)
            drain = rng.randint(1, fill - 1)
            start = rng.randint(0, 50)
            target = rng.randint(start + 20, start + 100)
            net = fill - drain
            time_needed = round((target - start) / net, 2)
            # Round up since we can't have partial minutes
            if time_needed != int(time_needed):
                time_ceil = int(time_needed) + 1
            else:
                time_ceil = int(time_needed)

            prompt = (
                f"A tank fills at {fill} L/min and drains at {drain} L/min. "
                f"Starting from {start}L, how many minutes until it reaches {target}L?"
            )
            correct_val = round((target - start) / net, 1)
            candidates_set = {correct_val}
            candidates_set.add(round((target - start) / fill, 1))  # Forgot drain
            candidates_set.add(round(target / net, 1))  # Forgot starting amount
            while len(candidates_set) < 4:
                candidates_set.add(round(correct_val + rng.uniform(-5, 10), 1))
            candidates = sorted(candidates_set)

            traps.append({
                "prompt": prompt,
                "candidates": [f"{c} minutes" for c in candidates],
                "correct": f"{correct_val} minutes",
                "category": "rate_of_change",
            })

        elif variant == 1:
            # Two objects approaching
            d = rng.randint(50, 200)
            v1 = rng.randint(20, 60)
            v2 = rng.randint(20, 60)
            closing = v1 + v2
            time_to_meet = round(d / closing, 1)

            prompt = (
                f"Two cars start {d} km apart, driving toward each other. "
                f"Car A goes {v1} km/h and Car B goes {v2} km/h. "
                f"How long until they meet?"
            )
            candidates_set = {time_to_meet}
            candidates_set.add(round(d / v1, 1))
            candidates_set.add(round(d / v2, 1))
            while len(candidates_set) < 4:
                candidates_set.add(round(time_to_meet + rng.uniform(-1, 3), 1))
            candidates = sorted(candidates_set)

            traps.append({
                "prompt": prompt,
                "candidates": [f"{c} hours" for c in candidates],
                "correct": f"{time_to_meet} hours",
                "category": "rate_of_change",
            })

        else:
            # Population growth/decay
            pop = rng.randint(1000, 5000)
            birth = rng.randint(5, 15)
            death = rng.randint(1, birth - 1)
            net_rate = birth - death
            years = rng.randint(2, 5)
            # Simple linear model
            final_pop = pop + net_rate * years

            prompt = (
                f"A town has {pop} people. Each year, {birth} people are born "
                f"and {death} people die. After {years} years, what is the population? "
                f"(Assume simple linear growth.)"
            )
            candidates_set = {final_pop}
            candidates_set.add(pop + birth * years)  # Forgot deaths
            candidates_set.add(pop - death * years)  # Only subtracted
            while len(candidates_set) < 4:
                candidates_set.add(final_pop + rng.randint(-50, 50))
            candidates = sorted(candidates_set)

            traps.append({
                "prompt": prompt,
                "candidates": [str(c) for c in candidates],
                "correct": str(final_pop),
                "category": "rate_of_change",
            })
    return traps


# ── 11. Causal Confounding Hard ──────────────────────────────────────────

def generate_causal_confounding_hard(seed: int) -> list[dict]:
    rng = random.Random(seed)
    traps = []

    scenarios = [
        {
            "observed": "{X} users tend to {habit}. {X} users have lower {outcome}. "
                        "{habit_verb} also reduces {outcome}.",
            "question": "Does {X} directly reduce {outcome}, or is {habit_noun} the confounder?",
            "correct": "{habit_noun} is the confounder",
            "fills": [
                {"X": "Coffee", "habit": "exercise more", "outcome": "heart disease",
                 "habit_verb": "Exercise", "habit_noun": "Exercise"},
                {"X": "Green tea", "habit": "eat healthier diets", "outcome": "obesity",
                 "habit_verb": "Healthy eating", "habit_noun": "Healthy eating"},
                {"X": "Wine", "habit": "have higher income", "outcome": "stress-related illness",
                 "habit_verb": "Higher income", "habit_noun": "Income"},
            ],
        },
        {
            "observed": "Countries that consume more {X} win more {Y}. "
                        "Countries that consume more {X} also tend to be wealthier. "
                        "Wealthier countries invest more in {Z}, which leads to more {Y}.",
            "question": "Does {X} consumption cause {Y} wins?",
            "correct": "No, national wealth is the confounder",
            "fills": [
                {"X": "chocolate", "Y": "Nobel Prizes", "Z": "education and research"},
                {"X": "cheese", "Y": "Olympic medals", "Z": "sports infrastructure"},
            ],
        },
        {
            "observed": "Students who {X} get better grades. Students who {X} also come "
                        "from families that {Y}. Families that {Y} provide {Z}, which "
                        "independently improves grades.",
            "question": "Does {X} directly cause better grades, or is family background the confounder?",
            "correct": "Family background is the confounder",
            "fills": [
                {"X": "take private tutoring", "Y": "have higher income",
                 "Z": "better learning environments at home"},
                {"X": "attend summer camps", "Y": "value education highly",
                 "Z": "more academic support and motivation"},
            ],
        },
    ]

    for _ in range(max(4, len(scenarios))):
        s = rng.choice(scenarios)
        fills = rng.choice(s["fills"])
        prompt = (
            s["observed"].format(**fills) + " " + s["question"].format(**fills)
        )
        correct = s["correct"].format(**fills)
        traps.append({
            "prompt": prompt,
            "candidates": [
                f"{fills.get('X', 'It')} directly causes the effect",
                correct,
                "Both are independent causes",
                "Cannot determine from the information given",
            ],
            "correct": correct,
            "category": "causal_confounding_hard",
        })
    return traps


# ── 12. Temporal Complex ─────────────────────────────────────────────────

def generate_temporal_complex(seed: int) -> list[dict]:
    rng = random.Random(seed)
    traps = []

    for _ in range(4):
        c1, c2 = _pick(rng, list(_CITY_UTC.keys()), 2)
        tz1, tz2 = _CITY_UTC[c1], _CITY_UTC[c2]
        tz_diff = tz2 - tz1  # hours ahead of c1

        start_hour = rng.randint(18, 23)  # evening flights
        day_idx = rng.randint(0, 6)
        start_day = _DAYS[day_idx]
        flight_hours = rng.randint(3, 14)

        # Arrival in local time at c2
        arrival_utc_hour = start_hour + flight_hours  # still in c1 local conceptually
        # Convert: c1 local to UTC = subtract tz1, then add tz2
        arrival_c2_hour = start_hour + flight_hours + tz_diff
        arrival_days_offset = 0
        while arrival_c2_hour >= 24:
            arrival_c2_hour -= 24
            arrival_days_offset += 1
        while arrival_c2_hour < 0:
            arrival_c2_hour += 24
            arrival_days_offset -= 1

        arrival_day_idx = (day_idx + arrival_days_offset) % 7
        arrival_day = _DAYS[arrival_day_idx]

        # Format hour
        if arrival_c2_hour == 0:
            time_str = "12:00 AM (midnight)"
        elif arrival_c2_hour < 12:
            time_str = f"{arrival_c2_hour}:00 AM"
        elif arrival_c2_hour == 12:
            time_str = "12:00 PM (noon)"
        else:
            time_str = f"{arrival_c2_hour - 12}:00 PM"

        correct = f"{arrival_day} {time_str}"

        # Naive distractor: just add flight hours, no timezone
        naive_hour = (start_hour + flight_hours) % 24
        naive_day_offset = (start_hour + flight_hours) // 24
        naive_day = _DAYS[(day_idx + naive_day_offset) % 7]

        tz_sign = "+" if tz_diff >= 0 else ""
        prompt = (
            f"It's {start_hour}:00 ({start_day}) in {c1} (UTC{'+' if tz1 >= 0 else ''}{tz1}). "
            f"A {flight_hours}-hour flight departs for {c2} (UTC{'+' if tz2 >= 0 else ''}{tz2}). "
            f"What day and local time does it land in {c2}?"
        )

        # Build candidate set
        candidates = set()
        candidates.add(correct)
        # Naive (no tz adjustment)
        if naive_hour == 0:
            naive_time = "12:00 AM (midnight)"
        elif naive_hour < 12:
            naive_time = f"{naive_hour}:00 AM"
        elif naive_hour == 12:
            naive_time = "12:00 PM (noon)"
        else:
            naive_time = f"{naive_hour - 12}:00 PM"
        candidates.add(f"{naive_day} {naive_time}")

        # Wrong tz direction
        wrong_hour = start_hour + flight_hours - tz_diff
        wrong_days = 0
        while wrong_hour >= 24:
            wrong_hour -= 24
            wrong_days += 1
        while wrong_hour < 0:
            wrong_hour += 24
            wrong_days -= 1
        wrong_day = _DAYS[(day_idx + wrong_days) % 7]
        if wrong_hour == 0:
            wrong_time = "12:00 AM (midnight)"
        elif wrong_hour < 12:
            wrong_time = f"{wrong_hour}:00 AM"
        elif wrong_hour == 12:
            wrong_time = "12:00 PM (noon)"
        else:
            wrong_time = f"{wrong_hour - 12}:00 PM"
        candidates.add(f"{wrong_day} {wrong_time}")

        while len(candidates) < 4:
            rh = rng.randint(0, 23)
            rd = rng.choice(_DAYS)
            if rh < 12:
                rt = f"{rh}:00 AM" if rh > 0 else "12:00 AM (midnight)"
            elif rh == 12:
                rt = "12:00 PM (noon)"
            else:
                rt = f"{rh - 12}:00 PM"
            candidates.add(f"{rd} {rt}")

        traps.append({
            "prompt": prompt,
            "candidates": sorted(candidates),
            "correct": correct,
            "category": "temporal_complex",
        })
    return traps


# ── Master battery generator ─────────────────────────────────────────────

_GENERATORS = {
    "simpson_paradox": generate_simpson_paradox,
    "causal_counterfactual": generate_causal_counterfactual,
    "conjunction_fallacy": generate_conjunction_fallacy,
    "strategic_deception": generate_strategic_deception,
    "perspective_shift": generate_perspective_shift,
    "temporal_scheduling": generate_temporal_scheduling,
    "argument_strength": generate_argument_strength,
    "liar_detection": generate_liar_detection,
    "compositional_multi_step": generate_compositional_multi_step,
    "rate_of_change": generate_rate_of_change,
    "causal_confounding_hard": generate_causal_confounding_hard,
    "temporal_complex": generate_temporal_complex,
}


def generate_t2_battery(n_per_category: int = 2, seed: int = 42) -> list[dict]:
    """Generate the full Tier 2 battery.

    Args:
        n_per_category: Number of traps per category.
        seed: Master seed for reproducibility. Each category gets a derived seed.

    Returns:
        List of trap dicts with keys: prompt, candidates, correct, category.
    """
    battery = []
    for i, cat in enumerate(T2_CATEGORIES):
        gen = _GENERATORS[cat]
        cat_seed = seed + i * 1000
        all_traps = gen(cat_seed)
        # Take up to n_per_category, cycling if needed
        selected = []
        for j in range(n_per_category):
            selected.append(all_traps[j % len(all_traps)])
        battery.extend(selected)
    return battery


if __name__ == "__main__":
    battery = generate_t2_battery(n_per_category=2, seed=42)
    print(f"{len(battery)} traps across {len(T2_CATEGORIES)} categories")
    for t in battery[:5]:
        print(f"\n  [{t['category']}] {t['prompt'][:100]}...")
        print(f"    candidates: {t['candidates']}")
        print(f"    correct: {t['correct']}")
