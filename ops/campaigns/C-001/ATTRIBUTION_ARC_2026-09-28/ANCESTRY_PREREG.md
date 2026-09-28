# Byte-level ancestry replays (BEE, NPE) -- preregistration v1 (Archaeon, 2026-09-28)

Directive: roles/Archaeon/prompts/2026-09-28_attribution_arc/00_OPERATOR_DIRECTIVE_verbatim.md.
Baseline: attribution v0 as corrected (ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/).
This file is frozen at commit before any replay runs. Amendments are appended, dated, and never edit the text above them.

## 0. Division of labour
- **Owners (Bellerophon for BEE, Nestor for NPE):**
  * implement and run a NATIVE observation-only material-provenance replay in their own harness;
  * pass the calibration fixtures (s4) first;
  * export the fields in s3.
- **Archaeon:**
  * owns these questions, the fields, the fixtures, the identifiability rules and the final synthesis;
  * does not run the other engines' harnesses for production numbers.

## 1. What "ancestry" means here (and what it may never be inferred from)
- **Scope.** The ancestry of a child byte at locus p is the ORIGIN of the value in that byte, followed through every operation of
  the birth's execution.
- **Forbidden sources:**
  * resemblance / identity by state;
  * source address;
  * value match (the final byte equals someone's byte);
  * execution context (who ran the instruction);
  * code location.
  None of these may assign, or break a tie in, a material label.
- **Material labels.** Every memory byte AND every register carries a label. At the start of an execution:
  * writer / executing organism's tape locus i -> (ENTITY writer_id, i);
  * partner / occupant / window locus j -> (ENTITY occupant_id, j), or (EMPTY) if the cell was empty;
  * any other memory -> (OTHER region, address);
  * each input value read -> (INPUT);
  * an immediate operand used as a value -> the label of the operand BYTE, i.e. (ENTITY owner, locus of the operand).
    A painter that stores its own operand is IBD from that one locus.
- **Propagation:**
  * pure moves (load, store, register copy, block copy, exchange) carry the label unchanged;
  * any arithmetic / logic / combining operation produces (COMPUTED, {contributor labels});
  * a constant written by an instruction with no operand -> (CONSTANT, instruction label);
  * a byte never written during the birth keeps its start label (retention).
- **Mutation.** Copy noise or mutation applied by the world after the execution -> (MUTATION). If the world mutates a byte, its
  label is MUTATION regardless of value.
- **Multi-generation identity.** Across births, each living organism stores its per-locus labels (entity, locus) resolved to
  ORIGINAL material ids, the way Archaeon's core does: founder id * L + locus; new material gets fresh ids. That makes founder
  descent (Q5) answerable. If an owner can do only within-birth labels, Q5 is NOT IDENTIFIABLE and says so.

## 2. The questions (Q1-Q7) and when each is identifiable

For each birth, the child locus set is L loci. A locus is IDENTIFIED iff its label chain resolves without any "unknown" link. An
unknown link is any of: a read from an untracked region or register, a dropped label, or an operation the tracer does not model.
Per-birth identified share = identified loci / L.

| Q | question | identifiable for a birth iff | NOT identifiable when | what would ALTER v0 | what would BREAK v0 |
|---|---|---|---|---|---|
| Q1 | producer != material donor: does an entity other than the performer supply >= 10% of the child? | identified share >= 0.9 AND the performer set is known (executing code's owner, from the native trace) | identified share < 0.9 | producer and donor definitions need a third role (e.g. partner-executed own material is common) | the performer cannot be defined per birth in the engine (e.g. code of both parties interleaved at byte granularity), so CARRIER is not a per-event field there |
| Q2 | resemblance mistaken for descent: does the native label (BEE `material` writer/target; NPE anc/oid identity) name a different majority donor than IBD? | identified share >= 0.9 | < 0.9 | -- | IBD and the native label agree on > 99% (then the IBS/IBD separation adds nothing for this engine) |
| Q3 | singular-parent loss: second donor >= 10%, or new material >= 10%, or producer != donor | identified share >= 0.9 | < 0.9 | -- | loss < 1% in both engines AND in Archaeon (then parent_id is harmless everywhere measured) |
| Q4 | material without capability: majority-donor children that never demonstrate copying (in situ: later is_sr / P-11-causal as donor; isolated: engine's own isolated test if available) | Q1 identifiable AND a capability test recorded for the child | no capability test | capability needs the engine's scaffold to be defined (then the capability conditions field must be mandatory) | -- |
| Q5 | capacity without founder material: capable children whose founder-material share < 10% | multi-generation ids available | within-birth labels only | -- | -- |
| Q6 | co-execution: births where the executing code's MATERIAL (not location, not context) belongs to a non-donor | the owner can label executed instruction bytes with material labels (the same propagation, applied to code bytes) | executed-byte material unavailable | WHO/WHERE/WHAT needs a fourth referent | -- |
| Q7 | painting vs copying: source diversity (distinct (entity, source locus) per IBD locus) | identified share >= 0.9 | < 0.9 | a predicate must include source diversity | -- |

**Decision rules for the synthesis:**
- **VALIDATED:** every Q identifiable in >= 80% of births; the v0 schema holds the results without new fields; no break condition
  met.
- **ALTERED:** a new field or role is required, or an alter condition is met.
- **BROKEN:** any break condition is met, or ancestry cannot be made identifiable in the engine even with full labels. In that
  case v0's per-event record is the wrong unit for that engine, and plural substrate-specific records follow.

## 3. Fields each owner exports (one JSON per birth; attribution-v0 compatible)
- birth_id, native row / event id, run id, and the harness commit + module sha256;
- child tape (hex); writer / executing organism id and tape (pre-execution); partner / occupant id and tape (pre-execution), or
  EMPTY;
- per child locus: label = [kind, entity_or_null, source_locus_or_null, original_material_id_or_null, contributors_if_computed];
  kind is one of ENTITY | INPUT | CONSTANT | COMPUTED | MUTATION | EMPTY | OTHER | UNKNOWN;
- per executed instruction byte (for Q6): the material label of the code byte at execution time, aggregated per birth as counts
  by entity;
- performer(s): the execution context(s) in the engine's own terms;
- native fields verbatim (BEE: the 20-column row; NPE: P-11 C2/C4/C5, anc/oid, prov);
- capability evidence already native (BEE: whether the child later writes an is_sr birth; NPE: P-11 as donor), clearly marked
  in-situ;
- fixture results (s4) and the output sha256.

## 4. Calibration fixtures (must pass BEFORE the production replay; known answers)
Each owner builds these in their own ISA and memory model. The expected answers are stated here, not by the owner.

| id | construction | expected labels | catches |
|---|---|---|---|
| K1 | exact self-copy (writer copies its own tape into the window) | all L loci (writer, p) | baseline |
| K2 | scratch copy (Review 1 CX-5a): writer copies partner bytes into its own region, then copies that region into the window | the copied loci are (partner, source locus), NOT writer | address-as-material |
| K3 | partner-executed copy (CX-5b): the partner's code copies the writer's tape into the window | loci (writer, p); performer = partner | context-as-material |
| K4 | shifted copy by s | (writer, p - s) with the source locus recorded | position as identity |
| K5 | self-painter: store own operand to every window locus | every locus (writer, operand locus); source diversity 1/L | value/painting |
| K6 | computed byte: window[p] = mem[a] + mem[b] | (COMPUTED, {labels of a, b}), not IBD | arithmetic laundering |
| K7 | retention: the writer writes half the window | the unwritten half keeps (occupant, p) or EMPTY | retention |
| K8 | value coincidence: the writer writes a CONSTANT that happens to equal the occupant's byte | (CONSTANT), not occupant | value match |
| K9 | engine mutation after the birth (if the engine applies copy noise) | (MUTATION) at mutated loci | noise |

A replay that fails any applicable fixture does not proceed. An engine where a fixture is inapplicable says why.

## 5. Samples (bounded)
- **BEE:** ONE run, r016299 (PAIR_EXECUTION, 83,384 births).
  * Why this run: it is where v1's address reading failed; the partner's code executes in 12.5% of births; and the native
    `material` label disagrees with the address reading in 22.5%.
  * It has already been fully replayed portably (E-001 T-002, result sha256 recorded).
  * Alternative the owner may choose instead, with a stated reason: r038751 (the TH-006-attested run).
- **NPE:** the 34 T-003 births (11 runs of specimen 4931614d912c52b2), as replayed in E-001 T-003.
- **Compute:** leases per the canonical convention (comms LEASE ACQUIRE/RELEASE). Estimated from E-001 as 30-90 CPU-min for BEE and
  minutes for NPE.

## 6. Predictions (made before any data; each can lose)

| # | prediction | loses if |
|---|---|---|
| P1 | BEE r016299: identified share >= 0.9 in >= 95% of births | < 95% |
| P2 | BEE: among births where the partner's code executed (10,454), the IBD majority donor is the WRITER in >= 50% (partner code copying the writer: producer != donor is common) | < 50% |
| P3 | BEE: the address reading (row field 8 >= L/2) agrees with the IBD majority in >= 90% of births (the address reading is mostly right; Review 1's CX-5a is rare in practice) | < 90% |
| P4 | BEE: the native resemblance label disagrees with the IBD majority in 5%-40% of births | outside [5%, 40%] |
| P5 | NPE: >= 1/3 of the 34 births have two identified donors each >= 10% of the child | < 12 of 34 |
| P6 | NPE: in >= 10/34 births the material of the executed code (Q6) belongs to the victim while the child's IBD majority is the donor | < 10 |
| P7 | both engines: singular-parent loss by identified structure (Q3) is below 10% of births in BEE and above 20% in NPE | either side fails |

## 7. What this cannot establish
- One BEE run and one NPE specimen family: this is not engine-wide.
- In-situ capability is confounded with survival.
- The replays test the ATTRIBUTION instrument. They are not a new science result about either engine.
