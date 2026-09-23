+=====================================================================+
|  C5-07 -- COST OF INSULATION: READOUT                                 |
|  Archaeon[m2-49ee5a4d]   2026-09-18 14:56Z   attempt of record a01   |
|  INSULATION_CHEAP                                                    |
+=====================================================================+

Ran because C5-06 read REAL_LOCAL_RECOVERY. Input: the 229 replicated
recovery children and their 44 parents. Control: each parent's second-
edit census here equals its C5-05 grammar-B FIZZLE rows count for count
(44/44). 1 engine record, 0 errors, 208 s. (Harness decl reading:
UNDERPOWERED by its row-pairing rule; the preregistered reading is K1-K3.)

  K1 compute   ops per episode, recovered child under FIZZLE over parent
               under OLD: median ratio 1.00; 2.2% of children cost more
               than 1.10x; 0.4% cost less than 0.90x.
  K2 fragility second single edit (grammar B, 12 x 8, FIZZLE) on the
               recovered child versus on its parent:
                 children neutral .532 [.525,.539] over 20,101 edits
                 parents  neutral .509 (weighted)   over 19,729 edits
                 diff +.023 (inside the band); per child: 64 more
                 robust than their parent by a band, 30 less.
               Cost (children below parents by > band): NO.
  K3 elsewhere 10 of 229 (4.4%) recovered children lose >= a band on
               another environment where the parent was above the floor
               (W1_d1 9, W2_K2 2).
  Beside them: C5-06's 154 replicated INSULATION_LOSS events -- the
  direct cost, paid by register-field faults.

READING
R1  A skipped fault is a free NOP: it costs no compute (the skip is one
    op like any other), it does not make the program more fragile to
    the next edit (if anything the hole is one more neutral site: +.023),
    and it rarely costs function elsewhere (4.4%).
R2  The insulation's real cost is not on the recovered programs but on
    the other class: instructions with a wrapped register field that
    worked under reinterpretation and are lost when skipped (154
    events). FIZZLE trades 229 saved opcode faults for 154 lost register
    faults on this grammar mix; under grammar B alone the trade is 15
    for 34 (C5-06), i.e. a net LOSS for the grammar evolution actually
    uses.
+=====================================================================+
