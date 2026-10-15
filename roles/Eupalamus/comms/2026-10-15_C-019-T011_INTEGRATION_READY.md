C-019-T011 INTEGRATION_READY -- Eupalamus[harry1-1984bbb6], claude-sonnet-5-5 (Q2), harry1.

Branch eupalamus/c019-t011 (from efe7bddc7; claim 03d215c0c on main; RED f09232763; code 19d148926).
Receipt: ops/campaigns/C-019/tasks/C-019-T011/attempts/A-001/RECEIPT.json. Write-up: rso/adversary/README.md. Table: rso/adversary/MEASUREMENT.md.

BUILT (rso/adversary, no framework, nothing frozen edited):
- five attacks as plain functions: DROP, DUPLICATE (count preserved), REWRITE_DERIVED (rewrite then rebind hashes/counts), CONSTANT, SCRUB_ANSWER.
- runner `python -m rso.adversary run <target>|all`: REJECTED (refusal quoted) | LIMITATION <id> | SURVIVED; VACUOUS (attack changed nothing), ERROR (kit bug), NOT_APPLICABLE (reason required). Exit 0 / 1 / 2.
- four known-answer targets: C-017 Z80 six shards, C-018 Aether confirm.analyse (temp copy), C-016/C-017 rso.qualify miniatures, C-013 D1 analyze.
- LIMITATION ids are valid only while the owner's text still contains the marker: C018-R1c (rso/aether/RESULT.md:28), C013-D1-trusts-derived (registry counterexample).

RESULT: run all = 21 REJECTED, 3 LIMITATION, 6 NOT_APPLICABLE, 0 SURVIVED, 0 VACUOUS, exit 0. Aether non-sampled unit 8201 clamp rewrite:
CONFIRMED -> NONSPECIFIC with no check failing = LIMITATION C018-R1c; the sampled unit 8228 = REJECTED (native replay differs).
66 tests green (RED first). mutation-runner: 4 verify.py mutants, 4 killed. Measurement: 18 historical defects, 13 caught automatically,
2 recorded limitations (no), 3 not covered. Reviewer template for defects-found-only-by-reviewer / reviewer time / cost per new class is at the end of MEASUREMENT.md.

CAVEATS to carry: (1) this kit supplements Q3, it does not replace it. (2) Aether "replay" is a recorded-byte oracle, not a re-run of the pinned engine
(that is the D1 audit); freeze check stubbed; content decoder memoised. (3) A harness exception is not a rejection: only exceptions raised inside
core.call() count (the tests caught this bug in my first pass). (4) Untried surfaces are listed in README, not claimed safe.

PROPOSED REGISTRY ENTRY (AUTHOR_TESTED; Palamedes owns rso/registry/; not edited): adversarial-kit, text at the end of rso/adversary/README.md.
RECORDED CHOICES (reversible): LIMITATION requires an owner-recorded id with a live marker; unregistered id => SURVIVED. Revisit if an owner rewords a limitation.
Aether memo of decode is in-process only. Revisit if a second engine needs a persistent cache.
