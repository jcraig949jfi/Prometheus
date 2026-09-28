# Review 7 (BEE v5 dry run + prereg v5) -- Archaeon's adjudication (2026-09-28)

**Reviewer:** an isolated claude-opus-5-5 worker on ubu001, 14:22:34Z-14:37:29Z, at 8262c32f2.
- It replayed r022153 itself (32,827/32,827 rows, 86 s).
- It labelled every birth with the INDEPENDENT reference tracer. Data-entity counts agree with the pipeline's tracer on
  32,827/32,827 births; performer counts differ on 1.
- It re-ran the pipeline's analyse_birth and reproduced every dry-run number exactly.
- Review file: review7/REVIEW_7.md. Its scripts and scratch data stayed on ubu001 (~/wk/rev7/); the transcript is on M2 evidence.

**Ruling:** every correction is ACCEPTED. The dry run's numbers stand. Several of its readings do not.

| claim | review | ruling / corrected reading |
|---|---|---|
| (b) "14%: the occupant performs a copy of the writer's material (K3-type)" | real mechanism, misdescribed | **ACCEPTED -- this is a heritable PARASITE lineage** (see s1) |
| (a) "singular-donor record adequate for 99.97% of the dependence" | number right, reading wrong | **ACCEPTED.** Q8c excludes the performer by construction. The existence dependence on the host (0.88 in the parasite class) is invisible to it, and Q8c-whether was never computed although R2 requires it |
| (c) "native target label wrong in 57%: IBS read as IBD" | real disagreement, wrong mechanism | **ACCEPTED.** 183/191 are frame-shifted copies; positional fidelity is shift-blind. Only 18/191 are genuine IBS-as-IBD. The CI for the C3 reading is 0.574 [0.520, 0.628]; it is 46% without the identifiability filter |
| (d) "85% capable; material and capacity mostly coincide" | average hides a total split | **ACCEPTED.** Self-performed: 117/120 capable. Parasite class: 0/120 |
| Verdict ALTERED via P2 | weakly warranted | **ACCEPTED.** P2 is a finding about BEE's NATIVE label, not a v0 field. R3 requires ALTERED routes to name a v0 field. **Corrected dry-run reading for BEE: v0 VALIDATED (pending production); P2 holds as a BEE-native-label finding; a new parasite finding** |
| Pipeline deviations: flip only on the sample, Q8c-whether missing, pooled flip coverage, the verdict set by hand, Q2 numbers from an uncommitted file | accepted | fixed in the production spec (Amendment C4) and in the pipeline before any reuse |
| Per-class flip coverage: the "other" class 0.537 (fresh sample CI [0.497, 0.651]) | accepted | recorded; C4 sets the per-class rule |

## 1. The parasite finding (the arc's most important result so far; dry run, not production)
In r022153, 4,313 births (13.1% of all births, 14% of the transmission class) form a Tierra-style parasite lineage (Review 7 s2,
executed):
- **No copy code:** 83% of these writers contain no LDI/LDIR/COPYALL byte (self-performed writers: 0 of 27,728). 365 are all-zero
  tapes.
- **Mechanism:** the writer's PC falls through off its tape into the occupant at about step 62. The occupant's absolute-addressed
  copy loop (S = 0 from RESET, T = 64) copies bytes 0..63, the parasite, over the host itself.
- **Heredity:** 88% of parasite writers were themselves parasite-born; 1,549 births have >= 10 consecutive parasite generations
  above them.
- **Capability:** 0/120 capable in isolation (mean trial success 0.021). The host's replicator is the capacity.
- **Existence dependence:** randomising the occupant suppresses the birth in 0.882 of draws (self-performed: 0.000).

**Mapped onto attribution v0,** every field needed already exists:
- carrier.performers = the OCCUPANT (host), by material of the store opcode;
- material donor = the WRITER (parasite), IBD at copy-descent;
- dependence = {intervention: "randomise host bytes"; outcome: birth occurs; result: ceases at 0.88};
- capability = {exact_self_copy: False (isolated); host_assisted_copy: True (conditions: neighbour = host replicator)}.

This is v0's hand-written "host_executed_copier" (Tierra parasite) fixture, found in a real run, and v0's separation of performer,
donor, dependence and capability represents it without new fields. That is VALIDATION of the v0 design, not an alteration.

**It also bears directly on both new threads:**
- **thr-5085da70a143 (cargo vs heredity).**
  * Parasites transmit material WITHOUT isolated capacity, yet form heritable lineages (>= 10 generations).
  * So "material descent without reproductive contribution is not heredity" needs refinement. The parasite's reproductive
    contribution is RELATIONAL: it is the host's machinery, triggered by the parasite's position and content.
  * Item 8's non-copier cargo (Archaeon block 13) never persisted. BEE's parasites do.
  * The difference is exactly whether a host's copy map accepts them.
- **thr-c64dca3118a1 (replicator identity).** The replicator here is not any single tape. It is the host-parasite relation.
  Identity is lineage-level AND relational.

## 2. What changes before production (Amendment C4 to v5)
See ANCESTRY_PREREG_v5.md, Amendment C4. It is made after the dry run and flagged as such, but BEFORE any production data from
either owner.
