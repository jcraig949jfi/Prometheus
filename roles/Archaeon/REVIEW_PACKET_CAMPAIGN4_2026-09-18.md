+=====================================================================+
|  REVIEW PACKET -- CAMPAIGN 4: DAMAGE GEOMETRY AND EVOLVABILITY         |
|  Archaeon[m2-49ee5a4d]  (lead, M2 / SPECTREX5)   2026-09-18 09:50Z   |
|  For: the operator (HITL) and external reviewers                     |
|  Status: campaign COMPLETE, ten attempted dispositions; campaign     |
|          disposition NO_CONDITION_SELECTED                           |
|  Self-contained: every load-bearing number is inline.                |
+=====================================================================+

-----------------------------------------------------------------------
0. MANDATE AND VERDICT
-----------------------------------------------------------------------
Mandate (operator directive, verbatim on file): ten sequential
experiments on the frozen substrate, no operator, no HITL; every
experiment gets an attempted disposition; harness defects may be
repaired and rerun with the failed attempt preserved; no scientific
failure converted into an engineering task; no ISA change; then stop.

Verdict: the campaign ran 05:54Z-09:35Z on a green launch gate, all ten
slots have preregistered designs (committed before any row), sealed
preregistrations, receipts and readouts; 1,255 engine records, 0
errors on every attempt of record. The directive's three-part claim
(less lost at the boundary; recovered mass non-trivial; greater reach)
is NOT made: no condition qualified for the held-out trial under the
rule fixed before the qualifying slots reported. Two slots and one arm
are REPRESENTATION_BLOCKED for a measured reason.

-----------------------------------------------------------------------
1. THE SUBSTRATE FACT THAT SHAPED THE CAMPAIGN (measured, not assumed)
-----------------------------------------------------------------------
The interpreter is total: opcode words are reduced modulo the 25-entry
table, operands modulo register and tape counts, jumps modulo the tape;
the status vocabulary is halt / yield / budget. The foundry writes
uniformly random 32-bit words, so 932 of 932 instruction words in the
57 starting program variants are outside the table, and P("would-be-
fatal") = 1.000 on all 7,146 regenerated children (Wilson lower bound
.9992). There is no invalid operation, no fizzle event distinct from
execution, no free insulation to remove. D1 (execution fault) cannot
fire; D0 (undecodable) never did. C4-03 and C4-07 closed
REPRESENTATION_BLOCKED; C4-08's "insulation removed" arm likewise. The
directive forbids fixing this during the campaign; it is recorded as a
Campaign 5 premise.

-----------------------------------------------------------------------
2. WHAT WAS MEASURED (the ten slots)
-----------------------------------------------------------------------
C4-01 census  57 parents x 12 operators x 8 draws (5,472 edits) on five
  environments under common random numbers; controls: identity 57/57,
  whole-genome randomization destroyed 56/57 (floor 45). No single edit
  improved any parent (D7 0/5,472). Displacement is bimodal: 0 or > .75,
  1-3% between. Loss (D2+D3) by operator .15 (unreachable_removal, 65%
  cannot apply) .. .76 (randomization); pairwise TVD .023-.633. The 12
  gen0_random parents are degenerate themselves (identity D2 12/12).
  Exaptive edits 34 (0.6%), 30 on shelf parents.
C4-02 radius  57 x {1,2,4,8,16} x 8: loss .522/.664/.834/.930/.989;
  neutral .467 -> .004; displacement bimodal at every radius; variance
  falls; one traversable cell (shelf, r2); D7 0/2,280; radius-1
  distribution within TVD .029 of C4-01's weighted mixture.
C4-03 HARD/FIZZLE  both arms REPRESENTATION_BLOCKED (section 1); the
  proxy's vacuity check, added before any row, fired.
