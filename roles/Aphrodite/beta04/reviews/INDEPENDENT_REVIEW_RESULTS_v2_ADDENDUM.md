# INDEPENDENT ADVERSARIAL REVIEW, v2 ADDENDUM: E2, AR-1, FINAL FIELDS, AND THE v1 RESPONSE AUDIT (C-015)

- **Reviewer:** the same independent role as v1 (`3ac85e783`). The reviewer produced none of the reviewed work.
- **Basis:** origin/main at `7a19484e2`, merged into branch `aphrodite/b04-review`.
- **Compute:** 1 worker, OMP_NUM_THREADS=1, under 0.02 core-h. No production search was run. Scratch output only.
- **Severity scale (as in v1):**
  - **BLOCKER:** a label or headline claim is wrong or unsupported.
  - **MAJOR:** an interpretation is overstated, or an alternative is not excluded.
  - **MINOR:** everything else.

---

## 1. Verdicts

| Item | Reported | Verdict |
|---|---|---|
| E2 freeze / custody | FREEZE_E2 (`4e4995da0`) before results (`af3e7a0c5`) | **VERIFIED** (see V1 below) |
| E2 per-family labels | REACHED 13, DESERT_OR_HORIZON 2 (headline) | **SUPPORTED** under A1-B.5 / A2.1 |
| E2 co-labels | CREDIT_GRADIENT 4 (F051, F045, F052, F041); CREDIT_MISLEADING 1 (W483b8c31-F046) | **DERIVATION CORRECT.** Re-derived from the hit table; identical to the analyzer's own `per_family[*].flags`. Descriptive only (E2-4) |
| Primary hit totals /120 | credit_blind 68, chain_strict 44, chain_neutral 80, desert_ref 0 | **SUPPORTED.** Recounted from 720 shards; 0 differences |
| Archive arms (5 qualified families) | X3 17/40, X3G 25/40, chain_neutral 27/40 | **SUPPORTED**, recounted |
| REACHABILITY_ATLAS_COMPLETE | YES | **SUPPORTED** against A1-B.9. Needs a rendering limit (E2-2) |
| FRONTIER_ARCHIVE_EFFECT | INCONCLUSIVE_CENSORED | **SUPPORTED.** Cluster differences re-derived: map_of_filter -2.25 / -2.0; scan_of_map -1.0 / 0.0. The descriptive direction must be stated (E2-5) |
| 4x skip | "cannot change a label" | **DEFENSIBLE.** The stated reason is inaccurate, and the skip is a deviation from prereg s B (E2-6) |
| AR-1 production | 0/15; scratch 15/15; HORIZON_R1 12, UD 3; exploratory | **SUPPORTED as a readout.** Freeze precedes the result; 10/10 blobs match. Its bearing on MIGRATE is near zero (AR-1 below) |
| Response to v1 | 14 items accepted | **Mostly carried out.** Two open items (R-1, R-2) |

**V1 (custody checks).**
- FREEZE_E2 is an ancestor of `af3e7a0c5`.
- Between the freeze and the result, the frozen atlas/tfs1 code (arms.py, e2_driver.py, e2_analyze.py, enum.py, core.py,
  library.py) is byte-identical.
- The E2 PLAN.json `code_sha256` matches FREEZE_E2 on all 23 shared entries.
- **Independent re-derivation of a stratified sample of 30 shards.** Arms: all 6 arms, hits and non-hits. Methods:
  - reviewer's own code: tfs1 interpreter;
  - library rebuilt from WORLD_MANIFEST foundry-acquired terms;
  - evaluator test + task tribunal via `tfs1.e3.worlds.judge`;
  - the reviewer's own widened probe (400 random lists, |v| <= 60) against the sealed expanded witness.
- **Result:** the primary-hit verdict agrees in **30 / 30**.
  - Every runner primary hit is dev-consistent, passes test and tribunal, and agrees with the sealed witness on all
    400 widened inputs.
  - Every non-hit sampled is either "no dev-consistent program in 2e5", or has a first dev-consistent program that
    fails the tribunal (16-33 / 400 widened disagreements).
