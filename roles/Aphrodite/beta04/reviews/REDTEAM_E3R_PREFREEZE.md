# PRE-FREEZE RED TEAM: E3-R (windows/E3R_PREREG.md, draft at 91456b10b)

- **Red team:** an independent agent. It wrote none of E3-R, X-ABS, the runner, or the reviews it cites.
- **Basis:** `origin/aphrodite/b04-tfs1` at `91456b10b`, read in a detached worktree. The draft, s4D of
  `tfs1/e3/E3_RUNNER.md`, `e3_known_positive.py` (X-ABS, `--oe`, `--extract`, `--seed-cache-from`,
  `--scratch-cpu-cap`, `--repair-class`), `runs/kp_production/`, `runs/id_production/`, `tfs1/e3/runs/e3r_pilot/`,
  `E2_E3KP_PREREG.md` (A1-A, A1-C, A3), `FREEZE_E3KP.json`, the review and the coordinator response.
- **Compute used:** 1 worker, OMP_NUM_THREADS=1, about 4 CPU-s in total. There was no new search of any kind: the
  checks only extracted stones from stored programs and compared files. Scratch outputs are outside the repo.
- **Severity:** BLOCKER = the run would be uninterpretable or would not follow its own prereg; MAJOR = biased, forking,
  or open to over-claiming; MINOR = everything else.

## 0. Verdict: **FREEZE_WITH_AMENDMENTS**

The design is worth running: it is cheap, its factors are well defined in code, and it answers a question that is
actually open. But as drafted:
- the headline label has a realistic chance of being decided by **CPU censoring of the OE scratch control rather than
  by the data** (B1);
- the prereg text does **not** describe the X-ABS rule that the code implements (B2);
- **one of the four cells is already known exactly** (M1);
- **X-ABS has no held-out evidence at all** (M2);
- the label at one seed sits on an **order lottery** (M3).

Freeze only after amendments A1-A12 in s3. A1-A4 are required. A5-A12 are strongly recommended.

---

## 1. Red-team checks (exploratory; relabel nothing)

### 1.1 Held-out behaviour of X-ABS on every stored R1 program (no search)

`xabs_extract` and the frozen `extract_mechanism` were run on every stored R1 program whose mechanism is of kind f
(118 distinct (world, family, program) triples, 15 worlds):

| Source | Distinct programs |
|---|---|
| E3-KP production cache, qualified R1 hits, seed 0 / 1 / 2 (all rows) | 11 / 8 / 6 |
| E3-ID production: every dev-consistent hit in the R1 enumerations | 45 |
| Foundry `FINAL.jsonl` chain_c found programs (independent enumerator): 10 production worlds, 3 pilot_v2 worlds | 23 + 5 |
| Sealed R1 witnesses: 12 production worlds and 3 pilot_v2 worlds | 46 + 8 |

**Results:**
- **X-ABS has any candidate at all on exactly 4 programs.** They are the 3 seed-0 mis-cuts the reviewer identified
  (W483b8c31-F007, W6eb945cc-F006, Wb49b6a5f-F009), plus the seed-1 sibling W6eb945cc-F007
  `(sub 1 (max (map (lam x (mul x x)) xs)))`. That sibling is the same unit f0 and needs the dual reducer (min).
  On all 4, the X-ABS stone agrees with the sealed mechanism at 1.0, both narrow and wide.
- **On the other 114 programs X-ABS is a no-op.** It changed 0 frozen-correct stones, 0 foundry-found programs and
  0 sealed witnesses. None of the 54 sealed R1 f-witnesses has any context above the reducer; they are all
  `R(map f xs)` or `(map f xs)`.
  - Consequence (good): X-ABS **cannot** break the 7 primary successes. Their R1 programs are readout-fallback forms
    with no `R(map L xs)` node.
  - Consequence (bad): X-ABS has **zero held-out firings**. Every case it has ever fired on was in view when it was
    designed. Its only out-of-sample exposure will be the new OE R1 programs inside the on_xabs cell.
- **"Maximal absorption" is right only because of a foundry convention.** It is correct precisely because the foundry's
  R1 templates never place a context above the reducer. That is design-level knowledge of the ruler, read from the
  generator and sealed witnesses. It is not leakage at run time, but it should be stated.

