+=====================================================================+
|  C4-03 -- LOCAL FAILURE VS GLOBAL DEATH: PREREGISTRATION             |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
+=====================================================================+

QUESTION (directive)
  When one edited operation becomes invalid, is search better served by
  killing the program variant (HARD) or by letting the invalid operation
  alone do nothing while execution continues (FIZZLE)?

THE SUBSTRATE FACT THAT SHAPES THIS SLOT (D4-002)
  The frozen interpreter is TOTAL: an opcode word outside the 25-entry
  table is reduced modulo 25 and executes as that opcode; operand and
  address words are reduced modulo n_regs / tape_words by the PUBLISHED
  ISA semantics; jumps wrap. There is no invalid operation and no fault
  status. The substrate is FIZZLE-everywhere by construction, and a HARD
  condition cannot be EXECUTED without a new termination status, which
  is a new ISA primitive and forbidden during the campaign.

ARMS
  HARD (executed)   REPRESENTATION_BLOCKED, recorded as such. No row.
  HARD (static proxy)  a child is "would-be-fatal" if it carries an
                    out-of-table opcode word (word >= 25 at an instruction
                    start). Two readings, both reported:
                      fatal_present    anywhere in the genome
                      fatal_reachable  at a statically reachable instruction
                                       (grammar.static_reachable, initial
                                       tape; unsound if code is rewritten)
                    Operand/address words are NOT counted: their reduction
                    is defined semantics, not an invalid operation.
  FIZZLE (executed) the actual substrate: every C4-01 child's measured
                    class D0..D7 and displacement (committed rows,
                    attempts/a02/children.json.gz).

METHOD
  Regenerate every C4-01 child deterministically (same seeds, same
  operators, same parents; grammar.mutate) WITHOUT re-evaluating; verify
  the regenerated child's digest equals the committed child_digest (join
  integrity; any mismatch = INSTRUMENT_INVALID). Compute the two fatal
  predicates on every child and on every parent. Join with the committed
  class and displacement. Same for C4-02's children by radius (fatal mass
  as a function of radius).

MEASUREMENTS (per operator, per stratum, pooled; Wilson bands)
  P(fatal_present), P(fatal_reachable) among applied edits; the parents'
  own fatal predicates (a HARD substrate would have killed them at start).
  Among would-be-fatal children (reachable reading; present reading
  beside it), the FIZZLE class distribution:
    -> D2                         mass HARD would kill that FIZZLE keeps INERT
    -> D5 with displacement 0     silent (the fatal word never mattered)
    -> D5 with displacement > 0   neutral but behaviourally distinct
    -> D3, D4, D6, D7             coherent, non-trivial variation
  COHERENT SHARE := P(D3 or D4 or D6 or D7 or (D5 and displacement > 0)
                       | would-be-fatal)
  The same shares among NOT-would-be-fatal children, as the contrast.

VACUITY CHECK (annotation 2026-09-18 06:35Z, before any row; found by the
runner's self-test on a synthetic draw and confirmed on the 57 parents:
932 of 932 instruction words are out of the 25-entry table -- the foundry
writes uniformly random 32-bit words and the interpreter's modulo IS the
decode, not an insulation layer over a valid instruction set)
  If P(fatal_present | parents) >= 0.9 the static proxy is VACUOUS: "would-
  be-fatal" has no discriminating extension, and the proxy arm is recorded
  REPRESENTATION_BLOCKED with the measured number, beside the executed
  HARD arm. The share tables are still produced and committed, labelled
  uninformative (they partition on a predicate that is true everywhere).
  This is the slot's result: on this substrate there is no valid/invalid
  distinction for an insulation rule to act on; C4-07 ("cost the
  fizzle event") and C4-08 ("remove free semantic insulation") inherit
  the same fact and are re-premised in their own preregistrations.

PREREGISTERED READINGS (all three are results)
  PROXY_VACUOUS                          P(fatal_present | parents) >= 0.9
  FIZZLE_PRESERVES_COHERENT_VARIATION   coherent share among reachable
        would-be-fatal children >= 0.10 with Wilson lower bound >= 0.05
  INERT_CONVERSION                       otherwise (FIZZLE turns would-be
        fatal programs into inert ones and has not improved evolvability;
        the directive's critical distinction)
  Prediction written to be lost: coherent share among would-be-fatal
  children is LOWER than among non-fatal children by >= 0.10 (an
  out-of-table word is more often a wrecked instruction than a harmless
  one).

CONTROLS
  positive   an injected out-of-table opcode word at instruction 0 of a
             copy of each parent reads fatal_present AND fatal_reachable
             (57/57) -- the detector can fire
  negative   the identity child of every parent carries exactly the
             parent's predicates (57/57)
  integrity  regenerated child digest == committed child_digest for every
             applied C4-01 child (5,472/5,472) and C4-02 child (2,280)
  cheat      a hand-set fatal row with class D7 counts in the coherent
             share (classifier reads the field it claims to)

LIMITS (stated before any row)
  Static proxies over-count (a reachable out-of-table word may never
  execute at runtime because of data-dependent halts) and the "present"
  reading over-counts more. Neither is an executed HARD arm. What this
  slot can say: how much of the substrate's measured variation SITS ON
  fizzled operations, and of what kind. What it cannot say: what a real
  HARD interpreter would do to search.

DISPOSITIONS
  HARD executed: REPRESENTATION_BLOCKED (recorded, not converted into a
  substrate change). Proxy comparison: SUPPORTED if the reading is
  FIZZLE_PRESERVES_COHERENT_VARIATION; NEGATIVE if INERT_CONVERSION;
  INSTRUMENT_INVALID on any control or integrity failure.

RECORDS
  One engine world; one observation per operator (aggregate over its
  children) plus one for parents and one per C4-02 radius; rows.json with
  every child's predicates joined to its committed class.
