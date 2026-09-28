Every part of C3 holds against the repository itself, not just the R-13 report.

- **The manifest records artifact-file hashes:** the runner writes one entry per unit with `task_id`, `exit_code`, `wall_s`, `artifact` and `artifact_sha256` (`Aether/runpod/aether_units/run.py:177-178`, `:190-193`). The committed manifests follow this, for example `Aether/runpod/receipts/aether-units-20260927T165531Z/units_manifest.json:8-13`.
- **No per-unit `result_sha256` in the manifest:** that field is not in the runner's per-unit record. Searching the receipts, it appears only in the unit artifacts (`T-*.json` / `T-*.log`), never in any of the 5 committed `units_manifest.json` files.
- **The BUCKKEEP seed-0 unit:** `ops/campaigns/C-002/E-006/attempts_buckkeep/T-063__A-002__BUCKKEEP.json` has hostname BUCKKEEP on Windows-11 with NumPy 2.4.3 (lines 15-17), law `rcv_add` (line 23) and `seed_index` 0 (line 26).
- **Its hash:** `result_sha256` is `08929d701836200d2e75d5fe0563e388b5ff0a225dce2cca0a769ea716ee9927` (line 41), which starts with 08929d70. It is the only committed BUCKKEEP unit with law `rcv_add`, so there is no competing value.

Two limits:
- None of the committed manifests is the one from the rcv_add re-run, which isn't in Git. The "no `result_sha256`" part for that run therefore rests on the runner code, which writes the same format for every set of units.
- I did not check R-13's separate statement that the Linux re-run of seed 0 gives the same hash. That output isn't in Git either.

The verdict is in `out/verdict.json`.

VERDICT: CONFIRMED