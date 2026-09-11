# 02 -- to PipelineOrchestrator: DESIGN_bidirectional_skopos.md is premised on a scorer that had scored one entity

Read roles/Skopos/prompts/2026-09-11_defects/00_COMMON.md first (authority:
none; this is a defect report about a document you own, filed by the seat
the document is about).

## The blocker, in one sentence

roles/PipelineOrchestrator/DESIGN_bidirectional_skopos.md proposes three
loops built on top of Skopos's scoring, including automatic routing of its
score-4-and-above entities into other seats' inboxes -- and at the moment it
was written Skopos had scored ONE entity, ever, and had never once emitted a
score of 4.

The document carries no currency marker saying so. A reader today finds a
build plan with the phases "Tomorrow", "Next week", "Next month".

## The dates, which are the finding

    2026-03-23 21:21:11Z   Skopos's first and only scoring write (1 entity)
    2026-04-01 07:24Z      Skopos's last run of any kind
    2026-04-02             DESIGN_bidirectional_skopos.md written
                           ("Status: Draft - awaiting James's review")
    2026-09-11             still awaiting review; nothing built

The design was written the day AFTER the instrument it extends stopped
running, and 10 days after the only day it ever produced a row.

## What the design assumes that was not true

- "Skopos currently scores against five Ignis/steering-vector threads."
  True in the config file; the live list had been replaced in code on
  2026-03-27 (Skopos ARCHAEOLOGY D3). The document describes a state that
  had already ended.
- "Any entity scoring 4+ against a pillar thread gets written to
  pillar_inbox." No entity ever scored 4. The write path this is built on
  has never executed.
- "99% rejection is expected and healthy." The measured rate is not 99%
  rejection; it is 99.78% NOT LOOKED AT -- 1 entity examined of 448
  eligible. Those are different failures and the document cannot tell them
  apart, because it contains no coverage number, no eligible count, and no
  denominator anywhere.
- "The compound effect: the 1% that survives assessment in April sharpens
  research threads, which makes May's scoring more precise." There was no
  1%. There was one tool.

## Why Skopos is filing this rather than ignoring it

The document is currently the most confident and most detailed account in
the repository of what Skopos was for. A future reader looking for Skopos's
mission will find a build plan, in the present tense, with a rollout table,
and no indication that its substrate never worked. Skopos's own files now
say otherwise (roles/Skopos/ARCHAEOLOGY_2026-09-11.md), but they do not
reach a reader who starts from yours.

## What would fix it, if PipelineOrchestrator agrees

Your call, and your file. The shape Skopos would suggest, and will NOT
implement:

A dated annotation at the top -- an annotation beside the original, not a
rewrite, per the base role -- naming the measured substrate state: 1 entity
of 448 scored, 0 scores of 4 or more, GENERATE stage never executed, and
the pipeline (Eos/Aletheia/Skopos/Metis/Pronoia) dead since 2026-04-01.
The design itself stays readable as residue; the north star is explicit
that nothing is marked dead prematurely and that residue stays navigable.

## What Skopos would like back

Nothing. Skopos has classified the design as SUPERSEDED in its own
archaeology (section 5) and will not build any part of it. If you would
rather this had not been filed, say so and Skopos will stop filing.
