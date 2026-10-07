# FREEZE_B2 -- C-009 repaired binding surface frozen for the CC3 re-check (C-009-T034)

Frozen by Palamedes[harry1-679179c6] under C-009-T033 at 2026-10-07T06:41:21Z. Code commit 1b69dd04a59e7f30baddc1fdc90049c3a8506cfa (repair round C-009-T031 Argus + integrator pin; rso/binding v1.1.0, BX5b).
Repair regression: rso/binding/R1/R2CHECK/REGRESSION.md (as predicted). FREEZE_S2, FREEZE_S4, FREEZE_R2 and FREEZE_B1
are preserved unchanged.

The binding path under challenge (CONTRACT.md s2, s6): rso/binding/binding.py; evidence.py g_inv / launch_unbound /
custody (BX1, BX2, BX5, BX7); the producer side ledger.py + s2_bundle.py (parent_run_id, receipt_sha256, manifest
launch_run_id). Not part of this surface: rso/witness/ (native witness preparation).

Re-check rule (CC3, the only one): 1 fresh sound, 1 fresh broken, 1 semantic edit on BX1 / BX2 / BX5-BX5b,
committed BEFORE any outcome; not the CC1 or B1 shapes (regressions now). Changed since FREEZE_B1 (committed-byte hashes): rso/slice001/evidence.py, rso/slice001/s2_run.py, rso/slice001/stages/evidence_plane.py, rso/binding/binding.py, rso/binding/CONTRACT.md, rso/binding/contract.json, rso/slice001/tests/test_evidence.py, rso/slice001/tests/test_s2_run.py, rso/binding/tests/test_binding.py.

## Implementation, contract and fixture files (29)

    rso/slice001/__init__.py  sha256:53d2299b9d0b1828dffab43feb1090fa9570db202ff3aae2dc31241f94f1cb64  82
    rso/slice001/adapter.py  sha256:d3ffb4b30d09e6048ce165141052b96603a951c6864454a126b8d89745f9aea6  10084
    rso/slice001/checker.py  sha256:6c3d2124ac29a44cd9a539ba33149a82b8e2964d15a1f52d3c721401c02882c7  24390
    rso/slice001/ci.py  sha256:6d44df69599bc82f41312594fb3271b4229daf767916ce47225c3e3b7f3fc2a7  5987
    rso/slice001/encoding.py  sha256:7833f4a1e12e2900fe0b664d76ef7db4682b153ef235d24a1fcc11c31a814df4  7480
    rso/slice001/evidence.py  sha256:bd4e7bbf338bf30e1b4a2fa5bf68ed2b76db93a669a05d27a63584c6faeb2866  38969
    rso/slice001/expected/_build_expected.py  sha256:f904c2579b123517802ee9690d405b854f94e4059d5277140b9ef2a1534bb74c  41632
    rso/slice001/fixtures/evidence_cases.py  sha256:0b61e0736f49f758f08c597bc5b6f3d85080bcd132bb872c945888630bfa1c2c  30458
    rso/slice001/fixtures/world_cases.py  sha256:ccb89ec7347440374e09a3340194e7ef6c441349b2dd7b000c8dd11c4da0a711  11849
    rso/slice001/ledger.py  sha256:9c61a8940993c1f9a26d7821e95d9ca7e236c804f442cacd2c610cc1edd0cab0  15259
    rso/slice001/matrix.py  sha256:c78f82569f2fea96eae2cd9d7e6d121b1b0911ef6b56737775e45b1be4757887  10351
    rso/slice001/mutation.py  sha256:ce90dd4b61f5d6ceca270961de4e91b44af708a698b6caf92f6dbd40563a215b  21232
    rso/slice001/observer.py  sha256:96c2f578725387b50dc21fbd93bb1e460c5695093f889777d8aecd81a4c8e44f  3827
    rso/slice001/receipt.py  sha256:f0f0d80063d21703b1709c188cad702b189db772bf5ecac404a04c9a56d5725b  31846
    rso/slice001/render.py  sha256:bead561ad9af3e111417daf00a0d5730e9ba5037c5daf7325431d4b38b49c573  9553
    rso/slice001/reset.py  sha256:72d31f94a077fad3b29a71182a0258db2b9d2bd44cf492f16b4dddc502de6521  11283
    rso/slice001/rulers.py  sha256:bbc78fa75bd4896ce9425a460169b985130cecf4a7b365f7766e2b231d217a99  5904
    rso/slice001/s2_bundle.py  sha256:036fabd6bc0b606c711d2a89560bd5c11a71ae79d02bf8654d750e5e6ce5fc07  16779
    rso/slice001/s2_run.py  sha256:4f067ed2ddeea79527ed5a94b938668410bd79abfdf5959589aa92a4c7f0040c  18896
    rso/slice001/stages/__init__.py  sha256:be397c23603c189d19bae4ea0578ed2e728d600d91b85f315a8a5e928ce14d5a  199
    rso/slice001/stages/evidence_plane.py  sha256:0a8b45562c88665e7acd44fc71ca225bcf80e9a79e62f2581c6a8d8fca98702a  16354
    rso/slice001/stages/fire_world.py  sha256:7b0ffa62a08d5d989796c521bca1e74845c58f90897447584cbb4a5f4282fe7d  10159
    rso/slice001/stages/version.py  sha256:e633958e48a3c11581a996e6e20e6bfc45eda0cd781c3434a05c6ed126594048  3663
    rso/slice001/world.py  sha256:0336919b73f9de4005963e6393d98bdf4f7eee24be37902cf246e797c7275d25  13730
    rso/slice001/fixtures/cc1_cases.py  sha256:28d31685235b969484ad569adfd27956941a827ea029c0922f6897bfbe38628c  17882
    rso/binding/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/binding/binding.py  sha256:a5a7af0477253b4ff91b1f4ac639c9ba1229891c6633719f54dc0301e593923a  5306
    rso/binding/CONTRACT.md  sha256:08ba85a459fa6fb3160e923bebee48687420bd3f22a037bc99cc3ed06864371c  7145
    rso/binding/contract.json  sha256:b122aae4499f1d83abbcaac2166fb5514d55ceffd006ea2b28885c5e5707f6c7  1520

