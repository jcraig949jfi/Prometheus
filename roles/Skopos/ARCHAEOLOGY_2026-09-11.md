# Skopos -- archaeology of the March 2026 seat

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Author: Skopos, on its own adoption pass. CONFLICT OF
INTEREST: the subject is the author (RESPONSIBILITIES.md section 6). Every
finding below is adverse to this seat; that is the only direction a
self-audit runs in credibly. An independent pass is SKOPOS-08.

Built from base_sha 363120e08665af062d40810183624fa23ed19698, branch
skopos/base-role-adopt-2026-09-11, worktree Prometheus-worktrees/
skopos-base-role, dirty: no tracked changes at the time of measurement.

Base role: "BOOTING AN OLD SEAT IS AN ARCHAEOLOGICAL EVENT, not an
instruction to resume its last queue." This file is that event.

--------------------------------------------------------------------------
## 1. What existed, and for how long

    2026-03-23 21:21:11Z  first and only scoring write (5 rows)
    2026-03-23             first alignment report
    2026-03-24             committed (7e9719cb0, "Bulk commit: ... Skopos
                           agent, docs, and session artifacts")
    2026-03-27             the research-thread list rewritten in code
                           (8af6ba9e5)
    2026-04-01 07:24Z      last alignment report; last run of any kind
    2026-04-03 11:53Z      last commit touching agents/skopos (b674a9976):
                           README ONLY, +45/-6 lines, elaborating the
                           two-stage design and the Titan-prompt output.
                           The documentation grew two days AFTER the last
                           run, describing behaviour that had never once
                           occurred.
    2026-09-11             this pass. 163 days dormant.

Tracked surface, entire lifetime (git ls-files):

    agents/skopos/README.md
    agents/skopos/configs/skopos_config.yaml
    agents/skopos/data/scores.db
    agents/skopos/src/skopos.py
    + 6 files under agents/skopos/reports/

--------------------------------------------------------------------------
## 2. What it actually produced -- the rows

Command:

    python -c "import sqlite3; c=sqlite3.connect(
      'agents/skopos/data/scores.db');
      print(c.execute('select count(*) from skopos_scores').fetchone())"

Result: 5.

The five rows, in full, are the seat's entire lifetime output:

    id type   entity_id name               thread_id                 score
    -- ------ --------- ------------------ ------------------------- -----
     1 tools  19        Circuits Zoom-In   anti_cot_geometry             2
     2 tools  19        Circuits Zoom-In   precipitation_signatures      3
     3 tools  19        Circuits Zoom-In   tensor_decomposition          2
     4 tools  19        Circuits Zoom-In   sae_features                  3
     5 tools  19        Circuits Zoom-In   scale_threshold               2

    all scored_at 2026-03-23T21:21:11.728455+00:00
    all rationale identical (one LLM call, one entity, five threads)

ONE ENTITY. Not five. One tool, scored once against five threads, in a
single call, on the first day, and never again.

The eligible population in the upstream it read
(agents/aletheia/data/knowledge_graph.db, the five tables skopos.py names
in `entity_tables`):

    techniques           93
    terms               224
    claims               76
    tools                41
    reasoning_motifs     14
    ------------------------
    total eligible      448

    papers processed = 1                163
    earliest processed_at   2026-03-22T20:53:46Z
    latest   processed_at   2026-04-01T07:22:11Z

Coverage, lifetime: 1 / 448 = 0.22%.

The GENERATE stage -- the half of the design that was to write Titan
Council prompts -- required a score of 4 or more. No row ever reached 4.
`git ls-files docs/titan_prompts` returns nothing: the output directory was
never created. That branch of the program has never executed, not once, and
was never tested. Lifetime Titan prompts: 0.

--------------------------------------------------------------------------
## 3. The defects, with the line that causes each

### D1 -- the published number counted rows and called them entities

agents/skopos/src/skopos.py:510-511

    total    = "SELECT COUNT(*) FROM skopos_scores"
    relevant = "SELECT COUNT(*) FROM skopos_scores WHERE score >= 3"

printed as

    f"**{total} scored entities | {relevant} relevant (3+) | ..."

The table's grain is (entity, thread). `COUNT(*)` is entity-thread PAIRS.
With five threads configured the count is inflated 5x by construction.
Every report this seat ever published said "5 scored entities". The true
value is 1. "2 relevant (3+)" is the same single entity counted twice.

This is the ONLY number Skopos ever published about itself, and it was
wrong by 5x in the favourable direction. It is the seat's own instance of
the base role's rule 2, one layer in from where that rule usually bites:
not a tool's self-reported status, but a seat's self-reported yield.
Nothing in the pipeline could have caught it, because nothing else counted
the same quantity.

### D2 -- the dedup key omitted the thread, so new threads were unreachable