- **Library hashes.** The reviewer-built library resolves every `L_` id in the programs. Its sha256 differs from the
  shard's only because the provenance metadata differs.
- **Full recount over 720 shards:**
  - 0 START_HITs;
  - 0 certifier-assisted primary hits;
  - every primary hit passes FINAL evaluation (archive OFF);
  - 232 / 234 primary hits call both constituent stones. The 2 exceptions are chain_neutral W0321d83c-F040 s1 and
    Wc025415a-F041 s2, which re-express one mechanism inline.

---

## 2. Findings on E2

### E2-1 -- MAJOR -- What "REACHED 13/15" licenses

**What it does mean.** On the 15 foundry-selected families, given:
- the ORACLE decomposition: a 2-entry, constituents-only library;
- the FOUNDRY-ACQUIRED stones, which are behaviourally sealed-equivalent (probe agreement 1.0);

a dev-credit mutation chain at 2e5 produces a first dev-consistent program that qualifies in at least 1 of 8 seeds on
13 / 15 families.

**How strong it is.**

| Measure | Value |
|---|---|
| REACHED threshold (A1-B.5) | chain_neutral >= 1 / 8, a lenient bar |
| Robust (chain_neutral >= 6 / 8) | 10 / 15 |
| Weak (1 / 8) | W6eb945cc-F033, W483b8c31-F046 (neutral) |
| Median chain_neutral hitting charge | about 400-11,000 on 12 families; about 109k on F033 |

**What it does NOT license.**
- Stone discovery.
- Composition with library *selection*: no all-acquired E2 row exists.
- Generality beyond the motif set.
- Anything about TFS-1's own stones. The E3-KP primary is 7 / 15 with those.

**Cognitive accounting.**
- Stones and decomposition: supplied DEVELOPMENTAL context. The decomposition comes from the coordinator / foundry.
- Composition: SEARCH_INFRASTRUCTURE plus ORGANISM-level local search.
- Qualification: CERTIFIER.

**Required rendering:** "Given oracle-decomposed foundry stones, the composition step on these 15 foundry-selected
families is reachable by local search at 2e5 (robustly on 10 / 15)".

### E2-2 -- MINOR (rendering) -- REACHABILITY_ATLAS_COMPLETE = YES describes the composition step, not the link that failed

- The atlas (53/53) measures existence, density, hitting cost and robustness **with the foundry stones supplied**. 17
  R2 families ran in the base grammar.
- The first demonstrated failure, R1 stone acquisition, is characterized by E3-KP / E3-ID, not by the atlas.
- The YES is correct against A1-B.9. The synthesis must render it as an atlas of the composition step given stones.

### E2-3 -- MAJOR (partly resolves v1 F5) -- E2 and E3-KP agree, and E2 removes the order-fragility half of F5; the selection half stands

**Where the two searches agree.** Same stones, same families, two independent search procedures:
- E3-KP enumeration at 1e6: 14 / 15 (given-foundry row).
- E2 chain_neutral at 2e5: REACHED 13 / 15.

| Family group | Enumeration (1e6) | Chain (2e5) |
|---|---|---|
| post_fold W6eb945cc-F047 | fails | fails |
| post_fold W2bdef02f-F048 | solved at 589,267 | DESERT_OR_HORIZON (589k is beyond 2e5, so consistent with horizon) |
| guard_p (F045, F052, F041) | order-fragile; solved at 61-96% of budget | chain_neutral 8, 7 and 7 of 8 |

**Where the reviewer's own s3.2 run failed.** It used syntactically different stones and missed the guard_p families
at 1e6 under enumeration.

**Conclusion.**
- v1 F5's **order-fragility** concern applies to the enumeration INSTRUMENT, not to composition per se.
- Given the right stones, the composition step is robustly reachable on these families by local search.
- This strengthens "composition is not the first failing link".
- F5's **selection** half stands. Admission rule 3(c)-(d) selected exactly the families where the foundry's stones
  composed, and both rows reuse those stones on those families.

