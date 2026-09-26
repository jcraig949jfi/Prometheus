# PREREG PTE-C1b -- adjudicate the two unexpected C1 mechanisms (M2, M3)

Currency: 2026-09-26 (v1; date -u 00:3xZ). Seat: Ananke. Status:
PREREGISTERED v1 (frozen). This file is committed on its own, before the
C1b code freeze and before any C1b row exists. History: DRAFT v0
77a55ec8f; steward review #643 (Aporia) items 1-5 applied in v1; D-A
independently re-derived in #640. Any later change is a dated annotation
beside the original. No C1b run may
start until Aporia releases the HOLD over comms (directive
roles/Ananke/prompts/2026-09-25_pte_si01_directive/, s2-s3).

Scope rule (directive s3): C1b adjudicates M2 and M3 and nothing else.
It carries NO Selective-Irreversibility endpoint. It does not relabel C1:
every C1 label stands as computed, and C1b issues its own labels beside
them. The C1 substrate, physics and oracle are unchanged (s5 lists the
only new code: assay switches and read-only telemetry).

## 0. Question

M2 (C1_REPORT s3): in HOLD cell 4ab2ba014aac967e the held bit appeared to
live in packets in flight, not in site state. That result is POST-HOC and
rests on ONE cell. Does the bit really live in in-flight packets, in which
other carrier if not, and does a fresh search find the same fingerprint?

M3 (C1_REPORT s3): in MAJ cells 0a23398f20cc41a2 and f6b623cdb23afd2c,
zero-comm gave 0.50 but packet ablation did nothing, adaptation-off gave
0.53-0.55, and +1 latency gave 0.49-0.50. The candidate reading was
"self-modifying, timing-locked". Is it self-modification (SETRULE), is it
an instrument artefact (s2 D-A), or neither?

A NULL is a valid result for either mechanism.

## 1. Specimens (frozen; genomes are in the committed C1 rows)

Source: roles/Ananke/pte/c1_rows/cells.jsonl.gz (6596 rows, raw sha256
prefix 2416b7bb3a9e0f37), field result.champion. Code at C1 freeze:
362f2189b.

  id                 fam   wave  key physics (full levels in the row)
  4ab2ba014aac967e   HOLD  C     ring N=144 r3, sync period 2, lat 1+1*hop
                                 +jit 1, loss .1, cap 2 saturate, fanout 8
                                 sample, state_dim 2, P 2, C 1, decay 0,
                                 plastic_route 1, WIMM 1, setrule 0,
                                 rules 1, mut 0; env gap 8, d 3
  0a23398f20cc41a2   MAJ   B     ring N=100 r3 rewire 200, async p .8,
                                 lat 4+0*hop+jit 0, loss .3, dup .1,
                                 noise 64, cap 2 none, fanout 8 all,
                                 state_dim 8, P 4, C 4, decay 3,
                                 plastic_route 1, WIMM 0, SETRULE 1,
                                 rules 4, mut 0; env delta 4, d 2
  f6b623cdb23afd2c   MAJ   B     as 0a23398f but collision saturate; env d 3

## 2. Design facts found by CODE INSPECTION before any C1b data

These come from reading assays.py and engine.py and the C1 rows. No new
run produced them. Each one is a hypothesis C1b tests, not a finding.

