"""Tier 2 trap generators — challenges that CANNOT be solved by regex/NCD/keyword detection.

Each category requires actual computation: state tracking, constraint propagation,
formal inference, Bayesian updating, or information sufficiency analysis.

24 categories across 4 waves.

Usage:
    from trap_generator_tier2 import generate_tier2_battery, generate_combined_battery
    traps = generate_combined_battery(n_per_category=2, seed=42)

Design principles:
    1. No category solvable by regex alone (existing tools must score <60%)
    2. Each category requires a specific computational capability
    3. Template variation defeats keyword spotting
    4. Ground truth is computationally verifiable
    5. Anti-gaming: name randomization, surface form variation, distractor injection,
       intermediate value traps, keyword traps
"""

import random
import math

from trap_generator_extended import generate_full_battery

# ---------------------------------------------------------------------------
# Expanded name/entity pools (50+ to defeat memorization)
# ---------------------------------------------------------------------------
_NAMES = [
    "Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Hank",
    "Ivy", "Jack", "Karen", "Leo", "Mia", "Nate", "Olive", "Paul",
    "Quinn", "Rosa", "Sam", "Tara", "Uma", "Victor", "Wendy", "Xavier",
    "Yara", "Zane", "Amir", "Bianca", "Chen", "Diana", "Elias", "Fiona",
    "Gavin", "Holly", "Igor", "Jia", "Kenji", "Luna", "Marco", "Nina",
    "Oscar", "Priya", "Ravi", "Sofia", "Tomás", "Uri", "Vera", "Wren",
    "Xena", "Yuki", "Zara",
]
_NONSENSE = [
    "blorp", "snark", "fizz", "quog", "brint", "wex", "plonk", "grix",
    "trev", "yumble", "drak", "moof", "plib", "zorp", "krint", "flimb",
    "snog", "gleep", "borp", "twix", "norf", "vren", "clump", "spaz",
    "wibble", "frug", "dint", "glop",
]
_DISTRACTORS = [
    "The weather was unusually warm that day.",
    "Several birds could be seen flying overhead.",
    "A nearby clock showed it was mid-afternoon.",
    "The room smelled faintly of coffee.",
    "Someone had left a newspaper on the table.",
    "Traffic outside was light for a weekday.",
    "The walls were painted a pale shade of blue.",
    "A dog barked somewhere in the distance.",
    "The elevator took exactly 12 seconds to arrive.",
    "Three paintings hung on the far wall.",
    "A fan hummed quietly in the corner.",
    "The carpet had a subtle geometric pattern.",
]
_SURFACE_INTROS = [
    "Consider the following scenario.",
    "Here is a problem to solve.",
    "Read carefully and answer.",
    "Analyze the following situation.",
    "",  # no intro
]


def _pick_names(rng, n):
    return rng.sample(_NAMES, n)


def _maybe_distractor(rng, p=0.5):
    if rng.random() < p:
        return " " + rng.choice(_DISTRACTORS)
    return ""


def _intro(rng):
    s = rng.choice(_SURFACE_INTROS)
    return s + " " if s else ""


# ===================================================================
# WAVE 1: Core Computational Primitives (8 categories)
# ===================================================================

def _stateful_register_machine(rng: random.Random) -> dict:
    """Initialize 2-4 registers, apply 3-8 operations, query final value."""
    n_regs = rng.randint(2, 4)
    n_ops = rng.randint(3, 7)
    names = rng.sample(["X", "Y", "Z", "W", "A", "B", "R", "S"], n_regs)
    regs = {}
    for nm in names:
        regs[nm] = rng.randint(1, 20)

    ops_text = []
    history = [dict(regs)]  # track intermediates for traps

    op_types = ["add", "sub", "mul", "assign", "swap"]
    for _ in range(n_ops):
        op = rng.choice(op_types)
        if op == "add":
            r = rng.choice(names)
            v = rng.randint(1, 10)
            templates = [f"Add {v} to {r}.", f"Increase {r} by {v}.", f"{r} = {r} + {v}."]
            ops_text.append(rng.choice(templates))
            regs[r] += v
        elif op == "sub":
            r = rng.choice(names)
            v = rng.randint(1, min(5, max(1, regs[r])))
            templates = [f"Subtract {v} from {r}.", f"Decrease {r} by {v}.", f"{r} = {r} - {v}."]
            ops_text.append(rng.choice(templates))
            regs[r] -= v
        elif op == "mul":
            r = rng.choice(names)
            v = rng.choice([2, 3])
            templates = [f"Multiply {r} by {v}.", f"{'Double' if v==2 else 'Triple'} {r}.", f"{r} = {r} * {v}."]
            ops_text.append(rng.choice(templates))
            regs[r] *= v
        elif op == "assign":
            r = rng.choice(names)
            v = rng.randint(1, 30)
            templates = [f"Set {r} to {v}.", f"{r} = {v}.", f"Assign the value {v} to {r}."]
            ops_text.append(rng.choice(templates))
            regs[r] = v
        elif op == "swap" and n_regs >= 2:
            a, b = rng.sample(names, 2)
            templates = [f"Swap {a} and {b}.", f"Exchange the values of {a} and {b}."]
            ops_text.append(rng.choice(templates))
            regs[a], regs[b] = regs[b], regs[a]
        history.append(dict(regs))

    query_reg = rng.choice(names)
    correct = str(regs[query_reg])

    # Build wrong candidates: intermediate values, initial value, off-by-one
    wrong = set()
    for h in history[:-1]:
        wrong.add(str(h[query_reg]))
    for r in names:
        if r != query_reg:
            wrong.add(str(regs[r]))
    wrong.add(str(regs[query_reg] + 1))
    wrong.add(str(regs[query_reg] - 1))
    wrong.discard(correct)
    wrong_list = rng.sample(sorted(wrong), min(3, len(wrong)))
    while len(wrong_list) < 3:
        v = str(rng.randint(1, 50))
        if v != correct and v not in wrong_list:
            wrong_list.append(v)

    init_text = ", ".join(f"{nm} = {history[0][nm]}" for nm in names)
    prompt = f"{_intro(rng)}Registers: {init_text}. {' '.join(ops_text)}{_maybe_distractor(rng)} What is the final value of {query_reg}?"

    candidates = wrong_list + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "stateful_register_machine", "tier": "A"}


def _epistemic_belief_tracking(rng: random.Random) -> dict:
    """Multi-agent belief divergence (Sally-Anne variants)."""
    names = _pick_names(rng, rng.randint(2, 3))
    objects = rng.sample(["ball", "key", "book", "coin", "ring", "hat", "cup", "toy"], 1)
    obj = objects[0]
    locations = rng.sample(["kitchen", "garden", "bedroom", "closet", "garage",
                            "attic", "shed", "pantry", "hallway", "study"], 3)

    loc_real = locations[0]  # initial
    beliefs = {n: loc_real for n in names}

    # Person 0 puts object in loc_real, then leaves
    events = [f"{names[0]} puts the {obj} in the {loc_real}."]

    templates_leave = [
        f"{names[0]} leaves the room.",
        f"{names[0]} goes outside.",
        f"{names[0]} steps out for a moment.",
    ]
    events.append(rng.choice(templates_leave))
    absent = {names[0]}

    # Person 1 moves object
    new_loc = locations[1]
    templates_move = [
        f"{names[1]} moves the {obj} to the {new_loc}.",
        f"{names[1]} takes the {obj} and puts it in the {new_loc}.",
        f"While {names[0]} is away, {names[1]} relocates the {obj} to the {new_loc}.",
    ]
    events.append(rng.choice(templates_move))
    loc_real = new_loc

    for n in names:
        if n not in absent:
            beliefs[n] = loc_real
    # names[0] still believes original location

    # Optional: third person arrives and sees current state
    if len(names) == 3:
        events.append(f"{names[2]} arrives and sees the {obj} in the {new_loc}.")
        beliefs[names[2]] = new_loc

    query_person = names[0]  # the absent one
    correct = beliefs[query_person]

    wrong = [loc_real, locations[2]]
    if correct == loc_real:
        wrong = [locations[1], locations[2]]
    wrong = [w for w in wrong if w != correct][:2]
    wrong.append("Cannot be determined")

    prompt = f"{_intro(rng)}{' '.join(events)}{_maybe_distractor(rng)} Where does {query_person} think the {obj} is?"

    candidates = wrong + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "epistemic_belief_tracking", "tier": "A"}


