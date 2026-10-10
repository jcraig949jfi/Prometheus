# FREEZE_D1 v1.0.1 -- the D1 archive-arm demonstration re-frozen after the one repair round (C-013-T013)

Re-frozen by Argus[harry1-91546d7d] (claude-opus-5-5, Q2) under C-013-T013 on 2026-10-10. Code commit
b85d690bfb6519b9e9807862509e260712bc60e3 on branch Argus/C-013-T013 (base 187ebe447). Preregistration:
rso/reach/PREREGISTRATION.md v1.0.1, sha256 4e3c10a0dba4dd9757e52467281082315bea57837b578d5d79af7bb10597bc0d
(v1.0.0 + wording-only amendment A1, s9). Manifest: rso/reach/FROZEN_D1.json, sha256
cdd5de75f7799a5f43855bccb1fd5d3f1b1a1ed97799b2f731ef7e7e2c4023a5; rso.reach.run_d1 refuses to start if any listed file's LF sha256 differs
(tests/test_runner.py fire test). Supersedes FREEZE_D1 v1.0.0 (code 307afe4b1, freeze 66c7ccdae, PREREGISTRATION sha256
879efd39, manifest sha256 45b7f126), which Pallas challenged under C-013-T011 (rso/reach/challenge/D1/REPORT.md).

STATE AT RE-FREEZE: no confirmatory lineage (seed 20261011, lineages 0..23 = knock-out indices 5000..5023) has been
executed; no rso/reach/runs/ directory exists. No outcome of any arm exists. Development lineages run by the challenge
are disclosed in REPORT.md s6 item 5; the repair round ran none (its tests use synthetic ledgers, a synthetic prior
ledger with the toy controls, and fixed programs on the certification lives).

WHAT CHANGED FROM v1.0.0. Of the 34 files frozen at v1.0.0, exactly one changed: PREREGISTRATION.md (amendment A1,
wording only: s4 outcome-symmetric stopping; s5 selection band 2000..2063 named, the sealed ruler restated as the
reporting block; s7 rows pooled over d with a per-stratum caveat, C2 / C4 / C5 / last row narrowed, the stepping-stone
row withdrawn as inferential). Every other v1.0.0 file is byte-identical, so nothing the run executes changed and no
s2-s6 number changed: arms, seeds, budgets, B_d (12,226 / 12,762 / 12,388), the stratified exact test, Holm over five
contrasts, alpha 0.05, the power table, the 3.2 core-hour cap, the 12-round minimum, certification and controls.
Fourteen files are newly pinned: the challenge set (rso/reach/challenge/), the repair round's RED runner and edits
(rso/reach/repair_v101/; its red_rows.jsonl is evidence, not pinned) and tests/test_repair_v101.py.

NEW BEHAVIOURAL PINS (A1.5). Four lines that only the hash manifest held at v1.0.0 now have tests, each RED on its
mutant applied verbatim (rso/reach/repair_v101/red_rows.jsonl): E1 certify.py:52 selection on the selection lives
(mutant reads [126, 126] for the target instead of [500, 500]); E3 analyze.py:93 Holm decides (mutant separates C2 at
raw p 0.039, Holm 0.196); E4 run_d1.py:141 --resume counts prior CPU (mutant ignores an over-cap ledger and runs on);
M80 certify.py:54 the 90% threshold (builder(7), 449/500 = 89.8%, certifies under the 80% mutant).

Evidence at the re-freeze: 80 tests green in the venv C:/Prometheus-worktrees/argus-reach-venv (numba 0.65.1, pytest
8.3.3): the 76 frozen tests plus the 4 pins (receipt ops/campaigns/C-013/tasks/C-013-T013/attempts/A-001/RECEIPT.json).

To run (C-013-T012): unchanged from v1.0.0. A Python with numba 0.65.1; `python -m rso.reach.run_d1 --out-dir
rso/reach/runs/D1 --workers 2 [--max-rounds-this-call K]`, repeated with `--resume` until RUN.json says COMPLETE or
STOPPED_AT_CPU_CAP; then `python -m rso.reach.analyze --run-dir rso/reach/runs/D1`; read the result under s7 as
amended by A1 (print the per-(arm, d) counts beside every separating contrast, A1.3). Commit the ledger with the result.

