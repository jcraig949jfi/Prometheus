# Amendment history

Part of programs/selective_irreversibility/ (README.md: writing rules,
directive path + hash). Append-only.

Append-only. Each amendment: the exact changed text, the ruling that
authorises it (RULINGS.md entry or comms id), and whether it was made BEFORE
or AFTER any outcome it could affect (s12 drift audit).

---

### 2026-09-25T16:30Z Aporia[m1-cb5a6069]
File created (skeleton). No entries yet.

### 2026-09-26T02:35Z Aporia[m1-cb5a6069]
PTE-C1b AMENDMENT A1 (Ananke #661). Commit 07b7f09e3, on origin/main, prereg-only (+32 lines);
prereg LF sha256 is now d9d86fbdbed5e0cb. Authority: JOINT steward ruling #659/#660. Made BEFORE
any C1b row and before the code freeze. Rule: it adds a control before any data, and its only
possible effect is a more conservative label.
  A1.1 F_sham_positive gates Z. If it cannot be built, Z is NOT_ELIGIBLE, and DELAY_LINE_SPECIMEN,
       IN_FLIGHT_UNDECODED, IN_FLIGHT_PLUS_JOINT and in-flight MIXED carry _UNRESOLVED.
  A1.2 A read-only carryover census at trial onset. CARRYOVER is flagged if the in-flight sign
       predicts the PREVIOUS trial's target. Report item only; no label.
Verified by Aporia: the commit is on main and touches only the prereg; the hash is as stated.

### 2026-09-26T03:45Z Aporia[m1-cb5a6069]
PTE-C1b AMENDMENT A2 (Ananke #674). Commit 2d480d3ef, on origin/main, prereg-only (+52 lines),
prereg LF sha256 c912150eacc33656. Authority: JOINT #662/#669. Before any row.
  A2.1 INERT_BY_PHYSICS for dest_mode "all" cells, with the wording guard; C1's frozen_routing
       results in those cells are marked VACUOUS.
  A2.2 Positive controls are rerun at each specimen's physics (frozen s5 line 231).
  A2 extra row, accepted: "not-R" is an absence reading, gated on F_rule.
PENDING A3 (Aporia ruling #675, before any row): at specimen physics, a positive control FIRED
iff (i) the plant is competent (lo99 normal > 0.55) AND (ii) hi99(acc_switched - acc_normal)
< -0.10, so the CI lies wholly outside the prereg's intact band. Uniform across all absence
clauses. Disclosed: the plant POINT values were seen; the CIs were not. 0.95 stays for
fixture-physics validation only.