### E2-4 -- MINOR -- CREDIT co-labels are correct, but they are screening noise-level in count, and saturated

- **Derivation.** It reproduces A1-B.5 / A2.1 exactly (check: F052 neutral 7 vs blind 4 = 3, the boundary case).
- **Factual correction.** The analyzer is said to emit "headline only". In fact it emits the co-labels in
  `per_family[*].flags`. The ledger 22:58Z note should be corrected.
- **Count vs chance.** 5 directional labels on 15 families, against about 3 expected by chance (P(|d| >= 3) about 0.21).
- **But the pattern is not uniform.** It is skeleton-consistent: all 3 guard_p families favour credit (blind 0, 4, 2
  vs neutral 8, 7, 7). F051 and F045 are 8-vs-0.
- **The seed-count endpoint saturates at 2e5.** Hitting charges show a much larger credit effect that the labels do
  not capture. Median chain_neutral vs credit_blind:

  | Family | chain_neutral | credit_blind |
  |---|---|---|
  | F040 | 1,437 | 54,273 |
  | F039 | 411 | 43,748 |
  | F044 | 2,277 | 55,584 |

  This is a 1-2 order-of-magnitude reduction in hitting time from dev partial credit on about 10 families. It is
  descriptive, and it is the most informative credit observation in E2.
- **CREDIT_MISLEADING on W483b8c31-F046** (blind 7 vs strict 1 / neutral 1) is a single family.
- **None of these is a confirmatory claim.**

### E2-5 -- MINOR -- FRONTIER: state the descriptive direction

- INCONCLUSIVE_CENSORED is structurally fixed (2 informative units < 5).
- Both informative clusters point AGAINST the archive arm:
  - X3 - neutral: -2.25 and -1.0;
  - X3 - X3G: -2.0 and 0.0.
- Pooled over the 5 qualified families: X3 17, X3G 25, neutral 27 (of 40).
- The synthesis should say: "censored; the descriptive direction on the 5 qualified families is negative for the
  descriptor archive; no NO is inferable (fewer than 5 units)". Do not leave the impression of a neutral null.

### E2-6 -- MINOR (process) -- The 4x skip is defensible, but the stated reason is inaccurate and the skip is a deviation from a pre-registered conditional

**The literal trigger fired.**
- Prereg s B (`E2_E3KP_PREREG.md:76-78`) lists 4x when "FRONTIER_ARCHIVE_EFFECT is INCONCLUSIVE". It did fire.
- A1-B.7 restricts the scope to (family, arm) pairs with at least 1 hit.

**"Cannot change a label" is not accurate.**
- 4x could change descriptive co-labels. Examples: F051 credit_blind 0 / 8; W483b8c31-F046 neutral 1 / 8.
- Headline REACHED cannot fall, and DESERT families are ineligible.

**What makes the skip defensible.**
- (a) 4x cannot resolve the frozen question. FRONTIER is censored by descriptor non-qualification on 3 / 5 clusters,
  and more budget cannot create informative units.
- (b) EXPERIMENT_PLAN s4 and directive Exp 5 scale only "qualified treatments", and none qualified.

**Required:** record it as a declared deviation from the s B trigger, with reasons (a) and (b), not "near ceiling".

### E2-7 -- MINOR -- desert_ref 0/120 is a fair LIBRARY ablation, but not an informative desert measurement

**As a library ablation it is matched.** desert_ref is credit_blind without the library, so credit_blind vs
desert_ref (68 vs 0) is a one-factor library contrast.

**As a "desert reference" it is predetermined.**
- Admission rule 3(b) already required from-scratch failure at 1e6 (enumeration). Expanded witnesses are 13-19
  nodes.
- There is no credit-using no-library arm. Red-team B1 suggested lib=None chain_neutral; A1-B.1 chose credit-blind.
  So E2 cannot say whether dev credit alone crosses the desert without stones.
- Render it as "library ablation at credit = none", not as a desert measurement.

---

## 3. AR-1 (alien reserve) -- MINOR -- It bears on MIGRATE only weakly

