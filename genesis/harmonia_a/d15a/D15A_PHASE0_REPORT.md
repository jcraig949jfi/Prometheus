# D15A_PHASE0_REPORT — dual verdict

Harmonia A (M2) · 2026-09-02 · Phase 0 of D15-A (Active Identifiability).
Two independent tracks, two independent verdicts (amendment A4). Design
frozen at commit 167e10efd (packet 85e50a619 + amendments R1).

## HEADLINE (do not collapse)

    D15A_PHASE0_GEN21            = ENGINE_QUALIFIED_WITH_LIMITATIONS
    D15A_PHASE0_SCIENCE_INSTRUMENT = SCIENCE_NOT_READY

    => CONFIRMATORY D15-A DOES NOT PROCEED. Both must be green; the
       science instrument is red. The GENERATOR must be redesigned
       before confirmation. The engine is ready; my worlds are not.

This is the intended function of Phase 0: I attacked both, the engine
survived with two recoverable limitations, and my own science
instrument DIED on its census — which is the correct, cheap place for
it to die.

## Track A — GEN-2.1 engine (release 5274ddbe, API 2.2.0, schema 3)

Attack results (D15A_GEN21_REQUALIFICATION.json). After correcting
THREE test-side bugs found during diagnosis (F4 header case-sensitivity;
F10 inherited artifacts carry their id in `source_artifact` not
`artifact_id`), all core + F1/F2/F3/F4/F5/F10-depth1 + A3-replay gates
PASS:
- prediction ordering (late-pred 409, commit-boundary, recommit
  idempotent, fork-mint blocked) PASS
- F1 content retrieval: native round-trips; imported bytes hash-match
  source; unimported + foreign both denied 403/404 PASS
- F2 ontology: success first-class; SUCCESSES_ONLY shares exactly
  {success}, rejects failure 403 PASS
- F3 binding: repeat-without-replication rejected; replication never
  re-adjudicates; FALSIFIED->SURVIVED impossible (monotonic) PASS
- F4 identity header X-SFE-Engine-Source-Hash on version, world, AND
  error responses PASS
- F5 idempotency: exact retry same object; changed-body+same-key 409;
  cross-world key scoped; no double debit on the budget-bearing call
  PASS (via raw HTTP)
- F10 cutoffs: native + import first_available_seq exact (before:no,
  at:yes); depth-1 fork inherits pre-fork frontier, excludes post-fork
  PASS
- A3 epistemic replay: warrant feature-vector bit-identical across a
  destroyed-and-reconstructed client process, from ledger+KnowledgeSet
  alone PASS

TWO DECLARED LIMITATIONS (filed as engine findings, both RECOVERABLE,
neither blocking D15-A's depth-1 fork design):
- **ENG-1 (P2)** at fork depth >= 2, an artifact the parent itself
  INHERITED loses its `source_artifact` id in the grandchild's
  KnowledgeSet (shows null). Its `content_hash` IS preserved and
  matches the original payload, so identity is recoverable by hash.
  Impact: deep-ancestry id-chains break; ancestry joins must key on
  content_hash, not source_artifact. D15-A uses depth-1 forks
  (one checkpoint -> sibling policy arms), so unaffected in practice.
- **ENG-2 (design question, P3)** a fork child sees inherited
  artifacts in its KnowledgeSet (origin INHERITED) but CANNOT read
  their content (404 "not visible"). Availability != readability by
  design ("availability != read != used"). Impact on D15-A: the
  counterfactual policy forks must reconstruct working state from the
  inherited EVENT ledger (observations/experiments/failures, which
  ARE readable), not from pre-fork artifact content. Recorded so the
  generator/runner respects it.
- Client plumbing note (P3): sfclient.experiment() lacks the
  `idem_key` kwarg the engine supports on the budget-bearing POST;
  tested via raw HTTP. Minor client gap for Daedalus.

VERDICT A: ENGINE_QUALIFIED for D15-A's actual usage (depth-1 forks,
ancestry keyed on content_hash, state reconstructed from event
ledger), with ENG-1/ENG-2 declared. The engine is FIT; the two
limitations are documented and designed around, not waved away.

## Track B — Science instrument (generator + census)

