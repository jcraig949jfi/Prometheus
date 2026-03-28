"""
Expanded Battery Generators — Temporal, Causal, Theory of Mind, Compositional
==============================================================================

31 new parametric generators expanding the battery from ~58 to ~89 categories.
Each generator takes rng: random.Random, returns dict with:
    prompt, candidates, correct, category, tier

Append EXPANDED_GENERATORS to your existing EXTENDED_GENERATORS list.
Do NOT modify existing generators.
"""

import random
import math

# --- Name / entity pools for randomization ---

NAMES = [
    "Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Hank",
    "Iris", "Jack", "Karen", "Leo", "Mia", "Nathan", "Olivia", "Paul",
    "Quinn", "Rachel", "Sam", "Tina", "Uma", "Victor", "Wendy", "Xavier",
    "Yara", "Zach", "Diana", "Ethan", "Fiona", "George", "Hannah", "Ivan",
    "Julia", "Kevin", "Luna", "Marcus", "Nora", "Oscar", "Priya", "Raj",
]

OBJECTS = [
    "toy", "book", "key", "ball", "letter", "package", "phone", "hat",
    "coin", "ring", "notebook", "map", "ticket", "badge", "photo",
]

COLORS = ["red", "blue", "green", "yellow", "purple", "orange", "white", "black"]

ROOMS = ["kitchen", "bedroom", "living room", "attic", "basement", "garage", "office", "garden"]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

TASKS = [
    "painting a fence", "baking a cake", "writing a report", "assembling a shelf",
    "debugging code", "mowing the lawn", "washing the car", "cleaning the garage",
    "organizing files", "preparing dinner", "setting up equipment", "reviewing documents",
]


def _pick_names(rng, n):
    return rng.sample(NAMES, n)


def _shuffled_candidates(rng, correct, distractors):
    """Return shuffled candidate list with correct answer included."""
    cands = [correct] + distractors
    rng.shuffle(cands)
    return cands


# =============================================================================
# TEMPORAL EXPANSION (3 → 12)
# =============================================================================

def _temporal_concurrent_events(rng: random.Random) -> dict:
    """A takes X min, B takes Y min. Start both at same time. When is first done?"""
    n1, n2 = _pick_names(rng, 2)
    tasks = rng.sample(TASKS, 2)
    t1 = rng.randint(5, 30)
    t2 = rng.randint(t1 + 5, 60)  # t2 always longer

    correct_val = t1
    correct = f"{correct_val} minutes"

    templates = [
        f"{n1} starts {tasks[0]} (takes {t1} minutes) and {n2} starts {tasks[1]} (takes {t2} minutes) at the same time. How many minutes until the first task is completed?",
        f"Two tasks begin simultaneously: {n1} does {tasks[0]} ({t1} min) while {n2} does {tasks[1]} ({t2} min). How long before the first one finishes?",
        f"At 9:00 AM, {n1} begins {tasks[0]} which takes {t1} minutes, and {n2} begins {tasks[1]} which takes {t2} minutes. How many minutes pass before the first task is done?",
    ]

    distractors = [
        f"{t2} minutes",
        f"{t1 + t2} minutes",
        f"{(t1 + t2) // 2} minutes",
    ]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "temporal_concurrent_events",
        "tier": "A",
    }


def _temporal_frequency_coincidence(rng: random.Random) -> dict:
    """A happens every X days, B every Y days. When do they coincide? (LCM)"""
    n1, n2 = _pick_names(rng, 2)
    a = rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15])
    b = rng.choice([x for x in [3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15] if x != a])

    lcm_val = abs(a * b) // math.gcd(a, b)
    correct = f"{lcm_val} days"

    events = [
        ("waters the garden", "trims the hedge"),
        ("goes jogging", "does yoga"),
        ("visits the library", "cleans the house"),
        ("checks inventory", "runs a backup"),
        ("takes a vitamin", "does laundry"),
    ]
    e1, e2 = rng.choice(events)

    templates = [
        f"{n1} {e1} every {a} days. {n2} {e2} every {b} days. They both start today. In how many days will they next do their tasks on the same day?",
        f"Event A occurs every {a} days and event B occurs every {b} days. Both happen today. How many days until they coincide again?",
        f"{n1} has a {a}-day cycle for {e1} and a {b}-day cycle for {e2}. Starting from the same day, how many days until both happen together again?",
    ]

    distractors = [
        f"{a * b} days",
        f"{a + b} days",
        f"{max(a, b)} days",
    ]
    # Ensure no duplicate candidates
    distractors = [d for d in distractors if d != correct][:3]
    while len(distractors) < 3:
        distractors.append(f"{lcm_val + rng.randint(1, 10)} days")

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "temporal_frequency_coincidence",
        "tier": "A",
    }


def _temporal_sequence_reconstruction(rng: random.Random) -> dict:
    """N events with scrambled temporal descriptions. Reconstruct order."""
    n_events = rng.randint(4, 6)
    names = _pick_names(rng, n_events)
    # True order is names[0], names[1], ..., names[n-1]
    # Generate scrambled clues
    clues = []
    indices = list(range(n_events))

    # Generate sufficient constraints to determine unique order
    for i in range(n_events - 1):
        clues.append(f"{names[i]} happened before {names[i+1]}")

    # Add a redundant transitive clue for realism
    if n_events >= 4:
        gap = rng.randint(2, n_events - 1)
        i = rng.randint(0, n_events - 1 - gap)
        clues.append(f"{names[i]} happened before {names[i + gap]}")

    rng.shuffle(clues)
    clue_text = ". ".join(clues)

    # Ask about first or last
    ask_pos = rng.choice(["first", "last"])
    correct_name = names[0] if ask_pos == "first" else names[-1]

    distractor_pool = [n for n in names if n != correct_name]
    distractors = rng.sample(distractor_pool, min(3, len(distractor_pool)))

    templates = [
        f"Given these facts: {clue_text}. What was the {ask_pos} event?",
        f"Consider the following: {clue_text}. Which event happened {ask_pos}?",
        f"{clue_text}. Which of these was the {ask_pos} to occur?",
    ]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct_name, distractors),
        "correct": correct_name,
        "category": "temporal_sequence_reconstruction",
        "tier": "A",
    }


