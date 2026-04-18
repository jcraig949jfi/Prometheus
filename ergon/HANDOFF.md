# Ergon Handoff — Start Here
## For the next Claude Code session
### 2026-04-18

---

## What was done this session (2026-04-18)

### Aporia Research Execution (6 items)
1. **L-space filter**: 13/2977 knot candidates (0.4%). Torus knots T(2,3/5/7) confirmed.
2. **Hyperbolic volumes**: 12,965 computed via SnapPy in 20s. New `knots_topo` domain (4 features).
3. **Knot re-engineering**: `knots_eng` domain — 12 engineered features (Mahler, roots of unity, PCA, signature).
4. **Oscillation detector**: abc CONVERGENT, BSD FLAT, Chowla CONVERGENT. No ZFC independence signals.
5. **Density anomaly scan**: Mendeleev gaps in space_groups (2403), codata (1073).
6. **Knot silence test**: Volumes + engineered features do NOT break cross-domain silence. Aporia confirmed: bridge is categorical, not numerical.

### Harmonia Work Queue (8 items)
1. **F041a catalog entry**: DRAFTED. Rank-2+ slope monotone in nbp (1.21→2.52). Pending CFKRS gate.
2. **DHKMS prediction**: 31% rank-0 residual is NOT a reference error. Gaudin baseline confirmed. DHKMS finite-N goes WRONG direction. Either unfolding error or genuine anomaly.
3. **F011 low-tail mechanism**: Faltings height low-tail compresses with conductor (15.8%→7.6%). Bad primes strongly predict faltings height.
4. **Euler product deflation**: BLOCKED — needs lfunc Dirichlet coefficient access.
5. **Scholz reflection p=3**: ZERO violations across 344,130 pairs. 71.5% equality, 28.5% differ by 1. Cohen-Lenstra deficit (0.816 ratio). Explains p=3 BST anomaly.
6. **Bootstrap CI k=3,4**: Agent running (awaiting completion).
7. **P104 block-shuffle null**: REVIEWED, APPROVED for merge. Thorough calibration anchors.
8. **EC projection triage**: 3 ready now (#3 isogeny, #5 Sha, #7 compound), 3 testable, 1 blocked. Key finding: lfunc has ~1.74M EC L-functions with zeros AND an origin index.

### Threads Opened

**THREAD A: F011 rank-0 residual is genuine frontier.**
DHKMS can't explain it. The 31% non-excised deficit at rank 0 is:
- Not a Wigner-vs-Gaudin reference error (Harmonia used Gaudin)
- Not a finite-N correction (DHKMS predicts the opposite direction)
- Possibly an unfolding artifact, but would need 25% mean bias (implausible)
- The most interesting open finding in the project

**THREAD B: Scholz reflection as new F-anchor.**
Zero violations is perfect calibration. The 71.5/28.5 equality/inequality split is a testable prediction. Could become a battery test: any NF computation that violates |r3(K*)-r3(K)| <= 1 has a bug.

**THREAD C: Three EC zero projections immediately executable.**
Isogeny class size, Sha order, and compound (rank×CM×w) projections need zero joins from lfunc — and we now know lfunc has an origin index. These could produce new specimens.

**THREAD D: lfunc origin index exists.**
The triage agent discovered lfunc has an origin index. This changes the game — EC↔lfunc joins are feasible at scale. Unlocks zero-statistic tests we thought were blocked.

---

## Key Files Created This Session
- `ergon/dhkms_prediction.py` — DHKMS theoretical comparison
- `ergon/scholz_reflection.py` — Scholz p=3 test on 344K pairs
- `ergon/oscillation_detector.py` — Independence oscillation test
- `ergon/density_anomaly_scan.py` — Mendeleev gap finder
- `ergon/moment_bootstrap.py` — Bootstrap CI for moment non-monotonicity
- `ergon/ec_projection_triage.md` — 8 open projections assessed
- `ergon/results/hyperbolic_volumes.json` — 12,965 knot volumes
- `ergon/results/l_space_candidates.json` — 13 L-space candidates
- `cartography/docs/catalog_F041a_draft.md` — F041a specimen nomination
- `harmonia/src/domain_index.py` — load_knots_engineered(), load_knots_topo()

### Level 2 Research (scripts written, NOT yet executed — agents hit rate limit)
These scripts are ready to run. Just execute them:
- `ergon/tamagawa_mediation.py` — Q1+P1: does Tamagawa mediate isogeny effect?
- `ergon/convergence_by_class_size.py` — Q5+P5: finite-conductor transient or structural?
- `ergon/wachs_reproduction.py` — Q3: reproduce Wachs displacement, correlate with variance
- `ergon/higher_gap_analysis.py` — gap1 vs gap2-4 deficit, cross-family comparison
- `ergon/isogeny_sha_joint.py` — joint distribution, partial correlations, BSD connection
- `ergon/murmuration_isogeny.py` — COMPLETED: weak but above-chance signal (5/21 primes significant)

### Murmuration by Isogeny (COMPLETED)
- 5/21 large primes show significant F-test stratification (vs ~1 expected by chance)
- p=79 strongest (F=6.6, p=3.85e-06): class_size=8 has mean a_p/sqrt(p)=-0.045 vs class_size=6 at +0.028
- Effect ~5-10x weaker than rank murmurations
- Small primes heavily confounded by conductor divisibility
- NOVEL axis — nobody has tested isogeny-stratified murmurations before
- Results + plots in ergon/results/murmuration_isogeny/

### Literature Findings (literature_zero_suppression.md)
- Wachs (arXiv:2603.04604, Mar 2026) independently found Sha modulates zero displacement/packing — CONFIRMS our Sha direction
- Isogeny class size stratification is NOVEL — no prior work
- CFKRS arithmetic factor a_E(k) may depend on isogeny structure through Euler product — UNTESTED
- 6 testable predictions, 7 research questions documented

## Infrastructure
- Tensor v2: 23 domains, 4.76M objects, 208 features
- F0 honest battery: object-identity permutation null + synthetic null for tiny domains
- SnapPy available on M1 (volumes work, Alexander polynomial needs Sage)
- Postgres: ec_curvedata (3.8M), nf_fields (22M), artin_reps (798K), lfunc (24M with origin index)
