# REACH01 R4c preregistration: GENUINE reuse of a DISCOVERED mechanism (not an assisted control)

Component: the first COMBINE discovered by search (LADDER01, geometry G1, arm C certificate-guided, seed 7). It is
AUTONOMOUS: COMBINE at 256/256 tile positions and under both alternative physics seeds. It is not COMPOSE (its
a-necessary cells are all shared with the b-path).
- Minimal causally sufficient substructure: its 7 certified-necessary cells (Na U Nb) ALONE reproduce the full
  patch's table at 100% of positions (the full patch has 123 active writers). component_discovered_s7.json holds
  the cells and states.
- Its function (inputs {0x0F, 0x33, 0x55, 0xAA}): f(a, b) = [46 unless a = 0x55] XOR [1 iff b = 0xAA].
  Strict two-input dependence, but each input acts only through one value (a low-information combination).
- Provenance: discovered by search infrastructure (the archive-assisted certificate-guided arm), not designed by the
  experimenter.

New capability (task 2): COMBINE3 on geometry G1 (A (8,1), B (10,1), output (9,6)) plus a third input C at (12,1).
- Input alphabet {0x55, 0xAA} for all three inputs: the values the component's interface is sensitive to. This was
  chosen AFTER seeing the mechanism (disclosed). Every arm faces the identical task.
- Known answers: the component alone depends strictly on a and b (not c) at all positions; an empty patch on none.

Arms, budget, operators and rules: as R4 (N none, S shuffled, U unpromoted, P promoted insert with offsets [-3, 3]^2;
20 x 1024 evaluations; 8 seeds; RULES.json). Reported in addition: position robustness of the solutions.
Dispositions as R4, labelled GENUINE (discovered component; archive-assisted provenance).

Hashes:
  cafa85333e5b08f7fb0dce18598321fd3cb5f0ccbe587923b7ef6d1d24491561 plan_R4c.json
  a2cf73918215363b2e1a11199e94b528dcea7f5a8f09495063fa177b19192737 r4_accum.py
  9937fb2f82e05e64f6a5827bffec3700f929b17b169e5569d910c25847f3c17a component_discovered_s7.json
  f611cc7ef4bbc99214aa57cf0cc841b7227fef40d8fc1e6dd8110399fdde7fd2 RULES.json
  b5d0ba8c340d93788b7f3bacbea9b3e37f28f8cae353cd4be6f934eb10a84d96 ../R3/r3_frontier.py
