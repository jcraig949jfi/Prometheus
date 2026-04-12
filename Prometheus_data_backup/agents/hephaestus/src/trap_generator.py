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


# ---------------------------------------------------------------------------
# EXISTING GENERATORS (Phase 0) — tier A
# ---------------------------------------------------------------------------

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
            "tier": "A",
        }
    else:
        # Ask "is larger larger than smaller?" -> Yes
        return {
            "prompt": f"Is {larger} larger than {smaller}?",
            "candidates": ["Yes", "No"],
            "correct": "Yes",
            "category": "numeric_comparison",
            "tier": "A",
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
        "tier": "A",
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
        "tier": "A",
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
        "tier": "A",
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
        "tier": "A",
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
        "tier": "A",
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
        "tier": "A",
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
        "tier": "A",
    }


# ---------------------------------------------------------------------------
# PHASE 1 — Temporal + Probabilistic traps
# ---------------------------------------------------------------------------

def _temporal_ordering(rng: random.Random) -> dict:
    """'A happened before B, B before C. Did A happen before C?' Random chain 3-5."""
    first_names = [
        "Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace",
        "Hank", "Ivy", "Jake", "Kim", "Leo", "Mia", "Nina", "Oscar",
    ]
    chain_len = rng.randint(3, 5)
    names = rng.sample(first_names, chain_len)
    # names[0] happened first, names[-1] happened last

    verbs = [
        "arrived at the station",
        "finished the race",
        "left the building",
        "submitted the report",
        "crossed the finish line",
        "entered the room",
        "completed the task",
    ]
    verb = rng.choice(verbs)

    # Build premises: names[i] before names[i+1]
    premises = []
    for i in range(chain_len - 1):
        premises.append(f"{names[i]} {verb} before {names[i+1]}")
    rng.shuffle(premises)

    # Ask about a non-adjacent pair
    ask_first = rng.randint(0, chain_len - 3)
    ask_second = rng.randint(ask_first + 2, chain_len - 1)

    phrasing = rng.choice([
        f"Did {names[ask_first]} {verb.split()[0]} before {names[ask_second]}?",
        f"Is it true that {names[ask_first]} {verb} before {names[ask_second]}?",
    ])
    prompt = ". ".join(premises) + ". " + phrasing

    return {
        "prompt": prompt,
        "candidates": ["Yes", "No", "Cannot be determined"],
        "correct": "Yes",
        "category": "temporal_ordering",
        "tier": "A",
    }


def _parallel_vs_sequential(rng: random.Random) -> dict:
    """'Takes N min to do X. How long for M items in parallel?'"""
    tasks = [
        ("wash a car", "washing"),
        ("bake a cake", "baking"),
        ("print a document", "printing"),
        ("scan a part", "scanning"),
        ("paint a fence panel", "painting"),
        ("charge a battery", "charging"),
        ("run a test cycle", "running"),
    ]
    task_verb, task_gerund = rng.choice(tasks)
    time_per = rng.randint(5, 60)
    count = rng.randint(3, 10)
    units = rng.choice(["minutes", "hours"])

    sequential_answer = time_per * count
    parallel_answer = time_per

    mode = rng.choice(["parallel", "sequential"])
    if mode == "parallel":
        qualifier = rng.choice([
            f"all {count} at the same time",
            f"all {count} simultaneously",
            f"{count} of them in parallel",
        ])
        prompt = (
            f"It takes {time_per} {units} to {task_verb}. "
            f"If you are {task_gerund} {qualifier}, "
            f"how many {units} does it take?"
        )
        correct = str(parallel_answer)
        wrong = str(sequential_answer)
    else:
        qualifier = rng.choice([
            f"{count} of them one after another",
            f"{count} of them sequentially",
            f"{count} in a row, one at a time",
        ])
        prompt = (
            f"It takes {time_per} {units} to {task_verb}. "
            f"If you are {task_gerund} {qualifier}, "
            f"how many {units} does it take in total?"
        )
        correct = str(sequential_answer)
        wrong = str(parallel_answer)

    candidates = [correct, wrong]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "parallel_vs_sequential",
        "tier": "A",
    }


