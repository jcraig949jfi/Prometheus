# D16-C PHASE 0 REPORT

Harmonia C. 2026-09-02. Design packet v1.1 (`D16C_DESIGN_PACKET.md`,
sha256 5189b617...) with the four review amendments applied.

Engine under test: SFE GEN-2.1, `engine_source_hash
sha256:5274ddbe9120ddbbd75a36965106d2efe640a3b72278e7bb97b82e356e1fc9fc`,
API 2.2.0, schema 3. Every engine measurement in this report was taken on
a **private pinned instance** (`http://127.0.0.1:8899`, same source hash
verified via `x-sfe-engine-source-hash`, scratch SQLite DB). The live
engine at `192.168.1.202:8811` was not touched: no ecology, no bursts,
no Daedalus window was announced. No Harmonia A or B output was read or
imported. No confirmatory ecology science was run.

Directory: `D:\Prometheus\genesis\harmonia_c\d16c\`.

## 0. Bottom line

Phase 0 ran steps 1-9 of the mandated order and **stopped at step 10**.
Step 5 found that GEN-2.1 launders imported knowledge into native export
(6/6 variations). Under Amendment 2 that is `GEN21_ORIGIN_LAUNDERING =
CRITICAL`, a blocking engine gate: the pilot (step 10) and the
threshold/N freeze (step 11) are **HELD**; a minimal reproducer is filed
for Daedalus. Steps 6-9 (engine characterisation, no ecology science)
were completed because they feed the same defect packet.

The five verdicts, never collapsed:

```
D16C_BENCHMARK_QUALIFIED     YES   LT instrument sound; BC killed (SD-001);
                                   synthesizer VERIFY_ONE->VERIFY_K (SD-002)
D16C_CAUSAL_AUDIT_QUALIFIED  YES   AVAILABLE/CONSUMED/NECESSARY computable
                                   on-engine, 20/20 match design; caveats:
                                   read F10 at cutoff seq (ED-003), CONSUMED
                                   is CLIENT_ASSERTED
D16C_CROSSING_QUALIFIED      NO    ED-001 CRITICAL laundering; ED-002 evidence
                                   independence not representable; ED-003
                                   F10 provenance rewrite
D16C_CONCURRENCY_ENVELOPE    16    C1 1-16 all invariants PASS (p95 0.67 s);
                                   C2 32-1024 all invariants PASS, no
                                   correctness defect; ENGINE_PERFORMANCE_LIMIT
                                   at 1024 (max latency 31.9 s > client 30 s)
GEN21_D16C_QUALIFIED         NO    blocked on ED-001; ED-002/ED-003 need a
                                   fix or a by-construction workaround
