# Addendum A — Panel Reconciliation

> **Date:** 2026-08-13 · **Author:** Apollo (Claude Opus 5, M2)
> **Reconciles:** `pivot/STRATEGY_2026-08-12_resumption_and_roadmap.md` (committed
> `61b6ea9d`) against the Harmonia four-lens panel and the fleet revival assessments
> that landed 2026-08-12.
> **FREEZE COMPLIANCE:** written under the freeze James declared 2026-08-13 (and
> consistent with `stations/M2_STATUS.md`: *"No hard decisions until ~2026-08-14"*).
> This is a **read-only findings document**. It makes **no structural changes and no
> code changes**. The committed roadmap is **not edited** — corrections are recorded
> here and applied later, if approved.

---

## 0. Why this exists

The roadmap was written from a local tree that was roughly **281 commits behind
origin**. Between drafting it and reading the panel, four whole-program reviews, three
revival assessments, and seven new diagnostics landed. Several of the roadmap's
load-bearing claims are now falsified, and several of the things it proposed to *build*
**already exist**.

Both facts matter. The first is an error I owe an honest correction on. The second is
the difference between Apollo doing new work and Apollo rebuilding someone else's
instrument.

---

## 1. Corrections to the roadmap — my errors, worst first

### C1. §1 "the entire program stopped on 2026-06-27" — METHOD FALSIFIED, conclusion survives

I read local `HEAD` as program state. It was stale, I never fetched, and I could not
have known either way. Harmonia A made the identical error the same day, which the panel
promoted to a standing rule: **repo state is not program state** (already recorded as
`feedback_repo_state_is_not_program_state`).

Measured properly, in the window I called silent (2026-06-28 → 2026-08-11):

> **271 commits. 270 automated** (`auto: portfolio update`, `arsenal: capability
> matrix`). **1 substantive** — `fda01127`, Aporia's session journal, 2026-06-28.

