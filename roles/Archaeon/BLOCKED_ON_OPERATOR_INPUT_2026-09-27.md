# Archaeon -- items BLOCKED_ON_OPERATOR_INPUT (recorded 2026-09-27; no values guessed)

## Azure E8s v5 compute placement (TODO 2026-09-25) -- BLOCKED_ON_OPERATOR_INPUT
Exact inputs needed from the operator:
1. The Azure subscription and resource group to use (names or ids).
2. WHICH existing GitHub Actions start/stop workflow ("mso/jfi pipeline") to copy: repository and workflow path.
3. The secrets mechanism: which GitHub Actions secret names hold the Azure credentials (Archaeon will never read or print them).
4. The spend ceiling per run or month, and whether spot (evictable) is allowed.
Not needed from the operator: the VM size estimate (E8s v5 / E16s v5 comparison is recorded) and the engineering-block sizing run
(Archaeon can do it once 1-4 exist).

## Commit-aware admission gate for Archaeon heavy jobs (TODO 2026-09-25) -- NOT blocked on operator input
Archaeon can build it for its own jobs from measured per-worker peak commit. The only operator question is optional: whether to
offer it fleet-wide (other seats opt in; never imposed). Not started under the Contract v0.2 directive (out of scope).

## Aphrodite Campaign 1 requests #452 #472 #475 #492 #534 -- untouched, pending separate operator triage (ruling 2026-09-27 s7/s18)
