"""
Diverse Evolver — Launch multiple evolution runs with different strategies.
============================================================================
Each run focuses on a different aspect of the search space:
  1. Distribution shape hunters (KS, Wasserstein, histogram)
  2. Nonlinear correlation finders (Spearman, MI, distance correlation)
  3. Spectral/frequency analyzers (FFT, autocorrelation, periodicity)
  4. Tail behavior detectives (extreme values, heavy tails, outlier patterns)
  5. Structural fingerprint matchers (moment vectors, quantile profiles)

Usage:
    python evolve_diverse.py                    # all 5 strategies, 20 gen each
    python evolve_diverse.py --generations 50   # longer runs
    python evolve_diverse.py --strategy 3       # only spectral
"""

import argparse
import json
import sys
import time
import random
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sandbox import Sandbox, validate_code, complexity_score, extract_function_name

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from falsification_battery import run_battery

OUTPUT_DIR = REPO / "cartography" / "convergence" / "data"
EVOLVED_DIR = Path(__file__).resolve().parent / "evolved_functions"
EVOLVED_DIR.mkdir(exist_ok=True)

STRATEGIES = {
    1: {
        "name": "DISTRIBUTION_SHAPE",
        "description": "Hunt for shared distribution shapes across domains",
        "seed": '''
def search_distribution_shape(values_a, values_b):
    import numpy as np
    from scipy import stats
    n = min(len(values_a), len(values_b), 500)
    if n < 20:
        return {"statistic": 0, "p_value": 1.0, "description": "insufficient data"}
    a, b = np.array(values_a[:n], dtype=float), np.array(values_b[:n], dtype=float)
    a = (a - a.mean()) / (a.std() + 1e-10)
    b = (b - b.mean()) / (b.std() + 1e-10)
    ks_stat, p = stats.ks_2samp(a, b)
    return {"statistic": float(1 - ks_stat), "p_value": float(p), "description": f"shape similarity={1-ks_stat:.4f}"}
''',
        "targets": [
            "compare histogram shapes using Earth Mover Distance",
            "compare quantile-quantile divergence between datasets",
            "test if two datasets share the same tail decay rate",
            "compare empirical CDFs using Anderson-Darling",
            "test if normalized distributions share modes",
        ],
    },
    2: {
        "name": "NONLINEAR_CORRELATION",
        "description": "Find nonlinear relationships invisible to Pearson",
        "seed": '''
def search_nonlinear(values_a, values_b):
    import numpy as np
    from scipy import stats
    n = min(len(values_a), len(values_b), 500)
    if n < 20:
        return {"statistic": 0, "p_value": 1.0, "description": "insufficient data"}
    a, b = np.array(values_a[:n], dtype=float), np.array(values_b[:n], dtype=float)
    rho, p = stats.spearmanr(a, b)
    return {"statistic": float(abs(rho)), "p_value": float(p), "description": f"Spearman rho={rho:.4f}"}
''',
        "targets": [
            "compute distance correlation (dcor) between datasets",
            "test for monotonic but nonlinear relationship using rank statistics",
            "check if the conditional variance of B given A is non-constant",
            "use maximal information coefficient to find any functional relationship",
            "test if sorting by A reveals structure in B that random ordering doesn't",
        ],
    },
    3: {
        "name": "SPECTRAL_FREQUENCY",
        "description": "Find shared periodic or spectral structure",
        "seed": '''
def search_spectral(values_a, values_b):
    import numpy as np
    n = min(len(values_a), len(values_b), 256)
    if n < 32:
        return {"statistic": 0, "p_value": 1.0, "description": "insufficient data"}
    a, b = np.array(values_a[:n], dtype=float), np.array(values_b[:n], dtype=float)
    fa, fb = np.abs(np.fft.rfft(a - a.mean())), np.abs(np.fft.rfft(b - b.mean()))
    fa, fb = fa / (fa.sum() + 1e-10), fb / (fb.sum() + 1e-10)
    cos_sim = float(np.dot(fa, fb) / (np.linalg.norm(fa) * np.linalg.norm(fb) + 1e-10))
    return {"statistic": cos_sim, "p_value": 0.05, "description": f"spectral cosine={cos_sim:.4f}"}
''',
        "targets": [
            "compare power spectra using cross-spectral density",
            "test if autocorrelation decay rates match between datasets",
            "find shared periodicities using Lomb-Scargle periodogram",
            "compare wavelet coefficient distributions",
            "test if the dominant frequency in A appears in B",
        ],
    },
    4: {
        "name": "TAIL_BEHAVIOR",
        "description": "Compare extreme value and tail structure",
        "seed": '''
def search_tails(values_a, values_b):
    import numpy as np
    from scipy import stats
    n = min(len(values_a), len(values_b), 500)
    if n < 30:
        return {"statistic": 0, "p_value": 1.0, "description": "insufficient data"}
    a, b = np.array(values_a[:n], dtype=float), np.array(values_b[:n], dtype=float)
    top_a, top_b = np.sort(a)[-n//10:], np.sort(b)[-n//10:]
    ks, p = stats.ks_2samp(top_a, top_b)
    return {"statistic": float(1 - ks), "p_value": float(p), "description": f"tail match={1-ks:.4f}"}
''',
        "targets": [
            "compare generalized Pareto fits on upper tails",
            "test if extreme value indices match between datasets",
            "compare the ratio of max to mean across datasets",
            "test if outlier patterns (values > 3 sigma) are correlated",
            "compare heavy-tail exponents using Hill estimator",
        ],
    },
    5: {
        "name": "STRUCTURAL_FINGERPRINT",
        "description": "Match structural signatures: moments, gaps, spacing patterns",
        "seed": '''
def search_fingerprint(values_a, values_b):
    import numpy as np
    from scipy import stats
    n = min(len(values_a), len(values_b), 500)
    if n < 20:
        return {"statistic": 0, "p_value": 1.0, "description": "insufficient data"}
    a, b = np.array(values_a[:n], dtype=float), np.array(values_b[:n], dtype=float)
    def fp(x):
        return np.array([np.mean(x), np.std(x), stats.skew(x), stats.kurtosis(x)])
    fa, fb = fp(a), fp(b)
    dist = float(np.linalg.norm(fa - fb) / (np.linalg.norm(fa) + 1e-10))
    return {"statistic": float(max(0, 1 - dist)), "p_value": 0.05, "description": f"fingerprint match={1-dist:.4f}"}
''',
        "targets": [
            "compare gap spacing distributions (consecutive differences)",
            "test if the digit frequency distributions match",
            "compare Benford's law deviation profiles",
            "test if the ratio distributions (a[i+1]/a[i]) match",
            "compare the fractal dimension estimates of both sequences",
        ],
    },
}

