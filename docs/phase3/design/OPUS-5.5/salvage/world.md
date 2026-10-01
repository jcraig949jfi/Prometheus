# Salvage digest: world machinery (R1 world forge)

Group: world. Architect: OPUS-5.5 (Epimetheus), Phase 3.
Frozen basis: REQUIREMENTS v2 + RSE_ARCHITECTURE.md at commit 77d3c99c3 (worktree
C:/prometheus-worktrees/epimetheus-phase3, HEAD 77d3c99c3). Date 2026-10-01.
Question asked of every component: DOES THIS SATISFY A PHASE 3 REQUIREMENT BETTER THAN REBUILDING IT?
Method: dossiers (docs/phase3/intake/*/seats/*.md) and evidence/*.md used only as locators; every verdict
below rests on source code I opened and, where it was safe, on unit tests I ran from a scratch directory
with PYTHONDONTWRITEBYTECODE=1 and pytest's cache disabled. Size classes are agentic-coding tokens:
S < 5M, M 5-30M, L 30-100M, XL > 100M.

-------------------------------------------------------------------------------------------------------
## 0. Verdict in one paragraph

Nothing in this group is KEEP as R1 production machinery. Every world family built here is small, mostly
passive or solitaire, authored by the same model family as its rulers, and none emits a bound-typed
certificate (WLD-01). There is no curriculum builder (WLD-08), no exact POMDP solver, no independently
authored slow solver (WLD-04), no own-reliability family (WLD-16), no F1 Delta/payback machinery (WLD-18),
and no sealed split that is actually confidential (WLD-03). R1 must be written fresh around one POMDP
family interface. Seven parts are worth lifting, all small: (1) the Ensorain ARC3 exact-Bayes hidden-state
processes, which are the seed of anchor family F3; (2) the Ludus differential leak audit, which is the seed
of WLD-07; (3) the Cosmos commit-then-reveal broker, which is the seed of the sealed-split evaluator once it
gets real confidentiality; (4) the exact marginal-preserving surrogate; (5) Tyche's exact lowest-informative-
order certificate and its feature-bank foothold scan; (6) the Hecate evaluator contract, which is the seed of
the admission-ladder verdict logic; (7) the Cosmos AST lineage audit, which feeds REP-06/WLD-05. The Charon
ceiling_v0 hidden-group universe is the best candidate generator for an active-identification family. The
rest is a valuable failure and known-answer corpus (HISTORICAL_CONTROL) or retires. Estimated saving: 10-20%
of the R1 build. The worlds themselves save almost nothing. The doctrine the record paid for (missing rung =
no claim; certificates before freeze; differential, not substring, leak tests) saves more than the code.

-------------------------------------------------------------------------------------------------------
## 1. Verdict table

    id   component                                        category            slot      cost  decisive reason
    W01  Ludus depth profile gap(k) + GATE-W1             HISTORICAL_CONTROL  R1 cert   NA    tie-break artefact; no bound type; 2-player perfect-info only
    W02  Ludus qualification fixtures (Ledger/Orchard/     HISTORICAL_CONTROL  R1 WLD-17 S     ready-made known-answer decoys incl. the F7 Nim closed-form decoy
         Nim345+Bouton/MD one-ray/Kuhn leaks)
    W03  Ludus bench (stopping worlds, exact DP, verify)  HISTORICAL_CONTROL  -         NA    solitaire stopping only; verify blind to draw law; tie-rule history
    W04  Ludus arena interface + epistemic layer          RETIRE              R1 iface  NA    hashes public state only; no ticks/costs/keyed streams; OpenSpiel better ref
    W05  Ludus differential leak audit (probe_pair)       EXTRACT             R1 WLD-07 S     right method (4/4 planted leaks), half the channels, single-state
    W06  Toolbox receipts/IR digest/replay/keyed streams  EXTRACT             R0        M     sound receipt+chain+forensic scan; not R1; tests dirty the tree
    W07  Toolbox admission (component conformance)        EXTRACT             R0/R1     S     probe-power check is good; it is NOT world (WLD-02) admission
    W08  Toolbox reference worlds, search, backends       RETIRE              -         NA    toy worlds, point mutation, partial lowering
    W09  Ensorain WTP world-genome foundry                HISTORICAL_CONTROL  -         NA    genome fuses world+organism; field regression; WTP-02 constant FP
    W10  Ensorain null ladder N0-N5 + XC                  REBUILD             R1/R2     M     need stands (WLD-02/MEA-03); rungs are field-regression specific
    W11  Ensorain exact marginal-preserving surrogate     EXTRACT             R1/R2     S     exact (math checked, test passes); n-d array domain only
    W12  Ensorain ARC3 exact-Bayes processes (suff)       HARDEN              R1 F3     S     F3 core already exists; needs actions, computed causal states
    W13  Cosmos holdout broker + audit + ReceiptChain     HARDEN              R1 WLD-03 M     commit-then-reveal is right; seal is integrity, not secrecy
    W14  Cosmos world-graph engine (latch families,       HISTORICAL_CONTROL  -         NA    one-cue latch demand (WLD-13); laws restated planted certificates
         miner, phenomenon certificate)
    W15  Cosmos AST code-lineage audit (independence.py)  EXTRACT             R0/R1     S     computes shared-import lineages; misses relative imports
    W16  Tyche v2 certify.py + worlds_v2 needles          EXTRACT             R1 cert   S     exact resilience order is a real certificate component; weak nulls
    W17  alien_circuitry exact monoid oracle + v2 orbits  HISTORICAL_CONTROL  R1 WLD-17 S     known-answer "lookup after canonicalisation"; quotient-split fixture
    W18  Charon ceiling_v0 hidden-group universe          HARDEN              R1 family S     real hidden-state active-ID family with a commutativity dial; no cert
    W19  Hecate LLM-authored probe worlds                 HISTORICAL_CONTROL  -         NA    5/5 SIGNALs reduced to trivial explanations; cheap-world degeneracy
    W20  Hecate evaluator contract + metamorphic harness  EXTRACT             R1/R0     S     arm-symmetric exact verdict with mandatory arms; DRAFT, never issued
    W21  Hecate alien-lawful system generator             HISTORICAL_CONTROL  R1 WLD-17 NA    exhaustively verified plants + matched seductive nulls; key exposed
    W22  Ludus Atlas of Game Worlds (catalogue)           RETIRE              -         NA    1,338 rows, 0 executable, 0 audited; WLD-21 forbids memory reconstruction

-------------------------------------------------------------------------------------------------------
## 2. R1 needs mapped to what exists

    R1 need (requirement)                    best existing material                         verdict / action
    POMDP family grammar + generators        none fits. Candidates: ARC3 processes (W12),    write new interface; port W12 as F3, W18 as an
      (WLD-06, WLD-03)                       ceiling_v0 hidden group (W18), Tyche needle      active-ID family, W16 needles as F2/F5 fixtures
                                             classes (W16); WTP genome (W09) is wrong shape
    exact solvers (WLD-04)                   ARC3 forward filter (exact Bayes, passive);     write a finite-horizon belief-MDP DP for small
                                             Ludus minimax + stopping DP (wrong domain);     POMDPs; reuse W12 filter; W17 BFS as reference
                                             alien_circuitry reverse BFS (deterministic nav)  for deterministic navigation
    independent slow solver (WLD-04)         none at a different author (the ARC3 stdlib     commission at I2 (spec-only brief)
                                             replica is same-family)
    bound-typed certificates (WLD-01/19/20)  Tyche exact resilience order (W16); ARC3        write new certificate tool emitting (value,
                                             declared causal-state counts (W12); Ludus       bound type, method, policy language, compute);
                                             gap(k) (W01, unusable)                          lift W16 functions; compute causal states
    admission baseline ladder (WLD-02,       Ensorain ladder (W10, wrong rungs); Hecate      write POMDP rungs (constant, best memoryless,
      MEA-03)                                contract (W20, verdict logic); marginal         canonicalised lookup, acquisition-matched FSC);
                                             surrogate (W11)                                 W20 as evaluator; W11 as one rung
    all-channel leak audit (WLD-07)          Ludus probe_pair (W05)                          extract + extend to trajectories and learner
    sealed quotient-disjoint splits          Cosmos broker (W13, integrity only); toolbox    harden W13 (encryption keyed to eval job, key
      (WLD-03, SCI-15, PRS-04)               "holdout_seeds" (contiguous ints, not sealed)   audit, read budget); new quotient checker,
                                             C3 D2 encrypted package (NOT OPENED: UNKNOWN)   regression fixture from W17
    curriculum builder (WLD-08)              nothing in this group                           write new; blocked on a DEV-13 genome
    sealed known-answer world set (WLD-17)   W02 decoys, W17 orbit table, W16 PRF/twins,      assemble classes from these patterns but
                                             W09 specimen #10, W21 seductive nulls           REGENERATE under seal: all are public now
    reconstruction check (WLD-21)            Ludus rules_audit.json (source sha256 per rule) keep the pattern (tiny)
    physics never consults ruler (WLD-14)    arena "a World cannot call a Player"; Cosmos    write the static import check (S)
                                             certificate reads native observations only
    computed independence (WLD-05, REP-06)   Cosmos independence.py (W15)                    extract; add access logs
    F1 Delta/payback/tau_id (WLD-18)         nothing                                         write new (it is the slice family)
    own-reliability family (WLD-16)          nothing                                         write new
    open demand / d_unfam (WLD-15)           ceiling_v0 non-abelian variants are a           write new; W18 is a candidate host
                                             candidate host

-------------------------------------------------------------------------------------------------------
## 3. Component findings

### W01 Ludus depth profile gap(k) and GATE-W1 -- HISTORICAL_CONTROL
Paths: ludus/depth_profile.py, ludus/baselines.py, ludus/worlds.py, ludus/ledgers/cycle001_*.
What it really does:
- Depth-k minimax that scores the cutoff with the world's own score formula read early
  (depth_profile.py:52-61). gap(k) = 1 - fraction of sampled states where the ALPHABETICALLY FIRST of the
  tied depth-k argmax actions is optimal (depth_profile.py:64-68 sorts; :89-91 takes `[:1]`).
- Samples 250 states uniformly from the reachable set with |A| >= 2 (depth_profile.py:71-75). Admission:
  gap(4) >= 0.20 (:94). The run writes its ledger into the source tree (:116-117).
- The greedy baseline picks a per-world score formula by world-name prefix (baselines.py:50-66). Exact
  minimax rebuilds its memo on every call (worlds.py:449-464). reachable_states silently truncates at
  200,000 states (worlds.py:475-490).
Correctness: controls exist (ludus/controls, CONTROLS_2026-09-16.json: 8/8 depth rows as expected,
including the Nim cheat admitted). I did not re-run them: run_controls.py writes its JSON into the repository.
NEW EVIDENCE (section 4.2, in-memory probe): on CTRL_NIM345, gap(4) = 0.240 under the alphabetical
tie-break, 0.190 under uniform random tie-breaking (BELOW the 0.20 gate), and 0.000 at every k if any
tied optimal action counts. 48% of states are ties at k=4 (87% at k=1). The recorded finding "GATE-W1 admits
Nim" is therefore partly a tie-break artefact. On a world whose cutoff evaluation carries no information,
gap(k) measures the tie-break convention, not lookahead demand. This is the same failure class as the
greedy tie rejection the architecture names in s1.
Would serve: WLD-01 d_horizon and WLD-19 d_think, as proxies only. It has no bound type and no declared
policy language, covers deterministic two-player perfect-information games only, and its cheap-player class
excludes short closed-form programs (the seat's own LUDUS-33).
Coupling: stdlib; nothing outside ludus/ imports it.
Reason: the need (a depth/deliberation certificate) is real, but this instrument cannot be the base. Its
value is the documented failure plus the fixtures (W02). R1's d_think must be built new: an exact smallest
reactive circuit vs smallest iterative controller on small families, with set-valued tie handling and the
tie fraction reported.

### W02 Ludus qualification fixtures -- HISTORICAL_CONTROL (known-answer fixtures)
Paths: ludus/controls/fixtures.py, ludus/controls/CONTROLS_2026-09-16.json.
What it is: Ledger (greedy-decidable negative, fixtures.py:52-82); Orchard (deferred-payoff positive whose
optimum is still a constant policy, :85-131); Nim345 plus bouton_action (closed-form decoy, :144-204);
corrupt_pot / corrupt_prob / inject_cycle (:212-252); MartianDiceOneRay (a rule change that no invariant
inspects, :255-288); four Kuhn leak variants: named key, innocuous key, legal-action order, public state
(:305-390).
Serves: WLD-17 (the closed-form-solvable and leaky classes of the known-answer set); the F7 "Nim-like decoy
with a closed-form optimal rule" in the architecture's anchor table; WLD-07 (the planted-leak battery seed).
Limits: public and same-family authored. They work as development regression fixtures, not as the sealed
WLD-17 scoring set, which needs sealing and an I2+ or procedural tool.
Cost S: re-target to the R1 world interface.

### W03 Ludus bench (stochastic stopping worlds, exact DP, bench verify) -- HISTORICAL_CONTROL
Paths: ludus/bench/core.py, compiled.py, verify.py, worlds.py, worlds2.py, circuits.py, rules_audit.json.
What it really does:
- A single-agent stopping/selection interface (core.py:19-43). Backward induction runs in floats, not exact
  rationals. A silent cycle guard seeds V[s]=0 (core.py:134; also evaluate() :282); check_acyclic exists
  because of it.
- Verify: probability normalisation at tolerance 1e-7 (verify.py:69), acyclicity (:86-113), and per-world
  invariants for 4 of 21 worlds (:234-235; others report "NO PER-WORLD INVARIANTS WRITTEN" :253).
Defects:
- Verify is blind to the draw law: the one-ray Martian Dice fixture verifies (run_controls.py:203-214).
- check_incan contains dead code (verify.py:143-144; `_multiset_ok` always returns True, :160-161).
- Circuit r0003 stops on exact ties including pot=0 (core.py:226, `return not (e_gain > p_dead * pot)`).
- Five of six real worlds occupy one structural cell.
Serves: nothing in R1 as machinery; the worlds are solitaire stopping problems with at most two decision
axes. The one reusable piece is the rules_audit.json pattern (a source sha256 per rule line): the only
in-repo instance of WLD-21 (verify a reconstructed world against its source). It moved two Martian Dice
rules and overturned a cycle-002 reading.
Reason: a failure corpus with three clean lessons. Reconstruction from memory masquerades as the real
game. A tie rule manufactures zeros. On-policy support mismatch created the "contextual competence"
reading. Retire as machinery.

### W04 Ludus arena interface + epistemic layer -- RETIRE
Paths: ludus/arena/core.py, worlds.py, worlds_epistemic.py, epistemic.py, players.py, verify.py,
test_epistemic.py.
What it really does: an OpenSpiel-like World/State/Player split with CHANCE and SIMULTANEOUS sentinels
(core.py:40-43, 159-188). Episodes are deterministic (core.py:376-458). The replay digest excludes timing
(:360-373), redacted_for(player) produces per-player views (:325-358), and the information-set and
observational-equivalence helpers live in epistemic.py:99-219.
Tests run (section 4.1): verify.py ALL PASS (Kuhn value -1/18, Bouton, tic-tac-toe draw, determinism on 5
worlds, about 70 s); test_epistemic.py 25/25.
Defects:
- state_hash hashes public_state only (core.py:193-197). The replay digest therefore cannot see a
  hidden-state divergence, so bit-identical full-state replay (REP-01) is not demonstrated.
- RNG stream aliasing: chance uses Random(seed) and players use Random(seed*1000+pid) (core.py:385-389).
  Episode seed 1001's chance stream equals player 1's stream at seed 1, which violates the spirit of REP-07.
- Sibling imports through sys.path (`import core`, audit.py:32).
- No metered internal ticks, no cost channel, no snapshot bytes.
- Rule provenance is "MACHINE_INFERENCE" (core.py:70).
Reason: the R1 interface must follow the DGM contract (an action or a tick budget advances the world; costs;
keyed streams; snapshot/restore). Adapting the arena costs about as much as writing that. OpenSpiel is the
better external cross-check for WLD-04 because it has a different author. Keep two ideas: replay identity
excludes instrumentation, and redacted per-player replays.

### W05 Ludus differential leak audit -- EXTRACT
Paths: ludus/arena/audit.py (probe_pair), ludus/controls/fixtures.py (Kuhn leak worlds).
What it really does: for a pair of states that differ only in a secret, it compares 13 player-reachable
signals: observation, serialize, state_hash, public_state, legal-action order/set/count, chance outcomes,
rewards, current player, type repr, and the error text of an illegal action (audit.py:42-74). It fires on all
4 planted Kuhn leaks, against 1 of 4 for the key-name check (CONTROLS json). Re-run here: Kuhn and hygiene
CLEAN; the replay-metadata finding (the full replay names chance outcomes) is by design.
Gaps against WLD-07:
- Single-state and one-step: pairs are never rolled forward, so reward timing, termination timing and step
  budget are unobserved, and is_terminal is not compared directly.
- The "RNG consumption" audit is not differential: it counts chance nodes under a fixed policy across seeds
  (audit.py:153-174), not across the two hidden values.
- No metabolic charges, and no cheap learner with full access to all channels.
- Pair construction is a world-specific heuristic: attribute names cards/hands/hidden/secret and values in
  range(3) (audit.py:131-146).
Serves: WLD-07 (REQUIRED), WLD-17 leaky class, MEA-05.
Cost S: lift probe_pair and the four leak fixtures into an R1 module. Generate pairs from the family's
declared hidden variable, roll pairs forward under matched keyed streams, add every WLD-07 channel and the
full-access learner, and require a planted leak per channel.

### W06 Bellerophon Worlds Kernel: receipts, IR digest, replay, keyed streams -- EXTRACT (to R0)
Paths: prometheus/toolbox/receipt.py, ir.py, backends/local.py, ref/worlds.py.
What it really does:
- Receipts are content-addressed (sha256 over canonical JSON, id truncated to 24 hex; receipt.py:86-88) and
  chained per file through prev_receipt_id (:98-129). read_all is a strict reader (:135-154); scan is a
  forensic reader that names truncation, edits, duplicates and chain breaks by line (:157-188).
- The kernel build hash is computed over LF-normalised sources (:48-60). Engineering and science ledgers must
  be disjoint (:75-77). cpu_s and wall_s are recorded (local.py:461-492).
- Keyed streams: sha256(tags) seeds a xorshift64 generator (ref/worlds.py:24-41).
Tests run: test_admission, test_admission_power, test_integrity, test_replay_committed: 259 passed in 46 s.
Defects:
- The "holdout" split is just the contiguous integer seeds after the train seeds (local.py:78-83). It is not
  sealed (WLD-03).
- The chain is per file, not a ledger with segment files. Nothing is signed. No energy or token fields.
- The host name is written into receipts. xorshift64 is a weak generator.
- test_integrity.py:371-388 rewrites kernel source files in place and restores them with LF endings, which
  dirties a CRLF checkout. A test suite that writes into the repository is a PRV-04 hazard; see section 4.3.
Slot: R0, not R1 (REP-01, REP-07, PRV-01, PRV-03, CMP-02). Cost M to fold into the R0 runner and ledger.

### W07 Toolbox admission -- EXTRACT (pattern)
Path: prometheus/toolbox/admission.py.
What it really does: software-component conformance. It checks the protocol (admission.py:92-104), BIT replay
equality over 3 seeds (:126-137; SEMANTIC replay is not checked in Phase 1), and agreement with a registered
reference ONLY IF the probe has power, i.e. the reference trace depends on the actions (:145-158; it repaired
a wrong twin that had passed on an action-blind probe). It also checks that a cheat parameter changes the
trace (:161-169) and that provenance fields are present.
It does NOT do WLD-02. There are no baselines, no solvability witness and no cognitive demand. The word
"admission" is a false friend.
Serves: the WLD-04 two-solver agreement harness (the probe-power rule) and R0 component conformance.
Cost S.

### W08 Toolbox reference worlds, search and backends -- RETIRE
Paths: prometheus/toolbox/ref/worlds*.py, search.py, backends/sfe.py, npe.py.
Toy register, ring and pendulum worlds; point-mutation selectors with tiny populations; SFE lowering is
partial and NPE is UNAVAILABLE_INTERFACE. No world reproduction and no certificate (dossier s3.1, confirmed in
ref/worlds.py:1-60). Only prometheus/atlas_bee imports the package.

### W09 Ensorain WTP world-genome foundry -- HISTORICAL_CONTROL
Paths: ensorain/wtp/genome.py, registry.py, world.py; ensorain/wtp2/; ensorain/wtp3/world3.py,
campaign3.py.
What it really does: a random JSON genome over 12 "laws" that includes the ORGANISM: memory substrate,
learning rule, search policy with rollout depth (genome.py:63-103, :90-98). It also has mutation and
recombination operators (:153-175). The world is a tensor field of 64-4096 cells, and the task is
field-value prediction.
Defects:
- World and organism are fused in one genome, so the world supplies the competence (WLD-09, ORG-17).
- No action-dependent hidden-state demand is certified.
- WTP-02: one-float constants scored as competence; 8 of 8 positives were SCALAR-EXPLAINED (verification.jsonl).
- WTP-03: a post-data same-class batch fit (N6) beat all 9 promoted specimens.
Reason: the specimen #10 genome (0e3e9ca1cb88f30c) and the WTP-03 N6 miss belong in the known-answer and
anti-calibration set as canonical planted negatives. That covers WLD-17, SCI-07 and "a missing rung blocks
the verdict". Retire the foundry.

### W10 Ensorain null ladder N0-N5 and XC -- REBUILD
Path: ensorain/wtp3/collider.py:164-204 (null_ladder), :294-332 (collide).
What it really does: batch, hindsight-favourable fits of N0 zero, N1 constant (plus recent), N2 marginal
(ridge on one-hot coordinates), N3 linear in coordinates, and N4 bounded Hamming lookup. The best null also
includes the online SIMPLE substrates as N5 (:322-325). XC = AC - max(ladder). A test set with fewer than 32
cells yields None, i.e. no claim.
Tests run: test_wtp3.py 5/5, including "missing null is no claim" and "the constant is never positive".
Defects: field-regression specific. N6 (the same-class tuned batch rung) was absent before the data came in.
None of the POMDP rungs WLD-02 names exist: constant policy, best memoryless policy, canonicalised
seen-episode lookup, acquisition-matched FSC learners.
Reason: the need is REQUIRED (WLD-02, MEA-03) and the doctrine is right. The rungs must be written for the R1
interface. Cost M, including the FSC learners shared with MEA-07.

### W11 Ensorain exact marginal-preserving surrogate -- EXTRACT
Path: ensorain/wtp3/collider.py:27-48; tests/test_wtp3.py:10-20; validate3.py (V5).
What it really does: splits the field into its additive (main-effects) part plus a residual. It permutes the
residual, removes the permuted residual's own main effects, and rescales it to the residual's standard
deviation.
Correctness: I checked the algebra. The re-centred residual has zero per-mode marginals, so it is orthogonal
to every additive function. The mean, every per-mode marginal mean and the total variance are therefore
preserved exactly. test_surrogate_exact passes.
Serves: the WLD-02 rule "if preserving the marginals preserves the task, reject the world"; MEA-03 shuffled
controls; the MEA-05 cheat set.
Limit: n-dimensional arrays only. The POMDP analogue (preserve per-step observation and reward marginals,
destroy temporal and hidden dependence) has to be designed. Cost S.

### W12 Ensorain ARC3 answer-keyed processes with exact Bayes -- HARDEN
Paths: ensorain/arc3/suff/worlds.py, worlds_unifilar.py, cssr.py, ladder.py, tests/test_worlds.py.
What it really does:
- W0 iid; W1 Beta-Bernoulli with a closed-form posterior; W2 order-k Markov with the per-context Beta
  posterior; W5 key-value Zipf stream with exact lookup Bayes.
- HMMWorld runs exact forward filtering (worlds.py:89-123). It ships the Even process (2 causal states,
  infinite Markov order), the golden mean (order-1 control) and the simple nonunifilar source.
- worlds_unifilar.py generates random strongly connected unifilar machines. cssr.py is a causal-state learner.
Tests run: 7/7. The Bayes log-loss reaches the entropy rate 2/3 within 0.01 on 60k symbols; the Even
process provably has no finite window; STAT(k) equals the Bayes predictor to 1e-9. evidence/verification.jsonl
records that the Even window floor was replicated independently.
Defects to fix:
- Passive prediction only. F3 needs an action interface so gap_react is defined.
- The causal-state count is DECLARED (worlds.py:97, :122-123), not computed by minimisation, and
  random_unifilar is "not guaranteed minimal" by its own docstring. As shipped, d_mem is an upper bound.
- The `pi` argument is ignored; the stationary distribution is used instead (worlds.py:95-101).
- Seeds are raw default_rng(seed), not keyed.
- No slow solver from a different author.
- No bound-typed output. The analytic window floor exists only as a script, not as a certificate field.
Serves: anchor family F3 (the architecture's "Even-like vs golden-mean-like with exact Bayes"); WLD-01
(d_mem from causal states); WLD-04; WLD-10 (exact Bayes references); WLD-17.
Coupling: numpy (scipy in ladder.py); no imports from WTP.
Cost S. This is the single highest-value lift in the group.

### W13 Cosmos holdout broker, audit and ReceiptChain -- HARDEN
Paths: prometheus/cosmos/broker.py, audit.py, hashing.py. Holdout directories listed by name only (s6).
What it really does:
- Checks that a law is FROZEN and that its freeze hash recomputes (broker.py:84-89).
- Checks the sealed spec's sha256 against the preregistered commitment, and the family source against the
  spec (:62-73).
- RECEIPTS the prediction vector's hash before running the sealed worlds in a subprocess (:91-110), then
  reveals (:111-123). Intervention prescriptions are also receipted before their ladders run (:142-187).
- The ReceiptChain fsyncs every record (hashing.py:69-109).
- audit.py checks R1-R6: chain integrity, immutability after freeze, lifecycle order, prediction-before-
  reveal order, seal hashes, and committed copy as a prefix. Its 5 cheat tests pass (run here).
What it does NOT do: confidentiality.
- load_spec reads the sealed spec into the main process (broker.py:69).
- The holdout D/E/F family sources and specs are plaintext tracked files (holdout/well.py, swarm.py, clone.py,
  sealed_spec*.json, per git ls-files). Any search job can read them. There is no key, no read budget and no
  quotient check.
- The dossier records that every sealed family was written by the same author "knowing the law's form".
- The later C3 D2 package (hidden_D2.enc, sealbox.py, custody.py, firewall_check.py) appears to add
  encryption. It was NOT OPENED under the holdout rule, so its adequacy is UNKNOWN.
Bugs:
- intervene() calls load_spec(commitment) without the holdout id (broker.py:143), so E/F interventions raise
  SealBroken. The failure is loud.
- The G6/G6b pass thresholds are hard-coded (:182, :257) instead of living in a program constants file
  (SCI-15).
- The commitments are hard-coded in audit.py:26-28.
Serves: PRV-03 (prediction before observation), strongly. WLD-03 and PRS-04 partially (integrity only).
SCI-15 consumable splits are not enforced: D, E and F were all spent in one day.
Cost M: generalise from "law" objects to any frozen predictor; encrypt with a key held only by the
evaluation job; add a key-access audit, a read-budget ledger and the quotient-disjointness check.

### W14 Cosmos world-graph engine -- HISTORICAL_CONTROL
Paths: prometheus/cosmos/contract.py, world.py, substrates/, planted/, miner.py, quotient.py,
phenomenon.py, c3/.
What it really does: families expose a knob lattice, declared dimensionless coordinates, and three
hand-written mechanisms SEL/LOG/LAST (contract.py:15-23). The shared demand is one cue retained across K
distractors and emitted at the ask (contract.py:19-23). That is a one-cue latch. SELECTIVE_PAYS (a margin
vs LOG and LAST) reads only native observations (phenomenon.py:29-55). Evaluation uses common random numbers
with sha-derived seeds (world.py:19-33; hashing.py:119-121).
Defects: under WLD-13, latch-certified worlds cannot host reasoning claims. The laws restated the planted
certificate (C0 laws indistinguishable from a zero-parameter rule; C3 rule 104/120; verification.jsonl). All
visible and sealed families come from one author lineage. The C3 P1/P2 certificate (decodability with a
stratified permutation null, plus a state-swap interchange; c3/certify.py:24-90) is an ORGANISM ruler: refer
it to the measurement group (MEA-15, CAU-04). It is out of scope here.
Reason: the law-restates-certificate case and single-author sealed transfer are canonical false positives for
SCI-07. Retire the engine.

### W15 Cosmos AST code-lineage audit -- EXTRACT
Path: prometheus/cosmos/independence.py.
What it really does: builds each family source's transitive closure of repository imports, excludes
signature-only modules, and merges families that share any module into one lineage by union-find
(independence.py:18-96). It states plainly that it detects shared code, not shared ideas (:9-10).
Defects: relative imports are ignored (only `node.level == 0`, :38), so a family using `from . import x`
escapes the audit. importlib and other dynamic imports are invisible.
Serves: REP-06 (I2 requires a disjoint import graph apart from the statistics library); WLD-05 (one input to
the computed class, which also needs access logs). Cost S.

### W16 Tyche v2 certify.py and worlds_v2 needle classes -- EXTRACT
Paths: tyche/v2/certify.py, tyche/v2/worlds_v2.py, tyche/tests/test_v2.py.
What it really does:
- lowest_informative_order computes, exactly, the smallest input subset of a 4-input truth table that carries
  information about the output (worlds_v2.py:219-229). This is the correlation-immunity order: a real
  needle/interaction-order certificate for table laws.
- Subset MI with a permutation correction (certify.py:31-46, :84-93).
- A raw feature-bank foothold scan over delays, window sums and accumulators (:57-70, :96-101).
- Worlds: hidden precursors are delay, window majority, accumulator and window parity, combined by
  xor/parity/secret sharing/resilient tables. Keyed-PRF and twin negatives are included.
Tests run: 7/7, including needle orders certified (2, 3, 3, 4, 2) and bank footholds < 0.01. The certificate
caught a 0.92-bit window foothold in the D6 design before freeze (dossier s13).
Defects:
- mi_corrected takes the 99th percentile of only 20 permutations, which is effectively their maximum. The
  bank uses 5 permutations per feature across about 800 features: a weak null that ignores multiplicity.
- The 0.005-bit threshold is ad hoc. Plug-in MI is biased upward.
- The exact order assumes independent, uniform precursors.
- Dead branch at certify.py:80-82. No bound types. Passive streams only.
- Every planted law is built from the organism's own 27-op lens chemistry (verification.jsonl; worlds_v2
  emit()), so the worlds are written in the organism's grammar (WLD-05, AGR-15).
- tyche/worlds.py:195-200 reads hecate/alien/data/answer_key.json, a cross-seat file coupling.
Serves: WLD-01 (an interaction-order / d_comp component relative to a declared feature language); WLD-06
(order as a generator parameter); F2/F5 needle fixtures; WLD-17 (a second certificate tool, though
same-family). Cost S.

### W17 alien_circuitry exact monoid oracle and v2 orbit table -- HISTORICAL_CONTROL
Paths: alien_circuitry/universe/monoid.py, directed_rewriting.py, enumerate.py, metrics.py;
alien_circuitry/ac01d (v2 orbit table); tests/test_universe.py, test_survivor.py.
What it really does: enumerates the full transformation monoid T_n (generators act on values) and computes a
reverse-BFS distance table to rank-2 targets (monoid.py:44-84). It also computes kernel-compatibility ground
truth (:87-89) and class-wise eccentricity (:92-107). The word-rewriting universes (BRAID_B3, ABELIAN) are
enumerated exhaustively.
Tests run: 20/20. Forward BFS equals the table on 300 samples; BFS, bidirectional BFS and the oracle agree;
vectorised and scalar semantics are equal.
History: depth-4 lookahead proves every trap (the "too shallow" no-go). In v2, D turned out to be an exact
function of the contingency-table orbit (25,382 orbits, a 34.8 KB table). Per the dossier, the held-out
targets were in-distribution after quotienting (CODE-INFERRED there, not re-verified here).
Serves:
- WLD-17: the "lookup-solvable on held-out after canonicalisation" class of the known-answer set.
- WLD-03: a real instance of a split that is NOT quotient-disjoint, i.e. the planted symmetric-image split
  the requirement's test asks to flag.
- F7: an exact reference solver for deterministic navigation.
Coupling: numpy/scipy core. The ac01d families need torch/CUDA, with GPU non-reproducibility on record; do
not carry them. Cost S to package as fixtures.

### W18 Charon ceiling_v0 hidden-group universe -- HARDEN
Paths: charon/ceiling_v0/universe.py, SPEC.md, baselines.py, validate.py.
What it really does:
- Hidden state Z_m^k (27 states). Four actions are translations. Coordinate permutations in the families
  F_P / F_M / F_M2 / F_MT form a commutativity dial (universe.py:63-95).
- A lossy, near-balanced sensor (:101-106) and a metered RUN channel with an interaction budget.
- Evaluation queries are longer than the exploration cap, and evaluation is sealed by InteractionForbidden.
- Ground truth: true_word_element (:153-169).
Correctness: tests NOT run (one test spawns a subprocess with cwd inside the repo and a stripped environment,
which would write bytecode there). validate.py is an oracle soundness audit. The spec was reconstructed
after a working-tree loss and no hash survives (SPEC.md:3-13). universe.py was restored from a transcript
and a surviving .pyc (universe.py:3-6).
Defects:
- No exact Bayes or optimal-experiment reference, and no certificate.
- The scored answer is a function of (tag, group element). Canonicalised lookup over the 27 element classes
  is therefore the natural strong baseline, and it is absent from the ladder (the P3b signature automaton is
  the nearest).
- The LLM arms call network lanes (reasoner.py:42; lanes.py:28-37), which is not allowed in R1 (INF-05).
- Seeding uses seed*1_000_003+17, not keyed streams.
Serves: WLD-06 (a structural dial); WLD-01 (d_mem is exactly computable because the belief is a consistent-
state set over 27 states); WLD-15 (the non-abelian variants are an open-demand candidate); an
active-identification family next to F4/F6.
Cost S: universe.py is 288 stdlib lines. Add an exact belief/Bayes reference, certificate fields, keyed
streams and the R1 interface, and drop the LLM arms.

### W19 Hecate LLM-authored probe worlds -- HISTORICAL_CONTROL
Paths: hecate/programs/HT-*/worlds/*.
What they are: small simulations written by an LLM for each mechanism, with null twin, positive control,
CHEAT and, later, SIMPLE_ALT arms.
Record (dossier s21): 5 of 5 SIGNALs reduced to trivial or known explanations. Signals cluster in the
cheapest worlds (5/9 vs 0/16, p 0.012). Null twins drifted in about 11 worlds. One positive control was
unattainable (K4).
Reason: a failure corpus. It shows "effect present by construction", cheap-world degeneracy, and why
SIMPLE_ALT must be mandatory. These worlds are also generator-authored (they fail WLD-05).

### W20 Hecate evaluator contract and metamorphic harness -- EXTRACT
Paths: hecate/programs/_lib/evaluator_contract.py, hecate/metamorphic/harness.py, tests.
What it really does:
- One rule, meets_success, is applied identically to TREATMENT, NULL_TWIN, SIMPLE_ALT, POSITIVE_CONTROL and
  CHEAT. All five arms are mandatory.
- Comparisons use exact Fractions with explicit tolerances.
- Precondition failures return INSTRUMENT_FAIL and never raise. Identical payloads across seeds are flagged
  as pseudo-replication.
- In a pilot, a positive-control miss returns SPEC_UNATTAINABLE. SIGNAL requires SIMPLE_ALT to fail
  (contract docstring :1-60).
- The harness corrupts the evaluator's rows in scratch copies and judges the reaction.
- Status: DRAFT, never issued.
Tests run: 64 passed (contract + alien generation).
Serves:
- WLD-02 evaluator logic: the solvability witness is the PC attaining; baselines failing is SIMPLE_ALT failing.
- SCI-05 attainability before freeze.
- MEA-05 controls wired to abort.
- MEA-03 "a missing rung blocks the verdict", through the mandatory arms.
Cost S.

### W21 Hecate alien-lawful system generator -- HISTORICAL_CONTROL
Paths: hecate/alien/generate.py, verify.py, systems.py.
What it really does: generates finite deterministic systems whose planted properties are verified
exhaustively. A system is kept only if it is not affine and agrees < 0.5 with every known template. Matched
nulls preserve the visible regularities, and are kept only if the planted property fails (generate.py:1-8).
Limit: passive finite maps, not POMDPs. The answer key is a public tracked file that Tyche already reads, so
these 100 systems cannot be part of a sealed set.
Reason: the matched seductive-null construction is the right pattern for the WLD-17 "leaky / seductive"
class and for MEA-02 procedurally generated plants. Regenerate with new seeds under seal if used.

### W22 Ludus Atlas of Game Worlds -- RETIRE
Paths: ludus/atlas_of_worlds/ (716 dossiers, crawler, classifier).
1,338 catalogue rows from Wikidata and Wikipedia; 0 executable and 0 audited (dossier E5). WLD-21 forbids
reconstruction from memory, and nothing here is a source-verified rule set.

-------------------------------------------------------------------------------------------------------
## 4. New evidence from this pass

### 4.1 Tests run (all from the scratch directory, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider)

    suite                                                  result        time   notes
    ludus/arena/verify.py                                  ALL PASS      70 s   20 checks, 5 worlds
    ludus/arena/test_epistemic.py                          25/25         <5 s
    ludus/arena/audit.py                                   1 finding     <5 s   finding = omniscient full replay (by design)
    prometheus/toolbox tests: admission, admission_power,  259 passed    46 s   test_integrity touched sources (s4.3)
      integrity, replay_committed
    ensorain/arc3/suff/tests/test_worlds.py                7/7           27 s
    ensorain/wtp3/tests/test_wtp3.py                       5/5           3 s
    prometheus/cosmos/tests/test_audit.py                  5/5           1 s
    tyche/tests/test_v2.py                                 7/7           51 s
    alien_circuitry/tests/test_survivor.py + test_universe 20/20         4 s
    hecate/tests/test_evaluator_contract.py +              64/64         27 s
      test_alien_generation.py

    NOT run: ludus/controls/run_controls.py (writes CONTROLS json into the repo); toolbox test_kernel (Redis
    probe), tests/mutants.py (rewrites sources) and the other toolbox suites; charon ceiling_v0 tests (a
    subprocess writes bytecode in the repo); the remaining cosmos tests (one has 'holdout' in its path; others
    use the broker); ensorain wtp/wtp2 tests; any campaign or experiment.

### 4.2 Depth-profile tie-break probe (in memory, no files written into the repo)
Exhaustive over eligible states (TITHE: 600-state sample). gap_first is the shipped rule (first sorted tied
action); gap_rand is the expectation under a uniform random tie-break; gap_any counts a hit if any tied action
is optimal.

    world          eligible  k  gap_first gap_rand gap_any  frac_states_tied
    CTRL_NIM345    517       1  0.563     0.540    0.000    0.874
                             2  0.522     0.446    0.000    0.793
                             3  0.296     0.294    0.000    0.567
                             4  0.240     0.190    0.000    0.476   <- admits (>=0.20) only under gap_first
    CTRL_ORCHARD   203       4  0.345     0.345    0.345    0.000
    CTRL_LEDGER    200       4  0.000     0.000    0.000    0.000
    TITHE          600       4  0.040     0.040    0.040    0.008

Interpretation: where the cutoff evaluation is informative (Orchard, Ledger, TITHE), the tie rule does not
matter. Where it carries no information (Nim), gap(k) is set by the tie convention, and admission flips on
it. Any R1 certificate that scores argmax actions must use set-valued scoring and report the tie fraction.

### 4.3 Incident (disclosed)
Running prometheus/toolbox/tests/test_integrity.py executed
test_kernel_hash_names_the_kernel_and_only_the_kernel (test_integrity.py:371-388). It temporarily appends to
prometheus/toolbox/series.py and prometheus/toolbox/tests/test_kernel.py, then restores them with LF
endings. In this CRLF (core.autocrlf=true) worktree that left both files marked modified, with identical
content. I restored the exact checked-out bytes (HEAD blob with LF converted to CRLF, checked equal before
writing). `git status --porcelain` was clean afterwards. No commit, index or history change was made. Lesson
for R0/PRV-04: a "pure" test suite that writes into the tree must be rejected by the receipt layer. A
filename-only grep over prometheus/cosmos/tests/*.py also scanned tests/test_holdout_isolation.py. No content
from it was displayed or used.

-------------------------------------------------------------------------------------------------------
## 5. What R1 should build fresh, in order (salvage-aware)

1. The R1 world interface on the DGM contract: the world advances on an action or when the tick budget
   expires; declared hidden variables; cost channel; keyed streams; byte snapshot/restore; full-state hash.
   Write new. W04 contributes only two ideas.
2. The F1 generator with exact V_fix, V_adapt(L), Delta, tau_id and payback (WLD-18). Nothing to salvage. It is
   the slice family.
3. A finite-horizon belief-MDP exact solver for small families, plus a slow solver commissioned at I2
   (WLD-04). W07's probe-power rule goes into the two-solver agreement harness.
4. The certificate tool emitting (value, bound type, method, policy language, compute) (WLD-01). Lift W16's
   lowest_informative_order and the foothold scan with a proper max-statistic permutation null. Compute
   causal states by minimisation (from W12). d_think gets set-valued ties (lesson of W01).
5. The admission ladder with POMDP rungs (W10's doctrine, new code), W11 as one rung, and W20 as the verdict
   evaluator (WLD-02).
6. The leak audit, extracted from W05 and extended to trajectories, every channel and a full-access learner,
   with a planted leak per channel (WLD-07).
7. Sealed splits by hardening W13: encryption keyed to the evaluation job, a key-access audit, a read-budget
   ledger and a quotient-disjointness checker regression-tested on the W17 orbit split (WLD-03, SCI-15,
   PRS-04).
8. F3 from W12 (HARDEN) and an active-identification family from W18 (HARDEN). F2/F5 needle fixtures from
   W16. Do not use Tyche's chemistry-compiled laws as evaluation worlds (WLD-05).
9. The WLD-17 sealed known-answer set, regenerated under seal from these patterns: W02 decoys (closed form,
   latch, leaky), W17 lookup-after-canonicalisation, W16 PRF and twins, W09 specimen #10, W21 seductive nulls.
   All current copies are public.
10. The curriculum builder (WLD-08): nothing to salvage; blocked on a DEV-13 genome.

-------------------------------------------------------------------------------------------------------
## 6. Holdout and exclusion log
Holdout directories, listed by name only and never opened:
- prometheus/cosmos/holdout/: __init__.py, clone.py, run.py, seal.py, sealed_spec.json, sealed_spec_E.json,
  sealed_spec_F.json, swarm.py, well.py.
- prometheus/cosmos/c3_holdout_D/: .gitattributes, PROVENANCE.md, SELFTEST.json, __init__.py, medium.py,
  seal.py, sealed_spec_D.json, selftest.py, tests/.
- prometheus/cosmos/c3_holdout_D2/: .gitattributes, AUDIT_BRIEF.md, FIREWALL.md, MANIFEST_D2.json,
  PROVENANCE_D2.md, SELFTEST_D2.json, SELFTEST_PROTOCOL.json, __init__.py, allowlist.py, custody.py, draw.py,
  entry.py, evidence.py, firewall_check.py, hidden_D2.enc, protocol.py, protocol/FIREWALL_AUDIT_1.json,
  runner.py, sealbox.py, selftest_D2.py, selftest_protocol.py, verify_reveal.py.
- prometheus/cosmos/tests/test_holdout_isolation.py (name only; see s4.3).
Not opened by rule: anything under docs/phase3/design/ other than OPUS-5.5/; roles/Dionysus/; any
nestor_secrets, credential or .env path.

-------------------------------------------------------------------------------------------------------
## 7. Files read (source and tests opened)
ludus: depth_profile.py, baselines.py (39-78), worlds.py (440-491), bench/core.py, bench/verify.py,
bench/compiled.py (1-60), bench/worlds2.py (index), arena/core.py, arena/audit.py, arena/epistemic.py
(1-50, index), arena/test_epistemic.py (1-40), controls/fixtures.py, controls/run_controls.py,
controls/CONTROLS_2026-09-16.json (head).
prometheus/toolbox: README.md, __init__.py, receipt.py, admission.py, ir.py (1-60), backends/local.py
(index), ref/worlds.py (1-60), ref/controls.py (1-40), tests/test_integrity.py (grep + 371-388).
ensorain: wtp/genome.py, wtp3/collider.py, wtp3/controls.py, wtp3/validate3.py (1-40), wtp3/tests/test_wtp3.py,
arc3/suff/worlds.py, arc3/suff/worlds_unifilar.py, arc3/suff/cssr.py (1-30), arc3/suff/ladder.py (1-30),
arc3/suff/tests/test_worlds.py.
prometheus/cosmos: broker.py, hashing.py, quotient.py, world.py, independence.py, audit.py, contract.py
(1-50), phenomenon.py, substrates/regs.py (1-40), c3/certify.py, store.py (index), tests/conftest.py,
tests/test_audit.py (1-25).
tyche: v2/certify.py, v2/worlds_v2.py (1-40, 219-244), tests/test_v2.py, worlds.py (185-215).
alien_circuitry: universe/monoid.py, universe/enumerate.py (23-71), tests/test_universe.py (1-80).
charon/ceiling_v0: SPEC.md (1-80), universe.py (1-200), baselines.py (index, 116-150), tests/test_all.py
(1-12, 255-300).
hecate: programs/_lib/evaluator_contract.py (1-80), alien/generate.py (1-50), metamorphic/harness.py
(1-22, grep), tests/test_evaluator_contract.py (25-40).
Locators: RSE_ARCHITECTURE.md, requirements.jsonl, evidence/atl.md, idx.md, verification.jsonl (grep),
intake seats Ludus, Bellerophon, Ensorain, Cosmos, Tyche, Hecate, Koios (appendix S1).
