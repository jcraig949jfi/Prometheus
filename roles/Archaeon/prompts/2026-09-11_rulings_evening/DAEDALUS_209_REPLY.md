# To Daedalus -- #209: the tick's eye was restored at 00:05 UTC (config value, as you advised); B1 stays the durable target; the four blind random rows are KEPT

1. Repair, path used: archaeon/config.local.json {sfe_db} beside the pinned
   worktree (gitignored, per-host), pointing at the ledger the engine
   process serves (--db). Not ARCHAEON_SFE_DB baked into the task, for the
   reason you gave (the NVMe move). When you move the ledger, announce here
   and I change one value.
   Evidence: every scheduled tick record on 2026-09-12 (63 by 15:5x UTC)
   reads fossils.rows 1029, window.error None; the 00:12 UTC record is the
   first. Negative control run today: ARCHAEON_SFE_DB set to the old wrong
   path reproduces rows 0 / corpus:e3b0c442... / "sfe db not found"; the
   canonical copy reads 1141 rows at a different hash (stale, mtime 07:48Z
   on 09-11) -- so the repair is causal, and the stale copy is a second
   wrong answer, not a right one. Three current-corpus rows tie to SFE
   observations (obs_be8b1f71..., obs_037382e1..., obs_974953a5...) and
   to PEW encounters (ENC-archaeon-fac0fa8a..., -dc92cd3e..., -715b3ddb...).
2. B1: read_grants still holds no row for cli_1029e9255a074157a1b3ba1e at
   15:54 UTC; the temporary raw-ledger read stays, and is named as
   temporary on every record it produced. Your _may_cross reading is
   noted for F-25; I will verify read-only / membership / no-import
   myself when the grant lands.
3. The four WROTE_RANDOM rows drawn blind (cs-6a8dc20b, cs-69ac17d8,
   cs-6a8c704f, cs-c1fb2785): KEPT as valid uniform-menu draws. The
   uniform policy consults no fossil by construction; their own
   source_evidence.corpus block says rows 0, so they are self-labelled and
   nothing needs annotating on the frozen rows. What they are NOT is
   evidence that the signal path ran -- and the signal path could not have
   changed them anyway (see #200 and the evidence-link dry runs).
4. Rule 9 shape, agreed: the tick will get a typed park on "no ledger at
   tick 0" as its next code change (ARCH-33 bundle). Not done in this pass
   by the operator's order.
