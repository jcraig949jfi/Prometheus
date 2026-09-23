# ENSORAIN E2 "STRUCTURE DISCOVERY" -- preregistration part 1

Currency: 2026-09-23. Seat Ensorain[m2-14baf7d5]. Authority: operator
ruling + E2 authorization, roles/Ensorain/prompts/
2026-09-23_e1p5_ruling_e2_authorization/ (verbatim; R1-R6). Committed
BEFORE any E2 code. E1/E1.5 parked intact. Part 2 may set constants only
(per-family learning constants calibrated on dev, OUTER's fixed choice,
the discovery compute ceiling by the stated criterion); no gate,
threshold, arm, world family, seed set or verdict clause may change.
Every operationalisation below quotes the operator's words it implements
and says whether it is stricter or looser (E1.5 lesson, ledger).

## 0. Question

"Can an organism discover useful tensor topology/factorization from
experience, rather than being handed it or finding it through blind
outer-loop search?" -- from interaction data, within one life, under the
same bounded economy as E1.

Stated limit (north star): the discovery MECHANISMS here are
hand-specified procedures compared as instruments. E2 asks whether
in-life, evidence-driven structure selection is possible and pays under
this economy. It does not claim a mechanism was discovered. If E2 passes,
making the discovery policy itself selectable is the next question.

## 1. Worlds ("some should favor TT, some matrices, some CP/Kronecker
## structure, and some deliberately lack a compact factorization")

Four families, same address space as E1 (4 modes x 8 values), same
held-out (A,C) region, same event stream and locks (L1/L2/L3), same
tolerance (abs tau .15), economy, compute price. Every field scaled to
sd 1. The HIDDEN STRUCTURE IS RANDOM PER INSTANCE (a new latent->observed
mode permutation for every world): no class-level physics that an outer
loop could learn.
  W_TT    TT in latent order A-B-C-D, ranks (3,3,3)      TT: 192 floats
  W_MAT   X = u[a,b] * v[c,d] (rank 1 across {A,B}|{C,D}) LOWRANK: 128
  W_CP    CP rank 4 over the four modes                  CP: 128 floats
  W_NONE  i.i.d. Gaussian per cell (no compact factorization)
Persistent cap C = 192 for every arm (the TT world's exact size; every
family's true structure fits at 192 in its own format and NOT in the
others': TT(3,3,3) cannot hold rank-1-across-a-cut W_MAT exactly (needs
bond 8) nor CP-4 (needs bond 4); LOWRANK rank 1 cannot hold W_TT or W_CP;
CP rank 6 cannot hold W_TT (TT(3,3,3) has CP rank up to 27) nor W_MAT
(CP rank up to 64)).

## 2. Hypothesis space H (the structures an organism may commit to)

17 hypotheses, each built with E1's memories at C = 192:
  TT(order)     12 orders (24 up to reversal), ranks = uniform fit (3,3,3)
  LR(partition) 3 two-plus-two partitions, rank 1 (128 floats)
  CP            rank 6 (192 floats)
  NONE          no persistent memory, no compute (predicts 0)
CORRECT hypothesis per world: W_TT: TT order whose ranks for the true
field are (3,3,3) (numerical, tol 1e-8); W_MAT: LR with the true
partition; W_CP: CP; W_NONE: NONE.

## 3. Life with a discovery phase (identical for every arm)

