"""Extended trap generators — Phase 3 (Meta-Reasoning / ToM / Multi-Step)
and Phase 4 (Arithmetic / Spatial / Set Theory / Cognitive Bias).

Complements the base battery in trap_generator.py without modifying it.

Usage:
    from trap_generator_extended import generate_extended_battery, generate_full_battery
    traps = generate_full_battery(n_per_category=2, seed=42)
"""

import random

from trap_generator import generate_trap_battery


# ---------------------------------------------------------------------------
# Helper pools
# ---------------------------------------------------------------------------
_NAMES = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Hank",
          "Ivy", "Jack", "Karen", "Leo", "Mia", "Nate", "Olive", "Paul"]
_OBJECTS = ["ball", "book", "hat", "key", "cup", "ring", "pen", "coin",
            "scarf", "toy", "box", "clock", "vase", "bag", "doll", "lamp"]
_LOCATIONS = ["kitchen", "bedroom", "garden", "garage", "attic", "closet",
              "basement", "shed", "porch", "pantry", "study", "hallway"]
_ANIMALS = ["cats", "dogs", "birds", "fish", "horses", "rabbits",
            "turtles", "wolves", "foxes", "deer", "bears", "owls"]
_PROPS = ["fluffy", "fast", "loud", "small", "tall", "heavy",
          "bright", "sharp", "round", "warm"]
_CATEGORIES = ["mammals", "vehicles", "planets", "instruments",
               "fruits", "gemstones", "metals", "languages"]


# ===================================================================
# PHASE 3 — Meta-Reasoning + Theory of Mind + Multi-Step Chain
# ===================================================================

def _validity_vs_truth(rng: random.Random) -> dict:
    """Valid syllogism with false premises.  Answer: Yes (valid)."""
    templates = [
        {
            "x_class": "rocks", "y_verb": "swim", "z_name": "granite",
            "premise1": "All rocks can swim",
            "premise2": "Granite is a rock",
            "conclusion": "Granite can swim",
        },
        {
            "x_class": "tables", "y_verb": "fly", "z_name": None,
            "premise1": "All tables can fly",
            "premise2": "{z} is a table",
            "conclusion": "{z} can fly",
        },
        {
            "x_class": "pencils", "y_verb": "sing", "z_name": None,
            "premise1": "All pencils can sing",
            "premise2": "{z} is a pencil",
            "conclusion": "{z} can sing",
        },
        {
            "x_class": "clouds", "y_verb": "dance", "z_name": None,
            "premise1": "All clouds can dance",
            "premise2": "{z} is a cloud",
            "conclusion": "{z} can dance",
        },
    ]
    t = rng.choice(templates)
    z = t["z_name"] or rng.choice(["Nimbus", "Stratus", "Cirrus", "Cumulus",
                                    "Woody", "Sparky", "Bolt", "Rusty"])
    p1 = t["premise1"]
    p2 = t["premise2"].replace("{z}", z)
    conc = t["conclusion"].replace("{z}", z)
    prompt = (f"{p1}. {p2}. Therefore, {conc}. "
              f"Is this argument logically valid?")
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No"],
        "correct": "Yes",
        "category": "validity_vs_truth",
        "tier": "B",
    }


def _argument_strength(rng: random.Random) -> dict:
    """Two arguments for the same conclusion — one valid, one fallacious."""
    name = rng.choice(_NAMES)
    animal = rng.choice(["cat", "dog", "parrot", "hamster"])
    # Valid argument (modus ponens)
    arg_valid = (f"If {name} has a {animal}, then {name} has a pet. "
                 f"{name} has a {animal}. Therefore {name} has a pet.")
    # Fallacious argument (affirming the consequent)
    arg_fallacy = (f"If {name} has a {animal}, then {name} has a pet. "
                   f"{name} has a pet. Therefore {name} has a {animal}.")
    if rng.random() < 0.5:
        prompt = (f"Argument A: {arg_valid}\n"
                  f"Argument B: {arg_fallacy}\n"
                  f"Which argument is logically stronger?")
        correct = "A"
    else:
        prompt = (f"Argument A: {arg_fallacy}\n"
                  f"Argument B: {arg_valid}\n"
                  f"Which argument is logically stronger?")
        correct = "B"
    return {
        "prompt": prompt,
        "candidates": ["A", "B", "Both are equally strong", "Neither is valid"],
        "correct": correct,
        "category": "argument_strength",
        "tier": "B",
    }


def _confidence_calibration(rng: random.Random) -> dict:
    """Told 'probably X'. How confident should you be?"""
    hedges = [
        ("probably", "Moderate"),
        ("likely", "Moderate"),
        ("almost certainly", "High"),
        ("possibly", "Low"),
        ("it is believed that", "Moderate"),
    ]
    hedge, level = rng.choice(hedges)
    subjects = ["the package will arrive tomorrow",
                "it will rain this afternoon",
                "the meeting is cancelled",
                "the restaurant is open today",
                "the flight is on time"]
    subj = rng.choice(subjects)
    prompt = (f"A reliable source tells you: '{hedge} {subj}.' "
              f"How confident should you be that {subj}?")
    return {
        "prompt": prompt,
        "candidates": ["Very high", "High", "Moderate", "Low", "No confidence"],
        "correct": level,
        "category": "confidence_calibration",
        "tier": "B",
    }


def _self_referential_consistency(rng: random.Random) -> dict:
    """'This sentence has N words.'  Count and verify."""
    # Build a sentence of a known word count, then state a claim
    fillers = [
        ("This sentence has exactly {n} words in it", 8),
        ("This particular sentence contains precisely {n} words", 7),
        ("There are exactly {n} words in this short sentence here", 10),
        ("This sentence is composed of {n} individual words total", 9),
    ]
    template, true_count = rng.choice(fillers)
    # Decide whether to state the correct count or a wrong one
    if rng.random() < 0.5:
        claimed = true_count
        correct = "True"
    else:
        claimed = true_count + rng.choice([-1, 1, 2])
        correct = "False"
    sentence = template.format(n=claimed)
    # Verify our count
    actual = len(sentence.split())
    if actual != true_count:
        # Safety fallback: recalculate
        if actual == claimed:
            correct = "True"
        else:
            correct = "False"
    prompt = f'Is the following statement true? "{sentence}"'
    return {
        "prompt": prompt,
        "candidates": ["True", "False"],
        "correct": correct,
        "category": "self_referential_consistency",
        "tier": "A",
    }


def _liar_detection(rng: random.Random) -> dict:
    """Three people, exactly one tells the truth. Solve by constraint."""
    names = rng.sample(_NAMES[:8], 3)
    a, b, c = names
    # Structure: A says B lies. B says C lies. C says A tells truth.
    # If A truthful: B lies (ok). Since B lies, C doesn't lie => C truthful.
    #   But we need exactly one truthful. C truthful too => contradiction.
    # If B truthful: A lies (from A's claim, B actually tells truth, contradiction
    #   with A saying B lies). Actually: A says B lies. If B is truthful,
    #   then A is wrong => A is a liar. B says C lies => C is a liar. Exactly one truthful (B). Works!
    # If C truthful: C says A tells truth => two truthful. Contradiction.
    # Answer: B
    prompt = (f"{a} says '{b} always lies.' "
              f"{b} says '{c} always lies.' "
              f"{c} says '{a} always tells the truth.' "
              f"If exactly one of them always tells the truth, who is it?")
    candidates = rng.sample(names, 3) + ["None of them"]
    if b not in candidates:
        candidates[0] = b
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": b,
        "category": "liar_detection",
        "tier": "A",
    }


def _false_belief_task(rng: random.Random) -> dict:
    """Sally-Anne false-belief test."""
    names = rng.sample(_NAMES[:8], 2)
    sally, anne = names
    obj = rng.choice(_OBJECTS[:8])
    loc1, loc2 = rng.sample(_LOCATIONS[:6], 2)
    prompt = (f"{sally} puts a {obj} in the {loc1} and leaves the room. "
              f"While {sally} is away, {anne} moves the {obj} to the {loc2}. "
              f"{sally} comes back. Where will {sally} look for the {obj}?")
    return {
        "prompt": prompt,
        "candidates": [f"The {loc1}", f"The {loc2}",
                       "Both places", "Neither place"],
        "correct": f"The {loc1}",
        "category": "false_belief_task",
        "tier": "A",
    }


def _knowledge_attribution(rng: random.Random) -> dict:
    """You know something is rigged; an uninformed person doesn't."""
    names = rng.sample(_NAMES[:8], 1)
    tom = names[0]
    sides = rng.randint(2, 3)
    rigged = rng.choice(["heads", "red", "win", "6"])
    obj_map = {"heads": "coin", "red": "roulette wheel",
               "win": "game", "6": "die"}
    obj = obj_map[rigged]
    prompt = (f"You know a {obj} is rigged to always land on {rigged}. "
              f"{tom} does not know it is rigged. "
              f"What does {tom} expect the {obj} to produce?")
    if rigged == "heads":
        correct = "Either heads or tails with roughly equal chance"
    elif rigged == "red":
        correct = "Any color with roughly equal chance"
    elif rigged == "win":
        correct = "Either a win or loss with roughly equal chance"
    else:
        correct = "Any number from 1 to 6 with roughly equal chance"
    return {
        "prompt": prompt,
        "candidates": [f"Always {rigged}", correct,
                       "Cannot determine", f"Never {rigged}"],
        "correct": correct,
        "category": "knowledge_attribution",
        "tier": "A",
    }


