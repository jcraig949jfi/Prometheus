# Theophrastus founding round -- report (2026-09-13)

Currency: 2026-09-13. Built from base 02ffd7603 (origin/main) in worktree
theophrastus-founding, branch theophrastus/founding-2026-09-13. Rows:
roles/Theophrastus/ledgers/ (rows.jsonl 46, cells.jsonl 125,
contrasts.jsonl 123, signals.jsonl 46 = 23 signals + 23 annotations,
dead.jsonl 5). Preregistration: crucible/PREREG_FOUNDING_CRUCIBLE_2026-09-13.md
committed at 05ee51977 BEFORE the first execution.

## 1. Operational reading of the charter

roles/Theophrastus/RESPONSIBILITIES.md. In one line: CONTRAST(A,B) over
replayable, content-identified cells, on the bench's own engine and
executor, with dispositions from a closed set, nulls kept, no LLM in
selection, no discovery vocabulary.

## 2. Capability matrix

recon/CAPABILITY_MATRIX_2026-09-13.md. Summary: 8 NATIVE, 4 REP, 2 AWK,
2 MISSING (mechanism composition for CA kinds; cross-producer coordinate
query in PEW), 0 UNKNOWN left unresolved.

## 3. Producer / consumer flow as implemented

recon/CAPABILITY_MATRIX s2. Archaeon -> Postgres queue -> Vivarium daemon
-> SFE -> PEW(prod) -> Archaeon. The daemon was not alive on 2026-09-13;
this seat ran as an alternative consumer on the same engine via
Vivarium's runner as a library, own client, PEW namespace `theophrastus`.

## 4. Exact gaps

recon/CAPABILITY_MATRIX s4 (G1-G5).

## 5. Change requirements issued

reqs/THEO-REQ-001 (Mnemosyne: `ecology` selector on fossil encounters),
THEO-REQ-002 (Vivarium: per-parameter axis annotation on kind contracts),
THEO-REQ-003 (Proteus, cc Herakles/Nyx: a provenance-carrying composition
operation for same-kind CA mechanisms). Posted via comms as delegations.

## 6. The founding ecology and why

PREREG s1-s2: ca_density_v0 is the ONLY live kind on which all five axes
are natively expressible in the sealed spec AND whose mechanisms carry
provenance (RECOVERED_SPECIMEN) and published behaviour at more than one
world size. Herakles's C1-e gives positive-control values; the bench's 150
rows sit at one world only. 4 mechanisms (maj, GKL, exp, par), 2 branches
with published-characterisation evidence, 2 worlds + 2 horizon
neighbours, 2 pressures + 1 exact-null neighbour, 2 interventions.

## 7. Cell representation

theophrastus/cell.py. cell_id = sha256 over CONTENT (rule hex; lattice
tuple; density set + n_ic + criterion; transform; branch members' hexes +
relation; seed_root; repeat block). Labels ride beside, never inside.
spec_hash = Vivarium's own spec_hash of the derived sealed v3 spec;
execution_hash = the executor-visible subset (alias/no-op surface).
UNKNOWN is written for ancestry.

## 8. Self-controls and cheats

theophrastus/tests/test_controls.py, 19 tests, all passing, run BEFORE any
live cell. Every preregistered cheat was caught:
    C1 duplicate cell           unit + LIVE (25/25 refused on re-proposal)
    C2 coordinate alias         unit (two labels, one execution_hash)
    C3 changed world as same    unit (label W149 with steps 298 -> refused)
    C4 branch without evidence  unit
    C5 no-op intervention       unit (label claims, execution equal)
    C6 nondeterministic replay  unit (mismatch flagged; honest label not)
    C7 missing provenance       unit
    C8 stale result reuse       unit (build / instance / spec mismatch)
    C9 LLM rationale in select  unit (loud rationales cannot reorder)
    C10 budget overrun          unit + LIVE (2/2 blocked at 45/45)
    CHEAT-SIGNAL                unit (|D|=0.5 with no rows/stencil/
                                replication refused; WEAK refused)
Two controls corrected the explorer during the round (annotation, not
rewrite): alias/no-op detection first keyed on spec_hash and missed
because the sealed spec legitimately carries the pew identity block;
re-keyed on execution_hash. The C10 wall clock was saved at charge time
and under-counted each phase's last execution; fixed (crucible.py) --
executions were counted correctly throughout.

## 9. First completed loop

