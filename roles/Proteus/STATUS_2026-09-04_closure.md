# Proteus status — 2026-09-04, player/primitive closure pass

Machine: **M2 / SPECTREX5 (192.168.1.191)**, repo `D:\Prometheus`. The seat ran on M2 for the
first time; M1's Claude budget was exhausted, and the fleet's services were moved/verified here
earlier the same day (see `MAINTENANCE_RECORD_2026-09-04.md` for the infrastructure half of the
day, which is a different piece of work with a different owner).

Commits: **`6be6103f1`** (code, contracts, rows) and **`6ca171129`** (closure packet).
Both verified reachable from `origin/main` with `git merge-base --is-ancestor`.

Open work: **`TODO.md`**.

---

## What was asked

Close the remaining player-side cleanup so Harmonia knows exactly what specimens and compositions
she may place into the repaired arena: specimen identity, registry identity, primitive identity,
composition identity, exact ablation, an R≈0.000001 retention policy, a raw measurement surface,
an A/B/A+B readiness matrix, and the two handoff contracts. Explicitly **not** to run the science.

## What was delivered

`PROTEUS_CLOSURE_PACKET_2026-09-04.txt` — 16 sections, pure ASCII, 828 lines.

New: `proteus/compose/` (segment/composition identity, exact ablation, golden vectors, two
measurement studies), `proteus/integration/specimen_gate.py`, three measurement scripts,
two contracts, five result files under `proteus/v0_7/`.

Tests **106 → 146**. Both new gates were verified able to **fail**, not merely to pass.

## The result that matters most

**The experimental object is exact; the instrument is not.**

A, B and A+B construct, hash, reconstruct, ablate exactly and report activation — 200/200 on every
one of those. But A+B differed from **both** parents in **0 of 200 pairs**, and the cause is the
observable, not composition:

| population | transcript classes | largest share | emitting ≥1 value |
|---|---|---|---|
| 2-instruction segment players (n=56) | 3 | 87.5% | 4 / 56 |
| full committed specimens (n=64) | 12 | 60.9% | 10 / 64 |

The meter vector on the same 56 players resolves **37 classes at 10.7%** — roughly 13× richer.
So the 0/200 is an instrument reading. The closure packet names "composition adds nothing" as the
single most promotable-looking and most wrong constraint candidate in it (X1), precisely because it
would fossilise a measurement artifact as a fact about the substrate.

## Second result: `organism_id` pins bytes, not execution

`organism_id` hashes the manifest only, and the manifest carries neither `runtime_hash` nor
`affordance_hash` — while the runtime decodes every instruction as `op = word mod N_OPCODES`.
Probing the smallest possible table amendment (25 → 26 opcodes): **961/1013 instructions (94.87%)
re-decode, median organism 100%, with `organism_id` unchanged.** `entry_id` does pin execution.
The replayable identity is therefore the triple `(organism_id, runtime_hash, affordance_hash)`.

## Design decisions worth remembering

- **Ablation is NOP-substitution, never deletion.** Deleting shifts every later component's tape
  address, and LD/ST address the tape by register contents. Substitution preserves length, offsets,
  envelope and every other component's words byte for byte.
- **The NOP-alias differential** exists because the genome is copied into the tape, so an opcode
  word is also a datum. `w mod 25 == 0` decodes to NOP, so ablating to 0/25/50 gives three
  instruction-identical, data-distinct operations; disagreement means the ablation moved a data
  channel. 342/343 class knockouts clean, 1 confounded. The certificate is a **lower bound**.
- **`proteus/compose/` sits outside `proteus/foundry/` deliberately.** The audit stamp still reads
  FRESH on its **original** tree digest `3ae4ee8b773e0fcf`, `runtime_hash` is unchanged, and
  `run_determinism_check` still reproduces the committed registry byte for byte. No frozen
  specimen's interpretation identity moved.
- **Activation is a differential, not instrumentation**, for the same reason: instrumenting `vm.py`
  would change `runtime_hash` and invalidate Harmonia's existing fossils.

## Defect found and deliberately not fixed

`affordances.py`'s docstring says the `LDC` immediate is operand `c`; `vm.py` reads it from slot
`b`. The TABLE row is right, the prose is wrong. It cost one wrong test before it was traced. Not
fixable in place — `runtime_hash` covers the whole file, docstring included. Recorded in the
contract, in `test_composition.py`, and as **T9** in `TODO.md`.

## Boundary note

This pass modified `SerendipityFoundry/` and `evidence_wiki/` earlier in the day under an operator
directive, which departs from `RESPONSIBILITIES.md` §3. That is logged in `READ_LEDGER.md` rather
than left implicit. James subsequently ruled that **PEW is Mnemosyne's**; this seat stood down from
it. The player-side work in this document is squarely inside the seat's mandate.

## What this pass did not do

No specimen was selected, scored, ranked or interpreted. No phenotype was read or written. No
campaign was launched. Nothing was called a reasoning primitive; a structural primitive is not one,
and 85% of components that ACTIVATED had no marginal effect on the transcript at all.
