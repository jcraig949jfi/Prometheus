"""Search Evolver — evolutionary program synthesis for mathematical discovery.

LLM generates Python search functions. Falsification battery selects.
Survivors seed next generation. AlphaEvolve pattern applied to cross-domain search.
"""

import argparse
import hashlib
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

# Path setup
REPO = Path(__file__).resolve().parents[5]  # F:/Prometheus
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # shared/scripts

from sandbox import Sandbox, validate_code, complexity_score, extract_function_name
from falsification_battery import run_battery

OUTPUT_DIR = REPO / "cartography" / "convergence" / "data"
EVOLVED_DIR = Path(__file__).resolve().parent / "evolved_functions"
EVOLVED_DIR.mkdir(exist_ok=True)
EVOLUTION_LOG = OUTPUT_DIR / "evolution_log.jsonl"
FRONTIER_TARGETS = OUTPUT_DIR / "frontier_targets.jsonl"


# ---------------------------------------------------------------------------
# Seed population
# ---------------------------------------------------------------------------

SEED_FUNCTIONS = [
    # Seed 1: Pearson correlation
    '''
def search_pearson(values_a, values_b):
    """Pearson correlation between two value arrays."""
    import numpy as np
    from scipy import stats
    n = min(len(values_a), len(values_b))
    if n < 10:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    r, p = stats.pearsonr(values_a[:n], values_b[:n])
    return {"statistic": float(r), "p_value": float(p), "description": f"Pearson r={r:.4f}"}
''',

    # Seed 2: KS test (distribution comparison)
    '''
def search_ks(values_a, values_b):
    """Kolmogorov-Smirnov test: are distributions different?"""
    import numpy as np
    from scipy import stats
    a, b = np.array(values_a, dtype=float), np.array(values_b, dtype=float)
    if len(a) < 5 or len(b) < 5:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    d, p = stats.ks_2samp(a, b)
    return {"statistic": float(d), "p_value": float(p), "description": f"KS D={d:.4f}"}
''',

    # Seed 3: Mutual information (binned)
    '''
def search_mutual_info(values_a, values_b):
    """Binned mutual information between two arrays."""
    import numpy as np
    n = min(len(values_a), len(values_b))
    if n < 20:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    a, b = np.array(values_a[:n], dtype=float), np.array(values_b[:n], dtype=float)
    n_bins = max(5, int(np.sqrt(n)))
    hist_ab, _, _ = np.histogram2d(a, b, bins=n_bins)
    pxy = hist_ab / hist_ab.sum()
    px = pxy.sum(axis=1)
    py = pxy.sum(axis=0)
    mi = 0.0
    for i in range(n_bins):
        for j in range(n_bins):
            if pxy[i, j] > 0 and px[i] > 0 and py[j] > 0:
                mi += pxy[i, j] * np.log(pxy[i, j] / (px[i] * py[j]))
    # Null: random pairing MI
    rng = np.random.RandomState(42)
    null_mis = []
    for _ in range(200):
        b_shuf = rng.permutation(b)
        h, _, _ = np.histogram2d(a, b_shuf, bins=n_bins)
        p_s = h / h.sum()
        px_s = p_s.sum(axis=1)
        py_s = p_s.sum(axis=0)
        mi_s = 0.0
        for ii in range(n_bins):
            for jj in range(n_bins):
                if p_s[ii, jj] > 0 and px_s[ii] > 0 and py_s[jj] > 0:
                    mi_s += p_s[ii, jj] * np.log(p_s[ii, jj] / (px_s[ii] * py_s[jj]))
        null_mis.append(mi_s)
    null_mean = np.mean(null_mis)
    null_std = np.std(null_mis) + 1e-12
    z = (mi - null_mean) / null_std
    from scipy import stats
    p_value = float(2 * (1 - stats.norm.cdf(abs(z))))
    return {"statistic": float(mi), "p_value": p_value, "description": f"MI={mi:.4f}, z={z:.2f}"}
''',

    # Seed 4: Gap spacing ratio
    '''
def search_gap_ratio(values_a, values_b):
    """Compare consecutive-difference distributions."""
    import numpy as np
    from scipy import stats
    def gaps(v):
        s = np.sort(np.array(v, dtype=float))
        d = np.diff(s)
        if len(d) == 0:
            return np.array([])
        mean_d = np.mean(d)
        if mean_d > 0:
            return d / mean_d
        return d
    ga, gb = gaps(values_a), gaps(values_b)
    if len(ga) < 5 or len(gb) < 5:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    d, p = stats.ks_2samp(ga, gb)
    return {"statistic": float(d), "p_value": float(p), "description": f"Gap-ratio KS D={d:.4f}"}
''',

    # Seed 5: Moment comparison
    '''
def search_moments(values_a, values_b):
    """Compare moment vectors (mean, var, skew, kurtosis) as Euclidean distance."""
    import numpy as np
    from scipy import stats
    def moment_vec(v):
        a = np.array(v, dtype=float)
        if len(a) < 10:
            return None
        return np.array([np.mean(a), np.var(a), float(stats.skew(a)), float(stats.kurtosis(a))])
    ma, mb = moment_vec(values_a), moment_vec(values_b)
    if ma is None or mb is None:
        return {"statistic": 0.0, "p_value": 1.0, "description": "insufficient data"}
    # Normalize each moment by pooled scale
    scale = np.abs(ma) + np.abs(mb) + 1e-12
    diff = np.abs(ma - mb) / scale
    dist = float(np.linalg.norm(diff))
    # Null via permutation
    pool = np.concatenate([np.array(values_a, dtype=float), np.array(values_b, dtype=float)])
    rng = np.random.RandomState(42)
    null_dists = []
    for _ in range(500):
        rng.shuffle(pool)
        half = len(pool) // 2
        sa, sb = pool[:half], pool[half:]
        mma = np.array([np.mean(sa), np.var(sa), float(stats.skew(sa)), float(stats.kurtosis(sa))])
        mmb = np.array([np.mean(sb), np.var(sb), float(stats.skew(sb)), float(stats.kurtosis(sb))])
        sc = np.abs(mma) + np.abs(mmb) + 1e-12
        null_dists.append(float(np.linalg.norm(np.abs(mma - mmb) / sc)))
    p_value = float(np.mean([1 if nd >= dist else 0 for nd in null_dists]))
    return {"statistic": dist, "p_value": max(p_value, 1e-6), "description": f"Moment dist={dist:.4f}"}
''',
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _func_id(code: str) -> str:
    """Short hash for function identity."""
    return "f_" + hashlib.md5(code.encode()).hexdigest()[:8]


def _timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _load_frontier_targets() -> list[dict]:
    """Load frontier targets if file exists."""
    if not FRONTIER_TARGETS.exists():
        return []
    targets = []
    with open(FRONTIER_TARGETS, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    targets.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return targets


def _extract_code_block(text: str) -> str:
    """Extract Python code from LLM response (strip markdown fences)."""
    if "```python" in text:
        text = text.split("```python", 1)[1]
        if "```" in text:
            text = text.split("```", 1)[0]
    elif "```" in text:
        text = text.split("```", 1)[1]
        if "```" in text:
            text = text.split("```", 1)[0]
    return text.strip()


def _tournament_select(population: list[dict], k: int = 3) -> dict:
    """Tournament selection: pick k random, return best."""
    candidates = random.sample(population, min(k, len(population)))
    return max(candidates, key=lambda x: x.get("fitness", 0.0))


# ---------------------------------------------------------------------------
# Synthetic test data (for evaluation without search_engine)
# ---------------------------------------------------------------------------

def _make_test_pairs(n_pairs: int = 4, seed: int = 42) -> list[tuple]:
    """Generate synthetic dataset pairs for function evaluation."""
    rng = np.random.RandomState(seed)
    pairs = []
    # Pair 1: correlated normal
    a = rng.randn(100)
    b = 0.5 * a + 0.5 * rng.randn(100)
    pairs.append((a.tolist(), b.tolist(), "correlated_normal"))
    # Pair 2: same distribution
    a = rng.exponential(2.0, 100)
    b = rng.exponential(2.0, 100)
    pairs.append((a.tolist(), b.tolist(), "same_exponential"))
    # Pair 3: different distributions
    a = rng.randn(100)
    b = rng.exponential(1.0, 100)
    pairs.append((a.tolist(), b.tolist(), "normal_vs_exponential"))
    # Pair 4: integer sequences with structure
    a = list(range(2, 102))
    b = [x**2 % 97 for x in range(2, 102)]
    pairs.append((a, b, "linear_vs_quadmod"))
    return pairs


# ---------------------------------------------------------------------------
# Score a function
# ---------------------------------------------------------------------------

def score_function(code: str, func_name: str, sandbox: Sandbox,
                   test_pairs: list[tuple], seen_kills: set) -> dict:
    """Run function on test pairs, battery-test results, compute fitness."""
    results = {
        "battery_survival": 0.0,
        "novel_failure_bonus": 0.0,
        "frontier_bonus": 0.0,
        "parsimony": 0.0,
        "fitness": 0.0,
        "tests_run": 0,
        "tests_survived": 0,
        "kill_signature": None,
        "errors": [],
    }

    # Parsimony
    cx = complexity_score(code)
    max_cx = 200
    results["parsimony"] = max(0.0, 1.0 - cx / max_cx)
    results["complexity"] = cx

    survived = 0
    total = 0
    kill_sig = []

    for values_a, values_b, pair_label in test_pairs:
        r = sandbox.execute(code, func_name, values_a, values_b)
        if not r["success"]:
            results["errors"].append(f"{pair_label}: {r.get('error', 'unknown')}")
            continue

        ret = r["result"]
        if not isinstance(ret, dict) or "statistic" not in ret or "p_value" not in ret:
            results["errors"].append(f"{pair_label}: bad return format")
            continue

        total += 1
        # Run battery on the two arrays (the function is a search method,
        # the battery validates whether the found relationship is real)
        try:
            a_arr = np.array(values_a, dtype=float)
            b_arr = np.array(values_b, dtype=float)
            n = min(len(a_arr), len(b_arr))
            if n >= 10:
                verdict, batt = run_battery(a_arr[:n], b_arr[:n],
                                            label_a="A", label_b="B")
                if verdict == "SURVIVES":
                    survived += 1
                else:
                    # Record which tests killed it
                    for tname, tres in batt.items():
                        if tres.get("verdict") == "FAIL":
                            kill_sig.append(f"{pair_label}:{tname}")
            else:
                survived += 1  # too small to test, don't penalize
        except Exception as e:
            results["errors"].append(f"{pair_label}: battery error: {e}")

    if total > 0:
        results["battery_survival"] = survived / total
    results["tests_run"] = total
    results["tests_survived"] = survived

    # Kill signature for novelty bonus
    sig = tuple(sorted(set(kill_sig))) if kill_sig else None
    results["kill_signature"] = sig
    if sig and sig not in seen_kills:
        results["novel_failure_bonus"] = 1.0

    # Frontier bonus: placeholder (1.0 if function targets an undertested concept)
    # Without live frontier data, give partial credit for code diversity
    results["frontier_bonus"] = 0.5

    # Fitness
    results["fitness"] = (
        results["battery_survival"] * 0.3 +
        results["novel_failure_bonus"] * 0.3 +
        results["frontier_bonus"] * 0.2 +
        results["parsimony"] * 0.2
    )

    return results


# ---------------------------------------------------------------------------
# LLM mutation
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a mathematical research tool. Generate Python functions that compare "
    "two numerical arrays to find statistical relationships. Use only numpy and scipy. "
    "Return ONLY the Python function definition, no explanation or markdown."
)


def _mutate(parent_code: str, target_desc: str, provider: str) -> str | None:
    """Ask LLM to mutate a parent function toward a target."""
    user_prompt = (
        f"Here is a search function:\n\n{parent_code}\n\n"
        f"Modify it to test: {target_desc}\n\n"
        "Requirements:\n"
        "- Function must accept (values_a, values_b) and return "
        '{"statistic": float, "p_value": float, "description": str}\n'
        "- Only use numpy (as np) and scipy.stats\n"
        "- MAXIMUM 15 lines of code. No comments. No docstrings. No type hints.\n"
        "- Keep it simple: one test statistic, one p-value.\n"
        "- Return ONLY the Python function, no explanation."
    )
    try:
        from council_client import ask
        response = ask(user_prompt, system=SYSTEM_PROMPT, provider=provider,
                       max_tokens=2048, temperature=0.7)
        return _extract_code_block(response)
    except Exception as e:
        print(f"  [MUTATE] API error: {e}")
        return None


# ---------------------------------------------------------------------------
# Evolution loop
# ---------------------------------------------------------------------------

def evolve(n_generations: int = 10, population_size: int = 20,
           provider: str = "deepseek", dry_run: bool = False):
    """Main evolutionary loop."""
    sandbox = Sandbox(timeout_s=5, max_memory_mb=256)
    test_pairs = _make_test_pairs()
    seen_kills: set = set()

    # Initialize population from seeds
    population = []
    for code in SEED_FUNCTIONS:
        code = code.strip()
        fname = extract_function_name(code)
        if not fname:
            continue
        fid = _func_id(code)
        scores = score_function(code, fname, sandbox, test_pairs, seen_kills)
        if scores["kill_signature"]:
            seen_kills.add(scores["kill_signature"])
        population.append({
            "id": fid,
            "code": code,
            "function_name": fname,
            "fitness": scores["fitness"],
            "scores": scores,
            "parent": "seed",
            "generation": 0,
        })

    population.sort(key=lambda x: x["fitness"], reverse=True)
    print(f"[GEN 0] seeds={len(population)}, best={population[0]['fitness']:.3f} "
          f"({population[0]['function_name']})")

    # Log seeds
    for ind in population:
        _log_individual(ind, 0)

    # Mutation targets
    targets = _load_frontier_targets()
    default_targets = [
        "higher-order correlation (Spearman rank)",
        "tail behavior comparison (extreme value overlap)",
        "periodicity detection via autocorrelation",
        "entropy comparison (Shannon entropy of binned values)",
        "ratio of consecutive elements distribution test",
        "power spectrum similarity (FFT magnitudes)",
        "median absolute deviation comparison",
        "quantile-quantile divergence measure",
    ]

    for gen in range(1, n_generations + 1):
        new_offspring = []

        if not dry_run:
            # Generate offspring via LLM mutation
            n_offspring = max(2, population_size // 3)
            for i in range(n_offspring):
                parent = _tournament_select(population)
                # Pick target
                if targets:
                    target = random.choice(targets).get("description", random.choice(default_targets))
                else:
                    target = random.choice(default_targets)

                child_code = _mutate(parent["code"], target, provider)
                if child_code is None:
                    continue

                # Validate
                safe, reason = validate_code(child_code)
                if not safe:
                    print(f"  [GEN {gen}] child rejected: {reason}")
                    continue

                cx = complexity_score(child_code)
                if cx > 300:
                    print(f"  [GEN {gen}] child too complex: {cx} nodes")
                    continue

                fname = extract_function_name(child_code)
                if not fname:
                    print(f"  [GEN {gen}] child has no function def")
                    continue

                # Score
                fid = _func_id(child_code)
                scores = score_function(child_code, fname, sandbox, test_pairs, seen_kills)
                if scores["kill_signature"]:
                    seen_kills.add(scores["kill_signature"])

                new_offspring.append({
                    "id": fid,
                    "code": child_code,
                    "function_name": fname,
                    "fitness": scores["fitness"],
                    "scores": scores,
                    "parent": parent["id"],
                    "generation": gen,
                })

        # Inject 2 random seeds (diversity injection)
        for _ in range(2):
            seed_code = random.choice(SEED_FUNCTIONS).strip()
            # Slightly perturb by renaming to avoid exact duplicates
            fname = extract_function_name(seed_code)
            if fname:
                new_name = f"{fname}_v{gen}_{random.randint(0, 999)}"
                seed_code = seed_code.replace(f"def {fname}(", f"def {new_name}(", 1)
                fid = _func_id(seed_code)
                scores = score_function(seed_code, new_name, Sandbox(timeout_s=5),
                                        test_pairs, seen_kills)
                new_offspring.append({
                    "id": fid,
                    "code": seed_code,
                    "function_name": new_name,
                    "fitness": scores["fitness"],
                    "scores": scores,
                    "parent": "seed_injection",
                    "generation": gen,
                })

        # Merge and select
        population.extend(new_offspring)

        # Deduplicate by id
        seen_ids = set()
        deduped = []
        for ind in population:
            if ind["id"] not in seen_ids:
                seen_ids.add(ind["id"])
                deduped.append(ind)
        population = deduped

        population.sort(key=lambda x: x["fitness"], reverse=True)
        population = population[:population_size]

        best = population[0]
        new_kills = sum(1 for o in new_offspring if o["scores"].get("novel_failure_bonus", 0) > 0)
        print(f"[GEN {gen}] pop={len(population)}, offspring={len(new_offspring)}, "
              f"best={best['fitness']:.3f} ({best['function_name']}), new_kills={new_kills}")

        # Log
        for ind in new_offspring:
            _log_individual(ind, gen)

        # Save surviving functions
        for ind in population[:5]:  # top 5
            fpath = EVOLVED_DIR / f"{ind['id']}.py"
            if not fpath.exists():
                fpath.write_text(ind["code"], encoding="utf-8")

    # Final summary
    print(f"\n{'='*60}")
    print(f"Evolution complete: {n_generations} generations")
    print(f"Population: {len(population)} functions")
    print(f"Unique kill signatures: {len(seen_kills)}")
    print(f"Best function: {population[0]['function_name']} (fitness={population[0]['fitness']:.3f})")
    print(f"Log: {EVOLUTION_LOG}")
    print(f"Evolved functions: {EVOLVED_DIR}")

    return population


def _log_individual(ind: dict, generation: int):
    """Append individual to evolution log."""
    entry = {
        "generation": generation,
        "function_id": ind["id"],
        "function_name": ind["function_name"],
        "code": ind["code"],
        "fitness": ind["fitness"],
        "battery_survival": ind["scores"]["battery_survival"],
        "novel_failure_bonus": ind["scores"]["novel_failure_bonus"],
        "parsimony": ind["scores"]["parsimony"],
        "complexity": ind["scores"].get("complexity", 0),
        "tests_run": ind["scores"]["tests_run"],
        "tests_survived": ind["scores"]["tests_survived"],
        "errors": ind["scores"]["errors"],
        "parent": ind["parent"],
        "timestamp": _timestamp(),
    }
    with open(EVOLUTION_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Search Evolver — evolutionary program synthesis")
    parser.add_argument("--generations", type=int, default=10)
    parser.add_argument("--population", type=int, default=20)
    parser.add_argument("--provider", type=str, default="deepseek",
                        choices=["deepseek", "openai", "claude", "gemini"])
    parser.add_argument("--dry-run", action="store_true",
                        help="Evaluate seeds only, no LLM calls")
    args = parser.parse_args()

    print(f"Search Evolver — {args.generations} generations, pop={args.population}, "
          f"provider={args.provider}" + (" (DRY RUN)" if args.dry_run else ""))

    evolve(
        n_generations=args.generations,
        population_size=args.population,
        provider=args.provider,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