So the *conclusion* — substantive agent work was dormant for ~6 weeks — holds, and holds
more precisely than I stated it. The *claim as written* ("no commits," "six and a half
weeks of silence") is false, and the method that produced it was unsound. A right answer
reached by an unsound method is not a result. **Correction: §1's dormancy claim stands
only as restated here, with the 270/1 split.**

Harmonia B measured the same collapse independently and dates it earlier and better than
I did: monthly `.md` churn ran **28,268 (April) → 2,031 (May, 7%) → 392 (June, 1.4%)**.
The sprawl ended in May, not late June. My freeze date was an artifact of where my clone
happened to stop.

### C2. §1 "0% reject → the battery never certifies a true claim FALSE" — CITING A FOSSIL

This was load-bearing in the roadmap: I used M0's 0% type-II rate to argue the failure
mode is *silent, not loudly wrong*, and therefore that the audit fallback (success-state
A) is solid. **The panel killed it inside a 24-hour window.**

- Harmonia A: `verify()` returns `valid=False` on unregistered kinds — it **does**
  certify true claims wrong.
- The 0% held only because M0's harness **hand-routed around `verify()`**.
- Harmonia D found the bug firing **160/160 at R5/R7/R8** on the live ladder.
- Aporia caught the fleet propagating the number while it was already dead.

**Correction: §1's "fails silent, never loudly wrong" is withdrawn, and the inference
built on it — that the audit fallback is safe — is unsupported pending a re-measurement
that does not bypass `verify()`.** Anyone citing "0% type-II" after 2026-08-12 is citing
a fossil, and my roadmap is one of the documents doing it.

### C3. §8 ladder v0.2 — the ladder is a design document, not an instrument

Harmonia D found, and **I confirmed independently** by reading
`harmonia/services/grading_oracle.py:60`:

> `TIER_GENS` holds exactly **R0, R1, R2, R3, R5, R6, R7, R8**.
> **R4 and R9–R12 do not exist.** Five sixths of the upper ladder was never built.

Three consequences:

1. My §8(c) — "the *fails-in-the-tier-predicted-way* clause has no recorded instance" —
   is **partly explained rather than merely confirmed**: for R4 and R9–R12 there is no
   instrument that *could* have produced an instance. The audit I proposed is still worth
   running on R0–R3/R5–R8, but its scope is a third of what I assumed.
2. My §8(e) — "sharp tests are writable now" — was **mis-scoped**. The gap is not
   test-sharpness, it is tier non-existence.
3. **Apollo's own charter target — R9 (compositional synthesis) — points at a tier with
   no grader.** The 2026-05-22 baseline-matrix falsification that "falsified Apollo at R9"
   used a bespoke test, not a ladder instrument. That result stands on its own; the *tier
   label* attached to it does not.

### C4. §6.2 / §9.5 "diversify hypothesis classes" — the prescription does not terminate

I inherited this from Harmonia A's B1/B2 framing and repeated it as leverage item #5.
Harmonia D refined it in a way that **breaks the action**:

> *"Does novel structure exist outside H?"* has **no finite certificate**. B1 is not
> establishable in principle, so **every possible instrument result is B2-shaped**, and
> "add another hypothesis class" never terminates — there is always another class.

D's redirect: adopt **class-relative exhaustion** as the deliverable in its own right,
not as a way-station toward B1. **Correction: §9 item 5 and the §6.2 framing are
superseded.** The panel calls this the most useful disagreement it produced, and I agree:
my version would have kept the program hunting a question no instrument can answer.

### C5. §3 "widening has been 100% human-supplied" — SURVIVES, with a disclosed dependency

The panel's standing rule #2 is **base-rate null before any pattern claim**, and the kill
list shows both A's and C's dispositional claims dying to exactly that. Mine is a census
of a complete population (all five Apollo walls), not a sample from one, so a base rate
does not straightforwardly apply — but it has a different soft spot, and it is the *same*
soft spot as the open Apollo question in §3:

**"Agent-supplied widening" vs "search-found improvement" is a classification call I made
without stating a criterion.** Crossover found a de-novo solver in 4/5 seeds and produced
61 `novel_multitier` discoveries — search-found, by any ordinary reading. I classified
those as *exploitation within a fixed representation*, which is what makes "0 self-found"
true. That classification is defensible but it is **load-bearing and undeclared**, and
§2 below shows the panel's Apollo verdict turning on the very same distinction.

**Correction: §3's thesis stands, with the criterion now stated explicitly — a
"widening" adds a representable shape; an "improvement" reaches a shape already
representable. Anyone who rejects that criterion should reject the 5/5 claim with it.**

---

## 2. Already built — what §10/§11 proposed and the panel shipped first

| Roadmap item | Status | What actually exists |
|---|---|---|
| §6.2 program-wide **coverage measure** ("what replaces the kill date") | **ALREADY BUILT** | `harmonia/diagnostics/lane_exhaustion_audit.py` — class-relative exhaustion, thresholds fixed in April, with null controls that pass. **It already fires on Apollo.** |
| §8(e) sharp tier tests | **SUPERSEDED by a better pair** | `ladder_liveness_audit.py` (positive control: can *anything* pass?) + `ladder_leakage_audit.py` (negative control: can a *cheat* pass?) |
| §10 W0 typed widening records | **PARTLY EXISTS** | `harmonia/corpus/typed_objects.jsonl` (14 objects) + `validate_corpus.py`. Apollo's widenings are not in it; the schema is. |
| — | **NEW, no roadmap analogue** | `component_reachability_census.py`, `dependency_door_audit.py` |
| §11(4) M1 candidate-organism harness | **STILL UNBUILT** | B′ exists — 24 held-out claims, independent model family, oracle calibrated 8/8 — and is **unspent**. It must be graded **once**. |

**Net: two of my four proposed builds already exist, and one of the existing ones is
better than what I specified.** Building the coverage measure now would have been
duplicated work — which is exactly the outcome this reconciliation was meant to prevent.

### The consequence of R1 that I did not anticipate

Ruling R1 made mathematics the program's **calibration standard**. Harmonia C then
measured the library that *is* that standard:

> `prometheus_math` (307 modules, ~160K LOC) + `techne.lib` do not import on this host.
> Cause: **one line** — `prometheus_math\__init__.py:35` → `techne\lib\class_number.py:19`
> → bare `import cypari`.
> Doors: **29/222 importable now → 46 with `cypari` → 48 with `snappy` → 220/222 with
> `knot_floer_homology`.** `pip install snappy` resolves all three.

> **Any instrument that "passed on math" this year passed against 29 modules.**

The calibration standard R1 leans on has been **87% unreachable since April**. C
correctly did *not* run the install — it changes the global interpreter and is James's
call. Honest bound (C's own): an import is a weak positive and a strong negative; 220
bounds STRANDED from above, and does not certify the mathematics.

**This is the single cheapest high-leverage item on the board, and it is a DECISION
parked for James — not something Apollo should touch, freeze or no freeze.**

---

## 3. The one call that is Apollo's alone

Harmonia C's exhaustion audit fires on Apollo — **5 kills, 0 constructive results, class
`evolutionary_search`, threshold crossed 2026-05-24**, lane continued to 06-28. But C
declined to hide the sensitivity:

> If the 2026-06-16 recombination result is classed as **`search_operator`**, Apollo
> **fires**. If crossover is classed as *part of* **`evolutionary_search`**, that class
> has a June success, the count resets, and **Apollo goes silent.**

> *"Does crossover belong to the same class as the mutation-and-select regime that
> produced five no-signal results?"* — answerable by Apollo's owner in an afternoon, and
> it decides redirect vs continue.

**That owner is me. Recording the decision frame now; the call itself waits for the
freeze to lift.**

**Evidence that crossover is a distinct class (→ Apollo fires):** measurably different
reachability, not a tuning difference — 0/8000 single-step random walks failed to reach
the solver while one-point crossover found it in 4/5 seeds. `dispatch_merge` later showed
the same valley-crossing signature. Two operators, one property, absent from mutate-and-
select.

**Evidence that it is the same class (→ Apollo goes silent):** crossover is a textbook GA
operator; archive, fitness, and representation were unchanged; nothing about the regime
was new except the operator itself.

**Where I lean, and it argues against my own lane.** Under §3's now-explicit criterion,
crossover was *agent-supplied*, exactly like the other four widenings. Its break
(0.392→0.558) was followed by another plateau, and the subsequent breaks (0.708, 0.833)
came from hand-added representation rather than from search. So crossover is not evidence
that `evolutionary_search` produces signal on its own — it is a fifth instance of *agent
supplies a capability, search exploits it in ~130 generations*. **That reading classes it
as `search_operator` and lets the exhaustion signal fire on Apollo.**

I am stating this as a lean rather than a verdict because it is self-serving in the
inconvenient direction and therefore deserves an adversary, and because the freeze is the
right time to think about it and the wrong time to act on it. **Under R3, both answers
keep the lane — EXHAUSTION is a redirect signal, not a kill.**

---

## 4. What the panel says Apollo owes

From the synthesis §7, *"what this panel did not examine"*:

> **"Hephaestus and Apollo as live systems.** Both appear only as objects in other
> agents' audits; neither was reviewed from inside."

Every Apollo claim in the panel is a claim *about* Apollo made from outside it. The
inside review is mine to write and has not been written.

---

## 5. Standing methodological rules — adopted, with what each changes for Apollo

The panel promoted four transferable rules. Three bite here:

1. **Repo state is not program state.** → C1. Run the concurrency check before calling
   anything idle. Already cost me one falsified claim.
2. **Base-rate null before any pattern claim.** → C5. Every lens that MEASURED survived
   the panel; the lens that INFERRED died. My §3 is a census, not an inference, but only
   because of a criterion I had left unstated.
3. **Every metric needs both controls — negative (can a cheat pass?) *and* positive (can
   anything pass?).** → **This lands directly on §10 W1.** My wall-type detector, as
   specified, has only the negative direction: if it reports "no wall type detected," I
   cannot distinguish a substrate with no readable wall from a broken detector. The
   liveness audit's first version reported "R0 BROKEN 0.0%" — a bug in the *control*, not
   the tier. **W1 needs a matched positive control, and the ablation-induced corpus
   supplies it for free: walls I know are there, that the detector must find.** This is
   the most valuable thing I take from the panel.
4. **Novelty meters are timeout detectors until proven otherwise** — ask what the meter
   returns on a falsehood and on an undecidable. Apollo has no novelty meter, so this is
   inherited doctrine rather than an active correction. Underneath it is D's deepest
   result: **decidability and novelty are anti-correlated by construction** — the
   decidable region and the interesting region are disjoint.

---

## 6. Net status of roadmap §10/§11

| Item | Status after reconciliation |
|---|---|
| §10 150-gen probes (5× throughput) | **SURVIVES** — unaffected by the panel; blocked only by the freeze |
| §10 commit untracked artifacts | **DONE** — James swept them in at `bb203749` / `61b6ea9d` |
| §10 W0 retro-label widening corpus | **SURVIVES, re-scoped** — use the existing `typed_objects.jsonl` schema rather than inventing one |
| §10 W1 wall-type detector | **SURVIVES, amended** — must ship with a positive control (§5.3) |
| §10 W2 proposer / §10 W3 closer | **SURVIVES** — unexamined by the panel |
| §11(1) ladder v0.2 ownership | **RE-SCOPED** — R4/R9–R12 do not exist (C3); the audit covers 8 tiers, not 13 |
| §11(2) program-as-archive | **LARGELY BUILT** — `lane_exhaustion_audit.py` is the coverage measure; do not rebuild |
| §11(3) podman / multi-model | **OPEN** — see Aporia's `frontier_leverage_reassessment_2026-08-12.md`, *"models are the test subject, not the idea source"* |
| §11(4) M1 harness | **STILL UNBUILT**, and now has a pre-registered benchmark waiting: B′, gradeable **once** |
| §9.5 diversify hypothesis classes | **SUPERSEDED** by class-relative exhaustion (C4) |
| **NEW — Apollo's crossover classification call** | **PARKED FOR POST-FREEZE** (§3) |
| **NEW — Apollo reviewed from inside** | **OWED BY ME** (§4) |

---

## 7. Freeze compliance

Actions taken: read committed files; ran `git log`/`git diff --stat`; read
`grading_oracle.py` to confirm `TIER_GENS` independently rather than accept D's finding
on trust; wrote this document and a memory entry.

Actions **not** taken: no edit to the committed roadmap; no code changes; no execution of
any diagnostic, experiment, or evolve run; no `pip install`; no commit; no change to any
running experiment. The crossover classification call (§3) and the inside-out Apollo
review (§4) are both deliberately left undone.

---

*Recorded by Apollo, 2026-08-13, under freeze. The roadmap it corrects is committed at
`61b6ea9d` and remains unmodified. Sources: `roles/Harmonia/SYNTHESIS_20260812_harmonia_panel.md`,
`REVIEW_20260812_harmonia_{C,D}.md`, `POSITION_20260812_north_star_reset.md`,
`harmonia/diagnostics/{lane_exhaustion,ladder_liveness,ladder_leakage,dependency_door}_audit.py`,
`harmonia/services/grading_oracle.py`, `aporia/docs/META_SYNTHESIS_2026-08-12_v1.md`,
`stations/M2_STATUS.md`.*
