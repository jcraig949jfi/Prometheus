"""Parameterized Puzzle Generator — unlimited reasoning problems that force computation.

Each generator produces {prompt, candidates, correct, category} dicts with
verifiable answers. Different seeds produce different instances. Tools that
memorize fixed problems fail on generated variants.

Usage:
    from puzzle_gen import generate_battery
    battery = generate_battery(n=50, seed=42)

    # Or individual generators:
    from puzzle_gen import constraint_satisfaction, graph_problem, ...
    problem = constraint_satisfaction(n=3, seed=99)
"""

import random
import itertools
from collections import defaultdict, deque


# ---------------------------------------------------------------------------
# 1. Constraint Satisfaction — Latin Squares
# ---------------------------------------------------------------------------

def constraint_satisfaction(n=3, seed=None):
    """Generate a random NxN Latin square with clues, ask for a missing cell.

    A Latin square has each number 1..N exactly once per row and column.
    We generate a complete solution, reveal some cells as clues, and ask
    for a specific hidden cell.
    """
    rng = random.Random(seed)

    # Generate a valid Latin square by random permutation
    base = list(range(1, n + 1))
    rows = []
    for i in range(n):
        row = base[i:] + base[:i]
        rows.append(row)

    # Shuffle rows and columns to randomize
    rng.shuffle(rows)
    cols_order = list(range(n))
    rng.shuffle(cols_order)
    grid = [[rows[r][cols_order[c]] for c in range(n)] for r in range(n)]

    # Pick a cell to hide
    hide_r, hide_c = rng.randint(0, n - 1), rng.randint(0, n - 1)
    correct = str(grid[hide_r][hide_c])

    # Build prompt with clues
    clue_lines = []
    for r in range(n):
        row_str = []
        for c in range(n):
            if r == hide_r and c == hide_c:
                row_str.append("_")
            else:
                row_str.append(str(grid[r][c]))
        clue_lines.append(f"  Row {r}: [{', '.join(row_str)}]")

    prompt = (f"Fill a {n}x{n} grid so each row and column contains exactly "
              f"{{{', '.join(str(i) for i in range(1, n+1))}}}.\n"
              + "\n".join(clue_lines) +
              f"\nWhat number goes in Row {hide_r}, Column {hide_c}?")

    candidates = [str(i) for i in range(1, n + 1)]
    rng.shuffle(candidates)

    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "constraint_satisfaction",
        "type": "constraint",
    }


# ---------------------------------------------------------------------------
# 2. Graph Problems — Shortest Path
# ---------------------------------------------------------------------------

def graph_problem(n_nodes=4, seed=None):
    """Generate a random weighted graph and ask for shortest path distance."""
    rng = random.Random(seed)

    nodes = [chr(65 + i) for i in range(n_nodes)]  # A, B, C, D, ...

    # Generate random edges (not fully connected)
    edges = []
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            if rng.random() < 0.6:  # 60% chance of edge
                weight = rng.randint(1, 9)
                edges.append((nodes[i], nodes[j], weight))

    if not edges:
        # Ensure at least one edge
        weight = rng.randint(1, 9)
        edges.append((nodes[0], nodes[1], weight))

    # Build adjacency for Dijkstra
    adj = defaultdict(list)
    for a, b, w in edges:
        adj[a].append((b, w))
        adj[b].append((a, w))

    # Pick source and target
    source = nodes[0]
    target = nodes[-1]

    # Dijkstra
    dist = {n: float('inf') for n in nodes}
    dist[source] = 0
    visited = set()
    queue = [(0, source)]

    while queue:
        queue.sort()
        d, node = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        for neighbor, weight in adj[node]:
            new_dist = d + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                queue.append((new_dist, neighbor))

    correct_dist = dist[target]

    if correct_dist == float('inf'):
        # No path — regenerate with more edges
        return graph_problem(n_nodes=n_nodes, seed=(seed or 0) + 1000)

    # Build prompt
    edge_strs = [f"{a}-{b}({w})" for a, b, w in edges]
    prompt = (f"Graph edges (undirected, weighted): {', '.join(edge_strs)}. "
              f"What is the shortest path distance from {source} to {target}?")

    # Candidates: correct + distractors
    candidates = [str(correct_dist)]
    while len(candidates) < 4:
        distractor = str(correct_dist + rng.choice([-2, -1, 1, 2, 3]))
        if distractor not in candidates and int(distractor) > 0:
            candidates.append(distractor)
    rng.shuffle(candidates)

    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": str(correct_dist),
        "category": "shortest_path",
        "type": "graph",
    }


