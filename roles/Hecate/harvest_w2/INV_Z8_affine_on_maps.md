# INV_Z8 -- affine and structured baselines on the adversarial ALIEN systems

Date: 2026-09-30. Analyst for Hecate. DESCRIPTIVE ONLY. Read-only over hecate/alien/data
and runs/claude/RESULTS.json. No model calls, no network, no git writes. Frozen files
(baselines.py, BASELINES.json, score.py) untouched; they are imported, not edited.
Code: roles/Hecate/harvest_w2/INV_Z8_affine_on_maps.py (77 s wall total, one CPU).
Raw output: <session scratchpad>/Z8/INV_Z8_results.json (not committed).

    python roles/Hecate/harvest_w2/INV_Z8_affine_on_maps.py [scratch_dir]

## 0. Setup (what every learner gets)

- Data: baselines._transitions(p, pub) = the same 80 observed transitions (8 trajectories
  x 10 steps) the subject saw blind. Distinct sources: 38-71 per system.
- Scoring: hecate.alien.score.acc on (a) the 12 T2 queries and (b) all 200 T5 eval states
  (Claude's T5 code was scored on 200; the frozen BASELINES.json used the first 100, so
  the vm/tab affine numbers below differ slightly from that file).
- The 8 ADV ALIEN systems: 3 linmix:tab_local (Z_5^5), 3 linmix:poly_sym (Z_31^2),
  2 vm_long (pc 0..5, r in Z_7^3).

Learners:
- identity            next = current.
- fit_affine_gl       baselines.fit_affine unchanged, with the max(dims)<=7 gate lifted
                      (for Z_31 it searches coefficients in -3..3 per the frozen code).
- affine_full         maps only: best-agreement affine per component over ALL of Z_31^3.
- poly_deg3           maps only: exact GF(31) linear solve for a degree<=3 polynomial per
                      component (10 monomials, 80 equations). Uses only "low-degree
                      polynomial mod 31"; no change-of-coordinates search at all.
- poly_min_degree     maps only: smallest d in 1..12 with an exact consistent solution
                      (Occam scan; the learner is not told d=3).
- struct (maps)       for each of the 992 involutions S of GF(31)^2 conjugate to the swap,
                      a frame A with A S A^-1 = swap; fit z' = (g(x,y), g(y,x)) with g
                      degree<=3 in z = A s (10 unknowns, 160 equations). This is the full
                      linear-map search up to the centraliser of the swap, which preserves
                      the class; |GL(2,31)| = 892,800 = 992 x 900.
