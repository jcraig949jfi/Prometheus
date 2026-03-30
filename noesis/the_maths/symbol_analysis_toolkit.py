"""
Symbol Analysis Toolkit — General tools for analyzing ANY symbolic sequence (undeciphered systems)

Connects to: [geometric_reading_transforms]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "symbol_analysis_toolkit"
OPERATIONS = {}


def entropy_rate_multiscale(x):
    """Compute Shannon entropy at multiple block sizes.
    Input: array of symbol indices (integers). Output: array of [H_1, H_2, H_3, ...] per-symbol entropy.
    H_n = (1/n) * H(n-grams) estimates the entropy rate as n grows."""
    symbols = np.round(x).astype(int)
    symbols = symbols - np.min(symbols)  # shift to 0-based
    max_block = min(5, len(symbols))
    entropies = []
    for block_size in range(1, max_block + 1):
        # Extract n-grams
        ngrams = []
        for i in range(len(symbols) - block_size + 1):
            ngram = tuple(symbols[i:i + block_size])
            ngrams.append(ngram)
        # Count frequencies
        from collections import Counter
        counts = Counter(ngrams)
        total = len(ngrams)
        if total == 0:
            entropies.append(0.0)
            continue
        probs = np.array(list(counts.values())) / total
        H = -np.sum(probs * np.log2(probs + 1e-15))
        entropies.append(H / block_size)
    return np.array(entropies)


OPERATIONS["entropy_rate_multiscale"] = {
    "fn": entropy_rate_multiscale,
    "input_type": "array",
    "output_type": "array",
    "description": "Shannon entropy rate at block sizes 1..5"
}


def zipf_compliance_test(x):
    """Test Zipf's law compliance: rank*frequency ~ constant for natural languages.
    Input: array of symbol indices. Output: array [slope, r_squared, is_zipfian].
    Zipf's law: log(freq) = -alpha * log(rank) + C, alpha ~ 1 for language."""
    from collections import Counter
    symbols = np.round(x).astype(int)
    counts = Counter(symbols)
    freqs = np.sort(list(counts.values()))[::-1]
    if len(freqs) < 3:
        return np.array([0.0, 0.0, 0.0])
    ranks = np.arange(1, len(freqs) + 1, dtype=float)
    log_ranks = np.log(ranks)
    log_freqs = np.log(freqs.astype(float) + 1e-15)
    # Linear regression in log-log space
    A = np.vstack([log_ranks, np.ones_like(log_ranks)]).T
    result = np.linalg.lstsq(A, log_freqs, rcond=None)
    slope = result[0][0]
    # R^2
    pred = A @ result[0]
    ss_res = np.sum((log_freqs - pred) ** 2)
    ss_tot = np.sum((log_freqs - np.mean(log_freqs)) ** 2)
    r_squared = 1.0 - ss_res / (ss_tot + 1e-15)
    is_zipfian = 1.0 if (r_squared > 0.8 and -2.0 < slope < -0.5) else 0.0
    return np.array([slope, r_squared, is_zipfian])


OPERATIONS["zipf_compliance_test"] = {
    "fn": zipf_compliance_test,
    "input_type": "array",
    "output_type": "array",
    "description": "Test Zipf's law: [slope, R^2, is_zipfian]"
}


