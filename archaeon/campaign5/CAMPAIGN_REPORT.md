+=====================================================================+
|  CAMPAIGN 5 -- ESCAPE THE NEUTRAL CLIFF: CAMPAIGN REPORT              |
|  Archaeon[m2-49ee5a4d]   2026-09-18   ten slots, 14:16Z - 15:07Z     |
|  FINAL DISPOSITION: BOUNDARY_CREATED_NO_DISCOVERY_GAIN               |
|  (Phase A: OLD_SUBSTRATE_EXHAUSTED; C5-10: NO_CONDITION_SELECTED)    |
+=====================================================================+

0. THE ANSWER THE DIRECTIVE ASKED FOR
-----------------------------------------------------------------------
A real local failure boundary was created (representation B: a narrow
in-table encoding of the same 25-opcode table, Proteus's VM untouched)
and qualified. At the single-edit level it did MORE than change how
programs die: when a crossing edit's fault is executed, skipping it
preserves function that reinterpretation lost in 229 replicated cases
against 154 of the reverse, at no measurable cost to the program that
survives. That is a region of bounded variation -- the surviving child
is its parent with a hole in it, displacement .015 -- and it is not a
region from which evolution discovers more efficiently: at equal total
compute on four worlds with measured headroom, no arm under either
representation raised an elite's held-out reward by a band in any of
96 cells, and the held-out rule selected no condition. The neutral
cliff was not escaped; it was described one level deeper.

1. WHAT WAS DONE (ten slots, no HITL, every attempt preserved)
-----------------------------------------------------------------------
  slot   result                                            attempts
  C5-01  deep neutral walk: MIXED; PRESERVE_NEUTRAL NO       a01
  C5-02  fair lateral ecology: A_TAKEOVER_WITHOUT_IMPROVEMENT a01
         Phase A -> OLD_SUBSTRATE_EXHAUSTED (D5-009)
  C5-03  representation qualification: a01 FAILED its own
         text; a02 REPRESENTATION_QUALIFIED under a labelled
         post-hoc amendment (D5-008)                         a01, a02
  C5-04  generator x representation: P1-P4 hold              a01
  C5-05  damage geometry under B: C4-01 replicated
         5,586/5,586; boundary fires .84-.86; D5 of
         non-crossing children unchanged                     a01
  C5-06  local failure vs recovery: REAL_LOCAL_RECOVERY       a01 (path
         (229 vs 154, replicated on held-out episodes)       defect), a02
  C5-07  cost of insulation: INSULATION_CHEAP                 a01
  C5-08  robustness mechanism: MIXED (length yes, dead code
         no, boundary component .021 independent of both)    a01
  C5-09  reach/discovery at equal compute: NO_GAIN            a01 (control
                                                              defect), a02
  C5-10  held-out trial: NO_CONDITION_SELECTED                a01, a02
  Execution path: the campaign harness under client cmp5-archaeon,
  campaign seed 20260922 (D5-001); Vivarium's wse_evaluate_v1 did not
  exist and cannot evaluate representation B. Worlds: every world used
  for an improvement claim was screened for pre-solution against all
  57 starting parents with the rule in code BEFORE any preregistration
  (WORLD_SCREEN_2026-09-18.json: 9 eligible of 25). Controls: equal
  total compute in C5-02 (control run 162-180 generations to match the
  lateral arm's evaluations within one generation) and by construction
  in C5-09/C5-10. Ancestry preserved (origins unioned at every birth;
  elite ancestry chains recorded).

2. PHASE A -- THE OLD SUBSTRATE, TESTED FAIRLY
-----------------------------------------------------------------------
C5-01 (282 walkers x 64 accepted steps; C4-05 replicated 3,648/3,648):
  exaptation .050 / .064 / .078 / .082 at depth 16/32/48/64 (Wilson at
  64: [.055,.119]); the marginal rate per step falls fourfold in the
  last quarter; yield per evaluation .00127 -> .00082 against a random
  single edit's .0012. The gradient is real and it is bought by
  evaluations a single edit spends at least as well. Rule (D5-003):
  PRESERVE iff continued gradient AND yield >= 2x a single edit's -> NO.
C5-02 (four screened worlds, 6 seeds, lateral vs equal-compute control):
  0 of 24 cells improved by a band in either direction; rescued
  lineages take the population (.83/.67/.50/.20) without moving the
  elite; in most cells the elite IS the starting parent after 36,000
  evaluations. Prediction (class B on W3_K3/W4_K4) lost.
Neither mechanism is preserved. The stronger fact is the flat elite:
selection under the frozen grammar does not climb these worlds at all.

3. PHASE B -- THE BOUNDARY
-----------------------------------------------------------------------
3.1 Representation B (C5-03). Opcode word defined iff < 25; register
  field the opcode reads defined iff < n_regs; else FAULT. FAIL ends
  the evaluation; FIZZLE skips and counts. canonicalize(P) carries the
  old meaning across exactly (57/57). Populations separate without
  fitness: static validity raw .00 / valid 1.00 / injected(k) exactly k
  (TVD 1.0); trap share 1.00 / .01 / .84; FAIL/FIZZLE coherent 100%;
  fault sites <= k in 100% of non-writable injected programs; 32/200
  raw programs answer under OLD and trap under B.
  THE AMENDMENT (read this): a01 failed on F3's raw-vs-injected(2)
  fault-COUNT TVD (.42 < .50) and on F6 (volatile timings compared).
  a02 measures that one pair by distinct SITES at the same threshold
  (.785) and strips timings. A post-hoc change of statistic, labelled
  D5-008; the operator may overrule it, in which case C5-03 is
  REPRESENTATION_FAILURE and sections 3.2-3.7 are void.
3.2 Generator x representation (C5-04, 27 cells, no selection): under
  the total interpreter the generator is neutral (raw .170 vs valid
  .152 viable); under B raw programs are dead in both modes (.000);
  two injected faults leave .118 viable under FIZZLE vs .017 under
  FAIL; no sampled program of any kind reaches the floor (.000 in all
  27 cells -- the starting population's competence was selection's).
3.3 Damage geometry (C5-05; DAMAGE_GEOMETRY_MAP_V2.md). C4-01's census
  replicated digest for digest. Crossing share of children: grammar
  v0.4 .386, grammar B .055. The boundary fires on .84/.86 of crossing
  children and changes nothing for the rest (D5 .441 vs .442). Under
  v0.4, TRAP (.327) comes equally out of D2 (.451 -> .293) and D5
  (.439 -> .311): half of the crossing edits were silently lethal,
  half silently neutral. D6 is .006-.008 everywhere (prediction that
  FAIL cuts it: lost). D7 = 0 under every interpreter and grammar.
3.4 Local failure vs local recovery (C5-06; 1,449 executed-crossing
  children of 47 competent parents, matched under OLD / FAIL / FIZZLE):
      RECOVERY 234 (229 replicated on held-out episodes, 3 rng seeds)
      INSULATION_LOSS 157 (154)   BOTH_LIVE 591   BOTH_DIE 467
  Opcode faults recover (209 vs 15): reinterpreted, a broken opcode is
  a random instruction and kills; skipped, it is a NOP. Register faults
  are lost (142 vs 25): wrapped, a broken register index still names a
  register; skipped, the instruction's effect is gone. Insertion is the
  rescued operator (102 recoveries, 0 losses). Under grammar B alone
  the trade is 15 recoveries for 34 losses. Gate for C5-07: 229 >= 10,
  Wilson lower .140 > .01 -> REAL_LOCAL_RECOVERY; "merely changed how
  programs die" (loss >= recovery): NO.
3.5 Cost of insulation (C5-07, 229 recovered children): ops ratio to
  parent median 1.00 (2% above 1.10x); second-edit neutrality +.023
  (children slightly MORE robust; 64 above their parent by a band, 30
  below); 4.4% lose function on another environment. INSULATION_CHEAP
  for the survivor; the cost sits on the register-fault class.
3.6 Robustness mechanism (C5-08): removing the 11% of statically dead
  instructions moves the neutral share .435 -> .409 (one length bin
  over the band; M1 fails); length carries it (.17 -> .46 -> .57 ->
  .71 across bins); the boundary's own component (FIZZLE - FAIL) is
  .021 with and without dead code. Reading MIXED. C4-07's "neutrality
  + length" is corrected to LENGTH + behavioural neutrality; its
  numbers stand.
3.7 Reach at equal compute (C5-09; OLD_v04 / OLD_B / B_FAIL / B_FIZZLE
  x 4 screened worlds x 6 seeds; identical starting programs, N=50,
  G=100, E=16): cells vs OLD_v04 won/lost/tied  OLD_B 0/0/24, B_FAIL
  1/0/23, B_FIZZLE 1/0/23 (the one cell: W2_K2_rand seed 4, +.094, the
  cell where C5-02's control also found a step). First held-out gain
  over the starting best: NONE in 96 cells. Under FIZZLE the final
  populations carry executed faults in .46-.80 of members -- hidden
  load with nothing bought. Reading NO_GAIN; prediction (NO_GAIN) held.
  a01 was INSTRUMENT_INVALID by its own kill rule (the determinism
  control compared wall_s); a02 re-ran under the fixed control with
  the same numbers.
3.8 Held-out trial (C5-10): RULE.md (committed 14:36Z, before C5-04 and
  C5-05 ran) selects a condition only at net >= +4 with the grammar-only
  arm below +4. Nets 0 / +1 / +1 -> NO_CONDITION_SELECTED. The held-out
  worlds W3_K3d1 and W2_K2d4 were never run.

4. DEFECTS AND DEPARTURES, PLAINLY
-----------------------------------------------------------------------
  D1  C5-03 a01 failed its own text; a02 under a post-hoc statistic
      change (D5-008). The only departure from "no post-hoc movement".
  D2  C5-05 wrote its children artifact to the slot directory
      (att.dir vs att.path); moved into attempts/a01, runner fixed;
      C5-06 a01 crashed on it and is preserved.
  D3  C5-09 a01's determinism control compared a volatile timing and
      read False -> INSTRUMENT_INVALID by rule; a02 re-run; C5-10 a01
      re-run as a02 on it.
  D4  Readout timestamps were written ahead of the clock (local time
      labelled Z, then guessed); corrected from the attempt receipts
      (D5-011 gives the design-file times precisely: C5-07's and
      C5-10's DESIGN.md were written in the minute C5-05's summary was
      read; C5-10's binding RULE.md and the C5-06/08/09 designs were
      earlier).
  D5  Harness decl readings (UNDERPOWERED on C5-04/C5-07/C5-09-style
      row counts, WEAK_POSITIVE on C5-03/C5-06, INCONCLUSIVE on C5-10)
      are the machine's mechanical labels; the preregistered readings
      are in each READOUT (D5-012), as with C4-08.
  D6  The harness receipt's "campaign" field still says cmp2 (a runner
      fossil since campaign 3); campaign_seed 20260922 and client
      cmp5-archaeon identify the rows.

5. WHAT THIS DOES AND DOES NOT ESTABLISH
-----------------------------------------------------------------------
Established (each with its preregistered rule and attempt of record):
the old substrate's two live signals do not survive fair tests; a
narrow encoding creates a real, countable local failure; the two
encodings fail in opposite directions on opcode vs register faults;
recovery is cheap for the survivor; robustness is length, not dead
code; none of it moves discovery at equal compute on worlds with
headroom. Not established: anything about worlds that evolution CAN
climb (no arm climbed any); anything about longer runs, larger N, or
a grammar whose crossing rate is tuned; whether a FAIL boundary at the
ADDRESS level (rejected in D5-007) would behave differently. The C5-03
amendment is the one thing a reviewer may reject outright.

6. DISPOSITION
-----------------------------------------------------------------------
Phase A: OLD_SUBSTRATE_EXHAUSTED. Phase B: the boundary was created
and qualified; C5-06 says it did not merely change how programs die;
C5-09/C5-10 say the bounded variation it creates buys no discovery.
FINAL: BOUNDARY_CREATED_NO_DISCOVERY_GAIN (C5-10 NO_CONDITION_SELECTED
recorded as the rule's success). No affirmative answer was optimized
for; the one prediction written to be lost that favoured the boundary
(C5-05 T3) lost, and the one that disfavoured it (C5-09 NO_GAIN) held.

7. ARTIFACTS
-----------------------------------------------------------------------
  archaeon/campaign5/  DECISIONS.md (D5-001..014), CAMPAIGN_REPORT.md,
    DAMAGE_GEOMETRY_MAP_V2.{md,json}, REPRESENTATION_COMPARISON.md,
    WORLD_SCREEN_2026-09-18.json, C5-NN/{DESIGN,READOUT}.md,
    C5-NN/attempts/aNN/{PREREG,RECEIPT,rows,...}.json, C5-10/RULE.md,
    repb/ (vm_b, gen_b, grammar_b, evaluate_b, evolve_b), c5_NN.py,
    FUNNEL.json, LEDGER.jsonl (local).
  roles/Archaeon/prompts/2026-09-18_campaign5/ (directive verbatim,
    Phase A report packet, MANIFEST.md).
  Commits: campaign opened at f01a00f58; C5-01 2999623c9; Phase A
    823356eec; RULE aad7e9ca0; C5-05 0632ec92b; C5-06 f44c31a31;
    C5-07/08 aac15fe02; C5-09 a01 0b0a75d5d; cf841ed6d (campaign close); 8e0eff852 (packet).
    (this file: the commit after 8e0eff852).
+=====================================================================+