agents/skopos/src/skopos.py:130-136

    SELECT 1 FROM skopos_scores WHERE entity_type = ? AND entity_id = ?

while the table declares

    UNIQUE(entity_type, entity_id, thread_id)

The storage grain is (entity, thread); the skip decision is taken on
(entity) alone. Once an entity had been scored against ANY thread it was
skipped for ALL threads, for ever -- including threads that did not exist
when it was first seen. Adding a research thread therefore could not pick
up a single entity the seat had already touched. Only `--rescore-all`
could, and it was never run.

### D3 -- the scoring key lived in code while a config file claimed to hold it

agents/skopos/src/skopos.py:64 `RESEARCH_THREADS = [...]`
agents/skopos/configs/skopos_config.yaml, verbatim:

    # Research threads - update here when priorities shift
    # (Currently hardcoded in skopos.py for speed; this file is for
    #  reference)

Between the 2026-03-25 report and the 2026-03-27 report the thread list was
replaced wholesale in code (commit 8af6ba9e5). The old thread_ids
(anti_cot_geometry, precipitation_signatures, tensor_decomposition,
sae_features, scale_threshold) vanished from RESEARCH_THREADS; the five
rows keyed to them stayed in the database, orphaned and unreadable by the
report writer, which iterates `for t in RESEARCH_THREADS`.

No migration. No supersession marker. No error. The rows are still there
today, keyed to threads that have not existed since March.

### D4 -- the eligibility window, not the judgement, decided what was seen

agents/skopos/src/skopos.py:143-198, `load_recent_entities(since_hours=24)`
selects papers with `processed_at >= now - 24 hours`, then keeps entities
whose `source_papers` list intersects those papers. Combined with D2, the
reachable set after day one was approximately empty: anything old was out
of the window, anything already seen was skipped, and a new thread could
rescue neither.

The seat's coverage was therefore set by an eligibility rule, not by
relevance, and the reports it wrote were titled "alignment" -- a claim
about relevance -- with no eligible count anywhere on them. The base role's
rule is explicit: "'Nothing fired' and 'nothing could have fired' are
different facts and both are always reported." Skopos reported neither, and
the report it did write could not distinguish them.

### D5 -- the report contradicted itself for four consecutive runs

The six reports, headers and bodies:

    report      header                   per-thread body
    ----------  -----------------------  --------------------------------
    2026-03-23  5 scored entities | 2    5 threads, 1 entity each, 2..3
    2026-03-24  5 scored entities | 2    identical to 03-23
    2026-03-25  5 scored entities | 2    identical to 03-23
    2026-03-27  5 scored entities | 2    ALL 5 threads: 0 entities, max=0
    2026-03-31  5 scored entities | 2    ALL 5 threads: 0 entities, max=0
    2026-04-01  5 scored entities | 2    ALL 5 threads: 0 entities, max=0

From 03-27 the document asserts "5 scored entities" in bold on line 4 and
"0 entities" on every thread line below it. The two halves read different
keys (D3): the header counts all rows, the body counts rows per CURRENT
thread. A reader had both numbers on one screen. The contradiction survived
three more runs and 163 days until this pass.

Note also the first three: byte-identical below the date line. The loop
exited 0 daily while rewriting the same artifact -- the same signature the
base role's rule 8 was written for, and the same one Eos's registry row
records for its own digests.

### D6 -- liveness was only readable by reading the output, and the output looked the same either way

No last_input_at, no last_success_at, no no-op reason, anywhere. The only
freshness record Skopos ever produced was the report itself, and a report
from a working scorer and a report from a scorer that had scored nothing
for ten days were byte-identical below the date line.

Meanwhile the orchestrator published a health verdict. From
agents/pronoia/logs/audit_2026-03-24_003808.md, line 10, verbatim:

    - **skopos**: OK

That line is true and useless in exactly the way base rule 7 names: the
process ran and exited 0. It says nothing about rows. A health check that
reads OK across the entire productive death of the thing it checks is not a
health check. Silence was read as health for ten days and then for 163 more.

### D7 -- the score gated an artifact with no predicate and no human

By design (README, "Stage 2: GENERATE"), a model's 0-5 relevance score of 4
or more was to trigger automatic synthesis of a prompt for frontier models.
No deterministic predicate, no human admission step. This contradicts the
base role's "No LLM adjudicates" and it never came up in March because the
trigger never fired -- the design defect was masked by the coverage defect.

--------------------------------------------------------------------------
## 4. What propagated downstream

agents/metis/src/metis.py:94-103 globs `agents/skopos/reports/*_alignment.md`,
takes the newest, and appends it to the LLM context for the executive brief
under the heading "RESEARCH THREAD ALIGNMENT (from Skopos)". The `except:
pass` on line 103 comments "Skopos not available - that's fine".

