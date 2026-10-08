# O1 repair: observation of promoted applications (Beta-03, qualification on EXPOSED W9-H pilot data)

Representation lead. Branch `aphrodite/b03-w5p`. Exposed data only: W9-H pilot seeds 0-2, which the ecology lead's
discovery pilot already used. Nothing here is confirmatory.

## 0. Frozen before any O1 run (committed before the runs; see git history of this file)

### 0.1 Design

O1 is the donor option `donor_w5p(..., o1=True)`. It defaults to **OFF**.

- **O1 entry.** For every ORDERED pair (Q, P) of promoted primitives in the donor's registry, Q == P included and
  taken in id order, form the promoted-form schema `Q.schema[{H} := P({H})]`. The entry's bodies are the
  **W5P instantiations** of these schemas: the same `promote.instantiate` filler set (LEVEL1 + P(atom)) and the
  same depth/shape rule every W5P candidate entry uses. Bodies already present in a START entry are dropped,
  because the ordinary walk covers them. inits = H1 and finals = FINAL_SPACE, as `a17.schema_entry`.
- **Where the contexts come from.** They are the arm's OWN promoted schemas, which are the only one-hole contexts
  an arm possesses. No generic context set, no motif and no truth enters. An empty registry (pristine, gen-1)
  gives no entry, no walk and no charge, so O1 is a no-op for pristine.
- **Placement: a deviation from the letter of the request, decided on arithmetic before any run.** For the
  oracle start, the START library holds 6 × 57,960 + 151,920 = **499,680** candidates per observation walk. An O1
  entry placed "after the start entries, before the W5 fallback" inside the same walk therefore begins at
  candidate 499,681. At escrow 300k (or 30k) it is **never reached**, so that literal variant is identical to
  O1-off by arithmetic. O1 is implemented instead as follows:
  - After each ordinary observation walk, a **second walk per observation cell** is made over the O1 entry ONLY,
    with no fallback.
  - It uses the **same escrow value** (`a17.ESCROW`), the same max-hits and the standard keyed order and charge
    rule (`walk.iter_hits`, which is conformant to `fair.search_collect` and `a18.fast_cost`).
  - Its hits join the observations.
  - The ordinary observation walk is untouched, so every O1-off observation is still made.
  - Charges go to `meta_charges` and to both cost ledgers (phase `observe_o1`).
- **Size.** Oracle-start O1 entries hold 1,214 / 1,224 / 1,242 bodies on seeds 0 / 1 / 2, which is
  437,040 / 440,640 / 447,120 candidates. A 300k walk with no hit covers about 68% of it.
- **Everything downstream is unchanged:** certification (coverage = START), W5P derivation, candidates and
  selection.

### 0.2 Qualification protocol

- **Runner and roles.** The ecology lead's runner and roles: `w9h_pilot_discovery.py`, `discovery/ROLES.json`
  (W9H-R1).
- **Known-positive gen-2 control.** START = the seed's 6 TRUE level-1 mechanisms (`oracle_start`), then PRISTINE.
  Rule g11 (g10 minus MEMORISE), promotion ON, **o1=True**, escrow **300k** for observation, the O1 walk and
  `Cell.cost`. Seeds 0, 1, 2. At most 2 workers, `OMP_NUM_THREADS=1`.
- **Secondary runs** (reported, not part of the criterion):
  - the same at escrow 30k;
  - gen-1 (pristine start, 30k) with o1=True, which is expected to be byte-equal to the recorded `gen1_30k` rows on
    every output key.
- **Truth timing.** Truth (`W9H_TRUTH.json`) is read only by the scorer, after the donors have run.

### 0.3 PASS criterion (frozen)

A seed PASSES iff ALL of the following hold for the 300k O1 oracle donor.

- **(S1) Non-trivial depth-2 selection.** The selected schema contains a promoted node, `dag_depth_selected >= 2`,
  and it is not a bare `P_x({H})`.
- **(S2) Matches a true composition.** The selected schema equals a TRUE composition `S_b ∘ S_a` of that seed, up
  to W5 canonicalisation. That means either of:
  - `identity.normalise(parse(expansion))` equals the same for the truth composition schema, with `{H}` as one
    variable; or
  - its W5P instantiation set equals the W5P instantiation set of `P_b-schema[{H} := P_a({H})]` under the run's
    registry.
