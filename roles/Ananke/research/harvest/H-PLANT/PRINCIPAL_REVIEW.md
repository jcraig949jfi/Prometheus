# H-PLANT principal review (Ananke, 2026-10-01 ~00:40Z)

Worker report: REPORT.md (deposited verbatim, provenance REPORT.provenance.json). Plan 01234c0ad, frozen
before any run. Lease skullport:cpu8 lse-8fce73fc75f6 held for the run and then released.

## Independent re-check (principal, CPU only, 2 threads, 387 CPU-s)
The worker's plants were re-scored at d9cc on a fresh principal namespace (assays.world_seeds(0x414E4B50
"ANKP", 256)), so the scoring worlds are disjoint from the worker's HPLT namespace:
| plant | worker (HPLT) | principal (ANKP) | gated must-fail (ANKP) |
|---|---|---|---|
| P-FLIP @ d9cc, C1 cell 6f82f9c7 | .978 [.962, .990] | .973 [.953, .988] | teacher zeroed .500 |
| P-MULTIHOP @ d9cc, d5 | .984 [.969, .995] | .967 [.944, .984] | relay off .500 |
Both replicate.

## Corrections to the report's H6 implications (from the C1 rows)
1. **FLIP: stands.** 6f82f9c7 is a real `evolve` cell at d9cc (FLIP d3): held .479 [.436, .523], and its
   final generation reached max acc .578 with max_contrast .25. A 16-line program in the same genome
   space scores about .97. That is first direct evidence that this FLIP NULL is search-limited, not
   physics-limited. It covers one cell (plus ef77ef2e per the worker, which I did not re-check), not
   FLIP in general.
2. **MULTIHOP: QUALIFIED.** fac4aaa23a0bdcb2 is kind `transfer`, not `evolve`: the RELAY d3 champion
   bbef66a1 was evaluated at d5, and no search ran. Across all C1 rows there are ZERO RELAY multi-hop
   `evolve` cells at d9cc (1 transfer; 9 multi-hop evolve cells exist only at other physics). So "C1
   search failed multi-hop at d9cc" was never measured. What H-PLANT shows is that physics allows
   multi-hop at d9cc and that the one-hop champion does not transfer. H6 for multi-hop remains UNTESTED
   at d9cc.
3. **XOR: as the worker says.** XOR is plant-reachable at a C1 census point (aa2b8d68, strict
   no-override, lo99 .636; that strict scoring was added post-screen, addendum A6). At d9cc, where C1
   searched XOR, the light-cone bound caps any program at .574. So H6 is FALSE for d9cc XOR: physics
   plus actuator placement bind there.

## New instrument finding to carry forward (worker Disagreement 4)
A one-flag readout ("+ iff no + cue") scores .763 on XOR at X0, because the mirror negates only x1. C1's
XOR SIGNAL rule (lo99 > .55) can therefore pass without computing XOR. XOR SIGNAL claims need a
one-flag-readout control. No C1 XOR row held lo99 > .55 (lc_census), so no existing claim is affected
yet.

## Plan deviations
The one-hop XOR design was impossible under envs.build's actuator placement (worker A1): the plant became
a flood plus a clock. A4 (multi-hop d=5) and A6 (post-screen strict scoring) are disclosed in
PLAN_ADDENDUM.md.

## Correction (2026-10-01, Wave 2; flagged by W2-I kind_audit, and W2-G F4 / W2-D F1)
Item 1 above says the FLIP evidence "covers one cell (plus ef77ef2e per the worker, which I did not
re-check)". ef77ef2e0a1026c2 is a TRANSFER (RELAY champion bbef66a1 evaluated on FLIP), not a search.
1b26026fc846d03d (cited in REPORT L29 as an XOR cell "where C1 searched") is also a transfer.
- d9cc has exactly ONE FLIP search (6f82f9c7) and ONE XOR search (d64656f2).
- The FLIP search-limitation evidence rests on n = 1 search seed.
- The worker's REPORT is a verbatim deposit and is not edited; this correction governs.
