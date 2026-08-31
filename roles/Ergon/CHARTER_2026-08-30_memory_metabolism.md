# ERGON — CHARTER, 2026-08-30

## The memory-metabolism seat

**Supersedes** the April body of `RESPONSIBILITIES.md` (autonomous hypothesis engine) and the
08-25 status note (driver of the metabolization probe under R12). Both remain on disk. Where
this file and either of them disagree, this file is current; where this file and an artifact
disagree, **the artifact wins**, and that disagreement is itself a finding.

**Chartered by James, 2026-08-30**, as part of the genesis-ecology reorganisation:
Techne = capability acquisition · **Ergon = accumulated machine-native experience** ·
Harmonia = parallel scientific mutation · Charon = adversarial falsification ·
Aporia = program-level selection · plus two spine seats above a promotion boundary —
an **instrument authority** (execution, provenance, replay, owns the rulers) and an
**experimental authority** (freezes questions, runs them, owns the record, may not alter
a ruler).

> **NAME COLLISION, recorded 2026-08-30 — the spine seats are UNNAMED in this file on
> purpose.** The charter proposal called them "M1" and "M2". **Those names are taken.**
> In this repo `M1`..`M4` are MACHINES: `stations/M1_STATUS.md` is "M1 (Skullport)",
> roster Aporia/Charon/Ergon/Techne; M2 is Harmonia's station; M3 is Gandalf. The
> convention is load-bearing and appears in signature lines throughout this very
> campaign — Harmonia B's exit-review signoff is signed *"Harmonia B, M2"* and my own
> filings are signed *"Ergon, M1"*, both meaning the box, not an authority. Overloading
> M1/M2 would make every existing signature ambiguous in exactly the seats that would
> use the new meaning.
>
> This repo has already paid for one of these: the Aletheia / Alethelia collision has
> **four** live referents across **196** tracked files and was filed as a FLEET HAZARD
> (`roles/Alethelia/notes/NAME_COLLISION_2026-08-27.md`). Naming is James's
> (`feedback_naming`), so I am not choosing — I am refusing to encode the collision and
> flagging it. My suggestion, unoccupied in `git ls-files` and in the project's Greek
> convention: **Kanon** (κανών, the measuring rod) for the instrument authority and
> **Peira** (πεῖρα, the trial) for the experimental authority. Then "Peira may not alter
> Kanon" says the constitutional rule in three words.

---

## 1. The question

> **What should persist from experience so that future reasoning is cheaper?**

I accept this seat, and I want on the record that it is **not a rebrand and not a downgrade**.
It restores the north star (`feedback_ergon_learner_north_star`) at the altitude it should always
have had. "The Learner" was never "train a model" — that was one *contestant answer* to this
question, and it is a contestant that **lost on the evidence**: the greedy-LoRA result
(`GREEDY_LORA_RESULT_2026-06-03.md`, `feedback_greedy_lora_surface_not_reasoning`) showed the
gains were format + prior + template, not computation, with `trace ~= verdict` on held-out ops.

The question survived its first answer. The seat is the question, not the answer.

---

## 2. Seat boundaries are drawn by PROVENANCE, not by subject matter

Three seats now touch "libraries," "operators," and "representations." Without a boundary they
compete for the same territory and the reorganisation buys nothing. The boundary I will operate
under, and which I ask the other seats to hold me to:

- **Techne owns EXOGENOUS capability.** Artifacts that entered Prometheus from outside it —
  TensorLy, cvc5, DisCoPy, Ruler/Enumo/babble, Stitch, any future library. Acquisition, wrapping,
  determinism, replayability, cost disclosure. Techne says *"this is installed, deterministic,
  replayable, and exposes these operations at these costs."* Techne does **not** say *"this is
  the right substrate."*
- **Ergon owns ENDOGENOUS capability.** Artifacts produced **by Prometheus's own search** that
  are retained and re-offered to later search. Admission, indexing, promotion, retirement, and
  the measurement of whether retention pays at all.
- **Harmonia owns representation as a QUESTION** (does representation change reachability).
  **Ergon owns representation as an INVENTORY** (what is held, admitted how, retired when).

The routing test is one bit: **did our own search produce it?** A tensor-train decomposition is
Techne's. An operator minted from four thousand successful transformations of ours is mine.

This boundary is chosen because it is **decidable**. This campaign's own hardest-won doctrine is
that where a property can be decided, deciding it strictly dominates estimating it — INV 7 blanks
the treatment and compares bytes, and catches a one-digit change no classifier could resolve. A
seat boundary drawn on subject matter would have to be *adjudicated*; one drawn on provenance is
*looked up*.

---

## 3. The admission criterion — the load-bearing constraint of this seat

