# BEL-48H FINAL REPORT -- Bellerophon, campaign BEL-48H-2026-10-08

Directive: roles/Bellerophon/prompts/2026-10-08_bel48h/ (verbatim + MANIFEST). Clock 2026-10-08T05:14Z -> 2026-10-10T05:14Z.
Host ubu005 (8 cores, 22 GB). Starting commit 22793858f; repaired kernel merged to main 2c6072c9d; campaign branch
bellerophon/def-bel-008-010-2026-10-06. Status: FINAL (closed 2026-10-10 ~01:40Z, before the 05:14Z deadline; every block complete).

Artifacts: BEL_48H_PREREG.md (20 sections, 2 amendments, errata, 2 disclosures) | BEL_48H_EXECUTION_LEDGER.jsonl |
BEL_48H_CAUSAL_LEDGER.jsonl (20 claims) | BEL_48H_CORRECTED_BASELINE.md | BEL_48H_HEREDITY.md | BEL_48H_REACHABILITY.md |
BEL_48H_COMPUTATION_REPRODUCTION.md | BEL_48H_MECHANISM_DISCOVERY.md | BEL_48H_FAILURE_BOUNDARIES.md |
BEL_48H_NEXT_EXPERIMENTS.md | BEL_48H_REVIEW_RECORD.md | packets/ | receipts/ (one analysis JSON per block) | tools/
(instruments, plans, frozen analyses, tests). Raw data host-local: ~/bel48h_runs on ubu005 (results.jsonl + events per
block; plan files and pinned code copies per freeze commit).

## 1. Answers to the directive's twelve questions