def _rate_inverse_proportion(rng: random.Random) -> dict:
    """'N workers finish in D days. How long for M workers?' answer=(N*D)/M."""
    occupations = ["workers", "painters", "bricklayers", "programmers",
                   "carpenters", "electricians", "plumbers"]
    tasks = ["build a wall", "paint a house", "finish the project",
             "dig a trench", "assemble the furniture", "wire the building"]
    occupation = rng.choice(occupations)
    task = rng.choice(tasks)

    n_workers = rng.randint(2, 12)
    days = rng.randint(2, 30)

    # Pick m_workers so that the answer divides evenly
    total_work = n_workers * days
    # Choose m_workers from divisors of total_work (excluding trivial)
    divisors = [d for d in range(2, total_work + 1) if total_work % d == 0 and d != n_workers]
    if not divisors:
        divisors = [n_workers * 2]
    m_workers = rng.choice(divisors[:10])
    answer = total_work // m_workers

    # Build wrong answers
    wrong1 = days  # ignoring the worker change
    wrong2 = m_workers * days  # multiplying instead of dividing
    wrongs = list({str(wrong1), str(wrong2)} - {str(answer)})
    candidates = [str(answer)] + wrongs[:2]
    while len(candidates) < 3:
        candidates.append(str(answer + rng.randint(1, 5)))
    rng.shuffle(candidates)

    prompt = (
        f"{n_workers} {occupation} can {task} in {days} days. "
        f"How many days would it take {m_workers} {occupation} to {task}?"
    )
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": str(answer),
        "category": "rate_inverse_proportion",
        "tier": "A",
    }


def _base_rate_neglect(rng: random.Random) -> dict:
    """Disease prevalence + test accuracy -> Bayesian posterior."""
    diseases = ["Zorplax syndrome", "condition Q7", "Malbeck disease",
                "syndrome R12", "viral strain V4", "factor-K deficiency"]
    disease = rng.choice(diseases)

    # Prevalence: 1 in N (keep N large for strong base-rate effect)
    prevalence_denom = rng.choice([100, 200, 500, 1000])
    # Sensitivity (true positive rate)
    sensitivity = rng.choice([90, 95, 99])
    # Specificity (true negative rate)
    specificity = rng.choice([90, 95, 99])

    # Bayes: P(disease|positive) = (sens * prev) / (sens*prev + (1-spec)*(1-prev))
    prev = 1.0 / prevalence_denom
    p_pos_given_disease = sensitivity / 100.0
    p_pos_given_no_disease = (100 - specificity) / 100.0

    numerator = p_pos_given_disease * prev
    denominator = numerator + p_pos_given_no_disease * (1 - prev)
    posterior = numerator / denominator
    posterior_pct = round(posterior * 100, 1)

    # Wrong answers people typically give
    naive_answer = sensitivity  # confusing sensitivity with posterior
    wrong1 = f"{naive_answer}%"
    wrong2 = f"{specificity}%"
    correct_str = f"{posterior_pct}%"

    candidates = [correct_str, wrong1, wrong2]
    # Add a fourth option
    alt = round(posterior_pct * rng.uniform(1.5, 3.0), 1)
    candidates.append(f"{alt}%")
    # Deduplicate
    candidates = list(dict.fromkeys(candidates))
    rng.shuffle(candidates)

    prompt = (
        f"{disease} affects 1 in {prevalence_denom} people. "
        f"A test has a {sensitivity}% true positive rate and a "
        f"{100 - specificity}% false positive rate. "
        f"If a person tests positive, what is the probability they actually "
        f"have {disease}?"
    )
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct_str,
        "category": "base_rate_neglect",
        "tier": "A",
    }


