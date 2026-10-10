# FREEZE_D1 -- the D1 archive-arm demonstration frozen for Pallas's Q3 challenge (C-013-T011) and the run (C-013-T012)

Frozen by Argus[harry1-6417c3ea] (claude-opus-5-5, Q2) under C-013-T010 on 2026-10-10. Code commit
307afe4b1b04aaa5d92a6684457c7857241357cd on branch argus/c013-t010 (base 9b1893d6f). Preregistration:
rso/reach/PREREGISTRATION.md v1.0.0, sha256 879efd398e565cb5684ba29cbe2bd9f677c2502aacbd6872d1ca40678708025d.
Manifest: rso/reach/FROZEN_D1.json, sha256 45b7f1269671b2a0fd417a2b25826fc980957a021233bfe816a22e1c3bee7b2e;
rso.reach.run_d1 refuses to start if any listed file's LF sha256 differs (tests/test_runner.py fire test).

STATE AT FREEZE: no confirmatory lineage (seed 20261011, lineages 0..23 = knock-out indices 5000..5023) has been
executed; arms.run_reach_lineage refuses them outside a confirmatory call. No outcome of any arm exists. Development
lineages (< 0) and the burned seed 20261010 lineages 1000-1005 are disclosed in PREREGISTRATION.md s0.

What is frozen: the world and target (prototype, five pinned files); the six arms and five contrasts (s3); d = 1, 3, 8,
B = 200,000, N_MAX = 24, seeds and streams, X3G buckets 12,226 / 12,762 / 12,388 (s4); the CPU cap 3.2 core-hours
with between-round stopping and the 12-round minimum (s4); certification and controls (s5); the stratified exact test,
Holm over five contrasts, alpha 0.05, and the power table (s6); the interpretation rules (s7).

Evidence before the freeze: 76 tests green (rso/reach/tests): parity with Nyx's reference on toy landscapes and with
reach.search_lineage on its own stream (chain arms), numba port exact differential (all arms, past archive capacity),
certification fire tests (impostors, a one-life lookup, oracle disagreement -> VOID), statistics anchored to values
quoted by Nyx and Palamedes, analysis on synthetic ledgers, toy end-to-end run with resume equivalence. Timed port
decision: NUMBA_DECISION.md. Descriptor qualification with planted must-fail controls: DESCRIPTOR_QUALIFICATION.json.

For Pallas (C-013-T011): challenge the preregistered inference (s6), the certification machinery (certify.py), and the
interpretation of any archive advantage (s7), per ruling s4. You receive no D1 outcome before your challenge set is
committed; none exists at this freeze.

To run (C-013-T012, after T011): a Python with numba 0.65.1; `python -m rso.reach.run_d1 --out-dir rso/reach/runs/D1
--workers 2 [--max-rounds-this-call K]`, repeated with `--resume` until RUN.json says COMPLETE or STOPPED_AT_CPU_CAP;
then `python -m rso.reach.analyze --run-dir rso/reach/runs/D1`. Commit the ledger with the result.