def _second_order_belief(rng: random.Random) -> dict:
    """Alice thinks Bob thinks X. What does Alice believe about Bob's belief?"""
    names = rng.sample(_NAMES[:8], 2)
    alice, bob = names
    beliefs = [
        ("the store is open", "the store is closed"),
        ("the movie starts at 7", "the movie starts at 8"),
        ("the test is easy", "the test is hard"),
        ("it will rain tomorrow", "it will be sunny tomorrow"),
    ]
    true_belief, alt = rng.choice(beliefs)
    prompt = (f"{alice} thinks that {bob} believes {true_belief}. "
              f"According to {alice}, what does {bob} believe?")
    return {
        "prompt": prompt,
        "candidates": [true_belief, alt,
                       f"{alice} has no opinion", "Cannot determine"],
        "correct": true_belief,
        "category": "second_order_belief",
        "tier": "A",
    }


def _multi_hop_deduction(rng: random.Random) -> dict:
    """All A are B. All B are C. ... Is X a <last>?"""
    n_hops = rng.randint(3, 5)
    # Build a chain of categories
    pool = rng.sample(_CATEGORIES, min(n_hops + 1, len(_CATEGORIES)))
    while len(pool) < n_hops + 1:
        pool.append(rng.choice(_PROPS) + " things")
    chain = pool[:n_hops + 1]  # chain[0] -> chain[1] -> ... -> chain[n_hops]
    name = rng.choice(_NAMES[:8])
    premises = [f"All {chain[i]} are {chain[i+1]}" for i in range(n_hops)]
    rng.shuffle(premises)
    premises_str = ". ".join(premises)
    prompt = (f"{premises_str}. {name} is one of the {chain[0]}. "
              f"Is {name} one of the {chain[-1]}?")
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No", "Cannot determine"],
        "correct": "Yes",
        "category": "multi_hop_deduction",
        "tier": "A",
    }


def _information_sufficiency(rng: random.Random) -> dict:
    """Disconnected comparisons — cannot determine ordering across chains."""
    names = rng.sample(_NAMES[:8], 4)
    a, b, c, d = names
    trait = rng.choice(["taller", "faster", "older", "heavier"])
    prompt = (f"{a} is {trait} than {b}. {c} is {trait} than {d}. "
              f"Is {a} {trait} than {d}?")
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No", "Cannot determine"],
        "correct": "Cannot determine",
        "category": "information_sufficiency",
        "tier": "A",
    }


def _irrelevant_premise(rng: random.Random) -> dict:
    """Premises with a red herring. Correct answer ignores it."""
    names = rng.sample(_NAMES[:8], 2)
    subj = names[0]
    # Real premises
    animal = rng.choice(["cat", "dog", "parrot", "hamster"])
    color = rng.choice(["red", "blue", "green", "yellow"])
    # Red herring
    herring = rng.choice([
        f"{names[1]} enjoys painting",
        f"The weather today is sunny",
        f"There are 52 cards in a standard deck",
        f"Water boils at 100 degrees Celsius",
    ])
    prompt = (f"If {subj} has a {animal}, then {subj} is a pet owner. "
              f"{herring}. {subj} has a {animal}. "
              f"Is {subj} a pet owner?")
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No", "Cannot determine"],
        "correct": "Yes",
        "category": "irrelevant_premise",
        "tier": "A",
    }


def _premise_contradiction(rng: random.Random) -> dict:
    """Two premises that contradict each other."""
    name = rng.choice(_NAMES[:8])
    contradictions = [
        (f"{name} is taller than 6 feet", f"{name} is shorter than 5 feet"),
        (f"The box is completely empty", f"The box contains a ball"),
        (f"All lights are off", f"The kitchen light is on"),
        (f"No one passed the test", f"{name} scored 100 on the test"),
        (f"The store is closed today", f"The store is open until 9 PM today"),
    ]
    p1, p2 = rng.choice(contradictions)
    prompt = (f'Premise 1: "{p1}." Premise 2: "{p2}." '
              f"Are these two premises consistent with each other?")
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No"],
        "correct": "No",
        "category": "premise_contradiction",
        "tier": "A",
    }


def _chained_conditional(rng: random.Random) -> dict:
    """If A then B. If B then C. If C then D. A is true. Is D true?"""
    n_links = rng.randint(3, 5)
    props = rng.sample([
        "the alarm rings", "the dog barks", "the baby wakes up",
        "the lights turn on", "the door opens", "the phone buzzes",
        "the bell chimes", "the fan starts", "the water flows",
    ], min(n_links + 1, 9))
    while len(props) < n_links + 1:
        props.append(f"event {len(props)} occurs")
    chain = props[:n_links + 1]
    conditionals = [f"If {chain[i]}, then {chain[i+1]}" for i in range(n_links)]
    rng.shuffle(conditionals)
    prompt = (". ".join(conditionals) + f". {chain[0].capitalize()}. "
              f"Does it follow that {chain[-1]}?")
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No", "Cannot determine"],
        "correct": "Yes",
        "category": "chained_conditional",
        "tier": "A",
    }


# ===================================================================
# PHASE 4 — Arithmetic + Spatial + Set Theory + Remaining
# ===================================================================

def _order_of_operations(rng: random.Random) -> dict:
    """PEMDAS: A + B * C  (multiplication before addition)."""
    a = rng.randint(1, 20)
    b = rng.randint(2, 10)
    c = rng.randint(2, 10)
    correct_val = a + b * c
    wrong_val = (a + b) * c  # left-to-right mistake
    prompt = f"What is {a} + {b} * {c}?"
    candidates = [str(correct_val), str(wrong_val)]
    if correct_val == wrong_val:
        candidates.append(str(correct_val + 1))
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": str(correct_val),
        "category": "order_of_operations",
        "tier": "A",
    }


def _modular_arithmetic(rng: random.Random) -> dict:
    """Clock math: 'It's H o'clock. What time in N hours?'"""
    h = rng.randint(1, 12)
    n = rng.randint(3, 30)
    result_24 = (h + n) % 12
    if result_24 == 0:
        result_24 = 12
    # Determine AM/PM
    # Use 12-hour display only, keep it simple
    prompt = (f"It is {h}:00 PM. What time will it be in {n} hours? "
              f"(Give the hour only, in 12-hour format.)")
    total = h + n
    hour_12 = total % 12
    if hour_12 == 0:
        hour_12 = 12
    # Count how many half-days pass to determine AM/PM
    # Starting at PM: after 12 hours flips to AM, etc.
    pm_start = True
    flips = total // 12 - h // 12
    # Simpler: h PM = h+12 in 24hr (except 12 PM = 12)
    h24 = h + 12 if h != 12 else 12
    end24 = (h24 + n) % 24
    if end24 == 0:
        end24_display = 12
        ampm = "AM"
    elif end24 < 12:
        end24_display = end24
        ampm = "AM"
    elif end24 == 12:
        end24_display = 12
        ampm = "PM"
    else:
        end24_display = end24 - 12
        ampm = "PM"
    correct_str = f"{end24_display}:00 {ampm}"
    # Generate wrong answers
    wrong1 = f"{end24_display}:00 {'AM' if ampm == 'PM' else 'PM'}"
    wrong_hour = (end24_display % 12) + 1
    wrong2 = f"{wrong_hour}:00 {ampm}"
    candidates = [correct_str, wrong1, wrong2]
    # Deduplicate
    candidates = list(dict.fromkeys(candidates))
    while len(candidates) < 3:
        candidates.append(f"{rng.randint(1,12)}:00 {rng.choice(['AM','PM'])}")
        candidates = list(dict.fromkeys(candidates))
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct_str,
        "category": "modular_arithmetic",
        "tier": "A",
    }


def _fencepost(rng: random.Random) -> dict:
    """Fence M meters, post every N meters — how many posts? (M/N + 1)."""
    n = rng.choice([2, 3, 4, 5, 10])
    sections = rng.randint(3, 15)
    m = n * sections
    correct_posts = sections + 1
    wrong_posts = sections  # classic off-by-one
    prompt = (f"A straight fence is {m} meters long. A post is placed every "
              f"{n} meters, including both ends. How many posts are there?")
    candidates = [str(correct_posts), str(wrong_posts)]
    if correct_posts - 1 != wrong_posts:
        candidates.append(str(correct_posts - 1))
    else:
        candidates.append(str(correct_posts + 1))
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": str(correct_posts),
        "category": "fencepost",
        "tier": "A",
    }


def _inclusion_exclusion(rng: random.Random) -> dict:
    """N students, A play X, B play Y. Minimum playing both?"""
    n = rng.randint(20, 50)
    a = rng.randint(n // 2 + 1, n)  # ensure overlap is possible
    b = rng.randint(n // 2 + 1, n)
    min_both = max(0, a + b - n)
    sport1 = rng.choice(["soccer", "basketball", "tennis", "volleyball"])
    sport2 = rng.choice(["chess", "swimming", "baseball", "hockey"])
    prompt = (f"In a class of {n} students, {a} play {sport1} and "
              f"{b} play {sport2}. Every student plays at least one. "
              f"What is the minimum number that play both?")
    wrong = min(a, b)
    candidates = [str(min_both), str(wrong), str(a + b - n - 1)]
    candidates = [c for c in dict.fromkeys(candidates)]
    while len(candidates) < 3:
        candidates.append(str(min_both + rng.randint(1, 5)))
        candidates = list(dict.fromkeys(candidates))
    candidates = candidates[:4]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": str(min_both),
        "category": "inclusion_exclusion",
        "tier": "A",
    }


def _left_right_reversal(rng: random.Random) -> dict:
    """Alice faces Bob, raises left hand. Which side from Bob's view?"""
    names = rng.sample(_NAMES[:8], 2)
    a, b = names
    hand = rng.choice(["left", "right"])
    # When facing someone, their left appears on your right and vice versa
    from_other = "right" if hand == "left" else "left"
    prompt = (f"{a} and {b} are facing each other. {a} raises their "
              f"{hand} hand. From {b}'s perspective, on which side "
              f"does {a}'s raised hand appear?")
    return {
        "prompt": prompt,
        "candidates": [f"{b}'s left", f"{b}'s right"],
        "correct": f"{b}'s {from_other}",
        "category": "left_right_reversal",
        "tier": "A",
    }


def _direction_composition(rng: random.Random) -> dict:
    """Face a direction, make turns. What direction now?"""
    directions = ["North", "East", "South", "West"]
    start_idx = rng.randint(0, 3)
    n_turns = rng.randint(2, 4)
    turns = []
    current = start_idx
    for _ in range(n_turns):
        turn = rng.choice(["right", "left"])
        turns.append(turn)
        if turn == "right":
            current = (current + 1) % 4
        else:
            current = (current - 1) % 4
    turn_str = ", then turn ".join(turns)
    prompt = (f"You are facing {directions[start_idx]}. "
              f"You turn {turn_str}. Which direction are you facing now?")
    candidates = list(directions)
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": directions[current],
        "category": "direction_composition",
        "tier": "A",
    }


