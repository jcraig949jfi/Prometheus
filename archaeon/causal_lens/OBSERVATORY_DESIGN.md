# Causal-lineage lens: two modes (PORTABILITY-01 s14; deliverables 15-16)

Pattern: **cheap online anomaly flag -> preserved evidence -> expensive causal replay.** Neither mode requires an engine to adopt
Archaeon's data structures. Each engine keeps its own records, and an adapter maps them onto the contract.

## LIGHT OBSERVATORY (continuous, native records only)

What an engine emits per reproduction-like event: the fields it ALREADY computes, named by their canonical role, with a basis.

| field | minimal native source | if absent |
|---|---|---|
| executor id | whoever's context ran (BEE `parent`/writer; NPE BIRTH caller or pair-tape donor; Archaeon executor_oid; PTE: NONE) | NOT_IDENTIFIABLE |
| executed-material share | step counts by code region (BEE own/win/other steps; Archaeon exec_counts) | NOT_IDENTIFIABLE |
| per-source byte COUNTS of the child | copy-op source counts + written set (BEE copied_from_own, n_window_writes; Archaeon copied_exec/nbr/computed; NPE wrote/residue via observer) | contributors NOT_IDENTIFIABLE |
| occupant / host id | the entity overwritten or supplying the body (Archaeon occupant; NPE victim old oid via observer; BEE `replaced`, NOT persisted in the traced rows) | NOT_IDENTIFIABLE |
| founder origin | init / seed / transplant / implant rule | UNKNOWN |

The adapter derives: HU continuity (majority-provenance rule), event classes (AUTONOMOUS, CAPTURE, DECOUPLED, ORIGINATION,
UNRESOLVED), tri-valued spontaneity by ancestry, and abstention counts.

**Anomaly flags** (cheap, online; each one nominates a specimen for FULL FORENSIC):
- F1 AUTONOMY_WITHOUT_OWN_EXECUTION: the child continues the executor's HU while win_steps > own_steps (BEE DECOUPLED).
- F2 PROVENANCE_RESEMBLANCE_SPLIT: the provenance majority names one source and positional resemblance names another (BEE
  AUTONOMOUS|target).
- F3 HOST_AMPLIFICATION_BURST: one HU gains births executed by many distinct other-HU executors (block-15 shape).
- F4 INSERTED_TO_SPONTANEOUS_LABEL: a lineage the engine labels spontaneous has inserted ancestry by the lens (I1).
- F5 UNRESOLVED_MAJORITY: the share of births whose majority source was not persisted exceeds a bound (instrument insufficiency).
- F6 NO_MAJORITY_RECOMBINATION: an ORIGINATION by recombination with no majority parent (PTE GA; HU ill-posed there).

Measured cost (this program):

| engine | light lens cost | engine cost per event | overhead |
|---|---|---|---|
| BEE (offline over traced logs) | 13.8 us per birth row (28.96M rows, 399 CPU-s) | ~0.75 ms per birth (25.5 s median run / ~34k births) | ~1.8% if run online |
| NPE observer subclass | measured in PERFORMANCE (out/PERFORMANCE.json) | -- | -- |
| Archaeon (native: the four identities are always on) | fast path when the birth is a plain self-copy | -- | included in the frozen engine |

## FULL FORENSIC (selected specimens, deterministic replay)

Execution-level data flow for ONE specimen: per-byte provenance (Archaeon taint VM; BEE `Trace.win_prov`, which is computed in
memory and not persisted; NPE `prov`/`prov_lit` + z8taint niche tags), interventional re-execution (NPE P-11 C5 = donor writes
blocked; Archaeon paired arms), and the canonical graph at segment or byte granularity.

Requirements: a deterministic replay from preserved inputs (all four engines have one), an observer that is shown to be
NON-PERTURBING (NPE: summary + lineage bit-identical with and without the observer; PTE: champion + curve identical; Archaeon: taint
VM result == frozen VM result, asserted per birth), and a hash-pinned code commit.

Measured cost:

| engine | full-forensic unit | cost |
|---|---|---|
| Archaeon | taint VM per birth | 141 us vs 98 us plain (1.45x per execution). In the ENVGATE-02 inflow ecology: ~12k taint calls per block = ~1.7 s of a 5,309 s block (~0.03%), because births are rare relative to executions |
| Archaeon | block-13 fossil replay to epoch 14,800 | measured in out/PERFORMANCE.json |
| BEE | traced replay of one run | median 25.5 s untraced per run (POST_CAMPAIGN_FORENSICS); traced replay adds the per-write provenance |
| NPE | H2 RESERVOIR arm replay with observer | ~150-190 s per arm on 9 concurrent workers |
| PTE | instrumented GA replay (pop 16, 6 gens, CPU) | ~58 s per evolve (116 s for observed + unobserved check) |

## Where each engine must add a field to leave NOT_IDENTIFIABLE (not required; recorded as research asks only)
- BEE: persist `replaced` (occupant id) and the per-source write counts from `win_prov` in the traced birth row. Today 33% of traced
  births are UNRESOLVED because the majority source is not persisted, and CAPTURE cannot name its donor HU.
- NPE: persist the victim's pre-rename oid in pair-tape birth events, and `wrote_bytes`/residue separately from `repro_span`.
- PTE: log GA parent indices in `evolve` (one list per generation).
