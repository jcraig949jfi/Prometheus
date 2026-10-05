# V2-B TEST-3 -- does a recoil x exchange interaction make the Aether medium endogenously mobile?

Thread: TH-P2B-AETHER-V2B, cycle 3 (TH-009 axis). Frozen at the end of DEV-3 and pushed BEFORE any TEST-3 unit runs.
Rungs: P1 (ENDOGENOUSLY MOBILE), primary; P3 (content carried), descriptive only (see the shortcut declaration).

## Question
TEST-2 measured every current medium as FROZEN or COUNTER. DEV-3 built a bounded enumeration over three binary
mechanism switches on the v1 shared path (laws mob_r?x?e?):
- recoil (r): a winning write turns its emitter's direction by the byte it displaced. Mechanism class: data-dependent
  reorientation. Shortcut attack: with a constant displaced byte it is a counter or short cycle, which the ruler
  catches.
- exchange (x): a winning write hands the displaced byte back to the emitter's payload. Mechanism class: conservative
  two-way value movement. Shortcut attack: a fixed swap partner cycles, which the ruler catches. **Exchange encodes one-hop
  value movement by construction, so P3 content readings under x-laws are NOT discoveries** (cf. fwd).
- energy aim (e): direction follows energy, as in str. Shortcut attack: TEST-2 showed str alone is FROZEN.

Corners mob_r0x0e0 and mob_r0x0e1 equal v1 and str bit for bit (tested) and are not re-run (TEST-2 classified them).
Question: is P1 mobility produced by the recoil x exchange INTERACTION, and by neither switch alone?

## Apparatus (pinned)
- Code: c0284fcae1f7ec23ea1fc932733c041a724bda19.
  - Physics: aeth03_variants.py adds the mob family; existing laws are unchanged and 97 tests are green, including
    the corner identities and the exchange, recoil and precedence fixtures.
  - Observatories: aeth_prov.py (prov0 now models the mob side effects; per-tick self-check) and aeth_mobility.py
    (frozen P1 ruler from TEST-2, plus a warm-up-arm option).
- World: as TEST-2 (n=128, warm-up 1500, followed window 400 ticks, arm OFF).
- P1 arms: mob_r0x1e0, mob_r0x1e1, mob_r1x0e0, mob_r1x0e1, mob_r1x1e0 and mob_r1x1e1 (warm-up ON, as TEST-2), plus the
  review-Q4 control: v1 with warm-up OFF. Seeds 4-7. 28 units.
- P3 arms (descriptive): aeth_prov_assay for mob_r1x1e0 and mob_r1x1e1, seeds 4-7, 64 origins each. 8 units.
- DEV pilot: seed 100 only, used to choose this design. On seed 100: x-only CYCLING, r-only COUNTER, r1x1 (both e)
  ENDOGENOUSLY_MOBILE, v1 warm-up-OFF FROZEN.

## Rules (fixed now)
P1 class per unit: aeth_mobility.P1_RULE, unchanged from TEST-2. Per law: the class held on at least 3 of 4 seeds,
otherwise MIXED.

**Primary (P1 interaction claim):**
- INTERACTION_MOBILITY_SUPPORTED -> MECHANISM_SUPPORTED iff BOTH mob_r1x1e0 and mob_r1x1e1 are ENDOGENOUSLY_MOBILE AND
  none of the four single-switch laws (mob_r0x1e*, mob_r1x0e*) is ENDOGENOUSLY_MOBILE.
- MOBILITY_WITHOUT_INTERACTION -> PARTIAL iff some single-switch law is ENDOGENOUSLY_MOBILE. Mobility exists, but it
  is not an interaction.
- NO_EFFECT iff neither r1x1 law is ENDOGENOUSLY_MOBILE.
- PARTIAL otherwise (exactly one r1x1 law mobile, and no single switch mobile).

**Secondary (review Q4):** v1 with warm-up OFF classified FROZEN -> "the noisy warm-up is not what freezes v1"
SUPPORTED; any other class -> NOT SUPPORTED.

**Descriptive (P3, with the shortcut caveat):** P3_far, P4, P5 and P6 shares for the r1x1 laws vs TEST-1's v1 / rcv /
fwd. Reported only; no claim of content transport is admissible from x-laws.

Technical failures (an exception including ProvenanceMismatch; a missing unit; a hash mismatch) are rerun up to 3 times
unchanged.

## Limits declared in advance
- One regime (B-balanced) and one 400-tick window.
- The P1 ruler's known blind spots: varying-step counters, and causal dependence (not tested).
- ENDOGENOUSLY_MOBILE here means "sustained, non-cyclic, non-constant-step, spread-out turnover", not yet "causally
  structured". A causal-dependence check (twin divergence in turnover patterns) is the next ruler refinement if this
  test is positive.

## Execution
Fabric if live numpy workers exist; otherwise MWO-0004 R3 native fallback on BUCKKEEP (pinned worktree, lease
buckkeep:cpu8, waves of 3). About 50-60 s per unit.
