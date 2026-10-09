# BEL-48H FINAL REPORT -- Bellerophon, campaign BEL-48H-2026-10-08 (DRAFT at the campaign midpoint; finalised at close)

Directive: roles/Bellerophon/prompts/2026-10-08_bel48h/ (verbatim + MANIFEST). Clock: 2026-10-08T05:14Z -> 2026-10-10T05:14Z.
Host ubu005 (8 cores, 22 GB; at most 6 + 2 campaign workers; the host's prometheus-worker service untouched).
Preregistration: BEL_48H_PREREG.md (17 sections, 2 amendments, 5 errata, 1 disclosure). Execution:
BEL_48H_EXECUTION_LEDGER.jsonl. Claims: BEL_48H_CAUSAL_LEDGER.jsonl. Window reports: BEL_48H_CORRECTED_BASELINE.md,
BEL_48H_HEREDITY.md, BEL_48H_REACHABILITY.md, BEL_48H_COMPUTATION_REPRODUCTION.md, BEL_48H_MECHANISM_DISCOVERY.md,
BEL_48H_FAILURE_BOUNDARIES.md, BEL_48H_NEXT_EXPERIMENTS.md; review record BEL_48H_REVIEW_RECORD.md.

## The twelve questions

**1. Which repaired instruments survived adversarial review?** All three, after repair and with disclosed limits.
Review A (implementation) failed DEF-BEL-008 as shipped (one-hop provenance: 22-62% of 'capture' labels wrong) and
found a zero-sweep hole in DEF-BEL-010; both fixed (multi-hop material origin in the VM, dc1833bc2), byte-identity
re-verified (478 cases + golden), merged to main 2c6072c9d; Nestor notified (#1884). Review B (scientific validity):
SOUND_WITH_LIMITS -- PROVENANCE is material ancestry not parentage; PAIRED aligns initialisation only (no variance
reduction; confirmed: ratio 0.9998, divergence at tick 1 in 150/150); 'written' is a single-execution near-copy test.

**2. Which historical findings survived corrected measurement?** Spontaneous self-replication and its rates (6/7 cells;
BYTECODE32 not reproduced), the sustained fraction (34.8% vs 39.4%), SR-level statistics (0.02% ruler difference), the
coupling campaign's P1-P4 and -- now with power -- its failed P6 (conflict repair 10/300 vs 0/300; reproduced 15/300).
Did NOT survive: lineage-level statistics in mixing worlds (22-26% of living organisms change genetic root between
rulers); G6a in its published form (already withdrawn 2026-09-29; corrected form reproduced); pooled origin counts as
'independent' (grounding 160 origins = 83 populations).

**3. What did we learn about genetic inheritance?** Function is inherited without lineage continuity: capability
persists in 98/100 worlds while the first assembled lineage survives in 36/100 and in 42/100 no assembly lineage is
alive (REPRODUCED). Heritable machinery can be assembled from two non-replicating sources (CAUSALLY_CONFIRMED, general
across 3 confound-free variants) and imported horizontally (uptake). Random founder material contributes almost
nothing to working machines; their critical bytes are post-founding changes.

**4. How do new replicators arise?** By a single change (54/75) that activates a non-copying precursor (60/85) which
other organisms' imperfect copying assembled (56/85): mutation 53, uptake 13, born-assembly 10, self-move 7, self-
construct 2 of 85 independent unseen populations (REPRODUCED). LDIR is indispensable (85/85).

**5. Incremental or atomic?** Neither in the usual sense: activation of cryptic precursors. Which operator completes a
precursor is predictable from its neighbourhood: needle precursors need point mutation (completion 0.14 -> 0.78 from
VLOW to HIGH mutation), move-rich ones are completed by the copy dynamics regardless (0.98 -> 1.00) (CAUSALLY_CONFIRMED,
N1). Substitution-based reachability rulers are blind to this (fault-line).

**6. Can useful computation influence hereditary success?** Yes, causally: contingent payment raises competent self-
replicators (ON 10/300 vs OFF 0/300; ECHO 20/150 vs 0 vs 3 SHUFFLED; reproduced 15/300 and 41/300).

**7. Did any reproductive mechanism preserve task competence?** Two architectures: compute-then-copy (separated) and
copy-then-compute (budget-coupled: the copy-length operand is competence-critical because an unbounded copy starves the
task of the shared step budget; vanishes when the budget exceeds the copy cost: 0.52 -> 0.00). Payment favours the
compute-first form at MED mutation in two independent specimen pairs (23/24, 24/24).

**8. Did a novel reproductive architecture emerge?** Fragment complementation (two non-replicators -> heritable
replicator), horizontal uptake as a route to the FIRST replicator, and distributed persistence (re-making instead of
descent). Uptake is simultaneously a route and a net suppressor: blocking it RAISES origination 38% (84 vs 61 of 800
pairs, p 0.018; fresh-seed replication U2 running).

**9. Which findings survived transplantation?** Complementation transplanted to new operands, offsets and a writer with no
copy routine (120/120 two-source first events); precursors re-placed in new worlds behave by their neighbourhood class
(N1); the architecture-payment effect at MED transplanted to a second specimen pair; the HIGH-mutation architecture
effect did NOT.

**10. Which hypotheses were falsified?** W1-P7 (from a withdrawn figure), W1-P9, W2-P1..P4, W2-P6, W3-P2, W4-P5 (as
written), W5-P1, W5-P4, W5-P7, C1-P6 (as written), X-P6; and my own W4 mechanism claim (answer 'through the child
copy', retracted 0/20).

**11. Which mechanisms deserve another multi-day campaign?** (a) Uptake as creator and suppressor of replicators (route
economics); (b) operator-matched completion as a general theory of reachability under copy physics; (c) architecture
selection under payment across mutation regimes with a specimen panel.

**12. What should Bellerophon investigate next?** BEL_48H_NEXT_EXPERIMENTS.md (ranked).

## Receipts (updated at close)

Runs executed (all lanes, excluding smoke tests and superseded W1): see the execution ledger; voids so far 0 in every
completed block. Deterministic replay: 202/202 sampled (all confirmatory windows), 27/27 (W3a), 75/75 (W3b).
