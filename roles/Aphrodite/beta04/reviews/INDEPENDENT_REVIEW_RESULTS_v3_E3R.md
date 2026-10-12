# INDEPENDENT ADVERSARIAL REVIEW, v3: E3-R REPAIR-CLASS RESULT (C-015)

- **Reviewer:** the same independent role as v1 / v2. The reviewer produced none of the reviewed work.
- **Basis:** origin/main at `af407f28f`, merged into `aphrodite/b04-review`.
- **Compute:** 1 worker, OMP_NUM_THREADS=1, under 0.01 core-h. No production search. Scratch output only.
- **Severity scale:**
  - **BLOCKER:** a label or claim is wrong.
  - **MAJOR:** an interpretation is overstated, or an alternative is not excluded.
  - **MINOR:** everything else.

---

## 1. Verdict

- **REPAIR_CLASS = SEARCH (MAJORITY; unconditional; 0 censored) is a CORRECT application of the frozen rules.**
- **Custody is clean.**
- **The interpretive wording "pruning alone works" / "primary class SEARCH, extraction secondary" is OVERSTATED
  (MAJOR).**
  - The data support a SEARCH-led repair in which refactoring-invariant extraction is **co-required** for
    seed-robust qualification.
  - Every cell also rests on the foundry-derived readout fallback.
  - The recommendation should name both factors. The frozen label stays SEARCH.

---

## 2. Custody (all verified)

**Freeze before outputs.**

| Event | Commit | Time |
|---|---|---|
| Code build | `40fdf5eab` | 2026-10-11 00:00:00Z |
| FREEZE_E3R | `8efd1ae71` | 00:01:33Z (its `utc_written` 00:01Z agrees) |
| Result | `148b78c5a` | 13:34:02Z |

`40fdf5eab` is an ancestor of `8efd1ae71`, which is an ancestor of `148b78c5a`.

**Blob hashes.**
- All 29 FREEZE_E3R entries (16 code / prereg / red-team + 13 KP inputs) equal `git rev-parse 148b78c5a:<path>`.
- The 154 sha256 code hashes embedded in `runs/e3r_production/*.json` match the committed code: 0 mismatches,
  LF / CRLF.

**UTC fields (E3R-A1.10 / A2).**
- `E3R_RESULT.json` utc_start 11:30:12Z, utc_end 13:33:05Z. That is after the frozen not-before of 11:30Z and inside
  the ledger LAUNCH (11:36Z, commit 11:36:45Z) and RESULT (13:34Z, commit 13:34:45Z) entries.
- All 134 searches newly run in E3-R carry utc_start / utc_end. The earliest start is 11:30:13Z; the latest end is
  13:33:03Z.
- The other 226 searches in the KPA1 caches are reused from the frozen `runs/kp_production` (`seeded_from` recorded,
  with the source code hashes). They carry no UTC. That is acceptable as declared reuse.
- **The v1-F1 / v2 R-1 UTC item is now carried out.**

**Reproduction asserts.**
- off_frozen seed 0 = 7 / 15, equal to the frozen E3-KP pooled result: PASS.
- off_xabs = 9 / 15: REPRODUCED.
- The reused off_frozen seed-1 / seed-2 cells (9, 8) equal the frozen KP seed rows.

---

## 3. Re-derivations

### 3.1 Cells, per-seed labels, MAJORITY and attribution

Re-derived from the raw chain statuses in the 7 KPA1 files with the reviewer's own script (E3R-A1 / A3 rules):
`>= 12` means 5q >= 4n. LO scratch is 12 in the OE cells (12 FAILED + 3 NOT_RUN counted as not failed; 5 x 12 >= 60).

| Seed | off_frozen | off_xabs | on_frozen | on_xabs | Label | Attribution |
|---|---|---|---|---|---|---|
| 0 | 7 | 9 | **12** | 15 | SEARCH | OE-only 3, both-only 3, either 2 |
| 1 | 9 | 10 | 11 | 13 | BOTH_REQUIRED | OE-only 2, both-only 2, either 1, neither 1 |
| 2 | 8 | 8 | **12** | 13 | SEARCH | OE-only 5, neither 2 |

- **All of this matches E3R_RESULT.json exactly.** MAJORITY SEARCH (2 of 3) is confirmed.
- **Main effects and interaction re-derived:**
  - OE: 5.5 / 2.5 / 4.5;
  - X-ABS: 2.5 / 1.5 / 0.5;
  - interaction: **+1 at every seed**.
- X-ABS-only = 0 at every seed.

### 3.2 Independent spot-check of four qualified OE-cell families

Method:
- library rebuilt from the cell's unit lambdas (L_ ids match the runner's);
- dev consistency;
- evaluator test + tribunal;
- 2,000 random widened lists (|v| <= 60) against the sealed expanded witness.