def _constraint_satisfaction(rng: random.Random) -> dict:
    """3-4 entities with constraints. Query assignment."""
    n = rng.choice([3, 4])
    people = _pick_names(rng, n)
    items_pool = [
        ["coffee", "tea", "juice", "water"],
        ["red", "blue", "green", "yellow"],
        ["pizza", "pasta", "salad", "soup"],
        ["guitar", "piano", "violin", "drums"],
    ]
    items_set = rng.choice(items_pool)[:n]
    rng.shuffle(items_set)

    # Generate a valid assignment
    assignment = dict(zip(people, items_set))

    # Generate constraints that are consistent with the assignment
    constraints = []
    constraint_texts = []

    # Negative constraints: "X did NOT choose Y"
    for p in people:
        wrong_items = [it for it in items_set if it != assignment[p]]
        if wrong_items:
            wi = rng.choice(wrong_items)
            constraints.append(("not", p, wi))
            templates = [
                f"{p} did not choose {wi}.",
                f"{p}'s choice was not {wi}.",
                f"{wi} was not chosen by {p}.",
            ]
            constraint_texts.append(rng.choice(templates))

    # Add ordering/relative constraints instead of direct anchoring
    if n >= 3:
        # "X chose something alphabetically before Y's choice"
        p1, p2 = rng.sample(people, 2)
        if assignment[p1] < assignment[p2]:
            constraint_texts.append(f"{p1}'s choice comes alphabetically before {p2}'s choice.")
        else:
            constraint_texts.append(f"{p2}'s choice comes alphabetically before {p1}'s choice.")

    # One positive anchor (needed to make solvable) but phrased indirectly
    anchor = rng.choice(people)
    item = assignment[anchor]
    indirect_templates = [
        f"The person who chose {item} has a name starting with '{anchor[0]}'.",
        f"{anchor} did not choose any of {', '.join(it for it in items_set if it != item)}.",
    ]
    constraint_texts.append(rng.choice(indirect_templates))

    rng.shuffle(constraint_texts)

    # Query a non-anchor person
    query = rng.choice([p for p in people if p != anchor])
    correct = assignment[query]

    wrong = [it for it in items_set if it != correct]
    while len(wrong) < 3:
        wrong.append("Cannot be determined")
    wrong = wrong[:3]

    category_name = items_set[0]  # e.g., "coffee" to describe the category
    setup = rng.choice([
        f"{', '.join(people)} each chose a different item from: {', '.join(items_set)}.",
        f"Each of {', '.join(people)} selected exactly one of {', '.join(items_set)} (no two chose the same).",
    ])

    prompt = f"{_intro(rng)}{setup} {' '.join(constraint_texts)}{_maybe_distractor(rng)} What did {query} choose?"

    candidates = wrong + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "constraint_satisfaction", "tier": "A"}


def _recursive_evaluation(rng: random.Random) -> dict:
    """Evaluate f(n) given base case and recurrence relation."""
    base_n = rng.choice([0, 1])
    base_val = rng.randint(1, 5)
    # f(n) = a * f(n-1) + b
    a = rng.choice([2, 3])
    b = rng.choice([-1, 0, 1, 2, 3])
    query_n = rng.randint(3, 6)

    # Compute
    vals = {base_n: base_val}
    for i in range(base_n + 1, query_n + 1):
        vals[i] = a * vals[i - 1] + b

    correct = str(vals[query_n])

    # Build wrong candidates from intermediate values
    wrong = set()
    for k, v in vals.items():
        if k != query_n:
            wrong.add(str(v))
    wrong.add(str(vals[query_n] + rng.choice([1, -1, 2])))
    wrong.add(str(a * vals[query_n]))  # common over-application
    wrong.discard(correct)
    wrong_list = rng.sample(sorted(wrong), min(3, len(wrong)))
    while len(wrong_list) < 3:
        v = str(rng.randint(1, vals[query_n] * 2))
        if v != correct and v not in wrong_list:
            wrong_list.append(v)

    b_str = f" + {b}" if b > 0 else (f" - {abs(b)}" if b < 0 else "")
    templates = [
        f"Define f({base_n}) = {base_val}. For n > {base_n}, f(n) = {a} × f(n-1){b_str}. What is f({query_n})?",
        f"A function is defined: f({base_n}) = {base_val}, and f(n) = {a}·f(n-1){b_str} for n > {base_n}. Calculate f({query_n}).",
        f"Given the recurrence f({base_n}) = {base_val}, f(n) = {a}*f(n-1){b_str}. Find f({query_n}).",
    ]

    prompt = f"{_intro(rng)}{rng.choice(templates)}{_maybe_distractor(rng)}"

    candidates = wrong_list + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "recursive_evaluation", "tier": "A"}


def _counterfactual_dependency(rng: random.Random) -> dict:
    """Causal chain with independent facts. Alter one premise, query what changes."""
    n_chain = rng.randint(3, 5)
    names = _pick_names(rng, 1)[0]

    events = [f"event_{i}" for i in range(n_chain)]
    labels = rng.sample([
        "the power went out", "the alarm triggered", "the pipes froze",
        "the backup started", "the lights flickered", "the server rebooted",
        "the gate opened", "the sensor activated", "the pump stopped",
        "the heater turned on", "the fan spun up", "the lock engaged",
    ], n_chain)

    # Chain: label[0] → label[1] → ... → label[n-1]
    chain_text = []
    for i in range(n_chain - 1):
        templates = [
            f"{labels[i].capitalize()} caused {labels[i+1]}.",
            f"Because {labels[i]}, {labels[i+1]}.",
            f"{labels[i].capitalize()} led to {labels[i+1]}.",
        ]
        chain_text.append(rng.choice(templates))

    # Independent fact
    indep = rng.choice([
        f"{names} slept through the whole event",
        "The weather remained clear",
        "The morning newspaper was delivered on time",
        f"{names} had coffee at 7 AM",
    ])
    chain_text.append(f"{indep}.")
    rng.shuffle(chain_text)

    # Alter premise 0 (the root)
    templates_q = [
        f"If {labels[0]} had NOT happened, which of the following would still be true?",
        f"Suppose {labels[0]} never occurred. What would still hold?",
    ]

    correct = indep
    wrong = [labels[i] for i in range(1, min(4, n_chain))]
    while len(wrong) < 3:
        wrong.append("Everything would still happen")
    wrong = wrong[:3]

    prompt = f"{_intro(rng)}{' '.join(chain_text)} {rng.choice(templates_q)}"

    candidates = wrong + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "counterfactual_dependency", "tier": "A"}


