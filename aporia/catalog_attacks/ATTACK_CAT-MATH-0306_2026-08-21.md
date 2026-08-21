# ATTACK CAT-MATH-0306 — odd perfect numbers to 1e8 (CALIBRATION, spec ELENCHUS-SOUND)
Date: 2026-08-21 (Aporia P59) | Code: attack_0293_0306.py | Data: attack_0293_0306_results.json

Pre-stated readings: NO-ODD-PERFECT + CONTROL-FIRES (all five even perfects <= 1e8) /
anything else = instrument fail.

Result: full-range sigma sieve to 1e8 (the reviewer verified the harness at 1e7 and
flagged 1e8 feasibility — executed here: 60s, 400MB int32). Perfects found:
EXACTLY [6, 28, 496, 8128, 33550336] — the even-perfect positive control fires
completely; odd perfects: NONE. Per the P58 measured-or-unmeasured rule, the int32
overflow negligibility claim carries its measurement: max s(n) = 388,251,360 = 18.08%
of 2^31.

CALIBRATION: the literature bound is 10^1500 (Ochem-Rao); this certifies the sigma
harness (shared with the 0316 amicable attack) and adds a second calibration point.

Trace-vector: problem_id CAT-MATH-0306 | operations [sigma-sieve-full-range,
positive-control-set-match, measured-negligibility] | kill_pattern none |
residue: positive controls as SETS (all five members) beat single-point controls —
a partial control catch would localize a sieve boundary bug immediately
