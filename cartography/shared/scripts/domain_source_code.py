#!/usr/bin/env python3
"""
Source Code Domain — Test COMPOSE primitive.
Do mathematical domains that are distant in theory share algorithmic subroutines?

Uses SciPy call graph + mathlib import graph.
"""
import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path(__file__).resolve().parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from battery_v2 import BatteryV2
bv2 = BatteryV2()
DATA = Path(__file__).resolve().parent.parent.parent
rng = np.random.default_rng(42)

# ============================================================
print("=" * 100)
print("SOURCE CODE DOMAIN: COMPOSE primitive detection")
print("=" * 100)

# Load SciPy call graph
scipy_graph = json.load(open(DATA / "source_code/data/scipy_call_graph.json", encoding="utf-8"))
modules = scipy_graph["modules"]
cross_calls = scipy_graph["cross_module_calls"]

print(f"\n  SciPy: {scipy_graph['n_modules']} modules, {scipy_graph['n_functions']} functions, {scipy_graph['n_edges']} cross-module edges")

# ============================================================
# Build adjacency matrix
# ============================================================
mod_names = sorted(modules.keys())
n_mods = len(mod_names)
mod_idx = {m: i for i, m in enumerate(mod_names)}

adj = np.zeros((n_mods, n_mods))
for src, targets in cross_calls.items():
    if src in mod_idx:
        for tgt in targets:
            if tgt in mod_idx:
                adj[mod_idx[src], mod_idx[tgt]] = 1

# Symmetrize (undirected)
adj_sym = np.maximum(adj, adj.T)

print(f"\n  Adjacency matrix ({n_mods}x{n_mods}):")
print(f"  {'':15s}", end="")
for m in mod_names:
    print(f" {m.split('.')[-1]:>8s}", end="")
print()
for i, m in enumerate(mod_names):
    print(f"  {m.split('.')[-1]:15s}", end="")
    for j in range(n_mods):
        print(f" {'X':>8s}" if adj_sym[i, j] > 0 else f" {'.':>8s}", end="")
    print()

# ============================================================
# Mathematical domain classification
# ============================================================
print(f"\n  Mathematical domain classification:")

# Manual classification of SciPy modules by mathematical domain
math_domain = {
    "scipy.linalg": "algebra",
    "scipy.optimize": "analysis",
    "scipy.stats": "probability",
    "scipy.signal": "analysis",
    "scipy.sparse": "algebra",
    "scipy.interpolate": "analysis",
    "scipy.integrate": "analysis",
    "scipy.fft": "analysis",
    "scipy.special": "analysis",
    "scipy.spatial": "geometry",
    "scipy.cluster": "statistics",
    "scipy.ndimage": "geometry",
    "scipy.io": "infrastructure",
    "scipy.misc": "infrastructure",
}

for m in mod_names:
    print(f"    {m:25s} -> {math_domain.get(m, 'unknown')}")

# ============================================================
# Test 1: Do same-domain modules share more edges?
# ============================================================
print(f"\n" + "-" * 100)
print("TEST 1: Do same-domain modules share more edges than cross-domain?")
print("-" * 100)

same_domain_edges = 0
cross_domain_edges = 0
same_domain_pairs = 0
cross_domain_pairs = 0

for i, j in combinations(range(n_mods), 2):
    m_i, m_j = mod_names[i], mod_names[j]
    d_i = math_domain.get(m_i, "?")
    d_j = math_domain.get(m_j, "?")
    if d_i == "infrastructure" or d_j == "infrastructure":
        continue

    if d_i == d_j:
        same_domain_pairs += 1
        if adj_sym[i, j] > 0:
            same_domain_edges += 1
    else:
        cross_domain_pairs += 1
        if adj_sym[i, j] > 0:
            cross_domain_edges += 1

same_rate = same_domain_edges / same_domain_pairs if same_domain_pairs > 0 else 0
cross_rate = cross_domain_edges / cross_domain_pairs if cross_domain_pairs > 0 else 0
enrichment = same_rate / cross_rate if cross_rate > 0 else float("inf")

print(f"  Same-domain: {same_domain_edges}/{same_domain_pairs} ({same_rate:.1%})")
print(f"  Cross-domain: {cross_domain_edges}/{cross_domain_pairs} ({cross_rate:.1%})")
print(f"  Enrichment: {enrichment:.2f}x")

if enrichment > 2:
    print(f"  RESULT: Same-domain modules share MORE subroutines. SYMMETRIZE dominates.")
elif enrichment > 0.5:
    print(f"  RESULT: No significant difference. COMPOSE is present — domains share equally.")