**1. Which repaired instruments survived adversarial review?** All three -- after repair, with limits disclosed. Review A
failed DEF-BEL-008 as shipped (one-hop provenance mislabelled 22-62% of 'captures') and found a zero-sweep hole in
DEF-BEL-010; both repaired by tracking each byte's pre-execution origin through the VM (multi-hop, measurement only),
byte-identity re-verified on 478 cases + the golden replay, merged to main, Nestor notified (#1884). Review B: SOUND_WITH_
LIMITS -- PROVENANCE is material ancestry, not parentage; PAIRED aligns initialisation only (variance ratio 0.9998,
divergence at tick 1 in 150/150 pairs); 'written' is a one-execution near-copy test. Its two defect specimens are fixed;
its k-generation functional test was adopted as an extra measurement.

**2. Which historical findings survived?** SURVIVED: spontaneous self-replication and its per-cell rates (6/7 cells under
both rulers; BYTECODE32 0/150 not reproduced); the sustained fraction (34.8% vs 39.4%); SR-level statistics (0.02%
ruler difference over 1.58M births); coupling P1-P4; and coupling P6 (conflict repair), which had FAILED for power and
is now confirmed (10/300 vs 0/300; reproduced 15/300). DID NOT SURVIVE: lineage-level statistics in mixing worlds (22-26%
of living organisms change genetic root between rulers); G6a in its published form (already withdrawn 2026-09-29;
corrected form reproduced on fresh seeds); pooled 'independent origins' (grounding 160 origins = 83 populations; G1 55
= 41; G1T 32 = 9).

**3. What did we learn about genetic inheritance?** (a) Functional heredity can be ASSEMBLED from two non-replicating
sources: a writer that lays down LD T,n and a carrier that holds LDIR produce a heritable self-copier; each byte set is
necessary, single-source reconstructions fail -- CAUSALLY_CONFIRMED, general across 3 confound-free variants (incl. a
writer with no copy routine that computes its bytes) and 3 world models, abolished by complete-overwrite physics.
(b) CAPABILITY persists without LINEAGE: function in 98/100 worlds while the first assembled lineage survives in 36/100
and in 42/100 no assembly lineage is alive -- REPRODUCED. (c) The working machinery is newly made: its critical bytes
are post-founding changes, not founder material.

**4. How do new replicators arise?** (85 independent unseen populations, REPRODUCED.) A SINGLE change (54/75) activates
a NON-COPYING precursor (60/85) that other organisms' imperfect copying ASSEMBLED (56/85). Causes: mutation 53, uptake
13, born-assembly 10, self-move 7, self-construction 2. LDIR is indispensable (85/85; 2 machines carry redundant LDIRs
that single knockout cannot see).

**5. Incremental or atomic?** Neither as usually meant: activation of cryptic precursors. WHICH operator completes a
precursor is predictable from its neighbourhood -- CAUSALLY_CONFIRMED by a mutation-rate intervention (N1): 'needle'
precursors (0 segment-move routes) need point mutation (completion 0.14 -> 0.78 from VLOW to HIGH mutation); 'move-rich'
precursors are completed by the copy dynamics themselves (0.98 -> 1.00; 63/63 completions at VLOW non-mutational).
Substitution-based reachability rulers cannot see this (fault-line: fragment A 0/16,320 substitutions vs 8/50,512 moves).

**6. Can useful computation influence hereditary success?** Yes, causally: contingent payment raises competent self-
replicators (conflict repair 10/300 vs 0/300; ECHO acquisition 20/150 vs 0 OFF vs 3 SHUFFLED; reproduced 15/300, 41/300).

**7. Did any reproductive mechanism preserve task competence?** Two architectures. Compute-then-copy (separated) and
copy-then-compute (BUDGET-COUPLED: the copy-length operand is competence-critical because an unbounded copy consumes the
shared step budget before the task code runs -- causal on a specimen, prevalence 17/41 on fresh seeds; the coupling
VANISHES when the budget exceeds the copy cost: 0.52 -> 0.50 -> 0.00 at budget 192/256/384). Paying for the computation
favours the compute-first architecture at MED mutation: two independent pairs (23/24, 24/24 seeds) and a 4 x 4 panel
(14 of 15 pairings, p 0.0005) -- CAUSALLY_CONFIRMED and general. Conflict repair runs in place in the damaging lineage
(8/10, 8/15), never by cross-lineage recombination (0/25).

**8. Did a novel reproductive architecture emerge?** Three: fragment complementation; horizontal UPTAKE as a route to the
FIRST replicator (15% of origins; an organism imports partner bytes that were inert where they came from); and
distributed persistence (re-making and re-capture instead of descent). Uptake is also a net SUPPRESSOR: blocking it
raises origination by 38% (U 84 vs 61; U2 83 vs 60 on fresh seeds; 1,600 independent pairs) because imports scramble
working and near-working machines (destroyed 2,363 vs created 418) -- but only in GRID WELL_MIXED at budget 256: no
effect in a SOUP world or at budget 384 (S1).

**9. Which findings survived transplantation?** Complementation -> new operands, offsets, construction mode, world
models (all hold). Precursors re-placed in new worlds complete by their neighbourhood class (N1). The architecture-
payment effect at MED -> 18 specimen pairings. Did NOT survive: the HIGH-mutation architecture effect (pair-specific);
the uptake-suppression effect across world models and budgets.

**10. Which hypotheses were falsified?** W1-P7 (from a withdrawn figure), W1-P9, W2-P1..P4, W2-P6, W3-P2, W4-P5 (as
written), W5-P1, W5-P4, W5-P7, C1-P6 (as written), X-P6, S1-P1, U3-P2, U3-P3, UF2-P1; and my own W4 mechanism claim ('answer produced through
the child copy', retracted: 0/20, then 1/41); and my post-hoc staging-copier reading of CL-20 (retracted by U3).

**11. Which mechanisms deserve another multi-day campaign?** (1) Uptake as creator and suppressor of replicators -- the
route economics and its substrate boundary. (2) Operator-matched completion as a theory of reachability under copy
physics (a rearrangement-aware ruler for the kernel). (3) Architecture selection under payment across mutation regimes
and budgets, with a specimen panel.

**12. What next?** BEL_48H_NEXT_EXPERIMENTS.md (ranked; #5 and #8 were done inside the campaign as B1 and the seed audit).

## 2. Process record (what went wrong and how it was handled)

Instrument defects caught before the affected analysis was read: DEF-008 one-hop (Review A; W1 stopped at 128 runs and
re-frozen); FUNC zero-sweep; Func short-tape shrink; a name collision with World.comp. Analysis defects caught after:
W4-P5 tag case, C1-P6 field mismatch (both reported as written AND corrected). Design defect: seeds shared across cells
(amendment 2; claims restated per population). A claim retracted (W4 'through the child'). Predictions written from a
withdrawn figure (W1-P7) and from a 3-run pilot (W2-P3). Three hand-written future timestamps (errata). Two operational
incidents (a marker collision started U2 early -- stopped at 0 results; my own shell killed twice by loose process
patterns). All in the calibration ledger with the rule adopted.

## 3. Receipts

Runs (complete blocks; excluding 56 pilot runs, 128 superseded W1 runs and all smoke tests): 16,100, 0 voids, 0 NOT_RUN.
Per block (runs / lane-active h; lanes overlapped, so these are not CPU hours): W1v2 3,240/4.05; W2 1,050/2.10; W3a
27/0.65; W3b 75/1.01; W4 1,050/2.25; W5b1 240/5.62; W5b2 400/3.03; W5b3 192/2.79; W6b1 1,300/3.90; W6b2 720/2.00; W6b3
600/1.46; W6b4 U 1,600/4.95, R 202/1.28, X 192/2.72; N1 440/2.30; B1 600/2.22; U2 1,600/4.22; UF 300/2.67; P1 512/2.37;
S1 1,760/6.71; U3 1,800/4.17; P2 512/1.31; UF2 450/1.63.
Independent origins (distinct initial populations): 21 (W3a discovery), 85 (W6 C1 confirmation), 288 in the uptake
contrasts (121 + 167 over 1,600 pairs).
Reproducibility: deterministic replay 202/202 sampled runs from W1v2, W2, W4, W5, W6 with the final code; 27/27 (W3a) and
75/75 (W3b) replays of discovery runs. Every analysis script committed before its data; every plan hashed at freeze;
every run executed from a pinned code copy (~/bel48h_runs/pins/<freeze commit>).

## 4. Mechanism records

Seven records in the directive's 10-field format: BEL_48H_MECHANISM_DISCOVERY.md (M1 complementation, M2 cryptic-
precursor activation, M3 uptake, M4 distributed persistence, M5 rearrangement accessibility, M6 budget coupling, M7
payment-driven conflict repair). Packets: packets/PACKET_HARMONIA.md, PACKET_ATLAS.md, PACKET_TECHNE_NYX.md.

## 5. Results of the last blocks

U3 (split CL-20; 1,800 runs, 0 voids): blocking all imports raised origination a third time (63 vs 46; 43 vs 26, p 0.027).
Blocking only imports made during a self-copy did nothing (45 vs 46): before the first replicator nobody self-copies, so
the origin gain comes entirely from imports by non-replicating organisms (the UF mechanism). My post-hoc 'staging-copier
self-damage' reading was logically unable to explain an origin effect and is retracted (calibration ledger).
P2 (architecture-payment panel at HIGH mutation; 512 runs, 0 voids): no consistent direction (ON < OFF in 3, > in 2, 5
ties of 10 decided pairings; two-sided p 1.0): the payment effect on architecture is general at MED, indeterminate at
HIGH.
UF2 (450 runs, 0 voids): why CL-20 vanishes in SOUP and at budget 384. The frozen precursor-proxy prediction failed
(SOUP breaks precursors more). Post-hoc: imports destroy more FUNCTIONAL replicators than they create only in the
reference substrate (1.63) -- not at budget 384 (0.77) or in SOUP (0.24) -- matching exactly where the block mattered.

## 6. Closing totals

Runs (excluding 56 pilot, 128 superseded and all smoke runs): 18,862 in 23 blocks, 0 voids, 0 NOT_RUN. Campaign ended on
schedule; no experiment was cut short. Final commits are listed in the execution ledger; branch
bellerophon/def-bel-008-010-2026-10-06 (campaign artifacts), main 2c6072c9d (kernel repairs).
