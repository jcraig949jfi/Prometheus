# Worker L: is a retention regime REACHABLE when the task rewards it?

ID W-L. Output workers/W-L/. Namespace 0x5F2 (0x5F3 for held-out). Read
COMMON_RULES.md and COMMON_RULES_ARC3.md first. Budget ~4 h. CPU for
building and validating; the GPU (lease) for searches; queue if busy.

QUESTION
Current PTE champions were evolved on tasks that never reward keeping a
cue beyond its own query, and none of them does. Hand-built plants show
that the substrate CAN retain and use a cue across trials. When the task
DOES reward it (e.g. answer at trial k+n with cue k: an n-back task, with
n = 1 or 2), does the declared outer search (C1 SearchSpec) reach a
retention mechanism? If so, WHAT carrier does it use (site state, Kp/WIMM,
routing w, channel recirculation)? If not, is that a search-reachability
failure (plants solve it at the same physics and program length) or a
physics limit?

EVIDENCE (raw)
- Retention census code and hand-plant controls: workers/W-G/ (wg.py,
  controls C-EFF, C-AVL: an S integrator and a Kp/WIMM latent store) and
  workers/W-E/.
- Engine and environment construction: prometheus/ananke/envs.py (HOLD
  episode building: schedule sense_val, ro_tick, y), engine.py; search:
  prometheus/ananke/search.py (evolve, SearchSpec). Do NOT edit envs.py.
  Build the n-back episodes in your directory (an envs.Episode object with
  your own schedule and targets; mirror pairs negate the whole cue
  sequence).
- Carrier instruments: prometheus/ananke/lens.py (carrier_table, swaps);
  instruments/*.md.
- M2 physics and specimen: c1b_run.load("4ab2ba014aac967e").
REQUIRED
- PLAN.md frozen before any search: the task definition (check that the
  lag-n target is independent of the current cue; the sequential-exploit
  test), the plant solvability checks (at least one hand plant must solve
  the task at the chosen physics and program length, otherwise the search
  question is ill-posed), arms (n = 1, n = 2; 4+ seeds each), success
  criterion (held-out lo99 > .60 and above a no-memory baseline), and how
  you will identify the carrier.
- A search that fails is a result, provided the plant control shows the
  task is solvable.
DELIVERABLE: the report in your final message; DISAGREEMENTS.
STOP: 4 h, or when the arms are done.
