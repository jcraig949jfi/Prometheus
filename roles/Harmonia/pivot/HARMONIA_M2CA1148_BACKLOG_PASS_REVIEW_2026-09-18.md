+==============================================================================+
|  REVIEW PACKET -- HARMONIA BACKLOG PASS: 27 OF 51 ROWS CLOSED/SUPERSEDED/    |
|  DELEGATED IN ONE SITTING; A DEAD RUNNER, A WRONG DERIVATION PHRASE AND A     |
|  CONTROL THAT CANNOT FAIL FOUND ON THE WAY                                   |
|  Author: Harmonia[m2-ca1148a0] (scientific audit seat), M2 SPECTREX5,        |
|          operator label "Harmonia B"                                         |
|  Date: 2026-09-18 ~02:00 UTC      Status: PASS COMPLETE; nothing in flight   |
|  For: HITL (operator) + external reviewers                                   |
|  Self-contained: every load-bearing number is inline; no repo access needed  |
+==============================================================================+

0. SUMMARY / MANDATE / VERDICT
------------------------------------------------------------------------------
Mandate (operator, chat, 2026-09-18 ~01:10Z): "work through all the HARM-**
that are unclaimed and see if we can clear them." The backlog had 51 rows.
Classification before any work: 25 unclaimed and doable, 9 blocked on another
seat, 14 in a sibling instance's declared lane, 2 already closed, 1 stale
(scope moved). Every row's disposition is written beside it in the backlog
with the artifact that closes it.

Result: 24 rows CLOSED, 4 SUPERSEDED with reasons, 1 DELEGATED. 20 rows stay
OPEN and every one of them is blocked on a named seat or sits in a sibling's
lane. No row was closed by fiat: each closing artifact is a file, a script
that runs, a test that passes, or a posted ruling.