C4-04 addressing  static reference resolution on 4,866 regenerated
  children (digests 4,866/4,866): P(broken jump | length-changing edit
  with a reachable jump) .423; loss .640 broken vs .552 intact pooled
  (prediction .10 LOST at .087); insertion +.215, movement +.193,
  deletion/splice/duplication ~0; every viable stratum positive; the
  executed addressing-mode comparison REPRESENTATION_BLOCKED.
C4-05 walk  188/188 walkers reach depth 16 inside a 1/16 band at ~.55
  acceptance, flat over depth; structural diversity .30 -> .76; held-out
  exaptation .016/.032/.037/.043 at depths 2/4/8/16 (single edit .006;
  shelf .079; delay-general 0). Both preregistered bars missed by
  .013-.023; NEGATIVE as written, gradient recorded.
C4-06 recombination  188 depth-16 walkers, W2_K2 summit, 2 arms x 6
  seeds, N=200 G=100: crossings 0/6 and 0/6; mate-splice births .734
  viable vs .815-.820 (prediction .10 LOST at .081); no novelty
  difference; INCONCLUSIVE; harness TARGET_UNREACHABLE (0/12).
C4-07 cost of insulation  REPRESENTATION_BLOCKED (no event to cost;
  pricing reduced operands would price the representation).
C4-08 constructed robustness  fresh assay on 188 ancestral / 192
  ordinary / 192 doubled-load descendants: single-edit loss .419 / .185
  / .125 (bands apart); coherent share .149 / .077 / .044; D7 10/0/0;
  mean length 19 / 40 / 62 instructions; no category share differs by
  .10 (ablation NOT_EXAMINED). ROBUST_WITHOUT_MECHANISM: selection
  builds neutrality and length; load is not required (P2 lost).
C4-09 ecology  4 worlds x N=50 x G=100, 3 seeds: rescues 335-460 per
  seed, survival .30-.55, rescued lineages take over receiving
  populations; three worlds were pre-solved by the walkers (defect,
  recorded), the live world improved in 1/3 seeds (+.094); extra
  compute .65-.74. INCONCLUSIVE.
C4-10 trial  rule-selected conditions: NONE; baseline alone on
  W1_d2 / W1_d3 / W2_K2d1 / W0_8b: three pre-solved by the parents
  (drop rule computed, not applied: defect recorded); live world
  W2_K2d1 shelf 4/4, held-out <= .55, per-birth loss .23-.27, non-
  trivial yield .73-.78. NO_CONDITION_SELECTED.

-----------------------------------------------------------------------
3. THE MAP (archaeon/campaign4/DAMAGE_GEOMETRY_MAP.md; the product)
-----------------------------------------------------------------------
  condition                     mag   degen  neutral coherent viable exapt
  single edit, best operator     1     .294   .667    .040    .680   .002
  single edit, worst operator    1     .638   .217    .145    .243   .011
  single edit, shelf stratum     1     .266   .602    .133    .646   .019
  single edit, delay stratum     1     .390   .422    .190    .430   .000
  radius 2 / 4 / 8 / 16         2-16   .546/.713/.809/.903  .305/.147/.046/.004
  ancestral walkers on W2_K2     1      -     .538    .149    .581    -
  selected descendants (load)    1      -     .863    .044    .875    -
  held-out family, baseline    birth    -      -       -      .740    -
  Fatal loss is 0 in every row by construction. Descendant consequence:
  neutral network fully connected (C4-05), no valley crossed (C4-06),
  robustness = neutrality + length (C4-08), rescue = takeover without
  improvement (C4-09).

