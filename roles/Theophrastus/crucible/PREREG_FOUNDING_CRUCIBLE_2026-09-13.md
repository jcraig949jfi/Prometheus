# Theophrastus founding crucible -- PREREGISTRATION

Currency: 2026-09-13. Committed BEFORE any cell is executed (the commit
that carries this file precedes every row in ledgers/). Nothing below is
moved after a number is seen; a change is an annotation beside the original.

## 1. Why this ecology

The charter asks for a tiny founding ecology built from inputs that already
carry strong evidence. The substrate reconnaissance (roles/Theophrastus/recon/)
found exactly one kind on the live SFE+PEW bench whose five ecological axes
are ALL natively expressible in the sealed spec and whose mechanisms carry
provenance and published behaviour at more than one world size:
`ca_density_v0` (Vivarium contract, Herakles semantics, herakles/evca).

Evidence already in the tree:
- Six recovered EvCA genomes, provenance class RECOVERED_SPECIMEN, with
  published performance at N = 149 / 599 / 999 (herakles/evca/genomes.py).
- Herakles WP-C1-e reproduced 17 of 18 (rule x N) cells OFFLINE, not through
  SFE/PEW (herakles/evca/c1e/REPORT.md, 906.5 s, protocol 0e6b9e812).
- The bench itself has 150 completed `ca_density_v0` rows, ALL at
  n_cells=149, steps=320, ic_density_set=[null] (queue census 2026-09-13,
  recon/queue_census.json). The WORLD axis has never moved on the bench;
  the PRESSURE axis (IC ensemble) has never moved on the bench.

So the known structure (published + C1-e) serves as the POSITIVE CONTROL for
the loop, the bench rows serve as an independent cross-consumer anchor at
W149, and the cells at W599 and under the uniform-density pressure are new to
the SFE+PEW record while being cheap (0.1-2 s per 100 ICs in-process).

## 2. The ecology (exact coordinates)

MECHANISMS (4), each = (name, rule_hex, provenance pointer):
    maj   000101170117177f0117177f177f7fff  herakles/evca/genomes.py GENOMES["maj"]
    GKL   005f005f005f005f005fff5f005fff5f  herakles/evca/genomes.py GENOMES["GKL"]
    exp   0505408305c90101200b0efb94c7cff7  herakles/evca/genomes.py GENOMES["exp"]
    par   0504058705000f77037755837bffb77f  herakles/evca/genomes.py GENOMES["par"]
  `maj` is included as a DELIBERATE NULL REGION: MAJ_STRUCTURAL_ZERO.md and
  C1-e show accuracy is exactly 0 under the unbiased ensemble at every N.

BRANCHES (2, related; evidence = the `kind` field and `source` field of the
same genome record, i.e. the published characterisation, not an inference
of this seat):
    hand_designed        {maj, GKL}   (GENOMES[*].kind = "hand-designed ...")
    ga_evolved_1993_95   {exp, par}   (GENOMES[*].kind = "GA-evolved ...")
  Sub-branch labels carried but NOT used in any predicate:
    exp = block-expanding strategy; par = particle-based strategy.
  No other branch relation is asserted. Ancestor/descendant relations between
  the four rules are UNKNOWN and recorded as UNKNOWN.

WORLDS (2 primary + 2 neighbours), world = (n_cells, steps, radius=3):
    W149   (149, 320)    the bench's established world (150 bench rows)
    W599   (599, 1198)   C1-e's 2N horizon convention at N=599
  Neighbours for the RESOURCE stencil (same lattice, different horizon):
    W149h  (149, 298)    C1-e's 2N convention at 149
    W599h  (599, 1286)   the bench's 320/149 ratio at 599
  A world is identified by the hash of its coordinate tuple; a label is
  never trusted (self-control C3).

PRESSURES (2), pressure = (ic_density_set, n_ic, success_criterion):
    P_iid   ([null], 100, "stable")   unbiased iid ensemble (published convention)
    P_unif  ([0.1,0.2,0.3,0.4,0.45,0.55,0.6,0.7,0.8,0.9], 10, "stable")
            a declared discrete uniform-over-density regime (n_ic_total 100).
            This is THIS SEAT'S declared regime; it is not the C1-e arm's
            exact set (that set is not in the tree) and is not compared to it.
  Neighbour for the exact-null stencil: P_iid_T = ([null], 100, "at_T").