def _conjunction_fallacy(rng: random.Random) -> dict:
    """Description of person + 'which more likely: A or A-and-B?' correct=A."""
    profiles = [
        {
            "desc": "{name} is 31 years old, outspoken, and very bright. "
                    "{pronoun} majored in philosophy and was deeply concerned "
                    "with issues of social justice.",
            "option_a": "{name} is a bank teller",
            "option_b": "{name} is a bank teller and is active in the feminist movement",
        },
        {
            "desc": "{name} is quiet, meticulous, and enjoys solving puzzles. "
                    "{pronoun} studied mathematics in college.",
            "option_a": "{name} is an accountant",
            "option_b": "{name} is an accountant who plays competitive chess",
        },
        {
            "desc": "{name} loves the outdoors, goes hiking every weekend, "
                    "and volunteers at an animal shelter.",
            "option_a": "{name} is a software engineer",
            "option_b": "{name} is a software engineer and an environmental activist",
        },
        {
            "desc": "{name} is energetic, sociable, and was captain of the "
                    "debate team in college.",
            "option_a": "{name} works in sales",
            "option_b": "{name} works in sales and is a member of a political party",
        },
        {
            "desc": "{name} wears glasses, reads voraciously, and keeps a "
                    "meticulously organized desk.",
            "option_a": "{name} is a librarian",
            "option_b": "{name} is a librarian who writes poetry",
        },
    ]
    male_names = ["Tom", "James", "Carlos", "Raj", "Dmitri", "Kofi", "Liam"]
    female_names = ["Linda", "Sarah", "Mei", "Priya", "Amara", "Sofia", "Yuki"]

    if rng.random() < 0.5:
        name = rng.choice(male_names)
        pronoun = "He"
    else:
        name = rng.choice(female_names)
        pronoun = "She"

    profile = rng.choice(profiles)
    desc = profile["desc"].format(name=name, pronoun=pronoun)
    opt_a = profile["option_a"].format(name=name)
    opt_b = profile["option_b"].format(name=name)

    prompt = f"{desc} Which is more likely?"
    candidates = [opt_a, opt_b]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": opt_a,
        "category": "conjunction_fallacy",
        "tier": "A",
    }


def _conditional_probability_asymmetry(rng: random.Random) -> dict:
    """'X% of A are B. Is the probability a B is an A the same?' correct=No."""
    scenarios = [
        ("{pct}% of doctors are women", "Is the probability that a woman is a doctor also {pct}%?"),
        ("{pct}% of basketball players are over 6 feet tall", "Is the probability that someone over 6 feet is a basketball player also {pct}%?"),
        ("{pct}% of programmers use Linux", "Is the probability that a Linux user is a programmer also {pct}%?"),
        ("{pct}% of teachers have a master's degree", "Is the probability that someone with a master's degree is a teacher also {pct}%?"),
        ("{pct}% of chefs are left-handed", "Is the probability that a left-handed person is a chef also {pct}%?"),
        ("{pct}% of swimmers have blond hair", "Is the probability that a blond-haired person is a swimmer also {pct}%?"),
    ]
    pct = rng.randint(15, 85)
    premise_template, question_template = rng.choice(scenarios)
    premise = premise_template.format(pct=pct)
    question = question_template.format(pct=pct)

    prompt = f"{premise}. {question}"
    return {
        "prompt": prompt,
        "candidates": [
            "Yes, the probability is the same",
            "No, the probability is not necessarily the same",
        ],
        "correct": "No, the probability is not necessarily the same",
        "category": "conditional_probability_asymmetry",
        "tier": "A",
    }


