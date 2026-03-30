"""
Systematic Novel Bridge Search — Noesis v2
=============================================

For every hub pair that shares an IDENTICAL depth-3 chain support signature
but lives in DIFFERENT domains: assess whether the connection is known,
novel, or trivial.

This extends the Goodhart<->No-Cloning finding to a full census.

Author: Aletheia
Date: 2026-03-29
"""

import duckdb
import numpy as np
import json
import sys
import io
from collections import defaultdict
from pathlib import Path
from itertools import combinations

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = Path(__file__).parent / "noesis_v2.duckdb"
OUT_PATH = Path(__file__).parent / "systematic_novel_bridges.json"

# ─── The 10 depth-3 chains ──────────────────────────────────────────────────

CHAINS = [
    {"id": "C3_01", "name": "Variational quantization",
     "sequence": ("EXTEND", "CONCENTRATE", "DISTRIBUTE")},
    {"id": "C3_02", "name": "Digital signal processing",
     "sequence": ("TRUNCATE", "QUANTIZE", "DISTRIBUTE")},
    {"id": "C3_03", "name": "Adaptive localization",
     "sequence": ("PARTITION", "TRUNCATE", "CONCENTRATE")},
    {"id": "C3_04", "name": "Monte Carlo inversion",
     "sequence": ("RANDOMIZE", "TRUNCATE", "INVERT")},
    {"id": "C3_05", "name": "Gauge -> SSB",
     "sequence": ("EXTEND", "PARTITION", "INVERT")},
    {"id": "C3_06", "name": "Multi-resolution discretization",
     "sequence": ("HIERARCHIZE", "PARTITION", "QUANTIZE")},
    {"id": "C3_07", "name": "Redistribute then reverse",
     "sequence": ("DISTRIBUTE", "CONCENTRATE", "INVERT")},
    {"id": "C3_08", "name": "Stochastic meta-truncation",
     "sequence": ("RANDOMIZE", "HIERARCHIZE", "TRUNCATE")},
    {"id": "C3_09", "name": "Inverse variational",
     "sequence": ("EXTEND", "INVERT", "CONCENTRATE")},
    {"id": "C3_10", "name": "Discrete averaging hierarchy",
     "sequence": ("QUANTIZE", "DISTRIBUTE", "HIERARCHIZE")},
]

CANONICAL_OPS = {
    "DISTRIBUTE", "CONCENTRATE", "TRUNCATE", "EXTEND",
    "RANDOMIZE", "HIERARCHIZE", "PARTITION", "QUANTIZE", "INVERT"
}

# ─── Domain inference ────────────────────────────────────────────────────────

DOMAIN_RULES = [
    # (keywords, domain_name)
    (['topology', 'manifold', 'embedding', 'euler', 'hairy', 'brouwer', 'borsuk',
      'banach_tarski', 'poincare'], 'topology'),
    (['quantum', 'cloning', 'bell', 'holevo', 'entangle', 'no_cloning',
      'decoherence', 'margolus_levitin', 'qkd', 'key_distribution'], 'quantum_physics'),
    (['arrow', 'gibbard', 'social', 'voting', 'mechanism', 'myerson', 'nash',
      'vcg', 'revelation', 'envy_free', 'dictatorship', 'folk_theorem',
      'bilateral_trade', 'chatterjee', 'revenue_equivalence',
      'budget_balance', 'satterthwaite'], 'social_choice_mechanism_design'),
    (['shannon', 'nyquist', 'bode', 'control', 'kalman', 'sensitivity_waterbed',
      'integral'], 'signal_control'),
    (['carnot', 'thermody', 'landauer'], 'thermodynamics'),
    (['heisenberg', 'uncertainty'], 'quantum_measurement'),
    (['gibbs', 'fourier', 'runge', 'approximat', 'gibbs_phenomenon'], 'analysis_approximation'),
    (['calendar', 'pythagorean_comma', 'tuning', 'comma', 'temperament'], 'incommensurability'),
    (['goodhart'], 'optimization_epistemology'),
    (['crystal', 'crystallographic'], 'crystallography_geometry'),
    (['map_projection', 'egregium'], 'differential_geometry'),
    (['godel', 'halting', 'rice', 'incomplet'], 'logic_computation'),
    (['cap', 'distributed_system'], 'distributed_systems'),
    (['mundell', 'fleming', 'trinity', 'macroeconom', 'impossible_trinity'], 'economics'),
    (['fitts', 'hick', 'speed_accuracy'], 'cognitive_science'),
    (['quintic', 'insolvab', 'galois'], 'algebra'),
    (['free_lunch', 'no_free'], 'machine_learning'),
    (['sqrt', 'rational', 'irrational'], 'number_theory'),
    (['symmetry_break', 'forced_symmetry'], 'symmetry_breaking'),
    (['bells_theorem'], 'quantum_foundations'),
]

