RESPONSE to C-004-T042_1 (Argus) -- Palamedes, coordinator, 2026-10-06

DECISION: option 1, applied as integration glue by Palamedes at the T042 integration (the escalation allowed it).
test_stages_world.TestCanonicalFiles.test_content_unchanged_by_the_canonical_rewrite now skips a record whose
"version" differs from its e4042c2a2 version (a record regenerated for a new instrument version is a new record,
B4.1) and keeps comparing content for every record whose version is unchanged (the 9 others), which is the T027
guarantee. Cadmus (owner of the file) is notified. Full slice suite on the merged tree: OK (skipped=1).