So the self-contradicting report was loaded as context into every Metis
brief run from 2026-03-27 to 2026-04-01.

Whether it changed any brief: UNMEASURED. Grepping the eight briefs in
agents/metis/briefs/ for `skopos|alignment|starv|scored entit` returns
nothing, so the numbers do not surface in the brief TEXT. That bounds the
visible contamination; it does not establish that the context had no
effect, and this seat will not claim it did. The honest statement is: the
false number was fed to a model five times and no brief quotes it.

roles/PipelineOrchestrator/DESIGN_bidirectional_skopos.md (2026-04-02, the
day after the last run, by PipelineOrchestrator) proposes building three
further loops ON TOP of this scorer, including automatic routing of its
score-4+ entities into other seats' inboxes. Its phase table says
"Tomorrow", "Next week", "Next month". Nothing in it was built. It was
written about an instrument that had by then scored one entity, and it does
not mention a coverage number, an eligible count, or a control. It is
recorded here as residue and as evidence of how far a design can travel
from a dead instrument in 24 hours.

--------------------------------------------------------------------------
## 5. The old queue, classified (base role: the mandatory adoption step)

Every item Skopos carried on 2026-04-01, against the current north star.

    item                                       class
    -----------------------------------------  ----------------------
    Score Aletheia entities daily against the  RETIRED. Upstream
    five Ignis/steering-vector threads         (Aletheia) last wrote
                                               2026-04-01; the invoker
                                               (Pronoia) is not in the
                                               tree; the consumer
                                               (Metis) last wrote
                                               2026-04-01. All three
                                               links dead. Base rule 9.

    Generate Titan Council prompts on any      RETIRED, and on two
    score of 4+                                grounds: never executed
                                               once, AND the design
                                               lets a model score gate
                                               an artifact with no
                                               predicate (D7), which
                                               the base role forbids.
                                               The Phalanx strategy it
                                               served is not a current
                                               program lane.

    Feed alignment context to Metis            RETIRED. Consumer dead;
                                               and what it fed was
                                               wrong (D1, D5).

    The five March research threads            SUPERSEDED. Both lists.
    (anti-CoT geometry, precipitation          The steering-vector and
    signatures, tensor decomposition, SAE      forge-era questions are
    features, scale threshold) AND the         not the current program's
    2026-03-27 replacements (ejection          questions.
    mechanism, CMA-ES/LoRA, Forge+Sphinx
    eval, knowledge substrate, scale
    transfer)

    DESIGN_bidirectional_skopos.md: pillar     SUPERSEDED. Its pillars
    threads, pillar inboxes, reverse flow,     (Charon zero-geometry,
    auto-generated threads                     Noesis primitives, Forge
                                               gap categories) are March
                                               structure; comms is now
                                               the routing substrate and
                                               it is owned by Archaeon.
                                               Nothing in it is this
                                               seat's to build.

    The function "decide what deserves         NEEDS_REPREMISE. The only
    attention", stripped of its March          live thread. Restated in
    wiring                                     RESPONSIBILITIES.md
                                               section 3 as the
                                               INSTRUMENTATION of
                                               selection rather than
                                               selection, and gated
                                               behind SKOPOS-XL-01.

    -----------------------------------------------------------------
    STILL_LIVE: 0 items. Nothing from the old queue is executable work.

--------------------------------------------------------------------------
## 6. What this seat is not claiming

- Not claiming the LLM's judgement was bad. It was exercised once, on one
  tool, and produced five plausible-looking scores. n = 1. There is no
  basis to say anything about the quality of the scoring, in either
  direction, and this seat will not defend it either.
- Not claiming Metis was harmed. See section 4: unmeasured.
- Not claiming the seat was sabotaged or starved by others. The upstream
  had 448 eligible entities and 163 processed papers. The input was there.
  The instrument did not look at it.
- Not claiming these defects are novel. D1 is a units error, D2 a key
  mismatch, D6 a missing freshness record. They are ordinary. That is the
  point: an ordinary units error in the only number an instrument publishes
  about itself is invisible for 163 days when nothing else computes the
  same quantity, and a health check saying OK actively conceals it.

--------------------------------------------------------------------------
## 7. The one transferable thing

Skopos was the seat whose job was to notice what matters, and it could not
notice that it had stopped working. It had a daily report, a health check,
a downstream consumer and a follow-on design, and all four were compatible
with zero production.

The generalisable form, offered to whoever wants it and claimed as a lane
by nobody today:

    An instrument that publishes a YIELD must publish the ELIGIBLE
    COUNT beside it, in the same units, in the same artifact. Without
    the denominator, "5 scored" and "0 scored" are the same document,
    and every downstream reader -- human, model, or health check --
    will read the one that looks like work.
