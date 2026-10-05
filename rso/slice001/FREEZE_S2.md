# FREEZE_S2 -- C-004 S2 implementation and tests frozen for the S3 first-sight challenge

Frozen by Palamedes[harry1-679179c6] under C-004-T020 at 2026-10-04T18:37:13Z.
Code commit: b220c7e39ed544351b14da2bf51e912a2c845cf5 (the S2 produce ran at 6379cd3a6; no rso/slice001 source changed between them except
the T020 driver/engine and their tests, which no instrument imports).

Contract: v1.0.3 (rso/slice001/contract/). Expected table: rso/slice001/expected/EXPECTED_ANSWERS.json (3ea4af125).
Run evidence: rso/slice001/s2/ (PRODUCE.json, LEDGER.jsonl, five bundles, MATRIX.json/.txt, CLASSIFICATION.md).
Custody: G0 EVIDENCE_MANIFEST + RUN_INVENTORY + 12 canonical STAGE_RECORD + EXPECTED_ANSWER_TABLE registered;
registry chain verified at 18:35Z (33 rows, head 4315fe5b3ad38e1030f6726ff26f67a372157c005ea99eda09db48426ec05a68).

S3 rule (plan s5): the reviewer commits attack edits BEFORE opening any file under '## Test files' below;
the hashes here let anyone check that the frozen bodies were not changed afterwards.

## Implementation files (24)

    rso/slice001/__init__.py  sha256:53d2299b9d0b1828dffab43feb1090fa9570db202ff3aae2dc31241f94f1cb64  82
    rso/slice001/adapter.py  sha256:d71ee0319e54fef90c817f343426d50e74fde252369bc5ecd5f9d3265bfc7db3  9701
    rso/slice001/checker.py  sha256:40d9fe95018925f8eb412c7b31a74f648b18f3e8931f337913e697198a966c87  24261
    rso/slice001/ci.py  sha256:6d44df69599bc82f41312594fb3271b4229daf767916ce47225c3e3b7f3fc2a7  5987
    rso/slice001/encoding.py  sha256:7833f4a1e12e2900fe0b664d76ef7db4682b153ef235d24a1fcc11c31a814df4  7480
    rso/slice001/evidence.py  sha256:06ef526b5e346f1cf749f5c85535e2f90cdaf8bb59c8db775003c7b57d9423a0  30721
    rso/slice001/expected/_build_expected.py  sha256:f904c2579b123517802ee9690d405b854f94e4059d5277140b9ef2a1534bb74c  41632
    rso/slice001/fixtures/evidence_cases.py  sha256:06ce290e9c1fe89334bc35659b1085bdec71f745dffe9c77fbe909b71c78a5d5  25503
    rso/slice001/fixtures/world_cases.py  sha256:ccb89ec7347440374e09a3340194e7ef6c441349b2dd7b000c8dd11c4da0a711  11849
    rso/slice001/ledger.py  sha256:d103f7abc92ea65f2d777fce8d3fed1de7b18a97ca4684cb4a62746f32832990  13763
    rso/slice001/matrix.py  sha256:c78f82569f2fea96eae2cd9d7e6d121b1b0911ef6b56737775e45b1be4757887  10351
    rso/slice001/mutation.py  sha256:ce90dd4b61f5d6ceca270961de4e91b44af708a698b6caf92f6dbd40563a215b  21232
    rso/slice001/observer.py  sha256:96c2f578725387b50dc21fbd93bb1e460c5695093f889777d8aecd81a4c8e44f  3827
    rso/slice001/receipt.py  sha256:f0f0d80063d21703b1709c188cad702b189db772bf5ecac404a04c9a56d5725b  31846
    rso/slice001/render.py  sha256:bead561ad9af3e111417daf00a0d5730e9ba5037c5daf7325431d4b38b49c573  9553
    rso/slice001/reset.py  sha256:72d31f94a077fad3b29a71182a0258db2b9d2bd44cf492f16b4dddc502de6521  11283
    rso/slice001/rulers.py  sha256:bbc78fa75bd4896ce9425a460169b985130cecf4a7b365f7766e2b231d217a99  5904
    rso/slice001/s2_bundle.py  sha256:4326a7ce586569cb1ddc488ddb443c0453dfb897db812d90838c3a46baf303c6  15842
    rso/slice001/s2_run.py  sha256:7e2b42894d5324ffcdb681d01db9559b6ae2904a466d5271decbd62d2fd33efc  18331
    rso/slice001/stages/__init__.py  sha256:be397c23603c189d19bae4ea0578ed2e728d600d91b85f315a8a5e928ce14d5a  199
    rso/slice001/stages/evidence_plane.py  sha256:e5878b272f3221aa4ec8494b409edad21a77256b87595a7eef84c21e61f9c879  11711
    rso/slice001/stages/fire_world.py  sha256:7b0ffa62a08d5d989796c521bca1e74845c58f90897447584cbb4a5f4282fe7d  10159
    rso/slice001/stages/version.py  sha256:5e1007b952b53da9ce22c457e426ce6ebcb5a94554c34adc49108872fcf40880  3401
    rso/slice001/world.py  sha256:0336919b73f9de4005963e6393d98bdf4f7eee24be37902cf246e797c7275d25  13730

