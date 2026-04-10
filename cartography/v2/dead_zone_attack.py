"""
Dead Zone Attack: 20 transforms on EC a_p sequences vs OEIS
============================================================
The EC-OEIS gap is ~83% after the pi wormhole (round(a_p/pi) bridges 12.1%).
Systematically test 20 transforms to find new constant wormholes.

Method:
- mod-p fingerprint = tuple of (val mod p) for first 5 terms, at p=3 and p=5
- For each transform, count how many (EC, OEIS) pairs share a fingerprint
- Null model: random pairing null. For each trial, randomly permute EC curve
  indices and re-count matches. This preserves marginal distributions of both
  EC and OEIS fingerprints while breaking any genuine correspondence.
- Also compare every transform against the IDENTITY (raw a_p) as baseline.
"""

import sys, json, math, random
import numpy as np
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(line_buffering=True)

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "charon" / "data" / "charon.duckdb"
OEIS_PATH = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
OUT_PATH = Path(__file__).resolve().parent / "dead_zone_attack_results.json"

random.seed(42)
np.random.seed(42)

PRIMES_25 = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]

PI = math.pi
E_CONST = math.e
SQRT2 = math.sqrt(2)
PHI = (1 + math.sqrt(5)) / 2
LN2 = math.log(2)
FIB_INDICES = [0, 1, 1, 2, 3, 5, 8, 13, 21]


def load_ec_data(n=500):
    import duckdb
    con = duckdb.connect(str(DB_PATH), read_only=True)
    all_rows = con.execute("""
        SELECT lmfdb_label, conductor, aplist, bad_primes
        FROM elliptic_curves
        WHERE aplist IS NOT NULL AND list_count(aplist) >= 10
        ORDER BY conductor
    """).fetchall()
    con.close()
    indices = np.linspace(0, len(all_rows)-1, n, dtype=int)
    return [all_rows[i] for i in indices]


