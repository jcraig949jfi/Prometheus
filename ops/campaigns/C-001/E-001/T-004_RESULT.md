# T-004 -- Archaeon / BEE / NPE compared on who / where / what (2026-09-27)

Inputs:
- T-001 and T-002 (BEE, code-material replays on ubu001/ubu002, bit-identical to the M2 references);
- T-003 (NPE, observation-only transform of NPE's own tainted VM on ubu001; lineage identical to the preserved replays 11/11;
  instrument equal to NPE's own prov_lit share 34/34);
- T-004 A-003 (Archaeon, location vs material on 176 census copiers x 256 inputs x 2 neighbours, plus the 63-host block-15 panel,
  on ubu002).
Evidence: C:/Prometheus-data/evidence/ops_pilot_2026-09-27/.

## The four readings in each engine's own terms

| role | Archaeon | BEE | NPE |
|---|---|---|---|
| WHO (executor identity) | the executor cell/organism (native) | the writer org (native `parent`) | the executing CONTEXT: tape half 1 or 2 (native `prov`, `prov_lit`) |
| WHERE (code location) | pc < G own region vs >= G neighbour region (native `exec_foreign`) | pc < L own / [L, 2L) window / elsewhere (native `by_own_code`, own/win steps) | which tape half the instruction sits in (not recorded natively; measured in T-003) |
| WHAT (code material) | taint label of each fetched byte, E / N / other (native, travels with writes) | NOT recorded natively; measured by FULL replay: own-region / self-copied into the window / original window bytes / elsewhere | NOT recorded natively; measured in T-003: prov at the code byte (original of its half, or changed by a context this interaction) |
| write-governing material | = WHAT of the instructions executing the writes (Archaeon records fetch material, so single-source executions are decided) | = WHAT of the copy ops' code (T-001/T-002 probe) | = WHAT of the instruction that last wrote each directed byte (T-003) |

## What diverges, per engine (measured)

| engine | WHO vs WHAT | WHERE vs WHAT | numbers |
|---|---|---|---|
| BEE | (writer = WHO throughout) | **large** | r038751: 28,163 births have location-foreign governed writes; by material 27,083 own, 21 foreign, 1,059 NI (1,726,650 writes by self-copied code vs 941 by foreign code). r016299: 38,825 -> 17,501 own, **8,166 genuinely foreign**, 13,158 NI |
| NPE | **large** | small | 481 directed writes over 34 pair births: WHO != WHAT in 127 (26.4%). The victim's thread ran the DONOR's code in 68 writes; the donor's thread ran the VICTIM's code in 59. Code relocated by the other context (WHERE != WHAT) in 17 (3.5%) |
| Archaeon | yes, by design (host executes resident) | present in hosting | self-copying copiers: 19,615 births, no divergence detected. Block-15 hosting births that emit the resident exactly: 3,594. Of these, 2,570 run mostly RESIDENT material in place (WHO != WHAT, WHERE == WHAT); 1,024 run the HOST's own material from the neighbour region (WHERE != WHAT) |

**Host-conditioning and cross-execution (NPE):**
- In births where the donor can rebuild a random victim (P-11 C2 true, 9 births), WHO != WHAT in 11% of directed writes.
- In births where it cannot (C2 false, 25 births: the host-conditioned set), WHO != WHAT in **46%** of writes.
- In the C2-false births the dominant cross-execution is the donor's thread running the victim's code (59 of 97 writes).
- At the majority level, WHO and WHAT disagree in 12 of the 25 host-conditioned births and in 1 of the 9 others.
- This is an association on 34 births from one specimen, not a mechanism proof. It is the first mechanistic lead for AN3: the donor
  uses the host's material as code.

## Classification of earlier disagreements

| earlier item | now | why |
|---|---|---|
| AN1 BEE "decoupling" (233,499 births) | **instrumentation artifact** (mostly) + **true substrate phenomenon** (residual) | location-based execution accounting; in both measured runs most location-foreign governance is self-copied code, but genuine foreign-material governance exists (8,166 births in r016299) |
| FF-28 BEE SR vs step share (38,817) | **unresolved** at the material level | both readings are location-based; whether BEE's SR (pc < L) under-counts self-replication run from self-copied code needs a BEE-wide material recount (not done) |
| v0.2 defect D2 (my BEE adapter: pc >= L = foreign code) | **field-mapping error** (confirmed on 2 runs) | location read as material |
| v0.2 defect D3 / FF-31 (NPE "donor authored" read as governing material) | **field-mapping error** (confirmed) | prov is WHO; WHAT differs in 26.4% of directed writes and at the majority level in 13/34 births |
| D3 / FF-29 NPE in-situ authorship vs C4 | **field-mapping error + legitimate distinction** | in-situ prov = WHO (factual context authorship); C4 = counterfactual authorship; WHAT is a third quantity now measured |
| Archaeon host-mediated reproduction (ENVGATE-01 R2) | **survives, refined** | Archaeon measures WHAT natively. 72% of block-15 hosting births run resident material; 28% run host material relocated into the neighbour region, a second route to the same outcome |
| AN3 NPE host-conditioned (16/34 signature) | **survives; mechanistic lead** | host-conditioning coincides with cross-execution (46% vs 11%) |
| which B6 axis matters | **true substrate difference** | BEE: WHERE != WHAT (self-copied code in the window). NPE: WHO != WHAT (threads run each other's code). Archaeon: both occur; WHAT is native |
| AN8 NPE donor writes not necessary in situ (11/34) | **unresolved** | not addressed by T-003 |

## Still NOT_IDENTIFIABLE
- BEE code executing from "elsewhere" (pc >= 2L): 528,897 writes in r016299 and 66,669 in r038751; the material there is not
  classified by the probe.
- BEE code material in preserved logs: only a FULL replay recovers it.
- NPE donor body: the slot is not recorded.
- NPE same-value retained vs rewritten bytes (outside D).
- Aggregate-only Archaeon divergence: per-step pairs are not recorded, so divergence can be under-detected (the positives are proofs).
