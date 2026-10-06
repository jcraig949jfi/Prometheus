+==============================================================================+
| REVIEW PACKET -- AETH-V2B-AIM02: is the re-aim medium richer than matched     |
| flicker, on fields the re-aim law never touches?                             |
| Author: Aether (role seat), host SPECTREX5 / M2, RTX 5060 Ti 16 GB           |
| Date: 2026-10-06                                                             |
| For: HITL operator + external reviewers                                      |
| Status: COMPLETE. Frozen disposition RICHNESS_WEAK; repertoire is            |
|         flicker-equivalent (reading: REAIM_MOBILE_BUT_TRIVIAL)               |
| Self-contained: no repo access needed; every load-bearing number is inline.  |
+==============================================================================+

-----
0. SUMMARY
-----
AIM01 showed that letting a winning writer advance its own direction (reaim1)
opens much more of the Aether lattice to change. AIM01's "nontrivial dynamics"
verdict, however, rested on an instrument artifact. AIM02 re-asks only that
question, on opcode/arg1/payload (never arg0), activity-matched against real
high-flicker controls.

Answer: no richer in state repertoire.
 - A changing site-field under reaim1 holds 2 values in 88-96% of cases over
   2000 ticks, even with 256+ changes. Mean distinct values 2.04-2.13 vs 2.01
   for flicker.
 - Late-half discovery of new values is 0.0000. A 4000-tick window adds no new
   value at all.
 - L1's novelty excess at 16-tick memory (+0.10) shrinks to +0.0025 at 64
   ticks, at all 3 densities, 8/8 seeds.
 - Only return timing differs: median 4 vs 2 ticks, p90 16 vs 4-5.
The frozen rule says RICHNESS_WEAK (N16 and the return-time ratio are material,
N64 is not). In substance: re-aim spreads two-state flicker over a larger area,
with slower timing.

-----
1. BUILT AND FROZEN BEFORE PRODUCTION
-----
 - Integration first: AIM01 merged to main (9bffb1f7c) with ER01/AIM01 frozen
   files verified byte-for-byte; fresh branch.
 - Instrument (pure measurement). Fields opcode/arg1/payload on a 256x256 grid
   (196,608 site-field columns per unit), 2000-tick late window. Per changing
   column:
    * distinct values U; unique/change; distinct transitions/change;
    * N16 and N64 novelty;
    * late-half discovery rate;
    * return gaps.
   Columns are binned by change count; comparators are weighted by the
   treatment's bin mix.
 - Known answers 8/8, including:
    * arbitrary arg0/energy changes give exactly 0;
    * a 32-period revisit gives N16 > 0.95 and N64 < 0.05;
    * POSITIVE CONTROL through the frozen decision function: an expanding
      catalogue gives RICHNESS_SUPPORTED; flicker vs flicker gives
      FLICKER_EQUIVALENT.
 - Conformance: L0/L1 bit-identical to AIM01; comparators bit-identical to ER01
   free-compute / rich-rain; CPU == GPU including the analysis.
 - Rules (frozen 619dd3b25). Five families, each must beat BOTH comparators in
   >= 7/8 seeds:
     n64 +0.05, unique/change +0.05, late discovery +0.05,
     transitions/change +0.05, return-time ratio 1.5x.
   SUPPORTED = n64 plus one more family at 2 of 3 densities.
   WEAK = anything material, or n16 only.
 - DISCLOSURE: qualification numbers (identical in pattern to production) were
   seen before the margins were fixed. The margins were chosen for meaning, and
   two clauses were known to fire (N16, return ratio).

-----
2. RESULTS (production: 8 conditions x 8 seeds + duplicate = 65 units, 512^2 x 6000 ticks)
-----
                    L1D25  L1D50  L1D75  FREE   RICH   L0D25  L0D50  L0D75
  changing cols     .011   .030   .048   .0034  .0030  .0008  .0030  .0059
  U==2 share        .961   .919   .882   .986   .984   .993   .983   .973
  U>=4 share        .0007  .0030  .0075  .0002  .0002  0      .0002  .0007
  mean U            2.040  2.084  2.126  2.014  2.016  2.007  2.017  2.028
  N16               .109   .112   .115   .001   .002   .083   .086   .088
  N64               .0044  .0058  .0070  .0009  .0011  .0031  .0035  .0039
  return p10/50/90  2/4/16 2/4/16 2/4/16 2/2/4  2/2/5  2/3/14 2/3/14 2/3/14
 - Activity-matched L1 minus comparators (both, all densities, 8/8 seeds):
   N16 +0.097..+0.101; N64 +0.0024..+0.0026; unique/change +0.0022;
   transitions +0.0046..+0.0049; discovery 0.0000; return ratio 2.0x.
 - L1 minus same-density L0: N16 +0.02, N64 +0.0008, return 1.33x.
 - Gates pass: one table hash, duplicate identical, 65/65 rc=0, coverage
   0.90-0.94.

