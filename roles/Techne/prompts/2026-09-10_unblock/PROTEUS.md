PROTEUS -- A PROGRAM-SPACE SHRINK TARGET (from the operator, 2026-09-10)
Read techne/acquisition/fixtures/hypothesis_h1_minimiser.json.

Techne qualified Hypothesis's shrinking as a witness-minimiser over ASSIGNMENTS
and it is sound: 44/44 shrunk witnesses still witnesses under
proteus.eval.boolean.truth_table, all minimal under a declared order. Techne
also recorded the honest limit -- on 3 inputs there are 8 assignments, so
enumeration is cheaper and exact, and the qualification establishes SOUND, not
USEFUL. Minimising PROGRAMS is where a minimiser would earn its place.

DELIVER (clears TECHNE-12)
1. a Hypothesis strategy over your Boolean PROGRAM space -- the bounded typed
   grammar, not assignments -- at the declared interface version.
2. the VALIDITY PREDICATE a shrunk program must still satisfy, in your code, so
   the post-condition is yours rather than Techne's guess: a shrunk
   counterexample must still be a counterexample under your evaluator.
3. the size order you want minimised, stated. Hypothesis shrinks toward its own
   notion of simplicity; if yours differs, say so and Techne measures agreement
   instead of assuming it.

REPORT: the strategy, the predicate, and one program you already know shrinks,
so the first run has a known answer to be scored against.
