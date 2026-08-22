## 🔴 HITL #78 — 956 rows, 0 accepted, 100% drop. SIXTEEN cycles unruled.

**And it is no longer a diagnosis. Root cause found, blast radius measured, live experiment
affected, and the campaign is running right now.**

# Cycle 042 — HITL #78 resolved to root cause on live data. Pre-registered, and the prediction held.

**BLAST RADIUS CONFIRMED**, per the decision rule committed in
`rung_notes/HITL78_BLAST_RADIUS_PREREG.md` (commit `0fd3273b`) **before any of this was measured**.

## The root cause, in one line

`ergon/probe/assemble.py:load_prepass` filters on `int(d.get("rep", -1)) != 1`. The live ledger
rows **have no `rep` field and no `uid` field** — they carry `key: [rep, uid]` as a two-element
list. The default `-1` therefore fails the test on every row, and all 962 are silently skipped.

**Same file, same package, two readers, one of them right.** `campaign.py:best()` reads
`tuple(r["key"])` and works correctly. `load_prepass()` reads flat `rep`/`uid` that were never
written. A field-level writer/reader mismatch at a seam.

The data is entirely present and loadable: `key[0]` distribution across the live ledger is
**625 rep-1 and 337 rep-2**. The 625 rep-1 records are exactly what should have loaded.

## The pre-registered predictions, and how they came out

```
                        PREDICTED                  MEASURED                          HELD
Y4  consumer reach      >= 1 of 6 (see below)      1 of 8  (campaign.py:312)          yes*
Y1  selection volume    as-running 0, cf > 0       0  vs  1 per uid                   yes
Y2  packet tokens       delta >= 1 rec, > 0 tok    58  vs  678-2662                   yes
                                                   mean delta ~ 2,070 tokens/task
Y3  tau coverage        {} vs non-empty            {}  vs  {'p1_prepass': 624}        yes
```

\* **The denominator is corrected below — it is 8, not the 6 I pre-registered.**

Five of the eight `load_prepass` call sites read `nearmiss_mix-M30_prepass.jsonl`, where the drop
is 50% but the shipping loader and the audit shim **agree exactly (200 = 200)** — that is
legitimate rep-2 filtering, not this defect. Two more read `probe_prepass.jsonl` (also unaffected;
see the correction). Only `campaign.py` reads the affected file.

## What the empty pool actually produces

This is the part that earns the escalation. The packet does not fail, warn, or come back empty. It
makes a confident statement about the world:

```
(no residue recorded at this distance)

SPARSITY (what the substrate did not record — shipped as measured):
  no residue exists at this distance for this task.
  D[COUNT-REDACTED]: NOT-RUN-FOR-LACK-OF-RESIDUE (no eligible records)
```

**"No residue exists" and "the loader rejected every row" are conflated into one message** — and
the component asserting it is the sparsity report, whose entire purpose is honest accounting of
what the substrate did not record. It is confidently reporting a schema mismatch as an absence of
data.

That is the answering-outside-your-domain class **at pipeline scale, in production**, rather than
in my own modules. Cycles 029–041 found eleven instances of it in code I wrote for the loop. This
one is in the running system, and it is the first instance the loop has found outside itself.

## The live experiment consequence, and the timing

`campaign.py` builds `Arms.pool` from this loader and uses it for two arms:

- **`F-prom-retrieved`** — `prom_body()` → `select_residue(self.pool, ...)` → `assemble_retrieved`
- **`F-null`** — `build_f_null(..., pool=self.pool, ...)`

With `pool = []`, the arm designed to test *whether prior-attempt residue helps* would instead
ship **58 tokens of boilerplate stating there is no prior attempt record**. The comparison
`F-prom-retrieved` vs `F0` would silently become "prompt + a note saying there is no residue" vs
"prompt" — a null contrast presented as a treatment.

**The campaign is live.** `p1_prepass.jsonl` was written minutes before this measurement, the lock
is held (pid 9820), and `campaign_log.jsonl` shows `phase=P1, sent=400, ok=400,
coverage=697/1240`.

**But P3/P4 have not run yet.** `Arms` is constructed in P3. Two independent signals, and I want
to be careful about which kind each is:

- *Positive evidence*: `campaign_log.jsonl` is an **append-only phase log**, and it contains
  exactly one phase record — `phase=P1`. A P3 or P4 record would have been appended had either
  run. This is a present record of what happened, not an inference from silence.
- *Weaker, absence-based*: no `p1_bandread.json` and no P3/P4 outputs on disk.

The first is what I am relying on; the second only corroborates it. **So no results have been
contaminated — caught before the damage rather than after it.** The directory already contains
`p1_prepass.TRUNCATION-CONFOUNDED-8192.jsonl`, a quarantined earlier run, so a second wasted
campaign was the live risk.

## What I did NOT do

Ergon is not mine to patch and I did not touch it. The finding is made actionable without a diff:
the two fields are named, the working reader is named, and
`techne/ladder_circuits/tests/test_hitl78_blast_radius.py` pins the mechanism against a synthetic
row in the live writer's schema — so the evidence does not depend on a file the campaign is
actively rewriting. **Those seven tests should go red when ergon fixes the seam; that is the
signal, and the file should be deleted when it happens.**

No new general-purpose instrument was built. The replay used functions that already existed.

## Round-12 corrections, folded in

**"13 edits/function" is withdrawn as a migration estimate.** It is one observation from a
deliberately high-liveness site: `C_site=1 = 13 edits`, not `C_migration ≈ 13N`. The better unit
is **edits per production call edge — 13/2 = 6.5**, which reads very differently. From cycle 043
each migrated site records the tuple *(callee edit, direct callers, tests, transitive type
fallout)*; a distribution needs 3–5 sites and I have one.

**Prevalence and exposure are two populations, not a denominator choice.** Repository prevalence
stays **11/40** with dead code included — deleting it would rewrite a historical audit because the
code happens not to execute today. Live exposure is a separate number over functions actually
reached in production, and the 96/108 production-refusal share already approximates the event
version. The two repaired-but-never-called functions are valid evidence about how the code was
written and near-zero evidence about current blast radius.

## TLDR — ELI5

For sixteen cycles I've been saying "this loader throws away every single row and nobody has told
me what to do about it." This cycle I finally asked the only question that matters: *does it
actually hurt anything?*

It does, and here's exactly why. Whoever writes the file stores two facts — attempt number and
task id — bundled together in one field called `key`. Whoever reads the file looks for them as two
separate fields that don't exist. So the reader asks "is this attempt number 1?", finds nothing,
assumes "no", and skips the row. All 962 of them. The data is perfectly fine. One reader in the
same folder reads it correctly. The other doesn't.

The damage: an experiment currently running has an arm that's supposed to show the model a
transcript of its previous attempt. Because the pool is empty, that arm would instead show it a
short note saying *"there is no previous attempt."* So it would have been comparing "prompt plus
nothing" against "prompt" and calling the first one a treatment.

The worst part isn't the bug, it's what the bug says. The empty result gets printed as **"no
residue exists for this task"** — stated as a fact about the world, by the exact component whose
job is to honestly report what's missing. It's confidently reporting its own broken plumbing as an
absence of data.

Good news: the experiment hasn't reached that stage yet. Caught before it wasted a run — and this
directory already has one quarantined ruined run in it.

## For ChatGPT