### 1.2 The OE-off x X-ABS cell is already known

- **The stones are identical to the reviewer's.** The 3 X-ABS stones are, term for term, the reviewer's s3.2
  readout-of-map stones: `(lam x (add 2 (pow x 2)))`, `(lam x (sub 1 (mul x x)))` and `(lam x (mul 3 (mul x x)))`.
- **The rest of the cell is fixed.** The chain search is deterministic given (family, seed, library, oe, budget,
  max_size). All other units, R1 searches and scratch searches are imported from the frozen cache.
- **So the cell is determined.** The off_xabs cell is (up to a reproduction check) **9 / 15 with scratch 15 / 15**:
  F033 and Wb49b6a5f-F055 solved; F045, F052 and F047 COMPOSITION_HORIZON.
- **The draft understates this.** It lists this as a reviewer "projection" and "predicts" 8-10. It is not a
  prediction.
- **Two labels are unattainable before data.** Since off_xabs < 12 is known, **DEVELOPMENTAL and EITHER cannot occur**.
  REPAIR_CLASS reduces to:
  - SEARCH if on_frozen counts;
  - else BOTH_REQUIRED if on_xabs counts;
  - else NONE.

### 1.3 Seed noise in the frozen rows (OE off, X-FROZEN)

Per family over seeds 0 / 1 / 2 (7 / 9 / 8 qualified):

| Group | Families |
|---|---|
| Always qualified (6) | F040, W2bdef02f-F048, F051, F039, W480ffd54-F046, W480ffd54-F055 |
| Never qualified (4) | F045, W483b8c31-F046, F052, F041 |
| Seed-dependent (5) | F042 (2/3), F033, F047, Wb49b6a5f-F055, F044 (1/3 each) |

- **Five of 15 families flip with the keyed order.** Their first-failing-link labels also flip between
  UNDERDETERMINED_STONE and HORIZON across seeds.
- With predictions of 9-11 (on_frozen) and 11-14 (on_xabs) around a bar of 12, the seed-0 label is close to a coin
  toss over these lottery families.

### 1.4 Dev inputs used by the X-ABS validity check

- For all 118 production R1 families, `evaluator/<W>/<fid>.json` `dev` is byte-identical to the arm-view `dev`.
- X-ABS reads inputs only: no outputs, no test, no tribunal, no `input_dist`.
- So no leakage arises from where X-ABS reads its inputs.

### 1.5 OE scratch cost (pilot record, `e3r_pilot/KPA1_*.json`)

- **Non-OE scratch at complete_through 7:** OE scratch reached 8 at 140-160 CPU-s.
- **Non-OE scratch at complete_through 8:**
  - Int families: OE about 237 s;
  - List families: F071 and F077 about 237 s, F085 more than 1,500 s (CENSORED).
- **In production, 13 / 15 non-OE scratches completed size 8, and 13 / 15 families have List output.** On the pilot
  rate (1 slow in 3 List families), about 4 slow OE scratches are expected, with a wide range (roughly 1-8).
- **Escaping the scratch is hard.** The sealed base witnesses are size 13-19 and MAX_SIZE is 12. An OE scratch can
  succeed only through an equivalent program of size 12 or less, inside the class it reaches (about 9-10).

---

## 2. Findings

### B1 -- BLOCKER -- "CENSORED = not failed" (A3.6) is no longer conservative in a 2x2; it trivialises only the OE cells

- **How the rule biases.**
  - A cell counts only if scratch fails >= 12 / 15. CENSORED counts as not failed (code: `describe`,
    `repair_class_from`).
  - Only the OE cells re-run scratch. The OE-off cells inherit the complete non-OE scratch, which failed 15 / 15.
  - So censoring can disqualify only the SEARCH factor's cells. **Four** censored OE scratches make both OE cells
    TRIVIALISED **whatever their chain counts are**, and the label becomes NONE. s1.5 puts the expected number of
    slow OE scratches at about 4.
  - In E3-KP, A3.6 was "conservative toward FAIL" of one instrument verdict. Here the same rule is a
    factor-confounded bias toward NONE, and so toward the CHANGE_SEARCH (horizon) or WORLD/MIGRATE readings.
