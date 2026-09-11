# Eos archaeology -- the March-April queue and the May work, classified

Currency: 2026-09-11. Written on the re-seating pass, under the base
role's rule that BOOTING AN OLD SEAT IS AN ARCHAEOLOGICAL EVENT: every
item of the old queue is classified against the current north star, and
only STILL_LIVE becomes executable work. Nothing here was executed.

Provenance grades used below:
  COMMIT   read from a commit in this repository (SHA given)
  MEASURED read from a live store or file on this pass (command given)
  DOC      read from a committed document
  RECALL   remembered, not verified -- cited as such, never as fact

## 0. The seat's lifetime in one paragraph

Eos was built in March 2026 as the intelligence pipeline's horizon
scanner: hourly sweeps of five sources, keyword scoring, an LLM analysis
hop, a daily digest. It produced 8 digests between 2026-03-22 and
2026-04-01 (MEASURED: the archive) and indexed 163 items (MEASURED:
paper_index.json _meta.total_items). In May it was instrumented into the
Postgres-logged pipeline and ran once (MEASURED: agora.intelligence_
outputs has exactly one row with stage='eos', 2026-05-17T03:54:44Z,
success=true, output_summary 'digest 2026-05-17.md'). On 2026-05-18 a
substrate redirect was designed, built and backed out the same day by
operator redirect (COMMIT 54ccb3e97, 82716d87d, 2de21a796). Nothing has
run since. 116 days.

## 1. What the sole May receipt actually proves

    stage   eos
    cycle   c5a3539b-885c-4ab1-ac15-fac76b14b28e
    at      2026-05-17T03:54:44Z
    success TRUE
    output  "digest 2026-05-17.md"

The row says the stage succeeded. The artifact it names is not in this
repository (agents/eos/reports/ is gitignored), is not on the canonical
checkout's disk (MEASURED: the reports directory holds 8 files, newest
2026-04-01.md), and the host it was written on was M4 (COMMIT 5b39c7b04:
"pronoia.py (gitignored, local-only patch on M4)"). The seat's one
instrumented success is a success label pointing at an artifact no one
can now read. This is the base role's opening case -- a status is the
tool's execution state, not the truth of its output -- found in this
seat's own ledger, and it is row 1 of CALIBRATION.md.

The table itself outlived the pipeline: agora.intelligence_outputs now
holds 15,490 rows, most recent 2026-09-11T11:19Z (MEASURED). Other seats
adopted it as a general program log. The plumbing Eos's May commits laid
down is load-bearing; the seat that laid it is not.

## 2. The README roadmap (10 items), classified