| Family (cell, seed 0) | dev | test | tribunal | widened diff | OE scratch |
|---|---|---|---|---|---|
| W483b8c31-F046 (on_frozen) | ok | ok | ok | 0 / 2000 | NOT_FOUND_AT_BUDGET (complete through 8) |
| Wc025415a-F041 (on_frozen) | ok | ok | ok | 0 / 2000 | NOT_RUN (lazy; LO counts it as not failed) |
| W6eb945cc-F047 (on_xabs) | ok | ok | ok | 0 / 2000 | NOT_FOUND_AT_BUDGET |
| Wb49b6a5f-F055 (on_frozen) | ok | ok | ok | 0 / 2000 | NOT_RUN |

All four qualify as recorded.

---

## 4. Findings

### R3-1 -- MAJOR -- The SEARCH margin rests on lottery outcomes, including the one world dev-gap

on_frozen is exactly at the bar at seeds 0 and 2, and at 11 at seed 1. The per-unit records show what produced the
OE-cell successes.

**(a) Seed 0, Wc025415a-F041 and F044 (2 of the 5 OE rescues).**
- Under OE, R1 family F010's first dev-consistent program is `(gt (div x 2) 2)` (x >= 6), which fails the test.
- The certifier-guided retry moves to F011, whose first dev-consistent program under OE happens to be `x > 4`.
- Without OE it was `x > 5`.
- F011's dev set contains no 5 (v1 F2), so both are dev-consistent. OE changed which one comes first. It did not
  remove the ambiguity.
- These two families are lost again at seeds 1 and 2 (UD-R1).
- **Without them, seed 0's on_frozen would be 10 and the seed-0 label BOTH_REQUIRED. The majority would then be
  BOTH_REQUIRED.**

**(b) Seed 0, W6eb945cc-F033 and Wb49b6a5f-F055 (2 more).**
- They qualify in on_frozen with the MIS-CUT stones still in the library (`(mul x x)`, agreement 0.0 / 0.0123).
- The chain absorbed the missing part inline, near the end of the budget:
  - `(scanl (lam a (lam b (L_s a (sub 1 (L_f b))))) 1 xs)` at 951,260;
  - `(map (lam x (mul 3 (L_f x))) ...)` at 779,385.
- That is OE buying composition headroom, not fixing the stone.

**(c) Seed 2, F045 and F052 (OE-only).**
- Without OE, both units were HORIZON_R1 at seed 2. OE's coverage cured that horizon.
- The first dev-consistent program OE reached happened to be the un-hoisted form, so the stone was correct.
- At seed 0 the same OE coverage reached the HOISTED form for W483b8c31 f0 (`(add 2 (min (map (lam x (mul x x))
  xs)))`), giving the mis-cut `(mul x x)`.
- So the mis-cut was avoided by order, not repaired.

**(d) Genuine coverage gain.** Only W483b8c31-F046 at seed 0 (f1 found in F008 at 234,821, a former IN_CLASS
horizon) is clearly an R1-horizon cure by coverage.

**Conclusion.**
- OE's average effect is large and real.
- But "pruning alone qualifies" is decided by about one family per seed, and those families are reshuffled
  lotteries on the very defects (dev gap, mis-cut) that pruning does not address.

### R3-2 -- MAJOR -- The fallback-off check cannot detect dependence of a SEARCH label on the readout fallback

- A3.11 defines "fallback-off disagrees" as the seed-0 LO label changing when fallback-off on_xabs **replaces
  on_xabs**.
- The SEARCH rule reads only on_frozen and off_xabs. So the substitution cannot change a SEARCH label, and "agree" is
  vacuous.
- **The informative fact:** fallback-off on_xabs (both repairs on) is **9 / 15** (R1_ACQUISITION 6). Without the
  foundry-derived readout fallback, even OE + X-ABS fails the bar.
- Fallback-off on_frozen was not run. It is very likely <= 9.
- **So "OE alone works" is conditional on a second extraction rule: the readout fallback, a motif-specific
  DEVELOPMENTAL device (v1 F6).** This must be stated next to the label, not only in the claim limits.

### R3-3 -- MAJOR -- "Primary class SEARCH, extraction secondary" understates extraction

- **The only configuration at or above the bar at every seed is on_xabs: 15 / 13 / 13.**
- The OE x X-ABS interaction is positive at every seed (+1).
- At seed 1, X-ABS is required (BOTH_REQUIRED).
- At seed 0, 3 of 8 rescued families are both-only.
- Its residual failures are exactly the Wc025415a dev gap (UD-R1 2 at seeds 1 and 2).

"Extraction secondary" is accurate only in the narrow sense that OE has the larger main effect and is present in
every rescue (X-ABS-only = 0). Rendering X-ABS as optional is not supported.

### R3-4 -- MINOR -- X-ABS is in-sample by construction

- X-ABS was specified after inspecting these production failures. Its dual-reducer clause was added after seeing
  W6eb945cc (E3R-A1.2, disclosed).
- At seed 0 it fires on exactly the 3 known units.
- Its contribution is therefore not evidence of a general extraction method. The operator already requires
  confirmation on fresh families.
- Its first held-out-like firing in production is W6eb945cc / Wb49b6a5f at seeds 1-2, but those are the same units.

