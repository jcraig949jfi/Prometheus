# PEW export contract (V0). Brief §12; amendment A7.

**Direction.** One way. Proteus → Mnemosyne's Prometheus Evidence Wiki (PEW). Nothing in PEW is
ever read by a player, by the generator, by the grammar, or by the probes. The human-language
layer of PEW is quarantined from players by construction: no module under `proteus/foundry`
imports anything that could reach it, and the audit enforces the import allowlist.

**Status.** The Evidence Wiki client (`evidence_wiki/ew/client.py`) is on branch
`mnemosyne/evidence-wiki-v0` and not on `origin/main` as of 2026-09-02. This contract is written
against the documented API (the `evidence-wiki` skill) and produces the rows PEW will ingest;
it has not been exercised against the service. `export.pew_rows()` is the producer.

## 1. Rows

`export.pew_rows(organisms, lineage_records, signature_rows, degeneracy, packet_ref, git_commit)`
yields JSONL rows of four kinds, each carrying `provenance = {runtime_hash, grammar_hash,
affordance_hash, packet_ref, git_commit}`:

- `proteus.organism` — organism_id, lineage_id, generation, manifest hash, genome length, bounds,
  code_writable, persist. **Not the genome itself**: PEW holds interpretation over identities;
  the genome lives in the Proteus rows and in SFE.
- `proteus.descent` — record_id, organism_id, parent_ids, operator names, mutation seed.
- `proteus.signature` — organism_id, transcript_class, knockout_vector, resource vector.
- `proteus.transcript_class` — class_id, n_genomes, n_lineages, parent-child pairs within the
  class, knockout-vector distribution. **This is the A7 degeneracy map**, kept per class so that
  PEW can later distinguish "reached independently by unrelated lineages" from "repeated within
  one lineage" from immutable evidence.

## 2. How a Proteus result enters PEW (when the client is on main)

```
p = ew.register_packet("proteus/v0/REVIEW_PACKET_PROTEUS_V0_POSTBUILD_<date>.txt", "review_packet", git_commit=<sha>)
x = ew.register_experiment("Proteus", "v0", "Player Foundry V0 instrument qualification",
                           substrate="proteus.runtime.v0", packet_id=p["packet_id"])
```
then one `submit_claim` per claim in the packet, with `write_stage="SOURCE_BOUND"` and the
claim ceiling copied verbatim from the packet's claim-ceiling section, and one `submit_evidence`
per number, quoting the result file. Negative results (the failed neutrality run) go through
`register_failure`. Rows from §1 are attached as an artifact reference, not inlined.

## 3. What PEW may do that Proteus may not

PEW may associate, reinterpret, tag, cross-link and revise its reading of any of these rows.
Proteus may not: the rows are immutable once shipped, and a corrected reading is a new PEW
object pointing at the same identities.

## 4. Statuses

Every claim Proteus submits is `SUBMITTED` and agent-attributed. Nothing Proteus writes becomes
established by transport. Proteus does not adjudicate its own organisms (brief §14), so the only
statuses it can honestly assert are about the instrument: `SUPPORTED` for "the runtime replays
bit-exactly" and the like; never anything about what an organism is or can do.

## 5. Machine-native ancestral evidence

Brief §12: "any future machine-native ancestral evidence interface requires a separate
semantically sterile protocol and explicit qualification." Not designed, not started. If one is
ever proposed it is a new contract with its own quarantine audit, and it would deliver
integers on channels through the ABI like any other world input, never through a privileged path.
