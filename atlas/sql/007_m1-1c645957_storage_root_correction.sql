-- Atlas migration 007 (claimed in comms 2026-09-19): storage_root means the
-- engine instance's PRIMARY store (local_files/3+; registry storage_role).
-- local_files/2 set it from any directory holding the ledger, including
-- copies, backups and a scratch probe. The never-erase merge cannot clear a
-- value by offering NULL, so the M1 instances Atlas wrote are reset here and
-- re-derived by the next local_files pass. eng_906356f7 (M2) is Atlas-M2's
-- and is not touched.
UPDATE atlas.engine_instance SET storage_root = NULL
WHERE engine_instance_key IN ('eng_8a37a5d305969034d488c43e', 'eng_192d0c561da0ca77bd652916');