The queue of record is the Roadmap in agents/eos/README.md (DOC), last
touched 2026-04-03.

    R1 Wire Groq for LLM summarisation (14.4K RPD free)
       SUPERSEDED by prometheus_llm (COMMIT 25623303e, 2026-08-22): one
       model API for the program, groq among its providers. Eos calls
       prometheus_llm or it does not call a model. Wiring a seventh
       client is the defect prometheus_llm was built to end.
    R2 Wire Cerebras for deep analysis (Qwen 3-235B free)
       SUPERSEDED, same reason. NOTE the deeper objection: "deep
       analysis" by an LLM over a title and 500 characters is
       constraint 2 of the seat's charter -- a confabulation channel.
       The item is not merely re-routed, its purpose is refused.
    R3 Wire Semantic Scholar live API (awaiting key)
       NEEDS_REPREMISE. The key exists and is REJECTED: COMMIT
       0d76ac34d (2026-08-31, Techne) records the S2 key present via
       keys.get_key and answering 403. The item is not "get a key", it
       is "determine whether S2 is reachable at all from this program,
       and if not, say so and stop citing it as a source".
    R4 Download S2 bulk CS dataset to a local index
    R5 Add scan_local_s2()
    R6 Nightly S2 diff sync
       NEEDS_REPREMISE as one item, and only in the ANCHOR lane. A
       local corpus is justified if and only if it serves the hunt for
       calibration anchors in territory the substrate is WEAK in
       (HARD-4). "A local copy of computer science" serves nothing this
       program has a consumer for, and R3's 403 blocks the bulk route
       as well until measured.
    R7 SPECTER v2 embedding search
       NEEDS_REPREMISE. A similarity instrument needs negative,
       positive and cheat controls before any output is read (base s2);
       it would be the second uncalibrated scorer in this seat if added
       as written. Rank below R4-R6.
    R8 Wire Serper (2,500 lifetime budget -- conserve)
       PARKED. A LIFETIME budget spent against a retired premise is
       waste that cannot be undone. It stays unspent until the seat has
       a ruling and a typed query set.
    R9 Wire OpenRouter as fallback router
       SUPERSEDED by prometheus_llm. RECALL, worth verifying: the
       2026-08-12 shelf note records OpenRouter live with 27 free
       models. Verify before citing.
    R10 Relevance scoring v2: boost papers citing our prior work
       RETIRED, and the reason is doctrinal, not practical. Prometheus
       publishes nothing (HARD-1), so "our prior work" is not a citable
       object -- and an instrument that scores the outside world by how
       much it resembles us is reward-signal capture with a scoring
       function. The seat does not build it. Recorded here so the idea
       stays visible as a refusal rather than being quietly dropped.

    Totals: 0 STILL_LIVE, 4 NEEDS_REPREMISE (R3, R4-R6, R7), 1 PARKED
    (R8), 3 SUPERSEDED (R1, R2, R9), 1 RETIRED (R10), 0 TRANSFERRED.

## 3. The May substrate redirect

COMMIT 54ccb3e97 and 82716d87d (2026-05-18) redirected Eos from generic
AI/ML scanning to substrate-priority mathematics (tensor decomposition,
polynomial method, Mahler measure, modularity, Sato-Tate), restricted to
math arXiv categories, with hour-of-epoch keyword rotation, and added
agora.eos_findings so M1 consumers could read what M4 scanned.

COMMIT 2de21a796, the same day, backed all of it out on the operator's
redirect: the intelligence pipeline keeps running as it did, and a NEW
dedicated agent will own substrate paper mining, claim extraction and
direct Sigma kernel ingestion.

    STATE: RETIRED by the operator, complete. MEASURED: agora.eos_
    findings does not exist in prometheus_fire today; the revert was
    clean. The helper module and the M4 patch recipe are recoverable
    from 82716d87d if ever wanted.
    RESIDUE WORTH KEEPING: hour-of-epoch rotation solved a real defect
    in this seat -- single-keyword scanners always hit keyword[0], so
    the tail of every keyword list was never searched. That defect is
    still in agents/eos/src today. It is EOS-11, independent of the
    substrate premise that was backed out.
    OPEN QUESTION for the operator, not for this seat to answer: was
    the "new dedicated agent" ever built? If it was, Eos must not
    duplicate it. If it was not, the substrate-mining need named on
    2026-05-18 is unserved and nobody is carrying it. EOS-03 (XL).

## 4. The pipeline Eos sat in

    Pronoia -> Eos -> Aletheia -> Skopos -> Metis -> Clymene -> Hermes
    (DOC: roles/PipelineOrchestrator/RESPONSIBILITIES.md:31)

    STATE: the whole pipeline is listed under "RETIRE-after-HITL (21)"
    in pivot/PORTFOLIO_FUTURE_OPTIONS_2026-06-24.md:31, which names
    "the pipeline (Coeus/Aletheia/Eos/Hermes)". That document ALSO
    records, line 41, that these "didn't fail on quality" -- the
    retirement ground was consumers, not output.
    NOT A VERDICT: a disposition proposed in a June options document is
    not an operator ruling, and the base role forbids marking anything
    dead prematurely. Alethelia's NAME_COLLISION note (2026-08-27)
    found the retire ground for the Aletheia component REFUTED on
    measurement (Elenchus executed the consumer). Eos's own retire
    ground deserves the same treatment before it is accepted: EOS-06
    measures whether any consumer of Eos output is alive.
    MEASURED today: three code paths still reference Eos artifacts --
    agents/aletheia/src/aletheia.py:41 (the paper index),
    agents/hermes/src/hermes.py:406,550 (the newest digest into the
    mail body), scripts/check_intelligence_pipeline.py:29-32 (the log
    and report directory as health inputs). Referenced is not
    consuming; none has a 2026-09 receipt. Consumer count is ZERO until
    one is measured.
    Hermes is being seated today in parallel (worktree hermes-base-role
    at 8714b2709). The two seats must agree who owns the digest-to-mail
    hop before either re-runs anything.

