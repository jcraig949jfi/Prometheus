# hypothesis shrinker -- the cuts

Currency: 2026-09-11. Ledger: cuts.json. CUT-1 is never rewritten.

## Flow log (K1: bodies read sequentially, no def-grep; one entry per window)


Read 2026-09-11 23:0x-23:4x UTC, in this order, sequentially, bodies not
skeletons: shrinker.py 1-400, 401-800, 801-1200, 1201-1600, 1601-1953;
shrinking/common.py, integer.py, ordering.py, collection.py; choicetree.py;
junkdrawer.find_integer (located by the NAME the flow gave, then read);
choice.py 10-330, 331-637; engine.py cached_test_function 468-540,
shrink/new_shrinker/passing_choice_sequences 1759-1800,
shrink_interesting_test_cases 1678-1720 (located by name from the flow);
data.py Span 169-260; datatree.simulate_test_function; _settings.Phase.
Then the CONSUMER: proteus/eval/hypothesis_strategy.py, proteus/eval/shrink.py.
NOT read: floats.py, bytes.py, string.py shrinkers; datatree beyond
simulate; data.py beyond Span; providers; the database; engine run loop.

W1 shrinker 1-400.  IN: engine, initial ConjectureData, predicate,
   allow_transition, explain flag.  STATE: shrink_target (best so far),
   derived-value cache invalidated on target change, shrinks count,
   max_stall=200, per-pass stats, a FIXED LIST of 15 passes.  sort_key =
   (len(nodes), tuple(choice_to_index(node)))  -- "simpler" is shortlex
   over a per-choice index computed OUTSIDE this file (choice.py); the
   docstring gives three human reasons for the order.  cached_test_function
   begins: prefix check against current nodes.
