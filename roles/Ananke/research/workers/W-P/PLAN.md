# W-P PLAN (E-ANANKE-W-P, T-INS-8, MWO-0002) -- FROZEN before any champion swap run

Question. 369f5a5b (RELAY) and 4781b0a1 (MAJ) have a large N ("neither") fraction under
the site/channel swap (W-M SINGLE census). Name the interaction behind N.

## 0 Algebra (why a truth table answers it)
Mirror partners A, B share every exogenous draw. After the last cue tick (o >= 1) no
mirror-different input arrives before the readout (W-M: identity 1.00 at o >= 1), so the
readout is a deterministic function of the state at the swap tick. Partition that state
into components c_1..c_n (sub-arrays). For z in {0,1}^n let a(z) = sign of world A's
readout when the components with z_i = 1 come from B (swap). Then world B with swap set z
is world A with swap set ~z: b(z) = a(~z) (IDENTITY; checked, s3). Define
f(z) = 1 if a(z) = y_B (follows partner), 0 if a(z) = y_A, T if S0 = 0 (tie).
For an eligible pair-trial (both partners normal-correct) f(0) = 0 and f(1) = 1.
Coarse census: S <=> f(site)=1, f(chan)=0; C <=> f(site)=0, f(chan)=1; N <=> f(site) =
f(chan). Lemma: if f depended on site components only, f(site) = f(1) = 1 and
f(chan) = f(0) = 0, i.e. S. So N ALWAYS needs >= 1 site and >= 1 channel component in
its relevant set: "N is a site x channel interaction" is a tautology. The content is
WHICH components and WHAT function:
- JOINT-2: f depends on exactly two components X (site), Y (channel) and is AND
  (f = 1 only when both swapped) or OR (f = 1 when either is). Both N sub-patterns are
  this: (1,0,1,0) = AND for A = OR for B. The chimeras' common answer d is the
  "dominant polarity": the readout is d unless BOTH carriers hold not-d.