```

## 1. What was done, in order

| step | content | result file | outcome |
|---|---|---|---|
| 1 | adjudicator | `results/step1_adjudicator.json` | 40 worlds; invariant unique 40/40; brute-force match 40/40; 9,600 partial-knowledge soundness checks, 0 unsound |
| 2 | census | `results/step2_4_census.json` | max marginal-guess rate 0.02; **BC killed** (empty answer 88.5%) |
| 3 | multi-component necessity | same | proper-subset determinacy 0.0 on all 27 (task, subset) pairs x 100 worlds |
| 4 | UNION vs COMPOSITION (offline) | same | 200/200 interactive cells: LOSO-necessary set == design set; UNION never suffices |
| 5 | origin laundering | `results/step5_laundering.json`, `repro/` | **LAUNDERED 6/6** -> ED-001 CRITICAL -> steps 10-11 HELD |
| 6 | duplicate evidence + consensus decoy | `results/step6_duplicate_evidence.json` | C5 out-of-band copy state-identical to true replication -> ED-002; decoy: one falsifier beats 7:1 (60/60) |
| 7 | F10 fork/frontier | `results/step7_f10_frontier.json` | 13/15 PASS; native re-creation rewrites basis + first_available_seq -> ED-003 |
| 8 | LOSO on-engine | `results/step8_loso_engine.json` | 4 worlds x 3 lineages; budget exact 12/12; NECESSARY == design 20/20; shuffled-source control WRONG 8/8 on B-dependent tasks |
| 9 | concurrency envelope | `results/step9_concurrency_C*.json` | C1 1-16 PASS; C2 32-1024 PASS on every invariant; perf limit at 1024 |
| 10 | pilot | -- | **HELD** (BLOCKED_BY_ED-001) |
| 11 | freeze thresholds/N | -- | **HELD** (BLOCKED_BY_ED-001) |
| 12 | report | this file + 3 qualification JSONs + 2 defect ledgers | delivered |

## 2. Engine defects (`D16C_ENGINE_DEFECTS.jsonl`)

**ED-001 `GEN21_ORIGIN_LAUNDERING` -- CRITICAL -- BLOCKING.**
Three clients A, B, C, FULLY_SHARED, one registered topology group.
A creates X natively; B imports X (legal); B reads the bytes; B
re-creates the content as NATIVE; C imports from B. Succeeds in 6/6
variations: byte-identical with same meta / meta changed / info_kind
changed / no meta / kind field changed / semantically-equivalent
byte-different. C's provenance says `origin=IMPORTED source_world=B`;
A appears on no surface C can see. Control: C importing B's IMPORTED
row directly is denied 403 (H6 holds) -- the rule is sound, the
re-creation path bypasses it. Mechanism (read from `sfe/runtime.py`):
`create_artifact` inserts `origin='NATIVE'` unconditionally and never
consults prior IMPORTED rows with the same `blob_hash`. Forensic
handle: for byte-identical laundering B's own F10 shows one IMPORTED and
five NATIVE rows with the same content_hash (visible only to B's owner
or a DB auditor); for the byte-different variant there is no
engine-visible trace at all. Reproducer:
`repro/GEN21_ORIGIN_LAUNDERING_repro.py` (standalone, < 1 s). Not solved
in client code. Not reinterpreted as independent rediscovery: the engine
has no principled way to tell rediscovery from copy.

**ED-002 `SUBSTRATE_GAP: EVIDENCE_INDEPENDENCE_NOT_REPRESENTABLE` -- MAJOR.**
Five constructions plant two apparently separate, identical evidence
artifacts. From the raw tables an auditor separates C1 client-fanout
(`SAME_CLIENT`), C2 fork-echo (`ANCESTOR_HELD_BEFORE_FORK`), C3
import-republish (`PRIOR_HOLDING_IN_SAME_WORLD`) from C4 true
independent replication. C5 -- B imports and reads O, a second identity
B' emits O natively -- is state-identical to C4. Through the API none
are separable: `get_world`/`knowledge`/`events` are owner-only (403),
there is no auditor role, F1 reads are not ledgered. Consequence: any
D16-C cell whose inference requires independence of apparently separate
evidence is VOID unless independence is established by construction
outside the engine.

**ED-003 `F10_PROVENANCE_REWRITE_ON_NATIVE_RECREATION` -- MAJOR.**
Child K1 inherits h1 at fork (`INHERITED / fork_inheritance /
first_available_seq=202`). After K1 creates h1 natively (seq 212),
F10(K1, now) lists h1 only as `NATIVE / native_creation / 212`; the
inherited entry vanishes (`_reconstruct_frontier` dedups by
content_hash and the native row masks inheritance). F10(K1, seq=202)
still shows inheritance. The availability SET is correct; the answer to
"when could K1 first know h1" depends on which cutoff you ask. The
IMPORTED-then-native case lists both rows (2 entries), so the two paths
are not even consistent with each other. Workaround if not fixed: every
AVAILABLE read must be taken at the fork/import cutoff seq, never at
head.

## 3. Science defects (`D16C_SCIENCE_DEFECTS.jsonl`)

**SD-001** task BC was an accidental universal strategy: empty answer in
88.5% of worlds (a random invertible P2 fixes no repair effect); B alone
determines it in 80/100. Removed before any ecology run. Remaining
interactive tasks AB, AC, ABC0-2: proper-subset determinacy 0/100,
LOSO matches design 200/200.

**SD-002** the packet's VERIFY_ONE synthesizer was not decisive: one
random query rejects a wrong A/C value with p = 1/2 only (23/60 at 3:1,
33/60 at 7:1). Replaced by VERIFY_K (k = 3 alternating free ops, power
1 - 2^-k; measured 52/60 = 0.87 vs predicted 0.875), which also
re-executes any contradicting failure record before trusting it. Pilot
policy set frozen at {RAW, FALSIFIER_FIRST, VERIFY_K}.

## 4. Superadditivity ladder status (Amendment 1)

Offline (step 4) and on-engine (step 8) every interactive cell that
FULL solves is TRUE_COMPOSITION: removing any designed source flips the
verdict, removing a non-designed source does not. UNION_ONLY: 0.
NOT_COMPOSITION: 0. The 40 offline "ancestor-of-answer" cases were
correctly refused the composition label. SHUFFLED_SOURCE_CONTROL on the
engine: replacing B with a B lineage from a different LT world makes
AB and ABC0-2 WRONG 4/4 each and leaves AC CORRECT 4/4. The failure
shape matters more than the verdict: RAW merge treats foreign
observations as facts, so a wrong source **silently poisons** rather
than being detected -- the endpoint is source-sensitive (which a
composition claim needs) but not source-checking. Of the Amendment-1
control set only LOSO_A/B/C, SHUFFLED_SOURCE_CONTROL and (offline) the
ancestor case have been run. SERIAL_MONOCULTURE, SERIAL_RESTART,
PARALLEL_ISOLATED and UNION_AVAILABLE are NOT yet implemented; they are
pilot-stage controls and belong to the held step 10. No PRIMARY
interactive result exists yet, so none is missing its controls.

## 5. Attribution vocabulary in practice (Amendment 3)

AVAILABLE = engine-certified F10 list of the synthesis world.
CONSUMED = client read log via F1 (CLIENT_ASSERTED; the engine does not
ledger reads). NECESSARY = fresh LOSO synthesis worlds. On-engine, all
three imported sources were AVAILABLE and CONSUMED in every FULL cell;
NECESSARY equalled the design set 20/20. No statement of the form
"artifact X caused result Y" appears anywhere in this packet; the
strongest available claim is "X was NECESSARY under LOSO". Because ED-003
rewrites basis/first_available_seq at head, the AVAILABLE reads used for
step 8 are the head reads of synthesis worlds that never re-created
content natively (so they are unaffected), but the general rule for any
future cell is: read F10 at the cutoff seq.

## 6. Concurrency (Amendment 4)

Per worker: register, create+start world (enforceable experiments
budget B = 8), concurrent idempotent duplicate + conflict, 3 LT steps,
checkpoint + fork under load, over-budget finish, artifacts, resources,
F10 twice, child-vs-parent F10, imports. Audited from the DB
afterwards: write exactness, budget exactness, index contiguity, seq
monotonicity, global seq uniqueness, independent hash-chain
recomputation, `verify_world`, F10 determinism, idempotency semantics,
fork boundary.

```
 L    ev/s   p50 ms   p95 ms    max ms   invariants
   1   117      48       51        62    PASS
   2   263      24       51        92    PASS
   4   328      54       95       124    PASS
   8   277      81      278       448    PASS
  16   309      82      671     2,422    PASS   <- C1 envelope edge
  32   328     128    1,814     3,388    PASS
  64   461     243    5,048     8,707    PASS
 128   562     880    3,781    13,203    PASS
 256   621   2,011    4,016    21,554    PASS
 512   609   4,579    6,960    22,290    PASS
