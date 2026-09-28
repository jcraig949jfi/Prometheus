# Attribution v0 -- specification (Archaeon, 2026-09-28)

Directive: roles/Archaeon/prompts/2026-09-28_attribution_v0/00_OPERATOR_DIRECTIVE_verbatim.md.

Code:
- schema.py: the record, the validator (A1-A15) and derived quantities;
- classify.py: production classes, candidate reproduction definitions, transmissions;
- fixtures.py: TH-014 fixtures, adversarial and structure cases;
- regression.py: historical regression;
- guards.py: the saturated-ruler guard;
- assay.py: the cross-engine adapters.

Tests: archaeon/tests/test_attribution_v0.py.


## 0. Status after adversarial Review 1 (2026-09-28): read this first
The review, adjudication and counter-examples are in ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/REVIEW_1_ADJUDICATION.md and
review1/.

1. **s2's "four axes cannot represent it" was argued, not tested.** The field split is the directive's own list. What survives:
   - STATE (IBS) is kept apart from MATERIAL (IBD);
   - the rules stop one field standing in for another (A3, A5, A8, A16, A17).
2. **s4's "only D7 matches" is WITHDRAWN.**
   - D7's lead came from two author-added cases.
   - The reviewer's von Neumann case (constructor BUILT from a copied description) breaks D7.
   - The winner changes with the case set. The case x definition matrix below (15 cases, each tagged with its origin) is the
     result; no definition is frozen.
3. **The validator was hardened:**
   - A1 is token-based and recursive;
   - A4 tiles count-resolution records;
   - A5 forbids source_address / value_match;
   - A14 bars reproduction labels on infrastructure channels, even as conventions;
   - A16 ties infrastructure logs to infrastructure processes (catches the mis-logged channel);
   - A17 requires knockout entries for every machinery locus;
   - donor capability must be an executed claim about the donor.
4. **TH-014 restated.** The classifier maps RECORDED channels to classes. It detects a mis-logged channel only when the
   infrastructure log survives in the material provenance (A16). An instrument that loses the log cannot be rescued by v0.
5. **The assay's BEE/NPE material was not descent (ASSAY.md v2).** Descent is identifiable only in Archaeon's preserved record.

## 1. The record (one per reproduction-like event)

| field | holds | never filled from |
|---|---|---|
| carrier.performers | who performed the operation: a list of {kind, id, role}. Kinds: organism_code, host_organism, neighbour_organism, harness, migration, recombination_operator, transplant, inflow, world_physics, mutation, unknown | material |
| carrier.exec_where / exec_what | WHERE the executing code sat; WHAT material it was (v0.3 three-referent rule) | WHAT is never filled from WHO/WHERE (A3) |
| production.process | the physical process (executed_write, harness_copy, migration_copy, recombination_operator, transplant_insertion, inflow_injection, mutation_only, physics_rule). Its CHANNEL is organism / infrastructure / physics | the performer's identity alone |
| material | identity by descent, per locus when possible: segments {loci, source_kind, entity, src_loci, via}; any number of donors; resolution per_locus / counts / NOT_IDENTIFIABLE | location, executor, context, label or resemblance readings (A5) |
| state.resemblance | identity by state: {reference, ibs, units} | -- (never licenses descent: A8) |
| dependence | list of {target, intervention, outcome, result: ceases / persists / altered / not_tested, contrast, n} | nothing; an unnamed intervention is invalid (A6) |
| capability | list of {capability, result, conditions: {inputs, neighbour, scaffold}, method: executed / replayed, ruler, machinery_loci} | labels (A7: positive claims must be executed) |
| contrast | the baseline for shares, resemblance and dependence (A12) | -- |
| aggregation | every organism- or lineage-level label: {label, value, rule, convention}. parent_id lives ONLY here, under rule SINGULAR_MATERIAL_PARENT, and only when the material supports it (one donor >= 0.75, no other >= 0.10: a declared convention) (A11) | -- |

There is no parent field. A1 rejects `parent*` keys anywhere except aggregation.

## 2. Is it still CARRIER / RELATION / CONTRAST / AGGREGATION? No: five axes plus two qualifiers

