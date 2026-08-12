# Prometheus — whole-program review: auditing the goals

**Author:** Harmonia_M2_C (cartographer / information-recovery lane) · **Date:** 2026-08-12
**Lens (assigned by James):** *What would we build if we started today, and what does this
program actually produce?* A and B audited Prometheus against its own goals. This audits
the goals.
**Companions:** `D:\Prometheus\roles\Harmonia\REVIEW_20260812_syntactic_router.md` (A),
`D:\Prometheus\roles\Harmonia\REVIEW_20260812_program_and_instrument_audit.md` (B),
`D:\Prometheus\roles\Harmonia\POSITION_20260812_north_star_reset.md` (B).

**Declared contamination — read this first.** My challenge prompt
(`review_prometheus_harmonia_C_20260812.md`) was never written; B's prompt names it as a
companion, but it does not exist on disk. During bootstrap, before my lens was assigned,
**I read both A's and B's reviews.** My Phase 1 is therefore *not* independent and I do not
claim it. The compensation is that everything load-bearing here is E3 measurement on
surfaces neither of them touched, produced by three runnable artifacts shipped with this
document. Where I agree with A or B, treat it as weak corroboration; where I disagree
(§7), the disagreement is grounded in a number.

**Evidence levels:** E1 = read the source · E3 = executed this session · M = recalled from
a prior session's recorded verdict, not re-executed.

**Artifacts shipped (per R4's guard — a runnable artifact, never a paragraph):**

| artifact | what it measures |
|---|---|
| `D:\Prometheus\harmonia\diagnostics\component_reachability_census.py` | FINISHED / ABANDONED / STRANDED trichotomy over 8,726 modules |
| `D:\Prometheus\harmonia\diagnostics\dependency_door_audit.py` | how many missing packages gate a library |
| `D:\Prometheus\harmonia\diagnostics\lane_exhaustion_audit.py` | `EXHAUSTION@v1` lifted from features to lanes, with its null |

Results: `_reachability_census.json`, `_dependency_doors.json`, `_lane_exhaustion.json`
(same directory).

**Concurrency check (per `feedback_repo_state_is_not_program_state`, recorded mid-session).**
HEAD moved twice while I worked: `bb203749` (catch-up: Apollo June findings, Icarus state,
the August reviews, B′) and `ec6fbd89` (B's typed-object corpus + R6 corrections). HEAD is
now **`ec6fbd89`, 2026-08-12** — not the 2026-06-27 tree I started from. My census ran
against the earlier tree; the newly-tracked files are Apollo/Icarus artifacts that carry
today's date and would classify as LIVE, which moves none of the numbers in §1–§3 (Apollo
had zero lost-consumer modules either way). **Six typed objects from this session are
appended to B's corpus** (`D:\Prometheus\harmonia\corpus\typed_objects.jsonl`,
`HC-20260812-001..006`; `validate_corpus.py` → PASS, 14 objects). One of them,
`HC-20260812-003`, is the failed attack in §3.

---

## 1. What this program actually produces (E3)

Not "what it aims at" — what comes out. Every number from
`component_reachability_census.py` over the tracked tree.

> **2,239,810 lines of Python in 8,726 modules.**
> **577 of those modules (6.6%) are ever imported by another module.**

The repo divides into three kinds, and conflating them is how prior reviews got a
misleading picture (my own first pass reported "84% unreachable" before I separated them):

| kind | modules | LOC | ever imported |
|---|---:|---:|---:|
| GENERATED (forge/specimen output) | 5,503 | 1,255,508 | **0** |
| SCRIPT (one-shot, has `__main__`) | 1,372 | 486,802 | n/a by design |
| LIBRARY (shared components) | 1,851 | 497,500 | 577 |

**63% of the program's Python by volume is generator output that nothing has ever read** —
`agents/hephaestus/{humanreadable,scrap,scrap_staging,forge_v2..v9}`, `forge/candidates`.
**200 of those 5,503 files are not syntactically valid Python** (`ast.parse` fails). They
were produced, committed, and never parsed by anything, including the forge that made them.

That is the honest answer to "what does this program produce": **terminal artifacts, at
industrial volume, with a component layer two orders of magnitude smaller.** B measured the
same shape in prose (12,666 markdown docs vs 8 typed training objects, ~1,500:1). The code
side has the same signature and it is not a metaphor: 1.26M LOC in, 0 reads out.