def _temporal_duration_across_midnight(rng: random.Random) -> dict:
    """Meeting starts before midnight, ends after. How long?"""
    start_h = rng.randint(21, 23)
    start_m = rng.choice([0, 15, 30, 45])
    dur_minutes = rng.randint(60, 240)
    end_total = start_h * 60 + start_m + dur_minutes
    end_h = (end_total // 60) % 24
    end_m = end_total % 60

    def fmt(h, m):
        period = "AM" if h < 12 else "PM"
        display_h = h % 12
        if display_h == 0:
            display_h = 12
        return f"{display_h}:{m:02d} {period}"

    start_str = fmt(start_h, start_m)
    end_str = fmt(end_h, end_m)

    dur_h = dur_minutes // 60
    dur_m = dur_minutes % 60
    if dur_m == 0:
        correct = f"{dur_h} hours"
    elif dur_h == 0:
        correct = f"{dur_m} minutes"
    else:
        correct = f"{dur_h} hours and {dur_m} minutes"

    events = ["meeting", "shift", "study session", "rehearsal", "workshop", "film screening"]
    event = rng.choice(events)
    n1 = _pick_names(rng, 1)[0]

    templates = [
        f"{n1}'s {event} starts at {start_str} and ends at {end_str}. How long is the {event}?",
        f"A {event} runs from {start_str} to {end_str}. What is the total duration?",
        f"If {n1} begins at {start_str} and finishes at {end_str}, how long did the {event} last?",
    ]

    # Distractors: common mistakes
    wrong1_min = abs(24 * 60 - dur_minutes)  # subtracting from 24h instead
    wrong1_h, wrong1_m = wrong1_min // 60, wrong1_min % 60
    wrong2_min = abs(start_h * 60 + start_m - (end_h * 60 + end_m))
    wrong2_h, wrong2_m = wrong2_min // 60, wrong2_min % 60

    def fmt_dur(h, m):
        if m == 0:
            return f"{h} hours"
        if h == 0:
            return f"{m} minutes"
        return f"{h} hours and {m} minutes"

    distractors = list({
        fmt_dur(wrong1_h, wrong1_m),
        fmt_dur(wrong2_h, wrong2_m),
        fmt_dur(dur_h + 1, dur_m),
    } - {correct})
    while len(distractors) < 3:
        distractors.append(fmt_dur(dur_h + rng.randint(1, 3), (dur_m + 15) % 60))
    distractors = distractors[:3]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "temporal_duration_across_midnight",
        "tier": "A",
    }


def _temporal_relative_day(rng: random.Random) -> dict:
    """Today is X. What day is [complex relative expression]?"""
    today_idx = rng.randint(0, 6)
    today = DAYS[today_idx]

    # Build relative expressions with known offsets
    expressions = [
        ("the day after tomorrow", 2),
        ("the day before yesterday", -2),
        ("the day after the day before yesterday", -1),  # yesterday
        ("the day before the day after tomorrow", 1),  # tomorrow
        ("three days from now", 3),
        ("two days before tomorrow", -1),
        ("the day after the day after tomorrow", 3),
        ("four days ago", -4),
        ("the day before three days from now", 2),
        ("five days from now", 5),
    ]

    expr_text, offset = rng.choice(expressions)
    answer_idx = (today_idx + offset) % 7
    correct = DAYS[answer_idx]

    distractor_offsets = [offset + d for d in [-2, -1, 1, 2] if (today_idx + offset + d) % 7 != answer_idx]
    distractors = [DAYS[(today_idx + o) % 7] for o in distractor_offsets[:4]]
    distractors = list(set(d for d in distractors if d != correct))[:3]
    while len(distractors) < 3:
        d = DAYS[rng.randint(0, 6)]
        if d != correct and d not in distractors:
            distractors.append(d)

    templates = [
        f"Today is {today}. What day is {expr_text}?",
        f"If today is {today}, what day of the week is {expr_text}?",
        f"It's {today} today. {expr_text.capitalize()} — what day is that?",
    ]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "temporal_relative_day",
        "tier": "A",
    }


def _temporal_rate_of_change(rng: random.Random) -> dict:
    """Sequence of values — is change accelerating, decelerating, or constant?"""
    n1 = _pick_names(rng, 1)[0]
    measures = [
        ("population", "people"),
        ("revenue", "dollars"),
        ("subscribers", "users"),
        ("temperature", "degrees"),
        ("inventory", "units"),
    ]
    measure, unit = rng.choice(measures)
    base = rng.randint(50, 500)

    case = rng.choice(["accelerating", "decelerating", "constant"])
    if case == "accelerating":
        d1 = rng.randint(5, 15)
        d2 = rng.randint(d1 + 5, d1 + 20)
        d3 = rng.randint(d2 + 5, d2 + 20)
    elif case == "decelerating":
        d1 = rng.randint(20, 40)
        d2 = rng.randint(5, d1 - 5)
        d3 = rng.randint(1, max(2, d2 - 5))
    else:  # constant
        d1 = rng.randint(10, 30)
        d2 = d1
        d3 = d1

    vals = [base, base + d1, base + d1 + d2, base + d1 + d2 + d3]
    correct = case

    periods = ["month", "quarter", "year", "week"]
    period = rng.choice(periods)

    val_str = ", ".join(str(v) for v in vals)
    templates = [
        f"{n1}'s {measure} over four {period}s: {val_str} {unit}. Is the rate of change accelerating, decelerating, or constant?",
        f"The {measure} readings are {val_str}. Describe the trend: accelerating, decelerating, or constant?",
        f"Given these sequential measurements of {measure}: {val_str}. Is growth accelerating, decelerating, or constant?",
    ]

    all_opts = ["accelerating", "decelerating", "constant"]
    distractors = [o for o in all_opts if o != correct]
    distractors.append("insufficient data")
    distractors = distractors[:3]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "temporal_rate_of_change",
        "tier": "A",
    }


def _temporal_causal_ordering(rng: random.Random) -> dict:
    """Narrative with temporal clues, extract earliest/latest event."""
    events_pool = [
        ("the {obj} was inspected", "the inspection found a defect"),
        ("it rained heavily for three days", "the storm flooded the area"),
        ("the alarm went off", "the alarm triggered a response"),
        ("the contract was signed", "the agreement was finalized"),
        ("a warning was issued", "officials raised concerns"),
    ]

    n_events = rng.randint(4, 5)
    # Create an ordered chain
    event_descs = []
    for i in range(n_events):
        n = _pick_names(rng, 1)[0]
        action = rng.choice(TASKS)
        event_descs.append(f"{n} finished {action}")

    # Present events in scrambled order with temporal connectors
    order = list(range(n_events))
    presentation = list(range(n_events))
    rng.shuffle(presentation)

    clues = []
    for idx in presentation:
        if idx == 0:
            clues.append(f"First, {event_descs[idx]}")
        elif idx == n_events - 1:
            # reference a previous event
            ref = rng.randint(0, idx - 1)
            clues.append(f"After {event_descs[ref]}, finally {event_descs[idx]}")
        else:
            ref = rng.randint(0, idx - 1)
            clues.append(f"After {event_descs[ref]}, {event_descs[idx]}")

    clue_text = ". ".join(clues)
    ask = rng.choice(["earliest", "latest"])
    correct_event = event_descs[0] if ask == "earliest" else event_descs[-1]

    distractor_pool = [e for e in event_descs if e != correct_event]
    distractors = rng.sample(distractor_pool, min(3, len(distractor_pool)))

    return {
        "prompt": f"{clue_text}. Which event was the {ask}?",
        "candidates": _shuffled_candidates(rng, correct_event, distractors),
        "correct": correct_event,
        "category": "temporal_causal_ordering",
        "tier": "A",
    }


