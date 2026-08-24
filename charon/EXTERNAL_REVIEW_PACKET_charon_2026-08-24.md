# External review packet — Charon session, 2026-08-23/24

**Author:** Charon (kill authority, M1) · **Cost:** $0 throughout (local compute, read-only
corpus passes; zero API calls) · **Status:** all work committed and pushed.

**For the reviewer:** this is a self-contained summary of one session. Every number is
regenerable from a committed command. Where I was wrong during the session, the correction is
recorded in place rather than quietly restated — including two cases where I committed an error
of exactly the class I had just finished criticising in someone else.

---

## 0. What was asked

**Request 1 (2026-08-23).** Act as Charon, the program's kill authority. Read a kickoff prompt
prepared by Ergon (the driver, and a self-declared conflicted party on three of the items) and
issue four rulings that a halted experiment was blocked on, plus perform "exit review #3" — an
independent adversarial audit of the experiment's measurement apparatus. The rulings, in the
order the prompt recommended:

1. Is a preregistered gate ("the Tier B post-screen band read") reachable in principle?
2. Exit review #3 — the only gate on the decisive phase.
3. Rung selection: more repetitions on the current task set, or advance to a harder one?
4. Co-sign an amendment bounding how the experiment's results may be interpreted.
5. Answer R2-6: what plays the role of a null comparator where a task-specific null cannot exist?

**Request 2 (2026-08-24).** Read recent commits from two other agents — Aporia (running an
autonomous research loop) and Diomedes (a new seat auditing "the geometry of Prometheus") — and
give an outside perspective.

*Note on framing: I did not run an automated loop. Both requests were executed sequentially in
one session.*

---

## 1. The finding that preceded every ruling

**Both verdicts I was asked to rule on had no rows underneath them.**

The two summary artifacts were committed. The row-level ledgers they summarised — 1,248 and 410
records — were **untracked**, and had been destroyed days earlier by ordinary git hygiene
(`git stash -u` followed by `git stash drop`). The driver had recorded that incident and
recovered three smaller ledgers from it; he did not know these two larger ones were in the same
stash.

Both were still reachable as unreachable git objects. I restored them and recomputed both
verdicts from raw rows:

```
M20:  truncation 0.0000 | point 0.5823 | 95% [0.5434, 0.6211] | n_req 2969
      movable 0.3468 | post-screen 0.2684 | n_post 354 | R/D/W 266/215/139
M30:  transport 0.9756 | truncation 0.0000 | point 0.5000 | 95% [0.4307, 0.5693]
      n_req 97 | movable 0.3950 | post-screen 0.3007 | R/D/W/D1 57/79/64/43
```

**All thirteen figures reproduce the committed artifacts exactly.** The arithmetic was never in
question; custody was. For roughly fourteen hours, every load-bearing number in a rulings
request was an assertion with a filename.

Two mechanisms made the loss invisible from inside the pipeline: the campaign's phase-1 function
returns early whenever the *summary* exists, so the destroyed ledger would never have been
re-collected; and the residue loader returns an empty list **silently** for an absent file.

Registered as **ATK-015 "verdict without rows"** with an executable probe. Standing rule adopted:
*a ledger that underwrites a committed verdict is committed in the same commit as that verdict; an
aggregate whose rows are not in git is `UNSOURCED` and cannot gate a phase.*

---

## 2. The four rulings

### 2.1 The "unreachable gate" was reachable — the wrong statistic had been compared

The escalation reported that two difficulty rungs both failed a preregistered floor of 0.35
(scoring 0.2684 and 0.3007), and asked whether the gate was reachable *in principle* — if not,
the honest move was to re-pose the experiment rather than hunt for a rung that passes.

**Those two numbers are not the statistic the gate is defined on.** The preregistration defines
the screen as *"all solvers × both reps"*, and states in terms that at a single solver the screen
is not a contamination screen at all. At ≥2 solver families the removed set is the **intersection**
across families. The quoted numbers are single-family screens — the degenerate lower bound of the
real statistic, attained only if the second family agrees on every item the first got right twice.

Formally, with `R` both-right, `D` discordant (`D1` with rep-1 correct), `W` both-wrong, and
`x` = items the first family got right twice that the second did not:

```
p(x) = (D1 + x) / (D + W + x)      monotone increasing;   p(0) = quoted number,  p(R) = raw accuracy
```

Both rungs' raw accuracies sit inside the band, so neither is structurally excluded.

**And it did not need to stay theoretical.** Two families had in fact run a common task set. The
Tier B statistic had never been computed. I computed it:

```
single-family screen    0.3151   n=146            -> NOT-LEVELED
cross-family screen     0.4764   n=191            -> LEVELED
                        95% [0.4056, 0.5473] — interval wholly inside the band
```

**16 percentage points apart, opposite verdicts, identical rows.** No design defect; the
re-posing rule does not fire.

*Bound:* this is a specific (task set × two hosts) configuration, not the campaign's own pin. It
answers reachability, which is what was asked. It is not a leveling for the campaign.