def _expected_value(rng: random.Random) -> dict:
    """Two games with different probability/payoff. Compute EV."""
    # Game A: higher probability, lower payoff
    prob_a = rng.randint(40, 80)
    payoff_a = rng.randint(5, 30) * 10  # e.g. $50-$300
    ev_a = round(prob_a / 100 * payoff_a, 2)

    # Game B: lower probability, higher payoff (ensure different EV)
    prob_b = rng.randint(10, prob_a - 10)
    # Pick payoff_b so EVs differ
    payoff_b = rng.randint(payoff_a // 10 + 2, payoff_a // 10 + 15) * 10
    ev_b = round(prob_b / 100 * payoff_b, 2)

    # Make sure they're not equal
    while ev_a == ev_b:
        payoff_b += 10
        ev_b = round(prob_b / 100 * payoff_b, 2)

    if ev_a > ev_b:
        correct = f"Game A (EV=${ev_a})"
        wrong = f"Game B (EV=${ev_b})"
    else:
        correct = f"Game B (EV=${ev_b})"
        wrong = f"Game A (EV=${ev_a})"

    game_names = [("Game A", "Game B"), ("Option 1", "Option 2"),
                  ("Gamble X", "Gamble Y"), ("Bet Alpha", "Bet Beta")]
    name_a, name_b = rng.choice(game_names)

    prompt = (
        f"{name_a}: {prob_a}% chance of winning ${payoff_a}, otherwise $0. "
        f"{name_b}: {prob_b}% chance of winning ${payoff_b}, otherwise $0. "
        f"Which has the higher expected value?"
    )

    # Rewrite correct/wrong with chosen names
    if ev_a > ev_b:
        correct = f"{name_a} (EV=${ev_a})"
        wrong = f"{name_b} (EV=${ev_b})"
    else:
        correct = f"{name_b} (EV=${ev_b})"
        wrong = f"{name_a} (EV=${ev_a})"

    candidates = [correct, wrong, "They are equal"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "expected_value",
        "tier": "A",
    }


# ---------------------------------------------------------------------------
# PHASE 2 — Causal + Linguistic + Formal Logic traps
# ---------------------------------------------------------------------------

def _affirming_consequent(rng: random.Random) -> dict:
    """'If P then Q. Q is true. Is P true?' correct=Cannot determine."""
    scenarios = [
        ("it rains", "the streets are wet", "The streets are wet"),
        ("the alarm is triggered", "the siren sounds", "The siren is sounding"),
        ("he trained hard", "he won the match", "He won the match"),
        ("the power is on", "the light works", "The light works"),
        ("she studied all night", "she aced the exam", "She aced the exam"),
        ("the code compiles", "the tests pass", "The tests pass"),
        ("the oven is on", "the kitchen is warm", "The kitchen is warm"),
    ]
    p_str, q_str, q_observed = rng.choice(scenarios)

    prompt = f"If {p_str}, then {q_str}. {q_observed}. Can we conclude that {p_str}?"
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No", "Cannot be determined from the given information"],
        "correct": "Cannot be determined from the given information",
        "category": "affirming_consequent",
        "tier": "A",
    }


def _denying_antecedent(rng: random.Random) -> dict:
    """'If P then Q. Not P. Is Q true?' correct=Cannot determine."""
    scenarios = [
        ("she is a lawyer", "she studied law", "She is not a lawyer"),
        ("it snows", "the schools close", "It is not snowing"),
        ("he eats the cake", "he will feel full", "He did not eat the cake"),
        ("the battery is charged", "the phone turns on", "The battery is not charged"),
        ("you press the button", "the door opens", "You did not press the button"),
        ("the dog barks", "the cat hides", "The dog is not barking"),
    ]
    p_str, q_str, not_p_observed = rng.choice(scenarios)

    prompt = f"If {p_str}, then {q_str}. {not_p_observed}. Can we conclude anything about whether {q_str}?"
    return {
        "prompt": prompt,
        "candidates": [
            f"Yes, {q_str} is false",
            f"Yes, {q_str} is true",
            "No, we cannot determine whether " + q_str,
        ],
        "correct": "No, we cannot determine whether " + q_str,
        "category": "denying_antecedent",
        "tier": "A",
    }


