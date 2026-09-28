REPORT -- persistence vs equal-information context; portable executable organs

1. WHAT I SET OUT TO TEST

The proposal under test says a persistent, growing library of executable procedures (the Voyager-style skill library) is a distinct scientific object, not just a way of managing context. The cheapest test that could kill it is this: with the same information and the same compute, does keeping acquired procedures as a persistent executable library beat keeping the same experience as raw context (episodes or demonstrations)? A related proposal asks whether acquired machinery can be packaged as "organs" (identity + description + executable payload + retrieval key). Such organs would have to stay useful when the payload is ablated, and when they are moved to another agent or another world. I built the smallest deterministic world without a language model that the proposal itself specifies. I ran the matched-information comparison, a closed-loop version with a late library swap, and the payload and transplant ablations this world can express.

2. WHAT I DID

Sources read (read-only clone):
- The ladder and experiment records in roles/Atlas/proposals/2026-09-21_prior_art_raid/{ENGINE_FIVE_EXPERIMENT_LADDER.md, EXPERIMENTS.jsonl} @ 2c7a19adb.
- The portable-organ section of roles/Chiron/prompts/2026-09-21_synthesis_directive/SYNTHESIS_DIRECTIVE.md @ 9e54a51ce.

No repository code was run, and I found no existing implementation in the repo. The nearest engine branch (origin/aphrodite/compounding-2026-09-27) has no library-vs-context test.

All code is new, in /home/jcraig/artemis-selftest/work/R-12:
- f50.py: world, controllers, memories (sha256 70a424ac281a...)
- phase1.py: matched-information test (1e6b70b91739...)
- phase2.py: closed loop plus swap and transplant tests (e13820901a64...)
- phase2bx.py: closed loop, context-only arm (e46d4708004e...)
- calib.py: budget calibration
- Outputs: phase1_*.json, phase2_*.json, phase2bx_*.json, p*.log, agg1.py

The world is generated synthetically by this code. No committed data and no holdout were used.

World:
- Tasks transform lists of integers using 14 primitives (rev, sort, inc, dbl, dedup, tail, cums, ...).
- Each world seed draws 10 hidden "motifs". A motif is a 3-primitive sub-procedure that cannot be reduced to 2 primitives.
- A task is a hidden program of 2-3 motifs, plus one extra "glue" primitive with probability 0.5. It is given as 5 I/O examples, and a solution must also pass 5 held-out examples.
- Four world seeds (1-4).

Controller: breadth-first enumeration over a set of tokens (the primitives plus whatever the memory supplies). Candidates that produce identical outputs are pruned. Every arm gets the same hard budget of 20000 primitive applications per task.

Memory arms, all capped at K primitive-tokens (the equal-byte budget):

| Arm | What it holds and how the controller uses it |
|---|---|
| A | nothing (primitives only) |
| B_edit | raw past solution programs, adapted by up to 2 edits ("demonstration adapted in context") |
| B_macro | raw past solution programs, callable whole as tokens ("retrieved demonstrations / whole-fossil reuse") |
| BX | the same raw context as B, but the controller extracts a fragment library from it before searching; nothing persists beyond the raw context |
| D | persistent library: fragments extracted from all history by a greedy compressor that keeps the most token-saving repeated fragments, capped at K tokens |
| D_shuffled | same fragment lengths, random payload |
| D_foreign | library extracted from a different world's history |

Phase 1 (information matched):
- All arms are built from the same 100 ground-truth training programs.
- 40 held-out tasks per seed per condition.
- Recurrence 0 or 0.5 (the fraction of test tasks that repeat a training program on new inputs).
- K in {30, 100, 300, all (~650-700)}.

Phase 2 (closed loop, not information matched):
- Each arm learns only from its own solutions, over 50 one-motif, then 50 two-motif, then 60 three-motif tasks (K=100; BX also at K=300).
- The final memories are then tested on 40 fresh three-motif probe tasks.
- For D, the library is also swapped to empty, shuffled, another lineage in the same world (different task stream), and a lineage from a foreign world.

Commands: `python3 phase1.py 1 2` and `python3 phase1.py 3 4`, run in parallel; the same for phase2.py and phase2bx.py. At most 2 processes at a time.

3. RESULT

Phase 1, recurrence 0 (tasks solved out of 160, summed over 4 worlds; mean primitive applications per task in brackets):

| K | B_edit | B_macro | BX | D | D_shuffled | D_foreign |
|---|---|---|---|---|---|---|
| 30 | 11 | 20 | 31 | 125 (10.0k) | 9 | 17 |
| 100 | 17 | 25 | 67 | 123 | 9 | 17 |
| 300 | 20 | 37 | 131 | 123 | 9 | 17 |
| all | 27 | 31 | 123 | 123 | 9 | 17 |

- A (no memory) solved 20 (18.3k).
- At K=all, BX and D are identical by construction, a sanity check that passed.
- In 3 of 4 worlds, D at K=30 recovered exactly the 10 hidden motifs.