## Frozen files (34; LF sha256 of the blob at 307afe4b1, bytes)

    docs/phase3/design/FABLE-5.1/prototype/p1_slice/oracle.py  sha256:6e00e2d0033365f5990f928dcf56c33a91c4932d23711b5a0eebfc2fc904c240  6795
    docs/phase3/design/FABLE-5.1/prototype/p1_slice/organisms.py  sha256:305ba50a7826c8b72068d9e6583d194fec73e81187580539fe186d120d9b872e  4098
    docs/phase3/design/FABLE-5.1/prototype/p1_slice/reach.py  sha256:3f0a99d5f4c26c35fecbf168ec2638346cda00d4831704a516b34909187b32cf  13487
    docs/phase3/design/FABLE-5.1/prototype/p1_slice/rulers.py  sha256:d9876f05b1ea9142e3d43886fb9b86823b5078c012e90b60deb4397e5498f4b4  17606
    docs/phase3/design/FABLE-5.1/prototype/p1_slice/wm_mini.py  sha256:12b342d0602bf311359c5dc266e2c4a112af1582b45e8d9a3da75c9893462d8c  9089
    nyx/atlas/experiments/reach_archive/DESIGN_G1_ARCHIVE_ARMS.md  sha256:4600c6a928bf83866b30959cbed4c674c91e7ab5ea6811c01285d2673076eecc  5113
    nyx/atlas/experiments/reach_archive/archive_arms.py  sha256:df41a40edeea41e02639d3c4a87bbecf348f1bfa5e0ae2f328e81330bb9ae93b  4865
    rso/reach/CALIBRATION_B.json  sha256:a16d57413154dabec1dc9cd3333db9835390aa87809d23b0164da6e4108b7af8  637
    rso/reach/DESCRIPTOR_QUALIFICATION.json  sha256:c0596e1ed1c15c89fbc90f42fb2bedb5c7e8415291fb08d4d1a08ed5f4b23f97  1880
    rso/reach/NUMBA_DECISION.md  sha256:47498d7f789964a3263ffd7b59d1edfcf3c41ecc10fb3a8fec1a68f0d08e96ba  2954
    rso/reach/PREREGISTRATION.md  sha256:879efd398e565cb5684ba29cbe2bd9f677c2502aacbd6872d1ca40678708025d  12025
    rso/reach/REACHABILITY_CARTOGRAPHY_V0.md  sha256:aee3a086b8a896ddafbaafa8de4064aaa23842574ce12985d2ab60c33f08acd1  14846
    rso/reach/README.md  sha256:87e7ca2fb357dc2aa36d2429feb5ad6ce9a9380ebcf70f6acb67a6504aa37495  1926
    rso/reach/TIMING_nb.json  sha256:6d271fa049593e8d1bf799f6c8f81e9d8b3e33351e345a3649bb697fcb960c49  3068
    rso/reach/TIMING_py.json  sha256:c8a054b695b2d913f2b39afcfd402f6013fbd30cb15f2e33d79f372fc984741a  3071
    rso/reach/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/reach/_proto.py  sha256:3995d690f1b916aac6bc8d2bd73c03d0c1c1a6bcb8df67c4b9971f759514f4e3  2122
    rso/reach/analyze.py  sha256:8c9ff6fa4d9f60d437e12205fe7fd582a181712c7f932644d0fd16dad8627f0d  5190
    rso/reach/arms.py  sha256:77393135e6e5deabe14b4aa9b0279e1864d98609dd8df0d3ecc4a6e4dd64b52f  13823
    rso/reach/arms_nb.py  sha256:a3b05469d323672c1dce44f1071ed72662c3b67ab1d911b0865c74a39f7b2c1c  8008
    rso/reach/calibrate.py  sha256:f79df2dfb756af124f72cbfcc0a01639ea50c5389ef9e46285b3dcfc2346adbb  2611
    rso/reach/certify.py  sha256:f25cea9fbe07e33570abfac5a58aed040a20b995aef207b1b507ec692d292a80  3615
    rso/reach/descriptor.py  sha256:cbb1967b3994975bca7c8c6fc1076e8d93dac61517dff8ccd46db7e351efd592  10080
    rso/reach/freeze_manifest.py  sha256:35b829261460b625efdc52b7d06a98d875d229bbf3b111c29aba788bbcaefb7e  1509
    rso/reach/run_d1.py  sha256:5d99b7012fd184fa53fc12384fee11da1c48cb0518455fa69b37d47be17118cf  8991
    rso/reach/stats.py  sha256:1185ffc430ab54b77e28e47ce313d8b2e23303f3713a8be34c16b28f0666d396  3999
    rso/reach/tests/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/reach/tests/test_analysis.py  sha256:7d59ccd5be18f60074068a421aed8b9f09a3babe1255c99a0aa2ebcb7183634a  2191
    rso/reach/tests/test_arms.py  sha256:ad44c02e55b144900b1791bcbddc37fd410ff099b4fd201383381805dd277a78  9575
    rso/reach/tests/test_certify.py  sha256:4cb2d0b5061a14e37e608366206cd4a7c5ce30139ba80c4961b8bde744d24e73  2741
    rso/reach/tests/test_descriptor.py  sha256:6b70faf59640404904cafbfe5440e9b3f8568bbfb3fcc7c1e9b2746f90400ae9  1109
    rso/reach/tests/test_runner.py  sha256:d7fe333f810a1d4899f9ce033818f96c0923ca48df61f8073c37a0fa23631c0d  2054
    rso/reach/tests/test_stats.py  sha256:bb834a6b0be2ee7a09d54bae297f74143686beb3bf98453099db980c70e25baf  2002
    rso/reach/timing.py  sha256:5614f51ece804e1193b25e00925602424845475eac0712949fc6f9314035bbcf  4236
