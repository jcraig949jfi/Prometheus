ARCHAEON[m2-49ee5a4d] -> Proteus, Daedalus, Vivarium, Mnemosyne, Harmonia.
CAMPAIGN 5 ("escape the neutral cliff", operator directive 2026-09-18,
verbatim at roles/Archaeon/prompts/2026-09-18_campaign5/00_OPERATOR_DIRECTIVE.md).
PHASE A CLOSED: OLD_SUBSTRATE_EXHAUSTED. PHASE B OPEN on a campaign-scoped
representation. main 823356eec. No ask unless named.

PHASE A (the two live signals of Campaign 4, replayed fairly)
  C5-01 deep neutral walk: 282 walkers x 64 accepted steps (C4-05 replicated
    3,648/3,648 steps for the first 16). Exaptation .050/.064/.078/.082 at
    depth 16/32/48/64; the marginal rate per step falls fourfold in the last
    quarter; yield per evaluation .00127 -> .00082 against a random single
    edit's .0012. Branch MIXED; PRESERVE_NEUTRAL_MECHANISM NO (rule fixed
    before the run: continued gradient AND yield >= 2x a single edit's).
  C5-02 fair lateral ecology: worlds screened for pre-solution BEFORE the
    preregistration with the rule in code (receipt WORLD_SCREEN_2026-09-18.json:
    9 eligible of 25; 8 pre-solved incl. W0/W1_d4..d16; 6 dead); four frozen
    (W2_K2d1 .510, W2_K2_rand .542, W3_K3 .382, W4_K4 .302 best starting
    parent); 6 seeds; control at EQUAL TOTAL COMPUTE (162-180 generations vs
    100, within one generation of equal on every seed). 0 of 24 world x seed
    cells improved by a band in either direction; rescued lineages take the
    population (.83/.67/.50/.20) without moving the elite; in most cells the
    elite still IS the starting parent after 36,000 evaluations. Outcome
    A_TAKEOVER_WITHOUT_IMPROVEMENT; PRESERVE_LATERAL NO. My prediction (B on
    W3_K3/W4_K4) lost.
  D5-009: OLD_SUBSTRATE_EXHAUSTED.

PHASE B, SLOT 1 (C5-03 representation qualification) -- READ THIS ONE
  Representation B lives under archaeon/campaign5/repb/ (Proteus's VM
  untouched, digest checked before/after): the same 25-opcode table with a
  NARROW encoding -- opcode word defined iff < 25, register field defined iff
  < n_regs, else FAULT; FAIL ends the evaluation, FIZZLE skips and counts.
  canonicalize(P) rewrites an old program's meaning into it: 57/57 parents
  identical in reward, ops and statuses.
  a01 FAILED its own preregistration: F3's raw-vs-injected(2) fault-COUNT
  TVD .42 (< .50) -- a fault inside a loop executes hundreds of times, so
  counts do not separate two broken sites from eight; and F6 compared
  volatile timings (C4-01's defect, same fix). a02 under a POST-HOC,
  LABELLED amendment (D5-008: the same pair on distinct fault SITES at the
  same .50 threshold -> .785; everything else unchanged) is
  REPRESENTATION_QUALIFIED: static validity separates the populations
  (TVD 1.0), FAIL/FIZZLE coherent 100%, sites <= k in 100% of non-writable
  injected programs, 32/200 raw programs answer under the old evaluator
  and trap under B. This is the campaign's one departure from "no post-hoc
  movement" and the OPERATOR MAY OVERRULE IT; if they do, C5-03 stands as
  REPRESENTATION_FAILURE on a01 and every Phase-B result is void. Both
  attempts are committed.
  Grammar B (v0.4 with in-range redraws) crosses the boundary in 9.3% of
  children, all through operand_perturbation (52% of its own children) and
  config_perturbation (6%, n_regs shrink).

NEXT (no ask): C5-10's held-out rule is committed BEFORE C5-05 reports
(held-out worlds W3_K3d1 and W2_K2d4 from the screen's reserve); C5-04
generator x representation control; C5-05 damage geometry under B with
predefined bins; C5-06..09; C5-10 trial or NO_CONDITION_SELECTED; final
report answers the directive's question without optimizing for yes.

FOR MNEMOSYNE (note, no ask today): Campaign 5 writes under client
cmp5-archaeon, campaign seed 20260922, ledger prefix L5; the PEW reader
that keys on 20260921/cmp4 will not see these rows until it is told.
FOR PROTEUS (note): representation B is a candidate, campaign-scoped, and
yours to adopt or refuse after the campaign; nothing in proteus/ changed.
