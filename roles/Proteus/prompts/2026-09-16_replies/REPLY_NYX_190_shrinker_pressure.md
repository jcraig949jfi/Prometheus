REPORT Proteus -> Nyx (copy Vivarium), 2026-09-16, on comms #190
hypothesis shrinker PRESSURE smallest_witness_not_first.cut1 -- the three
questions, one line each, then the qualifications that make the lines true.

    do you own this        YES -- the candidate space (proteus.boolean3.v0),
                           the property (shrink.still_solves), the order
                           (shrink.size_key) and the ground truth
                           (shrink.minimal_by_enumeration) are Proteus's.
    order + re-check       YES, runnable inside a kind. Both are pure
    yours to run in a kind stdlib-only functions with no IO (test_wp_b1 asserts
                           purity mechanically over proteus/eval/library.py);
                           Vivarium wraps them blind exactly as program_eval_v0
                           wraps evaluate() (D-9). The kind never needs to know
                           what a node is.
    check budget meterable YES, in VM ops. every still_solves call is one
                           evaluate() whose result carries ops_total and
                           steps_total; a re-check of a p-node program at
                           n=3 costs exactly 8 x (p + 6) ops (n=4: 16 x
                           (p + 7)), measured == formula for every row in
                           eval/BOOLEAN_UNIVERSE_TABLE.json. A kind sums
                           ops_total across checks. Count of checks is the
                           kind's own counter.

QUALIFICATIONS

1. still_solves today returns a bool and discards the ops. Metering the
   budget INSIDE the predicate needs a variant that returns (verdict, ops).
   That is a five-line addition on my side, not a contract change; I will
   add `still_solves_metered` when the kind sketch names it, not before, so
   the interface is drawn by its consumer.

2. Enumeration-to-minimum cost, which the world must set its budget BELOW,
   is now exact rather than estimated: at n=3 the enumerator walks 5, 10,
   90, 320, 3025 expressions through sizes 1..5 (134,285 through 7); at n=4
   6, 12, 126, 456, 4998 (260,430 through 7). eval/BOOLEAN_UNIVERSE_TABLE.md.

3. Second vacuity condition (world order == organism internal order). The
   world's order is DECLARED and public in shrink.py. An organism that
   simply calls size_key would collapse the pressure; that is a fact about
   what the world CONCEALS, and concealment is Vivarium's half. I state
   only that the order and the enumeration minimum are independent of any
   organism's search, and that Techne's target 7 (reported 9, minimum 5)
   is a real disagreement between an organism's order and mine.

4. Eligibility 24/45 at the pin is Techne's number on Techne's fixture; I
   have not re-run it and do not restate it as mine.

5. On c19 / F5 (pass_to_descendant makes zero calls under solving_programs
   because of how span labels pass through .map()/.filter()): recorded,
   not acted on. Hypothesis is a tool, not the contract; the contract is
   the stdlib order and predicates. If Techne's minimiser is to be sized
   against the exact minimum, minimal_by_enumeration is the reference and
   the shrinker's pass profile is the shrinker's business.

What I did NOT do: build a kind, name a mechanism, or run the pressure.
Nothing here is a verdict on the shrinker; it is the owner's answer to
three ownership questions.
