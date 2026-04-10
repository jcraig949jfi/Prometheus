"""
Frontier2 #11: Fungrim Formula Complexity vs OEIS Recurrence Order Correlation.

Strategy:
1. Load 3K Fungrim formulas and compute complexity (distinct operators + nesting
   depth + total node count) from the actual expression trees via pygrim.
2. Connect Fungrim formulas to OEIS sequences through shared mathematical
   symbols/function names found in OEIS formula text.
3. For connected OEIS sequences, extract recurrence order from formula text
   (linear recurrence patterns, a(n-k) lag detection).
4. Correlate: Spearman between formula complexity and mean connected-sequence
   recurrence order.
"""

import json, re, os, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]  # cartography/
FUNGRIM_DIR = ROOT / "fungrim" / "data"
OEIS_DIR = ROOT / "oeis" / "data"
OUT_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# 1. Load Fungrim formulas and compute expression-tree complexity
# ---------------------------------------------------------------------------

def load_fungrim_entries():
    """Load all Fungrim entries via pygrim and return expression trees."""
    sys.path.insert(0, str(FUNGRIM_DIR))
    import importlib

    formula_dir = FUNGRIM_DIR / "pygrim" / "formulas"
    for fname in os.listdir(formula_dir):
        if fname.endswith(".py") and fname != "__init__.py":
            mod_name = fname[:-3]
            try:
                importlib.import_module(f"pygrim.formulas.{mod_name}")
            except Exception:
                pass

    from pygrim.expr import all_entries
    return list(all_entries)


def analyze_expr(expr, depth=0):
    """Recursively compute (node_count, max_depth, distinct_operators)."""
    if expr.is_atom():
        return 1, depth, set()

    nodes = 1
    max_d = depth
    ops = set()

    h = expr.head()
    if h is not None and h.is_symbol():
        ops.add(h._symbol)

    for a in (expr.args() or []):
        n, d, o = analyze_expr(a, depth + 1)
        nodes += n
        max_d = max(max_d, d)
        ops |= o

    return nodes, max_d, ops


def extract_formula_complexity(entries):
    """
    For each entry that contains a Formula(...), compute complexity.
    Returns list of dicts with id, module, symbols, node_count, max_depth,
    n_distinct_ops, complexity_score.
    """
    results = []
    for entry in entries:
        eid = entry.id()
        if eid is None:
            continue

        # Find the Formula argument
        formula_expr = None
        for arg in (entry.args() or []):
            h = arg.head()
            if h and h.is_symbol() and h._symbol == "Formula":
                sub_args = arg.args()
                if sub_args:
                    formula_expr = sub_args[0]
                break

        if formula_expr is None:
            continue

        nodes, max_depth, ops = analyze_expr(formula_expr)
        complexity = len(ops) + max_depth + nodes

        # Extract symbol list
        syms = set()
        try:
            raw_syms = entry.symbols()
            syms = {str(s) if not isinstance(s, str) else s for s in raw_syms}
        except Exception:
            pass

        results.append({
            "id": eid,
            "symbols": sorted(str(s) for s in syms),
            "node_count": nodes,
            "max_depth": max_depth,
            "n_distinct_ops": len(ops),
            "distinct_ops": sorted(ops),
            "complexity_score": complexity,
        })

    return results


# ---------------------------------------------------------------------------
# 2. Build Fungrim symbol -> OEIS sequence mapping
# ---------------------------------------------------------------------------

