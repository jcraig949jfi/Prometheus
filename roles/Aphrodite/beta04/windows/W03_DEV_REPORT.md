# W03 REPORT: E3-KP, KP SECONDARIES, E3-ID; E2 ATLAS + SCREEN UNDER WAY

C-015, 2026-10-10 17:27-21:27Z. The W02 close was committed early, at 17:07Z; W03 work began then.

## E2 (FREEZE_E2; A1 + A2)
- **Prelaunch on PRODUCTION: PASS.** Certifier recheck of witnesses + routes, start-at-target, constant / lookup
  control, target blindness, restoration.
- **D-BEH qualification** (outcome-free): 5 / 15 families, in 2 / 5 clusters (fp:map_of_filter 4, fs:scan_of_map 1).
  - **FRONTIER_ARCHIVE_EFFECT = INCONCLUSIVE (INCONCLUSIVE_CENSORED)**, determined BEFORE any screen outcome (ledger
    17:24Z).
- **Atlas mode:** 53 / 53 families measured.
- **1x screen:** 720 shards at 2 workers, no truncation (projected 14.3 core-h). 445 / 720 done at 21:29Z; running
  ahead of projection.

## E3-KP (FREEZE_E3KP; A1-A + A1-C + A3) -- TFS1_INSTRUMENT_QUALIFIED = NO
**Primary:**
- chain-qualified 7 / 15 (bar 12);
- scratch fails 15 / 15;
- first failing links: UNDERDETERMINED_STONE 7, HORIZON_R1 1.

The OE repair was not triggered (horizons are not a strict majority). **TFS1_REACHABILITY_INSTRUMENT = FAIL.**
This is not a rejection of compositional learning.

**The pre-data prediction was wrong in mechanism:** horizon-dominated was predicted; underdetermination-dominated
was observed.

**Secondary rows** (descriptive; scratch fails 15 / 15 in every row):

| Row | Chain-qualified |
|---|---|
| fallback-off | 0 / 15 |
| given-foundry-primitives | **14 / 15** |
| all-acquired | 7 / 15 |
| seed 1 | 9 / 15 |
| seed 2 | 8 / 15 |

A1-C: fallback-off agrees with the primary (NO).

## E3-ID (NEW prereg E3ID_PREREG + ID-A1; FREEZE_E3ID)
- **ID_IDENTIFIABILITY:** all 4 units behind the 7 UNDERDETERMINED_STONE families are **UNIQUE_WRONG.**
  - At 1e6, TFS-1 enumeration on the R1 family finds exactly one dev-consistent program, and it is not the sealed
    mechanism.
  - 3 / 4 also pass the R1 test + tribunal; they diverge only on the wider domain the composite uses.
- **ID_RETENTION_REPAIR = NO:** RETAIN-4 7 / 15. The CERT secondary gives 9 / 15; both agree.
- The code's interpretation string "INSTRUMENT" is superseded by frozen ID-A1.4. INSTRUMENT cases: 0.
- **Reading:** the first demonstrated failure in the causal chain is **stepping-stone identifiability at the
  world / ruler level**. Composition is reachable given true stones (14 / 15). The archive question is censored by
  descriptor qualification.

## Other
- **Phase-3 wind-tunnel interface:** proposal draft v0 committed. It proposes IDENTIFIABILITY as a qualification
  question, a descriptor gate before archive arms, and the first-failing-link report format.
- **ALIEN reserve AR-1** (a stack-tape machine with a mutation chain; non-lambda):
  - built and piloted: pilot 0 / 7 chain-qualified, scratch fails 7 / 7, links UNDERDETERMINED_STONE 4 / HORIZON_R1 3;
  - production addendum frozen (FREEZE_ALIEN_AR1; primary only; exploratory; confounded representation + search);
  - production running (1 worker).
- **Comms:** #2087 (KP), #2096 (E3-ID). Palamedes #2079 / #2035 closed.
- **Process:** Ledger utc stamps at 18:40Z / 18:55Z were estimates a few minutes ahead; commit times are
  authoritative. FREEZE_E3ID utc was corrected.
- **Compute:** about 30 core-h since activation (estimate). M4 has stayed at <= 4 workers.

## Next (W04)
1. E2 screen -> e2_analyze.
2. ALIEN review + frozen addendum + production.
3. Independent adversarial review of results.
4. Synthesis preparation.