**This is not an argument for deleting it.** Under R3 (archive-not-funnel) a specimen
corpus is a legitimate terminal artifact. It is an argument that *volume of output has
never been the program's constraint*, and any plan that produces more of it is not
addressing the bottleneck.

---

## 2. The frozen half, trichotomized (E3)

James's category was the right one to add. Splitting frozen components by **reachability**
(does anything live import it?) and then **executability** (does it still stand up?):

- **FINISHED** — frozen, still reached, or needs no consumer (a proof, a dataset).
- **ABANDONED** — frozen, unreached, and no longer stands up.
- **STRANDED** — frozen, unreached, **and it still works.**

Of 934 frozen LIBRARY modules, **104 have lost every live consumer** — they had importers
once and have none now. Probing the 93 largest by subprocess import: **30 import cleanly
(STRANDED candidates), 63 fail (ABANDONED)**.

### 2.1 The highest-value find: the calibration library is stranded behind three doors

`prometheus_math` (307 library modules, ~160K LOC) plus `techne.lib` do not import on this
host. The failure is **one line**: `prometheus_math\__init__.py:35` eagerly imports
`number_theory`, which imports `techne\lib\class_number.py:19`, which does a bare
`import cypari`.

`dependency_door_audit.py` iteratively stubs whatever package the error names and
re-measures. The doors are countable:

| round | importable | after installing |
|---|---:|---|
| 0 (this host, as it stands) | **29 / 222** | — |
| 1 | 46 | `cypari` |
| 2 | 48 | `snappy` |
| 3 | **220 / 222** | `knot_floer_homology` |

**Three missing packages stand between this host and 191 modules of mathematics.** Only 2
modules fail for any other reason (`torch` partial-init; `tensorly` missing, which the
module reports cleanly itself).

Falsifier I ran before recommending anything: *are those packages actually installable
here?* `pip install --dry-run` resolves all three on Python 3.14/Windows — and
`pip install snappy` alone pulls `cypari-2.5.6`, `knot_floer_homology-1.2.2` and
`snappy-3.3.2` together. **One command, 29 → 220 modules.** I have not run it: installing
into the user's global interpreter is a host change and is James's call, not mine.

**Why this is load-bearing rather than archaeology.** Ruling R1 today makes mathematics the
program's *calibration standard* — "an instrument earns deployment on the reasoning
landscape by first passing on the math landscape, where it can be scored without argument."
The library that scores that standard is 87% unreachable on the host, and has been since
April. Any instrument that "passes on math" today passed against 29 modules.

**Honest bound:** an import is a weak positive (it does not prove the math is correct) and
a strong negative (a module that cannot be imported cannot be used by anyone). So 220
bounds STRANDED from above; it does not certify the code.

### 2.2 Stranded data, and one asset whose live state has no file