def _multi_step_arithmetic_carried(rng: random.Random) -> dict:
    """Sequential operations on a value. Answer never appears in prompt."""
    start = rng.randint(2, 15)
    n_ops = rng.randint(4, 7)
    val = start
    ops_text = [f"Start with {start}."]
    history = [val]

    for _ in range(n_ops):
        op = rng.choice(["add", "sub", "mul", "div"])
        if op == "add":
            n = rng.randint(1, 20)
            ops_text.append(rng.choice([f"Add {n}.", f"Increase by {n}.", f"Plus {n}."]))
            val += n
        elif op == "sub":
            n = rng.randint(1, min(10, max(1, val - 1)))
            ops_text.append(rng.choice([f"Subtract {n}.", f"Take away {n}.", f"Minus {n}."]))
            val -= n
        elif op == "mul":
            n = rng.choice([2, 3, 4])
            ops_text.append(rng.choice([f"Multiply by {n}.", f"{'Double' if n==2 else 'Triple' if n==3 else 'Quadruple'} it."]))
            val *= n
        elif op == "div" and val % 2 == 0:
            ops_text.append(rng.choice(["Divide by 2.", "Halve it."]))
            val //= 2
        else:
            n = rng.randint(1, 10)
            ops_text.append(f"Add {n}.")
            val += n
        history.append(val)

    correct = str(val)

    wrong = set()
    for h in history[:-1]:
        wrong.add(str(h))
    wrong.add(str(start))
    wrong.add(str(val + rng.randint(1, 5)))
    wrong.add(str(val - rng.randint(1, 3)))
    wrong.discard(correct)
    wrong_list = rng.sample(sorted(wrong), min(3, len(wrong)))
    while len(wrong_list) < 3:
        v = str(rng.randint(1, val * 2 if val > 0 else 50))
        if v != correct and v not in wrong_list:
            wrong_list.append(v)

    prompt = f"{_intro(rng)}{' '.join(ops_text)}{_maybe_distractor(rng)} What is the result?"

    candidates = wrong_list + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "multi_step_arithmetic_carried", "tier": "A"}


def _bayesian_update(rng: random.Random) -> dict:
    """Prior + likelihood + false positive → posterior probability."""
    # Base rate: 1 in N
    base_denom = rng.choice([100, 200, 500, 1000])
    base_rate = 1 / base_denom

    # Sensitivity (true positive rate): 90-99%
    sensitivity = rng.choice([0.90, 0.95, 0.99])
    # False positive rate: 1-10%
    fpr = rng.choice([0.01, 0.02, 0.05, 0.10])

    # Bayes' theorem
    p_positive = sensitivity * base_rate + fpr * (1 - base_rate)
    posterior = (sensitivity * base_rate) / p_positive

    # Round to nearest percent
    posterior_pct = round(posterior * 100, 1)
    correct = f"{posterior_pct}%"

    # Wrong candidates
    wrong = [
        f"{round(sensitivity * 100)}%",  # base rate neglect trap
        f"{round(base_rate * 100, 2)}%",  # no update trap
        f"{round((1 - fpr) * 100)}%",  # specificity confusion
    ]
    wrong = [w for w in wrong if w != correct][:3]
    while len(wrong) < 3:
        v = f"{rng.randint(1, 95)}%"
        if v != correct and v not in wrong:
            wrong.append(v)

    sens_pct = int(sensitivity * 100)
    fpr_pct = int(fpr * 100)
    context = rng.choice(["disease", "defect", "condition", "fault"])
    test = rng.choice(["test", "screening", "diagnostic", "scan"])

    templates = [
        f"A {context} affects 1 in {base_denom} people. A {test} correctly identifies it {sens_pct}% of the time (sensitivity), but has a {fpr_pct}% false positive rate. If a person tests positive, what is the probability they actually have the {context}?",
        f"The prevalence of a {context} is 1/{base_denom}. A {test} has {sens_pct}% sensitivity and {fpr_pct}% false positive rate. Given a positive result, what is the posterior probability of having the {context}?",
        f"Out of every {base_denom} people, 1 has a rare {context}. The {test} detects it with {sens_pct}% accuracy but falsely flags {fpr_pct}% of healthy people. Someone tests positive. What's the chance they're truly affected?",
    ]

    prompt = f"{_intro(rng)}{rng.choice(templates)}{_maybe_distractor(rng)}"

    candidates = wrong + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "bayesian_update", "tier": "A"}


def _information_sufficiency(rng: random.Random) -> dict:
    """Mix of solvable and unsolvable systems. ~50% each."""
    is_solvable = rng.random() < 0.5
    names = _pick_names(rng, 2)

    if is_solvable:
        # 2 equations, 2 unknowns
        x_val = rng.randint(2, 15)
        y_val = rng.randint(2, 15)
        a1, b1 = rng.randint(1, 5), rng.randint(1, 5)
        c1 = a1 * x_val + b1 * y_val
        a2, b2 = rng.randint(1, 5), rng.randint(1, 5)
        # Ensure not parallel (linearly independent)
        while a1 * b2 == a2 * b1:
            a2 = rng.randint(1, 5)
            b2 = rng.randint(1, 5)
        c2 = a2 * x_val + b2 * y_val

        query = rng.choice(["x", "y"])
        correct_val = x_val if query == "x" else y_val
        correct = str(correct_val)

        eq1 = f"{a1}x + {b1}y = {c1}"
        eq2 = f"{a2}x + {b2}y = {c2}"

        templates = [
            f"Given: {eq1} and {eq2}. What is {query}?",
            f"Solve the system: {eq1}, {eq2}. Find {query}.",
        ]

        wrong = [str(correct_val + rng.choice([1, -1, 2])),
                 str(y_val if query == "x" else x_val),
                 "Cannot be determined"]
        wrong = [w for w in wrong if w != correct][:3]
    else:
        # 1 equation, 2 unknowns — underdetermined
        a1, b1 = rng.randint(1, 5), rng.randint(1, 5)
        c1 = rng.randint(10, 50)
        query = rng.choice(["x", "y"])
        correct = "Cannot be determined"

        templates = [
            f"Given: {a1}x + {b1}y = {c1}. What is {query}?",
            f"If {a1}x + {b1}y = {c1}, find the value of {query}.",
        ]

        # Wrong candidates: specific numbers that could be answers
        wrong = [str(rng.randint(1, 15)) for _ in range(3)]
        while "Cannot be determined" in wrong:
            wrong = [str(rng.randint(1, 15)) for _ in range(3)]

    prompt = f"{_intro(rng)}{rng.choice(templates)}{_maybe_distractor(rng)}"

    candidates = wrong + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "information_sufficiency", "tier": "A"}


# ===================================================================
# WAVE 2: Structural Reasoning (8 categories)
# ===================================================================

def _defeasible_reasoning(rng: random.Random) -> dict:
    """Default rules with exceptions. Most specific exception wins."""
    scenarios = [
        {
            "default": "Birds can fly",
            "exception1": "Penguins are birds that cannot fly",
            "exception2": "Baby penguins cannot even walk",
            "entity": "Tweety",
            "entity_type": "penguin",
            "query": "Can Tweety fly?",
            "correct": "No",
            "wrong": ["Yes", "Only short distances", "Cannot be determined"],
        },
        {
            "default": "Students must attend class",
            "exception1": "Students with medical exemptions can skip class",
            "exception2": "Medical exemptions expire after 30 days",
            "entity": None,
            "entity_type": None,
            "query": None,
            "correct": None,
            "wrong": [],
        },
    ]

    # Generate parametrically
    name = rng.choice(_NAMES)
    categories = rng.sample([
        ("animals", "swim", "fish", "clownfish", "freshwater clownfish"),
        ("vehicles", "need fuel", "electric vehicles", "solar cars", "indoor solar cars"),
        ("employees", "work on weekdays", "managers", "senior managers", "retired senior managers"),
        ("plants", "need sunlight", "mushrooms", "cave mushrooms", "deep cave mushrooms"),
    ], 1)[0]

    cat, default_prop, exc1_type, exc2_type, exc3_type = categories
    depth = rng.randint(2, 3)

    facts = [f"All {cat} {default_prop}."]
    facts.append(f"{exc1_type.capitalize()} are {cat} that do NOT {default_prop}.")

    entity_is = exc1_type
    expected = "No"

    if depth >= 3:
        facts.append(f"{exc2_type.capitalize()} are {exc1_type} that DO {default_prop} (exception to the exception).")
        entity_is = exc2_type
        expected = "Yes"

    facts.append(f"{name} is a {entity_is}.")
    rng.shuffle(facts[:-1])  # keep entity declaration at end

    correct = expected
    wrong = ["Yes" if correct == "No" else "No", "Cannot be determined",
             f"Only if {name} is also a {cat}"]
    wrong = [w for w in wrong if w != correct][:3]

    query = rng.choice([
        f"Does {name} {default_prop}?",
        f"Can we conclude that {name} {default_prop}?",
    ])

    prompt = f"{_intro(rng)}{' '.join(facts)}{_maybe_distractor(rng)} {query}"

    candidates = wrong + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "defeasible_reasoning", "tier": "A"}