**Custody.** FREEZE_ALIEN_AR1 (`6c92d3b08`) is an ancestor of the result (`6f841131a`). All 10 frozen blobs match.

**The readout.**
- Only 1 / 17 units acquired.
- HORIZON_R1 12: budget exhausted with no dev-consistent program.
- UD 3: W0321d83c f0, W483b8c31 p0, Wc025415a p0.

**Why it barely bears on MIGRATE.**
- (i) It fails at an EARLIER point than TFS-1. TFS-1 acquired 14 / 17 units; AR-1's MC-1 search mostly never reaches
  a dev-consistent R1 program. That is a statement about AR-1's search efficiency, confounded with its representation.
- (ii) There is no given-true-stones row (NOT_DEFINABLE). So it says nothing about composition in the alien
  representation.
- (iii) The hypothesis MIGRATE rests on is that mechanisms not defined as syntactic lambda subterms avoid the
  extraction mis-cut. AR-1 does not test it: almost no unit produced a correct program to extract from.

**What it does add.**
- (a) The Wc025415a p0 dev gap reproduces in a second, independent representation and search. That strengthens the
  WORLD dev-gap reading for that single unit.
- (b) It is one instance showing that a naive alien candidate does not escape the acquisition horizon at 1e6.

**On the coordinator's ledger reading** ("the stone-acquisition link binds in a non-lambda representation too"):
- It is literally true.
- It must carry "for this one machine + search; confounded; composition untested".
- It is not evidence against MIGRATE as a class.

---

## 4. Audit of COORDINATOR_RESPONSE_REVIEW_v1.md (accepted vs carried out)

| v1 item | Promised | Carried out? |
|---|---|---|
| F2 / F3 | Withdraw the world/ruler reading; W03 erratum | YES: `W03_DEV_REPORT.md:68-74`; CAMPAIGN_STATE E3ID "SUPERSEDED INTERPRETATION" |
| F4 | Precedence blocked the OE trigger; prediction right | Recorded in the response. The CAMPAIGN_STATE TFS1 entry still lists "UNDERDETERMINED_STONE 7" without the F4 note. MINOR |
| F5 | New rendering | PARTLY. The response doc has it. **The ledger 18:55Z entry ("composition step reachable given correct stones") has no correction entry, unlike F10's utc correction.** MINOR (R-2) |
| F6, F11, F12 | "stated in the synthesis" | **NOT YET**: no synthesis exists. Open (R-1) |
| F7 | RETAIN non-discriminating | YES (CAMPAIGN_STATE) |
| F8 | ID-A1.4 premise falsified | YES (response + CAMPAIGN_STATE) |
| F9 | PHASE3 s4 revised | YES (`PHASE3_WIND_TUNNEL_INTERFACE.md` s4: extraction invariance, budget coverage, IDENTIFIABILITY on 1 case) |
| F10 | Ledger correction; `date -u` from now on | YES. Correction entry at 21:56Z. Later stamps match their commits: 21:56Z vs 21:57:07Z, 22:58Z vs 22:58:34Z, 23:19Z vs 23:19:24Z |
| F1 | "Future result files record start/end UTC" | **NOT YET.** The first post-response result file, `tfs1/e3/runs/e3r_pilot/E3R_REPAIR_CLASS_seed0_B1000000.json` (`91456b10b`), has no start/end UTC. **Must be in the E3-R runner before FREEZE_E3R.** MINOR (R-1) |

**R-1 and R-2.** Open items are the synthesis-dependent ones (F6, F11, F12) and F1 (UTC in the E3-R runner). The
missing ledger correction for the F5 wording at 18:55Z is R-2.

**E3-R note (not reviewed in depth; pending).** `E3R_PREREG.md` item 6 treats the reviewer's s3.2 estimate
(off_xabs = 9 / 15) as KNOWN.
- That number was an exploratory run with hand-derived stone spellings.
- The guard_p / post_fold outcomes depend on the library sha, through the keyed order. An X-ABS spelling that differs
  would change them.
