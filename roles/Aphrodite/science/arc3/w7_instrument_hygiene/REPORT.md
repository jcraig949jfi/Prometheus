# ARC3 W7 -- INSTRUMENT HYGIENE (PKG-6 T4/dev alignment + Q2 beyond coverage; PKG-7 ruler v2.1)
(Deposited verbatim by the principal from worker W7's final message; the harness blocked the
worker's own Write of this file. Provenance: WORKER_MANIFEST.md row W7.)

Worker: W7 (ARC3, Aphrodite seat), host M4, worktree aphrodite-base-role, 2026-09-28.
FORENSIC / DRAFT ONLY. Nothing is adopted. No existing file was modified. Every instrument here
is a NEW-module draft for the principal to freeze or reject.
Compute: lease ff0752f9 (2 cores) and lease a43e47e7 (1 core). Both are released. All of my
python processes have exited.

## 0. HEADLINE

1. **The T4/dev query mismatch is small in the foundry and dominant among spurious hits.**
   - Over 644 T4-qualified families (C2 = A19: 283; C3 = A20: 361):
     - 11 families (1.7%) have a dev-domain-equivalent PRISTINE/L1 program that T4 v1 rejects
       only because of query 1 or 2.
     - 31 of 2,721 dev-equivalent programs (1.1%) are such artifacts.
     - All 31 fail T4 v1 and pass the v1a draft.
   - Exactly 3 families flip their frozen pilot p. All three are p=0 families that are
     unsolvable by construction under v1:
     - C2 qbda: p_PRISTINE 0 -> 1, p_L1 0 -> 1.
     - C2 qoja: p_PRISTINE 0 -> 1, p_L1 0 -> 0.75.
     - C3 cgfa: p_PRISTINE 0 -> 1, p_L1 0 -> 1.
     In each of them, every program in the equivalence class inside coverage is a query-1/2
     artifact.
   - At the frozen 250k escrow, 12 of the 13 T4-failing PRISTINE first hits (92%) are
     query-1/2 artifacts, and 11 of 15 for L1 (73%). Inside the escrow, the "spurious hit"
     channel is mostly T4's domain, not Q2's identifiability.

2. **Fix (a) changes far fewer frozen results than fix (b), and fix (b) does not work.** Fix (a)
   is T4 v1a with counterexample queries 3..97; fix (b) widens the dev/Q2 query draw to 1..97.
   - (b) re-draws every dev set: 0/400 tasks are identical to the old stream.
   - (b) changed Q2 sizes in 4/30 control families and 3/11 affected ones.
   - (b) drives 2 affected families out of the world (Q2 fails: qoja, cgfa).
   - (b) leaves qbda at p=0. Queries 1-2 are only 2% of examples, so a 4-12 example dev set
     rarely contains one.
   - (a) touches only T4's counterexample items.
   - Caveat: even (a) re-draws all 12 C2 role assignments. `assign_roles` shuffles a pool whose
     membership changes when qbda/qoja leave the p <= 0.75 head (section 3).

3. **Spurious fallback hits (W2 F5) decompose into three kinds.** Of the 25 W2 4M-escrow
   spurious fallback hits:
   - 4 are query-1/2 artifacts that v1a admits.
   - 1 is a long-length artifact.
   - 20 differ from the witness on the dev domain.

   A post-hit hold-out battery of 8 examples:
   - rescues 3/25 solves, at about 1.18M extra charges each;
   - turns 10 spurious hits into honest failures;
   - leaves 12/25 spurious.

   Rejecting a spurious hit takes a median of 9 extra same-stream dev examples; 5/25 are never
   rejected within 40. The 10 true-hit controls cost 0 extra charges.

4. **Ruler v2.1 (draft, `ruler_v21.py`)** on the 47 W3 adversarial schemas (W5):
   - Errors fall from 14 to 8. All 15 flips are listed in section 5.
   - W5 base rate: 23.0% (v2) -> 24.5% (v2.1, strict domain) or 29.0% (with the 25% None
     tolerance).
   - G4 base rate (n=400): 10.25% -> 10.5%.
   - C2 re-score, G1 NOVELTY: 2/8 -> 3/8.
   - All 4 SHAM_0-arm selections carry a G1 relation (2 REFINE G1 algebraically). CON1/G1's
     (v - (acc + {H})) is EQUAL to SHAM_0 under the closure.

## 1. FILES (all in w7_instrument_hygiene/)

**Drafts (never adopted):**
- `tribunal_t4_v1a.py` -- fix (a).
  - T4 with counterexample queries 3..97. The rng stream is the same; only items whose query
    was 1 or 2 change.
  - Profile totality probes use queries (3, 41, 97).
  - Also `direct_score()`, a program-level T4 scorer. It is validated against the real
    artifact tribunals: 60/60 agreement for v1 and v1a (W7_DIRECT_VALIDATION.json).
- `a17_dev197.py` -- fix (b). Prov197 draws the query from 1..97; a17.qualify is reused
  unchanged.
- `ruler_v21.py` -- ruler v2.1.

**Scripts:**
- `w7_common.py`
- `w7_t4dev.py` -- A(1)
- `w7_fixb.py` -- A(2b)
- `w7_downstream_fixa.py` -- A(2a) roles and transfer
- `w7_spurious.py`, `w7_spurious_v1a.py` -- A(3)
- `w7_validate_direct.py`
- `w7_ruler_validate.py` -- B

**Data:**
- W7_T4DEV_ROWS.jsonl (648 rows = every row that reached T4: 644 qualified,
  4 NONE_ON_DOMAIN)
- W7_FIXB.json
- W7_DOWNSTREAM_FIXA.json
- W7_SPURIOUS.json, W7_SPURIOUS_V1A.json
- W7_DIRECT_VALIDATION.json
- W7_RULER_ADV_{W5,G4}.json, W7_RULER_ADV_W5_tol0.25.json
- W7_RULER_BASE_W5_200.json, W7_RULER_BASE_W5_200_tol0.25.json, W7_RULER_BASE_G4_400.json
- *.log

**Reproduction checks (all passed):**
- The v1 re-score of the witness matches the frozen T4_qualified on 648/648 rows.
- Pilot p re-walked with a18.fast_cost at 250k matches frozen p_PRISTINE and p_L1 in 99/99
  walked families, both arms.
- W2's 4M walks reproduce 40/40.
- C2 transfer cells re-walked: 72/72 charges and verdicts reproduce.
- Ruler v2 on the adversarial set equals W3's stored verdicts 47/47.
- The W5 v2 base rate reproduces W3 (46/200). The G4 n=400 rate reproduces W3's 10.3%
  (41/400).

## 2. TASK A(1): THE T4 / DEV QUERY-DOMAIN MISMATCH

**Method.** For every row that reached T4:
1. Build E_dev: the programs in PRISTINE coverage H1 x H2 x FINAL, plus the L1 `derived_0`
   entry, that equal the witness on W2's dev-domain probe. That probe has 100 inputs of length
   4-9 and 20 of length 20, all with queries 3..97.
2. Screen every E_dev program on T4 v1's counterexample items that have query 1 or 2 (25-31
   items per family).
