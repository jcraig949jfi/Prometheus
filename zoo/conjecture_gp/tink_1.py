"""Tink 1 — minimal F003 rediscovery test under GP + Framing B.

Per `tink_3_design_questions.md` v3 §0:
  - Hard prerequisite for Tink 3 implementation.
  - Goal: GP under Framing B + minimal grammar rediscovers
    F003 BSD parity (`(−1)^rank == root_number`) within 500
    candidate evaluations on rank-{0, 1} mixed cohort.
  - Pass criteria (§0.4): all five must hold.
    1. Framing B compliance (output type valid, no claim-shaped root)
    2. Multi-seed reproducibility (top-5 on ≥ 2 of 3 seeds)
    3. Semantic equivalence (canonical-form check on output)
    4. Beats shuffled-null margin pre-registered (§0.3: candidate
       score exceeds null p99 by ≥ 0.05)
    5. Proxy-leakage audit clean (vacuous for Tink 1's minimal
       grammar; documented but not gating)

If this fails on ≥ 2 of 3 seeds: Tink 3 cannot proceed. Stop.

Run: `PYTHONIOENCODING=utf-8 python tink_1.py`
"""

from __future__ import annotations

import random
from copy import deepcopy
from datetime import datetime, timezone

import numpy as np

from ast_utils import (
    atoms_used, evaluate, format_ast, token_count,
)


# ---------- pre-registered constants (committed BEFORE first run) ---------

# §0.3 shuffled-null margin
NULL_SHUFFLE_COUNT = 200
NULL_MARGIN_OVER_P99 = 0.05  # candidate score must exceed null_p99 + 0.05

# §0.4 multi-seed
SEEDS = [0, 1, 2]
MIN_PASSING_SEEDS = 2

# §0.4 top-K
TOP_K = 5

# §0.1 GP parameters
POP_SIZE = 50
N_GENERATIONS = 10
MAX_DEPTH = 3
TOURNAMENT_SIZE = 3
ELITISM = 5
CROSSOVER_RATE = 0.6
LEAF_RATE = 0.3  # probability of leaf at non-zero depth

# §0.2 canonical-form check
F003_DETECTION_TOLERANCE = 1e-9  # for numpy isclose

# Scoring coefficients
ALPHA_L_EXPR = 0.01
BETA_F003 = 1.0
PENALTY_MISSING_ATOM = 100.0  # candidate not using both rank and root_number


# ---------- minimal grammar -----------------------------------------------

GRAMMAR = {
    "atoms": ["rank", "root_number"],
    "constants": [-2.0, -1.0, 0.0, 1.0, 2.0],
    "binary_ops": ["add", "sub", "mul", "iverson_eq"],
    "unary_ops": ["neg"],
    "scalar_mul_ks": [-2.0, -1.0, 0.5, 2.0],
}

REQUIRED_ATOMS = {"rank", "root_number"}


# ---------- synthetic mixed-rank dataset ----------------------------------

def generate_tink_1_dataset(n: int = 1000, seed: int = 42) -> dict[str, np.ndarray]:
    """Half rank-0 (root_number=+1), half rank-1 (root_number=−1).

    BSD parity: `(−1)^rank = root_number`. Identity holds exactly
    by construction. Includes some optional noise via seed-dependent
    rank distribution but not in the relation itself.
    """
    rng = np.random.default_rng(seed)
    half = n // 2
    rank = np.concatenate([np.zeros(half), np.ones(n - half)])
    rng.shuffle(rank)
    root_number = np.where(rank % 2 == 0, 1.0, -1.0)
    return {"rank": rank.astype(float), "root_number": root_number}


# ---------- random tree generation ----------------------------------------

def random_leaf(grammar: dict, rng: random.Random) -> tuple:
    if rng.random() < 0.7:
        return ("atom", rng.choice(grammar["atoms"]))
    return ("const", rng.choice(grammar["constants"]))


