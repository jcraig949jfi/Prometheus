# Donor Foundry closeout -- the operator's eight questions, answered from measurement

Currency: 2026-09-12T01:30Z. Techne, worktree Prometheus-worktrees/techne-pass-0911, base
d109add9b. Directive: roles/Techne/prompts/2026-09-11_donor_foundry/OPERATOR.md
(sha256 0b8b6177...f2a79). Every number below is produced by a committed script and can be
regenerated:

    python -m techne.scripts.donor_disposition   --out <json> --txt <txt>   (donors)
    python -m techne.scripts.forensic_inventory  --run-tests --out <json> --txt <txt>
    python -m techne.acquisition.checks.scipy_resampling_check

The Gen-0 handoff (techne/TECHNE_GEN0_DONOR_HANDOFF.txt, 2026-08-31) was read and then
DISTRUSTED as instructed; what follows is the tree on 2026-09-12, not the handoff.

## 1. What donor capabilities does Prometheus actually possess?

Measured in the default interpreter (Python 3.12.10) from a fresh process; "installed"
is importlib.metadata, "import" is a subprocess import, "direct" is tracked non-test .py
files outside techne/ that import the donor, "via" the same through a wrapper.

    donor               installed   import   wrap  ctrl  direct  via   labels
    ------------------  ----------  -------  ----  ----  ------  ----  ---------------------------------------------
    tensorly            0.9.0       IMPORTS  2     3     4       0     ACQUIRED IMPORT-TESTED WRAPPED CONTROLLED CONSUMED
    pyribs (ribs)       0.12.0      IMPORTS  3     3     1       0     ACQUIRED IMPORT-TESTED WRAPPED CONTROLLED CONSUMED
    discopy             1.2.2       IMPORTS  1     1     0       0     ACQUIRED IMPORT-TESTED WRAPPED CONTROLLED
    egglog              13.2.0      IMPORTS  2     1     1       0     ACQUIRED IMPORT-TESTED WRAPPED CONTROLLED CONSUMED BLOCKED
    cvc5                1.3.4       IMPORTS  1     2     0       0     ... WRAPPED CONTROLLED BLOCKED SUPERSEDED (by z3)
    stitch              isolated    FAILS*   2     2     0       0     ACQUIRED(isolated env) WRAPPED CONTROLLED BLOCKED
    z3                  5.0.0.0     IMPORTS  2     1     5       3     ACQUIRED IMPORT-TESTED WRAPPED CONTROLLED CONSUMED BLOCKED
    hypothesis          6.165.10    IMPORTS  2     1     2       0     ACQUIRED IMPORT-TESTED WRAPPED CONTROLLED CONSUMED
    cvxpy+CLARABEL+SCS  1.9.2       IMPORTS  2     2     5       0     ACQUIRED IMPORT-TESTED WRAPPED CONTROLLED CONSUMED BLOCKED
    Lean 4 + mathlib4   v4.30.0     runs**   2     yes   1       0     ACQUIRED IMPORT-TESTED WRAPPED CONTROLLED CONSUMED
    scipy resampling    1.17.1      IMPORTS  0     1     22      0     ACQUIRED IMPORT-TESTED CONTROLLED CONSUMED (new receipt)
    dreamcoder          -           N/A      1     1     0       0     CANDIDATE BLOCKED (TECHNE-15 build, -16 licence)
    POET                -           N/A      0     0     0       0     CANDIDATE PARKED to 2026-12-11
    SDPA-GMP            -           N/A      0     0     0       0     CANDIDATE (no consumer declared the requirement)
    MOSEK               -           N/A      0     1     0       0     REJECTED (struck 2026-09-11)

    *  stitch_core is installed in the ISOLATED tool env (TECHNE_TOOL_CACHE; lock
       techne/acquisition/locks/stitch-cp312-win-amd64.lock.txt), not the default
       interpreter; the Rust core is built from the pinned MIT revision. A default-
       interpreter import failure is not ABSENT.
    ** Lean is not a pip distribution: elan toolchain leanprover/lean4:v4.30.0 plus the
       lean-repl and mathlib4 builds in the canonical checkout's gitignored external_deps/.

Full rows with the consumer paths: roles/Techne/DONOR_DISPOSITION_2026-09-11.txt.

## 2. Which of them execute today?