def infer_domain(hub_id):
    h = hub_id.lower()
    for keywords, domain in DOMAIN_RULES:
        if any(w in h for w in keywords):
            return domain
    return 'other'

# ─── Domain distance (for ranking interestingness) ───────────────────────────

DOMAIN_CLUSTERS = {
    'quantum_physics': 'physics',
    'quantum_measurement': 'physics',
    'quantum_foundations': 'physics',
    'thermodynamics': 'physics',
    'signal_control': 'engineering',
    'distributed_systems': 'engineering',
    'social_choice_mechanism_design': 'economics_social',
    'economics': 'economics_social',
    'optimization_epistemology': 'epistemology',
    'machine_learning': 'computer_science',
    'logic_computation': 'computer_science',
    'topology': 'mathematics',
    'analysis_approximation': 'mathematics',
    'differential_geometry': 'mathematics',
    'crystallography_geometry': 'mathematics',
    'algebra': 'mathematics',
    'number_theory': 'mathematics',
    'incommensurability': 'measurement',
    'cognitive_science': 'psychology',
    'symmetry_breaking': 'physics',
}

def domain_distance(d1, d2):
    """Higher = more distant domains. Max distance for different super-clusters."""
    if d1 == d2:
        return 0
    c1 = DOMAIN_CLUSTERS.get(d1, d1)
    c2 = DOMAIN_CLUSTERS.get(d2, d2)
    if c1 == c2:
        return 1  # same super-cluster
    return 2      # different super-clusters


# ─── Known connection registry ───────────────────────────────────────────────

KNOWN_CONNECTIONS = [
    # (hub_keyword_a, hub_keyword_b, reference, explanation)
    ('heisenberg', 'bode', 'Seron et al.; Freudenberg-Looze fundamental limitations',
     'Uncertainty-sensitivity duality is well-established in control theory'),
    ('heisenberg', 'gibbs', 'Signal processing: time-frequency uncertainty as dual of Gibbs overshoot',
     'Both are Fourier uncertainty consequences'),
    ('bode', 'gibbs', 'Hilbert transform / Kramers-Kronig relations',
     'Sensitivity integrals and Fourier convergence share analytic structure'),
    ('arrow', 'free_lunch', 'Computational social choice (Conitzer, Procaccia)',
     'Impossibility theorems in aggregation are well-connected to NFL'),
    ('arrow', 'gibbard', 'Gibbard-Satterthwaite is direct consequence of Arrow',
     'Same field, same theorem family'),
    ('myerson', 'vcg', 'Mechanism design textbooks (Nisan et al.)',
     'Both are mechanism design impossibilities'),
    ('myerson', 'bilateral_trade', 'Myerson-Satterthwaite is bilateral trade theorem',
     'Same theorem'),
    ('myerson', 'revelation', 'Revelation principle is foundation of Myerson-Satterthwaite',
     'Same field, tight connection'),
    ('goodhart', 'campbell', 'Goodhart/Campbell/Lucas critique are the same family',
     'Well-known in economics/policy'),
    ('mundell', 'trinity', 'Mundell-Fleming IS the impossible trinity',
     'Same theorem'),
    ('carnot', 'landauer', 'Bennett 1982; Landauer principle derives from 2nd law',
     'Well-established physics connection'),
    ('godel', 'halting', 'Turing 1936 / Gödel 1931 cross-reduction',
     'Foundational equivalence in logic'),
    ('bell', 'cloning', 'Quantum information textbooks (Nielsen & Chuang)',
     'Both are quantum no-go theorems, well-connected'),
    ('cap', 'distributed', 'Gilbert & Lynch 2002; Brewer 2000',
     'CAP is a distributed systems theorem'),
    ('crystallographic', 'symmetry_break', 'Standard crystallography; Landau theory',
     'Crystallographic restriction IS about symmetry breaking'),
    ('social_choice', 'arrow', 'Arrow IS social choice impossibility',
     'Identical'),
    ('borsuk', 'brouwer', 'Both are algebraic topology fixed-point theorems',
     'Same field, standard connection'),
    ('envy_free', 'arrow', 'Fair division and social choice (Moulin, Procaccia)',
     'Connected in mechanism design literature'),
    ('folk_theorem', 'nash', 'Game theory fundamentals',
     'Folk theorem relies on Nash equilibrium concept'),
    ('revenue_equivalence', 'myerson', 'Myerson 1981 optimal auction paper',
     'Same paper'),
]


