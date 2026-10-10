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

## ADDENDUM D (frozen 2026-10-10 after the v2 PILOT and BEFORE any production world; resolves the lead's decisions D1-D5)
The v2 pilot (3 secret seeds; aa2c1a7b1):
- per-world gate PASS 2/3;
- admitted R2 6, R3 5, R4 2, R5 0;
- R3/R4 cover 2 mechanism-kind pairings (fp, fs).

The pilot is a pilot. **The E1 decision is taken on the PRODUCTION set** (the 12 committed secret production seeds)
under the UNCHANGED v2 rules and code (generator c199f0ae, qualification 22d2c387, regression 439e168c):
1. **E1 = WORLD_DEMAND_QUALIFIED iff BOTH:**
   - >= 1 production world passes the per-world gate (>= 1 admitted R2 AND >= 1 admitted R3);
   - **rule 7 holds on the pooled production admitted set** (>= 3 mechanism-kind pairings among admitted R3/R4, after
     near-duplicate merging and caps).

   Otherwise **E1 = WORLD_DEMAND_NOT_QUALIFIED**, with qualifiers (per-world pass count; pairing count). The stricter
   reading is chosen deliberately, without regard to which outcome it favours.
2. **Stepping-stone selection:** the FIRST dev-consistent program must then pass test + tribunal. No hindsight (it is
   learner-realistic).
3. **Hindsight regression diagnostic:** DESCRIPTIVE ONLY, not a gate. Report how many admitted families a hindsight
   regression fit would solve.
4. **Production:** 12 worlds (about 0.3 core-h each).
5. **R5 = 0** in the pilot is recorded. If production admits no R5 family, E4 cannot demand depth-2 inheritance from
   these worlds; that is a stated E4 limitation, not a reason to retune.

**Note:** the evaluator view (test / witness / tribunal) is in the repo. Arms are programmatic and read only the arm
view; no learning arm reads the repository.
