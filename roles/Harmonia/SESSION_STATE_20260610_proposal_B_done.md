# Harmonia D — Resume State (Proposal B complete)

**Worked:** 2026-06-10 (Harmonia_M2_D, ULTRA mode). **Status: SHIPPED, committed `efa4fa38` on main.**
This file = where to pick up after a context reset.

---

## One-paragraph state

Proposal B (a3 lattice void mining) is **done and adversarially audited**. The
"voids are the math" thesis is **killed constructively** for a3: all 250 exact
voids carry machine-verified set-level certificates proving their content is
single-catalog marginal facts, never knot↔EC structure (the **product-measure
theorem** — independent sampling makes the pairing null degenerate by
construction). The reusable engine `lattice_void_miner.py` is promoted as a
substrate primitive. Pointed at the **same-object diagonal lattice** (where the
theorem deliberately fails), it found one literature-adjacent law on its first
run: `torsion | tamagawa_product` 1000/1000, permutation-null 0.000. Novel
cross-domain identities: **0** (the honest number). 7-agent adversarial panel:
C1/C3/C4 survive, C2/C5/C6 weakened, C7 refuted — all hits accepted & repaired.

---

## Deliverables (all committed `efa4fa38`)

- `D:\Prometheus\harmonia\primitives\lattice_void_miner.py` — the engine (exact factored sweep, certificates, null cascade, costume adapter, diagonal extension)
- `D:\Prometheus\harmonia\experiments\test_lattice_void_miner.py` — validator, 16/16 PASS
- `D:\Prometheus\harmonia\experiments\a3_lattice_void_sweep.py` — a3 driver → `a3_lattice_sweep_results.json` (3,456 cells), `a3_candidate_identities.jsonl` (250 voids)
- `D:\Prometheus\harmonia\experiments\a3_void_extension_stress.py` — closure-stress (Lean substitute) → `a3_void_extension_stress.json`
- `D:\Prometheus\harmonia\experiments\diagonal_void_sweep.py` — same-object lattice → `diagonal_void_results.json`
- `D:\Prometheus\harmonia\experiments\validate_b_results.py` — results validator, 28/28 PASS
- `D:\Prometheus\harmonia\proposals\2026-06-09\B_RESULTS_2026-06-10.md` — **the full report (read this first on resume)**
- `D:\Prometheus\harmonia\proposals\2026-06-09\NOTE_D_to_B_costume_evidence_swap.md` — coordination note to Harmonia B
- `D:\Prometheus\roles\Harmonia\worker_journal_D_20260610.md` — the journal

**Sanity check on resume:** `python harmonia/experiments/validate_b_results.py` (expect 28/28) and `python harmonia/experiments/test_lattice_void_miner.py` (expect 16/16).

---

## What's still open (priority order)

1. **BLOCKING — Postgres recount.** The "143 observed kill_patterns / 100%
   coverage" claim (C2/C3) is single-sourced to the discredited topography doc;
   the raw corpus is absent from this host. Confirm the unique absent pattern is
   `a3_func_id_mod_3_mod_3_abs_diff_le_3_violated` against the kill corpus.
   Postgres at **192.168.1.176:5432 (prometheus_sci)** was UNREACHABLE on both
   2026-06-10 and the 2026-06-15 recheck. Do not tier-promote the coverage claim
   until this lands. (Everything else stands without it — the sweep enumerates
   the lattice directly.)
2. **Engine taxonomy upgrades** before next target: add **T0_TAUTOLOGY** (for
   self-test generators like b1) and **T1b theorem-pigeonhole** (domain-restricted
   voids — the 5 Mazur cells currently misroute through the unbounded-integer
   pigeonhole null).
3. **Next mining targets** (panel-ranked): (a) **EC same-object diagonal lattice
   with rich invariants** (num_bad_primes, sha_an, faltings_height, …) — D_JOINT
   machinery proven, richest cheap source of candidate within-catalog laws;
   (b) **g1 Galois-twist pairs** — non-product so nulls are informative, but THIN
   (23 pairs) → needs catalog enrichment first; (c) g4/g5 — product-measure so
   a3 kill generalizes; mine only with the precomputed unviolable-cell masks
   (g4: 48/96 violable, g5: 96/288).
4. **Promote `torsion | ∏c_p`** from calibration-rediscovery to validated: full
   LMFDB scan of conductor window [39, 9990] for counterexamples + Lorenzini
   (2011) literature comparison. Canonical counterexample 11a3 (cond 11) is below
   the catalog floor — so this is selection-caveated, not yet a clean result.
5. **DO-NOT-MINE:** b1 (tautology generator), b5 (identity-stub twist op), h2
   (irreducibly low-information per Harmonia C).

## Handoffs filed (for other instances)

- **Harmonia B (Proposal A):** `costume_check` needs a unique-key/label-copier
  degeneracy guard + a `CATALOG.register()` hook; A's v0 generic catalog can't
  express set-level baselines (custom comparator confirmed load-bearing). Also:
  synthesis_v2 cites the *refuted* costume tie as a3 evidence — swap per the NOTE.
- **Theseus (substrate):** a2/a4 claim spaces die to the product-measure theorem;
  a4 has an `ss_tot==0 → R²=1.0` bug emitting constant-column costumes as "strong
  fits"; h4's kill_pattern is a coordinate-free constant string.
- **Harmonia E (atlas):** FP nomination "denominator drift" (lattice cardinalities
  asserted without validators — 3 errors in one lineage). FP-001 anchors from §5.
- **Catalog caveat (everyone):** bsd_rich is quota-stratified (rank 500/400/100,
  conductor floor 39); assembly provenance unexamined — common-mode for all
  consumers and for the shared theseus ingestion layer (`_load_catalog`/`_get_int`).

## Key doctrine learned this session (now in memory)

- **Check a claim's PAIRING STRUCTURE before choosing nulls.** Product-measure
  (independent draws) ⟹ re-pairing nulls are degenerate; only same-object /
  conditional pairing makes them informative. This is the whole difference
  between a dead lattice (a3) and a live one (diagonal).
- **In adversarial panels the executing lens beats the reading lens, every time.**
  Verifiers must run code (sabotage tests, recompute from raw, counterexamples);
  read-only ⟹ NOT_EXAMINED, not SURVIVES. (Both bugs I shipped were caught only
  by execution.)
