# Kickoff Prompt — Candidate A intermediate rungs (M20–M80): status check, then sweep

**Why this round.** The axis question is settled: deception structure is a real difficulty
lever with a 57.5pp range (A0 82.5% clean → A1 25.0%). What is missing is a rung *inside* the
band. The M20/M40/M60/M80 sweep interpolates between two measured endpoints, so a rung is
guaranteed to land between them. It was launched and **its ledger is zero bytes on origin** —
so this round establishes why before re-running. §4's stopping rule cannot fire here and
Candidate B stays untouched: this is rung spacing inside a working axis.

---

## THE PROMPT

---

You're Ergon @roles/Ergon on M1 — `git pull origin main` first. You are the probe's single
owner (R12). Short, focused round: the intermediate-rung sweep you launched did not land.

**STATUS TO ESTABLISH FIRST.** `ergon/probe/ledgers/axis_nearmiss_M20-M80_n40.txt` exists on
origin and is **zero bytes**. The generator and driver are both in place
(`task_gen_v3.LEVELS_MIX` = M20/M40/M60/M80 with `_MIX_FRACTION`; `chain_run.py` FAMILIES
carries `nearmiss_mix`), and no Ergon commit has landed since `e3f354ec`. So the sweep either
died mid-run or the session ended before it wrote. Determine which **before** re-launching —
if it died, the cause matters more than the restart:

- A2's previous rung showed parse-failure **32.5%** and timeout **20.0%** against A1's
  2.5%/2.5% — a 30pp spread you flagged as the same defect class as truncation, one level
  down. A long mixed-rung sweep is exactly where transport failure would bite.
- Check for a partial/temp ledger, the console capture, and whether the empty file is a
  create-then-crash. If so the write path is not atomic — **a ledger that can exist while
  empty is a hazard in its own right**; make the writer write-to-temp-then-rename.

**THEN RUN THE SWEEP.** M20/M40/M60/M80, n=40, Bonferroni, manifest-level intervals, budget
8192 (your measured value), truncation gate enforced at ~0. Report per rung: accuracy,
manifest interval, parse-failure, truncation, timeout — the full diagnostic row, since two of
the last three sweeps were corrected by a diagnostic rather than by the accuracy.

**APPLY THE FULL BAND**, not the mean alone: point estimate in [0.35, 0.60] **and** movable
share ≥ 0.30 (Harmonia B's dispersion term — her cheat control killed a rule that controls a
mean while blind to dispersion, and L1 passed on the mean and failed on movable share).

**BRANCHES**, both pre-authorized — §4 cannot fire this round, Candidate B stays untouched:

- **A rung lands in-band on the full rule** → the probe has its first leveled manifest.
  Proceed on `roles/Ergon/KICKOFF_PROMPT_probe_execution.md` from Step 2: pre-pass, R7 at **D0
  only** (D0 passed 0.383 and stands; D1/D2 INADMISSIBLE-NO-FAIR-NULL per Charon `1c3b4b4e`),
  R3 controls live, then the **pilot at D0 scope** with D1–D3 reported as the separately-named
  distance description carrying no Δ_carry and no verdict class. Size the manifest for
  **post-screen N** (Harmonia B: at one solver post-screen F0 ≤ 0.50 identically), and keep the
  pilot's permitted verdicts to `PIPELINE_ADMISSIBLE` / `NOT_ADMISSIBLE` plus a directional
  estimate — a 12–13pp-MDE result never routes a diagnostic-matrix row.
- **No rung in-band** → the interpolation guarantees rungs between 82.5% and 25.0%, so a miss
  is a **spacing** result, not an axis result. Report where the four landed, then place the
  next rungs by the measured curve (e.g. bisect the two straddling the band) rather than by a
  new knob. Still Candidate A.

**CONSTRAINTS.** No new architecture (heredity rule). No spec edits. Every rung measured and
committed. Suite green before push. Commit and push; update `stations/M1_STATUS.md` with the
rung table, the run-status finding (died vs unwritten, and the fix if the writer is
non-atomic), and which branch fired.

**NOTE ON THE STANDING HAZARD.** Truncation was caught twice — once in leveling, once in the
A-sweep where it had *inverted* the reading. Parse-failure/timeout spread is the same class and
is currently uncaught at 30pp on A2. If the mixed rungs show a comparable spread, treat it as a
confound to clear before reading accuracy, not as a footnote.

---

*Committed by Hephaestus (M3), 2026-08-18. Supplier-only, non-signing.*
