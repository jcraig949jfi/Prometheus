"""
Test 04: Goodhart <-> No-Cloning Null Model (RANDOMIZE->INVERT->TRUNCATE chain)
================================================================================
CLAIM: Sharing the chain RANDOMIZE->INVERT->TRUNCATE between Goodhart's Law
       and No-Cloning Theorem is statistically significant.

Falsification:
  PASS: p < 0.01 even after Bonferroni correction for multiple testing.
  FAIL: Chain is common enough that sharing it is unremarkable, OR p > 0.01 after correction.
"""

import json
import math
from pathlib import Path

import duckdb

DB_PATH = "F:/Prometheus/noesis/v2/noesis_v2.duckdb"
OUT_PATH = Path("F:/Prometheus/falsification/test_04_result.json")

con = duckdb.connect(DB_PATH, read_only=True)

# ── 1. Depth-2 pair prevalence ──────────────────────────────────────────────
total_hubs = con.execute("SELECT COUNT(DISTINCT hub_id) FROM depth2_matrix").fetchone()[0]
print(f"Total distinct hubs in depth2_matrix: {total_hubs}")

# Count hubs with each relevant pair
ri_hubs = set(r[0] for r in con.execute(
    "SELECT DISTINCT hub_id FROM depth2_matrix WHERE op1='RANDOMIZE' AND op2='INVERT'"
).fetchall())
it_hubs = set(r[0] for r in con.execute(
    "SELECT DISTINCT hub_id FROM depth2_matrix WHERE op1='INVERT' AND op2='TRUNCATE'"
).fetchall())

n_ri = len(ri_hubs)
n_it = len(it_hubs)
n_both = len(ri_hubs & it_hubs)

print(f"Hubs with RANDOMIZE->INVERT: {n_ri}/{total_hubs} = {n_ri/total_hubs:.3f}")
print(f"Hubs with INVERT->TRUNCATE:  {n_it}/{total_hubs} = {n_it/total_hubs:.3f}")
print(f"Hubs with BOTH (R->I AND I->T): {n_both}/{total_hubs} = {n_both/total_hubs:.3f}")

# ── 2. Depth-3 probes for R->I->T ──────────────────────────────────────────
d3_rit = con.execute(
    "SELECT hub_id, verdict, confidence FROM depth3_probes "
    "WHERE op1='RANDOMIZE' AND op2='INVERT' AND op3='TRUNCATE'"
).fetchall()
print(f"\nDepth-3 R->I->T confirmed hubs: {len(d3_rit)}")
for hub, verdict, conf in d3_rit:
    print(f"  {hub}: {verdict} ({conf})")

# NOTE: Goodhart and No-Cloning are NOT in the depth2_matrix R->I or I->T lists,
# meaning the depth-3 chain was found through probing, not from depth-2 composition.
# The depth-2 base rates come from the 246 hubs that DO have these pairs filled.

# ── 3. Null model calculation ───────────────────────────────────────────────
# We need: P(a hub has the R->I->T chain)
#
# Approach A: From depth-2 conditional
#   P(R->I) = n_ri / total_hubs
#   P(I->T | has R->I) ≈ n_both / n_ri  (hubs that have both / hubs that have R->I)
#   P(R->I->T) ≈ P(R->I) × P(I->T | has R->I) = n_both / total_hubs

p_ri = n_ri / total_hubs
p_it = n_it / total_hubs
p_it_given_ri = n_both / n_ri if n_ri > 0 else 0.0
p_chain_conditional = p_ri * p_it_given_ri  # = n_both / total_hubs

# Approach B: Independence assumption
p_chain_indep = p_ri * p_it

print(f"\n-- Null model estimates --")
print(f"P(R->I) = {p_ri:.4f}")
print(f"P(I->T) = {p_it:.4f}")
print(f"P(I->T | R->I) = {p_it_given_ri:.4f}")
print(f"P(chain) [conditional] = {p_chain_conditional:.4f}  (= {n_both}/{total_hubs})")
print(f"P(chain) [independent] = {p_chain_indep:.4f}")

# ── 4. P(two specific hubs BOTH have R->I->T) ──────────────────────────────
# Use the more conservative (higher) estimate: conditional
p_one = p_chain_conditional
p_two = p_one ** 2

print(f"\nP(one hub has R->I->T):  {p_one:.4f}")
print(f"P(two specific hubs both have it): {p_two:.6f}")

# ── 5. Expected pairs sharing this chain by chance ──────────────────────────
n_pairs = math.comb(total_hubs, 2)
expected_pairs = n_pairs * p_two
print(f"\nC({total_hubs},2) = {n_pairs} possible hub pairs")
print(f"Expected pairs sharing R->I->T by chance: {expected_pairs:.2f}")

# ── 6. Multiple testing correction (Bonferroni) ────────────────────────────
# 9 operators, so 9^3 = 729 possible depth-3 chains
n_ops = 9
n_possible_chains = n_ops ** 3
print(f"\nPossible depth-3 chains (9^3): {n_possible_chains}")

# The claim was found by searching — we checked all possible chains
# Bonferroni: p_corrected = p_raw × number_of_tests
p_raw = p_two
p_bonferroni = min(1.0, p_raw * n_possible_chains)

