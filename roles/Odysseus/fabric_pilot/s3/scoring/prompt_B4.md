You are a blind quality scorer for research reports about the Prometheus research repository. You receive several
reports, each labelled X###. They come from different sources, and you do not know which. Score each report
independently against the rubric below. Do not try to find out where a report came from: do NOT search the
repository for a report's own sentences, title or label. Only verify the evidence its claims cite.

Tools: Read, Grep and Glob inside the repository, and `rogit` for git history (a single command, used exactly like
git).

Rubric (frozen, S3_PROTOCOL s5). Score each item 0, 1 or 2:
1. EVIDENCE: are the load-bearing claims tied to checkable primary evidence (path:line, commit:path, data)?
   0 = mostly unsupported, 1 = partly, 2 = consistently.
2. CORRECTNESS: pick the 3 highest-stakes claims and verify them in the repository yourself.
   0 = a load-bearing claim is false, 1 = unverifiable or partly true, 2 = all 3 verified true.
   Name the 3 claims and what you found.
3. ANSWERS THE QUESTION: does it answer what it set out to answer, or state precisely why it could not?
   0 = no, 1 = partly, 2 = yes.
4. LIMITS STATED: does it say what was not checked and what would change the conclusion?
   0 = no, 1 = partly, 2 = yes.
5. USABLE: could a research principal act on it without redoing the work?
   0 = no, 1 = with significant rework, 2 = yes.

Write `scores.json` in your output directory:
{"<label>": {"evidence": n, "correctness": n, "answers": n, "limits": n, "usable": n, "total": n,
             "checked_claims": ["claim -> verified/false/unverifiable, with path:line"], "notes": "one or two sentences"},
 ...}
Finish with one line per report: `<label>: <total>/10`.


---------------- THE REPORTS ----------------


======== REPORT X014 ========

# [redacted] [redacted] [redacted] — a term-rewriting substrate (H-D4-42 / FR-115)

Commit read: `5266ccebea3ad5522b7cfa7a07a8718cac113a70` (read-only). All paths are relative to the repo root at that commit. Nothing was executed.

## 1. Question

"Should Prometheus host a term-rewriting substrate (transformation store, exhaustive application, observable termination) so that simplification strategies can evolve?" (`roles/[redacted]/[redacted]/draft/[redacted].[redacted]:12`; harvest source `roles/[redacted]/backlog/harvest/D4_sfe_era.md:381-386`).

It breaks into three parts that the repo can answer to different degrees:

