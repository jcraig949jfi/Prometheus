"""
Materials Project: Phase Transition Energies Between Crystal Systems

For materials appearing in multiple crystal systems (polymorphs),
compute energy differences between phases and identify stability hierarchies.

Data: materials_project_10k.json (10K entries)
Output: mp_phase_transitions_results.json
"""

import json
import os
from collections import defaultdict
from itertools import combinations
from statistics import mean, median, stdev

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "physics", "data", "materials_project_10k.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "mp_phase_transitions_results.json")

# ── 1. Load data ──────────────────────────────────────────────────────────────
with open(DATA_PATH) as f:
    raw = json.load(f)

print(f"Loaded {len(raw)} entries")

# ── 2. Group by formula, track crystal systems + energies ─────────────────────
# For each formula, collect (crystal_system, formation_energy_per_atom) pairs
formula_phases = defaultdict(list)
for entry in raw:
    formula = entry["formula"]
    cs = entry["crystal_system"]
    e = entry["formation_energy_per_atom"]
    formula_phases[formula].append({"crystal_system": cs, "energy": e, "material_id": entry["material_id"]})

# ── 3. Find polymorphs: formulas in 2+ distinct crystal systems ───────────────
polymorphs = {}
for formula, phases in formula_phases.items():
    systems = set(p["crystal_system"] for p in phases)
    if len(systems) >= 2:
        polymorphs[formula] = phases

print(f"Total unique formulas: {len(formula_phases)}")
print(f"Polymorphic formulas (2+ crystal systems): {len(polymorphs)}")

# ── 4. Compute transition energies for each polymorph ─────────────────────────
# For each formula, find the lowest-energy entry per crystal system,
# then compute pairwise energy differences between systems.
transitions = []
per_formula_transitions = {}

for formula, phases in polymorphs.items():
    # Lowest energy per crystal system (ground state polymorph in each system)
    best_per_system = {}
    for p in phases:
        cs = p["crystal_system"]
        if cs not in best_per_system or p["energy"] < best_per_system[cs]["energy"]:
            best_per_system[cs] = p

    systems_sorted = sorted(best_per_system.keys())
    formula_trans = []
    for cs_a, cs_b in combinations(systems_sorted, 2):
        e_a = best_per_system[cs_a]["energy"]
        e_b = best_per_system[cs_b]["energy"]
        delta_e = abs(e_b - e_a)
        # Order so lower-energy system comes first
        if e_a <= e_b:
            low_sys, high_sys = cs_a, cs_b
            low_e, high_e = e_a, e_b
        else:
            low_sys, high_sys = cs_b, cs_a
            low_e, high_e = e_b, e_a

        t = {
            "formula": formula,
            "system_low": low_sys,
            "system_high": high_sys,
            "energy_low": round(low_e, 6),
            "energy_high": round(high_e, 6),
            "delta_energy": round(delta_e, 6),
            "pair": f"{low_sys}->{high_sys}"
        }
        transitions.append(t)
        formula_trans.append(t)

    per_formula_transitions[formula] = formula_trans

print(f"Total pairwise transitions: {len(transitions)}")

# ── 5. Distribution of transition energies ────────────────────────────────────
delta_es = [t["delta_energy"] for t in transitions]
delta_es_sorted = sorted(delta_es)

percentiles = {}
for p in [10, 25, 50, 75, 90, 95, 99]:
    idx = int(len(delta_es_sorted) * p / 100)
    idx = min(idx, len(delta_es_sorted) - 1)
    percentiles[f"p{p}"] = round(delta_es_sorted[idx], 6)

energy_distribution = {
    "count": len(delta_es),
    "mean": round(mean(delta_es), 6),
    "median": round(median(delta_es), 6),
    "stdev": round(stdev(delta_es), 6) if len(delta_es) > 1 else 0,
    "min": round(min(delta_es), 6),
    "max": round(max(delta_es), 6),
    "percentiles": percentiles,
}

print(f"\nTransition energy distribution (eV/atom):")
print(f"  Mean:   {energy_distribution['mean']}")
print(f"  Median: {energy_distribution['median']}")
print(f"  Stdev:  {energy_distribution['stdev']}")
print(f"  Range:  [{energy_distribution['min']}, {energy_distribution['max']}]")

# ── 6. Most common crystal system transitions ────────────────────────────────
# Use canonical pair label (alphabetical)
pair_counts = defaultdict(int)
pair_energies = defaultdict(list)

for t in transitions:
    # Canonical alphabetical pair for counting
    pair_alpha = tuple(sorted([t["system_low"], t["system_high"]]))
    label = f"{pair_alpha[0]}<->{pair_alpha[1]}"
    pair_counts[label] += 1
    pair_energies[label].append(t["delta_energy"])

pair_stats = []
for label in sorted(pair_counts, key=pair_counts.get, reverse=True):
    es = pair_energies[label]
    pair_stats.append({
        "pair": label,
        "count": pair_counts[label],
        "mean_delta_e": round(mean(es), 6),
        "median_delta_e": round(median(es), 6),
        "stdev_delta_e": round(stdev(es), 6) if len(es) > 1 else 0,
        "min_delta_e": round(min(es), 6),
        "max_delta_e": round(max(es), 6),
    })

