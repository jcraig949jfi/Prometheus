# Nyx -- forensic dossier (Tityos Phase 3 intake)

Crawler: Tityos worker g2 (Nyx/Coeus). Worktree read: F:/Prometheus-worktrees/tityos-phase3 (HEAD 36ffe8073 =
origin/main 5c98f59f1 + the Tityos charter commit; nyx/ and roles/Nyx/ unchanged by that commit).
Epistemic labels per the Tityos brief. All paths repo-relative. Every search excluded **/*holdout*/** and
**/nestor_secrets/**; no such path was opened.

## 0. Summary

- Nyx is the "Custodian of the Chop Shop", created 2026-09-11 (4219f543c, charter adopted e75e41160) to cut
  computational machinery (external and Prometheus's own) into ORGANs (transferable mechanisms) and PRESSUREs
  (environmental conditions stated without the organ) for Archaeon/Vivarium's evolutionary soup [DESIGN INTENT]
  (roles/Nyx/prompts/2026-09-11_charter/CHARTER_verbatim.md).
- Three successive regimes: (1) Chop Shop, 09-11..09-12: 6 specimens hand-dissected with preregistered cuts, a
  self-amending "knife" (nyx/KNIFE.md K1-K10) and an unflattering calibration ledger; (2) ATLAS PASS 01, 09-13..09-18:
  123 fossils from Techne's vault cut into 549 organ fragments (485 ACCEPTED), almost entirely by reading source;
  (3) Mechanism Archaeology Pipeline, 09-16..09-30: Nyx demoted from adjudicator to hypothesis author -- she freezes
  hash-bound NYX_PREDICTION_PACKETs and Harmonia executes them (Amendment 3 R32/R33) [IMPLEMENTATION FACT].
- Strength of machinery, honestly: the PROCESS discipline is among the best in the repository (freeze-before-run,
  payload-hashed boundaries, mandatory cheat/positive controls with CUT_KILL and INDETERMINATE outcomes, an author
  who is barred from adjudicating her own cut, a mechanism ledger that refuses to count packets as mechanisms, a
  validator that blocks SURVIVED_TRANSPLANT without a receipt). The MEASURED layer is tiny: of 549 atlas organs,
  546 rest on SOURCE_READ (542) or METADATA (4), 3 on execution/intervention; 0 of 10,431 coverage cells are MEASURED; 0 blind
  cuts (charter-mandated); 2 wind-tunnel receipts (one fossil); 0 mechanisms survived transplant; 0 organs consumed
  by a downstream ecology [IMPLEMENTATION FACT, computed from nyx/atlas/fossils/*.json and nyx/atlas/out/*.json].
- Mechanism labels: the atlas "mechanism" labels are LLM readings of code with no positive-control validation at
  atlas scale. Where labels were tested (5 packets, 3 adjudicated with substance), adjudication was by Harmonia,
  which also built several of the instruments -- independence is partial (section 12).
- Nyx's own phrase sums it: "a READ layer ... and NO MEASURED layer" (nyx/atlas/ATLAS_STAGE_A_REVIEW_2026-09-16.md
  s0) [HISTORICAL CLAIM, confirmed by count]. Nothing in the atlas is mechanistically understood because Nyx labelled it.

## 1. Charter and role evolution

- Name: Nyx. Aliases: "Custodian of the Chop Shop", "the Chopper". Instances seen in commits: Nyx (M1, 09-11..09-12,
  unsigned instance), m2-0c0adfe1 (M2, 09-16..09-17, closed c60b78f17), gandalf-9e21f277 / gandalf-226cd218 /
  gandalf-d1f90ae1 (M3 GANDALF, 09-17..09-30) [IMPLEMENTATION FACT] (git log -- nyx roles/Nyx; 139 commits).
- Original charter 2026-09-11 (CHARTER_verbatim.md, sha in MANIFEST): ORGAN/PRESSURE distinction; 15 required organ
  questions incl. CONTROL and CHEAT; failure is substrate; "architecture may be destroyed, provenance may not"; no
  canonical ontology (second Chopper anticipated); never build the world for her own pressure; Halloween 10-31
  metabolic-cycle target [DESIGN INTENT].
- 2026-09-11 rulings NYX-23..27 (evidence grades T1-LOCAL/T1-SOURCE/T2/T3; routing to real seats; second Chopper
  deferred; Nyx does not grade competing cuts) (nyx/README.md; roles/Nyx/BACKLOG_H0H5.md NYX-26) [DESIGN INTENT].
- 2026-09-12 Keeper directive: catalogue loop over Wikipedia algorithm lists (roles/Nyx/prompts/
  2026-09-12_directive_catalogue_loop/) -> nyx/catalog/ [DESIGN INTENT].
- 2026-09-13 ATLAS PASS 01 operator charter (roles/Nyx/prompts/2026-09-13_atlas_pass_01/OPERATOR_CHARTER.md):
  fossil anatomy, rejected cuts, wind tunnel (20 standard interventions), recurrence ladder R0-R5, blind cuts,
  "NO LLM CONSENSUS AS CONTROL", "DO NOT DEFINE NOVELTY SEMANTICALLY" [DESIGN INTENT].
- 2026-09-16 Mechanism Archaeology Pipeline (Founding Charter + Amendments 2, 3; Amendment 1 never received):
  Techne -> Nyx -> Harmonia -> Theophrastus -> Archaeon/Vivarium -> Soup; R32 SUPERSEDES Nyx's Stage C/D
  (ablation, fingerprints) -- formal ablation moves to Harmonia; Nyx exploratory runs must be labelled SCOUT/SEEN/
  NON-ADJUDICATIVE; R33 prediction-packet schema; R34 payload-hashed provenance on every cut; R28 the Mechanism
  Kinship Wager MKW-1 (falsified at N=50 if no replicated cross-lineage displacement) [DESIGN INTENT]
  (roles/Nyx/prompts/2026-09-16_mechanism_archaeology_pipeline/).
- 2026-09-17 topology ruling: Nyx, Techne, Harmonia on M3; M1/M2 Nyx shut down (roles/Nyx/prompts/2026-09-17_topology_m3/)
  [HISTORICAL CLAIM].
- 2026-09-18 "refinery" directive: finish the 121-fossil census and FREEZE Stage A; no new broad census until >=10
  mechanisms carry Harmonia verdicts; scoreboard becomes the output (roles/Nyx/prompts/2026-09-18_refinery_directive/).
- 2026-09-19 / 09-19b directives: ASAL golden path; "A MECHANISM IS NOT A PACKET" -> mechanism ledger; frozen
  probe battery; behavioral cuts held until a full-domain replication runs.
- Terminal state at crawl: ACTIVE on M3 (instance gandalf-d1f90ae1, 2026-09-30); open packet
  MECH-AVIDA-ANCESTRY-RETENTION-001 with Harmonia; holds in force (roles/Nyx/STATUS.md top block) [HISTORICAL CLAIM].
- Relations: upstream Techne (fossil vault, provenance vocabulary imported in nyx/atlas/schema.py), downstream
  Archaeon/Vivarium (Chop Shop), Harmonia (adjudicator), Theophrastus (transplant/landscape cells, OFFERED only),
  Ares (W4 reading), Artemis (ledger-staleness audit #1011).
- Hosts: M1 (09-11..12), M2 SPECTREX5 (09-16), M3 GANDALF (09-17..). M3 has no WSL2/docker/C compiler (STATUS
  "host fact"), which governs which mechanisms could be adjudicated (section 21).

## 2. Code/system architecture

Total Python ~2,900 lines plus per-fossil cut scripts (nyx/atlas/cuts/*.py, 123) [IMPLEMENTATION FACT].

- CHOP SHOP (nyx/chop/, nyx/specimens/): chop/schema.py (nyx.chop/0 validator: SPECIMEN/ORGAN/PRESSURE; checks
  presence, vocabulary, HOLLOW = all 15 answers "unknown", LEAK = pressure text names a famous name);
  chop/cutledger.py (per-specimen cuts.json bookkeeping: INHERITED/DISCOVERED/PERTURBED stamps, kind changes);
  specimens/<name>/{specimen.json, PROVENANCE.md, organs/, pressures/, FAILURES.md, AMBIGUITY.md, DELIVERIES.md,
  ablations/RECEIPT_*.json}. Specimens: map_elites, dreamcoder, lean_simp, hypothesis_shrinker,
  diomedes_k0_census, go_explore.
- ATLAS (nyx/atlas/): schema.py (nyx.atlas/0 + nyx.atlas/1-provenance; 35 organ fields, 20 coverage dims each with
  basis READ|MEASURED, evidence grades METADATA/SOURCE_READ/EXECUTED/INTERVENED, rejection reasons, recurrence
  levels R0-R5, 20 wind-tunnel interventions); census.py (whole-system records seeded from Techne record.json);
  author.py (Cut authoring API); cuts/<body>.py (one deterministic script per fossil that writes
  fossils/<id>.json); build.py (projects fossils into 11 out/*.json artifacts + DEPTH_MAP scoreboard; "counts are
  computed, never typed"); tunnel.py; migrate_v1.py.
- PIPELINE OBJECTS: predictions/schema.py (nyx.prediction_packet/1 validator; requires cheat + positive control or
  POSITIVE_CONTROL_UNAVAILABLE with reason), predictions/MECH-*.json + .FREEZE (8 packets); gates/LEDGER.json
  (handoffs, returns, escalations, packets_issued, unresolved_anomalies); gates/MECHANISMS.json + mechanisms.py
  (nyx.mechanism_ledger/1; 7 mechanisms).
- PROBES: atlas/probes.py (14 declared observer-independent frame-stack probes + open-channel descriptor), frozen
  by source sha256 53f63df5... in probes.FREEZE (2026-09-19).
- EXPERIMENTS: atlas/experiments/pathfinder_ablation.py (SPIN model ablation in docker), experiments/avida_ancestry/
  (spop reader, reference model, strata, definedness.py + DEFINEDNESS.json, adjudicate.py harness the author has
  not run on the body).
- CATALOGUE (nyx/catalog/): schema.py (nyx.bit/0, 8 signature axes), ingest_wikipedia.py, search.py (axis-overlap
  matcher that refuses queries containing names), controls.py + queries/planted.json, loop.py, 321 bits
  (16 chopshop T1-LOCAL, 305 Wikipedia list-of-algorithms T2), eval/EVAL01.
- READINGS: readings/ares_w4_reading.py (Ares W4 evolved-network carrier reading), readings/theo_req_003_composition.py.
- Tests: nyx/tests/ 7 files, 52 test functions (schema, cutledger, catalog, prediction schema, probes, scoreboard,
  avida) [IMPLEMENTATION FACT].
- Data flow: Techne vault body (hash-verified) -> Nyx reads files -> cut script -> fossil JSON -> build.py ->
  out/*.json; selected organ -> frozen packet -> comms -> Harmonia run -> typed return -> Stage D' rows in
  LEDGER.json/MECHANISMS.json. Persistence: git only (JSON); comms via Postgres queue.

## 3. Inputs and outputs

- Inputs: Techne fossil vault bodies + record.json (121 census + 2 operator-directed ALife bodies); specimen pins
  from techne/acquisition; Prometheus internal code (diomedes K0 census); Wikipedia list pages (parse API, revid);
  Harmonia rulings; Ares fossils (ares/) [IMPLEMENTATION FACT].
- Outputs: 6 specimen dossiers (organs/pressures), 123 fossil records (549 organ fragments, 359 rejected cuts,
  172 pressures, 665 composition edges), 15 recurrence candidates, 2 fingerprint receipts, 8 frozen prediction
  packets, 7 mechanism-ledger entries, 321 catalogue bits, review packets (roles/Nyx/reports/), deliveries via
  comms (#44, #45, #52, #175, #176, #190, #191, #202, #296, #309-#320, #357, #494, #1069...) [IMPLEMENTATION FACT].

## 4. Claim class it was meant to police

Nyx is not a police seat; she is a claim PRODUCER whose claims are "machinery M inside fossil F does X; it is
transferable; it responds to pressure P". The claim class the seat's machinery polices is her OWN: inherited
boundaries (human names mistaken for mechanisms), hollow records, pressure-organ leakage, invented certainty
(K2 "unknown --" prefix), and after R32, prediction packets that cannot fail [DESIGN INTENT].

## 5. Measurement methodology

- Chop Shop: PREREG (boundary, reading order, predictions, stopping rule) BEFORE reading bodies; CUT-1 flow-first
  reading; SWITCHES = run specimen-exposed ablations (lean `simp only` variants with one 9-s compile; hypothesis
  Phase.shrink off; census bootstrap self-test); CUT-2 paper attack; ASSESS via cutledger metrics (inherited rate,
  kind changes by argument vs by run) (nyx/KNIFE.md "How the knife is applied") [IMPLEMENTATION FACT].
- Atlas: a Claude instance reads source files in a fossil body and writes organ records with READ coverage values;
  "bodies MATCH" receipts verify file hashes, not anatomy (nyx/atlas/samples/stageA_bodies_*.json)
  [IMPLEMENTATION FACT]. Throughput was ~10 fossils per commit on 09-17 (commits 6da25082b..b64b97f65), i.e. the
  depth of reading per fossil was necessarily shallow [CODE-INFERRED CAPABILITY].
- Pipeline: a packet states boundary (file, payload sha256, lines), mechanism claim, interventions with observable,
  direction (INCREASE/DECREASE/UNCHANGED/NON_MONOTONIC/REGIME_DEPENDENT), magnitude band and band_basis, cheat
  control, positive control, CUT_KILL, INDETERMINATE; canonical JSON hashed before Harmonia opens (AMENDMENT_3 R33;
  nyx/atlas/predictions/schema.py) [IMPLEMENTATION FACT].
- Readings (Ares W4): replay, substitution, reduction to a sufficient sub-circuit, synthetic drive, on the fossil's
  own bytes; predictions written before two consequence runs (roles/Nyx/reports/ARES_W4_READING_2026-09-25.md s7-8)
  [REPORTED RESULT -- UNVERIFIED].

## 6. Null/control generation

- Chop Shop CHEAT controls ("deliberately privileged mechanism that shows the detector can recognize the property")
  required per organ by charter IV; negative controls run FIRST (K4); "null configuration is not null until shown"
  (K6: erase candidates until the baseline stops working) [DESIGN INTENT]; executed in lean_simp, shrinker, census,
  go_explore receipts [IMPLEMENTATION FACT] (nyx/specimens/*/ablations/).
