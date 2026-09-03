# D15A_TRACKB_REPORT — generator/instrument redesign

Harmonia A · 2026-09-02 · Track B only (engine stays qualified at
5274ddbe; no engine battery re-run — no engine behavior was materially
exercised). Design of the scientific object in
D15A_REPAIR_EQUIVALENCE_V2.md; constructive generator + exhaustive
census in generator_v2.py.

## DUAL VERDICT (return for review; do NOT begin confirmatory D15-A)

    D15A_TRACKB_GENERATOR              = GENERATOR_NOT_READY (5/6 rungs)
    D15A_TRACKB_IDENTIFIABILITY_INSTRUMENT = INSTRUMENT_NOT_READY

    => SCIENCE stays NOT_READY. Confirmatory D15-A remains forbidden.

But this is a NARROW, well-diagnosed miss on top of a repaired core, not
the v1 collapse. The v1 failure (equivalence collapsed nothing; 37-142
classes; EQUIV rung absent) is FIXED and verified. What remains is one
non-constructible rung in a too-small substrate, with a precise remedy.

## What is now FIXED and exactly verified

- **E2 collapses operator multiplicity.** Goal-relevant equivalence
  (same reachable-target-subset + soundness bit) yields E1/E2 ratio
  median 3.0-5.0 across every rung: many extensionally-distinct
  operators, few meaningful repair classes. The v1 defect is gone.
- **EQUIV rung is real (I5).** median E1/E2 = 5.0, |V0|=1: many
  syntactic candidates, one meaningful class. Built by construction
  (variants agreeing with h on reach_h), verified exactly.
- **ZERO_INFO pole is real (I0).** zero_info_frac = 1.00: probing the
  ENTIRE observable universe does not shrink the version space;
  |V0|>1 forever. Distinguishing states are unobservable by construction.
- **IDENTIFIED pole is real (I5).** identified_frac = 1.00.
- **The active-information object is real and SHARP (I1).**
  active_advantage_frac = 1.00: in every I1 world, passive
  (navigation-reachable) probing CANNOT identify the repair
  (cost = infinite), while a single active teleport probe DOES
  (cost = 1). This is the strongest possible form of "actively chosen
  information disambiguates the repair" — stronger than the graded I2
  the design asked for.
- **No master-key** (max hidden-op frequency <= 0.15 after enlarging
  the operator family to 26 permutations).
- **Firewall + replay intact** (unchanged from Phase 0; no oracle token
  in the discovery pipeline; A3 replay bit-identical).

## What is NOT ready

- **I2 (graded middle: both passive and active identify, active with
  strictly fewer probes) is non-constructible in Z_6x Z_6.** In a
  36-state world, informative states are almost always already in the
  navigation reach, so passive and active costs are typically EQUAL
  (both 1). The strict per-world filter (active < passive, both finite)
  rejected all 12,000 candidate seeds. This is a substrate-size limit,
  not a logic error.
- Consequence: the ladder currently instantiates {I0, I1, I3, I4, I5}
  by exact construction, but the GRADED active-advantage rung is
  missing. The design's 6-rung ladder is not fully populated -> the
  frozen census criterion "reject if a rung disappears" fires ->
  NOT_READY, honestly.

## Remedy (for review — two clean options, not self-authorized)

R-A **Enlarge the substrate** to Z_8 x Z_8 (64 states) or Z_6^3 (216).
   A larger navigation/observable gap makes graded passive>active costs
   generic; I2 becomes constructible. Cost: census enumeration is still
   exact but ~2-6x slower; well within budget.
R-B **Rescope to a 5-rung ladder** where I1 (passive-impossible /
   active-trivial) IS the active-advantage rung. This is scientifically
   DEFENSIBLE and arguably stronger: the D15-A claim ("actively chosen
   information makes an underidentified failure identifiable") is
   sharpest when passive literally cannot do it. The graded I2 becomes
   a secondary/optional rung. This needs operator sign-off because it
   changes the preregistered ladder.
Recommendation: R-B for the confirmatory ladder (I1 is the cleaner
scientific contrast), with R-A pursued in parallel if the graded
gradient is wanted for the dose-response secondary.

## The 10 report questions

1. **What is a meaningful repair equivalence class now?** An E2 class:
   the pair (set of targets made reachable, soundness bit) from x0 under
   T + repair. Collapses all off-goal-region differences.
2. **E1-distinct / E2-equivalent examples?** The I5 EQUIV rung: 5
   operators per world agreeing with h on reach_h (so identical
   reachable-target-subset) but transposing states outside it -
   extensionally distinct, E2-identical. Verified E1/E2 = 5.0.
3. **All rungs constructively populated?** NO - 5 of 6 (I0,I1,I3,I4,I5
   at n=80 each, exactly verified). I2 not constructible in this
   substrate.
4. **Ladder survives exact census?** For the 5 populated rungs, YES
   (each world's defining property verified, not inferred). The 6-rung
   ladder as designed does NOT (I2 absent).
5. **Can legal probes change repair entropy?** YES - and it is the
   axis: I0 no probe helps; I1 only teleport probes help; I3/I4
   navigation probes help; I5 already resolved.
6. **Do probes differ in information value at matched cost?** YES -
   I1's passive vs active cost (inf vs 1) at identical per-probe cost
   is the exact demonstration.
7. **Information value separable from goal progress?** Partially
   demonstrated: I1's identifying probes are outside navigation reach
   (pure information, zero goal progress by construction). The full
   4-way factorial (info-only/goal-only/mixed/null) is only partially
   instantiated - info_only_exists came from the now-empty I2 metric
   and must be re-measured on the populated rungs (open item).
8. **Identifiability separable from search difficulty?** Structurally
   YES by construction (I0 and I5 can share reach-size/target-count
   while differing maximally in identifiability), but the explicit
   matched-difficulty stratification (report Q of the design, §10) is
   NOT yet measured across the populated rungs - open item for the
   READY resubmission.
9. **Universal repairs / marginal-prior shortcuts?** None: master-key
   <= 0.15; E2 classes per rung balanced by the enlarged family.
10. **Would an adversarial reviewer agree it measures identifiability,
    not operator multiplicity?** For the CORE claim, YES - E1/E2 = 3-5x
    proves multiplicity is collapsed and identifiability varies
    independently (I0 vs I5). For the FULL 6-rung graded ladder, NO -
    the graded middle and the matched-difficulty stratification are not
    yet delivered. Honest reviewer verdict: "the object is now correct
    and the poles are sharp; finish the middle and the difficulty
    control before running."

## Carried-forward engine limitations (unchanged, still declared)
ENG-1 (P2 depth>=2 fork id-nulling; content_hash recovers identity;
D15-A depth-1). ENG-2 (P3 inherited artifacts available-not-readable;
reconstruct from event ledger). ENG-3 (P3 client idem_key plumbing gap).

## Next action (not self-authorized past redesign)
Choose R-A or R-B (operator sign-off, since R-B changes the frozen
ladder). Re-run Track B: populate the chosen ladder, add the
info/goal/mixed/null probe factorial and the matched-difficulty
stratification (open items 7,8), re-census, and return READY/READY or
a further honest miss. No confirmatory execution until then.

## Artifacts
D15A_REPAIR_EQUIVALENCE_V2.md · generator_v2.py ·
D15A_GENERATOR_CENSUS_V2.json · D15A_IDENTIFIABILITY_LADDER_V2.json ·
D15A_PROBE_ORTHOGONALITY.json · D15A_SCIENCE_DEFECTS_TRACKB.jsonl ·
JOURNAL.jsonl.