def _logical_consistency_checking(rng: random.Random) -> dict:
    """3-4 propositional statements. Are they jointly consistent?"""
    name = rng.choice(_NAMES)
    n_statements = rng.randint(3, 4)

    # Generate consistent or inconsistent set
    is_consistent = rng.random() < 0.5

    if not is_consistent:
        # Create a contradiction
        templates = [
            {
                "statements": [
                    f"{name} is taller than 6 feet.",
                    f"Everyone taller than 6 feet must duck through the doorway.",
                    f"{name} does not need to duck through the doorway.",
                ],
                "contradiction": f"Statement 1 and 2 imply {name} must duck, but statement 3 says otherwise.",
            },
            {
                "statements": [
                    f"All of {name}'s pets are dogs.",
                    f"{name} has a pet named Whiskers.",
                    f"Whiskers is a cat.",
                ],
                "contradiction": f"Whiskers must be a dog (statement 1-2) but is a cat (statement 3).",
            },
            {
                "statements": [
                    f"The meeting is on Monday.",
                    f"The meeting is after the deadline.",
                    f"The deadline is on Wednesday.",
                ],
                "contradiction": "Monday is before Wednesday, contradicting statement 2.",
            },
        ]
        t = rng.choice(templates)
        correct = "No, they are inconsistent"
        wrong = ["Yes, they are consistent", "Cannot be determined",
                 "Only the first two are consistent"]
    else:
        templates = [
            {
                "statements": [
                    f"{name} has a dog.",
                    f"{name}'s dog is brown.",
                    f"Some brown dogs are large.",
                ],
            },
            {
                "statements": [
                    f"The store opens at 9 AM.",
                    f"The delivery arrives before the store opens.",
                    f"The delivery arrives at 8 AM.",
                ],
            },
            {
                "statements": [
                    f"All team members submitted their reports.",
                    f"{name} is a team member.",
                    f"{name} submitted a 10-page report.",
                ],
            },
        ]
        t = rng.choice(templates)
        correct = "Yes, they are consistent"
        wrong = ["No, they are inconsistent", "Cannot be determined",
                 "Only if additional information is given"]

    numbered = " ".join(f"({i+1}) {s}" for i, s in enumerate(t["statements"]))
    query = rng.choice([
        "Are these statements jointly consistent?",
        "Can all of these statements be true at the same time?",
        "Is there a contradiction among these statements?",
    ])

    prompt = f"{_intro(rng)}{numbered}{_maybe_distractor(rng)} {query}"

    candidates = wrong + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "logical_consistency_checking", "tier": "A"}


def _temporal_interval_algebra(rng: random.Random) -> dict:
    """Events with start/end times. Query overlap or gap."""
    names = _pick_names(rng, rng.randint(2, 3))
    events = []
    for i, name in enumerate(names):
        start = rng.randint(8, 16)
        duration = rng.randint(1, 3)
        end = start + duration
        events.append({"name": name, "event": rng.choice(["meeting", "class", "shift", "appointment"]),
                       "start": start, "end": end})

    # Format times
    def fmt(h):
        if h < 12: return f"{h}:00 AM"
        elif h == 12: return "12:00 PM"
        else: return f"{h-12}:00 PM"

    event_texts = []
    for e in events:
        event_texts.append(f"{e['name']}'s {e['event']} runs from {fmt(e['start'])} to {fmt(e['end'])}.")

    # Query: do any two overlap?
    overlap_pairs = []
    for i in range(len(events)):
        for j in range(i+1, len(events)):
            if events[i]['start'] < events[j]['end'] and events[j]['start'] < events[i]['end']:
                overlap_pairs.append((events[i]['name'], events[j]['name']))

    if overlap_pairs:
        pair = rng.choice(overlap_pairs)
        query = f"Do {pair[0]}'s and {pair[1]}'s schedules overlap?"
        correct = "Yes"
        wrong = ["No", "Only partially", "Cannot be determined"]
    else:
        i, j = 0, 1
        query = f"Do {events[i]['name']}'s and {events[j]['name']}'s schedules overlap?"
        correct = "No"
        wrong = ["Yes", "Only partially", "Cannot be determined"]

    prompt = f"{_intro(rng)}{' '.join(event_texts)}{_maybe_distractor(rng)} {query}"

    candidates = wrong + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "temporal_interval_algebra", "tier": "A"}


def _stable_model_finding(rng: random.Random) -> dict:
    """Mutually dependent variables with numerical propagation. Find self-consistent values."""
    names = rng.sample(["X", "Y", "Z", "W", "P", "Q"], 3)
    # Create a system where values depend on each other
    # X = 2*Y - 1, Y = Z + 3, Z = 5 → X = 2*(5+3)-1 = 15
    z_val = rng.randint(2, 8)
    y_offset = rng.randint(1, 5)
    x_mult = rng.choice([2, 3])
    x_offset = rng.choice([-1, 0, 1, 2])

    y_val = z_val + y_offset
    x_val = x_mult * y_val + x_offset

    x_off_str = f" + {x_offset}" if x_offset > 0 else (f" - {abs(x_offset)}" if x_offset < 0 else "")
    rules = [
        f"{names[0]} = {x_mult} * {names[1]}{x_off_str}.",
        f"{names[1]} = {names[2]} + {y_offset}.",
        f"{names[2]} = {z_val}.",
    ]
    rng.shuffle(rules)

    query_idx = rng.choice([0, 1])
    query_var = names[query_idx]
    correct_val = x_val if query_idx == 0 else y_val
    correct = str(correct_val)

    wrong = [str(z_val), str(y_val if query_idx == 0 else x_val),
             str(correct_val + rng.choice([1, -1, 3]))]
    wrong = [w for w in wrong if w != correct][:3]
    while len(wrong) < 3:
        wrong.append(str(rng.randint(1, 50)))

    prompt = f"{_intro(rng)}Variables are defined by: {' '.join(rules)}{_maybe_distractor(rng)} What is the value of {query_var}?"

    candidates = wrong + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "stable_model_finding", "tier": "A"}


def _conditional_graph_traversal(rng: random.Random) -> dict:
    """Rooms with locked doors requiring keys. Can you reach the goal?"""
    rooms = rng.sample(["Hall", "Library", "Kitchen", "Garden", "Tower",
                        "Cellar", "Study", "Chapel", "Armory", "Vault"], 5)
    # Place a key in one room that unlocks a door to another
    key_room = rooms[1]
    locked_room = rooms[3]
    goal_room = rooms[4]

    # Path: rooms[0] → rooms[1] (get key) → rooms[2] → rooms[3] (use key) → rooms[4]
    connections = [
        f"The {rooms[0]} connects to the {rooms[1]} and the {rooms[2]}.",
        f"The {rooms[1]} contains a gold key.",
        f"The {rooms[2]} connects to the {rooms[3]}, but the door is locked (requires gold key).",
        f"The {rooms[3]} connects to the {goal_room}.",
    ]
    # Add a dead-end
    connections.append(f"The {rooms[0]} also connects to a dead-end corridor.")

    rng.shuffle(connections)

    query = f"Starting in the {rooms[0]}, can you reach the {goal_room}?"
    correct = f"Yes, go to {rooms[1]} for the key, then {rooms[2]}, unlock {rooms[3]}, reach {goal_room}"

    # Simplified correct answer
    correct = "Yes, by getting the key first"
    wrong = [
        "No, the locked door blocks all paths",
        f"Yes, go directly through {rooms[2]}",
        "Cannot be determined",
    ]

    prompt = f"{_intro(rng)}{' '.join(connections)}{_maybe_distractor(rng)} {query}"

    candidates = wrong + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "conditional_graph_traversal", "tier": "A"}


