<!-- PROVENANCE: deposited VERBATIM by the principal (Aphrodite) from worker W8's final message, 2026-09-28 ~14:45Z; the harness blocked the worker's own write. Principal note: W8's statement that PID 7948 (a23 foundry) was still running is STALE -- A23 had completed and the principal verified 0 python processes and an empty lease list at 14:29Z and again after W8 finished. -->

# ARC3 W8 -- CG-1 LIN-NX NATURAL-RECURRENCE GENERATOR, TASK SIDE (W1 WP-1)

Worker W8, Aphrodite seat, host M4, 2026-09-28. Plain ASCII.
FORENSIC ONLY. NOT A DISPOSITION. No donor was run. No existing file was modified.
Compute: lease bbf2e885 (2 cores) for generation, genuine tests and coverage. It expired
during the coverage phase and was then released. Analysis and the LIND variant ran on
1 core. No W8 python process remains; the only python processes on the host are the
principal's a23_c3r2c foundry (PID 7948 and its 5 children).

## 0. BOTTOM LINE

1. W1's "natural recurrence exists" test FAILS for CG-1 as specified. This holds under
   both the syntactic reading and the genuine-composition reading. N = 144, 24 LIN +
   24 STAR seeds.

   | criterion | threshold | syntactic (W1) | genuine |
   |---|---|---|---|
   | C1 LIN P_reuse >= 5x STAR, same seed | >= 80% of seeds | 91.7% PASS | 87.5% PASS |
   | C2 cross-seed Jaccard, LIN | <= .10 | .0998 PASS (on the edge) | .0997 PASS (on the edge) |
   | C3 dup, LIN mean | <= .35 | .429 FAIL (only 25% of seeds <= .35) | .429 FAIL |
   | C4 seeds with X_G1 >= .10 / X_G1 <= .02 | >= 25% each | .29 / .25 PASS | .125 / .58 FAIL |

