# Tyche v0 campaign report (2026-09-30)

Run: tyche/runs/v0_2026-09-30, built from 32fa63544 (clean) on M2
SPECTREX5, 16 workers; Pass D resumed for 11 lenses from e8f9ff4c3
(8 workers) after a harness memory stop. PREREG 075e5fc21, amendments 1
(32fa63544) and 2 (e8f9ff4c3). Machine-readable: REPORT.json (computed by
tyche/report.py, frozen with the prereg), genealogy GENEALOGY.jsonl,
FOSSILS.jsonl, EVALS.jsonl.gz, ADMISSIONS.jsonl, RESIDUALS.jsonl,
PASS_A_BASELINE.json, PASS_D_AUDITS.json.

## Verdicts (preregistered; computed in code)

    H5 instrument          PASS   cheat LEAD lens z=54.9 and REJECTED by
                                  the causality audit; honest lens passes;
                                  44/44 admitted lenses causal
    H2 false gradients     PASS   0 negative worlds (TSD1-4, PRF1-2, TSD7,
                                  PRF3) with a replicated null-beating
                                  gain; 0 admissions on negative worlds
                                  (210 admission tests)
    H1 planted controls    INDET  3/6 VOID (random 1-4 op lenses already
                                  had test gain >= 0.03: P3 0.227, P4
                                  0.109, P6 0.141); valid 3: P2 SOLVED,
                                  P5 SOLVED, P1 NOT SOLVED
    H3 residual shift      FAIL   instrument defect (below)
    H4 redundancy          FAIL   instrument defect (below)
    H6 end to end          INDET  follows H1; 19 lenses admitted in epochs
                                  >= 1 on worlds whose residual had shifted

Labels (annotation 2026-09-30, from Harmonia's ruler-quality audit
e72508448; the computed verdicts above are unchanged):
- H1 and H6: UNREACHABLE_BY_DESIGN (NOTHING_COULD_FIRE for PASS). With
  the fixed initial population P3, P4 and P6 were VOID before any
  generation ran, leaving 3 valid worlds against a rule needing >= 4.
  These are not scientific FAIL/INDETERMINATE results of lens evolution.
  What H1 still says is descriptive: P1 NOT SOLVED, P2 and P5 SOLVED.