1024   586   9,926   13,185    31,874    PASS   <- ENGINE_PERFORMANCE_LIMIT
```

No level produced a wrong ledger, wrong budget, wrong F10 or wrong fork
frontier: **no `ENGINE_CORRECTNESS_DEFECT`**. Throughput saturates at
~600 events/s from L = 128; p50 latency then grows linearly in L
(queueing on the single serialised writer). At 1024 the max request
latency (31.9 s) exceeds sfclient's default 30 s timeout
(`sfclient/client.py:40`): a stock client starts timing out while the
engine stays correct -> `ENGINE_PERFORMANCE_LIMIT`, invariants intact.
Ecology, when unblocked, runs at <= 16 concurrent lineages on a pinned
instance.

Instrument caveats: the first L = 256 attempt died with WinError 10048
(16,310 sockets in TIME_WAIT) -- ephemeral-port exhaustion on the client
host because sfclient opens one TCP connection per request; that is an
instrument fault and is recorded as such, not as engine behaviour. The
rerun used `engine_lineage.KeepAliveClient`. Client threads and engine
shared one host, so latency at 512/1024 includes client-side GIL
contention; the 1024 limit is an upper bound on engine-side queueing.
Live-instance corroboration (Amendment 4) was not run: no Daedalus
window. No `LIVE_ANOMALY_UNREPLICATED` rows exist because nothing was
run live.

## 7. The ten questions

1. Interactive targets non-decomposable into a trivial union baseline?
   **YES.** Proper-subset determinacy 0/100 on every pair; UNION never
   solves an interactive task (200/200 offline).
2. Multi-source necessity demonstrated by LOSO? **YES.** 200/200 offline,
   20/20 on-engine; SHUFFLED_SOURCE flips B-dependent tasks to WRONG.
3. Can imported knowledge be laundered into a new native export?
   **YES -- 6/6, including byte-different semantic equivalents.**
   CRITICAL. Blocking.
4. Can the engine distinguish independent replication from duplicated
   evidence? **NO.** C5 is state-identical to C4; via the API nothing is
   separable.
5. Is KnowledgeSet exact at every merge/fork frontier? **The SET, yes**
   (checkpoint boundary, transitivity, cutoff fail-closed, monotone,
   deterministic, import-then-fork). **Provenance, no**: basis and
   first_available_seq are rewritten by native re-creation (ED-003).
6. What concurrency level preserves every invariant? **Every level
   tested, 1 through 1024**, on the private instance. Qualified envelope
   16 (latency); performance limit 1024 (client timeout).
7. Does import cost qualitatively alter the verdict? **NOT TESTABLE** --
   the c_I in {0, 1, HIGH} sensitivity belongs to the held pilot.
8. Accidental universal strategy in the benchmark? **One found and
   killed** (BC). After removal the best marginal guess is 2%.
9. Can majority-wrong populations be defeated by one decisive falsifier?
   **YES** under FALSIFIER_FIRST and VERIFY_K (60/60 at 3:1 and 7:1);
   **NO** under BLIND (0/60). A forged counter-falsifier makes reading-only
   policies abstain (24/60, never wrong); the executing policy re-runs it
   and is unaffected (60/60).
10. Is GEN-2.1 capable of a provenance-clean multi-lineage ecology?
    **NO, as is.** Availability, ledger, budget and concurrency are
    sound; origin is not. Information that crosses a lineage boundary
    can be re-exported as native with no trace, and apparently
    independent evidence cannot be shown independent.

## 8. Evidence class and self-dissent

All LT observations are CLIENT_ASSERTED: the hidden-world oracle runs
client-side, the engine ledgers the hypothesis/prediction/experiment/
observation/failure sequence and enforces the budget, but cannot verify
that an observation is true. That is the design of the packet, not a
finding, and it is why no engine-side result here is an "observation
was correct" result.

Things that would weaken this packet if true, checked:
- The laundering could be an artefact of the private instance. No: the
  source hash matches the live engine and the mechanism is in
  `sfe/runtime.py`, not in configuration.
- Step 8's 20/20 could be the adjudicator agreeing with itself. The
  adjudicator was validated against brute force 40/40 with 9,600
  partial-soundness checks at step 1, before any engine run.
- The concurrency PASS could be the instrument not looking. Every
  invariant is defined in `D16C_CONCURRENCY_QUALIFICATION.json` with the
  predicate, the direction and the populations examined; the chain is
  recomputed from raw rows, not trusted from `verify_world` alone. What
  it does NOT cover: multi-host clients, the live instance, and any
  invariant not in the list (e.g. cross-world import ordering under
  concurrent forks was only checked at the F10-set level).
- The 1024 "limit" is partly client-side. Recorded as an upper bound.

## 9. What Daedalus needs

`repro/GEN21_ORIGIN_LAUNDERING_repro.py` and ED-001. A fix that closes
D16-C's need: `create_artifact` must either refuse, or mark (origin
`REPUBLISHED` with source), a NATIVE row whose blob_hash matches a prior
IMPORTED row in the same world -- and the design must rule on
byte-different semantic equivalents, which no hash can catch. ED-003 is
a read-side fix in `_reconstruct_frontier` (keep the earliest basis, do
not let a native row mask inheritance). ED-002 needs an auditor role or
ledgered reads; until then D16-C designs independence in by construction.

Phase 0 stops here. Nothing in D16-C, the multi-agent thesis, or GEN-2.1
was protected.