INTERVENTIONS (2):
    NONE      transform = "none"
    REFLECT   transform = "reflect"   (REPRESENTATION_CHANGE; the spatial
              mirror of the rule table, Vivarium's _reflect_table; expected
              invariance of accuracy up to IC sampling)

CELL = (mechanism, pressure, world, branch, intervention). The sealed spec is
spec_version 3, repeat {count 8, sequential, sha256_index, reset,
budget {max_seconds 600, max_observations 8}}, seed_root 20260913 for the
primary pass and 20260914 for the replication pass. outcome_rule:
criteria_agree == true -> SURVIVED / FALSIFIED / INCONCLUSIVE (a per-cell
integrity prediction C1-e already established for all six rules; a
FALSIFIED here means the substrate differs from C1-e, not a result about
the mechanism). pew.encounter_id = "ENC-theophrastus-<cell_id[:16]>",
players = ["evca:<name>"], namespace "theophrastus" (NOT prod).

## 3. Cells planned (coverage pass), eligibility and budget

Coverage pass (intervention NONE): 4 mechanisms x 2 worlds x 2 pressures = 16.
Intervention stencil: REFLECT on {GKL, exp, par, maj} x W149 x P_iid = 4.
Resource stencil: {GKL, exp} x {W149h, W599h} x P_iid x NONE = 4.
Exact-null stencil: GKL x W149 x P_iid_T x NONE = 1.
Replication pass (seed_root 20260914): every cell that enters a candidate
contrast (section 5), plus the two anchor cells GKL/W149/P_iid and
exp/W149/P_iid whatever happens.
Replay: two cells re-executed with the IDENTICAL sealed spec (same
spec_hash) in a fresh SFE world; result digests must match.
Budget: 45 executions and 3600 s wall for the whole founding round,
enforced by the explorer (self-control C10). Per-cell cost estimate: 8
observations x (0.2-2 s) plus engine round trips.

## 4. Measurement and its error, computed BEFORE the gates

Per cell: 8 observations x 100 ICs = 800 ICs; p = mean accuracy;
SE_cell = sqrt(p(1-p)/800) <= 0.0177 (worst case p = 0.5).
CONTRAST(A,B) = p_A - p_B; SE_D = sqrt(SE_A^2 + SE_B^2) <= 0.0250.
Attainable range of a contrast: [-1, 1]. The candidate bar is
|D| >= 4 SE_D (<= 0.100 at worst case), which sits inside the attainable
range and below the published magnitude of the one contrast the record
predicts to be large (exp: W149 0.652 vs W599 0.515, D = 0.137 = 5.5 SE_D
at worst case). Published contrasts predicted to sit BELOW the bar (and so
expected NO_SIGNAL or WEAK_SIGNAL): GKL across worlds (0.050 = 2.0 SE_D),
par across worlds (0.044). These are stated so that "nothing fired" can be
read against "what could have fired".

## 5. Dispositions (closed set) and the decision rule

For every contrast the explorer evaluates:
  INSTRUMENT_BLOCKED  either cell FAILED / not executed / outcome INCONCLUSIVE
  NO_SIGNAL           |D| < 2 SE_D in the primary pass
  WEAK_SIGNAL         2 SE_D <= |D| < 4 SE_D in the primary pass, OR
                      |D| >= 4 SE_D in the primary pass but the replication
                      pass has |D'| < 4 SE_D' or a different sign
  REPRODUCIBLE_SIGNAL |D| >= 4 SE_D in the primary pass AND |D'| >= 4 SE_D'
                      in the replication pass with the same sign AND the
                      stencil cells the contrast depends on were executed
  REPRESENTATION_BLOCKED  the contrast needs a coordinate the cell
                      representation cannot carry (recorded, not scored)
INDETERMINATE branch: a contrast with fewer than 8 observations on either
side is INSTRUMENT_BLOCKED, never scored on a partial sample.
Eligible count = contrasts with both cells COMPLETED; reported beside every
firing count.