SYSTEM_PROMPT = (
    "You are a mathematician writing Python search functions. "
    "Be concise: max 15 lines, no comments, no docstrings. "
    "Use only numpy and scipy.stats."
)


def _mutate(parent_code, target, provider="deepseek"):
    prompt = (
        f"Here is a search function:\n\n{parent_code}\n\n"
        f"Modify it to: {target}\n\n"
        "Requirements:\n"
        '- Accept (values_a, values_b), return {"statistic": float, "p_value": float, "description": str}\n'
        "- Only numpy and scipy.stats. MAXIMUM 15 lines. No comments.\n"
        "- Return ONLY the Python function."
    )
    try:
        from council_client import ask
        response = ask(prompt, system=SYSTEM_PROMPT, provider=provider,
                       max_tokens=1024, temperature=0.8)
        # Extract code block
        import re
        m = re.search(r'```python\s*(.*?)```', response, re.DOTALL)
        if m:
            return m.group(1).strip()
        m = re.search(r'(def search_\w+\(.*?\n(?:    .*\n)*)', response)
        if m:
            return m.group(1).strip()
        if 'def search_' in response or 'def ' in response:
            lines = response.strip().split('\n')
            start = next((i for i, l in enumerate(lines) if l.strip().startswith('def ')), None)
            if start is not None:
                return '\n'.join(lines[start:]).strip()
        return None
    except Exception as e:
        print(f"    MUTATE ERROR: {e}")
        return None


def _score(code, fname, sandbox, test_pairs):
    """Score a function: run on test pairs, battery on results."""
    total_pass = 0
    total_tests = 0
    executes = 0

    for a, b in test_pairs:
        result = sandbox.execute(code, fname, a, b)
        if not result["success"]:
            continue
        r = result["result"]
        if not isinstance(r, dict) or "statistic" not in r:
            continue
        executes += 1

        # Only run battery if the function claims significance
        if r.get("p_value", 1.0) < 0.1 and abs(r.get("statistic", 0)) > 0.05:
            try:
                verdict, tests = run_battery(
                    np.array(a, dtype=float), np.array(b, dtype=float),
                    claim=r.get("description", "evolved"))
                if isinstance(tests, list):
                    n_pass = sum(1 for t in tests if t.get("verdict") == "PASS")
                    total_pass += n_pass
                    total_tests += len(tests)
                elif isinstance(tests, dict):
                    n_pass = sum(1 for v in tests.values() if v.get("verdict") == "PASS")
                    total_pass += n_pass
                    total_tests += len(tests)
            except Exception:
                pass

    cx = complexity_score(code)
    parsimony = max(0, 1.0 - cx / 300)
    exec_rate = executes / max(len(test_pairs), 1)
    battery_rate = total_pass / max(total_tests, 1)

    fitness = 0.3 * battery_rate + 0.3 * exec_rate + 0.2 * parsimony + 0.2 * (total_tests > 0)
    return {"fitness": fitness, "battery_rate": battery_rate, "exec_rate": exec_rate,
            "complexity": cx, "total_tests": total_tests, "total_pass": total_pass}