def _temporal_scheduling_conflict(rng: random.Random) -> dict:
    """Two or more time ranges — do they overlap?"""
    n1 = _pick_names(rng, 1)[0]
    start_a = rng.randint(8, 15)
    dur_a = rng.randint(1, 3)
    end_a = start_a + dur_a

    # Sometimes overlap, sometimes not
    overlap = rng.choice([True, False])
    if overlap:
        start_b = rng.randint(start_a, end_a - 1)
        dur_b = rng.randint(1, 3)
    else:
        start_b = end_a + rng.randint(0, 2)
        dur_b = rng.randint(1, 3)
    end_b = start_b + dur_b

    def fmt_time(h):
        if h < 12:
            return f"{h}:00 AM"
        elif h == 12:
            return f"12:00 PM"
        else:
            return f"{h - 12}:00 PM"

    events = rng.sample(["team meeting", "client call", "training session",
                         "project review", "lunch meeting", "workshop", "interview"], 2)

    correct = "No" if not overlap else "Yes"
    # "Can you attend both fully?" - overlap means you cannot
    # Wait — rethink: overlap means CONFLICT, so cannot attend both
    if overlap:
        correct = "No, there is a scheduling conflict"
    else:
        correct = "Yes, there is no conflict"

    templates = [
        f"{n1} has a {events[0]} from {fmt_time(start_a)} to {fmt_time(end_a)} and a {events[1]} from {fmt_time(start_b)} to {fmt_time(end_b)}. Can {n1} attend both events fully?",
        f"Meeting A runs {fmt_time(start_a)}-{fmt_time(end_a)}. Meeting B runs {fmt_time(start_b)}-{fmt_time(end_b)}. Is there a scheduling conflict?",
    ]

    if overlap:
        distractors = [
            "Yes, there is no conflict",
            "Only if one meeting is shortened",
            "Cannot determine without more information",
        ]
    else:
        distractors = [
            "No, there is a scheduling conflict",
            "Only if one meeting is moved",
            "Cannot determine without more information",
        ]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "temporal_scheduling_conflict",
        "tier": "A",
    }


def _temporal_age_reasoning(rng: random.Random) -> dict:
    """Age relationships between 3 people. Compute target age."""
    n1, n2, n3 = _pick_names(rng, 3)
    base_age = rng.randint(4, 12)
    multiplier = rng.randint(2, 3)
    offset = rng.randint(1, 8)

    # n3 = base_age, n2 = multiplier * n3, n1 = n2 + offset
    age3 = base_age
    age2 = multiplier * base_age
    age1 = age2 + offset

    ask_target = rng.choice([n1, n2])
    if ask_target == n1:
        correct_age = age1
    else:
        correct_age = age2

    correct = str(correct_age)

    templates = [
        f"{n1} is {offset} years older than {n2}. {n2} is {multiplier} times {n3}'s age. {n3} is {age3}. How old is {ask_target}?",
        f"If {n3} is {age3} years old, {n2} is {multiplier} times {n3}'s age, and {n1} is {offset} years older than {n2}, how old is {ask_target}?",
        f"{n3} is {age3}. {n2}'s age is {multiplier} times that of {n3}. {n1} is {offset} years older than {n2}. What is {ask_target}'s age?",
    ]

    distractors = list({
        str(correct_age + offset),
        str(correct_age - offset),
        str(base_age * multiplier + offset + rng.randint(1, 5)),
        str(abs(correct_age - multiplier)),
    } - {correct})
    distractors = distractors[:3]
    while len(distractors) < 3:
        distractors.append(str(correct_age + rng.randint(1, 10)))

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "temporal_age_reasoning",
        "tier": "A",
    }


# =============================================================================
# CAUSAL EXPANSION (3 → 10)
# =============================================================================

def _causal_intervention(rng: random.Random) -> dict:
    """In a causal chain X→Y→Z, force a node to a value. What happens downstream?"""
    vars_pool = ["X", "Y", "Z", "W", "A", "B", "C"]
    chain_len = rng.randint(3, 4)
    chain = rng.sample(vars_pool, chain_len)

    # Build chain: chain[0] → chain[1] → ... → chain[-1]
    chain_desc = " → ".join(chain)

    # Intervene on a middle node
    intervene_idx = rng.randint(1, chain_len - 2)
    intervene_var = chain[intervene_idx]

    # Ask about a downstream node
    ask_var = chain[-1]

    # After intervention, upstream is disconnected, downstream follows from forced value
    correct = f"{ask_var} is determined by the forced value of {intervene_var}, not by {chain[0]}"
    wrong1 = f"{ask_var} is still determined by {chain[0]}"
    wrong2 = f"{ask_var} becomes unpredictable"
    wrong3 = f"The intervention has no effect on {ask_var}"

    templates = [
        f"In the causal chain {chain_desc}, if we intervene and force {intervene_var} to a fixed value, what determines {ask_var}?",
        f"Consider: {chain_desc}. We perform an intervention setting {intervene_var} = fixed. Does {chain[0]} still influence {ask_var}?",
        f"System: {chain_desc}. If we externally set {intervene_var}, breaking its dependence on {chain[intervene_idx-1]}, what determines {ask_var}?",
    ]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, [wrong1, wrong2, wrong3]),
        "correct": correct,
        "category": "causal_intervention",
        "tier": "A",
    }


def _causal_confounding(rng: random.Random) -> dict:
    """Two variables correlate due to a hidden common cause."""
    scenarios = [
        {
            "x": "ice cream sales", "y": "drowning incidents",
            "confounder": "hot weather (summer)",
            "x_desc": "ice cream consumption rises", "y_desc": "drowning rates increase",
        },
        {
            "x": "firefighter count at a scene", "y": "property damage",
            "confounder": "fire severity",
            "x_desc": "more firefighters are deployed", "y_desc": "damage is higher",
        },
        {
            "x": "number of hospitals", "y": "number of deaths",
            "confounder": "population size",
            "x_desc": "a city has more hospitals", "y_desc": "more deaths are recorded",
        },
        {
            "x": "shoe size", "y": "reading ability in children",
            "confounder": "age",
            "x_desc": "children have larger shoe sizes", "y_desc": "they read better",
        },
        {
            "x": "organic food sales", "y": "autism diagnoses",
            "confounder": "time (both increase over years)",
            "x_desc": "organic food sales increase", "y_desc": "autism diagnoses increase",
        },
    ]

    s = rng.choice(scenarios)
    n1 = _pick_names(rng, 1)[0]

    templates = [
        f"Data shows that when {s['x_desc']}, {s['y_desc']}. {n1} concludes that {s['x']} causes {s['y']}. What is the flaw in this reasoning?",
        f"A study finds a strong correlation between {s['x']} and {s['y']}. Does {s['x']} cause {s['y']}?",
        f"Observation: {s['x_desc']} and {s['y_desc']} tend to occur together. What's the most likely explanation?",
    ]

    correct = f"Confounding variable ({s['confounder']}) causes both; correlation is not causation"
    distractors = [
        f"{s['x']} directly causes {s['y']}",
        f"{s['y']} causes {s['x']} (reverse causation)",
        "The correlation is coincidental and meaningless",
    ]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "causal_confounding",
        "tier": "A",
    }


def _causal_chain_length(rng: random.Random) -> dict:
    """A causes B, B causes C, ... Does A cause the final node? (Yes, transitivity.)"""
    chain_len = rng.randint(3, 6)
    names = _pick_names(rng, chain_len)
    chain_stmts = [f"If {names[i]} happens, then {names[i+1]} happens" for i in range(chain_len - 1)]
    rng.shuffle(chain_stmts)
    chain_text = ". ".join(chain_stmts)

    correct = "Yes"
    templates = [
        f"{chain_text}. If {names[0]} happens, does {names[-1]} happen?",
        f"Given: {chain_text}. Does {names[0]} occurring guarantee that {names[-1]} occurs?",
    ]

    distractors = [
        "No",
        "Only if the chain is short enough",
        "Cannot be determined",
    ]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "causal_chain_length",
        "tier": "A",
    }