def _rule_application_order(rng: random.Random) -> dict:
    """Rewrite rules applied in sequence. Order matters."""
    start = rng.choice(["AAB", "ABA", "BAA", "ABB", "BBA"])

    rules = []
    rule_texts = []
    # Simple string rewrite rules
    r1 = ("AB", "BA")
    r2 = ("BA", "AB")
    r3 = ("AA", "A")
    r4 = ("BB", "B")

    available = [(r1, "Replace every 'AB' with 'BA'"),
                 (r3, "Replace every 'AA' with 'A'"),
                 (r4, "Replace every 'BB' with 'B'")]

    chosen = rng.sample(available, rng.randint(2, 3))

    # Apply rules in order
    val = start
    steps = []
    for (old, new), text in chosen:
        rule_texts.append(text)
        val = val.replace(old, new)
        steps.append(val)

    correct = val

    # Wrong: apply in reverse order
    val_rev = start
    for (old, new), text in reversed(chosen):
        val_rev = val_rev.replace(old, new)

    wrong = [val_rev, start, steps[0] if steps else start]
    wrong = [w for w in wrong if w != correct]
    while len(wrong) < 3:
        w = rng.choice(["A", "B", "AB", "BA", "ABA", "BAB", "AA", "BB"])
        if w != correct and w not in wrong:
            wrong.append(w)
    wrong = wrong[:3]

    numbered_rules = " ".join(f"Rule {i+1}: {t}." for i, t in enumerate(rule_texts))
    prompt = f"{_intro(rng)}Starting string: '{start}'. Apply these rules in order: {numbered_rules}{_maybe_distractor(rng)} What is the final string?"

    candidates = wrong + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "rule_application_order", "tier": "A"}


def _compositional_instruction_following(rng: random.Random) -> dict:
    """Composed operations on a list. Query the result."""
    size = rng.randint(5, 8)
    lst = [rng.randint(1, 20) for _ in range(size)]

    ops = []
    ops_text = []
    val = list(lst)

    n_ops = rng.randint(2, 4)
    available_ops = ["sort", "reverse", "first_n", "last_n", "sum", "remove_odd", "remove_even"]

    for _ in range(n_ops):
        op = rng.choice(available_ops)
        if op == "sort" and len(val) > 1:
            ops_text.append("Sort the list in ascending order.")
            val.sort()
        elif op == "reverse" and len(val) > 1:
            ops_text.append("Reverse the list.")
            val.reverse()
        elif op == "first_n" and len(val) > 2:
            n = rng.randint(2, min(4, len(val)))
            ops_text.append(f"Keep only the first {n} elements.")
            val = val[:n]
        elif op == "last_n" and len(val) > 2:
            n = rng.randint(2, min(4, len(val)))
            ops_text.append(f"Keep only the last {n} elements.")
            val = val[-n:]
        elif op == "sum" and len(val) > 1:
            ops_text.append("Sum all elements.")
            val = [sum(val)]
        elif op == "remove_odd":
            ops_text.append("Remove all odd numbers.")
            val = [x for x in val if x % 2 == 0]
            if not val:
                val = [0]
        elif op == "remove_even":
            ops_text.append("Remove all even numbers.")
            val = [x for x in val if x % 2 != 0]
            if not val:
                val = [0]

    if len(val) == 1:
        correct = str(val[0])
    else:
        correct = str(val)

    # Wrong candidates
    wrong = set()
    wrong.add(str(lst))  # original list
    wrong.add(str(sorted(lst)))
    wrong.add(str(sum(lst)))
    wrong.discard(correct)
    wrong_list = list(wrong)[:3]
    while len(wrong_list) < 3:
        w = str(rng.randint(1, 100))
        if w != correct and w not in wrong_list:
            wrong_list.append(w)

    prompt = f"{_intro(rng)}Given the list: {lst}. {' '.join(ops_text)}{_maybe_distractor(rng)} What is the result?"

    candidates = wrong_list + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "compositional_instruction_following", "tier": "A"}


# ===================================================================
# WAVE 3: NL-Heavy (4 categories)
# ===================================================================

def _referent_tracking_anaphora(rng: random.Random) -> dict:
    """Pronoun resolution where proximity gives wrong referent."""
    names = _pick_names(rng, 2)
    n1, n2 = names

    scenarios = [
        {
            "text": f"{n1} told {n2} that she would need to leave early. {n2} was disappointed.",
            "query": f"Who needs to leave early?",
            "correct": n1,  # "she" = speaker, not the closer name
            "wrong": [n2, "Both", "Cannot be determined"],
        },
        {
            "text": f"{n1} lent {n2} a book. A week later, she returned it.",
            "query": "Who returned the book?",
            "correct": n2,  # borrower returns
            "wrong": [n1, "Neither", "Cannot be determined"],
        },
        {
            "text": f"{n1} asked {n2} to help with the project, but she was too busy.",
            "query": "Who was too busy?",
            "correct": n2,  # "but she" = the asked person declining
            "wrong": [n1, "Both", "Cannot be determined"],
        },
        {
            "text": f"{n1} congratulated {n2} after she won the competition.",
            "query": "Who won the competition?",
            "correct": n2,  # "she won" = the congratulated person
            "wrong": [n1, "Both", "Cannot be determined"],
        },
    ]

    s = rng.choice(scenarios)
    prompt = f"{_intro(rng)}{s['text']}{_maybe_distractor(rng)} {s['query']}"

    candidates = s['wrong'] + [s['correct']]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": s['correct'],
            "category": "referent_tracking_anaphora", "tier": "B"}


def _closed_world_negation(rng: random.Random) -> dict:
    """Enumerated set. Query about unlisted member."""
    category = rng.choice([
        ("fruits in the basket", ["apple", "banana", "orange", "grape"]),
        ("students in the class", None),
        ("books on the shelf", ["novel", "textbook", "dictionary", "atlas"]),
        ("tools in the box", ["hammer", "screwdriver", "pliers", "wrench"]),
    ])

    cat_name = category[0]
    if category[1]:
        items = rng.sample(category[1], rng.randint(3, len(category[1])))
    else:
        items = rng.sample(_NAMES, rng.randint(3, 5))

    # Pick a query item NOT in the list
    if category[1]:
        all_possible = category[1]
        query_item = rng.choice([x for x in ["pear", "mango", "kiwi", "plum", "fig",
                                              "encyclopedia", "saw", "drill"]
                                 if x not in items])
    else:
        query_item = rng.choice([n for n in _NAMES if n not in items])

    listing = ", ".join(items)
    templates = [
        f"The {cat_name} are: {listing}. That is the complete list.",
        f"The only {cat_name} are {listing}. There are no others.",
        f"Here is the exhaustive list of {cat_name}: {listing}.",
    ]

    correct = "No"
    wrong = ["Yes", "Cannot be determined", "Possibly"]

    query = f"Is {query_item} among the {cat_name}?"
    prompt = f"{_intro(rng)}{rng.choice(templates)}{_maybe_distractor(rng)} {query}"

    candidates = wrong + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "closed_world_negation", "tier": "A"}


