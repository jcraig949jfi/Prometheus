# Charon Journal — 2026-04-09 Data Sprint

## What happened

Another Claude Code instance found the LMFDB PostgreSQL mirror (devmirror.lmfdb.xyz:5432) and pulled 23 GB across 271 tables. Combined with browser downloads and API fetches, 8 datasets arrived:

| Dataset | Records | Source | Status |
|---------|---------|--------|--------|
| Maass forms (rigorous) | 35,416 (was 300) | PostgreSQL | **Wired** |
| Lattices | 39,293 (was 21) | PostgreSQL | **Wired** |
| Genus-2 curves (full) | 66,158 (50+ fields) | PostgreSQL | **Wired** |
| Siegel modular forms | 29,435 total | API + PostgreSQL | Sprint 2 |
| Hilbert modular forms | 368,356 | Browser | Sprint 2 |
| Bianchi modular forms | 233,333 | Browser | Sprint 2 |
| Hypergeometric motives | 61,063 families | Browser | Sprint 3 |
| Abstract groups | 544,831 | PostgreSQL | Sprint 3 |

## Sprint 1: Wire the three massive expansions

### Changes made
1. **search_engine.py**: Updated path constants to prefer postgres dumps. Rewrote `_load_maass`, `_load_lattices`, `_load_genus2` to handle postgres envelope format (`{"records": [...]}`) + normalize field names. Added 7 new search functions.
2. **concept_index.py**: Updated all 6 extractors (3 noun + 3 verb) for Maass/Lattices/Genus2 to handle postgres envelope format, field name normalization, and non-string object_id guards.
3. **tensor_bridge.py**: Added defensive str() cast for non-hashable object_ids.

### Results after realignment
| Metric | Before | After |
|--------|--------|-------|
| Search functions | 56 | **63** |
| Concept links | 1.91M | **2.74M** |
| Contributing datasets | 15 | **17** |
| Tensor objects | 205K | **280K** |
| Battery | 180/180 | **180/180** |

### New tensor connections
The Lattices dataset went from invisible (21 objects, no concept extraction) to one of the most connected:
- Lattices--NumberFields: sv=5,829 (second strongest in entire tensor)
- Lattices--SmallGroups: sv=5,526
- Lattices--LMFDB: sv=3,395
- Lattices--Isogenies: sv=3,307
- Lattices--SpaceGroups: sv=2,130
- Lattices--Polytopes: bond_dim=3, sv=265

ANTEDB--Maass (sv=283) and Fungrim--Maass (sv=89) are new cross-domain bridges.

## Challenge Queue

Consolidated 25 challenges from 5 sources (Claude, ChatGPT, Gemini, DeepSeek, Grok) into 17 deduplicated items. 6 in Tier 1 (run now), 6 in Tier 2 (setup needed), 5 in Tier 3 (blocked on data).

Key unblocks from the data sprint:
- C01 (Paramodular probe) unblocked by Siegel eigenvalue data
- C04 (Hilbert congruences) unblocked by 368K HMF data

Firing 5 challenges in parallel.

## Honest count
Novel cross-domain discoveries: **zero.**
Sprint 1 wired, documented, battery passes.

---

*Session: 2026-04-09 data sprint*
*Charon v5.1 -> v5.2 (data sprint + challenge queue)*
*Standing orders: explore the unpopular, trust nothing, kill everything*
