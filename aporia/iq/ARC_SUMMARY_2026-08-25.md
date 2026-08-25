# The IQ arc, 2026-08-25 — seven rungs, in one document

Written for an external reviewer. Every number here is traceable to a committed `RESULT_*.json`
in `aporia/iq/`. Preregistrations were committed **before** the code they govern in every case;
the commit hashes below are the audit trail for that ordering, not a claim about it.

---

## 0. What the arc was for

Apollo's O1 is a deterministic **ISA expressivity assay**:

    E(C, T) = max over type-correct compositions g in G(C) of score(g, T)
    ΔE(p)   = E(C ∪ {p}, T) − E(C, T)

Battery: 120 tasks (canary 50 + synth 30 + inference 20 + cross_tier 20). Baseline ceiling
100/120 = 0.8333. The missing 16.7% is exactly 20 tasks, all of which **abstain**.

The question the arc exists to answer is doctrine §9: *does this representation merely describe
what already worked, or does it tell the system what capability to acquire next?* — microscope
versus compass.

## 1. The seven rungs

| rung | commit | verdict | the number |
|---|---|---|---|
| IQ-PORT-1 | `28761a6f` | ADVANCE | ΔE_port = +0.0416667 = 5/120 exactly |
| provenance | `c66ea4a9` | CONFIRMED_MODULO_INCIDENTAL | 464,652 pipelines; 0 non-port reach 5/5 |
| IQ-NULL | `953a8e97` | ADVANCE | ΔE(no-op) = 0.000000; ΔE(check_transitivity) = 0.000000 |
| TRANSFER-1 | `285b8d44` | REDESIGN | port 0.95 structural / 0 transfer across route |
| SCORER-FIX | `5971288b` | ADVANCE | every mutant → 0.0000; port unchanged |
| CEILING-ABSTAIN | `e0675de7` | ADVANCE | ceiling unchanged; 0 tasks lost |
| BATTERY | `86b1e582` | ADVANCE | 6 admissible / 6 inadmissible when ablated |
| SELECTOR | `01bfbfa6` | PREREGISTERED | pre-flight predicts VACUOUS |

## 2. What is established

**The port works and is exactly what its label says.** ΔE_port = +0.0416667, battery
0.8333 → 0.8750, canary 0.60 → 0.70, all five previously-abstaining `all_but_n` tasks solved,
`single_primitive_baseline` still 0. Exact rather than bounded because the footprint, measured by
state-diff over all 120 tasks, is precisely those five. Verdict **ADAPTER** by monkeypatching
`fp.all_but_n` (5/5 → 0/5) — an execution, not a source reading. **Novelty claim ZERO**, fixed by
class before the run.

**The deflationary diagnostic is the real content.** Injecting the parser's output solves 0/5;
injecting the port's output solves 5/5. C's existing routing and scoring tail already handled
`all_but_n` given the count. The delta is a new template-shaped regex plus a one-line subtraction
that has existed since v1.

**The assay measures expressivity, not search dynamics.** Both nulls read exactly 0 — and the
no-op was genuinely at risk: it writes nothing at runtime but *declares* a write, which unlocked
`entity_counter` into the enumerable space. That region tops out 0.1000 below the ceiling. Real
unlock, zero gain.

**Three registered operators are structurally dead.** `entity_counter`, `evidence_updater`,
`distribution_reducer` can never appear in any valid ordering — their read-slots have no producer.
They are exactly the three the 2026-05-25 v2 rewrite was written to create. O1's effective pool
was **12 transformers, not 15**.

**The substrate pays wrong rules a floor.** 9 of 10 scorers emit `candidates[0]` when nothing
matches. That guessing is **completely inert for capability** — abstaining all nine costs the
ceiling organism and the ported pipeline zero tasks — but it gives any firing-but-wrong rule
1-in-4 on a 4-candidate task. It corrupts **mutation batteries**, not ceilings.

**The port does not transfer.** ~0.95 structural competence on the three of four surfaces its
regex matches, 0.0000 on the fourth, and the parser fires **0 times on 200** X-heldout tasks
expressing the identical relation.

## 3. What is NOT established

- **SELECTOR is unrun.** The arc's decisive question is open.
- The true abstain-regime ceiling **over all programs** is unmeasured; only two programs were
  scored. It would need Lexis's joint product BFS re-run.
