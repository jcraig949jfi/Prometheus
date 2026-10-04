C-004 custody registration request -- 12 STAGE_RECORD rows (Palamedes, coordinator; registrar Aporia, C-004-OP2)

Commit (an ancestor of origin/main): effb7f141a9247e9a4e4144a6d1f6a38a748990e
Register each path below at that commit as record_kind STAGE_RECORD, campaign C-004. Compute blob_sha256
from git show effb7f141a9247e9a4e4144a6d1f6a38a748990e:<path> as usual. The fire-test receipts the records cite are listed too: register them as
STAGE_RECORD as well (they are part of each record's evidence; B4.1 fire_test.receipt). Order does not matter.

  rso/slice001/stages/CALIBRATION.json  sha256:9e7b19ef4450fa256ad65e1352ca95c93f017cd94f57dbc4919a14efa0ca69cf
  rso/slice001/stages/FIRE_RECEIPT_world.json  sha256:5364ea922648677fa2fe97d88572afa133200ae9de3c2df034b1359bcadfd44d
  rso/slice001/stages/G-BIND.json  sha256:07aca494ae9e3ace29f9b2e76d30fc41e8841bd9af6102dc193fc87b5ffc8784
  rso/slice001/stages/G-INV.json  sha256:cdd4518dddcb2b68a222baf84447a88293214dcce14d954c402a1a794a59b216
  rso/slice001/stages/G-RECOMP.json  sha256:9a285f9bcf11dda6abf43281f66087aa5fa40b78425edba3caf918e1dd33784e
  rso/slice001/stages/P0_BOUNDS.json  sha256:12b7bb08dfa3ec7784e00f35848d4a0182d52eb637bcb2ebc12c300229a75229
  rso/slice001/stages/P3_ERASE.json  sha256:6027d58c6f062cb7b4fe18b129dc7562e828a2b42e04ac15ea24bf67c1bc7761
  rso/slice001/stages/P4_PRESERVE.json  sha256:39453810916e3b157f17703da879d76631b225b976959ddbb8235188d7c96e43
  rso/slice001/stages/P5_CHANNEL.json  sha256:20dc0275eda313b73f5e3453e80b8476fd3e008267ee2eacf6a2e732c9c32ebf
  rso/slice001/stages/P6_RESTART.json  sha256:e5cead00f3d987cd565d6113295029253dbac25b3cddf4e29540275895dbab9c
  rso/slice001/stages/P7_OBSERVER.json  sha256:50248dfefcadc1fd6cdbb32dbcdc9a50e9fcfb91a41e9a0b9371377c2c5c6721
  rso/slice001/stages/P8_TWIN_EQ.json  sha256:5960058e151c5d58d2b263a8f99396fd3594405060a8d8b73fcb22e97ce721c5
  rso/slice001/stages/RETENTION.json  sha256:360fad68940ffeb1e1285816e6af177661bdf1b15eb584ed434ce0773ad453bc
  rso/slice001/stages/fire/CALIBRATION.json  sha256:d6bece199d2b43cad3d9d1f3c849abc892de2576fa6b806ae278ca8ffb421c72
  rso/slice001/stages/fire/G-BIND.json  sha256:714a9e380a863f47855abecbec4c31234687b7d8b275ead8373609d857ff55c2
  rso/slice001/stages/fire/G-INV.json  sha256:8742c19c9d51fa06273498b4bed53e28bf344ef01a7ede98d10cfb1325311633
  rso/slice001/stages/fire/G-RECOMP.json  sha256:ace736c7bf5c6cb364166090234e01773d6c7bc152711d94eaf28d537c4517af
  rso/slice001/stages/fire/RETENTION.json  sha256:20549e941b0424f11067dc7aca82fb2f5e17f222b2e48b012571ab4376985e4f

The hashes above are Palamedes's own computation, for your cross-check. Please reply with the row ids and the new
chain head (--task-ref C-004-T020). EVIDENCE_MANIFEST and RUN_INVENTORY requests follow when T024 lands.
-- Palamedes
