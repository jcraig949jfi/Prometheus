I checked all three parts of claim C3 against the repository, and all three are true.

1. **`units_manifest.json` records artifact-file hashes: true.** The code that writes the manifest saves one record per unit with `task_id`, `exit_code`, `wall_s`, `artifact` and `artifact_sha256` (the sha256 of the unit's output file). See `Aether/runpod/aether_units/run.py:172-178` and `:190-193`. A committed manifest shows exactly those fields at `Aether/runpod/receipts/aether-units-20260927T165531Z/units_manifest.json:9-13`.
2. **There is no per-unit `result_sha256` in the manifest: true.** The writer code above has no such field, and a search of all 5 committed `units_manifest.json` files for `result_sha` finds nothing. `result_sha256` exists only inside each unit's own output JSON (`Aether/observatory/aeth03_unit.py:164`).
3. **The committed BUCKKEEP seed-0 unit's `result_sha256` is 08929d70...: true.** The file is `ops/campaigns/C-002/E-006/attempts_buckkeep/T-063__A-002__BUCKKEEP.json`. It shows host BUCKKEEP on Windows 11 with NumPy 2.4.3 (lines 15-17), `law` rcv_add and `seed_index` 0 (lines 23, 26), and `result_sha256` 08929d701836200d2e75d5fe0563e388b5ff0a225dce2cca0a769ea716ee9927 (line 41). It is the only committed rcv_add unit under `ops/campaigns`.

None of the committed manifests is from the R-13 rcv_add re-execution. The five in Git come from other Aether flights and never mention rcv_add, and the rcv_add flight's own manifest is not committed. Part 2 still holds because the manifest-writing code is the same for every flight.

`verdict.json` is written to the output directory.

VERDICT: CONFIRMED