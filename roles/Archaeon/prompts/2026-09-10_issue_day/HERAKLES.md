HERAKLES -- WHAT ARCHAEON NEEDS ON MAIN, WITH POINTERS
(from the operator via Archaeon, 2026-09-10, issue day)

State: C3-2 (cs-c3-2, 150 rows: 6 hist, 6 base, 18 exact-symmetry nulls,
120 random) is executing on the live consumer under success_criterion
`stable`; first live results: GKL/par/particle1/particle2/exp in the
0.6-0.85 band per IC sample, maj = 0.0 on every sample and every
transform. The null already holds exactly on exp x3 and par:reflect.
Your class map is wired in (archaeon/producer/h5_reference.py
load_class_map, scope carried beside the number). D-18 is the operator's
decision; nothing here asks you to re-run.

DELIVER, each as a committed file on origin/main, then push, then report
the SHA on main and the path of every item:

1. MAIN vs BRANCH: for every file you named today (OBSTRUCTION.md
   correction, reset_v2.py, D18_AMENDMENT_v1.md, d18_development.json,
   d18_horizon_evidence.json, INBOX_HERAKLES_CA_CONVENTIONS_CONFIRMED,
   c3_transform_fixture.json, class_map_fixture.json) state whether it is
   on origin/main (`git merge-base --is-ancestor`), and merge what is not.

2. EXACT-SYMMETRY NULL CHECK, executable: herakles/evca/c3_null_check.py
   taking two ca_density_v0 wrapper results (untransformed twin and
   transformed) and returning IDENTICAL / NOT_IDENTICAL / INDETERMINATE
   with the fields compared (per-IC-sample accuracy, incorrect counts,
   mask digest, witness ICs) and the complement handling (target flips;
   compare the mask, never raw trajectories). Test it on your
   c3_transform_fixture. Archaeon runs it on the 18 live null rows.

3. THE maj STRUCTURAL ZERO, as a committed fixture: the relaxation table
   (median / reached / censored per rule, 200 samples, density 0.5) and
   the command that produced it, so the C3-2 readout cites a file and not
   a chat message. Beside it, one paragraph: what maj scored under at_T in
   C1-e (17/18, particle2 HELD) so the two criteria are documented side
   by side and nobody reads maj = 0.0 under `stable` as a failed
   reproduction.

4. H5 INPUTS: for the class map, the scope sentence and the two
   degenerate groups (240 = 15,180,210; 170 = 85,154,166) are wired in.
   State: (a) whether the 224-class map is the equivalence H5's decoders
   should collapse to at alpha, or whether a finer scope (more steps, a
   larger ring) is the right one and why; (b) the status of
   eca_rule_eval_v1 registration in Vivarium -- yours to hand over or
   already handed, with the pointer to the kind spec.

5. C3-2 READ: when the corpus completes (~4 h), Archaeon posts
   archaeon/docs/h0h5/C3_2_READOUT.md. Say now what you need in it to
   judge the historical arm against C1-e (fields, per-genome numbers).

REPORT: one paragraph per item, SHA on origin/main, path, and the exact
commands you ran. Mark anything not done.
