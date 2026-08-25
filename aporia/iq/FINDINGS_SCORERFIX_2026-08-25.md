# SCORER-FIX — ADVANCE. The fix is clean, and the audit says the defect is the norm.

Preregistration `aporia/iq/PREREG_SCORERFIX_2026-08-25.md` committed **35b500cd, before the fix
code existed**; the harness self-gates and refused to run until that commit was on record.
Corpus reused unchanged: `sha256 e2e6898d…`, verified at run time.
Ledger: `aporia/iq/RESULT_SCORER_FIX.json`. **`C` was not edited** — the fix is a harness-side
variant op.

---

## Verdict: ADVANCE. S1, S2 and S3 all hold.

    S1  every mutant on NONDEGENERATE, before -> after the abstain fix
          M1_plus       0.1366 -> 0.0000        M2_off_by_one  0.0000 -> 0.0000
          M3_swapped    0.1366 -> 0.0000        M4_identity    0.0000 -> 0.0000
          M6_half_total 0.1268 -> 0.0000        M5_return_n    0.0000 -> 0.0000
        worst mutant after the fix: 0.0000, against a preregistered bar of <= 0.02.

    S2  the port, per surface, before -> after: IDENTICAL on all four.
          v0 0.9497   v1 0.9227   v2 0.0000   v3 0.9600      (0 surfaces moved)
        NONDEGENERATE 0.6780 -> 0.6780.

    S3  the 120-task battery: baseline 0.833333 -> 0.833333, ported 0.875000 -> 0.875000.
        dE_port after the fix = +0.041667. UNCHANGED. No prior number in this arc moves.

**The port was not riding the guess.** S2 was the consequential prediction — a move there would
have forced IQ-PORT-1's ΔE to be re-read — and it is flat to four decimal places. The mutants
lose their entire score; the port loses nothing. That is exactly the separation the mutation
battery was supposed to provide and could not, because the substrate was paying a floor.

**The attainable-range check paid off.** With abstain the floor is exactly 0, so the ≤0.02 bar
sat inside the range rather than below it. Contrast TRANSFER-1, where I placed a `<0.10` bar
beneath an achievable floor of 0.25.

## S4 — the audit, and a vacuous first reading I caught and redid

The first audit ran every scorer against **one** shared probe state. That state populated
`ordered`, `facts` and `derived_facts`, which are exactly the slots several guarded scorers'
exclusion clauses forbid — so those scorers never fired, wrote nothing, and were recorded as
"abstained". **That reading could not have come out any other way, so it was VACUOUS**, not a
pass. Redone with a state tailored to fire each scorer's own guard:

    score_by_aggregate         GUESSES candidates[0]
    score_by_aggregate__g      GUESSES candidates[0]      <- guarded
    score_by_derivability      GUESSES candidates[0]
    score_by_derivability__g   GUESSES candidates[0]      <- guarded
    score_by_max_entity        GUESSES candidates[0]
    score_by_max_value         GUESSES candidates[0]
    select_nth                 GUESSES candidates[0]
    select_nth__g              GUESSES candidates[0]      <- guarded
    score_by_comparison__g     abstains
    score_by_extreme_number__g VACUOUS — its guard did not fire under my probe; unresolved

**8 of 10 scorers guess. Three of them are guarded**, so they sit inside Apollo's clean-routing
pool. The pathology is the **norm** in this substrate, not an exception, and
`score_by_aggregate` was merely the one a mutant happened to route through.

`score_by_extreme_number__g` is reported as **unresolved**, not as an abstainer. I did not find
a state that fires its guard, and claiming it abstains on that basis would repeat the vacuity I
just corrected.

## The consequence I am flagging and NOT acting on

**`select_nth__g` is in the known 0.8333 ceiling organism, and it guesses.** Lexis's joint
product BFS (`fcdc91af`) proved 0.8333 exact under the "clean-routing" pool on the stated grounds
that guarded scorers do not rack up incidental hits the way an unconditional scorer does. That
premise is false for at least three guarded scorers.

**What this does NOT establish.** Fixing `score_by_aggregate` alone moved the battery by exactly
zero (S3). Whether fixing all eight moves the 0.8333 ceiling is **unmeasured**, and the direction
is not obvious: removing a guess can only lose tasks that the guess happened to win, so the
ceiling can fall but cannot rise. It could be that no ceiling-organism task depends on a guess.

**That is the next rung, and it is preregistered as a question rather than answered here.** I am
not expanding this rung's scope to chase it, and I am not touching `C`.

## Scope

- Single seed, no replication, no intervals quoted.
- The abstain variant reproduces `score_by_aggregate` exactly except on the no-match path; the
  guarded variant is rebuilt from the same function with the registry's own guard.
- The audit is a single synthetic probe per scorer, not a measurement over the battery. It shows
  each scorer's behaviour on its own no-match path and nothing about how often that path is taken.
- **Nothing dropped**: every task scored under both pools; pipeline exceptions count as wrong.

## Method note — my own retry loops were the contention

For several passes I attributed repeated `.git/index.lock` failures to other agents. Sampling
`tasklist` showed **zero** git processes against a 12-minute-old lock, which I read as a crashed
process and removed. The lock reappeared instantly: it was **my own background retry loop**,
cycling `git add`/`git commit` every 5 seconds, and the process count had been sampled during its
sleep window.

Two corrections, both mine:

1. **A point-in-time process count is not a liveness test for a process that cycles.** The check I
   used cannot distinguish "crashed" from "sleeping between attempts".
2. **Tight retry loops are themselves the contention.** Stopping my own loop cleared the lock
   immediately. Retries belong at a cadence matched to the work, not at 5-second intervals, and
   two of my own loops racing each other starved both.

The standing rule "never delete the lock" survives, with its premise made explicit: it assumes a
live owner, and the liveness test has to be something better than one `tasklist` sample.
