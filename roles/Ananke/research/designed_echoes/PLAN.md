# Designed echoes as calibration: PLAN (committed with predictions.json BEFORE any engine run)

Purpose: positive controls for W-A's echo model AND for the instruments.
A hand-designed echo is NOT evidence of emergence.
Model: workers/W-A/echo_model.py (zero fitted parameters). Genomes:
design.genome(ph, k, route), a canonical echo with pipeline depth k. The
builder was checked bit-identical to W-A's canon (sanity only; no result).
Predictions: predictions.json, sha256
db6e1c76cb81085ce53fee82c3ebc3013c5417e53b78295cc1ffda7ad9dd3a17.
Engine: 64 worlds, ns 0x5F1, gaps 2..16, CPU 2 threads, 99% pair bootstrap.

Designs (physics = the M2 specimen's, plus overrides):
  E1  canon, plastic_route 0                   peak 7 (0.95)
  E1s canon + specimen routing                 lower edge raised: 6 -> ~7
  E2  pipeline 2 (state_dim 3)                 interval shifted +4: peak 11
  E3  pipeline 2 + lat_base 0                  partial cancellation; two peaks (7, 11)
  E4  pipeline 4 (state_dim 5)                 DESIGNED MISTIMING: chance at the
                                               trained gap 8 (predicted .50), peak 15
  E5  pipeline 1 + update_period 3             two peaks (7, 13): wake-parity comb
  E6  specimen routing + lat_hop 2             comb: peaks 11, 15; gap 13 dead

Decision rules (W-A's, unchanged):
  FIT per curve: MAE(model, engine) <= 0.07.
  INTERVAL-HOLDS: endpoints of the >= 0.65 interval within +-1 gap.
  MODEL SURVIVES CALIBRATION iff >= 6/7 curves FIT and INTERVAL-HOLDS.
  E4 must show engine acc at gap 8 hi99 <= 0.60 (a designed failure is a
  success of the model).

Instrument calibration (stage 'instruments', committed predictions):
  E2 at its best gap: at some lag in {-1, -2} before the readout,
  site_all FLIPs and channel_all is NO-EFFECT (the bit has moved into the
  pipeline registers). At some lag in {-6, -4}, channel_all or pay1 FLIPs
  (the bit is still in transit). -> a DESIGNED channel -> site HANDOFF, a
  positive control for trajectory measurement (W-I).
  E1 at its best gap: channel_all FLIPs at some lag in {-6, -4}; site_all
  does not FLIP at lag -6.
  cue_arrival_profile: E2's cue-bearing arrivals at the actuator come
  EARLIER relative to the readout than E1's (by ~ pipeline x period = 4
  ticks).