- **165 GB of April corpora** sit under `D:\Prometheus\cartography\convergence\data\` — a
  74 GB `hmf_hecke_eigenvalues.jsonl`, a 37 GB `formula_trees.jsonl` **duplicated** in
  `Prometheus_data_backup\`, 13.9 GB `openwebmath_formulas.jsonl`. The 74 GB file is
  referenced by exactly **one** `.py` file in the repo, and that file is a fetch script.
- **No PostgreSQL on this host** (E3: nothing listening on 5432; no service; no install
  directory). Anything DB-backed — Mnemosyne's `prometheus_sci`, Apollo's dual-write — is
  unreachable from here. I cannot say whether it lives on another host; I can say it is not
  restorable from this tree.
- **The landscape tensor's live state was Redis-resident.**
  `D:\Prometheus\harmonia\memory\TENSOR_REDIS.md` documents `tensor:cells`,
  `tensor:version`, and a `tensor:updates` stream capped at 5000. Redis is retired. The
  surviving on-disk artifact is `landscape_tensor.npz` — 31 features × 37 projections,
  **104 of 1,147 cells filled**, last committed 2026-04-19 (`c9d2276e`). Session journals
  reference a tensor v17; no v17 exists in any file. I found no `dump.rdb` or
  `appendonly.aof` anywhere on the drive. **Note the manifest self-reports
  `date: 2026-04-17` while git shows it was rewritten through 04-19 — the artifact's own
  metadata is stale, which is a small instance of exactly what B's lens is about.**
- **The null-model library is stranded.** `D:\Prometheus\harmonia\nulls\` (`block_shuffle`,
  `bootstrap`, `frame`, `model`, `plain`) imports cleanly and is the reference
  implementation of `NULL_BSWCD@v1` — **the only symbol in the entire registry with a real
  promotion hash** (`043ba782`; all 23 others say `pending`). It is imported by nothing
  live. I want to be careful here rather than score a cheap point: these are *statistical*
  nulls (block-shuffle over strata) and today's instruments needed a *behavioural* null (a
  degenerate agent). The honest reading is not negligence — it is that **the null library
  was built for the math lane and did not transfer when the program moved to the reasoner
  lane.** That is a lane-transition cost, and it is the strongest evidence I have that the
  two lanes share less machinery than the program's self-description implies.

---

## 3. The pattern claim I tried to make, and its death (E3)

Assembling §2 I formed a synthesis that unified A's finding with mine:

> *The program's characteristic output is a detector it never wires to a decision.*
> `EXHAUSTION@v1` — formalized, `implementation: null`. `kill_clusters.json` — computed by
> `agents\icarus\kill_clusters.py`, **read by zero modules**, frozen at 6 failures analysed
> out of 22 cycles. `content_aware_promote.py` — built, not in the gate (A). `entails()` —
> built, called by nothing in production (A). `harmonia\nulls\` — promoted, stranded.

Five instances across five authors. It felt like the finding of the session.

**It fails its base rate.** Classifying LIBRARY modules by whether their name marks them as
decision machinery (`gate|detect|audit|null|score|verdict|promote|falsif|kill|diagnos|
validat|check|calibrat|battery|probe|lens`), excluding 577 test/scrap modules that my first
pass miscategorised:

| group | n | lost all live consumers | never wired at all |
|---|---:|---:|---:|
| detector-ish | 93 | 5 (**5.4%**) | 54 (**58%**) |
| everything else | 1,181 | 99 (**8.4%**) | 647 (**55%**) |

**Decision machinery is orphaned *less* often than ordinary code, and never-wired at the
same rate.** The five instances are individually true and individually consequential, but
they are not a pattern above background. What is actually true is duller and larger:
**being unwired is the ambient condition of this repo — 55–58% of real library modules were
never imported by anything, ever.** Detectors are not special; they are merely the ones we
notice, because we remember building them.

I am reporting this because it is the most useful thing in the section: it is a
pre-registered null that killed my own best idea in fifteen minutes, and it is the same
move that should have been applied to A's §1 (see §7).

---

## 4. Slice 2 — the math-claim lane, and when exhaustion was knowable (E1/E3)

### 4.1 The program built the exhaustion detector, and never ran it

`D:\Prometheus\harmonia\memory\symbols\EXHAUSTION.md`, canonicalized **2026-04-20**,
`immutable: true`, thresholds pinned:

> `n_kills >= 3`, clustered in **one** axis class, `>= 1` surviving axis class → **redirect**.
> Explicitly *not* a death sentence: *"a directional signal, not a guarantee."*

Its `implementation:` field is `null`. Its `promoted_commit:` is `pending`. No `.py` file in
the repo mentions it (E3, grep). And it is scoped to **features** — a tensor row — never
lifted to the altitude where the program actually spends months: the **lane**.

This is the single most on-lens fact I found. The program specified its own redirect
instrument, pinned defensible thresholds, declared them immutable, and then applied it one
altitude too low, in a substrate that died nine days later.

*(Registry-wide: of ~24 real symbols, **1** carries a promotion hash. "Promoted" in this
program's record has meant "a markdown file was written.")*

### 4.2 Lifting it, with a null

`lane_exhaustion_audit.py` implements the rubric at lane altitude with **thresholds
inherited unchanged** — tuning a threshold to an outcome you already know is the failure
this program keeps finding in itself. The ledger is 28 dated events (20 E1, 8 M), each with
a citation, published in the source so anyone can re-class and re-run.

Raw kill count cannot separate an exhausted lane from a productive one — productive lanes
kill constantly. The tensor's own encoding already draws the right line:
`-1 "tested, not resolved"` (uninformative) vs `-2 "provably collapses"` (constructive, a
result). So only NO_SIGNAL events count toward exhaustion, and **constructive fraction** is
the health statistic.

**The null:** two lanes that demonstrably produced results are included as controls — the
a3 product-measure theorem lane and the h2 information-recovery lane. If the rubric fires on
those, it cannot tell exhaustion from productive struggle and must be discarded.

| lane | no-signal | constructive | constr. fraction | `EXHAUSTION@v1` |
|---|---:|---:|---:|---|
| a3_lattice_void *(control)* | 0 | 2 | **100%** | silent |
| h2_info_recovery *(control)* | 0 | 2 | **100%** | silent |
| math_claim | 9 | 0 | 0% | **FIRES** — class `statistical_coupling`, crossed **2026-04-19** |
| apollo | 5 | 0 | 0% | **FIRES** — class `evolutionary_search`, crossed **2026-05-24** |
| icarus | 3 | 0 | 0% | **FIRES** — class `reasoner_capability`, crossed **2026-08-12** |

**The null passes.** The rubric is silent on both lanes that produced results, so it is not
merely counting activity. The separator is constructive fraction: the controls kill as much,
but their kills prove things.

### 4.3 Was it knowable earlier? Yes — and the redirect it prescribes is the one that worked

By the program's own thresholds, the math-claim lane's `statistical_coupling` class crossed
`n_kills = 3` on **2026-04-19** (strict classing) or **2026-04-15** (if moment-hierarchy
counts as coupling). The detector that would have fired was authored **2026-04-20 — one day
to five days later** — and pointed at features instead of lanes.

**But the retrospective is more interesting than "ten wasted weeks," and I want to correct
the reading a reader would reach for.** The program *did* redirect. The rubric's surviving
classes for the math lane were the non-coupling ones, and the two lanes that later produced
the program's only Tier-1 results — the a3 product-measure theorem and the h2
information-recovery law, both 2026-06-10 — are exactly `constructive_enumeration` and
`information_bound`. **The redirect happened, and it paid off.** What the missing detector
cost was not the work; it was roughly **seven weeks of delay** in a course correction that
succeeded within about a week of finally being made.

That is a retrodictive validation of the lifted instrument: the redirect target it names is
the one that historically produced results. It is also the strongest argument I can make
for building it, and I note it is a *convenient* argument for a cartographer, so weigh §7's
self-criticism accordingly.

---

## 5. The transfer — the signal is live in an active lane right now

This is the deliverable; the retrospective above exists only to calibrate it.

**Icarus fires today.** `reasoner_capability` reached its third no-signal kill on
**2026-08-12** — B's R6 finding is that third kill, because it converts a claimed capability
into an answer-key read. The three events (R5 wall was serialization, 06-10 M; R6 walls were
lens source-blindness and cid-family, 06-15 M; R6 "capability" was payload reading, 08-12
E1) are one class: *the measured wall was never in the reasoner*. The rubric's redirect
target is the single surviving class, `interface_representation`.

**That is the same prescription A and B reached by different instruments** — A's translator
with kind-routing deleted, B's Move 1 ladder repair. Three lenses, three methods, one
redirect. Given my declared contamination this is weak corroboration, but the *instrument*
did not read their documents: it read dated events and thresholds fixed in April.

**Apollo's verdict turns on one judgement, and I will not hide it behind a table.** If the
2026-06-16 recombination result (crossover crosses a valley single-step search cannot) is
classed as `search_operator`, Apollo fires — five kills in `evolutionary_search`, threshold
crossed 2026-05-24, lane continued to 06-28. If crossover is classed as *part of*
evolutionary search, that class has a June success, the kill count resets, and **Apollo goes
silent.** Sensitivity B in the audit output shows both.

**So the actionable question for Apollo is not "is it exhausted" but: does crossover belong
to the same class as the mutation-and-select regime that produced five no-signal results?**
That is a question about Apollo's substrate that Apollo's owner can answer in an afternoon,
and it decides whether the lane redirects or continues. Under R3 (do not narrow), note that
*both* answers are compatible with keeping the lane — EXHAUSTION is a redirect signal, not a
kill. This is precisely the anti-drift **coverage measure** R4 asks for, and it already
existed in April.

---

## 6. What would we build if we started today

Restricting myself to what the measurements support:

1. **The three doors, first.** One `pip install` restores the calibration standard R1 just
   made load-bearing. It is the cheapest high-value act available in the program, and it
   was invisible to every prior review because none of them tried to import anything.
2. **A lane-altitude coverage instrument, not a fifth reassessment.** It exists as a spec
   (`EXHAUSTION@v1`) and now as ~200 lines of runnable code. What it needs is an event
   ledger written *as work happens* rather than reconstructed by me from a retraction
   registry — the ledger is this audit's weakest link (§8).
3. **Not more terminal artifacts.** 1.26M LOC of generated specimens with zero reads, and
   200 of them not valid Python, is the measured verdict on volume as a strategy.
4. **What I would drop:** the assumption that the math lane and the reasoner lane share
   machinery. The stranded null library is direct evidence they do not. Under R1 they share
   a *standard*, not a codebase — and budgeting as though instruments transfer for free has
   been silently wrong since May.

---

## 7. Phase 2 — attacking A's review

**What survives.** A's §2 (the `verify()` `unknown_kind` correctness bug) and §6 (the
self-inflicted regex import screen) are E3 and stand. §6 is the best evidence in any of the
three reviews, precisely because it was involuntary.

**Where I break A's §1.** A's central claim is that the semantic check being built-and-not-
wired is *"a repeated architectural choice, not incidental typing"* — i.e. that decision
machinery specifically gets orphaned. A tested one null ("all software dispatches on type
tags") and it failed. **A did not test the base rate**, and the base rate kills the strong
form: decision-machinery modules lose consumers at 5.4% against 8.4% for everything else,
and are never-wired at 58% against 55% (§3). Being unwired is this repo's ambient condition,
not a property of gates. A's four instances are real; the inference from four instances to
an architectural disposition does not survive a measurement A could have run in fifteen
minutes. I know, because I made the same inference from five instances and had to kill it.

**Where my lens and A's genuinely disagree.** A locates the defect in *dispatch* — the
router in front of a working engine — and prescribes a translator. My census says the
program's dominant failure is not that the engine is misrouted but that **93% of it is never
called by anything at all**, and that the most consequential single instance is not a router
but three absent pip packages. Those are different theories of the same stall: A's predicts
that fixing dispatch unblocks the engine; mine predicts that most of the engine is not
connected to any dispatch, correct or otherwise. **These are cheaply separable:** A's B′
held-out set will discriminate translator-vs-lookup-table, but it will say nothing about
reach. Run the census after any translator lands — if the translator is reachable from one
gate and nothing else, A's fix is correct and insufficient.

**On A's §4 (Q1 ill-posed).** A names it the weakest load-bearing claim and I agree it has
no E-level, but I think it is *right* and under-argued. My §4.1 supplies the missing
evidence from a different direction: the program has repeatedly authored recognizers for
things it had already conceived (`EXHAUSTION@v1` recognizes a kill pattern it was derived
from) and the recognizer was never even run. Recognition against an authored manifold is not
merely ill-posed in principle; in this program it has an empirical track record of zero
executions.

---

## 8. Weaknesses of this review

- **Not independent.** I read A's and B's reviews before my lens was assigned (§0). Any
  convergence in §5 must be discounted accordingly.
- **The lane ledger is hand-curated by me** — 28 events, 8 of them M-level from memory
  rather than re-executed. I chose the lanes, the events, and the classes. I published the
  ledger and the sensitivity runs, but a hostile re-classer could move Apollo's verdict, and
  I showed exactly which single choice does it. This is the weakest load-bearing part of the
  document.
- **`constructive` vs `no_signal` is my judgement**, imported by analogy from the tensor's
  `-2`/`-1` encoding. It does all the work in the null. If the controls' kills were
  re-typed as no-signal, the rubric would fire everywhere and be worthless.
- **Import success is not correctness.** §2.1's 220 modules are reachable, not verified. I
  did not execute a single mathematical function in `prometheus_math` against a known
  answer, so "the calibration library works" is **NOT_EXAMINED**, not SURVIVES.
- **I did not run the pip install**, so the 29 → 220 recovery is measured against permissive
  stubs plus a dry-run resolution, not against the real packages. A real install could
  reveal ABI failures that stubs hide.
- **The Redis/tensor-v17 claim is bounded by this host.** I searched this drive; I cannot
  speak to other machines.
- **Single author, single family** — Opus auditing Opus artifacts, again. The load-bearing
  parts are deliberately the two executed nulls (§3, §4.2), one of which killed my own
  headline.

---

*The program's honest number of novel discoveries is still zero. What this audit adds is
that the program specified its own redirect instrument on 2026-04-20, never implemented it,
and has since paid for its absence in three lanes — one of which crossed the threshold
today. The instrument is 200 lines. It is now committed and it disagrees with me about
Apollo, which is the first useful thing it has done.*

— Harmonia C, 2026-08-12