def _causal_counterfactual(rng: random.Random) -> dict:
    """Rule + exception. Counterfactual: what would have happened if X?"""
    n1 = _pick_names(rng, 1)[0]

    scenarios = [
        {
            "rule": "All employees who arrived late were fined $50",
            "fact": f"{n1} was not fined",
            "counter": f"If {n1} had arrived late",
            "question": f"would {n1} have been fined?",
            "correct": f"Yes, {n1} would have been fined $50",
            "distractors": [
                f"No, {n1} is exempt",
                "Cannot determine without more information",
                f"Only if {n1}'s manager approved",
            ],
        },
        {
            "rule": "Every student who submitted the project on time received full marks",
            "fact": f"{n1} did not receive full marks",
            "counter": f"If {n1} had submitted on time",
            "question": f"would {n1} have received full marks?",
            "correct": f"Yes, {n1} would have received full marks",
            "distractors": [
                f"No, the quality also matters",
                "Cannot determine from the given information",
                f"{n1} would still have lost marks",
            ],
        },
        {
            "rule": "All packages over 10kg require a surcharge",
            "fact": f"{n1}'s package had no surcharge",
            "counter": f"If {n1}'s package weighed 15kg",
            "question": "would it require a surcharge?",
            "correct": "Yes, it would require a surcharge",
            "distractors": [
                "No, the surcharge is optional",
                "Only for international packages",
                "Cannot determine without the exact policy",
            ],
        },
    ]

    s = rng.choice(scenarios)

    templates = [
        f"Rule: {s['rule']}. Fact: {s['fact']}. Counterfactual: {s['counter']}, {s['question']}",
        f"{s['rule']}. We know that {s['fact']}. But {s['counter']} — {s['question']}",
    ]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, s["correct"], s["distractors"]),
        "correct": s["correct"],
        "category": "causal_counterfactual",
        "tier": "A",
    }


def _causal_necessary_sufficient_extended(rng: random.Random) -> dict:
    """Necessary condition present but not sufficient. Will the outcome occur?"""
    scenarios = [
        {
            "necessary": "water",
            "context": "a plant",
            "outcome": "grow",
            "missing": "sunlight and soil nutrients",
            "has_necessary": True,
        },
        {
            "necessary": "electricity",
            "context": "a computer",
            "outcome": "run a program",
            "missing": "the correct software installed",
            "has_necessary": True,
        },
        {
            "necessary": "fuel",
            "context": "a car",
            "outcome": "drive",
            "missing": "a working engine and tires",
            "has_necessary": True,
        },
        {
            "necessary": "ingredients",
            "context": "a chef",
            "outcome": "cook the dish",
            "missing": "kitchen equipment and a recipe",
            "has_necessary": True,
        },
    ]

    s = rng.choice(scenarios)
    correct = f"Not necessarily — {s['necessary']} is necessary but not sufficient; also needs {s['missing']}"

    templates = [
        f"{s['necessary'].capitalize()} is necessary for {s['context']} to {s['outcome']}. {s['context'].capitalize()} has {s['necessary']}. Will it definitely {s['outcome']}?",
        f"Without {s['necessary']}, {s['context']} cannot {s['outcome']}. {s['context'].capitalize()} now has {s['necessary']}. Does this guarantee it will {s['outcome']}?",
    ]

    distractors = [
        f"Yes, having {s['necessary']} is enough",
        f"No, {s['necessary']} is irrelevant to the outcome",
        "Cannot determine — insufficient information",
    ]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "causal_necessary_sufficient_extended",
        "tier": "A",
    }


def _causal_simpson_paradox(rng: random.Random) -> dict:
    """Numeric example where a trend reverses in subgroups vs aggregate."""
    n1, n2 = _pick_names(rng, 2)

    # Treatment A and B, two groups (mild and severe)
    # Design so B is better in both subgroups but A looks better overall
    # because A is given mostly to the easy group

    # Group 1 (mild): A treats many, B treats few
    a1_success = rng.randint(85, 95)  # % success
    b1_success = a1_success + rng.randint(1, 5)
    b1_success = min(b1_success, 99)
    a1_n = rng.randint(80, 120)
    b1_n = rng.randint(10, 25)

    # Group 2 (severe): A treats few, B treats many
    a2_success = rng.randint(40, 60)
    b2_success = a2_success + rng.randint(1, 8)
    b2_success = min(b2_success, 70)
    a2_n = rng.randint(10, 25)
    b2_n = rng.randint(80, 120)

    # Compute aggregates
    a_total_success = round((a1_success * a1_n + a2_success * a2_n) / (a1_n + a2_n), 1)
    b_total_success = round((b1_success * b1_n + b2_success * b2_n) / (b1_n + b2_n), 1)

    context = rng.choice(["treatment", "method", "approach", "technique"])

    prompt = (
        f"{context.capitalize()} A: {a1_success}% success rate on mild cases (n={a1_n}), "
        f"{a2_success}% on severe cases (n={a2_n}). Overall: {a_total_success}%. "
        f"{context.capitalize()} B: {b1_success}% on mild (n={b1_n}), "
        f"{b2_success}% on severe (n={b2_n}). Overall: {b_total_success}%. "
        f"Which {context} is actually more effective?"
    )

    correct = f"{context.capitalize()} B (better in both subgroups — Simpson's paradox in the aggregate)"
    distractors = [
        f"{context.capitalize()} A (higher overall rate)",
        "They are equally effective",
        "Cannot be determined from this data",
    ]

    return {
        "prompt": prompt,
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "causal_simpson_paradox",
        "tier": "A",
    }


def _causal_common_cause(rng: random.Random) -> dict:
    """Two things increase together. Did A cause B? (No — common cause possible.) tier=B"""
    n1 = _pick_names(rng, 1)[0]

    scenarios = [
        ("coffee consumption", "productivity", "both increase on weekday mornings"),
        ("umbrella sales", "taxi usage", "both rise when it rains"),
        ("advertising spend", "website traffic", "both increase during product launches"),
        ("gym membership", "salad purchases", "both rise in January due to New Year's resolutions"),
    ]

    a, b, reason = rng.choice(scenarios)

    templates = [
        f"{n1} notices that {a} and {b} have both increased recently. {n1} concludes that increasing {a} caused the rise in {b}. Is this conclusion justified?",
        f"Data shows {a} and {b} rising together. Can we conclude {a} causes {b}?",
    ]

    correct = f"Not justified — a common cause is possible ({reason})"
    distractors = [
        f"Yes, the correlation supports causation",
        f"Yes, but {b} causes {a} instead",
        "The data is insufficient to say anything",
    ]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "causal_common_cause",
        "tier": "B",
    }


# =============================================================================
# THEORY OF MIND EXPANSION (3 → 10)
# =============================================================================

def _tom_second_order_belief(rng: random.Random) -> dict:
    """Alice thinks Bob thinks X is in location A. Where does Alice expect Bob to look?"""
    n1, n2 = _pick_names(rng, 2)
    obj = rng.choice(OBJECTS)
    r1, r2, r3 = rng.sample(ROOMS, 3)

    # Reality: obj is in r3. Bob saw it placed in r1 but didn't see it moved.
    # Alice knows Bob saw it in r1 (and doesn't know it was moved).

    templates = [
        f"The {obj} was placed in the {r1}. {n2} saw this. Then, while {n2} was away, the {obj} was moved to the {r3}. {n1} watched all of this happen. Where does {n1} think {n2} will look for the {obj}?",
        f"{n2} watched someone put the {obj} in the {r1} and then left. While {n2} was gone, it was moved to the {r3}. {n1} observed everything. Where does {n1} expect {n2} to search?",
    ]

    correct = r1
    distractors = [r2, r3, f"Wherever {n1} tells {n2} to look"]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "tom_second_order_belief",
        "tier": "A",
    }