def vocabulary_growth_heaps(x):
    """Heaps' law: V(n) = K * n^beta. Estimate K and beta from cumulative vocabulary growth.
    Input: array of symbol indices (sequence). Output: array [K, beta, V_final].
    beta ~ 0.5-0.7 for natural languages."""
    symbols = np.round(x).astype(int)
    n = len(symbols)
    if n < 3:
        return np.array([1.0, 1.0, float(len(np.unique(symbols)))])
    # Compute vocabulary at each position
    seen = set()
    vocab_curve = []
    positions = []
    step = max(1, n // 20)
    for i in range(n):
        seen.add(symbols[i])
        if (i + 1) % step == 0 or i == n - 1:
            vocab_curve.append(len(seen))
            positions.append(i + 1)
    V = np.array(vocab_curve, dtype=float)
    N = np.array(positions, dtype=float)
    # Fit log(V) = log(K) + beta * log(N)
    log_N = np.log(N)
    log_V = np.log(V + 1e-15)
    A = np.vstack([log_N, np.ones_like(log_N)]).T
    result = np.linalg.lstsq(A, log_V, rcond=None)
    beta = result[0][0]
    K = np.exp(result[0][1])
    return np.array([K, beta, float(len(seen))])


OPERATIONS["vocabulary_growth_heaps"] = {
    "fn": vocabulary_growth_heaps,
    "input_type": "array",
    "output_type": "array",
    "description": "Heaps' law fit: [K, beta, V_final]"
}


def bigram_transition_matrix(x):
    """Construct bigram transition probability matrix P(s_j | s_i).
    Input: array of symbol indices. Output: array (flattened transition matrix)."""
    symbols = np.round(x).astype(int)
    symbols = symbols - np.min(symbols)
    vocab = int(np.max(symbols)) + 1
    vocab = min(vocab, 50)  # cap for memory
    trans = np.zeros((vocab, vocab))
    for i in range(len(symbols) - 1):
        s_i = min(symbols[i], vocab - 1)
        s_j = min(symbols[i + 1], vocab - 1)
        trans[s_i, s_j] += 1.0
    # Normalize rows to probabilities
    row_sums = trans.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    trans /= row_sums
    return trans.flatten()


OPERATIONS["bigram_transition_matrix"] = {
    "fn": bigram_transition_matrix,
    "input_type": "array",
    "output_type": "array",
    "description": "Bigram transition probability matrix P(s_j | s_i)"
}


def trigram_frequency(x):
    """Compute trigram frequencies.
    Input: array of symbol indices. Output: array of top trigram counts (sorted descending)."""
    from collections import Counter
    symbols = np.round(x).astype(int)
    trigrams = []
    for i in range(len(symbols) - 2):
        trigrams.append(tuple(symbols[i:i+3]))
    counts = Counter(trigrams)
    sorted_counts = sorted(counts.values(), reverse=True)
    return np.array(sorted_counts[:min(len(sorted_counts), 20)], dtype=float)


OPERATIONS["trigram_frequency"] = {
    "fn": trigram_frequency,
    "input_type": "array",
    "output_type": "array",
    "description": "Top trigram frequencies (descending)"
}


def writing_vs_decoration_score(x):
    """Score whether a symbol sequence looks like writing vs decorative pattern.
    Input: array of symbol indices. Output: scalar score [0=decoration, 1=writing].
    Based on: entropy (writing: 3-5 bits), Zipf compliance, vocabulary ratio, repetition."""
    symbols = np.round(x).astype(int)
    n = len(symbols)
    if n < 5:
        return np.float64(0.5)
    score = 0.0
    # 1. Entropy check (writing: moderate entropy ~3-5 bits per symbol)
    from collections import Counter
    counts = Counter(symbols)
    probs = np.array(list(counts.values())) / n
    H = -np.sum(probs * np.log2(probs + 1e-15))
    if 2.0 < H < 6.0:
        score += 0.3
    elif H < 1.0:
        score -= 0.2  # Too repetitive -> decoration
    # 2. Vocabulary ratio (writing: typically vocab/n ~ 0.1-0.5)
    vocab_ratio = len(counts) / n
    if 0.05 < vocab_ratio < 0.6:
        score += 0.2
    # 3. Zipf-like distribution
    freqs = np.sort(list(counts.values()))[::-1]
    if len(freqs) >= 3:
        # Check if top frequency is not too dominant
        if freqs[0] / n < 0.5:
            score += 0.2
    # 4. Non-trivial bigram structure
    bigrams = set()
    for i in range(n - 1):
        bigrams.add((symbols[i], symbols[i+1]))
    bigram_ratio = len(bigrams) / max(n - 1, 1)
    if 0.1 < bigram_ratio < 0.8:
        score += 0.2
    # 5. Low immediate repetition (writing avoids xxx patterns)
    repeats = sum(1 for i in range(n-1) if symbols[i] == symbols[i+1])
    repeat_rate = repeats / max(n-1, 1)
    if repeat_rate < 0.3:
        score += 0.1
    return np.float64(np.clip(score, 0.0, 1.0))


OPERATIONS["writing_vs_decoration_score"] = {
    "fn": writing_vs_decoration_score,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Score [0,1] for writing vs decoration classification"
}


def information_capacity_estimate(x):
    """Estimate information capacity of a symbol system in bits per symbol.
    Input: array of symbol indices. Output: scalar (conditional entropy H(X_n | X_{n-1})).
    Lower bound on encoding capacity."""
    from collections import Counter
    symbols = np.round(x).astype(int)
    n = len(symbols)
    if n < 3:
        return np.float64(0.0)
    # Bigram conditional entropy H(X_n | X_{n-1})
    bigram_counts = Counter()
    unigram_counts = Counter()
    for i in range(n - 1):
        bigram_counts[(symbols[i], symbols[i+1])] += 1
        unigram_counts[symbols[i]] += 1
    H_cond = 0.0
    total_bigrams = n - 1
    for (s_i, s_j), count in bigram_counts.items():
        p_ij = count / total_bigrams
        p_j_given_i = count / unigram_counts[s_i]
        H_cond -= p_ij * np.log2(p_j_given_i + 1e-15)
    return np.float64(H_cond)


OPERATIONS["information_capacity_estimate"] = {
    "fn": information_capacity_estimate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Information capacity estimate via conditional entropy H(X_n|X_{n-1})"
}


def positional_frequency_profile(x):
    """Compute symbol frequency as function of position within a "line" or segment.
    Input: array of symbol indices. Output: array of entropy at each position quintile.
    Useful for detecting positional constraints (e.g., certain glyphs only at line start)."""
    from collections import Counter
    symbols = np.round(x).astype(int)
    n = len(symbols)
    n_bins = min(5, n)
    bin_size = max(n // n_bins, 1)
    entropies = []
    for b in range(n_bins):
        start = b * bin_size
        end = min((b + 1) * bin_size, n)
        seg = symbols[start:end]
        if len(seg) == 0:
            entropies.append(0.0)
            continue
        counts = Counter(seg)
        probs = np.array(list(counts.values())) / len(seg)
        H = -np.sum(probs * np.log2(probs + 1e-15))
        entropies.append(H)
    return np.array(entropies)


OPERATIONS["positional_frequency_profile"] = {
    "fn": positional_frequency_profile,
    "input_type": "array",
    "output_type": "array",
    "description": "Entropy profile across positional quintiles of the sequence"
}


def symbol_burstiness(x):
    """Measure burstiness of symbol occurrences (Goh-Barabasi burstiness parameter).
    Input: array of symbol indices. Output: scalar B = (sigma_tau - mu_tau)/(sigma_tau + mu_tau).
    B=1 maximally bursty, B=0 Poisson, B=-1 periodic."""
    from collections import Counter
    symbols = np.round(x).astype(int)
    n = len(symbols)
    if n < 5:
        return np.float64(0.0)
    # Compute inter-event times for the most common symbol
    counts = Counter(symbols)
    most_common = counts.most_common(1)[0][0]
    positions = np.where(symbols == most_common)[0]
    if len(positions) < 3:
        return np.float64(0.0)
    inter_times = np.diff(positions).astype(float)
    mu = np.mean(inter_times)
    sigma = np.std(inter_times)
    if mu + sigma < 1e-15:
        return np.float64(0.0)
    B = (sigma - mu) / (sigma + mu)
    return np.float64(B)


OPERATIONS["symbol_burstiness"] = {
    "fn": symbol_burstiness,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Goh-Barabasi burstiness parameter for most common symbol"
}


def conditional_entropy_chain(x):
    """Compute conditional entropy chain: H(X_1), H(X_2|X_1), H(X_3|X_1,X_2), ...
    Input: array of symbol indices. Output: array of conditional entropies up to order 4.
    Decreasing conditional entropy indicates learnable structure."""
    from collections import Counter
    symbols = np.round(x).astype(int)
    n = len(symbols)
    max_order = min(4, n - 1)
    cond_entropies = []
    for order in range(max_order):
        if order == 0:
            counts = Counter(symbols)
            probs = np.array(list(counts.values())) / n
            H = -np.sum(probs * np.log2(probs + 1e-15))
            cond_entropies.append(H)
        else:
            # H(X_{k+1} | X_1, ..., X_k) = H(k+1-gram) - H(k-gram)
            ngram_counts = Counter()
            prev_counts = Counter()
            for i in range(n - order):
                ngram = tuple(symbols[i:i + order + 1])
                ngram_counts[ngram] += 1
                prev = tuple(symbols[i:i + order])
                prev_counts[prev] += 1
            total = sum(ngram_counts.values())
            H_joint = -sum((c / total) * np.log2(c / total + 1e-15) for c in ngram_counts.values())
            total_prev = sum(prev_counts.values())
            H_prev = -sum((c / total_prev) * np.log2(c / total_prev + 1e-15) for c in prev_counts.values())
            cond_entropies.append(H_joint - H_prev)
    return np.array(cond_entropies)


OPERATIONS["conditional_entropy_chain"] = {
    "fn": conditional_entropy_chain,
    "input_type": "array",
    "output_type": "array",
    "description": "Conditional entropy chain H(X_1), H(X_2|X_1), H(X_3|X_1,X_2), ..."
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
