# OPERATOR SCIENCE ORDER: Beta-01 TEST-9 (received 2026-10-05 ~10:58Z, in session)

**Source:** the operator (James), as a direct science order to the Aphrodite seat on M4/HARRY1, CPU only.
**Status:** this is a binding summary. The verbatim text is in session transcript 0f14ab93.

## Binding points
- **Continue from durable state.**
  - No reboot, no T51 rerun, no apparatus rebuild.
  - Do not wait for Aporia.
- **Run T09 exactly as frozen** (`beta01/windows/T09_SUBSET_SPEC.md`; `engine/v2b/t09_subset.py`):
  - arms: g0, g10, ORACLE10 (diagnostic), NULL10 (gate);
  - fresh breadth-12 validation;
  - TAU 1000.
- **Nothing changes during execution:** TAU, breadth, families, seeds, endpoint, the rule, the gate, the threshold,
  the genomes, the horizon, escrow. There is no "g10b" in TEST-9.
- **Honor the compute hold** (until 12:45Z). Before launch, only lightweight readiness checks are allowed. No pilot.
- **HARRY1 limits:**
  - at most 4 workers;
  - BLAS/OpenMP threads limited to 1;
  - drop to 3 workers on thermal or memory pressure.
- **Gate:** NULL10 fails -> MEASUREMENT_FAILED. No TAU rescue, no seed removal, no new null.
- **Primary readout:**
  - R7_SUBSET_POSITIVE = (sign p < 0.05) AND (total g10 > total g0), from the paired fresh comparison;
  - secondary: rescued validation-limited seeds, ORACLE10 acceptance, seed 12 as a mechanistic boundary;
  - reading if positive: "first observable R7, tier 2". Not R8, not RSI.
- **The report answers the 11 questions in s22 of the order.**
- **Close TEST-9 in full:** report, evidence, STATE, thread, commit/push/merge, comms.
- **Open DEV-10 once, starting from the actual result.**
  - It localises the first broken rung:
    - positive: cheapest discriminator toward transfer / R8;
    - negative: one discriminating T10 (candidacy / validation content / criterion / transfer mismatch);
    - gate failed: smallest causal repair.
  - T10 may run today if it is frozen and pre-registered first, a known-answer control passes, and it fits budget and
    the thermal envelope.
- **Boundaries still in force:** no Campaign-1 live models, no W5P, no GPU, no RSI claims, no relabelling.
- **Comms milestones:** READY / LAUNCHED / (technical failure) / COMPLETE / DEV-10 opened / T10 freeze+launch. No idle
  heartbeats.

## Readiness check (2026-10-05T11:00Z)
- **Frozen files unchanged:**
  - gtc.py sha256 e097e1d4... OK;
  - t09_subset.py d48b8dbf... OK.
- **Prior evidence present:** T07 R7E_WALKS / INDEX / RESULT; T08 T08_WALKS / ROLES.
- **No T09 outputs exist yet** (clean start).
- **Imports and supply:** imports OK; roles_fresh gives 15 seeds x 8/8 fresh extras.
- **HARRY1 resources:**
  - 8 logical CPUs;
  - 20.6 / 31.9 GB RAM free;
  - 715 GB disk free;
  - no python processes running.