Results in D15A_INSTRUMENT_QUALIFICATION.json. The census REJECTED my
generator, correctly, on four counts:
1. **Repair-class equivalence is mis-implemented.** n_useful_classes
   came back 37-142 per world. My world-conditional equivalence keyed
   classes on the image over the ENTIRE reachable set, so almost no
   DSL terms collapse -- the whole "how constrained is the useful
   repair class" object is not actually being measured. The
   equivalence must collapse on the GOAL-RELEVANT frontier (the states
   whose reachability the repair changes), not on all of reach_full.
2. **Equivalent-repair (type G) worlds absent** (equiv_present: false)
   -- a direct consequence of (1); no syntactic candidates collapse
   into one class, so the EQUIV ladder rung does not exist.
3. **Population too small** (34/200 seeds instantiated). The
   target-outside-reach construction fails too often; the generator
   needs a constructive target placement, not rejection sampling.
4. **master-key census fails** (top hidden op 0.294 > 0.15) and
   **probe/goal orthogonality untested** (n=0: the info/goal vectors
   were degenerate under the broken class definition). Both are
   downstream of (1)+(3) and cannot be trusted until those are fixed.
PASSED: DSL-shortcut leakage 0/40; oracle-firewall canary clean
(the replay pipeline references zero oracle tokens).

VERDICT B: SCIENCE_NOT_READY. The generator does not yet instantiate
the intended repair-identifiability ladder. Required redesign before
any confirmatory science: (a) re-define world-conditional equivalence
on the goal-relevant frontier so classes actually collapse; (b)
constructive target/hidden-op placement to yield >=100 worlds/type
and the full A-G ladder incl. EQUIV; (c) re-run the census with the
per-type class-balance and master-key bands enforced by construction;
(d) re-test probe/goal orthogonality once classes are meaningful.

## The 10 report questions

1. Does the generator instantiate the repair-identifiability ladder?
   **NO** -- equivalence mis-defined; EQUIV rung absent; N too small.
2. Probe informativeness vs goal progress orthogonal? **UNTESTED**
   (degenerate under the broken class def; re-test after redesign).
3. Can useful repair classes be enumerated exactly? **YES** mechanically
   (every world yielded a finite enumerated set) -- but the EQUIVALENCE
   that makes the count meaningful is wrong (Q1).
4. Can the prospective estimator run without oracle contamination?
   **YES** -- firewall canary clean; replay pipeline references no
   oracle state.
5. Can every warrant decision be reconstructed from its legal frontier?
   **YES** -- A3 replay bit-identical from ledger+KnowledgeSet.
6. Fork inheritance exact under the real workflow? **YES at depth 1**
   (D15-A's usage); id-chain breaks at depth>=2 (ENG-1, recoverable).
7. Idempotency under aggressive retry? **YES** -- no dup objects/debits.
8. Evidence binding falsification-monotonic? **YES** -- F3 holds.
9. Does coverage threaten to confound active gain? **CANNOT ASSESS YET**
   -- the coverage-controlled analysis (amendment A1) needs the fixed
   generator; the tripwire+control machinery is designed and frozen.
10. GEN-2.1 qualified for D15-A confirmatory science? **YES, with
    ENG-1/ENG-2 declared** -- but confirmatory science is BLOCKED by
    the science-instrument redness, not the engine.

## Topology-2 (amendment A5)
Remains frozen at 6/90 under the prior pin. No F3/F5/F10 defect found
that alters epistemic history at depth 1; ENG-1/ENG-2 are new-release
semantics that did not exist when T2 ran. Recommendation: T2 may
RESTART clean under a fresh freeze against 5274ddbe if the topology
question is still wanted, but should NOT resume the suspended 6-cell
state across the qualification boundary. Decision deferred to operator;
D15-A generator redesign takes priority.

## Next action (not self-authorized past redesign)
Redesign the generator per Track-B (a)-(d), re-run Phase-0 Track B
only (engine stays qualified at this pin), and return an updated dual
verdict. No confirmatory execution until SCIENCE_READY + the pin is
re-confirmed. Do not protect the schedule.

## Artifacts
D15A_GEN21_REQUALIFICATION.json · D15A_INSTRUMENT_QUALIFICATION.json ·
D15A_ENGINE_DEFECTS.jsonl · D15A_SCIENCE_DEFECTS.jsonl ·
phase0_engine_attack.py · phase0_science_instrument.py ·
replay_pipeline.py · JOURNAL.jsonl. Design: D15A_DESIGN_PACKET.md +
D15A_AMENDMENTS_R1.md.
