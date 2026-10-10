# E3 DESIGN DRAFT: MINIMAL TFS-1, LIFETIME ORGANISM, 2x2 PROMOTION x ARCHIVE (NOT FROZEN)

C-015, W02. This is the implementation target for the runner. It is frozen, red-teamed and registered only after the
E1 production set is known. Pilot worlds (pilot_v2) are exposed, development-only data.

## 1. Known-positive first: TFS1_INSTRUMENT_QUALIFIED
- **Procedure:** replicate the foundry's reachability chain with the INDEPENDENT substrate (interpreter B / TFS-1
  enumeration). For each admitted R3 / R4 family:
  - (i) TFS-1 base enumeration from scratch on each constituent mechanism's R1 family, budget 1e6;
  - (ii) promote the FOUND program's mechanism (the function-typed argument subterm; closed; alias-collapsed);
  - (iii) TFS-1 enumeration with that library on the R3 / R4 family, budget 1e6, until the first dev-consistent
    program; then the test + tribunal verdict.
- **TFS1_INSTRUMENT_QUALIFIED = YES** iff the chain succeeds on >= 80% of the admitted R3 / R4 families, and
  from-scratch TFS-1 enumeration fails them at 1e6.
- **Otherwise:** TFS1_REACHABILITY_INSTRUMENT = FAIL (per the directive), with no scientific rejection.

## 2. Lifetime organism (identical base semantics in all arms)
- **Lifetime:** the world's families are presented in CURRICULUM order, through the ARM VIEW only (opaque id + dev).
- **Search per family:** budget B charges (matched across arms; candidate value 2e5), with a fixed base operator:
  mutation chain search (atlas `chain`) with restarts every R steps, under common random numbers per (world, family,
  seed). The first dev-consistent program ends the family.
- **Arms:**
  - **PROMOTION (developmental machinery):** after each solved family, collect closed function-typed subterms of the
    solved program plus the TFS-1 compressor's proposals over all solved programs so far. Promote those used by >= 1
    solved program (alias-collapsed; closed over their own args, per v0.1-1). The library cap is K = 8, with a
    deterministic tie-break. The library entries become leaves / operators for the mutator in later families.
  - **ARCHIVE (search infrastructure):** a lifetime archive of programs from earlier families (all solved programs + the
    top-k partial-credit programs per family). Restarts draw parents from the archive (uniformly: one-factor X1 genome
    retention) instead of fresh random terms. It is target-blind and uses dev feedback only. Descriptor-guided
    selection is used only where a descriptor passed qualification on that task class; otherwise it is X1 only.
  - **2x2:** {promotion off/on} x {archive off/on}.
- **Controls:**
  - **RANDOM-LIBRARY:** promotion of K random closed subterms of matched sizes.
  - **SHUFFLED-HISTORY:** promotion on, with families in the SHUFFLED_ANTI order.
  - **RANDOM-ARCHIVE:** an archive of random programs, matched in count.

## 3. Final evaluation (autonomous competence)
- After the lifetime, each solved program is re-evaluated on test + tribunal, with no archive and no search.
- Library primitives are allowed, because they are the organism's own machinery.
- **Endpoint per world:** the number of admitted R3 / R4 families solved (qualified), plus R2 and the total.
- **Cognitive ledger per solved family:** ORGANISM (search found it) / DEVELOPMENTAL (a promoted primitive used) /
  SEARCH_INFRA (archive parent lineage) / CERTIFIER.

## 4. Causal dependency (for any depth claim)
For each R3 / R4 solution that uses a promoted primitive: re-run that family with the primitive REMOVED (base
expressivity intact), and with it replaced by a matched sham primitive. The dependency is supported only if both
fail where the original succeeded.

## 5. Screen
- 8 worlds per cell (the production worlds that pass the per-world gate; if fewer than 8 qualify, all of them, and the
  readout is labelled underpowered).
- Paired exact sign-flip tests across worlds on the R3 / R4 endpoint:
  - promotion effect;
  - archive effect;
  - interaction.
- Screening only. No confirmatory significance is claimed.

## 6. W5P comparator: applicability
- The frozen W5P comparator (W5P + O1 + g12 + alias fix) is defined over the W5 fold language. The Beta-04 tasks are
  typed list pipelines (map / filter / fold / scan / zip), most of which W5 cannot express.
- The comparator is therefore **NOT COMMENSURABLE** on the E1 production worlds. It is reported as such, with the
  fraction of admitted families expressible as a single W5 fold, rather than forced.