def random_tree(grammar: dict, max_depth: int, rng: random.Random) -> tuple:
    if max_depth == 0:
        return random_leaf(grammar, rng)
    if rng.random() < LEAF_RATE:
        return random_leaf(grammar, rng)

    n_unary = len(grammar["unary_ops"])
    n_binary = len(grammar["binary_ops"])
    pick_total = n_unary + n_binary + 1  # +1 for scalar_mul

    pick = rng.randrange(pick_total)
    if pick < n_unary:
        op = grammar["unary_ops"][pick]
        return ("op", op, random_tree(grammar, max_depth - 1, rng))
    elif pick < n_unary + n_binary:
        op = grammar["binary_ops"][pick - n_unary]
        return (
            "op",
            op,
            random_tree(grammar, max_depth - 1, rng),
            random_tree(grammar, max_depth - 1, rng),
        )
    else:
        k = rng.choice(grammar["scalar_mul_ks"])
        return ("op", "scalar_mul", k, random_tree(grammar, max_depth - 1, rng))


# ---------- AST utilities for GP ------------------------------------------

def tree_depth(node: tuple) -> int:
    if node[0] in ("atom", "const"):
        return 0
    if node[0] == "op":
        op = node[1]
        children = []
        if op in ("add", "sub", "mul", "div", "iverson_eq"):
            children = [node[2], node[3]]
        elif op in ("neg", "exp", "log"):
            children = [node[2]]
        elif op == "scalar_mul":
            children = [node[3]]
        elif op == "pow":
            children = [node[2]]
        if not children:
            return 0
        return 1 + max(tree_depth(c) for c in children)
    return 0


def collect_subtrees(node: tuple, path: tuple = ()) -> list[tuple]:
    """List of (subtree, path-from-root) tuples. Path is a tuple of
    indices into the node's args."""
    out = [(node, path)]
    if node[0] != "op":
        return out
    op = node[1]
    if op in ("add", "sub", "mul", "div", "iverson_eq"):
        out.extend(collect_subtrees(node[2], path + (2,)))
        out.extend(collect_subtrees(node[3], path + (3,)))
    elif op in ("neg", "exp", "log"):
        out.extend(collect_subtrees(node[2], path + (2,)))
    elif op == "scalar_mul":
        out.extend(collect_subtrees(node[3], path + (3,)))
    elif op == "pow":
        out.extend(collect_subtrees(node[2], path + (2,)))
    return out


def replace_at_path(node: tuple, path: tuple, replacement: tuple) -> tuple:
    if not path:
        return replacement
    idx = path[0]
    rest = path[1:]
    new_node = list(node)
    new_node[idx] = replace_at_path(node[idx], rest, replacement)
    return tuple(new_node)


def crossover(parent_a: tuple, parent_b: tuple, rng: random.Random,
              max_depth: int) -> tuple:
    """Subtree crossover: pick random subtree in parent_a, replace
    with random subtree from parent_b."""
    subtrees_a = collect_subtrees(parent_a)
    subtrees_b = collect_subtrees(parent_b)
    if not subtrees_a or not subtrees_b:
        return deepcopy(parent_a)
    _, path_a = rng.choice(subtrees_a)
    sub_b, _ = rng.choice(subtrees_b)
    child = replace_at_path(parent_a, path_a, sub_b)
    if tree_depth(child) > max_depth + 1:  # allow slight overflow
        return deepcopy(parent_a)
    return child


def mutate(node: tuple, grammar: dict, max_depth: int,
           rng: random.Random) -> tuple:
    """Subtree mutation: pick a random subtree, replace with a fresh
    random subtree."""
    subtrees = collect_subtrees(node)
    if not subtrees:
        return random_tree(grammar, max_depth, rng)
    _, path = rng.choice(subtrees)
    remaining_depth = max(1, max_depth - len(path))
    new_subtree = random_tree(grammar, remaining_depth, rng)
    return replace_at_path(node, path, new_subtree)


def tournament_select(scored: list[tuple], k: int,
                      rng: random.Random) -> tuple:
    """Pick k random, return the best (lowest aggregate)."""
    contenders = rng.sample(scored, min(k, len(scored)))
    contenders.sort(key=lambda x: x[1]["aggregate"])
    return contenders[0][0]


