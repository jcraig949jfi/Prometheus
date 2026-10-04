# V2-B DEV-1 design/repair packet -- value-provenance observatory prov0

Cycle 1, DEV window 1 (opened 2026-10-04T11:37Z). Limiting layer addressed: the CONTENT DETECTOR (E-P1 failure;
E-011 lesion leak).

## Built
- `Aether/observatory/aeth_prov.py` (prov0). An external shadow; the physics is unchanged and never sees metadata.
  - Nodes: INIT, COPY, ADD, with a MUT flag; losing proposals are never parents.
  - Lineage bitmask (up to 64 origins) and hop depth.
  - Queries: last_writer, ancestry (DAG), holders, rung_profile.
  - Per-tick self-check: the predicted committed bytes must equal the physics output, otherwise ProvenanceMismatch.
- `Aether/observatory/aeth_prov_assay.py`: a content assay on the twin assay's worlds and origin draw; 64 origins per
  run; deterministic result hash.
- `Aether/observatory/aeth_prov_reduce.py`: pooled P3/P4/P5/P6 shares and the fwd positive-control rule.
- `Aether/test/test_aeth_prov.py`: the 7 directive fixtures (direct forwarding; no forwarding; transformed
  forwarding; two-parent composition; perturbation; overwritten ancestry; arbitration winner only), a 14-law rich-soup
  zero-mismatch self-check, and a refusal of unsupported laws. 22/22 pass; the aeth03 suite is still 64/64.

## Repairs made while building
- fwd relays that start the window holding a received byte now get INIT nodes. Without them the shadow mis-attributes
  the first relay emission; the self-check would have caught it as a mismatch.
- The result hash excluded wall time, so results are deterministic.

## DEV pilot (seed 100 only, not evidence)
fwd is the only law with multi-hop carried content (to distance 4, 6 hops, at n=64). add and rcv_add show transformed
ancestry that persists in place. rcv_add shows composed lineages. rcv_str spreads activity but not content
(distance <= 2). At full size, fwd P3_far 0.109 vs rcv 0 vs v1 0.

## Limits
- Energy is not a lineage in prov0.
- mov is unsupported; it is refused, not modelled.
- Single cut-offs (FAR/DEEP) are complemented by distributions.

## Frozen next TEST
Aether/V2B/TEST-1/PREREGISTRATION.md.

## Questions for external review
1. Is "losing proposals are never parents" the right causal convention for P3-P5? Or should arbitration losers
   count as counterfactual influences, measured separately with twins?
2. Is FAR = 3 (two hops beyond v1's natural one-hop copy) a fair line for "carried"?
3. Should energy become a lineage in prov1? Transfers move payload-derived amounts into energy.