# ---------------------------------------------------------------------------
# 3. State Machine Simulation
# ---------------------------------------------------------------------------

def state_machine(n_states=3, n_steps=4, seed=None):
    """Generate a random state machine and ask for final state after input."""
    rng = random.Random(seed)

    states = [chr(65 + i) for i in range(n_states)]  # A, B, C, ...
    symbols = ["0", "1"]

    # Random transition table
    transitions = {}
    for s in states:
        transitions[s] = {}
        for sym in symbols:
            transitions[s][sym] = rng.choice(states)

    # Random input sequence
    input_seq = "".join(rng.choice(symbols) for _ in range(n_steps))

    # Simulate
    current = states[0]
    for sym in input_seq:
        current = transitions[current][sym]

    correct = current

    # Build prompt
    trans_strs = []
    for s in states:
        for sym in symbols:
            trans_strs.append(f"State {s} + input '{sym}' -> State {transitions[s][sym]}")

    prompt = (f"A state machine with states {{{', '.join(states)}}} and inputs {{0, 1}}.\n"
              f"Transitions:\n  " + "\n  ".join(trans_strs) +
              f"\nStarting in State {states[0]}, input sequence: {input_seq}\n"
              f"What is the final state?")

    candidates = states[:]
    rng.shuffle(candidates)

    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "state_machine",
        "type": "state",
    }


# ---------------------------------------------------------------------------
# 4. Sequence Prediction
# ---------------------------------------------------------------------------

def sequence_prediction(rule_type=None, seed=None):
    """Generate a sequence with a known rule, ask for the next element."""
    rng = random.Random(seed)

    if rule_type is None:
        rule_type = rng.choice(["geometric", "arithmetic", "fibonacci", "power"])

    if rule_type == "geometric":
        start = rng.randint(1, 5)
        ratio = rng.randint(2, 4)
        seq = [start * (ratio ** i) for i in range(5)]
        correct = start * (ratio ** 5)

    elif rule_type == "arithmetic":
        start = rng.randint(1, 20)
        diff = rng.randint(2, 10)
        seq = [start + diff * i for i in range(5)]
        correct = start + diff * 5

    elif rule_type == "fibonacci":
        a = rng.randint(1, 5)
        b = rng.randint(1, 5)
        seq = [a, b]
        for _ in range(4):
            seq.append(seq[-1] + seq[-2])
        correct = seq[-1] + seq[-2]
        seq = seq[:6]

    elif rule_type == "power":
        base = rng.randint(2, 4)
        seq = [base ** i for i in range(1, 6)]
        correct = base ** 6

    else:
        return sequence_prediction(rule_type="arithmetic", seed=seed)

    prompt = f"Sequence: {', '.join(str(x) for x in seq)}, ?. What comes next?"

    candidates = [str(correct)]
    while len(candidates) < 4:
        offset = rng.choice([-3, -2, -1, 1, 2, 3])
        distractor = str(correct + offset * rng.randint(1, max(1, correct // 10 + 1)))
        if distractor not in candidates and int(distractor) > 0:
            candidates.append(distractor)
    # Ensure 4 candidates
    while len(candidates) < 4:
        candidates.append(str(correct + rng.randint(1, 100)))
    rng.shuffle(candidates)

    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": str(correct),
        "category": f"sequence_{rule_type}",
        "type": "sequence",
    }


# ---------------------------------------------------------------------------
# 5. Arithmetic Chain
# ---------------------------------------------------------------------------

def arithmetic_chain(n_steps=4, seed=None):
    """Generate a multi-step computation and ask for the final result."""
    rng = random.Random(seed)

    ops = ["+", "-", "*"]
    var = "x"
    value = rng.randint(1, 20)
    steps = [f"Start with {var}={value}"]

    for i in range(n_steps):
        op = rng.choice(ops)
        operand = rng.randint(1, 10)
        if op == "+":
            value = value + operand
            steps.append(f"Step {i+1}: {var}={var}+{operand}")
        elif op == "-":
            value = value - operand
            steps.append(f"Step {i+1}: {var}={var}-{operand}")
        elif op == "*":
            value = value * operand
            steps.append(f"Step {i+1}: {var}={var}*{operand}")

    correct = str(value)
    prompt = ". ".join(steps) + f". What is {var}?"

    candidates = [correct]
    while len(candidates) < 4:
        offset = rng.choice([-5, -3, -1, 1, 3, 5, 10])
        distractor = str(value + offset)
        if distractor not in candidates:
            candidates.append(distractor)
    rng.shuffle(candidates)

    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "arithmetic_chain",
        "type": "math",
    }


# ---------------------------------------------------------------------------
# 6. Modular Arithmetic
# ---------------------------------------------------------------------------

def modular_arithmetic(seed=None):
    """Generate a modular arithmetic problem."""
    rng = random.Random(seed)

    a = rng.randint(10, 200)
    m = rng.randint(3, 13)
    correct = str(a % m)

    prompt = f"What is {a} mod {m}?"

    candidates = [correct]
    while len(candidates) < 4:
        d = str(rng.randint(0, m - 1))
        if d not in candidates:
            candidates.append(d)
    rng.shuffle(candidates)

    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "modular_arithmetic",
        "type": "math",
    }


