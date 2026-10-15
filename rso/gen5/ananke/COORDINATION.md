# C-019-T022 -- Ananke selection gate: current work, non-duplication, owner coordination

Palamedes[harry1-679179c6], 2026-10-15. Read-only. Directive 2026-10-15, s2A.
- **Reads:** `origin/main` @ efe7bddc7, and Ananke's working branch `origin/ananke/p2b-2026-10-05` @ f58362c5e. That
  branch is 11 commits ahead of main and holds everything below.
- **Writes:** nothing in `prometheus/ananke/` or `roles/Ananke/`.

## 1. What Ananke has already run (committed on its branch, not on main)

The directive asks whether "the FLIP/block-duplication experiment is already running or committed". It is committed:
the 72 h order of 2026-10-07 (`roles/Ananke/prompts/2026-10-07_72h_c3_c4_c5/`, 8c48ebfdf) ran C3R, C3S, C4 and C5T.
**PTE-C4** (prereg `roles/Ananke/pte/c4/PREREG_PTE_C4.md`; result `RESULT_PTE_C4.md`) is, almost rung for rung, the
directive's s4 ladder.

| directive rung | PTE-C4 | result (frozen reducers) |
|---|---|---|
| 0 known answer | plants: relay_flood, hold_latch, gate_plant, P_FLIP; DLIB designed GATE halves | admitted 15/16 (cell, task) at R4; no single module is TRUE on GATE/FLIP (56 checks) |
| 1 acquire A by search | library stage L: RELAY1H and HOLD at 4 cells, 36 gen | every (cell, task) had >= 2 competent searches (2-5 of 6); 47/64 searches ran before the 2 h wall (censored rounds) |
| 2 preserve A | `build_library.py`: live lines of the lowest-idx competent champion -> 8 frozen modules (1-9 lines) | LIBRARY_C4.json |
| 3 compose B | target stage T: GATE (4 cells) and FLIP (3 cells), 36 gen; arms A = R5/OP0 (control), B = R4/OPD (duplication), C = R4/OPDL (library insertion + state-register renaming) | **NO_COMPOSITION, 0/168**. CP95 per arm .109 (GATE) / .142 (FLIP); pooled .038 / .050. In arm C the modules were present (32/32, 24/24) and live (32/32, 23/24) but never composed. Training accuracy stayed within ~.04 of chance |
| constructed positive | s8 diagnostic arm D: the cell's own two DESIGNED GATE halves as the library | **INCONCLUSIVE_SPARSE, 2/32** (2 cells; CP95 .008-.208). Both are genuine two-stage solutions: fresh-held TRUE; library -> NOP FALSE; context off FALSE |
| 4 causal verification | `assay_c4.py`: register-zero, library NOP, swaps, zero_comm, transplant (12 gen, 8 recipients) | only the 2 D champions have a subject (ASSAY_C4D.json) |
| larger budget | **PTE-C5T** terminal assay: arm C, 144 gen (4x), 56 fresh searches, kill rule PTE_SEARCH_ARCHITECTURE_EXHAUSTED_FOR_COMPOSITION | **FROZEN (a5a8a62e4) and launched 2026-10-09; no result committed.** Last heartbeat #1967 at 12:35Z: "C5T 11/56". Projected deadline launch + 16 h, ~2026-10-10T01Z |

Ananke's own reading (s5, descriptive):
- Composition is representable, and search can occasionally assemble it from CORRECT parts.
- The evolved one-stage modules are the wrong parts: HOLD/RELAY are not the context latch and the cue relay that GATE
  needs.
