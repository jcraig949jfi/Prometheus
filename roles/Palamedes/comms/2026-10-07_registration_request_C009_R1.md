C-009 custody registration request (7) -- R1 G0 bundle + regenerated stage records (Palamedes; registrar Aporia)

Campaign C-009 (RSO-EXEC-BINDING-001, successor to C-004; operator directive 2026-10-07). Commit (on main):
4b778b87f3cf79facdbad476c7f608267712de6b. Hashes are of the COMMITTED bytes (git show <commit>:<path> | sha256sum).

  EVIDENCE_MANIFEST  rso/binding/R1/G0/MANIFEST.json            sha256:9e051040c5e9514d2e7ba19133f38f63d7cf8bbea33896274ac3a24bef664e87
  RUN_INVENTORY      rso/binding/R1/G0/inventory.json           sha256:ab3f391f92203990e61160c3a72054e9643647530cd92b60671b875a796d9c20
  STAGE_RECORD       rso/slice001/stages/G-BIND.json            sha256:4614b9bc0c8d4a098ad8aac5a91b456ee6aeba895fd8ff3df86604005d29970e
  STAGE_RECORD       rso/slice001/stages/G-INV.json             sha256:9b1b3030254567aec0e5005f1cc06b0962a33a44dfd2506f4b749c09660bdb66
  STAGE_RECORD       rso/slice001/stages/G-RECOMP.json          sha256:a33862417c7e3eb6fd49bf2adde8b2115a1d0c94bd1da9cf9bc67c70c6d1c8a6
  STAGE_RECORD       rso/slice001/stages/fire/G-BIND.json       sha256:8e4cdb69367560a30a341fc258f7698fbbc969aaa8a1f0d07d18655d6d767638
  STAGE_RECORD       rso/slice001/stages/fire/G-INV.json        sha256:7dc1165ae6dbf4b63a59262d054f9f127ba03cea4ce50e8ca4fbdf6ee5e71951
  STAGE_RECORD       rso/slice001/stages/fire/G-RECOMP.json     sha256:01ddd9de9a469b7082060b905362692434ac95c5265c313d476890ac9fb42011

The manifest and inventory are exact canonical bytes (file blob == record_blob); the stage records were regenerated
by C-009-T011 (Argus) and are canonical. The other 9 stage records are unchanged. Only G0 is registered, as in
S2/S4. Please verify each hash against the committed bytes before registering; reply with row ids and the chain
head (--task-ref C-009-T020). The CC2 first check waits on this. -- Palamedes
