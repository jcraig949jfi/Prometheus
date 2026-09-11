================================================================================
EXTERNAL REVIEW PACKET
ARACHNE -- ARCHAEOLOGY AS EXPERIMENT: WHAT THE JUNE 2026 CRAWLER RUN SHOWED
================================================================================
Prepared:        2026-09-11   frozen; two preregistrations before rows
Location/Code:   roles/Arachne/science/ (specimen, branch_fitness,
                 emergence, feral_autopsy, harvest_audit, census; 21 tests)
Artifacts:       roles/Arachne/ARCHAEOLOGY_AS_EXPERIMENT_2026-09-11.md
                 roles/Arachne/ledgers/{branch_fitness,emergence,
                 feral_autopsy,harvest_audit}_2026-06-04.json
                 roles/Arachne/prereg/PREREG_BRANCH_FITNESS_v0.md @ 16dba61d8
                 roles/Arachne/prereg/PREREG_EMERGENCE_v0.md @ dbd5345c0
Version/Hash:    specimen roles/Arachne/archive/run_2026-06-04/ (6 files,
                 LF sha256 in MANIFEST.md); ruling sha256 96986463b4e5...
Headline:        BRANCHING WAS A DEATH RATTLE AND THE MUTATION WAS
                 DECORATIVE; EMERGENCE NOT EARNED (the fabric is the
                 adapters' tables of contents plus BFS/LIMIT-n mechanics);
                 FERAL DIED OF A DEFECT; HARVEST HAD NO CONSUMER AND
                 ALMOST NO INFORMATION. RECOMMENDATION: C. METABOLIZE.

--------------------------------------------------------------------------------
1. CLAIMS UNDER REVIEW
--------------------------------------------------------------------------------
Q3  Did near-death branching ever produce a fitter child, under the
    mechanism that actually ran?
Q4  Does the 21,209-edge fabric hold structure that would be surprising
    under cheaper generative explanations (partition / ablation / nulls)?
Q5  Why did the feral organism die, and is that evidence about "fewer
    rules"?
Q6  Why was the harvest never consumed?
Falsifiers were frozen in two preregistrations, each committed before
its rows; readings are reported AS FROZEN, and where a frozen gate is
found mis-specified the reading stands and the defect is a calibration
row, never a moved gate.

--------------------------------------------------------------------------------
2. SPECIMEN AND SETUP
--------------------------------------------------------------------------------
- Frozen June residue, manifest-verified on every load; tamper test.
- Two segments: 1,424 edges / 45 ticks, then a --fresh restart (ticks
  and ids reset) of 19,785 edges / 700 ticks. Ids collide across
  segments; keyed by (segment, id).
- Whole archive post-dates the escape fix 9cb4602bb; the pre-fix run was
  never preserved. The trough-only branch trigger was never changed.
- Every edge mapped to a tick by interpolation; the crawler's fitness
  reconstructed per tick. POSITIVE CONTROL: 82 of 82 logged
  parent_fitness values reproduced within 0.10 (74 within 0.05); 124 of
  124 death rows' edge counts exact.
- No crawl, no expand(), no edge. One flagged DB read: 34 OEIS names.

--------------------------------------------------------------------------------
3. RESULTS -- BRANCH FITNESS (82 events; 79 seg-2)
--------------------------------------------------------------------------------
comparison                          child>ref   frac   95% CI          status
--------------------------------    ---------   -----  -------------   -------
C1 mechanism view (parent@trough)   63/63       1.000  [0.943,1.000]   READ*
C2 age-matched (both at age 16)     30/43       0.698  [0.549,0.814]   READ
C3 contemporaneous (tick b+16)      14/17       0.824  [0.590,0.938]   INDET
C4 productivity vs default birth    35/68       0.515  [0.398,0.629]   READ
C4 survival vs default birth        39/67       0.582  [0.463,0.693]   READ
C5 survival child vs parent         36/68       0.529  [0.412,0.643]   READ
F3 productivity child vs parent     47/68       0.691  [0.574,0.788]   READ
  ESCAPED arm C4 productivity       16/44       0.364  [0.238,0.511]   READ
  STAYED  arm C4 productivity       19/24       0.792  [0.595,0.908]   READ
(* biased by construction: every parent branched at f < 0.6)
Frozen readings: Q1 INDETERMINATE (C3 gate 20, reached 17; 7 witnesses
listed); Q2 MUTATION_DECORATIVE; Q3 stayed-arm C4 EXCLUDES 0.5 UP.
59 of 79 parents dead within 16 ticks of branching. Medians: child 29,
parent 28, default birth 34 ticks.

--------------------------------------------------------------------------------
4. RESULTS -- EMERGENCE (5,621 nodes; 16,583 pairs; 10 samples/null)
--------------------------------------------------------------------------------
Nulls: N1 global degree; N2 block-constrained; N3 class-constrained
(cheapest explanation E0); N4 LIMIT-n star toward class hubs (E1).
statistic                  observed  N2 block      N3 class      N4 LIMIT-n
------------------------   --------  -----------   -----------   -----------
modularity                 0.8895    0.69-0.70 ^   0.870-0.879^  0.888-0.892 in
NMI vs landscape           0.4579    0.65-0.70 v   0.450-0.469in 0.463-0.474 v
NMI vs classes: oeis       0.8829    --            0.897-0.908v  0.885-0.909 v
                knots      0.9790    --            0.974-0.983in 0.973-0.985 in
                groups     0.9322    --            0.932-0.937in 0.934-0.941 v
                lmfdb      0.9882    --            0.9882 in     0.9882 in
transitivity               0.4499    0.019-0.020^  0.438-0.441^  0.218-0.222 ^
bridge redundancy (57)     0.246     0.298-0.456v  0.246-0.281in --
cross concentration max    212       700-1536 v    --            --
mixed-triangle fraction    0.1198    --            0.111-0.121in 0.125-0.136 v
Ablation: 5 of 75 units load-bearing; 6.8 expected by chance
(P(X<=5)=0.31); oeis-0-4 (17 pct of pairs) perturbs LESS than random.
Frozen ladder: (a) CROSS_CUTTING (b) NOT_STABLE (c) CANDIDATE_STRUCTURE
-> EMERGENCE_EARNED = FALSE.
Disposition: (a) fired on resolution (178 communities vs 6 labels; the
value is reproduced by N3); within-landscape NMI 0.88-0.99 = the
invariant classes = table of contents. (b) has no power as frozen. (c)
fired on statistics lying BETWEEN N3 and N4; outside both: transitivity
+2 pct, connectivity +3 pct, LOWER class alignment in oeis -- BFS over
LIMIT-n rows (post-hoc: hub-8 clique density 0.88-0.93; 918 of 2,806
expanded nodes carry 2+ ops). No cross-landscape excess anywhere.

--------------------------------------------------------------------------------
5. RESULTS -- FERAL AND HARVEST
--------------------------------------------------------------------------------
Feral: hop re-draws the landscape each step over one mixed frontier;
every adapter returns nothing for a foreign prefix; p_success ~ 1/6.
P(death by tick 28) = 0.40; by 700 = 1.0; specialist at p=0.9: 0.0. No
revival path; no bridge capability. IMPLEMENTATION DEFECT; uninformative.
Harvest: ran on the 1,424-edge segment-1 fabric; rule unrecoverable (58
claimed, 25 listed, 29 recovered); three 3-term prefix groups, two of
them binomial-row openings; 22 of 29 OEIS names already state a rule;
"no computing function" = none of 12 sympy functions; no consumer, no
routing event, no experiment. Anchors = the joiner's own positive control.

--------------------------------------------------------------------------------
6. VERDICT MATRIX (abridged; full in the readout s6)
--------------------------------------------------------------------------------
population/branch/floor machinery ............... MECHANISM WORKED
branch-near-death as selection .................. MECHANISM FAILED
escape fix as an improvement .................... INSUFFICIENT EVIDENCE
corrected trigger ............................... EXPERIMENT NEVER RUN
pre-fix run evidence ............................ MEASUREMENT FAILED
three epistemic rules per edge .................. MECHANISM WORKED
null_p as a null ................................ IMPLEMENTATION DEFECT
emergence (a) partition ......................... HYPOTHESIS FALSIFIED*
emergence (b) ablation .......................... INSUFFICIENT EVIDENCE
emergence (c) nulls ............................. HYPOTHESIS FALSIFIED*
n=2 emergence ................................... HYPOTHESIS FALSIFIED*
bridge redundancy ............................... MECHANISM FAILED
"fewer rules" (feral) ........................... EXPERIMENT NEVER RUN
June holdout / usefulness judges ................ MEASUREMENT FAILED
lexical rosetta join ............................ MECHANISM FAILED
operational computes join ....................... MECHANISM WORKED
harvest anchors / void targets .................. CONSUMER ABSENT
landscapes ...................................... MECHANISM WORKED
silent LMFDB degrade, no freshness .............. IMPLEMENTATION DEFECT (fixed)
(* on this fabric, these landscapes, these adapters; nothing marked dead)

--------------------------------------------------------------------------------
7. CONTROLS
--------------------------------------------------------------------------------
Reconstruction positive control (82/82; 124/124). Partition instrument:
positive NMI 1.000, negative 0.0003, planted-clique cheat recovered pure.
Ablation: negative ARI 1.0, positive < 1. Every null sample asserts its
own preservation. Sign statistic: negative (symmetric) includes 0.5,
positive (planted) excludes, cheat (all ties) INDETERMINATE. Specimen
tamper cheat: a one-byte change is refused.

--------------------------------------------------------------------------------
8. KNOWN LIMITATIONS AND CAVEATS
--------------------------------------------------------------------------------
- Three frozen gates were mis-specified (calibration rows 8-11): (a)
  resolution, (b) no power, (c) no hull requirement, Q1 above eligible.
  Readings are reported as frozen; dispositions are labelled.
- C4 controls are matched by landscape and nearest tick, median 37
  ticks apart; a 5-tick match is ARACHNE-34.
- Arms differ in landscape mix; n=24 on STAYED.
- Ten null samples; 5*m swaps for N1/N2 is the stated mixing budget.
- The pre-fix (inverted-selection) run is not in the specimen; the
  STAYED arm is the nearest available proxy.
- Louvain is one method; NMI/ARI are two agreement measures; the class
  labels are components of the op's own pairs, i.e. subsets of true
  classes.
- The harvest rule could not be reproduced exactly (threshold lost).
- Conflict of interest: the seat that built the June organism graded it.
  The reconstruction control, the nulls' self-assertions and the
  committed rows are what a reviewer can check without trusting me.

--------------------------------------------------------------------------------
9. REPRODUCTION
--------------------------------------------------------------------------------
    python -m pytest roles/Arachne/science/tests -q         (21 tests)
    python roles/Arachne/science/specimen.py                 (82/82 control)
    python roles/Arachne/science/branch_fitness.py           (~10 s)
    python roles/Arachne/science/emergence.py controls
    python roles/Arachne/science/emergence.py full           (~9 min)
    python roles/Arachne/science/feral_autopsy.py
    python roles/Arachne/science/harvest_audit.py            (1 DB read)
    python roles/Arachne/science/census.py                   (no expand)
From a linked worktree (D-23); the census and audit need the Evidence
Wiki credential resolver; everything else needs only the archive.

--------------------------------------------------------------------------------
10. DECISION
--------------------------------------------------------------------------------
A. RESUME ......................... no  (nothing beyond adapter mechanics)
B. REBUILD ........................ no  (the environments emit equivalence
                                        relations; fixing the organism
                                        does not change that)
C. METABOLIZE ..................... YES (verified joiner + damage.py kept;
                                        nulls/judge packaged; negatives to
                                        the Evidence Wiki; H3 candidate
                                        write-up; a re-premised
                                        COMPUTATIONAL organism proposed as
                                        NEEDS_REPREMISE, not executed)
D. PARK ........................... no  (instruments and residue have a
                                        named gradient)
Reviewer's bottom line: is there any reading of the class-constrained
null under which a crawler over invariant tables could have shown
organization -- or was the founding experiment unable to produce its
own positive outcome on these landscapes?
================================================================================
END OF PACKET
================================================================================
