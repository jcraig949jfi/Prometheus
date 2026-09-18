+=====================================================================+
|  C5-04 -- GENERATOR x REPRESENTATION CONTROL: PREREGISTRATION         |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
|  Campaign 5, Phase B                                                 |
+=====================================================================+

QUESTION. When programs die or live under representation B, is it the
generator (which words the program was born with) or the representation
(what the interpreter does with them)? No selection anywhere in this
slot: populations are sampled, evaluated once, counted.

DESIGN. 3 generators x 3 interpreters x 3 population seeds, N=200 each.
  generators    raw (uniform 32-bit words, the old FOUNDRY generator)
                valid (in-range opcode and register words, same knobs)
                injected(2) (valid + exactly two out-of-range read fields)
  interpreters  OLD (total, proteus.foundry.vm.Player)
                B_FAIL, B_FIZZLE (archaeon/campaign5/repb)
  environment   W0, 16 train episodes (family train, index 1), rng 0
  per cell      viable share (answers >= 1 ask), floor share (reward per
                ask >= 3/16), mean reward, trapped share, faults > 0 share

PREDICTIONS WRITTEN TO BE LOST
  P1  raw x OLD == valid x OLD within the band on viable and floor shares
      (under the total interpreter a uniform word IS a uniform in-range
      word after the modulus; the generator cannot matter there).
  P2  valid x OLD == valid x B_FAIL == valid x B_FIZZLE within the band
      (a valid program is its own canonical form; only run-time
      self-modification can separate them: reported as the residual).
  P3  raw x B_FAIL viable share = 0 (+-.01); raw x B_FIZZLE viable share
      < raw x OLD viable share by more than the band (the representation,
      not the generator, kills raw programs).
  P4  injected(2) x B_FIZZLE viable share > injected(2) x B_FAIL viable
      share by more than the band (recovery is real at the population
      level) and < valid x B_FIZZLE (a fault costs something).
  READ: the representation effect = valid x B_* minus raw x B_* at fixed
  generator distribution under OLD (P1); the generator effect = zero
  under OLD (P1) by construction. If P1 fails the old campaign's
  generator was not neutral and every C4 census carries that.

CONTROLS
  positive   injected(2) x B_FAIL trapped share >= .50 (C5-03 F3 read .84)
  identity   valid x OLD reward equals valid x B_FAIL reward program for
             program on non-writable programs (100%)
  determinism  seed 1 cells re-evaluated equal
DISPOSITION: a table; P1-P4 each PASS/FAIL; INSTRUMENT_INVALID on a
control failure. No mechanism claim.
