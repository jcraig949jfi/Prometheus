# Retired donor adapters -- the record (TECHNE-51)

Currency: 2026-09-12. Ruling: the operator, verbatim at
roles/Techne/prompts/2026-09-12_techne51_ruling/OPERATOR.md (MANIFEST.md beside it).
Recommendation that led to it: roles/Techne/DONOR_FOUNDRY_CLOSEOUT_2026-09-12.md section 7;
evidence: techne/acquisition/DONOR_DISPOSITION_2026-09-11.json (script
techne/scripts/donor_disposition.py, re-runnable).

## What was retired

    adapter                      moved from                            reason (measured)
    ---------------------------  ------------------------------------  -------------------------------------------
    techne.lib.donors.discopy    techne/lib/donors/discopy_adapter.py  0 importers anywhere on the tree, 11 days
    techne.lib.donors.cvc5       techne/lib/donors/cvc5_adapter.py     0 importers anywhere; SUPERSEDED as the SMT
                                                                       route by z3 5.0.0.0 (qualified 2026-09-10:
                                                                       2048/2048 parity; 5 direct consumers)

Both files are here VERBATIM (git mv; one import line changed from `.contract` to
`..contract`, marked in the file). Their Gen-0 receipts stay where they were:
techne/donor_inventory.json, techne/donor_smt_comparison_2026-08-31.json (the 6/6 QF_LIA
parity that proved cvc5 redundant), techne/dependency_vetting_gen0_2026-08-31.json (identity
RESOLVED for both), and the handoff techne/TECHNE_GEN0_DONOR_HANDOFF.txt sections 9 and 11.

## What was deliberately NOT retired

- THE DONORS. DisCoPy 1.2.2 and cvc5 1.3.4 remain installed, pinned in
  techne/requirements-donors.txt, and remain CANDIDATES on their own evidence. A consumer
  that needs typed string diagrams, or an SMT theory z3 lacks (finite fields, sequences,
  bags, separation logic, SyGuS), consumes the donor DIRECTLY and cites the receipt. The
  operator's words: "Do not retire DisCoPy or cvc5 themselves from consideration merely
  because their Techne adapters were unused."
- THE TESTS. techne/tests/test_retired_adapters.py runs the contract battery's load-bearing
  checks (identity, config echo, determinism, strictness, selection relation, typed failure)
  against both retired modules, and asserts the registry gate: `get` refuses, `available`
  excludes, `include_retired=True` reaches them. A retired adapter that silently rots is a
  history nobody can reconstruct.
- THE cvc5 LESSON. Raising while a live cvc5 TermManager/Solver is in the frame segfaults
  the interpreter at teardown on this platform (exit 139 AFTER pytest reports PASS). The
  retired adapter validates its whole payload before constructing any cvc5 object and drops
  every native handle before returning. Any future direct cvc5 consumer inherits that
  discipline from the file, not from memory.

## What the ruling changed for every future donor

    DEMAND -> FIND -> PIN -> EXECUTE -> CONTROL -> RECEIPT -> CONSUME
    -> WRAP only when the consumer requires an interface Prometheus does not already have.

The universal adapter contract (native_selection_relation on every artifact as the
required provenance route) is no longer required. The three live adapters (tensorly,
pyribs, egglog) stay because they are tested and cost nothing; none is a precondition for
consuming its donor, and the disposition file shows every consumer that arrived went direct.