2. Lineage produces generic recurrence. It does not produce G1 recurrence, and a matched
   sham recurs MORE than G1.
   - P_reuse (syntactic) is .213 for LIN, .014 for STAR and .013 for U. The paired
     LIN/STAR ratio has a median of 13.5x.
   - For genuine compositions only, P_reuse is .135 for LIN, .008 for STAR and .010 for U.
   - The genuine X_G1 (COND_8) under LIN has a mean of .051 and a median of .010.
   - The frequency-matched sham PA = ({H} + v) has a genuine X of .152 (median .101) under
     the same LIN supplies.
   - Genuine X for the other panel schemas under LIN: PC (v // {H}) .082, PD .041, PB .017.
3. Recurrence under LIN concentrates in families that PRISTINE cannot reach.
   - In LIN, a family that carries a recurring genuine schema has p0 = .834 at 30k and
     .769 at 250k. For non-carriers the figures are .690 and .612.
   - Carriers sit in the 30k window at .146; non-carriers at .243.
   - G1 genuine members under LIN have p0 = .862 at 30k and .727 at 250k.
   - STAR shows no such gap (carrier and non-carrier within .01-.03).
4. The window problem is generator-independent.
   - The fraction of families in the PRISTINE window (0 < p < 1) at 250k is .021 for LIN,
     .026 for STAR and .020 for U.
   - At 30k it is .21 (LIN), .24 (STAR) and .17 (U); at 1M it is .13-.14.
   - W2's U-shape reproduces on generated supplies.
5. The duplicate-guarded variant CG-1d (LIND: reject a body already archived; 12 seeds)
   fixes dup (0.00) but breaks C2. Its Jaccard is .167 and its X_G1 fractions are
   .17 / .50, so it still fails C4.
6. Recommendation: a PKG-3 / WP-2 task-side freeze is FEASIBLE as an instrument
   (section 6). It must NOT be preregistered as "natural G1 recurrence". The honest
   estimand is a POOLED slope of reuse on X_S over the whole panel, with G1 as one point.
   G1 is not the high-X schema in this world.

## 1. WHAT WAS BUILT

- `w8_lin.py`: the generator and phases.
  - `gen`: builds the supplies.
  - `genuine`: builds the genuine cache and the panel.
  - `cover`: runs the PRISTINE window using W2's coverage and fallback logic.
- `w8_analyse.py`: per-seed statistics and the criteria.
- `w8_extra.py`: the per-seed table, the carrier-vs-noncarrier window split, and LIND.

Data files:
- W8_SUPPLIES.json: 54 supplies x 144 families, each with name, init, body and final.
- W8_SUPPLIES_LIND.json
- W8_GENUINE_CACHE.json: 6790 (w, S) pairs, of which 2619 are genuine.
- W8_PANEL.json
- W8_COVER.json: 7776 families.
- W8_RESULTS.json
- W8_EXTRA.json
- Logs: *.log and *.out. W8_SMOKE_SUPPLIES.json is a 20-family smoke test and is not
  used.

### Generators

All generators use the A19 NAT screen:
- the canonical G5 body (T3D.in_space_body);
- R.accumulating;
- init drawn uniformly from H1;
- final drawn uniformly from the acc-finals;
- T4 family_profile admissible.
Init and final are re-drawn on every proposal.

- LIN (CG-1):
  - Founders: W5-shaped PCFG draws until 8 are admitted.
  - After that, each proposal takes a parent uniformly from the archive of admitted
    bodies and applies ONE edit:
    - with p = .5, an operator swap at a uniform internal node (new op != old op);
    - otherwise, a uniform NON-ROOT subterm is replaced by a fresh E1.
- STAR: the same edit applied to a fresh PCFG draw each time.
- U: the A19 NAT rule (uniform over the G5 list). 6 seeds; used as the reference pool and
  for panel matching.
- LIND: LIN plus a rejection of any body already in the archive.
- Declared deviation from W1's probe code: W1's mutate() could replace the ROOT. CG-1's
  text and W1's docstring say non-root, and I followed the text. This probably explains
  why LIN P_reuse is .21 here vs .45 in W1. W1 also used N = 96.
- Seeds: I._seed("ARC3/W8/SUPPLY/<kind>/<seed>").
- Family names are letters only (fam_name).
- Admission per proposal: LIN .103, STAR .0107, U .0149.
- Runtime: about 15-50 s per supply.

### Statistics (per seed)

- Syntactic statistics are W1's:
  - dup;
  - R3u;
  - P_reuse: 2000 Monte Carlo draws of 4 VAL + 8 TRANSFER;
  - n_recurring: schemas occurring in >= 3 distinct bodies;
  - cross-seed Jaccard of the recurring sets.
- GENUINE statistics restrict schemas as follows.
  - Keep only the W1 schemas that decompose as a wrap, w = op(atom, S) or op(S, atom).
  - Keep only pairs with genuine_motifs.genuine(w, S) = True. This excludes inert wraps,
    EQUAL / REFINES relations to S or its re-expressions, and anything not NEW_V2 +
    NEW_TRAJ.
  - Non-wrap schemas (for example ({H} - (acc + first))) are excluded.
- X_S = (share, COND_8) for S in {G1} + panel.
  - COND_8 is computed EXACTLY, as a hypergeometric P(>= 2 of 8 other families instantiate
    the same composition), averaged over members and their compositions. This is W1's
    definition without Monte Carlo noise.
  - Two versions are reported:
    - "nontrivial" (W1): all compositions except identity wraps and S's own instances;
    - "genuine": genuine compositions only.
- Frequency-matched panel.
  - 600 draws of a18._random_schema gave 40 clean schemas (a20_c3.clean).
  - A pre-filter kept those with raw U-share >= .25 x G1; 13 survived.
  - These were matched on genuine U-share and COND_8 over the pooled U supply
    (864 families). G1 on U: share .058, COND .0044.
  - Duplicates (commutative gcd) were collapsed.
  - Only 2 schemas matched within 0.5-1.5x on both measures:
    - PA ({H} + v): 1.00 / 0.98. This is A19's SHAM_1. Its U-member Jaccard with G1 is
      .094, so it is not a disguised G1.
    - PB gcd(acc, {H}): 1.12 / 1.41.
  - PC (v // {H}) and PD gcd({H}, v) match on share only (COND 3.3-3.6x) and are the
    nearest.
  - A fully matched 4-schema panel does not exist among the random clean schemas at this
    draw size. Declared.
- PRISTINE window (W2 logic).
  - Covered = the witness has an extensional equivalent in H1 x H2 x FINAL, tested on
    W2's 120-probe set. Per cell, the charge is the first equivalent's keyed charge.
  - If uncovered, the charge is W2's fallback lower-bound class: ri, rb, rf, keyed as in
    w2_fallback.
  - The 4 cells use seeds E.search_entropy("A19-pilot-PRISTINE/<name>/<r>").
  - p(E) = the fraction of cells with charge <= E. Window = 0 < p < 1.
  - Approximations (declared):
    - equivalent-hit, not first-dev-consistent hit (spurious early hits are ignored);
    - no Q2 dev set;
    - fallback body ranks are exact only when the expected rank is < 3000. Otherwise the
      expectation is used (sd about sqrt(rank)), which is irrelevant for escrow <= 250k.
    - When ri > 0 the charge is a lower bound (>= 84M).

## 2. PER-GENERATOR RESULTS (mean; median where informative)

| | LIN (24) | STAR (24) | U (6) | LIND (12) |
|---|---|---|---|---|
| dup | .429 (range .26-.63) | .206 | .068 | .000 |
| R3u syntactic / genuine | .565 / .382 | .294 / .171 | .259 / .196 | .690 / n/a |
| P_reuse syntactic | .213 (med .186, range .068-.445) | .0144 | .0132 | .148 |
| P_reuse genuine | .135 (med .100) | .0083 | .0099 | .109 (*) |
| n_recurring syntactic / genuine | 11.8 / 7.8 | 10.0 / 5.7 | 9.7 / 7.2 | - |
| Jaccard syntactic / genuine | .0998 / .0997 | .211 / .185 | .176 / .166 | .167 |
| X_G1 nontrivial COND_8 | .088 (med .042) | .025 | .004 | - |
| X_G1 genuine COND_8 | .051 (med .010, max .306) | .020 | .005 | - |
| G1 genuine share | .080 | .098 | .058 | - |
| PA ({H}+v) genuine COND_8 | .152 (med .101) | .035 | .003 | - |
| PB gcd(acc,{H}) genuine COND_8 | .017 | .003 | .005 | - |
| PC (v//{H}) genuine COND_8 | .082 | .059 | .013 | - |
| PD gcd({H},v) genuine COND_8 | .041 | .009 | .011 | - |
| covered by PRISTINE | .309 (range .06-.63) | .345 | .249 | not run |
| window 30k / 100k / 250k / 1M | .21 / .13 / .021 / .13 | .24 / .15 / .026 / .14 | .17 / .10 / .020 / .10 | not run |
| p0 (uncovered) at 30k / 250k / 1M | .74 / .67 / .56 | .71 / .63 / .52 | .79 / .73 / .65 | not run |

(*) For LIND, 21% of wrap pairs were not in the genuine cache and were counted as
non-genuine. The LIND genuine number is therefore a lower bound. LIND windows were
skipped on the coordinator's time budget.

Per-seed X_G1 (genuine) under LIN:
- >= .10 in 3/24 seeds: LIN:12 .306, LIN:13 .243, LIN:19 .272.
- <= .02 in 14/24 seeds.
The W1 non-trivial version is >= .10 in 7/24 and <= .02 in 6/24. The difference comes
from compositions such as (v * (acc + {H})) and additive spans, which the genuine test
rejects.

The full per-seed table (dup, R3u, P_reuse, n_rec, their genuine versions, X_G1 nt/gen,
share, covered, win30k, win250k) is in W8_EXTRA.json "per_seed_table" and w8_extra.out.

## 3. RECURRENCE vs LEARNABILITY (carriers of recurring genuine schemas)

A carrier is a family whose body instantiates a genuine schema that occurs in >= 3
distinct bodies of its supply.

p0 = no cell reaches an equivalent; win = 0 < p < 1.

| p0 / win | 30k | 100k | 250k | 1M |
|---|---|---|---|---|
| LIN carrier (n = 1262) | .834 / .146 | .798 / .102 | .769 / .027 | .639 / .157 |
| LIN non-carrier (2194) | .690 / .243 | .631 / .143 | .612 / .018 | .510 / .120 |
| LIN G1 genuine members (275) | .862 / .127 | .745 / .193 | .727 / .018 | .625 / .120 |
| STAR carrier (526) | .717 / .224 | .658 / .173 | .627 / .030 | .502 / .156 |
| STAR non-carrier (2930) | .705 / .248 | .656 / .143 | .630 / .025 | .520 / .135 |
| U carrier (167) | .725 / .240 | .683 / .120 | .641 / .042 | .557 / .126 |
| U non-carrier (697) | .806 / .155 | .769 / .098 | .753 / .014 | .671 / .096 |

Reading:
- Under lineage, recurring structure is inherited mostly from deep, uncovered ancestors.
  The families where reuse could be observed are those that PRISTINE, and therefore the
  REUSABLE/SOLVED ladder, will mostly score p = 0.
- At 250k, only about 2.7% of LIN carriers are in the window.
- A window-by-design escrow per stratum (W2 F2) is required. At 30k about 15% of carriers
  and 13% of G1 members are in the window. At 1M the figures are 16% and 12%.

## 4. EVIDENCE AGAINST APHRODITE'S CURRENT INTERPRETATION
Current interpretation: under guaranteed, validation-visible recurrence, inheritance +
composition yields generic reuse; natural worlds rarely present such recurrence.

A1. "Natural worlds rarely present such recurrence" is false for a memoryful natural
    generator.
    - LIN, which never names an abstraction, gives genuine P_reuse .135: 14x U and 16x
      its no-ancestry twin.
    - In 21/24 seeds, P_reuse(LIN) >= 5x STAR.
    - Rarity is a property of the i.i.d. sampler (U, STAR), not of "natural" worlds.
A2. But the recurrence that appears is NOT where the assays can see it. LIN carriers are
    MORE often uncovered than non-carriers: p0 .83 vs .69 at 30k, .77 vs .61 at 250k.
    At 250k the window is about 2% in every generator. Two consequences:
    - "Guaranteed, validation-visible recurrence" is jointly hard to get naturally. When
      recurrence appears, visibility (a learnability window) disappears.
    - A negative natural-world reuse result is therefore predicted by the instrument, not
      by the absence of recurrence. The interpretation conflates the two.
A3. G1 is not privileged by natural lineage.
    - The frequency-matched sham ({H} + v), A19's SHAM_1, recurs 3x more than G1 under LIN
      (genuine X .152 vs .051).
    - (v // {H}) recurs at .082.
    - Any natural-world result that credits G1-specific stepping-stone value, including
      the CON1 forensic replicate, has to beat schemas that the same world makes recur
      more often.
    - Conversely, a null for G1 in a LIN world would be uninformative. G1's X is <= .02 in
      58% of seeds.
A4. The "reliable reuse" bottleneck partly reflects the unit of counting.
    - Syntactic X_G1 overstates genuine X_G1 by about 1.7x (.088 vs .051 mean; .042 vs
      .010 median).
    - Most "recurring G1 compositions" are refinements, additive spans or
      (v * (acc + {H})), which genuine_motifs rejects.
    - Reuse claims measured syntactically (W1, A19) are inflated for G1 in particular.
A5. W1's criteria are internally in tension.
    - dup <= .35 and Jaccard <= .10 trade off along the generator axis:
      - LIN: dup .43, Jaccard .0998;
      - LIND (dup-guarded): dup .00, Jaccard .167.
    - The emergent-identity signal (low Jaccard) is partly produced by duplicated lineages.
    - A generator that passes all four criteria may not exist in this edit law. The
      criterion set, not only the world, limits "natural".
A6. For balance, in support of the interpretation:
    - Under U and STAR, the genuine X_G1 is <= .02 in 100% and 63% of seeds, and
      P_reuse <= .02.
    - The A19-style natural world really is recurrence-poor.
    - Lineage recurrence is also highly seed-dependent: P_reuse ranges .07-.45 across LIN
      seeds.

## 5. SMUGGLING CHANNELS (declared and measured)

S1 T4 viability filter (level iv).
- Admission per proposal is 10x higher under LIN (.103) than under STAR (.011). Lineage
  mostly re-proposes near-admissible bodies, so T4 shapes what recurs.
- Pre-screen vs post-screen composition frequencies were not measured (W1 WP-5).
S2 Archive policy (level iii).
- The uniform parent choice and the dup guard (LIND) change dup and Jaccard sharply.
- The archive policy is a recurrence-magnitude knob and must be frozen.
S3 Panel construction.
- Matching on U-share / COND over the U pool is blind to LIN outcomes. Only 2 schemas
  matched on both measures.
- Choosing the panel after seeing LIN X_S would be smuggling. This report's panel was
  fixed before W8_RESULTS existed.
- The pre-filter (raw share >= .25 x G1) is a declared rule.
S4 Genuine test.
- genuine() treats G1 specially: its ADDITIVE class is excluded. This makes the genuine
  X_G1 conservative relative to the shams.
- A symmetric variant (no class exclusion for any S) should be reported alongside it.
S5 PCFG prior (level v).
- Its atom and operator marginals set which schemas can recur at all. This is declared
  and not varied.
S6 Seed-dependent recurrence identity.
- Low Jaccard means the recurring schema is set by the founders. Roles must not be chosen
  by realised recurrence. Use the A19 role rule at random.

## 6. FROZEN-READY TASK-SIDE SPEC (for a WP-2 / PKG-3 preregistration; no donors run)

F0 Code path.
- roles/Aphrodite/science/arc3/w8_lin_generator/w8_lin.py
- Functions: supply(kind, seed, 144) with kind "LIN"; pcfg(); mutate(); fam_name().
- Engine modules imported read-only: a17, a18 (W5), tier3d, ruler_v2.accumulating,
  tribunal_t4.family_profile.
- Environment: A17_FASTEVAL=1, A18_TAG=A19, a18.worker_init.
- Record the sha256 of w8_lin.py at freeze time.
F1 Supplies.
- LIN seeds 0-23 (W8_SUPPLIES.json is the reference realisation: tags "LIN:<s>").
- STAR seeds 0-23 as the twin.
- U seeds 0-5 as the reference pool.
- N = 144 each.
- Re-running must reproduce W8_SUPPLIES.json byte-for-byte on the family lists. This is
  the freeze check.
F2 Panel.
- G1 + PA ({H} + v) + PB gcd(acc, {H}): matched.
- PC (v // {H}) + PD gcd({H}, v): share-matched only, COND 3.3-3.6x. Declared.
- X_S is computed with comp_index(S, cache, genuine_only = True) and xs(bodies, per, 8).
- The cache is W8_GENUINE_CACHE.json.
- Also report the non-trivial version.
F3 Per-seed pre-donor covariates, frozen from W8_RESULTS.json:
- X_S (share, COND_8), genuine and non-trivial, for all 5 panel schemas;
- dup, R3u, P_reuse (syntactic and genuine);
- covered fraction and window fractions at 30k / 100k / 250k / 1M.
F4 Estimand for the donor stage (W1).
- The slope of REUSABLE / CAPABILITY / SOLVED on X_S, POOLED over the 5 panel schemas,
  seed-clustered, over 24 seeds.
- G1_SPECIFIC only if G1's residual above the pooled slope is > 0 (one-sided p < .05).
- REUSE_NOT_BOTTLENECK if the slope is flat over the realised X_S range. The certified
  range is .00-.66: PA spans .001-.661, G1 .00-.31.
F5 Escrow (MANDATORY). Do not score at 250k: every generator has a window of about 2%
there. Pick one of:
- per-family escrow from W2's class model;
- a fixed 30k for covered families plus 1M+ for uncovered ones (W2 F2).
Preregister the expected window fractions: at 30k, LIN .21; for carriers, .15.
F6 Stop rules.
- If the pooled X_S range across seed x schema cells is < .10 wide, stop: there is no
  dose to test.
- If the window fraction among carriers at the chosen escrow is < .10, stop. This holds
  at 250k now.
- C4 fails for the genuine X_G1 (3/24 seeds >= .10). A G1-only design is therefore
  underpowered. Use the pooled design, or raise K to 16/32 (W1 E2).
F7 Compute for WP-2 (W1's estimate): about 16 core-hours; needs a lease.

Feasibility verdict: the task side is freezable today, with F5 and F6 as conditions.
Not supportable in a preregistration:
- "natural recurrence exists" per W1's four criteria. C3 fails under both readings, and
  C4 fails under the genuine reading.
- a G1-specific natural-world hypothesis.

## 7. DISCLOSURES
- Syntactic matching gives lower bounds on extensional reuse (W2 s5.3). Genuine
  filtering is conservative for G1 (S4).
- The window model is equivalent-hit based, ignores Q2 and spurious hits, uses the
  lower-bound fallback class, and uses expected ranks above 3000.
- A family-profile T4 screen only; no T4 qualification of artifacts.
- The panel has only 2 fully matched schemas.
- LIND: 12 seeds; 21% of its wrap pairs were untested and counted non-genuine; no window
  analysis.
- The first cover run crashed on a failing-fold witness (FE._final on _FAIL). This was
  patched (FAIL is treated as a value) and resumed. Results for families done before the
  crash are unaffected.
- No literature is cited in this report. W1's tags stand.