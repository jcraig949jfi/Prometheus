# RB-6 LEVER CHECK -- RESULT (FORENSIC, NOT A DISPOSITION)

Run 2026-09-27, 16:33-17:03 EDT, M4, 2 workers, labels "RB6-<supply>-L1-{obs,val,hold}".
Script: rb6_lever_check.py (imports a17/tier3d/fair/identity/tier3e unmodified; sets
A17_FASTEVAL=1 and calls a17.worker_init in every worker). Raw record:
RB6_LEVER_CHECK_L1.log. The run was stopped at the 30-minute cap during the 4th supply
(NONG1_MIX_4), so the end-of-run JSON was not written; the log holds everything below.
(The script now also checkpoints each supply to a .partial.jsonl; that change came after
the run.) No rb6 python process remains (checked with Get-CimInstance).

Design: supplies = K5 regimes GCD_RICH_2, G1_PLUS_4 and G1_PLUS_1, rebuilt with K5's rng
string. The fixed initial library is L1 ([G1] + PRISTINE). There is ONE observe stage per
supply, shared by every variant, so any difference comes from the improver alone. The
candidate libraries are costed on the a17 selection geometry (8 cells x 3 VALIDATE
families) and, for the selected library, on 4 fresh HELD-OUT cells per validate family.
"sel" and "hold" are mean paired savings in charges vs INHERITED (L1).

| supply     | variant   | selected | schema                          | sel   | hold  |
|------------|-----------|----------|---------------------------------|-------|-------|
| GCD_RICH_2 | V0_BASE   | S1_1     | (acc + gcd({H}, v))             | 16997 | 10864 |
|            | V1_H2ONLY | MEMORISE | -                               | 16467 | 10440 |
|            | V1_H12    | S1_1     | (acc + gcd({H}, v))             | 16997 | 10864 |
|            | V3_MEDIAN | S1_4     | (acc + ({H} * v))               | 16940 | 10656 |
|            | V2_LOOK   | S1_1     | (acc + gcd({H}, v))             | 16997 | 10864 |
| G1_PLUS_4  | V0_BASE   | S1_3     | (acc + gcd({H}, v))             | 15064 | 17776 |
|            | V1_H2ONLY | MEMORISE | -                               | 14910 | 17430 |
|            | V1_H12    | S1_3     | same as V0                      | 15064 | 17776 |
|            | V3_MEDIAN | S1_3     | same as V0                      | 15064 | 17776 |
|            | V2_LOOK   | S1_3     | same as V0                      | 15064 | 17776 |
| G1_PLUS_1  | V0_BASE   | S1_1     | (acc + gcd({H}, v))             | 11161 | 12642 |
|            | V1_H2ONLY | MEMORISE | -                               | 11064 | 12702 |
|            | V1_H12    | S1_1     | same as V0                      | 11161 | 12642 |
|            | V3_MEDIAN | S1_1     | same as V0                      | 11161 | 12642 |
|            | V2_LOOK   | S1_1     | same as V0                      | 11161 | 12642 |
(gcd(x, y) abbreviates math.gcd(abs(x), abs(y)).) Classes per supply: 4 / 5 / 4.
Single-hole candidates: 5 / 5 / 4. Two-hole LGGs with >= 2 in-space instantiations:
2 / 1 / 1. Ruler-NEW (tier3e key): 0 everywhere. Every schema selection is G1-built
(compounding proxy = 1).

Findings (n = 3 supplies; forensic):
F1 HOLE COUNT (P8) HAS NO SELECTION LEVER HERE. Allowing two-hole LGGs (V1_H12) changes
   nothing in 3/3 supplies. The depth-2 in-space rule leaves only 1-2 useful two-hole
   schemas per supply, and a two-hole schema is never the best candidate. With two-hole
   schemas ONLY (V1_H2ONLY), the selector falls back to MEMORISE every time, which means
   no two-hole schema beat MEMORISE. So the variant changes the product's IDENTITY
   (schema -> no schema, and V3-proxy 1 -> 0) but barely changes held-out value:
   -424 / -346 / +60 charges, 0.5-4% of the ~11-18k saving.
F2 2-STEP LOOKAHEAD (P19, CMP proxy) = BASELINE in 3/3. On the same observations, every
   eligible candidate adds the same number of fresh next-generation schemas, or the
   saving already ranks the top candidate first. The lookahead signal carries no
   information here.
F3 MEDIAN STATISTIC (P19) differs in 1/3 supplies: (acc + ({H} * v)) in place of the gcd
   schema. The two are within 57 charges on the selection cells and 208 on held-out
   cells, a coin flip between near-equivalent G1-built schemas.
F4 SPREAD: 4 variants x 3 supplies. Schema identity differs from V0 in 4/12
   variant-supply pairs (3 of them are the degenerate H2ONLY -> MEMORISE). The largest
   held-out value difference is 4% of the saving (the held-out SE was not recorded,
   because the run was killed before the JSON was written; K5-scale SEs suggest
   differences of this size are within noise). The spread in V3 is non-zero only
   through the degenerate H2ONLY arm, and the spread in V4 is zero.

Interpretation: the DERIVATION-SIDE and SELECTION-SIDE levers tested here (hole count,
selection statistic, lookahead) are practically inert in this DSL and supply. The
candidate menus are too small (4-9) and too semantically homogeneous (every candidate
lies inside G1's span, per K5/K7) for the choice among them to matter. This is the
partial STOP signal RB-6 asked about: V5 is untestable through these levers. It is NOT
yet a stop for V5 as a whole. The inventory predicts the larger levers are the
EFFICIENCY ones (P15 entry finals, P16 walk order, P18 escrow split) and the ACCESS ones
(P7 member space, P23 composition, owned by RB-3). None of those was tested. Stage 1 of
IMPROVER_EVOLUTION_PROGRAM.md s6 should test P15/P18 before the program goes further.

Cost note: under shared load (another seat's 5-worker job was running), one supply took
5.4-24 min per worker. Most of the time goes to costing ~10 candidate libraries x 24
cells + 12 held-out cells at up to 250k charges each. A full 18-supply Stage 1 needs
about 2-3 h at 2 workers, or a pre-computed per-cell cost cache.

Caveats: n = 3, all from the K5 regimes and all with the L1 start (no PRISTINE start).
Two-hole instantiation uses exact structural matching after normalisation, filling each
depth-2 hole with atoms only, so a few in-space instantiations that the tier3d
string-substitution rule would also map may be missed (hypothesis: negligible). The
one-hole candidate set was asserted equal to tier3d.derive_schemas, and the assertion
passed.
