# C-004 S4 regression rerun (C-004-T045)

Palamedes, 2026-10-06. Repaired code (S4 repair round: T042 Argus, T043 Cadmus; contract v1.0.4) at 6463d8b61.
Produce: five bundles (G0, EXTRA, HEAL, FLAT, LOSSY), launches 9-13 of 20 (OP-7 repair window), committed at
0e1943bff before any consume. Consume: first check after Aporia registered the 3 regenerated stage records (G-BIND,
G-INV, G-RECOMP) with their fire receipts and the S4 G0 manifest + inventory; live registry chain verified
(41 rows, head 216829137ae611ea2704f2a6adb381377b7ffa2599c411d790053d314aaf834f).

## 1. Against the independent table (the S2 regression)

    48 registered, 45 gating: AGREE 32, PARTIAL 8, DISAGREE 8 -- identical to the S2 run (s2/MATRIX.txt).
    The 8 disagreements are exactly the OP-5 dispositions (X02, X06 x3, X18 x3, X19 x3 cells over 8 cases);
    no new disagreement. Rows: MATRIX.json, MATRIX.txt in this directory.

## 2. Against the S2 run, every claim of every bundle

One difference, the predicted one:

    EXTRA  CL-RET(HCOUNT)  G-RECOMP  S2: FAIL OUTCOME_MISMATCH:value  ->  S4: PASS "recomputed equal"

This is S3 finding F1 (the bound clamp trace restored into a fresh instance while the CHANNEL outcome clamped the
same instance), predicted by the reviewer for HCOUNT in S3 REPORT.md and invisible to the S2 matrix because the
table has no cell for that line. Every eligibility and standing of every claim of all five bundles is unchanged;
S4 has no G-RECOMP FAIL anywhere.

## 3. S3 attack cases on the repaired code

Replayed at T042 integration with the reviewer's committed driver and answer key (throwaway ledger, development):
sound 5/5, broken 5/5, controls 2/2 (S3 first sight: 4/5, 3/5, 2/2). S3 survivor edits E01, E02 (T043) and E07,
E09, E10 (T042), applied verbatim to the repaired code: all killed. The first-sight scores themselves are preserved
unchanged in challenge/S3/REPORT.md; these are post-repair figures, reported separately (plan s5).

## 4. Observation O-S4-1 (for S5)

The slice ledger is cumulative, so each bundle's terminal RUN_INVENTORY lists every earlier attempted run, including
S2 runs of the same node ids. In E02.MISSING on the S4 base, the removed receipt's node has two COMPLETED rows (S2
and S4) and G-INV's RUN_UNREPORTED names the first (the S2 run id). The verdict is right; the reason cites the
earliest unreported run. A per-window inventory would cite the S4 run; the contract does not say which.

## 5. Caps after S4 regression

Launches 13 of 20 (S2/S3 window: 8 of the original 12; repair window so far: 5). Ledgered CPU 2465.6 s
(41.1 min) of the 80 ledgered minutes (OP-4 accounting). Artifacts 31.8 MB of 100 MB. Remaining for the S4
closure set (T041): 7 launches, about 39 ledgered CPU-minutes.
