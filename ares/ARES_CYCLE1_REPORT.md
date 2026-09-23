# ARES_CYCLE1_REPORT -- VALIDATE, COMPRESS, EXIT

Currency: 2026-09-21. Ares, M2. Prereg ares/DESIGN_C1.md on main at
3ea24dda8 before any run; sweep code_commit 3ea24dda8; results
ares/runs/sweep_c1/ (130 GA runs at 10 seeds + dissection + ancestry
+ causal transplant + mechanical disposition, disposition.txt). Two
EXPLORATORY post-hoc analyses are labelled as such (s3). This is the
closing report; the seat parks after it (directive item 7-8).

## 0. Disposition (mechanical, DESIGN_C1 s5)

    W4  hidden regime       MECHANISM_DIVERSE   i 10/10 ii 10/10 iii 6/10 iv 10/10
    W5  delayed revelation  MECHANISM_DIVERSE   i 10/10 ii  8/10 iii 7/10 iv 10/10
    W12 dying lineage       MECHANISM_DIVERSE   i 10/10 ii  9/10 iii 10/10 (iv n/a)
    W13 carrier stress      PRESERVE            i  9/10, ACT majority 6/10; NEW_CARRIER: none
    arm_nomem_W4 (no cross-step channel): 3.4-4.6 in 10/10, threshold 8.0 never reached

Reading: the cycle-0 W4 fossil REPLICATES as a function and is
IDIOSYNCRATIC as a structure. Every one of ten lineages solves the
hidden-regime world at the cap by carrying the early cue across the
lifetime in activation state; none carries it in plastic weights; the
carrier is implemented differently by every lineage. The lens is
proven on the operator's own criterion ("multiple lineages
independently invent functionally equivalent memory machinery"), with
the honest count below.

## 1. Independence count (a caveat that changes the numbers)

GA seeds 1-3 in cycle 1 reproduce the cycle-0 lineages byte for byte
(same seed -> same trajectory; only the held-out set changed; final
genomes verified identical). So "10 seeds" is 7 NEW independent
lineages plus 3 cycle-0 lineages re-evaluated under repaired controls.
Every claim below holds on the 7 new lineages alone: W4 7/7 at cap,
7/7 ACT-class, 7/7 collapse under no_memory. The cycle-0 GATE+MAX
signature appears only in seed 3, which is the same lineage; it was
rediscovered 0 times in 7 independent runs. It was an idiosyncrasy of
one lineage (DESIGN_C1 s5, recorded as predicted in P2).

## 2. What replicated, per world

W4 (hidden regime). 10/10 champions at the cap (40.0). Late-life
accuracy 1.00 for both regimes in 10/10; the repaired shuffled control
shows the behaviour in 0/10. Three-way memory ablation, all 10 seeds:
no_activation_mem 2.1-3.8 (collapse), no_plasticity 40.0 (no effect),
no_memory 2.1-3.8. Memory class ACT 10/10. The no-memory substrate arm
confirms the semantics: with no cross-step channel the GA reaches
3.4-4.6 in 10/10, never the 8.0 threshold. Node-level signatures (ops
of load-bearing hidden nodes): (none) x4, DIFF, GATE+MAX,
CONST+GATE+GATE, GATE, TANH, ADD+ADD -- no signature reaches 2/10.

W5 (delayed revelation), repaired control (shuffled balanced 8/8/8/8
on token x pay). 10/10 above threshold; 9/10 at the cap (50.0); decision
accuracy 1.00 in 8/10 with both sides >= 0.55; shuffled shows the
behaviour in 2/10 (search found a partial leak-free exploit at 28 in
one seed; recorded, below the 4/10 CONTROL_ARTIFACT bar). Memory class
BOTH 8/10, ACT 2/10: the 26-step carrier needs plasticity AND
activation state in most lineages. Cycle 0's "contradicts P-W5" reading
is confirmed at 10 seeds with a clean control: delayed revelation DOES
produce cross-delay memory in this substrate.

W12 (dying lineage), own-mode threshold 21.26. 10/10 above threshold
(25.6-32.7; seed 7 at 32.72 beats the best of the hand-written
"risky iff energy < k" family, 30.28). State-dependent risk (P(risky |
lowest energy bin) - P(risky | highest) >= 0.3) in 9/10; the shuffled
control (energy channel replaced by noise) is flat in 10/10. Memory
class NONE 6/10 as expected: the switch keys on OBSERVED energy and
needs no carrier. Signatures diverse (10 distinct). Cycle 0's MERELY
HARDER label was the threshold's error, not the world's.

W13 (carrier stress: W4 cue + W5 delay + louder distractor, reward
only in steps 60-79). 9/10 above threshold, 8/10 at the cap (20.0). The
early cue survives 57 steps of sd-1.0 distractor on its own channel.
Memory class among above-threshold champions: ACT 6, BOTH 2, PLAST 2
-> PRESERVE by the preregistered rule, with recruitment of the second
channel in 4/10. NEW_CARRIER (class NONE above threshold) occurred 0
times: no cross-step route outside the enumerated channels appeared.
Per DESIGN_C1 s8 this is the only outcome that could have earned
another round, and it did not occur.

## 3. EXPLORATORY: what the carrier actually is (post-hoc, labelled)

