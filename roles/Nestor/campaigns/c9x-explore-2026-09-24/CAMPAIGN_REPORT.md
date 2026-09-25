# Cycle-9 campaign -- autonomous-loop report (2026-09-24)

Seat: Nestor, under the promotion charter of 2026-09-24. Budget window: 48 wall-h from
06:47 EDT. The machine record is `roles/Nestor/EXPERIMENT_GRAPH.jsonl`: 43 nodes, of which
9 CONFIRM, 28 EXPLORE, 5 FORENSIC and 1 INFRA. Claims live in `roles/Nestor/FINDINGS.md`
section E. Every experiment below was declared and committed before it ran; every CONFIRM
test was frozen (cells, seeds, arms, endpoint, rule) before its first run.

## 1. The frozen inner experiment C9

Protocol `5819bc6d`. 1,200 of 1,200 runs, 0 errors; the report audit passes 21 of 21.

| hypothesis | frozen verdict | after mining |
|---|---|---|
| H1 cue gating | no detected effect | **INVALID (C9-D16)**: the intervention never reached the task. Repaired and rerun as C9-H1R (confirm): **gating harms competence only when reading the cue costs instructions** (I = +0.20); transplanted to all 4 other transforms. Mechanism: without the gate, all competence is carried by answer-before-read guessers and no reader ever evolves |
| H2 propagation | replication events without propagation | weak signal in one specimen (7ae3), which led to E-10 |
| H3 reservoir | not demonstrated | retired structurally: random pair-tape populations evolve no task competence in any niche, even an XOR1 niche |

## 2. What was confirmed (CONFIRM lane, fresh frozen tests)

| claim | test | result |
|---|---|---|
| In non-pair physics with search, **self-location gates heredity** | C-SELFLOC | depth >= 3 in 13/36 vs 0/36, p = 1.6e-10 |
| **The depth-1 wall is newborn starvation** under energy economies | C-ENERGY | child replication 20/40 vs 4/40, p = 7e-5 (my side-prediction was falsified) |
| **Spontaneous non-pair heredity is blocked by the encoding length** of the ALLOC->copy->BIRTH chain | C-DENSE | 13/40 vs 0/40 cells replicate from random bytes, p = 3.8e-5 |
| Under short encodings, **self-location and search are necessary** | C-ABLATE | 15 -> 1 (p = 6e-5) and 15 -> 6 (p = 0.006); energy-for-depth not confirmed |
| With the splice off, **pair-tape heredity is establishment-limited** (4 founders vs 1) | C-CRITICAL-MASS | depth >= 5 in 41/80 vs 5/80, p = 8e-11; runaways 15 vs 2 |
| **Tape-write erosion (write-back of both halves after every interaction) stops pair-tape heredity** (7ae3 cell) | C-ATOMIC C1 | runaway 46/80 vs 1/80, p = 4e-17; generality C2 not confirmed |
| **The world's recombination splice prevents runaway pair-tape heredity** | C-RUNAWAY | runaway (depth >= 20) in 7/150 vs 0/150, p = 0.007; max depth 549 vs 13 |
| H1 cost interaction (C9-D16 repaired) | C9-H1R | I = +0.20 |

Not confirmed, and recorded as such:
- C-ATOMIC C2: the atomic-write-back effect across the other 15 panel specimens (1/120 vs 0/120).
- C-NORECOMB: the threshold endpoint, 5/48 vs 5/48.
- The energy-for-depth arm of C-ABLATE.

## 3. The barrier geometry, answering the 2026-09-23 question

The question was *why is sustained heredity so much harder than making one convincing
copy, and where does the transition fail?*

**Non-pair physics.** The chain fails at every stage, and each stage was deformed and
measured:
1. There is no search: mutation happens only at birth.
2. The copier cannot locate itself.
3. The six-byte op chain is too rare to discover.
4. Newborns starve under energy economies.

With all four relieved, heredity arises spontaneously from random bytes. With any one of
the first three removed, it disappears.