def load_oeis_data(n=500):
    seqs = {}
    with open(OEIS_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split(' ', 1)
            if len(parts) < 2:
                continue
            aid = parts[0]
            terms_str = parts[1].strip().strip(',')
            if not terms_str:
                continue
            try:
                terms = [int(x) for x in terms_str.split(',') if x.strip()]
            except ValueError:
                continue
            if len(terms) >= 10:
                seqs[aid] = terms
            if len(seqs) >= n * 5:
                break
    keys = list(seqs.keys())
    random.shuffle(keys)
    selected = {}
    for k in keys:
        if max(abs(v) for v in seqs[k][:20]) > 1:
            selected[k] = seqs[k]
        if len(selected) >= n:
            break
    for k in keys:
        if k not in selected:
            selected[k] = seqs[k]
        if len(selected) >= n:
            break
    return dict(list(selected.items())[:n])


def fp_mod(seq, p, width=5):
    terms = seq[:width]
    if len(terms) < width:
        return None
    return tuple(t % p for t in terms)


def safe_round(x):
    if not math.isfinite(x):
        return 0
    return int(round(x))


def _sign(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)


def _smallest_prime_factor(n):
    if n <= 1: return 2
    if n % 2 == 0: return 2
    i = 3
    while i * i <= n:
        if n % i == 0: return i
        i += 2
    return n


def apply_transforms(ap, conductor, bad_primes):
    N = conductor
    primes = PRIMES_25[:len(ap)]
    R = {}

    # Identity (baseline)
    R['T00_identity'] = list(ap)

    # Constant divisions
    R['T01_div_pi']    = [safe_round(a / PI) for a in ap]
    R['T02_div_e']     = [safe_round(a / E_CONST) for a in ap]
    R['T03_div_sqrt2'] = [safe_round(a / SQRT2) for a in ap]
    R['T04_div_phi']   = [safe_round(a / PHI) for a in ap]
    R['T05_div_ln2']   = [safe_round(a / LN2) for a in ap]

    # Arithmetic
    R['T06_mod_cond'] = [a % N if N > 1 else a for a in ap]
    R['T07_div_sqrtp'] = [int(math.floor(a / math.sqrt(p))) for a, p in zip(ap, primes)]
    R['T08_sign_flip'] = [a * ((-1)**p) for a, p in zip(ap, primes)]

    # Accumulations
    cs = []
    s = 0
    for a in ap:
        s += a; cs.append(s)
    R['T09_cumsum'] = cs

    cp = []
    prod = 1
    for a in ap:
        prod = (prod * a) % 1000 if a != 0 else 0; cp.append(prod)
    R['T10_cumprod1k'] = cp

    # Bitwise / scaling
    R['T11_xor_p'] = [a ^ p for a, p in zip(ap, primes)]
    R['T12_scaled'] = [safe_round(a * p / N) if N > 0 else a for a, p in zip(ap, primes)]

    # Structural
    fib_seq = [ap[fi] for fi in FIB_INDICES if fi < len(ap)]
    R['T13_fib_idx'] = fib_seq if len(fib_seq) >= 5 else ap[:5]

    gaps = [primes[i+1] - primes[i] for i in range(len(primes)-1)]
    R['T14_gap_wt'] = [a * g for a, g in zip(ap, gaps)]

    if len(ap) >= 3:
        d1 = [ap[i+1] - ap[i] for i in range(len(ap)-1)]
        R['T15_diff2'] = [d1[i+1] - d1[i] for i in range(len(d1)-1)]
    else:
        R['T15_diff2'] = ap

    ratios = [0]
    for i in range(1, len(ap)):
        ratios.append(safe_round(100 * ap[i] / ap[i-1]) if ap[i-1] != 0 else 0)
    R['T16_ratio'] = ratios

    if len(ap) >= 3:
        R['T17_mavg3'] = [safe_round((ap[i]+ap[i+1]+ap[i+2])/3) for i in range(len(ap)-2)]
    else:
        R['T17_mavg3'] = ap

    spf = _smallest_prime_factor(N)
    R['T18_mod_spf'] = [a % spf if spf > 1 else a % 2 for a in ap]

    R['T19_abs'] = [abs(a) for a in ap]
    R['T20_sign'] = [_sign(a) for a in ap]

    return R


def main():
    print("Loading data...")
    ec_data = load_ec_data(500)
    oeis_data = load_oeis_data(500)
    print(f"  EC: {len(ec_data)}, OEIS: {len(oeis_data)}")

    # OEIS fingerprints
    oeis_fp3_index = defaultdict(set)  # fp -> set of aids
    oeis_fp5_index = defaultdict(set)
    for aid, terms in oeis_data.items():
        f3 = fp_mod(terms, 3, 5)
        f5 = fp_mod(terms, 5, 5)
        if f3: oeis_fp3_index[f3].add(aid)
        if f5: oeis_fp5_index[f5].add(aid)
    print(f"  OEIS mod-3 distinct fps: {len(oeis_fp3_index)}/243")
    print(f"  OEIS mod-5 distinct fps: {len(oeis_fp5_index)}/3125")

    # Precompute all EC fingerprints per transform
    label0, cond0, ap0, bp0 = ec_data[0]
    tnames = list(apply_transforms(list(ap0), cond0, bp0 or []).keys())

    print(f"\nComputing {len(tnames)} transforms x {len(ec_data)} curves...")

    # ec_fp3[tname][i], ec_fp5[tname][i] = fingerprint for i-th EC curve under transform tname
    ec_fp3 = {t: [] for t in tnames}
    ec_fp5 = {t: [] for t in tnames}

    for idx, (label, cond, aplist, bp) in enumerate(ec_data):
        transforms = apply_transforms(list(aplist), cond, bp or [])
        for t in tnames:
            ec_fp3[t].append(fp_mod(transforms[t], 3, 5))
            ec_fp5[t].append(fp_mod(transforms[t], 5, 5))
        if (idx+1) % 200 == 0:
            print(f"  {idx+1}/{len(ec_data)}")

    # Count matches: for each transform, how many EC curves have fp in OEIS fp set
    def count_matches_3(fps):
        return sum(1 for fp in fps if fp is not None and fp in oeis_fp3_index)

    def count_matches_5(fps):
        return sum(1 for fp in fps if fp is not None and fp in oeis_fp5_index)

    def unique_oeis_3(fps):
        s = set()
        for fp in fps:
            if fp is not None and fp in oeis_fp3_index:
                s.update(oeis_fp3_index[fp])
        return s

    def unique_oeis_5(fps):
        s = set()
        for fp in fps:
            if fp is not None and fp in oeis_fp5_index:
                s.update(oeis_fp5_index[fp])
        return s

    print("\nCounting observed matches...")
    obs = {}
    for t in tnames:
        m3 = count_matches_3(ec_fp3[t])
        m5 = count_matches_5(ec_fp5[t])
        u3 = unique_oeis_3(ec_fp3[t])
        u5 = unique_oeis_5(ec_fp5[t])
        obs[t] = {'m3': m3, 'm5': m5, 'u3': len(u3), 'u5': len(u5),
                   'u_combined': len(u3 | u5)}

    # ── Null model: cross-transform shuffle ──
    # For each null trial: for each EC curve, pick a random transform (from
    # the 21 including identity) to get its fingerprint. This preserves the
    # marginal distribution of EC fingerprints across transforms.
    # Then count matches against the REAL OEIS fingerprint set.
    # A transform beats this null only if it produces MORE matches than
    # a typical random transform does.

    print("\nNull model: cross-transform shuffle (1000 trials)...")
    n_ec = len(ec_data)
    null_m3 = {t: [] for t in tnames}
    null_m5 = {t: [] for t in tnames}

    # Precompute: pool all (transform, curve_idx) fps
    # For each null trial, for each curve, randomly pick a transform
    for trial in range(1000):
        for t in tnames:
            # Null: shuffle EC curve indices (permute which curve gets which fp)
            perm = list(range(n_ec))
            random.shuffle(perm)
            c3 = sum(1 for i in perm if ec_fp3[t][i] is not None and ec_fp3[t][i] in oeis_fp3_index)
            c5 = sum(1 for i in perm if ec_fp5[t][i] is not None and ec_fp5[t][i] in oeis_fp5_index)
            null_m3[t].append(c3)
            null_m5[t].append(c5)

        if (trial+1) % 200 == 0:
            print(f"  Trial {trial+1}/1000")

    # Wait -- shuffling indices doesn't change the count since we sum over all.
    # We need a DIFFERENT null. The real question: is transform T better than
    # a random transform at producing OEIS matches?
    # Better null: for each transform T, null = average match count across
    # all OTHER transforms. This directly answers "is T special?"

    print("\nComputing cross-transform null (leave-one-out)...")
    all_m3 = [obs[t]['m3'] for t in tnames]
    all_m5 = [obs[t]['m5'] for t in tnames]
    total_m3 = sum(all_m3)
    total_m5 = sum(all_m5)
    n_t = len(tnames)

    results = {}
    for t in tnames:
        # Leave-one-out: null mean = mean of all OTHER transforms
        loo_m3 = (total_m3 - obs[t]['m3']) / (n_t - 1)
        loo_m5 = (total_m5 - obs[t]['m5']) / (n_t - 1)
        # Std from the cross-transform distribution
        std_m3 = float(np.std(all_m3))
        std_m5 = float(np.std(all_m5))

        z3 = (obs[t]['m3'] - loo_m3) / std_m3 if std_m3 > 0 else 0
        z5 = (obs[t]['m5'] - loo_m5) / std_m5 if std_m5 > 0 else 0

        results[t] = {
            'mod3_ec_matches': obs[t]['m3'],
            'mod5_ec_matches': obs[t]['m5'],
            'mod3_oeis_unique': obs[t]['u3'],
            'mod5_oeis_unique': obs[t]['u5'],
            'combined_oeis_unique': obs[t]['u_combined'],
            'cross_transform_null_m3': round(loo_m3, 1),
            'cross_transform_null_m5': round(loo_m5, 1),
            'cross_transform_std_m3': round(std_m3, 1),
            'cross_transform_std_m5': round(std_m5, 1),
            'z3_vs_transforms': round(z3, 2),
            'z5_vs_transforms': round(z5, 2),
            'z_max': round(max(z3, z5), 2),
            'above_identity_m3': obs[t]['m3'] - obs['T00_identity']['m3'],
            'above_identity_m5': obs[t]['m5'] - obs['T00_identity']['m5'],
        }

    # Also compute a proper random-pairing null for the IDENTITY transform
    # to establish the absolute baseline
    print("\nRandom-pairing null for absolute baseline (1000 trials)...")
    # Null: randomly generate 500 sequences of 5 integers in the EC a_p range
    # and fingerprint them against OEIS
    ap_min = min(min(list(row[2])) for row in ec_data)
    ap_max = max(max(list(row[2])) for row in ec_data)

    abs_null_m3 = []
    abs_null_m5 = []
    for trial in range(1000):
        # Generate 500 random 5-term sequences in the EC a_p value range
        rand_seqs = [tuple(random.randint(ap_min, ap_max) for _ in range(5)) for _ in range(500)]
        c3 = sum(1 for s in rand_seqs if fp_mod(s, 3, 5) in oeis_fp3_index)
        c5 = sum(1 for s in rand_seqs if fp_mod(s, 5, 5) in oeis_fp5_index)
        abs_null_m3.append(c3)
        abs_null_m5.append(c5)

    abs_null_m3 = np.array(abs_null_m3, dtype=float)
    abs_null_m5 = np.array(abs_null_m5, dtype=float)

    # Add absolute z-scores
    for t in tnames:
        az3 = (obs[t]['m3'] - abs_null_m3.mean()) / abs_null_m3.std() if abs_null_m3.std() > 0 else 0
        az5 = (obs[t]['m5'] - abs_null_m5.mean()) / abs_null_m5.std() if abs_null_m5.std() > 0 else 0
        results[t]['abs_null_m3_mean'] = round(float(abs_null_m3.mean()), 1)
        results[t]['abs_null_m3_std'] = round(float(abs_null_m3.std()), 1)
        results[t]['abs_null_m5_mean'] = round(float(abs_null_m5.mean()), 1)
        results[t]['abs_null_m5_std'] = round(float(abs_null_m5.std()), 1)
        results[t]['abs_z3'] = round(float(az3), 2)
        results[t]['abs_z5'] = round(float(az5), 2)
        results[t]['abs_z_max'] = round(float(max(az3, az5)), 2)
        results[t]['genuine_vs_random'] = bool(max(az3, az5) > 3.0)
        results[t]['genuine_vs_transforms'] = bool(results[t]['z_max'] > 2.0)

    # Collect examples for genuine transforms
    print("\nCollecting match examples...")
    for t in tnames:
        examples = []
        for idx, (label, cond, aplist, bp) in enumerate(ec_data):
            fp3 = ec_fp3[t][idx]
            if fp3 is not None and fp3 in oeis_fp3_index:
                for aid in list(oeis_fp3_index[fp3])[:1]:
                    examples.append({'ec': label, 'oeis': aid, 'mod': 3,
                                     'fp': [int(x) for x in fp3], 'conductor': int(cond)})
            if len(examples) >= 10:
                break
        results[t]['examples'] = examples

    # Sort by abs_z_max (genuine signal vs random)
    sorted_names = sorted(tnames, key=lambda t: -results[t]['abs_z_max'])

    # Print report
    print("\n" + "="*90)
    print("DEAD ZONE ATTACK: 20 TRANSFORMS + IDENTITY BASELINE")
    print("="*90)
    print(f"{'Transform':20s}  {'m3':>4s} {'m5':>4s} | {'abs_z3':>7s} {'abs_z5':>7s} | "
          f"{'vs_xform_z3':>10s} {'vs_xform_z5':>10s} | {'OEIS':>4s} | flags")
    print("-"*90)

    for t in sorted_names:
        r = results[t]
        flags = []
        if r['genuine_vs_random']:
            flags.append('ABOVE_RANDOM')
        if r['genuine_vs_transforms']:
            flags.append('ABOVE_PEERS')
        flag_str = ' '.join(flags)
        print(f"  {t:20s}  {r['mod3_ec_matches']:4d} {r['mod5_ec_matches']:4d} | "
              f"{r['abs_z3']:+7.1f} {r['abs_z5']:+7.1f} | "
              f"{r['z3_vs_transforms']:+10.2f} {r['z5_vs_transforms']:+10.2f} | "
              f"{r['combined_oeis_unique']:4d} | {flag_str}")

    # Summary
    genuine_random = [t for t in sorted_names if results[t]['genuine_vs_random']]
    genuine_peers = [t for t in sorted_names if results[t]['genuine_vs_transforms']]
    print(f"\n  Above random null (z>3): {len(genuine_random)}/{len(tnames)}")
    print(f"  Above peer transforms (z>2): {len(genuine_peers)}/{len(tnames)}")
    print(f"  Absolute null: m3={float(abs_null_m3.mean()):.1f}+/-{float(abs_null_m3.std()):.1f}, "
          f"m5={float(abs_null_m5.mean()):.1f}+/-{float(abs_null_m5.std()):.1f}")

    # Identity baseline
    id_r = results['T00_identity']
    print(f"\n  IDENTITY baseline: m3={id_r['mod3_ec_matches']}, m5={id_r['mod5_ec_matches']}, "
          f"OEIS={id_r['combined_oeis_unique']}")

    # New wormholes
    new_wormholes = [t for t in sorted_names
                     if results[t]['genuine_vs_transforms']
                     and t not in ('T00_identity', 'T01_div_pi')]
    if new_wormholes:
        print(f"\n  CANDIDATE WORMHOLES (above peers, not identity/pi):")
        for t in new_wormholes:
            r = results[t]
            gain3 = r['above_identity_m3']
            gain5 = r['above_identity_m5']
            print(f"    {t}: m3={r['mod3_ec_matches']} ({gain3:+d} vs identity), "
                  f"m5={r['mod5_ec_matches']} ({gain5:+d} vs identity), "
                  f"oeis_coverage={r['combined_oeis_unique']}")

    # Coverage
    all_covered_oeis = set()
    for t in sorted_names:
        if results[t]['genuine_vs_random']:
            for idx in range(len(ec_data)):
                fp3 = ec_fp3[t][idx]
                fp5 = ec_fp5[t][idx]
                if fp3 is not None and fp3 in oeis_fp3_index:
                    all_covered_oeis.update(oeis_fp3_index[fp3])
                if fp5 is not None and fp5 in oeis_fp5_index:
                    all_covered_oeis.update(oeis_fp5_index[fp5])

    pct = 100 * len(all_covered_oeis) / len(oeis_data) if oeis_data else 0
    print(f"\n  Combined OEIS coverage (all genuine transforms): "
          f"{len(all_covered_oeis)}/{len(oeis_data)} = {pct:.1f}%")

    # Save
    sorted_results = {t: results[t] for t in sorted_names}
    output = {
        'metadata': {
            'n_ec': len(ec_data),
            'n_oeis': len(oeis_data),
            'n_oeis_fp3_distinct': len(oeis_fp3_index),
            'n_oeis_fp5_distinct': len(oeis_fp5_index),
            'fp_width': 5,
            'null_method': 'Two nulls: (1) random 5-term seqs in EC range vs OEIS fps, (2) leave-one-out cross-transform',
            'random_null_trials': 1000,
            'ap_range': [int(ap_min), int(ap_max)],
        },
        'transforms': sorted_results,
        'summary': {
            'genuine_vs_random': len(genuine_random),
            'genuine_vs_peers': len(genuine_peers),
            'total_transforms': len(tnames),
            'identity_m3': id_r['mod3_ec_matches'],
            'identity_m5': id_r['mod5_ec_matches'],
            'identity_oeis': id_r['combined_oeis_unique'],
            'combined_oeis_coverage': len(all_covered_oeis),
            'combined_oeis_pct': round(pct, 2),
            'new_wormholes': new_wormholes,
        }
    }

    with open(OUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nSaved to {OUT_PATH}")


if __name__ == '__main__':
    main()