3.1 Self-recurrence, not leak. Four W4 champions have NO load-bearing
hidden node yet collapse under no_activation_mem. Inspection: they
carry self-loop edges (a node feeding itself), in three cases on an
OUTPUT node, which node ablation never removes (seed 9 has zero hidden
nodes and one output self-loop). A self-loop cut (ares/supp_selfloop.py,
runs/sweep_c1/selfloop.json) across all W4 champions: self-loops present
in 9/10; cutting them collapses 6/10 (2.4-9.4); the other 4 use
multi-node recurrent cycles (seed 3's GATE<->MAX is a 2-cycle). Cutting
the KEEP coefficient (the leak primitive the substrate offers) collapses
0/10: no W4 lineage uses it. So the compressed, non-named description of
the W4 mechanism across ten lineages is:
    the early cue is held in RECURRENT ACTIVATION (a self-loop in 6/10,
    a longer cycle in 4/10), never in a leak coefficient, never in a
    plastic weight; the node ops around the loop vary freely.
This matches the cycle-0 cheat-control experience (a keep-only carrier
decayed by step ~15; a saturating self-loop held). Evolution reached
the same conclusion ten times.

3.2 Under stress the carriers diversify. W13: self-loop cut collapses
5/10, keep cut collapses 2/10, plasticity is load-bearing in 4/10 (from
the three-way ablation). W5 (26-step delay through distractor): self-
loop cut 5/10, keep cut 4/10, plasticity load-bearing 8/10. Longer or
noisier delays recruit every available channel; the short W4 delay is
served by recurrence alone.

3.3 The "accreted" claim of cycle 0 is retracted. Cycle 0 read "13
lineage generations of mutations" as accretion. The functional test
(snapshots evaluated intact vs no_memory every 5 generations; DESIGN_C1
s6) shows the memory gap reaching half its final size at the SAME
snapshot as fitness onset in 8/10 W4 lineages (accretion 0-5), and 10
generations later in 2/10. In W4 the memory IS the solution, so they
co-emerge; the mutation-chain length measured lineage age, not
assembly. W5 by contrast accretes genuinely (10-65 generations in 9/10).
LEDGER row added.

3.4 Causal transplant fails. Splicing each champion's load-bearing
nodes into 64 random organisms conferred competence above a random
subgraph in 1/10 (W4), 0/10 (W5, W12, W13). The mechanisms are
wiring-context dependent, consistent with cycle 0's W8 null and with
the self-loop finding (the carrier is an edge pattern, not a node set,
and output-node self-loops are not transplantable by a hidden-node
splice at all). Predicted (P7, second clause).

## 4. Instrument audit (what this cycle found wrong with itself)

- W4/W13 shuffled controls balance the regime but not the SHOWN cue (a
  second draw); a pure cue reflex scores 0.59 on the shuffled set, not
  0.50. Same defect class as the W5 row of 2026-09-19, fixed for W5 and
  missed here. Effect: criterion (ii)'s shuffled bar (0.65) sits 0.06
  above the reflex floor instead of 0.15 -- CONSERVATIVE, so no
  disposition changes (W4 ii 10/10 anyway; W13's disposition does not
  use ii). LEDGER row added; DESIGN_C1 ADDENDUM 1.
- Node ablation cannot see output-node self-loops (s3.1). Criterion
  (iii) therefore under-counts localisable mechanisms (W4 6/10 where
  the carrier is provably present 10/10). Recorded; not repaired this
  cycle (the seat parks).
- Predictions: P1, P5, P6 (direction), P7 (transplant clause) held.
  P2 held on disposition, lost on count (GATE+MAX 1/10, not 2-4). P3
  lost strictly (8/10 <= 4.0; all 10 < 8.0 threshold). P4, P6 (count)
  lost in the FAVOURABLE direction: my priors under-estimated this GA
  on this substrate every time. P7 accretion clause lost (s3.3).

## 5. Answer to the operator's question

"Has the pressure-engineering lens demonstrated a distinct yield
curve?" On two cycles: one pressure (hidden regime) reliably yields a
memory carrier that no control yields, in 10/10 lineages, structurally
diverse, functionally identical, with the substrate's own designed
memory primitive (keep) never selected and its undesigned one
(recurrence) selected every time. Two more pressures (delayed
revelation, dying lineage) yield their target behaviour at 10/10 once
their controls were repaired. The combined stress preserves the carrier
and recruits others but produces nothing outside the enumerated
channels. The lens is proven for this substrate; it has not (yet)
produced a mechanism that resists description as a gated recurrent
carrier or a state-keyed switch, and cycle 1 found no reason to expect
that from more of the same.

## 6. Disposition of the seat

PARKED after this commit (STATUS.md). No cycle 2 self-authorised.
What is left reusable: ares/PRESSURE_CATALOG.json (12 worlds with
falsifiers, 6 candidates never built), the substrate and worlds as a
batched sandbox (~13 ms per 128-organism episode), the three-way
memory ablation and per-world balanced seeding as instruments, and the
W4 fossil set (ares/fossils/ + runs/sweep_c1/W4_present_s*.json, ten
lineages). The W4 artifacts are re-sent to Nyx/Harmonia with this
report; their reading is wanted, not waited on. If the operator reopens
the seat, the first item is the output-node self-loop blind spot in
node ablation (s4), then the six CANDIDATE pressures.