def _containment(rng: random.Random) -> dict:
    """X is in Y, Y is in Z. Is X in Z?  (Transitive containment.)"""
    objs = rng.sample(_OBJECTS[:8], 3)
    x, y, z = objs
    # Randomly shuffle premise order to avoid trivial pattern matching
    premises = [f"The {x} is inside the {y}", f"The {y} is inside the {z}"]
    rng.shuffle(premises)
    prompt = f"{premises[0]}. {premises[1]}. Is the {x} inside the {z}?"
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No", "Cannot determine"],
        "correct": "Yes",
        "category": "containment",
        "tier": "A",
    }


def _empty_set(rng: random.Random) -> dict:
    """Vacuous truth: all unicorns are X AND all unicorns are not-X. Both true."""
    creatures = ["unicorns", "dragons", "phoenixes", "griffins", "mermaids"]
    creature = rng.choice(creatures)
    prop_pairs = [
        ("blue", "red"), ("tall", "short"), ("heavy", "light"),
        ("fast", "slow"), ("loud", "quiet"),
    ]
    p1, p2 = rng.choice(prop_pairs)
    prompt = (f'Consider: "All {creature} are {p1}" and '
              f'"All {creature} are {p2}." '
              f"Given that no {creature} exist, can both statements be true simultaneously?")
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No"],
        "correct": "Yes",
        "category": "empty_set",
        "tier": "A",
    }


def _subset_inversion(rng: random.Random) -> dict:
    """'All A are B' does NOT imply 'All B are A'."""
    pairs = [
        ("primes greater than 2", "odd numbers", "odd numbers greater than 2", "prime"),
        ("squares", "rectangles", "rectangles", "squares"),
        ("teenagers", "people under 20", "people under 20", "teenagers"),
        ("poodles", "dogs", "dogs", "poodles"),
        ("January days", "winter days", "winter days", "January days"),
    ]
    a, b, b_full, a_short = rng.choice(pairs)
    prompt = (f"All {a} are {b}. Does it follow that all {b_full} are {a_short}?")
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No"],
        "correct": "No",
        "category": "subset_inversion",
        "tier": "A",
    }


def _survivorship_bias(rng: random.Random) -> dict:
    """All successes had trait X — should you adopt X?"""
    traits = [
        ("dropped out of college", "successful entrepreneurs"),
        ("woke up at 5 AM", "top CEOs"),
        ("practiced 10 hours a day", "Olympic athletes"),
        ("moved to Silicon Valley", "tech billionaires"),
    ]
    trait, group = rng.choice(traits)
    prompt = (f"A study finds that all {group} in a sample {trait}. "
              f"Should you {trait} to increase your chances of similar success?")
    return {
        "prompt": prompt,
        "candidates": [
            "Yes, it clearly works",
            "No, we also need to see how many who did that failed",
            "Yes, the pattern is strong enough",
            "No, correlation never implies anything",
        ],
        "correct": "No, we also need to see how many who did that failed",
        "category": "survivorship_bias",
        "tier": "B",
    }


def _sunk_cost(rng: random.Random) -> dict:
    """Already spent money/time. Should that affect the go/no-go decision?"""
    costs = [
        (rng.randint(50, 500), "concert ticket", "feeling sick",
         "staying home"),
        (rng.randint(100, 1000), "non-refundable vacation package",
         "a family emergency", "cancelling the trip"),
        (rng.randint(20, 200), "movie ticket", "finding out the movie "
         "has terrible reviews", "skipping the movie"),
    ]
    amt, item, obstacle, alt = rng.choice(costs)
    prompt = (f"You spent ${amt} on a {item}. On the day of the event, "
              f"you are {obstacle}. A friend says you should go because "
              f"you already paid. Is the amount already spent a good reason "
              f"to go?")
    return {
        "prompt": prompt,
        "candidates": [
            "Yes, otherwise the money is wasted",
            "No, the money is spent regardless of whether you go",
            "Yes, you should always get your money's worth",
            "It depends on the amount spent",
        ],
        "correct": "No, the money is spent regardless of whether you go",
        "category": "sunk_cost",
        "tier": "B",
    }


def _framing_effect(rng: random.Random) -> dict:
    """Same statistic framed differently. Are they equivalent?"""
    pct = rng.randint(70, 99)
    complement = 100 - pct
    frames = [
        (f"{pct}% survival rate", f"{complement}% mortality rate"),
        (f"{pct}% success rate", f"{complement}% failure rate"),
        (f"{pct}% of trains arrive on time",
         f"{complement}% of trains are delayed"),
    ]
    pos, neg = rng.choice(frames)
    prompt = (f'Statement A: "{pos}." Statement B: "{neg}." '
              f"Do these two statements convey the same information?")
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No"],
        "correct": "Yes",
        "category": "framing_effect",
        "tier": "A",
    }


def _false_dichotomy(rng: random.Random) -> dict:
    """Either X or Y presented as only options, but Z is possible."""
    scenarios = [
        ("you support policy X", "you don't care about the issue",
         "support a different policy"),
        ("you agree with me", "you are against me",
         "be neutral or partially agree"),
        ("we expand the project", "we cancel it entirely",
         "scale it down"),
        ("you eat meat", "you are a strict vegan",
         "be vegetarian or flexitarian"),
    ]
    x, y, z = rng.choice(scenarios)
    name = rng.choice(_NAMES[:8])
    prompt = (f'{name} says: "Either {x}, or {y}. There is no other option." '
              f"Is it possible to {z} instead?")
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No"],
        "correct": "Yes",
        "category": "false_dichotomy",
        "tier": "B",
    }


def _composition_fallacy(rng: random.Random) -> dict:
    """Every part has property P. Must the whole have property P?"""
    scenarios = [
        ("atom", "invisible to the naked eye", "a rock"),
        ("feather", "light", "a pillow filled with feathers"),
        ("player on the team", "talented", "the team as a whole"),
        ("grain of sand", "tiny", "a sand dune"),
        ("water molecule", "odorless", "the ocean"),
    ]
    part, prop, whole = rng.choice(scenarios)
    prompt = (f"Every {part} is {prop}. Does it necessarily follow "
              f"that {whole} is also {prop}?")
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No, not necessarily"],
        "correct": "No, not necessarily",
        "category": "composition_fallacy",
        "tier": "B",
    }


def _regression_to_mean(rng: random.Random) -> dict:
    """Extreme score followed by less extreme — regression, not decline."""
    name = rng.choice(_NAMES[:8])
    high = rng.randint(90, 99)
    lower = rng.randint(75, 89)
    activity = rng.choice(["exam", "game", "race", "performance review"])
    prompt = (f"{name} scored {high} on one {activity}, then {lower} on the next. "
              f"A coach concludes {name} is getting worse. "
              f"What is the most likely explanation?")
    return {
        "prompt": prompt,
        "candidates": [
            f"{name} is indeed declining in ability",
            "Regression to the mean — the first score was unusually high",
            "The second test was harder",
            "The coach's feedback caused the drop",
        ],
        "correct": "Regression to the mean — the first score was unusually high",
        "category": "regression_to_mean",
        "tier": "B",
    }


def _affirming_consequent_numeric(rng: random.Random) -> dict:
    """'If divisible by 4 then even. N is even. Divisible by 4?'  No."""
    # Pick a number that is even but NOT divisible by 4
    base = rng.randint(1, 24)
    n = base * 2  # guaranteed even
    # Make sure it's not divisible by 4
    if n % 4 == 0:
        n += 2  # still even, not div by 4
    prompt = (f"If a number is divisible by 4, then it is even. "
              f"{n} is even. Is {n} necessarily divisible by 4?")
    return {
        "prompt": prompt,
        "candidates": ["Yes", "No"],
        "correct": "No",
        "category": "affirming_consequent_numeric",
        "tier": "A",
    }


def _intention_vs_outcome(rng: random.Random) -> dict:
    """Good decision, bad outcome. Was the decision itself correct?"""
    scenarios = [
        (
            "A doctor prescribed the standard recommended treatment for a "
            "patient. The patient had a rare, unpredictable allergic reaction.",
            "Was the doctor's decision to prescribe that treatment a reasonable one?",
            "Yes, the decision was reasonable given available information",
        ),
        (
            "A driver wore a seatbelt and drove the speed limit. Another car "
            "ran a red light and caused an accident.",
            "Was the driver's behavior appropriate?",
            "Yes, the decision was reasonable given available information",
        ),
        (
            "An investor diversified their portfolio following standard "
            "financial advice. An unprecedented market crash caused losses.",
            "Was the investment strategy a sound decision?",
            "Yes, the decision was reasonable given available information",
        ),
        (
            "A firefighter followed protocol to enter a building. "
            "An unforeseeable structural collapse trapped them.",
            "Was the firefighter's decision to enter correct?",
            "Yes, the decision was reasonable given available information",
        ),
    ]
    context, question, correct = rng.choice(scenarios)
    prompt = f"{context} {question}"
    return {
        "prompt": prompt,
        "candidates": [
            correct,
            "No, the bad outcome proves it was a bad decision",
            "Cannot evaluate without knowing the outcome first",
            "Only if the outcome had been good",
        ],
        "correct": correct,
        "category": "intention_vs_outcome",
        "tier": "B",
    }


