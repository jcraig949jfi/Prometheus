# INDEPENDENT ADVERSARIAL REVIEW OF BETA-04 RESULTS (C-015), v1

- **Reviewer:** an independent agent. It produced none of the work under review.
- **Scope:** completed results E1, E3-KP (primary and secondaries), E3-ID, and FRONTIER_ARCHIVE_EFFECT.
  - E2 screen analysis (credit labels) and AR-1 alien production are PENDING and not reviewed here.
- **Basis:** origin/main at `ea1d944bd`, read in a detached review worktree.
- **Compute used:** 1 worker, OMP_NUM_THREADS=1, about 0.06 core-h in total.
  - All outputs were written to the reviewer's scratch directory only. Nothing was written under `runs/` or
    `foundry/production/`.
  - The re-computations are reported in s3. They are post-hoc and EXPLORATORY. They relabel nothing.
- **Severity:**
  - **BLOCKER:** a label or headline claim is wrong or unsupported.
  - **MAJOR:** interpretation overstated, or an alternative explanation not excluded.
  - **MINOR:** everything else.
- **Policy:** disagreements are preserved (s6), not resolved by narrative.

---

## 1. Verdict per label

| Label | Reported | Review verdict |
|---|---|---|
| WORLD_DEMAND_QUALIFIED | NO (strict; 5/12 worlds pass gate; pairings 2 < 3) | **SUPPORTED.** Recomputed from WORLD_MANIFEST + WORLD_SEALED: gate pass 5/12, admitted R2 38 / R3 8 / R4 7, kind pairs {fp, fs}. Addendum D (`e8cf3a88c`, 13:01Z) precedes production (`8d16a3288`, 15:26Z). |
| TFS1_INSTRUMENT_QUALIFIED | NO, so TFS1_REACHABILITY_INSTRUMENT = FAIL (7/15; UD 7, HORIZON_R1 1; OE not triggered) | **SUPPORTED as a frozen-rule outcome.** The freeze precedes the result in the DAG and the hashes match (F1). **The attached mechanism narrative is not supported** (F3, F4, F6). |
| E3-KP secondaries | fallback-off 0/15; given-foundry 14/15; all-acquired 7/15; seeds 9/15, 8/15 | **Numbers SUPPORTED.** "Composition is reachable given true stones (14/15)" is **OVERSTATED**: the set is selection-conditioned and order-fragile (F5). |
| ID_IDENTIFIABILITY | UD units 4/4 UNIQUE_WRONG | **Counts SUPPORTED** as a literal application of the ID-A1.4 rule. **The causal mapping is NOT supported** for 3 of 4 units (F2, F3). |
| ID_RETENTION_REPAIR | NO (RETAIN-4 7/15; CERT 9/15) | **Mechanically correct, but ZERO-POWER on the units that matter.** Every UD unit had exactly 1 class within budget, so RETAIN-4 = RETAIN-1 there. "Retention does not repair" is unsupported (F7). |
| E3-ID interpretation / "first demonstrated failure = stepping-stone identifiability at world/ruler level" | coordinator reading (W03, ledger, commit `eb1048f28`) | **BLOCKER: UNSUPPORTED.** It is stronger than the frozen ID-A1.4 mapping, which is "WORLD/RULER-**or-HORIZON**". It is contradicted by the data on 3 of 4 units (F2, F3, F4). |
| FRONTIER_ARCHIVE_EFFECT | INCONCLUSIVE (INCONCLUSIVE_CENSORED), pre-outcome | **SUPPORTED.** It is determined structurally (2 informative clusters at most, against the 5 needed) from outcome-free D-BEH qualification (5/15; clusters fp:map_of_filter 4, fs:scan_of_map 1, as in `runs/e2/qual/*.json`). Vocabulary note: F12. |

---

## 2. Findings

### F1 -- (verification; no defect in substance) -- Freezes precede data; hashes match the code that produced the results