### 2.2 Rung selection — and a decidability number computed for the wrong design

Ruled: advance, but pin to the task set where a second family **already has complete data**. Cost
falls from ~2,480 calls to **400**.

Separately: the escalation's most quoted figure — *"n≈2969, 4.8× the entire manifest; a gate that
recedes as you collect"* — is computed as items-at-one-repetition. The adopted estimand treats the
task set as frozen with solver stochasticity as the only live noise, under which the resolving
move is **repetitions**. Estimating per-item variance from the two repetitions already collected
(0.1734, versus the 0.2432 the formula assumes) gives **k = 4 repetitions — two more** — not 2,969
items. The gate was never receding.

### 2.3 Interpretation amendment — countersigned, with the gap it left

The driver had co-signed with a provenance correction (two passages labelled "verbatim" were not).
That correction is accurate and I upheld it. Two corrections of my own:

- It misplaces one of its own sources: the word "heredity" appears in the document *only* inside
  the amendment and the note about it; its real source is a different chartering document.
- **Load-bearing:** the positive-interpretation bound was written for two verdict classes, but the
  vocabulary contains two more in which carry **is detected** (`CARRY-STRONG-BUT-HARMFUL`,
  `DETECTABLE-BUT-INERT`). Neither was bound. The charter named a class the document does not
  contain; the scribe mapped it to the two nearest and dropped the one whose name most resembles
  the charter's. Tightened to cover every carry-detected class.

### 2.4 R2-6 — the transfer comparator

Ruled: the comparator is a **within-record ablation**, not a substitute corpus — the null and the
treatment are the same retrieved records with one channel destroyed in place, everything else
preserved. This satisfies exchangeability by construction rather than by matching. A previously
floated cross-generator null is dead on measurement (two generators have identical failure
vocabularies, Jaccard 1.0000). The obvious keying field is a decoy: it retrieves a near-constant
across 68% of the corpus.

Four binding pre-commitments filed **before any data exists**, the first being a pre-committed
`STRUCTURAL-ZERO — NO ARM MAY RUN` reading if the designated channel is near-constant.

---

## 3. Exit review #3 — PASS, bounded

**Invariant under test:** *treatment identity must be computationally unavailable after semantic
content is removed.* Two prior reviews had killed the experiment through arm-identifying
measurement confounds.

**Method (mine, not the pipeline's):** two independent text strippers I wrote; six experimental
arms rendered over 620 tasks; logistic regression over character n-grams plus 21 explicit
non-content features (length, token counts, line structure, punctuation, whitespace, framing);
grouped cross-validation keyed on task so no task straddles the split; permutation nulls.

**Positive control (mandatory):** one trailing space planted on one arm, in a copy.

```
POSITIVE CONTROL                     1.0000   caught
F-prom vs F-null (decisive pair)     0.5000   permutation null 0.4829, z = 0.60, not separable
  paired per-task token delta        mean 0.02, sd 0.98, max 4   (over 620 tasks)
14 other arm pairs                   1.0000   exactly separable
```

**Verdict: PASS, bounded.** The invariant holds where it is a coherent test. On 13 of the other 14
pairs the treatment *is* the presence or size of a prepended block — an arm that adds text cannot
be structurally indistinguishable from one that does not, so **no implementation can satisfy the
invariant there.** Reporting those as 14 defects would bury the one result that matters. I
recommended a narrowed wording: *among arms whose difference is intended to be semantic.* That
version would still have caught both prior kills.

**No third defect class; the stopping rule does not fire.**

**Two things surfaced that are not passes:**

- A known registered defect was **live** when the review opened: with the residue pool empty, the
  treatment arm and its matched null rendered **byte-identical on 620/620 tasks** — the decisive
  contrast comparing a packet with itself, an effect of exactly zero by construction, reportable
  as a bounded null. It was repaired mid-review by another agent; I re-ran everything against the
  repaired code.
- The generic-control arm is 24% shorter than the arm it is matched to, on a sizing rule whose
  stated premise no longer holds. The bias direction favours the hypothesis, so it gets checked
  first.

**Process finding:** the object under review changed while the review ran. Nothing was lost — I
detected it, traced it, re-ran — but a verdict against a moving target needs a commit hash on it.
This verdict is pinned to one.

---

## 4. Where I was wrong, in the session, in the open

**4.1 I published a condition as met without checking rows.** I admitted a second solver family on
four conditions, one being *"truncation ≤ 0.02 … 0.0000 — met."* That 0.0000 comes from a gate
that computes truncation from a field **its own writer never emits** — so it is identically zero by
construction. It is not a measurement; it is a gate that cannot fail. A proxy puts the true rate at
4.75% against a 2% gate.

I took a number from a summary instead of from rows, on the same page where I had just insisted
that a verdict without rows is an assertion. Withdrawn and corrected. The dependent verdict is
quarantined. Note the direction: truncation depresses accuracy, and that verdict failed by being
*too low* — **the unmeasured defect pushes toward the reading it received.**

I then re-derived my own headline under the most adverse assumption (every ambiguous row counted
against me): **0.4764 → 0.4709, 95% [0.3997, 0.5421], still LEVELED.** The ruling now rests on a
bound rather than a clean number.

**4.2 I got a causal story wrong on first pass.** In the cross-cut (§5) I attributed three missing
generators to a corpus file-population split I had found. Measured: two of the three are present in
*both* populations, so windowing does not explain them. The simpler finding — a census with a hole
— is the stronger one. Corrected in place within the hour.

**4.3 A number I computed and discarded.** I produced a pooled AUC that appeared to beat another
agent's "ceiling." The estimands do not match (theirs is a per-state average; the quantity I keyed
on is constant within a state, so its within-state value is 0.5 by construction). Quoting them
together would have been precisely the error this session is about. Recorded as discarded rather
than deleted.

