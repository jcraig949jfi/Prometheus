# PROTEUS-46 (second half) -- PREREGISTRATION, committed before any child is generated

    seat      Proteus[m2-7d051790]; worktree proteus-boot-2026-09-17
    question  Does the graph grammar (proteus.graph_grammar.v1, connectivity edits) change the
              SEARCH GEOMETRY around the same programs that grammar v0.4 (position edits) sees as a
              cliff? C3-SFE-02 measured, from evolved W2_K2 shelf organisms: 1 useful child in 4,800,
              0.64 neutral / 0.36 destructive, 0 of 480 greedy 3-step paths reaching the summit.
    why       operator ruling 2026-09-18: graph-dependent Deep Frontier transformations are locally
              gated on this verdict; Archaeon's loop reads a verdict file.
    verdicts  CLIFF_DOES_NOT_SURVIVE | CLIFF_SURVIVES | INDETERMINATE  (semantics: s5)

## 1. Parents (hand-written, one per substrate, expressiveness already shown equal)

    one_value  the shelf strategy: store every PUT in one slot; answer every ASK from it. Scores exactly
               3/6 on the two-key probe on both substrates (witness controls). This is the C3 analogue:
               a one-value memory whose two-value improvement exists 12 instructions / 12 nodes away.
    keyed      the two-value memory, 6/6 and 16/16 on both substrates (the destructive-rate parent).
    v0: proteus/eval/keyed_memory_witness.py (one_value_genome, keyed_memory_genome(48))
    graph: proteus/graph/witness.py (one_value_manifest, keyed_memory_manifest)

Limits declared: hand-written programs, not evolved organisms; a neutral world-free probe, not
W2_K2; the graph parents' wiring is one hand-chosen topology of the same function. The result is
about THIS pair of programs on THIS probe; it is the falsifier the profile itself declared (review
s7; GRAPH_ORGANISM_V1.md s5), not a claim about worlds.

## 2. Measurement

    probe          two_key_episode (6 asks) + all_keys_episode (16 asks); score = correct asks, 0..22;
                   the two-key score (0..6) is the primary because the one-value parent sits at 3 of it
    children       per operator, K = 400 children of each parent (seeded, SplitMix64; child i uses
                   seed_from("p46", substrate, parent, operator, i)); operators = every operator of
                   the grammar (v0.4: 12; graph: 13) -> 4,800 v0 children and 5,200 graph children per
                   parent; identity children (post_hash == pre_hash) counted and excluded from shares
    classes        from the one_value parent (score 3 on two_key):
                     USEFUL       two_key score > 3
                     GRADED_DOWN  two_key score in {1, 2}          (bounded, non-catastrophic loss)
                     DESTROYED    two_key score == 0
                     NEUTRAL      two_key score == 3 AND identical outputs on both probes
                     NEUTRAL_DIFF two_key score == 3 AND different outputs
                   from the keyed parent (score 6): DESTROYED (0), GRADED_DOWN (1..5), NEUTRAL, NEUTRAL_DIFF
    walks          from one_value: 200 random 3-step walks per substrate (operators drawn by their
                   masses), count reaching 6/6; 100 GREEDY 3-step paths (each step: 50 children, keep
                   the best two_key score, ties -> lowest ops), count reaching 6/6
    noise floor    every share computed on two disjoint seed batches (A: i < 200, B: i >= 200) per
                   substrate; the within-substrate |A - B| difference is the floor a cross-substrate
                   difference must exceed (C3-SFE-07's lesson)
    stratified     every share also per operator, so the verdict can name WHICH operators carry it

## 3. Pre-registered verdict rule (primary = one_value parent, two_key probe)

    CLIFF_DOES_NOT_SURVIVE  iff  useful_share(graph) >= 5 x useful_share(v0)  (or >= 5/5,200 when
                                 useful_share(v0) == 0)
                            AND  graded_share(graph) >= 2 x graded_share(v0)
                            AND  both differences exceed the within-substrate noise floor
    CLIFF_SURVIVES          iff  useful_share(graph) <= useful_share(v0) + floor
                            AND  graded_share(graph) <= graded_share(v0) + floor
    INDETERMINATE           otherwise (reported with every number; no verdict is forced)

The walks are SECONDARY: reported with the verdict, never moving it. A secondary that contradicts the
primary is written down as a contradiction, not resolved here.

## 4. What each verdict means downstream (operator ruling 2026-09-18, verbatim in
##    roles/Proteus/prompts/2026-09-18_campaign6/02_OPERATOR_RULING_G6-0_PROTEUS_AND_46_SEMANTICS.md)

    CLIFF_DOES_NOT_SURVIVE  graph transformations become EXECUTABLE
    CLIFF_SURVIVES          those transformations are FALSIFIER_FAILED / blocked AS FORMULATED; they are
                            retirement candidates under condition A ONLY IF the registered neighbourhood
                            is exhausted; otherwise a REOPEN condition stands: a materially different
                            graph topology, mutation operator, developmental regime, or representation
    INDETERMINATE           blocked as formulated; the file names the number that would decide it

The verdict file (proteus/round2/PROTEUS-46_FALSIFIER.json) therefore carries: verdict,
falsifier_status (PASSED | FALSIFIER_FAILED | INDETERMINATE), neighbourhood_exhausted (false: one
hand-written parent pair on one probe cannot exhaust anything), reopen_conditions (the four the
ruling names), and every number in s2 with its floor. Archaeon's loop should read `verdict` and
`falsifier_status`, never infer retirement from this file.

## 5. Self-dissent, before the run

- The graph one_value parent was wired by the same hand that hopes the graph wins; a different
  wiring of the same function could sit in a different neighbourhood. Mitigation: the topology is
  the SAME node set as the keyed parent minus two address edges, so the improvement is two edge
  retargets away by construction -- which is exactly what the flat program also has (two operand
  words). Stated so a reviewer can reject the pairing.
- K = 400 per operator is chosen to match C3-SFE-02's 400 per parent; with 13 operators the graph
  total is 5,200 vs 4,800 -- shares, not counts, are compared.
- A verdict of CLIFF_DOES_NOT_SURVIVE on a hand-written pair does not predict a world; it only
  unblocks the transformation that will measure the world.
