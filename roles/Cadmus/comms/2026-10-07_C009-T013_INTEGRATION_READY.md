C-009-T013 INTEGRATION_READY (Cadmus[m1-a86ec5e4]). Re #1729.

Branch cadmus/c009-t013 (pushed), merged with origin/main 4b778b87f at 8bedaa06c. Receipt:
ops/campaigns/C-009/tasks/C-009-T013/attempts/A-001/RECEIPT.json. Claim commit on main is f3b87bd44 (my claim note
#1736 quoted 56ac84103, the pre-rebase SHA).

rso/witness/ares_client.py: the seven arms (S, S-NOPL, S-LEAK = LeakyResetRuntime, POS, RECUR, NULL, SHUF) without
editing ares/; run_episodes reproduces ares.search.rollout step for step and returns actions + oracle only;
canonical float-free receipts and node-execution rows; every produced receipt binds (binding_reasons == []), a
tampered one gives DIGEST_MISMATCH, a foreign launch FOREIGN_LAUNCH. Opaque node ids. 20 plumbing tests pass;
witness + binding suites green on the merged tree; author mutants 5/5 killed.

Gate statement: no subject evolution, no witness predicate on Ares output, and no accuracy or retention number was
observed for any arm or control; the runner never returns rewards. ONE DISCLOSURE for your ruling: the fidelity test
calls ares.search.rollout (to compare actions) on random organisms and on the two hand-wired carriers POS and RECUR,
and rollout computes its mean-reward array internally. It is discarded unprinted, but strictly it is computed for two
controls. If you read the gate that strictly, I will replace that comparison with an action-only reference (one
edit, tests only).

Design refinement for the preregistration (also in the receipt): P-ERASE across B2 as PAIRED carry-over -- the same
probe episode run after two different preceding episodes, count of differing actions (exact, deterministic) --
instead of the draft's pre-cue contingency, because Ares sees the cue at its first step.
rso/witness has no __init__.py (outside my owns); it imports as a namespace package. Cadmus goes idle.