def _argument_structure_analysis(rng: random.Random) -> dict:
    """Evidence that looks supportive but actually undermines (or vice versa)."""
    scenarios = [
        {
            "conclusion": "The new drug is effective",
            "evidence": "In the trial, 80% of patients improved. However, the placebo group also saw 78% improvement.",
            "correct": "Undermines",
            "wrong": ["Supports", "No bearing", "Cannot be determined"],
        },
        {
            "conclusion": "Exercise improves memory",
            "evidence": "A study found that the exercise group scored 15% higher on memory tests. The groups were randomly assigned and the study was double-blind.",
            "correct": "Supports",
            "wrong": ["Undermines", "No bearing", "Cannot be determined"],
        },
        {
            "conclusion": "The restaurant's food quality has improved",
            "evidence": "Online ratings went from 3.2 to 4.5 stars. During the same period, the restaurant started offering a 20% discount for 5-star reviews.",
            "correct": "No bearing (confounded)",
            "wrong": ["Supports", "Undermines", "Cannot be determined"],
        },
        {
            "conclusion": "Country X's education system is better than Country Y's",
            "evidence": "Country X spends 20% more per student. Country X's test scores are 5% lower than Country Y's.",
            "correct": "Undermines",
            "wrong": ["Supports", "No bearing", "Cannot be determined"],
        },
    ]

    s = rng.choice(scenarios)
    prompt = f"{_intro(rng)}Conclusion: {s['conclusion']}. Evidence: {s['evidence']}{_maybe_distractor(rng)} Does this evidence support, undermine, or have no bearing on the conclusion?"

    candidates = s['wrong'] + [s['correct']]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": s['correct'],
            "category": "argument_structure_analysis", "tier": "B"}


def _implicit_constraint_inference(rng: random.Random) -> dict:
    """Unstated constraint (pigeonhole, parity, completeness) makes problem solvable."""
    scenario_type = rng.choice(["pigeonhole", "parity", "completeness"])

    if scenario_type == "pigeonhole":
        items = rng.randint(5, 10)
        boxes = rng.randint(2, 4)
        min_per = math.ceil(items / boxes)
        prompt_text = f"There are {items} balls and {boxes} boxes. Each ball is placed in exactly one box. What is the minimum number of balls that must be in at least one box?"
        correct = str(min_per)
        wrong = [str(min_per - 1), str(min_per + 1), str(items // boxes)]
        wrong = [w for w in wrong if w != correct][:3]
    elif scenario_type == "parity":
        n = rng.randint(5, 10)
        prompt_text = f"A group of {n} people shake hands. Each person shakes hands with at least one other person. Can the total number of handshakes be odd?"
        # Each handshake involves 2 people, so sum of handshakes per person is even
        # But total handshakes = sum / 2, which can be odd or even
        # Actually the parity constraint: sum of degrees is always even
        correct = "Yes" if True else "No"  # Total handshakes CAN be odd
        # Actually: total handshakes = edges, which can be any number. But sum of degrees is always even.
        # The question as stated: yes, total handshakes can be odd (3 people each shake with both others = 3 handshakes)
        correct = "Yes"
        wrong = ["No", "Only if n is even", "Cannot be determined"]
    else:  # completeness
        name = rng.choice(_NAMES)
        total = rng.randint(5, 8)
        known = total - 1
        known_sum = sum(rng.sample(range(1, 15), known))
        total_sum = known_sum + rng.randint(1, 10)
        last = total_sum - known_sum
        prompt_text = f"{name} has {total} scores. The first {known} scores sum to {known_sum}. The total of all {total} scores is {total_sum}. What is the last score?"
        correct = str(last)
        wrong = [str(last + 1), str(last - 1), str(total_sum)]
        wrong = [w for w in wrong if w != correct][:3]
        while len(wrong) < 3:
            wrong.append(str(rng.randint(1, 20)))

    prompt = f"{_intro(rng)}{prompt_text}{_maybe_distractor(rng)}"

    candidates = wrong + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "implicit_constraint_inference", "tier": "A"}


# ===================================================================
# WAVE 4: Formal / Quantitative Reasoning (5 categories)
# ===================================================================

def _quantifier_scope_ambiguity(rng: random.Random) -> dict:
    """'Every X did a Y' with explicit model — disambiguate same-object vs different."""
    students = _pick_names(rng, 3)
    item_pools = [
        ("book", ["Moby Dick", "Dune", "1984", "Hamlet", "Ulysses",
                   "Beloved", "Emma", "Dracula", "Neuromancer", "Solaris"]),
        ("movie", ["Jaws", "Alien", "Psycho", "Inception", "Arrival",
                    "Parasite", "Vertigo", "Her", "Stalker", "Ran"]),
        ("song", ["Imagine", "Bohemian Rhapsody", "Yesterday", "Hallelujah",
                   "Waterloo", "Roxanne", "Creep", "Heroes", "Purple Rain", "Respect"]),
    ]
    item_kind, item_names = rng.choice(item_pools)

    same = rng.random() < 0.5

    if same:
        shared = rng.choice(item_names)
        assignments = {s: shared for s in students}
    else:
        chosen = rng.sample(item_names, 3)
        assignments = {s: c for s, c in zip(students, chosen)}

    # Build model description
    model_lines = [f"  {s} read \"{assignments[s]}\"." if item_kind == "book"
                   else f"  {s} watched \"{assignments[s]}\"." if item_kind == "movie"
                   else f"  {s} listened to \"{assignments[s]}\"."
                   for s in students]

    verb = {"book": "read", "movie": "watched", "song": "listened to"}[item_kind]
    article = "a" if item_kind != "song" else "a"

    ambig_templates = [
        f"Every student {verb} {article} {item_kind}.",
        f"Each of the students {verb} {article} {item_kind}.",
        f"All students {verb} {article} {item_kind}.",
    ]
    ambig_sent = rng.choice(ambig_templates)

    question_templates = [
        f"The sentence \"{ambig_sent}\" is ambiguous. Given the model below, which reading is correct?\n\n" + "\n".join(model_lines) + "\n\nDid they all {verb} the SAME {item_kind}, or DIFFERENT {item_kind}s?",
        f"Consider: \"{ambig_sent}\"\n\nHere is what actually happened:\n" + "\n".join(model_lines) + f"\n\nUnder this model, is the correct reading 'same {item_kind}' or 'different {item_kind}s'?",
        f"\"{ambig_sent}\"\n\nModel:\n" + "\n".join(model_lines) + f"\n\nWhich interpretation does this model support: all the same {item_kind} or each a different {item_kind}?",
    ]

    prompt = f"{_intro(rng)}{rng.choice(question_templates)}{_maybe_distractor(rng)}"

    if same:
        correct = f"Same {item_kind}"
        wrong = [f"Different {item_kind}s",
                 "Cannot be determined",
                 f"Only two shared the same {item_kind}"]
    else:
        correct = f"Different {item_kind}s"
        wrong = [f"Same {item_kind}",
                 "Cannot be determined",
                 f"Only two shared the same {item_kind}"]

    candidates = wrong + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "quantifier_scope_ambiguity", "tier": "A"}