def check_known(ha, hb):
    """Check if a pair is known to be connected in literature."""
    ha_l = ha.lower()
    hb_l = hb.lower()
    for kw_a, kw_b, ref, explanation in KNOWN_CONNECTIONS:
        if (kw_a in ha_l and kw_b in hb_l) or (kw_b in ha_l and kw_a in hb_l):
            return True, ref, explanation
    return False, None, None


# ─── Structural claim generator ──────────────────────────────────────────────

def generate_claim(ha, hb, da, db, shared_chains, chain_names):
    """Generate a human-readable structural claim for a novel bridge."""
    chain_str = ', '.join(chain_names)

    # Extract readable names
    def readable(hub_id):
        return hub_id.replace('IMPOSSIBILITY_', '').replace('_', ' ').title()

    ra = readable(ha)
    rb = readable(hb)

    # Identify shared structural features from chain semantics
    features = []
    for c in CHAINS:
        if c['name'] in chain_names:
            ops = c['sequence']
            if 'RANDOMIZE' in ops:
                features.append('stochastic sampling')
            if 'TRUNCATE' in ops:
                features.append('domain restriction')
            if 'INVERT' in ops:
                features.append('structural reversal')
            if 'HIERARCHIZE' in ops:
                features.append('meta-level elevation')
            if 'PARTITION' in ops:
                features.append('domain decomposition')
            if 'EXTEND' in ops:
                features.append('structural enlargement')
            if 'CONCENTRATE' in ops:
                features.append('extremal focusing')
            if 'DISTRIBUTE' in ops:
                features.append('error spreading')
            if 'QUANTIZE' in ops:
                features.append('grid forcing')

    features = list(dict.fromkeys(features))  # dedupe preserving order
    feature_str = ', '.join(features[:4])

    claim = (f"{ra} and {rb} share [{chain_str}] "
             f"because both involve [{feature_str}]")

    return claim


# ─── Main analysis ───────────────────────────────────────────────────────────

def get_hub_data(con):
    """Extract hubs, their spokes, and the damage operators each spoke carries."""
    rows = con.execute("""
        WITH all_res AS (
            SELECT source_resolution_id AS rid, shared_damage_operator AS op
            FROM cross_domain_edges
            UNION ALL
            SELECT target_resolution_id AS rid, shared_damage_operator AS op
            FROM cross_domain_edges
        ),
        parsed AS (
            SELECT rid, op,
                   CASE WHEN POSITION('__' IN rid) > 0
                        THEN SUBSTRING(rid, 1, POSITION('__' IN rid)-1)
                        ELSE rid END AS hub,
                   CASE WHEN POSITION('__' IN rid) > 0
                        THEN SUBSTRING(rid, POSITION('__' IN rid)+2)
                        ELSE rid END AS spoke
            FROM all_res
        )
        SELECT hub, spoke, rid, op
        FROM parsed
        ORDER BY hub, spoke
    """).fetchall()

    hubs = defaultdict(lambda: {"spokes": defaultdict(set), "all_ops": set()})
    for hub, spoke, rid, op in rows:
        normalized = op.strip()
        hubs[hub]["spokes"][spoke].add(normalized)
        hubs[hub]["all_ops"].add(normalized)

    return dict(hubs)