def _double_negation(rng: random.Random) -> dict:
    """'It is not untrue that X. Is X true?' Vary depth 2-4 negations."""
    statements = [
        "the door is open",
        "the sky is blue",
        "cats are mammals",
        "water boils at 100 degrees Celsius",
        "the store is closed",
        "the project is complete",
        "she passed the test",
        "the bridge is safe",
    ]
    base = rng.choice(statements)
    depth = rng.randint(1, 2)  # number of double-negation wraps (2-4 total negations)

    # Even number of negations -> affirmative; odd -> negative
    # We always use pairs, so result = original
    neg_prefixes = [
        ("It is not untrue that", "It is not false that",
         "It is not the case that it is not true that"),
        ("It would be incorrect to say it is not the case that",
         "It is not the case that it is untrue that",
         "One cannot say it is false that"),
    ]

    sentence = base
    for i in range(depth):
        prefix = rng.choice(neg_prefixes[i % len(neg_prefixes)])
        sentence = f"{prefix} {sentence}"

    # depth double-negations = 2*depth negations = even = affirmative
    prompt = f"{sentence}. Is it true that {base}?"
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No", "Cannot be determined"],
        "correct": "Yes",
        "category": "double_negation",
        "tier": "A",
    }


def _demorgan(rng: random.Random) -> dict:
    """'Not (A and B)' => 'at least one is false.' Test understanding."""
    subjects = [
        ("Alice passed the exam", "Bob passed the exam"),
        ("the engine started", "the headlights turned on"),
        ("the proposal was approved", "the budget was allocated"),
        ("sensor A triggered", "sensor B triggered"),
        ("the cake rose properly", "the frosting set"),
        ("file X compiled", "file Y compiled"),
    ]
    a_str, b_str = rng.choice(subjects)

    phrasing = rng.choice([
        f"It is not the case that both {a_str} and {b_str}",
        f"It is false that {a_str} and {b_str} both occurred",
    ])

    correct_text = f"At least one of these is false: '{a_str}' or '{b_str}'"
    wrong1 = f"Both '{a_str}' and '{b_str}' are false"
    wrong2 = f"We cannot draw any conclusion"
    wrong3 = f"'{a_str}' is false but '{b_str}' might be true"

    prompt = f"{phrasing}. What can we conclude?"
    candidates = [correct_text, wrong1, wrong2, wrong3]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct_text,
        "category": "demorgan",
        "tier": "A",
    }


def _vacuous_truth(rng: random.Random) -> dict:
    """'If [impossible/false antecedent] then [anything].' correct=True."""
    false_antecedents = [
        "2 + 2 = 5",
        "the moon is made of cheese",
        "pigs can fly",
        "0 = 1",
        "all prime numbers are even",
        "water is dry",
        "the Earth is flat",
    ]
    consequents = [
        "then the sky is green",
        "then all dogs are cats",
        "then 1 + 1 = 3",
        "then I am the king of France",
        "then time flows backwards",
        "then triangles have four sides",
    ]
    antecedent = rng.choice(false_antecedents)
    consequent = rng.choice(consequents)

    prompt = (
        f'In classical logic, consider the statement: "If {antecedent}, '
        f'{consequent}." Is this statement logically true or false?'
    )
    return {
        "prompt": prompt,
        "candidates": [
            "True (the statement is vacuously true)",
            "False (the consequent is absurd)",
            "Neither true nor false",
            "Cannot be evaluated",
        ],
        "correct": "True (the statement is vacuously true)",
        "category": "vacuous_truth",
        "tier": "A",
    }


def _correlation_not_causation(rng: random.Random) -> dict:
    """'X and Y correlate. Does X cause Y?' correct=No."""
    scenarios = [
        ("ice cream sales", "drowning incidents", "summer months"),
        ("shoe size", "reading ability", "age"),
        ("number of firefighters at a fire", "damage from the fire", "fire severity"),
        ("per-capita cheese consumption", "number of civil engineering doctorates", "population growth"),
        ("hours of TV watched", "grades in school", "various confounders"),
        ("sunscreen sales", "sunburn frequency", "sun exposure"),
    ]
    x, y, confound = rng.choice(scenarios)

    prompt_templates = [
        f"Studies show a strong positive correlation between {x} and {y}. Can we conclude that {x} causes {y}?",
        f"Data reveals that {x} and {y} tend to rise and fall together. Does this mean {x} causes {y}?",
        f"There is a statistically significant correlation between {x} and {y}. Does {x} therefore cause {y}?",
    ]
    prompt = rng.choice(prompt_templates)
    return {
        "prompt": prompt,
        "candidates": [
            "Yes, the correlation demonstrates causation",
            "No, correlation does not imply causation",
            "Only if the p-value is below 0.05",
        ],
        "correct": "No, correlation does not imply causation",
        "category": "correlation_not_causation",
        "tier": "A",
    }