- The pre-registered reproduction check is the right guard. "KNOWN" should read "expected, pending reproduction".

---

## 5. Recommended labels for all 8 final fields

None of COMPOSITIONAL_DISCOVERY, DEVELOPMENTAL_INHERITANCE, SECOND_ORDER_ACQUISITION or ECONOMIC_ADVANTAGE has a
frozen definition anywhere in beta04/ (grep: only "not COMPOSITIONAL_DISCOVERY" disclaimers). **MAJOR (process):** fix
the mapping rule below in a dated amendment BEFORE the synthesis states these four fields.

| Field | Recommended value | Basis / rendering |
|---|---|---|
| WORLD_DEMAND_QUALIFIED | **NO** | Addendum D strict: 5/12 worlds; 2 pairings < 3. The admitted families are demand-genuine |
| REACHABILITY_ATLAS_COMPLETE | **YES** | A1-B.9 met. It is an atlas of the composition step given supplied foundry stones (E2-2) |
| TFS1_INSTRUMENT_QUALIFIED | **NO** (TFS1_REACHABILITY_INSTRUMENT = FAIL) | Frozen pooled rule, 7/15. The first failing link is stone acquisition (horizon + extraction), per the v1 response |
| FRONTIER_ARCHIVE_EFFECT | **INCONCLUSIVE** (INCONCLUSIVE_CENSORED) | The descriptor is INSTRUMENT_UNVALIDATED on 10/15 families; the descriptive direction is negative (E2-5) |
| COMPOSITIONAL_DISCOVERY | **INSTRUMENT_UNVALIDATED** | The E3 2x2 (the only discovery test) was gated off by TFS1 = NO. E3-KP / E2 / E3-ID / E3-R all use supplied decompositions or sealed-indexed R1 tasks, so they are not discovery. Not NO (finite, unqualified null); not INCONCLUSIVE (no discovery data exist) |
| DEVELOPMENTAL_INHERITANCE | **INSTRUMENT_UNVALIDATED** | E4 barred: E1 = NO, R5 = 0, TFS1 = NO. Not run |
| SECOND_ORDER_ACQUISITION | **INSTRUMENT_UNVALIDATED** | Requires E4-type depth-2 dependency with ablation; not run |
| ECONOMIC_ADVANTAGE | **INSTRUMENT_UNVALIDATED** | Q5 accounts for an improvement of a qualified treatment, and none exists. The partial-credit hitting-time reduction in E2 (E2-4) is a descriptive search observation with supplied stones, not an economic advantage of a developmental mechanism |

**Strongest counter-position on the last four:** "NO" (nothing was achieved).
- It is rejected. NO reads as a tested negative, and the directive forbids inferring impossibility from a finite
  null.
- INSTRUMENT_UNVALIDATED states truthfully that the gates protecting these questions were not passed.

**Recommendation and first failure (unchanged from v1; strengthened).**
- **Recommendation:** CHANGE_SEARCH_OR_DEVELOPMENTAL_MACHINERY.
- **First demonstrated failure:** stepping-stone ACQUISITION: search horizon plus extraction non-invariance, with a
  world dev-gap in 1 unit.
- **Why it is strengthened:**
  - E2 shows, by a second search procedure, that the composition step given correct stones is not the binding link
    on this set.
  - AR-1 neither supports nor refutes MIGRATE's representation hypothesis.
- **Remaining open disagreement:** MIGRATE. It stays a minority option until an alien candidate with a definable
  given-stones row exists.

---

## 6. Not checked

- **E3-R:** not run, not frozen.
- **E2 atlas metric values:** density, robustness, gradient. Completeness flags and one family's content were
  inspected; the values were not re-derived.
- **X3G K-calibration internals:** K matched within 5% as reported.
- **D-BEH qualification internals:** accepted from v1 and from the qual shards.
- **AR-1 machine semantics and conformance:** `alien/runs/CONFORMANCE_pilot_v2.json` was not re-run.
- **Worker concurrency** during E2 / AR-1 / E3-R pilot.
