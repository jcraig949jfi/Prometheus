+=====================================================================+
|  C4-04 -- ADDRESSING DAMAGE: PREREGISTRATION                          |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
+=====================================================================+

QUESTION (directive)
  How much brittleness comes specifically from references destroyed by
  insertion, deletion or displacement?

THE REPRESENTATION FACTS (before any row)
  The frozen ISA has ONE statically resolvable reference kind: the
  control instructions JMP / JZ / JNZ, whose operand is a SIGNED RELATIVE
  offset in instructions (ip = ip + 4*off mod tape_words). LD/ST address
  the tape through register contents (data-dependent, not static). The
  grammar's length-changing operators (insertion, deletion, duplication,
  movement, splice) shift instruction positions with NO offset fix-up, so
  a jump whose span crosses the edit point lands on a different
  instruction afterwards.
  The directive's comparison ("position-sensitive reference semantics
  versus relational / locally recoverable semantics") needs two addressing
  modes. This ISA has one (relative offsets); an absolute-address jump
  or a label/template mode does not exist and would be a new primitive.
  The executed comparison is therefore REPRESENTATION_BLOCKED, recorded.
  The measurable part -- how much of the loss under length-changing
  edits co-occurs with a broken reference -- is preregistered here on
  the committed C4-01 rows.

METHOD (static; no evaluation; committed rows only)
  For every applied C4-01 child of a length-changing operator,
  regenerate the child (seeds), verify its digest equals the committed
  child_digest, and for every control instruction at parent index i that
  is statically reachable in the parent (grammar.static_reachable):
    old target   t  = (i + off) mod total, content = the 4 words at t in
                 the parent (zeros beyond the genome: NOP-land)
    new position i' = map_op(i) where map_op is the operator's exact
                 index map (insertion/duplication: shift >= pos by k;
                 deletion/splice: remove [pos,pos+k), shift the rest by
                 -k or k2-k; movement: remove [src,src+k) then insert at
                 pos), or REMOVED if the jump itself was cut
    new target   t' = (i' + off) mod total, content in the child
    BROKEN iff content(child, t') != content(parent, t)
  Per child: n_refs (reachable jumps in the parent), n_removed, n_broken,
  ref_broken := n_broken > 0, ref_removed := n_removed > 0. Baseline:
  the length-preserving operators (replacement, operand_perturbation,
  reference_redirection, region_swap, randomization, unreachable_removal
  (length-changing but removes only unreachable instructions),
  config_perturbation) with the same predicate (map = identity except
  region_swap, whose two regions are swapped in the map).
  Join with the committed class D and displacement.

MEASUREMENTS (Wilson bands throughout)
  per length-changing operator: P(ref_broken), P(ref_removed), mean
  n_broken / n_refs; P(loss = D2 or D3 | ref_broken) vs P(loss | refs
  intact); the same for displacement > 0 and for the coherent share
  (D3/D4/D6/D7 or D5 with displacement > 0); pooled over the five
  operators; per stratum. Parents with zero reachable jumps form their
  own row (no reference to break) and are the natural negative control:
  their loss under the same operators is the no-reference baseline.

PREDICTIONS (written to be lost)
  P1  among length-changing edits, P(loss | ref_broken) - P(loss | refs
      intact) >= 0.10 pooled
  P2  parents with zero reachable jumps lose LESS under length-changing
      edits than parents with >= 1 (difference >= 0.10)
  A lost P1 with intact-loss high says the brittleness is not in the
  references; a lost P2 says jump-free programs are no more robust.

CONTROLS
  positive   a constructed parent (JMP at 0 with offset +2 to a
             distinct instruction) under an insertion at index 1 reads
             ref_broken; under an insertion at index 3 reads intact
  negative   identity child: n_broken 0 on every parent (57/57)
  integrity  regenerated digests equal committed (all applied children
             of the seven operators considered)
  cheat      a hand-set row with ref_broken and D7 counts coherent

DISPOSITIONS
  executed comparison of addressing modes: REPRESENTATION_BLOCKED.
  measurable part: SUPPORTED if P1 holds (references carry >= 0.10 of the
  loss difference); NEGATIVE if P1 is lost (brittleness is elsewhere);
  INSTRUMENT_INVALID on a control or integrity failure. Both P1 outcomes
  are results; neither changes the ISA.

RECORDS
  one engine world; one observation per operator plus one for the
  no-jump parents; rows.json with every child's reference facts joined
  to its committed class.