Contrasts pre-declared (the explorer evaluates exactly these families):
  C-WORLD   same mechanism, same pressure, NONE: W149 vs W599           (8)
  C-PRESS   same mechanism, same world, NONE: P_iid vs P_unif           (8)
  C-BRANCH  same world, same pressure, NONE: GKL vs exp, GKL vs par,
            maj vs exp, maj vs par (hand vs GA)                         (16)
  C-INTERV  same mechanism, W149, P_iid: NONE vs REFLECT                (4)
  C-RES     same mechanism, P_iid, NONE: W149 vs W149h, W599 vs W599h   (4)
  C-NULL    GKL, W149, NONE: P_iid vs P_iid_T                           (1)
  Signal type is assigned by WHICH family fired, never by magnitude:
  C-WORLD -> ENVIRONMENTAL_OBSOLESCENCE (if accuracy falls toward 0.5) or
  ROBUSTNESS_ISLAND (recorded only as a NON-firing beside a firing
  neighbour); C-PRESS -> PRESSURE_SENSITIVITY; C-BRANCH firing in one world
  and reversing sign in the other -> BRANCH_REVERSAL; C-INTERV ->
  REPRESENTATION_FAILURE candidate (a symmetry that is not a symmetry);
  C-RES -> PRESSURE_SENSITIVITY on the resource axis; C-NULL is expected
  to be an EXACT zero (criteria_agree) and any non-zero is an
  INSTRUMENT finding.

## 6. Self-controls and cheats (each must be DETECTED; a cheat that passes
undetected fails the founding round)

  C1  duplicated cell             the same cell proposed twice
  C2  coordinate aliasing         two labels, one spec_hash
  C3  changed world as identical  label W149 with steps 298
  C4  branch without evidence     branch asserted with evidence None
  C5  no-op intervention          intervention whose spec equals NONE's
  C6  nondeterministic replay     a row claiming BIT_DETERMINISTIC whose
                                  digest differs at the same spec_hash
  C7  missing provenance          mechanism with no provenance pointer
  C8  stale result reuse          cached row from a different engine
                                  source hash offered as current
  C9  LLM rationale in selection  proposal text must not change ordering
  C10 budget overrun              the (budget+1)th execution refused
  CHEAT-SIGNAL  a fabricated row with |D| = 0.5 and no stencil, no
                replication, offered to the signal emitter: must NOT be
                promoted.
The controls run BEFORE any live execution (theophrastus/tests) and the
cheat rows are kept in ledgers/cheats.jsonl, never mixed with real rows.

## 7. What this round does NOT license

No statement about the mechanisms beyond the dispositions above. No claim
that a signal is a discovery. No comparison of exploration policies
(charter XVIII comes later). No writes to the PEW `prod` namespace and no
rows in Vivarium's queue unless section 8 is exercised.

## 8. Optional cross-consumer probe (decided after the loop, recorded here
so it is not invented later)

One cell (GKL, W149, P_iid, NONE, seed_root 20260913) MAY additionally be
submitted to viv.research_experiment_queue with created_by="theophrastus"
so that when Vivarium's consumer next runs, the SAME sealed spec is executed
by a DIFFERENT consumer on the SAME engine. The prediction is a matching
result digest. It is not counted in this round's budget and is reported as
PENDING until Vivarium runs it.

## ANNOTATIONS AFTER EXECUTION (2026-09-13; the text above is unchanged)

A1. Section 2, INTERVENTIONS, "expected invariance of accuracy up to IC
    sampling": UNDER-DESCRIBED. The ca_density_v0 wrapper applies the
    transform to the initial conditions as well as to the rule table
    (vivarium/viv/ca_density.py apply_transform; herakles/evca/
    c3_null_check.py), so REFLECT is an exact symmetry and the predicted
    contrast is EXACTLY zero per IC (mask digests equal). Observed 4/4
    exact. The C-INTERV family is therefore an exact-null family like
    C-NULL; its signal type REPRESENTATION_FAILURE would fire only on an
    implementation defect. No gate was moved; no disposition changed.
A2. Section 5: the prior-evidence classification of admitted signals
    (crucible/SIGNALS_ANNOTATED_2026-09-13.json) was added AFTER the
    dispositions and does not alter them. It is the input to backlog
    THEO-01 (a prior-evidence gate at admission in the next prereg).
A3. Section 3: `contrasts` was scored once standalone and once inside
    `replicate`, so contrasts.jsonl holds two identical primary rows per
    contrast (82 rows for 41). Append-only; recorded, not deleted.
A4. Section 8 (cross-consumer probe): NOT exercised; Vivarium's daemon was
    down all pass and starting it is not this seat's act.