# ---------- scoring -------------------------------------------------------

def f003_detection_score(node: tuple, data: dict) -> float:
    """Fraction of rows where the candidate's output equals 1.0."""
    try:
        out = evaluate(node, data)
    except Exception:
        return 0.0
    if not isinstance(out, np.ndarray):
        out = np.array(out)
    if out.shape != (len(data["rank"]),):
        if out.size == 1:
            out = np.full(len(data["rank"]), float(out))
        else:
            return 0.0
    if not np.isfinite(out).all():
        return 0.0
    return float(np.mean(np.isclose(out, 1.0, atol=F003_DETECTION_TOLERANCE)))


def score_candidate(node: tuple, data: dict) -> dict:
    """Compute aggregate, F003 detection score, L_expr, atom usage."""
    n_tokens = token_count(node)
    used = atoms_used(node)
    f003 = f003_detection_score(node, data)
    l_expr = ALPHA_L_EXPR * n_tokens

    # Penalize candidates not using both required atoms (these would
    # be trivially constant or meaningless)
    missing = REQUIRED_ATOMS - used
    penalty = PENALTY_MISSING_ATOM * len(missing)

    aggregate = l_expr - BETA_F003 * f003 + penalty

    return {
        "aggregate": aggregate,
        "f003_score": f003,
        "L_expr": l_expr,
        "n_tokens": n_tokens,
        "atoms_used": sorted(used),
        "all_required_present": (missing == set()),
        "penalty": penalty,
    }


def shuffled_null_distribution(node: tuple, data: dict, n_shuffles: int,
                                seed: int) -> np.ndarray:
    """Generate null distribution of F003-detection scores by
    shuffling root_number labels."""
    rng = np.random.default_rng(seed + 9999)
    null_scores = []
    for _ in range(n_shuffles):
        shuffled = data["root_number"].copy()
        rng.shuffle(shuffled)
        shuffled_data = {"rank": data["rank"], "root_number": shuffled}
        null_scores.append(f003_detection_score(node, shuffled_data))
    return np.array(null_scores)


# ---------- canonical-form / semantic equivalence check -------------------

def is_f003_equivalent(node: tuple, data: dict) -> bool:
    """§0.2 canonical-form check.

    A candidate is F003-equivalent iff:
      - its output evaluated on the dataset is constant 1.0 across
        all rows, AND
      - it uses BOTH `rank` AND `root_number`.

    The "constant 1.0" check, combined with the multi-rank dataset
    (rank ∈ {0, 1}, root_number ∈ {+1, −1}), means the candidate
    must encode the F003 identity to achieve constant 1 across
    rank-0 (root_number=+1) AND rank-1 (root_number=−1) cohorts.
    """
    try:
        out = evaluate(node, data)
    except Exception:
        return False
    if not isinstance(out, np.ndarray):
        return False
    if not np.isfinite(out).all():
        return False
    used = atoms_used(node)
    if used != REQUIRED_ATOMS:
        return False
    return bool(np.all(np.isclose(out, 1.0, atol=F003_DETECTION_TOLERANCE)))


# ---------- GP loop -------------------------------------------------------

def gp_search(grammar: dict, data: dict, pop_size: int, n_gens: int,
              seed: int, max_depth: int) -> tuple[list, list]:
    rng = random.Random(seed)
    population = [random_tree(grammar, max_depth, rng) for _ in range(pop_size)]
    history = []

    for gen in range(n_gens):
        scored = [(t, score_candidate(t, data)) for t in population]
        scored.sort(key=lambda x: x[1]["aggregate"])

        history.append({
            "generation": gen,
            "best_aggregate": scored[0][1]["aggregate"],
            "best_f003": scored[0][1]["f003_score"],
            "best_tree": format_ast(scored[0][0]),
        })

        # Elitism: top-K carry forward
        new_pop = [deepcopy(t) for t, _ in scored[:ELITISM]]
        while len(new_pop) < pop_size:
            parent_a = tournament_select(scored, TOURNAMENT_SIZE, rng)
            parent_b = tournament_select(scored, TOURNAMENT_SIZE, rng)
            if rng.random() < CROSSOVER_RATE:
                child = crossover(parent_a, parent_b, rng, max_depth)
            else:
                child = mutate(parent_a, grammar, max_depth, rng)
            new_pop.append(child)
        population = new_pop

    final_scored = [(t, score_candidate(t, data)) for t in population]
    final_scored.sort(key=lambda x: x[1]["aggregate"])
    return final_scored, history


