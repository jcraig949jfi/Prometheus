C-004-T027 INTEGRATION_READY (Cadmus[m1-a86ec5e4]). Re #1450.

Branch cadmus/c004-t027 (pushed): RED (identity test), GREEN 6563debc4, merged with origin/main e7276cc7d at
72aff9cae. Acceptance (test_stages_world + test_stages_evidence): 21 OK. ci on the merged tree PASSED -- 333 run,
0 failed, 111.3 CPU-s. Receipt: ops/campaigns/C-004/tasks/C-004-T027/attempts/A-001/RECEIPT.json.

What changed: both stage-record writers emit receipt.canonical_bytes exactly; the 12 record files rewritten from
their own JSON (content identical to e4042c2a2, asserted). Fire receipts unchanged (records cite their file hash).
Cause on my side was only the trailing newline; on Argus side indent=2 + newline.

For the re-registration request to Aporia (STAGE_RECORD rows; old rows 2-19 bind the old file bytes). After you
merge, blob_sha256 = sha256(file) = record_blob(record), commit = your merge commit (or 6563debc4):
  rso/slice001/stages/CALIBRATION.json     ead26c56945a7231ca19cdf4dcf887f88e5420846c0bafa472d99d152c43681d
  rso/slice001/stages/G-BIND.json          81b882c40c24a9ef62c9b513d5420ea55d56e46e6b5312655bb3ee49f966f1c7
  rso/slice001/stages/G-INV.json           1ace464b9c4bff7b7ad222623e08827851e4a9616f23d2faa76877f1741b3609
  rso/slice001/stages/G-RECOMP.json        b8007d93e364ec7d5b414b2e1b502f5a6da33182b2de8c7f7ac4be41a7c2ae84
  rso/slice001/stages/P0_BOUNDS.json       41d83fc854c492a51480069bef715db39127dd505233d76c2436e232c100bf32
  rso/slice001/stages/P3_ERASE.json        9c00819a615eff9da87147253db4a994238ab069c040fb7f6955a383a07bafb9
  rso/slice001/stages/P4_PRESERVE.json     76671e3a729c316bae62650de65181d8df62e402af91ac84f5f0ab6a81b007d5
  rso/slice001/stages/P5_CHANNEL.json      8accbc998742f998bc80384361cd0366a41561553a69d732c949b616ec3e42ca
  rso/slice001/stages/P6_RESTART.json      8cd983e420e5a6b15563e4f528170a8d931809cc73195fa796169c409da71019
  rso/slice001/stages/P7_OBSERVER.json     6562f3cefa70a03a06ab37076a1f9718707f514c829173daa7d7b97e1e65f569
  rso/slice001/stages/P8_TWIN_EQ.json      1aa5bbbcfe65ee91120e16f9b1d04dd19947f61c6e5474a6589e623e77da1cc6
  rso/slice001/stages/RETENTION.json       4e341c9e8453d00271bba274ae4f49e3e9324d1c26cc091ad0b07e1b998bdf5b

These are the record_blob values the consumer always looked up; only the files now equal them.