- **DAG order.**
  - `FREEZE_E3KP` (`19a374fbf`, 17:29:06Z) is an ancestor of the KP primary result (`19f2b08fa`, 17:49:10Z) and of
    the secondaries (`ea01b7961`, 18:43:54Z).
  - `FREEZE_E3ID` + ID-A1 (`3f18a96bc`, 19:04:54Z) is an ancestor of the E3-ID result (`eb1048f28`, 19:30:11Z).
  - `FREEZE_E2` (`4e4995da0`, 17:06Z) precedes the CENSORED determination (`6cfb02579`, 17:11:57Z).
- **Git-blob hashes.**
  - Every `git_blob` entry in FREEZE_E3KP equals `git rev-parse <commit>:<path>` at `19a374fbf`, `19f2b08fa` and
    `ea01b7961`. That covers core, enum, library, membrane, bench, mutate, e3_known_positive, worlds, the prereg and
    WORLD_MANIFEST.
  - Every FREEZE_E3ID entry equals the blob at `eb1048f28`: e3_identifiability `e885c79c`, prereg `967c2e7c`.
- **Run-time sha256 in result files.** The `code_sha256` / `e3_code_sha256` recorded inside all 14 result files
  (`runs/kp_production/KPA1_W*.json`, `runs/id_production/ID_W*.json`) match the committed code: 273 file hashes,
  0 mismatches (CRLF / LF variants).
- **FREEZE_E2.** All 26 sha256 entries match at `4e4995da0`. Between FREEZE_E2 and FREEZE_E3KP only `tfs1/enum.py`
  changed among the frozen tfs1 files, as FREEZE_E3KP declares.
- **Timing feasibility (tight, not disproven).**
  - KP primary: 2,136 CPU-s on 2 workers needs at least about 1,070 s of wall time. The freeze-to-result window is
    1,204 s.
  - E3-ID: 1,368 CPU-s on 1 worker. The launch-to-result window is 1,470 s.
  - Both are feasible only if launched immediately. Result files carry no wall-clock start/end, so this cannot be
    positively proven either way. See F10.

### F2 -- BLOCKER -- For 3 of the 4 UNDERDETERMINED_STONE units, the R1 world DOES identify the mechanism; the TFS-1 program is globally correct and the stone extraction mis-cuts it

Recomputed with interpreter B (`tfs1.core`). Inputs: 20,402 lists (empty, all singletons in [-200, 200], and 20,000
random lists of length 1-16 with elements in [-60, 60]).

| Unit (ID family) | Sealed mechanism | Seed-0 TFS-1 R1 program (the only dev-consistent one in 1e6) | Program vs sealed witness | Extracted stone | Stone vs sealed on [-40, 40] | Program on [x] vs sealed f(x) |
|---|---|---|---|---|---|---|
| W483b8c31 f0 (F007) | `(lam x (add 2 (mul x x)))` | `(add 2 (max (map (lam x (pow x 2)) xs)))` | **0 / 20,402 differ** | `(lam x (pow x 2))` | 81/81 differ | 0 / 401 differ |
| W6eb945cc f0 (F006) | `(lam x (sub 1 (mul x x)))` | `(sub 1 (min (map (lam x (mul x x)) xs)))` | **0 / 20,402** | `(lam x (mul x x))` | 81/81 differ | 0 / 401 |
| Wb49b6a5f f1 (F009) | `(lam x (mul (mul x x) 3))` | `(mul 3 (max (map (lam x (mul x x)) xs)))` | **0 / 20,402** | `(lam x (mul x x))` | 80/81 differ | 0 / 401 |
| Wc025415a p0 (F010) | x > 4 | `(len (filter (lam x (gt (sub x 2) 3)) xs))`, i.e. x > 5 | 1,379 / 20,402 differ; fails R1 test | `(lam x (gt (sub x 2) 3))` | 1/81 differ (v = 5 only) | -- |