Every installed donor above imports in a fresh process. Executed beyond import this pass:
tensorly, pyribs, discopy, egglog, cvc5 (adapter battery, 58 passed 4 skipped); z3 and
hypothesis (techne/tests/test_acquisition.py, 32 passed); cvxpy/CLARABEL/SCS (gap fixture,
146 solver runs); Lean (32 of 32 proof-search and runtime tests against the real REPL --
see section 6); scipy (the new resampling check). stitch executed on 2026-09-11 (receipts
...074111Z, ...094436Z), not re-run here. DreamCoder, POET, SDPA-GMP, MOSEK do not execute.

## 3. Which have real controls?

A "real control" here is a positive, cheat, parity or ground-truth check of the CAPABILITY,
with the path quoted. Adapter engineering tests (T1-T10) are counted separately.

    tensorly      TT bond-rank parity 5/5 vs quimb, truth by construction (donor_tensor_parity)
    pyribs        identical retained set vs Archaeon's independent behavioral policy, 150 rows,
                  12 sealed queries (receipt ...pyribs-20260911T065018Z)
    z3            exhaustive 2048/2048 parity vs proteus truth_table, every witness validated
    hypothesis    SOUND 45/45, NOT MINIMAL 24/45 (usefulness NOT established)
    cvxpy/...     positive + cheat + negative + bound, 17 tests; every arm ground-truth scored
    stitch        17/17 expansion-correct; Vivarium leak check as the verdict
    Lean          32 integration tests with known proofs (positive controls; NO cheat control)
    scipy         40/40 concordant on a planted effect, 40/40 p-values within MC error on
                  exchangeable data, label-blind cheat 0/40
    discopy       adapter battery ONLY (T1-T10): no capability control exists
    egglog        adapter battery ONLY, plus Ergon's negative result on RM genotypes
    cvc5          6/6 QF_LIA agreement with z3 (a parity control that proved redundancy)

## 4. Which are actually consumed?

    CONSUMED, by import, outside techne/ (tracked, non-test):
      tensorly    evidence_wiki/ew/compiler.py + benchmarks (Mnemosyne, 2026-09-01),
                  cartography dissection_tensor (2026-04), prometheus_math wrapper
      pyribs      agents/hephaestus/src/diversity_forge.py (2026-05, direct)
      egglog      ergon/gen0/family_b_probe.py (2026-08-31; a NEGATIVE result: Family B
                  needs a synthesis layer egglog does not supply)
      z3          charon erebos predicate handles, harmonia m0_anticalibration + z3_backend
                  (+ verifier_lens, denominator_impact, falsecert battery through it),
                  prometheus_math.optimization
      hypothesis  proteus/eval/hypothesis_strategy.py (2026-09-11), prometheus_math
                  adversarial_fixtures
      cvxpy       prometheus_math optimization / _qp / _sdp / _socp; Elenchus verify_sdp_family
      Lean        agents/_shared/proof_search (walk_1 bridge; fixture jsonl missing)
      scipy       22 files already
    CONSUMED by ARTEFACT, not import:
      pyribs      Techne's H3 comparator receipts were read by Archaeon's H3 scoring
                  (sealed manifest de4cae9b); the adapter is not imported by them
    NOT CONSUMED:
      discopy     0 anywhere.  cvc5  0 anywhere.  stitch  0 (Archaeon has its own extractor
                  and stitch returned 0 abstractions on the held-out-legal corpus).
      techne.lib.donors -- THE GEN-0 ADAPTER CONTRACT ITSELF: 0 importers outside techne/
                  after 11 days. Every consumer that arrived went DIRECT to the donor.

The ugly condition the Gen-0 inventory named (installed, unused) is therefore half true
today: the DONORS acquired callers; the ADAPTER LAYER did not. The one thing the adapter
carried that direct callers lose is the declared native_selection_relation (which
objective the donor already optimised). That is recorded here as a handoff, not fixed
with more adapter code: a layer nobody reached for in eleven days is not made reachable
by usage exemplars.

WAS THE CHEAPEST REMAINING ACTION (usage exemplars) EVER DONE? No. techne/DONOR_INVENTORY.md
has one commit (2026-08-31) and no exemplar. Given the finding above, it is not being done
now either; the disposition file is the exemplar of record ("here is who consumes it, how").