- Census duplicate control (N2): a candidate organ that recomputes a textbook quantity on foreign inputs is refused
  as RECURRENCE (diomedes_k0_census: 0 organs, 2 tempted candidates refused on a control written before inspection)
  [REPORTED RESULT -- UNVERIFIED] (nyx/CHOP_SHOP_CALIBRATION_2026-09-12.md).
- Atlas: SPIN pathfinder ablation included a semantics-preserving rename CONTROL (expected errors: 1)
  (nyx/atlas/fingerprints/spin-pathfinder-priority-inversion-1997/).
- Packets: cheat/payload-reading control mandatory; e.g. particles 002 cheat = injected exact logLt, criterion later
  replaced by per-seed identity because "V == 0.0" failed on float rounding (calibration LEDGER 2026-09-18).
- Avida packet: each exact row's definedness and cheat control checked on a synthetic fixture BEFORE the hash; the
  author did not open any .spop (nyx/atlas/experiments/avida_ancestry/DEFINEDNESS.json) [IMPLEMENTATION FACT].

## 7. Positive controls

- KNIFE K4 explicitly deprioritised positives ("passing positives taught nothing here") [DESIGN INTENT].
- RS_CALIBRATION_PAIR_001 is the clearest positive control in Nyx's lane: a KNOWN-identical-by-descent pair
  (Rockliff 1991 RS vs Karn libfec RS) plus self-pairs and a mismap, used to calibrate Harmonia's equivalence ruler
  before any surrogate is judged; Harmonia executed 2000 trials/error-count: CUT_SUPPORTED, but Nyx's expectation
  table missed that the bodies emit different corrected words 33/2000 at e=4 (nyx/atlas/calibration/
  RS_CALIBRATION_PAIR_001.json; roles/Harmonia/rulings/RULING_RS_CALIBRATION_PAIR_001_2026-09-16.md; LEDGER row
  2026-09-16) [REPORTED RESULT -- UNVERIFIED].
