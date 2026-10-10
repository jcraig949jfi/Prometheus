# E1 FOUNDRY v2: REPAIR RULES (frozen BEFORE the v2 pilot; the single permitted repair round)

Source: beta04/reviews/REDTEAM_FOUNDRY_PREFREEZE.md (F1-F13). Foundry v1 is preserved as an E1 result:
**demand = feature selection, not composition.** Admission rules are fixed here. The v2 pilot is reported as it comes
out; no further retuning in Beta-04.

1. **Null ladder += frozen REGRESSION rung (F1).** The red team's five cheap policy families:
   - per-class elementwise fits;
   - keep-rule + map;
   - scan transducer;
   - single-statistic polynomial / piecewise fit;
   - one-register linear recurrence.

   Features are derived ONLY from the public operator set in CONFIG, are frozen before the v2 pilot, and are fitted on
   dev and selected on dev (no hindsight). A family solved by any rung is rejected (TRIVIAL_BY_<rung>).
2. **Mechanism screen (F1 / D7):**
   - reject fold steps that are affine in the accumulator;
   - each mechanism's R1 families must survive the regression rung.
3. **Reachability chain replaces the circular prerequisite (F2).** An R3 / R4 family is admitted only if ALL hold:
   - (a) all null rungs fail;
   - (b) base search from scratch fails at B = 1e6;
   - (c) for each constituent mechanism, base search at <= 1e6 FINDS a qualified program on that mechanism's R1
     family;
   - (d) the FOUND programs (not the sealed truth), promoted as library primitives, make R3 reachable: a qualified
     solution within 1e6.

   R2 is admitted by (a) + (b) + the witness / known-positive.
4. **Redacted arm view (F3, F5) and secret seeds (F4):**
   - Arms receive a frozen, hashed export containing an opaque ID and dev examples ONLY: no rung, class, index, status,
     witness, test or tribunal.
   - Seeds are 128-bit secrets, hash-committed by the coordinator.
5. **Clean export (F6):** the export wipes and rewrites tasks/; consumers load only through the manifest.
6. **Reporting fixes:**
   - (F7) an order-free expected rank (random order within each size level) alongside the CRN rank;
   - (F8) NOT_FOUND beyond the enumeration horizon is labelled HORIZON, not desert; an optional registered 1e7
     diagnostic covers multi-step pipelines only;
   - (F12) count dev-consistent programs per family;
   - (F13) a nearest-input lookup fallback.
7. **Motif control (F9):** cap per merged skeleton x mechanism-pair; count near-duplicates once; require >= 3
   mechanism-kind pairings across the admitted set.
8. **R5 combination-reuse rung (F10):** families that reuse an R3 combination with a new outer context, so that depth-2
   inheritance can be demanded in E4.
9. **YOKED world (D10)** and several shuffles per world for history contingency.
10. **D4:** R4 dev from the base distribution; test and tribunal shifted.
11. **D9:** gate only the upper band (reject capture > 0.8); report the lower band.

**The E1 gate is unchanged:** >= 1 admitted family at R2 AND at R3 per qualified world. If the v2 pilot admits no R3
family under these rules, **E1 = WORLD_DEMAND_NOT_QUALIFIED for this generator family.** That is a result, and it
determines what E2-E4 can claim.
