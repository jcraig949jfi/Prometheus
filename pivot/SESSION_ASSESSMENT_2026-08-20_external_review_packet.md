# Prometheus — Session Assessment & External Review Packet

**Date:** 2026-08-20 · **Author:** Hephaestus (Claude Fable 5, M3 — the fleet's one non-Opus
seat; meta-thinker / HITL wingman for this session) · **Audience:** James, the fleet, and an
**external AI reviewer with no prior context** — Part 0 exists for the latter.
**Status:** assessment, not doctrine. Everything here is checkable against the repo.

---

## PART 0 — BACKGROUND FOR A COLD REVIEWER

**What Prometheus is.** A five-month-old private research program run by one human (James)
across four home-lab machines (M1–M4), operated almost entirely by long-running AI agent
sessions with named charters — Aporia (void detection / meta-synthesis), Techne (toolsmith /
substrate), Charon (falsification battery / kill authority), Ergon (the Learner), Apollo
(evolutionary search), Harmonia A–D (measurement fleet, four deliberately non-overlapping
lenses), Hephaestus (the forge). Agents coordinate through **git commits** — that is the real
bus; a Postgres message bus exists and has carried zero production messages.

**The founding bet.** Everyone else treats LLM hallucination as a defect to suppress;
Prometheus treats it as *mutation* and tries to build the *selection pressure*: an automated
falsification machine that tries to kill every claim and records exactly how each died. The
accumulated "kill geometry" was hypothesised to become a navigable gradient a learner could
climb toward genuine mathematical discovery. Mathematics was chosen because it has
unambiguous ground truth.

**Where that stood before this session** (from the August 12 program-wide reassessment): the
program had generated 658M records and 360M kills, 12,666 markdown documents, 2.2M lines of
Python — against **one** verified capability-typed training object, **zero** completed
learning loops, and **zero** novel discoveries. The promotion pipeline had never promoted
(its celebrated "2,351 discoveries" was a fossil of a superseded formula). The
navigable-gradient object was never computed (`kill_vector` 0% populated). Eight architectural
eras in fourteen weeks, each ended by an honest kill, each era's best artifact orphaned.

**James's diagnosis, which became this phase's frame:** in Darwinian terms the program has
mutation ✅, selection ✅✅, measurement ✅✅✅ — and **inheritance ❌**. Nothing a failed attempt
learned has ever changed a descendant. Without inheritance, evolution never starts.

**The constitutional rules that follow** (James, 2026-08-12/13):
1. **The heredity rule** — *no new architecture until one failure produces one verified
   improvement.*
2. **Two controls per meter** — every instrument ships a positive control (can something good
   pass?) and a cheat control (can something fake fail?), or its output is inadmissible.
3. **Iterate on free, reserve paid for the decisive run** (added 08-19 after a $10 API budget
   went on iterations rather than the experiment).

**The decisive experiment.** The *Metabolization Probe*: give a capable model the program's
actual failure records for a problem and measure — against controls — whether it does better
next attempt. Arms: **F0** (nothing) · **F-oracle** (ground-truth diagnosis, the ceiling) ·
**F-prom** (what Prometheus actually recorded) · **F-null** (adversarially matched but
*mismatched* residue) · **F-generic** (generic "be careful" advice) · **F-answer**
(instrumentation control). Primary quantity **Δ_carry = F-prom − F-null**. Both outcomes are
wins: carry means the corpus has value; no carry means the records are exhaust and we know
what richer records must look like.

**Two vocabulary items a reviewer needs:** *E1* = read the source, *E3* = executed it this
session (the fleet tags claims this way after discovering that five agents citing one summary
looks like corroboration but is one measurement with five pointers). *Preregistration* here is
literal: a binding committed document that fixes arms, thresholds and kill conditions before
any data exists.

---

## PART 1 — THIS SESSION'S CHARTER

James's brief to me (2026-08-12, verbatim in substance): *step back and assess the whole
program from as many perspectives as possible; enumerate them; integrate the other agents'
assessments as they arrive; no linear thinking — there is not one correct path forward but
many exploratory paths, possibly parallel; be the architect that is the HITL wingman.*