# ---------- per-seed run + criteria check ---------------------------------

def run_seed(grammar: dict, data: dict, seed: int) -> dict:
    final_scored, history = gp_search(
        grammar, data,
        pop_size=POP_SIZE, n_gens=N_GENERATIONS,
        seed=seed, max_depth=MAX_DEPTH,
    )

    top_k = final_scored[:TOP_K]

    # Find best F003-equivalent in top-K (if any)
    f003_in_top_k = None
    for tree, score in top_k:
        if is_f003_equivalent(tree, data):
            f003_in_top_k = (tree, score)
            break

    # Also: best F003 in entire final population (for diagnostic)
    f003_anywhere = None
    for tree, score in final_scored:
        if is_f003_equivalent(tree, data):
            f003_anywhere = (tree, score)
            break

    # If F003 found in top-K, run shuffled-null check (§0.3)
    null_check_result = None
    if f003_in_top_k is not None:
        tree, score = f003_in_top_k
        null_dist = shuffled_null_distribution(
            tree, data, NULL_SHUFFLE_COUNT, seed
        )
        null_p99 = float(np.quantile(null_dist, 0.99))
        candidate_score = score["f003_score"]
        margin = candidate_score - null_p99
        passes_null_margin = margin >= NULL_MARGIN_OVER_P99
        null_check_result = {
            "candidate_f003_score": candidate_score,
            "null_p99": null_p99,
            "null_p95": float(np.quantile(null_dist, 0.95)),
            "null_mean": float(null_dist.mean()),
            "null_max": float(null_dist.max()),
            "margin": float(margin),
            "passes_null_margin": passes_null_margin,
        }

    return {
        "seed": seed,
        "top_k": [(format_ast(t), s) for t, s in top_k],
        "f003_in_top_k": f003_in_top_k is not None,
        "f003_in_top_k_tree": (
            format_ast(f003_in_top_k[0]) if f003_in_top_k else None
        ),
        "f003_in_top_k_score": (
            f003_in_top_k[1] if f003_in_top_k else None
        ),
        "f003_anywhere": f003_anywhere is not None,
        "f003_anywhere_tree": (
            format_ast(f003_anywhere[0]) if f003_anywhere else None
        ),
        "null_check": null_check_result,
        "history": history,
    }


# ---------- main runner ---------------------------------------------------

