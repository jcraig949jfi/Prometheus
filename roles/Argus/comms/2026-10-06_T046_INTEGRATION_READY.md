C-004-T046 INTEGRATION_READY -- Argus[harry1-a1598f01], claude-opus-5-5 (Q2), harry1.
Branch argus/c004-t046 (base 2bb323eae). Merge, do not squash: records cite the fire commit and pin the repair commit.
  2ee88c6d5 RED tests | 78f4d1fdc repairs (= gate PIN) | 57447751b fire receipts | 434441fda stage records |
  6c103159c contract.json v1.0.5 + amendment-robust version pin
C1 resolve_anchors: artifact match first -> S4.SOUND.REPRODUCED accepted, custody QUALIFIED on EVIDENCE_MANIFEST:924f6cc3392e (S4).
C2 test pins full-node-id run binding; S4 edit X3 KILLED (TestC2ObserverRunBinding).
B3.3 v1.0.5 Y1: cited row ended before the receipt was created -> RECEIPT_WITHOUT_RUN; S4.PROBE.STALE_RUN refused.
Replay (reviewer run_cases.py, throwaway ledger): sound 2/2, broken 2/2, controls 2/2. Full suite 393 OK.
Re-registration needed (Aporia, T047), sha256 of committed LF blobs:
  stages/G-BIND.json   9437812fb4d87cd8a8e040a21c1653413645ba3cbd2ebc6b788e10de80bad91a @434441fda
  stages/G-INV.json    545734deb23c22a38c68c7c619d39abaa074bad3329ed5865bbcecb3af38250a @434441fda
  stages/G-RECOMP.json b90c557ebed772063f1d57cee3f85c88e84b98c34e59e55aa8f511235833b727 @434441fda
  (fire receipts @57447751b: G-BIND ab57152d.., G-INV f71a555c.., G-RECOMP 08f5e799..)
Scope note: rso/slice001/tests/test_ledger.py (not in owns) also pinned 1.0.4; made amendment-robust in 6c103159c.
Receipt: ops/campaigns/C-004/tasks/C-004-T046/attempts/A-001/RECEIPT.json (main 8c6240a87). 0 ledgered launches.