# ---------------------------------------------------------------------------
# 7. Ordering / Transitivity
# ---------------------------------------------------------------------------

def ordering_problem(n_entities=4, seed=None):
    """Generate a chain of comparisons and ask who is greatest/least."""
    rng = random.Random(seed)

    names = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Hank"]
    entities = rng.sample(names, n_entities)

    # Random total ordering
    rng.shuffle(entities)
    # entities[0] > entities[1] > ... > entities[-1]

    # Present as pairwise comparisons (not necessarily in order)
    comparisons = []
    for i in range(n_entities - 1):
        attr = rng.choice(["taller", "older", "faster", "heavier"])
        comparisons.append(f"{entities[i]} is {attr} than {entities[i+1]}")
    rng.shuffle(comparisons)

    query = rng.choice(["tallest", "oldest", "fastest", "heaviest",
                        "shortest", "youngest", "slowest", "lightest"])
    if query in ["tallest", "oldest", "fastest", "heaviest"]:
        correct = entities[0]
    else:
        correct = entities[-1]

    prompt = ". ".join(comparisons) + f". Who is the {query}?"

    candidates = entities[:]
    rng.shuffle(candidates)

    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": "ordering",
        "type": "logic",
    }


# ---------------------------------------------------------------------------
# 8. Modus Tollens / Conditional Logic
# ---------------------------------------------------------------------------