Operationally that became four jobs, all of which ran:
1. **Assess** — a 14-domain parallel code survey plus integration of seven agent assessments
   into a meta-assessment with a divergence file (where I contradict the fleet) placed first.
2. **Design** — turn the fleet's convergent instinct into a falsifiable experiment: the probe
   spec, hardened through two adversarial rounds plus James's own peer review.
3. **Delegate** — write and dispatch role-scoped prompts, one seat at a time, verifying each
   deliverable on origin before dispatching the next.
4. **Execute my own contract** — the forge's outstanding debt, on the same terms I set for
   everyone else.

**Standing constraint on me:** the residue being priced by the probe is substantially
forge-sourced, so I am the **declared-conflicted supplier**. I do not grade, do not sign, and
do not adjudicate verdicts. That declaration was made before any of it started and has been
enforced by the others as well as by me.

---

## PART 2 — WHAT EACH SEAT WAS ASKED TO DO, AND WHAT CAME BACK

### Ergon (M1) — the Learner; drives the probe
**Asked:** draft the binding preregistration; then execute it — clear conditions, pre-pass,
controls, pilot.
**Delivered:** a preregistration that *measured before designing* (found the June corpus
manifest silently imbalanced 80/80/…/14, and that the old eval harness **logged scores, not
residue** — the consumption disease at the harness level). Computed statistical power rather
than asserting it. Then, across ~10 sessions: killed **three difficulty axes** with clean
negatives (operand magnitude — non-monotone; answer-space width — fixed three defects, changed
no difficulty; compositional depth 1→20 — a 20-step chain solved 40/40, correlation *positive*);
found a working fourth (deception structure, 57.5pp range); built the first monotone rung set
in program history; **and stopped the experiment twice at preregistered gates** rather than
produce a defensible-looking number — HEADROOM-FAILURE, and R7 failing at two strata.
**Its own defects, self-reported:** a token cap that was measuring itself; unpaced dispatch;
a silent no-op patch that ran the wrong family for a whole overnight run (now raises instead
of lying).
**Ended at:** the pilot ran clean — `F-answer 93.8% ≫ F-oracle 48.6% > F-prom 45.9% > F0 43.2%
> F-null 36.3%`, the spec's predicted ladder order on real residue for the first time.
Δ_carry = +9.6pp, CI [−0.7, +19.2] — routes nothing, classifies nothing. **Then it was
withdrawn** (see Charon).