# ===================================================================
# PHASE 5 — Temporal Expansion (3→12)
# ===================================================================

_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
         "Saturday", "Sunday"]

_ACTIVITIES = ["baking a cake", "assembling furniture", "writing a report",
               "painting a wall", "downloading a file", "running a bath",
               "charging a battery", "defrosting a chicken"]

_EVENT_NAMES = ["the lecture", "the concert", "the ceremony", "the parade",
                "the launch", "the broadcast", "the rehearsal", "the drill"]


def _temporal_concurrent_events(rng: random.Random) -> dict:
    """A takes X min, B takes Y min. Start both at same time. When is first done?"""
    n_events = rng.randint(2, 4)
    activities = rng.sample(_ACTIVITIES, n_events)
    durations = [rng.randint(3, 60) for _ in range(n_events)]
    min_dur = min(durations)
    fastest = activities[durations.index(min_dur)]

    descs = [f"{a} takes {d} minutes" for a, d in zip(activities, durations)]
    templates = [
        "You start all tasks at the same time: {tasks}. Which finishes first, and after how many minutes?",
        "{tasks}. If all begin simultaneously, which is done earliest, and when?",
        "Starting together: {tasks}. What completes first and how long does it take?",
    ]
    prompt = rng.choice(templates).format(tasks="; ".join(descs))
    correct = f"{fastest.capitalize()} after {min_dur} minutes"
    # Build distractors
    candidates = [correct]
    for a, d in zip(activities, durations):
        if d != min_dur:
            candidates.append(f"{a.capitalize()} after {d} minutes")
            if len(candidates) >= 4:
                break
    while len(candidates) < 3:
        candidates.append(f"{activities[-1].capitalize()} after {max(durations)} minutes")
    candidates = list(dict.fromkeys(candidates))[:4]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "temporal_concurrent_events",
        "tier": "A",
    }


def _temporal_frequency_coincidence(rng: random.Random) -> dict:
    """A happens every X days, B every Y days. When do they coincide? (LCM)"""
    from math import gcd
    a_freq = rng.randint(2, 12)
    b_freq = rng.randint(2, 12)
    while b_freq == a_freq:
        b_freq = rng.randint(2, 12)
    lcm = a_freq * b_freq // gcd(a_freq, b_freq)
    event_a = rng.choice(["a market", "a bus", "a newsletter", "a ferry",
                          "a street sweeper", "a garbage truck"])
    event_b = rng.choice(["a festival", "a shuttle", "a magazine", "a barge",
                          "a recycling truck", "a street fair"])
    templates = [
        f"{event_a.capitalize()} runs every {a_freq} days and {event_b} "
        f"runs every {b_freq} days. Both ran today. In how many days will "
        f"they next coincide?",
        f"Event A occurs every {a_freq} days; event B occurs every "
        f"{b_freq} days. They both happened today. How many days until "
        f"both happen on the same day again?",
    ]
    prompt = rng.choice(templates)
    wrong1 = a_freq * b_freq  # common mistake: just multiply
    wrong2 = a_freq + b_freq
    candidates = [str(lcm), str(wrong1), str(wrong2)]
    candidates = list(dict.fromkeys(candidates))
    while len(candidates) < 4:
        candidates.append(str(lcm + rng.randint(1, 10)))
        candidates = list(dict.fromkeys(candidates))
    candidates = candidates[:4]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": str(lcm),
        "category": "temporal_frequency_coincidence",
        "tier": "A",
    }


def _temporal_sequence_reconstruction(rng: random.Random) -> dict:
    """Scrambled temporal clues — reconstruct the order of 4-5 events."""
    n = rng.randint(4, 5)
    names = rng.sample(_NAMES[:10], n)
    # Ground truth order: names[0] < names[1] < ... < names[n-1]
    ordered = list(names)
    # Build relational clues (enough to fully determine order)
    clues = []
    for i in range(n - 1):
        templates = [
            f"{ordered[i]} happened before {ordered[i+1]}",
            f"{ordered[i+1]} occurred after {ordered[i]}",
            f"{ordered[i]} preceded {ordered[i+1]}",
        ]
        clues.append(rng.choice(templates))
    rng.shuffle(clues)
    clue_str = ". ".join(clues)
    correct_order = ", ".join(ordered)
    prompt = f"{clue_str}. What is the correct chronological order?"
    # Build distractors
    reversed_order = ", ".join(reversed(ordered))
    shuffled = list(ordered)
    rng.shuffle(shuffled)
    shuffled_order = ", ".join(shuffled)
    candidates = list(dict.fromkeys([correct_order, reversed_order, shuffled_order]))
    while len(candidates) < 4:
        s = list(ordered)
        rng.shuffle(s)
        candidates.append(", ".join(s))
        candidates = list(dict.fromkeys(candidates))
    candidates = candidates[:4]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct_order,
        "category": "temporal_sequence_reconstruction",
        "tier": "A",
    }


def _temporal_duration_across_midnight(rng: random.Random) -> dict:
    """Meeting starts before midnight, ends after. How long?"""
    start_h = rng.randint(9, 11)  # PM
    start_m = rng.choice([0, 15, 30, 45])
    end_h = rng.randint(1, 4)     # AM
    end_m = rng.choice([0, 15, 30, 45])
    # start_h PM → start_h + 12 in 24hr; end_h AM → end_h in 24hr
    # Duration: (end_h - (start_h + 12) + 24) hours converted to minutes + minute diff
    dur_total = (end_h + 24 - (start_h + 12)) * 60 + (end_m - start_m)
    hours = dur_total // 60
    mins = dur_total % 60
    if mins == 0:
        correct = f"{hours} hours"
    else:
        correct = f"{hours} hours and {mins} minutes"
    activity = rng.choice(["meeting", "shift", "study session",
                           "movie marathon", "party"])
    templates = [
        f"A {activity} starts at {start_h}:{start_m:02d} PM and ends at "
        f"{end_h}:{end_m:02d} AM. How long does it last?",
        f"If a {activity} begins at {start_h}:{start_m:02d} PM and "
        f"finishes at {end_h}:{end_m:02d} AM the next day, what is its duration?",
    ]
    prompt = rng.choice(templates)
    # Distractors: naive subtraction (negative→wrong), off by 12
    wrong1_total = abs((end_h * 60 + end_m) - (start_h * 60 + start_m))
    w1h, w1m = wrong1_total // 60, wrong1_total % 60
    wrong1 = f"{w1h} hours and {w1m} minutes" if w1m else f"{w1h} hours"
    wrong2_total = dur_total + 60
    w2h, w2m = wrong2_total // 60, wrong2_total % 60
    wrong2 = f"{w2h} hours and {w2m} minutes" if w2m else f"{w2h} hours"
    candidates = list(dict.fromkeys([correct, wrong1, wrong2]))
    while len(candidates) < 4:
        fake = dur_total + rng.choice([-30, 30, 60, -60])
        if fake > 0:
            fh, fm = fake // 60, fake % 60
            candidates.append(f"{fh} hours and {fm} minutes" if fm else f"{fh} hours")
        candidates = list(dict.fromkeys(candidates))
    candidates = candidates[:4]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "temporal_duration_across_midnight",
        "tier": "A",
    }


def _temporal_relative_day(rng: random.Random) -> dict:
    """Today is X. What day is <relative expression>?"""
    today_idx = rng.randint(0, 6)
    today = _DAYS[today_idx]
    expressions = [
        ("the day after the day before yesterday",
         lambda i: (i - 2 + 1) % 7),  # yesterday-1 +1 = i-1
        ("the day before the day after tomorrow",
         lambda i: (i + 2 - 1) % 7),  # tomorrow+1 -1 = i+1
        ("two days after the day before yesterday",
         lambda i: (i - 1 + 2) % 7),  # i-1 +2 = i+1
        ("three days before the day after tomorrow",
         lambda i: (i + 2 - 3) % 7),  # i+2 -3 = i-1
        ("the day after tomorrow's yesterday",
         lambda i: (i + 2 - 1) % 7),  # day after tomorrow, then yesterday = i+1
    ]
    expr_text, fn = rng.choice(expressions)
    answer_idx = fn(today_idx)
    correct = _DAYS[answer_idx]
    prompt = f"Today is {today}. What day is {expr_text}?"
    candidates = list(dict.fromkeys([correct, today,
                                      _DAYS[(answer_idx + 1) % 7],
                                      _DAYS[(answer_idx - 1) % 7]]))
    candidates = candidates[:4]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "temporal_relative_day",
        "tier": "A",
    }


