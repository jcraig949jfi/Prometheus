+=====================================================================+
|  CAMPAIGN 4 -- DAMAGE GEOMETRY AND EVOLVABILITY: CAMPAIGN REPORT      |
|  Lead: Archaeon[m2-49ee5a4d]   2026-09-18   Status: COMPLETE 09:40Z |
|  Campaign started 05:54Z on gate GREEN (readiness receipt 9632e95f8) |
+=====================================================================+

The directive's instruction was: do not improve the story, improve the
machine; do not convert a scientific failure into an engineering task;
give every experiment an attempted disposition; then stop. This report
is the ledger of ten attempted dispositions, in the vocabulary of
DISPOSITION_C4-REH-1.md section 6. Every number below is in a committed
attempt-of-record table under archaeon/campaign4/C4-NN/attempts/, and
every decision is in DECISIONS.md (D4-001..D4-014).

-----------------------------------------------------------------------
0. THE CAMPAIGN QUESTION AND THE ANSWER THE DATA GIVES
-----------------------------------------------------------------------
Asked: can the Foundry expose a region in which edits usually produce
different, bounded, coherent computation rather than no change or
catastrophe, and does access to that region improve later discovery?

Answered, on the frozen substrate (engine 9.0.1 / 699ca0f9, grammar
v0.4, profile pfp1:625bc70456ebfa20, 57 starting program variants):

  * There is no fault boundary to widen. The interpreter is total and
    the foundry writes random words: 932/932 parent instruction words
    are outside the opcode table and the modulo decode IS the
    instruction set (C4-03). D1 cannot fire; D0 never did; "invalid
    operation", "fizzle event" and "free insulation" have no extension
    here (C4-03, C4-07 REPRESENTATION_BLOCKED; C4-08's removal arm too).
  * The damage boundary that does exist is a cliff in behaviour, not a
    slope: at every edit radius tried (1..16), an edit either leaves the
    answer vector untouched or replaces most of it; 1-3% of edits fall
    between (C4-01, C4-02). Genotypic distance predicts the PROBABILITY
    of destruction (loss .52 -> .99 over radii 1..16), not the degree
    of change.
  * No single edit improved any parent on its own environment (D7 = 0
    in 5,472; C4-01), and no multi-step random edit did either (0 in
    2,280; C4-02). Exaptive edits (better elsewhere) are rare (0.6%)
    and concentrated in the shelf stratum.
  * The neutral network is large, fully connected and cheap to walk
    (188/188 walkers reach depth 16 at ~55% acceptance), accumulates
    structure and behavioural difference, and yields held-out
    exaptation that grows with depth (.016 -> .043, 7x a single edit)
    but stays under the preregistered bars (C4-05).
  * Neither the existing recombination (C4-06) nor 100 generations of
    selection on 188 drifted lineages crosses the W2_K2 valley; mate-
    splice births are 8 points less viable and add no novelty.
  * Selection does build robustness -- single-edit loss falls from .42
    to .19 under ordinary load and .13 under doubled load -- but what it
    builds is neutrality and length (coherent share .15 -> .04, genomes
    19 -> 62 instructions, D7 10 -> 0, no structural category to
    ablate): ROBUST_WITHOUT_MECHANISM (C4-08).
  * Stepping stones are real and cheap: a third to a half of a delay
    world's failed children run in W0 and enough run in W2_K2 to enter;
    rescued lineages persist and take over receiving populations, but
    improved the one live world in one seed of three (C4-09).
  * By the preregistered selection rule NO condition decreased
    catastrophic loss AND increased non-trivial variation; C4-10 ran
    the baseline alone on the held-out family. Three of its four worlds
    turned out to be solved by the starting parents at generation 0
    (the delay-general parents solve delays 2 and 3; 8-bit values do
    not trouble a W0 solver); on the one live world (K=2, delay 1) the
    baseline reaches the shelf in 4/4 seeds and nothing above .55
    held-out; per-birth loss .23-.27, non-trivial yield .73-.78.

The campaign claim (directive section 3, C4-10) is therefore NOT made:
the disposition is the preregistered NO_CONDITION_SELECTED, with the
held-out baseline column of the map produced and the baseline
preserved. Nothing was weakened into a positive.

-----------------------------------------------------------------------
1. THE TEN SLOTS (disposition, one line, the number that carries it)
-----------------------------------------------------------------------
  C4-01  damage-boundary census      SUPPORTED (map)   D7 0/5,472; displacement bimodal; TVD .023-.633
  C4-02  radius response curve       SUPPORTED, thin   loss .522/.664/.834/.930/.989; one traversable cell
  C4-03  local failure vs death      REPRESENTATION_BLOCKED (both arms)  932/932 words out of table
  C4-04  addressing damage           NEGATIVE pooled (.087 < .10); insertion +.215, movement +.193
  C4-05  neutral-network walk        NEGATIVE as written; exaptation .016 -> .043 vs .006
  C4-06  recombination / crossing    INCONCLUSIVE; 0/6 and 0/6 crossings; splice -.08 viability
  C4-07  cost of insulation          REPRESENTATION_BLOCKED (no event to cost)
  C4-08  constructed robustness      ROBUST_WITHOUT_MECHANISM; loss .42 -> .13; coherent .15 -> .04
  C4-09  lateral ecology             INCONCLUSIVE; survival .30-.55; improved 1/3 seeds on one live world
  C4-10  held-out trial              NO_CONDITION_SELECTED; live world: shelf 4/4, held-out <= .55; 3 worlds pre-solved
  Attempts: 11 for 10 slots (C4-01 a01 failed at publish, harness
  defect D4-005, preserved; a02 of record). Engine records: 798 + 342
  + 18 + 13 + 57 + 12 + 1 + 4 + 6 + 4 = 1,255. Errors: 0 on every
  attempt of record. Wall time of the science: about 22 minutes of
  compute across the ten slots; the campaign ran 05:54Z to 09:35Z.

-----------------------------------------------------------------------
2. WHAT THE MACHINE LEARNED (the friction ledger)
-----------------------------------------------------------------------
  M1  The execution path. "Execution: Vivarium" could not be honoured
      for science rows: no admissible kind evaluates a program variant
      (D4-001). C4 ran on the campaign-3 harness path; the queue path
      carried the rehearsal only. A kind was asked of Vivarium (#411).
  M2  Every slot refused to run while the launch gate was RED, by
      reading the gate receipt, not prose.
  M3  Rows that are pure functions of seeds are regenerated and
      digest-verified rather than stored twice (C4-03/04/06/08/09:
      thousands of children, 0 mismatches). The walk (C4-05) is
      reproducible from its seeds; C4-06 and C4-08 relied on that.
  M4  Instrument defects caught by self-tests before any real row:
      the removed operator's name, an identity control defined as a
      label instead of a property, non-deterministic timing keys in
      stored rows, a descriptor key mismatch, a walk regenerated at
      the wrong E. Two defects surfaced only in the run: a wrong
      artifact info_kind (C4-01, rerun) and a sign convention in a
      sealed declaration (C4-08, label kept beside the reading).
  M5  Preregistration defects recorded, not repaired: C4-06's shelf
      control tested nothing (walkers start on the shelf); C4-09's
      worlds were not checked against the starting population (three
      pre-solved). C4-10 carries the check.
  M6  Vocabulary: prose in the neutral register throughout; no field
      name, schema or identifier renamed.

-----------------------------------------------------------------------
3. WHAT CAMPAIGN 5 SHOULD BE DERIVED FROM (whichever part proves real)
-----------------------------------------------------------------------
  * A representation with a distinguishable insulation event (a narrow
    in-table encoding, a trap-and-continue on undefined words) is a NEW
    substrate; C4-03/07/08 cannot be asked on this one. Everything
    measured here would need re-measuring there.
  * The neutral network's exaptation gradient (C4-05) and the stepping-
    stone takeover (C4-09) are the two live signals: a deeper walk (32,
    64) and an ecology on UNSOLVED worlds at equal total budget are the
    cheapest next measurements, both preregisterable from this report.
  * The cliff (C4-01/02) is the substrate's answer at every scale
    tried; the shelf stratum is the only place where graded change,
    viable-worse and exaptive edits exist in numbers.

-----------------------------------------------------------------------
4. ARTIFACTS
-----------------------------------------------------------------------
  archaeon/campaign4/DAMAGE_GEOMETRY_MAP.{md,json}  the primary product
  archaeon/campaign4/C4-NN/READOUT.md               per-slot readouts
  archaeon/campaign4/C4-NN/attempts/aNN/            sealed prereg, receipt,
                                                    tables, rows (gzipped
                                                    where large), digests
  archaeon/campaign4/DECISIONS.md                   D4-001..D4-014
  archaeon/campaign4/FUNNEL.json, LEDGER.jsonl      harness accounting
  archaeon/campaign2/REACHABILITY.jsonl             +12 rows (C4-06)
  roles/Archaeon/journal/2026-09-17_m2-49ee5a4d.md  the journal
+=====================================================================+