## Test files (17) -- do not open before committing the S3 attack set

    rso/slice001/tests/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/slice001/tests/test_adapter.py  sha256:6c90ef3b3c0c431d1b2289605809fcff01954795c57b9057b9023dcc35af985c  13104
    rso/slice001/tests/test_checker_render.py  sha256:e0815576ac4a8373779a164c1795a3bfe13c990115d36910d2d87de6466169e4  34114
    rso/slice001/tests/test_ci.py  sha256:ec172228d7c2211e32065b6cf220e7ca804c53e66c99081849885371f06cb06c  4648
    rso/slice001/tests/test_encoding.py  sha256:256dbb94cf562618a28235f58f9b1ad4f2fcc3b6e02eaeaf6d2e53a0d81cbb56  3492
    rso/slice001/tests/test_evidence.py  sha256:e395a256669311e8d365defbc3fb07fbd2ba8b8ff1058b77fd25fc5119f64545  31611
    rso/slice001/tests/test_ledger.py  sha256:19f1b67e3dea97337e6005f0dc0b7bac819b79b1184bbd766182886e53c9a4f7  20771
    rso/slice001/tests/test_matrix_engine.py  sha256:aafdcaf2c1520a75e12b90cf751be3424e0a1cdcd7a8752215558c56a55f5dfb  8304
    rso/slice001/tests/test_mutation.py  sha256:cc19613b17199998c75967b75c7f50767cd01ba5d41acb7cf584789ecd336800  10819
    rso/slice001/tests/test_receipt.py  sha256:d72f5b6a00e6d68ccf86d29f4f8949033ef7cb263d44933ce67b89e82d7d458f  24583
    rso/slice001/tests/test_reset_observer.py  sha256:19134219b8534fa8f9f73eabf582fee2e7001dc64e0fc93d3e79a167ec5077f6  16051
    rso/slice001/tests/test_rulers.py  sha256:0194fdba2f111e9eec2077adcfb389e60b1ce34fbe713e973664be09b0be1108  9421
    rso/slice001/tests/test_s2_bundle.py  sha256:9b972c95f501645fc67401f478898609eca650da4fef1dd7c590f868d732f27c  16647
    rso/slice001/tests/test_s2_run.py  sha256:fda018e91fcf083c9eb5d73ac512a7914edc6eb567a031eb47b5c795fea40b8c  2052
    rso/slice001/tests/test_stages_evidence.py  sha256:b109bc0a60a76c2eda76f52c3a2d4cbfd7719f1c62e3cb7fc469920603f0528c  6322
    rso/slice001/tests/test_stages_world.py  sha256:095c2e01f4d2d4de4fab4600a03826caceca01f0483264e145be4a36151ea183  6472
    rso/slice001/tests/test_world.py  sha256:292d8b2a48a688ce9bdb72607ad02e95c34569b37bae869812d8c44c0fcbcc7a  12838
