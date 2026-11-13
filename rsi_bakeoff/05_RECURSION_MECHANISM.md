# 05 -- The recursion mechanism

How the improver changes itself, how a changed improver improves again, and how large the effect can honestly be
expected to be. Notation is from `04_SELECTED_ARCHITECTURE.md`: L is the library, T the theory (laws), S the
schemas (law templates), K the fixed kernel.

## 1. What "the improver" is in this design

The improver is the procedure that turns a lifetime of experience into a new artifact:

```
IMPROVE(K ; L, T, S)  =  ( PROMOTE[T] ,  MINE[T, S] ,  GENERALISE )      run over the experience SEARCH[L, T] produced
```

The brackets are the point. Each operator's code is fixed in K, but what each operator does depends on content
the engine produced earlier:

| Operator | Its behaviour depends on | So a change to that content changes |
|---|---|---|
| SEARCH[L, T] | the library and the laws | which tasks get solved, and so what experience exists to learn from |
| PROMOTE[T] | the laws used to normalise programs | which shared structure is visible, and so which primitives are extracted |
| MINE[T, S] | the laws (it enumerates normal forms only) and the schemas (it conjectures from them) | which laws are found next, and at what cost |

Self-modification here means: **the improver's output is the bracketed input of the improver's next run.** No code
is rewritten. The honest name for this is a learner whose inductive machinery is parameterised by structured
content that it learns. Section 7 says why I think that is the right place to stop.

## 2. The three recursive paths

```
        +------------------------- R-C ---------------------------+
        |                                                          |
        v                                                          |
   [ schemas S ] --conjecture--> [ laws T about new entries ] --generalise--+
                                       |          ^
                              R-A      |          |  R-A: mining in normal form reaches larger terms
                          prune,invert |          |
                                       v          |
                                  [ SEARCH ] --collisions--> [ MINE ]
                                       |
                                  solutions
                                       |           R-B: normalise under T before compressing
                                       v
                                  [ PROMOTE ] --> [ new entries in L ] --> new laws are now needed --> (back to S)
```

| Path | Loop | Is the improver using its own product? | Expected size of effect |
|---|---|---|---|
| R-A | laws -> smaller search space for the miner -> more laws | Yes, directly | Small. About one size level in total, then it saturates |
| R-B | laws -> better extraction -> new primitives -> new laws to find | Yes, through the compressor | Unknown. It repairs a measured defect (3 of 4 mis-cut stones in Beta-04) |
| R-C | laws -> schemas -> cheap laws about each new primitive -> search can use and see through the primitive -> deeper solutions -> new primitives | Yes: the miner itself has been changed | Grows with library size and with the size of the laws that matter. Negligible when both are small |

R-C is the path the L3 claim rests on. R-A is the path the first experiment (M0) can test in a day.

## 3. The arithmetic of why a library alone stalls

These numbers are from committed measurements, combined by me. Treat the combination as a back-of-envelope model,
not a result.

**Measured.** In TFS-1, the number of Int-valued candidate programs grows by a factor of about 9.6 per size level
with no library, and about 11.4 with five entries (`TFS1_THROUGHPUT.json`: 563,912 to 5,379,790, and 1,602,560 to
18,231,562).

**Consequence.** With a budget of one million candidates, the search horizon is `ln(1e6) / ln(growth)`:

| Library | Growth per level | Horizon (size levels) at 1e6 candidates |
|---|---|---|
| none | 9.6 | 6.1 |
| 5 entries | 11.4 | 5.7 |
| 30 entries (extrapolated, growth near 20) | ~20 | ~4.6 |

So every entry shortens the horizon. Five entries cost 0.4 levels. Thirty would cost about 1.5 levels, which is
more than most abstractions give back. This is a mechanical reading of findings F7-F9: a library pays only for
tasks that use its entries, and taxes all the others.

**What the theory offers.** The probe (file 01 s6) found that at size 6 only about 1 in 14 Int candidates is a new
behaviour. Skipping the other 13 is worth `ln(14) / ln(9.6)`, about 1.2 levels. So a theory that captured most of
that redundancy would pay the tax of roughly two dozen entries.

