# FREEZE_W1 -- C-010 witness machinery frozen for the independent challenge (C-010-T014)

Frozen by Palamedes[harry1-679179c6] under C-010-T013 at 2026-10-07T10:34:12Z. Code commit 98345e104cf8bf2a55298b5726d9c6dd45e76f38. Preregistration:
rso/witness/PREREGISTRATION.md (sha256 099f408f6e7c1c3e6c1e3b885a2db42f58efd5a0a941a7d8e23205ab623bc1f7), unchanged.
Integrated: C-010-T010 (Cadmus, node executions + artifact bytes), T011 (Eupalamus, artifact storage), T012 (Argus,
evaluator); T013 (Palamedes): config generator (s3 seed procedure), the S-NOPL/P-RET pairing fix, the per-launch
bundle inventory (C-010-T012_1 option 2), WITNESS_SEEDS.json, and an end-to-end dry run on tiny random subjects
(rso/witness/dry_run.py: 3 launches, 16 receipts bound, P-FLAT PASS, custody QUALIFIED on a fixture store, every gate
evaluated; outcome values of the stand-ins not printed). Witness suite 133 OK, binding 21 OK.

The witness path under challenge: rso/witness/ares_client.py (node executions), run_witness.py (subject runs,
launches, artifact storage, per-launch inventory, seed refusals), make_configs.py (seed procedure, configs),
evaluate.py (P-FLAT, binding, custody, artifact re-hash, oracle recomputation, gates, classes), ruler.py.
No registered subject has been run; no witness episode exists.

## Witness files (22)

    rso/witness/CANDIDATES.md  sha256:e0a2019bffd7359de58cfa7d063c168cf4e11c7a188fc1f8d84ded4ad4c80b4c  8886
    rso/witness/DESIGN_DRAFT.md  sha256:3ca211fb0898fa2854b41ac35c0295eaab487437042f3efb61490bb9b1c3a39a  6380
    rso/witness/ERASE_PROBES.md  sha256:297f2caf60aec08ae901ce224539d414bc78819e71710cf1d7506bab33f38a18  3533
    rso/witness/PREREGISTRATION.md  sha256:099f408f6e7c1c3e6c1e3b885a2db42f58efd5a0a941a7d8e23205ab623bc1f7  9578
    rso/witness/PREREG_DRAFT.md  sha256:8a46e6f3838d8c7c66a85b62eec85a3dff4d3ec023df46c5293281c580ef368a  7341
    rso/witness/RULER.md  sha256:a60c85222a3885dd29b9adfaf22b312ee2c16b66b5699b89f6b53b42b4ea607b  8360
    rso/witness/SELECTION.md  sha256:a76f72b0f0cad7bdc730e435d6a932d8ce448972b9d2e45c94fba84fd3fd9198  2096
    rso/witness/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/witness/ares_client.py  sha256:cf1bab2101ff811246c6268417fcd462f041ad28ef37b72c1b65f5646778cb54  18796
    rso/witness/contract.json  sha256:cd59ba6b872cab28b857fc49802310ad3e6fa3f4de78d826e797061d2a05216e  901
    rso/witness/dry_run.py  sha256:49ada4e489c053114c3d9238bb3ec1cb87c715a9a39a8918df3a5bc6a62f3dd2  4395
    rso/witness/evaluate.py  sha256:fd1ddf6bfe5fca31163129ff75bd2eed7405e4cf871a820e1ecf95e6f1f00665  19633
    rso/witness/make_configs.py  sha256:e18c1a7062001d254d414de0f44ad3ebe3b76509e373070de5d2e5d78054fb3e  3982
    rso/witness/ruler.py  sha256:6b972f9eef3127dc80f66bacfa26d61097304e74f486523ad1c65d7cd31caed8  13833
    rso/witness/run_witness.py  sha256:4ca20878ba1988c13ee53d8b2c3351097cb28ea90a8fddad6f50ec907dec1b92  23248
    rso/witness/tests/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/witness/tests/test_ares_client.py  sha256:f4ff66ae302b4a7e586ed6b91def9742b83a04dabe649d46cdc0583902a61034  19506
    rso/witness/tests/test_evaluate.py  sha256:9bfddb3b2b4df189e087d18496298c84d1a860c76e7d0d87f9a6f222ef83f4b8  19342
    rso/witness/tests/test_launch_inventory.py  sha256:76307ae690b71e28de504430d315bf9d4140f1986bf5dfcc68f5dd99332f8618  2250
    rso/witness/tests/test_make_configs.py  sha256:cf1629cade4e2807edc28f26250019d5d1e06fdbc5395082e87c5d24c965b7ff  4680
    rso/witness/tests/test_ruler.py  sha256:e75e2f12104cbcbbf9122174894ed012b9f135355762113163f65398e5e2ef82  13534
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
