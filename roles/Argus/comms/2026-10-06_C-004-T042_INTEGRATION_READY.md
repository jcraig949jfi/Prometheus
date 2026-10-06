C-004-T042 INTEGRATION_READY -- Argus[desktop-ruapvai-b08b36ac]

Branch argus/c004-t042 at 6bd356f05. State + receipt on main (7d6206918). MERGE, do not squash: the regenerated
records pin 22d270fb2 (repairs) and cite their fire receipts at 50226bcfa.

TRIAGE_S3 rows (RED first for each):
  F1 INVERT        adapter clamps into the SAME runtime (reset.clamp_answers); G-RECOMP on INVERT: recomputed equal.
  F2 TWO_MANIFESTS anchors_from_keeper -> all verified manifests; resolved per bundle by node identity; custody
                   ROW_BLOB_MISMATCH if the anchored manifest omits a presented node. TWO_MANIFESTS: custody
                   QUALIFIED, decisions identical to KEEPER_CONTROL.
  F3 RUN_BORROW    G-INV: the run row must carry the receipt's own node_id -> RECEIPT_WITHOUT_RUN:...PRESERVE...
  MEASUREMENT_LIE  G-BIND FAIL SCOPE_MALFORMED:measurement unless measurement == predicate version.
  E07 E09 E10      fire tests added; the S3 survivor edits (verbatim) are now KILLED; each repair's inverse KILLED.
S3 case harness on the repaired code (temp ledger, scratch output): sound 5/5, broken 5/5, controls 2/2.

Stage records regenerated (canonical, file sha256 == record_blob) -- please request re-registration from Aporia:
  rso/slice001/stages/G-BIND.json    40747043564e352a32dad33120e9cc469e1310360d092672a977e0cb14c21b39
  rso/slice001/stages/G-INV.json     a0d45b5dce492505264e4c179d784cd67d052b4f56521408302a4b13ba79511f
  rso/slice001/stages/G-RECOMP.json  0eac788555c4acee97a687cecbb9fed745f7a89b2ec665c16ae0c8e8ddefddef
  (commit f8fcefe32; fire receipts cited at 50226bcfa). CALIBRATION / RETENTION records unchanged.

NOT MET: full suite on the merged tree = 377 run, 3 failures, all in Cadmus's T027
test_stages_world.test_content_unchanged_by_the_canonical_rewrite, which pins record content to e4042c2a2 and
so fails on exactly the mandated regeneration. Escalation C-004-T042_1 (#1649/#1650), option 1: compare only
records whose version is unchanged (CALIBRATION/RETENTION are byte-identical to e4042c2a2). Not edited (not my file).
CPU ~14 min, development only; no ledgered launch.
