# H1/H0 phase-2 readout -- PARTIAL

Written 2026-09-10T18:30:24+00:00. Sets: cs-h1h0-1-p2, cs-h1h0-1-p2-r1, cs-h1h0-1-p2b. Numbers only; Harmonia analyses (block = target task, n = 12).

## Degeneracy check (second seed_root vs first, target 0, S00)

- {"verdict": "BIT_IDENTICAL", "task": "tgt-00", "differing_fields": [], "first_seed": {"status": "BUDGET_VM_OPS", "solved": false, "vm_ops": 6003, "oracle_calls": 12, "candidates_tried": 368}, "second_seed": {"status": "BUDGET_VM_OPS", "solved": false, "vm_ops": 6003, "oracle_calls": 12, "candidates_tried": 368}, "consequence": "the second-seed replicate is bit-identical and measures nothing; NOT issued (Harmonia item 4)"}

## Counts per cell

- fresh: {"completed": 12, "failed": 0, "queued": 0, "running": 0, "solved": 2}
- random_pack: {"completed": 0, "failed": 5, "queued": 0, "running": 0, "solved": 0}
- S00: {"completed": 12, "failed": 0, "queued": 0, "running": 0, "solved": 2}
- S10: {"completed": 0, "failed": 5, "queued": 0, "running": 0, "solved": 0}
- S01: {"completed": 0, "failed": 5, "queued": 0, "running": 0, "solved": 0}
- S11: {"completed": 0, "failed": 5, "queued": 0, "running": 0, "solved": 0}
- S00-deg: {"completed": 1, "failed": 0, "queued": 0, "running": 0, "solved": 0}

## Per task, per cell (kind status / solved / vm_ops)

- tgt-00: fresh: BUDGET_VM_OPS/-/6003; random_pack: FAILED; S00: BUDGET_VM_OPS/-/6003; S10: FAILED; S01: FAILED; S11: FAILED; S00-deg: BUDGET_VM_OPS/-/6003
- tgt-01: fresh: SOLVED/S/3667; random_pack: FAILED; S00: SOLVED/S/3667; S10: FAILED; S01: FAILED; S11: FAILED; S00-deg: -
- tgt-02: fresh: BUDGET_VM_OPS/-/6014; random_pack: FAILED; S00: BUDGET_VM_OPS/-/6014; S10: FAILED; S01: FAILED; S11: FAILED; S00-deg: -
- tgt-03: fresh: BUDGET_VM_OPS/-/6003; random_pack: FAILED; S00: BUDGET_VM_OPS/-/6003; S10: FAILED; S01: FAILED; S11: FAILED; S00-deg: -
- tgt-04: fresh: BUDGET_VM_OPS/-/6003; random_pack: FAILED; S00: BUDGET_VM_OPS/-/6003; S10: FAILED; S01: FAILED; S11: FAILED; S00-deg: -
- tgt-05: fresh: BUDGET_VM_OPS/-/6041; random_pack: -; S00: BUDGET_VM_OPS/-/6041; S10: -; S01: -; S11: -; S00-deg: -
- tgt-06: fresh: BUDGET_VM_OPS/-/6047; random_pack: -; S00: BUDGET_VM_OPS/-/6047; S10: -; S01: -; S11: -; S00-deg: -
- tgt-07: fresh: BUDGET_VM_OPS/-/6016; random_pack: -; S00: BUDGET_VM_OPS/-/6016; S10: -; S01: -; S11: -; S00-deg: -
- tgt-08: fresh: BUDGET_VM_OPS/-/6003; random_pack: -; S00: BUDGET_VM_OPS/-/6003; S10: -; S01: -; S11: -; S00-deg: -
- tgt-09: fresh: BUDGET_VM_OPS/-/6006; random_pack: -; S00: BUDGET_VM_OPS/-/6006; S10: -; S01: -; S11: -; S00-deg: -
- tgt-10: fresh: SOLVED/S/658; random_pack: -; S00: SOLVED/S/658; S10: -; S01: -; S11: -; S00-deg: -
- tgt-11: fresh: BUDGET_VM_OPS/-/6022; random_pack: -; S00: BUDGET_VM_OPS/-/6022; S10: -; S01: -; S11: -; S00-deg: -

By set: {"cs-h1h0-1-p2": {"completed": 11, "failed": 20, "cancelled": 42}, "cs-h1h0-1-p2-r1": {"completed": 14}}

H1 contrast label: transport_only (fresh vs random_pack); relevance inert at this scope (Harmonia 745d9c698)