def _post_hoc(rng: random.Random) -> dict:
    """'A happened, then B happened. Did A cause B?' correct=No."""
    scenarios = [
        ("I wore my lucky socks", "our team won the game"),
        ("The rooster crowed", "the sun rose"),
        ("She took a vitamin", "her cold went away the next day"),
        ("He washed his car", "it rained that afternoon"),
        ("The city installed speed cameras", "crime rates fell"),
        ("I walked under a ladder", "I tripped on the sidewalk later"),
        ("The CEO changed the logo", "stock prices increased"),
    ]
    a_str, b_str = rng.choice(scenarios)

    prompt_templates = [
        f"{a_str}, and then {b_str}. Can we conclude that the first event caused the second?",
        f"First, {a_str.lower()}. Shortly after, {b_str.lower()}. Does the timing alone prove causation?",
        f"{a_str}. Afterwards, {b_str}. Is the fact that A preceded B sufficient to say A caused B?",
    ]
    prompt = rng.choice(prompt_templates)
    return {
        "prompt": prompt,
        "candidates": [
            "Yes, because A preceded B",
            "No, temporal sequence alone does not establish causation",
            "Yes, if it happened more than once",
        ],
        "correct": "No, temporal sequence alone does not establish causation",
        "category": "post_hoc",
        "tier": "A",
    }


def _necessary_vs_sufficient(rng: random.Random) -> dict:
    """'X is necessary for Y. X is present. Will Y happen?' correct=Not enough info."""
    scenarios = [
        ("oxygen", "a fire to burn"),
        ("a passport", "international travel"),
        ("electricity", "a computer to run"),
        ("water", "plant growth"),
        ("a driver's license", "legally driving a car"),
        ("sunlight", "photosynthesis"),
        ("fuel", "an engine to run"),
    ]
    necessary, outcome = rng.choice(scenarios)

    prompt_templates = [
        (f"{necessary.capitalize()} is necessary for {outcome}. "
         f"{necessary.capitalize()} is present. Will {outcome} definitely occur?"),
        (f"Without {necessary}, {outcome} cannot happen. "
         f"{necessary.capitalize()} is available. Does that guarantee {outcome}?"),
    ]
    prompt = rng.choice(prompt_templates)
    return {
        "prompt": prompt,
        "candidates": [
            "Yes, since the necessary condition is met",
            "No, a necessary condition being met does not guarantee the outcome",
            "It depends on the specific case",
        ],
        "correct": "No, a necessary condition being met does not guarantee the outcome",
        "category": "necessary_vs_sufficient",
        "tier": "A",
    }


def _scope_ambiguity(rng: random.Random) -> dict:
    """'Every X did a Y. Same Y?' correct=Not necessarily. tier=B."""
    scenarios = [
        ("student in the class", "read a book",
         "Did every student read the same book?"),
        ("employee", "attended a meeting",
         "Was it the same meeting for everyone?"),
        ("child at the party", "ate a slice of cake",
         "Did they all eat the same slice?"),
        ("runner in the marathon", "wore a pair of shoes",
         "Did they all wear the same pair of shoes?"),
        ("scientist on the team", "published a paper",
         "Did they all publish the same paper?"),
        ("guest at the wedding", "brought a gift",
         "Did they all bring the same gift?"),
    ]
    subject, action, question = rng.choice(scenarios)
    prompt = f"Every {subject} {action}. {question}"
    return {
        "prompt": prompt,
        "candidates": [
            "Yes, the sentence implies the same one",
            "Not necessarily; the sentence is ambiguous between each having their own and all sharing one",
            "No, they each had a different one",
        ],
        "correct": "Not necessarily; the sentence is ambiguous between each having their own and all sharing one",
        "category": "scope_ambiguity",
        "tier": "B",
    }


