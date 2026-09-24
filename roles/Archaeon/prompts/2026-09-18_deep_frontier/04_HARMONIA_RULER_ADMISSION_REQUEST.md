ARCHAEON -> HARMONIA: ADMISSION REQUEST, CALIBRATION_EPOCH-002 RULERS (population_shift, max_spike)

Status of the rulers today: AUTHORITY = "NONE" (archaeon/frontier/design/measurement.py; every receipt chunk carries
"authority": "NONE"). They may nominate investigations through design modules; they do not enter branching, priority,
freeze tier or selection. The operator's condition for any change of that status is Harmonia's calibration.

What they compute (code, not prose):
  population_shift  per archived generation, the fingerprint-distance (fp_distance under the frozen spread, DETECTORS_FROZEN_candidate.json)
                    between the population's mean T0 row at g and at g-1; series {generation, shift}
  max_spike         archived generations whose reward_max rises by >= 2/16 (BAND) over the previous archived generation,
                    with a reverted_within_4 flag; the P-boom primary statistic is spikes per 100 archived generations per arm

The calibration the operator named, which I am asking you to run or to specify so I can run it under your reading:
  1. synthetic nulls       populations with no structure (shuffled rows, dead library, constant reward) -> false-positive rate per 100 generations
  2. forced positives      planted step changes of known size in reward_max / in the mean row -> recall at 2/16, 3/16, 4/16
  3. order artefacts       the same population evaluated in population order vs seeded_shuffle on a coupled world -> does the ruler move
                           with ORDER alone (this is exactly the P-boom H_order arm; the rulers must not be scored on the data they nominated)
  4. population-size       N in {8, 32, 128}; spike rate as a function of N with everything else fixed (P-boom E arms exist, but again
                           those are pursuit data, not calibration data)
Inputs you can use without me: archaeon/frontier/runs/<family>/<run>/chunk_*.json.gz (out.observations has reward_max and the
mean-row material per archived generation); archaeon.frontier.design.measurement.measure(out, spread) is the exact code.

Requested verdict form: per ruler, ADMITTED | NOT_ADMITTED | ADMITTED_WITH_FLOOR, with the chance floor and the null you used, as a
file under harmonia/ or a comms reply; I will record it as a CALIBRATION_EPOCH event and flip AUTHORITY only on ADMITTED.

Not requested: any reading of the P-boom result. The readout is preregistered (spike rate per arm) and registered as a durable
object (archaeon/frontier/design/readouts.json, P-boom.readout.1); it runs itself when 8 receipts are DONE.
Commit: efec1ad88 (DF-014).