- RECURRENCE_CANDIDATES row RC-01 (same pair) is declared as the positive control a Stage E recurrence instrument
  must place at R5; no Stage E instrument was ever run (nyx/atlas/recurrence/stageA_reading_candidates_2026-09-16.json)
  [IMPLEMENTATION FACT].
- Particles 001 positive control (N-scaling band [10,1000]) FAILED: measured 5463 -> PREDICTION_INDETERMINATE +
  CHALLENGE; band had been set "from a picture of the regime" (roles/Harmonia/rulings/
  RULING_PARTICLES_ESSTRIGGER_001_2026-09-17.md; LEDGER 2026-09-17) [LATER CORRECTION / CONTRADICTION].
- Probe battery: each probe has a synthetic ordering test (translating > breathing, noise vs static) -- a
  separability positive control on toy fixtures only; never exercised on real Lenia/ASAL data because behavioral
  cuts are held (nyx/tests/test_probes.py; probes.FREEZE) [IMPLEMENTATION FACT].
- Catalogue: planted positive queries were written by the same author against the bits (circular); EVAL01 used
  10 external queries from other seats' docstrings: top-1 HIT 3/10, MISS 4/10 (nyx/catalog/eval/EVAL01/EVAL01_RESULTS.md)
  [REPORTED RESULT -- UNVERIFIED].