def _presupposition(rng: random.Random) -> dict:
    """'Have you stopped doing X?' correct=Question contains false presupposition. tier=B."""
    scenarios = [
        ("Have you stopped cheating on exams?", "cheating on exams"),
        ("Have you stopped stealing office supplies?", "stealing office supplies"),
        ("When did you stop lying to your friends?", "lying to your friends"),
        ("Have you quit skipping your workouts?", "skipping your workouts"),
        ("Why did you stop donating to charity?", "donating to charity"),
        ("Have you stopped eating junk food every day?", "eating junk food every day"),
    ]
    names = ["Alex", "Jordan", "Morgan", "Taylor", "Casey", "Riley", "Sam"]
    name = rng.choice(names)

    question_template, activity = rng.choice(scenarios)

    prompt = (
        f"Someone asks {name}: \"{question_template}\" "
        f"Assume {name} never engaged in {activity}. "
        f"Can {name} answer Yes or No without accepting a false premise?"
    )
    return {
        "prompt": prompt,
        "candidates": [
            "Yes, answering 'No' is safe",
            "Yes, answering 'Yes' is safe",
            "No, both Yes and No accept the false presupposition that they once did this",
        ],
        "correct": "No, both Yes and No accept the false presupposition that they once did this",
        "category": "presupposition",
        "tier": "B",
    }


def _pronoun_ambiguity(rng: random.Random) -> dict:
    """'John told Bill he was wrong. Who was wrong?' correct=Ambiguous. tier=B."""
    male_pairs = [
        ("John", "Bill"), ("Tom", "Jerry"), ("Carlos", "Miguel"),
        ("Ahmed", "Omar"), ("Liam", "Noah"), ("David", "Michael"),
    ]
    female_pairs = [
        ("Alice", "Beth"), ("Maria", "Sofia"), ("Yuki", "Hana"),
        ("Priya", "Ananya"), ("Emma", "Olivia"), ("Sarah", "Rachel"),
    ]

    if rng.random() < 0.5:
        name_a, name_b = rng.choice(male_pairs)
        pronoun = "he"
    else:
        name_a, name_b = rng.choice(female_pairs)
        pronoun = "she"

    verb_phrases = [
        (f"told {name_b} {pronoun} was wrong", "was wrong"),
        (f"said to {name_b} that {pronoun} was late", "was late"),
        (f"informed {name_b} that {pronoun} had made a mistake", "made the mistake"),
        (f"reminded {name_b} that {pronoun} needed to leave", "needed to leave"),
        (f"told {name_b} that {pronoun} was being unreasonable", "was being unreasonable"),
    ]
    verb_phrase, quality = rng.choice(verb_phrases)
    prompt = f"{name_a} {verb_phrase}. Who {quality}?"
    return {
        "prompt": prompt,
        "candidates": [
            name_a,
            name_b,
            f"It is ambiguous; '{pronoun}' could refer to either {name_a} or {name_b}",
        ],
        "correct": f"It is ambiguous; '{pronoun}' could refer to either {name_a} or {name_b}",
        "category": "pronoun_ambiguity",
        "tier": "B",
    }


def _percentage_change_asymmetry(rng: random.Random) -> dict:
    """'Up X% then down X%. Back to original?' correct=No, lower."""
    pct = rng.choice([10, 15, 20, 25, 30, 40, 50])
    items = ["a stock", "the price of a widget", "a house's value",
             "an investment", "a product's price", "a salary"]
    item = rng.choice(items)
    original = rng.choice([100, 200, 500, 1000])

    after_increase = original * (1 + pct / 100)
    after_decrease = after_increase * (1 - pct / 100)
    final = round(after_decrease, 2)

    prompt = (
        f"The value of {item} starts at ${original}. It increases by {pct}%, "
        f"then decreases by {pct}%. Is the final value back to ${original}?"
    )
    return {
        "prompt": prompt,
        "candidates": [
            f"Yes, it returns to ${original}",
            f"No, it is lower than ${original} (final value: ${final})",
            f"No, it is higher than ${original}",
        ],
        "correct": f"No, it is lower than ${original} (final value: ${final})",
        "category": "percentage_change_asymmetry",
        "tier": "A",
    }