- **(S3) Transfer.** The selected library (`selected_entries`) reaches at least 1 of the seed's admitted L2
  families, where reaching means:
  - in ≥ 1 of the 2 W9H-tx cells;
  - cap 1M, T4 v1a qualifier (`w9h_admit.walk_cell`);
  - with a first qualified program whose body is **outside G5**;
  - on a family PRISTINE reaches in **0** of the same cells (`W9H_FOUNDRY` `PRISTINE_TX`).
  - Transfer walks are run only for seeds that pass S1 and S2. This is cost control, declared here.

**O1_QUALIFIES** iff ≥ 2 of 3 seeds PASS **and** total CPU for this task ≤ 2.0 core-h. Otherwise **O1_FAILS**.

The first broken link is reported as the earliest failing stage on the majority of seeds:
- **CANDIDACY:** no derived schema satisfies S2;
- **SELECTION:** one does, but it was not selected (S1 + S2 fail);
- **TRANSFER:** S3 fails;
- **BUDGET:** CPU exceeds 2.0 core-h.

No parameter is tuned after the outcome is seen.

## 1. No-op proof (O1 OFF is the frozen E5-N path)

- **Code.** With `o1=False` (the default), `o1_entry` is never called, no O1 walk runs, and no `o1` key is added
  to the output. The only code change on the OFF path is a `None` check.
- **NO-OP CONTINUITY, re-run on this commit with O1 OFF: PASS.** It reproduces Beta-01 T12 seed 17 rows exactly
  for g11@O10 and g0@O4 (selected_schema, selected_origin, selected_entries, n_observed, n_derived, classes).
  Record: `o1_runs/NOOP_T12_O1OFF.json`; 248 CPU s.
- **Fast suite: 10/10 PASS** (`W5P_TEST_RESULTS_FAST.json`). This includes the new `O1_ENTRY_WALK` test:
  - an empty registry gives no entry;
  - the O1 walk equals `fair.search_collect` over the same entry and cap: 24 cells, 8 with hits, 0 mismatches.
- **O1 ON with an empty registry (gen-1, pristine start, 30k, seeds 0-2): byte-equal** to the eco lead's recorded
  `gen1_30k` rows on selected, selected_schema, selected_entries, n_observed, n_derived, classes and meta_charges
  (3/3 seeds). As expected, gen-1 still derives nothing: observations 3 / 1 / 0, derived 0 / 0 / 0, O1 hits 0.
- **Ordinary observation is unchanged with O1 ON.** At 300k, the observation count equals the eco run's count
  plus the O1 hits on every seed: 24 + 21 = 45, 13 + 14 = 27, 16 + 1 = 17.

## 2. Qualification: known-positive gen-2 control, oracle start, g11, promotion ON, O1 ON, escrow 300k

| | seed 0 | seed 1 | seed 2 |
|---|---|---|---|
| O1 entry bodies / candidates | 1,214 / 437,040 | 1,224 / 440,640 | 1,242 / 447,120 |
| O1 hits (of 30 observation cells), by level | 21: L2 ×7 (C1 ×3, C0 ×4), L1 ×8, L0 ×6 | 14: L2 ×8 (C1 ×3, C2 ×5), L0 ×6 | 1: L2 ×1 (C2) |
| observed / classes / derived (with P) | 45 / 12 / 34 (15) | 27 / 13 / 19 (9) | 17 / 7 / 7 (3) |
| a TRUE composition among derived candidates (S2 test) | **no** | **yes**: C1 `P_b(P_a({H}))` and C2 | **no** |
| selected | `math.gcd(abs((1 - (acc * {H}))), abs(v))` (depth 1) | `P_acbd91eb902a({H})` = `({H} + v)`, a bare re-expression of an inherited mechanism | `((acc + {H}) + v)` = inherited mechanism (depth 1) |
| S1 non-trivial depth-2 selected | no | no (bare P) | no |
| S2 selected = true composition | no | no | no |
| S3 transfer | not run (S1/S2 fail, declared) | not run | not run |
| **seed PASS** | **no** | **no** | **no** |
| first failing link | CANDIDACY | SELECTION | CANDIDACY |
| search charges (meta) | 334.3M (O1 walks: 5.6M) | 185.5M (7.1M) | 115.1M (8.9M) |
| expanded / promoted exec units (overhead) | 3.54G / 2.72G (1.30) | 2.06G / 1.59G (1.29) | 1.25G / 0.95G (1.31) |
| CPU s | 1,398.7 | 637.3 | 419.8 |

