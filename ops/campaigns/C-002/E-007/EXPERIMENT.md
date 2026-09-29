# E-007 -- Known-answer lane (Block G)

Campaign: C-002. Thread: TH-007 (engineering only; no science claim can come from this lane).
Question: does the unit machinery dispatch correctly, give bit-identical results across hosts, detect duplicates and missing
units, refuse an incomplete battery, and clean up?
Units: six slices of ladder-2 runs whose results are already committed (T-001..T-006, known_tasks.json). The expected result is
the historical record: legacy_sha256 computed FROM the committed evidence file by aeth03_lane_reduce.py expected.
Reducer: aeth03_lane_reduce.py reduce --tasks known_tasks.json --results attempts/.
