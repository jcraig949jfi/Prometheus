# Review 1 -- claims submitted for adversarial review (Archaeon, 2026-09-28)

Protocol (operator directive 2026-09-28 item 11): Archaeon writes the claims; a fresh reviewer with no Archaeon context gets
these claims and pointers to primary evidence, and is asked to INVALIDATE them. Archaeon then adjudicates, and the claims, the
review and the adjudication all stay in the record.
Branch archaeon/attribution-v0-2026-09-28. Code in archaeon/attribution/; tests in archaeon/tests/test_attribution_v0.py.

## Claims

**R1-1 (representation).** CARRIER / RELATION / CONTRAST / AGGREGATION cannot represent the directive's required cases.
- RELATION must split into MATERIAL (identity by descent, per locus), STATE (identity by state), PRODUCTION (the physical process
  and its channel) and DEPENDENCE (named intervention -> outcome).
- CAPABILITY is a fifth axis: a property of an entity under conditions, established by execution.
- CONTRAST and AGGREGATION are qualifiers on claims, not axes.
- Evidence: schema.py (rules A1-A15); fixtures.STRUCTURE (8 directive structures, all valid, none with a parent field);
  schema.singular_parent / singular_loss.

**R1-2 (TH-014, harness leak).** Six histories ending in byte-identical children get six distinct production classes: harness
copy, migration copy, operator recombination, host write, neighbour write, self-construction. The historical mistake (an
infrastructure copy credited to the organism, by label or by carrier) is rejected by the validator in all 6 leaky variants.
- Evidence: fixtures.TH014_LEAK, th014_leaky_variants; tests test_th014_*.

**R1-3 (reproduction boundary).** Of 9 candidate reproduction predicates (D1-D7_STRICT, classify.py), only D7_MACHINERY_IBD
matches the intended verdict on all 12 adversarial cases (fixtures.ADVERSARIAL).
- D7_MACHINERY_IBD = organism-channel production, AND an executed copy capability in the child, AND at least theta of the child's
  knockout-defined machinery loci descend from a capable donor.
- Each other predicate has a named breaker case. The fixtures bound theta to (0, 0.8]; they do not pin it.
- Heredity (a variant introduced into the donor reaches a still-capable child) is separate from reproduction (D6). The exact
  copier with no heritable variation is reproduction without heredity.
- Host-assisted reproduction is accepted as RELATIONAL: the machinery is not local to the child.
- Evidence: tests test_only_machinery_ibd_matches_every_intended_verdict, test_named_breakers, test_threshold_is_bounded_not_pinned.

**R1-4 (historical regression).** Ten documented Prometheus attribution errors, reconstructed as event shapes with sources, are
classified correctly by v0, and each historical mistaken label is REJECTED by the validator when added.
- Evidence: regression.py; test_regression_case.
- Caveat: these are shape reconstructions, not re-extractions of the original events.

**R1-5 (cross-engine assay).** The same schema runs, with 0 invalid records, over preserved samples. Adapters: assay.py. Output:
ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/assay/ASSAY.json.
- Samples:
  * BEE r038751: 74,800 births;
  * BEE r016299: 83,384 births;
  * NPE T-003: 34 births;
  * Archaeon block 13: 53,185 births.
- Findings:
  a. BEE's native `material` label (assigned by resemblance) contradicts the identity-by-descent majority in 1.1% (r038751) and
     23% (r016299) of births. In almost all of these the label says "target" while most traced material is the writer's.
  b. Producer != some material donor: BEE 0.0% / 0.85%; NPE 8.8%; Archaeon 3.9%. Majority donor != producer: Archaeon 0.71%.
  c. A singular parent loses identified structure (another donor >= 10%, new material >= 10%, or producer != donor) in:
     BEE 0.0% / 0.85%; NPE 23.5%; Archaeon 4.9%.
     But material is NOT IDENTIFIABLE (>= 10% of loci untraced) in: BEE 3.6% / 98.0%; NPE 73.5%; Archaeon 0%.
  d. Children carrying a majority of the writer's material that later wrote a self-replication (is_sr) birth, among those seen
     writing at all: BEE r038751 60%; r016299 0.04% (18 of about 47,770).
- Capability is not recorded per event in any engine; see the assay docstring.

**R1-6 (retraction).** The deep-block claim "founder material 0.0 at every position" (block 13) is unsupported. The metric
counted founder material only at the same position, while the founder is a near-copier. Dated notes were added; the original
text is kept.

## Primary evidence the reviewer may use
- Code: archaeon/attribution/{schema,classify,fixtures,regression,guards,assay}.py; archaeon/lineage/core.py (Archaeon engine,
  frozen); archaeon/causal_lens/tools_bee/codeprov_replay.py.
- BEE row layout: roles/Bellerophon/forensics_2026-09-23/tools/traced_replay.py (_register_offspring).
- History:
  * ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/ (D_Z80_SYNTHESIS.md, W1_NPE_LENS.md, W2_BEE_LENS.md, REPORT.md);
  * ops/campaigns/C-001/E-001/;
  * archaeon/causal_lens/FALSE_FRIENDS.md.
- Run: `python -m pytest -q archaeon/tests/test_attribution_v0.py` (needs pytest). The assay inputs are M2-only; the reviewer
  audits the adapter logic, not the numbers.