**Seed 1 selection diagnostic.** This is a post-outcome re-run of the identical donor that keeps the selection
table, 630 CPU s. Its decision was identical: P_acbd({H}).
- The true composition **C1 `P_acbd(P_d6c1({H}))` was ELIGIBLE** under g11: mean paired saving 5,524, lower95
  −24,355.
- It lost to the re-expression `P_acbd({H})`, with mean saving 7,862, and to its plain twin `({H} + v)`, which
  has the same numbers.
- C2 `P_acbd(P_f3d7({H}))` had a negative saving (−3,933).

So on the one seed where O1 repaired candidacy, selection preferred re-spelling an inherited mechanism.

**Escrow 30k** (secondary, not part of the criterion): O1 hits 3 / 2 / 0. Depth-2 candidates with P: 2 / 1 / 2.
No true composition is a candidate. Selected: INHERITED / INHERITED / M0 (depth 1). CPU 238.6 / 62.2 / 122.0 s.

## 3. Verdict: **O1_FAILS**

- **0 of 3 seeds PASS.** The frozen criterion needs 2.
- **First broken link (majority): CANDIDACY**, on seeds 0 and 2.
  - O1 does make true level-2 families observable: 7 / 8 / 1 L2 observations.
  - But on seeds 0 and 2, LGG over the observed classes does not produce a true composition. The depth-2
    candidates are `P_outer(base-inner)` forms or nestings of one primitive.
  - On seed 2 the O1 walk hit only once, because the 300k escrow covers about 68% of the entry and the order
    within it is keyed.
- **On seed 1, candidacy was repaired and SELECTION broke.** C1 was a candidate and eligible, but g11 picked the
  bare re-expression `P({H})`, which has larger savings.
- **Budget was not the binding link:** 1.13 core-h total, within the 2.0 limit.

Not tested, and not claimed: whether excluding bare re-expression candidates would fix seed 1. Even if it did,
the result would be 1/3 seeds, below the frozen 2/3. No parameter was changed after the outcome.

**Defect found (bookkeeping, no effect on this verdict).** Promoting a bare `P_x({H})` schema records a new id
with depth 2, although it is only an alias of P_x. S1 excludes bare P, so the verdict is unaffected. If W5P is
used again, an alias should map to P_x (depth 1). This is not fixed here, because W5P is frozen for E5-N.

## 4. CPU used (`time.process_time` in workers; ≤ 2 workers; OMP_NUM_THREADS=1)

| item | CPU s |
|---|---|
| oracle 300k O1 donors ×3 (2 workers) | 2,455.8 |
| oracle 30k O1 donors ×3 | 422.8 |
| gen-1 30k O1 donors ×3 | 86.4 |
| seed-1 selection diagnostic (post-outcome) | 629.5 |
| T12 no-op continuity (O1 OFF) | 247.9 |
| fast test suite + O1 unit test + O1 entry sizing + scoring | ~200 (wall; not metered) |
| **total** | **≈ 4,040 s ≈ 1.12 core-h** (≤ 2.0) |

**Cost per donor.**
- At 300k, O1 adds 5.6-8.9M search charges for its own walks.
- The larger cost is downstream. More observations lead to more derived candidates (34 vs 26 on seed 0, 19 vs 9
  on seed 1). Each candidate is walked on 48 validation cells.
- Totals vs the eco run without O1:
  - seed 0: 334M vs 263M charges, 1,399 vs 1,120 CPU s;
  - seed 1: 186M vs 105M charges, 637 vs 395 CPU s;
  - seed 2: 115M vs 106M charges, 420 vs 347 CPU s.

## 5. Recommendation

Per the directive (*if the limitation cannot be repaired cheaply, stop*): **stop.**
- The cheapest arm-neutral observation repair does expose level-2 structure: 16 L2 observations over 3 seeds,
  where previously there were 0 true-composition candidates.
- But it does not turn that into a selected depth-2 abstraction in the known-positive control on any seed.
  Two links break: derivation (LGG produces the wrong generalisations on 2 seeds) and selection (re-expressions
  of inherited mechanisms outcompete the true composition on 1 seed).
- Fixing either needs more than an observation change: a different derivation (multi-hole / anti-unification
  over promoted forms) or a selection rule that penalises re-expression. Both are new design work.
- Do not launch E5-H. Record that W9-H depth-2 structure is certifiably reachable but not discoverable by this
  learner, even with oracle level-1 knowledge and O1 observation (option O3 in E5H_DESIGN_NOTES).

