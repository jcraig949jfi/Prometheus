# REVIEW 1 -- adversarial review of REVIEW_1_CLAIMS.md (R1-1 .. R1-6)

Reviewer: independent, no prior context. Checkout ~/Prometheus-worktrees/rev1 at 6ff584d14. Date 2026-09-28.
Test suite as shipped: `python3 -m pytest -q archaeon/tests/test_attribution_v0.py` -> 44 passed. The tests are green. That is not
in dispute. What is in dispute is what they test.

All counter-examples are runnable from the repo root. The three scripts are reproduced verbatim in the appendix:
- cx_schema_defs.py: validator, D7 and NPE-adapter counter-examples, plus the E-002 record.
- cx_bee_scratch.py: BEE adapter, material read from a source address.
- cx_bee_partner_code.py: BEE adapter, performer hard-coded.

The two BEE scripts run Bellerophon's own traced VM (traced_replay._install, unmodified) on hand-built memories. Each one rebuilds
the births row formula-for-formula from traced_replay._register_offspring and passes it to assay.bee_records.

Verdict summary:

| claim | verdict |
|---|---|
| R1-1 representation | FAILS as stated (the "cannot" is never tested; the split is the directive's own field list) |
| R1-2 TH-014 | STANDS WITH CORRECTION (tautological classifier; the realistic leak passes the validator) |
| R1-3 reproduction boundary | FAILS (uniqueness comes from two author-written cases; D7 gives defensibly wrong verdicts; its inputs are not validated) |
| R1-4 historical regression | STANDS WITH CORRECTION (at least one case misstates its source; the rejections are guaranteed by construction) |
| R1-5 cross-engine assay | FAILS for findings a, b, c on NPE and BEE r016299; "0 invalid" carries no information |
| R1-6 retraction | STANDS WITH CORRECTION (minor) |

---------------------------------------------------------------------------------------------------------------------------------

## R1-1 (representation)

**Restated.** A record that stores "who acted / how the two events are related / compared to what / how it was summarised" cannot
hold the directive's cases. You need separate fields for:
- descent of material, locus by locus (identity by descent, IBD);
- similarity (identity by state, IBS);
- the physical process and whether it ran through an organism, the infrastructure or physics;
- intervention-based dependence (a counterfactual).

A separate field is needed for tested capabilities (a phenotype measured under stated conditions). The baseline and the summary
rule are qualifiers, not fields.

Standard terms: IBD/IBS is textbook population genetics. "Production versus material" is Griesemer's distinction between the
material overlap of reproducers and the process that makes them. Capability measured under conditions is the phenotype / reaction
norm. Scaffolded and host-assisted reproducers follow Godfrey-Smith. None of this is new, and the author's own G_PRIOR_ART.md says
as much for the host case.

**Attack.**
1. **Nothing in the evidence tests "cannot".**
   - fixtures.STRUCTURE shows that the NEW schema can hold 8 cases (test_structures_representable_without_parent_field,
     test_attribution_v0.py:183).
   - No fixture tries to encode any case in the four-field model and shows it failing.
   - The argument the claim relies on is "ATTRIBUTION_V0.md s2" (schema.py:20; fixtures.py:4 cites s5). That file does not exist
     at this commit (`find . -name 'ATTRIBUTION_V0*'` finds only the campaign directory).
   - A claim of impossibility with no attempted counter-model is not established.
2. **The split was specified in advance.** The operator directive
   (roles/Archaeon/prompts/2026-09-28_attribution_v0/00_OPERATOR_DIRECTIVE_verbatim.md:24-85) already requires the record to hold
   CARRIER, MATERIAL, PRODUCTION, DEPENDENCE, CAPABILITY, CONTRAST and AGGREGATION separately. "RELATION must split into material,
   production and dependence, and capability is a fifth axis" therefore restates the specification; it is not a finding. The only
   addition is STATE (IBS), and the directive's "identical state with unrelated descent" (item 2) already implies it.
3. **"Contrast and aggregation are qualifiers, not axes" is contradicted by the code.** Both are mandatory top-level keys
   (schema.py:63-64, TOP_KEYS), and rule A12 (schema.py:235) treats a missing contrast as a record-level violation. In the schema
   they are fields like any other. The count of "axes" (4, 5, or the 8 top-level parts in schema.py:6-18) is a naming choice with no
   testable consequence.
4. **"No universal parent field" is a substring filter, not a structural guarantee** (schema.py:160-162). It checks only the keys of
   four sub-dicts, for the substring "parent".
   - CX-1a: `native.parent_id`, a `parent` key inside a material segment, `carrier.template` and `production.ancestor` are all
     VALID. `template` is exactly Archaeon's native field (core.py:256, `"template"`, `template_glin`) that the deep block found
     misleading.
   - CX-1b: a legitimate key `state.apparent_fidelity` is REJECTED (A1), because "apparent" contains "parent".

**Verdict: FAILS as stated.**
- True: the new schema holds the 8 structures.
- Not shown: that the four-field model cannot.
- "Qualifiers, not axes" contradicts schema.py.
- The parent-field guarantee is lexical and can be bypassed (CX-1a) or triggered by a legitimate key (CX-1b).

---------------------------------------------------------------------------------------------------------------------------------

## R1-2 (TH-014, infrastructure leak)

**Restated.** Six synthetic events that end in the same child get six different production classes. The validator rejects every
record in which an infrastructure copy (harness, migration, crossover operator) is credited to the organism.

**Attack.**
1. **The classifier only returns the answer written into the fixture.**
   - production_class (classify.py:16-31) is a lookup on `production.process` and the performer `kind` strings. Each fixture sets
     those by hand (fixtures.py:47-57).
   - The test asserts `classes == {k: k}` (test_attribution_v0.py:118): the known answer is the dict key, and the key was written
     into the record's process field. No byte, log or trace is examined.
   - "Same child bytes" is never checked against the records. The records contain no child bytes. TH014_CHILD_BYTES is a separate
     dict built as `{k: CHILD for k in TH014_LEAK}` (fixtures.py:58), so `len(set(...)) == 1` (test:116) holds by construction.
   - The OPERATOR_RECOMBINATION fixture takes loci 28..32 from Q. The child could only be byte-identical if Q equals P there, and
     that is not represented.
   - What is shown: distinct input labels map to distinct output labels. What is not shown: that histories can be told apart from
     evidence.
2. **The six "leaky variants" (fixtures.py:61-71) each keep one field honest.**
   - `+SELF_LABEL` keeps the infrastructure process. `+ORGANISM_CARRIER` also keeps the infrastructure process (A2 fires on the
     process/carrier mismatch).
   - The historical leak (Z80A-D05; BEE migration; Z80xAtlas transplants) was an infrastructure copy LOGGED AS the organism's event.
     In a record, that means the process and the carrier are both wrong.
   - Written that way, the leak PASSES:
     - CX-2a: process `executed_write`, performer `organism_code P`, material `via="harness_log"`, label SELF_COPY. VALID, class
       SELF_CONSTRUCTED.
     - CX-2b: splice material `via="operator_log"` on an organism `executed_write`, labelled "reproduction". VALID.
   - The validator never checks that a `harness_log` / `operator_log` material channel agrees with an infrastructure process, even
     though the record carries exactly the evidence that would catch the leak.
3. **A14 exempts every label marked `convention: true`** (schema.py:216).
   - CX-2c: a harness copy labelled `replicator` with convention=True is VALID.
   - Nothing stops a writer from marking a mistaken label as a "convention".

**Verdict: STANDS WITH CORRECTION.** Correct statement: "Given records whose `process` and performer kinds already correctly
describe the channel, production_class returns six distinct labels, and the validator rejects a SELF label or an organism-only
carrier that contradicts the recorded infrastructure process." It does not detect a leak in which the channel itself was mis-logged
(CX-2a, CX-2b). Calling it a "known-answer fixture required for future reproduction instruments" (fixtures.py:5) overstates it: any
instrument that writes the right process string passes.

---------------------------------------------------------------------------------------------------------------------------------

## R1-3 (reproduction boundary)

**Restated.** Nine candidate predicates for "this event is reproduction" were scored against 12 cases, each with a verdict the
author chose. Only one predicate agrees with all 12. It says reproduction iff:
- an organism, not the infrastructure, did the writing;
- the child passes an executed copy test;
- at least theta of the loci the child's copying depends on descend from a donor that could copy.

For a host-assisted child, "no local loci" counts as a pass.

The coined term "machinery IBD" hides this assumption: the machinery loci are an input written into the capability claim, not
something the code derives by knockout.

**Attack.**
1. **Circularity: the unique win comes entirely from two cases the author added.** Scoring each predicate on the directive's own 8
   cases (00_OPERATOR_DIRECTIVE_verbatim.md, item 3) gives three perfect scorers: D5_CAPACITY, D7_MACHINERY_IBD and D7_STRICT
   (cx_schema_defs.py, last block).
   - D7 beats D5 only on `trace_material_constructed_copier`.
   - D7 beats D7_STRICT only on `machinery_synonymous_mutation`.
   - Neither case is in the directive. Each one is built to break exactly one rival, and its intended verdict was set by the author
     of D7.
   - The fixture docstring says three cases are "ours" (harness copy, IBS without IBD, one producer / two donors) (fixtures.py:6).
     In fact four are added (harness_copy, ibs_without_ibd, trace_material, synonymous). The listed "one producer / two donors" is
     not in ADVERSARIAL at all.
2. **Constructed cases where D7 gives an answer I defend as wrong.**
   - **CX-3a: a universal copier makes inert junk "reproduce".**
     - Setup: host H copies junk J into the child. J is declared not capable. The child passes a host-assisted copy test, which is
       true of any string in a world with a universal copier. No locus of J affects copying, so the knockout-defined machinery is
       empty.
     - Result: machinery_ibd returns "RELATIONAL" and D7 is TRUE (classify.py:114). D5 correctly says False.
     - Why this is wrong: the case is the fixture's own `cargo_without_capacity` (intended False), moved under a host. The RELATIONAL
       clause does not look at the donor's capability at all. It treats "no locus matters" (pure cargo) the same as "the machinery
       is outside the child" (a real parasite).
     - Tierra parasites are not like this: knocking out their templates or jump code removes copying, so they have local machinery.
       The fixture's `host_executed_copier` encodes the Tierra parasite with `machinery=[]` (fixtures.py:116), which is wrong about
       Tierra.
   - **CX-3b: von Neumann's architecture.**
     - Setup: a description (loci 16..32) is copied from P, and a constructor (loci 0..16) is BUILT from it. That is von Neumann's
       self-reproducing automaton: the machinery is constructed and only the description is copied.
     - Result: with machinery set to the copy-loop loci (the fixtures' convention, MACH), D7 is FALSE for every theta > 0. The
       author's own D6_HEREDITARY is TRUE on the same record.
     - So the author's "heredity" predicate accepts, as heritable reproduction with variation, an event that the author's
       "reproduction" predicate rejects. "Heredity is separate from reproduction" only holds because D6 is built on D5, not on D7.
     - If the knockout-defined machinery also includes the description (damaging the description does break exact copying), the
       verdict depends on byte counts: D7(0.5) is True and D7(0.6) is False. A definition of reproduction whose verdict on von
       Neumann's automaton depends on the ratio of description bytes to constructor bytes does not track the concept.
   - **CX-3c: the inputs D7 depends on are not validated.**
     - `machinery_loci` is a free list in the capability claim. No rule requires a matching knockout entry in `dependence`.
     - Setting `machinery_loci=[0]` on the fixture's `trace_material_constructed_copier` gives a VALID record with D7 TRUE, reversing
       the case D7 was built to win.
     - Donor capability is read from `rec["native"]["donor_capabilities"]` (classify.py:37, 103), a free field that rule A7 never
       checks. "Labels are not capability" (schema.py:14) is enforced for the child, not for the donor.
3. **Theta is not bounded by data.** The fixtures produce only four machinery-share values: 0.0, 0.8, 1.0 and RELATIONAL.
   - "(0, 0.8]" is just the gap between two author-chosen points. The 0.01 floor is the grid step in test:165.
   - Any case with a share between 0 and 0.8 is decided by an unchosen parameter.
4. Minor points.
   - The claim says 9 predicates. test_only_machinery_ibd_matches_every_intended_verdict silently excludes D6_HEREDITARY
     (test:151), so 8 are tested.
   - The "executed" capability in fixtures is a dict literal `method="executed"`. No execution happens anywhere in R1-3.

**Verdict: FAILS.**
- On the directive's cases, D7 does not stand alone.
- Its uniqueness depends on two author-written cases whose verdicts the author assigned.
- D7 accepts junk copied by a universal copier (CX-3a).
- D7 rejects von Neumann's architecture while the author's heredity predicate accepts it (CX-3b).
- D7 flips on unvalidated inputs (CX-3c).

---------------------------------------------------------------------------------------------------------------------------------

## R1-4 (historical regression)

**Restated.** Ten past Prometheus misattributions were hand-encoded as synthetic records with the correct fields. v0 gives each the
expected class, and rejects each record once the historical wrong label is added.

**Attack.**
1. **The rejections hold by construction.**
   - Every record already carries the correct material and production, written by the author (regression.py:33-104).
   - The historical errors happened because those fields were wrong or missing when the label was assigned. Re-labelling a record
     that is already correct tests only that the validator notices a direct contradiction.
   - With the fields as the engines actually logged them (CX-2a, CX-2b), the mistaken labels are ACCEPTED.
   - The test also accepts ANY violation as a rejection (`assert S.check(r2)`, test:234). It does not check that the rule that
     fires is the relevant one.
2. **`archaeon_self_cross` misstates its source.**
   - The cited E-002 self-cross is a PTE genetic-algorithm crossover (a == b) produced by `search.py` truncation parents over 64
     units. Sources: A_E002_REVIEW.md:13; E-002/T-008_T-011_RESULTS.md:32-36.
   - regression.py:69-75 encodes it as an Archaeon organism's `executed_write`, n = 32, with an invented executed `exact_self_copy`
     capability, and expects SELF_CONSTRUCTED with reproduction True.
   - Encoded faithfully (CX-4a: recombination_operator, operator_log, one donor A over 64 units) the class is OPERATOR_RECOMBINATION
     and D7 is False.
   - The "recombinant" label is still rejected (A15), but the expected class and the reproduction verdict for this case are wrong
     about history.
3. **`npe_p11_failing_overwrite` treats P-11 C2 as a capability test** (`cap("exact_self_copy", False, ..., ruler="NPE P-11 C2")`,
   regression.py:56). assay.py:16 states the opposite: "P-11 is a test of the EVENT's dependence, not of the child's capability".
   The case's `reproduction: False` rests on that misfiled capability claim.

**Verdict: STANDS WITH CORRECTION.** Correct statement: "For ten hand-built records, written with the correct channel and
material, the validator rejects a contradicting label." Beyond that:
- It is not evidence that v0 would have caught any of these errors from the data available at the time.
- At least one case (E-002) is recorded with the wrong channel and engine.
- One (P-11) contradicts the author's own treatment of P-11 elsewhere.
- The author's caveat "shape reconstructions" does not cover a changed channel.

---------------------------------------------------------------------------------------------------------------------------------

## R1-5 (cross-engine assay)

**Restated.** Engine-specific converters turn preserved birth logs from BEE, NPE and Archaeon into v0 records, and the validator
passes all of them. From these records the author reports four findings:
- how often BEE's similarity-based "material" label disagrees with a descent reading;
- how often the writer is not a source of material;
- how often a single-parent summary loses information;
- how often writer-majority children later make an in-situ self-copy.

I did not have the M2 inputs (paths are `C:/Prometheus-data/...`), so I did not re-derive the numbers. I audited the converters
against the source code they cite. The printed numbers are consistent with the adapter formulas and with ASSAY.json. They do not
measure what the claims say they measure.

1. **BEE: "IBD" is a reading of the source address, stamped `via="replay_taint"`.**
   - Row field 8 (`copied_from_own`) counts window bytes whose last write was a copy op with SOURCE ADDRESS < L
     (traced_replay.py:237).
   - The tracer's last-writer map covers only the window (traced_replay.py:83-84). Bytes at [0, L) that were overwritten earlier in
     the same execution are not traced.
   - assay.py:57 turns field 8 into writer material with `via="replay_taint"`, a channel A5 accepts. Under the schema's own rule this
     is a `location` reading (FORBIDDEN_VIA, schema.py:51); the label hides that.
   - **CX-5a** (cx_bee_scratch.py, real traced VM):
     - Setup: the writer copies the partner's bytes into its own scratch region [20, 64), copies them back into the window and
       changes one byte.
     - Ground truth: 63 of 64 child bytes are the partner's own bytes at the same position.
     - The native similarity label says `target`, which is correct.
     - The adapter gives writer material 0.69 and occupant 0.30, class ORGANISM_RECOMBINATION_SELF_INCLUDED. It counts the birth
       under `native_label_target_but_IBD_majority_writer`: the adapter is wrong and it blames the label.
   - So finding (a), "the label contradicts descent in 23% of r016299 births, almost all label-target / descent-writer", mixes two
     things:
     - genuine label errors from shifted copies, which the positional similarity cannot see (`cx_bee_partner_code.py 12`:
       a shift-by-12 copy gives the label `target` and a correct writer majority);
     - adapter errors of the CX-5a kind.
   - The row cannot tell these apart. In PAIR_EXECUTION, where the partner's code can write the writer's half (world.py:15, 362-371),
     the second kind cannot be ruled out. The finding is UNTESTABLE AS STATED from the preserved row.
2. **BEE: the performer is hard-coded, so the "producer != donor" figures for BEE are mostly fixed by the adapter.**
   - assay.py:70 always records the writer alone as `organism_code`.
   - That holds even when the native row says the writer's code did none of the copying: field 9 `by_own_code` = 0, window steps > 0,
     and codeprov `foreign` = 100%.
   - **CX-5b** (cx_bee_partner_code.py, real traced VM): the PARTNER's code copies the writer's tape over the whole window.
     - The native tracer separates this: by_own_code 0, codeprov foreign 64, and is_sr would fail.
     - The adapter records performer = writer and class SELF_CONSTRUCTED, and producer_ne_donor is False.
   - This is exactly the TH-014 NEIGHBOUR_WRITTEN vs SELF_CONSTRUCTED distinction from R1-2, and the assay collapses it.
   - ASSAY.json itself counts `code_run_mostly_occupant_material` = 10,398 r016299 births and 168 r038751 births. All of them are
     credited to the writer alone.
   - In r038751 (ENDOGENOUS_COPY: a birth requires all L bytes written, world.py:11/500), the occupant is never a donor. With a fixed
     performer, `producer_ne_any_donor` = 0.0% there is a tautology.
   - The adapters are also inconsistent: the NPE adapter adds the victim as a co-performer (assay.py:96), while BEE and Archaeon never
     add the partner (Archaeon records `executed_material: mixed` for 5,363 births, assay.py:119/123). The cross-engine comparison in
     (b) therefore compares adapter policies.
3. **NPE: the "material" is code location plus code provenance, not descent.**
   - T-003's WHO|WHERE|WHAT is defined (npe_b6_replay.py:11-16) over positions D where the final byte EQUALS THE DONOR'S BYTE, "by
     construction of D".
   - WHERE is the address of the INSTRUCTION. WHAT is "code byte provenance at execution", i.e. the provenance of the executing
     instruction.
   - assay.py:88-89 sums `(where == donor_half and what == original) or what == changed_by_donor` into donor MATERIAL, and the same
     for the victim. It puts these into material segments with `via="replay_taint"`.
   - The author's previous adapter labelled this same formula "write_governing ... code-byte provenance at execution", a carrier
     quantity (adapters_v03.py:49-51). assay.py:102 also stores it as carrier.exec_what. The same number fills both the carrier field
     and the material field: the conflation the schema exists to prevent (J21; A3/A5).
   - **CX-5e:** 40 positions whose bytes are all, by construction, the donor's, written by the victim's original code, become 62.5%
     VICTIM material, class SELF_CONSTRUCTED_WITH_HELP. VALID.
   - Every NPE figure in (b) and (c) (8.8%, 23.5%, 73.5%, and two_plus_donors 50%) is computed on this. The positions outside D
     (bytes that already matched, or that did not end up equal to the donor's) are labelled "unknown". That accounts for the 73.5%
     "not identifiable": it is an artefact of how T-003 selected positions, not a property of NPE.
4. **"Not identifiable" is defined differently per engine.**
   - BEE: everything that is neither copied-from-own nor untouched is `unknown` (assay.py:59). That includes non-copy writes of
     computed or constant values, copies from source addresses >= L (the tracer had those sources; the row dropped them), and the
     zeros of an empty target cell (into_empty sets retained = 0, assay.py:54).
   - Archaeon: the same residue is `new_unspecified` (assay.py:118) and counts as identified.
   - "BEE 98.0% vs Archaeon 0%" in (c) compares these adapter choices. The 98% is a limit of the row format, not of BEE: the
     traced replay held the source for every window byte.
5. **"0 invalid records" carries no information.**
   - Every adapter record uses `resolution: "counts"`, which switches off the A4 tiling check (schema.py:181).
   - Process, performer kind, contrast and via are set to constants that satisfy A2/A3/A5/A12.
   - No aggregation labels are emitted, so A8/A9/A11/A14/A15 never run.
   - CX-5c: three overlapping full-length segments (donor shares 1.0 + 1.0, new share 1.0) are VALID.
   - CX-5d: an impossible BEE row (64 bytes copied-from-own out of 10 written) gives donor shares summing to 1.84, and the record is
     VALID.
6. **Scope.**
   - "Three engines" rests, for NPE, on 34 births from one specimen family.
   - The claim reports 8.8% and 23.5% (3 and 8 events) to 0.1%. Stated honestly, they are 3/34 and 8/34.
7. Finding (d) uses the address-based writer majority from point 1. BEE capability is an in-situ later is_sr event labelled
   `method: "replayed"` (assay.py:65), which A7 accepts as executed evidence. Also, `donor_capabilities: {w: bool(r[11])}`
   (assay.py:69) makes the writer "capable" iff THIS birth is is_sr. It is unused in the reported numbers, but it is circular.

**Verdict: FAILS for findings (a), (b) and (c) on NPE and on BEE r016299.**
- The NPE "material" is code location and code provenance (CX-5e).
- The BEE "descent" is a source-address reading (CX-5a).
- The BEE producer is fixed by the adapter (CX-5b).
- "0 invalid records" is guaranteed by construction (CX-5c, CX-5d).

What survives: the Archaeon adapter, which reads the taint VM's per-byte labels (core.py:196-213), is a descent reading. Even there
the carrier omits the co-executing neighbour.

---------------------------------------------------------------------------------------------------------------------------------

## R1-6 (retraction)

**Restated.** The earlier claim was that none of the founder's original bytes remain anywhere in block-13's dominant lineage. It is
withdrawn, because the metric only matched the founder's byte p at position p, and the founder copies with shifts.

**Check.**
- block13_probe.py:48 is exactly `w.orig[c][p] == fid * 32 + p`. The defect is real.
- `fid` is consistent with core.py:101/221 (founder_oid = f; orig = f*32 + p), so the zero is not a wrong-id bug.
- The dated notes are appended, and the original text is kept, in D_Z80_SYNTHESIS.md, F_FRONTIER.md, REPORT.md and TH-013.md.

**Corrections.**
1. The note explains the zero as displacement by a near-copier only. The record documents more:
   - ENVGATE01_REVIEW_2026-09-24.md:239-245 says the near-copier 447,492 was "failing (18 births, 6 exact, dead by epoch 14,072)".
   - The takeover came from HOST EXECUTION by INERT arrival 446,966 starting at epoch 14,001.
   - Background mutation (core.py:155-159) also replaces material ids with new ones.
   - So the lineage measured "after 14,800 epochs" was about 800 epochs old, and it was propagated by a host. Both matter for any
     re-measurement. The retraction should name them rather than suggest displacement as the explanation.
2. The note says "18 births, 6 exact" in the older record, while the retraction says "no exact self-copy on any input". The first is
   an in-situ count and the second an isolated-VM test, so both can be true, but the difference should be stated.
3. The corrected measurement "goes in ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/". At this commit that directory holds only
   REVIEW_1_CLAIMS.md and assay/. The retraction is therefore correctly labelled "unsupported, not refuted", and no replacement
   number exists yet.

**Verdict: STANDS WITH CORRECTION** (the three points above).

---------------------------------------------------------------------------------------------------------------------------------

## Single strongest objection

The assay's "material" fields for BEE and NPE are carrier readings relabelled as descent:
- BEE: source address < L, stamped `replay_taint`.
- NPE: instruction location and code-byte provenance, a formula the author earlier labelled "write_governing".

The validator cannot see this, because an adapter can write any `via`, and the `counts` resolution switches off the only structural
check. The schema built to separate carrier from material therefore certifies ("0 invalid records") exactly the carrier/material
conflation it was built to catch, and CX-5a/CX-5e produce label-vs-descent "contradictions" in which the adapter, not the label,
is wrong.

---------------------------------------------------------------------------------------------------------------------------------

## Appendix A -- cx_schema_defs.py (run: python3 ~/wk/rev1/out/cx_schema_defs.py)

Output at 6ff584d14:
```
CX-2a harness_log material + organism process + SELF_COPY  check=VALID class=SELF_CONSTRUCTED
CX-2b operator_log material, organism process, 'reproduction' (convention) check=VALID class=ORGANISM_RECOMBINATION_SELF_INCLUDED
CX-2c harness copy + 'replicator' convention=True          check=VALID
CX-1a parent_id in native, 'parent' in a segment, template/ancestor keys check=VALID
CX-1b legitimate key 'apparent_fidelity' in state (REJECTED) check=['A1 state.apparent_fidelity: parent fields are allowed only as an aggregation convention']
CX-5c three full-length overlapping segments               check=VALID donors={'P': 1.0, 'Q': 1.0} new=1.0
CX-5d impossible BEE row (own 64 > written 10)             check=VALID donors={'bee:1': 1.0, 'bee:occupant_of_slot_before_2': 0.84375}
CX-5e 40 positions carrying the donor's bytes, written by victim code check=VALID donors={'npe:victim': 0.625} class=SELF_CONSTRUCTED_WITH_HELP
CX-3a host copies inert junk J (J not capable)             check=VALID D7=True D5=False machinery_ibd=RELATIONAL
CX-3b von Neumann constructor+description                  check=VALID D7=False D6_HEREDITARY=True D5=True
   same, machinery = constructor+description (16/32 descend): D7(theta .5)=True D7(theta .6)=False
CX-3c trace_material with machinery_loci=[0]               check=VALID D7=True (intended False)
   perfect on directive's 8 cases : ['D5_CAPACITY', 'D7_MACHINERY_IBD', 'D7_STRICT']
   perfect on all 12              : ['D7_MACHINERY_IBD']
CX-4a faithful E-002 self-cross                            check=VALID class=OPERATOR_RECOMBINATION D7=False (regression.py expects SELF_CONSTRUCTED, reproduction True)
```

```python
"""Counter-examples against schema.check (R1-1/R1-2/R1-5), classify.D7_MACHINERY_IBD (R1-3) and the NPE adapter (R1-5).
Run from the repo root:  python3 ~/wk/rev1/out/cx_schema_defs.py"""
import copy, json, os, sys
sys.path.insert(0, os.path.expanduser("~/Prometheus-worktrees/rev1"))
from archaeon.attribution import schema as S, classify as K, fixtures as F, assay as A
from archaeon.attribution.schema import seg
from archaeon.attribution.fixtures import base, perf, cap, mat

def show(tag, rec, extra=""):
    print("%-58s check=%s %s" % (tag, S.check(rec) or "VALID", extra))

print("== R1-2: the leak when BOTH process and carrier were mis-logged (the historical situation) ==")
# CX-2a: harness copy logged the way the engine logged it (organism executed_write), material provenance = the harness log.
r = base("cx.leak", "C", [perf("organism_code", "P")], "executed_write", mat(seg(0, 32, entity="P", src_lo=0, via="harness_log")))
r["aggregation"] = [{"label": "SELF_COPY", "rule": "native_flag", "convention": False}]
show("CX-2a harness_log material + organism process + SELF_COPY", r, "class=" + K.production_class(r))
# CX-2b: operator splice logged as organism write (Z80A-D05 shape), two donors, via operator_log, labelled self_reproduction by the donor
r = base("cx.splice", "child", [perf("organism_code", "donor")], "executed_write",
         mat(seg(0, 58, entity="donor", src_lo=0, via="operator_log"), seg(58, 64, entity="recipient", src_lo=58, via="operator_log"), n=64))
r["aggregation"] = [{"label": "reproduction", "rule": "native_flag", "convention": True}]
show("CX-2b operator_log material, organism process, 'reproduction' (convention)", r, "class=" + K.production_class(r))
# CX-2c: A14 exempts conventions entirely: a harness copy labelled 'replicator' as a declared convention is VALID
h = copy.deepcopy(F.TH014_LEAK["HARNESS_COPY"]); h["aggregation"] = [{"label": "replicator", "rule": "native_flag", "convention": True}]
show("CX-2c harness copy + 'replicator' convention=True", h)

print("\n== R1-1: 'no universal parent field anywhere but aggregation' is a substring filter ==")
r = copy.deepcopy(F.TH014_LEAK["SELF_CONSTRUCTED"]); r["native"]["parent_id"] = "P"; r["material"]["segments"][0]["parent"] = "P"
r["carrier"]["template"] = "P"; r["production"]["ancestor"] = "P"
show("CX-1a parent_id in native, 'parent' in a segment, template/ancestor keys", r)
r = copy.deepcopy(F.TH014_LEAK["SELF_CONSTRUCTED"]); r["state"]["apparent_fidelity"] = 1.0
show("CX-1b legitimate key 'apparent_fidelity' in state (REJECTED)", r)

print("\n== R1-5: resolution 'counts' disables A4; any count arithmetic passes ==")
r = base("cx.counts", "C", [perf("organism_code", "P")], "executed_write",
         {"unit": "byte", "n_units": 32, "resolution": "counts", "segments": [seg(0, 32, entity="P"), seg(0, 32, entity="Q"), seg(0, 32, "new_computed")]})
show("CX-5c three full-length overlapping segments", r, "donors=%s new=%s" % (S.donors(r), S.new_share(r)))
row = [0, 1, 2, "PAIR_EXECUTION", 0.5, 0.5, "writer", 10, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]   # 64 copied-from-own of 10 bytes written: impossible
rec, = A.bee_records({"births_rows": [row], "codeprov": [{"own_region": 0, "self_copied": 0, "foreign": 0, "elsewhere": 0}], "rid": "x"})
show("CX-5d impossible BEE row (own 64 > written 10)", rec, "donors=%s" % S.donors(rec))

print("\n== R1-5: NPE adapter turns WHERE/code-provenance into MATERIAL ==")
# In T-003 every counted position D has, by construction, the DONOR's byte value (npe_b6_replay.py docstring: 'VALUE: equals the
# donor's byte by construction of D'). The adapter nevertheless assigns these positions to the victim when the victim's original
# code executed the write.
d = {"results": [{"name": "toy", "births": [{"child": 7, "n": 64, "D": 40, "who_where_what": {"victim_ctx|victim_half|original": 40}}]}]}
rec, = A.npe_records(d)
show("CX-5e 40 positions carrying the donor's bytes, written by victim code", rec,
     "donors=%s class=%s" % (S.donors(rec), K.production_class(rec)))

print("\n== R1-3: D7 counter-examples ==")
dc = {"donor_capabilities": {"P": True, "J": False, "N": True}}
def rec_(eid, performers, m, caps, native=dc, dep=None):
    return base(eid, "C", performers, "executed_write", m, capability=caps, native=dict(native), dependence=dep or [])
# CX-3a universal-copier cargo: host H copies inert junk J (donor NOT capable). Any string is 'host-assisted copyable'; no locus of J
# matters, so knockout-defined machinery is empty -> RELATIONAL -> D7 True. Same event as cargo_without_capacity, but D7 flips.
r = rec_("cx.junk", [perf("host_organism", "H")], mat(seg(0, 32, entity="J", src_lo=0)),
         [cap("host_assisted_copy", True, {"neighbour": "host:H-class"}, machinery=[])])
show("CX-3a host copies inert junk J (J not capable)", r, "D7=%s D5=%s machinery_ibd=%s" % (K.D7_MACHINERY_IBD(r), K.D5_CAPACITY(r), K.machinery_ibd(r)))
# CX-3b von Neumann architecture: description loci [16,32) copied from P, constructor loci [0,16) BUILT from the description (computed).
# Child builds grandchildren the same way; a variant in the description is inherited by a child that still reproduces.
VAR = dict(F.VARIANT_OK, intervention="variant: flip a description byte in the donor before copying")
r = rec_("cx.vn", [perf("organism_code", "P")], mat(seg(0, 16, "new_computed"), seg(16, 32, entity="P", src_lo=16)),
         [cap("exact_self_copy", True, machinery=[3, 4, 5, 6, 12])], dep=[VAR])
show("CX-3b von Neumann constructor+description", r, "D7=%s D6_HEREDITARY=%s D5=%s" % (K.D7_MACHINERY_IBD(r), K.D6_HEREDITARY(r), K.D5_CAPACITY(r)))
r2 = copy.deepcopy(r); r2["capability"][0]["machinery_loci"] = list(range(0, 32))   # knockout of description loci also kills copying
print("   same, machinery = constructor+description (16/32 descend): D7(theta .5)=%s D7(theta .6)=%s" % (K.D7_MACHINERY_IBD(r2, .5), K.D7_MACHINERY_IBD(r2, .6)))
# CX-3c machinery_loci and donor_capabilities are unvalidated author inputs: the fixture's own trace_material case flips to
# 'reproduction' by listing the one descended locus as machinery.
t = copy.deepcopy(F.ADVERSARIAL["trace_material_constructed_copier"]["record"]); t["capability"][0]["machinery_loci"] = [0]
show("CX-3c trace_material with machinery_loci=[0]", t, "D7=%s (intended False)" % K.D7_MACHINERY_IBD(t))
t = copy.deepcopy(F.ADVERSARIAL["cargo_without_capacity"]["record"]); t["native"]["donor_capabilities"] = {"P": True}
print("   donor capability is read from rec['native'] (no A7 check): any record can assert {'P': True}")

print("\n== R1-3: which cases decide D7's uniqueness ==")
DIRECTIVE = ["homopolymer_painter", "exact_copier_no_heritable_variation", "cargo_without_capacity", "machinery_without_founder_bytes",
             "scaffolded_copier", "host_executed_copier", "recombined_offspring", "changed_encoding_conserved_function"]
for sub, keys in (("directive's 8 cases", DIRECTIVE), ("all 12", list(F.ADVERSARIAL))):
    ok = [n for n, fn in K.DEFINITIONS.items() if all(fn(F.ADVERSARIAL[k]["record"]) == F.ADVERSARIAL[k]["intended"]["reproduction"] for k in keys)]
    print("   perfect on %-20s: %s" % (sub, ok))

print("\n== R1-4: the E-002 self-cross, recorded as what it was (a PTE GA crossover operator, 64 units, a == b) ==")
r = base("cx.e002", "child", [perf("recombination_operator", "search.py crossover")], "recombination_operator",
         mat(seg(0, 32, entity="A", src_lo=0, via="operator_log"), seg(32, 64, entity="A", src_lo=32, via="operator_log"), n=64))
show("CX-4a faithful E-002 self-cross", r, "class=%s D7=%s (regression.py expects SELF_CONSTRUCTED, reproduction True)"
     % (K.production_class(r), K.D7_MACHINERY_IBD(r)))
```

## Appendix B -- cx_bee_scratch.py (CX-5a)

Output:
```
row: [0, 1, 2, 'PAIR_EXECUTION', 0.031, 0.984, 'target', 45, 44, 44, 1, 0, 0, 12, 0, 0, 0, 0.0, 0, 0]
ground truth: child bytes identical to partner's original bytes at the same locus: 63 / 64
native label (resemblance): target
adapter donors (IBD): {'bee:1': 0.6875, 'bee:occupant_of_slot_before_2': 0.296875}  invalid: []  class: ORGANISM_RECOMBINATION_SELF_INCLUDED
assay counts this birth under 'native_label_target_but_IBD_majority_writer': True
```

```python
"""Counter-example CX-5a: BEE adapter reads 'copied from the writer's own region' (source ADDRESS < L) as writer IBD.
Runs Bellerophon's own traced VM (traced_replay._install, unmodified) on a 2L pair-execution memory, rebuilds the row
exactly as traced_replay._register_offspring does, and feeds it to archaeon.attribution.assay.bee_records."""
import os, sys, random
REPO = os.path.expanduser("~/Prometheus-worktrees/rev1")
sys.path.insert(0, REPO); sys.path.insert(0, REPO + "/roles/Bellerophon/forensics_2026-09-23/tools")
import traced_replay as TR
vm, W = TR._install()
from archaeon.attribution import assay as A, schema as S, classify as K

L = 64
rng = random.Random(1)
b = bytes(rng.randrange(0x80, 0xFF) for _ in range(L))        # partner/occupant tape (bytes >=0x80: never executed here)
code = bytes([0x01, 0x99,  0x08, 112,  0x11,                  # A=0x99; T=112; (T)=A      -> 1 non-copy write into the window
              0x07, 64,  0x08, 20,  0x03, 44,  0x15,          # S=64 T=20 C=44 LDIR  : partner bytes -> writer's scratch [20,64)
              0x07, 20,  0x08, 64,  0x03, 44,  0x15,          # S=20 T=64 C=44 LDIR  : scratch -> window (src < L)
              0xFF])
a = code + bytes(L - len(code))
mem = bytearray(256); mem[:L] = a; mem[L:2 * L] = b
TR._ACC.update(L=L, writes={}, own_steps=0, win_steps=0, other_steps=0, prior=b, writer_tape=a)
tr = vm.execute(mem, 2 * L, 0, 500, [])
child, new_a = bytes(mem[L:2 * L]), bytes(mem[:L])
ws = TR._ACC["writes"]
# ---- row, formula-for-formula from traced_replay._register_offspring (parent.tape == new_a at that point in world.step)
fid_w = 1.0 - sum(x != y for x, y in zip(child, new_a)) / L
fid_t = 1.0 - sum(x != y for x, y in zip(child, b)) / L
material = "target" if fid_t > fid_w else "writer"
own = sum(1 for _, (src, pc, op) in ws.items() if op in TR.COPY_OPS and src is not None and src < L)
byown = sum(1 for _, (src, pc, op) in ws.items() if op in TR.COPY_OPS and src is not None and src < L and pc < L)
row = [0, 1, 2, "PAIR_EXECUTION", round(fid_w, 3), round(fid_t, 3), material, len(ws), own, byown,
       sum(child[k] != b[k] for k in range(L)), 0, 0, TR._ACC["own_steps"], TR._ACC["win_steps"], TR._ACC["other_steps"], 0,
       round(1 - sum(x != y for x, y in zip(child, a)) / L, 3), 0, 0]
cp = {"own_region": byown, "self_copied": 0, "foreign": 0, "elsewhere": 0}
true_partner_bytes = sum(child[k] == b[k] for k in range(L))
rec, = A.bee_records({"births_rows": [row], "codeprov": [cp], "rid": "toy"})
print("row:", row)
print("ground truth: child bytes identical to partner's original bytes at the same locus:", true_partner_bytes, "/", L)
print("native label (resemblance):", material)
print("adapter donors (IBD):", S.donors(rec), " invalid:", S.check(rec), " class:", K.production_class(rec))
top = max(S.donors(rec), key=S.donors(rec).get)
print("assay counts this birth under 'native_label_target_but_IBD_majority_writer':", material == "target" and top == "bee:1")
```

## Appendix C -- cx_bee_partner_code.py (CX-5b; argument 12 = shifted-copy variant)

Output (no argument, then argument 12):
```
row: [0, 1, 2, 'PAIR_EXECUTION', 1.0, 0.016, 'writer', 64, 64, 0, 63, 0, 0, 128, 125, 183, 0, 0, 0, 0]
native: copied_from_own=64 by_own_code=0 own_steps=128 win_steps=125 codeprov foreign=64
adapter performers: [{'kind': 'organism_code', 'id': 'bee:1', 'role': 'performer'}]  exec_what: {'via': 'replay_taint', 'writer_material': 0.0, 'occupant_material': 1.0, 'unclassified': 0.0}
adapter class: SELF_CONSTRUCTED  producer_ne_donor: False  invalid: []
row: [0, 1, 2, 'PAIR_EXECUTION', 0.031, 0.203, 'target', 52, 52, 0, 51, 0, 0, 64, 5, 0, 0, 0, 0, 0]
native: copied_from_own=52 by_own_code=0 own_steps=64 win_steps=5 codeprov foreign=52
adapter performers: [{'kind': 'organism_code', 'id': 'bee:1', 'role': 'performer'}]  exec_what: {'via': 'replay_taint', 'writer_material': 0.0, 'occupant_material': 1.0, 'unclassified': 0.0}
adapter class: ORGANISM_RECOMBINATION_SELF_INCLUDED  producer_ne_donor: True  invalid: []
```

```python
"""Counter-example CX-5b: in PAIR_EXECUTION the PARTNER's code performs the copy; the BEE adapter still records the writer
as the sole performer (kind organism_code) and the birth as SELF_CONSTRUCTED. The native tracer itself separates the two
(by_own_code = 0, win_steps > 0, codeprov 'foreign'); the adapter keeps those numbers in exec_where/exec_what and ignores them."""
import os, sys, random
REPO = os.path.expanduser("~/Prometheus-worktrees/rev1")
sys.path.insert(0, REPO); sys.path.insert(0, REPO + "/roles/Bellerophon/forensics_2026-09-23/tools")
import traced_replay as TR
vm, W = TR._install()
from archaeon.attribution import assay as A, schema as S, classify as K

L = 64; rng = random.Random(2)
a = bytes(rng.randrange(0x50, 0x80) for _ in range(L))          # undefined opcodes: executes as a NOP sled into the window
SHIFT = int(sys.argv[1]) if len(sys.argv) > 1 else 0                 # 0: full-window copy; 12: shifted copy (label error case)
bcode = bytes([0x07, 0, 0x08, 64 + SHIFT, 0x03, 64 - SHIFT, 0x15, 0xFF])   # partner code: S=0 T=64+SHIFT C=64-SHIFT LDIR, HALT
b = bcode + bytes(rng.randrange(0x50, 0x80) for _ in range(L - len(bcode)))
mem = bytearray(256); mem[:L] = a; mem[L:2 * L] = b
TR._ACC.update(L=L, writes={}, own_steps=0, win_steps=0, other_steps=0, prior=b, writer_tape=a)
vm.execute(mem, 2 * L, 0, 500, [])
child, new_a = bytes(mem[L:2 * L]), bytes(mem[:L]); ws = TR._ACC["writes"]
fid_w = 1 - sum(x != y for x, y in zip(child, new_a)) / L; fid_t = 1 - sum(x != y for x, y in zip(child, b)) / L
own = sum(1 for _, (s, pc, op) in ws.items() if op in TR.COPY_OPS and s is not None and s < L)
byown = sum(1 for _, (s, pc, op) in ws.items() if op in TR.COPY_OPS and s is not None and s < L and pc < L)
foreign = sum(1 for _, (s, pc, op) in ws.items() if op in TR.COPY_OPS and s is not None and s < L and L <= pc < 2 * L)
row = [0, 1, 2, "PAIR_EXECUTION", round(fid_w, 3), round(fid_t, 3), "target" if fid_t > fid_w else "writer", len(ws), own, byown,
       sum(child[k] != b[k] for k in range(L)), 0, 0, TR._ACC["own_steps"], TR._ACC["win_steps"], TR._ACC["other_steps"], 0, 0, 0, 0]
rec, = A.bee_records({"births_rows": [row], "codeprov": [{"own_region": byown, "self_copied": 0, "foreign": foreign, "elsewhere": 0}], "rid": "toy"})
print("row:", row)
print("native: copied_from_own=%d by_own_code=%d own_steps=%d win_steps=%d codeprov foreign=%d" % (own, byown, row[13], row[14], foreign))
print("adapter performers:", rec["carrier"]["performers"], " exec_what:", rec["carrier"]["exec_what"])
print("adapter class:", K.production_class(rec), " producer_ne_donor:", S.producer_ne_donor(rec), " invalid:", S.check(rec))
```