def _process_simulation(rng: random.Random) -> dict:
    """Two processes with different rates and offsets — when does one overtake the other?"""
    name_a, name_b = _pick_names(rng, 2)
    item_pools = ["widgets", "parts", "units", "bottles", "boxes", "reports"]
    item = rng.choice(item_pools)

    rate_a = rng.randint(2, 6)
    rate_b = rng.randint(rate_a + 1, rate_a + 5)  # B is faster
    delay_b = rng.randint(1, 4)  # B starts late

    # A total at time t: rate_a * t
    # B total at time t: rate_b * (t - delay_b) for t >= delay_b
    # B > A when rate_b*(t - delay_b) > rate_a*t
    # t*(rate_b - rate_a) > rate_b*delay_b
    # t > rate_b*delay_b / (rate_b - rate_a)
    threshold = (rate_b * delay_b) / (rate_b - rate_a)
    # First integer hour where B's total exceeds A's
    import math as _m
    answer_t = _m.ceil(threshold) if threshold != int(threshold) else int(threshold) + 1

    a_total_at_answer = rate_a * answer_t
    b_total_at_answer = rate_b * (answer_t - delay_b)

    setup_templates = [
        f"{name_a} produces {rate_a} {item} per hour starting at hour 0. {name_b} produces {rate_b} {item} per hour but starts at hour {delay_b}. At what hour does {name_b}'s total first exceed {name_a}'s total?",
        f"Machine {name_a} makes {rate_a} {item}/hour from the start. Machine {name_b} makes {rate_b} {item}/hour but doesn't begin until hour {delay_b}. When does {name_b} first have more total {item} than {name_a}?",
        f"Starting at t=0, {name_a} outputs {rate_a} {item} every hour. {name_b} outputs {rate_b} {item} every hour but only begins at t={delay_b}. At what hour t does {name_b}'s cumulative output first surpass {name_a}'s?",
    ]

    prompt = f"{_intro(rng)}{rng.choice(setup_templates)}{_maybe_distractor(rng)}"
    correct = str(answer_t)

    # Traps: the delay itself, threshold (non-integer), off-by-one, ratio
    wrong = set()
    wrong.add(str(delay_b))  # naive "when B starts"
    wrong.add(str(answer_t - 1))  # off by one (they might be equal here)
    wrong.add(str(answer_t + 1))
    wrong.add(str(int(threshold)))  # truncated threshold
    wrong.add(str(rate_b - rate_a))  # rate difference
    wrong.discard(correct)
    wrong_list = rng.sample(sorted(wrong), min(3, len(wrong)))
    while len(wrong_list) < 3:
        v = str(rng.randint(1, answer_t + 5))
        if v != correct and v not in wrong_list:
            wrong_list.append(v)

    candidates = wrong_list + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "process_simulation", "tier": "A"}


def _graph_path_existence(rng: random.Random) -> dict:
    """Small graph (4-6 nodes), ask if a path exists between two nodes."""
    n_nodes = rng.randint(4, 6)
    labels = rng.sample(["A", "B", "C", "D", "E", "F", "G", "H"], n_nodes)
    # Use room/city names for flavor
    place_pools = [
        ["Room", ["Lobby", "Kitchen", "Library", "Garage", "Attic", "Cellar", "Study", "Den"]],
        ["City", ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel"]],
    ]
    place_kind, place_names = rng.choice(place_pools)
    nodes = rng.sample(place_names, n_nodes)

    # Build a random sparse graph ensuring we control connectivity
    has_path = rng.random() < 0.6  # 60% chance path exists

    edges = set()
    if has_path:
        # Create a guaranteed path from nodes[0] to nodes[-1]
        path_nodes = [nodes[0]]
        remaining = list(nodes[1:])
        rng.shuffle(remaining)
        # Ensure nodes[-1] is the end
        if nodes[-1] in remaining:
            remaining.remove(nodes[-1])
        path_nodes.extend(remaining)
        path_nodes.append(nodes[-1])
        for i in range(len(path_nodes) - 1):
            edges.add((path_nodes[i], path_nodes[i + 1]))
        # Add a few extra edges
        for _ in range(rng.randint(0, 2)):
            a, b = rng.sample(nodes, 2)
            edges.add((a, b))
    else:
        # Split into two disconnected components
        mid = n_nodes // 2
        comp1 = nodes[:mid]
        comp2 = nodes[mid:]
        for i in range(len(comp1) - 1):
            edges.add((comp1[i], comp1[i + 1]))
        for i in range(len(comp2) - 1):
            edges.add((comp2[i], comp2[i + 1]))
        # Extra edges within components only
        for _ in range(rng.randint(0, 2)):
            comp = rng.choice([comp1, comp2])
            if len(comp) >= 2:
                a, b = rng.sample(comp, 2)
                edges.add((a, b))

    source = nodes[0]
    target = nodes[-1]

    # Verify actual connectivity via BFS
    adj = {n: set() for n in nodes}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)  # undirected

    visited = set()
    queue = [source]
    while queue:
        cur = queue.pop(0)
        if cur in visited:
            continue
        visited.add(cur)
        for nb in adj[cur]:
            if nb not in visited:
                queue.append(nb)
    actual_path = target in visited
    correct = "Yes" if actual_path else "No"

    edge_strs = []
    for a, b in sorted(edges):
        templates = [
            f"{a} connects to {b}.",
            f"There is a link between {a} and {b}.",
            f"{a} and {b} are connected.",
        ]
        edge_strs.append(rng.choice(templates))
    rng.shuffle(edge_strs)

    question_templates = [
        f"Given these connections between {place_kind.lower()}s:\n" + " ".join(edge_strs) + f"\n\nCan you get from {source} to {target}?",
        f"The following {place_kind.lower()}s are connected:\n" + " ".join(edge_strs) + f"\n\nIs there a path from {source} to {target}?",
        f"{place_kind} connections: " + " ".join(edge_strs) + f" Is it possible to travel from {source} to {target} using these connections?",
    ]

    prompt = f"{_intro(rng)}{rng.choice(question_templates)}{_maybe_distractor(rng)}"

    wrong_list = []
    if correct == "Yes":
        wrong_list = ["No", "Only via direct connection", "Not enough information"]
    else:
        wrong_list = ["Yes", "Only in one direction", "Not enough information"]

    candidates = wrong_list + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "graph_path_existence", "tier": "A"}


def _set_membership_operations(rng: random.Random) -> dict:
    """Set operations: union, intersection, difference, symmetric difference."""
    pool = list(range(1, 20))
    size_a = rng.randint(3, 6)
    size_b = rng.randint(3, 6)
    overlap = rng.randint(1, min(size_a, size_b) - 1)

    shared = rng.sample(pool, overlap)
    remaining = [x for x in pool if x not in shared]
    only_a = rng.sample(remaining, size_a - overlap)
    remaining2 = [x for x in remaining if x not in only_a]
    only_b = rng.sample(remaining2, min(size_b - overlap, len(remaining2)))

    set_a = sorted(shared + only_a)
    set_b = sorted(shared + only_b)
    rng.shuffle(set_a)
    rng.shuffle(set_b)

    sa = set(set_a)
    sb = set(set_b)

    op = rng.choice(["intersection", "union", "difference", "symmetric_difference"])

    if op == "intersection":
        result = sorted(sa & sb)
        op_symbol = rng.choice(["A ∩ B", "A intersection B", "the intersection of A and B"])
    elif op == "union":
        result = sorted(sa | sb)
        op_symbol = rng.choice(["A ∪ B", "A union B", "the union of A and B"])
    elif op == "difference":
        result = sorted(sa - sb)
        op_symbol = rng.choice(["A - B", "A minus B", "elements in A but not in B"])
    else:
        result = sorted(sa.symmetric_difference(sb))
        op_symbol = rng.choice(["A △ B", "A symmetric difference B",
                                 "elements in exactly one of A or B"])

    correct = "{" + ", ".join(str(x) for x in result) + "}"

    # Wrong candidates: other operations as traps
    all_results = {
        "intersection": sorted(sa & sb),
        "union": sorted(sa | sb),
        "difference": sorted(sa - sb),
        "symmetric_difference": sorted(sa.symmetric_difference(sb)),
    }
    wrong = set()
    for k, v in all_results.items():
        s = "{" + ", ".join(str(x) for x in v) + "}"
        if s != correct:
            wrong.add(s)
    # Also add B - A as a trap
    b_minus_a = sorted(sb - sa)
    wrong.add("{" + ", ".join(str(x) for x in b_minus_a) + "}")
    wrong.discard(correct)
    wrong_list = rng.sample(sorted(wrong), min(3, len(wrong)))
    while len(wrong_list) < 3:
        fake = sorted(rng.sample(pool, rng.randint(2, 5)))
        s = "{" + ", ".join(str(x) for x in fake) + "}"
        if s != correct and s not in wrong_list:
            wrong_list.append(s)

    set_a_str = "{" + ", ".join(str(x) for x in set_a) + "}"
    set_b_str = "{" + ", ".join(str(x) for x in set_b) + "}"

    question_templates = [
        f"Set A = {set_a_str}. Set B = {set_b_str}. What is {op_symbol}?",
        f"Given A = {set_a_str} and B = {set_b_str}, compute {op_symbol}.",
        f"Let A = {set_a_str}, B = {set_b_str}. Find {op_symbol}.",
    ]

    prompt = f"{_intro(rng)}{rng.choice(question_templates)}{_maybe_distractor(rng)}"

    candidates = wrong_list + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "set_membership_operations", "tier": "A"}