- **Uncapped is not an option either.** No cap at all (A3.6 as written) makes compute unbounded (M6).
- **The coordinator's alternative, using the frozen non-OE scratch (15 / 15) as the OE cells' control, is NOT more
  defensible as the primary control.**
  - The trivialisation check exists to show that a chain success is due to the stones.
  - A control run with a weaker enumerator than the chain's cannot show that.
  - It over-credits SEARCH exactly when OE alone solves a family.
  - A3.5 / s4B item 8 already ruled this, and E3_RUNNER s4A calls it "NOT recommended".
  - Structurally the risk is small (s1.5: size 12 or less is needed against witnesses of size 13-19), but that
    argument is post hoc and does not license changing the control.
- **Fix:** amendment A1 (bound reporting with a fixed cap, an envelope and lazy evaluation).

### B2 -- BLOCKER -- The prereg text and the implementation define different X-ABS rules

- **The draft's step 2 rewrites to `R(map L' xs)` with the SAME reducer R.**
  - Under that text, W6eb945cc f0 (`(sub 1 (min (map (lam x (mul x x)) xs)))`) has no valid candidate:
    min(1 - x^2) != 1 - min(x^2).
  - It therefore stays mis-cut, and F033 and F047 keep the wrong stone.
  - The code also tries the dual reducer (max <-> min), and the stone becomes correct.
- **Other unstated choices.** The text also leaves out:
  - probe lengths 0..max dev length;
  - list argument exactly `xs`;
  - no ancestor under a lambda;
  - "absorbed nodes" as the measure of "largest C";
  - the tie order.
- **Why this blocks.** Two readers would compute different off_xabs and on_xabs cells from the same freeze.
- **Fix:** amendment A2. Write the implemented rule into the prereg text, with the rulings in s4.

### M1 -- MAJOR -- One cell is known, so two labels are unattainable; the draft presents a replication as a test

- See s1.2. The "known before" item 1 must say what is actually known:
  - off_xabs = 9 / 15 (scratch 15 / 15) at seed 0;
  - DEVELOPMENTAL and EITHER are therefore impossible;
  - the experiment is effectively ONE factor (OE), with X-ABS as a modifier, read through the two OE cells.
- **The off_xabs "prediction (8-10)" must be deleted** or relabelled as a known value.
- Run off_xabs first, as a **reproduction check** of reviewer s3.2. A mismatch is itself a finding: nondeterminism or a
  different library.

### M2 -- MAJOR -- X-ABS was designed on the 3 failures and has zero held-out firings; the draft gives no discount rule

- **Where the design came from.**
  - The reducer set {max, min, head, last}, the dual reducer and "maximal absorption" were all chosen after the 3
    mis-cuts were seen.
  - The dual was added specifically for W6eb945cc.
- **The rule is principled, and the draft should say so.**
  - For a monotone context C, C(max S) = max C(S).
  - For an antitone context C, C(max S) = min C(S).
  - head and last commute with any C.
  - On singleton lists, R(map g [v]) = g(v), so any valid L' equals P([v]) on the probed range.
- **Its evidence base is still one motif on 3 units** (4 programs), all in view at design time (s1.1).
- **Required discounting language:**
  - **BOTH_REQUIRED:** must read "OE plus a post-hoc, single-motif extraction patch". It is NOT evidence that
    "developmental machinery" in general is the binding fix.
  - **SEARCH:** must report how many OE-cell R1 units X-ABS changed.
    - If X-ABS changes any unit in the OE cells, the extraction defect is still present and only masked by the new
      order. The reading is then "OE sufficient at seed 0; extraction non-invariance present but masked".
    - It must not be read as "extraction is fine".
  - **Out-of-sample firings:** the report must state X-ABS's firings in the OE cells that fall outside the 3 design
    units. These are its only out-of-sample firings, and they must be reported separately.

### M3 -- MAJOR -- At one seed the label is decided by a within-class order lottery; SEARCH vs BOTH_REQUIRED is not a property of the repair class

- **SEARCH vs BOTH_REQUIRED depends on the first hit in a new order.** At seed 0 the distinction turns on whether the
  OE R1 enumerator happens to hit a hoisted form first for the 3 units. That is a fresh draw from a new order (F3).
- **The bar sits inside the noise.** 5 / 15 families are seed-dependent at OE off (s1.3), and the predicted counts
  straddle the bar.
- **The bar answers a different question.** The 12 / 15 bar is an instrument-qualification bar, not a repair-class
  discriminator:
  - on_frozen = 11 with on_xabs = 12 gives BOTH_REQUIRED, although X-ABS added 1 family;
  - on_frozen = 12 gives SEARCH, even if on_xabs = 15.
- **Fix:** amendment A3. Seeds 1 and 2 for both OE cells become required for the label's stability. A per-family
  attribution table becomes the primary descriptive output.

### M4 -- MAJOR -- The interpretation map is lopsided, has a gap, and its NONE / UD branch confuses extraction gaps with world gaps

- **Lopsided.**
  - SEARCH, DEVELOPMENTAL, BOTH_REQUIRED and EITHER all map to CHANGE_SEARCH_OR_DEVELOPMENTAL_MACHINERY.
  - NONE with horizon-dominated links maps to CHANGE_SEARCH.
  - Given the draft's own prediction ("most likely BOTH_REQUIRED or NONE"), almost every likely outcome supports
    CHANGE_*.
  - E3-R cannot produce evidence against CHANGE_* except through NONE with UD-dominated links. After X-ABS, only
    Wc025415a p0 (2 families) is a known UD source, so that branch is improbable.
  - Not formally a pre-commitment, but the experiment **does not discriminate CHANGE from MIGRATE**. The prereg must
    say so.
  - NONE with horizon-dominated links is equally consistent with MIGRATE: the AR-1 pilot showed the same horizon
    link.
- **Gap.** NONE with MIXED links has no reading in the prereg. The code prints "no fixed reading".
- **UD confusion.**
  - UNDERDETERMINED_STONE covers two different things:
    - (a) the R1 program fails test (a dev gap: WORLD);
    - (b) a qualified R1 program whose extracted stone disagrees with the sealed mechanism (EXTRACTION).
  - Case (b) can still happen in the on_xabs cell whenever OE finds a refactoring shape that X-ABS does not cover,
    for example `(max (map g (map h xs)))`.
  - The draft maps UD-dominated links to "WORLD or MIGRATE". That would repeat the E3-ID error the review overturned
    (F2 / F8).
- **Fix:** amendment A4.

### M5 -- MAJOR -- Every success still rests on the readout fallback; A1-C is not addressed

- All 7 primary successes use readout-fallback stones, and fallback-off gives 0 / 15 (F6).
- E3-R keeps fallback ON in every cell and runs no fallback-off variant. Frozen A1-C says that when the fallback-on
  and fallback-off rows disagree, "the recommendation uses the fallback-OFF row". E3-R exists only to inform the
  recommendation.
- **Any positive REPAIR_CLASS is therefore conditional on a second motif-specific extraction rule** (foundry-derived).
- **Fix:** amendment A8.

### M6 -- MAJOR -- Compute: the 2-9 core-h projection has an unbounded tail, and there is no completion rule before the hard stop

- **Where the tail comes from.** The tail is OE scratch on List families (s1.5).
- **What OE scratch costs at different caps:**
  - Uncapped: unknown, possibly hours per search.
  - 3,600 CPU-s cap, about 4 slow searches: about 4 core-h of scratch.
  - Add OE R1 (about 17-34 searches at about 200 s, i.e. 1-2 core-h) and OE chains (2 cells x 15, at most about
    0.7 core-h).
- **Projected totals:**
  - Seed 0: about 6-8 core-h.
  - Seeds 1 and 2 for the OE cells (R1 + chains only, scratch from seed 0): about +4-5 core-h.
  - Total: about 10-13 core-h.
- **Feasibility:** within 48 / 24 h only if the concurrent E2 / AR-1 load is debited first. The window runs from
  2026-10-11 11:30Z to the hard stop at 2026-10-13 09:27Z (about 46 h). On 2 workers that is about 6-7 h of wall time,
  which is feasible.
- **Memory.** OE uses "several GB" per search.
- **Missing.**
  - The draft has no rule for what is reported if the run is incomplete at the hard stop.
  - `--scratch-cpu-cap` is labelled "development only" in the code.
  - A censored row counts as `complete`, but a skipped (lazy) one would not; the code needs a change for A1.

### M7 -- MAJOR -- "Best cell" selection is a forking path for the NONE reading

- The NONE reading uses the dominant link of the cell with the most qualified families. Ties are broken in the order
  on_xabs > on_frozen > off_xabs > off_frozen.
- So a 1-family difference can switch which cell's links are read.
- **Fix:** amendment A5. Read the on_xabs cell (both repairs applied) always.

### MINOR

- **m1. The "Known before" list is incomplete.** It should add:
  - the E3-R pilot readout (REPAIR_CLASS = SEARCH; X-ABS a no-op on the pilot), committed together with the draft;
  - the E2 result (`af3e7a0c5`, REACHED 13 / 15 with foundry stones);
  - the seed-1 / seed-2 unit texts (F3), including W6eb945cc-F007 seed 1, which motivated the dual reducer;
  - the fact that all sealed R1 f-witnesses are `R(map f xs)` or `(map f xs)` (s1.1).
- **m2. Dev source.** The dev inputs come from the evaluator files, which are identical to the arm view (s1.4). Add a
  run-time assert, or read the arm-view file.
- **m3. Probe set.** Add every singleton [v] for v in the dev element range to the X-ABS probe set. Singletons pin the
  stone exactly on that range (s M2). It is cheap and makes the check principled rather than random.
- **m4. Wall-clock times.** Result files still carry no wall-clock start / end UTC. `e3_known_positive.py` has no utc
  field, although the coordinator response (F1 / F10) committed to adding one. Add it before the run. Take every
  freeze / ledger utc from `date -u`.
- **m5. Freeze contents.** FREEZE_E3R should carry:
  - the git blobs: the new `e3_known_positive.py`; `enum.py` unchanged at `6ffd14bf`, as verified;
  - the reused-cell assert: off_frozen reproduces 7 / 15, scratch 15 / 15 and the frozen link counts.
- **m6. Report per cell:**
  - n_censored;
  - the X-ABS firing count and its units;
  - stone agreement before and after X-ABS;
  - certifier-assisted retries;
  - the UD sub-labels (A4).
- **m7. Priorities.** "Priority 3" is undefined. List the priorities explicitly (A3 / A8).
- **m8. Claim limits must say:**
  - A positive label does **not** open the E3 lifetime gate, which needs TFS1_INSTRUMENT_QUALIFIED = YES (still NO).
  - It is **not** the counterfactual A1-A.5 repair. The trigger did not fire, and E3-R must not be read as "TFS-1
    would have qualified".
  - The other limits stand: oracle decomposition (sealed-indexed R1 tasks); certifier-guided R1 retry; 15
    foundry-selected families (regression to the mean, F5); judging on the same test + tribunal as foundry admission
    (no fresh tribunal, F11 / M6).

---

## 3. Amendment list (concrete)

### Required before freeze

- **A1. OE scratch control: bounds, cap, envelope, lazy evaluation** (replaces A3.6 for E3-R only)
  1. Per-search cap of 3,600 CPU-s for every OE scratch, in the capped child process. Promote `--scratch-cpu-cap` from
     "development only" to frozen.
  2. CENSORED is a THIRD state, neither failed nor solved. Each cell is computed at both bounds:
     - **LO:** CENSORED counted as not failed;
     - **HI:** CENSORED counted as failed.
  3. If the bounds agree, the cell's status stands. If they disagree, the cell is COUNTS_CONDITIONAL.
     - A REPAIR_CLASS that depends on a conditional cell is reported as e.g.
       `SEARCH (CONDITIONAL: k OE scratches censored at 3,600 CPU-s)`.
     - The recommendation may not rest on the conditional part.
  4. Lazy evaluation. OE scratch is needed for the label only when an OE cell's chain count is >= 12.
     - Run all OE chains first.
     - If neither OE cell reaches 12, OE scratch is descriptive only (it may still run under the cap if the envelope
       allows).
     - If one does, run OE scratch in a fixed order: family_id order, Int-output families first.
     - Stop as soon as the bounds can no longer change the label.
     - The code must accept "not needed" as complete for the label.
  5. One pre-registered extension. If the label is bound-indeterminate, the censored searches that decide it may
     continue ONCE to 14,400 CPU-s each, within the envelope and before the hard stop.
  6. Envelope: at most 16 core-h for all E3-R OE scratch.
  7. The frozen non-OE scratch (15 / 15) is reported beside each cell as a weaker secondary control, never as the
     primary.
- **A2. X-ABS text = the implemented rule** (B2), with the rulings of s4. Include the monotone / antitone / singleton
  justification (M2) and the optional singleton probes (m3).
- **A3. Seeds and the per-family primary output** (M3)
  - Seeds 1 and 2 for BOTH OE cells are REQUIRED for the label's stability. Promote them from "priority 3" to
    "before reporting".
    - They re-key R1 and the chain.
    - The trivialisation check reuses the seed-0 OE scratch. Declare this as a deviation from the s4B item 10
      convention, made for compute.
  - Run off_xabs at seeds 1 and 2 too. This is cheap: the R1 searches are cached, and only changed-library chains
    are new.
  - The label is STABLE if all 3 seeds give it, MAJORITY if 2 of 3 do, and SEED_UNSTABLE otherwise.
  - The PRIMARY descriptive output is a per-family attribution table over the seed-0 failures. For each family it
    states whether the failure is fixed by:
    - OE alone;
    - X-ABS alone (already known: F033, Wb49b6a5f-F055);
    - both only;
    - either;
    - neither (with the residual link).
  - Report the OE and X-ABS main effects and their interaction (counts, per seed).
- **A4. Interpretation map rewritten** (M4)
  - State plainly: **E3-R discriminates repair class WITHIN TFS-1. It does not discriminate CHANGE vs MIGRATE.** That
    decision rests on AR-1 and on the synthesis.
  - Split UNDERDETERMINED_STONE into:
    - **UD-R1:** the R1 program fails test, i.e. a dev gap (WORLD);
    - **UD-EXTRACT:** a qualified R1 program whose stone disagrees with the sealed mechanism. Report whether the R1
      program is globally equivalent to the sealed R1 witness on a fixed random list set (the reviewer's F2 method).
  - **Only UD-R1** can point to WORLD (foundry identifiability). UD-EXTRACT in on_xabs points to DEVELOPMENTAL
    coverage. Neither of them, alone, points to MIGRATE.
  - **NONE with horizon-dominated links:** "no repair class identified at 1e6; the horizon remains binding". It is
    consistent with CHANGE_SEARCH (bigger search change) or MIGRATE. Not a CHANGE_SEARCH finding.
  - **NONE with MIXED links:** no repair class identified; the residual links are listed.

### Strongly recommended

- **A5. Fixed reading cell.** The NONE reading always uses the on_xabs cell; all four cells are reported (M7).
- **A6. Known-before list** completed (m1), including "off_xabs = 9 / 15 is known; DEVELOPMENTAL and EITHER are
  unattainable" (M1). Delete or relabel the off_xabs prediction. Run off_xabs first as a reproduction check of s3.2.
- **A7. Discount language and masking report for X-ABS** (M2).
- **A8. A1-C / fallback** (M5)
  - State that every label is conditional on the readout fallback.
  - As priority 2, after A3 and if the envelope allows, run on_xabs with fallback OFF. It shares the OE R1 searches;
    the new work is only the next-R1-family attempts and the chains.
  - If it disagrees with fallback-ON, report both. Per A1-C, the recommendation names the fallback-off row.
- **A9. Compute and stop rule** (M6)
  - Total envelope about 14 core-h, debited against the rolling cap together with any concurrent E2 / AR-1 load.
  - At most 2 workers, with the OE memory footprint checked before a second OE worker is started.
  - Run order:
    1. off_xabs (the reproduction check);
    2. the OE R1 searches, then the OE chains of both cells (seed 0);
    3. OE scratch, lazily (A1);
    4. seeds 1 and 2 (A3);
    5. fallback-off (A8).
  - If the hard stop (2026-10-13 09:27Z) arrives first, report what is complete. The label is computed only from
    complete required items, else REPAIR_CLASS = INCOMPLETE with bounds.
- **A10. Custody:** wall-clock start / end UTC written into every result file; FREEZE_E3R blobs; the reused-cell
  assert (m4, m5).
- **A11. Reporting fields per cell** (m6).
- **A12. Claim limits added** (m8).

---

## 4. Rulings recommended on the 9 open decisions

| # | Decision | Ruling | Reason |
|---|---|---|---|
| 1 | Dual reducer (min <-> max) in the validity rewrite | **ALLOW**; write it into the text (B2). | A sign-flipping (antitone) context turns max into min. That is a theorem, and validity is still checked behaviourally against P. Forbidding it would keep a known mis-cut for reasons of syntax only. Disclose that it was added after seeing W6eb945cc (M2). |
| 2 | Probe list lengths 0..max dev length | **ACCEPT**, and ADD all singletons over the dev element range (m3). | Value-or-FAIL on the empty list is a legitimate check. Singletons pin L'(v) = P([v]). |
| 3 | Only top-level `(map L xs)` nodes (list argument exactly xs, not under a lambda) | **ACCEPT.** | It matches the R1 f template `R(map f xs)` (s1.1). Derived lists such as `(map L (filter ..))` do not define an element-wise f-stone. Label any residual mis-cut of another shape UD-EXTRACT (A4). |
| 4 | "Largest C" = most absorbed nodes | **ACCEPT**; define it as "the highest valid ancestor on the path from R(N)". Across several N, the most absorbed wins, then the tie rule. | Per N the candidates form a chain, so the definitions coincide. No stored program has more than one N. |
| 5 | Tie order for the best cell | **REPLACE** with a fixed reading cell = on_xabs (A5). | A count-based choice is a forking path (M7). |
| 6 | "Dominated" = strict majority, else MIXED | **ACCEPT**, plus a frozen MIXED reading and the UD split (A4). | It is consistent with A3.3. MIXED currently has no reading. |
| 7 | X-ABS reads R1 dev inputs from the production evaluator files | **ACCEPT**, plus a run-time assert that they equal the arm view (or read the arm view directly). | Verified identical for 118 / 118 R1 families. Inputs only; the search already uses them. |
| 8 | OE cells re-run OE scratch (A3.5); CENSORED = not failed (A3.6) | **A3.5: ACCEPT. A3.6: REPLACE for E3-R** with bound reporting (A1). | In a 2x2, A3.6 penalises only the OE factor (B1). |
| 9 | Per-search CPU cap for OE scratch | **3,600 CPU-s, with CENSORED as a third state and LO / HI bounds, lazy evaluation, one 14,400 s extension for label-deciding searches, and a 16 core-h envelope.** **REJECT** the frozen non-OE scratch as the primary control; report it as secondary. | A weaker-enumerator control cannot attribute an OE chain success to the stones, and it over-credits SEARCH. "3,600 + not failed" trivialises the OE cells with real probability (s1.5). Bounds make the censoring visible instead of deciding the label. |

---

## 5. What a positive result may and may not claim (for the synthesis)

- **May claim:** "On 15 foundry-selected families, with oracle decomposition and certifier-guided R1 acquisition, and
  with the readout fallback ON, at seed(s) S:
  - pre-registered OE pruning [plus a post-hoc single-motif extraction patch] qualifies the known-positive chain at
    >= 12 / 15;
  - the repair class is <label> (<stability>)."
- **May not claim:**
  - TFS1_INSTRUMENT_QUALIFIED = YES, or any relabel of E3-KP;
  - an open E3 lifetime gate;
  - COMPOSITIONAL_DISCOVERY;
  - generality of X-ABS beyond the hoisted-reducer motif;
  - "developmental machinery is fine" (under SEARCH with X-ABS firing in the OE cells);
  - evidence for CHANGE over MIGRATE.
