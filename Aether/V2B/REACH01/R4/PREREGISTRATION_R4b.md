# REACH01 R4b preregistration: geometry control for the R4 promotion advantage (assisted control)

Question: does R4's promotion advantage (P 8/8 vs 0/8) depend on the insert operator being able to shift a component
copy by exactly +3 rows, which maps the component's row-6 relay onto input C's row 9?
Arms (same component, task, budget and seeds 0-7, and the same P arm as R4, i.e. identical rng streams except for the
vertical offset draw):
  Pno3  vertical insert offsets {-3, -2, -1, 0, 1, 2} (the +3 alignment excluded); horizontal [-3, 3] unchanged
  Pdy0  vertical insert offset {0} only (horizontal relocation only)
Prediction if the advantage is row-alignment duplication: Pno3 and Pdy0 acquire COMBINE3 in <= 2/8 seeds each.
Disposition:
  ALIGNMENT_DEPENDENT   both <= 2/8
  ALIGNMENT_INDEPENDENT both >= 6/8 (the advantage survives without the aligning shift)
  PARTIAL               otherwise
Reported as ASSISTED CONTROL. No R4 result is changed by R4b.