**What the table shows.**
- In the three f-units, TFS-1 found a program that is **semantically identical** to the sealed R1 witness. It hoisted
  the affine or scale part of f outside a reducer that commutes with it: max/min with a monotone map, or a sign flip
  that swaps max and min.
- The first-closed-lambda extraction rule (`e3_known_positive.py:218-228`) then takes only the map body.
- The R1 family identifies f exactly: singletons are in the tribunal, and the program on [x] equals the sealed f.
  The error is in **where the stone boundary is cut**, not in what the world reveals.
- Only Wc025415a p0 is a genuine dev underdetermination. The dev lists contain no element 5
  (`WORLD_SEALED.json` dev for F010), so x > 4 and x > 5 are indistinguishable on dev.

**Claims this falsifies.**
- W03_DEV_REPORT.md:43: "3/4 also pass the R1 test + tribunal; they diverge only on the wider domain the composite
  uses". **False.**
  - The programs diverge nowhere.
  - The stones diverge on essentially every input, including the R1 element range [-20, 20], which is also the
    composite's element range for guard_p and map_of_filter.
- CAMPAIGN_STATE.json:189: "the R1 stepping-stone families do not identify their mechanism over the domain the
  composite uses". **False for 3 of 4.**
- ID-A1.4 (E3ID_PREREG.md:104-105): "Within budget the dev data admit only a wrong mechanism". **False for 3 of 4.**
  The dev data admitted a behaviourally correct mechanism; the instrument extracted a wrong stone from it.
- The pre-amendment map (E3ID_PREREG.md:72-73; code `e3_identifiability.py:53, 489-490`) reads: "mostly UNIQUE ->
  the extraction or promotion step is at fault (an instrument defect)". **That is what the data actually show** for
  3 of 4 units.

### F3 -- BLOCKER -- The same R1 data, the same grammar and the same extraction yield the sealed-equivalent stone under other enumeration keys, so the failure is order-dependent, not world-forced

From the frozen secondary rows that were already in hand before E3-ID was pre-registered
(`runs/kp_production/KPA1_POOLED_*seed1*`, `*seed2*`, `units`):

| Unit | Seed 0 (primary) | Seed 1 | Seed 2 |
|---|---|---|---|
| W483b8c31 f0 | `(pow x 2)`, agreement 0.0 | **`(add 2 (mul x x))` from the SAME F007, agreement 1.0** | HORIZON_R1 |
| W6eb945cc f0 | `(mul x x)`, 0.0 | `(mul x x)`, 0.0 | **`(sub 1 (mul x x))`, 1.0** (F007) |
| Wb49b6a5f f1 | `(mul x x)`, 0.0123 | **`(mul 3 (pow x 2))` from the SAME F009, 1.0** | HORIZON_R1 |
| Wc025415a p0 | x > 5, fails test | **x > 4 from the SAME F010, 1.0** | UNDERDETERMINED |

**All 4 UD units are acquired correctly in at least one keyed order.** The foundry's enumerator also found the
sealed-form programs first on the same families, at charges 442k-476k (`foundry/production/<W>/FINAL.jsonl`
chain_c). The found and sealed forms sit in the **same size class** (Int size 8, bracket 627,413-6,007,202), and
1e6 covers about 7% of that class.

**Why "UNIQUE" is not a property of the world.** It is an artefact of the seed-0 within-class order: n_dev_consistent
= 1 because the budget ends inside the class.

**What the evidence supports.** The first failing link is **R1 stone acquisition under first-dev-consistent
commitment**, driven by two things:
- (a) the within-class enumeration order at a budget covering a small fraction of the witness class, a horizon
  lottery that red-team M1 and M3 predicted pre-data (`REDTEAM_E2_E3KP_PREFREEZE.md:47-155`);
- (b) an extraction rule that is not invariant to semantics-preserving refactoring.

World-level dev underdetermination is real in 1 of 4 units (Wc025415a p0), and even there order decides.

**What the evidence does NOT support:** "stepping-stone identifiability at the world / ruler level" as the first
demonstrated failure.

