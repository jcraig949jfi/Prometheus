# Cross-engine attribution assay (directive item 13) -- Archaeon, 2026-09-28

The same attribution-v0 schema was run over bounded preserved samples. Nothing was re-simulated.

- Adapters: archaeon/attribution/assay.py.
- Output: assay/ASSAY.json, result_sha256 0ff534181c3db4f2fcb6fea4da70ca13d36d2101e78424e5f47a3194adefbf2c.
- Input sha256 (M2 evidence):

| input | sha256 |
|---|---|
| BEE r038751 | b1fef410070c... |
| BEE r016299 | 83a24a85ba12... |
| NPE T-003 | 003f50616ef3... |
| Archaeon block 13 | e95abcc6cb33... |

Full hashes are in ASSAY.json.

Every record validated (0 invalid of 211,403). Each engine kept its own mechanisms: the production classes differ per engine, and
nothing was mapped onto another engine's vocabulary.

| question | BEE r038751 (ENDOGENOUS_COPY) | BEE r016299 (PAIR_EXECUTION) | NPE T-003 (34 births) | Archaeon block 13 (53,185) |
|---|---|---|---|---|
| producer != some material donor | 0.0% | 0.85% | 8.8% | 3.9% |
| majority donor != producer | 0.0% | 0.51% | 8.8% | 0.71% |
| two or more identified donors | 0.0% | 0.66% | 50% | 3.3% |
| singular parent loses IDENTIFIED structure (other donor >= 10%, new >= 10%, or producer != donor) | 0.0% | 0.85% | 23.5% | 4.9% |
| material NOT IDENTIFIABLE (>= 10% of loci untraced) | 3.6% | 98.0% | 73.5% | 0% |
| resemblance mistaken for descent (native label vs IBD majority) | 1.1% (845: label "target", IBD majority writer) | 23% (19,126 "target" vs writer; 7 the reverse) | executor-identity vs material: 15/34 disagree on majority (WHO vs WHAT) | parent chain = executor: 0.71% name a non-majority donor |
| material without demonstrated later capability (writer-majority children seen writing, never is_sr) | 40% | 99.96% | n/a (capability not recorded; P-11 tests the event) | block-13 probe: about 16% of births (sampling-weighted) are non-copier children; TH-013 item-8 tracking follows them |
| scaffold dependence | all births need the world (ENDOGENOUS_COPY); capability only in situ | 100% need a partner (PAIR_EXECUTION) | pair-tape co-execution; 25/34 births have victim-context writes | isolated-VM capability of children: SELF_COPY 86.7%, HOST_EXECUTION 47%, NEIGHBOUR_COPY 35% (deep block) |

## Reading, engine by engine (what the schema preserved)
- **BEE.** Descent is almost always one writer (ENDOGENOUS_COPY), so a singular parent loses nothing IDENTIFIED.
  * But BEE's own `material` field is assigned by resemblance (traced_replay.py: "target" when the child resembles the replaced
    occupant more than the writer).
  * It contradicts the traced descent majority in 1.1% (r038751) and 23% (r016299) of births. That is IBS read as IBD, now
    measured.
  * In r016299, 98% of births leave >= 10% of loci untraced. The schema carries that as NOT_IDENTIFIABLE instead of inventing a
    parent.
  * r016299's writers pass material to children that almost never self-replicate (18 of about 47,770 children seen writing).
    That is material transmission with ~no capacity transmission, in a PAIR_EXECUTION world.
- **NPE.** Half of the 34 births have two identified material donors.
  * The executing context (WHO) and the code material (WHAT) disagree about the majority in 15/34.
  * A singular parent loses identified structure in 23.5%.
  * 6/34 are P-11 causal (unchanged).
  * This is the engine where "parent" is least adequate.
- **Archaeon.** Production is almost always by the majority donor.
  * 0.71% are host-written: the executor is not the majority donor. The parent chain names the wrong entity there.
  * 3.3% have two donors.
  * Material is fully identified (native taint).

## Limits
- One or two runs per engine. NPE is 34 events.
- BEE and NPE material is at count resolution (not per locus), so segments are pseudo-ordered.
- "Material without capability" uses different rulers per engine (BEE: later is_sr in situ, which confounds with death; Archaeon:
  isolated VM). These rows are not comparable across engines; they are placed side by side, not pooled.
- The Archaeon adapter infers host_organism from the material majority (ATTRIBUTION_V0.md F9).
