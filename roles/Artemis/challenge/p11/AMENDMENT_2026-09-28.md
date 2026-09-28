# AMENDMENT 2026-09-28 to PREREG_P11.md (@d5241a102) -- written BEFORE any phase-2 run

No specimen, gate, certificate, threshold or stop rule (D1, D2, D3, A0) is changed. This file only fixes
implementation details that PREREG_P11.md left open, so that they are not chosen after seeing results.

1. Copy-mutation rate for P-11 on constructed specimens. The constructed cells have no mutation_rate factor. P-11
   (and FERT, which calls P-11) runs at the LOW rate 0.002 (world.py:40 @d7641744d) for every constructed specimen,
   z8 and toy alike. Certificates CVT-1/2/R and LOCAL run at 0 as preregistered. Natural donors use their own cell
   rate for P-11.
2. P-11 "observed event" for a constructed pair specimen: donor = specimen at its stated side (side 0 unless stated;
   Z3 and Z3b side 0 primary, side 1 as the preregistered sensitivity), other half = 32/64/96 bytes from
   sha256("OBS", specimen id). P0 is read on that one event (no world mutation). Assay: p11.assay unchanged with
   seed = ("P11-PANEL", specimen id, j), j = 0..19. CERTIFY iff P0 and pass rate >= 0.5.
   TV-5b: P-11 verdict = CERTIFY iff either member, run as a lone donor in the ordinary two-half tape against the
   observed random half, certifies. Z5a: the observed event is (host half 0, guest half 1); P0 and the assay are
   evaluated with each half as victim; CERTIFY iff either passes.
3. FERT: the three children are the victim halves of draws k = 0, 1, 2 of assay seed j = 0 (regenerated exactly as
   p11.assay generates them: victim from event_seed(seed, "victim", k), copy RNG from event_seed(seed, "copy", k)).
   Each child is re-assayed as donor (same side, seed ("FERT", specimen id, k)). FERT accepts iff P-11 CERTIFIES and
   >= 2 of the 3 children pass the assay. Z3n (outside P-11 scope): FERT analogue = NPE REPL rule holds at generation
   1 AND generation 2 in the host harness.
4. H-HOST layout (Z3n): arena 256 bytes (_pow2(4 x 64)); parent at 0, length 64; the single child slot is
   [128, 256) (slot_size = 2 x 64 as world.py SLOT_FACTOR); its pre-image is sha256 draw bytes; on_alloc always
   returns 128 and sets the FREE window; on_birth records mem[128:192]; slices of 220 instructions (tier S) with pc
   and registers carried (pc reset to 0 on HALT) until the first BIRTH or 10 slices.
5. SHUF diagnostic fidelity = mean fid_final over all P-11 assay draws of the specimen (Z3n: REPL fidelity; specimens
   P-11 never assays because P0 failed: the observed-event victim fidelity). Shuffles: 200, seeded by specimen id.
6. Natural cell parameters are computed from the committed cell by the world.py rules and cross-checked against
   world.Runner(cell, 1, tier=tier) (L, _ops_mask(), t["slice"], copy_mut) from the archived d7641744d tree.
7. Mechanism audit (s4.2 item 4): one fresh-state draw (victim = sha256 bytes) with a write-logging tape; reported:
   donor steps, donor writes into the victim half, distinct values written, steps per victim cell written.
8. Workers: 2 processes (coordinator instruction; host shared with other jobs). Scripts run with python3 -B from the
   scratch directory; no bytecode is written into the worktree.
9. E0 scope: substrate z8 vs verify z8 -- full P-11 records and all CVT descendants, every constructed z8 specimen.
   aa5833488 z8 (no provenance support) -- a provenance-free copy of p11.interact on each constructed pair
   specimen's observed event and generation-1 baseline draws, tapes compared byte for byte with the other two.
   E1: the full constructed-panel record is computed twice with the substrate z8 and compared.
