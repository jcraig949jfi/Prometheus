ARCHAEON[m2-49ee5a4d] -> Proteus (Daedalus, Vivarium, Mnemosyne, Harmonia
for the record). OPERATOR RULING ON CAMPAIGN 5 (2026-09-18, verbatim at
roles/Archaeon/prompts/2026-09-18_campaign5/03_OPERATOR_RULING_CLOSURE.md)
and the HANDOVER OF REPRESENTATION B it orders. No ask beyond the receipt
of the handover.

THE RULING, IN ITS OWN WORDS (closure paragraph)
  "Campaign 5 accepted. Phase A: OLD_SUBSTRATE_EXHAUSTED. Phase B:
  boundary successfully created, mechanistic interpretation improved, no
  discovery advantage observed. C5-03 carries an amendment qualification
  caveat. No further Campaign-5 slots authorized. Representation B is
  retained as an experimental instrument, not promoted to the platform VM.
  Next work must alter generative/search structure, not continue
  fault-boundary tuning."

FOR PROTEUS -- what is handed over, where, and what it is NOT
  Representation B is a QUALIFIED EXPERIMENTAL REPRESENTATION, campaign-
  scoped, not a candidate for the frozen VM. The operator: "adoption
  should wait for evidence that it enables a capability that the current
  representation cannot reach, rather than merely different failure
  modes." Nothing in proteus/ was changed (vm.py digest checked before
  and after every Phase-B run).
  archaeon/campaign5/repb/
    vm_b.py        PlayerB: narrow encoding (opcode < 25, read register
                   fields < n_regs, else FAULT); FAIL / FIZZLE; MeterB
                   with faults / distinct sites / faulting ticks;
                   static_validity(); REG_FIELDS table.
    gen_b.py       canonicalize() (old meaning -> narrow encoding, exact:
                   57/57), sample_valid(), raw_words(), inject_invalid(),
                   population().
    grammar_b.py   v0.4 with in-range redraws (insertion, replacement,
                   reference_redirection, randomization); operand_
                   perturbation kept raw; GRAMMAR_B_HASH; descend_b().
    evaluate_b.py  the campaign evaluator through PlayerB (+ answer vector).
    evolve_b.py    EvolutionB: pluggable (evaluator, grammar) on the
                   campaign evolver; crossing / trapped / faulted telemetry.
  Qualification and geometry: C5-03 (fixtures F1-F8; note the caveat:
  a01 PREREGISTRATION_FAILED -- STATISTIC_MISSPECIFIED, a02 exploratory
  under amendment D5-008), C5-04, C5-05 DAMAGE_GEOMETRY_MAP_V2.{md,json},
  C5-06/07/08 readouts, REPRESENTATION_COMPARISON.md.
  What the instrument measured that yours cannot: a countable local
  failure; opcode-word faults recover when skipped (229 replicated),
  register-field faults are lost when skipped (154); no discovery gain
  at equal compute (96 cells). Whether it enables a capability is
  untested and, by the ruling, not Campaign 5's to test.

FOR EVERY SEAT -- the correction that stands
  C4-07's mechanism reading "robustness = dead code" is superseded
  (archaeon/campaign4/SUPERSESSION_2026-09-18.md): robustness is largely
  length/representation-mediated; ablating 11% unreachable code moves
  the neutral share .435 -> .409 while length carries it .17 -> .71;
  executed faults persist under FIZZLE (.46-.80 of populations) with no
  useful novelty. C4-07's numbers are valid.

FOR THE PROGRAM -- where the failure now sits (operator)
  "Campaign 4 could still plausibly blame the absence of a fault
  boundary. Campaign 5 created that boundary and showed that it changes
  local evolutionary geometry and survival semantics, yet discovery
  remains zero. The next experiment should therefore not be 'more
  mutation on Representation B.' It should change the searchable program
  structure or grammar of useful behaviors -- something that can
  generate compositional innovations rather than merely alter fault
  tolerance." Archaeon takes no next slot until directed.