- `score_by_extreme_number__g` was resolved as a guesser only at the last rung; before that it
  was reported UNRESOLVED, never as an abstainer.
- Every reading is single-seed. No intervals are quoted anywhere.

## 4. Errors I made and caught, with how

Listed because the reviewer's best attack surface is the ones I did **not** catch.

1. **A verdict rule compared rounded values to unrounded ones** and reported REDESIGN on a clean
   pass. Direction: false negative.
2. **A footprint computed as a set-difference was empty by construction**, so its predicate
   passed **vacuously**. Caught, redone as a differential footprint (25 tasks).
3. **A threshold below its attainable floor** — TRANSFER-1's `<0.10` bar against a 1/k floor of
   0.25, written one pass after I logged that exact lesson.
4. **An audit using one shared probe state** violated several guards' exclusion clauses, so those
   scorers never fired and read as "abstaining". Vacuous; redone per-scorer.
5. **A probe that perturbed what it measured.** CEILING-ABSTAIN v1 removed the emitted candidate
   — which destroys a genuine match by construction — and reported the proven ceiling collapsing
   by 24 tasks. Caught because 24 ≈ 25% of the 100 won tasks; **all 24 lost tasks had their
   answer at index 0**, against a 29% base rate. Replaced with rotation.
6. **A preregistered branch gloss falsified** — TRANSFER-1's REDESIGN fired for a cause its own
   preregistration named wrongly.
7. **My own retry loops were the git contention** I spent several passes attributing to other
   agents. A point-in-time process count is not a liveness test for a cycling process.
8. **I rewrote a published commit** when a background pusher raced a foreground amend. Repaired
   with `reset --soft`, never a force-push.

Every one was caught **by me noticing**, which is precisely the mechanism doctrine §2 says will
not catch the next one. That is the argument BATTERY was built on.

## 5. BATTERY, and the hole its first prospective use found

`adjudicate(claim) → ADMISSIBLE | INADMISSIBLE(reasons)` is a pure function over a structured
claim object — deterministic, reading exactly twelve structural fields, **zero prose fields, no
model call in the path**. Six rungs admissible; all six inadmissible when one falsifier is
ablated, so both endpoints of its range occur.

**Two disclosures.** TRANSFER-1 as literally shipped trips G-FLOOR; it passes only under the
corrected threshold its own findings established, and the shipped form is on the record. And the
gate's retro-validation is a **fit statistic** — those defects designed those gates.

**On first prospective use it found a hole in itself:** only **5 of 7** gates can fire on a
preregistration. `G-VACUOUS` and `G-INERT` key exclusively on post-hoc fields. Those are two of
the three defect classes I commit most, so SELECTOR's vacuity pre-flight had to be written by
hand. The prospective forms are specified and **deliberately unbuilt** — adding gates after
seeing what they would have caught is retune-to-pass.

## 6. SELECTOR, preregistered

Frozen candidate pool; five selectors (S_C, S_R, S_C+R, S_random, S_oracle) at identical
insertion count and downstream compute; DV = marginal held-out reachability **per library slot
and per unit compute**, never solve rate.

**Preregistered kill:** if R-ranking cannot beat compression or random under frozen candidates
and equal resources, ΔE's promotion to abstraction *selector* is killed — **and that does not
kill the assay as a diagnostic.**

**Mandatory pre-flight, predicted to fire.** Lexis measured ΔS = 0.00%. If fewer than three
frozen candidates move ΔE, every selector ranks a near-constant vector. PF3 gates on that, and
the preregistration predicts VACUOUS **in advance**, specifically so a vacuous outcome cannot
later be re-read as a kill.

## 7. Standing corrections carried forward

- The null for a firing-but-wrong rule on a k-candidate task is **1/k, not 0**.
- Apollo's clean-routing regime is **not** free of the guessing pathology; it excludes only the
  unconditional form.
- E(C) = 0.8333 is the exact ceiling under **clean routing** (proven closed at all depths by
  Lexis, `fcdc91af`); the unrestricted-pool maximum is 0.8917, reached only by guessing.
- Five canary tasks cannot distinguish a mutant at 0.00 from one at 0.14.
- Cost-to-falsify is prospective: 31 rows closed, predicted probe cost matched **27/31**.