### F4 -- MAJOR -- The headline drops "or-HORIZON" from the frozen mapping; the E3-ID data concede the horizon, and that horizon would have triggered the single pre-registered repair

- **The drop.**
  - ID-A1.4 maps UNIQUE_WRONG to "WORLD / RULER-**or-HORIZON**".
  - The W03 report (`W03_DEV_REPORT.md:46-47`) and the commit message `eb1048f28` state "world / ruler" only.
  - That is a label stated stronger than its frozen definition.
- **The concession.** ID-A1.4's own text says "the sealed class is beyond the R1 horizon". For the 3 refactoring units,
  the sealed-form program is in the size-8 class that was not completed (complete_through_size 7).
- **The counterfactual.**
  - Had these 3 units been labelled as horizon cases, the not-qualified families would show horizons in 6 of 8
    (F045, F033, F047, F052, F055 + F046). That is a strict majority, which fires the pre-registered OE trigger
    (A1-A.5, A3.3; `E2_E3KP_PREREG.md:104-109, 225`). The development pilot of that repair was 7/7.
  - The frozen label precedence (`e3_known_positive.py:563-569`) makes any chain with a probe-disagreeing stone
    UNDERDETERMINED_STONE before horizon is considered. So the precedence, not the data, decided that the repair did
    not run.
- **This does not change TFS1_INSTRUMENT_QUALIFIED = NO.** The frozen rules were applied as written.
- **It does falsify** W03_DEV_REPORT.md:24, "The pre-data prediction was wrong in mechanism: horizon-dominated was
  predicted; underdetermination-dominated was observed". The prediction (`E2_E3KP_PREREG.md:94-95`: about 4-7/15;
  1e6 covers about 7% of the size-8 class) was essentially right in mechanism and right in count. The label taxonomy
  renamed in-class horizon outcomes as underdetermination.

### F5 -- MAJOR -- "Composition is reachable given true stones (14/15)" is selection-conditioned and order-fragile

- **Selection.**
  - E1 admission rule 3(c)-(d) (`windows/E1_V2_RULES.md:19-25`) admitted an R3/R4 family ONLY IF the foundry's own
    found stones composed into a qualified solution within 1e6.
  - The 15 families are therefore the foundry chain's winners. Unconditionally, the foundry acquired 29/59
    mechanisms (red-team M1); CHAIN_C_FAIL dominates the R3-R5 rejections (`E1_ADDENDUM_D.md:38-40`).
  - The given-foundry row is a cross-implementation REPLICATION of the admission criterion: valuable as a
    conformance-like check of TFS-1's composition step, but not independent evidence that composition is reachable
    from correct stones in general.
  - The TFS-1 vs foundry contrast (7/15 vs 14/15) is a regression-to-the-mean design that M1 flagged pre-data.
- **Order fragility (reviewer re-computation, s3.2).**
  - Exploratory reviewer re-computation: give TFS-1 behaviourally sealed-equivalent stones that differ only
    syntactically from the foundry's. Of 5 such families, 2 qualify (F033, F055). The 3 guard_p / post_fold families
    are NOT found at 1e6 (COMPOSITION_HORIZON; complete_through_size < size_promoted_form).
  - In the foundry row the guard_p families were solved at charges 606,927, 678,844 and 956,941, i.e. 61-96% of the
    budget.
  - The 14/15 includes a favourable within-class draw on about 4 families (M3 put P at about 0.5-0.7 each).
- **Render the claim as:** "in this cell, on the 15 foundry-selected families, with the foundry's stones, 14/15
  qualified at 1e6; 4 of these sit in a partially covered size class".
  - `PHASE3_WIND_TUNNEL_INTERFACE.md:65` already uses roughly this form.
  - W03:47 ("Composition is reachable given true stones") and the ledger (18:55Z) do not.
  - This is a generalisation beyond the motif set (red-team M12.5).

### F6 -- MAJOR -- Every one of the 7 primary successes depends on the foundry-derived readout fallback; every closed-lambda f-stone in the primary is wrong