## 5. Which unfinished acquisitions from the original mission still matter?

    stitch (D-17 v1)     Matters ONLY if an H1/H0 corpus ever yields an abstraction with
                         arity > 0. Two rows: bindings dev-only on licence (operator
                         amendment pending); Rust core MIT and export-clean. TECHNE-43
                         (eight boundary fixtures) is RE-PREMISED: not before a consumer.
    B2 Family A vs B     Never ruled by Lexis; RESOLVED BY MEASUREMENT instead -- Family B
                         (egglog) needs a synthesis layer (Ergon 2026-08-31) and Family A
                         (stitch) finds nothing to abstract on real H1 output (Techne
                         2026-09-11). Neither family has a live consumer. Recorded, not ruled.
    B3 cvc5 segfault     Still worked around by ordering, not by a test; moot if cvc5 is
                         retired (TECHNE-51, operator).
    B5 zero callers      Answered above: donors yes, adapters no.
    pyribs CVT/Sliding   TECHNE-03/04: only when Ludus/Archaeon ask for an H3 beta comparator.
    DreamCoder           TECHNE-15/16: Nyx delivered a DreamCoder-shaped organ independently;
                         Techne's build is a reference arm nobody has queued. PARKED.
    SDPA-GMP             TECHNE-39: the only certificate route; waits on TECHNE-46 (Harmonia).

## 6. What did I finish?

    TECHNE-45   every arm of the SDP gap fixture correctness-scored; 0/26 rows change class
    msg 151     forensic inventory for Necropolis: 44 instruments, import-tested, callers
                by git grep, tests executed (26 PASS / 17 NO_TESTS / 1 FAIL), controls
                quoted or NONE; roles/Rhadamanthus/INBOX_TECHNE_FORENSIC_INVENTORY_...
    TECHNE-48   the Lean donor executes from any worktree. From a D-23 worktree the
                whole Lean battery reported 16 SKIPPED ("lean-repl not built") because
                the tests derived external_deps from __file__ and the build is host-
                local in the canonical checkout only. locate.py resolves it (env, this
                tree, canonical root -- each checked for the REPL binary). Measured:
                31 passed 3 skipped in 39 s warm; first cold start of the mathlib cache
                took 143 s and exceeded the 600 s session timeout once.
    TECHNE-47   scipy.stats.permutation_test qualified as the mature replacement for the
                tree's 124 hand-rolled resampling loops (receipt quoted above); handed
                to Nemesis and Rhadamanthus; no code in the tree was changed.
    TECHNE-50   this disposition, derived by script.
    TALOS-10    NONE, with the two declarations that would change it.

## 7. What did I kill?

    - the reading "Lean is dead" (it was a path bug in nine test files)
    - my own first certificate lower bound (infeasible; the bound control caught it)
    - my own first positive-control gate for scipy (unattainable at power 0.8; recorded
      as a deviation, gate moved to the attainable range before run 2)
    - TECHNE-43 as written (re-premised, original kept verbatim)
    - the claim implicit in DONOR_INVENTORY.md that the adapter contract is the route
      consumers take (it is not; 0 importers)
    - MOSEK was already struck 2026-09-11; nothing here revives it

Not killed, recommended for a human's decision: discopy and cvc5 adapters (TECHNE-51).

## 8. What remains blocked, and on whom?

    operator     D-17 v1 (stitch rows); TECHNE-06 (upstream licence ask); TECHNE-09
                 (packet JSONs); TECHNE-16 (DreamCoder licence); TECHNE-32 (Magma);
                 TECHNE-51 (retire discopy/cvc5 or name a consumer)
    Harmonia     TECHNE-46 accuracy requirement (gates TECHNE-39 SDPA-GMP)
    Archaeon     comms/tests/test_identity.py 5/18 failing on this host (TECHNE-53)
    Mnemosyne    evidence_wiki tests mutate two tracked JSONs (TECHNE-52)
    Ludus/Arch.  TECHNE-03/04 pyribs CVT / SlidingBoundaries, on request only
    H4 1.0       TECHNE-17 POET

## What this closeout does NOT say

No donor here has been shown to earn scientific rent. A control on a capability is not a
result about a bench. The forensic inventory ranks by a declared formula over engineering
evidence, not by forensic truth; Rhadamanthus owns that. Consumption counts are import
counts over tracked files: a seat that vendored a donor into an untracked directory is
invisible here by design.