**Pair tape.** The predecessor's 1,031 "replicators" were 94% artefacts. The same world
operator, the recombination splice, both manufactured them and destroys genuine copies.
Turn it off and about 5% of single-founder implants of one specimen run away into
sustained, population-wide causal copying, 549 causal generations at the maximum.
Runaway is specimen-specific: 0 of 7 other specimens ran away. It is not explained by
copier quality. It is dose-sensitive: with 4 founders instead of 1, runaways rose from
0/64 to 9/64 and depth >= 5 from 8/64 to 32/64 (X-CRITICAL-MASS, exploratory WEAK_SIGNAL;
the SIGNAL bar was missed by one run). **A fresh frozen test confirmed it** (C-CRITICAL-MASS:
depth >= 5 in 41/80 vs 5/80, p = 8e-11): heredity here is establishment-limited. Whether
founders help each other was then tested and **they do not** (X-DOSE-CURVE, clean null,
LRT p = 0.42): each founder is an independent ~13% lottery ticket, s(k) = 1-(1-p)^k. The
"critical mass" name was wrong; the post-hoc excess came from a noisy single-founder rate.

**Why pair-tape heredity stops: two barriers in series.** Following the losing tickets:
1. *Copying ceases, lineages persist* (X-TICKET): outside the runaways, a founder's causal line
   stops copying by about epoch 12, while its members stay alive.
2. *Not mutation, not copy error* (X-DECAY, X-STERILE): switching off in-place mutation barely
   helps, and children are 75-80% fertile at birth.
3. *Erosion* (X-STALL, X-STALL-F0): by epoch 100 the members are genomically sterile even with
   mutation off. After every interaction the world writes BOTH tape halves back into the two
   organisms, so an organism's own writes and its partner's rewrite ~5.5 bytes in 57% of
   interactions: about 5% per byte per epoch, 25x the nominal mutation rate.
4. *Removing erosion restores heredity* (X-ATOMIC; **confirmed by C-ATOMIC C1**): if a half
   changes only when an accepted copy lands on it, runaway heredity rises from 1/80 to 46/80
   (p = 4e-17) in 7ae3's cell.
5. *But not across the panel* (C-ATOMIC C2, not confirmed: 1/120 vs 0/120). The other donors
   mostly cannot copy at all from a fresh state (X-DONOR-RATE: 7ae3 96%, two others 29%, twelve
   0%). Donor copy competence is the first barrier; erosion is the second. Given a competent
   donor (7ae3's genome, atomic write-back), 3 of 11 other cells permit runaway (X-DONOR-SWAP,
   WEAK_SIGNAL: ffa6 4/8, 9cba 1/8, e160 1/8 vs own cell 3/8). The genome copies from a fresh state
   only in 7ae3's cell and the near-identical ffa6 (0.955) and in no other cell (0.0): competence
   belongs to the genome-cell pair. Exploratory; not confirmed. X-SWAP-ORIGIN: the 9cba and e160
   runaways lie outside the founder's CERTIFIED causal lineage. X-ATOMIC-RANDOM then showed that in 7ae3's
   cell a random implant never runs away (0/80 vs 46/80) and that genome runaways are 100% founder-descended
   by ancestry: certification breaks inside the lineage, it does not mark native lineages. Whether the
   foreign runaways are founder-descended: X-SWAP-ANCESTRY.

## 4. Defects found and handled

| defect | handling |
|---|---|
| C9-D13 H3 arm-B migration mismatch | repaired pre-freeze |
| C9-D14 id is not heredity | repaired by the material ruler R3, tournament winner 9/9 |
| C9-D15 implant reaped first on age ties | conservative bias; frozen H2 unaffected |
| C9-D16 H1 intervention inert | INVALID; repaired rerun C9-H1R |
| C9-D17 H2 arms A and C identical | recorded |
| X-DENSE-OPS worker module leak | INVALID; repaired rerun |
| X-POSITION | withdrawn: partner sabotage, not register dependence |
| audit regex defect | caught by a negative control, fixed pre-freeze |

## 5. Honest scope

Every confirmed claim is scoped to the cells, physics and implants tested. "Spontaneous"
in C-DENSE means from random bytes *in a permissive world* (search, free self-location,
energy inheritance, 1-byte ops). The runaway claim is one specimen's cell. EXPLORE results
are hypotheses, not findings.