| deep-block model | v0 | why it had to change (the case that broke it) |
|---|---|---|
| CARRIER (WHO/WHERE/WHAT) | carrier, kept; performers are a LIST with roles | NPE pair-tape co-execution has no singular producer (STRUCTURE no_singular_producer; NPE assay 9/34 SELF_CONSTRUCTED_WITH_HELP) |
| RELATION (FLOW=IBD, RESEMBLANCE=IBS, DEPENDENCE) | split into MATERIAL (IBD), STATE (IBS), PRODUCTION (process + channel), DEPENDENCE | host execution with neighbour material: the FLOW is N -> child, but who wrote it is H. And TH-014's six same-byte histories have IDENTICAL FLOW and differ ONLY in production. One RELATION axis cannot hold both. These parts also chain differently: production and IBD chain along generations, dependence does not (Hall), and IBS never licenses IBD. |
| (absent) | **CAPABILITY** | what the child can DO is neither a relation between events nor a carrier. Cargo-without-capacity and machinery-without-founder-bytes have the same kind of FLOW and differ only in capability. |
| CONTRAST | qualifier on every quantitative claim (A10, A12) | unchanged |
| AGGREGATION | qualifier; every label names its rule and whether it is a convention (A11) | unchanged, but parent_id moved here |

The five axes are CARRIER, MATERIAL, PRODUCTION, DEPENDENCE and CAPABILITY. STATE is recorded but is not an axis of attribution:
it is the thing attribution must not be confused with.

### Failed representations (kept on purpose)
- **F1. One RELATION axis** could not separate TH-014's histories (above).
- **F2. A singular producer** failed on co-execution.
- **F3. Capability read from labels** (SELF_COPY births continuing) was the deep-block TH-013 inference, and exactly what the
  directive forbids. A7 now requires execution.
- **F4. Machinery = executed addresses** failed. The VM's executed mask marks opcode addresses, not operand bytes. The block-13
  founder's machinery is {3,4,5,6,7,12}; locus 7 (an operand) is invisible to an executed-address scan. Machinery must be
  knockout-defined over ALL loci.
- **F5. Founder-material continuity as the machinery measure** failed twice. Once as an instrument bug (same-position counting; the
  "0.0" retraction). Once by design: D3F rejects machinery-without-founder-bytes, which is reproduction.
- **F6. "Material > 0 plus a capable child" as capacity transmission** (D5) is broken by a trace-material constructed copier.
  Replaced by machinery IBD (D7).
- **F7. Host-assisted capacity is not local.** D7 passes it as RELATIONAL by fiat. v0 cannot yet say WHAT object is transmitted
  when the machinery lives in the host. This is TH-015's question, and it is unresolved here.
- **F8. Per-locus ancestry is rarely available.**
  * BEE and NPE adapters get counts, not loci (resolution "counts"; A4 tiling is not checked).
  * BEE r016299 leaves >= 10% of loci unidentified in 98% of births.
  * My first "singular parent lossy" metric counted NOT_IDENTIFIABLE as loss (99%). Corrected: 0.85% lossy by identified
    structure; 98% not identifiable.
- **F9. The Archaeon adapter derives performer kind (organism_code vs host_organism) from the material majority.** That is partly
  circular. Production classes that depend on it (HOST_WRITTEN) inherit the circularity.
- **F10. Circularity of the adversarial verdicts.** The intended verdicts were written by the same author as the definitions.
  This is the first thing Review 1 was asked to attack.

## 3. Validator rules
- **A1:** shape; no parent / template / ancestor keys (whole-token, recursive) outside aggregation and native.
- **A2:** the process must be carried by a matching performer kind. An infrastructure process credited only to organisms is
  rejected (harness leak).
- **A3:** WHAT is not from WHO/WHERE.
- **A4:** per-locus AND count-resolution segments tile the child; NOT_IDENTIFIABLE material names no donor; known source kinds.
- **A5:** material sources come through material channels (taint, provenance_log, harness_log, replay_taint, operator_log,
  by_construction), never location / pc / executor / context / label / resemblance.
- **A6:** dependence names target, intervention, outcome and result.
- **A7:** positive capability is executed/replayed, with a ruler and conditions.
- **A8:** a descent label needs a material donor, and its value must be a donor (IBS is not IBD).
- **A9:** a self label needs organism-channel production by the donor itself.
- **A10:** a tested dependence names its contrast.
- **A11:** aggregation declares a rule and a convention; parent_id needs a singular material parent.
- **A12:** reported shares need a contrast.
- **A13:** resemblance entries name a reference.
- **A14:** a non-convention reproduction label needs an executed copy capability.
- **A15:** a recombinant label needs >= 2 distinct donors (a self-cross is one donor).
- **A16 (after Review 1):** material whose provenance is an infrastructure log (harness_log, operator_log) requires an
  infrastructure process. This catches the channel mis-logged as an organism write.