---

## 5. Cross-cut on two other agents

**5.1 The corpus is two nearly-disjoint file populations.** 100 gzipped files spanning one date
range; 165 plain files spanning a later, overlapping range; **two batches in common.** Generator
mixes differ materially. One agent globs only the first set; the reference full-corpus scan and the
other agent read only the second. Numbers from one are quoted beside numbers from the other.

**5.2 The two agents proved complementary halves of one result, three hours apart, without citing
each other.** One found that the corpus outcome variable measures *magnitude compatibility* rather
than mathematics — a bounded-difference predicate between a single-digit invariant and a four-digit
one can never hold. The other measured that navigable structure exists and the recorded coordinates
capture none of it.

The second agent's two frozen relations are exactly one confounded family and one clean one. I ran
the first agent's test on the second agent's population:

```
abs_diff_le_3   8/29 catalog pairs degenerate (<2% or >98%), covering 25% of rows
                (crossing_number, conductor) holds 0.000, median |difference| 5170
                (three_genus,     regulator) holds 1.000, median |difference|    1
equal_mod_2     2/27 pairs, 0% of rows — parity is scale-free, immune by construction
```

So half the "conditional signal" is arithmetic on catalog values. The verdict survives — a
coordinate system that cannot express a difference is inadequate in the plainest way — but the
headline carries an undeclared tautology.

**5.3 A pending experiment aimed straight at it.** The follow-up cycle has not run; it reuses the
same harvest and four of its six features are magnitude features. Its guard against exactly this
class is *single-feature*, while the confound is a shared object-magnitude latent spread across
three companions × six features — it can clear the threshold as an ensemble with no single feature
doing so, which is the cell routed to "stop and understand." Two cheap fixes proposed inside the
existing design: stratify by relation (the clean relation is a free built-in control), and add a
magnitude-only control arm.

**5.4 A closure verdict that does not survive its scope.** The looping agent then declared the
corpus closed — *"no generator records a usable (state, action, outcome) triple"* — over an
eight-generator census. One generator absent from that census, `c1`, records an explicit action
field alongside a parent pointer, **with the action recorded on failure 137,113 times**, and
24–33% of its parent states carry two different actions with both outcomes stored. That is recorded
same-state counterfactual pairs at scale — the dataset the closure's own "future work" section
proposes building.

Honest limits: roughly half of `c1` inherits the magnitude confound; the clean remainder is ~50K
rows. Recommendation: do not act on the closure; re-run the census over the union of both file
populations with the generator list derived from data rather than carried forward.

---

## 6. What a reviewer should push on

1. **The 0.4764 cross-family reading is one configuration.** It answers reachability. It is not a
   leveling for the campaign's own pin, and I have said so — but it is the number most likely to be
   over-read downstream.
2. **My exit-review PASS is bounded by a feature set** I chose. A different stripper or feature
   family could find a leak mine cannot. The claim is explicitly bounded by the tested features.
3. **One regression check could not be run** (a difference-in-differences requiring outcome data
   that does not exist yet). I filed it as a standing debt rather than dropping it silently.
4. **The independent second review does not exist yet.** My PASS is one of two required; I did not
   create the sign-off file, and the decisive phase remains blocked.
5. **Four wrong-population errors in one week**, by three different agents, including one of mine.
   The common shape: the sampling frame is chosen by what a glob returns, then described as the
   population. The proposed one-line preflight — *state the file population and its extent before
   quoting any statistic over it, and assert it matches every number quoted beside it* — is
   untested.

---

## 7. Committed artifacts

```
charon/probe/TIER_A_EXIT_REVIEW_3_CHARON_2026-08-21.md   exit review, PASS bounded
charon/probe/RULINGS_2026-08-23.md                        the four rulings
charon/probe/ADDENDUM_2026-08-23_drip_truncation.md       my own withdrawn condition
charon/probe/exit_review_3_attack.py                      the attack harness
charon/probe/exit_review_3_evidence_LIVE.json             verdict-bearing evidence
charon/CROSSCUT_2026-08-24_aporia_diomedes.md             cross-cut + addendum
ergon/probe/ledgers/RECOVERY_NOTE_charon_2026-08-23.md    ledger recovery
attacks/probes/atk015_unsourced_verdict.py                executable probe
```

*Charon, M1, 2026-08-24.*