# Map from Fungrim symbol names to search patterns in OEIS formula text.
# Only mathematically meaningful symbols (not structural ones like Equal, And).
SYMBOL_TO_OEIS_PATTERNS = {
    "AGM": [r"\bAGM\b", r"arithmetic[- ]geometric\s+mean"],
    "BernoulliB": [r"\bBernoulli\b"],
    "BellNumber": [r"\bBell\s+number", r"\bBell\("],
    "Binomial": [r"\bbinomial\b", r"\bC\(n,\s*k\)"],
    "CarlsonRC": [r"\bCarlson\b", r"\bR_C\b"],
    "CarlsonRD": [r"\bCarlson\b", r"\bR_D\b"],
    "CarlsonRF": [r"\bCarlson\b", r"\bR_F\b"],
    "CarlsonRJ": [r"\bCarlson\b", r"\bR_J\b"],
    "ChebyshevT": [r"\bChebyshev\b", r"\bT_?\("],
    "ChebyshevU": [r"\bChebyshev\b", r"\bU_?\("],
    "ConstCatalan": [r"\bCatalan\b"],
    "ConstGamma": [r"\bEuler[- ]Mascheroni\b", r"\bgamma\s*=\s*0\.577"],
    "Cos": [r"\bcos\b"],
    "DedekindEta": [r"\bDedekind\s+eta\b", r"\beta\("],
    "DigammaFunction": [r"\bdigamma\b", r"\bpsi\s*\("],
    "DirichletL": [r"\bDirichlet\s+L\b", r"\bL-function\b"],
    "DivisorSigma": [r"\bsigma_?\(", r"\bdivisor\s+sum\b"],
    "EisensteinE": [r"\bEisenstein\b", r"\bE_?\d"],
    "EllipticK": [r"\belliptic\s+integral\b", r"\bK\("],
    "Exp": [r"\bexp\b", r"\be\^"],
    "Factorial": [r"\bfactorial\b", r"n!"],
    "Fibonacci": [r"\bFibonacci\b", r"\bF\(n\)"],
    "GCD": [r"\bgcd\b"],
    "Gamma": [r"\bGamma\s*\(", r"\bGamma\s+function\b"],
    "GoldenRatio": [r"\bgolden\s+ratio\b", r"\bphi\b"],
    "HarmonicNumber": [r"\bharmonic\s+number\b", r"\bH_?\(n\)"],
    "HurwitzZeta": [r"\bHurwitz\s+zeta\b"],
    "Hypergeometric2F1": [r"\bhypergeometric\b", r"\b2F1\b"],
    "Hypergeometric1F1": [r"\bhypergeometric\b", r"\b1F1\b"],
    "JacobiTheta": [r"\bJacobi\s+theta\b", r"\btheta\b"],
    "LambertW": [r"\bLambert\s*W\b"],
    "LegendrePolynomial": [r"\bLegendre\s+polynomial\b", r"\bP_n\b"],
    "Log": [r"\blog\b", r"\bln\b"],
    "LogGamma": [r"\blog\s*Gamma\b", r"\blog\s*\(\s*Gamma"],
    "ModularJ": [r"\bmodular\s+j\b", r"\bj-invariant\b"],
    "MoebiusMu": [r"\bMoebius\b", r"\bMobius\b", r"\bmu\(n\)"],
    "PartitionsP": [r"\bpartition\b", r"\bp\(n\)"],
    "Pi": [r"\bPi\b", r"\bpi\b"],
    "PolyGamma": [r"\bpolygamma\b"],
    "PolyLog": [r"\bpolylogarithm\b", r"\bLi_"],
    "PrimeNumber": [r"\bprime\b"],
    "PrimePi": [r"\bPrimePi\b", r"\bpi\(n\)"],
    "Product": [r"\bproduct\b", r"\bprod\b"],
    "RiemannZeta": [r"\bRiemann\s+zeta\b", r"\bzeta\s*\("],
    "RisingFactorial": [r"\bPochhammer\b", r"\brising\s+factorial\b"],
    "Sin": [r"\bsin\b"],
    "StieltjesGamma": [r"\bStieltjes\b"],
    "StirlingS1": [r"\bStirling\b"],
    "StirlingS2": [r"\bStirling\b"],
    "Sum": [r"\bSum\b", r"\bsum\b"],
    "Tan": [r"\btan\b"],
    "Totient": [r"\btotient\b", r"\bphi\(n\)"],
    "WeierstrassP": [r"\bWeierstrass\b"],
}