- **Q5a (fact).** Is it true that no rewriting substrate is hosted or owned, and that the rewrite-strategy pressures are unhostable today?
- **Q5b (fact).** Is there rewriting machinery in the repo that the thread (comms #182/#189/#276) did not take into account?
- **Q5c (judgement).** Does the committed evidence support hosting one, and on what conditions?

## 2. Method

1. I read the primary thread in order: Vivarium's return #182, Nyx's question #189, Proteus's answer (#276 in the harvest), and Nyx's pressure records and knife rules.
2. I grepped the whole tree for `rewrit`, `rewriting substrate`, `UNHOSTABLE`, `egglog`, `e-graph`, `TRS` and `normal form`. Then I read every hit that could be a rewriting executor.
3. I checked the Vivarium kind registry (`vivarium/viv/kinds.py`) and the Proteus pieces that Proteus offered to keep stable.
4. I read the verdicts of the two earlier substrate campaigns that included a rewriting basis (D3, D4).
5. I used `rogit log` to date the key files.

Comms rows 188, 189 and 276 are not in the repo as database rows. I cite the committed copies of those messages.

## 3. Evidence

### 3.1 Nothing is hosted or owned (Q5a)

- **Vivarium (the host seat), 2026-09-11.** "all four: cannot be operationalized TODAY -- requirement 1 in each is an evaluable REWRITING substrate ... no kind, no executor and no seat on Prometheus owns one. Nothing in vivarium/viv/kinds.py rewrites terms." (`roles/Vivarium/prompts/2026-09-11_replies/NYX_PRESSURE_RETURNS_44_52_175.md:99-103`). Vivarium's pointer was "Proteus's boolean grammar v0 ... Owner would be Proteus", offered "as a pointer and not a design" (same file :131-134).
- **Kind registry at HEAD.** The registered kinds are `noop_v0`, `random_walk_v0`, `ca_density_v0`, `artifact_probe_v1`, `cegis_boolean_v1` and `eca_rule_eval_v1` (`vivarium/viv/kinds.py:210,274,303,432,480,573`). None is a rewriting kind. A grep for `rewrit` under `vivarium/` finds only prose about files and ledgers.
- **Proteus, 2026-09-16 (commit a648b99a7).** Answer "(b)": "Proteus does NOT own a rewriting substrate and does not intend to build one" (`roles/Proteus/prompts/2026-09-16_replies/REPLY_NYX_189_rewriting_substrate.md:4-7`).
  - Proteus lists what exists and what does not. Missing: "a STORE of transformations", "'one transformation step' as an operation on a term", "a termination criterion (normal form) -- canonical() is not one", and "an executor that applies a store exhaustively and reports termination" (:24-28).
  - It says it will not build the executor "because it is a kind" (:30-33). It does not know of any owner, and it names Techne library learning and Herakles evca as untried neighbours (:35-37).
- **The pieces Proteus offers exist as described:**
  - `proteus/eval/boolean.py:59-60` (grammar) and `:122` (`truth_table` oracle)
  - `proteus/eval/shrink.py:79-90` (`canonical` is documented as "NOT a simplicity claim -- only a tie-break"; `size_key`)
  - `:158` (`minimal_by_enumeration`)
  - `proteus/eval/BOOLEAN_UNIVERSE_TABLE.json`
- **The pressures carry the annotation.** Each of the four lean_simp records has `hosting.status = UNHOSTABLE_TODAY`, blocking requirement "an evaluable rewriting substrate", owner "Proteus (unclaimed)". For example `nyx/specimens/lean_simp/pressures/growing_store_must_terminate.cut1.json:74-80`; the others are `retrieval_at_store_scale.cut1.json:74-76`, `conditional_facts_must_be_paid_for.cut1.json:74-76` and `orientation_is_a_choice.cut3.json:75-76`. Nyx made this a rule: knife K9 "ROUTE TO THE SUBSTRATE OWNER" (`nyx/KNIFE.md:105-114`).
- **A fifth dependent pressure is not annotated.** `nyx/specimens/lean_simp/pressures/mutual_normalisation.cut2.json:9-11` requires "fact A rewrites B which rewrites C". It has no `hosting` block (a grep for `hosting|status|owner` finds nothing in it). So "four unhostable" undercounts by at least one. This is my reading; Nyx may have scoped it differently.
- **Nyx's own ledger is stale on the answer.**
  - `nyx/LOOP.md:127` still reads "#189 Proteus+Vivarium question, no answer".
  - `nyx/CHOP_SHOP_CALIBRATION_2026-09-12.md:88` says the same.
  - `nyx/specimens/hypothesis_shrinker/cuts.json:1038` says the "Proteus halves of #189/#190" were "HELD, not delivered (never booted)".
  - Proteus's reply was committed later, at a648b99a7 (2026-09-16). The harvest's "later evidence" is right; the Nyx ledgers do not reflect it.

### 3.2 Rewriting machinery the thread did not consider (Q5b)

"No rewriting substrate" is true of **hosting and ownership**. It is not true of **code**. There are three committed rewriting executors, and none of them was raised in #182, #189 or #276:

1. **`agent_d3_blind/substrates/s3_trs.py`.** An "ordered local sequence-rewrite" system. It "applies the first matching rule, and repeats to fixpoint or fuel exhaustion" (:1-6). Termination is observable: it returns `"ok"` at fixpoint and `"timeout"` when fuel (`FUEL = 80`) runs out (:108-142).
   - [redacted]'s asset survey (commit 87bab0877/f0987100c, 2026-09-06/08) calls it "the only term-rewriting substrate in the repo" and recommends "ADAPT D3 `s3_trs.py` for a rewriting world" (`[redacted]/docs/expansion/ASSETS.md:123-124`). That recommendation predates #182 by three days, and nobody in the thread cites it.
   - Limits: it rewrites flat sequences, not trees. The rule set is the organism's *genome* (at most 6 rules), not a growing fact store. It does not report per-fact examination counts or which rules fired.
2. **`agent_d4_blind/substrates/vm_substrates.py:418-454` (`S3_REWRITE`).** Leftmost-first pair rewriting with 16 rules over an 8-symbol alphabet. It halts when no rule matches, with a 64-step cap.
3. **`techne/lib/donors/egglog_adapter.py`.** An e-graph / equality-saturation donor.
   - It offers a closed menu of 6 arithmetic rules (:56). It saturates and then extracts a minimum-cost term (:70-81, :131-141).
   - It reports `rules_applied` as *configured*, not as fired (:140-141). It exposes no step counts, no termination-by-budget signal and no trace.
   - Its docstring says extraction imposes egglog's cost model as an ordering (:23-26).
   - Status: labelled ACQUIRED / IMPORT-TESTED / WRAPPED / CONTROLLED, with one direct consumer, `ergon/gen0/family_b_probe.py` (`techne/acquisition/DONOR_DISPOSITION_2026-09-11.json:163-209`).

The Proteus oracle pieces (§3.1) would give any of these a soundness check. None of them is a Vivarium kind.

### 3.3 Evidence that bears on "should" (Q5c)

**For hosting:**

- Five pressures need a rewriting substrate to be operational, and none has any other route (§3.1).
- Nyx's program table shows "pressures operationalized 0 ... 4 unhostable -- no rewriting substrate" (`nyx/LOOP.md:110`). This single missing substrate accounts for most of the unhostable backlog.
- [redacted] already recommends adapting an existing executor (`[redacted]/docs/expansion/ASSETS.md:124`).
- Lexis argues the e-graph family may fit Prometheus better than the DreamCoder/Stitch family. Lexis states this is an argument, not a result: "Nobody has run babble on anything of ours" (`roles/Lexis/library_learning/notes/PASS_04_gene_extractor_and_the_e_graph_fit.md:122-124`; also cited in `techne/lib/donors/egglog_adapter.py:15-19`).

**Against, or cautions:**

- **Both earlier rewriting substrates were killed.**
  - D4 `S3_REWRITE` had the highest validity (0.996) and the largest phenotype mass, but "a dead accessibility geometry: far-stratum hits 0.00 for every navigator ... [redacted] maximized both and failed the only property that matters for a learning substrate" (`agent_d4_blind/VERDICT-PHASE1.md:85-96`).
  - D3 `[redacted] TRS` failed G1 (viable neighbour rate), G8 (M0 coverage) and G10 (witness access), passing 7/10 gates. That campaign's overall verdict was `NO_BASIS_PASSED` (`agent_d3_blind/VERDICT-PHASE1.md:6,18-30`).
  - Caveat: both campaigns used rewrite rules *as the evolving program* and asked about navigability. The lean_simp pressures use rewriting *as the world* and evolve the organism's store discipline. The kills are a caution, not a refutation (see §5).
- **A prior install on a leverage claim went unused.** egglog "was installed on a leverage claim and never consumed". Techne's own retrospective says this and treats it as a warning against further dependency asks (`techne/loop/rung_notes/CYCLE049_RETROSPECTIVE_FINDINGS.md:68-77`).
- **No seat will own it.**
  - Proteus declines (§3.1).
  - Vivarium hosts only a kind whose semantics another seat declares (`NYX_PRESSURE_RETURNS_44_52_175.md:7-15,137-145`).
  - Nyx "never builds the world for her own pressure" (`roles/Nyx/prompts/2026-09-11_reply_182_and_proteus_question/QUESTION_PROTEUS_rewriting_substrate.md:23-26`).
- **Vacuity risk in the only named candidate (my inference; not stated in the repo).**
  - `growing_store_must_terminate` lists as trivial shortcut 1 "ignore the store entirely and answer by direct evaluation". It closes that shortcut by requiring "some problems must be unanswerable without a stored fact" (`growing_store_must_terminate.cut1.json:17-18`).
  - In Vivarium's pointer (boolean grammar v0 at n=3), every term's function is decidable by `truth_table` over 8 rows. The exact minimum of each function is already tabulated (`REPLY_NYX_189...:18-22`).
  - So an organism that ignores the store may be able to answer any "simplify this term" problem directly. Whether this shortcut can be closed in that world is an open question. `out/analysis.py` measures part of it (§6).

## 4. Result

- **Q5a — confirmed, with a correction.** At 5266cce no rewriting kind, executor or owning seat exists (Vivarium #182, Proteus 2026-09-16, kind registry). The lean_simp rewrite-strategy pressures are unhostable. Two corrections:
  - there are at least **five** dependent pressures, not four (`mutual_normalisation.cut2` is unannotated);
  - Nyx's ledgers still record #189 as unanswered.
- **Q5b — the harvest's framing ("no substrate") overstates the gap.** Three rewriting executors are committed: D3 `s3_trs.py`, D4 `S3_REWRITE` and the Techne egglog adapter. [redacted] had recommended adapting `s3_trs.py` for a rewriting world before the thread began. None of the three meets the pressures' requirements as they stand; each lacks at least one of:
  - a growing store held as data;
  - tree terms;
  - world-owned step counting with fixpoint and exhausted distinguished (only `s3_trs`/`S3_REWRITE` have this);
  - per-fact examination counts;
  - a fired-fact trace.
  The real gap is **ownership plus instrumentation**, not the rewriting mechanism itself.
- **Q5c — the repo does not settle "should".**
  - What it supports: the gap is real and specific. The missing piece is small; the pressures spell out the needed instrumentation (step log, examination counts, fired-fact trace). Building parts exist.
  - What it does not support: that hosting would pay off. No run on any rewriting-as-world setup exists. Both rewriting-as-genome substrates were killed. The previous acquisition justified by rewriting leverage went unused. No seat has claimed ownership. The candidate world has an unmeasured vacuity risk.
  - **Conditional answer:** host it only if (i) a seat claims the semantics and (ii) a pre-run eligibility/vacuity check on the candidate world is non-vacuous (planted looping pairs > 0; the undisciplined store hits the budget and the disciplined one does not; the direct-evaluation shortcut is closed). Otherwise it stays a coverage note.
- **On the harvest label.** "New-lens signal (strong)" is supported as a *coverage* signal: an entire mechanism class currently has zero routes into selection. It is not supported as evidence of *value*.

## 5. Limits

- **Comms rows.** I did not read comms rows 188, 189 or 276. Their committed copies agree with the harvest quotes, but I cannot rule out uncommitted follow-ups in the comms DB after 2026-09-16.
- **Search coverage.** Grep may miss rewriting code under other names, such as normalisers inside the Lean ablation tooling or fossil specimens (for example the eprover fossil). I excluded `techne/fossils/**` payloads from the egglog sweep. Fossil specimens are frozen third-party bytes, not hosted substrates.
- **Relevance of the kills.** Whether the D3/D4 kills matter for a rewriting-*world* is my argument. Neither verdict addresses store discipline.
- **Vacuity risk is unmeasured.** The boolean-grammar vacuity concern is an inference. `analysis.py` is written but not run.
- **"Should" is a question of values and priorities.** This report bounds it with evidence; it does not decide it.

## 6. What would change the conclusion

- **A seat claims ownership** (Techne, Herakles or [redacted], via an ADAPT of `s3_trs.py`), or a Vivarium rewriting kind is committed. Then Q5a flips to "hostable" and the question becomes one of operation.
- **`out/analysis.py`** (stdlib only). It mirrors `proteus/eval/boolean.py@5266cce` (grammar lines 59-60, oracle semantics lines 122-136) and runs a naive exhaustive first-match rewriter over true boolean identities. What would decide:
  - planted permutative/inverse pairs > 0 (eligibility; stated in the record at `growing_store_must_terminate.cut1.json:16`);
  - the undisciplined store hits the step budget on a large fraction of problems after planting, while the size-decreasing-orientation store does not (the cheat control, :23);
  - the two score the same with no planted pairs (the negative control, :24).
  If the cheat control separates the two, the boolean-v0 pointer is a live world for that pressure, which strengthens "host". If it does not separate them, or the direct-evaluation baseline matches the rewriter's answers on every problem, the pointer is vacuous and a different term language is needed, which weakens "host on this pointer". I have not run it and do not state its output.
- **A pilot showing that simplification strategy (store discipline) is selectable in a rewriting world** would move Q5c from "conditional" to "yes". A pilot showing the same dead-geometry failure as D4 [redacted] would move it toward "no".
- **Evidence that the egglog adapter has consumers beyond `ergon/gen0/family_b_probe.py`,** or that it exposes iteration and fired-rule reports, would reduce the build cost.



======== REPORT X010 ========

# [redacted] [redacted]: Reanalyses that need no new compute (Atlas RA-1..RA-5)

[redacted]
Every path below is at that commit unless another sha is given. No code was executed.

## 1. Question

Harvest entry H-D1-51 (roles/[redacted]/backlog/harvest/D1_program.md:473-480) says Atlas's five "reanalyses that need no new
compute" are an unfollowed recommendation ("none run"). The [redacted] asks for them to be answered from committed repository
content. That breaks into three parts:

- **(Q-a) Status.** Were RA-1..RA-5 run, in name or in substance?
- **(Q-b) Feasibility.** Can each be answered from committed files alone, as the harvest's "repo-only science" framing claims?
- **(Q-c) Answers.** Where committed evidence already answers part of a question, what is the answer?

The five records are at roles/Atlas/proposals/2026-09-21_prior_art_raid/EXPERIMENTS.jsonl:30-34:
- **RA-1:** did queue pools act as a curriculum?
- **RA-2:** learned descriptors over GraphWorld and CW01. The harvest omits it, but the [redacted] title covers it.
- **RA-3:** evaluator-exploitation census.
- **RA-4:** Crius PARTS takeovers as cross-niche recombination.
- **RA-5:** rediscovery rate across seats.

## 2. Method

1. Read the five records and their status everywhere they are cited: the Atlas journal, backlog, STATUS, roadmaps and prompts; the Techne journal; the [redacted] threads.
2. Searched commit messages on all refs (`rogit log --all --grep`) for RA-n or reanalysis.
3. For each RA, found where its named inputs live. I read the Atlas harvesters to tell whether an input is a committed file or a row in the uncommitted M1 Postgres `atlas` schema.
4. Three read-only search sweeps (sub-agents) covered: (i) committed exploit-shaped events and their catchers; (ii) committed cross-seat convergence and rediscovery documents plus the Nyx and Techne inventories; (iii) committed frontier-queue and Crius C2 data.
5. I re-verified the load-bearing lines myself: the [redacted] report in full, the FAILURE_PRINCIPLES s4 table, the [redacted] verdict, the Crius C2 disposition, the scheduler code and the WSE/Eos/Nemesis/ASAL lines. Sub-agent rows I did not re-open are marked MEDIUM confidence in [redacted].
6. Where a question needs computation over committed data (RA-1, RA-4), I wrote it as `out/analysis.py`, with decision rules fixed in advance. I did not run it.

## 3. Evidence and results

### 3.0 Status and a quote correction (Q-a)

- **The quote behind "RA-1/RA-3 need nothing" is truncated.** The source says RA-1/RA-3 "need nothing *from Techne*" (roles/Techne/journal/2026-09-25_gandalf-a04f7c25_RESET.md:91-92; also roles/Atlas/prompts/2026-09-21_to_techne/TO_TECHNE.md:19: "they run over the Atlas index"). It is a statement about donor dependencies, not about compute or data.
- **Atlas designed the RAs to run over its Postgres index, which is not in git.** The schema `atlas` lives on the M1 store (atlas/README.md:3-5; atlas/db.py:1-7,27-29), and the only committed Atlas data file is atlas/registry.json. So the counts quoted in the records cannot be recomputed from git: "442 queue items, 22 RUN attempts, 1,196 detector_firing facts" (EXPERIMENTS.jsonl:30), "218 defects, 610 control facts" (:32), and "atlas.conclusion (468), mechanism_claim facts (99)" (:34).
- **Atlas could not run them anyway.** The Atlas seat is PARKED (roles/Atlas/STATUS.md:7, :58 "REPORTS ONLY"), and its own journal says "Crius and the Nyx mechanism ledger are not yet indexed, so RA-4 and RA-5 cannot run today" (roles/Atlas/journal/2026-09-21.md:41-42). The index extensions ATLAS-34/35/36 are still open (roles/Atlas/BACKLOG_H0H5.md:27-29; atlas/registry.json:256).
- **Only RA-2 and RA-4 rank in the policy layer.** They appear in Atlas's ROADMAP top-15 (roles/Atlas/reports/ROADMAP_2026-09-25.txt:118,123). RA-1, RA-3 and RA-5 do not.
- **"None run" is true under the Atlas names but stale in substance.**
  - [redacted] [redacted] [redacted] (roles/[redacted]/[redacted]/runs/[redacted]/REPORT.md, committed by 7e1ca095d/088608cdf on 2026-09-28) ran an RA-3-equivalent census.
  - [redacted] FAILURE_PRINCIPLES s4 (roles/[redacted]/challenge/FAILURE_PRINCIPLES.md:797-898, d5241a102, 2026-09-28) and [redacted] (roles/[redacted]/[redacted]/runs/[redacted]/REPORT.md:222-235) did partial RA-5 work, with independence coding.
  - None of these three cite "RA-3" or "RA-5".
- **Name collision.** The commits "RA-1 INDETERMINATE" (d51d1fa82) and "RA-1 preregistration" (9c1badfba) are Herakles's own RA-1/RA-2 (herakles/specimens/spec-toussaint-exploration/reanalysis/...). They are unrelated to Atlas RA-1.

### 3.1 RA-1: queue pools as curriculum

**Feasibility: YES from git, with gaps.** Atlas's frontier harvester reads committed files (atlas/harvest/frontier.py:39, `ls_tree(ref, "[redacted]/frontier")`). The per-chunk detector counts behind the 1,196 detector_firing facts come instead from host-only receipts (atlas/harvest/frontier_runs_m2.py:3-6,205-210; RUN_HOST "M2"). The data committed @5266ccebe:

- **Queue rows** carrying pool, lane, priority, budget and state: [redacted]/frontier/queues/{EXPLORATION,EXPLOITATION,AUDIT}.jsonl (414/144/134 lines, append-only snapshots). REVISIT.jsonl is git-ignored ([redacted]/frontier/.gitignore:3).
- **Events:** [redacted]/frontier/registry/EVENTS.jsonl holds 130 RUN events (my count) and 129 OBSERVATION events whose text carries per-run firings, written at scheduler.py:385. The format is, for example, EVENTS.jsonl:12793 "B-scatter.T000.d_seed: 2 chunks, 9984 evaluations, firings {...}". It also holds 299,991 BLOCKED_BY_SUPPRESSION rows, which are a logging defect ([redacted]/frontier/scheduler.py:269-271; roles/Atlas/journal/2026-09-25.md:29-36) and must be dropped.
- **Pool outcomes at epoch 2026-09-21T2054Z** ([redacted]/frontier/digests/EPOCH_2026-09-21T2054Z.json:49-105; RUN = 119 at :18):

  | pool | done | pending | dropped |
  |---|---|---|---|
  | EXPLORATION | 50 | 202 | 25 |
  | EXPLOITATION | 36 | 12 | 5 |
  | AUDIT | 21 | 40 | 3 |
  | REVISIT | 12 | 1 | 0 |

**Design finding that changes the reading (new; not in the RA-1 record).** Pool assignment is partly a function of prior firings and of lineage mode:

- `descendants()` enqueues the seed/initialization controls of a depth-0 run into AUDIT only when an ADMITTED detector fired on that run (scheduler.py:181-200; ADMITTED at :178).
- Items seeded by `ingest` get their pool from the lineage's mode ([redacted]/frontier/ingest.py:120).
- The scheduler chooses a pool by share deficit (`choose_pool`, scheduler.py:239-248), not by item merit.

So an unstratified pool-vs-firing association is expected by construction, and is not evidence of a curriculum. The proposal's time-window permutation null (EXPERIMENTS.jsonl:30 anticheat) does not remove this. A within-lineage null and exclusion of scheduler-spawned controls are needed; both are in analysis.py.

A second confound: firing thresholds were calibrated on v0 populations, and graph populations fire "two orders of magnitude fewer" (EPOCH_2026-09-21T2054Z.json:46). Firing rate therefore partly tracks the substrate profile, which is itself lineage-bound.

**Answer: not yet computed.** The analysis.py `ra1` decision rule:
- **Ineligible** if fewer than 2 pools have at least 10 joined runs.
- **"Curriculum-shaped association"** only if the within-lineage permutation p < 0.05 and the effect survives excluding `branch: control` items.
- **"Composition, not curriculum"** if only the global null rejects.

REVISIT runs cannot be joined, because their queue file is not committed.

### 3.2 RA-2: learned descriptors (included because the [redacted] title says RA-1..RA-5)

Not repo-only in practice. It is NEEDS_DONOR, needs the ATLAS-07 row/cell harvest and a descriptor pipeline (EXPERIMENTS.jsonl:31; BACKLOG_H0H5.md:29, ATLAS-36 open), and is "S" compute, not zero. No committed run was found. Not pursued further.

### 3.3 RA-3: evaluator-exploitation census

**Already done in substance.** [redacted] [redacted] (roles/[redacted]/[redacted]/runs/[redacted]/REPORT.md, repo @6ff2b2f8a) used RA-3's own event definition (:30-31) and read every roles/*/calibration ledger (:29). Its results:

- **Size:** "38 recorded events across about 20 seats and engines" (:120).
- **By class** (:121-122): 21 found by selection/search, 11 instrument/analyst bugs, 5 human-built trivial baselines passing, 1 mixed.
- **Caught by:** "mostly null, shuffled or cheat controls, then human reading and adversarial review. A second independent evaluator caught one, and it was the planted case" (:123-124).
- **Latency:** usually within the same campaign. The outliers were caught 6 weeks to about 5 months late: Nemesis about 162 days, Eos about 163 days, [redacted] about 6 weeks, Hephaestus months (:125-127).
- **Rate:** "the repository cannot yield a rate because it does not record its denominators" (:175-176; also :138-139).
- **Limit:** only the summary is committed. The per-row table stayed in scratch (:23). RA-3's own anticheat, a hand-labelled sample to measure classifier error (EXPERIMENTS.jsonl:32), was not done. [redacted] says so itself: "the remaining census rows rest on a single read" (:232-234).

**Independent re-census (this attempt, one reader, not hand-validated).** A separate sweep reconstructed 38 events with citations, listed in [redacted] C-RA3-*. My tally by primary catcher:

| caught by (primary or co-primary) | events |
|---|---|
| cheat control or exploit probe | about 13 |
| null, shuffled or held-out control | about 11 |
| human reading or self-audit | about 11 |
| external review or second evaluator | about 5 |
| positive control as sole catcher | 0 |

**The RA-3 claim under test is SUPPORTED on the recorded frame, weakly.** The claim is "cheat controls, not positive controls or human reading, caught most exploitation". Controls of some kind (cheat plus null) caught roughly 24 of 38. Positive controls caught none alone. But human reading is not a minor catcher (about 11), and cheat controls alone are not a majority.

Two observations, both from single-read coding:
1. **The long-latency catches all come from human, external or audit catches, never from a cheat control:** Nemesis constant string, 0.674, "292 of 294 tools score below it" (roles/Nemesis/CALIBRATION.md:16); Eos CHEAT 100/100 (roles/Eos/CALIBRATION.md:118-121); [redacted] R6 answer key; Hephaestus constant floor (roles/Hephaestus/journal/2026-09-19.md:163).
2. **In at least two events a preregistered null control missed the exploit:**
   - WSE W8: "The null battery ... could not see a one-tick-lag echo, so the leak passed the s5 gate" ([redacted]/wse/READOUT_v01.md:111-112).
   - [redacted] WTP-01: the shuffled control hit 0-2 of 5, so the ARTIFACT rule did not fire ([redacted]/ENSORAIN_WTP01_REPORT.md:50-63, sub-agent citation).

**Where denominators exist, exploitation is common** ([redacted]:128-133):
- ASAL: 49 of 105 threshold-crossers were METRIC_EXPLOIT (roles/[redacted]/rulings/RULING_ASAL_LEGIT_SEARCH_001_2026-09-18.md:69).
- Crius: abstention in 6/6 C0 runs.
- WSE: 1 of 18 cells.
- [redacted]: 0/90 probes became dominant.

**Denominator and category problems:**
- The Atlas "218 defects" come from two harvested sources only: [redacted] campaign ledgers (atlas/harvest/archaeon_campaigns.py) and NPE CW01 DEFECTS.jsonl, whose 92 rows are the only ones with a `found_by` field (atlas/harvest/npe.py:514-538).
- These are defects, not exploits. FR-057 makes the same point: "These are defects, not reversals" (roles/[redacted]/backlog/threads/FR-057.md:46-48).
- The roughly 45 calibration ledgers that hold most exploit events are not harvested.
- Category vocabularies differ per seat, and `caught_by` is rarely a field.

### 3.4 RA-4: Crius PARTS takeovers

**Feasibility: YES from git. The prerequisite is now met.** The record required "Crius C2 arm complete" (EXPERIMENTS.jsonl:33). The arm is complete: crius/runs/C2_TERMINAL_DISPOSITION.md:95 `R5_survives false`, :103 `"CLOSED -- ACCESSIBILITY FRONTIER MAPPED"`. All 36 runs' takeovers.jsonl and candidates.jsonl.gz are committed under crius/runs/search_c2{a..d}_{arm}_s{1..3}/ (sub-agent listing). ATLAS-34 is still open (atlas/registry.json:256), but the Atlas index is not needed.

**Committed partial answer (PART donors only, rung d)** from C2_TERMINAL_DISPOSITION.md:54,63,79:

| run | P_INV | P_PLAN | P_REC | PART-child takeover rate |
|---|---|---|---|---|
| c2d recombination s1 | 15/203 | 7/197 | 10/182 | 32/582 = 5.5% |
| c2d recombination s2 | 9/189 | 8/194 | 8/209 | 25/592 = 4.2% |
| c2d recombination [redacted] | 1/205 | 4/195 | 1/197 | 6/597 = 1.0% |

The per-run totals and percentages are my arithmetic from those lines. **No committed comparison with population-donor (ELITE) or self-splice children exists**, so RA-4's primary endpoint is not yet answered.

Three facts bound what it could show:
1. **Takeovers of PART children are mostly selectively neutral.** The top lineages' PART takeovers carry paired fitness deltas of about +0.0005 and solved delta 0 (C2_TERMINAL_DISPOSITION.md:55-57,65-69). Takeover rate is therefore a weak proxy for "selective value".
2. **The donor type is confounded with everything else.** PART donors exist only at rung d. They descend from P_BASE, not from the population's ENUMERATE_VM seed, and sit at fixed structural distances from it (sub-agent: crius/DESIGN_C2.md:104-110,228-231; C2_SUMMARY.md:116-119). So donor class, rung, ancestry and distance move together. Only within-rung-d contrasts are interpretable.
3. **The population donor pool includes the parent itself** (crius/search.py:312-315). "Within-lineage" therefore has to be split into SELF vs ELITE.

analysis.py `ra4` does this, with a within-(run, iteration) permutation null that respects Crius's common-random streams (search.py:321-326).

### 3.5 RA-5: rediscovery rate across seats

**Feasibility as specified: NO.** Both named inventories record outside mechanisms harvested by a single seat, with no discovering-seat field:
- Nyx MECHANISMS.json: 6 entries, `source_lineage` = external origin (nyx/atlas/gates/MECHANISMS.json).
- Techne CATALOG: 121 fossils, no seat/author field (techne/fossils/CATALOG.json).

Seat-level rediscovery is 0 by construction in those files. The Atlas mechanism_claim/conclusion rows are uncommitted.

**Partial answer already committed (failure-principle unit, not mechanism unit).** FAILURE_PRINCIPLES s4 (roles/[redacted]/challenge/FAILURE_PRINCIPLES.md:797-898):
- It counts a structure as rediscovered when "at least two catalogues reach the same mechanism from different evidence" (:799-800).
- It codes evidence independence as IND/SP/SS (:761-766).
- Result: five of 15 principles (P01, P04, P07, P13, P08) are found by all three catalogues on at least partly independent evidence (:840-842).
- [redacted]'s June Failure-Primitive Atlas: "three of four fossil classes recurred in September engines, and every recurrence was rediscovered without citation" (:895-896). FP-001, FP-003 and FP-004 recur uncited; FP-002 does not (:867-893).

**Independence is weaker than "rediscovery" suggests.** [redacted] tested the Z80 "three engines" recurrences and found "Survives in 2 or more engines with its factor removed: none ... They are not three independent sightings of a law" (roles/[redacted]/[redacted]/runs/[redacted]/REPORT.md:230-235). The three builds came from one directive and one paper (:234).

**Participant-written convergence lists** (selected, not a rate; sub-agent citations, MEDIUM):
- Herakles CROSS_SEAT_META_ANALYSIS_2026-09-04.txt:13, "SIX convergences", with "None cites the others" at :133.
- Elenchus CROSS_SEAT_COMPARISON.md:23-30, the 16-minute opposite finding.
- [redacted] CROSSWALK.md:102-103, "existence is not accessibility -- found three times without citation".
- Hermes CONVERGENCE_PROBE_2026-09-11.md:49-81, ops defects hit by 5-7 seats uncited.

**Result for RA-5.** No rate over a defined denominator exists or can be formed from committed inventories.

What the committed record does show:
- Rediscovery of failure classes happens.
- It happens mostly **without citation**. That is the transmission failure RA-5's secondary endpoint asks about ("whether the later one cited the earlier").
- Apparent cross-engine recurrence within one directive/model/day cohort does not survive a factor-removal test.

That mix is two different things. For the "convergence the operator fears" (H-D1-51), the committed evidence says the September recurrences are shared-design echoes. It does not say they are independent convergence. The robust rediscoveries are across eras (June [redacted] vs September engines).

## 4. Result (summary)

| RA | Run under this name? | Answerable from git? | Committed answer |
|---|---|---|---|
| RA-1 | No | Yes, from queues + EVENTS.jsonl; REVISIT missing | None. Pool is endogenous to firings and lineage, so a naive association would be an artefact. analysis.py `ra1` decides it. |
| RA-2 | No | No (donor + pipeline + ATLAS-07) | None |
| RA-3 | In substance ([redacted] [redacted]) | Yes, as a census; No as a rate | 38 events. Controls (cheat + null) catch most; positive controls catch none alone; human reading is significant and owns the long-latency catches; a rate is impossible because exploit-free runs are unrecorded. |
| RA-4 | No | Yes (C2 complete, all files committed) | PART-child takeover 1.0-5.5% per seed, with no ELITE/SELF comparator yet; takeovers near-neutral; donor type confounded with rung and ancestry. analysis.py `ra4` decides the within-rung contrast. |
| RA-5 | Partially (FAILURE_PRINCIPLES s4, [redacted]) | No for mechanisms; partly for failure classes | Failure-class rediscovery is common and uncited across eras. Within-cohort "independent" recurrence does not survive factor removal. No rate. |

Overall, H-D1-51's framing is half right:
- RA-1 and RA-4 really are no-compute and repo-only (a short stdlib pass).
- RA-3 and RA-5 are already partly answered by [redacted]'s 09-28 work, and their "rate" forms are unanswerable from the repo because the denominators (exploit-free runs; a seat-attributed mechanism inventory) are not recorded.
- "RA-1/RA-3 need nothing" was misquoted: they needed nothing *from Techne*, but did need the uncommitted Atlas index.

## 5. Limits

- No code was run. The RA-1 and RA-4 numbers are not computed, and analysis.py is untested.
- The RA-3 re-census and the RA-5 convergence list were assembled by one reader via sub-agent sweeps. I re-opened the load-bearing rows only (see [redacted] confidence). There is no inter-rater check, and exploit-vs-bug classification is subjective.
- Only recorded events are visible. Undetected exploits and uncited convergences that nobody noticed are missing by construction.
- [redacted] [redacted]'s per-row table is not committed, so my 38 cannot be matched row-for-row to its 38.
- I could not see the Atlas Postgres counts (442/22/1,196; 218/610; 468/99), so I cannot confirm them or reconcile them to git.

## 6. What would change the conclusion

- **RA-1:** a within-lineage permutation p < 0.05 that survives excluding scheduler-spawned controls would move it from "no evidence" to "association". Committing REVISIT.jsonl would add a pool.
- **RA-4:** if PART takeover rate exceeds ELITE rate within (run, iteration) in at least 2/3 seeds, it provisionally supports donor splices beating within-population variation (still confounded with ancestry). Otherwise QD-9 needs a prospective design.
- **RA-3:**
  - Committing [redacted]'s row table, or two-coder labelling of 30 rows with kappa of at least 0.6, would firm up the catcher split.
  - Per-campaign records of "runs with a cheat control" and "exploit-free runs" ([redacted]:209-212) would allow a rate.
  - A finding that the long-latency catches had cheat controls available but unused would sharpen the doctrine claim.
- **RA-5:**
  - A seat-attributed inventory (ATLAS-35 with a discoverer field) plus a labelled dedup sample would allow a rate.
  - Finding cross-seat recurrences that survive [redacted]-style factor removal within a cohort would overturn "shared-design echo".



======== REPORT X008 ========

# [redacted] [redacted] -- Recombinant continuity: C-OP', per-unit ancestry (ARG), the privileged-operator null, FLOW vs DIFFERENCE

[redacted]
was run. Paths without a commit prefix are at HEAD.

## 1. Question
The harvest entries (H-D1-07, H-D1-08, H-D2-14, H-D2-15, H-D2-37) ask five things:
1. Does the E-002 rule C-OP' hold outside PTE?
2. What is the null for a privileged (asymmetric) recombination operator?
3. Should material contribution be counted by FLOW or by DIFFERENCE?
4. Should the lineage contract replace a singular parent with graded per-unit (ARG-style) ancestry plus a declared convention?
5. Does label-based "descent" count as heredity?

## 2. Method
- I read the E-002 record (RESULT.md, T-007_CRITERION.md, T-008_T-011_RESULTS.md).
- I read the deep-block review files (A_E002_REVIEW.md, B_B1_B6_B8.md, G_PRIOR_ART.md) and Block A's attack script
  (cop_prime_attack.py).
- I read the later Attribution v0 campaign: the spec, schema.py, the assay and the packet.
- I traced the history with `rogit log` and `rogit branch --contains`.
- I did not run any code. The one computation that would tighten the result is written as out/analysis.py, and its output is not
  stated here.

**Provenance correction to the harvest:** the harvest says the deep block (72923db05) is "Not merged" / "unmerged". At HEAD it is
merged. `rogit branch -a --contains 72923db05` lists `remotes/origin/main` and the current HEAD, and the files are at
ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/. Being merged does not make it adopted: Block A still marks its narrowed rule
"proposed, not adopted" (A_E002_REVIEW.md:36).

## 3. Evidence

### 3.1 C-OP' as proposed
- The proposal (RESULT.md:42-45) is:
  * collapse identical contributors and exclude inert units;
  * lift ILL_POSED only when the difference-making share clears the declared operator null at a declared alpha;
  * "NOT adopted, and NOT tested outside PTE". The alpha is "a free choice" (0.005 suggested, not tuned).
- Clause (b) is defined only for an exchangeable operator, "Binomial(n, 1/2)" (RESULT.md:28-29).
- For a privileged operator, C-OP falls back to C-MAJ (T-007_CRITERION.md:28, :36; T-008_T-011_RESULTS.md:13).

### 3.2 C-OP' attacked and narrowed (Block A, now on main)
Block A (A_E002_REVIEW.md) implemented the rule in [redacted]/causal_lens/deep_block/cop_prime_attack.py. It found:
- **E1b** (A_E002_REVIEW.md:23): a child byte-identical to a, from parents that differ at 3 units, is called **ILL_POSED**. With
  nd = 3 no child can clear alpha. The real GA crossovers had nd = 10-28.
- **E4** (:26): 15/16 units flow from b, but the only distinguishing unit comes from a. The child is byte-identical to a.
  DIFFERENCE says a, FLOW says b, and C-OP' says ILL_POSED.
- **E5** (:27): 75-81% of the distinguishing units come from a, and the child is still ILL_POSED "purely by a significance
  convention".
- **E7** (:29): the phenotype is exactly a's while the material share is 4/16 from a. Clause (a) is ambiguous between MATERIAL
  difference and EFFECT difference.
- **E3/E3b** (:25): the privileged case is "unaddressed". Under a 90%-a operator a 14/16 child is typical, yet it is extreme under
  the unbiased null.
- **Root defect** (:31-34): clause (b) tests one realized operator draw. That asks whether the operator was biased, which is a
  population question, not a per-child fact. "Nearly every PTE recombinant has no singular parent" therefore "restates the chosen
  alpha".
- **Narrowed version** (:36-43):
  * keep self-cross collapse and NOT_IDENTIFIABLE;
  * report the DIFFERENCE and FLOW shares separately as graded quantities;
  * make a singular label a declared convention on the difference share (>= 1 - eps), not a significance test;
  * "operator symmetry ... cannot make a realized child's content ill-posed";
  * report MATERIAL and EFFECT separately.
- Status line (:46-47): C-OP' is "operator-specific in (b) and wrong at close relatives". The narrowed version is "tested only on
  synthetic units here and on PTE by the worker".

### 3.3 FLOW vs DIFFERENCE
- E-002 (RESULT.md:69-73) makes three points:
  * FLOW = which source the operator copied a unit from; DIFFERENCE = which source's distinguishing material the child carries;
  * the FF-33 "correction" swapped one referent for the other and fixed no error;
  * NPE v0.2 uses DIFFERENCE.
- Block B (B_B1_B6_B8.md:32-39) answers "No as a distinction; yes as a lesson":
  * FLOW = IBD; DIFFERENCE = IBS at informative units;
  * "continuity/identity questions about CONTENT use DIFFERENCE; genealogy questions use FLOW";
  * do not open B8.
- Block A agrees that FLOW answers ARE facts about genealogy, not about distinguishing content (A_E002_REVIEW.md:57-58).
- Block G maps the pair onto IBD/IBS and calls it a rediscovery (G_PRIOR_ART.md:8). The ARG row is at :9, and the challenge to C-OP' at :28.
- Minor inconsistency: B_B1_B6_B8.md:28 describes clause (b) as testing a "per-child FLOW-share". But C-OP' and
  cop_prime_attack.py count k over differing units only, which is the DIFFERENCE share (cop_prime_attack.py:21, :25). The defect
  Block B identifies (per-child share vs population null) holds either way.

### 3.4 What the later campaign actually shipped (Attribution v0, on main)
- Terminology ([redacted]/attribution/ATTRIBUTION_V0.md:192-194):
  * "FLOW -> identity by descent (IBD); FLOW retired";
  * "RESEMBLANCE / DIFFERENCE -> IBS; informative sites; retired";
  * "per-unit lineage / B1 -> local ancestry, ARG". v0 records local ancestry but builds no ARG.
- Record shape: there is no parent field (ATTRIBUTION_V0.md:54). A1 rejects parent/ancestor/template keys outside aggregation
  (schema.py:54-55).
- A singular parent_id appears only as an aggregation label under rule SINGULAR_MATERIAL_PARENT. It is allowed only when one donor
  supplies >= 0.75 of the child's units AND no other donor supplies >= 0.10, which is "a declared convention"
  (ATTRIBUTION_V0.md:52; schema.py:65-66, 134-139; validator A11 at schema.py:283-291).
- The shares are IBD (FLOW) shares over ALL child units (schema.py:88-95, `donors`). They are not DIFFERENCE shares over
  informative units.
- Self-cross collapse is built in: two segments from one entity count as one donor (schema.py:89). A15 says a recombinant needs
  >= 2 distinct donors (ATTRIBUTION_V0.md:110).
- The rule has no operator-null or significance clause anywhere in v0 (schema.py:134-139).
- Second-substrate use: the assay applies the convention to [redacted] block 13 (53,185 events, native per-byte taint):
  * two or more donors in 3.3%;
  * a singular parent loses identified structure in 4.9%;
  * the other engines are "not identifiable" (ASSAY.md:23-29).
  * BEE and NPE preserved records carry no per-byte descent, and NPE's z8taint tracks the executing code (ASSAY.md:49-55).
  * Recombinant births in block 13 are 0.07% (440/655,307) (ITEM8_RESULT.md:53; ATTRIBUTION_PACKET.md:307).
- Regression cases "organism recombination, [redacted], 2 donors" and "EXTERNAL crossover, BEE" are synthetic event shapes checked by
  A11 (ATTRIBUTION_PACKET.md:216-217). The packet notes this "does NOT show v0 would have caught the errors from the data available
  at the time" (:221-222).
- Status: "attribution v0 BUILT and TESTED; two adversarial reviews". Reproduction definitions are "NOT frozen"
  (ATTRIBUTION_PACKET.md:5; ATTRIBUTION_V0.md:123).

### 3.5 Privileged operator (F2)
- E-002 found no thin-margin case in Git:
  * [redacted]'s 15 two-source events are >= 27/32;
  * NPE is decided only at donor share >= 0.906;
  * the full distributions sit on M2, not in Git (T-008_T-011_RESULTS.md:60-66).
- Block A leaves F2 "Unresolved" (A_E002_REVIEW.md:70).
- v0 sidesteps the null entirely with an operator-independent convention.
- I found no committed null for a privileged operator.

### 3.6 Label descent vs content (H-D2-37)
- [redacted], roles/[redacted]/FINDINGS.md:360-366 at HEAD (the harvest cites :362 at 345e0ceef): in anc-descended NPE runaways only 13-25% of bytes are founder
  material (z8taint). "Every 'founder-descended' statement above ... is lineage descent, not content inheritance".
- v0 answers this in form. Validator A8 says "a descent label needs a material donor ... (IBS is not IBD)" (ATTRIBUTION_V0.md:103).
- The assay then shows NPE's preserved record cannot supply material donors (ASSAY.md:25, :53). No material-share endpoint rule
  for NPE heredity claims has been adopted.

## 4. Result

| sub-question | answer from committed content | confidence |
|---|---|---|
| 1. Does C-OP' hold beyond PTE? | **No; it is superseded, not extended.** Its clause (b) fails on synthetic counter-cases that are substrate-neutral (E1b, E4, E5). The failure is structural: a per-child label is tested against a population null. No second substrate has ever tested C-OP'. The later v0 instrument drops clause (b) and keeps clause (1) (self-cross collapse) and NOT_IDENTIFIABLE | high that it is superseded in the committed record; C-OP' is formally neither adopted nor rejected by a contract revision |
| 2. Null for a privileged operator? | **Unanswered, and on the record's own logic the wrong question for a per-child label.** Block A says operator symmetry or asymmetry cannot make a realized child's content ill-posed; an operator null answers "is the operator biased" (a population question). v0 uses an operator-independent convention. A privileged-operator null (Binomial(nd, p_a)) is only meaningful for auditing the operator, and the data for that ([redacted]/BEE margins) are on M2 | medium: this is a reviewer argument plus a design choice, not an empirical result |
| 3. FLOW vs DIFFERENCE? | **Both, for different questions:** genealogy uses FLOW = IBD; content/identity uses DIFFERENCE = IBS at informative sites (Block B, Block G). v0 adopts the IBD/IBS vocabulary. **Open tension:** v0's only shipped singular-parent convention is defined on the IBD (FLOW) share over all units. So for a content question it gives the genealogy answer. Reading schema.py:134-139, E4 (child byte-identical to a, 15/16 flow from b) gets parent_id = b (0.9375 >= 0.75; 0.0625 < 0.10), where Block A's narrowed DIFFERENCE rule gives a. v0 has no DIFFERENCE-based aggregation rule | high for the division of labour; high for the tension (plain threshold arithmetic, confirmable with analysis.py) |
| 4. Graded per-unit ancestry + declared convention? | **Yes, and it is implemented in v0 for [redacted]:** per-locus IBD segments, no parent field, and parent_id only as a declared convention (0.75/0.10). No ARG is built. It "behaves" in [redacted] block 13 (3.3% multi-donor, 4.9% lossy singular parent). It is **not testable** in NPE splice cells or BEE from preserved records, because those have no per-byte descent. It has not been tested on [redacted] RECOMBINATION births specifically (0.07% of births) | medium-high |
| 5. Label descent as heredity? | **No, not without material.** The v0 validator requires a material donor for descent labels (A8). NPE's founder-descended claims are lineage-label claims ([redacted]). A cross-engine material-share endpoint is not adopted, and NPE cannot currently supply it | medium-high |

**Bottom line:** in the committed record, the singular lineage of a recombinant is an aggregation over per-unit ancestry. It must name
its referent and a declared convention; an operator-null significance test does not decide it. C-OP' clause (b) is rejected on
review. Two things remain open:
1. v0's convention is on FLOW (IBD), so the "CONTENT uses DIFFERENCE" half of Block B is not implemented.
2. The privileged-operator null and any practitioner-accepted convention remain unaddressed.

## 5. Limits
- No code was run. All numbers are quoted from committed files.
- The E4 v0 verdict in section 4 is my reading of schema.py thresholds applied to Block A's case. It is not an executed output
  (analysis.py would confirm it).
- Block A's counter-cases are synthetic (16 abstract units). Block A's narrowed rule was reviewed by no second party I could find.
- v0's 0.75/0.10 thresholds are declared, not justified. Nothing in Git calibrates them against practitioner use.
- The F2 data (the [redacted] 53,185-event margins and BEE's per-birth margins) are on M2 and not in Git (T-008_T-011_RESULTS.md:65).
- I did not search other seats' unmerged branches exhaustively. The one I checked ([redacted]/e003) has nothing beyond HEAD.

## 6. What would change the conclusion
- **A contract revision** adopting C-OP' clause (b), or a v1 aggregation rule defined on DIFFERENCE shares, would change answers 1
  and 3.
- **Running out/analysis.py:**
  * if v0 returns `b` on E4 while the DIFFERENCE convention returns `a`, the FLOW/DIFFERENCE tension in v0 is confirmed;
  * if it returns `a`, my reading of schema.py is wrong and the tension claim should be withdrawn.
  * For E3b, compare p under p_a = 0.5 with p under p_a = 0.9. A large p under 0.9 and a small p under 0.5 shows the privileged null
    only relocates the question to operator bias.
- **F2 margins from M2:**
  * if [redacted] or BEE privileged-operator events cluster near the 0.75/0.10 boundary, the choice of convention becomes
    outcome-determining for establishment counts;
  * if they stay >= 27/32 as in the 200-event sample, F2 is empirically moot there.
- **A per-byte material-taint replay for NPE** (T-003 births) or BEE, as recommended in ASSAY.md:56, would make the per-unit
  convention testable in a second and third engine, including NPE splice cells.



======== REPORT X013 ========

# [redacted] [redacted] [redacted]: exp one-class collapse, and whether the signed-margin curve transports

[redacted]

## Question

- **H-D4-63.** Which entries of exp's rule table cause its N-dependent collapse to "all ones", which appears between N=149 and N=599 and saturates by N=999? The companion question: does the particle1 non-convergence row (1 IC of 100, with 100/149 cells still flipping at T=298) replicate on 5 more seeds?
- **H-D4-64.** Does `acc = sum_k P_ens(k) c(k)` carry beyond density-CA, so that a task ensemble acts on a phenotype only through a scalar statistic? And is maj's boundary shift m*(N) (THEO-CAND-003) real once there are about 10x more ICs?

## Short answer

1. **Which exp entries cause the collapse: still unanswered at `5266ccebe`. No ablation has ever been run.** The library can now build the intervention. `derive_edit`/`derive_flip` are in `herakles/evca/derive.py:134-168`, and Vivarium says derived rules run unchanged (`roles/Vivarium/STATUS.md:102-103`). But no fossil, ledger row or result file in the repo holds an exp child. The only `edit_entries` record anywhere is a Proteus mint rehearsal on the **GKL** table (parent `evca:r3:005f005f…`, edit `[11,0]`, namespace `test`): `proteus/integration/RESULT_MINT_ROUNDTRIP_TEST.json:11-28,36`. The 128-cell scan that THEO-REQ-005 promised (`roles/Theophrastus/reqs/THEO-REQ-005_table_level_intervention.md:29-31`) is written out as analysis.py Part C.
2. **The phenotype is well supported, with three qualifications the harvest entry does not carry:**
   - (a) **"Collapses to all ones" is an inference; the committed data only shows failure on the zero side.** The per-IC files store only `success`. Failing ICs are never split into "all ones" versus "not uniform" (`theophrastus/dissect.py:65-81`). Fossils carry only `all_ones_fixed` (a property of the rule table), not the final state.
   - (b) **Where the collapse begins is not located.** The only lattice sizes in the repo are N ∈ {149, 599, 999}. Searches for any other N under `roles/Theophrastus` found no rows. "Between 149 and 599" is the whole resolution.
   - (c) **One pre-registered prediction failed, but a later write-up lists its observed value as "predicted".**
     - ADAPTIVE_RECORD_02 predicted 0.3042 for exp/W599/P_d40 and observed 0.3475. Its own pass rule (tolerance 0.034) gives `pass: false`: `roles/Theophrastus/crucible/round2/ADAPTIVE_RECORD_02.json:69-93`.
     - SPEC-001 counts this correctly as a miss (`SPECIMENS_ROUND2_2026-09-14.md:37-39`).
     - SPEC-002, however, lists ".35 (d=.40) … (predicted; observed 1.000 and .3475)" (`:116-118`).
     - Also, "saturated 599→999" (chi2 12.4/23, `ROUND2_SCORE.json:614-622`) sits beside a failed 599-curve prediction for exp W999 P_unif: 0.7887 observed vs 0.8228 predicted (`ROUND2_SCORE.json:515-531`).
3. **particle1 replication: not run.** It is still an open box in `roles/Herakles/todo_2026-09-16.md:35-39`. The committed row fits exactly one bad IC. `mean_flip_fraction` = 0.0067114 = (100/149)/100 (`herakles/evca/sync_floor_2026-09-16.json:335-340`). This is analysis.py Part E.
4. **Transport of the curve to other kinds: untested. At this commit no registered kind could test it.**
   - The registered kinds are `noop_v0`, `evaluate_bitstring`, `[redacted].probe.v0` (retired), `random_walk_v0`, `ca_density_v0`, `artifact_probe_v1`, `cegis_boolean_v1` and `eca_rule_eval_v1` (`vivarium/viv/kinds.py:209-594`).
   - Only `ca_density_v0` samples inputs from an ensemble and scores a classification.
   - `eca_rule_eval_v1` is exhaustive and says "IT REPORTS THE OBSERVABLE, NOT A SCORE" (`kinds.py:584-592`).
   - `cegis_boolean_v1` covers all 8 assignments exhaustively (`kinds.py:521-524`).
   - The only transport ever shown is across *consumers* (Vivarium fossils, 150/150, at N=149): `SPECIMENS…md:164-178`.
5. **A logical point that narrows H-D4-64.**
   - For any generator that is uniform over arrangements once k is fixed (every Bernoulli mixture), the decomposition is an identity by exchangeability. The specimen says so itself (`SPECIMENS…md:43-44`). Its "transport" to another task is automatic whenever such a statistic and generator exist.
   - The empirical content is (i) whether k stays **sufficient for non-exchangeable generators**, and (ii) whether c carries across N.
   - (ii) is already known to fail quantitatively (`SPECIMENS…md:56-63`; GKL W999 0.7925 observed vs 0.7236 predicted, `ROUND2_SCORE.json:532-548`).
   - (i) has never been tested. It can be tested inside `ca_density` today with blocky fixed-k ICs (analysis.py Part D).
6. **maj m*(N): still a candidate.** No ICs were added after round 2. The specimen's own stop reason is that "discrimination [is] below binomial resolution without ~10x more ICs at m in [.25,.35]" (`SPECIMENS…md:150-152`), and both constructive predictions at the boundary missed by 2-3 SE (`ROUND2_SCORE.json:378-411`). analysis.py Part A2 bootstraps m*(149) and m*(599) from the committed per-IC data and reports the ICs needed.

## Method

- Read the source specimen, THEO-REQ-005, the Herakles derive library and todo, and the Vivarium status and kind registry.
- Read the round-2 evidence files: `stepA_tests.json`, `ROUND2_SCORE.json` and `ADAPTIVE_RECORD_02.json`, plus the schemas of `per_ic*.jsonl`.
- Searched the whole tree for any `edit_entries` artefact or exp child, any lattice size other than 149/599/999, and any other kind that classifies inputs.
- Checked `rogit log --since=2026-09-15` for `roles/Theophrastus`, `theophrastus/` and `herakles/evca/derive.py`. The only later commits are other seats' inbox files and Herakles's derive delivery: dbc41fd2f, bfe8f0bd8, 13000800f. None comes from Theophrastus and none is an experiment. The Theophrastus journal ends at `journal/2026-09-14.md`.

## Evidence (key numbers)

| claim | value | citation |
|---|---|---|
| exp zero-side vs one-side success at \|m\|<.01, N=149 | .367 (n=188) vs .674 (n=178), z −5.9 | `roles/Theophrastus/crucible/round2/stepA_tests.json:2690-2703` |
| same, N=599 | .0043 (n=461) vs .9911 (n=450), z −29.8; 13/23 bins \|z\|≥3 | `stepA_tests.json:2843-2857` |
| exp N=999 asymmetry | max \|z\| 19.6, chi2 850.8/7 | `ROUND2_SCORE.json:657-664` |
| exp curve 599 vs 999 by \|m\| | chi2 12.4/23, max \|z\| 1.51 | `ROUND2_SCORE.json:614-622` |
| exp W999 P_iid pred from 599 curve | .5262 obs vs .5303 pred, pass | `ROUND2_SCORE.json:498-514` |
| exp W999 P_unif pred from 599 curve | .7887 obs vs .8228 pred, **fail** | `ROUND2_SCORE.json:515-531` |
| exp W599 d=.40 retry | .3475 obs vs .3042 pred, **fail**; CHEAT-B curve (.9998) misses | `ADAPTIVE_RECORD_02.json:69-93` |
| exp W599 d=.60 | 1.000 vs 1.000 | `ROUND2_SCORE.json:259-275` |
| published exp P | .652 / .515 / .503 at 149/599/999; labelled "block-expanding" | `herakles/evca/genomes.py:52-56` |
| par asymmetric the other way; particle1 symmetric | par N599 max\|z\| 10.15; particle1 max\|z\| 2.12 / 0.91 | `stepA_tests.json:3535-3538`; `ROUND2_SCORE.json:584-598` |
| horizon not a cause | bit-identical at half the steps (exp, par) | `ROUND2_SCORE.json:412-441`; `SPECIMENS…md:50-52` |
| cause of the collapse | "UNKNOWN at the rule-table level" | `SPECIMENS…md:119-123,138-139` |
| intervention library delivered | derive_edit / derive_flip | `herakles/evca/derive.py:134-168`; `roles/Herakles/todo_2026-09-16.md:21` |
| Vivarium half | "derived rules run unchanged" | `roles/Vivarium/STATUS.md:102-103` (commit cdb7d3850) |
| no exp ablation exists | only edit_entries record is on GKL, test namespace | `proteus/integration/RESULT_MINT_ROUNDTRIP_TEST.json:11-37` |
| per-IC files store success only | `correct = where(target==1, ones==N, ones==0)`; only `success` written | `theophrastus/dissect.py:65-81` |
| particle1 outlier unreplicated | unchecked todo item | `roles/Herakles/todo_2026-09-16.md:35-39`; `herakles/evca/sync_floor_2026-09-16.json:331-341` |
| transport status | "To other kinds: UNTESTED" | `SPECIMENS…md:67-72` |
| cross-consumer transport | 150/150 bit-exact, N=149 | `SPECIMENS…md:164-178` |
| no other classification kind | registry | `vivarium/viv/kinds.py:209-594` (eca: 572-594; cegis: 479-568) |
| curve not portable across N | GKL W999 .7925 vs .7236 | `ROUND2_SCORE.json:532-548`; `SPECIMENS…md:56-63` |
| maj boundary candidate | m*≈.27 at 149, ≈.30 at 599; 2/2 boundary predictions missed | `SPECIMENS…md:143-152`; `ROUND2_SCORE.json:378-411` |

## Result

- **H-D4-63: OPEN.**
  - The genotype→phenotype question has not been attacked. It became *executable* on 2026-09-16 (library dbc41fd2f, Vivarium cdb7d3850), but nobody submitted the scan.
  - The phenotype side (strong zero-side failure at N≥599, and the detector) stands at high confidence.
  - "Collapse to all ones" should be downgraded to "near-total zero-side failure" until the final states are recorded.
  - The onset window is only as fine as the three sampled N.
  - particle1: OPEN, one row.
- **H-D4-64: OPEN / UNTESTED** for other kinds, and there is structurally no registered kind to test it on.
  - The decomposition is exact for exchangeable ensembles on any task, so the question that is still open and testable is whether k is sufficient beyond exchangeable ensembles.
  - That can be tested inside ca_density now (analysis.py Part D).
  - Across N the curve carries in *form* but not in *value*, and that part is already settled negatively.
  - maj m*(N): CANDIDATE, unchanged.

## Limits

- No code was executed, so every quantitative statement here is quoted from committed files.
- I did not re-verify SPEC-001/002's own statistics against per_ic.jsonl; analysis.py Part A would.
- I did not confirm that per_ic.jsonl and per_ic_round2.jsonl are disjoint (see the dedupe note in Part A).
- The absence of an exp ablation is based on repo-wide searches for `edit_entries`, the exp hex and REQ-005 references. An ablation run outside the repo, or on an uncommitted branch, would not show up.
- "Theophrastus inactive" means only that no seat-authored commit after the 2026-09-14 journal was found under `roles/Theophrastus`.

## What would change the conclusion

- **analysis.py Part C** (128 single flips at N=599):
  - ≥1 flip that lifts zero-side success to ≥0.5 while keeping one-side success ≥0.9 localises a necessary ingredient and answers H-D4-63 at single-entry resolution.
  - Zero such flips means the collapse is spread over several entries; the next step is pairwise flips ranked by usage on failing runs.
- **Part B:**
  - If most zero-side failures at N≥599 are non-uniform final states, the "constant classifier / all ones" description is wrong in mechanism, although the accuracy argument still holds.
  - A sharp longest-1-run threshold that is stable across N would explain the N-dependence as an opportunity count, like the maj story in THEO-CAND-003.
- **Part D:** if blocky fixed-k ICs give the same success as uniform fixed-k ICs within 2 SE for every rule, then k is a genuinely sufficient scalar and the curve is a stronger curriculum knob. If they differ, transport is limited to Bernoulli-type generators.
- **Part E:** recurrence in ≥2 of 5 new seeds makes particle1's non-convergence a rate finding that bears on its at_T numbers. Zero recurrences in 500 ICs retires it as a single row.
- **Part A2:** disjoint 95% bootstrap CIs for m*(149) and m*(599) would promote THEO-CAND-003 without new runs. Otherwise the run needs roughly 10x the ICs per bin in [.25,.35], as Part A2 will quantify.
- Registering any new kind that samples inputs and scores classification (e.g. a scored synchronisation kind over `core.synchronisation_score`) would make cross-kind transport testable for the first time.



======== REPORT X015 ========

# [redacted] — Residual bridges (H-D5-56) and incidents as splittable hypotheses (H-D5-55)

Repo: read-only checkout at 5266ccebe. All citations are `path:line` at that commit unless a different commit is named. I did not run any code.

## Questions
1. **H-D5-56.** If residuals from all engines are clustered by failure signature, do shared signatures point to shared mechanisms? And has any such clustering been built and checked against a family-shuffled null?
2. **H-D5-55.** Should causal-lineage clustering treat each incident as a hypothesis ("these observations share one cause"), with split() so that one failure cannot hide another? And once a live population exists, does adversarial ancestry predict which descendants break?

## Method
- Read the sources the harvest names: the residual spec, the Hermes convergence probe, and the Nemesis archaeology.
- Searched the repo for anything that implements or tests these ideas: CLUSTER_RESIDUALS, failure_signature, residual stores, split() callers, incident files, and ancestry data in Ares and Nemesis.
- Found an implementation the harvest missed: [redacted]'s cross-agent failure-primitive atlas. Read it in full.
- Checked the one run under [redacted]'s null ladder.
- Wrote `analysis.py` for the only lineage-versus-breakage computation the repo can support. It is not run.

## Evidence

### A. CLUSTER_RESIDUALS was never built, and no residual corpus exists to cluster
- The spec defines `CLUSTER_RESIDUALS`. A cluster needs ≥3 residuals from independent claims with cosine > 0.8 in failure_signature space (`[redacted]/memory/architecture/residual_primitive_spec.md:178-185`). The spec's only example is labelled "Hypothetical" (`:191`).
- The spec's own status section lists CLUSTER_RESIDUALS and the null-baseline pilot as "still spec-only" (`:218-221`), and "Out of scope for first pass; do it manually" (`:230`).
- `sigma_kernel/residuals.py` has no `failure_signature` field. It stores a `failure_shape` JSON string in a SQL table (`sigma_kernel/residuals.py:137,187-202`).
- I found no committed residuals database or dump from real engine runs. `record_residual(` is called only from tests and benchmarks (search result; absence is not proven from git history).

### B. What did get built: agent-level failure-shape clustering with an independence rule
- [redacted] Proposal D (`[redacted]/proposals/2026-06-09/D_cross_agent_failure_primitive_atlas.md:59`) became `[redacted]/primitives/failure_primitives.py`. It is the H-D5-56 idea lifted from claim residuals to agent failures.
- Its null-like safeguard is **lineage independence**, not shuffling. Anchors that share a code or authorship lineage count once (`failure_primitives.py:12-14,76-86`).
- State as of the last registry commit (2026-06-15):
  - FP-003 bounded_menu_wall: **coordinate_invariant**. It has 3 lineages judged code-disjoint by import analysis (`:386-478`).
  - FP-001 baseline_costume: surviving_candidate, 2 lineages (`:324-343`).
  - FP-004 degenerate_field_flatline: surviving_candidate. It has 4 anchors, but the independence audit "was NOT run (blocked by the Anthropic spend limit)" (`:532-542`).
  - FP-002 opaque_kill_black_hole: shadow, 1 anchor (`:361-373`).
  - 89 further candidate shapes are "mostly unaudited shadows" (`:546`).
- **Answer to "do shared signatures point to shared mechanisms?" — for the one invariant shape, NO.**
  - FP-003's three anchors have three *different* mechanisms: region_empty, source_saturated and expressiveness_ceiling (`:444-448,479-490`).
  - Two of them call for *opposite* remedies (STOP versus GROW). The atlas flags this as the "SHARPEST OPEN CRITIQUE" and still owes a subclass-discriminator probe (`:471-478`).
  - The atlas explicitly reads heterogeneous causes under one shape as *strengthening* shape invariance (`:446-448`). So what it shows is a shared observable. It does not show a shared mechanism.
- Later evidence ([redacted], September):
  - FP-001, FP-003 and FP-004 recurred in September engines, and each recurrence was "rediscovered without citation" (`roles/[redacted]/challenge/FAILURE_PRINCIPLES.md:867-898`).
  - The September data add a fourth FP-003 cause, "expressible but unreachable". They also falsify FP-003's predicted GROW escape: growing the menu still gave 0/4,881 useful children (`:877-885`, FR-132).
  - So the shape recurs, the mechanism under it keeps splitting, and the remedy the shape attached did not transfer.

### C. The family-shuffled null has been run exactly once, and it came out NULL
- Null-2 ("operator-/family-shuffled near-math … beating THIS is what means something") is defined at `[redacted]/docs/failure_signal_protocol_v0.1.md:221-224`.
- It was run once, frozen before the run, as H5a OEIS MVP (`[redacted]/results/h5_oeis_mvp_2026_06_04.json:2-3`). Real lift@100 was 200.1 against 169.1 under the operator-shuffle null; verdict **NULL** (`:185-189`).
- The file also records "Family metadata absent … holdout is random" and 3 of 5 controls as STUB (`:24-30,190`).
- This is not a residual clustering. It is still the only committed execution of the null that H-D5-56 says the idea needs.
- No failure_signature cluster from any engine has been tested against a family-shuffled null.

### D. Splittable incidents: built and tested on fixtures, never used on a live incident, and the one live incident already gathers several causes
- The probe establishes the design: a symptom key can gather two causes (CTL-2), so an incident is a HYPOTHESIS. split() moves observations with pointers both ways and no loss, tested as 5 = 3 + 2 (`roles/Hermes/CONVERGENCE_PROBE_2026-09-11.md:65-70,174-179`). Code: `roles/Hermes/science/convergence/record.py:125-154`.
- split() is called only in the test (`roles/Hermes/science/convergence/test_convergence.py:204`, search result).
- The single live incident is `roles/Hermes/incidents/c84e26826cc12217.md`. It is a hand-kept OCCURRENCES table with 11 entries from 2026-09-11 and 2026-09-16, not record.py's format (`:25-52`). No split was ever performed on it.
- Under one symptom key, it records at least three distinct fix paths:
  - comms, closed structurally (`:56-62`)
  - Evidence Wiki, OPEN, accepts writes silently (`:63-71`)
  - Vivarium's viv/db.py, which "had NO guard", fixed in place (`:44-49`)
- This is the CTL-2 situation occurring for real: several causes under one key, resolved by annotation, never split.
- The probe's own falsifier for the design, "seats do bury one failure inside another despite split()" (`CONVERGENCE_PROBE:263-267`), has therefore not been tested. Nobody has used split() yet.

### E. Adversarial ancestry: no live population, and ancestry data are either unused or not saved
- Nemesis: "52 of 92 records carry lineage_depth > 0 and no use was ever made of them." NEM-A4 is PARKED because there is no live population (`roles/Nemesis/ARCHAEOLOGY_2026-09-11.md:145`).
- The ledger is a negative fixture:
  - 292 of 294 tools score below a constant "Not enough information" responder (`:71-89`).
  - Confidence is not discriminative (`:93-96`).
- Each record does carry `lineage_depth` and `tools_broken` (`agents/nemesis/adversarial/adversarial_results.jsonl`, record 1).
- Ares builds a full population ancestry map in memory (`ares/search.py:230,288`) but returns only the champion's chain (`:295-305`).
- Descendant breakage is kept only as a pooled per-generation `mutation_survival` (`:242-247`). The committed `ares/runs/sweep_c1/*_ancestry.json` files hold champion curves and accretion counts, nothing per descendant (search result).
- So no committed data can say whether ancestry predicts which descendants break.

## Result
1. **H-D5-56: NOT ANSWERABLE AS POSED. The adjacent evidence is negative on "shared signature ⇒ shared mechanism".**
   - Residual-level clustering was never built, and no residual corpus exists.
   - The agent-level version (the FP atlas) found one coordinate-invariant shape. Its anchors have 3 or 4 different mechanisms with opposite remedies, and its predicted remedy failed on September data.
   - The one family-shuffle null ever run came out NULL.
   - Within this repo, a shared failure signature has been a good *triage/detector* key and a poor *mechanism* key.
   - The harvest's "later evidence: none found (never built)" is wrong in one respect: the FP atlas (June) and the [redacted] recurrence audit (September) are relevant later evidence.
2. **H-D5-55, first half: YES on design grounds, still unvalidated in use.**
   - The one live incident shows the problem split() exists for: several causes under one symptom key, handled by prose annotation.
   - split() has never been exercised, and the "seats read `prior`" and "don't bury" falsifiers are unmeasured.
   - The FP-003 STOP/GROW collision is the same problem one level up. The atlas has no split operation, only prose subclasses.
3. **H-D5-55, second half: UNTESTABLE on committed data.**
   - There is no live population. The only ancestry-bearing ledger is a negative fixture, and Ares discards non-champion ancestry.
   - `analysis.py` sets out the only possible check, on the Nemesis ledger, with a pre-fixed rule. Even a positive result there would be a lead, not an answer.

## Limits
- My "never built / never used / no data" claims rest on repo-wide text search at 5266ccebe. I did not check full git history, and uncommitted artifacts (e.g. Nemesis's untracked `reports/`, `nemesis.log`) are invisible to me.
- Most FP-atlas independence rulings were done by [redacted] on itself. FP-003's third anchor used a local audit, not the multi-probe one (`failure_primitives.py:457-461`).
- H5a is an OEIS void-recovery test, not residual clustering. I cite it only as the precedent for the required null.
- I did not verify the [redacted] recurrence mappings (R-numbers, FR-132) against their primary artifacts.

## What would change the conclusion
- A committed residual store from ≥2 engines, clustered by failure_signature, where a cluster beats a family-shuffled (Null-2) baseline *and* the members share a mechanism confirmed by an intervention. That would turn H-D5-56 positive.
- A subclass-discriminator probe showing FP-003's causes separable from the event series alone. That would show one signature can carry the mechanism (the probe owed at `failure_primitives.py:477`).
- A real split() on c84e26826cc12217 (e.g. comms / EW / viv), or evidence that some seat buried a cause despite split(), would test H-D5-55's design.
- Ares persisting the full `ancestry` dict plus per-child fitness, or a revived Nemesis population that beats its constant-responder floor. Either would make the ancestry question testable. Running `analysis.py` gives only a fixture-bound hint. Its verdict is decided by the pre-fixed rule in its docstring (p < 0.01, rho > 0, ≥ 20 effective depth>0 records within NEI×category strata).