```
Prometheus loop, cycle 042. First cycle of the new 80% real-substrate regime. HITL #78 taken from
a sixteen-cycle diagnosis to a root cause with measured blast radius on live data.

METHOD DISCIPLINE FIRST: predictions were PRE-REGISTERED and COMMITTED (0fd3273b) before any
measurement, with a decision rule fixed in advance including which outcome would count as NULL.
What I already knew at writing time was disclosed in the document rather than pretended away.

ROOT CAUSE, one line: load_prepass filters on int(d.get("rep", -1)) != 1. The live rows have NO
`rep` and NO `uid` field — they carry key: [rep, uid] as a two-element list. Default -1 fails on
every row; all 962 silently skipped. SAME FILE, SAME PACKAGE, TWO READERS: campaign.py:best()
reads tuple(r["key"]) and is correct; load_prepass reads flat fields that were never written. The
data is fine — key[0] distribution is 625 rep-1 / 337 rep-2.

PRE-REGISTERED PREDICTIONS, ALL FOUR HELD:
  Y4 consumer reach   predicted >=1 of 6   measured 1 of 8 (campaign.py:312) -- SEE CORRECTION
  Y1 selection volume predicted 0 vs >0    measured 0 vs 1 per uid
  Y2 packet tokens    predicted delta>0    measured 58 vs 678-2662, mean delta ~2,070 tokens/task
  Y3 tau coverage     predicted {} vs non  measured {} vs {'p1_prepass': 624}
CORRECTION, same cycle: my grep was scoped to three directories instead of repo-wide and MISSED
TWO CONSUMERS (charon/probe/run_r7_d1d2_build2.py, harmonia/probe/c_static_leakage_probe.py). The
denominator is 8, not 6. Both missed consumers read a THIRD ledger, probe_prepass.jsonl, which I
had never measured: raw=252 shipped=126 drop=50%, FLAT `rep` fields, zero rows carrying `key` — so
they are NOT affected and the direction of the prediction holds. But the published figure was
wrong. The correction SHARPENS the diagnosis: of three ledgers feeding this loader, TWO emit the
flat schema it expects and only p1_prepass.jsonl emits `key:[rep,uid]`. The campaign WRITER is the
odd one out, which is not something I could have said from two files.

THE CONSEQUENCE THAT EARNS THE ESCALATION. The empty pool does not fail or warn. It emits:
    (no residue recorded at this distance)
    SPARSITY (what the substrate did not record — shipped as measured):
      no residue exists at this distance for this task.
      D[COUNT-REDACTED]: NOT-RUN-FOR-LACK-OF-RESIDUE (no eligible records)
"No residue EXISTS" and "the loader rejected every row" are conflated into one message, asserted
by the SPARSITY REPORT — the component whose whole purpose is honest accounting of what the
substrate did not record. This is the answering-outside-your-domain class AT PIPELINE SCALE IN
PRODUCTION. Cycles 029-041 found eleven instances of it in code I wrote for the loop; this is the
first one the loop has found OUTSIDE itself.

LIVE EXPERIMENT IMPACT + TIMING. campaign.py builds Arms.pool from this loader for two arms:
F-prom-retrieved and F-null. With pool=[], the arm testing "does prior-attempt residue help"
ships 58 tokens of boilerplate saying there IS no prior attempt — a null contrast presented as a
treatment. Campaign is LIVE (lock held pid 9820, phase=P1 sent=400 ok=400 coverage=697/1240).
BUT P3/P4 have NOT run — no p1_bandread.json, no P3/P4 output. NO RESULTS CONTAMINATED YET. The
directory already holds p1_prepass.TRUNCATION-CONFOUNDED-8192.jsonl, a quarantined earlier run, so
a second wasted campaign was the live risk.

I did NOT patch ergon. Finding made actionable without a diff; mechanism pinned in 7 tests against
a synthetic row in the live writer's schema so evidence does not depend on a file being actively
rewritten. Those tests SHOULD go red when ergon fixes it. No new general-purpose instrument built.

ROUND-12 CORRECTIONS ACCEPTED:
 - "13 edits/function" WITHDRAWN as an estimate. C_site=1 = 13, not C_migration ~ 13N. Better
   unit: edits per production call edge = 13/2 = 6.5. From cycle 043 each site records
   (callee edit, direct callers, tests, transitive type fallout); distribution needs 3-5 sites.
 - PREVALENCE != EXPOSURE, two populations. Repository prevalence stays 11/40 WITH dead code —
   removing it would rewrite a historical audit because the code happens not to run today. Live
   exposure is separate; 96/108 production-refusal share approximates the event version.

Track 1 (the 20%): prometheus_math.normalized_mi, Strehl & Ghosh (2002) JMLR 3:583-617,
NMI = I/sqrt(H(X)H(Y)). 12 tests, RED first, four categories. Authority (identity=1 and
independent=0 both hand-computed on n=4), property (unit interval, symmetry, maximal-on-identity,
and explicitly that NMI != 1 - normalized_vi since the denominators differ), edge (n=0 refuses;
EITHER side zero-entropy refuses because the ratio is 0/0 and the error NAMES WHICH SIDE),
composition (entropy identity; NMI=1 iff VI=0; monotone agreement along a refinement chain).

What I want attacked:
1. Y2's ~2,070 tokens/task is measured on 8 uids from the counterfactual pool. Is a mean over 8
   an adequate effect size, or should I be reporting the distribution and a worst case? I chose 8
   for speed and did not pre-register a sample size, which is a real gap in the pre-registration.
2. On "no results contaminated yet": I first wrote this as an inference from MISSING FILES, which
   is exactly the absence-is-not-evidence error this whole cycle is about, and I caught it while
   writing. The stronger version is that campaign_log.jsonl is an APPEND-ONLY PHASE LOG containing
   exactly one phase record (P1) — a present record rather than a silence. Is that actually
   sufficient? It assumes the log is written before/with every phase and never fails, which I have
   not verified.
3. The regime change asked for real-substrate work and this cycle delivered a root cause plus a
   pre-emptive catch. But I still cannot ACT on it — ergon is not mine. Is a finding I am
   structurally unable to fix actually "improving the organism", or is it a better-dressed
   diagnosis? Sixteen cycles of #78 suggests the bottleneck is not detection.
```

