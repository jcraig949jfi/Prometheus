# Dossier: sigma_kernel (Techne; the Sigma substrate kernel)

Audit group G3. Auditor: Hestia audit worker (read-only). Currency 2026-10-06.

VERDICT: SALVAGE_COMPONENT -- sigma_kernel is a provenance and promotion ledger (content-addressed append-only symbols, single-use capability tokens, a three-way BLOCK/WARN/CLEAR branch), not a cognitive substrate: nothing in it represents, searches, learns or composes. Its hash-locked caveat/provenance discipline is worth keeping as infrastructure for other engines, after the core PROMOTE double-spend race is fixed.

## 0. Identity

- Path: sigma_kernel/ (72 tracked files; 28 non-test .py modules, 11,039 lines; 6 SQL
  migrations). Core: sigma_kernel.py (1514 lines). Sidecars: bind_eval.py, bind_eval_v2.py,
  residuals.py, caveats.py, method_spec.py, exclusion_certificate.py, coordinate_chart.py,
  triangulation_protocol.py, operator_portability.py; math probes a148_*/a149_*/a150_*.
- Seat: Techne (per the task brief; README points at the harmonia/memory/architecture
  spec). Last commit touching sigma_kernel/ = 6eeb1c823; core file last changed 71652470e
  (2026-05-08).
- Consumers: git grep finds imports from prometheus_math (32 files, e.g. discovery_env*.py,
  bsd_rank_env.py), charon (28), ergon (2), aporia (2). These are math RL/cartography
  environments, outside this audit's population (AUDIT_PLAN s1 exclusions).
- READ IN FULL: omega_oracle.py; sigma_kernel.py lines 100-135, 150-221, 424-520,
  700-940, 1118-1140, 1294-1320; migrations/001; README.md lines 1-80; bind_eval.py lines
  1-60; RESIDUAL_PRIMITIVE.md lines 1-40.
- NOT READ: the rest of sigma_kernel.py (CLAIM body, ERRATA, TRACE, REWRITE/EQUIV bodies),
  bind_eval*.py bodies, residuals.py body, every math probe (a148/a149/a150, curvature,
  lehmer charts/certificates), all tests, the harmonia architecture spec and the 25-round
  council synthesis it cites.

## 1. Mechanism

- Storage: three tables -- symbols (PRIMARY KEY name, version; def_hash = sha256 of a JSON
  blob), claims, capabilities (sigma_kernel.py:156-209; migrations/001). "Append-only" is
  enforced for symbols by the primary key and by the API not issuing DELETE; claims and
  capabilities are mutated by UPDATE (migration 001 comments, lines near the GRANT block).
- Opcodes are Python methods: RESOLVE (fetch + hash check, :509), CLAIM (:574), FALSIFY
  (:709), GATE (:801), PROMOTE (:822), ERRATA (:936), TRACE (:1023), REWRITE (:1118),
  EQUIV (:1294).
- FALSIFY ships the claim to a subprocess oracle (:709-765). The shipped oracle,
  omega_oracle.py:39-69, parses exactly "mean OP value" and compares it with an
  evidence field true_mean that the caller supplies: CLEAR if satisfied, WARN if it misses
  by < 1.0, BLOCK otherwise. All epistemic work is the caller's; the kernel records it.
- GATE (:801-819) is a three-way branch on that verdict: BLOCK raises, WARN prints and
  returns "WARN", CLEAR returns "CLEAR". The "three-valued gate" is an enum switch.
- PROMOTE (:822-934) checks the capability row, checks the verdict is not BLOCK, writes a
  new version of the symbol with caveats and precision metadata folded into the hashed blob
  (so caveats cannot be dropped without changing the hash; :868-898), and marks the
  capability consumed.
- REWRITE and EQUIV RECORD that a rewrite or equivalence was asserted, with a witness
  reference; "the actual transformation logic ... is the caller's responsibility"
  (:1134-1137). They do not rewrite or check anything mathematical themselves.
- BIND/EVAL (bind_eval.py:1-33) register an import path + cost model and run the callable
  under a budget, recording output as a symbol: a sandboxed function-call ledger.

DOCUMENTED vs CODE:
- "Linear capability tokens ... linearity holds across process boundaries"
  (sigma_kernel.py:113-117). The core PROMOTE does a SELECT on consumed (:832-842) and
  later an unconditional UPDATE capabilities SET consumed=1 WHERE cap_id=? (:899) without
  "AND consumed=0" and without a rowcount check. Two processes holding the same token can
  both pass the SELECT and both promote (a time-of-check/time-of-use race under concurrent
  Postgres sessions). The same unconditional UPDATE appears at :995, :1261, :1449 (ERRATA,
  REWRITE, EQUIV). The sidecars do it correctly (compare-and-set + rowcount at
  bind_eval.py:565-571, bind_eval_v2.py:76-81, residuals.py:623-628), so the fix exists in
  the same directory and was not back-ported. Linearity across processes is therefore
  CLAIMED for the core opcodes, true only for sequential use. (Static reading; not executed.)
- "Falsification-first promotion": true in the narrow sense that PROMOTE refuses a claim
  with no verdict or a BLOCK verdict (:844-850). The falsifier shipped is a threshold
  comparison on a caller-provided number.
