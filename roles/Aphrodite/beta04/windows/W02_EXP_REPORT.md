# W02 (EXP) REPORT: E1 PRODUCTION DECISION; E2/E3-KP PREREG, RED TEAM, E2 FREEZE

C-015, 2026-10-10 13:27-17:27Z.

## E1 production (foundry v2, 8d16a3288; 12 secret seeds; Addendum D strict)
**Result: WORLD_DEMAND_QUALIFIED = NO (WORLD_DEMAND_NOT_QUALIFIED).** Recorded as is (comms #2077).
- **Per-world gate:** 5 / 12 worlds pass.
- **Mechanism pairings:** 2 (fp, fs) < 3.
- **Admitted:** R2 38, R3 8, R4 7, R5 0.

The 15 admitted R3 / R4 families are demand-genuine:
- hindsight regression 0 / 53;
- from-scratch 0 at 1e6.

The dominant loss is R1 stepping stones that base search cannot reach (112 R3 CHAIN_C_FAIL). E4 is barred on these
worlds.

## E3 runner smoke (exposed pilot_v2; development data)
- Known positive 3 / 7. The failing stone is under-determined (x > 3 vs x > 4).
- A library forms only at B = 2e5.

## E2 / E3-KP pre-registration
The draft was followed by a red team: **5 BLOCKER / 13 MAJOR.** Fixed before any data.

**Amendment A1:**
- **E2 library:** foundry-acquired primitives, plus a no-library desert reference.
- **Credit control:** `credit="none"` as the true credit-blind arm.
- **FRONTIER_ARCHIVE_EFFECT:** X3 vs X3G vs chain_neutral; 5 skeleton clusters as the units; INCONCLUSIVE_CENSORED rule.
- **Primary endpoint:** the first dev-consistent program.
- **Escalation:** only on hits (Hestia's rule).
- **E3-KP:** a pooled verdict; the FAIL prediction written down in advance; first-failing-link classes; secondaries
  (fallback-off, given foundry primitives, extra seeds, all-acquired library); OE pruning pre-registered as the single
  neutral repair.

**Amendment A2:** the driver's conservative readings are frozen, along with a pre-data power statement. The 5-cluster
design has 80% power only for large effects; at D1-like hit rates power is about 0.15.

**FREEZE_E2.json** is written (26 file hashes; the 15 screen and 38 atlas family IDs).

## Leads
- **ATLAS** delivered the E2 driver, analyzer, projection and prelaunch (2bfeeda16; tests 13 / 13 + 14 / 14). Two
  fixes to existing code:
  - an O(n) restart-selection speedup, bit-identical in decisions;
  - the certifier's task tribunal now uses value-or-FAIL agreement. Without it, sealed witnesses were rejected.
- **SUBSTRATE:** KP alignment in progress.

**Projection for the E2 1x screen:**
- 8.6 core-h if 0 / 15 families qualify on D-BEH;
- 25.6 core-h if 15 / 15 qualify, which triggers truncation step 1.

## Coordination
- Palamedes #2079 (C-013 D1): NOTHING SEPARATES, under-powered.
- Their hardening note was adopted: the analyzer re-derives every endpoint.

## Compute
About 19 core-h since activation (estimate: leads, production, smoke, red teams).

## Next (W03)
1. E2 prelaunch and D-BEH qualification on production (outcome-free).
2. Atlas mode.
3. The 1x screen within the cap.
4. Freeze and run E3-KP after the SUBSTRATE lead returns.
