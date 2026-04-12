"""
M32: EC↔OEIS silence characterization
========================================
For elliptic curves in DuckDB, compute the a_p sequence (first 20 terms).
Which OEIS sequences are NEVER matched? Which are disproportionately matched?
The "silence" pattern reveals what arithmetic structures ECs cannot represent.
"""
import json, time
import numpy as np
import duckdb
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OEIS_PATH = V2.parents[3] / "cartography" / "oeis" / "data" / "stripped_new.txt"
OEIS_NAMES_PATH = V2.parents[3] / "cartography" / "oeis" / "data" / "oeis_names.json"
OUT = V2 / "m32_ec_oeis_silence_results.json"

def sieve(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit+1, i): is_p[j] = False
    return [i for i in range(2, limit+1) if is_p[i]]

def main():
    t0 = time.time()
    print("=== M32: EC↔OEIS silence characterization ===\n")

    # Load EC a_p sequences from DuckDB (use first 1000 ECs)
    print("[1] Loading EC data from DuckDB...")
    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level LIMIT 2000
    """).fetchall()
    con.close()
    print(f"  {len(rows)} forms (weight-2 newforms ↔ ECs by modularity)")

    ap_primes = sieve(50)
    # Build 5-gram fingerprints from a_p sequences
    ec_fingerprints = set()
    ec_5grams = []
    for label, level, ap_json in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_vals = [x[0] if isinstance(x, list) else x for x in ap[:10]]
        if len(ap_vals) >= 5:
            gram = tuple(ap_vals[:5])
            ec_fingerprints.add(gram)
            ec_5grams.append({"label": label, "gram": gram})
    print(f"  Unique EC 5-grams: {len(ec_fingerprints)}")

    # Load OEIS
    print("\n[2] Loading OEIS sequences...")
    oeis = {}
    with open(OEIS_PATH, 'r', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith('A'): continue
            parts = line.split(',')
            sid = parts[0].strip().split()[0]
            terms = []
            for t in parts[1:]:
                t = t.strip()
                if t:
                    try: terms.append(int(t))
                    except: pass
            if len(terms) >= 5:
                oeis[sid] = terms
    print(f"  {len(oeis)} OEIS sequences with ≥5 terms")

    try:
        with open(OEIS_NAMES_PATH) as f:
            names = json.load(f)
    except: names = {}

    # Build OEIS 5-gram index
    print("\n[3] Building OEIS 5-gram index...")
    oeis_gram_to_seq = defaultdict(set)
    for sid, terms in oeis.items():
        for j in range(min(len(terms) - 4, 30)):
            gram = tuple(terms[j:j+5])
            oeis_gram_to_seq[gram].add(sid)
    print(f"  {len(oeis_gram_to_seq)} unique 5-grams in OEIS")

    # Match EC fingerprints to OEIS
    print("\n[4] Matching EC fingerprints to OEIS...")
    matched_seqs = Counter()
    matched_ecs = 0
    for ecg in ec_5grams:
        gram = ecg["gram"]
        if gram in oeis_gram_to_seq:
            matched_ecs += 1
            for sid in oeis_gram_to_seq[gram]:
                matched_seqs[sid] += 1

    match_rate = matched_ecs / len(ec_5grams) if ec_5grams else 0
    print(f"  ECs matched to ≥1 OEIS sequence: {matched_ecs}/{len(ec_5grams)} ({match_rate:.1%})")
    print(f"  Unique OEIS sequences matched: {len(matched_seqs)}")

    # Top matched sequences
    print("\n  Top matched OEIS sequences:")
    for sid, cnt in matched_seqs.most_common(15):
        print(f"    {sid} ({cnt}x): {names.get(sid, '')[:60]}")

    # Silence: OEIS sequences with terms in EC range but NO EC match
    # What integer ranges do ECs produce?
    all_ec_vals = set()
    for ecg in ec_5grams:
        all_ec_vals.update(ecg["gram"])
    ec_range = (min(all_ec_vals), max(all_ec_vals))
    print(f"\n  EC a_p value range: [{ec_range[0]}, {ec_range[1]}]")

    # Count OEIS seqs whose first 5 terms are ALL in EC range but don't match any EC
    n_in_range = 0; n_silent = 0
    silent_examples = []
    for sid, terms in oeis.items():
        first5 = terms[:5]
        if all(ec_range[0] <= t <= ec_range[1] for t in first5):
            n_in_range += 1
            if sid not in matched_seqs:
                n_silent += 1
                if len(silent_examples) < 20:
                    silent_examples.append({"oeis_id": sid, "terms": first5,
                                           "name": names.get(sid, "")[:60]})

    silence_rate = n_silent / n_in_range if n_in_range > 0 else 0
    print(f"\n  OEIS seqs with terms in EC range: {n_in_range}")
    print(f"  Of those, SILENT (no EC match): {n_silent} ({silence_rate:.1%})")

    elapsed = time.time() - t0
    output = {
        "probe": "M32", "title": "EC↔OEIS silence characterization",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_ecs": len(ec_5grams),
        "n_unique_ec_fingerprints": len(ec_fingerprints),
        "n_oeis_sequences": len(oeis),
        "match_rate": round(match_rate, 4),
        "n_oeis_matched": len(matched_seqs),
        "top_matches": [{"oeis_id": sid, "count": cnt, "name": names.get(sid, "")[:60]}
                       for sid, cnt in matched_seqs.most_common(20)],
        "silence": {
            "n_in_range": n_in_range,
            "n_silent": n_silent,
            "silence_rate": round(silence_rate, 4),
            "examples": silent_examples,
        },
        "ec_value_range": list(ec_range),
        "assessment": None,
    }

    if silence_rate > 0.95:
        output["assessment"] = f"EXTREME SILENCE: {silence_rate:.0%} of range-compatible OEIS seqs have NO EC match — EC sequences are highly specific"
    elif silence_rate > 0.7:
        output["assessment"] = f"HIGH SILENCE: {silence_rate:.0%} — most OEIS sequences in EC range are NOT realizable as a_p"
    else:
        output["assessment"] = f"LOW SILENCE: {silence_rate:.0%} — EC sequences overlap broadly with OEIS"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
