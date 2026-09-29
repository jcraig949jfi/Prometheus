REPORT -- does a compact inherited handle raise a fresh receiver's REACH, or only its speed?

1. WHAT I SET OUT TO TEST

In the Aphrodite integer-fold engine, a donor derived one hole-bearing body
schema, (acc + {H}), and a fresh recipient that inherited it solved five
unseen-body families 16/16 inside a 250,000-charge escrow where the no-handle
recipient (PRISTINE) solved 0-1/16. That committed result is a speed readout
censored at the escrow. I asked whether the handle lets a fresh receiver
solve families it CANNOT solve without it -- i.e. families that stay unsolved
by the no-handle receiver even at 10x the escrow -- beyond what a
compute-matched no-handle receiver, random handles of the same shape and size,
a verbatim memo of the donor's witnesses, and a receiver with a different
enumeration order would get. If no such "reach set" exists in this DSL, the
question cannot be answered here and the honest reading of the transplant
result is leverage (acceleration), not reach.

2. WHAT I DID

Code and data (read-only clone /home/jcraig/artemis-selftest/repo, exported
with git archive into scratch; nothing run against the clone):
  - engine: origin/aphrodite/engine-2026-09-21 @ 9490f3f34, roles/Aphrodite/engine
    (fair.py keyed search, tier3d.py catalog, meta_tribunal.py, basis_v4.py),
    frozen artifacts S3_ARTIFACT_2026-09-23.json (selected library sha
    4fed9489d956...), T3D_SHAMS_2026-09-23.json, T3D_QUALIFICATION_2026-09-23.json,
    S4_RESULTS_2026-09-23.json.
  - ceiling candidates: origin/aphrodite/a16-campaign-2026-09-26 @ 4f937e88f,
    A17_CATALOGS_2026-09-26.json catalog A (all 11 families, including the fdiv
    and gcd OBSERVE families no donor solved), provider copied from a17.py.
