# Designed echoes: RESULT

Plan and predictions committed before any engine run (4c4ca8dea;
predictions sha256 db6e1c76...). Engine: 64 worlds, ns 0x5F1, CPU 2 threads.
Outputs: engine.json, instruments.json, run.log.

## Model calibration: 7/7 FIT (the model SURVIVES)
  design                 MAE    >=.65 interval pred -> engine
  E1 canon               .018   4-10 -> 4-11
  E1s + specimen route   .023   6-11 -> 6-11  (routing raises the lower edge, as designed)
  E2 pipeline 2          .015   8-14 -> 7-14  (+4 shift; peak 11: 0.96)
  E3 pipeline 2 + lb0    .015   6-12 -> 6-12  (partial cancellation, two lobes)
  E4 pipeline 4          .012   12-16 -> 12-16 (DESIGNED FAILURE at the trained gap 8:
                                               0.53, hi99 0.59 <= .60 as required; peak 15: 0.96)
  E5 pipeline 1 + up3    .021   7-15 -> 7-15  (wake-parity comb: peaks 7 and 13)
  E6 route + lat_hop 2   .018   10-16 -> 10-16 (comb: 11 and 15 alive, 13 dead)
The zero-parameter echo model designs working mechanisms, deliberate
failures, and comb-shaped intervals to within MAE <= .023. This is
calibration, NOT emergence: every specimen is hand-built.

## Instrument calibration on DESIGNED trajectories: 2/3 predictions held
- E1 (gap 7): the channel carries the bit at lags -4/-3 (channel_all and
  pay1 FLIP); site_all at -6 does not FLIP (CHANCE). HELD. At lag -1 the
  bit is in S0 (site FLIP, channel NO-EFFECT), after the last wake.
- Arrival profile: E2's cue-bearing arrivals at the actuator sit at lags
  -9..-2 vs E1's -5..+2, about 4 ticks earlier, as predicted. HELD.
- E2 (gap 11): predicted "in transit at lag -6 or -4". FAILED: at -4..-1
  the bit is already in the pipeline registers (site FLIP, channel
  NO-EFFECT at every lag -4..-1). At -6 BOTH site and channel are
  CHANCE. My timing assumption was wrong: the echo lands earlier, and
  the handoff falls between -6 and -4.
What the failure teaches: on a mechanism whose trajectory is KNOWN by
construction (channel -> S2 -> S1 -> S0), the swap instrument returns
CHANCE/CHANCE exactly at the handoff tick. This is W-F's "JOINT = phase
mixture" signature (instrument F5') reproduced on a designed positive
control. It confirms that CHANCE/CHANCE at a single tick is a HANDOFF
reading, not a joint code, and that designed pipelines are good
trajectory fixtures for W-I-style measurement.

## Next
T-REDISCOVER (backlog Tier 3): now justified. The model designs; does
search rediscover pipeline-depth or routing-filter solutions when the
task demands gaps outside the native kernel (e.g. gap 14, which needs
pipeline >= 2 at base physics)? This is a GPU search; queue it behind the
current leases.