- In the primary row, all 7 chain-qualified families used an f-stone extracted by `readout_fallback`, at agreement 1.0.
- All 3 f-stones extracted as `closed_lambda` (from map+reduce R1 programs) had agreement 0.0-0.0123.
- Fallback-off gives 0/15.
- So TFS-1's acquisition works only on the R1 template `f(readout(xs))`, which red-team M2 flagged as a designed
  motif. On map+reduce R1 families it fails whenever the enumerator lands on a hoisted variant first.
- This is a DEVELOPMENTAL-MACHINERY (extraction / promotion) fact. It should be in the first-failure statement.

### F7 -- MAJOR -- ID_RETENTION_REPAIR = NO has zero discriminating power on the UD units

- All 4 UD units have n_classes = 1 within 1e6 (`runs/id_production/ID_*.json`, id1). RETAIN-4 therefore holds exactly
  the RETAIN-1 stone for them, and the designated row is identical to RETAIN-1 (7/15).
- The only change in any RETAIN row comes from the certifier-assisted secondary: RETAIN-2/4-CERT give 9/15, via
  Wc025415a F011, where the class set is AMBIGUOUS and the sealed class is rank 2. That is the one genuine dev
  underdetermination.
- "Retention of hypotheses does not repair" (CAMPAIGN_STATE.json:189) is therefore not tested for 3 of 4 units.
- Retention across keyed restarts WOULD have contained a sealed-equivalent stone for all 4 units (F3). That is a
  post-hoc observation, not a claim.

### F8 -- MAJOR -- ID-A1.4 was written with the KP production stones in view, and it steered the interpretation away from the pre-registered INSTRUMENT branch

- **Timing.** The draft (`767ee7adf`, 19:03:29Z) and ID-A1 (`3f18a96bc`, 19:04:54Z) both post-date the KP primary
  (17:49Z), whose result files already showed agreement 0.0 for the 3 refactoring units.
- **The pilot did not motivate it.** The exposed pilot (`tfs1/e3/runs/ID_W0467897d.json`, `ID_W1d5301d0.json`) had
  NO unique-and-wrong unit: all 4 pilot UNIQUE units were sealed-equivalent. So the UNIQUE_WRONG edge case was not
  pilot-driven.
- **It was pre-data for E3-ID production,** and the draft map genuinely conflated "unique and right" with "unique and
  wrong". A clarification was legitimate.
- **But the mapping it chose (not INSTRUMENT) is the decisive interpretive step.** Its stated premise is falsified
  (F2).
- **The freeze is internally inconsistent.** The frozen code prints INSTRUMENT (`ID_POOLED_B1000000.json`
  "interpretation"), while the frozen text maps to WORLD/RULER-or-HORIZON. The frozen prereg's first line still reads
  "DRAFT, NOT FROZEN" (`E3ID_PREREG.md:1`).
- **Not a post-data relabel in the strict sense, but a relabel informed by related production data.** The synthesis
  should report both readings and the evidence of F2 and F3.

### F9 -- MAJOR -- The PHASE3 proposal promotes IDENTIFIABILITY on a mis-attributed calibration case

`PHASE3_WIND_TUNNEL_INTERFACE.md:68` proposes "Stepping-stone IDENTIFIABILITY" as a new qualification question with
E3-ID as its calibration case.

- On the evidence (F2, F3), 3 of the 4 calibration units are extraction-boundary + enumeration-order cases.
- A wind-tunnel question worth proposing instead is **STONE-BOUNDARY INVARIANCE**: is the extracted mechanism
  invariant under semantics-preserving refactorings of the found program? Report it separately from genuine dev
  identifiability (the Wc025415a p0 type).

### F10 -- MAJOR (process / custody) -- Ledger and freeze "utc" stamps run up to 51 min ahead of the commits that contain them