## Frozen files (48; LF sha256 of the blob at b85d690bf, bytes)

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
    rso/reach/PREREGISTRATION.md  sha256:4e3c10a0dba4dd9757e52467281082315bea57837b578d5d79af7bb10597bc0d  18654
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
    rso/reach/challenge/D1/CHALLENGE_SET.md  sha256:4b4b84f408677507ac063119f3c0536b9f765b59e4c27b6329ea20b53add861d  13464
    rso/reach/challenge/D1/EXPOSURE.md  sha256:8f2e0d8fcb9637312943e875d411abff948b4188a57337b430bf8e90a78aa538  3013
    rso/reach/challenge/D1/REPORT.md  sha256:8e816ce9ea76617e4614c28d601a55c6bd3e0b57c054e9d91f36509afb1079a8  19294
    rso/reach/challenge/D1/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/reach/challenge/D1/cases_d1.py  sha256:910a42f122b7a5f4012fed5e41a6d367f50c0297549ac4c1360a4bb7e25767b8  23195
    rso/reach/challenge/D1/edits.json  sha256:39be2733607face36ccb4ce6e3050a3544f04322098e136423d00399c7d7af4f  2335
    rso/reach/challenge/D1/expected.json  sha256:2354efcb49d07c3fb1c0cf00d7eba68fe8db8c7fd45dcf93f661432123f87d17  4936
    rso/reach/challenge/D1/posthoc_p4.json  sha256:129a2ff91e6994d89a8575bda45093a3cb1aed96eb596b7f56a3a5f2485a8c3b  568
    rso/reach/challenge/D1/run_edits.py  sha256:19991e258926e8c2ea9d68b154f04198af245a5c9346ea8b1bc5a1b25c4c171e  5415
    rso/reach/challenge/D1/witnesses.py  sha256:f1a31cc6fcf565e24ab8341a5a6420e3fec0f1890de92d24ab1de47d83b9eca5  3613
    rso/reach/challenge/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/reach/descriptor.py  sha256:cbb1967b3994975bca7c8c6fc1076e8d93dac61517dff8ccd46db7e351efd592  10080
    rso/reach/freeze_manifest.py  sha256:35b829261460b625efdc52b7d06a98d875d229bbf3b111c29aba788bbcaefb7e  1509
    rso/reach/repair_v101/RED_EDITS.json  sha256:08eb8880d632c3d8babf252033ae901b3f4e3e16573391808b2831d711b59fde  1908
    rso/reach/repair_v101/run_red.py  sha256:5e6bac7ae470d69e94d3788d05e3837fba06089ab234f0758a029cb6e6db0540  2763
    rso/reach/run_d1.py  sha256:5d99b7012fd184fa53fc12384fee11da1c48cb0518455fa69b37d47be17118cf  8991
    rso/reach/stats.py  sha256:1185ffc430ab54b77e28e47ce313d8b2e23303f3713a8be34c16b28f0666d396  3999
    rso/reach/tests/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/reach/tests/test_analysis.py  sha256:7d59ccd5be18f60074068a421aed8b9f09a3babe1255c99a0aa2ebcb7183634a  2191
    rso/reach/tests/test_arms.py  sha256:ad44c02e55b144900b1791bcbddc37fd410ff099b4fd201383381805dd277a78  9575
    rso/reach/tests/test_certify.py  sha256:4cb2d0b5061a14e37e608366206cd4a7c5ce30139ba80c4961b8bde744d24e73  2741
    rso/reach/tests/test_descriptor.py  sha256:6b70faf59640404904cafbfe5440e9b3f8568bbfb3fcc7c1e9b2746f90400ae9  1109
    rso/reach/tests/test_repair_v101.py  sha256:4d03c375b3295be83bdcc4c879f2cd7e9ad07c0dd8d2c8e0c63b84ae06e7c938  5035
    rso/reach/tests/test_runner.py  sha256:d7fe333f810a1d4899f9ce033818f96c0923ca48df61f8073c37a0fa23631c0d  2054
    rso/reach/tests/test_stats.py  sha256:bb834a6b0be2ee7a09d54bae297f74143686beb3bf98453099db980c70e25baf  2002
    rso/reach/timing.py  sha256:5614f51ece804e1193b25e00925602424845475eac0712949fc6f9314035bbcf  4236