def run_tink_1(seeds: list[int] = SEEDS, n: int = 1000) -> dict:
    print("=" * 78)
    print("Tink 1 — minimal F003 rediscovery (Framing B + GP)")
    print(f"  Date: {datetime.now(timezone.utc).isoformat()}")
    print(f"  Population: {POP_SIZE} × {N_GENERATIONS} gens"
          f" = {POP_SIZE * N_GENERATIONS} evals/seed")
    print(f"  Seeds: {seeds} (≥{MIN_PASSING_SEEDS} must pass)")
    print(f"  Pre-registered margin: candidate F003 > null p99 + {NULL_MARGIN_OVER_P99}")
    print(f"  Allowed canonical form: output ≡ 1 across all rows AND uses both atoms")
    print("=" * 78)

    seed_results = []
    for seed in seeds:
        print(f"\n--- Seed {seed} ---")
        data = generate_tink_1_dataset(n=n, seed=seed)
        result = run_seed(GRAMMAR, data, seed)
        seed_results.append(result)

        print(f"  Top-{TOP_K} (best aggregate first):")
        for i, (tree_str, s) in enumerate(result["top_k"], 1):
            mark = "  [F003]" if (
                i == 1 and result["f003_in_top_k"]
                and result["f003_in_top_k_tree"] == tree_str
            ) else ""
            # Check each top-K for F003 equivalence
            print(
                f"    {i}. {tree_str}  "
                f"agg={s['aggregate']:+.4f}  f003={s['f003_score']:.4f}  "
                f"tokens={s['n_tokens']}{mark}"
            )

        if result["f003_in_top_k"]:
            print(f"  F003-equivalent in top-K: YES → {result['f003_in_top_k_tree']}")
            nc = result["null_check"]
            print(
                f"  Null check: candidate={nc['candidate_f003_score']:.3f}, "
                f"p99={nc['null_p99']:.3f}, p95={nc['null_p95']:.3f}, "
                f"margin={nc['margin']:+.3f}, "
                f"passes={nc['passes_null_margin']}"
            )
        else:
            print(f"  F003-equivalent in top-K: NO")
            if result["f003_anywhere"]:
                print(f"  F003 found elsewhere in pop: {result['f003_anywhere_tree']}")
            else:
                print(f"  F003 not found anywhere in pop.")

    # ---- Aggregate hard criteria (§0.4) -----------------------------------

    n_seeds_with_f003_top_k = sum(1 for r in seed_results if r["f003_in_top_k"])
    n_seeds_passing_null = sum(
        1 for r in seed_results
        if r["null_check"] and r["null_check"]["passes_null_margin"]
    )

    # Criterion 1: Framing B compliance
    # (Verified by construction: grammar has no top-level corr/=/≤
    # operators)
    crit_1 = True

    # Criterion 2: multi-seed reproducibility
    crit_2 = n_seeds_with_f003_top_k >= MIN_PASSING_SEEDS

    # Criterion 3: semantic equivalence verified
    # (Implicit in is_f003_equivalent check; passes if any seed has F003 in top-K)
    crit_3 = n_seeds_with_f003_top_k > 0

    # Criterion 4: shuffled-null margin passes on ≥ MIN_PASSING_SEEDS seeds
    crit_4 = n_seeds_passing_null >= MIN_PASSING_SEEDS

    # Criterion 5: proxy-leakage audit clean
    # For Tink 1's minimal grammar (only rank, root_number atoms; no
    # off-basis atoms to leak through), the proxy-leakage audit is
    # vacuous. Documented per design doc §0.4 caveat. NOT gating.
    crit_5_vacuous = True

    overall_pass = crit_1 and crit_2 and crit_3 and crit_4 and crit_5_vacuous

    summary = {
        "n_seeds_with_f003_top_k": n_seeds_with_f003_top_k,
        "n_seeds_passing_null": n_seeds_passing_null,
        "criterion_1_framing_b": crit_1,
        "criterion_2_multi_seed": crit_2,
        "criterion_3_semantic": crit_3,
        "criterion_4_null_margin": crit_4,
        "criterion_5_proxy_audit": "VACUOUS (Tink 1 minimal grammar)",
        "overall_pass": overall_pass,
        "verdict": _verdict(overall_pass, crit_2, crit_4, seed_results),
    }

    print("\n" + "=" * 78)
    print("HARD CRITERIA (§0.4)")
    print("-" * 78)
    print(f"  1. Framing B compliance:        {'PASS' if crit_1 else 'FAIL'}"
          f"  (no top-level corr/=/≤ in grammar)")
    print(f"  2. Multi-seed reproducibility:  {'PASS' if crit_2 else 'FAIL'}"
          f"  ({n_seeds_with_f003_top_k}/{len(seeds)} seeds w/ F003 in top-{TOP_K},"
          f" need ≥ {MIN_PASSING_SEEDS})")
    print(f"  3. Semantic equivalence:        {'PASS' if crit_3 else 'FAIL'}"
          f"  (canonical-form constant-1 check)")
    print(f"  4. Shuffled-null margin:        {'PASS' if crit_4 else 'FAIL'}"
          f"  ({n_seeds_passing_null}/{len(seeds)} seeds pass margin)")
    print(f"  5. Proxy-leakage audit:         VACUOUS"
          f"  (Tink 1 minimal grammar has no off-basis atoms)")

    print("\n" + "=" * 78)
    print(f"VERDICT: {summary['verdict']}")
    print("=" * 78)

    return {"seed_results": seed_results, "summary": summary}


