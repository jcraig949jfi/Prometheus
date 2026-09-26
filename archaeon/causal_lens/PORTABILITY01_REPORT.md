# PORTABILITY-01 report -- can the causal lineage lens leave the Z80 machine?

Author: Archaeon[m2-1034e815]. 2026-09-26. Ruling: roles/Archaeon/prompts/2026-09-26_portability01/00_OPERATOR_RULING_verbatim.md.
Contract: archaeon/causal_lens/CAUSAL_LINEAGE_CONTRACT.md v0.1, frozen at 13cdec715 BEFORE any foreign adapter existed.
Foreign adapters were frozen before their native adjudications were read: BEE at 0d598efd2, NPE at 19b9e76c9. PTE has no
native parentage to read.

## 1. What was run (nothing new and long; every run is a replay of preserved or frozen inputs)

| target | engine (independent implementation) | evidence used | lens mode | units |
|---|---|---|---|---|
| A | Archaeon (archaeon/lineage) | ENVGATE-01 block 13 replay to epoch 14,800 (1,518 s); real block-15 tapes on the real VM; fixtures | FULL FORENSIC (taint VM) | 5 fossils, 54,616 births in block 13 |
| B | Bellerophon BEE (prometheus/z80atlas, harness 16fc6c2a) | 845 preserved traced-birth logs (C:\Users\James\z80atlas_forensics_2026-09-23_local\births) + run configs; BEE's SPECIMEN_LEDGER for the native reading | LIGHT (offline over native trace counts) | 845 runs, 28,964,089 births |
| C | Nestor NPE (Cycle-9 z80atlas-verify, frozen MANIFEST) | H2 RESERVOIR arms replayed exactly as frozen; observer subclass, shown bit-identical (summary + lineage) and 0% overhead | FULL (observer + NPE's own P-11 provenance) | 36 runs (12 seeds x arms A/B/C), 34 pair-tape births |
| D | Ananke PTE (non-copy control) | 6,596 preserved C1 rows; one instrumented GA replay (pop 16, 6 gens, CPU), champion and curve identical to the un-instrumented run | stored rows + FULL (GA operator log) | 76 GA operations; 99 transfer rows |

## 2. Archaeon reference results (Target A) -- PASS

| fossil | required distinction | lens result | native | field status |
|---|---|---|---|---|
| A1 autonomous copier | executor = template = genetic ancestor; unhosted | REPRODUCTION; contributors = own HU; host NONE; spontaneous YES | SELF_COPY, template executor | AGREES |
| A2 inserted lineage hosted by a random executor | inserted ancestry survives hosting (I1); host is not the ancestor (I2/I3) | child HU = resident's; spontaneous NO; executor HU not a contributor; AMPLIFICATION+HOSTING | HOST_EXECUTION, child glin inserted | AGREES |
| A3 block-15 host panel (63 inert founders, 23 emit the resident) | many labels, one genetic architecture | 23 events, 23 distinct native parent labels, 23 distinct hosts, contributor = the ONE resident HU in all 23 | parent chain: 23 lineages | AGREES with the genetic reading; DISAGREES with the parent chain (FF-1, by design) |
| A4 block-13 host rescue | the dominant lineage is the near-copier's genome, not the host's; the host gets host credit only | dominant glin 1071 = arrival 447492; host arrival glin 1072 hosted births into it and is never a contributor | same (test_10) | AGREES |
| A5 random-origin establishment | establishment of a random-inflow HU | glin 1071 ESTABLISHMENT; origins {RANDOM_INFLOW, COMPUTED}; spontaneous YES | genetic_established = [1071] | AGREES |
| (block-13 hosting count) | -- | 359 HOSTING events into 1071 = 82 cross-lineage + 277 same-lineage | births_hosted = 82 | AGREES on 82; 277 LENS_ONLY (FF-26) |

Instrument defect D1, caught by the contract: the first block-13 graph had 12 I2/I3 violations. Neighbour-copied bytes from an
occupant of the SAME glin as the executor got no provenance edge, because the adapter resolved the occupant's glin only when it
differed. The checker refused the unsupported contributor claims. The fix is in adapters/archaeon.py (D1), and the graph was
rebuilt from the preserved events with no replay: 0 violations. Tests: archaeon/tests/test_causal_lens_archaeon.py (3) + corpus (27).

## 3. Native-vs-lens differential (s9)

### BEE (per birth, 28,964,089 births; lens class x native `material` x native `is_sr`)

| lens class | native material | native SR | births | status |
|---|---|---|---|---|
| AUTONOMOUS | writer | yes | 10,814,259 | AGREES |
| AUTONOMOUS | writer | no | 4,974,749 | AGREES on provenance; lens category is WEAKER than SR (>= L/2 own bytes + majority own execution vs BEE's 0.9 thresholds). Not a disagreement about causes |
| AUTONOMOUS | **target** | no | **847,000** | **DISAGREES**: the trace says the writer copied >= L/2 of its own bytes; resemblance credits the target. Mechanism: out-of-position (frame-shifted) copying (FF-27) |
| CAPTURE | target | no | 1,259,948 | AGREES (occupant material persisted; the writer acted) |
| CAPTURE | writer | no | 7,113 | DISAGREES: >= L/2 bytes never written (occupant's), but the occupant already resembled the writer |
| DECOUPLED | writer | yes | 38,817 | **DISAGREES** on "own execution": copy ops ran from own code (native), but most steps ran partner/window code (lens) (FF-28) |
| DECOUPLED | writer/target | no | 194,682 | LENS_ONLY: executor mostly ran foreign code while its OWN material was inherited |
| WRITER_MIXED_EXEC | any | any | 1,235,603 | LENS_ONLY refinement |
| ORIGINATION | writer | no | 13,476 | LENS_ONLY (no majority source; new HU with contributors) |
| UNRESOLVED | any | any | 9,578,442 (33.1%) | NOT_IDENTIFIABLE by the lens (majority source not persisted); native answers anyway, by resemblance |

Run level (BEE's own SPECIMEN_LEDGER, read after the lens run):
- QUARANTINED_INTERVENTION (transplant runs, n = 42). BEE quarantines the whole run. For the run's first autonomous
  reproduction, the lens says it descends from the transplant in 22 runs, from the RANDOM background in 17, and is NOT
  IDENTIFIABLE in 3. Classification: LENS_ONLY refinement. The native quarantine is correct as a run-level policy.
- SELF_REPLICATION_* (sustained / active / transient / missed-by-v1, n = 361). The lens finds an autonomous first reproduction
  with spontaneous YES in 271 and NOT_IDENTIFIABLE in 90. No case has spontaneous NO. AGREES where identifiable.
- TRIGGER_FALSE_POSITIVE_NO_SR (n = 156). The lens still finds AUTONOMOUS births in 153. This is the weaker category (partial
  self-copies), NOT a claim of SR. The native verdict stands.
- Seeded (1 run in the traced set): lens NO. Seed ancestry is protected (I1). AGREES.

### NPE (34 pair-tape births; native = P-11 verdicts, lens = in-situ provenance)

| lens | P-11 pass | C4 (counterfactual authorship) | C5 (donor writes necessary) | n | status |
|---|---|---|---|---|---|
| donor HU resolved | yes | yes | yes | 5 | AGREES |
| donor HU resolved | no | yes | yes | 7 | AGREES on authorship; P-11 fails on C2 |
| donor HU resolved | no | **no** | yes | **8** | **DISAGREES**: in situ the donor authored >= half, but it cannot rebuild a random victim. Reproduction is conditional on the host's prior state (anomaly AN3) |
| NOT_IDENTIFIABLE | no | no | yes | 10 | NOT_IDENTIFIABLE (lens) vs native "not causal". Compatible |
| NOT_IDENTIFIABLE | no/yes | **yes** | yes | **4** | **DISAGREES**: counterfactual authorship high, in-situ authorship < 0.5 (FF-29) |
| native parent == provenance donor | -- | -- | -- | 34/34 | AGREES (executor/donor identity) |
| host = victim body (pre-rename oid) | -- | -- | -- | 34/34 | LENS_ONLY: natively the body's identity is overwritten (FF-11) |

Transplant arm B (the implant = specimen's actual genome): 5 of 24 pair births descend from the implant, 7 from the random
background, 12 NOT_IDENTIFIABLE. Arms A and C: 8 YES, 2 NI.

### PTE (non-copy control)

| question | lens answer | native | status |
|---|---|---|---|
| is a packet material? do packets TRANSFER? | NO / never emitted | packets carry data, no code (DESIGN) | AGREES; decoy correctly refused |
| in-world executor / executed template | site / genome rule r | same by construction | AGREES |
| in-world contributors, host, establishment, amplification | NOT_APPLICABLE | none exist | NOT_IDENTIFIABLE_BOTH (correct abstention) |
| GA parentage from stored rows | NOT_IDENTIFIABLE | not stored | NOT_IDENTIFIABLE_BOTH |
| GA parentage from instrumented replay | 44 REPRODUCTION+MUTATION; 5 recombinant continuations; **11 ORIGINATION+RECOMBINATION with no majority parent** | -- | LENS_ONLY; exposes an ontology limit (B1) |
| `transfer` cells | TRANSFER (transplant), source provenance on 99/99 | extra.source_cell | AGREES |

## 4. Portability matrix (s10)

NATIVE = the engine records it. DERIVABLE = computable from preserved records or a verified replay by a stated rule.
APPROXIMATE = computable only at a coarser resolution or with a stated heuristic. NOT_IDENTIFIABLE = the engine's records
cannot decide. NOT_APPLICABLE = the concept does not exist in the substrate.

| capability | Archaeon | BEE | NPE | PTE (non-copy) |
|---|---|---|---|---|
| material origin | NATIVE (per-byte material ids) | DERIVABLE (founder rule) | DERIVABLE (seeding/implant rule; niche tags = WHERE, not WHOSE) | NATIVE (gen-0 random; transfer = transplant) |
| executor identity | NATIVE | NATIVE (writer) | NATIVE, role depends on mechanism (FF-10) | NATIVE in-world (site); NOT_APPLICABLE for reproduction (GA = NONE) |
| executed / template identity | NATIVE (fetch-source counts) | APPROXIMATE (step shares by region) | NOT_IDENTIFIABLE shares (both halves run) | NATIVE (rule r) |
| child contributor ancestry | NATIVE (taint VM) | APPROXIMATE (own-copy count only; 33% unresolved) | DERIVABLE for pair births via P-11 provenance (41% abstain); NOT_IDENTIFIABLE for private-slot births | NOT_APPLICABLE in-world; DERIVABLE for the GA by replay |
| mutation provenance | NATIVE | NOT_IDENTIFIABLE (not logged) | APPROXIMATE (niche re-tag only) | DERIVABLE (replay) |
| recombination provenance | NATIVE (+RECOMBINATION, contributor set) | NOT_IDENTIFIABLE (mate not recorded) | NOT_IDENTIFIABLE (splice counter only) | DERIVABLE (replay); HU ill-posed |
| transplant provenance | NATIVE (control_inserted) | NATIVE (init_tapes) | NATIVE (implant arms) | NATIVE (transfer cells) |
| host / facilitator identity | NATIVE | APPROXIMATE (writer when capture; occupant not persisted) | DERIVABLE (victim body via observer; lost natively) | NOT_APPLICABLE |
| independent establishment counting | NATIVE (genetic_establishments) | NOT_IDENTIFIABLE from births logs (no deaths) | NOT_IDENTIFIABLE (lineage has no deaths) | NOT_APPLICABLE |
| amplification | NATIVE | APPROXIMATE (CAPTURE; donor HU often NI) | DERIVABLE (pair overwrite) | NOT_APPLICABLE |
| dependency acquisition / loss | APPROXIMATE (arm-level interventions; per birth not identified) | APPROXIMATE (run-level coupling controls) | NATIVE per event (P-11 C5 intervention) | NATIVE at world level (zero-comm control, physics dials) |
| origin vs amplification | NATIVE | APPROXIMATE | DERIVABLE | NOT_APPLICABLE in-world; DERIVABLE in the GA |
| forensic replayability | NATIVE (deterministic; taint == frozen VM asserted) | NATIVE (replay 606/606; traced replay) | NATIVE (bit-identical with observer, verified here) | NATIVE (CPU oracle; champion identical, verified here) |

## 5. Disagreements (preserved, not normalized)
1. BEE resemblance vs provenance: 847,000 + 7,113 births (FF-27).
2. BEE "own code" (copy-op pc) vs "own execution" (step share): 38,817 native-SR births are lens-DECOUPLED (FF-28).
3. NPE in-situ authorship vs counterfactual authorship (C4): 12 of 34 (FF-29).
4. Archaeon native hosted (lineage-level) vs canonical host (entity-level): 82 vs 359 (FF-26). Resolves to AGREES + LENS_ONLY.
5. Parent chain vs genetic lineage: block 15 (23 -> 1), ENVGATE-02 (8-42x) (FF-1).
None of these was resolved by editing either side.

## 6. Newly observed anomalies (preserved; NO campaign launched)
- AN1 (BEE) executor/material decoupling at scale: 233,499 births where the writer spent most of its execution in partner or
  window code while its OWN material was inherited. 38,817 of them are native SR.
- AN2 (BEE) spontaneous-in-intervention: in 17 of 42 quarantined transplant runs, the first autonomous reproducer descends
  from the RANDOM background, not from the transplant.
- AN3 (NPE) host-conditioned reproduction: 8 pair births where the donor authored the victim in situ but cannot rebuild a random
  victim, while its writes are necessary (C5). Reproduction depends on the host's prior state. This is the NPE counterpart of
  Archaeon's host-mediated reproduction (ENVGATE-01 R2) in an independently written engine.
- AN4 (NPE) the transplanted genome is a minority of transplant-arm reproduction: 5 of 24 pair births.
- AN5 (Archaeon) same-lineage hosting: 277 births into the dominant block-13 lineage executed by a different organism of the same
  lineage copying a neighbour. The native births_hosted counter cannot see it.
- AN6 (PTE) genealogy is not a tree: 11 of 16 GA crossovers have no majority parent.
- AN7 (BEE) frame-shifted self-copying: provenance-majority copies whose positional fidelity is < 0.9 (most of the 847k).

## 7. Where the ontology broke (the instruction was to try)
- **B1 heritable-unit continuity by majority provenance is ill-posed under symmetric recombination** (PTE: 11/16) and blurs under
  rearranged copying (BEE AN7). An HU is a convenience, not a primitive. The primitive is the segment-level contribution DAG,
  which the schema already stores. Contract v0.2 should let `resulting_hu` be ILL_POSED (a fourth value, distinct from
  NOT_IDENTIFIABLE) when no source holds a majority, and make establishment counting fall back to architecture classes.
- **B2 ENTITY conflates body and identity.** NPE renames a persisting body (FF-11). The contract needs BODY (location, execution
  state) and IDENTITY (the engine's id) as separate node attributes, or `host` cannot be stated when a body is re-identified.
- **B3 "executed material" is not one quantity.** BEE separates the code that performed the heritable writes from where execution
  time went (FF-28). The contract must name which one is meant (proposal: `write_governing_material` and `execution_share`).
- **B4 provenance has more than one axis.** NPE tags record WHERE a value was made (niche), not WHOSE. The contract's origin classes
  have no spatial axis. Proposal: `material_origin` gains an optional `made_in` location class.
- **B5 authorship is counterfactual or factual.** NPE P-11 C4 (rebuild a random victim) and in-situ provenance disagree in 12/34.
  The contract should carry both: contributor (factual, trace) and sufficiency (counterfactual, replay).
None of B1-B5 forces a Z80 concept. Each is a missing distinction, and each was found by an independent engine.

## 8. Gates (s15)

| gate | result |
|---|---|
| 1 Archaeon reference cases pass | PASS (A1-A5; 0 violations after D1; 30 tests) |
| 2 >= 2 independent engines represented without changing their semantics | PASS (BEE read-only over preserved logs; NPE via an observer shown bit-identical, 0% overhead) |
| 3 >= 1 non-copy engine tested | PASS (PTE) |
| 4 NOT_IDENTIFIABLE representable and used | PASS (BEE 33.1% UNRESOLVED; NPE 14/34; PTE stored rows) |
| 5 a host/executor/material distinction survives outside ENVGATE | PASS: NPE pair tape (executor/donor vs host body, 34/34; host-conditioned reproduction AN3); BEE CAPTURE (writer hosts occupant material, 1.27M, native agrees) and DECOUPLED (AN1) |
| 6 disagreements preserved | PASS (section 5) |
| 7 overhead measured | PASS (OBSERVATORY_DESIGN.md; out/PERFORMANCE.json) |
| 8 no historical verdict silently rewritten | PASS (no BEE / NPE / PTE file edited; frozen ENVGATE results untouched; BEE's quarantine and NPE's P-11 verdicts are reported beside the lens, not replaced) |

## 9. Verdict: **PORTABLE_WITH_DOMAIN_LIMITS**

The executor / executed material / contributor / host distinctions are real outside Archaeon. Two independently written Z80
engines expose them, one of them (NPE) through its own provenance machinery, and the lens reproduces their agreements and localizes
their disagreements to named definitional choices. On the non-copy engine it abstains correctly and refuses the packet decoy.
Domain limits: (a) contributor ancestry is only as good as the persisted provenance (BEE abstains on a third of births); (b)
establishment is not identifiable from BEE or NPE records; (c) the heritable-unit concept is ill-posed under symmetric
recombination (B1). It is not Z80_SPECIFIC, because the contract ran unchanged on PTE and every break found (B1-B5) is a missing
distinction, not a Z80 assumption. It is not PORTABLE_CAUSAL_LENS_SUPPORTED, because of B1 and the establishment gap.

## 10. Recommendation for the next program (s17 outcome B, with a C candidate)
The lens transfers PARTIALLY, so the missing dimensions become the research questions. Priority:
1. **Contract v0.2** (small, no campaign): ILL_POSED heritable units, BODY vs IDENTITY, write-governing vs execution-share
   material, spatial origin axis, factual vs counterfactual authorship. Re-run the three adapters; the differential tables are
   the regression suite.
2. **Outcome-C candidate: host-conditioned reproduction** now has three independent sightings: Archaeon host-mediated amplification
   (ENVGATE-01 R2), NPE AN3 (reproduction that needs a similar host), and BEE CAPTURE/DECOUPLED. A cross-engine preregistered
   assay (same question, three implementations, paired sham hosts) is a stronger next experiment than ENVGATE-03. Proposed only;
   it needs the operator's go.
3. Light-observatory fields as ASKS to seat owners, never impositions: BEE persist `replaced` + per-source write counts; NPE
   persist the victim's pre-rename id and wrote/residue; PTE log GA parent indices.
Nothing was launched after this report.
