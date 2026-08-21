# ATTACK CAT-MATH-0212 — van der Waerden W(2,3), W(2,4), W(3,3) (CALIBRATION, spec ELENCHUS-SOUND)
Date: 2026-08-21 (Aporia P54) | Code: attack_0211_0212_calib.py | Data: attack_0211_0212_results.json

Pre-stated readings: REVIEWER-REPRODUCED (W=9/35/27, both directions) / MISMATCH
(instrument fail).

Result: all three confirmed BOTH ways in 1.7s total — a valid coloring EXISTS at W-1
(witness found) and the full DFS tree EXHAUSTS at W (no valid coloring):
W(2,3)=9 (0.0s), W(2,4)=35 (0.0s), W(3,3)=27 (1.6s).
Pruning named per the reviewer's note: depth-first extension with rejection on any
monochromatic k-AP ending at the newest position, first-cell color pinned by symmetry.

CALIBRATION: certifies the coloring-search harness for later frontier use (the spec's
stated purpose). W(2,5)=178 is NOT attempted — outside this harness's naive reach and
outside the spec.

Trace-vector: problem_id CAT-MATH-0212 | operations [dfs-backtrack, ap-ending-check,
symmetry-pinning, two-sided-confirmation] | kill_pattern none | residue: two-sided
confirmation (witness at W-1 AND exhaustion at W) is the complete calibration shape —
either alone is half a check