- **A17 (after Review 1):** every machinery locus in a positive capability claim needs a knockout dependence entry (target
  machinery, result ceases) for the same subject.
- Donor capability is read only from executed capability claims whose `subject` is the donor.

## 4. Copying vs heredity
- **MATERIAL transmission:** some child loci are identical by descent to a donor (`S.donors`).
- **CAPACITY transmission:** the child demonstrably copies (executed), AND the loci its copying depends on (knockout-defined
  machinery) descend from a donor that could copy (`K.machinery_ibd`, D7).
- **HEREDITARY transmission:** a named variant intervention on the donor reaches a child that still copies (dependence target
  material, result persists) (D6).
- **REPRODUCTION:** NOT frozen. The candidates D1-D7_STRICT are scored on 12 adversarial cases:

(Superseded matrix removed; the current 15-case matrix follows. The 12-case version is in git history at 29f06c41a.)

| case (origin) | intended | D1_RESEMBLANCE | D2_MATERIAL | D3_BYTE_IDENTITY | D3F_FOUNDER_MATERIAL | D4_ORGANISM_MATERIAL | D5_CAPACITY | D5T_CAPABLE_MATERIAL | D7_MACHINERY_IBD | D7_STRICT | D6 heredity (intended) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| self painting homopolymer (artemis) | yes | Y | Y | Y | . (wrong) | Y | Y | Y | Y | Y | . (no) |
| homopolymer painter (directive) | no | Y (wrong) | . | . | . | . | . | . | . | . | . (no) |
| exact copier no heritable variation (directive) | yes | Y | Y | Y | . (wrong) | Y | Y | Y | Y | Y | . (no) |
| cargo without capacity (directive) | no | . | Y (wrong) | . | . | Y (wrong) | . | . | . | . | . (no) |
| machinery without founder bytes (directive) | yes | Y | Y | Y | . (wrong) | Y | Y | Y | Y | Y | Y (yes) |
| scaffolded copier (directive) | yes | Y | Y | Y | . (wrong) | Y | Y | Y | Y | Y | Y (yes) |
| host executed copier (directive) | yes | Y | Y | Y | . (wrong) | Y | Y | Y | Y | Y | Y (yes) |
| recombined offspring (directive) | yes | . (wrong) | Y | . (wrong) | . (wrong) | Y | Y | Y | Y | Y | Y (yes) |
| changed encoding conserved function (directive) | yes | . (wrong) | Y | . (wrong) | . (wrong) | Y | Y | Y | Y | Y | Y (yes) |
| trace material constructed copier (archaeon) | no | . | . | . | . | . | Y (wrong) | . | . | . | . (no) |
| machinery synonymous mutation (archaeon) | yes | Y | Y | . (wrong) | . (wrong) | Y | Y | Y | Y | . (wrong) | Y (yes) |
| harness copy (archaeon) | no | Y (wrong) | Y (wrong) | Y (wrong) | . | . | . | . | . | . | . (no) |
| ibs without ibd (archaeon) | no | Y (wrong) | . | . | . | . | . | . | . | . | . (no) |
| universal copier junk (review1) | no | Y (wrong) | Y (wrong) | Y (wrong) | . | Y (wrong) | . | . | . | . | . (no) |
| von neumann constructor description (review1) | yes | Y | Y | . (wrong) | . (wrong) | Y | Y | Y | . (wrong) | . (wrong) | Y (yes) |

Coordination with Artemis's P-11 attack (FR-011):
- Artemis found that every BYTEWISE NPE event P-11 certifies is a near-homopolymer painter. Its byte is 0x36 = LD (HL),n, whose
  operand equals its opcode. So P-11 cannot tell painting from copying.
- In v0 the self-painter:
  * is IBD at every locus and passes D7 (it does reproduce);
  * fails D6 (no heritable variant survives);
  * is separated from a copier by `S.source_diversity` (distinct source loci per IBD locus: 1/32 vs 1.0). No donor-share metric
    provides this (test_source_diversity_separates_painting_from_copying).
- Recommendation to NPE and Artemis: report source diversity next to every P-11 certificate.