### Charon (M1) — kill authority
**Asked:** author the F-generic control clean-room *before* seeing any residue; co-sign or
refuse the preregistration; build F-null; later, rule on the leveling band; later still,
review Tier-A exit.
**Delivered:** clean-room attestation, then a co-sign **with six conditions**, two material.
Built F-null through two documented failures — including one where *its own fix made things
worse* (nearest-neighbour matching is regression to the mean, "a matching heuristic
manufactured the signature it was built to remove"). Declared a **twelfth marginal** nobody
specified (verdict polarity: the residue pool ran 26:1 negative against a 50/50 task set).
Ruled **D1/D2 INADMISSIBLE-NO-FAIR-NULL** after testing both horns — break the relation and
the null leaves the domain; preserve the topic and the null is drawn from what F-prom *is*.
**Its through-line, the round's single most useful sentence:** every material defect found that
day was *the same defect at a different distance* — a selection relation that is not
task-specific. Hence **Δ_carry is interpretable at D0 alone**.
**Then it killed the pilot:** TIER-A-EXIT-FAIL. The pilot rendered F-prom with `.body` and
F-null with `.packet.text`, so F-null shipped a JSON header and F-prom did not — classifier
**1.0000** as deployed (perfectly separable) versus 0.4417 as validated. The arithmetic closed
exactly: header = 281.9 tokens; the pilot logged an F-null−F-prom gap of 282.4. The solver
could condition on arm identity without reading a word of residue.

### Harmonia B (M2) — meter integrity
**Asked:** co-sign or refuse; build the R3 control battery; later rule on the band; later
review Tier-A exit.
**Delivered:** the third signature (making the prereg binding), with Charon's two material
remedies recorded as binding-conditions-before-arms. Re-derived the verdict-class partition
exhaustively — complete and disjoint *after* Charon's amendments, **genuinely gapped before**.
Calibrated every control two-sided as OC curves, which **killed its own first cheat rule** (20%
clean-world false-alarm). On the band: measured that the point rule beats the interval rule by
a wide margin — *"I expected an interval rule to beat the point rule. It does not… Recorded
rather than quietly dropped."* Its **cheat control killed the band itself**: a bimodal task set
with mean dead-centre and zero movable items was accepted by all six candidate rules, so the
band gained a dispersion term.
**Then it also failed Tier-A exit, independently and on different grounds:** R7 layer (a) was
never executed (a function imported and never called); and **F-oracle > F0 fails** (+5.5pp,
p=0.31) — meaning the only rung clearing significance was the instrumentation control. It also
ruled the token-matching deviation **not conservative**, with a difference-in-differences
showing that in the longest tercile **F-prom gives exactly zero benefit over F0** — the entire
apparent gain was F-null being *harmed* by longer packets.

### Apollo (M2) — evolutionary search
**Asked:** supply the Tier-A ablation-wall corpus; later, run the type-bridge **metabolic
cycle** — the heredity rule's first-cycle candidate.
**Delivered (corpus):** 26 walls / 4 classes + 2 controls, with a validator that *enforces*
the cause-not-fix separation and a planted-violation self-test. Three of its own wall specs
were killed by their own telemetry before release — including the finding that **plateau
telemetry cannot distinguish "capability absent" from "capability present but mis-wired."**
**Delivered (cycle):** a preregistered 2×2 × 5 seeds × 400 generations, and it **corrected the
brief**: the bridging op had already been forged in June, so "forge the bridge" was discharged
two months ago — what had never been done is *reproduce it*, which is the step heredity cares
about. Result:

| | crossover off | crossover on |
|---|---|---|
| **bridge absent** | 0/5 (reproduces T₀) | 0/5 |
| **bridge present** | 0/5 | **3/5** |

A clean interaction: neither factor alone produces a cross-tier organism in 400 generations;
together they do. **And the finding nobody was looking for — a validated result decayed on the
shelf:** mean generations to discovery went **30 (June) → 255 (today), 8.6× slower**, caused by
measured substrate drift. *"The June 4/5 would still be cited today had this cycle not re-run
it."*

### Harmonia C (M2) — counterfactual / base-rate lens *(reassigned from Aporia)*
**Asked:** the kill-resurrection retrodiction, re-keyed on representability; and the repair
ledger.
**Delivered — and this is the session's most consequential result:** **0 of 92 historical kills
resurrect** (95% upper bound 3.3%); 176/176 records representable — *the blind band is empty*.
Structural cause found in code: the verdict is content-determined at emit (`SHADOW_CATALOG if
holds else REJECTED`), shared by 43 of 48 generators. **A kill is a predicate result, not a
dispatch outcome.** The pre-committed reading fires: the router thesis does not explain the
nulls. **But the survivors are the real finding** — 84/84 non-promoted survivor records
re-evaluate TRUE at 45.9% observed against a 46.1% random-pairing null: **dead on the chance
floor.** So the probe is not pricing a mislabeled asset; it is pricing a correctly-labeled
*chance-level* one. Repair ledger: 8 repairs, 3 with preregistered predictions, all 3 right
about capability, **0 followed by a consumer consuming** — my own earlier inference, now a
typed table. Also a correction owed to Harmonia A, delivered.

### Harmonia D (M2) — permanence / coverage lens *(reassigned from Aporia)*
**Asked:** the detector-band audit — what the substrate emits vs what the battery can
represent.
**Delivered:** enumerated rather than sampled — all 56 generator classes instantiated and
executed, 7,914 records classified, weighted by 658M lifetime records, with both controls
asserted in code (its cheat control caught a case that would have inflated the headline from
36.4% to ~44%). Two findings: `verify()`'s dispatch has an **empty intersection** with
substrate claim kinds — disjoint ontologies, the battery has never seen a Theseus record; and
the deciding number is not a coverage number at all — **99.98% of lifetime records were
verdicted by the generator that authored them.**

### Hephaestus (M3) — me
**Asked (by myself, on the same terms):** grade the composed engine on the independent oracle;
close the forge's E0 claim.
**Delivered:** first, a finding *before* the measurement — the **+11pp/+32pp claim, cited
program-wide as the only demonstrated metabolization, had no computation anywhere in the
repository.** Input data existed; no ablation script, no artifact. Prose in five documents,
computed in none. Then I wrote the ablation (my own knockout protocol, applied to my own claim,
55 days after my own journal named it the top priority) and **it reproduces**: `prob_fallacy`
+11.1pp on R3, `temporal` +32.1pp on R4, `causal` **−6.2pp** on R5 (the engine doctrine calls
decorative — confirmed *harmful*), each **perfectly tier-localized at 0.0pp elsewhere**.
**What failed:** the oracle cannot grade the engine — it expects a free-answer generator over
symbolic probes; the engine is a multiple-choice scorer. An adapter must synthesize the
candidate list, and **the distractor policy is the measurement** — set by the conflicted party.
I declined and referred the fix (an oracle *scorer mode* with a meter-owned distractor policy)
to Harmonia. "One import away" was false and is corrected in place.

---

## PART 3 — THE ELI5

Imagine a laboratory that has spent five months building an extraordinarily good **lie
detector for its own results**, while never quite managing to build the thing the lie detector
was supposed to test.

This week the lab finally built one small experiment to answer its founding question:
*if we hand the machine its own record of past failures, does it do better next time?*

Four things happened, and three of them are the lab catching itself.

1. **The experiment produced a positive result — and then two independent reviewers killed
   it.** One found that the two things being compared had been formatted differently, so the
   machine could tell them apart without reading either. The other found that the apparent
   benefit was really the *comparison* arm being handicapped by longer text. The encouraging
   number was withdrawn by the people who produced it.

2. **The lab's proudest claim turned out to have no arithmetic behind it** — five documents
   repeated it, no file computed it. When someone finally wrote the computation, **the claim
   was true** and matched to within a rounding error. It survived; but nobody could have known
   that until it was run, which is the actual lesson.

3. **The lab asked whether a year of "nothing found" was real, or just a broken detector.** The
   answer: the detector was fine. Nothing was wrongly thrown away. But the things it *kept*
   turned out to be right about as often as coin flips — so the treasure chest is full of
   correctly-labeled noise.

4. **And one genuinely new thing worked.** A missing connector plus a particular kind of
   recombination, together, produced a result neither produces alone — reproduced under
   preregistered conditions. That is the first complete "failure → fix → verified improvement →
   replayed" cycle in the program's history. It also revealed that an old validated result had
   quietly become **8.6× harder to rediscover** as the surrounding system grew — nobody would
   have noticed if they hadn't re-run it.

**In one sentence:** the machine did not learn from its dead this week, but the laboratory
proved — four separate times — that it can tell the difference between learning and the
appearance of learning, which is the harder and rarer capability.

---

## PART 4 — HONEST ASSESSMENT

**What is now established (each measured this week, each with artifacts):**
- Heredity is *possible* in this substrate: the type-bridge cycle closed, preregistered,
  reproduced (Apollo, 3/5 with a clean 2×2 interaction).
- The forge's one capability claim is real and now re-runnable by command (Hephaestus).
- The kill record is **not** corrupted by router artifacts — the nulls were real (Harmonia C).
- The survivor record is **chance-level** — the corpus's positive half carries ~no information
  (Harmonia C). This is the sharpest strategic fact of the session.
- The battery and the substrate have **disjoint ontologies**, and 99.98% of records were
  verdicted by their own author (Harmonia D).
- The probe's harness works end-to-end and its arms behave as designed — but only after two
  independent reviewers killed its first result.

**What is not established:** whether residue carries transferable information. Δ_carry has no
valid measurement yet. Tier B has not run.

**The one structural worry.** Every seat this week found real defects, most of them in their own
work — that is the program at its best. But the *ratio of instrument-work to organism-work
remains extreme*, and the program's documented failure mode is exactly that: work which is
always defensible and never terminates. Two counterweights now exist that did not before: the
heredity rule (no new architecture until a cycle closes) and Apollo's demonstration that a
cycle *can* close. Use them.

**The finding I would put in front of an external reviewer first:** Harmonia C's chance-floor
result. If the substrate's survivors are indistinguishable from random pairing, then the
Metabolization Probe — the program's decisive experiment — is being run against a corpus whose
*positive* half is noise. That does not invalidate the probe (it prices *failure* structure,
not survivors), but it sharply raises the priority of Ergon's own conclusion from June: the
substrate stores **verdicts** and throws away **derivations**. Price failure structure; and if
Tier B comes back null, that is the first place to look.

---

## PART 5 — OPTIONS AND NEXT STEPS

Presented as options with costs and kill conditions, not a single path. **All of A–D are $0.**

**A. Second Tier-A exit review, then Tier B** *(the decisive path; ~$9 at measured burn)*
The cures are in (rendering fixed and asserted, F-oracle v2, R7 re-run through the shipping
path). The gate failed twice on grounds neither reviewer anticipated, so it must be re-reviewed
by the same two seats under the same independence discipline, then Tier B runs at full N.
*Kill:* if a third exit review finds a third class of defect, the harness is not the problem —
the *design* is, and that changes the question.

**B. Price failure structure, not survivors** *(follows directly from Harmonia C)*
The corpus's survivors are chance-level; its failures may not be. Ergon's June diagnosis said
the substrate stores verdicts and discards derivations. The pilot's own residue design already
records *the method the prior attempt used* — "the prior run decided this on a single Fermat
base" — which is the verb, not the noun. Consider making that the probe's primary residue shape
rather than one arm of it.

**C. A second metabolic cycle** *(heredity stage 2, repeatable now)*
Apollo proved one cycle can close. The M0-widening cycle is the other pre-specified candidate
(take a true claim the checker cannot pose, widen the interface, re-run, measure conversion). A
second closed cycle turns "it happened once" into "it is a capability."

**D. Periodic replay of load-bearing numbers** *(new, cheap, and earned)*
Apollo found a validated result 8.6× harder to re-find; I found a headline claim with no
computation; the fleet has now caught three fossils in a month. **Proposal: any number cited in
a role doc must carry a command that regenerates it, and load-bearing numbers get re-run on a
schedule.** This is the cheapest insurance the program can buy and it is the common thread of
this entire session.

**E. Spend money only here** *(when A is ready)*
Tier B at full N. Nothing else needs paying for right now.

**Prompt ideas, ready to write on request:**
- *Charon ∥ Harmonia B:* second Tier-A exit review, blind, with an explicit instruction to look
  for a **third** defect class rather than re-checking the two already found.
- *Ergon:* Tier B, with the residue-shape question from (B) posed as a pre-registered secondary
  analysis rather than a redesign.
- *Harmonia A:* the oracle **scorer mode** — a distractor policy owned by the meter, which
  would make the forge's engines (and anything else with a scorer interface) gradeable on the
  independent instrument. This is the fix I referred rather than built.
- *Apollo:* the second metabolic cycle, plus the substrate-drift regression it discovered
  (v3's Q2 "search efficiency" axis).
- *Anyone:* the replay harness from (D).

---

## PART 6 — FOR THE EXTERNAL REVIEWER: WHAT I WOULD MOST LIKE CHALLENGED

1. **Is the Metabolization Probe the right decisive experiment**, given that the corpus's
   survivor half has now measured chance-level? Or should the decisive experiment be
   re-pointed at failure structure before Tier B runs?
2. **Is "heredity" the right frame** for what Apollo demonstrated? A 2×2 interaction reproduced
   over 5 seeds is a real result — but is it *inheritance*, or is it a correctly-configured
   search finally reaching a solution that was always in its space?
3. **Is this program over-instrumented?** Six of seven seats spent this week measuring
   measurement. I argue two closed cycles now justify it; a reviewer with no stake may see a
   lab that has optimised epistemology in place of metabolism, which is precisely the charge
   the August assessment levelled and which I may be too close to re-level.
4. **The conflict structure.** I supply residue the probe prices, I wrote the spec whose
   thresholds classify it, and I authored the prompts that dispatched every other seat. The
   mitigations are declared and enforced (I neither sign, grade, nor adjudicate). Is that
   sufficient, or does the prompt-authorship itself need to move to an unconflicted seat?

---

*Filed by Hephaestus, M3, 2026-08-20. Every claim above is committed to
`github.com/jcraig949jfi/Prometheus` and re-checkable by command; where a number could not be
regenerated, that fact is the finding rather than a footnote.*
