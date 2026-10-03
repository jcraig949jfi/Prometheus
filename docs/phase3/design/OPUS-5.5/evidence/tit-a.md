# tit-a -- evidence digest: Tityos A (Harmonia, Nyx, Techne, Hecate, Artemis)

Reader: read-only evidence reader for EPIMETHEUS (Phase 3 independent architect, OPUS-5.5), 2026-10-01.
Worktree: C:/prometheus-worktrees/epimetheus-phase3 (HEAD c9b18697b). Nothing executed except cheap
python one-liners that parsed committed JSON (nyx/atlas fossils, mechanism ledger, packets, Hecate
probe-round reports, gravity controls). No experiment, no write outside this file.

Epistemic tags: IMPL (read in code/data by me), INTENT, HIST, REPORTED (a result stated in a committed
report that I did not re-execute), CORR (later correction on the record), INFER (inferred from code),
UNK. "[confirmed]" = I opened the underlying artifact. "[crawler]" = taken from the Tityos dossier
without my opening the source. Paths are repo-relative.

The question asked of every result: what did the apparatus genuinely have the capacity to reveal?

----------------------------------------------------------------------------------------------------

## 0. Bottom line (ten points)

1. Almost nothing in this group studied a learning or developing organism. The organisms actually
   instantiated were: frozen engineered software read by an LLM (Nyx atlas), deterministic code
   bodies executed once (Nyx/Harmonia packets), enumerative generators (Theseus), LLM-written toy
   simulations (Hecate worlds), one frozen LLM doing in-context induction (Hecate alien assay), tiny
   RL learners on episode-length-1 bandits (Techne), z8 VM byte programs (Artemis P-11 panel), and VM
   genomes in a menagerie that was 75% world-blind (SFE, audited by Harmonia). [IMPL/REPORTED; s2]
2. The single most important world-demand finding: Harmonia's boundary-depth packet measured that
   48/64 SFE specimens are WORLD-BLIND (no observable responds to input/seed variation) and that
   composition destroys world-coupling in 94% of cases; 7 ordered pairs out of 4,032 were usable.
   Preregistered selection had picked an inert pair. [REPORTED, roles/Harmonia/BOUNDARY_DEPTH_PACKET_01_2026-09-05.txt;
   confirmed text]
3. The highest cognitive demand any world in this group verifiably imposed and an organism verifiably
   met is a 1-bit latch: Ares W4 champions (read by Nyx) hold a cue bit for ~37 steps in a
   saturating positive-feedback loop, 10/10 lineages; cutting recurrence floors all 10; and all 10
   FAIL a moved-cue transfer world (W16) as predicted in advance, because the latch is set-once and
   timed by the substrate reset, not a cue detector. [REPORTED, roles/Nyx/reports/ARES_W4_READING_2026-09-25.md;
   confirmed text]
4. The best organism-vs-world separation instrument is Techne's modal-collapse synthetic null: a
   world certified learnable by an authority (least squares >= 60% bin accuracy) on which REINFORCE
   and PPO scored at chance (4.91% / 4.61% vs random 4.84%). It killed the program's own six-domain RL
   "transfer" headline as class-prior recovery. [REPORTED, prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md; confirmed text]
5. The best induction-vs-lookup instrument is Hecate's INV_E coverage oracle: on table-driven alien
   systems, Claude's accuracy on never-observed entries (0.50) is below a pure-coverage oracle with a
   no-change default (0.58); real induction appeared only for compact parametric laws (poly maps 1.00
   vs 0.05) and at the level of update architecture. DESIGN_P turns this into a matched LAW/ARB
   coverage-controlled family (designed, never run). [REPORTED, roles/Hecate/harvest_w2/INV_E_induction_vs_coverage.md,
   DESIGN_P_coverage_controlled_family.md; confirmed text]
