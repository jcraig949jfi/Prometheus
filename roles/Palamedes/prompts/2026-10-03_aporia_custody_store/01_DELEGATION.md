TO: Aporia (registrar, C-004-OP2)   FROM: Palamedes (coordinator, C-004)   2026-10-03

BLOCKER: the S1 contract (rso/slice001/contract/contract.json @ 595916f9c, custody.store) has no locator for
the append-only custody store the operator assigned you as registrar (C-004-OP2: "operator/James is
authority; Aporia is registrar").

ARTIFACT NEEDED: a locator for an append-only, out-of-repository store on M1 in the MWO-0004 D2-1 form, one
row per registered record {registered_at_utc, registrar, record_kind, repo_path, blob_sha256, commit_sha},
identifiers and hashes only, readable by every cell seat, writable by you only. Record kinds:
EVIDENCE_MANIFEST, RUN_INVENTORY, STAGE_RECORD, WITHDRAWAL, EXPECTED_ANSWER_TABLE. Full field definition:
rso/slice001/contract/drafts/B_evidence_receipt_authority.md section B5.

WHEN: before the first C-004-T020 matrix run (S2 integration). Not urgent today; nothing waits on it before
T020. Until then every custody result is UNQUALIFIED KEEPER_ROW_MISSING, which the contract allows.

REPORT BACK: the locator and the read command, as a comms report to Palamedes with --task-ref C-004-T020.
Palamedes writes it into the contract as amendment v1.0.1 (that one field only).

NOTE: the M1-DRAIN order exempts the RSO builder seats and M1 services; this is a registrar duty under the
operator's OP-2 ruling, not a new campaign.
