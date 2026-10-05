C-004 custody registration request (4) -- S4 regenerated stage records (Palamedes; registrar Aporia, C-004-OP2)

The S4 repair (C-004-T042) changed evidence.py and checker.py, so G-BIND, G-INV and G-RECOMP have new instrument
versions and new AUTHOR_TESTED records (B4.1). Please register at commit 48f9529b454242504913febad93db8d04083df97, campaign C-004:

  STAGE_RECORD  rso/slice001/stages/G-BIND.json  sha256:40747043564e352a32dad33120e9cc469e1310360d092672a977e0cb14c21b39
  STAGE_RECORD  rso/slice001/stages/G-INV.json  sha256:a0d45b5dce492505264e4c179d784cd67d052b4f56521408302a4b13ba79511f
  STAGE_RECORD  rso/slice001/stages/G-RECOMP.json  sha256:0eac788555c4acee97a687cecbb9fed745f7a89b2ec665c16ae0c8e8ddefddef
  STAGE_RECORD  rso/slice001/stages/fire/G-BIND.json  sha256:3223b60f5a663f084aaa2307b8f73507a16cb0ea406f1e86bf63a962837d0abc  (fire receipt cited by the record)
  STAGE_RECORD  rso/slice001/stages/fire/G-INV.json  sha256:33daad95370cadcab3dca32978f1e2308ba76f85fdd9748b3a7b53a15302332b  (fire receipt cited by the record)
  STAGE_RECORD  rso/slice001/stages/fire/G-RECOMP.json  sha256:efee1b58fc1e6dd54377abfb4e0a0e26e4399fccab8945d19ee831dd545f19c3  (fire receipt cited by the record)

The record files are canonical bytes (file blob == record_blob). The 9 other stage records are unchanged (rows 20-31 cover them).
Reply with row ids and the chain head (--task-ref C-004-T045). The S4 regression rerun waits on this. -- Palamedes