Scratch (/home/jcraig/artemis-selftest/work/R-35):
  rsearch.py  exact re-implementation of fair.search_collect (same keyed
              init>body>final stream, same charge = stream position), with the
              fold accumulator hoisted per (init, body) and passing finals
              memoised per accumulator; every accepted candidate is re-confirmed
              with the reference basis_v4.run_program. Also a second receiver
              ("size order": smallest expressions first, keyed ties).
  cells.py    one fresh recipient: keyed cell (dev set + order seed from the
              engine's Cell), search, then the engine's own MetaTribunal on up
              to 5 hits (emitter 2), exactly as run_s3s4.run_recipient.
  validate.py reproduction check against the committed transplant rows.
  run_r35.py  stages 1-3 (design frozen in its docstring before stage 2 ran;
              one pre-stage-2 revision for CPU budget is marked there).
  analyse.py  tables; out/*.jsonl raw rows, out/summary.json, out/partition.json.
Runs (python3, CPU, at most 2 processes):
  0. Reproduction: 1,232 recipient cells (7 admitted families x 11 arms x 16
     recipients, escrow 250k) -- 0 mismatches in qualified / charges / hits /
     false positives / escrow spent vs S4_RESULTS. After a speed patch, 48 cells
     re-checked, 0 mismatches.
  1. Partition: PRISTINE, keyed, 18 families (7 transplant families on the
     SAME recipients as the committed run + 11 catalog-A families on fresh cells
     "R35-rx/0..15"), 16 recipients, cap 7,166,141 = escrow B (250,000) + the
     donor meta-cost 6,916,141 (compute-matched budget B'). Rule fixed before
     running: easy = PRISTINE >= 8/16 at B; reach set = PRISTINE <= 1/16 at
     10B (2.5M); middle = the rest.
  2. Arms on all 18 families, same recipients/seeds, cap B: derived handle,
     8 committed shams, MEMORISE (verbatim certified member bodies), 5
     same-shape same-size scrambled schemas ((acc*H), (acc//H), (acc%H),
     gcd(acc,H), pow(acc,H); 161 instantiations each, like the handle), and
     (acc - H) run separately and labelled NEAR-COPY. For the 7 transplant
     families the committed rows were used for arms already in that run.
     Size-order receiver with and without the handle, cap 10B.
  3. Leave-one-out: each derived-handle win at B re-run with the winning body
     removed from the handle (224 cells).

3. RESULT

Stage 1 -- the reach set is EMPTY. Every one of the 18 candidate families is
solved by the no-handle receiver once it is given more budget:
  PRISTINE qualified/16 at B / 10B / B':
    5 unseen-body transplant families: 0-1 / 2-11 / 12-16
    fdiv_bf 1/8/10, gcd_al 1/13/15, gcd_bf 1/4/11 (the "no donor solved" ones)
    other catalog-A families: 0-3 / 4-12 / 8-16
    2 related families: 16/16/16 (easy set)
  Median first-qualified charge of PRISTINE solvers: 0.5M-4.2M, i.e. 2-17x
  the escrow. Over the 16 middle families PRISTINE solves 16/256 recipients
  at B, 11 families at 10B (>= 8/16), and 16/16 families (210/256
  recipients) at the compute-matched budget. By the frozen rule, reach cannot
  be measured here; everything below is speed.
Why this is structural, not an accident of family choice: every library in
this engine (fair.KLib) is its entries FOLLOWED by the complete G4 fallback
(226,381,140 fold candidates plus 180 expressions), in a key order that does
not depend on the library. A handle therefore only prepends candidates:
the derived handle's entry is 2 x 161 x 180 = 57,960 candidates, so a
handle-carrying receiver at budget b finds everything PRISTINE finds at
b - 57,960, plus whatever the handle entry itself contains. The sets of
reachable families are identical for every arm at any budget >= the full
space (~226.5M); handles move the budget at which a family is reached, never
whether it is reachable. (Only the 5-hit false-positive stop can make a
recipient permanently fail; it did so for 0-2/16 per family, for PRISTINE.)

Stage 2 -- speed at B (families solved >= 8/16, over the 16 middle families):
  derived handle 12 (192/256 recipients); PRISTINE 0 (16/256)
  derived handle FAILS 0/16 on fdiv_bf, gcd_al, gcd_bf and sub_aa (PRISTINE
    gets 1,1,1,0 there at B; 8-15/16 at B') -- the handle is slightly harmful
    off its home ground, as the prepend arithmetic predicts.
  NEAR-COPY (acc - H) 8 families; committed SHAM_7 (which drew (acc - H)) 8.
  scrambled same-shape schemas: (acc // H) solves fdiv_bf 16/16, gcd(acc,H)
    solves gcd_bf 16/16 -- families the derived handle cannot solve; each
    other scrambled schema solves none. Random-body shams: 0 families (SHAM_5
    solves one catalog-A additive family 16/16).
  MEMORISE: 0 middle families; it is the cheapest arm only on the two related
    families (about 1,500 charges vs 26,000-28,000 for the handle).
  So a one-hole schema of this shape gives 16/16 at B exactly on the families
  whose body's outer operator matches its own (or is reachable from it by a
  compensating final, e.g. negmod via (acc + ...) and first - acc). The derived
  handle's advantage over the scrambled/sham nulls is that its operator (+) is
  the one that dominates the catalog (12 of 16 middle families are additive or
  subtractive), not that it carries a richer lesson.
Different receiver (size order): with the handle, 12 families at B (identical
  set) and 14 at 10B; without it 0 at B, 11 at 10B. The speed gain transfers
  to a receiver with a different enumeration order, because any receiver that
  walks the inherited entry first gets it; it is not a lineage-local bias.
Leave-one-out: removing the single winning body from the handle removes the
  win in 169 of 224 cells; the 55 survivors are the two related families and
  hA_add_at (another instantiation of the same schema wins) plus a few
  recipients PRISTINE solves at B anyway. The handle is causally used.

Plain conclusion: in this engine the inherited handle is real, causal,
receiver-portable search LEVERAGE (roughly 15-100x fewer charges than PRISTINE's median solve on its
home families, 0/16 -> 16/16 inside a fixed escrow), and it is not reach: every
family it "unlocks" is solved by the no-handle receiver at 10x the escrow or
at the donor's own compute, and the engine's complete fallback makes a reach
gain impossible by construction. The sagacity reading (a handle lets a fresh
receiver reach what it could not) is neither supported nor refuted here; this
DSL cannot express it.

4. DID IT RESOLVE THE QUESTION

Partly. It resolved the question for this engine and these inputs: a clean
"cannot speak to reach" -- the reach set is empty after the 10x pass for all 18
committed candidates, and a structural argument shows every family in the
grammar is reachable by every arm at the full-space budget, so a handle can
only move the budget at which a family is reached. It did NOT
test sagacity anywhere it could in principle appear (a receiver without a
complete fallback, a bounded-search or learned proposer, or an LLM receiver
where the handle is also a name). Compute-matched, scrambled-handle, memo,
different-receiver and leave-one-out readouts were all obtained, but as speed
readouts. A shuffled-handle arm with a second MINTED handle was impossible
(the ecology has minted only one); the same-shape scrambled schemas stand in
for it and show that a hand-picked operator-matched schema does as well as
the minted one on its own families.

5. CONSEQUENCES

- False premise / instrument property (for the Aphrodite seat and whoever
  frames carrier claims): the transplant success is censored speed. Under the
  frozen expressive-equivalence condition every arm has the same reachable set;
  "PRISTINE 0-1/16" only means "PRISTINE needs 2-17x the escrow". Any claim
  that the derived schema lets recipients do something they otherwise cannot
  should be withdrawn or restated as acceleration; the existing review text
  mostly already says leverage, but the 0/16 vs 16/16 framing invites the
  reach reading.
- The "no donor solved" fdiv/gcd families are solved by a fresh no-handle
  receiver at about 3-11x the escrow (median 0.8-2.8M charges). They were
  escrow-limited, not out of reach.
- Null calibration: the committed sham distribution (random bodies) is too
  weak a null for a schema. Same-shape scrambled schemas are the right null:
  each one wins 16/16 on the families matching its operator. Whether the
  derived handle "beats the sham distribution" is then a statement about the
  catalog's operator mix (additive-heavy), not about the handle.
- Reproduction of something known: the committed transplant rows reproduce
  exactly (1,232/1,232 cells) with an independent hoisted searcher; the
  memorise-vs-generalise trade-off and SHAM_7's near-copy status reproduce.
- Positive, small: the handle's leverage is receiver-portable across
  enumeration orders and survives a leave-one-out mask test (it is used).
- For designers of carriers (packets, keys, libraries): a reach test needs a
  receiver whose unaided search is genuinely bounded (no exhaustive fallback,
  or a budget-free notion of failure), otherwise it measures only speed. The
  hoisted searcher here (about 0.1-3 s per recipient at up to 7M charges)
  makes budget sweeps cheap for anyone who wants to report reach-vs-budget
  curves instead of one censored point.
- No new engine runs were made in the program's name; all runs were in
  scratch against committed inputs, no sealed holdout was touched.

6. COST

About 1.5 hours of my own work. CPU: about 38 CPU-minutes in total
(reproduction check 4.6 min, partition 8 min, arms plus size-order receiver
about 22 CPU-min on 2 workers, leave-one-out 0.4 min, profiling and probes a
few minutes). Peak RAM under 60 MB. Not done: stage-2 arms were capped at B
(not 10B) to stay in budget, so handle/sham counts at 10B are not measured
directly (by the prepend arithmetic a handle arm at 10B equals PRISTINE at
10B minus 57,960 charges plus its entry hits); no receiver without a complete
fallback was built; no second minted handle exists; nothing on LLM or named
handles.