def _temporal_rate_of_change(rng: random.Random) -> dict:
    """Given a sequence, is the rate of change accelerating or decelerating?"""
    measure = rng.choice(["population", "revenue", "temperature",
                          "website visits", "production output"])
    base = rng.randint(50, 200)
    # Accelerating: increasing increments
    # Decelerating: decreasing increments
    accelerating = rng.choice([True, False])
    if accelerating:
        d1 = rng.randint(5, 15)
        d2 = d1 + rng.randint(3, 15)
        d3 = d2 + rng.randint(3, 15)
    else:
        d1 = rng.randint(15, 30)
        d2 = d1 - rng.randint(3, 10)
        d3 = d2 - rng.randint(1, max(1, d2 - 2))
        if d3 < 1:
            d3 = 1
    vals = [base, base + d1, base + d1 + d2, base + d1 + d2 + d3]
    years = [2020, 2021, 2022, 2023]
    desc = ", ".join(f"{y}: {v}" for y, v in zip(years, vals))
    correct = "Accelerating" if accelerating else "Decelerating"
    templates = [
        f"The {measure} over four years was: {desc}. Is the growth rate "
        f"accelerating or decelerating?",
        f"Given these {measure} figures — {desc} — is the rate of increase "
        f"speeding up or slowing down?",
    ]
    prompt = rng.choice(templates)
    candidates = ["Accelerating", "Decelerating", "Constant", "Cannot determine"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "temporal_rate_of_change",
        "tier": "A",
    }


def _temporal_causal_ordering(rng: random.Random) -> dict:
    """Multi-event narrative. Identify the earliest event."""
    scenarios = [
        {
            "narrative": (
                "The bridge collapsed on {day3}. Before that, it rained "
                "heavily for three days starting {day2}. Before the rain, "
                "an inspection on {day1} found cracks in the supports."
            ),
            "events": ["the inspection finding cracks", "the heavy rain starting",
                       "the bridge collapsing"],
            "earliest_idx": 0,
        },
        {
            "narrative": (
                "The server crashed at {day3}. Earlier, a patch was deployed "
                "at {day2}. Before the patch, a vulnerability was reported "
                "on {day1}."
            ),
            "events": ["the vulnerability report", "the patch deployment",
                       "the server crash"],
            "earliest_idx": 0,
        },
        {
            "narrative": (
                "The patient recovered on {day3}. Treatment began on {day2}. "
                "The diagnosis was made on {day1}."
            ),
            "events": ["the diagnosis", "treatment beginning",
                       "the patient's recovery"],
            "earliest_idx": 0,
        },
    ]
    s = rng.choice(scenarios)
    day1 = f"Day {rng.randint(1, 5)}"
    day2 = f"Day {rng.randint(6, 10)}"
    day3 = f"Day {rng.randint(11, 15)}"
    prompt_text = s["narrative"].format(day1=day1, day2=day2, day3=day3)
    prompt = f"{prompt_text} What was the earliest event?"
    correct = s["events"][s["earliest_idx"]]
    candidates = list(s["events"]) + ["Cannot determine"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "temporal_causal_ordering",
        "tier": "A",
    }


def _temporal_scheduling_conflict(rng: random.Random) -> dict:
    """Two meetings — do they overlap?"""
    m1_start = rng.randint(8, 15)
    m1_dur = rng.randint(1, 3)
    m1_end = m1_start + m1_dur
    # Sometimes overlapping, sometimes not
    overlap = rng.choice([True, False])
    if overlap:
        m2_start = rng.randint(m1_start, m1_end - 1)
        m2_dur = rng.randint(1, 3)
    else:
        m2_start = m1_end + rng.randint(0, 2)
        m2_dur = rng.randint(1, 3)
    m2_end = m2_start + m2_dur
    actual_overlap = m2_start < m1_end and m1_start < m2_end
    correct = "No" if actual_overlap else "Yes"
    label_a = rng.choice(["Meeting A", "Workshop", "Seminar"])
    label_b = rng.choice(["Meeting B", "Lecture", "Training"])
    templates = [
        (f"{label_a} runs from {m1_start}:00 to {m1_end}:00. "
         f"{label_b} runs from {m2_start}:00 to {m2_end}:00. "
         f"Can you attend both in full?"),
        (f"You have {label_a} ({m1_start}:00-{m1_end}:00) and "
         f"{label_b} ({m2_start}:00-{m2_end}:00). "
         f"Is it possible to attend both completely?"),
    ]
    prompt = rng.choice(templates)
    candidates = ["Yes", "No"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "temporal_scheduling_conflict",
        "tier": "A",
    }


def _temporal_age_reasoning(rng: random.Random) -> dict:
    """Multi-step age reasoning with relational clues."""
    names = rng.sample(_NAMES[:10], 3)
    a, b, c = names
    c_age = rng.randint(3, 10)
    multiplier = rng.randint(2, 3)
    b_age = c_age * multiplier
    diff = rng.randint(1, 8)
    a_age = b_age + diff
    templates = [
        (f"{a} is {diff} years older than {b}. {b} is {multiplier} times "
         f"{c}'s age. {c} is {c_age}. How old is {a}?"),
        (f"{c} is {c_age} years old. {b} is {multiplier} times as old as "
         f"{c}. {a} is {diff} years older than {b}. What is {a}'s age?"),
    ]
    prompt = rng.choice(templates)
    correct = str(a_age)
    candidates = [correct, str(b_age), str(a_age - 1), str(a_age + diff)]
    candidates = list(dict.fromkeys(candidates))[:4]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "temporal_age_reasoning",
        "tier": "A",
    }


# ===================================================================
# PHASE 5 — Causal Expansion (3→10)
# ===================================================================

def _causal_intervention(rng: random.Random) -> dict:
    """In X→Y→Z, if we force Y=0, what happens to Z?"""
    chains = [
        ("rain", "wet ground", "puddles forming",
         "Puddles stop forming", "Puddles still form"),
        ("exercise", "calorie burn", "weight loss",
         "Weight loss stops", "Weight loss continues"),
        ("advertising", "brand awareness", "increased sales",
         "Sales increase stops", "Sales still increase"),
        ("studying", "understanding", "passing the exam",
         "Passing the exam is unlikely", "Passing still happens"),
    ]
    x, y, z, correct_text, wrong_text = rng.choice(chains)
    templates = [
        (f"In a system where {x} causes {y}, and {y} causes {z}, "
         f"if we forcibly prevent {y}, what happens to {z}?"),
        (f"{x.capitalize()} leads to {y}, which leads to {z}. "
         f"If we intervene to block {y}, what is the effect on {z}?"),
    ]
    prompt = rng.choice(templates)
    candidates = [correct_text, wrong_text,
                  f"{x.capitalize()} directly causes {z}",
                  "Cannot determine"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct_text,
        "category": "causal_intervention",
        "tier": "A",
    }


def _causal_confounding(rng: random.Random) -> dict:
    """X and Y correlate due to common cause Z. Does X cause Y?"""
    scenarios = [
        ("ice cream sales", "drowning incidents", "hot summer weather"),
        ("umbrella sales", "car accidents", "rainy weather"),
        ("sunglasses purchases", "sunburn cases", "sunny weather"),
        ("hot chocolate sales", "flu cases", "cold winter weather"),
        ("air conditioning usage", "electricity bills", "high temperatures"),
    ]
    x, y, z = rng.choice(scenarios)
    templates = [
        (f"Data shows that {x} and {y} both increase at the same time. "
         f"Does increasing {x} cause more {y}?"),
        (f"A study finds a strong correlation between {x} and {y}. "
         f"Can we conclude that {x} causes {y}?"),
    ]
    prompt = rng.choice(templates)
    correct = f"No, both are likely caused by a confounding variable ({z})"
    candidates = [
        correct,
        f"Yes, the correlation is strong enough",
        f"Yes, {x} clearly drives {y}",
        "More data is needed before any conclusion",
    ]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "causal_confounding",
        "tier": "A",
    }


def _causal_chain_length(rng: random.Random) -> dict:
    """A→B→C→...→N. If A happens, does N happen?"""
    length = rng.randint(3, 6)
    pool = rng.sample([
        "the alarm sounds", "the guard wakes up", "the door is locked",
        "the light turns on", "the camera activates", "the siren blares",
        "the police are called", "the intruder flees", "the gate closes",
    ], min(length + 1, 9))
    while len(pool) < length + 1:
        pool.append(f"step {len(pool)} triggers")
    chain = pool[:length + 1]
    links = [f"If {chain[i]}, then {chain[i+1]}" for i in range(length)]
    rng.shuffle(links)
    prompt = (". ".join(links) + f". Suppose {chain[0]}. "
              f"Does it follow that {chain[-1]}?")
    candidates = ["Yes", "No", "Only if the chain is unbroken", "Cannot determine"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": "Yes",
        "category": "causal_chain_length",
        "tier": "A",
    }


def _causal_counterfactual(rng: random.Random) -> dict:
    """If a rule applies universally, what would happen counterfactually?"""
    scenarios = [
        {
            "rule": "All employees who arrived late were fined $50",
            "fact": "{name} was not fined",
            "counter": "If {name} had arrived late, would {name} have been fined?",
            "correct": "Yes",
        },
        {
            "rule": "Every student who submitted late received a penalty",
            "fact": "{name} received no penalty",
            "counter": "If {name} had submitted late, would {name} have received a penalty?",
            "correct": "Yes",
        },
        {
            "rule": "All packages over 10 kg require a signature",
            "fact": "{name}'s package did not require a signature",
            "counter": "If {name}'s package had been over 10 kg, would it have required a signature?",
            "correct": "Yes",
        },
    ]
    s = rng.choice(scenarios)
    name = rng.choice(_NAMES[:8])
    prompt = (f"{s['rule']}. {s['fact'].format(name=name)}. "
              f"{s['counter'].format(name=name)}")
    candidates = ["Yes", "No", "Cannot determine", "Only if other conditions are met"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": s["correct"],
        "category": "causal_counterfactual",
        "tier": "A",
    }


