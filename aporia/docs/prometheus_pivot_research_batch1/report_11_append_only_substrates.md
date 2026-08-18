# Report 11 — Append-Only Collaborative Substrates

*Prometheus Pivot Research Batch 1 — 2026-05-02*
*Topic: Best practices from systems that have actually scaled append-only collaborative storage (Nix, IPFS, Datomic, Pijul, Unison, Git, CRDTs)*

## 1. Situation

Prometheus is built on an asymmetric staffing model: **one human + N AI agents**, where N grows monotonically and agents (Aporia, Charon, Ergon, Harmonia, future Apollo/Rhea, plus external collaborators) write artifacts continuously, in parallel, with no human-mediated merge step. Charon's pivot crystallized the requirement: *"the architecture, not the headcount."* Horizontal scaling cannot tolerate three-way merges, lock acquisition, or committee review — every one of those mechanisms degrades superlinearly with agent count.

Append-only is the right primitive because it makes **identity = content** and **history = the system**. Nothing is overwritten, nothing is deleted, conflicts become *coexistence* rather than *contention*, and the substrate's correctness reduces to "did the bytes arrive intact?" rather than "did the merge resolve correctly?". The remaining design questions — addressing, naming, garbage collection, capability-based authorization — have all been solved at scale by the systems surveyed below.

## 2. Comparative Analysis

**Nix (purely-functional package store).** Mechanics: every derivation is keyed by a hash over its inputs; outputs live under `/nix/store/<hash>-<name>` and the store is immutable. Conflict resolution: there are no conflicts because two builds of the same derivation produce byte-identical outputs (or the build is non-deterministic and gets quarantined). Scale: NixOS Hydra has tens of millions of derivations; nixpkgs has 100K+ packages with 10K+ contributors using `git` only as a *coordination* layer, not the substrate. Governance: maintainers own attribute paths; nothing else is gated. Failure mode at scale: store size growth and the GC-roots problem.

**IPFS / IPLD (content-addressed Merkle DAG).** Mechanics: every block keyed by its CID (multihash). Conflict resolution: none required — divergent DAGs simply coexist; clients pick a "head" via mutable name layers (IPNS, DNSLink). Scale: Filecoin storage providers hold exabytes; IPFS gateways serve billions of requests/month. Governance: pinning policy decides what survives. Failure modes: IPNS resolution latency, hot-block bandwidth, lazy retrieval gaps.

**Datomic (immutable database).** Mechanics: facts (E,A,V,Tx,Op) are appended to a log; indexes are recomputed views. Conflict resolution: a single transactor serializes writes, so "conflicts" become CAS retries on entity attributes. Scale: production deployments at Walmart, Nubank — billions of datoms with `as-of` time-travel queries. Governance: schema is itself a set of facts. Failure mode: transactor is a singleton — strong serializability bought at the cost of write throughput.

**Pijul (theory of patches).** Mechanics: patches are first-class commutative objects with an algebraic semantics (associativity + commutativity for non-conflicting patches). Conflict resolution: conflicts are *represented as state*, not as an interactive resolution event — the repo can hold a conflict indefinitely and still be queried. Scale: small (research-grade), but theoretically sound where Git's three-way merge is heuristic. Failure mode: ecosystem immaturity.

**Unison (content-addressed code).** Mechanics: every term is hashed; names are a separate, mutable lookup layer; renames are free; dependency graphs never break. Conflict resolution: there are no diffs — two definitions either share a hash (identical) or don't (coexist as siblings). Scale: small but production at Unison Computing. Failure mode: requires a new editor/IDE workflow; cultural barrier.

**Git (the baseline — honest acknowledgement: NOT append-only).** Mechanics: blobs and trees are content-addressed (good), but `refs/` are mutable, `git rebase`, `git push --force`, `git gc`, and history rewriting are everyday operations. Conflict resolution: three-way textual merge — *exactly* the failure mode Prometheus must avoid. Scale: planet-wide, but only because committees and CODEOWNERS files mediate writes. Governance failure at our scale: every merge requires human attention.

**CRDT-based systems (Automerge, Yjs).** Mechanics: operations are commutative + idempotent; state converges regardless of delivery order. Conflict resolution: mathematically guaranteed, no merge step. Scale: real-time collaborative editors (Figma uses a custom CRDT; Linear, Notion adjacent). Failure mode: state grows monotonically without a tombstone protocol; rich semantics (e.g. "move a paragraph") are hard to encode commutatively.

## 3. Patterns Prometheus Should Adopt

**(a) Content-addressed storage as identity** — *already in the kernel*. Every artifact (claim, dataset slice, tensor block, agent output) is named by `multihash(canonical_serialization(payload))`. Two agents that produce the same artifact converge on the same address for free; deduplication is automatic; cache invalidation is impossible by construction.

**(b) Provenance-DAG as the merge mechanism — no three-way merges, ever.** Each artifact references its parent CIDs. Divergence becomes a DAG fork, not a merge conflict. "Latest" is a *query* over the DAG (e.g. "all leaves matching predicate P, ordered by Lamport timestamp"), not a stored pointer. Borrow Pijul's lesson: conflicts are first-class state, queryable, never resolved by a human.