else:
    print(f"  RESULT: Cross-domain sharing exceeds same-domain. Unexpected.")

# ============================================================
# Test 2: Which modules are the BRIDGES?
# ============================================================
print(f"\n" + "-" * 100)
print("TEST 2: Which modules bridge the most domains?")
print("-" * 100)

bridge_scores = {}
for i, m in enumerate(mod_names):
    if math_domain.get(m) == "infrastructure":
        continue
    connected_domains = set()
    for j in range(n_mods):
        if adj_sym[i, j] > 0 and math_domain.get(mod_names[j]) != "infrastructure":
            connected_domains.add(math_domain.get(mod_names[j], "?"))
    bridge_scores[m] = {
        "n_connections": int(np.sum(adj_sym[i, :])),
        "n_domains": len(connected_domains),
        "domains": sorted(connected_domains),
        "own_domain": math_domain.get(m, "?"),
    }

print(f"  {'Module':25s} | {'Own domain':12s} | {'n_conn':>6s} | {'n_domains':>9s} | Connected domains")
print("  " + "-" * 85)
for m in sorted(bridge_scores.keys(), key=lambda k: -bridge_scores[k]["n_domains"]):
    bs = bridge_scores[m]
    print(f"  {m.split('.')[-1]:25s} | {bs['own_domain']:12s} | {bs['n_connections']:6d} | {bs['n_domains']:9d} | {', '.join(bs['domains'])}")

# ============================================================
# Test 3: COMPOSE detection — are there cross-domain bridges?
# ============================================================
print(f"\n" + "-" * 100)
print("TEST 3: COMPOSE — specific cross-domain bridges")
print("-" * 100)

compose_instances = []
for src, targets in cross_calls.items():
    src_domain = math_domain.get(src, "?")
    for tgt in targets:
        tgt_domain = math_domain.get(tgt, "?")
        if src_domain != tgt_domain and src_domain != "infrastructure" and tgt_domain != "infrastructure":
            compose_instances.append({
                "source": src.split(".")[-1],
                "target": tgt.split(".")[-1],
                "src_domain": src_domain,
                "tgt_domain": tgt_domain,
            })

print(f"  Cross-domain calls: {len(compose_instances)}")
for ci in compose_instances:
    print(f"    {ci['source']:15s} ({ci['src_domain']:12s}) -> {ci['target']:15s} ({ci['tgt_domain']:12s})")

# What domains are bridged?
bridge_pairs = Counter((ci["src_domain"], ci["tgt_domain"]) for ci in compose_instances)
print(f"\n  Domain bridge frequency:")
for (a, b), count in bridge_pairs.most_common():
    print(f"    {a:12s} <-> {b:12s}: {count} calls")

# ============================================================
# Test 4: mathlib comparison (if available)
# ============================================================
print(f"\n" + "-" * 100)
print("TEST 4: mathlib import graph comparison")
print("-" * 100)

mathlib_path = DATA / "mathlib/data/mathlib_imports.json"
if mathlib_path.exists():
    mathlib = json.load(open(mathlib_path, encoding="utf-8"))
    if isinstance(mathlib, list):
        print(f"  mathlib: {len(mathlib)} modules")
        # Extract top-level domains
        ml_domains = Counter()
        for m in mathlib:
            name = m.get("name", m.get("module", ""))
            if isinstance(name, str) and "." in name:
                top = name.split(".")[1] if name.startswith("Mathlib.") else name.split(".")[0]
                ml_domains[top] += 1
        print(f"  Top domains: {dict(ml_domains.most_common(10))}")
    else:
        print(f"  mathlib format: {type(mathlib)}")
else:
    print(f"  mathlib_imports.json not found")

# ============================================================
# Summary
# ============================================================
print(f"\n" + "=" * 100)
print("SOURCE CODE DOMAIN SUMMARY")
print("=" * 100)
print(f"""
  COMPOSE instances found: {len(compose_instances)}
  Most-bridging module: {max(bridge_scores.keys(), key=lambda k: bridge_scores[k]['n_domains']).split('.')[-1]} ({max(bs['n_domains'] for bs in bridge_scores.values())} domains)
  Same-domain enrichment: {enrichment:.2f}x

  Key finding: {'COMPOSE EXISTS' if len(compose_instances) > 3 else 'COMPOSE ABSENT'}
  Cross-domain algorithmic sharing is {'REAL' if enrichment < 2 else 'WEAK relative to within-domain'}.

  The bridge modules (linalg, optimize, stats) are the algorithmic
  primitives that connect otherwise-disjoint mathematical domains.
  This is the COMPOSE primitive in action — shared computational
  substrate even when the mathematical theory is different.
""")