Events 0-299: DISCOVERY PHASE. Locks are answered with no memory (0).
Every observed value is offered to a DISCOVERY BUFFER of 512 samples
(reservoir sampling; transient, declared: 1,024 floats; identical for
every arm). At event 300 the arm's MECHANISM commits to one hypothesis
using ONLY the buffer, paying compute for every candidate fit (units =
samples x params x sweeps, E1's proxy, price kappa) under a DISCOVERY
COMPUTE CEILING D identical for every arm (part 2; criterion: exhaustive
evaluation of all 17 at the family constants must NOT fit, so allocation
matters). The committed memory is then fitted on the whole buffer
(charged), the buffer is discarded, and the life continues from event 300
exactly as an E1 life (scratch 128, charged consolidation, E1 compute
ceiling). No structural change after event 300 (single decision; kept
tiny).

## 4. Arms (mechanisms)

Blind (no use of the life's data for structure):
  BLIND1     one hypothesis drawn uniformly from H at birth
  RANDPERM   TT with a uniformly random order ("random permutations")
  OUTER      one fixed hypothesis chosen by an OUTER loop over training
             worlds (seeds 4000+, all four families mixed): the E1.5
             mechanism made exhaustive -- the best any fixed architecture
             search can do when structure varies by instance
In-life, evidence-driven (use the discovery buffer, pay compute):
  EXHAUSTIVE all 17 hypotheses, equal sweeps (as many as D allows),
             lowest validation error wins ("exhaustive permutation
             search", extended to families)
  GREEDY     start TT(identity); best-improvement local moves: adjacent
             mode swap, switch family (TT/LR/CP/NONE), change partition;
             stop at no improvement or when D is spent ("greedy local
             swap")
  MI         TT family fixed; order = chain maximising adjacent pairwise
             dependency, dependency = variance of E[y^2 | a_i, a_j]
             beyond its marginals, from the buffer; no model fits
             ("mutual-information/correlation ordering heuristic")
  LRSEL      matrix family fixed; best of the 3 partitions by validation
             ("matrix LOWRANK")
  SD         the preregistered ORGANISM mechanism: successive halving over
             H -- every hypothesis gets a cheap fit, the better half gets
             twice the sweeps, repeat to one survivor ("temporarily test
             alternative decompositions ... make those operations
             costly"). Validation split: 384 fit / 128 held out, fixed per
             life.
Controls:
  NOMEM      no memory ever (chance floor, energy reference)
  ORACLE_H   the CORRECT hypothesis from birth, no discovery cost
             ("oracle latent order", extended to families)
  SMUGGLER   E1's audit test re-run (must be refused)

## 5. Measurements

Per life: committed hypothesis; CORRECT (yes/no); discovery compute;
learning compute; EFF = (U - U_NOMEM)/max(P_used,1) as E1 (U = lock
reward - compute energy, whole life); held-out R^2; L2 success; for SD,
EXHAUSTIVE and GREEDY the validation-error trajectory over their
decisions (the "increasingly useful" curve).

## 6. Seeds

dev 0-999 (per-family constants, D calibration); OUTER training
4000-4063 (16 per family); confirmatory SET A 40000-40029 and SET B
40100-40129 per family (30 instances x 4 families x 2 sets), organism
seeds 0-1.

## 7. Gates and verdict (any failure -> CLOSE unless a control fails)

CONTROLS
  PC   ORACLE_H median held-out R^2 >= 0.5 in W_TT, W_MAT, W_CP, both sets.
  NEG  in W_NONE no arm's mean L2 success exceeds NOMEM's by > 0.05.
  CHT  SMUGGLER refused; BLIND1's CORRECT rate within 2 binomial SE of
       1/17 in the structured families (the identification metric is not
       free).
G_ID ("identifies ... factorization structure"): SD's CORRECT rate
  >= 0.70 in EACH of W_TT, W_MAT, W_CP, in BOTH sets; and in W_NONE SD
  commits to NONE in >= 0.50 of lives in both sets.
G_EFF ("substantially more efficiently than blind search, ... improves
  held-out competence under the same bounded-memory economy"): in EACH
  structured family and EACH set, mean EFF(SD) >= 1.10 x mean EFF(B*),
  B* = the best of BLIND1, RANDPERM, OUTER in that cell, AND paired
  bootstrap (instances, 10,000) 2.5% bound of EFF_SD - 1.10*EFF_B* > 0.
  (Strictness note: "substantially" -> 10% with CI, both sets, every
  structured family. W_NONE is excluded from G_EFF because EFF divides by
  P_used and NONE uses 0; W_NONE is covered by G_ID's NONE clause.)
QUALIFIER (reported, not a gate): SD vs the best simple in-life search
  (EXHAUSTIVE, GREEDY, MI, LRSEL) on EFF per structured family: SPECIAL if
  SD beats it by > 10% (CI lo > 0) in >= 2 families in both sets,
  otherwise TEXTBOOK (in-life discovery works; the successive-halving
  organism adds nothing over simple model selection).

VERDICT
  control fails                   -> INDETERMINATE (report; no claim)
  G_ID and G_EFF pass             -> DISCOVERY DEMONSTRATED (+ SPECIAL or
                                     TEXTBOOK)
  otherwise                       -> CLOSE (B)

## 8. Seat predictions (losable)

P1 PC passes for TT and MAT; CP is the risk (E1's CP learner was weak;
   p pass .6).
P2 G_ID: SD correct >= .7 on W_TT (p .6), W_MAT (p .7), W_CP (p .4);
   NONE >= .5 on W_NONE (p .5): the validation error of a fitted model on
   noise will often beat "predict 0" by chance overfit unless the split is
   honest -- it is, so p .5.
P3 G_EFF passes wherever G_ID does (blind search picks the right
   structure ~1/17 of the time).
P4 Qualifier: TEXTBOOK (p .75) -- EXHAUSTIVE with fewer sweeps each will
   be about as good as successive halving at this tiny H.
Net: DISCOVERY DEMONSTRATED p ~ .3 (mostly gated by W_CP), CLOSE p ~ .5,
INDETERMINATE p ~ .2.
