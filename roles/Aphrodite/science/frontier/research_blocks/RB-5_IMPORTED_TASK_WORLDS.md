# RB-5 -- IMPORTED TASK WORLDS: EC POLYNOMIAL LADDER AND AN OEIS SUBSET (T06, T07)

Medium, autonomous. Estimated 1-2 days. Read RB-00 first, then
PRIOR_ART_B_LIBRARY_LEARNING.md sections 1.1 (EC), 1.23 (integer sequences) and (e).

WHY
  Aphrodite's own task world is nearly additive (K1/K7). Independently designed task
  ladders avoid the smuggling danger (we did not design them to show recursion). The EC
  2013 polynomial experiment is the ONE published controlled task-supply ablation:
  removing the constant and linear polynomials caused sharp drops, and quadratics with
  coefficients > 1 gave zero learning.

STEPS
  1. EXPRESSIBILITY CENSUS
     - EC polynomials: tasks f(x) = a x^2 + b x + c over small integers. Decide the
       mapping into fold tasks. Candidate: the list = a sampled x-range, and the answer =
       a sum/fold of f over it. Alternative: a new "map" task shape. Document the choice
       and why it does not smuggle G1.
     - OEIS: pick 500 sequences with small integer terms and a simple recurrence (Gauthier
       & Urban's selection criteria, see PRIOR_ART_B 1.23). Map to "given the first k
       terms as the list, answer the (k+1)-th". Check which have a G4 fold witness
       (enumerate G4, fasteval, early exit).
  2. For expressible tasks, run the K1 admissibility checks and Q2 (a17.qualify). Note
     that the tribunal's permutation test will reject most OEIS tasks by construction.
     Report that separately and do not relax it here (RB-2 does that).
  3. Rerun a K5-style donor comparison on the EC ladder:
       {full ladder, ladder minus constant+linear, quadratics only}
     x {DONOR_G1, DONOR_P}. Record derived and selected schemas and the RB-1 ruler
     verdicts.
DELIVERABLES
  science/frontier/rb5/ (bridge code, census JSON, donor results, IMPORTED_WORLDS.md).
  If the fold DSL cannot express the ladder without new primitives, say so. That is a
  NEW-LENS SIGNAL (T06).
