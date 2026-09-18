+=====================================================================+
|  C5-03 -- REPRESENTATION QUALIFICATION: PREREGISTRATION              |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
|  Campaign 5, Phase B                                                 |
+=====================================================================+

THE CANDIDATE (archaeon/campaign5/repb/, Proteus's VM untouched)
  Representation B = the Proteus affordance table with a NARROW in-table
  encoding: an opcode word is defined iff < 25; a register field the
  opcode reads is defined iff < n_regs; any other word in a read field
  is a FAULT. Addresses formed from register contents and jump offsets
  stay modulo tape (values, not encodings); immediates are 32-bit;
  unread fields cannot fault.
    FAIL    first fault ends the whole evaluation (status trap, reward 0)
    FIZZLE  the faulting instruction is skipped and COUNTED; execution
            continues (faults, distinct sites, faulting ticks)
  canonicalize(P): the old program's meaning in the narrow encoding
  (opcode mod 25, read register fields mod n_regs). Under B it must
  behave exactly as P does under the old player.
  Generators: raw (the old uniform-word generator), valid (opcode and
  register fields drawn in range), injected(k) (valid + exactly k read
  fields pushed out of range). Grammar B = v0.4 with whole-instruction
  and field redraws in range; operand_perturbation unchanged (it is the
  operator that can carry a word across the boundary).

FIXTURES (thresholds fixed here; all measured WITHOUT fitness except F1,
which is an identity check, not a comparison)
  F1  canonical identity: for all 57 starting parents on their parent
      environment (16 episodes) and on W0 (16 episodes): reward per ask,
      ops and status counts under B/FAIL(canonicalize(P)) equal the old
      evaluator's on P, zero faults, canonicalize(P) statically all
      valid. PASS iff 57/57 on both environments.
  F2  static separability (N=200 per population, seed 1, old FOUNDRY
      knobs): share statically all-valid: raw <= .01, valid = 1.00,
      injected(k) = 0 with invalid count == k in >= .99 of programs, for
      k in {1,2,4}.
  F3  dynamic separability without fitness (four W0 episodes, FAIL):
      trap share raw >= .95, valid <= .10, injected(2) >= .50; pairwise
      total variation distance between FIZZLE fault-count histograms
      (bins 0 / 1-3 / 4-15 / 16-63 / 64+) >= .50 for raw-vs-valid,
      valid-vs-injected(2) and raw-vs-injected(2).
  F4  FAIL/FIZZLE coherence: for every program in the three
      populations, trapped under FAIL iff faults > 0 under FIZZLE
      (100%); and among injected(2) programs, some (>= .05) answer at
      least one ask under FIZZLE while every trapped FAIL evaluation
      answers none.
  F5  countable recovery: for injected(k) programs whose code region is
      NOT writable, distinct fault sites under FIZZLE <= k (100%). For
      writable ones the excess is reported (self-modification can mint
      faults at run time; that is a property, not a defect).
  F6  determinism: two evaluations of every program in F3 are equal.
  F7  undefined is undefined (a count, must be > 0): raw programs that
      answer an ask under the OLD evaluator but trap under B/FAIL.
  F8  grammar B crossing rate by operator over 1,200 children of valid
      parents (a measurement; recorded, no threshold).
  DISPOSITION: REPRESENTATION_QUALIFIED iff F1-F6 all pass and F7 > 0;
  otherwise REPRESENTATION_FAILURE and Phase B stops (D5-002 default 3
  if Phase A also returned OLD_SUBSTRATE_EXHAUSTED).

CONTROLS
  positive  a hand-made program with one out-of-range opcode word at
            its second instruction: FAIL traps at episode 0 tick 0 with
            reward 0; FIZZLE reports faults >= 1 and one fault site, and
            the program's remaining instructions execute.
  cheat     a valid program relabelled as injected(1) must FAIL F2's
            invalid-count check (the check reads the genome, not the
            label).
  old-VM    proteus.foundry.vm is imported but never modified: its
            file digest before and after the run is recorded.

EXECUTION PATH: the campaign harness (D5-001); wse_evaluate_v1 does not
exist for representation B and cannot (it wraps the old evaluator).
