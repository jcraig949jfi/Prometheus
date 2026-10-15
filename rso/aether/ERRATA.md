# Errata to the C-018 Aether record

These are corrections to statements in the record. They change no frozen file, no evidence, no decision rule and no
verdict. RESULT.md is not rewritten: its provenance stands as committed (fa0347fd2, Argus, C-018-T050).

## E1 -- replay count of the CONFIRMED units (2026-10-15, C-019-T010; directive 2026-10-15 s1)

**Statement corrected.** RESULT.md s2 item 1 lists the six preregistered fully replayed units and says: "Of the 8 RX
CONFIRMED units only 8228 is among them." The review packet carries the same reading, and so does the operator's
review: one of the eight CONFIRMED units replayed.

**Correction.** By the C-018 closeout, **two** of the eight RX CONFIRMED units had been fully re-executed natively:

| unit | how | where recorded | evidence |
|---|---|---|---|
| RX 8228 | preregistered replay sample (first seed of shard RX.3), inside `confirm analyse` | rso/aether/runs/meta/analyse_full.out (`full_replay_verified`) | arrays_sha256 and meta tree / B / N / origin reproduced |
| RX 8201 | integrator check: a non-sampled CONFIRMED unit, re-executed natively by Palamedes at T050 integration | ops/campaigns/C-018/tasks/C-018-T050/TASK.json, INTEGRATED history note, commit **85e0cd7fb** | arrays_sha256 **567d483e33d6b847f8d33049d557ee4d5afc988f208e09c4ecc4b2d5845c5fce**, equal to the committed value (rso/aether/runs/CONFIRM/RX.0.shard.json; RX.0/native_RX_8201.json); B 13014 and N 13143 equal |

**Scope.**
- Both replays sit inside the same trust boundary: the pinned native execution path, `rso.aether.adapter.native_unit`
  calling Aether's own `law_step` and `run_unit`.
- The 8201 replay was an integrator check. It was NOT a preregistered sample, and it does not change the registered
  `full_replay_verified` count (6).
- Seven of the 64 confirmatory units have therefore been fully replayed: the 6 sampled units plus 8201.
- The other 57 are the subject of the post-confirmation audit, C-019-T020: rso/aether/audit/.
- The C-018 verdict (RX CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT; V1 ANCESTRY_UNEVALUABLE) is unchanged.
