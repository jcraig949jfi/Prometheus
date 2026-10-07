C-009-T016 INTEGRATION_READY -- Eupalamus[harry1-f1642b68]

Branch eupalamus/c009-t016 at 31733f237 (code d34cf480f + receipt). State + receipt A-001 on main (3838b6e0a).
Files: rso/witness/run_witness.py, rso/witness/tests/test_run_witness.py. No edit of ares/, rso/binding,
ares_client.py, ruler.py.

- `launch CONFIG --ledger --out`: one TOP_LEVEL launch per bundle; one RECEIPT row per (subject, arm, predicate,
  seeds) entry with parent_run_id + receipt_sha256; bundle receipts/ subjects/ seeds.json inventory.json run.json
  MANIFEST.json (last; carries launch_run_id). Every receipt binds (binding_reasons == []).
- `subject ...`: ares.search.run for a registered config; genome.json, sha256 (= ares_client.genome_digest), run
  receipt, EVERY episode seed drawn (per-generation training + held-out sets) -> subject_record.json
  "episode_seeds" = PREREG_DRAFT s3 exclusion input (OPEN 3). No fitness/log stored or printed.
- Refused before any ledger row: unknown arm, bad/duplicate seeds, seed < seed_floor, seed in EVAL_SEEDS /
  balanced_seeds_for / excluded subject record, non-canonical subject file, S-NOPL seeds != S seeds (value+order,
  Argus T017), non-empty output dir. Config: exclude_seed_records lists the two subject_record.json files.
- Evidence: RED (module absent), 24 plumbing tests GREEN (P=4, G=1, random populations, temp dir), witness suite 75
  OK, binding 13 OK on the merged tree, 5/5 mutants killed. No registered subject run (P=128, G=120), no
  accuracy/retention/reward computed.
- Not covered: P-ERASE probe-set / P-PRES seed-set construction (PREREG OPEN 2); action-trace bytes are not in the
  bundle (ares_client.receipt_dict does not return them).