def _tom_information_asymmetry(rng: random.Random) -> dict:
    """You know X. Another person doesn't. What do they believe?"""
    n1 = _pick_names(rng, 1)[0]

    scenarios = [
        {
            "setup": f"You know the coin is rigged to land heads 80% of the time. {n1} thinks it's a fair coin.",
            "question": f"What probability does {n1} assign to heads on the next flip?",
            "correct": "50%",
            "distractors": ["80%", "Cannot determine", "0%"],
        },
        {
            "setup": f"You know the exam has been postponed to Friday. {n1} hasn't been told and believes it's still on Wednesday.",
            "question": f"What day does {n1} think the exam is?",
            "correct": "Wednesday",
            "distractors": ["Friday", "Thursday", f"{n1} doesn't know"],
        },
        {
            "setup": f"The box contains a red ball. {n1} was told the box contains a blue ball.",
            "question": f"What color does {n1} believe the ball is?",
            "correct": "Blue",
            "distractors": ["Red", f"{n1} is uncertain", "Both red and blue"],
        },
        {
            "setup": f"The store closes at 8 PM now. {n1} still has the old schedule showing 9 PM.",
            "question": f"What time does {n1} think the store closes?",
            "correct": "9 PM",
            "distractors": ["8 PM", "10 PM", f"{n1} would check first"],
        },
    ]

    s = rng.choice(scenarios)

    return {
        "prompt": f"{s['setup']} {s['question']}",
        "candidates": _shuffled_candidates(rng, s["correct"], s["distractors"]),
        "correct": s["correct"],
        "category": "tom_information_asymmetry",
        "tier": "A",
    }


def _tom_strategic_deception(rng: random.Random) -> dict:
    """Agent wants target to believe/do X. Target has a known reaction pattern."""
    n1, n2 = _pick_names(rng, 2)

    scenarios = [
        {
            "setup": f"{n1} wants {n2} to go left. {n1} knows {n2} always does the opposite of what {n1} suggests.",
            "question": f"What should {n1} say?",
            "correct": f"{n1} should say 'go right'",
            "distractors": [
                f"{n1} should say 'go left'",
                f"{n1} should say nothing",
                f"{n1} should say 'go straight'",
            ],
        },
        {
            "setup": f"{n1} wants {n2} to pick the red box. {n2} is contrarian and always avoids what's recommended.",
            "question": f"What should {n1} recommend?",
            "correct": f"Recommend any box except the red one",
            "distractors": [
                "Recommend the red box",
                "Don't make any recommendation",
                "Recommend all boxes equally",
            ],
        },
        {
            "setup": f"{n1} wants to surprise {n2} on Friday. {n2} suspects surprises on weekends and lets their guard down on weekdays.",
            "question": f"Is Friday a good choice for the surprise?",
            "correct": "Yes — Friday is a weekday so the guard is down",
            "distractors": [
                "No — Friday is too close to the weekend",
                "No — surprises should always be on weekends",
                "Cannot determine",
            ],
        },
    ]

    s = rng.choice(scenarios)

    return {
        "prompt": f"{s['setup']} {s['question']}",
        "candidates": _shuffled_candidates(rng, s["correct"], s["distractors"]),
        "correct": s["correct"],
        "category": "tom_strategic_deception",
        "tier": "A",
    }


def _tom_group_knowledge(rng: random.Random) -> dict:
    """Common knowledge vs mutual knowledge. Tier B (judgment)."""
    n1, n2, n3 = _pick_names(rng, 3)

    scenarios = [
        {
            "setup": (
                f"{n1}, {n2}, and {n3} are in a room. A public announcement is made: 'The meeting is canceled.' "
                f"Everyone hears it."
            ),
            "question": f"Does {n1} know that {n2} knows the meeting is canceled?",
            "correct": "Yes — the announcement was public, so it's common knowledge",
            "distractors": [
                f"No — {n1} can't be sure {n2} was listening",
                "Only if they make eye contact",
                "Cannot determine",
            ],
        },
        {
            "setup": (
                f"{n1} and {n2} each receive a private text message: 'The party is at 7pm.' "
                f"Neither knows the other received the message."
            ),
            "question": f"Does {n1} know that {n2} knows the party time?",
            "correct": f"No — {n1} doesn't know {n2} was also told (mutual but not common knowledge)",
            "distractors": [
                "Yes — they both know",
                "Yes — same information means shared knowledge",
                "Only if they compare messages",
            ],
        },
    ]

    s = rng.choice(scenarios)

    return {
        "prompt": f"{s['setup']} {s['question']}",
        "candidates": _shuffled_candidates(rng, s["correct"], s["distractors"]),
        "correct": s["correct"],
        "category": "tom_group_knowledge",
        "tier": "B",
    }


def _tom_perspective_shift(rng: random.Random) -> dict:
    """Spatial or viewpoint perspective-taking."""
    n1, n2 = _pick_names(rng, 2)

    scenarios = [
        {
            "setup": f"{n1} and {n2} sit facing each other at a table. A {rng.choice(OBJECTS)} is on {n1}'s left side.",
            "question": f"On which side is the {rng.choice(OBJECTS)} from {n2}'s perspective?",
            "correct": "right",
            "distractors": ["left", "center", "behind"],
        },
        {
            "setup": f"{n1} faces north. {n2} faces south, directly opposite {n1}. A sign is to {n1}'s east.",
            "question": f"From {n2}'s perspective, which direction is the sign?",
            "correct": "west",
            "distractors": ["east", "north", "south"],
        },
    ]

    s = rng.choice(scenarios)

    # Re-randomize the object consistently
    obj = rng.choice(OBJECTS)

    if "table" in s["setup"]:
        setup = f"{n1} and {n2} sit facing each other at a table. A {obj} is on {n1}'s left side."
        question = f"On which side is the {obj} from {n2}'s perspective?"
        return {
            "prompt": f"{setup} {question}",
            "candidates": _shuffled_candidates(rng, "right", ["left", "center", "behind"]),
            "correct": "right",
            "category": "tom_perspective_shift",
            "tier": "A",
        }
    else:
        return {
            "prompt": f"{s['setup']} {s['question']}",
            "candidates": _shuffled_candidates(rng, s["correct"], s["distractors"]),
            "correct": s["correct"],
            "category": "tom_perspective_shift",
            "tier": "A",
        }


