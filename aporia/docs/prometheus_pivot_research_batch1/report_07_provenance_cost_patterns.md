# Provenance + Cost Annotation Patterns for the Σ-Kernel

**Research brief — Topic #7, Batch 1**
**Date:** 2026-05-02

---

## 1. Situation

Prometheus's Σ-kernel already does the hard half: every symbol definition is a content-addressed `def_blob` (SHA256), and TRACE walks the dependency DAG to recover the full lineage of any claim. This is structurally equivalent to a Nix store path or an IPLD CID — the substrate is *referentially transparent at the storage layer*.

What is missing is the **cost half** and the **purity contract**:

- No `op_application` record carries wall-time, memory, or oracle-call cost.
- No declared purity invariant — we trust that recomputing a symbol from its def_blob yields the same hash, but nothing enforces it (no sandboxing, no input pinning of nondeterministic seeds).
- No temporal index on substrate state — TRACE walks lineage but cannot answer "what did the kernel believe at t=T?"
- Cost estimates, when they exist (Techne's queue), are bare numbers without provenance — we cannot tell whether 4.2s came from a measurement, a model, or a guess.

Techne's pivot to cost-annotated callables forces these gaps to close.

## 2. Comparative analysis of existing systems

**Bazel** encodes provenance as an *action graph*: each action is `(inputs, command, outputs)` keyed by a content hash of the tuple. The remote cache (CAS, content-addressed store) lets any worker skip an action if its key is hit. Cost is tracked per-action via `--profile` (JSON event traces of CPU/wall/memory) and per-target via build-event protocol. Failure modes: action key drift from non-hermetic toolchains (timestamp leaks, `$PWD` leaks), cache poisoning when one worker has a corrupt environment, and cost-blindness across the cache boundary (cached actions show "0 cost" in the trace, hiding original expense).

**Nix** elevates purity to an *invariant*: derivations are pure functions of their inputs, sandboxed at build time. Content-addressed derivations (CA-derivations, ~2021+) hash on output content rather than input recipe, enabling early cutoff. Cost is *not* first-class — `nix log` gives wall time, but no structured profile. Failure modes: impurity smuggled via `__noChroot`, fixed-output derivations as a network escape hatch, and the famous "rebuild the world" cliff when a low-level dep changes.

**IPFS/IPLD** is pure provenance, no cost: every block is a CID (multihash), DAGs are immutable Merkle structures. Cost annotation is entirely out-of-band (pinning services track storage cost). Failure modes: the *garbage collection problem* — without external pin metadata, you cannot tell which CIDs are live; and *graph traversal cost* is unbounded without a budget primitive.

**Datomic** indexes facts as `[entity, attribute, value, tx, op]` 5-tuples. Every fact has a transaction ID, giving free time-travel: `as-of`, `since`, `history`. Provenance is the `tx` reference; cost (query time, datom count) is exposed via the `db.query/stats` API. Failure modes: unbounded history growth, expensive `history` queries on hot attributes, and the fact that *retraction is also a fact* — you cannot truly delete, only assert non-belief.

**Unison** content-addresses *code itself* — every function is named by the hash of its normalized AST. Renames are free; the dependency graph never breaks. No native cost model, but the hash-naming makes memoization trivial. Failure mode: the *codebase manager* becomes a critical-path dependency, and AST normalization edge cases (effect rows, ability handlers) can cause hash drift between releases.

**Pijul** uses a theory-of-patches: changes commute when independent, giving an actual algebra of edits rather than Git's ad-hoc 3-way merge. Provenance is the patch DAG; cost is not modeled. Failure mode: patch-explosion in long-lived branches and the conceptual learning cliff vs. Git.

## 3. Patterns Prometheus should adopt

**(a) Bazel-style action graph for compositions.** Every Techne callable invocation should be reified as an `op_application` with a content-addressed key over `(symbol_hash, arg_hashes, env_hash)`. This gives us a remote-cache-equivalent: if the same callable is invoked with the same arg hashes anywhere in the org (M1, M2, future Forge workers), the result is reused. Critically, *cache hits must still record cost* — store the original measured cost on the cache entry, and emit a `cache_hit` event with `original_cost` so profiling stays honest.

**(b) Nix-style purity invariant for op_applications.** Declare each callable as `pure | impure(reasons)`. Pure callables run in a sandbox (no network, pinned RNG, frozen wallclock); impure ones (oracle calls, LMFDB queries) must declare their impurity sources as explicit inputs to the hash — e.g. an LMFDB query hashes in the database snapshot ID. This converts impurity from a silent footgun into a typed annotation.

**(c) Datomic-style temporal indexing.** Add a transaction log to the kernel: every assertion/retraction of a Claim gets a `tx_id` and `tx_time`. Implement `kernel.as_of(t)` for time-travel queries — essential for "did this discovery survive battery v8 even though it fails v9?" forensics, and for the `feedback_assume_wrong` workflow (kills are the most valuable output, but only if you can reconstruct the pre-kill state).

**(d) Cost-of-cost provenance.** Every cost annotation must itself carry `(value, unit, source, confidence)` where `source ∈ {measured, modeled, declared, inherited}`. A 4.2s cost from a single timing run is different from a 4.2s cost from 100 runs (σ=0.1) is different from a 4.2s cost copied from an analogous callable. Without this, planners will treat guesses as ground truth — exactly the `feedback_calibration` failure mode.

## 4. Concrete schema proposal for kernel extension

Add to `Symbol`:
```
purity:        Enum[pure, impure]
impurity_sources: List[Source]   # e.g. ["lmfdb_snapshot:2026-04-15", "rng:numpy"]
cost_model:    Optional[CostModel]
```

Add to `op_application`:
```
op_id:         SHA256(symbol_hash || arg_hashes || env_hash)
inputs:        List[Hash]        # arg def_blobs
output:        Hash              # result def_blob
tx_id:         Int64             # monotonic
tx_time:       Timestamp
sandbox:       Optional[SandboxSpec]
cost:          CostRecord
cache_status:  Enum[fresh, hit, recomputed_for_validation]
```

Add new `CostRecord`:
```
wall_seconds:  Float
peak_rss_mb:   Float
oracle_calls:  Map[OracleName, Int]
source:        Enum[measured, modeled, declared, inherited]
confidence:    Optional[(n_samples, std_dev)]
estimator_id:  Optional[Hash]    # provenance of the model that produced the estimate
```

Add to `Claim`:
```
asserted_at:   tx_id
retracted_at:  Optional[tx_id]
cost_to_falsify: Optional[CostRecord]   # battery cost that could kill it
```

This makes `kernel.plan(goal, budget)` expressible: walk candidate op_applications, sum CostRecords, prefer cached or low-confidence-margin paths.

## 5. Anti-patterns

- **Action keys that aren't truly hermetic** (Bazel's perennial wound) — leaking `$HOSTNAME`, `$DATE`, or absolute paths into the hash. Sandbox or fail.
- **Treating impurity as binary** (Nix's fixed-output escape hatch) — instead, make impurity sources first-class typed inputs.
- **Unbounded history retention** (Datomic's "excision" came late) — design retention policies up front; cold-archive old tx logs.
- **Cost without confidence** — a single measurement labeled as "the cost" misleads planners; always carry n and σ.
- **Cache hits that hide cost** — every hit must report what it would have cost, or you cannot reason about the value of the cache itself.
- **Hash-naming without a normalization spec** (Unison's edge cases) — pin AST/blob normalization rules and version them.

## 6. References

1. Bazel team. *Remote Execution API Specification.* github.com/bazelbuild/remote-apis (v2.3, 2024).
2. Bazel team. *Build Event Protocol.* bazel.build/remote/bep (2023).
3. Dolstra, E. *The Purely Functional Software Deployment Model.* PhD thesis, Utrecht, 2006.
4. Courtès, L. & Wurmus, R. *Reproducible and User-Controlled Software Environments in HPC with Guix.* Euro-Par 2015.
5. Roosen-Runge, T. et al. *Content-Addressed Derivations in Nix.* NixCon 2021 talk + RFC 0062.
6. Benet, J. *IPFS — Content Addressed, Versioned, P2P File System.* arXiv:1407.3561, 2014.
7. Trautwein, D. et al. *Design and Evaluation of IPFS: A Storage Layer for the Decentralized Web.* SIGCOMM 2022.
8. Hickey, R. *The Database as a Value.* Datomic whitepaper / QCon NYC 2012.
9. Hickey, R. & Halloway, S. *Datomic: Database for Composite Systems.* Cognitect technical report, 2014.
10. Chiusano, P. & Bjarnason, R. *Unison: A Friendly Programming Language from the Future.* unison-lang.org docs (2020+).
11. Mimram, S. & Di Giusto, C. *A Categorical Theory of Patches.* ENTCS 298, 2013. (Theoretical basis for Pijul.)
12. Erdweg, S. et al. *A Sound and Optimal Incremental Build System with Dynamic Dependencies.* OOPSLA 2015. (Pluto / build-system semantics.)
13. Mokhov, A., Mitchell, N., Peyton Jones, S. *Build Systems à la Carte.* ICFP 2018. (The canonical taxonomy paper covering Bazel/Nix/Shake/Excel along the same axes used here.)
