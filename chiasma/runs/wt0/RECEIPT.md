# WT-0 receipt (known-answer geometry), 2026-10-07T09:25:08Z

Command (repo root): python -B -m unittest discover -s chiasma/tests -t .
Result: chiasma/runs/wt0/unittest_output.txt (18 tests, rc=0).

Mutation check: python -B -m chiasma.wt0_mutation
Result: chiasma/runs/wt0/mutation_summary.json -- 16 planted one-line defects,
16 KILLED, 0 SURVIVED, 0 NOT_APPLIED.

History, kept: the first mutation pass killed 14/16. M02 (exception objects keep f)
survived because the test only required exceptions to exist; M11 (random shadow
keeps content) survived because the test only checked mask size. Both tests were
strengthened (exception RATE within +-4 sd; random shadow content differs from the
honest projection and leaves the support). Two vacuous guards found on reading
were also removed before the first mutation pass (a self-comparison in the shadow
compression test; a cap test that went vacuous when over budget).

Limits: these are the author's own mutants (AUTHOR_TESTED). An outside first-sight
challenge has not been run.

git blob ids (world, organisms, runner, test_wt0): 89afd3779c3bcbe157c33560713e7928984f6680 24c13276908c67699ccc17c4513a022d7a52126b 13e2e4ca894c38b2222202c6595fed8adb6bea04 6fe5c4fe5c779b0f761922c4117b4484cbbe6899 