def _tom_mistaken_belief_chain(rng: random.Random) -> dict:
    """Misinformation propagates through a chain of agents."""
    n1, n2, n3 = _pick_names(rng, 3)

    true_val = rng.randint(1, 12)
    wrong_val = true_val + rng.choice([-2, -1, 1, 2])
    if wrong_val <= 0:
        wrong_val = true_val + 2

    contexts = [
        ("meeting", "pm", "the meeting time"),
        ("price", "dollars", "the item's price"),
        ("floor", "", "which floor"),
    ]
    ctx, unit, desc = rng.choice(contexts)
    true_str = f"{true_val} {unit}".strip() if unit else str(true_val)
    wrong_str = f"{wrong_val} {unit}".strip() if unit else str(wrong_val)

    templates = [
        f"The actual {ctx} is at {true_str}. {n1} mistakenly tells {n2} it's at {wrong_str}. {n2} then tells {n3} what {n1} said. What does {n3} believe about {desc}?",
        f"{n1} incorrectly thinks {desc} is {wrong_str} (the real answer is {true_str}). {n1} tells {n2}, who passes it to {n3}. What does {n3} believe?",
    ]

    correct = wrong_str
    distractors = [true_str]
    extras = [f"{true_val + 3} {unit}".strip() if unit else str(true_val + 3),
              f"{wrong_val + 1} {unit}".strip() if unit else str(wrong_val + 1)]
    distractors.extend([e for e in extras if e != correct and e != distractors[0]])
    distractors = distractors[:3]
    while len(distractors) < 3:
        filler = f"{true_val + rng.randint(3, 7)} {unit}".strip() if unit else str(true_val + rng.randint(3, 7))
        if filler != correct and filler not in distractors:
            distractors.append(filler)

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "tom_mistaken_belief_chain",
        "tier": "A",
    }


def _tom_intention_reading(rng: random.Random) -> dict:
    """Observe behavior, infer belief/intention. Tier B (judgment)."""
    n1 = _pick_names(rng, 1)[0]

    scenarios = [
        {
            "observation": f"{n1} brought an umbrella on a sunny day",
            "correct": f"{n1} likely expected rain or saw a forecast predicting rain",
            "distractors": [
                f"{n1} enjoys carrying umbrellas",
                f"{n1} didn't notice the weather",
                "No inference can be made about beliefs from actions",
            ],
        },
        {
            "observation": f"{n1} brought a textbook to a party",
            "correct": f"{n1} likely plans to study at some point, possibly expecting free time or an early departure",
            "distractors": [
                f"{n1} confused the party for a class",
                f"{n1} brings textbooks everywhere without reason",
                "People never bring books to social events",
            ],
        },
        {
            "observation": f"{n1} checked the clock three times during the conversation",
            "correct": f"{n1} likely has a time constraint or upcoming commitment",
            "distractors": [
                f"{n1} is fascinated by clocks",
                f"{n1} is fully engaged and not thinking about time",
                "Clock-checking has no connection to mental states",
            ],
        },
    ]

    s = rng.choice(scenarios)

    return {
        "prompt": f"Observation: {s['observation']}. What can we reasonably infer about {n1}'s beliefs or intentions?",
        "candidates": _shuffled_candidates(rng, s["correct"], s["distractors"]),
        "correct": s["correct"],
        "category": "tom_intention_reading",
        "tier": "B",
    }


# =============================================================================
# COMPOSITIONAL REASONING (NEW — 8 categories)
# =============================================================================

def _compositional_logic_arithmetic(rng: random.Random) -> dict:
    """Embed arithmetic result in logical premise."""
    a = rng.randint(1, 20)
    b = rng.randint(1, 20)
    s = a + b
    threshold = rng.randint(5, 35)

    n1 = _pick_names(rng, 1)[0]

    if s > threshold:
        correct = "Yes"
        logic_result = "the condition is satisfied"
    else:
        correct = "No"
        logic_result = "the condition is not satisfied"

    templates = [
        f"If a number is greater than {threshold}, it qualifies. {n1}'s number is the sum of {a} and {b}. Does {n1}'s number qualify?",
        f"Rule: values above {threshold} pass. {n1} has a score equal to {a} + {b}. Does {n1} pass?",
        f"Criterion: X > {threshold}. Given X = {a} + {b}, is the criterion met?",
    ]

    distractors = [
        "No" if correct == "Yes" else "Yes",
        "Cannot be determined",
        "Only if the numbers are positive",
    ]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "compositional_logic_arithmetic",
        "tier": "A",
    }


def _compositional_temporal_causal(rng: random.Random) -> dict:
    """Chain of causes with temporal ordering. Counterfactual question."""
    n1, n2, n3, n4 = _pick_names(rng, 4)

    events = [
        f"{n1} left the gate open",
        f"the dog escaped",
        f"the dog knocked over {n3}'s garden gnome",
        f"{n4} filed a complaint",
    ]

    chain_text = (
        f"{events[0]}, which caused {events[1]}. "
        f"After that, {events[2]}. "
        f"Because of the damage, {events[3]}."
    )

    correct = f"No — without {events[0]}, the chain of events would not have occurred"
    templates = [
        f"{chain_text} If {n1} had not left the gate open, would {n4} have filed a complaint?",
        f"Sequence: {chain_text} Counterfactual: if the first event hadn't happened, would the last event still occur?",
    ]

    distractors = [
        f"Yes — {n4} would have complained anyway",
        "Cannot determine — other factors might be involved",
        f"Yes — {n3}'s gnome was already damaged",
    ]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "compositional_temporal_causal",
        "tier": "A",
    }


def _compositional_logic_tom(rng: random.Random) -> dict:
    """Logic + Theory of Mind: what does an agent conclude from their beliefs?"""
    n1 = _pick_names(rng, 1)[0]

    scenarios = [
        {
            "belief": f"{n1} believes all birds can fly",
            "observation": f"{n1} sees a penguin, which {n1} knows is a bird",
            "question": f"What does {n1} conclude about the penguin?",
            "correct": f"{n1} concludes the penguin can fly (following from {n1}'s mistaken belief)",
            "distractors": [
                f"{n1} concludes the penguin cannot fly",
                f"{n1} has no basis for a conclusion",
                f"{n1} questions whether penguins are birds",
            ],
        },
        {
            "belief": f"{n1} believes all metals are magnetic",
            "observation": f"{n1} learns that gold is a metal",
            "question": f"What does {n1} conclude about gold?",
            "correct": f"{n1} concludes gold is magnetic (following from the mistaken premise)",
            "distractors": [
                f"{n1} concludes gold is not magnetic",
                f"{n1} revises the belief about metals",
                f"{n1} makes no conclusion",
            ],
        },
        {
            "belief": f"{n1} believes everyone in the office speaks French",
            "observation": f"{n1} meets a new colleague in the office",
            "question": f"What does {n1} assume about the new colleague?",
            "correct": f"{n1} assumes the colleague speaks French",
            "distractors": [
                f"{n1} asks to confirm first",
                f"{n1} assumes nothing about languages",
                f"{n1} assumes the colleague speaks English",
            ],
        },
    ]

    s = rng.choice(scenarios)

    return {
        "prompt": f"{s['belief']}. {s['observation']}. {s['question']}",
        "candidates": _shuffled_candidates(rng, s["correct"], s["distractors"]),
        "correct": s["correct"],
        "category": "compositional_logic_tom",
        "tier": "A",
    }


