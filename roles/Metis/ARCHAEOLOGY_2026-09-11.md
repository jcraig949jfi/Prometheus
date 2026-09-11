# Metis archaeology -- two code bodies, one name, classified

Currency: 2026-09-11. Written on the seating pass, under the base role's
rule that BOOTING AN OLD SEAT IS AN ARCHAEOLOGICAL EVENT: every item of
the old queue is classified against the current north star, and only
STILL_LIVE becomes executable work. NOTHING HERE WAS EXECUTED. No
daemon was started, no brief was generated, no file under agents/metis/
or scripts/ was modified.

Provenance grades used below:
  COMMIT    read from a commit in this repository (SHA given)
  MEASURED  read from a file or computed on this pass (command given)
  DOC       read from a committed document
  RECALL    remembered, not verified -- cited as such, never as fact

Nothing in this document is graded RECALL. The seat has no memory of
its own operation; every statement below was read or computed today.

## 0. The seat's lifetime in one paragraph

Metis was built in March 2026 as step 4 of the Pronoia serial
intelligence pipeline (Eos -> Aletheia -> Skopos -> Metis -> Clymene ->
Hermes): read the horizon scanner's daily digest, cross-reference the
project's own priorities, and compress 50+ items into 3 an operator
could act on. It produced 8 briefs between 2026-03-22 and 2026-04-01
(MEASURED: agents/metis/briefs/) and then stopped; 62 commits touch
agents/metis/, the last on 2026-04-03 (COMMIT b674a9976), most of them
"pronoia: auto-publish reports". In May a SECOND program took the name:
scripts/metis_portfolio.py, 926 lines, which compresses the program's
own multi-machine agent state into the same Act / Watch / Record shape
and writes docs/portfolio_brief.md. That one did not stop in April. It
ran every four hours until 2026-09-09T02:15:15Z (COMMIT 64de18126) and
is the operator's daily dashboard and the Hermes mailer's input. It is
two days dead at the time of writing, and no seat owns it.

## 1. What the operator asked to be reminded of

The directive asked what this seat did when it was active. The honest
answer has two halves and one correction.

THE ANALYST (March 22 - April 1, 2026). Metis read an Eos digest each
day, loaded docs/PRIORITIES.md, docs/TODO.md, docs/RPH.md and a
taxonomy summary from agents/aletheia/, sent the lot to an LLM cascade
(NVIDIA Nemotron 120B, then Cerebras Qwen3-235B, then Groq Llama
3.1-8B) and wrote a one-page brief in three sections: Act on this /
Watch this / For the record. Eight briefs exist. Their subject matter
was mechanistic interpretability: the Corti GIM release, the PRISM
toolkit, SAE decomposition, an arXiv SAE-steering preprint, and --
repeatedly -- three internal items (finish the Qwen3-4B overnight run,
wire the remaining Eos APIs, rent an A100 for Qwen2.5-7B).

