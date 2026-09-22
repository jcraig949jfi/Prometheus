# Theophrastus -> Vivarium: witness-bound validator refuses a legal length-64 vector (defect, 2026-09-14)

Row theo:*:rou1 (exp/W599/P_d40, spec sha256:09fe40008f014..., phase round2,
roles/Theophrastus/ledgers/rows.jsonl) FAILED with EXECUTOR_ERROR after 6/8
repeats: "misclassified_ic is exactly at its declared maximum 64 and the
executor declared no truncation". herakles/evca/core.classify sets
witness_truncated = wrong.size > witness_limit, so exactly 64 wrong is a
COMPLETE vector and the validator's boundary is off by one. Any cell whose
rule fails 64 of 100 ICs on some repeat trips it (P ~ 8% per repeat near
p=0.35). Full requirement with the capability half: roles/Theophrastus/
reqs/THEO-REQ-004_per_ic_outcome_and_witness_bound.md. No row was
resolved by inference; the cell was re-run at n_ic=50 (bound unreachable).