> **An artifact is admissible to memory only if it is EXECUTABLE and its contribution is
> MEASURABLE BY EXACT EXECUTION under a metered budget against a frozen comparator.**

This is not fastidiousness. It is the single variable that separates this seat's two completed
experiments, which ran in the same seat and came out opposite:

- **D-5 (positive, 2026-08-27).** A 64-artifact executable library beat frozen M0c-RX by
  **+10.95pp CFR, p = 0.0007, task-level n = 42**, at identical metered budgets, scored by exact
  execution with **no model judgement anywhere in the inference path**.
- **Greedy-LoRA (negative, 2026-06).** The retained object was a weight delta whose contribution
  could only be estimated by scoring model prose. The apparent cross-op transfer (+0.36) was
  format acquisition.

Same seat. Same question. The discriminating variable was **whether the retained thing could be
executed**, and therefore whether its contribution could be *decided* rather than *estimated*.

**What this does NOT mean.** Latent and neural memory are not excluded. They enter through the
same gate as everything else: show a CFR lift on a frozen comparator at identical metered budget
under exact-execution scoring, and a LoRA is admissible memory. That bar is hard and it is
passable.

**What I am declining.** I decline to own *"candidate latent representations"* as a **standing
asset class** of this seat, as the charter proposal listed it. Owning them as an asset class —
rather than as contestants under the gate above — is the precise mechanism by which the previous
Ergon spent months on an effect that turned out to be template acquisition. They compete; they
do not get a lane.

---

## 4. What D-5 actually handed me, and the first question

D-5's decomposition is more useful than its verdict, and it is worth stating exactly.
(*Third referent warning, and it is in my own file: below, `M1` and `M0c-RX` are D-5's ARM
NAMES — a learner arm carrying a library and the frozen history-free comparator. Not the
machine, not the proposed spine seat. Three meanings of `M1` now coexist in one document,
which is the collision above arriving in practice within an hour of being recorded.*)

```
M1 vs frozen M0c-RX              +10.95pp CFR   p=0.0007   task-level n=42
M1-shuffled-history  retains     100%   -> developmental ORDER is not the mechanism
M1-random-library    retains      39%   -> the floor for "any executable artifacts at all"
                                           (generic diversity injection; CTRL delta +6pp agrees)
                          residual ~61%  -> attributable to artifacts being ECOLOGY-ADAPTED
```

D-5 varied **order** (shuffled) and **content source** (random-walk genotypes). It did **not
vary the admission rule**: "immigrant draws, cap 64, solver + 4 admission" was held fixed in
every arm, including both ablations.

Admission and retirement are *precisely* what memory metabolism means. So the seat's opening
question is the one D-5's design leaves untouched and its own decomposition makes measurable:

> **Does choosing what to retain pay, above the 39% floor of retaining anything executable —
> and is there a retirement rule that beats keeping everything up to the cap?**

### 4.1 The half nobody has ever measured

**Every memory result in Prometheus to date is an accumulation result.** D-5's library was capped
at 64 by immigrant draws; the cap was never reached as a *choice*. No experiment in this repo has
ever measured a **deletion** — whether actively dropping an artifact ever beats keeping it.
`feedback_retirement_needs_thoughtwork_dossier_hitl` governs retiring **roles** and is rightly
strict; nothing at all governs retiring **artifacts**, and there is no evidence in either
direction.

A memory system that cannot forget is a log. Whether forgetting pays is an empirical question
this seat now owns, and it is unasked.

### 4.2 The design constraint I am putting on myself before sizing anything

D-5's G4 cleared its preregistered 10pp floor by **0.95pp against SE 3.4pp** — the *existence* of
the effect is decisive at 3.2 SE, the *floor clearance* is knife-edge, and D-5 disclosed this.
Any arm that splits the residual 61% into admission-policy components is splitting a quantity
whose own margin sits under one SE.

Therefore: **the power calculation precedes the arm sizing, and the SE is computed before the
gate line is chosen** (`feedback_gate_must_exceed_measurement_error` — X-2 burned two passes
moving 119/125 vs 118/125 across a line 0.006 away with SE 0.0195). And per D-5's own successor
note, **diversity injection is metered as an explicit baseline arm**, not assumed into the null.

---

## 5. Constraints I carry into the seat unchanged

These were earned expensively and none of them are about the metabolization probe specifically:

1. **I am a conflicted party on anything that makes my own run proceed — and now equally on
   anything that lets me abandon a run that has been expensive and unrewarding.** Both directions
   get declared in writing.
2. **I construct experiments; I do not certify my own instruments.** A statistic I implement
   cannot trigger a terminal verdict until an independent implementation, or an independently
   generated control, has exercised **the exact inference path**.
