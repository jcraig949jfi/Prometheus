# T-INS-1  Make the mirror-pair carrier swap a first-class PTE assay

QUESTION. Build and validate a tested assay that returns FLIP /
NO-EFFECT / CHANCE for each carrier, for any champion and tick:
- site state: S, inbox, Kp, E, w, r, each alone and all together;
- channel content, per payload component;
- channel count;
- channel timing (+1/+2 delay);
- channel destination (recipient roll).

WHY. On 2026-09-27 this swap decoded M2 and settled M3 in minutes, and it
beat every C1b mechanical label. A future prereg should use it as the
primary mechanism instrument.

EVIDENCE.
- prometheus/ananke/lens.py: swap, roll_slots, roll_recipients,
  swap_verdict.
- spikes/s_m2.py and s_m3.py.
- The decision rule in ../SPIKES_2026-09-27_PLAN.md.

STEPS
1 Move the swap logic into a tested module (lens.py is fine), with pytest
  fixtures on HAND PLANTS whose answers are known:
  - plants.echo_hold: content FLIPs; S NO-EFFECT;
  - hold_latch: S FLIPs; channel NO-EFFECT;
  - rule_switch_hold: r FLIPs;
  - route_relay: w FLIPs.
  Every verdict must be shown on a known answer, and each check must be
  able to fail.
2 Add the reach check (T-TA-1) as an optional column.
3 Document the relative-threshold rule (T-INS-4). CHANCE vs NO-EFFECT is
  already relative to the normal lo99 in swap_verdict.
4 Run the assay over all C1 SIGNAL comm cells and produce a carrier table.
  The data also feeds T-TM-1 and T-DM-2.

DECISION. Done when the fixtures pass, including negative controls: a
swap on the wrong carrier must return NO-EFFECT on each plant.

DELIVERABLES. The module + tests, a C1 carrier table (out/), a one-page
note.

STOP. 4 h.
