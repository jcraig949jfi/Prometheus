# Cross-thread compression (ARC3 Block P): hypotheses, and attempts to falsify them

These are candidate compressions of many Threads into few ideas. They are
NOT laws. Each is tested against existing PTE and fleet examples, and a
counterexample is actively sought.

H1 FUNCTION != STORAGE FORM. Memory-like behaviour without persistent
   stored state.
   For: M2 holds a bit across a gap as a two-hop echo, with no register
     holding it (W-A); the designed echoes E1-E6 do too.
   Attempted falsification: is every HOLD solution like this? No. 81/85
     HOLD champions are SITE-carried (W-F). The latch is the common form,
     and the echo is a minority. H1 therefore survives only as "the
     function does not FIX the form"; it is NOT "memory is usually
     transient".
   Status: SURVIVES in the weak form.
H2 CARRIER != LOCATION (information moves between carriers over time).
   For: 4781b0a1 source -> channel handoff; W-F late-tick class changes
     (5 JOINT -> SITE, 3 CHANNEL -> SITE); designed E2 channel -> S2 ->
     S0, with CHANCE/CHANCE exactly at the handoff tick.
   Attempted falsification: HOLD latches keep one carrier (site) for the
     whole interval, with no handoff after the cue lands. So H2 is a
     property of TRANSPORT-type mechanisms, not of all PTE computation.
   Status: SURVIVES, scoped to transport.
H3 DECODABLE != USED.
   For: 4781b0a1 pay0 decodes at .85 but its swap has no effect; W-E scars
     are decodable (paired 1.00) yet never change an answer.
   Counter-evidence sought: a decodable carrier whose swap has no effect
     but which IS used, in a way the swap misses (e.g. presence leaking
     into content, W-C F7). The pay0 case may be presence leakage, which
     is still "not used as content".
   Status: SURVIVES. Decoders never establish a carrier; this is already
     written into the instrument cards.
H4 INTERVENTION != CAUSAL TEST.
   For: 8 fleet cases (W-D); C1 D-A; routing under dest_mode all;
     arm_identical no-ops.
   Falsification attempt (W-K: 21 fixtures, 16 checks, valid twins): no
     single check separates reached from unreached. Identical outputs
     describe both an inert intervention and a true null. Only a plant
     through the arm's own code separates them.
   Status: SURVIVES, sharpened: intervention != causal test, AND
     no-output-change != no-reach.
H5 FAMILY LABEL != MECHANISM.
   For: RELAY champions split site / channel / joint at ONE physics point
     (W-F); C1 "routed relay" x4 hid 2 carrier classes; W-C: 7/13
     specimens are presence codes under content labels.
   Attempted falsification: HOLD is near-uniform (site). The family label
     DOES predict mechanism there.
   Status: SURVIVES for RELAY/MAJ; FAILS for HOLD. Correct scope: "task
     labels under-determine mechanism when the task admits several
     cheap solutions".

A DEEPER COMPRESSION (proposal, to test): H1, H2 and H5 may be one fact.
When a task admits several solutions of similar cost, which one evolves
is set by small program and physics contingencies, and the solutions
differ in carrier and trajectory. HOLD has one dominant cheap solution
(the latch), hence uniformity. RELAY and MAJ have several, hence
diversity. PREDICTION (falsifiable, backlog T-CT-6): carrier diversity
within a family should track the number of distinct low-cost designs
available at that physics. That count can be ESTIMATED with the echo
model and hand-plant costs (instruction counts). HOLD at M2 physics: latch
(4 instr) vs echo (4 instr); the latch dominates, so something beyond
instruction count (robustness to distractors?) must also enter.