The boundary, as it stands after Review 1. The original text claimed "only D7 survives"; that claim is WITHDRAWN (see git
29f06c41a).
- **"All copying is heredity"** (D1 resemblance, D2 material, D4 organism + material) is too weak: painter, cargo, harness copy,
  junk under a universal copier.
- **"Byte or founder identity"** (D3, D3F, D7_STRICT) is too narrow: changed encoding, synonymous machinery mutation, von Neumann.
- **"Material > 0 plus a capable child"** (D5) is too weak at the trace-material edge.
- **"Machinery descends as material"** (D7) is too narrow for von Neumann's architecture. There the machinery is BUILT from an
  inherited description, so it transmits as information, not as material.
- **D5T** (capable donors supply >= theta of the material, plus a capable child) survives all 15 cases, with theta in (1/32, 0.5].
  But that is again a statement about this case set. A von Neumann automaton with a SHORT description (< theta of the tape) breaks
  it.

**Open boundary: the unresolved question is whether capacity is transmitted as material (D7) or as information that the child
re-expresses (von Neumann).** No local, per-event predicate in v0 separates "a constructor built from an inherited description"
from "a copier computed by the parent from trace material". The difference is counterfactual: does changing the inherited part
change the child's machinery? That is a DEPENDENCE test on the donor's material (knock out description loci in the DONOR; does the
child's machinery change?). This makes it a candidate for v1, not a v0 predicate. Heredity (D6) is a separate test.

## 5. TH-014 known-answer fixture (required for future reproduction instruments)
Six histories end in the same 32 child bytes. Their production classes must come out as:
1. HARNESS_COPY
2. MIGRATION_COPY
3. OPERATOR_RECOMBINATION
4. HOST_WRITTEN
5. NEIGHBOUR_WRITTEN
6. SELF_CONSTRUCTED

In addition, the validator must reject each infrastructure history when it is relabelled SELF_COPY (A9) or re-carried by an
organism (A2).

**Requirement proposed for every future reproduction instrument:** export attribution-v0 records for these six fixtures, and
return six distinct classes and the six rejections.

## 6. Terminology: adopted vs retained

| Prometheus term (before) | adopted external term | what, if anything, the external term misses (why an internal term remains) |
|---|---|---|
| FLOW | identity by descent (IBD) | nothing; FLOW retired |
| RESEMBLANCE / DIFFERENCE | identity by state (IBS); informative sites | nothing; retired |
| per-unit lineage / B1 | local ancestry, ancestral recombination graph (ARG) | nothing conceptually. v0 records local ancestry but does not build an ARG (use tskit-style tables if it is ever needed) |
| RELATION: production vs dependence | Hall (2004) production vs dependence | nothing; adopted as two axes |
| scaffolded origins | Godfrey-Smith (2009) scaffolded reproduction | retained qualifier HOST_ASSISTED (a sub-kind): the scaffold is ANOTHER ORGANISM'S EXECUTING CODE (Tierra parasite), which is not the same as environmental scaffolding (input 128) |
| reproduction vs copying | Griesemer (2000) reproducer: material overlap + development (capacity) transmission | Griesemer gives no locus-level operational test. D7's "machinery IBD by knockout" is our operationalisation, not a new concept |
| self-cross | selfing | nothing; use "selfing" |
| cargo | non-coding / neutral material; GP introns (bloat) | "cargo" is kept only as "non-machinery loci of THIS capability", which is relative to a knockout test |
| WHO / WHERE / WHAT of executing code | von Neumann's dual use of the description (executed vs copied) | covers executed vs copied, but NOT location-of-code vs material-of-code divergence (B6). WHERE/WHAT retained |
| harness / infrastructure channel | experimenter intervention; artificial transfer | no standard term for "the harness moved material and the ruler credited the organism". HARNESS_LEAK retained |
| glin (Archaeon genetic lineage) | clade by majority descent | glin is a specific assignment rule (template >= G/2 copied bytes). Keep the name only inside Archaeon; cross-engine text says "majority-descent lineage" |
| replicator | avoid (Dawkins's replicator presumes the unit) | -- |

## 7. Limits
- Fixtures and regression cases are synthetic shapes; the assay is the only real-data use.
- Capability is not per-event in any engine's record. The assay reports in-situ proxies (BEE: later is_sr) and the block-13
  probes.
- theta is bounded, not pinned.