print(f"\nTop 10 most common transition pairs:")
for ps in pair_stats[:10]:
    print(f"  {ps['pair']:40s}  count={ps['count']:4d}  mean_dE={ps['mean_delta_e']:.4f} eV/atom")

# ── 7. Crystal system stability hierarchy ────────────────────────────────────
# For each crystal system, count how often it is the LOW-energy vs HIGH-energy phase
system_wins = defaultdict(int)   # times this system is the lower-energy phase
system_losses = defaultdict(int) # times this system is the higher-energy phase

for t in transitions:
    system_wins[t["system_low"]] += 1
    system_losses[t["system_high"]] += 1

all_systems = sorted(set(list(system_wins.keys()) + list(system_losses.keys())))
hierarchy = []
for s in all_systems:
    w = system_wins.get(s, 0)
    l = system_losses.get(s, 0)
    total = w + l
    win_rate = round(w / total, 4) if total > 0 else 0
    hierarchy.append({
        "crystal_system": s,
        "times_lower_energy": w,
        "times_higher_energy": l,
        "total_comparisons": total,
        "stability_rate": win_rate,
    })

hierarchy.sort(key=lambda x: x["stability_rate"], reverse=True)

print(f"\nCrystal system stability hierarchy (win rate = fraction of pairwise comparisons where system is lower energy):")
for h in hierarchy:
    print(f"  {h['crystal_system']:14s}  wins={h['times_lower_energy']:4d}  losses={h['times_higher_energy']:4d}  rate={h['stability_rate']:.3f}")

# ── 8. Head-to-head matrix ───────────────────────────────────────────────────
# For each ordered pair (A, B), count how often A is lower energy than B
h2h = defaultdict(lambda: {"wins": 0, "losses": 0})
for t in transitions:
    key_win = (t["system_low"], t["system_high"])
    key_loss = (t["system_high"], t["system_low"])
    h2h[key_win]["wins"] += 1
    h2h[key_loss]["losses"] += 1

# Build a clean matrix
h2h_matrix = {}
for sa in all_systems:
    row = {}
    for sb in all_systems:
        if sa == sb:
            row[sb] = "-"
        else:
            key = (sa, sb)
            w = h2h.get(key, {"wins": 0})["wins"]
            l = h2h.get(key, {"losses": 0})["losses"]
            row[sb] = f"{w}W/{l}L"
    h2h_matrix[sa] = row

# ── 9. Notable examples ──────────────────────────────────────────────────────
# Smallest transitions (near-degenerate polymorphs)
transitions_sorted = sorted(transitions, key=lambda x: x["delta_energy"])
smallest = transitions_sorted[:20]
largest = transitions_sorted[-20:]

# Most polymorphic formulas
most_polymorphic = sorted(polymorphs.items(), key=lambda x: len(set(p["crystal_system"] for p in x[1])), reverse=True)[:20]
most_polymorphic_summary = []
for formula, phases in most_polymorphic:
    systems = sorted(set(p["crystal_system"] for p in phases))
    energies = {s: round(min(p["energy"] for p in phases if p["crystal_system"] == s), 6) for s in systems}
    most_polymorphic_summary.append({
        "formula": formula,
        "n_crystal_systems": len(systems),
        "crystal_systems": systems,
        "lowest_energy_per_system": energies,
        "n_entries": len(phases),
    })

print(f"\nMost polymorphic formulas:")
for m in most_polymorphic_summary[:10]:
    print(f"  {m['formula']:12s}  {m['n_crystal_systems']} systems: {', '.join(m['crystal_systems'])}")

# ── 10. Energy histogram bins ────────────────────────────────────────────────
bins = [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 100.0]
hist = []
for i in range(len(bins) - 1):
    lo, hi = bins[i], bins[i + 1]
    count = sum(1 for e in delta_es if lo <= e < hi)
    hist.append({"bin_low": lo, "bin_high": hi, "count": count})

# ── Assemble results ─────────────────────────────────────────────────────────
results = {
    "metadata": {
        "source": "materials_project_10k.json",
        "total_entries": len(raw),
        "unique_formulas": len(formula_phases),
        "polymorphic_formulas": len(polymorphs),
        "total_pairwise_transitions": len(transitions),
        "crystal_systems": sorted(all_systems),
    },
    "energy_distribution": energy_distribution,
    "energy_histogram": hist,
    "pair_statistics": pair_stats,
    "stability_hierarchy": hierarchy,
    "head_to_head_matrix": h2h_matrix,
    "most_polymorphic_formulas": most_polymorphic_summary,
    "smallest_transitions": smallest,
    "largest_transitions": largest,
    "all_transitions": transitions,
}

with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {OUT_PATH}")
print(f"Total transitions recorded: {len(transitions)}")
