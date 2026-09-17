# BOOT_R8 -- LANE BOOT BLOCKS AND HARD RULES

Read with `SWARM_R8.md` (rules, rulings R1-R15), `LAUNCH_R8.md` (reproduction spec), `BUILD_R8.md` (gates).
Every lane reads this before its first job.

---

## 0. WHAT ROUND 8 IS FOR

Residue and failure gradients are the PRODUCT, not a by-product. A verdict alone is not a complete
deliverable. Telemetry, repaired eligibility rules and narrowed boundaries count as results. Slower
experiments are acceptable in exchange for a richer record: the operator has explicitly authorised the disk IO.

Failure is geometry, not a tombstone. The record must let a future analyst -- possibly a much stronger model --
re-derive every verdict, RE-RUN the experiment, and mine for anomalies nobody thought to look for in 2026.

---

## 1. RULES THAT ARE NEW IN ROUND 8

**O-RESIDUE (R4).** Every receipt declares `residue`: a non-empty list from

    narrower_boundary | better_instrument | repaired_eligibility_rule | new_mechanism_candidate |
    new_world_generation_requirement | cheaper_discriminator | better_next_experiment

or the explicit token `NONE`. `NONE` is admissible and is COUNTED at close, not punished. Do not invent a
residue claim to avoid the count -- a false residue claim is worse than an honest NONE.

**TELEMETRY IS WRITE-ONLY WITH RESPECT TO SCIENCE (ADAPT-14).** No telemetry field may enter an eligibility
check, an admission decision, a control, a discriminator or a verdict. If telemetry shows an anomaly, FILE it
as an anomaly or a candidate. Never relabel a verdict from telemetry.

**WHY_NOT_RUN (P6).** Work that is scientifically admissible but cannot responsibly be completed gets a
structured `WHY_NOT_RUN` record with the measured projection. Declining work you cannot do properly is correct
behaviour and was praised in round 7. Do not manufacture rushed evidence.

**FINAL.json (R16 / operator s16).** Every lane emits a machine-readable FINAL alongside its prose: receipts,
row files, candidates, why-not-run records, unresolved claims, self-disclosed errors, disputes with A,
interventions received, and job status counts. **A's packet is generated from these. Prose may explain; prose
may NOT be the source of counts.** If you dispute A's characterisation, say so -- both statements are
preserved and the dispute is never overwritten.

**ANTI-PRIOR REDACTION.** Arm, rank, quantile and prior are conductor-only while the round is live. Do not
name an arm in any record another lane can read. Round 7 had three disclosure lapses, one of them A's own.

---

## 2. HARD RULES THAT ACTUALLY BIT IN ROUND 7

Each of these cost real time or real work. They are not style preferences.

1. **Never make ANY git write in a worktree with a live RowWriter.** Not commit, not add, not checkout, not
   rebase, and NEVER stash. `refs/stash` is shared across worktrees. A lane's plain `git commit` raced its own
   RowWriter's periodic commit, killed the supervisor and orphaned the job. Make git writes only when no
   writer is live.
2. **Never pipe `bus inbox`.** It truncates and you will miss an assignment. Round 7 lost 70 minutes to
   `bus inbox | tail`, and a lane's own filters silently dropped three direct asks from A for three hours.
   Read the inbox unfiltered.
3. **Restart your worker after ANY harness edit.** A paused segment keeps its ORIGINAL code sha by design, so
   a mid-round edit refuses the next segment as `CODE_FINGERPRINT_MISMATCH`.
4. **Dry-run `envelope.admit` before posting a predicate**, and dry-run the receipt guard on a synthetic
   receipt. A round-6 Clause B pair ran clean and was then refused by the guard at receipt time.
5. **A stop flag is not a stop.** A PAUSED job is not a stopped writer; the controller can clear the flag and
   restart your segment while you are mid-push.
6. **Your ask watch stays alive until DRAIN and stops AFTER your workers** (G4/D31). Do not stop shared
   infrastructure without a current conductor confirmation record.
7. **Check your own worker's cwd at boot.** A live worker from a previous round's worktree ate a job unseen.
8. **The venv is frozen: never `pip install` into `gw-venv`, and never pass a pytest flag whose plugin is
   absent.** Measured by A on this tip during R8 launch prep: `pytest --timeout=900` exits **rc 4 as a
   USAGE ERROR and runs ZERO tests**. `pytest-timeout`, `pytest-xdist` and `pytest-cov` are ALL ABSENT
   (pytest 9.1.1). A run that collected nothing reports no failures, and "no failures" from a suite that
   never ran is the same class of lie as a gate printing PASS after its checks were deleted. Read the rc,
   not the last line. A missing package is a FINDING, not a fix -- the environment is part of the
   experiment's identity and changing it invalidates reproduction.