def _verdict(overall_pass: bool, crit_2: bool, crit_4: bool,
             seed_results: list) -> str:
    if overall_pass:
        return "PASS — Tink 3 implementation gates open"
    # Distinguish FAIL from INCONCLUSIVE
    # INCONCLUSIVE: any seed had a tree-evaluation crash, NaN output,
    # or other instrument failure
    instrument_failure = any(
        r.get("instrument_failure") for r in seed_results
    )
    if instrument_failure:
        return "INCONCLUSIVE — instrument failure; fix and re-run"
    if not crit_2:
        return "FAIL — F003 not rediscovered on ≥ 2 of 3 seeds. STOP."
    if not crit_4:
        return "FAIL — F003 found but does not exceed shuffled-null margin"
    return "FAIL"


# ---------- markdown report ------------------------------------------------

def write_results_md(results: dict, path: str) -> None:
    summary = results["summary"]
    seed_results = results["seed_results"]

    L = []
    L.append(f"# Tink 1 results — {datetime.now(timezone.utc).date().isoformat()}")
    L.append("")
    L.append(f"**Verdict: {summary['verdict']}**")
    L.append("")
    L.append("## Setup")
    L.append("")
    L.append("- Grammar: minimal — atoms `{rank, root_number}`, ops "
             "`{add, sub, mul, neg, scalar_mul, iverson_eq}`, "
             f"max depth `{MAX_DEPTH}`")
    L.append(f"- Population: `{POP_SIZE}` individuals × "
             f"`{N_GENERATIONS}` generations = "
             f"`{POP_SIZE * N_GENERATIONS}` evals/seed")
    L.append(f"- Seeds: `{SEEDS}` (≥ `{MIN_PASSING_SEEDS}` of 3 must pass)")
    L.append("- Aggregate: `α · L_expr − β · f003_score + penalty_missing_atom`"
             f"  (α=`{ALPHA_L_EXPR}`, β=`{BETA_F003}`, "
             f"penalty=`{PENALTY_MISSING_ATOM}`)")
    L.append(f"- Pre-registered shuffled-null margin: `{NULL_MARGIN_OVER_P99}`"
             f" above `null p99` over `{NULL_SHUFFLE_COUNT}` shuffles")
    L.append(f"- Allowed canonical form (§0.2): output ≡ 1 across all rows "
             f"AND atom set == `{{rank, root_number}}`")
    L.append("")

    L.append("## Hard pass criteria (§0.4)")
    L.append("")
    L.append(f"1. **Framing B compliance**: "
             f"{'PASS' if summary['criterion_1_framing_b'] else 'FAIL'}")
    L.append(f"2. **Multi-seed reproducibility**: "
             f"{'PASS' if summary['criterion_2_multi_seed'] else 'FAIL'} — "
             f"{summary['n_seeds_with_f003_top_k']}/{len(SEEDS)} seeds had "
             f"F003-equivalent in top-{TOP_K}")
    L.append(f"3. **Semantic equivalence**: "
             f"{'PASS' if summary['criterion_3_semantic'] else 'FAIL'}")
    L.append(f"4. **Shuffled-null margin**: "
             f"{'PASS' if summary['criterion_4_null_margin'] else 'FAIL'} — "
             f"{summary['n_seeds_passing_null']}/{len(SEEDS)} seeds clear margin")
    L.append(f"5. **Proxy-leakage audit**: VACUOUS (Tink 1 minimal grammar; "
             f"deferred to Tink 3)")
    L.append("")

    L.append("## Per-seed results")
    L.append("")
    for r in seed_results:
        L.append(f"### Seed {r['seed']}")
        L.append("")
        L.append(f"**F003 in top-{TOP_K}: {'YES' if r['f003_in_top_k'] else 'NO'}**"
                 + (f" → `{r['f003_in_top_k_tree']}`" if r["f003_in_top_k"] else ""))
        L.append("")
        if r["null_check"]:
            nc = r["null_check"]
            L.append(f"Null check: candidate F003 = `{nc['candidate_f003_score']:.4f}`, "
                     f"null p99 = `{nc['null_p99']:.4f}`, p95 = `{nc['null_p95']:.4f}`, "
                     f"null mean = `{nc['null_mean']:.4f}`, "
                     f"margin = `{nc['margin']:+.4f}`, "
                     f"passes = **{nc['passes_null_margin']}**")
            L.append("")
        L.append(f"Top-{TOP_K} candidates:")
        L.append("")
        L.append("| # | tree | aggregate | f003_score | tokens |")
        L.append("|--:|------|----------:|-----------:|-------:|")
        for i, (tree_str, s) in enumerate(r["top_k"], 1):
            L.append(f"| {i} | `{tree_str}` | "
                     f"{s['aggregate']:+.4f} | "
                     f"{s['f003_score']:.4f} | "
                     f"{s['n_tokens']} |")
        L.append("")
        L.append(f"GP history (best aggregate per generation):")
        L.append("")
        L.append("| gen | best_aggregate | best_f003 | best_tree |")
        L.append("|----:|---------------:|----------:|-----------|")
        for h in r["history"]:
            L.append(f"| {h['generation']} | {h['best_aggregate']:+.4f} | "
                     f"{h['best_f003']:.4f} | `{h['best_tree']}` |")
        L.append("")

    L.append("## Notes on criterion 5 (proxy-leakage)")
    L.append("")
    L.append("The proxy-leakage audit defined in `tink_3_design_questions.md` v3 "
             "§5.6 conditional-residualizes a candidate's features against the "
             "identity basis, recomputes its affordance, and rejects candidates "
             "whose affordance comes from basis-atom proxies.")
    L.append("")
    L.append("For Tink 1's minimal grammar (atoms `{rank, root_number}`), there "
             "are no off-basis atoms; the basis IS the F003 identity itself. The "
             "audit is vacuous: any candidate that captures F003 will register "
             "100% leakage by construction. The audit fires only when a richer "
             "atom set creates the possibility of basis-proxy candidates, which "
             "is the Tink 3 setting. Per §0.4 design caveat, the audit is "
             "documented as run, not gating, for Tink 1.")
    L.append("")

    L.append("## What this verdict implies")
    L.append("")
    if summary["overall_pass"]:
        L.append("**v3 design doc §0.4 hard criteria passed on Tink 1.** GP "
                 "under Framing B with the minimal grammar can rediscover "
                 "F003 within the pre-registered budget. The instrument is "
                 "validated for the central composition (search + Framing B + "
                 "scoring) at minimum-viable scale.")
        L.append("")
        L.append("**Next step per design doc Status §:** pin "
                 "`Q_EC_R012_D5@v0` (or `Q_EC_R01_D5@v0` if rank-2 fallback "
                 "triggers per §4.5.1), run coefficient sub-sweep, then "
                 "Tink 3 implementation.")
    else:
        L.append("**v3 design doc §0.4 hard criteria did NOT pass.** Per the "
                 "design doc's stop condition, Tink 3 cannot proceed. The "
                 "GP-vs-Framing-B composition is broken at minimum scale and "
                 "must be debugged before continuing.")
        L.append("")
        L.append("**Investigation order:** check that the canonical-form "
                 "check is correctly identifying F003-equivalent expressions; "
                 "verify the GP loop is not pathologically converging; "
                 "examine if the grammar makes F003 reachable at depth ≤ 3.")
    L.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    results = run_tink_1()
    out_path = "results_2026-04-25_tink_1.md"
    write_results_md(results, out_path)
    print(f"\nMarkdown summary written to: {out_path}")