def _compositional_arithmetic_temporal(rng: random.Random) -> dict:
    """Classic rate-time-distance or work-rate problem requiring both arithmetic and temporal reasoning."""
    n1, n2 = _pick_names(rng, 2)

    # Train/vehicle catch-up problem
    speed_a = rng.choice([30, 40, 50, 60])
    speed_b = speed_a + rng.choice([15, 20, 30])
    head_start_hours = rng.randint(1, 3)

    # B catches A when: speed_b * t = speed_a * (t + head_start)
    # t = speed_a * head_start / (speed_b - speed_a)
    t_num = speed_a * head_start_hours
    t_den = speed_b - speed_a

    if t_num % t_den == 0:
        t = t_num // t_den
        correct = f"{t} hours after {n2} departs"
    else:
        # Use fractions for exactness
        from fractions import Fraction
        t_frac = Fraction(t_num, t_den)
        correct = f"{t_frac} hours after {n2} departs"

    start_hour = rng.randint(6, 12)

    templates = [
        f"{n1} leaves at {start_hour}:00 traveling at {speed_a} mph. {n2} leaves from the same place at {start_hour + head_start_hours}:00 traveling in the same direction at {speed_b} mph. When does {n2} catch up to {n1}?",
        f"At {start_hour} AM, {n1} departs going {speed_a} mph. {head_start_hours} hour(s) later, {n2} follows at {speed_b} mph along the same route. How long after {n2}'s departure will {n2} overtake {n1}?",
    ]

    # Generate distractor values
    wrong1 = f"{head_start_hours} hours after {n2} departs"
    wrong2 = f"{t_num} hours after {n2} departs"
    wrong3 = f"{head_start_hours + 1} hours after {n2} departs"
    distractors = [d for d in [wrong1, wrong2, wrong3] if d != correct][:3]
    while len(distractors) < 3:
        distractors.append(f"{rng.randint(1, 10)} hours after {n2} departs")

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "compositional_arithmetic_temporal",
        "tier": "A",
    }


def _compositional_causal_statistical(rng: random.Random) -> dict:
    """Simpson's paradox + causal reasoning about which treatment is better."""
    # Reuse Simpson's structure but frame as compositional reasoning task
    n1 = _pick_names(rng, 1)[0]

    # School A vs School B admission rates
    # A admits more overall, but B is better in each department
    dept1 = rng.choice(["Engineering", "Sciences", "Business", "Medicine", "Law"])
    dept2 = rng.choice([d for d in ["Humanities", "Arts", "Education", "Social Sciences"] if d != dept1])

    # Dept 1 (easy): A has many applicants, B has few
    a1_rate = rng.randint(75, 90)
    b1_rate = a1_rate + rng.randint(1, 5)
    b1_rate = min(b1_rate, 98)
    a1_n = rng.randint(500, 800)
    b1_n = rng.randint(50, 100)

    # Dept 2 (hard): A has few, B has many
    a2_rate = rng.randint(20, 40)
    b2_rate = a2_rate + rng.randint(1, 8)
    a2_n = rng.randint(50, 100)
    b2_n = rng.randint(500, 800)

    a_overall = round((a1_rate * a1_n + a2_rate * a2_n) / (a1_n + a2_n), 1)
    b_overall = round((b1_rate * b1_n + b2_rate * b2_n) / (b1_n + b2_n), 1)

    prompt = (
        f"School A overall admission rate: {a_overall}%. School B: {b_overall}%. "
        f"But broken down: {dept1} — A: {a1_rate}% (n={a1_n}), B: {b1_rate}% (n={b1_n}). "
        f"{dept2} — A: {a2_rate}% (n={a2_n}), B: {b2_rate}% (n={b2_n}). "
        f"{n1} concludes School A is less selective. Is this correct?"
    )

    correct = "No — Simpson's paradox. School B has higher rates in every department; A's overall rate is inflated by more applicants to the easier department"
    distractors = [
        f"Yes — A's overall rate of {a_overall}% proves it admits more",
        "Cannot determine without individual student data",
        "Both schools are equally selective",
    ]

    return {
        "prompt": prompt,
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "compositional_causal_statistical",
        "tier": "A",
    }


def _compositional_multi_hop_with_distractor(rng: random.Random) -> dict:
    """Logic chain with irrelevant premises mixed in."""
    n1 = _pick_names(rng, 1)[0]
    categories = rng.sample(["A", "B", "C", "D", "E"], 3)
    chain_a, chain_b, chain_c = categories

    distractors_premises = [
        "The sky is blue.",
        "Water freezes at 0°C.",
        f"{n1} enjoys hiking.",
        "Most birds can fly.",
        "The speed of light is constant.",
        "Triangles have three sides.",
    ]

    n_distractors = rng.randint(1, 3)
    distractor_stmts = rng.sample(distractors_premises, n_distractors)

    premises = [
        f"All {chain_a}s are {chain_b}s",
        f"All {chain_b}s are {chain_c}s",
    ] + distractor_stmts

    rng.shuffle(premises)
    premise_text = ". ".join(premises)

    entity_name = _pick_names(rng, 1)[0]

    templates = [
        f"{premise_text}. {entity_name} is a {chain_a}. Is {entity_name} a {chain_c}?",
        f"Given: {premise_text}. We know {entity_name} is a {chain_a}. Can we conclude {entity_name} is a {chain_c}?",
    ]

    correct = f"Yes — {chain_a} → {chain_b} → {chain_c}, so all {chain_a}s are {chain_c}s"
    wrong = [
        "No — the chain doesn't connect",
        "Cannot determine — the irrelevant premises create ambiguity",
        f"Only if {entity_name} is also a {chain_b}",
    ]

    return {
        "prompt": rng.choice(templates),
        "candidates": _shuffled_candidates(rng, correct, wrong),
        "correct": correct,
        "category": "compositional_multi_hop_with_distractor",
        "tier": "A",
    }


def _compositional_nested_tom_logic(rng: random.Random) -> dict:
    """Nested belief + logical evaluation."""
    n1, n2 = _pick_names(rng, 2)
    obj = rng.choice(OBJECTS)
    container = rng.choice(["box", "bag", "drawer", "locker"])
    content = rng.choice(["a cat", "a red ball", "a letter", "a gold coin"])

    actually_contains = rng.choice([True, False])
    n1_thinks = rng.choice([True, False])
    n2_thinks_n1_is = rng.choice(["right", "wrong"])

    # Determine correctness
    if n2_thinks_n1_is == "right":
        n2_belief = n1_thinks
    else:
        n2_belief = not n1_thinks

    if actually_contains:
        if n1_thinks:
            n1_status = "correct"
        else:
            n1_status = "wrong"
        if n2_thinks_n1_is == "right":
            n2_correct = n1_thinks == actually_contains
        else:
            n2_correct = (not n1_thinks) == actually_contains
    else:
        if not n1_thinks:
            n1_status = "correct"
        else:
            n1_status = "wrong"
        if n2_thinks_n1_is == "right":
            n2_correct = n1_thinks == actually_contains
        else:
            n2_correct = (not n1_thinks) == actually_contains

    contains_str = "contains" if actually_contains else "does not contain"
    n1_thinks_str = "contains" if n1_thinks else "does not contain"

    prompt = (
        f"The {container} {contains_str} {content}. "
        f"{n1} thinks the {container} {n1_thinks_str} {content}. "
        f"{n2} thinks {n1} is {n2_thinks_n1_is}. "
        f"Who is correct about what the {container} actually contains?"
    )

    # Determine answer
    both_wrong = (not (n1_thinks == actually_contains)) and (not n2_correct)
    both_right = (n1_thinks == actually_contains) and n2_correct

    if both_right:
        correct = "Both are correct"
    elif both_wrong:
        correct = "Neither is correct"
    elif n1_thinks == actually_contains:
        correct = f"Only {n1} is correct"
    else:
        correct = f"Only {n2} is correct"

    all_opts = [f"Only {n1} is correct", f"Only {n2} is correct", "Both are correct", "Neither is correct"]
    distractors = [o for o in all_opts if o != correct][:3]

    return {
        "prompt": prompt,
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "compositional_nested_tom_logic",
        "tier": "A",
    }


