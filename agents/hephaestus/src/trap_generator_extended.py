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