| Commit | Commit time | Ledger entries it already contains | Offset |
|---|---|---|---|
| `6cfb02579` | 17:11:57Z | 17:20Z, 17:24Z, 17:27Z | +8 to +15 min |
| `19f2b08fa` | 17:49:10Z | RESULT stamped 18:40Z | +51 min |

- FREEZE_E3KP.json `"utc": "2026-10-10T18:05Z"` is 36 min after its own commit and **16 min after the KP primary
  result commit**. An auditor reading only the freeze file would conclude the freeze post-dates its result.
- The ledger note (19:04Z) calls these "estimates a few minutes ahead". That understates them.
- The FREEZE_E3ID stamp was corrected; FREEZE_E3KP was not.
- Substance is unaffected (the DAG order is correct, F1).
- **Recommended:**
  - correct the FREEZE_E3KP utc;
  - derive every ledger utc from `git log -1 --format=%cI` or the system clock;
  - write wall-clock start/end into every result file.

### F11 -- MINOR -- Red-team items not fully closed by A1-A3

Checked against `reviews/REDTEAM_E2_E3KP_PREFREEZE.md`:
- **B1-B4:** adopted in A1-B / A2.
- **B5:** partly. The pooled verdict and docstring were fixed, but the recommended "scratch fails ALL" was replaced by
  >= 80% with all reported. Moot: 15/15.
- **M1:** (a)-(d) adopted, but the selection / regression-to-the-mean point is **not carried into the
  interpretation** (F5).
- **M2:** the organism-promotion alignment is moot while KP = NO. It must be resolved before any 2x2: the E3 organism
  has no readout fallback, and all 7 KP passes used it.
- **M3:** seeds were added, but their order-sensitivity evidence was **not used** in the E3-ID reading (F3).
- **M6:** the fresh FINAL tribunal was adopted for E2 only. E3-KP judges on the same evaluator test + tribunal that
  the foundry admission used.
- **M10:** the O-item renumbering was not done. The O2 premise ("max size 20 >= witness sizes") remains false for 5
  atlas R2 families. It is handled operationally by A2.6 (LIBRARY_UNAVAILABLE), but the frozen text is unchanged.
- **M1 MINOR:** the R3 vs R4 separate report and the agreement on the shifted R4 range are not in the pooled outputs.
- **M7, M8, M9, M11, M12, M13:** adopted.

### F12 -- MINOR -- FRONTIER_ARCHIVE_EFFECT vocabulary

- INCONCLUSIVE_CENSORED follows A1-B.6 / A2.3 and is correct as frozen.
- But the cause is the INSTRUMENT (the descriptor failed qualification on 3/5 clusters), not ambiguous data.
- The directive offers INSTRUMENT_UNVALIDATED. Suggested final rendering: "INCONCLUSIVE (INCONCLUSIVE_CENSORED; the
  descriptor is INSTRUMENT_UNVALIDATED on 10/15 families, 3/5 clusters)".
- The design itself had power 0 whenever any one of the 5 clusters was censored. A2.9 and the projection's
  power_notes disclosed this.

### F13 -- MINOR -- Internal inconsistencies in the record

- **Pilot labels disagree.**
  - A3 (`E2_E3KP_PREREG.md:243`) says the development pilot primary was 3/7 "all failures horizons".
  - The W02 report and ledger 15:21Z say the failing pilot stone was "under-determined (x > 3 vs x > 4)".
- **CAMPAIGN_STATE pending list.** `contract_decisions_pending` still lists items that A3 later ruled on.

### F14 -- (verification) -- Compute accounting is plausible; the worker cap cannot be fully verified

**Measured from result files:**

| Item | Measured | Estimate in the record |
|---|---|---|
| KP, all rows, unique searches | 8,206 CPU-s, about 2.3 core-h | 2-3 + 2-3 |
| E3-ID production | 1,368 CPU-s, 0.38 core-h | 2-4 |
| E3-ID pilot | 586 CPU-s | -- |
| Foundry production (QUALIFICATION + CHAIN + ABLATION) | about 5.5 core-h | about 3.6 (Addendum D) |
| E2 screen at 445/720 | about 9 core-h, projected | -- |