SOURCE (genomes.py) -> REPRESENT (cell.py/ecology.py) -> PROPOSE (25
cells, check_batch clean) -> EXECUTE (adapter -> SfeRunner -> engine
eng_8a37a5d3, 25/25 COMPLETED, 25/25 fossilized) -> MEASURE (contrast.py)
-> PROBE NEIGHBOURS (3 stencil families in the same batch; 16-cell
replication pass) -> RECORD (ledgers) -> QUEUE OR KILL (23 admitted, 5 dead)
-> REPLAY (2 cells x 3 executions, REPLAY_OK).

## 10. All cells visited

46 executions = 1 smoke (seed 1, repeat 2, never scored) + 25 coverage
(seed 20260913) + 16 replication (seed 20260914) + 4 replay (2 cells x 2,
seed 20260913). 42 distinct spec hashes; 46 SFE worlds; 362 observations.
Per-cell table (coverage pass, p over 800 ICs; SE <= 0.0177):

    mech  world  press   interv   p       mech  world  press   interv   p
    GKL   W149   P_iid   NONE     0.8125  exp   W149   P_iid   NONE     0.6713
    GKL   W149   P_iid   REFLECT  0.8125  exp   W149   P_iid   REFLECT  0.6713
    GKL   W149   P_iid_T NONE     0.8125  exp   W149   P_unif  NONE     0.9038
    GKL   W149   P_unif  NONE     0.9750  exp   W149h  P_iid   NONE     0.6713
    GKL   W149h  P_iid   NONE     0.8125  exp   W599   P_iid   NONE     0.5500
    GKL   W599   P_iid   NONE     0.7550  exp   W599   P_unif  NONE     0.8275
    GKL   W599   P_unif  NONE     0.9938  exp   W599h  P_iid   NONE     0.5500
    GKL   W599h  P_iid   NONE     0.7550
    par   W149   P_iid   NONE     0.7500  maj   W149   P_iid   NONE     0.0000
    par   W149   P_iid   REFLECT  0.7500  maj   W149   P_iid   REFLECT  0.0000
    par   W149   P_unif  NONE     0.9650  maj   W149   P_unif  NONE     0.3200
    par   W599   P_iid   NONE     0.7238  maj   W599   P_iid   NONE     0.0000
    par   W599   P_unif  NONE     0.9850  maj   W599   P_unif  NONE     0.2150

Outcome rule (criteria_agree == true, aggregate all): SURVIVED on 46/46.
Positive-control check against the published/C1-e values at P_iid: GKL
0.8125/0.7550 vs published 0.816/0.766; exp 0.6713/0.5500 vs 0.652/0.515;
par 0.7500/0.7238 vs 0.769/0.725; maj 0/0 vs 0/0. All within 2 SE of the
published figure except exp at W599 (+0.035, 2.0 SE) -- consistent with
C1-e's own +0.008 and not read further.

## 11. Local stencils

Around every coverage cell the batch itself supplied neighbours on each
axis: pressure (P_iid vs P_unif), world (W149 vs W599), branch (four
hand-vs-GA pairs), intervention (REFLECT), resource (W149h/W599h) and
criterion (P_iid_T). contrasts.jsonl carries `stencil_cells` per contrast
(executed cells sharing >= 3 of 4 label coordinates).

## 12. Signals emitted (dispositions only; nothing here is a discovery)

23 contrasts REPRODUCIBLE_SIGNAL under the preregistered rule (>= 4 SE
in both passes, same sign): 3 C-WORLD, 8 C-PRESS, 12 C-BRANCH. Emitted as
THEO-SIGNAL-0001..0023 (ledgers/signals.jsonl) and annotated POST HOC by
prior-evidence class (crucible/SIGNALS_ANNOTATED_2026-09-13.json):
    PUBLISHED+C1E     7   predicted by published_P and C1-e s1
    C1E_AT_149_ONLY   7   predicted by C1-e s3 Suspect-3 (149 only)
    NEW_TO_RECORD     9   no measurement in the tree under a uniform-over-
                          density ensemble at N=599 (dated 2026-09-13)
The 14 predicted signals are the loop's POSITIVE CONTROL: the instrument
detects known structure with the right sign and magnitude. The 9
NEW_TO_RECORD rows are what a consumer could look at; the cheapest reading
of all nine is "the uniform-density regime lifts every rule, and the lift
is itself world-sensitive", which is a PRESSURE x WORLD interaction the
prereg did not declare as a family and this seat therefore does NOT score.
4 WEAK_SIGNAL: GKL across worlds (2.8 SE, P_iid), GKL/par across worlds
under P_unif (~3 SE, negative), GKL vs par at W149 (3.0 SE). 14
NO_SIGNAL, of which 9 are EXACT zeros (see 13).