D-A PACKET-ABLATION WINDOW EXCLUDES THE READOUT TICK.
    assays.control_battery drops arrivals at ticks [t0, t0+delta) (MAJ)
    or [t0, t0+cue_len+gap) (HOLD); the readout is traced at t0+delta
    (resp. t0+cue_len+gap), AFTER that tick's delivery and program. An
    arrival AT the readout tick is never dropped. In both M3 cells the
    delay is exactly lat_base 4 + 0*hop + jitter 0 = 4 = delta. So a cue
    emitted at t0 arrives exactly at the readout tick, the one tick the
    ablation leaves alone. That alone would explain "packet ablation does
    nothing" and "+1 latency -> 0.50" without any self-modification.
    Hypothesis H-M3-0 (s4) tests it first. If it holds, M3 is ordinary
    timing-locked transport and the C1 CAUSAL_SUPPORT rule missed it
    through an instrument defect. C1 labels are still not changed; the
    defect is ledgered.
    The same window rule applies to RELAY and HOLD, but there the
    ablation already fired, so it cannot have produced a false SUPPORT.
    It can only have produced false NOT_SUPPORTED. The exclusion is
    FAMILY-GENERAL (HOLD included: an arrival exactly at the HOLD readout
    tick also survives), per the independent re-derivation #640.
    C1b re-runs the battery with the corrected window on EVERY D-wave
    adjudicated cell, all families including HOLD, as a side table
    (label CORRECTED_WINDOW_RECHECK), reported beside C1's labels.
D-B C1 "MEMORY ABLATION" RESET ONLY S.
    Controls.reset_state_at zeroes S. It leaves Acc_sum/Acc_cnt (delivered
    but unread inbox), Kp (writable immediates; M2 has WIMM 1), w (routing
    weights; M2 has plastic_route 1) and r untouched. The M2 claim
    "not in any site" is therefore under-identified: the bit could sit in
    the inbox, in Kp or in w. C1b resets each carrier separately (s3).
D-C M3's SELF-MODIFICATION CHANNELS ARE SETRULE AND ROUTING ONLY.
    Both M3 cells have wimm 0 and mut_site 0. C1's "adaptation off"
    disabled routing writes + SETRULE (WIMM and mutation were already off),
    and "frozen routing" alone did nothing. So the WIMM / mutation-site
    arms of the directive's s3 split are NOT_APPLICABLE by physics for M3.
    They are reported as such, not run. The live split is SETRULE vs
    routing.

## 3. M2 battery (HOLD 4ab2ba01)