3. Score each divergent program fully with v1 and v1a.
4. Re-walk the 8 frozen pilot cells (PRISTINE and L1, 250k) for two groups: every family with
   a divergent program, and a deterministic 1/8 hash sample of the rest. That is 99 families in
   all.

| set | T4-qualified | E_dev non-empty | families w/ q1/2 artifact | artifacts / E_dev progs | foundry p flips |
|---|---|---|---|---|---|
| C2 | 283 | 93 | 7 | 23 / 977 | qbda, qoja |
| C3 | 361 | 106 | 4 | 8 / 1,744 | cgfa |
| all | 644 | 199 | 11 (1.7%) | 31 / 2,721 (1.1%) | 3 (0.47%) |

**Two artifact types cover all 31 programs.**
- **Families unsolvable by construction under v1: qbda, qoja, cgfa.** Every coverage
  equivalent is an artifact (8/8, 10/10, 5/5).
  - qoja: the witness body is (acc + (v % (v*last))). It behaves like (acc + v) except when
    last = 1, and PRISTINE finds init 1, (acc + v), (acc + first).
  - qbda: the witness contains (1 // last).
  - cgfa: the witness contains (1 % last).
  - In all three, the witness itself is the query-1/2-special program; PRISTINE only holds the
    generic version.
- **An L1 library artifact:** ('fold', '1', '(acc + (v * last))', '(acc // last)').
  - It equals sum for last >= 2 and sum + 1 for last = 1.
  - It sits in the equivalence class of 8 sum-class families.
  - It was never a first hit in the walked cells: the keyed order put a true equivalent first.

**First-hit rate of "correct-on-dev, wrong-on-T4" artifacts:**
- PRISTINE: 12 of 2,576 cells, which is 2.2% of dev-consistent first hits (12/557).
- L1: 11 cells, 1.4% (11/772).
- Among T4-failing first hits in the walked families: PRISTINE 12/13, L1 11/15.
- In the 88 control families: 0.

**Beyond coverage (W2's 4M NAT cells):**
- In coverage, 4 of the 5 T4-failing first hits are qoja.
- In the fallback, 4 of 25 are query-1/2 artifacts. They come through G4 inits and terms that
  are constant for query >= 3, such as (1 // last), (1 % last) and (v - (acc + (1 % last))).
- The fallback init space contains many such terms, so the artifact rate should grow with
  escrow.

## 3. TASK A(2): TWO FIXES AND WHAT EACH DOES TO FROZEN RESULTS

### Fix (a): `tribunal_t4_v1a.py`

The counterexample query becomes the r.randint(3, 97) value that v1 already draws and
discards. List lengths, list values and the rng stream are byte-identical. Profile totality
probes use queries (3, 41, 97).

Measured effect:
- **Witness admission:** 0 changes. The 4 NONE_ON_DOMAIN rejections stay rejected.
- **Q2:** 0 changes.
- **Foundry p:** 3 families (qbda, qoja, cgfa).
- **Downstream C2 roles:** `assign_roles` shuffles the head pool (p_PRISTINE <= 0.75) with
  rng.shuffle. Removing qbda (CON:SHAM_0 head) and qoja (NAT head) changes the shuffled order,
  so all 12 C2 replicates get different role sets.
  - CON: 9-13 of 16 families kept per replicate.
  - NAT: 5-11 of 14 kept.
  - The frozen roles reproduce exactly when nothing is changed.
- **Downstream C3 roles:** `assign()` takes the first k by name, and cgfa is in no role pool,
  so 0 of 8 replicates change.
- **C2 transfer cells of qbda** (TRANSFER in CON4; 6 arms x 4 cells x 3 libraries):
  - Qualified library-cells go from 0 to 10-12 per arm.
  - SOLVED (selected library qualified and START not) is unchanged in all 6 arms, because
    START finds the same artifact class.
  - qoja has no transfer rows.

### Fix (b): `a17_dev197.py`

Measured on 41 families: all 11 affected ones and 30 hash controls. Q2 was recomputed and the
pilots re-walked, both with the frozen labels.
- Every dev set and Q2 probe pool changes. randint(1,97) and randint(3,97) consume the Mersenne
  stream differently, and 0/400 tasks were identical in the self-test.
- Q2 size changed in 4/30 controls (13%) and 3/11 affected families.
- qoja and cgfa become Q2-unqualified. A program that differs only at queries 1-2 matches the
  witness on about 98% of probes, so no random dev subset of 24 or fewer items discriminates
  it. The families are deleted, not made learnable.
- qbda: Q2 goes 12 -> 8 and p stays 0. A dev set of size 4 contains a query 1 or 2 only 8% of
  the time (22% at size 12), so the walk still meets the artifact first.
- p changed in 0/30 controls; qyfa's p_L1 went 0.75 -> 0.5 (walk luck).
- Downstream, every donor, validation and transfer dev set changes, and so do the roles.

### Which changes fewer frozen results, and why

(a) does. It is a pure verifier-side change and cannot alter any dev set, Q2 size, walk or
charge. It flips p only where a first hit differs from the witness solely at queries 1-2,
which happens in 3 families.

(b) changes the training distribution. That perturbs the shared rng stream, so everything is
re-drawn. It also does not align T4 and dev at the sample level.

**Recommendation.**
- Freeze (a) as a new instrument version and keep v1 as the instrument of record for
  AMENDMENTS <= 22.
- State that v1a certifies nothing about queries 1-2.
- Separately, replace `assign_roles`' pool shuffle with a keyed order, as `fair.keyed` does for
  walks. Then a one-family foundry change moves one role instead of re-drawing twelve
  replicates.

## 4. TASK A(3): SPURIOUS FALLBACK HITS -- Q2-BEYOND-COVERAGE DISCRIMINATORS

**Sample:** 40 W2 4M NAT cells, re-walked exactly at 4M:
- all 25 T4-failing fallback first hits;
- all 5 T4-failing coverage first hits;
- 10 T4-passing fallback first hits as controls.

**Variants:**
- **HOLD8:** a post-hit hold-out battery of 8 examples from a separate stream. A failing hit is
  discarded and the walk continues.
- **DEV+4:** the dev set extended by 4 examples along the same stream. This is what a Q2 that
  knew about the fallback's wrong programs would pick.

| variant | spurious_fallback (25) | spurious_cov (5) | true controls (10) |
|---|---|---|---|
| HOLD8 | 3 solved; 10 no hit; 12 still spurious (same program); +3.54M charges over the 3 solves | 4 still spurious, 1 no hit | 10/10 unchanged, 0 extra charges |
| DEV+4 | 0 solved; 6 no hit; 19 still spurious | 4 still spurious | 10/10 unchanged |

**Extra same-stream dev examples needed to reject each spurious fallback hit:**
- 1-4 examples: 6 hits.
- 5-8 examples: 4.
- 9-40 examples: 10.
- Never within 40: 5. These are qhga (a long-length artifact) plus qkia, qmja, qvha/3 and qxfa,
  all query-1/2 artifacts that v1a admits.
- Median: 9 examples.

**Decomposition of the 30 T4-failing first hits in the sample:**
- 8 are query-1/2 artifacts: qoja x4, qkia, qmja, qvha/3, qxfa. v1a admits all 8.
- 1 is a length artifact.
- 21 are wrong programs that the dev domain can distinguish.
- Under v1a, W2's fallback spurious rate falls from 25/93 (27%) to 21/93 (23%).

**Cost / benefit.**
- HOLD8 is strictly better than DEV+4 here. It costs 8 extra labelled examples per cell, about
  3.5x the wall time per cell (16 s vs 4.6 s), and about 1.2M charges per rescued solve.
- Even HOLD8 leaves about half of the spurious hits undetected.
- Neither variant costs anything on true hits: adding examples can only remove candidates, and
  a true equivalent stays consistent.
- A Q2 that certified the first B fallback charges would need dev sets of about 13-50 examples.
  That is a different task regime, not a patch.

**Recommendation.** Report spurious-hit rates per arm and segment. If a discriminator is
wanted, use HOLD8 as a counting rule and declare it before any 16x floor assay.

## 5. TASK B: RULER v2.1 (`ruler_v21.py`; draft)

### Repairs

- **R1 -- Relations closed over re-expressions of the reference.**
  - The literal v2 relations are OR-ed over reexpressions(G).
  - Signed-sum algebra over +/- chains, with const 0 dropped:
    - EQUAL_C: F(S) = fixed(G) + {+-hole}.
    - REFINES_C: fixed(G) is a sub-multiset of F(S), and the remaining operands contain the
      hole.
    - COMPOSES_C: sign-flipped fixed(G) is a sub-multiset of F(S) with the hole in the rest (a
      negated G inside a context), or some proper subchain or subterm relates.
- **R2 -- Same witness.** NEW_FINAL counts instances that are both grid-novel and
  trajectory-novel: at least 2, and at least 10% of accumulating instances.
- **R3 -- Declared length domain on the frozen 80-input battery.**
  - L_dom is the largest rung in (20, 25, 30, 35, 40) at which at most NONE_TOL of inputs up to
    that length give None. Longer inputs are masked.
  - L_dom undefined below 20 means the trajectory is degenerate (T4's DOMAIN_TOO_SHORT).
  - "Novel" means no reference trajectory agrees on at least 10 commonly defined positions.
  - **Default NONE_TOL = 0.0.** A tolerance of 0.25 gave identical W5 adversarial verdicts but
    raised the W5 base rate from 24.5% to 29%. It admits division-by-zero junk such as
    math.gcd(abs(0), abs(({H} - (v // acc)))). "At most 25%" is satisfied by 0.
- **R4 -- Base rate reported per world** (below).

**Not repaired** (documented in the file header):
- distributed forms such as ((acc*v) + ({H}*v)) are not factored;
- the grid still assumes acc >= 0;
- inert wraps are still COMPOSES;
- efficiency-only schemas are still NEW.

### W3 adversarial set, W5 (errors against W3's expected labels)

| class | n | v2 errors | v2.1 errors |
|---|---|---|---|
| a_reexpr | 8 | 0 | 0 |
| a_reexpr_comp | 6 | 4 | 3 |
| b_domain | 5 | 3 | 3 |
| c_inert | 10 | 0 | 0 |
| d_special | 7 | 2 | 0 |
| e_compose | 7 | 4 | 2 |
| f_efficiency | 4 | 1 | 0 |
| **total** | **47** | **14** | **8** |

In G4, total errors go from 15 to 12.

### Every flip vs v2 (W5; identical at tolerance 0.25)

**NEW_FINAL flips:**
1. ((acc * v) + ({H} * v)): False -> True. Fixes an FN. Only 2 of 2 instances are novel, so it
   sits exactly at the minimum-count floor.
2. ((acc + {H}) * v): False -> True. Fixes an FN; this is the product/None repair (W3 F4). 133
   of 144 instances are novel on both grid and trajectory.
3. ((acc + {H}) * last): False -> True. Fixes an FN (domain repair).
4. ((acc * v) + {H}): False -> True. Fixes an FN.
5. (acc - ({H} * first)): True -> False. Fixes an FP (REFINES_C).
6. ((acc - {H}) + v): True -> False. Fixes an FP (REFINES_C). It is also tagged COMPOSES, which
   is a tag ambiguity.

**Relation-only flips** (the NEW verdict is unchanged):
7. (acc - (0 - {H})): EQUAL False -> True.
8. ({H} - (0 - acc)): EQUAL False -> True.
9. (0 - ((0 - acc) - {H})): EQUAL False -> True.
10. (0 - (0 - (acc + {H}))): EQUAL False -> True.
11. (v - (acc - {H})): COMPOSES False -> True. SHAM_0 composes G1 (W3 F2).
12. ((v - acc) - {H}): COMPOSES False -> True. Still a novelty FN.
13. ((v - {H}) - acc): COMPOSES False -> True. Still a novelty FN.
14. ((0 - acc) - {H}): COMPOSES False -> True. Still a novelty FN.
15. (acc - ({H} - v)): REFINES False -> True.

**Remaining v2.1 errors:**
- 3 a_reexpr_comp FNs: novelty depends on how the schema is written (W3 F3).
- 3 b_domain FNs: the grid assumes acc >= 0.
- 2 e_compose FNs: ((acc + {H}) // v) and ((acc + {H}) % last), which have 1 and 0 novel
  instances.

### Base rate (RB-1 junk generator, W3's seed; Wilson 95% intervals)

| world, n | v2 | v2.1 (tolerance 0) | v2.1 (tolerance 0.25) |
|---|---|---|---|
| W5, 200 | 23.0% (17.7-29.3) | 24.5% (19.1-30.9) | 29.0% (23.2-35.6) |
| G4, 400 | 10.25% (7.7-13.6) | 10.5% (7.9-13.9) | not run |

- The same-witness requirement and the relation closure change 0 random schemas in either
  world.
- The whole increase comes from the trajectory-domain repair: 3 extra random schemas pass in W5
  at tolerance 0, and 12 at tolerance 0.25.

### Re-scored C2 selections vs G1 (W5)

- **G1 arm, NEW vs G1:** 2/8 -> 3/8. CON7's ((acc + {H}) * v) becomes NEW.
- **SHAM_0 arm:** 1/8 -> 2/8. CON2's (first * (v - (acc - {H}))) becomes NEW and COMPOSES G1.
- **SHAM_1 arm:** 3/8 -> 3/8.
- **Every SHAM_0-arm selection now relates to G1:**
  - (0 - (v - (acc - {H}))) and (first - (v - (acc - {H}))) REFINE G1. They are
    acc + (-v - H) and acc + (first - v - H).
  - All four COMPOSE G1.
- **CON1/G1:** (v - (acc + {H})) is EQUAL_C to the SHAM_0 panel schema.

## 6. EVIDENCE AGAINST APHRODITE'S CURRENT INTERPRETATION

**E1. The "27% spurious fallback hits (Q2 is coverage-relative)" figure mixes two instruments.**
- At the frozen 250k escrow, 12/13 PRISTINE and 11/15 L1 T4-failing first hits are T4-domain
  artifacts.
- At 4M, 8 of 30 are T4-domain artifacts.
- Q2 is sound inside coverage. The residual identifiability problem (21/93 fallback hits) is
  real, but fixing it costs a median of 9 extra dev examples per cell.

**E2. C2's per-replicate counts are not replicate-stable.**
- Perturbing the foundry p of 2 families re-draws the role sets of all 12 C2 replicates; 3-7 of
  16 CON families change per replicate.
- The frozen "G1 0/8" is one realisation of a role draw that is chaotic in pool membership.
- Any instrument repair re-draws C2 wholesale, so it needs a new assay rather than a
  correction.

**E3. SHAM_0 is not a G1-free control.**
- Under closed relations, 4/4 of its selections COMPOSE G1, and 2 REFINE G1 algebraically.
- CON1's G1 selection is EQUAL_C to SHAM_0.
- The G1-specific story weakens: the arms are not separated in schema space.

**E4. "16% of random schemas pass" is a G4, n=100 number.**
- In W5, where C2 and C3 live, the rate is 23% under v2 and 24.5-29% after repair; G4 at n=400
  is about 10%.
- A W5 novelty verdict therefore carries a prior of about 1 in 4.
- None of the repairs lowers the base rate.

**E5. Widening the dev draw fails empirically.**
- qbda stays at p=0.
- Two families are deleted by Q2.
- The whole world is re-drawn.
- Only the verifier-side fix (a) aligns T4 and dev.

**E6. The query-1/2 confound is also active beyond coverage.**
- G4 inits such as (1 // last) and (1 % last) are constants for every query >= 3.
- A 16x floor under v1 would admit more of these artifacts.
- 4 of the 25 fallback spurious hits at 4M are this confound, not identifiability.

## 7. LIMITS

- E_dev uses a 120-input probe with lengths up to 20, so programs that differ only at longer
  lengths count as dev-equivalent (qhga is one).
- Walks covered the 11 affected families plus a 1/8 hash sample, not all 644. Divergence was
  screened for every family, so the 3 flips are complete for coverage and L1 first hits within
  250k. First hits in the 98k fallback sliver are not covered; none occurred in the walked
  families.
- Fix (b) was measured on 41 families. Its donor, transfer and C3 consequences are argued, not
  re-run.
- The spurious-hit sample is W2's 40 NAT C2 4M cells only.
- W3's expected labels are judgements, so v2.1's error counts are relative to them.
- No external claims or citations.
