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
