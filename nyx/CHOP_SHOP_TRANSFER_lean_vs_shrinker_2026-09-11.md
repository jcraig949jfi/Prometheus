# Transfer assessment: did Lean teach Nyx to chop machinery, or to chop Lean?

Date 2026-09-11. Ruling: roles/Nyx/prompts/2026-09-11_ruling_proceed_n1/.
Compared: nyx/specimens/lean_simp (cuts.json at 1a54d02d2) and
nyx/specimens/hypothesis_shrinker (cuts.json, CUT-2). Numbers are cutledger
output; K statuses are the ledger's knife_application with evidence. No
scalar score. The ledger, not this file, is the record.

## The comparison ledger

    quantity                                  lean_simp            hypothesis_shrinker
    candidates at CUT-1                       23                   18
    ORGAN at CUT-1 -> last cut                8 -> 4 (CUT-3)       7 -> 6 (CUT-2)
    inherited rate at CUT-1                   20/23 = 0.87         10/18 = 0.56
    boundaries drawn ACROSS defs at CUT-1     3                    8
    inherited-and-supported (live, last cut)  0                    2  (c03 find_integer, c07 shrinking/)
    inherited-and-falsified                   0                    0
    not-inherited-and-supported               0                    3  (c01, c08, c19)
    untested boundaries (live, last cut)      all 28               14 of 19
    literal unknowns at CUT-1                 0                    14
    unknown -> known (receipt-backed)         0 (metric defective) 5
    preregistered composite passes?           NO (both transitions) YES (CUT-1 -> CUT-2: 1 / no verbosity / 5)
    executable contact before paper attack?   NO (CUT-3 after CUT-2) YES (switches after CUT-1)
    kind changes by argument (paper)          7 (CUT-2)            0 (the paper attack changed a scale note)
    kind changes by experiment                1 (CUT-3)            1 (c08 -> COUPLED)
    PERTURBED boundaries found                2 (c29 c30)          1 (c19)
    negative control that did not fire        1 (c23: hidden route) 0 (all negatives behaved as read)
    null configuration null?                  NO (eq_self hidden)  YES (N-c)
    foreign callee altered the boundary?      YES (c30 unifier)    NO (c12 named, not observed)
    independent-of-ancestor tests RUN         0 of 4               3 of 6 (c01 c03 c07)
    cheat controls fired / did not / not run  1 / 1 / 7            3 / 1 / 4
    consumer worst case reproduced?           n/a                  YES (Techne target 7, size 9 vs 5)
    consumer return                           1 (#182, 0.5 h)      none yet
    time from receipt to first delivery       ~2h40m               (deliveries posted after this file)

## The ruling's eleven questions

1. Which knife rules transferred?  K1 K2 K3 K4 K7 K8 K9 K10 FIRED with
   evidence in the ledger. K3 is the one that mattered: the only kind
   change again came from execution, and this time it came BEFORE the
   paper attack, so the paper attack had nothing left to invent.
2. Which were Lean-specific?  K6 (null configuration) and K5 (foreign
   callee) were APPLIED and DID NOT FIRE: the shrinker's Phase.shrink-off
   run returned exactly the first example, and the named callee (engine
   cache + DataTree) showed no participation. They are not Lean-specific
   in form -- they are checks that can come back negative. They stay.
3. Which failed to fire?  K5, K6 (above). Neither was wrong to run; each
   cost one block of the controls script.
4. Which produced false suspicion?  K5 predicted (P5) that the DataTree
   would shape what the shrinker explores; not observed. K1's DISCOVERED
   stamps on c06 (budget) and c13 (heuristics) united defs into a
   POLICY, not an organ -- cross-def cutting produced two policies and no
   falsified boundary. Mild.
5. Did executable contact again change the cut more than textual
   analysis?  YES, and more cleanly: 1 kind change from P-b, 0 from the
   paper attack. On Lean the paper attack made 7 changes and falsified
   nothing; here it was run second and had nothing to change.
6. Did Nyx discover machinery below inherited names?  Partly. c01 (the
   acceptance shape shared by two files) and c19 (label alignment) are
   below any name. c02 (the order across two files) is real but Nyx could
   not decide organ vs data. c08 and c09 united named passes by an idea;
   c08's union was SUPPORTED by P-b, c09's is untested.
7. Did Nyx merely invert the bias and cut across valid boundaries?  Two
   of the most useful organs (c03 find_integer, c07 the shrinking
   package) are INHERITED and now SUPPORTED by standalone runs: the
   programmer's boundaries were the mechanistic ones and Nyx kept them.
   Zero inherited boundaries were falsified. The cross-def cuts that
   were tested (c01, c08) held. The ones untested (c02, c09, c10) are
   where an inverted bias would hide; they are marked UNTESTED, not
   claimed.
8. Did explicit "unknown --" improve epistemic bookkeeping?  YES, by the
   only test available: the preregistered composite became attainable
   and passed (5 fields moved from unknown to a receipt-backed number).
   On Lean the same composite failed for want of literal unknowns.
9. Did the negative control reveal hidden machinery?  NO. Every negative
   behaved as read (N-a fired, N-b/N-f confirmed local minima, N-c null
   was null). The hidden-machinery finding (c19) came from a POSITIVE
   that failed to fire on the consumer's strategy (P-b) against one
   that fired on a plain strategy (N-g). K4 stays; the lesson is that
   the consumer's own fixture is the strongest control available.
10. Did the foreign-callee search materially alter the specimen
    boundary?  NO (see 2). It did produce the one CUT-1 COUPLED_CLUSTER
    (c12) honestly labelled as outside.
11. How many surviving ORGANs have evidence for independent behaviour?
    3 of 6 (c01 via common.Shrinker, c03, c07), all run with no engine
    imported, receipts in ablations/. Lean: 0 of 4.

## Answer to the question

Lean taught Nyx three things that transferred and one that did not.
Transferred: run the switches first (K3), say "unknown" (K2), stamp
origin at drawing (K8) -- each changed a number on the second specimen
in the direction the rule promised. Did not transfer as a FINDING: the
expectation that a null configuration hides machinery and that a foreign
callee is load-bearing -- both true of Lean, both false here. That is
the correct outcome for a rule: it ran and came back negative.

What Nyx did NOT learn from Lean and had to be told (ruling): that a low
inherited rate is not the goal. The second specimen's two best-supported
organs sit on inherited boundaries.

What remains unlearned: c02, c04, c09 are ORGAN with UNTESTED boundaries
-- three records that a consumer or a pass-list harness must test before
anyone should read them as organs. P7 predicted <= 2 survivors and 6
survived; Nyx again predicted a harsher knife than she used. Two
specimens, same miss. That is now a pattern in the calibration ledger.

## What the consumer test says that neither specimen's cut says

The Chop Shop's product is not these six records. It is one reproduced
consumer failure (Techne's target 7) with a MECHANISM-level account of
why it happens (the descendant pass needs labels the consumer's strategy
combinators do not record in the needed shape) and one PRESSURE stated
in the consumer's own order that a hostable world can pay for. Whether
Proteus or Vivarium can use either is theirs to say.
