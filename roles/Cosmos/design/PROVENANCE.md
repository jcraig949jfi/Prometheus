# CWE provenance: what was borrowed, from where, and how much

Currency: 2026-09-23. No external code was copied into prometheus/cosmos/. Every external
item below is a CONCEPT, cited from recall (evidence tier: RECALLED, not re-fetched this
campaign; no web research was run). Repository donors are cited by path.

## Repository donors (inspected 2026-09-23)

| concept | donor | how used | code imported? |
|---|---|---|---|
| canonical-JSON sha256 content identity | prometheus/toolbox/receipt.py `_h` | recipe re-implemented in cosmos/hashing.py (full 64-hex) | no (module import pulls 15 kernel modules + kernel hash) |
| chained receipts (prev id) | prometheus/toolbox/receipt.py ReceiptWriter | ReceiptChain in cosmos/hashing.py | no |
| SHAM control | prometheus/toolbox/ref/transforms.py transform.shuffle.v1 | each family's sham(): the ask stops depending on the cue | no |
| translation manifest classes | roles/Bellerophon/atlas_bee | SELECTIVE_PAYS.v1 manifest in phenomenon.py | no |
| SELECTIVE_PAYS contract | archaeon/wse/ssf.py:66,103,107 + economics.py | verified; v1 abstraction, WSE contract untouched | no |
| hand-written reference organisms (log/one-slot/last) | archaeon/wse/controls.py (boundary map) | SEL/LOG/LAST per family, natively | no |
| denotational quotient over a frozen probe battery | roles/Aphrodite/engine/semantics.py | (a) miner collapses expressions with equal rank order; (b) cosmos/quotient.py over worlds | no |
| planted-truth world table, assay blind to it | roles/Aphrodite/science/campaign0/worlds.py | prometheus/cosmos/planted/ | no |
| Hamming-1 matched control partner | roles/Nestor/campaigns/z80atlas-2026-09-19/grammar.py control_partner | matched single-knob neighbours (DEFORMATION_OF) | no |
| typed edges DEFORMATION_OF / TRANSPLANT_OF, fact layers RAN/OBSERVED/CONCLUDED | atlas/sql/002_model_v2.sql | edge vocabulary + atlas_export.py | no (Atlas needs Postgres) |

## External concepts (RECALLED)

- Uncertainty sampling for active learning (Lewis and Gale, 1994) -> sampler.run_active.
- Level-set estimation / active boundary search (Gotovos et al., 2013) -> motivates the
  boundary and band attacks; NOT implemented as a GP.
- Invariant causal prediction / environment invariance (Peters, Buhlmann, Meinshausen,
  2016) -> leave-one-lineage-out scoring and the family-residual test are its spirit, not
  its algorithm.
- Max-statistic permutation null for selection over many hypotheses (Westfall and Young,
  1993) -> the whole-search permutation null in miner.mine.
- Metamorphic testing (Chen et al., 1998) -> coordinate-preserving pairs in the adversary.
- Counterexample-guided inductive synthesis (Solar-Lezama, 2006) -> the attack/revise loop.
- Kramers escape rate (Kramers, 1940) -> the sealed family's DECLARED hazard (deliberately
  approximate).
- Minimum description length -> complexity penalty lambda * size (a crude stand-in).

None of these determined what the engine may find; they shaped the instrument.
