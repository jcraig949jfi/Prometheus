# T-CT-1  Carrier census over all C1 SIGNAL cells: which physics favours which carrier?

QUESTION
Across every C1 champion that reached SIGNAL, where does the task bit sit
at mid-interval: site state, channel content, jointly, or elsewhere? Does
the carrier class depend on physics dials (decay, loss, update mode,
latency, caps, fanout, payload width, WIMM) or on the task family?

WHY
It is the prerequisite for the C2 successor ("carrier-load mapping"). A
load boundary can only be read as a competence limit, and not as a
carrier switch, if the unloaded carrier is known. It also tests whether
C1 family labels hide carrier diversity (in 12 D-wave cells they did).

EVIDENCE POINTERS
- Instrument: prometheus/ananke/lens.py carrier_table (read
  roles/Ananke/research/instruments/INSTRUMENT_CARRIER_SWAP.md, esp. the
  failure modes F1-F6 and arm_identical).
- 12-cell pilot: roles/Ananke/research/spikes/out/s_ct.json
  (spikes/s_ct.py).
- All C1 rows: roles/Ananke/pte/c1_rows/cells.jsonl.gz (kind evolve;
  result.held.lo99 > 0.55 = SIGNAL; result.champion is the genome;
  physics and env are stored).

STEPS
1 PLAN.md: define the carrier classes from the verdict pattern BEFORE the
  census (e.g. SITE: site_all FLIP; CHANNEL: channel_all FLIP; JOINT: both
  CHANCE with joint FLIP; UNREADABLE: normal lo99 < 0.60), the probe tick
  per family, and the physics features to regress on.
2 Run carrier_table (site_all, channel_all, channel_content,
  channel_count, pay<k>, w) at one mid-interval tick per cell, 64
  worlds, plus the joint swap where both singles are CHANCE. GPU lease
  (roles/Ananke/research/lease.py). Estimate ~20 s per cell; ~150 SIGNAL
  cells -> ~1 h.
3 Tabulate class x family x physics. Fit a small, interpretable model
  (a depth-2 tree or logistic regression on 5-6 dials); report
  cross-validated accuracy against a family-only baseline.
DECISION
"Physics selects the carrier" if the physics model beats family-only by
>= 0.10 cross-validated accuracy; otherwise "family selects".
DELIVERABLES
census table (out/), PLAN, LOG, REPORT; update the backlog T-CT-1 entry.
STOP. 4 h. GPU lease required for step 2; queue it if BUSY.