W2 shrinker 401-800.  FLOW of a candidate: reject if not shortlex-smaller
   BEFORE running; reject if any choice violates its constraints; call
   engine.cached_test_function (OUT of file); accept iff predicate AND
   smaller AND allow_transition.  shrink() = initial_coarse_reduction
   (reduce_each_alternative: an integer <= 10 with min 0 "looks like a
   one_of selector" -- knowledge about the STRATEGY encoding, not about
   choice sequences) then greedy_shrink = fixate over passes; StopShrinking
   on stall; profiling report; then explain(): vary each arg span 500x
   with random values (100 same-failures => "or any other generated
   value"), borrowing values from sibling spans first; uses
   engine.passing_choice_sequences (the engine's cache of VALID runs).
W3 shrinker 801-1200.  step(): each pass runs through a ChoiceTree
   (shrinking/choicetree.py): the pass's own decisions (chooser.choose)
   are enumerated once; exhausted branches are never retried; selection
   order = resume-from-last-prefix or random.  fixate_shrink_passes: loop
   until no pass ran; each pass until 20 consecutive no-progress steps;
   switch to random selection after 10; pad max_stall; reorder passes by
   whether they deleted; remove_discarded interleaved.  pass_to_descendant:
   replace a SPAN with a descendant span of the SAME LABEL (labels and
   spans are recorded by generation, in data.py -- foreign state).
   lower_common_node_offset: when several integer nodes changed together,
   lower their common offset via Integer.shrink (the standalone shrinker)
   -- an anti-zigzag escape; change tracking state.
W4 shrinker 1201-1600.  try_shrinking_nodes: replace nodes with n, then
   REPAIR: if the engine realigned a collection (string/bytes now too
   long) retry truncated; if nodes were lost, delete contiguous regions
   guided by span children; remove_discarded reads span.discarded set by
   REJECTION SAMPLING in strategies (foreign); node_program "X"*n deletes
   n contiguous nodes, made adaptive by find_integer (junkdrawer, OUT of
   file); minimize_duplicated_choices, redistribute_numeric_pairs,
   lower_integers_together, lower_duplicated_characters: values that
   cannot shrink alone are moved TOGETHER, each restricted to a window of
   3-4 nodes ahead ("to avoid quadratic behaviour" -- a locality prior).
W5 shrinker 1601-1953.  normalize_unicode_chars (NFKD/case tables);
   widen_to_span_with_recorded_value: replace a one_of span by a
   ValueHole so the STRATEGY re-encodes the value ("all knowledge of how
   to encode values lives with the strategies, not here" -- the authors
   draw a boundary); minimize_nodes dispatches per type to the standalone
   shrinkers Integer/Float/Bytes/String with try_shrinking_nodes as the
   predicate; try_trivial_spans: replace a span by index-0 choices;
   minimize_individual_choices with a size-dependency fixup (lower n by 1,
   then delete a span or node after it); reorder_spans via Ordering.shrink
   keyed by sort_key; run_node_program: a "mini-DSL" with ONE command.
W6 shrinking/common.py: Shrinker base = current value, predicate, SEEN
   set, consider(value): dedupe -> left_is_better -> predicate -> accept;
   run = short_circuit then run_step (once, or to fixpoint if full).
   integer.py: try 0,1; mask high bits; byte squeeze; shift right; subtract
   multiples of 2 then 1, all via find_integer.  ordering.py: sort whole
   first; then sort adaptive regions; then regions with a fixed centre.
   collection.py: all-zero; delete chunks from the back adaptively;
   reorder; shrink duplicates together; shrink each element.  NONE of
   these import the engine: they take a value and a predicate.
W7 choicetree.py: TreeNode with live_child_count; Chooser.choose walks a
   trail; finish() marks the leaf dead and collapses exhausted ancestors;
   DeadBranch aborts a step whose choices are all exhausted.
W8 junkdrawer.find_integer: f(1..4) linear, then exponential probe, then
   binary search; f(0) assumed true.  A PRIMITIVE used by every adaptive
   loop in the specimen.
W9 choice.py: ChoiceNode(type, value, constraints, was_forced); trivial
   iff value == choice_from_index(0); choice_to_index: integers zigzag
   around shrink_towards (clamped to bounds; the nearer bound decides
   which side runs out first), booleans 0/1 (or 0 if p is extreme),
   bytes/strings = collection_index (size class first, then lexicographic
   in the ALPHABET's shrink order: intervals.index_from_char_in_shrink_order),
   floats = sign bit + float_to_lex; choice_from_index is the inverse;
   choice_permitted checks constraints.  The ORDER lives here; shrinker.py
   only composes it shortlex.
W10 engine.py: cached_test_function: data cache keyed by choices; before
   running, tree.simulate_test_function(trial) REPLAYS the prefix through
   the DataTree (datatree.py) and returns a cached result if the whole run
   is known -- a candidate can be answered WITHOUT executing the test;
   ValueHole forces execution.  shrink_interesting_test_cases: Phase.shrink
   gate; MAX_SHRINKING_SECONDS deadline; re-run the failing example first
   and exit FLAKY if it no longer fails; predicate = same
   interesting_origin (or any INTERESTING if not report_multiple_bugs);
   targets shrunk in sort_key order.
W11 data.py Span: index into compact Spans arrays; label (opaque strategy
   origin), parent, start, end, depth, discarded (set by the strategy's
   stop_span(discard=True)), choice_count, children.  Spans are produced
   by GENERATION; the shrinker only reads them.
W12 consumer (Proteus): strategy = st.recursive(sampled_from(leaves),
   one_of(Not, And, Or, Xor)).filter(compiles); predicate still_solves
   (evaluator, full coverage); DECLARED ORDER (node_count, depth,
   canonical) with the explicit sentence "Hypothesis shrinks toward ITS
   OWN notion of simplicity ... THAT IS NOT THIS ORDER"; ground truth by
   enumeration to size 5.

## CUT-1 candidates (18), origin stamped at drawing (K8), disposition and reason

    id  origin      disp             boundary / reason
    c01 DISCOVERED  ORGAN            order-gated greedy acceptance: reject-before-run unless smaller; accept iff predicate AND smaller AND allowed. The SAME shape appears in shrinker.cached_test_function+incorporate_test_data and in common.Shrinker.consider (two files, one mechanism)
    c02 DISCOVERED  ORGAN            the simplicity order with its inverse: shortlex (shrinker.sort_key) over choice_to_index/choice_from_index (choice.py); crosses two files; carries the human prior "smaller index = simpler"
    c03 INHERITED   ORGAN            find_integer (junkdrawer): linear-then-exponential-then-binary search for the largest k with f(k); coincides with one def; every adaptive loop uses it
    c04 INHERITED   ORGAN            pass-step enumeration by ChoiceTree/Chooser: a pass's nondeterministic choices are enumerated once and never retried; coincides with module choicetree.py
    c05 INHERITED   POLICY           fixate_shrink_passes schedule: 20 failures per pass, random after 10, reorder by deletion, stall padding -- a schedule over c04 (the Lean c08 lesson applied at drawing)
    c06 DISCOVERED  POLICY           termination budget: max_stall adaptive (shrinker) + MAX_SHRINKING_SECONDS deadline (engine); crosses files; a budget, not a mechanism
    c07 INHERITED   ORGAN            standalone value shrinkers (shrinking/common + integer + ordering + collection + floats/bytes/string unread): value + predicate -> smaller value; coincides with package boundary; no engine import
    c08 DISCOVERED  ORGAN            span-structured passes (try_trivial_spans, pass_to_descendant, reorder_spans, remove_discarded, node_program deletions): united by the FOREIGN STATE they all read -- spans/labels/discarded recorded by generation
    c09 DISCOVERED  ORGAN            coupled-value passes (minimize_duplicated_choices, redistribute_numeric_pairs, lower_integers_together, lower_duplicated_characters, lower_common_node_offset): united by "values that cannot shrink alone shrink together", each with a 3-4 node locality window
    c10 DISCOVERED  UNRESOLVED       shape-repair after a size-controlling change (truncate realigned collections, delete lost regions, rerandomise-and-repair, size-dependency fixup): a cluster of fixes for the engine's realignment behaviour; organ or scaffolding undecided
    c11 INHERITED   UNRESOLVED       explain phase (_explain): sensitivity analysis over arg spans by random resampling; coincides with def _explain / Phase.explain; a different capability ("which parts do not matter") -- possibly a different specimen
    c12 DISCOVERED  COUPLED_CLUSTER  engine data cache + DataTree.simulate_test_function: a candidate is answered without running the test when its prefix is known; OUTSIDE the boundary; the K5 foreign callee named at prereg (P5)
    c13 DISCOVERED  POLICY           strategy-encoding heuristics: "integer <= 10 with min 0 is a one_of selector" (reduce_each_alternative) and ValueHole re-encoding by the strategy (widen_to_span_with_recorded_value); knowledge about the generator smuggled into the shrinker
    c14 INHERITED   SCAFFOLDING      per-pass statistics and the profiling report
    c15 INHERITED   SCAFFOLDING      choice_permitted validity gate
    c16 INHERITED   DATA             per-node constraints (shrink_towards, bounds, intervals with a char shrink order): the DATA the order reads; supplied by strategies
    c17 INHERITED   POLICY           what counts as "still failing": same interesting_origin; flaky exit if the re-run passes (engine)
    c18 INHERITED   SCAFFOLDING      node-program "mini-DSL" with exactly one command

Prompt-named failed-cut check (parser / simplifier / database / result):
none of the 18 is "the shrinker" as one box; c05 (schedule) is the nearest
and was dispositioned POLICY at drawing. The operator's word "SHRINKER"
denotes, on this cut, the class (c01+c05+c08+c09+c10+c13 live there),
the package (c07), and the phase (c17 gates it) -- three different things.

## CUT-1 numbers (cutledger, read after the records were written)

    candidates 18; ORGAN 7; POLICY 4; SCAFFOLDING 3; UNRESOLVED 2; COUPLED 1; DATA 1
    inherited-boundary rate 10/18 = 0.56        (P1 band 0.30-0.87: INSIDE; Lean was 0.87)
    literal-unknown fields 14                   (Lean CUT-1: 0)   K2 applied
    boundary_support: 18 UNTESTED               (switches not yet run)
    record bytes 38,860 over 7 organs           (Lean CUT-1: 49,587 over 8)

## SWITCHES AND CONTROLS (run BEFORE the paper attack; K3, K4, K6)

ablations/n1_controls.py in Techne's isolated env; RECEIPT_N1_2026-09-11.json;
16 blocks, 0 errors. Negatives first.
    N-a  standalone always-false            initial returned unchanged (Integer 1000; Collection (5,7,9))   FIRED as designed
    N-b  standalone local-minimum plant     1000 stays 1000; 5 unreachable (P3 CONFIRMED)
    N-b2 reachable control                  0 in 1 call
    N-e  find_integer non-monotone          3 (the local boundary), not 5+
    P-a1..P-a4 standalone positives         43 (14 calls); (1,2,3); [7] (11 calls); 37 (12 calls)   OUTSIDE THE ENGINE
    P-a5 cheat control (strict decrease)    488 232 104 52 50 48 46 44 43 -- strictly decreasing (first run of this
                                            block had a malformed check whose 'true' was vacuous; fixed, rerun)
    S-b  engine, shrink on                  first satisfying seen 362881 -> returned 1000
    N-c  engine, Phase.shrink EXCLUDED      returned 362881 == first satisfying seen   K6 DID NOT FIRE (null was null)
    N-d  engine, non-monotone, two seeds    283 and 325 (minimum 101 NOT reached by either); seed-1 gave 1291 in the
                                            first run and 283 in the second -- not run-stable; S-a (derandomize) stable
    S-a  derandomize vs seed                1000 == 1000
    N-f  engine local-minimum plant         1000 (the full pass set does not reach 5; P3 at engine level)
    N-g  structural positive                nested Not on a plain recursive strategy -> ('Not','x0')
    P-b  CONSUMER worst case, target 7      REPRODUCED: '(not (not (or (and x0 x1) (and x0 x2))))' size_key (9,5,...)
                                            vs enumerated minimum '(and (or x1 x2) x0)' (5,3,...). Profile: 132 calls,
                                            5 shrinks, 5/12 choices deleted; reorder_spans 2/2; minimize_individual
                                            48/0; try_trivial_spans 16/0; lower_integers_together 15/0; redistribute
                                            14/0; node_program X..XXXXX 23/0; minimize_duplicated 5/0;
                                            pass_to_descendant NOT IN THE PROFILE (0 calls).
The one cut-changing result: pass_to_descendant fires on N-g's plain st.recursive
and makes no calls on Proteus's st.recursive(...).map()/.filter() strategy. The
structural pass exists; the LABELS it needs are not recorded in the shape it
requires by that combinator chain. P6 (the encoding decides what is reachable)
CONFIRMED on one target; whether it explains all 24/45 is NOT shown.

## CUT-2 (paper attack on what the runs left standing)

    id  CUT-1 -> CUT-2           support     reason
    c01 ORGAN -> ORGAN           SUPPORTED   standalone strict-decrease + never-adopt; independent test RUN
    c02 ORGAN -> ORGAN           UNTESTED    P-b shows the order's disagreement with the consumer but does not isolate it
    c03 ORGAN -> ORGAN           SUPPORTED   inherited AND supported: the def boundary is the mechanistic one
    c04 ORGAN -> ORGAN           UNTESTED    no exhaustion test run
    c07 ORGAN -> ORGAN           SUPPORTED   inherited AND supported: the package runs with no engine (P4 CONFIRMED)
    c08 ORGAN -> COUPLED_CLUSTER SUPPORTED   the foreign-state dependence is exactly what P-b exposed; applicability = passes x labels
    c09 ORGAN -> ORGAN           UNTESTED    fired on P-b (34 calls) and shrank nothing; own claim untested
    c12 COUPLED (P5 not observed: N-c returned the first example unchanged)
    c19 NEW PERTURBED DATA       SUPPORTED   label alignment between combinators and the descendant pass
    others unchanged.

CUT-2 numbers: candidates 19; ORGAN 7 -> 6; kind changes 1; new 1; materially
revised 1; bytes 38,860 -> 33,672 (-13%); VERBOSITY_FAILURE false; literal
unknowns 14 -> 9; unknown_became_known 5 (with receipt refs); independent-of-
ancestor tests RUN 3/6 (c01 c03 c07); cheat controls fired 3, did not fire 1
(c08's attribution control had nothing to attribute), not run 4.
Boundary categories over live candidates: inherited 10; independently
supported 5; inherited-and-supported 2 (c03 c07); inherited-and-falsified 0;
not-inherited-and-supported 3 (c01 c08 c19); untested 14.
Preregistered composite (revised > 0 AND no verbosity AND unknown->known > 0):
1 / false / 5 -> PASSES. First time in the Chop Shop.

Predictions: P1 CONFIRMED (0.56 in band); P2 CONFIRMED (order defined in
choice.py; shrinker.py only composes shortlex) -- but Nyx kept it ORGAN not
POLICY, so half-confirmed; P3 CONFIRMED (N-b, N-f); P4 CONFIRMED (P-a);
P5 NOT OBSERVED (N-c); P6 CONFIRMED on one target; P7 FALSIFIED (6 organs
survive, not <= 2).

No CUT-3: no consumer return on N1 and no patched-build ablation; the
stopping rule says CUT-3 waits. Natural stopping point reached.