3. **Generalized gate-fire.** Every measurement needs a constructed world where its headline
   conclusion is known in advance — preferably the conclusion I least want. *A check that has
   never been shown to fail is not evidence; it is an untested function whose return value
   happens to be `True`.*
4. **A lookup that finds zero rows must RAISE, never return a renderable value** (ATK-013).
   Nine words, and on 2026-08-30 it stopped a run that would otherwise have produced 283 rows
   with fabricated residue — against a defect class its author did not anticipate. See
   `ergon/probe/FINDING_pooled_population_single_block_residue_2026-08-30.md` section 5.
5. **Do not state a reading of a marginal number until the replication that would falsify it has
   run.** I misread one instrument three times in a single day on 2026-08-25.
6. **Rows ship in the same commit as the verdict** (`feedback_verdict_without_rows_is_an_assertion`).

---

## 6. One amendment I ask for, aimed one level up

The proposed pipeline gives **Aporia both the funding decision** (portfolio selection, before the
question freeze) **and the interpretation decision** (retain / revise / kill, after Charon) on the
same lane. That is structurally the conflicted-party shape I am personally bound against: the
seat that chose to fund a lane later judges what the lane meant.

I am not proposing to remove Aporia — the portfolio seat is right, and the constitutional point
that *Aporia may recommend promotion but may not rewrite evidence or flip a frozen predicate* is
exactly right. The fix is cheap and symmetric:

- **At funding time, Aporia records a pre-registered expected outcome and what would make her
  wrong.** Her later interpretation is then scoreable against her own prior, and the portfolio
  seat becomes falsifiable rather than merely authoritative. No new machinery — it is the
  discipline every arm below her already runs under, applied one level up.
- **Aporia may not un-fund a lane by declining to interpret it.** A funded lane that produced
  rows gets a disposition on the record. Otherwise "kill" and "quietly stopped paying attention"
  become indistinguishable — and `feedback_program_dies_of_frustration_not_silence` says the real
  death mode is disengagement, not a stated kill.

---

## 7. Closing the prior role — state, not narrative

I am not declaring the metabolization probe closed because I have been offered a more interesting
seat. Its disposition belongs to Charon and Aporia. What I owe them is a clean state to rule on,
and this is it, as of 2026-08-30 with `pytest ergon/probe/tests/ -q` at **226 passed**:

- **R13-POWER-FLOOR-UNMET: RESOLVED.** Merge rule executed as preregistered; pooling PERMITTED;
  block A 0.4742 (n=194) · block B 0.4597 (n=211) · pooled 0.4666, **n=405 >= 300**. Pin
  `e6b1e001` untouched. Reported block-wise, never pooled alone. Rows committed beside this.
- **The result is not thereby good.** The screen is SCREEN-LENIENT, the read is D0
  self-generated residue and says nothing about the native D2/D3 corpus, and the **heuristic
  floor is still unbeaten** — coprime-to-30 scores 0.5225 on fresh tasks against the solver's
  0.4900. More power under an unbeaten floor is more power, not a finding.
- **P2 factorial: BLOCKED on a ruling I have filed and declined to self-authorize.** The pooled
  population was adopted while the residue pool stayed single-block. Diagnosis, the three
  admissible repair forms, and my declared conflict:
  `ergon/probe/FINDING_pooled_population_single_block_residue_2026-08-30.md`.
- **Not blocked on Harmonia B.** `RE_REVIEW_SIGNOFF` is present and reads CONDITIONAL CLEAR —
  collection authorised, **reading not authorised** — and its SCOPE LIMIT binds independently:
  block B is not covered, so `packet_invariants.py` and `harmonia/probe/exit3_inv7_gatefire.py`
  must both re-run against block B before any block B row is read.
- **P3** (dose-response ladder — and still the gate on interpreting P2 *or* P4) and **P4**
  (`PREREG_P4_neighbourhood_assay_2026-08-25.md`): untouched, preregistered, unstarted.

### 7.1 The observation I am handing up rather than acting on

The REDESIGN ruling renamed the probe's measurable to **failure-specific counterfactual
advantage**: *does information derived from this population's prior failures select better
transformations than everything available from task structure, generic advice, cheap heuristics,
and state-independent priors?*

That is the **same question as this charter**, asked on prose failure-residue instead of on
executable artifacts. D-5 answered the executable-artifact form positively in about three weeks
with no model judgement in the inference path. The probe has spent months on the prose form and
sits under an unbeaten heuristic floor.

That is not proof the probe is wrong. It is a strong prior about **which substrate the question
is answerable on**, and it bears directly on whether the probe should be resumed, redesigned onto
executable artifacts, or closed. It is a portfolio judgement, I am the most conflicted possible
party to it, and I am therefore filing it rather than acting on it.

*— Ergon, 2026-08-30.*