Attainable-range / eligibility: 41/41 contrasts eligible on both passes;
the 4-SE bar (<= 0.100) lay inside [-1, 1] and below the one predicted
large contrast (exp across worlds, predicted 0.137, measured 0.121/0.146).

## 13. Null / dead terrain recorded

    C-INTERV  4/4 EXACT identity (mask digests equal). The wrapper
              transforms the ICs as well as the table: REFLECT is a
              semantics-preserving symmetry, so identity is the designed
              null (herakles/evca/c3_null_check.py; Archaeon C3 72/72
              IDENTICAL). PREREG s2 wording "up to IC sampling" under-
              described it; annotated, not rewritten.
    C-RES     4/4 EXACT identity across different steps (320 vs 298;
              1198 vs 1286): converged dynamics, distinct execution hashes.
              The horizon convention is immaterial here (matches C1-e s3
              Suspect 1).
    C-NULL    1/1 EXACT identity (criteria agree; C1-e Suspect 2).
    dead.jsonl 5 cells: maj under P_iid at W149 (NONE, REFLECT), W599, and
              the two replication rows -- accuracy exactly 0 over 800 ICs
              (MAJ_STRUCTURAL_ZERO.md). Coverage mode skips them; the
              counterfactual mode can revisit them (controls.select).

## 14. Representation / instrument blocks

REPRESENTATION_BLOCKED (not scored): the M1+M2 stencil (no composition,
REQ-003); the PRESSURE x WORLD interaction (a family the prereg did not
declare; next round). INSTRUMENT_BLOCKED: none -- 41/41 eligible.
Instrument findings: none; science profile findings on every completed
work item: [].

## 15. Replay

GKL/W149/P_iid/NONE and exp/W599/P_iid/NONE, identical sealed spec, fresh
SFE world each time, 3 executions each: result digests identical
(bb88142db2cf..., 04689f27607d...), reproducibility BIT_DETERMINISTIC on
every row. REPLAY_OK.

## 16. Compute / resource accounting

45 budgeted executions of 45 (+1 unbudgeted smoke); adapter wall 287.0 s
(coverage 142.9 s / 25, replication 114.4 s / 16, replay 29.8 s / 4);
executor-reported elapsed 282.0 s; 46 SFE worlds, 46 experiments, 362
observations, 46 PEW encounters (namespace theophrastus); one engine
instance and one build throughout (eng_8a37a5d3..., sha256:5380cb90...).
Per cell: W149 ~1.3 s, W599 ~12 s executor time; ~4-6 s engine round
trips per cell on top.

## 17. What must change before a sustained crawler is scientifically honest

    a. PRIOR-EVIDENCE GATE. The admission gate has no notion of what the
       record already predicts, so a round with positive controls emits
       controls as signals (14 of 23). A sustained crawler must classify
       every candidate contrast against PEW/published evidence BEFORE
       admission and route predicted contrasts to a CALIBRATION ledger,
       not the signal queue. This is the largest change and it depends on
       REQ-001 (coordinate queries) to be done without reading other
       seats' code.
    b. INTERACTION FAMILIES. Declare difference-of-differences families
       (pressure x world, branch x world = BRANCH_REVERSAL) in the prereg
       with their own SE (sqrt of four variances); this round could not
       score them without moving the gate after seeing data.
    c. SFE FAMILIES. Register each contrast as an SFE comparison family
       with sealed arms so the substrate, not this seat's ledger, is the
       authority on "which two cells were compared".
    d. PLAYER IDS. Agree a content-based player id for recovered specimens
       (evca:<rule_hex> or a Herakles-minted specimen id) so PEW player
       queries work across producers; "evca:GKL" is a label.
    e. SAMPLE SIZE PER CELL is a policy knob (n=800 here); make it part of
       the cell (it already is via repeat/n_ic) and never change it
       mid-neighbourhood.
    f. COVERAGE / EXPANSION / COUNTERFACTUAL modes exist in controls.select
       but were exercised only as coverage + expansion (replication). The
       counterfactual mode (revisit dead terrain deliberately) needs its
       own budget line and productivity signal (base rule 8).
    g. RULE 10 PARK. The crawler as a loop needs a declared non-productive
       bound and an accountable seat before it may run unattended
       (MONITORS.md row); it has none yet and is therefore run by hand.
    h. The optional cross-consumer probe (PREREG s8) was NOT exercised:
       Vivarium's daemon is down and Archaeon's charter forbids starting
       it; the queue row is not submitted this round. It remains the right
       way to test "same engine, different consumer".
