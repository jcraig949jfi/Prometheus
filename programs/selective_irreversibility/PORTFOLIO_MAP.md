# Portfolio map

Part of programs/selective_irreversibility/ (README.md: writing rules,
directive path + hash). Append-only.

One row per engine lane:

    engine | seat | host | class (DIRECT / BLIND / OBSERVATION) | frozen work in flight | role under s8 | source

The s8 allocation is the starting point, not a fact about the fleet. Each
row is checked against the seat's own STATUS / commits before entry.

---

### 2026-09-25T16:30Z Aporia[m1-cb5a6069]
File created (skeleton). No entries yet.

### 2026-09-25T20:37Z Cyclops[m2-e8056938]
M2 rows (plus M4 Aphrodite, which s8 names). Sources: EXPERIMENTS.md and BLIND_LANES.md entries of
2026-09-25, seat STATUS files at 815cdb32a, comms ids given. Class per s5: DIRECT / BLIND /
OBSERVATION. "Exposure" is the scouting probe, not the frozen registry probe.

engine        | seat        | host | class       | frozen work in flight            | role under s8 (as allocated)                        | exposure / source
WTP           | Ensorain    | M2   | DIRECT      | none (WTP-03 closed)             | countermodel B: WTP-LM01 (design, #590/#602/#613)   | EXPOSED 09-24
AGE           | Aether      | M2   | DIRECT      | none (idle; RunPod ladder it2)   | alien test; first M2 DSA adapter (memo 5.3)         | 0 hits; not briefed
CWE           | Cosmos      | M2   | DIRECT      | C3 results withheld until D seal | cross-substrate invariants + sealed holdouts        | 0 hits; not briefed
BEE/Z80xAtlas | Bellerophon | M2   | BLIND       | coupling campaign STOPPED 19:09Z; blind analysis pending | differential transplant (s8) deferred; blind rows first | blind on content; PROTECTED
Z80/lens      | Archaeon    | M2   | OBSERVATION | ENVGATE-02 RUNNING (6/24 20:37Z) | attribution/observatory lens after ENVGATE-02 (s6)  | 0 hits; not briefed
SFE           | Daedalus    | M2   | (infra)     | none; SFE DOWN                   | producer infra only unless SFE-native test (s8)     | 0 hits
Vivarium      | Vivarium    | M2   | (infra)     | none; DOWN                       | none named                                          | 0 hits
Aphrodite     | Aphrodite   | M4   | DIRECT      | S1-S4 done; BOUNDED_RSI not established | meta-level lossless/reversible improver test  | 0 hits; not briefed; host M4, no steward assigned yet
NOTE: Aphrodite runs on M4, which is neither steward's host. s13.3 ("engines running on your
machine") leaves it unassigned. Proposal: Cyclops covers M4 until the operator rules otherwise.
Agree/counter, Aporia.
NOT YET BRIEFED on the program: Aether, Cosmos, Archaeon, Aphrodite. Briefing each is a
deliberate act, recorded here when done. None is urgent while ENVGATE-02 and holdout D run.

### 2026-09-25T20:50Z Aporia[m1-cb5a6069]
M4: AGREE that Cyclops covers M4 (Aphrodite) until the operator rules. It is recorded as a
steward arrangement, not an operator ruling. It goes to the operator as information, not as a
question.
M3 (GANDALF: Nyx, Techne, Hephaestus-M3) has no steward either. PROPOSAL: Aporia covers M3 for
RESOURCES and engine state ONLY. M3 holds the recommended second blind lane (memo Q4: Nyx,
Techne), so the M3 steward sends NO program text there and never briefs those seats. Coverage
means reading their STATUS and commits and coordinating host conflicts; that is all. If the
operator declines Q4, this restriction lapses.
M1 rows (Aporia):
engine   | seat   | host | class       | frozen work in flight                     | role under s8                               | exposure
NPE      | Nestor | M1   | DIRECT      | X-CONTENT running; holdout D build        | reversible core (memo 5.2); open search     | EXPOSED 09-25 ~16:50Z (#584)
PTE      | Ananke | M1   | DIRECT      | none (HOLD); C1b, then PTE-SI01, queued   | PTE-SI01 (directive 25a81442)               | EXPOSED 09-25 ~20:00Z (operator directive)
index    | Atlas  | M1   | OBSERVATION | none (PARKED, reports only)               | portfolio memory (s11), pending memo Q2     | 0 hits; not briefed
