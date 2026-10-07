# FREEZE_W2 -- C-010 repaired witness machinery frozen for the re-check (C-010-T034) and the witness run (C-010-T020)

Frozen by Palamedes[harry1-679179c6] under C-010-T033 at 2026-10-07T13:33:38Z. Code commit 9dd4e9671db047076373baa5f170ede85a13764a. Preregistration:
rso/witness/PREREGISTRATION.md (sha256 099f408f6e7c1c3e6c1e3b885a2db42f58efd5a0a941a7d8e23205ab623bc1f7), unchanged.
Repair round after W1 (ADJUDICATION_W1.md; AMENDMENT_v1.0.1 NULL): C-010-T031 (Argus, evaluator R1-R4 + pins), T032
(Cadmus, NULL + E2 pin); integration: P-OBS on every witness seed. Earlier: T010-T012 and T013 (Palamedes): config generator (s3 seed procedure), the S-NOPL/P-RET pairing fix, the per-launch
bundle inventory (C-010-T012_1 option 2), WITNESS_SEEDS.json, and an end-to-end dry run on tiny random subjects
(rso/witness/dry_run.py: 3 launches, 16 receipts bound, P-FLAT PASS, custody QUALIFIED on a fixture store, every gate
evaluated; outcome values of the stand-ins not printed; re-run after the repair, clean). Witness suite 149 OK, binding 21 OK.

The witness path under challenge: rso/witness/ares_client.py (node executions), run_witness.py (subject runs,
launches, artifact storage, per-launch inventory, seed refusals), make_configs.py (seed procedure, configs),
evaluate.py (P-FLAT, binding, custody, artifact re-hash, oracle recomputation, gates, classes), ruler.py.
No registered subject has been run; no witness episode exists.

## Witness files (25)

    rso/witness/ADJUDICATION_W1.md  sha256:bb463a470ceda1c7b350960e29e5c6936b1fb3b6ba1c981b27f59b6dce861da3  2300
    rso/witness/AMENDMENT_v1.0.1.md  sha256:d7f765c58e7e3f3c931165a75b9bc6ecdfc8a02c87473e1e407acce02d6742ea  1660
    rso/witness/CANDIDATES.md  sha256:e0a2019bffd7359de58cfa7d063c168cf4e11c7a188fc1f8d84ded4ad4c80b4c  8886
    rso/witness/DESIGN_DRAFT.md  sha256:3ca211fb0898fa2854b41ac35c0295eaab487437042f3efb61490bb9b1c3a39a  6380
    rso/witness/ERASE_PROBES.md  sha256:297f2caf60aec08ae901ce224539d414bc78819e71710cf1d7506bab33f38a18  3533
    rso/witness/FREEZE_W1.md  sha256:5364363405cbf8d056b98dc771ff1ead4820249a7b7470117157ed0da09fe1c6  4984
    rso/witness/PREREGISTRATION.md  sha256:099f408f6e7c1c3e6c1e3b885a2db42f58efd5a0a941a7d8e23205ab623bc1f7  9578
    rso/witness/PREREG_DRAFT.md  sha256:8a46e6f3838d8c7c66a85b62eec85a3dff4d3ec023df46c5293281c580ef368a  7341
    rso/witness/RULER.md  sha256:a60c85222a3885dd29b9adfaf22b312ee2c16b66b5699b89f6b53b42b4ea607b  8360
    rso/witness/SELECTION.md  sha256:a76f72b0f0cad7bdc730e435d6a932d8ce448972b9d2e45c94fba84fd3fd9198  2096
    rso/witness/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/witness/ares_client.py  sha256:0028f21dcda032ff43876495d492ffe5e2f411afdf1723ac756626ef57adb1ec  19059
    rso/witness/contract.json  sha256:15b88fda7ab08744550168d67b2cfaba6903ec3badf6d9733db7dd32d14b1eb6  1149
    rso/witness/dry_run.py  sha256:be6cc3c9120cc0fd0e2c4b3d3e3cc16f7e91e28c2f04597504101b50be5ed5c6  4395
    rso/witness/evaluate.py  sha256:8bb426dee359ce14df61032a3fa647e689db9576b8f71d0606b9ef70707efdb1  24758
    rso/witness/make_configs.py  sha256:cd0a8a8cfcff969ef98c91832cadacae664552890ed53302235bbb97a54e7c36  4029
    rso/witness/ruler.py  sha256:6b972f9eef3127dc80f66bacfa26d61097304e74f486523ad1c65d7cd31caed8  13833
    rso/witness/run_witness.py  sha256:4ca20878ba1988c13ee53d8b2c3351097cb28ea90a8fddad6f50ec907dec1b92  23248
    rso/witness/tests/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/witness/tests/test_ares_client.py  sha256:5527af3284d10838c701d46d32c05a361d4d5b1f01a87e7b2906afc370887156  21225
    rso/witness/tests/test_evaluate.py  sha256:32edd0ddc80cce060f09966da3fcc88958f1c7aa2bb3c3d36ac0391486f4402c  28646
    rso/witness/tests/test_launch_inventory.py  sha256:76307ae690b71e28de504430d315bf9d4140f1986bf5dfcc68f5dd99332f8618  2250
    rso/witness/tests/test_make_configs.py  sha256:422959c12b01c3a4160334806c20c63defbc9919139a063b989351d7ab4b9e6d  5284
    rso/witness/tests/test_ruler.py  sha256:0d9ebb2f3024f45d73931a50a4a4f4d5fb247eb6af376dbf7e0c753f44ff054e  14210
    rso/witness/tests/test_run_witness.py  sha256:4c419664a25fe5714d8ee3990bbc5beadbf81f9f634b78ec581821a4e5be5c49  23472

## Dependencies frozen with it (11)

    rso/binding/binding.py  sha256:a5a7af0477253b4ff91b1f4ac639c9ba1229891c6633719f54dc0301e593923a  5306
    rso/binding/CONTRACT.md  sha256:08ba85a459fa6fb3160e923bebee48687420bd3f22a037bc99cc3ed06864371c  7145
    rso/binding/CLOSURE.md  sha256:c6ef89007f65b5e728dc6d65e8954c974a81a70d5140be57d26fb3f59f612b50  4263
    rso/slice001/evidence.py  sha256:bd4e7bbf338bf30e1b4a2fa5bf68ed2b76db93a669a05d27a63584c6faeb2866  38969
    rso/slice001/ledger.py  sha256:9c61a8940993c1f9a26d7821e95d9ca7e236c804f442cacd2c610cc1edd0cab0  15259
    rso/slice001/receipt.py  sha256:f0f0d80063d21703b1709c188cad702b189db772bf5ecac404a04c9a56d5725b  31846
    rso/slice001/s2_bundle.py  sha256:036fabd6bc0b606c711d2a89560bd5c11a71ae79d02bf8654d750e5e6ce5fc07  16779
    ares/substrate.py  sha256:a48a6073b1cb778791e783800e527f3c7ab58c7ccfe343cfe231db3ca52c6611  23371
    ares/worlds.py  sha256:0cfa481ac800faf7bc7b7fb8ee4687cab0fd878ced24613553e0f4a15a916259  17421
    ares/search.py  sha256:6cd523cfda2c91f44faf83f85aaf8b4dd9fee3a126240a535145e72f97ca9f48  20706
    ares/carriers.py  sha256:c9c3b113267dc3c17404aa479b02aca2170119063d023e1cd5f34dce5b6d1dac  15963