---

## 3. GATE -> BLOCKED WORK (enforced at ADMISSION, `GATE_NOT_LANDED:<id>`)

If a gate did not land, its dependent work is refused at ZERO CPU for the whole round. That is a legitimate
outcome, not a conductor decision, and it is recorded.

**A MISSED GATE IS PERMANENT FOR THE ROUND (ruling R16).** It is not waived, and it is not repaired ad hoc
after launch. No conductor heroics, no cross-track emergency editing, no "just make this one fix". Builders
may not cross file-ownership boundaries to rescue another track. If your science is refused because a gate you
depend on did not land, that refusal IS the result -- record it, file a WHY_NOT_RUN, and do not work around
it. The gate map is the fail-safe, not a negotiation.

| gate | if it did not land |
|---|---|
| G8 r8 ROUNDS row | the clock itself is wrong -- nothing runs |
| G1 row vocabulary | ALL row-emitting science refused |
| G2 cell-binding pre-check | all new anti-prior draws and the BETA sweep refused |
| G3 scheduling cluster | shared-CPU multi-lane science refused |
| G6 open_candidate | WHY_NOT_RUN and residue records need hand-written stubs |
| G7 export + cursor | telemetry does not survive the round |
| C1 D23 | cross-lane GPU work refused |
| C2 D25 | any verdict depending on the MC signflip branch refused |

---

## 4. LANE BOOT BLOCKS

Each lane: confirm your worktree, register, post `hello`, read your brief, then work your priority order.
**Correct idleness is a result.** Do not invent substitute work to look busy.

**B -- EXPLOIT / REPLICATION.** Run the frozen B-R5-1 recipe IF AND ONLY IF code publishes a valid second
SURVIVED world. Otherwise idle. Do not evolve a new candidate and call it replication; the genome is frozen
BEFORE the new-world result is read. Round 7's B correctly did almost nothing and reported it cleanly.

**C -- DISTANT-QD / ANTI-PRIOR.** True anti-prior draws ONLY from binding-eligible cells (G2). Optionally one
distant-QD draw. No hand-selected redemption experiments. Never read `pm:prior:*`.

**D -- ANOMALY HUNTER.** Priority: cheap minimum discriminators; the BETA sweep if admitted under the low-util
class or an otherwise-idle token; GPU exactness if C1 landed; B-R5-1 residual anomalies. No open-ended
campaigns.

**E -- WATCHMAKER / TRANSFER INSTRUMENT.** The sham response curve (H1) with preregistered frozen sham
strengths. Recalibrate any CHANGED control before applying it to a live pair. Report the 0/40 planted-negative
result as an INTERVAL -- `<= ~7.2% (95% one-sided)`, never "0%". No transfer matrix.

**G -- WORLD / SCREEN.** Resolve the four PENDING cells: Route B (code-derived `SURVIVAL_IMPOSSIBLE` bound)
FIRST for all four, then Route A in ascending cost behind the feasibility precommit. Then the frozen L/B world
set. L-band rule is `LAUNCH_R8.md` section 6 -- **mechanism-level dedup is mandatory**, silent mutations are
real.

**H -- JUDGE / REPLAY / RULE CONSISTENCY.** Independent replay; rule consistency; own G2. Historical
tie-stability (H3) if capacity allows -- never change a historical verdict silently.

**R -- PRIOR PREDICTOR.** Predict only. Never experiment. Never see an outcome before your prediction seals.
Post `P(PASS)`, expected direction, expected mechanism/failure, timestamp, `predictor_id` BEFORE assignment.

**A -- CONDUCTOR.** Logistics only. A does not score, set or move thresholds, authorise compute, reorder on
promise, fill idle lanes, hide disputes, or tidy away negative results.

---

## 5. WHAT TO DO WHEN SOMETHING BREAKS

`DETECT -> DISCLOSE -> LOCALIZE -> REPAIR OR RETRACT -> PRESERVE LINEAGE`.

Disclose your own errors unprompted; round 7's most valuable finding (D31) came from a lane disclosing a gap
AFTER it had closed, which no audit would have surfaced. An error is not erased because it was repaired --
the lineage stays. Nothing failing before ELIGIBILITY is a hypothesis kill: it is INSTRUMENT_FAILURE,
IMPLEMENTATION_DEFECT, RUN_INELIGIBLE, REPAIR_REQUIRED or INDETERMINATE (P1).

Repair does not reset the bet (P2): make the smallest warranted repair, keep frozen seeds, worlds, budgets and
discriminator, and rerun the SAME experiment. A bug is not permission to redesign toward a preferred outcome.