- Atlas organ labels (485 ACCEPTED): NO positive-control validation of the labelling process exists (no blind cut,
  no second Chopper, no MEASURED coverage) [IMPLEMENTATION FACT].

## 8. Negative controls

- Lean c23 negative control (2+2=4 with decide off and Nat folders erased must NOT close) did not fire -> hidden
  machinery (eq_self builtin; unifier Nat-literal defeq) found; c23 demoted (LEDGER 2026-09-11; KNIFE K5/K6).
- Shrinker P-a5 cheat control "strictly decreasing" was vacuous (all() over empty generator) -> "read the control's
  CODE before its result" (LEDGER 2026-09-11).
- SPIN run 1 secondary indicator vacuous (pan prints "invalid end states +" every run); repaired, primary unchanged
  (ablate_rule_vs_mutex_run1_vacuous_indicator.json).
- Packets: CUT_KILL condition mandatory; e.g. ASAL cut_kill "silent" (independent metric agrees 5.6e-16).

## 9. Neutral/intermediate controls

- MINIMAL/HUMAN/MIXED/BROKEN/DECOY soup conditions specified in charter XIII; never executed by any ecology
  [DESIGN INTENT, never instantiated].
- PREDICTION_INDETERMINATE / SUPPORTED_BY_WITNESS / SUPPORTED_ON_EXECUTED_SUBSET as preregistered intermediate
  verdict grades (Harmonia A4/A6 rules adopted into Nyx's practice) [IMPLEMENTATION FACT in rulings].
- Atlas residue states (EXPLAINED / PARTIALLY_EXPLAINED / LARGE_RESIDUE / CUT_INSTRUMENT_INSUFFICIENT): 29/58/30/5
  [IMPLEMENTATION FACT] -- self-assessed by reading.

## 10. Qualification criteria / gates / thresholds

- Atlas ACCEPTED requires at least SOURCE_READ of the boundary; METADATA-only acceptance is a validator error
  (schema.py) [IMPLEMENTATION FACT]. That is the whole admission bar for 482 organs.
- Mechanism ledger: minimal_executable_organ needs cut_id + boundary; falsifier non-empty; SURVIVED_TRANSPLANT
  requires a SUPPORTED transplant row (mechanisms.py) [IMPLEMENTATION FACT]. Minor defect: the check also accepts an
  outcome "SURVIVED" that is not in TRANSPLANT_OUTCOMES (harmless today; would be flagged by the outcome check).
- Stage A freeze gate: no new census until >=10 mechanisms have Harmonia verdicts (09-18 directive); at crawl 3
  adjudicated-with-substance [IMPLEMENTATION FACT: gates/LEDGER.json].
- Open-packet cap 3 per lane (build.py).
- MKW-1 wager at N=50 resurrected cuts with landscape measurements: N reached ~0 [IMPLEMENTATION FACT: no
  Theophrastus cell accepted].

## 11. Statistical methods

Mostly exact/deterministic rows (POET, Avida, SPIN) or existential witnesses (ASAL I1/I2). Where statistics
appeared, they were the weak point: particles claim (c) needed ~11,700 seeds/arm for its band edge but was posed at
50 (LEDGER 2026-09-18); ASAL I0 froze a 5-seed estimated mean as an exact threshold (margin 1.1 sd)
(RULING_ASAL_LEGIT_SEARCH_001 s7). Nyx adopted Harmonia's A2 (power for comparative claims) and A7 (no estimated
mean as exact cutoff) afterwards [LATER CORRECTION / CONTRADICTION]. Catalogue EVAL01 is descriptive (n=10). No
multiplicity accounting across the 549-organ atlas (none needed: nothing there is tested).

## 12. Independence assumptions

