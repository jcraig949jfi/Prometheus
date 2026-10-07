# C-004-T048 exposure note (Pallas[m2-1500b878], claude-fable-5-1, SPECTREX5)

This is a fresh session (comms boot 2026-10-06T21:53:17Z). It inherits no in-context memory from the Pallas
sessions that ran T005, T030 or T041; what it knows of them it read from the committed tree.

Read before writing this set, in order:
- ops/campaigns/C-004/tasks/C-004-T048/TASK.json (packet, notes), C-004-OP6/TASK.json (operator ruling), C-004-T046
  and T047 TASK.json status lines, the T046 attempt receipt (RECEIPT.json: evidence_added and evidence_executed
  prose, which names test CLASSES and counts but not bodies).
- rso/slice001/FREEZE_R2.md; hashes verified. rso/slice001/contract/AMENDMENT_v1.0.5.md. rso/slice001/s4/R2/REGRESSION.md.
- rso/slice001/evidence.py: lines 86-181 (Anchors, AnchorChoice, anchors_from_keeper, _artifact_hits,
  resolve_anchors), 418-470 (inventory_terminal, _ended_before, g_inv), 753-802 (required_records, custody); the
  function index of the file. rso/slice001/checker.py lines 470-486 (_relative, decide_all, decision_bytes) and a
  grep for CL-CUST.
- rso/slice001/fixtures/evidence_cases.py: lines 142-356 and 538-560 (Case, Base, real_base, g0_dicts, claims,
  _inventory, keeper_rows, make_bundle, manifest_of, retained, _case, g0, _keeper_case, keeper), make_receipt_dict.
- rso/slice001/challenge/S4/closure_set/* in full (this seat's own prior set and drivers), and from
  challenge/S3/attack_set/run_cases.py the function index plus run_checks, decide_case, case_two_manifests,
  case_run_borrow.
- Data: rso/slice001/s4/G0/inventory.json row shapes, statuses, launch kinds, and for each S4 receipt the cited
  row's start/end against created_at_utc (the fact that created_at_utc precedes every S4 run's start_utc); one
  S4 receipt's dict (LAGD BOUNDS) to the execution block.
- rso/slice001/s2/LEDGER.jsonl usage via ledger.Ledger.usage() (15 launches, 2924.7 s).

NOT read: any file under rso/slice001/tests/ (no test body, at any point); the T042 or T046 repair DIFFS (the
repaired functions were read in their frozen final form only); s4/MATRIX.*, s4/R2/MATRIX.*; S5_REPORT.md;
contract/CONTRACT.md body (only a grep for clause numbers); drafts; T042/T043/T044/T045 receipts; the
mutation.py or ledger.py bodies beyond the names the drivers import.

Same-family caveat (CONTRACT.md s6 as cited in S3/S4): reviewer and author are both Claude models of one
vendor; the T046 author ran claude-opus-5-5, this reviewer runs claude-fable-5-1. Cell membership: this seat is a
member of the RSO Builder Cell and took the S3 and S4 sets; this is not an outside review.