def _causal_necessary_sufficient_extended(rng: random.Random) -> dict:
    """Necessary but not sufficient condition — having it doesn't guarantee outcome."""
    scenarios = [
        {
            "necessary": "water",
            "outcome": "plant growth",
            "also_needs": "sunlight and soil nutrients",
            "has": "water",
        },
        {
            "necessary": "fuel",
            "outcome": "a car running",
            "also_needs": "a working engine and battery",
            "has": "fuel",
        },
        {
            "necessary": "flour",
            "outcome": "baking bread",
            "also_needs": "yeast, water, and heat",
            "has": "flour",
        },
        {
            "necessary": "electricity",
            "outcome": "a computer working",
            "also_needs": "functioning hardware and an operating system",
            "has": "electricity",
        },
    ]
    s = rng.choice(scenarios)
    templates = [
        (f"{s['necessary'].capitalize()} is necessary for {s['outcome']}. "
         f"A system has {s['has']}. Is {s['outcome']} guaranteed?"),
        (f"Without {s['necessary']}, {s['outcome']} is impossible. "
         f"Given that {s['necessary']} is present, must {s['outcome']} occur?"),
    ]
    prompt = rng.choice(templates)
    correct = f"No, {s['also_needs']} are also needed"
    candidates = [
        correct,
        f"Yes, {s['necessary']} is sufficient",
        "Cannot determine",
        f"Only if {s['necessary']} is abundant",
    ]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "causal_necessary_sufficient_extended",
        "tier": "A",
    }


def _causal_simpson_paradox(rng: random.Random) -> dict:
    """Numeric table where a trend reverses when subgroups are combined."""
    # Treatment A vs B across two groups
    # Group 1: A=80/100 (80%), B=85/100 (85%) — B better
    # Group 2: A=5/10 (50%), B=50/100 (50%) — tied → A and B same
    # Combined: A=85/110 (77.3%), B=135/200 (67.5%) — A better overall
    # Simplified with random scaling
    name_a = rng.choice(["Treatment A", "Drug X", "Method Alpha", "Program P"])
    name_b = rng.choice(["Treatment B", "Drug Y", "Method Beta", "Program Q"])
    # Group 1 (large): B wins
    g1_a_success = rng.randint(70, 85)
    g1_a_total = 100
    g1_b_success = g1_a_success + rng.randint(3, 10)
    g1_b_total = 100
    # Group 2 (small for A, large for B): A wins or ties
    g2_a_total = rng.randint(8, 15)
    g2_a_success = rng.randint(g2_a_total // 2, g2_a_total - 1)
    g2_b_total = rng.randint(80, 120)
    # Make B's rate in group 2 lower than A's group 2 rate
    g2_a_rate = g2_a_success / g2_a_total
    g2_b_success = int(g2_b_total * (g2_a_rate - 0.1))
    if g2_b_success < 1:
        g2_b_success = 1
    # Compute combined
    total_a = g1_a_success + g2_a_success
    total_a_n = g1_a_total + g2_a_total
    total_b = g1_b_success + g2_b_success
    total_b_n = g1_b_total + g2_b_total
    rate_a = total_a / total_a_n
    rate_b = total_b / total_b_n
    # Determine which is actually better when combined
    if rate_a > rate_b:
        combined_winner = name_a
    else:
        combined_winner = name_b
    prompt = (
        f"Group 1: {name_a} succeeded in {g1_a_success}/{g1_a_total} cases, "
        f"{name_b} in {g1_b_success}/{g1_b_total}. "
        f"Group 2: {name_a} succeeded in {g2_a_success}/{g2_a_total}, "
        f"{name_b} in {g2_b_success}/{g2_b_total}. "
        f"{name_b} has a higher success rate in BOTH groups. "
        f"When combined, which treatment has the higher overall success rate?"
    )
    correct = combined_winner
    candidates = [name_a, name_b, "They are equal", "Cannot determine"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "causal_simpson_paradox",
        "tier": "A",
    }


def _causal_common_cause(rng: random.Random) -> dict:
    """Both A and B increased — does A cause B? Common cause possible."""
    pairs = [
        ("rooftop solar installations", "electric vehicle purchases",
         "government green-energy subsidies"),
        ("coffee shop openings", "coworking space growth",
         "rising remote work trends"),
        ("gym memberships", "protein supplement sales",
         "a New Year fitness craze"),
        ("reading glasses sales", "hearing aid sales",
         "an aging population"),
    ]
    a, b, c = rng.choice(pairs)
    templates = [
        (f"Over the past decade, both {a} and {b} have increased sharply. "
         f"Does this mean {a} caused the rise in {b}?"),
        (f"Statistics show that {a} and {b} both surged in recent years. "
         f"Can we conclude a causal link from {a} to {b}?"),
    ]
    prompt = rng.choice(templates)
    correct = f"Not necessarily — a common cause like {c} could explain both"
    candidates = [
        correct,
        f"Yes, the parallel trends prove causation",
        f"Yes, {a} clearly drives {b}",
        "No, they are completely unrelated",
    ]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "causal_common_cause",
        "tier": "B",
    }


# ===================================================================
# PHASE 5 — Theory of Mind Expansion (3→10)
# ===================================================================

def _tom_second_order_belief(rng: random.Random) -> dict:
    """Alice thinks Bob thinks X. Where does Alice expect Bob to look?"""
    names = rng.sample(_NAMES[:8], 2)
    alice, bob = names
    obj = rng.choice(_OBJECTS[:8])
    loc1, loc2 = rng.sample(_LOCATIONS[:6], 2)
    templates = [
        (f"{alice} thinks {bob} believes the {obj} is in the {loc1}. "
         f"Where does {alice} expect {bob} to look for the {obj}?"),
        (f"According to {alice}'s understanding, {bob} thinks the {obj} "
         f"is in the {loc1}. Where will {alice} predict {bob} searches?"),
    ]
    prompt = rng.choice(templates)
    correct = f"The {loc1}"
    candidates = [f"The {loc1}", f"The {loc2}",
                  "Both places", "Neither place"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "tom_second_order_belief",
        "tier": "A",
    }


def _tom_information_asymmetry(rng: random.Random) -> dict:
    """You know something is rigged. An uninformed person assigns default probability."""
    name = rng.choice(_NAMES[:8])
    setups = [
        {
            "object": "six-sided die", "rigged_to": "always land on 6",
            "fair_answer": "1/6 (any face equally likely)",
        },
        {
            "object": "coin", "rigged_to": "always land on heads",
            "fair_answer": "50% heads, 50% tails",
        },
        {
            "object": "roulette wheel", "rigged_to": "always land on red",
            "fair_answer": "Roughly equal chance of any color",
        },
        {
            "object": "deck of cards", "rigged_to": "always deal an ace on top",
            "fair_answer": "1/52 chance of any specific card",
        },
    ]
    s = rng.choice(setups)
    templates = [
        (f"You know that a {s['object']} is rigged to {s['rigged_to']}. "
         f"{name} has no idea it is rigged. What probability does {name} "
         f"assign to the outcome?"),
        (f"A {s['object']} has been tampered with to {s['rigged_to']}. "
         f"You know this, but {name} does not. What does {name} expect?"),
    ]
    prompt = rng.choice(templates)
    correct = s["fair_answer"]
    candidates = [correct, f"100% (always the rigged outcome)",
                  "0%", "Cannot determine"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "tom_information_asymmetry",
        "tier": "A",
    }


def _tom_strategic_deception(rng: random.Random) -> dict:
    """Alice knows Bob does the opposite. What should Alice say?"""
    names = rng.sample(_NAMES[:8], 2)
    alice, bob = names
    options = [
        ("go left", "go right", "Go right"),
        ("take the stairs", "take the elevator", "Take the elevator"),
        ("pick the red box", "pick the blue box", "Pick the blue box"),
        ("eat at the Italian place", "eat at the Chinese place",
         "Eat at the Chinese place"),
    ]
    desired, opposite, say_text = rng.choice(options)
    templates = [
        (f"{alice} wants {bob} to {desired}. {alice} knows {bob} always "
         f"does the opposite of what she says. What should {alice} tell "
         f"{bob} to do?"),
        (f"If {alice} wants {bob} to {desired}, and {bob} reliably does "
         f"the opposite of {alice}'s suggestion, what should {alice} say?"),
    ]
    prompt = rng.choice(templates)
    correct = say_text
    # The correct answer is to say the opposite of what you want
    wrong1 = desired.capitalize()
    candidates = [correct, wrong1, "Say nothing", "It doesn't matter"]
    candidates = list(dict.fromkeys(candidates))[:4]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "tom_strategic_deception",
        "tier": "A",
    }


def _tom_group_knowledge(rng: random.Random) -> dict:
    """Common knowledge vs mutual knowledge."""
    names = rng.sample(_NAMES[:8], 3)
    a, b, c = names
    secret = rng.choice(["the surprise party", "the project deadline change",
                         "the office relocation", "the bonus announcement"])
    templates = [
        (f"{a}, {b}, and {c} are in a room. An announcement about "
         f"{secret} is made so everyone hears it. Does {a} know that "
         f"{b} knows about {secret}?"),
        (f"All three — {a}, {b}, and {c} — hear a public announcement "
         f"about {secret}. Can {a} be certain that {b} also knows?"),
    ]
    prompt = rng.choice(templates)
    correct = "Yes, it is common knowledge since all heard it publicly"
    candidates = [
        correct,
        f"No, {a} only knows their own knowledge",
        "Only if they discussed it afterward",
        "Cannot determine",
    ]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "tom_group_knowledge",
        "tier": "B",
    }