Two honest limits on that sentence:

1. The redundancy measurement was made without a library. Whether terms that contain learned entries are as
   redundant is not known. R-C exists because I expect they are redundant only if the engine learns laws about
   the entries.
2. Per-task observational-equivalence pruning already removes this redundancy with no learning. Laws must beat it
   on total work, which they can only do by amortising across tasks, by being sound inside lambda bodies where
   that pruning is a heuristic, and by enabling inverse steps. File 06 makes that pruning the baseline.

**The growth condition.** Write `c` for the factor by which one level of abstraction shortens the programs of the
next rung, and `b_g` for effective growth per level at generation g. Reach in base-program size is roughly
`c^g * ln(B) / ln(b_g)`. Recursion is sustained while `c^g` rises faster than `ln(b_g)`. That needs two things at
once: the world must have a next rung that the new entries compress (`c > 1`), and the theory must keep `b_g` from
climbing with the library. Lose either and the gain ratio falls below one. This is the quantity the experiments
track, generation by generation.

## 4. Why schemas might matter, and when they will not

A law about a learned entry can be found in two ways.

| Method | Cost to find a law of size n in a language with m operators |
|---|---|
| Collision mining | Enumerate all terms up to size n: grows like `m^n` |
| Schema instantiation | Try each schema with each fitting operator or operator pair: grows like `|S| * m` or `|S| * m^2`, independent of n |

So the advantage of schemas is exponential in the size of the law and polynomial in the size of the library. But
it starts from nothing:

- A learned entry is one node. `L_a(L_a(x))` has size 3 in the promoted language. Collision mining finds a law of
  size 3 or 4 almost for free. For small laws about a small library, **schemas add nothing measurable.**
- Schemas begin to pay for laws of promoted size about 6 or more (distribution over a binary operator,
  cancellation with a side argument, commuting two learned entries), and once the library is large enough that
  enumerating to size 5 or 6 is itself out of budget.

That gives a falsifiable prediction with a threshold, rather than a general hope: there is a library size below
which the schema-equipped miner and the plain miner find the same laws at the same cost, and above which the
plain miner falls behind. M1 measures where that threshold is. If the tasks never push the library past it, R-C
is real but irrelevant, and the design reduces to Candidate A plus a pruning theory.

## 5. From generation 0 to generation 2, traced as a causal chain

Each arrow is a dependency that the falsification plan can cut.

```
Generation 0 lifetime
  SEARCH (plain)  --collisions-->  MINE (plain)  ----------------------->  T_1   base laws
                                                    T_1 --GENERALISE-->    S_1   schemas
  solutions --PROMOTE-->                                                   L_1   depth-1 entries

Generation 1 lifetime            (machinery now: SEARCH[L_1, T_1], PROMOTE[T_1], MINE[T_1, S_1])
  SEARCH[L_1, T_1] reaches tasks plain search could not          [cut: clamp T_1 out of search]
  solutions normalised by T_1 --PROMOTE-->  L_2 with depth-2 entries   [cut: compress without normalising]
  S_1 instantiated on L_1 and L_2 entries --> laws about them    [cut: clamp S_1 out of the miner]
  those laws --> T_2 ; T_2 --GENERALISE--> S_2

Generation 2 lifetime            (machinery now: SEARCH[L_2, T_2], PROMOTE[T_2], MINE[T_2, S_2])
  search prunes and inverts through learned entries using laws that only exist because of S_1
```

**The L3 event.** A second-order improvement has occurred when there is at least one law in T_2 for which all of
the following hold:

1. It mentions an entry of L_1 or L_2 (it is about learned vocabulary).
2. Its record says `found_by: SCHEMA:<id>`, and that schema has origin SELF, created in an earlier lifetime.
3. It passed the acceptance test, and removing it raises work on the evaluator's held-out families.
4. With the schemas clamped out of the miner, a generation-1 lifetime at the same work budget does not find it.

Conditions 1-2 are read from the ledger. Condition 3 is an ablation. Condition 4 is the clamp arm. Together they
say: machinery the engine built (a schema) was used by the engine's improver (the miner) to build further
machinery (a law) that helps. None of the four depends on anyone's opinion.

