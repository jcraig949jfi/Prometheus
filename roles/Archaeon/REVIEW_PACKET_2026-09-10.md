================================================================================
PROMETHEUS / SFE — EXTERNAL REVIEW PACKET
Where the ecosystem stands, what has been tested, what it has found, and what
should happen next.  Prepared by Archaeon (coordinator seat), 2026-09-10.
================================================================================
Baseline for every statement: origin/main a15e12ffe (2026-09-10) plus the
branch commits named inline. Every claim below is traceable to a committed
receipt, ruling, or a live measurement taken 2026-09-10 and quoted with its
denominator. Nothing here is inferred from a plan. Where a seat's work is on a
branch and not on main, the packet says so.

--------------------------------------------------------------------------------
0. ONE-PARAGRAPH SUMMARY
--------------------------------------------------------------------------------
In four days (2026-09-06 to 09-10) the program went from one qualified world
and a producer that could not read the engine to: a live autonomous loop
(producer -> queue -> executor -> engine -> evidence wiki) completing real
experiments; a roadmap for four diversity branches with kill conditions and
attainable ranges; three new executable substrates as pure libraries (radius-3
cellular automaton, streaming CA, radius-1 elementary CA) and one wrapped as a
runnable kind; a Boolean program substrate verified exhaustively against an
independent oracle; an artifact-consuming execution path proven on a
development engine with ten ordered rejection conditions; executable
qualification rules with six adversarial fixtures; four external tools pinned
by hash with one published result reproduced at zero tolerance; and a detector
calibration corrected twice by measurement. NOTHING SCIENTIFIC HAS BEEN
CLAIMED. Every experiment run so far is a plumbing check, an instrument
calibration, or a corpus acquisition, and each is labelled as such. Two
findings changed the plan rather than confirmed it: the intended first
detector cannot resolve the contrast the first campaign plants, and the
intended first streaming-CA configuration is provably inert. Both were caught
before any result was read.

--------------------------------------------------------------------------------
1. THE PROGRAM SHAPE, IN ONE PLACE
--------------------------------------------------------------------------------
Seats and what each owns (charters verified 2026-09-06):
  Daedalus   the engine (SFE): worlds, work, artifacts, budgets, seals
  Vivarium   the executor: queue, kinds, blind execution, PEW publication
  Archaeon   the producer/scientist: templates, detectors, campaigns, analyses
  Harmonia   design and adjudication: nulls, controls, units, what evidence licenses
  Herakles   historical specimens and CA libraries; literature verification
  Proteus    program organisms: VM semantics, identity, Boolean substrate
  Mnemosyne  the evidence wiki (PEW): references, indexes, provenance
  Techne     tools: acquisition, pinning, reproduction, in isolation
  Operator   admissions, policy values, deployment, credentials, design forks

Doctrine that every receipt below obeys: the sealed spec carries exactly the
execution inputs and nothing else; the executor is blind and defaults nothing;
provenance and design labels live outside the execution hash; PEW references
and never copies; no LLM sits in any decision or adjudication path; admission
of a template or kind is a human act; completion of an implementation is a
separate axis from qualification of a conclusion.

--------------------------------------------------------------------------------
2. EXPERIMENTAL STATE OF THE ECOSYSTEM (measured 2026-09-10)
--------------------------------------------------------------------------------
ENGINE (SFE, M1 at 192.168.1.202:8811)
  production schema 7 (live since 2026-09-06, source f1e36c062); 562 worlds and
  35,440 events preserved through the v7 migration; read scopes and family-
  member arm seals exist; measurements registered for evaluate_bitstring.
  schema 8 exists on a DEVELOPMENT engine only (ef05397f2): read-path digest
  gate, 16 MiB artifact limit, reservation phase. NOT deployed; review record
  deploy/CANDIDATE_BUILD.json.
  Read grant to Archaeon's client: NONE. The corpus owner's (harmonia-m2,
  cli_11ec5935..., 189 worlds) token is not persisted anywhere reachable and
  v7 has no reissue route. Archaeon reads the ledger file directly (declared
  tenancy, one transaction, schema guard) until a grant exists.