def _tom_perspective_shift(rng: random.Random) -> dict:
    """Spatial perspective: object on Alice's left is on Bob's right if facing her."""
    names = rng.sample(_NAMES[:8], 2)
    alice, bob = names
    obj = rng.choice(["painting", "window", "clock", "poster", "door",
                      "bookshelf", "whiteboard"])
    side = rng.choice(["left", "right"])
    opposite = "right" if side == "left" else "left"
    templates = [
        (f"From {alice}'s seat, the {obj} is on the {side}. {bob} sits "
         f"directly across from {alice}, facing her. From {bob}'s "
         f"perspective, which side is the {obj} on?"),
        (f"{alice} sees the {obj} on her {side}. {bob} faces {alice} from "
         f"the opposite side of the table. On which side does {bob} see "
         f"the {obj}?"),
    ]
    prompt = rng.choice(templates)
    correct = f"{bob}'s {opposite}"
    candidates = [f"{bob}'s left", f"{bob}'s right",
                  "The same side", "Cannot determine"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "tom_perspective_shift",
        "tier": "A",
    }


def _tom_mistaken_belief_chain(rng: random.Random) -> dict:
    """Misinformation propagated through a chain of people."""
    names = rng.sample(_NAMES[:8], 3)
    a, b, c = names
    wrong_val = rng.choice(["3 PM", "Tuesday", "Room 101", "$50"])
    right_val = rng.choice(["4 PM", "Wednesday", "Room 202", "$75"])
    topic = rng.choice(["the meeting time", "the event day",
                        "the room number", "the registration fee"])
    templates = [
        (f"{a} told {b} that {topic} is {wrong_val}. Actually, {topic} "
         f"is {right_val}. {b} then told {c} what {a} said. "
         f"What does {c} think {topic} is?"),
        (f"{a} mistakenly believes {topic} is {wrong_val} (it's really "
         f"{right_val}). {a} tells {b}, and {b} passes it to {c}. "
         f"What value does {c} hold for {topic}?"),
    ]
    prompt = rng.choice(templates)
    correct = wrong_val
    candidates = [wrong_val, right_val,
                  "Cannot determine", "Somewhere in between"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "tom_mistaken_belief_chain",
        "tier": "A",
    }


def _tom_intention_reading(rng: random.Random) -> dict:
    """Infer a belief from an observable action."""
    name = rng.choice(_NAMES[:8])
    scenarios = [
        {
            "action": f"{name} brought an umbrella on a sunny day",
            "belief": f"{name} believed it might rain later",
            "wrong1": f"{name} enjoys carrying umbrellas",
            "wrong2": f"{name} thinks it is currently raining",
        },
        {
            "action": f"{name} packed a heavy coat for a trip to the tropics",
            "belief": f"{name} expected cold weather or indoor air conditioning",
            "wrong1": f"{name} likes wearing coats in hot weather",
            "wrong2": f"{name} was not paying attention to the forecast",
        },
        {
            "action": f"{name} studied all night before an exam",
            "belief": f"{name} believed preparation was needed to do well",
            "wrong1": f"{name} had nothing else to do",
            "wrong2": f"{name} already knew the material perfectly",
        },
        {
            "action": f"{name} locked the door twice before leaving",
            "belief": f"{name} was worried about security",
            "wrong1": f"{name} enjoys locking doors",
            "wrong2": f"{name} forgot whether the door was locked",
        },
    ]
    s = rng.choice(scenarios)
    templates = [
        f"{s['action']}. What can we most reasonably infer about {name}'s belief?",
        f"Observation: {s['action']}. What does this suggest {name} was thinking?",
    ]
    prompt = rng.choice(templates)
    correct = s["belief"]
    candidates = [correct, s["wrong1"], s["wrong2"], "Nothing can be inferred"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "tom_intention_reading",
        "tier": "B",
    }


# ===================================================================
# PHASE 5 — Compositional Reasoning (8 categories)
# ===================================================================

def _compositional_logic_arithmetic(rng: random.Random) -> dict:
    """Arithmetic embedded in logical premises."""
    a = rng.randint(1, 10)
    b = rng.randint(1, 10)
    s = a + b
    threshold = rng.randint(s - 3, s + 3)
    if threshold == s:
        threshold = s - 1  # ensure definite answer
    result = s > threshold
    correct = "Yes" if result else "No"
    templates = [
        (f"If X > {threshold} and X is the sum of {a} and {b}, is X > {threshold}?"),
        (f"Let X = {a} + {b}. Given the rule 'if X > {threshold} then the "
         f"alarm sounds,' does the alarm sound?"),
    ]
    prompt = rng.choice(templates)
    if "alarm" in prompt:
        correct = "Yes" if result else "No"
    candidates = ["Yes", "No"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "compositional_logic_arithmetic",
        "tier": "A",
    }


def _compositional_temporal_causal(rng: random.Random) -> dict:
    """Combine temporal ordering with causal counterfactual reasoning."""
    chains = [
        ("the factory emitted pollutants", "the river was contaminated",
         "fish in the river died", "the downstream village lost its food source"),
        ("the storm hit", "the power lines fell",
         "the hospital lost electricity", "the backup generator activated"),
        ("the developer pushed buggy code", "the app crashed",
         "users filed complaints", "the company issued a public apology"),
    ]
    c = rng.choice(chains)
    prompt = (
        f"{c[0].capitalize()} caused {c[1]}. {c[1].capitalize()} happened "
        f"before {c[2]}. {c[2].capitalize()} caused {c[3]}. "
        f"If {c[0]} had not happened, would {c[3]} have occurred?"
    )
    correct = "No, the causal chain would have been broken at the start"
    candidates = [
        correct,
        "Yes, the later events are independent",
        f"Only {c[3]} would still happen",
        "Cannot determine",
    ]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "compositional_temporal_causal",
        "tier": "A",
    }


def _compositional_logic_tom(rng: random.Random) -> dict:
    """Logic applied within a ToM frame."""
    name = rng.choice(_NAMES[:8])
    animal = rng.choice(["cats", "dogs", "birds", "fish"])
    category = rng.choice(["animals", "pets", "living things", "vertebrates"])
    instance = rng.choice(["a tabby", "a poodle", "a parrot", "a goldfish"])
    # Map instance to matching animal
    mapping = {"a tabby": "cats", "a poodle": "dogs",
               "a parrot": "birds", "a goldfish": "fish"}
    # Pick an instance that matches the animal
    matching_instances = [k for k, v in mapping.items() if v == animal]
    instance = rng.choice(matching_instances) if matching_instances else instance
    templates = [
        (f"{name} believes that all {animal} are {category}. {name} sees "
         f"{instance}. What does {name} believe about {instance}?"),
        (f"In {name}'s worldview, every member of {animal} is a member of "
         f"{category}. {name} encounters {instance}. What conclusion does "
         f"{name} draw?"),
    ]
    prompt = rng.choice(templates)
    correct = f"{name} believes {instance} is {category}"
    candidates = [
        correct,
        f"{name} is uncertain about {instance}",
        f"{name} thinks {instance} is not {category}",
        f"{name} has no opinion about {instance}",
    ]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "compositional_logic_tom",
        "tier": "A",
    }


def _compositional_arithmetic_temporal(rng: random.Random) -> dict:
    """Classic train-catch-up problem combining arithmetic with time."""
    speed_a = rng.choice([40, 50, 60, 70, 80])
    speed_b = speed_a + rng.choice([10, 20, 30, 40])
    head_start_hours = rng.randint(1, 3)
    # B catches A when: speed_b * t = speed_a * (t + head_start_hours)
    # t = speed_a * head_start_hours / (speed_b - speed_a)
    gap = speed_b - speed_a
    distance_head = speed_a * head_start_hours
    # Time for B to catch up
    # Make sure it divides evenly
    while distance_head % gap != 0:
        speed_a = rng.choice([40, 50, 60, 80])
        speed_b = speed_a + rng.choice([10, 20, 40])
        head_start_hours = rng.randint(1, 3)
        gap = speed_b - speed_a
        distance_head = speed_a * head_start_hours
    t_catch = distance_head // gap
    depart_a = rng.randint(1, 4)  # PM hour
    depart_b = depart_a + head_start_hours
    catch_time = depart_b + t_catch
    # Convert to 12-hour display (depart is PM, so catch_time is hours from noon+)
    if catch_time <= 12:
        catch_display = f"{catch_time}:00 PM"
    else:
        h = catch_time - 12
        catch_display = f"{h}:00 AM" if h != 0 else "12:00 AM"

    prompt = (
        f"Train A leaves at {depart_a}:00 PM traveling at {speed_a} mph. "
        f"Train B leaves from the same station at {depart_b}:00 PM traveling "
        f"at {speed_b} mph in the same direction. "
        f"When does Train B catch Train A?"
    )
    correct = catch_display
    # Distractors
    wrong1 = f"{catch_time + 1}:00 PM" if catch_time + 1 <= 12 else f"{catch_time + 1 - 12}:00 AM"
    wrong2 = f"{depart_b + t_catch + 2}:00 PM"
    candidates = list(dict.fromkeys([correct, wrong1, wrong2, "They never meet"]))[:4]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "compositional_arithmetic_temporal",
        "tier": "A",
    }


