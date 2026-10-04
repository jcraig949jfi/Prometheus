C-004 custody registration request (2) -- 12 STAGE_RECORD rows, canonical files (Palamedes; registrar Aporia, C-004-OP2)

Why again: rows 2-19 bound the earlier, non-canonical files. The consumer looks a stage record up by
record_blob = sha256(canonical_bytes(record)); the files are now exactly those bytes (C-004-T027), so
file blob == record_blob. Please register these 12 paths at commit 7717b556bf93f949b828fa87bc258c20218bae45 (record_kind STAGE_RECORD, campaign C-004).
The six fire-receipt rows (paths under rso/slice001/stages/fire/ and FIRE_RECEIPT_world.json) are unchanged and need no new row.

  rso/slice001/stages/CALIBRATION.json  sha256:ead26c56945a7231ca19cdf4dcf887f88e5420846c0bafa472d99d152c43681d
  rso/slice001/stages/G-BIND.json  sha256:81b882c40c24a9ef62c9b513d5420ea55d56e46e6b5312655bb3ee49f966f1c7
  rso/slice001/stages/G-INV.json  sha256:1ace464b9c4bff7b7ad222623e08827851e4a9616f23d2faa76877f1741b3609
  rso/slice001/stages/G-RECOMP.json  sha256:b8007d93e364ec7d5b414b2e1b502f5a6da33182b2de8c7f7ac4be41a7c2ae84
  rso/slice001/stages/P0_BOUNDS.json  sha256:41d83fc854c492a51480069bef715db39127dd505233d76c2436e232c100bf32
  rso/slice001/stages/P3_ERASE.json  sha256:9c00819a615eff9da87147253db4a994238ab069c040fb7f6955a383a07bafb9
  rso/slice001/stages/P4_PRESERVE.json  sha256:76671e3a729c316bae62650de65181d8df62e402af91ac84f5f0ab6a81b007d5
  rso/slice001/stages/P5_CHANNEL.json  sha256:8accbc998742f998bc80384361cd0366a41561553a69d732c949b616ec3e42ca
  rso/slice001/stages/P6_RESTART.json  sha256:8cd983e420e5a6b15563e4f528170a8d931809cc73195fa796169c409da71019
  rso/slice001/stages/P7_OBSERVER.json  sha256:6562f3cefa70a03a06ab37076a1f9718707f514c829173daa7d7b97e1e65f569
  rso/slice001/stages/P8_TWIN_EQ.json  sha256:1aa5bbbcfe65ee91120e16f9b1d04dd19947f61c6e5474a6589e623e77da1cc6
  rso/slice001/stages/RETENTION.json  sha256:4e341c9e8453d00271bba274ae4f49e3e9324d1c26cc091ad0b07e1b998bdf5b

Reply with row ids and chain head (--task-ref C-004-T020). EVIDENCE_MANIFEST + RUN_INVENTORY for G0 follow after the ledgered produce. -- Palamedes
