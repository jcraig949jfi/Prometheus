# cw01-e02 — ENGINEERING LEDGER (XIII)

Experiment 2 of 10. Disposition **NULL** (ratchet hypothesis). RECONCILE 17:27 → disposition ~17:50,
≈23 min of a 24 h timebox. Science cost: 29.2 s for 4 replicates × 80 generations × 64 organisms.

---

## THE SCIENCE, BRIEFLY

Evolution worked **enormously** well — +174% ancestor-relative (4/4 replicates), with the mechanism
firing hard (ordered transformations 26.3 → 134.9 per episode) and every selected gene moving
decisively (p_norm 0.495→0.947, p_factor 0.452→0.941).

And there was **no ratchet**. Condition 1 (temporal ordering) fails: `p_factor` fixes *before*
`p_norm` in **6/6 runs across three selection strengths**, with separation growing to 12–13
generations at the weakest setting. The foundation never precedes what rests on it.

The mechanism is legible: **T2 is already profitable without T1** (Q8 measured +38.11% for factoring
alone). Selection grabs the directly-rewarding gene first and adopts the foundation afterwards as an
optimisation. A ratchet needs the foundation to be a *precondition*; here it is an *enhancement*.
That interpretive limit was written down **before** EXECUTE ran, and it predicted the result.

---

## STARTUP

**Reused unchanged from e01 — the first real evidence of the campaign's trajectory:**
`lib/seeds.py`, `lib/localrun.py`, `lib/residue.py`, and `Region`/`Refused` **imported** from
`world_e01.py` rather than copied. e01's five world defects were inherited as fixes, not re-earned.

**Had to be created:** `world_e02.py`, `execute_e02.py`, `WORLD.json`, the 12 QUALIFY predicates,
and `residue.process_census()`.

**Unexpectedly already existed:** nothing new — the e01 survey had already mapped the terrain. This
is what reuse is supposed to feel like.

**Failed qualification (5 defects caught before any budget was spent):**

| Predicate | Failure |
|---|---|
| Q10 | `arms["T1_enabled"] and prng.random()` short-circuited a draw → arms walked different random streams (**D019 — CW01-D010 again, in new code, within the hour**) |
| Q10b | the recurrence read was gated on the arm flag with **no gene**, so organisms paid 0.5 to look at an empty store (**D021**) |
| Q11 | the gain detector fired on **pure noise** — 0% synthetic → 1 gain; a 15% planted step → 4 gains, three before the step existed (**D022**) |
| Q8 | two probe genomes were **identical**, producing a spurious FAIL (**D023**) |
| — | patch scripts kept dying on shell escaping (**D020**) |

---

## EXECUTION

**Used:** `RowWriter`, `envelope.example/admit/prepare_row`, `lib/*`, numpy. **Unused:** broker,
worker, consumer groups, schtasks, epoch controller, Claude sessions — again, none required.

**The bottleneck was the instrument, again.** 29 s of compute against hours of instrument repair.
Eight science defects in e02 alone.

**Missing telemetry (D026):** only **6 rows** were emitted (4 replicate summaries + backend +
disposition) against e01's 128. The 4×80 per-generation trajectories — *which are the actual
evidence for the NULL* — existed only inside RESULT.json, and diagnosing the trajectory shape
required **re-running evolution**. Evidence that must be regenerated to be inspected is not durable.

---

## TEARDOWN

Clean. e02 ran in-process and owned **0** runtime resources. `pm:cw01:e02:*` verified empty by
re-reading, not by trusting the delete. 0 live consumers anywhere, 0 matched processes,
0 non-campaign dirty paths. All r8 science keys intact and untouched.

---

## PORTABILITY

Unchanged from e01 and still the most portable shape available here: **git worktree + `PM_TAG`**,
no GPU, no Redis (except the optional IX backend check), no container. M1 QUALIFIED; M2 / cloud CPU
LIKELY but untested and therefore not claimed; Podman UNQUALIFIED; Docker-in-WSL LIKELY.

---

## COMPRESSION

**Landed:** `residue.process_census()` — correct process residue matching (interpreter + exact argv
tokens), replacing substring matching that had flagged four `RuntimeBroker.exe`, `UserOOBEBroker.exe`,
`NVIDIA Overlay.exe` and two GOG Galaxy renderers as "stray workers" (**D018**).

**Extracted for e03 (the three OPEN driver defects):**
1. **A disposition builder** where every branch names the test that produced it and is *unreachable*
   unless that test ran (**D024** — my driver announced "gains are additive" about a knockout that
   never executed).
2. **An ancestor-seeded gain detector** (**D025** — `detect_gains` cannot evaluate generations before
   its baseline window, which is exactly where all the improvement was: +203.2% within gens 0–9).
3. **Per-generation row emission** (**D026**).

---

## THE HONEST HEADLINE

**The predicted cost curve has not appeared yet.** e02 logged **12** defects against e01's 8. Reuse
genuinely worked — three components carried over unchanged, e01's world defects never recurred — but
writing a *new* world reproduced the same defect **class** within an hour (D019 ≡ D010). Components
transfer; patterns do not. What caught it was the standing gate promoted from e01's failure, which is
the strongest argument so far for turning every failure into a gate rather than a memo.

The second lesson is about disposition honesty: the driver returned a confident NULL with a reason
describing a test it had never run. Two experiments in, **the most dangerous failure mode is not a
broken world — it is a well-formed conclusion about an unperformed measurement.**