print(f"p_raw (two hubs share chain):  {p_raw:.6f}")
print(f"p_bonferroni (×{n_possible_chains}):         {p_bonferroni:.6f}")

# ── 7. Alternative: how many depth-3 chains are shared by ANY pair? ─────────
# From depth3_probes, count chains shared by 2+ hubs
chain_sharing = {}
all_d3 = con.execute(
    "SELECT op1, op2, op3, hub_id FROM depth3_probes WHERE verdict IN ('MATCHED','CONFIRMED','CRACKED')"
).fetchall()
for op1, op2, op3, hub in all_d3:
    chain_key = f"{op1}->{op2}->{op3}"
    chain_sharing.setdefault(chain_key, set()).add(hub)

print(f"\n-- Depth-3 chains with 2+ hubs --")
shared_chains = {k: v for k, v in chain_sharing.items() if len(v) >= 2}
for chain, hubs in sorted(shared_chains.items(), key=lambda x: -len(x[1])):
    print(f"  {chain}: {len(hubs)} hubs — {hubs}")

n_shared_chains = len(shared_chains)
print(f"\nTotal depth-3 chains shared by 2+ hubs: {n_shared_chains}")

# ── 8. Verdict ──────────────────────────────────────────────────────────────
# The key question: is p_bonferroni < 0.01?
# But also: the conditional base rate n_both/total_hubs is the fraction of hubs
# that have both depth-2 pairs. If that fraction is high, the chain is not rare.

print(f"\n{'='*60}")

if p_bonferroni < 0.01:
    result = "PASS"
    confidence = "HIGH"
    evidence = (
        f"R->I->T chain shared by Goodhart and No-Cloning. "
        f"Depth-2 base rates: P(R->I)={p_ri:.3f}, P(I->T)={p_it:.3f}. "
        f"Hubs with both depth-2 pairs: {n_both}/{total_hubs}={p_chain_conditional:.3f}. "
        f"P(two specific hubs share chain)={p_two:.2e}. "
        f"After Bonferroni correction (×{n_possible_chains}): p={p_bonferroni:.4f} < 0.01. "
        f"Expected pairs sharing any depth-3 chain by chance: {expected_pairs:.1f}. "
        f"Result is significant even accounting for multiple testing."
    )
elif p_chain_conditional > 0.15:
    result = "FAIL"
    confidence = "HIGH"
    evidence = (
        f"R->I->T chain is common: {n_both}/{total_hubs} = {p_chain_conditional:.1%} of hubs "
        f"have both constituent depth-2 pairs. Sharing this chain is unremarkable."
    )
else:
    result = "FAIL"
    confidence = "MODERATE"
    evidence = (
        f"R->I->T chain: P(two hubs share)={p_two:.4f}, "
        f"Bonferroni-corrected p={p_bonferroni:.4f} > 0.01. "
        f"Base rate for chain: {n_both}/{total_hubs}={p_chain_conditional:.3f}. "
        f"The shared chain is not significant after correcting for the {n_possible_chains} "
        f"possible depth-3 chains that could have been found."
    )

print(f"RESULT: {result} (confidence: {confidence})")
print(f"EVIDENCE: {evidence}")

# ── Save ────────────────────────────────────────────────────────────────────
output = {
    "test": 4,
    "paper": "Noesis v2 — Goodhart/No-Cloning Shared Chain",
    "claim": "Sharing the chain RANDOMIZE->INVERT->TRUNCATE between Goodhart's Law and No-Cloning Theorem is statistically significant",
    "result": result,
    "confidence": confidence,
    "evidence": evidence,
    "details": {
        "total_hubs": total_hubs,
        "n_hubs_R_I": n_ri,
        "n_hubs_I_T": n_it,
        "n_hubs_both_pairs": n_both,
        "p_R_I": round(p_ri, 4),
        "p_I_T": round(p_it, 4),
        "p_chain_conditional": round(p_chain_conditional, 4),
        "p_chain_independent": round(p_chain_indep, 4),
        "p_two_hubs_share": round(p_two, 8),
        "bonferroni_factor": n_possible_chains,
        "p_bonferroni": round(p_bonferroni, 6),
        "expected_pairs_by_chance": round(expected_pairs, 2),
        "depth3_shared_chains": {k: list(v) for k, v in shared_chains.items()},
        "goodhart_nocloning_in_depth2_RI": False,
        "note": "Goodhart and No-Cloning are NOT in depth2_matrix R->I or I->T hub lists; chain found through targeted depth-3 probing only",
    },
    "implications_for_other_papers": (
        "The R->I->T chain has a high depth-2 base rate: 39/246 = 15.9% of hubs possess both "
        "constituent pairs. After Bonferroni correction for 729 possible depth-3 chains, "
        "the significance of the Goodhart/No-Cloning shared chain depends critically on whether "
        "the corrected p-value crosses 0.01. Cross-domain structural isomorphisms in Noesis v2 "
        "should be tested with similar null models before claiming deep structural connections."
    ),
}

OUT_PATH.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
print(f"\nSaved to {OUT_PATH}")

con.close()