def _compositional_causal_statistical(rng: random.Random) -> dict:
    """Simpson's paradox in a causal framing — which treatment is actually better?"""
    drug_a = rng.choice(["Drug X", "Treatment Alpha", "Vaccine A"])
    drug_b = rng.choice(["Drug Y", "Treatment Beta", "Vaccine B"])
    # Mild cases: Drug A given mostly here → high rate
    a_mild_success = rng.randint(85, 95)
    a_mild_total = 100
    b_mild_success = rng.randint(80, 90)
    b_mild_total = rng.randint(8, 15)
    # Severe cases: Drug B given mostly here → looks worse
    a_severe_total = rng.randint(8, 15)
    a_severe_success = rng.randint(3, a_severe_total - 1)
    b_severe_total = 100
    b_severe_success = rng.randint(40, 60)
    # Rates within groups
    a_mild_rate = a_mild_success / a_mild_total
    b_mild_rate = b_mild_success / b_mild_total
    a_severe_rate = a_severe_success / a_severe_total
    b_severe_rate = b_severe_success / b_severe_total
    # Make B better in both subgroups
    if b_mild_rate <= a_mild_rate:
        b_mild_success = int(a_mild_rate * b_mild_total) + 1
        if b_mild_success > b_mild_total:
            b_mild_success = b_mild_total
    if b_severe_rate <= a_severe_rate:
        b_severe_success = int(a_severe_rate * b_severe_total) + 1
    prompt = (
        f"{drug_a} was given mostly to mild cases: {a_mild_success}/{a_mild_total} "
        f"mild patients cured, {a_severe_success}/{a_severe_total} severe patients "
        f"cured. {drug_b} was given mostly to severe cases: "
        f"{b_mild_success}/{b_mild_total} mild patients cured, "
        f"{b_severe_success}/{b_severe_total} severe patients cured. "
        f"{drug_a}'s overall cure rate looks higher. Which drug is actually "
        f"more effective when accounting for severity?"
    )
    correct = f"{drug_b}, it has a higher cure rate in both subgroups"
    candidates = [
        correct,
        f"{drug_a}, because its overall rate is higher",
        "They are equally effective",
        "Cannot determine without more data",
    ]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "compositional_causal_statistical",
        "tier": "A",
    }


def _compositional_multi_hop_with_distractor(rng: random.Random) -> dict:
    """Logic chain + irrelevant premise as distractor."""
    cat_a = rng.choice(["widgets", "bloops", "zargs", "plonks"])
    cat_b = rng.choice(["gadgets", "flerps", "norks", "trinkets"])
    cat_c = rng.choice(["devices", "glorps", "whizzles", "contraptions"])
    name = rng.choice(_NAMES[:8])
    distractors = [
        "The sky is blue.",
        "Water freezes at 0 degrees Celsius.",
        f"The capital of France is Paris.",
        f"{rng.choice(_NAMES[:8])} enjoys hiking.",
        "There are 365 days in a common year.",
    ]
    distractor = rng.choice(distractors)
    # Insert distractor at random position in premise list
    premises = [f"All {cat_a} are {cat_b}", f"All {cat_b} are {cat_c}"]
    insert_pos = rng.randint(0, len(premises))
    premises.insert(insert_pos, distractor)
    premises.append(f"{name}'s item is a {cat_a[:-1] if cat_a.endswith('s') else cat_a}")
    premise_str = ". ".join(premises)
    singular_c = cat_c[:-1] if cat_c.endswith('s') else cat_c
    prompt = f"{premise_str}. Is {name}'s item a {singular_c}?"
    candidates = ["Yes", "No", "Cannot determine",
                  "Only if the distractor is relevant"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": "Yes",
        "category": "compositional_multi_hop_with_distractor",
        "tier": "A",
    }


def _compositional_nested_tom_logic(rng: random.Random) -> dict:
    """Alice thinks X. Bob thinks Alice is wrong. Check against reality."""
    names = rng.sample(_NAMES[:8], 2)
    alice, bob = names
    contents = rng.choice(["a cat", "a book", "a diamond", "a letter"])
    obj = rng.choice(["box", "safe", "drawer", "chest"])
    templates = [
        (f"{alice} thinks the {obj} contains {contents}. {bob} thinks "
         f"{alice} is wrong. If the {obj} actually contains {contents}, "
         f"who is correct?"),
        (f"{alice} believes there is {contents} in the {obj}. {bob} "
         f"disagrees with {alice}. It turns out the {obj} does contain "
         f"{contents}. Who was right?"),
    ]
    prompt = rng.choice(templates)
    correct = alice
    candidates = [alice, bob, "Both", "Neither"]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "compositional_nested_tom_logic",
        "tier": "A",
    }


def _compositional_depth_scaling(rng: random.Random) -> dict:
    """Chain N heterogeneous reasoning steps, N from 2 to 8."""
    n_steps = rng.randint(2, 8)
    start_val = rng.randint(1, 10)
    step_types = ["add", "multiply", "conditional"]

    # Pre-generate step parameters, then compute the answer
    step_specs = []
    for _ in range(n_steps):
        stype = rng.choice(step_types)
        if stype == "add":
            step_specs.append(("add", rng.randint(1, 10)))
        elif stype == "multiply":
            step_specs.append(("multiply", rng.randint(2, 3)))
        else:
            step_specs.append(("conditional", None))

    # Build descriptions and compute final value
    v = start_val
    step_descs = []
    for stype, param in step_specs:
        if stype == "add":
            step_descs.append(f"add {param}")
            v += param
        elif stype == "multiply":
            step_descs.append(f"multiply by {param}")
            v *= param
        elif stype == "conditional":
            if v % 2 == 0:
                step_descs.append("if the current value is even, subtract 1; otherwise do nothing")
                v -= 1
            else:
                step_descs.append("if the current value is odd, add 1; otherwise do nothing")
                v += 1

    numbered = ". ".join(f"Step {i+1}: {s}" for i, s in enumerate(step_descs))
    prompt = (f"Start with {start_val}. Apply these steps in order: "
              f"{numbered}. What is the final value?")
    correct = str(v)
    # Distractors
    candidates = [correct]
    for offset in [1, -1, 2, -2, 5]:
        c = str(v + offset)
        if c not in candidates:
            candidates.append(c)
        if len(candidates) >= 4:
            break
    candidates = candidates[:4]
    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "compositional_depth_scaling",
        "tier": "A",
    }


# ===================================================================
# Registry + battery functions
# ===================================================================

EXTENDED_GENERATORS = [
    # Phase 3 — Meta-Reasoning + Theory of Mind + Multi-Step Chain
    _validity_vs_truth,
    _argument_strength,
    _confidence_calibration,
    _self_referential_consistency,
    _liar_detection,
    _false_belief_task,
    _knowledge_attribution,
    _second_order_belief,
    _multi_hop_deduction,
    _information_sufficiency,
    _irrelevant_premise,
    _premise_contradiction,
    _chained_conditional,
    # Phase 4 — Arithmetic + Spatial + Set Theory + Remaining
    _order_of_operations,
    _modular_arithmetic,
    _fencepost,
    _inclusion_exclusion,
    _left_right_reversal,
    _direction_composition,
    _containment,
    _empty_set,
    _subset_inversion,
    _survivorship_bias,
    _sunk_cost,
    _framing_effect,
    _false_dichotomy,
    _composition_fallacy,
    _regression_to_mean,
    _affirming_consequent_numeric,
    _intention_vs_outcome,
    # Phase 5 — Temporal Expansion
    _temporal_concurrent_events,
    _temporal_frequency_coincidence,
    _temporal_sequence_reconstruction,
    _temporal_duration_across_midnight,
    _temporal_relative_day,
    _temporal_rate_of_change,
    _temporal_causal_ordering,
    _temporal_scheduling_conflict,
    _temporal_age_reasoning,
    # Phase 5 — Causal Expansion
    _causal_intervention,
    _causal_confounding,
    _causal_chain_length,
    _causal_counterfactual,
    _causal_necessary_sufficient_extended,
    _causal_simpson_paradox,
    _causal_common_cause,
    # Phase 5 — Theory of Mind Expansion
    _tom_second_order_belief,
    _tom_information_asymmetry,
    _tom_strategic_deception,
    _tom_group_knowledge,
    _tom_perspective_shift,
    _tom_mistaken_belief_chain,
    _tom_intention_reading,
    # Phase 5 — Compositional Reasoning
    _compositional_logic_arithmetic,
    _compositional_temporal_causal,
    _compositional_logic_tom,
    _compositional_arithmetic_temporal,
    _compositional_causal_statistical,
    _compositional_multi_hop_with_distractor,
    _compositional_nested_tom_logic,
    _compositional_depth_scaling,
]


def generate_extended_battery(
    n_per_category: int = 2, seed: int | None = None
) -> list[dict]:
    """Generate a battery from Phase 3-4 generators only.

    Returns list of trap dicts compatible with test_harness.run_trap_battery().
    """
    rng = random.Random(seed)
    traps: list[dict] = []
    for gen_fn in EXTENDED_GENERATORS:
        cat = gen_fn.__name__.lstrip("_")
        seen_prompts: set[str] = set()
        for _ in range(n_per_category * 3):  # oversample to avoid duplicates
            if len([t for t in traps if t.get("category") == cat]) >= n_per_category:
                break
            trap = gen_fn(rng)
            if trap["prompt"] not in seen_prompts:
                seen_prompts.add(trap["prompt"])
                traps.append(trap)
    return traps


def generate_full_battery(
    n_per_category: int = 2, seed: int | None = None
) -> list[dict]:
    """Combine base (Phase 1-2) + extended (Phase 3-4) batteries.

    Uses the same seed for both so results are reproducible.
    """
    base = generate_trap_battery(n_per_category=n_per_category, seed=seed)
    extended = generate_extended_battery(n_per_category=n_per_category, seed=seed)
    return base + extended


if __name__ == "__main__":
    battery = generate_full_battery(n_per_category=2, seed=42)
    print("=" * 72)
    print(f"Full battery: {len(battery)} traps")
    print("=" * 72)
    for t in battery:
        tier = t.get("tier", "?")
        print(f"[{t['category']:35s}] (tier {tier}) {t['prompt'][:60]}")
        print(f"  candidates = {t['candidates']}")
        print(f"  correct    = {t['correct']}")
        print()

    # Summary
    cats = {}
    for t in battery:
        cats.setdefault(t["category"], 0)
        cats[t["category"]] += 1
    print("-" * 72)
    for cat, cnt in sorted(cats.items()):
        print(f"  {cat:35s} {cnt}")
    print(f"  {'TOTAL':35s} {len(battery)}")
