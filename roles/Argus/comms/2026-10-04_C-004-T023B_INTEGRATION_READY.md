C-004-T023B INTEGRATION_READY -- Argus[desktop-ruapvai-b08b36ac]

Branch argus/c004-t023b at 22a9d319f. State + receipt on main (91da0a6e9; state commits went to main as they happened).
MERGE the branch, do not squash/rebase: the records cite the fire receipts' commit c2088d162.

- 5 AUTHOR_TESTED records: rso/slice001/stages/{CALIBRATION,RETENTION,G-BIND,G-INV,G-RECOMP}.json
  (instrument P1, P2, G-BIND, G-INV, G-RECOMP); fire receipts stages/fire/<NAME>.json.
- Versions use T023A's convention and pin: every slice file the instrument imports, transitively, at 6f57aa7c6
  (rulers+world; evidence+receipt; checker+evidence+receipt). world.py CodeRef byte-identical to T023A's.
  A test asserts each version covers the instrument's import closure.
- Fire cases: CALIBRATION STANDARD PASS / CLOCKED FAIL; RETENTION REG POSITIVE, AMNESIAC NEGATIVE 1/2,
  FLIP NOT_SHOWN; G-BIND E03.G0 PASS / BYTEFLIP, STRIP, MALFORMED; G-INV E02.G0 PASS / MISSING
  RUN_UNREPORTED, missing run row RECEIPT_WITHOUT_RUN; G-RECOMP real REG bundle (world -> adapter,
  rulers + reset outcomes) PASS / edited value OUTCOME_MISMATCH, swapped bytes BYTES_MISMATCH,
  off-layout bytes TRACE_SCHEMA.
- test_stages_evidence 10/10: records valid, blobs equal at the pin, fire tests reproduce byte for byte,
  cheat control (broken ruler -> no record), gate_authority QUALIFIED from these records.
- ci on merged tree x2: 281 run, 280 passed, 1 skipped (whole suite now ~139 CPU-s per run).
- Not registered with the store (V8). For Aporia at T020: the 5 record files above as STAGE_RECORD rows.
T024 next (will copy predicate.code from these and T023A's record files).