All at mid-gap tick t_m = t0 + cue_len + gap//2 of every trial (C1's
tick), on H = 64 held-out worlds (32 mirror pairs), namespace s6.
  normal
  reset_S                    S := 0              (C1's control, repeated)
  reset_inbox                Acc_sum, Acc_cnt := 0
  reset_Kp                   Kp := 0
  reset_w                    w := initial (16)
  reset_En                   En := e_max (energy carrier; review #643.1)
  reset_all_nonpacket        S, inbox, Kp, w, En (r is constant: rules 1)
  flush_inflight             Msum, Mcnt := 0 (every ring slot) at t_m
  flush_inflight_iti         the same flush at the first ITI tick of every
                             trial (t0 + cue_len + gap + 1), scored on the
                             trials that follow it (trial 0 excluded):
                             the sham for flush (review #643.2)
  flush_inflight_late        same at t0 + cue_len + gap - 1
  drop_window_corrected      arrivals dropped over [t0, readout] incl.
  zero_comm, randomize_payload, shuffle_time   (C1 controls, repeated)
Census (read-only telemetry, every tick of the gap): total in-flight
count sum(Mcnt); signed in-flight payload sum sum(Msum[..., 0]); the
same restricted to slots addressed to the readout site; the inbox sum.
Fingerprint statistic: held-out accuracy of predicting the target from
sign(signed in-flight sum) at t_m, against a permutation null over mirror
pairs (2000 permutations).
En note: in M2 and M3 the economy is OFF, so En is held at e_max every
tick and cannot carry a sign. reset_En is still run: its no-op guard is
then expected to return NOT_APPLICABLE, which itself confirms the point.
Component booleans (CI = 99% bootstrap over mirror pairs, as C1;
"kills" = hi99 <= 0.60; "drops" = point drop >= 0.10 vs normal with the
lo99 of the difference < -0.05; "intact" = lo99 of (acc - normal)
>= -0.10, which is an ABSENCE reading and counts only where its positive
control fixture (s5) fired):
  A   flush_inflight kills
  Z   flush_inflight_iti intact (the sham)
  B   reset_all_nonpacket intact
  C   the in-flight sign predicts the target at t_m (lo99 > 0.60 and
      permutation p < 0.01)
  I   reset_inbox drops
  Kx  reset_x drops, for x in {S, Kp, w, En}
Label = the FIRST rule that matches (an ordered decision list, total by
construction; review #643.4):
  1 INSTRUMENT_FAILURE      any s5 fixture failed
  2 FLUSH_NONSPECIFIC       A and not Z (the flush hurts even outside the
                            gap: generic disruption, not a delay line)
  3 DELAY_LINE_SPECIMEN     A and Z and B and C
  4 IN_FLIGHT_UNDECODED     A and Z and B and not C (the bit rides in
                            flight but not as the signed sum)
  5 MIXED                   two or more of {A and Z, I, K_S, K_Kp, K_w,
                            K_En} (carriers named)
  6 INBOX_CARRIER           I
  7 OTHER_CARRIER           exactly one Kx (x named)
  8 IN_FLIGHT_PLUS_JOINT    A and Z and not B (in flight, plus a non-packet
                            contribution that no single reset shows)
  9 JOINT_NONPACKET         not B (only the joint non-packet reset hurts)
 10 NOT_SUPPORTED           otherwise
The code enumerates all 2^9 combinations of the component booleans
(A, Z, B, C, I, K_S, K_Kp, K_w, K_En), asserts that each maps to exactly
one label, and commits that table with the code freeze, before any row.
  DELAY_LINE_REPRODUCED iff DELAY_LINE_SPECIMEN and >= 1 of the 4
    fresh-seed searches (s5) reaches SIGNAL AND passes (a)-(c) itself.
    A fresh search that reaches SIGNAL with a site latch is reported as
    "same physics, different mechanism", not as a replication.

## 4. M3 battery (MAJ 0a23398f, f6b623cd)

H-M3-0 first (instrument check):
  drop_window_corrected      arrivals dropped over [t0, t0+delta]
  drop_readout_tick_only     arrivals dropped at t0+delta only
  drop_window_c1             C1's window [t0, t0+delta), repeated
Then the self-modification split:
  freeze_rule                SETRULE writes ignored (new switch)
  freeze_routing             (C1 control, repeated)
  adaptation_off             (C1 control, repeated)
  latency -1 / +1            lat_base 3 / 5 (law transplant)
  jitter +1                  lat_jitter 1
  zero_comm                  (repeated)
Census: per trial, the fraction of sites whose rule pointer r changed;
at the readout tick, the actuator's r and whether it predicts the target
(held-out, with a permutation null).
Component booleans (definitions as s3):
  T   drop_readout_tick_only kills AND drop_window_corrected kills AND
      drop_window_c1 intact (lo99 >= 0.62): H-M3-0 confirmed, i.e. C1's
      null was the window and the packets land on the readout tick
  X   drop_window_c1 kills (C1's own control does NOT reproduce on fresh
      held-out worlds)
  R   freeze_rule drops AND freeze_routing intact (freeze_routing's
      absence reading counts only if the routing positive-control plant
      fired, s5; otherwise R is computed without that clause and the
      label carries the suffix _ROUTING_UNRESOLVED)
  M   the actuator's r at readout predicts the target (lo99 > 0.60,
      permutation p < 0.01): the rule state carries the cue
One PRODUCT label per cell (review #643.4), first match wins:
  1 INSTRUMENT_FAILURE          any s5 fixture failed
  2 C1_CONTROL_NOT_REPRODUCED   X (reported; the rest is still computed
                                and shown, but no M3 label is issued)
  3 TRANSPORT+SELF_MODIFYING    T and R and M
  4 TRANSPORT+RULE_SWITCH       T and R and not M
  5 TRANSPORT_ONLY              T and not R
  6 SELF_MODIFYING_ONLY         not T and R and M
  7 RULE_SWITCH_ONLY            not T and R and not M
  8 NOT_SUPPORTED               otherwise
Same exhaustive enumeration + assert as s3 (2^4 combinations).
  M3_REPRODUCED iff the cell's label is one of 3-7 and >= 1 of 4 fresh-seed
    searches per cell reaches SIGNAL with the same label.
WIMM, mut_site: NOT_APPLICABLE by physics (D-C).

## 5. What gets built (no physics change)

Assay switches in Controls, default off, with a no-op guard (a control
that changes no state is NOT_APPLICABLE, as in C1):
  reset_parts: which arrays reset_state_at zeroes (default ("S",) = C1)
  flush_inflight_at: ticks at which Msum/Mcnt are zeroed in every slot
  drop_window: inclusive-readout variant (C1's default unchanged)
  freeze_rule: SETRULE writes ignored
Read-only census telemetry (in-flight count and signed sum, per-site
rule-change counts).
Tests: every switch changes state when the channel exists and is a no-op
guard otherwise; with all switches off, per-world digests equal those of
the C1 freeze code on the conformance worlds (the switches cannot move
normal physics); the independent CPU oracle suite still passes (145).
The oracle has no Controls path, so the switches are verified against
hand plants with known answers:
  hold_latch (a site latch): reset_S kills it, flush_inflight does not;
  an echo plant (the bit only in flight): flush kills it, reset_S does
    not;
  relay_flood with delay == delta: drop_window_c1 does NOT kill it,
    drop_readout_tick_only DOES (the D-A fixture);
  echo plant under flush_inflight_iti: the next trial is intact (the sham
    cannot fire on a pure in-gap delay line);
  a rule-switch plant (rules 2; the cue sign selects the rule by SETRULE,
    and each rule writes a fixed sign into S0 at readout): freeze_rule
    MUST drop it (the positive control for R; review #643.3);
  a plastic-routing plant (the cue sign writes w toward or away from the
    actuator; the actuator reads its arrival count): freeze_routing MUST
    drop it (the positive control for freeze_routing's absence reading).
Every "intact" (absence) reading counts only where its positive control
fired (joint rule #611/#617/#618). If a positive-control plant CANNOT be
constructed at the specimen's physics, the absence clause it guards is
declared NOT_ELIGIBLE in the code freeze, before any row, and labels that
need it carry the suffix _UNRESOLVED.
Any fixture failing -> INSTRUMENT_FAILURE; no C1b label is issued.

## 6. Seeds, budget, stopping

Held-out worlds: namespace 0xC1B0 (disjoint from C1's 0x7A1 / 0xF1A /
0x4E1D and the post-hoc 0x9057). Fresh-seed searches: 4 per specimen,
search seeds H(0xC1B5, cell, k), k = 0..3, C1's SearchSpec unchanged
(pop 96, 36 gens), same physics and env as the specimen. The champion is
chosen on training accuracy only and evaluated once on held-out worlds.
Budget: batteries are minutes per specimen; 12 fresh searches at C1's
~51 s/cell (A1 measured) plus batteries on the fresh champions come to
well under 1 h. Hard cap 3 h GPU on M1, and only after Aporia confirms
no host conflict. Unrun cells are CENSORED. The driver refuses to start
on a dirty tree or a code SHA other than the frozen one. PARK after 5
consecutive failed cells.

## 7. Losable predictions (Ananke's, scored in the C1b report)

C1b-P1 H-M3-0 holds in BOTH M3 cells (TIMING_LOCKED_TRANSPORT).
C1b-P2 M3 is also RULE_SWITCH_REQUIRED in at least one cell (C1's
       adaptation-off drop to 0.53-0.55 was not a window artefact).
C1b-P3 M2 gets DELAY_LINE_SPECIMEN (flush kills it, non-packet resets
       do not).
C1b-P4 reset_inbox alone does not drop M2 by >= 0.10.
C1b-P5 DELAY_LINE_REPRODUCED fails: at most 1 of 4 fresh HOLD searches
       reproduces the fingerprint (HOLD searches mostly find the latch).
C1b-P6 CORRECTED_WINDOW_RECHECK changes no RELAY verdict.

## 8. Conflicts of interest and limits

Same author as C1 (substrate, envs, search, detectors, and now this
battery). D-A was found by that author reading its own code. It was
independently re-derived from engine.py and assays.py by Aporia (comms
#640, read before this draft's reasoning): mechanism CONFIRMED in code,
family-general. #640 did NOT verify that the M3 cells have
delay == delta; H-M3-0 settles that.
Held-out worlds are seed namespaces, not sealed worlds. 4 fresh searches
per specimen is a small replication budget: "not reproduced" means
"not at this budget". Nothing here promotes a mechanism beyond the seat
before the Kairos/Elenchus review (operator ruling 2026-09-25).

## Amendment A1, 2026-09-26 02:3xZ (PRE-DATA; no C1b row exists; before the code freeze)

Authority: Ananke #658 (proposal), Aporia #659 (ruling), Cyclops #660
(concurrence -> JOINT). Rule that permits it, as the stewards state it: an
amendment may be added before any row exists if it ADDS a control and its
only possible effect is to make a label MORE conservative. Nothing above
this line is changed.

A1.1 F_sham_positive (a positive control for Z). Z ("flush_inflight_iti
intact") is an absence reading that gates M2 labels, and on F_echo the
ITI flush was NOT_APPLICABLE (nothing in flight at the ITI tick), so it
passed trivially. Add a fixture: a hand plant whose competence NEEDS
in-flight traffic that crosses the inter-trial interval. The ITI flush
must DROP it (s3 "drops"). Z then counts only if F_sham_positive fired.
If no such plant can be built, Z is NOT_ELIGIBLE, and every M2 label whose
rule requires Z true (DELAY_LINE_SPECIMEN, IN_FLIGHT_UNDECODED,
IN_FLIGHT_PLUS_JOINT, and MIXED where its in_flight component is present)
carries the suffix _UNRESOLVED. FLUSH_NONSPECIFIC needs Z FALSE (a
positive harm reading) and is unaffected.

A1.2 CARRYOVER CENSUS (read-only, report item, changes no label). At each
trial's onset tick t0, before the cue, record the in-flight count and the
signed in-flight sum, per specimen and per arm where the census runs. If
the count is nonzero AND the signed sum's sign correlates with the
PREVIOUS trial's target (the s3 census_predicts statistic, targets
shifted by one trial, lo99 > 0.60 and permutation p < 0.01), the C1b
report flags CARRYOVER as a confound on that specimen. Why: in the F_DA
dev run, relay waves needed about 48 ticks to die, while C1's
environments use iti 2. drop_readout_tick_only (H-M3-0) could then remove
a carried-over wave as well as this trial's cue, and an M2 "held bit"
could partly be the previous trial's echo.

## Amendment A2, 2026-09-26 03:3xZ (PRE-DATA; no C1b row exists; before the code freeze)

Authority: Ananke #661 (observation), Aporia #662 (ruling), Cyclops #669
(concurrence -> JOINT). A2.1 is added under the stewards' rule (a control
added before any row, whose only effect is a more conservative label).
A2.2 is a CLARIFICATION of the frozen s5 text (line 231, "constructed at
the specimen's physics"), not a relaxation. Nothing above is changed.

A2.1 INERT_BY_PHYSICS. Under dest_mode "all", engine._emit sends to the
whole neighbour table and never reads w, and no instruction loads w
(independently confirmed, #662). In such cells routing cannot carry
anything, so R's routing clause reads INERT_BY_PHYSICS, with no
_ROUTING_UNRESOLVED suffix. WORDING GUARD (binding on the report): in such
a cell a label containing RULE_SWITCH means "SETRULE is required; routing
could not carry anything". It must NOT be read or written as "the rule,
rather than routing, was shown to carry it". The D-wave side table marks
the C1 frozen_routing result of every dest_mode "all" cell as VACUOUS.
Both M3 cells are dest_mode "all".

A2.2 POSITIVE CONTROLS AT EACH SPECIMEN'S PHYSICS. Fixtures at fixture
physics validate the instrument. They do NOT satisfy the eligibility
clause. Before the code freeze, each positive-control plant is rerun at
each specimen's physics and environment:
  specimen physics = the specimen's levels for topology, n_sites,
    radius, dest_mode, fanout, loss, loss_per_hop, lat_base, lat_hop,
    lat_jitter, dup, noise, cap, collision, update_mode, update_p,
    update_period, decay_shift, economy, mut_site;
  plant-structural fields set to the plant's needs (these are genome
    space, not communication physics): prog_len, state_dim,
    payload_width, channels, rules, setrule, wimm, plastic_route,
    adapt_shift.
  Specimen env = the specimen's env (M2: HOLD gap 8; M3: MAJ, delta 4).
  A plant written for another family runs on that family's env with the
  specimen's timing dials (gap, delta, cue_len, iti).
Absence clause -> the plant that must fire at that physics:
  M2  B (reset_all_nonpacket intact) ........ F_latch (reset_S kills it)
  M2  Z (ITI flush intact) .................. F_sham_positive (A1.1)
  M3  T's "drop_window_c1 intact" ........... F_DA (C1 window leaves it;
                                              readout-tick drop kills it)
  M3  R's "freeze_routing intact" ........... INERT_BY_PHYSICS (A2.1)
  M3  not-R ("freeze_rule did not drop") .... F_rule (freeze_rule drops
                                              it). This row is ADDED here
                                              under the same conservative
                                              rule: a null freeze_rule
                                              reading is an absence too.
Every absence clause whose plant fails at the specimen's physics is
NOT_ELIGIBLE, and each label that uses it carries _UNRESOLVED. A plant
that cannot be built at all at a physics where the mechanism cannot exist
is covered by A2.1 (INERT_BY_PHYSICS), not by _UNRESOLVED. The
per-specimen eligibility table is committed with the code freeze, before
any row.

## Amendment A3, 2026-09-26 04:3xZ (PRE-DATA; no C1b row exists; before the code freeze)

Authority: Ananke #674 (question), Aporia #675 (ruling; disclosed that it
had seen the plant POINT values in #674, not their CIs), Cyclops #678
(concurrence -> JOINT). A2's added not-R row is accepted (#675).

A3.1 "The positive control FIRED" at a specimen's physics (A2.2) means
BOTH:
  (i)  COMPETENT: the plant at that physics meets C1's SIGNAL bar, i.e.
       lo99 of normal accuracy > 0.55 over mirror pairs, same bootstrap;
  (ii) DECISIVELY NOT-INTACT: under the switch, hi99 of
       (acc_switched - acc_normal) < -0.10, same 99% bootstrap, so the
       whole CI lies outside s3's intact band (intact = lo99 >= -0.10).
This applies UNIFORMLY to every absence clause (B, Z, not-R, T's C1
window, and any other), whatever it does to any label. A clause whose
plant fails (i) or (ii) is NOT_ELIGIBLE, and its labels carry
_UNRESOLVED. The 0.95 competence bar is kept ONLY for fixture-physics
validation (s5), unchanged.
A3.2 Switch per plant, as mapped in A2.2:
  F_latch -> reset_S; F_sham_positive -> flush_inflight_iti (scored from
  trial 1, against normal from trial 1); F_rule -> freeze_rule;
  F_DA -> drop_readout_tick_only. F_echo validates A only and gates
  nothing.
A3.3 The recomputed per-specimen eligibility table is committed with the
code freeze.