## 5. What the residue measures (MEASURED on this pass)

The 8 digests and the daemon log, archived at
roles/Eos/archive/digests_2026-03-22_2026-04-01/ with an LF manifest:

    digest        items   body hash (first 8, below the date line)
    2026-03-22     5      c816c369
    2026-03-23     5      c816c369   IDENTICAL to 03-22
    2026-03-24     5      c816c369   IDENTICAL to 03-22
    2026-03-25    27      e47f5968
    2026-03-27     5      6a5c8049
    2026-03-28    13      b58f0d43
    2026-03-31     5      bf7adea4
    2026-04-01     3      8b92de75

    command: for a in *.md; do tail -n +3 $a | md5sum; done

Three of the eight are byte-identical below the date header. Three
consecutive days of "intelligence" carried the same five items. The
daemon log for 2026-03-22 shows the 11:30 and 12:30 cycles both writing
"Digest written: ...2026-03-22.md" -- an hourly loop overwriting a
daily-granularity artifact, exiting cleanly each time. This is base rule
8 (scheduled activity is not progress) found in this seat's own residue,
and it is why constraint 3 of the charter exists.

The final digest, 2026-04-01, reports "All Papers (0 found)" and does
not say that the dedup index had saturated at 163 items. "0 new" was
printed; "0 could have been new" was never computed. Both facts are
always reported from now on (charter constraint 6).

That same digest's "Deep Analysis" section is the model's scratchpad
printed verbatim -- "Likely they provide tools to probe internal
representations", "Could be they find that certain modules correspond to
reasoning", "if they find no such circuits, challenges" -- under a
heading that reads as analysis, beside a real GitHub URL, about a
0-star repository the model never opened. Charter constraint 2.

## 6. The live dependency nobody registered

MEASURED: keys.py (the repo-root loader CLAUDE.md mandates) lists
agents/eos/.env as one of its two sources (keys.py:20-21), and
scripts/llm_cascade.py:29, scripts/metis_portfolio.py:48,
scripts/send_brief_email.py:447 and agents/aletheia/src/aletheia.py:59
each auto-load that exact path. The file exists (1,252 bytes,
timestamped with the April tree; contents NOT read, NOT printed, NOT
committed -- CLAUDE.md and base s2).

A seat that has been unseated since April has been holding the
program's credential path the whole time. This is not a defect Eos
should fix unilaterally -- moving it breaks five call sites -- so it is
EOS-04 (XL), an operator decision, with the recommendation that the
keyring move to a path named for what it is and keys.py keep the old
path as a deprecated fallback for one cycle.

## 7. Classification summary

    STILL_LIVE       0
    NEEDS_REPREMISE  4   R3; R4-R6 as one; R7; the substrate-mining
                         need orphaned by the 2026-05-18 backout
    PARKED           1   R8 (lifetime budget, unspent)
    SUPERSEDED       3   R1, R2, R9 -> prometheus_llm
    RETIRED          2   R10 (doctrinal); the May substrate redirect
                         (operator, complete, clean)
    TRANSFERRED      0

Zero items of the old queue are executable as written. Existing backlog
is not permission to resume an obsolete mission. What the seat proposes
instead is the typing rule in RESPONSIBILITIES.md, and that proposal is
an operator decision: EOS-01 (XL).