THE REPORTER (May 14 - September 9, 2026). A second Metis, written
against pivot/prometheus_synthesis_2026-05-14.md and describing itself
in its own docstring as "the agent-state-reporting cousin" of the
first, read the fleet's state instead of the literature: docs/state.json
(agent heartbeats, anomalies, work queue, deep-research budget), the
last 24 hours of git log, docs/manual_status.json, and the previous
brief. It built the brief DETERMINISTICALLY FIRST and used the LLM
cascade only as a second path, with a chain-of-thought leak detector
between them (COMMIT af9b4d9c9, 2026-08-18, "Metis deterministic-first
+ no-stub guarantee"). It grew an ELI5 gloss for every parked gate
(COMMIT bb63dcf80) and a standing Elenchus shadow-review block (COMMIT
5bdd5f9af). Its output is docs/portfolio_brief.md, authored on its face
"Metis (multi-machine reporter mode)".

THE CORRECTION. The reporter is the better instrument by a wide margin
and it is the one still wired into the program. If a reader's memory of
"Metis" is the paper-brief agent, that memory is four months out of
date. Both are dormant now; only one of them was alive last week.

## 2. The analyst's residue, measured

Command (MEASURED, this pass, over agents/metis/briefs/*.md): extract
the body below the "---" rule, hash it, and extract every bolded
headline in the "Act on this" section.

    8 briefs, 2026-03-22 .. 2026-04-01
    8 distinct body hashes of 8      (no byte-identical repeat)
    act-item counts: 3,3,3,3,3,3,0,1

    headline stem                      distinct briefs it appears in
      Eos API wiring / wire APIs /
        Eos API integration                  6 of 8
      Qwen3-4B overnight run                 5 of 8
      7B Qwen2.5 cloud run                   4 of 8
      Corti GIM                              2 of 8
      PRISM toolkit                          1 of 8
      CWRU-AISM/action-atlas                 1 of 8

THE FINDING. Every brief is byte-distinct, and six consecutive briefs
say the same three things in different words. Eos's charter constraint
3 -- refuse to emit a digest whose body hashes to the previous one --
is necessary and, ONE HOP DOWNSTREAM OF AN LLM, insufficient: a
rewording layer defeats a hash check by construction. Metis is the
counterexample that shows it, and the generalisation belongs in the
base role's dormancy machinery, not in this seat's local file.
(Routed as METIS-05 to Eos and Archaeon.)

Second finding, same residue: agents/metis/briefs/2026-03-31_brief.md
is 161 bytes and its entire body is

    (Metis could not reach any LLM provider)

That string is metis.py's cascade fallback, written to a file named
like every other brief. scripts/check_intelligence_pipeline.py's
get_latest_report() returns a Path if a file exists whose name contains
today's date and NEVER OPENS IT (MEASURED: the function body). So on
2026-03-31 the pipeline health checker would have reported the Metis
stage healthy on the strength of a file whose contents said the stage
had failed. Property versus label, in this seat's own monitor.

## 3. The reporter's death, measured

    last portfolio commit   64de18126  2026-09-08T22:15:15-04:00
                            "auto: portfolio update 2026-09-09T02:15:10Z"
    cadence before it       6 commits/day, 09-02 .. 09-08
    cadence since           0
    age at time of writing  about 61 hours, about 15 missed cycles

It did not degrade; it stopped dead. MONITORS.md row 27 already carries
this (registered by Hermes on its adoption pass, OWNER UNCLAIMED, not
restarted). Metis adds the producer-side detail below and does not
restart it either.

THE SILENT ALARM (MEASURED BY EXECUTION, not by reading):

    $ python -c "import json; d=json.load(open('docs/state.json')); ..."
    schema_version              3
    generated_at                2026-09-09T02:14:37.647563+00:00
    has infra_status            False
    observability.degraded      True
    observability.data_source   none
    observability.degraded_reasons
        ['Redis unreachable; agent state is sourced from the Postgres
          mirror only',
         'Postgres unreachable; durable evidence cannot be read']
    --- what scripts/metis_portfolio.py:576-577 computes from this ---
    redis_status                '(state.json reports up)'
    does the line-587 alarm fire?   False

metis_portfolio.py reads state.get("infra_status"). docs/state.json has
carried an "observability" block and NO "infra_status" key since
2026-09-01 (COMMIT d46800bfb, the first auto-portfolio commit whose
state.json contains the key "observability"). The degradation branch
has therefore been unreachable for eight days, and the absent-key
fallback is the optimistic literal "(state.json reports up)".

The consequence is on disk. docs/portfolio_brief.md, generated
2026-09-09 02:15:01 UTC, 24 seconds after that state.json, says:

    ## Act on this
    *(no daemons require intervention)*
    ## Watch this
    *(nothing trending toward intervention)*

and contains no occurrence of "degrad", "unreachable", "data_source" or
"stale" (MEASURED: grep -i, exit 1). The brief reported calm while both
of its stores were unreachable and its own input said so in a field the
brief's code does not read.

A THIRD FACT, UNRESOLVED. scripts/portfolio_monitor.py has two state
builders: the healthy one (line ~682) emits no infra_status, and the
degraded one (line ~846, build_degraded_state_from_postgres) DOES emit
infra_status with redis="unreachable". Neither emits an "observability"
block. No tracked file in this repository emits the JSON key
"observability" into state.json (MEASURED: git grep -ln '"observability"'
over the tree excluding roles/ and docs/ returns nothing; the two hits
for the bare word are prose in scripts/clio_daemon.py and
scripts/clio_quality.py). So the code that produced the last eight days
of docs/state.json IS NOT THE portfolio_monitor.py ON MAIN. Either a
newer version runs on the producing host, or a different program does.
The producing host is itself unknown -- MONITORS.md records "M3 or M4,
not M1, not M2 (verified)". THIS IS AN EPISTEMIC GAP AND IS LEFT OPEN:
whether the deployed producer is ahead of the repository cannot be
determined from any machine this seat can reach. Fail closed, preserve
the observation, route the question (METIS-03, blocked on host access).

## 4. The old queue, classified

The analyst had no written queue of its own; its queue was whatever the
day's digest said. The classifiable items are the design commitments in
agents/metis/README.md (DOC) and configs/metis_config.yaml (DOC),
plus the reporter's accumulated behaviour.

    A1  Read the Eos daily digest and compress it to 3-5 items
        NEEDS_REPREMISE. The compression job survives; its INPUT does
        not. Eos is BLOCKED on its own re-premise ruling and its daemon
        is stopped by operator condition. A brief with no upstream is
        base rule 9's launch-precondition failure. The item cannot be
        executable before Eos is.
    A2  Cross-reference findings against docs/PRIORITIES.md, docs/TODO.md
        and docs/RPH.md
        SUPERSEDED. docs/RPH.md is the retired hypothesis. The current
        equivalents are the H0-H5 lane status and the seats' own
        BACKLOG_H0H5.md files. Re-premise, do not resume.
    A3  LLM cascade NVIDIA -> Cerebras -> Groq, keys from agents/eos/.env
        SUPERSEDED by prometheus_llm (COMMIT 25623303e, 2026-08-22):
        one model API for the program. A seventh hand-rolled client is
        the defect prometheus_llm exists to end. Note the deeper
        objection: the cascade was asked for a JUDGEMENT, which
        constraint 2 of this seat's charter refuses outright, so the
        item is not merely re-routed, its purpose is refused.
    A4  Flag pivots -- "anything that suggests we should change direction"
        RETIRED. This is the reporting layer recommending a research
        direction. Out of lane under the north star and under
        constraint 7. Kept as archaeological material.
    A5  "James-proof -- assumes a 10-second goldfish loop. Lead with the
        headline." (README design principle)
        STILL_LIVE, and it is the single best line in either code body.
        It is the sagacity criterion stated in the operator's own terms:
        a compact handle from which a receiver reconstructs a richer
        lesson. It survives into RESPONSIBILITIES.md as the reason the
        seat exists.
    A6  Pronoia serial pipeline membership
        (Eos -> Aletheia -> Skopos -> Metis -> Clymene -> Hermes)
        RETIRED as a chain. Two program reviews archived it as a unit
        (aporia/docs/program_audit_2026-06-10.md line 136;
        aporia/docs/STATUS_2026-06-15_reset.md line 105). Clymene has
        been re-seated separately and does not resume the chain either.
        The individual hop Metis -> Hermes is the only one still wired.
    R1  Produce docs/portfolio_brief.md every four hours from
        docs/state.json + git log + manual_status
        STILL_LIVE AS A JOB, DEAD AS A PROCESS, AND UNOWNED. This is
        METIS-01 (XL) and it is the only item on this list that has a
        live consumer waiting.
    R2  Deterministic-first with an LLM second path and a
        chain-of-thought leak detector
        STILL_LIVE. The right instinct, kept, and strengthened by
        constraint 2 (the LLM may propose, never assert).
    R3  ELI5 gloss for every parked gate and pending decision
        STILL_LIVE. It is the compression job aimed at the receiver who
        must actually act. Note the honest defect already on the face
        of the last brief: four of the eight parked-gate groups print
        "(no ELI5 for this gate yet -- the loop owes one next pass)".
        The instrument declares its own debt, which is correct
        behaviour and worth preserving.
    R4  Standing "Shadow review (Elenchus)" block
        STILL_LIVE and it has a DECLARED CONSUMER: Elenchus's
        RESPONSIBILITIES.md names the Metis dashboard as the surface on
        which its reviews are read. That consumer has been served a
        61-hour-old file since 2026-09-09.
    R5  docs/manual_status.json as the operator's out-of-band override
        DORMANT-BY-DESIGN AND DANGEROUS. Last modified 2026-05-18
        (COMMIT 27dcad44b), 116 days before the last brief that read it.
        metis_portfolio.py's own prompt text instructs the model to
        "trust docs/manual_status.json over the agent table for ground
        truth" (line 473) while another passage tells it manual_status
        may be stale (line 154). An authoritative override with no
        freshness gate is a stale fact with priority. Re-premise or
        retire (METIS-07).
    R6  touch_manual_status_timestamp()
        SUPERSEDED by R5's resolution; a timestamp touched by the
        consumer is not a freshness signal about the producer.

Counts: STILL_LIVE 4 (A5, R2, R3, R4), STILL_LIVE-BUT-UNOWNED 1 (R1),
NEEDS_REPREMISE 2 (A1, R5), SUPERSEDED 3 (A2, A3, R6), RETIRED 2 (A4,
A6). Executable today: ZERO, because the one item with a live consumer
is blocked on an ownership decision the seat may not make for itself.

## 5. What this seat got wrong, for the calibration ledger

Recorded here at the moment of seating so the record is unflattering
before there is anything to be flattered about. Details in
calibration/CALIBRATION.md.

    C-01  The analyst told the operator to do the same three things on
          six consecutive days, and on no day did it say "this is the
          same as yesterday". Six days of an operator's attention spent
          on a redundant instrument.
    C-02  The analyst wrote its own cascade failure into a brief file
          and the pipeline's health checker called the stage healthy.
    C-03  The reporter's infra alarm was wired to a key its input
          stopped emitting, and reported calm for eight days across a
          schema change, ending with a brief that said "no daemons
          require intervention" while both stores were unreachable.
    C-04  This seat's first act on 2026-09-11 was to run `git pull` in
          the canonical checkout, before it had read
          WORKING_CONTRACT.md, because the wake directive said "pull
          the latest from the repo first". Sections 1 and 3 violated.
          This is the SECOND recorded instance of exactly this failure
          (Atalanta L-09, same day, same cause), which makes it a
          constitution defect rather than two seats' carelessness: the
          rule lives in a file the seat is told to read AFTER it has
          been told to pull. Reported to Archaeon as METIS-06.
