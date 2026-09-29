# PTE instrument: temporal reach (cue-arrival profile)

Status: PTE instrument, tested (test_lens_instruments.py: known answers
on the delay == delta relay plant, plus an undefined-reach control). NOT a
fleet rule. Code: prometheus/ananke/lens.py (cue_arrival_profile, reach).

CAUSAL QUESTION
"Could this time-windowed intervention have intersected the cue-bearing
causal traffic at all?" This is asked BEFORE reading a windowed null.
Single-cue twins (worlds identical except for one trial's cue sign)
reveal, tick by tick, when a cue-bearing delivery reaches the actuator.
reach(window) = the fraction of those arrivals, from cue onset to the
readout inclusive, that fall inside the window.

OUTPUT
profile = {lags: {lag relative to readout: #pairs with a differing
delivery}, cue_onset_lag, pairs}. reach(profile, lags) in [0, 1], or None
when no cue-bearing arrival exists (reach undefined, NOT zero).

SUGGESTED READING (a PTE convention, not a rule)
  reach < 0.5 for a windowed ablation null -> read it as
  WINDOW_UNREACHABLE, not as NOT_SUPPORTED.

CONTROLS (known answers, passing)
  relay_flood with delay == delta: C1 window reach 0.0, corrected 1.0.
  hold_latch (sends nothing): reach None.

REAL SPECIMENS (S-F, 2026-09-27)
  M3 0a23398f, f6b623cd: C1 window reach 0.00 (100% at lag 0).
  RELAY D cells: 0.69-1.00; MAJ D cells 0.93; M2 0.80 (arrivals at -2..0).

KNOWN FAILURE MODES
  F1 ACTUATOR-ONLY: it measures deliveries to the readout site. A
     mechanism whose causal event is elsewhere (a relay upstream) needs a
     per-site profile. The engine exposes that, but it is not packaged.
  F2 ONE TRIAL: the profile uses one trial (default 5). Carryover-heavy
     mechanisms can differ across trials; profile several.
  F3 DIFFERENCE != CAUSE: a differing delivery is cue-DEPENDENT, not
     necessarily cue-USED. Reach bounds what an ablation could hit; it does
     not say the hit mattered.
  F4 SITE-STATE PATHWAYS: reach says nothing about ablations of site state
     (memory_ablation). Those need the state-difference analogue.

SCOPE CORRECTION (W-K, 2026-09-28): reach is necessary for WINDOWED arms
only (it caught 1/10 broken fixtures overall, but it is one of only two
checks catching a realistic window miss). It does NOT address inert,
unwired, saturated, forced or wrong-target interventions. The broad remedy
is a must-flip PLANT run through the arm's OWN code (K2, J .70, 0 false
alarms). The min zero-false-alarm cover is {K2, an applied count, a
could-fail counter-plant} (workers/W-K/).

INTERPRETATION BOUNDARIES
  High reach is necessary, not sufficient, for an informative windowed
  null. Carrier swaps at a mid-interval tick move every future arrival at
  once and are far less window-sensitive. Prefer them for carrier
  identification, and use reach to audit windowed ablations.