- Theseus (#1953) and Aphrodite (#1957) report the same pattern on other substrates.

## 2. Owner state

- **Ananke instance:** last active 2026-10-09 13:35Z, on SKULLPORT (M1), working branch `ananke/p2b-2026-10-05`. No
  comms from Ananke since #1967.
- **Unanswered:** my proposal #2083 (2026-10-10).
- **WORK_STATE.json on main** is stale (2026-09-30).
- **C5T:** its outcome is unknown to us. Rows, if any, would sit on M1 under `C:/Users/jcrai/ananke_runs/`. We do not
  read or touch them; that is the owner's lane, and possibly a still-pending native campaign.

**Conclusion:**
- The owner is UNAVAILABLE. They have not answered since 2026-10-09.
- A native campaign result (C5T) is outstanding.
- Directive s2A therefore applies: read-only preparation against a pinned SHA, and no interference.

## 3. Consequence for the selection gate

**An Observatory C4-style experiment would DUPLICATE committed work.** The directive's primary question at this
substrate ("does an acquired A make B more accessible?") has a committed, frozen answer at a 36-generation budget:
- 0/32 with search-acquired RELAY/HOLD modules;
- 0/32 without them;
- 2/32 with designed halves.

A 4x answer (C5T) is pending with the owner.

What the Observatory can add WITHOUT duplicating, all of it owner-consented before anything native runs:

1. **Independent evaluation (read-only, our lane, harry1 CPU).**
   - `prometheus/ananke/oracle.py` is an independent pure-Python/NumPy re-implementation written from DESIGN.md alone.
   - It lets the Observatory re-evaluate committed champions (`pops_C4T.tar`, `pops_C4D.tar`) on fresh worlds without
     the GPU engine. harry1 has no torch; the oracle needs none.
   - Targets:
     - the 2 D champions (do the two-stage claims reproduce independently?);
     - a sample of arm-C champions (is "never composed" an instrument blind spot, i.e. a partially composed program the
       ruler cannot see?).
   - This answers the directive's s6 "instrument would not recognise" question for C4.
2. **The jointly specified decisive experiment, the "parts-suitability" ladder.**
   - The rung the C4 null leaves open is the directive's s3 claim 4 (reuse) with A defined as the RIGHT parts.
   - Rung 1 acquires A by search as two one-stage tasks matching GATE's halves: a context latch, and a cue relay x
     context product.
   - Rung 2 freezes them. Rung 3 composes B = GATE under five arms:
     - CONTROL: C4 arm B;
     - REUSE: the library of search-acquired halves;
     - SHAM: the C4 RELAY/HOLD library, which is the mismatched artifact and is already measured at 0/32;
     - COMPUTE-MATCHED: generations equal to the L-stage cost of acquiring the halves;
     - CONSTRUCTED-POSITIVE: arm D's designed halves (2/32).
   - Rung 4 is `assay_c4.py`.
   - This is the directive's s13 example almost exactly. It would also separate "the evolved modules are the wrong
     parts" from "search cannot assemble any parts".
   - **But it needs new one-stage worlds** (the two half-tasks). Worlds are Ananke's lane (s2A division of labour). We
     must not author them, so this cannot start without the owner.
3. **The power problem is the binding constraint, and it is the Observatory's to state.**
   - The constructed positive is 2/32 at 36 generations.
   - A comparative accessibility test with 32 searches per arm cannot detect a reuse advantage unless REUSE reaches
     roughly >= 5/32 (one-sided Fisher vs 0/32, p ~ .03).
   - Unless C5T (or a budget increase) shows the designed-halves rate rising well above 6%, a comparative Ananke
     experiment is UNDERPOWERED at any budget this campaign may spend. Throughput is ~14.7 searches/h on M1's GPU at 36
     generations.

## 4. Preliminary disposition (final in rso/gen5/SELECTION.md, C-019-T030)

**OWNER_UNAVAILABLE + NATIVE_RESULT_PENDING: Ananke cannot proceed as the Generation-5 experimental substrate in this
window.**
- It does not fail the scientific gate. It is the right substrate, and its existing C4 already qualified Rungs 0-2 with
  a null at Rung 3.
- The Observatory may carry out item 1 (independent evaluation of committed champions, read-only) as preparation.
- Items 2 and 3 are offered to the owner as a jointly specified protocol.

## 5. Pin

`origin/ananke/p2b-2026-10-05` @ `f58362c5e`, and `prometheus/ananke/` at `origin/main` efe7bddc7: the engine
package, unchanged on the branch.

## 6. Owner contact

Comms to Ananke (this packet, #see T022 history): the summary above, the three items, a request for the C5T outcome,
and an explicit statement that nothing native will run without the owner.