### R3-5 -- MINOR -- Declared deviations stand, and they matter

- Seeds 1 and 2 reuse the seed-0 OE scratch and the seed-0 non-OE scratch.
- OE scratch was NOT_RUN on 3 families (Wb49b6a5f-F055, Wc025415a-F041, F044). Two of those are the margin families
  of R3-1. LO correctly counts them as not failed, and scratch is then exactly 12 / 15: also at the bar.
- The SEARCH label is determined (LO = HI), but both of its conditions sit exactly at 60 >= 60.

### R3-6 -- MINOR -- Standing limits carry over unchanged

Oracle decomposition; certifier-guided R1 retry (2 retries per cell at seed 0, including the Wc025415a rescue);
foundry-selected families (v1 F5); no fresh tribunal (F11 / M6). `E3R_RESULT.json` claim_limits states these
correctly.

---

## 5. What SEARCH licenses under the operator's direction map

- **Which branch applies.** The operator's branches are "search pruning alone works" vs "both interventions work".
  - The frozen label selects the first.
  - The evidence (R3-1 to R3-3) is closer to the second: OE is the dominant and necessary factor, and seed-robust
    qualification needed OE + extraction invariance, on top of the readout fallback.
- **The first branch's instruction does not apply to X-ABS.** "Do not introduce additional representation complexity"
  should NOT be used to drop extraction work: X-ABS is developmental machinery, not representation.

**Recommended recommendation wording (reviewer):**

> **CHANGE_SEARCH_OR_DEVELOPMENTAL_MACHINERY.** Keep the TFS-1 representation.
>
> The frozen E3-R repair class is **SEARCH (MAJORITY 2/3; at the 12/15 bar on seeds 0 and 2, 11/15 on seed 1)**.
> Pre-registered observational-equivalence pruning is the dominant and necessary factor: it is present in every
> rescued family, and X-ABS-only rescues are 0.
>
> Seed-robust qualification was reached only with pruning PLUS a refactoring-invariant extraction (15/13/13; positive
> interaction at every seed). Every cell relies on the foundry-derived readout fallback (fallback-off with both
> repairs: 9/15).
>
> The residual failure is a world dev-gap (Wc025415a p0).
>
> Next campaign:
> - search geometry first;
> - a generalized, target-blind extraction as a co-requirement;
> - fallback-disabled controls;
> - pruning costs accounted;
> - fresh, independently generated families;
> - stone discovery without a supplied decomposition.

The frozen label (SEARCH) is reported unchanged. The recommendation text names both factors.

---

## 6. Overclaim risks in the provisional SYNTHESIS.md

1. **Section 5 and `E3R_RESULT.json` "reading"** ("OE pruning alone qualifies the known-positive chain").
   - Qualify it: at 2 of 3 seeds, exactly at the bar, with the readout fallback ON, oracle decomposition and
     certifier-guided R1 retry.
   - Never "TFS-1 would have qualified": E3-R is not the A1-A.5 counterfactual repair, as the claim_limits already
     say.
2. **The A1-C fallback agreement.** Do not present it as robustness evidence (R3-2). Report fallback-off on_xabs
   9 / 15 as a dependence.
3. **The operator's ACQUISITION / UTILIZATION / AUTONOMY split is not yet in the draft.** Suggested content:

   | Dimension | Suggested content |
   |---|---|
   | ACQUISITION | Given decomposition + certifier retry + readout fallback: 7 / 15, rising to 15 / 13 / 13 with OE + X-ABS. Not independent discovery |
   | UTILIZATION | With given stones, 14 / 15 enumeration and 13 / 15 chain, on the selected set. With TFS-1's own stones after repair, as above |
   | AUTONOMY | Decomposition: coordinator / sealed. R1 retry: CERTIFIER. Readout fallback: foundry-derived DEVELOPMENTAL rule. X-ABS: designed post hoc on these failures. Pruning: SEARCH_INFRASTRUCTURE. Autonomy is low; no claim of discovery |

4. **Section 4 (AR-1): "proposed mechanisms the lambda grammar would not, e.g. a comparison-free predicate".**
   Unsupported as written. The TFS-1 grammar can express non-comparison predicates via eq / mod / gcd. Either cite
   the specific AR-1 program and show it is outside the TFS-1 size horizon, or drop the claim.
5. **Section 2 "search horizon = within-class order lottery".** Refine it with R3-1: OE's gain is partly coverage and
   partly reshuffling of the lottery; it does not remove the dev-gap or mis-cut defects.
6. **TFS1_INSTRUMENT_QUALIFIED row.** Keep it NO with no E3-R annotation suggesting it "would pass". The draft row is
   correct now.

---

## 7. Not checked

- **The X-ABS implementation** (`tfs1/e3/e3r.py`) against its prose beyond the fired units. Its before / after stones
  were checked against sealed agreement only.
- **The OE scratch internals** for the NOT_RUN families (by design).
- **Compute ledger** (2.84 core-h): accepted.
- **Seed-1 / seed-2 per-unit X-ABS firings:** not re-derived.
