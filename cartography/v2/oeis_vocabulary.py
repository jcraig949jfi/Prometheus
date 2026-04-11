"""
OEIS Sequence Name Word Frequency: The Vocabulary of Mathematics
================================================================
Map the language of human mathematical knowledge by analysing word and
bigram frequencies in the ~394K OEIS sequence names.

Outputs: oeis_vocabulary_results.json
"""

import json
import re
import time
from collections import Counter
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent / "oeis" / "data"
NAMES_FILE = DATA_DIR / "oeis_names.json"
FUNGRIM_FILE = (
    Path(__file__).resolve().parent.parent / "fungrim" / "data" / "fungrim_index.json"
)
OUT_JSON = Path(__file__).resolve().parent / "oeis_vocabulary_results.json"

# ── Stop words (common English + maths boilerplate) ───────────────────
STOP_WORDS = {
    "the", "of", "a", "an", "in", "is", "for", "and", "or", "to", "with",
    "by", "that", "from", "on", "at", "as", "it", "its", "are", "be",
    "this", "which", "not", "all", "such", "if", "then", "also", "where",
    "when", "we", "can", "has", "have", "each", "every", "any", "no",
    "but", "so", "than", "into", "over", "between", "through", "about",
    "up", "out", "their", "there", "other", "one", "two", "some", "more",
    "most", "only", "these", "those", "same", "see", "cf", "i.e", "e.g",
    "etc", "given", "defined", "called", "least", "first", "second",
    "let", "i", "ii", "iii",
}

# Tokens to skip: pure numbers, single chars, A-numbers
SKIP_RE = re.compile(r"^(a?\d+|[a-z])$")


def tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alpha, filter stop words and noise."""
    tokens = re.findall(r"[a-z]{2,}", text.lower())
    return [t for t in tokens if t not in STOP_WORDS and not SKIP_RE.match(t)]


def bigrams(tokens: list[str]) -> list[tuple[str, str]]:
    return list(zip(tokens, tokens[1:]))


# ── Mathematical domain classifier ───────────────────────────────────
DOMAIN_KEYWORDS = {
    "number_theory": {
        "prime", "primes", "divisor", "divisors", "factor", "factors",
        "modular", "mod", "congruence", "residue", "gcd", "coprime",
        "squarefree", "totient", "euler", "fibonacci", "lucas",
        "quadratic", "sieve", "multiplicative", "arithmetic",
    },
    "combinatorics": {
        "permutation", "permutations", "partition", "partitions",
        "combination", "combinations", "binomial", "catalan", "stirling",
        "bell", "tree", "trees", "graph", "graphs", "path", "paths",
        "lattice", "walk", "walks", "tiling", "tilings", "arrangement",
        "derangement", "subset", "subsets", "polyomino", "polyominoes",
    },
    "algebra": {
        "group", "groups", "ring", "rings", "field", "fields",
        "polynomial", "polynomials", "coefficient", "coefficients",
        "matrix", "matrices", "determinant", "eigenvalue", "linear",
        "vector", "algebra", "algebraic", "module", "ideal",
    },
    "analysis": {
        "series", "sum", "sums", "integral", "continued", "fraction",
        "convergent", "expansion", "decimal", "digits", "constant",
        "zeta", "gamma", "bernoulli", "harmonic", "asymptotic",
    },
    "geometry_topology": {
        "triangle", "triangles", "polygon", "polygons", "polyhedra",
        "vertex", "vertices", "edge", "edges", "face", "faces",
        "plane", "cube", "sphere", "surface", "knot", "manifold",
        "dimension", "dimensional", "convex", "regular",
    },
    "logic_computation": {
        "boolean", "binary", "turing", "automaton", "automata",
        "cellular", "recursive", "computable", "decidable", "halting",
        "iteration", "recurrence", "sequence", "sequences",
    },
}


def classify_domains(word_counts: Counter) -> dict:
    """Score each domain by total frequency of its keywords in the corpus."""
    domain_scores = {}
    for domain, kws in DOMAIN_KEYWORDS.items():
        total = sum(word_counts.get(w, 0) for w in kws)
        hits = {w: word_counts[w] for w in kws if w in word_counts}
        domain_scores[domain] = {
            "total_frequency": total,
            "keyword_hits": dict(sorted(hits.items(), key=lambda x: -x[1])[:15]),
        }
    return dict(sorted(domain_scores.items(), key=lambda x: -x[1]["total_frequency"]))


def load_fungrim_vocabulary():
    """Extract vocabulary from Fungrim for comparison."""
    if not FUNGRIM_FILE.exists():
        return None
    with open(FUNGRIM_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # Module names as domain labels
    modules = list(data.get("module_stats", {}).keys())
    # Top symbols
    top_symbols = data.get("top_symbols", {})
    # Bridge symbols (operadic skeleton hubs)
    bridge_symbols = data.get("bridge_symbols", {})

    # Tokenize module names
    module_words = Counter()
    for m in modules:
        for w in m.replace("_", " ").split():
            if len(w) > 1:
                module_words[w.lower()] += 1

    return {
        "n_modules": len(modules),
        "n_symbols": data.get("n_symbols", 0),
        "n_bridge_symbols": data.get("n_bridge_symbols", 0),
        "top_symbols_top20": dict(
            sorted(top_symbols.items(), key=lambda x: -x[1])[:20]
        ),
        "bridge_symbols_top20": dict(
            sorted(bridge_symbols.items(), key=lambda x: -len(x[1]))[:20]
        ),
        "module_domain_words": dict(module_words.most_common(20)),
    }


def main():
    t0 = time.time()

    # ── Load OEIS names ───────────────────────────────────────────────
    print("Loading OEIS names...")
    with open(NAMES_FILE, encoding="utf-8") as f:
        names = json.load(f)
    n_seqs = len(names)
    print(f"  {n_seqs:,} sequences loaded.")

    # ── Tokenize ──────────────────────────────────────────────────────
    print("Tokenizing...")
    word_counter = Counter()
    bigram_counter = Counter()
    seq_lengths = []

    for _aid, name in names.items():
        tokens = tokenize(name)
        seq_lengths.append(len(tokens))
        word_counter.update(tokens)
        bigram_counter.update(bigrams(tokens))

    total_tokens = sum(word_counter.values())
    unique_words = len(word_counter)
    print(f"  {total_tokens:,} tokens, {unique_words:,} unique words.")

    # ── Top 50 words ──────────────────────────────────────────────────
    top50 = word_counter.most_common(50)
    print("\n-- Top 50 words --")
    for rank, (w, c) in enumerate(top50, 1):
        pct = 100 * c / total_tokens
        print(f"  {rank:2d}. {w:25s} {c:>8,}  ({pct:.2f}%)")

    # ── Top 30 bigrams ────────────────────────────────────────────────
    top30_bg = bigram_counter.most_common(30)
    print("\n-- Top 30 bigrams --")
    for rank, (bg, c) in enumerate(top30_bg, 1):
        label = f"{bg[0]} {bg[1]}"
        print(f"  {rank:2d}. {label:35s} {c:>7,}")

    # ── Domain classification ─────────────────────────────────────────
    print("\n-- Domain scores --")
    domain_scores = classify_domains(word_counter)
    for dom, info in domain_scores.items():
        print(f"  {dom:25s}  total_freq={info['total_frequency']:>8,}")

    # ── Fungrim comparison ────────────────────────────────────────────
    print("\n-- Fungrim vocabulary --")
    fungrim = load_fungrim_vocabulary()
    if fungrim:
        print(f"  Modules: {fungrim['n_modules']}, Symbols: {fungrim['n_symbols']}, "
              f"Bridge symbols: {fungrim['n_bridge_symbols']}")

        # Overlap: which OEIS top words appear as Fungrim module words?
        oeis_top_set = set(w for w, _ in top50)
        fungrim_module_set = set(fungrim["module_domain_words"].keys())
        overlap = oeis_top_set & fungrim_module_set
        print(f"  Overlap (OEIS top50 vs Fungrim module words): {sorted(overlap)}")

        # Which Fungrim top symbols map to OEIS top words?
        fungrim_sym_lower = {s.lower() for s in fungrim["top_symbols_top20"]}
        oeis_top100_set = set(w for w, _ in word_counter.most_common(100))
        sym_overlap = oeis_top100_set & fungrim_sym_lower
        print(f"  Overlap (OEIS top100 vs Fungrim top symbols): {sorted(sym_overlap)}")
    else:
        print("  Fungrim data not found.")

    # ── Hapax legomena and vocabulary shape ────────────────────────────
    hapax = sum(1 for w, c in word_counter.items() if c == 1)
    top10_share = sum(c for _, c in top50[:10]) / total_tokens

    # ── Sequence length stats ─────────────────────────────────────────
    import numpy as np
    sl = np.array(seq_lengths)

    # ── Assemble results ──────────────────────────────────────────────
    results = {
        "metadata": {
            "n_sequences": n_seqs,
            "total_tokens": total_tokens,
            "unique_words": unique_words,
            "hapax_legomena": hapax,
            "hapax_fraction": round(hapax / unique_words, 4),
            "top10_token_share": round(top10_share, 4),
            "mean_tokens_per_name": round(float(sl.mean()), 2),
            "median_tokens_per_name": float(np.median(sl)),
            "elapsed_seconds": round(time.time() - t0, 1),
        },
        "top50_words": [
            {"rank": i + 1, "word": w, "count": c,
             "pct": round(100 * c / total_tokens, 3)}
            for i, (w, c) in enumerate(top50)
        ],
        "top30_bigrams": [
            {"rank": i + 1, "bigram": f"{bg[0]} {bg[1]}", "count": c}
            for i, (bg, c) in enumerate(top30_bg)
        ],
        "domain_scores": domain_scores,
        "vocabulary_shape": {
            "description": "Zipf-like distribution statistics",
            "top1_pct": round(100 * top50[0][1] / total_tokens, 3),
            "top10_pct": round(100 * top10_share, 3),
            "top50_pct": round(
                100 * sum(c for _, c in top50) / total_tokens, 3
            ),
        },
    }

    if fungrim:
        results["fungrim_comparison"] = {
            "fungrim_top20_symbols": fungrim["top_symbols_top20"],
            "fungrim_bridge_top20": fungrim["bridge_symbols_top20"],
            "fungrim_module_words": fungrim["module_domain_words"],
            "overlap_oeis_top50_vs_fungrim_modules": sorted(
                oeis_top_set & fungrim_module_set
            ),
            "overlap_oeis_top100_vs_fungrim_symbols": sorted(
                oeis_top100_set & fungrim_sym_lower
            ),
            "interpretation": (
                "OEIS vocabulary is dominated by number theory and combinatorics "
                "(counting, primes, partitions). Fungrim vocabulary is dominated by "
                "analysis (special functions, constants, integrals). The two corpora "
                "are complementary: OEIS maps the discrete/combinatorial landscape, "
                "Fungrim maps the continuous/analytic landscape. Bridge concepts "
                "(e.g. 'zeta', 'bernoulli', 'euler') appear in both."
            ),
        }

    # ── Save ──────────────────────────────────────────────────────────
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {OUT_JSON}")
    print(f"Elapsed: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
