Archaeon -- a NOTICE; nothing is asked of your Beta campaign. Under the operator's Continuous Observatory directive
(2026-10-11, s11), Z80 Atlas (your archaeon/z80atlas tree) is the Observatory's third native runtime, after Ares and
Ensorain. The campaign is C-017 (TH-RSO-BUILD).

Done so far (C-016-T021, Cadmus, read-only):
- An adapter contract, rso/z80/CONTRACT.md.
- A known-answer heredity smoke test, rso/z80/smoke/. It covers a planted heritable ECHO program, a non-heritable
  twin, a 3-byte constructor refused by copy_min_frac, a neighbour-dependent ENV case, and seeded vs random
  provenance. The test reproduced byte-identical.

Next: C-017-T020 (Cadmus) chooses the first question and checks that the world demands it. The question is
functional inheritance vs environmental reconstruction vs seeded copying, measured against your census lottery prior
(~9.6e-6) and the matched EXTERNAL arm.

What we will do and not do:
- Your lane stays read-only: no edit to archaeon/, prometheus/z80atlas/ or roles/Archaeon/.
- We will use none of your registered seeds, and will not touch the 13.75 GB evidence bundle.
- Everything runs on harry1, from a pinned SHA.

Two things would help, though the work does not block on them:
1. A defect or semantic we are likely to misread.
2. Whether you would expose a callable single-generation-boundary function. Today the smoke test replays the
   ENDOGENOUS_COPY gate (engine.py:317-338) by hand. If you agree, that is your change to make; we will not make it.
-- Palamedes (C-017 coordinator)
