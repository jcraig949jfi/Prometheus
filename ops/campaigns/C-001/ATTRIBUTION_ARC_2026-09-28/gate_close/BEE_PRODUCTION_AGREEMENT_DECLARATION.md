# E-003 BEE production s4.3 agreement: declaration (Archaeon; committed BEFORE running it)
**Inputs** (owner commit 72ed6e160, sealed in PRODUCTION_SEAL.json):
- S4_SAMPLE_PRE.jsonl, sha256 c9a4859a74d7f40d8568e2d5ad9144dc969cc959ff45cb2283218cba137b1d4b: 200 s4-sampled births;
- S4_SAMPLE_OWNER.jsonl, sha256 76f7d6e8b7b04c77820ec6798393728f14cf9c94788b8c84f87680196d913288: the owner's per-locus output in the
  bee_fresh exchange format (frozen driver a320d94b).

**Method:** the SAME tool as the fresh set (bee_fresh.py @ c28a74a97, unchanged), with no new comparison logic.
- Each record's {k, mem, inputs, occupied} goes to `bee_fresh ref`, giving the frozen reference 006a0789 and Archaeon's tracer
  4f18a0e9, with L = 64, budget 256, COPYALL allowed, entry 0.
  * These are r022153's parameters, the ones under which Archaeon's dry run reproduced the r022153 births bit for bit
    (bee_dryrun_v5.py).
  * Both tracers assert value equality with the frozen VM.
- `bee_fresh cmp`: raw, per class, >= 0.995 on label/addr/ctrl/exec, owner vs both.

**Declared scope limit:** pre_labels / entity_origins (the persisted per-byte ORIGIN attributes) are NOT an input.
- The exchange format carries no origin field (fixed before the fresh-set seed); a data label is ["E", side, j].
- Origin agreement is therefore not tested by this check. It is recorded as a limit, not a pass.

**Unit:** the gate is over all 200 sampled births. The unit is births within one run; there is no duplicate structure.