-----
3. POST-HOC LOCALIZATION (not preregistered; descriptive)
-----
Seed 0, last 500 ticks: distinct WINNING writers and offered values per
changing target-field. L1D50: writers 2.06-2.11, offered = held = 2.05-2.10
(<= 2 in 90-95%). L0D50 / free compute: ~1.95 writers, 2.01 values.
=> The repertoire bound sits upstream of aim. Each target is fed by about 2
writers with near-fixed payloads, each writing only its own field. Re-aim
changes WHERE a writer points, not WHAT arrives.

-----
4. WHAT THIS ESTABLISHES / DOES NOT
-----
ESTABLISHES (P0, B_balanced for L1, 512^2):
 - The re-aim medium is not richer than flicker in state repertoire,
   transition diversity, or late discovery.
 - AIM01's ~0.10 non-AIM novelty is revisitation just beyond a 16-tick memory.
 - Fixed aim explains WHERE the medium can change (AIM01), not how richly.
DOES NOT:
 - Show that a timing-matched comparator would also call the return-time
   difference trivial. The comparators flicker unusually regularly.
 - Cover multi-field joint states (each field is ~2-valued, so the joint
   catalogue is bounded by ~8).
 - Cover any other energy economy or perturbation setting for L1.

-----
5. RECOMMENDATION (HITL's call)
-----
Close the richness question for reaim1 as REAIM_MOBILE_BUT_TRIVIAL. Do not run
the content experiment: there is no rich medium to carry content. Do not speed
up re-aim or rotate arg1: either can at most give K <= 4 flicker among
fixed-payload neighbours.

Next (one): OFFER01. Keep reaim1. Add one rule: a winning writer's payload
becomes the byte it displaced (offer/displaced swap). This targets the measured
bound (fixed offers).
 - Prediction if it works: offers > 2, U growing with the window, late
   discovery > 0, N64 material.
 - Preregistered falsifier: period-2 swap shuttling (U ~2-3, N64 ~0).
 - Must distinguish itself from V2-B TEST-3's exchange family (classed
   CYCLING under another ruler).

-----
6. QUESTIONS FOR THE REVIEWER (try to disagree)
-----
 Q1. The comparators flicker with period 2, but B_balanced worlds flicker
     slowly. Should the frozen rule have used L0 at matched density as the
     primary comparator? It would likely give FLICKER_EQUIVALENT rather than
     WEAK.
 Q2. Is a single-field repertoire the right richness unit, or could
     structured joint dynamics across fields be rich while each field stays
     2-valued?
 Q3. Is "held = offered" tautological under P0 (no perturbation creates
     values)? If so, does the offer probe add anything beyond counting
     writers?
 Q4. Is the OFFER01 swap rule a single-axis change, or does it import a relay
     (like the killed rcv) that would pass richness for the wrong reason?
 Q5. Has the frozen-medium programme reached the point where a copy-only,
     radius-1, P0 law is known to be bounded, and should be retired rather
     than patched rule by rule?

-----
7. ARTIFACTS
-----
Branch aether/aim02-2026-10-06; freeze 619dd3b25; main 9bffb1f7c.
 - Order: roles/Aether/prompts/2026-10-06_aim02/
 - Aether/V2B/AIM02/:
    * RESULT.md, PREREGISTRATION.md, RULES.json
    * production/ (65 units, REDUCTION.json, posthoc_offer_*.json)
    * qual/
    * aim02_run.py, aim02_meter.py, aim02_reduce.py, aim02_conformance.py,
      posthoc_offer_probe.py
 - Fixtures: Aether/test/test_aim02_meter.py

+==============================================================================+
| END. "Patching rules one at a time will not get a copy-only radius-1 medium  |
| to richness; retire the line" is a first-class answer. Say so if you think   |
| it.                                                                          |
+==============================================================================+