-----------------------------------------------------------------------
4. INCIDENTS AND DEFECTS (mine, recorded, not smoothed)
-----------------------------------------------------------------------
  I-1  C4-01 a01 failed at the last publish (artifact info_kind not one
       of the engine's five) after 798 records landed; repaired, rerun
       as a02 which resumed a01 (803 steps replayed); a01 preserved.
  I-2  Five instrument defects caught by self-tests before any row
       (wrong removed-operator name; identity control as a label; timing
       keys in stored rows; descriptor key; walk regenerated at wrong E).
  I-3  C4-08's sealed declaration used a signed min_effect the harness
       read the wrong way; label kept beside the preregistered reading.
  I-4  C4-06's shelf control tests nothing (walkers start on the shelf).
  I-5  C4-09's worlds and C4-10's family were not checked against the
       starting population before the run (three pre-solved in each);
       C4-10's drop rule was computed and not applied. Nothing re-run
       after seeing results.
  I-6  "Execution: Vivarium" not honoured for science rows: no queue
       kind evaluates a program variant (D4-001; asked, #411). Science
       ran on the campaign-3 harness path; the queue carried the
       rehearsal.

-----------------------------------------------------------------------
5. WHAT THIS DOES AND DOES NOT ESTABLISH
-----------------------------------------------------------------------
Establishes, on this substrate: the shape of the damage boundary (a
cliff at every radius; distance predicts probability of destruction,
not degree of change); the absence of one-step and multi-step random
improvement from these 57 starting points; a large connected neutral
network whose exaptive yield grows slowly with depth; that selection
builds neutrality rather than preserved variation; that lateral rescue
is cheap and invasive. Does not establish: anything about a substrate
with a fault boundary; any mechanism; what a deeper walk, an unsolved
ecology at equal total budget, or more seeds would show. Claim ceiling
per slot is in each READOUT.

-----------------------------------------------------------------------
6. RECOMMENDATION (the lead's lean; the operator's call)
-----------------------------------------------------------------------
Do not build Campaign 5 automatically (the directive). Two cheap,
preregisterable follow-ups exist inside this substrate: the walk at
depths 32/64 (does the .016 -> .043 gradient continue?) and the ecology
on UNSOLVED worlds at equal total budget (is takeover ever
improvement?). The larger move is a representation with a real
insulation event, which reopens C4-03/07/08 as questions and re-
measures everything. "Not worth continuing on this substrate" is a
legitimate reading of sections 1-3: the substrate's answer to "where
can computation move" is "on its neutral network, sideways", and no
tested intervention changed that.

-----------------------------------------------------------------------
7. QUESTIONS FOR THE REVIEWER (written to resist agreement)
-----------------------------------------------------------------------
  Q1  Is the total-interpreter finding (section 1) a property of the
      foundry's word generator rather than of the ISA? A generator
      that wrote in-table opcodes would make C4-03/07 askable without
      changing the interpreter. Is that an ISA change or a foundry
      change under the directive's rule?
  Q2  The displacement metric is a Hamming distance over answer vectors
      on 16 episodes. Could a finer behavioural distance turn the cliff
      into a slope?
  Q3  C4-08's robustness is confounded with a tripling of length. Would
      a length-matched fresh assay change the reading?
  Q4  C4-05 and C4-09 both show gradients under their bars. Were the
      bars (.05) set too high for the sample sizes chosen?
  Q5  The selection rule for C4-10 required coherent share to INCREASE.
      Is neutrality-building robustness "inert" by definition, or is
      that a choice the rule made?

-----------------------------------------------------------------------
8. ARTIFACTS
-----------------------------------------------------------------------
  archaeon/campaign4/CAMPAIGN_REPORT.md, DAMAGE_GEOMETRY_MAP.{md,json},
  DECISIONS.md (D4-001..014), C4-NN/DESIGN.md + READOUT.md + attempts/,
  FUNNEL.json; roles/Archaeon/journal/2026-09-17_m2-49ee5a4d.md.
  Commits on main: 9632e95f8 (readiness receipt) .. 8f1a82ced
  (campaign complete). Comms: 425 (started), 428/431/432/433/436/440/
  442/443/444 (per-slot and completion).
+=====================================================================+
|  END. "Not worth continuing" is a first-class answer here; section  |
|  6 gives it and the two cheap alternatives.                          |
+=====================================================================+