6. Mechanism claims: Nyx's atlas is a READ layer only. 549 organs, 542 SOURCE_READ + 4 METADATA,
   3 executed/intervened; 10,431 coverage cells all basis READ, 0 MEASURED; portability "YES" asserted
   for 533; all 549 cuts ANCESTRY_AWARE (0 blind). Mechanism ledger: 7 mechanisms, 0 transplants
   survived, 1 offered. [IMPL confirmed by parsing nyx/atlas/fossils/*.json, nyx/atlas/gates/MECHANISMS.json]
7. Novelty: Hecate's LLM gravity detector could not output UNFAMILIAR (no UNFAMILIAR calibration
   item; definition makes it unreachable because universal formalisms always "fit"); the alien-assay
   validation rule is passed by a lookup-table baseline, so it validates lawful-vs-noise, not novelty.
   No external corpus was ever searched by Hecate. [IMPL confirmed: hecate/gravity/controls_v1.json,
   run.py:80-94; RULER_QUALITY_2026-09-30.md s2]
8. Control-first world generation fixed attainability but not discrimination: Hecate Pass-3 v2 cut
   instrument failures (round 1: 6/16; round 2: 6/13 SPEC_UNATTAINABLE; round 3: 0/8), yet INV_J
   found 5/16 v2 worlds PASS BY CONSTRUCTION and both round-3 SIGNALs are met by the spec's own named
   simpler alternative. [IMPL counts from hecate/programs/PROBE_ROUND{1,2,3}_REPORT.json; REPORTED INV_J]
9. Auditors were never calibrated against planted defects. Harmonia's AP-1.1.0 primitives have
   transcribed fixture numbers and an ablation leg that forces flag=False (cannot fail); Harmonia made
   at least two era-3 audit errors corrected by the audited seats (Tyche H4, audit J). [IMPL confirmed
   roles/Harmonia/qualification/primitives/audit_primitives.py:146-165; CORR RULER_QUALITY C-1]
10. Independence was by role and write permission only. In Hecate every generator, implementer,
    attacker, detector, subject and auditor is Claude-family; cross-family arms (gpt-oss, gemini) died
    on free-tier quota. Nyx-author vs Harmonia-adjudicator is two Claude instances; Harmonia also built
    several of the instruments it adjudicated with. [REPORTED hecate/alien/REPORT_pilot.md; crawler]

----------------------------------------------------------------------------------------------------

## 1. What each apparatus really was (organism / world / pressure / ruler / max demand)

| engine | organism actually instantiated | world actually instantiated | pressure | ruler | max cognitive demand actually imposed |
|---|---|---|---|---|---|
| SFE/PEW menagerie (owner Archaeon/Daedalus; audited by Harmonia 09-05) | 64 VM genome specimens on the Proteus VM; composition concat.v0 | 4 input tuples x 4 seeds x 3 budgets, 6 ticks, budget 64 | none (qualification probe) | execution differential vs image digest; Proteus op-category differential | input response at all: 48/64 specimens have none (world-blind) |
| Archaeon H0-H5 lanes (Harmonia rulings; VACUOUS_READINGS) | random rule tables / genomes; learned decoder over 4,096 genomes | 3-bit task (8 witness inputs, 4 observed); C3-2 criterion constant | evolutionary / acquisition | QR paired contrasts; reach bounds | lookup over 8 inputs; H5 reach = random-permutation value (11.7305 vs 11.72) |
| Ares W4 hidden-regime world (owner Ares; read by Nyx 09-25) | GA-evolved recurrent op graphs (ADD/GATE/MAX/MUL/TANH...), value clip +-8, 2 ticks/step, plastic weights and a `keep` primitive available | cue -1/+1 (+noise) on steps 0-2, 40 steps, action reward per regime, 32 held-out eval seeds, cap 40 | GA fitness | held-out score; carriers.py SCC inventory; Nyx per-SCC latch test | 1-bit latch, set once at a fixed window; W16 (moving cue) shows no cue detection |
| Techne modal-collapse synthetic env | REINFORCE-linear; PPO-MLP (32 hidden), byte ports of domain trainers | contextual bandit, x~N(0,I_20), y=w.x+b+e, 21 bins, reward 100/0, episode length 1, 5,000 episodes x 3 seeds | sparse 0/1 reward | accuracy vs random; active-bin count; least-squares learnability authority | linear regression (authority solves >= 60%); organisms reach chance |
| Techne DiscoveryEnv / withheld benchmark | REINFORCE linear policy | degree-10 polynomial construction, 7^6 trajectories, shaped reward band 1.001<M<1.18; 3,000 episodes | shaped reward | rediscovery of 36 withheld Mossinghoff entries | rare-pattern search; only 2/36 targets inside the reward band |
| Theseus substrate (operated by Techne, May) | none: 55 enumerative generators + yield bandit | knot x EC catalog cross-products | bandit reward (uncalibrated yield_score) | generator self-verdict (99.98% of 658M records); F1 shape gate; F2 contrast vs random re-pairing | relation evaluation (lookup) |
| Hecate probe worlds (Pass 3 v1/v2, rounds 1-3) | LLM-written implementations of LLM-generated toy mechanisms | small executable sims, >=5 seeds; all 5 SIGNAL worlds cost 0.014-0.045 core-min | none | evaluate.py clauses vs positive control, null twin, cheat | execute a fixed designed behaviour; SIGNALs passed by construction |
| Hecate alien-lawful assay (Family A) | claude-opus-5-5 in context (plus local-table, affine, structured-polynomial baselines; gpt-oss 29 calls; gemini 0 valid) | 100 finite discrete dynamical systems (20 KNOWN, 40 ALIEN incl. 8 adversarial, 30 incompressible nulls, 10 DESTROY); 80 transitions; 200 held-out states | none | simulator over full state space; answer key; coverage oracle (INV_E) | induction of update architecture and compact parametric laws; table entries = coverage |
| Hecate gravity detector / meta v1 | n/a (generator arms on claude-sonnet-5) | prose mechanism descriptions | n/a | claude-opus-5-5 classifier FAMILIAR/COMPOSITE/UNFAMILIAR/INCOHERENT | n/a; UNFAMILIAR unreachable |
| Nyx atlas + Chop Shop | 123 historical engineered-software fossils; 6 hand-dissected specimens | none (reading); a few specimen switches | none | LLM reading; evidence grade field | none measured |
| Nyx/Harmonia prediction-packet adjudications | deterministic fossil code: particles SMC, ASAL Lenia numpy port, POET novelty.py, Avida saves, gzip 1.2.4 (never run) | W1/W2 state-space models; Lenia 128x128; POET fixtures; Avida spop files | none | packet-specific rows with cheat/positive controls, CUT_KILL | code-fact structural identity; no learning |
| TECHNE-107 ASAL observer | Lenia Orbium (numpy port of Chakazul/Lenia) | 128x128, 256 steps, 8 frames; 7 arms incl. GARBAGE/NOISE/STATIC/DRIFT | none | ASAL open-endedness score via CLIP ViT-B/32 | n/a; ruler test |
| Artemis P-11/CVT panel | z8 VM byte programs: 17 constructed specimens, 57 natural NPE survivors, Nestor's 138 genomes | pair tape, 96-byte cells, one-slice budget | none (certification) | P-11, FERT, LOCAL, CVT-1/2/R, SHUF/DOM | self-replication with heritable variation (copier vs painter) |

Reading: no engine in this group combined (a) an organism that learns or develops over a lifetime,
(b) a world certified to demand a capability beyond lookup/latching, and (c) a ruler calibrated on
planted positives at the capability of interest. Pieces of each exist separately (s4, s5).
[INFER from the table above]

----------------------------------------------------------------------------------------------------

## 2. Seat by seat: what was built, what it could and could not show

### 2.1 Harmonia (three lives; instrument/program auditor)

Built:
- Era 1 (Apr): consumer of Charon's F1-F14 battery plus NULL_BSWCD block shuffle; TT-Cross coupling
  engine. The "38-test battery calibrated against 3.8M objects at 100.000%" is a database-consistency
  check against theorems that never runs the battery; its script is uncommitted. [REPORTED/crawler]
  The TT engine never ran the battery: harmonia/src/validate.py:220-223 calls
  `battery.test_correlation(values_a, values_b, claim=...)` against the signature
  `test_correlation(self, finding_id, claim, values_a, values_b, ...)`
  (cartography/shared/scripts/battery_unified.py:196): `claim` is bound twice, so a TypeError always
  routes to "UNTESTED". [IMPL confirmed]
- Era 2 (Jun-Aug): program audits. Emission-path census: 658,302,367 / 658,454,531 = 99.98% of
  Theseus lifetime records were verdicted by the generator that wrote them; "the ceiling is at the
  emission side, not the detection side". [IMPL confirmed roles/Harmonia/AUDIT_20260819_detector_band.md:21,137]
- Era 3 (Sep): ~3k LOC qualification code (QR/AF/EX/FP/PR/OQ/HA/AP), STANDING_RULES A-F,
  VACUOUS_READINGS V-001..V-008, evidence audit (13 packages), ruler-quality audit. [IMPL/HIST]

What it could show:
- Re-execution plus git-chronology audits do catch real defects: Hecate W6 ORIG kill condition met by
  the packet's own ALT rows (r=0.65: LLE -0.919, ARI 1.0) while reported "not fired"; "zero
  UNFAMILIAR" uninstrumented; "affine beats Claude" from mismatched subsets (like-for-like 0.512 vs
  0.487); Odysseus S3 quality clause at ceiling (10.0 vs control 9.1, margin 1). All three Hecate
  MAJORs were later confirmed by Hecate. [REPORTED roles/Harmonia/audits/EVIDENCE_AUDIT_2026-09-30.md; confirmed text]
- Reachability analysis at design time: Tyche v0 H1/H6 PASS unreachable (3 valid worlds vs a rule
  needing >= 4, fixed by the initial population). [REPORTED RULER_QUALITY_2026-09-30.md s1; confirmed text]
- The world-blindness census (s0 point 2) is the most consequential Harmonia measurement for Phase 3:
  it found the population could not show interaction effects at all, caught two
  distinctness-by-construction traps (64/64 distinct meters, which a sha256 of the genome would also
  give; 7/7 composition profiles produced by the genome being copied onto the tape), and corrected
  its own over-generalisation (L4 "B never executes", 0/6, killed by a 400-pair sample: 223/400
  activate; predictor = first segment halts). [REPORTED; confirmed text]

What it could not show:
- Its own error rate. No planted defect was ever slipped into an audited package. [crawler; consistent
  with what I read: the 09-30 audits list no planted-defect arm]
- AP-1.1.0 (audit_primitives.py) checks are real functions, but (a) its fixtures are transcribed
  constants (HECATE_BASELINES numbers typed in, lines 148-152; GRAVITY_CALIBRATION hand-encoded,
  154-157), not re-derived from the source data at test time; (b) the "ablation" leg `chk` sets
  `flag=False` when a check is disabled (lines 161-165), so "defect escapes when disabled" is true by
  construction; (c) `reachability` enumerates a caller-supplied design space, so it is exactly as good
  as the encoding (Harmonia's own H4 error, C-1, was an encoding error: evolving baseline read at t=0).
  The freeze_precedes test does run on real git history (Ananke W-O). [IMPL confirmed]
- Harmonia's own era-3 errors: H4 "nearly unattainable" (wrong; K1 baseline fell 1.000 -> 0.547 ->
  0.518 as the ecology grew; CORR C-1) and audit J SUPPORTED (CORR C-2 to SUPPORTED_WITH_DEFECTS).
  [CORR confirmed RULER_QUALITY C-1; C-2 crawler]

STANDING_RULES F1-F8 (roles/Harmonia/STANDING_RULES.md s F, confirmed): F1 reachability first (amended:
evolving-state baselines are part of the attainable set); F2 absence needs a positive control; F3 the
verdict's name is what a shortcut cannot pass; F4 a clause at ceiling is a sanity check; F5 a chance
floor beside every threshold; F6 the freeze is a separate, earlier commit; F7 post-exposure route
changes listed, pre-exposure verdict first; F8 a descent label is not descent, and a descent kill
needs a ruler shown able to PASS on a planted descended positive under the same turnover. Executable
forms exist for F1-F6 only; F7/F8 are reading-level. Each was set on a real defect. [IMPL confirmed]

VACUOUS_READINGS (confirmed) is the right bookkeeping for Phase 3: a vacuous reading "had no power to
separate the alternatives, whatever the truth"; it is never quoted as a null. Rows relevant to
world/ruler insufficiency: V-001 C3-2 H2 (criterion constant by construction: support 1, p_mode 1.0);
V-003 H1 relevance at 3 input bits (8 possible witness inputs; packs cannot differ unless pool >= 2K);
V-005 H5 learned decoder reach at the random-permutation value; V-007 particles claim (c) needs
~11,700 seeds/arm, posed at 50. [IMPL confirmed]

### 2.2 Nyx (mechanism archaeology; hypothesis author)

Built: Chop Shop (6 specimens, preregistered cuts, self-amending KNIFE K1-K10); Atlas (123 fossils);
NYX_PREDICTION_PACKET v1 (nyx/atlas/predictions/schema.py); mechanism ledger (nyx/atlas/mechanisms.py);
calibration ledger (roles/Nyx/calibration/LEDGER.md, 23 wrong calls). [IMPL confirmed]

Packet discipline (confirmed in schema.py): canonical JSON hashed as the freeze; boundary needs a
64-hex file payload hash; interventions need level, direction, numeric magnitude band, band_basis;
cheat and positive controls mandatory (or POSITIVE_CONTROL_UNAVAILABLE with a reason); CUT_KILL and
INDETERMINATE need observation and consequence; corrections are new packets with `supersedes`. The
validator checks FORM only: it checks the hash is 64 characters, not that it matches the bytes.
Binding to bytes is enforced at adjudication by Harmonia (STANDING_RULES B4), which is what caught
deflate.c:667 vs :672. [IMPL confirmed; INFER on enforcement split]

Mechanism ledger (confirmed): "a mechanism without an executable boundary is a name, not a mechanism";
SURVIVED_TRANSPLANT requires a transplant row with a receiving_ecology (the check also accepts an
outcome string "SURVIVED" outside its own vocabulary, line 82). Current ledger: MECH-ASAL-OE-SCORE
EVIDENCE_SUPPORTED + OBSERVER_STABLE (transplant OFFERED only), MECH-PARTICLES-ESS-TRIGGER and
MECH-POET-NOVELTY-ESTIMATOR EVIDENCE_SUPPORTED, four PROPOSED. [IMPL confirmed]

What it could show:
- Controls-first catches hidden machinery: the lean c23 negative control did not fire, revealing the
  eq_self builtin and Nat-literal defeq (LEDGER 2026-09-11). [REPORTED; confirmed ledger row]
- Calibration-pair method: RS_CALIBRATION_PAIR_001 (Rockliff 1991 vs Karn libfec, known identical by
  descent) calibrated Harmonia's equivalence ruler before any surrogate was judged, and found an
  unanticipated 33/2000 corrected-word divergence at e=4. [REPORTED; ledger row confirmed]
- The Ares W4 reading (s0 point 3; s5 G4) is the strongest executed mechanism analysis in the group.

What it could not show:
- Anything about what the atlas organs do. 546/549 are readings; no blind cut, no second Chopper, no
  measured coverage cell. Portability is asserted, not measured. [IMPL confirmed counts]
- Transplant survival: no receiving ecology existed (Vivarium #182: pressures unbuildable; Archaeon
  #200 INTERFACE_INSUFFICIENT). 0 survived is "untested", not "failed". [crawler; ledger confirmed]
- Mechanisms in C/Fortran bodies: M3 had no compiler/docker, so adjudication was selected by host
  runnability (gzip pilot never adjudicated). [crawler; consistent with packets: 003 never ruled]
- Function in an ecology: POET/Avida rows are structural identities on bytes. Harmonia ruled a row the
  author had SEEN on a deterministic payload is a "code fact", predictions_tested 0
  (RULING_MECH_POET_NOVELTY_ESTIMATOR_001_2026-09-30.md:51,63). [IMPL confirmed lines]

### 2.3 Techne (toolsmith -> substrate owner -> self-audit -> fossil vault)

What it could show:
- Modal-collapse null (s0 point 4). V2 SKEWED shows the trap exactly: REINFORCE 26.9% vs random 4.6%
  (5.8x "lift") by collapsing onto 2 bins that hold >50% of y-mass; the lift is real, the learning is
  not. Its own recommendations: compare against the modal-class predictor, not uniform random; add a
  per-input perturbation probe ("if predictions do not change when x changes, the agent is not using
  x"). [REPORTED; confirmed text]
- F2 planted-relation gate: synthetic Murasugi (eq: contrast 0.153; le1: 0.214) and EC torsion
  (0.117) promoted; DECOY_PARITY, DECOY_CODOMAIN, stratified and marginal permutations all < 0.03; one
  seed (20260530), 500 per source, threshold 0.10. Murasugi le3 (codomain-trivial) correctly not
  promoted. Then on the real corpus: v2 "18.5% signal" collapsed to 0/96 under generator a1's uniform
  independent sampling (max contrast 0.023); the residual came from meta-relational generators g4/g5/a3
  whose verdict answers a different predicate than the stored payload (claim-shape category error).
  [REPORTED pivot/calibration_v0, v1, v3_VERDICT, v3c_VERDICT; confirmed text]
- TECHNE-107: through CLIP, 8 unrelated ellipse scenes (GARBAGE 0.8167) score "more open-ended" than
  the living Orbium (0.8472); a translated blob is within 0.026 of the Orbium; the CLIP dynamic range is
  0.058 wide. 6/6 preregistered predictions pass. [REPORTED techne/acquisition/poet_alife/TECHNE107_RESULTS_2026-09-17.md; confirmed text]
- Fossil hash preservation detected 23/57 bodies dirtied by in-place builds while receipts said PASS.
  [crawler]

What it could not show:
- That any search/RL loop can recover a planted target. The withheld benchmark's 0/36 is weaker than
  the dossier says: the partition put only 2/36 withheld entries inside the reward band (1.001<M<1.18),
  so the structural ceiling was 2/36 = 5.6% (the report says so itself). 34/36 were unreachable by
  design. [IMPL/REPORTED prometheus_math/WITHHELD_BENCHMARK_RESULTS.md s1; CORR to the Techne dossier's
  framing "0/36 withheld rediscovered"]
- Lehmer "discovery": F9 returns True unconditionally (discovery_pipeline.py ~272-282); F11 compares
  M(p) with M(reversed p) via the same function, equal for every polynomial (~285-304); a synthetic
  CLEAR verdict is written by SQL (~487-498). The terminal state of a survivor was SHADOW_CATALOG; the
  code never called anything new. [IMPL confirmed]

### 2.4 Hecate (2026-09 triplicate deep search; plus a May namesake in Charon)

Built: preregistered selection; Pass 0-3 generation; control-first probe worlds (positive control,
CHEAT, null twin); Pass 4 attacks (R replication, ORIG = implement the known explanation, ALT
alternative implementation); gravity detector; meta-experiment (5 arms); alien-lawful assay;
novelty autopsy; Wave-2 harnesses (metamorphic evaluator corruption, exact-arithmetic shadow of
decision rules, derived-file reproduction). [IMPL/HIST]

What it could show:
- Behavioural discrimination of lawful vs incompressible systems by an LLM: Family A behavioural AUC
  0.97-1.00, KNOWN 20/20 learned, standard aliens 28/32; labels did NOT discriminate (19/30 nulls
  called RULE, 24/30 COHERENT; 1/100 systems ever called INCOHERENT). [REPORTED hecate/alien/REPORT_pilot.md; confirmed text]
- Coverage vs induction (INV_E; s0 point 5). Also: errors respect planted conservation laws (graph_flow
  62/62 nontrivial wrong predictions conserve the sum vs random 0.12), and active experimentation
  mostly buys coverage. Revealed rules give 1.000 everywhere: the shortfall is knowledge, not
  simulation. [REPORTED; confirmed text]
- A structured non-LLM solver (degree-3 polynomial solve mod 31) cracks all 3 adversarial map systems
  in <1 s where Claude scores 0.025-0.035 (INV_Z8), so "hard, not LLM-specific" was wrong for maps.
  [REPORTED LEDGER Q31; confirmed ledger row]

What it could not show:
- Novelty in either direction. Gravity calibration: 14 controls = 8 disguised knowns, 2 composites, 4
  nonsense; no UNFAMILIAR kind (hecate/gravity/controls_v1.json). Gate PASS = all_calls_ok AND knowns
  >= 7 AND nonsense-called-FAMILIAR <= 1 (run.py:94); a composite counts as a hit if called FAMILIAR or
  COMPOSITE (run.py:82-83), and PASS ignores composites. Detector prompt defines FAMILIAR as "one known
  mechanism, at most renamed or reparameterised" (detector_v1.md). [IMPL confirmed] Autopsy Part B: 0/32
  mechanically alien rules called UNFAMILIAR (nearest priors: "cellular automaton on a graph",
  "register machine", "semi-Thue system"); K6 later found Part B inputs scrubbed (rewrite rules erased).
  [REPORTED hecate/autopsy/AUTOPSY.md; confirmed text]
- Mechanism quality: all 5 SIGNALs reduced to trivial/known explanations (decoding radius, channel
  reset, perturbation response, fixed listener tie, endpoint confound); SIGNALs cluster in the cheapest
  worlds (5/9 valid worlds < 0.05 core-min vs 0/16 above, p=0.012 two-sided), read as "cheap =
  degenerate = sharp thresholds pass by construction". 126/243 mechanisms never got a world; world
  selection predicted by list position (M1-M3 0.83 vs M4+ 0.39), not by form or self-declared
  familiarity. [REPORTED LEDGER Q5, Q10, Q20, INV_N; confirmed text]
- Cross-family replication: gpt-oss 29/100 calls before quota; gemini 10 calls, all truncated, the
  shared JSON extractor accepted inner objects; B/C as designed cannot reach NOT_SUPPORTED (INV_Z4).
  [REPORTED; confirmed text]

### 2.5 Artemis (backlog ecology; prior art; forensic sampling)

What it could show:
- Heredity certification on constructed specimens with known bit content (P-11 panel). P-11 certified
  all four zero-bit painters (pass 0.90-1.00) and rejected four genuine hereditary systems (complement
  child, host-executed guest, two cooperating tapes, budget-limited bytewise copier: a 3-step painter
  passes the one-slice C2 20/20, a 5-step copier 0/20). CVT-2/CVT-R (perturb one parental byte, require
  a consistent offspring difference in generation 1 AND re-transmission in generation 2) accept all 11
  required hereditary specimens, reject all painters, and calibrate exactly (TB: 1-bit painter = 1,
  16-state = 4, painters = 0). Every confusion-table cell equalled the preregistered prediction.
  [REPORTED roles/Artemis/challenge/p11/RESULT.md; IMPL certs.py confirmed: CVT is perturbation-based,
  3 draws, 4 generations, "defined" = same signature in >= 2 of 3 draws]
- On natural donors: only 6/57 P-11 survivors re-pass from a fresh state; 4 of those 6 are single-value
  painters. On Nestor's sets CVT-R accepts 83% of the q1 sample; ~1 in 4-6 "competent" genomes fail,
  mostly at generation 2 (child built but does not carry variation forward). [REPORTED; confirmed text]
- External literature changed interpretations: H-D3-33 "self-signal eviction loses to random" is a known
  result (Isele & Cosgun 2018), and reservoir "random eviction" is distribution matching, a strong
  structured policy, not a null. [REPORTED PA_memory_and_sagacity.md W08/P4; confirmed by grep]

What it could not show:
- Recall of its own prior-art search: about 40 targeted searches (PA_instruments_and_gaming.md:478),
  queries not logged, so "genuinely unexplored" U-lists are search-bounded absence claims. [IMPL confirmed scope note]
- Value of its own curation: the self-test outcome saturated (34/36 executions "consequential"), so a
  0.3 enrichment was undetectable; its priority forecasts were worse than a constant (Brier 0.470 vs
  0.391), so it withdrew them. [REPORTED roles/Artemis/selftest/RESULT.md; confirmed text]

----------------------------------------------------------------------------------------------------

## 3. Results ledger with evidence-profile axes

Axes: Q question could fail; S substrate capacity; W world demand; R ruler validity; B baseline
discrimination; Rep replication (not replay); M mechanism. Y / P / N / U; "-" = not applicable.

| id | historical claim | record status | reclassification | Q | S | W | R | B | Rep | M |
|---|---|---|---|---|---|---|---|---|---|---|
| HA-1 | "battery calibrated on 3.8M objects at 100.000%" | REPORTED, uncorrected | ruler_insufficiency (calibration aimed beside the instrument) + provenance_defect (script uncommitted) | N | - | - | N | N | N | - |
| HA-2 | April "40+ kills, zero novel bridges" | REPORTED NEGATIVE | statistical_insufficiency + ruler_insufficiency + implementation_defect (TT path always UNTESTED) | Y | U | U | N | P | N | N |
| HA-3 | spectral tail 8/8 survivor; rank from zeros 92.1% | never retracted | false_positive likely: implementation_defect (metadata slots read as zeros) + provenance_defect | Y | U | - | N | P | N | N |
| HA-4 | F043 BSD-Sha anticorrelation z=-348 | CORR (external catch) | false_positive (algebraic identity passed the block null) | Y | - | - | N | N | N | - |
| HA-5 | 99.98% of Theseus records self-verdicted at emission | REPORTED | instrument_positive (census) / provenance_defect of the substrate | Y | - | - | P | - | P | - |
| HA-6 | SFE: 48/64 world-blind; coupling survives composition 15/240; 7 usable pairs | REPORTED | instrument_positive; exposes world_insufficiency + organism_insufficiency of the population | Y | P | N | P | P | P | P |
| HA-7 | C3-2 H2 / H1 at 3 bits / H5 reach (V-001, V-003, V-005) | VACUOUS | world_insufficiency + ruler_insufficiency (could not answer either way) | N | U | N | N | P | N | N |
| HA-8 | Tyche H1/H6 unreachable; Harmonia H4 rating | CORR C-1 on H4 | instrument_positive (reachability) + auditor false_positive corrected | Y | - | - | P | - | N | - |
| HA-9 | grading oracle "non-gameable" | CORR (self-attack, ~6 weeks) | implementation_defect (answer key in R6 probe) | Y | - | - | N | N | - | - |
| NY-1 | atlas: 549 organs, 485 accepted | descriptive | not a test; ruler_insufficiency (labelling never validated) | N | U | - | N | N | N | N |
| NY-2 | mechanisms survived transplant: 0 | scoreboard | untested: world_insufficiency (no receiving ecology) | N | U | U | - | - | N | N |
| NY-3 | RS calibration pair CUT_SUPPORTED | REPORTED | instrument_positive (equivalence ruler calibrated; unanticipated divergence found) | Y | Y | - | P | P | N | - |
| NY-4 | particles ESS trigger 001 INDETERMINATE; 002 boundary CUT_SUPPORTED; (c) failed@50 | MIXED | 001: ruler_insufficiency (PC band from "a picture"); 002: instrument_positive on exact rows; (c): statistical_insufficiency | Y | Y | P | P | P | N | P |
| NY-5 | ASAL legit search 001 (I1/I2 by witness; I3 on 395/1045) | MIXED | survives_as_anomaly (exploitable metric within Lenia parameters) with ruler_insufficiency (class rule from one rollout) and executor-domain insufficiency (650 refused) | Y | Y | - | P | P | P | N |
| NY-6 | POET novelty estimator 4/4 CUT_SUPPORTED | ruled code fact | not a test (seen deterministic rows); predictions_tested 0 | N | Y | - | - | - | N | P |
| NY-7 | gzip level-table pilot | never adjudicated | search_insufficiency (no execution route on host) + provenance save (line 667 vs 672) | Y | U | - | - | - | N | N |
| NY-8 | Ares W4 carrier = saturating positive-feedback 1-bit latch, 10/10 lineages; fails W16 | REPORTED (non-adjudicative reading) | instrument_positive (mechanism located by lesion + sufficiency); world_insufficiency for any general-memory claim | Y | Y | P | P | P | P | Y |
| TE-1 | six-domain RL lifts 1.37x-18x | CORR (retracted, not propagated) | false_positive: organism_insufficiency + pressure_insufficiency (sparse 0/1, episode length 1); baseline was uniform, not modal | Y | P | P | N | N | N | N |
| TE-2 | modal-collapse synthetic null: Case A | REPORTED | instrument_positive (world learnable by authority; organisms at chance) | Y | P | Y | Y | Y | P | N |
| TE-3 | withheld benchmark 0/36 | REPORTED NEGATIVE | search_insufficiency + world/ruler ceiling (2/36 reachable); not a true_negative | P | U | P | P | N | P | N |
| TE-4 | F2 calibration: planted relations recovered, decoys rejected | REPORTED | instrument_positive (narrow: 2 families, 1 seed) | Y | - | - | Y | Y | P | - |
| TE-5 | Theseus corpus cross-catalog signal (18.5% groups) | CORR | false_positive (selection bias + predicate category error) | Y | - | - | P | Y | P | - |
| TE-6 | Theseus 2,351 promoted | CORR | false_positive (shape-only gate; formula fossil) | Y | - | - | N | N | N | - |
| TE-7 | Lehmer pipeline F1/F6/F9/F11 survivors; deg-14 lemma | MIXED / CORR | ruler_insufficiency + implementation_defect (F9 vacuous, F11 tautology, CLEAR by SQL; repeated-root verifier FN) | P | - | - | N | P | N | - |
| TE-8 | TECHNE-107: garbage scores more open-ended than Lenia | REPORTED POSITIVE | instrument_positive (metric pathology of the ASAL OE score) | Y | Y | - | Y | Y | P | - |
| HE-1 | 16 programs, 5 SIGNALs, 0 survive Pass 4 | REPORTED | SIGNALs: false_positive (pass by construction / trivial); NULLs: world_insufficiency + search_insufficiency + ruler_insufficiency; not hypothesis_failure | P | U | N | N | P | P | P |
| HE-2 | meta v1 "zero UNFAMILIAR in any arm" | CORR | ruler_insufficiency (no UNFAMILIAR positive control; unreachable by definition) | N | - | - | N | N | N | - |
| HE-3 | autopsy R1: 0/32 alien rules UNFAMILIAR | CORR (K6) | instrument_positive for the detector's ceiling; partial implementation_defect (scrubbed inputs) | Y | - | - | P | P | N | - |
| HE-4 | Pass-3 v2 control-first generator: 0/8 instrument failures | REPORTED + INV_J | instrument_positive (attainability) + ruler_insufficiency (discrimination vs simpler alternative) | Y | - | P | P | N | N | - |
| HE-5 | alien assay Family A; detector NOT_VALIDATED | MIXED | instrument_positive (behavioural); ruler_insufficiency (labels; construct passable by lookup); induction mostly coverage; statistical_insufficiency for B/C | Y | Y | P | P | Y | N | P |
| HE-6 | "affine (0.44) beats Claude (0.33)" | CORR K2 | false_positive (mismatched subsets/metrics) | Y | - | - | - | - | - | - |
| HE-7 | Charon-Hecate MI z=946 "emergent operator structure" | CORR | false_positive (generator prefix in the label) | Y | - | - | N | P | - | - |
| AR-1 | P-11 unsound for heredity; CVT-2/CVT-R adequate | REPORTED | instrument_positive (constructed specimen panel) | Y | Y | - | Y | P | P | Y |
| AR-2 | CVT-R on Nestor sets: 83% heritable, ~1/4-1/6 not | REPORTED | instrument applied; partial true_negative on non-heritable competents | Y | Y | - | P | - | N | Y |
| AR-3 | self-test: sharpening adds no detectable yield; Brier worse than constant | REPORTED | ruler_insufficiency (saturated outcome) for yield; true_negative for forecast skill (n=19) | P | - | - | N | Y | N | - |
| AR-4 | H-D3-33 is a known result; random eviction is not a null | REPORTED | hypothesis_failure (novelty) + ruler_insufficiency (invalid null) for the owning seat | Y | - | - | - | - | N | - |

Notes on axis calls (where non-obvious):
- HA-6 S=P: 16/64 specimens are world-coupled (constructive existence in-population); M=P: exact
  ablations (A+B\B) showed B executed in 0/6 of the first subset, later corrected by a broad sample.
- NY-8 M=Y: cutting every recurrent edge floors 10/10 lineages (0.50-5.50 of cap 40); the minimal
  circuit alone (output self-loop, 2 edges) reaches the cap; synthetic drive maps ignition and reset
  thresholds. No transplant into a different body. Rep=P: 10 independent evolutionary lineages, one
  reader and one instrument. W=P: the world demanded a bit held ~37 steps, but only from a fixed cue
  window at reset, so a set-once latch suffices.
- TE-2 S=P: the authority shows the WORLD contains a learnable map; the ORGANISMS were shown unable
  to learn it under this pressure (that is the finding). Rep=P: 3 seeds, one host.
- AR-1 Rep=P: E0 (VM equivalence across two commits) and E1 (determinism) are replays; the panel was
  built once by one author. M=Y: the certificate is itself an intervention (perturb parent, observe
  re-transmission).

----------------------------------------------------------------------------------------------------

## 4. Instruments with demonstrated detectability (and the limit of each demonstration)

| instrument | what it detects | demonstration | limit |
|---|---|---|---|
| Techne modal-collapse synthetic null (prometheus_math/modal_collapse_synthetic.py) | class-prior recovery masquerading as learning; organism failure on a learnable world | lstsq authority >= 60% on V3; REINFORCE/PPO at chance; V2 reproduces the 5.8x false lift | linear tasks only; 3 seeds; episode length 1 |
| F2 planted-relation contrast gate (theseus/scoring/content_aware_promote.py) | real catalog coupling vs codomain/parity artifacts | Murasugi eq/le1 and EC torsion promoted; 0/8 decoys and permutations | 2 families, 1 seed, 500/source; needs predicate_kind guard |
| a1 uniform independent sampler as null (theseus/generators/a1_catalog_cross_product.py) | generator selection bias in corpora | 61/96 -> 0/96 promoted when restricted to a1 | requires a generator that samples independently by construction |
| Artemis CVT-2 / CVT-R (roles/Artemis/challenge/p11/certs.py) | heritable variation (copying) vs painting | 17-specimen panel, exact TB calibration 0/1/4 bits | z8 + toy ISA; author-built panel; pair assay at copy rate 0 |
| Hecate INV_E coverage oracle + induction index (roles/Hecate/harvest_w2/INV_E_induction_vs_coverage.py) | induction of unseen entries vs coverage/default | poly_sym II +0.95 vs pooled tables II_ocd -0.08 | 1-8 systems per family; analysis snippets uncommitted |
| Hecate alien assay behavioural score (hecate/alien/score.py) | lawful vs incompressible structure via prediction | KNOWN 20/20; behavioural AUC 0.97-1.00 | one subject family; label outputs non-discriminating |
| Hecate metamorphic harness (hecate/metamorphic/harness.py) | evaluators insensitive to corrupted inputs | found 47f4/W1 empty-all() pass; 32/42 accept copied seeds | toy worlds |
| Hecate exact shadow evaluator (hecate/alien/shadow_decisions.py) | float/edge-case divergence of preregistered decision rules | found H3 0.2-0.1 = 0.0999 defect; 62 tests | decision rules only |
| Harmonia emission-path census (harmonia/diagnostics/detector_band_audit.py) | who issued the verdict | 99.98% self-verdict; positive a1 and cheat a3 controls [crawler] | Theseus-specific |
| Harmonia execution-vs-image differential (boundary-depth L3/L4) | whether a component executed vs merely sits in memory | agreed with Proteus op-category differential 6/6 | SFE VM only |
| TECHNE-107 arm battery (techne/scripts/techne107_asal_observer.py) | metric pathology of an open-endedness score | garbage < life; drift ~ life; static = (T-1)/T exactly | one pattern, one world size |
| RS calibration pair (nyx/atlas/calibration/RS_CALIBRATION_PAIR_001.json) | equivalence-ruler validity before judging surrogates | known-identical pair + self-pairs + mismap; 2000 trials per error count | used once |
| Nyx per-SCC latch test (nyx/readings/ares_w4_reading.py) | carrier loops vs bystander loops in evolved networks | separates carrier SCCs in 10 lineages; node ablation misses them | Ares substrate; non-adjudicative |
| AP-1.1.0 freeze_precedes (audit_primitives.py) | plan committed together with results | flags the real Ananke W-O plan from git | uses the plan's FIRST add only |
| Fossil hash preservation (techne/fossils/harvest.py) | dirtied or mis-hashed bodies | 23/57 dirty bodies; 11 CRLF records [crawler] | packet validator is form-only |

Instruments shown unable to fire or cosmetic in this group (confirmed unless marked):
gravity-detector gate (no UNFAMILIAR item; composites cannot fail); NOVELTY_DETECTOR_VALIDATED rule
(passed by lookup-table baselines localtab_t2_comp 0.844/0.721/0.800 and localtab_eval_exact
0.852/0.747/0.817); AP-1.1.0 ablation leg (forced flag=False); F9 and F11 in the Lehmer pipeline; the
validate.py battery hook (always UNTESTED); Nyx packet validator (form-only hash check); FOSSIL_PACKET
validator (accepts fabricated hashes) [crawler]; ASAL CLIP open-endedness score as a ruler of life.

----------------------------------------------------------------------------------------------------

## 5. Most informative experimental geometries (what Phase 3 can learn from)

G1. Learnable-world authority beside the organism (modal-collapse null). Certify the world with a
    non-organism solver (lstsq) before reading the organism. This alone separates
    organism_insufficiency from world_insufficiency. Add a modal-class (not uniform) baseline and an
    input-perturbation probe. [prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md]

G2. Matched LAW/ARB coverage-controlled pairs (DESIGN_P). Same architecture (ring of 6 sites, Z_7,
    one shared 7x7 table), same revealed key set (25/49 or 37/49), ARB unseen values a
    histogram-matched shuffle of LAW's, so every pure-coverage, mode or default learner ties exactly;
    a SHADOW rescoring is a leak control; power 0.98 at 48 untied pairs. Only an inducer of the hidden
    law separates the arms. Never run. [roles/Hecate/harvest_w2/DESIGN_P_coverage_controlled_family.md]

G3. Set world vs transfer world (Ares W4 vs W16). W4: cue at steps 0-2; W16: cue window anywhere in
    [0,20], reward in the last 10 steps. The prediction (champions near floor because each loop reaches
    its default clip state within 10 steps and a +-1 cue cannot flip a saturated loop) was written
    before the run and held 10/10. This is a trajectory-and-world-demand test in miniature: it shows
    what the world did NOT demand. [roles/Nyx/reports/ARES_W4_READING_2026-09-25.md s7]

G4. Lesion + sufficiency + synthetic drive on evolved bytes (Ares W4). SCC inventory; cut every
    recurrent edge (floors 10/10); strip all non-carrier hidden nodes (cap kept 8/10); reduce to a
    2-edge self-loop (cap); sweep loop gain (viable for scale >= 0.8, gain up to 106: wide flat basin,
    vs the designed `keep` primitive's 4%-wide sliver); map ignition (cue <= -0.5) and reset (+r >= 3)
    thresholds. Instrument note: node ablation never removes output nodes and "signature by ops" reads
    identities, so both miss this mechanism class (8/10 loops run through an output node).

G5. Constructed specimen panel with known heritable bit content (P-11/CVT). Zero-bit painters
    (homopolymer, periodic, closed), 1-bit and 4-bit painter positives, block/bytewise/budget-limited
    copiers, complement child, host-executed guest, two-tape cooperation, hash scrambler (stress),
    counter copier. Every certificate is run on all specimens before it touches natural data.

G6. World-dependence census on the composed object (SFE boundary depth). Vary one factor at a time
    (input, seed, budget); a specimen invariant to all inputs is world-blind; measure the precondition
    on the composite, never inherit it from parts; report EXECUTION and IMAGE observables separately
    (state was the most sensitive surface, 14/16 vs meter 11/16 vs transcript 2/16).

G7. Garbage/static/noise/drift/hue arms for any novelty or open-endedness score (TECHNE-107), and the
    analytic "find the world that maximises the metric" check (Artemis PA_instruments P7: for ASAL
    novelty it is turbulence; for shape-keyed novelty it is op-duplication).

G8. Simple-alternative arm before freeze (Hecate LEDGER Q6, INV_J s5). The spec's own named simpler
    explanation is built as an arm and the world freezes only if it fails at least one success clause;
    the positive control must pass through the same censoring/saturation path as the treatment.

G9. Calibration pair (RS): known-identical-by-descent pair plus known-different-same-label pair, run
    before any equivalence or recurrence ruler judges anything.

G10. Hash-bound frozen packet with CUT_KILL and INDETERMINATE as preregistered losing outcomes, author
    barred from adjudicating, seen rows declared, existential vs extremal rows labelled (A6), executor
    domain acceptance before freeze (A4), measure definedness on synthetic fixtures before the hash
    (A5), power statement or descriptive estimate only (A2).

----------------------------------------------------------------------------------------------------

## 6. Failure shapes recurring in this group

| class | direction | instance | cite |
|---|---|---|---|
| world_insufficiency | FN (and FP for any "interaction" reading) | 75% of SFE specimens world-blind; composition destroys coupling | roles/Harmonia/BOUNDARY_DEPTH_PACKET_01_2026-09-05.txt |
| world_insufficiency | FN for general memory | Ares W4 fixed cue window lets a reset-timed latch reach the cap; W16 exposes it | roles/Nyx/reports/ARES_W4_READING_2026-09-25.md s5, s7 |
| world_insufficiency | FN | 3-bit task: relevance untestable at any n (V-003); C3-2 criterion constant (V-001) | roles/Harmonia/VACUOUS_READINGS.md |
| world_insufficiency / ruler | FN | withheld benchmark: 34/36 targets outside the reward band | prometheus_math/WITHHELD_BENCHMARK_RESULTS.md s1 |
| world_insufficiency | FN/FP | Hecate signals only in near-deterministic cheap worlds; e106 W6 NULL by construction | roles/Hecate/harvest_w2/INV_N_cheap_world_signals.md; INV_J |
| organism_insufficiency | FN | REINFORCE/PPO cannot learn a linear map lstsq solves | MODAL_COLLAPSE_SYNTHETIC_RESULTS.md |
| pressure_insufficiency | FP | sparse 0/100 reward, episode length 1 produces modal collapse read as transfer | same |
| ruler_insufficiency (absence without positive control) | FN | "zero UNFAMILIAR"; unreachable by definition | hecate/gravity/controls_v1.json; AUTOPSY.md C6 |
| ruler_insufficiency (construct passable by shortcut) | FP | lookup table passes NOVELTY_DETECTOR_VALIDATED | RULER_QUALITY_2026-09-30.md s2 |
| ruler_insufficiency (attainable but non-discriminating) | FP | control-first worlds pass the PC check but the simpler alternative also passes | INV_J s5 |
| ruler_insufficiency (metric pathology) | FP | ASAL OE score ranks garbage above life | TECHNE107_RESULTS_2026-09-17.md |
| ruler_insufficiency (ceiling/saturation) | FN | self-test outcome 34/36; Odysseus quality 10.0 vs 9.1 | selftest/RESULT.md; EVIDENCE_AUDIT D |
| ruler_insufficiency (calibration beside the instrument) | FP | 3.8M "calibration" never runs the battery | Harmonia dossier s0 [crawler] |
| ruler_insufficiency (unreachable gate) | FN | Tyche H1/H6 PASS fixed impossible by initial population | RULER_QUALITY s1 |
| implementation_defect (wrong-signature call) | FN | validate.py battery hook always UNTESTED | harmonia/src/validate.py:220 |
| implementation_defect (tautological check) | FP | F11 compares M(p) with M(reversed p); F9 always True | prometheus_math/discovery_pipeline.py |
| implementation_defect (control cannot fail) | FP | AP ablation forced flag=False; empty all() cheat (Nyx P-a5, Hecate 47f4/W1); "V == 0.0" on float variance | audit_primitives.py:161-165; roles/Nyx/calibration/LEDGER.md |
| implementation_defect (lesion blind spot) | FN | Ares node ablation never removes output nodes; hid one third of the ring | ARES_W4_READING s0, s9 |
| implementation_defect (input damage) | FN | scrubber erased rewrite rules ("YZ -> XW" -> "[X] -> [X]") | LEDGER Q13 |
| search_insufficiency (selection frame) | FN | 126/243 mechanisms never in a world; list position predicts selection; host runnability decides which fossils get verdicts | LEDGER Q10; Nyx dossier s21 |
| search_insufficiency (executor domain) | FN | ASAL port refused 650/1,045 draws after freeze | STANDING_RULES A4 |
| statistical_insufficiency | FN | particles (c) needs ~11,700 seeds/arm, posed at 50; alien B/C cannot reach NOT_SUPPORTED | VACUOUS_READINGS V-007; LEDGER Q30 |
| false_positive (label leakage) | FP | MI(kill_pattern, generator_id) z=946 with generator-prefixed labels; F2 predicate category error | Hecate dossier s16; calibration_v3c |
| false_positive (selection bias) | FP | mutation inheritance (~91% of v2 groups) | calibration_v3_VERDICT |
| false_positive (convention as threshold) | FP | ASAL I0 crossed a 5-seed estimated mean (margin 1.1 sd) | roles/Nyx/calibration/LEDGER.md 2026-09-18 |
| provenance_defect | FP persistence | spectral_bsd never retracted; 14 stale Hecate prose claims after corrections; six-domain lifts still headlined | crawler; LEDGER Q26 |
| provenance_defect (identity of observer) | FP of independence | "observer stable" = same CLIP weights in torch vs Flax (4.8e-7 agreement); ledger records OBSERVER_STABLE | RECORD_HARM55_HARM56_NATIVE_OBSERVER_2026-09-30.md:46; MECHANISMS.json |
| auditor false_positive | both | Harmonia H4 rating wrong (evolving baseline); audit J overturned; Hecate corrections biased toward Hecate (REDTEAM_Y) | RULER_QUALITY C-1; LEDGER Q27 |
| true_negative (narrow) | - | F2 on a1 direct records: no knot x EC coupling (sub_hold = null everywhere) | calibration_v3_VERDICT |

Dominant pattern in this group: positives died because the measurement or the world carried the
answer (cheap worlds passing by construction, label prefixes, transcribed fixtures, garbage scoring as
life); negatives were mostly uninformative because the world or ruler could not have produced the
positive (world-blind organisms, unreachable classes, 2/36 reachable targets, constant criteria).
[INFER from the table]

----------------------------------------------------------------------------------------------------

## 7. Design implications for Phase 3 (each tied to evidence)

D1. Certify world demand before studying the organism. Require, per world: (a) an ablated-capability
    baseline organism (e.g. no recurrence, no memory) that must FAIL; (b) a world-dependence census on
    the actual (composed) organism. Evidence: 48/64 SFE specimens world-blind; Ares W4 was solvable by a
    set-once latch timed by reset; cutting recurrence floors all ten W4 champions (so W4 does demand
    a latch, but only that).
D2. Pair every "acquisition" world with a transfer world that moves the demand (cue timing, table
    entries, coordinates), with the outcome predicted before running. Evidence: W4/W16 10/10; INV_Z8
    (linear change of coordinates defeats an LLM, not a structured solver).
D3. Certify world learnability with a non-organism authority, and use modal-class and lookup
    baselines rather than uniform random. Evidence: modal-collapse V2 5.8x false lift; six-domain RL
    retracted.
D4. Rulers for "reasoning machinery" must separate induction from coverage/lookup. Adopt coverage
    oracles and matched LAW/ARB families with histogram-matched unseen entries. Evidence: INV_E
    (tables II_ocd -0.08 vs parametric laws +0.95); DESIGN_P.
D5. Every verdict name must be one a shortcut cannot pass; run the frozen rule on lookup, mode,
    constant and simpler-alternative baselines before freeze. Evidence: lookup table passes
    NOVELTY_DETECTOR_VALIDATED; both Hecate round-3 SIGNALs met by the named simpler alternative.
D6. Absence claims require a calibration item of the absent class on which the ruler fired, and the
    class must be reachable by construction. Evidence: gravity detector UNFAMILIAR unreachable
    (definition + no control); withheld benchmark 2/36 reachable.
D7. Reachability must be enumerated over evolving state, not t=0. Evidence: Harmonia's own H4 error
    (K1 baseline 1.000 -> 0.547 -> 0.518).
D8. Mechanism claims need executed lesion AND sufficiency (minimal circuit restores function) AND a
    transfer or transplant into a receiving body/world; readings carry no evidential weight. Lesion
    instruments must be shown able to remove every node class. Evidence: Nyx atlas 546/549 readings;
    Ares W4 template; node ablation blind to output nodes; lesion rescue in evolved substrates (126/345
    ablated still replicate, cited in Artemis PA P8).
D9. Replication means new evolutionary/learning seeds or independent reimplementation; a deterministic
    replay or a byte-identical port is attestation, and a seen deterministic row is a code fact.
    Evidence: QR-REPLAY; POET ruling; HARM-56 same weights.
D10. Heredity/descent rulers: constructed specimen panels with known bit content, plus
    perturb-and-retransmit certificates, plus (F8) a planted descended positive under the same
    turnover regime before a descent kill counts. Evidence: P-11 certified four zero-bit painters;
    E-BEL-REPL-01 founder-snapshot ruler could not pass.
D11. Novelty/open-endedness scores must beat garbage, static, noise, drift and extremal-maximiser
    arms before use. Evidence: TECHNE-107.
D12. Freeze discipline that is mechanically checkable: plan committed strictly before results;
    hash-bound packets; executor-domain acceptance (650/1,045 refused after freeze); definedness on
    first/last boundary fixtures (Avida I7 caught pre-hash); power statements for stochastic rows
    (particles (c)). Evidence: STANDING_RULES A1-A8, B1-B10, F6; Nyx LEDGER rows.
D13. Auditors and certifiers need sealed planted-defect calibration and controls that can fail.
    Evidence: AP ablation forced; no planted defect in any Harmonia audit; Hecate corrections biased
    toward the corrector.
D14. If LLMs are organisms or judges, include cross-family subjects and non-LLM structured solvers,
    budgeted so the arms complete. Evidence: alien B/C died on quota; INV_Z8 polynomial solver.
D15. Selection frames must be explicit and randomised: shuffle candidate order, record the eligible /
    observed / judged denominators, and do not let host runnability or cost pick what gets tested.
    Evidence: list-position effect (0.83 vs 0.39); M3 Python-only adjudication; cheapest-world signals.
D16. Corrections must propagate to every citing artifact in the same change. Evidence: 14 stale Hecate
    claims (K15); six-domain lifts and spectral_bsd at HEAD.

----------------------------------------------------------------------------------------------------

## 8. Crawler claims I checked

Confirmed in the artifact:
- Nyx 546/549 read-only organs; 0/10,431 measured coverage cells; portability YES 533; all ANCESTRY_AWARE
  (parsed nyx/atlas/fossils/*.json). Ledger 7 mechanisms, 0 SURVIVED_TRANSPLANT (MECHANISMS.json).
- validate.py battery call raises TypeError -> UNTESTED (validate.py:220-223 vs battery_unified.py:196).
- F9 vacuous, F11 tautological, CLEAR written by SQL (discovery_pipeline.py).
- Gravity gate structure and missing UNFAMILIAR control (controls_v1.json; run.py:80-94).
- AP-1.1.0 tautological ablation (`chk`, audit_primitives.py:161-165).
- 99.98% self-verdict figure (AUDIT_20260819_detector_band.md:137).
- Probe-round failure counts 6/16 -> 6/13 -> 0/8 (PROBE_ROUND reports).
- F2 single-seed planted calibration (calibration_v0, v1).

Corrected or sharpened:
- Techne "0/36 withheld rediscovered" omits the stated ceiling: only 2/36 withheld entries lay in the
  reward band. Read as world/ruler ceiling plus search insufficiency, not as a measured inability.
- "Control-first world generator cut instrument failures to 0/8" is true for attainability only; INV_J
  shows 5/16 PASSES_BY_CONSTRUCTION, 3 NON_DISCRIMINATING, 3 GOODHARTED, and both round-3 SIGNALs fall
  to the simpler alternative.
- AP-1.1.0 fixtures are real defects but transcribed as constants, not recomputed.
- MECH-ASAL-OE-SCORE carries OBSERVER_STABLE in the ledger, while Harmonia's record states HARM-56
  "says nothing new about whether the crossings are open-endedness" (same CLIP weights, 4.8e-7).
- The Ares W4 reading (only briefly mentioned in the Nyx dossier) is the strongest executed mechanism
  analysis in this group and the only one that tests world demand by transfer.

Not verified by me (crawler-only): 3.8M calibration content; zeros_vector line 45; F12-F14 row-order
dependence; FOSSIL_PACKET fabricated-hash probe; CRLF PAYLOAD_MANIFEST_ID recomputation; Harmonia
qualification t-quantile defects; grading-oracle R6 leak.

----------------------------------------------------------------------------------------------------

## 9. Open questions for the architect

1. Can an evolved organism develop a cue detector (ignition from rest) when the world moves the cue
   (W16-class), and what is the developmental trajectory from set-once latch to detector? No W16
   lineage evidence was found. [UNK]
2. Would DESIGN_P (matched LAW/ARB) show entry-level induction in any organism, LLM or evolved? Never run. [UNK]
3. Does F2's recall survive more planted families, seeds and effect sizes (a completeness curve)? [UNK]
4. What is the false-negative rate of Harmonia's re-execution audit on sealed planted defects? [UNK]
5. Would a non-Claude detector or subject also give zero UNFAMILIAR / the same over-attribution? [UNK]
6. Does the SFE world-blindness finding generalise to other substrates in the program (Archaeon,
   Vivarium, NPE)? Only the SFE menagerie was censused in what I read. [UNK]
7. Avida ancestry packet (frozen blind 09-30) verdict pending. [UNK]
8. INV_E analysis snippets an1..an5 were not committed; are its table-level numbers reproducible from
   the committed script alone? [UNK]

----------------------------------------------------------------------------------------------------

## 10. Files opened

docs/phase3/intake/tityos/REPORT.md; docs/phase3/intake/tityos/failure_taxonomy.md (lines 1-200);
docs/phase3/intake/tityos/seats/{Harmonia,Nyx,Techne,Hecate,Artemis}.md;
roles/Harmonia/STANDING_RULES.md; roles/Harmonia/VACUOUS_READINGS.md;
roles/Harmonia/audits/RULER_QUALITY_2026-09-30.md; roles/Harmonia/audits/EVIDENCE_AUDIT_2026-09-30.md;
roles/Harmonia/qualification/primitives/audit_primitives.py; .../tests/test_audit_primitives.py;
roles/Harmonia/BOUNDARY_DEPTH_PACKET_01_2026-09-05.txt; roles/Harmonia/AUDIT_20260819_detector_band.md (grep);
roles/Harmonia/rulings/RECORD_HARM55_HARM56_NATIVE_OBSERVER_2026-09-30.md (partial);
roles/Harmonia/rulings/RULING_MECH_POET_NOVELTY_ESTIMATOR_001_2026-09-30.md (grep);
harmonia/src/validate.py (214-226); cartography/shared/scripts/battery_unified.py (grep);
nyx/atlas/fossils/*.json (parsed); nyx/atlas/gates/MECHANISMS.json (parsed); nyx/atlas/predictions/schema.py;
nyx/atlas/predictions/MECH-*.json (parsed); nyx/atlas/mechanisms.py; nyx/atlas/ATLAS_STAGE_A_REVIEW_2026-09-16.md (1-60);
roles/Nyx/calibration/LEDGER.md; roles/Nyx/reports/ARES_W4_READING_2026-09-25.md;
prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md; prometheus_math/modal_collapse_synthetic.py (grep);
prometheus_math/WITHHELD_BENCHMARK_RESULTS.md; prometheus_math/discovery_pipeline.py (255-306, grep);
pivot/calibration_v0_murasugi_2026-05-30.md; pivot/calibration_v1_ec_torsion_2026-05-30.md;
pivot/calibration_v3_VERDICT_2026-06-03.md; pivot/calibration_v3c_VERDICT_generator_category_error_2026-06-03.md;
techne/acquisition/poet_alife/TECHNE107_RESULTS_2026-09-17.md;
hecate/gravity/detector_v1.md; hecate/gravity/run.py (80-109); hecate/gravity/controls_v1.json (parsed);
hecate/autopsy/AUTOPSY.md; hecate/alien/REPORT_pilot.md; hecate/programs/PROBE_ROUND{1,2,3}_REPORT.json (parsed);
roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md; roles/Hecate/harvest_w2/LEDGER.md;
roles/Hecate/harvest_w2/INV_E_induction_vs_coverage.md; roles/Hecate/harvest_w2/INV_J_v2_clause_reachability.md (grep + summary);
roles/Hecate/harvest_w2/INV_N_cheap_world_signals.md (grep); roles/Hecate/harvest_w2/DESIGN_P_coverage_controlled_family.md (1-60);
roles/Artemis/challenge/p11/RESULT.md; roles/Artemis/challenge/p11/certs.py; roles/Artemis/challenge/cvtr_nestor/RESULT.md;
roles/Artemis/selftest/RESULT.md; roles/Artemis/backlog/prior_art/PA_instruments_and_gaming.md (401-530, grep);
roles/Artemis/backlog/prior_art/PA_memory_and_sagacity.md (grep); roles/Artemis/backlog/prior_art/PA_origin_of_replication.md (grep).