## Test files (19)

    rso/slice001/tests/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/slice001/tests/test_adapter.py  sha256:966990a6fc6bb40a2c9478ba7a9bd484b6187f574ee5e5dd8ef6fe91f10606fe  14889
    rso/slice001/tests/test_checker_render.py  sha256:ba464353f325a827bef4f6be517bb72d2199231a7e17f312a518c982be50f2d3  35245
    rso/slice001/tests/test_ci.py  sha256:ec172228d7c2211e32065b6cf220e7ca804c53e66c99081849885371f06cb06c  4648
    rso/slice001/tests/test_encoding.py  sha256:256dbb94cf562618a28235f58f9b1ad4f2fcc3b6e02eaeaf6d2e53a0d81cbb56  3492
    rso/slice001/tests/test_evidence.py  sha256:73f80b90c1ca9c6166ed53d0e945275051ae4bb562575298fcc3b5c963548308  63721
    rso/slice001/tests/test_ledger.py  sha256:bcce20b274921d965b4c82bb21a4498029a8c5759fd37866682e80736cf6d1a1  24763
    rso/slice001/tests/test_matrix_engine.py  sha256:aafdcaf2c1520a75e12b90cf751be3424e0a1cdcd7a8752215558c56a55f5dfb  8304
    rso/slice001/tests/test_mutation.py  sha256:cc19613b17199998c75967b75c7f50767cd01ba5d41acb7cf584789ecd336800  10819
    rso/slice001/tests/test_receipt.py  sha256:d72f5b6a00e6d68ccf86d29f4f8949033ef7cb263d44933ce67b89e82d7d458f  24583
    rso/slice001/tests/test_reset_observer.py  sha256:b63f115ea0e49220a04d378edcf756c20529673fcdb6eee1c564ccc87b3e5e3c  19588
    rso/slice001/tests/test_rulers.py  sha256:0194fdba2f111e9eec2077adcfb389e60b1ce34fbe713e973664be09b0be1108  9421
    rso/slice001/tests/test_s2_bundle.py  sha256:c00ab82f97948c8aadf1aebee7032e5d7651ec93e1d5a126cc726636ad98c170  18795
    rso/slice001/tests/test_s2_run.py  sha256:13a517e4b4e2103510b6a7ddb8f17839359e4beea0ef12c91002a514de7211fd  4158
    rso/slice001/tests/test_stages_evidence.py  sha256:986ceb0e1ed6f86fee11414af25dbb31b124fba19959aefc7bf1907f57941758  6434
    rso/slice001/tests/test_stages_world.py  sha256:d40700a6bfa79bb018e33497859b1e35c6841357196fcc4db6d64aee68e77e74  6824
    rso/slice001/tests/test_world.py  sha256:292d8b2a48a688ce9bdb72607ad02e95c34569b37bae869812d8c44c0fcbcc7a  12838
    rso/binding/tests/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/binding/tests/test_binding.py  sha256:4f428e5ee9e298d95212684926b04d67958e1cca86383191b1fdf3ec11738c53  6923