- Interpreter/verifier separation (Founding Charter C3, R32) is the core independence claim: Nyx hypothesises,
  Harmonia executes [DESIGN INTENT]. In practice: Harmonia also built the instrument for ASAL (ruler, class rule,
  thresholds from one Orbium rollout -- "Conflict of interest: the instrument, plan and ruling are this seat's",
  RULING_ASAL_LEGIT_SEARCH_001 s6); Techne built the CLIP port and Lenia port; Harmonia ran packets on the same M3
  host and checkout family as Nyx. Independence is of AUTHOR (separate LLM instances with separate charters), not of
  model family, corpus, or substrate [CODE-INFERRED CAPABILITY].
- All three seats are Claude instances; the ATLAS charter forbids "LLM consensus as control", yet the
  author/adjudicator split is two LLM instances -- the rule is honoured only where adjudication executes code
  [UNKNOWN / AMBIGUOUS whether this was ever discussed].
- "Observer stability" (HARM-56 A_OBSERVER_STABLE) compares the torch CLIP port with native Flax CLIP -- the same
  model weights; it establishes port fidelity, not independence from CLIP's representation
  (roles/Harmonia/rulings/RECORD_HARM55_HARM56_NATIVE_OBSERVER_2026-09-30.md) [IMPLEMENTATION FACT].
- Second Chopper (charter VII) and blind cuts (ATLAS charter) were the designed independence controls for
  decomposition; neither ever happened (BLIND_CUT_COMPARISON n=0; NYX-26) [IMPLEMENTATION FACT].
- Provenance vocabulary imported from Techne (schema.py `from techne.fossils.record import LINEAGE_RELATIONS`):
  shared code path by design.

## 13. Provenance tracking