QUEUE AND EXECUTOR (Vivarium)
  research_experiment_queue: 26 completed, 5 failed, 324 cancelled (cancelled =
  candidate-set alternatives, by design). Consumer running (worker vivarium@m1,
  PID 3268, started 2026-09-08). Kinds live on main: noop_v0, evaluate_bitstring,
  random_walk_v0. On branches: artifact_probe_v1 (loader fixture kind,
  959d35043), ca_density_v0 (wraps Herakles's library; six genomes reproduce
  golden exactly; e43a6c7f2), result_schema on every kind (295482d4e).

PRODUCER (Archaeon)
  ArchaeonTick registered 2026-09-08 04:57, every 15 min, prod lane, 6/day
  quota, 4 h separation; 102 cadence decisions/day; 11 experiments completed
  since registration, all bitstring.uniform.v0 (the frozen random baseline);
  each published to PEW (production encounter count 5458 -> 5469). Reader
  accepts schema 7; sees 2,949 attested observations from declared clients
  across 93 worlds (harmonia-m2 and vivarium tenancy), aggregated to one row
  per independent unit before any detector runs.

EVIDENCE WIKI (PEW, Mnemosyne)
  schema migration 011: typed references (six kinds), a required five-state
  availability enum, an append-only availability-events log, a publication
  outbox keyed by publication intent (retries never duplicate science),
  evidence rows carrying software stage / connection evidence / scientific
  outcome / reproduction state as four separate vocabulary-checked fields.
  Index rebuilt twice from references alone with a stable digest.

DETECTORS ON THE LIVE CORPUS (Archaeon, 2026-09-10; interpretation pending)
  D1/D2/D4 (player detectors): ineligible -- the chart models no player
  identity; 21 of 3,005 attested experiments declare players.
  D3 LOCAL_VARIANCE_ANOMALY: eligible 77 of 93 regions (median 40 obs each);
  fires on 30: 28 LOWER_DISPERSION, 2 HIGHER; fired ratios 0.02..4.23. At n=40
  the band [1/3, 3] is close to a phase boundary (Harmonia be9c22959), so
  these are very likely outside-band ratios -- worlds whose score variance is
  far below their neighbours' -- not small-sample noise. What that means about
  Harmonia's harness corpus is HARMONIA'S to say; the number is reported with
  its geometry and nothing more.
  D5 REPEATED_OUTLIER_REGION: eligible 314/710 cells, 3 signals.
  D6 BOUNDARY_TRANSITION_HINT: eligible 50/50, 1 signal.
  None of these is a finding. D3 is the only detector Harmonia has admitted,
  and only for region discrimination on a frozen corpus.

SUBSTRATES THAT EXIST AS RUNNABLE CODE
  evaluate_bitstring     integrated, qualified  (the only one that was, 09-06)
  herakles/evca          radius-3 CA, pure library, 50 tests, conventions
                         re-earned by test against the published hex; on main
  ca_density_v0          Vivarium wrapper of the above; golden reproduced;
                         BRANCH (worktree-vivarium-campaign-e1-e6-e16)
  herakles/ca_stream     streaming CA kind, 27 tests; the specified alpha
                         configuration proven INERT (see 4.7); on main
  eca_rule_eval_v1       radius-1 elementary CA, 25 tests, convention
                         re-earned; 256 rules -> 224 behavioural classes at
                         the 7-ring/8-step scope; on main
  proteus/eval + boolean3 pure VM evaluation with first-witness ordering and
                         budget-exhaustion-as-status; 3-input Boolean grammar
                         compiled to a declared VM subset, exhaustive parity
                         vs an independent evaluator; on main
  nk_landscape_v0        NOT built. Licensed by Harmonia; Daedalus's A1.