def _make_test_pairs():
    """Generate synthetic test pairs for evaluation."""
    import numpy as np
    rng = np.random.RandomState(42)
    pairs = [
        (rng.normal(0, 1, 100).tolist(), rng.normal(0, 1, 100).tolist()),       # uncorrelated normal
        (rng.exponential(2, 100).tolist(), rng.exponential(2.1, 100).tolist()),   # similar exponential
        (list(range(100)), [x**2 + rng.normal(0, 5) for x in range(100)]),       # quadratic
        (rng.poisson(5, 100).tolist(), rng.poisson(5.5, 100).tolist()),          # similar Poisson
        (rng.uniform(0, np.pi, 100).tolist(), np.arccos(rng.uniform(-1, 1, 100)).tolist()),  # angle distributions
    ]
    return pairs


def run_strategy(strategy_id, n_generations=20, provider="deepseek"):
    """Run one evolutionary strategy."""
    import numpy as np
    strat = STRATEGIES[strategy_id]
    name = strat["name"]
    seed = strat["seed"].strip()
    targets = strat["targets"]

    print(f"\n{'='*60}")
    print(f"  STRATEGY {strategy_id}: {name}")
    print(f"  {strat['description']}")
    print(f"  {n_generations} generations, {len(targets)} mutation targets")
    print(f"{'='*60}")

    sandbox = Sandbox(timeout_s=5)
    test_pairs = _make_test_pairs()

    # Initialize
    fname = extract_function_name(seed)
    if not fname:
        print(f"  ERROR: could not extract function name from seed")
        return

    scores = _score(seed, fname, sandbox, test_pairs)
    population = [{"code": seed, "name": fname, "fitness": scores["fitness"],
                    "scores": scores, "generation": 0, "parent": "seed"}]
    best = population[0]

    log_file = OUTPUT_DIR / f"evolution_{name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

    print(f"  [GEN 0] seed={fname} fitness={scores['fitness']:.3f}")

    for gen in range(1, n_generations + 1):
        target = targets[gen % len(targets)]
        parent = max(population, key=lambda x: x["fitness"])

        child_code = _mutate(parent["code"], target, provider)
        if child_code is None:
            continue

        safe, reason = validate_code(child_code)
        if not safe:
            continue

        cx = complexity_score(child_code)
        if cx > 300:
            print(f"  [GEN {gen}] too complex: {cx}")
            continue

        child_fname = extract_function_name(child_code)
        if not child_fname:
            continue

        child_scores = _score(child_code, child_fname, sandbox, test_pairs)
        child = {"code": child_code, "name": child_fname,
                 "fitness": child_scores["fitness"], "scores": child_scores,
                 "generation": gen, "parent": parent["name"]}

        population.append(child)
        if child["fitness"] > best["fitness"]:
            best = child
            # Save best
            out_path = EVOLVED_DIR / f"evolved_{name.lower()}_{child_fname}.py"
            out_path.write_text(child_code)

        # Log
        with open(log_file, "a") as f:
            f.write(json.dumps({
                "strategy": name, "generation": gen, "function": child_fname,
                "fitness": child["fitness"], "target": target,
                **child_scores
            }) + "\n")

        tag = "NEW BEST" if child is best else ""
        print(f"  [GEN {gen}] {child_fname} fit={child['fitness']:.3f} "
              f"bat={child_scores['battery_rate']:.2f} exec={child_scores['exec_rate']:.2f} {tag}")

        # Cull worst if population grows
        if len(population) > 15:
            population.sort(key=lambda x: x["fitness"], reverse=True)
            population = population[:10]

    print(f"\n  Strategy {name} complete: best={best['name']} fitness={best['fitness']:.3f}")
    return best


def main():
    parser = argparse.ArgumentParser(description="Diverse Evolver")
    parser.add_argument("--generations", type=int, default=20, help="Generations per strategy")
    parser.add_argument("--strategy", type=int, default=0, help="Run one strategy (1-5, 0=all)")
    parser.add_argument("--provider", type=str, default="deepseek", help="LLM provider")
    args = parser.parse_args()

    print("=" * 60)
    print(f"  DIVERSE EVOLVER — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Strategies: {'all 5' if args.strategy == 0 else f'#{args.strategy}'}")
    print(f"  Generations: {args.generations} per strategy")
    print(f"  Provider: {args.provider}")
    print("=" * 60)

    t0 = time.time()
    results = []

    strategies = [args.strategy] if args.strategy > 0 else list(STRATEGIES.keys())

    for sid in strategies:
        best = run_strategy(sid, n_generations=args.generations, provider=args.provider)
        if best:
            results.append({"strategy": STRATEGIES[sid]["name"], "best_fitness": best["fitness"],
                            "best_function": best["name"]})

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"  DIVERSE EVOLUTION COMPLETE — {elapsed:.0f}s")
    for r in results:
        print(f"  {r['strategy']:25s} best={r['best_function']:25s} fit={r['best_fitness']:.3f}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