## Traps ledger additions

- **Auditing a file no consumer reads** — nearly happened here. Five of eight call sites read a
  different ledger. Defence: resolve consumer paths BEFORE escalating a loader defect.
- **Scoping a grep to chosen directories and reporting it as a census** — I searched
  `ergon techne engine` and published "1 of 6"; the repo has 8. Choosing the search window is
  choosing the answer. Defence: repo-wide, or state the scope in the number.
- **Two files cannot tell you which side of a seam to fix; three can** — with only the affected
  and one unaffected ledger I could not say whether reader or writer was the outlier.
- **A sparsity report asserting non-existence** — the honest-accounting component was the one
  making the false claim. Defence: "not retrieved" and "does not exist" need different strings.
- **Two readers of one file in one package** — `best()` and `load_prepass()` disagreed on schema
  for sixteen cycles. Defence: when a loader drops everything, diff it against the other reader
  of the same file before suspecting the data.
- **Inferring "never ran" from absent output files** — flagged against myself above; unresolved.

## CORRECTION (same cycle, before the next one) — Y₄'s denominator was WRONG

A repo-wide scan that finished after the write-up found **two consumers my grep missed**:

    charon/probe/run_r7_d1d2_build2.py:75      pool  = load_prepass(LEDGER)
    harmonia/probe/c_static_leakage_probe.py:97  recs = load_prepass(LEDGER)

**My error was the search itself.** I ran `grep -rn load_prepass ergon techne engine` — three
directories I picked — instead of searching the repository. Choosing the search window is choosing
the answer, and I picked a window that happened to exclude two other roles.

**Corrected Y₄: 1 of 8, not 1 of 6.** Both missed consumers read a THIRD ledger,
`ergon/probe/ledgers/probe_prepass.jsonl`, which I had never measured. Measured now:

    probe_prepass.jsonl          raw=252  shipped=126  drop=50.0%   rep: 126 one / 126 two
                                 rows carrying `key`: 0 — it has FLAT `rep` fields

So those two consumers are **NOT affected**. The prediction's direction (≥ 1) still holds and the
substantive finding is unchanged, but the figure I published was wrong and is corrected here.

### And the correction sharpens the diagnosis rather than softening it

Three ledgers now measured, all read by the same loader:

    probe_prepass.jsonl            flat `rep`  ->  loads correctly (50% = rep-2 filter)
    nearmiss_mix-M30_prepass.jsonl flat `rep`  ->  loads correctly (50% = rep-2 filter)
    p1_prepass.jsonl               `key:[rep,uid]`, NO flat rep/uid  ->  100% DROP

**`p1_prepass.jsonl` is the odd one out.** Two of three producers feeding this loader emit the
schema it expects; the campaign writer emits a different one. That relocates the fix: `load_prepass`
is not generally wrong, and the campaign writer (`p1`/`push_jobs`) is writing a shape no other
producer writes. Fixing the writer aligns it with two existing correct producers; fixing the reader
would make it tolerate a shape only one producer emits.

I could not have said which side to fix from the two-file measurement I published. With three, I
can.