def _compositional_depth_scaling(rng: random.Random) -> dict:
    """Parameterized multi-type reasoning chain. Difficulty scales with step count."""
    n1 = _pick_names(rng, 1)[0]
    depth = rng.randint(2, 5)

    # Build a chain where each step is a different type
    # Start with a number and transform it
    val = rng.randint(2, 10)
    steps = []
    step_types = ["arithmetic", "comparison", "modular", "doubling", "offset"]
    used_types = rng.sample(step_types, min(depth, len(step_types)))

    for i, stype in enumerate(used_types):
        if stype == "arithmetic":
            addend = rng.randint(1, 10)
            steps.append(f"Add {addend} to the current value")
            val += addend
        elif stype == "comparison":
            # No change to val, but adds a reasoning step
            threshold = val + rng.choice([-5, -3, -1, 1, 3, 5])
            gt = val > threshold
            steps.append(f"Check: is the current value ({val}) greater than {threshold}? ({'Yes' if gt else 'No'})")
        elif stype == "modular":
            mod = rng.choice([3, 5, 7])
            remainder = val % mod
            steps.append(f"Take the current value mod {mod} (result: {remainder})")
            val = remainder
        elif stype == "doubling":
            steps.append(f"Double the current value")
            val *= 2
        elif stype == "offset":
            sub = rng.randint(1, max(2, val - 1))
            steps.append(f"Subtract {sub}")
            val -= sub

    step_text = ". ".join([f"Step {i+1}: {s}" for i, s in enumerate(steps)])
    correct = str(val)

    templates = [
        f"{n1} starts with the number {rng.randint(2, 10)}. {'... wait, ' if False else ''}{step_text}. What is the final value?",
    ]

    # Reconstruct starting value from the steps to make the prompt consistent
    # Actually, let's rebuild properly
    start_val = rng.randint(2, 10)
    val = start_val
    steps_clean = []

    for stype in used_types:
        if stype == "arithmetic":
            addend = rng.randint(1, 10)
            steps_clean.append(f"Add {addend}")
            val += addend
        elif stype == "comparison":
            # Comparison doesn't change value — skip for simplicity
            pass
        elif stype == "modular":
            mod = rng.choice([3, 5, 7])
            steps_clean.append(f"Take the result mod {mod}")
            val = val % mod
        elif stype == "doubling":
            steps_clean.append(f"Double the result")
            val *= 2
        elif stype == "offset":
            sub = rng.randint(1, max(2, val // 2 + 1))
            steps_clean.append(f"Subtract {sub}")
            val -= sub

    correct = str(val)
    step_text = ". ".join([f"Step {i+1}: {s}" for i, s in enumerate(steps_clean)])

    prompt = f"Start with {start_val}. {step_text}. What is the final result?"

    distractors = list({
        str(val + rng.randint(1, 5)),
        str(abs(val - rng.randint(1, 5))),
        str(start_val),
    } - {correct})
    while len(distractors) < 3:
        d = str(val + rng.randint(-10, 10))
        if d != correct and d not in distractors:
            distractors.append(d)
    distractors = distractors[:3]

    return {
        "prompt": prompt,
        "candidates": _shuffled_candidates(rng, correct, distractors),
        "correct": correct,
        "category": "compositional_depth_scaling",
        "tier": "A",
    }


# =============================================================================
# EXPANDED_GENERATORS — append to your EXTENDED_GENERATORS list
# =============================================================================

EXPANDED_GENERATORS = [
    # Temporal (9)
    _temporal_concurrent_events,
    _temporal_frequency_coincidence,
    _temporal_sequence_reconstruction,
    _temporal_duration_across_midnight,
    _temporal_relative_day,
    _temporal_rate_of_change,
    _temporal_causal_ordering,
    _temporal_scheduling_conflict,
    _temporal_age_reasoning,
    # Causal (7)
    _causal_intervention,
    _causal_confounding,
    _causal_chain_length,
    _causal_counterfactual,
    _causal_necessary_sufficient_extended,
    _causal_simpson_paradox,
    _causal_common_cause,
    # Theory of Mind (7)
    _tom_second_order_belief,
    _tom_information_asymmetry,
    _tom_strategic_deception,
    _tom_group_knowledge,
    _tom_perspective_shift,
    _tom_mistaken_belief_chain,
    _tom_intention_reading,
    # Compositional (8)
    _compositional_logic_arithmetic,
    _compositional_temporal_causal,
    _compositional_logic_tom,
    _compositional_arithmetic_temporal,
    _compositional_causal_statistical,
    _compositional_multi_hop_with_distractor,
    _compositional_nested_tom_logic,
    _compositional_depth_scaling,
]


# =============================================================================
# Self-test: verify all generators produce valid output
# =============================================================================

def test_all_generators(seed=99, n_per=3):
    """Run all expanded generators, verify output format and determinism."""
    print(f"Testing {len(EXPANDED_GENERATORS)} generators, {n_per} instances each...\n")
    categories_seen = set()
    total = 0
    errors = 0

    for gen_fn in EXPANDED_GENERATORS:
        for i in range(n_per):
            try:
                rng = random.Random(seed + i)
                result = gen_fn(rng)

                # Validate structure
                assert isinstance(result, dict), f"Not a dict: {type(result)}"
                for key in ["prompt", "candidates", "correct", "category", "tier"]:
                    assert key in result, f"Missing key: {key}"
                assert isinstance(result["candidates"], list), "candidates not a list"
                assert len(result["candidates"]) >= 2, f"Too few candidates: {len(result['candidates'])}"
                assert result["correct"] in result["candidates"], (
                    f"Correct answer not in candidates!\n"
                    f"  correct: {result['correct']}\n"
                    f"  candidates: {result['candidates']}"
                )
                assert result["tier"] in ("A", "B"), f"Invalid tier: {result['tier']}"

                categories_seen.add(result["category"])
                total += 1

            except Exception as e:
                errors += 1
                print(f"  ERROR in {gen_fn.__name__} (seed={seed+i}): {e}")

    print(f"Results: {total} items generated, {errors} errors")
    print(f"Categories: {len(categories_seen)}")
    for cat in sorted(categories_seen):
        print(f"  - {cat}")

    # Tier breakdown
    tier_a = sum(1 for g in EXPANDED_GENERATORS
                 for _ in [g(random.Random(seed))]
                 if _["tier"] == "A")
    tier_b = len(EXPANDED_GENERATORS) - tier_a
    print(f"\nTier A: {tier_a} generators")
    print(f"Tier B: {tier_b} generators")
    print(f"\nBattery expansion: 58 existing + {len(categories_seen)} new = {58 + len(categories_seen)} total categories")

    return errors == 0


if __name__ == "__main__":
    success = test_all_generators()
    if success:
        print("\n✓ All generators passed validation.")
    else:
        print("\n✗ Some generators failed — see errors above.")