def _truth_table_evaluation(rng: random.Random) -> dict:
    """Evaluate compound boolean expression with 2-3 variables."""
    n_vars = rng.choice([2, 2, 3])  # weight toward 2
    var_names = ["P", "Q", "R"][:n_vars]
    values = {v: rng.choice([True, False]) for v in var_names}

    def _fmt_bool(b):
        return "True" if b else "False"

    # Build compound expression (2-3 connectives)
    if n_vars == 2:
        expr_builders = [
            lambda: ("({P} AND {Q}) OR (NOT {P})",
                     (values["P"] and values["Q"]) or (not values["P"])),
            lambda: ("(NOT {P}) AND ({P} OR {Q})",
                     (not values["P"]) and (values["P"] or values["Q"])),
            lambda: ("({P} OR {Q}) AND (NOT ({P} AND {Q}))",
                     (values["P"] or values["Q"]) and not (values["P"] and values["Q"])),
            lambda: ("NOT ({P} AND {Q})",
                     not (values["P"] and values["Q"])),
            lambda: ("({P} AND (NOT {Q})) OR ({Q} AND (NOT {P}))",
                     (values["P"] and not values["Q"]) or (values["Q"] and not values["P"])),
            lambda: ("(NOT {P}) OR (NOT {Q})",
                     (not values["P"]) or (not values["Q"])),
        ]
    else:
        expr_builders = [
            lambda: ("({P} AND {Q}) OR {R}",
                     (values["P"] and values["Q"]) or values["R"]),
            lambda: ("({P} OR {Q}) AND (NOT {R})",
                     (values["P"] or values["Q"]) and (not values["R"])),
            lambda: ("NOT ({P} AND {Q} AND {R})",
                     not (values["P"] and values["Q"] and values["R"])),
            lambda: ("({P} OR {R}) AND ({Q} OR (NOT {R}))",
                     (values["P"] or values["R"]) and (values["Q"] or (not values["R"]))),
            lambda: ("(NOT {P}) AND ({Q} OR {R})",
                     (not values["P"]) and (values["Q"] or values["R"])),
            lambda: ("({P} AND {Q}) OR ({Q} AND {R}) OR ({R} AND {P})",
                     (values["P"] and values["Q"]) or (values["Q"] and values["R"]) or (values["R"] and values["P"])),
        ]

    builder = rng.choice(expr_builders)
    expr_template, result = builder()
    expr_str = expr_template.format(**{v: v for v in var_names})
    correct = _fmt_bool(result)

    assign_str = ", ".join(f"{v} is {_fmt_bool(values[v])}" for v in var_names)

    question_templates = [
        f"{assign_str}. What is {expr_str}?",
        f"Given {assign_str}: evaluate {expr_str}.",
        f"Let {assign_str}. Compute {expr_str}.",
        f"If {assign_str}, what does {expr_str} evaluate to?",
    ]

    prompt = f"{_intro(rng)}{rng.choice(question_templates)}{_maybe_distractor(rng)}"

    # Wrong candidates
    wrong_list = [_fmt_bool(not result)]  # opposite
    # Add sub-expression traps
    sub_traps = set()
    sub_traps.add(_fmt_bool(values["P"] and values["Q"]))
    if n_vars == 3:
        sub_traps.add(_fmt_bool(values["Q"] and values["R"]))
    sub_traps.add(_fmt_bool(not values["P"]))
    sub_traps.discard(correct)
    for s in sub_traps:
        if s not in wrong_list:
            wrong_list.append(s)
    # Ensure we have exactly 3 wrong + ensure "Cannot be determined" trap
    if "Cannot be determined" not in wrong_list and len(wrong_list) < 3:
        wrong_list.append("Cannot be determined")
    wrong_list = wrong_list[:3]
    while len(wrong_list) < 3:
        wrong_list.append("Cannot be determined")

    candidates = wrong_list + [correct]
    rng.shuffle(candidates)
    return {"prompt": prompt, "candidates": candidates, "correct": correct,
            "category": "truth_table_evaluation", "tier": "A"}


# ===================================================================
# Generator registry
# ===================================================================

TIER2_GENERATORS = [
    # Wave 1: Core Computational Primitives
    _stateful_register_machine,
    _epistemic_belief_tracking,
    _constraint_satisfaction,
    _recursive_evaluation,
    _counterfactual_dependency,
    _multi_step_arithmetic_carried,
    _bayesian_update,
    _information_sufficiency,
    # Wave 2: Structural Reasoning
    _defeasible_reasoning,
    _logical_consistency_checking,
    _temporal_interval_algebra,
    _stable_model_finding,
    _conditional_graph_traversal,
    _rule_application_order,
    _compositional_instruction_following,
    # Wave 3: NL-Heavy
    _referent_tracking_anaphora,
    _closed_world_negation,
    _argument_structure_analysis,
    _implicit_constraint_inference,
    # Wave 4: Formal / Quantitative Reasoning
    _quantifier_scope_ambiguity,
    _process_simulation,
    _graph_path_existence,
    _set_membership_operations,
    _truth_table_evaluation,
]


def generate_tier2_battery(
    n_per_category: int = 2, seed: int | None = None
) -> list[dict]:
    """Generate Tier 2 battery only."""
    rng = random.Random(seed)
    traps: list[dict] = []
    for gen_fn in TIER2_GENERATORS:
        cat = gen_fn.__name__.lstrip("_")
        seen_prompts: set[str] = set()
        for _ in range(n_per_category * 5):  # oversample more for parametric variety
            if len([t for t in traps if t.get("category") == cat]) >= n_per_category:
                break
            trap = gen_fn(rng)
            if trap["prompt"] not in seen_prompts:
                seen_prompts.add(trap["prompt"])
                traps.append(trap)
    return traps


def generate_combined_battery(
    n_per_category: int = 2, seed: int | None = None
) -> list[dict]:
    """Combine Tier 1 (89 cats) + Tier 2 (24 cats) = 113 categories."""
    tier1 = generate_full_battery(n_per_category=n_per_category, seed=seed)
    tier2 = generate_tier2_battery(n_per_category=n_per_category, seed=seed)
    return tier1 + tier2


if __name__ == "__main__":
    battery = generate_tier2_battery(n_per_category=3, seed=42)
    print("=" * 72)
    print(f"Tier 2 battery: {len(battery)} traps")
    print("=" * 72)
    for t in battery:
        tier = t.get("tier", "?")
        print(f"[{t['category']:40s}] (tier {tier})")
        print(f"  prompt:     {t['prompt'][:80]}...")
        print(f"  candidates: {t['candidates']}")
        print(f"  correct:    {t['correct']}")
        print()

    cats = {}
    for t in battery:
        cats.setdefault(t["category"], 0)
        cats[t["category"]] += 1
    print("-" * 72)
    for cat, cnt in sorted(cats.items()):
        print(f"  {cat:40s} {cnt}")
    print(f"  {'TOTAL':40s} {len(battery)}")
