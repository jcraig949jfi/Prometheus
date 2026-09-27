# E-005 result -- horizon before area (Block C). CLOSED 2026-09-27.

Preregistration: Aether/AETH-03/PHYSICS_DESIGN_03_2026-09-27.md s1 (committed 39b7f7e85 before any run).
Execution: 8 long-horizon units (T-007..T-014), 256^2, 16 origins per twin pair, 10,000 ticks, run concurrently on one RunPod L4
host (128 vCPUs; Linux; Python 3.11.10; NumPy 1.26.3) via Aether/runpod/aether_units v3, pinned code c49f2ebad. Flight
aether-units-20260927T155823Z: FLIGHT_PASS, all artifacts sha256-verified, pod absent by LIST+GET, inventory 0. Longest unit 426 s.
Reduction: `python Aether/observatory/aeth03_longhorizon_reduce.py ops/campaigns/C-002/E-005/attempts` -> REDUCTION.json.
0 locality violations in every unit.

| arm | max radius +500 / +2,000 / +10,000 | max generation +500 / +10,000 | breached | new max gen after 2,000 | differing at +500 / +10,000 |
|---|---|---|---|---|---|
| v1 OFF | 2 / 2 / 2 | 2 / 2 | 0 | 0% | 0.81 / 0.81 |
| add OFF | 3 / 3 / 5 | 3 / 5 | 0 | 9.4% | 0.97 / 0.94 |
| rcv OFF | 7 / 7 / 7 | 8 / 13 | 0 | 3.1% | 0.69 / 0.62 |
| rcv ON | 17 / 22 / 39 | 17 / 48 | 7 of 32 | 34.4% | 0.66 / 0.40 |

Verdict by the preregistered rule (OFF arms): **locality conclusions are horizon-robust to 10,000 ticks** for v1, add and rcv.
No clause fires: no OFF region breached; the radius >= 5 share at +10,000 is 0 (v1), 0.031 (add), 0.031 (rcv), below the 0.10
floor; late new generations 0%, 9.4%, 3.1%, below 10%.

Read at its width:
- Nothing local at +500 becomes non-local by +10,000 without injected perturbation. Twenty times the horizon changed no OFF
  conclusion.
- rcv OFF's generation count climbs (8 -> 13) while its radius does not move from 7: differences flicker in place. Generation is
  not reach (the false friend already caught in ladder 2).
- add OFF shows the only late movement in any OFF arm: one origin crossed from radius 3 to 5 between +5,000 and +10,000, and 3
  of 32 origins set new generations after +2,000. Below every bar; recorded as the one slow process seen, not as a finding.
- rcv ON keeps growing, sub-ballistically (radius 22 at +1,000, 37 at +5,000; 7 of 32 regions reach 28 sites by +10,000) while
  the share of origins still differing falls to 0.40. Perturbation-driven spread is horizon-dependent; the substrate's own spread
  is not.
- Area was not needed: the largest OFF footprint (radius 7) stayed 21 sites inside the breach line.
