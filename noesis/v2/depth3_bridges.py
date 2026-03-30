"""
Find cross-domain bridges that depth-3 reveals but depth-1 misses.
Two hubs in DIFFERENT domains but SAME depth-3 cluster = structural kinship
invisible at depth 1.
"""
import duckdb, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# Load depth-3 results
data = json.loads(open('noesis/v2/composition_depth3_results.json', encoding='utf-8').read())

print("=" * 70)
print("DEPTH-3 CROSS-DOMAIN BRIDGES")
print("=" * 70)

# Map hubs to their depth-3 signatures
hub_to_cluster = {}
for cname, cdata in data.get('clusters', {}).items():
    if isinstance(cdata, dict):
        sig = cdata.get('signature', [])
        chains = cdata.get('chains_supported', [])
        members = cdata.get('members', [])
        for m in members:
            hub_to_cluster[m] = {
                'cluster': cname,
                'signature': sig,
                'chains': chains,
            }

# Identify cross-domain pairs within each cluster
print(f"\nHubs in clusters: {len(hub_to_cluster)}")

# Domain inference from hub name
def infer_domain(hub_id):
    h = hub_id.lower()
    if any(w in h for w in ['topology', 'manifold', 'embedding', 'euler', 'hairy', 'brouwer', 'borsuk']):
        return 'topology'
    if any(w in h for w in ['quantum', 'cloning', 'bell', 'holevo', 'entangle']):
        return 'quantum'
    if any(w in h for w in ['arrow', 'gibbard', 'social', 'voting', 'mechanism', 'myerson', 'nash']):
        return 'social_choice'
    if any(w in h for w in ['shannon', 'nyquist', 'bode', 'control', 'kalman']):
        return 'signal_control'
    if any(w in h for w in ['carnot', 'thermody', 'landauer']):
        return 'thermodynamics'
    if any(w in h for w in ['heisenberg', 'uncertainty']):
        return 'physics'
    if any(w in h for w in ['gibbs', 'fourier', 'runge', 'approximat']):
        return 'analysis'
    if any(w in h for w in ['calendar', 'symmetry_break', 'tuning', 'comma']):
        return 'applied'
    if any(w in h for w in ['goodhart', 'free_lunch', 'no_free']):
        return 'optimization'
    if any(w in h for w in ['crystal', 'map_proj']):
        return 'geometry'
    if any(w in h for w in ['godel', 'halting', 'rice', 'incomplet']):
        return 'logic'
    return 'other'

# Find cross-domain bridges within clusters
bridges = []
for cname, cdata in data.get('clusters', {}).items():
    if not isinstance(cdata, dict):
        continue
    members = cdata.get('members', [])
    chains = cdata.get('chains_supported', [])

    if len(members) < 2:
        continue

    # Check all pairs
    for i in range(len(members)):
        for j in range(i+1, len(members)):
            d1 = infer_domain(members[i])
            d2 = infer_domain(members[j])
            if d1 != d2:
                bridges.append({
                    'hub_a': members[i],
                    'domain_a': d1,
                    'hub_b': members[j],
                    'domain_b': d2,
                    'cluster': cname,
                    'shared_chains': chains,
                    'n_chains': len(chains),
                })

print(f"\nCross-domain bridges found at depth 3: {len(bridges)}")
print()

for b in bridges:
    print(f"  {b['hub_a']:45s} ({b['domain_a']:15s}) <-> {b['hub_b']:45s} ({b['domain_b']})")
    print(f"    Shared depth-3 chains: {', '.join(b['shared_chains'])}")
    print()

# Highlight the most interesting ones
print("=" * 70)
print("MOST INTERESTING DEPTH-3 BRIDGES")
print("=" * 70)

for b in bridges:
    if b['n_chains'] >= 2:
        print(f"\n  ** {b['hub_a']} <-> {b['hub_b']} **")
        print(f"     Domains: {b['domain_a']} <-> {b['domain_b']}")
        print(f"     Shared chains ({b['n_chains']}): {', '.join(b['shared_chains'])}")
        print(f"     Interpretation: These impossibilities respond to the SAME multi-step")
        print(f"     resolution strategies despite being in completely different domains.")

with open('noesis/v2/depth3_bridges.json', 'w') as f:
    json.dump({'bridges': bridges, 'total': len(bridges)}, f, indent=2)

print(f"\nSaved to noesis/v2/depth3_bridges.json")