The "about 33 core-h by 21:29Z" figure is consistent, and well under 48 / 24 h.

**Worker cap.**
- The ledger records <= 4 workers at each launch.
- The SUBSTRATE lead's E3-ID pilot (1 worker) has no timestamp. If it overlapped the KP secondaries (2) + E2 (2)
  between 17:49 and 18:43Z, the total was 5. **Not verifiable** from the record.
- Two process defects are already self-reported (a killed sibling PID; 3 lead workers for about 10 min).

---

## 3. Re-computations (reviewer scratch; EXPLORATORY; 1 worker)

### 3.1 Global equivalence of the seed-0 R1 programs

See the table in F2: 20,402 inputs per unit, interpreter B.

### 3.2 Chain search with refactoring-invariant stones

- **Stones.** Derived from the SAME seed-0 R1 programs by a "readout of a map" abstraction: `(red (map (lam x B) xs))`
  maps to B. All three equal the sealed mechanism (probe agreement 1.0):
  - `(lam x (add 2 (pow x 2)))`;
  - `(lam x (sub 1 (mul x x)))`;
  - `(lam x (mul 3 (mul x x)))`.
- **Run.** `KP.run_chain` with the PRIMARY config (B = 1e6, seed 0), in memory only.
- **Script:** reviewer scratch `b04/readout_map_diag.py`, not committed. About 133 CPU-s.

| Family | Result | complete_through / promoted size |
|---|---|---|
| W6eb945cc-F033-R3 | **SOLVED** (test + tribunal), charge 86,345 | 6 / 9 |
| Wb49b6a5f-F055-R4 | **SOLVED**, charge 64,157 | 6 / 7 |
| W483b8c31-F045-R3 (guard_p) | NOT_FOUND at 1e6 (COMPOSITION_HORIZON) | 7 / 8 |
| Wb49b6a5f-F052-R4 (guard_p) | NOT_FOUND at 1e6 (COMPOSITION_HORIZON) | 7 / 8 |
| W6eb945cc-F047-R3 (post_fold) | NOT_FOUND at 1e6 (COMPOSITION_HORIZON) | 6 / 7 |

**Reading (exploratory).**
- With the extraction defect removed, the primary would be about 9/15, still below 12.
- The residual failures would be:
  - horizons: R1 1 + composition 3;
  - dev underdetermination: 2 families via Wc025415a p0.
- **Horizon (search) is the dominant residual constraint.** Extraction is the dominant cause of the UD labels.
  World-level underdetermination is a minority contributor.
- This is post-hoc. It relabels nothing and must not be read as a repair of E3-KP.

---

## 4. Recommendation and first demonstrated failure (reviewer's own answer)

### Recommendation: **CHANGE_SEARCH_OR_DEVELOPMENTAL_MACHINERY**

TFS-1 is retained as the representation; it does not continue on the current search and developmental machinery. The
plan's frozen gate (E3 FAIL stops the line) bars CONTINUE_TFS1 as is.

### First demonstrated failure in the causal chain

Stepping-stone **ACQUISITION** by enumerative base search with first-dev-consistent commitment. It has three
components:
1. **Search.** A within-size-class enumeration lottery at a 1e6 budget covering about 7% of the Int size-8 class.
   This is the R1 horizon. It explains HORIZON_R1 and, in different seeds, the same units' failures.
2. **Developmental machinery.** A stone-extraction rule that is not invariant to semantics-preserving refactoring.
   It explains 3 of 4 UD units. Fallback-off gives 0/15; every closed-lambda f-stone in the primary is wrong.
3. **World.** A genuine dev-identifiability gap in 1 of 4 units (Wc025415a p0: no element 5 in dev).

**The same link also dominates E1's shortfall.** The foundry's own base search failed to acquire stones (CHAIN_C_FAIL
is the dominant R3-R5 rejection; s-mechanisms are almost never acquired), and that is what left only 2 kind
pairings. So E1 = NO and E3-KP = NO share their first failing link.