- struct (tab)        all 781 projective functionals u on Z_5^5 and partners v such that
                      u.(s'-s) is a function of (u.s, v.s) on all 80 transitions; conserved
                      functionals; assemble every invertible frame of 4 such u + 1 conserved
                      functional; predict z' = z + T(z_u, z_v) (unseen cell -> 0), omega'=omega.
                      Reported: median over all invertible assemblies (data-only) and the
                      true-frame assembly (ORACLE pick, ceiling under this data).
- struct (vm)         per pc value, every instruction of the vm_long generator grammar
                      (aff a,b,z,k1,k2,e; tab a,b,T as partial permutation; jz/jnz a,t)
                      consistent with the transitions at that pc; pick by a fixed
                      simplicity order (jumps < aff < tab); unseen tab entry -> no change.
All struct learners are GIVEN the generator grammar (oracle class knowledge the subject
did not have). poly_deg3 / poly_min_degree are not given the linmix wrapper or symmetry.

## 1. Per-system results (comp = component accuracy; T5 on 200 eval states)

    system     kind              Claude      identity   fit_affine_gl  best structured
                                 T2   T5     T2   T5    T2   T5        T2   T5     learner
    SYS-41174  linmix:poly_sym  .000 .025   .125 .033  .167 .030      1.00 1.00   poly_deg3
    SYS-46945  linmix:poly_sym  .000 .035   .000 .033  .000 .045      1.00 1.00   poly_deg3
    SYS-67061  linmix:poly_sym  .042 .030   .042 .068  .000 .038      1.00 1.00   poly_deg3
    SYS-37739  linmix:tab_local .300 .221   .283 .221  .333 .182      .667 .472   struct tab (1 frame)
    SYS-42741  linmix:tab_local .183 .205   .150 .205  .200 .200      .417 .337   struct tab (median/53)
    SYS-46005  linmix:tab_local .183 .234   .183 .234  .300 .217      .867 .725   struct tab (1 frame)
    SYS-14818  vm_long          .958 .954   .625 .621  .813 .823      .958 .956   struct vm
    SYS-70612  vm_long          .938 .953   .542 .565  .792 .785      .979 .969   struct vm

Exact-match (T5 eval_exact): maps poly_deg3 1.000 on all 3 (Claude 0.000 on all 3);
tab struct 0.295 / 0.280 (oracle frame; data-only median for 42741 not split out) / 0.670
(Claude 0.02 / 0.02 / 0.03); vm struct 0.825 / 0.875 (Claude 0.815 / 0.810).

Maps, extra learners:
    system     affine_full T2/T5  train agree (of 80)  poly_min_degree  struct frames  struct T2/T5
    SYS-41174  .125 / .048        23, 22               d=3, unique      2 of 992       1.00 / 1.00
    SYS-46945  .000 / .035        19, 18               d=3, unique      1 of 992       1.00 / 1.00
    SYS-67061  .000 / .043        20, 20               d=3, unique      2 of 992       1.00 / 1.00
The degree<=3 fit equals the true step on all 961 states for all 3 systems (exhaustive
check). The true frame is among the consistent frames in all 3. Where 2 frames are
consistent, both reproduce the same unique degree<=3 map (the fitted map commutes with a
second involution); the predicted function is the same.

8-system ADV means (8 systems, equal weight):
    learner                         T2 comp   T5 comp
    Claude                          0.326     0.332
    fit_affine_gl                   0.326     0.290
    best structured (as in table)   0.861     0.807
    3 maps only:  Claude 0.014 / 0.030; fit_affine_gl 0.056 / 0.038; poly_deg3 1.000 / 1.000
    3 tabs only:  Claude 0.222 / 0.220; fit_affine_gl 0.278 / 0.200; struct 0.650 / 0.511
    2 vms only:   Claude 0.948 / 0.953; fit_affine_gl 0.802 / 0.804; struct 0.969 / 0.963

## 2. Compute used

    learner            per system         search size
    fit_affine_gl      0.05-1.5 s         frozen ranges (5^5 x 5 per comp on tab; 7^2 x 31 on map)
    affine_full (map)  0.05-0.3 s         31^2 x 31 per component
    poly_deg3          0.4-0.7 s          2 GF(31) solves, 80 x 10 (scan d=1..12: 24 solves)
    struct map         11.9-17.4 s        992 frames x one 160 x 10 GF(31) solve
    struct tab         2.7-13.6 s         781 x 781 (u,v) table-consistency checks + assemblies
    struct vm          0.1-0.2 s          6 pcs x 7,992 grammar instructions
All numbers are from one run of the script on this host; timings are wall-clock seconds.

## 3. Identifiability from 80 transitions (consistent-hypothesis counts)

Maps (Z_31^2; counts per system, both components; nullity summed over the 2 components;
consistent hypotheses = 31^nullity):
    degree d   monomials  41174           46945           67061
    1          3          inconsistent    inconsistent    inconsistent
    2          6          inconsistent    inconsistent    inconsistent
    3..8       10..45     unique (1)      unique (1)      unique (1)
    9          55         31^10           31^12           31^10
    10         66         31^30           31^32           31^32
    11         78         31^52           31^56           31^56
    12         91         31^76           31^82           31^82
For d = 3..8 the unique solution is the degree-3 map itself (it lies in every larger class
and the solution is unique). The map ADV systems are exactly identifiable from the 80
transitions in any polynomial class up to degree 8; identifiability is lost from degree 9.
Symmetric-frame class: 1-2 of 992 frames consistent, one distinct predicted map.
Affine class: no exact affine map is consistent (best agreement 18-23 of 80 per component).

Note on the construction: a degree<=3 polynomial map conjugated by an invertible linear
map mod 31 is again a degree<=3 polynomial map. The linmix wrapper therefore does not
leave the polynomial class; poly_deg3 recovers the system without finding the hidden
coordinates. analogue_ok in generate.py rejects only AFFINE maps, not low-degree ones.

Tabs (Z_5^5; latent frame recovery and table coverage):
    system     u with partner  conserved  invertible frames  true frame found  seen cells  free cells
    SYS-37739  4               1 (true)   1                  yes               66/100      34 -> 5^34
    SYS-42741  14              1 (true)   53                 yes               50/100      50 -> 5^50
    SYS-46005  4               1 (true)   1                  yes               85/100      15 -> 5^15
(Each true row has 5 consistent partners v; these are v + lambda u, lambda in 0..4, which
index the same table, so the partner is effectively unique.)
- The coordinate frame is identified from the data alone in 2 of 3 tab systems (one
  invertible assembly) and narrowed to 53 candidates in SYS-42741 (eval comp range across
  them 0.269-0.406; the true frame is the max).
- The tables are NOT identified: in the true frame, 15-50 of the 100 (row, cell) entries
  were never observed. Eval (row, state) units hitting an unseen cell: 274 / 404 / 126 of
  800; among those, the true increment is nonzero in 223 / 257 / 74. Eval states fully
  covered in all 4 rows: 42 / 34 / 103 of 200.
- So the tab ceiling under this data (true frame, true values on seen cells, 0 default)
  is T5 comp 0.472 / 0.406 / 0.725, i.e. coverage-limited even with the frame known.

VMs (consistent instructions per pc under the generator grammar, tab completions counted):
    SYS-14818  obs per pc 17,16,2,5,21,19   consistent 2,1,798,2,1,2      picked = true at 5/6 pcs
    SYS-70612  obs per pc 3,15,16,15,15,16  consistent 50,1,1,6,6,1       picked = true at 6/6 pcs
Under-observed pcs (2-5 transitions) carry most of the ambiguity.

## 4. Descriptive reading

- The 3 map ADV systems are not hard for this data: a degree<=3 polynomial solve over
  GF(31) (sub-second, no frame search, degree found by an Occam scan) and the explicit
  992-frame symmetric search both reproduce the system exactly (T2 1.00, T5 1.00, exact
  1.00). Claude (T5 comp 0.025-0.035) and every affine learner (0.030-0.048) score at the
  identity level on the same 80 transitions. Map systems are uniquely identifiable in
  polynomial classes up to degree 8.
- The 3 tab ADV systems are partly hard for any learner with this data. The hidden
  frame is recoverable (1, 53, 1 consistent frames), and a grammar-given search reaches
  T5 comp 0.47 / 0.34 / 0.73 vs Claude 0.22 / 0.21 / 0.23 (identity level). The
  remaining gap is table coverage: 5^15 to 5^50 table completions fit the data.
- The 2 vm_long systems are not adversarial in effect: Claude T5 comp 0.954 / 0.953,
  grammar search 0.956 / 0.969, fit_affine_gl 0.823 / 0.785.
- Over the 8 ADV systems: Claude T5 comp 0.332, fit_affine_gl 0.290, best structured
  0.807. The structured learners were given the generator grammar; poly_deg3 on the maps
  was given only "low-degree polynomial mod 31".
- Not tested: grammar-free learners on tab (e.g. generic decision trees), robustness to
  fewer transitions, and the other subject models (gemini, gptoss).
