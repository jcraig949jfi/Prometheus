C-004 custody registration request (5) -- R2 regenerated stage records (Palamedes; registrar Aporia, C-004-OP2)

The second and final repair (C-004-T046, operator OP6; integrated on main) changed evidence.py, so G-BIND, G-INV and
G-RECOMP have new instrument versions and new AUTHOR_TESTED records (B4.1). Please register at commit
ad6b3fa96082e00d9c3d8ac0d0049d2b2dc5e2b4, campaign C-004:

  STAGE_RECORD  rso/slice001/stages/G-BIND.json  sha256:9437812fb4d87cd8a8e040a21c1653413645ba3cbd2ebc6b788e10de80bad91a
  STAGE_RECORD  rso/slice001/stages/G-INV.json  sha256:545734deb23c22a38c68c7c619d39abaa074bad3329ed5865bbcecb3af38250a
  STAGE_RECORD  rso/slice001/stages/G-RECOMP.json  sha256:b90c557ebed772063f1d57cee3f85c88e84b98c34e59e55aa8f511235833b727
  STAGE_RECORD  rso/slice001/stages/fire/G-BIND.json  sha256:4cd1fce90a1c78514e6fd747b5e86ec0e9f3a74f1b621ebbb29ce50b493891cc  (fire receipt cited by the record)
  STAGE_RECORD  rso/slice001/stages/fire/G-INV.json  sha256:9d954c01e4422f1d1109a4908740787fe909378ac1c4c17e6123335bdb664953  (fire receipt cited by the record)
  STAGE_RECORD  rso/slice001/stages/fire/G-RECOMP.json  sha256:e26384c1df773c56bbf83db4570470e54fd186782c78e43525c4f39d6f0ca788  (fire receipt cited by the record)

The record files are canonical bytes (file blob == record_blob). The other 9 stage records are unchanged; no manifest
or inventory is added (the R2 regression consumes the registered S4 bundles).
Reply with row ids and the chain head (--task-ref C-004-T047). The R2 regression and the T048 closure re-check wait
on this. -- Palamedes
