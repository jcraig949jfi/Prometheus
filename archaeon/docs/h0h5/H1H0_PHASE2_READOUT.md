# H1/H0 phase-2 readout -- COMPLETE

Written 2026-09-10T23:15:24+00:00. Sets: cs-h1h0-1-p2, cs-h1h0-1-p2-r1, cs-h1h0-1-p2b. Numbers only; Harmonia analyses (block = target task, n = 12).

## Degeneracy check (second seed_root vs first, target 0, S00)

- {"verdict": "BIT_IDENTICAL", "task": "tgt-00", "differing_fields": [], "first_seed": {"status": "BUDGET_VM_OPS", "solved": false, "vm_ops": 6003, "oracle_calls": 12, "candidates_tried": 368}, "second_seed": {"status": "BUDGET_VM_OPS", "solved": false, "vm_ops": 6003, "oracle_calls": 12, "candidates_tried": 368}, "consequence": "the second-seed replicate is bit-identical and measures nothing; NOT issued (Harmonia item 4)"}

## Spec-hash dedup (Harmonia 1b)

- {"distinct_payloads": 73, "labels_sharing_a_hash": [], "refusal": null}

## Counts per cell

- fresh: {"completed": 12, "failed": 0, "queued": 0, "running": 0, "solved": 2}
- random_pack: {"completed": 12, "failed": 0, "queued": 0, "running": 0, "solved": 2}
- S00: {"completed": 12, "failed": 0, "queued": 0, "running": 0, "solved": 2}
- S10: {"completed": 12, "failed": 0, "queued": 0, "running": 0, "solved": 2}
- S01: {"completed": 12, "failed": 0, "queued": 0, "running": 0, "solved": 3}
- S11: {"completed": 12, "failed": 0, "queued": 0, "running": 0, "solved": 3}
- S00-deg: {"completed": 1, "failed": 0, "queued": 0, "running": 0, "solved": 0}

## Per task, per cell (kind status / solved / vm_ops)

- tgt-00: fresh: BUDGET_VM_OPS/-/6003; random_pack: BUDGET_VM_OPS/-/6022; S00: BUDGET_VM_OPS/-/6003; S10: BUDGET_VM_OPS/-/6022; S01: BUDGET_VM_OPS/-/6006; S11: BUDGET_VM_OPS/-/6019; S00-deg: BUDGET_VM_OPS/-/6003
- tgt-01: fresh: SOLVED/S/3667; random_pack: SOLVED/S/3562; S00: SOLVED/S/3667; S10: SOLVED/S/3562; S01: SOLVED/S/4152; S11: SOLVED/S/4938; S00-deg: -
- tgt-02: fresh: BUDGET_VM_OPS/-/6014; random_pack: BUDGET_VM_OPS/-/6003; S00: BUDGET_VM_OPS/-/6014; S10: BUDGET_VM_OPS/-/6003; S01: BUDGET_VM_OPS/-/6003; S11: BUDGET_VM_OPS/-/6027; S00-deg: -
- tgt-03: fresh: BUDGET_VM_OPS/-/6003; random_pack: BUDGET_VM_OPS/-/6025; S00: BUDGET_VM_OPS/-/6003; S10: BUDGET_VM_OPS/-/6025; S01: BUDGET_VM_OPS/-/6006; S11: BUDGET_VM_OPS/-/6006; S00-deg: -
- tgt-04: fresh: BUDGET_VM_OPS/-/6003; random_pack: BUDGET_VM_OPS/-/6003; S00: BUDGET_VM_OPS/-/6003; S10: BUDGET_VM_OPS/-/6003; S01: BUDGET_VM_OPS/-/6006; S11: BUDGET_VM_OPS/-/6009; S00-deg: -
- tgt-05: fresh: BUDGET_VM_OPS/-/6041; random_pack: BUDGET_VM_OPS/-/6007; S00: BUDGET_VM_OPS/-/6041; S10: BUDGET_VM_OPS/-/6007; S01: BUDGET_VM_OPS/-/6030; S11: BUDGET_VM_OPS/-/6021; S00-deg: -
- tgt-06: fresh: BUDGET_VM_OPS/-/6047; random_pack: BUDGET_VM_OPS/-/6009; S00: BUDGET_VM_OPS/-/6047; S10: BUDGET_VM_OPS/-/6009; S01: BUDGET_VM_OPS/-/6003; S11: BUDGET_VM_OPS/-/6017; S00-deg: -
- tgt-07: fresh: BUDGET_VM_OPS/-/6016; random_pack: BUDGET_VM_OPS/-/6002; S00: BUDGET_VM_OPS/-/6016; S10: BUDGET_VM_OPS/-/6002; S01: BUDGET_VM_OPS/-/6005; S11: BUDGET_VM_OPS/-/6007; S00-deg: -
- tgt-08: fresh: BUDGET_VM_OPS/-/6003; random_pack: BUDGET_VM_OPS/-/6009; S00: BUDGET_VM_OPS/-/6003; S10: BUDGET_VM_OPS/-/6009; S01: BUDGET_VM_OPS/-/6006; S11: BUDGET_VM_OPS/-/6020; S00-deg: -
- tgt-09: fresh: BUDGET_VM_OPS/-/6006; random_pack: BUDGET_VM_OPS/-/6002; S00: BUDGET_VM_OPS/-/6006; S10: BUDGET_VM_OPS/-/6002; S01: BUDGET_VM_OPS/-/6007; S11: BUDGET_VM_OPS/-/6006; S00-deg: -
- tgt-10: fresh: SOLVED/S/658; random_pack: SOLVED/S/578; S00: SOLVED/S/658; S10: SOLVED/S/578; S01: SOLVED/S/664; S11: SOLVED/S/672; S00-deg: -
- tgt-11: fresh: BUDGET_VM_OPS/-/6022; random_pack: BUDGET_VM_OPS/-/6010; S00: BUDGET_VM_OPS/-/6022; S10: BUDGET_VM_OPS/-/6010; S01: SOLVED/S/821; S11: SOLVED/S/503; S00-deg: -

By set: {"cs-h1h0-1-p2": {"completed": 11, "failed": 20, "cancelled": 42}, "cs-h1h0-1-p2b": {"completed": 48}, "cs-h1h0-1-p2-r1": {"completed": 14}}

H1 contrast label: transport_only (fresh vs random_pack); relevance inert at this scope (Harmonia 745d9c698)