Phase 1, recurrence 0.5, K=all:
- B_macro solved 71/71 repeated tasks against 55/71 for D; overall 92/160 against 127/160.
- Replaying whole episodes wins on exact repeats; the library wins on new combinations.

Phase 2, closed loop (solved per block, summed over 4 worlds; out of 200 / 200 / 240):

| Arm | one-motif | two-motif | three-motif |
|---|---|---|---|
| A none | 196 | 35 | 11 |
| B_edit | 11 | 4 | 1 |
| B_macro | 176 | 50 | 13 |
| BX, raw context K=100 | 184 | 101 | 29 |
| BX, raw context K=300 | 182 | 145 | 91 |
| D persistent, K=100 | 182 | 145 | 101 |

B_edit cannot start from empty memory: two edits from nothing only reach 2-primitive programs.

Probe on fresh three-motif tasks (out of 160):
- D with its own library: 50.
- D with the library swapped: empty 2; shuffled payload 6; other lineage in the same world 28; foreign-world lineage 1.
- Raw-context arms: B_macro 10, B_edit 0, BX K=100 18, BX K=300 46.

Plain conclusion. A persistent executable library beats naive use of the same information in context by a wide margin (125 vs 20-31 at K=30). Almost all of that advantage goes away once two things hold: the controller may extract a library from its own context (BX), and the budget holds about 30 past solutions (K=300). BX then ties or beats D: 131 vs 123 in phase 1, 418 vs 428 in the loop.

What is left of "persistence" breaks into two parts:
- (a) Compression under a byte budget. The library holds distilled information from all of history in K tokens, which raw context cannot do.
- (b) Amortised derivation. Extraction took 0.4-36 ms per task, against about 90 ms of search. That is a modest wall-clock cache, and it does not show in primitive-application units.

Neither part needs persistence as such. Under the ladder's own kill criterion (no advantage at matched information and compute), the rung kills whenever the context arm is allowed to extract. It survives only when the context arm cannot abstract or the byte budget is tight.

Organ findings:
- The payload is everything. A shuffled payload does worse than no memory in phase 1 (9 vs 20), and in the loop swap it is about as useless as an empty library (6 vs 2).
- The swap test collapses competence (50 to 2), so progress in the loop really did depend on the retained structure.
- Moving a library to another agent in the same world works partially (28 vs 50 for the agent's own library).
- Moving it across worlds with different regularities gives nothing (phase 1: 17 vs 20 for no memory; loop: 1/160).
- Description and retrieval-key ablations cannot be expressed here: there is no natural language, and the whole library is always inside the search.

4. DID IT RESOLVE THE QUESTION

Partly.

For a search-based controller without a language model the answer is clear: persistence adds nothing beyond "equal-information context plus an extraction step", apart from compression per byte and caching. Against naive use of context it wins big. The question as posed is therefore partly ill-posed: whether context wins depends mostly on how well the context-using controller can abstract and on the byte budget, not on persistence.

What is still open:
- The language-model case. There, "equal-information context" means a model that may abstract implicitly. That needs a language-model arm, which was out of scope (CPU only, no API).
- Generality. The world deliberately favours libraries: it has discrete, exactly reusable motifs, which is the assumption cost the ladder names itself. The run covers 4 seeds, one compute budget and one world family, where the ladder's promotion gate asks for 2 or more.

5. CONSEQUENCES

- The kill rung is badly posed; Atlas (ladder owner) should know. It should be restated as a per-byte and per-compute comparison that includes an explicit "same raw context + on-the-fly extraction" arm. Without that arm, any library beats a controller that cannot decompose its context, so the rung cannot kill. With it, persistence reduces to compression plus caching. That points to the ladder's memory-forms-per-byte experiment as the informative test. It also supports the ladder's own fallback of making the library a memory component inside an existing engine. Whoever next designs the fifth engine should know too.
- New positive result (small, expected): in a closed loop the retained library carries the competence. The swap collapses it (50 to 2), and a shuffled payload does no better than an empty library. Organs transfer partially between agents in the same world and not at all across worlds. This gives Nyx and Techne a cheap working harness for swap and transplant tests.
- Harness warning: a controller that adapts demonstrations by edits cannot start from empty memory. Using it as the context arm in a closed loop is unfair by construction.
- Design hint: replaying whole solutions beats a fragment library on exact repeats, so libraries should keep whole solutions as well as fragments when tasks recur.
- No defect was found in the program's own code, since none of it was run.

6. COST

- About 1.5 hours of my own time.
- About 39 CPU-minutes: phase 1 ~25, phase 2 ~10.5, context-only loop arm ~2.7, calibration ~1.
- At most 2 processes, under 200 MB RAM.
- Not done: a language-model context arm; a second world family; retrieval-key and description ablations; a test of composition depth on withheld composite tasks; learning curves across budgets; confidence intervals beyond 4 seeds.