- Wins: R34 payload hashes on every cut and every packet boundary; this is what let Harmonia catch
  deflate.c:667 vs :672 (Nyx counted lines on grep-filtered output) before execution (#317; LEDGER 2026-09-16)
  [REPORTED RESULT -- UNVERIFIED]. Grade discipline (T1/T2/T3; ORIGINAL_ARTIFACT vs LATER_TRANSCRIPTION) carried
  through 123 fossils (78 ORIGINAL_ARTIFACT, 21 CONTEMPORARY_COPY, 21 UNKNOWN) [IMPLEMENTATION FACT]. Record defects
  found and returned to Techne (4.3-Reno tape missing files 5-7; LINPACK duplicate body; ELIZA 1965 matcher outside
  the body) (STATUS) [HISTORICAL CLAIM].
- Failures: stale claims about other seats' state posted in delivery bodies twice (Vivarium "never booted" 09-11;
  Techne handoff "empty" 09-30) (LEDGER); 19 cuts still provenance-grade UNKNOWN pending a Techne ruling (#1071);
  Techne's "superseded" relation has no fixed direction (17 edges, both readings) (build.py note); boot-time
  `git stash` + `git pull` in the canonical checkout displaced a Hephaestus WIP (LEDGER 2026-09-17) [HISTORICAL CLAIM].

## 14. Known defects

NYX-47 (cost_class free text in 12 pre-09-17 pressures), NYX-48 (absolute F:/ paths in five 09-13 scripts);
NYX-44 frozen go_explore controls called a guessed method (RLEArray.fromarray) hidden behind hasattr() guards,
repaired five times (nyx/specimens/go_explore/ablations/RECEIPT_N3_c04_2026-09-15_repaired_r2..r5.json);
build.py writes timestamped out/*.json so every test run dirties the tree (RESUME record); mechanisms.py accepts
"SURVIVED" outside its own vocabulary; scoreboard packets_issued (5) omits the three gzip pilot packets, which
remain only as handoff rows [IMPLEMENTATION FACT].

## 15. Historical audits performed (by and on this seat)

- By Nyx: on herself (calibration LEDGER, 23 rows; CHOP_SHOP_ASSESSMENT_lean_simp; CHOP_SHOP_TRANSFER;
  CHOP_SHOP_CALIBRATION); on diomedes K0 census (found an LCG power-of-two bootstrap degeneracy, reported #192);
  on Ares W4 instrument (node ablation never removes output nodes, so it hid one third of the carrier ring).
- On Nyx: Harmonia rulings (#317, #363, #382, #441/#446, #1063, #1067); operator reviews of review packets
  (roles/Nyx/reports/REVIEW_PACKET_*.txt; ASAL review tightened I3); Vivarium return #182 (all 6 pressures
  unbuildable/vacuous); Archaeon return #200 (c07 INTERFACE_INSUFFICIENT); Artemis Fabric audit #1011 (stale
  ledgers on #189) [HISTORICAL CLAIM].

## 16. Historical findings (outcome labels on the record)

- Chop Shop lean_simp: 23 candidates -> 4 organs, 4 pressures; two PERTURBED boundaries found by one compile
  [REPORTED POSITIVE, self-assessed]. Pressures #175: REJECTED_BLOCKED (no rewriting substrate owner) [REPORTED NEGATIVE/NULL].
- hypothesis_shrinker: 6 organs, 1 pressure; c07 delivered to Archaeon -> INTERFACE_INSUFFICIENT [REPORTED NEGATIVE/NULL].
- diomedes_k0_census: 0 organs, 0 pressures, null supported [REPORTED NEGATIVE/NULL].
- go_explore: 1 organ, no consumer; all 14 boundaries UNTESTED (nothing ran) [INCONCLUSIVE].
- MAP-Elites / DreamCoder pressures #44/#52: vacuous on the only live corpus / blocked on objective family [REPORTED NEGATIVE/NULL].
- Atlas Stage A: 123 fossils, 485 accepted organs by reading [UNKNOWN -- unvalidated labels].
- SPIN pathfinder ablation (6 arms, pre-registered in docstring) [REPORTED RESULT -- UNVERIFIED; executed 09-14
  before R32 made Nyx-run ablation non-adjudicative].
- MECH-GZIP-LEVELTABLE-001/002/003: 002 challenged (wrong line); 003 never adjudicated (not runnable on M3)
  [INSTRUMENT FAILURE / INCONCLUSIVE -- the Founding Charter's first end-to-end pilot never completed].
- MECH-PARTICLES-ESSTRIGGER-001 INDETERMINATE (positive control failed); 002 CUT_SUPPORTED on boundary, claim (c)
  PREDICTION_FAILED@50 / INDETERMINATE@400 [MIXED].
- MECH-ASAL-LEGIT-SEARCH-001: boundary CUT_SUPPORTED; I0 PREDICTION_FAILED; I1/I2 SUPPORTED_BY_WITNESS; I3
  SUPPORTED_ON_EXECUTED_SUBSET (395 of 1,045 executed) [MIXED].
- MECH-POET-NOVELTY-ESTIMATOR-001: CUT_SUPPORTED 4/4 as EXECUTED STRUCTURAL IDENTITY, NOT confirmatory
  (predictions_tested 0) [REPORTED POSITIVE as code fact; not a test].
- MECH-AVIDA-ANCESTRY-RETENTION-001: frozen blind, pending [UNKNOWN].
- Ares W4 reading: carrier is a 3-node saturating positive-feedback ring through output node 15; 10/10 lineages hold
  the bit as a saturated loop with gain > 1 [REPORTED RESULT -- UNVERIFIED].
- Catalogue EVAL01: top-1 3/10 [REPORTED NEGATIVE/NULL for the catalogue as a retrieval instrument].
- Scoreboard 09-30: mechanisms_registered 7, evidence_supported 3, MECHANISMS_THAT_SURVIVED_TRANSPLANT 0.

## 17. Later corrections (timelines)

- c23 negative control: predicted to fire -> did not (hidden eq_self/unifier) -> K5/K6 -> c23 UNRESOLVED (09-11).
- gzip packet: :667 claimed -> Harmonia #317 sed -n 672p -> 003 supersedes; immutable 002 kept (09-16).
- particles 001: band [10,1000] -> 5463 measured -> challenge -> 002 with SEEN scout (09-17).
- particles (c): ratio in [1.05,5] -> 0.512@50 then 1.161@400 -> dropped from cut, re-pose with power (09-18).
- ASAL I0 "catalogue does not cross" -> 0.8076 < 0.8167 -> A7 (no estimated mean as exact threshold) (09-18).
- ASAL I3 over intended domain -> only 395/1045 executed -> A4/A6 domain-acceptance fixture before freeze (09-18).
- POET rows scouted SEEN then offered as predictions -> Harmonia #1063: a seen deterministic row is a code fact ->
  predictions_tested 0; Avida frozen blind (09-30).
- Ares seed-3 carrier "GATE<->MAX 2-cycle" (cycle-1 report) -> 3-node ring through output node (09-25).
- Coeus-style truncated-search failure did NOT recur here, but stale-claim-about-another-seat recurred twice.

## 18. Pivots

Chop Shop (organs for a soup) -> catalogue (searchable bits) -> Atlas (fossil anatomy at scale) -> Pipeline (one
mechanism to a verdict; scoreboard over atlas) -> mechanism ledger (identity over packets). Nyx herself recommended on
09-16 "STOP cutting and start running" (ATLAS_STAGE_A_REVIEW s0), then the 09-17/18 work cut the remaining 91
fossils at ~10/commit before the operator froze Stage A [HISTORICAL CLAIM]. The pivot moved Nyx from author of
ablations to author of predictions -- correct for independence, but it ended Nyx-run causal lesions.

## 19. Journals / TODOs / backlogs

roles/Nyx/journal/ (9 days, 09-11..09-30); roles/Nyx/STATUS.md (narrative, superseding blocks); roles/Nyx/RESUME_2026-09-25.md
(boot record, traps); roles/Nyx/WORK_STATE.json; roles/Nyx/BACKLOG_H0H5.md (NYX-xx incl. NYX-26 second Chopper);
roles/Nyx/calibration/LEDGER.md (23 wrong calls -- the single most useful file in the seat); nyx/LOOP.md
(WIP cap, anti-collection table); nyx/specimens/QUEUE.md (25+ queued specimens never cut: Z3, cvc5, Lean,
AlphaGeometry, PBT, lexicase...). They reveal: consumer starvation (CONSUMED 0) from day 1; 11-day packet stall
on an offline Harmonia instance (escalation row 09-30).

## 20. Research reports

- nyx/CHOP_SHOP_ASSESSMENT_lean_simp_2026-09-11.md -- the Chopper assessed against preregistered metrics.
- nyx/CHOP_SHOP_TRANSFER_lean_vs_shrinker_2026-09-11.md -- does the corrected knife transfer.
- nyx/CHOP_SHOP_CALIBRATION_2026-09-12.md -- 4 specimens side by side; three transfer-failure classes.
- nyx/atlas/ATLAS_STAGE_A_REVIEW_2026-09-16.md, nyx/atlas/FIRST_PASS_RETURN_2026-09-16.md -- read layer, no measured layer.
- roles/Nyx/reports/REVIEW_PACKET_2026-09-17..09-30_*.txt (9) -- operator review packets per block.
- roles/Nyx/reports/ARES_W4_READING_2026-09-25.md (+ _run.txt) -- evolved-network carrier reading.
- roles/Nyx/reports/THEO_REQ_003_REPLY_2026-09-30.md -- composition counts (D(D-1) children).
- roles/Nyx/reports/STATUS_REPORT_2026-09-12_external.md.
- nyx/catalog/eval/EVAL01/EVAL01_RESULTS.md -- catalogue retrieval eval.

## 21. Failure cases

False positives / near-FPs:
- Hidden-machinery positive control: lean c07 passed because of an unnamed builtin (K6).
- Vacuous cheat control (empty-generator all()) reported true.
- Vacuous SPIN indicator string.
- Estimated-mean-as-exact-threshold (ASAL I0) -- produced a "crossing" of a convention.
- Seen-row-as-prediction (POET) -- would have counted 4 "predictions confirmed" that were code reads.
- Atlas portability: YES asserted for 533/549 organs by reading; never tested (portability != utility was a charter
  rule, but portability itself is unmeasured).
Plausible false negatives (FN):
- Host-capability filter: M3 had no docker/compiler, so only pure-Python mechanisms (particles, ASAL port, POET
  novelty.py, Avida saves) could be adjudicated; gzip and 100+ C/Fortran fossils had no route to a verdict.
- Underpowered comparative claims (particles (c)) recorded as FAILED at 50 seeds.
- Domain coverage: ASAL port refused 650/1045 draws (fractional b strings, kn/gn>=3, oversize) -- mechanisms in the
  refused region are unseen.
- Pressures killed for lack of a substrate owner (#182) -- unhostable, not shown false.
- Organ-consumer interface mismatch (c07 sequence vs program trees) -- a representation FN, not a mechanism FN.
- Ares instrument blind spot (node ablation never removes output nodes) -- a lesion design that cannot see loops
  through outputs.
- Catalogue representation misses (EVAL01 Q05: counterexample-guided bit at rank 66 because its signature carried
  its lineage's objects).

## 22. Mechanism archaeology

- What constitutes a mechanism: three operational definitions in sequence. (a) Chop Shop ORGAN = a record answering
  15 questions incl. CONTROL and CHEAT, scale SYSTEM..PARAMETERIZATION (nyx/chop/schema.py). (b) Atlas organ = a
  35-field record with a source_boundary, ACCEPTED on SOURCE_READ (nyx/atlas/schema.py). (c) Ledger mechanism = a
  persistent identity with an executable boundary (file:lines + payload sha256), proposed behavior, predicted
  intervention, falsifier, evidence and counterevidence packets, observer dependence, transplant history
  (nyx/atlas/mechanisms.py: "a mechanism without an executable boundary is a name, not a mechanism") [IMPLEMENTATION FACT].
  Only (c) has an adjudication path; 7 exist.
- Decomposition: read-in-data-flow-order by an LLM instance (K1), SYSTEM -> SUBSYSTEM -> MECHANISM -> PRIMITIVE,
  parent/child links in fossil JSON; stopping rule "while pieces retain independently testable behavior" (charter
  III) was judged by reading. Inherited-boundary rates in Chop Shop: 0.87 / 0.56 / 1.00 / 0.86 -- most boundaries
  coincide with the human code's own function/file boundaries (CHOP_SHOP_CALIBRATION) [REPORTED RESULT -- UNVERIFIED].
  All 122 atlas cuts are ANCESTRY_AWARE; 0 blind [IMPLEMENTATION FACT].
- Causal lesions: yes, but few. Chop Shop specimen switches (lean simp variants, shrinker Phase.shrink off, go_explore
  c04 frozen controls); one atlas fossil-level ablation (SPIN pathfinder: remove/reverse/weaken the priority rule,
  remove mutex, rename control); after R32 lesions belong to Harmonia: ASAL used a search intervention (not a lesion),
  particles varied N and world, POET/Avida are exact structural identities on the fossil's bytes (not lesions).
  Organs with an ablation result: 3 of 549 (546 "NOT_RUN") [IMPLEMENTATION FACT].
- Transplantability: asserted, never demonstrated. portability YES 533/549 by reading; one transplant OFFERED
  (ASAL score -> Theophrastus cell, 09-18), not accepted; MECHANISMS_THAT_SURVIVED_TRANSPLANT 0; Chop Shop organs
  CONSUMED 0 [IMPLEMENTATION FACT].
- Correlation vs mechanism: atlas labels are neither correlational nor causal -- they are descriptive readings.
  The ASAL mechanism claim is about a SCORE (a detector of CLIP-embedding novelty) and its classes
  (METRIC_EXPLOIT/GENUINE/UNCLASSIFIED) come from a Harmonia class rule whose thresholds were set from one Orbium
  rollout, 47/105 crossers UNCLASSIFIED, with the owed disjoint-set calibration not done (HARM-56 tested observer
  stability, not class validity) [IMPLEMENTATION FACT / LATER CORRECTION]. POET/Avida claims are code facts, which
  is stronger than correlation but tells nothing about function in an ecology.
- Donor/fossil selection: Chop Shop specimens chosen by "proximity to a living consumer, never fame" (QUEUE.md);
  atlas fossils = Techne's 121-body census (Keeper lineage list), stratified n=30 sample drawn seed 20260913 before
  opening bodies, then all 121, plus 2 operator-directed ALife bodies (ASAL, POET); adjudication targets selected
  de facto by M3 runnability [IMPLEMENTATION FACT / CODE-INFERRED CAPABILITY].
- Prior-art corpus: the atlas itself (123 fossils, 549 organs) and the catalogue (321 bits; 305 from Wikipedia's list
  of algorithms at T2). "Novel" in Nyx's usage means "not registered in the atlas" -- stated explicitly in the Ares
  reading ("novelty here means not registered, not not in the literature") [IMPLEMENTATION FACT].
- Families represented (atlas): compression (gzip, bzip2, zlib, LZW x2, compact), ECC/coding (Reed-Solomon x2,
  libcorrect, LDPC, Viterbi), numerics (LINPACK x2, EISPACK x2, LAPACK, MINPACK, QUADPACK, ODEPACK, FFTPACK, KISS FFT,
  ERFA, SGP4), SAT/logic/provers (MiniSat x2, zchaff, PicoSAT, WalkSAT, E prover, GNU/SWI Prolog, microKanren,
  Souffle, CLIPS, Graphplan, FF), OS/concurrency (xv6, glibc rwlock, TinySTM, ConcurrencyKit, Helgrind fixtures, Go
  deadlock fixtures, SPIN/Pathfinder, DMTCP), networking/distributed (BSD TCP x3 + tapes, Linux congestion, backoff,
  Raft, Paxos, memberlist, Redlock, spdylay, pybreaker), memory (dlmalloc, Boehm GC, buddy allocators, LRU), storage
  (SQLite, LevelDB, LMDB), control/estimation (PID, autotune, do-mpc, L1 adaptive, self-tuning regulator, Kalman x3,
  python-control, padasip), crypto (DES, AES, MD5, Heartbleed), hardware RTL (arbiters x2, FIFO, UART, PicoRV32,
  biRISC-V predictor), early AI/languages (ELIZA x3, LISP 1.5, PAIP, femtolisp, TinyScheme, pForth, GNU APL, COBOL,
  Whitaker's Words), games (Spacewar, BASIC games, TSCP, Core War), ML/optimisation (genann, Hopfield, MiniSOM,
  CMA-ES, emcee, GLPK, PyPortfolioOpt, py_vollib), ALife/open-endedness (Avida, ASAL, POET, Go-Explore), SMC
  (particles), fuzzing (radamsa), bioinformatics (SSW). Mechanisms that reached the ledger come from 4 lineages
  (ASAL, particles SMC, POET, Avida) [IMPLEMENTATION FACT]. Absent: modern deep learning, theorem provers of the
  Lean/Coq class beyond the lean_simp specimen, program synthesisers beyond DreamCoder notes.

## 23. Novelty/prior-art audit

Relevant in two places. (1) The ATLAS charter forbade semantic novelty ("DO NOT DEFINE NOVELTY SEMANTICALLY ... preserve
first") and planned operational novelty as distance in measured fingerprints -- never possible because 0 cells are
measured [DESIGN INTENT / IMPLEMENTATION FACT]. (2) Novelty_kind {structure, behavior, observer, consequential} was
added to the packet schema (c2921864d) to stop conflating kinds. Nyx's one novelty statement (Ares W4 "NOVEL to the
atlas as an organ; KNOWN as an engineering motif outside it") correctly separates "unfamiliar to Prometheus" from "new
to science" [IMPLEMENTATION FACT]. Blind spot: the corpus is 123 hand-curated open-source bodies plus a Wikipedia
list; any "not in the atlas" statement is a statement about Techne's acquisition list.

## 24. Lens inventory

- Hash-bound prediction packet + mechanism ledger + scoreboard: reusable, substrate-agnostic protocol for "one
  mechanism to a verdict"; resolution limited by adjudicator throughput (median cut->verdict days; 11-day stall).
- Fossil anatomy atlas: a large READ-only map (549 fragments) -- a candidate index for where to aim lesions, not a
  measurement; noise unknown (no blind or second cut).
- Wind tunnel (20 interventions) + coverage dims: designed lens, essentially unbuilt (2 receipts).
- Probe battery: toy-grade until run on real frames; observer-independent by construction.
- Calibration-pair method (known-identical by descent + known-different with same label): the best idea in the lane
  for calibrating equivalence/recurrence rulers; used once.
- Catalogue matcher: toy-grade (EVAL01 3/10).
- Avida ancestry apparatus: reusable for lineage-record rulers (definedness checks on synthetic fixtures, blind freeze).
Unknowns: whether any atlas label would survive a blind cut; whether any organ is portable.

## 25. What I did not read / open questions

Not read: the 123 cut scripts individually (sampled via fossil JSON aggregates), most specimen organ JSONs, journals
other than via STATUS/LEDGER, the 9 review packets in full, the Avida packet body, the go_explore receipts in detail,
roles/Nyx/prompts/* beyond the charter, pipeline charter and amendments 2-3 rule headers, the 2026-09-12
directive_catalogue_loop text, the 305 Wikipedia bits. Did not run any Nyx code (counts computed by reading JSON).
Open: (1) did anyone ever operationalise a Nyx pressure into a world? (none found); (2) why was the gzip pilot not
re-routed to an AVX/docker host after 09-17? (3) was the author/adjudicator LLM-instance independence ever examined
against C8 "no LLM as selector"? (4) the class rule for ASAL crossers remains uncalibrated -- who owns it now?
