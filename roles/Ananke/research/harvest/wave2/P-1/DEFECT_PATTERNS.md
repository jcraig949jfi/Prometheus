# How C1's beliefs failed: recurring defect patterns (principal synthesis, Wave 2)

Source: Wave-1 harvest plus Wave-2 reports W2-A1, A2, B, C, D, E, F, G, H, I, K (deposited), and principal
checks P-1a..P-4. Each pattern has its instances, why it looked persuasive, the measurement that would
have caught it earlier, and the reusable instrument now available. The purpose is to make the next
campaign's freeze packet fail on these before data exists.

## Pattern 1: CONSTRUCTION MASQUERADING AS RESULT
The env, the placement or the scheduling decides an outcome, and the report presents it as an empirical
finding.

Instances:
- 43% of XOR searches light-cone-capped (E-W3).
- MAJ placement forces one hop and is reversed on directed graphs (E-W2).
- 77% of RELAY tasks only demanded one hop (E-W4).
- "Topology-bound" laws are hop-bound (E-W1).
- Size-free is forced for local laws (E-W8).
- 8/104 transects cannot yield a boundary.
- HOLD memory is clocked by the fixed distractor schedule (W2-E D1).

Why persuasive: the outcome matched a plausible mechanism story ("one-hop machinery", "lattice-bound
laws"), and the env code was trusted to implement DESIGN s7.

Earlier catch: before freeze, run the attainable-outcome census per cell (light cone, realized
placement distances, per-cell timing ceiling), and require the eligible count per family and condition.

Instruments:
- H-PLANT lightcone.py;
- W2-B attain.py (UNREACHABLE / DEGENERATE verdicts);
- W2-A1 invariant tests and the inert-dial canonicaliser;
- W2-I maj_direction_census;
- W2-P (pending) construction-capped NULL counts.

## Pattern 2: CONTROLS THAT CANNOT FAIL
Instances:
- zero_comm (exact .5 per pair), so COMM_DEPENDENT == SIGNAL and LOCAL_ONLY is unreachable.
- env_permutation (E = .5 for any program).
- max_loss == zero_comm.
- shuffle_dest on global is a routing re-draw.
- Twin-symmetric C1b predictors are exactly .5.
- 24/98 swap no-op arms forced NO_EFFECT_REL.
- The causal_label adjudication had no competence gate (W2-C F2).

Why persuasive: each control is semantically sensible ("cut communication"). Its forcing comes from
mirror-pair design details invisible at the claim level.

Earlier catch: the identity audit, i.e. does the control's value vary across programs, including null
and adversary programs? Plus a mutation gate in which the control's designated mutant must be KILLED-A on
a positive control.

Instruments:
- W2-F explib.controls (A1-A4 identity audit);
- W2-C pte_mut plus guards (s4 standing gate, item 3d "a control whose designated mutant is
  EQUIVALENT must be replaced");
- W2-B certifier forced/alias detection.

## Pattern 3: RULER AIMED BESIDE THE CLAIM (cheatable or blind rulers)
Instances:
- XOR SIGNAL vs parity (the NOR cheat scores .759).
- FLIP SIGNAL vs feedback (the clock cheat scores 1.000).
- Legacy REACH_BEYOND_HOP fired by one-hop emitters.
- lens.verify_reach "applied" is not reached.
- div_frac counts unused divergence (613162a3, the HOLD-global cluster).
- The absolute .62 "intact" bar measures the normal level, not the window effect (W2-K F5).
- Pooled accuracy blind to half-dead runs (W2-C F4).

Why persuasive: the ruler crosses for the intended mechanism, so it was validated on positives only.

Earlier catch: for every ruler, the best score of a program that LACKS the claimed property (W2-B's
property-free readout table), and a must-fail adversary.

Instruments:
- W2-B rulers (XOR_PIVOT, FLIP_FEEDBACK, REACH_BEYOND_HOP_NEAREST);
- W2-B's reach_certificate window patch (applied);
- explib.attainable (null / adversary / plant).

## Pattern 4: SELECTION AND TARGETED SAMPLING REPORTED AS RATES
Instances:
- The "RELAY 50/196" and "one hop 48/50" pooled targeted waves (17 distinct conditions; 32/50 from one
  lineage).
- 5/8 predictions "held", where most HELD ones were low-risk (P-4).
- A per-cell SIGNAL is one search draw (D replicates .857 -> .706; W2-H F9).
- AUDIT3 double-counts the site/channel arms, which are one measurement (W2-F F4).

Why persuasive: counts are exact and reproducible (W2-G: report.py reproduces), so the numbers felt
solid. The denominators were the problem.

Earlier catch: report the unbiased-wave rate (A1) next to every pooled count. Count independence units
(distinct conditions, lineages, search seeds), not rows. Attach a risk statement to every prediction.

Instruments:
- explib.stats (independence-unit declaration, count_check, Simpson guard);
- inference.py (BH/Holm, replication gate, reading3);
- W2-G rederive scripts.

## Pattern 5: A LOWER BOUND READ AS AN IMPOSSIBILITY ("physics-dead")
Instances:
- relay_flood failure at decay > 0 read as physics, but a 3-line refresh plant survives decay 3 exactly
  (P-2).
- The economy boundary is the budget identity of a flooding plant (W2-A1 F5).
- The "XOR/FLIP have no plant" claim: relay_flood partly solves FLIP (W2-D F6, W2-E N3), and P-FLIP and
  P-XOR exist (H-PLANT).
- Multi-hop "plant-dead" rows (P-1b).

Why persuasive: plant_viability was designed as the physics map ("separating physics-dead from
search-failed"), and one plant per family looked sufficient.

Earlier catch: bracket every cell with an UPPER bound (light cone, derived physics bound) as well as the
plant LOWER bound. A cell is "physics-dead" only when the upper bound is below threshold. Use at least 2
plant designs that differ in their failure modes (emission density, write policy).

Instruments: lightcone.py; H-PLANT plants plus P-2 relay_refresh; W2-D's R/S/U/P/V chain.

## Pattern 6: VOCABULARY AND PROVENANCE DRIFT
Instances:
- Transfers cited as search NULLs (fac4aaa2, ef77ef2e, 1b26026f), including in the principal's own
  review.
- Adjudicate ids used as champion names (17 NAMING).
- Transfer rows stamped REACH_BEYOND_HOP=False (fixed to None).
- The dest_mode record differs from what ran.
- "XOR single input = .500 exactly" is true only for sensor 2.
- "Every number recomputed by report.py" is false.

Why persuasive: the 8-hex id looks like a self-describing citation, and the reader never sees the kind.

Earlier catch: a kind audit on every deposit, and claim-support checks (explib.provenance.support_check).

Instruments: W2-I kind_audit.py; explib.provenance; W2-G claim ledger.

## Pattern 7: THE OBJECTIVE IS NOT THE TASK
Instances:
- The w_any bonus initiates the NULL sensitivity climb while accuracy is flat (P-3).
- The contrast bonus pays linear sub-noise codes the full .10 at chance (W2-A1 F4).
- Champions selected on 8 worlds below the selector ceiling (~.57; W2-D F7).
- Mis-tuned champions (62a7fff9 one tick off; W2-E N4).
- Rule-mosaic lottery champions (W2-E N1).

Why persuasive: "the champion" is read as the search's best mechanism, and MEMORY_WITHOUT_USE etc. as
properties of the substrate.

Earlier catch:
- log per-generation accuracy variance (when is selection blind?);
- report the bonus share of fitness;
- run a w = 0 control arm (not authorized in this harvest);
- run timing sweeps of champions.

Instruments: C1 curve fields (already recorded); W2-R (pending); W2-D selector-ceiling definition.

## Cross-pattern observation
Every pattern survived C1's preregistration and freeze. Preregistration fixed the INTERPRETATION of each
ruler and control. It did not certify that the ruler or control COULD discriminate. The Wave-2
instruments (certifier, mutation gate, explib, kind audit) all target that gap: certify the instrument
against nulls, adversaries and broken experiments BEFORE the freeze. That is the one process change
these patterns jointly recommend.
