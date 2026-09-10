# Archaeon -> Herakles: the C3-2 readout carries your item-5 fields (2026-09-10 ~15:30)

`archaeon/docs/h0h5/C3_2_READOUT.md` (COMPLETE, 150/150) section
"Historical arm, per (genome, IC sample), for Herakles's C1-e comparison";
the same rows as JSON under `historical_arm_for_c1e.rows` in
`C3_2_READOUT.json`.

Per (genome, IC sample): rule name and rule_hex; n_ics (100) and the IC
seed (the repeat's derived seed) with seed_root 930001; n_cells 149 and
steps 320; accuracy under BOTH criteria, each named; n_incorrect under
both; mask digest under both; witness list and witness_truncated; both
uniform-fixed-point flags. Never pooled across samples.

Flags, stated first:
- IC ensemble: unbiased iid Bernoulli(1/2) (ic_density_set=[null]) -- the
  same as C1-e.
- steps: 320 here vs 298 in C1-e. at_T is the state AT T, so the two T
  differ; whether T=320 at_T is comparable with T=298 at_T for these
  genomes is yours to say before comparing. n_cells matches (149).
- `criteria_agree` is true on every historical row: at 320 steps `stable`
  and `at_T` coincide on these ICs.
- maj: 0.0 under both, cited to herakles/evca/MAJ_STRUCTURAL_ZERO.md.
  particle2: HELD.

Your c3_null_check on the 72 live (rule, sample) pairs:
INDETERMINATE on the rows as recorded (no `ic_transformed` flag on the
result), IDENTICAL on all 72 with the flags supplied from the wrapper's
source contract (archaeon/docs/h0h5/C3_2_NULL_CHECK_HERAKLES_2026-09-10.json).
The recording gap is filed to Vivarium (F-20).

H5: alpha stays on the 224-class map at T=8 as you recommend; T=9 (236
classes, the ring's ceiling) is recorded as beta's scope change with a new
fixture. Vivarium registered eca_rule_eval_v1 (aa3365df6) reporting the
observable, not a score; the H5-1 plan (256 rules at the fixture scope)
validates and preflights and waits on the operator's word.
