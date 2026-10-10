# PHASE-3 WIND-TUNNEL INTERFACE PROPOSAL FROM BETA-04 (C-015) -- DRAFT v0

Status: DRAFT; finalised at the Beta-04 close.

It proposes how Beta-04's instruments plug into the Phase-3 RSO wind tunnel. It does NOT merge runtimes (synthesis
D01: "one minimal contract and verdict adapter only after review"). Interface terms follow the RSO v0.1 design /
closure v0.4 and the S1 contract (rso/slice001/contract, v1.0.x).

## 1. What Beta-04 offers the wind tunnel
1. **WORLD FOUNDRY for typed list-program demand** (`foundry/`; E1).
   - A generator of mechanism families at rungs R1-R5.
   - The null ladder: constant, lookup + nearest, reactive, history2, fixed library, small search 1e5, and the frozen
     REGRESSION rung.
   - Admission requires a known-positive chain (reachability chain a-d).
   - Secret 128-bit world seeds under sha256 commitment; a redacted ARM VIEW (id + dev only) separated from the
     EVALUATOR side.
   - It maps onto the RSO **W0 calibration / W1 demand** roles, and onto the demand generator d = (H, L, C, V, I, Q)
     with C = compositional depth (rung) and V = mechanism variability.
   - It meets Fable's "generator may propose, an exact solver must certify": every admitted family has a sealed witness
     and an independent certifier.
2. **DUAL INTERPRETERS with a conformance known answer** (K-AB: interpreter A in the foundry vs interpreter B in
   TFS-1; 204k + 48k runs, 0 mismatches). This is a reusable **DETECTION-qualification** template: two independent
   semantics, one contract, a mismatch is fatal.
3. **KNOWN-POSITIVE CHAIN instrument with first-failing-link labels** (E3-KP).
   - Labels: R1_ACQUISITION / UNDERDETERMINED_STONE / HORIZON_R1 / COMPOSITION_HORIZON / COMPOSITION_UNDERDETERMINED.
   - These are typed nulls that map onto the RSO's: REACH_UNESTABLISHED (horizons), WORLD_INSUFFICIENT or DETECTION
     (underdetermination), CAPACITY (composition given true stones).
   - This is the RSO **CLIMBABILITY / REACH** question in executable form, with secondary rows that isolate one link at
     a time (given-true-stones, fallback-off, all-acquired, seeds).
4. **REACHABILITY ATLAS + archive-factorisation driver** (E2; `atlas/`).
   - One-factor arms: credit_blind / chain_strict / chain_neutral / D1-X3 / X3G / desert_ref.
   - Matched random-archive calibration (Nyx M2).
   - Outcome-free descriptor qualification BEFORE an archive arm may run (the C-013 D1 procedure).
   - Sharded, resumable, CRN per (world, family, seed).
   - An analyzer that re-derives every endpoint from stored program text (Palamedes #2079).
   - This is the RSO s13 **search geometry** measurement, plus a frontier-archive test.

## 2. Registered developmental cell for a Beta-04 claim
C = (Phi, B, W, D, P, S, M, R):

| Field | Meaning |
|---|---|
| Phi | the representation: TFS-1 typed s-expressions, contract v0 + v0.1-1 (closed learned primitives) |
| B | charges: 1 per candidate on dev; expanded AND promoted unit ledgers; OE INFRA ledger when used |
| W | the foundry world set: secret seeds + WORLD_MANIFEST hash |
| D | the developmental operator: promotion rule, extraction (incl. readout fallback), library cap |
| P | the search policy: enumeration order / mutation chain; the first-dev-consistent stopping rule |
| S | the seeds (CRN keys) |
| M | the measurement: test + tribunal, value-or-FAIL agreement, archive OFF at final evaluation |
| R | the ruler: the per-label frozen definitions in the prereg + freeze files |

Every Beta-04 label is rendered with its cell. "Not detected in this cell under this budget" never becomes "does not
exist".

## 3. Receipt adapter (three-field, S1-compatible)
Each Beta-04 label maps to {execution RAN / BLOCKED; authority QUALIFIED@stage / UNQUALIFIED; outcome}:
- **Authority stage** = AUTHOR_TESTED for anything only the lead tested. FIRST_SIGHT_CHALLENGED after the independent
  red team / review. CLOSED_AFTER_REPAIR only where a registered repair round closed a finding.
- **Instrument authority inherits the LOWEST stage among its prerequisites** (FD-B6). Example: E3-KP's authority is
  bounded by the foundry's (FIRST_SIGHT_CHALLENGED after the pre-freeze red team).
- **Custody:** freeze files carry git-blob hashes (line-ending independent). For anchor registration, Beta-04 proposes
  the registrar (Aporia) records {FREEZE_*.json blob sha, commit sha} rows in the out-of-repo store; Beta-04 never
  holds the producer authority key.
- **Render refusals apply.** E.g. "TFS-1 cannot compose" is refused (RENDER_QUANTIFIER_UNBOUND). The renderable form
  is: "in cell C, with true stones given, the chain qualified 14 / 15 at B = 1e6".

## 4. What the wind tunnel should take from Beta-04's results (to be completed at close)
- **Stone ACQUISITION needs its own qualification checks** (revised after independent review v1, F2 / F3 / F9).
  1. **Extraction invariance.** A mechanism extracted from a found program must be invariant to semantics-preserving
     refactorings of that program. In Beta-04, 3 / 4 "underdetermined" stones were mis-cuts of globally correct
     programs (e.g. affine parts hoisted outside a max / min). Proposal: a wind-tunnel known answer that feeds the
     extractor equivalent rewrites and requires identical stones.
  2. **Budget coverage of the witness size class.** Report the fraction of the witness's size class covered by the
     budget. In Beta-04, 1e6 covered about 7% of the size-8 class, so acquisition was an order lottery (seeds 0 / 1 / 2
     gave 7 / 9 / 8 of 15).
  3. **IDENTIFIABILITY of stepping-stone tasks** (dev sets contain the distinguishing boundary inputs). This is kept as
     a proposed qualification question with typed null STONE_UNDERDETERMINED. Its Beta-04 support is ONE case
     (Wc025415a p0: no element 5 in dev, so x > 4 vs x > 5 cannot be told apart).
- **Descriptor qualification before archive arms is a wind-tunnel GATE, not a reporting option.** In Beta-04 the
  descriptor qualified on 5 / 15 families (2 / 5 clusters), which censored FRONTIER_ARCHIVE_EFFECT before any outcome.
- **The first-failing-link vocabulary should be the wind tunnel's ascent-from-scratch report format** (RSO s14), so
  that a negative names its link.

## 5. Minimal adapter (proposed; not built)
`rso/adapters/beta04.py` (future, after review):
- reads a Beta-04 FREEZE_*.json + result JSON;
- emits S1-schema receipts (rso.slice001.receipt.v1 node ids `rcpt:<subject>:<predicate>:<world>`) with the cell
  fields above;
- refuses to emit any label whose freeze hash does not match the code that produced the result.

No runtime merge.