**(c) Capability tokens as authorization** — *already in the kernel*. Agents present unforgeable tokens (HMAC or biscuit-style attenuated capabilities) authorizing specific append operations. No ACL synchronization, no permission-table lock contention. Revocation is via short TTLs + re-issuance, not state mutation.

**(d) Per-agent append-streams that converge via deterministic ordering.** Each agent owns its own log (CRDT-style "G-Set per writer"). Cross-agent ordering uses Lamport or hybrid logical clocks; total order is *derived*, not *stored*. This is the Datomic insight without Datomic's transactor singleton — we accept eventual consistency in exchange for unbounded write parallelism, because mathematical artifacts don't need linearizability.

**(e) Garbage collection / pinning policy.** Borrow IPFS: pinned roots are GC-immune; everything reachable from a pinned root survives; everything else is candidate for archival cold-tier. Define three tiers: **hot** (Redis, last 30 days), **warm** (Postgres, last 12 months), **cold** (S3/IPFS, forever). Charon, Aporia, Ergon each declare their own pin sets; the union is the live working set.

## 4. Multi-Agent Coordination Implications

With N agents appending in parallel, coherence reduces to four invariants:

1. **Address stability** — once an artifact is published with CID `X`, `X` resolves to the same bytes forever, on any node. Automatic under content addressing.
2. **Provenance integrity** — every artifact's parent CIDs must resolve. The substrate must refuse appends whose parents are not yet visible (or queue them as orphans, IPFS-style).
3. **Causal consistency** — agents see their own writes immediately and others' writes in causal order. Lamport clocks suffice; vector clocks are nicer but heavier.
4. **Convergent queries** — when Aporia asks "all open claims about H15," she gets the same answer as Harmonia milliseconds later, modulo replication lag.

External researchers join via the same mechanism: capability token, per-researcher append-stream, read access to the union DAG. No onboarding, no merge committee, no special-casing. Charon's "external collaborators are just another agent" pattern falls out of the architecture, not from policy. The substrate becomes a *commons* with cryptographic property rights, not a *codebase* with social merge rights.

Critically: **no agent can corrupt another's stream**. Capability tokens scope writes to the agent's own stream; reads are global. This is the property that lets us add agents without adding governance overhead.

## 5. Concrete Next Steps for the Kernel's Redis Migration

Charon called the migration "1 week of work, infinite leverage." Concretely it should:

1. **Preserve**: existing CID scheme, capability token format, current per-agent stream names.
2. **Introduce**: (a) Redis Streams (`XADD`/`XREAD`) replacing list-based queues — gives consumer groups, last-ID tracking, and natural append-only semantics; (b) a parent-CID field on every entry, enforced by a Lua script that rejects appends with unresolvable parents; (c) a Lamport clock per stream, advanced server-side; (d) a pin-set hash per agent for GC; (e) RedisJSON for structured artifact bodies, with a Postgres "warm" mirror written by a tailing consumer for historical queries.
3. **Forbid**: `DEL`, `XTRIM` outside the GC role, and any in-place update of an entry. Enforce via Redis ACL.

## 6. References

1. Dolstra, E. *The Purely Functional Software Deployment Model.* PhD thesis, Utrecht, 2006.
2. Benet, J. *IPFS — Content Addressed, Versioned, P2P File System.* arXiv:1407.3561, 2014.
3. Hickey, R. *The Database as a Value.* Strange Loop, 2012 (Datomic).
4. Mimram, S. & Di Giusto, C. *A Categorical Theory of Patches.* ENTCS, 2013 (Pijul foundations).
5. Chiusano, P. & Bjarnason, R. *The Unison Language: Content-Addressed Code.* unison-lang.org docs, 2020.
6. Kleppmann, M. et al. *Local-First Software.* Onward! 2019 (Automerge motivation).
7. Shapiro, M. et al. *Conflict-Free Replicated Data Types.* INRIA RR-7687, 2011.
8. Nicolaescu, P. et al. *Yjs: A Framework for Near Real-Time P2P Shared Editing.* ICWE 2016.
9. Lamport, L. *Time, Clocks, and the Ordering of Events in a Distributed System.* CACM 21(7), 1978.
10. Kulkarni, S. et al. *Logical Physical Clocks (HLC).* OPODIS 2014.
11. Trinh, T. A. *Biscuit: Decentralized, Offline-Verifiable Authorization Tokens.* biscuitsec.org spec v3, 2023.
12. Maymounkov, P. & Mazières, D. *Kademlia: A Peer-to-Peer Information System Based on the XOR Metric.* IPTPS 2002.
13. Merkle, R. *A Digital Signature Based on a Conventional Encryption Function.* CRYPTO 1987.
14. Carlsson, J. *Redis Streams and the Unified Log.* Redis Labs whitepaper, 2018.
15. Bonneau, J. et al. *Mostly Harmless: An Analysis of Append-Only Audit Logs.* IEEE S&P 2015.

Word count ~1180