**Composition from correct stones is not demonstrated to fail.** It is demonstrated to succeed on a foundry-selected
set, with a horizon lottery on guard_p / post_fold.

**Archive effects and development are untested** (censored / gated).

### Concrete next steps (each needs a NEW pre-registration; none relabels Beta-04)

- (i) The already pre-registered OE pruning.
- (ii) Multi-key restarts with hypothesis retention across restarts.
- (iii) A refactoring-invariant (behavioural) stone extraction, e.g. readout-of-map.
- (iv) Foundry-side: an identifiability check of R1 dev sets (boundary elements present), reported as a WORLD
  qualification item, separately from (iii).

### Strongest counter-arguments

- **MIGRATE_TO_ALTERNATIVE_REPRESENTATION.**
  - The extraction failure is intrinsic to "a mechanism is a syntactic lambda subterm". The representation itself
    makes the mechanism boundary non-canonical.
  - The only successes needed a motif-specific readout hack (fallback-off 0/15).
  - The foundry, an independent enumerator over the same typed-term family, also fails stone acquisition on about
    half of all mechanisms.
  - A representation whose mechanisms are behaviourally defined might not have this failure mode.
  - Rebuttal: a behavioural extraction inside TFS-1 removes it in the 3 cases tested (s3.2). The binding residual is
    search horizon, which a representation change does not obviously fix. The AR-1 pilot was 0/7, with links UD 4 /
    HORIZON 3. Pending its production result, the alien path shows the same two links.
- **WORLD / RULER (the coordinator's reading).**
  - The sealed decomposition is a ruler convention. A world whose R1 families allow reducer-commuting refactorings
    does not pin the mechanism boundary, so the fix belongs in the foundry: R1 families that force the boundary.
  - This is a coherent position. It is preserved in s6.
  - But it cannot be the "first demonstrated" failure: the same R1 data yielded the sealed-equivalent stone under
    other keys (F3), and the R1 behaviour determines f exactly (F2).

---

## 5. Items the reviewer could NOT check

- **E2 screen and analyzer outputs** (credit labels, REACHABILITY_ATLAS_COMPLETE). Pending; not yet on main.
- **AR-1 alien production.** Pending.
- **Wall-clock run start / end** for KP and E3-ID. There are no timestamps in the result files, so pre-freeze
  execution cannot be positively excluded. Only DAG order plus CPU-time feasibility were checked (F1).
- **Worker concurrency** during 17:49-19:03Z (F14).
- **Whether OE pruning would have changed the primary.** Not run: it is the coordinator's single registered repair,
  and running it here would pre-empt it.
- **Foundry generator internals** (generator.py world construction) beyond the chain_c / chain_d / acquisition code
  paths.
- **K-AB conformance re-run.** Its reported receipt was accepted.

---

## 6. Disagreements preserved (not resolved)

1. **First failure.**
   - Coordinator: WORLD / RULER identifiability of stepping stones.
   - Reviewer: ACQUISITION, i.e. search horizon + extraction non-invariance, with world dev-gaps a minority.
   - Both sides agree TFS1_INSTRUMENT_QUALIFIED = NO stands.
2. **ID-A1.4.**
   - Coordinator: a legitimate pre-data clarification.
   - Reviewer: pre-data for E3-ID, but written with the KP production stones in view; its causal premise is falsified
     by data. The pre-amendment INSTRUMENT branch fits 3 of 4 units.
3. **"Composition reachable given true stones."**
   - Coordinator: shown (14/15).
   - Reviewer: shown only on a foundry-selected set, and order-fragile on about 4 families.
4. **Recommendation.**
   - Reviewer: CHANGE_SEARCH_OR_DEVELOPMENTAL_MACHINERY.
   - A MIGRATE reading has a non-trivial case (s4). It should be re-examined once AR-1 production is in.