def _garden_path(rng: random.Random) -> dict:
    """Temporarily ambiguous garden-path sentences. tier=B."""
    # Inventory of garden-path sentences with their correct parses
    inventory = [
        {
            "sentence": "The horse raced past the barn fell.",
            "question": "What fell?",
            "candidates": [
                "The barn",
                "The horse (that was raced past the barn)",
                "The sentence is ungrammatical",
                "Nothing fell",
            ],
            "correct": "The horse (that was raced past the barn)",
        },
        {
            "sentence": "The old man the boat.",
            "question": "Who mans the boat?",
            "candidates": [
                "An old man",
                "The old people (the old man the boat = the elderly crew the vessel)",
                "The sentence is ungrammatical",
                "No one",
            ],
            "correct": "The old people (the old man the boat = the elderly crew the vessel)",
        },
        {
            "sentence": "The complex houses married and single soldiers and their families.",
            "question": "What does 'the complex' refer to?",
            "candidates": [
                "Something complicated",
                "A housing complex (a building complex that houses soldiers)",
                "The sentence is ungrammatical",
                "A complex idea",
            ],
            "correct": "A housing complex (a building complex that houses soldiers)",
        },
        {
            "sentence": "Fat people eat accumulates.",
            "question": "What accumulates?",
            "candidates": [
                "People",
                "Fat (the fat that people eat accumulates in the body)",
                "The sentence is ungrammatical",
                "Food",
            ],
            "correct": "Fat (the fat that people eat accumulates in the body)",
        },
        {
            "sentence": "The cotton clothing is made of grows in Mississippi.",
            "question": "What grows in Mississippi?",
            "candidates": [
                "Clothing",
                "The cotton (that clothing is made of)",
                "The sentence is ungrammatical",
                "Mississippi grows everything",
            ],
            "correct": "The cotton (that clothing is made of)",
        },
        {
            "sentence": "Time flies like an arrow; fruit flies like a banana.",
            "question": "In the second clause, what does 'flies' mean?",
            "candidates": [
                "Moves quickly (same as first clause)",
                "The insects called fruit flies enjoy bananas",
                "The sentence is nonsensical",
                "Both interpretations are valid",
            ],
            "correct": "Both interpretations are valid",
        },
    ]

    item = rng.choice(inventory)
    prompt = f'Consider this sentence: "{item["sentence"]}" {item["question"]}'
    candidates = list(item["candidates"])
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": item["correct"],
        "category": "garden_path",
        "tier": "B",
    }


# ---------------------------------------------------------------------------
# Registry of generators
# ---------------------------------------------------------------------------
GENERATORS = [
    # Phase 0 — original
    _numeric_comparison,
    _numeric_which_larger,
    _transitivity_chain,
    _modus_tollens,
    _quantifier_inversion,
    _subject_object,
    _all_but_n,
    _negation_scope,
    # Phase 1 — temporal + probabilistic
    _temporal_ordering,
    _parallel_vs_sequential,
    _rate_inverse_proportion,
    _base_rate_neglect,
    _conjunction_fallacy,
    _conditional_probability_asymmetry,
    _expected_value,
    # Phase 2 — causal + linguistic + formal logic
    _affirming_consequent,
    _denying_antecedent,
    _double_negation,
    _demorgan,
    _vacuous_truth,
    _correlation_not_causation,
    _post_hoc,
    _necessary_vs_sufficient,
    _scope_ambiguity,
    _presupposition,
    _pronoun_ambiguity,
    _percentage_change_asymmetry,
    _garden_path,
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
        tier = t.get("tier", "?")
        print(f"[{t['category']:35s}] (tier {tier}) {t['prompt'][:70]}")
        print(f"  candidates={t['candidates']}")
        print(f"  correct={t['correct']}")
        print()
    print(f"Total: {len(battery)} traps across {len(GENERATORS)} generators")
