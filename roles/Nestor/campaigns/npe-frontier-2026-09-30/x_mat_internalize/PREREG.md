# X-MAT-INTERNALIZE: preregistration

- **Seat:** Nestor.
- **Order:** CWO 2026-09-30 NEXT, the NPE frontier. The task is to discriminate endogenous reproductive organization from seeded, transplanted or bookkeeping artifacts.
- **Frozen:** at the commit that adds this file. No tag readout exists before that commit.
- **Instrument:** `run_xmi.py` and `dense_taint.py` in this directory, both at that same commit. Neither may change after exposure.

## Question

C-A3-INTERNALIZE was CONFIRMED with 8 events in 144 fresh runs. It found lineages, founded only by donors that are not state-free, that come to carry state-free competent genomes.

Its lineage L is a label:
- L starts as D0.
- L then adds every accepted pair-tape replication whose writer is in L.
- A member that is overwritten by a non-L source leaves L.

A writer on the pair tape can copy bytes it read from a non-L partner. The child is still in L. So the confirmed result has two readings:

- **Endogenous:** the state-free genomes are built from founder material and from values that L organisms computed.
- **Bookkeeping or transplant:** the label runs through L, but the bytes came from organisms outside L.

This experiment decides between the two readings with material tags. It does not re-test the recurrence claim. That claim is closed, and no compute is spent reproducing it.

## Ruler

The ruler is z8taint material tags on the dense VM, from `dense_taint.dense_z8taint()`.

Instrument check (committed with this file, before any exposure): selftest E1–E3 PASS on 600 alias-rich programs.
- **E1:** dense taint matches `dense_z8.run` bit for bit, 0 mismatches.
- **E2:** as a non-vacuity control, plain taint differs on 551 of the 600 programs.
- **E3:** plain taint matches plain z8, 0 mismatches.

Tag classes (copies keep their source tag):

| Tag | Value | Meaning |
|---|---|---|
| D0 | 250 | Every genome byte and register of every D0 organism, set at the D0 epoch |
| PRE | 251 | The same for every other organism alive at the D0 epoch |
| MKL | 252 | A value computed after D0 by an organism in L at that moment |
| MKN | 253 | A value computed after D0 by an organism outside L |
| MUT | 249 | A byte made by the world's mutation step after D0. Neutral, because the maker class is unknown |
| OTHER | < 249, or 255 | Placed after D0, or UNKNOWN tape padding |

ENDO = D0 + MKL. XENO = PRE + MKN.

## Sample

The sample is every C-A3-INTERNALIZE run that `run_ci.event()` classifies:
- **EVENT runs (8):**
  - 7ae3: 27000023;
  - ffa6: 27000012, 27000020, 27000024, 27000046, 27000048, 27000051, 27000052.
- **REPLACEMENT runs (18):** a descriptive comparison group only.

Each run is a replay with the same seed, cell, world, dense VM, ATOMIC runner and L bookkeeping as `run_ci._run`, with tracking switched on.

## Replay gate (INVALID condition)

Each replay's full record must equal the committed `c_a3_internalize/results/<cell>_<seed>.json` exactly. The record covers depth, D0 epoch, D0 state-freeness and every checkpoint. Any mismatch makes the whole verdict INVALID.

## Endpoint

The endpoint is read at the checkpoint that `event()` reads, the last checkpoint with a state-free competent genome. It is computed for the organisms that are in L and carry a state-free competent genome (`free_L`).

- **X** = XENO / (ENDO + XENO), over their genome bytes.
- **attributed_share** = (ENDO + XENO) / bytes.

Per-run class:
- **UNRESOLVED** if attributed_share < 0.3, meaning the bytes are mostly mutation-made or OTHER.
- Otherwise **ENDOGENOUS_MATERIAL** if X ≤ 0.2, **TRANSPLANTED** if X ≥ 0.5, and **MIXED** in between.

Verdict over the 8 EVENT runs:
- **ENDOGENOUS** if at least 6 are ENDOGENOUS_MATERIAL. Internalization is material, not bookkeeping.
- **BOOKKEEPING** if at least 4 are TRANSPLANTED. The confirmed internalization is a label artifact in at least half the events.
- **MIXED** otherwise.
- **INVALID** on any replay mismatch, or if the EVENT count is not 8.

Both named verdicts need a positive threshold. A weak or empty readout gives MIXED or UNRESOLVED, never support.

## Scope and limits, declared now

- MUT bytes carry no maker class. A byte mutated inside a non-L organism and later copied into L counts as neutral, not XENO. X is therefore read over attributed bytes only, and MUT_share is reported beside it.
- The endpoint covers whole genomes. It is not restricted to register-setting bytes, because this ruler cannot identify them.
- Register tags are set at D0. Register-to-memory writes carry register tags as z8taint defines them.
- MKL/MKN use L membership at execution time, and L is the same label under audit. That is intended: the question is whether the label's members made the bytes.
- The REPLACEMENT runs and `free_nonL` are descriptive and never decisive.

## Compute

- The replays total 26 runs of 2000 epochs each.
- They run locally with a pool of 8, within MWO-0004 R2: at most 16 CPU core-hours for the item.
- One single-core pilot, run 7ae3 27000023, measures time and checks the replay gate before launch. It prints no endpoint, and its result file is deleted.
- If the pilot projects more than 16 core-hours, the sample is not cut after the fact. The launch waits for a lease and a budget note instead.
