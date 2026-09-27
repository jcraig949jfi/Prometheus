# E-001 -- B6: Who / Where / What  [CLOSED 2026-09-27 -- see RESULT.md]

Campaign C-001, Thread TH-001.

Question: when reproduction occurs, can we distinguish the executing entity, the execution location, the code material, and the
material governing the inherited writes?

Why it is the most urgent integrity question: Contract v0.2 found that BEE's "own code" (pc < L) measures LOCATION. In r038751,
27,083 of the 28,163 births that location calls foreign-governed were governed by the writer's OWN material, running from a copy of
itself in the window. NPE's prov records the executing CONTEXT. Only Archaeon's taint VM records code MATERIAL. Readings built on
location or context may be misattributing authorship (V02_REGRESSION_REPORT.md s5).

Starting evidence:
- archaeon/causal_lens/out_v02/B6_PROBE_r038751.json and B6_PROBE_r016299.json
- archaeon/causal_lens/tools_bee/codeprov_replay.py
- Bellerophon's traced VM (origin/bellerophon/coupling-campaign-2026-09-24, roles/Bellerophon/forensics_2026-09-23/tools/)