- GATED (the brief's "register that makes both chimeras answer the same"): f is a
  3-variable multiplexer f(z) = (z_G == 0 ? z_X : z_Y): a mirror-different gate/phase
  component G selects which carrier is read. When G_A and G_B select different carriers
  the pair-trial is N; when they select the same carrier it is S or C.
- HIGHER: |R| >= 3 and not a MUX (e.g. coherence of >= 3 components required).
R = relevant set = {i : f(z) != f(z xor e_i) for some z}. Minimal decisive set = the
smallest Z with f(Z) = 1 and f(~Z) = 0 (swapping Z makes BOTH partners follow the
partner, i.e. a clean site-like pattern for the split Z vs ~Z). Note: for both JOINT-2
and GATED the minimal decisive set is the carrier pair {X, Y}; R separates them.

## 1 Instrument
tt.py: run M normal worlds to the swap tick of trial k, snapshot the full state, then
run 2^(n-1) chimera blocks (all z with z_S = 0; the other half from b(z) = a(~z)) to the
readout. Bit-identity with lens_swap.run_arms SINGLE arms asserted (check_vs_lens) on
both champions and a plant before use. SINGLE-trial semantics (only trial k swapped).
Worlds: assays.world_seeds(0x610, 256) = 128 mirror pairs; trials 1..11; offsets 1..15.
Coarse components (brief): 369f5a5b: S, inbox (Acc_sum+Acc_cnt), Kp, r, Msum, Mcnt
(w dropped from the main run: dest_mode 'all' never reads w; kept in a verification
slice, s3). E dropped for both (economy off: E constant = e_max). 4781b0a1: S, inbox,
Kp, w (dest 'sample': w routes), Msum, Mcnt.
CIs: 99% pair bootstrap (resample the 128 pairs, pool their trials), 2000 draws.

## 2 Decision rules (per champion x offset; frozen)
Base = eligible N pair-trials with no tie in the cube (f defined everywhere). If base < 20:
UNDEFINED. Else:
- JOINT-2(X,Y) if the modal 2-component relevant set {X,Y} covers >= .60 of base and
  its 99% CI lo >= .45.
- GATED(G; X,Y) if MUX with the same gate G covers >= .60 of base, CI lo >= .45.
- HIGHER if |R| >= 3 non-MUX covers >= .50 of base.
- else MIXED (report the distribution).
Polarity: RECTIFIED(+/-) if the chimeras' common answer d has one fixed sign in >= .90
of base (CI lo >= .80); else PAIR-SPECIFIC.
Also reported per offset: census fS/fC/fN recomputed from the cube (must agree exactly
with lens_swap-style counting), modal minimal decisive set and its fraction, fraction of
N trials whose R contains each component, fraction of ties.

## 3 Checks
C1 bit-identity tt vs lens_swap.run_arms (normal, site_all, channel_all, joint SINGLE
   arms) on each champion (1 trial, 1 offset, 32 worlds) and on the KA plants.
C2 identity: on one verification slice per champion (trial 6, all offsets, FULL cube incl.
   w for 369f5a5b) b(z) = a(~z) for >= .99 of (pair, z) at o >= 1. Must-fail: o = -1
   (a cue tick still arrives after the swap) gives < .99.
C3 w inert in 369f5a5b: w in R for 0 pair-trials in the verification slice (exact).

## 4 Known answers (plants on c1b_echo_physics, HOLD cue 2 gap 8, swap offsets 3..8)
KA-AND  max_plant: sensor latches cue sign in S1; echo (echo_hold) carries it in flight;
        readout S0 := MAX(arrival sign, S1). Expected: fN = 1, JOINT-2(S, Msum), OR/AND
        per pair, RECTIFIED(+), minimal decisive set {S, Msum}.
KA-MUX  mux_plant: as KA-AND plus a gate Kp[j] := cue sign (WIMM); readout
        S0 := (Kp[j] > 0 ? S1 : arrival sign). Expected: fN = 1, GATED(Kp; S, Msum),
        minimal decisive set {S, Msum}, and NOT JOINT-2.
Must-fail inputs: hold_latch (expected R = {S}, pattern S, base N = 0 -> UNDEFINED, never
JOINT-2/GATED); echo_hold (R = {Msum}, pattern C, UNDEFINED); KA-AND analysed with an
incomplete component list (Msum omitted) must NOT find a decisive set inside the list
(reported as NO-DECISIVE) and must not read JOINT-2(S, Msum); a synthetic XOR-of-3 table
must read HIGHER, a synthetic MUX table GATED, a synthetic AND table JOINT-2 (unit tests
of the classifier).

## 5 Predictions (from specimen decompilation, before any swap result)
P1 identity >= .99 at o >= 1 on both verification slices (C2).
P2 4781b0a1 readout line S0 := IN0_1 - 3 + Kp[7]; Kp written with EMIT = MAX(S1, SENSE)
   (>= 0 at the actuator). Predict JOINT-2({Kp} x {Msum or inbox}) at the majority of
   offsets with base >= 20, RECTIFIED(+).
P3 369f5a5b: S1 := MAX(IN1_0, SENSE + S1), S0 := 4(Kp[7] - 25) + S1, r := CNT0 mod 4.
   Predict the modal R contains S and Msum; r in R for >= .30 of N trials at >= 1
   offset (a candidate gate); class less clean than 4781b0a1 (MIXED or GATED allowed);
   RECTIFIED(+).
P4 C3 holds (w never relevant).
If a prediction fails it is reported as failed; thresholds are not moved.

## 6 Stage 2 (refinement; procedure frozen, parts chosen from stage-1 output)
At <= 3 offsets per champion (max-fN offset, earliest and latest offsets with fN >= .20):
split the components of the modal minimal decisive set into parts (S -> S0, S1;
inbox -> Acc_sum, Acc_cnt; Kp -> Kp[7], Kp[rest]; Msum -> per channel (369f5a5b) or per
payload (4781b0a1); Mcnt kept whole), lump every other coarse component into one "rest"
part, <= 6 parts, full truth table, same rules. Reports the refined minimal decisive set.

## 7 Budget
CPU only, torch threads 2 per process, <= 4 processes under a Fabric cpu8 lease; <= 3 h.
