# PREREG PTE-C1b -- adjudicate the two unexpected C1 mechanisms (M2, M3)

Currency: 2026-09-25 (date -u 23:3xZ). Seat: Ananke. Status: DRAFT v0.
Committed for steward review under the operator HOLD. It is NOT frozen:
it becomes PREREGISTERED at its freeze commit, which lands on its own,
before the C1b code freeze and before any C1b row exists. No C1b run may
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
    It can only have produced false NOT_SUPPORTED. C1b re-runs the battery
    with the corrected window on the 7 D-wave promoted cells as a side
    table (label CORRECTED_WINDOW_RECHECK), reported beside C1's labels.
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
  reset_all_nonpacket        S, inbox, Kp, w (r is constant: rules 1)
  flush_inflight             Msum, Mcnt := 0 (every ring slot) at t_m
  flush_inflight_late        same at t0 + cue_len + gap - 1
  drop_window_corrected      arrivals dropped over [t0, readout] incl.
  zero_comm, randomize_payload, shuffle_time   (C1 controls, repeated)
Census (read-only telemetry, every tick of the gap): total in-flight
count sum(Mcnt); signed in-flight payload sum sum(Msum[..., 0]); the
same restricted to slots addressed to the readout site; the inbox sum.
Fingerprint statistic: held-out accuracy of predicting the target from
sign(signed in-flight sum) at t_m, against a permutation null over mirror
pairs (2000 permutations).
Labels (mechanical; CI = 99% bootstrap over mirror pairs, as C1):
  DELAY_LINE_SPECIMEN iff
    (a) flush_inflight hi99 <= 0.60, AND
    (b) reset_all_nonpacket: lo99 of (acc - normal) >= -0.10, AND
    (c) the in-flight sign predicts the target at t_m with lo99 > 0.60
        and beats the permutation null (p < 0.01).
  INBOX_CARRIER    (a) fails, reset_inbox hi99 <= 0.60, (b) fails.
  OTHER_CARRIER    (b) fails for a named carrier (Kp, w or S): named.
  MIXED            more than one single-carrier reset drops acc by >= 0.10.
  NOT_SUPPORTED    none of the above.
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
Labels:
  TIMING_LOCKED_TRANSPORT iff drop_readout_tick_only hi99 <= 0.60 AND
    drop_window_corrected hi99 <= 0.60 AND drop_window_c1 lo99 >= 0.62.
    That is H-M3-0 confirmed: C1's null was the window, and M3 is transport
    whose packets land on the readout tick.
  RULE_SWITCH_REQUIRED iff freeze_rule <= normal - 0.10 (lo99 of the
    difference < -0.05 and point <= -0.10) AND freeze_routing within
    0.05. Reported whether or not TIMING_LOCKED_TRANSPORT also holds:
    both can be true (transport delivers, the rule switch reads).
  SELF_MODIFYING_CONFIRMED iff RULE_SWITCH_REQUIRED AND the actuator's r
    at readout predicts the target above the permutation null. The rule
    state carries the cue, not just the capacity to read it.
  NOT_SUPPORTED    none of the above.
  M3_REPRODUCED iff a label above holds and >= 1 of 4 fresh-seed searches
    per cell reaches SIGNAL with the same label.
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
    drop_readout_tick_only DOES (the D-A fixture).
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
battery). D-A was found by that author reading its own code. An
independent reviewer should re-derive D-A from assays.py and engine.py
(tick order: delivery, sense, wake, run, emit, readout trace).
Held-out worlds are seed namespaces, not sealed worlds. 4 fresh searches
per specimen is a small replication budget: "not reproduced" means
"not at this budget". Nothing here promotes a mechanism beyond the seat
before the Kairos/Elenchus review (operator ruling 2026-09-25).