def build_oeis_symbol_index():
    """
    For each OEIS sequence, collect which Fungrim-mappable symbols appear
    in its formula text. Returns {seq_id: set_of_symbols}.
    """
    # Pre-compile patterns
    compiled = {}
    for sym, patterns in SYMBOL_TO_OEIS_PATTERNS.items():
        compiled[sym] = [re.compile(p, re.IGNORECASE) for p in patterns]

    seq_symbols = defaultdict(set)
    formula_path = OEIS_DIR / "oeis_formulas.jsonl"

    with open(formula_path, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            seq_id = d["seq_id"]
            text = d.get("formula", "")

            for sym, pats in compiled.items():
                for pat in pats:
                    if pat.search(text):
                        seq_symbols[seq_id].add(sym)
                        break

    return seq_symbols


# ---------------------------------------------------------------------------
# 3. Extract recurrence orders from OEIS
# ---------------------------------------------------------------------------

def extract_recurrence_orders():
    """
    Parse OEIS formula text for recurrence order.
    Returns {seq_id: order}.
    """
    orders = {}
    formula_path = OEIS_DIR / "oeis_formulas.jsonl"

    with open(formula_path, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            seq_id = d["seq_id"]
            text = d.get("formula", "")

            # Method 1: "linear recurrence of order N"
            m = re.search(r"linear recurrence.*?order\s+(\d+)", text, re.IGNORECASE)
            if m:
                order = int(m.group(1))
                if seq_id not in orders or order > orders[seq_id]:
                    orders[seq_id] = order
                continue

            # Method 2: "N-term linear recurrence"
            m = re.search(r"(\d+)[- ]term\s+linear\s+recurrence", text, re.IGNORECASE)
            if m:
                order = int(m.group(1))
                if seq_id not in orders or order > orders[seq_id]:
                    orders[seq_id] = order
                continue

            # Method 3: a(n-k) lag extraction (when "recurrence" or "a(n) =" present)
            lags = re.findall(r"a\(n\s*-\s*(\d+)\)", text)
            if lags and ("recurrence" in text.lower() or
                         "a(n) =" in text.lower() or
                         "a(n)=" in text):
                order = max(int(x) for x in lags)
                if seq_id not in orders or order > orders[seq_id]:
                    orders[seq_id] = order

    return orders


# ---------------------------------------------------------------------------
# 4. Connect Fungrim formulas to OEIS sequences and correlate
# ---------------------------------------------------------------------------

def connect_and_correlate(formula_data, oeis_symbol_index, recurrence_orders):
    """
    For each Fungrim formula, find OEIS sequences that share >=2 mathematical
    symbols. For those with recurrence orders, compute mean recurrence order.
    Then correlate complexity vs mean recurrence order.
    """
    # Build inverted index: symbol -> set of OEIS seq_ids
    symbol_to_seqs = defaultdict(set)
    for seq_id, syms in oeis_symbol_index.items():
        for sym in syms:
            symbol_to_seqs[sym].add(seq_id)

    # Cap extreme recurrence orders (>100 likely parsing artifacts)
    MAX_RECURRENCE_ORDER = 100

    paired = []  # (complexity, mean_recurrence_order, n_connections)

    for fd in formula_data:
        formula_syms = set(fd["symbols"]) & set(SYMBOL_TO_OEIS_PATTERNS.keys())
        if len(formula_syms) < 1:
            continue

        # Find OEIS sequences sharing >=2 symbols with this formula
        # (or any if formula has only 1 math symbol)
        seq_sym_count = Counter()
        for sym in formula_syms:
            for seq_id in symbol_to_seqs.get(sym, set()):
                seq_sym_count[seq_id] += 1

        min_shared = 2 if len(formula_syms) >= 2 else 1
        connected_seqs = {s for s, c in seq_sym_count.items() if c >= min_shared}

        # Filter to those with recurrence orders, cap at MAX_RECURRENCE_ORDER
        rec_orders = []
        for seq_id in connected_seqs:
            if seq_id in recurrence_orders:
                order = recurrence_orders[seq_id]
                if order <= MAX_RECURRENCE_ORDER:
                    rec_orders.append(order)

        if not rec_orders:
            continue

        mean_order = np.mean(rec_orders)
        median_order = np.median(rec_orders)

        paired.append({
            "formula_id": fd["id"],
            "complexity_score": fd["complexity_score"],
            "node_count": fd["node_count"],
            "max_depth": fd["max_depth"],
            "n_distinct_ops": fd["n_distinct_ops"],
            "n_math_symbols": len(formula_syms),
            "math_symbols": sorted(formula_syms),
            "n_connected_oeis": len(connected_seqs),
            "n_with_recurrence": len(rec_orders),
            "mean_recurrence_order": round(mean_order, 4),
            "median_recurrence_order": round(median_order, 4),
        })

    return paired


def run_correlation(paired):
    """Compute Spearman correlations for multiple complexity measures."""
    if len(paired) < 10:
        return {"error": "too_few_pairs", "n_pairs": len(paired)}

    complexity = np.array([p["complexity_score"] for p in paired])
    nodes = np.array([p["node_count"] for p in paired])
    depth = np.array([p["max_depth"] for p in paired])
    n_ops = np.array([p["n_distinct_ops"] for p in paired])
    n_sym = np.array([p["n_math_symbols"] for p in paired])
    mean_rec = np.array([p["mean_recurrence_order"] for p in paired])
    median_rec = np.array([p["median_recurrence_order"] for p in paired])

    results = {}
    for name, x_arr in [
        ("complexity_score", complexity),
        ("node_count", nodes),
        ("max_depth", depth),
        ("n_distinct_ops", n_ops),
        ("n_math_symbols", n_sym),
    ]:
        for rec_name, y_arr in [
            ("mean_recurrence_order", mean_rec),
            ("median_recurrence_order", median_rec),
        ]:
            rho, p = stats.spearmanr(x_arr, y_arr)
            results[f"{name}_vs_{rec_name}"] = {
                "spearman_rho": round(float(rho), 6),
                "p_value": float(f"{p:.6e}"),
                "n_pairs": len(paired),
            }

    return results


# ---------------------------------------------------------------------------
# 5. Null model: shuffle complexity and recompute correlation
# ---------------------------------------------------------------------------

def null_model(paired, n_shuffles=1000):
    """Permutation null: shuffle complexity, compute Spearman distribution."""
    complexity = np.array([p["complexity_score"] for p in paired])
    mean_rec = np.array([p["mean_recurrence_order"] for p in paired])

    observed_rho, _ = stats.spearmanr(complexity, mean_rec)
    null_rhos = []

    rng = np.random.default_rng(42)
    for _ in range(n_shuffles):
        shuffled = rng.permutation(complexity)
        rho, _ = stats.spearmanr(shuffled, mean_rec)
        null_rhos.append(float(rho))

    null_rhos = np.array(null_rhos)
    z_score = (observed_rho - null_rhos.mean()) / (null_rhos.std() + 1e-12)

    return {
        "observed_rho": round(float(observed_rho), 6),
        "null_mean": round(float(null_rhos.mean()), 6),
        "null_std": round(float(null_rhos.std()), 6),
        "z_score": round(float(z_score), 4),
        "p_empirical": round(float(np.mean(np.abs(null_rhos) >= np.abs(observed_rho))), 6),
        "n_shuffles": n_shuffles,
    }


# ---------------------------------------------------------------------------
# 6. Binned analysis: complexity quintiles vs mean recurrence order
# ---------------------------------------------------------------------------

def binned_analysis(paired, n_bins=5):
    """Bin formulas by complexity quintile, report mean recurrence order per bin."""
    complexity = np.array([p["complexity_score"] for p in paired])
    mean_rec = np.array([p["mean_recurrence_order"] for p in paired])

    quantiles = np.percentile(complexity, np.linspace(0, 100, n_bins + 1))
    bins = []
    for i in range(n_bins):
        lo, hi = quantiles[i], quantiles[i + 1]
        if i < n_bins - 1:
            mask = (complexity >= lo) & (complexity < hi)
        else:
            mask = (complexity >= lo) & (complexity <= hi)

        if mask.sum() == 0:
            continue

        bins.append({
            "bin": i + 1,
            "complexity_range": [round(float(lo), 1), round(float(hi), 1)],
            "n_formulas": int(mask.sum()),
            "mean_recurrence_order": round(float(mean_rec[mask].mean()), 4),
            "median_recurrence_order": round(float(np.median(mean_rec[mask])), 4),
            "std_recurrence_order": round(float(mean_rec[mask].std()), 4),
        })

    return bins


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("Frontier2 #11: Fungrim Complexity vs OEIS Recurrence Order")
    print("=" * 60)

    # Step 1: Load Fungrim
    print("\n[1/5] Loading Fungrim expression trees...")
    entries = load_fungrim_entries()
    print(f"  Loaded {len(entries)} Fungrim entries")

    formula_data = extract_formula_complexity(entries)
    print(f"  {len(formula_data)} formulas with computable complexity")

    complexities = [f["complexity_score"] for f in formula_data]
    print(f"  Complexity range: [{min(complexities)}, {max(complexities)}]")
    print(f"  Complexity mean: {np.mean(complexities):.1f}, median: {np.median(complexities):.1f}")

    # Step 2: Build OEIS symbol index
    print("\n[2/5] Building OEIS symbol index...")
    oeis_sym_index = build_oeis_symbol_index()
    print(f"  {len(oeis_sym_index)} OEIS sequences with matched symbols")

    # Step 3: Extract recurrence orders
    print("\n[3/5] Extracting recurrence orders from OEIS...")
    rec_orders = extract_recurrence_orders()
    print(f"  {len(rec_orders)} sequences with recurrence order")

    # Overlap
    both = set(oeis_sym_index.keys()) & set(rec_orders.keys())
    print(f"  {len(both)} sequences have both symbol match and recurrence order")

    # Step 4: Connect and correlate
    print("\n[4/5] Connecting Fungrim formulas to OEIS sequences...")
    paired = connect_and_correlate(formula_data, oeis_sym_index, rec_orders)
    print(f"  {len(paired)} Fungrim formulas connected to OEIS with recurrences")

    if len(paired) < 10:
        print("  ERROR: Too few pairs for meaningful correlation")
        result = {
            "status": "insufficient_data",
            "n_fungrim_formulas": len(formula_data),
            "n_oeis_with_symbols": len(oeis_sym_index),
            "n_oeis_with_recurrence": len(rec_orders),
            "n_paired": len(paired),
        }
        with open(OUT_DIR / "fungrim_complexity_recurrence_results.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # Correlations
    print("\n[5/5] Computing correlations...")
    correlations = run_correlation(paired)

    # Primary result
    primary = correlations.get("complexity_score_vs_mean_recurrence_order", {})
    print(f"\n  PRIMARY: complexity_score vs mean_recurrence_order")
    print(f"    Spearman rho = {primary.get('spearman_rho', 'N/A')}")
    print(f"    p-value      = {primary.get('p_value', 'N/A')}")
    print(f"    n_pairs      = {primary.get('n_pairs', 'N/A')}")

    # Null model
    print("\n  Running permutation null (1000 shuffles)...")
    null = null_model(paired)
    print(f"    Observed rho: {null['observed_rho']}")
    print(f"    Null mean:    {null['null_mean']} +/- {null['null_std']}")
    print(f"    Z-score:      {null['z_score']}")
    print(f"    p_empirical:  {null['p_empirical']}")

    # Binned analysis
    bins = binned_analysis(paired)
    print("\n  Binned analysis (complexity quintiles):")
    for b in bins:
        print(f"    Bin {b['bin']}: complexity {b['complexity_range']}, "
              f"mean_rec_order = {b['mean_recurrence_order']:.2f} "
              f"(n={b['n_formulas']})")

    # Summary statistics
    sym_counts = Counter()
    for p in paired:
        for s in p["math_symbols"]:
            sym_counts[s] += 1

    # Assemble results
    result = {
        "status": "complete",
        "n_fungrim_formulas_total": len(formula_data),
        "n_oeis_with_symbols": len(oeis_sym_index),
        "n_oeis_with_recurrence": len(rec_orders),
        "n_oeis_with_both": len(both),
        "n_paired_formulas": len(paired),
        "complexity_stats": {
            "min": int(min(complexities)),
            "max": int(max(complexities)),
            "mean": round(float(np.mean(complexities)), 2),
            "median": round(float(np.median(complexities)), 2),
        },
        "correlations": correlations,
        "null_model": null,
        "binned_analysis": bins,
        "top_bridging_symbols": [
            {"symbol": s, "count": c} for s, c in sym_counts.most_common(20)
        ],
        "interpretation": _interpret(primary, null, bins),
        "sample_pairs": paired[:20],
    }

    out_path = OUT_DIR / "fungrim_complexity_recurrence_results.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n  Results saved to {out_path}")
    print(f"\n  INTERPRETATION: {result['interpretation']['summary']}")


def _interpret(primary, null, bins):
    """Generate human-readable interpretation."""
    rho = primary.get("spearman_rho", 0)
    p = primary.get("p_value", 1)
    z = null.get("z_score", 0)

    if abs(rho) < 0.05 and p > 0.05:
        strength = "negligible"
    elif abs(rho) < 0.1:
        strength = "very weak"
    elif abs(rho) < 0.3:
        strength = "weak"
    elif abs(rho) < 0.5:
        strength = "moderate"
    else:
        strength = "strong"

    direction = "positive" if rho > 0 else "negative"

    if p < 0.001 and abs(z) > 3:
        significance = "highly significant (survives null)"
    elif p < 0.05 and abs(z) > 2:
        significance = "significant (survives null)"
    elif p < 0.05:
        significance = "nominally significant (marginal null survival)"
    else:
        significance = "not significant"

    # Check monotonicity in bins
    if len(bins) >= 3:
        rec_orders = [b["mean_recurrence_order"] for b in bins]
        monotone = all(rec_orders[i] <= rec_orders[i+1] for i in range(len(rec_orders)-1))
        anti_monotone = all(rec_orders[i] >= rec_orders[i+1] for i in range(len(rec_orders)-1))
    else:
        monotone = anti_monotone = False

    summary = (
        f"{strength.capitalize()} {direction} correlation (rho={rho:.4f}, p={p:.2e}). "
        f"{significance}. "
        f"Z-score vs null: {z:.2f}. "
    )

    if monotone:
        summary += "Bins show monotonic increase in recurrence order with complexity."
    elif anti_monotone:
        summary += "Bins show monotonic decrease in recurrence order with complexity."
    else:
        summary += "No monotonic trend in binned analysis."

    return {
        "summary": summary,
        "correlation_strength": strength,
        "direction": direction,
        "significance": significance,
        "bin_monotonic": monotone,
    }


if __name__ == "__main__":
    main()