def conditional_logic(seed=None):
    """Generate a conditional reasoning problem (modus ponens/tollens)."""
    rng = random.Random(seed)

    things = [
        ("it rains", "the ground is wet"),
        ("the alarm sounds", "there is a fire"),
        ("you study hard", "you pass the exam"),
        ("the light is on", "someone is home"),
        ("the dog barks", "someone is at the door"),
        ("it snows", "the roads are icy"),
    ]

    antecedent, consequent = rng.choice(things)

    mode = rng.choice(["modus_ponens", "modus_tollens",
                        "affirming_consequent", "denying_antecedent"])

    if mode == "modus_tollens":
        prompt = (f"If {antecedent}, then {consequent}. "
                  f"The {consequent.split('the ', 1)[-1] if 'the ' in consequent else consequent} is NOT the case. "
                  f"Is it true that {antecedent}?")
        correct = "No"
        candidates = ["Yes", "No", "Cannot determine"]
    elif mode == "modus_ponens":
        prompt = (f"If {antecedent}, then {consequent}. "
                  f"It is the case that {antecedent}. "
                  f"Is it true that {consequent}?")
        correct = "Yes"
        candidates = ["Yes", "No", "Cannot determine"]
    elif mode == "affirming_consequent":
        prompt = (f"If {antecedent}, then {consequent}. "
                  f"It is the case that {consequent}. "
                  f"Can we conclude that {antecedent}?")
        correct = "Cannot determine"
        candidates = ["Yes", "No", "Cannot determine"]
    else:  # denying_antecedent
        prompt = (f"If {antecedent}, then {consequent}. "
                  f"It is NOT the case that {antecedent}. "
                  f"Can we conclude that {consequent} is false?")
        correct = "Cannot determine"
        candidates = ["Yes", "No", "Cannot determine"]

    rng.shuffle(candidates)
    return {
        "prompt": prompt,
        "candidates": candidates,
        "correct": correct,
        "category": f"conditional_{mode}",
        "type": "logic",
    }


# ---------------------------------------------------------------------------
# Master Generator
# ---------------------------------------------------------------------------

ALL_GENERATORS = [
    (constraint_satisfaction, {"n": 3}, 2),
    (constraint_satisfaction, {"n": 4}, 1),
    (graph_problem, {"n_nodes": 4}, 2),
    (graph_problem, {"n_nodes": 5}, 1),
    (state_machine, {"n_states": 3, "n_steps": 4}, 2),
    (state_machine, {"n_states": 4, "n_steps": 5}, 1),
    (sequence_prediction, {"rule_type": "geometric"}, 1),
    (sequence_prediction, {"rule_type": "arithmetic"}, 1),
    (sequence_prediction, {"rule_type": "fibonacci"}, 1),
    (sequence_prediction, {"rule_type": "power"}, 1),
    (arithmetic_chain, {"n_steps": 3}, 1),
    (arithmetic_chain, {"n_steps": 5}, 1),
    (modular_arithmetic, {}, 2),
    (ordering_problem, {"n_entities": 3}, 1),
    (ordering_problem, {"n_entities": 4}, 1),
    (conditional_logic, {}, 3),
]


def generate_battery(n=50, seed=42):
    """Generate a battery of n diverse puzzles with verified answers."""
    rng = random.Random(seed)
    battery = []
    problem_seed = seed * 1000

    # Weighted selection based on generator weights
    generators_weighted = []
    for gen, kwargs, weight in ALL_GENERATORS:
        generators_weighted.extend([(gen, kwargs)] * weight)

    for i in range(n):
        gen, kwargs = rng.choice(generators_weighted)
        problem_seed += 1
        try:
            problem = gen(seed=problem_seed, **kwargs)
            battery.append(problem)
        except Exception:
            pass

    return battery


def verify_battery(battery):
    """Verify all generated problems have correct answers in candidates."""
    errors = 0
    for i, p in enumerate(battery):
        if p["correct"] not in p["candidates"]:
            print(f"  ERROR #{i}: correct '{p['correct']}' not in candidates {p['candidates']}")
            errors += 1
    return errors


if __name__ == "__main__":
    print("Generating 50 puzzles with seed=42...")
    battery = generate_battery(n=50, seed=42)
    print(f"Generated {len(battery)} puzzles")

    # Category distribution
    from collections import Counter
    cats = Counter(p["category"] for p in battery)
    print("\nCategory distribution:")
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")

    # Verify
    print("\nVerifying answers...")
    errors = verify_battery(battery)
    print(f"Errors: {errors}")

    # Show samples
    print("\nSamples:")
    for p in battery[:5]:
        print(f"\n  [{p['category']}] {p['prompt'][:100]}")
        print(f"  Candidates: {p['candidates']}")
        print(f"  Correct: {p['correct']}")