TOOLS (Techne, branch techne/h0h5-tools-2026-09-09)
  z3-solver 5.0.0.0, hypothesis 6.165.10, ribs 0.12.0, stitch_core 0.1.29:
  installed, pinned, wheel-hashed, first checks passed. DreamCoder cb0e63f5c
  with submodules pinned; smoke run BLOCKED (four measured blockers). Stitch's
  documented result reproduced exactly (1,919,558 -> 316,890, 3 abstractions)
  under a manifest committed DECLARED_NOT_RUN before the run. stitch_core's
  distributed artifacts carry NO license: export blocked, internal use only.
  POET not downloaded: it has no consumer yet.

HOST
  16 logical cores, 31.6 GiB RAM, ~12-13 GiB free with the engine, consumer and
  other seats resident. Available RAM is the binding constraint. No GPU used.

--------------------------------------------------------------------------------
3. WHAT HAS BEEN TESTED, BY SEAT, WITH RECEIPTS
--------------------------------------------------------------------------------
ARCHAEON (main; 261 tests, with and without the engine ledger)
  - Template registry: flat/nested normalisation; check() = runnable AND
    drawable AND buildable; kind-generic spec builder (any implemented kind,
    template-declared outcome rule, nothing defaulted, legacy hashes byte-
    identical); constant form; cross-axis constraints.
  - Detector calibration: D3's null rate reconciled (exact F-tail; floor
    geometry; denominators); repeat aggregation to one row per independent
    unit (reproduces Harmonia's 6.4x inflation and its removal).
  - Campaign design metadata v2 for M-ELIGIBLE: deterministic enumeration at
    WORLD, mean-null with variances 1/96 vs 1/112, sealed hashes pinned.
  - Exploration reserve (family-first deficit round-robin), INACTIVE until the
    operator sets values; release-condition probe against the live engine;
    frozen-universe machinery; H5 decoders (exactly 16 per rule, checked);
    producer cost receipts with enforcement classes.
  - Roadmap, 69-entry crosswalk, 28 work packages, 18 decisions; live loop.
DAEDALUS (dev engine; ef05397f2)
  - Baseline audit found the authorized resolver, read-side re-hashing, write-
    side hash gate, lineage-root budget debit and import provenance ALREADY
    EXISTED; added only the read-path expected-digest gate (checked after
    authorization), a symmetric 16 MiB limit, and a reservation phase.
  - Fixtures: foreign client with the exact digest gets AccessDenied; own
    world wrong id gets NotFound; wrong hash; double billing; fork budget.
VIVARIUM (branch; 364 tests; 24 real boundary executions)
  - Loader slice: artifact slot on a new fixture kind; ten ordered preflight
    rejections; kind called with frozen bytes and no client; consumed digest
    changes the seal, locator does not; budget exhaustion a distinct status;
    interruption/lease; duplicate publication idempotent; enforceable vs
    measured limits recorded; gpu unavailable, not zero.
  - Earlier: repeat capability (4 ordered observations in one world),
    degeneracy guard fixed, result_schema per kind, campaign branch rebased on
    the live v7 engine, ca_density_v0 wrapper with both success masks.
HARMONIA (main; rulings 5759518f0, c9910be21, a88f2ab71, be9c22959, dd38720c0)
  - Arm ruling confirmed; three analysis levels; D3 admitted for region
    discrimination only; five scope rules for quoting D3 rates; binomial-null
    frozen design; packet v2 accepted with two amendments; routes (c) and (d)
    accepted; repeat blocker found and verified closed; D3 band shown to be a
    phase boundary with a sizing rule; H0-H5 qualification cycle QR-1.0.0
    with six adversarial fixtures all caught; H4-ADAPTIVE-1.0.0 protocol.
HERAKLES (main)
  - 69 templates mined then re-examined (31 mechanisms, six capabilities);
    six machinery findings by running it; EvCA library with conventions
    pinned; C1-e historical reproduction 17/18 under a pre-committed
    protocol; twelve references fetched (7 VERIFIED, 4 PARTIAL, 1 MISMATCH);
    region-ablation probe with a size-matched control; ca_stream_v1 and
    eca_rule_eval_v1 with the inert-configuration obstruction filed.
PROTEUS (main)
  - B1 pure library (27 tests; 64/64 specimens agree with the arena path;
    budget exhaustion distinct from mismatch); PR-ID identity convention
    backward-compatible with the 64 fossils; boolean3 substrate; genome_read.
MNEMOSYNE (main)
  - X5 design (reference-only); migration 011 with the 16/16 battery;
    credential-rotation tracker opened; ASSETS path correction.
TECHNE (branch)
  - Acquisition command; four tools pinned; five first-useful-check receipts;
    Stitch reproduction at zero tolerance; "no upstream pickle in the engine"
    as a test; licences recorded unresolved rather than guessed.

--------------------------------------------------------------------------------
4. WHAT HAS BEEN FOUND (each with its scope; none is a scientific claim)
--------------------------------------------------------------------------------
4.1 The bitstring bench has an analytic null. Against a fresh hashed target,
    any candidate's score is Binomial(L, 1/2)/L; mean 1/2, variance 1/(4L).
    Scoped to fresh-target sampling: against a FIXED target one score is an
    exact Hamming distance and is informative. (Herakles F-6; Archaeon test.)
4.2 D3's 0.000 vs 0.106 was sample size, not coupling. Exact F(7,15) tail
    0.1088 at the eligibility floor; F(79,319) tail 2e-8 at the old
    calibration geometry. Both numbers right. (Archaeon WP-0d; Harmonia
    accepted and withdrew her coupling hypothesis.)
4.3 D3's band is a phase boundary, not a sensitivity setting. For a true
    ratio inside [1/3, 3] the fire rate -> 0 as n grows; outside -> 1; at 3.0
    -> 0.5. Lift over the null for an inside-band ratio peaks near n=12-16 per
    region. Sizing rule adopted. (Harmonia be9c22959.)
4.4 D3 cannot detect the M-ELIGIBLE arm contrast. Arms L=24 vs 28 give a true
    variance ratio 1.167; at every size the lift is zero or negative. M-SIGNAL
    over that campaign with D3 would be a guaranteed null. Resolution: route
    (d) -- the endpoint is region discrimination on a frozen corpus; the arm
    contrast leaves the endpoint; M-ELIGIBLE keeps its purpose (S17
    eligibility). (Harmonia 2d; Archaeon as design owner; accepted.)
4.5 Counting rows instead of independent units inflated D3's false-alarm rate
    6.4x at the floor (2 experiments x 4 repeats). Fixed by aggregating to one
    row per experiment before any detector runs; verified independently
    (0.0808 at 1 and at 4 repeats). (Harmonia; Archaeon.)
4.6 NK within-landscape variance follows (1 - 2^-(k+1))/(12N); checked by
    exhaustive evaluation at N=8. Consequence: the NK k-contrast (1.94x at
    N=16) is also inside D3's band; route (c), a variance-ratio test across
    landscapes, is the k-contrast instrument. (Reviewer; Archaeon; Harmonia.)
4.7 The specified H2 streaming configuration is inert. All six recovered
    density genomes map every popcount-<=1 neighbourhood to 0, so an all-zero
    reset plus one injected bit returns to all-zeros in one step. The
    instrument is proven by its controls (shift register solves delayed
    recall exactly; fails temporal XOR because the readout is linear).
    Measured statement is exact and narrow; four alternatives filed; D-18.
    (Herakles 175b5da08.)
4.8 EvCA historical reproduction: 17 of 18 cells within a pre-committed band;
    maj reproduces exactly; particle2 at N=149 is 4.97 SE off with
    transcription the only surviving suspect; HELD as a qualification number.
    (Herakles C1-e.)
4.9 Under the direct 12-bit decoder the four high genome bits are inert, so a
    parent reaches at most 8 distinct neighbour rules; a balanced permutation
    reaches up to 12. Catalogue and multiplicities identical. This is the
    access difference H5 is about and is a construction fact to declare, not
    a finding. (Archaeon h5_decoders.)
4.10 256 elementary rules collapse to 224 behavioural equivalence classes at
    the 7-ring/8-step scope; right-shift and identity are distinguishable at
    horizon 8 and identical at horizon 7. The scope decides what is
    separable. (Herakles feca5e688.)
4.11 H0's interaction has sqrt(2) the SE of its main effects for ANY pairing
    correlation; it needs twice the blocks. The 5 pp effect threshold is a
    sizing decision frozen from the pilot's observed SD, never chosen first.
    (Harmonia dd38720c0.)
4.12 Proteus's VM NOT is bitwise complement mod 2^32; Boolean NOT must be
    compiled as XOR with ONE or the program leaves the Boolean domain on its
    first negation. (Proteus 790fb4803.)
4.13 External evidence, fetched and verified (Aporia deck, vivarium branch
    3b1fb8a0f): reservoir-computing-with-CA success can stem from the ENCODING
    rather than the automaton (Glover, Osipov, Nichele 2024) -- H2's confound
    is published, which is why the readout class and budget are sealed;
    a repository-scale QD study found NO archive advantage over a sequential
    champion at matched budgets (Chen 2026) -- H3's nearest test found none.
    H4's precedent is "established only against a TUNED baseline". Four of
    six hypotheses are UNTESTED in the literature as posed.
4.14 A program-level proposal (a sparse dynamic-graph "evolutionary
    substrate") was adjudicated as NOT a culmination: five of its six elements
    are H1-H3 under new names, and it never says what gets copied when
    something works. (vivarium branch 5362ef6c7.)

--------------------------------------------------------------------------------
5. WHAT HAS NOT BEEN TESTED, AND WHAT NOTHING LICENSES
--------------------------------------------------------------------------------
  - No experiment on any new family has run. NK does not exist. The CA corpus
    (C3) and the Boolean/CEGIS lanes have not been issued.
  - No M-SIGNAL round has run; M-ELIGIBLE has not been issued (credential).
  - No fossil-directed selection has been compared against the frozen random
    control anywhere. The signal->experiment path is wired and tested; it
    has never directed a real experiment because no directed template is
    admitted.
  - No detector result on the live corpus has been adjudicated (section 2).
  - D3's binomial-null calibration at the family's actual L has not run
    (frozen design exists).
  - Nothing licenses: a discovery claim; a novelty claim; a transfer claim;
    that the bitstring bench "has nothing in it" beyond fresh-target
    sampling; that any CA computes; that stitch_core may leave this host; that
    the 64 Proteus specimens are responsive agents (75% world-blind under the
    current channel); that a unit-test count is acceptance evidence.

--------------------------------------------------------------------------------
6. BLOCKERS AND DECISIONS THAT SIT WITH THE OPERATOR
--------------------------------------------------------------------------------
  B1  harmonia-m2 credential: supply the token if saved, or authorise Daedalus
      to build an owner-preserving reissue route. Blocks the read grant,
      hence M-ELIGIBLE's release condition and every read-scope analysis.
  B2  v8 deployment review (deploy/CANDIDATE_BUILD.json). Blocks the read-
      path digest gate in production, hence artifact-consuming kinds outside
      the dev engine.
  D-6  reserve and archive values (1 of 6; 90 days; 24 rows; caps). Producer
      records the established share only until set.
  D-15 append-only witness-availability log (Mnemosyne proposes; Archaeon
      and, per migration 011, already implemented as the design; confirm).
  D-17 stitch_core licensing: development-only; nothing derived through it
      leaves the host until a licence is recorded.
  D-18 H2 injection semantics: alternative 1 (non-uniform reset at declared
      density; relaxation time measured before the horizon), as recommended.
  P1  packet JSONs (acquisition plan, backlog) still absent.
  R-1  credential rotation: PEW credentials in git history; simultaneous on
       M1 and M2. Not a research dependency.
  Also: branches to land on main (Vivarium loader + ca_density_v0; Techne
  tools) so every seat reads one head.

--------------------------------------------------------------------------------
7. SUGGESTED NEXT STEPS, IN ORDER, WITH PARALLEL SETS
--------------------------------------------------------------------------------
NOW, in parallel, no dependencies
  a  Land the branches on main (Vivarium, Techne); Vivarium drops its copy of
     herakles/evca now that Herakles's is on main.
  b  Branch C first corpus. Archaeon writes the C2 templates (reflection and
     complement nulls, centre-only and one-step controls, uniform) against
     the wrapped ca_density_v0; the operator admits them; Archaeon issues
     C3-hist (six genomes), C3-base (constant-output and centre-only rules),
     C3-null (transforms), C3-acq (120 random rules) as human-issued batches;
     Vivarium executes (minutes); Harmonia declares the paired analysis before
     issue. First real corpus on a spatial substrate.
  c  Branch A. Daedalus builds nk_landscape_v0 on packet v2.1 (licensed);
     Archaeon's A2 templates follow; A3-acq at length 16, six landscapes per k.
  d  H1. Vivarium + Proteus build cegis_boolean_v1 (loop sealed inside the
     kind, consuming a failure_input_set through the loader); Archaeon then
     issues source packs and the three arms.
  e  H3. Archaeon builds the offline replay on the first real candidate
     stream (b or c) and hands Techne the stream format for the pyribs
     adapter (first-writer-wins on exact ties is now a measured fact to
     declare in the policy).
  f  H5. Vivarium wraps eca_rule_eval_v1; Archaeon's decoder templates and a
     human-issued fixed-neighbourhood comparison follow.
  g  Harmonia: HA-1 rulings; X1 with route (c) as the worked analysis; the
     binomial-null calibration at the bitstring family's L.
THEN
  h  M-ELIGIBLE once B1 and WP-0c land: issue, rerun Stage 0 unchanged,
     report eligible units.
  i  H2 under D-18: measure relaxation time, fix the horizon, re-run the alpha
     with the non-uniform reset; rule search only after.
  j  H0 Boolean 2x2 once d exists; size the interaction at twice the blocks.
  k  H4 alpha loop on synthetic tasks under H4-ADAPTIVE-1.0.0.
LATER
  A4 related landscapes and source-artifact transfer; C4 co-development;
  P0 replicator spike (operator cap); X2 backend contract with a tool that
  passed repeatability under tested conditions.

--------------------------------------------------------------------------------
8. WHAT AN EXTERNAL REVIEWER SHOULD CHECK
--------------------------------------------------------------------------------
  1  Every rate quoted with a geometry and a denominator (section 2, 4.2-4.5).
  2  That "done" rows in roles/Archaeon/H0H5_STATUS.md cite commits and
     receipts, not plans; that branch-only work is marked as such.
  3  That no directed template is admitted and no M-SIGNAL round has run, so
     no selection-improvement claim can exist yet.
  4  That the two design changes forced by measurement (4.4, 4.7) were made as
     versioned amendments with the old result preserved.
  5  That D3's live firing (section 2) is reported without interpretation.
  6  That the H5 access difference (4.9) appears in the stipulated-outcomes
     list before H5 runs.
  7  That stitch_core has not left the host (D-17).
  8  That the loader's ten rejection conditions are real executions on a
     development engine, not mocks (Vivarium receipt).
================================================================================
END OF PACKET
================================================================================