- H3 negative-world arm: NON_DISCRIMINATING. Ecology growth alone moves
  the err fraction (Harmonia's random-ecology simulation: 0/20 pass at
  16-48 lenses; F1 below shows the same mechanism in this run's rows).
- H4: Harmonia rated FAIL "nearly unattainable" from the epoch-0
  baselines; it WAS attained, because tab's baseline moves with the
  ecology (F2). Reply posted to Harmonia.
- Informative in v0: H2 and the admission gate (Harmonia: sound; null
  pass about 1e-8 per lens x world), per-world solve status, F1-F4.

## Required report fields (charter)

WORLD FAMILY: planted, tsd (TARGET_STRUCTURE_DESTROYED), prf, known,
  hec_alien, hec_null, adv. 32 worlds, 24 selection, 8 held out.
INITIAL PERFORMANCE: raw ecology, R0 val, planted/tsd/prf: 0.314-0.594
  across organisms, at or near majority except P6 (0.50 vs majority
  0.40: the automaton state partly follows the current input); K1/K2 1.00 (tree);
  K3 tree 0.953, tab 0.740. Full table REPORT.json INITIAL_PERFORMANCE.
INITIAL RESIDUAL: R0 err-fraction at epoch 0, e.g. P2 0.433, PRF1 0.261,
  TSD3 0.405 (REPORT.json INITIAL_RESIDUAL). Near-chance worlds at start:
  P1-P5, TSD1-4, PRF1-2, ADV_alias.
LENS POPULATION SIZE: 96 per generation; 40 generations (4 epochs x 10);
  2368 distinct lenses born.
MUTATION OPERATORS (births): graft 578, temporal 307, point 304, insert
  294, delete 293, replace 287, recur 276, out 275, dup 272, rewire 264.
SURVIVING LINEAGES: 7 root lineages alive at the end (of 96 roots).
DARK ECOLOGY LINEAGES: 14 reserve slots; 146 lenses spent >= 1
  generation in reserve before dying (fossil record).
MARGINAL GAINS: 44 admitted; 39 replicated on 2 fresh seeds, 41 beat the
  matched random null, 37 both. Planted home gains (test): P2 +0.675
  (tree, 3 ops, reps 0.668/0.670), P3 +0.295..+0.325 (tab), P4 +0.18..
  +0.23, P5 +0.236 (reps 0.033/0.218), P6 +0.173 (reps 0.118/0.127).
HELD-OUT PERFORMANCE: P3 sibling (p=0.45): 8 lenses transfer (best
  +0.170, R2 tree). P1 sibling, P7 parity: nothing. K4 xor: 5 lenses
  help lin/tab (+0.08..+0.18). HA_map +0.048 (1 lens). ADV_sparse +0.037.
  PRF3, TSD7: nothing.
TRANSFER PERFORMANCE: LOCAL 12, FAMILY 7, TRANSFER 10, GENERAL 11,
  NOT_REPLICATED 4 (transfer requires fresh-seed replication and beating
  32 matched random lenses on the target world and case).
SHORTCUT AUDITS: causality 44/44 pass; LEAD cheat caught; consequence
  never in observations (tests); matched random null per lens.
FALSIFICATIONS: 5 not replicated; 2 replicated but inside the null
  (L-861fe03cde, L-863275e472); P5/R2/tree seed fragility (3 lenses).
OPAQUE SUCCESSFUL LENSES: 28 (replicated, null-beating, interpretation
  UNKNOWN); effective lengths 1-16. Nobody has interpreted them.
INTERPRETABLE SUCCESSFUL LENSES: 9 PLANTED_INPUTS_RECOVERED (ablation
  set equals the planted law's channels) on P2, P3, P6.
RESIDUAL AFTER EVOLUTION: P2 err 0.433 -> 0.000 (tree acc 0.335 ->
  1.000); P5 R2 0.179 -> 0.101. On negative worlds err fell too (PRF1
  0.261 -> 0.140) with NO accuracy change -- see defects.
REVIVED LINEAGES: 37 of 44 admitted lenses have an ancestor that spent
  time in the reserve. NO base-rate null computed: with 14 slots x 40
  generations most lineages pass through the reserve, so this number is
  not evidence that the reserve mattered.
FAILED LINEAGES: 85 of 96 roots left no admitted descendant.
OPEN ANOMALIES: (1) P5/R2/tree: L-3c1c67ab5c test +0.134 (z 12.3) on the
  selection seed, EXACTLY 0.000 on both fresh seeds; L-31c5492eec +0.159
  vs -0.006/-0.004; L-cd407208ed 0.236 vs 0.033/0.218. (2) best val gain
  on ADV_decoy reached 0.114 (gen ~20-28) then fell to 0.036.
  (3) 2 replicated-but-within-null lenses.
NEXT SEARCH PRESSURE: see "Successors".

## Failure shapes

1. H3 -- the err/dis residual measures organism decorrelation, not
   unexploited information. On negative worlds accuracy is unchanged
   (PRF1 lin 0.495 -> 0.499, tree 0.506 -> 0.491) while err falls 0.261
   -> 0.140 and dis rises 0.492 -> 0.735; same on TSD1, TSD3. Adding
   ecology features makes the three organisms disagree more, so the set
   where ALL are wrong shrinks mechanically. The residual instrument had
   no negative control of its own; it needed one.
2. H4 -- the tab organism's 10-feature attention budget (candidate lens,
   then admitted lenses newest first, then raw) MANUFACTURES residuals:
   tab's baseline on K1_ident goes 1.000, 0.995, 0.547, 0.998, 0.518 over
   the epochs as admitted lenses push the raw channel out of its window;
   a lens that restores the channel then "earns" +0.49. tab accounts for
   28/44 admissions, rising 4, 6, 11, 7 by epoch. P3 tab baseline
   oscillates 0.566, 0.574, 0.866, 0.558, 0.547 (R0). On P2 the tree lens
   admitted in epoch 0 lifted tree to 1.000, but tab's baseline stayed at
   0.338-0.362 all run: the oldest ecology lens never sat inside tab's
   window, so the three later P2 tab admissions were credited for
   information the ecology already held. The observer's architecture created a dark
   residual and evolution solved the residual it created.
3. H1 -- search follows partial gradients and misses needles. Laws with
   partial information (window majority, gate, automaton) were reachable
   by random lenses, so they were not valid "inaccessible" controls. P2
   (running count mod 3) and P5 (sign of delayed product) were solved
   from chance. P1 (delayed XOR, delays 4 and 11: each half carries zero
   marginal information) stayed at the noise floor (best val gain 0.029-
   0.037) for all 40 generations; P7 (3-way parity, held out) and the
   xor inside ADV_decoy were never reached either.

## Successors (frontier replenishment, ordered)

S1 instrument: remove the attention-budget displacement (tab sees a
   fixed feature set independent of ecology order) and re-run the H4
   check. S2 instrument: a residual with its own negative control -- it
   must stay flat on TSD/PRF worlds as the ecology grows (e.g. held-out
   log-loss of one fixed reference organism on all ecology features).
S3 science: the XOR needle -- is zero-marginal structure reachable by
   any operator in the chemistry (pairwise interaction search, experiment
   organisms that perturb two channels jointly, recombination of two
   single-delay lenses)? P1, P7, ADV_decoy are the targets; initial access
   measured over the whole initial population. S4: P5/R2 seed-fragility
   anomaly. S5: base-rate null for "revived lineage" (fraction of ALL
   lenses with a reserve ancestor). S6: bound ecology growth (cost rose
   2 s -> 18 s per generation; features x worlds x organisms).
