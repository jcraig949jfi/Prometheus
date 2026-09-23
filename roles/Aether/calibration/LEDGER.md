# Aether calibration ledger

Currency: 2026-09-22. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. One row.

date | call made | what was true | corrected by | changed practice

2026-09-22 | Reported the NumPy "overflow encountered in scalar
multiply" RuntimeWarning as a NEW cosmetic regression introduced by the
memory-wall round's in-place `mix64_vec`, in the Phase 5 receipt, the
round report and the journal. | The warning PREDATED the round. The
previous expression form, `(x ^ (x >> 30)) * MIX_MUL_1`, warns
identically on a numpy scalar -- both forms route through the same
ufunc. The baseline A40 run emitted it too. | Direct experiment at the
start of the Phase A repair: ran both the old and the new form on a
scalar and on an array under `warnings.catch_warnings`, and got 1
warning for each form on the scalar and 0 for each on the array. | Do
not attribute an artifact to my own most recent change just because it
appeared in the first log I could read. The warning became VISIBLE this
round only because I fixed the `.gitignore` rule that had been
swallowing `*.log`, which is a change in observability, not a change in
behaviour. Before calling anything a regression, run the pre-change
code and check -- a one-line experiment here would have prevented a
wrong claim in three committed documents.