## 6. What the descendant can do that the ancestor cannot

| Capability | Generation 0 | Generation 1 | Generation 2 |
|---|---|---|---|
| Skip redundant base terms | No | Yes (T_1) | Yes |
| Recognise two differently written programs as sharing structure | No | Yes (normalise under T_1) | Yes, including through learned entries |
| Invert through a base operator | No | Yes, where a cancellation law was mined | Yes |
| Conjecture a law about a new primitive without enumerating | No | Yes (S_1) | Yes, with more templates (S_2) |
| Prune and invert through a **learned** primitive | No | No: no laws about entries exist yet | Yes, if R-C worked |

The last row is the difference between first-order and second-order improvement in this design. Generation 1 is
better than generation 0 because of what generation 0 learned. Generation 2 is better than generation 1 at
handling its own inventions, because of machinery generation 1 built with machinery generation 0 built.

## 7. Where the regress stops, and why I stop it there

Any self-improving system has a part that does not change. The question is where to put it.

| Option | What is fixed | Problem |
|---|---|---|
| Rewrite everything, including the rewriter | Nothing | No stable evaluator; the brief forbids it; Eurisko shows mutating heuristics mostly yields noise |
| Fix an outer optimiser, evolve an inner learner's parameters | The optimiser and the learner's form | Finding F10: the parameters turned out to be inert |
| **This design: fix the induction operators, let their structured inputs be learned** | Compression, collision mining, anti-unification, acceptance | The engine cannot invent a new kind of induction |
| Fix only an interpreter; represent induction operators as programs in the language and search for them | The interpreter | Searching for a compressor by enumeration is far beyond any budget here. This is the composition wall at the meta level |

The fourth option is the more ambitious and, I think, not reachable now. The third is the highest point at which
every self-change is still found by induction from evidence rather than by blind search. Its ceiling is explicit:
laws, and templates of laws. Templates of templates would add nothing, because a template over operator variables
is already as abstract as this language can state.

A possible later step toward the fourth option, flagged as speculative: pose "find a better scoring function for
candidate abstractions" as a synthesis task in the engine's own language, with the acceptance test as its
specification. Then the engine's search would be applied to a piece of its own improver. I do not include it in
M0-M2 because nothing in the record suggests such a search would find anything.

## 8. What this mechanism is not

- It is not open-ended. A fixed primitive basis has a finite stock of small laws; a foundry world has a finite
  depth of planted structure. The expected shape is a few generations of gain and then saturation.
- It is not discovery of learning algorithms. The learning algorithms are supplied (file 04 s7).
- It is not evidence about intelligence in general. It is a test of one causal claim: that learned content can
  become a necessary part of the machinery that learns further content.
- It does not escape the composition wall for mechanisms with no observable regularity. Laws are found from
  collisions; a structure that produces no collision and no compression is invisible to every operator here.

## 9. Predictions, stated before any run

| # | Prediction | If wrong |
|---|---|---|
| PRED-1 | Generation 0 rediscovers the foundry's hand-written rule families (its labels P1-P4, P6, P7) from collisions | The miner is broken or the probe set is poor. Fix before anything else |
| PRED-2 | Mining under T_1 at budget B finds few laws that plain mining at 2B does not (R-A saturates) | Pleasant surprise: R-A is stronger than I think |
| PRED-3 | Normalising before compression reduces mis-cut stones on the Beta-04 families | R-B is not a real path; extraction needs another repair |
| PRED-4 | With a library under about 10 entries, clamping schemas changes nothing measurable | Schemas matter earlier than the cost model says |
| PRED-5 | With a library over about 20 entries, the plain miner misses accepted laws that the schema miner finds | R-C does not exist at any scale reachable here. The L3 claim fails |
| PRED-6 | The gain ratio between generations is below one by generation 3 on foundry worlds | The world has more layered structure than expected, or the engine found structure the foundry did not plant |

PRED-2, PRED-4 and PRED-6 are predictions against my own proposal's stronger readings. They are listed so that a result
cannot be re-described afterwards as what was expected.
