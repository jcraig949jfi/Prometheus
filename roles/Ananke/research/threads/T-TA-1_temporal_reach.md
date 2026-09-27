# T-TA-1  Temporal reach check for windowed interventions

QUESTION. For any time-windowed ablation, how much of the cue-bearing
causal mass does the window intersect? Build cue_arrival_profile and a
WINDOW_UNREACHABLE label.

WHY. C1's packet-ablation window covered 0% of the cue-bearing arrivals
in both M3 cells (S-F), and that produced a false "transport irrelevant".
The same failure shape recurs in 4 seats (../CROSS_ENGINE_THREADS X-4).

EVIDENCE. ../TEMPORAL_INTERVENTION_COVERAGE.md; spikes/s_f.py (the
single-cue twin construction and the actuator-delivery diff).

STEPS
1 Generalize s_f.py into lens.cue_arrival_profile(ph, genome, env,
  trial=k). It returns a per (tick, site) boolean map of cue-bearing
  deliveries and of state differences, from single-cue twins.
2 Define reach(window) = cue-bearing mass inside the window / total from
  the cue onset to the readout. Known-answer test: plants.c1b_da_physics
  + relay_flood with delay == delta must give reach 0 for C1's window and
  1 for the corrected window.
3 Apply it to every C1 D-wave windowed control (packet_ablation,
  memory_ablation). Tabulate reach per cell and flag reach < 0.5.
4 Write a short methodology note for other seats (the X-4 fleet check).

DECISION. Done when the known-answer tests pass and the C1 table is
committed.

DELIVERABLES. The function + tests, the table, the fleet note.

STOP. 3 h.