def check_chain_support(hub_data, chain_seq):
    """Check if a hub supports a three-operator chain."""
    a_op, b_op, c_op = chain_seq
    all_ops = hub_data["all_ops"]

    if not ({a_op, b_op, c_op} <= all_ops):
        return False, 0.0

    spokes_a = {s for s, ops in hub_data["spokes"].items() if a_op in ops}
    spokes_b = {s for s, ops in hub_data["spokes"].items() if b_op in ops}
    spokes_c = {s for s, ops in hub_data["spokes"].items() if c_op in ops}

    if not (spokes_a and spokes_b and spokes_c):
        return False, 0.0

    distinct_spokes = len(spokes_a | spokes_b | spokes_c)
    overlap_penalty = len(spokes_a & spokes_b & spokes_c) / max(1, distinct_spokes)
    n_triples = len(spokes_a) * len(spokes_b) * len(spokes_c)
    total_spokes = len(hub_data["spokes"])
    raw_strength = min(1.0, n_triples / max(1, total_spokes ** 2))
    diversity = distinct_spokes / max(1, total_spokes)
    strength = raw_strength * (1.0 + diversity) / 2.0 * (1.0 - 0.5 * overlap_penalty)

    return True, max(0.01, min(1.0, strength))


def main():
    print("=" * 80)
    print("SYSTEMATIC NOVEL BRIDGE SEARCH — Noesis v2")
    print("=" * 80)

    con = duckdb.connect(str(DB_PATH), read_only=True)

    # ── Step 1: Extract all hub data ──
    print("\n[1] Extracting hub-spoke-operator structure...")
    all_hubs = get_hub_data(con)
    print(f"    Total hubs: {len(all_hubs)}")

    # Filter to hubs with >= 3 canonical ops
    qualified = {}
    for name, data in all_hubs.items():
        canonical = data["all_ops"] & CANONICAL_OPS
        if len(canonical) >= 3:
            qualified[name] = data
    print(f"    Qualified (3+ canonical ops): {len(qualified)}")

    # ── Step 2: Compute depth-3 chain signatures ──
    print("\n[2] Computing depth-3 chain signatures...")
    signatures = {}
    for hub_name, hub_data in qualified.items():
        vec = []
        for chain in CHAINS:
            supported, strength = check_chain_support(hub_data, chain["sequence"])
            vec.append(1 if supported else 0)
        signatures[hub_name] = tuple(vec)

    # Filter to hubs with at least one chain supported
    active = {k: v for k, v in signatures.items() if any(v)}
    print(f"    Active hubs (support >= 1 chain): {len(active)}")

    # ── Step 3: Group by identical signatures ──
    print("\n[3] Grouping by identical depth-3 chain signatures...")
    sig_groups = defaultdict(list)
    for hub_name, sig in active.items():
        sig_groups[sig].append(hub_name)

    # Show signature groups
    multi_groups = {s: m for s, m in sig_groups.items() if len(m) >= 2}
    print(f"    Unique signatures: {len(sig_groups)}")
    print(f"    Signatures with 2+ members: {len(multi_groups)}")

    # ── Step 4: Find ALL cross-domain pairs within same signature ──
    print("\n[4] Enumerating all cross-domain pairs within signature groups...")

    all_pairs = []
    for sig, members in sig_groups.items():
        if len(members) < 2:
            continue

        chain_names = [CHAINS[j]["name"] for j in range(10) if sig[j]]
        n_chains = sum(sig)

        for ha, hb in combinations(sorted(members), 2):
            da = infer_domain(ha)
            db = infer_domain(hb)

            if da == db:
                continue  # same domain, skip

            dist = domain_distance(da, db)
            known, ref, explanation = check_known(ha, hb)

            # Check triviality: if both support ALL 10 chains, it's uninformative
            trivial = (n_chains == 10)

            pair = {
                'hub_a': ha,
                'hub_b': hb,
                'domain_a': da,
                'domain_b': db,
                'signature': list(sig),
                'chain_names': chain_names,
                'n_chains': n_chains,
                'domain_distance': dist,
                'known': known,
                'reference': ref if ref else None,
                'known_explanation': explanation if explanation else None,
                'trivial': trivial,
            }

            if not known and not trivial:
                pair['novelty'] = 'NOVEL'
                pair['claim'] = generate_claim(ha, hb, da, db, sig, chain_names)
            elif known:
                pair['novelty'] = 'KNOWN'
                pair['claim'] = None
            elif trivial:
                pair['novelty'] = 'TRIVIAL'
                pair['claim'] = None
            else:
                pair['novelty'] = 'UNCERTAIN'
                pair['claim'] = generate_claim(ha, hb, da, db, sig, chain_names)

            all_pairs.append(pair)

    # ── Step 5: Also find pairs that share SUBSET signatures ──
    # Beyond exact match: hubs that share the SAME supported chains
    # even if one supports additional chains
    # This catches asymmetric bridges

    print("\n[5] Also scanning for subset-match bridges (A's chains ⊆ B's chains)...")
    subset_pairs = []
    active_list = sorted(active.keys())

    for i in range(len(active_list)):
        for j in range(i + 1, len(active_list)):
            ha, hb = active_list[i], active_list[j]
            sig_a, sig_b = active[ha], active[hb]

            # Already captured exact matches above
            if sig_a == sig_b:
                continue

            da = infer_domain(ha)
            db = infer_domain(hb)
            if da == db:
                continue

            # Find shared chains (intersection)
            shared = tuple(min(a, b) for a, b in zip(sig_a, sig_b))
            n_shared = sum(shared)

            if n_shared < 2:  # need at least 2 shared chains to be interesting
                continue

            # The interesting case: they share 2+ chains but not all
            known, ref, explanation = check_known(ha, hb)
            shared_chain_names = [CHAINS[k]["name"] for k in range(10) if shared[k]]

            dist = domain_distance(da, db)

            pair = {
                'hub_a': ha,
                'hub_b': hb,
                'domain_a': da,
                'domain_b': db,
                'signature_a': list(sig_a),
                'signature_b': list(sig_b),
                'shared_signature': list(shared),
                'chain_names': shared_chain_names,
                'n_shared_chains': n_shared,
                'n_chains_a': sum(sig_a),
                'n_chains_b': sum(sig_b),
                'domain_distance': dist,
                'known': known,
                'reference': ref if ref else None,
                'known_explanation': explanation if explanation else None,
                'match_type': 'subset',
            }

            if not known:
                pair['novelty'] = 'NOVEL'
                pair['claim'] = generate_claim(ha, hb, da, db, shared, shared_chain_names)
            else:
                pair['novelty'] = 'KNOWN'
                pair['claim'] = None

            subset_pairs.append(pair)

    # ── Step 6: Rank and report ──
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    # Exact match pairs
    novel_exact = [p for p in all_pairs if p['novelty'] == 'NOVEL']
    known_exact = [p for p in all_pairs if p['novelty'] == 'KNOWN']
    trivial_exact = [p for p in all_pairs if p['novelty'] == 'TRIVIAL']

    print(f"\n  EXACT SIGNATURE MATCHES (cross-domain):")
    print(f"    Total:   {len(all_pairs)}")
    print(f"    NOVEL:   {len(novel_exact)}")
    print(f"    KNOWN:   {len(known_exact)}")
    print(f"    TRIVIAL: {len(trivial_exact)}")

    # Subset match pairs
    novel_subset = [p for p in subset_pairs if p['novelty'] == 'NOVEL']
    known_subset = [p for p in subset_pairs if p['novelty'] == 'KNOWN']

    print(f"\n  SUBSET MATCHES (2+ shared chains, cross-domain):")
    print(f"    Total:   {len(subset_pairs)}")
    print(f"    NOVEL:   {len(novel_subset)}")
    print(f"    KNOWN:   {len(known_subset)}")

    # ── Rank novel exact matches by interestingness ──
    novel_exact.sort(key=lambda p: (-p['domain_distance'], -p['n_chains']))

    print(f"\n{'=' * 80}")
    print("NOVEL EXACT-SIGNATURE BRIDGES (ranked by domain distance x chain count)")
    print(f"{'=' * 80}\n")

    for i, p in enumerate(novel_exact, 1):
        print(f"  [{i}] {p['hub_a']} <-> {p['hub_b']}")
        print(f"      Domains: {p['domain_a']} <-> {p['domain_b']}  (distance={p['domain_distance']})")
        print(f"      Shared chains ({p['n_chains']}): {', '.join(p['chain_names'])}")
        print(f"      CLAIM: {p['claim']}")
        print()

    # ── Rank novel subset matches ──
    novel_subset.sort(key=lambda p: (-p['domain_distance'], -p['n_shared_chains']))

    print(f"\n{'=' * 80}")
    print(f"TOP NOVEL SUBSET BRIDGES (ranked, top 30)")
    print(f"{'=' * 80}\n")

    for i, p in enumerate(novel_subset[:30], 1):
        print(f"  [{i}] {p['hub_a']} <-> {p['hub_b']}")
        print(f"      Domains: {p['domain_a']} <-> {p['domain_b']}  (distance={p['domain_distance']})")
        print(f"      Shared chains ({p['n_shared_chains']}): {', '.join(p['chain_names'])}")
        extra_a = [CHAINS[k]['name'] for k in range(10) if p['signature_a'][k] and not p['shared_signature'][k]]
        extra_b = [CHAINS[k]['name'] for k in range(10) if p['signature_b'][k] and not p['shared_signature'][k]]
        if extra_a:
            print(f"      Only in A: {', '.join(extra_a)}")
        if extra_b:
            print(f"      Only in B: {', '.join(extra_b)}")
        print(f"      CLAIM: {p['claim']}")
        print()

    # ── Known connections (for completeness) ──
    print(f"\n{'=' * 80}")
    print("KNOWN CONNECTIONS (literature-confirmed)")
    print(f"{'=' * 80}\n")

    for p in known_exact:
        print(f"  {p['hub_a']} <-> {p['hub_b']}")
        print(f"    Reference: {p['reference']}")
        print()

    for p in known_subset[:10]:
        print(f"  {p['hub_a']} <-> {p['hub_b']}  (subset, {p['n_shared_chains']} shared)")
        print(f"    Reference: {p['reference']}")
        print()

    # ── Summary statistics ──
    print(f"\n{'=' * 80}")
    print("CENSUS SUMMARY")
    print(f"{'=' * 80}")

    all_novel = novel_exact + novel_subset

    # Unique hub pairs in novel connections
    novel_hub_pairs = set()
    for p in all_novel:
        pair_key = tuple(sorted([p['hub_a'], p['hub_b']]))
        novel_hub_pairs.add(pair_key)

    # Unique domains involved
    novel_domains = set()
    for p in all_novel:
        novel_domains.add(p['domain_a'])
        novel_domains.add(p['domain_b'])

    # Cross-supercluster bridges
    cross_super = [p for p in all_novel if p['domain_distance'] >= 2]

    print(f"\n  Total novel bridges found:        {len(all_novel)}")
    print(f"  Unique novel hub pairs:           {len(novel_hub_pairs)}")
    print(f"  Domains involved:                 {len(novel_domains)}")
    print(f"  Cross-supercluster (most novel):  {len(cross_super)}")
    print(f"  Known connections confirmed:       {len(known_exact) + len(known_subset)}")

    # Top 5 most interesting novel bridges
    print(f"\n  TOP 5 MOST INTERESTING NOVEL BRIDGES:")
    top5 = sorted(all_novel, key=lambda p: (-p.get('domain_distance', 0), -p.get('n_chains', p.get('n_shared_chains', 0))))[:5]
    for i, p in enumerate(top5, 1):
        nc = p.get('n_chains', p.get('n_shared_chains', 0))
        print(f"    {i}. {p['hub_a']} <-> {p['hub_b']}")
        print(f"       {p['domain_a']} <-> {p['domain_b']} | {nc} shared chains")
        if p.get('claim'):
            print(f"       {p['claim']}")

    # ── Save results ──
    output = {
        'metadata': {
            'analysis': 'systematic_novel_search',
            'date': '2026-03-29',
            'author': 'Aletheia',
            'total_hubs': len(all_hubs),
            'qualified_hubs': len(qualified),
            'active_hubs': len(active),
        },
        'exact_matches': {
            'total': len(all_pairs),
            'novel': len(novel_exact),
            'known': len(known_exact),
            'trivial': len(trivial_exact),
            'pairs': all_pairs,
        },
        'subset_matches': {
            'total': len(subset_pairs),
            'novel': len(novel_subset),
            'known': len(known_subset),
            'pairs': subset_pairs[:100],  # top 100 to keep file manageable
        },
        'census': {
            'total_novel_bridges': len(all_novel),
            'unique_novel_pairs': len(novel_hub_pairs),
            'domains_involved': sorted(novel_domains),
            'cross_supercluster': len(cross_super),
        },
        'top_5': [{
            'hub_a': p['hub_a'],
            'hub_b': p['hub_b'],
            'domain_a': p['domain_a'],
            'domain_b': p['domain_b'],
            'chains': p.get('chain_names', []),
            'claim': p.get('claim'),
            'domain_distance': p.get('domain_distance', 0),
        } for p in top5],
    }

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n  Results saved to: {OUT_PATH}")

    con.close()


if __name__ == "__main__":
    main()