- "Substrate" / opcodes / "symbolic half of the grammar": names for database operations.
  Nothing executes a symbol's content.

## 2. Evidence

OBSERVED (files on main, glanced): a148_validation_results.json reports a math-sequence
probe with verdict INCONCLUSIVE ("Cannot evaluate transfer at this n"), and an A149 signature
that kills 5/5 strict matches vs 1/54 non-matches. That is a mathematical-data result
routed through the kernel, not a property of the kernel.
CLAIMED: README/spec claims of epistemic discipline; the tests (test_bughunt.py,
test_bind_eval_v2.py property tests) were not run or read beyond test names. A cross-process
double-spend test exists only for the bind_eval path on Postgres
(test_bind_eval_postgres.py:156), not for core PROMOTE.
DESIGNED: GENESIS protocol, quorum-issued capabilities (both marked STUB at :476-479,
:495-497), spectral oracle (RESIDUAL_PRIMITIVE.md "deferred").

## 3. Matrix

3a. Combinatorial explosion and reachability: not applicable -- the kernel performs no
search. Its state space is a growing set of (name, version) rows; every operation is O(1)
or O(index). There is no reachability question because nothing is generated.

3b. Cosplay vs foundation: the vocabulary (substrate, opcodes, kernel, GATE, Omega oracle,
REWRITE/EQUIV "subsume cleanly into a CoC kernel") borrows from type theory and OS kernels,
but the mechanism is a CRUD ledger with hashes and a single-use flag. Calling it a cognitive
substrate would be cosplay; calling it a provenance kernel is accurate. Its ceiling as a
reasoning substrate is zero: it never computes a consequence of a stored symbol. As a
ledger it is competent and its caveat hash-lock is a genuinely good idea.

3c. Substrate bottlenecks (as a ledger): the oracle stub accepts one hypothesis grammar;
the hash covers a JSON blob so semantic equivalence of two claims is invisible (EQUIV only
records an assertion); the core capability race (above); WARN propagation in GATE is a
print statement (:812-818) -- the caller must carry it, though PROMOTE does fold FALSIFY's
WARN into caveats (:779-783).

## 4. Deliverable

Discovery Approach. It does not attempt to generate the physics of intelligence. It
enforces bookkeeping around claims that other engines (mostly math RL environments)
generate: every promoted symbol is content-addressed, versioned, carries its falsification
verdict and caveats inside its hash, and can be traced.

The Brick Walls.
1. Zero cognitive mechanism: 0 of 9 opcodes compute anything about a symbol's content;
   the shipped falsifier is a 3-token threshold parser (omega_oracle.py:39-69).
2. Linearity gap: 4 unconditional consume UPDATEs in the core (:899, :995, :1261, :1449)
   vs 3 correct compare-and-set sites in the sidecars.
3. Scope creep risk: 11k lines of math probes and certificates now live in the "kernel"
   directory, mixing a small, auditable ledger with domain experiments.

Seed Viability. Not a cognitive seed. Salvageable component: the content-addressed,
caveat-hash-locked promotion record, as the provenance layer under any engine that claims
a mechanism (it maps cleanly onto Moonshot's R-EP semantic identity and the RSO's typed
verdicts).

Evolutionary Roadmap (as infrastructure, not cognition).
1. Back-port compare-and-set (UPDATE ... WHERE cap_id=? AND consumed=0; check rowcount) to
   PROMOTE, ERRATA, REWRITE and EQUIV; add a two-process race test for each.
2. Split the directory: kernel (sigma_kernel.py + migrations + caveats) vs domain probes
   (a148/a149/a150, lehmer, curvature) into their owning seats' trees.
3. Replace the oracle stub's role with a typed interface to real checkers (the RSO
   predicates, a proof assistant via EQUIV witnesses of type proof_ref) so FALSIFY means
   something beyond a threshold.
4. If anyone wants it to become a reasoning substrate, the honest path is a different
   project: a term-rewriting engine whose rewrite rules are executed and checked (confluence,
   termination), with this ledger recording the derivations. That is a new engine, not an
   evolution of this one.

THE ONE decisive experiment. A concurrency test: two processes on the Postgres backend
each PROMOTE with the same unconsumed capability, 1000 trials with randomized interleaving.
Kill criterion for the linearity claim: any trial producing two symbols from one token
falsifies "linearity holds across process boundaries" for the core opcodes; pass = 0/1000
after the compare-and-set fix.

## 5. What would change this verdict

- To DEAD_END: if the ledger is redundant with an existing fleet provenance layer (Moonshot
  R-EP CAS, the RSO receipts, the evidence wiki) such that no consumer needs it; I did not
  survey those overlaps.
- Nothing in the read code could move it to VIABLE_SEED as a cognitive substrate; the unread
  REWRITE/EQUIV bodies are documented as recording-only (:1134-1137).
- The race finding is from static reading; a test showing the Postgres path serializes
  PROMOTE would withdraw Brick Wall 2. What I saw argues against it: the Postgres adapter
  (sigma_kernel.py:260-410; I grepped it, did not read it) shows only autocommit=False (:294) and no isolation setting, i.e. the READ
  COMMITTED default, under which the second unconditional UPDATE waits for the first commit
  and then also succeeds.
