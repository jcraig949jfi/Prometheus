# Evidence Wiki / Mnemosyne Evidence Tensor — V0 Architecture

Status: V0 build, 2026-09-01. Owner: Mnemosyne.
Charter: `roles/Mnemosyne/prompts/CHARTER_EVIDENCE_WIKI_V0_2026-09-01.txt`
(sha256 c81a21278fd084b4e40a2ef4403f422043599cc5fe000c631dacbaa758ba0ead).

## 1. One substrate, many projections

Canonical epistemic state lives in ONE place: Postgres schema **`ew`** inside
`prometheus_fire` (the existing durable spine — deliberately NOT a new stack).
Everything else — wiki pages, REST responses, BM25/embedding/graph indexes,
sparse coordinates compiled to TensorLy, CP/Tucker/TT factors — is a DERIVED
representation carrying `snapshot_id` + versions + a reproducibility hash, and
is deletable/rebuildable (gate G17).

```
L0  fossils: files in git + hashes            (never copied, only referenced)
L1  ew.* canonical store                      (claims/evidence/relations/provenance)
L2  relational/graph view                     (SQL traversals over ew.relations)
L3  ew.coordinates                            (sparse, versioned, deterministic)
L4  evidence_wiki/derived/*                   (CP/Tucker/TT, embeddings, BM25)
L5  FastAPI REST  /api/v1/*                   (the only write path for agents)
L6  Wiki UI (server-rendered from L1)         (same objects as the API)
```

Rejected alternative: reusing the `sigma` schema (sigma_kernel). Sigma is the
operator-symbol promotion kernel (symbols/capabilities, linear-token
discipline); its claims are kernel claims, not program-level empirical
findings. Different lifecycle, different adjudication. Both live in
prometheus_fire; they stay separate.

## 2. Epistemic hard rules (enforced in code, not convention)

1. **Append-only.** No UPDATE/DELETE on claims/evidence/relations through the
   service. Corrections are new claim versions plus `CORRECTS`/`SUPERSEDES`
   relations (charter A13). Historical status is never rewritten.
2. **No provenance, no write.** Evidence requires `packet_id` + verbatim
   `source_quote`. Claims require a packet or an experiment. Writes without
   them are rejected (gate G15).
3. **Epistemic class is explicit everywhere.** Relations carry
   `epistemic_class ∈ {OBSERVED, INFERRED, HYPOTHESIZED}` and
   `creation_method ∈ {HUMAN, EXPERIMENT, MODEL_EXTRACTED, TENSOR_INFERRED}`.
   The API and UI always surface both (gate G2/G22).
4. **Derived is quarantined.** `ew.source_packets.kind='derived_view'` is
   refused as evidence provenance — a wiki page or tensor output can never be
   registered as a source packet backing new evidence (gate G8/25). The
   ingestion path checks the URI against `evidence_wiki/derived/` and the
   wiki route namespace and rejects.
5. **Agent submissions enter staged.** `write_stage: SUBMITTED → VALIDATED →
   CANONICALIZED → SOURCE_BOUND → INDEXED`. Nothing an agent POSTs becomes
   ESTABLISHED by transport; status is whatever the SOURCE adjudicated, and
   the service validates the packet reference before promotion past
   VALIDATED (charter A7).
6. **Hypotheses cannot promote themselves.** `ew.hypotheses.status` is
   'HYPOTHESIZED' forever; promotion happens only by NEW evidence rows that
   reference a real packet — the hypothesis row is then linked, not mutated.

## 3. Identity and idempotency (charter A8)

All canonical IDs are **content-addressed**: `<prefix>-<sha256[:12]>` over a
canonical JSON serialization of the identity fields (e.g. claim: canonical
text + packet + span; evidence: packet + span + quote). Consequences:

- the same submission from two machines yields the same ID;
- retries collapse via `INSERT ... ON CONFLICT DO NOTHING`;
- `ew.write_log.idempotency_key` (unique) short-circuits replayed POSTs;
- duplicate scientific records are structurally impossible, not policed.

Every accepted write takes `nextval(ew.canonical_revision_seq)`; the max is
the **canonical_revision** that derived views report their freshness against
(gate G18).

## 4. Tensor views v1 — and why these modes

Charter §5 lists 10-mode candidate views. At V0 scale (~60-100 findings) most
candidate modes (claim, experiment, time) are **unique per observation**;
using them as tensor modes yields a permutation matrix — pure diagonal, no
shared structure, nothing for a decomposition to compress. Modes earn their
place only when their vocabulary is SHARED across observations. V1 therefore:

- `evidence_v1` — modes `[agent, substrate_class, mechanism, evidence_type,
  outcome]`; value 1 per evidence row; claim/experiment/time ride as metadata
  reachable through the coordinate's `evidence_id`.
- `failure_v1` — modes `[failure_class, mechanism, substrate_class, outcome]`
  over negative evidence only.
- `relation_v1` — modes `[src_claim, relation_type, dst_claim]` (the graph as
  a 3-tensor; used for link-prediction baselines and the missing-cell test).

Mode dictionaries come from `ew.dim_terms` (versioned); free-text source
vocabulary maps in via `ew.term_mappings` with `creation_method` recorded —
Mnemosyne's own mappings are `MODEL_EXTRACTED` and reviewable, per charter
§23. Source wording is never discarded (`claims.source_wording`,
`evidence.source_quote`).

Time is deliberately NOT a v1 mode: at this scale each month is nearly
unique per observation. Revisit at V1 with binning once density justifies it.

## 5. Tensor compiler (charter A5)

`ew/compiler.py`: `compile(view, filters) → snapshot` (immutable row in
`ew.snapshots` + coordinate file with content sha256) → `factor(snapshot,
method∈{cp,tucker,tt}, rank)` / `contract(snapshot, marginalize, retain)`.
Factorizations only ever read snapshot files, never live tables. Derived
artifacts persist under `evidence_wiki/derived/` with full parameterization
and reproducibility hashes.

## 6. Search is multi-paradigm (charter §8, §17)

`ew/search.py` implements: (A) BM25 lexical; (B) embedding retrieval
(sentence-transformers all-MiniLM-L6-v2, local GPU); (C) graph traversal over
`ew.relations`; (D) tensor-factor retrieval (cosine in factor space from the
compiled decompositions); (E) hybrid (rank fusion). Benchmarks compare all
five; the tensor must EARN G6 or the packet reports TENSOR_NOT_YET_JUSTIFIED.

## 7. Network service (addendum A1/A9)

FastAPI on a configured bind/port (`evidence_wiki/config.json`, default
0.0.0.0:8377). Auth V0: single shared bearer token + mandatory
`X-Prometheus-Machine` / `X-Prometheus-Agent` headers recorded on every
write; the DB is NOT exposed — only the service port. LIMITATION (documented
per A9): no TLS and a shared token on a trusted LAN; per-machine tokens and
TLS are the V1 upgrade path. Firewall rule: `scripts/open_firewall.ps1`
(requires admin; if not yet run, the service is localhost-only and gate G11
is reported honestly as pending).

## 8. Live update model (A17)

Canonical writes commit transactionally and bump the revision. Cheap indexes
(BM25, embeddings, graph) rebuild on demand/lazily; decompositions rebuild on
explicit compile. Every search/tensor response carries
`canonical_revision` + the artifact's revision so staleness is visible.

## 9. What V0 does NOT do (scope fences)

No autonomous scheduler; no bulk corpus ingestion; no LLM adjudication of
contradictions; no promotion of tensor predictions; no per-agent authz model
beyond attribution; no TLS. All recorded as V1 candidates in the packet.