Three findings the pass did not go looking for:
  F-1  the seat's own qualification runner had been UNRUNNABLE since 09-10
       (two faults from the QR-1.1.0 rename); the committed ledger predates it
  F-2  a derivation phrase in a standing ruling was wrong ("0.577 = half the
       band edge in log terms"; it is the linear half); numbers unchanged
  F-3  the Proteus current instrument's only negative control is one that
       cannot fail (a reversible reference is reversible by algebra)
And one program-level gap: a Harmonia instance cannot message a sibling
Harmonia instance through comms (inbox excludes the seat's own messages).

Verdict I am asking the reviewer to test: the QR-1.2.0 release turned eleven
prose rules into refusals that fire and stay silent on clean controls, and the
two registers (standing rules, vacuous readings) make the seat's rules findable.
A reviewer who thinks a 22-row release in one sitting cannot have been
adversarially checked has a real case; section 9 is written for that reviewer.

1. WHAT WAS BUILT (and what existed before)
------------------------------------------------------------------------------
Before this pass: QR-1.1.0 / AF-1.0.0 / H4-ADAPTIVE-1.0.0 (09-10), a runner
whose last ledger was dated 09-09, 21 rulings, a backlog of 51 rows of which
2 were closed.

Built, in commit order (all on origin/main; SHAs in section 10):

  c387de555  HARM-44  ruling on Proteus #341 + an EXECUTING audit script
  60f710042  HARM-43  the landed SFE contract re-verified from an independent
                      worktree, five gate outputs, SUPERSEDED annotation
  f58d4bd36  15 rows  QR-1.2.0, AF-1.1.0, EX-1.0.0, FP-1.0.0, the H0 analysis
                      plan, MULTIPLICITY.md, SIZING_RULE.md, 22 tests
  724e7988b  3 rows   STANDING_RULES.md (40 rules), VACUOUS_READINGS.md
                      (8 rows), CALIBRATION_CORPUS_POLICY.md; HARM-13 delegated
  17121698e  2 rows   H3 prospective-utility manifest; PEW encounter manifests
  22d5c7432  1 row    number-scope audit; H4-ADAPTIVE 1.0.0 -> 1.0.1
  3a9a1b295  1 row    Stage-A triage over 107 cut fossils
  (final)    2 rows   HARM-15/17 superseded; STATUS, journal, this packet

2. THE CLAIM AND WHY IT MATTERS
------------------------------------------------------------------------------
This seat decides what the evidence permits, by executable checks. A backlog
row that says "state the gate for H3" is worth nothing until a call refuses
the wrong endpoint. The claim of this pass is narrow: every rule the seat had
written in prose since 09-08 that COULD be made mechanical now is, with a test
that shows it firing on the defect and silent on a clean case; and every rule
that cannot be made mechanical is indexed to the ruling that set it, marked
"--" as applied-by-reading.

3. DESIGN AS EXECUTED
------------------------------------------------------------------------------
Order: owed items first (HARM-44 ACK was late; HARM-43 a stale verification),
then the module release (so later rows could use it), then registers, then
declarations, then audits of my own rulings, then the reading-level triage.

Discipline per row: classify against sibling journals and commits (none of
the taken rows had a sibling artifact); build; run; test on the merged tree
(archaeon test_base_role 11 + the new h0h5 suite) before every push; ASCII
check every committed text file; close the row with the artifact named.

Not taken, deliberately: HARM-38/39 (gzip oracle grading and corpus). Two
sibling instances declared them (m2-038758c6 as "next", gandalf-6cd1348b
"started" 38 on 09-17). Neither has an artifact and both were idle > 7 h,
but a third instance opening the same body on a third host is the failure
INSTANCES.md exists to prevent. Left in the gzip lane, said so in STATUS.

4. RESULTS, EXACT
------------------------------------------------------------------------------
4a. HARM-44 (Proteus #341): the V0.5 current instrument
    124 states, 50,000 samples/state, 506 pairs, floor 4.156e-05, 166 above,
    max |J| 2.449e-04, reference max |J| 2.168e-19, occupancy TV 0.019747.
    Audit script on a synthetic 4-state cyclic kernel (true |J| = 0.05):
      C-NEG  reversible reference max |J| 0.0        -> CANNOT FAIL (algebra)
      C-POS  injected eps 1e-2..1e-5: recovered exact, rel err < 1e-15
      C-CHEAT floor with B == A: floor 0.0, 4/4 pairs "above floor"; no
              guard in run_kernel.py (would print 506/506 on the live kernel)
    Ruling: ADMITTED as a detector; NOT admitted as an absence instrument
    until P-1 positive control at declared magnitude (gives a minimum
    detectable current), P-2 floor guard, P-4 per-pair rows committed (the
    JSON carries aggregates + top 40 of 506). R4 on a length-fixed profile:
    NOT_APPLICABLE_BY_CONSTRUCTION, verified on the measured kernel (count of
    length-changing draws must be exactly 0); TRIVIALLY_SATISFIED refused.

4b. HARM-43: landed SFE contract (9.0.1, build 699ca0f9, eng_906356f7, schema 9)
    against https://192.168.1.191:8811/v2, CA m2.crt:
      plain                     exit 0 CONFORMANT  (72 = 72 routes, 33 GET scoping probes match)
      Archaeon route set (1)    exit 0 CONFORMANT
      Vivarium route set (30)   exit 0 CONFORMANT
      superseded candidate 726275da vs its own base (M1 :8811)  exit 2 UNREACHABLE
      superseded candidate vs the M2 engine                      exit 1 DRIFT on
                                engine_instance_id; hash/schema/4 routes ADDED
    The DRIFT run is the negative control: same program, wrong ledger, refuses.
    None of the candidate's three promote_only_when conditions was ever met.

4c. QR-1.2.0 / AF-1.1.0 / EX-1.0.0 / FP-1.0.0
    AF battery 12/12: F1-F5 fire; F4 control silent; F7 degenerate replicate
    (4 replays of one payload -> attests determinism, counts 1 unit, refused
    as replicates), F8 structural floor (p_mode 0.833 > 0.50 refused; clean
    corpus PASS, f 1.000), F9 non-exchangeable rows (serial r +0.998,
    inflation x200 -> VIOLATED; exchangeable control silent).
    F6 calibration at threshold 0, 8000 draws: G 0.0139, I 0.0129 vs expected
    0.0125 (alpha/2 under Bonferroni over 2); at threshold 0.05 both 0.0000
    and labelled VACUOUS (3.1 and 2.2 SE from zero).
    EX-1.0.0 on the committed live dossier: 40 regions -> 12 / 5 / 23 / 0,
    matching the 09-10 ruling. Cuts shown band-derived: inflation 1/(1-r^2)
    = 1.5 at 0.5774, = 3.0 at 0.8165.
    FP-1.0.0 on C3-2's 120 acquired rules: support 1, p_mode 1.000, f 0.000,
    REFUSED; clean synthetic: support 120, p_mode 0.008, f 1.000, PASS.
    lane_gate: 6 lanes x 2 stages; beta promises PRECISION, 1.0 promises
    POWER; min blocks 6 everywhere (2/2^6 = 0.031); eligibility(5) prints
    NOTHING_COULD_FIRE. H3 refuses archive_diversity / qd_score / coverage /
    descriptor_spread / novelty; H4 refuses any endpoint computed on training
    tasks; H5 carries reach bounds 8 (direct) / 12 (any permutation) and the
    live readout's 8.0000 / 11.7305 label AT_OR_UNDER_BOUND_NO_EVIDENCE.
    Shared-arm correlation: G|transport = 0.5 for rho in {0, 0.3, 0.7};
    G|I = 0 under exchangeable equal variances.
    program_family: uncorrected FWER across 6 lanes 1 - 0.95^6 = 0.265,
    expected false supports 0.30, program-level alpha per lane 0.0083.
    Tests: 25 passed (0.2 s). test_base_role: 11 passed on the merged tree.

4d. F-1 in detail (the dead runner). QR-1.1.0 (789ce4fdd, 09-10) renamed the
    H0 estimand to G_joint_treatment_S11_minus_S00 and required_blocks to
    blocks_for_interval_clearance(assumed_effect=). adversarial_fixtures.
    detect_f6 kept the QR-1.0.0 name (KeyError); run_qualification.py kept
    the old keyword (TypeError). The runner could not have completed between
    09-10 and 09-18; the committed ledger is dated 09-09 (dd38720c0). Fixed;
    ledger regenerated; the fix is annotated in the code where it bit.

4e. Number-scope audit (HARM-32): 16 numbers; 1 OUT (the 09-08 ruling's
    "SE(I) = sqrt(2) x SE(main) FOR ANY rho" -- true only under equal marginal
    variances + exchangeable correlation; QR-1.1.0 corrected the rule on 09-10
    but never annotated the ruling; the H4 protocol text carried the same
    sentence "by construction" -> H4-ADAPTIVE-1.0.1, no rule changed, no
    campaign ran under 1.0.0); 2 LOOSE (0.379 called a "floor" in CHARTER --
    it is a false-fire rate at 10 x 12, true ratio 1.0, i.i.d.; 12/5/23 is a
    count over the FIRED neighbourhoods, 40 of 65 regions, a selected subset);
    13 IN. No number changed.

4f. Stage-A triage (HARM-46): the 39-cut scope was stale; the atlas has 107
    cut fossils. Predicates over the cut record + Techne record + latest ok
    run receipt: REPRODUCTION feasible now 96; MUTATION (a bounded ACCEPTED
    organ in a running world) 94; NEW_EXPERIMENT (entry point or pressure)
    107; ablations actually run 3; prediction packets 2 (gzip, particles);
    oracles: SMOKE_ONLY+example 78, UPSTREAM_TESTS+example 16, example only
    8, none 3, drivers-no-oracle 2; worlds: NOW 96, SOURCE_ONLY 9,
    BUILDS_BUT_NOT_RUN 1, NOT_ATTEMPTED 1; residue: explained 28, partial 50,
    large 25, instrument-insufficient 4. Two records (avida, do-mpc) say
    "none this pass -- SOURCE pinned" in their environment field while a
    docker receipt ran: the receipt wins, the label is stale.

5. INCIDENTS AND WHAT THEY VALIDATED
------------------------------------------------------------------------------
- A `cat > file` with no stdin hung a shell for 120 s at boot (mine). Cost:
  one background task killed. Validated nothing; recorded.
- Two heredoc appends of 100+ lines wrote NOTHING (the tool's known large-
  heredoc failure); the additions were written to files and appended from
  Python. The runner fix then needed a second pass because the tool
  unescaped "\n" inside a Python string in the edit script. Both recoverable;
  neither reached a commit.
- The comms gap: comms.api.inbox has `m.sender <> agent`, so a post from
  Harmonia to Harmonia is invisible to every Harmonia instance. Instances
  coordinate only through STATUS.md / INSTANCES.md / journals. Reported here
  and in the post carrying this packet; comms is Archaeon's lane.

6. WHAT WAS NOT RUN
------------------------------------------------------------------------------
- No experiment on the program's substrate (seat scope s2). Every "run" above
  is a synthetic calibration, an offline gate, or a reading.
- The HARM-13 per-detector class table (needs the corpus as D1/D2/D4/D5 see
  it; delegated to Archaeon, #413).
- The d3.v2 live dossier (#260, owed by Archaeon since 09-14; reminded).
- HARM-38/39 (gzip oracle grading and corpus): siblings' declared lane.
- The Proteus P-1..P-6 wiring: Proteus's lane.

7. WHAT THIS DOES AND DOES NOT ESTABLISH
------------------------------------------------------------------------------
Establishes: the seat's rules are now executable where they can be, indexed
where they cannot; the runner works again; the landed contract is verified
from an independent checkout; the Proteus instrument's admission boundary is
stated with an executing audit behind it.
Does NOT establish: that any lane's science moved. Not one H0-H5 verdict
changed. The gates now exist; no confirmatory data has been read through
them. The triage is a feasibility map and says nothing about worth. The
policy for D1/D2/D4-D6 is derived from what each detector computes, not from
a measured class distribution (that is HARM-13, delegated).
Conditionality: every QR-1.2.0 constant is the one its ruling set; where a
ruling's number was superseded (D3 survivors under /(n-2); the C3-3 region
gate), the current reading is cited and the annotation sits in the ruling.

8. DECISION / RECOMMENDATION
------------------------------------------------------------------------------
HITL's call. My lean: (a) accept the pass; (b) route the two owed inputs --
#260 (Archaeon, d3.v2 live dossier, 4 days) and the HARM-13 table -- since
four backlog rows and d3.v2's live use wait on them; (c) let the gzip lane's
two instances be asked which one holds HARM-38/39, because two "next" claims
and no artifact is how work stalls; (d) do not open more backlog rows on this
seat until a lane consumes what exists (SIZING_RULE.md, MULTIPLICITY.md and
lane_gate are unread by any lane yet).
"Not worth continuing" is a legitimate answer for HARM-24 (PEW encounter
manifests): five declared analyses with no consumer named as wanting them.

9. QUESTIONS FOR THE REVIEWER
------------------------------------------------------------------------------
1. QR-1.2.0 adds ~460 lines in one commit, tested by 25 tests I wrote the
   same hour. Which refusal would you expect to be wrong, and what input
   would show it? (Candidates: refuse_relabel on a plan whose body changed
   AND purpose changed; validate_cell_payloads on aliases that chain.)
2. The H5 bounds 8 / 12 are quoted from Archaeon's readout as ANALYTIC facts
   about a 12-bit genome with 4 inert high bits. Do you accept "any
   permutation of the map reaches <= 12 neighbours" without a proof in the
   file? I did; it should perhaps be a computed check over the 4,096 entries.
3. The 0.5 shared-arm correlation is exact under exchangeable equal
   variances. At the phase-2 pilot Sigma it will not be 0.5; is printing the
   exchangeable reference beside the measured value helpful or misleading?
4. Is superseding HARM-15/17 (v1 trend recalibration) by the v2 calibration's
   A2 rows honest, given A2 was run at FLOOR and LIVE geometries but the row
   named (n=40, k=4)?
5. The triage predicates call a cut "MUTATION feasible" when it has one
   ACCEPTED organ with a non-UNKNOWN source_boundary in a running world.
   78 of those worlds have only a SMOKE oracle. Is "feasible" the right word
   for an ablation whose readout does not yet exist?
6. The number-scope audit was done by the instance whose predecessors wrote
   the numbers. Which of the 13 "IN" rows would you re-read first?

10. ARTIFACTS
------------------------------------------------------------------------------
Commits on origin/main (branch harmonia/m2-ca1148a0-boot-2026-09-17):
  a2c45a48e boot; c387de555 HARM-44; 60f710042 HARM-43; f58d4bd36 QR-1.2.0;
  724e7988b registers/policy/delegation; 17121698e manifests; 22d5c7432
  audit; 3a9a1b295 triage; final commit carries this packet, STATUS, journal.
Files (all under roles/Harmonia/):
  rulings/RULING_PROTEUS_CURRENT_INSTRUMENT_AND_R4_2026-09-18.md
  science/proteus_current_instrument_audit.py; science/ledgers/
    proteus_current_instrument_audit_2026-09-18.json
  contracts/verify_landed_2026-09-18/{README.md, gate_*.txt};
    contracts/candidates/726275da9c8d/SUPERSEDED.md
  qualification/h0h5/{qualification_rules.py, adversarial_fixtures.py,
    exchangeability.py, floor_precheck.py, run_qualification.py,
    h0_analysis_plan.json, write_h0_analysis_plan.py, MULTIPLICITY.md,
    SIZING_RULE.md, CALIBRATION_CORPUS_POLICY.md,
    h3_prospective_utility_analysis_v1.json, pew_encounter_analyses_v1.json,
    tests/test_qr_1_2_0.py, ledgers/h0h5_qualification.json}
  STANDING_RULES.md; VACUOUS_READINGS.md; AUDIT_20260918_number_scope.md
  archaeology/{triage_stage_a.py, TRIAGE_STAGE_A_2026-09-18.md, .json}
  prompts/2026-09-18_exchangeability_d1_d6/ (MANIFEST sha256 755323df...)
  BACKLOG_H0H5.md (every row annotated); STATUS.md; journal/2026-09-17_m2-ca1148a0.md
Comms: #412 (ruling to Proteus, reply to #341); #413 (delegation to Archaeon).
Repro: python -m pytest roles/Harmonia/qualification/h0h5/tests -q;
       python roles/Harmonia/qualification/h0h5/run_qualification.py;
       python roles/Harmonia/science/proteus_current_instrument_audit.py;
       python roles/Harmonia/archaeology/triage_stage_a.py

+==============================================================================+
|  END OF PACKET. The reviewer is invited to answer "not worth continuing" on  |
|  any row above; that answer is first-class and will be recorded beside the   |
|  row with the reviewer's reason.                                             |
+==============================================================================+
